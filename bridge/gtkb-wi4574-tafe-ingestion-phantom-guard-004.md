REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c50a9788-517e-4adc-a32d-a14594942b91
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code autonomous Prime Builder session; WI-4574 REVISED after NO-GO -003 (remove --apply)
author_metadata_source: env runtime envelope (WI-4522)

# WI-4574 — TAFE ingestion phantom-guard + reconcile the isolated `sp1` orphan (REVISED after NO-GO -003)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4574
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/tests/test_tafe_bridge_ingestion.py", "config/governance/tafe-acknowledged-archived-bridges.toml"]

## Response to NO-GO (bridge/gtkb-wi4574-tafe-ingestion-phantom-guard-003.md)

- **F1 (P1, blocking) — the verification plan's `gt flow ingest-bridge-index --apply` is a DB mutation
  outside `target_paths`.** RESOLVED via Codex's offered remedy 2 (remove `--apply`; read-only
  verification only). WI-4574 needs NO database write: (a) the ingestion phantom-guard is verified by
  unit tests that call `ingest_bridge_index(..., apply=True)` against an in-memory fixture DB (each test
  uses its own `tmp_path` DB, not the project `groundtruth.db`); (b) the `sp1` reconciliation is verified
  by a READ-ONLY `gt flow regen-verify` confirming `sp1-dispatch-reliability-prime-handoff` is now in
  `extra_archived_in_generated` (tolerated) rather than `extra_divergent_in_generated` (gating). The
  `target_paths` are unchanged (the three source/test/config files); no DB target is needed.
- **Scope clarification (the overall regen-verify GREEN belongs to WI-4510 Phase-0, not WI-4574).** A
  read-only `gt flow regen-verify` against the live shadow currently also reports
  `missing_in_generated = [gtkb-wi4574-tafe-ingestion-phantom-guard]` — i.e. the WI-4574 thread itself
  is not yet in the shadow. That is pure shadow-staleness (the shadow has not ingested the new thread),
  reconciled by the `gt flow ingest-bridge-index --apply` Phase-0 step that WI-4510 already owns (its
  cutover PAUTH covers `dual_write`). WI-4574's deliverable is narrower and DB-write-free: prove the
  `sp1` orphan is reclassified from gating to tolerated. The overall regen-verify GREEN is achieved when
  WI-4510's Phase-0 re-ingest runs; this fix does not perform that re-ingest.

## Summary

WI-4574 is the owner-directed blocking precursor that unblocks the WI-4510 TAFE cutover. WI-4510's
Phase-2 gate (`gt flow regen-verify`, after the Refined-Option-B fix landed this session) was
legitimately RED on a single isolated phantom shadow row: `flow-bridge-sp1-dispatch-reliability-prime-handoff`
(subject_id `sp1-dispatch-reliability-prime-handoff`, no `gtkb-` prefix, whose only `flow_artifact`'s
`artifact_ref` points at `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md` — i.e. a pure
duplicate of the correctly-slugged `gtkb-sp1-…` instance; zero content loss).

Root cause (owner-directed "investigate first"; a full shadow scan of 349 `bridge_thread` instances
confirmed it is ISOLATED — exactly 1 phantom / 1 mismatched / 1 duplicate, NOT systemic): the ingestion
`_plan_thread` derives the flow-instance `subject_id` directly from the INDEX `Document:` block name
(`slug = block.name`) with no consistency check against the block's version-line `artifact_ref`. A
historical phantom INDEX entry `Document: sp1-…` (no `gtkb-` prefix) pointing at the `gtkb-sp1-…` file
was ingested → orphan instance; the INDEX phantom was later trimmed, but the append-only shadow retains
the orphan.

