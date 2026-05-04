NO-GO

# Prime Advisory - AUQ Policy Gates Backlog Item

Status: NO-GO on leaving AUQ-backed action gating as scattered hook behavior.
Author: Codex Loyal Opposition
Date: 2026-05-04
Source report:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md`

## Bridge Delivery Note

This is an owner-requested Loyal Opposition advisory sent to Prime for backlog
addition. It is not a response to a Prime implementation proposal, and it does
not authorize implementation without a normal proposal/review cycle.

The `NO-GO` status is deliberate: the current posture should not remain an
ad hoc collection of hooks and agent memory.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this advisory is delivered through the
  Prime/Loyal Opposition bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Prime's eventual
  implementation proposal must cite the governing specifications and this
  advisory source.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must
  include spec-derived tests for policy outcomes, scope protection, and
  approval receipts.
- `GOV-OWNER-DECISION-SURFACING-001` - owner decisions should be surfaced
  through durable, visible owner-interaction mechanisms.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this owner directive should become
  a backlog item and implementation proposal, not remain chat-only.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - action gates should preserve
  traceable artifacts, receipts, and test evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - policy outcomes should use explicit
  lifecycle states such as ALLOW/WARN/ASK/DENY.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - application-scope sessions must
  not casually mutate GT-KB platform implementation artifacts.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive policy decisions
  should be deterministic service/CLI behavior, not agent reconstruction.
- `DELIB-0878` - prior isolation authority-matrix planning supports
  application/platform write-scope separation.

## Owner Decisions / Input

- 2026-05-04 owner observation: AskUserQuestion is valuable because it opens a
  dedicated Claude Chrome UI dialog that is hard to miss.
- 2026-05-04 owner directive: consider wider use of hooks plus
  AskUserQuestion for commit, push, tests, build/deploy to staging, production
  deploy, operating-state probes, requirements updates, and other tracked
  actions.
- 2026-05-04 owner directive: consider hooks that prevent accidental GT-KB
  artifact changes while working in a GT-KB-hosted application scope, such as
  Agent Red.
- 2026-05-04 owner question: identify lower-token or easier-to-maintain
  alternatives.

## Claim

Prime should add a backlog item for a central deterministic AUQ policy gate,
not expand one bespoke hook per action.

Recommended backlog item:

```text
GTKB-AUQ-POLICY-GATES-001
```

## Recommended Backlog Scope

Create a central deterministic policy checker:

```text
gt policy check --action <action> --scope <scope> --paths <paths> --json
```

Canonical outcomes:

```text
ALLOW - proceed silently
WARN  - proceed with deterministic advisory text
ASK   - block until AskUserQuestion produces a scoped approval receipt
DENY  - block; requires scope change, different command, or external approval
```

Initial action classes:

- commit
- push
- test
- build
- deploy-staging
- deploy-production
- status/probe
- requirements/specification update
- GT-KB platform writes while active scope is application

## Lower-Cost Controls To Consider

- structural read-only boundaries or installed-package consumption for GT-KB
  platform code during application-scope sessions;
- Git branch protection and required reviews;
- deployment environment approvals for production;
- `gt` command wrappers for commit, push, deploy, spec update, and status;
- thin hooks that call the same policy engine;
- short-lived approval receipts to prevent repeated AUQ prompts for one
  already-approved action.

Do not use LLM/API classifiers for this backlog item.

## Recommended Prime Action

Add `GTKB-AUQ-POLICY-GATES-001` to the backlog, then file a normal
implementation proposal with:

- policy registry schema;
- active-scope model;
- path-ownership mapping;
- approval receipt format;
- first hook/wrapper adapters;
- tests for ALLOW/WARN/ASK/DENY outcomes and Agent Red application-scope
  protection.

## Decision Needed From Owner

None for backlog addition. Prime should propose slice order and exact policy
registry shape through the bridge.
