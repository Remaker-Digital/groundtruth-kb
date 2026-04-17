# GT-KB Operational Governance Hardening — Revision 6

**Status:** REVISED
**Prime Builder:** Claude Sonnet 4.6
**Author session:** S295 (revision drafted during bridge scan)
**Revised to address:** NO-GO findings in `bridge/gtkb-operational-governance-hardening-008.md`
**Scope:** Close the gap between governance specs that exist and governance behavior that is mechanically enforced
**Repository:** `groundtruth-kb` + Agent Red project hooks/rules

---

## Prior Deliberations

- **DELIB-0628** — S279 Cycle Enforcement Hooks NO-GO. Session-local state, fail-open, Bash bypass, untracked hooks.
- **DELIB-0629, DELIB-0630** — Earlier hook designs rejected for session-local state and status-history parsing errors.
- **DELIB-0631** — Post-impl review. Hooks untracked, fail-open, mutation paths incomplete.
- **NO-GO -002** — 6 findings: wrong output surface, flat settings schema, session-local deliberation tracking, section-field matching, migration unplanned, shallow doctor contract.
- **NO-GO -004** — 4 findings: `hookEventName` missing from PreToolUse output, inert Bash hooks still registered, bridge parser acts on historical NO-GO lines, `.groundtruth/` not in `.gitignore`.
- **NO-GO -006** — 3 P1 findings: `ask` gates don't put reason into Claude's context; SessionStart/UserPromptSubmit output shape not runtime-proven; hard-deny hook `--self-test` exit-code contract contradicts itself. 1 P2 finding: Ruby mutation test missing.
- **NO-GO -008** — 2 findings: hard-deny hooks mix JSON control (exit 0) with exit-code blocking (exit 2) — mutually exclusive runtime paths; `source_paths` migration uses `ADD COLUMN IF NOT EXISTS` which fails on the local SQLite build and is untested.

---

## What Changed from -007

| NO-GO -008 finding | Resolution |
|---|---|
| P1: hard-deny hooks mix JSON `permissionDecision:"deny"` with exit 2 — Claude Code ignores JSON on non-zero exit | **Switched hard-deny hooks to the structured path: exit 0 + `hookSpecificOutput.permissionDecision="deny"`.** `emit_deny()` exits 0. Exit-code table updated: deny mode is now exit 0. Tests for direct-stdin blocking now assert exit 0 + deny JSON, not exit 2. `--self-test` still exits 0; its output is now identical to the runtime denial (no separate "would-have-been" distinction needed). |
| P2: `ALTER TABLE specifications ADD COLUMN source_paths TEXT DEFAULT NULL IF NOT EXISTS` is not supported in local SQLite build (3.50.4 returns `OperationalError`) and is untested | **Replaced with PRAGMA-based guard** matching the existing pattern at `src/groundtruth_kb/db.py:624-652`. Added 3 migration tests: `test_source_paths_migration_fresh_db`, `test_source_paths_migration_idempotent`, `test_insert_spec_without_source_paths_still_works`. Added 1 spec-before-code hook test using a `KnowledgeDB` instance created through the migrated schema rather than a manually mocked column. |

No other sections changed. All -006 resolutions remain in place.

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
    """Inject text into Claude's context.

    Uses hookSpecificOutput + hookEventName for all event types, per the current
    Claude Code hook reference (docs lines 541-571 for PreToolUse, 734-745 for
    SessionStart, 836-856 for UserPromptSubmit). This is the documented form for
    structured JSON output in all hook events.
    """
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }
    }))


def emit_ask(event: EventName, reason: str) -> None:
    """Pause and ask user whether to proceed, AND inject the reason into Claude's context.

    PreToolUse only. Uses hookSpecificOutput + hookEventName per docs.

    Two separate fields carry the reason:
    - permissionDecisionReason: shown to the user in the ask dialog (docs line 967)
    - additionalContext: injected into Claude's context (docs line 965)
    Both must be present so the governance rationale is visible to both parties.
    """
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,  # user-visible
            "additionalContext": reason,           # model-visible
        }
    }))


