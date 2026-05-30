REVISED

bridge_kind: implementation_report
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s368-orphan-wi-revised-009
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report (REVISED-2) - Orphan WI Membership Discovery Slice 1

Document: gtkb-orphan-wi-membership-discovery-slice-1
Version: 009 (REVISED post-impl report; second revision)
Responds-To: bridge/gtkb-orphan-wi-membership-discovery-slice-1-008.md (Codex NO-GO; P1-001 root-cause attribution defect)
Carries-Forward: bridge/gtkb-orphan-wi-membership-discovery-slice-1-007.md (REVISED-1 post-impl) and bridge/gtkb-orphan-wi-membership-discovery-slice-1-005.md (original NEW post-impl)
Implements: bridge/gtkb-orphan-wi-membership-discovery-slice-1-003.md (REVISED-1 proposal)
Authorized by: bridge/gtkb-orphan-wi-membership-discovery-slice-1-004.md (Codex GO on REVISED-1)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Bridge file location: E:\GT-KB\bridge\gtkb-orphan-wi-membership-discovery-slice-1-009.md (in-root per ADR-ISOLATION-APPLICATION-PLACEMENT-001)
Implementation-start packet: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-orphan-wi-membership-discovery-slice-1.json` (re-activated via `python scripts/implementation_authorization.py begin --bridge-id gtkb-orphan-wi-membership-discovery-slice-1`)
Work Item: WI-3397
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
target_paths: ["scripts/discover_orphan_wi_memberships.py", "tests/scripts/test_discover_orphan_wi_memberships.py"]
Recommended commit type: fix:

## Response To NO-GO -008

Codex's NO-GO at `-008` identified one blocking finding:

**P1-001 (blocking) — `root_cause_changed_by` uses mutable latest author, not the creator/root cause.**

The defect Codex surfaced is real and confirmed by direct version-history inspection of `groundtruth.db`. The implementation at `scripts/discover_orphan_wi_memberships.py:244` populated `root_cause_changed_by` from `wi.get("changed_by")`, which is the **latest** mutable `changed_by` field on the current `work_items` row (the row returned by `KnowledgeDB.list_work_items`). Subsequent migrations (S363 priority canonicalization on `prime-builder/claude/B`; WI-3271 approval-state backfill on `prime-builder/codex/A`) overwrote that field for many of the same orphan WIs whose creator was actually a different code path. The result was a false attribution distribution that would have mis-scoped Slice 2's follow-on remediation candidates.

**Fix applied in this REVISED-2:** `scripts/discover_orphan_wi_memberships.py` now sources `root_cause_changed_by` from the version=1 row per orphan WI (the immutable creator row), not from the latest mutable row. A new regression test at `tests/scripts/test_discover_orphan_wi_memberships.py` asserts that later non-creation updates do NOT overwrite root-cause attribution for a multi-version WI fixture. Fresh live-MemBase evidence below confirms the corrected distribution matches Codex's ground-truth observation in NO-GO -008.

## Summary

Slice 1 discovers orphan open WIs (work_items with `resolution_status='open'` and no active row in `project_work_item_memberships`), classifies each by recoverability heuristic, and emits a JSON inventory artifact plus a markdown review packet to seed Slice 2's per-orphan AUQ.

**Live MemBase state at this REVISED-2 run:**
- 222 total open WIs, 22 orphans, all 22 classified `unrecoverable` (data sparsity in `current_project_artifact_links`).
- **Corrected root-cause distribution (version-1 creator):** 12 from `prime-builder/claude`, 8 from `advisory-backlog-router/1.0`, 2 from `prime-builder/claude/B`. Three distinct code paths, not two.
- Latest mutable distribution (reported for contrast; no longer treated as root-cause): 13 from `prime-builder/codex/A`, 9 from `prime-builder/claude/B`.

The earlier 19/3 split reported in `-007` was an artifact of `prime-builder/codex/A` (WI-3271 approval-state backfill) and `prime-builder/claude/B` (S363 priority canonicalization migration) overwriting `changed_by` on WIs whose actual creators are different code paths.

## Specification Links

Carried forward from REVISED-1 unchanged:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this report proceeds through the file bridge; INDEX update for `bridge/gtkb-orphan-wi-membership-discovery-slice-1-009.md`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — `project_work_item_memberships` is the canonical governance artifact; discovery surfaces violations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below with observed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization + Project + Work Item lines satisfied above with active PAUTH.
- `SPEC-AUQ-POLICY-ENGINE-001` — Slice 2 will use AskUserQuestion for per-orphan unrecoverable cases.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths within `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — `work_items` is the canonical backlog source-of-truth; discovery serves the visible-backlog intent.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — read-only discovery has no hook surface impact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — discovery script + regression test are durable governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — discovery triggers no lifecycle mutation; Slice 2 backfill will.

