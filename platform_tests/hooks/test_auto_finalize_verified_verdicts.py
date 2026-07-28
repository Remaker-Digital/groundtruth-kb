"""WI-4889: tests for the auto-finalization sweep (scripts/auto_finalize_sweep.py).

Exercises the eligibility gates (independence + impl-already-committed), the
isolated-index verdict-file-only commit, idempotency, the cheap no-op gate, and
cross-harness registration parity. Uses a temporary git repo so the sweep's git
operations run in isolation (no real pre-commit hooks fire there).
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import auto_finalize_sweep as sweep_mod  # noqa: E402


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Sweep Test")
    _git(repo, "config", "commit.gpgsign", "false")
    # Committed implementation file so target_paths can be "clean".
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "foo.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "bridge").mkdir(parents=True, exist_ok=True)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")


_REPORT = """NEW

bridge_kind: implementation_report
Document: {slug}
Version: 001
Responds to: bridge/{slug}-002.md

author_identity: prime-builder/claude
author_session_context_id: {report_session}

target_paths: ["src/foo.py"]

## Summary
report body
"""

_VERDICT = """VERIFIED
author_identity: loyal-opposition/cursor
author_session_context_id: {verdict_session}

bridge_kind: implementation_verification
Document: {slug}
Version: 002
Responds to: bridge/{slug}-001.md
Recommended commit type: chore

## Verdict
VERIFIED.

## Spec-to-Test Mapping

| Spec | Verification | Executed | Result |
| --- | --- | --- | --- |
| GOV-WORK-TREE-HYGIENE-001 | python -m pytest tests/test_{slug}.py -q | yes | passed |

## Commands Executed

- `python -m pytest tests/test_{slug}.py -q` -> passed

## Commit Finalization Evidence

Same-transaction path set:

- `bridge/{slug}-001.md`
- `bridge/{slug}-002.md`
"""

_INVALID_VERDICT = """VERIFIED
author_identity: loyal-opposition/cursor
author_session_context_id: {verdict_session}

bridge_kind: implementation_verification
Document: {slug}
Version: 002
Responds to: bridge/{slug}-001.md

## Verdict
VERIFIED.
"""

_VALID_BODY_WITHOUT_FINALIZATION_EVIDENCE = """VERIFIED
author_identity: loyal-opposition/cursor
author_session_context_id: {verdict_session}

bridge_kind: implementation_verification
Document: {slug}
Version: 002
Responds to: bridge/{slug}-001.md
Recommended commit type: chore

## Verdict
VERIFIED.

## Spec-to-Test Mapping

| Spec | Verification | Executed | Result |
| --- | --- | --- | --- |
| GOV-WORK-TREE-HYGIENE-001 | python -m pytest tests/test_{slug}.py -q | yes | passed |

## Commands Executed

