NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive; approval_policy=never; implementation-start packet sha256:92f52e40da0b3c57b8d0aed4e6ff07f227117f3f00d381ebd47d4f130066e3d9

# GT-KB Bridge Implementation Report - gtkb-headless-dispatch-model-pinning - 005

bridge_kind: implementation_report
Document: gtkb-headless-dispatch-model-pinning
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-headless-dispatch-model-pinning-004.md
Approved proposal: bridge/gtkb-headless-dispatch-model-pinning-003.md
Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING-ABD
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4964
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth.db", "harness-state/harness-registry.json", ".api-harness/routing.toml", "config/dispatcher/rules.toml"]

## Implementation Claim

Implemented the approved WI-4964 A/B/D headless model-pinning slice.

- Added a narrow append-only harness registry operation, `harness_ops.set_invocation_surface`, and exposed it as `gt harness set-invocation-surface` so headless argv changes go through MemBase harness records and refresh `harness-state/harness-registry.json`.
- Updated Codex/A headless Prime Builder argv through that command to use `codex exec --model gpt-5.5 -c model_reasoning_effort="xhigh"` while preserving `-c approval_policy="never"`, prompt placeholder, and project-root working directory.
- Updated Claude Code/B headless Loyal Opposition argv through that command to use `claude --model claude-opus-4-8 --effort max` while preserving prompt placeholder, project-root add-dir, and JSON output.
- Added an Ollama route key `deepseek-v4-pro-cloud` whose `model_id` is exactly `deepseek-v4-pro:cloud`, made it the Ollama default and skill route, and updated Ollama/D headless argv to pass `--model deepseek-v4-pro-cloud` with `--skill bridge-review`.
- Updated dispatcher budget/status model labels for A/B/D to `gpt-5.5`, `claude-opus-4-8`, and `deepseek-v4-pro-cloud`.

No role assignment, reviewer precedence, Cursor/E, Antigravity/C, OpenRouter/F provider route, provider credentials, production deployment, or external account setting was intentionally changed by this implementation.

## Authorization Evidence

