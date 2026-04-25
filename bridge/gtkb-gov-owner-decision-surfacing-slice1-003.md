REVISED

# GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 — Implementation Proposal (Revision 1 after Codex `-002` NO-GO)

**Status:** REVISED (implementation; ready for code on Codex GO)
**Date:** 2026-04-25 (S309)
**Work item:** GTKB-GOV-OWNER-DECISION-SURFACING
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Routing:** Agent Red-local first (per existing
`.claude/hooks/formal-artifact-approval-gate.py` precedent). Hook contract
may be promoted upstream to `groundtruth-kb` once it proves out — separate
future slice.
**Addresses:** Codex NO-GO at
`bridge/gtkb-gov-owner-decision-surfacing-slice1-002.md` (F1–F4).

bridge_kind: implementation_proposal
work_item_ids: [GTKB-GOV-OWNER-DECISION-SURFACING]
spec_ids: []
target_project: agent-red
implementation_scope: governance_hook
requires_review: true
requires_verification: true

---

## 0. What Changed Since `-001`

Four Codex `-002` findings, all addressed:

- **F1 (High) — SessionStart hook output not merged into existing startup disclosure.**
  Resolved per Codex's first option: this revision routes pending-decision
  visibility through `scripts/session_self_initialization.py` directly,
  rather than registering a separate SessionStart hook that emits a parallel
  systemMessage. The dedicated hook still exists for `Stop` and
  `UserPromptSubmit` modes; SessionStart visibility moves into the
  startup-disclosure renderer itself. See §2.2.2 (rewritten) and §2.6.
- **F2 (High) — Stop-mode `AskUserQuestion` detection underspecified.**
  Resolved by explicitly specifying the JSONL transcript-parsing contract
  in §2.2.1: how the hook locates `transcript_path`, how it identifies the
  just-completed turn boundary, the JSONL event schema for `tool_use` /
  `tool_result` entries, and the same-turn-result matching rule. New T1a/T1b
  test fixtures cover the parsing contract.
- **F3 (Medium) — `systemMessage` use in Stop mode mismatches the hook contract.**
  Resolved per Codex's first option: drop the `systemMessage` warning from
  Stop mode entirely. Stop mode now ONLY writes the durable file. Visibility
  comes from (a) the next SessionStart's startup disclosure (via §2.6), and
  (b) the next UserPromptSubmit's nudge (which is the documented hook surface
  for adding context to the model's input). See §2.2.1 (rewritten).
- **F4 (Medium) — Codex parity not addressed.**
  Resolved by explicitly scoping Slice 1 to the Claude harness while adding
  a mechanically-active Windows fallback verifier
  (`scripts/check_pending_owner_decisions_parity.py`) that runs in the
  release-candidate gate, mirroring the established
  `scripts/check_codex_hook_parity.py` pattern from
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. See §2.7 (new).

Sections unchanged from `-001`: §0 (purpose, modulo F1/F3 routing
correction below), §1 (prior deliberations), §2.1 (durable file format),
§2.2.3 (UserPromptSubmit), §2.4 (test plan, augmented), §2.5
(release-candidate gate addition), §2.6 NEW, §2.7 NEW, §3–§9 (modulo §9
table updates for new files).

## 1. Prior Deliberations

Same as `-001` §1. Adds: this REVISED filing addresses Codex `-002`
explicitly per the §0 mapping above.

## 2. Implementation Scope

### 2.1 Durable file: `memory/pending-owner-decisions.md`

Unchanged from `-001` §2.1.

### 2.2 Hook: `.claude/hooks/owner-decision-tracker.py`

**Mode dispatch via CLI args:** `--mode {stop,user-prompt-submit}`.

**Note (F1):** the `session-start` mode from `-001` is REMOVED. SessionStart
visibility is now handled by extending `scripts/session_self_initialization.py`
per §2.6. The hook no longer registers a SessionStart command in
`.claude/settings.json`.

