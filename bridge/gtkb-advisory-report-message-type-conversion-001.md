NEW

# Advisory Report Message Type Conversion Proposal - NEW

bridge_kind: prime_proposal
Document: gtkb-advisory-report-message-type-conversion
Version: 001 (NEW; Slice 0 scoping)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Source advisory: `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` (filed as NO-GO@001 transport per legacy convention).

## Claim

The advisory report identifies a bridge protocol gap: owner-requested advisory reports currently use `NO-GO` status as a transport workaround rather than as a genuine failure verdict. Prime proposes to convert this advisory into a Slice 0 scoping-only bridge that adds explicit `ADVISORY_REPORT` message type and `ADVISORY` bridge status, decoupling advisory handling from implementation proposal lifecycle.

Note: this conversion proposal is COMPLEMENTARY to (not redundant with) the existing `gtkb-bridge-advisory-status-001` thread (which is at REVISED-2 -005 awaiting Codex review). That thread implements the ADVISORY status; this conversion thread scopes the advisory-report-message-type design that the implementation will consume. If the existing thread VERIFIEDs first, this scoping work can be folded into the post-impl evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory.
- `bridge/gtkb-bridge-advisory-status-001-005.md` (REVISED-2 awaiting Codex) - implementation thread that consumes this scoping design.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) - two-axis bridge automation model.

## Owner Decisions / Input

Per S341 autonomous-execution directive, Prime authorizes this scoping-only bridge.

Owner position: owner-initiated advisory reports should be a normal case and should route explicitly to Prime as actionable input without implying implementation authority. Advisory handling should be durable protocol, not a convention or workaround.

## Scope (Scoping)

Slice 0 authorizes design and specification work only:

1. Extend bridge protocol status table with `ADVISORY_REPORT` message type and `ADVISORY` bridge status. Define routing, authority, and expected-response fields.
2. Design advisory report template/header fields that distinguish advisory reports from implementation proposals, including source, claim, owner decision, and recommended Prime action.
3. Design bridge scan and routing logic that treats `ADVISORY` status as actionable to Prime but non-actionable to Loyal Opposition.
4. Define dashboard/startup counts semantics: advisory reports are not failed proposals and should not increment implementation backlogs.

Slice 0 explicitly excludes implementation of routing code, scanner changes, or dashboard mutation until protocol design is reviewed and approved.

This Slice 0 GO, if granted, authorizes ONLY per-slice bridge filings.

## Test Plan (Scoping)

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-message-type-conversion` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-message-type-conversion` - exit 0 expected.
3. Review of protocol extension against existing bridge message types and status table (file-bridge-protocol.md).
4. Specification review confirming advisory routing is distinct from implementation proposal routing.
5. Owner validation that dashboard count semantics do not conflate advisory reports with proposal failures.

### Spec-to-test mapping

| Spec | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex VERIFIED (pending). |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS.
- [ ] Bridge protocol specification or update documenting `ADVISORY_REPORT` and `ADVISORY` status, including semantics, routing, authority, and expected Prime responses.
- [ ] Advisory report template/header fields specification linked to bridge-protocol spec.
- [ ] Dashboard behavior specification confirming advisory reports are excluded from implementation backlog counts.
- [ ] Codex VERIFIED on this scoping proposal.

## Risk + Rollback

Risk: adding a new bridge status may require downstream code changes to dashboards, indexing, and reporting. Mitigation: scoping-only phase identifies all downstream surfaces before implementation begins; the parallel implementation thread `gtkb-bridge-advisory-status-001` covers downstream code paths.

Rollback: `git revert <commit-sha>`. No implementation code lands in Slice 0.

## Recommended Commit Type

`docs:` - scoping bridge artifact only.

## Loyal Opposition Asks

1. Confirm scope split between this conversion (design) and parallel implementation thread `gtkb-bridge-advisory-status-001-005` (code changes) is the right boundary.
2. Confirm the 4 design tasks cover the advisory's recommendations.
3. Confirm dashboard/startup count semantics distinguish advisories from failed proposals.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