- Work-intent claim acquired for `gtkb-headless-dispatch-model-pinning` by session `019f247b-4dc8-7b32-a2ab-25839614d33f` at `2026-07-02T23:45:16Z`; `claim_kind` was `go_implementation`, `project_id` was `PROJECT-HARNESS-EQUIVALENCE-PHASE-3`, and `ttl_expires_at` was `2026-07-03T00:25:16Z`.
- Implementation-start packet created at `2026-07-02T23:45:36Z`; packet hash `sha256:92f52e40da0b3c57b8d0aed4e6ff07f227117f3f00d381ebd47d4f130066e3d9`; latest status `GO`; GO file `bridge/gtkb-headless-dispatch-model-pinning-004.md`.
- `python scripts/implementation_authorization.py validate --target ...` returned `"authorized": true` for all target paths listed above.

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
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- `DELIB-20260702-HEADLESS-DISPATCH-MODEL-PINNING` - owner directive for A/B model-selection investigation, proposal filing, and implementation after bridge GO.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - owner directive that Ollama/D must use `deepseek-v4-pro:cloud`, equivalent to `ollama run deepseek-v4-pro:cloud`.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4964-HEADLESS-MODEL-PINNING-ABD` - active A/B/D project authorization for this bounded slice.

## Prior Deliberations

- `bridge/gtkb-headless-dispatch-model-pinning-003.md` - approved REVISED proposal carried forward.
- `bridge/gtkb-headless-dispatch-model-pinning-004.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-202665197` - owner authorization for the HARNESS-EQUIVALENCE-PHASE-3 umbrella and WI-4964.
- `DELIB-20260702-HEADLESS-DISPATCH-MODEL-PINNING` - direct A/B model-pinning mandate.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - direct D/Ollama model selector mandate.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Projection check printed A/B/D headless argv and showed explicit pinned model selectors for all three harnesses. Focused tests cover the canonical invocation-surface update path and Ollama route selection. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m groundtruth_kb.cli bridge dispatch config --json`, `python scripts/verify_codex_dispatch.py --json`, `python scripts/verify_claude_dispatch.py --json`, and `python scripts/verify_ollama_dispatch.py --readiness-only --skip-daemon --json` exercised dispatcher-facing config and headless argv surfaces. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Dispatcher evidence was taken from `gt bridge dispatch config/health/report --json`, not cached aggregate queue files. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Work-intent claim, implementation-start packet, and target-path validation were run before protected mutations. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This implementation report is filed as the next numbered `NEW` bridge file after GO through the implementation-report helper. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries Project Authorization, Project, Work Item, and target_paths metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Linked specs are carried forward from the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report includes spec-to-test mapping, exact commands, and observed results. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `gt harness set-invocation-surface` preserves Codex/A `approval_policy="never"` while adding the model and reasoning selectors. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | No `applications/` or Agent Red files were changed. |
| `GOV-STANDING-BACKLOG-001` | No new WI was created because WI-4964 already covers provider-shim routing and model identity drift. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The Ollama owner directive was captured as `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The owner model directives, expanded PAUTH, revised proposal, and this report are durable lifecycle artifacts. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The owner model directives, dispatch-storm operational evidence, and bounded follow-through are preserved in durable deliberation, PAUTH, proposal, implementation, and report artifacts. |

## Commands Run

- `python scripts/bridge_claim_cli.py claim gtkb-headless-dispatch-model-pinning --session-id 019f247b-4dc8-7b32-a2ab-25839614d33f --ttl-seconds 3600`
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-headless-dispatch-model-pinning --session-id 019f247b-4dc8-7b32-a2ab-25839614d33f --expires-minutes 30`
- `python scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/harness_ops.py --target groundtruth-kb/src/groundtruth_kb/cli.py --target groundtruth-kb/tests/test_harness_ops.py --target platform_tests/groundtruth_kb/cli/test_harness_cli.py --target platform_tests/scripts/test_verify_ollama_dispatch.py --target groundtruth.db --target harness-state/harness-registry.json --target .api-harness/routing.toml --target config/dispatcher/rules.toml`
- `python -m groundtruth_kb.cli harness set-invocation-surface --harness A --surface headless --reason "WI-4964 headless model pinning: Codex A uses gpt-5.5 with Extra High reasoning" --value-json ...`
- `python -m groundtruth_kb.cli harness set-invocation-surface --harness B --surface headless --reason "WI-4964 headless model pinning: Claude B uses Opus 4.8 with Max effort" --value-json ...`
- `python -m groundtruth_kb.cli harness set-invocation-surface --harness D --surface headless --reason "WI-4964 headless model pinning: Ollama D explicitly selects deepseek-v4-pro:cloud route" --value-json ...`
- `python -c "import json; data=json.load(open('harness-state/harness-registry.json', encoding='utf-8')); print(json.dumps({r['id']: r.get('invocation_surfaces',{}).get('headless',{}).get('argv',[]) for r in data['harnesses'] if r['id'] in ['A','B','D']}, indent=2))"`
- `python -c "from pathlib import Path; from scripts.ollama_harness import load_routing_config, resolve_model; cfg=load_routing_config(Path('.')); route=resolve_model(cfg, 'deepseek-v4-pro-cloud', skill='bridge-review'); print({'key': route.key, 'model_id': route.model_id, 'allowed_tools': route.allowed_tools})"`
- `python -m groundtruth_kb.cli bridge dispatch config --json`
- `python -m groundtruth_kb.cli bridge dispatch health --json`
- `python -m pytest groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/harness_ops.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/harness_ops.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_harness_ops.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_verify_ollama_dispatch.py`
- `python scripts/verify_codex_dispatch.py --json`
- `python scripts/verify_claude_dispatch.py --json`
- `python scripts/verify_ollama_dispatch.py --readiness-only --skip-daemon --json`
- `python scripts/verify_claude_dispatch.py --live --prompt "Reply with READY only." --timeout 120 --json`

## Observed Results

- Implementation-start claim: acquired `go_implementation` claim for this session; not expired; `latest_bridge_status` was `GO`.
- Implementation-start packet: created with packet hash `sha256:92f52e40da0b3c57b8d0aed4e6ff07f227117f3f00d381ebd47d4f130066e3d9`.
- Target validation: returned `"authorized": true` for all approved target paths.
- Harness projection check:
  - A argv contains `codex exec --model gpt-5.5 -c approval_policy="never" -c model_reasoning_effort="xhigh" {{PROMPT}} --cd {{PROJECT_ROOT}}`.
  - B argv contains `claude --model claude-opus-4-8 --effort max`, the Claude short prompt flag with `{{PROMPT}}`, `--add-dir {{PROJECT_ROOT}}`, and `--output-format json`.
  - D argv contains `scripts/ollama_harness.py`, the harness short prompt flag with `{{PROMPT}}`, `--skill bridge-review`, and `--model deepseek-v4-pro-cloud`.
