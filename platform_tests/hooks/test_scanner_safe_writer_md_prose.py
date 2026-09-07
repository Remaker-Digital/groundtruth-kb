"""W0.3 item 2: scanner-safe-writer `bash_password_flag_p` md-prose exemption.

The `-p` flag pattern must not fire on `.md` prose unless an adjacent
secret-shaped value is present. Two-layer defense is preserved: real
credential-shaped values still block via the general catalog.

Authority: bridge/gtkb-w0-gate-false-positive-repair-001.md item 2 (GO at -002);
GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_SSW = _load("scanner_safe_writer_under_test", ".claude/hooks/scanner-safe-writer.py")


def _names(content: str) -> list[str]:
    return [h[0] for h in _SSW._scan_content(content)]


def test_p_flag_plain_prose_allowed() -> None:
    # `-p port` / `-p version` style prose: no secret-shaped value -> ALLOW.
    assert "bash_password_flag_p" not in _names("-p port forward the traffic ")


def test_p_flag_secret_shaped_blocks() -> None:
    # A long digit+letter value adjacent to -p is secret-shaped -> BLOCK.
    assert "bash_password_flag_p" in _names("-p mypassword123 ")


def test_real_credential_value_blocks() -> None:
    # Two-layer defense preserved: a real credential-shaped value in md BLOCKs.
    assert _names("the key is AKIAIOSFODNN7EXAMPLE ")  # placeholder: scanner fixture
