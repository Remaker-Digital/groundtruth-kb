NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# GT-KB Bridge Implementation Report - gtkb-wi5400-cloud-verdict-claim-lifecycle - 003

bridge_kind: implementation_report
Document: gtkb-wi5400-cloud-verdict-claim-lifecycle
Version: 003 (NEW; post-implementation report)
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5400

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]

Responds to GO: bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-002.md
Approved proposal: bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-001.md
Recommended commit type: fix:

## Summary

Implemented WI-5400 cloud LO verdict-claim lifecycle handling. The dispatcher now acquires a Loyal Opposition verdict work-intent claim after trusted worker-session creation and before provider launch, with a TTL at least as long as the worker/document-lease lifetime. Peer-held LO verdict claims now suppress provider launch as neutral contention instead of spending provider time or feeding retry/breaker state.

The cloud harness now renews or reacquires the worker claim before governed `PublishBridgeVerdict` publication. If a peer-held claim race is detected during publication, the run returns structured neutral stand-down evidence after one publish attempt rather than entering the publisher recovery loop. Dispatcher exit reconciliation recognizes that marker as neutral, releases only the worker-owned verdict claims, avoids `no_verdict_produced`, and avoids failure-count or circuit-breaker churn.

No MemBase mutation, dispatcher/TAFE configuration mutation, Git commit/push/history operation, release, deployment, credential lifecycle action, or destructive cleanup was performed.

## Implementation Claim

- Latest bridge status before implementation/reporting: `GO` at `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-002.md`.
- Work-intent claim: `go_implementation`, rowid `32157`, session `019f6668-9974-7d72-a456-826f9a67e627`, acquired `2026-07-17T12:11:37Z`, extended once, TTL/grace through `2026-07-17T13:21:37Z` at reporting time.
- Implementation-start packet created `2026-07-17T12:11:58Z`; pre-start packet hash `sha256:9fcf2bfae236a9c2e73ee1826e72839e36d2e22e382623ce048d44921f81bf03`; packet hash `sha256:77356d14a60d795dc66f6cde19f378fbf6ab2d00e035e4876ff395222800941e`.
- Implementation stayed inside the four approved target paths: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `scripts/cloud_harness_base.py`, and `platform_tests/scripts/test_cloud_harness_base.py`.

## Foreign Work Disclosure

The four WI-5400 target files were clean before the implementation-start packet. This report claims all current hunks in those four files for WI-5400. It does not claim any unrelated dirty work elsewhere in the repository; `impl_report_bridge.py plan --compact` reported `1512` excluded dirty paths outside this implementation report scope.

## Files Changed

- `scripts/dispatcher_runtime.py`
  - Added LO verdict-claim acquisition before provider launch, after trusted worker-session creation and document-lease acquisition.
  - Added neutral peer-held claim suppression with dispatch-suppression evidence rather than dispatch-failure evidence.
  - Stamped launched LO workers with `verdict_claim_session_id` and `verdict_claim_slugs`.
  - Released only worker-owned LO verdict claims on launch failure, selected-document incomplete exit, normal failure exit, or neutral peer-held publication stand-down.
  - Added neutral exit reconciliation for `provider_verdict_claim_peer_stand_down` output so exit-0/no-verdict peer contention does not become `no_verdict_produced`.
- `scripts/cloud_harness_base.py`
  - Added `BridgeVerdictClaimStandDown` with structured JSON evidence.
  - Renewed or reacquired the worker's work-intent claim before calling the governed provider verdict publisher.
  - Converted peer-held verdict claim races into neutral stand-down results instead of `ERROR:` tool output and publisher recovery retries.
- `platform_tests/scripts/test_dispatcher_runtime.py`
  - Added regressions for LO pre-spawn verdict claim acquisition, peer-held claim launch suppression, and neutral exit reconciliation.
- `platform_tests/scripts/test_cloud_harness_base.py`
  - Added explicit claim-helper allowances for existing publisher tests.
  - Added a regression proving peer-held publish claim contention returns neutral stand-down evidence after one provider publish tool call.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-HARNESS-ISOLATION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5400`.
- `DELIB-202666274` - owner-decision deliberation cited by the active project authorization.
- No new owner decision, waiver, credential action, release, deployment, destructive cleanup, or Git history operation is requested by this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-202666173` - prior NO-GO for provider LO governed verdict publication, carried forward from the approved proposal.
- `DELIB-202666250` - prior Alibaba H publisher recovery verification, carried forward from the approved proposal.
- `DELIB-202666178` - WI-5213 prior verification context, carried forward from the approved proposal.
- `DELIB-20265758` and `DELIB-20265754` - verdict/finalization retry context carried forward from the approved proposal.

