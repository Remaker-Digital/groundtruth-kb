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
    # c123 (owner decision A1): python -m pytest left this list. A test run is a program run, which needs a live claim
    # of the bound context (_program_run).
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
# c123 (batch design WP1, G27): gt service serve starts the authority API itself, and gt dashboard install downloads
# and installs the dashboard's server; both are service operations of the same kind.
# c123 (owner decision A2): gt home open starts the Home when it is down, so it is a Home operation as well; gt db
# postgres init and import-current administer the authority database directly (three command words). Ending a process
# and controlling the PostgreSQL cluster are owner operations too (_process_or_cluster_control).
GT_OWNER_OPERATIONS = {
    "services": frozenset({"start", "stop"}),
    "service": frozenset({"serve"}),
    "home": frozenset({"start", "stop", "open"}),
    "dashboard": frozenset({"start", "stop", "serve", "install"}),
    "controls": frozenset({"set"}),
}
GT_OWNER_SUBCOMMAND_OPERATIONS: dict[tuple[str, str], frozenset[str]] = {
    ("db", "postgres"): frozenset({"init", "import-current"}),
}
# c123 (owner decision E1): the owner's levers over project authorization (GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001)
# are refused to every agent context, bound or not, like the owner operations above: gt projects set-authorization, gt
# projects move-item (a move can carry intake work into an authorized project), and gt projects record when it creates
# an execution project, which starts authorized (_creates_execution_project). Amendments of existing records, program
# creation and the nested projects dependencies and formal-links records are not levers.
GT_OWNER_LEVERS = {"projects": frozenset({"set-authorization", "move-item", "record"})}
GT_GLOBAL_OPTIONS_WITH_VALUES = frozenset({"--config"})
GT_MODULES = frozenset({"groundtruth_kb", "groundtruth_kb.cli"})
_PYTHON_VALUE_OPTIONS = frozenset({"-X", "-W", "--check-hash-based-pycs"})
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
# c123 (owner decision A2; batch design WP1 item 4, change 3): ending a process, controlling the PostgreSQL cluster and
# reaching the authority database with the PostgreSQL programs are owner operations whatever the target: a process name
# or number does not say whose process it is, and the authority database is read and changed through the gt CLI. A
# context still ends its own shell's jobs (Stop-Job, Remove-Job, kill %1) and reads process and cluster state
# (Get-Process, tasklist, pg_ctl status, pg_isready, a program's --version or --help).
PROCESS_TERMINATORS = frozenset({"stop-process", "spps", "taskkill", "tskill", "pkill", "killall"})
_PROCESS_TERMINATING_CALL_RE = re.compile(r"\.(?:kill|terminate)\s*\(", re.IGNORECASE)
PG_CTL_CHANGING_ACTIONS = frozenset(
    {"start", "stop", "restart", "kill", "promote", "reload", "init", "initdb", "register", "unregister", "logrotate"}
)
POSTGRESQL_PROGRAMS = frozenset(
    {
        "postgres",
        "initdb",
        "pg_resetwal",
        "psql",
        "pg_dump",
        "pg_dumpall",
        "pg_restore",
        "createdb",
        "dropdb",
        "createuser",
        "dropuser",
        "vacuumdb",
        "reindexdb",
        "clusterdb",
        "pg_basebackup",
        "pg_receivewal",
        "pg_recvlogical",
        "pg_rewind",
        "pg_upgrade",
        "pg_amcheck",
        "pg_checksums",
    }
)
# The options with which those programs only print their version or usage.
_POSTGRESQL_INFORMATIONAL_OPTIONS = frozenset({"-V", "--version", "-?", "--help"})
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
    # c123 (owner decision A5, row 18): sed's -i also counts inside a flag bundle (-ni, -Ei) and as --in-place.
    r"sed\s+(?:[^|;&]*\s)?(?:-[nrEsuzb]*i|--in-place)\b|awk\s+[^|;&]*-i\s+inplace\b|"
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

REDIRECT_OPERATOR_TOKEN_RE = re.compile(r"&?>{1,2}|>\|")

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


# c123 (owner decision A5; batch design WP1 section 6, row 18): two over-collections failed a claimed edit's claim check
# (the native check refused `sed -i 's/a/b/' f.txt` because the script "s/a/b/" lies outside the claim). sed's and
# awk's script operand is not a file: without a script option (sed's -e, -f, --expression and --file; awk's -f, -e, -E,
# --file, --source and --exec) the first operand is the script, and the values of their options are not files either.
# A copy's sources are read, not written, so only its destination is a target.
_SED_VALUE_OPTIONS = frozenset({"-e", "-f", "-l", "--expression", "--file", "--line-length"})
_SED_SCRIPT_OPTIONS = frozenset({"-e", "-f", "--expression", "--file"})
_AWK_VALUE_OPTIONS = frozenset(
    {
        "-f",
        "-v",
        "-F",
        "-i",
        "-e",
        "-E",
        "-l",
        "-W",
        "--file",
        "--assign",
        "--field-separator",
        "--include",
        "--source",
        "--exec",
        "--load",
    }
)
_AWK_SCRIPT_OPTIONS = frozenset({"-f", "-e", "-E", "--file", "--source", "--exec"})
_AWK_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.DOTALL)


def _extract_sed_awk_paths(tokens: list[str]) -> list[str]:
    """The files sed or awk reads, and with -i writes: its operands after the script, option values excluded (c123).

    awk's var=value operands are assignments, not files. sed's -i takes its backup suffix attached (-i.bak).
    """
    awk = _executable_name(tokens[0]).removesuffix(".exe") == "awk"
    values, scripts = (_AWK_VALUE_OPTIONS, _AWK_SCRIPT_OPTIONS) if awk else (_SED_VALUE_OPTIONS, _SED_SCRIPT_OPTIONS)
    operands: list[str] = []
    scripted = False
    index = 1
    while index < len(tokens):
        word = _clean_shell_token(tokens[index])
        if word == "--":
            operands.extend(tokens[index + 1 :])
            break
        if word.startswith("--"):
            name = word.split("=", 1)[0]
            scripted = scripted or name in scripts
            index += 2 if name in values and "=" not in word else 1
            continue
        if word.startswith("-") and len(word) > 1:
            letters = word[1:]
            for position, letter in enumerate(letters):
                if not awk and letter == "i":
                    break  # the rest of the bundle is sed's backup suffix
                scripted = scripted or f"-{letter}" in scripts
                if f"-{letter}" in values:
                    # The rest of the bundle is the option's value, or the next word when the option ends it.
                    index += 1 if position == len(letters) - 1 else 0
                    break
            index += 1
            continue
        if not (awk and _AWK_ASSIGNMENT.fullmatch(word)):
            operands.append(tokens[index])
        index += 1
    return operands if scripted else operands[1:]


_COPY_VERBS = frozenset({"copy-item", "copy", "cp", "copy-itemproperty"})
_COPY_SOURCE_PARAMETERS = frozenset({"-path", "-literalpath", "-lp", "-pspath"})
# Copy-Item's and Copy-ItemProperty's valued parameters and PowerShell's valued common parameters, and cp's --suffix.
_COPY_VALUE_PARAMETERS = frozenset(
    {
        "-filter",
        "-include",
        "-exclude",
        "-credential",
        "-tosession",
        "-fromsession",
        "-name",
        "-erroraction",
        "-ea",
        "-warningaction",
        "-wa",
        "-informationaction",
        "-infa",
        "-progressaction",
        "-proga",
        "-errorvariable",
        "-ev",
        "-warningvariable",
        "-wv",
        "-informationvariable",
        "-iv",
        "-outvariable",
        "-ov",
        "-outbuffer",
        "-ob",
        "-pipelinevariable",
        "-pv",
        "--suffix",
    }
)
_COPY_SWITCHES = frozenset(
    {
        "-recurse",
        "-force",
        "-container",
        "-passthru",
        "-whatif",
        "-wi",
        "-confirm",
        "-cf",
        "-verbose",
        "-vb",
        "-debug",
        "-db",
        "-usetransaction",
        "--archive",
        "--attributes-only",
        "--backup",
        "--copy-contents",
        "--debug",
        "--dereference",
        "--force",
        "--interactive",
        "--keep-directory-symlink",
        "--link",
        "--no-clobber",
        "--no-dereference",
        "--no-preserve",
        "--no-target-directory",
        "--one-file-system",
        "--parents",
        "--preserve",
        "--recursive",
        "--reflink",
        "--remove-destination",
        "--sparse",
        "--strip-trailing-slashes",
        "--symbolic-link",
        "--update",
        "--verbose",
    }
)
# POSIX cp's short flags, which take no value; a bundle of them (-rf, -av) is a flag word.
_CP_SHORT_FLAGS = frozenset("abdfHilLnPpRrsTuvxZ")


def _extract_copy_destination(tokens: list[str]) -> list[str]:
    """The destination a copy writes: Copy-Item (cpi, and copy or cp in PowerShell), cmd's copy, POSIX cp (c123).

    -Destination, or cp's -t and --target-directory, when named; otherwise the last operand, which is cmd's and cp's
    destination and binds to Copy-Item's -Destination. Copy-ItemProperty's destination is its second operand, or its
    first when -Path names the source. A copy that names no destination writes into the current directory, which is
    then the target. Its sources (-Path, -LiteralPath, the other operands) are read. An option the gate does not know
    could take the destination's place, so every operand is then a target, as before c123.
    """
    property_copy = _canonical_write_verb(tokens[0]) == "copy-itemproperty"
    destination: list[str] = []
    operands: list[str] = []
    named_source = False
    known = True
    index = 1
    while index < len(tokens):
        word = _clean_shell_token(tokens[index])
        if word.startswith("-") and len(word) > 1:
            head, separator, attached = word.partition("=" if word.startswith("--") else ":")
            name = head.lower()
            step = 1 if separator else 2
            if name in ("-destination", "--target-directory") or head == "-t":
                destination.extend([attached] if separator else tokens[index + 1 : index + 2])
                index += step
                continue
            if name in _COPY_SOURCE_PARAMETERS:
                named_source = True
                index += step
                continue
            if name in _COPY_VALUE_PARAMETERS or head == "-S":
                index += step
                continue
            if name not in _COPY_SWITCHES and not (not word.startswith("--") and set(word[1:]) <= _CP_SHORT_FLAGS):
                known = False
            index += 1
            continue
        if word != "+" and not _CMD_SWITCH_RE.fullmatch(word):
            operands.append(tokens[index])
        index += 1
    if destination:
        return destination
    if not known:
        return operands or ["."]
    if property_copy:
        position = 0 if named_source else 1
        return operands[position : position + 1] or ["."]
    if named_source:
        return operands[:1] or ["."]
    return operands[-1:] if len(operands) > 1 else ["."]


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
        # c123 (batch design WP1, residual row 6): Set-Item and Clear-Item write the item they name. On the session-state
        # drives (Env:, Variable:, Function:, Alias:) they hold no file and are not writes (_ITEM_WRITE_RE); on the
        # machine-configuration drives they are owner operations (_machine_configuration_write).
        "set-item",
        "clear-item",
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
    # c123 (residual rows 5 and 6): si and cli; sc is Set-Content in Windows PowerShell, and sc.exe when its first
    # operand is one of sc.exe's verbs or a \\server name (_sc_runs_sc_exe).
    "si": "set-item",
    "cli": "clear-item",
    "sc": "set-content",
}
# The aliases matched by their own patterns in _NAMED_WRITE_RE, each with a condition on what follows.
_CONDITIONAL_WRITE_ALIASES = frozenset({"si", "cli", "sc"})
_ITEM_WRITE_VERBS = frozenset({"set-item", "clear-item"})
_SC_EXE_VERBS = frozenset(
    {
        "query",
        "queryex",
        "start",
        "pause",
        "interrogate",
        "continue",
        "stop",
        "config",
        "description",
        "failure",
        "failureflag",
        "sidtype",
        "privs",
        "managedaccount",
        "qc",
        "qdescription",
        "qfailure",
        "qfailureflag",
        "qsidtype",
        "qprivs",
        "qtriggerinfo",
        "qpreferrednode",
        "qmanagedaccount",
        "qprotection",
        "quserservice",
        "delete",
        "create",
        "control",
        "sdshow",
        "sdset",
        "showsid",
        "triggerinfo",
        "preferrednode",
        "getdisplayname",
        "getkeyname",
        "enumdepend",
        "boot",
        "lock",
        "querylock",
    }
)


