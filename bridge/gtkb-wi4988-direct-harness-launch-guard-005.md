NEW

# WI-4988 Direct Harness-to-Harness Launch Guard - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4988-direct-harness-launch-guard
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4988-direct-harness-launch-guard-004.md
Approved proposal: bridge/gtkb-wi4988-direct-harness-launch-guard-003.md
Recommended commit type: feat:
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T08:00:52Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; ::init gtkb pb; ::open ops; model identity not otherwise exposed by harness

## Implementation Claim

Implemented deterministic direct harness-launch enforcement in the shared shell-command directive parser.

`groundtruth_kb.enforcement.check_bash_command` now detects and denies interactive shell/PowerShell command text that directly launches another harness, including Claude Code, Codex `exec`, Ollama, Cursor, OpenRouter, Antigravity/Gemini wrappers, PowerShell call-operator forms, `Start-Process`, and project harness shims such as `scripts/ollama_harness.py`.

The detector intentionally ignores any shell-forgeable dispatcher marker as an allow signal. Spoof attempts such as `GTKB_DISPATCHER_MEDIATED=1 claude ...`, `$env:GTKB_DISPATCHER_MEDIATED=1; claude ...`, or marker-file creation followed by `codex exec ...` are denied.

Dispatcher-mediated launches remain available because they occur inside `scripts/dispatcher_runtime.py` through Python `subprocess.Popen`, outside the interactive shell hook text path. The regression test `test_dispatcher_mediated_codex_exec_composition_remains_launchable` proves dispatcher-owned Codex command composition still produces a launchable `codex exec` wrapper command without trusting an interactive shell exemption.

No live headless Claude, Ollama, Cursor, or Codex worker was directly spawned from this PB session.

## Specification Links

- `SPEC-INTAKE-21c5b3` - owner-stated requirement prohibiting direct harness-to-harness invocation and requiring mechanical enforcement.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner decision evidence authorizing this enforcement work.
- `ADR-DISPATCHER-ARCHITECTURE-001` - cross-harness work must use the dispatcher/control-plane substrate, not harness-to-harness fallback launches.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - centralized dispatcher remains the launch substrate for automated cross-harness work.
- `.claude/rules/bridge-essential.md` - dispatcher daemon/control plane is canonical; manual owner assignment/scanning is the non-automated fallback.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - enforcement applies across harness/tooling paths with explicit regression coverage.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - classifier is deterministic regex/token logic with no model/API call path.
- `SPEC-AUQ-POLICY-ENGINE-001` - false-positive corpus preserves legitimate status/read/search commands while blocking true launch signatures.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook/batch surface remains covered on the Windows Codex path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation report is filed through the live numbered bridge chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision, spec intake, WI, tests, report, and verification remain traceable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact graph from owner decision to implementation evidence is preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - NO-GO -> REVISED -> GO -> implementation-report lifecycle is preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete links are present and mapped to tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - executed tests below map to the GO expectations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, WI, and target-path metadata are inherited from the GO'd proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - changes stay inside GT-KB platform paths under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4988 remains the backlog authority for this enforcement slice.

## Owner Decisions / Input

No new owner decision is required. This implements `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`: no harness may directly launch, trigger, command, supervise, or otherwise interact with another harness as a standby or backup path.

## Prior Deliberations

- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - direct harness-to-harness launch prohibition and mechanical-enforcement directive.
- `.claude/rules/bridge-essential.md` - dispatcher-only bridge automation substrate.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher-owned black-box service and harness-isolation rationale.
- `WI-4977` - bridge stability context that motivated enforcement.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity/history on this Windows host class.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - prior cross-harness enforcement matrix.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-003.md` - approved revised implementation proposal.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| GO expectation / governing surface | Executed verification evidence |
| --- | --- |
| Adversarial spoof-denial cases execute and are denied. | `python -m pytest groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short` returned 50 passed. Cases include shell env spoof, PowerShell env spoof, marker-file then `codex exec`, PowerShell `& claude`, `Start-Process claude`, and `Start-Process -FilePath codex -ArgumentList "exec review"`. |
| False-positive corpus passes for mention-not-launch, and true-positive corpus blocks launch signatures. | `python -m pytest platform_tests/scripts/test_gate_fp_corpus.py -q --tb=short` returned 34 passed. Added pass cases for `gt bridge show ...`, `python scripts/verify_codex_dispatch.py`, `rg claude bridge/`, and PowerShell prose output. Added block cases for direct launch signatures and spoof attempts. |
| Claude/Codex hook surfaces inherit the shared classifier. | `python -m pytest platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --tb=short` returned 7 passed. Codex Bash and Claude PowerShell direct-launch payloads deny and log `root-boundary-command`; Codex batched hook registration still routes Bash through `directive-enforcement.cmd`. |
| Dispatcher-mediated command composition still works without trusting interactive shell exemptions. | `python -m pytest ... test_dispatcher_runtime_work_intent.py ...` included `test_dispatcher_mediated_codex_exec_composition_remains_launchable`, proving dispatcher-owned `subprocess.Popen` composes a `codex exec` worker wrapper with `--cd` and launches under the dispatcher path. |
| Classifier is deterministic with no LLM/API call path. | Implementation is local token/regex logic in `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`; no network/API/model imports or calls were added. `python -m ruff check ...` passed. |
| Adjacent framework directive adapter remains green. | `python -m pytest groundtruth-kb/tests/framework/test_bash_enforcement_parser.py groundtruth-kb/tests/framework/test_claude_directive_adapter.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short` returned 52 passed. |

## Commands Run

- `python -m pytest groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short` - 50 passed.
- `python -m pytest groundtruth-kb/tests/framework/test_bash_enforcement_parser.py groundtruth-kb/tests/framework/test_claude_directive_adapter.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short` - 52 passed.
- `python -m pytest platform_tests/scripts/test_gate_fp_corpus.py -q --tb=short` - 34 passed.
- `python -m pytest platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --tb=short` - 7 passed.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py` - all checks passed.
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_gate_fp_corpus.py platform_tests/scripts/test_fab14_directive_hook_coverage.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py` - 5 files already formatted.

## Observed Results

- Direct interactive shell/PowerShell launches are denied with remediation text naming `SPEC-INTAKE-21c5b3` and `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`.
- Mention-only commands, bridge status/read commands, readiness-script names, and search commands continue to pass.
- Spoofed dispatcher markers are ignored for allow/deny.
- Dispatcher-owned Codex worker composition remains launchable through `subprocess.Popen`; no direct interactive spawn path was added.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `config/governance/gate-fp-corpus.toml`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`

## Rollback

Revert the files above to remove direct-harness launch detection and restore the prior root-boundary-only command parser behavior. No external service, database migration, or dispatcher runtime state change is required.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
