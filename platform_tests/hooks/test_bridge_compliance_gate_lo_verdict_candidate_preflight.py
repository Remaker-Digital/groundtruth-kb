"""WI-5554 verdict applicability evidence freshness tests."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

from scripts import bridge_applicability_preflight as preflight

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"
HOOKS = ((LIVE_HOOK, "live"), (TEMPLATE_HOOK, "template"))


def _load_gate(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"wi5554_bridge_gate_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=HOOKS)
def gate(request: pytest.FixtureRequest) -> ModuleType:
    path, name = request.param
    return _load_gate(path, name)


def _project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    root = tmp_path / "project"
    bridge_dir = root / "bridge"
    config_dir = root / "config" / "governance"
    bridge_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)
    (root / "groundtruth.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
    (config_dir / "spec-applicability.toml").write_text("rules = []\n", encoding="utf-8")
    source = bridge_dir / "topic-001.md"
    source.write_text(
        "NEW\n"
        "::init gtkb pb\n"
        "::open build\n\n"
        "bridge_kind: prime_proposal\n"
        "Document: topic\n"
        "Version: 001\n"
        'target_paths: ["scripts/example.py"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(preflight, "PROJECT_ROOT", root)
    return root, source


def _candidate(
    gate: ModuleType,
    root: Path,
    source: Path,
    *,
    status: str = "GO",
    file_path: str = "bridge/topic-002.md",
    source_anchor: str = "bridge/topic-001.md",
) -> str:
    packet = preflight.build_packet(
        bridge_id="topic",
        bridge_dir=root / "bridge",
        config_path=root / "config" / "governance" / "spec-applicability.toml",
        db_path=root / "groundtruth.db",
        content_file=source,
    )
    content = (
        f"{status}\n"
        "::init gtkb lo\n"
        "::open test\n\n"
        "author_identity: loyal-opposition/test/Z\n"
        "author_harness_id: Z\n"
        "author_session_context_id: reviewer-session\n"
        "author_model: fixture-model\n"
        "author_model_version: fixture-version\n"
        "author_model_configuration: fixture-configuration\n\n"
        "bridge_kind: lo_verdict\n"
        "Document: topic\n"
        "Version: 002\n"
        "Responds to: bridge/topic-001.md\n\n"
        "## Applicability Preflight\n\n"
        f"- packet_hash: `{packet['packet_hash']}`\n"
        "- bridge_document_name: `topic`\n"
        f"- content_file: `{source_anchor}`\n"
        "- operative_file: `bridge/topic-001.md`\n"
        "- missing_required_specs: []\n"
        f"- candidate_evidence_hash: `{gate.CANDIDATE_EVIDENCE_HASH_SENTINEL}`\n"
    )
    expected_hash = gate._candidate_evidence_hash(file_path, content, root)
    assert expected_hash is not None
    return content.replace(gate.CANDIDATE_EVIDENCE_HASH_SENTINEL, expected_hash)


def _freshness_reason(gate: ModuleType, root: Path, file_path: str, content: str) -> str | None:
    return gate._verdict_preflight_freshness_deny_reason(
        cwd_path=root,
        file_path=file_path,
        content=content,
    )


def test_pending_candidate_status_set_is_unchanged(gate: ModuleType) -> None:
    assert {"NEW", "REVISED"} == gate.PENDING_PREFLIGHT_STATUSES


@pytest.mark.parametrize("status", ("GO", "VERIFIED"))
def test_valid_go_and_verified_without_specification_links_pass_freshness(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    content = _candidate(gate, root, source, status=status)

    assert "Specification Links" not in content
    assert _freshness_reason(gate, root, "bridge/topic-002.md", content) is None


def test_no_go_without_applicability_section_remains_allowed(gate: ModuleType, tmp_path: Path) -> None:
    content = "NO-GO\nResponds to: bridge/topic-001.md\n"

    assert _freshness_reason(gate, tmp_path, "bridge/topic-002.md", content) is None


def test_no_go_with_valid_applicability_section_passes(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    content = _candidate(gate, root, source, status="NO-GO")

    assert _freshness_reason(gate, root, "bridge/topic-002.md", content) is None


@pytest.mark.parametrize(
    ("replacement", "expected_fragment"),
    (
        ("bridge/other-001.md", "source mismatch"),
        ("bridge/topic-000.md", "same bridge thread"),
    ),
)
def test_wrong_thread_or_version_source_is_denied(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    replacement: str,
    expected_fragment: str,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    other = root / "bridge" / "other-001.md"
    other.write_text(source.read_text(encoding="utf-8").replace("Document: topic", "Document: other"), encoding="utf-8")
    content = _candidate(gate, root, source)
    if replacement == "bridge/other-001.md":
        content = content.replace("content_file: `bridge/topic-001.md`", f"content_file: `{replacement}`")
    else:
        content = content.replace("Responds to: bridge/topic-001.md", f"Responds to: {replacement}")
    expected_hash = gate._candidate_evidence_hash("bridge/topic-002.md", content, root)
    assert expected_hash is not None
    content = gate.CANDIDATE_EVIDENCE_HASH_LINE_RE.sub(
        lambda match: match.group("prefix") + expected_hash + match.group("suffix"),
        content,
    )

    reason = _freshness_reason(gate, root, "bridge/topic-002.md", content)

    assert reason is not None
    assert expected_fragment in reason


def test_stale_packet_hash_is_denied(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    content = _candidate(gate, root, source)
    packet_match = gate.PREFLIGHT_PACKET_HASH_RE.search(content)
    assert packet_match is not None
    packet_hash = packet_match.group(0).split("`")[1]
    flipped_digit = "0" if packet_hash[7] != "0" else "1"
    content = content.replace(packet_hash, "sha256:" + flipped_digit + packet_hash[8:], 1)
    expected_hash = gate._candidate_evidence_hash("bridge/topic-002.md", content, root)
    assert expected_hash is not None
    content = gate.CANDIDATE_EVIDENCE_HASH_LINE_RE.sub(
        lambda match: match.group("prefix") + expected_hash + match.group("suffix"),
        content,
    )

    reason = _freshness_reason(gate, root, "bridge/topic-002.md", content)

    assert reason is not None
    assert "stale packet_hash" in reason


def test_one_byte_candidate_mutation_is_denied_with_expected_hash(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    content = _candidate(gate, root, source) + "x"
    expected_hash = gate._candidate_evidence_hash("bridge/topic-002.md", content, root)
    assert expected_hash is not None

    reason = _freshness_reason(gate, root, "bridge/topic-002.md", content)

    assert reason is not None
    assert "candidate_evidence_hash" in reason
    assert expected_hash in reason


def test_crlf_and_backslash_candidate_path_normalize_identically(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    content = _candidate(gate, root, source).replace("\n", "\r\n")

    assert _freshness_reason(gate, root, r"bridge\topic-002.md", content) is None


def test_active_writer_audit_path_denies_stale_candidate(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    content = _candidate(gate, root, source) + "x"
    with patch.object(gate, "_verdict_self_review_deny", return_value=None):
        reason = gate._deny_reason_for_content(
            cwd_path=root,
            file_path=str(root / "bridge" / "topic-002.md"),
            content=content,
            run_pending_preflight=False,
        )

    assert reason is not None
    assert "candidate_evidence_hash" in reason


def test_verdict_packet_hash_survives_membase_absence_between_phases(
    gate: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, source = _project(tmp_path, monkeypatch)
    (root / "config" / "governance" / "spec-applicability.toml").write_text(
        """
[[rules]]
spec_id = "SPEC-ENVIRONMENT-DESCRIPTION-001"
severity = "advisory"
rationale = "Fixture environment description."
applies_when_doc_matches = ["topic"]
""",
        encoding="utf-8",
    )
    db_path = root / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE current_specifications (id TEXT PRIMARY KEY, title TEXT, status TEXT, type TEXT)")
        conn.execute(
            "INSERT INTO current_specifications VALUES (?, ?, ?, ?)",
            (
                "SPEC-ENVIRONMENT-DESCRIPTION-001",
                "Worktree-only description",
                "specified",
                "specification",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    content = _candidate(gate, root, source, status="VERIFIED")
    db_path.unlink()

    assert _freshness_reason(gate, root, "bridge/topic-002.md", content) is None


def test_active_and_template_hooks_remain_byte_identical() -> None:
    assert LIVE_HOOK.read_bytes() == TEMPLATE_HOOK.read_bytes()
