# SPDX-License-Identifier: Apache-2.0
"""Annotation codecs (PAGE-XML, ...) bridging files and the document model."""

from rikaocr.data.annotation.page_xml import PageXmlCodec, from_page_xml, to_page_xml
from rikaocr.data.annotation.region_mapping import (
    region_type_from_page,
    region_type_to_page,
)

__all__ = [
    "PageXmlCodec",
    "from_page_xml",
    "to_page_xml",
    "region_type_from_page",
    "region_type_to_page",
]
