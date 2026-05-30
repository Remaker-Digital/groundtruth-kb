NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s363-phase-2-rc-gate-seed-resilient
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Defect-Fix Proposal - Repair RC Gate membase-seed step (Path B: resilient handling when CI seed fixture is absent)

bridge_kind: implementation_proposal
Document: gtkb-rc-gate-membase-seed-resilient-fixture
Version: 001 (NEW)
Date: 2026-05-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3418

target_paths: ["scripts/membase_ci_seed.py", "tests/scripts/test_membase_ci_seed_resilient_fixture.py"]

## Claim

The Release Candidate Gate workflow (run 26502233081 on `develop@7ee608e`, 2026-05-27 09:15Z) fails hard with `FileNotFoundError: Fixture not found: tests/fixtures/ci_membase_seed.json` from `scripts/membase_ci_seed.py:204`. The fixture file does not exist anywhere in the repo. This proposal implements **Path B** (resilient seed step): when the fixture is absent, log a warning to stderr and return a zero-counts result rather than raise. Path A (generate + commit the fixture content) is documented as an alternative slice and deferred until the owner directs it.

## Defect / Reproduction

Workflow failure (S363 Phase 2 CI triage, 2026-05-28):

```
$ gh run view 26502233081 --log-failed | grep -E "Error|exit"
File "/home/runner/work/groundtruth-kb/groundtruth-kb/scripts/membase_ci_seed.py", line 204, in seed_records
    raise FileNotFoundError(f"Fixture not found: {fixture_path}")
FileNotFoundError: Fixture not found: /home/runner/work/groundtruth-kb/groundtruth-kb/tests/fixtures/ci_membase_seed.json
##[error]Process completed with exit code 1.
```

Current script behavior (`scripts/membase_ci_seed.py:199-205`):

```python
def seed_records(db_path: Path, fixture_path: Path) -> dict[str, int]:
    _ensure_groundtruth_kb_on_path()
    from groundtruth_kb.db import KnowledgeDB

    if not fixture_path.is_file():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
```

Repo state: `find` for `ci_membase_seed.json` returns no results outside permission-denied transient directories. The fixture file is not committed.

Script docstring context (`scripts/membase_ci_seed.py:1-22`):

```
"""Export/import the MemBase records that CI tests require.

This script bridges the gap created by the 2026-04-24 owner decision (commit
``23a54af3``) that untracked ``groundtruth.db``. The Slice 8.6 -003 GO'd plan
plus the S330 Phase 1.5 owner decision (Option A) requires CI to seed the
records governance_adoption tests assert before pytest runs.

Two modes:

* ``--export``: read the listed spec/deliberation IDs from the local
  ``groundtruth.db`` and write a JSON fixture at
  ``tests/fixtures/ci_membase_seed.json``. Run this locally when records
  change; commit the fixture so CI sees the update.
* ``--seed``: read the JSON fixture and insert the records into the target
  database (default: repo-root ``groundtruth.db``). Idempotent — skips
  records that already exist at the same version.
```

