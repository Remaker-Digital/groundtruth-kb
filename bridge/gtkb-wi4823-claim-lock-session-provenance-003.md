NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T15-54-29Z-prime-builder-A-8e0644
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: dispatcher-spawned headless Prime Builder; approval_policy=never; workspace=E:\GT-KB; active role=prime-builder
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Report - Work-intent claim locking and session provenance

bridge_kind: implementation_report
Document: gtkb-wi4823-claim-lock-session-provenance
Version: 003 (NEW; post-implementation report)
Date: 2026-07-06 UTC
Responds to GO: bridge/gtkb-wi4823-claim-lock-session-provenance-002.md
Approved proposal: bridge/gtkb-wi4823-claim-lock-session-provenance-001.md
Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4823
Recommended commit type: test:

## Implementation Claim

The approved implementation scope was inspected against the current tree and the existing claim/authorization implementation already enforced the core WI-4823 behavior. This report adds focused regression coverage in `platform_tests/scripts/test_bridge_work_intent_registry.py` rather than changing production code that is already present and passing.

The new tests cover the two WI-4823 failure modes directly:

- `test_go_impl_peer_claim_stays_locked_until_lapsed_then_reacquires` proves a same-thread GO implementation claim remains exclusive while live, refuses a peer Prime session, lapses after deadline plus grace, and can then be reacquired by the peer.
- `test_impl_authorization_refuses_borrowed_work_intent_claim` proves `implementation_authorization.work_intent_claim_block_reason(...)` refuses a caller trying to use another session's active bridge claim as implementation provenance.

No source-code hunk was needed in this dispatch. The durable implementation is in the existing registry and authorization paths:

- `scripts/bridge_work_intent_registry.py` holds one claim per `thread_slug`, records GO claims as `go_implementation`, ignores lapsed GO claims, and preserves takeover only after expiry/lapse.
- `scripts/implementation_authorization.py` requires the caller session to hold the bridge's active work-intent claim before minting or using implementation authorization evidence.
- Dispatcher batching already filters held Prime work-intent claims and serializes overlapping target paths in `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher architecture must prevent duplicate implementations and false provenance.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - concurrency and provenance behavior must be enforced across harnesses.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4823`.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorization for Harness Parity Phase 2 implementation scope.

No new owner decision was required in this headless dispatch.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - parent owner authorization cited by the proposal.
- `DELIB-20266137` - related owner decision requiring de-confliction with a concurrent Prime session and claim/check discipline before drafting.
- `DELIB-20261534` / `DELIB-2798` - prior VERIFIED work-intent registry integration review, establishing the base claim CLI and enforcement surface.
- `bridge/gtkb-wi4823-claim-lock-session-provenance-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4823-claim-lock-session-provenance-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | `test_go_impl_peer_claim_stays_locked_until_lapsed_then_reacquires` and dispatcher work-intent batching tests prove duplicate same-thread Prime implementation claims fail closed while live. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Registry, CLI, and dispatcher tests cover dispatch-format Prime session ids, peer holders, held-work filtering, and mismatch refusal without relying on a single harness. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live bridge state was read through `gt bridge show`; implementation-start authorization was created from latest `GO`; this report is being filed as the next numbered bridge file. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward linked specifications and exact executed command evidence below. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `implementation_authorization.py begin --bridge-id gtkb-wi4823-claim-lock-session-provenance` succeeded with the active PAUTH, live GO, and scoped target paths. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\gt.exe harness roles
```

Observed result: Codex harness `A` is active and assigned `prime-builder`.

```text
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status --json
groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi4823-claim-lock-session-provenance --json
```

Observed result: latest status remains `GO` at `bridge/gtkb-wi4823-claim-lock-session-provenance-002.md`; the version chain is `NEW` then `GO`.

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4823-claim-lock-session-provenance
```

Observed result: authorized `true` equivalent via exit 0; packet hash `sha256:711d3f4b846da709404974a280b23441a520b01a5b19e7a8dd5ed4cd3f59121c`; target path globs matched the approved six-file scope.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_dispatcher_runtime_work_intent.py -q --tb=short --basetemp .harness-tmp\pytest-wi4823
```

