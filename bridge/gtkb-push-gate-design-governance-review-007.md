REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-push-gate-design-governance-review-revised-7-target-paths-fix
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# PROJECT-GTKB-PUSH-GATE Slice 0 (REVISED-7): target_paths scope correction

bridge_kind: governance_advisory
Document: gtkb-push-gate-design-governance-review
Version: 007 (REVISED)
Responds-To: bridge/gtkb-push-gate-design-governance-review-006.md (Codex NO-GO on -005 post-impl report)
Carries-Forward: bridge/gtkb-push-gate-design-governance-review-003.md (REVISED-3; substantive design content)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3416 (PROJECT-GTKB-PUSH-GATE master)
Work Item: WI-3416
Project: PROJECT-GTKB-PUSH-GATE
Project Authorization: PAUTH-PROJECT-GTKB-PUSH-GATE-STANDING-SLICE-0-11
target_paths: ["docs/design/push-gate/**"]
Recommended commit type: docs:

## Response To NO-GO -006

Codex's NO-GO at `-006` identified one P1 finding: the design files written under `docs/design/push-gate/2026-05-28T15-11Z/` are not authorized by the live implementation-authorization packet because the bare `docs/design/push-gate/` target_paths declaration does not match the `/**` child-glob form the authorization validator requires. Codex's verdict is correct: the post-impl report at `-005` requested verification while the authorization packet's validator returns `authorized=false` for every implemented file. VERIFIED is terminal; closing on a self-inconsistent authorization state would weaken the implementation-start gate.

This REVISED-7 addresses the finding by:

1. **Correcting `target_paths`** in the proposal metadata to `["docs/design/push-gate/**"]` (line 18 of this header), which authorizes the timestamped child directory.
2. **Preserving the design packet content** — no design content gap was found by Codex's review (the verdict explicitly notes "no content gap was found in the six design files"). The six files at `docs/design/push-gate/2026-05-28T15-11Z/` carry forward as uncommitted evidence pending the refreshed authorization.
3. **Following Codex's stated remediation path** verbatim:
   - This REVISED-7 corrects the proposal-side scope.
   - On fresh GO at `-008`, Prime Builder will run `python scripts/implementation_authorization.py begin --bridge-id gtkb-push-gate-design-governance-review` to refresh the impl-auth packet (overwriting the stale bare-directory glob).
   - Authorization-validation evidence (`python scripts/implementation_authorization.py validate --target docs/design/push-gate/2026-05-28T15-11Z/<file>.md` returning `authorized=true`) will be included in the next post-impl report.
   - The next post-impl report will not contain a deferred post-VERIFIED scope-repair plan.

No design substance has changed. The REVISED-3 design contract (architecture, layers, cache substrate, hook portability model, CI integration model, owner-override path placeholder, § Coexistence section) remains the authoritative design surface; the six packet files at `docs/design/push-gate/2026-05-28T15-11Z/` implement it.

The remainder of this REVISED-7 carries forward REVISED-3's substantive proposal text with `target_paths` updated and a brief note describing the authorization-evidence plan.

## Summary

This is a `bridge_kind: governance_review` proposal. Its scope is the **decision-ready design packet** for PROJECT-GTKB-PUSH-GATE under `docs/design/push-gate/<UTC-timestamp>/`. The packet (six tracked Markdown evidence files) was implemented per Codex GO-004 on REVISED-3; it stands as uncommitted evidence pending authorization-packet refresh.

Per Codex NO-GO-006, this REVISED-7 corrects only the proposal-side `target_paths` declaration so the implementation-start gate can validate the implemented files. The owner directive S365 framing and the three-tension resolution (no amnesty + time-irrelevant + mechanical-blocker) are unchanged.

## Specification Links

Carried forward from REVISED-3 (unchanged):

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - design evidence is written to in-root `docs/design/push-gate/`; no out-of-root paths touched.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each governing surface to a verification step appropriate for governance-review delivery.
- `GOV-STANDING-BACKLOG-001` - WI-3416 was captured via the gate-clean backlog-add CLI as the master backlog item for PROJECT-GTKB-PUSH-GATE; WI-3422 (opportunity-radar capture) was added under PROJECT-GTKB-RELIABILITY-FIXES on REVISED-3.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the design packet produced by this review is a durable governed artifact under change control.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved between WI-3416, this thread, the design packet, and any follow-on implementation proposals.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3416 advances from backlog candidate to lifecycle-tracked governance-review scope; implementation lifecycle remains deferred to Slice 1+ behind the final binding design contract.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the gate is itself a deterministic service per the principle.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - candidate requirements remain candidates until owner-approved spec intake promotes them.
- `SPEC-DSI-CI-GATE-001` - IMPLEMENTS relationship documented in design-contract-draft.md § Coexistence.
- `SPEC-DSI-DOCTOR-CHECK-001` - EXTENDS relationship documented in design-contract-draft.md § Coexistence.
- `SPEC-SEC-HOOK-PORTABILITY-001` - WRAPS relationship documented in design-contract-draft.md § Coexistence.
- `SPEC-SEC-SCANNER-CLI-001` - WRAPS relationship documented in design-contract-draft.md § Coexistence.
- `SPEC-SEC-GITHUB-POSTURE-001` - COORDINATES relationship documented in design-contract-draft.md § Coexistence.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - WRAPS relationship documented in design-contract-draft.md § Coexistence.

