NEW

# gtkb-ar-readiness-phase-1-4-partition-in-place (Slice 1) - Application-scope partition-in-place

bridge_kind: prime_proposal
Document: gtkb-ar-readiness-phase-1-4-partition-in-place
Version: 001
Author: Prime Builder / Codex Desktop
Date: 2026-06-28T17:29:04Z

author_identity: Prime Builder / Codex Desktop
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 via Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop, Windows PowerShell, danger-full-access workspace, network enabled

Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS-AGENT-RED-READINESS-PROGRAM-PHASE-1-ISOLATION-PARTITION-IN-PLACE
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: WI-4657

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli_spec_record.py", "groundtruth-kb/src/groundtruth_kb/cli_spec_update.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/application_scope.py", "scripts/agent_red_partition_in_place.py", "platform_tests/scripts/test_agent_red_partition_in_place.py", "platform_tests/scripts/test_application_scope_doctor.py", "groundtruth-kb/tests/test_db.py"]

implementation_scope: schema | governed_kb_mutation | dry_run_batch_migration | doctor_check | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement the Phase 1.4 Agent Red Readiness partition-in-place data slice. The work item requires Agent Red-related specs and tests to carry an explicit `application_scope`, to repath Agent Red source/test evidence under `applications/Agent_Red/`, and to add a doctor check that enforces alignment between scope and path.

This proposal is deliberately conservative because the live schema does not currently contain `application_scope`, and a quick read-only census showed naive top-level matching would misclassify GT-KB platform paths such as `scripts/` and `tests/`. The implementation must therefore introduce explicit schema/API support, produce a dry-run classification manifest, reject ambiguous candidates, and apply append-only version updates in batches of no more than 50 items.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the append-only bridge filing and requires GO plus implementation-start authorization before protected source, script, test, or MemBase mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - constrains implementation to the active project authorization and requires the per-slice bridge/implementation-start gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the specifications that drive implementation and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit project, work-item, and PAUTH linkage for this bridge proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification to prove the linked requirements through targeted tests and not only through inspection.
- `GOV-STANDING-BACKLOG-001` - establishes MemBase backlog authority; WI-4657 is the active P1 backlog item being processed.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires migration and doctor decisions to read live DB/filesystem state rather than cached startup or bridge summaries.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - requires Agent Red to remain a separate project, so application-specific rows must be distinguishable from GT-KB platform rows.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - establishes `applications/Agent_Red/` as the application root for repathed application evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - establishes the `applications/<name>/` placement boundary that repathed evidence must honor.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - defines applications as isolated execution contexts with separate lifecycle authority from GT-KB platform artifacts.
- `DCL-APP-ROOT-MINIMIZATION-001` - supplies the application-root vocabulary that path alignment must respect.
- `DCL-ADOPTER-SPEC-RECLASSIFICATION-001` - requires adopter-origin specs to be explicitly reviewed as platform-vs-adopter rather than silently treated as one or the other; this is the governing DCL for recording the DELIB-1402 reclassification.

## Prior Deliberations And Evidence

- `DELIB-20265219` - owner ratified the Agent Red Readiness program and its platform-side Phase 1 focus.
- `DELIB-20265220` - owner approved materializing Phase 1 slices, including the partition-in-place data slice.
- `DELIB-20265227` - owner resolved the Phase 1.1 governance foundation that gives this data slice its isolation vocabulary.
- `DELIB-1402` - captured in `DCL-ADOPTER-SPEC-RECLASSIFICATION-001`; adopter-origin specifications may be reclassified as GT-KB platform requirements only through explicit review.
- Read-only schema check on 2026-06-28: `specifications` has `source_paths`; `tests` has `test_file`; neither table has `application_scope`.

## Owner Decisions / Input

No new owner decision is required before filing. The active Phase 1 PAUTH covers this work item and cites `DELIB-20265219`; the work item cites `DELIB-20265219` and `DELIB-20265220`. A per-slice bridge GO and implementation-start packet are still required before schema, source, script, test, or `groundtruth.db` mutations.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4657 states the acceptance outcome: "AR specs/tests carry application_scope + repathed source_paths/test_file; doctor check enforces alignment." `DCL-ADOPTER-SPEC-RECLASSIFICATION-001` supplies the explicit platform-vs-adopter review rule, and the Phase 1.1 ADR/DCL supply the application-root vocabulary.

## Proposed Implementation

