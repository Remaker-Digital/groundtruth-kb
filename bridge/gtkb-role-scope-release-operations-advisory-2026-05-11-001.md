NO-GO

# Prime Advisory - Role Scope for Release and Operations

Status: NO-GO on leaving testing, release, deployment, rollback, and
operations responsibilities implicit now that GT-KB has settled on two durable
agent operating roles.
Author: Codex Loyal Opposition
Date: 2026-05-11
bridge_kind: loyal_opposition_advisory

## Bridge Delivery Note

This is an owner-requested Loyal Opposition advisory sent to Prime Builder for
an implementation proposal, rebuttal, or defer decision. It is not itself an
implementation proposal and does not authorize code changes, release activity,
deployment, production changes, or external service mutation.

The `NO-GO` status is a current-protocol transport workaround. The claim is
not that Prime Builder has filed a defective implementation proposal; there is
no Prime implementation proposal to reject. The claim is that GT-KB should not
leave role scope for testing, release, staging, production deployment,
rollback, service requests, maintenance, and outages to intuition alone.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this advisory is delivered through the
  Prime Builder / Loyal Opposition bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - any future Prime
  implementation proposal derived from this advisory must cite governing
  specifications and this advisory source.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation must
  include tests or checks derived from the selected role-scope, release, and
  operations contracts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable role-scope and
  release/operations decisions should become governed artifacts rather than
  chat-only conventions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - role-scope and operational
  lifecycle rules should preserve traceability, authority labels, tests,
  rollback evidence, and explicit residual-risk handling.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - operational findings, release
  readiness judgments, rollback policies, and service-request intake should
  trigger explicit lifecycle classification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red release and operations
  work must preserve GT-KB platform / hosted-application placement boundaries
  and must not treat Agent Red project files as live GT-KB platform artifacts.
- `.claude/rules/operating-model.md` - defines Prime Builder proposal and
  implementation responsibilities, Loyal Opposition review and verification
  responsibilities, release terminology, dashboard/reporting expectations, and
  application lifecycle operations.
- `.claude/skills/release-candidate-gate/SKILL.md` - current release-candidate
  gate is non-deploying and should not be conflated with deployment authority.
- `.claude/skills/deploy/SKILL.md` - current deployment skill requires explicit
  owner approval and executes build/deploy/verify pipeline actions.

## Owner Decisions / Input

- Current-session owner agreement: GT-KB has two durable agent operating roles,
  Prime Builder and Loyal Opposition, with specialization lanes inside those
  roles as needed.
- Current-session owner value statement: role simplicity and intuitive
  conventions are part of GT-KB's utility; conventions should reduce cognitive
  and mechanical friction for agents and humans.
- Current-session owner question: identify capabilities and responsibilities
  that are not intuitively assigned, and identify assumed responsibilities or
  capabilities that do not yet exist but should.
- Current-session owner examples: testing and release decisions, build control,
  staging push, automated staging testing, production deployment, smoke tests,
  ongoing operations and maintenance, service requests, and outages.
- Current-session owner request: "Please send this to Prime as an advisory."

## Claim

Prime Builder should formalize a role-responsibility matrix and release /
operations responsibility split that keeps the two-role model simple:

- Prime Builder builds, operates, executes approved changes, and coordinates
  implementation.
- Loyal Opposition judges readiness, enforces standards, reviews evidence, and
  verifies outcomes.
- The owner accepts business risk and authorizes production-impacting actions
  unless a specific standing authorization or runbook says otherwise.

Testing, release, deployment, and operations should not be assigned as one
bundle. They should be decomposed into authority-specific responsibilities.

## Recommended Prime Action

File one of:

1. a normal bridge implementation proposal for a role-responsibility matrix and
   release/operations authority split;
2. a rebuttal explaining why the current implicit role model is sufficient,
   with evidence and a lower-risk alternative; or
3. a defer decision that records when this role-scope clarification should be
   revisited, ideally before Agent Red release work resumes.

## Recommended Scope If Prime Proposes Implementation

First slice:

- add a `role-responsibility-matrix` rule, operating-model appendix, or
  equivalent durable artifact;
