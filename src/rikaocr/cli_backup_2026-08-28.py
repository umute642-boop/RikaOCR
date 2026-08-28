# SPDX-License-Identifier: Apache-2.0
"""Command-line entry point for the recognition pipeline (see ADR-021).

Usage::

    python -m rikaocr.cli <image> -o <output.xml>
    python -m rikaocr.cli <image> -o out.txt --format text
    python -m rikaocr.cli <image> -o out.xml --engine kraken \
        --seg-model seg.mlmodel --rec-model rec.mlmodel

The default ``dummy`` engine has no ML dependency, so the CLI plumbing is fully
testable without running inference. Kraken engines are imported lazily, only
when ``--engine kraken`` is selected, keeping import and ``--help`` lightweight.
This module is intentionally separate from the legacy root ``predict.py``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rikaocr.common.types import PathLike
from rikaocr.data.dataset.image_io import load_image
from rikaocr.output import write_page_xml, write_text
from rikaocr.pipeline import Pipeline


def build_pipeline(
    engine: str = "dummy",
    *,
    seg_model: PathLike | None = None,
    rec_model: PathLike | None = None,
    num_lines: int = 3,
) -> Pipeline:
    """Construct a :class:`Pipeline` for the chosen engine.

    The ``kraken`` engines are imported lazily so the optional ``[train]`` extra
    is only required when actually selected.

    Raises:
        ValueError: if ``engine`` is not a known engine name.
    """
    if engine == "dummy":
        from rikaocr.layout.dummy import DummySegmenter
        from rikaocr.recognition.dummy import DummyRecognizer

        return Pipeline(DummySegmenter(num_lines=num_lines), DummyRecognizer())
    if engine == "kraken":
        if rec_model is None:
            raise ValueError("Kraken engine requires --rec-model (a trained recognition model).")
        from rikaocr.layout.kraken_segmenter import KrakenSegmenter
        from rikaocr.recognition.kraken_adapter import KrakenRecognizer

        return Pipeline(
            KrakenSegmenter(model_path=seg_model),
            KrakenRecognizer(model_path=rec_model),
        )
    raise ValueError(f"Unknown engine: {engine!r} (expected 'dummy' or 'kraken').")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rikaocr",
        description="Recognise a page image into PAGE-XML or plain text.",
    )
    parser.add_argument("image", help="Path to the input page image.")
    parser.add_argument("-o", "--output", required=True, help="Output file path.")
    parser.add_argument(
        "--format",
        choices=("page", "text"),
        default="page",
        help="Output format: PAGE-XML (default) or plain text.",
    )
    parser.add_argument(
        "--engine",
        choices=("dummy", "kraken"),
        default="dummy",
        help="Recognition engine (default: dummy, no ML dependency).",
    )
    parser.add_argument("--seg-model", default=None, help="Kraken segmentation model path.")
    parser.add_argument("--rec-model", default=None, help="Kraken recognition model path.")
    parser.add_argument(
        "--num-lines",
        type=int,
        default=3,
        help="Number of lines for the dummy segmenter (default: 3).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI: segment + recognise an image and write the result.

    Returns:
        Process exit code (0 on success).
    """
    args = _build_parser().parse_args(argv)
    image_path = Path(args.image)
    pipeline = build_pipeline(
        args.engine,
        seg_model=args.seg_model,
        rec_model=args.rec_model,
        num_lines=args.num_lines,
    )
    image = load_image(image_path)
    document = pipeline.run(
        image,
        doc_id=image_path.stem,
        page_id=image_path.name,
        image_ref=image_path.name,
    )
    if args.format == "text":
        write_text(document, args.output)
    else:
        write_page_xml(document, args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
