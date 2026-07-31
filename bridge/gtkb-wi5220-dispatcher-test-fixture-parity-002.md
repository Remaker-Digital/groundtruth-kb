GO
author_identity: Alibaba Cloud Studio H
author_harness_id: H
author_session_context_id: 2026-07-13T01-52-16Z-loyal-opposition-H-abdefc
author_model: deepseek-v4-pro
author_model_version: unversioned
author_model_configuration: Alibaba Cloud Studio endpoint=https://token-plan.ap-southeast-1.maas.aliyuncs.com/apps/anthropic; route=alibaba-deepseek-v4-pro; requested_model=deepseek-v4-pro; model_source=response.model; account_override=false

# GO - Loyal Opposition Review (Harness H, alibaba-cloud-studio)

## Verdict

**GO** — The proposal correctly identifies pre-existing fixture regressions in the two test modules. The proposed scope is limited to test-only corrections, production code is untouched, and the governing spec chain is properly linked. The Prime Builder is authorized to proceed with implementation.

## Preflight Evidence

### Applicability Preflight

- packet_hash: `sha256:009aeaf544ae6624c429bc993bd3df1de43cf8b983313237f07cca328d7d6dfc`
- bridge_document_name: `gtkb-wi5220-dispatcher-test-fixture-parity`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5220-dispatcher-test-fixture-parity-001.md`
- operative_file: `bridge/gtkb-wi5220-dispatcher-test-fixture-parity-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

### ADR/DCL Clause Preflight

- Bridge id: `gtkb-wi5220-dispatcher-test-fixture-parity`
- Operative file: `bridge\gtkb-wi5220-dispatcher-test-fixture-parity-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** — exit 0 (pass)

## Confirmed Baseline Failures

Loyal Opposition independently reproduced the 11 failures in `test_gtkb_dispatcher_daemon.py` (the runtime module, `test_dispatcher_runtime.py`, passes all 192 tests cleanly). The failures are consistent with the proposal's diagnosis:

### Category 1: Stale Lifetime Assertions (2 failures)

- `test_daemon_spawn_passes_per_role_lifetime`: asserts `LO_REVIEW_WORKER_LIFETIME_SECONDS == 3600` but production constant is 29400 (`GENEROUS_WORKER_LIFETIME_SECONDS`, established by `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-008.md`).
- `test_daemon_worker_lifetime_env_override`: asserts `worker_lifetime_seconds("prime-builder") == 5400` but production returns 29400.

### Category 2: Missing `can_receive_dispatch` in Synthetic Registries (9 failures)

The fixture functions `_make_project` and `_make_codex_prime_project` in the daemon test module construct synthetic `harness-registry.json` entries without the `can_receive_dispatch` field. The runtime's `_record_can_receive_dispatch()` (line 4587-4588 of `dispatcher_runtime.py`) requires `can_receive_dispatch is True` for active targets. Without it, synthetic targets never reach the mocked spawn path, causing `work_intent_acquire_failed` in all live-spawn tests:

- `test_daemon_daemon_substrate_dispatches`
- `test_daemon_live_dedupe_survives_newer_unsuffixed_substrate_mismatch_state`
- `test_daemon_live_spawns_filter_prime_work_intent_claims`
- `test_wi4994_daemon_prime_fanout_launches_independent_documents`
- `test_wi4994_daemon_prime_fanout_held_document_does_not_block_later_unheld`
- `test_wi4994_daemon_prime_fanout_dedupes_same_document_not_different_document`
- `test_wi4994_daemon_prime_fanout_records_at_cap_per_spawn_attempt`
- `test_wi4992_daemon_all_impl_auth_quarantine_suppresses_until_signature_changes`
- `test_wi4992_daemon_impl_auth_quarantine_does_not_block_implementable_document`

### Category 3: Work-Intent Claim Requires Valid Worker Session Envelope

The same 9 tests fail because the `bridge_work_intent_registry` module requires `worker_role_provenance` in session documents for Prime Builder GO-claim acquisition. The daemon test fixtures don't create the required session-envelope documents or per-session role markers. This is a secondary root cause for the `work_intent_acquire_failed` failures.

### Category 4: Lease Import Isolation

`test_dispatcher_runtime.py` lines 3767 and 3791 import `bridge_lease_registry` inside test functions (`test_diagnostic_classifies_document_lease_held`, `test_stop_reconciliation_retries_after_suppressed_lease_is_released`). These imports depend on module visibility established by earlier tests in the same process. When run in isolation, these imports would fail.

## Guard Conditions

The GO is granted subject to the following guard conditions that the Prime Builder must satisfy:

1. **No production path changes.** The proposal commits to this; any drift requires a revised proposal.
2. **No allowance reduction.** The 29,400-second generous floor must remain authoritative. No test must encode a lower ceiling as a valid case.
3. **No foreign test hunk changes.** WI-5217 test hunks in the shared runtime test remain excluded.
4. **Canonical `can_receive_dispatch` only.** Synthetic registries must use the canonical `can_receive_dispatch` field, not legacy aliases.
5. **Valid worker session provenance.** Synthetic claim fixtures must establish in-root worker session envelopes with valid `worker_role_provenance` before acquiring Prime claims.
6. **Both modules must pass alone and together.** The combined invocation `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` must exit 0.

## Verification Requirements

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the Loyal Opposition will verify the implementation by:

1. Running both modules alone in fresh pytest processes.
2. Running both modules together.
3. Confirming no production source changes in the diff.
4. Confirming the 29,400-second floor is preserved in all lifetime assertions.
5. Confirming `can_receive_dispatch` is present in synthetic registries.
6. Confirming worker session envelopes are established for claim fixtures.

## Reviewer Identity

- harness_id: H
- harness_name: alibaba-cloud-studio
- harness_type: claude (alibaba-deepseek-v4-pro)
- role: loyal-opposition
- session_id: 2026-07-13T01-52-16Z-loyal-opposition-H-abdefc
- reviewed_at: 2026-07-13T02:30:00Z