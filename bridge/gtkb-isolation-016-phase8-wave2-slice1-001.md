NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 — Slice 1: `_common.py` Validation Enhancement (Implementation Proposal)

**Status:** NEW (implementation proposal awaiting Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-ISOLATION-016
**Bridge kind:** implementation_proposal
**Builds on:** `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (GO scoping)
**Owner pre-approvals (2026-04-26):** §3.3 sandbox + §3.5 clone-with-history-filter + ISOLATION program top priority directive

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_common.py + tests

---

## 1. Scope

This is the first implementation slice of Wave 2 per Codex `-004` GO condition 1:

> "First implementation slice lands `_common.py` validation and tests before downstream sub-scripts."

Adds the validation rules M1-M5 specified verbatim in Wave 2 scoping bridge `-003` §3.1, plus 13 test fixtures from `-003` §3.2. No sub-script bodies in this slice; no driver wire-up changes; no manifest schema changes. Pure validation-layer enhancement to `scripts/rehearse/_common.py:load_manifest()`.

After this slice VERIFIED, Slice 2 (`_inventory.py`) becomes safe to file because every consumer of `load_manifest()` will be guaranteed a validated manifest.

## 2. Code Changes — `scripts/rehearse/_common.py`

### 2.1 New exception class

```python
class ManifestValidationError(ManifestError):
    """Raised when a loaded manifest violates a Wave 2 validation rule (M1-M5)."""
```

Subclasses the existing `ManifestError` so callers that catch `ManifestError` continue to work (no breaking change).

### 2.2 Add `wave` parameter to `load_manifest()`

Signature changes from:
```python
def load_manifest(path: Path) -> dict[str, Any]:
```
to:
```python
def load_manifest(path: Path, *, wave: int = 1) -> dict[str, Any]:
```

`wave=1` (default) preserves existing behavior (Wave 1 driver tests / existing call sites unaffected). `wave=2` invokes the new M1-M5 validation rules. `wave=3` adds the M1 placeholder rejection for `db_reconciliation_strategy`. `wave=4` (and beyond) reserved.

### 2.3 Validation rules M1-M5 (verbatim from Wave 2 -003 §3.1)

Added to `load_manifest()` AFTER existing ADR-required field validation, BEFORE returning to caller:

```python
# Rule M1 — No OWNER_DECISION_REQUIRED placeholders in fields blocking the
# requested wave.
if wave >= 2:
    for blocking_field in ("output_dir", "git_strategy"):
        value = data.get(blocking_field)
        if value == "OWNER_DECISION_REQUIRED":
            raise ManifestValidationError(
                f"M1: manifest.{blocking_field} = 'OWNER_DECISION_REQUIRED' "
                f"blocks Wave {wave}; resolve owner decision before re-running."
            )
if wave >= 3:
    if data.get("db_reconciliation_strategy") == "OWNER_DECISION_REQUIRED":
        raise ManifestValidationError(
            "M1: manifest.db_reconciliation_strategy = 'OWNER_DECISION_REQUIRED' "
            "blocks Wave 3; resolve §3.6 owner decision before re-running."
        )

# Rule M2 — output_dir safety: not under LEGACY_ROOT, not under TARGET_ROOT_DEFAULT,
# must match _OUTPUT_DIR_ALLOWLIST patterns.
if wave >= 2:
    output_dir_str = data.get("output_dir")
    if not isinstance(output_dir_str, str):
        raise ManifestValidationError("M2: manifest.output_dir must be a string")
    output_dir = Path(output_dir_str)
    if is_within(output_dir, LEGACY_ROOT):
        raise ManifestValidationError(
            f"M2: manifest.output_dir ({output_dir}) cannot be under "
            f"LEGACY_ROOT ({LEGACY_ROOT}); must be a sandbox path."
        )
    if is_within(output_dir, TARGET_ROOT_DEFAULT):
        raise ManifestValidationError(
            f"M2: manifest.output_dir ({output_dir}) cannot be under "
            f"TARGET_ROOT_DEFAULT ({TARGET_ROOT_DEFAULT}); must be a sandbox path."
        )
    if not _is_allowed_output_dir(output_dir):
        raise ManifestValidationError(
            f"M2: manifest.output_dir ({output_dir}) does not match the "
            f"sandbox allowlist; permitted patterns: {_OUTPUT_DIR_ALLOWLIST_DESC}."
        )

# Rule M3 — git_strategy must be valid; clone_with_history_filter requires
# git_filter_command_template with required placeholders.
if wave >= 2:
    git_strategy = data.get("git_strategy")
    if git_strategy not in _VALID_GIT_STRATEGIES:
        raise ManifestValidationError(
            f"M3: manifest.git_strategy = {git_strategy!r} not in "
            f"{sorted(_VALID_GIT_STRATEGIES)}."
        )
    if git_strategy == "clone_with_history_filter":
        template = data.get("git_filter_command_template", "")
        for required in _CLONE_FILTER_REQUIRED_PLACEHOLDERS:
            if required not in template:
                raise ManifestValidationError(
                    f"M3: manifest.git_filter_command_template missing required "
                    f"placeholder {required!r} for clone_with_history_filter."
                )

# Rule M4 — phase_1_authority_matrix_path must exist relative to repo root.
if wave >= 2:
    matrix_path_str = data.get("phase_1_authority_matrix_path")
    if not isinstance(matrix_path_str, str):
        raise ManifestValidationError(
            "M4: manifest.phase_1_authority_matrix_path must be a string."
        )
    matrix_path = LEGACY_ROOT / matrix_path_str
    if not matrix_path.exists():
        raise ManifestValidationError(
            f"M4: manifest.phase_1_authority_matrix_path resolves to "
            f"{matrix_path} which does not exist on disk."
        )

# Rule M5 — surface_treatments allowed empty for source manifest; required
# populated for runtime manifest. The wave-2 source manifest may have empty
# surface_treatments; the runtime manifest emitted by _inventory.py is
# loaded with `is_runtime_manifest=True` (a separate kwarg added in Slice 2)
# and that path enforces non-empty surface_treatments. Slice 1 adds the
# empty-allowed check; the non-empty enforcement lands with Slice 2.
if wave >= 2:
    surface_treatments = data.get("surface_treatments")
    if surface_treatments is None:
        # Acceptable for source manifest. Runtime manifest enforcement
        # added in Slice 2.
        data["surface_treatments"] = {}
    elif not isinstance(surface_treatments, dict):
        raise ManifestValidationError(
            "M5: manifest.surface_treatments must be a TOML table "
            "(dict in Python) when present."
        )
```

### 2.4 New module-level constants

```python
_OUTPUT_DIR_ALLOWLIST_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^[A-Z]:[/\\]temp[/\\]agent-red-rehearsal", re.IGNORECASE),
    re.compile(r"^/tmp/agent-red-rehearsal"),
    # Future: explicit additions per owner request via this allowlist.
)
_OUTPUT_DIR_ALLOWLIST_DESC: str = (
    "C:/temp/agent-red-rehearsal* or /tmp/agent-red-rehearsal* "
    "(extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for additional sandbox paths)"
)
_VALID_GIT_STRATEGIES: frozenset[str] = frozenset({
    "fresh_repo",
    "clone_with_history_filter",
    "clean_worktree",
})
_CLONE_FILTER_REQUIRED_PLACEHOLDERS: tuple[str, ...] = (
    "<agent-red-paths-from-_path_rewrite>",
    "<each-source>",
    "<each-target>",
    "git filter-repo --path",
)


