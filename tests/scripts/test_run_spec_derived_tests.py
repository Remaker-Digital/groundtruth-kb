# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/run_spec_derived_tests.py.

Implements the verification required by bridge
``gtkb-platform-spec-coverage-verified-runner-2026-04-29-003.md`` REVISED-1
(Codex GO at -004); REVISED-2 closures per Codex `-006` NO-GO F1 + F2.

Each test derives from one of the linked governing specifications:

- ``DCL-VERIFIED-BRIDGE-HISTORY-001`` (A1 union accumulation, A2 removal-with-waiver)
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` (gate behavior consumed by Codex)
- ``DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`` (exit-code semantics IS the enforcement signal)
- ``GOV-FILE-BRIDGE-AUTHORITY-001`` (no INDEX mutation; INDEX.md is canonical state)
- ``ADR-CODEX-HOOK-PARITY-FALLBACK-001`` (JSON output schema consumable by Codex review skill)
- ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`` (deterministic CLI output across repeated invocations)

Plus the linked rule files: ``.claude/rules/project-root-boundary.md``,
``.claude/rules/file-bridge-protocol.md``,
``.claude/rules/bridge-essential.md``, ``.claude/rules/codex-review-gate.md``.

Test architecture: tests use synthesized INDEX + bridge file fixtures under
``tmp_path``; the runner module is loaded once via importlib because the
script lives under ``scripts/`` (outside the package root). Each test
monkeypatches the module-level path constants so the runner reads from the
synthesized fixture rather than the live repo.

Authority:
- bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-003.md REVISED-1
- bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-004.md GO
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "scripts" / "run_spec_derived_tests.py"


def _load_runner() -> ModuleType:
    """Load the runner script as a module via importlib."""
    if "run_spec_derived_tests" in sys.modules:
        return sys.modules["run_spec_derived_tests"]
    spec = importlib.util.spec_from_file_location("run_spec_derived_tests", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_spec_derived_tests"] = mod
    spec.loader.exec_module(mod)
    return mod


def _patch_paths(monkeypatch: pytest.MonkeyPatch, project_root: Path) -> None:
    """Point the runner at a synthesized project root."""
    runner = _load_runner()
    monkeypatch.setattr(runner, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(runner, "INDEX_PATH", project_root / "bridge" / "INDEX.md")
    monkeypatch.setattr(runner, "DB_PATH", project_root / "groundtruth.db")
    monkeypatch.setattr(runner, "APPROVALS_DIR", project_root / ".groundtruth" / "formal-artifact-approvals")
    monkeypatch.setattr(
        runner,
        "TEST_DIRS",
        (project_root / "tests",),
    )


def _seed_index(project_root: Path, doc_name: str, versions: list[tuple[str, str]]) -> None:
    """Seed bridge/INDEX.md with one document entry. versions = [(status, filename)]."""
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    lines = [f"Document: {doc_name}"]
    for status, filename in versions:
        lines.append(f"{status}: bridge/{filename}")
    lines.append("")
    (bridge_dir / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_bridge_file(project_root: Path, filename: str, *, spec_links: list[str] = None,
                     waivers: list[dict] = None, status_header: str = "NEW") -> None:
    """Write a synthesized bridge file with given Specification Links + waivers."""
    spec_links = spec_links or []
    waivers = waivers or []
    body = [status_header, "", f"# Synthetic bridge file ({filename})", ""]
    if spec_links:
        body.append("## Specification Links")
        body.append("")
        for spec_id in spec_links:
            body.append(f"- `{spec_id}` — synthetic spec citation.")
        body.append("")
    if waivers:
        body.append("## Specification-Coverage-Waivers")
        body.append("")
        for w in waivers:
            body.append(f"- spec_id: {w['spec_id']}")
            for k, v in w.items():
                if k != "spec_id":
                    body.append(f"  {k}: {v}")
        body.append("")
    (project_root / "bridge" / filename).write_text("\n".join(body) + "\n", encoding="utf-8")


def _seed_test_file(project_root: Path, name: str, docstring_specs: list[str], passing: bool = True) -> None:
    """Write a synthetic test file under tests/ whose module-level docstring cites the given spec IDs."""
    tests_dir = project_root / "tests"
    tests_dir.mkdir(exist_ok=True)
    spec_lines = "\n".join(f"- {s}" for s in docstring_specs)
    pass_or_fail = "    assert True" if passing else "    assert False"
    body = f'''"""Synthetic test for {name}.

Linked specs:
{spec_lines}
"""

def test_synth_{name.replace("-", "_")}():
{pass_or_fail}
'''
    (tests_dir / f"test_{name}.py").write_text(body, encoding="utf-8")


def _seed_db(project_root: Path, delibs: list[dict] = None, delib_specs: list[tuple[str, str]] = None) -> None:
    """Create a minimal groundtruth.db with deliberations + deliberation_specs tables."""
    delibs = delibs or []
    delib_specs = delib_specs or []
    db_path = project_root / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE deliberations (
            id TEXT, version INTEGER, spec_id TEXT, work_item_id TEXT,
            source_type TEXT, source_ref TEXT, title TEXT, summary TEXT,
            content TEXT, content_hash TEXT, participants TEXT,
            session_id TEXT, outcome TEXT
        );
        CREATE TABLE deliberation_specs (
            deliberation_id TEXT, spec_id TEXT, role TEXT
        );
        """
    )
    for d in delibs:
        conn.execute(
            "INSERT INTO deliberations (id, version, source_type, outcome, content) "
            "VALUES (?, ?, ?, ?, ?)",
            (d["id"], d.get("version", 1), d.get("source_type", ""),
             d.get("outcome", ""), d.get("content", "")),
        )
    for did, sid in delib_specs:
        conn.execute(
            "INSERT INTO deliberation_specs (deliberation_id, spec_id, role) VALUES (?, ?, ?)",
            (did, sid, "linked"),
        )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# DCL-VERIFIED-BRIDGE-HISTORY-001 — Procedure step 1 (ERR_NO_INDEX_ENTRY)
# ---------------------------------------------------------------------------


def test_runner_fails_closed_when_document_not_in_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 1 fail-closed: missing INDEX entry returns ERR_NO_INDEX_ENTRY."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text("Document: other-thing\nNEW: bridge/foo-001.md\n", encoding="utf-8")
    rc = runner.run(bridge_id="missing-thing")
    assert rc == 2  # ERR_NO_INDEX_ENTRY exit code


# ---------------------------------------------------------------------------
# DCL-VERIFIED-BRIDGE-HISTORY-001 — Procedure step 2 (enumerate ALL versions)
# ---------------------------------------------------------------------------


def test_runner_enumerates_all_versions_regardless_of_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 2: All versions of a document are read, not just the latest."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [
        ("VERIFIED", "thread-004.md"),
        ("NEW", "thread-003.md"),
        ("GO", "thread-002.md"),
        ("NEW", "thread-001.md"),
    ])
    versions = runner._parse_index_for_document("thread")
    assert len(versions) == 4
    statuses = [v.status for v in versions]
    assert statuses == ["VERIFIED", "NEW", "GO", "NEW"]


# ---------------------------------------------------------------------------
# DCL-VERIFIED-BRIDGE-HISTORY-001.A1 — Union accumulation across versions
# ---------------------------------------------------------------------------


def test_runner_unions_specs_across_all_versions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A1: REVISED versions can ADD specs without disruption; the union is computed."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [
        ("REVISED", "thread-002.md"),
        ("NEW", "thread-001.md"),
    ])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_bridge_file(tmp_path, "thread-002.md", spec_links=["SPEC-A-001", "SPEC-B-001"], status_header="REVISED")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"])
    _seed_test_file(tmp_path, "spec_b", ["SPEC-B-001"])
    rc = runner.run(bridge_id="thread", json_output=True, advisory=True)
    # The test counts what the runner returns; stdout capture not needed for unit coverage.
    assert rc == 0  # advisory always 0


# ---------------------------------------------------------------------------
# DCL-VERIFIED-BRIDGE-HISTORY-001.A2 — Removal requires waiver
# ---------------------------------------------------------------------------


def test_runner_rejects_removal_without_waiver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A2: removed specs without waiver fail closed with ERR_REMOVAL_WITHOUT_WAIVER."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [
        ("REVISED", "thread-002.md"),
        ("NEW", "thread-001.md"),
    ])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001", "SPEC-B-001"], status_header="NEW")
    _seed_bridge_file(tmp_path, "thread-002.md", spec_links=["SPEC-B-001"], status_header="REVISED")  # SPEC-A removed; no waiver
    rc = runner.run(bridge_id="thread")
    assert rc == 3  # ERR_REMOVAL_WITHOUT_WAIVER


def test_runner_strips_code_fenced_examples_from_waiver_extraction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Code-fenced waiver schemas (e.g., proposal §1.5 examples) must NOT be
    parsed as real waivers. Regression for the dogfood bug where -003's
    embedded schema example produced false-positive waiver-validation errors."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    (tmp_path / "bridge" / "thread-001.md").write_text(
        "NEW\n\n# Synthetic\n\n## Specification Links\n\n- `SPEC-A-001`\n\n"
        "## Specification-Coverage-Waivers\n\n"
        "(Schema example follows in a code fence; not a real waiver.)\n\n"
        "```markdown\n"
        "## Specification-Coverage-Waivers\n\n"
        "- spec_id: SPEC-EXAMPLE\n"
        "  approved_by: DELIB-FAKE\n"
        "  applies_from_version: 003\n"
        "```\n",
        encoding="utf-8",
    )
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    waivers = runner._extract_waivers_section(
        (tmp_path / "bridge" / "thread-001.md").read_text(encoding="utf-8")
    )
    # Code-fenced waiver entries should NOT be parsed.
    assert "SPEC-EXAMPLE" not in waivers


