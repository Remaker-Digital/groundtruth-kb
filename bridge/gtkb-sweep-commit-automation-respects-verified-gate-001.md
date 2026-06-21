NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Sweep-commit automation commits in-flight (un-VERIFIED) bridge work, bypassing the bridge VERIFIED finalization gate

bridge_kind: prime_proposal
Document: gtkb-sweep-commit-automation-respects-verified-gate
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4709

target_paths: ["scripts/sweep_commit_helpers.py", "platform_tests/scripts/test_sweep_commit_helpers.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The sweep-commit batch planner in `scripts/sweep_commit_helpers.py` decides which protected paths may be committed using only two predicates: (1) a co-staged numbered bridge-evidence file is present (`is_bridge_evidence_path` / `bridge_files_citing`), and (2) the narrative-artifact commit floor (a matching approval packet) passes elsewhere in the flow (`scripts/check_narrative_artifact_evidence.py`). Neither predicate checks whether the protected path is currently part of an *active, non-terminal* bridge thread (latest status `NEW`/`REVISED`/`GO`/`NO-GO`). As a result, the `gtkb-sweep-commit` skill, which executes the planned batches, commits protected files (e.g. `.claude/rules/*.md` narrative artifacts whose packets exist) while their addressing bridge thread is still un-VERIFIED. This bypasses the bridge protocol's Mandatory VERIFIED Commit-Finalization Gate (per `.claude/rules/file-bridge-protocol.md`) and desyncs committed worktree state from the bridge thread of record.

## Defect / Reproduction

Observed incident: commit `9759c5cd9` ("chore(gtkb): sweep accumulated multi-session work") committed WI-4682's protected-narrative rule-file changes (`.claude/rules/bridge-essential.md`, `.claude/rules/canonical-terminology.md`) into HEAD while the addressing bridge thread was still `REVISED@-015` (not `VERIFIED`). Commits `0f96c4e6e` and `13097296d` show the same recurring pattern, some originating from abandoned agent sessions. In each case the narrative-artifact commit floor passed because approval packets existed, and the inventory-drift co-stage check passed because a numbered bridge file was co-staged, yet the protected file belonged to a bridge thread that had not reached `VERIFIED`.

Reproduction (logical, deterministic, no git required): construct a project root containing (a) the inventory-drift TOML marking `.claude/rules/*.md` (or `.codex/hooks.json`) as a co-staged-evidence-required protected path, and (b) a numbered bridge thread `bridge/<slug>-001.md` ... `-015.md` whose latest version's first status token is `REVISED` and whose body cites the protected path. Stage the protected path. The current `plan_commit_batches` classifies it as `protected-with-evidence` (commit-eligible) whenever any numbered bridge file is co-staged, even though the cited thread's latest status is non-terminal. Expected: the planner must surface the protected path in a held/blocked batch (it is part of an active non-terminal bridge thread) rather than green-lighting the commit.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/sweep_commit_helpers.py`, `platform_tests/scripts/test_sweep_commit_helpers.py`. No path outside the GT-KB root is read as a live dependency, created, or required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `VERIFIED` is the authoritative terminal signal and the bridge protocol must not be bypassed; committing a protected file while its thread is non-terminal is a de-facto bridge bypass at the commit boundary, which this fix closes by reading the live bridge thread status before allowing the commit batch.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - committed worktree state is a durable artifact that must stay consistent with the bridge thread of record; the fix keeps the sweep commit aligned with bridge verification evidence rather than committing ahead of it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing specification that constrains the change (mandatory linkage); the spec list below is the complete governing surface.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each regression test directly from a cited spec clause and runs them under pytest (mandatory spec-derived testing).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / PROJECT-GTKB-RELIABILITY-FIXES / WI-4709) as required.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision/approval gating policy; the sweep commit must not let automation finalize work (committing in-flight protected bridge changes) that the bridge protocol still routes through Loyal Opposition verification, so the fix keeps the commit decision subordinate to the bridge verification gate rather than an automation shortcut around owner/LO control.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform tooling (`scripts/sweep_commit_helpers.py`) and platform tests (`platform_tests/scripts/...`); no application/adopter surface is touched and no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4709 is a standing-backlog work item (P2, origin=defect) under PROJECT-GTKB-RELIABILITY-FIXES, the canonical backlog authority for this work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - `.codex/hooks.json` is one of the protected co-staged-evidence paths the sweep handles; the non-terminal-thread gate must treat the Codex hook-config surface identically to the Claude narrative surfaces so parity-relevant hook-config commits are not finalized ahead of bridge verification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the commit-eligibility decision remains artifact-backed (driven by the live bridge thread's status token) rather than inferred from packet/evidence presence alone.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the sweep's commit trigger for a protected artifact with that artifact's bridge lifecycle state (only commit when the addressing thread is terminal/VERIFIED or no active thread exists).

## Prior Deliberations

- `DELIB-20263482` - WI-4528 Shared Bridge Evidence Batch Defect - the originating deliberation for `scripts/sweep_commit_helpers.py`; that fix added the co-staged-evidence planner, and this WI extends the same planner with a non-terminal-thread gate, so it is the direct lineage for the touched module.
- `DELIB-20260867` - Owner approval: WI-4356 work-tree hygiene implementation authorization - sibling work-tree/sweep hygiene context establishing the automation-hygiene theme WI-4709 (and the related WI-4703) sit within.
- `DELIB-20263080` - Loyal Opposition Review - WI-4250 Status Reconciliation Authorization - prior LO reasoning on keeping committed state reconciled with bridge thread status, the same desync class this defect produces.
- `DELIB-2290` - Loyal Opposition Review - Project Completion Scanner WI-AUTO Regex Fix - retained as prior precedent that automation must respect verification state before finalizing lifecycle transitions.
- `DELIB-20264651` - Loyal Opposition Review - Project Completion Scanner WI-AUTO Regex Fix - companion verification of the same scanner correction; same principle (automation gated on verification evidence) applies to the sweep-commit boundary.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - the standing project authorization for PROJECT-GTKB-RELIABILITY-FIXES; WI-4709 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the defect, and is bounded to ~1 source file + 1 test, so it is covered by this standing authorization through active project membership.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing reliability fast-lane authorization (carried by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) that authorizes small, single-concern defect/regression fixes to proceed through the fast lane; WI-4709 meets every fast-lane criterion (see Fast-Lane Eligibility below).
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (pipeline-repair and P1/P2 first); WI-4709 (P2, defect) is in scope for this batch.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` and the Mandatory VERIFIED Commit-Finalization Gate in `.claude/rules/file-bridge-protocol.md` already establish that protected bridge work must not be finalized (committed) before its thread reaches `VERIFIED`. This fix enforces that existing contract at the sweep-commit planning boundary by adding a non-terminal-bridge-thread gate. No new or revised requirement/specification is introduced; the change closes a gap between the established requirement and the automation that bypassed it.

## Proposed Scope

1. In `scripts/sweep_commit_helpers.py`, add a read-only helper that maps a staged protected path to the active *non-terminal* bridge threads that cite it. It reuses the existing bridge reader `groundtruth_kb.bridge.versioned_files.scan_expected_documents` (slug -> ordered files + latest version) and `status_from_bridge_file` (canonical status token) so NO new bridge-reading surface is introduced; non-terminal is the existing `{NEW, REVISED, GO, NO-GO}` token set (a thread whose latest version's status token is terminal — `VERIFIED`/`WITHDRAWN`/`DEFERRED`/`ADVISORY`/`ACCEPTED` — does not gate). Citation matching reuses the existing path-token/basename match already implemented in `bridge_files_citing`.
2. Extend `plan_commit_batches` so that a protected path cited by at least one active non-terminal bridge thread is emitted in a new batch kind `protected-active-thread-nonterminal` whose `rationale` names the citing slug(s) and their latest non-terminal status, and whose paths are NOT grouped with co-staged evidence for commit. This withholds the protected path from a commit-eligible batch (it is surfaced as held/blocked) rather than raising, so the orchestrator skips it and continues committing the rest of the staged set.
   - Precedence: the non-terminal-thread gate is evaluated BEFORE the existing `protected-with-evidence` / `protected-missing-evidence` classification, so a protected path that is both co-staged with evidence AND part of an active non-terminal thread is held (the conservative/correct posture for this defect), not green-lit.
   - Scope guard (no over-tightening / no regression): the gate fires ONLY when an active non-terminal thread actually cites the protected path. A protected path with no citing thread, or whose only citing threads are terminal/`VERIFIED`, retains the existing co-staged-evidence behavior unchanged.
   - Fail-soft: when the bridge directory is absent or a bridge file is unreadable, the new helper returns "no non-terminal threads" so the planner degrades to existing behavior and never raises (consistent with the module's existing fail-soft contract).
3. Update the `gtkb-sweep-commit` skill documentation (`.claude/skills/gtkb-sweep-commit/SKILL.md`) is OUT OF SCOPE for this fast-lane fix; the skill already consumes `plan_commit_batches` output, so honoring the new held batch kind is a behavior the planner enforces. (Noted for transparency; not a target path.)
4. Add regression tests in `platform_tests/scripts/test_sweep_commit_helpers.py` (see verification plan), using the existing synthetic-bridge-fixture pattern in that file (`tmp_path` bridge files; not citations to live threads).

This is the defect-removal path. The WI's alternative ("model/display that automatic completion can precede report verification" / accept the desync) is a behavior/contract change that would require a new requirement and is explicitly out of scope for this fast-lane defect fix.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no commit ahead of VERIFIED) | `test_protected_path_in_nonterminal_thread_is_held` | A protected path cited by a `REVISED` thread is emitted in a `protected-active-thread-nonterminal` batch and is NOT in any `protected-with-evidence` batch, even when a numbered bridge file is co-staged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no false-positive regression) | `test_protected_path_with_only_verified_thread_commits` | A protected path whose citing thread's latest status is `VERIFIED` retains `protected-with-evidence` behavior (the gate does not over-reach). |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (decision is bridge-status-driven) | `test_latest_version_status_decides_not_earlier_version` | A thread with `NEW@-001`...`VERIFIED@-002` (latest terminal) does NOT gate; a thread with `GO@-001`...`REVISED@-002` (latest non-terminal) DOES gate. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (scope guard / no over-tightening) | `test_protected_path_with_no_citing_thread_unaffected` | A protected path that no active non-terminal thread cites retains existing co-staged-evidence / missing-evidence classification unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (fail-soft) | `test_nonterminal_gate_fail_soft_when_bridge_dir_absent` | With no `bridge/` directory (or an unreadable bridge file), the new helper returns no non-terminal threads and `plan_commit_batches` degrades to existing behavior without raising. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Codex hook-config parity) | `test_codex_hooks_json_in_nonterminal_thread_is_held` | A `.codex/hooks.json` change cited by a non-terminal thread is held identically to the narrative-rule-file case. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_sweep_commit_helpers.py -q --tb=short`
- `python -m ruff check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py`
- `python -m ruff format --check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py`

## Acceptance Criteria

1. `plan_commit_batches` emits a `protected-active-thread-nonterminal` batch (held, not commit-eligible) for any protected path cited by an active non-terminal (`NEW`/`REVISED`/`GO`/`NO-GO`) bridge thread, and that path appears in no `protected-with-evidence` batch.
2. Commit-eligibility is unchanged for protected paths whose citing threads are all terminal/`VERIFIED`, and for protected paths with no citing thread (no regression to the WI-4528 behavior or its existing tests).
3. The new gate reuses `groundtruth_kb.bridge.versioned_files` (`scan_expected_documents`, `status_from_bridge_file`) and introduces no new bridge-reading surface.
4. The gate is fail-soft (no raised exception) when `bridge/` is absent or a bridge file is unreadable.
5. All existing tests in `platform_tests/scripts/test_sweep_commit_helpers.py` continue to pass, the six new derived tests pass, and `ruff check` / `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: over-tightening could hold a protected path whose thread is effectively done but was left at a non-terminal token. Mitigation: the gate keys on the latest version's canonical status token; the correct remedy for a stuck thread is to finalize it to `VERIFIED` (the bridge protocol's own discipline), which is the behavior we want to enforce. The held batch is surfaced with a clear rationale naming the citing slug so the operator can act.
- Risk: citation false-positives (a bridge body mentions a protected path it does not actually address). Mitigation: this reuses the existing `bridge_files_citing` path-token/basename match already accepted for the co-staged-evidence planner; holding on a citation match is the conservative posture for a VERIFIED-gate bypass and does not lose work (the path stays staged/uncommitted, never reverted).
- Risk: performance of scanning all `bridge/` files during a sweep. Mitigation: `scan_expected_documents` is a single directory glob already used by bridge tooling; the planner runs once per sweep, not per file.
- Rollback: revert the predicate/helper addition in `scripts/sweep_commit_helpers.py` and the new tests; the change is additive (a new batch kind plus a guarded pre-classification branch) with no migration and no change to existing batch-kind semantics, so it is fully reversible.

## Files Expected To Change

- `scripts/sweep_commit_helpers.py`
- `platform_tests/scripts/test_sweep_commit_helpers.py`

## Recommended Commit Type

`fix`
