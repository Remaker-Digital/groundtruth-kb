NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - gtkb-sweep-commit commits in-flight (un-VERIFIED) bridge work, bypassing the VERIFIED finalization gate

bridge_kind: prime_proposal
Document: gtkb-gtkb-sweep-commit-skill-respects-verified-gate
Version: 001
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4710

target_paths: ["scripts/sweep_commit_helpers.py", "platform_tests/scripts/test_sweep_commit_helpers.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The `gtkb-sweep-commit` skill performs a whole-worktree `git add -A` sweep and its deterministic batch-planner `scripts/sweep_commit_helpers.py` co-stages protected files (`.claude/hooks/**`, `.codex/hooks.json`, `.githooks/**`, and — via the narrative-artifact-evidence path — protected `.claude/rules/*.md` / `CLAUDE.md` / `AGENTS.md` narrative files) with any *present* numbered bridge evidence file, WITHOUT checking whether that file's bridge thread has reached `VERIFIED`. The planner's `plan_commit_batches` treats a path as commit-ready as soon as a citing bridge file (or `bridge/INDEX.md`) is co-staged (`kind="protected-with-evidence"`); it never reads the thread's latest status token. A sweep therefore commits protected rule files plus the in-flight implementation *report* of an un-VERIFIED bridge thread, which makes the mandatory same-commit `VERIFIED` finalization (per `GOV-FILE-BRIDGE-AUTHORITY-001` Mandatory VERIFIED Commit-Finalization Gate) impossible after the fact and forces an owner-waiver recovery.

## Defect / Reproduction

Observed incident (origin of WI-4710): a generic worktree sweep, commit `9759c5cd9` ("chore: sweep accumulated multi-session work"), committed WI-4682's two protected rule files together with the `-015` implementation report BEFORE Loyal Opposition recorded `VERIFIED` on that thread. Because the verified work was already in history under a non-finalization commit, the same-commit `VERIFIED` finalization the gate requires could no longer be produced, and recovery required an owner waiver (`DELIB-S20260620-WI4682-SWEEP-FINALIZATION-WAIVER`, captured at `bridge/gtkb-wi4682-automation-value-cost-principle-017.md`).

Reproduction (logical): stage a protected file (e.g. `.claude/hooks/foo.py`, or a protected narrative `.claude/rules/bar.md` whose narrative-artifact approval packet is present) together with the in-flight bridge file of a thread whose latest status token is `NEW` or `REVISED` (i.e. not `VERIFIED`). Call `plan_commit_batches(staged, project_root)`. Current behavior: the planner emits a `protected-with-evidence` batch and reports the commit as gate-acceptable, so the orchestrating skill commits the protected path. Expected: the planner recognizes that the only co-staged "evidence" belongs to an un-VERIFIED thread and surfaces a new block-or-exclude batch kind (`protected-unverified-thread`) whose rationale instructs the skill to exclude the protected path from the sweep until the thread is `VERIFIED`, so in-flight bridge work cannot be prematurely finalized outside the VERIFIED gate.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/sweep_commit_helpers.py`, `platform_tests/scripts/test_sweep_commit_helpers.py`. The fix reuses the in-root bridge status reader `groundtruth_kb.bridge.versioned_files.status_from_bridge_file` / `scan_expected_documents`; no path outside the root is read or required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the bridge protocol and the Mandatory VERIFIED Commit-Finalization Gate; the defect lets a sweep commit verified-pending protected work outside that gate. The fix reads the authoritative bridge `VERIFIED` signal before allowing a protected path tied to that thread into a sweep.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - completion/finalization is an artifact-lifecycle transition; the fix keeps the sweep's commit decision consistent with the durable bridge verification artifact rather than mere file presence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from the cited specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - the recovery path for the original incident required an owner AUQ waiver; the fix removes the need for that owner-decision detour by preventing the premature commit deterministically, keeping owner-decision load down per the GT-KB vision filter.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to GT-KB platform tooling (`scripts/sweep_commit_helpers.py`) and platform tests; no application-placement boundary is crossed and no adopter/application surface is touched.
- `GOV-STANDING-BACKLOG-001` - WI-4710 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the protected paths most affected are the cross-harness hook configs (`.codex/hooks.json`, `.claude/hooks/**`); the fix preserves their parity-gated co-staging contract while adding the VERIFIED gate, so harness-parity behavior is unchanged.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the commit decision remains backed by the bridge artifact's verification state rather than inferred from presence of any numbered file.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the sweep's commit trigger with the bridge `VERIFIED` lifecycle state that should gate finalization of protected bridge work.

## Prior Deliberations

- `DELIB-S20260620-WI4682-SWEEP-FINALIZATION-WAIVER` - Owner waiver recovering the exact WI-4682 incident this defect describes (sweep committed protected rule files + `-015` report before VERIFIED); the waiver is the cost this fix exists to prevent recurring.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - Owner directive that VERIFIED commit-finalization is mandatory and same-commit; the defect makes that directive unsatisfiable when a sweep front-runs verification.
- `DELIB-20265510` - Owner waiver finalizing WI-4681 VERIFIED by reference to commit `9759c5cd9` (the same sweep commit), narrowly waiving same-commit finalization — additional evidence of the recovery burden caused by sweeping in-flight bridge work.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-4710 (P2) is in scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4710 is origin=defect, single-concern, introduces no new public API/CLI surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items, pipeline-repair and P1/P2 first; WI-4710 is P2.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing reliability fast-lane authorization (surfaced via PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) under which small single-concern defect fixes proceed through the bridge protocol without a fresh per-item owner approval.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (Mandatory VERIFIED Commit-Finalization Gate) already establishes that protected verified bridge work must be finalized in the same commit as its `VERIFIED` verdict; this fix enforces that existing contract at the sweep-commit boundary by withholding protected paths tied to an un-VERIFIED bridge thread. No new or revised requirement/specification is introduced.

## Proposed Scope

1. In `scripts/sweep_commit_helpers.py`, add a deterministic, read-only thread-verification check used by `plan_commit_batches`:
   - Reuse the in-root bridge status reader `groundtruth_kb.bridge.versioned_files.scan_expected_documents` (and `status_from_bridge_file`) to map each co-staged bridge-evidence file to its thread slug and the thread's current latest status token. The module already inspects bridge file bodies, so this stays pure planning: no git invocation, no file mutation, no bridge/KB writes.
   - When a protected path's only citing bridge evidence belongs to a thread whose latest status is NOT `VERIFIED` (i.e. `NEW`/`REVISED`/no terminal token), emit the protected path in a NEW batch `kind="protected-unverified-thread"` whose rationale instructs the orchestrator to EXCLUDE that protected path from the sweep until the thread reaches `VERIFIED` (so the protected work can be finalized in the same commit as its VERIFIED verdict). The path is withheld, not silently committed.
   - Preserve the existing `protected-with-evidence` outcome ONLY when the citing thread is `VERIFIED` (or the universal `bridge/INDEX.md` co-stage continues to satisfy presence but the per-protected thread-status gate is the controlling condition for protected paths that map to a specific in-flight thread).
   - Keep fail-soft posture: if a bridge thread's status cannot be read, treat it conservatively as not-VERIFIED (withhold), never raise.
2. Update the `gtkb-sweep-commit` SKILL.md narrative ONLY if required to describe the new `protected-unverified-thread` exclusion — but per fast-lane scope the SKILL.md (a protected narrative) is NOT in `target_paths`; the deterministic planner is the controlling surface and the skill consumes its plan, so the source+test change is sufficient for the defect removal. (Any SKILL.md wording change would be a separate protected-narrative packet and is explicitly out of scope here.)
3. Add regression tests in `platform_tests/scripts/test_sweep_commit_helpers.py` (see verification plan), including a synthetic replay of the WI-4682 incident shape (protected rule/hook path + un-VERIFIED report co-staged).

This is the defect-removal path. The WI's noted alternative (modeling/displaying that automatic sweep commits may precede report verification) is a behavior/contract change requiring a new requirement and is explicitly out of scope for this fast-lane defect fix.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (VERIFIED finalization gate; protected bridge work not committed pre-VERIFIED) | `test_protected_path_with_unverified_thread_is_withheld` | A protected path co-staged only with a bridge file whose thread latest status is `NEW` produces a `protected-unverified-thread` batch and NO `protected-with-evidence` batch for that path. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no false-negative regression) | `test_protected_path_with_verified_thread_is_committed` | The same protected path IS placed in a `protected-with-evidence` batch once its citing thread's latest status is `VERIFIED`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (gate aligned to lifecycle state) | `test_unverified_thread_batch_rationale_instructs_exclusion` | The `protected-unverified-thread` batch rationale names the protected path and instructs exclusion-until-VERIFIED (deterministic diagnostic). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (artifact-backed, fail-soft) | `test_unreadable_thread_status_treated_as_unverified` | When a citing bridge thread's status cannot be read, the protected path is withheld (conservative), and the planner does not raise. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (WI-4682 incident regression) | `test_wi4682_incident_replay_withholds_protected_rule_files` | Replaying the incident shape (protected rule/hook path + un-VERIFIED implementation report co-staged) withholds the protected path rather than emitting an acceptable commit batch. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (non-protected paths unaffected) | `test_non_protected_paths_unaffected_by_thread_gate` | Non-protected source/test/doc paths remain in an `unconstrained` batch regardless of any co-staged thread's status (gate does not over-reach). |

Execution commands:
- `python -m pytest platform_tests/scripts/test_sweep_commit_helpers.py -q --tb=short`
- `python -m ruff check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py`
- `python -m ruff format --check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py`

## Acceptance Criteria

1. `plan_commit_batches` withholds (via a `protected-unverified-thread` batch) any protected path whose only co-staged bridge evidence belongs to a thread whose latest status is not `VERIFIED`.
2. A protected path tied to a `VERIFIED` thread continues to be committable (`protected-with-evidence`), and non-protected paths are unaffected (no regression).
3. Thread-status reads are fail-soft (unreadable status -> withhold, never raise).
4. All six derived tests pass; `ruff check` and `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: over-tightening could withhold a protected path whose thread is legitimately complete but whose status the reader cannot resolve. Mitigation: the WI-4682 cost of premature finalization (owner waiver) is strictly worse than a conservatively-withheld path the owner can re-sweep after VERIFIED; the withhold is reversible within the same session.
- Risk: a protected path co-staged with `bridge/INDEX.md` only (no thread mapping). Mitigation: INDEX co-staging still satisfies presence, but a protected path that ALSO maps to a specific in-flight thread is gated on that thread's status; the conservative posture withholds when any mapped thread is non-VERIFIED.
- Risk: coupling the planner to `groundtruth_kb.bridge.versioned_files`. Mitigation: that is an existing in-root reader already used by other bridge tooling; the import is read-only and the planner degrades fail-soft if the reader is unavailable.
- Rollback: revert the predicate/batch-kind addition in `sweep_commit_helpers.py`; the change is additive (one new batch kind + one guarded condition) plus tests, fully reversible with no migration.

## Files Expected To Change

- `scripts/sweep_commit_helpers.py`
- `platform_tests/scripts/test_sweep_commit_helpers.py`

## Recommended Commit Type

`fix`