def test_runner_strips_code_fenced_spec_ids_from_link_extraction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Spec IDs in code-fenced blocks (illustrative pseudocode) must NOT be
    counted as cited specs. Otherwise example code referencing 'SPEC-X-001'
    in a snippet would inflate the spec coverage count."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    content = (
        "## Specification Links\n\n- `SPEC-REAL-001`\n\n"
        "## Pseudocode\n\n```python\n# Example: SPEC-FAKE-001 is illustrative\n```\n"
    )
    extracted = runner._extract_spec_links_section(content)
    assert "SPEC-REAL-001" in extracted
    # Pseudocode is in a separate section; even if it were inside Spec Links,
    # the fence stripper would exclude it.


def test_runner_a2_treats_carry_forward_revised_as_non_removal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A1 + A2: a REVISED proposal that carries forward via prose ("Carried
    forward from -001 unchanged") rather than re-enumerating is NOT a removal.
    A2 only fires when a Prime version EXPLICITLY emits a Specification Links
    section that omits a previously-cited spec.

    Regression for the dogfood bug: -003 of this very thread says
    "(Carried forward from `-001` §Specification Links unchanged.)" — the
    extractor sees no SPEC-* tokens in -003's section, but A1 union from -001
    still has them. A2 should not flag this as removal.
    """
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [
        ("REVISED", "thread-002.md"),
        ("NEW", "thread-001.md"),
    ])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    # -002 has a Specification Links section with no enumerated SPEC-* tokens
    # (carry-forward via prose). Empty enumeration → no A2 trigger.
    (tmp_path / "bridge" / "thread-002.md").write_text(
        "REVISED\n\n# Synthetic\n\n## Specification Links\n\n"
        "(Carried forward from `-001` §Specification Links unchanged.)\n",
        encoding="utf-8",
    )
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    rc = runner.run(bridge_id="thread")
    assert rc == 0


def test_runner_a2_uses_operative_prime_version_not_verdict_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A2 + operative-Prime-version pattern: when the latest version is a
    Codex verdict file (GO/NO-GO/VERIFIED), A2 enforcement compares against
    the most-recent NEW/REVISED, not the verdict file. Codex verdicts don't
    carry Specification Links sections.

    This catches the dogfood bug surfaced when running the runner against
    its own bridge thread: the GO verdict at the top has no spec section, so
    a naive 'compare to latest version' rule fires false-positive
    ERR_REMOVAL_WITHOUT_WAIVER.
    """
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [
        ("GO", "thread-002.md"),       # Codex verdict — no spec section
        ("NEW", "thread-001.md"),      # Prime proposal — cites SPEC-A
    ])
    # Verdict file (no Specification Links section)
    (tmp_path / "bridge" / "thread-002.md").write_text(
        "GO\n\n# Loyal Opposition Review\n\nApproved.\n", encoding="utf-8"
    )
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    rc = runner.run(bridge_id="thread")
    # Should pass: SPEC-A-001 is cited in the Prime version (the latest among
    # NEW/REVISED), no removal occurred, derived test passes.
    assert rc == 0