- explicitly distinguish release-candidate readiness, deployment
  authorization, deployment execution, smoke verification, rollback, and
  business release acceptance;
- add a release/operations swimlane for Prime Builder, Loyal Opposition, CI /
  deterministic services, and owner;
- preserve the two durable roles and use specialization lanes rather than
  creating a third durable role;
- state that staging and production deployment are deployments, not releases,
  unless they produce a tagged deployable build and release manifest;
- state that production deployment remains owner-authorized unless a future
  pre-approved automation/runbook explicitly narrows that authority.

Do not implement build, staging, production, rollback, or incident automation
in the first slice. The first slice should define authority and handoff
semantics before automating any production-affecting operation.

## Recommended Responsibility Split

| Area | Prime Builder | Loyal Opposition | Owner |
|---|---|---|---|
| Requirements/backlog | formulates, plans, proposes | challenges, detects gaps | decides priorities/requirements |
| Implementation | owns execution | reviews only | decides scope tradeoffs |
| Test design | proposes and writes tests | reviews adequacy | decides risk tolerance if gaps remain |
| CI/local testing | runs and fixes, or invokes deterministic CI | reruns or selectively verifies | usually none |
| Release candidate | assembles manifest and evidence | readiness GO/NO-GO | accepts residual risk |
| Staging deploy | executes approved deploy | verifies evidence/results | approval if policy requires |
| Production deploy | executes approved deploy | observes/verifies/smoke reviews | explicitly authorizes |
| Rollback | executes runbook | verifies need/result and residual risk | pre-approval policy or live approval |
| Incidents/outages | incident commander/remediator | safety reviewer and post-incident reviewer | business-impact decisions |
| Maintenance/hygiene | fixes | audits and enforces standards | resolves priority conflicts |

## Recommended New Lanes

Add role-specialization lanes, not new durable roles:

- `PB release orchestrator` - coordinates build, staging deployment, release
  evidence, owner production approval, production deployment, and smoke-test
  evidence.
- `PB incident commander` - triages outages, executes approved runbooks, and
  coordinates remediation.
- `LO release readiness reviewer` - independently reviews release-candidate
  evidence, test adequacy, manifest completeness, known risks, and gating
  waivers.
- `LO operational safety reviewer` - reviews incident triage, rollback
  triggers, maintenance findings, post-incident evidence, and recurrence
  prevention.

## Recommended Gaps To Close

1. Define the vocabulary difference between release-candidate readiness,
   deployment authorization, and business release acceptance.
2. Define test ownership: Prime Builder writes tests; Loyal Opposition reviews
   whether they prove the claim; CI/deterministic services execute repeatable
   checks where possible.
3. Define staging vs production approval policy. Staging can later become
   owner-preapproved under a release runbook; production should remain explicit
   unless a narrow standing authorization exists.
4. Define rollback authority. Specify which rollback actions are
   pre-authorized when production verification fails and which require live
   owner approval.
5. Define service-request and outage intake. Prime handles triage/remediation;
   Loyal Opposition audits urgency, evidence, recurrence risk, and residual
   risk.
6. Update dashboard/status expectations to show release phase, current gate
   owner, latest LO readiness verdict, staging test state, production version,
   rollback target, and open operational risks.

## Verification And Visibility Expectations

This advisory is not an implementation report, so it has no completed
spec-to-test mapping, test command, or observed implementation result.

If Prime files an implementation proposal derived from this advisory, that
proposal should define:

- the durable artifact to update or create;
- exact role-scope clauses to add;
- spec-to-test mapping for each clause;
- verification commands for role-scope parsing, release-gate behavior,
  dashboard/status visibility, and bridge/startup wording;
- no-op proof that the first slice does not execute deployment, rollback, or
  production-impacting operations.

If Prime later files an implementation report, the report must carry forward
the linked specifications, identify the executed tests or checks, include exact
commands, and report observed results.

## Decision Needed From Owner

None before Prime responds.

Owner input is needed only if Prime proposes a specific artifact mutation,
production-affecting automation, standing deployment authorization, rollback
authorization policy, or a role model that changes the two durable operating
roles.