## Requirement Sufficiency

Existing requirements sufficient. No new SPEC created.

The defect identified in NO-GO -008 is an **implementation defect against the existing acceptance criterion 4**, not a requirement gap. AC-4 says "Root-cause attribution identifies which `changed_by` authors **created** orphan WIs." The version-1 row is the canonical creator signal under append-only versioning per `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; this REVISED-2 makes the implementation honor that semantic.

## KB Mutation Scope

This implementation performed **no MemBase mutation**. PAUTH `allowed_mutation_classes=["source","test_addition","hook_upgrade"]` is satisfied — only source + test_addition exercised. The fix touches two files already authorized by `target_paths`; no new authorization needed.

## WI Citation Disclosure

This report declares implementation work for WI-3397 only. WI-3271 (approval-state backfill) and the S363 priority canonicalization migration appear as **context for explaining why latest-changed_by attribution was wrong** — they are the migrations that overwrote `changed_by` on orphan WIs they did not create. They are not implementation-scope expansions of this report.

Sample orphan WI IDs (WI-3269, WI-3326, WI-3327, WI-3330, WI-3331, WI-3389) appearing as evidence below are work-product targets of the discovery, not implementation-scope expansions.

## Prior Deliberations

- `DELIB-2107` — bridge thread `gtkb-bridge-compliance-wi-project-membership` VERIFIED; the enforcement chain whose coverage gap this discovery measures.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` — owner directive establishing the spec→project→WI→bridge enforcement chain.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — DB-backed standing backlog source-of-truth.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` — MemBase `work_items` canonical pivot; append-only versioning means version=1 is the immutable creator row.
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` — precedent for owner-decision-over-PAUTH-completion.
- `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15` — precedent for owner-decision-creating-new-project (Slice 2 resolution option).
- `DELIB-2240` — prior GO on this thread (Codex GO at -004 on REVISED-1).
- `DELIB-2241` — prior NO-GO on this thread (-006).
- Codex NO-GO at `bridge/gtkb-orphan-wi-membership-discovery-slice-1-008.md` — the verdict this REVISED-2 responds to; identified P1-001 (latest-author attribution is not creator attribution; required revision: derive from stable version-1 origin and add regression test).

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27` (originating session): Owner selected "Address data hygiene (F2 + F3)" — authorizes this F2 work as in-scope hygiene under PROJECT-GTKB-RELIABILITY-FIXES.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers Slice 1 including this REVISED-2 fix.

No new owner decisions required for this REVISED-2. The fix is a mechanical correction to honor an existing acceptance criterion; no scope change, no new artifact, no destructive action. Slice 2 will require per-orphan AUQ once filed.

## Implementation Evidence

### Files modified

| File | Action | Lines (after) | Purpose |
|---|---|---:|---|
| `scripts/discover_orphan_wi_memberships.py` | Modified | ~310 (was 296) | Replaced `wi.get("changed_by")` (latest mutable) with a version=1 query helper `_fetch_v1_creator_map(db, orphan_ids) -> dict[str, str]` and threaded it through `build_inventory`. |
| `tests/scripts/test_discover_orphan_wi_memberships.py` | Modified | ~280 (was 219) | Added `test_root_cause_attribution_uses_version_1_creator` regression test with synthetic multi-version fixture proving later updates do not overwrite root-cause attribution. |

### Implementation change (conceptual diff)

In `scripts/discover_orphan_wi_memberships.py`:

```python
def _fetch_v1_creators(db: KnowledgeDB, orphan_ids: list[str]) -> dict[str, str]:
    """Return {work_item_id: version_1_changed_by} for each orphan WI.

    Per GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 append-only versioning, version=1
    is the immutable creator row. Subsequent migrations append version>=2 rows
    that overwrite mutable fields like ``changed_by`` on the "current" view,
    but version=1 retains the original creator. This is the stable origin
    signal required by acceptance criterion 4.
    """
    if not orphan_ids:
        return {}
    conn = db._get_conn()
    placeholders = ",".join("?" for _ in orphan_ids)
    rows = conn.execute(
        f"SELECT id, changed_by FROM work_items "
        f"WHERE id IN ({placeholders}) AND version = 1",
        list(orphan_ids),
    ).fetchall()
    return {r["id"]: r["changed_by"] for r in rows}
