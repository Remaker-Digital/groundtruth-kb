REVISED

# Revised Proposal - Control-Plane Placeholder-Test Remediation Slice 1 (read-only inventory, re-scoped to governance review)

bridge_kind: governance_review
Document: gtkb-control-plane-placeholder-test-remediation-slice-1-revert
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-004.md (NO-GO)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 4a09ec70-04a7-4cda-babc-998de47942f3
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, 1M context

Work Item (context only): WI-3184
target_paths: []

implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Revision Claim

This revision responds to the NO-GO at `-004`, which found the `-003`
`scoping_proposal` missing implementation-start metadata (F1), a
`## Requirement Sufficiency` section (F2), and a `## Prior Deliberations`
section (F3). `-004` F1 explicitly offered, as an alternative to adding
project-authorization metadata, re-scoping the thread "into one of the
recognized non-implementation bridge kinds without file writes."

This `-005` takes that path. It re-scopes Slice 1 from a file-writing
`scoping_proposal` (which would create `scripts/audit_control_plane_spec_evidence.py`,
its test, and a report — a `source-file-creation`/`test-creation` mutation
requiring WI-3184 to be covered by a project authorization) into a
**`governance_review`** that delivers the read-only evidence inventory **as the
proposal's own content**. No source, test, report, `.gtkb-state`, or
`groundtruth.db` artifacts are created (`target_paths: []`), so the
project-metadata gate's non-implementation exemption applies and no project
authorization / WI-3184 PAUTH coverage is required.

The owner authorized this re-scope (DECISION-0937, 2026-06-03). The reusable
inventory script + the source/UI/API implementation-evidence dimension are
deferred to a Slice 2 that, being file-writing, will require an active project
authorization covering WI-3184 with `source-file-creation`/`test-creation`
classes.

## Read-Only Evidence Inventory (Slice 1 deliverable)

Computed read-only from the live `groundtruth.db` `specifications` and `tests`
tables on 2026-06-03 (latest version per id; linked-test count = distinct
current `tests.id` whose latest version has `spec_id = <spec>`):

| Spec | Title (abbrev) | Current lifecycle status | Current KB linked tests |
|---|---|---|---|
| SPEC-1816 | Superadmin Entitlement Management API | implemented | 0 |
| SPEC-1818 | SPA Console: Full Service Management | implemented | 0 |
| SPEC-1819 | SPA Console: Code-Free Runtime Configuration | implemented | 0 |
| SPEC-1820 | Allow/Block List Management | implemented | 0 |
| SPEC-1821 | Back-off and Retry Configuration | implemented | 0 |
| SPEC-1822 | Alert Threshold Configuration | implemented | 0 |
| SPEC-1823 | Notification Channel Configuration | implemented | 0 |
| SPEC-1824 | Feature Flag System | implemented | 0 |
| SPEC-1826 | SPA Test Execution Trigger | implemented | 0 |
| SPEC-1827 | Diagnostic Data Export for Claude Code | implemented | 0 |

### Inventory findings

1. **All 10 control-plane cluster specs are at `implemented`, not `verified`.**
   The verified→implemented correction that motivated the original WI-3184 is
   already reflected in current MemBase state; no lifecycle downgrade is
   outstanding for these 10 ids on the KB-status axis.
2. **All 10 have zero current KB test linkage.** This confirms the WI-3184 root
   cause (S198 GOV-12 placeholder test rows recycled by S200 for real
   SPEC-1837 log-retention tests, per `DELIB-0772`), and is consistent with the
   `-002`/`-003` finding that zero linkage makes `verified` unsafe while not, by
   itself, disproving `implemented`.
3. **Slice 1 conclusion:** the KB-side evidence gap is fully characterized
   (10/10 specs `implemented` + 0 linked tests). What this inventory does **not**
   establish — and what a later slice must — is the source/UI/API
   implementation-evidence dimension that would decide whether `implemented`
   remains justified or whether test-remediation (re-linking real tests) is the
   correct correction. That dimension requires reading Agent Red product source
   and authoring a reusable audit script, which is file-writing work for Slice 2.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this revision uses the live bridge thread and converts the rejected file-writing scope into a reviewable non-implementation governance review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing specification is cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the inventory exists because lifecycle status and test linkage must be evidence-aligned; it documents the linkage gap rather than asserting verification.
- `GOV-STANDING-BACKLOG-001` — WI-3184 remains the standing-backlog context; this revision performs no bulk transition and no WI closure.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — no files are written; the only artifact is this in-root bridge document.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the evidence inventory is captured as a durable governance artifact before any lifecycle mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle transitions require explicit evidence and confirmation flow; this slice supplies the evidence only.
- `SPEC-1816`, `SPEC-1818`, `SPEC-1819`, `SPEC-1820`, `SPEC-1821`, `SPEC-1822`, `SPEC-1823`, `SPEC-1824`, `SPEC-1826`, `SPEC-1827` — target specs inventoried (read-only).
- `.claude/rules/file-bridge-protocol.md`; `.claude/rules/project-root-boundary.md` — live `bridge/INDEX.md` is workflow authority; all artifacts are in root.

