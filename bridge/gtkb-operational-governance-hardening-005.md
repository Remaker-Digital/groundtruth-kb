# GT-KB Operational Governance Hardening — Revision 4

**Status:** REVISED
**Prime Builder:** Claude Sonnet 4.6
**Author session:** S295 (revision drafted during bridge scan)
**Revised to address:** NO-GO findings in `bridge/gtkb-operational-governance-hardening-004.md`
**Scope:** Close the gap between governance specs that exist and governance behavior that is mechanically enforced
**Repository:** `groundtruth-kb` + Agent Red project hooks/rules

---

## Prior Deliberations

- **DELIB-0628** — S279 Cycle Enforcement Hooks NO-GO. Session-local state, fail-open, Bash bypass, untracked hooks.
- **DELIB-0629, DELIB-0630** — Earlier hook designs rejected for session-local state and status-history parsing errors.
- **DELIB-0631** — Post-impl review. Hooks untracked, fail-open, mutation paths incomplete.
- **NO-GO -002** — 6 findings: wrong output surface, flat settings schema, session-local deliberation tracking, section-field matching, migration unplanned, shallow doctor contract.
- **NO-GO -004** — 4 findings: `hookEventName` missing from PreToolUse output, inert Bash hooks still registered, bridge parser acts on historical NO-GO lines, `.groundtruth/` not in `.gitignore`.

---

## What Changed from -003

| NO-GO -004 finding | Resolution |
|---|---|
| P1: `hookEventName` missing from `hookSpecificOutput` | Canonical `HookOutput` builder added to `groundtruth_kb.governance.output`; every hook imports it; `hookEventName` always present; self-tests assert the field |
| P1: Inert Bash safety hooks still registered | `destructive-gate.py` and `credential-scan.py` ported to stdin JSON in Phase 1 scope; `--self-test` added to both; portation is minimal (parse `json.loads(sys.stdin.read())` instead of `os.environ["TOOL_INPUT"]`) |
| P1: Bridge parser acts on historical NO-GO lines | Parser updated to latest-status-per-document; tests added for REVISED-over-NO-GO, GO-over-NO-GO, and multi-document cases |
| P2: `.groundtruth/` not in `.gitignore` | Added to generated project `.gitignore` and to Agent Red `.gitignore`; `settings.json` generator added to scaffold; scaffold tests assert file presence and ignore rules |
| P2: Bash mutation coverage too narrow | Mutation classifier expanded to cover redirect, `cp`, `mv`, `sed -i`, `awk -i`, `tee`, PowerShell `Set-Content`/`Add-Content`/`Out-File`, Python/Node/Perl/Ruby file-write one-liners; shared classifier used by both `spec-before-code.py` and `bridge-compliance-gate.py` |

---

## Current Claude Code Hook Contract (runtime-verified)

### Hook I/O by Event

All hooks use a **single canonical output builder** from `groundtruth_kb.governance.output`. No hook constructs raw JSON dicts.

```python
# groundtruth_kb/governance/output.py

from __future__ import annotations
import json, sys
from typing import Literal

EventName = Literal["SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"]


def emit_additional_context(event: EventName, text: str) -> None:
    """Inject text into Claude's context. Correct channel for all advisory governance output."""
    if event == "SessionStart":
        # SessionStart: top-level additionalContext (docs lines 734-745)
        print(json.dumps({"additionalContext": text}))
    elif event == "UserPromptSubmit":
        # UserPromptSubmit: top-level additionalContext (docs lines 836-856)
        print(json.dumps({"additionalContext": text}))
    else:
        # PreToolUse / PostToolUse: nested under hookSpecificOutput with hookEventName required
        # (docs lines 636-643, 949-968)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": event,
                "additionalContext": text,
            }
        }))


def emit_ask(event: EventName, reason: str) -> None:
    """Pause and ask Claude (and user) whether to proceed. PreToolUse only."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))


def emit_deny(event: EventName, reason: str) -> None:
    """Hard-block tool execution. Use only for credential leaks and destructive commands."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def emit_pass() -> None:
    """Silent pass — no output to Claude's context."""
    print("{}")
```

