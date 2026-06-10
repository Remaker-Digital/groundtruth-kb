REVISED

# New Version of ADR-SINGLE-HARNESS-OPERATING-MODE-001: Harness Registry Architecture (WI-3343)

bridge_kind: prime_proposal
Document: gtkb-adr-harness-registry-extension
Version: 003 (REVISED; addresses NO-GO at -002 — adds the governing mode-switch transaction requirement to the proposal and the planned ADR v2 linkage)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: REQ-HARNESS-REGISTRY-001; DELIB-2079 Q11
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3343
target_paths: [".gtkb-state/adr-drafts/adr-single-harness-operating-mode-001-v2.md", "groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]
Recommended commit type: docs:

## Claim

`ADR-SINGLE-HARNESS-OPERATING-MODE-001` (v1, `architecture_decision`, status `specified`) records GT-KB's operating-mode topology decision: single-harness and multi-harness are both first-class topologies, with role state carried as a role-set list in `harness-state/role-assignments.json`. The Antigravity Integration project has since introduced a harness-registry architecture — a DB-backed `harnesses` table, a generated hot-path projection, a `gt harness` CLI, a four-state lifecycle FSM, and data-driven cross-harness dispatch — that is the storage and lifecycle evolution of that same role model. Per DELIB-2079 Q11, this architecture is recorded by extending the existing ADR with a new version, not by creating a new ADR.

This proposal creates a new version of `ADR-SINGLE-HARNESS-OPERATING-MODE-001` that extends its Decision and Consequences to cover the harness-registry architecture while preserving the v1 role-set topology decision intact. Because an ADR is a formal artifact, the new version is inserted through the governed `gt spec update` path, which writes a formal-artifact-approval packet; the proposed v2 content is presented to the owner for approval before insertion (see Owner Decisions / Input).

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement whose architecture the ADR new version records.
- DELIB-2079 — owner-decided Antigravity Integration design; Q11 decided the architecture is recorded by a new version of this ADR, not a new ADR.
- DELIB-2080 — role-portability amendment (FR9); the registry preserves portable harness-assigned roles.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the existing ADR (v1) this proposal supersedes with a new version.
- GOV-HARNESS-ROLE-PORTABILITY-001 — role portability across harnesses; carried forward into the v2 Spec Linkage.
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 — multi-harness role configuration; carried forward into the v2 Spec Linkage.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 — harness role/topology mutation (the `gt harness set-role` surface the v2 ADR records as governed) is an operating-mode-switch transaction; this spec requires those switch requests to go through a deterministic transaction component with authoritative-artifact/service validation, audit evidence, and session-initialization reading of the transaction result.
- GOV-ARTIFACT-APPROVAL-001 — formal-artifact-approval discipline; the ADR new version requires an owner-approval packet.
- DCL-ARTIFACT-APPROVAL-HOOK-001 — the approval-gate hook contract the `gt spec update` path satisfies.
- GOV-FILE-BRIDGE-AUTHORITY-001 — this work proceeds through the file bridge; `bridge/INDEX.md` remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and decisions (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 — the owner-decided Antigravity Integration design. Q11 explicitly decided "the architecture decisions extend `ADR-SINGLE-HARNESS-OPERATING-MODE-001` via a new version (no new ADR)", rejecting "a new dedicated ADR" and "project plus work-items only with no SPEC/ADR".
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 v1 — the operating-mode topology decision being extended. Its v1 role-set decision, failed approaches, and rejected alternatives are preserved by the new version.
- WI-3337 through WI-3342 (harnesses table, projection, FSM, `gt harness` CLI, role portability, reader migration) — the implementation work the v2 ADR documents at the architecture level.

## Owner Decisions / Input

The Antigravity Integration project and the decision to record its architecture by a new version of this ADR (DELIB-2079 Q11) were owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16. The project is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344).

A second, distinct owner decision is required at implementation time: because the ADR new version is a formal artifact, GOV-ARTIFACT-APPROVAL-001 requires the proposed v2 content to be presented to the owner and explicitly approved before insertion. After Loyal Opposition GO, Prime Builder presents the full proposed v2 ADR text via AskUserQuestion; only on owner approval does the `gt spec update` insertion proceed (the CLI writes the formal-artifact-approval packet with `approved_by=owner`). This proposal being GO'd does not pre-authorize the ADR content; the per-artifact owner approval remains mandatory.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 and DELIB-2079 Q11 govern this work, and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 governs the mode-switch transaction boundary the v2 ADR must carry forward. No new or revised GOV/SPEC/PB/DCL artifact is required before implementation; the ADR new version itself is the artifact this proposal produces, through the governed approval path.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal produces a single new version of one ADR. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is not applicable. The work item cited (WI-3343) is this proposal's own implementing work item under the mandatory project-linkage metadata. The owner-approval packet referenced below is the per-artifact formal-artifact-approval packet for the ADR, not a bulk-action approval.

## Scope

### IP-1: Draft the v2 ADR content

Draft the new ADR version text at `.gtkb-state/adr-drafts/adr-single-harness-operating-mode-001-v2.md`, extending the v1 Decision and Consequences to record the harness-registry architecture:

- The DB-backed `harnesses` table in MemBase as the authority for harness identity, role, lifecycle state, and reviewer precedence.
- The generated hot-path projection (`harness-state/harness-registry.json`) as the derived, non-authoritative read-fast artifact for SessionStart resolution.
- The `gt harness` CLI as the governed mutation surface (register / activate / suspend / resume / retire / set-role / set-precedence / list / show).
- The four-state lifecycle FSM `registered -> active <-> suspended -> retired`, with allowed transitions stated explicitly.
- Data-driven cross-harness dispatch resolving recipients from the registry rather than from hard-coded per-harness branches.
- The mode-switch transaction boundary: the v2 ADR must explicitly state that harness role/topology mutation (the `gt harness set-role` surface) is an operating-mode-switch transaction and still goes through the deterministic transaction component per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 — or through a named successor service providing equivalent authoritative-artifact/service validation, audit evidence, and effective-state (session-initialization) semantics. Recording the registry table and CLI must not imply they are sufficient by themselves; the transaction validation/audit/effective-state contract is preserved.

The v1 role-set topology decision, its failed approaches, and its rejected alternatives are preserved unchanged. New Failed Approaches / Rejected Alternatives entries explain why a generated projection is preferred over reading the table on every hot path, and why a DB-backed table supersedes the file-based `harness-state/*.json` authority. Spec Linkage is extended with GOV-HARNESS-ROLE-PORTABILITY-001, GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001, REQ-HARNESS-REGISTRY-001, and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

### IP-2: Present the v2 content for formal-artifact approval

After Loyal Opposition GO, present the full proposed v2 ADR text to the owner via AskUserQuestion for formal-artifact approval per GOV-ARTIFACT-APPROVAL-001 and DCL-ARTIFACT-APPROVAL-HOOK-001. Implementation does not proceed without explicit owner approval of the content.

### IP-3: Insert the new version through the governed path

On owner approval, insert the new version with `gt spec update --id ADR-SINGLE-HARNESS-OPERATING-MODE-001 --content-file .gtkb-state/adr-drafts/adr-single-harness-operating-mode-001-v2.md --change-reason <reason> --owner-presented --approved-by owner`. The `gt spec update` path self-writes the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/<date>-ADR-SINGLE-HARNESS-OPERATING-MODE-001-v2.json` with the required fields and a `full_content_sha256` matching the inserted content.

### IP-4: Verify the new version

Confirm: the ADR is retrievable at the incremented version; the live version's content matches the approval packet's `full_content_sha256`; the v1 role-set topology decision text is preserved in v2; the v2 text explicitly records the mode-switch transaction boundary for role/topology mutation; and the doctor's harness/role-set checks still pass after the ADR update.

## Out Of Scope

- Changing the v1 role-set topology decision (preserved verbatim in v2).
- Implementing the harness-registry components themselves (WI-3337 through WI-3344, separate threads) — the v2 ADR records the architecture; it does not build it.
- Any artifact outside the E:\GT-KB project root. All artifacts produced — the v2 ADR row in `groundtruth.db`, its formal-artifact-approval packet, and the transient draft content-file — are within E:\GT-KB.

## Files Expected To Change

- `.gtkb-state/adr-drafts/adr-single-harness-operating-mode-001-v2.md` — the transient v2 content draft consumed by `gt spec update --content-file`.
- `groundtruth.db` — the new append-only `ADR-SINGLE-HARNESS-OPERATING-MODE-001` version row.
- `.groundtruth/formal-artifact-approvals/` — the formal-artifact-approval packet written by `gt spec update`.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 / DELIB-2079 Q11 | Content review confirms the v2 ADR records the registry architecture (table, projection, CLI, FSM, data-driven dispatch); `get_spec` retrieval confirms the new version is live. |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | Content review of the inserted v2 ADR confirms it explicitly records that harness role/topology mutation (the `gt harness set-role` surface) still goes through the deterministic transaction component — or a named successor service providing equivalent validation, audit, and effective-state semantics — so the registry table/CLI are not implied to be sufficient by themselves. |
| GOV-ARTIFACT-APPROVAL-001 / DCL-ARTIFACT-APPROVAL-HOOK-001 | The formal-artifact-approval packet exists with `presented_to_user=true`, `approved_by=owner`, and a `full_content_sha256` matching the inserted ADR content. |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 v1 preservation | A diff/assertion confirms the v1 role-set topology decision text is present unchanged in v2. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed verification commands and observed results. |

Implementation verification will run:
- `gt spec update ... --dry-run` (packet validation without write) prior to the live insert.
- A `get_spec` retrieval of `ADR-SINGLE-HARNESS-OPERATING-MODE-001` confirming the incremented version and content.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-harness-registry-extension`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-harness-registry-extension`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] The proposed v2 ADR content is presented to the owner and explicitly approved via AskUserQuestion before insertion.
- [ ] The new ADR version is inserted through `gt spec update` with a valid formal-artifact-approval packet.
- [ ] The v1 role-set topology decision is preserved unchanged in v2.
- [ ] The v2 ADR records the registry architecture (table, projection, `gt harness` CLI, FSM, data-driven dispatch).
- [ ] The v2 ADR records the mode-switch-transaction boundary for harness role/topology mutation per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 (the `gt harness set-role` surface goes through the deterministic transaction component, or a named successor service with equivalent validation/audit/effective-state semantics).
- [ ] The doctor's harness/role-set checks pass after the ADR update.
- [ ] Post-implementation report carries observed verification results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this draft before the live REVISED INDEX entry is inserted, and re-run against the indexed operative file after filing.

Observed results (run against this REVISED draft, prior to INDEX insertion):

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:0203a73d96939270789de690a480b1254f324dd15a73de88155dc2e941a89984`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0` across 5 must_apply clauses.

## Risk And Rollback

**Risk R1 (medium): the v2 ADR drops or alters v1 content.** A new version that loses the v1 role-set decision would silently weaken the architecture record. Mitigation: IP-1 explicitly preserves v1 text; IP-4 asserts the v1 decision text is present in v2; append-only versioning keeps v1 retrievable regardless.

**Risk R2 (low): approval-packet / content mismatch.** The packet's `full_content_sha256` could drift from the inserted content. Mitigation: `gt spec update` computes the SHA from the same content it inserts; the `--dry-run` validates the packet before the live write.

**Risk R3 (low): the v2 content overclaims implemented capability.** The ADR could describe registry components as complete when some are still in flight. Mitigation: the v2 text distinguishes implemented from intended surfaces, consistent with the operating-model implemented-vs-intended discipline.

Rollback: append-only versioning means v1 remains the prior retrievable version; a corrective new version supersedes a flawed v2 rather than rewriting history. The transient draft content-file can be discarded with no effect on canonical state.

## Response to NO-GO (-002)

The `-002` review issued NO-GO with one finding:

**F1 (P1) — The proposal omits the governing mode-switch transaction requirement.** The reviewer observed that the planned v2 ADR records `gt harness` (including `set-role`) as the governed mutation surface and supersedes file-based `harness-state/*.json` role authority, yet the proposal did not cite `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` in `Specification Links`, did not name it in the planned v2 ADR Spec Linkage, and did not map it to verification. Because `gt harness set-role` and role/topology mutation are operating-mode-switch transactions, an ADR recording the registry as the architecture for harness role authority must carry the deterministic-transaction validation/audit/effective-state boundary forward.

Resolution in this REVISED `-003`:

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` is added to the proposal's `## Specification Links` section, with the reason that harness role/topology mutation is an operating-mode-switch transaction governed by this spec.
- IP-1 now extends the planned ADR v2 Spec Linkage with `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` (alongside GOV-HARNESS-ROLE-PORTABILITY-001, GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001, and REQ-HARNESS-REGISTRY-001).
- IP-1's description of the v2 ADR content delta now states the v2 must explicitly record that harness role/topology mutation goes through the deterministic transaction component per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 — or a named successor service with equivalent validation/audit/effective-state semantics — and that recording the registry table/CLI must not imply they are sufficient by themselves.
- The `## Spec-To-Test Mapping` adds a row for `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`: the inserted v2 ADR must, by content review, explicitly record that harness role/topology mutation still goes through the deterministic transaction component (or a named successor service providing equivalent validation/audit/effective-state semantics).
- IP-4 verification now confirms the v2 text explicitly records the mode-switch transaction boundary for role/topology mutation.
- A new acceptance-criteria checkbox requires the v2 ADR to record the mode-switch-transaction boundary for harness role/topology mutation per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

No other findings were raised; the reviewer's Non-Blocking Confirmations (ADR-as-new-version correctly implements DELIB-2079 Q11; the IP-2 post-GO owner-approval boundary is correct; the root boundary is satisfied) are preserved unchanged in this revision.

## Loyal Opposition Asks

1. Confirm that recording the registry architecture as a new version of the existing ADR (rather than a new ADR) correctly implements DELIB-2079 Q11.
2. Confirm the IP-2 owner-approval step (AskUserQuestion presentation of the full v2 content post-GO) satisfies GOV-ARTIFACT-APPROVAL-001 for this proposal.
3. Confirm the addition of SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 to the proposal's Specification Links, the planned v2 ADR Spec Linkage, the Spec-To-Test Mapping, and the acceptance criteria fully addresses F1 from the -002 NO-GO.
4. Confirm the verification plan is adequate for an ADR artifact, or recommend additional checks.
