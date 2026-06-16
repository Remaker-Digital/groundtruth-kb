REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ed143-b414-7a70-aecb-ec719a6d6c27
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop; Prime Builder role; WI-4556 remediation session

# WI-4556 Ollama Provider Fallback Backoff - Revised Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi-4556-ollama-provider-fallback-backoff
Version: 005 (REVISED; post-implementation report revision after NO-GO 004)
Responds-To: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-004.md
Reviewed GO: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-002.md
Approved Proposal: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-001.md
Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4556
Recommended commit type: fix:
target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-*.md"]

---

## Revision Claim

This revision addresses the two findings in Loyal Opposition NO-GO 004. The live checkout now reproduces the WI-4556 behavior tests and the full focused verification lane. The remaining correction was not a provider-backoff algorithm change; it was a no-index fixture and reporting mismatch:

- Synthetic bridge fixtures in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` now add lifecycle status tokens to numbered fixture bridge files when old INDEX-shaped helper bodies omit them. This makes the test fixture match the current no-index bridge renderer, which reads status-bearing numbered files.
- `scripts/cross_harness_bridge_trigger.py` now emits the documented `index_signature_post` diagnostic key again while still hashing the rendered live bridge state.
- Ollama and OpenRouter Bash guard tests now attempt to mutate an existing numbered bridge file instead of the retired `bridge/INDEX.md`, matching the current protected artifact invariant.
- `scripts/verify_ollama_dispatch.py` is explicitly disclosed as changed. Its HEAD-relative diff removes fixture INDEX mutation from the verification script and checks the numbered bridge file status instead; ruff formatting was also applied.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-TAFE-R4`
- `SPEC-TAFE-R5`
- `SPEC-TAFE-R6`

## Owner Decisions / Input

No new owner decision is required for this revision. The implementation remains within the owner authorization recorded in `DELIB-20263381` / `AUQ-2026-06-14-COST-AUTODISPATCH-WI-4556`.

## Prior Deliberations

- `DELIB-20263381` / `AUQ-2026-06-14-COST-AUTODISPATCH-WI-4556` - owner authorization for bounded WI-4556 provider-failure handling, fallback/backoff behavior, stale worker suppression, and focused regression tests.
- `DELIB-20261075` - dispatch reliability investigation identifying max-turn exhaustion, no-verdict completion, missing outcome feedback, and self-review guard issues.
- `DELIB-20263076` - ordered fallback routing GO for WI-4484; WI-4556 builds on that substrate rather than duplicating it.
- `DELIB-20263438` - owner decision that role assignment, dispatchability, and routing are independent.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-001.md` - approved implementation proposal.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-002.md` - Loyal Opposition GO verdict authorizing bounded implementation.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-003.md` - original implementation report.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-004.md` - Loyal Opposition NO-GO requiring live verification repair and accurate file-change accounting.

## Findings Addressed

### F1 - Required behavior tests failed live

Response: Fixed the synthetic bridge fixtures so numbered bridge files carry status tokens in addition to their compatibility INDEX rows. The trigger now sees the fixture `NEW` item through `_read_bridge_state_live`, so the same selected-batch signature exists on the second dispatch attempt and provider-failure backoff selects the alternate OpenRouter target. The two WI-4556 behavior tests now pass live.

Evidence:

```text
$env:GTKB_NO_CROSS_HARNESS_TRIGGER='';
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .pytest-tmp-wi4556-pb-repro2 platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_provider_failure_backoff_falls_back_after_max_turn_marker platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_exit_zero_without_verdict_backs_off_and_falls_back -q --tb=short
```

Observed result:

```text
2 passed, 1 warning in 0.50s
```

### F2 - `scripts/verify_ollama_dispatch.py` was changed but reported unchanged

Response: This revised report no longer lists `scripts/verify_ollama_dispatch.py` as unchanged. The file is part of the approved target paths and is included in the changed-file list below. Its HEAD-relative diff removes retired fixture INDEX writes from the Ollama dispatch verifier and checks the numbered bridge file status token instead; a final ruff pass also compacted one `_print_result` expression.

Evidence:

```text
git diff --cached -- scripts/verify_ollama_dispatch.py
git diff -- scripts/verify_ollama_dispatch.py
```

Observed result: the cached diff contains no-index fixture cleanup in `_check_bridge_filing_via_dispatch` and `_check_guard_bridge_bash_denial`; the unstaged diff after ruff format is a one-expression formatting change. The file is now disclosed as changed in this report.

## Scope Changes

No owner-scope expansion is introduced. This revision stays within the approved WI-4556 target paths. It adds a focused fixture repair and diagnostic key restoration needed to make the approved provider-failure implementation verifiable in the current no-index bridge architecture.

