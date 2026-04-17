# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the /gtkb-bridge-propose skill helper.

Covers the full contract:

- Scan catalog is credential-only (PII excluded).
- Redaction is overlap-safe (normalization, reverse replacement,
  post-scan gate).
- INDEX update is atomic, retry-safe, and idempotent using EXACT
  line matching.
- Proposal writer is file-first, refuses silent overwrite, and
  enforces the **2 total attempts** retry budget.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from groundtruth_kb import get_templates_dir

_HELPER_PATH = Path(get_templates_dir()) / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"


def _load_helper() -> ModuleType:
    """Import ``write_bridge`` from the template tree into a stable module name.

    The helper lives under ``templates/skills/...`` and is not on
    the default Python path. Load by file path so every test uses
    the same module reference (mirrors the decision-capture helper
    test pattern).
    """
    module_name = "gtkb_test_bridge_propose_helper"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(module_name, _HELPER_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load helper from {_HELPER_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Runtime-assembled credential samples (so the source file itself is clean).
# ---------------------------------------------------------------------------


def _synthetic_ar_live_key() -> str:
    """Construct an ``ar_live_``-shaped credential at runtime."""
    return "ar" + "_live_" + "TESTTOKEN123456"


def _synthetic_aws_key() -> str:
    """Construct an AWS access key ID shape at runtime."""
    return "AK" + "IA" + "ABCDEFGHIJKLMNOP"


def _synthetic_anthropic_key() -> str:
    """Construct an Anthropic API key shape at runtime."""
    return "sk" + "-ant-api" + "03-" + "ABCDEFGHIJKLMNOP1234567890_-xyz"


def _synthetic_bearer_header() -> str:
    """Construct an ``Authorization: Bearer <token>`` sample at runtime."""
    return "Authorization: " + "Bearer " + "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789"


# ---------------------------------------------------------------------------
# Phase 1 — Scan catalog: credential-only, PII excluded.
# ---------------------------------------------------------------------------


def test_scan_allows_email() -> None:
    """Email addresses are PII — must NOT be detected by the credential scan."""
    helper = _load_helper()
    hits = helper.scan_credential_hits("Contact support@example.com for details.")
    names = {h["pattern_name"] for h in hits}
    assert "email" not in names, f"PII 'email' leaked into credential scan: {names}"
    # The scan should return empty for a PII-only sample.
    assert not hits, f"credential scan returned hits on PII-only content: {hits}"


def test_scan_allows_phone() -> None:
    """Phone numbers are PII — must NOT be detected by the credential scan."""
    helper = _load_helper()
    hits = helper.scan_credential_hits("Call +15551234567 or +442012345678.")
    names = {h["pattern_name"] for h in hits}
    assert "phone" not in names, f"PII 'phone' leaked into credential scan: {names}"
    assert not hits, f"credential scan returned hits on phone-only content: {hits}"


def test_scan_allows_ipv4() -> None:
    """IPv4 addresses are PII — must NOT be detected by the credential scan."""
    helper = _load_helper()
    hits = helper.scan_credential_hits("Server 192.168.1.1 responded from 10.0.0.1.")
    names = {h["pattern_name"] for h in hits}
    assert "ip_address" not in names, f"PII 'ip_address' leaked into credential scan: {names}"
    assert not hits, f"credential scan returned hits on IPv4-only content: {hits}"


def test_scan_detects_ar_live_key() -> None:
    """Runtime-assembled ``ar_live_`` key is detected."""
    helper = _load_helper()
    body = f"Rotate {_synthetic_ar_live_key()} soon."
    hits = helper.scan_credential_hits(body)
    names = {h["pattern_name"] for h in hits}
    assert "ar_live_key" in names, f"ar_live_key not detected; got {names}"


def test_scan_detects_aws_key() -> None:
    """Runtime-assembled AWS key ID is detected (under both ``aws_key`` and ``bash_aws_key``)."""
    helper = _load_helper()
    body = f"Key is {_synthetic_aws_key()} in config."
    hits = helper.scan_credential_hits(body)
    names = {h["pattern_name"] for h in hits}
    # Both DB-scope (aws_key) and BASH-scope (bash_aws_key) match the same span.
    assert "aws_key" in names, f"aws_key not detected; got {names}"
    assert "bash_aws_key" in names, f"bash_aws_key not detected; got {names}"


def test_scan_detects_anthropic_api_key() -> None:
    """Runtime-assembled Anthropic API key is detected."""
    helper = _load_helper()
    body = f"Secret: {_synthetic_anthropic_key()} in env."
    hits = helper.scan_credential_hits(body)
    names = {h["pattern_name"] for h in hits}
    assert "anthropic_api_key" in names, f"anthropic_api_key not detected; got {names}"


# ---------------------------------------------------------------------------
# Phase 2 — Redaction (overlap-safe).
# ---------------------------------------------------------------------------


def test_redact_nested_api_key_plus_aws_key() -> None:
    """``api_key=AKIA...`` produces nested hits; a single outer redaction wins."""
    helper = _load_helper()
    body = f"api_key={_synthetic_aws_key()} end"
    hits = helper.scan_credential_hits(body)
    assert hits, "expected at least one hit for api_key=AKIA... sample"

    intervals = helper._normalize_hit_intervals(hits)
    # One merged interval, labelled 'api_key' (the outermost/earliest-start spec).
    assert len(intervals) == 1, f"expected 1 merged interval; got {intervals}"
    start, end, label = intervals[0]
    assert label == "api_key", f"expected outer label 'api_key'; got {label!r}"
    # Interval must span the entire api_key=AKIA... credential chunk.
    assert start == 0, f"expected merged start at 0; got {start}"

    redacted = helper.redact_credential_hits(body, hits)
    # Exactly one redaction marker in the output — no corruption.
    assert redacted.count("[REDACTED:api_key]") == 1
    # Re-scan clean.
    assert not helper.scan_credential_hits(redacted)


def test_redact_bearer_plus_anthropic() -> None:
    """``Authorization: Bearer sk-ant-api...`` collapses into one outer redaction."""
    helper = _load_helper()
    body = f"{_synthetic_bearer_header()[: len(_synthetic_bearer_header()) - 30]}{_synthetic_anthropic_key()}"
    hits = helper.scan_credential_hits(body)
    assert hits, "expected hits for Bearer + Anthropic sample"

    intervals = helper._normalize_hit_intervals(hits)
    # All overlapping hits must collapse into a single interval labelled by
    # the outermost (earliest-start) spec — bearer_header.
    assert len(intervals) == 1, f"expected 1 merged interval; got {intervals}"
    _, _, label = intervals[0]
    assert label == "bearer_header", f"expected outer label 'bearer_header'; got {label!r}"

    redacted = helper.redact_credential_hits(body, hits)
    assert redacted.count("[REDACTED:bearer_header]") == 1
    assert not helper.scan_credential_hits(redacted)


def test_redact_duplicate_same_span_db_and_bash() -> None:
    """Duplicate hits covering the identical span collapse to one redaction.

    Uses hand-crafted hits (not the live catalog) to pin the exact duplicate
    scenario: ``aws_key`` and ``bash_aws_key`` both covering ``(0, 20)``.
    """
    helper = _load_helper()
    # Hand-crafted duplicate hits.
    hits: list[dict[str, Any]] = [
        {"pattern_name": "aws_key", "pattern_description": "AWS access key ID", "span": (0, 20)},
        {"pattern_name": "bash_aws_key", "pattern_description": "Bash AWS access key ID", "span": (0, 20)},
    ]
    intervals = helper._normalize_hit_intervals(hits)
    assert len(intervals) == 1, f"expected 1 merged interval; got {intervals}"
    start, end, label = intervals[0]
    assert (start, end) == (0, 20)
    # First-sorted label wins for identical spans. Because ``(0, 20)`` and
    # ``-end=-20`` are equal for both, the stable sort preserves input order;
    # aws_key comes first in the hits list.
    assert label == "aws_key", f"expected first-sorted label 'aws_key'; got {label!r}"


def test_redact_nonoverlapping_multiple() -> None:
    """Two non-overlapping credentials yield two separate redactions in stable order."""
    helper = _load_helper()
    ar_key = _synthetic_ar_live_key()
    ant_key = _synthetic_anthropic_key()
    body = f"first={ar_key} middle second={ant_key} end"
    hits = helper.scan_credential_hits(body)
    intervals = helper._normalize_hit_intervals(hits)
    assert len(intervals) == 2, f"expected 2 non-overlapping intervals; got {intervals}"
    # Intervals must be sorted by start ascending.
    assert intervals[0][0] < intervals[1][0], f"intervals must be start-ascending; got {intervals}"

    redacted = helper.redact_credential_hits(body, hits)
    # Two redaction markers in the output.
    assert redacted.count("[REDACTED:") == 2
    # Re-scan clean.
    assert not helper.scan_credential_hits(redacted)


def test_redact_then_rescan_clean() -> None:
    """End-to-end: redact + re-scan returns empty for all tested credential shapes."""
    helper = _load_helper()
    body = f"Key: {_synthetic_ar_live_key()} AWS: {_synthetic_aws_key()} Anthropic: {_synthetic_anthropic_key()}"
    hits = helper.scan_credential_hits(body)
    assert hits, "expected hits in the multi-credential body"
    redacted = helper.redact_credential_hits(body, hits)
    assert not helper.scan_credential_hits(redacted), f"re-scan found residual hits: {redacted!r}"


def test_redact_residual_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Post-redaction re-scan detecting residual hits raises RedactionResidualError.

    Monkey-patches ``redact_credential_hits`` to return the original body
    unchanged; the re-scan then still finds hits and the helper raises.
    """
    helper = _load_helper()
    body = f"key={_synthetic_ar_live_key()} end"
    hits = helper.scan_credential_hits(body)
    assert hits, "expected hits in the sample body"

    def _broken_redact(content: str, hits: list[dict[str, Any]]) -> str:  # noqa: ARG001
        # Intentionally broken: returns the original content unchanged, so the
        # re-scan will still find hits and the helper must abort.
        return content

    monkeypatch.setattr(helper, "redact_credential_hits", _broken_redact)
    with pytest.raises(helper.RedactionResidualError):
        helper.handle_hits_abort_or_redact(body, hits, mode="redact")


# ---------------------------------------------------------------------------
# Phase 3 — INDEX merge + retry.
# ---------------------------------------------------------------------------


_INDEX_HEADER = """\
# Project — File Bridge Index

<!-- This file is the single coordination artifact for the Prime Builder ↔
     Loyal Opposition file bridge. Both agents read and write this file.
     Newest entries are at the top. -->

## Statuses

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime | Fresh proposal awaiting review |

<!-- Add new document entries below this line -->

"""


def _write_fresh_index(path: Path) -> None:
    """Write a minimal valid INDEX.md with the standard header block."""
    path.write_text(_INDEX_HEADER, encoding="utf-8")


def test_update_bridge_index_inserts_after_header_comments(tmp_path: Path) -> None:
    """Entry is inserted after the header comment region, not at byte 0."""
    helper = _load_helper()
    index_path = tmp_path / "INDEX.md"
    _write_fresh_index(index_path)
    entry = "Document: sample-topic\nNEW: bridge/sample-topic-001.md\n"
    helper._update_bridge_index(index_path, entry, topic_slug="sample-topic")

    content = index_path.read_text(encoding="utf-8")
    # The entry must appear after the header block.
    header_end = content.find("<!-- Add new document entries below this line -->")
    entry_pos = content.find("Document: sample-topic")
    assert header_end > 0, "header marker missing in test fixture"
    assert entry_pos > header_end, "entry must follow the header block, not precede it"


def test_update_bridge_index_is_atomic_via_os_replace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``_update_bridge_index`` writes via temp file + ``os.replace``.

    Assertion: an ``os.replace`` call from temp file to the index path
    occurs. We monkey-patch ``os.replace`` to record the transition.
    """
    import os as _os

    helper = _load_helper()
    index_path = tmp_path / "INDEX.md"
    _write_fresh_index(index_path)

    calls: list[tuple[str, str]] = []
    orig_replace = _os.replace

    def _recording_replace(src: str | Path, dst: str | Path) -> None:
        calls.append((str(src), str(dst)))
        orig_replace(src, dst)

    monkeypatch.setattr(helper.os, "replace", _recording_replace)
    entry = "Document: atomic-topic\nNEW: bridge/atomic-topic-001.md\n"
    helper._update_bridge_index(index_path, entry, topic_slug="atomic-topic")

    # Verify one replace call happened, from a temp file named with our INDEX stem.
    assert len(calls) == 1, f"expected 1 os.replace call; got {calls}"
    src, dst = calls[0]
    assert Path(dst).name == "INDEX.md", f"replace dst must be INDEX.md; got {dst}"
    assert ".tmp." in Path(src).name, f"replace src must be a temp file; got {src}"


def test_update_bridge_index_detects_concurrent_modification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Content changes between read and rename → BridgeIndexConflictError, temp cleaned up."""
    helper = _load_helper()
    index_path = tmp_path / "INDEX.md"
    _write_fresh_index(index_path)

    # Intercept read_bytes on the Path instance so the second read (pre-rename)
    # sees different content from the first read.
    original_read_bytes = Path.read_bytes
    state = {"calls": 0}

    def _racing_read_bytes(self: Path) -> bytes:
        result = original_read_bytes(self)
        state["calls"] += 1
        if self == index_path and state["calls"] == 2:
            # Between the first read (step 1) and the second read
            # (step 5 pre-rename), simulate a concurrent writer by
            # appending non-topic content to the file bytes in-flight.
            return result + b"\n# Concurrent writer appended content.\n"
        return result

    monkeypatch.setattr(Path, "read_bytes", _racing_read_bytes)

    entry = "Document: racing-topic\nNEW: bridge/racing-topic-001.md\n"
    with pytest.raises(helper.BridgeIndexConflictError) as excinfo:
        helper._update_bridge_index(index_path, entry, topic_slug="racing-topic")
    assert "changed during update" in str(excinfo.value).lower()

    # Temp file cleaned up.
    leftover = list(tmp_path.glob("INDEX.md.tmp.*"))
    assert not leftover, f"temp file not cleaned up on conflict; found {leftover}"


def test_update_bridge_index_detects_concurrent_same_topic(tmp_path: Path) -> None:
    """Pre-seeded ``Document: <topic>`` line → BridgeIndexConflictError on EXACT match.

    Uses exact-line matching: the sentinel ``Document: same-topic`` must be
    detected, not a merely-substring-similar line.
    """
    helper = _load_helper()
    index_path = tmp_path / "INDEX.md"
    content = _INDEX_HEADER + "Document: same-topic\nNEW: bridge/same-topic-001.md\n\n"
    index_path.write_text(content, encoding="utf-8")

    entry = "Document: same-topic\nNEW: bridge/same-topic-001.md\n"
    with pytest.raises(helper.BridgeIndexConflictError) as excinfo:
        helper._update_bridge_index(index_path, entry, topic_slug="same-topic")
    msg = str(excinfo.value)
    assert "same-topic" in msg
    assert "concurrently" in msg.lower() or "already has an entry" in msg.lower()


def test_update_bridge_index_exact_line_match_not_prefix(tmp_path: Path) -> None:
    """Slug-prefix collision is NOT flagged; exact line match avoids false positives.

    If substring matching were used, ``Document: foo-bar`` would false-match
    ``topic_slug='foo'``. Exact line matching correctly treats them as
    distinct topics.
    """
    helper = _load_helper()
    index_path = tmp_path / "INDEX.md"
    content = _INDEX_HEADER + "Document: foo-bar\nNEW: bridge/foo-bar-001.md\n\n"
    index_path.write_text(content, encoding="utf-8")

    # A fresh proposal with topic_slug='foo' must NOT trip the idempotency gate.
    entry = "Document: foo\nNEW: bridge/foo-001.md\n"
    helper._update_bridge_index(index_path, entry, topic_slug="foo")
    # Success: file now contains both topics.
    result = index_path.read_text(encoding="utf-8")
    assert "Document: foo-bar" in result
    assert "Document: foo\n" in result or result.rstrip().endswith("Document: foo")


# ---------------------------------------------------------------------------
# Phase 4 — Proposal writer.
# ---------------------------------------------------------------------------


def test_propose_bridge_writes_file_first_then_index(tmp_path: Path) -> None:
    """Happy path: clean body → bridge file on disk + INDEX entry inserted."""
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_fresh_index(bridge_dir / "INDEX.md")

    body = "Clean proposal body with no credentials."
    result_path = helper.propose_bridge(
        "clean-topic",
        body,
        mode="abort",
        bridge_dir=bridge_dir,
    )
    # File on disk.
    assert result_path.exists()
    assert result_path.read_text(encoding="utf-8") == body
    # INDEX entry inserted.
    index_content = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")
    assert "Document: clean-topic" in index_content
    assert "NEW: bridge/clean-topic-001.md" in index_content


def test_propose_bridge_refuses_silent_overwrite(tmp_path: Path) -> None:
    """Pre-existing ``bridge/<topic>-001.md`` → BridgeFileAlreadyExistsError before INDEX touch."""
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_fresh_index(bridge_dir / "INDEX.md")

    # Pre-seed the bridge file.
    target = bridge_dir / "occupied-topic-001.md"
    target.write_text("Previous content that must not be overwritten.", encoding="utf-8")
    original_index = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")

    with pytest.raises(helper.BridgeFileAlreadyExistsError) as excinfo:
        helper.propose_bridge(
            "occupied-topic",
            "New body that should not be written.",
            mode="abort",
            bridge_dir=bridge_dir,
        )
    assert "occupied-topic-001" in str(excinfo.value)

    # Pre-existing content untouched.
    assert target.read_text(encoding="utf-8") == "Previous content that must not be overwritten."
    # INDEX untouched.
    assert (bridge_dir / "INDEX.md").read_text(encoding="utf-8") == original_index


def test_propose_bridge_aborts_on_hits_when_mode_abort(tmp_path: Path) -> None:
    """mode='abort' + hits → CredentialHitsFoundError, no file, no INDEX change."""
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_fresh_index(bridge_dir / "INDEX.md")
    original_index = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")

    body = f"Forbidden content: {_synthetic_ar_live_key()}"
    with pytest.raises(helper.CredentialHitsFoundError):
        helper.propose_bridge("abort-topic", body, mode="abort", bridge_dir=bridge_dir)

    # Bridge file NOT created.
    assert not (bridge_dir / "abort-topic-001.md").exists()
    # INDEX unchanged.
    assert (bridge_dir / "INDEX.md").read_text(encoding="utf-8") == original_index


def test_propose_bridge_redacts_and_writes_when_mode_redact_and_clean(tmp_path: Path) -> None:
    """mode='redact' + hits → redacted body written, INDEX updated, no residual."""
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_fresh_index(bridge_dir / "INDEX.md")

    synthetic = _synthetic_ar_live_key()
    body = f"Rotate {synthetic} and report."
    result_path = helper.propose_bridge(
        "redact-topic",
        body,
        mode="redact",
        bridge_dir=bridge_dir,
    )
    written = result_path.read_text(encoding="utf-8")
    assert synthetic not in written, "raw credential must not persist after redaction"
    assert "[REDACTED:ar_live_key]" in written

    index_content = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")
    assert "Document: redact-topic" in index_content


# ---------------------------------------------------------------------------
# Phase 5 — Retry semantics (2 total attempts: 1 initial + 1 retry).
# ---------------------------------------------------------------------------


def test_propose_bridge_succeeds_after_one_concurrent_mod(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """1 concurrent mod → retry succeeds; **exactly 2 total attempts**."""
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_fresh_index(bridge_dir / "INDEX.md")

    attempt_counter = {"calls": 0}
    original_update = helper._update_bridge_index

    def _retrying_update(index_path: Path, new_entry: str, *, topic_slug: str) -> None:
        attempt_counter["calls"] += 1
        if attempt_counter["calls"] == 1:
            raise helper.BridgeIndexConflictError("simulated first-attempt conflict")
        # Second attempt: succeed via the original function.
        original_update(index_path, new_entry, topic_slug=topic_slug)

    monkeypatch.setattr(helper, "_update_bridge_index", _retrying_update)
    result_path = helper.propose_bridge(
        "retry-topic",
        "Retry-survival body.",
        mode="abort",
        bridge_dir=bridge_dir,
    )

    # Exactly 2 total attempts: 1 failed + 1 succeeded.
    assert attempt_counter["calls"] == 2, (
        f"expected exactly 2 total attempts (1 initial + 1 retry); got {attempt_counter['calls']}"
    )
    # Bridge file on disk, INDEX updated.
    assert result_path.exists()
    assert "Document: retry-topic" in (bridge_dir / "INDEX.md").read_text(encoding="utf-8")


def test_propose_bridge_aborts_after_2_concurrent_mods(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """2 concurrent mods → abort after exactly 2 total attempts.

    Assertion: the final exception message mentions '2 total attempts' so
    the comment, exception text, and test remain in lockstep per Codex
    ``-006`` Condition 3.
    """
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_fresh_index(bridge_dir / "INDEX.md")

    attempt_counter = {"calls": 0}

    def _always_conflicting_update(
        index_path: Path,  # noqa: ARG001
        new_entry: str,  # noqa: ARG001
        *,
        topic_slug: str,  # noqa: ARG001
    ) -> None:
        attempt_counter["calls"] += 1
        raise helper.BridgeIndexConflictError(f"simulated conflict #{attempt_counter['calls']}")

    monkeypatch.setattr(helper, "_update_bridge_index", _always_conflicting_update)

    with pytest.raises(helper.BridgeIndexConflictError) as excinfo:
        helper.propose_bridge(
            "persistent-conflict-topic",
            "Persistent-conflict body.",
            mode="abort",
            bridge_dir=bridge_dir,
        )

    # Exactly 2 total attempts — no more, no less.
    assert attempt_counter["calls"] == 2, f"expected exactly 2 total attempts; got {attempt_counter['calls']}"
    # Bridge file is on disk even though INDEX failed.
    assert (bridge_dir / "persistent-conflict-topic-001.md").exists()
    # Final error message uses the "2 total attempts" wording.
    assert "2 total attempts" in str(excinfo.value), (
        f"final error must mention '2 total attempts'; got: {excinfo.value}"
    )
