REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-bridge-propose-helper-caller-migration-to-writer
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY
target_paths: ["scripts/gtkb_bridge_writer.py", ".claude/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/skills/test_bridge_revise_helper.py", "platform_tests/skills/test_bridge_impl_report_helper.py"]

# Implementation Proposal: Caller Migration To Validated Bridge Writer

## Summary

Complete GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY by migrating remaining Prime helper callers that directly edit `bridge/INDEX.md` to `scripts/gtkb_bridge_writer.py`, and harden that writer so status insertion combines atomic index update semantics with role and transition validation.

The remaining defect is not a missing helper concept. Prior review already rejected a raw status inserter. The existing writer is the durable target; the work is to make helper call sites use it for REVISED and post-implementation NEW insertions, with tests proving stale index detection and transition validation stay active.

## Prior Deliberations

- `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` authorizes the active bridge protocol reliability PAUTH cited above.
- Prior bridge threads `gtkb-bridge-propose-helper-index-parity-2026-04-30`, `gtkb-bridge-propose-helper-index-parity-2026-05-02`, and `gtkb-bridge-propose-helper-caller-migration-2026-05-02` rejected raw helper insertion and narrowed the remaining work to caller migration onto the existing validated writer.
- Backlog row `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` records the current acceptance statement: identify callers that edit `bridge/INDEX.md` directly and migrate them to `scripts/gtkb_bridge_writer.py` with role and transition validation.

## Owner Decisions / Input

- Mike's current-session directive on 2026-06-02 asks Prime Builder to continue until all listed items are completed. This proposal still requires normal Loyal Opposition GO before protected implementation edits.
- The cited project authorization supplies bounded owner-approval evidence for bridge protocol reliability work; it does not bypass bridge GO, target path scope, implementation-start packets, implementation reports, or Loyal Opposition verification.

## Specification Links

- `.claude/rules/file-bridge-protocol.md` governs bridge lifecycle, INDEX authority, target paths, project metadata, and implementation report verification.
- `.claude/rules/codex-review-gate.md` requires Loyal Opposition review, specification linkage, project authorization metadata, and spec-derived tests before implementation.
- `.claude/rules/project-root-boundary.md` keeps all live GT-KB artifacts under `E:\GT-KB`.
- `.claude/rules/operating-model.md` supplies canonical meanings for work item, implementation proposal, implementation report, verification, and project authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` governs bridge authority and queue-state handling.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` governs the Codex helper path and parity expectations where Codex lacks Claude Write/Edit hook coverage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` requires the project authorization, project, and work item metadata lines in this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` requires complete implementation proposal spec linkage and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires implementation-report evidence to map linked specs to executed tests.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` supports using live `bridge/INDEX.md` and live helper source rather than cached queue summaries.
- `GOV-STANDING-BACKLOG-001` supports closing the tracked backlog item only after verified completion evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` supports treating the proposal, tests, implementation report, and backlog resolution as linked durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` supports using explicit NEW, REVISED, GO, VERIFIED, and resolved lifecycle transitions instead of informal closure.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` supports preserving concrete implementation and decision evidence as durable artifacts.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements already require bridge state to be sourced from `bridge/INDEX.md`, proposal writes to use helper-mediated governance-safe paths, and implementation to include target paths plus spec-derived tests. No new requirement is needed before implementation.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep proposal and code changes credential-free; use existing helper scan for bridge proposal content. | Helper compliance audit and targeted tests. | |
| CQ-PATHS-001 | Yes | Keep all target paths under `E:\GT-KB` and preserve managed template parity. | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-propose-helper-caller-migration-to-writer` plus parity tests. | |
| CQ-COMPLEXITY-001 | Yes | Add a small writer API or narrow wrapper instead of broad helper rewrites. | Focused pytest coverage around writer and helper callers. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing status, role, and transition constants where present. | Ruff and targeted pytest coverage. | |
| CQ-SECURITY-001 | Yes | Preserve credential scanning and compliance-audit behavior; do not add bypass switches. | Existing helper tests plus new caller tests. | |
| CQ-DOCS-001 | Yes | Update canonical helper sources and managed template copies together. | Template parity or adapter-focused tests named in this proposal. | |
| CQ-TESTS-001 | Yes | Add regression tests for writer delegation, stale INDEX conflict handling, and role transition validation. | `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Preserve existing helper CLI output; surface writer errors without swallowing conflict details. | Targeted helper CLI tests. | |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check, and ruff format on changed Python files before filing the implementation report. | Commands listed in the verification plan. | |

