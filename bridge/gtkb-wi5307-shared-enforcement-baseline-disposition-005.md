REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912-wi5307-revised-pauth-v2
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; owner goal to close black-box bridge/TAFE/harness complex program
author_metadata_source: explicit_interactive_session_metadata

# REVISED Implementation Proposal - WI-5307 Shared Enforcement Baseline Disposition

bridge_kind: prime_proposal
Document: gtkb-wi5307-shared-enforcement-baseline-disposition
Version: 005
Responds to: bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-004.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V2-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5307

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision corrects the sole blocking authority defect from the latest Loyal Opposition verdict. The original `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715` used unregistered `forbidden_operations` tokens and was revoked after a valid successor was created. The new active authorization, `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V2-20260716`, uses only registered operation-taxonomy tokens while preserving the owner-approved two-file baseline-disposition boundary from `DELIB-202666317`.

The implementation remains unchanged in substance: after independent Loyal Opposition approval, Prime Builder will acquire a fresh `go_implementation` work-intent claim, run the implementation-start gate, then either retain only hunks with terminal owning bridge evidence or clear non-terminal foreign hunks in exactly the two target files back to committed `HEAD`.

## Findings Addressed

### F1 (P0, blocking) - Unexecutable Project Authorization

Response: corrected. Prime Builder created `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V2-20260716` with registered forbidden operations only:

- `credential_lifecycle`
- `production_deployment`
- `dispatcher_mutation`
- `external_system_mutation`
- `destructive_cleanup`
- `git_history_rewrite`
- `git_push`

The invalid predecessor `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715` was revoked after the successor was written. The bounded scope text still excludes dispatcher topology/routing mutation and unrelated runtime mutation without placing unregistered labels in the operation-token field.

## Corrected Authority Evidence

- Owner decision: `DELIB-202666317`
- Corrected active PAUTH: `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V2-20260716`
- Revoked invalid PAUTH: `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715`
- Latest blocking verdict answered: `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-004.md`

The corrected PAUTH includes only `WI-5307`, includes `GOV-WORK-TREE-HYGIENE-001` and `ADR-DISPATCHER-ARCHITECTURE-001`, and permits only the mutation classes needed for the two-file baseline-disposition slice: `bridge`, `metadata`, `governance_evidence`, `source`, `configuration`, and `test`.

## Requirement Sufficiency

