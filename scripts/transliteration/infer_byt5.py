import argparse
import unicodedata

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def main():
    parser = argparse.ArgumentParser(
        description="ByT5 Ottoman Arabic-script to Latin transliteration"
    )
    parser.add_argument("--text", required=True, help="Ottoman text to transliterate")
    parser.add_argument(
        "--model",
        default="/usr/src/app/media/byt5/output/byt5_small_seed42_bf16/best_model",
        help="Path to the trained ByT5 model",
    )
    parser.add_argument("--max-new-tokens", type=int, default=160)
    args = parser.parse_args()

    text = unicodedata.normalize("NFC", args.text)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    model.to(device)
    model.eval()

    inputs = tokenizer(text, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            num_beams=1,
        )

    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(prediction)


if __name__ == "__main__":
    main()
