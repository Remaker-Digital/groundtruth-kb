"""Tests for the shared LO file-safety payload normalization layer.

Verifies equivalent mutation intent across Claude, Codex, Cursor, and
Antigravity harness payload shapes produces equivalent normalization results.

Specification: DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, TEST-11581.
"""

from __future__ import annotations

from scripts.lo_file_safety_payloads import (
    Harness,
    MutationClass,
    is_mutation_payload,
    normalize,
    normalize_antigravity,
    normalize_claude,
    normalize_codex,
    normalize_cursor,
    targets_include_live_carrier,
)

# --- Claude payloads ---


def test_claude_bash_git_restore_is_shell():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git restore groundtruth.db"}}
    n = normalize_claude(payload)
    assert n.mutation_class == MutationClass.SHELL
    assert n.harness == Harness.CLAUDE


def test_claude_bash_git_checkout_is_shell():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git checkout -- groundtruth.db"}}
    n = normalize_claude(payload)
    assert n.mutation_class == MutationClass.SHELL


def test_claude_bash_git_reset_is_shell():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git reset HEAD groundtruth.db"}}
    n = normalize_claude(payload)
    assert n.mutation_class == MutationClass.SHELL
    assert "groundtruth.db" in n.target_paths


def test_claude_bash_opaque_command_substitution():
    payload = {"tool_name": "Bash", "tool_input": {"command": "rm $(find . -name groundtruth.db)"}}
    n = normalize_claude(payload)
    assert n.mutation_class == MutationClass.OPAQUE
    assert n.is_opaque


def test_claude_bash_read_only():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git status"}}
    n = normalize_claude(payload)
    assert n.mutation_class == MutationClass.READ_ONLY


def test_claude_write():
    payload = {"tool_name": "Write", "tool_input": {"file_path": "bridge/test.md"}}
    n = normalize_claude(payload)
    assert n.mutation_class == MutationClass.WRITE
    assert "bridge/test.md" in n.target_paths


def test_claude_edit():
    payload = {"tool_name": "Edit", "tool_input": {"file_path": "src/main.py"}}
    n = normalize_claude(payload)
    assert n.mutation_class == MutationClass.EDIT


# --- Codex payloads ---


def test_codex_bash_git_reset_is_shell():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git reset --hard HEAD"}}
    n = normalize_codex(payload)
    assert n.mutation_class == MutationClass.SHELL
    assert n.harness == Harness.CODEX


def test_codex_bash_cmd_field():
    payload = {"tool_name": "Bash", "tool_input": {"cmd": "rm -rf groundtruth.db"}}
    n = normalize_codex(payload)
    assert n.mutation_class == MutationClass.SHELL


def test_codex_write():
    payload = {"tool_name": "Write", "tool_input": {"file_path": "test.py"}}
    n = normalize_codex(payload)
    assert n.mutation_class == MutationClass.WRITE


# --- Antigravity payloads ---


def test_antigravity_run_command():
    payload = {"tool_name": "run_command", "tool_input": {"command": "git reset groundtruth.db"}}
    n = normalize_antigravity(payload)
    assert n.mutation_class == MutationClass.SHELL
    assert n.harness == Harness.ANTIGRAVITY


def test_antigravity_write_to_file():
    payload = {"tool_name": "write_to_file", "tool_input": {"file_path": "test.txt", "content": "hello"}}
    n = normalize_antigravity(payload)
    assert n.mutation_class == MutationClass.WRITE
    assert "test.txt" in n.target_paths
    assert n.candidate_content == "hello"


def test_antigravity_replace_file_content():
    payload = {"tool_name": "replace_file_content", "tool_input": {"file_path": "test.py"}}
    n = normalize_antigravity(payload)
    assert n.mutation_class == MutationClass.EDIT


def test_antigravity_multi_replace():
    payload = {"tool_name": "multi_replace_file_content", "tool_input": {"file_path": "test.py"}}
    n = normalize_antigravity(payload)
    assert n.mutation_class == MutationClass.EDIT


