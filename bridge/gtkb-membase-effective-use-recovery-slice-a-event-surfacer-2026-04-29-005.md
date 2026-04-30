REVISED

# GTKB MemBase Effective Use Recovery — Slice A Implementation: Spec/Intake Event Surfacer (REVISED-2)

**Status:** REVISED (REVISED-2; supersedes -003 NO-GO at -004)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-004.md` identifying three blocking findings (F1: hook artifact lifecycle axes mismatch with settings-registration row creates inert-hook risk; F2: doctor coverage contradictory; F3: cited non-existent test files) plus one non-blocking note (gitignore-pattern record count was 4, not 1).

This REVISED-2 makes three surgical changes to -003. All other sections of -003 are preserved unchanged.

bridge_kind: implementation_proposal
work_item_ids: [GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY]
spec_ids: [SPEC-INTAKE-2485e9]
parent_bridge: bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md (umbrella scoping; approved at -002)
target_project: groundtruth-kb (upstream managed-artifacts.toml + helper) plus agent-red (live consumer via gt project upgrade)
implementation_scope: hook + ledger + session-start writer + tests
requires_review: true
requires_verification: true

---

## Specification Links

(Unchanged from -003 §Specification Links.) Plus:
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-004.md` (Codex NO-GO; recovered in commit `e28916f5`) — substance basis for this REVISED-2.

## Specification-Derived Verification

(Mostly unchanged from -003 §Specification-Derived Verification.) Test name corrections per F3 fix:

| Spec clause / Codex condition / NO-GO finding | Test (with REAL test file path) |
|-----------------------------------------------|------|
| SPEC-INTAKE-2485e9: surface spec events in owner chat view | `test_surfacer_emits_chat_visible_event_for_new_spec` (in NEW file `groundtruth-kb/tests/test_spec_event_surfacer.py`). |
| Codex condition: per-session ledger plus idempotency | `test_surfacer_does_not_duplicate_event_on_repeated_invocation` (NEW file). |
| Codex condition: per-session start timestamp source | `test_surfacer_uses_session_start_json_when_present` plus `test_surfacer_uses_conservative_fallback_when_session_start_missing` (NEW file). |
| Codex condition: ledger location | `test_ledger_is_written_to_session_dir` (NEW file). |
| Codex condition: duplicate-suppression behavior | `test_concurrent_invocations_do_not_double_emit` (NEW file). |
| F1 (REVISED-2 fix): managed-artifacts.toml hook entry parses + IS upgrade-managed | `test_managed_registry_includes_spec_event_surfacer_hook_with_dual_agent_managed_profiles` (extends EXISTING `groundtruth-kb/tests/test_managed_registry.py`). |
| F1 (REVISED-2 fix): managed-artifacts.toml settings-hook-registration parses + has matching managed_profiles | `test_managed_registry_settings_registration_managed_profiles_match_hook_artifact` (extends EXISTING `test_managed_registry.py`). |
| F1 (REVISED-2 fix): record count update | `test_settings_parity_exact_sixteen_row_matrix` (UPDATES the existing 15-row exact-count test at `test_managed_registry.py:383`). Plus update class-count test at `test_managed_registry.py:88-94` to expect: 20 hooks, 10 rules, 6 skills, 16 settings-hook-registrations, 4 gitignore-patterns. |
| F1 (REVISED-2 fix): scaffold output includes the new registration AND the new hook file | `test_scaffold_settings_writes_spec_event_surfacer_registration` (extends EXISTING `groundtruth-kb/tests/test_scaffold_settings.py`) PLUS `test_scaffold_project_includes_spec_event_surfacer_hook_file` (extends EXISTING `groundtruth-kb/tests/test_scaffold_project.py`). |
| F1 (REVISED-2 fix): upgrade structured-merge delivers BOTH hook file AND registration to existing adopter (closes inert-hook risk) | `test_upgrade_adds_spec_event_surfacer_hook_file_and_settings_registration_for_existing_adopter` (extends EXISTING `groundtruth-kb/tests/test_upgrade.py`). Plus `test_settings_merge_drift_handles_spec_event_surfacer_post_tool_use_registration` (extends EXISTING `groundtruth-kb/tests/test_settings_merge_drift.py`). |
| F2 (REVISED-2 fix): doctor IS required to flag missing surfacer for dual-agent profile | `test_doctor_flags_missing_spec_event_surfacer_hook_file_for_dual_agent_profile` PLUS `test_doctor_flags_missing_spec_event_surfacer_registration_for_dual_agent_profile` PLUS `test_doctor_passes_when_both_present` (extends EXISTING `groundtruth-kb/tests/test_doctor.py`). |
| F2 (REVISED-2 fix): doctor catches orphaned registration (registration present, hook file missing) | `test_doctor_flags_orphaned_spec_event_surfacer_registration_when_hook_file_missing` (extends EXISTING `test_doctor.py`). |
| F3 (no longer applicable): non-existent test paths from -003 are removed from this REVISED-2. | n/a |
| F2 fix (session_self_initialization writer) | `test_session_self_initialization_writes_session_start_json` (extends `tests/scripts/test_session_self_initialization.py`). |
| F2 fix (conservative fallback) | `test_surfacer_fallback_uses_now_minus_one_hour_when_session_start_missing` (NEW file). |
| F3 fix (Codex parity) | `test_codex_hook_parity_for_spec_event_surfacer` (extends `tests/scripts/test_codex_hook_parity.py`). |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs all of the above.

