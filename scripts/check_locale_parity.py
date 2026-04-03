#!/usr/bin/env python3
"""Check locale file key parity against en.ts reference.

Verifies that all 8 locale files (en, es, fr, de, pt, ja, zh, ko) have
identical key sets. Reports missing and extra keys per locale.

Exit code: 0 if all locales are complete, 1 if any are missing keys.

Phase 2 (S254) — WCAG AA locale completeness audit.

Usage:
    python scripts/check_locale_parity.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WIDGET_DIR = Path(__file__).resolve().parent.parent / "widget" / "src" / "locale"
LOCALES = ["en", "es", "fr", "de", "pt", "ja", "zh", "ko"]
# Pattern matches keys in TypeScript object literals: `keyName: 'value'` or `keyName: "value"`
KEY_PATTERN = re.compile(r"^\s+(\w+):\s+['\"]", re.MULTILINE)


def extract_keys(locale_file: Path) -> set[str]:
    """Extract all locale keys from a TypeScript locale file."""
    content = locale_file.read_text(encoding="utf-8")
    return set(KEY_PATTERN.findall(content))


def main() -> int:
    ref_file = WIDGET_DIR / "en.ts"
    if not ref_file.exists():
        print(f"ERROR: Reference locale file not found: {ref_file}")
        return 1

    ref_keys = extract_keys(ref_file)
    print(f"Reference (en.ts): {len(ref_keys)} keys")
    print("-" * 50)

    has_errors = False
    for code in LOCALES:
        if code == "en":
            continue
        locale_file = WIDGET_DIR / f"{code}.ts"
        if not locale_file.exists():
            print(f"  {code}: FILE MISSING")
            has_errors = True
            continue

        locale_keys = extract_keys(locale_file)
        missing = ref_keys - locale_keys
        extra = locale_keys - ref_keys

        if missing or extra:
            has_errors = True
            print(f"  {code}: FAIL — {len(missing)} missing, {len(extra)} extra")
            for k in sorted(missing):
                print(f"    MISSING: {k}")
            for k in sorted(extra):
                print(f"    EXTRA:   {k}")
        else:
            print(f"  {code}: OK ({len(locale_keys)} keys)")

    print("-" * 50)
    if has_errors:
        print("RESULT: FAIL — locale parity violations found")
        return 1
    else:
        print(f"RESULT: PASS — all {len(LOCALES)} locales have {len(ref_keys)} keys")
        return 0


if __name__ == "__main__":
    sys.exit(main())