Intended workflow: developer runs `--export` locally → commits fixture → CI uses `--seed`. Currently the fixture has either never been generated/committed, or was deleted, leaving CI's `--seed` step with no fixture to consume.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`:
- `scripts/membase_ci_seed.py`
- `tests/scripts/test_membase_ci_seed_resilient_fixture.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal follows NEW/REVISED/GO/NO-GO/VERIFIED workflow
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - `scripts/membase_ci_seed.py` is a CI infrastructure artifact whose hard-failure breaks the RC Gate workflow
- `GOV-RELIABILITY-FAST-LANE-001` - governing fast-lane spec; eligibility per Reliability Fast-Lane Eligibility subsection below
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan below maps acceptance to verification commands and a regression test
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied above
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - new regression test creation is a lifecycle trigger; satisfied by the new test file under target_paths
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision captured via AskUserQuestion (Owner Decisions section)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`
- `GOV-SESSION-SELF-INITIALIZATION-001` - Release Candidate Gate is one of the testing/tool integrations surfaced in the startup payload; correct seed-step behavior restores the workflow's ability to reach pytest
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - script-only change in `scripts/`; no hook surface impact; parity preserved
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - creates a durable regression test artifact under `tests/scripts/`

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing fast-lane authorization underlying `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - parent governance for the Slice 8.6 work that introduced `membase_ci_seed.py`
- `2026-04-24 owner decision (commit 23a54af3)` - untracked `groundtruth.db`; the original motivation for the seed-step pattern referenced in the script docstring
- `S363 backlog review session` - owner focus selection (B: Repair Testing/Tool Integrations)
- `S363 owner direction 2026-05-28 (RC Gate as follow-on)`: Owner directed RC Gate fix as follow-on after SonarCloud, with Path A vs Path B as documented decision

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: Owner selected "Repair Testing/Tool Integrations"
- `S363 AskUserQuestion answer 2026-05-28 (Phase 2 direction)`: Owner selected "File proposals for the 2 quick-win config fixes"
- `S363 owner direction 2026-05-28 (RC Gate as follow-on)`: Owner directed RC Gate fix as follow-on after SonarCloud; Path B chosen as default by Prime per the rationale documented in the Path A vs Path B Decision subsection below; owner may override via REVISED if Path A is preferred
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization; allowed_mutation_classes=["source","test_addition","hook_upgrade"]; this proposal's target_paths (one source file + one test file) fit the source + test_addition classes

## Requirement Sufficiency

Existing requirements sufficient. The script's purpose is documented in its docstring (Slice 8.6 / S330 Phase 1.5 artifact). The Path B repair makes the seed step *resilient to fixture absence* without changing the intended workflow when the fixture is present. No new requirement created. The script's `--export` mode is unchanged.

### Reliability Fast-Lane Eligibility (per GOV-RELIABILITY-FAST-LANE-001)

1. **Small single-concern defect fix**: one resilience patch in one function (`seed_records`).
2. **Source + test-addition target paths only**: `scripts/membase_ci_seed.py` (source) + `tests/scripts/test_membase_ci_seed_resilient_fixture.py` (test_addition).
3. **No forbidden operations**: no deploy, no `git push --force`, no spec deletion.
4. **Bounded scope**: ~10 LOC change in the script + ~50 LOC new test file.
5. **Reversible**: rollback is a single revert of `scripts/membase_ci_seed.py` + drop of the new test file.

### Path A vs Path B Decision

The defect has two valid fix paths. Prime selected **Path B** as the default for this proposal. The rationale and Path A's alternative status are documented here so the bridge protocol's review surface can ratify or redirect.

| Path | Approach | Pros | Cons | Recommendation |
|---|---|---|---|---|
| **A** | Generate fixture via `scripts/membase_ci_seed.py export` against a populated local DB, commit `tests/fixtures/ci_membase_seed.json` | Preserves intended seed-with-records workflow; CI runs pytest against pre-seeded DB | Requires owner's local DB to contain the records that test files reference; commits generated JSON data (~KB-class artifact tracked in git); does not address future fixture-absence cases (next deletion re-introduces the same failure) | Deferred follow-on slice if owner confirms tests require seeded records |
| **B (this proposal)** | Modify `seed_records()` to log warning and return zero-counts when fixture absent, rather than raise | Resilient by design; no fixture generation; ~10 LOC code-only change; future fixture absence does not break CI; tests that strictly require seeded records can be made explicit about that dependency | If tests genuinely require the fixture content, those tests will fail downstream (but with their own clearer errors, separable from the seed-step concern) | **Default for this proposal** |

If LO or owner prefers Path A, this proposal is NO-GO'd with that note and a Path-A proposal is filed at a sibling thread.

## Proposed Scope

IP-1 - Make seed_records resilient to absent fixture

Modify `scripts/membase_ci_seed.py:seed_records()` to:

```python
import sys

def seed_records(db_path: Path, fixture_path: Path) -> dict[str, int]:
    _ensure_groundtruth_kb_on_path()
    from groundtruth_kb.db import KnowledgeDB

    if not fixture_path.is_file():
        print(
            f"Warning: CI seed fixture not found at {fixture_path}; "
            f"skipping seed step (zero records inserted).",
            file=sys.stderr,
        )
        return {
            "specs_inserted": 0,
            "specs_skipped": 0,
            "delibs_inserted": 0,
            "delibs_skipped": 0,
        }

    # ... rest of function unchanged ...
