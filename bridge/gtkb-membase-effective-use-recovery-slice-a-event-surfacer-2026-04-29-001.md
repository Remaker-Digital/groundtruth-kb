NEW

# GTKB MemBase Effective Use Recovery — Slice A Implementation: Spec/Intake Event Surfacer

**Status:** NEW (implementation bridge for Slice A of `gtkb-membase-effective-use-recovery-2026-04-29` umbrella; Codex GO at -002)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex required Prime action #2 from membase-recovery GO at `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md`: "File Slice A as a new implementation bridge before modifying any hook code."

bridge_kind: implementation_proposal
work_item_ids: [GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY]
spec_ids: [SPEC-INTAKE-2485e9]
parent_bridge: bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md (umbrella scoping; GO at -002)
target_project: groundtruth-kb (upstream + adopter consume via gt project upgrade)
implementation_scope: hook + ledger + tests
requires_review: true
requires_verification: true

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate. Codex MUST issue rejection on this proposal if any relevant specification is missing.

**Primary spec served:**
- `SPEC-INTAKE-2485e9` — "Surface spec creation/update events in owner chat view". Verified to exist in KB (commit `ed4d7b37` filing of umbrella). This Slice A is the first implementation that satisfies this spec.

**Umbrella & sister-bridge linkage:**
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` (umbrella scoping; approved at -002) — Slice A is the first slice; per umbrella section 3.1 and section 6 sequencing.
- Codex approval at `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md` Non-Blocking Conditions for Follow-On Bridges item 1 — Slice A must prove the chat-visible event path mechanically; specify exact hook event(s), hook registration files, per-session start timestamp source, ledger location, and duplicate-suppression behavior. This proposal directly addresses each item.

**Governance specs / records that constrain this work:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-protocol audit-trail discipline; the surfacer reads from KB only, so audit-trail invariants are preserved.
- `GOV-ARTIFACT-APPROVAL-001` plus `ADR-ARTIFACT-FORMALIZATION-GATE-001` — this slice does not mutate the Deliberation Archive or formal records; it only observes KB rows and emits chat-visible events. The formal-artifact-approval gate does not apply to this slice (it will apply to Slice B which adds auto-capture).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the surfacer is a lifecycle-trigger producer (it announces lifecycle events to the owner); aligns with artifact-oriented governance.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the surfacer is a deterministic service (per-session ledger plus idempotent emission); reduces AI-mediated event-surfacing burden.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook registration must mirror to `.codex/hooks.json` for Codex-side consumption (per the Windows-runtime fallback contract).

**Adjacent / parallel work:**
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md` (REVISED; approved at -004) — schema migration that will eventually replace `status` with date columns. Slice A must be schema-tolerant; design uses `changed_at` (which exists in BOTH old and new schemas). Status-string interpretation is bounded to the emission format only (which can be updated when schema migrates).
- `bridge/active-workspace-declaration-architecture-2026-04-29-003.md` (REVISED) — vocabulary alignment; Slice A's emission format includes `parent` field placeholder for future schema (currently shows `parent=unset` until schema lands).

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`; upstream changes route to `E:\GT-KB\groundtruth-kb\`.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Root Boundary Gate, Mandatory Specification Linkage Gate, Mandatory Specification-Derived Verification Gate satisfied here.
- `.claude/rules/codex-review-gate.md` — Codex must reject unlinked proposals.

---

## Specification-Derived Verification (Test Mapping)

Per file-bridge-protocol Mandatory Specification-Derived Verification Gate, every test below derives from `SPEC-INTAKE-2485e9` ("Surface spec creation/update events in owner chat view") and Codex approval condition 1:

| Spec clause / Codex condition | Test |
|-------------------------------|------|
| SPEC-INTAKE-2485e9: surface spec events in owner chat view | `test_surfacer_emits_chat_visible_event_for_new_spec` — creates a spec row in test KB; asserts hook produces a systemMessage with the canonical format. Run via `pytest groundtruth-kb/tests/test_spec_event_surfacer.py -v`. |
| Codex condition: per-session seen ledger plus idempotency | `test_surfacer_does_not_duplicate_event_on_repeated_invocation` — runs hook twice on the same KB state; asserts second invocation produces no events. Run via `pytest`. |
| Codex condition: per-session start timestamp source | `test_surfacer_ignores_pre_session_rows` — pre-populates KB with rows whose `changed_at < session_started_at`; asserts these rows are NOT surfaced. Run via `pytest`. |
| Codex condition: exact hook event(s) | `test_surfacer_runs_on_post_tool_use_and_stop` — registers hook on both events; asserts hook fires (and is idempotent across both event types). Run via `pytest`. |
| Codex condition: hook registration files | `test_settings_json_registers_surfacer` — asserts `.claude/settings.json` includes the registration; `test_codex_hooks_json_registers_surfacer` asserts `.codex/hooks.json` has matching intent. Run via `pytest tests/scripts/test_codex_hook_parity.py`. |
| Codex condition: ledger location | `test_ledger_location_is_session_scoped` — asserts ledger written to `.claude/session/spec-events-seen.jsonl`; new session implies fresh ledger. Run via `pytest`. |
| Codex condition: duplicate-suppression behavior | `test_surfacer_handles_concurrent_invocations_safely` — concurrent hook invocations don't double-emit; ledger writes are atomic-rename (not mid-write). Run via `pytest`. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full surfacer test suite as part of the regression gate.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` (lo_review, S319) — substance basis for the umbrella; this slice is the first of four implementation deliverables.
- `bridge/gtkb-membase-effective-use-umbrella-001.md` (filed earlier; phantom -014; surviving scoping artifact) — original Slice A design pattern (PostToolUse plus Stop plus per-session ledger); preserved here.
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` (umbrella scoping; approved at -002) — Slice A scoping per section 3.1.
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md` (Codex approval; -002) — six non-blocking conditions; condition 1 directly drives this proposal's design.
- No prior deliberation reverses this approach.

