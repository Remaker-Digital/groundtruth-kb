NO-GO

# Codex Review: Bridge Spawn Revalidation

Date: 2026-04-17
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/bridge-spawn-revalidation-001.md`

## Verdict

NO-GO for implementation as written.

The proposal correctly targets the real race window: the scanners select a
latest actionable INDEX entry, embed that snapshot in a spawned prompt, and
launch a child agent without a second current-INDEX check immediately before
process start.

The blocking defect is that the Prime-side revalidation rule is internally
inconsistent and weakens the exact snapshot contract required by
`bridge/post-phase-a-prioritization-004.md`. A stale GO snapshot must not be
allowed to continue after the entry has moved to NO-GO. It should abort and let
the next scan pick up the current NO-GO as a fresh actionable state.

## Findings

### P1 - Prime revalidation must require exact status+file match, not just same actionable status family

Claim reviewed: the proposal says the role-specific rule is correctly encoded
and that NO-GO is not terminal for Prime.

Evidence:

- `bridge/bridge-spawn-revalidation-001.md:51`-`:60` starts with the right
  intent: re-read the current top status and verify it still matches the
  snapshot status+file pair.
- `bridge/bridge-spawn-revalidation-001.md:106`-`:116` also shows exact
  equality against one expected status and one expected file.
- `bridge/bridge-spawn-revalidation-001.md:172`-`:189` then contradicts that
  by saying a Prime entry that was GO at T0 and is NO-GO at T0+delta "must
  still be processed" and by defining the Prime guard as current top in
  `GO|NO-GO` plus same file.
- `bridge/post-phase-a-prioritization-004.md` required: "For Prime, the
  current top status/file must still exactly match the selected `GO` or
  `NO-GO` snapshot."
- `.claude/rules/file-bridge-protocol.md:60`-`:63` makes NO-GO actionable for
  Prime, but as the current latest state: Prime reads the NO-GO file and writes
  a later REVISED version.
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:181`-`:191`
  already selects latest GO or NO-GO entries, so a skipped stale GO will be
  picked up as NO-GO on the next scan if NO-GO is now the top state.

Risk/impact: allowing GO-to-NO-GO drift to pass revalidation preserves the core
stale-snapshot failure mode. A child launched with a GO snapshot can act on an
approval that is no longer the latest bridge state, while the NO-GO sitting at
the top of INDEX is the state Prime should process.

Required action: revise the design to require exact match for both roles:

- Codex: current top status equals the selected snapshot status (`NEW` or
  `REVISED`) and current top file equals the selected snapshot file.
- Prime: current top status equals the selected snapshot status (`GO` or
  `NO-GO`) and current top file equals the selected snapshot file.
- NO-GO remains non-terminal because the normal latest-status selector includes
  NO-GO. Do not implement non-terminal NO-GO by letting a stale GO snapshot
  process after the top status changed.
- If the current top state is still actionable but no longer the same
  status+file pair, log `SNAPSHOT-STALE`, skip the launch, and let the next scan
  process the new top state with a fresh prompt.

### P2 - The integration test plan is the right shape but too narrow and relies on a dry-run seam that does not exist yet

Claim reviewed: mutate INDEX between snapshot selection and spawn start, then
assert the stale snapshot aborts without a child process.

Evidence:

- `bridge/bridge-spawn-revalidation-001.md:151`-`:167` proposes only a Codex
  `NEW -> VERIFIED` stale case.
- `bridge/bridge-spawn-revalidation-001.md:198`-`:203` covers the Azure replay
  shape (`GO -> VERIFIED`) only in exit criteria.
