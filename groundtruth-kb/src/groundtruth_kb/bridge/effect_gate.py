#!/usr/bin/env python3
"""Check tool effects through the native CLI and current artifact claims."""

from __future__ import annotations

import ast
import json
import os
import re
import shlex
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from groundtruth_kb.governance.output import emit_effect_gate_result

SAFE_COMMAND_PREFIXES = (
    "rg ",
    "git status",
    "git diff",
    "git show",
    "git log",
    "get-content",
    "select-string",
    "get-childitem",
    "python -m pytest",
    "python -m groundtruth_kb deliberations search",
)

INVALID_HOOK_PAYLOAD_KEY = "__gtkb_invalid_hook_payload__"

DIRECT_GIT_READ_ONLY_SUBCOMMANDS = frozenset(
    {
        "blame",
        # c118: object and content reads; neither has a writing form, and `git cat-file` reads an object by id.
        # This set judges whether Git can write. What a read-only form can reach is judged by _git_reach_roots: git
        # grep and git ls-files forms that read Git-ignored files are refused there as traversal (round 2, B127).
        "cat-file",
        "grep",
        "check-attr",
        "check-ignore",
        "cherry",
        "describe",
        "diff",
        # Read-only ref enumeration. Reviewers must be able to inspect branch
        # topology to verify claims about it; blocking that degrades review
        # quality without preventing any effect. `branch` is deliberately NOT
        # listed: `git branch -d/-D/-m/-M/--set-upstream-to` mutate, so it
        # cannot be allow-listed by subcommand name alone. Covered by
        # test_change7_drops_argument_position_false_positives.
        "for-each-ref",
        "show-ref",
        "help",
        "log",
        "ls-files",
        "ls-remote",
        "ls-tree",
        "merge-base",
        "rev-list",
        "rev-parse",
        "shortlog",
        "show",
        "status",
        "verify-commit",
        "verify-tag",
        "version",
    }
)

GIT_GLOBAL_OPTIONS_WITH_VALUES = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}
)

GIT_FINALIZATION_CHAINING_MARKERS = (";", "&&", "||", "|")

GIT_FINALIZATION_EXECUTION_MARKERS = ("$(", "`")

# Owner decision D61 (2026-09-25, observer B90): starting and stopping GT-KB's services, Home and dashboard, and
# replacing its operational controls, are owner operations, done from the GT-KB Home's controls page or the owner's own
# terminal. They are neither file nor Git effects, so the gate passed them for any agent shell. It now refuses them in
# every harness context, bound or not, whatever the target. Read-only forms stay allowed (gt services status, gt
# controls show, Get-ScheduledTask, Get-Service, schtasks /query).
GT_OWNER_OPERATIONS = {
    "services": frozenset({"start", "stop"}),
    "home": frozenset({"start", "stop"}),
    "dashboard": frozenset({"start", "stop", "serve"}),
    "controls": frozenset({"set"}),
}
GT_GLOBAL_OPTIONS_WITH_VALUES = frozenset({"--config"})
GT_MODULES = frozenset({"groundtruth_kb", "groundtruth_kb.cli"})
# GT-KB's scheduled tasks and Windows service share this prefix (GTKB-DomainService, GTKB-Home, GTKB-Ollama-Serve,
# GTKB-BaseBackup, gtkb-postgresql); a wildcard such as 'GTKB*' names them too.
GTKB_TASK_OR_SERVICE_NAME_RE = re.compile(r"gtkb(?:-[a-z0-9-]+|-?\*[a-z0-9*-]*)", re.IGNORECASE)
SERVICE_CONTROL_CMDLETS = frozenset(
    {
        "start-scheduledtask",
        "stop-scheduledtask",
        "enable-scheduledtask",
        "disable-scheduledtask",
        "register-scheduledtask",
        "unregister-scheduledtask",
        "set-scheduledtask",
        "start-service",
        "stop-service",
        "restart-service",
        "set-service",
        "suspend-service",
        "resume-service",
        "new-service",
        "remove-service",
    }
)
SCHTASKS_CHANGING_SWITCHES = frozenset({"/run", "/end", "/change", "/delete", "/create"})
SC_CHANGING_VERBS = frozenset({"start", "stop", "pause", "continue", "config", "delete", "create", "failure"})
NET_CHANGING_VERBS = frozenset({"start", "stop", "pause", "continue"})
# A command the gate cannot inspect: nested past the inspection cap, or a recognized shell wrapper whose command is
# encoded or empty. The Git rule and the owner-operation rule each fail closed on it (observer B102), so neither rule's
# refusal depends on the other running first. c122 adds a program named by a variable or an expression, text that
# Invoke-Expression reads from its pipeline, unparsable handed text and a launcher option the gate does not know.
UNINSPECTABLE_SHELL_COMMAND = "<uninspectable-shell-command>"

# c121: every write cmdlet, alias and cmd built-in is also matched by _NAMED_WRITE_RE, which is built from the same
# verb tables that read their targets, so the write signal and the target reading cannot list different verbs again
# (M13 GTKB Home, Q1 on c120: add-content, clear-content and rename-item were in the tables and not here).
MUTATING_COMMAND_RE = re.compile(
    r"\b("
    r"set-content|out-file|new-item|remove-item|move-item|copy-item|"
    # WI-IMPL-START-GATE: verb-aware path extraction. Include `git add`,
    # `git rm`, and `git restore` so protected-path staging commands also
    # trip the gate. (Per Codex NO-GO -006: extracting the path without
    # firing `_is_mutating_command` left those commands silently allowed.)
    r"apply_patch|git\s+(?:add|rm|restore|commit|reset|checkout|merge|rebase|tag|push)|"
    # F10: POSIX write verbs. The original alternation covered only the
    # PowerShell surface (set-content/remove-item/move-item/copy-item), so on
    # the Bash surface `sed -i`, `touch`, `tee`, `cp`, `mv`, `rm` and friends
    # were never classified as mutations and passed the gate unconditionally,
    # while read-only inspection was refused. Quoted spans are masked by
    # _has_mutating_signal before this regex runs, so verbs appearing inside
    # quoted prose do not false-positive.
    r"sed\s+(?:[^|;&]*\s)?-i\b|awk\s+[^|;&]*-i\s+inplace\b|"
    r"python\s+.*(?:write_text|open\(.+,\s*['\"]w|sqlite3|insert_|update_|delete_)"
    r")\b"
    # Change 7 (WI-6821): bare POSIX write verbs are matched only at COMMAND
    # POSITION -- start of string, or after a pipe/semicolon/ampersand/newline,
    # or after an opening paren. The unanchored form these replace matched the
    # verbs anywhere, so ordinary prose in an argument (`git log --grep=rm`, a
    # `--filter` value, a quoted sentence) tripped a fail-closed gate. Quoted
    # spans are masked by `_has_mutating_signal` before this regex runs; the
    # anchor is the second, independent guard against argument-position text.
    #
    # This alternative sits OUTSIDE the `\b( ... )\b` group above, deliberately.
    # Inside it, the group's leading `\b` must match immediately before the
    # anchor, and a space-to-pipe transition is not a word boundary -- so
    # `cat x | tee <path>`, `true && rm <path>`, and `(cd d && rm <path>)` all
    # silently stopped matching. Hoisting it to a top-level alternative keeps
    # every real detection while dropping the argument-position false
    # positives. Regression coverage for both directions lives in
    # platform_tests/scripts/test_implementation_start_gate.py.
    r"|(?:^|[|;&\n]|\()\s*(?:tee|touch|truncate|shred|install|patch|dd|cp|mv|rm|ln)\b",
    re.IGNORECASE,
)

REDIRECT_OPERATOR_TOKEN_RE = re.compile(r"&?>{1,2}")

NULL_SINK_REDIRECT_STRIP_RE = re.compile(
    r"\s*(?:\d+|&)?>{1,2}(?!&)\s*(?:/dev/null|\$null|NUL)\b",
    re.IGNORECASE,
)

SAFE_SQLITE_READ_RE = re.compile(
    r"sqlite3\b.*?\.execute\(\s*['\"](?:SELECT|WITH|EXPLAIN)\b",
    re.IGNORECASE | re.DOTALL,
)

SQLITE_WRITE_DISQUALIFIERS_RE = re.compile(
    r"\.executescript\(|\.executemany\(|\.commit\(|"
    r"\b(?:INSERT|UPDATE|DELETE|REPLACE|CREATE|DROP|ALTER|TRUNCATE|PRAGMA)\b",
    re.IGNORECASE,
)

PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)

PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+)$", re.MULTILINE)

_HEREDOC_OPENER_RE = re.compile(
    r"\$\([ \t]*cat[ \t]+<<(?P<dash>-?)[ \t]*"
    r"(?P<q>['\"])(?P<delim>[A-Za-z_][A-Za-z0-9_]*)(?P=q)"
)

_PYTHON_EXECUTABLE_NAMES = {"py", "python", "python.exe"}

_WRAP_DIAGNOSTIC_SCRIPT_NAMES = {
    "wrap_capture_transcript.py",
    "wrap_scan_hygiene.py",
    "wrap_scan_consistency.py",
}


def _project_root(payload: dict[str, Any]) -> Path:
    explicit = payload.get("project_root")
    if isinstance(explicit, str) and explicit.strip():
        return Path(explicit).resolve()
    cwd = payload.get("cwd")
    cwd_path = Path(cwd).resolve() if isinstance(cwd, str) and cwd.strip() else Path.cwd()
    return Path(os.environ.get("GTKB_PROJECT_ROOT") or cwd_path).resolve()


