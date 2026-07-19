NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# WI-5345 Canonical Terminal Finalization Repair

bridge_kind: prime_proposal
Document: gtkb-wi5345-canonical-terminal-finalization-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5345-CANONICAL-FINALIZATION-REPAIR-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5345
target_paths: ["bridge/gtkb-wi5345-cursor-timeout-recovery-004.md"]

implementation_scope: bridge | metadata | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair WI-5345 terminal finalization without mutating or capturing either
Cursor source/test target. The primary WI-5345 proposal, GO, implementation
report, and exact implementation images are committed in current ancestry at
commit `42a252ab57b5a203e9406b626c741d897e8fb196`. The independently authored
primary version-004 `VERIFIED` verdict exists at its canonical numbered bridge
path but is untracked.

This repair makes that one verdict file the only implementation target. After
independent GO, Prime Builder will revalidate the committed implementation,
the complete primary thread, verdict independence, exact verdict bytes, and
current Git ancestry without changing any project file. Prime Builder will
then file a no-source implementation report. A distinct independent Loyal
Opposition session may return `VERIFIED` through the canonical atomic
finalizer, including only the primary verdict plus this repair thread.

No existing source/test worktree byte is authorized, attributed, staged,
committed, reverted, deleted, or otherwise changed by this proposal.

## Current-State Evidence

- The primary thread is a complete
  `NEW 001 -> GO 002 -> NEW implementation report 003 -> VERIFIED 004`
  lifecycle.
- Primary versions 001 through 003 are tracked.
- Primary version 004 is untracked and remains latest `VERIFIED`.
- Primary version 004 has length `4359`, SHA-256
  `7E6C25D1C2C1869ACDD7E4DACC58DFA5CD7B3A38610B45D710CCAC2EE8D09473`,
  and Git blob `6537b2de78a7d4435d19443b637da024b794563e`.
- Commit `42a252ab57b5a203e9406b626c741d897e8fb196` contains
  `scripts/cursor_harness.py`,
  `platform_tests/scripts/test_cursor_harness.py`, and primary bridge versions
  001 through 003.
- Commit `42a252ab57b5a203e9406b626c741d897e8fb196` is an ancestor of current
  `HEAD`.
- `git diff 42a252ab57b5a203e9406b626c741d897e8fb196..HEAD` is empty for both
  WI-5345 source/test paths, so the committed `HEAD` images remain the
  implementation images reviewed in the primary report.
- The current working copies of both source/test paths contain later foreign
  modifications. They are explicitly excluded from this repair.
- The current working-copy Cursor harness module passes `39` tests. That
  supporting result does not substitute for commit-bound verification and
  grants no ownership of the foreign worktree hunks.

No bridge artifact outside the primary WI-5345 numbered thread is relied upon
as implementation, verification, or finalization evidence.

## Proposed Implementation

After independent GO:

1. Acquire a fresh exact work-intent claim and schema-v3 implementation-start
   packet for the one declared target.
2. Re-read primary versions 001 through 004 in order.
3. Confirm primary proposal/report target paths remain exactly
   `scripts/cursor_harness.py` and
   `platform_tests/scripts/test_cursor_harness.py`.
4. Confirm the primary verdict author session differs from the report author
   session and the verdict still satisfies the canonical VERIFIED evidence
   floor.
5. Recompute the primary verdict length, SHA-256, and Git blob and require the
   exact values recorded above.
6. Confirm commit `42a252ab57b5a203e9406b626c741d897e8fb196` is an ancestor of
   `HEAD`, contains both source/test paths plus primary versions 001 through
   003, and has no later committed source/test delta through `HEAD`.
7. Verify the WI-5345 implementation from the committed `HEAD` images using an
   isolated in-root test view or an equivalent commit-bound method. Do not use
   the dirty working copies as sole evidence.
8. File a no-source implementation report whose only declared target remains
   the primary version-004 verdict.
9. Independent Loyal Opposition re-runs all checks and, only if they pass,
   uses the canonical atomic VERIFIED finalizer for this repair thread.

The focused finalization include set is:

- `bridge/gtkb-wi5345-cursor-timeout-recovery-004.md`;
- every status-bearing file in
  `gtkb-wi5345-canonical-terminal-finalization-repair`.

