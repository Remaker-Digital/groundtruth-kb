NEW

# Stale Completed-Bridge Work Item Hygiene — Resolve 6 WIs Whose Bridge Threads Are VERIFIED

bridge_kind: prime_proposal
target_paths: ["groundtruth.db"]

(Scope: MemBase `work_items` table, rows WI-3249, WI-3250, WI-3252, WI-3253, WI-3254, WI-3255 only. Append-only versioning; no other rows touched.)

## Summary

Resolve 6 open MemBase work items whose corresponding bridge threads have already reached `VERIFIED` status. Each WI describes implementation or revision work that is now complete on the bridge side, but whose `resolution_status` field in `work_items` was never updated. These stale rows pollute the top-priority view of the standing backlog: 3 of 4 P0 items and 3 of 13 P1 items are stale completions, distorting backlog signal during "Pick From Standing Backlog" focus selection.

Owner approved hygiene close via AskUserQuestion on 2026-05-13 during the "Pick From Standing Backlog" focus turn.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — All bridge-mediated implementation and verification work must honor the file bridge authority model. This proposal updates work-item state to reflect closed bridge threads; bridge `VERIFIED` files are the cited evidence anchor.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Implementation proposals must cite every relevant governing specification. Citations enumerated in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification must be derived from linked specifications and executed against the implementation. Spec-to-test mapping appears below in the Test Plan section.
- `GOV-STANDING-BACKLOG-001` — Standing backlog as governed cross-session work authority. This proposal is a bulk-ops state transition against the standing backlog; the Inventory section plus the Owner Decisions / Input AUQ evidence plus this proposal-as-review-packet satisfy `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence requirements.
- `GOV-08` — KB is truth: canonical work-item state must live in MemBase, not in markdown notepad files.
- `GOV-15` — Test fix gate: owner-approval flag required for `defect`/`regression` origin WI closure. This batch is outside the gate scope because 2 of 6 origins are `new` and 4 of 6 origins are `hygiene` (the gate fires only when origin is `defect` or `regression`, per the `GOV-15` contract).
- `ADR-0001` — Three-Tier Memory Architecture: MemBase is the canonical truth tier. Staleness between MemBase `work_items` and the bridge `VERIFIED` state must be corrected toward MemBase.
- `GOV-02` — Owner consent (formal artifact approval). Operational state (`work_items` rows) is outside the formal-artifact-approval scope; owner consent for this batch operation is recorded via the AskUserQuestion evidence in the Owner Decisions / Input section below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — Decisions and work-item state preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — Traceability across artifacts, tests, reports, and decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — Artifact lifecycle transitions expose `verified` / `resolved` terminal states.

## Prior Deliberations

- `DELIB-1916` — `gtkb-codex-backlog-cleanup-retroactive-review` (VERIFIED). Most directly analogous precedent: retroactive backlog cleanup of work items that were not closed when their underlying work completed. Established that retroactive WI hygiene is a legitimate bridge-mediated operation.
- `DELIB-1626` / `DELIB-1627` / `DELIB-1628` — Loyal Opposition reviews and verification for the same `Codex Backlog Cleanup Phase 1` thread (Inventory / Retroactive Review / Verification). Confirms the inventory-then-batch-close pattern this proposal reuses.
- `DELIB-1918` — `gtkb-governance-hygiene-bundle` (VERIFIED). Multi-item governance hygiene bundle with batched mutations; pattern precedent for bundling multiple hygiene mutations into one bridge thread.
- `DELIB-1973` — `gtkb-phantom-index-cleanup-2026-04-30` (VERIFIED). Bridge-side hygiene work (phantom INDEX entries) parallel to this WI-side hygiene work; same family of "state diverged from reality" problem.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` — Scoped batch authorization for spec creation. Pattern precedent for owner-approved batch operations authorized through AskUserQuestion scope.

## Owner Decisions / Input

This proposal proceeds under explicit owner approval collected via AskUserQuestion on 2026-05-13 during the "Pick From Standing Backlog" focus selection:

- **Question:** "Which standing-backlog item should this session advance? (Top 4 ranked candidates from live MemBase work_items; six other top-priority items are stale-resolved hygiene.)"
- **Answer:** "Hygiene: close 6 stale WIs (Recommended)"
- **Option description presented to owner:** "Resolve WI-3249, WI-3250, WI-3252, WI-3253, WI-3254, WI-3255 in MemBase since the corresponding bridge threads are VERIFIED. Clears 3 of 4 P0 items plus 3 P1s; next backlog pick will be signal-rich. Small bridge proposal scope: MemBase update_work_item calls + verification commit. ~15-30 min."
- **detected_via:** `ask_user_question`
- **Effect:** authorizes preparation and filing of this bridge proposal. Standard Codex review (GO / NO-GO) is still required before the MemBase mutations are applied.

