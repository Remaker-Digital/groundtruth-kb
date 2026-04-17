# GT-KB Operational Governance Hardening — Revised Implementation Proposal

**Status:** REVISED
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295 (revision drafted post-S295 bridge scan)
**Revised to address:** NO-GO findings in `bridge/gtkb-operational-governance-hardening-002.md`
**Scope:** Close the gap between governance specs that exist and governance behavior that is mechanically enforced
**Repository:** `groundtruth-kb` + Agent Red project hooks/rules

---

## Prior Deliberations

- **DELIB-0628** — S279 Cycle Enforcement Hooks NO-GO. Session-local state, fail-open, Bash bypass, untracked. Root failure modes this proposal must avoid.
- **DELIB-0631** — S279 Post-impl review. Hooks untracked, fail-open persisted, mutation paths incomplete.
- **NO-GO -002** — `bridge/gtkb-operational-governance-hardening-002.md`. 6 findings (4×P1, 2×P2): wrong output surface for PreToolUse hooks, flat settings schema mismatch, session-local deliberation tracking insufficient, spec/path matching underspecified, session health hook migration not planned, doctor contract shallow.

---

## What Changed from -001

This revision is **schema-first** per Codex's instruction: prove one hook pattern end-to-end against the current Claude Code contract, then scale.

| NO-GO finding | Resolution |
|---|---|
| P1: Wrong output surface | Documented exact JSON I/O per event; PreToolUse uses `hookSpecificOutput.additionalContext`; bridge-pending state uses `permissionDecision: "ask"` |
| P1: Settings schema flat vs nested | Verified against live Agent Red `settings.json`; templates updated to nested format; scaffold generates `.claude/settings.json` (tracked) not only `settings.local.json` |
| P1: Session-local deliberation tracking | Hook 1 tracks per bridge-document + per-topic with persistence to `.groundtruth/delib-search-log.jsonl`; resets when active bridge document changes |
| P1: Spec/path matching underspecified | Added `source_paths` optional field to spec metadata; Hook 2 warns only when `source_paths` coverage is missing for a target module; no false-positive on new/uncovered modules |
| P2: Session health migration not planned | Option 2 chosen: keep `assertion-check.py` + `session-health.py` as-is, add new `session-start-governance.py` SessionStart hook alongside |
| P2: Doctor/self-test contract shallow | Doctor distinguishes 7 failure modes; each hook exposes `--self-test` CLI with representative stdin payloads and exit-code contract |

---

## Current Claude Code Hook Contract (schema-verified 2026-04-16)

The following schemas are verified against the live Agent Red `settings.json` (commit `94392a1b`) and the Claude Code docs as fetched by Codex on 2026-04-16.

### Settings Schema (current)

The **nested** format is the current canonical schema. The flat format (direct `{"command": "..."}` entries) exists in older templates and may be tolerated but is not guaranteed to work with new Claude Code versions.

**Current (nested, correct):**
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \".claude/hooks/my-hook.py\"",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \".claude/hooks/spec-before-code.py\""
          }
        ]
      }
    ]
  }
}
```

**Old (flat, used in GT-KB templates/project/settings.local.json — must be updated):**
```json
{
  "hooks": {
    "UserPromptSubmit": [{"command": "python .claude/hooks/intake-classifier.py"}]
  }
}
```

**File ownership:**

| File | Tracked in git | Purpose |
|---|---|---|
| `.claude/settings.json` | **Yes** (via `!`-negation in `.gitignore`) | Project-level: governance hooks, required permissions. Every clone/worktree inherits it. |
| `.claude/settings.local.json` | **No** (untracked) | Workstation-local: additional tool permissions, developer-specific overrides. Merged on top of `settings.json`. |

`gt project init` generates **both** files. The governance hooks go in `settings.json`. The tool allowlist goes in `settings.local.json`. This separation ensures governance enforcement is not accidentally destroyed by a developer editing their local permissions file.

### Hook Input/Output by Event

#### SessionStart

```json
// stdin (Claude Code sends this to the hook process):
{"session_id": "abc123", "cwd": "/path/to/project"}

// stdout (hook returns this):
{"additionalContext": "plain text or markdown injected into Claude's context"}
// OR:
{}  // no-op

// Exit: always 0 (blocking session start is a bug)
```

**Existing example:** `templates/hooks/assertion-check.py` lines 68-72 correctly uses `{"additionalContext": ...}`.

#### UserPromptSubmit

```json
// stdin:
{"session_id": "abc123", "prompt": "...", "cwd": "/path/to/project"}

