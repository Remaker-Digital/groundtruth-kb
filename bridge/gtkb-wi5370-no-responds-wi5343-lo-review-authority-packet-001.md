NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Repair repo-wide failed VERIFIED finalization residue

bridge_kind: prime_proposal
Document: gtkb-wi5370-no-responds-wi5343-lo-review-authority-packet
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-wi5343-lo-review-authority-packet-004.md", "independent-progress-assessments/WI-5370-gtkb-wi5343-lo-review-authority-packet-004.no-responds-terminal.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Archive and remove the terminal VERIFIED artifact for `gtkb-wi5343-lo-review-authority-packet` because the current per-thread repair planner cannot prove a finalizer-safe implementation scope for that terminal verdict.

Planner reason: Approved proposal is missing concrete target_paths or Files Expected To Change.

Source work items observed by planner: `WI-4534, WI-4700, WI-5227, WI-5255, WI-5307, WI-5337, WI-5341, WI-5343`.

## Claim

Prime Builder proposes a bounded WI-5370 repair slice. This proposal does not authorize committing, staging, or modifying implementation source. It authorizes only an archive-then-remove transaction for the exact live terminal verdict bytes named in `target_paths`, after independent Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` and WI-5370 define the repo-wide finalization-repair boundary. The proposal preserves all bridge, work-intent, implementation-start, verification, and Git finalization gates.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5343-lo-review-authority-packet-004.md` and `independent-progress-assessments/WI-5370-gtkb-wi5343-lo-review-authority-packet-004.no-responds-terminal.md`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
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
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`

## Prior Deliberations

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering WI-5370.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-004.md` - VERIFIED read-only planner/runbook precedent requiring STOP-class bridge routing when scope cannot be proven.
- `bridge/gtkb-wi5351-tracked-terminal-verdict-stop-guard-004.md` - VERIFIED planner hardening precedent preserving exact byte ownership before terminal-verdict cleanup.
- `bridge/gtkb-wi5370-finalizer-classification-invalid-terminal-reissue-009.md` - WI-5370 precedent for bounded invalid-terminal verdict reissue routing.

## Owner Decisions / Input

No new owner decision is required. This proposal uses the active tree-stabilization project authorization and only opens a bounded review lane for one terminal bridge artifact.

## Proposed Scope

- Reconfirm `bridge/gtkb-wi5343-lo-review-authority-packet-004.md` is still the latest terminal VERIFIED artifact for `gtkb-wi5343-lo-review-authority-packet` and is still classified as `terminal_verified_blocked_missing_scope` by `scripts/per_thread_finalization_repair.py`.
- Archive the current live bytes (3943 bytes, SHA-256 `085993E77AED38A2782B39EBEAD1B9A4B50BE5C827FA959BD51D4EED8592AF79`, Git blob `70263c10e1611b796051e26d083c93c742cf4644`) to `independent-progress-assessments/WI-5370-gtkb-wi5343-lo-review-authority-packet-004.no-responds-terminal.md`, verify byte/hash/blob equality, and remove only `bridge/gtkb-wi5343-lo-review-authority-packet-004.md`.
- Leave implementation source, tests, rules, runbooks, database files, dispatcher state, and the Git index untouched.
- If the source thread still requires completion after removal, route that separately through a fresh proposal with explicit scope evidence; do not infer target paths from prose.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run scoped `git status --short -- bridge/gtkb-wi5343-lo-review-authority-packet-004.md independent-progress-assessments/WI-5370-gtkb-wi5343-lo-review-authority-packet-004.no-responds-terminal.md` before and after; confirm no staged/index changes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run `gt bridge show gtkb-wi5343-lo-review-authority-packet --json --compact` before and after; confirm only the exact terminal file is removed from the live chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330` and record the before/after classification. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Compare source and archive byte length, SHA-256, Git blob hash, and byte sequence before removing the source file. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve both target paths and confirm they remain under `E:\GT-KB`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Use bridge claim, implementation-start, and governed bridge report helpers; do not use alternate bridge runtimes. |

## Acceptance Criteria

- The terminal verdict bytes are preserved exactly in the declared archive before deletion.
- `gt bridge show gtkb-wi5343-lo-review-authority-packet --json --compact` no longer reports `bridge/gtkb-wi5343-lo-review-authority-packet-004.md` as the latest path after removal.
- No implementation source, tests, rules, runbooks, staged index entries, dispatcher state, database rows, commits, pushes, releases, or active WI-5320/WI-5328/WI-5330 program files are modified.

## Risks / Rollback

Risk is moderate because removing a terminal bridge artifact changes the live chain. The byte-identity guard and independent LO GO are mandatory. Rollback, before verification, is to restore only the archived bytes to `bridge/gtkb-wi5343-lo-review-authority-packet-004.md` after revalidating the same SHA-256 and blob. Bridge files and reports remain append-only audit artifacts.

## Files Expected To Change

- `bridge/gtkb-wi5343-lo-review-authority-packet-004.md`
- `independent-progress-assessments/WI-5370-gtkb-wi5343-lo-review-authority-packet-004.no-responds-terminal.md`

## Recommended Commit Type

`chore`
