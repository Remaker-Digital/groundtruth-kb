"""Tests for structured modernization non-impairment proposal enforcement."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=[ACTIVE_HOOK, TEMPLATE_HOOK], ids=["active", "template"])
def gate(request):
    return _load(request.param, f"nonimpairment_gate_{request.param.parent.name}")


def _disposition(**overrides) -> str:
    payload = {
        "schema_version": 1,
        "applicability": "applicable",
        "provenance": "DCL-EXAMPLE-001",
        "canonical_authority": "DCL-EXAMPLE-001",
        "primary_route": "gt example update",
        "before_behavior": "manual and ambiguous",
        "after_behavior": "deterministic and observable",
        "self_descriptive_naming": "names identify authority and lifecycle",
        "obsolete_guidance_disposition": "quarantined from active loading",
        "history_preservation": "append-only history remains queryable",
        "baseline": {"latency_seconds": 5},
        "expected_result": {"latency_seconds": 4},
        "rollback": {"instructions": "restore prior config", "test": "TEST-ROLLBACK"},
        "hard_invariants": ["INV-1"],
        "fail_closed_conditions": ["missing authority", "stale evidence"],
        "essential_context_preservation": "all required authority remains present",
    }
    payload.update(overrides)
    return "## Intuitiveness/Non-Impairment Disposition\n\n```json\n" + json.dumps(payload) + "\n```\n"


def _proposal(disposition: str | None) -> str:
    sections = [
        "NEW",
        "",
        "# Non-impairment proposal",
        "",
        "author_identity: prime-builder/codex/A",
        "author_harness_id: A",
        "author_session_context_id: test-session",
        "author_model: Codex",
        "author_model_version: test",
        "author_model_configuration: test",
        "bridge_kind: prime_proposal",
        "Project Authorization: PAUTH-TEST-PROJECT-X",
        "Project: PROJECT-TEST-X",
        "Work Item: WI-9999",
        'target_paths: [".claude/hooks/bridge-compliance-gate.py"]',
        "",
        "## Specification Links",
        "",
        "- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
        "- GOV-FILE-BRIDGE-AUTHORITY-001",
        "",
        "## Requirement Sufficiency",
        "",
        "Existing requirements sufficient. The structured contract is complete.",
        "",
        "## Cross-Harness Disposition",
        "",
        "The canonical hook behavior is identical across governed harness paths.",
    ]
    if disposition is not None:
        sections.extend(["", disposition])
    return "\n".join(sections)


def _deny(gate, content: str, cwd: Path) -> str | None:
    return gate._deny_reason_for_content(
        cwd_path=cwd,
        file_path="bridge/test-nonimpairment-001.md",
        content=content,
        run_pending_preflight=False,
    )


def test_concrete_structured_disposition_passes(gate):
    assert gate._nonimpairment_disposition_gap(_disposition()) is None


def test_absent_or_unfenced_disposition_fails(gate):
    assert gate._nonimpairment_disposition_gap("## Claim\n\nwork\n") == "section absent"
    assert "exactly one fenced JSON" in gate._nonimpairment_disposition_gap(
        "## Intuitiveness/Non-Impairment Disposition\n\n{}\n"
    )


def test_missing_or_placeholder_fields_fail(gate):
    missing = gate._nonimpairment_disposition_gap(_disposition(primary_route=None))
    placeholder = gate._nonimpairment_disposition_gap(_disposition(rollback="TBD"))

    assert missing == "placeholder or empty fields: primary_route"
    assert placeholder == "placeholder or empty fields: rollback"


def test_multiple_json_blocks_fail(gate):
    content = _disposition() + "\n```json\n{}\n```\n"
    assert "exactly one fenced JSON" in gate._nonimpairment_disposition_gap(content)


def test_proposal_without_structured_disposition_is_denied(gate, tmp_path: Path):
    reason = _deny(gate, _proposal(None), tmp_path)

    assert reason is not None
    assert "Cross-cutting implementation proposals" in reason
    assert "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001" in reason
    assert "section absent" in reason


def test_proposal_with_structured_disposition_passes(gate, tmp_path: Path):
    assert _deny(gate, _proposal(_disposition()), tmp_path) is None