def emit_deny(event: EventName, reason: str) -> None:
    """Hard-block tool execution. Structured path: exits 0, Claude Code reads JSON deny.

    Claude Code docs (2026-04-16) define two mutually exclusive blocking mechanisms:
    - Structured path: hookSpecificOutput.permissionDecision="deny" + exit 0
      Claude Code reads the JSON and blocks the tool. The permissionDecisionReason
      is shown to the user and injected into Claude's context.
    - Exit-code path: stderr + exit 2. Claude Code blocks on exit code alone;
      any JSON output is ignored.

    This function uses the STRUCTURED PATH. All hard-deny hooks exit 0 after
    calling emit_deny(). Do NOT exit 2 after calling this function — that would
    cause Claude Code to ignore the denial reason entirely.
    """
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
| SessionStart | `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}` | **Required** |
| UserPromptSubmit | `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "..."}}` | **Required** |
| PreToolUse advisory | `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "..."}}` | **Required** |
| PreToolUse ask | `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "...", "additionalContext": "..."}}` | **Required** |
| PreToolUse deny | `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}` | **Required** |

**Rationale for using `hookSpecificOutput` consistently:**

The current Claude Code hook reference (version 2.1.39, fetched by Codex on 2026-04-16) documents structured JSON output for SessionStart and UserPromptSubmit using the same `hookSpecificOutput` + `hookEventName` nesting as PreToolUse. The legacy `assertion-check.py` template uses top-level `additionalContext` — that is a legacy pattern inherited from an older Claude Code version and is NOT carried forward. The new canonical builder uses the documented form for all event types.

**Self-test validation:** Every `--self-test` invocation asserts:
1. Output is valid JSON
2. `hookSpecificOutput` is present for all 8 hooks
3. `hookEventName` key is present inside `hookSpecificOutput` for all 8 hooks
4. `hookEventName` value matches the expected event type for that hook
5. Advisory hooks: `"additionalContext"` is a non-empty string when advisory is expected
6. Gate hooks: `"permissionDecision"` is `"ask"` or `"deny"` when gate fires; `"additionalContext"` is also present for `"ask"` decisions (so reason reaches Claude)
7. All `--self-test` invocations exit 0 (including hard-deny hooks)

### Exit-Code Contract (uniform for all 8 hooks)

| Mode | Exit code | Meaning |
|---|---|---|
| Normal operation — pass | 0 | Hook ran; no governance concern; `emit_pass()` |
| Normal operation — advisory | 0 | Hook ran; advisory/ask emitted; Claude sees it |
| Normal operation — deny | **0** | Hook ran; `emit_deny()` outputs structured JSON deny; Claude Code reads JSON and blocks |
| `--self-test` — detection worked correctly | 0 | Self-test validates detection logic; prints runtime denial output; exits 0 |
| `--self-test` — detection failed (bug) | 1 | Self-test found an internal error; hook is broken |

**Why deny exits 0:**
Claude Code's structured PreToolUse control path processes `hookSpecificOutput` only when the hook exits 0. On exit 2, Claude Code uses the exit code alone as the block signal and ignores any JSON output. Since `emit_deny()` carries the governance reason in `permissionDecisionReason`, the hook must exit 0 for that reason to reach the user and Claude. Exit 2 would silently discard the reason, defeating the governance purpose of the hook.

`--self-test` **never** exits 2. `gt project doctor` can safely run `hook --self-test` for all 8 hooks and treat any non-zero exit as a failure.

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

**No hook reads `os.environ["TOOL_INPUT"]` or any other environment variable for payload data.**

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

**Hard-deny runtime behavior (structured path, exit 0):**

```python
# destructive-gate.py — runtime path when destructive command detected:
emit_deny("PreToolUse", "Destructive command blocked by governance gate: git reset --hard")
sys.exit(0)  # Exit 0: Claude Code reads JSON deny and blocks the tool call

# credential-scan.py — runtime path when credential pattern detected:
emit_deny("PreToolUse", "Credential pattern blocked: command contains API key material")
sys.exit(0)  # Exit 0: Claude Code reads JSON deny and blocks the tool call
```

**`--self-test` for both hooks (exit 0, validates detection and produces runtime-identical output):**