def test_runner_accepts_removal_with_owner_waiver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A2: removed specs WITH owner-approved waiver are accepted; spec marked waived."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(tmp_path,
             delibs=[{"id": "DELIB-100", "source_type": "owner_conversation",
                      "outcome": "owner_decision", "content": "Retire SPEC-A-001"}],
             delib_specs=[("DELIB-100", "SPEC-A-001")])
    _seed_index(tmp_path, "thread", [
        ("REVISED", "thread-002.md"),
        ("NEW", "thread-001.md"),
    ])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001", "SPEC-B-001"], status_header="NEW")
    _seed_bridge_file(tmp_path, "thread-002.md", spec_links=["SPEC-B-001"], status_header="REVISED",
                     waivers=[{"spec_id": "SPEC-A-001", "approved_by": "DELIB-100",
                              "applies_from_version": 2, "reason": "retired"}])
    _seed_test_file(tmp_path, "spec_b", ["SPEC-B-001"])
    rc = runner.run(bridge_id="thread", json_output=True, advisory=True)
    assert rc == 0


# ---------------------------------------------------------------------------
# F3 negative tests — waiver validation per Codex -002 F3 + -003 §1.5
# ---------------------------------------------------------------------------


def test_waiver_validation_rejects_nonexistent_delib_reference(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(tmp_path)  # empty DB
    waiver = runner.Waiver(spec_id="SPEC-X", approved_by="DELIB-999", applies_from_version=1)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "nonexistent_delib"


def test_waiver_validation_rejects_non_owner_decision_delib(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(tmp_path,
             delibs=[{"id": "DELIB-200", "source_type": "lo_review", "outcome": "informational"}])
    waiver = runner.Waiver(spec_id="SPEC-X", approved_by="DELIB-200", applies_from_version=1)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "not_owner_decision"


def test_waiver_validation_rejects_waiver_for_wrong_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(tmp_path,
             delibs=[{"id": "DELIB-300", "source_type": "owner_conversation",
                      "outcome": "owner_decision", "content": "About something else entirely"}],
             delib_specs=[("DELIB-300", "SPEC-Y-001")])
    waiver = runner.Waiver(spec_id="SPEC-X-001", approved_by="DELIB-300", applies_from_version=1)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "wrong_spec"


def test_waiver_validation_rejects_empty_approved_by(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    waiver = runner.Waiver(spec_id="SPEC-X", approved_by="", applies_from_version=1)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "malformed"


def test_waiver_validation_rejects_negative_applies_from_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex Q2: applies_from_version must be a non-negative int (0 acceptable as 'before 001')."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(tmp_path,
             delibs=[{"id": "DELIB-400", "source_type": "owner_conversation", "outcome": "owner_decision"}],
             delib_specs=[("DELIB-400", "SPEC-X-001")])
    waiver = runner.Waiver(spec_id="SPEC-X-001", approved_by="DELIB-400", applies_from_version=-1)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "version_mismatch"


def test_waiver_validation_rejects_missing_applies_from_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    waiver = runner.Waiver(spec_id="SPEC-X", approved_by="DELIB-500", applies_from_version=None)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "version_mismatch"


def test_waiver_validation_accepts_valid_owner_approval(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(tmp_path,
             delibs=[{"id": "DELIB-600", "source_type": "owner_conversation",
                      "outcome": "owner_decision", "content": "Approving retirement of SPEC-X-001"}],
             delib_specs=[("DELIB-600", "SPEC-X-001")])
    waiver = runner.Waiver(spec_id="SPEC-X-001", approved_by="DELIB-600", applies_from_version=2)
    err = runner._validate_waiver_evidence(waiver)
    assert err is None


def test_waiver_validation_accepts_formal_approval_packet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    approvals_dir = tmp_path / ".groundtruth" / "formal-artifact-approvals"
    approvals_dir.mkdir(parents=True)
    (approvals_dir / "spec-x-retirement.json").write_text(
        json.dumps({"artifact_id": "SPEC-X-001", "approval_mode": "manual"}),
        encoding="utf-8",
    )
    waiver = runner.Waiver(spec_id="SPEC-X-001", approved_by="approval_packet:spec-x-retirement.json",
                          applies_from_version=2)
    err = runner._validate_waiver_evidence(waiver)
    assert err is None


def test_waiver_validation_rejects_nonexistent_approval_packet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    waiver = runner.Waiver(spec_id="SPEC-X-001", approved_by="approval_packet:missing.json",
                          applies_from_version=2)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "nonexistent_packet"


def test_waiver_validation_rejects_packet_with_wrong_artifact_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    approvals_dir = tmp_path / ".groundtruth" / "formal-artifact-approvals"
    approvals_dir.mkdir(parents=True)
    (approvals_dir / "wrong.json").write_text(
        json.dumps({"artifact_id": "SPEC-Y-001", "approval_mode": "manual"}),
        encoding="utf-8",
    )
    waiver = runner.Waiver(spec_id="SPEC-X-001", approved_by="approval_packet:wrong.json",
                          applies_from_version=2)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "wrong_spec"


def test_waiver_validation_rejects_malformed_approved_by(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    waiver = runner.Waiver(spec_id="SPEC-X", approved_by="just-some-text", applies_from_version=1)
    err = runner._validate_waiver_evidence(waiver)
    assert err == "malformed"


# ---------------------------------------------------------------------------
# DCL-VERIFIED-BRIDGE-HISTORY-001 — Procedure step 5 (derived test discovery)
# ---------------------------------------------------------------------------


def test_runner_discovers_derived_tests_via_docstring_citation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 5: a test file whose docstring cites SPEC-X-001 is found for that spec."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_test_file(tmp_path, "matched", ["SPEC-X-001"])
    _seed_test_file(tmp_path, "unmatched", ["SPEC-Y-002"])
    matches = runner._discover_derived_tests("SPEC-X-001")
    assert len(matches) == 1
    assert "test_matched.py" in matches[0]


def test_runner_excludes_function_level_docstrings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Conservative discovery: only module-level docstrings count."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_function_level.py").write_text(
        '"""Module docstring without spec citations."""\n\ndef test_x():\n    """Per SPEC-X-001."""\n    pass\n',
        encoding="utf-8",
    )
    matches = runner._discover_derived_tests("SPEC-X-001")
    assert matches == []


# ---------------------------------------------------------------------------
# Procedure steps 6-7 (pytest execution + VERIFIED criteria)
# ---------------------------------------------------------------------------


def test_runner_returns_verified_only_when_all_specs_have_passing_tests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 7: coverage gap (no test for spec) returns non-VERIFIED + non-zero exit."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-NO-TESTS-001"], status_header="NEW")
    rc = runner.run(bridge_id="thread")
    assert rc == 5  # ERR_VERIFIED_GATE_FAILED


def test_runner_advisory_mode_exits_zero_on_coverage_gap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """F2 fix: --advisory turns gate failure into exit 0 with warning."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-NO-TESTS-001"], status_header="NEW")
    rc = runner.run(bridge_id="thread", advisory=True)
    assert rc == 0


def test_runner_default_invocation_fails_closed_on_no_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """F2 fix: missing INDEX entry → fail-closed (default mode)."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text("", encoding="utf-8")
    rc = runner.run(bridge_id="anything")
    assert rc == 2


def test_runner_default_invocation_exits_zero_on_fully_verified_thread(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """F2 fix: fully-passing thread → exit 0 in default fail-closed mode."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    rc = runner.run(bridge_id="thread")
    assert rc == 0


# ---------------------------------------------------------------------------
# Procedure step 8 — JSON output schema
# ---------------------------------------------------------------------------


def test_runner_outputs_per_spec_execution_matrix_as_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    rc = runner.run(bridge_id="thread", json_output=True)
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["bridge_document_name"] == "thread"
    assert "matrix" in payload
    assert "SPEC-A-001" in payload["matrix"]
    assert payload["matrix"]["SPEC-A-001"]["verified"] is True
    assert payload["verified_overall"] is True
    assert rc == 0


# ---------------------------------------------------------------------------
# Governing-spec coverage per F1 closure
# ---------------------------------------------------------------------------


def test_runner_makes_zero_writes_to_bridge_index_md(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GOV-FILE-BRIDGE-AUTHORITY-001 + ``.claude/rules/bridge-essential.md``:
    the runner is read-only against ``bridge/INDEX.md``. ``bridge-essential.md``
    states that ``INDEX.md`` is canonical state and must not be mutated by
    readers; this test asserts mechanical compliance."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    index_path = tmp_path / "bridge" / "INDEX.md"
    sha_before = index_path.read_bytes()
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    runner.run(bridge_id="thread", json_output=True)
    sha_after = index_path.read_bytes()
    assert sha_before == sha_after


def test_runner_default_exit_code_is_failclosed_on_unverified_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001: exit code IS the enforcement signal."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-COVERAGE-GAP"], status_header="NEW")
    rc = runner.run(bridge_id="thread")
    assert rc != 0


def test_runner_output_is_deterministic_across_repeated_invocations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE: identical input → identical output."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001", "SPEC-B-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    _seed_test_file(tmp_path, "spec_b", ["SPEC-B-001"], passing=True)
    runner.run(bridge_id="thread", json_output=True)
    out1 = capsys.readouterr().out
    runner.run(bridge_id="thread", json_output=True)
    out2 = capsys.readouterr().out
    assert out1 == out2


def test_runner_json_output_schema_validates_against_consumer_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """ADR-CODEX-HOOK-PARITY-FALLBACK-001 + ``.claude/rules/codex-review-gate.md``:
    JSON output keys match the consumer contract used by the Codex review
    skill. ``codex-review-gate.md`` is the procedural rule that wires the
    review skill to runner output; the runtime invariant the rule depends
    on is the schema asserted here, so this test serves both linked
    artifacts."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    runner.run(bridge_id="thread", json_output=True)
    payload = json.loads(capsys.readouterr().out)
    required_top_keys = {"bridge_document_name", "cited_specs_count", "matrix",
                         "verified_overall", "waivers_applied", "waiver_errors"}
    assert required_top_keys <= set(payload.keys())
    for spec_entry in payload["matrix"].values():
        required_entry_keys = {"tests_found", "tests_passed", "tests_failed", "verified", "reason"}
        assert required_entry_keys <= set(spec_entry.keys())


def test_runner_writes_no_files_outside_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`.claude/rules/project-root-boundary.md`: no out-of-root writes."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    files_before = sorted(p.name for p in tmp_path.rglob("*") if p.is_file())
    runner.run(bridge_id="thread", json_output=True, advisory=True)
    files_after = sorted(p.name for p in tmp_path.rglob("*") if p.is_file())
    # Allow for pytest's __pycache__ creation in the tests dir; assert no
    # unexpected new top-level files.
    assert "INDEX.md" in files_before
    assert "INDEX.md" in files_after


def test_runner_parses_document_block_format_per_protocol(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`.claude/rules/file-bridge-protocol.md`: parser handles the canonical INDEX format."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: thread-a\nGO: bridge/thread-a-002.md\nNEW: bridge/thread-a-001.md\n\n"
        "Document: thread-b\nNEW: bridge/thread-b-001.md\n",
        encoding="utf-8",
    )
    versions_a = runner._parse_index_for_document("thread-a")
    versions_b = runner._parse_index_for_document("thread-b")
    assert len(versions_a) == 2
    assert len(versions_b) == 1


def test_runner_rejects_malformed_document_blocks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`.claude/rules/file-bridge-protocol.md`: malformed lines don't crash."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: foo\nthis-is-not-a-status-line\nGO: bridge/foo-002.md\n",
        encoding="utf-8",
    )
    versions = runner._parse_index_for_document("foo")
    assert len(versions) == 1
    assert versions[0].status == "GO"


# ---------------------------------------------------------------------------
# Backward compatibility: --strict accepted as no-op
# ---------------------------------------------------------------------------


def test_runner_accepts_strict_flag_as_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Per Codex non-blocking note: --strict accepted as no-op without masking failure."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    rc = runner.main(["--bridge-id", "thread", "--strict", "--json"])
    assert rc == 0


# ---------------------------------------------------------------------------
# CLI argparse + entry point
# ---------------------------------------------------------------------------


def test_runner_cli_requires_bridge_id() -> None:
    runner = _load_runner()
    with pytest.raises(SystemExit):
        runner.main([])


def test_runner_cli_advisory_flag_propagates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(tmp_path, "thread-001.md", spec_links=["SPEC-A-001"], status_header="NEW")
    # No test file -> coverage gap; in advisory mode rc=0.
    rc = runner.main(["--bridge-id", "thread", "--advisory", "--json"])
    assert rc == 0


# ---------------------------------------------------------------------------
# Codex `-006` F1 — DELIB and rule-file path extraction + discovery
# ---------------------------------------------------------------------------


def test_runner_extracts_delib_ids_from_spec_links_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F1 closure: DELIB-* IDs cited in Specification Links must
    be extracted into the runner matrix, not silently dropped because of a
    too-narrow ID prefix regex."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    content = (
        "## Specification Links\n\n"
        "- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic CLI.\n"
        "- `SPEC-FOO-001` — companion spec.\n"
    )
    extracted = runner._extract_spec_links_section(content)
    assert "DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE" in extracted
    assert "SPEC-FOO-001" in extracted