## Prior Deliberations

- `DELIB-0770` — bridge thread `spec-hygiene-spa-remediation`, latest VERIFIED; prior remediation for the verified-to-implemented correction (Option A source for WI-3184).
- `DELIB-0772` — bridge thread `spec-hygiene-spa-investigation`, latest VERIFIED; established the recycled placeholder test IDs that are this cluster's root cause.
- `DELIB-1282`, `DELIB-1283` — orphan/duplicate harvest records for the same investigation/remediation threads (context; superseded views).
- `DELIB-2208` — SPA cluster test-ID investigation closure (S350 closure context).

No prior deliberation rejects a read-only inventory-first slice; the inventory-first-then-mutation sequence is the precedent path (cf. the SPA hygiene investigation→remediation ordering).

## Requirement Sufficiency

**Existing requirements sufficient.** This is a read-only governance inventory
that creates no source, test, configuration, deployment, repository-state, or
KB-mutation artifacts. The governing requirements
(`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` for evidence-aligned
lifecycle, `GOV-STANDING-BACKLOG-001` for WI-3184 context, and the prior SPA
hygiene deliberations) are sufficient to characterize the linkage gap. No new
or revised requirement is needed for this slice. Any subsequent lifecycle
correction or test-remediation slice is separate work that must capture its own
requirement-sufficiency state and project authorization.

## Specification-Derived Verification Plan

This slice authors no implementation, so it derives no implementation tests; its
verification is the **reproducibility of the read-only inventory**. The mapping
below ties each governing clause to a concrete, re-runnable verification.

| Specification / clause | Verification (read-only) | Expected |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lifecycle status and test linkage must be evidence-aligned) | Re-run the documented read-only query against live `groundtruth.db`: latest-version `status` per spec, and `COUNT(DISTINCT id)` of current `tests` whose latest version has `spec_id = <spec>`, for the 10 target ids. | All 10 = `implemented` / `0` linked tests (matches the inventory table). |
| Read-only / no-mutation invariant (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `target_paths: []`) | `git status --short` after this proposal; confirm the only change is this bridge document and that no `specifications`/`tests` rows were inserted (no new version rows for the 10 ids). | Only `bridge/...-005.md` (+ INDEX) present; no spec/test version inserts. |
| Coverage (all 10 specs) | Confirm the inventory table enumerates exactly SPEC-1816, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1826, 1827. | 10/10 present; fail-closed if any missing. |

No spec-derived implementation tests are created or required, because this slice
makes no implementation claim — it records evidence. Any subsequent slice that
re-links tests or corrects lifecycle status must supply its own spec-derived
tests and verification under its own authorization.

## Owner Decisions / Input

- **DECISION-0937 (owner AUQ, 2026-06-03):** owner greenlit revising #4
  control-plane now — "re-scope to read-only inventory + add the 3 missing
  sections." This `-005` implements that decision: re-scope to `governance_review`,
  deliver the inventory as content, and add the `Requirement Sufficiency` and
  `Prior Deliberations` sections the `-004` NO-GO required.
- No further owner decision is requested by this proposal. (The deferred
  file-writing Slice 2 will require an owner project-authorization decision for
  WI-3184 before it can be filed; that is out of scope here.)

## Findings Addressed (from NO-GO -004)

- **F1 (implementation-start metadata absent):** Closed by re-scoping to
  `governance_review` with `target_paths: []` — a recognized non-implementation
  bridge kind, exempt from the project-metadata gate per `-004` F1's own stated
  alternative. No `Project Authorization`/`Project`/`Work Item` implementation
  metadata is required because no implementation (file write / KB mutation) is
  requested.
- **F2 (missing Requirement Sufficiency):** Closed — see `## Requirement
  Sufficiency` above (`Existing requirements sufficient`).
- **F3 (missing Prior Deliberations):** Closed — see `## Prior Deliberations`
  above, citing `DELIB-0770`, `DELIB-0772`, `DELIB-1282`, `DELIB-1283`,
  `DELIB-2208`.

## Requested Loyal Opposition Disposition

Review this as a non-implementation governance review delivering the Slice-1
read-only evidence inventory. A `GO` accepts the inventory as the durable
Slice-1 artifact and acknowledges that any lifecycle correction, reusable audit
script, or source/UI/API evidence dimension is deferred to a separately
authorized Slice 2. No implementation-start packet, file write, or KB mutation
is requested by this proposal.

## Recommended Commit Type

`docs` — this thread's only artifact is this governance-review bridge document;
no source/test/config change accompanies it.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
