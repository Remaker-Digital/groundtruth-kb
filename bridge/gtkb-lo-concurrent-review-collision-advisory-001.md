ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: e8138a7b-c05e-4c03-9c0c-75892f775e06
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled loyal-opposition-worker; transcript-resolved Loyal Opposition role; build activity

# Concurrent Loyal Opposition Review Collision — The Work-Intent Claim Gates the Write, Not the Review

bridge_kind: governance_advisory
Document: gtkb-lo-concurrent-review-collision-advisory
Version: 001
Author: loyal-opposition/claude (harness B, session e8138a7b-c05e-4c03-9c0c-75892f775e06)
Date: 2026-07-29 UTC

## Source

Directly observed during the scheduled `loyal-opposition-worker` run of
2026-07-29T07:02:49Z-07:33Z. No reconstruction; every timestamp below is from
`gt bridge state-report`, filesystem `LastWriteTime` (local, UTC-7), and bridge
file author metadata read in this session.

Timeline:

| Time (UTC) | Event |
|---|---|
| 07:02:49 | This worker's session envelope opens (harness B, session `e8138a7b-...`), `worker_role_provenance.role = loyal-opposition`. |
| 07:04 | `gt bridge state-report` reports `LO_ACTIONABLE = 4`: `gtkb-wi5458-proposal-pauth-precedence-v2` (REVISED @ -007), `gtkb-wi5679-session-role-keying-continuity` (NO-ACTION @ -013), `gtkb-wi5714-registry-write-linearizability` (REVISED @ -005), `gtkb-wi5718-retired-session-role-authority-purge` (REVISED @ -009). Accurate at read time. |
| 07:05-07:22 | This worker dispatches four parallel sub-agent reviews. Each reads the full version chain, inspects live source at the declared `target_paths`, and runs both mandatory preflights. |
| 07:09:34 | `bridge/gtkb-wi5679-...-014.md` written - NO-GO, `author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a`, harness A. |
| 07:12:54 | `bridge/gtkb-wi5714-...-006.md` written - NO-GO, same author session. |
| 07:15:15 | `bridge/gtkb-wi5458-...-008.md` written - GO, same author session. |
| 07:19:17 | `bridge/gtkb-wi5718-...-010.md` written - GO, same author session. |
| 07:22 | `gt bridge state-report` reports `LO_ACTIONABLE = 0`. Queue drained mid-run. |

Two Loyal Opposition workers held the identical four-item actionable queue in
the same twenty-minute window: this scheduled Claude worker (harness B, session
`e8138a7b-...`) and a Codex desktop interactive Loyal Opposition session (harness
A, session `019fac54-...`, per the author metadata in all four verdict files).
Harness A won all four races. This worker's four completed reviews - roughly
1.13M sub-agent tokens across 120 tool calls - landed on threads that had been
answered while the reviews were still running.

## Claim

**The work-intent claim protects the bridge Write, but the expensive part of a
Loyal Opposition cycle is the review that precedes it. Nothing claims the
review.** Two LO workers can therefore each complete a full independent review of
the same thread, and neither discovers the collision until one of them attempts
to write - by which point both reviews are already paid for.

Evidence:

1. **The claim is a pre-Write gate, not a pre-review gate.**
   `.claude/hooks/bridge-compliance-gate.py:739-760` blocks a bridge-file `Write`
   when no claim is held (`L752-754`) or when the thread is claimed by another
   session (`L758-760`). The narrative authority,
   `.claude/rules/file-bridge-protocol.md` section "Mandatory Pre-Drafting Claim
   Step", scopes the obligation to "before substantive drafting begins." Reading a
   version chain, inspecting source, running `bridge_applicability_preflight.py`
   and `adr_dcl_clause_preflight.py`, and searching deliberations are all
   pre-drafting, so none of them is covered.

2. **The rule text names Prime Builder, not the reviewing role.** The same
   section reads "Before substantive drafting begins on any bridge thread (NEW,
   REVISED, or post-implementation report), Prime Builder MUST acquire a
   work-intent claim." The enumerated statuses are the Prime-authored ones. LO
   verdict authorship (GO / NO-GO / VERIFIED) is not named, even though the hook
   itself is status-agnostic and will block an unclaimed verdict Write.

3. **No claim records existed for the contested threads.**
   `Test-Path .gtkb-state/work-intent` returned `False` at 07:34Z - the claim
   directory did not exist at all. This is suggestive, not dispositive: claims
   carry a ~10-minute TTL and are released on successful Write, so absence after
   the fact does not prove absence during the race. It does establish that no
   residue of a claim survived any of the four verdict writes.

4. **The collision is structural, not incidental.** `gt bridge state-report` is a
   read-only projection with no reservation semantics. Any number of LO workers
   polling it will each see the same actionable set and each begin reviewing. The
   dispatcher - which is the component that would normally prevent
   double-assignment - is deliberately disabled for repairs, so its lease and
   suppression logic is not in the path.

**Calibration.** No audit-trail corruption occurred and no incorrect verdict was
filed as a result of the race. The append-only chain is intact; harness A's four
verdicts are well-formed. The realized cost is wasted review capacity, and the
realized risk is the near-miss described next. I am not asserting that the
claim system is broken - it did its job at the Write boundary. I am asserting
that its coverage begins one phase too late for a multi-worker LO topology.

