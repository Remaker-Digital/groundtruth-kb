ADVISORY
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner-declared ::init gtkb pb; owner-directed ADVISORY bridge filing

bridge_kind: governance_advisory
Document: gtkb-dispatcher-complex-black-box-advisory
Version: 001
Author: Owner-directed advisory prepared by Prime Builder (Codex, harness A)
Date: 2026-07-15 UTC
Mode: advisory report
Severity: high
Priority: high

# Dispatcher Complex Black Box Advisory

## Source

This non-dispatchable ADVISORY bridge artifact carries the owner-directed advisory deliberation and research completed on 2026-07-15. Its sources are the governed owner decisions, governing architecture/specification records, current-system checks, and exception-authorized transcript analysis cited below.

Owner decisions captured during the advisory intake:

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE`: strict operational black-box boundary for ordinary workers.
- `DELIB-20260715-TRANSCRIPT-REVIEW-EVIDENCE-EXCEPTION`: case-bound authorization to review Claude/Codex interactive transcripts outside `E:\GT-KB` for this advisory.
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET`: worker prompt should point to a safe CLI context packet, not raw files.
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT`: direct inspection requires a signed/recorded maintenance capability.
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`: raw bridge files are protected worker-internal surfaces; ordinary access must be mediated by CLI.

Known governing surfaces include `ADR-DISPATCHER-ARCHITECTURE-001`, `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`, `ADR-DISPATCHER-COMPLEX-CLI-001`, `SPEC-TAFE-R7`, and `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`.

External reference anchors used in the advisory research: NIST SP 800-207 Zero Trust Architecture, NIST SP 800-53 Rev. 5, and OpenTelemetry semantic conventions.

## Claim

GT-KB can make the bridge/TAFE/dispatcher complex operationally black-box for ordinary workers, but the current system is only partially aligned. Existing rules, ADRs, and some hooks already point toward a black-box service model, yet dispatch prompts, skills, tests, and current CLI affordances still cause or permit ordinary workers to inspect raw bridge files, dispatcher state, harness registry files, dispatcher config, and dispatcher source.

The least-regret design is a CLI-first worker-context facade plus capability-token enforcement. Ordinary workers should receive only a safe work packet and safe status summaries. Direct inspection should require an explicit, recorded maintenance capability scoped to a session, activity, paths, and TTL, with a break-glass path for dispatcher-down cases.

Need: ordinary workers should operate through the bridge/TAFE/dispatcher complex without learning or manipulating its internals. Workers should not inspect bridge files, raw queue mechanics, dispatcher runtime state, dispatcher configuration, harness state, or other harnesses unless explicitly assigned bridge/TAFE/dispatcher maintenance or granted owner permission case-by-case. This protects role isolation, prevents harness self-selection or bypass behavior, reduces prompt drift, and lets the dispatcher complex remain the single governed routing and queue authority.

## Owner Decision Needed

No owner decision is needed to file this ADVISORY. Implementation is not authorized by this artifact. Downstream Prime Builder disposition should choose whether to route the advisory into backlog/spec/project authorization and then file normal implementation proposals with Loyal Opposition GO before touching protected source, config, startup, rule, hook, dispatcher, TAFE, harness-state, or bridge surfaces.

## Recommended Prime Action

1. Route this ADVISORY through the governed advisory-disposition path.
2. Create or attach canonical backlog/spec/project records for a dispatcher-complex black-box program only after duplicate checks against existing dispatcher, TAFE, bridge, harness-isolation, and startup-context work.
3. Slice implementation so the worker-safe CLI context packet lands before hard enforcement.
4. File separate implementation proposals for protected edits to CLI, prompts, skills, gates, tests, dispatcher status/health redaction, and bridge-file mediation.
5. Keep this ADVISORY non-dispatchable; it is not a work packet, GO verdict, implementation report, or authorization to mutate protected paths.

## Classification Slot

Owner-directed governance advisory for Prime Builder disposition. Classification recommendation: `adopt` as a future governed program, with implementation deferred until normal project authorization, bridge proposal, Loyal Opposition GO, and implementation-start gates are satisfied.

## Evidence From Current System

Current partial support:

- `scripts/dispatch_blackbox_gate.py` already protects some dispatcher surfaces from write/edit operations: `config/dispatcher/rules.toml`, `harness-state/harness-registry.json`, `.gtkb-state/bridge-poller/`, and `.gtkb-state/dispatcher-daemon/`.
- `.claude/settings.json` wires that gate for Claude `Write|Edit`.
- `platform_tests/scripts/test_dispatch_blackbox_gate.py` verifies protected write/edit denial behavior.
- `gt bridge dispatch report --compact` already provides a safer high-level workflow view: dispatch workflow health, in-flight count, and role-actionable/blocked counts.

Current gaps:

