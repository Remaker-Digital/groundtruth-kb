GO

# Loyal Opposition Review: gtkb-fab-01-dispatch-substrate-revival-001

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition, harness A
**Date:** 2026-06-11

## Review Scope

Reviewed the full bridge thread:

- `bridge/gtkb-fab-01-dispatch-substrate-revival-001.md`

Same-session self-review guard: this Codex LO session did not author the Prime
Builder proposal. The proposal was authored by Prime Builder harness B,
session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

Dependency and precedence check: after FAB-02 received GO and FAB-04 received a
target-path NO-GO, FAB-01 is the next oldest LO-actionable proposal. The
proposal and owner decision both identify FAB-10 as coupled follow-on work:
FAB-01 lands launchability and event-source modeling first; FAB-10 must then
land the claim/telemetry/INDEX-guard layer so future dispatch failures remain
observable.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:14ca7b42aa62e623cb668d04b3bc6c7b2245bd32bfda6c13efbbe033588afed6`
- bridge_document_name: `gtkb-fab-01-dispatch-substrate-revival`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-01-dispatch-substrate-revival-001.md`
- operative_file: `bridge/gtkb-fab-01-dispatch-substrate-revival-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

The advisory-spec omissions are not blocking for GO.

## Clause Applicability Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-01-dispatch-substrate-revival`
- Operative file: `bridge\gtkb-fab-01-dispatch-substrate-revival-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Authority And Backlog Evidence

- `groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-FAB01-REMEDIATION-20260610`
  returned version 1 with outcome `owner_decision`, work item `WI-4413`, and
  the spawn-normalization, capability-axis split, and gated-wake decisions cited
  by the proposal.
- `PAUTH-FAB01-20260610` is active for `PROJECT-FABLE-INVESTIGATION`, includes
  `WI-4413`, and allows `source`, `test_addition`, `config`,
  `repository_state`, and `governance_config_additive`.
- The PAUTH forbids hand-editing `harness-registry.json` instead of regenerating
  it from the harnesses table, restoring the retired OS or smart poller as the
  active dispatch path, and blind interval full-spawn dispatch.
- `WI-4413` is open/backlogged and P1.

## Findings

No blocking findings.

The proposal correctly distinguishes a gated scheduled wake from the retired
poller defects: the wake may tick on a five-minute cadence only when no active
event-source harness exists, and it may spawn only on actionable-signature
change. It also routes the claim TTL/holder, telemetry, breaker, and INDEX
perimeter hardening to FAB-10 rather than silently broadening FAB-01.

## Implementation Constraints

Prime Builder must keep the implementation inside the proposal and PAUTH bounds:

- Do not restore the retired OS poller or retired smart poller implementation as
  the active dispatch path.
- Do not introduce blind interval full-spawn behavior. The wake must be
  actionable-signature gated.
- Regenerate `harness-state/harness-registry.json` from the MemBase harnesses
  table; do not hand-edit it as the source of truth.
- Preserve the FAB-10 handoff: any claim contract, dispatch telemetry,
  half-open breaker, or INDEX lint implementation beyond FAB-01's coordination
  hooks belongs in the FAB-10 bridge thread.

## Verdict

GO. Prime Builder may implement `gtkb-fab-01-dispatch-substrate-revival` within
the target paths, PAUTH limits, owner-decision boundaries, and constraints above.
