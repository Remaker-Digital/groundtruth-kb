# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/bridge_report_test_claim_rerun_verifier.py.

Implementation of `gtkb-proposal-standards-test-claim-rerun-verifier` Slice 2
(GO at `-004`, REVISED-3 post-impl at `-007` after NO-GO `-006`).

The verifier re-runs pytest claims from bridge post-implementation reports to
detect stale or false `N passed`-style claims. NO-GO `-006` surfaced two
parser defects against the current bridge-report convention, addressed in
the REVISED-3 implementation and exercised by these tests:

* `test_extract_claims_split_command_result_blocks` covers FINDING-P1-001:
  the parser must associate a pytest command fenced block with its adjacent
  observed-result fenced block when reports split them around prose labels
  like `Observed result:`.
* `test_extract_claims_command_without_summary_flagged_error` and
  `test_run_pytest_claim_status_error_on_none_summary` cover FINDING-P2-002:
  a pytest command present without an associated summary block surfaces as
  `ERROR` (not silent pass) so `--strict` gating catches the evidence gap.

Tests exercise the verifier module directly for parser/result behavior and
spawn the CLI as a subprocess only for end-to-end JSON-shape and strict-exit
assertions.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "bridge_report_test_claim_rerun_verifier.py"


@pytest.fixture(scope="module")
def verifier_module():
    """Load the verifier as a module for direct function calls.

    Registers in ``sys.modules`` before ``exec_module`` to work around a
    Python 3.14 dataclass-decorator quirk where the decorator looks up
    ``cls.__module__`` in ``sys.modules`` and raises ``AttributeError`` if
    the module is not yet registered.
    """
    assert _SCRIPT_PATH.is_file(), f"Missing {_SCRIPT_PATH}"
    module_name = "bridge_report_test_claim_rerun_verifier"
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


# ---------------------------------------------------------------------------
# extract_claims contract
# ---------------------------------------------------------------------------


def test_extract_claims_same_block_preserves_legacy_pairing(verifier_module):
    """Original behavior: command + summary inside one fenced block still pair."""
    markdown = "## Test Evidence\n\n```text\npython -m pytest tests/foo_test.py -v\n...\n9 passed\n```\n"
    claims = verifier_module.extract_claims(markdown)
    assert len(claims) == 1
    assert claims[0].command == "python -m pytest tests/foo_test.py -v"
    assert claims[0].claimed_summary == "9 passed"
    assert claims[0].claimed_counts == {
        "passed": 9,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
    }


def test_extract_claims_split_command_result_blocks(verifier_module):
    """FINDING-P1-001 fix: pair command-block with following observed-result block.

    Mirrors the live convention used in
    ``bridge/gtkb-proposal-standards-test-claim-rerun-verifier-005.md`` lines
    ~90 through ~106, where the pytest command and its claimed output sit in
    two adjacent fenced blocks separated by an ``Observed result:`` label.
    """
    markdown = (
        "## Test Evidence\n"
        "\n"
        "```text\n"
        "python -m pytest platform_tests/scripts/test_foo.py -v --tb=short\n"
        "```\n"
        "\n"
        "Observed result:\n"
        "\n"
        "```text\n"
        "collected 9 items\n"
        "platform_tests/scripts/test_foo.py::test_a PASSED\n"
        "...\n"
        "9 passed\n"
        "```\n"
    )
    claims = verifier_module.extract_claims(markdown)
    assert len(claims) == 1, f"Expected 1 claim, got {len(claims)}: {claims!r}"
    assert claims[0].command == ("python -m pytest platform_tests/scripts/test_foo.py -v --tb=short")
    assert claims[0].claimed_summary == "9 passed"
    assert claims[0].claimed_counts["passed"] == 9


def test_extract_claims_command_without_summary_flagged_error(verifier_module):
    """FINDING-P2-002 fix: pytest command alone (no associated summary) is recorded
    as an unassociated claim so downstream logic emits ``ERROR``.

    Pre-fix behavior silently returned ``claim_count == 0`` for this shape,
    which let strict-mode gating pass on reports with command-but-no-result.
    """
    markdown = (
        "## Test Evidence\n"
        "\n"
        "```text\n"
        "python -m pytest platform_tests/scripts/test_foo.py\n"
        "```\n"
        "\n"
        "Some prose with no fenced result block.\n"
    )
    claims = verifier_module.extract_claims(markdown)
    assert len(claims) == 1
    assert claims[0].claimed_summary is None
    assert claims[0].claimed_counts == {}
    assert claims[0].command.startswith("python -m pytest")


def test_extract_claims_non_pytest_command_without_summary_skipped(verifier_module):
    """Refinement guard: non-pytest commands (ruff/uv/etc.) without an adjacent
    summary are skipped silently rather than flagged ERROR.

    Without this guard the FINDING-P2-002 fix would emit false positives for
    every ruff or impl-auth-validate fenced block in a bridge report, since
    the parser's command-prefix regex accepts a broad set of build/test
    entry points.
    """
    markdown = "```text\npython -m ruff check scripts/foo.py\n```\n\n```text\nAll checks passed!\n```\n"
    claims = verifier_module.extract_claims(markdown)
    assert claims == []


