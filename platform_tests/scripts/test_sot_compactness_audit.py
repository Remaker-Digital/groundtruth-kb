from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / "scripts" / "sot_compactness_audit.py"


def _load():
    spec = importlib.util.spec_from_file_location("sot_compactness_audit", HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_h = _load()


def test_registry_is_valid_and_covers_required_sot_classes() -> None:
    registry = _h.default_registry()
    assert _h.validate_registry(registry) == ()

    assert {record.sot_class for record in registry} == {
        "Native operating status",
        "Native work items",
        "Native projects",
        "Native bridge coordination",
    }


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("gt status --startup", _h.COMMAND_KIND_COMPACT),
        ("gt backlog list --limit 20 --json", _h.COMMAND_KIND_BOUNDED),
        ("gt projects list --limit 20 --json", _h.COMMAND_KIND_BOUNDED),
        ("gt deliberations list --search compact --limit 5 --json", _h.COMMAND_KIND_BOUNDED),
        ("gt projects show PROJECT-X --history --json", _h.COMMAND_KIND_ARCHIVAL),
        ("gt projects show PROJECT-X --json", _h.COMMAND_KIND_UNCLASSIFIED),
        ("gt bridge state-report --json", _h.COMMAND_KIND_UNCLASSIFIED),
    ],
)
def test_command_classification(command: str, expected: str) -> None:
    assert _h.classify_command(command) == expected


def test_gaps_require_a_concrete_disposition_and_are_not_covered() -> None:
    gap = replace(
        _h.default_registry()[0], read_mode=_h.READ_MODE_GAP, follow_on_disposition="Measure and bound the response."
    )
    assert _h.validate_registry((gap,)) == ()
    assert _h.audit_registry((gap,))[0].status == _h.STATUS_GAP
    invalid = replace(gap, follow_on_disposition="")
    assert _h.validate_registry((invalid,))
    assert _h.audit_registry((invalid,))[0].status == _h.STATUS_INVALID


@pytest.mark.parametrize(
    "changes",
    [{"read_mode": "unknown"}, {"routine_command": "gt projects show PROJECT-X --json"}, {"governing_specs": ()}],
)
def test_invalid_read_contracts_are_rejected(changes) -> None:
    row = replace(_h.default_registry()[0], **changes)
    assert _h.validate_registry((row,))
    assert _h.audit_registry((row,))[0].status == _h.STATUS_INVALID


def test_duplicate_surface_ids_are_rejected() -> None:
    row = _h.default_registry()[0]
    assert _h.validate_registry((row, row))
    assert all(item.status == _h.STATUS_INVALID for item in _h.audit_registry((row, row)))


def test_markdown_report_renders_current_routes_without_claiming_measured_payloads() -> None:
    markdown = _h.render_markdown_report(_h.audit_registry(), generated_at="2026-09-20T00:00:00Z")
    assert "# Native Read-Surface Compactness Report" in markdown
    assert "| `covered` | 4 |" in markdown
    assert "gt projects list --limit 20 --json" in markdown
    assert "gt bridge state-report --json" in markdown
    assert "does not execute the routes or measure their payloads" in markdown
    assert "Project Authorization:" not in markdown


def test_rows_as_json_is_compact_and_omits_raw_payloads() -> None:
    payload = _h.rows_as_json(_h.audit_registry())
    encoded = json.dumps(payload, sort_keys=True)
    assert payload["summary"] == {_h.STATUS_COVERED: 4}
    assert set(payload) == {"summary", "rows"}
    assert "raw_payload" not in encoded
    assert "full_payload" not in encoded


def test_advisory_surface_reads_native_state_without_a_candidate_writer() -> None:
    advisory = next(record for record in _h.default_registry() if record.surface_id == "advisory-state-report")

    assert advisory.sot_class == "Native bridge coordination"
    assert advisory.routine_command == "gt bridge state-report --json"
    assert "dropbox" not in advisory.routine_command.lower()
    assert not hasattr(_h, "write_report")
    assert not hasattr(_h, "default_report_path")


def test_retired_report_writing_flag_is_rejected() -> None:
    with pytest.raises(SystemExit):
        _h.main(["--write-report"])