## Pre-Filing Preflight Subsection

The governed revision helper runs the candidate-content preflights before publishing this file:

```text
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\revise_bridge.py file gtkb-wi-4556-ollama-provider-fallback-backoff --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi-4556-ollama-provider-fallback-backoff-005.md
```

Expected helper gates:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff --content-file <candidate> --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff --content-file <candidate>`

This report was not written live until those helper gates passed.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff` issued packet `sha256:c24fee6bfa181d471ef910c4193c7ee55a6e0772ac5c965477bb5aa4506afbcd` for the approved target globs before this revision changed protected files. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-TAFE-R5`, `SPEC-TAFE-R6` | The two WI-4556 behavior tests pass and prove provider/output failure plus no-verdict completion back off the failed provider and select the alternate ready target. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-TAFE-R4` | The full focused dispatch lane passes with current no-index bridge fixture state and preserves selected-batch semantics. |
| WI-4556 duplicate/stale worker suppression | The passing behavior tests seed the same selected-batch signature and assert the failed provider is skipped with `provider_failure_backoff_active` instead of relaunched. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, and ruff format-check all pass after the revision. |
| No-index bridge invariant | `Test-Path bridge\INDEX.md` returned `False`; the revision does not recreate the retired index. |

## Code Quality Baseline

The final quality baseline for the approved WI-4556 target set is:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
```

Observed result:

```text
All checks passed!
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
```

Observed result:

```text
9 files already formatted
```

## Commands Run

```text
$env:GTKB_NO_CROSS_HARNESS_TRIGGER='';
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .pytest-tmp-wi4556-pb-full3 platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
```

Observed result:

```text
124 passed, 1 warning in 6.16s
```

```text
Test-Path bridge\INDEX.md
```

Observed result:

```text
False
```

Warnings: pytest still reports the pre-existing `PytestConfigWarning: Unknown config option: asyncio_mode`. No WI-4556 test failed.

## Files Changed

HEAD-relative WI-4556 target-path changes now include:

- `scripts/cross_harness_bridge_trigger.py`
- `scripts/verify_ollama_dispatch.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-003.md`
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-004.md`
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-005.md`

Approved target-path files that remain unchanged relative to HEAD:

- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py` was changed only by this revision's guard-test alignment.

Pre-report diff stat before adding this `005` file:

```text
 ...wi-4556-ollama-provider-fallback-backoff-003.md | 249 +++++++++++++
 ...wi-4556-ollama-provider-fallback-backoff-004.md | 255 ++++++++++++++
 .../src/groundtruth_kb/bridge_dispatch_config.py   |   6 +-
 .../scripts/test_bridge_dispatch_config.py         |   4 +-
 .../scripts/test_cross_harness_bridge_trigger.py   | 191 ++++++++++
 platform_tests/scripts/test_ollama_harness.py      |  16 +-
 platform_tests/scripts/test_openrouter_harness.py  |  12 +-
 scripts/cross_harness_bridge_trigger.py            | 388 ++++++++++++++++-----
 scripts/verify_ollama_dispatch.py                  |  51 +--
 9 files changed, 1030 insertions(+), 142 deletions(-)
```

## Acceptance Criteria Status

- [x] A launched worker that exits without a bridge verdict no longer remains a clean `launched` success state for LO dispatch.
- [x] Provider/output failures are recorded as operational dispatch evidence.
- [x] Same selected-batch provider failures suppress duplicate relaunch of the failed target while an alternate eligible backend is available.
- [x] Fallback to the next eligible backend preserves role, selected batch, dispatchability, and configured candidate ordering gates.
- [x] Focused regression tests, lint, and format checks passed in the live checkout after the NO-GO correction.
- [x] `bridge/INDEX.md` remains absent.
- [x] `scripts/verify_ollama_dispatch.py` is accurately disclosed as changed.

## Risk And Rollback

Residual risk remains bounded to dispatch target selection, completed-worker status processing, and no-index fixture compatibility. The revision's source change is deliberately small: restore a documented diagnostic key and align tests/verification fixtures with numbered status-bearing bridge files.

Rollback is a single implementation commit revert for the changed dispatcher, verifier, and test files while preserving append-only bridge audit files. Rollback must not recreate `bridge/INDEX.md` and must preserve the earlier WI-4484 ordered fallback behavior unless a future bridge explicitly authorizes otherwise.

## Loyal Opposition Asks

1. Verify that the NO-GO 004 findings are addressed by the live test evidence and file-change accounting above.
2. Return `VERIFIED` if the revised implementation report and current diff satisfy the approved WI-4556 proposal; otherwise return `NO-GO` with concrete findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