```python
# destructive-gate.py --self-test
SELF_TEST_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "git reset --hard"},
    "session_id": "test",
    "cwd": "/fake"
}
# Self-test runs detection logic against this payload.
# Detection fires (command is destructive).
# Self-test calls emit_deny() — same function as runtime path — and exits 0.
# Output:
#   {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", ...}}
# Exit 0 in both self-test and runtime: structured JSON is processed by Claude Code.

# credential-scan.py --self-test
SELF_TEST_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "echo sk-ant-api03-aaaaaaaaaaaaaaaa"},
    "session_id": "test",
    "cwd": "/fake"
}
# Same pattern: detection fires, emit_deny() called, exits 0.
```

**Direct stdin injection tests (asserting structured deny, not exit 2):**

```bash
# test_destructive_gate_stdin_blocks:
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git reset --hard"},...}' \
  | python destructive-gate.py
# Expected: exits 0; stdout contains permissionDecision:"deny" with non-empty permissionDecisionReason

# test_credential_scan_stdin_blocks:
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"echo sk-ant-api03-aaaaaaaaaaaaaaaa"},...}' \
  | python credential-scan.py
# Expected: exits 0; stdout contains permissionDecision:"deny" with non-empty permissionDecisionReason
```

---

## Bridge Status Parser (Latest-Status-Per-Document)

*(Unchanged from -007. Included for completeness.)*

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
- The first status line encountered after a `Document:` header is the latest version (per file bridge protocol).
- Subsequent `NO-GO:`, `NEW:`, or `REVISED:` lines within the same entry are historical and are ignored.
- A document with latest `REVISED` that has an older `NO-GO` line is NOT treated as NO-GO.
- A document with latest `GO` that has an older `NO-GO` line is NOT treated as NO-GO.

**Bridge compliance gate behavior:**

1. Parse `bridge/INDEX.md` → `{doc_name: latest_status}`
2. Read frontmatter from each proposal file with `NEW`, `REVISED`, or `NO-GO` latest status
3. If `file_path` matches `target_paths` in a proposal with latest status `NEW` or `REVISED`:
   → `emit_ask("PreToolUse", "Bridge proposal for this module is pending Codex review (bridge/{doc}). Wait for GO verdict.")`
4. If `file_path` matches a proposal with latest status `NO-GO`:
   → `emit_ask("PreToolUse", "Bridge proposal for this module has NO-GO status. Review Codex findings at bridge/{doc}-{N}.md before implementing.")`
5. Latest `GO` or `VERIFIED`: `emit_pass()`
6. No frontmatter match: `emit_pass()`

---

## Expanded Bash Mutation Classifier

*(Unchanged from -007. Included for completeness.)*

```python
# groundtruth_kb/governance/mutation.py

import re
from pathlib import Path

MUTATION_PATTERNS: list[tuple[str, str]] = [
    (r'>\s*\S+', "shell output redirection (>)"),
    (r'>>\s*\S+', "shell append redirection (>>)"),
    (r'\btee\b', "tee command"),
    (r'\bcp\b', "cp command"),
    (r'\bmv\b', "mv command"),
    (r'\bsed\s+-i\b', "sed -i (in-place edit)"),
    (r'\bawk\s+-i\b', "awk -i (in-place edit)"),
    (r'\bSet-Content\b', "PowerShell Set-Content"),
    (r'\bAdd-Content\b', "PowerShell Add-Content"),
    (r'\bOut-File\b', "PowerShell Out-File"),
    (r'''python\s+-c\s+['"].*open\s*\(''', "Python one-liner file write"),
    (r'''python\s+-c\s+['"].*write\s*\(''', "Python one-liner file write"),
    (r'''node\s+-e\s+['"].*writeFile''', "Node.js writeFile one-liner"),
    (r'''node\s+-e\s+['"].*writeFileSync''', "Node.js writeFileSync one-liner"),
    (r'\bperl\s+-i\b', "perl -i (in-place edit)"),
    (r'''\bruby\s+-i\b''', "ruby -i (in-place edit)"),
]

SOURCE_DIRS = ("src/", "lib/", "groundtruth_kb/", "tests/")


def is_source_path(path: str) -> bool:
    return any(path.startswith(d) for d in SOURCE_DIRS)


def classify_bash_command(command: str) -> list[str]:
    found = []
    for pattern, description in MUTATION_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            found.append(description)
    return found
```

---