def test_antigravity_read_only():
    payload = {"tool_name": "read_file", "tool_input": {"file_path": "test.py"}}
    n = normalize_antigravity(payload)
    assert n.mutation_class == MutationClass.READ_ONLY


# --- Cursor payloads ---


def test_cursor_shell():
    payload = {"tool_name": "Shell", "tool_input": {"command": "git restore groundtruth.db"}}
    n = normalize_cursor(payload)
    assert n.mutation_class == MutationClass.SHELL
    assert n.harness == Harness.CURSOR


def test_cursor_write():
    payload = {"tool_name": "Write", "tool_input": {"file_path": "test.py"}}
    n = normalize_cursor(payload)
    assert n.mutation_class == MutationClass.WRITE
    assert n.target_paths == ["test.py"]


def test_cursor_strreplace_is_edit():
    payload = {"tool_name": "StrReplace", "tool_input": {"file_path": "test.py"}}
    n = normalize_cursor(payload)
    assert n.mutation_class == MutationClass.EDIT


def test_cursor_delete_accepts_path():
    payload = {"toolName": "Delete", "toolInput": {"path": "gone.py"}}
    n = normalize_cursor(payload)
    assert n.mutation_class == MutationClass.DELETE
    assert n.target_paths == ["gone.py"]


def test_cursor_payload_level_path():
    payload = {"tool_name": "Write", "path": "root.py"}
    n = normalize_cursor(payload)
    assert n.mutation_class == MutationClass.WRITE
    assert n.target_paths == ["root.py"]


def test_cursor_bash():
    payload = {"tool_name": "Bash", "tool_input": {"command": "echo hello"}}
    n = normalize_cursor(payload)
    # echo is READ_ONLY
    assert n.mutation_class == MutationClass.READ_ONLY


# --- Auto-detect ---


def test_auto_detect_antigravity():
    payload = {"tool_name": "run_command", "tool_input": {"command": "ls"}}
    n = normalize(payload)
    assert n.harness == Harness.ANTIGRAVITY


def test_auto_detect_cursor():
    payload = {"tool_name": "Shell", "tool_input": {"command": "ls"}}
    n = normalize(payload)
    assert n.harness == Harness.CURSOR


def test_auto_detect_claude_default():
    payload = {"tool_name": "Bash", "tool_input": {"command": "ls"}}
    n = normalize(payload)
    assert n.harness == Harness.CLAUDE


# --- targets_include_live_carrier ---


def test_targets_include_live_carrier_exact():
    from scripts.lo_file_safety_payloads import NormalizedPayload

    n = NormalizedPayload(
        harness=Harness.CLAUDE,
        tool_name="Bash",
        mutation_class=MutationClass.SHELL,
        target_paths=["groundtruth.db"],
    )
    assert targets_include_live_carrier(n)


def test_targets_include_live_carrier_subpath():
    from scripts.lo_file_safety_payloads import NormalizedPayload

    n = NormalizedPayload(
        harness=Harness.CLAUDE,
        tool_name="Bash",
        mutation_class=MutationClass.SHELL,
        target_paths=["data/groundtruth.db"],
    )
    assert targets_include_live_carrier(n)


def test_targets_include_live_carrier_not_found():
    from scripts.lo_file_safety_payloads import NormalizedPayload

    n = NormalizedPayload(
        harness=Harness.CLAUDE,
        tool_name="Bash",
        mutation_class=MutationClass.SHELL,
        target_paths=["other.db"],
    )
    assert not targets_include_live_carrier(n)


# --- is_mutation_payload ---


def test_is_mutation_payload_shell():
    from scripts.lo_file_safety_payloads import NormalizedPayload

    n = NormalizedPayload(harness=Harness.CLAUDE, tool_name="Bash", mutation_class=MutationClass.SHELL)
    assert is_mutation_payload(n)