The finalizer must not include either Cursor source/test working-copy path,
any other bridge thread, any currently staged path, or any unrelated
worktree path.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5345 and PAUTH-DISPATCHER-BLACK-BOX-WI5345-CANONICAL-FINALIZATION-REPAIR-20260718",
  "canonical_authority": "The primary WI-5345 numbered bridge history, MemBase work item, exact primary verdict bytes, and current Git commit ancestry",
  "primary_route": "Prove the committed implementation and independent verdict, file a no-source repair report, then atomically finalize only the verdict and repair chain",
  "before_behavior": "The implementation and report are committed but the independent terminal verdict has no containing commit",
  "after_behavior": "The primary verdict has a focused containing commit whose repair chain proves the already-committed implementation without capturing later dirty Cursor work",
  "self_descriptive_naming": "canonical_terminal_finalization_repair, committed_implementation_ancestor, exact_verdict_bytes, and focused_include_set expose the complete decision",
  "obsolete_guidance_disposition": "No alternate carrier, copied evidence, or worktree-wide sweep is accepted; no historical primary bridge version is rewritten",
  "history_preservation": "Primary versions 001 through 004, the implementation commit, MemBase history, and all unrelated worktree and index state remain intact",
  "baseline": {
    "implementation_commit": "42a252ab57b5a203e9406b626c741d897e8fb196",
    "verdict_length": 4359,
    "verdict_sha256": "7E6C25D1C2C1869ACDD7E4DACC58DFA5CD7B3A38610B45D710CCAC2EE8D09473",
    "verdict_blob": "6537b2de78a7d4435d19443b637da024b794563e",
    "known_gap": "The primary verdict is untracked while both source/test working copies carry later foreign changes"
  },
  "expected_result": {
    "implementation": "Committed HEAD retains the exact WI-5345 source/test images from the implementation commit",
    "verification": "Independent review reproduces commit-bound behavior and validates the complete primary thread",
    "finalization": "One focused commit contains the primary verdict and complete repair thread only",
    "nonimpairment": "Current Cursor source/test working-copy bytes and all staged or unrelated paths remain byte-identical"
  },
  "rollback": {
    "instructions": "If finalization fails, leave the untracked primary verdict and repair chain intact for later governed retry",
    "preserve": "Do not remove, rewrite, revert, stage, or commit source/test or unrelated paths",
    "verification": "Re-run exact verdict hashing, ancestry, path coverage, focused tests, and finalizer isolation checks"
  },
  "hard_invariants": [
    "No source or test mutation",
    "No dispatcher or TAFE configuration or runtime mutation",
    "No harness, credential, external-system, deployment, release, push, or history-rewrite operation",
    "No destructive cleanup",
    "No Prime-authored GO or VERIFIED",
    "No foreign dirty or staged path capture",
    "No evidence outside canonical MemBase, Deliberation Archive, numbered bridge, source, tests, and Git"
  ],
  "fail_closed_conditions": [
    "Missing or stale GO, claim, implementation-start packet, or operation-time authority",
    "Primary verdict byte, author, status, or evidence-floor drift",
    "Implementation commit is absent from current ancestry",
    "Committed source/test images differ between the implementation commit and HEAD",
    "Commit-bound focused verification fails or cannot be isolated from dirty working copies",
    "Finalizer source or tests are dirty in a way that affects commit correctness",
    "The focused include set would capture source/test, staged, or unrelated paths",
    "Applicability, clause, evidence, Git, or finalizer isolation checks fail"
  ],
  "essential_context_preservation": "The result retains the primary proposal, GO, report, independent verdict, exact verdict identity, implementation commit, source/test path coverage, command results, finalization include set, and excluded-worktree disposition"
}
```

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-VERIFIED-BRIDGE-HISTORY-001`
- `SPEC-DSI-COMMIT-GATE-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
  bounded repair proposal while preserving every downstream gate.
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` establishes the
  Cursor hardening posture implemented by the primary WI-5345 thread.
- `bridge/gtkb-wi5345-cursor-timeout-recovery-001.md` is the primary approved
  implementation proposal.
- `bridge/gtkb-wi5345-cursor-timeout-recovery-002.md` is the primary
  independent GO.
- `bridge/gtkb-wi5345-cursor-timeout-recovery-003.md` is the committed primary
  implementation report.
- `bridge/gtkb-wi5345-cursor-timeout-recovery-004.md` is the exact independent
  primary VERIFIED verdict to be final-finalized.

## Owner Decisions / Input

