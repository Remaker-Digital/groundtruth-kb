"""WI-5918 Goose governance-hook registration census.

Fails unless the projected Goose plugin hooks.json registers the named blocking
gates, declares itself a projection, has no competing .agents shim, and
`.goosehints` still documents `::init gtkb pb` / `::init gtkb lo`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = REPO_ROOT / "scripts" / "check_harness_parity.py"
GOOSE_HOOKS_JSON = REPO_ROOT / ".goose" / "plugins" / "gtkb" / "hooks" / "hooks.json"
GOOSEHINTS = REPO_ROOT / ".goosehints"
AGENTS_SHIM = REPO_ROOT / ".agents" / "plugins" / "gtkb" / "hooks" / "hooks.json"
OBSOLETE_ADAPTER = REPO_ROOT / "scripts" / "goose_hook_adapter.py"
REGISTRY_PATH = REPO_ROOT / "config" / "agent-control" / "gtkb-harness-capability-registry.toml"
PROJECTION_MARKER = "PROJECTION, NOT CANONICAL"
NAMED_BLOCKING_GATES = (
    "destructive-gate.py",
    "credential-scan.py",
    "formal-artifact-approval-gate.py",
    "bridge-compliance-gate.py",
    "implementation-start-gate.py",
    "lo-file-safety-gate.py",
    "sot-read-discipline.py",
    "narrative-artifact-approval-gate.py",
    "document_author_provenance_gate.py",
)
EMPIRICAL_FIRING_CAPABILITY_ID = "hook.goose-blocking-gate-empirical-firing"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_harness_parity", CHECKER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_harness_parity"] = module
    spec.loader.exec_module(module)
    return module


def test_goose_plugin_hooks_json_is_a_projection() -> None:
    assert GOOSE_HOOKS_JSON.is_file()
    payload = json.loads(GOOSE_HOOKS_JSON.read_text(encoding="utf-8"))
    comment = str(payload.get("_comment") or "")
    assert PROJECTION_MARKER in comment


def test_goose_plugin_hooks_json_registers_named_blocking_gates() -> None:
    module = _load_checker()
    registration = module.load_goose_plugin_hook_registration(REPO_ROOT)
    missing = [name for name in NAMED_BLOCKING_GATES if name not in registration["scripts"]]
    assert missing == []


def test_competing_agents_plugin_shim_is_absent() -> None:
    assert not AGENTS_SHIM.exists()
    assert not OBSOLETE_ADAPTER.exists()


def test_goosehints_documents_init_keywords() -> None:
    text = GOOSEHINTS.read_text(encoding="utf-8")
    assert "::init gtkb pb" in text
    assert "::init gtkb lo" in text


def test_parity_checker_evidences_goose_hooks_from_plugin_registration() -> None:
    module = _load_checker()
    report = module.check_harness_parity(REPO_ROOT, harness="goose", include_all=True)
    gate_rows = [
        result
        for result in report.results
        if result.harness == "goose" and result.capability_id.startswith("goose.required-gate.")
    ]
    assert len(gate_rows) == len(NAMED_BLOCKING_GATES)
    assert {result.state for result in gate_rows} == {"PASS"}
    assert all("plugin hooks.json" in result.note for result in gate_rows)


def test_empirical_firing_is_typed_waived_not_silently_omitted() -> None:
    module = _load_checker()
    registry, _ = module.load_registry(REPO_ROOT)
    waivers = [
        item
        for item in module.load_parity_waivers(registry)
        if item.get("capability_id") == EMPIRICAL_FIRING_CAPABILITY_ID and item.get("harness") == "goose"
    ]
    assert len(waivers) == 1
    waiver = waivers[0]
    assert waiver.get("reason_class") in module.WAIVER_REASON_CLASSES
    rationale = str(waiver.get("rationale") or "")
    for gate in NAMED_BLOCKING_GATES:
        assert gate in rationale
    assert "fallback" in rationale.lower() or "Mechanical fallback" in rationale
    report = module.check_harness_parity(REPO_ROOT, harness="goose", include_all=True)
    firing = [
        result
        for result in report.results
        if result.harness == "goose" and result.capability_id == EMPIRICAL_FIRING_CAPABILITY_ID
    ]
    assert len(firing) == 1
    assert firing[0].state == "UNSUPPORTED"
    assert firing[0].configured_status.startswith("waived:")
    schema_errors = module.validate_parity_schema(registry)
    assert schema_errors == []
