NEW

# GT-KB WI-5142 Bounded Registry And Prunable-Worktree Readiness Repair

bridge_kind: prime_proposal
Document: gtkb-wi5142-bounded-readiness-repair
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-16T01-48-03Z-prime-builder-A-b8e790
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex interactive Prime Builder; reasoning effort xhigh; approval policy never

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI5142-BOUNDED-READINESS-REPAIR-20260716
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5142
Parent Bridge: gtkb-wi5142-hygiene-reclaim-cli-skill
Parent GO: version 004
Prior Verified Child: gtkb-wi5142-hygiene-reclaim-cli-skill-phase1 version 004

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth.db", ".git/worktrees/", ".gtkb-state/hygiene-reclaim/runs/", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_registry_schema_and_ci.py", "groundtruth-kb/tests/test_registry_drift_detection.py", "platform_tests/scripts/test_check_sot_registry_completeness.py"]

implementation_scope: configuration | metadata | governance-projection | runtime-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Repair two bounded readiness defects found by the independently verified
`gt hygiene reclaim plan`: one incorrect active SoT-registry storage path and
37 Git worktree administrative records that Git itself reports as prunable
because their gitdir targets are absent. The repair is confined to artifacts
under `E:/GT-KB`, uses canonical writers, captures before/after invariants, and
then produces a fresh read-only reclaim plan.

The owner also authorized a bounded `git reflog expire --stale-fix --all`
repair only if its dry run selected broken entries. The completed dry run
selected zero entries, retained 4,884, and emitted 69 diagnostics caused solely
by three invalid duplicate log filenames: `.git/logs/HEAD (1)`,
`.git/logs/refs/heads/develop (1)`, and `.git/logs/refs/stash (1)`. Therefore
this proposal performs no reflog mutation. Those three files remain unchanged
and require a separately reviewed exact reversible-trash batch; they are not
silently reclassified or deleted here.

No live reclaim trash/restore, Git object deletion, garbage collection, branch
or ref update/deletion, stash update/deletion, reflog mutation, permanent purge,
commit, push, release, deployment, credential operation, dispatcher mutation,
or external mutation is authorized by this proposal.

The bridge duplicate-thread guard reports the parent thread's live `GO`. That
relationship is intentional: the parent approved the complete design, the
prior child delivered and verified the non-DB implementation, and this child
uses a new owner decision and narrower PAUTH for the bounded live-readiness
repair. It neither reimplements the CLI nor competes for a second WI.

## Existing Capability Reuse

- Use `gt registry show`, `gt registry sync`, `gt registry diff`, and
  `gt registry validate`; do not edit the MemBase projection directly.
- Use `git worktree prune --dry-run --verbose --expire now` as the sole
  eligibility oracle and `git worktree prune --verbose --expire now` as the
  sole worktree-administration writer.
- Use `gt hygiene reclaim plan --json` and `history --json`; do not create a
  private cleanup script, queue, registry, or history index.
- Preserve the existing dirty worktree hunk-by-hunk. Only the named registry
  record may change in the TOML file, and only the projection rows produced by
  canonical registry sync may change in `groundtruth.db`.

## Exact Bounded Procedure

1. Record compact, deterministic SHA-256 digests and counts for refs, stashes,
   loose Git-object path/stat inventory, `.git/logs/`, the registry TOML, the
   current registry projection, and the worktree administration tree.
2. Confirm `project-resource-alias-registry` currently resolves to the missing
   `.claude/rules/project-resource-aliases.toml`, while
   `config/agent-control/project-resource-aliases.toml` is the existing
   canonical file. Change only that record's `storage_path` value.
3. Run the canonical `gt registry sync`, then require `gt registry diff` and
   `gt registry validate` to report complete TOML/MemBase parity and a passing
   reality check for all active records.
4. Re-run `git worktree prune --dry-run --verbose --expire now`. Proceed only
   if its exact output remains 37 non-empty lines, 2,921 bytes, SHA-256
   `28b1b743863df4c63911b2f31e9e6b6e8ef2ab1385365720049e7ac685094a69`,
   and every line reports either a missing gitdir file or a gitdir target at a
   nonexistent location. Any drift stops the operation.
5. Run `git worktree prune --verbose --expire now` once. Do not run `git gc`,
   object prune, reflog expire, ref deletion, branch deletion, or stash
   mutation. Require an immediate repeat dry run to emit zero candidates.
6. Recompute all invariants. Refs, stashes, loose-object inventory, reflog bytes,
   and every non-target worktree byte must match the before snapshot exactly.
7. Run a fresh compact `gt hygiene reclaim plan --json` and verify its recorded
   history. Registry and outside-worktree blockers must be gone. The plan may
   remain non-executable only for the explicitly preserved malformed duplicate
   reflog files; that remaining state is reported rather than bypassed.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - requires report-first hygiene, fresh evidence,
  deterministic selection, and bounded apply behavior.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the typed TOML registry canonical and
  MemBase a synchronized projection; direct projection edits are prohibited.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires fail-closed
  handling of stale, contradictory, incomplete, or drifting evidence.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - requires explicit disposition
  and audit preservation for obsolete artifacts rather than silent deletion.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires an independent GO and active claim
  before protected configuration, metadata, or database mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to
  the active project authorization and WI-5142.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - links the exact
  implementation behavior to governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the independent
  verdict to evaluate the requirement-derived invariants below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the owner decision,
  proposal, implementation evidence, and later malformed-artifact disposition
  as explicit durable lifecycle records.

