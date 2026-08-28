from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

EXPECTED_HASHES = {
    "checkpoint-9926": "1d772973765dddfc488ab466ed2a8352ec19499c0e03578f48fafda7127a2316",
    "checkpoint-10635": "9a6f7bdbafd68b82a596cab5b5fb0a59de2263db83edc39e2401d2a59d374db3",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct a split RikaOCR ByT5 optimizer.pt file."
    )
    parser.add_argument(
        "checkpoint",
        type=Path,
        help="Path to checkpoint-9926 or checkpoint-10635.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite optimizer.pt if it already exists.",
    )
    args = parser.parse_args()

    checkpoint: Path = args.checkpoint
    parts = [
        checkpoint / "optimizer.pt.part001",
        checkpoint / "optimizer.pt.part002",
    ]
    output = checkpoint / "optimizer.pt"

    for part in parts:
        if not part.is_file():
            raise FileNotFoundError(f"Missing optimizer part: {part}")

    if output.exists() and not args.force:
        raise FileExistsError(f"{output} already exists. Use --force to overwrite it.")

    with output.open("wb") as destination:
        for part in parts:
            with part.open("rb") as source:
                shutil.copyfileobj(source, destination, length=16 * 1024 * 1024)

    actual = sha256(output)
    expected = EXPECTED_HASHES.get(checkpoint.name)

    print(f"Output: {output}")
    print(f"SHA-256: {actual}")

    if expected is not None:
        if actual != expected:
            raise RuntimeError(f"SHA-256 mismatch: expected {expected}, got {actual}")
        print("Verification: MATCH")
    else:
        print("Verification: no built-in reference hash for this checkpoint")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
