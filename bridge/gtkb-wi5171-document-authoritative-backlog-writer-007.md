NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive session; owner established prime-builder role with ::init gtkb pb.

# GT-KB Bridge Implementation Report - gtkb-wi5171-document-authoritative-backlog-writer - 007

bridge_kind: implementation_report
Document: gtkb-wi5171-document-authoritative-backlog-writer
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5171-document-authoritative-backlog-writer-006.md
Approved proposal: bridge/gtkb-wi5171-document-authoritative-backlog-writer-005.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES
Work Item: WI-5171
Recommended commit type: test

## Implementation Claim

All implementation outputs, tests, and bridge-report artifacts for this work
remain under E:\GT-KB.

Implemented the document-authoritative worker-role correction for the canonical
backlog writers. Every worker session now has a session-keyed authority document
under `harness-state/<harness>/session-envelopes/`; the shared
`session-envelope.json` remains a compatibility projection only. The resolver
selects the exact session document, validates its role provenance and
session/harness consistency, and fails closed for missing, malformed, stale,
conflicting, ambiguous, or peer-session evidence.

`gt backlog add`, `gt backlog update`, and `gt backlog add-work-item` now
pass their configured project root to the document resolver before opening a
write path. They derive `changed_by` only from the validated document role and
never from dispatcher configuration, registry role, marker state, vendor
identity, or model identity. The startup path establishes worker evidence before
marker, lifecycle, or activity work. The new tests make the GOV v5 and DCL v6
matrix explicit and executable.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` v5
- `DCL-SESSION-ROLE-RESOLUTION-001` v6
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-ENVELOPE-META-MODEL-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-202666073` authorizes the bounded WI-5171/WI-5086 document-role
  correction under the active PAUTH.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-GOV-V5-FORMALIZATION-RESULT`
  approved the GOV v5 worker-envelope authority inventory.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-DCL-V6-APPROVAL`
  approved the DCL v6 ten-assertion inventory.
- The owner-directed document-only attribution boundary is implemented as
  approved: dispatch confirms intent only; it does not supply the writer role.

## Prior Deliberations

- `DELIB-202666073`
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-GOV-V5-FORMALIZATION-RESULT`
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-DCL-V6-APPROVAL`
- `bridge/gtkb-wi5171-document-authoritative-backlog-writer-005.md`
- `bridge/gtkb-wi5171-document-authoritative-backlog-writer-006.md`

## Specification-Derived Verification Plan

| Governing assertion | Executed primary evidence | Result |
| --- | --- | --- |
| GOV v5.1 explicit dispatch role/run/session evidence | `test_ensure_worker_session_writes_the_document_role_authority`; `test_dispatch_role_bootstrap_accepts_matching_document` | PASS |
| GOV v5.2 document-only worker bootstrap | `test_role_dcl_a2_canonical_writer_delegates_only_to_document_provenance` | PASS |
| GOV v5.3 audit-only mismatch | `test_dispatch_role_bootstrap_reports_mismatch_without_substituting_worker_role` | PASS |
| GOV v5.4 role bootstrap before activity work | `test_role_dcl_a4_worker_bootstrap_precedes_marker_and_lifecycle_loading` | PASS |
| GOV v5.5 invalid evidence fails before writer work | both `test_role_dcl_a5_*` tests | PASS |
| ROLE-DCL-A1 complete delivered dispatch evidence | worker-envelope and dispatched-bootstrap tests in the 62-test role-authority command | PASS |
| ROLE-DCL-A2 document-only worker bootstrap | `test_role_dcl_a2_canonical_writer_delegates_only_to_document_provenance` | PASS |
| ROLE-DCL-A3 audit-only mismatch | `test_dispatch_role_bootstrap_reports_mismatch_without_substituting_worker_role` | PASS |
| ROLE-DCL-A4 role bootstrap before activity specialization | `test_role_dcl_a4_worker_bootstrap_precedes_marker_and_lifecycle_loading` | PASS |
| ROLE-DCL-A5 invalid evidence fails before protected work | both `test_role_dcl_a5_*` tests | PASS |
| ROLE-DCL-A6 explicit interactive role persists over fallback | `test_role_dcl_a6_explicit_role_is_preserved_against_registry_fallback` | PASS |
| ROLE-DCL-A7 subject-only startup is fallback-classified | `test_role_dcl_a7_subject_only_startup_uses_source_classified_fallback` | PASS |
| ROLE-DCL-A8 peer/shared markers cannot authorize the worker | `test_role_dcl_a8_a9_shared_marker_and_registry_cannot_supply_behavior_role` | PASS |
| ROLE-DCL-A9 registry cannot supply/mutate non-dispatcher authority | `test_role_dcl_a8_a9_shared_marker_and_registry_cannot_supply_behavior_role` | PASS |
| ROLE-DCL-A10 equivalent harness semantics and classified reads | parametrized `test_role_dcl_a10_document_provenance_semantics_are_harness_independent` plus 22-test Codex/Claude parity command | PASS |