def _tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "tool", "name"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def _tool_input(payload: dict[str, Any]) -> Any:
    for key in ("tool_input", "input", "parameters"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return value
    return payload


def _normalize(root: Path, path_text: str, *, shell_quoted: bool = False) -> str | None:
    cleaned = path_text
    if shell_quoted and len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in "'\"":
        cleaned = cleaned[1:-1]
    cleaned = cleaned.replace("\\", "/")
    if not cleaned:
        return None
    try:
        target = Path(cleaned)
        target = target if target.is_absolute() else root / target
        return target.relative_to(root).as_posix()
    except ValueError:
        return cleaned


def _paths_from_apply_patch(root: Path, text: str) -> list[str]:
    raw = text or ""
    paths = PATCH_PATH_RE.findall(raw)
    paths.extend(PATCH_MOVE_RE.findall(raw))
    if not paths:
        normalized = raw.replace("`r`n", "\n").replace("`n", "\n").replace("\\r\\n", "\n").replace("\\n", "\n")
        paths = PATCH_PATH_RE.findall(normalized)
        paths.extend(PATCH_MOVE_RE.findall(normalized))
    return [rel for raw in paths if (rel := _normalize(root, raw))]


def _extract_git_rm(tokens: list[str]) -> list[str]:
    return [t for t in tokens[2:] if not t.startswith("-")]


def _extract_git_restore(tokens: list[str]) -> list[str]:
    args = tokens[2:]
    if "--staged" not in args:
        return []
    sep_idx = args.index("--staged")
    return [t for t in args[sep_idx + 1 :] if not t.startswith("-")]


def _extract_git_add(tokens: list[str]) -> list[str]:
    flags_no_paths = {"-A", "--all", "-u", "--update", "-p", "--patch", "-n", "--dry-run"}
    return [t for t in tokens[2:] if not t.startswith("-") and t not in flags_no_paths]


def _extract_git_mv(tokens: list[str]) -> list[str]:
    return [t for t in tokens[2:] if not t.startswith("-")]


def _extract_git_checkout(tokens: list[str]) -> list[str]:
    args = tokens[2:]
    if "--" in args:
        idx = args.index("--")
        return [t for t in args[idx + 1 :] if not t.startswith("-")]
    path_shaped = [t for t in args if "/" in t or "\\" in t]
    if path_shaped:
        return [t for t in args if not t.startswith("-")]
    return []


def _extract_git_reset(tokens: list[str]) -> list[str]:
    args = tokens[2:]
    if any(f in args for f in ("--hard", "--mixed", "--soft", "--keep", "--merge")):
        return []
    return [t for t in args if not t.startswith("-")]


def _extract_none(tokens: list[str]) -> list[str]:
    return []


def _extract_powershell_path_arg(tokens: list[str]) -> list[str]:
    """First positional arg OR -Path/-FilePath/-LiteralPath flag value.

    Once any of those sources supplies a path, subsequent non-flag tokens are
    not treated as positional paths -- they are values of other named flags
    like -Value, -Force, -Confirm, etc.
    """
    paths: list[str] = []
    path_captured = False
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t.lower() in ("-path", "-filepath", "-literalpath"):
            if i + 1 < len(tokens):
                paths.append(tokens[i + 1])
                path_captured = True
                i += 2
                continue
        elif t.startswith("-"):
            # Skip the named flag's value (PowerShell convention: flag + value)
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                i += 2
                continue
        elif not path_captured:
            paths.append(t)
            path_captured = True
        i += 1
    return paths


def _extract_powershell_both_paths(tokens: list[str]) -> list[str]:
    flag_paths: list[str] = []
    positional: list[str] = []
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t.lower() in ("-path", "-literalpath", "-destination"):
            if i + 1 < len(tokens):
                flag_paths.append(tokens[i + 1])
                i += 2
                continue
        elif not t.startswith("-") and len(positional) < 2:
            positional.append(t)
        i += 1
    return flag_paths + positional


_POSIX_PATH_ARG_VERBS = frozenset({"sed", "awk", "tee", "touch", "truncate", "rm", "shred", "install", "patch"})

_POSIX_BOTH_PATHS_VERBS = frozenset({"cp", "mv", "ln", "dd"})


def _extract_posix_paths(tokens: list[str]) -> list[str]:
    """Every non-flag operand of a POSIX write verb, plus ``dd`` ``of=`` targets.

    Deliberately over-collects: a non-path operand (a ``sed`` script such as
    ``s/a/b/``, or a ``dd`` ``if=`` source) simply fails to match any protected
    glob and is inert. Under-collecting is the dangerous direction -- a missed
    operand degrades to ``<unknown-mutating-target>``, which both refuses the
    emergency-repair exemption and hides which path was actually at risk.
    """
    paths: list[str] = []
    for token in tokens[1:]:
        if token.startswith("-"):
            continue
        if "=" in token and "/" not in token.split("=", 1)[0]:
            key, _, value = token.partition("=")
            if key.lower() == "of" and value:
                paths.append(value)
            continue
        paths.append(token)
    return paths


_GIT_NON_MUTATING_SUBCOMMANDS = DIRECT_GIT_READ_ONLY_SUBCOMMANDS

_GIT_MUTATING_EXTRACTORS = {
    "rm": _extract_git_rm,
    "restore": _extract_git_restore,
    "add": _extract_git_add,
    "mv": _extract_git_mv,
    "checkout": _extract_git_checkout,
    "reset": _extract_git_reset,
}

_POWERSHELL_PATH_ARG_VERBS = frozenset(
    {
        "set-content",
        "out-file",
        "new-item",
        "remove-item",
        "add-content",
        "clear-content",
        # c121 (M13 GTKB Home, Q1 on c120): the other cmdlets that write the file or item they name.
        "export-csv",
        "export-clixml",
        "tee-object",
        "start-transcript",
        "set-acl",
        "unblock-file",
        "set-itemproperty",
        "new-itemproperty",
        "remove-itemproperty",
        "rename-itemproperty",
        "clear-itemproperty",
    }
)

_POWERSHELL_BOTH_PATHS_VERBS = frozenset(
    {
        "move-item",
        "copy-item",
        "rename-item",
        "copy-itemproperty",
        "move-itemproperty",
    }
)

# c121: cmdlets whose written path is a destination parameter, and web requests, which write a file only with -OutFile.
_POWERSHELL_DESTINATION_VERBS = frozenset({"expand-archive", "compress-archive"})
_POWERSHELL_OUTFILE_VERBS = frozenset({"invoke-webrequest", "invoke-restmethod"})

# c121: PowerShell aliases that run a write cmdlet, read as that cmdlet.
_POWERSHELL_WRITE_ALIASES = {
    "ac": "add-content",
    "clc": "clear-content",
    "ni": "new-item",
    "ri": "remove-item",
    "rni": "rename-item",
    "mi": "move-item",
    "ci": "copy-item",
    "cpi": "copy-item",
    "epcsv": "export-csv",
    "sp": "set-itemproperty",
    "rp": "remove-itemproperty",
    "rnp": "rename-itemproperty",
    "clp": "clear-itemproperty",
    "iwr": "invoke-webrequest",
    "irm": "invoke-restmethod",
}

# c121: names that are a PowerShell alias of a write cmdlet and also a cmd built-in or, for mkdir and rmdir, a POSIX
# command. Each takes cmd switches (/s, /q, /y) or POSIX flags (-p) as well as PowerShell parameters, so every operand
# is read as a target (_extract_dual_syntax_paths).
_DUAL_SYNTAX_WRITE_VERBS = frozenset({"copy", "move", "ren", "del", "erase", "rd", "rmdir", "md", "mkdir"})

_CMD_SWITCH_RE = re.compile(r"/-?[a-z?](?::\S*)?", re.IGNORECASE)
_POWERSHELL_PATH_PARAMETERS = frozenset({"-path", "-literalpath", "-filepath", "-destination", "-destinationpath"})


def _extract_dual_syntax_paths(tokens: list[str]) -> list[str]:
    """Every operand of copy, move, ren, del, erase, rd, rmdir, md or mkdir (c121).

    In PowerShell these run the write cmdlets, in cmd the built-ins, and mkdir and rmdir are POSIX commands too. A
    PowerShell path parameter's value and every other token that is neither a flag (-p, -Force) nor a cmd switch (/s,
    /q, /y) is a target. Like _extract_posix_paths this over-collects rather than under-collects.
    """
    paths: list[str] = []
    i = 1
    while i < len(tokens):
        token = tokens[i]
        if token.lower() in _POWERSHELL_PATH_PARAMETERS:
            paths.extend(tokens[i + 1 : i + 2])
            i += 2
            continue
        if not token.startswith("-") and not _CMD_SWITCH_RE.fullmatch(token):
            paths.append(token)
        i += 1
    return paths


def _extract_destination_path(tokens: list[str]) -> list[str]:
    """The path Expand-Archive or Compress-Archive writes (c121).

    -DestinationPath when named; otherwise the operand that binds to it (the second, or the first when the source is
    named). Expand-Archive without a destination writes into the current directory, which is then the target.
    """
    positional: list[str] = []
    named_source = False
    i = 1
    while i < len(tokens):
        lowered = tokens[i].lower()
        if lowered in ("-destinationpath", "-destination"):
            return tokens[i + 1 : i + 2]
        if lowered in ("-path", "-literalpath", "-compressionlevel"):
            named_source = named_source or lowered != "-compressionlevel"
            i += 2
            continue
        if not tokens[i].startswith("-"):
            positional.append(tokens[i])
        i += 1
    index = 0 if named_source else 1
    if len(positional) > index:
        return [positional[index]]
    return ["."] if tokens[0].lower() == "expand-archive" else []


def _extract_outfile(tokens: list[str]) -> list[str]:
    """The file an Invoke-WebRequest or Invoke-RestMethod call writes, its -OutFile value (c121); none without it."""
    for index, token in enumerate(tokens[1:], start=1):
        lowered = token.lower()
        if lowered.startswith("-outf"):
            if ":" in token:
                return [token.split(":", 1)[1]]
            return tokens[index + 1 : index + 2]
    return []


def _word_alternation(words: frozenset[str] | set[str]) -> str:
    return "|".join(re.escape(word) for word in sorted(words, key=len, reverse=True))


# c121: every named write command, for the write signal and for checking that each one's target was read. A cmdlet
# name matches wherever it appears outside quotes, as set-content always has. An alias, a cmd built-in or a POSIX write
# verb matches only at command position (the start, after a separator, or at the start of a script block or group),
# so prose and argument text do not match. A web request is a write only with -OutFile. `sed -i` and `awk -i inplace`
# are the POSIX in-place edits of MUTATING_COMMAND_RE.
_COMMAND_POSITION = r"(?:^|[|;&\n{(])\s*"
_CMDLET_WRITE_WORDS = _word_alternation(
    _POWERSHELL_PATH_ARG_VERBS | _POWERSHELL_BOTH_PATHS_VERBS | _POWERSHELL_DESTINATION_VERBS
)
_ALIAS_WRITE_WORDS = _word_alternation(
    (frozenset(_POWERSHELL_WRITE_ALIASES) - {"iwr", "irm"}) | _DUAL_SYNTAX_WRITE_VERBS
)
_NAMED_WRITE_RE = re.compile(
    rf"\b(?P<cmdlet>{_CMDLET_WRITE_WORDS})\b"
    rf"|{_COMMAND_POSITION}(?P<alias>{_ALIAS_WRITE_WORDS})(?:\.exe)?\b(?![-.])"
    rf"|{_COMMAND_POSITION}(?P<posix>tee|touch|truncate|shred|install|patch|dd|cp|mv|rm|ln)(?:\.exe)?\b(?![-.])"
    r"|\b(?P<sed>sed)\s+(?:[^|;&]*\s)?-i\b|\b(?P<awk>awk)\s+[^|;&]*-i\s+inplace\b"
    rf"|(?:\b(?P<web>invoke-webrequest|invoke-restmethod)\b|{_COMMAND_POSITION}(?P<webalias>iwr|irm)\b)[^|;&\n]*?\s-outf",
    re.IGNORECASE,
)

# c121: .NET calls that write a file or directory. Their targets are not read (a call's argument may be any
# expression), so a command that carries one is refused whole: unknown_effect_targets.
_DOTNET_WRITE_RE = re.compile(
    r"\[(?:(?:system\.)?io\.)?(?:file|directory)\]::\s*"
    r"(?:write\w*|append\w*|create\w*|delete|move|copy|replace|open(?!read|text)\w*|set(?!currentdirectory)\w*"
    r"|encrypt|decrypt)\s*\("
    r"|\[(?:system\.)?io\.(?:streamwriter|filestream|binarywriter)\]::\s*new\s*\("
    r"|\[(?:system\.)?io\.compression\.zipfile\]::\s*(?:createfromdirectory|extracttodirectory|open)\s*\("
    r"|\bnew-object\s+(?:-typename\s+)?(?:system\.)?io\.(?:streamwriter|filestream|binarywriter)\b"
    r"|\.(?:delete|create|createtext|appendtext|openwrite|moveto|copyto|createsubdirectory|encrypt|decrypt"
    r"|extracttofile|downloadfile|save|setaccesscontrol)\s*\("
    r"|\.(?:isreadonly|attributes|(?:creation|lastwrite|lastaccess)time(?:utc)?)\s*[+-]?=(?!=)",
    re.IGNORECASE,
)


def _canonical_write_verb(word: str) -> str:
    lowered = word.lower().removesuffix(".exe")
    return _POWERSHELL_WRITE_ALIASES.get(lowered, lowered)


def _named_writes(shell_view: str) -> Counter[str]:
    """How many times each named write command occurs in a quote-masked command, by canonical verb (c121)."""
    found: Counter[str] = Counter()
    for match in _NAMED_WRITE_RE.finditer(shell_view):
        word = next(value for value in match.groupdict().values() if value)
        found[_canonical_write_verb(word)] += 1
    return found


MUTATING_VERB_TABLE = {
    "git_mutating": tuple(_GIT_MUTATING_EXTRACTORS),
    "git_non_mutating": tuple(_GIT_NON_MUTATING_SUBCOMMANDS),
    "powershell_path_arg": tuple(_POWERSHELL_PATH_ARG_VERBS),
    "powershell_both_paths": tuple(_POWERSHELL_BOTH_PATHS_VERBS),
    "powershell_destination": tuple(_POWERSHELL_DESTINATION_VERBS),
    "powershell_outfile": tuple(_POWERSHELL_OUTFILE_VERBS),
    "powershell_aliases": tuple(_POWERSHELL_WRITE_ALIASES),
    "dual_syntax": tuple(_DUAL_SYNTAX_WRITE_VERBS),
    "posix_path_arg": tuple(_POSIX_PATH_ARG_VERBS),
    "posix_both_paths": tuple(_POSIX_BOTH_PATHS_VERBS),
}


def _classify_command_verb(tokens: list[str]) -> tuple[Callable[[list[str]], list[str]], list[str]] | None:
    if not tokens:
        return None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if "=" in tok and not tok.startswith("-") and "/" not in tok and "\\" not in tok:
            i += 1
            continue
        break
    if i >= len(tokens):
        return None
    relevant = tokens[i:]
    verb = relevant[0].lower()

    if verb == "git" and len(relevant) >= 2:
        sub = relevant[1].lower()
        extractor = _GIT_MUTATING_EXTRACTORS.get(sub)
        if extractor is not None:
            return extractor, relevant
        if sub in _GIT_NON_MUTATING_SUBCOMMANDS:
            return _extract_none, relevant
        return None

    # c121: an alias reads as its cmdlet, and a trailing .exe (Git Bash's mkdir.exe) does not hide the verb.
    verb = _canonical_write_verb(verb)
    if verb in _POWERSHELL_PATH_ARG_VERBS:
        return _extract_powershell_path_arg, relevant
    if verb in _POWERSHELL_BOTH_PATHS_VERBS:
        return _extract_powershell_both_paths, relevant
    if verb in _DUAL_SYNTAX_WRITE_VERBS:
        return _extract_dual_syntax_paths, relevant
    if verb in _POWERSHELL_DESTINATION_VERBS:
        return _extract_destination_path, relevant
    if verb in _POWERSHELL_OUTFILE_VERBS:
        return _extract_outfile, relevant
    if verb in _POSIX_PATH_ARG_VERBS or verb in _POSIX_BOTH_PATHS_VERBS:
        return _extract_posix_paths, relevant

    return None


def _split_pipeline_stages(command: str) -> list[str]:
    if not command:
        return []
    masked = _mask_quoted_spans(command, mask_double=False)
    stages: list[str] = []
    start = 0
    i = 0
    while i < len(masked):
        ch = masked[i]
        nxt = masked[i + 1] if i + 1 < len(masked) else ""
        if ch in "\r\n":
            stages.append(command[start:i])
            if ch == "\r" and nxt == "\n":
                i += 1
            start = i + 1
            i += 1
            continue
        if ch == ";":
            stages.append(command[start:i])
            start = i + 1
            i += 1
            continue
        if ch == "|" and nxt == "|":
            stages.append(command[start:i])
            start = i + 2
            i += 2
            continue
        if ch == "|":
            stages.append(command[start:i])
            start = i + 1
            i += 1
            continue
        if ch == "&" and nxt == "&":
            stages.append(command[start:i])
            start = i + 2
            i += 2
            continue
        i += 1
    stages.append(command[start:])
    return [s.strip() for s in stages if s.strip()]


def _split_command_stages(command: str) -> list[str]:
    """Split a command into the commands it runs, for the Git rule and the owner-operation rule.

    As `_split_pipeline_stages`, and also at a single `&`: cmd's command separator, and the background operator of
    bash and PowerShell 7, both start another command. A redirection is not a separator (`2>&1`, `>&2`, `<&3`,
    `&>file`, `&>>file`), and PowerShell's leading call operator (`& gt.exe ...`) leaves only an empty stage, which is
    dropped. The file-effect analysis keeps `_split_pipeline_stages`.
    """
    stages: list[str] = []
    for stage in _split_pipeline_stages(command):
        masked = _mask_quoted_spans(stage, mask_double=False)
        start = 0
        for i, ch in enumerate(masked):
            if ch != "&":
                continue
            before = masked[i - 1] if i else ""
            after = masked[i + 1] if i + 1 < len(masked) else ""
            if (before and before in "<>|") or after == ">":
                continue
            stages.append(stage[start:i])
            start = i + 1
        stages.append(stage[start:])
    return [s.strip() for s in stages if s.strip()]


def _shell_split(command: str, *, punctuation: bool = False) -> list[str] | None:
    if not command:
        return []
    if punctuation:
        lexer = shlex.shlex(command, posix=False, punctuation_chars=True)
        lexer.whitespace_split = True
        try:
            return list(lexer)
        except ValueError:
            return None
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return None


def _shell_verb_index(tokens: list[str]) -> int | None:
    for index, token in enumerate(tokens):
        if "=" in token and not token.startswith("-") and "/" not in token and "\\" not in token:
            continue
        return index
    return None


def _executable_name(token: str) -> str:
    """Return a shell executable basename across POSIX and Windows paths."""
    return _clean_shell_token(token).replace("\\", "/").rsplit("/", 1)[-1].lower()


_CMD_SHELL_NAMES = frozenset({"cmd", "cmd.exe"})
_POWERSHELL_NAMES = frozenset({"powershell", "powershell.exe", "pwsh", "pwsh.exe"})
_POSIX_SHELL_NAMES = frozenset({"bash", "bash.exe", "sh", "sh.exe", "zsh", "zsh.exe"})
_POWERSHELL_ENCODED_COMMAND_FLAGS = frozenset(
    {"-e", "-ec", "-en", "-enc", "-enco", "-encod", "-encode", "-encoded", "-encodedcommand"}
)


def _nested_shell_command(stage: str) -> tuple[str | None, bool]:
    """Return a nested shell command and whether a shell wrapper was recognized.

    An encoded or malformed command is reported as a recognized wrapper with no
    inspectable command so direct Git enforcement can fail closed.
    """
    tokens = _shell_split(stage)
    if not tokens:
        return None, False
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None, False
    relevant = tokens[verb_index:]
    while relevant and _clean_shell_token(relevant[0]).lower() in {"&", "call"}:
        relevant = relevant[1:]
    if not relevant:
        return None, True
    executable = _executable_name(relevant[0])

    if executable in _CMD_SHELL_NAMES:
        for index, raw in enumerate(relevant[1:], start=1):
            if _clean_shell_token(raw).lower() in {"/c", "/k"}:
                nested = " ".join(relevant[index + 1 :]).strip()
                return (_clean_shell_token(nested) if nested else None), True
        return None, False

    if executable in _POWERSHELL_NAMES:
        normalized = [_clean_shell_token(token).lower() for token in relevant[1:]]
        if any(token in _POWERSHELL_ENCODED_COMMAND_FLAGS for token in normalized):
            return None, True
        for index, token in enumerate(normalized, start=1):
            if token in {"-c", "-command", "/c", "/command"}:
                nested = " ".join(relevant[index + 1 :]).strip()
                return (_clean_shell_token(nested) if nested else None), True
        return None, False

    if executable in _POSIX_SHELL_NAMES:
        normalized = [_clean_shell_token(token).lower() for token in relevant[1:]]
        for index, token in enumerate(normalized, start=1):
            if token == "-c":
                if index + 1 >= len(relevant):
                    return None, True
                return _clean_shell_token(relevant[index + 1]), True
        return None, False

    if verb_index < len(tokens) and tokens[verb_index:] != relevant:
        return " ".join(relevant), True
    return None, False


def _python_script_invocation(tokens: list[str]) -> tuple[str, list[str]] | None:
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    relevant = tokens[verb_index:]
    verb_name = Path(relevant[0].strip("'\"")).name.lower()
    if verb_name not in _PYTHON_EXECUTABLE_NAMES and not verb_name.startswith("python"):
        return None
    if len(relevant) < 2:
        return None
    script_token = relevant[1].strip("'\"")
    script_name = Path(script_token).name
    if script_name not in _WRAP_DIAGNOSTIC_SCRIPT_NAMES:
        return None
    return script_name, relevant[2:]


def _direct_git_subcommand(stage: str) -> str | None:
    """Return a direct Git subcommand, accounting for executable/global options."""
    tokens = _shell_split(stage)
    if not tokens:
        return None
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    relevant = [_clean_shell_token(token) for token in tokens[verb_index:]]
    executable = Path(relevant[0]).name.lower()
    if executable not in {"git", "git.exe"}:
        return None

    index = 1
    while index < len(relevant):
        token = relevant[index]
        if token == "--":
            index += 1
            break
        if token in GIT_GLOBAL_OPTIONS_WITH_VALUES:
            if index + 1 >= len(relevant):
                return None
            index += 2
            continue
        if any(token.startswith(option + "=") for option in GIT_GLOBAL_OPTIONS_WITH_VALUES):
            index += 1
            continue
        if token.startswith("-C") and token != "-C":
            index += 1
            continue
        if token.startswith("-c") and token != "-c":
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token.lower()
    if index < len(relevant):
        return relevant[index].lower()
    return None


def _is_direct_git_invocation(stage: str) -> bool:
    tokens = _shell_split(stage)
    if not tokens:
        return False
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return False
    return Path(_clean_shell_token(tokens[verb_index])).name.lower() in {"git", "git.exe"}


# c122 (owner 2026-09-30 20:52, "Fix first: c122"; batch design WP1, section W): one walk gives the Git rule and the
# owner-operation rule every command a line runs. Before c122 both rules followed only the nested shells (cmd /c,
# pwsh -c, bash -c) and PowerShell's call operator, so a Git effect or an owner operation inside a script block, a
# group, a subexpression, a POSIX keyword stage, a launcher or Invoke-Expression, or run through a program named by a
# variable, passed (probe-wp1-fail-open-20260930T204906.json). The write rule keeps c121's refuse-whole judgment.
_BLOCK_PLACEHOLDER = "__gtkb_block__"
_GROUP_PLACEHOLDER = "@__gtkb_group__"
_SUBEXPRESSION_PLACEHOLDER = "$__gtkb_subexpression__"
# An operand a launcher supplies when it runs (xargs's input item, find's {}): a value the gate cannot read.
_UNRESOLVED_OPERAND = "$__gtkb_operand__"
_GROUP_DEPTH = 32
_POSIX_KEYWORDS = frozenset({"if", "elif", "while", "until", "do", "then", "else", "!"})
_ENV_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\+?=")
_BASH_ARRAY_ASSIGNMENT = re.compile(r"(?:^|[\s;|&])[A-Za-z_][A-Za-z0-9_]*\+?=$")
_ASSIGNMENT_OPERATORS = frozenset({"=", "+=", "-=", "*=", "/=", "%=", "??="})
_POWERSHELL_ATTACHED_ASSIGNMENT = re.compile(r"\$[^\s=]*?(?:[-+*/%]|\?\?)?=(?!=)(?P<value>.*)", re.DOTALL)
_COMPARISON_OPERATOR_NAMES = (
    "eq",
    "ne",
    "gt",
    "ge",
    "lt",
    "le",
    "like",
    "notlike",
    "match",
    "notmatch",
    "contains",
    "notcontains",
    "in",
    "notin",
    "replace",
    "split",
)
_EXPRESSION_OPERATORS = frozenset(
    {f"-{case}{name}" for name in _COMPARISON_OPERATOR_NAMES for case in ("", "c", "i")}
    | {"-and", "-or", "-xor", "-not", "-band", "-bor", "-bxor", "-bnot", "-shl", "-shr", "-is", "-isnot", "-as", "-f"}
    | {"-join", "in"}
)
_CMD_VARIABLE = re.compile(r"%[A-Za-z_][A-Za-z0-9_]*%")


def _unresolved_value(token: str) -> bool:
    """Whether a shell word holds a value the shell supplies only when it runs (c122; batch design WP1, W and item 8).

    A $ (a variable, ${...}, $env:..., a subexpression), a backtick or a cmd %NAME% outside single quotes; a word that
    starts with @ (a splat or an array), ( (an expression) or, with its quotes removed, ~ (the home directory, which
    PowerShell's providers also resolve inside quotes); and a word whose quotes do not close, which cannot be read.
    Single-quoted text is literal.
    """
    text = token.strip()
    if not text:
        return False
    outside_single = _mask_quoted_spans(text, mask_double=False)
    if "$" in outside_single or "`" in outside_single or _CMD_VARIABLE.search(outside_single):
        return True
    if text.startswith(("@", "(")) or _clean_shell_token(text).startswith("~"):
        return True
    return outside_single.count('"') % 2 == 1 or _mask_quoted_spans(text, mask_double=True).count("'") % 2 == 1


def _continues_expression(word: str) -> bool:
    """Whether a word after a leading variable continues a PowerShell expression (c122).

    An operator, an assignment, a member or index access, a redirect, a pipe or foreach's in; never a program argument.
    """
    lowered = word.lower()
    return lowered in _EXPRESSION_OPERATORS or lowered.startswith((".", "[")) or not lowered.strip("=+-*/%?!,.|&<>:")


def _flatten_groups(text: str) -> tuple[str, list[tuple[bool, str]]]:
    """Replace each outermost group outside quotes with a placeholder; return the text and each group's body (c122).

    The groups are PowerShell's (...), $(...), @(...), @{...} and { ... } and the POSIX subshell, brace group, command
    substitution and array value list. Quotes are followed inside a group, so a quoted bracket neither opens nor closes
    one; ${...} is a variable, not a group; a backtick outside single quotes escapes the next character (PowerShell's
    escape). A group left open runs to the end of the text. Each body comes with whether its words are values only (a
    POSIX array's list, name=(...)); every other body runs as commands.
    """
    out: list[str] = []
    groups: list[tuple[bool, str]] = []
    quote: str | None = None
    depth = 0
    opened = 0
    values = False
    placeholder = ""
    index = 0
    while index < len(text):
        char = text[index]
        if char == "`" and quote != "'":
            if depth == 0:
                out.append(text[index : index + 2])
            index += 2
            continue
        if quote is not None:
            quote = None if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char == "{" and index and text[index - 1] == "$":
            close = text.find("}", index)
            end = len(text) if close < 0 else close + 1
            if depth == 0:
                out.append(text[index:end])
            index = end
            continue
        elif char in "({":
            if depth == 0:
                prefix = out[-1] if out and out[-1] in ("$", "@") else ""
                if prefix:
                    out.pop()
                values = not prefix and char == "(" and _BASH_ARRAY_ASSIGNMENT.search("".join(out)) is not None
                if prefix == "$":
                    placeholder = _SUBEXPRESSION_PLACEHOLDER
                elif char == "{" and not prefix:
                    placeholder = _BLOCK_PLACEHOLDER
                else:
                    placeholder = _GROUP_PLACEHOLDER
                opened = index
            depth += 1
            index += 1
            continue
        elif char in ")}" and depth:
            depth -= 1
            if depth == 0:
                groups.append((values, text[opened + 1 : index]))
                out.append(placeholder)
            index += 1
            continue
        if depth == 0:
            out.append(char)
        index += 1
    if depth:
        groups.append((values, text[opened + 1 :]))
        out.append(placeholder)
    return "".join(out), groups


def _split_statements(text: str) -> list[str]:
    """The statements of a flattened command (c122): split at newlines, ;, |, ||, && and a single & outside quotes.

    A redirection's & (2>&1, >&2, &>file) does not split; a leading & is PowerShell's call operator and stays with its
    statement; a backtick (PowerShell's escape) keeps the next character, so a continued line stays one statement.
    Unlike _split_command_stages, a separator inside double quotes never splits: no shell runs it.
    """
    statements: list[str] = []
    quote: str | None = None
    start = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char == "`" and quote != "'":
            index += 2
            continue
        if quote is not None:
            quote = None if char == quote else quote
            index += 1
            continue
        if char in "'\"":
            quote = char
            index += 1
            continue
        following = text[index + 1 : index + 2]
        width = 0
        if char in "\r\n;":
            width = 1
        elif char == "|":
            width = 2 if following == "|" else 1
        elif char == "&":
            preceding = text[index - 1 : index]
            if following == "&":
                width = 2
            elif preceding not in ("<", ">", "|") and following != ">" and text[start:index].strip():
                width = 1
        if width:
            statements.append(text[start:index])
            start = index = index + width
            continue
        index += 1
    statements.append(text[start:])
    return [statement.strip() for statement in statements if statement.strip()]


def _statement_program(tokens: list[str]) -> tuple[list[str], bool]:
    """A statement's words from its program on, and whether a call operator runs it (c122).

    The POSIX keywords that lead a stage (if, elif, while, until, do, then, else, !), environment assignments
    (NAME=value) and the call operators (&, ., call) come off. A PowerShell assignment ($x = ..., $x=...) stays: it is
    an expression whose value runs.
    """
    words = list(tokens)
    called = False
    while words:
        word = words[0]
        if word in ("&", ".") or word.lower() == "call":
            called = True
        elif word.lower() not in _POSIX_KEYWORDS and not _ENV_ASSIGNMENT.match(word):
            break
        words = words[1:]
    return words, called


def _handed_argument(words: list[str]) -> str:
    """The first word a nested shell is handed after its command flag, as the outer shell sees it (c122)."""
    flags = _HANDING_FLAGS["cmd"] | _HANDING_FLAGS["powershell"] | _HANDING_FLAGS["posix"]
    for index, word in enumerate(words[1:], start=1):
        if _clean_shell_token(word).lower() in flags:
            return words[index + 1] if index + 1 < len(words) else ""
    return ""


def _evaluated_argument(words: list[str]) -> str:
    """The first word Invoke-Expression evaluates, as the outer shell sees it (c122)."""
    return next((word for word in words[1:] if not (word.startswith("-") and "-command".startswith(word.lower()))), "")


# c122: the options each launcher takes before the command it runs, as (options with a value, flags). An option outside
# a launcher's table fails closed (UNINSPECTABLE_SHELL_COMMAND): a misread value could hide the command.
_POSIX_LAUNCHERS: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    "env": (
        frozenset({"-u", "--unset", "-C", "--chdir"}),
        frozenset(
            {
                "-",
                "-i",
                "--ignore-environment",
                "-0",
                "--null",
                "-v",
                "--debug",
                "--block-signal",
                "--default-signal",
                "--ignore-signal",
                "--list-signal-handling",
                "--help",
                "--version",
            }
        ),
    ),
    "time": (
        frozenset({"-f", "--format", "-o", "--output"}),
        frozenset({"-p", "--portability", "-a", "--append", "-v", "--verbose", "-q", "--quiet", "--help", "-V"}),
    ),
    "nohup": (frozenset(), frozenset({"--help", "--version"})),
    "nice": (frozenset({"-n", "--adjustment"}), frozenset({"--help", "--version"})),
    "timeout": (
        frozenset({"-s", "--signal", "-k", "--kill-after"}),
        frozenset({"--preserve-status", "--foreground", "-v", "--verbose", "--help", "--version"}),
    ),
    "stdbuf": (frozenset({"-i", "--input", "-o", "--output", "-e", "--error"}), frozenset({"--help", "--version"})),
    "command": (frozenset(), frozenset({"-p", "-v", "-V"})),
    "exec": (frozenset({"-a"}), frozenset({"-c", "-l"})),
    "builtin": (frozenset(), frozenset()),
    "sudo": (
        frozenset(
            {
                "-u",
                "--user",
                "-g",
                "--group",
                "-C",
                "--close-from",
                "-D",
                "--chdir",
                "-h",
                "--host",
                "-p",
                "--prompt",
                "-r",
                "--role",
                "-t",
                "--type",
                "-T",
                "--command-timeout",
                "-U",
                "--other-user",
                "-R",
                "--chroot",
            }
        ),
        frozenset(
            {
                "-A",
                "--askpass",
                "-b",
                "--background",
                "-B",
                "--bell",
                "-E",
                "--preserve-env",
                "-e",
                "--edit",
                "-H",
                "--set-home",
                "-i",
                "--login",
                "-K",
                "--remove-timestamp",
                "-k",
                "--reset-timestamp",
                "-l",
                "--list",
                "-n",
                "--non-interactive",
                "-N",
                "--no-update",
                "-P",
                "--preserve-groups",
                "-S",
                "--stdin",
                "-s",
                "--shell",
                "-V",
                "--version",
                "-v",
                "--validate",
                "--help",
                "--inline",
                "--new-window",
                "--disable-input",
            }
        ),
    ),
}
_XARGS_VALUES = frozenset(
    {
        "-a",
        "--arg-file",
        "-d",
        "--delimiter",
        "-E",
        "-I",
        "-L",
        "--max-lines",
        "-n",
        "--max-args",
        "-P",
        "--max-procs",
        "-s",
        "--max-chars",
        "--process-slot-var",
    }
)
_XARGS_FLAGS = frozenset(
    {
        "-0",
        "--null",
        "-p",
        "--interactive",
        "-r",
        "--no-run-if-empty",
        "-t",
        "--verbose",
        "-x",
        "--exit",
        "-o",
        "--open-tty",
        "--show-limits",
        "--help",
        "--version",
        "-e",
        "--eof",
        "-i",
        "--replace",
        "-l",
    }
)
# xargs -e, -i and -l take an optional value, attached only (-eEND, -i{}, -l5).
_XARGS_ATTACHED = frozenset({"-e", "-i", "-l"})
_UV_GLOBAL_VALUES = frozenset(
    {
        "--color",
        "--directory",
        "--project",
        "--config-file",
        "--cache-dir",
        "--python-preference",
        "--allow-insecure-host",
    }
)
_UV_GLOBAL_FLAGS = frozenset(
    {
        "-q",
        "--quiet",
        "-v",
        "--verbose",
        "--native-tls",
        "--offline",
        "--no-progress",
        "--no-config",
        "-n",
        "--no-cache",
        "--managed-python",
        "--no-managed-python",
        "--no-python-downloads",
        "--preview",
        "--no-preview",
        "-h",
        "--help",
        "-V",
        "--version",
    }
)
_UV_RESOLVER_VALUES = frozenset(
    {
        "--with",
        "-w",
        "--with-editable",
        "--with-requirements",
        "--python",
        "-p",
        "--index",
        "--default-index",
        "--index-url",
        "-i",
        "--extra-index-url",
        "--find-links",
        "-f",
        "--index-strategy",
        "--keyring-provider",
        "--resolution",
        "--prerelease",
        "--exclude-newer",
        "--link-mode",
        "--config-setting",
        "-C",
        "--refresh-package",
        "--reinstall-package",
        "--upgrade-package",
        "-P",
        "--python-platform",
    }
)
_UV_RESOLVER_FLAGS = frozenset(
    {
        "--isolated",
        "--upgrade",
        "-U",
        "--reinstall",
        "--refresh",
        "--no-build-isolation",
        "--no-build",
        "--no-binary",
        "--compile-bytecode",
        "--no-sources",
        "--no-index",
    }
)
_UV_RUN_VALUES = (
    _UV_GLOBAL_VALUES
    | _UV_RESOLVER_VALUES
    | frozenset({"--env-file", "--extra", "--no-extra", "--group", "--only-group", "--no-group", "--package"})
)
_UV_RUN_FLAGS = (
    _UV_GLOBAL_FLAGS
    | _UV_RESOLVER_FLAGS
    | frozenset(
        {
            "--frozen",
            "--locked",
            "--no-sync",
            "--no-project",
            "--active",
            "--no-active",
            "--all-extras",
            "--no-dev",
            "--dev",
            "--only-dev",
            "--no-default-groups",
            "--all-groups",
            "--all-packages",
            "--exact",
            "--inexact",
            "--no-editable",
            "--script",
            "-s",
            "--gui-script",
            "--no-env-file",
            "-m",
            "--module",
        }
    )
)
_UVX_VALUES = _UV_GLOBAL_VALUES | _UV_RESOLVER_VALUES | frozenset({"--from"})
_UVX_FLAGS = _UV_GLOBAL_FLAGS | _UV_RESOLVER_FLAGS
_PIPX_RUN_VALUES = frozenset({"--spec", "--python", "--pip-args", "--index-url", "-i", "--preinstall", "--backend"})
_PIPX_RUN_FLAGS = frozenset(
    {
        "--no-cache",
        "--path",
        "--pypackages",
        "--verbose",
        "-v",
        "--quiet",
        "-q",
        "--system-site-packages",
        "-h",
        "--help",
    }
)
_START_PROCESS_PARAMETERS = {
    "filepath": "file",
    "argumentlist": "arguments",
    "workingdirectory": "value",
    "verb": "value",
    "windowstyle": "value",
    "credential": "value",
    "redirectstandardoutput": "value",
    "redirectstandarderror": "value",
    "redirectstandardinput": "value",
    "environment": "value",
    "erroraction": "value",
    "warningaction": "value",
    "informationaction": "value",
    "progressaction": "value",
    "errorvariable": "value",
    "warningvariable": "value",
    "informationvariable": "value",
    "outvariable": "value",
    "outbuffer": "value",
    "pipelinevariable": "value",
    "wait": "switch",
    "nonewwindow": "switch",
    "passthru": "switch",
    "loaduserprofile": "switch",
    "usenewenvironment": "switch",
    "verbose": "switch",
    "debug": "switch",
    "whatif": "switch",
    "confirm": "switch",
}
_START_PROCESS_ALIASES = {
    "path": "filepath",
    "pspath": "filepath",
    "args": "argumentlist",
    "rso": "redirectstandardoutput",
    "rse": "redirectstandarderror",
    "rsi": "redirectstandardinput",
    "lup": "loaduserprofile",
    "nnw": "nonewwindow",
    "ea": "erroraction",
    "wa": "warningaction",
    "infa": "informationaction",
    "proga": "progressaction",
    "ev": "errorvariable",
    "wv": "warningvariable",
    "iv": "informationvariable",
    "ov": "outvariable",
    "ob": "outbuffer",
    "pv": "pipelinevariable",
    "vb": "verbose",
    "db": "debug",
    "wi": "whatif",
    "cf": "confirm",
}


