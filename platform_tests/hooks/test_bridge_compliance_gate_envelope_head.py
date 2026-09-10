"""Canonical hook sources validate authored headers through the native service parser."""

from __future__ import annotations

import builtins
import importlib.util
from itertools import permutations
from pathlib import Path

import pytest

from platform_tests.groundtruth_kb.test_native_bridge import authored

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(
    params=[
        ".harness-baseline-configuration/hooks/bridge-compliance-gate.py",
        "groundtruth-kb/templates/hooks/bridge-compliance-gate.py",
    ]
)
def gate(request):
    path = ROOT / request.param
    spec = importlib.util.spec_from_file_location("qualified_bridge_envelope", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def message(status="NEW"):
    return authored({"session_context_id": "fixture-context"}, "assigned-document", 1, status)


@pytest.mark.parametrize("head", list(permutations(["::init gtkb lo", "::open build", "NEW"])))
def test_complete_dispatchable_header_accepts_every_legal_order(gate, head):
    content = "\r\n".join([*head, *message().splitlines()[3:]])
    assert gate._bridge_envelope_head_deny_reason(content) is None


@pytest.mark.parametrize("status", ["ADVISORY", "VERIFIED", "WITHDRAWN", "SUPERSEDED", "BLOCKED"])
def test_non_dispatchable_header_needs_no_agent_envelope(gate, status):
    assert gate._bridge_envelope_head_deny_reason(message(status)) is None
    assert gate._bridge_envelope_head_deny_reason("::init gtkb lo\n::open build\n" + message(status))


@pytest.mark.parametrize(
    "old,new",
    [
        ("::init gtkb lo\r\n", ""),
        ("::init gtkb lo", "::init gtkb pb"),
        ("::open build", "::open unknown"),
        ("NEW", "NO-ACTION"),
        ("NEW", "DEFERRED"),
        ("Document: assigned-document", "Document: assigned-document\r\nDOCUMENT: duplicate"),
    ],
)
def test_invalid_authored_header_is_refused_without_repair(gate, old, new):
    reason = gate._bridge_envelope_head_deny_reason(message().replace(old, new, 1))
    assert reason and "Invalid authored bridge header" in reason
    assert "native bridge CLI" in reason


def test_unavailable_native_validator_never_becomes_a_pass(gate, monkeypatch):
    actual_import = builtins.__import__

    def unavailable(name, *args, **kwargs):
        if name == "groundtruth_kb.bridge.native":
            raise ModuleNotFoundError("Native validator unavailable")
        return actual_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", unavailable)
    reason = gate._bridge_envelope_head_deny_reason(message())
    assert "native_bridge_validator_unavailable" in reason
    assert "Repair the interpreter/package configuration" in reason


@pytest.mark.parametrize(
    "field",
    [
        "Document",
        "Version",
        "Date",
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "Project",
        "Work Item",
        "work_item_version",
        "target_paths",
        "test_artifact_targets",
        "spec_versions",
    ],
)
def test_required_proposal_metadata_is_checked_without_header_synthesis(gate, field):
    content = "\r\n".join(line for line in message().splitlines() if not line.startswith(field + ":"))
    assert gate._bridge_envelope_head_deny_reason(content)


@pytest.mark.parametrize(
    "field,value",
    [
        ("Project Authorization", "PAUTH-old"),
        ("target_role", "loyal-opposition"),
        ("target_paths", '["bridge/INDEX.md"]'),
        ("target_paths", '["../outside.py"]'),
    ],
)
def test_retired_permission_fields_and_non_concrete_scope_are_refused(gate, field, value):
    content = message()
    lines = [line for line in content.splitlines() if not line.startswith(field + ":")]
    lines.insert(4, f"{field}: {value}")
    assert gate._bridge_envelope_head_deny_reason("\r\n".join(lines))
