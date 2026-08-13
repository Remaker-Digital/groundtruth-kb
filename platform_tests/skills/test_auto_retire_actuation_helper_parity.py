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

HELPER_ROUTES: dict[str, Path] = {
    "claude": REPO_ROOT / ".claude" / "skills" / "gtkb-verify" / "helpers" / "write_verdict.py",
    "codex": REPO_ROOT / ".codex" / "skills" / "gtkb-verify" / "helpers" / "write_verdict.py",
    # Cursor's managed skill invokes the Codex helper; its local copied helper
    # is not the registered execution route.
    "cursor": REPO_ROOT / ".codex" / "skills" / "gtkb-verify" / "helpers" / "write_verdict.py",
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
    _git(repo, "config", "core.autocrlf", "false")
    _write(repo / "groundtruth.toml", "# test project root marker\n")
    _write(repo / "bridge" / "parity-fixture-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "parity-fixture-002.md", "GO\n\n# GO\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 1\n")
    _git(
        repo,
        "add",
        "--",
        "groundtruth.toml",
        "bridge/parity-fixture-001.md",
        "bridge/parity-fixture-002.md",
        "scripts/feature.py",
    )
    _git(repo, "commit", "-m", "chore: seed bridge thread")
    _write(
        repo / "bridge" / "parity-fixture-003.md",
        "NEW\n"
        "author_identity: prime-builder/test\n"
        "author_harness_id: T\n"
        "author_session_context_id: 11111111-1111-4111-8111-111111111111\n"
        "\n# Implementation report\n",
    )
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")
    return repo


_THIS_TEST = "platform_tests/skills/test_auto_retire_actuation_helper_parity.py"


def _verified_body() -> str:
    return f"""VERIFIED
author_identity: loyal-opposition/test
author_harness_id: T
author_session_context_id: 22222222-2222-4222-8222-222222222222
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

bridge_kind: lo_verdict
Document: parity-fixture
Version: 004
Responds to: bridge/parity-fixture-003.md
Recommended commit type: test

## Applicability Preflight

- packet_hash: sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
- candidate_evidence_hash: `<CANDIDATE_EVIDENCE_HASH>`
- missing_required_specs: []

## Prior Deliberations

_No prior deliberations: parity fixture._

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | `pytest {_THIS_TEST}` | yes | PASS |

## Positive Confirmations

- Parity fixture only.

## Commands Executed

- `pytest platform_tests/skills/test_auto_retire_actuation_helper_parity.py -q`
"""


def _mock_bridge_publication(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep these unit cases focused on finalizer commit/actuation behavior."""
    from scripts import gtkb_bridge_writer

    def _write_candidate(
        slug: str,
        version: int,
        body: str,
        project_root: Path,
        **_kwargs: object,
    ) -> Path:
        path = project_root / "bridge" / f"{slug}-{version:03d}.md"
        _write(path, body)
        return path

    monkeypatch.setattr(gtkb_bridge_writer, "write_bridge_file", _write_candidate)
    monkeypatch.setattr(gtkb_bridge_writer, "finalize_pending_bridge_publication", lambda *_args: None)
    monkeypatch.setattr(gtkb_bridge_writer, "rollback_pending_bridge_publication", lambda *_args, **_kwargs: None)


def _seed_retirable_project(project_root: Path) -> None:
    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.insert_project("Parity Project", "test", "seed", id="PROJECT-PARITY", status="active")
        db.insert_work_item("WI-1001", "Member one", "new", "backlog", "verified", "test", "seed")
        db.link_project_work_item("PROJECT-PARITY", "WI-1001", "test", "seed")
        bridge = project_root / "bridge"
        bridge.mkdir(parents=True, exist_ok=True)
        (bridge / "parity-project-001.md").write_text("VERIFIED\n\nWork Item: WI-1001\n", encoding="utf-8")
        db.add_project_artifact_link(
            "PROJECT-PARITY",
            "bridge_thread",
            "parity-project",
            "test",
            "seed verified bridge evidence",
            relationship="implements",
        )
    finally:
        db.close()


@pytest.mark.parametrize("harness_name", list(HELPER_ROUTES))
def test_each_helper_copy_defines_auto_retire_actuation(harness_name: str) -> None:
    helper = _load_helper(HELPER_ROUTES[harness_name], f"write_verdict_parity_define_{harness_name}")
    actuation = getattr(helper, "_auto_retire_completed_projects_after_verified", None)
    assert callable(actuation), f"{harness_name} helper missing auto-retire actuation"


@pytest.mark.parametrize("harness_name", list(HELPER_ROUTES))
def test_each_finalize_invokes_auto_retire_after_commit(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper(HELPER_ROUTES[harness_name], f"write_verdict_parity_finalize_{harness_name}")
    repo = _init_verified_repo(tmp_path)
    calls: list[Path] = []
    _mock_bridge_publication(monkeypatch)

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


@pytest.mark.parametrize("harness_name", list(HELPER_ROUTES))
def test_each_finalize_honors_explicit_auto_retire_suppression(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper(HELPER_ROUTES[harness_name], f"write_verdict_parity_suppress_{harness_name}")
    repo = _init_verified_repo(tmp_path)
    calls: list[Path] = []
    _mock_bridge_publication(monkeypatch)

    def _spy(project_root: Path) -> tuple[str, ...]:
        calls.append(project_root)
        return ()

    monkeypatch.setattr(helper, "_auto_retire_completed_projects_after_verified", _spy)

    result = helper.finalize_verified_commit(
        "parity-fixture",
        _verified_body(),
        include_paths=["bridge/parity-fixture-003.md", "scripts/feature.py"],
        commit_message="test(gtkb): parity suppressed finalize fixture",
        project_root=repo,
        auto_retire_completed_projects=False,
        pre_populate=False,
    )

    assert calls == []
    assert result.verdict_path == "bridge/parity-fixture-004.md"
    committed = set(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines())
    assert committed == {
        "bridge/parity-fixture-003.md",
        "bridge/parity-fixture-004.md",
        "scripts/feature.py",
    }


@pytest.mark.parametrize("harness_name", list(HELPER_ROUTES))
def test_each_cli_forwards_explicit_auto_retire_election(
    harness_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper(HELPER_ROUTES[harness_name], f"write_verdict_parity_cli_{harness_name}")
    body_path = tmp_path / f"{harness_name}-body.md"
    _write(body_path, _verified_body())
    observed: list[bool] = []

    def _fake_finalize(slug: str, body: str, **kwargs: object):
        assert slug == "parity-fixture"
        assert body.startswith("VERIFIED")
        observed.append(bool(kwargs["auto_retire_completed_projects"]))
        return helper.VerifiedFinalizationResult(
            commit_sha="fixture-sha",
            verdict_path="bridge/parity-fixture-004.md",
            committed_paths=("scripts/feature.py", "bridge/parity-fixture-004.md"),
        )

    monkeypatch.setattr(helper, "finalize_verified_commit", _fake_finalize)
    base_args = [
        "--slug",
        "parity-fixture",
        "--body-file",
        str(body_path),
        "--finalize-verified",
        "--include",
        "scripts/feature.py",
        "--commit-message",
        "test(gtkb): cli forwarding fixture",
        "--project-root",
        str(tmp_path),
        "--no-prepopulate",
        "--no-semantic-search",
    ]

    assert helper.main(base_args) == 0
    assert helper.main([*base_args, "--no-auto-retire"]) == 0
    assert observed == [True, False]


def test_pointer_harnesses_resolve_to_live_helper_routes() -> None:
    cursor_skill = (REPO_ROOT / ".cursor" / "skills" / "gtkb-verify" / "SKILL.md").read_text(encoding="utf-8")
    antigravity_skill = (REPO_ROOT / ".agent" / "skills" / "gtkb-verify" / "SKILL.md").read_text(encoding="utf-8")
    goose_skill = (REPO_ROOT / ".goose" / "skills" / "gtkb-verify" / "SKILL.md").read_text(encoding="utf-8")
    claude_skill = (REPO_ROOT / ".claude" / "skills" / "gtkb-verify" / "SKILL.md").read_text(encoding="utf-8")

    assert ".codex/skills/gtkb-verify/helpers/write_verdict.py" in cursor_skill
    assert ".claude/skills/gtkb-verify/helpers/write_verdict.py" in antigravity_skill
    assert "Canonical source: `.claude/skills/gtkb-verify/SKILL.md`" in goose_skill
    assert ".claude/skills/gtkb-verify/helpers/write_verdict.py" in claude_skill


def test_auto_retire_actuation_behaviour_is_equivalent_across_copies(tmp_path: Path) -> None:
    results: dict[str, tuple[str, ...]] = {}
    for harness_name, path in HELPER_ROUTES.items():
        project_root = tmp_path / harness_name
        project_root.mkdir()
        _seed_retirable_project(project_root)
        helper = _load_helper(path, f"write_verdict_parity_behaviour_{harness_name}")
        results[harness_name] = helper._auto_retire_completed_projects_after_verified(project_root)

    assert len(set(results.values())) == 1, f"auto-retire behaviour diverged across copies: {results}"
    assert results["claude"] == ("PROJECT-PARITY",)
