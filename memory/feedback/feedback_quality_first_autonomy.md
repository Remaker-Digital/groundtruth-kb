---
name: Quality-first autonomy on scope/effort/quality decisions
description: When a decision relates to scope/effort/quality and the options differ on quality or completeness, proceed autonomously with the maximum-quality option. Do not wait for owner input unless no option is clearly superior.
type: feedback
originSessionId: 1e7d9156-bb2f-4a35-837e-7615cd417206
---
**Rule:** When presenting decisions to the owner, elevate them visibly (not buried in chat prose). When the options differ on scope, effort, or quality grounds, **proceed autonomously with the most comprehensive, complete, and correct option.** Do not wait for owner input unless no option is clearly distinguished by superior quality or completeness. Owner explicitly does not care about time, effort, or scope expansion; quality and completeness are overriding concerns.

**Why:** Owner-decisions were being lost in the flow of the chat text during long bridge-protocol sessions. Rather than force the owner to re-surface each decision thread, Prime should make the max-quality call and proceed. Stated explicitly as an owner directive on 2026-04-18 late in session S301, after E1 Prepare VERIFIED surfaced two pending owner decisions (clean-tree strategy + per-file-skip mechanism) that the owner had not responded to across ~20 polling ticks.

**How to apply:**
- When drafting a bridge proposal with open questions: propose the max-quality option as the recommendation, not a neutral tree. Only leave truly symmetric options open.
- When executing the bridge protocol and hitting a decision fork that could block progress: **make the max-quality decision and document it inline** rather than wait.
- When decisions DO need owner input (e.g., values not derivable from technical merit — approvals for destructive ops, GOV-16 production gates, external-communication content, anything that commits the business): **elevate the decision explicitly** with a numbered bullet or bolded block at the top of the response, not paragraph-buried.
- Reserve "waiting for owner" for: truly-symmetric-on-quality choices, destructive operation approvals, production-gate approvals, external-facing communications, or anything the bridge protocol flags as owner-only.

**Scope boundary:** This applies to *how Prime operates within already-approved scope*. It does NOT override the codex-review-gate rule (every implementation still needs a bridge proposal) or the GOV-16 production deployment gate. Quality-first autonomy means Prime picks the max-quality path within the bridge protocol, not that Prime bypasses the bridge protocol.
