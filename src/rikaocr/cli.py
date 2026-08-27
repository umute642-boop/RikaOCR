# SPDX-License-Identifier: Apache-2.0
"""Command-line entry point for OCR and optional transliteration.

Standard page mode:
    image -> segmentation -> recognition -> Document

Line-image mode:
    single line image -> recognition -> Document

Optional transliteration is always a separate post-recognition layer. The
Arabic-script OCR output is preserved and Latin-script output is written
separately.

Heavy Kraken and ByT5 dependencies are imported lazily only when selected.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rikaocr.common.types import PathLike
from rikaocr.core.document.enums import RegionType
from rikaocr.core.document.models import Document, Line, Page, Region
from rikaocr.data.dataset.image_io import load_image
from rikaocr.output import write_page_xml, write_text
from rikaocr.pipeline import Pipeline
from rikaocr.transliteration.base import Transliterator
from rikaocr.transliteration.document import transliterate_document
from rikaocr.transliteration.output import (
    write_transliteration_json,
    write_transliteration_text,
)


def build_pipeline(
    engine: str = "dummy",
    *,
    seg_model: PathLike | None = None,
    rec_model: PathLike | None = None,
    num_lines: int = 3,
) -> Pipeline:
    """Construct a page-recognition pipeline for the chosen engine."""
    if engine == "dummy":
        from rikaocr.layout.dummy import DummySegmenter
        from rikaocr.recognition.dummy import DummyRecognizer

        return Pipeline(
            DummySegmenter(num_lines=num_lines),
            DummyRecognizer(),
        )

    if engine == "kraken":
        if rec_model is None:
            raise ValueError(
                "Kraken engine requires --rec-model "
                "(a trained recognition model)."
            )

        from rikaocr.layout.kraken_segmenter import KrakenSegmenter
        from rikaocr.recognition.kraken_adapter import KrakenRecognizer

        return Pipeline(
            KrakenSegmenter(model_path=seg_model),
            KrakenRecognizer(model_path=rec_model),
        )

    raise ValueError(
        f"Unknown engine: {engine!r} "
        "(expected 'dummy' or 'kraken')."
    )


def recognize_line_image(
    image,
    *,
    engine: str,
    rec_model: PathLike | None,
    doc_id: str,
    page_id: str,
    image_ref: str | None = None,
) -> Document:
    """Recognise one already-cropped text line without segmentation."""
    if engine == "dummy":
        from rikaocr.recognition.dummy import DummyRecognizer

        recognizer = DummyRecognizer()

    elif engine == "kraken":
        if rec_model is None:
            raise ValueError(
                "Kraken line-image mode requires --rec-model."
            )

        from rikaocr.recognition.kraken_adapter import KrakenRecognizer

        recognizer = KrakenRecognizer(model_path=rec_model)

    else:
        raise ValueError(
            f"Unknown engine: {engine!r} "
            "(expected 'dummy' or 'kraken')."
        )

    result = recognizer.recognize(image)

    return Document(
        doc_id=doc_id,
        pages=[
            Page(
                page_id=page_id,
                image_ref=image_ref,
                width=image.width,
                height=image.height,
                regions=[
                    Region(
                        region_type=RegionType.PARAGRAPH,
                        reading_index=0,
                        lines=[
                            Line(
                                text=result.text,
                                reading_index=0,
                                confidence=result.confidence,
                            )
                        ],
                    )
                ],
            )
        ],
    )


def build_transliterator(
    engine: str = "byt5",
    *,
    model_path: PathLike | None = None,
    device: str | None = None,
    mode: str = "whole",
) -> Transliterator:
    """Construct a transliterator using lazy ML imports."""
    if engine == "byt5":
        if model_path is None:
            raise ValueError(
                "ByT5 transliteration requires --translit-model."
            )

        from rikaocr.transliteration.byt5_adapter import ByT5Transliterator

        return ByT5Transliterator(
            model_path=model_path,
            device=device,
            mode=mode,
        )

    raise ValueError(
        f"Unknown transliteration engine: {engine!r} "
        "(expected 'byt5')."
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rikaocr",
        description=(
            "Recognise a page or line image and optionally transliterate "
            "the OCR output."
        ),
    )

    parser.add_argument(
        "image",
        help="Path to the input image.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="OCR output file path.",
    )
    parser.add_argument(
        "--format",
        choices=("page", "text"),
        default="page",
        help="OCR output format: PAGE-XML (default) or plain text.",
    )
    parser.add_argument(
        "--engine",
        choices=("dummy", "kraken"),
        default="dummy",
        help="Recognition engine (default: dummy).",
    )
    parser.add_argument(
        "--line-image",
        action="store_true",
        help="Treat input as one cropped text line and skip segmentation.",
    )
    parser.add_argument(
        "--seg-model",
        default=None,
        help="Kraken segmentation model path.",
    )
    parser.add_argument(
        "--rec-model",
        default=None,
        help="Kraken recognition model path.",
    )
    parser.add_argument(
        "--num-lines",
        type=int,
        default=3,
        help="Number of lines for the dummy page segmenter (default: 3).",
    )

    parser.add_argument(
        "--transliterate",
        action="store_true",
        help="Run transliteration after OCR.",
    )
    parser.add_argument(
        "--translit-engine",
        choices=("byt5",),
        default="byt5",
        help="Transliteration engine (default: byt5).",
    )
    parser.add_argument(
        "--translit-model",
        default=None,
        help="Path to the trained transliteration model.",
    )
    parser.add_argument(
        "--translit-output",
        default=None,
        help="Separate transliteration output file path.",
    )
    parser.add_argument(
        "--translit-format",
        choices=("text", "json"),
        default="json",
        help="Transliteration output format (default: json).",
    )
    parser.add_argument(
        "--translit-mode",
        choices=("whole", "word"),
        default="whole",
        help="ByT5 inference mode (default: whole).",
    )
    parser.add_argument(
        "--translit-device",
        default=None,
        help="Optional device override, e.g. cuda or cpu.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run OCR and, when requested, a separate transliteration stage."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    image_path = Path(args.image)
    image = load_image(image_path)

    if args.line_image:
        if args.format == "page":
            parser.error(
                "--line-image currently requires --format text."
            )

        document = recognize_line_image(
            image,
            engine=args.engine,
            rec_model=args.rec_model,
            doc_id=image_path.stem,
            page_id=image_path.name,
            image_ref=image_path.name,
        )

    else:
        pipeline = build_pipeline(
            args.engine,
            seg_model=args.seg_model,
            rec_model=args.rec_model,
            num_lines=args.num_lines,
        )

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

    if args.transliterate:
        if args.translit_model is None:
            parser.error(
                "--transliterate requires --translit-model."
            )
        if args.translit_output is None:
            parser.error(
                "--transliterate requires --translit-output."
            )

        transliterator = build_transliterator(
            args.translit_engine,
            model_path=args.translit_model,
            device=args.translit_device,
            mode=args.translit_mode,
        )

        result = transliterate_document(
            document,
            transliterator,
        )

        if args.translit_format == "text":
            write_transliteration_text(
                result,
                args.translit_output,
            )
        else:
            write_transliteration_json(
                result,
                args.translit_output,
            )

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