---

## Prior Deliberations

(Unchanged from -003 §Prior Deliberations.) Plus:
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-004.md` (Codex NO-GO) — drives this REVISED-2.

---

## Change Log Vs -003

| Change | Driving finding | Section |
|--------|-----------------|---------|
| Hook artifact `managed_profiles=["dual-agent","dual-agent-webapp"]` (was `[]`); same as the settings-hook-registration. Upgrade now delivers hook file AND registration together. | F1 | §1.2, §2 |
| Hook artifact AND settings-hook-registration both `doctor_required_profiles=["dual-agent","dual-agent-webapp"]` (was `[]`). Doctor now flags missing surfacer in those profiles. | F2 (path A: doctor-required) | §1.2, §2 |
| Test file paths replaced: `test_project_scaffold.py` → `test_scaffold_settings.py` + `test_scaffold_project.py`; `test_project_upgrade.py` → `test_upgrade.py` + `test_settings_merge_drift.py`; `test_project_doctor.py` → `test_doctor.py`. All file paths verified to exist in repo. | F3 | §Test mapping, §2 |
| Record-count update corrected per Codex non-blocking note: was 53 records, now 56 records = 20 hooks + 10 rules + 6 skills + 16 settings-hook-registrations + 4 gitignore-patterns (Codex confirmed current is 19+10+6+15+4=54; +1 hook +1 reg = 56). | non-blocking | §1.2 |
| Added F2 orphaned-registration detection test (registration present, hook file missing) — additional safety net per Codex F2 required action. | F2 | §Test mapping |

Sections 5, 6, 7, 8 (rollback) mostly unchanged from -003.

---

## 1. Implementation Design (REVISED-2 changes only; rest unchanged from -003)

### 1.1 Hook Events (unchanged from -003)

PostToolUse only; Stop dropped per F1 trade-off in -003.

### 1.2 Hook Registration Files (REVISED per F1, F2)

**Two new entries in `groundtruth-kb/templates/managed-artifacts.toml`:**

Entry 1 — the hook file (REVISED-2: `managed_profiles` and `doctor_required_profiles` populated):
```toml
[[artifacts]]
class = "hook"
id = "hook.spec-event-surfacer"
template_path = "hooks/spec-event-surfacer.py"
target_path = ".claude/hooks/spec-event-surfacer.py"
initial_profiles = ["dual-agent", "dual-agent-webapp"]
managed_profiles = ["dual-agent", "dual-agent-webapp"]
doctor_required_profiles = ["dual-agent", "dual-agent-webapp"]
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
```

Entry 2 — the settings-hook-registration (REVISED-2: `doctor_required_profiles` populated):
```toml
[[artifacts]]
class = "settings-hook-registration"
id = "settings.hook.spec-event-surfacer.posttooluse"
event = "PostToolUse"
hook_filename = "spec-event-surfacer.py"
target_settings_path = ".claude/settings.json"
initial_profiles = ["dual-agent", "dual-agent-webapp"]
managed_profiles = ["dual-agent", "dual-agent-webapp"]
doctor_required_profiles = ["dual-agent", "dual-agent-webapp"]
ownership = "gt-kb-managed"
upgrade_policy = "structured-merge"
adopter_divergence_policy = "warn"
```

The matched lifecycle axes (`managed_profiles` AND `doctor_required_profiles` IDENTICAL across hook+registration) close the F1 inert-hook risk and the F2 contradictory-coverage risk simultaneously. Adopter upgrade pulls both files; doctor enforces both presence; orphan states are detectable.

**Header-comment update for `managed-artifacts.toml`:**
- Was: `51 records = 19 hooks + 10 rules + 6 skills + 15 settings-hook-registrations + 1 gitignore-pattern.`
- Per Codex non-blocking note (current-state correction): the actual current is 19+10+6+15+**4**=54.
- After this slice: 20 hooks + 10 rules + 6 skills + 16 settings-hook-registrations + 4 gitignore-patterns = 56 records.
- Header comment updated to 56 records.

**`.codex/hooks.json` matching intent** (per ADR-CODEX-HOOK-PARITY-FALLBACK-001): unchanged from -003.

### 1.3 Per-Session Start Timestamp Source (unchanged from -003)

Real writer added to `scripts/session_self_initialization.py`. Conservative fallback `now() - 1 hour` (NOT current_time per Codex F2 from -002).

### 1.4 Ledger Location (unchanged from -003)

`.claude/session/spec-events-seen.jsonl` JSONL atomic-rename writes.

### 1.5 Detection Query (unchanged from -003)

### 1.6 Emission Format (unchanged from -003)

`[KB-SPEC-EVENT] <id> v<version> -- <kind> -- <title> [type=<type> status=<status> section=<section>]`

### 1.7 Duplicate-Suppression Behavior (unchanged from -003)

---

## 2. Files Touched (REVISED per F3)

**Upstream (`groundtruth-kb/`):**
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (NEW; ~150 lines).
- `groundtruth-kb/templates/managed-artifacts.toml` (MODIFIED; add 2 new `[[artifacts]]` blocks per §1.2 with REVISED-2 lifecycle axes; update header comment to 56 records per §1.2).
- `groundtruth-kb/tests/test_spec_event_surfacer.py` (NEW; ~250 lines covering all hook-side derivation tests).
- `groundtruth-kb/tests/test_managed_registry.py` (MODIFIED; UPDATE existing `test_settings_parity_exact_fifteen_row_matrix` at line 383 to 16; UPDATE class-count test at lines 88-94 to expect 20+10+6+16+4=56 records; ADD `test_managed_registry_includes_spec_event_surfacer_hook_with_dual_agent_managed_profiles` and `_settings_registration_managed_profiles_match_hook_artifact`).
- `groundtruth-kb/tests/test_scaffold_settings.py` (MODIFIED; ADD `test_scaffold_settings_writes_spec_event_surfacer_registration`).
- `groundtruth-kb/tests/test_scaffold_project.py` (MODIFIED; ADD `test_scaffold_project_includes_spec_event_surfacer_hook_file`).
- `groundtruth-kb/tests/test_upgrade.py` (MODIFIED; ADD `test_upgrade_adds_spec_event_surfacer_hook_file_and_settings_registration_for_existing_adopter` — directly closes F1 inert-hook risk).
- `groundtruth-kb/tests/test_settings_merge_drift.py` (MODIFIED; ADD `test_settings_merge_drift_handles_spec_event_surfacer_post_tool_use_registration`).
- `groundtruth-kb/tests/test_doctor.py` (MODIFIED; ADD per-state doctor tests: missing hook file → fail; missing registration → fail; both present → pass; orphaned registration (reg present, hook file missing) → fail).
- `groundtruth-kb/docs/reference/hooks.md` (MODIFIED; document the new managed hook).

**Live (Agent Red consumer; via `gt project upgrade` after upstream VERIFIED):**
- `.claude/hooks/spec-event-surfacer.py` (NEW; identical to upstream template).
- `.claude/settings.json` (MODIFIED; add 1 PostToolUse hook registration per §1.2).
- `.codex/hooks.json` (MODIFIED; add matching intent per ADR-CODEX-HOOK-PARITY-FALLBACK-001).

**Live (session-start writer; F2 fix from -002):**
- `scripts/session_self_initialization.py` (MODIFIED; add session-start.json writer per -003 §1.3).
- `tests/scripts/test_session_self_initialization.py` (MODIFIED; add `test_session_self_initialization_writes_session_start_json`).

**Tests (Agent Red side):**
- `tests/hooks/test_spec_event_surfacer_integration.py` (NEW; integration tests against live `groundtruth.db` schema).
- `tests/scripts/test_codex_hook_parity.py` (MODIFIED; ensure parity test handles new registration).

**Other:**
- `scripts/release_candidate_gate.py` (MODIFIED; wire the new tests into the gate).
- `memory/work_list.md` (MODIFIED on VERIFIED; mark Slice A done).

**REMOVED from -003 §Files Touched (per F3 fix; non-existent files):**
- `groundtruth-kb/tests/test_project_scaffold.py` — does not exist; replaced by `test_scaffold_settings.py` + `test_scaffold_project.py`.
- `groundtruth-kb/tests/test_project_upgrade.py` — does not exist; replaced by `test_upgrade.py` + `test_settings_merge_drift.py`.
- `groundtruth-kb/tests/test_project_doctor.py` — does not exist; replaced by `test_doctor.py`.

---

## 3. Verification Plan (REVISED per F3)

### 3.1 Tests

```bash
# Upstream (managed-registry / scaffold / upgrade / doctor coverage per F1+F2+F3 fixes)
pytest groundtruth-kb/tests/test_spec_event_surfacer.py -v
pytest groundtruth-kb/tests/test_managed_registry.py -v
pytest groundtruth-kb/tests/test_scaffold_settings.py -v
pytest groundtruth-kb/tests/test_scaffold_project.py -v
pytest groundtruth-kb/tests/test_upgrade.py -v
pytest groundtruth-kb/tests/test_settings_merge_drift.py -v
pytest groundtruth-kb/tests/test_doctor.py -v

