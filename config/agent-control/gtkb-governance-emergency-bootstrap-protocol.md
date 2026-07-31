# Governance Emergency-Bootstrap Exception Protocol

This rule auto-loads via the `.claude/rules/` convention. It defines the narrow,
audit-disciplined exception path for repairing foundational governance
infrastructure when the normal bridge protocol cannot run because the defect
being repaired *is* the infrastructure the protocol depends on.

## Authority and Scope

Source: WI-4458 (`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`); owner authorization
`DELIB-20266267`; governed by `GOV-FILE-BRIDGE-AUTHORITY-001` (audit-trail and
bridge discipline) and `GOV-ARTIFACT-APPROVAL-001` (retroactive owner-approval
capture).

This protocol generalizes the `bridge-essential.md` mandate — "restoring bridge
function is always the top-priority task" — from the bridge specifically to
other foundational governance subsystems: registered hooks, governance gates,
and the work-intent claim system. It is an exception class, not a general
license: every clause below narrows when a bypass is permitted and requires the
bypass to leave a durable, owner-visible audit trail.

## The Deadlock This Protocol Addresses

The normal bridge protocol is:

> Prime files NEW → Loyal Opposition GO → Prime implementation-start packet →
> Prime commit → Prime files post-impl NEW → Loyal Opposition VERIFIES.

That protocol cannot run when the defect being repaired is the very
infrastructure the protocol depends on. The motivating incident (WI-4449, commit
`e90b2f03`, `fix: restore registered governance hooks`): six governance hooks
were registered in `.claude/settings.json` but their on-disk `.py` files were
never committed. The pre-commit verify path itself invokes registered hooks
(scan-secrets, dev-environment-inventory-drift, narrative-artifact-evidence,
ruff-format). Restoring the hooks required a commit, but the verify path required
the hooks to exist — a chicken-and-egg deadlock. The verify-hook bypass used to
land that commit was the correct call, but it was an undocumented exception
class. This protocol canonicalizes it.

## (a) Sanctioned Conditions

A verify-hook bypass and/or a bridge-`GO`-bypass is sanctioned ONLY when ALL of
the following hold:

1. A foundational governance subsystem is broken in a way that produces a
   session-block or an active failure: a registered hook file is missing on
   disk, a governance gate cannot load, or the work-intent claim system cannot
   operate.
2. The normal bridge protocol path is itself blocked by the very defect being
   repaired (e.g., the verify path requires the artifact being committed, or
   the gate that would review the change is the gate being repaired).
3. The change is the minimal repair that restores the foundational subsystem.
   Scope creep beyond the minimal restoration is NOT covered by this exception
   and must follow the normal bridge protocol.

If any condition is not met, the normal bridge protocol applies and the bypass
is NOT sanctioned.

## (b) After-Action Audit-Trail Entry (Required)

After the emergency-bootstrap commit lands, the actor MUST file an after-action
bridge entry with status `WITHDRAWN` that records:

- the commit SHA of the emergency-bootstrap repair;
- the deadlock rationale (which condition in (a) was met and why the normal path
  was blocked);
- the scope of the minimal repair; and
- counterpart (Loyal Opposition) verification evidence that the repair is
  correct.

Precedent: `bridge/gtkb-commit-untracked-governance-hooks-002.md` (the WI-4449
closure) is the canonical example of this after-action entry. The `WITHDRAWN`
status marks the entry as an audit record rather than an actionable proposal in
the queue, while preserving it permanently in the append-only bridge audit
trail.

## (c) Retroactive Owner-Approval Capture (Required)

If owner approval for the emergency-bootstrap action was not already on record at
the time of the action, the actor MUST capture it retroactively as a
Deliberation Archive owner-decision record (`source_type=owner_conversation`,
`outcome=owner_decision`) per `GOV-ARTIFACT-APPROVAL-001`. The deliberation cites
the commit SHA and the after-action `WITHDRAWN` bridge entry, closing the
formal-approval invariant even though the action itself preceded approval.

## What This Protocol Does NOT Permit

- It does not permit bypassing the bridge for ordinary feature work, defect
  fixes, or refactors that are unrelated to restoring a broken foundational
  subsystem.
- It does not permit skipping the after-action `WITHDRAWN` entry or the
  retroactive owner-approval capture.
- It does not weaken the credential-scan or root-boundary invariants; those
  remain in force during an emergency-bootstrap action.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
