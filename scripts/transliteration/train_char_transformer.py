import argparse
import csv
import json
import math
import random
import unicodedata
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


PAD = "<pad>"
BOS = "<bos>"
EOS = "<eos>"
UNK = "<unk>"


def seed_everything(seed):
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def norm(s):
    return unicodedata.normalize("NFC", s.strip())


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return [(norm(r["osmanlica"]), norm(r["transkripsiyon"])) for r in rows]


def make_vocab(train_pairs):
    src_chars = sorted(set("".join(s for s, _ in train_pairs)))
    tgt_chars = sorted(set("".join(t for _, t in train_pairs)))

    src_itos = [PAD, BOS, EOS, UNK] + src_chars
    tgt_itos = [PAD, BOS, EOS, UNK] + tgt_chars

    src_stoi = {c: i for i, c in enumerate(src_itos)}
    tgt_stoi = {c: i for i, c in enumerate(tgt_itos)}

    return src_stoi, src_itos, tgt_stoi, tgt_itos


class PairDataset(Dataset):
    def __init__(self, pairs, src_stoi, tgt_stoi):
        self.pairs = pairs
        self.src_stoi = src_stoi
        self.tgt_stoi = tgt_stoi

    def __len__(self):
        return len(self.pairs)

    def encode(self, text, stoi):
        return [stoi[BOS]] + [stoi.get(c, stoi[UNK]) for c in text] + [stoi[EOS]]

    def __getitem__(self, i):
        s, t = self.pairs[i]
        return (
            torch.tensor(self.encode(s, self.src_stoi), dtype=torch.long),
            torch.tensor(self.encode(t, self.tgt_stoi), dtype=torch.long),
            s,
            t,
        )


def collate(batch, src_pad, tgt_pad):
    srcs, tgts, src_texts, tgt_texts = zip(*batch)
    max_s = max(len(x) for x in srcs)
    max_t = max(len(x) for x in tgts)

    src = torch.full((len(batch), max_s), src_pad, dtype=torch.long)
    tgt = torch.full((len(batch), max_t), tgt_pad, dtype=torch.long)

    for i, x in enumerate(srcs):
        src[i, :len(x)] = x
    for i, x in enumerate(tgts):
        tgt[i, :len(x)] = x

    return src, tgt, src_texts, tgt_texts


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=256):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(0, max_len, dtype=torch.float32).unsqueeze(1)
        div = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32)
            * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class CharTransformer(nn.Module):
    def __init__(
        self,
        src_vocab,
        tgt_vocab,
        src_pad,
        tgt_pad,
        d_model=128,
        nhead=4,
        layers=2,
        ff=256,
        dropout=0.1,
    ):
        super().__init__()
        self.src_pad = src_pad
        self.tgt_pad = tgt_pad
        self.d_model = d_model

        self.src_emb = nn.Embedding(src_vocab, d_model, padding_idx=src_pad)
        self.tgt_emb = nn.Embedding(tgt_vocab, d_model, padding_idx=tgt_pad)
        self.pos = PositionalEncoding(d_model)

        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=layers,
            num_decoder_layers=layers,
            dim_feedforward=ff,
            dropout=dropout,
            batch_first=True,
        )

        self.out = nn.Linear(d_model, tgt_vocab)

    def forward(self, src, tgt_in):
        src_mask = src.eq(self.src_pad)
        tgt_pad_mask = tgt_in.eq(self.tgt_pad)

        causal = nn.Transformer.generate_square_subsequent_mask(
            tgt_in.size(1), device=tgt_in.device
        )

        src_e = self.pos(self.src_emb(src) * math.sqrt(self.d_model))
        tgt_e = self.pos(self.tgt_emb(tgt_in) * math.sqrt(self.d_model))

        h = self.transformer(
            src_e,
            tgt_e,
            tgt_mask=causal,
            src_key_padding_mask=src_mask,
            tgt_key_padding_mask=tgt_pad_mask,
            memory_key_padding_mask=src_mask,
        )
        return self.out(h)

    @torch.no_grad()
    def greedy(self, src, bos_id, eos_id, max_len=140):
        src_mask = src.eq(self.src_pad)
        src_e = self.pos(self.src_emb(src) * math.sqrt(self.d_model))

        memory = self.transformer.encoder(
            src_e,
            src_key_padding_mask=src_mask,
        )

        ys = torch.full(
            (src.size(0), 1),
            bos_id,
            dtype=torch.long,
            device=src.device,
        )
        finished = torch.zeros(src.size(0), dtype=torch.bool, device=src.device)

        for _ in range(max_len):
            tgt_e = self.pos(self.tgt_emb(ys) * math.sqrt(self.d_model))
            causal = nn.Transformer.generate_square_subsequent_mask(
                ys.size(1), device=src.device
            )
            h = self.transformer.decoder(
                tgt_e,
                memory,
                tgt_mask=causal,
                memory_key_padding_mask=src_mask,
            )
            nxt = self.out(h[:, -1]).argmax(-1)
            nxt = torch.where(finished, torch.full_like(nxt, eos_id), nxt)
            ys = torch.cat([ys, nxt.unsqueeze(1)], dim=1)
            finished |= nxt.eq(eos_id)
            if finished.all():
                break

        return ys


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                cur[-1] + 1,
                prev[j] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = cur
    return prev[-1]


