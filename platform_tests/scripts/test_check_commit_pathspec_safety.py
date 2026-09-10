"""Real-index work-product boundaries; reads preserve index and foreign bytes."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("normal_commit_paths", ROOT / "scripts/check_commit_pathspec_safety.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def git(root, *args, input=None, check=True):
    return subprocess.run(["git", "-C", str(root), *args], input=input, capture_output=True, check=check)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "core.autocrlf", "false")
    git(tmp_path, "config", "user.email", "test@invalid.example")
    git(tmp_path, "config", "user.name", "Test")
    return tmp_path


def stage(repo, name, content="product\n"):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    git(repo, "add", "--", name)


def inspect_unchanged(repo):
    index = (repo / ".git/index").read_bytes()
    foreign = repo / "unrelated.tmp"
    foreign.write_bytes(b"foreign\x00work")
    result = checker.inspect_staged(repo)
    assert (repo / ".git/index").read_bytes() == index
    assert foreign.read_bytes() == b"foreign\x00work"
    return result


@pytest.mark.parametrize(
    "name",
    ["src/module.py", ".harness-baseline-configuration/rules/topic.md", "docs/bracket[1].md", "docs/café note.md"],
)
def test_real_product_index_passes_without_permission_evidence(repo, name):
    stage(repo, name)
    result = inspect_unchanged(repo)
    assert result["status"] == "pass"
    assert result["product"] == [name]


@pytest.mark.parametrize(
    "name",
    [
        "bridge/item.md",
        "bridge/item.json",
        ".codex/hooks.json",
        "sub/.claude/settings.json",
        "AGENTS.md",
        ".groundtruth/inventory/public.json",
        ".groundtruth/formal-artifact-approvals/packet.md",
        "config/agent-control/registry.json",
        "scratchpad/context/note.md",
        ".gtkb-state/permission.json",
        "harness-state/registry.json",
        "groundtruth.db",
    ],
)
@pytest.mark.parametrize("with_source", [False, True])
def test_nonproduct_postimages_refuse_even_without_mixed_source(repo, name, with_source):
    stage(repo, name)
    if with_source:
        stage(repo, "src/product.txt")
    result = inspect_unchanged(repo)
    assert result["status"] == "fail"
    assert result["refused"] == [{"path": name, "reason": "not_work_product"}]


def test_forward_deletion_and_product_rename_remain_possible(repo):
    for name in ["bridge/old.md", ".codex/old.json", "src/old.txt"]:
        stage(repo, name)
    git(repo, "commit", "-qm", "preimage")
    git(repo, "rm", "--", "bridge/old.md", ".codex/old.json")
    git(repo, "mv", "src/old.txt", "src/new.txt")
    result = inspect_unchanged(repo)
    assert result["status"] == "pass"
    assert set(result["removals"]) == {"bridge/old.md", ".codex/old.json", "src/old.txt"}
    assert result["product"] == ["src/new.txt"]


def test_mode_only_product_change_is_inspected(repo):
    stage(repo, "run.sh", "exit 0\n")
    git(repo, "commit", "-qm", "preimage")
    git(repo, "update-index", "--chmod=+x", "run.sh")
    assert inspect_unchanged(repo)["product"] == ["run.sh"]


def test_case_only_rename_has_one_surviving_identity(repo):
    stage(repo, "old.txt")
    git(repo, "commit", "-qm", "preimage")
    git(repo, "mv", "old.txt", "temporary.txt")
    git(repo, "mv", "temporary.txt", "OLD.txt")
    assert inspect_unchanged(repo)["status"] == "pass"


@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_nonregular_index_modes_refuse(repo, mode):
    oid = git(repo, "hash-object", "-w", "--stdin", input=b"target").stdout.decode().strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{oid},link")
    result = inspect_unchanged(repo)
    assert result["refused"] == [{"path": "link", "reason": "unsupported_file_mode"}]


def test_colliding_postimage_identities_refuse(repo):
    oid = git(repo, "hash-object", "-w", "--stdin", input=b"product").stdout.decode().strip()
    git(repo, "-c", "core.ignorecase=false", "update-index", "--add", "--cacheinfo", f"100644,{oid},File.txt")
    git(repo, "-c", "core.ignorecase=false", "update-index", "--add", "--cacheinfo", f"100644,{oid},file.txt")
    with pytest.raises(checker.IndexCheckError, match="colliding"):
        checker.inspect_staged(repo)


def test_unmerged_index_refuses(repo):
    oid = git(repo, "hash-object", "-w", "--stdin", input=b"product").stdout.decode().strip()
    git(
        repo,
        "update-index",
        "--index-info",
        input=f"100644 {oid} 1\tconflict.txt\n100644 {oid} 2\tconflict.txt\n".encode(),
    )
    with pytest.raises(checker.IndexCheckError, match="unmerged"):
        checker.inspect_staged(repo)


def test_unavailable_index_is_nonzero_and_never_fail_open(repo, monkeypatch):
    tmp_path = repo
    invalid = repo / "bad-index"
    invalid.write_bytes(b"invalid index")
    monkeypatch.setenv("GIT_INDEX_FILE", str(invalid))
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_commit_pathspec_safety.py"), "--staged", "--json"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["error"].startswith("staged_index_unavailable")


def test_empty_index_passes(repo):
    assert checker.inspect_staged(repo) == {"status": "pass", "product": [], "removals": [], "refused": []}
