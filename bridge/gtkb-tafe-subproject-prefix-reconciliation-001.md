NEW

# WI-4511: Generalize Doubled-Prefix Reconciliation to Clean TAFE Sub-Project Phantom Rows

bridge_kind: prime_proposal
Document: gtkb-tafe-subproject-prefix-reconciliation
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 869ade5b-58a4-4261-b2cb-98fcbecb8c0e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4511

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cli_projects_reconcile.py", "groundtruth.db"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: fix:

---

## Summary

Implement WI-4511, the cleanup of duplicate TAFE sub-project rows in the MemBase `projects` table. The duplicates are a second manifestation of the same `_project_id_from_names` doubling defect that produced the `PROJECT-PROJECT-*` phantoms reconciled under WI-3355 — but for **sub-projects**, where the doubled segment is the full canonical parent id rather than the literal `PROJECT-` prefix.

Concretely, each of the 8 TAFE sub-projects (Phase-0 through Phase-7) has two rows with the same display name (`PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE/Phase-N-...`):

- A **canonical** row, e.g. `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-3-DISPATCH-POLICY-ENGINE` — currently **empty** (no active work-item memberships).
- A **phantom** row with the parent id doubled, e.g. `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-PHASE-3-DISPATCH-POLICY-ENGINE` — which currently **holds the live work-item memberships** (e.g. WI-4497/4498/4499 on the Phase-3 phantom; WI-4500–4503 on the Phase-4 phantom).

The existing deterministic service `gt projects reconcile-doubled-prefix` (`groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py`, WI-3355) implements exactly the right reconciliation algorithm (re-link work items to canonical, supersede phantom memberships, retire the phantom project; idempotent on rerun) — but its **detection** is hardcoded to the literal `PHANTOM_PREFIX = "PROJECT-PROJECT-"`, so it does not see the TAFE sub-project phantoms (a dry-run on the current store reports 10 `PROJECT-PROJECT-*` phantoms and **0** of the TAFE-doubled rows).

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` and the tracked-surface bias, this proposal **generalizes the existing service** (rather than authoring a one-shot dedup script): replace the literal-prefix detection with a repeated-leading-segment detector, generalize canonical-id derivation to strip the detected repeated segment, and add a `--project` scope filter so the reconciliation can be applied bounded to one project's phantoms. WI-4511 is then closed by running the generalized service `--project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --apply`, which touches only TAFE rows.

### Bounding (explicit out-of-scope)

- **No cutover / dual-write / live-dispatch substrate / authoritative generated view / KB schema change** — all forbidden by the active tranche-3 PAUTH and not part of this slice. The reconciliation is append-only MemBase **data** reconciliation over existing tables; no DDL.
- **No global apply.** The applied reconciliation is scoped via `--project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`. The 10 pre-existing `PROJECT-PROJECT-*` phantoms (including the non-TAFE `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` with 71 memberships) are deliberately **not** touched by WI-4511; they remain WI-3355's domain. The generalized detector keeps `PROJECT-PROJECT-*` detection working (regression-tested), but a future *global* run is a separate operator action, not part of this slice.
- **No change to the reconciliation algorithm** (re-link / supersede / retire / idempotence / skip-if-canonical-missing). Only detection, canonical derivation, and an optional scope filter change.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — WI-4511 is the backlog authority for this slice; sibling tranche-3 items (WI-4504/4505/4506/4507) and the cutover items (WI-4508/4509/4510) remain out of scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is filed through the file bridge with `bridge/INDEX.md` as the canonical workflow state; the slice writes nothing to, and changes no authority of, the live index at runtime.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under the active bounded PAUTH `...-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED` (owner decision `DELIB-20263164`), which explicitly authorizes "WI-4511 duplicate sub-project-row cleanup; GT-KB platform code/tests only" plus the forthcoming Loyal Opposition GO and implementation-start packet.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the fix extends the existing deterministic reconciliation service (idempotent CLI) rather than performing per-row AI-mediated edits or a throwaway one-shot script; this is the principle's prescribed delivery mechanism.
- `SPEC-TAFE-R7` — the reconciliation is service-mediated and the root `groundtruth.db` remains the canonical store; no markdown or generated view authority is introduced.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs/rules are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project-authorization metadata is present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps the detection generalization, scope filter, no-regression of `PROJECT-PROJECT-*`, idempotence, and the data outcome to executed tests + read-back.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all source, test, and the canonical `groundtruth.db` mutation are inside `E:\GT-KB`; no out-of-root path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the reconciliation preserves the projects/membership audit trail (append-only supersede/retire) and WI-4511 stays unresolved until terminal VERIFIED.

## Prior Deliberations

<!-- Reviewed and pruned by author. -->

- `WI-3355` and `bridge/gtkb-phantom-project-prefix-reconciliation-003.md` (REVISED-1) / `-004.md` (Codex GO) — the original phantom-prefix reconciliation that this proposal generalizes. The reconciliation algorithm (re-link → supersede → retire, idempotent) is carried forward unchanged; only detection/derivation/scope change.
- `DELIB-2505`, `DELIB-2506` — the owner dispositions governing the original reconciliation (canonical re-link disposition, "re-link to retired canonical" for retired-canonical cases). These dispositions are honored unchanged by the generalized service.
- `bridge/gtkb-project-id-prefix-idempotent-fix-005.md` (VERIFIED; commit `281fa28f`) — fixed the source `_project_id_from_names` doubling defect. The TAFE sub-project phantoms are historical artifacts produced before that fix; this slice cleans the residue, it does not re-fix the source generator.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — directs extending the deterministic service over one-shot AI-mediated cleanup.
- `DELIB-20263164` — owner decision backing the tranche-3 PAUTH that includes WI-4511.
- No prior deliberations found specifically for the TAFE sub-project doubled-prefix dedup: `search_deliberations("duplicate sub-project rows projects table backfill dedup TAFE")` and `search_deliberations("phantom project prefix reconciliation doubled prefix WI-3355")` returned no matches on 2026-06-13. This is the first reconciliation of the sub-project doubling manifestation, not a revisit of a rejected approach.

## Owner Decisions / Input

No new owner decision is required to file or implement this proposal.

- **Implementation authority:** the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED`, backed by owner decision `DELIB-20263164`, whose `scope_summary` explicitly authorizes "WI-4511 duplicate sub-project-row cleanup. GT-KB platform code/tests only under E:/GT-KB; bridge/INDEX.md remains canonical; no cutover, no dual-write, no live dispatch substrate."
- **Work selection:** the owner selected WI-4511 as the parallel work track via AskUserQuestion on 2026-06-13 (S438), after this session's dependency verification established that the flow-type track (WI-4500–4503) is owner-gated behind a separate cutover/pilot decision and therefore not cleanly-unblocked.
- The slice stays strictly within the PAUTH's `source`/`test` mutation classes plus append-only MemBase data reconciliation, and within its forbidden-operation bounds (no cutover/dual-write/live-dispatch/generated-view/schema-change). No expanded authorization is requested.