def decode(ids, itos):
    out = []
    for i in ids:
        tok = itos[int(i)]
        if tok == EOS:
            break
        if tok not in (PAD, BOS):
            out.append(tok)
    return "".join(out)


@torch.no_grad()
def evaluate(model, loader, device, tgt_itos, bos_id, eos_id):
    model.eval()
    edits = 0
    chars = 0
    exact = 0
    total = 0

    examples = []

    for src, _, src_texts, refs in loader:
        src = src.to(device)
        pred_ids = model.greedy(src, bos_id, eos_id)

        for ids, source, ref in zip(pred_ids, src_texts, refs):
            hyp = decode(ids, tgt_itos)
            edits += levenshtein(hyp, ref)
            chars += len(ref)
            exact += int(hyp == ref)
            total += 1

            if len(examples) < 10:
                examples.append({
                    "osmanlica": source,
                    "reference": ref,
                    "prediction": hyp,
                })

    return {
        "cer": edits / chars if chars else 0.0,
        "exact_match": exact / total if total else 0.0,
        "examples": examples,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--validation", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--patience", type=int, default=7)
    args = ap.parse_args()

    seed_everything(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.set_float32_matmul_precision("high")

    train_pairs = read_csv(args.train)
    val_pairs = read_csv(args.validation)
    test_pairs = read_csv(args.test)

    src_stoi, src_itos, tgt_stoi, tgt_itos = make_vocab(train_pairs)

    src_pad = src_stoi[PAD]
    tgt_pad = tgt_stoi[PAD]
    bos_id = tgt_stoi[BOS]
    eos_id = tgt_stoi[EOS]

    train_ds = PairDataset(train_pairs, src_stoi, tgt_stoi)
    val_ds = PairDataset(val_pairs, src_stoi, tgt_stoi)
    test_ds = PairDataset(test_pairs, src_stoi, tgt_stoi)

    coll = lambda b: collate(b, src_pad, tgt_pad)

    g = torch.Generator()
    g.manual_seed(args.seed)

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=coll,
        generator=g,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=coll,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=coll,
    )

    model = CharTransformer(
        len(src_itos),
        len(tgt_itos),
        src_pad,
        tgt_pad,
    ).to(device)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss(ignore_index=tgt_pad)

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    best_path = outdir / "best_model.pt"

    best_cer = float("inf")
    bad_epochs = 0

    print("DEVICE:", device)
    if device.type == "cuda":
        print("GPU:", torch.cuda.get_device_name(0))
    print("TRAIN:", len(train_ds))
    print("VALIDATION:", len(val_ds))
    print("TEST:", len(test_ds))
    print("SRC VOCAB:", len(src_itos))
    print("TGT VOCAB:", len(tgt_itos))

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        batches = 0

        for src, tgt, _, _ in train_loader:
            src = src.to(device)
            tgt = tgt.to(device)

            tgt_in = tgt[:, :-1]
            tgt_out = tgt[:, 1:]

            opt.zero_grad(set_to_none=True)
            logits = model(src, tgt_in)

            loss = loss_fn(
                logits.reshape(-1, logits.size(-1)),
                tgt_out.reshape(-1),
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()

            total_loss += loss.item()
            batches += 1

        val = evaluate(
            model, val_loader, device, tgt_itos, bos_id, eos_id
        )

        train_loss = total_loss / max(batches, 1)

        print(
            f"EPOCH {epoch:02d} "
            f"loss={train_loss:.4f} "
            f"val_CER={val['cer']:.4f} "
            f"val_exact={val['exact_match']:.4f}"
        )

        if val["cer"] < best_cer:
            best_cer = val["cer"]
            bad_epochs = 0

            torch.save({
                "model_state": model.state_dict(),
                "src_itos": src_itos,
                "tgt_itos": tgt_itos,
                "seed": args.seed,
                "val_cer": best_cer,
            }, best_path)

            print("  BEST MODEL SAVED")
        else:
            bad_epochs += 1

        if bad_epochs >= args.patience:
            print("EARLY STOPPING")
            break

    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint["model_state"])

    final_val = evaluate(
        model, val_loader, device, tgt_itos, bos_id, eos_id
    )

    # Test is evaluated only here, after model selection is complete.
    final_test = evaluate(
        model, test_loader, device, tgt_itos, bos_id, eos_id
    )

    result = {
        "seed": args.seed,
        "train_size": len(train_ds),
        "validation_size": len(val_ds),
        "test_size": len(test_ds),
        "best_validation_cer": final_val["cer"],
        "best_validation_exact_match": final_val["exact_match"],
        "test_cer": final_test["cer"],
        "test_exact_match": final_test["exact_match"],
        "test_examples": final_test["examples"],
    }

    with open(outdir / "results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\nFINAL RESULTS")
    print("VALIDATION CER:", round(final_val["cer"], 6))
    print("VALIDATION EXACT:", round(final_val["exact_match"], 6))
    print("TEST CER:", round(final_test["cer"], 6))
    print("TEST EXACT:", round(final_test["exact_match"], 6))
    print("MODEL:", best_path)
    print("RESULTS:", outdir / "results.json")


if __name__ == "__main__":
    main()
