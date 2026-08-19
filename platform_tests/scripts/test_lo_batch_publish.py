"""WI-5939: specification-derived tests for the governed LO batch publisher.

Each test below is derived from a specification clause cited in
`bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-001.md`:

| Test | Derived from |
|------|--------------|
| T1 | `.claude/rules/file-bridge-protocol.md` Review Independence Boundary |
| T2 | same (fail-closed clause) + `.claude/rules/codex-review-gate.md` Review Independence Gate |
| T3 | `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` |
| T4 | `GOV-FILE-BRIDGE-AUTHORITY-001` (truthful audit-trail provenance) |
| T5 | `.claude/rules/deliberation-protocol.md` (mandatory search; no false claim) |
| T6 | `.claude/rules/bridge-essential.md`, `DELIB-202667526` (serialized contended publication) |
| T7 | `.claude/rules/codex-decision-ledger.md` tracked-surface bias |

The predecessor publisher these tests guard against embedded a fixed session id,
a fixed date, and a boilerplate independence sentence that was printed rather
than computed. T1-T5 exist so that class of defect cannot return silently.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "lo_batch_publish.py"

UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

REVIEWER_SESSION = "11111111-2222-3333-4444-555555555555"
AUTHOR_SESSION = "99999999-8888-7777-6666-555555555555"


def _load_module():
    spec = importlib.util.spec_from_file_location("lo_batch_publish", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["lo_batch_publish"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load_module()


@pytest.fixture
def author_metadata():
    return {
        "author_identity": "loyal-opposition/cursor",
        "author_harness_id": "E",
        "author_session_context_id": REVIEWER_SESSION,
        "author_model": "test-model",
        "author_model_version": "test-model-version",
        "author_model_configuration": "unit test",
    }


def _write_artifact(
    path: Path, *, author_session: str | None, status: str = "NEW"
) -> Path:
    lines = [status, ""]
    if author_session is not None:
        lines.append(f"author_session_context_id: {author_session}")
    lines += ["", "# body", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# T1 / T2 - review independence is computed and fails closed
# ---------------------------------------------------------------------------


def test_t1_self_review_is_refused(mod, tmp_path):
    """Publication is refused when the reviewer session authored the predecessor."""
    artifact = _write_artifact(
        tmp_path / "thread-001.md", author_session=REVIEWER_SESSION
    )
    with pytest.raises(mod.ReviewIndependenceError) as excinfo:
        mod.assert_review_independence(REVIEWER_SESSION, artifact)
    assert "self-review refused" in str(excinfo.value)


def test_t2_missing_author_session_fails_closed(mod, tmp_path):
    """Missing author session metadata fails closed rather than assuming independence."""
    artifact = _write_artifact(tmp_path / "thread-001.md", author_session=None)
    with pytest.raises(mod.ReviewIndependenceError) as excinfo:
        mod.assert_review_independence(REVIEWER_SESSION, artifact)
    assert "cannot be verified" in str(excinfo.value)


def test_t2_unreadable_artifact_fails_closed(mod, tmp_path):
    """An unreadable predecessor fails closed (no silent independence claim)."""
    missing = tmp_path / "does-not-exist-001.md"
    with pytest.raises(mod.ReviewIndependenceError):
        mod.assert_review_independence(REVIEWER_SESSION, missing)


def test_t1_distinct_sessions_are_accepted(mod, tmp_path):
    """A genuinely independent predecessor returns its author session."""
    artifact = _write_artifact(
        tmp_path / "thread-001.md", author_session=AUTHOR_SESSION
    )
    assert mod.assert_review_independence(REVIEWER_SESSION, artifact) == AUTHOR_SESSION


# ---------------------------------------------------------------------------
# T3 - runtime session provenance, no embedded session literal
# ---------------------------------------------------------------------------


def test_t3_no_hardcoded_uuid_literal_in_module():
    """No session-id literal may be embedded in the publisher source."""
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert not UUID_RE.search(source), (
        "a UUID literal is embedded in the publisher; session provenance must be resolved at runtime"
    )


def test_t3_body_carries_runtime_session(mod, author_metadata):
    """The emitted body records the resolved runtime session, not a constant."""
    body = mod.build_body(
        {"slug": "thread", "verdict": "GO", "summary": "ok"},
        next_version=2,
        responds="bridge/thread-001.md",
        author_metadata=author_metadata,
        reviewer_session=REVIEWER_SESSION,
        predecessor_session=AUTHOR_SESSION,
        published_date="2026-01-01",
    )
    assert f"author_session_context_id: {REVIEWER_SESSION}" in body
    assert REVIEWER_SESSION in body and AUTHOR_SESSION in body


def test_t3_provenance_fails_closed_without_session(mod, tmp_path, monkeypatch):
    """Unresolvable session provenance raises rather than substituting a placeholder."""
    monkeypatch.setattr(
        mod, "load_author_metadata", lambda *a, **k: {"author_identity": "lo/cursor"}
    )
    with pytest.raises(mod.PublisherProvenanceError):
        mod.resolve_publisher_identity(tmp_path, env={})


# ---------------------------------------------------------------------------
# T4 - runtime date, no embedded date literal
# ---------------------------------------------------------------------------


def test_t4_no_hardcoded_iso_date_literal_in_module():
    """No ISO date literal may be embedded in the publisher source."""
    source = MODULE_PATH.read_text(encoding="utf-8")
    found = ISO_DATE_RE.findall(source)
    assert not found, f"ISO date literal(s) embedded in publisher: {found}"


def test_t4_body_uses_supplied_runtime_date(mod, author_metadata):
    """The Date line reflects the date passed in at publication time."""
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    body = mod.build_body(
        {"slug": "thread", "verdict": "GO", "summary": "ok"},
        next_version=2,
        responds="bridge/thread-001.md",
        author_metadata=author_metadata,
        reviewer_session=REVIEWER_SESSION,
        predecessor_session=AUTHOR_SESSION,
        published_date=today,
    )
    assert f"Date: {today} UTC" in body


# ---------------------------------------------------------------------------
# T5 - deliberation honesty
# ---------------------------------------------------------------------------


def test_t5_absent_deliberations_disclose_rather_than_claim(mod):
    """With no supplied citations, the body discloses what was done, not a result."""
    rendered = mod.prior_deliberations_markdown({"slug": "thread"})
    assert (
        "No deliberation search was performed by this publishing transport" in rendered
    )
    assert "not a finding that no prior deliberations exist" in rendered


def test_t5_supplied_deliberations_are_rendered(mod):
    """Reviewer-supplied citations are rendered verbatim."""
    rendered = mod.prior_deliberations_markdown(
        {"prior_deliberations": ["DELIB-1", "DELIB-2"]}
    )
    assert "- DELIB-1" in rendered and "- DELIB-2" in rendered
    assert "No deliberation search was performed" not in rendered


# ---------------------------------------------------------------------------
# T6 - serialization and throttling
# ---------------------------------------------------------------------------


def test_t6_batch_publication_is_throttled(mod, monkeypatch, author_metadata):
    """Successive publications are separated by the configured minimum interval."""
    slept: list[float] = []
    monkeypatch.setattr(
        mod, "resolve_publisher_identity", lambda *a, **k: author_metadata
    )
    monkeypatch.setattr(
        mod, "publish_one", lambda item, **kwargs: {"slug": item["slug"], "ok": True}
    )

    items = [{"slug": f"thread-{i}", "verdict": "GO"} for i in range(4)]
    results = mod.publish_batch(items, min_interval_seconds=7.5, sleep=slept.append)

    assert len(results) == 4
    assert all(result["ok"] for result in results)
    # One inter-publication delay between each adjacent pair; none before the first.
    assert slept == [7.5, 7.5, 7.5]


def test_t6_no_delay_before_first_publication(mod, monkeypatch, author_metadata):
    """A single-item batch publishes without an artificial leading delay."""
    slept: list[float] = []
    monkeypatch.setattr(
        mod, "resolve_publisher_identity", lambda *a, **k: author_metadata
    )
    monkeypatch.setattr(
        mod, "publish_one", lambda item, **kwargs: {"slug": item["slug"], "ok": True}
    )

    mod.publish_batch(
        [{"slug": "only", "verdict": "GO"}],
        min_interval_seconds=5.0,
        sleep=slept.append,
    )
    assert slept == []


def test_t6_contention_is_retried_with_exponential_backoff(
    mod, tmp_path, monkeypatch, author_metadata
):
    """Contention-shaped publication failures back off exponentially, then succeed."""
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    _write_artifact(bridge / "thread-001.md", author_session=AUTHOR_SESSION)

    slept: list[float] = []
    attempts = {"n": 0}

    def flaky(*args, **kwargs):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError(
                "another bridge publication capability is active for bridge/x.md"
            )

        class _Published:
            def to_dict(self):
                return {"verdict_path": "bridge/thread-002.md"}

        return _Published()

    monkeypatch.setattr(
        mod, "prepare_verdict_candidate", lambda **kwargs: kwargs["content"]
    )
    monkeypatch.setattr(mod, "acquire", lambda *a, **k: True)
    monkeypatch.setattr(mod, "release", lambda *a, **k: None)
    monkeypatch.setattr(mod, "publish_lo_verdict", flaky)

    result = mod.publish_one(
        {"slug": "thread", "verdict": "GO", "summary": "ok"},
        project_root=tmp_path,
        author_metadata=author_metadata,
        backoff_base_seconds=2.0,
        sleep=slept.append,
    )

    assert result["ok"] is True
    assert result["attempts"] == 3
    assert slept == [2.0, 4.0]


def test_t6_non_contention_failure_is_not_retried(
    mod, tmp_path, monkeypatch, author_metadata
):
    """A deterministic (non-contention) failure fails fast instead of spinning."""
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    _write_artifact(bridge / "thread-001.md", author_session=AUTHOR_SESSION)

    slept: list[float] = []

    def boom(*args, **kwargs):
        raise ValueError("malformed verdict body")

    monkeypatch.setattr(
        mod, "prepare_verdict_candidate", lambda **kwargs: kwargs["content"]
    )
    monkeypatch.setattr(mod, "acquire", lambda *a, **k: True)
    monkeypatch.setattr(mod, "release", lambda *a, **k: None)
    monkeypatch.setattr(mod, "publish_lo_verdict", boom)

    result = mod.publish_one(
        {"slug": "thread", "verdict": "GO", "summary": "ok"},
        project_root=tmp_path,
        author_metadata=author_metadata,
        sleep=slept.append,
    )

    assert result["ok"] is False
    assert "ValueError" in result["error"]
    assert slept == []


def test_t6_non_actionable_predecessor_is_refused(mod, tmp_path, author_metadata):
    """A predecessor whose latest status is terminal is not published over."""
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    _write_artifact(
        bridge / "thread-001.md", author_session=AUTHOR_SESSION, status="VERIFIED"
    )

    result = mod.publish_one(
        {"slug": "thread", "verdict": "GO"},
        project_root=tmp_path,
        author_metadata=author_metadata,
    )
    assert result["ok"] is False
    assert result["error"].startswith("latest_status_not_actionable:VERIFIED")


def test_publish_one_retries_occupancy_with_fresh_slug_listing(
    mod, tmp_path, monkeypatch, author_metadata
):
    """A lost create rebuilds Version from a fresh per-slug listing, not latest+1 once."""
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    _write_artifact(bridge / "thread-001.md", author_session=AUTHOR_SESSION)
    versions: list[int] = []
    slept: list[float] = []

    class _Published:
        def to_dict(self):
            return {"verdict_path": "bridge/thread-003.md"}

    def flaky(_slug, _verdict, body, _project_root, **_kwargs):
        match = re.search(r"(?im)^Version:\s*`?(\d{3})", body)
        assert match is not None
        version = int(match.group(1))
        versions.append(version)
        if len(versions) == 1:
            (bridge / "thread-002.md").write_text("GO\nracer\n", encoding="utf-8")
            raise RuntimeError(
                "bridge/thread-002.md already exists; refusing to overwrite"
            )
        return _Published()

    monkeypatch.setattr(
        mod, "prepare_verdict_candidate", lambda **kwargs: kwargs["content"]
    )
    monkeypatch.setattr(mod, "acquire", lambda *a, **k: True)
    monkeypatch.setattr(mod, "release", lambda *a, **k: None)
    monkeypatch.setattr(mod, "publish_lo_verdict", flaky)

    result = mod.publish_one(
        {"slug": "thread", "verdict": "GO", "summary": "ok", "version": 2},
        project_root=tmp_path,
        author_metadata=author_metadata,
        backoff_base_seconds=0.5,
        sleep=slept.append,
    )

    assert result["ok"] is True
    assert versions == [2, 3]
    assert result["attempts"] == 2
    assert slept == [0.5]


# ---------------------------------------------------------------------------
# T7 - tracked-surface bias
# ---------------------------------------------------------------------------


def test_t7_module_lives_on_the_tracked_surface():
    """The publisher is a tracked module, not a runtime-state script."""
    assert MODULE_PATH.is_file()
    assert MODULE_PATH.parent.name == "scripts"


def test_t7_module_does_not_depend_on_runtime_state_paths(mod):
    """The publisher imports and runs without any .gtkb-state dependency."""
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert ".gtkb-state" not in source
    assert mod.PROJECT_ROOT == REPO_ROOT
