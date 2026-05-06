NEW

# Implementation Proposal - GTKB-CI-COVERAGE-FOR-PLATFORM-001: Dedicated CI Coverage for groundtruth-kb Tests

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** CI implementation proposal
**Risk tier:** Medium (GitHub Actions release evidence; no product runtime behavior)
**Backlog item:** `GTKB-CI-COVERAGE-FOR-PLATFORM-001`

---

## Background

Slice 8.5 established that `python-tests.yml` runs Agent Red product tests and
does not run `groundtruth-kb/tests/`. Owner waived that for `v0.7.0-rc1`, but
the waiver expires for `v0.7.0 GA`. This proposal creates the normal bridge
packet for adding GT-KB platform test coverage in CI.

No workflow files are changed until Loyal Opposition returns `GO`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md` with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites
  required specs and release evidence.
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
- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` - owner waived
  `python-tests.yml` for rc1 because it does not cover GT-KB platform tests.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "GT-KB CI coverage groundtruth-kb tests python-tests waiver v0.7.0 GA" --limit 8
```

Relevant result: `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER`.
`DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE` is adjacent because
it made the platform pytest lane pass locally.

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
`groundtruth-kb-tests` job. The dedicated workflow is cleaner because it
separates platform-package CI from Agent Red product test shards.

## Acceptance Criteria

- A GT-KB-only commit under `groundtruth-kb/**` triggers platform CI.
- CI runs `groundtruth-kb/tests/`, not only root `tests/`.
- The workflow has a manual dispatch path.
- The prior `python-tests.yml` waiver can be retired or narrowed once the new
  workflow is green.
- The implementation report includes a local run plus workflow binding evidence.

## Test Plan

Suggested commands:

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

## Prime Builder Recommendation

Proceed with a dedicated `groundtruth-kb-tests.yml` workflow after Loyal
Opposition `GO`.

