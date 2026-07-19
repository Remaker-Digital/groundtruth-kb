NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; build activity envelope; dispatcher configuration hold preserved

# Implementation Proposal - WI-5409 terminal-finalization evidence repair

bridge_kind: prime_proposal
Document: gtkb-wi5409-terminal-finalization-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5409-TERMINAL-FINALIZATION-REPAIR-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5409

target_paths: ["bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-001.md", "bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-002.md", "bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-003.md", "bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-004.md", "bridge/gtkb-wi5409-terminal-finalization-repair-001.md", "bridge/gtkb-wi5409-terminal-finalization-repair-002.md", "bridge/gtkb-wi5409-terminal-finalization-repair-003.md", "bridge/gtkb-wi5409-terminal-finalization-repair-004.md"]

implementation_scope: bridge-only terminal-evidence repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Repair WI-5409's terminal evidence without changing its already-committed
implementation. The primary thread's version 004 says VERIFIED, but all four
primary bridge files are untracked, no Git commit contains them, and version
004 lacks the current required `author_*` provenance envelope. It therefore
cannot prove focused terminal finalization.

The source and test implementation is healthy, clean, and already tracked in
ancestor commit `35dfaf0421979e4444ba513c0f60245b672135c9`. This proposal
preserves the primary chain byte-for-byte, performs no source or test mutation,
and establishes a fresh independently reviewed repair thread whose terminal
VERIFIED transaction can commit the exact eight bridge files listed above.

## Claim

Prime Builder proposes a bounded bridge-only repair that replaces no artifact
and changes no behavior. It treats the primary version 004 as historical,
substantively useful but structurally insufficient terminal evidence. After an
independent GO, Prime will revalidate the committed implementation and file a
bridge-only implementation report. An independent Loyal Opposition session may
then issue a compliant VERIFIED verdict and use the atomic finalizer to commit
the complete primary and repair chains together.

If version 002 is anything other than GO, this exact four-version repair shape
stops. Prime must file a revised proposal with a new exact target inventory
before any later finalization attempt.

## Defect / Reproduction

Current canonical evidence reproduces the terminal-integrity defect:

1. `git status --short -- bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-001.md ... -004.md`
   reports all four primary files as untracked.
2. `git log --all --oneline --` against those four paths returns no containing
   commit.
3. Primary version 004 uses `reviewer_*` fields rather than the current
   mandatory status-bearing `author_*` provenance fields and contains no atomic
   finalization evidence.
4. WI-5409 is therefore correctly represented in MemBase as
   `resolution_status=open`, despite its historical monotonic `stage=resolved`.

The implementation itself does not need repair:

1. Commit `35dfaf0421979e4444ba513c0f60245b672135c9` is an ancestor of
   current HEAD.
2. `git diff 35dfaf0421979e4444ba513c0f60245b672135c9..HEAD --` for the
   four implementation targets is empty.
3. All four implementation targets are clean in the current worktree.
4. Current focused verification passes 27 helper/work-intent tests and 9
   project-membership tests.

## In-Root Placement Evidence

Every proposed target is under `E:\GT-KB\bridge`. No artifact outside the
project root, retired assessment directory, scratch surface, or noncanonical
carrier is cited as evidence.

## Requirement Sufficiency