def _launch_operands(
    args: list[str], values: frozenset[str], flags: frozenset[str], attached: frozenset[str] = frozenset()
) -> tuple[list[str], set[str]] | None:
    """The words after a launcher's own options and the options seen; None for an option outside its table (c122).

    A short option may carry its value attached (-n5) or bundle flags (-it); attached lists the short options whose
    value is optional and attached only (xargs -e, -i, -l). -- ends the options.
    """
    seen: set[str] = set()
    index = 0
    while index < len(args):
        word = _clean_shell_token(args[index])
        if word == "--":
            return args[index + 1 :], seen
        if not word.startswith("-") or (word == "-" and word not in flags):
            return args[index:], seen
        name, separator, _value = word.partition("=")
        if name in values:
            index += 1 if separator else 2
        elif name in flags or (
            not word.startswith("--")
            and (word[:2] in values | attached or all(f"-{letter}" in flags for letter in word[1:]))
        ):
            index += 1
        else:
            return None
        seen.add(name if name in values | flags else word[:2])
    return [], seen


def _start_process_parameter(word: str) -> str | None:
    """The Start-Process parameter a -Name word binds: by name, alias or unambiguous prefix; None when unknown."""
    name = word[1:].lower()
    if name in _START_PROCESS_PARAMETERS:
        return name
    if name in _START_PROCESS_ALIASES:
        return _START_PROCESS_ALIASES[name]
    matches = {parameter for parameter in _START_PROCESS_PARAMETERS if parameter.startswith(name)}
    matches |= {parameter for alias, parameter in _START_PROCESS_ALIASES.items() if alias.startswith(name)}
    return matches.pop() if name and len(matches) == 1 else None


def _split_commas(text: str) -> list[str]:
    """Split an array argument at the commas outside quotes (c122)."""
    parts: list[str] = []
    quote: str | None = None
    start = 0
    for index, char in enumerate(text):
        if quote is not None:
            quote = None if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char == ",":
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return [part.strip() for part in parts if part.strip()]


def _argument_list(words: list[str], index: int) -> tuple[str, int]:
    """The command line a Start-Process argument list hands its program, and the index after it (c122).

    An array argument (a, b or 'a', 'b') continues across the words its commas join; PowerShell passes its elements
    joined with spaces, without quoting them.
    """
    collected = [words[index]]
    index += 1
    while index < len(words) and (collected[-1].endswith(",") or words[index].startswith(",")):
        collected.append(words[index])
        index += 1
    return " ".join(_unquote_once(element) for element in _split_commas(" ".join(collected))), index


def _start_process_commands(name: str, args: list[str]) -> list[str]:
    """The commands Start-Process (saps, start) runs and, for start, cmd's start (c122).

    PowerShell binds -FilePath (or the first operand) and -ArgumentList (or the second), also as -Name:value. cmd's
    start takes its switches (/b, /wait, /min, /d <path>, ...), then a window title when the first operand is double
    quoted, then the command. A parameter Start-Process does not know fails closed; start is also cmd's built-in, so
    there an unknown parameter only drops the PowerShell reading.
    """
    commands: list[str] = []
    if name == "start":
        operands = list(args)
        while operands and operands[0].startswith("/"):
            operands = operands[2:] if operands[0].lower() in ("/d", "/node", "/affinity") else operands[1:]
        if operands:
            commands.append(" ".join(operands))
            if operands[0].startswith('"'):
                commands.append(" ".join(operands[1:]))
    unreadable = commands if name == "start" else [UNINSPECTABLE_SHELL_COMMAND]
    file: str | None = None
    arguments: str | None = None
    index = 0
    while index < len(args):
        word = args[index]
        if word.startswith("-") and len(word) > 1 and not word[1].isdigit():
            head, colon, tail = word.partition(":")
            parameter = _start_process_parameter(head)
            kind = _START_PROCESS_PARAMETERS.get(parameter) if parameter else None
            if kind is None:
                return unreadable
            if kind == "switch" or (kind == "value" and colon):
                index += 1
            elif colon and kind == "file":
                file = tail
                index += 1
            elif colon:
                arguments, used = _argument_list([tail, *args[index + 1 :]], 0)
                index += used
            elif index + 1 >= len(args):
                index += 1
            elif kind == "arguments":
                arguments, index = _argument_list(args, index + 1)
            else:
                file = args[index + 1] if kind == "file" else file
                index += 2
        elif file is None:
            file = word
            index += 1
        elif arguments is None:
            arguments, index = _argument_list(args, index)
        else:
            return unreadable
    if file is not None:
        commands.append(f"{file} {arguments}" if arguments else file)
    return commands


