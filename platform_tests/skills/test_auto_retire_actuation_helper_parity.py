"""Parity regression: auto-retire-on-VERIFIED actuation across verify-helper copies (WI-4750)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]

HELPER_COPIES: dict[str, Path] = {
    "claude": REPO_ROOT / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py",
    "codex": REPO_ROOT / ".codex" / "skills" / "verify" / "helpers" / "write_verdict.py",
    "cursor": REPO_ROOT / ".cursor" / "skills" / "verify" / "helpers" / "write_verdict.py",
}


def _load_helper(path: Path, module_name: str) -> ModuleType:
    src_root = str(REPO_ROOT / "groundtruth-kb" / "src")
    if src_root not in sys.path:
        sys.path.insert(0, src_root)
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _init_verified_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _write(
        repo / "bridge" / "parity-fixture-001.md",
        "NEW\nauthor_session_context_id: prime-session-parity\n\n# Proposal\n",
    )
    _write(repo / "bridge" / "parity-fixture-002.md", "GO\n\n# GO\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 1\n")
    _git(repo, "add", "--", "bridge/parity-fixture-001.md", "bridge/parity-fixture-002.md", "scripts/feature.py")
    _git(repo, "commit", "-m", "chore: seed bridge thread")
    _write(
        repo / "bridge" / "parity-fixture-003.md",
        "NEW\nauthor_session_context_id: prime-session-parity\n\n# Implementation report\n",
    )
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")
    return repo


def _verified_body() -> str:
    return """VERIFIED
author_identity: loyal-opposition/test
author_harness_id: T
author_session_context_id: test-session-parity
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

bridge_kind: verification_verdict
Document: parity-fixture
Version: 004
Recommended commit type: test

## Prior Deliberations

_No prior deliberations: parity fixture._

## Specifications Carried Forward

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | this parity fixture test | yes | PASS |

## Positive Confirmations

- Parity fixture only.

## Commands Executed

- `pytest platform_tests/skills/test_auto_retire_actuation_helper_parity.py -q`
"""


def _seed_retirable_project(project_root: Path) -> None:
    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.insert_project("Parity Project", "test", "seed", id="PROJECT-PARITY", status="active")
        db.insert_work_item("WI-P1", "Member one", "new", "backlog", "verified", "test", "seed")
        db.link_project_work_item("PROJECT-PARITY", "WI-P1", "test", "seed")
    finally:
        db.close()


@pytest.mark.parametrize("harness_name", list(HELPER_COPIES))
def test_each_helper_copy_defines_auto_retire_actuation(harness_name: str) -> None:
    helper = _load_helper(HELPER_COPIES[harness_name], f"write_verdict_parity_define_{harness_name}")
    actuation = getattr(helper, "_auto_retire_completed_projects_after_verified", None)
    assert callable(actuation), f"{harness_name} helper missing auto-retire actuation"


@pytest.mark.parametrize("harness_name", list(HELPER_COPIES))
def test_each_finalize_invokes_auto_retire_after_commit(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper(HELPER_COPIES[harness_name], f"write_verdict_parity_finalize_{harness_name}")
    repo = _init_verified_repo(tmp_path)
    calls: list[Path] = []

    def _spy(project_root: Path) -> tuple[str, ...]:
        calls.append(project_root)
        return ()

    monkeypatch.setattr(helper, "_auto_retire_completed_projects_after_verified", _spy)

    helper.finalize_verified_commit(
        "parity-fixture",
        _verified_body(),
        include_paths=["bridge/parity-fixture-003.md", "scripts/feature.py"],
        commit_message="test(gtkb): parity finalize fixture",
        project_root=repo,
        pre_populate=False,
    )

    assert calls == [repo.resolve()]


def test_auto_retire_actuation_behaviour_is_equivalent_across_copies(tmp_path: Path) -> None:
    results: dict[str, tuple[str, ...]] = {}
    for harness_name, path in HELPER_COPIES.items():
        project_root = tmp_path / harness_name
        project_root.mkdir()
        _seed_retirable_project(project_root)
        helper = _load_helper(path, f"write_verdict_parity_behaviour_{harness_name}")
        results[harness_name] = helper._auto_retire_completed_projects_after_verified(project_root)

    assert len(set(results.values())) == 1, f"auto-retire behaviour diverged across copies: {results}"
    assert results["claude"] == ("PROJECT-PARITY",)
