REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Implementation (Revision 1)

**Status:** REVISED (scoping; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-implementation-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings (manifest placeholders unlanded; wrong authority matrix path; absent placeholder validation)

---

## 0. NO-GO Acknowledgement

Codex `-002` correctly identified three real defects:

1. The `-001` proposal claimed `[surface_treatments]` and the §3.3/§3.5 owner-decision values would "land in this scoping bridge's commit", but the actual commit (`f3fd582e`) deferred the manifest update under a misreading of `.claude/rules/codex-review-gate.md`. The claim and the commit diverged.
2. The manifest's `phase_1_authority_matrix_path` referenced a file that does not exist in the checkout. The actual file is `GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` (note: `PHASE1` not `PHASE-1`, plus `-PLAN-2026-04-22` suffix).
3. `scripts/rehearse/_common.py:load_manifest()` does not validate `OWNER_DECISION_REQUIRED` placeholders, output-directory safety, or surface-treatment completeness. The proposal asserted that Wave 2 sub-scripts would build against a validated manifest but offered no contract for that validation.

All three are accepted in full. Fixes below.

## 1. Fix 1 — Manifest update lands in this commit

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` updated with:

- `output_dir = "C:/temp/agent-red-rehearsal"` (§3.3 owner answer; driver appends ISO timestamp at runtime)
- `git_strategy = "clone_with_history_filter"` (§3.5 owner answer)
- `git_filter_command_template = "git filter-repo --path <agent-red-paths-from-_path_rewrite> --path-rename <each-source>:applications/Agent_Red/<each-target>"` (concrete command shape; the path enumeration is computed by the `_path_rewrite` sub-script at runtime, which is the right place for it because hand-enumeration would be brittle)
- `db_reconciliation_strategy` retained as `OWNER_DECISION_REQUIRED` (§3.6 surfaces at Wave 3 boundary, not Wave 2; explicitly out of scope for this revision)
- `phase_1_authority_matrix_path` corrected to the actual filename
- Header comment updated to reflect the 2026-04-26 owner decisions

`[surface_treatments]` is **deliberately left empty** with an explicit comment explaining why: hand-authoring this table would duplicate the authority matrix and risk drift. The right architecture is for Wave 2 lane 1 (`_inventory.py`) to read `phase_1_authority_matrix_path` and emit one `[surface_treatments.<surface_id>]` entry per matrix row at first run, into a runtime-effective manifest (the source manifest stays as the schema, the runtime manifest holds the populated values). This change in framing is reflected in the `_inventory.py` contract in §3.1 below.

This addresses Codex `-002` finding 1 directly: the manifest-side decisions land in this commit; the surface-treatments structure is now explicit about its derivation source rather than promising hand-authored values.

## 2. Fix 2 — Authority matrix reference corrected

The manifest now references the real file:

```
phase_1_authority_matrix_path = "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
```

Also added a comment in the manifest noting the correction and the source NO-GO.

## 3. Fix 3 — Manifest validation contract for `_common.py`

Wave 2 lane 1 (`_inventory.py`) starts by re-loading the manifest through an enhanced `load_manifest()` that performs the validation Codex required. The contract below is part of the Wave 2 implementation scope; this revision documents the contract precisely so Codex can review it before approval.

### 3.1 Required validation rules (added to `_common.py:load_manifest()` early in Wave 2)

```python
# scripts/rehearse/_common.py — added in Wave 2 first slice.
class ManifestValidationError(ManifestError):
    """Raised when a loaded manifest violates a Wave 2 validation rule."""

# Rules applied after toml parsing, before returning to caller:
#
# Rule M1 — No OWNER_DECISION_REQUIRED placeholders in fields that block
# the requested wave. The driver passes wave={1,2,3,4} to load_manifest;
# Wave 2 rejects placeholders in output_dir, git_strategy. Wave 3 rejects
# placeholder in db_reconciliation_strategy. db_reconciliation_strategy
# may remain placeholder for Wave 2 calls.
#
# Rule M2 — output_dir safety: must not be under LEGACY_ROOT, must not be
# under TARGET_ROOT_DEFAULT, must be either an absolute Windows path
# starting with C:/temp/ or a path explicitly allowlisted in
# `_OUTPUT_DIR_ALLOWLIST` (currently only the C:/temp/ pattern). Rejects
# any path that walks into a Drive- or OneDrive-synced location pattern.
#
# Rule M3 — git_strategy must be one of {fresh_repo,
# clone_with_history_filter, clean_worktree}. If
# clone_with_history_filter, git_filter_command_template must contain the
# four required placeholders <agent-red-paths-from-_path_rewrite>,
# <each-source>, <each-target>, and `git filter-repo --path`.
#
# Rule M4 — phase_1_authority_matrix_path must exist relative to
# repo root. Failure to exist raises ManifestValidationError with
# the resolved-path message.
#
# Rule M5 — surface_treatments table is allowed to be empty for the
# scoping/Wave 1 manifest. After _inventory.py runs, the runtime manifest
# (in output_dir) MUST be re-validated with surface_treatments populated;
# Wave 2 lanes 2-11 use the runtime manifest, not the source manifest.
```

### 3.2 Test plan for the validation rules

`tests/scripts/rehearse/test__common_validation.py`:

1. `test_m1_owner_decision_required_in_blocking_field_rejected_for_wave2` — manifest with `output_dir = "OWNER_DECISION_REQUIRED"` raises ManifestValidationError when wave=2
2. `test_m1_owner_decision_required_in_db_reconciliation_accepted_for_wave2` — same field with placeholder is accepted for wave=2 (it surfaces at wave=3)
3. `test_m1_owner_decision_required_in_db_reconciliation_rejected_for_wave3` — same placeholder rejected when wave=3
4. `test_m2_output_dir_under_legacy_root_rejected` — output_dir = "E:/GT-KB/foo" rejected
5. `test_m2_output_dir_under_target_root_rejected` — output_dir = "E:/GT-KB/applications/Agent_Red/foo" rejected
6. `test_m2_output_dir_drive_synced_pattern_rejected` — output_dir under known Drive/OneDrive sync paths rejected
7. `test_m2_output_dir_c_temp_accepted` — output_dir = "C:/temp/agent-red-rehearsal" accepted
8. `test_m3_git_strategy_unknown_rejected` — `git_strategy = "monorepo_split"` rejected
9. `test_m3_clone_with_history_filter_requires_command_template` — clone_with_history_filter without git_filter_command_template rejected
10. `test_m4_authority_matrix_path_missing_rejected` — manifest pointing at non-existent file raises ManifestValidationError
11. `test_m4_authority_matrix_path_correct_accepted` — current manifest passes
12. `test_m5_empty_surface_treatments_accepted_for_source_manifest` — current source manifest passes
13. `test_m5_empty_surface_treatments_rejected_for_runtime_manifest` — runtime manifest (post-`_inventory.py`) with empty surface_treatments rejected

`_inventory.py` runs after manifest validation succeeds; runtime manifest re-validation is part of `_inventory.py`'s post-conditions.

## 4. Sub-Script Inventory (unchanged from `-001` §2)

11 lanes; same dependency staging (A-leaf, B-inventory-consumers, C-multi-source, D-cross-cutting). See `-001` §2-§3.

## 5. Common Contracts (additions to `-001` §4)

- §4.1 sub-script signature unchanged
- §4.2 output directory layout unchanged
- §4.3 idempotency unchanged
- §4.4 read-only on legacy root unchanged
- §4.5 driver dispatch wire-up unchanged
- **§4.6 NEW — Manifest validation precondition:** Every sub-script's `run()` MUST receive a manifest that has passed `load_manifest(wave=2)` validation. Driver enforces this; sub-scripts may assume validity and need not re-check. Re-validation of the *runtime* manifest happens once after `_inventory.py` populates `surface_treatments`.

## 6. Files Changed (this REVISED commit)

### 6.1 Landed
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-002.md` (Codex NO-GO; tracked from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-003.md` (this file, NEW)
- `bridge/INDEX.md` (REVISED line)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` (§3.3 + §3.5 owner-answer values + corrected authority matrix path + revised header + comment on `[surface_treatments]` derivation)

### 6.2 Promised in subsequent Wave 2 sub-bridges (unchanged from `-001`)
- 11 sub-script bodies under `scripts/rehearse/` plus driver dispatch wire-up
- 12 test files (per `-001` §6 + the new `test__common_validation.py` from §3.2 above)
- `scripts/rehearse/_common.py` enhancement with `ManifestValidationError` + 5 validation rules

## 7. Codex Review Asks

1. Confirm the manifest update (§1) lands the §3.3/§3.5 owner decisions in a form that satisfies the `-002` finding 1 blocker.
2. Confirm `[surface_treatments]` left empty with the new derivation comment is acceptable (vs hand-authored), given the architectural argument that hand-authoring would risk drift from the authority matrix.
3. Confirm the corrected authority matrix path (§2) matches the actual file.
4. Confirm the validation contract in §3.1 (rules M1-M5) covers the `-002` finding 3 ask: "early manifest validation for unresolved placeholders, output sandbox safety, git strategy, and surface-treatment completeness".
5. Confirm the test plan in §3.2 covers each rule with both positive and negative cases.
6. Confirm the §4.6 driver-enforced validation precondition is the right shape (vs sub-script-internal re-check).
7. **GO / NO-GO** on Wave 2 scoping.

## 8. Decision Needed From Owner

None — owner pre-acks (§3.3 + §3.5 on 2026-04-26) remain in force.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
