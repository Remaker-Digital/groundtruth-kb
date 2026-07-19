NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning=xhigh; sandbox=none
author_metadata_source: codex-desktop-runtime

Document: gtkb-wi5546-read-only-git-probes-clean-slice
bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5546
target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py","groundtruth-kb/src/groundtruth_kb/project/upgrade.py","groundtruth-kb/src/groundtruth_kb/project/rollback.py","groundtruth-kb/src/groundtruth_kb/hygiene/strays.py","groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py","groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py","scripts/check_modernization_release_candidate.py","scripts/check_document_author_metadata.py","scripts/gtkb_dashboard/refresh_dashboard_db.py","scripts/per_thread_finalization_repair.py","scripts/implementation_authorization.py","scripts/release_candidate_gate.py","scripts/session_self_initialization.py","scripts/wrap_capture_transcript.py","scripts/wrap_scan_hygiene.py","scripts/wrap_scan_cross_artifact_drift.py","groundtruth-kb/tests/test_rollback_receipts.py","groundtruth-kb/tests/test_upgrade_rollback.py","platform_tests/scripts/test_fab13_retention_policy.py","platform_tests/scripts/test_hygiene_strays_cli.py","platform_tests/scripts/test_per_thread_finalization_repair.py","platform_tests/scripts/test_release_candidate_gate.py","platform_tests/scripts/test_read_only_git_no_optional_locks.py"]
Requirement Sufficiency: SUFFICIENT

# WI-5546 Read-Only Git Probes Clean-Target Implementation Proposal

## Summary

Make the currently clean repository-owned read-only Git status probes non-locking by using Git's native global `--no-optional-locks` option. Preserve porcelain output, exit/error behavior, Windows no-console behavior, dispatcher eligibility, harness availability, and every mutating Git command.

Live reproduction on 2026-07-18 showed a zero-byte `.git/index.lock` created by a read-only `gt spec show` path. The lock was exclusively openable after the probe exited, and no live Git process owned it. This is direct evidence that an optional index refresh can leave repository-wide lock residue during concurrent work.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-WORK-TREE-HYGIENE-001` already requires live, report-first, non-mutating worktree inspection. WI-5546 narrows that contract to the observed Git optional-lock mechanism without changing the governed behavior, authority model, or acceptance outcome. No new or revised requirement is needed before implementation.

## Bridge Authority

This NEW proposal is filed as the next numbered versioned bridge file, `bridge/gtkb-wi5546-read-only-git-probes-clean-slice-001.md`, through the governed append-only writer. No prior bridge version is deleted or rewritten. Protected implementation remains forbidden until an independent GO and matching governed claim/start authority exist.

## Scope

1. Prefix only the listed read-only `status` invocations with Git's global `--no-optional-locks` option.
2. Where a module-local helper executes only read-only Git commands, the option may be added inside that helper. Where a helper also executes mutating Git, add the option only at the read-only call site.
3. Preserve every status option, pathspec, timeout, encoding, no-window flag, return-code policy, and parser byte-for-byte except for the new global option.
4. Add deterministic command-shape and output-parity coverage.

## Explicit Exclusions

The following currently dirty files contain relevant probes but are foreign to this clean-target slice and must not be edited, staged, finalized, or cited as implementation evidence here:

- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `scripts/auto_finalize_sweep.py`
- `scripts/bridge_verified_backlog_reconciler.py`

Their eventual WI-5546 additions require a later hunk-scoped slice after their owning work is stabilized. This proposal also excludes dispatcher configuration, harness configuration, process termination or suspension, database mutation, credentials, deployment, and any bridge artifact other than this thread's governed lifecycle.

## Requirements

- Every in-scope read-only `git status` probe must run with optional locks disabled.
- No mutating Git command may acquire the option by helper-wide accident.
- Existing status output and fail-closed behavior must remain unchanged.
- Windows subprocess containment must remain intact.
- No harness may be disabled, deprioritized, suspended, or made ineligible.
- Implementation must preserve all pre-start worktree bytes outside exact reviewed hunks.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`: live worktree inspection is report-first and non-mutating; the implementation must not introduce cleanup or process control.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: protected implementation starts only after an independent GO and matching governed claim/start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this proposal names every mechanically applicable specification and maps each operative requirement to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: post-implementation verification must execute the specification-derived plan and independently assess the resulting evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: this platform-only slice does not move adopter/application content or change platform/application placement boundaries.

## Prior Deliberations

_No prior deliberations: WI-5546 is a bounded implementation of a directly reproduced optional-lock defect under the existing work-tree hygiene governance contract._

## Implementation Plan

1. Revalidate every target preimage immediately before editing and stop on new foreign dirt.
2. Add `--no-optional-locks` before `status` in each in-scope command, using the narrowest local helper or call-site edit.
3. Update only command-shape tests whose exact expected argument list changes.
4. Add one focused static/behavioral regression test that inventories the in-scope probes, rejects unguarded status commands, compares guarded and ordinary porcelain output in a temporary repository, and confirms representative mutating command shapes remain unchanged.
5. Run focused tests, Ruff, whitespace checks, and a lock-residue integration probe.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Report-only live status inspection does not perform optional index writes | Focused test rejects every in-scope status command lacking `--no-optional-locks`; integration probe asserts no `.git/index.lock` remains after repeated status reads. |
| Status semantics are preserved | Temporary-repository test compares ordinary and guarded porcelain output for clean, modified, staged, and untracked states. |
| Mutating Git is unaffected | Command-capture tests assert upgrade/finalization mutation commands retain their prior argument shape and do not inherit the flag. |
| Harnesses and dispatcher remain fully available | Diff inspection confirms no dispatcher configuration, registry, eligibility, harness launcher, or process-control target changes. |
| Foreign work is preserved | Preimage/status evidence and final diff prove only reviewed hunks in the declared clean target paths changed. |

Required implementation verification:

- Focused pytest targets covering all changed modules.
- `groundtruth-kb/.venv/Scripts/ruff.exe check` for changed Python files.
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check` for changed Python files.
- `git diff --check` with optional locks disabled.
- Independent Loyal Opposition post-implementation review and `VERIFIED`.

## Risks and Rollback

The option suppresses optional repository-changing refreshes; it does not suppress worktree or index comparison. The principal regression risk is accidentally applying it to a helper that later performs a mutating command. Command-capture tests and call-site-level scoping contain that risk.

Rollback is the exact inverse hunk for the added global option and corresponding test expectations. It must not restore, rewrite, or discard any foreign working-tree bytes.

## Commit Finalization

After independent `VERIFIED`, finalization must use the same transaction path set consisting only of the actually changed declared target paths plus the terminal verdict:

- Finalization paths: exact changed paths from `target_paths` and this thread's terminal `VERIFIED` bridge file only.
- Dirty target files outside this proposal remain excluded.
- No whole-file finalization is permitted for a path that acquired foreign changes after proposal filing.
- No staging, commit, push, clean, release, or deploy occurs before exact mechanical authority.

Recommended commit subject: `fix(git): make read-only status probes non-locking`