// stdout — advisory context added to Claude's context:
{"additionalContext": "GOVERNANCE CHECK: deliberation search required before..."}
// OR plain stdout text (also added to Claude's context):
GOVERNANCE CHECK: deliberation search required before...
// OR user-visible warning (shown in conversation but behavior depends on Claude Code version):
{"systemMessage": "..."}

// Exit: always 0
```

**Field name note:** The live Claude Code runtime sends `"prompt"` (not `"user_prompt"`) as of 2026-04-16. Existing `spec-classifier.py` reads `user_prompt` — it will return `{}` silently on the current runtime. The governance hooks in this proposal read `"prompt"` with a `"user_prompt"` fallback for backward compatibility.

**Advisory channel for UserPromptSubmit:** Use `additionalContext` (matching `assertion-check.py`). `systemMessage` is visible to the user in the transcript but its injection into Claude's model context is less reliably specified. `additionalContext` is the documented Claude-context channel.

Exception: `poller-freshness.py` legitimately uses `systemMessage` because it needs Claude to format a specific output block — that is a formatting instruction to Claude, not advisory governance context. New governance hooks use `additionalContext`.

#### PreToolUse (advisory — context without blocking)

```json
// stdin:
{
  "session_id": "abc123",
  "tool_name": "Write",
  "tool_input": {"file_path": "src/foo.py", "content": "..."},
  "cwd": "/path/to/project"
}

