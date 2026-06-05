"""Tests for verb-aware _paths_from_shell per DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.

Acceptance assertions verbatim from the DCL constraint body:
- git commit with HEREDOC body that mentions protected paths returns []
- grep -E with protected-shaped pattern returns []
- git restore --staged <path> extracts <path>
- git add <path> extracts <path>

Plus non-regression sanity fixtures preserving fail-closed behavior.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.implementation_start_gate import (
    MUTATING_VERB_TABLE,
    _classify_command_verb,
    _extract_git_add,
    _extract_git_checkout,
    _extract_git_mv,
    _extract_git_reset,
    _extract_git_restore,
    _extract_git_rm,
    _extract_powershell_both_paths,
    _extract_powershell_path_arg,
    _paths_from_shell,
    _split_pipeline_stages,
)


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    return tmp_path


# ---------------------------------------------------------------------------
# DCL Acceptance Assertion 1: git commit HEREDOC body mentioning paths -> []
# ---------------------------------------------------------------------------


def test_git_commit_heredoc_body_with_path_mentions_returns_empty(root: Path) -> None:
    cmd = (
        "git commit -m \"$(cat <<'PYEOF'\n"
        "This commit message body mentions scripts/foo.py and platform_tests/bar.py.\n"
        "PYEOF\n"
        ')"'
    )
    assert _paths_from_shell(root, cmd) == []


def test_git_commit_simple_message_returns_empty(root: Path) -> None:
    cmd = 'git commit -m "simple commit message"'
    assert _paths_from_shell(root, cmd) == []


def test_git_commit_with_explicit_protected_in_message_returns_empty(root: Path) -> None:
    cmd = "git commit -m 'docs: mention scripts/some.py in message body'"
    assert _paths_from_shell(root, cmd) == []


# ---------------------------------------------------------------------------
# DCL Acceptance Assertion 2: grep with protected-shaped pattern -> []
# ---------------------------------------------------------------------------


def test_grep_with_protected_pattern_returns_empty(root: Path) -> None:
    cmd = "grep -E '^scripts/' tmp.txt"
    assert _paths_from_shell(root, cmd) == []


def test_grep_with_arbitrary_protected_arg_returns_empty(root: Path) -> None:
    cmd = "grep -n 'pattern' scripts/implementation_start_gate.py"
    assert _paths_from_shell(root, cmd) == []


def test_egrep_pattern_returns_empty(root: Path) -> None:
    cmd = "egrep '^(scripts|platform_tests)/' notes.txt"
    assert _paths_from_shell(root, cmd) == []


# ---------------------------------------------------------------------------
# DCL Acceptance Assertion 3: git restore --staged <path> extracts the path
# ---------------------------------------------------------------------------


def test_git_restore_staged_protected_path_extracts_it(root: Path) -> None:
    cmd = "git restore --staged scripts/some_module.py"
    result = _paths_from_shell(root, cmd)
    assert "scripts/some_module.py" in result


def test_git_restore_without_staged_returns_empty(root: Path) -> None:
    cmd = "git restore scripts/some_module.py"
    assert _paths_from_shell(root, cmd) == []


# ---------------------------------------------------------------------------
# DCL Acceptance Assertion 4: git add <path> extracts the path
# ---------------------------------------------------------------------------


def test_git_add_protected_path_extracts_it(root: Path) -> None:
    cmd = "git add scripts/foo.py"
    result = _paths_from_shell(root, cmd)
    assert "scripts/foo.py" in result


def test_git_add_dash_a_flag_returns_empty(root: Path) -> None:
    cmd = "git add -A"
    assert _paths_from_shell(root, cmd) == []


def test_git_add_dash_u_flag_returns_empty(root: Path) -> None:
    cmd = "git add -u"
    assert _paths_from_shell(root, cmd) == []


def test_git_add_multiple_protected_paths(root: Path) -> None:
    cmd = "git add scripts/foo.py scripts/bar.py"
    result = _paths_from_shell(root, cmd)
    assert "scripts/foo.py" in result
    assert "scripts/bar.py" in result


# ---------------------------------------------------------------------------
# Pipeline stages tokenized independently
# ---------------------------------------------------------------------------


def test_pipeline_each_stage_independent(root: Path) -> None:
    # Stage 1 is grep (non-mutating); stage 2 is git add (mutating with path).
    # Each stage is tokenized independently per the DCL.
    cmd = "grep something scripts/foo.py | git add scripts/real_target.py"
    result = _paths_from_shell(root, cmd)
    assert "scripts/real_target.py" in result
    # grep's argument scripts/foo.py is NOT in result (grep is non-mutating).
    assert "scripts/foo.py" not in result


def test_semicolon_separator_stages(root: Path) -> None:
    cmd = "echo hello ; git add scripts/foo.py"
    result = _paths_from_shell(root, cmd)
    assert "scripts/foo.py" in result


def test_and_and_separator_stages(root: Path) -> None:
    cmd = "true && git add scripts/foo.py"
    result = _paths_from_shell(root, cmd)
    assert "scripts/foo.py" in result


def test_split_pipeline_stages_basic() -> None:
    stages = _split_pipeline_stages("cmd1 ; cmd2 | cmd3 && cmd4 || cmd5")
    assert stages == ["cmd1", "cmd2", "cmd3", "cmd4", "cmd5"]


def test_split_pipeline_stages_respects_quotes() -> None:
    stages = _split_pipeline_stages("echo 'a;b|c' ; ls")
    assert stages == ["echo 'a;b|c'", "ls"]


# ---------------------------------------------------------------------------
# Per-verb extractor behavior
# ---------------------------------------------------------------------------


def test_extract_git_rm_basic() -> None:
    assert _extract_git_rm(["git", "rm", "scripts/foo.py"]) == ["scripts/foo.py"]


def test_extract_git_rm_with_flag() -> None:
    assert _extract_git_rm(["git", "rm", "-r", "scripts/foo.py"]) == ["scripts/foo.py"]


def test_extract_git_mv_basic() -> None:
    assert _extract_git_mv(["git", "mv", "src.py", "dst.py"]) == ["src.py", "dst.py"]


def test_extract_git_restore_requires_staged_flag() -> None:
    assert _extract_git_restore(["git", "restore", "scripts/foo.py"]) == []
    assert _extract_git_restore(["git", "restore", "--staged", "scripts/foo.py"]) == ["scripts/foo.py"]


def test_extract_git_add_excludes_flag_args() -> None:
    # -A / --all / -u / --update / -p / --patch are NOT paths
    assert _extract_git_add(["git", "add", "-A"]) == []
    assert _extract_git_add(["git", "add", "--all"]) == []
    assert _extract_git_add(["git", "add", "-u"]) == []
    assert _extract_git_add(["git", "add", "--patch"]) == []


def test_extract_git_checkout_branch_mode_returns_empty() -> None:
    # No path-shaped tokens, no `--` separator → branch switch
    assert _extract_git_checkout(["git", "checkout", "main"]) == []
    assert _extract_git_checkout(["git", "checkout", "-b", "feature"]) == []


def test_extract_git_checkout_path_mode_extracts() -> None:
    # Path-shaped token present
    assert _extract_git_checkout(["git", "checkout", "scripts/foo.py"]) == ["scripts/foo.py"]
    # `--` separator
    assert _extract_git_checkout(["git", "checkout", "main", "--", "scripts/foo.py"]) == ["scripts/foo.py"]


def test_extract_git_reset_scope_changing_returns_empty() -> None:
    assert _extract_git_reset(["git", "reset", "--hard", "HEAD"]) == []
    assert _extract_git_reset(["git", "reset", "--soft", "HEAD~1"]) == []


def test_extract_git_reset_default_extracts() -> None:
    assert _extract_git_reset(["git", "reset", "HEAD", "scripts/foo.py"]) == ["HEAD", "scripts/foo.py"]


def test_extract_powershell_path_arg_positional() -> None:
    assert _extract_powershell_path_arg(["Set-Content", "scripts/foo.py"]) == ["scripts/foo.py"]


def test_extract_powershell_path_arg_named() -> None:
    assert _extract_powershell_path_arg(["Set-Content", "-Path", "scripts/foo.py"]) == ["scripts/foo.py"]


def test_extract_powershell_both_paths_positional() -> None:
    assert _extract_powershell_both_paths(["Copy-Item", "src.py", "dst.py"]) == ["src.py", "dst.py"]


def test_extract_powershell_both_paths_named() -> None:
    assert _extract_powershell_both_paths(["Copy-Item", "-Path", "src.py", "-Destination", "dst.py"]) == [
        "src.py",
        "dst.py",
    ]


# ---------------------------------------------------------------------------
# _classify_command_verb dispatch
# ---------------------------------------------------------------------------


def test_classify_git_rm() -> None:
    classification = _classify_command_verb(["git", "rm", "scripts/foo.py"])
    assert classification is not None
    extractor, relevant = classification
    assert extractor is not None
    assert relevant[0] == "git"


def test_classify_git_commit_non_mutating() -> None:
    classification = _classify_command_verb(["git", "commit", "-m", "msg"])
    assert classification is not None
    extractor, relevant = classification
    assert extractor(relevant) == []


def test_classify_unknown_verb_returns_none() -> None:
    assert _classify_command_verb(["unknown-verb", "scripts/foo.py"]) is None


def test_classify_env_prefix_skipped() -> None:
    # VAR=val git add scripts/foo.py
    classification = _classify_command_verb(["FOO=bar", "git", "add", "scripts/foo.py"])
    assert classification is not None
    extractor, relevant = classification
    assert relevant[0] == "git"
    assert "scripts/foo.py" in extractor(relevant)


def test_classify_empty_tokens() -> None:
    assert _classify_command_verb([]) is None


# ---------------------------------------------------------------------------
# Non-regression: protected-path filter via is_protected_path + ALLOWED_WRITE_PREFIXES
# ---------------------------------------------------------------------------


def test_unprotected_in_root_extracted(root: Path) -> None:
    # Per DCL acceptance assertion 3: an unprotected path IS extracted; the
    # caller's downstream logic decides whether the gate fires.
    cmd = "git add some/in-root/path.py"
    result = _paths_from_shell(root, cmd)
    assert "some/in-root/path.py" in result


def test_unprotected_in_root_path_extracted_per_dcl(root: Path) -> None:
    # Per DCL acceptance assertion 3: `git restore --staged unrelated/path`
    # returns `["unrelated/path"]` even though unrelated/path is not protected.
    cmd = "git restore --staged unrelated/path"
    result = _paths_from_shell(root, cmd)
    assert "unrelated/path" in result


def test_safe_command_with_protected_token_returns_empty(root: Path) -> None:
    # ls scripts/ -- ls is not a mutating verb
    cmd = "ls scripts/implementation_start_gate.py"
    assert _paths_from_shell(root, cmd) == []


# ---------------------------------------------------------------------------
# MUTATING_VERB_TABLE public surface
# ---------------------------------------------------------------------------


def test_mutating_verb_table_has_expected_keys() -> None:
    assert "git_mutating" in MUTATING_VERB_TABLE
    assert "git_non_mutating" in MUTATING_VERB_TABLE
    assert "powershell_path_arg" in MUTATING_VERB_TABLE
    assert "powershell_both_paths" in MUTATING_VERB_TABLE


def test_mutating_verb_table_contains_core_git_verbs() -> None:
    git_mut = MUTATING_VERB_TABLE["git_mutating"]
    for v in ("rm", "add", "mv", "restore", "checkout", "reset"):
        assert v in git_mut


def test_mutating_verb_table_git_commit_non_mutating() -> None:
    assert "commit" in MUTATING_VERB_TABLE["git_non_mutating"]
    assert "push" in MUTATING_VERB_TABLE["git_non_mutating"]
    assert "merge" in MUTATING_VERB_TABLE["git_non_mutating"]


# ---------------------------------------------------------------------------
# Tokenization failure → empty (fail-closed via caller's mutating-signal check)
# ---------------------------------------------------------------------------


def test_tokenization_failure_returns_empty(root: Path) -> None:
    # Unbalanced quote
    cmd = "git add 'unclosed-quote scripts/foo.py"
    result = _paths_from_shell(root, cmd)
    # shlex.split raises ValueError; stage produces no paths
    assert result == []


# ──────────────────────────────────────────────────────────────────────────
# NO-GO -006 F1 regression: _is_mutating_command MUST return True for the
# protected git verbs (`add`, `rm`, `restore`). Per Codex finding F1, the
# prior implementation extracted paths via _paths_from_shell but did not
# flag these commands as mutating in _is_mutating_command, so gate_decision
# allowed them without an impl-auth packet.
# ──────────────────────────────────────────────────────────────────────────


def test_is_mutating_git_add_returns_true() -> None:
    """`git add` MUST trigger the mutating-command predicate (NO-GO -006 F1)."""
    from scripts.implementation_start_gate import _is_mutating_command  # noqa: PLC0415

    assert _is_mutating_command("git add scripts/protected.py") is True
    assert _is_mutating_command("git add -A") is True
    assert _is_mutating_command("git add .") is True


def test_is_mutating_git_rm_returns_true() -> None:
    """`git rm` MUST trigger the mutating-command predicate (NO-GO -006 F1)."""
    from scripts.implementation_start_gate import _is_mutating_command  # noqa: PLC0415

    assert _is_mutating_command("git rm scripts/dead.py") is True
    assert _is_mutating_command("git rm --cached scripts/x.py") is True


def test_is_mutating_git_restore_returns_true() -> None:
    """`git restore` (with or without --staged) MUST trigger the predicate."""
    from scripts.implementation_start_gate import _is_mutating_command  # noqa: PLC0415

    assert _is_mutating_command("git restore --staged scripts/x.py") is True
    assert _is_mutating_command("git restore scripts/x.py") is True


def test_is_mutating_git_status_remains_false() -> None:
    """`git status` MUST remain a safe read command (no-regression guard)."""
    from scripts.implementation_start_gate import _is_mutating_command  # noqa: PLC0415

    assert _is_mutating_command("git status") is False
    assert _is_mutating_command("git status --short") is False


# ──────────────────────────────────────────────────────────────────────────
# NO-GO -008 F2 regression: final `gate_decision` behavior MUST block
# protected `git add` / `git rm` / `git restore --staged` payloads when no
# impl-auth packet is present. Per Codex F2 (carried forward from -006): the
# prior cycle's tests covered the `_is_mutating_command` predicate but did
# NOT exercise the end-to-end gate_decision return value.
# ──────────────────────────────────────────────────────────────────────────


def _no_auth_payload(tmp_path: Path, command: str) -> dict:
    """Build a Bash-payload dict for gate_decision with no impl-auth setup."""
    return {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }


def test_gate_decision_blocks_git_add_protected_path(tmp_path: Path) -> None:
    """`gate_decision` MUST return decision=block for `git add scripts/protected.py`."""
    from scripts.implementation_start_gate import gate_decision  # noqa: PLC0415

    payload = _no_auth_payload(tmp_path, "git add scripts/protected.py")
    result = gate_decision(payload)
    assert result.get("decision") == "block", f"expected block, got {result}"
    assert "scripts/" in result.get("reason", "")


def test_gate_decision_blocks_git_rm_protected_path(tmp_path: Path) -> None:
    """`gate_decision` MUST return decision=block for `git rm scripts/protected.py`."""
    from scripts.implementation_start_gate import gate_decision  # noqa: PLC0415

    payload = _no_auth_payload(tmp_path, "git rm scripts/protected.py")
    result = gate_decision(payload)
    assert result.get("decision") == "block", f"expected block, got {result}"
    assert "scripts/" in result.get("reason", "")


def test_gate_decision_blocks_git_restore_staged_protected_path(tmp_path: Path) -> None:
    """`gate_decision` MUST block `git restore --staged scripts/protected.py`."""
    from scripts.implementation_start_gate import gate_decision  # noqa: PLC0415

    payload = _no_auth_payload(tmp_path, "git restore --staged scripts/protected.py")
    result = gate_decision(payload)
    assert result.get("decision") == "block", f"expected block, got {result}"
    assert "scripts/" in result.get("reason", "")


def test_gate_decision_allows_git_status(tmp_path: Path) -> None:
    """`gate_decision` MUST allow `git status` (safe-read regression guard)."""
    from scripts.implementation_start_gate import gate_decision  # noqa: PLC0415

    payload = _no_auth_payload(tmp_path, "git status")
    result = gate_decision(payload)
    # Safe-read commands return empty dict (allow), not {"decision": "block"}.
    assert result == {}, f"expected empty allow-dict, got {result}"
