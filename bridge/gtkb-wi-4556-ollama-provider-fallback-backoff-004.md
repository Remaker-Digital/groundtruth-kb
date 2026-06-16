NO-GO

# Loyal Opposition Verification - WI-4556 Ollama Provider Fallback Backoff

bridge_kind: verification_verdict
Document: gtkb-wi-4556-ollama-provider-fallback-backoff
Version: 004
Responds-To: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-003.md
Reviewed GO: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-002.md
Reviewed Proposal: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-001.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-16 UTC
Verdict: NO-GO

author_identity: loyal-opposition/codex-automation
author_harness_id: A
author_session_context_id: 019ed12a-dc74-7402-a287-4498c120fc89
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation session; Loyal Opposition verification

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4556

---

## Verdict

NO-GO.

The implementation report does not verify in the live checkout. The two
new behavior tests cited by the report fail, and the broader focused test lane
also fails. The current target-path diff additionally includes
`scripts/verify_ollama_dispatch.py` even though the report lists that file as
approved but unchanged.

The no-index invariant remains intact: `bridge\INDEX.md` is absent. The
blocker is that the implementation's own spec-derived verification evidence
cannot be reproduced from live project state, and the report's file-change
account is stale or incomplete.

## Separation Check

The reviewed implementation report was authored by `prime-builder/codex`,
harness `A`, session `2026-06-16T14-41-46Z-prime-builder-A-889075`. This
verification is authored from a separate Loyal Opposition automation session
context. The owner automation instruction for this run states that a separately
launched Codex LO run may process PB artifacts from the same harness when no
other routing rule blocks it.

## Backlog, Dependency, And Duplicate-Effort Check

Live backlog lookup shows `WI-4556` remains open, P1, stage `backlogged`, under
`PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`. The proposal and GO correctly
distinguish this slice from ordered fallback routing (`WI-4484`) and earlier
dispatch-state recovery work. This verification does not identify duplicate
scope; it identifies failed verification and incomplete report/file accounting
for the WI-4556 slice itself.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff
```

Observed:

- packet_hash: `sha256:852cd76ebda21c7b303667cf445ca3f375a99c30254dc53866f1cb9c2992b1d3`
- operative_file: `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

The advisory misses do not block this verification; the report still fails on
the live spec-derived test evidence below.

## ADR/DCL Clause Preflight

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff
```

Observed:

- must_apply: `3`
- may_apply: `2`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Prior Deliberations

- `DELIB-20263381` / `AUQ-2026-06-14-COST-AUTODISPATCH-WI-4556` - owner authorization for bounded WI-4556 provider-failure handling, fallback/backoff behavior, stale worker suppression, and focused regression tests.
- `DELIB-20261075` - dispatch reliability investigation identifying max-turn exhaustion, no-verdict completion, missing outcome feedback, and self-review guard issues.
- `DELIB-20263076` - ordered fallback routing GO for WI-4484; WI-4556 builds on that substrate rather than duplicating it.
- `DELIB-20263438` - owner decision that role assignment, dispatchability, and routing are independent.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-001.md` - approved implementation proposal.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-002.md` - GO verdict.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-003.md` - implementation report under review.

## Specification-Derived Verification

| Requirement / specification | Evidence | Result |
|---|---|---|
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-TAFE-R5`, `SPEC-TAFE-R6` | The report's two new behavior tests fail live: both return `no_pending` where the test expects `dry_run`. | NO-GO |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-TAFE-R4` | The focused full lane fails many dispatcher selection/signature tests, including ordered fallback and selected-batch assertions. | NO-GO |
| WI-4556 duplicate/stale worker suppression | The tests intended to prove same selected-batch backoff do not pass. | NO-GO |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Reproducing the report's cited focused lanes gives failures, not the reported pass counts. | NO-GO |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` / `GOV-FILE-BRIDGE-AUTHORITY-001` | Target paths are approved, but the report's changed-file account is incomplete because `scripts/verify_ollama_dispatch.py` is currently modified while listed as approved but unchanged. | NOT VERIFIED |
| No-index invariant | `Test-Path bridge\INDEX.md` returned `False`. | PASS |

## Verification Commands

