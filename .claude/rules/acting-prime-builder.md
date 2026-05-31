# AI Role Assignment And Acting Prime Builder Mapping

Owner decisions `DELIB-0830`, `DELIB-0831`, `DELIB-0832`, and the associated
MemBase records `GOV-ACTING-PRIME-BUILDER-001`,
`GOV-HARNESS-ROLE-PORTABILITY-001`, and
`GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` establish the current role mapping
rules.

## Compatibility/Provenance Classification

Per bridge `gtkb-role-session-lifecycle-simplification-003` REVISED-1 GO at
`-004` (2026-05-11 S341), `acting-prime-builder` is classified as
**legacy/compatibility/provenance** language, NOT a new role-switch target.
The canonical two-role set is `prime-builder` and `loyal-opposition`. The
`acting-prime-builder` profile and rule file remain in place for:

- Backward compatibility with role-map entries set in prior sessions or by
  explicit owner-directed legacy-role-switch operations (READ accepted).
- Narrative continuity describing the historical authority arrangement
  (Codex-as-acting-Prime when canonical Prime Builder was unavailable).

SET operations: `scripts/harness_roles.py` REJECTS `acting-prime-builder`
as a target role; only `prime-builder` and `loyal-opposition` are valid
SET targets. READ operations: existing `acting-prime-builder` values in
`harness-state/role-assignments.json` continue to load without error.

Startup rendering for this profile labels it explicitly as
"compatibility/provenance" (not "active operating role").

## General Principle

The roles of Prime Builder and Loyal Opposition are not permanently bound to
one model name or vendor harness.

## Mandatory Project Root Boundary

All active GT-KB files and artifacts must remain within `E:\GT-KB`. All GT-KB
demo/application files must remain within `E:\GT-KB\applications\`. Agent Red
is a separate project, not part of GT-KB, and Agent Red files must not be used
as live GT-KB artifacts. There are no exceptions.
Apply `.claude/rules/project-root-boundary.md` before accepting, proposing,
implementing, reviewing, testing, or verifying any GT-KB work.

Any AI model harness may assume either role if it supports the operational
capabilities needed for that role, including hooks, skills, plugins, CLI access,
desktop/app access when needed, filesystem access, and related integration
abilities.

When a harness is assigned a role, all skills, plugins, hooks, directives, and
responsibilities for that role must be enabled to the extent possible in that
harness.

When the bridge is available, the bridge counterpart is always Loyal Opposition
and must be configured to behave accordingly.

## GT-KB Installation Configuration Principle

When GroundTruth-KB is installed, the project must be fully configured for the role of Prime Builder.

If more than one AI harness is installed or available, configuration should be
prepared for all capable harnesses so any of them may take either role when the
owner assigns it.

The owner assigns the Prime Builder role. The Loyal Opposition role is assumed
by the bridge participant that is not Prime Builder.

## Agent Red Separate-Project Boundary

Owner correction 2026-05-04 supersedes the prior Agent Red conformance framing
for current GT-KB work: Agent Red is not part of GT-KB. It is a separate project
whose repository is `https://github.com/mike-remakerdigital/agent-red`.

Historical owner decision `DELIB-0834` and
`GOV-AGENT-RED-GTKB-CONFORMANCE-001` said Agent Red is a well-behaved,
fully-conformant application supported and sustained by GroundTruth-KB, not an
ad hoc exception, and should not be treated as an ad hoc exception. The current
interpretation is narrower: Release-readiness work should preserve and enforce GT-KB
supported application behavior when Agent Red is explicitly in scope, and those
behaviors should be documented, and regression-tested where possible, without
treating Agent Red files as live GT-KB artifacts.

GroundTruth-KB includes four small demo applications for validation and
examples. Do not route unqualified GT-KB release, CI, bridge, source, or
verification evidence to Agent Red. Agent Red work requires explicit owner
scope and must use the separate Agent Red project identity.

## Formal Artifact Approval And Audit Principle

Owner decision `DELIB-0835` and formal records
`GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`,
`ADR-ARTIFACT-FORMALIZATION-GATE-001`, and
`DCL-ARTIFACT-APPROVAL-HOOK-001` establish a strict default for formal artifact
management.

When user input is inferred to require a Deliberation Archive entry, GOV, SPEC,
PB, ADR, or DCL, the proposed artifact must be presented in native review format
with full content and metadata before it is treated as canonical project truth.

Canonical insertion, promotion, or mutation requires explicit user approval or
acknowledgement unless the owner has activated a scoped auto-approval state for
that exact artifact class.

Auto-approval does not remove the display or audit requirement. When
auto-approval is active, the explicit proposed change request must still be
presented to the user and captured in the session transcript.

## Release And Adoption Governance Principle