## Spec-To-Test Mapping

| Spec | Evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Thread state remained latest `GO`; this Prime-authored `NEW` implementation report is version `003` and responds to LO GO `-002`; work-intent claim and implementation-start packet were created before mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This report preserves implementation claim, owner/PAUTH evidence, linked specs, target inventory, command evidence, observed results, residual risk, rollback, and LO asks as durable bridge evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python .codex\skills\bridge\helpers\impl_report_bridge.py plan gtkb-wi5400-cloud-verdict-claim-lifecycle --compact` carried forward the approved linked specification set and reported next version `003`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short` passed `305 passed in 37.94s`, including the new WI-5400 claim-lifecycle regressions. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report includes Project Authorization, Project, Work Item, `target_paths`, owner evidence, and implementation-start packet hashes for the exact authorized scope. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner/PAUTH evidence is explicitly listed; no new owner decision or AskUserQuestion-dependent mutation is embedded. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed paths are in-root GT-KB platform script/test paths; no Agent Red, adopter application, or out-of-root path is involved. |
| `GOV-STANDING-BACKLOG-001` | Work is bound to `WI-5400` under `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`; this report makes the bridge thread LO-actionable rather than silently resolving backlog state. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex self-enforced implementation authorization through `scripts\implementation_authorization.py begin` and target validation; compile, Ruff, format, diff-check, and pytest ran under the Codex/Windows execution surface. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation converts provider-spend-wasting race behavior into durable neutral suppression evidence and bounded worker-owned claim lifecycle state. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The lifecycle advances from approved proposal `GO` to implementation report `NEW`, awaiting independent LO verification; no Prime-authored terminal claim is made. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher tests prove pre-spawn LO claim ownership, peer-held launch suppression, owned-claim cleanup, and neutral exit reconciliation without queue mutation or breaker churn. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | The dispatcher remains the control-plane owner for worker-session creation, document leases, work-intent claims, launch metadata, and exit reconciliation; cloud harnesses use the governed writer and claim registry only. |
| `GOV-HARNESS-ISOLATION-001` | No direct harness contact, runtime reconfiguration, or cross-harness introspection was added; peer detection uses the existing shared work-intent registry and structured claim holder evidence. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Cloud harness tests prove publisher recovery remains bounded and fail-closed for non-contention publication failures while peer-held contention exits neutrally. |

## Commands Executed

```powershell
python scripts\bridge_claim_cli.py claim gtkb-wi5400-cloud-verdict-claim-lifecycle --session-id 019f6668-9974-7d72-a456-826f9a67e627 --ttl-seconds 3600
```

Observed result: exit 0; claim kind `go_implementation`, rowid `32157`, session `019f6668-9974-7d72-a456-826f9a67e627`, implementation deadline `2026-07-17T12:41:37Z`, grace `2026-07-17T12:51:37Z`.

```powershell
python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5400-cloud-verdict-claim-lifecycle --session-id 019f6668-9974-7d72-a456-826f9a67e627
```

Observed result: exit 0 on sequential rerun after claim acquisition; implementation-start packet created with packet hash `sha256:77356d14a60d795dc66f6cde19f378fbf6ab2d00e035e4876ff395222800941e`; pre-start packet hash `sha256:9fcf2bfae236a9c2e73ee1826e72839e36d2e22e382623ce048d44921f81bf03`.

```powershell
python scripts\bridge_claim_cli.py extend gtkb-wi5400-cloud-verdict-claim-lifecycle --session-id 019f6668-9974-7d72-a456-826f9a67e627
```

Observed result: exit 0; claim extended once to implementation deadline `2026-07-17T13:11:37Z`, grace `2026-07-17T13:21:37Z`.

```powershell
python scripts\implementation_authorization.py validate --target scripts\dispatcher_runtime.py
python scripts\implementation_authorization.py validate --target scripts\cloud_harness_base.py
python scripts\implementation_authorization.py validate --target platform_tests\scripts\test_dispatcher_runtime.py
python scripts\implementation_authorization.py validate --target platform_tests\scripts\test_cloud_harness_base.py
```

Observed result: exit 0 for all four targets; each reported `authorized: true`.

```powershell
python -m py_compile scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
```

Observed result: exit 0.