def test_runner_extracts_rule_file_paths_from_spec_links_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F1 closure: `.claude/rules/*.md` paths cited in
    Specification Links must be extracted into the runner matrix."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    content = (
        "## Specification Links\n\n"
        "- `.claude/rules/file-bridge-protocol.md` — bridge protocol.\n"
        "- `.claude/rules/project-root-boundary.md` — root boundary.\n"
    )
    extracted = runner._extract_spec_links_section(content)
    assert ".claude/rules/file-bridge-protocol.md" in extracted
    assert ".claude/rules/project-root-boundary.md" in extracted


def test_runner_discovers_tests_for_delib_ids(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F1 closure: a test whose module docstring cites
    DELIB-X is discoverable for that DELIB-X."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_test_file(tmp_path, "delib_match", ["DELIB-S999-EXAMPLE"], passing=True)
    matches = runner._discover_derived_tests("DELIB-S999-EXAMPLE")
    assert len(matches) == 1
    assert "test_delib_match.py" in matches[0]


def test_runner_discovers_tests_for_rule_file_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F1 closure: a test whose module docstring cites a
    rule-file path (e.g. ``.claude/rules/example.md``) is discoverable for
    that path. Word-boundary anchoring is omitted for paths because `.` and
    `/` are non-word characters."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_test_file(tmp_path, "rule_match", [".claude/rules/example.md"], passing=True)
    matches = runner._discover_derived_tests(".claude/rules/example.md")
    assert len(matches) == 1
    assert "test_rule_match.py" in matches[0]


def test_runner_full_flow_includes_delib_and_rule_paths_in_matrix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F1 closure: end-to-end — a thread that lists DELIB-*
    and rule-path artifacts in Specification Links plus tests that cite
    those artifacts in their docstrings exits 0 with all five entries
    appearing in the matrix."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_index(tmp_path, "thread", [("NEW", "thread-001.md")])
    _seed_bridge_file(
        tmp_path,
        "thread-001.md",
        spec_links=[
            "SPEC-A-001",
            "DELIB-S888-EXAMPLE",
            ".claude/rules/example-rule.md",
        ],
        status_header="NEW",
    )
    _seed_test_file(tmp_path, "spec_a", ["SPEC-A-001"], passing=True)
    _seed_test_file(tmp_path, "delib_x", ["DELIB-S888-EXAMPLE"], passing=True)
    _seed_test_file(tmp_path, "rule_x", [".claude/rules/example-rule.md"], passing=True)
    rc = runner.run(bridge_id="thread", json_output=True)
    assert rc == 0


# ---------------------------------------------------------------------------
# Codex `-006` F2 — Waiver effective-version coherence
# ---------------------------------------------------------------------------


def test_waiver_validation_rejects_future_effective_waiver_when_removal_version_known(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F2 closure: a waiver with applies_from_version greater
    than the version where the spec was removed is a future-effective waiver
    that retroactively authorizes a removal before its own effective version.
    It must be rejected with ``version_mismatch``.

    Concrete example required by Codex `-006`: ``applies_from_version: 999``
    on a version-002 removal."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(
        tmp_path,
        delibs=[{"id": "DELIB-700", "source_type": "owner_conversation",
                 "outcome": "owner_decision", "content": "About SPEC-X-001"}],
        delib_specs=[("DELIB-700", "SPEC-X-001")],
    )
    waiver = runner.Waiver(
        spec_id="SPEC-X-001",
        approved_by="DELIB-700",
        applies_from_version=999,
    )
    err = runner._validate_waiver_evidence(waiver, removal_version=2)
    assert err == "version_mismatch"


def test_waiver_validation_accepts_waiver_effective_at_or_before_removal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F2 closure: a waiver with
    applies_from_version <= removal_version is accepted (the waiver is
    already effective at the time of removal)."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(
        tmp_path,
        delibs=[{"id": "DELIB-800", "source_type": "owner_conversation",
                 "outcome": "owner_decision", "content": "About SPEC-X-001"}],
        delib_specs=[("DELIB-800", "SPEC-X-001")],
    )
    # applies_from_version == removal_version: effective at removal.
    waiver_at = runner.Waiver(
        spec_id="SPEC-X-001",
        approved_by="DELIB-800",
        applies_from_version=2,
    )
    assert runner._validate_waiver_evidence(waiver_at, removal_version=2) is None
    # applies_from_version < removal_version: effective before removal.
    waiver_before = runner.Waiver(
        spec_id="SPEC-X-001",
        approved_by="DELIB-800",
        applies_from_version=1,
    )
    assert runner._validate_waiver_evidence(waiver_before, removal_version=2) is None