- `python -m pytest tests/test_{slug}.py -q` -> passed
"""


def _write_thread(
    repo: Path,
    slug: str,
    *,
    report_session: str = "pb-sess-1",
    verdict_session: str = "lo-sess-2",
    target_paths_json: str | None = None,
    verdict_template: str = _VERDICT,
) -> None:
    report = _REPORT.format(slug=slug, report_session=report_session)
    if target_paths_json is not None:
        report = report.replace('target_paths: ["src/foo.py"]', f"target_paths: {target_paths_json}")
    (repo / "bridge" / f"{slug}-001.md").write_text(report, encoding="utf-8")
    (repo / "bridge" / f"{slug}-002.md").write_text(
        verdict_template.format(slug=slug, verdict_session=verdict_session), encoding="utf-8"
    )


@pytest.fixture
def repo(tmp_path, monkeypatch):
    r = tmp_path / "repo"
    r.mkdir()
    _init_repo(r)
    monkeypatch.setattr(sweep_mod, "PROJECT_ROOT", r)
    monkeypatch.setattr(sweep_mod, "AUDIT_DIR", r / ".gtkb-state" / "auto-finalize-sweep")
    monkeypatch.setattr(sweep_mod, "AUDIT_LOG", r / ".gtkb-state" / "auto-finalize-sweep" / "sweep.jsonl")
    return r


def _head_files(repo: Path) -> set[str]:
    out = _git(repo, "show", "--name-only", "--format=", "HEAD").stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def test_canonical_verified_validator_import_root_is_live() -> None:
    expected = _REPO_ROOT / ".claude" / "skills" / "gtkb-verify" / "helpers"
    assert expected == sweep_mod._VERIFY_HELPERS

    validator = importlib.import_module("write_verdict")
    assert Path(validator.__file__).resolve() == (expected / "write_verdict.py").resolve()
    assert callable(validator.validate_verified_body)


def test_sweep_finalizes_eligible_verdict(repo):
    _write_thread(repo, "thread-a")
    result = sweep_mod.sweep()
    assert len(result["finalized"]) == 1, result
    assert result["skipped"] == []
    # Both chain files committed; nothing left untracked.
    assert _git(repo, "ls-files", "--others", "--exclude-standard", "bridge").stdout.strip() == ""
    committed = _head_files(repo)
    assert "bridge/thread-a-001.md" in committed
    assert "bridge/thread-a-002.md" in committed
    # Verdict-file-only: src/foo.py is NOT part of the sweep commit.
    assert "src/foo.py" not in committed


def test_sweep_skips_self_review_verdict(repo):
    # Same session for report and verdict -> self-review -> skip.
    _write_thread(repo, "thread-b", report_session="same-sess", verdict_session="same-sess")
    result = sweep_mod.sweep()
    assert result["finalized"] == []
    assert len(result["skipped"]) == 1
    assert "self-review" in result["skipped"][0]["reason"]
    # Verdict remains untracked.
    assert "bridge/thread-b-002.md" in _git(repo, "ls-files", "--others", "bridge").stdout


def test_sweep_skips_when_impl_uncommitted(repo):
    # target_paths points at a path that is not committed -> skip.
    _write_thread(repo, "thread-c", target_paths_json='["src/uncommitted.py"]')
    (repo / "src" / "uncommitted.py").write_text("y = 2\n", encoding="utf-8")  # untracked
    result = sweep_mod.sweep()
    assert result["finalized"] == []
    assert len(result["skipped"]) == 1
    assert "not committed" in result["skipped"][0]["reason"]


def test_sweep_skips_invalid_verdict_before_commit(repo, monkeypatch):
    _write_thread(repo, "thread-invalid", verdict_template=_INVALID_VERDICT)
    monkeypatch.setattr(sweep_mod, "_commit_chain", lambda *args, **kwargs: pytest.fail("commit should not run"))

    result = sweep_mod.sweep()

    assert result["finalized"] == []
    assert len(result["skipped"]) == 1
    assert "canonical_finalizer_rejects_verdict_body" in result["skipped"][0]["reason"]


def test_sweep_skips_checker_rejected_verdict_before_commit(repo, monkeypatch):
    _write_thread(
        repo,
        "thread-no-finalization-evidence",
        verdict_template=_VALID_BODY_WITHOUT_FINALIZATION_EVIDENCE,
    )
    monkeypatch.setattr(sweep_mod, "_commit_chain", lambda *args, **kwargs: pytest.fail("commit should not run"))

    result = sweep_mod.sweep()

    assert result["finalized"] == []
    assert len(result["skipped"]) == 1
    assert "protected_commit_authorization_rejects_terminal_verdict" in result["skipped"][0]["reason"]


def test_sweep_noops_when_no_untracked_verdicts(repo):
    result = sweep_mod.sweep()
    assert result == {"finalized": [], "skipped": [], "errors": []}


def test_sweep_does_not_call_planner_before_cheap_gate(repo, monkeypatch):
    monkeypatch.setattr(
        sweep_mod,
        "_planner_report_only",
        lambda: pytest.fail("planner should not run when cheap gate finds no VERIFIED verdicts"),
    )

    result = sweep_mod.sweep()

    assert result == {"finalized": [], "skipped": [], "errors": []}


def test_sweep_consults_planner_after_cheap_gate(repo, monkeypatch):
    _write_thread(repo, "thread-planner")
    monkeypatch.setattr(
        sweep_mod,
        "_planner_report_only",
        lambda: {"status": "ok", "summary": {"dirty_paths": 2, "actuator_actions": {"safe_commit": 1}}},
    )

    result = sweep_mod.sweep(dry_run=True)

    assert result["planner"]["status"] == "ok"
    assert result["planner"]["summary"]["actuator_actions"]["safe_commit"] == 1
    assert len(result["finalized"]) == 1


def test_sweep_planner_error_is_fail_soft(repo, monkeypatch):
    _write_thread(repo, "thread-planner-error")

    def fail_planner() -> dict:
        raise RuntimeError("planner unavailable")

    monkeypatch.setattr(sweep_mod, "_planner_report_only", fail_planner)

    result = sweep_mod.sweep(dry_run=True)

    assert result["planner"]["status"] == "error"
    assert "planner unavailable" in result["planner"]["reason"]
    assert len(result["finalized"]) == 1


def test_sweep_idempotent(repo):
    _write_thread(repo, "thread-d")
    first = sweep_mod.sweep()
    assert len(first["finalized"]) == 1
    second = sweep_mod.sweep()
    assert second == {"finalized": [], "skipped": [], "errors": []}


def test_sweep_audit_log_written(repo):
    _write_thread(repo, "thread-e")
    sweep_mod.sweep()
    log = repo / ".gtkb-state" / "auto-finalize-sweep" / "sweep.jsonl"
    assert log.is_file()
    events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any(e.get("action") == "finalize" for e in events)


def test_git_timeout_returns_failed_completed_process(monkeypatch):
    monkeypatch.setattr(
        sweep_mod.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs.get("timeout"))
        ),
    )

    result = sweep_mod._git(["status"], timeout=1)

    assert result.returncode == 124
    assert "timed out after 1 seconds" in result.stderr


def test_sweep_registered_in_both_harness_surfaces():
    """Cross-harness parity: the shared script is a Stop hook in both surfaces."""
    claude = (_REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    codex = (_REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8")
    codex_batch = (_REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py").read_text(encoding="utf-8")
    assert "auto_finalize_sweep.py" in claude, "missing Claude .claude/settings.json registration"
    assert "--batch stop" in codex, "missing Codex Stop batch registration"
    assert "scripts/auto_finalize_sweep.py" in codex_batch, "missing Codex Stop batch auto-finalizer"
