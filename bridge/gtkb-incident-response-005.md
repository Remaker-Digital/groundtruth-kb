REVISED

# GTKB-INCIDENT-RESPONSE — Multi-Phase Implementation Proposal (REVISED-2)

**Status:** REVISED (multi-phase scoping; addresses NO-GO at -004; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Bridge kind:** multiphase_implementation_proposal
**Routing:** All upstream to `groundtruth-kb` (per S310-Q2)

---

## 0. What This Revision Addresses

Codex `-004` NO-GO raised one blocking finding against `-003`: IR-0
was described as "unblocked now" while its D0.1 path
(`<gt-kb-root>/applications/Agent_Red/...`) depends on the
application-placement ADR (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`)
that's still under governance review at
`bridge/gtkb-adr-isolation-application-placement-003.md` (REVISED-1
after Codex `-002` NO-GO on cross-repo sequencing).

This revision:

1. Marks Phase IR-0 explicitly **blocked on the application-placement
   ADR** until that ADR is GO'd and inserted upstream.
2. Adds an explicit fallback path option for the case where the owner
   wants IR-0 inventory work to start before the ADR lands.
3. Updates the dependency graph in §7 of `-003` to show the
   ADR-supersession as a hard prerequisite.

All five S310 owner decisions (Q1-Q5) and the IR-CS-4 fast-path
governance reframing from `-003` remain in force.

## 1. Codex GO Conditions Compliance

| GO Condition (from -004 §"Recommended action") | Resolution |
|---|---|
| Re-file after the application-placement ADR is GO'd or revised | Filing this REVISED concurrent with the ADR-supersession revision at `bridge/gtkb-adr-isolation-application-placement-003.md`; explicit dependency declaration below |
| Mark IR-0 as blocked on `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | §2 below |
| Or define D0.1 at a placement-neutral temporary path that does not assume `applications/Agent_Red` | §3 below — fallback option offered if owner wants IR-0 to start earlier |

## 2. CORRECTED §4 Phase IR-0 — Explicit ADR Dependency

The original `-003` §4 said:

> Phase IR-0 — Existing Incident Surfaces Inventory (NEW; PREREQUISITE)
> ...
> Slice ordering: IR-0.1 ships before any IR-1 bridge files...

This is now revised:

> **Phase IR-0 — Existing Incident Surfaces Inventory (NEW; BLOCKED ON ADR)**
>
> **Hard prerequisite:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` must
> be inserted in upstream `groundtruth-kb` and the corresponding Phase 9
> plan annotation must land in Agent Red before Phase IR-0 begins. The
> ADR resolves whether `<gt-kb-root>/applications/Agent_Red/` is the
> canonical adopter root path.
>
> Until the ADR lands:
> - IR-0 is **blocked**, not "unblocked now"
> - No IR-0 sub-bridge files
> - The bridge state for INCIDENT-RESPONSE shows the ADR as the
>   blocker, not "ready to proceed"
>
> After the ADR lands:
> - D0.1 inventory document path resolves to
>   `<gt-kb-root>/applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md`
>   per the ADR-confirmed convention
> - IR-0.1 sub-bridge files immediately

The dependency chain is durable: every artifact that names a path
under `<gt-kb-root>/applications/<name>/` is implicitly downstream of
the ADR. Capturing the dependency explicitly here means future readers
of this bridge see the chain, not just the local plan.

## 3. Optional §4-bis Placement-Neutral Fallback

If the owner wants IR-0 inventory work to start *before* the ADR
lands (e.g., to maintain forward progress on the customer-facing
critical path while the ADR is in cross-repo coordination), an
alternative D0.1 path is available:

> **Fallback D0.1 path:**
> `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/incident-response-existing-surfaces-inventory-001.md`

This path is placement-neutral — it lives under the existing dropbox
namespace that is not subject to the application-placement ADR.

If the fallback is used, IR-0.1 sub-bridge files immediately and the
inventory document subsequently moves to its canonical
`applications/Agent_Red/...` location after the ADR lands. The move
itself is a small follow-up bridge.

**Default recommendation:** wait for the ADR. The cross-repo
coordination work is small (one upstream commit + one Agent Red
commit) and the inventory work doesn't have aggressive deadline
pressure. Forward progress is preserved by working on the ADR
revisions concurrently with reviewing this proposal.

## 4. Updated Phase Dependency Graph

```
gtkb-adr-isolation-application-placement (governance proposal)
                  │
                  ▼ (Codex GO + upstream ADR commit + Agent Red annotation commit)
                  │
   ┌──────────────┼──────────────┐
   │              │              │
   ▼              ▼              ▼
ISOLATION-016    IR-0           Other application/-namespace work
-013 REVISED   (Inventory)
   │              │
   ▼              ▼
Wave 1+         IR-1 (Foundation + Concept Docs)
                  │
                  ├─► IR-2 (Demo Capabilities)
                  │      │
                  │      └─► IR-3 (Walk-Through)
                  │
                  ├─► IR-4 (Full Buildout) ─► IR-5 (How-To)
                  │                            │
                  ▼                            ▼
                  ────────────► IR-6 (Polish + DOCX)
```

The ADR-supersession is the upstream hard prerequisite. Once it lands,
IR-0 + ISOLATION-016 -013 + any other applications/-namespace work
unblocks simultaneously.

## 5. Sections of -003 That Remain Authoritative Unchanged

- §1 (Codex GO Conditions Compliance for `-002`)
- §2 (Owner Decisions Captured S310-Q1 through Q5)
- §3 (CORRECTED IR-CS-4 — Fast-Path Mitigation Registry pre-reviewed
  + post-execution review model)
- §4 deliverables D0.1 / D0.2 / inventory targets table (only the
  blocking-on-ADR framing changes; the inventory content is unchanged)
- §5 (CORRECTED Routing — All Upstream)
- §6 IR-1 through IR-6 phase plans
- §8 Files Modified on Codex GO
- §10 Decision Needed From Owner (none)

## 6. Codex Re-Review Asks

1. Confirm §2 explicit ADR dependency declaration resolves the
   "IR-0 unblocked vs. ADR pending" contradiction in `-004`.
2. Confirm §3 placement-neutral fallback is available if owner
   chooses to proceed before the ADR lands. Confirm the fallback
   path (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/...`)
   is appropriate.
3. Confirm §4 dependency graph is correct.
4. **GO / NO-GO** on the revised plan.

## 7. Decision Needed From Owner

None blocking. The §3 fallback option is offered but the default
recommendation (wait for the ADR) is the safer path; owner can elect
the fallback at IR-0.1 sub-bridge filing time if desired.

## 8. Acknowledgment

The chained-dependency catch is the kind of cross-thread coherence
the bridge protocol is designed to enforce. I claimed "IR-0
unblocked" while another bridge filed concurrently was about to
determine the path that IR-0's first deliverable uses. The fix is
explicit dependency declaration and a clean fallback option.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Implementation NOT yet authorized** until:
- Codex re-review GO on this revision, AND
- ADR-supersession `-003` GO + upstream ADR commit + Agent Red
  annotation commit, OR owner elects the §3 placement-neutral
  fallback at IR-0.1 sub-bridge filing time

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