## Prior Deliberations

- `DELIB-20260716-WI5142-BOUNDED-READINESS-REPAIR` - the owner explicitly
  approved the bounded registry correction, already-prunable worktree metadata
  repair, conditional stale-fix dry run, and fresh plan while excluding Git
  object/ref/stash mutation and all live trash.
- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` - requires
  deterministic classification, audit history, bounded cleanup, and no
  unbounded purge.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - established
  registry-first preservation after loss of essential local artifacts.
- Parent bridge `gtkb-wi5142-hygiene-reclaim-cli-skill` versions 001-004 and
  child bridge `gtkb-wi5142-hygiene-reclaim-cli-skill-phase1` versions 001-004
  establish the approved design, tested implementation, and independent
  verification. This proposal is the separately gated live-readiness step.

## Owner Decisions / Input

Owner approval is recorded as
`DELIB-20260716-WI5142-BOUNDED-READINESS-REPAIR` and is bound to active
authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI5142-BOUNDED-READINESS-REPAIR-20260716`.
It permits only the bounded readiness operations described here. The dry-run
condition for reflog mutation was not met, so no reflog writer will be invoked.

No further owner input is required for this readiness repair. A later exact
reversible-trash batch, including any malformed Git artifact, remains a
separate owner decision and bridge authorization.

## Requirement Sufficiency

Existing requirements sufficient. The linked worktree-hygiene, registry,
evaluability, obsolete-artifact, bridge-authority, project-linkage, and
spec-derived-verification requirements fully govern this bounded correction.
The owner decision narrows the authorized mutations and does not create a new
general Git-cleanup policy.

## Spec-Derived Verification Plan

| Governing surface | Required verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Before apply, the fresh Git dry-run must exactly match the 37-line/2,921-byte/SHA-256 baseline. After apply, the same dry run must be empty. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `gt registry show`, `sync`, `diff`, and `validate` must show the corrected existing path, complete TOML/MemBase parity, and no active-path defect. Registry-focused tests must pass. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Any dry-run, hunk, projection, baseline, target, or quiescence drift must stop before mutation. Before/after ref, stash, object, and reflog digests must be identical. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | The implementation report must enumerate removed worktree record names and preserve the malformed duplicate reflog files for a later exact disposition. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Independent GO, work-intent claim, implementation-start packet, and post-implementation independent verdict must cover the four target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The verdict must inspect command evidence and confirm every invariant in this table rather than relying on a generic test count. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/gt.exe registry show project-resource-alias-registry --json
groundtruth-kb/.venv/Scripts/gt.exe registry sync --json
groundtruth-kb/.venv/Scripts/gt.exe registry diff --json
groundtruth-kb/.venv/Scripts/gt.exe registry validate --json
git worktree prune --dry-run --verbose --expire now
git worktree prune --verbose --expire now
git worktree prune --dry-run --verbose --expire now
groundtruth-kb/.venv/Scripts/gt.exe hygiene reclaim plan --json
groundtruth-kb/.venv/Scripts/gt.exe hygiene reclaim history --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_registry_schema_and_ci.py groundtruth-kb/tests/test_registry_drift_detection.py platform_tests/scripts/test_check_sot_registry_completeness.py -q --tb=short
git diff --check -- config/registry/sot-artifacts.toml
```

The pre/post invariant collector is read-only and emits only compact counts and
hashes. It is evidence, not a second cleanup implementation.

## Acceptance Criteria

1. The TOML diff changes only the `project-resource-alias-registry`
   `storage_path` to `config/agent-control/project-resource-aliases.toml`.
2. Canonical registry sync completes; registry diff and validation pass with
   complete projection parity and no missing active alias-registry path.
3. The fresh worktree dry run exactly matches the authorized 37-entry digest
   before apply; the post-apply dry run is empty.
4. Ref, stash, loose-object inventory, and reflog byte digests are unchanged;
   no branch, ref, stash, object, or reflog content is mutated.
5. A fresh reclaim plan and history record the repaired registry and worktree
   readiness without suppressing the three malformed duplicate reflog files.
6. Focused tests, applicability, clause, target-coverage, and diff checks pass.
7. No live trash/restore, permanent purge, commit, push, release, deployment,
   credential operation, dispatcher mutation, or external mutation occurs.

## Risk / Rollback

The registry risk is accidental collateral change in a heavily dirty shared
file or projection. Exact before/after hunk review, canonical sync, parity
validation, and focused tests bound that risk. Rollback restores only the prior
single `storage_path` value and reruns canonical sync; unrelated dirty bytes
must remain untouched.

Worktree-prune risk is selection drift. The operation therefore requires an
exact fresh dry-run digest and stops on any difference. Git cannot reconstruct
already-orphaned administrative directories after pruning, but every selected
record points to an absent gitdir and carries no live checkout. Ref, stash,
object, and reflog invariants prove no repository history or recoverable object
is changed. Commit-based rollback is intentionally unavailable because this
authorization forbids commits.

## Bridge Filing

This proposal is filed under `bridge/` as the next versioned bridge file for
`gtkb-wi5142-bounded-readiness-repair`; no prior version is deleted or
rewritten. Dispatcher/TAFE state plus the append-only numbered file chain are
the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(hygiene):` if a later authorization permits committing the isolated
registry correction. This authorization itself permits no commit.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