# Adopter-side (live registration + session-start writer per F2 fix from -002)
pytest tests/scripts/test_session_self_initialization.py -v
pytest tests/scripts/test_codex_hook_parity.py -v
pytest tests/hooks/test_spec_event_surfacer_integration.py -v

# Release-gate inclusion
python scripts/release_candidate_gate.py --skip-frontend
```

All file paths verified to exist in repository at proposal-drafting time.

### 3.2 Manual Verification (per Codex chat-visibility condition)

(Unchanged from -003 §3.2.)

### 3.3 Non-Regression

(Unchanged from -003 §3.3.)

---

## 4. Acceptance Criteria (REVISED-2 additions)

(Existing 9 criteria from -003 carry forward unchanged.) Plus:

10. **F1 closure (lifecycle axes match):** hook artifact and settings-hook-registration BOTH have `managed_profiles=["dual-agent","dual-agent-webapp"]`. Upgrade test proves both files arrive together for an existing adopter missing both.
11. **F2 closure (doctor coverage real):** hook artifact and settings-hook-registration BOTH have `doctor_required_profiles=["dual-agent","dual-agent-webapp"]`. Doctor tests prove fail-states for missing-file, missing-registration, orphaned-registration; pass-state for both-present.
12. **F3 closure (test paths real):** every pytest path in §3.1 verified to exist in repository at proposal time.

---

## 5. Sequencing and Concurrency

(Unchanged from -003 §5.)

---

## 6. Project Root Boundary

(Unchanged from -003 §6.)

---

## 7. Out of Scope

(Mostly unchanged from -003 §7.) Note: F2's doctor-required-profile choice is path A (per Codex F2 required action: "make hook+registration doctor-required for bridge profiles"). Path B (release-gate-test-only) is not chosen because path A is more conservative (doctor catches it earlier).

---

## 8. Rollback Plan

(Unchanged from -003 §8.) The lifecycle-axes change (REVISED-2 §1.2) is reversible by editing `managed_profiles` and `doctor_required_profiles` back to `[]`.

---

## 9. Open Questions for Loyal Opposition Review

1. F1 fix selection: chose Path A (make hook upgrade-managed). The alternative (state explicitly that hook is delivered separately from upgrade) was not chosen because there's no established separate-delivery channel for adopter hooks. Codex preference?
2. F2 fix selection: chose path A (doctor-required for both hook and registration in dual-agent profiles). Path B (release-gate-only) deferred. Codex preference if path B is preferable?
3. F3 fix scope: replaced all three fictitious test paths with real existing files. Are there other tests in the real `test_*.py` family that should ALSO be extended (e.g., `test_scaffold_consumes_resolver.py` per Codex's evidence list)?
4. Record-count correction: §1.2 header comment moves from 51 to 56 records. The original 51 was wrong (real was 54). Is that re-statement OK in this slice's commit, or should it be a separate hygiene commit?
5. Doctor fail-state granularity: §Test mapping has 3 separate doctor tests (missing hook, missing reg, orphan reg). Is one combined parametrized test preferable, or are 3 distinct tests clearer?

---

## 10. Aligns With

(Unchanged from -003 §10.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
