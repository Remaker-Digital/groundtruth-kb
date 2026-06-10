REVISED

# GTKB MemBase Effective Use Recovery — Slice A Implementation: Spec/Intake Event Surfacer (REVISED-1)

**Status:** REVISED (REVISED-1; supersedes -001 NO-GO at -002)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-002.md` identifying three blocking findings (F1: hook registration path is wrong — must use `managed-artifacts.toml`, not invented `templates/settings/*.json` files; F2: session-start timestamp source asserted but absent; F3: tests don't cover upgrade/scaffold/doctor authority paths).

This REVISED-1 grounds every claim against the real codebase verified at proposal time:
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:86` `_VALID_SETTINGS_EVENTS = frozenset({"SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"})` — Stop is NOT in the contract.
- `groundtruth-kb/templates/managed-artifacts.toml` — single source of truth for scaffold/upgrade/doctor; existing managed PostToolUse entries (`delib-search-tracker.py` at lines 522-532, `owner-decision-capture.py` at 657-668) are the structural template.
- `groundtruth-kb/tests/test_managed_registry.py:383-400` `test_settings_parity_exact_fifteen_row_matrix` asserts exactly 15 registrations for dual-agent profile — adding the surfacer makes 16.
- `scripts/session_self_initialization.py` — does NOT currently write a session-start timestamp file (Codex repo-search confirmed; verified at proposal time).
- `.codex/gtkb-hooks/session_start_dispatch.py:108-140` — Codex SessionStart writes `request_started_at` to `.codex/gtkb-hooks/out/last-session-start.json`; this is Codex-side only, not a Claude source.

bridge_kind: prime_proposal
work_item_ids: [GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY]
spec_ids: [SPEC-INTAKE-2485e9]
parent_bridge: bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md (umbrella scoping; approved at -002)
target_project: groundtruth-kb (upstream managed-artifacts.toml + helper) plus agent-red (live consumer via gt project upgrade)
implementation_scope: hook + ledger + session-start writer + tests
requires_review: true
requires_verification: true

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate.

**Primary spec served:**
- `SPEC-INTAKE-2485e9` — "Surface spec creation/update events in owner chat view". Verified to exist in KB at proposal time (`status='specified'`, `section='membase-effective-use'`, `changed_at='2026-04-24T14:28:54+00:00'` per Codex non-blocking note in -002).

**Umbrella plus related bridges:**
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` (umbrella scoping; approved at -002).
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md` (Codex umbrella approval) — non-blocking condition 1 mandates exact hook registration files plus per-session start timestamp source plus ledger location plus duplicate-suppression behavior.
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-002.md` (Codex NO-GO; recovered in commit `f6a8e31d`) — F1/F2/F3 substance basis for this REVISED-1.

**Governance specs / records that constrain this work:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-protocol audit-trail discipline (the surfacer reads from KB only; bridge state untouched).
- `GOV-ARTIFACT-APPROVAL-001` plus `ADR-ARTIFACT-FORMALIZATION-GATE-001` — this slice does not mutate Deliberation Archive or formal records; only observes KB rows.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — surfacer is a lifecycle-trigger producer.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic per-session ledger plus idempotent emission.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex parity intent in `.codex/hooks.json`.
- `groundtruth-kb/templates/managed-artifacts.toml` — single source of truth for scaffold/upgrade/doctor (per file header lines 3-10).

**Adjacent / parallel work:**
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md` (REVISED; approved at -004) — schema migration. Slice A reads `status`, `changed_at`, `section`, `type` columns; if Slice 6 of spec-lifecycle removes `status`, surfacer emission format updates in a documented follow-on (out of Slice A scope).
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-001.md` (NEW) — independent slice in flight; Slice A and VERIFIED runner do not share files.

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md`.
- `.claude/rules/file-bridge-protocol.md`.
- `.claude/rules/codex-review-gate.md`.

---

## Specification-Derived Verification (Test Mapping)

Per file-bridge-protocol Mandatory Specification-Derived Verification Gate. Tests below derive from `SPEC-INTAKE-2485e9` plus Codex non-blocking conditions plus REVISED-1 F1/F2/F3 fixes.

| Spec clause / Codex condition / NO-GO finding | Test |
|-----------------------------------------------|------|
| SPEC-INTAKE-2485e9: surface spec events in owner chat view | `test_surfacer_emits_chat_visible_event_for_new_spec` (in `groundtruth-kb/tests/test_spec_event_surfacer.py`). Run via `pytest groundtruth-kb/tests/test_spec_event_surfacer.py -v`. |
| Codex condition: per-session ledger plus idempotency | `test_surfacer_does_not_duplicate_event_on_repeated_invocation`. Run via `pytest`. |
| Codex condition: per-session start timestamp source | `test_surfacer_uses_session_start_json_when_present` plus `test_surfacer_uses_conservative_fallback_when_session_start_missing` (NOT current_time per F2 fix). Run via `pytest`. |
| Codex condition: ledger location | `test_ledger_is_written_to_session_dir`. Run via `pytest`. |
| Codex condition: duplicate-suppression behavior | `test_concurrent_invocations_do_not_double_emit`. Run via `pytest`. |
| F1 fix: managed-artifacts.toml hook entry parses | `test_managed_registry_includes_spec_event_surfacer_hook` (extends `groundtruth-kb/tests/test_managed_registry.py`). Run via `pytest groundtruth-kb/tests/test_managed_registry.py -v`. |
| F1 fix: managed-artifacts.toml settings-hook-registration parses (PostToolUse only; Stop dropped per F1 trade-off) | `test_managed_registry_includes_spec_event_surfacer_post_tool_use_registration`. Run via `pytest`. |
| F1 fix: 16-row matrix test (was 15; adding surfacer makes 16) | `test_settings_parity_exact_sixteen_row_matrix` (UPDATES the existing 15-row exact-count test at `test_managed_registry.py:383`). Run via `pytest`. |
| F1 fix: scaffold output includes the new registration | `test_scaffold_writes_spec_event_surfacer_registration_for_dual_agent_profile` (extends scaffold tests). Run via `pytest`. |
| F1 fix: upgrade structured-merge preserves the new registration plus does not duplicate | `test_upgrade_structured_merge_adds_spec_event_surfacer_to_existing_settings`. Run via `pytest`. |
| F1 fix: doctor detects missing surfacer registration | `test_doctor_flags_missing_spec_event_surfacer_registration_when_required` — note: surfacer's `doctor_required_profiles` is empty in this slice (matching delib-search-tracker pattern); test validates that doctor PASSES when not required. A future hardening slice can elevate to required. Run via `pytest`. |
| F2 fix: session_self_initialization.py writes session-start.json | `test_session_self_initialization_writes_session_start_json` (extends `tests/scripts/test_session_self_initialization.py`). Run via `pytest tests/scripts/test_session_self_initialization.py -v`. |
| F2 fix: surfacer fallback is conservative (NOT current_time per Codex) | `test_surfacer_fallback_uses_now_minus_one_hour_when_session_start_missing`. The conservative bound prevents in-session writes from being silently suppressed. Run via `pytest`. |
| F3 fix: Codex parity test continues to pass after registry change | `test_codex_hook_parity_for_spec_event_surfacer` (extends `tests/scripts/test_codex_hook_parity.py`). Run via `pytest`. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs all of the above as part of the regression gate.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` (lo_review, S319) — substance basis for the umbrella.
- `bridge/gtkb-membase-effective-use-umbrella-001.md` (NEW; phantom -014; surviving scoping artifact).
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` (umbrella; approved at -002).
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-002.md` (Codex umbrella approval; six non-blocking conditions).
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-001.md` (this thread NEW; superseded by REVISED-1).
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-002.md` (Codex NO-GO; F1/F2/F3 directly addressed by REVISED-1).
- No prior deliberation reverses this approach.

---

## Change Log Vs -001

| Change | Driving finding | Section |
|--------|-----------------|---------|
| Stop event DROPPED from registration; only PostToolUse used. Coverage gap (KB writes from Stop hooks after last PostToolUse, missed until next turn) explicitly documented. | F1 (Stop not in `_VALID_SETTINGS_EVENTS`) | §1.1, §7 |
| Hook registration migrated to `groundtruth-kb/templates/managed-artifacts.toml` (two new entries: hook + settings-hook-registration). Invented files `templates/settings/post_tool_use.json` plus `hooks_registry.py` REMOVED from §Files Touched. | F1 | §1.2, §2 |
| Real session-start writer added to `scripts/session_self_initialization.py` as part of Slice A scope (small addition). Fallback rewritten: NOT current_time; uses conservative `now() - 1 hour` lower bound to avoid suppressing in-session writes. | F2 | §1.3 |
| Test mapping expanded with 6 new tests covering managed-artifact registry parsing, scaffold output, upgrade structured-merge, doctor behavior, session-start writer, conservative fallback. | F3 | §Test Mapping |
| Existing `test_settings_parity_exact_fifteen_row_matrix` UPDATED to 16-row form (adding surfacer makes 16). | F1 contract | §Test Mapping, §2 |

---

## 1. Implementation Design

### 1.1 Hook Events (per F1 fix: PostToolUse only)

The surfacer registers ONLY on `PostToolUse` (not Stop). Reasoning:

- `_VALID_SETTINGS_EVENTS = frozenset({"SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"})` per `managed_registry.py:86` — Stop is NOT a managed event.
- Adding Stop to the registry contract is significant scope expansion (would require changes to `_VALID_SETTINGS_EVENTS`, `SettingsEvent`, `SettingsHookRegistration` model, scaffold output, upgrade structured-merge for the new event, and 4+ tests proving the expansion). That belongs in a separate hardening slice.
- PostToolUse fires after every Bash/Write/Edit/etc tool call. Each fire scans for new KB rows since `session_started_at` not in the ledger. Most KB writes are tool-mediated (via Python invocations of `KnowledgeDB`), so PostToolUse coverage is the dominant case.
- **Coverage gap explicitly accepted:** KB writes that happen during a Stop hook (after the last PostToolUse and before turn end) are NOT surfaced this turn. They WILL be surfaced on the next turn's first PostToolUse (because `changed_at` of the missed row is still after the next turn's `session_started_at` — wait, no, on the next turn `session_started_at` advances, so a row written in the prior turn's Stop hook would be missed forever IF it predates the new session_started_at). Actually they will be missed permanently.
- This gap is acceptable for Slice A because: (a) currently NO Stop hooks write to KB (verified by repo-search at proposal time); (b) if a Stop hook starts writing to KB, a follow-on hardening slice can add Stop to the registry contract. This is a known limitation, not a silent bug.

### 1.2 Hook Registration Files (per F1 fix: managed-artifacts.toml)

**Two new entries in `groundtruth-kb/templates/managed-artifacts.toml`:**

Entry 1 — the hook file (modeled on `hook.delib-search-tracker` at lines 136-145):
```toml
[[artifacts]]
class = "hook"
id = "hook.spec-event-surfacer"
template_path = "hooks/spec-event-surfacer.py"
target_path = ".claude/hooks/spec-event-surfacer.py"
initial_profiles = ["dual-agent", "dual-agent-webapp"]
managed_profiles = []
doctor_required_profiles = []
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
```

Entry 2 — the settings-hook-registration (modeled on `settings.hook.delib-search-tracker.posttooluse` at lines 522-532):
```toml
[[artifacts]]
class = "settings-hook-registration"
id = "settings.hook.spec-event-surfacer.posttooluse"
event = "PostToolUse"
hook_filename = "spec-event-surfacer.py"
target_settings_path = ".claude/settings.json"
initial_profiles = ["dual-agent", "dual-agent-webapp"]
managed_profiles = ["dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []
ownership = "gt-kb-managed"
upgrade_policy = "structured-merge"
adopter_divergence_policy = "warn"
```

Both entries follow the same pattern as the existing `delib-search-tracker` PostToolUse registration (the closest functional analog: also a PostToolUse hook that scans KB activity).

**`.codex/hooks.json` matching intent** (per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`):
- Entry mirrors the `.claude/settings.json` PostToolUse registration.
- Currently disabled on Windows per ADR; intent preserved for non-Windows Codex.
- Verified via `tests/scripts/test_codex_hook_parity.py` extension.

### 1.3 Per-Session Start Timestamp Source (per F2 fix: real source plus conservative fallback)

**Slice A adds a writer** to `scripts/session_self_initialization.py`. Specifically, in the existing function that runs at SessionStart, add a write of:

```json
{
  "session_started_at": "2026-04-29T17:30:00.000000+00:00",
  "session_id": "<computed per existing convention>",
  "harness": "claude"
}
```

to `.claude/session/session-start.json` using the same atomic-rename pattern as other GT-KB hook outputs.

This is a small addition (estimated 10-20 lines) consistent with the existing function's structure.

**Surfacer reads** `.claude/session/session-start.json` for the lower-bound timestamp.

**Fallback (per F2 fix; NOT current_time):**

If `.claude/session/session-start.json` is missing, malformed, or unparseable, the surfacer uses a **conservative lower bound** computed as: `datetime.now(UTC) - timedelta(hours=1)`. This prevents the failure mode Codex flagged (where current_time would suppress already-created in-session writes).

The 1-hour window is large enough to cover any reasonable session lifetime and small enough to bound the lookback if the surfacer runs on a stale/persistent shell. The fallback also writes a one-line warning to stderr ("[KB-SPEC-EVENT] WARN: session-start.json missing; using conservative 1-hour lookback") so the degradation is owner-visible.

**Why not reuse Codex `last-session-start.json`?** That file lives at `.codex/gtkb-hooks/out/last-session-start.json` (Codex-side state). Cross-harness file sharing for state-of-truth would create coupling and per-harness divergence. Cleaner: each harness writes its own `session-start.json` to its own `.claude/session/` (Claude) or `.codex/gtkb-hooks/out/` (Codex). Surfacer reads whichever is appropriate for the running harness.

### 1.4 Ledger Location (unchanged from -001)

Path: `.claude/session/spec-events-seen.jsonl`. Format: JSONL with `spec_id`, `version`, `seen_at`, `kind` fields. Atomic-rename writes.

The ledger is initialized lazily by the surfacer itself on first invocation if absent (rather than depending on SessionStart to create it; per F2 fix's conservative-design principle).

### 1.5 Detection Query (mostly unchanged from -001)

```sql
SELECT id, version, title, type, status, section, changed_at
FROM current_specifications
WHERE changed_at >= :session_started_at
ORDER BY changed_at;
```

Plus Python-side filter against ledger contents loaded as `set[tuple[str, int]]`. Per Codex non-blocking note: `idx_specs_changed_at` index makes this query efficient.

### 1.6 Emission Format (unchanged from -001)

```
[KB-SPEC-EVENT] <spec_id> v<version> -- <kind> -- <title> [type=<type> status=<status> section=<section>]
```

### 1.7 Duplicate-Suppression Behavior (unchanged from -001)

Three layers: per-session ledger (primary) plus atomic ledger writes plus read-before-emit.

---

## 2. Files Touched (REVISED per F1, F2, F3)

**Upstream (`groundtruth-kb/`):**
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (NEW; ~150 lines).
- `groundtruth-kb/templates/managed-artifacts.toml` (MODIFIED; add 2 new `[[artifacts]]` blocks per §1.2; updates header comment to reflect 53 records = 20 hooks + 10 rules + 6 skills + 16 settings-hook-registrations + 1 gitignore-pattern).
- `groundtruth-kb/tests/test_spec_event_surfacer.py` (NEW; ~250 lines covering all derivation tests for the hook itself).
- `groundtruth-kb/tests/test_managed_registry.py` (MODIFIED; UPDATE existing `test_settings_parity_exact_fifteen_row_matrix` at line 383 to expect 16; ADD `test_managed_registry_includes_spec_event_surfacer_hook` and `_post_tool_use_registration`).
- `groundtruth-kb/tests/test_project_scaffold.py` (MODIFIED; ADD `test_scaffold_writes_spec_event_surfacer_registration_for_dual_agent_profile` if not already covered by parametrized tests).
- `groundtruth-kb/tests/test_project_upgrade.py` (MODIFIED; ADD `test_upgrade_structured_merge_adds_spec_event_surfacer_to_existing_settings`).
- `groundtruth-kb/tests/test_project_doctor.py` (MODIFIED; ADD `test_doctor_flags_missing_spec_event_surfacer_registration_when_required` — note this slice keeps `doctor_required_profiles=[]` so the test validates doctor passes when not required).
- `groundtruth-kb/docs/reference/hooks.md` (MODIFIED; document the new managed hook).

**Live (Agent Red consumer; via `gt project upgrade` after upstream VERIFIED):**
- `.claude/hooks/spec-event-surfacer.py` (NEW; identical to upstream template).
- `.claude/settings.json` (MODIFIED; add 1 PostToolUse hook registration per §1.2).
- `.codex/hooks.json` (MODIFIED; add matching intent per ADR-CODEX-HOOK-PARITY-FALLBACK-001).

**Live (session-start writer; F2 fix):**
- `scripts/session_self_initialization.py` (MODIFIED; add session-start.json writer per §1.3).
- `tests/scripts/test_session_self_initialization.py` (MODIFIED; add `test_session_self_initialization_writes_session_start_json`).

**Tests (Agent Red side):**
- `tests/hooks/test_spec_event_surfacer_integration.py` (NEW; integration tests against live `groundtruth.db` schema).
- `tests/scripts/test_codex_hook_parity.py` (MODIFIED; ensure parity test handles new registration).

**Other:**
- `scripts/release_candidate_gate.py` (MODIFIED; wire the new tests into the gate).
- `memory/work_list.md` (MODIFIED on VERIFIED; mark Slice A done).

**REMOVED from -001 §Files Touched (per F1 fix; these files don't exist in the real codebase):**
- `groundtruth-kb/templates/settings/post_tool_use.json` — invented file; managed-artifacts.toml is the real source.
- `groundtruth-kb/src/groundtruth_kb/hooks_registry.py` — invented file; managed_registry.py is the real loader.

---

## 3. Verification Plan

### 3.1 Tests

All 14 test cases from §Specification-Derived Verification table must pass. Run via:

```bash
# Upstream (managed-registry / scaffold / upgrade / doctor coverage per F3 fix)
pytest groundtruth-kb/tests/test_spec_event_surfacer.py -v
pytest groundtruth-kb/tests/test_managed_registry.py -v
pytest groundtruth-kb/tests/test_project_scaffold.py -v
pytest groundtruth-kb/tests/test_project_upgrade.py -v
pytest groundtruth-kb/tests/test_project_doctor.py -v

# Adopter-side (live registration + session-start writer per F2 fix)
pytest tests/scripts/test_session_self_initialization.py -v
pytest tests/scripts/test_codex_hook_parity.py -v
pytest tests/hooks/test_spec_event_surfacer_integration.py -v

# Release-gate inclusion
python scripts/release_candidate_gate.py --skip-frontend
```

### 3.2 Manual Verification (per Codex chat-visibility condition)

1. Insert a test spec via `python -c "from groundtruth_kb import KnowledgeDB; KnowledgeDB().insert_spec(...)"`.
2. Wait for next PostToolUse event.
3. Confirm the systemMessage `[KB-SPEC-EVENT] ...` appears in chat stream.

### 3.3 Non-Regression

- Existing 15-row registration matrix test UPDATED to 16-row (single line change); no other registrations affected.
- Existing classifier behavior (`spec-classifier.py`) unchanged in this slice (Slice B will modify it).
- Existing `delib-search-tracker.py` and `owner-decision-capture.py` PostToolUse registrations unchanged.

---

## 4. Acceptance Criteria

1. Functional: all 14 test cases from Specification-Derived Verification table pass.
2. Chat visibility: manual verification per §3.2 confirms systemMessage appears.
3. Idempotency: per-session ledger prevents duplicate emission across PostToolUse invocations.
4. Conservative fallback (per F2 fix): missing session-start.json triggers `now() - 1 hour` lookback plus stderr warning; in-session writes NEVER silently suppressed.
5. Managed-artifact contract (per F1 fix): new entries in `managed-artifacts.toml` parse correctly; 16-row exact-count test passes; scaffold/upgrade/doctor tests pass.
6. F2 writer: `scripts/session_self_initialization.py` writes `.claude/session/session-start.json` at SessionStart with `session_started_at` field.
7. KB write isolation: surfacer NEVER writes to `groundtruth.db`; zero `INSERT`/`UPDATE`/`DELETE` SQL.
8. Performance: detection query uses `idx_specs_changed_at`; surfacer runtime under 200ms per invocation.
9. Stop coverage gap is documented (per F1 trade-off): Slice A surfacer does NOT cover Stop-hook KB writes; future hardening slice may add Stop registration if a Stop hook starts writing to KB.

---

## 5. Sequencing and Concurrency

Internal: single coherent slice.

External: as -001 (first of four umbrella slices; Slice B depends on Slice A VERIFIED; WI-harvest track parallel).

Concurrency: atomic ledger writes plus read-before-emit (unchanged from -001).

---

## 6. Project Root Boundary

All artifacts under `E:\GT-KB`. Upstream changes route to `E:\GT-KB\groundtruth-kb\` (in-root).

---

## 7. Out of Scope (REVISED per F1 trade-off)

- Stop event registration (per F1 fix: dropped to avoid registry-contract expansion; future hardening slice if owner wants).
- Slice B auto-capture (separate bridge after Slice A VERIFIED).
- Ledger archival at end-of-session.
- Cross-session visibility.
- UI dashboard integration.
- Spec-event filtering.
- Schema-migration adaptation (handled when spec-lifecycle Slice 6 lands).

---

## 8. Rollback Plan (mostly unchanged from -001; explicit per F1)

1. Remove the 2 new entries from `groundtruth-kb/templates/managed-artifacts.toml`.
2. Remove the registration from `.claude/settings.json` and `.codex/hooks.json`.
3. Helper code at `.claude/hooks/spec-event-surfacer.py` and `groundtruth-kb/templates/hooks/spec-event-surfacer.py` left in place (audit trail).
4. The session-start.json writer in `scripts/session_self_initialization.py` may be left in place (harmless; could be useful for future hooks) or reverted.
5. Ledger file at `.claude/session/spec-events-seen.jsonl` may be left or removed; no KB or DA state affected.
6. Slice A makes ZERO writes to `groundtruth.db` and ZERO writes to the Deliberation Archive; rollback has no risk of state corruption.

---

## 9. Open Questions for Loyal Opposition Review

1. Stop coverage acceptable for Slice A per §1.1 trade-off, OR should this slice include the registry expansion to add Stop?
2. Conservative fallback bound: §1.3 uses `now() - 1 hour`. Codex preference for shorter (e.g., 30 minutes) or longer (e.g., 4 hours)?
3. `doctor_required_profiles=[]` for the surfacer matches `delib-search-tracker.py`. Should it be elevated to required for `dual-agent` profiles?
4. Function-level or module-level docstring discovery for the surfacer's own derived tests (only relevant if VERIFIED runner from sister bridge lands first; conservative is module-level)?
5. Session-start writer added to `scripts/session_self_initialization.py` — is this in Slice A scope or should it be a separate prerequisite slice?

---

## 10. Aligns With

- SPEC-INTAKE-2485e9.
- Umbrella `gtkb-membase-effective-use-recovery-2026-04-29-001` approved at -002.
- Real codebase: `managed-artifacts.toml` (single source of truth) + `managed_registry.py:86` (`_VALID_SETTINGS_EVENTS`) + `test_managed_registry.py:383` (15-row matrix).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