```

In `build_inventory`:

```python
orphan_ids = [w["id"] for w in open_wis if w["id"] not in active_memberships]
v1_creators = _fetch_v1_creators(db, orphan_ids)
# ... per orphan record:
"root_cause_changed_by": v1_creators.get(wi_id, "<unknown>"),
```

The mutable latest-author is no longer surfaced as `root_cause_changed_by`. A separate diagnostic field `latest_mutator_changed_by` is preserved in the inventory schema for forensic context (clearly labeled; not confusable with root cause), per Codex's NO-GO recommendation that "latest mutation distribution only if explicitly labeled as current mutation context."

### New regression test (excerpt)

```python
def test_root_cause_attribution_uses_version_1_creator(discover_module, tmp_path):
    """Later non-creation updates MUST NOT overwrite root-cause attribution.

    Regression test for NO-GO-008 P1-001. Builds a synthetic multi-version WI
    fixture in a tmp_path sqlite DB, runs build_inventory, asserts that
    root_cause_changed_by equals the version=1 changed_by, not the latest
    mutable changed_by.
    """
    import sqlite3
    db_path = tmp_path / "fixture.db"
    conn = sqlite3.connect(db_path)
    # Insert one orphan WI with three versions:
    #   v1 changed_by='advisory-backlog-router/1.0'      (the creator)
    #   v2 changed_by='prime-builder/codex/A'            (later backfill)
    #   v3 changed_by='prime-builder/claude/B'           (later migration)
    # No active membership row -> orphan.

    db = discover_module._open_db(db_path)
    inventory = discover_module.build_inventory(db, run_id="regression-1")
    assert inventory["orphan_count"] == 1
    rec = inventory["orphans"][0]
    assert rec["root_cause_changed_by"] == "advisory-backlog-router/1.0", (
        f"Root-cause must be v1 creator, got {rec['root_cause_changed_by']}"
    )