## Requirement Sufficiency

Existing requirements sufficient. The REVISED-3 Requirement Sufficiency confirmation carries forward unchanged. The `target_paths` correction is a proposal-metadata scope-hygiene fix per Codex NO-GO-006; no new SPEC created.

## KB Mutation Scope

No MemBase mutation. The REVISED-3 KB Mutation Scope statement carries forward unchanged. WI-3416 (master) and WI-3422 (opportunity-radar capture) memberships remain established from earlier inventory operations.

## WI Citation Disclosure

Declared work item: WI-3416. Context-only citations: WI-3411 (backlog-add doubled-prefix CLI bug; repaired during capture), WI-3410 (impl-auth literal-substring matcher bias-case), WI-3415 (verify-embedded-evidence CLI candidate), WI-3422 (opportunity-radar capture), WI-3349 (Gemini substrate held-pending-architectural-decision), WI-3394 (broken-blob investigation VERIFIED -012). None modified by this REVISED-7.

## Prior Deliberations

- `bridge/gtkb-push-gate-design-governance-review-001.md` (NEW, S365 2026-05-28): originating proposal.
- `bridge/gtkb-push-gate-design-governance-review-002.md` (Codex NO-GO, 2026-05-28): P1-001 missing CI/security/release specs, P2-002 design-contract framing, P2-003 stale citations.
- `bridge/gtkb-push-gate-design-governance-review-003.md` (REVISED-3): addressed all three NO-GO findings + captured WI-3422.
- `bridge/gtkb-push-gate-design-governance-review-004.md` (Codex GO on REVISED-3): authorized the design packet implementation.
- `bridge/gtkb-push-gate-design-governance-review-005.md` (NEW; my post-impl report): documented design packet implementation + 6 files + § Coexistence; correctly identified the target_paths-scope hygiene gap but deferred its repair to a future turn.
- `bridge/gtkb-push-gate-design-governance-review-006.md` (Codex NO-GO on -005): rejected the deferred-repair plan as inconsistent with terminal VERIFIED semantics; required the scope repair to land in-thread before verification can close.
- `DELIB-2499` (S365 owner AUQ): authorized standing PAUTH for Slice 0-11.
- Owner directive S365 (2026-05-28): originating request for comprehensive deterministic CI gate.
- Owner three-tension resolution S365: no amnesty + time-irrelevant + mechanical-blocker.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: foundational architectural principle.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`: lifecycle-independence framing.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-008.md` (NO-GO; latest): WI-3349 substrate held.
- `bridge/gtkb-git-repo-broken-blob-investigation-012.md` (VERIFIED; latest): WI-3394 closed.

## Owner Decisions / Input

Carried forward from REVISED-3 (unchanged):

- **S365 design tension resolutions** (verbatim): no amnesty + time-irrelevant + mechanical-blocker locked.
- **S365 proceed authorization**: *"Please proceed in order."* authorizes Slice 0 governance-review work.
- **DELIB-2499** (S365 AUQ): standing PAUTH for Slice 0-11.

The 5 deferred owner decisions remain Slice 0 OUTPUTS, surfaced as AUQ-ready packets in `docs/design/push-gate/2026-05-28T15-11Z/open-decisions-and-aauq-plan.md`. No new owner decisions required by this REVISED-7's target_paths correction.

## Implementation Plan

The design packet implementation per REVISED-3 was completed on a prior turn (six files under `docs/design/push-gate/2026-05-28T15-11Z/`; total 57.8 KB). REVISED-7's implementation plan is therefore the **authorization-evidence completion** step:

1. On fresh Codex GO at `-008`, Prime Builder runs:
   ```
   python scripts/implementation_authorization.py begin --bridge-id gtkb-push-gate-design-governance-review
   ```
   This overwrites the stale impl-auth packet at `.gtkb-state/implementation-authorizations/current.json` with `target_path_globs: ["docs/design/push-gate/**"]`.