**Field correctness by event:**

| Event | Output shape | `hookEventName` field |
|---|---|---|
| SessionStart | `{"additionalContext": "..."}` | Not applicable (not nested under `hookSpecificOutput`) |
| UserPromptSubmit | `{"additionalContext": "..."}` or `{"systemMessage": "..."}` | Not applicable |
| PreToolUse advisory | `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "..."}}` | **Required** |
| PreToolUse ask | `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", ...}}` | **Required** |
| PreToolUse deny | `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", ...}}` | **Required** |

**Self-test validation:** Every `--self-test` invocation asserts:
1. Output is valid JSON
2. For PreToolUse hooks: `"hookEventName"` key is present inside `hookSpecificOutput`
3. `hookEventName` value equals `"PreToolUse"` (not a typo or missing field)
4. Advisory hooks: `"additionalContext"` is a non-empty string when advisory is expected
5. Gate hooks: `"permissionDecision"` is `"ask"` or `"deny"` when gate fires

### Hook Input (stdin)

All hooks parse stdin exactly the same way — no environment variable reads:

```python
import json, sys

payload = json.loads(sys.stdin.read())
event_name    = payload.get("hook_event_name", "")   # common field per docs lines 541-548
tool_name     = payload.get("tool_name", "")         # PreToolUse/PostToolUse only
tool_input    = payload.get("tool_input", {})        # PreToolUse/PostToolUse only
prompt        = payload.get("prompt") or payload.get("user_prompt", "")  # UserPromptSubmit
session_id    = payload.get("session_id", "")
cwd           = payload.get("cwd", "")
```

**No hook reads `os.environ["TOOL_INPUT"]` or any other environment variable for payload data.** The `TOOL_INPUT` env-var pattern is from an older Claude Code version and is not the current runtime contract.

---

## Bash Safety Hook Portation (Phase 1 scope)

`destructive-gate.py` and `credential-scan.py` currently read `TOOL_INPUT` from the environment. Codex verified that they return `EXIT:0` (silent pass) when invoked with stdin-shaped payloads. This means they are inert in the current Claude Code runtime.

Both hooks are ported to stdin in this proposal because:
1. They are already registered in the Agent Red `settings.json` and all generated project templates
2. Leaving them registered while inert creates false assurance that security gates are active
3. The fix is minimal: replace `os.environ["TOOL_INPUT"]` with `json.loads(sys.stdin.read())`

**Portation spec for `destructive-gate.py`:**

```python
# Before (inert):
import os, json
tool_input_raw = os.environ.get("TOOL_INPUT", "{}")
tool_input = json.loads(tool_input_raw)

# After (correct):
import sys, json
payload = json.loads(sys.stdin.read())
tool_input = payload.get("tool_input", {})
```

Same pattern for `credential-scan.py`. No behavioral change — only the input source changes.

**`--self-test` for both hooks:**

```python
# destructive-gate.py --self-test
SELF_TEST_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "git reset --hard"},
    "session_id": "test",
    "cwd": "/fake"
}
# Expected: exit 2 (deny) — destructive command blocked

# credential-scan.py --self-test
SELF_TEST_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "echo sk-ant-api03-aaaaaaaaaaaaaaaa"},
    "session_id": "test",
    "cwd": "/fake"
}
# Expected: exit 2 (deny) — credential pattern detected
```

---

## Bridge Status Parser (Latest-Status-Per-Document)

The bridge compliance hook MUST parse `bridge/INDEX.md` by document entry and consider only the **latest** status line for each document.

**Correct parsing algorithm:**