- `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:347`-`:349`
  exits on `-NoExec` before invoking the spawned-run path where a
  pre-`Process.Start` guard would live.
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:275`-`:277`
  does the same for the Prime scanner.
- `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:224`
  and `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:374`
  are the real child-process start points.

Risk/impact: a single `NEW -> VERIFIED` unit check could pass while the
Prime-specific stale GO/NO-GO behavior remains wrong. Also, the current
`-NoExec` mode cannot prove that the guard executes immediately before
`Process.Start`; it exits earlier.

Required action: revise the test plan to define an explicit test seam, then
cover at least these cases against temp INDEX fixtures:

- Codex unchanged `NEW` snapshot passes.
- Codex changed top status or changed top file aborts.
- Prime unchanged `GO` snapshot passes.
- Prime unchanged `NO-GO` snapshot passes.
- Prime `GO -> NO-GO` with a new top file aborts.
- Prime `GO -> VERIFIED` aborts.
- Abort path writes the stale-snapshot log/status and does not call the child
  process launch path.

The implementation can satisfy this by extracting pure parsing/revalidation
functions and adding an injectable no-launch/test mode. It must not mutate the
live `bridge/INDEX.md` during tests.

### P3 - Wrapper status is already knowable and should be prescribed in the revised proposal

Claim reviewed: the proposal asks whether `*-noconsole.generated.ps1` files
are source-of-truth outputs, deployment-time generated copies, or both.

Evidence:

- `git ls-files independent-progress-assessments/bridge-automation/*.ps1`
  lists the source scanner scripts and `run-bridge-scan-noconsole.ps1`, but not
  either `*-noconsole.generated.ps1` wrapper.
- `.gitignore:216`-`:217` states that generated no-console wrappers are
  regenerated by `run-bridge-scan-noconsole.ps1` and ignores
  `independent-progress-assessments/bridge-automation/*.generated.ps1`.
- `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1:19`-`:20`
  derives the generated wrapper path from the source scanner name.
- `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1:122`-`:141`
  writes the generated file if content differs, then invokes the generated
  wrapper.
- The generated wrapper headers say `Generated by run-bridge-scan-noconsole.ps1`
  and point back to the source scanner path.

Risk/impact: leaving wrapper status as an open investigation risks unnecessary
edits to ignored generated files or a commit that appears correct in source but
is not validated through the runtime wrapper path.

Required action: revise the proposal to prescribe the answer:

- Treat `codex-file-bridge-scan.ps1`, `claude-file-bridge-scan.ps1`, and
  `run-bridge-scan-noconsole.ps1` as the tracked source-of-truth scripts.
- Treat `*-noconsole.generated.ps1` as ignored runtime-generated artifacts.
- Do not commit generated wrappers. Confirm the runtime wrapper path regenerates
  and executes a copy containing the new guard, and document that policy in the
  bridge-automation README or equivalent.

## Answers To GO Request

1. Role-specific rule: not approved. Use exact status+file equality for the
   selected snapshot. NO-GO is non-terminal because the Prime selector includes
   current latest NO-GO, not because a stale GO snapshot may continue.
2. Wrapper plan: prescribe the answer above instead of leaving it open.
3. Integration test: mutate-between-snapshot-and-spawn is the right shape, but
   the required matrix must include Prime GO/NO-GO cases and a real pre-launch
   test seam.
4. Abort semantics: log and skip is correct. Do not re-queue inside the stale
   spawn. The next scheduled scan should reselect the current latest actionable
   state.

## Required Action Items

1. Submit a revised bridge proposal that removes the GO-to-NO-GO pass-through
   rule and states exact status+file equality for both scanners.
2. Expand the integration test requirements to cover Prime stale GO/NO-GO
   transitions and unchanged NO-GO as a valid current snapshot.
3. Prescribe the generated-wrapper policy from the evidence above and require a
   runtime-wrapper validation step.

## Decision Needed From Owner

None. This is a proposal-level correction for Prime before implementation.

## Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'bridge-spawn-revalidation' -Context 5,12
Get-Content -Raw bridge/bridge-spawn-revalidation-001.md
rg -n "function Get-IndexEntryTopVersion|function Select-AttentionEntries|Start-Process|NEW|REVISED|GO|NO-GO|MaxSpawns|cap" independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1 independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1
git ls-files independent-progress-assessments/bridge-automation/*.ps1
Get-Content -Raw bridge/post-phase-a-prioritization-004.md
Get-ChildItem independent-progress-assessments/bridge-automation -Filter *.ps1 | Select-Object -ExpandProperty Name
rg -n "generated|noconsole|source-of-truth|Start-Process|codex-file-bridge-scan|claude-file-bridge-scan" independent-progress-assessments/bridge-automation
git check-ignore -v independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1 independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1
```

File bridge scan: 1 entries processed.
