# SPDX-License-Identifier: Apache-2.0
"""Export Kraken ``.gt.txt`` sidecars from a built dataset's manifests (ADR-019).

For each selected split, reads ``<base>/manifests/<split>.jsonl`` and writes one
``<name>.gt.txt`` beside each line image (UTF-8, no trailing newline), in the
format expected by ``ketos train``. Pure standard library -- no image or Kraken
dependency is required to produce the sidecars.

Usage::

    python scripts/export_gt.py --base data/processed/v1 [--splits train val]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rikaocr.data.dataset.sample import read_line_manifest
from rikaocr.data.dataset.splitting import Split
from rikaocr.training.kraken_export import export_gt_sidecars


def main(argv: list[str] | None = None) -> int:
    """Write ``.gt.txt`` sidecars for the selected splits; returns an exit code."""
    parser = argparse.ArgumentParser(
        description="Export Kraken .gt.txt sidecars from dataset manifests."
    )
    parser.add_argument(
        "--base", required=True, type=Path, help="Dataset version dir, e.g. data/processed/v1."
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train", "val"],
        choices=[split.value for split in Split],
        help="Splits to export (default: train val).",
    )
    args = parser.parse_args(argv)

    total = 0
    for split_name in args.splits:
        manifest = args.base / "manifests" / f"{split_name}.jsonl"
        if not manifest.exists():
            parser.error(f"Manifest not found: {manifest}")
        samples = read_line_manifest(manifest)
        written = export_gt_sidecars(samples, args.base)
        print(f"{split_name}: wrote {len(written)} .gt.txt sidecar(s)")
        total += len(written)
    print(f"Total sidecars: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