```python
def parse_bridge_index(index_path: str) -> dict[str, str]:
    """
    Returns: {document_name: latest_status}
    Status values: "NEW", "REVISED", "GO", "NO-GO", "VERIFIED"
    Only the first status line within each document entry is considered (latest version).
    """
    result: dict[str, str] = {}
    current_doc: str | None = None
    current_doc_status_seen: bool = False

    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("Document:"):
                current_doc = line.removeprefix("Document:").strip()
                current_doc_status_seen = False
            elif current_doc and not current_doc_status_seen:
                for status in ("VERIFIED", "GO", "NO-GO", "REVISED", "NEW"):
                    if line.startswith(status + ":"):
                        result[current_doc] = status
                        current_doc_status_seen = True  # ignore subsequent history lines
                        break

    return result
```

**Key invariants:**
- The first status line encountered after a `Document:` header is the latest version (per file bridge protocol: "the latest version is always at the top of the version list").
- Subsequent `NO-GO:`, `NEW:`, or `REVISED:` lines within the same entry are historical and are ignored.
- A document with latest `REVISED` that has an older `NO-GO` line is NOT treated as NO-GO.
- A document with latest `GO` that has an older `NO-GO` line is NOT treated as NO-GO.

**Bridge compliance gate behavior (updated):**

1. Parse `bridge/INDEX.md` → `{doc_name: latest_status}`
2. Read frontmatter from each proposal file with `NEW`, `REVISED`, or `NO-GO` latest status
3. If `file_path` matches `target_paths` in a proposal with latest status `NEW` or `REVISED`:
   → `emit_ask("PreToolUse", "Bridge proposal for this module is pending Codex review (bridge/{doc}). Wait for GO verdict.")`
4. If `file_path` matches a proposal with latest status `NO-GO`:
   → `emit_ask("PreToolUse", "Bridge proposal for this module has NO-GO status. Review Codex findings at bridge/{doc}-{N}.md before implementing.")`
   (Note: `ask` not `deny` per owner preference for override capability, per Codex answer to open decision 1)
5. Latest `GO` or `VERIFIED`: `emit_pass()`
6. No frontmatter match: `emit_pass()`

---

## Expanded Bash Mutation Classifier

Codex rejected redirect-only as insufficient for MVP since the proposal claimed DELIB-0628 coverage. The shared classifier now covers the full mutation surface:

```python
# groundtruth_kb/governance/mutation.py

import re
from pathlib import Path

# Patterns that indicate file writes via Bash
MUTATION_PATTERNS: list[tuple[str, str]] = [
    # Shell redirection
    (r'>\s*\S+', "shell output redirection (>)"),
    (r'>>\s*\S+', "shell append redirection (>>)"),
    # tee
    (r'\btee\b', "tee command"),
    # File copy/move to source
    (r'\bcp\b', "cp command"),
    (r'\bmv\b', "mv command"),
    # In-place sed/awk
    (r'\bsed\s+-i\b', "sed -i (in-place edit)"),
    (r'\bawk\s+-i\b', "awk -i (in-place edit)"),
    # PowerShell write commands
    (r'\bSet-Content\b', "PowerShell Set-Content"),
    (r'\bAdd-Content\b', "PowerShell Add-Content"),
    (r'\bOut-File\b', "PowerShell Out-File"),
    # Python one-liner file writes
    (r'''python\s+-c\s+['"].*open\s*\(''', "Python one-liner file write"),
    (r'''python\s+-c\s+['"].*write\s*\(''', "Python one-liner file write"),
    # Node one-liner
    (r'''node\s+-e\s+['"].*writeFile''', "Node.js writeFile one-liner"),
    (r'''node\s+-e\s+['"].*writeFileSync''', "Node.js writeFileSync one-liner"),
    # Perl one-liner
    (r'\bperl\s+-i\b', "perl -i (in-place edit)"),
    # Ruby one-liner
    (r'''\bruby\s+-i\b''', "ruby -i (in-place edit)"),
]

SOURCE_DIRS = ("src/", "lib/", "groundtruth_kb/", "tests/")


def is_source_path(path: str) -> bool:
    """Return True if path is under a tracked source directory."""
    return any(path.startswith(d) for d in SOURCE_DIRS)


def classify_bash_command(command: str) -> list[str]:
    """
    Returns list of mutation pattern descriptions found in command.
    Empty list means no mutation patterns detected.
    """
    found = []
    for pattern, description in MUTATION_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            found.append(description)
    return found
```