- Ollama route resolver: returned `{'key': 'deepseek-v4-pro-cloud', 'model_id': 'deepseek-v4-pro:cloud', 'allowed_tools': ('Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash')}`.
- Dispatcher config: budget/status labels now report A `gpt-5.5`, B `claude-opus-4-8`, and D `deepseek-v4-pro-cloud`.
- Focused pytest: `58 passed, 1 skipped in 13.85s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `5 files already formatted`.
- Codex dispatch verifier: `dispatchable: true`, `static_ok: true`, argv includes `--model gpt-5.5` and `model_reasoning_effort="xhigh"`.
- Claude dispatch verifier: `ready: true`, `static_ok: true`, argv includes `--model claude-opus-4-8` and `--effort max`.
- Claude live probe: return code 0, no stderr, command used `C:\Users\micha\.local\bin\claude.EXE --model claude-opus-4-8 --effort max`, the Claude short prompt flag with `"Reply with READY only."`, `--add-dir E:\GT-KB`, and `--output-format json`.
- Ollama readiness-only verifier with `--skip-daemon`: `ready: true`; route key `deepseek-v4-pro-cloud`; model id `deepseek-v4-pro:cloud`; full LO tool set present. It also warned that no Windows Ollama scheduled task or service was detected.
- Dispatcher health after the change was `WARN` because of a pre-existing Prime Builder A runtime quarantine (`all_impl_auth_quarantined`) unrelated to this model-pinning implementation. LO selected D only; B remains disabled by dispatcher eligibility.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/harness_ops.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_harness_ops.py`
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `groundtruth.db`
- `harness-state/harness-registry.json`
- `.api-harness/routing.toml`
- `config/dispatcher/rules.toml`

`impl_report_bridge.py plan` saw broader worktree dirtiness (`files_changed_count: 204`) that predates or sits outside this slice. This implementation report claims only the target paths listed above plus this report file.

## Acceptance Criteria Status

- [x] A headless argv contains `--model gpt-5.5` and `-c model_reasoning_effort="xhigh"` while preserving `approval_policy="never"`.
- [x] B headless argv contains `--model claude-opus-4-8` and `--effort max` while preserving JSON output and project-root add-dir.
- [x] D headless argv invokes `scripts/ollama_harness.py` with `--skill bridge-review` and explicit `--model deepseek-v4-pro-cloud`.
- [x] `.api-harness/routing.toml` contains an Ollama-provider route whose `model_id` is exactly `deepseek-v4-pro:cloud`.
- [x] Resolver check for the D route returns model id `deepseek-v4-pro:cloud`.
- [x] `gt bridge dispatch config --json` reports A/B/D model labels matching the pinned route names.
- [x] Focused tests cover invocation-surface update, projection refresh, dispatcher-facing labels, and Ollama route resolution without changing roles, status, reviewer precedence, or dispatch eligibility.

## Risk And Rollback

The implementation intentionally leaves Claude/B dispatcher eligibility unchanged. Owner-provided evidence during the session states that B was deliberately disabled (`config/dispatcher/rules.toml` with `can_receive_dispatch=false`) as a dispatch-storm backstop after accumulated hung headless LO workers. This report therefore treats the B live-spawn path as model-ready but currently not dispatcher-selected until a separate storm/root-cause repair and re-enable decision occurs. The approved model-pinning slice did not re-enable B.

Ollama/D now resolves the required route and model id, but local live inventory previously returned no advertised models and the readiness verifier was run with `--skip-daemon`; provider-side availability of `deepseek-v4-pro:cloud` was not live-smoked through Ollama chat in this implementation report.

Rollback is a revert of the source/config/test/projection changes plus a canonical harness registry version restoring the prior A/B/D headless argv values. Bridge files, project authorization rows, and deliberation records remain append-only audit artifacts and must not be deleted by rollback.

## Loyal Opposition Asks

1. Verify that the implementation satisfies WI-4964's A/B/D explicit headless model identity requirements.
2. Treat B's current `can_receive_dispatch=false` as an intentionally preserved operational backstop, not as a model-pinning implementation miss.
3. Return VERIFIED if the report and implementation satisfy the approved proposal; otherwise return NO-GO with concrete findings.