This proposal makes two scoped, single-concern defect fixes:
1. **Ingestion phantom-guard (source + test):** `_plan_thread` skips a `Document:` block whose name does
   not match the slug derived from its version-line `artifact_ref`, so a phantom/malformed block can
   never again create a mismatched-`subject_id` orphan. Enforces the existing ingestion identity
   contract (`ADR-TAFE-SLICE-C-INGESTION-001` D2: `flow-bridge-<slug>` with `subject_id` consistent
   with the thread's bridge files). No new public API, CLI, or behavior beyond removing the defect.
2. **Reconcile the existing `sp1` orphan (owner-curated config):** add
   `sp1-dispatch-reliability-prime-handoff` to `config/governance/tafe-acknowledged-archived-bridges.toml`
   (rule 3, reversible) so the already-landed regen-verify oracle classifies it as tolerated archival
   residue instead of a gating divergence. The append-only shadow row cannot be deleted; rule-3
   acknowledgement is the sanctioned, reversible reconciliation.

Net effect: the `sp1` orphan moves from gating (`extra_divergent_in_generated`) to tolerated
(`extra_archived_in_generated`) in `gt flow regen-verify`. Combined with WI-4510's own Phase-0 shadow
re-ingest (which adds the WI-4574 thread to the shadow), regen-verify reaches GREEN, unblocking
WI-4510's Phase-2 acceptance.

## Authorization (dual; explicit)

- **Fast-lane (source + test):** WI-4574 is a `GOV-RELIABILITY-FAST-LANE-001`-eligible defect fix
  (origin=defect; small/single-concern, ~1 source change + tests, well under the ~150-line guide; no new
  requirement). WI-4574 was admitted to `PROJECT-GTKB-RELIABILITY-FIXES`, so the ingestion-guard
  source + test are covered by the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
  (`allowed_mutation_classes = [source, test_addition, hook_upgrade]`).
- **Owner-curated config (the `sp1` entry):** the `config` mutation of the owner-curated
  `tafe-acknowledged-archived-bridges.toml` is NOT claimed under the fast-lane PAUTH; it is authorized
  by the owner directive recorded as `DELIB-WI4574-RECONCILE-AND-GUARD-AUTHORIZE-20260615`, consistent
  with that config's existing curation provenance (its header cites
  `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614`). The entry is reversible — removing it
  re-surfaces the slug — so it never permanently suppresses a real defect.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains the SOLE authoritative bridge workflow
  state; this fix honors CLAUSE-INDEX-IS-CANONICAL. Neither change writes `bridge/INDEX.md`: the
  ingestion `_plan_thread` guard is read-derive-only (it reads INDEX-parsed blocks and SKIPS mismatched
  ones; it never writes INDEX), the `tafe-acknowledged-archived-bridges.toml` edit is a governance
  config (not the INDEX), and `gt flow regen-verify` is read-only of the canonical INDEX and refuses to
  write it. The canonical INDEX is unchanged by this fix.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the ingestion identity derivation (D2: `flow-bridge-<slug>`,
  per-version `fa-bridge-<slug>-<NNN>`); the phantom-guard enforces the implicit consistency contract
  that a block's `subject_id` must match the slug of its version-line `artifact_ref`. The orphan is a
  violation of that contract.
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the rule-3 acknowledged-archived config
  mechanism the `sp1` reconciliation uses; the same shared classifier (`_candidate_is_archived`) the
  regen-verify oracle reuses.
- `GOV-RELIABILITY-FAST-LANE-001` — the eligibility + standing-authorization basis for the source/test
  defect fix.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` — the WI-4510 cutover this precursor unblocks; regen-verify
  is the Phase-2 gate whose `sp1` divergence this fix clears.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory cross-cutting: this section cites
  all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mandatory cross-cutting: the Spec-Derived
  Verification Plan derives its tests from the guard's consistency contract + the reconciliation's
  read-only regen-verify acceptance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory trio) — this fix is an artifact-lifecycle action: a
  defect-fix work item with an owner-decision reconciliation (the `sp1` acknowledged-archived entry) and
  a governed deliberation (`DELIB-WI4574-RECONCILE-AND-GUARD-AUTHORIZE-20260615`).
- `GOV-STANDING-BACKLOG-001` — WI-4574 is the governed standing-backlog work item driving this fix.

## Prior Deliberations

- `DELIB-WI4574-RECONCILE-AND-GUARD-AUTHORIZE-20260615` — owner directive ("continue with WI-4574")
  authorizing this fix after the isolated root-cause finding.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the reliability fast-lane standing authorization.
- `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614` — the curation provenance of the acknowledged-
  archived config (rule-3 disposition mechanism the `sp1` entry follows).
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614`, `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614`
  — the WI-4510 cutover chain this precursor unblocks; the Refined-Option-B regen-verify fix
  (`bridge/gtkb-wi4510-tafe-authoritative-cutover-006.md` GO) is what surfaced the `sp1` phantom.
- `bridge/gtkb-wi4574-tafe-ingestion-phantom-guard-003.md` — the Loyal Opposition NO-GO this revision
  resolves (F1: `--apply` DB mutation outside `target_paths`).

## Owner Decisions / Input