Existing requirements remain sufficient for this revised proposal. `WI-5307`, `TEST-11450`, owner decision `DELIB-202666317`, and the corrected active PAUTH define the implementation boundary. Any feature completion for `WI-5166`, `WI-5254`, `WI-5237`, `WI-5255`, `WI-5268`, or any black-box child work item remains outside this slice and requires its own bridge authority.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`

## Cross-Harness Disposition

This proposal touches one Claude hook file and one shared implementation-authorization script. The authorized action is baseline disposition only, not a cross-harness behavior rollout.

| Harness / surface | Disposition |
| --- | --- |
| Claude Code / `.claude/hooks/bridge-compliance-gate.py` | In scope only for exact baseline disposition. Non-terminal foreign hunks are cleared to committed `HEAD` unless independent terminal owning bridge evidence exists. |
| Codex / helper-mediated bridge writes | No Codex hook semantic change is authorized. Codex continues to use governed helper-mediated bridge writes. No `.codex/**` target is included. |
| Cursor, Antigravity, API, Goose, Ollama, OpenRouter | No direct harness-surface mutation is authorized. No generated skill, hook adapter, or runtime projection is changed by this slice. |
| Cross-harness parity | If implementation retains any hunk that changes hook semantics, the implementation report must cite terminal owning bridge evidence and include matching parity verification; otherwise expected result is no net behavior change relative to committed `HEAD`. |

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - governs clean baseline, foreign-work disposition, and hunk ownership.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires operation-time PAUTH vocabulary to pass before implementation starts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before `VERIFIED`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - governs owner-decision evidence carried into approval-dependent bridge work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - preserves backlog/WI traceability for derived blocker work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - preserves the Codex helper-mediated path rather than assuming Claude hook coverage applies to Codex.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governs durable artifact routing for owner-approved work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs lifecycle transitions from finding to work item to proposal.
- `ADR-DISPATCHER-ARCHITECTURE-001` - governs the dispatcher/bridge/TAFE complex affected by the black-box hardening dependency.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires explicit cross-harness disposition for harness-surface changes.
- `ADR-CROSS-HARNESS-PARITY-001` - governs parity handling for harness-specific behavior changes.

## Prior Deliberations

- `DELIB-202666317` - Owner approves WI-5307 shared enforcement baseline disposition.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` - original Prime proposal.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-002.md` - rejected non-executable GO based on the invalid predecessor PAUTH.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-003.md` - Prime NO-ACTION rejecting the non-executable GO after work-intent acquisition failed closed.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-004.md` - Loyal Opposition NO-GO requiring corrected PAUTH vocabulary before a fresh proposal.
- `DELIB-202666310` - Loyal Opposition GO verdict for dispatcher black-box specification foundation; documents the WI-5268 clean-baseline condition.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-006.md` - latest WI-5254 state is NO-GO.
- `bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-006.md` - latest WI-5237 state is NO-GO.
- `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-006.md` - terminal WI-5229 finalizer thread, relevant only for independently verified hunk ownership.

## Owner Decisions / Input

- `DELIB-202666317` captures the owner's approval to finalize or clear the existing foreign work in `.claude/hooks/bridge-compliance-gate.py` and `scripts/implementation_authorization.py`.
- `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666317.json` is the formal packet cited by the original GO verdict.
- No new owner decision is introduced by this revision; the V2 PAUTH preserves the already captured owner decision while correcting invalid registered-operation vocabulary.

## Proposed Scope

- Classify current dirty hunks in `.claude/hooks/bridge-compliance-gate.py` and `scripts/implementation_authorization.py` against live bridge states and exact owning work items.
- Retain only content with independently terminal owning bridge evidence.
- Clear all non-terminal or unowned foreign hunks in the two files back to the committed `HEAD` baseline.
- Do not implement `WI-5166`, `WI-5254`, `WI-5237`, `WI-5255`, `WI-5268`, or child black-box work in this slice.
- After cleanup, record `HEAD`, blob IDs, and zero-output status/diff evidence for the two target files so `WI-5268` can begin under its own bridge authority.

## Required Implementation-Start Evidence After GO

After a fresh Loyal Opposition GO, Prime Builder must run the normal gated sequence before protected mutation:

```text
python scripts/bridge_claim_cli.py claim gtkb-wi5307-shared-enforcement-baseline-disposition --session-id 019f69a3-25dd-75e1-83d6-8c4aa29fb912-wi5307-revised-pauth-v2 --ttl-seconds 3600
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition
```

The resulting implementation-start packet must bind `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V2-20260716`, `WI-5307`, and only the two declared target paths.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run `git status --short -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py` and `git diff --exit-code -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py`; expected clean after implementation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run live bridge applicability and clause preflights; implementation report must carry this revised bridge thread and exact target-path evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Fresh work-intent claim and implementation-start packet must pass using `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V2-20260716`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file <candidate>` during filing; expected `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include `TEST-11450` mapping plus executed clean-baseline commands. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate project authorization metadata and exact target paths in the implementation-start packet. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run `gt bridge show gtkb-dispatcher-black-box-spec-foundation --json --compact` and record that `WI-5268` remains latest GO/NO-GO state as applicable, then verify the exact clean-baseline evidence needed before WI-5268 starts. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` / `ADR-CROSS-HARNESS-PARITY-001` | Verify the cross-harness disposition is present and implementation either restores committed baseline or cites terminal owning evidence for any retained hook semantic hunk. |

## Acceptance Criteria

- `.claude/hooks/bridge-compliance-gate.py` and `scripts/implementation_authorization.py` have no non-terminal foreign hunks relative to committed `HEAD`.
- Any retained hunk has a cited terminal owning bridge thread; otherwise both files match `HEAD` exactly.
- `WI-5268` clean-baseline condition can be satisfied for the two previously dirty files without absorbing foreign work into `WI-5268`.
- No `.codex/**`, generated harness adapter, dispatcher topology, credential, deployment, external system, destructive cleanup, git push, or unrelated runtime surface is mutated.

## Risks / Rollback

Risk is moderate because the later implementation may touch shared enforcement files. The implementation must fail closed around latest bridge status, work-intent claim, implementation-start packet, exact target paths, hunk ownership, and owner-decision evidence.

Rollback is to restore the two target files to the committed `HEAD` baseline. Bridge files, Deliberation Archive rows, project authorization records, and work-item records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`

## Recommended Commit Type

`chore`