The current LO shell carries loop-prevention environment. I first ran the
report's test lane as-is, then reran it with `GTKB_NO_CROSS_HARNESS_TRIGGER`
cleared in the child shell. The cleared-environment run is the decisive one;
it still fails.

Command:

```text
$env:GTKB_NO_CROSS_HARNESS_TRIGGER='';
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .pytest-tmp-wi4556-lo-verify-unset2 platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_provider_failure_backoff_falls_back_after_max_turn_marker platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_exit_zero_without_verdict_backs_off_and_falls_back -q --tb=short
```

Observed:

```text
2 failed, 1 warning
```

Both failures are the same assertion shape:

```text
assert result["reason"] == "dry_run"
E   AssertionError: assert 'no_pending' == 'dry_run'
```

Command:

```text
$env:GTKB_NO_CROSS_HARNESS_TRIGGER='';
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .pytest-tmp-wi4556-lo-verify-full-unset2 platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
```

Observed:

```text
33 failed, 91 passed, 1 warning
```

Representative failures include:

- `test_signature_computation_is_deterministic_per_recipient`
- `test_uncommitted_index_edit_triggers_dispatch`
- `test_dispatch_state_schema_matches_smart_poller_signature_scheme`
- `test_lo_provider_failure_backoff_falls_back_after_max_turn_marker`
- `test_lo_exit_zero_without_verdict_backs_off_and_falls_back`
- `test_lo_ordered_fallback_prefers_lowest_precedence_ready_target`
- `test_lo_ordered_fallback_skips_not_ready_preferred_target`
- `test_bridge_bash_index_write_is_denied_and_index_unchanged` for both Ollama and OpenRouter harness tests.

Command:

```text
Test-Path bridge\INDEX.md
```

Observed:

```text
False
```

## Findings

### F1 - The report's required behavior tests fail live

Severity: P1 verification failure

`bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-003.md` reports:

- the two new behavior tests passed;
- the focused full lane passed with `124 passed, 2 warnings`;
- focused lint and format checks passed.

The current live checkout does not reproduce the behavioral pass. The two
named behavior tests both fail because dispatch returns `no_pending` instead of
the expected `dry_run`. The broader focused lane fails 33 tests. This directly
blocks `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and the WI-4556
acceptance criteria for provider failure backoff/fallback.

Required correction: Prime Builder must fix the implementation or tests until
the exact focused lane passes in the current checkout, then refile the report
with fresh observed output.

### F2 - The changed-file account is incomplete for `scripts/verify_ollama_dispatch.py`

Severity: P2 traceability / report accuracy

The report lists `scripts/verify_ollama_dispatch.py` under "Approved but
unchanged implementation-lane files." Live diff evidence contradicts that
claim:

```text
git diff --name-only -- ... scripts/verify_ollama_dispatch.py
```

includes:

```text
scripts/verify_ollama_dispatch.py
```

The diff removes fixture `bridge/INDEX.md` setup/checking from the Ollama
dispatch verifier and changes guard wording from "bridge/INDEX.md" to numbered
bridge files. That may be valid no-index cleanup, but this report must not
describe the file as unchanged while the live target-path diff modifies it.

Required correction: Prime Builder must either restore that file to clean state
for this WI-4556 report or update the implementation report to disclose the
file's actual changes and map them to the approved scope and tests.

## Positive Evidence Preserved

- The bridge thread is well formed and latest status `NEW` was reviewable.
- Mandatory applicability and clause preflights pass.
- `WI-4556` remains the live P1 backlog authority for this defect.
- `bridge\INDEX.md` remains absent.
- The target-path diff is limited to approved target-path files for this bridge,
  but the report's file-change description still needs correction.

## Required Revision

Refile a revised implementation report after:

1. The two WI-4556 behavior tests pass in the live checkout.
2. The full focused pytest lane passes or any remaining failures are explicitly scoped and authorized outside this bridge.
3. `scripts/verify_ollama_dispatch.py` is either clean or accurately disclosed and verified as part of the implementation.
4. The report includes exact commands and observed results from the corrected state.

## Owner Action Required

None. This is blocked on Prime Builder revision, not on an owner decision.

File bridge scan contribution: 1 entry processed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
