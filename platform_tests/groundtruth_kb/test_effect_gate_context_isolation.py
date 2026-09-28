"""The shared effect gate keeps each agent context to its own scratch and checkout (c118).

Owner decision after the 2026-09-27 M13 host I finding ("Fix first: c118"): a review context searched the whole
scratchpad and listed seven other contexts' runtime homes, the implementer's included, and c117's gate allowed it
because it bounded edits and credential material only. Now a call naming another context's
scratchpad/<session context> or .worktrees/<session context> is refused foreign_context_material, and a shell recursion
rooted at or above the shared scratchpad or .worktrees roots is refused context_traversal, which also keeps a root-level
recursive search away from Git-ignored credential files. Round 2 (observer B127, B128): PowerShell's -r and -re,
commands nested in PowerShell groups, and the read-only Git forms that read Git-ignored files count as traversal too;
git grep, git ls-files, git cat-file and git --version otherwise pass as read-only Git.
The binding lookup is replaced by a fixed answer in these cases; the registered hook script case runs the real gate for
a traversal, which is decided without an authority.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

ROOT = Path(__file__).resolve().parents[2]
OWN = "SENV-86526f577a72494991107571b7ae0e70"
OTHER = "SENV-dd6eda7b2ab4410f822ed5de5db7b605"


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project root with this context bound as OWN; no authority is contacted."""
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, project: (OWN, True))
    return tmp_path


def _decision(project: Path, tool: str, tool_input: dict, *, cwd: Path | None = None) -> dict:
    return effect_gate.gate_decision(
        {
            "tool_name": tool,
            "tool_input": tool_input,
            "session_id": "ctx-isolation-test",
            "cwd": str(cwd or project),
            "project_root": str(project),
        }
    )


FOREIGN = [
    ("Read", {"file_path": f"scratchpad/{OTHER}/ready-v3.md"}),
    ("Read", {"file_path": f".worktrees/{OTHER}/m13-sentinel/sentinel.txt"}),
    ("Write", {"file_path": f"scratchpad/{OTHER}/note.md", "content": "x"}),
    ("Edit", {"file_path": f".worktrees/{OTHER}/code.py", "old_string": "a", "new_string": "b"}),
    ("Grep", {"pattern": "verified_artifacts", "path": f"scratchpad/{OTHER}"}),
    ("Glob", {"pattern": f".worktrees/{OTHER}/**/*.py"}),
    ("view_file", {"AbsolutePath": f"scratchpad/{OTHER}/deepseek-sdk/session.jsonl"}),
    # M13 host I, Q6 continuation (07:35): a listing of another context's runtime home, verbatim but for the id.
    (
        "Bash",
        {
            "command": f"Get-ChildItem .\\scratchpad\\{OTHER}\\deepseek-sdk -Recurse -File | Select-Object FullName,Length"
        },
    ),
    ("Bash", {"command": f"Get-Content scratchpad\\{OTHER}\\ready-v3.md"}),
    # A wildcard child reaches every context, this one's included.
    ("Bash", {"command": "Select-String -Path .\\scratchpad\\*\\*.jsonl -Pattern verified_artifacts"}),
]


@pytest.mark.parametrize(("tool", "tool_input"), FOREIGN)
def test_another_contexts_scratch_or_checkout_is_refused_for_every_tool(project, tool, tool_input):
    decision = _decision(project, tool, tool_input)
    assert decision.get("reason_code") == "foreign_context_material", decision
    assert "its own scratch and checkout" in decision["reason"]


def test_a_patch_into_another_contexts_checkout_is_refused(project):
    patch = f"*** Begin Patch\n*** Update File: .worktrees/{OTHER}/code.py\n@@\n-a\n+b\n*** End Patch\n"
    assert _decision(project, "apply_patch", {"input": patch})["reason_code"] == "foreign_context_material"


OWN_OR_SHARED = [
    ("Read", {"file_path": f"scratchpad/{OWN}/verified-v4.txt"}),
    ("Read", {"file_path": f".worktrees/{OWN}/m13-sentinel/sentinel.txt"}),
    ("Grep", {"pattern": "x", "path": f"scratchpad/{OWN}"}),
    ("Bash", {"command": f"Get-ChildItem .\\scratchpad\\{OWN} -Recurse -File"}),
    ("Read", {"file_path": ".worktrees/projects/PROJECT-X/m13-sentinel/sentinel.txt"}),
    # A loose entry under the shared root belongs to no context.
    ("Read", {"file_path": "scratchpad/draft.md"}),
    ("Bash", {"command": "Get-ChildItem scratchpad -Force | Select-Object Name"}),
    ("Read", {"file_path": "README.md"}),
]


@pytest.mark.parametrize(("tool", "tool_input"), OWN_OR_SHARED)
def test_own_scratch_and_checkout_and_the_shared_project_checkouts_pass(project, tool, tool_input):
    decision = _decision(project, tool, tool_input)
    assert decision.get("reason_code") not in {"foreign_context_material", "context_traversal"}, decision


