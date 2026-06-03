"""Tests for WI-4250 Slice 1 — hygiene CLI UTF-8 output + portability.

Covers the spec-derived verification plan from
`bridge/gtkb-hygiene-cli-utf8-portability-slice-1-001.md` (GO at -002):

- `_ensure_utf8_streams` repairs the cp1252 `UnicodeEncodeError` crash class
  (Defect 1) and is a safe no-op on redirected/non-reconfigurable streams.
- the documented `python -m groundtruth_kb` fallback routes to the same CLI
  (Defect 2 portability — behavior-identical, deterministic, no subprocess).
- the `deliberations search` path that triggered Defect 1 tolerates a
  BOM-containing result without crashing.

All tests are hermetic: streams are in-memory buffers and the DB/config are
stubbed; no live `groundtruth.db` read or write.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import io
import types

import pytest
from click.testing import CliRunner

from groundtruth_kb import cli

_BOM = "﻿"


# --------------------------------------------------------------------------
# Defect 1: CP1252 UnicodeEncodeError repair
# --------------------------------------------------------------------------


def test_ensure_utf8_streams_fixes_cp1252_crash(monkeypatch: pytest.MonkeyPatch) -> None:
    """A strict cp1252 stream cannot encode a BOM pre-fix; after
    `_ensure_utf8_streams` the stream is UTF-8 and the BOM round-trips."""
    # Pre-fix reproduction: cp1252 has no mapping for U+FEFF.
    pre = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict", newline="")
    with pytest.raises(UnicodeEncodeError):
        pre.write(_BOM)
        pre.flush()

    # Apply the fix to controlled stdout/stderr so the real streams are untouched.
    out_raw, err_raw = io.BytesIO(), io.BytesIO()
    out = io.TextIOWrapper(out_raw, encoding="cp1252", errors="strict", newline="")
    err = io.TextIOWrapper(err_raw, encoding="cp1252", errors="strict", newline="")
    monkeypatch.setattr(cli.sys, "stdout", out)
    monkeypatch.setattr(cli.sys, "stderr", err)

    cli._ensure_utf8_streams()

    assert cli.sys.stdout.encoding.lower() == "utf-8"
    assert cli.sys.stderr.encoding.lower() == "utf-8"
    cli.sys.stdout.write(_BOM + "abc")
    cli.sys.stdout.flush()
    assert out_raw.getvalue() == (_BOM + "abc").encode("utf-8")


def test_ensure_utf8_streams_noop_without_reconfigure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Streams lacking `.reconfigure` (pytest capsys, CliRunner, closed pipes)
    are skipped without raising."""

    class _NoReconfigure:
        def write(self, s: str) -> int:
            return len(s)

        def flush(self) -> None:
            pass

    monkeypatch.setattr(cli.sys, "stdout", _NoReconfigure())
    monkeypatch.setattr(cli.sys, "stderr", _NoReconfigure())
    # Must not raise.
    cli._ensure_utf8_streams()


def test_ensure_utf8_streams_swallows_reconfigure_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A stream whose `.reconfigure` raises ValueError/OSError is tolerated."""

    class _BadReconfigure:
        def reconfigure(self, **_kw: object) -> None:
            raise ValueError("cannot reconfigure")

        def write(self, s: str) -> int:
            return len(s)

        def flush(self) -> None:
            pass

    monkeypatch.setattr(cli.sys, "stdout", _BadReconfigure())
    monkeypatch.setattr(cli.sys, "stderr", _BadReconfigure())
    # Must not raise.
    cli._ensure_utf8_streams()


# --------------------------------------------------------------------------
# Defect 2: documented `python -m groundtruth_kb` fallback is real
# --------------------------------------------------------------------------


def test_module_entrypoint_routes_to_cli() -> None:
    """`python -m groundtruth_kb` delegates to the same `cli.main`, so
    `python -m groundtruth_kb hygiene sweep` is behavior-identical to
    `gt hygiene sweep` (the WI-4250 portability fallback)."""
    import groundtruth_kb.__main__ as entry

    assert entry.main is cli.main


# --------------------------------------------------------------------------
# End-to-end: the deliberations-search path that triggered Defect 1
# --------------------------------------------------------------------------


def test_deliberations_search_handles_bom_title(monkeypatch: pytest.MonkeyPatch) -> None:
    """`deliberations search` formats a BOM-prefixed title without error."""

    class _FakeDB:
        def __init__(self, *_a: object, **_k: object) -> None:
            pass

        def search_deliberations(self, _query: str, *, limit: int = 5) -> list[dict[str, object]]:
            return [
                {
                    "id": "DELIB-9999",
                    "version": 1,
                    "title": _BOM + "BOM Title",
                    "summary": "a summary",
                    "search_method": "semantic",
                    "score": 0.9,
                }
            ]

    fake_cfg = types.SimpleNamespace(db_path=":memory:", chroma_path=None)
    monkeypatch.setattr(cli, "_resolve_config", lambda _ctx: fake_cfg)
    monkeypatch.setattr(cli, "KnowledgeDB", _FakeDB)

    result = CliRunner().invoke(cli.main, ["deliberations", "search", "anything"])

    assert result.exit_code == 0, result.output
    assert "BOM Title" in result.output