```

`sys` is already imported at the top of the file. The change is the if-block body: emit warning instead of raise, return zero-counts dict matching the existing return shape.

Optional callsite consideration: `main()` already prints a summary from the returned dict (`f"Seeded {result['specs_inserted']} new specs..."`). With zero counts, the summary will print "Seeded 0 new specs (0 skipped), 0 new deliberations (0 skipped)" which is correct and unambiguous.

IP-2 - Regression test

Add `tests/scripts/test_membase_ci_seed_resilient_fixture.py` with three tests:

1. `test_seed_records_raises_when_fixture_absent_was_old_behavior` - this test is NOT added; it would test the removed behavior. Documented here so the absence is intentional.
2. `test_seed_records_returns_zero_counts_when_fixture_absent` - tmp_path with no fixture file; assert returned dict has all zero values and matches the documented shape.
3. `test_seed_records_writes_warning_to_stderr_when_fixture_absent` - tmp_path with no fixture file; capture stderr via capsys; assert it contains "fixture not found" warning text.
4. `test_seed_records_processes_fixture_when_present` - tmp_path with a minimal fake fixture (empty arrays); assert returned dict is zero-counts (no records inserted because fixture has none). Verifies the present-fixture code path still works.

Test fixture data does NOT include real GT-KB spec/delib records — only minimal shape to exercise the code paths. No KB mutation in tests; tests use `tmp_path` for the DB path.

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| GOV-SESSION-SELF-INITIALIZATION-001 (RC Gate workflow seed step no longer hard-fails) | Post-commit gh run view on develop | `gh run list --workflow release-candidate-gate.yml --branch develop --limit 1` then `gh run view <id>` | Python release gate step completes seed substep with exit 0 (regardless of subsequent pytest outcome) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each acceptance has a test) | All 3 regression tests | `pytest tests/scripts/test_membase_ci_seed_resilient_fixture.py -v` | All 3 PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (CI artifact repaired) | `scripts/membase_ci_seed.py` source inspection | `grep -A 10 "def seed_records" scripts/membase_ci_seed.py` | Contains the new resilience block per IP-1 |
| GOV-RELIABILITY-FAST-LANE-001 (fast-lane eligibility) | target_paths + scope inspection | Manual review of -001 + PAUTH allowed_mutation_classes | source + test_addition; matches PAUTH |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (test creation lifecycle) | New test file creation | `git status` after impl | `tests/scripts/test_membase_ci_seed_resilient_fixture.py` present |

## Acceptance Criteria

1. `scripts/membase_ci_seed.py:seed_records()` no longer raises `FileNotFoundError` when fixture absent; instead emits stderr warning and returns zero-counts dict.
2. All 3 regression tests in `tests/scripts/test_membase_ci_seed_resilient_fixture.py` PASS via `pytest -v`.
3. Post-commit Release Candidate Gate workflow run on `develop` completes the `Python release gate` step's seed substep with exit 0 (the workflow may still fail downstream on pytest-level failures, but the seed step no longer cascades a hard FileNotFoundError into a workflow failure).
4. WI-3418 transitions to `resolved` upon VERIFIED.
5. If LO or owner determines tests genuinely require seeded records, Path A is filed as a sibling proposal `bridge/gtkb-rc-gate-membase-seed-fixture-content-001.md` (out of scope for this proposal).

## Risks / Rollback

- Risk: tests that depend on seeded records now fail downstream rather than skip cleanly. Mitigation: those failures become independently triageable (separated from the seed-step concern); if test count is small, file Path A as the sibling slice; if test count is large, owner may prefer Path A directly.
- Risk: workflow's overall success is not yet restored — Python Tests workflow has other failures (5 of 7 shards failing per S363 Phase 2 triage) that are independent of the seed step. Mitigation: this proposal's success criterion is the seed step passing, not the entire workflow turning green. Other failures are tracked as separate Phase 2 items.
- Risk: silent-skip in CI could mask a missing fixture that the developer thought existed. Mitigation: the stderr warning is logged and visible in workflow logs; explicit `Warning:` prefix makes it grep-able.
- Rollback: revert the patch to `scripts/membase_ci_seed.py` and drop the new test file. Single-commit revert.

## Files Expected To Change

- `scripts/membase_ci_seed.py` (modified; ~10 LOC change in `seed_records()` function)
- `tests/scripts/test_membase_ci_seed_resilient_fixture.py` (NEW; ~50 LOC)

## Recommended Commit Type

`fix` - CI seed-step resilience repair; no new capability surface beyond the resilient behavior and its regression test.