// stdout — inject advisory context but allow the tool call:
{
  "hookSpecificOutput": {
    "additionalContext": "GOVERNANCE WARNING: no specification covers src/foo.py..."
  }
}
// OR plain {} to pass through silently
```

#### PreToolUse (interactive gate — pause for agent to decide)

```json
// stdout — pause and ask Claude whether to proceed:
{
  "hookSpecificOutput": {
    "permissionDecision": "ask",
    "permissionDecisionReason": "Bridge proposal for this module has NO-GO status. Review Codex findings before implementing."
  }
}
```

`"ask"` shows a prompt to Claude (and the user) to approve or deny. It does not hard-block but creates a visible decision point.

`"deny"` hard-blocks (appropriate for credential leaks and destructive commands only — matching existing `credential-scan.py` and `destructive-gate.py` behavior).

#### PreToolUse (blocking — hard deny)

```json
// stdout:
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "Reason for denial."
  }
}
```

---

## Revised Hook Designs

### Hook 1: Deliberation Search Gate (`UserPromptSubmit`)

**Enforces:** `deliberation-protocol.md`, GOV-08

**Problem addressed:** The original proposal used a session-local flag. That is insufficient because: (a) state dies on session restart, (b) one search early in the session suppresses warnings for later unrelated topics.

**Revised design:** Track per *active bridge document* × *topic hash*.

**Persistent state:** `.groundtruth/delib-search-log.jsonl` (in `.groundtruth/`, already in `.gitignore` for runtime artifacts). Each entry:
```json
{
  "bridge_doc": "gtkb-adoption-gap-closure",
  "topic_hash": "a3b7c2d1",
  "topic_keywords": "adoption gap gtkb",
  "searched_at": "2026-04-16T14:22:00Z",
  "result_ids": ["DELIB-0628", "DELIB-0631"],
  "result_count": 2
}
```

**Active bridge document detection:** The hook reads `bridge/INDEX.md` and finds the most recent `NEW` or `REVISED` entry that is the active work item. If none found, uses `"__general__"` as the document key.

**Topic hash:** MD5-first-8 of the normalized top-5 content keywords extracted from the user's prompt.

**Hook behavior:**
1. Parse `bridge/INDEX.md` → `active_doc` (most recent `NEW` or `REVISED`)
2. Extract topic keywords from prompt
3. Check `.groundtruth/delib-search-log.jsonl` for an entry matching `active_doc` + `topic_hash` within the last 24 hours
4. If found: pass through silently (search already done)
5. If not found: emit `additionalContext`:
   ```
   DELIBERATION SEARCH REQUIRED: Before starting work on {active_doc}, run:
     db.search_deliberations('{keywords}')
   Cite any relevant DELIB-IDs in your response. This check resets when the
   active bridge document changes. Archive the search result by appending to
   .groundtruth/delib-search-log.jsonl.
   ```

**PostToolUse tracking (companion hook):** A `PostToolUse` hook on `Bash` tool detects when `search_deliberations` was called (by checking stdout for `DELIB-` pattern) and appends the record to `.groundtruth/delib-search-log.jsonl`. This closes the loop without requiring the agent to remember to update state.

**Fail mode:** Any exception → emit `additionalContext` ALARM warning (same style as poller-freshness.py). Never silently pass.

---

### Hook 2: Spec-Before-Code Advisory (`PreToolUse`)

**Enforces:** GOV-01, GOV-06, GOV-12

**Problem addressed:** Original design matched source paths against spec `section` field, which is NULL for all existing specs. Relied on section-field string matching that has no data to match against.

**Revised design:** Uses `source_paths` optional metadata field added to specs.

**New spec metadata field:** `source_paths: list[str]` — optional list of glob patterns relative to project root (e.g., `["src/groundtruth_kb/project/**/*.py"]`). Populated when a spec is created for a module. Not required (NULL = "not yet mapped").

**Hook behavior:**
1. Get `file_path` from `tool_input` (Write or Edit)
2. If file is NOT under a source directory (`src/`, `lib/`, etc.) → pass through silently (docs, bridge, tests, config)
3. Query KB for specs where `source_paths` contains a pattern matching `file_path`
4. If NO specs have `source_paths` defined at all → emit advisory: "GOVERNANCE INFO: No spec-to-source path mapping exists yet. Consider adding `source_paths` to relevant specs."
5. If specs have `source_paths` but NONE match `file_path` → emit advisory warning: "GOV-01 ADVISORY: No specification covers {file_path}. If this is new source code, create or identify a specification first."
6. If a matching spec exists → pass silently (spec-first is satisfied)

**Why advisory not `ask`:** Source edits during bridge-GO'd implementation sessions are expected and correct. Hard-blocking or `ask`-gating would interrupt normal flow. Advisory context is the right level for spec coverage gaps.

---

### Hook 3: Bridge Protocol Compliance Gate (`PreToolUse`)

**Enforces:** `file-bridge-protocol.md`, `CLAUDE.md:65-70`

**Problem addressed:** Original relied on topic/module string matching in INDEX.md. No structured relation between source paths and bridge documents.

**Revised design:** Uses bridge frontmatter instead of string matching.

**Bridge proposal frontmatter:** Each bridge proposal SHOULD include a frontmatter block:
```markdown
---
target_paths: ["src/groundtruth_kb/project/*.py"]
target_modules: ["groundtruth_kb.project"]
---
```

This is optional for existing proposals; the hook only warns when frontmatter is present and status is pending.

**Hook behavior:**
1. Get `file_path` from `tool_input`
2. Parse `bridge/INDEX.md` for all entries
3. For each NEW or NO-GO entry: read the proposal file, check for frontmatter `target_paths`
4. If `file_path` matches a frontmatter pattern AND that entry is `NEW` or `REVISED` (awaiting review) → emit `ask`:
   ```
   Bridge proposal for this module is pending Codex review (bridge/{doc}).
   Per the operating procedure, implementation should wait for GO verdict.
   Do you want to proceed anyway?
   ```
5. If `file_path` matches a `NO-GO` entry → emit `ask` with NO-GO reason summary
6. If no frontmatter match → pass silently (no false positives for undeclared modules)

**Why `ask` not `deny` for NO-GO:** DELIB-0628 showed hard blocks route around the gate. `ask` creates a visible checkpoint that Claude must acknowledge; it cannot silently skip the warning, but it can proceed with an explicit decision.

---

### Hook 4: KB-Not-Markdown Advisory (`PreToolUse`)

**Enforces:** GOV-08

**No design changes from -001.** This hook's design was not flagged in the NO-GO.

**Output format corrected:** Uses `hookSpecificOutput.additionalContext` (not top-level `systemMessage`) per the PreToolUse contract.

**Allowlist:** Made configurable via `groundtruth.toml`:
```toml
[governance.markdown_allowlist]
paths = [
  "CLAUDE.md", "MEMORY.md", "memory/*.md", "AGENTS.md",
  "bridge/*.md", "docs/**/*.md", ".claude/rules/*.md",
  "independent-progress-assessments/**/*.md",
  "CHANGELOG.md", "README.md", "CONTRIBUTING.md"
]
```
Default is the static list from -001. Projects can extend via `groundtruth.toml`.

---

### Hook 5 → Two Hooks: Session Health Check (`SessionStart`)

**Problem addressed:** -001 proposed replacing `assertion-check.py`. `session-health.py` is already a Stop hook, not SessionStart. Replacing assertion-check without migration would regress existing assertion context.

**Revised design (Option 2 chosen):** Add a new `session-start-governance.py` hook alongside the existing hooks:

| Hook file | Event | Keeps | Content |
|---|---|---|---|
| `assertion-check.py` | `SessionStart` | **Unchanged** | KB assertion results (as today) |
| `session-start-governance.py` | `SessionStart` | **New** | Bridge backlog, stale MEMORY.md, open owner decisions |
| `session-health.py` | `Stop` | **Unchanged** | Session snapshot via `db.capture_session_snapshot()` |

`session-start-governance.py` output uses `additionalContext`:
```
SESSION GOVERNANCE SUMMARY:
  Bridge: 1 entry requires action (gtkb-operational-governance-hardening NO-GO)
  Open owner decisions: 0 unarchived decisions found
  MEMORY.md: last session S295 (0 days ago) — current
  Deliberation search: not yet performed this session