def _package_runner_commands(name: str, args: list[str]) -> list[str]:
    """The command uv run, uv tool run, uvx or pipx run runs (c122); none for their other subcommands."""
    if name == "uv":
        parsed = _launch_operands(args, _UV_GLOBAL_VALUES, _UV_GLOBAL_FLAGS)
        if parsed is None:
            return [UNINSPECTABLE_SHELL_COMMAND]
        rest = parsed[0]
        subcommand = [_clean_shell_token(word).lower() for word in rest[:2]]
        if subcommand[:1] == ["run"]:
            options, values, flags = rest[1:], _UV_RUN_VALUES, _UV_RUN_FLAGS
        elif subcommand == ["tool", "run"]:
            options, values, flags = rest[2:], _UVX_VALUES, _UVX_FLAGS
        else:
            return []
    elif name == "uvx":
        options, values, flags = args, _UVX_VALUES, _UVX_FLAGS
    elif [_clean_shell_token(word).lower() for word in args[:1]] == ["run"]:
        options, values, flags = args[1:], _PIPX_RUN_VALUES, _PIPX_RUN_FLAGS
    else:
        return []
    parsed = _launch_operands(options, values, flags)
    if parsed is None:
        return [UNINSPECTABLE_SHELL_COMMAND]
    operands, seen = parsed
    if not operands:
        return []
    # uv run -m (--module) runs a module as python -m does.
    return [("python -m " if seen & {"-m", "--module"} else "") + " ".join(operands)]


def _find_exec_commands(args: list[str]) -> list[str]:
    """The commands find runs through -exec, -execdir, -ok and -okdir, each {} an unresolved operand (c122)."""
    commands: list[str] = []
    index = 0
    while index < len(args):
        if _clean_shell_token(args[index]).lower() not in ("-exec", "-execdir", "-ok", "-okdir"):
            index += 1
            continue
        end = index + 1
        while end < len(args) and _clean_shell_token(args[end]) not in (";", "\\;", "+"):
            end += 1
        words = [
            _UNRESOLVED_OPERAND if "{}" in _clean_shell_token(word) or word.startswith(_BLOCK_PLACEHOLDER) else word
            for word in args[index + 1 : end]
        ]
        if words:
            commands.append(" ".join(words))
        index = end + 1
    return commands


def _launched_commands(words: list[str]) -> list[str] | None:
    """The command lines a launcher statement runs (c122; batch design WP1, W); None when its program is no launcher.

    Start-Process (saps, start) and cmd's start; uv run, uv tool run, uvx and pipx run; env, time, nohup, nice,
    timeout, stdbuf, command, exec, builtin and sudo; xargs, whose input item is an unresolved operand; and find's
    -exec, -execdir, -ok and -okdir, whose {} is unresolved. UNINSPECTABLE_SHELL_COMMAND stands for an option a
    launcher's table does not know.
    """
    name = _executable_name(words[0]).removesuffix(".exe")
    args = words[1:]
    if name in ("start-process", "saps", "start"):
        return _start_process_commands(name, args)
    if name in ("uv", "uvx", "pipx"):
        return _package_runner_commands(name, args)
    if name == "find":
        return _find_exec_commands(args)
    if name == "xargs":
        parsed = _launch_operands(args, _XARGS_VALUES, _XARGS_FLAGS, _XARGS_ATTACHED)
        if parsed is None:
            return [UNINSPECTABLE_SHELL_COMMAND]
        return [" ".join([*(parsed[0] or ["echo"]), _UNRESOLVED_OPERAND])]
    if name not in _POSIX_LAUNCHERS:
        return None
    if name == "nice" and args and re.fullmatch(r"-\d+", _clean_shell_token(args[0])):
        args = args[1:]
    parsed = _launch_operands(args, *_POSIX_LAUNCHERS[name])
    if parsed is None:
        return [UNINSPECTABLE_SHELL_COMMAND]
    operands, seen = parsed
    if name == "command" and seen & {"-v", "-V"}:
        return []  # command -v and -V look a name up; nothing runs
    if name == "env":
        while operands and _ENV_ASSIGNMENT.match(operands[0]):
            operands = operands[1:]
    if name == "timeout":
        operands = operands[1:]  # the duration
    return [" ".join(operands)] if operands else []


def _walked_commands(
    command: str,
    *,
    strict: bool = False,
    values: bool = False,
    powershell: bool = False,
    _depth: int = 0,
    _nesting: int = 0,
) -> list[tuple[str, str]]:
    """Every command line a shell command runs, each with the text it was found in (c122; batch design WP1, W).

    A line starts at its program, named literally: the POSIX keywords, environment assignments and call operators
    (&, ., call) before it are removed. Each statement's line, the command a nested shell or Invoke-Expression is
    handed, the command a launcher runs, the body of each group and each $(...) inside a double-quoted string are
    walked in turn. UNINSPECTABLE_SHELL_COMMAND stands for a command the walk cannot read: encoded, empty or unparsable
    handed text, text Invoke-Expression reads from its pipeline, nesting past _INNER_COMMAND_DEPTH (shells, evaluation
    and launchers) or _GROUP_DEPTH (groups), a launcher option the gate does not know, or a program named by a variable
    or an expression. strict marks text whose program position runs whatever it holds (text a POSIX shell or cmd runs,
    text the outer shell expands first, a launched command): a variable there names a program even standing alone.
    values marks a POSIX array's list, whose words are values: only the groups inside it run. powershell marks text
    known to be PowerShell (an assignment's value, text handed to PowerShell or Invoke-Expression), where a statement
    led by a quoted string is an expression, not a program.
    """
    if _depth > _INNER_COMMAND_DEPTH or _nesting > _GROUP_DEPTH:
        return [(UNINSPECTABLE_SHELL_COMMAND, command)]
    flat, groups = _flatten_groups(command)
    found: list[tuple[str, str]] = []
    if not values:
        for statement in _split_statements(flat):
            found.extend(
                _statement_commands(
                    statement, text=command, strict=strict, powershell=powershell, _depth=_depth, _nesting=_nesting
                )
            )
    for only_values, body in groups:
        found.extend(
            _walked_commands(
                body, strict=strict, values=only_values, powershell=powershell, _depth=_depth, _nesting=_nesting + 1
            )
        )
    for body in _string_subexpressions(flat):
        found.extend(_walked_commands(body, strict=strict, powershell=powershell, _depth=_depth, _nesting=_nesting + 1))
    return found


def _statement_commands(
    statement: str, *, text: str, strict: bool, powershell: bool, _depth: int, _nesting: int
) -> list[tuple[str, str]]:
    """The command lines one flattened statement of text runs: its own line and what it hands on (c122)."""
    found: list[tuple[str, str]] = []
    cut = _mask_quoted_spans(statement, mask_double=True).rfind(")")
    if cut >= 0 and statement[cut + 1 :].strip():
        # A POSIX case pattern ends at a parenthesis the statement never opened (case $x in a) ...); its command runs.
        found.extend(_walked_commands(statement[cut + 1 :], strict=strict, _depth=_depth, _nesting=_nesting + 1))
    tokens = _shell_split(statement)
    if tokens is None:
        # Handed text that does not parse cannot be inspected; a typed line no shell parses does not run.
        return found + ([(UNINSPECTABLE_SHELL_COMMAND, text)] if _depth else [])
    words, called = _statement_program(tokens)
    if not words or words[0].startswith(_BLOCK_PLACEHOLDER):
        return found  # nothing runs, or a script block or brace group, whose body is walked as a group
    program = words[0]
    if powershell and not called and program[:1] in ("'", '"'):
        return found  # a PowerShell string expression; the groups inside it are walked as groups
    group_led = program.startswith(_GROUP_PLACEHOLDER)
    if group_led or _unresolved_value(program):
        attached = None if group_led else _POWERSHELL_ATTACHED_ASSIGNMENT.fullmatch(program)
        expression = not called and (
            group_led
            or (
                not strict
                and (
                    attached is not None or len(words) == 1 or program.endswith(",") or _continues_expression(words[1])
                )
            )
        )
        if not expression:
            return [*found, (UNINSPECTABLE_SHELL_COMMAND, text)]
        # A PowerShell expression: a variable read, a comparison, an assignment or foreach's in. The pipeline after an
        # assignment or an in runs.
        rest: list[str] = []
        if attached is not None:
            rest = [attached.group("value"), *words[1:]]
        else:
            for index, word in enumerate(words[1:], start=1):
                if word in _ASSIGNMENT_OPERATORS or word.lower() == "in":
                    rest = words[index + 1 :]
                    break
        if rest:
            found.extend(
                _walked_commands(" ".join(rest), strict=strict, powershell=True, _depth=_depth, _nesting=_nesting + 1)
            )
        return found
    line = " ".join(words)
    found.append((line, text))
    handed, recognized = _handed_command(line)
    if recognized:
        if not handed:
            found.append((UNINSPECTABLE_SHELL_COMMAND, text))
        else:
            shell = _executable_name(words[0])
            if shell in _CMD_SHELL_NAMES:
                handed = handed.replace("'", " ")  # cmd does not treat single quotes as quotes
            inner_powershell = shell in _POWERSHELL_NAMES
            literal = inner_powershell and _handed_argument(words).startswith("'")
            found.extend(
                _walked_commands(
                    handed, strict=not literal, powershell=inner_powershell, _depth=_depth + 1, _nesting=_nesting
                )
            )
    if _executable_name(words[0]) in _EVALUATING_VERBS:
        evaluated = _handed_evaluation(line)
        if evaluated is None:
            # Invoke-Expression without text evaluates what its pipeline sends it.
            found.append((UNINSPECTABLE_SHELL_COMMAND, text))
        else:
            literal = _evaluated_argument(words).startswith("'")
            found.extend(
                _walked_commands(evaluated, strict=not literal, powershell=True, _depth=_depth + 1, _nesting=_nesting)
            )
    for launched in _launched_commands(words) or []:
        if launched == UNINSPECTABLE_SHELL_COMMAND:
            found.append((UNINSPECTABLE_SHELL_COMMAND, text))
        else:
            found.extend(_walked_commands(launched, strict=True, _depth=_depth + 1, _nesting=_nesting))
    return found


def _direct_git_effect(stage: str, *, _depth: int = 0) -> str | None:
    """Name the direct Git effect a shell command performs, in any command the line runs (c122: _walked_commands).

    UNINSPECTABLE_SHELL_COMMAND when the walk meets a command it cannot read: the rule fails closed on its own
    (observer B102).
    """
    for line, _text in _walked_commands(stage, _depth=_depth):
        if line == UNINSPECTABLE_SHELL_COMMAND:
            return UNINSPECTABLE_SHELL_COMMAND
        if not _is_direct_git_invocation(line):
            continue
        subcommand = _direct_git_subcommand(line)
        if subcommand not in DIRECT_GIT_READ_ONLY_SUBCOMMANDS and not _git_informational_only(line):
            return subcommand or "<unknown>"
    return None


_GIT_INFORMATIONAL_OPTIONS = frozenset(
    {"--version", "-v", "--help", "-h", "--exec-path", "--html-path", "--man-path", "--info-path"}
)
_REDIRECT_TOKEN = re.compile(r"\d*>{1,2}.*|\d*<.*")


def _git_informational_only(stage: str) -> bool:
    """Return whether a Git invocation runs no subcommand and only reports (`git --version`, `git --help`).

    Redirections (`2>&1`) are not arguments. Any other non-option token is a subcommand or a value, so the
    invocation is judged by the ordinary subcommand rule instead.
    """
    tokens = _shell_split(stage) or []
    words = [_clean_shell_token(token) for token in tokens]
    while words and words[0].lower() in {"&", "call"}:
        words = words[1:]
    if not words or _executable_name(words[0]) not in {"git", "git.exe"}:
        return False
    options = [word for word in words[1:] if not _REDIRECT_TOKEN.fullmatch(word)]
    return (
        bool(options)
        and all(option.startswith("-") for option in options)
        and any(option.split("=", 1)[0].lower() in _GIT_INFORMATIONAL_OPTIONS for option in options)
    )


def _has_direct_git_effect_signal(command: str) -> bool:
    # c122: the walk reaches every command the line runs, its stages among them.
    return _direct_git_effect(command) is not None


def _gt_owner_operation(tokens: list[str]) -> str | None:
    """Name the GT-KB owner operation these tokens run through gt or python -m groundtruth_kb, if any.

    c122: a module, group or action word whose value the shell supplies (a variable, an expression) may name an owner
    operation, so it gives UNINSPECTABLE_SHELL_COMMAND.
    """
    words = [_clean_shell_token(token) for token in tokens]
    executable = _executable_name(words[0])
    index = 1
    if executable in _PYTHON_EXECUTABLE_NAMES or executable.startswith("python"):
        while index < len(words) and words[index].startswith("-") and words[index] != "-m":
            index += 1
        if index + 1 < len(words) and words[index] == "-m" and _unresolved_value(tokens[index + 1]):
            return UNINSPECTABLE_SHELL_COMMAND
        if index + 1 >= len(words) or words[index] != "-m" or words[index + 1] not in GT_MODULES:
            return None
        index += 2
    elif executable not in {"gt", "gt.exe"}:
        return None
    group_and_action: list[str] = []
    while index < len(words) and len(group_and_action) < 2:
        word = words[index]
        if word in GT_GLOBAL_OPTIONS_WITH_VALUES:
            index += 2
            continue
        index += 1
        if not word.startswith("-"):
            if _unresolved_value(tokens[index - 1]):
                return UNINSPECTABLE_SHELL_COMMAND
            group_and_action.append(word.lower())
    if len(group_and_action) == 2 and group_and_action[1] in GT_OWNER_OPERATIONS.get(group_and_action[0], ()):
        return "gt " + " ".join(group_and_action)
    return None


def _service_control_verb(tokens: list[str]) -> str | None:
    """Name the service or scheduled-task change these tokens make, if any; its target is checked separately."""
    words = [_clean_shell_token(token).lower() for token in tokens]
    executable = _executable_name(words[0])
    if executable in SERVICE_CONTROL_CMDLETS:
        return executable
    if executable in {"schtasks", "schtasks.exe"} and SCHTASKS_CHANGING_SWITCHES.intersection(words[1:]):
        return "schtasks"
    if executable in {"sc", "sc.exe"} and len(words) > 1 and words[1] in SC_CHANGING_VERBS:
        return f"sc {words[1]}"
    if executable in {"net", "net.exe", "net1", "net1.exe"} and len(words) > 1 and words[1] in NET_CHANGING_VERBS:
        return f"net {words[1]}"
    return None


def _names_gtkb_task_or_service(command: str) -> bool:
    """True when any argument of the command is a GT-KB task or service name (also as -Name:value or -Name=value)."""
    for token in _shell_split(command, punctuation=True) or []:
        for part in re.split(r"[=:,]", _clean_shell_token(token)):
            if GTKB_TASK_OR_SERVICE_NAME_RE.fullmatch(part.strip("\"'")):
                return True
    return False


def _owner_operation(command: str, *, _depth: int = 0) -> str | None:
    """Name the GT-KB owner operation a shell command performs, in any command the line runs (c122: _walked_commands).

    Like the Git rule, it fails closed on its own (observer B102): a command the walk cannot read returns
    UNINSPECTABLE_SHELL_COMMAND, so this rule's refusal does not depend on the Git rule running first. A service or task
    change counts when the command, or the text the walk found the change in, names a GT-KB task or service.
    """
    names_gtkb = _names_gtkb_task_or_service(command)
    for line, text in _walked_commands(command, _depth=_depth):
        if line == UNINSPECTABLE_SHELL_COMMAND:
            return UNINSPECTABLE_SHELL_COMMAND
        tokens = _shell_split(line)
        if not tokens:
            continue
        found = _gt_owner_operation(tokens)
        if found is not None:
            return found
        verb = _service_control_verb(tokens)
        if verb is not None and (names_gtkb or _names_gtkb_task_or_service(text)):
            return f"{verb} on a GT-KB task or service"
    return None


def _owner_operation_from_payload(payload: dict[str, Any]) -> str | None:
    command = _command_from_payload(payload, _tool_input(payload), _tool_name(payload).lower())
    return _owner_operation(command) if command else None


def _arg_value(args: list[str], flag: str) -> str | None:
    for index, token in enumerate(args):
        if token == flag and index + 1 < len(args):
            return args[index + 1]
        if token.startswith(flag + "="):
            return token.split("=", 1)[1]
    return None


def _redirect_targets(stage: str) -> list[str]:
    tokens = _shell_split(stage, punctuation=True)
    if tokens is None:
        return []
    targets: list[str] = []
    for index, token in enumerate(tokens):
        if REDIRECT_OPERATOR_TOKEN_RE.fullmatch(token):
            if index + 1 < len(tokens):
                targets.append(tokens[index + 1])
            continue
        if (
            re.fullmatch(r"\d+", token)
            and index + 1 < len(tokens)
            and REDIRECT_OPERATOR_TOKEN_RE.fullmatch(tokens[index + 1])
        ):
            if index + 2 < len(tokens):
                targets.append(tokens[index + 2])
    return targets


def _diagnostic_output_paths_for_stage(root: Path, stage: str) -> list[str] | None:
    tokens = _shell_split(stage)
    if tokens is None:
        return None
    invocation = _python_script_invocation(tokens)
    if invocation is None:
        return None
    script_name, args = invocation
    outputs: list[str] = []
    if script_name == "wrap_capture_transcript.py":
        session_id = _arg_value(args, "--session-id")
        if not session_id:
            return None
        snapshot_root = _arg_value(args, "--snapshot-root") or ".groundtruth/session/snapshots"
        snapshot_root = snapshot_root.rstrip("/").rstrip("\\")
        outputs.append(f"{snapshot_root}/{session_id}/manifest.json")
    else:
        report_path = _arg_value(args, "--write-report")
        if report_path:
            outputs.append(report_path)
        outputs.extend(_redirect_targets(stage))
        if not outputs:
            return None
    normalized: list[str] = []
    for output in outputs:
        rel = _normalize(root, output, shell_quoted=True)
        if not rel:
            return None
        normalized.append(rel)
    return sorted(set(normalized))


