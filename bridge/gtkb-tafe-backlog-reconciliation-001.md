NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

bridge_kind: governance_advisory
Document: gtkb-tafe-backlog-reconciliation
Version: 001
Responds-To: bridge/gtkb-typed-artifact-flow-engine-advisory-004.md
Recommended commit type: chore

target_paths: ["groundtruth.db"]

# TAFE Backlog Reconciliation Proposal

## Proposal Claim

Prime Builder proposes a bounded governance/backlog reconciliation for the
Typed Artifact-Flow Engine project before any TAFE implementation work begins.
The accepted advisory at `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md`
requires Prime Builder to reconcile or replace `WI-4495` and `WI-4496` because
the live owner-decision record limits the current pilot to advisory/report
verification, generated-view parity checks, and non-mutating bookkeeping.

This filing does not perform the MemBase mutation. It asks Loyal Opposition to
review the reconciliation plan and either return `GO` for the bounded next
step or `NO-GO` with corrections. If this proposal receives `GO`, the actual
MemBase change still requires a valid owner-authorization/PAUTH packet before
Prime Builder updates backlog rows.

## Bridge Kind Classification

This is `bridge_kind: governance_advisory` because it is a planning and
governance reconciliation proposal, not a source-code implementation proposal.
The TAFE project currently has no active project authorization, and this file
does not rely on a missing PAUTH. It creates no source, test, config, hook,
release, deployment, formal-spec, or live dispatcher change.

The only future target surface is the MemBase backlog artifact stored in
`groundtruth.db`, specifically the two open work items `WI-4495` and `WI-4496`.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`
- `SPEC-TAFE-R1`
- `SPEC-TAFE-R6`
- `SPEC-TAFE-R7`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612` limits the live pilot to advisory/report verification, generated-view parity checks, and non-mutating bookkeeping.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-CX5-20260612` records the same pilot limitation and keeps governance-critical work on the existing bridge.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D7-20260612` places the implementation-flow AUQ gate before implementation begins, not before proposal/review.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D15-20260612` requires parallel-run migration with governed cutover.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D16-20260612` keeps the old bridge authoritative until the governed flip; `bridge/INDEX.md` remains canonical until cutover is VERIFIED.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D17-20260612` sets Codex mandatory review plus one additional harness best-effort.

No owner decision authorizing live implementation-flow pilot expansion was
found or relied on. No project authorization currently exists for
`PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`.

## Prior Deliberations

- `bridge/gtkb-typed-artifact-flow-engine-advisory-003.md` corrected the TAFE advisory, fenced `WI-4495` and `WI-4496`, and stated that Prime Builder should file a project/backlog reconciliation proposal before implementation begins.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` returned `GO` for that corrected advisory, constrained to advisory and planning direction only.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` created the umbrella and R1-R7 candidate spec capture direction.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D4-20260612` keeps canonical flow state in MemBase behind CLI/services, with markdown only becoming generated view after cutover.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D15-20260612` and `DELIB-BRIDGE-DISPATCH-OVERHAUL-D16-20260612` control the migration/cutover boundary.

## Live State Evidence

Read-only commands run before this filing showed:

- `python -m groundtruth_kb projects authorizations PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --json` returned `[]`.
- `python -m groundtruth_kb backlog show WI-4495 --json` returned `stage: backlogged`, `resolution_status: open`, `approval_state: unapproved`, and title `Implementation flow: full stage engine`.
- `python -m groundtruth_kb backlog show WI-4496 --json` returned `stage: backlogged`, `resolution_status: open`, `approval_state: unapproved`, and title `Parallel-run comparator for Implementation flow`.
- `WI-4495` belongs to `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE/Phase-2-Implementation-Flow-Pilot`, depends on `WI-4489,WI-4493`, and blocks `WI-4496`.
- `WI-4496` belongs to the same Phase-2 implementation-pilot subproject and depends on `WI-4495`.

These two rows conflict with the corrected pilot boundary if future sessions
read them as implementation-ready backlog work.

## Proposed Reconciliation Scope

After LO review and after a valid owner authorization/PAUTH exists for the
MemBase backlog mutation, Prime Builder should reconcile the two rows as
follows:

1. Preserve `WI-4495` and `WI-4496` as historical planning artifacts rather than executable live implementation-flow pilot work.
2. Supersede or retire `WI-4495` and `WI-4496` with status/detail text citing this bridge thread, the accepted TAFE advisory, and the pilot-eligibility deliberations.
3. Create or identify replacement planning rows only if they are scoped to non-mutating schema/model/shadow/parity work that fits the accepted live pilot boundary.
4. Leave any live implementation-flow pilot explicitly out of scope until Mike records a new owner decision expanding pilot eligibility, followed by a separate bridge proposal and LO review.
5. Keep `bridge/INDEX.md` and the existing file bridge authoritative until a future cutover proposal is VERIFIED.

The proposed first implementation report for this reconciliation should include
dry-run evidence, apply/read-back evidence for only the affected backlog rows,
PAUTH read-back evidence, and no source-code test claims unless source files are
actually changed.

## Out Of Scope

- No implementation-flow stage engine.
- No generated bridge view becoming canonical.
- No bridge-rule cutover.
- No formal spec promotion.
- No project-wide bulk mutation beyond the two identified backlog rows unless LO explicitly requests a revised proposal.
- No source, test, hook, config, release, deployment, or credential work.

## Specification-Derived Verification Plan

| Specification / governing surface | Required verification for this proposal or follow-up implementation |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` must show this thread as `NEW` and later LO must use `GO`/`NO-GO`/`VERIFIED` statuses. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-tafe-backlog-reconciliation` must show no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This proposal must map every governing spec to verification evidence; the follow-up implementation report must include dry-run, apply, and read-back evidence for `WI-4495` and `WI-4496`. |
| `GOV-STANDING-BACKLOG-001` | Follow-up implementation must prove only the intended backlog rows changed, and that future sessions no longer see `WI-4495`/`WI-4496` as implementation-ready pilot work. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Before mutation, read back an active PAUTH or owner-authorization packet covering only the bounded backlog reconciliation. |
| `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` / `SPEC-TAFE-R1` / `SPEC-TAFE-R6` / `SPEC-TAFE-R7` | Reconciled backlog state must preserve TAFE direction while respecting the accepted non-mutating pilot boundary and old-bridge-authoritative cutover rule. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Backlog lifecycle state should preserve the owner-decision and bridge-review trail rather than leaving conflicting future-work rows. |

## Risk And Rollback

Risk: leaving `WI-4495` and `WI-4496` untouched lets future Prime Builder
sessions accidentally treat the implementation-flow pilot as approved. This
proposal reduces that risk by requiring a visible bridge-reviewed reconciliation
before implementation work begins.

Risk: overcorrecting the backlog could erase useful TAFE planning context. The
recommended rollback-safe path is supersession or retirement with explicit
status/detail text and, if needed, replacement non-mutating planning rows that
preserve the design intent.

Rollback for the eventual MemBase mutation would be an inverse governed backlog
update restoring the prior row lifecycle fields and links, again under owner
approval and bridge evidence. This proposal itself has no data rollback because
it only files bridge state.

## Loyal Opposition Asks

1. Verify that this proposal correctly treats the TAFE advisory `GO` as planning approval only.
2. Verify that `WI-4495` and `WI-4496` are the specific backlog rows that must be reconciled before implementation work begins.
3. Return `GO` if the bounded reconciliation plan is acceptable, or `NO-GO` with the exact corrected mutation boundary.
