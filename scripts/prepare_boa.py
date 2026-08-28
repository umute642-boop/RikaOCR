# SPDX-License-Identifier: Apache-2.0
"""Ingest an eScriptorium PAGE-XML export into a split line-image dataset.

Reads the per-page PAGE-XML files produced by eScriptorium (``mets.xml`` is
ignored), resolves each page's image via its ``imageFilename``, and builds a
deterministic, document-level train/val/test dataset with per-split JSONL
manifests and a datasheet under ``<out>/<version>/`` (see ADR-018).

Usage::

    python scripts/prepare_boa.py --export EXPORT_DIR [--images IMAGES_DIR] \
        [--out data/processed] [--version v1] [--mask-polygon] \
        [--train 0.8] [--val 0.1]

Requires the optional ``[data]`` extra (Pillow).
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from PIL import Image
from rikaocr.core.document.models import Document, Page
from rikaocr.data.annotation.page_xml import PageXmlCodec
from rikaocr.data.dataset.builder import build_dataset
from rikaocr.data.dataset.image_io import load_image
from rikaocr.data.dataset.splitting import Split, assign_split


def load_documents(export_dir: Path) -> list[Document]:
    """Load every PAGE-XML file in ``export_dir`` (skipping METS) as a Document."""
    codec = PageXmlCodec()
    documents: list[Document] = []
    for xml_path in sorted(export_dir.glob("*.xml")):
        if xml_path.name.lower().startswith("mets"):
            continue
        documents.append(codec.load(xml_path))
    return documents


def make_image_loader(images_dir: Path):
    """Return an image loader resolving ``page.image_ref`` under ``images_dir``."""

    def loader(document: Document, page: Page) -> Image.Image | None:
        if page.image_ref is None:
            return None
        for candidate in (images_dir / page.image_ref, images_dir / Path(page.image_ref).name):
            if candidate.exists():
                return load_image(candidate)
        return None

    return loader


def main(argv: list[str] | None = None) -> int:
    """Run the ingest + dataset build; returns a process exit code."""
    parser = argparse.ArgumentParser(
        description="Ingest eScriptorium PAGE-XML into a split line-image dataset."
    )
    parser.add_argument("--export", required=True, type=Path, help="Directory of PAGE-XML files.")
    parser.add_argument(
        "--images", type=Path, default=None, help="Directory of page images (default: --export)."
    )
    parser.add_argument(
        "--out", type=Path, default=Path("data/processed"), help="Output root directory."
    )
    parser.add_argument("--version", default="v1", help="Dataset version subfolder (default: v1).")
    parser.add_argument(
        "--mask-polygon", action="store_true", help="Mask each line crop to its polygon."
    )
    parser.add_argument(
        "--train", type=float, default=0.8, help="Training fraction (default: 0.8)."
    )
    parser.add_argument(
        "--val", type=float, default=0.1, help="Validation fraction (default: 0.1)."
    )
    args = parser.parse_args(argv)

    images_dir: Path = args.images or args.export
    documents = load_documents(args.export)
    if not documents:
        parser.error(f"No PAGE-XML files found in {args.export}")

    distribution = Counter(
        assign_split(doc.doc_id, train=args.train, val=args.val).value for doc in documents
    )
    print(f"Loaded {len(documents)} document(s). Split distribution: {dict(distribution)}")
    for split in Split:
        if distribution.get(split.value, 0) == 0:
            print(f"  WARNING: split '{split.value}' is empty; enlarge the pilot batch before F1.")

    report = build_dataset(
        documents,
        make_image_loader(images_dir),
        args.out,
        version=args.version,
        mask_polygon=args.mask_polygon,
        train=args.train,
        val=args.val,
    )
    print(f"Built dataset at {report.output_dir}")
    print(f"  line counts: {dict((s.value, n) for s, n in report.line_counts.items())}")
    print(f"  skipped lines (no geometry / empty crop): {report.skipped_lines}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