The owner directed completion of the black-box bridge/TAFE/harness complex and
authorized bounded in-scope defect-repair carriers through
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`. This proposal uses
that authority only to request independent review of one canonical bridge-only
finalization repair.

The dispatcher configuration troubleshooting hold remains binding. This
proposal inspects or mutates no dispatcher configuration or runtime state.
No new owner decision is required.

## Requirement Sufficiency

Existing requirements are sufficient. They define independent bridge review,
full-history verification, exact project authorization, operation-time
enforcement, commit traceability, worktree non-impairment, and fail-closed
terminal evidence. This proposal creates no new source behavior and requires
no requirement change or waiver.

## Spec-Derived Verification Plan

| Requirement | Verification | Required result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-BRIDGE-HISTORY-001` | Read primary versions 001 through 004 and this complete repair chain in order. | Both chains are complete; report and verdict authors are independent; no version is skipped or rewritten. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Read the active repair PAUTH and validate the exact target. | WI-5345 only; allowed classes are bridge, metadata, and governance evidence; one target is authorized. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Validate live claim, schema-v3 start, and operation-time authority before the no-source report and finalization. | Every gate passes for the same session, PAUTH, project, WI, and one target. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Verify timeout exit 124, bounded/redacted partial output, timeout provenance, and unchanged success behavior from committed HEAD images. | Commit-bound focused Cursor tests pass; no dispatcher source or runtime mutation is needed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Reproduce all primary mapped tests or a strictly stronger commit-bound suite and record exact results. | Every linked primary requirement has executed passing evidence. |
| `SPEC-DSI-COMMIT-GATE-001`, `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Prove commit ancestry, source/test path coverage, exact verdict identity, and focused finalization path set. | Durable trace and evaluable containing-commit evidence are complete. |
| `GOV-WORK-TREE-HYGIENE-001`, `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare pre/post status, hashes, and staged inventory for excluded paths. | No source/test, staged, or unrelated path changes or enters the final commit. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live applicability plus mandatory clause preflights. | Zero missing required/advisory specifications and zero blocking clause gaps. |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | After finalization, reconcile WI-5345 through governed CLI only. | WI-5345 becomes terminal only after the primary verdict and repair chain have containing-commit evidence. |

## Pre-Filing Preflight Subsection

Candidate applicability preflight:

- command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5345-canonical-terminal-finalization-repair --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5345-canonical-terminal-finalization-repair-001.md --json`;
- exit `0`;
- packet hash before recording this result subsection:
  `sha256:e80d1e15c8be021f2b1fd664fdd0526c48497695c47ce84f276c573c500ae004`;
- `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- `blocking_errors: []`;
- declared target paths:
  `["bridge/gtkb-wi5345-cursor-timeout-recovery-004.md"]`.

Candidate mandatory clause preflight:

- command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5345-canonical-terminal-finalization-repair --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5345-canonical-terminal-finalization-repair-001.md`;
- exit `0`;
- clauses evaluated: `5`;
- `must_apply: 4`;
- `may_apply: 1`;
- evidence gaps in must-apply clauses: `0`;
- blocking gaps: `0`.

The governed filing helper must rerun both gates against the exact final bytes
and fail closed on drift.

## Acceptance Criteria

- The primary WI-5345 lifecycle remains unchanged and latest `VERIFIED`.
- The exact primary verdict identity matches the recorded length, SHA-256,
  and Git blob.
- The implementation commit remains in current ancestry and covers the
  primary source, test, proposal, GO, and report.
- Committed source/test images remain unchanged from the implementation commit
  through `HEAD`.
- Commit-bound focused verification passes.
- The repair implementation changes no source/test byte.
- Independent Loyal Opposition authors both the repair GO and terminal
  VERIFIED verdict from session contexts distinct from Prime.
- The focused final commit includes only the primary verdict and complete
  repair chain.
- No current source/test working-copy hunk, staged path, or unrelated bridge
  thread is captured.
- No dispatcher configuration/runtime, TAFE, harness, credential, external
  system, deployment, release, push, destructive cleanup, or Git history
  rewrite occurs.

## Risk / Rollback

The main risks are treating dirty working-copy behavior as commit-bound
evidence, accepting drifted primary verdict bytes, or capturing unrelated
index/worktree state. Every case fails closed. A failed finalization leaves the
primary verdict and repair files untracked and unchanged for a later governed
retry. No rollback mutation is required because this proposal changes no
product byte.

## Recommended Commit Type

`chore(bridge)`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
