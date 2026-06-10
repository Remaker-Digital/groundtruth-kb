REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s368-rc-gate-fixture-revised-003
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Defect-Fix Proposal - Repair RC Gate membase-seed step (REVISED: fixture-path reconciliation; supersedes resilient-skip framing)

bridge_kind: prime_proposal
Document: gtkb-rc-gate-membase-seed-resilient-fixture
Version: 003 (REVISED)
Date: 2026-05-28 UTC
Responds to: bridge/gtkb-rc-gate-membase-seed-resilient-fixture-002.md (NO-GO)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3418

target_paths: ["scripts/membase_ci_seed.py", "platform_tests/scripts/test_membase_ci_seed_resilient_fixture.py"]

Implements: WI-3418 (RC Gate seed-step fixture-path reconciliation)

## Reframe Summary (Responds to NO-GO -002)

The NEW proposal (-001) was based on a false premise: it stated the CI seed fixture "does not exist anywhere in the repo." It does. A 89,354-byte committed fixture lives at `applications/Agent_Red/tests/fixtures/ci_membase_seed.json`, and the release-candidate workflow's comment block at `.github/workflows/release-candidate-gate.yml:85` already names that path as the canonical source. Codex's NO-GO (-002) F1 was correct: the real defect is fixture-path drift between three places (workflow comment, script default, committed file), not fixture absence.

This REVISED proposal scraps the silent-skip framing and treats the defect as a **fixture-path reconciliation** problem. The seed step's hard-fail is a symptom of the script's `DEFAULT_FIXTURE` constant pointing to the wrong path. Repairing the path turns the seed step green on its current canonical fixture content without authorizing skip-on-absence behavior that would mask future configuration drift.

Codex's NO-GO -002 F2 and F3 are also addressed: the script's stale `TEST_FILES` discovery list (root `tests/scripts/`) is corrected to `platform_tests/scripts/`, and the new regression test is placed under `platform_tests/scripts/` to match pyproject.toml testpaths.

## Authoritative Fixture Location Decision

**Canonical fixture path:** `applications/Agent_Red/tests/fixtures/ci_membase_seed.json`.

### Justification

1. **The file is committed and live.** `ls -la applications/Agent_Red/tests/fixtures/ci_membase_seed.json` shows a 89,354-byte file dated 2026-05-03. There is no committed file at root `tests/fixtures/ci_membase_seed.json` (the `tests/fixtures/` directory does not exist).

2. **The workflow comment already names the application path as canonical.** `.github/workflows/release-candidate-gate.yml:85` states: "groundtruth.db is gitignored per owner decision 2026-04-24 (commit 23a54af3); CI must materialize the records from `applications/Agent_Red/tests/fixtures/ci_membase_seed.json` before pytest runs."

3. **`pyproject.toml:9` includes `applications/Agent_Red/tests` in testpaths**, making fixtures under that tree first-class within the repo's test surface.

4. **CLAUDE.md project-root-boundary compliance.** All paths remain within `E:\GT-KB` and the file is within `E:\GT-KB\applications\`. Consistent with `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

5. **No GT-KB fixture exists at the root location to compete.** The `tests/fixtures/` directory does not exist in the live checkout.

### Why not relocate the fixture instead

Relocating to `tests/fixtures/` was rejected:
- CLAUDE.md project-root-boundary rule disfavors creating new top-level `tests/` content when an `applications/` subtree is the established home.
- The root `tests/` tree is not part of pytest testpaths.

Path drift is the defect. The fixture's actual location is canonical; the script and workflow invocation must align to that path.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`:
- `scripts/membase_ci_seed.py` (modified)
- `platform_tests/scripts/test_membase_ci_seed_resilient_fixture.py` (NEW)

