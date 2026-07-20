# Dispatcher Complex Black Box Advisory

Date: 2026-07-15

Skills applied: grill-me-for-clarification, alternatives-investigation, advisory-proposal, loyal-opposition-report

Advisory status: ADVISORY ONLY - this report is not implementation approval and does not authorize protected source/configuration changes. Any implementation should proceed through the governed bridge/work-item path.

## Claim

GT-KB can make the bridge/TAFE/dispatcher complex operationally black-box for ordinary workers, but the current system is only partially aligned. Existing rules, ADRs, and some hooks already point toward a black-box service model, yet dispatch prompts, skills, tests, and current CLI affordances still cause or permit ordinary workers to inspect raw bridge files, dispatcher state, harness registry files, dispatcher config, and dispatcher source.

The least-regret design is a CLI-first worker-context facade plus capability-token enforcement. Ordinary workers should receive only a safe work packet and safe status summaries. Direct inspection should require an explicit, recorded maintenance capability scoped to a session, activity, paths, and TTL, with a break-glass path for dispatcher-down cases.

## Need

The owner wants ordinary workers to operate through the bridge/TAFE/dispatcher complex without learning or manipulating its internals. Workers should not inspect bridge files, raw queue mechanics, dispatcher runtime state, dispatcher configuration, harness state, or other harnesses unless explicitly assigned bridge/TAFE/dispatcher maintenance or granted owner permission case-by-case.

This protects role isolation, prevents harness self-selection or bypass behavior, reduces prompt drift, and lets the dispatcher complex remain the single governed routing and queue authority.

## Owner Decisions Captured

The following decisions were captured in the Deliberation Archive during this advisory intake:

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE`: strict operational black-box boundary for ordinary workers.
- `DELIB-20260715-TRANSCRIPT-REVIEW-EVIDENCE-EXCEPTION`: case-bound authorization to review Claude/Codex interactive transcripts outside `E:\GT-KB` for this advisory.
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET`: worker prompt should point to a safe CLI context packet, not raw files.
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT`: direct inspection requires a signed/recorded maintenance capability.
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`: raw bridge files are protected worker-internal surfaces; ordinary access must be mediated by CLI.

## Known Constraints And Prior Decisions

- `ADR-DISPATCHER-ARCHITECTURE-001`: the dispatcher is a GT-KB-owned black-box service; harnesses are consumers only.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`: harnesses must not trigger dispatch, select targets, influence timing, suspend/resume other harnesses, or observe other harnesses except through governed registry/shared artifacts.
- `ADR-DISPATCHER-COMPLEX-CLI-001`: the dispatcher complex has a unified lifecycle CLI under `gt bridge dispatch complex`, and `gt bridge dispatch health` is the complex-health rollup.
- `SPEC-TAFE-R7`: authoritative artifact-flow data and services should be accessed through dedicated CLI/services; Markdown is generated presentation/report/compatibility after cutover, not protocol substrate.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`: TAFE store is authoritative bridge state, with bridge files/INDEX as generated view depending on status.

External standards support this direction. NIST SP 800-207 frames zero trust around no implicit trust, per-session authorization, and access decisions around resources and workflows, not network location. NIST SP 800-53 Rev. 5 provides the control families for access control, audit/accountability, identification/authentication, and system integrity. OpenTelemetry semantic conventions support a consistent, privacy-bounded telemetry vocabulary for worker-context, denials, capability issuance, and maintenance events.

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
- Current prompts/skills still instruct workers to read `harness-state/harness-identities.json`, `harness-state/harness-registry.json`, TAFE/dispatcher bridge state, and status-bearing bridge files directly.

Exception-authorized transcript scan:

- Claude transcripts under `C:\Users\micha\.claude\projects\E--GT-KB` since 2026-07-01 showed widespread direct access patterns:
  - 1848 `Read` tool uses touching raw bridge files.
  - 668 `Bash` tool uses touching raw bridge files.
  - 159 `Bash` and 96 `Read` uses touching dispatcher source.
  - 86 `Read` and 44 `Bash` uses touching harness registry.
  - 76 `PowerShell`, 71 `Bash`, and 39 `Read` uses touching dispatcher runtime state.
  - 57 `PowerShell`, 17 `Read`, and additional `Bash` uses touching dispatcher config.
- Codex `logs_2.sqlite` event patterns also show dispatcher config, harness registry/identity, dispatcher state, bridge-poller state, and dispatch CLI references.

Interpretation: workers are not merely unaware. The current guidance often directs them into the complex because needed context is not fully available from a safe facade, and the present enforcement surface does not prohibit read/shell inspection.

## What Is Possible

Mechanically, GT-KB can enforce the desired boundary at four layers:

1. Information architecture: make the CLI expose all ordinary worker needs as safe, typed summaries.
2. Prompt/skill contract: remove direct raw-file instructions from ordinary worker prompts and skills.
3. Tool/hook enforcement: deny direct read/write/shell inspection unless a maintenance capability is present.
4. Audit and replay: log denials, bypasses, grants, and maintenance sessions as governed evidence.

The hard part is not conceptual feasibility. It is coverage. Different harnesses expose different hook surfaces, and shell access can bypass narrow tool-level gates. Therefore the design should combine CLI sufficiency, harness-specific hooks, shell adapters, tests, and audit detection instead of relying on one mechanism.

## Best Implementation Approaches

### 1. Worker-Context CLI Facade Plus Prompt Rewrite

Recommended as the first implementation slice.

Add a worker-safe command such as:

```text
gt bridge dispatch worker-context --self --dispatch-id <id> [--json]
```

The command should return:

- role and assigned dispatch/correlation identifiers;
- assigned work packet;
- current allowed next actions;
- safe blocker/no-work reason;
- safe proposal/review/verdict/report content needed for the assignment;
- minimal status summaries for bridge/TAFE/dispatcher availability;
- explicit "not authorized; request maintenance capability" guidance when a worker attempts unsupported context needs.

It must not return raw queue state, raw bridge file paths/content beyond the assigned mediated packet, dispatcher config, runtime-state paths, harness registry internals, other harness state, raw lock/heartbeat paths, or worker-ranking/target-selection internals.

Why this is best: it addresses the root cause visible in transcripts. Workers touched internals because normal operation asked them to gather context from internals. A safe facade makes the desired path easier than the forbidden path.

Risks/tradeoffs: requires careful schema design and broad prompt/skill rewrites. It should be versioned and regression-tested because it becomes a core worker contract.

### 2. Capability-Token Enforcement For Protected Surfaces

Recommended as the enforcement backbone.

Define protected surface classes:

- `bridge_raw_files`
- `tafe_state`
- `dispatcher_source`
- `dispatcher_config`
- `dispatcher_runtime_state`
- `harness_registry`
- `harness_identity`
- `raw_queue_mechanics`
- `other_harness_state`

Ordinary workers are denied direct `Read`, `Grep`, `Glob`, `Bash`/`PowerShell`, `Write`, `Edit`, and `apply_patch` access to these surfaces. Maintenance workers receive a signed or recorded capability containing:

- purpose/activity;
- owner approval or assigned maintenance work item;
- harness/session identity;
- path/surface scope;
- allowed operations;
- TTL;
- reason;
- audit correlation id.

Why this is best: it converts the black-box rule from instruction into a mechanically checkable authorization decision. It also fits zero-trust principles: no implicit trust, resource-scoped access, per-session authorization, and auditability.

Risks/tradeoffs: Windows shell enforcement is imperfect unless all shell access flows through a reliable pretool adapter. Some harnesses may need weaker adapter coverage plus post-run detection until a stronger hook exists.

### 3. Worker-Safe Versus Operator CLI Separation

Recommended as a required companion to approaches 1 and 2.

Split or label dispatcher commands into safe and operator surfaces:

