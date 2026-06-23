"""SPEC-1743 docs landing logo theme source coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env

ROOT = Path(__file__).resolve().parents[2]
DOCS_SITE = ROOT / "docs-site"
INTRO = DOCS_SITE / "docs" / "intro.md"
IMG_DIR = DOCS_SITE / "static" / "img"

LIGHT_LOGO_SOURCE = "/img/primary-logo-no-wordmark_black_text.svg"
DARK_LOGO_SOURCE = "/img/primary-logo-no-wordmark_white_text.svg"


def _intro_markdown() -> str:
    return INTRO.read_text(encoding="utf-8")


def _themed_image_block() -> str:
    markdown = _intro_markdown()
    match = re.search(r"<ThemedImage\b(?P<body>.*?)\s*/>", markdown, flags=re.DOTALL)
    assert match, "Landing page must render the logo through Docusaurus ThemedImage"
    return match.group(0)


def _asset_path(source: str) -> Path:
    assert source.startswith("/img/")
    return IMG_DIR / source.removeprefix("/img/")


def test_docs_landing_page_uses_docusaurus_themed_image_for_logo() -> None:
    markdown = _intro_markdown()
    themed_image = _themed_image_block()

    assert "import ThemedImage from '@theme/ThemedImage';" in markdown
    assert 'alt="Agent Red"' in themed_image
    assert "sources={{" in themed_image


def test_docs_landing_logo_sources_are_theme_specific_svg_variants() -> None:
    themed_image = _themed_image_block()

    assert f"light: '{LIGHT_LOGO_SOURCE}'" in themed_image
    assert f"dark: '{DARK_LOGO_SOURCE}'" in themed_image
    assert "dark: '/img/agent-red-logo.svg'" not in themed_image


def test_docs_landing_logo_assets_exist() -> None:
    assert _asset_path(LIGHT_LOGO_SOURCE).is_file()
    assert _asset_path(DARK_LOGO_SOURCE).is_file()


def test_docs_landing_logo_assets_have_expected_wordmark_color_evidence() -> None:
    light_svg = _asset_path(LIGHT_LOGO_SOURCE).read_text(encoding="utf-8").lower()
    dark_svg = _asset_path(DARK_LOGO_SOURCE).read_text(encoding="utf-8").lower()

    assert "fill:#000000" in light_svg
    assert "fill:#ffffff" in dark_svg or "fill:#fff" in dark_svg