The committed fixture at `applications/Agent_Red/tests/fixtures/ci_membase_seed.json` is not modified by this proposal; it is referenced as the authoritative path target.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - `scripts/membase_ci_seed.py` is a CI infrastructure artifact whose path-drift defect breaks the RC Gate workflow
- `GOV-RELIABILITY-FAST-LANE-001` - governing fast-lane spec; eligibility per subsection below
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED cites all relevant cross-cutting specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Specification-Derived Verification Plan below
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - new regression test creation
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision captured via AskUserQuestion
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`; canonical fixture under `applications/Agent_Red/tests/fixtures/`
- `GOV-SESSION-SELF-INITIALIZATION-001` - RC Gate is in the testing/tool integrations surface
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - script-only change; no hook surface impact
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - creates a durable regression test artifact

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing fast-lane authorization
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - parent governance for Slice 8.6 work
- `DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE` - Option A owner decision establishing seed-from-fixture workflow pattern
- `2026-04-24 owner decision (commit 23a54af3)` - untracked `groundtruth.db`; original motivation
- `S363 backlog review session` - owner focus selection (B: Repair Testing/Tool Integrations)
- `DELIB-1750` and `DELIB-1749` - GTKB-ISOLATION-017 Slice 8.6 CI-failure triage revised GO and VERIFIED
- Codex NO-GO -002 (this thread) - established the path-drift framing

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27 (focus menu B)`: Owner selected "Repair Testing/Tool Integrations" - authorizes this CI infrastructure repair within standing fast-lane scope.
- `S363 AskUserQuestion answer 2026-05-28 (Phase 2 direction)`: Owner selected "File proposals for the 2 quick-win config fixes" - this proposal is one of those.
- `S363 owner direction 2026-05-28 (RC Gate as follow-on)`: Owner directed RC Gate fix as follow-on after SonarCloud; no new owner decision required because the path-reconciliation approach restores rather than narrows the seed-with-records workflow Option A authorized in `DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization; allowed_mutation_classes=["source","test_addition","hook_upgrade"]; this REVISED's target_paths fit source + test_addition.

No new AskUserQuestion is filed for this REVISED.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE` (Option A) already requires CI to seed records from a fixture before pytest runs. This REVISED corrects the script's fixture path constant and stale test discovery list so the existing Option A workflow operates against its canonical fixture.

### Reliability Fast-Lane Eligibility (per GOV-RELIABILITY-FAST-LANE-001)

1. **Small single-concern defect fix**: path reconciliation in one constant + one tuple + a callsite consistency update.
2. **Source + test-addition target paths only**: `scripts/membase_ci_seed.py` + `platform_tests/scripts/test_membase_ci_seed_resilient_fixture.py`.
3. **No forbidden operations**: no deploy, no `git push --force`, no spec deletion, no fixture content change.
4. **Bounded scope**: ~5 LOC change in script + ~80 LOC new test file.
5. **Reversible**: single revert.

## Proposed Scope

### IP-1 - Reconcile DEFAULT_FIXTURE path to canonical application location

Modify `scripts/membase_ci_seed.py:36`:

```python
# Before:
DEFAULT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "ci_membase_seed.json"

# After:
DEFAULT_FIXTURE = REPO_ROOT / "applications" / "Agent_Red" / "tests" / "fixtures" / "ci_membase_seed.json"
```

Update the script docstring (lines 11-13) to reflect the canonical path.

The `seed_records()` function retains its `FileNotFoundError` raise behavior: a fixture that genuinely went missing is still a hard error, not a silent skip. The defect was the wrong path, not missing resilience.

### IP-2 - Correct stale TEST_FILES discovery list

Modify `scripts/membase_ci_seed.py:37-40`:

```python
# Before:
TEST_FILES = (
    REPO_ROOT / "tests" / "scripts" / "test_groundtruth_governance_adoption.py",
    REPO_ROOT / "tests" / "scripts" / "test_standing_backlog_harvest.py",
)

# After:
TEST_FILES = (
    REPO_ROOT / "platform_tests" / "scripts" / "test_groundtruth_governance_adoption.py",
    REPO_ROOT / "platform_tests" / "scripts" / "test_standing_backlog_harvest.py",
)
```

### IP-3 - Regression test under platform_tests/scripts/

Add `platform_tests/scripts/test_membase_ci_seed_resilient_fixture.py` with:

1. `test_default_fixture_constant_points_to_application_tree` - assert path contains `applications/Agent_Red/tests/fixtures`.
2. `test_default_fixture_file_exists_at_canonical_path` - assert `.is_file()` is True.
3. `test_test_files_constant_points_to_platform_tree` - assert paths contain `platform_tests/scripts`.
4. `test_test_files_paths_exist_in_checkout` - assert `.is_file()` for each.
5. `test_seed_records_still_raises_when_fixture_absent` - tmp_path with no fixture; assert `FileNotFoundError` (preserves hard-fail behavior).