## `.gitignore` and Settings Ownership

*(Unchanged from -007. Included for completeness.)*

### Additions to Agent Red `.gitignore`

```gitignore
.groundtruth/
!.groundtruth-chroma/
```

### Additions to `groundtruth-kb` `.gitignore`

```gitignore
.groundtruth/
```

### Generated project `.gitignore` template (`src/groundtruth_kb/bootstrap.py`)

```gitignore
.groundtruth/
.claude/settings.local.json
```

### Scaffold file ownership

| File | Generated by | Tracked in git | Content |
|---|---|---|---|
| `.claude/settings.json` | `gt project init` | **Yes** | Governance hooks (all 6 Phase 1 hooks + ported destructive-gate + credential-scan) |
| `.claude/settings.local.json` | `gt project init` | **No** | Tool permission allowlist, workstation-specific overrides |
| `.groundtruth/` directory | First hook run | **No** | Runtime: `delib-search-log.jsonl`, hook state |

---

## `source_paths` Schema Migration (P2 fix)

The `source_paths` column is added using the **PRAGMA-based guard** pattern already established in `src/groundtruth_kb/db.py:624-652`. SQLite does not support `ADD COLUMN IF NOT EXISTS` syntax in all environments (confirmed: `sqlite3.sqlite_version == 3.50.4` returns `OperationalError` for that form).

**Migration implementation:**

```python
# In src/groundtruth_kb/db.py, _run_migrations() method,
# following the existing F1 migration pattern:

def _migrate_add_source_paths(self) -> None:
    """Add source_paths column to specifications if absent (idempotent via PRAGMA guard)."""
    existing = {
        row[1]
        for row in self._conn.execute("PRAGMA table_info(specifications)")
    }
    if "source_paths" not in existing:
        self._conn.execute(
            "ALTER TABLE specifications ADD COLUMN source_paths TEXT DEFAULT NULL"
        )
        self._conn.commit()
```

This is the same guard pattern as the F1 column migrations. It is safe to call on fresh databases (column absent → added) and on already-migrated databases (column present → skipped, no error).

**Migration tests (added to `tests/test_db.py`):**

```python
def test_source_paths_migration_fresh_db(tmp_path):
    """source_paths column is created on a brand-new database."""
    db = KnowledgeDB(tmp_path / "fresh.db")
    cols = {row[1] for row in db._conn.execute("PRAGMA table_info(specifications)")}
    assert "source_paths" in cols


def test_source_paths_migration_idempotent(tmp_path):
    """Opening an already-migrated database does not raise."""
    db_path = tmp_path / "existing.db"
    # First open: migrate
    db1 = KnowledgeDB(db_path)
    db1._conn.close()
    # Second open: migration guard skips the ALTER TABLE silently
    db2 = KnowledgeDB(db_path)
    cols = {row[1] for row in db2._conn.execute("PRAGMA table_info(specifications)")}
    assert "source_paths" in cols


def test_insert_spec_without_source_paths_still_works(tmp_path):
    """Specs can be inserted without supplying source_paths (column defaults to NULL)."""
    db = KnowledgeDB(tmp_path / "test.db")
    spec_id = db.insert_spec(
        title="Test",
        description="A spec",
        type="feature",
        status="specified",
    )
    row = db._conn.execute(
        "SELECT source_paths FROM specifications WHERE id = ?", (spec_id,)
    ).fetchone()
    assert row is not None
    assert row[0] is None  # DEFAULT NULL applied
```

**Spec-before-code hook test using migrated `KnowledgeDB`:**

The existing `test_spec_before_code_match` test must NOT manually inject the `source_paths` column into a mock or fixture database. It must construct a `KnowledgeDB` instance (which runs `_migrate_add_source_paths` automatically) and insert specs via the public API:

```python
def test_spec_before_code_match_via_migrated_db(tmp_path):
    """spec-before-code hook matches source_paths from a real migrated KnowledgeDB."""
    db = KnowledgeDB(tmp_path / "test.db")
    db.insert_spec(
        title="Auth module",
        description="Authentication logic",
        type="feature",
        status="specified",
        source_paths="src/groundtruth_kb/auth.py",
    )
    hook_output = run_spec_before_code_hook(
        db_path=tmp_path / "test.db",
        tool_name="Write",
        tool_input={"file_path": "src/groundtruth_kb/auth.py", "content": "x = 1"},
    )
    result = json.loads(hook_output)
    # A spec covers this path — no advisory needed
    assert result == {}
```

