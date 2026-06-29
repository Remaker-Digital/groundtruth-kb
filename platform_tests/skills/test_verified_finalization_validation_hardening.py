"""Regression: fail-closed VERIFIED finalization validation hardening (WI-4773)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

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


def _verified_body_base(*, extra_sections: str = "") -> str:
    return f"""VERIFIED
author_identity: loyal-opposition/test
author_harness_id: T
author_session_context_id: test-session-validation-hardening
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

bridge_kind: verification_verdict
Document: validation-hardening-fixture
Version: 004
Recommended commit type: test

## Prior Deliberations

_No prior deliberations: validation hardening fixture._

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_validation_hardening.py` | yes | PASS |

## Positive Confirmations

- Validation hardening fixture only.

## Commands Executed

- `pytest platform_tests/skills/test_verified_finalization_validation_hardening.py -q`
{extra_sections}
"""


@pytest.fixture
def claude_helper() -> ModuleType:
    return _load_helper(HELPER_COPIES["claude"], "write_verdict_claude_hardening")


def test_validate_rejects_unresolved_placeholder(claude_helper: ModuleType) -> None:
    body = _verified_body_base(extra_sections="\nPLACEHOLDER_DELIBERATIONS\n")
    with pytest.raises(claude_helper.VerifiedFinalizationError, match="unresolved placeholder"):
        claude_helper.validate_verified_body(body, project_root=REPO_ROOT)


def test_validate_rejects_embedded_failed_preflight(claude_helper: ModuleType) -> None:
    body = _verified_body_base(
        extra_sections="""
## Applicability Preflight

- preflight_passed: false
- missing_required_specs: []
"""
    )
    with pytest.raises(claude_helper.VerifiedFinalizationError, match="failed preflight"):
        claude_helper.validate_verified_body(body, project_root=REPO_ROOT)

    body_specs = _verified_body_base(
        extra_sections="""
## Applicability Preflight

- preflight_passed: true
- missing_required_specs: [`GOV-MISSING`]
"""
    )
    with pytest.raises(claude_helper.VerifiedFinalizationError, match="missing_required_specs"):
        claude_helper.validate_verified_body(body_specs, project_root=REPO_ROOT)


def test_validate_rejects_out_of_root_scratch_in_evidence(claude_helper: ModuleType, tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()
    scratch = "E:/Claude-Playground/scratch/preflight.json"
    body = _verified_body_base(
        extra_sections=f"""
## Preflight Evidence

```
operative_file: {scratch}
```
"""
    )
    with pytest.raises(claude_helper.VerifiedFinalizationError, match="out-of-root path evidence"):
        claude_helper.validate_verified_body(body, project_root=project_root)


def test_validate_allows_prose_disclosure_span(claude_helper: ModuleType, tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()
    body = _verified_body_base(
        extra_sections="""
## Positive Confirmations

- Reviewed historical defect where operative_file was recorded as
  `E:/Claude-Playground/scratch/preflight.json` in prose only; embedded evidence
  blocks must stay in-root.
"""
    )
    claude_helper.validate_verified_body(body, project_root=project_root)


def _init_finalize_repo(tmp_path: Path, *, commit_predecessors: bool) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _write(repo / "bridge" / "chain-fixture-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "chain-fixture-002.md", "GO\n\n# GO\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 1\n")
    if commit_predecessors:
        _git(repo, "add", "--", "bridge/chain-fixture-001.md", "bridge/chain-fixture-002.md", "scripts/feature.py")
        _git(repo, "commit", "-m", "chore: seed bridge thread")
    _write(repo / "bridge" / "chain-fixture-003.md", "NEW\n\n# Implementation report\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")
    return repo


def test_finalize_fails_closed_on_untracked_predecessor_chain(claude_helper: ModuleType, tmp_path: Path) -> None:
    repo = _init_finalize_repo(tmp_path, commit_predecessors=False)
    helper = claude_helper
    body = _verified_body_base().replace("validation-hardening-fixture", "chain-fixture")
    with pytest.raises(helper.VerifiedFinalizationError, match="predecessor bridge chain"):
        helper.finalize_verified_commit(
            "chain-fixture",
            body,
            include_paths=["scripts/feature.py"],
            commit_message="test: verified hardening fixture",
            project_root=repo,
            pre_populate=False,
            db=False,
            log_path=False,
        )
    verdict = repo / "bridge" / "chain-fixture-004.md"
    assert not verdict.exists()
    log = _git(repo, "log", "--oneline", check=False)
    assert "seed bridge thread" not in (log.stdout or "")


def test_finalize_rejects_include_set_missing_report_claim(claude_helper: ModuleType, tmp_path: Path) -> None:
    repo = _init_finalize_repo(tmp_path, commit_predecessors=True)
    _write(repo / "scripts" / "omitted.py", "VALUE = 3\n")
    _write(
        repo / "bridge" / "chain-fixture-003.md",
        """NEW

# Implementation report

## Files Changed

- `scripts/feature.py`
- `scripts/omitted.py`
""",
    )
    body = _verified_body_base().replace("validation-hardening-fixture", "chain-fixture")

    with pytest.raises(claude_helper.VerifiedFinalizationError, match="omits path"):
        claude_helper.finalize_verified_commit(
            "chain-fixture",
            body,
            include_paths=["scripts/feature.py", "bridge/chain-fixture-003.md"],
            commit_message="test: verified hardening fixture",
            project_root=repo,
            pre_populate=False,
            db=False,
            log_path=False,
        )

    assert not (repo / "bridge" / "chain-fixture-004.md").exists()


def test_report_claim_include_check_allows_owner_by_reference_waiver(claude_helper: ModuleType, tmp_path: Path) -> None:
    repo = _init_finalize_repo(tmp_path, commit_predecessors=True)
    _write(
        repo / "bridge" / "chain-fixture-003.md",
        """NEW

# Implementation report

## Files Changed

- `scripts/feature.py`
- `scripts/omitted.py`

## By-Reference Finalization Waiver

Owner-approved by-reference waiver captured at `DELIB-TEST-BY-REFERENCE-WAIVER`.
""",
    )

    claude_helper._assert_include_set_covers_report_claims(
        slug="chain-fixture",
        project_root=repo,
        latest_report_rel_path="bridge/chain-fixture-003.md",
        include_paths=["scripts/feature.py", "bridge/chain-fixture-003.md"],
    )


@pytest.mark.parametrize("harness_name", list(HELPER_COPIES))
def test_three_helper_copies_share_validation_behavior(harness_name: str, tmp_path: Path) -> None:
    helper = _load_helper(HELPER_COPIES[harness_name], f"write_verdict_{harness_name}_hardening")
    project_root = tmp_path / "repo"
    project_root.mkdir()

    good = _verified_body_base()
    helper.validate_verified_body(good, project_root=project_root)

    bad_placeholder = _verified_body_base(extra_sections="\nPLACEHOLDER_DELIBERATIONS\n")
    with pytest.raises(helper.VerifiedFinalizationError, match="unresolved placeholder"):
        helper.validate_verified_body(bad_placeholder, project_root=project_root)

    bad_preflight = _verified_body_base(
        extra_sections="""
## Applicability Preflight

- preflight_passed: false
"""
    )
    with pytest.raises(helper.VerifiedFinalizationError, match="failed preflight"):
        helper.validate_verified_body(bad_preflight, project_root=project_root)

    bad_path = _verified_body_base(
        extra_sections="""
## Command Output

```
path: E:/outside/root/evidence.txt
```
"""
    )
    with pytest.raises(helper.VerifiedFinalizationError, match="out-of-root path evidence"):
        helper.validate_verified_body(bad_path, project_root=project_root)
