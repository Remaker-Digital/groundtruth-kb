NEW

# Backlog JSON Option Validation

bridge_kind: prime_proposal
Document: gtkb-wi4677-backlog-json-option-validation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T06-32-00Z-prime-builder-A-keep-working
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Hygiene PB

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4677

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "platform_tests/scripts/test_cli_backlog_add.py", "groundtruth-kb/tests/test_backlog_update_cli.py"]

implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4677 captures a defect discovered during WI-4634 reconciliation: the Windows CLI path allowed `gt backlog resolve` and `gt backlog update` to persist malformed `related_bridge_threads` text when the caller intended a JSON array. The stored value looked like `[bridge/gtkb-bridge-thread-read-cli-004.md,bridge/gtkb-bridge-thread-read-cli-commands-002.md]`, which is not parseable JSON and required a follow-up `KnowledgeDB.update_work_item(...)` correction.

This proposal asks for a narrow source/test fix: validate JSON-list option fields before they are written by `gt backlog add`, `gt backlog update`, or `gt backlog resolve`. Valid JSON arrays should continue to persist unchanged; malformed values should fail closed with actionable CLI guidance rather than creating corrupted MemBase linkage fields.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Source and test mutations must wait for an approved bridge `GO` and a live implementation-start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The proposal carries concrete governing specification links for the source/test change.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries the active PAUTH, project id, and WI-4677 metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must prove malformed JSON values are rejected and valid JSON arrays remain parseable.
- `GOV-STANDING-BACKLOG-001` - WI-4677 is a governed backlog item and the implementation should protect backlog linkage fields from malformed stored values.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active May29 Hygiene authorization covers unimplemented May29 work items such as WI-4677.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Bridge/backlog evidence must remain durable and machine-readable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - CLI behavior, tests, backlog row, proposal, and report should form one consistent artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The captured defect is being advanced from backlog candidate to bridge-reviewed implementation scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are inside the GT-KB project root.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - Owner authorization for implementing unimplemented May29 Hygiene work items through the normal bridge/GO process.
- `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` - Backlog/project CLI precedent for adding bounded command-surface behavior with focused tests.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - Proposal-standards context for producing machine-readable target paths, project linkage, and spec-derived verification.
- Focused search `gt deliberations search "gt backlog related_bridge_threads JSON Windows PowerShell malformed quotes WI-4634" --limit 10 --json` found no exact prior decision for this new defect. The live WI-4634 reconciliation history is therefore the primary discovery evidence.

## Owner Decisions / Input

No new owner decision is required. Mike's automation instruction for this run explicitly asked PB to add stray/odd hygiene defects as work items, and the active May29 Hygiene PAUTH authorizes implementation proposals for unimplemented May29 work items. Implementation still requires Loyal Opposition `GO` before any target file mutation.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4677 defines the defect, component, acceptance summary, and regression visibility. The fix is bounded to validating JSON-list command options before service-layer writes and adding focused regression tests. No new architecture decision, backlog schema change, or MemBase migration is required.

## Implementation Scope

Approved source changes:

- Add service-layer JSON-list validation in `groundtruth_kb.cli_backlog_add` for `related_spec_ids`, `related_deliberation_ids`, `related_bridge_threads`, and `depends_on_work_items`.
- Add service-layer JSON-list validation in `groundtruth_kb.cli_backlog_update` for `related_bridge_threads`, covering both `gt backlog update` and `gt backlog resolve`.
- Preserve valid JSON array strings exactly enough that existing readback paths continue to expose parsed lists.
- Return clear CLI/service errors for malformed JSON or non-list JSON values.

Approved test changes:

- Add focused `gt backlog add` coverage in `platform_tests/scripts/test_cli_backlog_add.py` for valid JSON-list fields and malformed values.
- Add focused `gt backlog update` / `gt backlog resolve` coverage in `groundtruth-kb/tests/test_backlog_update_cli.py` for valid and malformed `related_bridge_threads` values.

Out of scope:

- No schema migration.
- No direct `groundtruth.db` mutation.
- No historical cleanup of previously malformed rows beyond the already-corrected WI-4634 row.
- No changes to project membership, bridge routing, implementation authorization, or unrelated backlog fields.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Use only synthetic bridge paths and JSON strings in tests; do not add credential-shaped fixtures. | Bridge helper credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep all mutations inside the declared in-root target paths. | Implementation-start packet and `git diff --name-only` scoped to target paths. | |
| CQ-COMPLEXITY-001 | Yes | Add a small shared JSON-list validation path in the backlog CLI services; avoid broad command rewrites. | Focused pytest and source review. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing field names and error types; introduce only named helper data where duplication would grow. | Source review plus focused tests for each structured field. | |
| CQ-SECURITY-001 | Yes | Fail closed before writing malformed structured linkage data; do not relax command validation. | Negative malformed-input tests and valid-input preservation tests. | |
| CQ-DOCS-001 | N/A | | | No user documentation surface changes are in scope. |
| CQ-TESTS-001 | Yes | Add focused add/update/resolve coverage for malformed and valid JSON-list values. | Verification-plan pytest commands. | |
| CQ-LOGGING-001 | N/A | | | No runtime logging or telemetry changes are in scope. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest plus Ruff check and Ruff format check before filing the implementation report. | Commands listed in the verification plan. | |

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: after LO `GO`, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4677-backlog-json-option-validation`; expected PASS with only the listed source/test target paths authorized.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4677-backlog-json-option-validation`; expected PASS with no missing required or advisory specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: inspect bridge header metadata; expected PASS with PAUTH, project, and WI-4677 present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short`; expected PASS proving malformed JSON-list values fail closed and valid arrays persist parseably.
- `GOV-STANDING-BACKLOG-001`: run `gt backlog show WI-4677 --history --json`; expected PASS with WI-4677 visible under May29 Hygiene and linked from report evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: run `gt projects show PROJECT-GTKB-MAY29-HYGIENE --json`; expected PASS with active May29 Hygiene PAUTH still valid for WI-4677.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: inspect implementation report and CLI readback evidence; expected PASS showing backlog linkage fields remain machine-readable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`: inspect tests and bridge report; expected PASS showing source, tests, backlog item, and bridge evidence describe the same behavior.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: inspect bridge chain plus WI-4677 history; expected PASS showing the lifecycle transition from captured defect to implemented/verified work is recorded.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: inspect target paths and run clause preflight; expected PASS with all target paths under `E:\GT-KB`.

Additional checks:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_cli_backlog_add.py groundtruth-kb/tests/test_backlog_update_cli.py
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4677-backlog-json-option-validation
```

## Risk / Rollback

Risk is low and localized to backlog CLI service validation. The main compatibility risk is rejecting existing caller shapes that passed non-JSON prose into JSON-list fields. That is intentional for structured fields, but the implementation should keep error messages explicit and should not change unrelated text fields.

Rollback is a single commit revert of the source/test change plus withdrawal or NO-GO handling through the bridge if verification fails.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4677-backlog-json-option-validation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