## Requirement Sufficiency

Existing requirements sufficient. The defect (duplicate `projects` rows from the `_project_id_from_names` doubling bug) and the correct disposition (re-link to canonical, supersede phantom memberships, retire phantom project) are already specified by the WI-3355 reconciliation contract (`DELIB-2505`/`DELIB-2506`) and the deterministic-services principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`). No new or revised requirement is needed because this slice generalizes the existing, already-governed reconciliation to a second manifestation of the same defect class and scopes its application; it introduces no new behavior class, schema, or policy.

## Implementation Plan

In `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py`:

1. **Generalize detection.** Replace the literal `PHANTOM_PREFIX = "PROJECT-PROJECT-"` membership test in `_list_doubled_prefix_projects` with a structural detector: a project id is a doubled-prefix phantom iff it has the form `S + S + rest` where `S` is the maximal non-empty leading segment ending in `-` such that `id` starts with `S + S`. The `PROJECT-PROJECT-*` case is the special case `S = "PROJECT-"`; the TAFE sub-project case is `S = "PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-"`. Detection remains guarded by the existing **canonical-must-exist** check (`_plan_one_phantom` already skips with `skip_reason="canonical_missing"`), which protects against false positives on any legitimately repeated-looking id.
2. **Generalize canonical derivation.** Replace `_canonical_id_from_phantom` (which strips a fixed `"PROJECT-"`) with stripping the detected repeated segment `S` (one copy). Preserve the single-strip invariant (a hypothetical triple-doubling reconciles over multiple idempotent rounds, never a greedy collapse). Raise on a non-phantom id as today.
3. **Add a `--project` scope filter.** Extend `ReconcileRequest` with `project_scope: str | None = None`. When set, `_list_doubled_prefix_projects` returns only phantoms whose derived canonical id equals `<project_scope>` or starts with `<project_scope>-` (the project plus its sub-projects). Default `None` preserves the current global behavior (now over the generalized detector).

In `groundtruth-kb/src/groundtruth_kb/cli.py`:

4. Add a `--project TEXT` option to the `reconcile-doubled-prefix` command, threaded into `ReconcileRequest.project_scope`. `--dry-run` default and `--apply`/`--json` semantics are unchanged.

In `platform_tests/scripts/test_cli_projects_reconcile.py`:

5. Add tests against a temp MemBase: (a) canonical-doubling detection for a TAFE-shaped id (`P-<canon>-<canon>-PHASE` → canonical `P-<canon>-PHASE`); (b) `--project` scoping reconciles only in-scope phantoms and leaves out-of-scope `PROJECT-PROJECT-*` phantoms untouched; (c) no-regression: `PROJECT-PROJECT-*` phantoms are still detected and reconciled when in scope/global; (d) re-link + supersede + retire correctness for a sub-project phantom holding work items; (e) idempotence (second `--apply` makes zero writes); (f) false-positive guard (phantom whose canonical is missing is skipped).

Then, as the WI-4511 data cleanup (post-GO, post-impl-start-packet):

6. Run `python -m groundtruth_kb projects reconcile-doubled-prefix --project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --apply`, re-linking the live work-item memberships (WI-4497..4503 and the other TAFE WIs) from the 8 phantom sub-project rows to their canonical sub-projects, superseding the phantom memberships, and retiring the 8 phantom sub-project rows. Append-only; prior versions preserved.

## Spec-Derived Verification Plan

The implementation report must include these commands and observed outcomes:

```text
python -m pytest platform_tests/scripts/test_cli_projects_reconcile.py -q --tb=short
Expected: pass; exercises canonical-doubling detection, --project scoping, PROJECT-PROJECT-* no-regression, re-link/supersede/retire correctness, idempotence, and the canonical-missing skip guard.