def test_is_mutation_payload_read_only():
    from scripts.lo_file_safety_payloads import NormalizedPayload

    n = NormalizedPayload(harness=Harness.CLAUDE, tool_name="Bash", mutation_class=MutationClass.READ_ONLY)
    assert not is_mutation_payload(n)


def test_is_mutation_payload_opaque():
    from scripts.lo_file_safety_payloads import NormalizedPayload

    n = NormalizedPayload(harness=Harness.CLAUDE, tool_name="Bash", mutation_class=MutationClass.OPAQUE)
    assert is_mutation_payload(n)


# --- Cross-harness parity: equivalent intent ---


def test_cross_harness_git_reset_parity():
    """git reset groundtruth.db must be recognized as SHELL across A/B/C/E."""
    payloads = {
        "claude": {"tool_name": "Bash", "tool_input": {"command": "git reset groundtruth.db"}},
        "codex": {"tool_name": "Bash", "tool_input": {"command": "git reset groundtruth.db"}},
        "antigravity": {"tool_name": "run_command", "tool_input": {"command": "git reset groundtruth.db"}},
        "cursor": {"tool_name": "Shell", "tool_input": {"command": "git reset groundtruth.db"}},
    }
    normalizers = {
        "claude": normalize_claude,
        "codex": normalize_codex,
        "antigravity": normalize_antigravity,
        "cursor": normalize_cursor,
    }
    results = {}
    for name, payload in payloads.items():
        n = normalizers[name](payload)
        results[name] = (n.mutation_class, n.is_opaque)
        assert n.mutation_class == MutationClass.SHELL, f"{name}: expected SHELL, got {n.mutation_class}"
        assert not n.is_opaque, f"{name}: expected not opaque"


def test_cross_harness_opaque_parity():
    """Opaque shell with write-ish command + command substitution must be OPAQUE."""
    payloads = {
        "claude": {"tool_name": "Bash", "tool_input": {"command": "rm $(find . -name '*.db')"}},
        "codex": {"tool_name": "Bash", "tool_input": {"command": "rm $(find . -name '*.db')"}},
        "antigravity": {"tool_name": "run_command", "tool_input": {"command": "rm $(find . -name '*.db')"}},
        "cursor": {"tool_name": "Shell", "tool_input": {"command": "rm $(find . -name '*.db')"}},
    }
    normalizers = {
        "claude": normalize_claude,
        "codex": normalize_codex,
        "antigravity": normalize_antigravity,
        "cursor": normalize_cursor,
    }
    for name, payload in payloads.items():
        n = normalizers[name](payload)
        assert n.mutation_class == MutationClass.OPAQUE, f"{name}: expected OPAQUE, got {n.mutation_class}"
        assert n.is_opaque, f"{name}: expected is_opaque=True"


def test_cross_harness_python_whole_file():
    """Python whole-file copy/move/delete must be detected as SHELL."""
    payloads = {
        "claude": {
            "tool_name": "Bash",
            "tool_input": {"command": "python -c \"import shutil; shutil.copy('groundtruth.db', 'backup.db')\""},
        },
        "codex": {
            "tool_name": "Bash",
            "tool_input": {"command": "python -c \"import shutil; shutil.copy('groundtruth.db', 'backup.db')\""},
        },
        "antigravity": {
            "tool_name": "run_command",
            "tool_input": {"command": "python -c \"import shutil; shutil.copy('groundtruth.db', 'backup.db')\""},
        },
        "cursor": {
            "tool_name": "Shell",
            "tool_input": {"command": "python -c \"import shutil; shutil.copy('groundtruth.db', 'backup.db')\""},
        },
    }
    normalizers = {
        "claude": normalize_claude,
        "codex": normalize_codex,
        "antigravity": normalize_antigravity,
        "cursor": normalize_cursor,
    }
    for name, payload in payloads.items():
        n = normalizers[name](payload)
        assert n.mutation_class == MutationClass.SHELL, (
            f"{name}: expected SHELL for Python whole-file, got {n.mutation_class}"
        )
