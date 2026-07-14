NEW

# Implementation Proposal - Install the minimal governed Git binding substrate before Gate 1.25

bridge_kind: prime_proposal
Document: gtkb-modernization-wi5187-minimal-git-binding-substrate
Version: 001
Date: 2026-07-11 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3618-1eea-7252-b02b-a3b9b6401bf7
author_model: GPT-5 family (Codex)
author_model_version: not exposed by harness
author_model_configuration: Codex desktop, default collaboration mode, interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-WI-5187-GATE-125-FOUNDATION-20260711
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5187

target_paths: [".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/manifest.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/attempt-record.md", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/command-packet.ps1", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/recovery-packet.ps1", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/initial-registry.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/initial-audit-event.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/preflight-evidence.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/validation-result.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/transaction.lock", ".gtkb-state/git-lifecycle/branch-bindings.json", ".gtkb-state/git-lifecycle/branch-binding-audit.json*", ".groundtruth/formal-artifact-approvals/*-DELIB-*.json", ".gitattributes", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/authority.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/bindings.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/scoped_commit.py", "scripts/implementation_start_gate.py", "scripts/protected_mutation_guard.py", "scripts/check_git_branch_binding_promotion.py", "scripts/check_governed_git_lifecycle.py", "scripts/check_modernization_nonimpairment.py", "groundtruth-kb/tests/test_cli_git_lifecycle.py", "groundtruth-kb/tests/test_git_lifecycle_models.py", "groundtruth-kb/tests/test_git_lifecycle_authority.py", "platform_tests/scripts/test_git_binding_bootstrap.py", "platform_tests/scripts/test_git_branch_binding.py", "platform_tests/scripts/test_git_scoped_commit.py", "platform_tests/scripts/test_git_lifecycle_host_root.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protected_mutation_guard.py", "platform_tests/scripts/test_check_git_branch_binding_promotion.py", "platform_tests/scripts/test_check_governed_git_lifecycle.py", "platform_tests/scripts/test_check_modernization_nonimpairment.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "platform_tests/scripts/test_gitattributes_lf_policy.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
bootstrap_runtime_state_in_scope: true

## Claim

Install and independently verify the smallest governed Git binding and scoped-commit substrate that can carry every Gate 1.25 child through one ordinary project/work-item workflow, while preserving all existing source and unrelated work and leaving integration, promotion, GitHub, quiescence, cleanup, release, and deployment unavailable.

## Requirement Sufficiency

The requirements are sufficient. Exact owner approval is preserved in `DELIB-202666093`, and `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v3 is stored with content SHA-256 `E8F50DD36CA48E3B02BF36389CBB95B66D5E59DEAAD0AB5CB71DC25A7D64D425`. That amendment supplies the single-use WI-5187 bootstrap, host-root authority rule, direct slice-verification contract, exact 28-assertion applicability map, and deferred ownership boundaries. The Git ADR/REQ, modernization non-impairment GOV, worktree hygiene GOV, project-authorization DCL, bridge and verification gates, and artifact evaluability DCL supply the remaining authority.

No additional formal requirement is needed for this slice. DCL approval alone does not authorize filing. This proposal may be filed only after the exact Option A activation decision is durably captured, the WI-5158 thread is owner-parked, the Git Lifecycle order is reconciled, and the WI-5187 PAUTH named above is current.

## Current Entry Evidence

- `DELIB-202666083` records the owner's selection of Option A and grants no implementation authority.
- `DELIB-202666093` records the owner's exact hash-bound DCL v3 approval and grants no implementation or Git authority.
- WI-5187 v2 is open, backlogged, unapproved, P0, and explicitly limited to this foundation.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v3 is stored as `specified`; its 32 implementation assertions are expected-red because `scripts/check_git_branch_binding_promotion.py` does not yet exist.
- At content-freeze time, the PAUTH named in this proposal does not exist. Filing preflight must prove that exact PAUTH is active, includes only WI-5187, and is the operative authorization for this proposal. The current WI-5158-only PAUTH cannot authorize filing, claiming, or implementing WI-5187 and must be revoked before this proposal is published.
- The prior WI-5158 bridge chain remains non-actionable for implementation under the Gate 1.25 hold. It is not reused as WI-5187 review authority.
- `gt git binding`, the binding registry, and the audit do not exist.
- Read-only remote evidence currently reports `origin` `refs/heads/develop` and local `refs/remotes/origin/develop` at `5297fc6719a4980ca175e4fe50ec9dbcabfa4a7e`; local `refs/heads/develop` is divergent at `0d852c33b295d9f3678d7ec73e4218b89a8bfae3` and is not accepted as base authority.
<!-- in-root-disclosure -->
- An attached worktree remains outside `E:\GT-KB` at `C:\Users\micha\.codex\worktrees\claude-design-backlog`. Bootstrap preflight must fail until it is separately and safely dispositioned.
<!-- /in-root-disclosure -->
- `groundtruth.db` is already dirty from unrelated governed activity. Clean database bytes are not an entry condition; exact logical authority versions, target ownership, claim serialization, and allowed DA delta are.
- The protected source, helper, and test targets inspected for this draft are currently clean. Every target is rehashed and ownership-checked before filing, claim, implementation start, exact-manifest review, and bootstrap.

## In-Root Placement Evidence

Every fixed source, test, configuration, runtime, and governance path is inside `E:\GT-KB`. Both new worktrees are under `E:\GT-KB\.gtkb-state\git-lifecycle\worktrees\`. Canonical MemBase, registry, and audit resolution is anchored to the common-directory host root even when the command runs inside a worktree. Agent Red, external repositories, harness scratchpads, and `E:\Claude-Playground` are outside scope.

Any attached out-of-root worktree blocks the exact bootstrap preflight. This proposal does not authorize moving or deleting one.

## Authority And Activation Sequence

1. Revalidate the stored owner-approved DCL v3 content, assertions, metadata, and version.
2. Obtain independent design review of this proposal draft and the non-executable `GBM-WI-5187-001` manifest design.
3. Prepare one exact owner activation packet that terminals or supersedes the WI-5158 pilot PAUTH, parks its bridge thread, creates the bounded WI-5187 PAUTH, and names this proposal hash. None of those changes may be inferred from DCL approval.
4. Revalidate targets and file this proposal through the governed bridge helper only after the WI-5187 PAUTH exists.
5. Obtain an independent Loyal Opposition `GO` from a distinct session context.
6. Acquire exact work intent and a successful implementation-start decision without changing source or Git state.
7. Materialize only the runtime review packet defined by `GBM-WI-5187-001-DESIGN-20260711`.
8. Obtain a separate independent governance-review `GO` on every packet byte and hash.
9. Obtain owner approval of the exact manifest hash.
10. Repeat all preflight evidence, consume the bootstrap in the Deliberation Archive, and execute or recover only the approved transaction.
11. Implement and test the bounded source slice in the active WI-5187 worktree.
12. File an implementation report and obtain independent `VERIFIED` using direct evidence. Only then may ordinary Gate 1.25 bindings be created.

Every step fails closed on stale or contradictory evidence. A later step cannot repair a missing earlier authority.

## Deterministic Identities

- manifest: `GBM-WI-5187-001`
- project branch: `project/gtkb-platform-modernization-git-lifecycle`
- work-item branch: `work-item/wi-5187-implement-minimal-governed-git-binding`
- project worktree: `.gtkb-state/git-lifecycle/worktrees/project-gtkb-platform-modernization-git-lifecycle`
- work-item worktree: `.gtkb-state/git-lifecycle/worktrees/wi-5187-implement-minimal-governed-git-binding`
- registry: `.gtkb-state/git-lifecycle/branch-bindings.json`
- audit: the exact append-only host-root audit declared in `target_paths`
- exact-packet review thread: `gtkb-modernization-wi5187-bootstrap-manifest-review`

Names are immutable after activation. Collision, case-fold collision, title drift, ambiguous normalization, stale base, or an already bound ref fails without suffixing or adoption.

## Canonical Host-Root State

`repository.py` resolves four distinct identities: canonical GT-KB host root, Git common directory, main checkout, and operation worktree. The canonical host root is derived from and verified against the common directory and required GT-KB root markers; it is not inferred from the process working directory.

`authority.py`, `bindings.py`, the evaluator scripts, and every CLI route read `E:\GT-KB\groundtruth.db`, the host-root registry, and the host-root audit regardless of which bound worktree launches them. A worktree-local copied database, registry, audit, approval packet, session cache, or dispatcher report is non-authoritative and produces a stable denial.

The binding record stores both host root and operation worktree identity. Tests invoke identical read and denial operations from the main checkout, project worktree, WI worktree, a detached in-root worktree, a wrong bound worktree, and a synthetic worktree-local authority copy.

## One-Time Bootstrap Packet

The exact packet follows design `GBM-WI-5187-001-DESIGN-20260711`. Its command and recovery scripts are byte-reviewed runtime artifacts, not source implementation. They use a pre-created stable lock file, deterministic hashes, expected-old ref updates, exact initial registry and audit bytes, and no hidden prompt or inferred default.

After the final read-only preflight, the command records the exact manifest-bound bootstrap attempt through `gt deliberations record`. The stable source reference and content hash are fixed; the collision-safe DELIB ID and its formal-approval filename are transaction outputs and are immediately validated. That governed logical insertion, its one approval packet, the two refs, two worktrees, registry, audit, and validation result are the only pre-activation changes.

The command never fetches, stages, commits, resets, cleans, moves, deletes, pushes, mutates GitHub or dispatcher state, acquires quiescence, drains or terminates a worker, imports a legacy baseline, rewrites history, or edits source/configuration bytes. The index and source/configuration fingerprints remain identical. `groundtruth.db` and the generated approval packet are never staged or committed by bootstrap.

The DA attempt consumes the exception before the first repository mutation. Any partial result is recovery-required under the same manifest and transaction; it never permits a second attempt.

## Binding Service And CLI

The minimal `groundtruth_kb.git_lifecycle` package provides:

- `models.py`: canonical JSON, versioned records/envelopes, deterministic hashes, state transitions, and validation;
- `repository.py`: host-root/common-dir/worktree identity, canonical remote observation, repository lock, expected-old ref operations, ancestry, index/diff inspection, and preservation evidence;
- `authority.py`: current MemBase project/WI/PAUTH, formal carriers, proposal/GO, claim, implementation start, role/session, and target-scope resolution without synthesizing authority;
- `bindings.py`: bootstrap adoption, reserve/activate/create/list/show/validate/recover, generation compare-and-swap, atomic registry replacement, and append-only audit; and
- `scoped_commit.py`: allowed path/hunk intersection, disposable index, hooks and credential preflight, deterministic commit evidence, and unrelated-byte preservation.

The bounded public routes are:

- `gt git binding create-project`
- `gt git binding create-work-item`
- `gt git binding list`
- `gt git binding show`
- `gt git binding validate`
- `gt git binding recover`
- `gt commit scoped --binding-id <id>`

Each mutating route supports deterministic `--dry-run` and JSON. Closing, work-item integration, project and stage promotion, GitHub mutation, quiescence, cleanup, release, and deployment are explicit unavailable denials tied to WI-5158, WI-5159, WI-5160, or their existing release authority. No success stub is allowed.

## Operation-Time Mutation Gate

`scripts/implementation_start_gate.py` and `scripts/protected_mutation_guard.py` require an active current binding for protected mutation after foundation activation. They revalidate host root, common directory, repository fingerprint, attached branch, worktree, binding generation, parentage, head, current PAUTH, proposal/GO, work intent, implementation-start evidence, role/session, claimed paths, and target intersection immediately before mutation.

Wrong branch, wrong worktree, detached HEAD, worktree-local authority, stale head, stale registry, missing parent binding, expired claim, foreign claim, overlapping path, changed PAUTH, terminal/nonimplementation bridge state, or dispatcher-derived role evidence produces a stable denial and no protected mutation. Error output names the exact read-only diagnosis command and governed next operation so the right path is also the obvious path.

## Scoped Commit And VERIFIED Finalization

`gt commit scoped` computes the stageable set from the exact current intersection of PAUTH, proposal targets, work-intent paths, active binding, and attributable diff hunks. It uses a disposable index, preserves pre-existing staged/unstaged/untracked/ignored and concurrent content, rejects broad staging and ambiguous commingled files, runs required hooks and credential scans, and emits binding/authority/claim/transaction evidence.

The canonical Claude VERIFIED helper and managed Codex and Cursor copies delegate commit construction to this service. They remain byte-identical and LF-only and retain no independent whole-file or broad-path commit path. Pending verdict/report evidence may be transaction input; it becomes durable terminal evidence only if the scoped commit succeeds. Failure removes only the new uncommitted verdict and temporary transaction state.

`.gitattributes` adds the narrow Cursor managed-skill LF rule needed for reproducible helper bytes. No unrelated line-ending policy changes are included.

## Exact Assertion Applicability

| Carrier | `MUST_APPLY` to WI-5187 | `DEFERRED_TO` | Conditional |
| --- | --- | --- | --- |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` v1 | `GIT-ADR-A1`, `GIT-ADR-A3`, `GIT-ADR-A6`, `GIT-ADR-A7` | `GIT-ADR-A2`, `GIT-ADR-A4` -> WI-5158; `GIT-ADR-A5` -> WI-5159 | none |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v1 | `GIT-REQ-A1`, `GIT-REQ-A2`, `GIT-REQ-A3`, `GIT-REQ-A6`, `GIT-REQ-A8` | `GIT-REQ-A4` -> WI-5158; `GIT-REQ-A5` -> WI-5159; `GIT-REQ-A7` -> WI-5160 | none |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v3 | `BRANCH-BIND-A1`, `BRANCH-BIND-A2`, `BRANCH-BIND-A3`, `BRANCH-BIND-A4`, `BRANCH-BIND-A7`, `BRANCH-BIND-A8`, `BRANCH-BIND-A9` | `BRANCH-BIND-A5` -> WI-5158; `BRANCH-BIND-A6` -> WI-5159 | none |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1 | `A1`, `A2`, `A3` | none | `A4` is N/A only with deterministic no-worker-loading-change proof; otherwise MUST_APPLY or UNASSESSED |

The three new direct evaluator scripts produce machine-readable results for all 28 entries: 19 applicable, 8 deferred, and 1 conditional. They never convert deferred or unsupported entries to pass. The full DCL aggregate remains non-passing until later owners complete their duties.

## Specification Links

- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v3 - sole bootstrap, host-root authority, binding, scoped commit, recovery, applicability, and no-false-pass rules; exact approval is `DELIB-202666093`.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` v1 - project/work-item topology and released-main semantics.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v1 - binding, mutation, commit, integration, promotion, and failure outcomes.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1 - mandatory intuitiveness, baseline, result, rollback, and hard-invariant evidence.
- `GOV-WORK-TREE-HYGIENE-001` - isolated work and preservation of unrelated content.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` v1 - current PAUTH bounds at proposal, claim, start, binding, commit, and recovery operations.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - exact project/WI implementation authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent proposal review, report, and verification authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - complete current carrier linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, WI, and PAUTH linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - direct spec-derived executed evidence before VERIFIED.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` v1 - no unsupported, skipped, partial, or unassessed evidence can satisfy an applicable assertion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable linkage and explicit lifecycle state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - proposal, implementation, report, verification, supersession, and recovery transitions stay explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform-only in-root placement; Agent Red remains isolated.

## Prior Deliberations

- `DELIB-202666083` - owner selects Option A, the minimal binding substrate before Gate 1.25.
- `DELIB-202666082` - owner approves operation-time PAUTH enforcement DCL bytes without implementation authority.
- `DELIB-202666081` - owner approves the Gate 1.25 readiness correction and terminal design review path.
- `DELIB-202666080` - owner approves the Gate 1.25 applicability map, outcomes, tests, and ordering.
- `DELIB-20260710-GTKB-MODERNIZATION-BRANCH-BINDING-BOOTSTRAP-DCL-V2-APPROVAL` - predecessor bootstrap design superseded only where v3 says so.
- `bridge/gtkb-modernization-gate-1-25-execution-design-002.md` - independent design-only GO; no implementation authority.
- `bridge/gtkb-modernization-wi5158-git-binding-bootstrap-004.md` - corrected NO-GO whose applicability, base-authority, intuitiveness, and currentness findings are addressed here.

## Owner Decisions / Input

- `DELIB-202666093` approved and the governed CLI stored exact DCL v3; that formal mutation grants no implementation authority.
- A later activation decision must explicitly terminal or supersede the WI-5158 pilot PAUTH, create the exact WI-5187 PAUTH, and authorize filing this proposal.
- A later, separate decision must approve the exact `GBM-WI-5187-001` manifest hash after both independent reviews and live claim/start evidence.
- No approval in this chain authorizes deletion or movement of the current out-of-root worktree; that requires its own safe disposition.

## Serialization And Currentness

WI-5187 is a new prerequisite before Gate 1.25 position 1. It must be independently VERIFIED before WI-5184 starts. WI-5184, WI-5183, WI-5178, WI-5153, WI-5152, and WI-5166 then use ordinary bindings in their approved order. WI-5158 remains held until Gate 1.25 closure.

`groundtruth.db`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `scripts/implementation_start_gate.py`, `scripts/protected_mutation_guard.py`, and their tests overlap later Gate work. Exact claims are serialized; no later child may claim an overlap before WI-5187 VERIFIED and release. Any foreign implementation packet, target hash change, unexplained dirty source, active same-project claim, or changed remote base blocks filing or start.

## Cross-Harness Disposition

All harnesses use the same Python CLI, host-root authority resolver, binding registry, mutation guard, and scoped-commit service. Role comes from explicit governed session authority, never dispatcher target selection. The managed VERIFIED helper remains canonical under Claude and projected to Codex; the Cursor fallback remains byte-identical. Antigravity and provider wrappers continue to invoke the shared helper and need no duplicate implementation.

No harness-specific Git authority, registry, branch naming, recovery path, or commit implementation is introduced. Catalog and operational parity checks are both required.

## Managed-Artifact Structural Review

This Prime Builder review is structural advisory evidence for the later independent verdict; it is not a verdict or filing authority.

1. **Registry Authority Assessment: PASS.** The canonical `harness-capability-registry.toml` registers `skill.verify` with Claude as canonical, Codex and Antigravity as generated adapters, and Cursor as fallback. The helper is a managed resource under that skill. No competing registry was found.
2. **Target-Path Completeness Assessment: PASS (45 unique paths).** The canonical Claude helper, generated Codex resource, Cursor fallback, narrow LF policy, scoped-commit implementation, host-root authority, focused finalization tests, and parity commands are present. The adapter generator already projects helper resources; its source does not change. `SKILL.md` bytes do not change, so capability-registry and skill-manifest hash edits would be false churn. Antigravity and API harnesses invoke the canonical Claude helper and require no duplicate helper target.
3. **Stale-Assumption Warnings: none carried as authority.** The active WI-5158 PAUTH is explicitly rejected for WI-5187, the old WI-5158 bridge chain is cited as corrective history rather than current `GO`, Cursor is treated as a fallback rather than a generated adapter, and dispatcher selection is not role evidence.
4. **Specification Linkage Gap Report: none.** The managed-resource change is linked to bridge authority, spec-derived verification, artifact governance, Git lifecycle, non-impairment, and worktree constraints, with byte-parity and operational commands.
5. **Lifecycle Compliance Status: PASS for NEW filing after activation prerequisites.** The first line and version are correct, prior deliberations are populated, and no predecessor exists for this slug. The governed writer must refuse publication until the exact Option A activation record, owner-directed WI-5158 park, reconciled project order, and WI-5187 PAUTH are current.
6. **Artifact Quality Assessment: PASS.** The helper change has one purpose, retains the existing skill's usage boundaries, removes a competing commit implementation, and has no placeholder section.
7. **Overall Recommendation: GO for later independent structural review after activation prerequisites; NO filing now.** This review grants no PAUTH, bridge, bootstrap, source, Git, or verification authority.

## Intuitiveness/Non-Impairment Disposition

The pervasive narrative is one sentence: select the governed project/work item, work in its bound worktree, and let `gt` validate and commit only that work. A denial names the exact mismatch and next governed command. Workers never need dispatcher configuration as a role or branch hint.

Baseline evidence records all current refs, worktrees, target hashes, claims, authority versions, source/index bytes, and known unrelated dirty state. Result evidence repeats them and isolates the exact DA/formal-packet/runtime/source deltas. Hard invariants are host-root singularity, one bootstrap, no source before active binding, operation-time authority, wrong-context no mutation, attributable commits, unrelated-byte preservation, no second finalizer commit path, no false aggregate pass, and no deferred-route success.

Rollback for source implementation is the exact scoped commit reversal after preserving evidence; bootstrap state is never destructively rolled back. A partial bootstrap enters same-manifest recovery. Ref deletion, worktree deletion, reset, clean, branch rename, suffix, force update, history rewrite, or hidden adoption is not rollback.

No active worker-loading file is changed in this minimal slice unless the deterministic superseded-guidance scan proves one must change. Such a finding blocks start and requires a reviewed target/PAUTH revision; it cannot be silently folded in.

## Specification-Derived Verification Plan

| Requirement | Executable evidence |
| --- | --- |
| One canonical host-root authority | Main/project/WI/wrong-worktree parity tests; worktree-local DB/registry/audit denial |
| Single-use pre-source bootstrap | Exact manifest validate-only fixtures, DA idempotency, second-attempt denial, source/index before/after hashes |
| Deterministic bindings | Naming, collision, ancestry, parent, worktree identity, registry CAS, and audit-link tests |
| Operation-time authority | PAUTH/GO/claim/start/session/target stale and conflicting negative matrix |
| Scoped commits | Authorized path/hunk tests, commingled ambiguity denial, disposable-index and unrelated-byte preservation |
| One VERIFIED finalizer path | Claude/Codex/Cursor byte parity, LF policy, delegated scoped commit, atomic failure tests |
| Recovery without guessing | Partial-state matrix using same manifest/transaction and contradiction preservation |
| Honest slice status | Three direct evaluator scripts report 19 applicable, 8 deferred, 1 conditional; aggregate DCL remains non-pass |
| Non-impairment | Baseline/result/rollback/hard-invariant JSON plus active worker-loading supersession scan |

Required focused commands:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_git_lifecycle.py groundtruth-kb/tests/test_git_lifecycle_models.py groundtruth-kb/tests/test_git_lifecycle_authority.py platform_tests/scripts/test_git_binding_bootstrap.py platform_tests/scripts/test_git_branch_binding.py platform_tests/scripts/test_git_scoped_commit.py platform_tests/scripts/test_git_lifecycle_host_root.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py platform_tests/scripts/test_check_git_branch_binding_promotion.py platform_tests/scripts/test_check_governed_git_lifecycle.py platform_tests/scripts/test_check_modernization_nonimpairment.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/scripts/test_gitattributes_lf_policy.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py groundtruth-kb/src/groundtruth_kb/git_lifecycle scripts/implementation_start_gate.py scripts/protected_mutation_guard.py scripts/check_git_branch_binding_promotion.py scripts/check_governed_git_lifecycle.py scripts/check_modernization_nonimpairment.py groundtruth-kb/tests/test_cli_git_lifecycle.py groundtruth-kb/tests/test_git_lifecycle_models.py groundtruth-kb/tests/test_git_lifecycle_authority.py platform_tests/scripts/test_git_binding_bootstrap.py platform_tests/scripts/test_git_branch_binding.py platform_tests/scripts/test_git_scoped_commit.py platform_tests/scripts/test_git_lifecycle_host_root.py platform_tests/scripts/test_check_git_branch_binding_promotion.py platform_tests/scripts/test_check_governed_git_lifecycle.py platform_tests/scripts/test_check_modernization_nonimpairment.py
groundtruth-kb/.venv/Scripts/python.exe scripts/check_git_branch_binding_promotion.py --work-item WI-5187 --gate verification --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_governed_git_lifecycle.py --work-item WI-5187 --gate verification --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_nonimpairment.py --work-item WI-5187 --gate verification --json
powershell -NoProfile -File .gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/command-packet.ps1 -ValidateOnly
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --markdown
groundtruth-kb/.venv/Scripts/python.exe scripts/harness_parity_phase2.py --project-root . --format markdown
```

The full `gt assert --spec DCL-GIT-BRANCH-BINDING-PROMOTION-001` result is also captured and is expected to remain non-passing for explicitly deferred duties. It is never used as WI-5187 acceptance proof.

## Acceptance Criteria

- Exact DCL v3, PAUTH, proposal/GO, claim, and implementation-start evidence are current at every mutation.
- The bootstrap packet passes independent packet review and owner hash approval before its DA attempt.
- Any out-of-root attached worktree, changed remote base, local object absence, ref/worktree/registry collision, foreign claim, stale authority, or target mismatch denies with no bootstrap attempt.
- The DA attempt exists exactly once by stable source reference/content hash before the first repository mutation and permanently consumes bootstrap.
- Project and WI refs start at the exact canonical remote `develop` commit with no imported baseline.
- Both worktrees are in-root, attached to exact refs, and observe one host-root MemBase/registry/audit.
- Registry generation 1 and audit linkage validate; partial state is recovery-only.
- No protected source/configuration or shared index byte changes before active binding; only the exact DA/formal-packet/runtime deltas occur.
- All bounded CLI routes have dry-run/JSON, currentness checks, stable denials, and side-effect-free negative behavior.
- `gt commit scoped` preserves all unrelated content and rejects ambiguous ownership.
- Managed VERIFIED helpers delegate to the scoped service, remain parity-clean/LF-only, and retain no broad staging path.
- Deferred integration, promotion, GitHub, quiescence, cleanup, release, and deployment routes fail explicitly unavailable.
- All required focused commands pass; all 19 applicable outer assertions have direct evidence; 8 deferred assertions remain non-passing; conditional A4 has explicit provenance.
- Independent Loyal Opposition verification cites the executed evidence and confirms no aggregate false-green claim.

## Risks / Rollback

The highest risks are an authority fork between worktrees, accidental shared-source mutation, stale remote base, concurrent DB/claim churn, an over-broad commit, or a bootstrap recovery path that guesses. Host-root parity tests, exact locks and hashes, stable source-reference idempotency, operation-time revalidation, disposable indexes, before/after fingerprints, and recovery-only partial states address them.

Bootstrap has no destructive rollback. The DA attempt, refs, worktrees, registry, and audit remain evidence. Recovery either completes the exact approved state or preserves it for owner disposition. Source implementation rollback is limited to the exact scoped work-item commit after verification; it never removes bootstrap history or unrelated work.

## Authority Boundary

Presence of this body at its draft path grants no authority. Publication as a live `NEW` proposal grants only Loyal Opposition review actionability; it does not grant a verdict, claim, implementation packet, implementation start, packet materialization, DA attempt, approval packet, ref, worktree, registry, audit, source/test/config/database mutation, Git commit, merge, push, dispatcher control, quiescence, cleanup, release, or deployment authority.

## Files Expected To Change

- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/manifest.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/attempt-record.md`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/command-packet.ps1`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/recovery-packet.ps1`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/initial-registry.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/initial-audit-event.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/preflight-evidence.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/validation-result.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/transaction.lock`
- `.gtkb-state/git-lifecycle/branch-bindings.json`
- `.groundtruth/formal-artifact-approvals/*-DELIB-*.json`
- `.gitattributes`
- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/authority.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/bindings.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/scoped_commit.py`
- `scripts/implementation_start_gate.py`
- `scripts/protected_mutation_guard.py`
- `scripts/check_git_branch_binding_promotion.py`
- `scripts/check_governed_git_lifecycle.py`
- `scripts/check_modernization_nonimpairment.py`
- `groundtruth-kb/tests/test_cli_git_lifecycle.py`
- `groundtruth-kb/tests/test_git_lifecycle_models.py`
- `groundtruth-kb/tests/test_git_lifecycle_authority.py`
- `platform_tests/scripts/test_git_binding_bootstrap.py`
- `platform_tests/scripts/test_git_branch_binding.py`
- `platform_tests/scripts/test_git_scoped_commit.py`
- `platform_tests/scripts/test_git_lifecycle_host_root.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`
- `platform_tests/scripts/test_check_git_branch_binding_promotion.py`
- `platform_tests/scripts/test_check_governed_git_lifecycle.py`
- `platform_tests/scripts/test_check_modernization_nonimpairment.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `platform_tests/scripts/test_gitattributes_lf_policy.py`
- `groundtruth.db`

## Recommended Commit Type

`feat`