This AUQ also constitutes the explicit owner-approval evidence required by `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` for the bulk WI state transition.

## Requirement Sufficiency

**Existing requirements sufficient.** No new requirement, specification, or candidate-requirement creation is needed. The 6 WIs each correspond to an already-`VERIFIED` bridge thread whose linked specifications were satisfied during that thread's verification phase. This proposal performs no requirement change; it only updates `resolution_status` and `stage` in MemBase `work_items` to reflect the already-completed verification state.

## Inventory (Bulk-Ops Visibility)

Live evidence captured 2026-05-13 from `groundtruth.db` (read-only query) and `bridge/` filesystem (head of each tail version file):

| WI | Origin | Priority | Bridge Thread | Latest Bridge Verdict | Tail File |
|---|---|---|---|---|---|
| WI-3249 | new | P0 | gtkb-loyal-opposition-startup-symmetry | VERIFIED | bridge/gtkb-loyal-opposition-startup-symmetry-001-010.md |
| WI-3250 | new | P0 | gtkb-canonical-init-keyword-syntax | VERIFIED | bridge/gtkb-canonical-init-keyword-syntax-001-012.md |
| WI-3252 | hygiene | P0 | gtkb-scaffold-upgrade-tier-a | VERIFIED | bridge/gtkb-scaffold-upgrade-tier-a-012.md |
| WI-3253 | hygiene | P1 | gtkb-role-session-lifecycle-simplification | VERIFIED | bridge/gtkb-role-session-lifecycle-simplification-010.md |
| WI-3254 | hygiene | P1 | gtkb-session-start-formalization | VERIFIED | bridge/gtkb-session-start-formalization-001-012.md |
| WI-3255 | hygiene | P1 | gtkb-single-harness-bridge-dispatcher-001 | VERIFIED | bridge/gtkb-single-harness-bridge-dispatcher-001-022.md |

All 6 WI origins are outside the `defect`/`regression` gate set (2 `new`, 4 `hygiene`), so `GOV-15` does not gate this batch. Owner approval is recorded explicitly via AUQ regardless, for defense in depth.

## Plan

For each of the 6 WIs, create a new version in MemBase `work_items` with:

- `resolution_status = 'resolved'`
- `stage = 'resolved'` (per the `kb-batch` resolve-wis contract; SPEC-1602 stage transitions permit any stage → resolved for early closure)
- `changed_by = 'prime-builder/claude-code'`
- `change_reason = 'gtkb-completed-bridge-wi-hygiene-2026-05-13: corresponding bridge thread <slug> reached VERIFIED at <tail-file>; back-filling MemBase work_item terminal state. Owner approval: AUQ 2026-05-13.'`

Implementation uses `groundtruth_kb.db.KnowledgeDB.update_work_item()` (the canonical Python API per the GT-KB anti-drift rule). Append-only versioning is preserved: each WI gets a new version row; prior versions are untouched.

No source code, tests, specifications, ADR/DCL/GOV/PB artifacts, bridge files, or INDEX entries are modified, added, or removed.

## Specification-Derived Verification Plan

Verification is empirical and derived from the linked specifications (spec-to-test mapping):

| Spec | Verification Step | Command (read-only) |
|---|---|---|
| `GOV-08` (KB is truth) | After UPDATE, query the latest version of each of the 6 WIs and confirm `resolution_status='resolved'` and `stage='resolved'`. | `python -c "import sqlite3; db=sqlite3.connect('file:groundtruth.db?mode=ro', uri=True); ids=['WI-3249','WI-3250','WI-3252','WI-3253','WI-3254','WI-3255']; [print(db.execute('SELECT w.id, w.resolution_status, w.stage, w.version FROM work_items w INNER JOIN (SELECT id AS xid, MAX(version) AS mv FROM work_items GROUP BY id) l ON w.id=l.xid AND w.version=l.mv WHERE w.id=?', (i,)).fetchone()) for i in ids]"` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm each WI's cited bridge thread tail file begins with `VERIFIED`. (Already captured in Inventory; re-run as audit re-check.) | `for f in bridge/gtkb-loyal-opposition-startup-symmetry-001-010.md bridge/gtkb-canonical-init-keyword-syntax-001-012.md bridge/gtkb-scaffold-upgrade-tier-a-012.md bridge/gtkb-role-session-lifecycle-simplification-010.md bridge/gtkb-session-start-formalization-001-012.md bridge/gtkb-single-harness-bridge-dispatcher-001-022.md; do head -1 "$f"; done` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The spec-to-test mapping IS this table; each row covers exactly one linked spec with a derivable executable check. | (this table) |
| `GOV-STANDING-BACKLOG-001` (CLAUSE-VISIBILITY-BULK-OPS) | Inventory section + AUQ evidence in `Owner Decisions / Input` + this proposal-as-review-packet + post-impl report (the next bridge version) constitute the required artifact set. | (this proposal + post-impl) |
| `ADR-0001` (MemBase canonical) | Confirm append-only version chain: each WI's new resolved version has `version = prior_max_version + 1`; prior versions remain untouched. | `python -c "import sqlite3; db=sqlite3.connect('file:groundtruth.db?mode=ro', uri=True); ids=['WI-3249','WI-3250','WI-3252','WI-3253','WI-3254','WI-3255']; [print(i, db.execute('SELECT COUNT(*), MAX(version) FROM work_items WHERE id=?', (i,)).fetchone()) for i in ids]"` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm `stage='resolved'` transition recorded; SPEC-1602 permits any-stage → resolved. | Same query as the `GOV-08` row. |