```powershell
python -m pytest platform_tests\scripts\test_cloud_harness_base.py::test_bridge_review_peer_held_publish_claim_stands_down_neutrally platform_tests\scripts\test_cloud_harness_base.py::test_bridge_review_fails_closed_after_repeated_publisher_failures platform_tests\scripts\test_dispatcher_runtime.py::test_wi5400_lo_live_spawn_acquires_verdict_claim_before_provider_launch platform_tests\scripts\test_dispatcher_runtime.py::test_wi5400_lo_peer_held_verdict_claim_suppresses_provider_launch platform_tests\scripts\test_dispatcher_runtime.py::test_wi5400_peer_claim_stand_down_exit_zero_is_neutral_not_missing_verdict -q --tb=short
```

Observed result: exit 0; `5 passed in 2.79s`.

```powershell
python -m pytest platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short
```

Observed result: exit 0; `305 passed in 37.94s`.

```powershell
python -m ruff check scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
```

Observed result: exit 0; `All checks passed!`.

```powershell
python -m ruff format --check scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
```

Observed result: exit 0; `4 files already formatted`.

```powershell
git diff --check -- scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
```

Observed result: exit 0; warnings only that Git may replace LF with CRLF for the four target files.

## Candidate Preflight Evidence

- Candidate applicability preflight: PASS on the draft content before filing. `python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md --json` exited 0 with `preflight_passed: true`, `blocking_errors: []`, `missing_required_specs: []`, and `missing_advisory_specs: []`. Reported candidate packet hash before this evidence section was populated: `sha256:fd3884e437a73ba156248993abd9c2a42da4bd7f3754f66ad5af8481c1acc441`.
- Candidate ADR/DCL clause preflight: PASS on the draft content before filing. `python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md` exited 0 with 5 clauses evaluated, 4 `must_apply`, 0 evidence gaps in `must_apply` clauses, and 0 blocking gaps.
- Live preflights will be rerun after the helper writes `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md`.

## Acceptance Criteria Result

- A cloud LO worker with a missing or expired own claim renews or reacquires it and publishes through the governed bridge writer: PASS. `_dispatch_publish_bridge_verdict()` calls `_ensure_provider_verdict_claim()` before loading the governed publisher, and existing publisher tests assert the helper is invoked with the dispatcher session id.
- A peer-held claim detected before launch causes no provider spawn or usage and no failure-count or circuit-breaker change: PASS. `test_wi5400_lo_peer_held_verdict_claim_suppresses_provider_launch` asserts spawn is not called, the reason is `lo_verdict_claim_held`, evidence is written to suppressions, and failures remain empty.
- A peer-held race detected during publication produces structured neutral stand-down evidence without four publisher retries and without `subprocess_execution_failed`: PASS. `test_bridge_review_peer_held_publish_claim_stands_down_neutrally` asserts a single publish tool call returns JSON with `reason: provider_verdict_claim_peer_stand_down`; `test_wi5400_peer_claim_stand_down_exit_zero_is_neutral_not_missing_verdict` asserts dispatcher exit reconciliation does not produce `no_verdict_produced` or failure-count churn.
- Launch failure and incomplete worker exit release only claims owned by that worker session; successful publication retains the writer release contract: PASS. Dispatcher code releases stamped `verdict_claim_slugs` with the recorded worker session on launch failure and incomplete/failure/neutral exits. `publish_lo_verdict()` remains responsible for successful publication release.
- Focused cloud-harness and dispatcher-runtime regressions pass while existing malformed-publication failures and full runtime allowances remain unchanged: PASS. Full focused files passed `305 passed in 37.94s`, including the existing repeated publisher failure test.

## Residual Risk

Residual risk is moderate because the dispatcher now coordinates two related concurrency primitives for LO work: document leases and verdict work-intent claims. The implementation keeps the lease as the coarse per-document worker ownership guard and adds the verdict claim as the publisher/writer ownership guard. The focused tests cover pre-spawn acquisition, peer-held suppression, launch failure cleanup, publication-time stand-down, and exit reconciliation, but live fleet behavior should still be observed for duplicate suppressions and claim TTL tuning under heavy multi-LO saturation.

The overall black-box bridge/TAFE/harness program is not claimed terminal by this report. WI-5400 only corrects one cloud verdict-claim lifecycle defect and then returns the thread for independent Loyal Opposition verification.

## Rollback

Rollback is a normal revert of the WI-5400 hunks in:

- `scripts/dispatcher_runtime.py`
- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_cloud_harness_base.py`

Bridge files, claim records, implementation-start packets, and project authorization evidence are append-only audit artifacts and must not be deleted as rollback.

## Recommended Commit Type

Recommended commit type: `fix:`. This implementation repairs a fleet-runtime defect where peer-held verdict claims caused provider-spend waste, publisher recovery loops, and false failure classification.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
