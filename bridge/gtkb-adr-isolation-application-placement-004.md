GO

# ADR-ISOLATION-APPLICATION-PLACEMENT Revised Governance Proposal Review

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-adr-isolation-application-placement-003.md`
**Mode:** Governance proposal re-review
**Decision:** GO

## Verdict

GO for the revised cross-repo sequencing. The `-003` revision fixes the `-002` blocker by separating the upstream `groundtruth-kb` ADR commit from the Agent Red follow-up commit and by requiring the upstream commit hash to be cited by the Agent Red artifacts.

## Evidence

- `bridge/gtkb-adr-isolation-application-placement-003.md` section 2 now places ADR insertion and its formal approval packet in upstream `groundtruth-kb`.
- The Agent Red side is limited to the Phase 9 plan annotation, the ISOLATION-016 `-013` bridge filing, and `bridge/INDEX.md`.
- The revised plan requires capturing the upstream ADR commit hash before Agent Red follow-up work lands.
- Live repo checks from `-002` remain applicable: `E:\GT-KB` and `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` are separate Git repositories with separate remotes.

## GO Conditions

- The upstream `groundtruth-kb` ADR commit must land before the Agent Red commit so the Agent Red artifacts can cite the immutable upstream commit hash.
- Treat section 2 step 5.1 as controlling for the Agent Red side: the Phase 9 annotation, ISOLATION-016 `-013` filing, and `bridge/INDEX.md` update should land together in one Agent Red commit. Do not create a separate annotation-only Agent Red commit from section 2 step 2.2 unless Prime Builder files a revised bridge plan.
- The upstream commit message should cite both the Prime proposal `bridge/gtkb-adr-isolation-application-placement-003.md` and this Codex GO response `bridge/gtkb-adr-isolation-application-placement-004.md`.
- If the formal-artifact approval gate cannot produce or validate the approval packet, stop and re-bridge before inserting the ADR.

## Non-Blocking Notes

- The ADR decision text, rationale, rejected alternatives, and consequences from `-001` remain adequate for the owner-directed Option B path.
- The Phase 9 strikethrough plus `SUPERSEDED-BY` annotation is the right supersession mechanism.
- Keeping the prior Phase 9 plan-review bridge thread VERIFIED remains acceptable because this is a later ADR supersession, not a retroactive correction to that review.

## Verification

Static review plus prior live repository-boundary evidence. No tests were run because this is a governance sequencing proposal.

## Decision Needed From Owner

None. Owner directive S310 supplies the substantive direction; this GO covers the corrected execution sequencing.

