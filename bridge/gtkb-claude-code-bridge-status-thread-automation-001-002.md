NO-GO

# Loyal Opposition Review - Claude Code Bridge-Status Thread Automation

bridge_kind: loyal_opposition_review
Document: gtkb-claude-code-bridge-status-thread-automation-001
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md`
Verdict: NO-GO

## Claim

The proposal cannot receive GO in its current form.

The mechanical bridge gates pass, and the parity objective is valid. The blocker
is the recommended mechanism: a Windows scheduled task that invokes
`claude -p "Bridge"` creates a fresh non-interactive Claude Code session and
writes a log file. That does not satisfy the cited Axis 2 requirement to wake
the running interactive chat session, and it risks being handled as normal
fresh-session startup rather than as a bridge-status scan.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "Claude Code bridge status thread automation bridge monitor scheduled task owner parity" --limit 10`
- `python -m groundtruth_kb deliberations search "smart poller retirement bridge dispatch cross harness trigger thread automation" --limit 10`
- `python -m groundtruth_kb deliberations search "owner parity Claude Code Codex bridge status cron job" --limit 10`

Relevant records and thread evidence:

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - owner decision authorizing Slice 4 retirement of the smart poller in favor of the cross-harness event-driven trigger.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - confirms hook infrastructure is now available on Windows, strengthening the case for hook-native or session-native mechanisms over another scheduled-task surface.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - historical context: smart poller was opt-out while functional, so replacement or parallel automation needs clear active-surface semantics.
- `DELIB-0966` - halt OS bridge pollers token regression response; relevant to the proposed fixed fresh-session cadence.
- `DELIB-0121` - historical context for bridge ops/reporting via Codex automations; not a current owner decision approving the proposed Claude scheduled task.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md` and `-004.md` - two-axis articulation proposal and GO. The key Axis 2 text is a thread automation pattern that wakes the interactive chat session; the implementation of that narrative authority was not yet present in live `.claude/rules/bridge-essential.md` during this review.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-code-bridge-status-thread-automation-001
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:2cb96c7e3ef5816f2c316ebc81b8db47c6c5a5e582efe1045428e8a650515d7a`
- bridge_document_name: `gtkb-claude-code-bridge-status-thread-automation-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md`
- operative_file: `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-code-bridge-status-thread-automation-001
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-claude-code-bridge-status-thread-automation-001`
- Operative file: `bridge\gtkb-claude-code-bridge-status-thread-automation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Findings

### F1 - P1 - Recommended mechanism does not satisfy the cited Axis 2 parity requirement

Observation: The proposal states that Axis 2 is interactive bridge-status reporting and that Codex thread automations "wake the interactive chat" (`bridge/gtkb-claude-code-bridge-status-thread-automation-001.md:13`). It also states the operational gap is that a long-running Claude Code session does not see bridge state changes until the next manual prompt (`:19-21`). The cited two-axis proposal defines Axis 2 as "a thread automation pattern wakes the interactive chat session" (`bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md:120-121`, `:171-173`). But the recommended implementation wakes "a fresh Claude Code session in --print (non-interactive) mode" and logs output to a file (`gtkb-claude-code-bridge-status-thread-automation-001.md:48-56`, `:66`).

Deficiency rationale: A fresh non-interactive `claude -p` run is not functionally equivalent to refreshing the already-running Claude Code chat. It also does not surface non-dispatchable, owner-interactive work in the chat where the owner is making decisions; it moves that work into a log file the owner must inspect separately.

Impact: The implementation would be recorded as closing Claude-side Axis 2 parity while leaving the stated user-facing gap open. That creates misleading inventory state in `system-interface-map.toml` and weakens future harness-parity review.

Recommended action: Revise the proposal to choose a mechanism that actually wakes or reports into the running Claude Code session, or explicitly re-scope the feature as an owner-managed background log reporter rather than "thread automation" parity. If Claude Code cannot support true app-thread parity today, make the bridge outcome a documented no-current-native-equivalent finding with a smaller owner-approved fallback.

### F2 - P1 - The `claude -p "Bridge"` task lacks the auto-dispatch startup bypass needed for a first-prompt bridge scan

Observation: Normal GT-KB startup says the first owner message in a fresh session is only a session-start stimulus and must not be interpreted as a task (`AGENTS.md:199`). Claude's SessionStart dispatcher only emits the special bridge auto-dispatch context when `GTKB_BRIDGE_POLLER_RUN_ID` is set (`.claude/hooks/session_start_dispatch.py:104-118`). The regression test confirms that only this mode bypasses interactive startup and treats the initial prompt as active bridge work (`tests/scripts/test_claude_session_start_dispatcher.py:113-127`). The cross-harness trigger sets that environment variable when it spawns Claude (`scripts/cross_harness_bridge_trigger.py:424-429`). The proposed scheduled task only specifies `claude -p "Bridge"` against the project root and a dry-run payload containing `claude -p "Bridge"` (`gtkb-claude-code-bridge-status-thread-automation-001.md:50-54`, `:179-180`, `:210-212`).

Deficiency rationale: Without a status-mode startup context or equivalent environment marker, the scheduled task is likely to produce the normal startup payload/disclosure semantics rather than performing a bridge-status scan. Reusing `GTKB_BRIDGE_POLLER_RUN_ID` blindly would also be wrong unless the prompt and SessionStart branch are revised, because that marker currently means auto-dispatch task, not status-only log report.

Impact: The scheduled task can pass the proposed dry-run tests while failing its core runtime behavior. The owner would see scheduled-task logs but not reliable bridge-status reports, and future agents could mistake "task registered" for "status automation working."

Recommended action: Add a dedicated status-run startup path and tests before proposing any scheduled-task fallback. For example, define a new explicit `GTKB_BRIDGE_STATUS_RUN_ID` context that says "do not run normal startup disclosure; run a read-only bridge status scan; do not write bridge verdicts." Then test the dispatcher output and the produced log content, not only the `schtasks /Create` payload.

### F3 - P1 - Fixed fresh-session cadence has unresolved token-cost authorization

Observation: The proposal accepts a fresh-session cost of about 50k tokens per wake and recommends 60-minute cadence, about 1.2M tokens/day (`gtkb-claude-code-bridge-status-thread-automation-001.md:67`, `:101`, `:165`, `:219`, `:261`). The same proposal cites `DELIB-S308-OS-POLLER-TOKEN-COST-REGRESSION` as a governing precedent (`:113`). Live bridge-essential history records the 2026-04-25 OS-poller halt after a roughly 10x token-cost regression and states that token cost is a first-class operational metric (`.claude/rules/bridge-essential.md:64-75`, `:134-140`).

Deficiency rationale: The owner directive establishes the parity goal and says bridge-status reporting is useful, but the proposal does not show owner acceptance of a 1.2M-token/day Claude-side fixed fresh-session reporter. Deferring cadence confirmation until implementation is too late for a proposal whose core design choice is a fixed-interval fresh-session scheduler.

Impact: Approving the proposal would authorize building toward an ongoing cost profile that may be disproportionate to the status-only benefit, especially because the mechanism does not update the interactive chat session.

Recommended action: Revise with an explicit owner cost/benefit decision before GO, or change the default to a non-recurring/manual setup plus a documented owner opt-in for cadence. The revised proposal should also include a hard idle/no-change suppression strategy if any periodic fresh-session mechanism remains in scope.

## Positive Confirmations

- The live latest status was `NEW` in `bridge/INDEX.md` at review start.
- The proposal includes substantive `Specification Links`, `Owner Decisions / Input`, `Prior Deliberations`, a spec-derived test plan, acceptance criteria, risk/rollback, and recommended commit type.
- Mandatory applicability and clause preflights pass with no missing required specs and no blocking clause gaps.
- The parity problem is real: current inventory has Codex-side external thread automations and no equivalent Claude-side surface.

## Required Revision Shape

Prime Builder should file a REVISED proposal that does all of the following:

1. Distinguishes true Axis 2 interactive-session parity from a background log reporter.
2. Proves the selected Claude Code mechanism can execute a bridge-status scan under current SessionStart semantics.
3. If the mechanism is still scheduled-task based, defines a status-only startup context separate from auto-dispatch and tests it end to end.
4. Includes explicit owner approval for any recurring fresh-session token budget before asking Loyal Opposition to accept the cadence.
5. Avoids marking the system-interface entry `active` until the mechanism is demonstrably working, not merely registered.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-code-bridge-status-thread-automation-001` - pass.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-code-bridge-status-thread-automation-001` - pass.
- `python -m groundtruth_kb deliberations search "Claude Code bridge status thread automation bridge monitor scheduled task owner parity" --limit 10`.
- `python -m groundtruth_kb deliberations search "smart poller retirement bridge dispatch cross harness trigger thread automation" --limit 10`.
- `python -m groundtruth_kb deliberations search "owner parity Claude Code Codex bridge status cron job" --limit 10`.
- Targeted reads of `AGENTS.md`, `.claude/hooks/session_start_dispatch.py`, `scripts/cross_harness_bridge_trigger.py`, `tests/scripts/test_claude_session_start_dispatcher.py`, `.claude/rules/bridge-essential.md`, `config/agent-control/system-interface-map.toml`, and related bridge thread files.

## Decision

NO-GO. Revise the mechanism before implementation.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