---

## 1. Implementation Design

### 1.1 Hook Events (per Codex condition: exact hook event(s))

The surfacer registers on two events:

- `PostToolUse` — fires after `Bash`, `Write`, or `Edit` tool calls (any tool that could have mutated the KB via direct API calls). Catches in-turn KB writes.
- `Stop` — fires at end of turn. End-of-turn sweep catches any KB writes that happened outside PostToolUse coverage (e.g., from a hook that ran during the turn).

Both events route to the same hook script with the same logic. The per-session ledger ensures idempotency across the two paths.

Why both: PostToolUse alone could miss events from hook-driven KB writes (which run between tool calls, not after). Stop alone would batch all events to end-of-turn (delayed visibility). Together: in-turn visibility (PostToolUse) plus end-of-turn coverage (Stop) with idempotency guard.

### 1.2 Hook Registration Files (per Codex condition: hook registration files)

Live (Agent Red consumer):
- `.claude/settings.json` — adds two entries to `hooks.PostToolUse` and `hooks.Stop` arrays. Existing Stop entry is supplemented (not replaced).
- `.codex/hooks.json` — matching intent for Codex parity per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Currently disabled on Windows; intent preserved for non-Windows Codex.

Upstream template (consumed via `gt project upgrade`):
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py` — the hook script.
- `groundtruth-kb/templates/settings/post_tool_use.json` (extends existing template if present; new file otherwise) — hook registration template.
- `groundtruth-kb/src/groundtruth_kb/hooks_registry.py` — registry entry so `gt project upgrade` knows to install this hook.

### 1.3 Per-Session Start Timestamp Source (per Codex condition: per-session start timestamp source)

Primary source: existing `scripts/session_self_initialization.py` writes a session-start timestamp to `.claude/session/session-start.json` at SessionStart event. Schema:

```json
{
  "session_started_at": "2026-04-29T17:30:00.000000+00:00",
  "session_id": "S322",
  "harness": "claude"
}
```

The surfacer reads `session_started_at` from this file. If the file exists and is parseable, that timestamp is the lower bound for "in-session" events.

Fallback (file missing or malformed): the surfacer reads its own ledger's first entry's `seen_at` minus 1 second; if the ledger is empty, it falls back to the current time (which means no events are surfaced this turn but the ledger is initialized for subsequent turns). This is a fail-open-with-degradation behavior; the surfacer never crashes the session on missing session-start data.

Per Slice A scope: the surfacer assumes the existing SessionStart hook writes the session-start.json file. If that's not present, Slice A's implementation includes adding the write as a one-line addition to `scripts/session_self_initialization.py`. This is a small add covered by test fixtures.

### 1.4 Ledger Location (per Codex condition: ledger location)

Path: `.claude/session/spec-events-seen.jsonl`

Format: one JSON object per line (JSONL):
```jsonl
{"spec_id": "SPEC-INTAKE-c9e997", "version": 1, "seen_at": "2026-04-29T17:31:15.000000+00:00", "kind": "created"}
{"spec_id": "GTKB-COMMIT-TRIAGE-001", "version": 1, "seen_at": "2026-04-29T17:35:42.000000+00:00", "kind": "created"}
{"spec_id": "GTKB-COMMIT-TRIAGE-001", "version": 2, "seen_at": "2026-04-29T17:48:01.000000+00:00", "kind": "updated"}
```

Fields:
- `spec_id` (str): KB row id.
- `version` (int): KB row version number.
- `seen_at` (str): ISO8601 UTC timestamp when surfacer emitted the event.
- `kind` (str): "created" (version=1) or "updated" (version>1).

Lifecycle: the ledger is per-session. New session implies fresh ledger (the existing SessionStart hook initializes an empty file at `.claude/session/spec-events-seen.jsonl` if absent). End of session implies ledger archived to `.claude/session/archive/spec-events-seen-{session-id}.jsonl` for audit (Slice A doesn't implement archive; that's deferred to a future hygiene slice).

Atomicity: ledger writes use the same atomic-rename pattern as other GT-KB hooks (write to `.tmp.<pid>` then `os.replace`). Per Codex condition: duplicate-suppression behavior — atomic writes plus per-session ledger semantics together prevent race conditions.

### 1.5 Detection Query

SQL (against `groundtruth.db`):
```sql
SELECT id, version, title, type, status, section, changed_at
FROM current_specifications
WHERE changed_at >= :session_started_at
  AND (id, version) NOT IN (
    -- ledger contents loaded from JSONL into a CTE for the query
    SELECT spec_id, version FROM session_seen_ledger
  )
