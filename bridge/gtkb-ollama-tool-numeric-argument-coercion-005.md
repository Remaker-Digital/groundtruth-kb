NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 2026-06-07T08-45-16Z-prime-builder-60524b
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: codex; headless bridge auto-dispatch; Prime Builder; workspace-write
author_metadata_source: bridge auto-dispatch session; corrected after stale bridge-author-metadata/current.json injection

bridge_kind: implementation_report
Document: gtkb-ollama-tool-numeric-argument-coercion
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-ollama-tool-numeric-argument-coercion-004.md
Approved proposal: bridge/gtkb-ollama-tool-numeric-argument-coercion-003.md
Recommended commit type: fix:

# Implementation Report - Ollama Tool Numeric Argument Coercion

## Implementation Claim

Implemented the approved parser hardening for Ollama harness bounded numeric tool arguments.

`scripts/ollama_harness.py` now routes `Read.max_chars`, `Grep.max_results`, and `Glob.max_results` through a single positive-integer parser that:

- defaults only when the optional field is omitted;
- accepts native positive integers, native integral floats, decimal integer strings, and integral float strings;
- rejects booleans, zero, negative values, nonintegral values, empty strings, and malformed strings through `OllamaHarnessError`; and
- preserves existing dispatch routing, guard order, author metadata, bridge queue selection, model routing, and prompt text.

Added focused regression coverage in `platform_tests/scripts/test_ollama_harness_numeric_args.py`.

## Implementation Authorization

- Live GO used: `bridge/gtkb-ollama-tool-numeric-argument-coercion-004.md`.
- Approved proposal used: `bridge/gtkb-ollama-tool-numeric-argument-coercion-003.md`.
- Implementation packet command: `python scripts\implementation_authorization.py begin --bridge-id gtkb-ollama-tool-numeric-argument-coercion`.
- Implementation packet activation command after concurrent packet overwrite: `python scripts\implementation_authorization.py activate --bridge-id gtkb-ollama-tool-numeric-argument-coercion`.
- Active packet hash at mutation time: `sha256:3a2f2039310af1ae136bd7a5a60a178b9dda5e9f296897c0d18d861afdef1b45`.
- Active packet target scope: `scripts/ollama_harness.py`, `platform_tests/scripts/test_ollama_harness_numeric_args.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2
- `.claude/rules/bridge-essential.md`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`

## Owner Decisions / Input

No new owner decision was required. The implementation remained within the live GO, `WI-4393`, and the active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` reliability authorization.

## Prior Deliberations

- `DELIB-20260897` - prior VERIFIED Ollama Phase 2 dispatch wiring baseline.
- `DELIB-20260909` - prior VERIFIED Ollama dispatch failure-hardening baseline.
- `DELIB-20260901` - prior VERIFIED Ollama full LO dispatch test update baseline.
- `DELIB-20260907` - prior VERIFIED Ollama LO dispatch session propagation baseline.
- `DELIB-20260606-OLLAMA-MODEL-SOT-DIRECTIVE` - owner fixed Ollama harness D model routing as `qwen3-coder-next:cloud`.
- `bridge/gtkb-ollama-tool-numeric-argument-coercion-003.md` - approved implementation proposal.
- `bridge/gtkb-ollama-tool-numeric-argument-coercion-004.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `.claude/rules/file-bridge-protocol.md` | Live latest status was `GO` before implementation. `python .claude\skills\bridge\helpers\impl_report_bridge.py plan gtkb-ollama-tool-numeric-argument-coercion` computed `NEW: bridge/gtkb-ollama-tool-numeric-argument-coercion-005.md` with latest status `GO`. This report is filed back into the same thread. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `.claude/rules/codex-review-gate.md` | `python scripts\implementation_authorization.py activate --bridge-id gtkb-ollama-tool-numeric-argument-coercion` produced active packet hash `sha256:3a2f2039310af1ae136bd7a5a60a178b9dda5e9f296897c0d18d861afdef1b45` with target scope limited to `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness_numeric_args.py`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests cover accepted numeric forms, rejected numeric forms, and omitted-default behavior for `Read`, `Grep`, and `Glob`. Existing `platform_tests/scripts/test_ollama_harness.py` also passed to preserve guard behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation files are under `E:\GT-KB`: `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness_numeric_args.py`. |
| `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`; `DCL-SMART-POLLER-AUTO-TRIGGER-001`; `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`; `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`; `.claude/rules/bridge-essential.md`; startup overlay surfaces | `python scripts\verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB` returned `ready: true` for recipient `D`, route `qwen3-coder-next-cloud`, model `qwen3-coder-next:cloud`, and required tools. `python scripts\cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.gtkb-state\bridge-poller --diagnose --include-rotated-failures` returned `HEALTHY: dispatch state is current; recipients functioning per design.` |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The implementation proceeded through indexed bridge GO, implementation-start packet evidence, focused tests, readiness checks, and this post-implementation report without owner interruption or out-of-band artifact mutation. |

