NO-GO

# Prime Advisory - GT-KB MCP Stable Harness Surface

Status: NO-GO on leaving GT-KB harness integration dependent on ad hoc
prompt/file scraping where a typed MCP adapter can provide a stable convenience
surface.
Author: Codex Loyal Opposition
Date: 2026-05-09 22:26 America/Los_Angeles (2026-05-10 UTC)
Source report:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-09-22-26-GTKB-MCP-STABLE-HARNESS-SURFACE-ADVISORY.md`

## Bridge Delivery Note

This is an owner-requested Loyal Opposition advisory sent to Prime Builder for
an implementation proposal or rebuttal. It is not itself an implementation
proposal and does not authorize code changes.

The `NO-GO` status is deliberate: do not leave the long-term harness boundary
as a collection of broad file reads, prompts, hooks, and generated summaries if
a narrow MCP adapter can provide a safer stable surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this advisory is delivered through the
  Prime/Loyal Opposition bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Prime's eventual
  implementation proposal or rebuttal must cite governing specifications and
  this advisory source.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation must
  include tests derived from the proposed MCP authority and role-boundary
  contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-confirmed MCP posture
  should become a durable proposal/rebuttal artifact rather than remaining chat
  context only.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the MCP surface should preserve
  durable traceability, authority labels, tests, and rollback evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - MCP tools should preserve explicit
  lifecycle and authority distinctions such as authoritative, generated
  summary, advisory, allowed, denied, and owner-approval-required.
- `.claude/rules/operating-model.md` - MemBase authority, CLI surfaces,
  integrations, dashboard/reporting, and lifecycle operations.
- `config/agent-control/system-interface-map.toml` - current authoritative
  system-interface distinctions for MemBase, Deliberation Archive, dashboard,
  plugin/app capability, and MCP server.

## Owner Decisions / Input

- Current-session owner position: do not change the implementation of GT-KB
  services for this question.
- Current-session owner position: adding MCP as a convenience and stable
  surface between harness and application may be beneficial.
- Current-session owner request: Loyal Opposition should prepare an advisory
  report and send it to Prime for an implementation proposal or rebuttal.

## Claim

Prime should evaluate a narrow MCP adapter as the stable harness-facing
contract for GT-KB services. MCP should wrap existing GT-KB APIs, CLI, and
governed service paths; it should not replace the implementation of MemBase,
the Deliberation Archive, dashboard generation, bridge workflow, or governance
mutation rules.

## Recommended Prime Action

File either:

1. a normal implementation proposal for a first GT-KB MCP adapter slice; or
2. a rebuttal explaining why MCP should be deferred or rejected, with evidence
   and a lower-risk alternative.

## Recommended Scope If Prime Proposes Implementation

First slice:

- read-only MCP tools/resources for status, MemBase lookup, deliberation
  search, spec lookup, backlog list, bridge index, and dashboard summary;
- authority labels on every response;
- no raw SQLite writes;
- no broad filesystem mutation tools;
- root boundary enforcement under `E:\GT-KB`;
- role-aware behavior for Prime Builder and Loyal Opposition;
- registration docs/config for one harness only after the server contract is
  stable.

Later slices may add governed mutation tools only when they call existing GT-KB
approval and audit paths.

## Plugin Boundary

If GT-KB is packaged as a plugin, the plugin should be an onboarding bundle:

- skills;
- hooks;
- startup context;
- MCP registration;
- dashboard/doc affordances.

The plugin must not become the source of truth or the core platform boundary.
Core GT-KB should remain package/service/CLI/API plus MCP adapter.

## Decision Needed From Owner

None before Prime responds. Owner input is needed only if Prime proposes to
change the agreed posture, for example by making MCP authoritative, changing
governed mutation rules, or making a plugin the primary GT-KB implementation
boundary.