def _diagnostic_output_paths_from_shell(root: Path, command: str) -> list[str] | None:
    if not command:
        return None
    outputs: list[str] = []
    matched = False
    for stage in _split_pipeline_stages(command):
        stage_outputs = _diagnostic_output_paths_for_stage(root, stage)
        if stage_outputs is None:
            continue
        matched = True
        outputs.extend(stage_outputs)
    if not matched:
        return None
    return sorted(set(outputs))


def _paths_from_shell(root: Path, command: str) -> list[str]:
    """Verb-aware path extraction per DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.

    Tokenize via shlex.split(posix=False), identify the verb (first non-env-prefix
    token), and extract paths ONLY from argument positions semantically meaningful
    to that verb. For pipelines, each stage is tokenized independently. For
    commands NOT matching any verb in the table, returns an empty list; the
    caller's `_has_mutating_signal` check produces the `<unknown-mutating-target>`
    fallback when appropriate.
    """
    paths: list[str] = []
    for stage in _split_pipeline_stages(command or ""):
        try:
            tokens = shlex.split(stage, posix=False)
        except ValueError:
            continue
        # c122: the file git diff, log, show or whatchanged writes through --output.
        for raw in _git_output_targets(tokens) or []:
            rel = _normalize(root, raw, shell_quoted=True)
            if rel:
                paths.append(rel)
        classification = _classify_command_verb(tokens)
        if classification is None:
            continue
        extractor, relevant = classification
        for raw in extractor(relevant):
            rel = _normalize(root, raw, shell_quoted=True)
            if rel:
                paths.append(rel)
    return sorted(set(paths))


# c122 (batch design WP1, item 3's second change): git diff, log, show and whatchanged write the file --output names,
# under the read-only name of their subcommand. Each such call is a write whose target is that file.
_GIT_OUTPUT_SUBCOMMANDS = frozenset({"diff", "log", "show", "whatchanged"})
_GIT_OUTPUT_RE = re.compile(
    r"\bgit(?:\.exe)?\b(?=[^|;&\n]*\b(?:diff|log|show|whatchanged)\b)[^|;&\n]*?(?<!\S)--output(?==|\s|$)",
    re.IGNORECASE,
)


def _git_output_targets(tokens: list[str]) -> list[str] | None:
    """The files git diff, log, show or whatchanged write through --output (c122); None for any other command.

    The tokens are one stage's words. An --output without a value gives an empty list, which no write reads. A value
    keeps the quotes of the word that carried it, so the unresolved-value rule judges it as written.
    """
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    relevant = tokens[verb_index:]
    if _executable_name(relevant[0]) not in {"git", "git.exe"}:
        return None
    index = 1
    while index < len(relevant) and _clean_shell_token(relevant[index]).startswith("-"):
        index += 2 if _clean_shell_token(relevant[index]) in GIT_GLOBAL_OPTIONS_WITH_VALUES else 1
    if index >= len(relevant) or _clean_shell_token(relevant[index]).lower() not in _GIT_OUTPUT_SUBCOMMANDS:
        return None
    targets: list[str] = []
    found = False
    rest = relevant[index + 1 :]
    position = 0
    while position < len(rest):
        word = _clean_shell_token(rest[position])
        if word == "--":
            break
        if word == "--output":
            found = True
            targets.extend(rest[position + 1 : position + 2])
            position += 2
            continue
        if word.startswith("--output="):
            found = True
            raw = rest[position].strip()
            if raw[:1] in ("'", '"') and len(raw) > 1 and raw.endswith(raw[0]):
                # The whole option is quoted: "--output=out dir/x.patch".
                targets.append(raw[0] + raw[1:-1].split("=", 1)[1] + raw[0])
            else:
                value = raw.split("=", 1)[1]
                # A quoted value holding a space spans words that shlex.split(posix=False) breaks apart: join them.
                while (
                    value[:1] in ("'", '"')
                    and (len(value) < 2 or not value.endswith(value[0]))
                    and position + 1 < len(rest)
                ):
                    position += 1
                    value += " " + rest[position].strip()
                if value:
                    targets.append(value)
        position += 1
    return targets if found else None


def _is_safe_command(command: str) -> bool:
    # A safe-command entry authorizes exactly one parsed shell stage. Applying
    # it to the raw command prefix lets a later stage inherit the exemption
    # (for example, ``pytest; Set-Content`` or ``git status; git add``).
    scan_command = _neutralize_heredoc_message_substitutions(command)
    if _has_disqualifying_control_marker(scan_command):
        return False
    # c122 (batch design WP1, item 2's first change): a redirect to a file writes whatever command precedes it, and
    # git's --output writes its file (item 3), so neither is exempt as a read. A null-sink redirect stays a read.
    if _shell_redirect_present(NULL_SINK_REDIRECT_STRIP_RE.sub("", scan_command)):
        return False
    if _GIT_OUTPUT_RE.search(_mask_quoted_spans(scan_command, mask_double=True)):
        return False
    chaining_view = _mask_quoted_spans(scan_command, mask_double=True)
    if any(marker in chaining_view for marker in ("&", "\r", "\n")):
        return False
    stages = _split_pipeline_stages(scan_command)
    if len(stages) != 1:
        return False
    tokens = _shell_split(stages[0])
    if not tokens:
        return False
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return False
    normalized_tokens = [_clean_shell_token(token).lower() for token in tokens[verb_index:]]
    if _requests_help_output_only(scan_command, normalized_tokens):
        return True
    normalized = " ".join(normalized_tokens)
    return any(
        normalized == prefix.strip() or normalized.startswith(prefix.strip() + " ") for prefix in SAFE_COMMAND_PREFIXES
    )


_RUFF_VALUE_OPTIONS = frozenset(
    {
        "--config",
        "--color",
        "--output-format",
        "--target-version",
        "--extension",
        "--select",
        "--ignore",
        "--extend-select",
        "--per-file-ignores",
        "--extend-per-file-ignores",
        "--fixable",
        "--unfixable",
        "--extend-fixable",
        "--exclude",
        "--extend-exclude",
        "--cache-dir",
        "--stdin-filename",
        "--line-length",
        "--range",
        "--output-file",
        "-o",
    }
)
_RUFF_FLAG_OPTIONS = frozenset(
    {
        "--fix",
        "--no-fix",
        "--fix-only",
        "--no-fix-only",
        "--unsafe-fixes",
        "--no-unsafe-fixes",
        "--show-fixes",
        "--no-show-fixes",
        "--diff",
        "--check",
        "--watch",
        "-w",
        "--ignore-noqa",
        "--preview",
        "--no-preview",
        "--statistics",
        "--show-files",
        "--show-settings",
        "--respect-gitignore",
        "--no-respect-gitignore",
        "--force-exclude",
        "--no-force-exclude",
        "--no-cache",
        "-n",
        "--exit-zero",
        "-e",
        "--exit-non-zero-on-fix",
        "--verbose",
        "-v",
        "--quiet",
        "-q",
        "--silent",
        "-s",
        "--isolated",
        "--help",
        "-h",
        "--add-noqa",
    }
)


def _ruff_effects(root: Path, command: str) -> tuple[list[str], bool] | None:
    """Identify Ruff's possible source and report writes without executing it.

    Configuration can enable fixes, so a plain check is not proof of read-only
    behavior. Unknown options or compound commands lack a complete target set.
    Ruff's disposable cache is not reviewed work product.
    """
    stages = _split_pipeline_stages(command)
    for stage in stages:
        nested, wrapper = _nested_shell_command(stage)
        if wrapper:
            if nested and nested != command and _ruff_effects(root, nested) is not None:
                return [], True  # Wrapper environment/cwd is not the supplied tool cwd.
            continue
        tokens = _shell_split(stage)
        if not tokens:
            continue
        verb_index = _shell_verb_index(tokens)
        if verb_index is None:
            continue
        relevant = tokens[verb_index:]
        executable = _executable_name(relevant[0])
        if executable in {"ruff", "ruff.exe"}:
            args = relevant[1:]
        elif (executable in _PYTHON_EXECUTABLE_NAMES or executable.startswith("python")) and relevant[1:3] == [
            "-m",
            "ruff",
        ]:
            args = relevant[3:]
        else:
            continue
        if (
            len(stages) != 1
            or verb_index
            or _has_disqualifying_control_marker(command)
            or _shell_redirect_present(command)
        ):
            return [], True
        if not args or args[0] not in {"check", "format"}:
            return [], True
        subcommand, *args = args
        flags: set[str] = set()
        sources: list[str] = []
        output = os.environ.get("RUFF_OUTPUT_FILE") if subcommand == "check" else None
        output_shell_quoted = False
        index = 0
        while index < len(args):
            token = args[index]
            if token == "--":
                sources.extend(args[index + 1 :])
                break
            option, separator, value = token.partition("=")
            if option in _RUFF_VALUE_OPTIONS:
                if not separator:
                    index += 1
                    if index >= len(args):
                        return [], True
                    value = args[index]
                if option in {"--output-file", "-o"}:
                    output = value
                    output_shell_quoted = True
            elif option in _RUFF_FLAG_OPTIONS and (not separator or option == "--add-noqa"):
                flags.add(option)
            elif token.startswith("-"):
                return [], True
            else:
                sources.append(token)
            index += 1
        if flags & {"--help", "-h"}:
            return [], False
        read_only = "--diff" in flags or (
            "--check" in flags if subcommand == "format" else {"--no-fix", "--no-fix-only"} <= flags
        )
        # Do not infer precedence among conflicting write/read modifiers.
        if "--add-noqa" in flags or ("--diff" not in flags and flags & {"--fix", "--fix-only"}):
            read_only = False
        if not read_only and not sources:
            return [], True  # An implicit recursive '.' is not a concrete artifact.
        targets = [] if read_only else sources
        paths = [_normalize(root, target, shell_quoted=True) for target in targets]
        if output:
            paths.append(_normalize(root, output, shell_quoted=output_shell_quoted))
        concrete_paths: list[str] = []
        for path in paths:
            if not path:
                return [], True
            concrete_paths.append(path)
        return sorted(set(concrete_paths)), bool(concrete_paths)
    return None


# WI-6674: help output is read-only, but the WI-3291 prefix allowlist cannot
# express it. That allowlist enumerates command VERBS, and a help request is
# identified by its FLAG -- the verb is an arbitrary governed CLI. Every such
# invocation therefore fell through to `<unknown-mutating-target>` and was
# denied.
_HELP_ONLY_FLAGS = frozenset({"--help", "--usage"})

# Redirection is checked here rather than inherited: the caller's
# `_has_disqualifying_control_marker` models chaining and command substitution
# but NOT redirection, so `<cli> --help > out.txt` would otherwise write a file
# under a read-only exemption.
_REDIRECTION_MARKERS = (">", ">>")


def _requests_help_output_only(command: str, normalized_tokens: list[str]) -> bool:
    """True iff this single stage only asks a command to print its usage text.

    Deliberately narrow. Only the unambiguous long flags qualify; ``-h`` is
    excluded because it is a real operation modifier for some verbs (``chown
    -h``, ``chmod -h``) and admitting it would exempt genuine mutations.

    Chaining, execution markers, and multi-stage commands are already rejected
    by the caller before this runs, so those guards are inherited rather than
    re-implemented. Redirection is not, and is rejected here.
    """
    if not any(token in _HELP_ONLY_FLAGS for token in normalized_tokens):
        return False
    redirect_view = _mask_quoted_spans(command, mask_double=True)
    return not any(marker in redirect_view for marker in _REDIRECTION_MARKERS)


