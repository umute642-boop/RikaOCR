import argparse
import math
import unicodedata

import torch
import torch.nn as nn

PAD = "<pad>"
BOS = "<bos>"
EOS = "<eos>"
UNK = "<unk>"


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=256):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(0, max_len, dtype=torch.float32).unsqueeze(1)
        div = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, : x.size(1)]


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

        for _ in range(max_len):
            tgt_e = self.pos(self.tgt_emb(ys) * math.sqrt(self.d_model))
            causal = nn.Transformer.generate_square_subsequent_mask(ys.size(1), device=src.device)
            h = self.transformer.decoder(
                tgt_e,
                memory,
                tgt_mask=causal,
                memory_key_padding_mask=src_mask,
            )
            nxt = self.out(h[:, -1]).argmax(-1)
            ys = torch.cat([ys, nxt.unsqueeze(1)], dim=1)

            if nxt.eq(eos_id).all():
                break

        return ys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--text", required=True)
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.model, map_location=device)

    src_itos = checkpoint["src_itos"]
    tgt_itos = checkpoint["tgt_itos"]

    src_stoi = {c: i for i, c in enumerate(src_itos)}
    tgt_stoi = {c: i for i, c in enumerate(tgt_itos)}

    model = CharTransformer(
        len(src_itos),
        len(tgt_itos),
        src_stoi[PAD],
        tgt_stoi[PAD],
    ).to(device)

    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    text = unicodedata.normalize("NFC", args.text.strip())

    ids = [src_stoi[BOS]] + [src_stoi.get(c, src_stoi[UNK]) for c in text] + [src_stoi[EOS]]

    src = torch.tensor([ids], dtype=torch.long, device=device)

    pred = model.greedy(
        src,
        tgt_stoi[BOS],
        tgt_stoi[EOS],
    )[0]

    out = []
    for i in pred.tolist():
        token = tgt_itos[i]
        if token == EOS:
            break
        if token not in (PAD, BOS):
            out.append(token)

    print("OSMANLICA:", text)
    print("LATIN:", "".join(out))


if __name__ == "__main__":
    main()
