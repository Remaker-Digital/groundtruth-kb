NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T16-31-35Z-prime-builder-A-3fc85e
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless bridge auto-dispatch; role prime-builder; approval_policy=never; sandbox=workspace-write; reasoning_effort=xhigh
Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-5047

# GT-KB Bridge Implementation Report - WI-5047 Ollama Kimi Route Switch - 003

bridge_kind: implementation_report
Document: gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch
Version: 003 (NEW; post-implementation blocker report)
Responds to GO: bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-002.md
Approved proposal: bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md
Recommended commit type: chore:

## Implementation Claim

Partial implementation was applied under the live GO and implementation-start packet, but this report is not ready for `VERIFIED`.

Completed:
- `.api-harness/routing.toml` now sets `[routing.ollama].default_model`, `bridge-review`, `verification`, and `implementation` to `kimi-k2-7-code-cloud`.
- Harness D MemBase registry version 25 was created through `gt harness set-invocation-surface`, and `harness-state/harness-registry.json` now records D headless `--model kimi-k2-7-code-cloud`.
- `platform_tests/scripts/test_verify_ollama_dispatch.py` now includes `test_default_ollama_bridge_review_route_uses_kimi_k2_7_code_cloud`.
- `TEST-11290` was updated to version 2 and bound to that concrete assertion with passing evidence.

Blocked:
- `config/dispatcher/rules.toml` still reports `[budget.harnesses.D].model = "deepseek-v4-pro-cloud"`.
- Direct mutation of `config/dispatcher/rules.toml` was blocked by `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`.
- The current `gt bridge dispatch config` command group exposes `set-eligibility`, `set-weights`, `set-caps`, `set-rule`, `add-harness`, and `remove-harness`, but no transaction that can update `budget.harnesses.<id>.model`.

This leaves the implementation in a known partial state: the actual D headless argv and active Ollama routing point to Kimi, while the dispatcher budget/status metadata label still points to DeepSeek. Loyal Opposition should return `NO-GO` unless a governed dispatcher transaction for budget model metadata already exists and was missed.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision was requested or required for the partial implementation. Owner authorization remains `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD`, carried by `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706`.

This dispatched worker cannot ask the owner interactively. The blocker is mechanical, not a new owner decision: the only permitted mutation path for `config/dispatcher/rules.toml` lacks the needed budget-model transaction.

## Prior Deliberations

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - owner decision to switch Ollama/D to `kimi-k2.7-code:cloud`.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - prior DeepSeek route decision, now superseded for this forward work.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Focused route assertion passed; live resolver and harness-registry checks show Kimi. Dispatcher budget label remains stale, so parity is incomplete. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch config --json` and `gt bridge dispatch status --json` were run; both still report D budget model as DeepSeek. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | The dispatcher control surface was inspected; it lacks a budget-model mutation command. Direct file mutation was blocked. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch` returned a live packet scoped to the approved target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work was performed against latest live `GO` and live work-intent claim `2026-07-06T16-31-35Z-prime-builder-A-3fc85e`. This report is filed as the next numbered `NEW` artifact. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `TEST-11290` is now bound to a real assertion and recorded as passing, but full verification must remain blocked until dispatcher metadata is corrected. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | No `applications/` or Agent Red paths were changed by this work. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\gt.exe harness roles` - confirmed Codex/A as `prime-builder` and Ollama/D as `loyal-opposition`.
- `groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch --json --compact` - latest status remained `GO` at `bridge/...-002.md`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch` - created authorization packet `sha256:ca26c4bb1cd337b00a5cafbd6eb8c0a459fcc3e0da82c841316a5b3e9b7f63e9`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py status gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch` - work-intent claim live, not expired.
- `groundtruth-kb\.venv\Scripts\gt.exe harness set-invocation-surface --harness D --surface headless --value-json ... --reason "WI-5047 switch Ollama/D headless dispatch to kimi-k2-7-code-cloud"` - applied harness D version 25 through MemBase/projection writer.
- Direct `apply_patch` attempt against `config/dispatcher/rules.toml` - blocked by `GTKB-DISPATCHER-CONFIG-CLI-ONLY / DCL-DISPATCHER-CONFIG-CLI-ONLY-001`.
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config --help` - no budget-model setter exists in the command list.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\scripts\test_verify_ollama_dispatch.py` - passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\scripts\test_verify_ollama_dispatch.py` - passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_verify_ollama_dispatch.py::test_default_ollama_bridge_review_route_uses_kimi_k2_7_code_cloud -q --tb=short` - errored before test body due `PermissionError` on `C:\Users\micha\AppData\Local\Temp\pytest-of-micha`.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_verify_ollama_dispatch.py::test_default_ollama_bridge_review_route_uses_kimi_k2_7_code_cloud -q --tb=short --basetemp .gtkb-state\pytest-tmp\wi5047-dispatch-20260706T1642` - passed.
- Live resolver one-liner - returned `default_model='kimi-k2-7-code-cloud'`, `route_key='kimi-k2-7-code-cloud'`, `model_id='kimi-k2.7-code:cloud'`, `timeout_seconds=3600.0`.
- Harness registry one-liner - D headless argv contains `--model kimi-k2-7-code-cloud`.
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config --json` - still reports `budget.harnesses.D.model = "deepseek-v4-pro-cloud"`.
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status --json` - still reports `budget.harnesses.D.model = "deepseek-v4-pro-cloud"` and shows unrelated current dispatcher WARN/FAIL findings for Antigravity/scheduled-task lifecycle.
- `groundtruth-kb\.venv\Scripts\gt.exe tests show TEST-11290 --json` - reports version 2, bound to `platform_tests/scripts/test_verify_ollama_dispatch.py::test_default_ollama_bridge_review_route_uses_kimi_k2_7_code_cloud`, `last_result="pass"`.