## Scope

In scope:

- Add or harden a `scripts/gtkb_bridge_writer.py` entry point that inserts an INDEX status line only after role and transition validation.
- Preserve atomic same-directory temp plus `os.replace` semantics and stale-read conflict detection.
- Replace direct `bridge/INDEX.md` insertion code in `.claude/skills/bridge/helpers/revise_bridge.py` with the validated writer call for completed REVISED filings.
- Replace direct `bridge/INDEX.md` insertion code in `.claude/skills/bridge/helpers/impl_report_bridge.py` with the validated writer call for completed post-implementation NEW filings.
- Update the managed template copies under `groundtruth-kb/templates/skills/bridge/helpers/` for the same helper behavior.
- Add focused tests proving caller delegation and writer safety behavior.

Out of scope:

- Loyal Opposition GO, NO-GO, or VERIFIED authoring paths.
- Retired OS poller or retired smart poller restoration.
- Any bridge queue runtime other than `bridge/INDEX.md`.
- Broad bridge INDEX archival, pruning, or dispatch changes.

## Acceptance Criteria

- Remaining Prime helper callers no longer perform ad hoc direct `bridge/INDEX.md` content insertion for REVISED or post-implementation NEW filings.
- The migrated call path invokes `scripts/gtkb_bridge_writer.py` validation before the INDEX status line is persisted.
- Role-slot and lifecycle transition validation are exercised by tests.
- Stale INDEX conflict behavior is covered by tests and continues to fail closed.
- Managed template helper copies remain aligned with canonical helper behavior.
- The backlog row `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` is resolved only after Loyal Opposition verifies the implementation report.

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md`: run `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` to prove validated INDEX writes preserve bridge authority semantics.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: run `python -m pytest platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py -q --tb=short` to prove Codex-safe helper flows no longer use raw INDEX mutation at the caller layer.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-propose-helper-caller-migration-to-writer` after filing and include the packet in the implementation report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: include all commands and observed results in the post-implementation report.
- Code quality: run `python -m ruff check scripts/gtkb_bridge_writer.py .claude/skills/bridge/helpers/revise_bridge.py .claude/skills/bridge/helpers/impl_report_bridge.py groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py`.
- Formatting: run `python -m ruff format --check scripts/gtkb_bridge_writer.py .claude/skills/bridge/helpers/revise_bridge.py .claude/skills/bridge/helpers/impl_report_bridge.py groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py`.

## Pre-Filing Preflight

- Manual catch-22 check performed before filing: proposal text now cites the cross-cutting bridge governance specs, project-linkage specs, source-of-truth freshness spec, artifact-oriented governance specs, and bridge authority spec triggered by the named target paths and implementation-proposal content.
- REVISED-2 was filed because the live preflight for NEW-1 passed required specs but reported missing advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
- The Codex helper will run `.claude/hooks/bridge-compliance-gate.py --audit-only` against this in-memory content before writing `bridge/gtkb-bridge-propose-helper-caller-migration-to-writer-001.md`.
- After filing, Prime Builder will run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-propose-helper-caller-migration-to-writer` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-propose-helper-caller-migration-to-writer` and will revise if either identifies a blocking gap.

## Risk And Rollback

Risk: changing helper INDEX insertion could strand REVISED or post-implementation report filings if the writer API is too strict. Mitigation: keep scope narrow, preserve current helper output semantics, and add direct tests for expected helper behavior.

Rollback: revert the source and test changes from the implementation commit. The bridge audit chain remains append-only; any filed implementation report or LO verdict remains as historical evidence.
