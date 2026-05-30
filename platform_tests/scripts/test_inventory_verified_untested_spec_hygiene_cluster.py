"""Tests for ``scripts/inventory_verified_untested_spec_hygiene_cluster.py``.

Bridge: ``gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory`` (GO
at ``-006``). Source WIs: WI-3178..WI-3182. PAUTH:
``PAUTH-AGENT-RED-SPEC-HYGIENE-VERIFIED-UNTESTED-CLUSTER-001`` (DELIB-2511).

These tests use an in-memory ``FakeReader`` fixture and a temporary output
directory; they never touch live ``groundtruth.db``. The ``FakeReader`` records
every method call so the "no mutation in inventory mode" obligation is checked
by asserting only read methods were invoked.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "inventory_verified_untested_spec_hygiene_cluster.py"
_SPEC = importlib.util.spec_from_file_location("inv_cluster", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
inv = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(inv)


# Read methods the inventory is allowed to call. Anything else is a mutation
# surface and must never be invoked in inventory mode.
_READ_METHODS = {
    "get_spec",
    "get_tests_for_spec",
    "get_test_coverage_for_spec",
    "get_open_work_items",
}


class FakeReader:
    """In-memory ``SpecReader`` that records every call it receives."""

    def __init__(
        self,
        specs: dict[str, dict[str, Any]],
        tests: dict[str, list[dict[str, Any]]] | None = None,
        coverage: dict[str, list[dict[str, Any]]] | None = None,
        work_items: list[dict[str, Any]] | None = None,
    ) -> None:
        self._specs = specs
        self._tests = tests or {}
        self._coverage = coverage or {}
        self._work_items = work_items or []
        self.calls: list[str] = []

    def get_spec(self, spec_id: str) -> dict[str, Any] | None:
        self.calls.append("get_spec")
        return self._specs.get(spec_id)

    def get_tests_for_spec(self, spec_id: str) -> list[dict[str, Any]]:
        self.calls.append("get_tests_for_spec")
        return list(self._tests.get(spec_id, []))

    def get_test_coverage_for_spec(self, spec_id: str) -> list[dict[str, Any]]:
        self.calls.append("get_test_coverage_for_spec")
        return list(self._coverage.get(spec_id, []))

    def get_open_work_items(self) -> list[dict[str, Any]]:
        self.calls.append("get_open_work_items")
        return list(self._work_items)


def _spec(spec_id: str, title: str = "Neutral requirement", description: str = "") -> dict[str, Any]:
    return {
        "id": spec_id,
        "status": "implemented",
        "type": "requirement",
        "title": title,
        "description": description,
        "testability": "testable",
        "priority": "P3",
        "source_paths": None,
        "implementation_verified_at": None,
    }


def _test_row(test_id: str, spec_id: str, test_file: str, test_function: str) -> dict[str, Any]:
    return {
        "id": test_id,
        "spec_id": spec_id,
        "test_file": test_file,
        "test_function": test_function,
        "test_class": None,
        "test_type": "unit",
        "last_result": "pass",
        "last_executed_at": "2026-05-01T00:00:00Z",
    }


# --------------------------------------------------------------------------- #
# Classification: all five buckets
# --------------------------------------------------------------------------- #


def test_classify_performance_oracle_from_timing_terms() -> None:
    spec = _spec("SPEC-PERF", title="Pipeline budget P50 7000ms and timeout 8000ms")
    bucket, reason = inv.classify_spec(spec, [], [])
    assert bucket == inv.BUCKET_PERFORMANCE
    assert "performance" in reason.lower()


def test_classify_live_server_from_endpoint_terms() -> None:
    spec = _spec("SPEC-EP", title="POST /alerts/{id}/acknowledge endpoint in superadmin_api")
    bucket, reason = inv.classify_spec(spec, [], [])
    assert bucket == inv.BUCKET_LIVE_SERVER
    assert "server" in reason.lower()


def test_classify_fixable_when_linked_test_resolves(tmp_path: Path) -> None:
    test_file = tmp_path / "fake_test_module.py"
    test_file.write_text("def test_widget_views():\n    assert True\n", encoding="utf-8")
    spec = _spec("SPEC-NEUTRAL", title="Define widget views closed prechat otp")
    tests = [_test_row("TEST-1", "SPEC-NEUTRAL", "fake_test_module.py", "test_widget_views")]
    probes = [inv.probe_test_on_disk(tmp_path, t) for t in tests]
    bucket, reason = inv.classify_spec(spec, tests, probes)
    assert bucket == inv.BUCKET_FIXABLE
    assert "resolve on disk" in reason


def test_classify_behavioral_mismatch_when_test_absent(tmp_path: Path) -> None:
    spec = _spec("SPEC-NEUTRAL", title="Pricing overage thresholds per tier")
    tests = [_test_row("TEST-2", "SPEC-NEUTRAL", "does_not_exist.py", "test_missing")]
    probes = [inv.probe_test_on_disk(tmp_path, t) for t in tests]
    bucket, reason = inv.classify_spec(spec, tests, probes)
    assert bucket == inv.BUCKET_BEHAVIORAL
    assert "does not match reality" in reason


def test_classify_unresolvable_when_no_test_and_no_signal() -> None:
    spec = _spec("SPEC-NEUTRAL", title="Pricing overage thresholds per tier")
    bucket, reason = inv.classify_spec(spec, [], [])
    assert bucket == inv.BUCKET_UNRESOLVABLE
    assert "cannot be determined" in reason


def test_performance_takes_precedence_over_endpoint() -> None:
    # A spec that mentions BOTH an endpoint and a latency budget should be
    # classed as performance (the stronger, intrinsic requirement signal).
    spec = _spec("SPEC-BOTH", title="GET /metrics endpoint must answer within P50 200ms")
    bucket, _ = inv.classify_spec(spec, [], [])
    assert bucket == inv.BUCKET_PERFORMANCE


# --------------------------------------------------------------------------- #
# Disk probe: static only
# --------------------------------------------------------------------------- #


def test_probe_detects_function_via_ast(tmp_path: Path) -> None:
    f = tmp_path / "mod.py"
    f.write_text("class C:\n    def test_inner(self):\n        pass\n", encoding="utf-8")
    probe = inv.probe_test_on_disk(tmp_path, _test_row("T", "S", "mod.py", "test_inner"))
    assert probe["file_present"] is True
    assert probe["function_present"] is True


def test_probe_reports_absent_file(tmp_path: Path) -> None:
    probe = inv.probe_test_on_disk(tmp_path, _test_row("T", "S", "nope.py", "test_x"))
    assert probe["file_present"] is False
    assert probe["function_present"] is False


def test_probe_function_absent_when_symbol_missing(tmp_path: Path) -> None:
    f = tmp_path / "mod.py"
    f.write_text("def other():\n    pass\n", encoding="utf-8")
    probe = inv.probe_test_on_disk(tmp_path, _test_row("T", "S", "mod.py", "test_x"))
    assert probe["file_present"] is True
    assert probe["function_present"] is False


# --------------------------------------------------------------------------- #
# Inventory assembly + outputs
# --------------------------------------------------------------------------- #


def _five_spec_reader(tmp_path: Path) -> FakeReader:
    fixable_file = tmp_path / "resolving_test.py"
    fixable_file.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    specs = {
        "SPEC-1076": _spec("SPEC-1076", title="POST /alerts/acknowledge endpoint"),
        "SPEC-1078": _spec("SPEC-1078", title="GET /mfa/status endpoint"),
        "SPEC-0811": _spec("SPEC-0811", title="pipeline budget P50 7000ms timeout 8000ms"),
        "SPEC-1138": _spec("SPEC-1138", title="Define widget views closed prechat"),
        "SPEC-0661": _spec("SPEC-0661", title="Pricing overage thresholds per tier"),
    }
    tests = {
        "SPEC-1138": [_test_row("TEST-W", "SPEC-1138", "resolving_test.py", "test_ok")],
        "SPEC-0661": [_test_row("TEST-P", "SPEC-0661", "ghost.py", "test_ghost")],
    }
    work_items = [
        {
            "id": "WI-3178",
            "source_spec_id": "SPEC-1076",
            "title": "hygiene",
            "resolution_status": "open",
            "priority": "P3",
            "origin": "hygiene",
            "component": "Backend",
        }
    ]
    return FakeReader(specs, tests=tests, work_items=work_items)


def test_build_inventory_emits_one_record_per_spec(tmp_path: Path) -> None:
    reader = _five_spec_reader(tmp_path)
    manifest = inv.build_inventory(reader, tmp_path, generated_at="FIXED")
    assert len(manifest["records"]) == len(inv.IN_SCOPE_SPECS)
    assert [r["spec_id"] for r in manifest["records"]] == list(inv.IN_SCOPE_SPECS)


def test_build_inventory_covers_multiple_buckets(tmp_path: Path) -> None:
    reader = _five_spec_reader(tmp_path)
    manifest = inv.build_inventory(reader, tmp_path, generated_at="FIXED")
    by_spec = {r["spec_id"]: r["classification"] for r in manifest["records"]}
    assert by_spec["SPEC-1076"] == inv.BUCKET_LIVE_SERVER
    assert by_spec["SPEC-1078"] == inv.BUCKET_LIVE_SERVER
    assert by_spec["SPEC-0811"] == inv.BUCKET_PERFORMANCE
    assert by_spec["SPEC-1138"] == inv.BUCKET_FIXABLE
    assert by_spec["SPEC-0661"] == inv.BUCKET_BEHAVIORAL


def test_classification_counts_match_records(tmp_path: Path) -> None:
    reader = _five_spec_reader(tmp_path)
    manifest = inv.build_inventory(reader, tmp_path, generated_at="FIXED")
    counts = manifest["classification_counts"]
    assert sum(counts.values()) == len(manifest["records"])
    assert set(counts) == set(inv.ALL_BUCKETS)
    assert counts[inv.BUCKET_LIVE_SERVER] == 2


def test_open_work_items_filtered_by_source_spec_id(tmp_path: Path) -> None:
    reader = _five_spec_reader(tmp_path)
    manifest = inv.build_inventory(reader, tmp_path, generated_at="FIXED")
    by_spec = {r["spec_id"]: r for r in manifest["records"]}
    assert [w["id"] for w in by_spec["SPEC-1076"]["open_work_items"]] == ["WI-3178"]
    assert by_spec["SPEC-1078"]["open_work_items"] == []


def test_missing_spec_is_unresolvable(tmp_path: Path) -> None:
    reader = FakeReader(specs={})
    manifest = inv.build_inventory(reader, tmp_path, specs=("SPEC-GONE",), generated_at="FIXED")
    record = manifest["records"][0]
    assert record["found"] is False
    assert record["classification"] == inv.BUCKET_UNRESOLVABLE


def test_build_inventory_idempotent_for_fixed_inputs(tmp_path: Path) -> None:
    reader_a = _five_spec_reader(tmp_path)
    reader_b = _five_spec_reader(tmp_path)
    man_a = inv.build_inventory(reader_a, tmp_path, generated_at="FIXED", database_sha256="X")
    man_b = inv.build_inventory(reader_b, tmp_path, generated_at="FIXED", database_sha256="X")
    assert json.dumps(man_a, sort_keys=True) == json.dumps(man_b, sort_keys=True)


def test_inventory_mode_calls_only_read_methods(tmp_path: Path) -> None:
    reader = _five_spec_reader(tmp_path)
    inv.build_inventory(reader, tmp_path, generated_at="FIXED")
    assert set(reader.calls) <= _READ_METHODS
    assert reader.calls, "expected at least one read call"


def test_write_outputs_confined_to_output_dir(tmp_path: Path) -> None:
    reader = _five_spec_reader(tmp_path)
    manifest = inv.build_inventory(reader, tmp_path, generated_at="FIXED")
    out = tmp_path / "out-subdir"
    paths = inv.write_outputs(manifest, out)
    written = sorted(p.name for p in out.iterdir())
    assert written == [inv.MANIFEST_FILENAME, inv.SUMMARY_FILENAME]
    assert paths["manifest"].parent == out
    assert paths["summary"].parent == out
    # Every written path stays under the requested output dir.
    for path in paths.values():
        assert out in path.parents


def test_manifest_json_roundtrips_and_summary_lists_specs(tmp_path: Path) -> None:
    reader = _five_spec_reader(tmp_path)
    manifest = inv.build_inventory(reader, tmp_path, generated_at="FIXED")
    out = tmp_path / "out"
    paths = inv.write_outputs(manifest, out)
    loaded = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    assert loaded == manifest
    summary = paths["summary"].read_text(encoding="utf-8")
    for spec_id in inv.IN_SCOPE_SPECS:
        assert spec_id in summary
    for bucket in inv.ALL_BUCKETS:
        assert bucket in summary


@pytest.mark.parametrize("bucket", inv.ALL_BUCKETS)
def test_every_bucket_has_a_recommended_action(bucket: str) -> None:
    assert bucket in inv.RECOMMENDED_SLICE2_ACTION
    assert inv.RECOMMENDED_SLICE2_ACTION[bucket].strip()
