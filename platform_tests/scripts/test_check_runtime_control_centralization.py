"""GHRP-DCL-CONTROL-A1: the declared operational-control set is proven complete; the unresolved inventory is reported.

DCL-CENTRAL-DYNAMIC-OPERATIONAL-CONTROLS-001 names scripts/check_runtime_control_centralization.py. These cases
evaluate the DCL's own assertion locally, prove the checked-in catalog against the two wired consumers, and show each
refusal on isolated fixture roots without contacting any authority.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import socket
import sys
from pathlib import Path

import pytest
import tomlkit
from groundtruth_kb.assertions import run_single_assertion
from groundtruth_kb.project import operational_control_config as controls

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = REPO_ROOT / "scripts/check_runtime_control_centralization.py"
CONSUMER_MODULES = (
    "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py",
    "scripts/timer_inventory.py",
)
DCL_ASSERTION = {
    "id": "GHRP-DCL-CONTROL-A1",
    "type": "all_of",
    "description": "The evaluator proves complete inventory, one typed value authority, no literal fallback, "
    "invariant validation, and dynamic replacement.",
    "assertions": [
        {"type": "file_exists", "file": "scripts/check_runtime_control_centralization.py"},
        {"type": "grep", "file": "scripts/check_runtime_control_centralization.py", "pattern": "GHRP-DCL-CONTROL-A1"},
    ],
}


def load():
    spec = importlib.util.spec_from_file_location("runtime_control_evaluator", EVALUATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


EVALUATOR_MODULE = load()


@pytest.fixture
def subject(tmp_path: Path) -> Path:
    """An isolated root carrying the checked-in catalog and the two wired consumer modules."""
    for relative in (controls.CATALOG_RELATIVE_PATH.as_posix(), *CONSUMER_MODULES):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    return tmp_path


def _catalog(root: Path):
    path = root / controls.CATALOG_RELATIVE_PATH
    return path, tomlkit.parse(path.read_text(encoding="utf-8"))


def _write(root: Path, document) -> None:
    (root / controls.CATALOG_RELATIVE_PATH).write_bytes(tomlkit.dumps(document).encode("utf-8"))


def _run(capsys, *args: str) -> tuple[int, str, str]:
    code = EVALUATOR_MODULE.main(list(args))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_dcl_assertion_evaluates_pass_against_this_checkout() -> None:
    text = EVALUATOR.read_text(encoding="utf-8")
    assert "GHRP-DCL-CONTROL-A1" in text
    result = run_single_assertion(DCL_ASSERTION, REPO_ROOT)
    assert result["passed"], result
    assert [child["passed"] for child in result["children"]] == [True, True]


@pytest.mark.timeout(240)
def test_checked_in_catalog_declared_set_is_complete_and_unresolved_inventory_is_reported(capsys) -> None:
    code, out, err = _run(capsys, "--project-root", str(REPO_ROOT), "--json")
    assert code == 0, (out, err)
    report = json.loads(out)
    assert report["assertion"] == "GHRP-DCL-CONTROL-A1"
    assert report["declared_set_complete"] is True and report["findings"] == []
    assert report["active_control_count"] == len(report["controls"]) >= 8
    assert set(report["consumer_contracts"]) == {
        "groundtruth_kb.project.registry_control_plane",
        "scripts.timer_inventory",
    }
    assert all(
        not contract["undeclared_keys"] and contract["module_present"]
        for contract in report["consumer_contracts"].values()
    )
    for key, control in report["controls"].items():
        assert control["wired_consumers"], key
        assert all(control["module_present"].values()) and all(control["module_references_key"].values()), key
        assert control["calibration_evidence"] and control["calibration_evidence"].startswith("calibration:20"), key
        assert not control["consumers_without_contract"], key
    assert report["invariants"] and all(invariant["holds"] for invariant in report["invariants"])
    assert report["dynamic_replacement"]["diff_route"] == "accepted"
    assert report["dynamic_replacement"]["same_sha256"] and report["dynamic_replacement"]["changed_controls"] == []
    assert report["dynamic_replacement"]["reload_behavior"] == ["next_operation"]
    inventory = report["inventory"]
    assert inventory["built"] is True
    assert inventory["semantic_completeness"] == "unproven"
    assert (
        isinstance(inventory["unclassified_or_ambiguous_count"], int)
        and inventory["unclassified_or_ambiguous_count"] >= 0
    )
    assert inventory["canonical_control_count"] == report["active_control_count"] + report["inactive_control_count"]
    assert "not adjudicated" in inventory["statement"]
    assert not list((REPO_ROOT / controls.CATALOG_RELATIVE_PATH).parent.glob("operational-controls.toml.lock"))


def test_text_report_names_the_declared_set_and_the_unresolved_count(capsys, subject: Path) -> None:
    # The copied consumer modules carry their own non-control literals; one unrecognised production numeric is added.
    baseline = EVALUATOR_MODULE.evaluate(subject)["inventory"]["unclassified_or_ambiguous_count"]
    (subject / "scripts/prod.py").write_text("FOO_BAR = 7\nTIMEOUT_SECONDS = 10\n", encoding="utf-8")
    code, out, err = _run(capsys, "--project-root", str(subject))
    assert code == 0, (out, err)
    first, second = out.splitlines()[:2]
    assert first.startswith("PASS runtime-control centralization (GHRP-DCL-CONTROL-A1):")
    assert "invariants hold" in first and "controls with dated calibration evidence" in first
    assert second.startswith(f"unresolved inventory: {baseline + 1} unclassified or ambiguous production uses")
    assert "migration completeness not established" in second
    code, out, _ = _run(capsys, "--project-root", str(subject), "--fail-on-unresolved")
    assert code == 1 and out.startswith("PASS")
    code, out, _ = _run(capsys, "--project-root", str(subject), "--skip-inventory")
    assert code == 0 and "unresolved inventory: not built (skipped)" in out


def test_control_without_a_wired_consumer_fails(capsys, subject: Path) -> None:
    path, document = _catalog(subject)
    orphan = dict(next(row for row in document["controls"] if row["id"] == controls.INVENTORY_GIT_PROBE_CONTROL))
    orphan.update(id="fixture.sample_timeout", consumers=["fixture.consumer"], evidence_refs=["fixture:observation"])
    document["controls"].append(orphan)
    _write(subject, document)
    code, out, _ = _run(capsys, "--project-root", str(subject), "--skip-inventory", "--json")
    assert code == 1
    report = json.loads(out)
    codes = {(finding["code"], finding["detail"].split(" ", 1)[0]) for finding in report["findings"]}
    assert codes == {
        ("orphan_control", "fixture.sample_timeout"),
        ("consumer_without_contract", "fixture.sample_timeout"),
        ("calibration_evidence_missing", "fixture.sample_timeout"),
    }
    assert report["controls"]["fixture.sample_timeout"]["wired_consumers"] == []
    assert report["declared_set_complete"] is False


def test_consumer_key_not_declared_fails(capsys, subject: Path) -> None:
    path, document = _catalog(subject)
    document["controls"] = [row for row in document["controls"] if not row["id"].startswith("registry.")]
    document["invariants"] = []
    _write(subject, document)
    assert set(controls.load_operational_control_catalog(subject).definitions) == {controls.INVENTORY_GIT_PROBE_CONTROL}
    code, out, _ = _run(capsys, "--project-root", str(subject), "--skip-inventory", "--json")
    assert code == 1
    report = json.loads(out)
    undeclared = {
        finding["detail"].split(" reads ")[1].split(",")[0]
        for finding in report["findings"]
        if finding["code"] == "undeclared_consumer_key"
    }
    assert undeclared == set(controls.REGISTRY_CONTROL_UNITS)
    assert report["consumer_contracts"]["groundtruth_kb.project.registry_control_plane"]["undeclared_keys"] == sorted(
        controls.REGISTRY_CONTROL_UNITS
    )
    assert report["consumer_contracts"]["scripts.timer_inventory"]["undeclared_keys"] == []


def test_missing_calibration_evidence_fails_for_that_control_only(capsys, subject: Path) -> None:
    path, document = _catalog(subject)
    row = next(row for row in document["controls"] if row["id"] == "registry.lock.acquire_seconds")
    row["evidence_refs"] = [ref for ref in row["evidence_refs"] if not str(ref).startswith("calibration:")] + [
        "calibration:2026-13-40"
    ]
    _write(subject, document)
    code, out, _ = _run(capsys, "--project-root", str(subject), "--skip-inventory", "--json")
    assert code == 1
    report = json.loads(out)
    assert [(finding["code"], finding["detail"].split(" ", 1)[0]) for finding in report["findings"]] == [
        ("calibration_evidence_missing", "registry.lock.acquire_seconds")
    ]
    assert report["controls"]["registry.lock.acquire_seconds"]["calibration_evidence"] is None


def test_absent_or_unreferencing_consumer_module_fails(capsys, subject: Path) -> None:
    (subject / "scripts/timer_inventory.py").unlink()
    registry_module = subject / "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py"
    registry_module.write_text("def unrelated() -> None:\n    return None\n", encoding="utf-8")
    code, out, _ = _run(capsys, "--project-root", str(subject), "--skip-inventory", "--json")
    assert code == 1
    report = json.loads(out)
    by_code: dict[str, set[str]] = {}
    for finding in report["findings"]:
        by_code.setdefault(finding["code"], set()).add(finding["detail"].split(":", 1)[0])
    assert by_code == {
        "consumer_module_absent": {controls.INVENTORY_GIT_PROBE_CONTROL},
        "consumer_module_unreferenced": set(controls.REGISTRY_CONTROL_UNITS),
    }


@pytest.mark.parametrize("defect", ["malformed", "invariant"])
def test_invalid_catalog_is_refused_without_fallback(capsys, subject: Path, defect: str) -> None:
    path, document = _catalog(subject)
    if defect == "malformed":
        path.write_text("bad = [", encoding="utf-8")
    else:
        row = next(row for row in document["controls"] if row["id"] == "registry.lock.max_backoff_seconds")
        row["value"] = "301"
        _write(subject, document)
    before = path.read_bytes()
    code, out, err = _run(capsys, "--project-root", str(subject), "--skip-inventory")
    assert code == 2 and out == ""
    assert "catalog refused" in err
    assert ("malformed_catalog" if defect == "malformed" else "invariant_violation") in err
    assert path.read_bytes() == before


def test_evaluation_is_local_and_leaves_no_writer_mutex(monkeypatch: pytest.MonkeyPatch, subject: Path) -> None:
    def deny(*args, **kwargs):
        raise AssertionError("The evaluator attempted a network connection")

    monkeypatch.setattr(socket.socket, "connect", deny)
    result = EVALUATOR_MODULE.evaluate(subject, inventory=True)
    assert result["declared_set_complete"] is True
    assert result["inventory"]["built"] is True and result["inventory"]["generating_commit"] is None
    assert not list((subject / controls.CATALOG_RELATIVE_PATH).parent.glob("*.lock"))
    assert sorted(p.relative_to(subject).as_posix() for p in subject.rglob("*") if p.is_file()) == sorted(
        [controls.CATALOG_RELATIVE_PATH.as_posix(), *CONSUMER_MODULES, "groundtruth.toml"]
    )