def test_extract_claims_non_pytest_command_with_inblock_summary_skipped(verifier_module):
    """NO-GO -009 FINDING-P1-001 closure: a non-pytest command whose output
    happens to contain pytest-like summary text (e.g. ``9 passed`` in the
    JSON output of the verifier itself) must NOT be paired into an ERROR
    claim. The pytest-shape guard is applied before any claim is added,
    not just for unassociated-command records.

    Before the fix the parser would emit a claim for the
    ``python scripts/bridge_report_test_claim_rerun_verifier.py ...`` block
    if the next/same block contained a summary-shaped line, then
    ``run_pytest_claim`` would reject it as ERROR, polluting the verdict.
    """
    markdown = (
        "## Live re-run\n"
        "\n"
        "```text\n"
        "python scripts/bridge_report_test_claim_rerun_verifier.py --bridge-id demo --json\n"
        "9 passed\n"
        "```\n"
    )
    claims = verifier_module.extract_claims(markdown)
    assert claims == []


def test_extract_claims_non_pytest_command_with_split_block_summary_skipped(verifier_module):
    """Same NO-GO -009 closure for the cross-block lookahead path: a
    non-pytest command followed by a summary in the next block is still
    skipped. The guard applies uniformly to in-block and cross-block
    summary association.
    """
    markdown = "```text\npython -m ruff check scripts/foo.py\n```\n\nObserved result:\n\n```text\n5 passed\n```\n"
    claims = verifier_module.extract_claims(markdown)
    assert claims == []


def test_extract_claims_lookahead_stops_at_next_command(verifier_module):
    """Cross-block lookahead must not associate commandA with the result of
    commandB. When the immediately following block has its own command, the
    first command is recorded as unassociated.
    """
    markdown = (
        "```text\npython -m pytest tests/a_test.py\n```\n\n```text\npython -m pytest tests/b_test.py\n5 passed\n```\n"
    )
    claims = verifier_module.extract_claims(markdown)
    assert len(claims) == 2
    first = next(c for c in claims if "a_test" in c.command)
    second = next(c for c in claims if "b_test" in c.command)
    assert first.claimed_summary is None
    assert second.claimed_summary == "5 passed"


def test_extract_claims_returns_empty_for_no_pytest_blocks(verifier_module):
    """A report with no command-like blocks legitimately yields zero claims.

    This preserves the original empty-success path for reports that report
    something other than pytest evidence (e.g. documentation-only or
    config-only post-impl reports).
    """
    markdown = (
        "## Summary\n"
        "\n"
        "This report describes a documentation-only change. No tests were run.\n"
        "\n"
        "```text\n"
        "this is not a command\n"
        "this is not a summary\n"
        "```\n"
    )
    claims = verifier_module.extract_claims(markdown)
    assert claims == []


# ---------------------------------------------------------------------------
# run_pytest_claim short-circuit on None summary
# ---------------------------------------------------------------------------


def test_run_pytest_claim_status_error_on_none_summary(verifier_module):
    """FINDING-P2-002: a claim with ``claimed_summary is None`` must short-circuit
    to ``ERROR`` without attempting to invoke pytest. Avoids accidentally
    running pytest with no claimed expectation and then reporting PASS.
    """
    claim = verifier_module.ExtractedClaim(
        claim_block_index=1,
        command="python -m pytest tests/foo_test.py",
        claimed_summary=None,
        claimed_counts={},
    )
    result = verifier_module.run_pytest_claim(_REPO_ROOT, claim, timeout_seconds=5)
    assert result.status == "ERROR"
    assert result.observed_summary is None
    assert "no associated observed-result block" in result.reason


def test_run_pytest_claim_rejects_non_pytest_command(verifier_module, tmp_path):
    """Non-pytest commands carrying a summary value are rejected at run-time.

    Preserves the pre-fix safety boundary: even if a non-pytest command was
    associated with a summary by some upstream parser, the verifier must not
    execute arbitrary python subprocess work.
    """
    claim = verifier_module.ExtractedClaim(
        claim_block_index=1,
        command="python scripts/something_else.py",
        claimed_summary="9 passed",
        claimed_counts={"passed": 9, "failed": 0, "errors": 0, "skipped": 0, "xfailed": 0, "xpassed": 0},
    )
    result = verifier_module.run_pytest_claim(_REPO_ROOT, claim, timeout_seconds=5)
    assert result.status == "ERROR"
    assert "not a python -m pytest" in result.reason or "not safely re-runnable" in result.reason


def test_validate_pytest_args_allows_in_root_basetemp(verifier_module):
    """NO-GO -009 FINDING-P1-001 closure: in-root path-valued options like
    ``--basetemp=.gtkb-state/...`` are accepted.

    The previous categorical PATH_OPTIONS rejection blocked the standard
    bridge-report pytest isolation pattern (basetemp inside the project's
    state directory). The fix validates the resolved path against the
    project root and rejects only when it escapes.
    """
    args_equals = ["--basetemp=.gtkb-state/pytest-tmp-demo", "tests/foo.py"]
    args_separate = ["--basetemp", ".gtkb-state/pytest-tmp-demo", "tests/foo.py"]
    assert verifier_module.validate_pytest_args(_REPO_ROOT, args_equals) is None
    assert verifier_module.validate_pytest_args(_REPO_ROOT, args_separate) is None