ORDER BY changed_at;
```

In Python the surfacer:
1. Loads ledger from JSONL into a Python `set[tuple[str, int]]`.
2. Queries `current_specifications` for rows with `changed_at >= session_started_at`.
3. Filters out rows already in the ledger set.
4. Emits one systemMessage per remaining row.
5. Appends new rows to the ledger (atomic rename).

### 1.6 Emission Format

Per spec event (chat-visible systemMessage):

```
[KB-SPEC-EVENT] <spec_id> v<version> -- <kind> -- <title> [type=<type> status=<status> section=<section>]
```

Concrete examples:
```
[KB-SPEC-EVENT] SPEC-INTAKE-c9e997 v1 -- created -- Extract specifications from conversation in-session [type=requirement status=specified section=membase-effective-use]
[KB-SPEC-EVENT] GTKB-COMMIT-TRIAGE-001 v2 -- updated -- Triage uncommitted file drift into bridge-thread-scoped commits [type=work_item status=resolved section=hygiene]
```

(Plain-text marker `[KB-SPEC-EVENT]` chosen over emoji for grep-ability per umbrella open question 4. Owner can request emoji change at impl review.)

Note on schema migration tolerance: when `gtkb-spec-lifecycle-schema-2026-04-29-003.md` lands its slices, the `status=` field will be replaced with date-derived lifecycle ("active/unverified", "implemented", "retired"). Slice A's emission code reads `status` from the row dictionary; if the schema migration removes that column, the emission format updates accordingly in a small follow-on commit (out of Slice A scope; tracked as a Slice A close-out followup).

### 1.7 Duplicate-Suppression Behavior (per Codex condition)

Three layers of suppression:

1. Per-session ledger — primary mechanism. Ledger entry exists implies no re-emission.
2. Atomic ledger writes — prevent partial-write states that would leave a row unsurfaced after crash.
3. Read-before-emit — surfacer re-reads the ledger immediately before emitting (handles concurrent invocations from PostToolUse plus Stop on the same turn).

---

## 2. Files Touched

Upstream (`groundtruth-kb/`):
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (NEW; ~150 lines)
- `groundtruth-kb/templates/settings/post_tool_use.json` (NEW or extend existing; ~10 lines)
- `groundtruth-kb/src/groundtruth_kb/hooks_registry.py` (extend; ~5 lines)
- `groundtruth-kb/tests/test_spec_event_surfacer.py` (NEW; ~250 lines covering all derivation tests)
- `groundtruth-kb/docs/reference/hooks.md` (extend; ~30 lines documentation)

Live (Agent Red consumer; via `gt project upgrade`):
- `.claude/hooks/spec-event-surfacer.py` (NEW; identical to upstream template)
- `.claude/settings.json` (modify; add 2 hook registrations to PostToolUse plus Stop arrays)
- `.codex/hooks.json` (modify; add matching intent per ADR-CODEX-HOOK-PARITY-FALLBACK-001)
- `scripts/session_self_initialization.py` (extend if needed; ensure session-start.json includes `session_started_at` field — checked at impl time)

Tests (Agent Red side):
- `tests/hooks/test_spec_event_surfacer_integration.py` (NEW; integration tests against live `groundtruth.db` schema)

Other:
- `scripts/release_candidate_gate.py` — wire `tests/hooks/test_spec_event_surfacer_integration.py` into the gate.
- `memory/work_list.md` — update row 19 on VERIFIED to mark Slice A done.

---

## 3. Verification Plan

### 3.1 Tests (per Specification-Derived Verification table above)

All seven test cases from the derivation table above must pass in CI:

```bash
# Upstream
pytest groundtruth-kb/tests/test_spec_event_surfacer.py -v

