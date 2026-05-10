NO-GO

# Loyal Opposition Review - Claude Code Bridge-Status Thread Automation REVISED-1

bridge_kind: loyal_opposition_review
Document: gtkb-claude-code-bridge-status-thread-automation-001
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md`
Verdict: NO-GO

## Claim

The revised proposal cannot receive GO.

The mechanical bridge gates pass, and the owner-facing parity goal remains valid. The blocker is still the selected mechanism. REVISED-1 conflates Claude Code remote Routines created by `/schedule` with local Claude Code Desktop scheduled tasks, then builds the design around local filesystem paths and `~/.claude/scheduled-tasks/.../SKILL.md` semantics that official Claude Code documentation assigns to Desktop scheduled tasks, not `/schedule` cloud routines. The proposal also asks a routine prompt to set a SessionStart environment marker after SessionStart would already have executed.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "Claude Code Routines schedule bridge status Axis 2 parity idle suppression" --limit 10`
- `python -m groundtruth_kb deliberations search "GTKB_BRIDGE_STATUS_RUN_ID SessionStart bridge status routine" --limit 10`
- `python -m groundtruth_kb deliberations search "Claude Code native primitives first schedule routine owner cadence idle suppression" --limit 10`

Relevant records and thread evidence:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - historical context that bridge automation surfaces need clear active-surface semantics.
- `DELIB-0121` - historical context for bridge operations/reporting via Codex automations; not a current approval of this Claude mechanism.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` - GO for the two-axis articulation; it approves pattern-level architecture, not this specific Routine/Desktop/local-files design.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-002.md` - prior NO-GO findings F1/F2/F3 remain relevant; REVISED-1 changes mechanism but does not yet prove the chosen runtime can operate against live local bridge state.

No targeted DA search surfaced a durable record for `DELIB-S339-2026-05-09-CLAUDE-CODE-NATIVE-PRIMITIVES-FIRST`; REVISED-1 describes it as pending DA harvest, so I treat it as proposal-cited context rather than durable DA evidence.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-code-bridge-status-thread-automation-001
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:5c1e96cadecb347dae43fafdbbb0b852d75e594235c3cc0fdd8d9bc58ad6695d`
- bridge_document_name: `gtkb-claude-code-bridge-status-thread-automation-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md`
- operative_file: `bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
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
- Operative file: `bridge\gtkb-claude-code-bridge-status-thread-automation-001-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - The proposal conflates cloud Routines with local Desktop scheduled tasks

Observation: REVISED-1 says Claude Code Routines via `/schedule` are the recommended primitive and that `/schedule` creates a routine at `~/.claude/scheduled-tasks/<routine-name>/SKILL.md` (`bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md:51-53`). It then requires that routine to compute a SHA-256 of live `bridge/INDEX.md`, read/write `.gtkb-state/bridge-status/last-index-hash.txt`, and use absolute local paths such as `E:\GT-KB\bridge\INDEX.md` (`:55-60`, `:163-179`). Official Claude Code docs distinguish these surfaces: `/schedule` creates scheduled Routines in the cloud, while local Desktop scheduled tasks are the surface with direct local-file/tool access and the on-disk `~/.claude/scheduled-tasks/<task-name>/SKILL.md` prompt file. The docs also state cloud Routines run as full cloud sessions against selected repositories/environments, and cloud scheduling has no local-file access except a fresh clone.

Evidence:

- Proposal: `bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md:51-76`, `:143-180`, `:219-237`.
- Official docs: `https://code.claude.com/docs/en/web-scheduled-tasks` lines 122-125 and 185-187; `https://code.claude.com/docs/en/scheduled-tasks` lines 90-101; `https://code.claude.com/docs/en/desktop-scheduled-tasks` lines 87-104 and 132-157; `https://claude.com/blog/introducing-routines-in-claude-code` lines 261-273.

Deficiency rationale: The proposed implementation surface is internally inconsistent. If Prime implements `/schedule` cloud Routines, the routine cannot operate on live `E:\GT-KB\bridge\INDEX.md` or the host-local `.gtkb-state` hash file as proposed. If Prime implements Desktop scheduled tasks to get local filesystem access and `~/.claude/scheduled-tasks/.../SKILL.md`, then the mechanism is not the `/schedule` cloud Routine selected and justified by the revised proposal.

Impact: The system-interface map could mark `claude-code-bridge-status-routine` as active while the runtime either scans a cloud clone rather than live bridge state, or depends on a different local scheduler than the one approved. That would falsely close the Axis 2 parity gap.

Recommended action: Revise by selecting exactly one Claude scheduling surface and designing to its actual constraints. For live local `E:\GT-KB` bridge status, the plausible surfaces are Desktop scheduled tasks or session-scoped `/loop`; for cloud Routines, the proposal must stop claiming live local-file access and must define how bridge state reaches the cloud session.

### F2 - P1 - The proposed `GTKB_BRIDGE_STATUS_RUN_ID` marker cannot be set by the routine prompt before SessionStart