All fifteen entries above executed as test evidence. None is skipped,
metadata-only, partial, blocked, or not-yet-complete.

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_backlog_update_cli.py groundtruth-kb\tests\test_backlog_update_source_spec_id.py platform_tests\cli\test_backlog_update_title_desc.py -q --tb=short --basetemp .harness-tmp\wi5171-update-writers`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_kb_attribution.py platform_tests\scripts\test_kb_attribution_session_role.py platform_tests\scripts\test_session_envelope_runtime.py platform_tests\scripts\test_dispatched_role_bootstrap.py platform_tests\scripts\test_cli_backlog_add.py platform_tests\scripts\test_cli_backlog_add_work_item.py -q --tb=short --basetemp .harness-tmp\wi5171-role-authority-final`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\hooks\test_session_start_dispatch_role_cache.py platform_tests\scripts\test_codex_hook_parity_resolution_table_drift.py -q --tb=short --basetemp .harness-tmp\wi5171-a10-parity`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check <all 16 authorized Python paths>`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check <all 16 authorized Python paths>`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-wi5171-document-authoritative-backlog-writer --json`

## Observed Results

- Canonical update-writer suite: 38 passed.
- Document-authority suite: 62 passed.
- Standalone A10 cache/parity suite: 22 passed.
- Scope preflight: all 16 candidates in scope; zero out-of-scope and unused targets.
- Ruff check: all checks passed. Ruff format check: all 16 files already formatted.
- A broader 105-test cross-harness batch had 103 passes and two unrelated
  `test_dispatcher_runtime_durable_keyed_regression.py` failures. Its synthetic
  Codex fixture lacks the readiness condition required by the current dispatcher;
  neither that source nor fixture is in this GO scope. This report does not use
  those failures as evidence for any WI-5171 acceptance criterion.

## Files Changed

- `scripts/_kb_attribution.py`
- `scripts/session_self_initialization.py`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`
- `platform_tests/scripts/test_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`
- `platform_tests/scripts/test_cli_backlog_add.py`
- `platform_tests/scripts/test_cli_backlog_add_work_item.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `groundtruth-kb/tests/test_backlog_update_cli.py`
- `groundtruth-kb/tests/test_backlog_update_source_spec_id.py`
- `platform_tests/cli/test_backlog_update_title_desc.py`

## Acceptance Criteria Status

- PASS: all three canonical update writers run with valid per-session document
  provenance while retaining their original authorization and GOV-15 coverage.
- PASS: every GOV v5 and DCL v6 outer assertion has direct executed evidence.
- PASS: shared marker, registry, dispatcher selection, harness identity, and
  model identity cannot substitute document-derived writer authority.
- PASS: invalid and cross-session evidence fails before canonical writer mutation.
- PASS: source/test changes are limited to the approved target set; no
  `groundtruth.db` or `harness-state/harness-registry.json` change is staged.

## Risk And Rollback

The legacy shared envelope remains a narrowly validated migration fallback only
when an exact session document is absent; it cannot authorize a different
session. Rollback is limited to restoring the previous resolver and writer
versions, after which the session-keyed documents are inert runtime artifacts.
The unrelated dispatcher-fixture regression remains outside this implementation
and is not masked by the report.

## Loyal Opposition Asks

1. Verify the session-keyed document selection, project-root threading, and
   document-only `changed_by` derivation against GOV v5 and DCL v6.
2. Confirm the full five-plus-ten matrix is independently sufficient for
   VERIFIED, while treating the disclosed dispatcher-fixture failures as outside
   this bridge scope.