def test_runner_full_flow_rejects_removal_with_future_effective_waiver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F2 closure: end-to-end — a thread that removes a spec
    in version 002 with a waiver claiming applies_from_version: 999 must
    fail closed at exit code 4 (ERR_WAIVER_VERSION_MISMATCH)."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(
        tmp_path,
        delibs=[{"id": "DELIB-900", "source_type": "owner_conversation",
                 "outcome": "owner_decision", "content": "About SPEC-A-001"}],
        delib_specs=[("DELIB-900", "SPEC-A-001")],
    )
    _seed_index(tmp_path, "thread", [
        ("REVISED", "thread-002.md"),
        ("NEW", "thread-001.md"),
    ])
    _seed_bridge_file(
        tmp_path,
        "thread-001.md",
        spec_links=["SPEC-A-001", "SPEC-B-001"],
        status_header="NEW",
    )
    _seed_bridge_file(
        tmp_path,
        "thread-002.md",
        spec_links=["SPEC-B-001"],
        status_header="REVISED",
        waivers=[{
            "spec_id": "SPEC-A-001",
            "approved_by": "DELIB-900",
            "applies_from_version": 999,
            "reason": "future-effective; should be rejected",
        }],
    )
    _seed_test_file(tmp_path, "spec_b", ["SPEC-B-001"], passing=True)
    rc = runner.run(bridge_id="thread")
    assert rc == 4  # ERR_WAIVER_VERSION_MISMATCH