```

This is additive only. It does not duplicate what `assertion-check.py` already emits.

---

## MVP Scope (Phase 1 only — narrowed per Codex direction)

Rather than proposing all 4 phases upfront, this revision delivers **Phase 1 only** for GO approval. Phases 2-4 will be proposed separately after Phase 1 is VERIFIED.

**Phase 1 deliverables:**

| Hook | File | Event | Output channel | Tests |
|---|---|---|---|---|
| Deliberation search gate | `delib-search-gate.py` | UserPromptSubmit | `additionalContext` | 5 unit tests |
| Deliberation search tracker | `delib-search-tracker.py` | PostToolUse (Bash) | `{}` | 3 unit tests |
| Spec-before-code advisory | `spec-before-code.py` | PreToolUse (Write/Edit) | `hookSpecificOutput.additionalContext` | 6 unit tests |
| Bridge compliance gate | `bridge-compliance-gate.py` | PreToolUse (Write/Edit) | `hookSpecificOutput` (ask/advisory) | 5 unit tests |
| KB-not-markdown advisory | `kb-not-markdown.py` | PreToolUse (Write) | `hookSpecificOutput.additionalContext` | 4 unit tests |
| Session governance summary | `session-start-governance.py` | SessionStart | `additionalContext` | 4 unit tests |

**Phase 1 also includes:**

1. **`groundtruth_kb.governance` package** — shared logic for all hooks (path classification, INDEX.md parsing, spec query, state file I/O). Hooks are thin wrappers importing from this package. One canonical location, no template drift.

2. **`source_paths` spec metadata** — add optional `source_paths: str` column to `specifications` table (JSON-encoded list of globs). Migration: `ALTER TABLE specifications ADD COLUMN source_paths TEXT DEFAULT NULL`. No data change to existing specs.

3. **Bridge frontmatter convention** — add SPEC-* to `specs` table documenting the frontmatter format for `target_paths` in bridge proposals. No code change required; it is a textual convention.

4. **`templates/project/settings.local.json` — updated to nested schema.** The existing flat-format template file is updated to the nested format.

5. **`gt project init --profile dual-agent` — updated to generate `.claude/settings.json` (tracked)** alongside the existing `.claude/settings.local.json`. `settings.json` registers all 6 Phase 1 hooks.

---

## Doctor Contract (Phase 2 - not in Phase 1 scope, specified here for GO decision)

`gt project doctor` will distinguish these 7 failure states per hook:

| State | Detection | Reported as |
|---|---|---|
| 1. File missing | `(target / ".claude/hooks" / name).exists()` | `fail` |
| 2. Not registered | `hook_name` absent from `settings.json` entries | `warning` |
| 3. Registered on wrong event | Event key doesn't match expected event | `warning` |
| 4. Malformed output | `--self-test` returns non-JSON or missing required field | `fail` |
| 5. Execution failure | `--self-test` exits non-zero | `fail` |
| 6. Stale runtime state | `.groundtruth/delib-search-log.jsonl` > 7 days old | `info` |
| 7. Intentionally disabled | `groundtruth.toml [governance] disabled_hooks = ["..."]` | `info` (not fail) |

`gt project doctor --fix`:
- Restores missing hook files from package templates
- Adds missing hook registrations to `settings.json`
- Only modifies files it owns (does not touch developer-created hooks or custom rules)
- Prints a diff of planned changes and prompts before writing

**Hook `--self-test` contract:**

Each hook accepts `--self-test` as a CLI argument. In self-test mode:
1. Runs with a hardcoded representative payload (not stdin)
2. Validates output JSON structure (correct field name, non-empty string value)
3. Does NOT write to `.groundtruth/delib-search-log.jsonl` or query the live DB
4. Exits 0 on pass, 1 on fail, 2 on dependency error (e.g., `groundtruth_kb` not installed)

Example representative payloads:

```python
# UserPromptSubmit
SELF_TEST_PAYLOAD = {
    "session_id": "test-session",
    "prompt": "Before implementing, let me check the deliberation archive",
    "cwd": "/fake/project"
}
# Expected: {"additionalContext": "..."} or {} (if search already logged for this doc)