This test catches any regression where the `source_paths` column is absent from the schema that the hook queries.

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
| Destructive gate — ported to stdin + structured deny (exit 0) | `templates/hooks/destructive-gate.py` | Modified |
| Credential scan — ported to stdin + structured deny (exit 0) | `templates/hooks/credential-scan.py` | Modified |
| `source_paths` column — PRAGMA-guard migration | `src/groundtruth_kb/db.py` | Modified |
| Settings JSON generator | `src/groundtruth_kb/project/scaffold.py` | Modified |
| Generated `.gitignore` additions | `src/groundtruth_kb/bootstrap.py` | Modified |
| Agent Red `.gitignore` | `.gitignore` | Modified |
| groundtruth-kb `.gitignore` | `.gitignore` | Modified |
| Governance hook tests | `tests/test_governance_hooks.py` | New |
| Mutation classifier tests | `tests/test_governance_mutation.py` | New |
| Scaffold settings tests | `tests/test_scaffold_settings.py` | New |
| Migration tests (source_paths) | `tests/test_db.py` | Added (3 tests) |
| Destructive gate + credential scan `--self-test` | In above hook files | Added |

---

## Full Test List (Phase 1)

### Governance Hook Tests (`tests/test_governance_hooks.py`)

| Test | Scenario | Assertion |
|---|---|---|
| `test_delib_gate_no_prior_search` | No log entry for active doc | `hookSpecificOutput.additionalContext` present; `hookEventName == "UserPromptSubmit"` |
| `test_delib_gate_recent_search` | Log entry < 24h, same doc + topic hash | Returns `{}` |
| `test_delib_gate_different_doc` | Log entry for different doc | `hookSpecificOutput.additionalContext` present |
| `test_delib_gate_missing_log_file` | Log file absent | Returns `additionalContext` (fail-closed) |
| `test_delib_gate_corrupt_log_file` | Invalid JSON lines in log | Ignores corrupt lines, emits advisory |
| `test_spec_before_code_no_source_paths` | No specs have `source_paths` | Info advisory, not fail advisory |
| `test_spec_before_code_match` | Spec with `source_paths` matching target | Returns `{}` |
| `test_spec_before_code_no_match` | `source_paths` defined but not matching | Warning advisory with `hookEventName` |
| `test_spec_before_code_non_source_file` | Target is `docs/guide.md` | Returns `{}` |
| **`test_spec_before_code_match_via_migrated_db`** | Spec inserted via `KnowledgeDB` (real migration) | Returns `{}` — proves schema, not mock |
| `test_bridge_compliance_new_entry_match` | Latest `NEW` with frontmatter matching | `ask` with `hookEventName`; both `permissionDecisionReason` and `additionalContext` present |
| `test_bridge_compliance_ask_has_additionalContext` | `emit_ask()` called for bridge pending | `hookSpecificOutput.additionalContext` == `hookSpecificOutput.permissionDecisionReason` |
| `test_bridge_compliance_nogo_ask_has_additionalContext` | `emit_ask()` called for NO-GO match | `hookSpecificOutput.additionalContext` == `hookSpecificOutput.permissionDecisionReason` |
| `test_bridge_compliance_no_frontmatter` | Latest `NEW`, no frontmatter | Returns `{}` |
| `test_bridge_compliance_go_entry` | Latest `GO` (was previously `NO-GO`) | Returns `{}` |
| `test_bridge_compliance_nogo_entry` | Latest `NO-GO` with frontmatter match | `ask` with `hookEventName`; both fields present |
| **`test_bridge_compliance_revised_over_nogo`** | Latest `REVISED`, historical `NO-GO` below | Returns `ask` for pending (not NO-GO flavor) |
| **`test_bridge_compliance_go_over_nogo`** | Latest `GO`, historical `NO-GO` below | Returns `{}` (approved, ignore history) |
| **`test_bridge_compliance_multi_doc_partial_match`** | Two docs, one matching one not | Only matching doc fires; other passes silently |
| `test_kb_not_markdown_approved_path` | Target is `bridge/foo.md` | Returns `{}` |
| `test_kb_not_markdown_unapproved_path` | Target is `analysis/notes.md` | Advisory with `hookEventName` |
| `test_kb_not_markdown_configured_allowlist` | `groundtruth.toml` adds `reports/*.md` | Returns `{}` for `reports/foo.md` |
| `test_session_governance_clean` | No pending bridge entries | `hookSpecificOutput.additionalContext` all-OK summary; `hookEventName == "SessionStart"` |
| `test_session_governance_pending_entry` | One `NEW` bridge entry | Summary names the entry; `hookSpecificOutput` wrapper present |
| **`test_hook_self_test_all_exit_zero`** | `--self-test` on all 8 hooks | All exit 0 — including `destructive-gate.py` and `credential-scan.py` |
| **`test_hook_self_test_hookSpecificOutput_all`** | `--self-test` on all 8 hooks | All output contains `hookSpecificOutput` with non-empty `hookEventName` |
| **`test_hook_self_test_hookEventName_pretooluse`** | `--self-test` on each PreToolUse hook | `hookEventName == "PreToolUse"` |
| **`test_hook_self_test_hookEventName_sessionstart`** | `--self-test` on session-start hook | `hookEventName == "SessionStart"` inside `hookSpecificOutput` |
| **`test_hook_self_test_hookEventName_userpromptsubmit`** | `--self-test` on UserPromptSubmit hooks | `hookEventName == "UserPromptSubmit"` inside `hookSpecificOutput` |
| `test_hook_payload_prompt_field` | UserPromptSubmit with `"prompt"` key | Hook reads content correctly |
| `test_hook_payload_user_prompt_fallback` | UserPromptSubmit with `"user_prompt"` key | Hook reads content correctly |
| **`test_destructive_gate_self_test_exit_zero`** | `--self-test` on destructive-gate.py | Exits 0; output contains `permissionDecision: "deny"` |
| **`test_destructive_gate_stdin_blocks`** | Direct stdin with `git reset --hard` payload | **Exits 0**; stdout contains `permissionDecision: "deny"` with non-empty `permissionDecisionReason` |
| **`test_destructive_gate_env_ignored`** | `TOOL_INPUT` env set, clean stdin payload | Does NOT block; env var no longer read |
| **`test_credential_scan_self_test_exit_zero`** | `--self-test` on credential-scan.py | Exits 0; output contains `permissionDecision: "deny"` |
| **`test_credential_scan_stdin_blocks`** | Direct stdin with credential pattern payload | **Exits 0**; stdout contains `permissionDecision: "deny"` with non-empty `permissionDecisionReason` |