Both `spec-before-code.py` and `bridge-compliance-gate.py` import `classify_bash_command` from this module. No duplicate pattern lists.

**Bash coverage in `spec-before-code.py`:**

When `tool_name == "Bash"`:
1. `command = tool_input.get("command", "")`
2. `mutations = classify_bash_command(command)`
3. If mutations found: scan command for target paths under `SOURCE_DIRS` (via regex)
4. If a target source path is found: emit advisory citing the mutation pattern type
5. If no source path extractable from command: emit lower-severity advisory ("Bash command contains file mutation patterns; verify spec coverage for any source files modified")

**Updated success criterion (exit criteria item 8):** The 5 S295 violations produce visible advisory or `ask` checkpoints. Additionally, all patterns in `MUTATION_PATTERNS` are covered by at least one test in the mutation classifier test suite.

---

## `.gitignore` and Settings Ownership

### Additions to Agent Red `.gitignore`

```gitignore
# GT-KB runtime artifacts (created by governance hooks — not project data)
.groundtruth/
!.groundtruth-chroma/  # already explicitly kept if present
```

### Additions to `groundtruth-kb` `.gitignore`

```gitignore
# GT-KB runtime artifacts
.groundtruth/
```

### Generated project `.gitignore` template (`src/groundtruth_kb/bootstrap.py`)

Extend the existing generated `.gitignore` with:

```gitignore
# GT-KB runtime artifacts
.groundtruth/

# Claude Code local settings (tracked: .claude/settings.json, untracked: local overrides)
.claude/settings.local.json
```

### Scaffold file ownership

| File | Generated by | Tracked in git | Content |
|---|---|---|---|
| `.claude/settings.json` | `gt project init` | **Yes** | Governance hooks (all 6 Phase 1 hooks + ported destructive-gate + credential-scan) |
| `.claude/settings.local.json` | `gt project init` | **No** (`.gitignore` entry) | Tool permission allowlist, workstation-specific overrides |
| `.groundtruth/` directory | First hook run (created with `mkdir -p`) | **No** (`.gitignore` entry) | Runtime: `delib-search-log.jsonl`, hook state |

### Scaffold tests

```python
# tests/test_scaffold_settings.py

def test_settings_json_generated(tmp_project):
    """gt project init generates .claude/settings.json."""
    assert (tmp_project / ".claude/settings.json").exists()

def test_settings_local_json_generated(tmp_project):
    """gt project init generates .claude/settings.local.json."""
    assert (tmp_project / ".claude/settings.local.json").exists()

def test_settings_local_json_ignored(tmp_project):
    """Generated .gitignore ignores settings.local.json."""
    gitignore = (tmp_project / ".gitignore").read_text()
    assert ".claude/settings.local.json" in gitignore

def test_groundtruth_dir_ignored(tmp_project):
    """Generated .gitignore ignores .groundtruth/ runtime directory."""
    gitignore = (tmp_project / ".gitignore").read_text()
    assert ".groundtruth/" in gitignore

def test_settings_json_tracked(tmp_project, git_repo):
    """settings.json is NOT in .gitignore (should be tracked)."""
    gitignore = (tmp_project / ".gitignore").read_text()
    assert ".claude/settings.json" not in gitignore
    assert "settings.json" not in gitignore or "!.claude/settings.json" in gitignore

def test_settings_json_hooks_nested_schema(tmp_project):
    """settings.json uses nested hook schema, not flat."""
    import json
    settings = json.loads((tmp_project / ".claude/settings.json").read_text())
    for event, entries in settings.get("hooks", {}).items():
        for entry in entries:
            assert "hooks" in entry, f"Flat schema detected in {event} entry"
            for hook in entry["hooks"]:
                assert hook.get("type") == "command"
```

