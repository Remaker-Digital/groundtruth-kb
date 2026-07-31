NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Harden peer_report_dirty_path_collision_reason to cover terminal-but-uncommitted and heading-format-mismatched peers

bridge_kind: prime_proposal
Document: gtkb-wi5521-dirty-peer-collision
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5521-DIRTY-PEER-COLLISION-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5521

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Harden peer dirty-path collision attribution so structured report target_paths survive heading variation and a terminal VERIFIED thread remains protective only until its terminal verdict is represented byte-for-byte in HEAD.

Work item description: scripts/implementation_authorization.py::peer_report_dirty_path_collision_reason only blocks begin when a NON-TERMINAL peer bridge thread has filed a post-GO NEW/REVISED implementation report with a heading literally named 'Files Changed' or 'Implemented Paths' (see _reported_paths_from_implementation_report). Two real gaps found during LO review of gtkb-wi5460-wi5465-canonical-spec-existence-gates-005: (1) a peer thread reaching VERIFIED/WITHDRAWN is excluded entirely from the scan (entry.latest_status check), so a terminal-but-not-yet-committed peer (the exact WI-5387 failure mode WI-5502 exists to repair) leaves its dirty target bytes with zero mechanical collision protection at the moment another thread's begin runs; (2) a peer implementation report that uses a different section convention (e.g. gtkb-wi5403-declared-applicability-target-scope-005.md uses 'Exact WI-5403 Ownership' instead of 'Files Changed') is invisible to the heading matcher even while non-terminal, and the guard falls through only by accident to an OLDER superseded report version (v003) that happened to use the recognized heading. Recommend: (a) add a general-purpose check that blocks begin on ANY currently-dirty declared target_path regardless of peer attribution unless the invoking session itself holds an active claim on that exact path, not just the narrower peer-report-attribution path; (b) broaden the heading matcher or add a structured 'target_paths carried forward' metadata convention so newer report revisions do not silently lose collision-guard visibility relative to their own superseded ancestors.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5521` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666411` - Loyal Opposition Corrected Verdict - NO-GO - WI-5227 Ollama D Abrupt-Exit Diagnostics (dependency disposition)
- `DELIB-202666393` - Loyal Opposition Corrected Verdict - WI-5178 Governed PAUTH Enforcement Predecessor Closure
- `DELIB-202666060` - Loyal Opposition Verdict — GO — WI-5105 Finalization Commingle Guard
- `DELIB-202666557` - Loyal Opposition review_no_action — WI-5347 WI-5142 Artifact Decontamination Baseline
- `DELIB-20265893` - Resolve WI-4772 + WI-4775 as covered by VERIFIED gtkb-verified-finalization-validation-hardening (may29-hygiene retirement)

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5521-DIRTY-PEER-COLLISION-20260718` - active project authorization covering `WI-5521`.

## Proposed Scope

- Hard-gate implementation behind terminal focused WI-5382 and WI-5454, clean exact target preimages, independent GO, exact claim, and schema-v3 implementation-start authorization.
- Extract structured target_paths from implementation reports and union them with the existing Files Changed and Implemented Paths heading evidence.
- Continue collision checks for terminal VERIFIED peers only while the latest terminal verdict is absent or differs from HEAD; once atomic finalization is represented in HEAD, do not let historical report paths create a permanent block.
- Preserve the existing three-way dirty-path, current-target, and historical-peer-target overlap requirement plus current-thread, clean-path, nonoverlap, bootstrap, and unreadable-chain behavior.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5521; PAUTH-DISPATCHER-BLACK-BOX-WI5521-DIRTY-PEER-COLLISION-20260718; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "scripts/implementation_authorization.py::peer_report_dirty_path_collision_reason only blocks begin when a NON-TERMINAL peer bridge thread has filed a post-GO NEW/REVISED implementation report with a heading literally named 'Files Changed' or 'Implemented Paths' (see _reported_paths_from_implementation_report). Two real gaps found during LO review of gtkb-wi5460-wi5465-canonical-spec-existence-gates-005: (1) a peer thread reaching VERIFIED/WITHDRAWN is excluded entirely from the scan (entry.latest_status check), so a terminal-but-not-yet-committed peer (the exact WI-5387 failure mode WI-5502 exists to repair) leaves its dirty target bytes with zero mechanical collision protection at the moment another thread's begin runs; (2) a peer implementation report that uses a different section convention (e.g. gtkb-wi5403-declared-applicability-target-scope-005.md uses 'Exact WI-5403 Ownership' instead of 'Files Changed') is invisible to the heading matcher even while non-terminal, and the guard falls through only by accident to an OLDER superseded report version (v003) that happened to use the recognized heading. Recommend: (a) add a general-purpose check that blocks begin on ANY currently-dirty declared target_path regardless of peer attribution unless the invoking session itself holds an active claim on that exact path, not just the narrower peer-report-attribution path; (b) broaden the heading matcher or add a structured 'target_paths carried forward' metadata convention so newer report revisions do not silently lose collision-guard visibility relative to their own superseded ancestors.",
  "after_behavior": "Harden peer dirty-path collision attribution so structured report target_paths survive heading variation and a terminal VERIFIED thread remains protective only until its terminal verdict is represented byte-for-byte in HEAD.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5521",
    "project": "PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
    "target_paths": [
      "scripts/implementation_authorization.py",
      "platform_tests/scripts/test_implementation_authorization.py"
    ],
    "linked_specifications": [
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
      "DCL-PROJECT-DEPENDENCY-ORDERING-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "Harden peer dirty-path collision attribution so structured report target_paths survive heading variation and a terminal VERIFIED thread remains protective only until its terminal verdict is represented byte-for-byte in HEAD.",
    "scope": [
      "Hard-gate implementation behind terminal focused WI-5382 and WI-5454, clean exact target preimages, independent GO, exact claim, and schema-v3 implementation-start authorization.",
      "Extract structured target_paths from implementation reports and union them with the existing Files Changed and Implemented Paths heading evidence.",
      "Continue collision checks for terminal VERIFIED peers only while the latest terminal verdict is absent or differs from HEAD; once atomic finalization is represented in HEAD, do not let historical report paths create a permanent block.",
      "Preserve the existing three-way dirty-path, current-target, and historical-peer-target overlap requirement plus current-thread, clean-path, nonoverlap, bootstrap, and unreadable-chain behavior."
    ],
    "acceptance_criteria": [
      "A nonterminal implementation report with structured target_paths and a nonstandard ownership heading blocks an overlapping dirty target.",
      "A terminal VERIFIED peer whose latest verdict is not represented byte-for-byte in HEAD blocks an overlapping dirty reported target.",
      "The same historical peer no longer blocks after its terminal verdict is represented byte-for-byte in HEAD, even when a later unrelated change dirties the old target.",
      "Existing current-thread, clean-path, nonoverlap, bootstrap, and unreadable-peer regression cases remain unchanged.",
      "Focused tests, full implementation-authorization tests, Ruff check, Ruff format check, py_compile, and git diff --check pass."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused and complete implementation-authorization test file and report exact commands and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Add exact collision tests for structured target_paths, uncommitted terminal VERIFIED evidence, and committed terminal non-blocking history. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exercise create_authorization_packet denial and allow paths with dirty worktree fixtures and historical peer packets. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Verify implementation remains blocked until WI-5382 and WI-5454 are terminal and both targets are clean. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the existing WI-5105 peer-collision regression set and prove no permanent block from committed terminal history. |
| `GOV-WORK-TREE-HYGIENE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A nonterminal implementation report with structured target_paths and a nonstandard ownership heading blocks an overlapping dirty target.
- A terminal VERIFIED peer whose latest verdict is not represented byte-for-byte in HEAD blocks an overlapping dirty reported target.
- The same historical peer no longer blocks after its terminal verdict is represented byte-for-byte in HEAD, even when a later unrelated change dirties the old target.
- Existing current-thread, clean-path, nonoverlap, bootstrap, and unreadable-peer regression cases remain unchanged.
- Focused tests, full implementation-authorization tests, Ruff check, Ruff format check, py_compile, and git diff --check pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`feat`
