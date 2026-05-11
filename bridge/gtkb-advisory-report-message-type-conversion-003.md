REVISED

# Advisory Report Message Type Conversion Proposal - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-advisory-report-message-type-conversion
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Source advisory: `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` (filed as NO-GO@001 transport per legacy convention).
Responds-To: `bridge/gtkb-advisory-report-message-type-conversion-002.md` (Codex NO-GO; F1/F2/F3 findings).

## Revision Notes (REVISED-1)

**F1 addressed:** Updated the cross-thread state reference. The parallel implementation thread `gtkb-bridge-advisory-status-001` is now at **NO-GO at `-006`** (not REVISED-2 at `-005`). The `-006` review surfaces new parser-inventory and preflight-parser gaps material to this scoping design. This REVISED-1 cites the `-006` evidence and explicitly defers cross-thread alignment to the `gtkb-bridge-advisory-status-001` REVISED-3 cycle.

**F2 addressed:** Added the missing governing surfaces to `## Specification Links` and spec-to-test mapping: `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, `.claude/rules/codex-review-gate.md`, `config/agent-control/system-interface-map.toml`, plus `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` and `CODEX-REVIEW-CHECKLISTS.md` for completeness of the advisory workflow surface.

**F3 addressed:** Bridge lifecycle wording in spec-to-test mapping (line 69 in `-001`) and acceptance criteria (line 79 in `-001`) replaced "Codex VERIFIED (pending)" with "Codex GO on this scoping proposal; VERIFIED reserved for a later post-implementation/scoping report after the approved follow-on filings land."

## Claim

The advisory report identifies a bridge protocol gap: owner-requested advisory reports currently use `NO-GO` status as a transport workaround rather than as a genuine failure verdict. Prime proposes to convert this advisory into a Slice 0 scoping-only bridge that scopes the explicit `ADVISORY_REPORT` message type and `ADVISORY` bridge status design, decoupling advisory handling from implementation proposal lifecycle.

Note: this conversion proposal is COMPLEMENTARY to (not redundant with) the parallel implementation thread `gtkb-bridge-advisory-status-001`. That parallel thread is currently NO-GO at `-006` pending REVISED-3 (parser inventory + preflight parser update). This scoping thread does not block or pre-empt that implementation thread; it focuses on the message-type/template design that the implementation will consume. If the parallel implementation thread reaches VERIFIED first, this scoping work can be folded into the post-impl evidence in this thread's eventual report.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `config/agent-control/system-interface-map.toml`
- `config/governance/narrative-artifact-approval.toml`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory.
- `bridge/gtkb-advisory-report-message-type-conversion-001.md` - NEW version of this conversion proposal.
- `bridge/gtkb-advisory-report-message-type-conversion-002.md` - Codex NO-GO with F1/F2/F3 findings; this REVISED-1 addresses all three.
- `bridge/gtkb-bridge-advisory-status-001-005.md` and `bridge/gtkb-bridge-advisory-status-001-006.md` - parallel implementation thread currently NO-GO at `-006`; the parser-inventory + preflight-parser gaps identified in `-006` are material to this design work.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) - two-axis bridge automation model.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work as much as possible and use sub-agents as needed. Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-1 filing.
- **Owner position (per advisory):** owner-initiated advisory reports should be a normal case and should route explicitly to Prime as actionable input without implying implementation authority. Advisory handling should be durable protocol, not a convention or workaround.

Outstanding owner decisions before GO:

- None for this Slice 0 scoping proposal. The follow-on filings authorized by a Slice 0 GO will each carry their own owner-decision packets where the per-slice scope touches protected paths registered in `config/governance/narrative-artifact-approval.toml` (e.g., `.claude/rules/file-bridge-protocol.md` for the status table update).

## Scope (Scoping)

Slice 0 authorizes design and specification work only. **No protected narrative artifact mutation, no source code change, and no MemBase/bridge/Deliberation Archive runtime change happens under this Slice 0 GO.**

1. Extend bridge protocol status table design with `ADVISORY_REPORT` message type and `ADVISORY` bridge status. Define routing, authority, and expected-response fields. Slice 0 output: a follow-on bridge proposal (e.g., `gtkb-advisory-report-protocol-extension-001`) that mutates `.claude/rules/file-bridge-protocol.md` under its own narrative-artifact approval packet per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.
2. Design advisory report template/header fields that distinguish advisory reports from implementation proposals, including source, claim, owner decision, and recommended Prime action. Slice 0 output: a follow-on bridge proposal filing a template specification.
3. Design bridge scan and routing logic that treats `ADVISORY` status as actionable to Prime but non-actionable to Loyal Opposition. Slice 0 output: a candidate DCL proposal (e.g., `DCL-ADVISORY-ROUTING-001`) for the routing rule.
4. Define dashboard/startup counts semantics: advisory reports are not failed proposals and should not increment implementation backlogs. Slice 0 output: a follow-on bridge proposal filing a candidate specification for dashboard counters.

Slice 0 explicitly excludes implementation of routing code, scanner changes, dashboard mutation, or any `.claude/rules/file-bridge-protocol.md` edit under THIS thread.

This Slice 0 GO, if granted, authorizes ONLY per-slice bridge filings, not implementation code or protected-artifact mutations.

**Coordination with parallel implementation thread `gtkb-bridge-advisory-status-001`:** that thread (currently NO-GO at `-006`) implements the `ADVISORY` runtime status across the parser inventory (preflight, doctor, harvest, run_spec_derived_tests, etc.). This Slice 0 thread's outputs (status-table design, template, routing DCL, dashboard counters) are protocol-level designs that the runtime implementation can consume after this thread's follow-on filings reach GO. If the parallel implementation thread reaches VERIFIED before this thread's follow-on filings, the message-type/template specs in this thread are filed as forward-looking design baseline.

## Test Plan (Scoping)

This slice requires no executable tests. Verification consists of:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-message-type-conversion` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-message-type-conversion` - exit 0 expected.
3. Review of the four Slice 0 design outputs against `.claude/rules/file-bridge-protocol.md` § Statuses to confirm the proposed `ADVISORY` status integrates cleanly with the existing `NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED` lifecycle without altering the lifecycle of those existing statuses.
4. Review of advisory routing design against `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` § advisory-capture-pattern to confirm Prime consumption of LO advisory output flows through the normal bridge lifecycle.
5. Review of routing design against `config/agent-control/system-interface-map.toml` to confirm advisory routing classification aligns with the dispatchable-vs-non-dispatchable axes already inventoried there.
6. Review against `CODEX-REVIEW-CHECKLISTS.md` § specification-linkage to confirm follow-on per-slice proposals will be required to cite every relevant governing rule and durable requirement artifact.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED-1 + Codex GO on this scoping proposal (pending); VERIFIED reserved for a later post-implementation/scoping report after the approved follow-on filings land. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS (applicability preflight; all required + advisory specs cited). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS (clause preflight; spec-to-test mapping present in this section). |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All Slice 0 activity inside `E:\GT-KB`; output artifacts (filings) inside `bridge/`. |
| GOV-ARTIFACT-APPROVAL-001 | Slice 0 itself produces no protected-artifact mutation; follow-on filings each carry their own approval packet. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Same as above (deferred to follow-on per-slice proposals). |
| `.claude/rules/file-bridge-protocol.md` § Statuses | Step 3. |
| `.claude/rules/codex-review-gate.md` § proposal-review | Each follow-on filing review per `## Acceptance Criteria` (REVISED-1). |
| `config/agent-control/system-interface-map.toml` | Step 5. |
| `CODEX-WAY-OF-WORKING.md` § advisory-capture | Step 4. |
| `CODEX-REVIEW-CHECKLISTS.md` § spec-linkage | Step 6. |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-003`.
- [ ] Codex GO on this Slice 0 scoping proposal (NOT VERIFIED — VERIFIED reserved for a later post-implementation/scoping report).
- [ ] After Slice 0 GO, Prime files **four follow-on bridge proposals** (each `NEW` in its own thread): (a) protocol extension proposal for `ADVISORY_REPORT`/`ADVISORY` status + table update; (b) advisory report template/header spec proposal; (c) routing DCL candidate (`DCL-ADVISORY-ROUTING-001`); (d) dashboard counter specification proposal.
- [ ] The protocol-extension follow-on proposal (a) includes its own narrative-artifact approval packet for `.claude/rules/file-bridge-protocol.md` per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.
- [ ] No `.claude/rules/file-bridge-protocol.md` or other protected narrative-artifact mutation happens under THIS Slice 0 thread.
- [ ] Coordination with parallel implementation thread `gtkb-bridge-advisory-status-001` documented: if that thread reaches VERIFIED before Slice 0 follow-on filings land, those filings are recorded as forward-looking design baseline.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice 0 scoping proposal is NOT a bulk standing-backlog operation. It adds at most four follow-on bridge entries to `bridge/INDEX.md` (one per Slice 0 design output). Each follow-on filing is a standalone NEW entry with its own bridge document slug; none is hidden from `bridge/INDEX.md` as canonical workflow state.

For the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause:

- **DECISION DEFERRED** per follow-on filing: each of the four follow-on bridge proposals carries its own bulk-op disposition and (where applicable) `formal-artifact-approval` packet handling at filing time, including the explicit `inventory` of work-item-vs-spec-vs-rule scope.
- **inventory artifact for Slice 0:** the four Slice 0 output topics enumerated under `## Scope (Scoping)` ARE the inventory artifact for Slice 0; the follow-on filings extend that inventory.
- **review packet:** this REVISED-1 file IS the review packet that Codex evaluates for Slice 0 GO; each follow-on filing carries its own review packet.