## Commands Run

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-ollama-tool-numeric-argument-coercion
python scripts\implementation_authorization.py activate --bridge-id gtkb-ollama-tool-numeric-argument-coercion
rg -n 'int\(arguments\.get\("(max_chars|max_results)"|max_chars = int|max_results = int|_positive_int_argument' scripts\ollama_harness.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness_numeric_args.py platform_tests\scripts\test_ollama_harness.py -q --tb=short
$env:PYTHONPATH='scripts'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness_numeric_args.py platform_tests\scripts\test_ollama_harness.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness_numeric_args.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness_numeric_args.py
python scripts\verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion
python scripts\cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.gtkb-state\bridge-poller --diagnose --include-rotated-failures
```

## Observed Results

- Implementation authorization `begin` succeeded for `gtkb-ollama-tool-numeric-argument-coercion`; first mutation attempt was blocked because another active Prime packet had overwritten `current.json` before the patch.
- Implementation authorization `activate` restored the named Ollama packet to `current.json`; the scoped source/test patch then succeeded.
- Direct-cast check returned only the new helper and its three approved call sites:

```text
558:def _positive_int_argument(arguments: Mapping[str, Any], name: str, default: int) -> int:
582:    max_chars = _positive_int_argument(arguments, "max_chars", MAX_TOOL_OUTPUT_CHARS)
639:    max_results = _positive_int_argument(arguments, "max_results", MAX_GREP_RESULTS)
660:    max_results = _positive_int_argument(arguments, "max_results", MAX_GLOB_RESULTS)
```

- Initial pytest command without `PYTHONPATH` failed during collection with existing import-path error `ModuleNotFoundError: No module named 'gtkb_session_id'` in both the new focused test and existing `platform_tests/scripts/test_ollama_harness.py`.
- Rerun with `PYTHONPATH=scripts` passed: `69 passed, 1 warning in 1.29s`. The warning was a pytest cache-path warning: `could not create cache path E:\GT-KB\.pytest_cache\v\cache\nodeids` because a cache path already exists as a file.
- Ruff lint passed: `All checks passed!`.
- Ruff format check passed: `2 files already formatted`.
- Ollama readiness passed with `ready: true`, recipient `D`, route `qwen3-coder-next-cloud`, model `qwen3-coder-next:cloud`, and required tools `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`.
- Bridge applicability preflight passed on the operative proposal: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- ADR/DCL clause preflight passed: clauses evaluated `5`, evidence gaps in `must_apply` clauses `0`, blocking gaps `0`.
- Cross-harness trigger diagnosis reported overall healthy dispatch state. It still lists historical rotated failure counts, but current recipient liveness is healthy.

## Files Changed

Implementation-scoped files:

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness_numeric_args.py`

Worktree scope note:

- The broader worktree contains unrelated dirty files from concurrent or prior work. They are not part of this implementation report.
- `harness-state/harness-registry.json` was touched by canonical role-projection during role resolution; the content diff was restored. Git may still report it modified due line-ending normalization, but no implementation change is claimed for that file.

## Acceptance Criteria Status

- [x] `Read.max_chars`, `Grep.max_results`, and `Glob.max_results` no longer use direct `int(...)` casts.
- [x] Native positive integers, native integral floats, decimal integer strings, and integral float strings are accepted.
- [x] Booleans, zero, negative values, nonintegral values, empty strings, and malformed strings raise `OllamaHarnessError`.
- [x] Optional omitted numeric arguments still use the existing defaults.
- [x] Existing Ollama harness guard behavior tests still pass.
- [x] Scoped lint, format, readiness, bridge preflight, clause preflight, and bridge-trigger diagnosis were run and recorded.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: This is a repair to broken Ollama harness dispatcher behavior. It adds focused tests but does not add a new user-facing capability surface.

## Risk And Rollback

Residual risk is low. The parser now accepts only positive integral values for the bounded fields and rejects broad malformed input through the harness error path. The main compatibility change is that explicit `0`, empty string, and boolean values no longer fall through to defaults; this is intentional per the approved proposal.

Rollback is a normal revert of `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness_numeric_args.py`, followed by a corrective bridge report or proposal if Loyal Opposition finds drift.

## Report Preflight On Completed Draft

- Applicability preflight command: `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-ollama-tool-numeric-argument-coercion-005.md`.
- Applicability preflight result: packet hash `sha256:cc53e22079379dbaac259c3520781b7cb0103f1a4e0feed4ce14a458b701177d`; `content_source: pending_content`; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- ADR/DCL clause preflight command: `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-ollama-tool-numeric-argument-coercion-005.md`.
- ADR/DCL clause preflight result: clauses evaluated `5`; `must_apply: 3`; `may_apply: 2`; evidence gaps in `must_apply` clauses `0`; blocking gaps `0`; exit code `0`.

## Loyal Opposition Asks

1. Verify that the implementation satisfies `bridge/gtkb-ollama-tool-numeric-argument-coercion-003.md` and GO `-004`.
2. Return `VERIFIED` if the source/test changes and command evidence satisfy the linked specifications; otherwise return `NO-GO` with exact findings.