python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cli_projects_reconcile.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cli_projects_reconcile.py
Expected: pass.

python -m groundtruth_kb projects reconcile-doubled-prefix --project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Expected (dry-run): 8 TAFE sub-project phantoms planned (Phase-0..Phase-7), with their work-item re-links + membership supersessions; non-TAFE PROJECT-PROJECT-* phantoms absent from the scoped plan.

python -m groundtruth_kb projects reconcile-doubled-prefix --project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --apply
Expected: the 8 TAFE phantoms reconciled; work items re-linked to canonical sub-projects; phantom memberships superseded; phantom projects retired.

python -m groundtruth_kb projects reconcile-doubled-prefix --project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Expected (idempotence re-run): 0 phantoms planned for apply (all reconciled).

python -m groundtruth_kb projects list --project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Expected: no active PROJECT-...-PROJECT-...-PHASE-* doubled rows; canonical sub-project rows now hold the work items.

git diff --check -- groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cli_projects_reconcile.py
Expected: no output, exit 0.
```

Spec mapping:

- `GOV-STANDING-BACKLOG-001` — read-back confirms the TAFE phantom rows are gone and the canonical sub-projects hold the work items; sibling WIs remain open/untouched.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` / `SPEC-TAFE-R7` — the fix is the generalized deterministic CLI service over canonical MemBase; idempotence re-run proves the service-mediated, rerun-safe contract.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each behavior (detection, scoping, no-regression, idempotence, re-link/supersede/retire, false-positive guard) maps to an executed test or read-back above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets under `E:\GT-KB`.

## Risk / Rollback

Primary risk is over-broad detection accidentally matching a legitimate project id with a coincidentally-repeated leading segment. Mitigation: the maximal-`S` detector requires an immediate `S + S` repeat ending in `-`, and the existing **canonical-must-exist** guard skips any candidate whose derived canonical is not a real project; tests include a false-positive guard case.

Secondary risk is regressing the existing `PROJECT-PROJECT-*` reconciliation. Mitigation: a no-regression test asserts those phantoms are still detected/reconciled; `PROJECT-` is just `S` in the generalized detector.

Scope risk (touching non-TAFE phantoms) is eliminated by the `--project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` filter on the applied run; the 71-membership `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` phantom and the other `PROJECT-PROJECT-*` rows are out of scope and untouched.

Rollback before VERIFIED is a normal source/test revert. The data reconciliation is append-only (supersede/retire insert new versions; prior versions preserved), so any mis-link can itself be re-superseded through the same service surface; destructive deletion from `groundtruth.db` is out of scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of a new `gtkb-tafe-subproject-prefix-reconciliation` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

`fix:` — WI-4511 is a backfill **defect** cleanup. The code change (generalized detection + `--project` scope filter) exists solely to let the existing deterministic reconciliation service repair the duplicate-row defect class; it adds no user-facing feature beyond the bugfix surface. The accompanying MemBase data reconciliation is the defect remediation itself.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