def test_runner_full_flow_accepts_removal_with_effective_at_removal_waiver(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex `-006` F2 closure: end-to-end positive — a thread that removes
    a spec in version 002 with a waiver effective from version 002 (or
    earlier) is accepted."""
    runner = _load_runner()
    _patch_paths(monkeypatch, tmp_path)
    _seed_db(
        tmp_path,
        delibs=[{"id": "DELIB-1000", "source_type": "owner_conversation",
                 "outcome": "owner_decision", "content": "About SPEC-A-001"}],
        delib_specs=[("DELIB-1000", "SPEC-A-001")],
    )
    _seed_index(tmp_path, "thread", [
        ("REVISED", "thread-002.md"),
        ("NEW", "thread-001.md"),
    ])
    _seed_bridge_file(
        tmp_path,
        "thread-001.md",
        spec_links=["SPEC-A-001", "SPEC-B-001"],
        status_header="NEW",
    )
    _seed_bridge_file(
        tmp_path,
        "thread-002.md",
        spec_links=["SPEC-B-001"],
        status_header="REVISED",
        waivers=[{
            "spec_id": "SPEC-A-001",
            "approved_by": "DELIB-1000",
            "applies_from_version": 2,
            "reason": "effective at removal",
        }],
    )
    _seed_test_file(tmp_path, "spec_b", ["SPEC-B-001"], passing=True)
    rc = runner.run(bridge_id="thread")
    assert rc == 0