def test_validate_pytest_args_rejects_out_of_root_basetemp(verifier_module):
    """Companion to the in-root allowance: out-of-root path values for
    PATH_OPTIONS are still rejected.
    """
    args = ["--basetemp=/tmp/escape-basetemp", "tests/foo.py"]
    error = verifier_module.validate_pytest_args(_REPO_ROOT, args)
    assert error is not None
    assert "escapes project root" in error


def test_validate_pytest_args_path_options_require_value(verifier_module):
    """A PATH_OPTION without any value (e.g. trailing ``--basetemp`` at the
    end of the arg list) must be rejected as malformed; otherwise the
    option would silently slip through with no validation.
    """
    args = ["--basetemp"]
    error = verifier_module.validate_pytest_args(_REPO_ROOT, args)
    assert error is not None
    assert "requires a path value" in error


# ---------------------------------------------------------------------------
# build_packet status logic
# ---------------------------------------------------------------------------


def test_build_packet_fail_status_when_unassociated_command(verifier_module, tmp_path):
    """End-to-end: a report whose only pytest command lacks a summary must
    yield ``packet["status"] == "fail"`` so ``--strict`` exits non-zero.
    """
    report = "## Test Evidence\n\n```text\npython -m pytest tests/foo_test.py\n```\n"
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    report_path = bridge_dir / "demo-001.md"
    report_path.write_text(report, encoding="utf-8")
    # bridge/INDEX.md is required by resolve_report_path when --report-version
    # is omitted, but our test passes --report-version=1 so no INDEX needed.
    packet = verifier_module.build_packet(
        bridge_id="demo",
        project_root=tmp_path,
        report_version=1,
        timeout_seconds=5,
    )
    assert packet["status"] == "fail"
    assert packet["claim_count"] == 1
    claim = packet["claims"][0]
    assert claim["status"] == "ERROR"
    assert claim["claimed_summary"] is None
    assert "no associated observed-result block" in claim["reason"]


def test_format_markdown_handles_none_summary(verifier_module):
    """Markdown rendering must not emit the literal string ``None`` for a
    claim whose ``claimed_summary`` is absent.
    """
    packet = {
        "bridge_id": "demo",
        "report_file": "bridge/demo-001.md",
        "status": "fail",
        "claim_count": 1,
        "claims": [
            {
                "claim_block_index": 1,
                "command": "python -m pytest tests/foo_test.py",
                "claimed_summary": None,
                "observed_summary": None,
                "status": "ERROR",
                "returncode": None,
                "reason": "pytest command present, no associated observed-result block found",
                "claimed_counts": {},
                "observed_counts": {},
            }
        ],
    }
    markdown = verifier_module.format_markdown(packet)
    assert "None" not in markdown
    assert "no associated observed-result block" in markdown


# ---------------------------------------------------------------------------
# CLI surface (subprocess-level regression)
# ---------------------------------------------------------------------------


def _write_minimal_index(bridge_dir: Path, bridge_id: str, version: int) -> None:
    """Write a minimal bridge/INDEX.md exposing one NEW entry."""
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "INDEX.md").write_text(
        f"Document: {bridge_id}\nNEW: bridge/{bridge_id}-{version:03d}.md\n",
        encoding="utf-8",
    )


def test_cli_json_output_schema(tmp_path):
    """CLI ``--json`` output carries the documented top-level keys.

    Uses an out-of-root pytest target so the safety boundary rejects the
    claim fast (no real pytest subprocess) — the test asserts the JSON
    schema, not the verifier verdict.
    """
    bridge_dir = tmp_path / "bridge"
    bridge_id = "cli-demo"
    _write_minimal_index(bridge_dir, bridge_id, 1)
    (bridge_dir / f"{bridge_id}-001.md").write_text(
        "## Test Evidence\n\n```text\npython -m pytest /etc/passwd\n1 passed\n```\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT_PATH),
            "--bridge-id",
            bridge_id,
            "--report-version",
            "1",
            "--project-root",
            str(tmp_path),
            "--json",
            "--timeout-seconds",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    for key in ("bridge_id", "report_file", "claim_count", "status", "claims", "markdown"):
        assert key in payload, f"Missing key {key} in {payload!r}"


def test_cli_strict_exit_nonzero_on_unassociated_command(tmp_path):
    """``--strict`` must exit non-zero when the packet status is not 'pass'."""
    bridge_dir = tmp_path / "bridge"
    bridge_id = "cli-demo-strict"
    _write_minimal_index(bridge_dir, bridge_id, 1)
    (bridge_dir / f"{bridge_id}-001.md").write_text(
        "## Test Evidence\n\n```text\npython -m pytest tests/foo.py\n```\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT_PATH),
            "--bridge-id",
            bridge_id,
            "--report-version",
            "1",
            "--project-root",
            str(tmp_path),
            "--json",
            "--strict",
            "--timeout-seconds",
            "5",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "fail"