Existing requirements are sufficient. This is an evidence-lifecycle defect,
not a missing behavioral requirement. The current bridge authority,
project-authorization, proposal-linkage, and mandatory spec-derived verification
requirements already define the required repair and terminal proof.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - makes the numbered bridge chain the canonical append-only status history and requires role-correct independent review.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires the fresh bounded PAUTH while preserving proposal, GO, claim/start, report, verification, and finalization gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires this proposal's PAUTH, project, and WI-5409 tuple to match active MemBase membership.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite and test every applicable governing specification before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires current executed tests mapped to every linked specification before the repair can become VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the false-terminal finding and repair decision to remain durable, linked, and explicit.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires traceability from WI-5409 through PAUTH, proposal, tests, report, verdict, commit, and MemBase reconciliation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the historical invalid terminal claim and the fresh repair lifecycle to retain distinct explicit states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every active repair artifact and dependency to remain within the GT-KB project root.
- `GOV-STANDING-BACKLOG-001` - requires WI-5409 to remain visible and nonterminal until exact verification and commit evidence exists.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers and governed proposals for newly discovered fleet and bridge defects while preserving every normal gate.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - records the proposal-standards context from which the WI-5409 project-linkage defect was derived.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner decision for this repair carrier.
- Active `PAUTH-DISPATCHER-BLACK-BOX-WI5409-TERMINAL-FINALIZATION-REPAIR-20260718` includes only WI-5409; allows only bridge, metadata, and governance-evidence mutation classes; and forbids credential lifecycle, destructive cleanup, dispatcher mutation, external-system mutation, Git history rewrite, push, production deployment, and release.
- The PAUTH explicitly permits one later focused local commit only after independent GO, the matching implementation lifecycle, and independent VERIFIED. It does not authorize rewriting or deleting primary version 004.

## Proposed Scope

1. Preserve the contents of primary versions 001 through 004 exactly as they
   exist. Do not rewrite, normalize, remove, or replace any primary artifact.
2. Preserve the four implementation targets exactly as committed at
   `35dfaf0421979e4444ba513c0f60245b672135c9`; treat them as read-only
   verification evidence.
3. After independent GO, acquire the exact repair-thread work-intent claim and
   schema-v3 implementation-start packet if required by the live gate.
4. Re-run the focused behavioral, membership, hash, cleanliness, ancestry, and
   Git-containment checks named below.
5. File a Prime implementation report at repair version 003. The report must
   say that no source, test, configuration, runtime, harness, dispatcher, TAFE,
   or primary-chain content was mutated.
6. Request independent Loyal Opposition verification from a session context
   unrelated to both this proposal author and the primary implementation
   author.
7. If VERIFIED, the Loyal Opposition finalizer must create one focused local
   commit containing exactly the four unchanged primary files and all four
   repair files. It must not include any source, test, hook, configuration,
   database, runtime-state, or unrelated dirty path.
8. Only after the containing commit exists and exact path-set verification
   passes may WI-5409 be reconciled to terminal resolution in MemBase.

## Specification-Derived Verification Plan

| Specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Inspect the complete primary and repair numbered chains; validate role/session provenance; run `git status --short` and `git log --all --oneline --` before finalization, then `git show --name-only --format=` and Git containment checks after finalization. | Before repair, primary v001-v004 are untracked and uncontained. After repair, all eight exact bridge files are in one focused commit and no other path is present. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5409-TERMINAL-FINALIZATION-REPAIR-20260718 --json`; live claim/start validation after GO. | PAUTH is active, includes only WI-5409, carries only registered mutation/operation tokens, and the later claim/start binds exactly this repair thread and target set. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Candidate and live applicability preflight plus `gt backlog show WI-5409 --json`. Run the 9-test WI/project membership subset in `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`. | PAUTH/project/work-item membership matches, preflight passes, and all 9 membership tests pass. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live applicability preflight; compare the preflight's applicable-spec set with this Specification Links section and table. | No required or advisory specification is missing and no blocking applicability error exists. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/skills/test_bridge_propose_helper.py platform_tests/skills/test_bridge_propose_helper_work_intent.py -q --tb=short`; the 9-test membership subset; exact source/test SHA-256 checks; canonical/Codex byte comparison. | 27 helper/work-intent tests pass, 9 membership tests pass, all four committed implementation hashes match the report, and canonical/Codex helpers are byte-identical. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `gt backlog show WI-5409 --json`, PAUTH inspection, and complete numbered-file inventory for both threads. | The finding, owner decision, bounded authorization, repair lifecycle, and eventual terminal evidence remain durably linked without relying on scratch or retired carriers. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Trace WI-5409 to TEST-11520, the PAUTH, both bridge chains, current tests, the focused commit, and final MemBase version. | Every lifecycle artifact is present and the terminal claim is supported by the exact commit and test evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect status tokens and MemBase versions before and after finalization. | Historical primary v004 remains preserved as invalid terminal evidence; the repair advances NEW -> GO -> NEW report -> independently VERIFIED before WI-5409 closes. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git rev-parse --show-toplevel` and resolved-path checks for every target and cited active artifact. | The root is `E:/GT-KB`; every target and active evidence dependency resolves inside it. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5409 --json` before finalization and after exact commit reconciliation. | WI-5409 remains `resolution_status=open` until terminal evidence exists, then receives one evidence-backed terminal version rather than disappearing from visibility. |