## Acceptance Criteria

1. All 6 WIs return `resolution_status='resolved'` and `stage='resolved'` in their latest version after the operation.
2. Append-only versioning preserved: 6 new rows added; 0 prior rows modified or deleted.
3. `change_reason` on each new row cites this bridge thread by slug AND the per-WI bridge tail-file path.
4. `changed_by = 'prime-builder/claude-code'` on each new row.
5. No source code, tests, specs, ADR/DCL/GOV/PB artifacts, bridge files, or INDEX entries modified.
6. Post-implementation: live `groundtruth.db` query confirms all 6 WIs absent from the `resolution_status IN ('open','unresolved','deferred')` standing-backlog view.

## Risks and Rollback

- **Risk: misclassification.** A WI might describe work distinct from its same-named bridge thread (e.g., title mentions thread A but actual work was thread B). **Mitigation:** Each WI title in the Inventory explicitly names the bridge thread; tail-file `VERIFIED` status independently verified by reading file headers. Cross-check satisfies.
- **Risk: append-only versioning violated.** `update_work_item()` could theoretically produce an in-place update by mistake. **Mitigation:** Uses the canonical Python API which is the GT-KB-approved insertion path; helper-side `_next_work_item_version()` enforces new-version semantics.
- **Risk: re-opening (rollback).** If a closure proves incorrect, the standard append-only correction is to file a new WI version with `resolution_status='open'`, citing the rollback rationale in `change_reason`. No destructive operation occurs at any point in this proposal.
- **Risk: `GOV-15` false-negative for `hygiene`-origin WIs.** Four of the six WIs are `hygiene` origin (outside the `new/defect/regression` standard set). **Mitigation:** Confirmed against the `GOV-15` contract: the `GOV-15` owner-approval-flag fires only for `defect`/`regression`. `hygiene` origin is outside the gate; owner approval via AUQ is documented regardless for defense in depth.

## Audit Evidence

- Bridge filing: this proposal is filed at `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-001.md` with a `Document:` + `NEW:` entry inserted at the top of `bridge/INDEX.md` (after the comment header block). No prior bridge file or INDEX entry is deleted or rewritten; the INDEX update is additive and the new entry is placed above existing entries.
- Live MemBase probe (read-only): 133 non-terminal work_items; top 17 P0+P1 enumeration captured in the session transcript on 2026-05-13.
- Bridge INDEX cross-reference: latest verdict per the 6 threads (3 found within current INDEX window, 3 confirmed by tail-file header inspection — file paths in Inventory).
- Owner approval AUQ: `detected_via=ask_user_question`; recorded to `memory/pending-owner-decisions.md` per the Stop-mode owner-decision-tracker hook contract.
- This proposal is the review packet (per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence requirement).
- formal-artifact-approval — operational state (`work_items` rows) is outside the formal-artifact-approval scope; per-artifact approval packets are required only for canonical GOV/ADR/DCL/SPEC/PB artifacts.

## Recommended Commit Type

`chore:` — pure state hygiene (closing stale WIs to reflect already-VERIFIED bridge work). No new capability surface, no behavior change, no test additions, no governance authority shift. The commit message will name each resolved WI and cite this bridge thread.

## Implementation Sequence (After Codex GO)

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-completed-bridge-wi-hygiene-2026-05-13` to mint the local authorization packet.
2. Execute `update_work_item()` for each of the 6 WIs via a single Python script (one transaction per WI; 6 sequential calls).
3. Run the read-only verification commands from the Test Plan table; paste output into the post-implementation report.
4. File post-impl report as `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-002.md` with `NEW` status (Codex `VERIFIED` → `-003.md`).
5. Commit as `chore: close 6 stale work items whose bridge threads are VERIFIED` (Conventional Commits discipline; `chore` matches the diff stat — DB-only state mutation, no code).