This proposal depends on owner approval, captured via the owner directive recorded as
`DELIB-WI4574-RECONCILE-AND-GUARD-AUTHORIZE-20260615` (owner: "Please continue with WI-4574", after the
"investigate root cause first" AUQ). That directive authorizes both the fast-lane ingestion-guard and
the owner-curated `sp1` acknowledged-archived config entry. No further owner decision is required to
review or implement this fix.

## Requirement Sufficiency

**Existing requirements sufficient.** The phantom-guard enforces the existing ingestion identity
contract in `ADR-TAFE-SLICE-C-INGESTION-001` (subject_id consistent with the thread's bridge files) —
it adds a consistency check that removes the orphan-creation defect, not a new capability. The `sp1`
reconciliation uses the existing rule-3 acknowledged-archived mechanism
(`DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`). No new or revised specification is needed.

## Proposed Change

**Change 1 — ingestion phantom-guard (`groundtruth_kb/tafe_bridge_ingestion.py`, `_plan_thread`).**
After `slug = block.name`, derive the file-slug from the block's latest version-line `path`
(strip the `bridge/` prefix and the `-NNN.md` suffix). When the file-slug is determinable AND differs
from `slug`, return `None` (skip the block; recorded in the ingestion's `skipped` list) so no
mismatched-`subject_id` flow_instance/artifact is ever created. Fail-open when the file-slug is not
determinable (no recognizable `-NNN.md` suffix) — only a clear mismatch skips, so legitimate threads
are never dropped.

**Change 2 — reconcile the `sp1` orphan (`config/governance/tafe-acknowledged-archived-bridges.toml`).**
Append an `[[acknowledged]]` entry `slug = "sp1-dispatch-reliability-prime-handoff"` with a reason
documenting it as a phantom duplicate (same `artifact_ref` as `gtkb-sp1-…`, zero content loss) of an
append-only shadow row, acknowledged to unblock regen-verify; reversible.

**Test — `groundtruth-kb/tests/test_tafe_bridge_ingestion.py`.** Add cases: (a) a `Document:` block whose
name mismatches its version-line file-slug is skipped (no flow_instance created, slug in `skipped`);
(b) a normal matching block ingests unchanged; (c) a block with an unparseable path is NOT skipped
(fail-open regression guard).

## Spec-Derived Verification Plan

Derived from the guard's consistency contract + the reconciliation's READ-ONLY regen-verify acceptance
(per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`); NO database `--apply` step is in scope:

- `test_tafe_bridge_ingestion.py`: the three cases above (mismatch-skipped, normal-ingested,
  unparseable-not-skipped), executed via `ingest_bridge_index(..., apply=True)` against a per-test
  in-memory fixture DB (`tmp_path`), not the project `groundtruth.db`; assertions on the resulting
  flow_instances / `skipped`.
- Reconciliation (recorded in the impl report; READ-ONLY): `gt flow regen-verify --json` (no
  `--apply-refresh`) shows `sp1-dispatch-reliability-prime-handoff` in `extra_archived_in_generated` and
  NOT in `extra_divergent_in_generated`. (The overall `ok` may remain False solely due to
  `missing_in_generated = [gtkb-wi4574-…]`, which is shadow-staleness reconciled by WI-4510's Phase-0
  `--apply` re-ingest — out of WI-4574 scope; this fix performs no re-ingest.)
- Regression: the existing `test_tafe_bridge_ingestion.py` suite + the broader TAFE/flow suite remain
  green (the guard only skips clear mismatches).
- Gates on changed Python: `ruff check` + `ruff format --check`.

## Risk / Rollback

- **Risk:** the guard skips a legitimate block (false positive). **Mitigation:** it skips ONLY when the
  file-slug is determinable AND clearly differs from the block name; unparseable paths fail open
  (current behavior). A full shadow scan found exactly one mismatch (`sp1`), so the real-world skip set
  is the single known phantom.
- **Risk:** acknowledging `sp1` hides a real thread. **Mitigation:** `sp1` is a verified pure duplicate
  (same `artifact_ref` as the correctly-slugged `gtkb-sp1-…`, which remains in INDEX + shadow); zero
  content loss. The entry is reversible (rule 3); removing it re-surfaces the slug.
- **Rollback:** revert `tafe_bridge_ingestion.py` + the test to HEAD (additive guard); remove the
  `sp1` config entry. No schema change, no data deletion, no DB `--apply` (append-only shadow untouched
  by this fix).

## Recommended Commit Type

`fix:` — repairs the ingestion orphan-creation defect and reconciles the resulting isolated `sp1`
shadow residue; no new capability surface.
