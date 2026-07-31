"""Behavioral coverage for the read-only PAUTH finalization exposure sweep."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "pauth_finalization_exposure_sweep.py"

spec = importlib.util.spec_from_file_location("pauth_finalization_exposure_sweep", SCRIPT_PATH)
assert spec is not None
sweep = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["pauth_finalization_exposure_sweep"] = sweep
spec.loader.exec_module(sweep)

FIXED_TIME = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)


def _envelope(authorization_id: str) -> dict[str, object]:
    allowed = ["source", "test_addition"]
    if authorization_id != "PAUTH-NO-BRIDGE":
        allowed.append("bridge")
    return {
        "id": authorization_id,
        "version": 3,
        "project_id": "PROJECT-FIXTURE",
        "status": "active",
        "allowed_mutation_classes": allowed,
        "forbidden_operations": [],
        "included_work_item_ids": [],
        "excluded_work_item_ids": [],
        "included_spec_ids": [],
        "excluded_spec_ids": [],
    }


def _install_authority_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    taxonomy = sweep.preflight._load_operation_taxonomy(REPO_ROOT)
    monkeypatch.setattr(sweep.preflight, "_load_operation_taxonomy", lambda _root: taxonomy)

    def extract(_root: Path, content: str, _specs: list[str]) -> dict[str, object] | None:
        for authorization_id in ("PAUTH-ALLOWED", "PAUTH-NO-BRIDGE"):
            if authorization_id in content:
                return _envelope(authorization_id)
        return None

    monkeypatch.setattr(sweep.preflight, "extract_and_validate_project_authorization", extract)


def _write_version(root: Path, slug: str, version: int, status: str, body: str) -> Path:
    bridge = root / "bridge"
    bridge.mkdir(exist_ok=True)
    path = bridge / f"{slug}-{version:03d}.md"
    path.write_text(f"{status}\n{body}", encoding="utf-8")
    return path


def _proposal(slug: str, authorization_id: str, target: str) -> str:
    return (
        "bridge_kind: prime_proposal\n"
        f"Document: {slug}\n"
        "Version: 001\n"
        f"Project Authorization: {authorization_id}\n"
        "Project: PROJECT-FIXTURE\n"
        "Work Item: WI-FIXTURE\n"
        f'target_paths: ["{target}"]\n\n'
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )


def _go(slug: str) -> str:
    return f"Responds to: bridge/{slug}-001.md\n\n# Approved\n"


def _report(slug: str, target: str, authorization_id: str = "PAUTH-REPORT-MUST-NOT-WIN") -> str:
    return (
        "bridge_kind: implementation_report\n"
        f"Document: {slug}\n"
        "Version: 003\n"
        f"Approved proposal: bridge/{slug}-001.md\n"
        f"Project Authorization: {authorization_id}\n"
        "Project: PROJECT-FIXTURE\n"
        "Work Item: WI-FIXTURE\n"
        f'target_paths: ["{target}"]\n\n'
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )


def _thread(
    root: Path,
    slug: str,
    authorization_id: str,
    *,
    report: bool = False,
    terminal: bool = False,
) -> None:
    _write_version(root, slug, 1, "REVISED", _proposal(slug, authorization_id, "scripts/tool.py"))
    _write_version(root, slug, 2, "GO", _go(slug))
    if report:
        _write_version(root, slug, 3, "NEW", _report(slug, "platform_tests/test_tool.py"))
    if terminal:
        terminal_version = 4 if report else 3
        _write_version(root, slug, terminal_version, "VERIFIED", "# Terminal\n")


def _bridge_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "bridge").glob("*.md")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_sweep_enumerates_only_exposed_nonterminal_threads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_authority_fixture(monkeypatch)
    _thread(tmp_path, "authorized-report", "PAUTH-ALLOWED", report=True)
    _thread(tmp_path, "class-denied", "PAUTH-NO-BRIDGE")
    _thread(tmp_path, "missing-pauth", "PAUTH-MISSING")
    _thread(tmp_path, "terminal", "PAUTH-ALLOWED", report=True, terminal=True)

    inventory = sweep.build_inventory(tmp_path, decision_time=FIXED_TIME)
    rows = {row["bridge_id"]: row for row in inventory["rows"]}

    assert "terminal" not in rows
    assert rows["authorized-report"]["classification"] == "authorized"
    assert rows["authorized-report"]["authorization_id"] == "PAUTH-ALLOWED"
    assert rows["authorized-report"]["authorization_source"] == "bridge/authorized-report-001.md"
    assert rows["authorized-report"]["cohort"] == [
        "bridge/authorized-report-001.md",
        "bridge/authorized-report-002.md",
        "bridge/authorized-report-003.md",
        "bridge/authorized-report-004.md",
        "platform_tests/test_tool.py",
        "scripts/tool.py",
    ]
    assert rows["class-denied"]["classification"] == "mutation_class_denied"
    assert rows["missing-pauth"]["classification"] == "missing_pauth"
    assert inventory["has_exposure"] is True


def test_sweep_surfaces_malformed_newest_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_authority_fixture(monkeypatch)
    _thread(tmp_path, "malformed-latest", "PAUTH-ALLOWED")
    _write_version(tmp_path, "malformed-latest", 3, "BROKEN", "# Missing status token\n")

    inventory = sweep.build_inventory(tmp_path, decision_time=FIXED_TIME)

    assert inventory["rows"] == [
        {
            "bridge_id": "malformed-latest",
            "latest_status": None,
            "latest_path": "bridge/malformed-latest-003.md",
            "classification": "unknown_latest_status",
            "blocking_errors": ["Latest numbered bridge file has no recognized status token."],
        }
    ]


def test_sweep_rejects_unapproved_report_rebinding(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_authority_fixture(monkeypatch)
    slug = "unapproved-report"
    _write_version(tmp_path, slug, 1, "REVISED", _proposal(slug, "PAUTH-ALLOWED", "scripts/tool.py"))
    _write_version(tmp_path, slug, 2, "NO-GO", "# Rejected\n")
    _write_version(tmp_path, slug, 3, "NEW", _report(slug, "platform_tests/test_tool.py", "PAUTH-NO-BRIDGE"))

    row = sweep.build_inventory(tmp_path, decision_time=FIXED_TIME)["rows"][0]

    assert row["classification"] == "lifecycle_resolution_failure"
    assert "no matching earlier GO verdict" in row["blocking_errors"][0]
    assert row["authorization_id"] is None


def test_sweep_surfaces_pauth_evaluator_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    taxonomy = sweep.preflight._load_operation_taxonomy(REPO_ROOT)
    monkeypatch.setattr(sweep.preflight, "_load_operation_taxonomy", lambda _root: taxonomy)
    monkeypatch.setattr(
        sweep.preflight,
        "extract_and_validate_project_authorization",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(sweep.preflight.AuthorizationError("malformed PAUTH fixture")),
    )
    _thread(tmp_path, "evaluator-failure", "PAUTH-ALLOWED")

    row = sweep.build_inventory(tmp_path, decision_time=FIXED_TIME)["rows"][0]

    assert row["classification"] == "pauth_load_or_evaluator_failure"
    assert "malformed PAUTH fixture" in row["blocking_errors"][0]


def test_sweep_discards_mixed_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_authority_fixture(monkeypatch)
    _thread(tmp_path, "concurrent", "PAUTH-ALLOWED")
    fingerprints = iter(("sha256:start", "sha256:end"))
    monkeypatch.setattr(sweep, "_source_fingerprint", lambda *_args: next(fingerprints))

    inventory = sweep.build_inventory(tmp_path, decision_time=FIXED_TIME)

    assert inventory["scan_consistent"] is False
    assert inventory["source_fingerprint"] is None
    assert inventory["rows"] == []
    assert inventory["classification_counts"] == {"concurrent_source_change": 1}
    assert "mixed-snapshot results were discarded" in inventory["blocking_errors"][0]


def test_sweep_is_fixture_rooted_and_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_authority_fixture(monkeypatch)
    _thread(tmp_path, "authorized", "PAUTH-ALLOWED")
    before = _bridge_digest(tmp_path)
    output = Path(".gtkb-state/pauth-exposure/result.json")
    args = [
        "--project-root",
        str(tmp_path),
        "--decision-time",
        "2026-07-30T12:00:00Z",
        "--json",
        "--output",
        str(output),
    ]

    assert sweep.main(args) == 0
    first = (tmp_path / output).read_bytes()
    assert sweep.main(args) == 0
    assert (tmp_path / output).read_bytes() == first
    assert _bridge_digest(tmp_path) == before
    assert json.loads(first)["decision_time"] == "2026-07-30T12:00:00Z"

    assert sweep.main(["--project-root", str(tmp_path), "--output", "outside.md"]) == 2
    assert "must remain under" in capsys.readouterr().err
    assert not (tmp_path / "outside.md").exists()