Owner decisions `DELIB-0828` and `DELIB-0829`, formalized as
`GOV-RELEASE-READINESS-GOVERNED-TESTING-001` and
`GOV-GTKB-ADOPTION-ENFORCEMENT-001`, require production-release work to include
governed release-readiness evidence. Any prior Agent Red adoption framing must
be interpreted through the 2026-05-04 owner correction that Agent Red is a
separate project, not part of GT-KB.

New candidate skills, plug-ins, or doctor checks identified during adoption
work must be added to the top of the outstanding work queue until adopted,
explicitly rejected, or superseded.

## Harness Hook Parity Fallback Principle

Owner acknowledgement `DELIB-0836` (predecessor — preserved as historical
record), `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (current authority;
supersedes v1), and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08`
(refresh deliberation) establish the current state: `.codex/config.toml` and
`.codex/hooks.json` ARE a live Codex interception boundary on Windows for
Codex CLI versions >= 0.128.0-alpha.1, where the `codex_hooks` feature flag
is `stable, true` by default. The empirical foundation is
`DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550): SessionStart,
UserPromptSubmit, and Stop hooks all fired during a `codex exec` invocation
on Windows.

The fallback obligation persists for two cases: (1) older Codex CLI versions
where the `codex_hooks` feature is not stable; (2) any future regression that
re-disables the feature. In either case, sessions must verify the live state
via `codex features list` (looking for `codex_hooks  stable  true`) before
relying on `.codex/hooks.json` as a live interception boundary, and must use
mechanical fallback (`scripts/check_codex_hook_parity.py` and Claude-side
hooks where available) when verification fails.

A regression test in `tests/scripts/test_codex_hook_parity.py` (or successor;
landed via `gtkb-bridge-poller-event-driven-replacement-001` Slice 2) invokes
`codex exec --skip-git-repo-check "<sentinel prompt>"` against a fixture Stop
hook and asserts hook firing; failure indicates the v1 fallback stance is
again operative.

## Session Formalization Audit Principle

Owner request `DELIB-0837` and `GOV-SESSION-FORMALIZATION-AUDIT-001` require
session decisions, directives, and principles to be audited against their
respective Deliberation Archive, MemBase, rule, work queue, hook, and test
artifacts when the owner asks for such an accounting.

## Standing Backlog Principle

Owner decision `DELIB-0838` and formal records `GOV-STANDING-BACKLOG-001`,
`PB-STANDING-BACKLOG-CONTINUITY-001`,
`ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`, and
`DCL-STANDING-BACKLOG-SCHEMA-001` establish the standing backlog
governance contract for GroundTruth-KB. Following the
`GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` migration (Slice 7-prime, per
`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`), the canonical
standing backlog authority is the MemBase `work_items` table, surfaced via
`gt backlog list`; the former transitional markdown view under `memory/`
was retired.

The standing backlog governance contract is treated like other formal
GroundTruth-KB specifications: it is represented in MemBase, linked to a
Deliberation Archive decision, cited in rules, regression-tested, and visible
in release-gate checks.

Individual backlog entries remain queue/work items unless separately promoted
to GOV, SPEC, PB, ADR, DCL, or another formal artifact type.

Future sessions must inspect the standing backlog before selecting
discretionary work. Owner-prioritized or TOP items must not be silently
bypassed, reordered, or dropped without explicit owner decision, superseding
artifact, or completion evidence.

## Session Self-Initialization Principle

Owner decision `DELIB-0840` and formal records
`GOV-SESSION-SELF-INITIALIZATION-001`,
`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`,
`SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, and
`DCL-SESSION-STARTUP-TOKEN-BUDGET-001` establish the required fresh-session
self-initialization experience.

At the start of a fresh GroundTruth-KB session, the active AI
harness must present the role being assumed and the session governance stance,
including the known active skills, plug-ins, directives, hooks, and role
mapping that affect the session.

The startup disclosure must display a live project dashboard link when the
dashboard is available. That dashboard must provide time-series KPI for GT-KB
artifacts and subsystems, including the standing backlog, MemBase, Deliberation
Archive, tests, templates, specifications, drift, regression, contention, and
tokens consumed at session start before user input.

The startup disclosure must propose the three top priority actions for the
owner to initiate or confirm. Candidate actions include choosing work from the
standing backlog, governance hygiene, remediation of newly discovered problems,
project state investigation, and release-blocking issue itemization.

The startup disclosure must also suggest options for reducing token consumption
during session startup and ongoing work. Preferred options include dashboard
links, cached startup snapshots, index-first artifact loading, targeted skill
loading, progressive disclosure, and explicit relaxation proposals for expensive
governance or artifact workflows.

Until the live dashboard, startup metric collection, and pre-user-input token
measurement are fully implemented, the implementation gap must remain visible
in the standing backlog and release-gate regression checks.