Observation: REVISED-1 defines `GTKB_BRIDGE_STATUS_RUN_ID` as a SessionStart bypass marker (`bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md:19`, `:184-213`) but the routine template tells the prompt body to "Set environment marker" (`:155-160`). The live dispatchers currently make the analogous auto-dispatch decision by reading `os.environ` before emitting any normal startup payload (`.claude/hooks/session_start_dispatch.py:103-124`, `:160-173`; `.codex/gtkb-hooks/session_start_dispatch.py:90-111`, `:147-160`). The cross-harness trigger succeeds because it sets `GTKB_BRIDGE_POLLER_RUN_ID` in the child process environment before launching the harness (`scripts/cross_harness_bridge_trigger.py:418-429`).

Deficiency rationale: A prompt instruction cannot retroactively affect the SessionStart hook that already ran before the prompt body was processed. For a status-mode bypass to work, the scheduler must provide the environment variable before Claude Code starts the session. REVISED-1 does not specify a tested way for either cloud Routines or Desktop scheduled tasks to inject a unique `GTKB_BRIDGE_STATUS_RUN_ID` into the process environment before SessionStart.

Impact: The proposed tests can pass by invoking the dispatcher directly with a synthetic environment variable, while the actual scheduled routine/task still enters normal fresh-session startup semantics. That repeats the prior F2 class: the automation can be registered but fail its core runtime behavior.

Recommended action: Move marker injection out of the prompt body and into the actual scheduler/runtime configuration, then test that exact path. If the chosen scheduler cannot set pre-SessionStart environment, drop the dispatcher-bypass design and make the scheduled prompt self-contained under normal startup semantics.

### F3 - P1 - Idle suppression does not support the claimed quiet-bridge cost reduction

Observation: REVISED-1 claims 60-minute cadence with idle suppression reduces quiet-bridge cost to about one wake per day / ~50k tokens/day (`bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md:20`, `:59`, `:167`, `:282`, `:289`). Official docs describe cloud Routines and Desktop scheduled tasks as starting a new session on each scheduled run; the no-change hash branch can only execute after that session starts. The existing GT-KB bridge-essential rule records the historical cost lesson: interval automation that scales faster than the work it serves is a regression even when functionally correct (`.claude/rules/bridge-essential.md:68-77`, `:140-146`).

Deficiency rationale: Hash-based early exit can reduce downstream prompt work after the scheduled session exists, but it does not suppress the hourly session starts, daily routine run accounting, startup hook work, or the basic cost of scheduling 24 runs/day. The "quiet bridge -> ~50k/day" claim is therefore not established by the proposed mechanism.

Impact: The owner cost authorization is tied to a cost model the mechanism does not actually prove. Approving GO would authorize building a recurring automation with understated ongoing cost.

Recommended action: Revise the cost model to count every scheduled run under the selected scheduler's actual semantics. If low cost is required, use an event-driven status trigger, a session-scoped dynamic `/loop`/Monitor path, or a cadence that is explicitly owner-approved without assuming hash-based suppression cancels scheduled wakes.

## Positive Confirmations

- The live latest status was `REVISED` in `bridge/INDEX.md` at review start.
- The proposal includes substantive `Specification Links`, `Owner Decisions / Input`, `Prior Deliberations`, a spec-derived test plan, acceptance criteria, risk/rollback, and recommended commit type.
- Mandatory applicability and clause preflights pass with no missing required specs and no blocking clause gaps.
- The native-primitives-first correction is directionally right; the defect is the specific Routine/Desktop/local-files design, not the goal of finding a Claude-native scheduling surface.

## Required Revision Shape

Prime Builder should file a REVISED proposal that:

1. Selects one concrete scheduler: cloud Routine, Desktop scheduled task, `/loop`, Monitor, or another documented mechanism.
2. States the selected scheduler's local-file, conversation-surface, persistence, permission, and startup-hook semantics with evidence.
3. Proves how the runtime reads the live authoritative `E:\GT-KB\bridge\INDEX.md`, or explicitly states that it cannot and scopes the feature differently.
4. If a SessionStart bypass remains in scope, shows how `GTKB_BRIDGE_STATUS_RUN_ID` is set before the hook runs and tests that real scheduler path.
5. Replaces the idle-suppression cost claim with a cost model that counts every scheduled session/run under the selected mechanism.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-code-bridge-status-thread-automation-001` - pass.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-code-bridge-status-thread-automation-001` - pass.
- `python -m groundtruth_kb deliberations search "Claude Code Routines schedule bridge status Axis 2 parity idle suppression" --limit 10`.
- `python -m groundtruth_kb deliberations search "GTKB_BRIDGE_STATUS_RUN_ID SessionStart bridge status routine" --limit 10`.
- `python -m groundtruth_kb deliberations search "Claude Code native primitives first schedule routine owner cadence idle suppression" --limit 10`.
- Targeted reads of the full bridge thread, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `scripts/cross_harness_bridge_trigger.py`, `tests/scripts/test_claude_session_start_dispatcher.py`, `.claude/rules/bridge-essential.md`, `config/agent-control/system-interface-map.toml`, and official Claude Code scheduling/Routines documentation.

## Decision

NO-GO. Revise the mechanism to match one real Claude scheduling surface before implementation.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
