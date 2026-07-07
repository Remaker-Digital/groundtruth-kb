NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex interactive Prime Builder

# GT-KB Bridge Implementation Report - gtkb-wi5060-harness-readiness-repair - 003

bridge_kind: implementation_report
Document: gtkb-wi5060-harness-readiness-repair
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5060-harness-readiness-repair-002.md
Approved proposal: bridge/gtkb-wi5060-harness-readiness-repair-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060
Recommended commit type: fix:

## Implementation Claim

Implemented the approved WI-5060 harness-readiness repair for A, C, D, and F.

OpenRouter/F now has an explicit `openrouter-cloud-default` route in `.api-harness/routing.toml` with `model_id = "moonshotai/kimi-k2.7-code"` for metadata and `omit_payload_model = true` for the API payload. The F dispatcher invocation remains model-free; the shim omits `payload["model"]` for the cloud-default route so OpenRouter's account/cloud default selects the model. Explicit non-omitting routes still send their configured model.

OpenRouter/F and Ollama/D now fail closed on missing or blank final assistant text. Ollama/D also has the repeated no-progress tool-call guard already used by the OpenRouter shim, preventing max-turn exhaustion on identical tool-call loops.

After successful direct smoke evidence, D and F dispatch eligibility were re-enabled through the governed dispatcher config writer. Current dispatcher topology selects A and F for Prime Builder dispatch and D and C for Loyal Opposition dispatch.

During implementation, an auto-dispatched A worker held the GO implementation claim and became idle while leaving partial edits. The worker was drained through the governed dispatcher control surface (`gt bridge dispatch drain --timeout 5 --json`), its stale claim was released, and this interactive Prime Builder session reacquired the work-intent claim before completing the report.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires status-bearing bridge work and role-correct proposal/GO sequencing before protected source/config mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded project authorization before implementation under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass Loyal Opposition GO, implementation-start, post-implementation reporting, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal/report links work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - bridge header includes Project Authorization, Project, and Work Item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each behavior to concrete tests and live readiness checks.
- `GOV-ENV-LOCAL-AUTHORITY-001` - live OpenRouter credential use remains read-only from `.env.local`; no credential lifecycle, disclosure, or rotation is in scope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - D/F readiness is measured through supported dispatcher/control-plane surfaces, not ad hoc durable-state claims alone.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatch status/health commands are the verification surface for final dispatchability.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, PAUTH, bridge proposal, tests, implementation report, and verification are preserved as durable linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair is framed as an artifact graph rather than an untracked local patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - D/F move from disabled/blocking evidence toward re-enabled readiness only through explicit lifecycle evidence.

## Owner Decisions / Input

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` records the owner goal to test and fix harnesses A, C, D, and F, with special focus on OpenRouter/F default model invocation and shim max-turn behavior.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` authorized the bounded source, test, configuration, and governance-evidence scope for WI-5060 under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `bridge/gtkb-wi5060-harness-readiness-repair-002.md` records the Loyal Opposition GO authorizing the implementation.

## Prior Deliberations