## Observed Results

- Active Ollama route config: Kimi.
- Harness D headless argv: Kimi.
- TEST-11290: concrete assertion bound and passing.
- Dispatcher budget/status model label: still DeepSeek.
- Direct dispatcher config mutation: correctly blocked.
- Governed dispatcher config CLI: no available transaction for the required budget model field.

## Files Changed

WI-5047 changes made by this session:
- `.api-harness/routing.toml`
- `groundtruth.db`
- `harness-state/harness-registry.json`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

Relevant dirty target path not changed by this session:
- `config/dispatcher/rules.toml` was already dirty for `[harnesses.F].max_items`; D budget model remains `deepseek-v4-pro-cloud`.

## Recommended Commit Type

- Recommended commit type: `chore:`
- Diff-stat justification: this is configuration and test-evidence maintenance for an approved model route switch; it does not add a user-facing platform feature.

## Acceptance Criteria Status

- [x] `.api-harness/routing.toml` defaults and Ollama skills point to `kimi-k2-7-code-cloud`.
- [x] D headless argv points to `--model kimi-k2-7-code-cloud`.
- [x] Focused route assertion exists and passes.
- [x] `TEST-11290` is bound to a concrete passing assertion.
- [ ] `config/dispatcher/rules.toml` / `gt bridge dispatch config --json` reports D model label as `kimi-k2-7-code-cloud`.
- [ ] Full implementation is ready for `VERIFIED`.

## Risk And Rollback

Residual risk is controlled but real: live D dispatch should use Kimi because the headless argv and route resolver now point to Kimi, but the dispatcher budget/status metadata still advertises DeepSeek. That is an owner-visible parity defect under `ADR-CROSS-HARNESS-PARITY-001`.

Rollback is to run `gt harness set-invocation-surface` to restore D headless `--model deepseek-v4-pro-cloud`, restore `.api-harness/routing.toml` Ollama defaults/skills to DeepSeek, and append a new MemBase test-artifact version reflecting the rollback state. Do not hand-edit `config/dispatcher/rules.toml`; it remains CLI-only.

## Loyal Opposition Asks

1. Return `NO-GO` unless an existing governed `gt bridge dispatch config` transaction can update `budget.harnesses.D.model` and this report missed it.
2. Confirm whether the correct follow-up is a separate implementation proposal adding a `gt bridge dispatch config set-budget-model` transaction to the dispatcher control surface, because that work would require source changes outside the current WI-5047 target paths.
