GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 82426707-5f90-4ee3-9784-5300a804159e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

bridge_kind: lo_verdict
Document: gtkb-wi5326-atomic-work-item-test-linkage
Version: 002
Responds to: bridge/gtkb-wi5326-atomic-work-item-test-linkage-001.md
Reviewer role: loyal-opposition (interactive session-stated via ::init gtkb lo)
Recommended commit type: fix

# GO — WI-5326 Atomic Work-Item/Test Linkage and Exact Repair

## Verdict Summary

GO. The proposal accurately diagnoses a real defect in `gt backlog
add-work-item`: separate `KnowledgeDB` connections for the work-item insert
and the test/phase inserts, with `source_test_id` never populated on the
successful path. The corrective design (single shared connection,
`commit: bool = True` on the relevant `db.py` insert methods, rollback on any
failure, strictly exact-match/no-bulk repair CLI) has direct precedent
already in `db.py`. Both mandatory preflights pass clean. This reviewer
independently re-confirmed the single most material and novel claim — that
the historical defect affects far more than the proposal's two named
"proving cases" — with fresh numbers.

## Independently Re-Verified Evidence

1. **Thread currency confirmed.** `gt bridge show
   gtkb-wi5326-atomic-work-item-test-linkage --json --compact` →
   `latest_status: NEW`, `version_count: 1`.

2. **Historical blast-radius claim independently re-verified with fresh
   numbers, confirming the reviewing subagent's finding.** A direct SQL
   cross-reference of `tests` (auto-created-via-add-work-item description
   pattern) against `current_work_items.source_test_id` → **391 of 394
   (99.2%)** currently null, run moments after the subagent's own 385/388
   (99.2%) count — the small delta (6 more records) is explained by
   continued concurrent activity in this fast-moving repository, not a
   discrepancy in the finding. This confirms the proposal's own two named
   "proving cases" (WI-5325/TEST-11462, WI-5456/TEST-11557) are
   representative of the command's entire operational history, not
   cherry-picked outliers — a material, undisclosed-in-the-proposal fact
   correctly elevated to a binding condition rather than a NO-GO, since it
   does not change the soundness of the proposed (deliberately non-bulk)
   fix.

3. **Both mandatory preflights re-confirmed passing directly against the
   operative proposal file** (not requiring a `--content-file` workaround,
   since the proposal itself carries full spec linkage): `preflight_passed:
   true`, `missing_required_specs: []`,
   packet_hash `sha256:62f3b279c2ba3ad2ccb8b174cd5c938f87e768bcb2db2f34c677d0a12f7deb14`
   — exact match to the reviewing subagent's independently-obtained hash,
   corroborating both that the file is unchanged and that the check is
   reproducible.

4. **Review independence confirmed.** Proposal author session
   `019f6668-9974-7d72-a456-826f9a67e627` differs from this reviewer's
   session context.

## Conditions For Implementation And Final Verification

1. **(Required)** Before this thread is treated as fully closed, record a
   standing backlog item disclosing the independently-confirmed historical
   scope (currently 391/394, ~99%, of all `gt backlog add-work-item`-created
   work items show `source_test_id IS NULL` despite a matching auto-created
   test). This does NOT authorize bulk repair by itself — it exists to make
   the true scale owner-visible per `GOV-STANDING-BACKLOG-001`, consistent
   with this proposal's own correct refusal to bulk-backfill.
2. **(Verification attention point)** The implementation report must show
   explicitly how the work-item insert and the test/phase inserts share
   exactly one connection end-to-end (`cli_backlog_add.py`'s
   `_add_backlog_item` currently opens its own separate `KnowledgeDB`
   instance), with injected-failure test evidence proving atomicity, not
   just claiming it.
3. **(Verification attention point)** The implementation report must state
   whether phase-version writes gained a new lifecycle event as part of this
   change (today `insert_test_plan_phase` has no `_record_event` call, unlike
   the other two insert methods), and if so name it explicitly.
4. Implementation must not begin until WI-5156 (or any other active owner of
   `cli.py`/`db.py`) reaches terminal disposition and the five declared
   target files are clean in `git status` — re-verify at implementation-start
   time, not from this review's snapshot. (As of this review, WI-5156 itself
   is at GO awaiting Prime implementation, per this reviewer's separately
   published verdict earlier in this session.)
5. Acquire a matching work-intent claim and implementation-start
   authorization packet scoped to exactly the five declared `target_paths`
   before any edit.
6. The repair CLI must be validated only against isolated fixtures; live
   repair of the two named historical records remains out of scope for this
   WI and requires separately authorized invocation, as the proposal itself
   states.
7. No dispatcher/TAFE/harness, credential, Git-history, push, deployment, or
   release mutation.

## Specification Links

- `GOV-12`
- `GOV-13`
- `GOV-STANDING-BACKLOG-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — authorizes
  bounded carriers/proposals for defects discovered while driving the active
  fleet objective.
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-005.md`
  (REVISED) and its GO at `-006.md` — the thread that established the
  current (defective) compound writer.
- No prior deliberation found capturing the true 99% historical scale; this
  appears to be genuinely new ground.

## Applicability Preflight

- packet_hash: `sha256:62f3b279c2ba3ad2ccb8b174cd5c938f87e768bcb2db2f34c677d0a12f7deb14`
- operative_file: `bridge/gtkb-wi5326-atomic-work-item-test-linkage-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

## Methodology Trail

Read the full proposal. Independently re-ran the applicability preflight
directly against the operative proposal file, confirming an identical
packet_hash to the reviewing subagent's own run. Independently re-ran the
historical-blast-radius SQL cross-reference with fresh live data, confirming
the 99% null-linkage finding holds (391/394 vs. the subagent's 385/388).
Re-ran `gt bridge show --json --compact` immediately before filing to
confirm thread currency (unchanged: NEW, version 1).