def _mask_quoted_spans(command: str, *, mask_double: bool) -> str:
    """Return ``command`` with quoted-span interiors replaced by spaces.

    Single-quoted span interiors are always blanked: single quotes make every
    shell metacharacter literal. Double-quoted span interiors are blanked only
    when ``mask_double`` is True -- double quotes make ``;``, ``|``, ``&&`` and
    ``||`` literal, but ``$(`` and backtick still execute inside them, so the
    execution-marker scan must keep double-quoted interiors visible.

    Quote characters are preserved. Backslash escaping is intentionally not
    modeled: a mis-segmented span can only end early and expose more text to
    the scan; it can never hide a structural operator (fail-closed). An
    unbalanced trailing quote blanks to end-of-string; the caller also fails
    closed because shlex.split raises ValueError on an unbalanced quote.
    """
    out: list[str] = []
    quote: str | None = None
    for ch in command:
        if quote is not None:
            blank = quote == "'" or mask_double
            out.append(" " if (blank and ch != quote) else ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        else:
            out.append(ch)
    return "".join(out)


def _has_disqualifying_control_marker(command: str) -> bool:
    """True iff a control marker disqualifies a safe-command prefix.

    ``command`` must already have safe HEREDOC substitutions neutralized.
    Chaining markers (``;``, ``|``, ``&&``, ``||``) count only outside every
    quote; execution markers (``$(``, backtick) count outside single quotes,
    including inside double quotes where they still execute.
    """
    chaining_view = _mask_quoted_spans(command, mask_double=True)
    if any(marker in chaining_view for marker in GIT_FINALIZATION_CHAINING_MARKERS):
        return True
    execution_view = _mask_quoted_spans(command, mask_double=False)
    return any(marker in execution_view for marker in GIT_FINALIZATION_EXECUTION_MARKERS)


def _find_heredoc_message_substitution_spans(command: str) -> list[tuple[int, int]]:
    """Return [start, end) spans of provably-safe ``$(cat <<'DELIM' ... DELIM)``
    command substitutions.

    A span is recognized only when EVERY boundary is validated:

    - the opener is ``$(cat <<['"]DELIM['"]`` -- the only command is read-only
      ``cat``, and the delimiter is quoted, so the heredoc body is literal;
    - the opener-line tail (between the quoted delimiter and the body's first
      newline) is whitespace-only -- a shell can place a redirect, separator,
      or pipeline there and it would execute;
    - the heredoc body ends at the FIRST line equal to DELIM (``^DELIM$``, or
      ``^\\t*DELIM$`` for the ``<<-`` form, which strips leading tabs) --
      exactly where a POSIX shell terminates the heredoc;
    - that first delimiter line is followed by optional whitespace and then the
      closing ``)`` of the substitution.

    Any deviation fails closed: the span is NOT returned and the ``$(`` stays
    visible to the control-marker scan. A recognized span runs only read-only
    ``cat`` over a literal (quoted-delimiter) heredoc body.
    """
    spans: list[tuple[int, int]] = []
    search_from = 0
    while True:
        opener = _HEREDOC_OPENER_RE.search(command, search_from)
        if opener is None:
            break
        # The heredoc body begins on the line AFTER the opener. The opener-line
        # tail -- between the quoted delimiter and that line break -- must be
        # whitespace-only; a redirect / separator / pipeline there executes.
        body_start = command.find("\n", opener.end())
        if body_start == -1 or command[opener.end() : body_start].strip():
            search_from = opener.end()
            continue
        body_start += 1
        prefix = r"\t*" if opener.group("dash") else ""
        delim_line_re = re.compile(rf"^{prefix}{re.escape(opener.group('delim'))}$", re.MULTILINE)
        delim_line = delim_line_re.search(command, body_start)
        if delim_line is None:
            search_from = opener.end()
            continue
        rest = command[delim_line.end() :]
        after_ws = rest.lstrip()
        if after_ws.startswith(")"):
            close = delim_line.end() + (len(rest) - len(after_ws)) + 1
            spans.append((opener.start(), close))
            search_from = close
        else:
            search_from = opener.end()
    return spans


def _neutralize_heredoc_message_substitutions(command: str) -> str:
    """Blank each provably-safe ``$(cat <<'DELIM' ... DELIM)`` substitution span.

    A recognized span runs only read-only ``cat`` over a quoted-delimiter
    heredoc body (literal text), so it is side-effect-free and is removed
    before the control-marker scan. Text that does not match the recognized
    shape is left intact and stays subject to the full scan (fail closed).
    """
    spans = _find_heredoc_message_substitution_spans(command)
    if not spans:
        return command
    out: list[str] = []
    cursor = 0
    for start, end in spans:
        out.append(command[cursor:start])
        out.append(" " * (end - start))
        cursor = end
    out.append(command[cursor:])
    return "".join(out)


def _clean_shell_token(token: str) -> str:
    return token.strip().strip("'\"")


def _shell_redirect_present(command: str) -> bool:
    """True when a shell redirection operator token (`>`, `>>`, `&>`, `&>>`)
    appears as a standalone token.

    Tokenizes with a punctuation-aware shlex scan so a `>` inside a quoted
    argument or an embedded Python expression -- a comparison, a `->` return
    arrow, a `:>` format spec, or a `>>` shift -- is not misread as a redirect:
    a quoted span tokenizes as a single token and never exposes a bare operator
    token. A parse failure (unbalanced quotes) falls back conservatively to
    non-redirect; the named-command alternatives in MUTATING_COMMAND_RE remain
    the other mutating signal in that case.
    """
    if not command:
        return False
    lexer = shlex.shlex(command, posix=False, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return any(REDIRECT_OPERATOR_TOKEN_RE.fullmatch(token) for token in lexer)
    except ValueError:
        return False


def _python_call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _constant_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _open_call_uses_write_mode(node: ast.Call) -> bool:
    mode: str | None = None
    if len(node.args) >= 2:
        mode = _constant_string(node.args[1])
    for keyword in node.keywords:
        if keyword.arg == "mode":
            mode = _constant_string(keyword.value)
            break
    return mode is not None and "w" in mode


# c121 (M13 GTKB Home, Q1 on c120; owner "All forms found"): the Python calls that write a file or directory. Before
# c121 only write_text, open(..., "w...") and the insert_/update_/delete_ calls were writes, so append mode, write_bytes
# and the os, shutil and pathlib file operations passed as reads.
_PYTHON_PATH_WRITE_METHODS = frozenset(
    {
        "write_text",
        "write_bytes",
        "touch",
        "mkdir",
        "rmdir",
        "unlink",
        "symlink_to",
        "hardlink_to",
        "chmod",
        "lchmod",
        "extractall",
        "urlretrieve",
    }
)
_PYTHON_MODULE_WRITES = {
    "os": frozenset(
        {
            "remove",
            "unlink",
            "rename",
            "renames",
            "replace",
            "rmdir",
            "removedirs",
            "mkdir",
            "makedirs",
            "link",
            "symlink",
            "chmod",
            "chown",
            "lchown",
            "truncate",
            "utime",
            "mkfifo",
            "mknod",
        }
    ),
    "shutil": frozenset(
        {
            "copy",
            "copy2",
            "copyfile",
            "copytree",
            "copymode",
            "copystat",
            "move",
            "rmtree",
            "make_archive",
            "unpack_archive",
            "chown",
        }
    ),
}
# Module-level open functions take the path first and the mode second; a path object's open() takes the mode first.
_PYTHON_OPEN_MODULES = frozenset({"io", "codecs", "gzip", "bz2", "lzma", "builtins", "tarfile"})
_PYTHON_OS_OPEN_WRITE_FLAGS = frozenset({"O_WRONLY", "O_RDWR", "O_CREAT", "O_APPEND", "O_TRUNC"})
# A file mode ("a", "wb", "r+", tarfile's "w:gz"); any other string (a URL, a file name) is not one.
_PYTHON_FILE_MODE_RE = re.compile(r"[rwxabtU+]{1,4}(?::\w*)?")


def _python_write_mode(node: ast.AST | None) -> bool:
    mode = _constant_string(node) if node is not None else None
    return (
        mode is not None and _PYTHON_FILE_MODE_RE.fullmatch(mode) is not None and any(flag in mode for flag in "wax+")
    )


def _python_call_writes(node: ast.Call) -> bool:
    """Whether one Python call writes a file or directory (c121)."""
    func = node.func
    name = _python_call_name(func)
    if name is None:
        return False
    receiver = func.value.id if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) else None
    if name == "open" and receiver == "os":
        return any(
            (child.attr if isinstance(child, ast.Attribute) else child.id) in _PYTHON_OS_OPEN_WRITE_FLAGS
            for argument in node.args[1:]
            for child in ast.walk(argument)
            if isinstance(child, ast.Attribute | ast.Name)
        )
    if name in ("open", "ZipFile"):
        for keyword in node.keywords:
            if keyword.arg == "mode":
                return _python_write_mode(keyword.value)
        method_open = name == "open" and isinstance(func, ast.Attribute) and receiver not in _PYTHON_OPEN_MODULES
        index = 0 if method_open else 1
        return len(node.args) > index and _python_write_mode(node.args[index])
    if name.startswith(("insert_", "update_", "delete_")):
        return True
    if receiver in _PYTHON_MODULE_WRITES:
        return name in _PYTHON_MODULE_WRITES[receiver]
    if name in _PYTHON_PATH_WRITE_METHODS:
        return True
    # A path's rename(target) or replace(target) takes one argument; str.replace takes two.
    return (
        isinstance(func, ast.Attribute) and name in ("rename", "replace") and len(node.args) == 1 and not node.keywords
    )


def _python_c_sources(command: str) -> list[str]:
    """Every source the command hands to python -c, wherever the call sits in the line (c121).

    _python_c_source reads only a command that starts with the interpreter, split as a POSIX shell splits it, so a
    python -c after Set-Location, a separator or a Windows path to the interpreter was not read. The line is split both
    ways here (a POSIX split drops a Windows path's backslashes; a Windows split keeps a source's quotes, removed once).
    """
    sources: list[str] = []
    first = _python_c_source(command)
    if first is not None:
        sources.append(first)
    for posix in (False, True):
        try:
            tokens = shlex.split(command, posix=posix)
        except ValueError:
            continue
        for index, token in enumerate(tokens):
            name = _executable_name(token).removesuffix(".exe")
            if not (name.startswith("python") or name == "py"):
                continue
            offset = index + 1
            while offset < len(tokens) and offset <= index + 6:
                option = _clean_shell_token(tokens[offset])
                if option == "-c":
                    if offset + 1 < len(tokens):
                        source = tokens[offset + 1] if posix else _unquote_once(tokens[offset + 1])
                        if source not in sources:
                            sources.append(source)
                    break
                if not option.startswith("-"):
                    break
                offset += 2 if option in ("-X", "-W") else 1
    return sources


def _has_python_mutating_signal(command: str) -> bool:
    if _classify_python_sqlite_read_ast(command) is False:
        return True
    for source in _python_c_sources(command):
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        if any(_python_call_writes(node) for node in ast.walk(tree) if isinstance(node, ast.Call)):
            return True
    return False


def _has_mutating_signal(command: str) -> bool:
    """True when the command carries a mutating signal: a named mutating
    command (MUTATING_COMMAND_RE) or a standalone shell redirect operator
    token (_shell_redirect_present)."""
    shell_view = _mask_quoted_spans(command, mask_double=True)
    return (
        MUTATING_COMMAND_RE.search(shell_view) is not None
        # c121: every named write command of the verb tables, and the .NET write calls.
        or _NAMED_WRITE_RE.search(shell_view) is not None
        or _DOTNET_WRITE_RE.search(shell_view) is not None
        # c122: git diff, log, show and whatchanged with --output.
        or _GIT_OUTPUT_RE.search(shell_view) is not None
        or _has_direct_git_effect_signal(command)
        or _has_python_mutating_signal(command)
        or _shell_redirect_present(command)
    )


def _all_mutating_signal_is_null_sink_redirect(command: str) -> bool:
    """True iff the only mutating signal in the command is one or more null-sink redirects.

    Strips null-sink redirect tokens (e.g. ``2>/dev/null``, ``2>$null``, ``2>NUL``,
    ``&>/dev/null``) from the command and re-tests the residue with
    _has_mutating_signal. If the original command had a mutating signal but the
    stripped residue does not, the only mutating signal was a null-sink
    redirect — those are diagnostic suppression, not file mutation, and the
    command is exempt from the gate. Real-file redirects survive the strip and
    keep _has_mutating_signal matching.
    """
    if not command:
        return False
    if not _has_mutating_signal(command):
        return False
    stripped = NULL_SINK_REDIRECT_STRIP_RE.sub("", command)
    return not _has_mutating_signal(stripped)


def _is_safe_sqlite_read(command: str) -> bool:
    """True iff the command is a literal-read sqlite probe.

    Required: matches SAFE_SQLITE_READ_RE (literal SELECT/WITH/EXPLAIN keyword
    inside an execute() call after a sqlite3 reference).

    Disqualifying: any of executescript(, executemany(, .commit(, a SQL write
    keyword (INSERT/UPDATE/DELETE/REPLACE/CREATE/DROP/ALTER/TRUNCATE), or any
    PRAGMA keyword (function-call or assignment form) appears anywhere in the
    command. PRAGMA is dropped from the safe-read set because PRAGMA is not
    categorically read-only; assignment forms like ``PRAGMA user_version = 7``
    mutate database state. Variable-sourced execute(sql) calls do not match
    SAFE_SQLITE_READ_RE because their argument is not a literal string starting
    with a read keyword.
    """
    ast_result = _classify_python_sqlite_read_ast(command)
    if ast_result is not None:
        return ast_result
    if not SAFE_SQLITE_READ_RE.search(command):
        return False
    return not SQLITE_WRITE_DISQUALIFIERS_RE.search(command)


def _python_c_source(command: str) -> str | None:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return None
    for index, token in enumerate(tokens):
        if token == "-c" and index + 1 < len(tokens):
            exe = Path(tokens[0]).name.lower() if tokens else ""
            if exe.startswith("python") or exe in {"py", "python.exe"}:
                return tokens[index + 1]
    return None


def _sql_literal_is_read_only(sql: str) -> bool:
    text = sql.strip()
    if not re.match(r"(?is)^(?:SELECT|WITH|EXPLAIN)\b", text):
        return False
    return SQLITE_WRITE_DISQUALIFIERS_RE.search(text) is None


def _is_sqlite_connect_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "connect"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "sqlite3"
    )


def _is_uri_ro_connect(node: ast.Call) -> bool:
    if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
        return False
    if not re.search(r"^file:.+?\bmode=ro\b", node.args[0].value, re.IGNORECASE):
        return False
    return any(
        keyword.arg == "uri" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
        for keyword in node.keywords
    )


class _SQLiteReadClassifier(ast.NodeVisitor):
    def __init__(self) -> None:
        self.connections: dict[str, str] = {}
        self.saw_sqlite_operation = False
        self.unsafe = False

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802 - ast visitor name
        if _is_sqlite_connect_call(node.value):
            assert isinstance(node.value, ast.Call)
            kind = "sqlite_conn_uri_ro" if _is_uri_ro_connect(node.value) else "sqlite_conn"
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.connections[target.id] = kind
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 - ast visitor name
        if isinstance(node.func, ast.Attribute):
            receiver = node.func.value
            method = node.func.attr
            conn_kind: str | None = None
            if isinstance(receiver, ast.Name) and receiver.id in self.connections:
                conn_kind = self.connections[receiver.id]
            elif _is_sqlite_connect_call(receiver):
                assert isinstance(receiver, ast.Call)
                conn_kind = "sqlite_conn_uri_ro" if _is_uri_ro_connect(receiver) else "sqlite_conn"

            if conn_kind is not None and method in {"execute", "executemany", "executescript", "commit"}:
                self.saw_sqlite_operation = True
                if method != "execute" or not node.args:
                    self.unsafe = True
                else:
                    sql_arg = node.args[0]
                    if isinstance(sql_arg, ast.Constant) and isinstance(sql_arg.value, str):
                        if not _sql_literal_is_read_only(sql_arg.value):
                            self.unsafe = True
                    elif conn_kind != "sqlite_conn_uri_ro":
                        self.unsafe = True
        self.generic_visit(node)


def _classify_python_sqlite_read_ast(command: str) -> bool | None:
    if "sqlite3" not in command.lower():
        return None
    source = _python_c_source(command)
    if source is None:
        return None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    classifier = _SQLiteReadClassifier()
    classifier.visit(tree)
    if not classifier.saw_sqlite_operation:
        return None
    return not classifier.unsafe


def _is_mutating_command(command: str) -> bool:
    cmd = command or ""
    if not _has_mutating_signal(cmd):
        return False
    if _all_mutating_signal_is_null_sink_redirect(cmd):
        return False
    return not ("sqlite3" in cmd.lower() and _is_safe_sqlite_read(cmd))


def _is_apply_patch_tool(tool: str) -> bool:
    return tool == "apply_patch" or tool.endswith(".apply_patch")


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_string_values(item))
        return strings
    if isinstance(value, list | tuple):
        sequence_strings: list[str] = []
        for item in value:
            sequence_strings.extend(_string_values(item))
        return sequence_strings
    return []


def _apply_patch_text(payload: dict[str, Any], data: Any) -> str:
    candidates: list[str] = []
    candidates.extend(_string_values(data))
    for key in ("patch", "input", "content", "tool_input"):
        candidates.extend(_string_values(payload.get(key)))
    candidates.extend(_string_values(payload))
    for candidate in candidates:
        if "*** Begin Patch" in candidate and candidate.strip():
            return candidate
    for candidate in candidates:
        if candidate.strip():
            return candidate
    return ""


def _argv_command(argv: Any) -> str | None:
    if not isinstance(argv, list | tuple) or not argv:
        return None
    if not all(isinstance(token, str | int | float) for token in argv):
        return None
    return subprocess.list2cmdline([str(token) for token in argv])


def _command_from_payload(payload: dict[str, Any], data: Any, tool: str) -> str | None:
    """Normalize shell command strings and shell-free Git argv payloads."""
    raw_command = data.get("command") if isinstance(data, dict) else None
    if raw_command is None:
        raw_command = payload.get("command")
    command = raw_command if isinstance(raw_command, str) else _argv_command(raw_command)

    args: Any = None
    if isinstance(data, dict):
        args = data.get("argv") if data.get("argv") is not None else data.get("args")
    if command:
        executable = Path(_clean_shell_token(command)).name.lower()
        argv_text = _argv_command(args)
        if executable in {"git", "git.exe"} and argv_text:
            return f"{command} {argv_text}"
        return command

    if Path(tool).name.lower() not in {"git", "git.exe"}:
        return None
    argv_text = _argv_command(args)
    if not argv_text:
        return None
    argv_tokens = list(args)
    first = Path(str(argv_tokens[0])).name.lower()
    return argv_text if first in {"git", "git.exe"} else f"git {argv_text}"


def _direct_git_effect_from_payload(payload: dict[str, Any]) -> str | None:
    data = _tool_input(payload)
    command = _command_from_payload(payload, data, _tool_name(payload).lower())
    if not command:
        return None
    # c122: the walk reaches every command the line runs, its stages among them.
    return _direct_git_effect(command)


# Credential material (owner decision after the 2026-09-26 M13 host I incident: "Fix first: c117"). An agent context
# never reads, searches, lists, prints or writes credential material: credential files and folders, .env files, the
# environment's listing or a secret-named variable. Whatever an agent reads enters a conversation sent to its model
# provider, so the refusal covers reads as well as effects and applies before binding and scope. The owner handles
# credentials in their own terminal.
CREDENTIAL_FILE_NAMES = frozenset({"pgpass", ".pgpass", "pgpass.conf", "pg_service.conf", ".pg_service.conf"})
CREDENTIAL_ENV_FILE_SAFE_SUFFIXES = (".example", ".sample", ".template", ".dist")
# Files the owner declares credential-bearing, relative to a project root (lower case).
DECLARED_CREDENTIAL_PATHS = frozenset(
    {
        "memory/topics/reference_openai_api_key.md",
        ".quality/release-candidate-tracked-secrets.json",
        "groundtruth-kb/tests/fixtures/bridge_spike_minimized_governance_hooks/credential_scan.py",
        "applications/agent_red/docs/owner-messages-all.json",
    }
)
SECRET_VARIABLE_NAME = re.compile(r"KEY|PASSWORD|PASSWD|SECRET|TOKEN|CREDENTIAL|PGPASS", re.IGNORECASE)
# Native read and search tools: every string argument (paths, globs, patterns) is inspected.
CREDENTIAL_READ_TOOLS = frozenset(
    {
        "read",
        "grep",
        "glob",
        "ls",
        "view",
        "notebookread",
        "read_image",
        "read_file",
        "view_file",
        "list_dir",
        "find_by_name",
        "grep_search",
        "codebase_search",
        # Goose's read-only tools, forwarded by its adapter under their namespaced names (developer__tree, ...).
        "tree",
        "list",
        "search",
    }
)
# Write, edit and unknown tools: only their target-path arguments are inspected, never the content they carry.
CREDENTIAL_TARGET_KEYS = ("file_path", "notebook_path", "path", "target_file", "TargetFile", "AbsolutePath")
_CREDENTIAL_TOKEN = re.compile(r"[^\s'\"`;|&(){}<>,=]+")
_ENVIRONMENT_LISTINGS = (
    # PowerShell's Env: drive, listed whole or by wildcard.
    re.compile(r"(?i)\b(?:get-childitem|gci|dir|ls)\s+(?:-(?:literal)?path\s+)?['\"]?env:"),
    re.compile(r"(?i)\benv:[\\/]?[^\s'\"`;|&()]*[*?]"),
    re.compile(r"(?i)\[(?:system\.)?environment\]::getenvironmentvariables\s*\("),
    # POSIX and cmd listings as whole commands.
    re.compile(r"(?i)(?:^|[;&|(\n]\s*)(?:printenv|env|set|export\s+-p|declare\s+-x|compgen\s+-e)\s*(?=$|[;&|)\n])"),
    # The whole mapping from Python or Node.
    re.compile(r"(?i)\bos\.environ\b(?!\s*(?:\[|\.get\s*\())"),
    re.compile(r"(?i)\bprocess\.env\b(?!\s*(?:\[|\.[A-Za-z_]))"),
)
_SECRET_VARIABLE_REFERENCES = (
    re.compile(r"(?i)\benv:([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"(?i)getenvironmentvariable\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)"),
    # POSIX variables are upper case by convention; a lower-case shell variable such as $key is not an environment read.
    re.compile(r"\$\{?([A-Z_][A-Z0-9_]*)\}?"),
    re.compile(r"%([A-Za-z_][A-Za-z0-9_]*)%"),
    re.compile(r"(?i)\bos\.environ\s*(?:\[\s*|\.get\s*\(\s*)['\"]([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"(?i)\bos\.getenv\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"(?i)\bprocess\.env(?:\.|\[\s*['\"])([A-Za-z_][A-Za-z0-9_]*)"),
)


def _credential_path(token: str) -> bool:
    """Return whether one path-like token names credential material."""
    text = token.strip().replace("\\", "/")
    segments = [segment for segment in text.lower().split("/") if segment not in ("", ".")]
    if not segments:
        return False
    name = segments[-1]
    if name in CREDENTIAL_FILE_NAMES or name.endswith(".pgpass"):
        return True
    if name == ".env" or (name.startswith(".env.") and not name.endswith(CREDENTIAL_ENV_FILE_SAFE_SUFFIXES)):
        return True
    # A credentials folder is named as a path segment; the bare word in prose is not a path.
    if "credentials" in segments[:-1] or (name == "credentials" and "/" in text):
        return True
    joined = "/".join(segments)
    return any(joined == declared or joined.endswith("/" + declared) for declared in DECLARED_CREDENTIAL_PATHS)


def _credential_material_access(payload: dict[str, Any]) -> str | None:
    """Name the credential material one tool call would read, search, list, print or write; None when it names none."""
    tool = _tool_name(payload).lower()
    data = _tool_input(payload)
    command = _command_from_payload(payload, data, tool)
    if command is not None:
        for pattern in _ENVIRONMENT_LISTINGS:
            if pattern.search(command):
                return "an environment listing"
        for pattern in _SECRET_VARIABLE_REFERENCES:
            for match in pattern.finditer(command):
                if SECRET_VARIABLE_NAME.search(match.group(1)):
                    return f"the secret-named variable {match.group(1)}"
        texts = [command]
    elif _is_apply_patch_tool(tool) or any("*** Begin Patch" in value for value in _string_values(payload)):
        texts = _paths_from_apply_patch(_project_root(payload), _apply_patch_text(payload, data))
    elif Path(tool).name.rsplit("__", 1)[-1] in CREDENTIAL_READ_TOOLS:
        texts = _string_values(data)
    else:
        texts = [str(data[key]) for key in CREDENTIAL_TARGET_KEYS if isinstance(data, dict) and data.get(key)]
    for text in texts:
        for token in _CREDENTIAL_TOKEN.findall(text):
            if _credential_path(token):
                return str(token)
    return None