## Current Read-Only Verification Baseline

- `.claude/skills/bridge-propose/helpers/write_bridge.py`: SHA-256 `5a0145455ab89aeca0252bf26228747b2b0a3869838e608e8284ee90da505d47`
- `.codex/skills/bridge-propose/helpers/write_bridge.py`: SHA-256 `5a0145455ab89aeca0252bf26228747b2b0a3869838e608e8284ee90da505d47`
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`: SHA-256 `e34ce6326530700fe2bb194fed03392a3ca6163c9eedae9675620cc5b907e15c`
- `platform_tests/skills/test_bridge_propose_helper.py`: SHA-256 `b6291a1c25865eb9d1e4609dc986abbdd4ae47c380da178cf9ef3b1af3015315`
- Focused helper/work-intent suite: `27 passed`.
- Focused project-membership subset: `9 passed, 8 deselected`.
- Canonical/Codex helper byte parity: PASS.
- Four-target worktree cleanliness: PASS.
- Commit `35dfaf0421979e4444ba513c0f60245b672135c9` ancestry and exact four-target comparison to HEAD: PASS.

## Acceptance Criteria

- Primary versions 001 through 004 remain byte-for-byte unchanged.
- No source, test, hook, skill, configuration, database, runtime-state, harness,
  dispatcher, or TAFE target is modified by this repair.
- The four implementation targets remain clean and match the baseline hashes.
- All 27 helper/work-intent tests and all 9 membership tests pass from current
  committed bytes.
- Repair version 003 carries current command results and exact hash evidence.
- Repair version 004, if VERIFIED, has valid `author_*` provenance,
  specification-derived mapping, tests-executed evidence, exact finalization
  path inventory, and independent session context.
- The atomic finalizer's commit contains exactly the eight listed bridge files
  and no unrelated path.
- WI-5409 is not marked terminal until exact Git containment and MemBase
  reconciliation are both proven.

## Risks / Rollback

The principal risk is accidentally absorbing unrelated work or treating the
historical primary v004 as valid authority. Exact path enumeration, read-only
source hashes, a clean-staging precondition, and the atomic finalizer constrain
that risk.

There is no destructive rollback. Before terminal finalization, a NO-GO leaves
the append-only repair thread nonterminal. After terminal finalization, any
correction must be a governed successor; neither primary nor repair history is
rewritten or deleted.

## Scope Exclusions

- No mutation of `.claude/skills/bridge-propose/helpers/write_bridge.py`.
- No mutation of `.codex/skills/bridge-propose/helpers/write_bridge.py`.
- No mutation of `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`.
- No mutation of `platform_tests/skills/test_bridge_propose_helper.py`.
- No dispatcher configuration, routing, topology, runtime, lease, worker, or TAFE mutation.
- No harness-state, role, eligibility, prompt, hook, or skill configuration mutation.
- No credential lifecycle, destructive cleanup, external-system mutation, history rewrite, push, deployment, or release.
- No staging or committing of foreign or unrelated dirty work.
- No reliance on retired assessment directories or session-external scratch artifacts.

## Files Expected To Change

- `bridge/gtkb-wi5409-terminal-finalization-repair-001.md`
- `bridge/gtkb-wi5409-terminal-finalization-repair-002.md`
- `bridge/gtkb-wi5409-terminal-finalization-repair-003.md`
- `bridge/gtkb-wi5409-terminal-finalization-repair-004.md`

The following existing files enter the later focused commit unchanged:

- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-001.md`
- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-002.md`
- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-003.md`
- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-004.md`

## Recommended Commit Type

`fix`
