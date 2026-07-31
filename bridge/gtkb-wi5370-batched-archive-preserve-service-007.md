REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - WI-5370 Batched Archive-Preserve Verification Corrections

bridge_kind: prime_proposal
Document: gtkb-wi5370-batched-archive-preserve-service
Version: 007
Responds to: bridge/gtkb-wi5370-batched-archive-preserve-service-006.md
Approved proposal: bridge/gtkb-wi5370-batched-archive-preserve-service-001.md
Prior GO: bridge/gtkb-wi5370-batched-archive-preserve-service-004.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
target_paths: ["scripts/batch_archive_terminal_verdicts.py", "platform_tests/scripts/test_batch_archive_terminal_verdicts.py"]
Recommended commit type: fix

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Correct the four concrete verification findings from version 006 without expanding the original two-file implementation scope. The service will use the governing terminal-status taxonomy exactly, clean up only archive copies created by a failed transaction so retries remain deterministic, and carry all prior specifications plus owner-decision evidence into the refreshed implementation report.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`, the version-006 findings, and the active Tree Stabilization PAUTH define the correction. No specification amendment or new owner decision is required.

## Specification Links

- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-202666766` - owner-selected refine-detector plus bulk-archive method and pilot-first risk posture.
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` - owner precedent favoring oracle refinement over broad moves.
- `DELIB-20264762` - requires candidate derivation from live state rather than stale snapshots.
- `DELIB-202666993` - prior Loyal Opposition review context for this service.

## Owner Decisions / Input

- `DELIB-202666766` remains the governing owner decision for the archive-preserve method and pilot-first posture.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` remains the active project authorization covering `WI-5370`.
- No new owner decision is requested; this revision responds only to deterministic verification findings.

## Findings Addressed

### F1 - P1 - Spec-derived runner fails on removed carried-forward specs

Response: The refreshed implementation report will carry forward `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and `DCL-NO-ACTION-STATUS-SEMANTICS-001` in both Specification Links and the spec-to-test matrix. It will also retain every specification listed in this revision and include the passing `run_spec_derived_tests.py --dry-run --json` matrix or return for further correction.

### F2 - P1 - Candidate terminal status taxonomy diverges from the governing DCL

Response: Replace `TERMINAL_STATUSES` with exactly `VERIFIED`, `WITHDRAWN`, `DEFERRED`, and `ADVISORY`, as stated by `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`. Add candidate-discovery tests proving `ADVISORY` is accepted and `RETIRED` plus `SUPERSEDED` are rejected unless a future governed DCL revision authorizes them.

### F3 - P1 - Implementation report omits required owner-decision section

Response: The refreshed implementation report will include a non-empty `## Owner Decisions / Input` section carrying `DELIB-202666766` and the active Tree Stabilization PAUTH as existing authority, without asserting a new approval.

### F4 - P2 - Commit-failure path strands a partial archive copy and makes retry non-clean

Response: On any failed archive commit, the service will unstage its exact archive pathspec where necessary and remove only archive copies created and byte-verified by the current invocation. Cleanup will verify the path remains under `archive/bridge-terminal-verdicts/` and still matches the recorded size/SHA-256 before unlinking; any mismatch or cleanup failure remains a surfaced hard error. Tests will prove index-lock and commit failures leave sources present, archive copies absent, no archive path staged, and a subsequent retry able to complete without manual cleanup.

## Scope Changes

No target-path expansion. The correction remains limited to:

- `scripts/batch_archive_terminal_verdicts.py`
- `platform_tests/scripts/test_batch_archive_terminal_verdicts.py`

No production archive run, live bridge deletion, live archive commit, dispatcher/TAFE mutation, configuration change, credential action, push, deploy, or release is authorized.

## Specification-Derived Verification Plan

| Specification / finding | Required verification |
| --- | --- |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` / F2 | Focused candidate tests prove exactly `VERIFIED`, `WITHDRAWN`, `DEFERRED`, and `ADVISORY` are terminal candidates; `RETIRED` and `SUPERSEDED` are rejected. |
| `GOV-WORK-TREE-HYGIENE-001` / F4 | Index-lock and forced commit-failure tests prove source retention, exact archive-copy cleanup, no archive staging residue, and successful retry. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, `DCL-NO-ACTION-STATUS-SEMANTICS-001` / F1 | `run_spec_derived_tests.py --dry-run --json` must pass continuity and emit a usable matrix after the refreshed report carries both links. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / F3 | Refreshed report includes a non-empty Owner Decisions / Input section with the existing PAUTH and owner deliberation. |
| All linked specifications | Focused pytest, Ruff check, Ruff format check, `py_compile`, diff check, applicability preflight, clause preflight, and spec-derived dry run pass before a new implementation report is filed. |

## Acceptance Criteria

- The executable terminal set exactly matches the governing DCL.
- Failed commit attempts leave all sources intact, remove only same-attempt verified archive copies, leave no archive staging residue, and can be retried without manual intervention.
- The focused suite covers `ADVISORY`, `RETIRED`, `SUPERSEDED`, index-lock cleanup, forced commit failure, and clean retry.
- The refreshed report carries every linked specification and a non-empty Owner Decisions / Input section.
- The spec-derived runner and all focused/static gates pass before independent verification.

## Pre-Filing Preflight Subsection

Applicability command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5370-batched-archive-preserve-service-007.md --json
```

Observed result: `preflight_passed: true`, packet hash `sha256:2f913b5a5ab6d5f99ef0bec1016f040f97fa0b3e53b1427967f28d642d8cefec`, `missing_required_specs: []`, `missing_advisory_specs: []`, and `blocking_errors: []`.

Clause command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5370-batched-archive-preserve-service-007.md
```

Observed result: 5 clauses evaluated, 3 `must_apply`, 2 `may_apply`, zero must-apply evidence gaps, zero blocking gaps, exit 0.

## Risk And Rollback

The cleanup path must never remove a pre-existing or drifted archive artifact. It therefore deletes only same-invocation paths whose current size and SHA-256 still match the recorded `ArchiveResult`; mismatch fails closed and leaves evidence in place. Rollback is a focused revert of the two implementation targets under separate authority. Numbered bridge artifacts remain append-only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
