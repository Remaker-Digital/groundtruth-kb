"""Canon v8.92 status-vocabulary tests for scripts/bridge_applicability_preflight.py.

Owner ruling 2026-09-07: the preflight derives every status set from
groundtruth_kb.bridge.vocabulary. The operative file for a Loyal Opposition
preflight is the latest Prime-authored, Loyal-Opposition-actionable file (NEW,
REVISED, READY, VERDICT-REJECTED); verdicts are the Loyal-Opposition-authored
statuses minus ADVISORY; historical-inert tokens are recognised on read but are
never operative.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from groundtruth_kb.bridge.vocabulary import (
    ACCEPTED_ON_READ,
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
    LOYAL_OPPOSITION_AUTHORED_STATUSES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_applicability_preflight.py"

spec = importlib.util.spec_from_file_location("bridge_applicability_preflight_vocab", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
preflight = importlib.util.module_from_spec(spec)
sys.modules["bridge_applicability_preflight_vocab"] = preflight
spec.loader.exec_module(preflight)

SPEC_LINKS = "## Specification Links\n\n- ADR-ISOLATION-APPLICATION-PLACEMENT-001\n"
TARGET = 'target_paths: ["applications/Agent_Red/src/app.py"]\n\n'


def _write(root: Path, bridge_id: str, version: int, status: str, body: str) -> Path:
    bridge = root / "bridge"
    bridge.mkdir(exist_ok=True)
    path = bridge / f"{bridge_id}-{version:03d}.md"
    path.write_text(f"{status}\n\nDocument: {bridge_id}\nVersion: {version:03d}\n{body}", encoding="utf-8")
    return path


def _config(root: Path) -> Path:
    config = root / "spec-applicability.toml"
    config.write_text(
        "[[rules]]\n"
        'spec_id = "ADR-ISOLATION-APPLICATION-PLACEMENT-001"\n'
        'severity = "blocking"\n'
        'rationale = "placement"\n'
        'applies_when_paths_match = ["applications/**"]\n',
        encoding="utf-8",
    )
    return config


def _go_ready_chain(root: Path, bridge_id: str) -> None:
    _write(root, bridge_id, 1, "NEW", f"bridge_kind: prime_proposal\n{TARGET}{SPEC_LINKS}")
    _write(
        root,
        bridge_id,
        2,
        "GO",
        f"bridge_kind: lo_verdict\nResponds to: bridge/{bridge_id}-001.md\nApproved proposal: bridge/{bridge_id}-001.md\n",
    )
    _write(
        root,
        bridge_id,
        3,
        "READY",
        f"bridge_kind: implementation_report\nResponds to: bridge/{bridge_id}-002.md\n"
        f"Approved proposal: bridge/{bridge_id}-001.md\n{TARGET}{SPEC_LINKS}",
    )


@pytest.mark.parametrize("status", sorted(ACCEPTED_ON_READ))
def test_status_regex_recognizes_every_vocabulary_token(status: str) -> None:
    assert preflight._status_from_content(f"{status}\n\n# body\n") == status


def test_verdict_candidate_statuses_are_the_loyal_opposition_verdicts() -> None:
    assert LOYAL_OPPOSITION_AUTHORED_STATUSES - {"ADVISORY"} == preflight.VERDICT_CANDIDATE_STATUSES
    assert {"GO", "NO-GO", "NOT-READY", "VERIFIED"} <= preflight.VERDICT_CANDIDATE_STATUSES


def test_ready_implementation_report_is_operative_after_go(tmp_path: Path) -> None:
    _go_ready_chain(tmp_path, "ready-thread")
    packet = preflight.build_packet(
        bridge_id="ready-thread",
        bridge_dir=tmp_path / "bridge",
        config_path=_config(tmp_path),
        db_path=tmp_path / "absent.db",
    )
    assert packet["operative_version"] == {"status": "READY", "path": "bridge/ready-thread-003.md", "version_number": 3}
    assert packet["project_authorization_operation_time"]["phase"] == "finalization"
    assert packet["preflight_passed"] is True


def test_explicit_ready_source_is_rebuilt_for_verdict_freshness(tmp_path: Path) -> None:
    """The gate freshness check calls build_packet(content_file=<Responds to path>)."""
    _go_ready_chain(tmp_path, "ready-source")
    packet = preflight.build_packet(
        bridge_id="ready-source",
        bridge_dir=tmp_path / "bridge",
        config_path=_config(tmp_path),
        db_path=tmp_path / "absent.db",
        content_file=tmp_path / "bridge" / "ready-source-003.md",
    )
    assert packet["source_identity"]["status"] == "READY"
    assert packet["content_source"] == {"mode": "pending_content", "path": "bridge/ready-source-003.md"}


def test_not_ready_then_ready_resolves_to_latest_ready(tmp_path: Path) -> None:
    _go_ready_chain(tmp_path, "resubmit")
    _write(tmp_path, "resubmit", 4, "NOT-READY", "bridge_kind: lo_verdict\nResponds to: bridge/resubmit-003.md\n")
    _write(
        tmp_path,
        "resubmit",
        5,
        "READY",
        "bridge_kind: implementation_report_revision\nResponds to: bridge/resubmit-004.md\n"
        f"Approved proposal: bridge/resubmit-001.md\n{TARGET}{SPEC_LINKS}",
    )
    versions = preflight.parse_versioned_files_for_document(tmp_path / "bridge", "resubmit")
    assert [v.version_number for v in versions] == [5, 4, 3, 2, 1]
    assert preflight.choose_operative_version(versions).version_number == 5


def test_verdict_rejected_is_operative_after_no_go(tmp_path: Path) -> None:
    _write(tmp_path, "rejected", 1, "NEW", f"bridge_kind: prime_proposal\n{SPEC_LINKS}")
    _write(tmp_path, "rejected", 2, "NO-GO", "bridge_kind: lo_verdict\nResponds to: bridge/rejected-001.md\n")
    _write(tmp_path, "rejected", 3, "VERDICT-REJECTED", "Responds to: bridge/rejected-002.md\n")
    versions = preflight.parse_versioned_files_for_document(tmp_path / "bridge", "rejected")
    operative = preflight.choose_operative_version(versions)
    assert (operative.status, operative.version_number) == ("VERDICT-REJECTED", 3)


def test_no_go_then_revised_resolves_to_revised(tmp_path: Path) -> None:
    _write(tmp_path, "revised", 1, "NEW", SPEC_LINKS)
    _write(tmp_path, "revised", 2, "NO-GO", "Responds to: bridge/revised-001.md\n")
    _write(tmp_path, "revised", 3, "REVISED", SPEC_LINKS)
    versions = preflight.parse_versioned_files_for_document(tmp_path / "bridge", "revised")
    assert preflight.choose_operative_version(versions).version_number == 3


def test_superseded_latest_is_terminal_operative(tmp_path: Path) -> None:
    _write(tmp_path, "closed", 1, "NEW", SPEC_LINKS)
    _write(tmp_path, "closed", 2, "SUPERSEDED", "Responds to: bridge/closed-001.md\n")
    versions = preflight.parse_versioned_files_for_document(tmp_path / "bridge", "closed")
    assert preflight.choose_operative_version(versions).status == "SUPERSEDED"


def test_historical_inert_tokens_are_never_operative() -> None:
    assert {"NEW", "REVISED", "READY", "VERDICT-REJECTED"} == LOYAL_OPPOSITION_ACTIONABLE_STATUSES
    for status in ("NO-ACTION", "DEFERRED", "ACCEPTED"):
        versions = [
            preflight.BridgeVersion(
                status="NEW", rel_path="bridge/x-001.md", abs_path=Path("bridge/x-001.md"), version_number=1
            ),
            preflight.BridgeVersion(
                status=status, rel_path="bridge/x-002.md", abs_path=Path("bridge/x-002.md"), version_number=2
            ),
        ]
        assert preflight.choose_operative_version(versions).version_number == 1, status


@pytest.mark.parametrize("head", ["VERIFIED", "NOT-READY"])
def test_prepare_verdict_candidate_accepts_verdicts_responding_to_ready(tmp_path: Path, head: str) -> None:
    _go_ready_chain(tmp_path, "prep")
    config = _config(tmp_path)
    candidate = (
        f"{head}\n\nDocument: prep\nVersion: 004\nResponds to: bridge/prep-003.md\n\n"
        "## Applicability Preflight\n\n- packet_hash: `pending`\n- candidate_evidence_hash: `<CANDIDATE_EVIDENCE_HASH>`\n"
    )
    assert preflight.verdict_candidate_needs_preparation(candidate) is True
    prepared = preflight.prepare_verdict_candidate(
        candidate_path="bridge/prep-004.md",
        content=candidate,
        project_root=tmp_path,
        config_path=config,
        db_path=tmp_path / "absent.db",
    )
    assert "- content_file: `bridge/prep-003.md`" in prepared
    assert "candidate_evidence_hash: `sha256:" in prepared