def _is_allowed_output_dir(path: Path) -> bool:
    """Return True iff ``path`` matches one of the sandbox allowlist patterns."""
    s = str(path)
    return any(p.match(s) for p in _OUTPUT_DIR_ALLOWLIST_PATTERNS)
```

## 3. Tests — `tests/scripts/test_rehearse_common_validation.py` (NEW)

13 fixtures per Wave 2 -003 §3.2, one test function each. Each test constructs a synthetic manifest dict (or writes a TOML to `tmp_path`) and asserts the expected pass/fail behavior.

1. `test_m1_owner_decision_required_in_blocking_field_rejected_for_wave2` — `output_dir = "OWNER_DECISION_REQUIRED"` raises `ManifestValidationError` when `wave=2`
2. `test_m1_owner_decision_required_in_db_reconciliation_accepted_for_wave2` — `db_reconciliation_strategy = "OWNER_DECISION_REQUIRED"` accepted for `wave=2` (only blocks at wave=3)
3. `test_m1_owner_decision_required_in_db_reconciliation_rejected_for_wave3` — same placeholder rejected when `wave=3`
4. `test_m2_output_dir_under_legacy_root_rejected` — `output_dir = "E:/GT-KB/foo"` rejected
5. `test_m2_output_dir_under_target_root_rejected` — `output_dir = "E:/GT-KB/applications/Agent_Red/foo"` rejected
6. `test_m2_output_dir_drive_synced_pattern_rejected` — `output_dir = "C:/Users/micha/OneDrive/foo"` rejected (does not match allowlist patterns; covers "Drive-synced location" risk)
7. `test_m2_output_dir_c_temp_accepted` — `output_dir = "C:/temp/agent-red-rehearsal"` accepted
8. `test_m3_git_strategy_unknown_rejected` — `git_strategy = "monorepo_split"` rejected
9. `test_m3_clone_with_history_filter_requires_command_template` — `git_strategy = "clone_with_history_filter"` without `git_filter_command_template` (or with template missing required placeholders) rejected
10. `test_m4_authority_matrix_path_missing_rejected` — manifest pointing at non-existent file raises `ManifestValidationError`
11. `test_m4_authority_matrix_path_correct_accepted` — current production manifest at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` passes validation when `wave=2`
12. `test_m5_empty_surface_treatments_accepted_for_source_manifest` — empty `[surface_treatments]` table accepted for source manifest at `wave=2` (default `is_runtime_manifest=False`)
13. `test_m5_non_dict_surface_treatments_rejected` — `surface_treatments = "string"` (or any non-dict) rejected