### Migration Tests (added to `tests/test_db.py`)

| Test | Scenario | Assertion |
|---|---|---|
| `test_source_paths_migration_fresh_db` | Brand-new `KnowledgeDB` | `source_paths` column present in `PRAGMA table_info(specifications)` |
| `test_source_paths_migration_idempotent` | Open same database twice | No error on second open; column still present |
| `test_insert_spec_without_source_paths_still_works` | Insert spec without `source_paths` arg | Row inserted; `source_paths` is `NULL` |

### Mutation Classifier Tests (`tests/test_governance_mutation.py`)

*(Unchanged from -007.)*

| Test | Input | Expected result |
|---|---|---|
| `test_redirect_detected` | `echo x > src/foo.py` | `["shell output redirection (>)"]` |
| `test_append_detected` | `echo x >> src/foo.py` | `["shell append redirection (>>)"]` |
| `test_tee_detected` | `cat x \| tee src/foo.py` | `["tee command"]` |
| `test_cp_detected` | `cp /tmp/foo src/foo.py` | `["cp command"]` |
| `test_mv_detected` | `mv /tmp/foo src/foo.py` | `["mv command"]` |
| `test_sed_i_detected` | `sed -i 's/a/b/' src/foo.py` | `["sed -i (in-place edit)"]` |
| `test_awk_i_detected` | `awk -i inplace ... src/foo.py` | `["awk -i (in-place edit)"]` |
| `test_powershell_set_content` | `Set-Content -Path src/foo.py -Value x` | `["PowerShell Set-Content"]` |
| `test_powershell_add_content` | `Add-Content src/foo.py x` | `["PowerShell Add-Content"]` |
| `test_powershell_out_file` | `Get-X \| Out-File src/foo.py` | `["PowerShell Out-File"]` |
| `test_python_oneliner_open` | `python -c "open('src/foo.py','w').write('x')"` | Python one-liner detected |
| `test_node_oneliner_writefile` | `node -e "fs.writeFileSync('src/foo.py','x')"` | Node.js one-liner detected |
| `test_perl_i_detected` | `perl -i -pe 's/a/b/' src/foo.py` | `["perl -i (in-place edit)"]` |
| **`test_ruby_i_detected`** | `ruby -i -pe 'gsub(/a/,"b")' src/foo.py` | `["ruby -i (in-place edit)"]` |
| `test_clean_command_no_mutations` | `ls -la src/` | `[]` |
| `test_is_source_path_true` | `src/groundtruth_kb/db.py` | `True` |
| `test_is_source_path_false` | `docs/guide.md` | `False` |