- Worker-safe: `worker-context`, compact assignment status, safe blocker summaries, assigned bridge packet view, safe report excerpts.
- Operator/maintenance: complex health internals, config, topology, runtime paths, daemon locks, heartbeats, target selection, raw telemetry, registry state, raw bridge/TAFE state.

Existing commands such as `gt bridge dispatch report --compact` can seed the worker-safe layer. Existing `status`, `health`, `report --json`, and `complex health` commands need explicit redaction or `--operator`/`--maintenance` modes.

Why this is best: the CLI should expose what workers need, but the current CLI mixes safe summaries with internal operator diagnostics. A split surface prevents accidental leakage and makes tests straightforward.

Risks/tradeoffs: operators need enough detail to diagnose failures. This is solved with capability-gated operator modes, not by leaving internals globally visible.

### 4. Raw Bridge File Mediation

Recommended because the owner selected raw bridge files as protected.

Ordinary workers should not read `bridge/*.md` or `bridge/INDEX.md` directly. Instead, add role-safe views:

```text
gt bridge dispatch worker-packet --dispatch-id <id>
gt bridge view --assigned --dispatch-id <id>
gt bridge status --worker-safe --self
```

The mediated view can include the exact proposal/verdict/report content needed for the assignment, but it should omit unrelated queue entries, path mechanics, status-chain internals not needed by the worker, and cross-harness metadata.

Break-glass rule: if the dispatcher complex is down and cannot serve the worker packet, the owner may grant a maintenance capability permitting manual raw bridge-file inspection. If the dispatcher still functions, it should dispatch back to Prime Builder or issue a safe packet; manual raw-file reads are mainly useful when dispatcher itself is down.

Why this is best: transcript evidence shows raw bridge-file access is the most common internal touchpoint. Mediation removes the largest leak while preserving ordinary productivity.

Risks/tradeoffs: bridge/TAFE cutover state must be handled carefully because bridge Markdown may still have compatibility roles. The mediated command should cite which authority it used.

### 5. Transcript/Log Violation Detector And Regression Corpus

Recommended as an audit layer, not as the only control.

Build a read-only detector that classifies completed sessions for black-box boundary violations:

- direct raw protected reads;
- shell commands touching protected paths;
- prompt/skill instructions that direct workers to protected internals;
- unauthorized maintenance claims;
- use of raw bridge files outside assigned packet or capability.

Use exception-authorized transcript findings as a seed corpus, but preserve only normalized findings in governed in-root artifacts. Add regression tests to prevent future prompts/skills from reintroducing direct internal-reading instructions.

Why this is useful: hooks will never be perfectly uniform across harnesses. Audit detection finds drift and supplies evidence for prompt/skill cleanup.

Risks/tradeoffs: audit is retrospective. It should not be treated as enforcement.

## Recommended Sequence

1. Add `worker-context --self --dispatch-id` and a typed safe packet schema.
2. Rewrite dispatch prompts and worker skills to use only the safe packet for ordinary work.
3. Split/redact dispatcher CLI output into worker-safe and maintenance/operator modes.
4. Extend black-box gate coverage from write/edit to read/grep/glob/shell/apply_patch where supported.
5. Add maintenance capability issuance/validation/audit.
6. Protect raw bridge files behind mediated views.
7. Add transcript/log boundary regression scans.

## Decision Needed

No further owner decision is needed for this advisory. Implementation requires a separate governed proposal/work item. The advisory recommendation is to pursue the combined CLI-facade plus capability-token approach, sliced so the worker-safe context packet lands before hard enforcement.

## Sources

- NIST SP 800-207, Zero Trust Architecture: https://csrc.nist.gov/pubs/sp/800/207/final
- NIST SP 800-53 Rev. 5, Security and Privacy Controls: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- OpenTelemetry Semantic Conventions: https://opentelemetry.io/docs/concepts/semantic-conventions/
- OpenTelemetry Metrics Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/general/metrics/

