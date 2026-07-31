Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-4528

# WI-4528 Shared Bridge Evidence Batch Defect

Prepared: 2026-06-14T15:43:43Z
Reviewer: Codex Loyal Opposition, harness A
Artifact type: advisory report, not a bridge verdict

## Claim

The WI-4528 helper can return an unsafe commit plan when multiple protected
paths share the same bridge evidence file. The latest bridge thread advanced to
`VERIFIED` by another Codex A session before this review could file a verdict,
so this report preserves the defect additively instead of issuing a competing
same-harness bridge verdict.

## Evidence

Source: `scripts/sweep_commit_helpers.py`.

The planner creates one `protected-with-evidence` batch per protected path:

- `scripts/sweep_commit_helpers.py:261-277` iterates protected paths and appends
  `[protected, *evidence]` for each one.
- `scripts/sweep_commit_helpers.py:265` records evidence in `consumed_bridge`,
  but that set is only used later to suppress leftover bridge-only batches. It
  does not prevent the same evidence path from appearing in multiple protected
  batches.

The focused implementation gates passed:

```text
python -m pytest platform_tests/scripts/test_sweep_commit_helpers.py -q --tb=short
14 passed in 3.34s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py
All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/sweep_commit_helpers.py platform_tests/scripts/test_sweep_commit_helpers.py
2 files already formatted
```

The uncovered probe:

```python
from pathlib import Path
import sys

sys.path.insert(0, "scripts")
import sweep_commit_helpers as h

batches = h.plan_commit_batches(
    [".codex/hooks.json", ".githooks/pre-commit", "bridge/INDEX.md"],
    Path("."),
)
```

Observed result:

```json
[
  {
    "paths": [".codex/hooks.json", "bridge/INDEX.md"],
    "kind": "protected-with-evidence",
    "evidence": ["bridge/INDEX.md"]
  },
  {
    "paths": [".githooks/pre-commit", "bridge/INDEX.md"],
    "kind": "protected-with-evidence",
    "evidence": ["bridge/INDEX.md"]
  }
]
```

The current test suite covers one protected path with `bridge/INDEX.md` and
multiple protected paths with distinct evidence files, but not shared evidence:

- `platform_tests/scripts/test_sweep_commit_helpers.py:124-133`
- `platform_tests/scripts/test_sweep_commit_helpers.py:163-183`

## Risk / Impact

WI-4528 exists to prevent protected hook/config commits from being separated
from their bridge evidence. The proposal and implementation report define the
execution model as committing each planned batch with `git commit -- <paths>`.
A staged evidence file can be consumed by only one commit. After the first batch
commits `bridge/INDEX.md`, the second batch still lists `bridge/INDEX.md`, but
that path no longer has a staged diff; the inventory-drift gate can then evaluate
the second protected-path commit without `review_evidence_present`.

This recreates the same commit blockage class WI-4528 was meant to eliminate.

## Recommended Action

File a follow-on repair for WI-4528 or revise the completed work if the bridge
thread is reopened. The minimal correction is to make `plan_commit_batches`
return a non-overlapping plan:

- each staged path appears in at most one batch;
- protected paths sharing `bridge/INDEX.md` are grouped into one
  `protected-with-evidence` batch;
- one bridge file that cites multiple protected paths is not duplicated across
  protected batches.

Add regression tests for:

- two protected paths plus `bridge/INDEX.md` produce one protected evidence
  batch;
- one bridge file citing two protected paths is not duplicated;
- a global duplicate-path invariant across all returned batches.

## Decision Needed From Owner

None. This is a Prime Builder repair candidate under existing bridge/backlog
governance.

## Opportunity Radar

The deterministic-service opportunity is local: the helper should enforce a
general "no duplicate staged path across batches" invariant, not rely on
operator judgement during sweep-commit execution. No separate automation
proposal is needed beyond the repair candidate above.