1. Add nullable `application_scope` columns to `specifications` and `tests` using the established PRAGMA-guard migration style in `KnowledgeDB`.
2. Extend the public spec/test record and update paths so `application_scope` is carried forward append-only. Valid values are initially limited to `gtkb_platform` and `agent_red_application`; unset/null remains allowed for rows outside this migration until a later tightening slice.
3. Add `groundtruth_kb.project.application_scope` helpers for:
   - parsing source path/test file JSON safely,
   - classifying candidate rows through explicit evidence,
   - rejecting ambiguous top-level-only matches,
   - validating scope/path alignment.
4. Add `scripts/agent_red_partition_in_place.py` with:
   - `--dry-run` default behavior,
   - `--execute` required for mutation,
   - a hard maximum of 50 mutations per execute run,
   - JSON manifest output listing candidate IDs, old values, proposed new values, and ambiguity reasons,
   - no raw SQL updates for current rows; use append-only `KnowledgeDB.update_spec()` and `KnowledgeDB.update_test()`.
5. Repath only rows that the dry-run manifest classifies unambiguously as Agent Red application evidence. Ambiguous rows, especially generic `scripts/`, `tests/`, `docs/`, and `config/` paths, remain unchanged and are reported for later review.
6. Add a doctor check that fails when:
   - `application_scope='agent_red_application'` but `source_paths` or `test_file` are outside `applications/Agent_Red/`,
   - `application_scope='gtkb_platform'` points at application product files,
   - a row has an ambiguous classification pending migration.

## Explicit Non-Goals

- No physical MemBase split.
- No writes outside `E:/GT-KB`.
- No automatic rewrite based only on top-level directory names.
- No formal GOV/ADR/DCL/SPEC creation or revision.
- No mutation of Agent Red product source.
- No batch larger than 50 changed spec/test rows per execute run.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `DCL-ADOPTER-SPEC-RECLASSIFICATION-001` | `platform_tests/scripts/test_agent_red_partition_in_place.py` proves ambiguous adopter/platform candidates are reported, not silently rewritten, and that accepted rows record `application_scope`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-APPLICATION-ISOLATION-CONTRACT-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`, `DCL-APP-ROOT-MINIMIZATION-001` | Partition tests and doctor tests prove Agent Red-scoped paths are under `applications/Agent_Red/` and platform-scoped rows do not point at application product artifacts. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Dry-run tests mutate fixture DB/file state between runs and prove the manifest reads live current views and filesystem state each time. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start must bind the GO bridge to WI-4657 and target `groundtruth.db` before execution; tests verify the migrator defaults to dry-run and caps apply batches at 50. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest commands cover schema migration, dry-run/apply behavior, ambiguous-candidate rejection, and doctor enforcement. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001` | Bridge applicability preflight and clause preflight must pass for this proposal, and implementation-start must bind the GO bridge to WI-4657 before protected edits. |

Expected post-implementation commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_agent_red_partition_in_place.py platform_tests/scripts/test_application_scope_doctor.py groundtruth-kb/tests/test_db.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/agent_red_partition_in_place.py --dry-run --json
groundtruth-kb/.venv/Scripts/gt.exe project doctor --dir . --json
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli_spec_record.py groundtruth-kb/src/groundtruth_kb/cli_spec_update.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/application_scope.py scripts/agent_red_partition_in_place.py platform_tests/scripts/test_agent_red_partition_in_place.py platform_tests/scripts/test_application_scope_doctor.py groundtruth-kb/tests/test_db.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli_spec_record.py groundtruth-kb/src/groundtruth_kb/cli_spec_update.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/application_scope.py scripts/agent_red_partition_in_place.py platform_tests/scripts/test_agent_red_partition_in_place.py platform_tests/scripts/test_application_scope_doctor.py groundtruth-kb/tests/test_db.py
```

## Risk / Rollback

Risk is high because this mutates `groundtruth.db` and schema/API surfaces. The major false-positive risk is misclassifying platform rows as Agent Red rows because many platform and application top-level directory names overlap. Mitigations are dry-run default, 50-row execute ceiling, explicit ambiguity reporting, append-only version rows, and doctor checks. Rollback is a commit revert for code/schema changes plus append-only corrective versions for any spec/test rows changed during execution; no destructive DB rollback is proposed.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-ar-readiness-phase-1-4-partition-in-place`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - this adds application-scope schema support, a governed migration tool, and doctor enforcement for the Agent Red readiness partition.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
