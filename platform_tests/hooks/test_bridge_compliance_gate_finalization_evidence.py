"""Regression tests for VERIFIED Commit Finalization Evidence gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_finalization", ACTIVE_HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GATE = _load_gate()
_PACKET_HASH = "packet_hash: sha256:" + "0" * 64


def _verified_body(*, finalization_evidence: bool) -> str:
    body = f"""VERIFIED
author_identity: loyal-opposition/test
author_harness_id: T
author_session_context_id: verifier-session
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

# Verification

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001

## Applicability Preflight

{_PACKET_HASH}
missing_required_specs: []

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | pytest platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py | yes | PASS |

## Commands Executed

- python -m pytest platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py -q
"""
    if not finalization_evidence:
        return body
    return (
        body
        + """
## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Same-transaction path set:
- `scripts/foo.py`
- `bridge/test-finalization-003.md`
- `bridge/test-finalization-004.md`
"""
    )


def test_verified_without_commit_finalization_evidence_is_blocked(tmp_path: Path) -> None:
    reason = _GATE._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(tmp_path / "bridge" / "test-finalization-004.md"),
        content=_verified_body(finalization_evidence=False),
        run_pending_preflight=False,
    )

    assert reason is not None
    assert "Commit Finalization Evidence" in reason


def test_verified_with_commit_finalization_evidence_is_allowed(tmp_path: Path) -> None:
    reason = _GATE._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=str(tmp_path / "bridge" / "test-finalization-004.md"),
        content=_verified_body(finalization_evidence=True),
        run_pending_preflight=False,
    )

    assert reason is None


def test_commit_finalization_evidence_requires_same_transaction_path_set() -> None:
    assert _GATE._has_commit_finalization_evidence(_verified_body(finalization_evidence=False)) is False
    assert _GATE._has_commit_finalization_evidence(_verified_body(finalization_evidence=True)) is True
