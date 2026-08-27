import argparse
import csv
import json
import random
import unicodedata
from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    EarlyStoppingCallback,
)


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


class TransliterationDataset(Dataset):
    def __init__(self, pairs, tokenizer, max_source_length, max_target_length):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        src, tgt = self.pairs[idx]

        model_inputs = self.tokenizer(
            src,
            max_length=self.max_source_length,
            truncation=True,
        )

        labels = self.tokenizer(
            text_target=tgt,
            max_length=self.max_target_length,
            truncation=True,
        )

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs


def make_compute_metrics(tokenizer):
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred

        if isinstance(predictions, tuple):
            predictions = predictions[0]

        predictions = predictions.copy()
        predictions[predictions == -100] = tokenizer.pad_token_id

        labels = labels.copy()
        labels[labels == -100] = tokenizer.pad_token_id

        pred_texts = tokenizer.batch_decode(
            predictions,
            skip_special_tokens=True,
        )
        ref_texts = tokenizer.batch_decode(
            labels,
            skip_special_tokens=True,
        )

        edits = 0
        chars = 0
        exact = 0

        for hyp, ref in zip(pred_texts, ref_texts):
            hyp = norm(hyp)
            ref = norm(ref)

            edits += levenshtein(hyp, ref)
            chars += len(ref)
            exact += int(hyp == ref)

        total = len(ref_texts)

        return {
            "cer": edits / chars if chars else 0.0,
            "exact_match": exact / total if total else 0.0,
        }

    return compute_metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--validation", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="google/byt5-small")
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--patience", type=int, default=3)
    ap.add_argument("--max-source-length", type=int, default=192)
    ap.add_argument("--max-target-length", type=int, default=160)
    args = ap.parse_args()

    seed_everything(args.seed)

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    print("CUDA:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        cache_dir=args.cache_dir,
        local_files_only=True,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.model,
        cache_dir=args.cache_dir,
        local_files_only=True,
    )

    model.gradient_checkpointing_enable()
    model.config.use_cache = False

    train_pairs = read_csv(args.train)
    val_pairs = read_csv(args.validation)

    print("TRAIN:", len(train_pairs))
    print("VALIDATION:", len(val_pairs))
    print("TEST: held out until model selection is complete")

    train_ds = TransliterationDataset(
        train_pairs,
        tokenizer,
        args.max_source_length,
        args.max_target_length,
    )

    val_ds = TransliterationDataset(
        val_pairs,
        tokenizer,
        args.max_source_length,
        args.max_target_length,
    )

    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        label_pad_token_id=-100,
        pad_to_multiple_of=8,
    )

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(outdir / "checkpoints"),
        num_train_epochs=args.epochs,
        learning_rate=args.lr,

        per_device_train_batch_size=1,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=16,

        fp16=False,
        bf16=True,
        gradient_checkpointing=True,

        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=100,

        predict_with_generate=True,
        generation_max_length=args.max_target_length,
        generation_num_beams=1,

        load_best_model_at_end=True,
        metric_for_best_model="cer",
        greater_is_better=False,

        save_total_limit=2,
        max_grad_norm=1.0,
        weight_decay=0.01,

        report_to="none",
        seed=args.seed,
        data_seed=args.seed,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        data_collator=collator,
        compute_metrics=make_compute_metrics(tokenizer),
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=args.patience
            )
        ],
    )

    trainer.train()

    print("\nMODEL SELECTION COMPLETE")
    print("Best checkpoint:", trainer.state.best_model_checkpoint)
    print("Best validation CER:", trainer.state.best_metric)

    final_val = trainer.evaluate(
        eval_dataset=val_ds,
        metric_key_prefix="validation",
    )

    best_dir = outdir / "best_model"
    trainer.save_model(str(best_dir))
    tokenizer.save_pretrained(str(best_dir))

    # Held-out test is loaded only after model selection is complete.
    test_pairs = read_csv(args.test)

    print("HELD-OUT TEST:", len(test_pairs))

    test_ds = TransliterationDataset(
        test_pairs,
        tokenizer,
        args.max_source_length,
        args.max_target_length,
    )

    trainer.model.config.use_cache = True

    test_output = trainer.predict(
        test_ds,
        metric_key_prefix="test",
    )

    predictions = test_output.predictions.copy()
    predictions[predictions == -100] = tokenizer.pad_token_id
    labels = test_output.label_ids.copy()
    labels[labels == -100] = tokenizer.pad_token_id

    pred_texts = tokenizer.batch_decode(
        predictions,
        skip_special_tokens=True,
    )
    ref_texts = tokenizer.batch_decode(
        labels,
        skip_special_tokens=True,
    )

    examples = []
    for (src, _), ref, hyp in zip(test_pairs, ref_texts, pred_texts):
        if len(examples) >= 20:
            break
        examples.append({
            "osmanlica": src,
            "reference": norm(ref),
            "prediction": norm(hyp),
        })

    results = {
        "model": args.model,
        "seed": args.seed,
        "train_size": len(train_pairs),
        "validation_size": len(val_pairs),
        "test_size": len(test_pairs),
        "best_checkpoint": trainer.state.best_model_checkpoint,
        "best_validation_cer": trainer.state.best_metric,
        "validation_metrics": final_val,
        "test_metrics": test_output.metrics,
        "test_examples": examples,
    }

    with open(outdir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nFINAL RESULTS")
    print(json.dumps(results["validation_metrics"], indent=2))
    print(json.dumps(results["test_metrics"], indent=2))
    print("MODEL:", best_dir)
    print("RESULTS:", outdir / "results.json")


if __name__ == "__main__":
    main()