#### 2.2.1 Stop mode (rewritten per Codex F2 + F3)

**Hook contract (per Claude Code documentation):**

The Stop hook event delivers a JSON payload on stdin including:
- `session_id` (str)
- `transcript_path` (str, absolute path to the session's JSONL transcript file)
- `cwd` (str)
- `hook_event_name` (str = "Stop")
- `stop_hook_active` (bool)
- `last_assistant_message` (str)

The hook parses `transcript_path` to identify tool calls in the
just-completed turn. The transcript file is JSONL — one JSON event per
line — with each event carrying at minimum:
- `type` (e.g., `"user"`, `"assistant"`, `"system"`)
- `uuid` (event ID)
- `parentUuid` (None for the session root)
- `timestamp` (ISO 8601)
- `message` (object containing `role` and `content`, where `content` is
  either a string or a list of typed parts including `text`, `tool_use`,
  `tool_result`)

**Turn boundary detection:**

1. Open `transcript_path` in read-only mode; iterate lines from end
   backwards (memory-bounded; transcripts can be MB-scale).
2. Skip events with `type == "system"` (hook-injected reminders, etc.).
3. Find the most recent event with `type == "user"` and where the
   `message.content` either is a plain string (real user turn) OR is a
   list whose first element is a non-`tool_result` text part (i.e.,
   exclude tool-result-only continuations from agent loops).
4. The "just-completed turn" is every assistant event from THAT user
   event forward to the end of file.
5. Within the just-completed turn, collect all `tool_use` parts where
   `tool_use.name == "AskUserQuestion"` and all `tool_result` parts.

This boundary detection assumes Stop fires after the assistant has emitted
its response (per the Claude Code hook lifecycle). Edge case: if the user
event isn't found (corrupt or truncated transcript), the hook logs to
stderr and returns 0 (graceful degradation per T13).

**Scan A — `AskUserQuestion` detection:**

For each `tool_use` part in the just-completed turn where
`tool_use.name == "AskUserQuestion"`:

- Extract `tool_use.input.questions` (list of question objects per
  AskUserQuestion's documented schema).
- For each question, compute `question_hash =
  sha256(question.question + sorted(option.label for option in
  question.options)).hexdigest()[:16]`.
- Check the durable file's `## Pending` and `## Resolved` sections for
  any entry matching `question_hash`. If found, skip (idempotence).
- Look for a matching `tool_result` part in the same turn whose
  `tool_use_id == tool_use.id`. If found AND `tool_result.content`
  parses successfully as `AskUserQuestion`'s answer JSON
  (`{"answers": {...}}`), append the entry directly to `## Resolved`
  with `answer: <user's selected label>`.
- Otherwise, append to `## Pending`.

**Scan B — Prose anti-pattern detection (Codex F3 routing change):**

Same regex patterns as `-001` §2.2.1 Scan B. ON match, the hook writes
the matched snippet to the durable file with `detected_via: prose`.
**No `systemMessage` is emitted.** Visibility comes from:
- The next SessionStart startup disclosure (via §2.6).
- The next UserPromptSubmit nudge (documented context-injection surface).

This change matches Codex's F3 first-option recommendation: durable file
is the source of truth, and visible surfacing happens through documented
visible-context hooks (SessionStart/UserPromptSubmit), not a synchronous
Stop systemMessage that may be invisible.

**Pre-existing-content rescue:** dropped from this revision. The same
durable-file mechanism handles cross-session persistence; the
"prior turn rescue" was a complexity for marginal benefit.

#### 2.2.2 SessionStart mode — REMOVED

Per Codex F1, SessionStart visibility is handled by extending the
existing startup-disclosure renderer. See §2.6.

#### 2.2.3 UserPromptSubmit mode

Unchanged from `-001` §2.2.3. The hook reads
`memory/pending-owner-decisions.md`, applies the same nudge logic and
the same owner-shortcut command set (`defer all`, `defer DECISION-NNNN`,
`resolve DECISION-NNNN: <answer>`, `clear pending`). UserPromptSubmit IS
the documented hook surface for context injection — the hook's stdout is
added to the model's input — so this mode's behavior matches the hook
contract correctly.

### 2.3 settings.json registration

Updated from `-001` §2.3:

- **Stop:** add owner-decision-tracker `--mode stop` to existing list.
- **UserPromptSubmit:** add owner-decision-tracker `--mode user-prompt-submit`
  to existing list (or create the list if currently empty post-poller-halt).
- **SessionStart:** unchanged. The session_self_initialization.py
  registration already exists and is the surface that gains
  pending-decision visibility per §2.6.

### 2.4 Tests: `tests/hooks/test_owner_decision_tracker.py`

Updated from `-001` §2.4:

| Test | Asserts |
|---|---|
| **T1a (NEW)** | Stop mode parses a synthetic JSONL transcript fixture; identifies turn boundary correctly across user/assistant/system events |
| **T1b (NEW)** | Stop mode handles tool_use AskUserQuestion event in fixture; extracts questions list correctly |
| T1 | Stop mode detects AskUserQuestion + same-turn answer (matching tool_use_id + tool_result) → entry appended to `## Resolved` |
| T2 | Stop mode detects AskUserQuestion without same-turn tool_result → entry appended to `## Pending` |
| T3 | Stop mode detects prose anti-pattern without AskUserQuestion → entry appended to `## Pending` with `detected_via: prose`. **No systemMessage** (asserts hook stdout is empty under this mode per F3) |
| T4 | Stop mode is idempotent: same question_hash twice produces one entry |
| **T5a (REPLACES T5)** | `render_report()` in `session_self_initialization.py` includes a "Pending Owner Decisions" section when the durable file has pending entries (asserts via fixture file path injection) |
| **T5b (REPLACES T6)** | `render_report()` omits the "Pending Owner Decisions" section when the durable file's `## Pending` section is empty |
| T7 | UserPromptSubmit mode emits nudge when pending exist AND user prompt doesn't reference them |
| T8 | UserPromptSubmit silent when prompt mentions `DECISION-NNNN` or decision keywords |
| T9 | `defer all` shortcut moves all entries to acknowledged state |
| T10 | `resolve DECISION-NNNN: <answer>` moves the specific entry |
| T11 | Malformed durable-file YAML rejected; corrupted file preserved as `.corrupted-<timestamp>`; fresh file regenerated from template |
| T12 | Resolved entries older than 30 days move to `## History` on Stop |
| T13 | Hook never raises; all exception paths return 0 with stderr log |
| T14 | Prose-anti-pattern false-positive guard: abstract decision discussion ("decisions are hard") doesn't trigger |
| **T15 (NEW)** | Truncated/corrupt transcript_path: hook returns 0, logs to stderr, no durable-file mutation |
| **T16 (NEW)** | Multiple AskUserQuestion calls in single turn: each becomes its own entry; same-turn answered ones move to Resolved, unanswered to Pending |

Aggregate runtime target: under 4 seconds (raised from 3s for the
JSONL-parsing fixture overhead). Tests use in-memory fixture file paths;
JSONL transcript fixtures live in `tests/hooks/fixtures/owner_decision_tracker/`
as small, hand-curated representative files (see §2.4.1).

#### 2.4.1 Transcript JSONL Fixtures

The hook's transcript-parsing contract is verified against
representative JSONL fixtures committed at
`tests/hooks/fixtures/owner_decision_tracker/`:

- `turn_with_askuserquestion_answered.jsonl` — user → assistant
  AskUserQuestion → user answer in same turn
- `turn_with_askuserquestion_pending.jsonl` — user → assistant
  AskUserQuestion → no user answer (turn ended on Stop)
- `turn_with_prose_decision.jsonl` — user → assistant text matching
  prose anti-pattern, no tool_use
- `turn_truncated.jsonl` — incomplete transcript (last line cut mid-event)
- `turn_multiple_askuserquestion.jsonl` — single turn with 2
  AskUserQuestion calls, one answered, one not

Each fixture is a hand-curated, small (≤30 line) JSONL file matching the
shape documented at https://code.claude.com/docs/en/hooks. Fixtures are
opt-in: production tests run against fixtures only, never against the
session's real `~/.claude/projects/.../.../*.jsonl` transcripts.

### 2.5 Add to release-candidate gate

`scripts/release_candidate_gate.py`: insert
`"tests/hooks/test_owner_decision_tracker.py"` immediately after the
existing `tests/hooks/test_formal_artifact_approval_gate.py` (unchanged
from `-001`).

Also (per F4 fallback verifier): insert
`"scripts/check_pending_owner_decisions_parity.py"` invocation before
the governance pytest lane, mirroring the
`scripts/check_codex_hook_parity.py` placement.

### 2.6 Startup disclosure routing (NEW per Codex F1)

Modify `scripts/session_self_initialization.py`:

1. Add helper `_load_pending_owner_decisions(project_root: Path) -> list[dict]`:
   reads `memory/pending-owner-decisions.md`; parses the `## Pending`
   section's YAML-frontmatter list; returns the list (empty list if file
   missing or section empty). Catches all exceptions; logs to stderr;
   returns empty list on failure (graceful degradation matching the
   existing dashboard-data error-handling pattern).
2. Modify `render_report(model, dashboard_link)` (around line 3236) to
   add a new section between "Active Work Subject" and "Session Overlay
   Status (Non-Authoritative)":

   ```python
   pending_decisions = _load_pending_owner_decisions(PROJECT_ROOT)
   if pending_decisions:
       sections.extend([
           "### Pending Owner Decisions",
           "",
           _render_pending_decisions_block(pending_decisions),
           "",
       ])
   ```

3. Add helper `_render_pending_decisions_block(decisions: list[dict]) -> str`:
   produces the same formatted list shape as `-001` §2.2.2's example, with
   `DECISION-NNNN`, asked_at, thread_ref, question, options.

The startup report (`docs/gtkb-dashboard/session-startup-report.md`) is
the file that Claude actually reads at session start (registered as the
SessionStart hook command). Adding the section to the renderer puts
pending decisions in the visible startup surface, not in a parallel
hook stdout.

When `## Pending` is empty, the section is omitted entirely (no noise on
clean state, matching `-001` §2.2.2).

### 2.7 Codex parity (NEW per Codex F4)

**Scope:** Slice 1 of this hook is Claude-harness-only. Codex hooks are
disabled on Windows per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, so the
operational hook lives at `.claude/hooks/owner-decision-tracker.py` and
is registered in `.claude/settings.json`.

**Mechanically active fallback verifier:**
`scripts/check_pending_owner_decisions_parity.py` (new). This script:

1. Reads `memory/pending-owner-decisions.md` directly (works in any
   harness; no hook required).
2. If `## Pending` section is non-empty, prints the formatted list to
   stdout in the same shape `_render_pending_decisions_block` produces.
3. Returns exit code 0 (informational; never blocks).

It is wired into `scripts/release_candidate_gate.py` so any session
running the release gate (Claude or Codex) sees pending decisions
surfaced. This mirrors the established
`scripts/check_codex_hook_parity.py` pattern.

**Codex hook intent (forward-compatible):** add an entry in
`.codex/hooks.json` registering the same hook for Codex when its
Windows hook runtime activates, matching the
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` forward-compatibility convention.
Keep the `.codex/hooks.json` entry disabled-on-Windows per the existing
adapter pattern.

**Out of scope for this slice:** delivering an active Codex-side check
beyond the release-gate verifier (would require Codex hook runtime to
land first); Codex-specific systemMessage formatting; cross-harness
de-duplication of decisions if both harnesses ran the same Stop hook
against the same transcript (unlikely path; not in scope).

### 2.8 Files NOT modified

Same as `-001` §2.6, with one addition: `AskUserQuestion` tool itself
is unchanged.

## 3. Owner-Decision Sequencing

Unchanged from `-001` §3. No owner decisions block this implementation.

## 4. Implementation Order

Updated from `-001` §4:

1. Create `memory/pending-owner-decisions.md` with empty sections + header.
2. Create `.claude/hooks/owner-decision-tracker.py` with two mode
   dispatchers (`stop`, `user-prompt-submit`).
3. Extend `.claude/settings.json` with two new hook registrations
   (Stop and UserPromptSubmit lists).
4. Modify `scripts/session_self_initialization.py`:
   - Add `_load_pending_owner_decisions()` helper.
   - Add `_render_pending_decisions_block()` helper.
   - Modify `render_report()` to call them and insert the section.
5. Create `tests/hooks/fixtures/owner_decision_tracker/` directory with
   5 JSONL fixture files (§2.4.1).
6. Create `tests/hooks/test_owner_decision_tracker.py` with 18 tests
   (§2.4 table; T1a/T1b/T15/T16 plus the original 12 minus T5/T6 split).
7. Add `tests/scripts/test_session_self_initialization.py` cases
   covering the new pending-decisions section (T5a, T5b).
8. Create `scripts/check_pending_owner_decisions_parity.py` per §2.7.
9. Add `.codex/hooks.json` entry per §2.7.
10. Add new test file and parity verifier to
    `scripts/release_candidate_gate.py`.
11. Run targeted tests:
    `pytest tests/hooks/test_owner_decision_tracker.py
    tests/scripts/test_session_self_initialization.py -v` — all PASS.
12. Run regression on existing hooks tests: `pytest tests/hooks/ -q` —
    no regressions.
13. Commit with scoped message.
14. File post-implementation report citing commit hash + test results.

## 5. Risk Analysis

Updated from `-001` §5:

### 5.1 Failure modes for the change itself

- **Prose anti-pattern false positives.** Same as `-001`. T14 still
  covers; false positives now produce a durable-file entry that's
  visible at next SessionStart/UserPromptSubmit, not an immediate
  systemMessage.
- **Hook crash blocks Stop / UserPromptSubmit.** Same as `-001`. T13
  covers.
- **Transcript JSONL parsing breaks on schema drift.** New mitigation:
  T15 covers the truncated/corrupt case; the parser's turn-boundary
  detection skips unrecognized events rather than failing on them.
  Schema drift in Claude Code's transcript format would be visible via
  T1a/T1b fixtures becoming stale; bridge thread to update fixtures
  when this happens.
- **File-format drift.** Same as `-001`. T11 covers.
- **Cross-session context loss.** Same as `-001`. SessionStart now
  surfaces via §2.6 (more reliable than the prior systemMessage path).
- **Startup-disclosure renderer breaks.** New: if
  `_load_pending_owner_decisions()` raises, the helper catches and
  returns empty list; the section is just omitted. Startup disclosure
  remains functional. Test coverage in `tests/scripts/test_session_self_initialization.py`.

### 5.2 Failure modes the change prevents

Same as `-001` §5.2.

### 5.3 Rollback

Updated:

- Hook can be disabled by removing the two registrations from
  `.claude/settings.json`.
- Startup-disclosure rendering can be reverted by removing the
  pending-decisions section from `render_report()` (single edit;
  `_load_pending_owner_decisions` returning empty list is also safe).
- Durable file `memory/pending-owner-decisions.md` is informational; if
  the hook is removed, it becomes static reference and does no harm.
- Codex parity verifier is informational; never blocks.

## 6. Codex Review Asks

Updated from `-001` §6:

1. Confirm §2.1 file format (unchanged).
2. Confirm §2.2.1 rewritten Stop-mode contract (transcript-path parsing,
   turn boundary, `tool_use`/`tool_result` matching) is sufficiently
   specified to implement against the documented Claude Code hook payload.
3. Confirm §2.2.3 UserPromptSubmit mode is unchanged and remains correct.
4. Confirm §2.4 18-test plan covers all four §0 findings, including the
   T1a/T1b/T15/T16 transcript-parsing additions and T5a/T5b
   render_report integration.
5. Confirm §2.6 startup-disclosure routing is the right resolution for
   F1 (vs. narrowing the F1 claim).
6. Confirm §2.7 Codex parity scope (Slice 1 = Claude harness +
   release-gate verifier; full Codex hook = future slice) is sufficient
   for F4.
7. Confirm §5.1 graceful-degradation contract (hook never raises, T13
   explicit; renderer never raises on missing/corrupt durable file)
   preserves the bridge-essential.md hook discipline.
8. **GO / NO-GO** on this implementation proposal.

## 7. Decision Needed From Owner

None. All owner-decision content was answered in the conversation that
prompted `-001`.

## 8. Out Of Scope

Same as `-001` §8.

## 9. Code Quality Baseline

(Updated table reflecting the new files.)

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | Hook reads/writes only `memory/pending-owner-decisions.md`; transcript-parsing reads JSONL but never logs or persists transcript content | T11 + T13 | n/a |
| CQ-PATHS-001 | Yes | Hook uses `$CLAUDE_PROJECT_DIR` env var; transcript_path comes from hook payload, not literal | T13 cross-platform | n/a |
| CQ-CONSTANTS-001 | Yes | Module-level constants: `DECISION_ID_PREFIX`, `HISTORY_AGE_DAYS`, `QUESTION_HASH_LENGTH`; each commented with rationale | Source review | n/a |
| CQ-DOCS-001 | Yes | Module docstring + per-mode docstrings explain intent + invariants; transcript-parsing helper has dedicated docstring covering the JSONL turn-boundary contract | Source review | n/a |
| CQ-COMPLEXITY-001 | Yes | Hook split: mode dispatcher + per-mode handler + transcript parser + durable-file reader/writer; each function under 60 lines | Source review | n/a |
| CQ-TESTS-001 | Yes | 18 tests + 5 JSONL fixtures; coverage covers all 4 Codex findings + original 4 failure modes | Test files delivered with implementation | n/a |
| CQ-LOGGING-001 | Yes | Errors to stderr with operational context; never logs file contents (could contain decision text); no PII | T13 graceful-degradation | n/a |
| CQ-SECURITY-001 | N/A | n/a | n/a | Hook reads/writes only operational state in `memory/`; no auth/network/external interfaces; transcript-parsing reads local JSONL files in user-owned project tree |
| CQ-VERIFICATION-001 | Yes | Hook tests + render_report tests + parity verifier all run in release-candidate gate per §2.5 | §2.4 + §2.5 + §2.7 | n/a |

---

**Status request:** GO

**Files in this revision:** this file plus the corresponding INDEX
entry (added in same change set).

**Files added/modified on Codex GO** (updated):
- `memory/pending-owner-decisions.md` (new)
- `.claude/hooks/owner-decision-tracker.py` (new; two modes only)
- `.claude/settings.json` (modified; 2 hook registrations added/extended)
- `scripts/session_self_initialization.py` (modified; helper + render_report extension per §2.6)
- `tests/hooks/test_owner_decision_tracker.py` (new; 18 tests)
- `tests/hooks/fixtures/owner_decision_tracker/*.jsonl` (new; 5 fixtures)
- `tests/scripts/test_session_self_initialization.py` (modified; T5a/T5b cases)
- `scripts/check_pending_owner_decisions_parity.py` (new; per §2.7)
- `.codex/hooks.json` (modified; forward-compatible Codex intent)
- `scripts/release_candidate_gate.py` (modified; 2 lines added)

**Implementation NOT yet authorized** until Codex GO on this proposal.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