Observed result: `46 passed, 6 warnings in 39.63s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_implementation_authorization.py -q --tb=short --basetemp .harness-tmp\pytest-wi4823-auth
```

Observed result: `124 passed, 2 warnings in 13.66s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\bridge_work_intent_registry.py scripts\bridge_claim_cli.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_dispatcher_runtime_work_intent.py
```

Observed result: `All checks passed!`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\bridge_work_intent_registry.py scripts\bridge_claim_cli.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_dispatcher_runtime_work_intent.py
```

Observed result: `6 files already formatted`.

Supporting check attempted:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\skills\test_bridge_impl_report_helper.py -q --tb=short --basetemp .harness-tmp\pytest-wi4823-report-helper
```

Observed result: `6 failed, 14 passed, 3 warnings in 36.19s`. The failures are not used as positive WI-4823 verification evidence: they occur in unrelated dirty helper/test surfaces (`.claude/skills/bridge/helpers/impl_report_bridge.py` and `platform_tests/skills/test_bridge_impl_report_helper.py`) because the live bridge writer now enforces project-membership validation on fixture metadata `PAUTH-PROJECT-TEST` / `WI-1234`. Those files are outside this bridge's approved target paths and are already dirty before this report.

## Observed Results

- The selected bridge thread was actionable for Prime Builder and remained latest `GO` before report filing.
- Implementation-start authorization succeeded for the selected GO and scoped target paths.
- The focused target suite now includes 46 tests and passes.
- The broader authorization suite passes with 124 tests, preserving existing current/named packet invariants while the new WI-4823 mismatch-refusal test covers borrowed-claim denial.
- Ruff lint and format checks pass on the approved source/test target set.

## Files Changed

- `platform_tests/scripts/test_bridge_work_intent_registry.py` - added two WI-4823 regressions covering same-thread GO claim exclusivity/lapsed takeover and mismatched-session claim refusal.
- `bridge/gtkb-wi4823-claim-lock-session-provenance-003.md` - this implementation report, filed through the bridge helper.

Focused diff stat for the implementation test change:

```text
platform_tests/scripts/test_bridge_work_intent_registry.py | 59 ++++++++++++++++++++++
1 file changed, 59 insertions(+)
```

The rest of the repository was already dirty before this dispatch. This report does not claim or verify unrelated dirty files.

## Recommended Commit Type

- Recommended commit type: `test:`
- Rationale: this dispatch adds focused regression coverage for behavior already present in the approved claim/authorization implementation paths.

## Acceptance Criteria Status

- [x] A second Prime implementer cannot begin the same GO slice while a valid claim exists: covered by `test_go_impl_peer_claim_stays_locked_until_lapsed_then_reacquires`, existing CLI peer-holder coverage, and dispatcher held-work filtering.
- [x] A report or mutation path cannot borrow another session's claim context as implementation provenance: covered by `test_impl_authorization_refuses_borrowed_work_intent_claim`.
- [x] Stale/lapsed claims still release through intended lifecycle: covered by `test_go_impl_peer_claim_stays_locked_until_lapsed_then_reacquires` and existing lapsed-claim tests.

## Risk And Rollback

Risk is low because the live change is test-only and does not alter production claim/authorization behavior. Rollback is removal of the two added tests from `platform_tests/scripts/test_bridge_work_intent_registry.py` plus this bridge report; bridge history remains append-only.

## Loyal Opposition Asks

1. Verify the two added WI-4823 regression tests against the linked specifications.
2. Confirm the unrelated helper provenance-suite failures are out of scope for this bridge and should not block this report.
3. Return `VERIFIED` if the implementation evidence satisfies the approved proposal; otherwise return `NO-GO` with concrete findings.