# Adopter integration
pytest tests/hooks/test_spec_event_surfacer_integration.py -v

# Release-gate inclusion
python scripts/release_candidate_gate.py --skip-frontend
```

### 3.2 Manual Verification (per Codex chat-visibility condition)

After implementation, verify chat visibility by:
1. Insert a test spec via `python -c "from groundtruth_kb import KnowledgeDB; KnowledgeDB().insert_spec(...)"`.
2. Wait for next PostToolUse OR Stop event.
3. Confirm the systemMessage appears in the chat stream (not just in logs).

### 3.3 Non-Regression

- `tests/scripts/test_release_candidate_gate.py` continues to pass.
- `tests/hooks/test_owner_decision_tracker.py` and other hook tests continue to pass (no shared state with surfacer).
- Existing classifier behavior (`spec-classifier.py`) unchanged in this slice (Slice B will modify it).

---

## 4. Acceptance Criteria

1. Functional: all seven test cases from the Specification-Derived Verification table pass.
2. Chat visibility: manual verification per section 3.2 confirms systemMessage appears in owner-visible chat.
3. Idempotency: repeated PostToolUse plus Stop hook invocations on the same KB state produce no duplicate events.
4. Per-session bounded: events from `changed_at < session_started_at` are not surfaced.
5. Hook registration: `.claude/settings.json` and `.codex/hooks.json` both include the registration; `tests/scripts/test_codex_hook_parity.py` continues to pass.
6. Schema tolerance: the surfacer reads `status` from the row dictionary; if/when that column is removed by spec-lifecycle migration, emission format updates without crashing.
7. KB write isolation: the surfacer NEVER writes to `groundtruth.db` (read-only consumer); zero `INSERT`/`UPDATE`/`DELETE` SQL in the surfacer's code path.
8. Performance: detection query uses indexed `changed_at` column; surfacer runtime under 200ms per invocation against current 2,153-row KB.

---

## 5. Sequencing and Concurrency

Internal: Slice A is a single coherent change; no internal sequencing.

External:
- Slice A is the FIRST of four slices in `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` (per umbrella section 3 ordering: A → B → C → D).
- Slice B (auto-capture) depends on Slice A being VERIFIED (so captures are observable).
- WI-harvest reconciliation track (parallel) doesn't depend on Slice A.

Concurrency safety: atomic ledger writes plus read-before-emit pattern handle concurrent PostToolUse plus Stop invocations.

---

## 6. Project Root Boundary

Per `.claude/rules/project-root-boundary.md`:
- All new and modified files under `E:\GT-KB`.
- Upstream changes routed to `E:\GT-KB\groundtruth-kb\`.
- Adopter consumption via `gt project upgrade` from in-root sources.

---

## 7. Out of Scope

- Slice B auto-capture (separate bridge `gtkb-membase-effective-use-recovery-slice-b-auto-capture-2026-04-29` after Slice A VERIFIED).
- Ledger archival at end-of-session (deferred to a future hygiene slice).
- Cross-session visibility (events from prior sessions are not re-surfaced; ledger is per-session by design).
- UI dashboard integration (events are chat-visible only; dashboard surfacing is separate work).
- Spec-event filtering (e.g., "only surface specs with `parent='gtkb'`"); all in-session spec writes are surfaced.
- Schema-migration adaptation (Slice A targets current schema; emission format will need update when `gtkb-spec-lifecycle-schema-2026-04-29` slices land — out of Slice A scope).

---

## 8. Rollback Plan

Per umbrella section 5 acceptance criterion 6 ("rollback plan that disables hooks without corrupting MemBase or DA state"):

To disable Slice A:
1. Remove the two registrations from `.claude/settings.json` (PostToolUse plus Stop arrays).
2. Remove the matching intent from `.codex/hooks.json`.
3. Helper code at `.claude/hooks/spec-event-surfacer.py` and `groundtruth-kb/templates/hooks/spec-event-surfacer.py` left in place (audit trail; can be re-enabled by re-adding the registrations).
4. The ledger file at `.claude/session/spec-events-seen.jsonl` may be left in place or removed; either way, no KB or DA state is affected.
5. Slice A makes ZERO writes to `groundtruth.db` and ZERO writes to the Deliberation Archive; rollback has no risk of KB or DA corruption.

---

## 9. Open Questions for Loyal Opposition Review

1. Ledger archival timing. Slice A defers ledger archival to a future hygiene slice (per section 7 out-of-scope). Should it be in Slice A scope to avoid orphaned ledgers across sessions?

2. Schema migration adaptation timing. Slice A reads `status` from the row dictionary. When the spec-lifecycle migration lands, the emission format needs updating. Should that be a small follow-on bridge OR included in Slice A scope as a "schema-tolerant emission format from day one"?

3. PostToolUse tool-targeting scope. Section 1.1 lists Bash, Write, Edit. Should this also include Task (subagent invocation) since subagents could mutate KB? Or is the Stop end-of-turn sweep sufficient for those cases?

4. Hook ordering. When PostToolUse and Stop both fire on the same turn, the surfacer runs twice. Per section 1.7 the ledger handles idempotency, but should there be an explicit "skip Stop run if PostToolUse already ran in this turn" optimization? Or is the idempotency guard sufficient?

---

## 10. Aligns With

- SPEC-INTAKE-2485e9 (the spec being satisfied).
- Umbrella `gtkb-membase-effective-use-recovery-2026-04-29-001` approved at -002 (per Codex required next Prime action 2).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (deterministic per-session ledger; idempotent emission; reduces AI surfacing burden).
- DELIB-0874 (artifact-oriented governance; the surfacer announces lifecycle events as artifacts).
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 (Codex-side intent preserved).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
