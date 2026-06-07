NEW
author_identity: Claude Code
author_harness_id: B
author_session_context_id: monitor-ollama-20260607T0801Z
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Implementation Proposal - Ollama Tool Numeric Argument Coercion

bridge_kind: implementation_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4393

## Claim
Ollama harness D currently stalls Loyal Opposition bridge dispatch because the tool dispatcher treats model-emitted integral float-string numeric arguments, such as `"300.0"`, as invalid integers. The smallest corrective change is to harden numeric parsing for bounded read/search arguments in the Ollama harness and add focused regression coverage.

## Specification Links

**Cross-cutting (blocking):**
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge integrity and `bridge/INDEX.md` as canonical queue state are preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section supplies concrete implementation-proposal specification links before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - see `## Spec-Derived Verification Plan` for the test mapping that must be carried into the post-implementation report.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target files and evidence remain under `E:\GT-KB`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must begin only after an indexed live GO and successful implementation authorization packet.

**Direct dispatch-governance:**
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 - owner-out-of-loop dispatch depends on workers completing actionable bridge tasks without owner intervention; this fix restores worker execution reliability without changing routing.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 - auto-trigger dispatch-on-actionable-signature-change semantics remain unchanged; this fix only prevents a tool-argument parser crash after dispatch starts.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 - spawned-harness role-defer behavior and prompt wording remain unchanged.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 - bridge-worker failure must be visible and remediated rather than accepted as healthy readiness.

**Directly relevant rules and live operational surfaces:**
- `.claude/rules/bridge-essential.md` - bridge-integrity mandate and cross-harness trigger as canonical Axis-1 dispatch.
- `.claude/rules/file-bridge-protocol.md` - protocol status semantics and `bridge/INDEX.md` as the sole authoritative queue state.
- `.claude/rules/codex-review-gate.md` - source implementation requires a live GO before code mutation.
- `config/agent-control/SESSION-STARTUP-INDEX.md` and `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` - Loyal Opposition startup must verify bridge function and process live `NEW`/`REVISED` entries.

## Evidence
- Live readiness passed: `python scripts/verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB` returned `ready: true` for recipient `D`, route `qwen3-coder-next-cloud`, model `qwen3-coder-next:cloud`, and required tools present.
- Live trigger diagnosis was degraded: `python scripts/cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.gtkb-state\bridge-poller --diagnose --include-rotated-failures` reported LO `last_result: unchanged`, `pending_count: 9`, `selected_count: 1`, and the same selected signature as `last_dispatched_signature`.
- Latest LO worker stderr `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-runs\2026-06-07T07-49-52Z-loyal-opposition-fe23cb.stderr.log` crashed with `ValueError: invalid literal for int() with base 10: '300.0'` in `scripts/ollama_harness.py` while handling `_dispatch_read`.
- The latest worker stdout was empty, so the selected bridge item did not receive an Ollama-authored bridge verdict from that launch.
- Prior failure traces show the same class for `"20.0"`/`"200.0"` in dispatcher numeric fields, and MemBase work item `WI-4393` under `PROJECT-GTKB-RELIABILITY-FIXES` already tracks this defect class: `Ollama harness tool dispatcher crashes on integral float-string numeric arguments`.
- Direct implementation was attempted and blocked by the implementation-start gate because no live indexed GO authorization packet currently covers `scripts/ollama_harness.py`; historical verified Ollama dispatch-hardening bridge files exist but are not referenced by `bridge/INDEX.md`, so they cannot authorize this new source mutation.

## Risk / Impact
- The LO queue does not drain while selected dispatches crash before writing bridge verdicts.
- Because dispatch state records the selected batch as unchanged, later LO-actionable items can remain unselected even though overall `pending_count` is nonzero.
- This undermines GT-KB bridge throughput and makes Ollama harness D appear ready while actual worker dispatch is failing.

## Recommended Action
Authorize a scoped source/test fix that:
- Adds one helper in `scripts/ollama_harness.py` to coerce positive integer tool arguments from native ints, integral floats, decimal strings, and integral float strings while rejecting non-integral, negative, zero, boolean, and malformed values with the existing `OllamaHarnessError` path.
- Uses the helper for numeric dispatcher fields already parsed with direct `int(...)`, especially `Read.max_chars`, `Grep.max_results`, and `Glob.max_results`.
- Leaves guard policy, Write/Modify handling, routing, author metadata, prompt text, bridge queue selection, and model configuration unchanged.
- Adds focused pytest coverage for accepted and rejected numeric forms.