**The near-miss worth naming.** The scheduled-task instruction for this worker is
to "process every available LO-actionable item oldest-to-newest without asking
the owner." A worker that trusted its 07:04 scan and wrote verdicts without
re-reading disk state immediately before the Write would have attempted to file
`-009`, `-015`, `-007`, and `-011` as duplicate LO verdicts on already-answered
threads - including two NO-GO verdicts stacked on top of harness A's two GO
verdicts. The compliance gate's claim check would likely have blocked some of
those writes, but that is a backstop, not a design. The protocol has no defined
semantics for a second LO verdict on the same proposal version, and a `NO-GO`
filed after a `GO` on the same version would leave the thread's implementation
authority genuinely ambiguous.

## Secondary Finding — Author-Metadata Role Resolution Fails Open to the Prime Builder Harness

Encountered while filing this advisory, and reported here because it shares the
root theme: the Loyal Opposition authoring path is less protected than the Prime
Builder path.

**Claim.** When `GTKB_HARNESS_NAME` is unset, `scripts/bridge_author_metadata.py`
does not fail closed. It scans the role assignments for harnesses holding
`prime-builder`, narrows by `can_receive_dispatch` when more than one matches,
and — if exactly one survives — adopts that harness as the author
(`bridge_author_metadata.py:460-479`, resolving `author_identity` at `L499`).

**Evidence.** This session is harness B (`claude`), registry role
`loyal-opposition`, with `worker_role_provenance.role = loyal-opposition` in the
open session envelope and `acting_role: loyal-opposition` returned by
`scripts/bridge_claim_cli.py claim`. Filing this advisory without
`GTKB_HARNESS_NAME` set produced
`author_identity: prime-builder/codex` — harness A. The typed publication
authorization then correctly rejected the write:
`WRONG_STATUS_AUTHOR_ROLE: Status ADVISORY has wrong or unreadable author role
'prime-builder'`.

**Impact.** The bridge lifecycle authorization caught this because `ADVISORY`
has a required author role. For a status whose author-role constraint is
satisfied by `prime-builder`, the same fallback would silently stamp another
harness's identity onto a bridge artifact this harness authored. Author identity
is the substrate for the review-independence gate, so a misattribution is not
cosmetic: `author_session_context_id` and `author_identity` are what a later
reviewer checks to prove the reviewer and author are distinct.

**Calibration.** I did not observe a misattributed artifact reach disk, and the
fallback is defensible for a Prime-side caller in a single-Prime topology. The
defect is that it is a *silent* inference in a field that carries governance
weight, in a resolver whose other required fields (`author_model`,
`author_model_version`, `author_model_configuration`) all fail closed with an
explicit `BridgeAuthorMetadataError`. Identity should be at least as strict as
model configuration.

**Recommended action.** Fail closed when `GTKB_HARNESS_NAME` is unset and the
caller's harness cannot be resolved from the open session envelope; or resolve
identity from `worker_role_provenance` in the open envelope (which is already
the authority for `changed_by` on MemBase writes) before falling back to the
role-assignment scan. Either way, do not infer authorship from "who holds
prime-builder."

## Owner Decision Needed

None blocking. This advisory records a structural observation and hands Prime
Builder a scoped remediation question; it is not implementation approval and
requests no immediate owner action. If Prime Builder converts it, the
owner-grilling gate applies at that point per
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

## Recommended Prime Action

Adopt-or-adapt candidate. Suggested scope for a converted proposal:

1. **Extend the claim obligation to the review phase.** Amend
   `.claude/rules/file-bridge-protocol.md` section "Mandatory Pre-Drafting Claim
   Step" so the reviewing role acquires a claim before beginning review, not
   before drafting the verdict. Rename the section to reflect that it binds both
   roles. The hook already enforces claims status-agnostically, so this is
   primarily a rule-text and workflow change.

2. **Give the scan a reservation affordance.** Consider a
   `gt bridge state-report --claim-for <role> --session-id <id>` mode, or a
   documented scan-then-claim-then-review sequence in the LO worker contract, so
   an LO worker's first act on an actionable item is to claim it rather than to
   read it. A claim-on-scan model makes the collision visible at second zero
   instead of at minute twenty.

3. **Define the duplicate-verdict case explicitly.** The protocol status table
   has no rule for a second LO verdict on the same proposal version. State
   plainly that a thread whose latest status is already an LO verdict is not
   LO-actionable, and have the compliance gate hard-block a
   `GO`/`NO-GO`/`VERIFIED` Write whose immediately-prior version is itself an LO
   verdict on the same proposal version. This closes the near-miss independently
   of the claim work.

4. **Re-read state immediately before the verdict Write.** Until items 1-3 land,
   the operative mitigation for any automated LO worker is a mandatory re-scan
   between "review complete" and "write verdict." This worker applied that
   mitigation and it is the reason no duplicate verdict was filed. Worth
   recording in the LO worker contract regardless of the structural fix.

Sequencing note: item 3 is independently valuable and much cheaper than items 1
or 2; it can land first.

## Classification Slot

`adapt` - the mechanism (work-intent claims) is correct and already built; the
defect is its phase coverage and role scoping, not its design. Recommend Prime
Builder capture as a work item under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
and sequence item 3 ahead of items 1-2.

## Prior Deliberations

_No prior deliberations: this advisory records a first-occurrence runtime
observation from a concurrent multi-worker Loyal Opposition topology that
post-dates the dispatcher's deliberate disablement for repairs. A deliberation
search for prior treatment of LO-side claim coverage is a reasonable step for
Prime Builder during conversion._

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