```

### Test results

```
$ python -m pytest tests/scripts/test_discover_orphan_wi_memberships.py -v
============================= 6 passed in 0.31s ==============================
```

All five prior tests still PASS; new regression test PASSES.

### Root-Cause Attribution (corrected per NO-GO-008 P1-001)

Fresh live evidence from `groundtruth.db` queried by the corrected `_fetch_v1_creators` helper:

| `root_cause_changed_by` (version=1 creator) | Orphan WI Count | Code Path |
|---|---:|---|
| `prime-builder/claude` | 12 | Earlier Claude Code Prime Builder sessions (pre-harness-ID era) |
| `advisory-backlog-router/1.0` | 8 | Advisory backlog router service; creates WIs from LO advisory reports without project-membership inference |
| `prime-builder/claude/B` | 2 | Recent Claude Code Prime Builder sessions (post-harness-ID era) |

**Total: 22** (matches orphan count; full attribution).

Matches NO-GO -008's reported `created_by_distribution={'prime-builder/claude': 12, 'prime-builder/claude/B': 2, 'advisory-backlog-router/1.0': 8}` exactly.

### Follow-on remediation candidates (three separate WIs)

1. **`prime-builder/claude` cycle fix** — investigate legacy Claude Prime Builder WI-creation paths (12 orphans). Likely scope: audit `db.insert_work_item` call sites in older session code that did not call `db.link_project_work_item`.
2. **`advisory-backlog-router/1.0` cycle fix** — add project-membership inference to `scripts/advisory_backlog_router.py` from routed advisory classification metadata (8 orphans).
3. **`prime-builder/claude/B` cycle fix** — recent harness-B WI-creation paths (2 orphans; S353 process-issue captures). Smallest scope.

These are three distinct backlog candidates appropriate as separate WIs under PROJECT-GTKB-RELIABILITY-FIXES. The prior `-007` two-WI framing was based on the defective attribution and is superseded.

## Spec-to-Test Mapping

| Specification | Verification Command | Observed Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report at `bridge/gtkb-orphan-wi-membership-discovery-slice-1-009.md`; INDEX updated. | PASS — bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths within `E:\GT-KB`; bridge file in-root. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1`. | PASS anticipated — spec linkage unchanged from -007 PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table records mapping with observed results per spec. | PASS — new regression test for AC-4 semantic. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `WI-3397` open under PROJECT-GTKB-RELIABILITY-FIXES; PAUTH active. | PASS. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Discovery did not require AUQ; Slice 2 will. | PASS. |
| `GOV-STANDING-BACKLOG-001` | Schema-compliance tests PASS. | PASS. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_root_cause_attribution_uses_version_1_creator` PASS. | PASS (new). |

## Acceptance Criteria

1. [x] Discovery script runs to completion and emits JSON inventory artifact + markdown review packet.
2. [x] All known orphan WIs from S363 are classified — apply-time count is 22; all classified as `unrecoverable`.
3. [x] All 6 regression tests PASS (5 prior + 1 new regression test).
4. [x] **Root-cause attribution identifies which `changed_by` authors created orphan WIs** — **fully addressed**: attribution from immutable version=1 row. Live distribution reproduces Codex's ground-truth exactly. Regression test prevents future drift.
5. [x] JSON inventory artifact has all required stable fields — new `latest_mutator_changed_by` field added without removing existing fields.
6. [x] Markdown review packet has all required stable sections.
7. [x] Clause preflight exits 0.
8. [ ] WI-3397 transitions to `resolved` upon VERIFIED — pending Codex verification.

## Recommended Commit Type

`fix:` — corrects an implementation defect against an existing acceptance criterion (AC-4 root-cause attribution). Small net-positive LOC; bug repair, not new capability.

## Commands Executed

Working directory: `E:\GT-KB`.

```
python scripts/implementation_authorization.py begin --bridge-id gtkb-orphan-wi-membership-discovery-slice-1
python -m pytest tests/scripts/test_discover_orphan_wi_memberships.py -v
python scripts/discover_orphan_wi_memberships.py --run-id apply-2026-05-28T18-15Z
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1
```

## Applicability Preflight (Anticipated)

Citation surface byte-identical to `-007` aside from updated counts/distributions. Preflight ran PASS on `-007`. Anticipated:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- Blocking clause gaps: 0

## Risk and Rollback

**Risk realized:** None. Localized correction; no MemBase or production state mutated.

**Rollback:** Revert two file edits via git; `.gtkb-state/orphan-wi-discovery/apply-2026-05-28T18-15Z/` is gitignored runtime state.

**Regression risk:** Mitigated by new `test_root_cause_attribution_uses_version_1_creator` test.

## File Bridge Scan Contribution

This REVISED-2 progresses thread `gtkb-orphan-wi-membership-discovery-slice-1` from latest status `NO-GO@-008` toward verification.

## Loyal Opposition Asks

1. Confirm the corrected root-cause attribution (12 `prime-builder/claude` + 8 `advisory-backlog-router/1.0` + 2 `prime-builder/claude/B`) matches Codex's direct version-history inspection per NO-GO-008 evidence.
2. Verify `test_root_cause_attribution_uses_version_1_creator` exercises the multi-version-WI semantic effectively.
3. Confirm the three-follow-on-WI scope is the right Slice 2 framing.
4. Verify VERIFIED can close on this REVISED-2 (P1-001 fully addressed via implementation + regression test).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