- `bridge/gtkb-wi5060-harness-readiness-repair-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5060-harness-readiness-repair-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - prior GO authorizing targeted PAUTH scope for shim max-turn exhaustion work.
- `DELIB-F-MAXTURN-PERSISTS-REDISABLE-20260706` - records that OpenRouter/F max-turn recurrence persisted after SSL/connectivity cleared, requiring F to remain disabled until repair evidence.
- `DELIB-F-POSTFIX-VERIFICATION-SSL-WATCH-20260706` - records the earlier OpenRouter SSL failure as transient and not the current blocker.
- `DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` - prior activation decision for OpenRouter/F Prime Builder dispatch.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt bridge show gtkb-wi5060-harness-readiness-repair --json --compact` returned latest `GO` at version 002 before implementation report filing; `python scripts/bridge_claim_cli.py claim gtkb-wi5060-harness-readiness-repair --session-id 019f39ff-4e44-7a32-b5d0-6969ec4d55ec` returned `acting_role: prime-builder` and `claim_kind: go_implementation`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | PAUTH id is carried in the proposal/report headers and claim status returned `project_id: PROJECT-GTKB-RELIABILITY-FIXES`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked specs plus Project Authorization, Project, and Work Item headers. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest run covered routing/payload omission, blank final-text failure, repeated no-progress tool-loop failure, and dispatcher budget regression: `93 passed`. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Live OpenRouter smoke consumed configured credentials without printing or modifying secret values; output was exactly `OK`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch config set-eligibility D/F --can-receive-dispatch --json` returned `status: applied`; `gt bridge dispatch report --json` reported `health_status: PASS`, `selected_candidate_count: loyal-opposition=2, prime-builder=2`, and selected A/F plus D/C. `gt bridge dispatch health --json` returned `health_status: PASS`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Owner decision, PAUTH, proposal, GO, source/test/config changes, live smoke evidence, dispatcher eligibility updates, and this implementation report are preserved in the bridge/MemBase artifact chain. |

## Commands Run

- `gt bridge dispatch drain --timeout 5 --json`
  - Observed: `drain_markers_written: 1`; terminated the stale auto-dispatched worker PIDs `5408`, `24716`, and `6740`.
- `python scripts/bridge_claim_cli.py release gtkb-wi5060-harness-readiness-repair --session-id 2026-07-07T01-10-39Z-prime-builder-A-1abfef`
  - Observed: exit 0.
- `python scripts/bridge_claim_cli.py claim gtkb-wi5060-harness-readiness-repair --session-id 019f39ff-4e44-7a32-b5d0-6969ec4d55ec`
  - Observed: exit 0; `acting_role: prime-builder`, `claim_kind: go_implementation`.
- Focused pytest command against `platform_tests/scripts/test_openrouter_harness.py`, `platform_tests/scripts/test_ollama_harness.py`, and `platform_tests/scripts/test_dispatcher_budget_constants_regression.py`, with quiet output, pytest cache disabled, and short tracebacks.
  - Observed: `93 passed, 1 warning in 1.52s`.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/openrouter_harness.py scripts/ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py`
  - Observed: `All checks passed!`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/openrouter_harness.py scripts/ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py`
  - Observed: `4 files already formatted`.
- OpenRouter/F smoke via `scripts/openrouter_harness.py` using its prompt option, `--skill implementation`, `--max-turns 2`, `--timeout 60`, and `--session-timeout 120`; no `--model` argument was supplied.
  - Observed: `OK`; no `--model` argument was supplied.
- Ollama/D smoke via `scripts/ollama_harness.py` using its prompt option, `--skill bridge-review`, `--model kimi-k2-7-code-cloud`, `--max-turns 2`, `--timeout 60`, and `--session-timeout 120`.
  - Observed: `OK`.
- `codex exec --model gpt-5.5 -c approval_policy="never" --sandbox read-only "Reply exactly OK." --cd E:\GT-KB --add-dir .codex`
  - Observed: process exited 0 and printed `OK`.
- `agy --print "Reply exactly OK." --print-timeout 60s --model "Gemini 3.5 Flash (High)" --dangerously-skip-permissions --add-dir E:\GT-KB`
  - Observed: process exited 0 and printed `OK` after the LO startup disclosure.
- `gt bridge dispatch config set-eligibility F --can-receive-dispatch --json`
  - Observed: `status: applied`; harness-registry projection regenerated.
- `gt bridge dispatch config set-eligibility D --can-receive-dispatch --json`
  - Observed: `status: applied`; harness-registry projection regenerated.
- `gt bridge dispatch report --json`
  - Observed: `health_status: PASS`; `selected_candidate_count` reported `prime-builder: 2` and `loyal-opposition: 2`; selected Prime Builder candidates were A and F; selected Loyal Opposition candidates were D and C.
- `gt bridge dispatch health --json`
  - Observed: `health_status: PASS`.
- `gt harness list`
  - Observed: A, C, D, and F all `status: active`; A/F and C/D dispatch surfaces all had `can_receive_dispatch: true`.

## Observed Results

- OpenRouter/F no longer needs a model argument in its headless invocation. The default implementation route omits `payload["model"]`, and the live smoke returned `OK`.
- Ollama/D bridge-review no longer returns blank-success for the smoke prompt; it returned `OK` under `--skill bridge-review --model kimi-k2-7-code-cloud`.
- Shim final-output behavior is fail-closed for blank final assistant text in both OpenRouter and Ollama.
- Ollama/D now fails fast on repeated identical no-progress tool calls instead of consuming the full max-turn budget.
- A/C/D/F all have current-role readiness evidence:
  - A: headless Codex exec returned `OK`.
  - C: headless Antigravity print returned `OK` after LO startup disclosure.
  - D: Ollama bridge-review smoke returned `OK`.
  - F: OpenRouter implementation smoke returned `OK` with no `--model`.
- Dispatcher health is PASS, and selected topology includes A/F for Prime Builder plus D/C for Loyal Opposition.

## Files Changed

- `.api-harness/routing.toml`
  - Added `models.openrouter-cloud-default` with `omit_payload_model = true`.
  - Routed OpenRouter default, implementation, verification, and bridge-review skills to `openrouter-cloud-default`.
  - Preserved D's Kimi cloud route selection.
- `scripts/openrouter_harness.py`
  - Added `ModelRoute.omit_payload_model`.
  - Parsed `omit_payload_model` from routing config.
  - Omitted the OpenRouter API `model` field when the route requests cloud-default behavior.
  - Failed closed on blank final assistant text.
- `scripts/ollama_harness.py`
  - Added nonblank final-text validation.
  - Added repeated no-progress tool-call detection.
- `platform_tests/scripts/test_openrouter_harness.py`
  - Added coverage for cloud-default route parsing, payload model omission, and blank final-text rejection.
- `platform_tests/scripts/test_ollama_harness.py`
  - Added coverage for blank final-text rejection and repeated no-progress loop termination.
- `harness-state/harness-registry.json`
  - Regenerated by `gt bridge dispatch config set-eligibility`; D and F dispatch surfaces now have `can_receive_dispatch: true`.
- `groundtruth.db`
  - Updated by the governed dispatcher/harness registry writer for D/F eligibility and related project-governance state.

The report helper observed a broader dirty worktree (`files_changed_count: 180`) because unrelated pre-existing worktree changes are present. This implementation report intentionally scopes the WI-5060 changed-path claim to the approved target paths and direct governance state listed above.

## Acceptance Criteria Status

- [x] OpenRouter/F uses account/cloud default model selection without a `--model` invocation argument.
- [x] OpenRouter/F preserves model provenance through configured requested metadata and response `model` metadata.
- [x] OpenRouter/F and Ollama/D fail closed on blank final assistant text.
- [x] Ollama/D terminates repeated no-progress tool-call loops before max-turn exhaustion.
- [x] Focused unit tests and ruff lint/format gates pass.
- [x] Live smokes for A, C, D, and F pass.
- [x] D and F dispatch eligibility is restored only after successful smoke evidence.
- [x] Dispatcher topology/health shows A/F as Prime Builder candidates and D/C as Loyal Opposition candidates.

## Risk And Rollback

Residual risk is limited to provider/account-side behavior: OpenRouter's account default must remain configured to `moonshotai/kimi-k2.7-code`, because the shim intentionally omits the request payload model for the cloud-default route. If provider-side behavior changes, rollback is to switch `.api-harness/routing.toml` OpenRouter routes back to an explicit model row or set `omit_payload_model = false`, then disable F dispatch with `gt bridge dispatch config set-eligibility F --no-can-receive-dispatch --json` until new smoke evidence passes.

If D regresses, rollback is to disable D dispatch with `gt bridge dispatch config set-eligibility D --no-can-receive-dispatch --json` while retaining the fail-closed shim behavior and tests.

The dispatcher drain used during implementation only stopped a stale auto-dispatched worker; it did not delete bridge artifacts. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and command evidence.
2. Confirm that `openrouter-cloud-default` omits the OpenRouter payload model while explicit routes can still carry configured model IDs.
3. Confirm that D/F dispatchability was restored only after successful live smoke evidence.
4. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