def test_the_own_context_is_recognized_from_inside_its_checkout(project, monkeypatch):
    """A context working in its own checkout, whose payload names no project root, still resolves the project that
    owns the shared roots."""
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    inside = project / ".worktrees" / OWN

    def decide(tool_input: dict) -> dict:
        return effect_gate.gate_decision(
            {"tool_name": "Read", "tool_input": tool_input, "session_id": "ctx-isolation-test", "cwd": str(inside)}
        )

    assert decide({"file_path": "m13-sentinel/sentinel.txt"}) == {}
    assert decide({"file_path": f"../{OTHER}/code.py"})["reason_code"] == "foreign_context_material"


def test_an_unbound_context_owns_no_scratch_or_checkout(project, monkeypatch):
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, project: (None, True))
    decision = _decision(project, "Read", {"file_path": f"scratchpad/{OWN}/verified-v4.txt"})
    assert decision["reason_code"] == "foreign_context_material"
    assert _decision(project, "Read", {"file_path": "README.md"}) == {}


def test_an_unavailable_authority_refuses_only_scratch_and_checkout_paths(project, monkeypatch):
    looked_up = []

    def unavailable(payload, project):
        looked_up.append(payload)
        return None, False

    monkeypatch.setattr(effect_gate, "_bound_session_context", unavailable)
    decision = _decision(project, "Read", {"file_path": f"scratchpad/{OWN}/verified-v4.txt"})
    assert decision["reason_code"] == "context_isolation_unavailable"
    assert _decision(project, "Read", {"file_path": "README.md"}) == {}
    assert len(looked_up) == 1, "only a scratch or checkout path asks the authority"


TRAVERSALS = [
    # M13 host I, Q6 continuation and Q7, verbatim.
    "Get-ChildItem .\\scratchpad -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern "
    "'verified_artifacts' -List | Select-Object Path,LineNumber,Line | Format-Table -AutoSize",
    "Get-ChildItem . -Recurse -File -Include *.md,*.txt,*.jsonl -ErrorAction SilentlyContinue | Select-String "
    "-Pattern 'target_paths:' -List | Select-Object -First 20 Path | Format-Table -AutoSize -Wrap",
    "Get-ChildItem -Recurse -Depth 2 scratchpad | Select-Object FullName,Length | Format-Table -AutoSize",
    "Get-ChildItem -Recurse -File -Path . -Include *.json,*.md,*.py | Select-String -Pattern 'spec record' -List",
    # The c117 gap: a root-level recursive search reads Git-ignored credential files without naming them.
    "Get-ChildItem . -Recurse | Select-String password",
    "gci -rec -file | sls secret",
    "dir /s",
    "cmd /c dir /s /b",
    "ls -R",
    "grep -rn verified_artifacts .",
    "find . -name '*.jsonl'",
    "tree",
    "rg -uu verified_artifacts",
    "rg --no-ignore verified_artifacts .",
    "rg verified_artifacts scratchpad",
    "findstr /s /i verified_artifacts *.jsonl",
    'pwsh -Command "Get-ChildItem .worktrees -Recurse"',
    # Round 2, B128: Get-ChildItem binds -r and -re to -Recurse (PowerShell 7 and 5.1); in PowerShell ls is
    # Get-ChildItem, and a POSIX ls -r (reverse order) is refused at the shared roots too, which is fail-closed.
    "Get-ChildItem .\\scratchpad -r -File | Select-String verified_artifacts",
    "gci -re . | sls secret",
    "ls -r",
    'pwsh -Command "Get-ChildItem . -r"',
    # Round 2: a subexpression, grouping or script block runs its own command.
    "Select-String -Path (Get-ChildItem . -Recurse -File) -Pattern verified_artifacts",
    "$(Get-ChildItem .\\scratchpad -r) | Out-Null",
    "& { Get-ChildItem . -Recurse | Select-String secret }",
    "(Get-ChildItem . -r -File | Select-String secret).Count",
    # Round 2c: a root that is a variable or an expression can name any directory; Invoke-Expression runs its text.
    "$root = Get-Location; Get-ChildItem $root -Recurse",
    "Get-ChildItem . | ForEach-Object { Get-ChildItem $_ -r }",
    "Get-ChildItem (Get-Location) -Recurse",
    "grep -r -e secret $DIR",
    'Invoke-Expression "Get-ChildItem . -r"',
    "iex 'gci -recurse | sls secret'",
    'Write-Output "$(Get-ChildItem .worktrees -Recurse)"',
]


@pytest.mark.parametrize("command", TRAVERSALS)
def test_recursion_into_the_shared_scratch_and_checkout_roots_is_refused(project, command):
    decision = _decision(project, "Bash", {"command": command})
    assert decision.get("reason_code") == "context_traversal", decision
    assert "git grep" in decision["reason"]


def test_recursion_from_above_the_project_is_refused(project):
    decision = _decision(project, "Bash", {"command": "Get-ChildItem -Recurse -Filter *.md"}, cwd=project.parent)
    assert decision["reason_code"] == "context_traversal"