# Context isolation (owner decision after the 2026-09-27 M13 host I finding: "Fix first: c118"). A review context
# searched the whole scratchpad and listed seven other contexts' runtime homes, the implementer's included. A context
# uses only its own scratch (scratchpad/<its session context>) and registered checkout (.worktrees/<its session
# context>): another context's scratch or checkout is not read, searched, listed or changed. A shell recursion rooted at
# or above the shared scratchpad or .worktrees roots, the project root included, is refused too, because it walks into
# them and into Git-ignored credential files. Repository content is searched with git grep or rg, which skip
# Git-ignored paths; shared state is read through the gt CLI.
CONTEXT_PARENTS = ("scratchpad", ".worktrees")
# A context's scratch and checkout are named by its session context; .worktrees/projects/<project> (the service's
# project work checkouts) and loose entries belong to no context.
_SESSION_CONTEXT_NAME = re.compile(r"SENV-[0-9a-f]{32}", re.IGNORECASE)
# Native tools that list or search a tree; their path-like arguments are inspected.
CONTEXT_SEARCH_TOOLS = frozenset(
    {"grep", "glob", "ls", "tree", "list", "search", "list_dir", "find_by_name", "grep_search", "codebase_search"}
)
_PATH_LIKE_KEY = re.compile(r"path|dir|glob|include|exclude|target", re.IGNORECASE)
_WILDCARD = re.compile(r"[*?\[]")
_LISTING_VERBS = frozenset({"get-childitem", "gci", "dir", "ls"})
# PowerShell accepts parameter prefixes, and Get-ChildItem binds -r and -re to -Recurse (both recurse in PowerShell 7 and
# Windows PowerShell 5.1; round 2, B128). In PowerShell `ls` is Get-ChildItem; a POSIX `ls -r` only reverses the order,
# and refusing it at the shared roots is fail-closed.
_POWERSHELL_RECURSE = re.compile(r"-(?:r|re|rec|recu|recur|recurs|recurse|de|dep|dept|depth)(?::.*)?", re.IGNORECASE)
_POSIX_LIST_RECURSE = re.compile(r"-[a-z]*R[a-z]*")
_GREP_RECURSE = re.compile(r"-[a-zA-Z]*[rR][a-zA-Z]*|--recursive|--dereference-recursive")
_GREP_PATTERN_OPTIONS = frozenset({"-e", "-f", "--regexp", "--file"})
_RG_UNIGNORE = frozenset(
    {"--no-ignore", "--no-ignore-vcs", "--no-ignore-parent", "--no-ignore-dot", "--unrestricted", "-u", "-uu", "-uuu"}
)
_POWERSHELL_VALUE_PARAMETERS = re.compile(
    r"-(?:fi|fil|filt|filte|filter|in|inc|incl|inclu|includ|include|ex|exc|excl|exclu|exclud|exclude|de|dep|dept|"
    r"depth|at|att|attr|attri|attrib|attribu|attribut|attribute|attributes)",
    re.IGNORECASE,
)


def _context_root(root: Path) -> Path:
    """Return the project that owns the shared scratchpad and .worktrees, also from inside a context's checkout."""
    for candidate in (root, *root.parents):
        if candidate.name.lower() in CONTEXT_PARENTS:
            return candidate.parent
    return root


def _absolute(base: Path, token: str) -> Path | None:
    """Resolve one path-like token against the call's working directory; None for flags and variables."""
    text = _clean_shell_token(token).strip().strip("'\"")
    if not text or text.startswith(("-", "$", "@", "%")) or "://" in text:
        return None
    candidate = Path(text)
    return Path(os.path.normpath(str(candidate if candidate.is_absolute() else base / candidate)))


def _wildcard_parent(token: str) -> str:
    """Return the part of a path token before its first wildcard segment."""
    text = _clean_shell_token(token).strip().strip("'\"").replace("\\", "/")
    parts = text.split("/")
    for index, part in enumerate(parts):
        if _WILDCARD.search(part):
            return "/".join(parts[:index]) or "."
    return text


def _is_within(path: Path, ancestor: Path) -> bool:
    """Return whether path is ancestor or lies below it (case-insensitive on Windows)."""
    here, there = os.path.normcase(str(path)), os.path.normcase(str(ancestor))
    return here == there or here.startswith(there.rstrip("\\/") + os.sep)


def _context_directory(project: Path, target: Path) -> tuple[str, str] | None:
    """Return (parent, child) when target lies in a context's scratch or checkout; a wildcard child counts too.

    A context's directory is named by its session context (SENV- and 32 hex digits). Any other entry directly under
    the shared roots (a loose file, the service's .worktrees/projects) belongs to no context and is judged as usual.
    """
    for parent in CONTEXT_PARENTS:
        base = project / parent
        if not _is_within(target, base):
            continue
        relative = os.path.normcase(str(target))[len(os.path.normcase(str(base))) :].strip("\\/")
        if not relative:
            return None
        child = str(target)[len(str(base)) :].strip("\\/").replace("\\", "/").split("/", 1)[0]
        if _SESSION_CONTEXT_NAME.fullmatch(child) or _WILDCARD.search(child):
            return parent, child
        return None
    return None


def _path_like_values(tool: str, data: Any) -> list[str]:
    """Path-like argument values of a native tool call: its paths and globs, never a content pattern or query."""
    if not isinstance(data, dict):
        return _string_values(data)
    values: list[str] = []
    for key, value in data.items():
        if _PATH_LIKE_KEY.search(str(key)) or (tool in {"glob", "find_by_name"} and str(key).lower() == "pattern"):
            values.extend(_string_values(value))
    return values


def _context_tokens(payload: dict[str, Any]) -> tuple[list[str], str | None]:
    """Return the tokens that may name paths in this call, and its shell command if it is one."""
    tool = _tool_name(payload).lower()
    data = _tool_input(payload)
    command = _command_from_payload(payload, data, tool)
    if command is not None:
        return _CREDENTIAL_TOKEN.findall(command), command
    if _is_apply_patch_tool(tool) or any("*** Begin Patch" in value for value in _string_values(payload)):
        return _paths_from_apply_patch(_project_root(payload), _apply_patch_text(payload, data)), None
    name = Path(tool).name.rsplit("__", 1)[-1]
    texts = _path_like_values(name, data)
    return [token for text in texts for token in _CREDENTIAL_TOKEN.findall(text)], None


def _named_context_directories(payload: dict[str, Any]) -> list[tuple[str, str]]:
    """Return (child, token) for every context scratch or checkout directory this call names."""
    root = _project_root(payload)
    project = _context_root(root)
    cwd = Path(str(payload.get("cwd") or root))
    named: list[tuple[str, str]] = []
    tokens, _command = _context_tokens(payload)
    for token in tokens:
        target = _absolute(cwd, token)
        found = _context_directory(project, target) if target is not None else None
        if found is not None:
            named.append((found[1], str(token)))
    return named


def _embedded_commands(stage: str) -> list[str]:
    """Commands nested in one stage: PowerShell (...), $(...), @(...) and { ... } groups, innermost first.

    PowerShell runs a subexpression inside a double-quoted string as well, so quotes do not hide a group; a group that
    is only text is judged like a command, which is fail-closed.
    """
    found: list[str] = []
    opened: list[int] = []
    for index, char in enumerate(stage):
        if char in "({":
            opened.append(index)
        elif char in ")}" and opened:
            found.append(stage[opened.pop() + 1 : index])
    return found


_EVALUATING_VERBS = frozenset({"invoke-expression", "iex"})


def _evaluated_command(stage: str) -> str | None:
    """Return the written-out command text a PowerShell Invoke-Expression (iex) stage runs; None for any other stage."""
    tokens = _shell_split(stage)
    if not tokens:
        return None
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    words = [_clean_shell_token(token) for token in tokens[verb_index:]]
    while words and words[0].lower() in {"&", "call"}:
        words = words[1:]
    if not words or _executable_name(words[0]) not in _EVALUATING_VERBS:
        return None
    text = " ".join(word for word in words[1:] if not (word.startswith("-") and "-command".startswith(word.lower())))
    return text or None


_INNER_COMMAND_DEPTH = 4


def _stage_executable(stage: str) -> str | None:
    """Return the executable basename a stage runs, past PowerShell's call operator and cmd's call."""
    tokens = _shell_split(stage)
    if not tokens:
        return None
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    relevant = tokens[verb_index:]
    while relevant and _clean_shell_token(relevant[0]).lower() in {"&", "call"}:
        relevant = relevant[1:]
    return _executable_name(relevant[0]) if relevant else None


def _unquote_once(text: str) -> str:
    """Remove one enclosing quote pair, keeping every quote inside the text."""
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    return text


_HANDING_FLAGS = {
    "cmd": frozenset({"/c", "/k"}),
    "powershell": frozenset({"-c", "-command", "/c", "/command"}),
    "posix": frozenset({"-c"}),
}


def _handed_command(stage: str) -> tuple[str | None, bool]:
    """The command a nested-shell stage hands on, with its inner quotes kept (c119).

    Recognizes the wrappers _nested_shell_command recognizes and returns the text after the handing flag (a POSIX shell
    runs only the next argument) with one enclosing quote pair removed; _nested_shell_command strips every quote at both
    ends, which can drop a quote that belongs to the inner command. Any other stage keeps that helper's answer.
    """
    nested, recognized = _nested_shell_command(stage)
    if not recognized or not nested:
        return nested, recognized
    tokens = _shell_split(stage) or []
    verb_index = _shell_verb_index(tokens)
    relevant = tokens[verb_index:] if verb_index is not None else []
    while relevant and _clean_shell_token(relevant[0]).lower() in {"&", "call"}:
        relevant = relevant[1:]
    if not relevant:
        return nested, recognized
    executable = _executable_name(relevant[0])
    if executable in _CMD_SHELL_NAMES:
        flags = _HANDING_FLAGS["cmd"]
    elif executable in _POWERSHELL_NAMES:
        flags = _HANDING_FLAGS["powershell"]
    elif executable in _POSIX_SHELL_NAMES:
        flags = _HANDING_FLAGS["posix"]
    else:
        return nested, recognized
    for index, raw in enumerate(relevant[1:], start=1):
        if _clean_shell_token(raw).lower() in flags:
            rest = relevant[index + 1 :]
            if executable in _POSIX_SHELL_NAMES:
                rest = rest[:1]
            text = _unquote_once(" ".join(rest))
            return (text or None), True
    return nested, recognized


def _handed_evaluation(stage: str) -> str | None:
    """The written-out text an Invoke-Expression (iex) stage runs, with its inner quotes kept (c119)."""
    if _evaluated_command(stage) is None:
        return None
    tokens = _shell_split(stage) or []
    verb_index = _shell_verb_index(tokens)
    words = tokens[verb_index:] if verb_index is not None else []
    while words and _clean_shell_token(words[0]).lower() in {"&", "call"}:
        words = words[1:]
    rest = [word for word in words[1:] if not (word.startswith("-") and "-command".startswith(word.lower()))]
    return _unquote_once(" ".join(rest)) or None


def _inner_commands(command: str, *, _depth: int = 0) -> list[str]:
    """Every command a stage hands to a nested shell or to Invoke-Expression, recursively (c119).

    A command string given to cmd /c or /k, powershell or pwsh -c/-Command, bash, sh or zsh -c, or Invoke-Expression
    (iex) is one quoted token to the outer shell, so a redirect or a mutating command inside it never reaches the outer
    write judgment. Each inner command is returned so the caller judges it as a command of its own. cmd does not treat
    single quotes as quotes, so for a cmd wrapper they are judged as ordinary characters. A recognized wrapper whose
    command is encoded, empty or unparsable, or nesting deeper than _INNER_COMMAND_DEPTH, yields
    UNINSPECTABLE_SHELL_COMMAND.
    """
    inner: list[str] = []
    for stage in _split_command_stages(command):
        nested, recognized = _handed_command(stage)
        found: list[str | None] = []
        if recognized:
            if nested and _stage_executable(stage) in _CMD_SHELL_NAMES:
                nested = nested.replace("'", " ")
            found.append(nested)
        evaluated = _handed_evaluation(stage)
        if evaluated is not None:
            found.append(evaluated)
        for text in found:
            if not text or _depth >= _INNER_COMMAND_DEPTH or _shell_split(text) is None:
                inner.append(UNINSPECTABLE_SHELL_COMMAND)
                continue
            inner.append(text)
            inner.extend(_inner_commands(text, _depth=_depth + 1))
    return inner


def _string_subexpressions(command: str) -> list[str]:
    """The text of each $(...) subexpression inside a double-quoted string of the command (c121).

    PowerShell and POSIX shells run a $(...) inside double quotes, so `Write-Output "$(Set-Content x y)"` writes while
    the quote-masked write judgment saw only a string. Single-quoted text is literal in both shells, and a character
    after PowerShell's escape (a backtick) is literal. A subexpression without its closing parenthesis is not returned.
    """
    found: list[str] = []
    quote: str | None = None
    i = 0
    while i < len(command):
        char = command[i]
        if quote == "'":
            quote = None if char == "'" else quote
        elif quote == '"':
            if char == '"':
                quote = None
            elif char == "`":
                i += 1
            elif command.startswith("$(", i):
                depth, j = 1, i + 2
                while j < len(command) and depth:
                    depth += {"(": 1, ")": -1}.get(command[j], 0)
                    j += 1
                if depth == 0:
                    found.append(command[i + 2 : j - 1])
                    i = j
                    continue
        elif char in "'\"":
            quote = char
        i += 1
    return found


def _string_subexpression_commands(command: str, *, _depth: int = 0) -> list[str]:
    """Each $(...) inside a double-quoted string, and every command inside it, recursively (c121)."""
    found: list[str] = []
    for text in _string_subexpressions(command):
        if _depth >= _INNER_COMMAND_DEPTH:
            found.append(UNINSPECTABLE_SHELL_COMMAND)
            continue
        found.append(text)
        found.extend(_inner_commands(text))
        found.extend(_string_subexpression_commands(text, _depth=_depth + 1))
    return found


def _has_unread_write(command: str) -> bool:
    """Whether the command carries a write whose target the gate does not read (c121).

    A redirect to a file (its target is not read yet: B149), a .NET write call, a Python write, or a named write command
    that does not begin a stage the gate parses (inside a script block, a group or a subexpression, or after a call
    operator) names no target the gate can check. Owner decision 2026-09-29 07:56 ("All forms found"): such a command is
    refused whole (unknown_effect_targets), so a claim check never covers one write while another goes unchecked.
    """
    shell_view = _mask_quoted_spans(command, mask_double=True)
    if _DOTNET_WRITE_RE.search(shell_view) is not None or _has_python_mutating_signal(command):
        return True
    if _shell_redirect_present(NULL_SINK_REDIRECT_STRIP_RE.sub("", command)):
        return True
    # c122 (batch design WP1, W and item 8): a target whose value the shell supplies when it runs is not read.
    if _unresolved_target(command) is not None:
        return True
    named = _named_writes(shell_view)
    # c122: git's --output is a named write too; it is read where a stage the gate parses gives its file.
    git_outputs = len(_GIT_OUTPUT_RE.findall(shell_view))
    if git_outputs:
        named["git --output"] = git_outputs
    if not named:
        return False
    read: Counter[str] = Counter()
    for stage in _split_pipeline_stages(command):
        try:
            tokens = shlex.split(stage, posix=False)
        except ValueError:
            continue
        if _git_output_targets(tokens):
            read["git --output"] += 1
            continue
        classification = _classify_command_verb(tokens)
        if classification is None:
            continue
        extractor, relevant = classification
        verb = _canonical_write_verb(relevant[0])
        if _named_writes(_mask_quoted_spans(stage, mask_double=True))[verb] and extractor(relevant):
            read[verb] += 1
    return any(count > read[verb] for verb, count in named.items())


def _unresolved_target(command: str) -> str | None:
    """The first write target the command names whose value the shell supplies when it runs (c122); None if none.

    Owner decision 2026-09-30 20:52 ("Fix first: c122"; batch design WP1, W and item 8): a write to
    "scratchpad\\<own>\\$x" was judged a write of that literal path, which the native check placed in the context's
    own scratch whatever $x held. A target holding a variable, an expression, an environment variable or a home or
    splat prefix is not read, so its write is refused whole before the native check. The targets judged are the ones
    the verb tables read for a named write command at the start of a stage (a copy's source among them) and git's
    --output file; a parameter's value, such as Set-Content's -Value, is not one.
    """
    for stage in _split_pipeline_stages(command):
        try:
            tokens = shlex.split(stage, posix=False)
        except ValueError:
            continue
        outputs = _git_output_targets(tokens)
        if outputs is not None:
            targets = outputs
        else:
            classification = _classify_command_verb(tokens)
            if classification is None:
                continue
            extractor, relevant = classification
            if not _named_writes(_mask_quoted_spans(stage, mask_double=True))[_canonical_write_verb(relevant[0])]:
                continue
            targets = extractor(relevant)
        unresolved = next((target for target in targets if _unresolved_value(target)), None)
        if unresolved is not None:
            return unresolved
    return None