# PreToolUse:Write
SELF_TEST_PAYLOAD = {
    "session_id": "test-session",
    "tool_name": "Write",
    "tool_input": {"file_path": "src/foo.py", "content": "x = 1"},
    "cwd": "/fake/project"
}
# Expected: {"hookSpecificOutput": {"additionalContext": "..."}} or {}
```

---

## Test Coverage Required for Phase 1

Tests live in `tests/test_governance_hooks.py`:

| Test | Scenario | Assertion |
|---|---|---|
| `test_delib_gate_no_prior_search` | No prior search log entry for active bridge doc | `additionalContext` present and contains bridge doc name |
| `test_delib_gate_recent_search` | Log entry < 24h for same doc + topic hash | Returns `{}` (no warning) |
| `test_delib_gate_different_doc` | Log entry exists for a different doc | `additionalContext` present (doc changed, search required again) |
| `test_delib_gate_missing_log_file` | `.groundtruth/delib-search-log.jsonl` absent | Returns `additionalContext` (fail-closed, not fail-open) |
| `test_delib_gate_corrupt_log_file` | Log file contains invalid JSON lines | Ignores corrupt lines, continues, emits advisory |
| `test_spec_before_code_no_source_paths` | No specs have `source_paths` defined | Emits info-level advisory, not fail advisory |
| `test_spec_before_code_match` | Spec with `source_paths: ["src/foo.py"]`, target is `src/foo.py` | Returns `{}` (covered) |
| `test_spec_before_code_no_match` | Spec with `source_paths` defined but not matching target | Emits warning advisory |
| `test_spec_before_code_non_source_file` | Target is `docs/guide.md` | Returns `{}` (not a source file) |
| `test_bridge_compliance_new_entry_match` | Bridge entry NEW with frontmatter matching target path | Returns `hookSpecificOutput` with `permissionDecision: "ask"` |
| `test_bridge_compliance_no_frontmatter` | Bridge entry NEW but no frontmatter | Returns `{}` (no false positive) |
| `test_bridge_compliance_go_entry` | Bridge entry GO (approved) | Returns `{}` (allow) |
| `test_bridge_compliance_nogo_entry` | Bridge entry NO-GO with frontmatter match | Returns `ask` with NO-GO reason |
| `test_kb_not_markdown_approved_path` | Target is `bridge/foo.md` | Returns `{}` |
| `test_kb_not_markdown_unapproved_path` | Target is `analysis/notes.md` | Returns advisory |
| `test_kb_not_markdown_configured_allowlist` | `groundtruth.toml` adds `reports/*.md` to allowlist | Returns `{}` for `reports/foo.md` |
| `test_session_governance_clean` | No pending bridge entries, no stale MEMORY.md | Returns `additionalContext` with all-OK summary |
| `test_session_governance_pending_entry` | One NEW bridge entry | Summary includes bridge entry name |
| `test_settings_schema_nested` | Generated `settings.json` | All hook registrations use nested `{"hooks": [{"type": "command", ...}]}` format |
| `test_settings_schema_flat_rejected` | Old flat `settings.local.json` | `gt project doctor` reports `warning` for each flat registration |
| `test_hook_self_test_all_pass` | Run `--self-test` on all 6 hooks | All exit 0 |
| `test_hook_payload_prompt_field` | UserPromptSubmit payload with `"prompt"` key (not `"user_prompt"`) | Hook reads prompt content correctly |
| `test_hook_payload_user_prompt_fallback` | UserPromptSubmit payload with `"user_prompt"` key (old format) | Hook reads prompt content correctly |
| `test_doctor_missing_hook_file` | Hook file deleted | `gt project doctor` reports `fail` |
| `test_doctor_unregistered_hook` | Hook file present but not in `settings.json` | Reports `warning` |
| `test_doctor_fix_restores_file` | `gt project doctor --fix` after hook deletion | Restores from template |
| `test_doctor_intentionally_disabled` | `groundtruth.toml [governance] disabled_hooks = ["delib-search-gate"]` | Doctor reports `info` not `fail` |
| `test_bash_mutation_surface` | PreToolUse on Bash with `echo x > src/foo.py` command | Advisory emitted (Bash writes to source paths) |

**Bash mutation surface coverage:** `spec-before-code.py` and `bridge-compliance-gate.py` also register on `PreToolUse:Bash`. When `tool_name == "Bash"`, the hook scans `tool_input.command` for output redirection patterns (`>`, `>>`, `tee`) targeting source paths. This addresses DELIB-0628's bypass failure mode.

---

## Updated Settings Template

`templates/project/settings.local.json` (updated from flat to nested format):

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Write", "Edit"],
    "deny": []
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/assertion-check.py"}
        ]
      },
      {
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/session-start-governance.py"}
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/intake-classifier.py"},
          {"type": "command", "command": "python .claude/hooks/delib-search-gate.py"}
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/destructive-gate.py"},
          {"type": "command", "command": "python .claude/hooks/credential-scan.py"},
          {"type": "command", "command": "python .claude/hooks/spec-before-code.py"},
          {"type": "command", "command": "python .claude/hooks/bridge-compliance-gate.py"}
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/spec-before-code.py"},
          {"type": "command", "command": "python .claude/hooks/bridge-compliance-gate.py"},
          {"type": "command", "command": "python .claude/hooks/kb-not-markdown.py"}
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/delib-search-tracker.py"}
        ]
      }
    ]
  }
}
```

Note: `settings.local.json` remains untracked. `gt project init` also generates a minimal `.claude/settings.json` (tracked) containing only the governance hooks that must survive across clones/worktrees. Tool permission allowlists remain in `settings.local.json` only.

---

## Open Decisions for Codex

1. **Warn vs block for bridge compliance.** Revised to use `permissionDecision: "ask"` for NEW/NO-GO bridge states (creates a visible decision checkpoint without hard-blocking). Is this acceptable for the dual-agent project setting, or should NO-GO state use `"deny"`?

2. **`source_paths` migration.** Adding `source_paths TEXT DEFAULT NULL` to the `specifications` table requires a schema migration. Should this migration be guarded by a version gate in the DB schema (e.g., `schema_version` table row) or is `ALTER TABLE ... ADD COLUMN ... DEFAULT NULL` (idempotent with `IF NOT EXISTS` guard) sufficient?

3. **Bash mutation detection scope.** The hook scans Bash commands for output redirections to source paths. Should this also cover `cp`, `mv`, `sed -i`, `awk -i`, and similar commands? Or is redirect-pattern detection sufficient for MVP?

4. **delib-search-log.jsonl location.** `.groundtruth/` is already the runtime artifact directory. Is this acceptable, or should the log live inside the KB (as a table row with `source_type = "search_log"`)? The table approach is queryable; the JSONL approach is greppable and avoids DB writes from hooks.

---

## Phase 1 Exit Criteria

1. All 6 hooks implemented under `src/groundtruth_kb/governance/`, imported by thin wrappers in `templates/hooks/`
2. 26 tests in `tests/test_governance_hooks.py` all pass
3. `settings.local.json` template updated to nested schema
4. `gt project init --profile dual-agent` generates `settings.json` (tracked) with all 6 hooks
5. Each hook exits 0 with valid JSON in `--self-test` mode
6. `gt project doctor` detects flat-format settings as `warning`
7. The `source_paths` migration applies cleanly on existing `groundtruth.db` databases
8. The 5 violations documented in S295 would each produce a visible advisory or `ask` checkpoint if hooks were active (demonstrated by pointing at the specific test case covering each violation)

---

## Phases 2-4 (deferred — separate proposals)

Phase 2 (scaffold integration), Phase 3 (recovery and resilience), and Phase 4 (observability) will be proposed separately once Phase 1 is VERIFIED. Their designs in `-001` remain the baseline for those future proposals.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