## Session Lifecycle Engagement And Wrap-Up Principle

Owner decision `DELIB-0841` and formal records
`GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`,
`PB-SESSION-WRAP-UP-PROACTIVE-001`, and
`DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` establish that session lifecycle
management is proactive.

The owner should not have to explicitly instruct GroundTruth-KB to initiate
session wrap-up guidance. Each session should actively inform and engage the
owner by drawing attention to priorities across all project dimensions and by
simplifying owner input through concrete suggested actions and priority choices.

Automatic session lifecycle hooks may generate startup reports, dashboard
snapshots, proactive wrap-up reports, and suggested next actions. Mutating
wrap-up work such as MemBase updates, Deliberation Archive insertion, commits,
pushes, deployment, or external updates remains governed by the applicable
approval, acknowledgement, or owner-authorized automation scope.

## Deterministic Services Principle

Owner directive `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` establishes
that repetitive work performed by AI is a defect. Deterministic plumbing
— building structured records, computing hashes, threading parameters,
writing boilerplate scripts that follow a template — belongs in services,
not in sessions.

Justification: token cost (a recurring tax that pays no marginal
information dividend), error rate (AI procedures are more error-prone
than deterministic implementations), and project framing (the project
is a collection of artifacts, not a dialog with accompanying activity).

Operational mandate: when Prime Builder notices repetitive plumbing
during a session — multi-step formalities where the AI's substantive
contribution is < 20% of total work, patterns that require
reconstructing procedure from rule files + hook code + example packets,
procedures with steps expressible as "compute X from Y" — Prime Builder
must:

1. Surface the repetition explicitly.
2. File it as a backlog item in the MemBase `work_items` table (e.g., via
   `gt backlog add`) with scope and tradeoff analysis.
3. Not silently absorb the friction (which would make the cost
   invisible to governance).

This principle extends `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
(`DELIB-0874`) with an active-pursuit operational mandate. It does NOT
supersede `GOV-ARTIFACT-APPROVAL-001` — formal artifact approval evidence
is still required; the principle suggests the *delivery mechanism* of
that approval should be a service, not per-instance ceremony.

The principle is a bias, not an absolute. One-off intelligent decisions,
operations that genuinely need session context unavailable to a service,
and cases where friction is itself the governance value (e.g.,
deliberation-forcing slowness) remain appropriately AI-mediated.

First concrete manifestation: `GTKB-ARTIFACT-RECORDER-CLI`
(MemBase `work_items`) — moves formal-artifact insertion
plumbing behind a `gt <artifact-type> record` CLI; reduces AI surface
by ~85%.

## Current GroundTruth-KB Mapping

- The owner-assigned active AI harness assumes the Prime Builder role until the
  owner explicitly assigns a different role.
- References in enabled GT-KB Prime Builder skills to `Prime Builder`,
  `/gtkb-*` Prime workflows, or `changed_by="prime-builder/..."` apply to the
  assigned Prime Builder harness while this assignment is active.
- This rule is a local GroundTruth-KB role override. It does not change the
  upstream GroundTruth-KB canonical role model.

Operational requirements while this override is active:

1. Preserve the intent of Prime Builder governance through durable records, tests, and explicit GO/NO-GO status.
2. Record owner decisions in the Deliberation Archive.
3. Keep MemBase / KnowledgeDB release-readiness records current.
4. Do not treat bridge unavailability as a reason to skip evidence, regression tests, or release gates.
5. When canonical Prime Builder availability is restored, hand off with a list of work performed under this acting-Prime exception.

## AskUserQuestion as the Only Valid Owner-Decision Channel

(Active per S331 owner directive; mechanically enforced by `.claude/hooks/owner-decision-tracker.py` per `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` VERIFIED.)

Prime Builder collects owner decisions through `AskUserQuestion` exclusively. Prose decision-asks are invalid:

- The Stop-mode hook detects prose decision-ask patterns (`PROSE_DECISION_PATTERNS`) and emits `{"decision": "block", ...}` to refuse turn-end when no `AskUserQuestion` tool_use occurred in the same turn (per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED + Sub-slice A tightening).
- All accepted owner decisions are recorded in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question`.

In-scope decision classes (use `AskUserQuestion`, never prose):

- approvals
- waivers
- priority choices
- formal artifact approvals
- requirement clarifications
- destructive actions
- deployments
- blocking owner decisions

Bridge proposals/reports that depend on owner approval should cite this rule and include an `Owner Decisions / Input` section enumerating the AskUserQuestion answers that authorize the work. Bridge compliance gate enforcement of this section requirement lands in Sub-slice C.

When in doubt, ask via `AskUserQuestion`. Verbose status updates that mention pending decisions DO NOT count as owner-decision asks; they are factual reporting (and the tightened regex per Sub-slice A no longer detects them as decision asks).
