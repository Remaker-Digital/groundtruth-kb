NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript role ::init gtkb pb; owner-directed repo-wide finalization repair
author_metadata_source: explicit current Codex session metadata and transcript role declaration

# Implementation Proposal - WI-5370 auto-finalize active index containment

bridge_kind: prime_proposal
Document: gtkb-wi5370-auto-finalize-active-index-containment
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: [".git/index", "scripts/auto_finalize_sweep.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", ".claude/rules/auto-finalization-sweep.md", "independent-progress-assessments/WI-5370-auto-finalize-active-index-containment-manifest.json"]

implementation_scope: active auto-finalize process containment, exact staged-index neutralization, and durable clean-index guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Contain the live auto-finalization sweep process that is repeatedly staging unrelated terminal `VERIFIED` bridge verdicts and holding `.git/index.lock`, then add a clean-index guard so future Stop-hook sweeps refuse to stage or commit when any unrelated path is already staged.

This is a follow-on to `gtkb-wi5370-auto-finalize-sweep-invalid-body-guard`, whose implementation report is currently awaiting Loyal Opposition verification. The live process started before that thread was verified and has demonstrated a remaining failure mode: even with canonical verdict-body validation, the sweep can enter pathspec-limited `git commit` attempts while the shared index already contains unrelated staged verdicts. Failed commits then rotate staged bridge files through the index and block normal per-thread finalization repair.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-WORK-TREE-HYGIENE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` already require preserving per-thread provenance, refusing broad commits, and repairing governance automation without collapsing multiple WI threads into one commit.

## Current Evidence

- Live process `pythonw "E:\GT-KB/scripts/auto_finalize_sweep.py"` PID `31224` has been running since 2026-07-16 17:02:31 local time.
- Its child `git commit` processes held `.git/index.lock` during failed pathspec commits for `gtkb-wi5254-pauth-amendment-packet-preflight-008.md` and `gtkb-wi5316-frozen-modernization-rc-contract-008.md`.
- `.gtkb-state/auto-finalize-sweep/sweep.jsonl` records repeated `commit blocked/failed` events for eligible bridge-only verdicts, including `gtkb-wi5249-prime-no-action-claim-filer` and `gtkb-wi5254-pauth-amendment-packet-preflight`.
- The staged index has rotated through unrelated terminal verdicts and currently includes `bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md` and `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md`.
- The prior `gtkb-wi5370-mixed-staged-index-neutralization` repair is terminal VERIFIED but was a no-op at its execution time; it does not authorize a new staged-index mutation after fresh auto-sweep contamination.

## Proposed Repair Steps

1. After independent `GO`, acquire a work-intent claim for `gtkb-wi5370-auto-finalize-active-index-containment`.
2. Reconfirm the live auto-finalization sweep process tree, including parent process, command line, and any child `git.exe` process holding `.git/index.lock`.
3. Stop only the confirmed `auto_finalize_sweep.py` process tree and record PID/command-line evidence in the manifest. Do not stop dispatcher workers, reviewer workers, editor Git status readers, or unrelated harness processes.
4. Wait until `.git/index.lock` is absent. If the lock remains after the process tree is stopped, record STOP evidence and do not delete the lock file unless a child process absence check proves it is stale.
5. Snapshot the current staged path list using a NUL-delimited pathspec file under ignored runtime state. Require every staged path to be a bridge verdict file that the active auto-sweep staged. If unrelated source, test, database, config, harness-state, or non-bridge paths are staged, STOP without unstage.
6. Compute pre-run worktree-content digests for the staged paths.
7. Run `git restore --staged --pathspec-from-file=<snapshot> --pathspec-file-nul` for exactly the captured staged paths. Do not use `git restore --staged .`, `git reset --hard`, `git checkout --`, `git clean`, `git add -A`, `git commit`, or `git reset` on broad pathspecs.
8. Compute post-run worktree-content digests for the same paths and require equality with the pre-run digest.
9. Patch `scripts/auto_finalize_sweep.py` so `sweep()` exits before any staging/commit attempt whenever `git diff --cached --name-only` is non-empty, audit-logging `dirty_index_preexisting` with the staged count and first few paths.
10. Patch `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` with a regression proving a pre-existing staged path makes the sweep skip without calling commit or staging another verdict.
11. Update `.claude/rules/auto-finalization-sweep.md` to state the clean-index precondition and the process-containment runbook consequence for a stuck sweep.
12. Run the focused pytest, ruff lint, ruff format, live dry-run, and per-thread finalization planner. File an implementation report. Do not commit as part of this repair.

## Out of Scope

- No broad commit, sweep commit, push, release, deployment, or dispatcher-state mutation.
- No finalization of any terminal `VERIFIED` thread.
- No source/test/config/database/harness-state mutation outside the three auto-finalization files listed in `target_paths`.
- No deletion of bridge verdict files.
- No unstaging of source, test, database, config, harness-state, or non-bridge paths.
- No mutation of the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - resolved precedent: classify and preserve per-thread ownership instead of bulk-committing mixed bridge/source sprawl.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current planner/runbook precedent for one-thread-at-a-time finalization repair.
- `bridge/gtkb-wi5370-mixed-staged-index-neutralization-001.md` through `-005.md` - exact staged-index neutralization precedent; terminal report showed the earlier run was a no-op.
- `bridge/gtkb-wi5370-auto-finalize-sweep-invalid-body-guard-001.md` through `-003.md` - immediate predecessor hardening; current live process proves a separate clean-index guard is needed.
- `docs/procedures/per-thread-finalization-repair.md` - live runbook requiring STOP on mixed provenance.
- `.claude/rules/auto-finalization-sweep.md` - existing sweep contract and disable mechanism.

## Owner Decisions / Input

- Owner directive in Codex task `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: keep working until the repo-wide uncommitted-file sprawl problem is resolved.
- Owner correction in the same task: role authority is transcript-defined for this interactive Prime Builder session and is not derived from `gt harness roles`. This proposal relies on the transcript `::init gtkb pb` role declaration for Prime status authority.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Manifest records stopped process evidence, staged path snapshot hash, pre/post worktree digest equality, and final staged path state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain shows NEW -> GO -> implementation report -> LO verdict; Prime does not author GO/NO-GO/VERIFIED. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Exact staged bridge verdicts are recorded and neutralized without committing them or attributing them to this repair. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests and live dry-run prove the sweep skips when the index is dirty before any staging/commit side effect. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal cites governing specs and maps them to concrete tests/evidence. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Work begins only after GO and implementation-start authorization; report records claim/session evidence. |

## Acceptance Criteria

- The live auto-finalization sweep process tree is stopped only if it still matches the exact `auto_finalize_sweep.py` command line.
- `.git/index.lock` is not deleted while a live Git writer exists.
- Only captured staged bridge verdict paths are unstaged; no working-tree bytes change.
- `git diff --cached --name-only` is empty after neutralization, unless the manifest records a concurrent-writer STOP.
- Future `sweep()` runs audit-log and return without staging or committing when the index is pre-existing dirty.
- Focused pytest, ruff lint, ruff format, live dry-run, and per-thread finalization planner are recorded in the implementation report.

## Files Expected To Change

- `.git/index`
- `scripts/auto_finalize_sweep.py`
- `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`
- `.claude/rules/auto-finalization-sweep.md`
- `independent-progress-assessments/WI-5370-auto-finalize-active-index-containment-manifest.json`

## Recommended Commit Type

`fix`
