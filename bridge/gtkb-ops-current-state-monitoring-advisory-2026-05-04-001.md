NO-GO

# Prime Advisory - GT-KB Current Operating State Monitoring

Status: NO-GO on the current operating-state monitoring posture.
Author: Codex Loyal Opposition
Date: 2026-05-04
Source report:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-OPERATING-STATE-MONITORING-ADVISORY-2026-05-04.md`

## Bridge Delivery Note

This is an owner-requested Loyal Opposition advisory sent to Prime. It is not a
response to a Prime implementation proposal, and it is not approval to
implement directly from this file.

The `NO-GO` status is deliberate: the current operating-state monitoring
posture is not sufficient, and Prime should file a normal implementation
proposal before code changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this handoff uses the bridge as the
  Prime-visible delivery path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Prime's eventual
  implementation proposal must cite the governing specifications and this
  advisory as source evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation must
  include spec-derived tests for CLI, dashboard, startup, and component-state
  reporting.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner's operating-state
  requirement should be preserved as durable implementation work, not left as
  chat-only guidance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposed status subsystem
  should reuse deterministic artifacts and expose traceable reports.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the operating-state output should
  expose explicit PASS/WARN/FAIL or equivalent lifecycle states.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive status
  reconstruction by AI should become deterministic service/CLI code.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - the verified smart-poller
  is the intended opt-out automation path when functioning; the retired OS
  poller remains halted.

## Owner Decisions / Input

- 2026-05-04 owner directive: Do not add an API key or use parallel API/LLM
  inspection for this class of workflow; deterministic regex/procedure code is
  acceptable.
- 2026-05-04 owner directive: GT-KB needs CLI and Dashboard displays of current
  operating state, available on user request and at session startup.
- 2026-05-04 owner directive: The session-startup/status procedure should be
  captured in code so the agent asks for status and receives a report rather
  than executing an LLM-authored inspection procedure.

## Claim

GT-KB has component checks, but no single deterministic current-operating-state
surface for ChromaDB, SQLite/MemBase, dashboard runtime, smart-poller/bridge,
hooks, and startup state.

## Evidence Summary

- `gt project doctor` already contains smart-poller freshness checks and a
  broad readiness report, but it is too noisy to serve as the owner-facing
  current-status answer.
- `gt health` reports session lifecycle metrics, not component liveness or
  freshness.
- The dashboard has a refresh service and Grafana runtime, but `/health`
  reports only the refresh service's own last status.
- The ChromaDB doctor check currently proves only that `.groundtruth-chroma`
  is regeneratable from `groundtruth.db`; it does not prove semantic index
  availability, collection health, fallback mode, or freshness.
- Live smart-poller state is available in `.gtkb-state/bridge-poller/`, but it
  is not normalized into one CLI/dashboard/startup report.

## Recommended Prime Action

File a normal implementation proposal:

```text
bridge/gtkb-ops-current-state-001-2026-05-04-001.md
```

The proposal should create a deterministic `groundtruth_kb.operating_state`
collector and consume it from:

- `gt status` / `gt status --startup --json`
- the generated dashboard SQLite model and panels
- session-startup instructions/hooks

Minimum acceptance criteria:

- no LLM/API calls;
- no additional API key;
- deterministic JSON schema;
- CLI text and JSON output;
- dashboard component-state panels;
- startup consumes command output, not agent reconstruction;
- distinct states for ChromaDB healthy/fallback/unavailable, SQLite
  healthy/corrupt/stale-snapshot, dashboard running/stale/stopped, and
  smart-poller fresh/stale/noisy/stopped.

## Decision Needed From Owner

None. The owner has already supplied the implementation constraint and desired
surfaces. Prime may choose final command naming in the proposal; Loyal
Opposition recommends `gt status`.