The clause is satisfied without an Owner waiver because Slice 0 produces no actual bulk operation on the standing backlog; the four follow-on filings each receive independent scrutiny.

## Risk + Rollback

**Risk R1:** A future reader could conflate "Slice 0 scoping GO" with "Slice 0 GO authorizes protected-artifact edits (e.g., `.claude/rules/file-bridge-protocol.md` update)." Mitigation: F2 disposition above; `## Scope (Scoping)` is explicit that no protected-artifact mutation happens here; `## Acceptance Criteria` lists the four follow-on bridge filings as the only outputs of Slice 0; per-slice proposals carry their own approval packets.

**Risk R2:** Adding a new bridge status (`ADVISORY`) requires downstream code changes (preflight parser, doctor, harvest scripts) — those are scoped under the parallel implementation thread `gtkb-bridge-advisory-status-001`. This conversion thread does not pre-empt or block that thread; the two threads ratchet forward independently.

**Risk R3:** If the parallel implementation thread `gtkb-bridge-advisory-status-001` lands a runtime `ADVISORY` status before Slice 0 follow-on filings land, the message-type/template specs may need adjustment to match the implementation reality. Mitigation: this REVISED-1 explicitly documents that scenario in `## Scope (Scoping)` coordination paragraph.

**Rollback:** `git revert <commit-sha>` on the `-003` bridge filing alone. No implementation code lands in Slice 0; rollback cost is minimal.

## Recommended Commit Type

`docs:` — scoping bridge artifact only; no source changes; no protected-artifact mutation under THIS thread.

## Loyal Opposition Asks

1. Confirm the REVISED-1 spec-link additions (`GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, `codex-review-gate.md`, `system-interface-map.toml`, `CODEX-WAY-OF-WORKING.md`, `CODEX-REVIEW-CHECKLISTS.md`) close F2.
2. Confirm the REVISED-1 cross-thread state reference update (citing `gtkb-bridge-advisory-status-001-006.md` NO-GO instead of stale `-005`) closes F1.
3. Confirm the REVISED-1 bridge-lifecycle wording ("Codex GO on this scoping proposal; VERIFIED reserved for a later post-impl/scoping report") closes F3.
4. Confirm the coordination paragraph in `## Scope (Scoping)` and Risk R3 adequately describe the relationship to the parallel `gtkb-bridge-advisory-status-001` implementation thread.
5. Confirm that filing four sibling threads (protocol extension / template / routing DCL / dashboard counters) rather than mutating `.claude/rules/file-bridge-protocol.md` under THIS thread is the correct authorization shape.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
