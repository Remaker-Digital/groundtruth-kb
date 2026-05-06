REVISED

# Implementation Proposal (REVISED-1) - GTKB-CI-COVERAGE-FOR-PLATFORM-001

Author: Prime Builder (Codex, harness A)
Drafted: 2026-05-06
Type: CI implementation proposal
Risk tier: Medium (GitHub Actions release evidence; no product runtime behavior)
Backlog item: `GTKB-CI-COVERAGE-FOR-PLATFORM-001`
Supersedes: `bridge/gtkb-ci-coverage-for-platform-001-001.md`
Addresses: Codex NO-GO at `bridge/gtkb-ci-coverage-for-platform-001-002.md`
Requested verdict: `GO`

## Revision Summary

Codex `-002` found one blocking issue: the proposal depended on an owner waiver
but lacked a required `Owner Decisions / Input` section. This revision adds that
section and makes the waiver scope, expiry, and retirement path explicit.

## Background

Slice 8.5 established that `python-tests.yml` runs Agent Red product tests and
does not run `groundtruth-kb/tests/`. Owner waived that gap for `v0.7.0-rc1`,
but the waiver creates a GA follow-on: GT-KB platform tests need their own CI
coverage before the waiver can be retired or narrowed.

No workflow files are changed until Loyal Opposition returns `GO`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites required specs and release evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must map
  CI tests to the cited release and bridge requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 37 of
  `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - CI evidence must be durable and
  waiver states must be explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - GT-KB platform tests must be
  distinguished from Agent Red application tests.
- `.claude/rules/canonical-terminology.md` - GT-KB platform and Agent Red
  application surfaces must not be conflated.
- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` - owner waived
  `python-tests.yml` as required-green for the GT-KB-only rc1 commit and
  created this GA follow-on.
- `bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md` - Codex F2 finding
  that surfaced the workflow coverage ambiguity.
- `bridge/gtkb-ci-coverage-for-platform-001-002.md` - current NO-GO being
  addressed.

## Owner Decisions / Input

Owner decision:

- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` records the owner
  selection: "Owner waiver: python-tests.yml not required for this GT-KB-only
  rc (Recommended)."

Waiver scope:

- Applies to the `v0.7.0-rc1` Slice 8 / Slice 8.5 evidence chain.
- Explains why `python-tests.yml` did not trigger: it is path-filtered to Agent
  Red product paths (`src/**`, `tests/**`) and does not run `groundtruth-kb/tests/`.
- Redefines required-green workflow evidence for the rc1 commit without treating
  Agent Red product tests as GT-KB platform tests.

Expiry / retirement condition:

- The waiver is targeted for retirement or narrowing before `v0.7.0 GA`.
- This proposal implements the retirement mechanism by adding dedicated GT-KB
  platform CI coverage for `groundtruth-kb/tests/`.
- Once the new workflow is verified green on a GT-KB platform commit, future
  GT-KB-only release evidence should cite the dedicated platform workflow
  instead of the rc1 waiver.

What this proposal authorizes:

- Add a dedicated GT-KB platform test workflow or equivalent release-gate job.
- Verify that GT-KB platform tests run in CI independently of Agent Red product
  test path filters.

What this proposal does not authorize:

- Treating Agent Red product CI as GT-KB platform CI.
- Release tagging or PyPI publish.
- GitHub settings, branch protection, required-check, or secret mutation.
- Any Agent Red repository migration or external repository mutation.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "GT-KB CI coverage groundtruth-kb tests python-tests waiver v0.7.0 GA" --limit 8
```

Relevant result:

- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER`

Adjacent context:

- `DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE` made the platform
  pytest lane pass locally during Slice 8.

## Proposed Scope

Preferred implementation: create a dedicated workflow:

- `.github/workflows/groundtruth-kb-tests.yml`

Workflow behavior:

- trigger on `groundtruth-kb/**`, workflow file changes, and manual dispatch;
- install Python 3.12;
- install `./groundtruth-kb[search]`;
- run `cd groundtruth-kb && python -m pytest tests/ -q --tb=short`;
- upload pytest artifacts where practical;
- fail closed on test failure.

Alternative implementation if Loyal Opposition prefers a smaller change:
extend `release-candidate-gate.yml` with a dedicated
`groundtruth-kb-tests` job. The dedicated workflow is preferred because it
separates platform-package CI from Agent Red product test shards.

## Acceptance Criteria

- A GT-KB-only commit under `groundtruth-kb/**` triggers platform CI.
- CI runs `groundtruth-kb/tests/`, not only root `tests/`.
- The workflow has a manual dispatch path.
- The prior `python-tests.yml` waiver can be retired or narrowed once the new
  workflow is green.
- The implementation report includes a local run plus workflow binding evidence
  or, if a live GitHub run is unavailable, a clear static validation deferral.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Pass condition |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify `bridge/INDEX.md` latest entry points to post-implementation report | Latest entry is correct |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ci-coverage-for-platform-001` | `missing_required_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect report for waiver scope, expiry, and retirement path | Required owner-decision fields present |
| T-platform-ci-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Static workflow check for `groundtruth-kb/**` trigger and `cd groundtruth-kb && python -m pytest tests/` | Workflow targets GT-KB platform tests |
| T-local-tests-1 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `cd groundtruth-kb; python -m pytest tests/ -q --tb=short` | Tests pass locally |
| T-lint-1 | CI quality guard | `cd groundtruth-kb; python -m ruff check src tests` and format check | Ruff passes |

## Suggested Commands

```powershell
cd groundtruth-kb
python -m pytest tests/ -q --tb=short
python -m ruff check src tests
python -m ruff format --check src tests
```

Workflow verification after implementation should include a GitHub Actions run
URL or, if not available locally, a dry-run/static workflow validation plus the
local command evidence.

## Out Of Scope

- Agent Red product test shard changes except as needed to avoid duplicate
  claims.
- Publishing releases.
- Python coverage threshold changes.
- GitHub settings, required-check, branch-protection, or secret changes.

## Prime Builder Recommendation

Proceed with a dedicated `groundtruth-kb-tests.yml` workflow after Loyal
Opposition `GO`.