### Scaffold Settings Tests (`tests/test_scaffold_settings.py`)

*(Unchanged from -007.)*

```python
def test_settings_json_generated(tmp_project): ...
def test_settings_local_json_generated(tmp_project): ...
def test_settings_local_json_ignored(tmp_project): ...
def test_groundtruth_dir_ignored(tmp_project): ...
def test_settings_json_tracked(tmp_project, git_repo): ...
def test_settings_json_hooks_nested_schema(tmp_project): ...
```

---

## Open Decisions (resolved)

1. **Bridge compliance warn vs block:** `ask` for NEW/REVISED (pending). `ask` for NO-GO (not `deny`) — per Codex answer: "`ask` is acceptable if the owner explicitly wants override capability and the transcript records the override."

2. **`source_paths` migration:** PRAGMA-based guard (consistent with existing F1 pattern). `ADD COLUMN IF NOT EXISTS` form rejected — not supported in the local SQLite environment.

3. **Bash mutation detection scope:** Full classifier per `MUTATION_PATTERNS` list above.

4. **`delib-search-log.jsonl` location:** JSONL in `.groundtruth/` — included in `.gitignore`.

5. **Non-interactive/headless behavior for `ask` gates:** `ask` is acceptable for this project's interactive workflow. Deferred upgrade path to `deny` for headless runs documented but not required now.

6. **Hard-deny runtime mechanism:** Structured path (exit 0 + JSON `permissionDecision:"deny"`) chosen over exit-code path (exit 2 + stderr). Rationale: `permissionDecisionReason` must reach the user and Claude; Claude Code ignores JSON on exit 2, making exit 2 unsuitable when a human-readable denial reason is required.

---

## Phase 1 Exit Criteria

1. All 8 hook files (6 new + 2 ported) implemented under `src/groundtruth_kb/governance/` imported by thin wrappers in `templates/hooks/`
2. `groundtruth_kb.governance.output` and `groundtruth_kb.governance.mutation` modules implemented and tested
3. All tests in `tests/test_governance_hooks.py`, `tests/test_governance_mutation.py`, `tests/test_scaffold_settings.py`, and the 3 new migration tests in `tests/test_db.py` pass
4. `--self-test` on all 8 hooks exits 0; each hook's `--self-test` output contains `hookSpecificOutput` with correct `hookEventName`
5. `ask` gate tests assert both `permissionDecisionReason` (user-visible) and `additionalContext` (model-visible) are present
6. `destructive-gate.py` and `credential-scan.py` block on direct stdin-shaped payloads (**exit 0** + structured JSON deny) and ignore `TOOL_INPUT` env var; their `--self-test` exits 0
7. `gt project init --profile dual-agent` generates `.claude/settings.json` (tracked) with all 8 hooks
8. Generated `.gitignore` includes `.groundtruth/` and `.claude/settings.local.json`
9. The 5 S295 violations each produce a visible advisory or `ask` checkpoint (test case reference for each)
10. All `MUTATION_PATTERNS` covered by at least one test in `tests/test_governance_mutation.py` (including Ruby)
11. `source_paths` column migration passes fresh + idempotent tests; spec-before-code hook test uses real `KnowledgeDB` (not mock)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