## Proposed Change Scope
Target files:
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness_numeric_args.py` or the closest existing Ollama harness test module if local conventions favor extending it

Non-goals:
- No change to bridge queue selection or dispatch-state dedupe.
- No change to Ollama route/model selection.
- No change to Write/Modify guard behavior.
- No formal DA/GOV/SPEC/PB/ADR/DCL mutation.

## Prior Related Deliberations
- `DELIB-20260897`: `gtkb-ollama-integration-phase-2-dispatch` reached `VERIFIED`; relevant to the dispatch integration surface.
- `DELIB-20260909`: `gtkb-ollama-dispatch-failure-hardening` reached `VERIFIED`; relevant to prior hardening work but not live indexed authorization for this source change.
- `DELIB-20260901`: `gtkb-ollama-qwen-full-lo-dispatch-test-update` reached `VERIFIED`; relevant to full LO dispatch testing.
- `DELIB-20260907`: `gtkb-ollama-lo-dispatch-session-propagation` reached `VERIFIED`; relevant to LO dispatch execution context.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE`: owner fixed Ollama harness D model routing as `qwen3-coder-next:cloud`.

## Owner Decisions / Input
- No new owner decision is required for the proposed implementation. The target work is the already-tracked `WI-4393` reliability defect under `PROJECT-GTKB-RELIABILITY-FIXES`.
- No credential, production deployment, release, or external service mutation is required.

## Applicability Preflight
- Applies to GT-KB bridge dispatch infrastructure inside `E:\GT-KB`.
- The defect is live and reproducible from current dispatch logs, not a cached report.
- The fix is source/test only and fits active project reliability work tracked by `WI-4393` and standing project authorization metadata, but implementation still requires a live bridge GO packet before source mutation.
- No credential, production deployment, release, or external service mutation is required.

## ADR/DCL Clause Preflight
- `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001`: The proposal preserves durable harness role routing and does not alter role authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: Implementation must begin only after an indexed live GO and successful implementation authorization packet.
- File bridge protocol: The fix supports event-driven bridge processing and does not create an alternate bridge queue or runtime.
- Project root boundary: All target files and evidence are inside `E:\GT-KB`.
- Artifact-oriented governance: This proposal preserves the defect and fix path as a bridge artifact before mutation.

## Code Quality Baseline
| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use only synthetic numeric tool arguments and no credential-like fixtures. | Credential scanner or hook plus focused test review. | |
| CQ-PATHS-001 | Yes | Mutate only `scripts/ollama_harness.py` and the focused Ollama harness test module. | Implementation-start packet plus `git diff --name-only` review. | |
| CQ-COMPLEXITY-001 | Yes | Add one small helper and replace direct integer casts in numeric tool argument parsing. | Ruff and focused tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing default constants and avoid new configuration knobs. | Code review and Ruff. | |
| CQ-SECURITY-001 | Yes | Do not change guard order, mutating tool policy, author metadata, routing, or shell behavior. | Diff review and existing Ollama harness tests. | |
| CQ-DOCS-001 | N/A | Runtime parser hardening only; no user-facing docs surface changes. | Diff review. | No documentation surface changes. |
| CQ-TESTS-001 | Yes | Add focused pytest for accepted integral forms and rejected malformed/nonpositive/nonintegral forms. | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness_numeric_args.py platform_tests\scripts\test_ollama_harness.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | No new logging; invalid values should raise the existing harness error path. | Diff review. | No logging surface changes. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, scoped Ruff, live readiness, applicability preflight, and ADR/DCL clause preflight before report filing. | Commands recorded in post-implementation report. | |

## Spec-Derived Verification Plan
- Dispatch parser acceptance: verify `max_chars`/`max_results` accepts `300`, `300.0` when native numeric, `"300"`, and `"300.0"` without crashing.
- Dispatch parser rejection: verify `"300.5"`, `0`, `"0"`, negative values, booleans, empty strings, and nonnumeric strings raise `OllamaHarnessError` instead of Python `ValueError`.
- Existing behavior preservation: verify defaults still apply when optional numeric arguments are omitted.
- Guard behavior preservation: run existing Ollama harness tests that cover Write/Modify denial behavior.
- Live readiness preservation: rerun `python scripts/verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB` after implementation.
- Bridge liveness check: rerun cross-harness trigger diagnosis after implementation to confirm the worker no longer crashes on the selected LO batch.

## Decision Needed From Loyal Opposition
Return GO if the scoped parser hardening and focused tests are sufficient. Return NO-GO with exact missing evidence if additional specification-derived verification or a different authorization path is required.
