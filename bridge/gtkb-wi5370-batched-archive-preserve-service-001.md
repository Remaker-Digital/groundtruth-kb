NEW

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 6011eeb9-dc03-47aa-9b8b-ab1ee2ca13f1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Batched Archive-Preserve Service (Slice 2)

bridge_kind: prime_proposal
Document: gtkb-wi5370-batched-archive-preserve-service
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
target_paths: ["scripts/batch_archive_terminal_verdicts.py", "platform_tests/scripts/test_batch_archive_terminal_verdicts.py"]
Recommended commit type: feat

## Summary

Implement the governed batch archive-preserve service that executes
`DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` (v1). The service drains
the untracked-terminal-verdict sprawl on the `research` working tree by
byte-preserving legacy non-finalizable terminal bridge verdicts to a tracked
in-root archive and removing the untracked sources, in one governed
pathspec-limited transaction per batch. It replaces the per-file reissue
treadmill for this candidate class.

This is Slice 2 of the batched archive-preserve method
(`DELIB-202666766`). Slice 1 (the DCL) is complete.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`,
`DELIB-202666766`, `GOV-FILE-BRIDGE-AUTHORITY-001`, and the active
tree-stabilization project authorization fully define this bounded service.
No new or revised requirement is needed before implementation.

## Specification Links

- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` (the executable contract)
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- WI-4871 (untracked-terminal-VERIFIED durability guard)

## Prior Deliberations

- `DELIB-202666766` - owner method decision (refine detector + bulk-archive).
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` - owner precedent
  preferring oracle refinement over mass file moves.
- `DELIB-20264762` - S373 Working-Tree Triage Umbrella NO-GO (staleness); this
  proposal derives its candidate set from live state, not a stale snapshot.
- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - precedent forbidding
  bulk commits of mixed bridge/source sprawl; this service is bridge-only.
- `bridge/gtkb-wi5370-auto-finalize-sweep-invalid-body-guard-003.md` - the
  complementary sweep hardening that skips invalid-body terminals; this service
  supplies their disposition.
- `bridge/gtkb-wi5370-auto-finalize-guard-invalid-terminal-reissue-003.md` - the
  per-file archive whose gitignored-archive-path defect this service fixes by
  archiving to a tracked path.

## Owner Decisions / Input

- `DELIB-202666766` (owner AUQ, 2026-07-17): selected the refine-detector +
  bulk-archive method over root-cause-commingling / fresh-umbrella /
  characterize-first.
- Owner AUQ (2026-07-17): approved creation of
  `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` v1.
- Owner AUQ (2026-07-17): selected the service risk posture "pilot first, then
  autonomous drain" - pathspec-limited commits, bounded first run (~20), validate,
  then scale.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` is the active
  owner-authorized project scope for WI-5370 tree-stabilization repairs.

## Proposed Scope

Implement `scripts/batch_archive_terminal_verdicts.py`, a read-then-transact
governed service:

1. **Enumerate** archive-preserve candidates per the DCL candidate class:
   untracked (`git ls-files --others --exclude-standard bridge`), first-line
   status token terminal, thread terminal in TAFE/dispatcher state, and
   non-finalizable-in-place (body fails `write_verdict.validate_verified_body()`
   or status is a non-finalizable terminal). Valid-bodied finalizable VERIFIED
   verdicts are excluded.
2. **Archive** each candidate: byte-exact copy to
   `archive/bridge-terminal-verdicts/<original-filename>`; verify length,
   SHA-256, and git blob equal; delete only the untracked source. Any mismatch
   aborts that candidate with the source left intact.
3. **Commit** the batch with a pathspec-limited commit
   (`git commit -- archive/bridge-terminal-verdicts/<committed-files>`) so the
   archive enters history AND the pre-staged `A bridge/gtkb-wi5318-...` entry and
   all commingled non-bridge changes are never captured.
4. **Bound** the run with `--limit N` (default a bounded pilot; `--all` for full
   drain after pilot validation), `--dry-run` (enumerate + report, no mutation),
   and an append-only audit log at `.gtkb-state/batch-archive/*.jsonl`.
5. **Fail closed** on byte mismatch, on any attempt to stage a non-bridge path,
   on `.git/index.lock` contention (timeout-bounded git subprocesses), or on a
   candidate whose thread is not TAFE-terminal.

## Out Of Scope

- No modification of live source, tests, rules, config, or the commingled
  finalizer-helper files.
- No touch of the pre-existing staged `A bridge/gtkb-wi5318-...` index entry.
- No reissue, no valid-bodied VERIFIED finalization (the sweep owns that).
- No dispatcher/TAFE/harness/registry mutation; no push/deploy.

## Specification-Derived Verification Plan

| Spec | Derived test / verification |
| --- | --- |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` candidate class | Test: enumeration selects only untracked + terminal-token + TAFE-terminal + non-finalizable; excludes valid-bodied VERIFIED. |
| DCL invariant 1 (tracked archive) | Test: archive target resolves under `archive/bridge-terminal-verdicts/` and `git check-ignore` reports NOT ignored. |
| DCL invariant 2 (byte identity) | Test: a byte-mismatch fixture aborts with source intact and no archive copy committed. |
| DCL invariant 3 (bridge-only, no staged-index touch) | Test: a batch run with a pre-staged foreign non-bridge index entry leaves that entry staged and uncommitted; commit contains only archive paths. |
| `GOV-WORK-TREE-HYGIENE-001` | Test: `--dry-run` mutates nothing; a real run reduces the untracked bridge count by exactly the committed set. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_batch_archive_terminal_verdicts.py -q`; `ruff check` and `ruff format --check` on both target files. |

## Acceptance Criteria

- The service enumerates the DCL candidate class correctly and excludes
  finalizable valid-bodied VERIFIED verdicts.
- Each archived verdict is byte-identical at the tracked archive path before its
  source is removed.
- The batch commit is pathspec-limited: it contains only
  `archive/bridge-terminal-verdicts/` paths and never the staged WI-5318 entry
  or any non-bridge change.
- `--dry-run` and `--limit` behave as specified; the audit log records every
  archive/skip/error.
- All derived tests pass; `ruff check` and `ruff format --check` are clean.

## Risk And Rollback

Risk is provenance- and tree-safety-sensitive: the service both deletes untracked
sources and creates git history. Mitigations: byte identity is verified before
every deletion; the commit is pathspec-limited; the first production run is a
bounded pilot (owner-selected posture). Rollback before commit is to restore the
archived bytes to the source path after revalidating the archive hash. Rollback
after commit is a `git revert` of the pathspec-limited archive commit, which
restores the archived files as tracked history (the bytes are never lost).
