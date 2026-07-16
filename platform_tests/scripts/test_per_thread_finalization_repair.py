"""Tests for the WI-5116 per-thread finalization repair planner."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import per_thread_finalization_repair as repair  # noqa: E402


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "repair-tests@example.invalid")
    _git(repo, "config", "user.name", "Repair Tests")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "tool.py").write_text("print('base')\n", encoding="utf-8")
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-q", "-m", "base").returncode == 0


def _write(repo: Path, rel_path: str, text: str) -> None:
    path = repo / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _proposal(slug: str, *, work_item: str = "WI-5116") -> str:
    return "\n".join(
        [
            "NEW",
            f"Document: {slug}",
            "bridge_kind: prime_proposal",
            f"Work Item: {work_item}",
            'target_paths: ["scripts/tool.py"]',
            "",
        ]
    )


def _go(slug: str) -> str:
    return f"GO\nDocument: {slug}\nResponds to: bridge/{slug}-001.md\n"


def _report(slug: str, *, target_paths: bool = True) -> str:
    lines = [
        "NEW",
        "bridge_kind: implementation_report",
        f"Document: {slug}",
        "Recommended commit type: fix",
    ]
    if target_paths:
        lines.append('target_paths: ["scripts/tool.py"]')
    return "\n".join(lines) + "\n"


def _verified(slug: str) -> str:
    return f"VERIFIED\nDocument: {slug}\nResponds to: bridge/{slug}-003.md\n"


def _commit_thread_through_report(
    repo: Path, slug: str, *, target_paths: bool = True, work_item: str = "WI-5116"
) -> None:
    _write(repo, f"bridge/{slug}-001.md", _proposal(slug, work_item=work_item))
    _write(repo, f"bridge/{slug}-002.md", _go(slug))
    _write(repo, f"bridge/{slug}-003.md", _report(slug, target_paths=target_paths))
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-q", "-m", f"{slug} report").returncode == 0


def _commit_thread_through_verified(repo: Path, slug: str, *, target_paths: bool = True) -> None:
    _commit_thread_through_report(repo, slug, target_paths=target_paths)
    _write(repo, f"bridge/{slug}-004.md", _verified(slug))
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-q", "-m", f"{slug} verified").returncode == 0


def _plan_by_slug(repo: Path, *, exclude_wis: list[str] | None = None) -> dict[str | None, dict]:
    plan = repair.build_repair_plan(repo, exclude_wis=exclude_wis)
    return {thread.get("thread_slug"): thread for thread in plan["threads"]}


def test_terminal_verified_clean_targets_is_candidate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    slug = "gtkb-wi5116-clean-finalization"
    _commit_thread_through_report(repo, slug)
    _write(repo, f"bridge/{slug}-004.md", _verified(slug))

    thread = _plan_by_slug(repo)[slug]

    assert thread["classification"] == "terminal_verified_repair_candidate"
    assert thread["stop"] is False
    assert thread["target_paths"] == ["scripts/tool.py"]
    assert "suggested_next_steps" in thread


def test_terminal_verified_dirty_targets_blocks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    slug = "gtkb-wi5116-dirty-finalization"
    _commit_thread_through_report(repo, slug)
    (repo / "scripts" / "tool.py").write_text("print('changed')\n", encoding="utf-8")
    _write(repo, f"bridge/{slug}-004.md", _verified(slug))

    thread = _plan_by_slug(repo)[slug]

    assert thread["classification"] == "terminal_verified_blocked_dirty_targets"
    assert thread["stop"] is True
    assert "scripts/tool.py" in thread["dirty_targets"]


def test_tracked_modified_terminal_verified_verdict_is_stop(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    slug = "gtkb-wi5116-modified-terminal-verdict"
    _commit_thread_through_verified(repo, slug)
    verdict = repo / "bridge" / f"{slug}-004.md"
    verdict.write_text(verdict.read_text(encoding="utf-8") + "\nChanged after review.\n", encoding="utf-8")

    thread = _plan_by_slug(repo)[slug]

    assert thread["classification"] == "mixed_provenance_stop"
    assert thread["stop"] is True
    assert thread["dirty_terminal_verdicts"] == [
        {
            "path": f"bridge/{slug}-004.md",
            "change_kind": "modified",
            "git_status": " M",
            "reason": (
                "tracked modified terminal verdict requires exact byte ownership and finalization evidence; "
                "terminal status alone does not authorize the changed artifact"
            ),
        }
    ]


def test_tracked_deleted_terminal_verified_verdict_is_stop(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    slug = "gtkb-wi5116-deleted-terminal-verdict"
    _commit_thread_through_verified(repo, slug)
    (repo / "bridge" / f"{slug}-004.md").unlink()

    thread = _plan_by_slug(repo)[slug]

    assert thread["classification"] == "mixed_provenance_stop"
    assert thread["stop"] is True
    assert thread["dirty_terminal_verdicts"] == [
        {
            "path": f"bridge/{slug}-004.md",
            "change_kind": "deleted",
            "git_status": " D",
            "reason": (
                "tracked deleted terminal verdict requires exact byte ownership and finalization evidence; "
                "terminal status alone does not authorize the changed artifact"
            ),
        }
    ]


def test_terminal_verified_missing_scope_blocks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    slug = "gtkb-wi5116-missing-scope"
    _commit_thread_through_report(repo, slug, target_paths=False)
    _write(repo, f"bridge/{slug}-004.md", _verified(slug))

    thread = _plan_by_slug(repo)[slug]

    assert thread["classification"] == "terminal_verified_blocked_missing_scope"
    assert thread["stop"] is True


def test_in_flight_bridge_chain_is_not_finalizable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    slug = "gtkb-wi5116-in-flight"
    _write(repo, f"bridge/{slug}-001.md", _proposal(slug))

    thread = _plan_by_slug(repo)[slug]

    assert thread["classification"] == "in_flight_bridge_chain"
    assert thread["latest_status"] == "NEW"
    assert thread["stop"] is True


def test_explicitly_excluded_work_item_is_not_processed(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    slug = "gtkb-wi5330-active-program"
    _commit_thread_through_report(repo, slug, work_item="WI-5330")
    _write(repo, f"bridge/{slug}-004.md", _verified(slug))

    thread = _plan_by_slug(repo, exclude_wis=["WI-5330"])[slug]

    assert thread["classification"] == "excluded_active_program"
    assert thread["stop"] is True


def test_shared_target_between_verified_threads_is_mixed_provenance_stop(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    first = "gtkb-wi5116-shared-a"
    second = "gtkb-wi5116-shared-b"
    _commit_thread_through_report(repo, first)
    _commit_thread_through_report(repo, second)
    _write(repo, f"bridge/{first}-004.md", _verified(first))
    _write(repo, f"bridge/{second}-004.md", _verified(second))

    by_slug = _plan_by_slug(repo)

    assert by_slug[first]["classification"] == "mixed_provenance_stop"
    assert by_slug[second]["classification"] == "mixed_provenance_stop"
    assert "scripts/tool.py" in by_slug[first]["conflicting_target_owners"]


def test_unattributed_non_bridge_dirty_paths_are_reported_as_stop(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    (repo / "scripts" / "unclaimed.py").write_text("print('new')\n", encoding="utf-8")

    mixed = _plan_by_slug(repo)[None]

    assert mixed["classification"] == "mixed_provenance_stop"
    assert mixed["path_count"] == 1
    assert mixed["paths"] == ["scripts/unclaimed.py"]


def test_plan_is_report_only_and_json_serializable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    before = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
    slug = "gtkb-wi5116-json"
    _write(repo, f"bridge/{slug}-001.md", _proposal(slug))

    plan = repair.build_repair_plan(repo)
    restored = json.loads(json.dumps(plan, sort_keys=True))
    after = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout

    assert restored["read_only"] is True
    assert restored["mutation_capabilities"] == []
    assert before != after
    assert after == _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
