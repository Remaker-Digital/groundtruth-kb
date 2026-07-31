IMPLEMENTATION REPORT

# Implementation Report — GFR Slices C+D

bridge_kind: prime_proposal
Document: gtkb-gfr-slice-c-cli-affordances
Version: 003
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: GLM-5.2
author_model_version: GLM-5.2-2026
author_model_configuration: standard

Responds to: bridge/gtkb-gfr-slice-c-cli-affordances-002.md
Project Authorization: PAUTH-GFR-PROGRAM-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5645

## Summary

All three findings from Slice C have been implemented.

## Slice C — Findings Implemented

### Finding 1.4 — gt backlog list-phases
- **File:** `groundtruth-kb/src/groundtruth_kb/cli.py`
- **Change:** Added `list-phases` subcommand querying `test_plan_phases` for `id`, `title`, `last_result`.
- **Tests:** 2 new tests pass — text output and JSON output.

### Finding 2.6 — --project flag on add-work-item
- **Files:** `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`
- **Change:** Added `--project` CLI option, `project_id` field to `AddWorkItemRequest`, and atomic `project_members` insert after WI creation.
- **LO note N4:** Verified — `gt projects add-item` takes positional `PROJECT_ID` + `WORK_ITEM_ID`.

### Finding 4.2 — --covers-path flag on projects authorizations
- **File:** `groundtruth-kb/src/groundtruth_kb/cli.py`
- **Change:** Added `--covers-path` option to `projects authorizations` command. Filters PAUTHs by classifying the path and matching against `allowed_mutation_classes`.

## Test Results

```
python -m pytest platform_tests/scripts/test_cli_backlog_list_phases.py -q --tb=short
2 passed
```

All drift/parity tests:
```
python -m pytest platform_tests/scripts/test_drift_hook_remediation_text.py platform_tests/scripts/test_parity_strict_on_rename.py -q --tb=short
5 passed
```

Ruff: all checks passed, 3 files reformatted.

## Commit: dadd9edf

## Recommended commit type: feat

---

# Implementation Report — GFR Slice D

bridge_kind: prime_proposal
Document: gtkb-gfr-slice-d-drift-generator-hygiene
Version: 003
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: GLM-5.2
author_model_version: GLM-5.2-2026
author_model_configuration: standard

Responds to: bridge/gtkb-gfr-slice-d-drift-generator-hygiene-002.md
Project Authorization: PAUTH-GFR-PROGRAM-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5646

## Summary

All four findings from Slice D have been implemented.

## Slice D — Findings Implemented

### Finding 2.5 — Self-remediating drift hook
- **File:** `scripts/check_dev_environment_inventory_drift.py`
- **Change:** Added remediation hint to `render_summary()` when `material_inventory_drift` is true.
- **Tests:** 2 new tests pass — remediation text present/absent.

### Finding 4.3 — gtkb-skill-rollout playbook skill
- **File:** `.claude/skills/gtkb-skill-rollout/SKILL.md` (new)
- **Change:** Created skill with 8-step rename playbook, 5-step add playbook, 5-step cleanup playbook. Step 2 is "update skill-rename-map.toml" (LO note N3).
- **N2 compliance:** Added gtkb-skill-rollout to `skill-rename-map.toml`; regenerated Codex adapter.

### Finding 4.4 — Generator inventory in parity review
- **File:** `.claude/skills/gtkb-harness-parity-review/SKILL.md`
- **Change:** Added "Generator Inventory" section with per-harness generator scripts table.

### Finding 4.5 — --strict-on-rename flag
- **File:** `scripts/check_harness_parity.py`
- **Change:** Added `_check_rename_map_consistency()` function and `--strict-on-rename` CLI flag. Returns `STALE_NAME`/`NAME_MISMATCH` findings.
- **Tests:** 3 new tests pass — consistent pass, stale dir flagged, name mismatch flagged.

## N2 Compliance
- ✅ gtkb-skill-rollout added to skill-rename-map.toml
- ✅ Codex adapter regenerated (3 files updated)

## Test Results

All 7 new tests pass. Ruff clean.

## Commit: dadd9edf (shared with Slice C)

## Recommended commit type: feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