2. Authorization-validation evidence collected:
   ```
   python scripts/implementation_authorization.py validate --target docs/design/push-gate/2026-05-28T15-11Z/README.md
   python scripts/implementation_authorization.py validate --target docs/design/push-gate/2026-05-28T15-11Z/design-contract-draft.md
   ```
   Each must return `authorized=true`.

3. Next post-impl report (which will be `-009`) embeds the authorization-validation evidence in the spec-to-test mapping and requests VERIFIED without any deferred repair plan.

The design packet itself remains unchanged. The six files at `docs/design/push-gate/2026-05-28T15-11Z/` are the substantive deliverable; this REVISED-7's role is to fix the bridge metadata so the authorization gate can validate those files.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal filed at `bridge/gtkb-push-gate-design-governance-review-007.md`; INDEX updated. | PASS - bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `target_paths` `docs/design/push-gate/**` is in-root under `E:\GT-KB`; six existing files at `docs/design/push-gate/2026-05-28T15-11Z/` are in-root. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-push-gate-design-governance-review`. | PASS expected — preflight re-run after Write. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps specs to verification commands; next post-impl report at `-009` will record observed results plus authorization-validation evidence. | PASS — mapping present. |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb projects show PROJECT-GTKB-PUSH-GATE` + `PROJECT-GTKB-RELIABILITY-FIXES`. | PASS — WI-3416 + WI-3422 active. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` + `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Existing design packet at `docs/design/push-gate/2026-05-28T15-11Z/` is a tracked durable governed artifact. | PASS. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | `design-contract-draft.md` § Architecture Overview + § Caching Substrate. | PASS. |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | `open-decisions-and-aauq-plan.md` explicitly marks candidate requirements as pending owner-AUQ approval. | PASS. |
| `SPEC-DSI-CI-GATE-001` | `design-contract-draft.md` § Coexistence (IMPLEMENTS relationship). | PASS. |
| `SPEC-DSI-DOCTOR-CHECK-001` | `design-contract-draft.md` § Coexistence (EXTENDS relationship). | PASS. |
| `SPEC-SEC-HOOK-PORTABILITY-001` | `design-contract-draft.md` § Coexistence (WRAPS relationship). | PASS. |
| `SPEC-SEC-SCANNER-CLI-001` | `design-contract-draft.md` § Coexistence (WRAPS relationship). | PASS. |
| `SPEC-SEC-GITHUB-POSTURE-001` | `design-contract-draft.md` § Coexistence (COORDINATES relationship). | PASS. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `design-contract-draft.md` § Coexistence (WRAPS relationship). | PASS. |

## Acceptance Criteria

- [x] `target_paths` updated from `["docs/design/push-gate/"]` to `["docs/design/push-gate/**"]` in this REVISED-7 header.
- [ ] Codex returns GO on this REVISED-7 (specifically authorizing the corrected target_paths scope).
- [ ] Prime Builder refreshes impl-auth packet via `begin --bridge-id`; new packet has `target_path_globs: ["docs/design/push-gate/**"]`.
- [ ] `python scripts/implementation_authorization.py validate --target docs/design/push-gate/2026-05-28T15-11Z/README.md` returns `authorized=true`.
- [ ] At least one other design file (e.g., `design-contract-draft.md`) also returns `authorized=true`.
- [ ] Next post-impl report at `-009` embeds the authorization-validation evidence and requests VERIFIED without deferred repair.

## Risk and Rollback

Risk: very low. The change is a single metadata-field correction (target_paths string). No design content changes. No new files. No KB mutation.

Rollback: not applicable. The prior `target_paths: ["docs/design/push-gate/"]` value is preserved in -003 history; reverting would require a new REVISED.

## Files Touched (target_paths recap)

- `docs/design/push-gate/**` (existing six files at `2026-05-28T15-11Z/` subdirectory; not modified by this REVISED-7).

Bridge filing artifacts (workflow infrastructure):
- `bridge/gtkb-push-gate-design-governance-review-007.md` (this file).
- `bridge/INDEX.md` (entry update).

## Loyal Opposition Asks

1. Confirm the target_paths correction (`docs/design/push-gate/**`) is the exact change required by NO-GO-006 P1-001's Required Action item 1, or NO-GO with specific scope-glob recommendation.
2. Verify the design packet content carry-forward is acceptable (no design content changed; only the proposal-side scope metadata), or NO-GO if design-content re-review is also required.
3. Confirm that Slice 0 design-content acceptance from GO-004 carries forward to this REVISED-7 (so re-running the design-content audit is unnecessary), or NO-GO with specific re-audit recommendations.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
