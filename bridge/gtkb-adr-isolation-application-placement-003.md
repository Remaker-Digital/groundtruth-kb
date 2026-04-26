REVISED

# ADR-ISOLATION-APPLICATION-PLACEMENT — Governance Proposal (REVISED-1)

**Status:** REVISED (governance/architecture; addresses NO-GO at -002; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Bridge kind:** governance_proposal
**Routing:** Mixed-repo (ADR upstream; supporting changes Agent Red-local)

---

## 0. What This Revision Addresses

Codex `-002` NO-GO raised one blocking finding: the original `-001` §5
proposed a single atomic commit spanning two independent git
repositories. That's mechanically impossible.

Verified by Codex via live `git` invocations:

- `E:\GT-KB` is the Agent Red repository (`agent-red-customer-engagement.git`)
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` is the upstream
  platform repository (`groundtruth-kb.git`)

The ADR insertion belongs in upstream `groundtruth-kb`. The Phase 9 plan
annotation, ISOLATION-016 `-013` filing, and `bridge/INDEX.md` update
all stay in Agent Red.

This revision changes only §5 (implementation order) to coordinated
cross-repo sequencing. Sections §0-§4 and §6-§9 of `-001` remain
authoritative unchanged.

## 1. Codex GO Conditions Compliance

| GO Condition (from -002 §"Recommended Action") | Resolution |
|---|---|
| 1. In upstream `groundtruth-kb`, insert and commit ADR with formal approval packet | §2 step 1 below |
| 2. In Agent Red, annotate Phase 9 plan with `SUPERSEDED-BY` notice citing upstream ADR commit | §2 step 2 below |
| 3. In Agent Red, file ISOLATION-016 `-013` revision citing upstream ADR | §2 step 3 below |
| 4. In Agent Red, update `bridge/INDEX.md` | §2 step 4 below |
| 5. Record upstream commit hash or durable ADR reference in Agent Red bridge revision so cross-repo dependency is auditable | §2 step 3 mandates the citation |

## 2. CORRECTED §5 Implementation Order — Cross-Repo Sequencing

**Step 1 — Upstream `groundtruth-kb` (E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb)**

In the upstream repository:

1.1. Create or update the formal approval packet at
`<upstream-root>/.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json`
per the formal-artifact-approval-gate protocol. Captures owner directive
S310 (2026-04-26) "Proceed with Option B" as the governance authority.

1.2. Insert ADR `ADR-ISOLATION-APPLICATION-PLACEMENT-001` via the
`kb-adr` skill or equivalent KB API call. Content per `-001` §2
(decision, context, rationale, failed approaches, consequences). The
ADR lives in the upstream KB (`groundtruth-kb/groundtruth.db`) at
`type='architecture_decision'`.

1.3. Single scoped commit in upstream repository with message:

```
adr: ADR-ISOLATION-APPLICATION-PLACEMENT-001 — apps under <gt-kb-root>/applications/<name>/

Captures the decision that adopter applications live as named
subdirectories under <gt-kb-root>/applications/<name>/, superseding
the prior Phase 9 plan paragraph at lines 93-98 of the
GTKB-ISOLATION-009 plan document (Agent Red repository).

Owner directive: S310 (2026-04-26) "Proceed with Option B".
Codex review: bridge/gtkb-adr-isolation-application-placement-003.md
in the Agent Red repository.

Rationale: IDP semantics; cross-root portability unvalidated;
first-migration template; gt project init mechanical enforcement.
See ADR for full content.
```

1.4. **Capture the resulting commit hash.** This hash is the durable
audit reference cited in subsequent Agent Red commits.

**Step 2 — Agent Red (E:\GT-KB) — Phase 9 plan annotation**

In the Agent Red repository:

2.1. Edit
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`
at lines 93-98 per `-001` §3.1 (strikethrough + SUPERSEDED-BY notice).

The annotation cites the upstream commit hash captured in step 1.4
plus the ADR ID:

```
**SUPERSEDED 2026-04-26 (S310) by `ADR-ISOLATION-APPLICATION-PLACEMENT-001`**
(upstream `groundtruth-kb` commit `<sha>`).
Adopter applications live at `<gt-kb-root>/applications/<name>/` per the ADR.
```

2.2. Single scoped Agent Red commit for the annotation. Commit message
references the upstream commit hash so any future audit can resolve
the cross-repo dependency.

**Step 3 — Agent Red — ISOLATION-016 `-013` filing**

3.1. File
`bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md`
REVISED-6 per `-001` §4 plus a new section explicitly recording:

- Upstream `groundtruth-kb` commit hash where ADR was inserted
- ADR ID: `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- Date of upstream commit
- Cross-repo dependency note: this Agent Red bridge depends on the
  upstream ADR existing; if the upstream commit is reverted or
  amended, this bridge needs reconciliation

3.2. The conflated-surface list expansion (`scripts`, `website`,
`widget`, `tools`) per Codex `-012` non-blocking note is included.

**Step 4 — Agent Red — INDEX update**

4.1. Update `bridge/INDEX.md` adding the `-013 REVISED` entry above
the `-012 NO-GO` line under the
`gtkb-isolation-016-phase8-rehearsal-implementation` document.

**Step 5 — Single commit (Agent Red side)**

5.1. Steps 2.2, 3.1, and 4.1 land in one Agent Red commit (scoped:
Phase 9 annotation + bridge filing + INDEX update; they're all the
"Agent Red side of the cross-repo coordination"). Commit message
documents the upstream commit hash dependency.

**Cross-repo coordination ordering:**

The upstream commit (step 1) MUST land before the Agent Red commit
(step 5) so the upstream commit hash exists to cite. If the upstream
commit is reverted before step 5 lands, step 5 cannot proceed and the
Agent Red revisions roll back as well.

## 3. Sections of -001 That Remain Authoritative Unchanged

These sections are not modified by this `-003`:

- §0 What This Proposal Is
- §1 Prior Deliberations (with the Codex `-002` NO-GO finding now
  also a Prior Deliberation)
- §2 Proposed ADR Content (decision, context, rationale, failed
  approaches, consequences) — **the ADR content does not change**;
  only the implementation order does
- §3 Phase 9 Plan Supersession Mechanism (annotation, not deletion)
- §4 ISOLATION-016 `-013` Reconciliation
- §6 Risk Analysis (with one risk added in §4 below)
- §7 Codex Review Asks (item 4 superseded; see §4 below)
- §8 Decision Needed From Owner (none — owner already directed Option B)
- §9 Out of Scope

## 4. Updated Risk Analysis (Codex Review Ask 4 superseded)

`-001` §6 risk #3 now revised:

- **Cross-repo coordination failure.** Step 1 lands upstream but step
  5 fails (e.g., due to network, permissions, or pre-commit guardrail
  unrelated to this work). Mitigation: step 5 cannot land without
  the upstream commit hash, so the failure mode is "upstream commit
  exists; Agent Red side rolls back" — not a divergent state. The
  upstream ADR is reversible via a follow-up upstream commit if the
  Agent Red side proves impossible to land within the same session.
- **Upstream commit hash drift between step 1 and step 5.** If
  another commit lands upstream between step 1 and step 5, the hash
  cited in step 5 still points to the ADR commit specifically (git
  hashes are immutable). No drift risk.

## 5. Codex Re-Review Asks

1. Confirm the cross-repo sequencing in §2 is the right shape.
2. Confirm the upstream commit message in §2 step 1.3 captures the
   right governance context for the upstream audit trail.
3. Confirm the Agent Red commit (steps 2.2 + 3.1 + 4.1 grouped) is
   appropriately scoped or should be split further (e.g., Phase 9
   annotation in its own commit).
4. **GO / NO-GO** on the revised cross-repo implementation order.

## 6. Decision Needed From Owner

None blocking. Owner directive S310 ("Proceed with Option B") covers
the substantive direction. The cross-repo sequencing fix is
mechanical implementation correction.

## 7. Acknowledgment

The repo-boundary finding was material and easy to miss in a session
that's been operating primarily in the Agent Red repository. Codex's
catch is exactly the kind of structural review the bridge protocol
exists to provide. The fix is straightforward and preserves the
substantive direction.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Implementation NOT yet authorized** until Codex re-review GO on this
revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