@pytest.mark.parametrize(
    ("tool", "tool_input"),
    [("Glob", {"pattern": "scratchpad/**/*.jsonl"}), ("Grep", {"pattern": "x", "path": ".worktrees"})],
)
def test_native_searches_of_the_shared_roots_are_refused(project, tool, tool_input):
    assert _decision(project, tool, tool_input)["reason_code"] == "context_traversal"


PASSING_SEARCHES = [
    (
        "Bash",
        {"command": "Get-ChildItem groundtruth-kb\\src -Recurse -Filter *.py | Select-String 'def scratch_teardown'"},
    ),
    ("Bash", {"command": "rg verified_artifacts"}),
    ("Bash", {"command": 'rg -n "hello" scripts/sample.py'}),
    ("Bash", {"command": "grep -rn dd scripts/"}),
    ("Bash", {"command": "git grep -n verified_artifacts"}),
    ("Bash", {"command": "git ls-files platform_tests"}),
    ("Bash", {"command": "Get-ChildItem groundtruth-kb\\src -r -Filter *.py"}),
    ("Bash", {"command": "Select-String -Path (Get-ChildItem docs -Recurse -File) -Pattern scratchpad"}),
    ("Bash", {"command": "Get-ChildItem . -Force"}),
    ("Bash", {"command": "Get-ChildItem $env:TEMP"}),
    ("Glob", {"pattern": "**/*.py"}),
    ("Grep", {"pattern": "scratchpad", "path": "docs"}),
]


@pytest.mark.parametrize(("tool", "tool_input"), PASSING_SEARCHES)
def test_searches_elsewhere_and_ignore_aware_searches_pass(project, tool, tool_input):
    assert _decision(project, tool, tool_input) == {}


READ_ONLY_GIT = [
    "git grep -n verified_artifacts -- platform_tests",
    # Round 2: the ignore-honouring forms stay read-only Git.
    "git grep --untracked -n verified_artifacts",
    "git grep --no-index --exclude-standard -n verified_artifacts",
    "git ls-files -o --exclude-standard",
    "git status --ignored=no",
    "git diff --no-index a.txt b.txt",
    "git cat-file -t 692dc252cde09a07747df7b6409bfab2affc1736",
    f"git -C .worktrees\\{OWN} cat-file -p 692dc252cde09a07747df7b6409bfab2affc1736 | Select-String appended",
    "git --version",
    # M13 host I, Q6 continuation: refused five times on c117, which left the agent believing Git was broken.
    "& 'C:\\Program Files\\Git\\cmd\\git.exe' --version 2>&1 | Out-String",
]


@pytest.mark.parametrize("command", READ_ONLY_GIT)
def test_read_only_git_reads_pass(project, command):
    assert _decision(project, "Bash", {"command": command}) == {}


@pytest.mark.parametrize(
    "command",
    ["git hash-object -w m13-sentinel/sentinel.txt", "git branch -D feature", "git config user.name someone"],
)
def test_git_forms_that_can_write_stay_refused(project, command):
    assert _decision(project, "Bash", {"command": command})["reason_code"] == "direct_git_effect_requires_lifecycle"


GIT_REACH = [
    # Round 2, B127: read-only Git judged by what it reads; each of these reads Git-ignored files, the shared roots
    # among them.
    "git grep --no-exclude-standard verified_artifacts",
    "git grep --untracked --no-exclude-standard verified_artifacts",
    "git grep --no-index verified_artifacts",
    "git ls-files -o",
    "git ls-files --others --directory",
    "git ls-files -oi --exclude-standard",
    "git ls-files --ignored --others --exclude-standard",
    "git status --ignored",
    "git status --ignored=matching --untracked-files=all",
    "git diff --no-index scratchpad empty",
    "git -C scratchpad grep --no-index -n verified_artifacts",
    "bash -c 'git grep --untracked --no-exclude-standard secret'",
]


@pytest.mark.parametrize("command", GIT_REACH)
def test_git_read_only_forms_that_can_reach_stay_refused(project, command):
    decision = _decision(project, "Bash", {"command": command})
    assert decision.get("reason_code") == "context_traversal", decision
    assert "--exclude-standard" in decision["reason"]


def _hook(payload: dict, cwd: Path) -> dict:
    done = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "implementation_start_gate.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        cwd=cwd,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def test_the_registered_hook_script_refuses_a_traversal_natively_and_allows_a_subtree_search(tmp_path):
    """The script every host registers emits the host-facing deny for a recursion from the project root."""
    base = {
        "cwd": str(tmp_path),
        "project_root": str(tmp_path),
        "session_id": "ctx-isolation-test",
        "tool_name": "Bash",
    }
    denied = _hook({**base, "tool_input": {"command": "Get-ChildItem . -Recurse | Select-String password"}}, tmp_path)
    assert denied["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "other contexts' scratch" in denied["hookSpecificOutput"]["permissionDecisionReason"]
    allowed = _hook({**base, "tool_input": {"command": "Get-ChildItem docs -Recurse -Filter *.md"}}, tmp_path)
    assert allowed == {}
