REVISED

# GT-KB WI-5142 Registry Reality Readiness Repair

bridge_kind: prime_proposal
Document: gtkb-wi5142-bounded-readiness-repair
Version: 003
Responds to: gtkb-wi5142-bounded-readiness-repair-002 (NO-GO)
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

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth.db", ".gtkb-state/hygiene-reclaim/runs/"]

implementation_scope: configuration | governance-projection | runtime-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Narrow the rejected combined proposal to the independently confirmed,
executable registry-reality correction only. Change the active
`project-resource-alias-registry` record from the nonexistent
`.claude/rules/project-resource-aliases.toml` path to the existing canonical
`config/agent-control/project-resource-aliases.toml`, synchronize the MemBase
projection through `gt registry sync`, validate complete parity, and create a
fresh compact reclaim plan under `E:/GT-KB`.

This revision accepts every finding in NO-GO 002. It removes `.git/worktrees/`
and every test file from `target_paths`; removes all `git worktree` commands;
and cites the prior stale-worktree diagnosis. No Git lifecycle operation,
worktree metadata mutation, reflog mutation, ref/branch/stash update, Git object
mutation, reclaim trash/restore, permanent purge, commit, push, release,
deployment, credential operation, dispatcher mutation, or external mutation is
authorized. Orphaned-worktree cleanup will proceed only through a separately
reviewed canonical Git-lifecycle extension, never a direct-command bypass.

## NO-GO 002 Disposition

- **F1 resolved:** the worktree half is removed in full. This revision invokes
  no direct `git worktree` command and does not list `.git/worktrees/` as a
  target. A separate proposal must add a sanctioned lifecycle operation before
  those records can be changed.
- **F2 resolved:** `DELIB-20266050` and its VERIFIED predecessor thread are
  cited below. The deferred cleanup remains deferred; this registry-only repair
  does not claim to discharge it.
- **F3 resolved:** the four read-only test files are removed from
  `target_paths`, and no test-file edit is proposed. Production registry
  commands and exact before/after evidence provide the verification surface.

## Existing Capability Reuse

- Use `gt registry show`, `gt registry sync`, `gt registry diff`, and
  `gt registry validate`; do not edit the MemBase projection directly.
- Use `gt hygiene reclaim plan --json` and `history --json`; do not create a
  private cleanup script, queue, registry, or history index.
- Preserve the heavily dirty file and database hunk-by-hunk. Only the named
  registry record may change in TOML, and canonical sync must report only that
  one projection ID as updated.
- Treat the GTKB-GIT-LIFECYCLE gate as authoritative. This revision has no Git
  writer and needs no exemption.

## Exact Bounded Procedure

1. Record the registry TOML SHA-256, parsed 47-record inventory, current
   `project-resource-alias-registry` record, and `gt registry diff` result.
2. Reconfirm that `.claude/rules/project-resource-aliases.toml` is absent and
   `config/agent-control/project-resource-aliases.toml` is a regular in-root
   file. Stop on any drift.
3. Change only that record's `storage_path` value. Compare the before/after
   bytes and require exactly one replaced line with every other byte preserved.
4. Run `gt registry sync` with WI-5142 and the owner-decision ID in its change
   reason. Require `inserted = []`, `updated =
   ["project-resource-alias-registry"]`, and 46 unchanged IDs. Any broader
   projection result is a refusal.
5. Require `gt registry diff --json` and `gt registry validate --json` to report
   complete TOML/MemBase parity and no missing active alias-registry path.
6. Run a fresh compact `gt hygiene reclaim plan --json` and verify its history.
   The prior `registry_reality_missing_active_file` blocker must be absent.
   Existing Git/worktree/reflog blockers remain visible and non-executable;
   this revision neither suppresses nor repairs them.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - requires report-first hygiene, fresh evidence,
  deterministic selection, and fail-closed behavior; this slice removes one
  registry blocker without performing cleanup.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the typed TOML registry canonical and
  MemBase a synchronized projection; direct projection edits are prohibited.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires fail-closed
  handling of stale, contradictory, incomplete, or over-broad evidence.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - requires explicit disposition
  and preservation of unresolved obsolete artifacts rather than silent purge.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO and an active claim
  before protected configuration or database mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to
  the active project authorization and WI-5142.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - links the exact
  correction to governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  verification of the requirement-derived invariants below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the decision, revision,
  projection evidence, and deferred Git-lifecycle work as durable records.

## Prior Deliberations

- `DELIB-20260716-WI5142-BOUNDED-READINESS-REPAIR` - owner approval for the
  bounded registry correction, conditional Git readiness work, and fresh plan.
  This revision exercises only the registry portion.
