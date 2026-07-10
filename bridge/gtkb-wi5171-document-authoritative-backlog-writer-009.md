REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive session; owner established prime-builder role with ::init gtkb pb.

bridge_kind: prime_proposal
Document: gtkb-wi5171-document-authoritative-backlog-writer
Version: 009
Date: 2026-07-10 UTC
Responds to: bridge/gtkb-wi5171-document-authoritative-backlog-writer-008.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES
Work Item: WI-5171

target_paths: ["scripts/_kb_attribution.py", "scripts/session_self_initialization.py", "scripts/check_dispatched_role_bootstrap.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "platform_tests/scripts/test_kb_attribution.py", "platform_tests/scripts/test_kb_attribution_session_role.py", "platform_tests/scripts/test_cli_backlog_add.py", "platform_tests/scripts/test_cli_backlog_add_work_item.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_dispatched_role_bootstrap.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_backlog_update_source_spec_id.py", "platform_tests/cli/test_backlog_update_title_desc.py"]

implementation_scope: source and tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5171 Revision - normalize one scoped source file to LF

## Revision Claim

This revision responds exclusively to `-008` F1. It does not change the approved document-authoritative worker-role design, its canonical writer behavior, or its test assertions. Under a renewed GO, Prime Builder will normalize `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` from CRLF to LF while preserving its approved content edits, then rerun the focused update-writer and document-authority suites. This removes whole-file EOL churn so the final VERIFIED commit can remain a clean subset of the original sixteen authorized paths.

## Requirement Sufficiency

Existing requirements sufficient.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` v5 and `DCL-SESSION-ROLE-RESOLUTION-001` v6 retain the document-only writer-authority behavior and complete executable matrix already independently reproduced at `-008`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` require this REVISED proposal, live GO, matching claim, and bounded project linkage before the source-file normalization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` require the carried-forward requirement-to-test mapping and executed evidence before terminal verification.
- `ADR-ENVELOPE-META-MODEL-001`, `DCL-ENVELOPE-META-MODEL-001`, `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, and `ADR-CODEX-HOOK-PARITY-FALLBACK-001` remain unchanged design constraints: worker behavior derives from the document artifact, not dispatcher configuration, registry role, marker, model, or harness identity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` keep the change inside the GT-KB root and the governed bridge lifecycle.

## Prior Deliberations

- `DELIB-202666073` - owner authorization for the bounded WI-5171/WI-5086 document-authoritative worker-role correction.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-GOV-V5-FORMALIZATION-RESULT` - the five GOV v5 worker-envelope authority assertions.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-DCL-V6-APPROVAL` - the ten DCL v6 role-resolution assertions.
- `DELIB-20260710-GTKB-INTERACTIVE-KB-ATTRIBUTION-GLOBAL-MARKER-COLLISION` - the shared-marker misattribution defect guarded by the approved matrix.
- `bridge/gtkb-wi5171-document-authoritative-backlog-writer-006.md` - prior GO carrying the binding verified conditions.
- `bridge/gtkb-wi5171-document-authoritative-backlog-writer-008.md` - independent NO-GO identifying the LF-to-CRLF scoped-commit blocker.

## Owner Decisions / Input

The owner authorization recorded by `DELIB-202666073` and the active `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001` cover this bounded correction. The `-008` finding directs a mechanical normalization without a product, priority, or requirement change; no fresh owner decision is requested.

## Findings Addressed

### F1 [P1] `cli_backlog_add_work_item.py` carries a whole-file LF to CRLF flip (scoped-commit blocker)

Response: after a renewed independent GO, normalize only `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` to LF. Preserve the approved `project_root` threading and `changed_by` content edits, do not edit the other fifteen target paths, and prove `git ls-files --eol` reports `i/lf  w/lf`. The raw `git diff --stat` and `git diff --ignore-cr-at-eol --stat` must agree for this file, demonstrating that its diff has collapsed to content-only change.

## Scope Changes

The sixteen `target_paths` remain exactly the `-005` authorization boundary so final verification can stage the complete approved implementation, including the two untracked dispatched-bootstrap paths that `-008` noted. The only new working-tree mutation proposed by this revision is an LF normalization of `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`; the other fifteen paths remain unchanged. No database, generated registry projection, dispatcher configuration, formal artifact, or unrelated source/test path is added.

## Pre-Filing Preflight Subsection

Candidate checks executed against this completed revision before filing:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:8d9fbaafba61cdc80cf4f91815b169b3edb2f5f8f2bd1462ecd72a2d2da05770`.
- Clause preflight: exit 0; three `must_apply` clauses had evidence, with zero blocking gaps.
- Bridge compliance audit-only check: passed.

The governed filing helper reruns the applicability and clause gates immediately before publication.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Scoped-commit hygiene from `-008` F1 and the `-006` carried-forward condition 4 | Check `git ls-files --eol`, raw and CRLF-ignoring diff statistics, and the staged path set before finalization. | The normalized file is `i/lf  w/lf`; raw and ignore-CR diff results agree; staged paths are a subset of the sixteen target paths; `groundtruth.db` and generated `harness-state/harness-registry.json` are absent. |
| GOV v5 / DCL v6 document-authority behavior | Run the focused document-authority suite used by `-007` and independently reproduced by `-008`. | 62 tests pass; the normalization changes no behavior or assertion coverage. |
| Canonical update-writer behavior and GOV-15 coverage | Run the focused update-writer suite used by `-007` and independently reproduced by `-008`. | 38 tests pass; all valid per-session provenance fixtures retain their original assertions. |
| Python quality gates | Run `ruff check` and `ruff format --check` on the normalized Python file. | Both gates pass. |
| Proposal governance | Run candidate applicability and clause preflights before filing, then acquire a fresh implementation-start packet only after the renewed GO. | No blocking linkage or clause gap; no source mutation occurs before live GO and matching claim. |

## Acceptance Criteria

- `cli_backlog_add_work_item.py` has LF working-tree line endings and only its approved content diff remains.
- The update-writer and document-authority suites remain green without altering behavior, tests, or other target paths.
- The final staged set is a clean subset of the sixteen original target paths and excludes `groundtruth.db` and generated `harness-state/harness-registry.json`.
- The terminal post-implementation report lists every finalization path, including the two untracked dispatched-bootstrap paths, and receives an independent VERIFIED verdict.

## Risk And Rollback

The only technical risk is accidentally altering content while normalizing line endings. The normalizer will preserve UTF-8 text and the post-change raw diff will be inspected against the CRLF-ignoring diff before filing the report. Rollback is a content-preserving reversal of the single file's line-ending conversion; the existing document-authority design and test changes remain untouched.

## Recommended Commit Type

`fix` - removes scoped-commit EOL churn from an already-approved document-authority correction.