def _sc_runs_sc_exe(relevant: list[str]) -> bool:
    """Whether a command led by sc runs sc.exe: no operand, one of its verbs, or a \\\\server name (c123, row 5)."""
    operand = _clean_shell_token(relevant[1]).strip("'\"").lower() if len(relevant) > 1 else ""
    return not operand or operand in _SC_EXE_VERBS or operand.startswith("\\\\")


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
    (_POWERSHELL_PATH_ARG_VERBS - _ITEM_WRITE_VERBS) | _POWERSHELL_BOTH_PATHS_VERBS | _POWERSHELL_DESTINATION_VERBS
)
_ALIAS_WRITE_WORDS = _word_alternation(
    (frozenset(_POWERSHELL_WRITE_ALIASES) - {"iwr", "irm"} - _CONDITIONAL_WRITE_ALIASES) | _DUAL_SYNTAX_WRITE_VERBS
)
# c123 (batch design WP1, residual row 6): an item write whose target is on a session-state drive is not a file write.
# A quoted target is masked in the view these patterns read, so a quoted session-state path still counts (refused).
_NOT_SESSION_STATE = r"(?!\s+(?:-(?:literal)?path[\s:]+)?(?:env|variable|function|alias):)"
_SESSION_STATE_DRIVES = ("env:", "variable:", "function:", "alias:")
# c123 (row 5): sc is Set-Content unless one of sc.exe's verbs or a \\server name follows it.
_SC_EXE_WORDS = _word_alternation(_SC_EXE_VERBS)
_NAMED_WRITE_RE = re.compile(
    rf"\b(?P<cmdlet>{_CMDLET_WRITE_WORDS})\b"
    rf"|\b(?P<item>set-item|clear-item)\b(?![-.]){_NOT_SESSION_STATE}"
    rf"|{_COMMAND_POSITION}(?P<itemalias>si|cli)\b(?![-.]){_NOT_SESSION_STATE}"
    rf"|{_COMMAND_POSITION}(?P<scalias>sc)\b(?![-.])(?=[ \t]+(?!(?:{_SC_EXE_WORDS})\b)(?!\\\\)[^\s|;&])"
    rf"|{_COMMAND_POSITION}(?P<alias>{_ALIAS_WRITE_WORDS})(?:\.exe)?\b(?![-.])"
    rf"|{_COMMAND_POSITION}(?P<posix>tee|touch|truncate|shred|install|patch|dd|cp|mv|rm|ln)(?:\.exe)?\b(?![-.])"
    r"|\b(?P<sed>sed)\s+(?:[^|;&]*\s)?(?:-[nrEsuzb]*i|--in-place)\b|\b(?P<awk>awk)\s+[^|;&]*-i\s+inplace\b"
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


# c123 (batch design WP1, residual row 10, accepted and stated): New-TemporaryFile and [IO.Path]::GetTempFileName()
# create a file only in the user's temporary directory, outside every governed tree, so they are not writes here; a
# later write to that file goes through a variable and is refused by the unresolved-value rule.


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


# c123 (batch design WP1, residual row 16): a write cmdlet's name given to a help or lookup command (Get-Help
# Export-Csv, Get-Command Remove-Item) is that command's argument, not a write. Those arguments are blanked, to the end
# of the statement, in the view the write patterns read; every other argument position stays as it was.
_HELP_ARGUMENTS_RE = re.compile(
    rf"{_COMMAND_POSITION}(?:get-help|help|man|get-command|gcm|get-alias)\b(?![-.])(?P<arguments>[^|;&\n{{}}()]*)",
    re.IGNORECASE,
)


def _mask_help_arguments(view: str) -> str:
    """The view with each help or lookup command's arguments blanked; every position is kept (c123, row 16)."""
    return _HELP_ARGUMENTS_RE.sub(
        lambda match: view[match.start() : match.start("arguments")] + " " * len(match.group("arguments")), view
    )


def _write_view(command: str) -> str:
    """The view the write patterns read: quoted interiors and help arguments blanked, positions kept (c123)."""
    return _mask_help_arguments(_mask_quoted_spans(command, mask_double=True))


# c123 (batch design WP1, residual rows 2, 7 and 9): commands that write through an option rather than by their name.
# find writes the file -fprint, -fprint0, -fprintf and -fls name, and -delete removes what it matches (not read). curl
# writes the files -o (--output), -c (--cookie-jar) and -D (--dump-header) name, and with -O (--remote-name,
# --remote-name-all) one named from the URL (not read). wget writes the files -O (--output-document), -o
# (--output-file) and -a (--append-output) name, and without -O one named from the URL (not read; --spider writes
# none). Start-Process writes the files -RedirectStandardOutput and -RedirectStandardError name. "-" is standard
# output. In Windows PowerShell 5.1 curl and wget are Invoke-WebRequest aliases, whose -OutFile the web-request
# pattern reads.
_FIND_FILE_OPTIONS = frozenset({"-fprint", "-fprint0", "-fprintf", "-fls"})
_CURL_FILE_OPTIONS = frozenset({"-o", "--output", "-c", "--cookie-jar", "-D", "--dump-header"})
_CURL_REMOTE_NAME = frozenset({"-O", "--remote-name", "--remote-name-all"})
_CURL_SHORT_VALUES = frozenset("AbcCdDeEFHKmoPQrtTuUwxXyYz")
_WGET_FILE_OPTIONS = frozenset({"-O", "--output-document", "-o", "--output-file", "-a", "--append-output"})
_WGET_SHORT_VALUES = frozenset("oaeiBtOTwQPUlARDIX")


def _short_option_values(word: str, values: frozenset[str]) -> list[tuple[str, str | None]]:
    """The options of one short-option bundle (-sSLo out.txt, -qO-), each with its attached value or None (c123)."""
    found: list[tuple[str, str | None]] = []
    letters = word[1:]
    for index, letter in enumerate(letters):
        if letter in values:
            found.append(("-" + letter, letters[index + 1 :] or None))
            break
        found.append(("-" + letter, None))
    return found


def _download_writes(name: str, args: list[str]) -> tuple[list[str], bool] | None:
    """The files curl or wget names to write, and whether it also writes one it does not name (c123, row 7)."""
    files = _CURL_FILE_OPTIONS if name == "curl" else _WGET_FILE_OPTIONS
    shorts = _CURL_SHORT_VALUES if name == "curl" else _WGET_SHORT_VALUES
    named: list[str] = []
    remote_name = False
    document = spider = False
    operands = 0
    index = 0
    while index < len(args):
        word = _clean_shell_token(args[index])
        following = args[index + 1] if index + 1 < len(args) else None
        if word.startswith("--"):
            option, equals, attached = word.partition("=")
            options = [(option, attached if equals else None)]
            takes_value = option in files
        elif word.startswith("-") and len(word) > 1:
            options = _short_option_values(word, shorts)
            takes_value = options[-1][0][1] in shorts
        else:
            operands += 1
            index += 1
            continue
        consumed = 1
        for option, value in options:
            if name == "curl" and option in _CURL_REMOTE_NAME:
                remote_name = True
            if name == "wget" and option in ("-O", "--output-document"):
                document = True
            if name == "wget" and option == "--spider":
                spider = True
            if option in files:
                if value is None and following is not None:
                    value = following
                    consumed = 2
                if value is not None and _clean_shell_token(value).strip("'\"") != "-":
                    named.append(value)
        if takes_value and consumed == 1 and options[-1][1] is None and following is not None:
            consumed = 2  # a value option's value is the next word
        index += consumed
    unnamed = remote_name if name == "curl" else (not document and not spider and operands > 0)
    return (named, unnamed) if named or unnamed else None


def _start_process_redirects(args: list[str]) -> list[str]:
    """The files Start-Process's -RedirectStandardOutput and -RedirectStandardError name (c123, row 9)."""
    found: list[str] = []
    for index, word in enumerate(args):
        if not (word.startswith("-") and len(word) > 1 and not word[1].isdigit()):
            continue
        head, colon, tail = word.partition(":")
        if _start_process_parameter(head) in ("redirectstandardoutput", "redirectstandarderror"):
            if colon and tail:
                found.append(tail)
            elif index + 1 < len(args):
                found.append(args[index + 1])
    return found


# c123 (owner decision A5; batch design WP1 section 6, row 17): Windows and archive tools that write what their operands
# or switches name. robocopy and xcopy write their destination; robocopy's /MOV and /MOVE also remove the sources,
# /MIR and /PURGE remove files under the destination, and /LOG: and /UNILOG: write log files. tar writes its archive
# when it creates, appends, updates, catenates or deletes, and its -C directory (or the current one) when it extracts;
# 7z writes its archive with a, d, u or rn and its -o directory (or the current one) with e or x; expand writes its
# destination; certutil writes the output file of -decode, -decodehex, -encode and -encodehex and the download file of
# -urlcache; mklink writes the link; icacls, attrib and takeown change the files they name (icacls /save writes its
# file); fsutil writes the file its file, hardlink, sparse, objectid and reparsepoint verbs name; cipher /e and /d
# change the files they name, and cipher /w overwrites free space under the directory it names. A form that writes
# without naming its file (an archive on the default device, tar extracting absolute names, a download named from its
# address, an expand without a destination, robocopy /SAVE, fsutil's volume and machine settings, cipher's key
# operations) names nothing the gate can check, so its command is refused whole.
_ROBOCOPY_LOG_SWITCHES = ("/log:", "/log+:", "/unilog:", "/unilog+:")


def _switches_and_operands(args: list[str]) -> tuple[list[str], list[str]]:
    """A Windows tool's switches (/x, /x:value), lower case, and its other words as written (c123, row 17)."""
    switches = [_clean_shell_token(arg).lower() for arg in args if _clean_shell_token(arg).startswith("/")]
    operands = [arg for arg in args if not _clean_shell_token(arg).startswith("/")]
    return switches, operands


def _robocopy_writes(args: list[str]) -> tuple[list[str], bool] | None:
    """robocopy's destination, with /MOV or /MOVE its source, and its log files; /SAVE's job file is not read."""
    switches, operands = _switches_and_operands(args)
    if "/l" in switches or "/?" in switches or len(operands) < 2:
        return None  # a listing, the usage text, or no destination: robocopy copies nothing
    named = [operands[1]]
    if {"/mov", "/move"} & set(switches):
        named.append(operands[0])
    for arg in args:
        word = _clean_shell_token(arg)
        if word.lower().startswith(_ROBOCOPY_LOG_SWITCHES) and word.split(":", 1)[1]:
            named.append(word.split(":", 1)[1])
    return named, any(switch.startswith("/save:") for switch in switches)


def _xcopy_writes(args: list[str]) -> tuple[list[str], bool] | None:
    """xcopy's destination, or the current directory when it names none."""
    switches, operands = _switches_and_operands(args)
    if "/l" in switches or "/?" in switches or not operands:
        return None
    return (operands[1:2] or ["."]), False


_TAR_LONG_MODES = {
    "--create": "c",
    "--append": "r",
    "--update": "u",
    "--catenate": "A",
    "--concatenate": "A",
    "--delete": "D",
    "--extract": "x",
    "--get": "x",
    "--list": "t",
    "--diff": "d",
    "--compare": "d",
}


def _tar_writes(args: list[str]) -> tuple[list[str], bool] | None:
    """The archive tar creates, appends to, updates or deletes from, or the directory it extracts into."""
    mode = ""
    archive: str | None = None
    directory: str | None = None
    to_stdout = absolute = False
    pending: list[str] = []  # the bundle's f and C, each waiting for the next word as its value
    for index, arg in enumerate(args):
        word = _clean_shell_token(arg)
        if pending:
            if pending.pop(0) == "f":
                archive = arg
            else:
                directory = arg
            continue
        if word.startswith("--"):
            name, separator, value = word.partition("=")
            if name in _TAR_LONG_MODES:
                mode = _TAR_LONG_MODES[name]
            elif name in ("--file", "--directory"):
                if separator:
                    archive, directory = (value, directory) if name == "--file" else (archive, value)
                else:
                    pending.append("f" if name == "--file" else "C")
            elif name == "--to-stdout":
                to_stdout = True
            elif name == "--absolute-names":
                absolute = True
            elif name in ("--help", "--usage", "--version"):
                return None
            continue
        old_style = index == 0 and word.isalpha()
        if not (word.startswith("-") or old_style):
            continue  # a member name
        letters = word.lstrip("-")
        for position, letter in enumerate(letters):
            if letter in "crutxAd":
                mode = letter
            elif letter in "fC":
                rest = letters[position + 1 :]
                if rest and not old_style:
                    archive, directory = (rest, directory) if letter == "f" else (archive, rest)
                    break  # the rest of a dashed bundle is the option's value
                pending.append(letter)
            elif letter == "O":
                to_stdout = True
            elif letter == "P":
                absolute = True
    if mode in ("c", "r", "u", "A", "D"):
        if archive is None:
            return [], True  # the default archive device
        return None if _clean_shell_token(archive) == "-" else ([archive], False)
    if mode == "x" and not to_stdout:
        return ([], True) if absolute else ([directory or "."], False)
    return None


_SEVEN_ZIP_NAMES = frozenset({"7z", "7za", "7zr", "7zz", "7zg"})


def _seven_zip_writes(args: list[str]) -> tuple[list[str], bool] | None:
    """The archive 7z adds to, deletes from, updates or renames in, or the directory it extracts into."""
    words = [_clean_shell_token(arg) for arg in args]
    operands = [arg for arg, word in zip(args, words, strict=True) if not word.startswith("-")]
    command = _clean_shell_token(operands[0]).lower() if operands else ""
    if command in ("a", "d", "u", "rn"):
        return (operands[1:2], False) if len(operands) > 1 else ([], True)
    if command in ("e", "x") and not any(word.lower() == "-so" for word in words):
        output = next((word[2:].strip("'\"") for word in words if word.lower().startswith("-o") and len(word) > 2), "")
        return [output or "."], False
    return None


def _expand_writes(args: list[str]) -> tuple[list[str], bool] | None:
    """The destination Windows expand writes; POSIX expand (tab stops) writes standard output."""
    words = [_clean_shell_token(arg).lower() for arg in args]
    if any(word in ("--tabs", "--initial") or word.startswith(("-t", "--tabs=")) for word in words):
        return None
    if {"-d", "/d", "-?", "/?"} & set(words):
        return None  # a listing or the usage text
    operands = [arg for arg, word in zip(args, words, strict=True) if not word.startswith(("-", "/"))]
    if len(operands) > 1:
        return operands[-1:], False
    return ([], True) if operands else None


def _certutil_writes(args: list[str]) -> tuple[list[str], bool] | None:
    """The file certutil decodes or encodes into, or downloads to with -urlcache."""
    words = [_clean_shell_token(arg) for arg in args]
    verbs = {word.lower().lstrip("-/") for word in words if word.startswith(("-", "/"))}
    operands = [arg for arg, word in zip(args, words, strict=True) if not word.startswith(("-", "/"))]
    if verbs & {"decode", "decodehex", "encode", "encodehex"}:
        return (operands[1:2], False) if len(operands) > 1 else ([], True)
    if "urlcache" in verbs:
        position = next((index for index, word in enumerate(operands) if "://" in word), None)
        if position is None:
            return None  # a cache listing or deletion, in the user's cache outside every governed tree
        return (operands[position + 1 : position + 2], False) if position + 1 < len(operands) else ([], True)
    return None


_ICACLS_CHANGES = frozenset(
    {
        "/grant",
        "/deny",
        "/remove",
        "/setowner",
        "/setintegritylevel",
        "/inheritance",
        "/reset",
        "/restore",
        "/substitute",
    }
)
_ATTRIB_FLAG = re.compile(r"[+-][rahsiolpuxvb]", re.IGNORECASE)
_FSUTIL_FILE_WRITES = frozenset(
    {
        ("file", "createnew"),
        ("file", "setzerodata"),
        ("file", "seteof"),
        ("file", "setshortname"),
        ("file", "setvaliddata"),
        ("file", "setcasesensitiveinfo"),
        ("file", "setstrictlysequential"),
        ("hardlink", "create"),
        ("sparse", "setflag"),
        ("sparse", "setrange"),
        ("objectid", "set"),
        ("objectid", "delete"),
        ("objectid", "create"),
        ("reparsepoint", "delete"),
    }
)


def _permission_tool_writes(name: str, args: list[str]) -> tuple[list[str], bool] | None:
    """What mklink, icacls, attrib, takeown, fsutil or cipher writes (c123, row 17); None for another program."""
    words = [_clean_shell_token(arg) for arg in args]
    lowered = [word.lower() for word in words]
    if name == "mklink":
        operands = [arg for arg, word in zip(args, words, strict=True) if not word.startswith("/")]
        return (operands[:1], False) if operands else None
    if name == "icacls":
        if "/save" in lowered:
            position = lowered.index("/save")
            return (args[position + 1 : position + 2], False) if position + 1 < len(args) else ([], True)
        changes = any(word.split(":", 1)[0] in _ICACLS_CHANGES for word in lowered)
        return (args[:1], False) if changes and args else None
    if name == "attrib":
        if not any(_ATTRIB_FLAG.fullmatch(word) for word in words):
            return None  # a display of attributes
        operands = [
            arg for arg, word in zip(args, words, strict=True) if not _ATTRIB_FLAG.fullmatch(word) and word[:1] != "/"
        ]
        return (operands or ["."]), False
    if name == "takeown":
        if "/f" not in lowered:
            return None
        position = lowered.index("/f")
        return (args[position + 1 : position + 2], False) if position + 1 < len(args) else ([], True)
    if name == "fsutil":
        if len(lowered) < 2 or lowered[0] == "fsinfo":
            return None
        group, verb = lowered[0], lowered[1]
        if verb.startswith("query") or verb in ("list", "diskfree", "info", "help", "/?"):
            return None
        if (group, verb) in _FSUTIL_FILE_WRITES:
            return (args[2:3], False) if len(args) > 2 else ([], True)
        return [], True  # a volume or machine setting, which names no file the gate checks
    if name == "cipher":
        for word, low in zip(words, lowered, strict=True):
            if low.startswith("/w"):
                directory = word.split(":", 1)[1] if ":" in word else ""
                return ([directory], False) if directory else ([], True)
        keys = ("/u", "/k", "/x", "/rekey", "/flushcache")
        if any(low in keys or low.startswith(("/r:", "/x:", "/adduser", "/removeuser")) for low in lowered):
            return [], True
        if "/e" in lowered or "/d" in lowered:
            operands = [arg for arg, word in zip(args, words, strict=True) if not word.startswith("/")]
            scopes = [word.split(":", 1)[1] for word, low in zip(words, lowered, strict=True) if low.startswith("/s:")]
            return (operands + scopes) or ["."], False
        return None
    return None


_PERMISSION_TOOLS = frozenset({"mklink", "icacls", "attrib", "takeown", "fsutil", "cipher"})


def _option_writes(tokens: list[str]) -> tuple[list[str], bool] | None:
    """The files one command writes through its options or, for row 17's tools, its operands, and whether it writes
    one it does not name; None if none."""
    words, _called = _statement_program(tokens)
    if not words:
        return None
    name = _executable_name(words[0]).removesuffix(".exe")
    args = words[1:]
    # c123 (owner decision A5, row 17): the system write tools.
    if name == "robocopy":
        return _robocopy_writes(args)
    if name == "xcopy":
        return _xcopy_writes(args)
    if name in ("tar", "bsdtar"):
        return _tar_writes(args)
    if name in _SEVEN_ZIP_NAMES:
        return _seven_zip_writes(args)
    if name == "expand":
        return _expand_writes(args)
    if name == "certutil":
        return _certutil_writes(args)
    if name in _PERMISSION_TOOLS:
        return _permission_tool_writes(name, args)
    if name == "find":
        named = [
            args[index + 1]
            for index, word in enumerate(args[:-1])
            if _clean_shell_token(word).lower() in _FIND_FILE_OPTIONS
        ]
        deletes = any(_clean_shell_token(word).lower() == "-delete" for word in args)
        return (named, deletes) if named or deletes else None
    if name in ("curl", "wget"):
        return _download_writes(name, args)
    if name in ("start-process", "saps"):
        named = _start_process_redirects(args)
        return (named, False) if named else None
    return None


def _stage_option_writes(command: str) -> list[tuple[list[str], bool]]:
    """_option_writes for each stage of a command the gate parses (c123)."""
    found: list[tuple[list[str], bool]] = []
    for stage in _split_pipeline_stages(command):
        tokens = _shell_split(stage)
        written = _option_writes(tokens) if tokens else None
        if written is not None:
            found.append(written)
    return found


# c123 (batch design WP1, residual row 4): a change of directory moves every relative target after it. A single
# leading cd, chdir, Set-Location, sl, pushd or Push-Location to a literal directory is read: the command's relative
# targets are judged from that directory. Any other change (a later one, a second one, popd, cd -, cd with no operand,
# one inside a group or a launched command, or one to a directory the shell supplies) leaves the relative targets
# unread, so a write among them is refused whole.
_DIRECTORY_CHANGE_VERBS = frozenset(
    {"cd", "chdir", "set-location", "sl", "pushd", "push-location", "popd", "pop-location"}
)


def _directory_change_operand(words: list[str]) -> str | None:
    """The literal directory a change of directory names; None when it names none the gate can read (c123)."""
    verb = _executable_name(words[0]).removesuffix(".exe")
    if verb in ("popd", "pop-location"):
        return None
    operands: list[str] = []
    index = 1
    while index < len(words):
        word = words[index]
        lowered = _clean_shell_token(word).lower()
        if lowered in ("-path", "-literalpath"):
            if index + 1 < len(words):
                operands.append(words[index + 1])
            index += 2
            continue
        if lowered.startswith("-") and lowered not in ("-",) and verb not in ("cd", "chdir", "pushd"):
            return None  # a Set-Location or Push-Location parameter the gate does not read
        if lowered.startswith("-") and verb in ("cd", "chdir", "pushd") and lowered in ("-l", "-p", "-e", "-@"):
            index += 1  # bash's cd -L, -P, -e and -@
            continue
        operands.append(word)
        index += 1
    if len(operands) != 1:
        return None
    operand = operands[0]
    literal = _clean_shell_token(operand).strip()
    if not literal or literal in ("-", "~") or _unresolved_value(operand):
        return None
    if literal[:1] in ("'", '"') and literal[-1:] == literal[:1]:
        literal = literal[1:-1]
    return literal


def _leading_directory(command: str) -> str | None:
    """The directory a command's relative targets are judged from: "" when it changes none, the literal directory of a
    single leading change, or None when a change leaves the targets unread (c123, row 4)."""
    changes = [
        line
        for line, _text in _walked_commands(command)
        if line != UNINSPECTABLE_SHELL_COMMAND
        and (words := _shell_split(line))
        and _executable_name(words[0]).removesuffix(".exe") in _DIRECTORY_CHANGE_VERBS
    ]
    if not changes:
        return ""
    flat, _groups = _flatten_groups(command)
    statements = _split_statements(flat)
    if len(changes) != 1 or not statements:
        return None
    first = _shell_split(statements[0])
    if not first:
        return None
    words, called = _statement_program(first)
    if called or not words or " ".join(words) != changes[0]:
        return None
    return _directory_change_operand(words)


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

    # c123 (batch design WP1, residual row 5): sc.exe controls services (the owner rule judges it); sc is Set-Content.
    if verb.removesuffix(".exe") == "sc" and (verb.endswith(".exe") or _sc_runs_sc_exe(relevant)):
        return None
    # c121: an alias reads as its cmdlet, and a trailing .exe (Git Bash's mkdir.exe) does not hide the verb.
    verb = _canonical_write_verb(verb)
    # c123 (owner decision A5, row 18): sed's and awk's script and a copy's sources are not targets.
    if verb in ("sed", "awk"):
        return _extract_sed_awk_paths, relevant
    if verb in _COPY_VERBS:
        return _extract_copy_destination, relevant
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


def _direct_git_subcommand_and_args(stage: str) -> tuple[str | None, list[str]]:
    """Return a direct Git subcommand and the words after it, accounting for executable/global options (c123)."""
    tokens = _shell_split(stage)
    if not tokens:
        return None, []
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None, []
    relevant = [_clean_shell_token(token) for token in tokens[verb_index:]]
    executable = Path(relevant[0]).name.lower()
    if executable not in {"git", "git.exe"}:
        return None, []

    index = 1
    while index < len(relevant):
        token = relevant[index]
        if token == "--":
            index += 1
            break
        if token in GIT_GLOBAL_OPTIONS_WITH_VALUES:
            if index + 1 >= len(relevant):
                return None, []
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
        return token.lower(), relevant[index + 1 :]
    if index < len(relevant):
        return relevant[index].lower(), relevant[index + 1 :]
    return None, []


def _direct_git_subcommand(stage: str) -> str | None:
    """Return a direct Git subcommand, accounting for executable/global options."""
    return _direct_git_subcommand_and_args(stage)[0]


# c123 (batch design WP1, item 3): hash-object, worktree and config read or write by their arguments, so their names
# alone cannot judge them. Each is a read only in its read forms, and an option the gate does not know fails closed.
_GIT_CONFIG_READ_ACTIONS = frozenset({"--get", "--get-all", "--get-regexp", "--get-urlmatch", "-l", "--list"})
_GIT_CONFIG_WRITE_ACTIONS = frozenset(
    {"--add", "--replace-all", "--unset", "--unset-all", "--rename-section", "--remove-section", "-e", "--edit"}
)
_GIT_CONFIG_VALUE_OPTIONS = frozenset(
    {"--file", "-f", "--blob", "--type", "--default", "--value", "--url", "--comment"}
)
_GIT_CONFIG_FLAGS = frozenset(
    {
        "--global",
        "--system",
        "--local",
        "--worktree",
        "--includes",
        "--no-includes",
        "--show-origin",
        "--show-scope",
        "--null",
        "-z",
        "--name-only",
        "--bool",
        "--int",
        "--bool-or-int",
        "--path",
        "--expiry-date",
        "--no-type",
        "--fixed-value",
        "--all",
        "--regexp",
    }
)
_GIT_CONFIG_READ_VERBS = frozenset({"get", "list"})
_GIT_CONFIG_WRITE_VERBS = frozenset({"set", "unset", "rename-section", "remove-section", "edit"})


def _git_config_read_only(args: list[str]) -> bool:
    """Whether git config reads: a read action, no write action, no legacy set form, no unknown option (c123)."""
    read = False
    operands: list[str] = []
    index = 0
    while index < len(args):
        word = args[index]
        if word == "--":
            operands.extend(args[index + 1 :])
            break
        if word.startswith("-") and word != "-":
            name = word.split("=", 1)[0]
            if name in _GIT_CONFIG_WRITE_ACTIONS:
                return False
            if name in _GIT_CONFIG_READ_ACTIONS:
                read = True
            elif name in _GIT_CONFIG_VALUE_OPTIONS:
                index += 0 if "=" in word else 1
            elif name not in _GIT_CONFIG_FLAGS:
                return False
        else:
            operands.append(word)
        index += 1
    if operands and operands[0].lower() in _GIT_CONFIG_WRITE_VERBS:
        return False
    if operands and operands[0].lower() in _GIT_CONFIG_READ_VERBS:
        read = True
    return read


def _git_read_only(subcommand: str | None, args: list[str]) -> bool:
    """Whether git hash-object, worktree or config runs in one of its read forms (c123; batch design WP1, item 3), or
    branch, stash, remote, reflog or symbolic-ref in one of its list forms (c123, owner decision A3)."""
    if subcommand == "hash-object":
        options = args[: args.index("--")] if "--" in args else args
        # -w writes the object, alone or inside a short-option bundle (-wt blob).
        return not any(word.startswith("-") and not word.startswith("--") and "w" in word[1:] for word in options)
    if subcommand == "worktree":
        operands = [word for word in args if not word.startswith("-")]
        return bool(operands) and operands[0].lower() == "list"
    if subcommand == "config":
        return _git_config_read_only(args)
    words = _without_redirects(args)
    if subcommand == "branch":
        return _git_branch_lists(words)
    if subcommand == "stash":
        return bool(words) and words[0].lower() in ("list", "show") and not _names_git_output(words)
    if subcommand == "remote":
        rest = [word for word in words if word not in ("-v", "--verbose")]
        return not rest or rest[0].lower() in ("get-url", "show")
    if subcommand == "reflog":
        if _names_git_output(words):
            return False
        return not words or words[0].lower() in ("show", "exists", "list") or words[0].startswith("-")
    if subcommand == "symbolic-ref":
        operands = [word for word in words if not word.startswith("-")]
        flags = [word for word in words if word.startswith("-")]
        return len(operands) == 1 and all(flag in _GIT_SYMBOLIC_REF_READ_FLAGS for flag in flags)
    return False


# c123 (owner decision A3; batch design WP1 item 3, the optional list forms): branch, stash, remote, reflog and
# symbolic-ref list or show in some forms and write in others, so their names alone cannot judge them either. Each is a
# read only in its list forms; an option the gate does not know fails closed.
# - branch: no operand, or a listing option (--list, -a, -r, -v, --show-current, --contains, --merged and their
#   negations, --points-at), with no option that creates, deletes, renames, copies or sets an upstream;
# - stash list and stash show; remote with no operand, -v, get-url or show; reflog show (also reflog with no
#   subcommand or with log options only, which is show, and reflog exists and list);
# - symbolic-ref with one operand (reading a ref; a second operand or -d writes).
# stash, reflog and the log options they pass on write a file with --output.
_GIT_BRANCH_LIST_OPTIONS = frozenset(
    {
        "--list",
        "--all",
        "--remotes",
        "--verbose",
        "--show-current",
        "--contains",
        "--no-contains",
        "--merged",
        "--no-merged",
        "--points-at",
    }
)
_GIT_BRANCH_NEUTRAL_OPTIONS = frozenset(
    {
        "--color",
        "--no-color",
        "--column",
        "--no-column",
        "--sort",
        "--format",
        "--abbrev",
        "--no-abbrev",
        "--ignore-case",
        "--omit-empty",
        "--quiet",
    }
)
# The branch options whose value may be the next word; their value is no new branch name.
_GIT_BRANCH_VALUE_OPTIONS = frozenset({"--sort", "--format", "--points-at"})
_GIT_SYMBOLIC_REF_READ_FLAGS = frozenset({"-q", "--quiet", "--short", "--no-short", "--recurse", "--no-recurse"})
_REDIRECT_OPERATOR_WORD = re.compile(r"(?:\d+|\*|&)?(?:>{1,2}|<)")
_REDIRECT_WORD = re.compile(r"(?:\d+|\*|&)?(?:>{1,2}|<).*", re.DOTALL)


def _without_redirects(args: list[str]) -> list[str]:
    """A Git call's words without its redirections (2>&1, > out.txt): those are the shell's, not Git's (c123)."""
    words: list[str] = []
    skip = False
    for word in args:
        if skip:
            skip = False
        elif _REDIRECT_OPERATOR_WORD.fullmatch(word):
            skip = True  # the operator stands alone; its target is the next word
        elif not _REDIRECT_WORD.fullmatch(word):
            words.append(word)
    return words


def _names_git_output(words: list[str]) -> bool:
    """Whether a Git call passes --output, which writes the file it names (c123)."""
    return any(word.split("=", 1)[0] == "--output" for word in words)


def _git_branch_lists(words: list[str]) -> bool:
    """Whether git branch lists branches: a listing option or no operand, and no option that writes (c123, A3)."""
    listing = False
    operands: list[str] = []
    index = 0
    while index < len(words):
        word = words[index]
        if word == "--":
            operands.extend(words[index + 1 :])
            break
        if word.startswith("--"):
            name = word.split("=", 1)[0]
            if name in _GIT_BRANCH_LIST_OPTIONS:
                listing = True
            elif name not in _GIT_BRANCH_NEUTRAL_OPTIONS:
                return False  # an option that writes (--delete, --move, --copy, --set-upstream-to) or is unknown
            index += 2 if name in _GIT_BRANCH_VALUE_OPTIONS and "=" not in word else 1
            continue
        if word.startswith("-") and len(word) > 1:
            for letter in word[1:]:
                if letter in "lavr":
                    listing = True
                elif letter not in "iq":
                    return False  # -d, -D, -m, -M, -c, -C, -u, -f, -t or an unknown option
            index += 1
            continue
        operands.append(word)
        index += 1
    return listing or not operands


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
            # c123: >| (noclobber's override) is a redirection, not a pipe.
            width = 0 if text[index - 1 : index] == ">" else 2 if following == "|" else 1
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
    same_process: bool = False,
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
    led by a quoted string is an expression, not a program. c123 (owner decision A6): same_process walks only what runs
    in the shell's own process: the statements, groups, string subexpressions and Invoke-Expression text, not the
    command a nested shell is handed or a launcher runs, which runs in another process.
    """
    if _depth > _INNER_COMMAND_DEPTH or _nesting > _GROUP_DEPTH:
        return [(UNINSPECTABLE_SHELL_COMMAND, command)]
    flat, groups = _flatten_groups(command)
    found: list[tuple[str, str]] = []
    if not values:
        for statement in _split_statements(flat):
            found.extend(
                _statement_commands(
                    statement,
                    text=command,
                    strict=strict,
                    powershell=powershell,
                    same_process=same_process,
                    _depth=_depth,
                    _nesting=_nesting,
                )
            )
    for only_values, body in groups:
        found.extend(
            _walked_commands(
                body,
                strict=strict,
                values=only_values,
                powershell=powershell,
                same_process=same_process,
                _depth=_depth,
                _nesting=_nesting + 1,
            )
        )
    for body in _string_subexpressions(flat):
        found.extend(
            _walked_commands(
                body,
                strict=strict,
                powershell=powershell,
                same_process=same_process,
                _depth=_depth,
                _nesting=_nesting + 1,
            )
        )
    return found


def _statement_commands(
    statement: str,
    *,
    text: str,
    strict: bool,
    powershell: bool,
    _depth: int,
    _nesting: int,
    same_process: bool = False,
) -> list[tuple[str, str]]:
    """The command lines one flattened statement of text runs: its own line and what it hands on (c122)."""
    found: list[tuple[str, str]] = []
    cut = _mask_quoted_spans(statement, mask_double=True).rfind(")")
    if cut >= 0 and statement[cut + 1 :].strip():
        # A POSIX case pattern ends at a parenthesis the statement never opened (case $x in a) ...); its command runs.
        found.extend(
            _walked_commands(
                statement[cut + 1 :], strict=strict, same_process=same_process, _depth=_depth, _nesting=_nesting + 1
            )
        )
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
                _walked_commands(
                    " ".join(rest),
                    strict=strict,
                    powershell=True,
                    same_process=same_process,
                    _depth=_depth,
                    _nesting=_nesting + 1,
                )
            )
        return found
    line = " ".join(words)
    found.append((line, text))
    handed, recognized = _handed_command(line) if not same_process else (None, False)
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
                _walked_commands(
                    evaluated,
                    strict=not literal,
                    powershell=True,
                    same_process=same_process,
                    _depth=_depth + 1,
                    _nesting=_nesting,
                )
            )
    for launched in (_launched_commands(words) or []) if not same_process else []:
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
        subcommand, args = _direct_git_subcommand_and_args(line)
        if (
            subcommand not in DIRECT_GIT_READ_ONLY_SUBCOMMANDS
            and not _git_read_only(subcommand, args)
            and not _git_informational_only(line)
        ):
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


def _gt_arguments(tokens: list[str]) -> list[str] | None:
    """The words a gt invocation passes to gt, as written; None when the tokens run another program.

    gt, gt.exe or a path to either, or python (py) -m groundtruth_kb. c123 (owner decision E1): the owner-operation,
    owner-lever and program rules read gt commands through this one parser. A module the shell supplies (python -m
    $module) may be groundtruth_kb, so it gives [UNINSPECTABLE_SHELL_COMMAND].
    """
    words = [_clean_shell_token(token) for token in tokens]
    executable = _executable_name(words[0]).removesuffix(".exe")
    if executable == "gt":
        return tokens[1:]
    if executable != "py" and not executable.startswith("python"):
        return None
    index = 1
    # c123 (batch design WP1, G27): python's -X and -W take a value (python -X utf8 -m groundtruth_kb ...).
    while index < len(words) and words[index].startswith("-") and words[index] != "-m":
        index += 2 if words[index] in _PYTHON_VALUE_OPTIONS else 1
    if index + 1 < len(words) and words[index] == "-m" and _unresolved_value(tokens[index + 1]):
        return [UNINSPECTABLE_SHELL_COMMAND]
    if index + 1 >= len(words) or words[index] != "-m" or words[index + 1] not in GT_MODULES:
        return None
    return tokens[index + 2 :]


def _gt_command_words(arguments: list[str], count: int) -> list[str] | None:
    """gt's first `count` command words (group, action, ...), lower case, past its options; None when one of them is a
    value the shell supplies (a variable, an expression), which may name any command (c122; shared since c123)."""
    found: list[str] = []
    index = 0
    while index < len(arguments) and len(found) < count:
        word = _clean_shell_token(arguments[index])
        if word in GT_GLOBAL_OPTIONS_WITH_VALUES:
            index += 2
            continue
        index += 1
        if not word.startswith("-"):
            if _unresolved_value(arguments[index - 1]):
                return None
            found.append(word.lower())
    return found


def _gt_owner_operation(tokens: list[str]) -> str | None:
    """Name the GT-KB owner operation these tokens run through gt or python -m groundtruth_kb, if any.

    c122: a module, group or action word whose value the shell supplies (a variable, an expression) may name an owner
    operation, so it gives UNINSPECTABLE_SHELL_COMMAND. c123 (owner decision A2): gt db postgres init and
    import-current name their operation with a third word.
    """
    arguments = _gt_arguments(tokens)
    if arguments is None:
        return None
    words = None if arguments == [UNINSPECTABLE_SHELL_COMMAND] else _gt_command_words(arguments, 2)
    if words is None:
        return UNINSPECTABLE_SHELL_COMMAND
    if len(words) == 2 and words[1] in GT_OWNER_OPERATIONS.get(words[0], ()):
        return "gt " + " ".join(words)
    actions = GT_OWNER_SUBCOMMAND_OPERATIONS.get((words[0], words[1])) if len(words) == 2 else None
    if actions is not None:
        full = _gt_command_words(arguments, 3)
        if full is None:
            return UNINSPECTABLE_SHELL_COMMAND
        if len(full) == 3 and full[2] in actions:
            return "gt " + " ".join(full)
    return None


def _creates_execution_project(arguments: list[str]) -> bool:
    """Whether gt projects record creates an execution project (c123, owner decision E1).

    Read with _arg_value: --expected-version 0, missing or unreadable (fail closed), and --kind other than program. A
    repeated option is unreadable as well, because click keeps its last value.
    """
    words = [_clean_shell_token(word) for word in arguments]
    names = [word.split("=", 1)[0] for word in words]
    if names.count("--expected-version") > 1 or names.count("--kind") > 1:
        return True
    version = _arg_value(words, "--expected-version")
    kind = _arg_value(words, "--kind")
    creates = version is None or not version.isdigit() or int(version) == 0
    return creates and (kind or "").lower() != "program"


def _owner_lever(command: str, *, _depth: int = 0) -> str | None:
    """Name the owner lever over project authorization a shell command uses, in any command the line runs (c123).

    Owner decision E1 (GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001): gt projects set-authorization, move-item, and
    record when it creates an execution project. Like the owner-operation rule it follows nested shells, chains,
    launchers and argument lists through _walked_commands, and it fails closed on its own: a command the walk cannot
    read, or a gt command whose module, group or action the shell supplies, returns UNINSPECTABLE_SHELL_COMMAND.
    """
    for line, _text in _walked_commands(command, _depth=_depth):
        if line == UNINSPECTABLE_SHELL_COMMAND:
            return UNINSPECTABLE_SHELL_COMMAND
        tokens = _shell_split(line)
        arguments = _gt_arguments(tokens) if tokens else None
        if arguments is None:
            continue
        words = None if arguments == [UNINSPECTABLE_SHELL_COMMAND] else _gt_command_words(arguments, 2)
        if words is None:
            return UNINSPECTABLE_SHELL_COMMAND
        if len(words) == 2 and words[1] in GT_OWNER_LEVERS.get(words[0], ()):
            if words[1] != "record" or _creates_execution_project(arguments):
                return "gt " + " ".join(words)
    return None


def _owner_lever_from_payload(payload: dict[str, Any]) -> str | None:
    command = _command_from_payload(payload, _tool_input(payload), _tool_name(payload).lower())
    return _owner_lever(command) if command else None


def _kills_only_jobs(args: list[str]) -> bool:
    """Whether a kill names only the shell's own jobs (%1, %+, %name), or lists signals (kill -l) (c123, A2)."""
    operands: list[str] = []
    index = 0
    while index < len(args):
        word = args[index]
        if word in ("-l", "-L", "--list", "--table"):
            return True
        if word in ("-s", "-n", "--signal"):
            index += 2
            continue
        if not (word.startswith("-") and len(word) > 1):
            operands.append(word)
        index += 1
    return all(word.startswith("%") for word in operands)


def _process_or_cluster_control(tokens: list[str]) -> str | None:
    """Name the process termination or PostgreSQL cluster or database access these tokens run, if any (c123, A2)."""
    words, _called = _statement_program(tokens)
    if not words:
        return None
    shown = _clean_shell_token(words[0]).replace("\\", "/").rsplit("/", 1)[-1]
    name = _executable_name(words[0]).removesuffix(".exe")
    args = [_clean_shell_token(word) for word in words[1:]]
    lowered = [arg.lower() for arg in args]
    ending = "process termination; a context ends only its own shell's jobs, with Stop-Job, Remove-Job or kill %<job>"
    if name in PROCESS_TERMINATORS or (name == "kill" and not _kills_only_jobs(args)):
        return f"{shown} ({ending})"
    if name == "wmic" and "process" in lowered and {"delete", "terminate"} & set(lowered):
        return f"{shown} process ({ending})"
    if name in ("invoke-cimmethod", "invoke-wmimethod") and "terminate" in lowered:
        return f"{shown} Terminate ({ending})"
    informational = bool(args) and all(arg in _POSTGRESQL_INFORMATIONAL_OPTIONS for arg in args)
    if name == "pg_ctl":
        action = next((arg for arg in lowered if arg in PG_CTL_CHANGING_ACTIONS), None)
        if action is None and ("status" in lowered or informational):
            return None
        return f"{shown}{' ' + action if action else ''} (PostgreSQL cluster control)"
    if name in POSTGRESQL_PROGRAMS and not informational:
        return f"{shown} (direct PostgreSQL access; the authority database is read and changed through the gt CLI)"
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


# c123 (batch design WP1, residual row 6): the registry, certificate and WSMan drives hold machine configuration, so an
# item or item-property write that names one is an owner operation, whatever the harness context.
_MACHINE_CONFIGURATION_DRIVE_RE = re.compile(r"(?:hk[a-z]{1,3}:|registry::|cert:|wsman:)", re.IGNORECASE)
_MACHINE_CONFIGURATION_WRITERS = frozenset(
    {
        "set-item",
        "clear-item",
        "new-item",
        "remove-item",
        "rename-item",
        "move-item",
        "copy-item",
        "set-itemproperty",
        "new-itemproperty",
        "remove-itemproperty",
        "rename-itemproperty",
        "clear-itemproperty",
        "copy-itemproperty",
        "move-itemproperty",
    }
)


def _machine_configuration_write(tokens: list[str]) -> str | None:
    """Name an item write that targets a machine-configuration drive (HKLM:, HKCU:, Registry::, Cert:, WSMan:)."""
    words, _called = _statement_program(tokens)
    if not words:
        return None
    verb = _clean_shell_token(words[0])
    if _canonical_write_verb(verb) not in _MACHINE_CONFIGURATION_WRITERS:
        return None
    for word in words[1:]:
        text = _clean_shell_token(word).strip("'\"")
        if _MACHINE_CONFIGURATION_DRIVE_RE.match(text):
            return f"{verb} on {text} (machine configuration)"
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
    change counts when the command, or the text the walk found the change in, names a GT-KB task or service. c123
    (owner decision A2): ending a process and controlling or reaching the PostgreSQL cluster count whatever the target,
    a .Kill() or .Terminate() call included, wherever the line or a command it hands on or evaluates makes it.
    """
    names_gtkb = _names_gtkb_task_or_service(command)
    for line, text in _walked_commands(command, _depth=_depth):
        if line == UNINSPECTABLE_SHELL_COMMAND:
            return UNINSPECTABLE_SHELL_COMMAND
        tokens = _shell_split(line)
        if not tokens:
            continue
        found = (
            _gt_owner_operation(tokens) or _machine_configuration_write(tokens) or _process_or_cluster_control(tokens)
        )
        if found is not None:
            return found
        verb = _service_control_verb(tokens)
        if verb is not None and (names_gtkb or _names_gtkb_task_or_service(text)):
            return f"{verb} on a GT-KB task or service"
    for text in (command, *_judged_commands(command)):
        call = (
            None
            if text == UNINSPECTABLE_SHELL_COMMAND
            else _PROCESS_TERMINATING_CALL_RE.search(_mask_quoted_spans(text, mask_double=True))
        )
        if call is not None:
            method = call.group(0).rstrip("( \t")
            return (
                f"a {method}() call (process termination; a context ends only its own shell's jobs, with Stop-Job, "
                "Remove-Job or kill %<job>)"
            )
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


def _paths_from_shell(root: Path, command: str, *, redirects: bool = True) -> list[str]:
    """Verb-aware path extraction per DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.

    Tokenize via shlex.split(posix=False), identify the verb (first non-env-prefix
    token), and extract paths ONLY from argument positions semantically meaningful
    to that verb. For pipelines, each stage is tokenized independently. For
    commands NOT matching any verb in the table, returns an empty list; the
    caller's `_has_mutating_signal` check produces the `<unknown-mutating-target>`
    fallback when appropriate.
    """
    paths: list[str] = []
    # c123 (batch design WP1, B149): each output redirection writes the word after its operator, read here like a direct
    # write's target; a word the shell supplies when it runs is left to the unresolved-value rule, which refuses it.
    # A walked line rebuilt from its words is read with redirects=False where a whole-command scan reads them (r12).
    for raw in (_redirect_writes(command or "") or []) if redirects else []:
        if raw is None or _unresolved_value(raw):
            continue
        rel = _normalize(root, _shell_word_literal(raw))
        if rel:
            paths.append(rel)
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
        # c123 (batch design WP1, residual rows 2, 7 and 9): the files a command writes through its options.
        written = _option_writes(tokens)
        for raw in written[0] if written else []:
            if _unresolved_value(raw):
                continue  # refused whole by the unresolved-value rule
            rel = _normalize(root, raw, shell_quoted=True)
            if rel:
                paths.append(rel)
        classification = _classify_command_verb(tokens)
        if classification is None:
            continue
        extractor, relevant = classification
        item_write = _canonical_write_verb(relevant[0]) in _ITEM_WRITE_VERBS
        for raw in extractor(relevant):
            if item_write and _clean_shell_token(raw).strip("'\"").lower().startswith(_SESSION_STATE_DRIVES):
                continue  # c123 (row 6): Env:, Variable:, Function: and Alias: hold no files
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
    token. A parse failure (unbalanced quotes) counts a `>` outside the closed
    quotes as a redirect (c123, batch design WP1, B149 change 5): cmd.exe takes
    a quote character literally and runs such a line, writing the file.
    """
    if not command:
        return False
    lexer = shlex.shlex(command, posix=False, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return ">" in _mask_quoted_spans(command, mask_double=True)
    for index, token in enumerate(tokens):
        if REDIRECT_OPERATOR_TOKEN_RE.fullmatch(token):
            return True
        # c123 (batch design WP1, B149): `>& file` writes the file in POSIX shells; `>&2` and `>&-` duplicate or close.
        if token == ">&" and index + 1 < len(tokens) and not re.fullmatch(r"\d+|-", tokens[index + 1]):
            return True
    return False


_REDIRECT_DEVICES = frozenset({"$null", "nul", "nul:", "/dev/null", "/dev/stdout", "/dev/stderr"})
_REDIRECT_WORD_ENDS = frozenset(" \t\r\n|;&<>()")


def _redirect_writes(command: str) -> list[str | None] | None:
    """The words a command's output redirections write, as written (c123; batch design WP1, B149); None if unreadable.

    Each `>`, `>>`, `>|`, `&>`, `&>>` or `>&` outside quotes writes the word after it; a descriptor before the operator
    (`1>`, `2>>`, `*>`) does not change that. A duplication or a close (`2>&1`, `>&2`, `*>&1`, `>&-`) and a null or
    standard device ($null, NUL, /dev/null, /dev/stdout, /dev/stderr) write no file and are left out. A redirection with
    no word after it is listed as None. A word keeps its quotes, so the unresolved-value rule judges it as written. The
    whole command is scanned at once (stage splitting does not respect double quotes), and a command whose quotes do not
    close cannot be read. A backtick escapes the next character, as in PowerShell.
    """
    writes: list[str | None] = []
    index, length = 0, len(command)
    quote = ""
    while index < length:
        char = command[index]
        if quote:
            if char == quote:
                quote = ""
            index += 1
            continue
        if char in "'\"":
            quote = char
            index += 1
            continue
        if char == "`":
            index += 2
            continue
        if char == "&" and command[index + 1 : index + 2] == ">":
            end = index + 2 + (command[index + 2 : index + 3] == ">")
            duplicates = False
        elif char == ">":
            follower = command[index + 1 : index + 2]
            end = index + 1 + (follower in (">", "|", "&"))
            duplicates = follower == "&"
        else:
            index += 1
            continue
        start = end
        while start < length and command[start] in " \t":
            start += 1
        word_end, word_quote = start, ""
        while word_end < length:
            char = command[word_end]
            if word_quote:
                if char == word_quote:
                    word_quote = ""
            elif char in "'\"":
                word_quote = char
            elif char in _REDIRECT_WORD_ENDS:
                break
            word_end += 1
        if word_quote:
            return None
        word = command[start:word_end]
        index = max(word_end, end)
        if not word:
            writes.append(None)
        elif duplicates and re.fullmatch(r"\d+|-", word):
            continue
        elif _shell_word_literal(word).lower() not in _REDIRECT_DEVICES:
            writes.append(word)
    return None if quote else writes


def _shell_word_literal(word: str) -> str:
    """A shell word's text with its quotes removed (`'a b'.txt` is `a b.txt`); for words without unresolved values."""
    text, quote = [], ""
    for char in word:
        if quote:
            if char == quote:
                quote = ""
            else:
                text.append(char)
        elif char in "'\"":
            quote = char
        else:
            text.append(char)
    return "".join(text)


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


# c123 (batch design WP1, residual row 14): os.open reads only with these flags; any other name, a computed flag or
# a nonzero number may write.
_PYTHON_OS_OPEN_READ_NAMES = frozenset(
    {
        "os",
        "O_RDONLY",
        "O_BINARY",
        "O_TEXT",
        "O_NOINHERIT",
        "O_CLOEXEC",
        "O_NOFOLLOW",
        "O_DIRECTORY",
        "O_NONBLOCK",
        "O_SEQUENTIAL",
        "O_RANDOM",
    }
)


def _python_import_aliases(tree: ast.AST) -> dict[str, tuple[str, str | None]]:
    """What each imported name refers to: (module, None) for a module, (module, name) for an imported name (c123).

    Batch design WP1, residual row 13: `from shutil import copy; copy(a, b)` and `import shutil as sh` hid a write.
    """
    aliases: dict[str, tuple[str, str | None]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                aliases[alias.asname or top] = (alias.name if alias.asname else top, None)
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                aliases[alias.asname or alias.name] = (node.module.split(".")[0], alias.name)
    return aliases


def _python_call_writes(node: ast.Call, aliases: dict[str, tuple[str, str | None]] | None = None) -> bool:
    """Whether one Python call writes a file or directory (c121; c123 reads imported names and computed modes)."""
    aliases = aliases or {}
    func = node.func
    name = _python_call_name(func)
    if name is None:
        return False
    receiver = func.value.id if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) else None
    if receiver in aliases and aliases[receiver][1] is None:
        receiver = aliases[receiver][0].split(".")[0]  # import shutil as sh: sh.copy is shutil.copy
    elif isinstance(func, ast.Name) and func.id in aliases:
        module, imported = aliases[func.id]
        if imported is not None:
            receiver, name = module, imported  # from shutil import copy as c: c is shutil.copy
    if name == "open" and receiver == "os":
        if len(node.args) < 2:
            return True  # flags passed some other way are not read
        for child in ast.walk(node.args[1]):
            if isinstance(child, ast.Attribute | ast.Name):
                word = child.attr if isinstance(child, ast.Attribute) else child.id
                if word in _PYTHON_OS_OPEN_WRITE_FLAGS or word not in _PYTHON_OS_OPEN_READ_NAMES:
                    return True
            elif isinstance(child, ast.Constant) and child.value != 0:
                return True
        return False
    if name in ("open", "ZipFile"):
        method_open = name == "open" and isinstance(func, ast.Attribute) and receiver not in _PYTHON_OPEN_MODULES
        index = 0 if method_open else 1
        mode = next((keyword.value for keyword in node.keywords if keyword.arg == "mode"), None)
        if mode is None and len(node.args) > index:
            mode = node.args[index]
        if mode is None:
            return False
        if _constant_string(mode) is None and not method_open:
            return True  # c123 (row 14): a mode the command computes may write
        return _python_write_mode(mode)
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
        aliases = _python_import_aliases(tree)
        if any(_python_call_writes(node, aliases) for node in ast.walk(tree) if isinstance(node, ast.Call)):
            return True
    return False


def _has_mutating_signal(command: str) -> bool:
    """True when the command carries a mutating signal: a named mutating
    command (MUTATING_COMMAND_RE) or a standalone shell redirect operator
    token (_shell_redirect_present)."""
    # c123 (batch design WP1, residual row 16): the write view blanks help and lookup arguments too.
    shell_view = _write_view(command)
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
        # c123 (residual rows 2, 7 and 9): a command that writes through an option.
        or bool(_stage_option_writes(command))
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


def _has_unread_write(command: str, *, redirects: bool = True) -> bool:
    """Whether the command carries a write whose target the gate does not read (c121).

    A redirect with no word after it (since c123, B149, a redirect's word is read like a direct write's target), a .NET
    write call, a Python write, or a named write command that does not begin a stage the gate parses (inside a script
    block, a group or a subexpression, or after a call operator) names no target the gate can check. Owner decision 2026-09-29 07:56 ("All forms found"): such a command is
    refused whole (unknown_effect_targets), so a claim check never covers one write while another goes unchecked.
    """
    shell_view = _write_view(command)
    if _DOTNET_WRITE_RE.search(shell_view) is not None or _has_python_mutating_signal(command):
        return True
    # c123 (batch design WP1, residual rows 2 and 7): find -delete, curl -O and wget without -O write files they do not
    # name.
    if any(unnamed for _files, unnamed in _stage_option_writes(command)):
        return True
    # c123 (batch design WP1, B149): a redirect names its target, which is read like a direct write's. It stays unread
    # only with no word after its operator, or in a command whose quotes do not close while a > stands in it; a word the
    # shell supplies is caught by the unresolved-value rule below.
    writes = _redirect_writes(command) if redirects else []
    if writes is None:
        if ">" in command:
            return True
    elif None in writes:
        return True
    # c122 (batch design WP1, W and item 8): a target whose value the shell supplies when it runs is not read.
    if _unresolved_target(command, redirects=redirects) is not None:
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
        if _named_writes(_write_view(stage))[verb] and extractor(relevant):
            read[verb] += 1
    return any(count > read[verb] for verb, count in named.items())


def _unresolved_target(command: str, *, redirects: bool = True) -> str | None:
    """The first write target the command names whose value the shell supplies when it runs (c122); None if none.

    Owner decision 2026-09-30 20:52 ("Fix first: c122"; batch design WP1, W and item 8): a write to
    "scratchpad\\<own>\\$x" was judged a write of that literal path, which the native check placed in the context's
    own scratch whatever $x held. A target holding a variable, an expression, an environment variable or a home or
    splat prefix is not read, so its write is refused whole before the native check. The targets judged are the ones
    the verb tables read for a named write command at the start of a stage (a copy's source among them) and git's
    --output file; a parameter's value, such as Set-Content's -Value, is not one. Since c123 (B149) a redirection's word
    is one too.
    """
    redirected = next(
        (raw for raw in (_redirect_writes(command) or []) if redirects and raw is not None and _unresolved_value(raw)),
        None,
    )
    if redirected is not None:
        return redirected
    for stage in _split_pipeline_stages(command):
        try:
            tokens = shlex.split(stage, posix=False)
        except ValueError:
            continue
        written = _option_writes(tokens)
        if written is not None:
            # c123 (residual rows 2, 7 and 9): a file a command writes through an option.
            unresolved = next((target for target in written[0] if _unresolved_value(target)), None)
            if unresolved is not None:
                return unresolved
        outputs = _git_output_targets(tokens)
        if outputs is not None:
            targets = outputs
        else:
            classification = _classify_command_verb(tokens)
            if classification is None:
                continue
            extractor, relevant = classification
            if not _named_writes(_write_view(stage))[_canonical_write_verb(relevant[0])]:
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
    elif "--" in rest:
        paths = rest[rest.index("--") + 1 :]
    else:
        # c123 (batch design WP1, item 3): without --, Git reads the operands as pathspecs too (c119's LO GO step was
        # refused because `git status --short --ignored m13-sentinel` was judged from the working directory).
        paths = _git_pathspecs(subcommand, rest)
    if any(path.startswith(":") or _WILDCARD.search(path) for path in paths):
        # Pathspec magic (":/" names the top of the tree) or a wildcard reaches the top of the Git tree.
        return [os.path.join(base, _GIT_TOPLEVEL) if base else _GIT_TOPLEVEL], True
    roots = [os.path.join(base, path) for path in paths] if base else paths
    return (roots or [base or "."]), True


_GIT_TOPLEVEL = "__gtkb_git_toplevel__"
_GIT_LS_FILES_VALUE_OPTIONS = frozenset(
    {"-x", "-X", "--exclude", "--exclude-from", "--exclude-per-directory", "--with-tree", "--format"}
)
_GIT_GREP_VALUE_OPTIONS = frozenset(
    {
        "-e",
        "-f",
        "-A",
        "-B",
        "-C",
        "-m",
        "--max-count",
        "--max-depth",
        "--threads",
        "--after-context",
        "--before-context",
        "--context",
    }
)


def _git_pathspecs(subcommand: str, rest: list[str]) -> list[str]:
    """The pathspecs of git status, ls-files or grep written without -- (c123; batch design WP1, item 3).

    status: every operand. ls-files: every operand, the values of -x, -X, --exclude*, --with-tree and --format skipped.
    grep: the operands after the pattern, or every operand when -e or -f supplies the pattern; the values of -e, -f,
    -A, -B, -C, -m, --max-count, --max-depth and --threads skipped.
    """
    values = {"ls-files": _GIT_LS_FILES_VALUE_OPTIONS, "grep": _GIT_GREP_VALUE_OPTIONS}.get(subcommand, frozenset())
    operands: list[str] = []
    pattern_option = False
    index = 0
    while index < len(rest):
        word = rest[index]
        if word.startswith("-") and word != "-":
            if subcommand == "grep" and not word.startswith("--") and word[:2] in ("-e", "-f"):
                pattern_option = True
            index += 2 if word in values else 1
            continue
        operands.append(word)
        index += 1
    if subcommand == "grep" and not pattern_option:
        operands = operands[1:]  # the first operand is the pattern
    return operands


def _git_toplevel(start: Path) -> Path:
    """The top of the Git tree that holds start: the nearest directory with a .git entry, else start (c123)."""
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return start


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


class _Traversal(str):
    """A traversal's command text; `unresolved_root` says the walk starts at a directory the shell supplies (c123, item 9)."""

    unresolved_root: bool

    def __new__(cls, text: str, *, unresolved_root: bool = False) -> _Traversal:
        found = super().__new__(cls, text)
        found.unresolved_root = unresolved_root
        return found


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
            return _Traversal(" ".join(words)[:240], unresolved_root=True)
        if os.path.basename(text.replace("\\", "/")) == _GIT_TOPLEVEL:
            # c123 (item 3): a Git pathspec with magic or a wildcard walks from the top of the tree.
            start = _absolute(cwd, os.path.dirname(text) or ".")
            target = _git_toplevel(start) if start is not None else None
        else:
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


class _LookupUnavailable:
    """A falsy `available` answer that carries the cause the binding lookup observed (c123; batch design WP1, item 9)."""

    def __init__(self, cause: str) -> None:
        self.cause = cause

    def __bool__(self) -> bool:
        return False


def _bound_session_context(payload: dict[str, Any], project: Path) -> tuple[str | None, bool | _LookupUnavailable]:
    """Return (session context, available) for this call's native context through the ordinary CLI.

    An unbound context owns no scratch or checkout. The CLI runs against the project that owns the shared roots, so a
    context inside its own checkout still reaches the configured authority. When the lookup fails, `available` is a
    falsy answer naming the observed cause (c123): a timeout, a start failure, an exit code with the first stderr line,
    or output that is not a JSON object.
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
    except subprocess.TimeoutExpired:
        return None, _LookupUnavailable("gt session show did not answer within 10 seconds")
    except OSError as error:
        return None, _LookupUnavailable(f"gt session show could not start ({error.__class__.__name__})")
    if result.returncode:
        if "no_session_binding" in (result.stderr or ""):
            return None, True
        first = next((line.strip() for line in (result.stderr or "").splitlines() if line.strip()), "no message")
        return None, _LookupUnavailable(f"gt session show exited {result.returncode}: {first[:200]}")
    try:
        context = json.loads(result.stdout).get("session_context_id")
    except (ValueError, AttributeError):
        return None, _LookupUnavailable("gt session show printed output that is not a JSON object")
    return (str(context) if context else None), True


def _judged_commands(command: str) -> list[str]:
    """The commands the write rule judges besides the line itself (c119 and c121; gathered here since c122).

    c119: a command handed to a nested shell or to Invoke-Expression is judged as a command of its own (M13 host I, Q6
    on c118: `cmd /c "gt --help > help.out 2>&1"` wrote a file under a read's judgment). c121: so is a $(...)
    subexpression inside a double-quoted string, which PowerShell and POSIX shells run.
    """
    judged = _inner_commands(command)
    judged += [
        text
        for source in (command, *judged)
        if source != UNINSPECTABLE_SHELL_COMMAND
        for text in _string_subexpression_commands(source)
    ]
    return judged


def _group_bodies(command: str, _nesting: int = 0) -> set[str]:
    """The text of every group in a command, nested ones included: text the whole-command scans read (c123)."""
    if _nesting > _GROUP_DEPTH:
        return set()
    _flat, groups = _flatten_groups(command)
    bodies: set[str] = set()
    for _only_values, body in groups:
        bodies.add(body)
        bodies |= _group_bodies(body, _nesting + 1)
    return bodies


def _walked_write_lines(command: str) -> list[tuple[str, bool]]:
    """The command lines the walk finds that the stage judgment does not read, each with whether its redirects are read
    from it (c123; batch design WP1, W and residual rows 1 to 3).

    The write rule judged each stage by its first word, so a write after a POSIX keyword (for f in *; do rm "$f"; done)
    or an assignment prefix (FOO=1 rm x), and the command a launcher runs (env rm x, find -exec rm {} \\;, ls | xargs rm,
    whose unresolved operand refuses it whole), were never judged. Each such line is judged now; this only adds checks,
    and c121's refuse-whole for a write inside a block stands. A line is rebuilt from its words, so its redirects are
    read here only when no whole-command scan reads them: in a command a launcher runs or a shell is handed.
    """
    stages = {" ".join(tokens) for stage in _split_pipeline_stages(command) if (tokens := _shell_split(stage))}
    original = {command, *_group_bodies(command)}
    lines: dict[str, bool] = {}
    for line, text in _walked_commands(command):
        if line == command or line in stages:
            continue
        lines[line] = lines.get(line, False) or text not in original
    return list(lines.items())


def _unresolved_write_target(command: str) -> str | None:
    """The first unresolved write target in the line or a command it hands on, for the refusal text (c122)."""
    for text in (command, *_judged_commands(command)):
        if text != UNINSPECTABLE_SHELL_COMMAND and (target := _unresolved_target(text)) is not None:
            return target
    for line, redirects in _walked_write_lines(command):
        if (
            line != UNINSPECTABLE_SHELL_COMMAND
            and (target := _unresolved_target(line, redirects=redirects)) is not None
        ):
            return target
    return None


def _rebased(path: str, base: Path, root: Path) -> str:
    """A target read relative to base, made relative to root as the native check reads it (c123, row 4)."""
    candidate = Path(path)
    if candidate.is_absolute():
        return path
    joined = os.path.normpath(base / candidate)
    try:
        return Path(os.path.relpath(joined, root)).as_posix()
    except ValueError:
        return Path(joined).as_posix()  # another drive: the absolute path


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
        # c123 (batch design WP1, residual row 4): a single leading change of directory moves every relative target,
        # in the line and in every command it runs; any other change leaves the relative targets unread.
        directory = _leading_directory(command)
        base = Path(os.path.normpath(root / directory)) if directory else root
        paths = _paths_from_shell(base, command)
        mutating = _is_mutating_command(command)
        unread = mutating and _has_unread_write(command)
        for inner in _judged_commands(command):
            if inner == UNINSPECTABLE_SHELL_COMMAND:
                mutating = True
                unread = True
            elif not _is_safe_command(inner):
                paths = sorted(set(paths) | set(_paths_from_shell(base, inner)))
                inner_mutating = _is_mutating_command(inner)
                mutating = mutating or inner_mutating
                unread = unread or (inner_mutating and _has_unread_write(inner))
        # c123 (batch design WP1, W and residual rows 1 to 3): every line the walk finds that no stage reads.
        for line, redirects in _walked_write_lines(command):
            if line == UNINSPECTABLE_SHELL_COMMAND:
                mutating = True
                unread = True
            elif not _is_safe_command(line):
                paths = sorted(set(paths) | set(_paths_from_shell(base, line, redirects=redirects)))
                line_mutating = _is_mutating_command(line)
                mutating = mutating or line_mutating
                unread = unread or (line_mutating and _has_unread_write(line, redirects=redirects))
        if directory is None and any(not Path(path).is_absolute() for path in paths):
            unread = True
        # c121 (M13 GTKB Home, Q1 on c120; owner 2026-09-29 07:56): the claim check must cover every write, so a command
        # carrying a write whose target the gate cannot read is refused whole (unknown_effect_targets).
        if unread:
            return [], True
        if base != root:
            paths = sorted({_rebased(path, base, root) for path in paths})
        return paths, mutating

    return [], False


def _unknown_target_cause(payload: dict[str, Any]) -> str:
    """What made a mutating call name no target the gate can check (c123; batch design WP1, item 9, entry 6).

    The refusal used to name no cause although several observations lead to it; this mirrors changed_paths' branches.
    """
    tool = _tool_name(payload).lower()
    data = _tool_input(payload)
    if tool in {"write", "edit", "strreplace", "multiedit", "notebookedit", "delete"}:
        return "the write tool named no path"
    if tool in {"move", "copy"}:
        return f"the {tool} tool's payload does not name both of its paths"
    if _is_apply_patch_tool(tool) or any("*** Begin Patch" in value for value in _string_values(payload)):
        return "the patch names no file"
    command = _command_from_payload(payload, data, tool)
    if command is None:
        return "the tool named no target"
    if _ruff_effects(_project_root(payload), command) is not None:
        return "a ruff command whose targets the gate cannot read"
    walked = _walked_write_lines(command)
    texts = [command, *_judged_commands(command), *(line for line, redirects in walked if redirects)]
    if UNINSPECTABLE_SHELL_COMMAND in texts or any(line == UNINSPECTABLE_SHELL_COMMAND for line, _r in walked):
        return "an inner command the gate cannot inspect (encoded, empty or nested too deeply)"
    for line, redirects in walked:
        if not redirects and _has_unread_write(line, redirects=False):
            return "a write after a keyword, a prefix or a launcher whose target the gate cannot read"
    if _leading_directory(command) is None:
        return (
            "a change of directory the gate cannot follow (only a single leading cd or Set-Location to a literal "
            "directory is read)"
        )
    for text in texts:
        if any(unnamed for _files, unnamed in _stage_option_writes(text)):
            # c123 (owner decision A5, row 17): the system write tools join the examples.
            return (
                "a command that writes files it does not name (find -delete, curl -O, wget without -O, or a system "
                "tool such as tar, certutil or fsutil writing a file it does not name)"
            )
        view = _mask_quoted_spans(text, mask_double=True)
        dotnet = _DOTNET_WRITE_RE.search(view)
        if dotnet is not None:
            return f"a .NET write call ({dotnet.group(0).strip().rstrip('(')})"
        if _has_python_mutating_signal(text):
            return "a Python file write"
        writes = _redirect_writes(text)
        if (writes is None and ">" in text) or (writes is not None and None in writes):
            return "a redirect with no target the gate can read"
        if _GIT_OUTPUT_RE.search(view) and _has_unread_write(text):
            return "git --output with no file the gate can read, or inside a block"
        if _has_unread_write(text):
            return "a write inside a script block, a group or a subexpression, or after a call operator"
    return "a write whose target the gate cannot read"


# c123 (owner decision A1; batch design WP1 item 5, option A): a program the shell runs can write what the command text
# does not show, so the write rule cannot judge it (M13 on c121: an unbound, unclaimed context's script wrote its file).
# A program run therefore needs a live claim of the bound context, of any intended status (a verifier's verdict claim
# counts), which the native `gt bridge check-program` confirms; an unbound context is refused. A claim ties the run to a
# delivery but does not bound the program: inside the claim it can still write outside the claim's targets. A program
# run is:
# - an interpreter given code: python (py, pythonw) with a script, -, or code from standard input, or with -m other than
#   the read-only modules below; python -c whose source starts a process or loads code (subprocess, os.system and the
#   os exec, spawn and popen calls, runpy, exec, eval, compile, __import__, importlib, ctypes) or imports a module from
#   outside the standard library (code from the working directory, the project or a package); node, deno, bun, perl,
#   ruby, php, lua, Rscript, cscript, wscript and java unless they only report their version or usage; pwsh or
#   powershell with -File, a script operand or code from standard input; bash, sh or zsh with a script or standard
#   input; cmd reading standard input;
# - a script file run as the program (.ps1, .bat, .cmd, .sh, .py, .js, .vbs, ...), and an executable named by a path
#   inside the project, a checkout or scratch (.\tools\x.exe);
# - pytest, npx, pnpx, bunx, uvx and make; npm, pnpm, yarn, uv, pip, pipx, cargo, dotnet and go beyond their
#   read-only commands (npm run, test, start and exec, uv run and uv tool run among them);
# - the PowerShell code loaders: Import-Module with a path, Add-Type, New-Object -ComObject;
# - the gt commands that write local files (_GT_LOCAL_WRITERS) and rg --pre;
# - a command the gate cannot inspect (a program named by a variable or an expression).
# Not program runs: python -c without those calls, python --version, python -m json.tool, every other gt command (gt.exe
# --help among them), rg, Get-Content, git (its own rule), node --version, and ruff, whose writes _ruff_effects reads.
_PYTHON_READ_ONLY_MODULES = frozenset({"json.tool", "site", "sysconfig", "platform", "tokenize", "ast"})
_PYTHON_INFORMATIONAL_OPTIONS = frozenset(
    {"-V", "-VV", "--version", "-h", "-?", "--help", "--help-env", "--help-xoptions", "--help-all"}
)
_PY_LAUNCHER_SELECTOR = re.compile(r"-\d+(?:\.\d+)*(?:-(?:32|64|arm64))?|-V:\S+")
_PYTHON_CODE_MODULES = frozenset({"runpy", "importlib", "ctypes", "pty"})
_PYTHON_SUBPROCESS_CALLS = frozenset(
    {"run", "call", "check_call", "check_output", "Popen", "getoutput", "getstatusoutput"}
)
_PYTHON_OS_PROCESS_CALLS = frozenset({"system", "popen", "startfile", "posix_spawn", "posix_spawnp"})
_PYTHON_CODE_BUILTINS = frozenset({"exec", "eval", "compile", "__import__"})
_SCRIPT_EXTENSIONS = frozenset(
    {
        ".ps1",
        ".psm1",
        ".bat",
        ".cmd",
        ".sh",
        ".bash",
        ".zsh",
        ".py",
        ".pyw",
        ".js",
        ".mjs",
        ".cjs",
        ".ts",
        ".mts",
        ".cts",
        ".vbs",
        ".vbe",
        ".wsf",
        ".wsh",
        ".jse",
        ".rb",
        ".pl",
        ".php",
        ".lua",
        ".jar",
        ".msi",
    }
)
_COMMON_INFORMATIONAL = frozenset({"--version", "-V", "--help", "-h", "-?", "/?"})
# Interpreters and runners that run code whenever they do more than report their version or usage.
_RUNS_UNLESS_INFORMATIONAL: dict[str, frozenset[str]] = {
    "node": frozenset({"--version", "-v", "--help", "-h", "--v8-options"}),
    "deno": frozenset({"--version", "-V", "--help", "-h", "help"}),
    "bun": frozenset({"--version", "-v", "--help", "-h", "--revision"}),
    "perl": frozenset({"-v", "-V", "--version", "--help", "-h"}),
    "ruby": frozenset({"-v", "--version", "--help", "-h"}),
    "php": frozenset({"-v", "--version", "--help", "-h"}),
    "lua": frozenset({"-v"}),
    "rscript": frozenset({"--version", "--help"}),
    "cscript": frozenset({"//?", "/?"}),
    "wscript": frozenset({"//?", "/?"}),
    "java": frozenset({"-version", "--version", "-help", "--help", "-h", "-?"}),
    "pytest": _COMMON_INFORMATIONAL,
    "py.test": _COMMON_INFORMATIONAL,
    "npx": _COMMON_INFORMATIONAL,
    "pnpx": _COMMON_INFORMATIONAL,
    "bunx": _COMMON_INFORMATIONAL,
    "uvx": _COMMON_INFORMATIONAL,
    "make": _COMMON_INFORMATIONAL,
    "gmake": _COMMON_INFORMATIONAL,
    "nmake": _COMMON_INFORMATIONAL,
    "mingw32-make": _COMMON_INFORMATIONAL,
}
_NODE_PACKAGE_READS = frozenset(
    {
        "--version",
        "-v",
        "-V",
        "--help",
        "-h",
        "help",
        "ls",
        "list",
        "ll",
        "la",
        "view",
        "info",
        "show",
        "v",
        "outdated",
        "why",
        "explain",
        "search",
        "root",
        "prefix",
        "bin",
        "ping",
        "whoami",
    }
)
# Package and build runners, with the first words with which they only read (install, run, build and test run code).
_RUNNER_READ_COMMANDS: dict[str, frozenset[str]] = {
    "npm": _NODE_PACKAGE_READS,
    "pnpm": _NODE_PACKAGE_READS,
    "yarn": _NODE_PACKAGE_READS,
    "pip": frozenset(
        {"list", "show", "freeze", "check", "help", "inspect", "debug", "--version", "-V", "--help", "-h"}
    ),
    "pipx": frozenset({"list", "environment", "help", "--version", "--help", "-h"}),
    "cargo": frozenset(
        {
            "--version",
            "-V",
            "version",
            "help",
            "--help",
            "-h",
            "--list",
            "metadata",
            "tree",
            "search",
            "locate-project",
            "pkgid",
            "read-manifest",
            "verify-project",
        }
    ),
    "dotnet": frozenset({"--version", "--info", "--list-sdks", "--list-runtimes", "help", "--help", "-h", "-?", "/?"}),
    "go": frozenset({"version", "help", "list", "doc", "env"}),
}
_UV_READS: frozenset[tuple[str, ...]] = frozenset(
    {
        ("--version",),
        ("-V",),
        ("version",),
        ("help",),
        ("--help",),
        ("-h",),
        ("tree",),
        ("pip", "list"),
        ("pip", "show"),
        ("pip", "freeze"),
        ("pip", "tree"),
        ("pip", "check"),
        ("tool", "list"),
        ("tool", "dir"),
        ("python", "list"),
        ("python", "find"),
        ("python", "dir"),
        ("cache", "dir"),
        ("self", "version"),
    }
)
_POWERSHELL_INFORMATIONAL = frozenset({"-version", "-v", "-help", "-h", "-?", "/?"})
_POWERSHELL_FILE_PARAMETERS = frozenset({"-file", "-f"})
_MODULE_FILE_SUFFIXES = (".psm1", ".psd1", ".ps1", ".dll", ".cdxml", ".xaml")
# The gt commands that write local files, read from cli.py and cli_authority.py, each with the options that make it
# write (none: it always writes). Every other gt command reads, or changes canonical state through the authority, which
# judges that change there. harness project runs the project's projector; commit preflight runs the project's checks.
_GT_LOCAL_WRITERS: dict[tuple[str, ...], frozenset[str]] = {
    ("harness", "project"): frozenset(),
    ("scaffold", "iac"): frozenset({"--apply"}),
    ("scaffold", "cicd"): frozenset({"--apply"}),
    ("controls", "propose"): frozenset(),
    ("dashboard", "init"): frozenset(),
    ("dashboard", "refresh"): frozenset(),
    ("db", "postgres", "export-current"): frozenset(),
    ("db", "postgres", "readback-current"): frozenset(),
    ("validate", "spec-coherence"): frozenset(),
    ("project", "init"): frozenset(),
    ("project", "chroma", "regenerate"): frozenset(),
    ("project", "classify-tree"): frozenset({"--output"}),
    ("project", "upgrade"): frozenset({"--apply", "--recover"}),
    ("application", "register"): frozenset(),
    ("env", "migrate"): frozenset({"--apply"}),
    ("registry", "reconcile"): frozenset({"--batch-output"}),
    ("registry", "register"): frozenset(),
    ("registry", "amend"): frozenset(),
    ("registry", "transition"): frozenset(),
    ("secrets", "scan"): frozenset({"--report-json"}),
    ("commit", "preflight"): frozenset(),
    ("push", "preflight"): frozenset({"--evidence-out", "--evidence-file"}),
    ("push", "readiness"): frozenset({"--evidence-out", "--evidence-file"}),
}
_GT_WRITER_PREFIXES = frozenset(key[:2] for key in _GT_LOCAL_WRITERS if len(key) == 3)
_KNOWN_PROGRAMS = frozenset(
    {
        "py",
        "gt",
        "git",
        "ruff",
        "rg",
        "uv",
        "pwsh",
        "powershell",
        "bash",
        "sh",
        "zsh",
        "cmd",
        *_RUNS_UNLESS_INFORMATIONAL,
        *_RUNNER_READ_COMMANDS,
    }
)


def _program_name(token: str) -> str:
    """A program's name for the program rule: its basename, lower case, without .exe, and without .cmd, .bat or .ps1
    when that names a known program (npm.cmd is npm) (c123)."""
    name = _executable_name(token).removesuffix(".exe")
    for suffix in (".cmd", ".bat", ".ps1", ".com"):
        stem = name.removesuffix(suffix)
        if stem != name and (stem in _KNOWN_PROGRAMS or stem.startswith("python") or stem.startswith("pip")):
            return stem
    return name


def _gt_writes_local_files(arguments: list[str]) -> bool:
    """Whether a gt command writes local files: one of _GT_LOCAL_WRITERS, with an option that makes it write (c123)."""
    words = _gt_command_words(arguments, 2)
    if words is not None and tuple(words) in _GT_WRITER_PREFIXES:
        words = _gt_command_words(arguments, 3)
    if words is None:
        return True  # a command word the shell supplies may name a writer
    options = _GT_LOCAL_WRITERS.get(tuple(words))
    if options is None:
        return False
    given = {_clean_shell_token(word).split("=", 1)[0] for word in arguments}
    return not options or bool(options & given)


def _python_call_runs_code(node: ast.Call, aliases: dict[str, tuple[str, str | None]]) -> bool:
    """Whether one Python call starts a process or loads code (c123, owner decision A1)."""
    func = node.func
    name = _python_call_name(func)
    if name is None:
        return False
    module = ""
    if isinstance(func, ast.Name):
        target = aliases.get(func.id)
        imported = target[1] if target is not None else None
        if target is not None and imported is not None:
            module, name = target[0], imported  # from os import system: system is os.system
        elif func.id in _PYTHON_CODE_BUILTINS:
            return True
    else:
        root: ast.expr = func
        while isinstance(root, ast.Attribute):
            root = root.value
        if isinstance(root, ast.Name):
            module = aliases[root.id][0] if root.id in aliases else root.id
    top = module.split(".")[0]
    if top in _PYTHON_CODE_MODULES:
        return True
    if top == "subprocess":
        return name in _PYTHON_SUBPROCESS_CALLS
    if top == "os":
        return name in _PYTHON_OS_PROCESS_CALLS or name.startswith(("exec", "spawn"))
    if top == "asyncio":
        return name.startswith("create_subprocess")
    return top == "builtins" and name in _PYTHON_CODE_BUILTINS


def _python_tree_runs_code(tree: ast.AST) -> bool:
    """Whether a python -c source starts a process, loads code, or imports a module from outside the standard library,
    whose code runs on import (python -c "import probe" runs probe.py from the working directory) (c123, A1)."""
    aliases = _python_import_aliases(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] not in sys.stdlib_module_names for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if node.level or (node.module or "").split(".")[0] not in sys.stdlib_module_names:
                return True
        elif isinstance(node, ast.Call) and _python_call_runs_code(node, aliases):
            return True
    return False


def _python_source_runs_code(words: list[str], position: int, attached: str) -> bool:
    """Whether python -c's source runs code; a source the shell supplies or the gate cannot parse does (c123, A1).

    The source is read as the Windows split keeps it (one quote pair removed) and as a POSIX shell splits the line, so a
    backslash-escaped quote does not make a readable source unreadable.
    """
    raw = attached or (words[position] if position < len(words) else "")
    if not raw:
        return False  # python -c without a source exits with an error
    if _unresolved_value(raw):
        return True
    sources = [_unquote_once(raw)]
    if not attached:
        try:
            posix = shlex.split(" ".join(words), posix=True)
        except ValueError:
            posix = []
        sources += [posix[index + 1] for index, word in enumerate(posix[:-1]) if word == "-c"][:1]
    trees: list[ast.AST] = []
    for source in sources:
        try:
            trees.append(ast.parse(source))
        except (SyntaxError, ValueError):
            continue
    return not trees or any(_python_tree_runs_code(tree) for tree in trees)


def _python_module_runs_code(module: str, rest: list[str]) -> bool:
    """Whether python -m <module> runs code: every module but the read-only ones, ruff (its writes are read by
    _ruff_effects) and gt, whose commands are judged one by one (c123, A1)."""
    if not module or _unresolved_value(module):
        return bool(module)
    name = _clean_shell_token(module)
    if name in GT_MODULES:
        return _gt_writes_local_files(rest)
    if name == "ruff" or name in _PYTHON_READ_ONLY_MODULES:
        return False
    if name == "pip":
        first = _clean_shell_token(rest[0]) if rest else ""
        return first not in _RUNNER_READ_COMMANDS["pip"]
    return True


def _python_runs_code(words: list[str]) -> bool:
    """Whether a python (py) command line runs code: a script, -, code from standard input, -m, or a -c source that
    starts a process or loads code (c123, owner decision A1)."""
    launcher = _program_name(words[0]) == "py"
    index = 1
    while index < len(words):
        word = _clean_shell_token(words[index])
        if launcher and _PY_LAUNCHER_SELECTOR.fullmatch(word):
            index += 1  # the py launcher's version selector
            continue
        if launcher and word in ("--list", "-0", "--list-paths", "-0p"):
            return False
        if word in _PYTHON_INFORMATIONAL_OPTIONS:
            return False
        if word == "-" or word == "--" or not word.startswith("-"):
            return True  # a script, or the source on standard input
        if word.startswith("--"):
            index += 2 if word in _PYTHON_VALUE_OPTIONS else 1
            continue
        letters = word[1:]
        for position, letter in enumerate(letters):
            rest = letters[position + 1 :]
            if letter == "c":
                return _python_source_runs_code(words, index + 1, rest)
            if letter == "m":
                if rest:
                    return _python_module_runs_code(rest, words[index + 1 :])
                return _python_module_runs_code(words[index + 1] if index + 1 < len(words) else "", words[index + 2 :])
            if letter in "XW":
                index += 0 if rest else 1  # the option's value is the rest of the bundle or the next word
                break
            if letter in "Vh?":
                return False
        index += 1
    return True  # no script, -c or -m: python reads its code from standard input


def _powershell_runs_code(args: list[str]) -> bool:
    """Whether pwsh or powershell runs a script or code from standard input itself, rather than handing a command the
    walk follows (-Command, -c) or reporting its version or usage (c123, A1)."""
    words = [_clean_shell_token(arg).lower() for arg in args]
    for index, word in enumerate(words):
        if word in _HANDING_FLAGS["powershell"]:
            return index + 1 >= len(words) or words[index + 1] == "-"
        if word in _POWERSHELL_FILE_PARAMETERS:
            return True
    if any(word in _POWERSHELL_ENCODED_COMMAND_FLAGS for word in words):
        return False  # the walk refuses an encoded command
    return not (words and all(word in _POWERSHELL_INFORMATIONAL for word in words))


def _posix_shell_runs_code(args: list[str]) -> bool:
    """Whether bash, sh or zsh runs a script or code from standard input itself, rather than handing -c's command to
    the walk or reporting its version or usage (c123, A1); a bundled -c (bash -lc) is not followed, so it runs code."""
    words = [_clean_shell_token(arg) for arg in args]
    if "-c" in words:
        return False
    return not (words and all(word in ("--version", "--help") for word in words))


def _cmd_runs_code(args: list[str]) -> bool:
    """Whether cmd reads commands from standard input: neither /c nor /k hands it one, and it is not /? (c123, A1)."""
    words = [_clean_shell_token(arg).lower() for arg in args]
    return not any(word in _HANDING_FLAGS["cmd"] for word in words) and words != ["/?"]


def _local_program(token: str, project: Path, cwd: Path) -> bool:
    """Whether a program a line names is a script file, or an executable named by a path inside the project, a checkout
    or scratch (c123, A1). A program found on PATH by its name alone is judged by that name, not here."""
    text = _clean_shell_token(token)
    if not text:
        return False
    if Path(text.replace("\\", "/")).suffix.lower() in _SCRIPT_EXTENSIONS:
        return True
    if not any(separator in text for separator in "/\\") and not text.startswith("."):
        return False
    target = _absolute(cwd, text)
    return target is not None and _is_within(target, project)


def _runs_program(words: list[str], project: Path, cwd: Path) -> bool:
    """Whether one command line the shell runs is a program run (c123, owner decision A1)."""
    name = _program_name(words[0])
    args = [_clean_shell_token(word) for word in words[1:]]
    if name == "py" or name.startswith("python"):
        return _python_runs_code(words)
    if name in _RUNS_UNLESS_INFORMATIONAL:
        if name == "node" and args[:1] in (["--check"], ["-c"]):
            return False  # a syntax check runs nothing
        return not args or not all(arg in _RUNS_UNLESS_INFORMATIONAL[name] for arg in args)
    reads = _RUNNER_READ_COMMANDS.get("pip" if re.fullmatch(r"pip\d*(?:\.\d+)?", name) else name)
    if reads is not None:
        if not args or (args[0] not in reads and args[0].lower() not in reads):
            return True
        return name == "go" and args[0] == "env" and bool({"-w", "-u"} & set(args))
    if name == "uv":
        lowered = [arg.lower() for arg in args]
        return tuple(lowered[:1]) not in _UV_READS and tuple(lowered[:2]) not in _UV_READS
    if name in ("pwsh", "powershell"):
        return _powershell_runs_code(words[1:])
    if name in ("bash", "sh", "zsh"):
        return _posix_shell_runs_code(words[1:])
    if name == "cmd":
        return _cmd_runs_code(words[1:])
    if name == "gt":
        return _gt_writes_local_files(words[1:])
    if name == "rg":
        return any(arg.split("=", 1)[0] == "--pre" for arg in args)
    if name in ("import-module", "ipmo"):
        return any(
            _unresolved_value(arg)
            or any(separator in arg for separator in "/\\")
            or arg.startswith(".")
            or arg.lower().endswith(_MODULE_FILE_SUFFIXES)
            for arg in args
            if not arg.startswith("-")
        )
    if name == "add-type":
        return True
    if name == "new-object":
        return any(
            len(arg) > 1 and "-comobject".startswith(arg.lower().split(":", 1)[0])
            for arg in args
            if arg.startswith("-")
        )
    if name in ("git", "ruff"):
        return False
    return _local_program(words[0], project, cwd)


def _program_run(payload: dict[str, Any]) -> str | None:
    """The first program run the call's shell command makes, as its command line; None when it makes none (c123, A1).

    Every command the line runs is judged (_walked_commands): the stages, the commands nested shells, Invoke-Expression
    and launchers run, groups and subexpressions.
    """
    command = _command_from_payload(payload, _tool_input(payload), _tool_name(payload).lower())
    if not command:
        return None
    root = _project_root(payload)
    project = _context_root(root)
    cwd = Path(str(payload.get("cwd") or root))
    for line, _text in _walked_commands(command):
        if line == UNINSPECTABLE_SHELL_COMMAND:
            return "a command the gate cannot inspect"
        words = _shell_split(line)
        if words and _runs_program(words, project, cwd):
            return line if len(line) <= 200 else line[:197] + "..."
    return None


_PROGRAM_RESIDUAL = (
    " A claim ties the run to a delivery; it does not bound the program, which can still write outside the claim's "
    "targets."
)


def _native_program_check(native: str, root: Path, env: dict[str, str], program: str) -> dict[str, Any]:
    """Confirm through the native CLI that this context holds a live claim before a program runs (c123, A1).

    `gt bridge check-program` answers {"status": "current", "scope": "program", "claims": <n>} when the bound context
    holds a live claim of any intended status; otherwise it exits nonzero with click's `Error: program_claim_required:
    <message>`, or the binding errors the effect check raises for an unbound context. It is called as check-effects is:
    the same root, environment and 10-second limit, and the same handling of every failure.
    """

    def blocked(code: str, reason: str) -> dict[str, Any]:
        return {"decision": "block", "reason_code": code, "reason": reason}

    argv = [sys.executable, "-m", "groundtruth_kb", "bridge", "check-program", "--native-context-id", native, "--json"]
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
            refusal = _native_refusal(result.stderr, [], check="program")
            refusal["reason"] = f"{refusal['reason']}\nProgram run: {program}.{_PROGRAM_RESIDUAL}"[:2000]
            return refusal
        current = json.loads(result.stdout)
        if not isinstance(current, dict) or current.get("status") != "current" or current.get("scope") != "program":
            return blocked("invalid_effect_response", "The native CLI did not return a current program check.")
    except subprocess.TimeoutExpired:
        return blocked(
            "effect_check_unavailable",
            "The native program check did not answer within 10 seconds. Restore the native CLI/authority connection "
            "before running this program.",
        )
    except OSError as error:
        return blocked(
            "effect_check_unavailable",
            f"The native program check could not start ({error.__class__.__name__}). Restore the native CLI/authority "
            "connection before running this program.",
        )
    except ValueError:
        return blocked(
            "effect_check_unavailable",
            "The native program check exited 0 but printed output that is not JSON, so its answer cannot be read.",
        )
    return {}


# c123 (owner decision A6; batch design WP1 section 6, row 4's persistence across calls): a hook payload marked
# "persistent_shell": true comes from a shell that keeps its working directory across calls (the persistent pwsh tool
# of the DeepSeek SDK host and of the GT-KB Home), while the gate judges every call from the payload's cwd. A change of
# directory there moves every later call's relative paths away from the directory the gate judges, so such a payload
# may not change the directory its session keeps: a cd, chdir, Set-Location, sl, pushd, Push-Location, popd or
# Pop-Location anywhere the shell's own process runs it (a stage, a script block, a group, a subexpression, a
# ForEach-Object or if body, Invoke-Expression text), or an assignment of [Environment]::CurrentDirectory, a
# [IO.Directory]::SetCurrentDirectory call or a session-state SetLocation call. PowerShell's location belongs to the
# whole runspace, so a script block does not contain the change. Text handed to another process (pwsh -Command, cmd
# /c, bash -c, Start-Process) runs there, and its change of directory does not persist.
PERSISTENT_SHELL_KEY = "persistent_shell"
_SESSION_DIRECTORY_CALL_RE = re.compile(
    r"\[(?:system\.)?environment\]::currentdirectory\s*=(?!=)"
    r"|\[(?:system\.)?io\.directory\]::setcurrentdirectory\s*\("
    r"|\.(?:setlocation|pushcurrentlocation|poplocation)\s*\(",
    re.IGNORECASE,
)


def _session_directory_call(text: str, _depth: int = 0) -> str | None:
    """A .NET or session-state call that changes the directory, in text the shell's own process runs (c123, A6)."""
    found = _SESSION_DIRECTORY_CALL_RE.search(_mask_quoted_spans(text, mask_double=True))
    if found is not None:
        return found.group(0).rstrip(" \t=(")
    if _depth >= _INNER_COMMAND_DEPTH:
        return None
    inner = list(_string_subexpressions(text))
    for line, _text in _walked_commands(text, same_process=True):
        words = _shell_split(line) if line != UNINSPECTABLE_SHELL_COMMAND else None
        if words and _executable_name(words[0]) in _EVALUATING_VERBS:
            evaluated = _handed_evaluation(line)
            inner.extend([evaluated] if evaluated else [])
    for part in inner:
        call = _session_directory_call(part, _depth + 1)
        if call is not None:
            return call
    return None


def _persistent_directory_change(payload: dict[str, Any]) -> str | None:
    """The change of directory a persistent shell's command keeps for its session, as written; None when it makes none
    (c123, owner decision A6)."""
    if payload.get(PERSISTENT_SHELL_KEY) is not True:
        return None
    command = _command_from_payload(payload, _tool_input(payload), _tool_name(payload).lower())
    if not command:
        return None
    for line, _text in _walked_commands(command, same_process=True):
        if line == UNINSPECTABLE_SHELL_COMMAND:
            return "a command the gate cannot inspect, which may change the directory"
        words = _shell_split(line)
        if words and _executable_name(words[0]).removesuffix(".exe") in _DIRECTORY_CHANGE_VERBS:
            return line if len(line) <= 200 else line[:197] + "..."
    return _session_directory_call(command)


def _native_refusal(stderr: str, paths: list[str], *, check: str = "effect") -> dict[str, Any]:
    """The native CLI's refusal with its own code (c123; batch design WP1, item 7).

    The CLI prints click's `Error: <code>: <message>`, and the DeepSeek runtime renders every denial as
    `Error: <reason>`, so hosts saw "Error: Error: <code>: ...". The gate strips click's prefix, returns the native code
    as the reason code (with B148 the host shows it once) and the message, detail lines and checked targets (at most
    five) as the reason. A line with no code (a bare `claim_expired`) keeps `native_effect_refused` with the cleaned text.
    c123 (owner decision A1): check names the refused check in that text, "effect" or "program".
    """
    lines = (stderr or "").strip().splitlines()
    first = lines[0].strip() if lines else ""
    if first.startswith("Error:"):
        first = first[len("Error:") :].strip()
    detail = "\n".join(line.rstrip() for line in lines[1:]).strip()
    shown = ", ".join(paths[:5]) + (f" and {len(paths) - 5} more" if len(paths) > 5 else "")
    targets = f" (targets: {shown})" if paths else ""
    match = re.fullmatch(r"([a-z][a-z0-9]*(?:_[a-z0-9]+)+):\s*(.+)", first)
    if match:
        reason = match.group(2) + targets + (f"\n{detail}" if detail else "")
        return {"decision": "block", "reason_code": match.group(1), "reason": reason[:2000]}
    cleaned = (first or f"The native CLI refused the {check} check.") + targets + (f"\n{detail}" if detail else "")
    return {"decision": "block", "reason_code": "native_effect_refused", "reason": cleaned[:2000]}


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    """Route actual mutating targets, and program runs, through the CLI; never consult legacy packets.

    c123 (owner decision A1): a program run needs a live claim of the bound context, checked after the writes. The claim
    does not bound the program: inside it the program can still write outside the claim's targets.
    """

    def blocked(code: str, reason: str) -> dict[str, Any]:
        return {"decision": "block", "reason_code": code, "reason": reason}

    invalid = payload.get(INVALID_HOOK_PAYLOAD_KEY)
    if invalid:
        # c123 (item 9, entry 7): the reader's detail is kept.
        return blocked("invalid_hook_payload", f"Cannot identify the tool effect from the supplied payload: {invalid}")
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
    # c123 (owner decision E1): the owner levers over project authorization, right after the owner operations and
    # before the credential, traversal and file-effect checks (gt projects move-item also names a write cmdlet).
    owner_lever = _owner_lever_from_payload(payload)
    if owner_lever == UNINSPECTABLE_SHELL_COMMAND:
        return blocked(
            "owner_lever_only",
            "A shell command that is encoded, empty, nested too deeply to inspect, or run through a program named by a "
            "variable or an expression may hide an owner lever over project authorization "
            "(GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001): name the program and its command literally; the owner "
            "runs those levers in their own terminal.",
        )
    if owner_lever is not None:
        return blocked(
            "owner_lever_only",
            f"{owner_lever} is an owner lever over project authorization "
            "(GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001): the owner runs it in their own terminal. State the change "
            "and the exact command for the owner to run.",
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
        # c123 (item 9, entry 2): a walk from a directory the shell supplies gets its own first sentence.
        opening = (
            f"A recursive listing or search from a directory the shell supplies when it runs ({traversal}) can walk "
            "into other contexts' scratch and checkouts: name the directory literally. "
            if getattr(traversal, "unresolved_root", False)
            else f"A recursive listing or search from here walks into other contexts' scratch and checkouts ({traversal}). "
        )
        return blocked(
            "context_traversal",
            opening
            + "Search tracked files with git grep or git ls-files in their ignore-honouring forms (not git grep "
            "--no-exclude-standard or --no-index, and git ls-files --others only with --exclude-standard), use rg (it "
            "skips Git-ignored paths), or name the directories to search; this context's own scratch is "
            "scratchpad/<its session context>.",
        )
    named = _named_context_directories(payload)
    if named:
        own, available = _bound_session_context(payload, _context_root(_project_root(payload)))
        if not available:
            # c123 (item 9, entry 3): name the cause the lookup observed when it gives one.
            cause = getattr(available, "cause", None)
            observed = f"The gate could not read this context's binding ({cause}). " if cause else ""
            return blocked(
                "context_isolation_unavailable",
                observed
                + "Restore the native CLI/authority connection before reading or changing scratch or checkout paths.",
            )
        foreign = [(child, token) for child, token in named if child.lower() != (own or "").lower()]
        if foreign:
            child, token = foreign[0]
            # c123 (item 9, entry 5): a wildcard child spans every context, this one included.
            reach = (
                f"{token} reaches other contexts' scratch or checkouts"
                if any(mark in child for mark in "*?[")
                else f"{token} belongs to another context"
            )
            return blocked(
                "foreign_context_material",
                f"A context uses only its own scratch and checkout; {reach}. Read "
                "shared state through the gt CLI and review work through your own checkout.",
            )
    # c123 (owner decision A6): a persistent shell may not change the directory its session keeps.
    change = _persistent_directory_change(payload)
    if change is not None:
        return blocked(
            "persistent_shell_directory_change",
            "This shell keeps its working directory across calls, but the gate judges every call from the working "
            f"directory the host reports, so this change of directory ({change}) would make later calls' relative "
            "paths name other files than the ones the gate checks. Name each path absolutely instead (in PowerShell, "
            "-LiteralPath 'C:\\full\\path') and leave the directory unchanged.",
        )
    root = _project_root(payload)
    cwd = Path(str(payload.get("cwd") or root)).absolute()
    paths, mutating = changed_paths({**payload, "project_root": str(cwd)})
    # c123 (owner decision A1): a program run needs a live claim too, checked after the writes.
    program = _program_run(payload)
    if not mutating and program is None:
        return {}
    if mutating and not paths:
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
        # c123 (item 9, entry 6): name what the gate observed.
        return blocked(
            "unknown_effect_targets",
            f"This call carries {_unknown_target_cause(payload)}, so the gate cannot check every target it writes. "
            "Name each target literally in a command the gate reads, or use the editor tool.",
        )
    native = str(os.environ.get("GTKB_NATIVE_CONTEXT_ID") or payload.get("session_id") or "").strip()
    supplied = str(payload.get("session_id") or "").strip()
    if not native or (supplied and supplied != native):
        # c123 (owner decision A1): an unbound context runs no program either.
        running = f" A program run ({program}) needs a live claim of the bound context." if program else ""
        return blocked(
            "invalid_native_context", "The tool must carry the current harness-native context identifier." + running
        )
    env = dict(os.environ)
    env["GT_PROJECT_ROOT"] = str(root)
    env["PYTHONIOENCODING"] = "utf-8"
    if mutating:
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
                # c123 (item 7): click's prefix stripped, the native code kept.
                return _native_refusal(result.stderr, paths)
            current = json.loads(result.stdout)
            if (
                not isinstance(current, dict)
                or current.get("status") != "current"
                or current.get("scope") not in {"scratch", "implementation"}
            ):
                return blocked("invalid_effect_response", "The native CLI did not return a current effect check.")
        except subprocess.TimeoutExpired:
            # c123 (item 9, entry 4): each failure names its cause.
            return blocked(
                "effect_check_unavailable",
                "The native effect check did not answer within 10 seconds. Restore the native CLI/authority connection "
                "before retrying this effect.",
            )
        except OSError as error:
            return blocked(
                "effect_check_unavailable",
                f"The native effect check could not start ({error.__class__.__name__}). Restore the native "
                "CLI/authority connection before retrying this effect.",
            )
        except ValueError:
            return blocked(
                "effect_check_unavailable",
                "The native effect check exited 0 but printed output that is not JSON, so its answer cannot be read.",
            )
    # c123 (owner decision A1): a command with both a write and a program run has both checked.
    if program is not None:
        return _native_program_check(native, root, env, program)
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