def _git_reach_roots(args: list[str]) -> tuple[list[str], bool] | None:
    """Return (roots, True) for a read-only Git form that reads past the ignore rules; None for every other Git call.

    DIRECT_GIT_READ_ONLY_SUBCOMMANDS judges whether Git can write. These forms are judged by what they read, and each
    reads Git-ignored files, the shared context roots among them: git grep with --no-exclude-standard, or with
    --no-index but without --exclude-standard; git ls-files with --others but without --exclude-standard, or with
    --ignored; git status with --ignored (other than --ignored=no); and git diff --no-index, which compares any two
    trees. Each walks from its paths (after -- for grep, ls-files and status), else from the working directory or the
    -C directory.
    """
    base = ""
    index = 0
    while index < len(args):
        token = args[index]
        if token == "-C" and index + 1 < len(args):
            base = args[index + 1]
            index += 2
        elif token in GIT_GLOBAL_OPTIONS_WITH_VALUES and index + 1 < len(args):
            index += 2
        elif token.startswith("-"):
            index += 1
        else:
            break
    if index >= len(args):
        return None
    subcommand, rest = args[index].lower(), args[index + 1 :]
    options = [arg.lower() for arg in rest if arg.startswith("-") and arg != "--"]
    short = "".join(option[1:] for option in options if not option.startswith("--"))
    if subcommand == "grep":
        reaches = "--no-exclude-standard" in options or (
            "--no-index" in options and "--exclude-standard" not in options
        )
    elif subcommand == "ls-files":
        ignored = "--ignored" in options or "i" in short
        others = "--others" in options or "o" in short
        reaches = ignored or (others and "--exclude-standard" not in options)
    elif subcommand == "status":
        reaches = any(
            option == "--ignored" or (option.startswith("--ignored=") and option != "--ignored=no")
            for option in options
        )
    elif subcommand == "diff":
        reaches = "--no-index" in options
    else:
        return None
    if not reaches:
        return None
    if subcommand == "diff":
        paths = [arg for arg in rest if not arg.startswith("-")]
    else:
        paths = rest[rest.index("--") + 1 :] if "--" in rest else []
    roots = [os.path.join(base, path) for path in paths] if base else paths
    return (roots or [base or "."]), True


def _recursive_roots(verb: str, args: list[str]) -> tuple[list[str], bool] | None:
    """Return (roots, walks_ignored) for a recursive listing or search; None when the stage is not one.

    walks_ignored is False only for rg without an ignore-disabling flag: rg skips Git-ignored paths, so only an explicit
    root at or inside the shared roots reaches them.
    """
    if verb in {"git", "git.exe"}:
        return _git_reach_roots(args)
    lowered = [arg.lower() for arg in args]
    if verb in _LISTING_VERBS:
        recursive = any(
            _POWERSHELL_RECURSE.fullmatch(arg) or _POSIX_LIST_RECURSE.fullmatch(arg) or low == "/s"
            for arg, low in zip(args, lowered, strict=True)
        )
        if not recursive:
            return None
        roots: list[str] = []
        skip = False
        for arg in args:
            if skip:
                skip = False
                continue
            if _POWERSHELL_VALUE_PARAMETERS.fullmatch(arg):
                skip = True
                continue
            if arg.startswith("-") or arg.startswith("/"):
                continue
            roots.append(arg)
        return roots, True
    if verb in {"tree", "tree.com", "du"}:
        return [arg for arg in args if not arg.startswith(("-", "/"))], True
    if verb == "find":
        roots = []
        for arg in args:
            if arg.startswith(("-", "(", "!")):
                break
            roots.append(arg)
        return roots, True
    if verb in {"grep", "egrep", "fgrep", "rg", "rg.exe"}:
        is_rg = verb.startswith("rg")
        if not is_rg and not any(_GREP_RECURSE.fullmatch(arg) for arg in args):
            return None
        explicit_pattern = any(arg.split("=", 1)[0] in _GREP_PATTERN_OPTIONS for arg in args)
        operands: list[str] = []
        skip = False
        for arg in args:
            if skip:
                skip = False
                continue
            if arg in _GREP_PATTERN_OPTIONS or arg in {"-g", "--glob", "-t", "--type", "-m", "--max-count"}:
                skip = True  # the option's value (a pattern, glob, type or count) is not a root
                continue
            if arg.startswith("-"):
                continue
            operands.append(arg)
        roots = operands if explicit_pattern else operands[1:]
        walks_ignored = not is_rg or any(low in _RG_UNIGNORE for low in lowered)
        return roots, walks_ignored
    if verb in {"findstr", "findstr.exe"} and "/s" in lowered:
        return [_wildcard_parent(arg) for arg in args if not arg.startswith("/")][1:], True
    if verb in {"forfiles", "forfiles.exe"} and "/s" in lowered:
        return [args[lowered.index("/p") + 1]] if "/p" in lowered and lowered.index("/p") + 1 < len(args) else [], True
    if verb in {"where", "where.exe"} and "/r" in lowered:
        return [args[lowered.index("/r") + 1]] if lowered.index("/r") + 1 < len(args) else [], True
    if verb in {"robocopy", "robocopy.exe", "xcopy", "xcopy.exe"} and ({"/s", "/e"} & set(lowered)):
        return [arg for arg in args if not arg.startswith("/")][:1], True
    return None


def _stage_traversal(stage: str, cwd: Path, shared: list[Path], *, _depth: int = 0) -> str | None:
    """Name the recursive listing or search in one shell stage that walks into a shared context root."""
    if _depth > 4:
        return None
    nested, recognized = _nested_shell_command(stage)
    if recognized:
        for inner in _split_command_stages(nested or "") or ([nested] if nested else []):
            found = _stage_traversal(inner, cwd, shared, _depth=_depth + 1)
            if found is not None:
                return found
        return None
    evaluated = _evaluated_command(stage)
    if evaluated:
        for inner in _split_command_stages(evaluated) or [evaluated]:
            found = _stage_traversal(inner, cwd, shared, _depth=_depth + 1)
            if found is not None:
                return found
    found = _stage_recursion(stage, cwd, shared)
    if found is not None:
        return found
    # A PowerShell subexpression, grouping or script block runs its own command; each one is judged like a stage.
    for inner in _embedded_commands(stage):
        for part in _split_command_stages(inner) or ([inner] if inner.strip() else []):
            found = _stage_traversal(part, cwd, shared, _depth=_depth + 1)
            if found is not None:
                return found
    return None


def _stage_recursion(stage: str, cwd: Path, shared: list[Path]) -> str | None:
    """Name the stage's own recursive listing or search (its leading verb) when it walks into a shared context root."""
    tokens = _shell_split(stage)
    if not tokens:
        return None
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    words = [_clean_shell_token(token) for token in tokens[verb_index:]]
    while words and words[0].lower() in {"&", "call"}:
        words = words[1:]
    if not words:
        return None
    recursion = _recursive_roots(_executable_name(words[0]), words[1:])
    if recursion is None:
        return None
    roots, walks_ignored = recursion
    for token in roots or ["."]:
        text = _clean_shell_token(token).strip().strip("'\"")
        if text.startswith(("$", "@", "%", "(")):
            # A variable or an expression can name any directory, the shared roots included (fail-closed).
            return " ".join(words)[:240]
        target = _absolute(cwd, _wildcard_parent(token))
        if target is None:
            continue
        for base in shared:
            reaches = _is_within(base, target) if walks_ignored else _is_within(target, base)
            if reaches:
                return " ".join(words)[:240]
    return None


def _context_traversal(payload: dict[str, Any]) -> str | None:
    """Name a listing or search that walks into the shared scratchpad or .worktrees roots; None when none does."""
    root = _project_root(payload)
    project = _context_root(root)
    cwd = Path(str(payload.get("cwd") or root))
    shared = [project / parent for parent in CONTEXT_PARENTS]
    tokens, command = _context_tokens(payload)
    if command is not None:
        for stage in _split_command_stages(command) or [command]:
            found = _stage_traversal(stage, cwd, shared)
            if found is not None:
                return found
        # A group that holds a pipe or a separator is split across the stages above; each group is judged whole too.
        for inner in _embedded_commands(command):
            for part in _split_command_stages(inner) or ([inner] if inner.strip() else []):
                found = _stage_traversal(part, cwd, shared)
                if found is not None:
                    return found
        return None
    if Path(_tool_name(payload).lower()).name.rsplit("__", 1)[-1] not in CONTEXT_SEARCH_TOOLS:
        return None
    for token in tokens:
        target = _absolute(cwd, _wildcard_parent(token))
        if target is not None and any(os.path.normcase(str(target)) == os.path.normcase(str(base)) for base in shared):
            return str(token)
    return None


def _bound_session_context(payload: dict[str, Any], project: Path) -> tuple[str | None, bool]:
    """Return (session context, available) for this call's native context through the ordinary CLI.

    An unbound context owns no scratch or checkout. The CLI runs against the project that owns the shared roots, so a
    context inside its own checkout still reaches the configured authority.
    """
    native = str(os.environ.get("GTKB_NATIVE_CONTEXT_ID") or payload.get("session_id") or "").strip()
    if not native:
        return None, True
    argv = [sys.executable, "-m", "groundtruth_kb", "session", "show", "--native-context-id", native, "--json"]
    env = {**os.environ, "GT_PROJECT_ROOT": str(project), "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            argv,
            cwd=project,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, False
    if result.returncode:
        return None, "no_session_binding" in (result.stderr or "")
    try:
        context = json.loads(result.stdout).get("session_context_id")
    except (ValueError, AttributeError):
        return None, False
    return (str(context) if context else None), True


def _judged_commands(command: str) -> list[str]:
    """The commands the write rule judges besides the line itself (c119 and c121; gathered here since c122).

    c119: a command handed to a nested shell or to Invoke-Expression is judged as a command of its own (M13 host I, Q6
    on c118: `cmd /c "gt --help > help.out 2>&1"` wrote a file under a read's judgment). c121: so is a $(...)
    subexpression inside a double-quoted string, which PowerShell and POSIX shells run.
    """
    judged = _inner_commands(command)
    return judged + [
        text
        for source in (command, *judged)
        if source != UNINSPECTABLE_SHELL_COMMAND
        for text in _string_subexpression_commands(source)
    ]


def _unresolved_write_target(command: str) -> str | None:
    """The first unresolved write target in the line or a command it hands on, for the refusal text (c122)."""
    for text in (command, *_judged_commands(command)):
        if text != UNINSPECTABLE_SHELL_COMMAND and (target := _unresolved_target(text)) is not None:
            return target
    return None


def changed_paths(payload: dict[str, Any]) -> tuple[list[str], bool]:
    root = _project_root(payload)
    tool = _tool_name(payload).lower()
    data = _tool_input(payload)

    if tool in {"write", "edit", "strreplace", "multiedit", "notebookedit", "delete"}:
        if not isinstance(data, dict):
            return [], True
        path = data.get("file_path") or data.get("notebook_path") or data.get("path")
        rel = _normalize(root, str(path)) if path else None
        return ([rel] if rel else []), True

    if tool in {"move", "copy"}:
        # No supported native payload identifies both paths for these tools.
        # Use an explicit shell/CLI operation instead of checking only one side.
        return [], True

    if _is_apply_patch_tool(tool) or any("*** Begin Patch" in value for value in _string_values(payload)):
        text = _apply_patch_text(payload, data)
        return _paths_from_apply_patch(root, text), True

    command = _command_from_payload(payload, data, tool)
    if command is not None:
        ruff_effects = _ruff_effects(root, command)
        if ruff_effects is not None:
            return ruff_effects
        if _is_safe_command(command):
            return [], False
        diagnostic_outputs = _diagnostic_output_paths_from_shell(root, command)
        if diagnostic_outputs is not None:
            return diagnostic_outputs, True
        paths = _paths_from_shell(root, command)
        mutating = _is_mutating_command(command)
        unread = mutating and _has_unread_write(command)
        for inner in _judged_commands(command):
            if inner == UNINSPECTABLE_SHELL_COMMAND:
                mutating = True
                unread = True
            elif not _is_safe_command(inner):
                paths = sorted(set(paths) | set(_paths_from_shell(root, inner)))
                inner_mutating = _is_mutating_command(inner)
                mutating = mutating or inner_mutating
                unread = unread or (inner_mutating and _has_unread_write(inner))
        # c121 (M13 GTKB Home, Q1 on c120; owner 2026-09-29 07:56): the claim check must cover every write, so a command
        # carrying a write whose target the gate cannot read is refused whole (unknown_effect_targets).
        if unread:
            return [], True
        return paths, mutating

    return [], False


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    """Route actual mutating targets through the CLI; never consult legacy packets."""

    def blocked(code: str, reason: str) -> dict[str, Any]:
        return {"decision": "block", "reason_code": code, "reason": reason}

    invalid = payload.get(INVALID_HOOK_PAYLOAD_KEY)
    if invalid:
        return blocked("invalid_hook_payload", "Cannot identify the tool effect from the supplied payload.")
    direct_git = _direct_git_effect_from_payload(payload)
    if direct_git == UNINSPECTABLE_SHELL_COMMAND:
        # c122: name what the gate observed; the code stays the Git rule's.
        return blocked(
            "direct_git_effect_requires_lifecycle",
            "A shell command that is encoded, empty, nested too deeply to inspect, run through a program named by a "
            "variable or an expression, fed to Invoke-Expression from its pipeline, or given a launcher option the gate "
            "does not know may hide a Git effect. Name the program literally (for example "
            ".\\groundtruth-kb\\.venv\\Scripts\\gt.exe), and use the ordinary gt project commit or gt bridge "
            "worktree/publish-work operation for Git effects.",
        )
    if direct_git is not None:
        return blocked(
            "direct_git_effect_requires_lifecycle",
            "Use the ordinary gt project commit or gt bridge worktree/publish-work operation for Git effects.",
        )
    owner_operation = _owner_operation_from_payload(payload)
    if owner_operation == UNINSPECTABLE_SHELL_COMMAND:
        return blocked(
            "owner_operation_only",
            "A shell command that is encoded, empty, nested too deeply to inspect, run through a program named by a "
            "variable or an expression, or a gt command whose group or action is such a value may hide an owner "
            "operation (D61): name it literally; the owner performs those from the GT-KB Home's controls or their own "
            "terminal.",
        )
    if owner_operation is not None:
        return blocked(
            "owner_operation_only",
            f"{owner_operation} is an owner operation (D61): the owner performs it from the GT-KB Home's controls "
            "or their own terminal.",
        )
    credential = _credential_material_access(payload)
    if credential is not None:
        return blocked(
            "credential_material_protected",
            f"Agents do not read, search, list, print or write credential material ({credential}): credential files "
            "and folders, .env files, environment listings and secret-named variables stay with the owner, who "
            "handles credentials in their own terminal.",
        )
    traversal = _context_traversal(payload)
    if traversal is not None:
        return blocked(
            "context_traversal",
            f"A recursive listing or search from here walks into other contexts' scratch and checkouts ({traversal}). "
            "Search tracked files with git grep or git ls-files in their ignore-honouring forms (not git grep "
            "--no-exclude-standard or --no-index, and git ls-files --others only with --exclude-standard), use rg (it "
            "skips Git-ignored paths), or name the directories to search; this context's own scratch is "
            "scratchpad/<its session context>.",
        )
    named = _named_context_directories(payload)
    if named:
        own, available = _bound_session_context(payload, _context_root(_project_root(payload)))
        if not available:
            return blocked(
                "context_isolation_unavailable",
                "Restore the native CLI/authority connection before reading or changing scratch or checkout paths.",
            )
        foreign = [token for child, token in named if child.lower() != (own or "").lower()]
        if foreign:
            return blocked(
                "foreign_context_material",
                f"A context uses only its own scratch and checkout; {foreign[0]} belongs to another context. Read "
                "shared state through the gt CLI and review work through your own checkout.",
            )
    root = _project_root(payload)
    cwd = Path(str(payload.get("cwd") or root)).absolute()
    paths, mutating = changed_paths({**payload, "project_root": str(cwd)})
    if not mutating:
        return {}
    if not paths:
        command = _command_from_payload(payload, _tool_input(payload), _tool_name(payload).lower())
        unresolved = _unresolved_write_target(command) if command else None
        if unresolved is not None:
            # c122 (batch design WP1, item 8): name the target and the remedy.
            return blocked(
                "unknown_effect_targets",
                f"The write target {unresolved} holds a value the shell supplies when it runs (a variable, an "
                "expression, an environment variable, or a home or splat prefix), so the gate cannot check it. Write "
                "the literal path (in PowerShell, -LiteralPath 'path'), or use the editor tool.",
            )
        return blocked("unknown_effect_targets", "Use an explicit tool target or the ordinary CLI for this effect.")
    native = str(os.environ.get("GTKB_NATIVE_CONTEXT_ID") or payload.get("session_id") or "").strip()
    supplied = str(payload.get("session_id") or "").strip()
    if not native or (supplied and supplied != native):
        return blocked("invalid_native_context", "The tool must carry the current harness-native context identifier.")
    argv = [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "bridge",
        "check-effects",
        "--native-context-id",
        native,
        "--cwd",
        str(cwd),
        "--json",
    ]
    for path in paths:
        argv.extend(["--path", path])
    env = dict(os.environ)
    env["GT_PROJECT_ROOT"] = str(root)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            argv,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode:
            return blocked(
                "native_effect_refused", result.stderr.strip()[:2000] or "The native CLI refused the effect check."
            )
        current = json.loads(result.stdout)
        if (
            not isinstance(current, dict)
            or current.get("status") != "current"
            or current.get("scope") not in {"scratch", "implementation"}
        ):
            return blocked("invalid_effect_response", "The native CLI did not return a current effect check.")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return blocked(
            "effect_check_unavailable", "Restore the native CLI/authority connection before retrying this effect."
        )
    return {}


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {INVALID_HOOK_PAYLOAD_KEY: "Hook input was empty."}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {INVALID_HOOK_PAYLOAD_KEY: (f"Hook input was malformed JSON at line {exc.lineno}, column {exc.colno}.")}
    if not isinstance(payload, dict) or not payload:
        return {INVALID_HOOK_PAYLOAD_KEY: "Hook input must be a non-empty JSON object."}
    return payload


def main() -> int:
    diagnostic = "--diagnostic" in sys.argv[1:]
    payload = _read_payload()
    if diagnostic:
        payload["__gtkb_registry_diagnostic__"] = True
    result = gate_decision(payload)
    emit_effect_gate_result(result, diagnostic=diagnostic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