- The existing black-box gate is primarily write/edit focused. Its tests explicitly allow `Read`, `Grep`, `Glob`, and `Bash` against protected paths.
- Codex hook batches in `.codex/gtkb-hooks/run_py_no_window.py` do not visibly include `dispatch_blackbox_gate.py`.
- `gt bridge dispatch health --json` exposes operator/internal details such as heartbeat paths, lock paths, PIDs, task names, state directories, and runtime state.
- There is no single worker-safe `worker-context --self --dispatch-id <id>` facade that ordinary workers can use as their complete source of truth.
- Current prompts/skills still instruct workers to read harness identity/registry state, TAFE/dispatcher bridge state, and status-bearing bridge files directly.

Exception-authorized normalized transcript scan found widespread direct access patterns since 2026-07-01: 1848 Claude `Read` tool uses touching raw bridge files; 668 shell uses touching raw bridge files; 159 shell and 96 read uses touching dispatcher source; direct read/shell access to harness registry, dispatcher runtime state, and dispatcher config; and Codex log patterns referencing dispatcher config, harness registry/identity, dispatcher state, bridge-poller state, and dispatch CLI. Interpretation: workers are not merely unaware. Current guidance often directs them into the complex because needed context is not fully available from a safe facade, and the present enforcement surface does not prohibit read/shell inspection.

## What Is Possible

GT-KB can enforce the desired boundary at four layers:

1. Information architecture: make the CLI expose all ordinary worker needs as safe, typed summaries.
2. Prompt/skill contract: remove direct raw-file instructions from ordinary worker prompts and skills.
3. Tool/hook enforcement: deny direct read/write/shell inspection unless a maintenance capability is present.
4. Audit and replay: log denials, bypasses, grants, and maintenance sessions as governed evidence.

The hard part is coverage. Different harnesses expose different hook surfaces, and shell access can bypass narrow tool-level gates. The design should combine CLI sufficiency, harness-specific hooks, shell adapters, tests, and audit detection instead of relying on one mechanism.

## Best Implementation Approaches

### 1. Worker-context CLI facade plus prompt rewrite

Add a worker-safe command such as:

```text
gt bridge dispatch worker-context --self --dispatch-id <id> [--json]
```

It should return role and assigned dispatch/correlation identifiers, assigned work packet, allowed next actions, safe blocker/no-work reason, safe proposal/review/verdict/report content needed for the assignment, minimal bridge/TAFE/dispatcher availability, and a clear maintenance-capability request path. It must not return raw queue state, raw bridge file paths/content beyond the assigned mediated packet, dispatcher config, runtime-state paths, harness registry internals, other harness state, raw lock/heartbeat paths, or worker-ranking/target-selection internals.

### 2. Capability-token enforcement for protected surfaces

Define protected surface classes such as `bridge_raw_files`, `tafe_state`, `dispatcher_source`, `dispatcher_config`, `dispatcher_runtime_state`, `harness_registry`, `harness_identity`, `raw_queue_mechanics`, and `other_harness_state`. Deny ordinary direct `Read`, `Grep`, `Glob`, shell, `Write`, `Edit`, and `apply_patch` access. Maintenance workers receive a signed or recorded capability carrying purpose, owner approval or assigned maintenance work item, harness/session identity, path/surface scope, allowed operations, TTL, reason, and audit correlation id.

### 3. Worker-safe versus operator CLI separation

Split or label dispatcher commands into worker-safe and operator/maintenance surfaces. Existing `gt bridge dispatch report --compact` can seed the worker-safe layer. Existing `status`, `health`, `report --json`, and `complex health` commands need explicit redaction or `--operator` / `--maintenance` modes.

### 4. Raw bridge-file mediation

Ordinary workers should not read `bridge/*.md` or `bridge/INDEX.md` directly. Add role-safe mediated views such as `gt bridge dispatch worker-packet --dispatch-id <id>`, `gt bridge view --assigned --dispatch-id <id>`, or `gt bridge status --worker-safe --self`. Break-glass raw reads should require owner-granted maintenance capability and mainly apply when the dispatcher itself is down and cannot serve the packet.

### 5. Transcript/log violation detector and regression corpus

Add a read-only detector for direct raw protected reads, shell commands touching protected paths, prompt/skill instructions that direct workers to protected internals, unauthorized maintenance claims, and raw bridge-file use outside assigned packet or capability. This is an audit layer, not the only control.

## Recommended Sequence

1. Add `worker-context --self --dispatch-id` and a typed safe packet schema.
2. Rewrite dispatch prompts and worker skills to use only the safe packet for ordinary work.
3. Split/redact dispatcher CLI output into worker-safe and maintenance/operator modes.
4. Extend black-box gate coverage from write/edit to read/grep/glob/shell/apply_patch where supported.
5. Add maintenance capability issuance/validation/audit.
6. Protect raw bridge files behind mediated views.
7. Add transcript/log boundary regression scans.

## Non-Approval Statement

This ADVISORY is a non-dispatchable bridge artifact. It is not implementation approval, not a GO verdict, not a project authorization, not an implementation-start packet, and not permission to modify protected source/configuration/bridge/TAFE/dispatcher/harness-state surfaces. Any downstream implementation must proceed through normal GT-KB project authorization, bridge proposal, Loyal Opposition GO, work-intent, implementation-start, and verification gates.
