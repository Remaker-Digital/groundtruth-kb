"""WI-3384 regression tests for CLAUSE-IN-ROOT disclosure-only path mentions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "adr_dcl_clause_preflight.py"
CLAUSES_CONFIG = REPO_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"


def _load_module():
    spec = importlib.util.spec_from_file_location("adr_dcl_clause_preflight", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["adr_dcl_clause_preflight"] = module
    spec.loader.exec_module(module)
    return module


def _in_root_clause(preflight):
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    return next(c for c in clauses if c.clause_id.endswith("/CLAUSE-IN-ROOT"))


def test_marked_disclosure_mention_not_refuted():
    preflight = _load_module()
    clause = _in_root_clause(preflight)
    content = (
        'target_paths: ["scripts/adr_dcl_clause_preflight.py"]\n\n'
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
        "<!-- in-root-disclosure -->\n"
        "Operator context mentioned C:\\Users\\micha\\scratch, which is not a GT-KB artifact.\n"
        "<!-- /in-root-disclosure -->\n"
    )

    found, reasons, gap = preflight.evaluate_evidence(clause, content)

    assert found is True, f"marked disclosure should not refute evidence; reasons={reasons}; gap={gap}"
    assert gap is None


def test_harness_local_observed_result_path_not_refuted():
    preflight = _load_module()
    clause = _in_root_clause(preflight)
    content = (
        'target_paths: ["scripts/adr_dcl_clause_preflight.py"]\n\n'
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
        "## Observed Results\n\n"
        "- Initial no-`--basetemp` pytest run failed during fixture setup because "
        "Windows denied access to `C:\\Users\\micha\\AppData\\Local\\Temp\\pytest-of-micha`; "
        "rerunning with repo-local `--basetemp` passed.\n"
    )

    found, reasons, gap = preflight.evaluate_evidence(clause, content)

    assert found is True, f"harness-local observed-result path should not refute; reasons={reasons}; gap={gap}"
    assert gap is None


def test_harness_local_diagnostic_disclosure_line_not_refuted():
    preflight = _load_module()
    clause = _in_root_clause(preflight)
    content = (
        'target_paths: ["scripts/adr_dcl_clause_preflight.py"]\n\n'
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
        "Diagnostic disclosure: stderr included local harness path "
        "`C:\\Users\\micha\\AppData\\Local\\Temp\\pytest-of-micha` from the test environment.\n"
    )

    found, reasons, gap = preflight.evaluate_evidence(clause, content)

    assert found is True, f"harness-local diagnostic disclosure should not refute; reasons={reasons}; gap={gap}"
    assert gap is None


def test_out_of_root_target_paths_still_refutes():
    preflight = _load_module()
    clause = _in_root_clause(preflight)
    unwrapped = (
        'target_paths: ["C:\\Users\\micha\\scratch\\out.md"]\n\n'
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
    )
    wrapped = (
        "<!-- in-root-disclosure -->\n"
        'target_paths: ["C:\\Users\\micha\\scratch\\out.md"]\n'
        "<!-- /in-root-disclosure -->\n"
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
    )

    for content in (unwrapped, wrapped):
        found, reasons, gap = preflight.evaluate_evidence(clause, content)
        assert found is False, f"out-of-root target_paths must still refute; reasons={reasons}"
        assert gap is not None


def test_unmarked_artifact_claim_still_refutes():
    preflight = _load_module()
    clause = _in_root_clause(preflight)
    content = (
        'target_paths: ["scripts/adr_dcl_clause_preflight.py"]\n\n'
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
        "The implementation will write output to C:\\Users\\micha\\scratch outside the project root.\n"
    )

    found, reasons, gap = preflight.evaluate_evidence(clause, content)

    assert found is False, f"unmarked out-of-root artifact claim must still refute; reasons={reasons}"
    assert gap is not None


def test_files_changed_user_profile_path_still_refutes():
    preflight = _load_module()
    clause = _in_root_clause(preflight)
    content = (
        'target_paths: ["scripts/adr_dcl_clause_preflight.py"]\n\n'
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
        "## Files Changed\n\n"
        "- C:\\Users\\micha\\scratch\\out.md (new)\n"
    )

    found, reasons, gap = preflight.evaluate_evidence(clause, content)

    assert found is False, f"out-of-root file-list entry must still refute; reasons={reasons}"
    assert gap is not None


def test_other_clauses_unchanged():
    preflight = _load_module()
    clause = preflight.Clause(
        clause_id="TEST/NO-DISCLOSURE-EXEMPT",
        spec_id="TEST",
        description="fixture",
        applies_when_path=(),
        applies_when_doc_name=(),
        applies_when_content=(),
        evidence_required="fixture evidence",
        evidence_pattern=r"(?i)valid evidence",
        failure_condition="fixture failure",
        failure_pattern=r"blocked-token",
        severity="blocking",
        waiver_policy="explicit_owner_waiver_required_in_bridge",
        enforcement_mode="blocking",
    )
    content = "valid evidence\n<!-- in-root-disclosure -->\nblocked-token\n<!-- /in-root-disclosure -->\n"

    found, reasons, gap = preflight.evaluate_evidence(clause, content)

    assert found is False, f"clauses without opt-in flag must scan full content; reasons={reasons}"
    assert gap is not None


def test_rehearsal_exception_preserved():
    preflight = _load_module()
    clause = _in_root_clause(preflight)
    content = (
        'target_paths: ["scripts/adr_dcl_clause_preflight.py"]\n\n'
        "Implementation artifacts remain in-root under E:\\GT-KB.\n"
        "The sanctioned rehearsal sandbox path is /tmp/agent-red-rehearsal/out.md.\n"
    )

    found, reasons, gap = preflight.evaluate_evidence(clause, content)

    assert found is True, f"agent-red rehearsal exception should remain allowed; reasons={reasons}; gap={gap}"
    assert gap is None


def test_flag_default_false(tmp_path: Path):
    preflight = _load_module()
    config = tmp_path / "wi3384-clause-fixture.toml"
    config.write_text(
        "[[clauses]]\n"
        'clause_id = "TEST/DEFAULT-FALSE"\n'
        'spec_id = "TEST"\n'
        'description = "fixture"\n'
        "applies_when_path = []\n"
        "applies_when_doc_name = []\n"
        "applies_when_content = []\n"
        'evidence_required = "fixture evidence"\n'
        'evidence_pattern = "valid evidence"\n'
        'failure_condition = "fixture failure"\n'
        'failure_pattern = "blocked-token"\n'
        'severity = "blocking"\n'
        'waiver_policy = "explicit_owner_waiver_required_in_bridge"\n'
        'enforcement_mode = "blocking"\n',
        encoding="utf-8",
    )

    clause = preflight.load_clauses(config)[0]

    assert clause.failure_pattern_disclosure_exempt is False