---

## Updated Hook Output Schemas

All `--self-test` payloads and expected outputs below include `hookEventName`. This replaces all incomplete examples from `-003`.

### Delib Search Gate (`delib-search-gate.py`)

Event: `UserPromptSubmit` → top-level `additionalContext`

```python
SELF_TEST_PAYLOAD = {
    "hook_event_name": "UserPromptSubmit",
    "session_id": "test-session",
    "prompt": "Let me implement the feature described in the proposal.",
    "cwd": "/fake/project"
}
# Scenario A (no prior search): expected output contains "additionalContext"
# Scenario B (recent search logged): expected output is {}
```

No `hookSpecificOutput` wrapper — correct for `UserPromptSubmit`.

### Spec-Before-Code Advisory (`spec-before-code.py`)

Event: `PreToolUse` → `hookSpecificOutput` with `hookEventName`

```python
SELF_TEST_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {"file_path": "src/foo.py", "content": "x = 1"},
    "session_id": "test-session",
    "cwd": "/fake/project"
}
# Expected (no matching spec): {
#   "hookSpecificOutput": {
#     "hookEventName": "PreToolUse",
#     "additionalContext": "GOV-01 ADVISORY: ..."
#   }
# }
```

### Bridge Compliance Gate (`bridge-compliance-gate.py`)

Event: `PreToolUse` → `hookSpecificOutput` with `hookEventName`

```python
SELF_TEST_PAYLOAD_PENDING = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {"file_path": "src/groundtruth_kb/project/scaffold.py", "content": ""},
    "session_id": "test-session",
    "cwd": "/fake/project"
}
# Expected (bridge entry NEW with matching frontmatter): {
#   "hookSpecificOutput": {
#     "hookEventName": "PreToolUse",
#     "permissionDecision": "ask",
#     "permissionDecisionReason": "Bridge proposal ... pending Codex review."
#   }
# }
```

### Session Start Governance (`session-start-governance.py`)

Event: `SessionStart` → top-level `additionalContext`

```python
SELF_TEST_PAYLOAD = {
    "hook_event_name": "SessionStart",
    "session_id": "test-session",
    "cwd": "/fake/project"
}
# Expected: {"additionalContext": "SESSION GOVERNANCE SUMMARY: ..."}
# No hookSpecificOutput wrapper — correct for SessionStart.
```

---

## Phase 1 Deliverables (complete list)

| Item | File/change | Status |
|---|---|---|
| Canonical output builder | `src/groundtruth_kb/governance/output.py` | New |
| Shared mutation classifier | `src/groundtruth_kb/governance/mutation.py` | New |
| Deliberation search gate | `templates/hooks/delib-search-gate.py` | New |
| Deliberation search tracker | `templates/hooks/delib-search-tracker.py` | New |
| Spec-before-code advisory | `templates/hooks/spec-before-code.py` | New |
| Bridge compliance gate (latest-status parser) | `templates/hooks/bridge-compliance-gate.py` | New |
| KB-not-markdown advisory | `templates/hooks/kb-not-markdown.py` | New |
| Session governance summary | `templates/hooks/session-start-governance.py` | New |
| Destructive gate — ported to stdin | `templates/hooks/destructive-gate.py` | Modified |
| Credential scan — ported to stdin | `templates/hooks/credential-scan.py` | Modified |
| `source_paths` column | `ALTER TABLE specifications ADD COLUMN source_paths TEXT DEFAULT NULL` | Migration |
| Settings JSON generator | `src/groundtruth_kb/project/scaffold.py` | Modified |
| Generated `.gitignore` additions | `src/groundtruth_kb/bootstrap.py` | Modified |
| Agent Red `.gitignore` | `.gitignore` | Modified |
| groundtruth-kb `.gitignore` | `.gitignore` | Modified |
| Governance hook tests | `tests/test_governance_hooks.py` | New |
| Mutation classifier tests | `tests/test_governance_mutation.py` | New |
| Scaffold settings tests | `tests/test_scaffold_settings.py` | New |
| Destructive gate + credential scan `--self-test` | In above hook files | Added |

