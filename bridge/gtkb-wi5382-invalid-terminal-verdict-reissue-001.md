NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; ::open build; approval_policy=never
author_metadata_source: explicit_current_codex_thread_metadata

# WI-5382: Reissue Malformed Terminal VERIFIED Verdict

bridge_kind: prime_proposal
Document: gtkb-wi5382-invalid-terminal-verdict-reissue
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5382-IMPLEMENTATION-START-PACKET-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5382

target_paths: ["bridge/gtkb-wi5382-implementation-start-packet-contract-004.md", "independent-progress-assessments/WI-5382-invalid-terminal-verdict-004.finalization-diagnostic.md"]

implementation_scope: bridge repair and governance evidence only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The WI-5382 implementation report at `bridge/gtkb-wi5382-implementation-start-packet-contract-003.md` was substantively verified by Loyal Opposition, but the terminal `VERIFIED` artifact at `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md` is not mechanically finalizable. The read-only per-thread finalization repair planner classifies the thread as `terminal_verified_blocked_missing_scope` because the latest VERIFIED verdict has no finalizer-recognized `Responds to` implementation-report reference. The file is also untracked, so it is not a valid same-transaction terminal commit outcome.

Prime Builder proposes a narrow repair: archive the exact invalid untracked verdict bytes and planner diagnostic, remove only that invalid untracked terminal verdict from the live bridge chain after GO, restore the WI-5382 thread to latest implementation report `-003`, and request Loyal Opposition to reissue a helper-valid `VERIFIED` verdict through the canonical finalizer with the correct report reference and exact include set.

## Claim

This proposal does not change the WI-5382 implementation. It corrects only the malformed terminal verdict artifact that prevents canonical finalization of already-reviewed work.

## Requirement Sufficiency

Existing requirements sufficient.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state must be role-correct, append-only, and finalization-aware.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED must be based on the implementation report and executed verification evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation and repair proposals must cite relevant specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths must be explicit.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization does not bypass bridge GO, target scope, reports, or verification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time authority must be live and target-bounded before mutation.
- `GOV-WORK-TREE-HYGIENE-001` - invalid untracked terminal artifacts must not be absorbed into broad commits.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all repair artifacts remain under the GT-KB root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, diagnostic, repair proposal, and final verdict remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - bridge report, verdict, diagnostic, repair, and finalization remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal state requires a valid finalization lifecycle, not only a status token.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded governed proposals for in-scope bridge, TAFE, and harness defects while preserving GO, claim, implementation-start, verification, and commit gates.
- `bridge/gtkb-wi5382-implementation-start-packet-contract-001.md` through `-004.md` - source thread whose latest terminal verdict is substantively positive but mechanically malformed.
- Read-only planner evidence from `scripts/per_thread_finalization_repair.py --format json` - classifies `gtkb-wi5382-implementation-start-packet-contract` as `terminal_verified_blocked_missing_scope`.

## Owner Decisions / Input

No new owner decision is required. This proposal uses the active WI-5382 PAUTH and the standing fleet-defect repair authorization. It does not request source, dispatcher, TAFE, runtime, credential, release, deployment, push, history rewrite, or unrelated worktree mutation.

## Proposed Scope

1. Before mutation, record a diagnostic evidence file at `independent-progress-assessments/WI-5382-invalid-terminal-verdict-004.finalization-diagnostic.md` containing the invalid verdict path, byte hash, Git status, planner classification, and exact reason.
2. Verify the current `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md` bytes match the archived diagnostic before any removal.
3. Remove only the untracked invalid `-004` verdict so the live source thread returns to latest implementation report `-003`.
4. Have Loyal Opposition reissue a canonical `VERIFIED` verdict for the WI-5382 source thread through `write_verdict.py --finalize-verified`, with a finalizer-recognized report reference and exact include set.

## Out Of Scope

- Any source or test change to `scripts/implementation_authorization.py` or `platform_tests/scripts/test_implementation_authorization.py`.
- Any database lifecycle correction for WI-5382.
- Any broad cleanup, reset, staging, commit, push, release, deployment, credential, dispatcher, TAFE, runtime, harness, or external-system mutation.
- Any Prime-authored `VERIFIED` verdict.

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run `python -m groundtruth_kb.cli bridge show gtkb-wi5382-implementation-start-packet-contract --json --compact` before and after repair | Before repair latest is malformed `VERIFIED`; after removing the invalid untracked file, latest returns to implementation report `NEW` at `-003` until LO reissues `VERIFIED`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Preserve and cite `bridge/gtkb-wi5382-implementation-start-packet-contract-003.md` plus LO's executed verification evidence | The reissued verdict responds to the implementation report, not an ambiguous terminal artifact. |
| `GOV-WORK-TREE-HYGIENE-001` | Archive SHA-256 and Git status for the exact invalid `-004` bytes before removal | No unrelated bridge or source files are touched. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Acquire matching claim and implementation-start authority before diagnostic/removal mutation | Repair stays target-bounded and PAUTH-backed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live bridge preflights | No missing required or advisory specs. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Rerun `python scripts/per_thread_finalization_repair.py --format json` for the WI-5382 source thread | The `terminal_verified_blocked_missing_scope` classification is gone after valid finalization. |

## Acceptance Criteria

- The invalid untracked WI-5382 `-004` verdict is archived by hash and removed only after GO and implementation-start authorization.
- The WI-5382 source thread is restored to the latest implementation report until Loyal Opposition reissues a valid finalizer-compatible `VERIFIED`.
- The reissued `VERIFIED` verdict can be committed with the implementation report, verified test hunk, proposal/GO/report chain, and final verdict in one focused terminal transaction.
- No source, test, dispatcher, TAFE, runtime, credential, release, deployment, push, history rewrite, or unrelated worktree path is changed by this repair.

## Risks / Rollback

Risk is low if the repair remains byte-checked and single-file scoped. Rollback is to restore the archived invalid `-004` bytes only if removal was performed against the wrong file; otherwise the correct path is Loyal Opposition reissue through the canonical finalizer.

## Files Expected To Change

- `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`
- `independent-progress-assessments/WI-5382-invalid-terminal-verdict-004.finalization-diagnostic.md`

## Recommended Commit Type

`fix`

## Pre-Filing Preflight Subsection

Before filing this proposal, Prime Builder runs:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5382-invalid-terminal-verdict-reissue --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5382-invalid-terminal-verdict-reissue-001.completed.md --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5382-invalid-terminal-verdict-reissue --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5382-invalid-terminal-verdict-reissue-001.completed.md`

Expected filing condition: applicability preflight passes with `missing_required_specs: []` and `missing_advisory_specs: []`; clause preflight exits 0 with no blocking gaps. The live filed proposal is rechecked after helper filing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