- `DELIB-20266050` / VERIFIED thread
  `gtkb-stale-git-worktree-autogc-diagnosis` - the direct predecessor diagnosed
  stale worktrees read-only and explicitly deferred `git worktree prune` to a
  later destructive-cleanup proposal. This revision preserves that deferral;
  the separate lifecycle-extension thread must discharge it.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-GIT-READINESS-ASSESSMENT` - records
  that Git-lifecycle modernization is not ready, reinforcing the split.
- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` - requires
  deterministic classification, audit history, bounded cleanup, and no
  unbounded purge.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - established
  registry-first preservation after essential local artifact loss.
- Bridge versions 001-002 - combined proposal and the independent NO-GO that
  identified the missing canonical worktree-prune execution route.

## Owner Decisions / Input

Owner approval is recorded as
`DELIB-20260716-WI5142-BOUNDED-READINESS-REPAIR` and bound to active
authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI5142-BOUNDED-READINESS-REPAIR-20260716`.
The registry correction is explicitly included. Narrowing away the blocked Git
half requires no additional owner decision and reduces mutation scope.

No later live trash, malformed-Git repair, or worktree mutation is inferred
from this approval. Each remains separately bridge- and owner-gated.

## Requirement Sufficiency

Existing requirements sufficient. The linked registry-authority, hygiene,
evaluability, artifact-lifecycle, bridge-authority, project-linkage, and
spec-derived-verification requirements fully govern this single-record
correction. No new requirement or Git-lifecycle exception is needed for this
registry-only slice.

## Specification-Derived Verification Plan

| Governing surface | Required verification |
| --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Before/after evidence must show exactly one TOML line replacement; canonical sync must update exactly `project-resource-alias-registry`; `diff` and `validate` must pass for all 47 records. |
| `GOV-WORK-TREE-HYGIENE-001` | A fresh plan must remove only the registry-reality blocker while retaining unresolved Git blockers and remaining non-executable. No cleanup actuator runs. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Any path, record-count, hunk, projection, parity, or plan drift must stop the operation. Unrelated dirty bytes must be identical before/after. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | The implementation report must preserve the 37 stale worktree records and three malformed reflog copies as explicitly deferred, unchanged artifacts. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Independent GO, work-intent claim, implementation-start packet, and post-implementation verdict must cover the three target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The verdict must inspect exact command evidence and each invariant in this table, not rely on a generic test count. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/gt.exe registry show project-resource-alias-registry --json
groundtruth-kb/.venv/Scripts/gt.exe registry sync --changed-by prime-builder/codex/A --change-reason <governed-reason> --json
groundtruth-kb/.venv/Scripts/gt.exe registry diff --json
groundtruth-kb/.venv/Scripts/gt.exe registry validate --json
groundtruth-kb/.venv/Scripts/gt.exe hygiene reclaim plan --json
groundtruth-kb/.venv/Scripts/gt.exe hygiene reclaim history --run-id <fresh-run-id> --json
git diff --check -- config/registry/sot-artifacts.toml
```

The production registry and reclaim interfaces are the test surface. No test
file is edited, and no direct Git lifecycle command is invoked.

## Acceptance Criteria

1. The TOML change replaces only the `project-resource-alias-registry`
   `storage_path` with `config/agent-control/project-resource-aliases.toml`.
2. Canonical registry sync reports zero inserts, exactly that one updated ID,
   and 46 unchanged IDs; registry diff and validation pass for all 47 records.
3. A fresh reclaim plan contains no
   `registry_reality_missing_active_file` blocker for the alias registry and
   preserves every unresolved Git blocker without becoming executable.
4. The 37 worktree records, three malformed reflog files, refs, stashes, Git
   objects, tests, and every unrelated dirty byte remain unchanged.
5. Applicability, clause, target-coverage, and diff checks pass.
6. No Git lifecycle command, cleanup actuator, permanent purge, commit, push,
   release, deployment, credential operation, dispatcher mutation, or external
   mutation occurs.

## Risk / Rollback

The risk is collateral change in a heavily dirty shared TOML or MemBase file.
Exact byte comparison, typed parsing, one-ID sync expectations, parity
validation, and independent verification bound that risk. Rollback restores
only the prior single `storage_path` value and reruns canonical sync; unrelated
dirty bytes must remain untouched. Commit-based rollback is unavailable because
the authorization forbids commits.

## Bridge Filing

This revision is filed as the next versioned bridge file
`bridge/gtkb-wi5142-bounded-readiness-repair-003.md`; versions 001 and 002 are
preserved unchanged. Dispatcher/TAFE state plus the append-only numbered file
chain remain canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(hygiene):` if a later authorization permits committing the isolated
registry correction. This authorization itself permits no commit.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