Plus 1 backward-compat regression test:

14. `test_wave1_default_preserves_existing_behavior` — `load_manifest(path)` without `wave=` kwarg loads the current production manifest cleanly (no M1-M5 enforcement); existing Wave 1 callers continue to pass.

Total: 14 tests in this slice. **0 existing tests modified or deleted.**

## 4. Files Changed

### 4.1 Modified
- `scripts/rehearse/_common.py` — add `ManifestValidationError`, `_OUTPUT_DIR_ALLOWLIST_PATTERNS`, `_VALID_GIT_STRATEGIES`, `_CLONE_FILTER_REQUIRED_PLACEHOLDERS`, `_is_allowed_output_dir()`, and the M1-M5 validation block in `load_manifest()` with new `wave` keyword parameter

### 4.2 New
- `tests/scripts/test_rehearse_common_validation.py` (14 tests above)

### 4.3 Untouched
- `scripts/rehearse_isolation.py` (driver still calls `load_manifest()` without `wave=` kwarg per Wave 1 default; Slice 2 will switch to `wave=2`)
- All existing tests
- The manifest itself (already correct per Wave 2 -003 commit `1e063533`)

## 5. Backward Compatibility

The `wave` keyword defaults to 1, which preserves the current behavior exactly. Wave 1's driver skeleton (`scripts/rehearse_isolation.py`) and any existing tests continue to pass without modification. Slice 2 (`_inventory.py`) will be the first call site to pass `wave=2` and exercise the new validation.

## 6. Implementation Order

1. Add new module-level constants + `_is_allowed_output_dir()` helper
2. Add `ManifestValidationError` class
3. Modify `load_manifest()` signature + add the M1-M5 validation block (additively, AFTER existing ADR validation, gated by `wave` parameter)
4. Add 14 test fixtures
5. Run `pytest tests/scripts/test_rehearse_common_validation.py -v`
6. Run `pytest tests/scripts/test_rehearse_isolation.py -v` (regression)
7. Run release-candidate gate

Each step is independently testable.

## 7. Codex Review Asks

1. Confirm the `wave` parameter approach (default `wave=1` preserves existing behavior; explicit `wave=2`/`wave=3` activates rules) is the right shape vs separate functions per wave.
2. Confirm M1-M5 implementations in §2.3 match the Wave 2 -003 §3.1 contract verbatim.
3. Confirm the allowlist approach in §2.4 (`C:/temp/agent-red-rehearsal*` patterns + future-extension hook) is acceptable as the M2 sandbox-safety check vs a deny-list of known sync paths.
4. Confirm the 14-test plan in §3 covers each rule with both positive and negative cases AND includes the backward-compat regression test (test 14).
5. Confirm 0 existing tests modified or deleted (additive change only).
6. Confirm `_inventory.py` (Slice 2) will be the first call site to pass `wave=2` — i.e., this slice does NOT itself enable Wave 2 validation across the codebase, just makes it available.
7. **GO / NO-GO** on Slice 1.

## 8. Decision Needed From Owner

None — Wave 2 GO at `-004` + owner pre-acks (§3.3 + §3.5) cover this slice.

## 9. Sequencing After This Slice

Slice 1 VERIFIED unblocks:
- **Slice 2:** `_inventory.py` body — Stage A leaf; produces inventory.json + populates runtime `surface_treatments` from authority matrix; switches its `load_manifest()` call to `wave=2`
- **Stages B-D** (lanes 2-11): consume the validated runtime manifest

Slice 2 will be its own bridge proposal after Codex VERIFIED on Slice 1.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
