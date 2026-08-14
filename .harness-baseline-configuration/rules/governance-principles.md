# Governance Principles — Active Cross-Harness Operating Rules

This rule carries the active operating principles that every harness inherits
from the neutral baseline. It was split from a legacy role-compatibility rule
whose provenance content now lives in MemBase governance records (Phase A of
the baseline-neutralization program, per the anti-destruction verification
lens: active principles must keep an always-loaded baseline home).

## Deterministic Services Principle

`GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` establishes that repetitive,
deterministic work belongs in services, not sessions.

Justification: token cost (a recurring tax that pays no marginal information
dividend), error rate (AI procedures are more error-prone than deterministic
implementations), and project framing (the project is a collection of
artifacts, not a dialog with accompanying activity).

Operational mandate: when the implementing role notices repetitive plumbing
during a session — multi-step formalities where the AI's substantive
contribution is under ~20% of total work, patterns that require reconstructing
procedure from rule files plus hook code plus example packets, procedures with
steps expressible as "compute X from Y" — it must:

1. Surface the repetition explicitly.
2. File it as a backlog item in the MemBase `work_items` table (e.g., via
   `gt backlog add`) with scope and tradeoff analysis.
3. Not silently absorb the friction (which would make the cost invisible to
   governance).

This principle extends `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` with an
active-pursuit operational mandate. It does NOT supersede
`GOV-ARTIFACT-APPROVAL-001` — formal artifact approval evidence is still
required; the principle suggests the *delivery mechanism* of that approval
should be a service, not per-instance ceremony.

The principle is a bias, not an absolute. One-off intelligent decisions,
operations that genuinely need session context unavailable to a service, and
cases where friction is itself the governance value remain appropriately
AI-mediated.

## Clean-Before-You-Leave Principle

When implementation work is complete, all temp, ephemeral, or session-only
artifacts must be cleaned up before the session ends. This includes temp
files, harness-local scratch files, `memory/` temp files, and any other
session-only artifacts. The session must leave the system in a clean state
for the next session. All important information must be persisted in the
Deliberation Archive, MemBase, bridge Advisory Proposals, or other formal
artifact storage before cleanup. If new code or durable artifacts have been
created as part of the work product of an implementation, those must be
registered as formal artifacts (change controlled) before cleanup.

## Session Self-Initialization Principle

Owner decision `DELIB-0840` and formal records
`GOV-SESSION-SELF-INITIALIZATION-001` and
`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` establish the required
fresh-session self-initialization experience: at the start of a fresh
GroundTruth-KB session, the active harness must present the role being
assumed and the session governance stance, including the known active skills,
plug-ins, directives, hooks, and role mapping that affect the session.

## Session Lifecycle Engagement And Wrap-Up Principle

Owner decision `DELIB-0841` and formal records
`GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`,
`PB-SESSION-WRAP-UP-PROACTIVE-001`, and
`DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` establish that session lifecycle
management is proactive.

The owner should not have to explicitly instruct the platform to initiate
session wrap-up guidance. Each session should actively inform and engage the
owner by drawing attention to priorities across all project dimensions and by
simplifying owner input through concrete suggested actions and priority
choices.

Automatic session lifecycle hooks may generate startup reports, dashboard
snapshots, proactive wrap-up reports, and suggested next actions. Mutating
wrap-up work such as MemBase updates, Deliberation Archive insertion, commits,
pushes, deployment, or external updates remains governed by the applicable
approval, acknowledgement, or owner-authorized automation scope.

## Release And Adoption Work-Queue Principle

Per `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` and
`GOV-GTKB-ADOPTION-ENFORCEMENT-001`: new candidate skills, plug-ins, or
doctor checks identified during adoption work must be added to the top of the
outstanding work queue until adopted, explicitly rejected, or superseded.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
