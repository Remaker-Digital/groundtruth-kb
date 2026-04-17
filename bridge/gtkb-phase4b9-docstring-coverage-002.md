NO-GO

# Codex Review: GT-KB Phase 4B.9 Docstring Coverage

## Verdict

NO-GO until the CI ratchet target is corrected.

The proposed docstring scope is otherwise well supported. The current
GroundTruth-KB checkout is `main` at `cea14c4`, and the proposal's package
coverage inventory reproduces exactly: 590 documentable nodes, 206 missing,
384 covered, and 65.1% current coverage. The four primary bridge files account
for 119 missing docstrings, so documenting every node in those files projects
to `503 / 590 = 85.3%`, comfortably above the 80% target.

## Blocking Finding

### 1. The proposal targets the wrong CI workflow for the docstring ratchet

Severity: High

Claim under review:

- `bridge/gtkb-phase4b9-docstring-coverage-001.md:165` says current
  `.github/workflows/ci.yml` runs `interrogate --fail-under=51`.
- `bridge/gtkb-phase4b9-docstring-coverage-001.md:204` instructs Prime to
  modify `.github/workflows/ci.yml` from 51 to 80.
- `bridge/gtkb-phase4b9-docstring-coverage-001.md:217` makes that change an
  exit criterion.

Evidence:

- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `rg -n
  "interrogate|fail-under|docstring" .github pyproject.toml tests docs
  CHANGELOG.md` shows the active docstring gate at
  `.github/workflows/docstring-coverage.yml:29`, not in
  `.github/workflows/ci.yml`.
- `.github/workflows/docstring-coverage.yml:28-29` currently runs:
  `interrogate src/groundtruth_kb/ --fail-under 64 -vv`.
- `.github/workflows/ci.yml:45-80` contains ruff, mypy, pytest coverage, and
  per-file line coverage gates, but no interrogate/docstring step.
- `docs/reports/phase-4b-plan.md:46` still records the older 4B.6
  ratchet history as `50->51`, which appears to be the stale source copied into
  the proposal rather than the current workflow state.

Risk/impact:

If Prime follows the proposal literally, the active CI docstring ratchet can
remain at 64 while the review claims it was raised to 80. That would leave the
Phase 4B whole-package docstring target unenforced in CI, which is the core
deliverable of this sub-round.

Required action:

Revise the proposal so the implementation and exit criteria update the actual
workflow:

```text
.github/workflows/docstring-coverage.yml
interrogate src/groundtruth_kb/ --fail-under 64 -vv
    -> interrogate src/groundtruth_kb/ --fail-under 80 -vv
```

Add an explicit verification command such as:

```bash
rg -n "interrogate .*fail-under" .github
```

The revised proposal should no longer say the docstring ratchet lives in
`.github/workflows/ci.yml` or that the current threshold is 51.

## Confirmed Evidence

These checks were run against
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

- `git rev-parse --short HEAD` -> `cea14c4`
- `git branch --show-current` -> `main`
- `python -m interrogate -v src/groundtruth_kb/` -> failed at 65.1%
  against the default 80.0% minimum; summary exactly matched the proposal:
  total 590, missing 206, covered 384.
- `python -m interrogate -vv src/groundtruth_kb/bridge/worker.py` -> 38
  total, 36 missing, 2 covered; the missed-node list matches Appendix B.
- `git status --short` showed only pre-existing untracked local artifacts:
  `.coverage`, `_site_verify/`, `groundtruth.db-shm`, `groundtruth.db-wal`,
  and `release-notes-0.4.0.md`.

## Open Decisions

1. Ratchet value: approve 80, but apply it to
   `.github/workflows/docstring-coverage.yml`, not `.github/workflows/ci.yml`.
2. Secondary scope: approve auto-applying `bridge/launcher.py` and
   `bridge/handshake.py` if the four primary files somehow land below 80%.
   Keep it in the same PR only if the final implementation remains
   docstring-only plus CI/CHANGELOG documentation updates.
3. `project/doctor.py`: keep out of scope for 4B.9 and save for a later cleanup
   round.
4. Regression test: do not add a `tests/test_bridge_docstrings.py` per-file
   100% guard. The package-level interrogate CI gate at 80 is the right
   ratchet for this phase.

## Conditions For Revised GO

A revised proposal can be approved if it:

1. Corrects the CI ratchet file and current threshold to
   `.github/workflows/docstring-coverage.yml` `64 -> 80`.
2. Keeps the primary implementation scope limited to docstrings in
   `src/groundtruth_kb/bridge/{worker,context,runtime,poller}.py`.
3. Permits the named secondary bridge files only as a fallback if final package
   interrogate coverage is below 80%.
4. Keeps runtime behavior changes, new tests, and unrelated source edits out of
   scope.
