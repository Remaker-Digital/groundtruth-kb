ADVISORY
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dbc5c1cd-13f2-4ff8-81a5-a80c06799bae
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: governance_advisory
Document: gtkb-wi5677-begin-commit-after-report-nogo-gap
Version: 001
Author: Prime Builder (Claude) — owner-directed advisory; advisories are role-agnostic per DELIB-202667454
Date: 2026-07-24

## Source

Session dbc5c1cd-13f2-4ff8-81a5-a80c06799bae (2026-07-24), Prime Builder (Claude).
Work Item: WI-5677 (origin=defect, priority P2, component=bridge-runtime).
Owner directive (2026-07-24): "Add defect candidate WI to the bridge as Advisory
Proposals." Owner decision: DELIB-202667454 (Advisory Proposals are
role-agnostic). Adjacent prior deliberations: DELIB-202666252 (WI-5249 Prime
NO-ACTION Claim/Filer), DELIB-202665620 (WI-4853 session-role marker claim
eligibility).

## Claim

`implementation_authorization.py begin` refuses to authorize a commit for a
bridge thread whose proposal was GO'd but whose latest status is a report-level
NO-GO — defeating the "commit under the existing GO, then re-report" remediation
that a Loyal Opposition report-NO-GO itself directs.

Evidence (session dbc5c1cd), thread `gtkb-wi5668-sweep-completion-gate`
(versions: 001 NEW, 002 GO, 003 NEW report, 004 NO-GO). After a PB re-stamp
yielded a `prime-builder` work-intent claim, `begin` returned exit 2:

    {"authorized": false, "error": "Bridge 'gtkb-wi5668-sweep-completion-gate'
    does not have a GO-implementation claim or project_authorization_bootstrap
    claim"}

A GO-implementation claim requires latest status = GO; the thread's latest is
NO-GO (v004), so `begin` fails closed. The v004 NO-GO's own Required Action was:
"Prime Builder must isolate, stage, and commit the approved function ... under
the existing GO; then file a revised implementation report."

Impact: the remediation the reviewing role directs is mechanically unreachable —
PB cannot obtain commit authorization to satisfy a report-NO-GO because the
authorization gate keys off latest=GO. Without a supported path, the thread
stalls or invites an ungoverned commit outside the authorization packet.

## Owner Decision Needed

None required to file this advisory (the owner already directed filing per
DELIB-202667454). Future owner decision: prioritization/scheduling of the fix
relative to other bridge-runtime work (relates to WI-5670 resolver work already
in Codex's queue).

## Recommended Prime Action

File a governed bridge proposal (Codex / bridge-runtime ownership) to allow a
GO-implementation claim (or a `project_authorization_bootstrap` path) when the
latest status is a report-level NO-GO whose thread carries a prior live GO for
the same target scope, so the LO-directed "commit-under-existing-GO, then
re-report" flow is mechanically supported. Do NOT patch the
resolver/checker/authorization stack without Codex ownership.

## Classification Slot

Recommended disposition: **adapt** (support the report-NO-GO re-commit flow in
the authorization layer). This advisory is NOT implementation approval and does
not bypass the bridge proposal, Loyal Opposition GO, or implementation-start
gates. Fix ownership (bridge-runtime = Codex domain) is determined through normal
bridge workflow.
