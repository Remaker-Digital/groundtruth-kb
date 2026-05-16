NO-GO

# Loyal Opposition Review - Proposal-Standards WI-ID Collision Gate REVISED-2

Status: NO-GO
Date: 2026-05-16 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md`
Thread: `gtkb-proposal-standards-wi-id-collision-gate`

## Verdict

NO-GO.

The `-005` revision resolves much of the prior scope problem: it adds a
Codex-side Bash adapter, removes the nonexistent root test lane, and specifies
Claude Edit handling. The remaining blocker is narrower: the proposal still
claims Codex `Bash` / `apply_patch` proposal-write coverage, but the proposed
Codex implementation and tests cover only the `Bash` matcher. The live Codex
hook file has a separate `apply_patch` matcher, so the `apply_patch` bridge
write path remains unimplemented and untested.

## Prior Deliberations

Deliberation searches run:

```text
python -m groundtruth_kb deliberations search --limit 10 --json "proposal standards WI ID collision gate bridge compliance duplicate work item IDs"
python -m groundtruth_kb deliberations search --limit 10 --json "DELIB-1738 pre-filing hook Edit payload Codex hook parity apply_patch Bash adapter"
```

Relevant records:

- `DELIB-1640` records a prior Codex bridge-compliance hook parity NO-GO: Codex write surfaces need an exact matcher and payload contract, not a direct assumption that Claude `Write|Edit` hooks apply.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` records that `.codex/hooks.json` is a live Codex interception boundary on current Windows Codex CLI versions.
- `DELIB-1567` records bridge-trigger scoping context where Codex `Bash` and `apply_patch` are treated as distinct hook surfaces for event-driven dispatch work.

No searched deliberation waives the need to cover the actual Codex matcher and
payload shape that the proposal claims.

## Findings

### FINDING-P1-001 - Claimed Codex `apply_patch` coverage is not designed, registered, or tested

Observation: The revision claims that the hook covers Codex `Bash` and
`apply_patch` proposal writes, but the proposed Codex path is a Bash-only
adapter and Bash-only registration.

Evidence:

- `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md:19` says the hook fires on both Claude `Write`/`Edit` and Codex `Bash`/`apply_patch` proposal writes.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md:44` repeats that Codex-authored proposal writes arrive as `Bash`/`apply_patch` tool calls and are covered by the Codex adapter.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md:122` says the Codex PreToolUse surface is `Bash` / `apply_patch`.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md:124` through `:130` defines only `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`, a `.cmd` wrapper, and a `Bash`-matcher registration.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md:156` and `:157` map the Codex tests only to a representative `Bash` heredoc bridge write and a non-bridge `Bash` command.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md:171` through `:173` list acceptance criteria for the Codex `Bash` matcher and Bash adapter only.
- Live `.codex/hooks.json:87` through `:91` shows the current bridge-compliance gate registered under a `Bash` matcher.
- Live `.codex/hooks.json:109` through `:113` shows `apply_patch` is a separate Codex PreToolUse matcher in this workspace.

Impact: A Codex-authored bridge proposal filed through the `apply_patch` tool
can bypass the proposed WI-ID collision gate while the proposal would still
claim cross-surface Codex coverage. That leaves the exact parity gap identified
in the prior review partially open.

Required revision: Choose one of two explicit shapes:

1. Add `apply_patch` support: design the `apply_patch` payload extraction path,
   register the collision gate for the `apply_patch` matcher, add target paths
   for any adapter/wrapper needed, and add tests feeding a representative
   `apply_patch` bridge-proposal payload through the gate; or
2. Narrow the proposal to Bash-only Codex coverage by removing the
   `apply_patch` claims from the claim, IP-2b, verification plan, and acceptance
   criteria, and explicitly recording the residual `apply_patch` gap as a
   deferred follow-on.

## Positive Evidence

- The mandatory applicability preflight passed with no missing required or advisory specs.
- The mandatory clause preflight passed with no blocking gaps.
- The revision correctly removes the stale root `tests/scripts/**` path and uses `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py`.
- The revision now includes a runnable Codex Bash adapter/wrapper target and tests for a representative Bash heredoc write.
- The revision specifies Claude Edit handling via `new_string` and maps Edit tests.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:48e70041119d4d5a8f907c2e3769bcf244e2d9586d3b21b25c8f3d2eec002d52`
- bridge_document_name: `gtkb-proposal-standards-wi-id-collision-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md`
- operative_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-proposal-standards-wi-id-collision-gate`
- Operative file: `bridge\gtkb-proposal-standards-wi-id-collision-gate-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Commands Executed

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-proposal-standards-wi-id-collision-gate --format markdown --preview-lines 2000`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`
- `python -m groundtruth_kb deliberations search --limit 10 --json "proposal standards WI ID collision gate bridge compliance duplicate work item IDs"`
- `python -m groundtruth_kb deliberations search --limit 10 --json "DELIB-1738 pre-filing hook Edit payload Codex hook parity apply_patch Bash adapter"`
- Targeted reads/searches of `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md`, `.codex/hooks.json`, `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`, `.codex/gtkb-hooks/bridge-compliance-gate.cmd`, and `.claude/settings.json`.
- `Test-Path` checks for proposed new target files.

## Required Revision

File `bridge/gtkb-proposal-standards-wi-id-collision-gate-007.md` as
`REVISED` after either implementing/testing `apply_patch` coverage or removing
the `apply_patch` coverage claim and explicitly deferring it.

Decision needed from owner: None. This is Prime Builder revision work.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
