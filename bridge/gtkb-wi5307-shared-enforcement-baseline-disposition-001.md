NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime (2026-07-15)
author_model_configuration: Codex desktop app; Prime Builder interactive session; collaboration_mode=Default; sandbox=danger-full-access; approval_policy=never

# Implementation Proposal - Clear non-terminal shared enforcement-file foreign work blocking black-box WI-5268

bridge_kind: prime_proposal
Document: gtkb-wi5307-shared-enforcement-baseline-disposition
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5307

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Owner-approved derived blocker to clear or terminally finalize the two dirty shared enforcement files that are excluded from WI-5268 but currently block its clean-baseline GO condition.

Work item description: Derived blocker for dispatcher black-box hardening. The WI-5268 GO requires `.claude/hooks/bridge-compliance-gate.py`, `scripts/implementation_authorization.py`, and `scripts/implementation_start_gate.py` to be clean relative to committed HEAD before protected mutation. Current foreign hunks in the first two files belong to non-terminal/open work (`WI-5166`, `WI-5254`, `WI-5237`, `WI-5255`) and must be either finalized through their owning terminal bridge paths or cleared back to HEAD before WI-5268 implementation can begin. This work item governs a narrow, reversible baseline disposition for exactly those two dirty files, without hiding or absorbing non-terminal feature work into WI-5268.

## Claim

Prime Builder proposes a bounded baseline-disposition slice for `WI-5307`. The slice exists only to remove non-terminal foreign changes from two shared enforcement files so `WI-5268` can later start under its own approved `GO` and implementation-start packet.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. `WI-5307`, `TEST-11450`, owner decision `DELIB-202666317`, and project authorization `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715` define the implementation boundary. Any further feature completion for `WI-5166`, `WI-5254`, `WI-5237`, `WI-5255`, or `WI-5268` requires its own bridge scope.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/bridge-compliance-gate.py`, `scripts/implementation_authorization.py`.

## Cross-Harness Disposition

This proposal touches the harness-surface path `.claude/hooks/bridge-compliance-gate.py`; the disposition is intentionally baseline-preserving rather than a new cross-harness behavior rollout.

| Harness / surface | Disposition |
| --- | --- |
| Claude Code / `.claude/hooks/bridge-compliance-gate.py` | In scope only for exact baseline disposition. Non-terminal foreign hunks are cleared to committed HEAD unless independent terminal owning bridge evidence exists. |
| Codex / helper-mediated bridge writes | No Codex hook semantic change is authorized. Codex continues to use the governed non-bypass bridge writer and audit helper path. No `.codex/**` target is included. |
| Cursor, Antigravity, API, Goose, Ollama, OpenRouter | No direct harness-surface mutation is authorized. No generated skill, hook adapter, or runtime projection is changed by this slice. |
| Cross-harness parity | No typed waiver is requested. If implementation retains any hunk that changes hook semantics, the implementation report must cite the terminal owning bridge evidence and include the corresponding parity verification; otherwise the expected result is no net behavioral change relative to committed HEAD. |

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - governs clean baseline, foreign-work disposition, and hunk ownership.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable capture of owner decisions and derived work when work crosses governance thresholds.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before `VERIFIED`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - governs owner-decision evidence carried into approval-dependent bridge work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - preserves backlog/WI traceability while adding a derived blocker item.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - preserves the Codex helper-mediated path rather than assuming Claude hook coverage applies to Codex.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governs durable artifact routing for owner-approved work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs lifecycle transitions from finding to work item to proposal.
- `ADR-DISPATCHER-ARCHITECTURE-001` - governs the dispatcher/bridge/TAFE complex affected by the black-box hardening dependency.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires explicit cross-harness disposition for harness-surface changes.
- `ADR-CROSS-HARNESS-PARITY-001` - governs parity handling for harness-specific behavior changes.

## Prior Deliberations

- `DELIB-202666317` - Owner approves WI-5307 shared enforcement baseline disposition.
- `DELIB-202666310` - Loyal Opposition GO verdict for dispatcher black-box specification foundation; documents WI-5268 clean-baseline condition.
- `DELIB-202666261` - Loyal Opposition NO-GO verdict for WI-5255 B/C telemetry worker provenance.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-006.md` - latest WI-5254 state is `NO-GO`.
- `bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-006.md` - latest WI-5237 state is `NO-GO`.
- `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-006.md` - terminal WI-5229 finalizer thread, relevant only for independently verified hunk ownership.

## Owner Decisions / Input

- `DELIB-202666317` - owner approved finalizing or clearing the existing foreign work in `.claude/hooks/bridge-compliance-gate.py` and `scripts/implementation_authorization.py`.
- `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666317.json` - formal packet validated with `scripts/validate_formal_artifact_packet.py`.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715` - active project authorization covering only `WI-5307`.

## Proposed Scope

- Classify the current dirty hunks in `.claude/hooks/bridge-compliance-gate.py` and `scripts/implementation_authorization.py` against live bridge states and exact owning work items.
- Retain only content with independently terminal owning bridge evidence.
- Clear all non-terminal or unowned foreign hunks in the two files back to the committed HEAD baseline.
- Do not implement `WI-5166`, `WI-5254`, `WI-5237`, `WI-5255`, or `WI-5268` feature work in this slice.
- After cleanup, record HEAD, blob IDs, and zero-output status/diff evidence for the two files so `WI-5268` can begin under its own `GO`.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run `git status --short -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py` and `git diff --exit-code -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py`; expected clean after implementation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run live bridge applicability and clause preflights; implementation report must carry this proposal's bridge thread and exact target-path evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition`; expected `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include `TEST-11450` mapping plus executed clean-baseline commands. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate project authorization metadata and exact target paths in the implementation-start packet. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run `gt bridge show gtkb-dispatcher-black-box-spec-foundation --json --compact` and record that `WI-5268` remains latest `GO`, then verify the exact clean-baseline evidence needed before WI-5268 starts. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition` after `GO`; expected packet binds `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715` and only the two target paths. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` / `ADR-CROSS-HARNESS-PARITY-001` | Verify the `## Cross-Harness Disposition` is present and implementation either restores committed baseline or cites terminal owning evidence for any retained hook semantic hunk. |

## Acceptance Criteria

- `.claude/hooks/bridge-compliance-gate.py` and `scripts/implementation_authorization.py` have no non-terminal foreign hunks relative to committed HEAD.
- Any retained hunk has a cited terminal owning bridge thread; otherwise both files match HEAD exactly.
- `WI-5268` GO condition 2 can be satisfied for the two previously dirty files without absorbing foreign work into WI-5268.
- No `.codex/**`, generated harness adapter, dispatcher topology, credential, deployment, or unrelated runtime surface is mutated.

## Risks / Rollback

Risk is moderate because the proposal authorizes later protected-file work in shared enforcement files. The implementation must fail closed around bridge status, work-intent, implementation-start packet, exact target paths, hunk ownership, and owner-decision evidence.

Rollback is to restore the two target files to the committed HEAD baseline. Bridge files, Deliberation Archive rows, project authorization records, and work-item records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`

## Recommended Commit Type

`chore`