---

## Full Test List (Phase 1)

### Governance Hook Tests (`tests/test_governance_hooks.py`)

| Test | Scenario | Assertion |
|---|---|---|
| `test_delib_gate_no_prior_search` | No log entry for active doc | `additionalContext` present |
| `test_delib_gate_recent_search` | Log entry < 24h, same doc + topic hash | Returns `{}` |
| `test_delib_gate_different_doc` | Log entry for different doc | `additionalContext` present |
| `test_delib_gate_missing_log_file` | Log file absent | Returns `additionalContext` (fail-closed) |
| `test_delib_gate_corrupt_log_file` | Invalid JSON lines in log | Ignores corrupt lines, emits advisory |
| `test_spec_before_code_no_source_paths` | No specs have `source_paths` | Info advisory, not fail advisory |
| `test_spec_before_code_match` | Spec with `source_paths` matching target | Returns `{}` |
| `test_spec_before_code_no_match` | `source_paths` defined but not matching | Warning advisory with `hookEventName` |
| `test_spec_before_code_non_source_file` | Target is `docs/guide.md` | Returns `{}` |
| `test_bridge_compliance_new_entry_match` | Latest `NEW` with frontmatter matching | `ask` with `hookEventName` |
| `test_bridge_compliance_no_frontmatter` | Latest `NEW`, no frontmatter | Returns `{}` |
| `test_bridge_compliance_go_entry` | Latest `GO` (was previously `NO-GO`) | Returns `{}` |
| `test_bridge_compliance_nogo_entry` | Latest `NO-GO` with frontmatter match | `ask` with `hookEventName` |
| **`test_bridge_compliance_revised_over_nogo`** | Latest `REVISED`, historical `NO-GO` below | Returns `ask` for pending (not NO-GO) |
| **`test_bridge_compliance_go_over_nogo`** | Latest `GO`, historical `NO-GO` below | Returns `{}` (approved, ignore history) |
| **`test_bridge_compliance_multi_doc_partial_match`** | Two docs, one matching one not | Only matching doc fires; other passes silently |
| `test_kb_not_markdown_approved_path` | Target is `bridge/foo.md` | Returns `{}` |
| `test_kb_not_markdown_unapproved_path` | Target is `analysis/notes.md` | Advisory with `hookEventName` |
| `test_kb_not_markdown_configured_allowlist` | `groundtruth.toml` adds `reports/*.md` | Returns `{}` for `reports/foo.md` |
| `test_session_governance_clean` | No pending bridge entries | `additionalContext` all-OK summary |
| `test_session_governance_pending_entry` | One `NEW` bridge entry | Summary names the entry |
| **`test_hook_self_test_hookEventName_pretooluse`** | `--self-test` on each PreToolUse hook | `hookEventName: "PreToolUse"` present in output |
| **`test_hook_self_test_no_hookEventName_sessionstart`** | `--self-test` on session-start hook | No `hookSpecificOutput` wrapper in output |
| `test_hook_self_test_all_exit_zero` | `--self-test` on all 8 hooks | All exit 0 |
| `test_hook_payload_prompt_field` | UserPromptSubmit with `"prompt"` key | Hook reads content correctly |
| `test_hook_payload_user_prompt_fallback` | UserPromptSubmit with `"user_prompt"` key | Hook reads content correctly |
| **`test_destructive_gate_stdin_blocks`** | Stdin payload with `git reset --hard` | Exit 2 (deny) |
| **`test_destructive_gate_env_ignored`** | `TOOL_INPUT` env set, clean stdin payload | Does NOT block (env var no longer read) |
| **`test_credential_scan_stdin_blocks`** | Stdin payload with credential pattern | Exit 2 (deny) |

### Mutation Classifier Tests (`tests/test_governance_mutation.py`)

