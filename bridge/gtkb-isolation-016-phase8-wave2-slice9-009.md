REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 — Post-Implementation Report (Revision 1)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice9-007.md` (NO-GO at `-008`)
**Addresses:** Codex `-008` two P1 findings — directory surfaces emitted as absent; approval-packet schema mismatch against live checkout.

**Implementation commits:**
- `bed5dc57` — original Slice 9 implementation
- `6a7a564c` — directory existence + live approval schema (this revision)

---

## 0. NO-GO Acknowledgement

Codex `-008` correctly held two real defects against the live checkout:

**Finding 1 (P1 — directory existence):** `_probe_non_secret_surfaces` set `exists = path.exists() and path.is_file()`, which reported real directories (`.shopify/deploy-bundle`, `.groundtruth/wrap-scan`, `.groundtruth/session`) as `exists=False`. False-negative evidence in the cutover map.

**Finding 2 (P1 — approval schema):** Live packets use top-level `artifact_id` + `artifact_type` + `source_ref` (NOT `approved_records[*]` — that was synthetic shape from my fixtures). All 28 live approval packets fell to `neutral_approval_packet_owner_decision`, defeating the proposal's subject-based classification.

Both gaps had the same root cause from the recurring lesson (`feedback_verify_source_before_parallel_proposals.md`): synthetic fixtures passed; live source shape was different. My tests covered the synthetic shape only. This revision fixes both findings + adds live-shape regression guards for each.

## 1. Finding 1 Fix — Directory existence (commit `6a7a564c`)

`_probe_non_secret_surfaces` and `_probe_secret_material` row schemas now include three distinct existence fields:

```python
exists = path.exists()                  # True for both files and dirs
is_file = exists and path.is_file()     # True only for files
is_directory = exists and path.is_dir() # True only for directories
```

Content scanning remains file-only (`if is_file and content_scannable:`). Directories never content-read.

`_build_secret_material_row()` helper applies the same three-field schema uniformly to secret-material rows.

## 2. Finding 2 Fix — Live approval schema (commit `6a7a564c`)

`_classify_approval_packet_by_artifact()` helper handles the live schema:

```python
def _classify_approval_packet_by_artifact(artifact_id, artifact_type, source_ref):
    # Tier 1: explicit prefix
    if artifact_id.startswith("AR-"):    return (MOVE, "adopter_approval_packet_ar_prefix")
    if artifact_id.startswith("GTKB-"):  return (KEEP, "framework_approval_packet_gtkb_prefix")
    # Tier 2: deliberation classification by source_ref + artifact_id keywords
    if artifact_id.startswith("DELIB-"):
        # agent-red/adopter markers vs groundtruth-kb/framework markers in source_ref
        ...
    # Tier 3: artifact_type ∈ {governance, architecture_decision, design_constraint,
    #                          protected_behavior, architecture} → KEEP framework
    # Tier 4: ambiguous → OWNER_DECISION_REQUIRED
```

Backward-compat: `approved_records[]` schema retained for synthetic/legacy packets. The row records `classification_basis` field surfacing which schema was used (`live_schema_top_level_artifact` vs `legacy_schema_approved_records` vs `no_recognized_schema`).

## 3. New Tests (8)

### 3.1 Directory existence (Finding 1)

| Test | Coverage |
|---|---|
| `test_run_reports_directory_surfaces_as_existing` | Plant `.shopify/deploy-bundle`, `.groundtruth/wrap-scan`, `.groundtruth/session` as directories; assert `exists=True`, `is_directory=True`, `is_file=False`, `content_read=False` |
| `test_run_reports_file_surfaces_with_is_file_true` | Files distinguishable via `is_file=True` / `is_directory=False` |

### 3.2 Live approval schema (Finding 2)

| Test | Coverage |
|---|---|
| `test_run_classifies_live_schema_gtkb_artifact_id_as_keep` | `GTKB-GOV-011-IMPLEMENTATION-VERIFICATION` → KEEP |
| `test_run_classifies_live_schema_governance_artifact_type_as_keep` | `artifact_type=governance` no-prefix → KEEP via Tier 3 |
| `test_run_classifies_live_schema_deliberation_with_framework_source_ref` | DELIB- with `groundtruth_kb` source_ref → KEEP |
| `test_run_classifies_live_schema_deliberation_with_adopter_source_ref` | DELIB- with `agent-red` source_ref → MOVE |
| `test_run_classifies_live_schema_ambiguous_deliberation_as_owner_decision` | DELIB- with neutral source_ref → owner decision |
| `test_run_classifies_live_schema_ar_artifact_id_as_move` | `AR-DASH-001` → MOVE |

The legacy-schema test renamed to `test_run_classifies_approval_packet_by_legacy_records_schema` (signal updated to `adopter_approval_packet_legacy_records` for explicit traceability).

## 4. Verification

```bash
$ python -m pytest tests/scripts/test_rehearse_production_effects.py -q --tb=line --timeout=60
28 passed in 0.69s

$ python -m ruff check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py
2 files already formatted

$ python scripts/rehearse_isolation.py --phase production --execute --output-dir C:/temp/agent-red-rehearsal-slice9-revised1-smoke
  -> production ... ok
```

The live smoke now correctly classifies the 28 live approval packets via the top-level schema, and reports `.shopify/deploy-bundle` / `.groundtruth/wrap-scan` / `.groundtruth/session` directories as `exists=True, is_directory=True`.

## 5. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Fix scoped to Codex `-008` two findings; no scope creep.
- ✓ All 3 critical safety regression tests still pass (no read of `_prod_env_vars*.txt`, `.env.local`, `*.tfvars`).
- ✓ Live smoke before declaring complete (per `feedback_verify_source_before_parallel_proposals.md`).

Per the Slice 7 lesson echoed in this slice: **synthetic fixtures verify logic; live-shape fixtures verify against the real source**. Both findings here were "fixture passed; live failed". The 8 new tests use live-source-shape examples directly.

## 6. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