Note: the original NEW proposal proposed three "resilient skip" tests; those are intentionally NOT carried forward because the resilient-skip behavior is no longer being implemented.

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| GOV-SESSION-SELF-INITIALIZATION-001 | Post-commit gh run view on develop | `gh run list --workflow release-candidate-gate.yml --branch develop --limit 1` then `gh run view <id>` | "Seed CI MemBase records" step exit 0 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | All 5 regression tests | `pytest platform_tests/scripts/test_membase_ci_seed_resilient_fixture.py -v` | All 5 PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | `scripts/membase_ci_seed.py` source inspection | Source review of lines 36-40 | DEFAULT_FIXTURE + TEST_FILES point at existing in-tree paths |
| GOV-RELIABILITY-FAST-LANE-001 | target_paths + scope inspection | Manual review | source + test_addition; matches PAUTH |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | New test file creation | `git status` after impl | New test file present |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Path inspection | Source review of DEFAULT_FIXTURE | Resolves under `E:\GT-KB\applications\` |

## Acceptance Criteria

1. `scripts/membase_ci_seed.py:36` DEFAULT_FIXTURE resolves to canonical application path; file present at HEAD.
2. `scripts/membase_ci_seed.py:37-40` TEST_FILES lists paths under `platform_tests/scripts/`; all exist.
3. Script docstring at lines 11-13 names canonical application fixture path.
4. All 5 regression tests PASS.
5. Post-commit RC Gate workflow "Seed CI MemBase records" step exit 0 (entire workflow may surface unrelated failures downstream).
6. WI-3418 transitions to `resolved` upon VERIFIED.

## Applicability Preflight (anticipated)

Anticipated PASS reasoning:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - 12 cited specs in Specification Links section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification Plan maps every spec to verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - filed under `bridge/` with numbered version.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` - all target paths within `E:\GT-KB`.

The reframe does not change spec linkage; preflight expected to pass on the same surface that satisfied -001.

## Risks / Rollback

- **Risk**: developer with old default path memorized may run `python scripts/membase_ci_seed.py export` and produce a fixture at non-canonical location. Mitigation: docstring update + DEFAULT_FIXTURE constant flagged in new test.
- **Risk**: application-tree fixture as load-bearing dependency for platform-tree workflow may evolve later. Mitigation: cross-tree dependency documented; new test fails loudly on path drift.
- **Risk**: `--export` may overwrite canonical fixture during developer regeneration. Mitigation: intended workflow per `DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE` Option A.
- **Risk**: workflow's overall success not yet restored — Python Tests workflow has other failures. Mitigation: this proposal's success criterion is the seed step passing.
- **Rollback**: revert patch + drop new test file. Single-commit revert.

## Files Touched (target_paths recap)

- `scripts/membase_ci_seed.py` (modified; lines 11-13 docstring, line 36 DEFAULT_FIXTURE, lines 37-40 TEST_FILES)
- `platform_tests/scripts/test_membase_ci_seed_resilient_fixture.py` (NEW; ~80 LOC)

Fixture `applications/Agent_Red/tests/fixtures/ci_membase_seed.json` is referenced but NOT modified.

## Recommended Commit Type

`fix:` - CI seed-step fixture-path reconciliation defect repair; aligns script defaults and test discovery to canonical fixture location named in workflow comment. Matches `fix:` per "repairs to broken behavior with no new capability surface."

## Loyal Opposition Asks

1. **Fixture authority**: Does Codex agree `applications/Agent_Red/tests/fixtures/ci_membase_seed.json` is canonical?
2. **Cross-tree dependency framing**: Is application-tree fixture as load-bearing input for platform-tree workflow acceptable under `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`?
3. **Resilience deferral**: This REVISED removes silent-skip behavior. If Codex believes resilience to fixture-absence is also required (independently of path-drift defect), NO-GO with that finding.
4. **Doctor-check follow-on**: Codex's -002 Opportunity Radar suggested a doctor check comparing DEFAULT_FIXTURE, workflow comments, and committed fixture path. Out of scope for this proposal; confirm acceptance of deferral as follow-on.
5. **Test count and coverage**: Are the 5 regression tests sufficient?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