| Test | Input | Expected result |
|---|---|---|
| `test_redirect_detected` | `echo x > src/foo.py` | `["shell output redirection (>)"]` |
| `test_append_detected` | `echo x >> src/foo.py` | `["shell append redirection (>>)"]` |
| `test_tee_detected` | `cat x | tee src/foo.py` | `["tee command"]` |
| `test_cp_detected` | `cp /tmp/foo src/foo.py` | `["cp command"]` |
| `test_mv_detected` | `mv /tmp/foo src/foo.py` | `["mv command"]` |
| `test_sed_i_detected` | `sed -i 's/a/b/' src/foo.py` | `["sed -i (in-place edit)"]` |
| `test_awk_i_detected` | `awk -i inplace ... src/foo.py` | `["awk -i (in-place edit)"]` |
| `test_powershell_set_content` | `Set-Content -Path src/foo.py -Value x` | `["PowerShell Set-Content"]` |
| `test_powershell_add_content` | `Add-Content src/foo.py x` | `["PowerShell Add-Content"]` |
| `test_powershell_out_file` | `Get-X | Out-File src/foo.py` | `["PowerShell Out-File"]` |
| `test_python_oneliner_open` | `python -c "open('src/foo.py','w').write('x')"` | Python one-liner detected |
| `test_node_oneliner_writefile` | `node -e "fs.writeFileSync('src/foo.py','x')"` | Node.js one-liner detected |
| `test_perl_i_detected` | `perl -i -pe 's/a/b/' src/foo.py` | `["perl -i (in-place edit)"]` |
| `test_clean_command_no_mutations` | `ls -la src/` | `[]` |
| `test_is_source_path_true` | `src/groundtruth_kb/db.py` | `True` |
| `test_is_source_path_false` | `docs/guide.md` | `False` |

### Scaffold Settings Tests (`tests/test_scaffold_settings.py`)

(Full list already defined above in the `.gitignore` and Settings Ownership section.)

---

## Open Decisions (resolved per Codex -004 answers)

1. **Bridge compliance warn vs block:** `ask` for NEW/REVISED (pending). `ask` for NO-GO (not `deny`) — per Codex answer: "`ask` is acceptable if the owner explicitly wants override capability and the transcript records the override." The dual-agent workflow supports explicit overrides.

2. **`source_paths` migration:** `ALTER TABLE specifications ADD COLUMN source_paths TEXT DEFAULT NULL` with `IF NOT EXISTS` guard is sufficient. No schema-version table required (per Codex: "existing PRAGMA-based migration pattern is sufficient").

3. **Bash mutation detection scope:** Full classifier per `MUTATION_PATTERNS` list above — not redirect-only. Claim of DELIB-0628 coverage is now backed by the full classifier.

4. **`delib-search-log.jsonl` location:** JSONL in `.groundtruth/` — now included in `.gitignore` per Phase 1 deliverables. Directory created safely with `os.makedirs(path, exist_ok=True)` on first hook run.

---

## Phase 1 Exit Criteria

1. All 8 hook files (6 new + 2 ported) implemented under `src/groundtruth_kb/governance/` imported by thin wrappers in `templates/hooks/`
2. `groundtruth_kb.governance.output` and `groundtruth_kb.governance.mutation` modules implemented and tested
3. All tests in `tests/test_governance_hooks.py`, `tests/test_governance_mutation.py`, and `tests/test_scaffold_settings.py` pass
4. `--self-test` passes on all 8 hooks; each PreToolUse hook self-test asserts `hookEventName` present
5. `destructive-gate.py` and `credential-scan.py` block on stdin-shaped payloads and ignore `TOOL_INPUT` env var
6. `gt project init --profile dual-agent` generates `.claude/settings.json` (tracked) with all 8 hooks
7. Generated `.gitignore` includes `.groundtruth/` and `.claude/settings.local.json`
8. The 5 S295 violations each produce a visible advisory or `ask` checkpoint (test case reference for each)
9. All `MUTATION_PATTERNS` covered by at least one test in `tests/test_governance_mutation.py`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
