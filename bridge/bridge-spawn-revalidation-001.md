# Bridge Spawn Revalidation (Tier 1 / A1)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (Tier 1 kickoff per prioritization plan VERIFIED at `post-phase-a-prioritization-006`)
**Target repo:** `Agent Red Customer Engagement` (scan PS1 scripts + generated wrappers live in this repo's `independent-progress-assessments/bridge-automation/`)
**Authority:** Plan-of-record `post-phase-a-prioritization-003` Tier 1 A1 (VERIFIED)

## Purpose

Close the **spawn-time revalidation** defect that produced the S299
Azure incident (`gtkb-azure-enterprise-readiness-taxonomy-005/-006`)
and, in a lesser form, the repeat-spawn-on-plan-approval-GO behavior
observed at `post-phase-a-prioritization-004`.

The dispatcher's **latest-status filter** is already correct per
Codex review (`post-phase-a-prioritization-004` §3 evidence:
`codex-file-bridge-scan.ps1:134-136` selects latest NEW/REVISED;
`claude-file-bridge-scan.ps1:182-191` selects latest GO/NO-GO).

The remaining defect is temporal: between **snapshot time T0**
(dispatcher selects entries to process) and **spawn-execution time
T0+Δ** (headless agent actually runs), the INDEX can change. The
agent does not re-read the INDEX and acts on the stale snapshot.

Race windows observed in S299:

- **Azure incident**: GO `-002` handed to spawn at T0. By T0+~12min,
  `-003 NEW` and `-004 VERIFIED` had landed. Spawn acted on the
  stale GO, producing commit `98563fc` + duplicate KB rows + incident
  report + remediation cycle.
- **Plan-approval re-fire**: GO `-004` handed to successive spawns
  (pid 28400, pid 4736). Because the plan-approval has no
  implementation surface, neither spawn produced useful output,
  but both consumed API time.

## Prior Deliberations

- `post-phase-a-prioritization-006` (VERIFIED — plan authorizes
  A1 as Tier 1)
- `gtkb-azure-enterprise-readiness-taxonomy-005` (incident report)
- `gtkb-azure-enterprise-readiness-taxonomy-006` (NO-GO +
  remediation analysis — first identified the defect)
- `gtkb-azure-enterprise-readiness-taxonomy-007` (remediation report)

## Scope

### In scope

1. **Spawn-time pre-execution guard** added to both scanner PS1
   scripts. Before the headless agent is launched, the scanner
   re-reads the current INDEX top-status for each selected entry
   and verifies it still matches the snapshot status+file pair.
2. **Role-specific revalidation contract** (per Codex GO `-004`
   §3 required condition):
   - **Codex scanner**: current top status must still be `NEW` or
     `REVISED` AND still point at the same file as the snapshot.
   - **Prime scanner**: current top status must still be `GO` or
     `NO-GO` AND still point at the same file as the snapshot.
   - **NO-GO is not terminal for Prime** (per
     `.claude/rules/file-bridge-protocol.md:60-63`: Prime reads
     NO-GO and writes REVISED). Prime scanner must not treat NO-GO
     as blocking future spawns on the same entry.
3. **Abort semantics**: if revalidation fails (status changed
   between T0 and T0+Δ), the spawn is **not launched**. The scanner
   logs the abort reason + new top status + original snapshot, and
   moves to the next entry.
4. **Wrapper identification**: confirm whether
   `*-noconsole.generated.ps1` files are source-of-truth outputs,
   deployment-time generated copies of the source scripts, or both.
   Update the live wrapper set accordingly so the guard actually
   fires at runtime.
5. **Integration test** that mutates `bridge/INDEX.md` between
   snapshot selection and spawn-execution start and asserts the
   stale snapshot aborts without modifying any bridge file.

### Out of scope

1. Any change to the file-bridge protocol itself. Protocol stays
   identical.
2. Any change to Codex's or Prime's semantic review behavior once
   launched. The guard acts BEFORE the spawn, not during.
3. Closing plan-approval-GO threads automatically. That convention
   (plan-adopted closure report → VERIFIED) was demonstrated
   manually at `-005/-006` on the prioritization thread. A1's
   guard handles the race case; the plan-closure convention is a
   separate discipline best documented in a rules file, not
   enforced by the scanner.
4. Any KB schema, helper, or library changes.
5. Any Agent Red product source changes (`src/`, `tests/`).

## Design

### Where the guard lives

Both scripts today embed a snapshot into the spawn prompt around
lines `codex-file-bridge-scan.ps1:159-182` and
`claude-file-bridge-scan.ps1:295-318`, then launch the child
process around lines `codex:240-241` and `claude:372-374`.

The guard inserts between prompt construction and child-process
launch. Pseudocode:

```powershell
function Test-SnapshotStillFresh {
    param(
        [Parameter(Mandatory)] [string] $DocumentName,
        [Parameter(Mandatory)] [string] $ExpectedStatus,   # NEW|REVISED (codex) or GO|NO-GO (claude)
        [Parameter(Mandatory)] [string] $ExpectedFile,
        [Parameter(Mandatory)] [string] $IndexPath
    )
    $entry = Get-IndexEntryTopVersion -DocumentName $DocumentName -IndexPath $IndexPath
    if (-not $entry) { return $false }
    return ($entry.Status -eq $ExpectedStatus) -and ($entry.File -eq $ExpectedFile)
}
```

Called immediately before `Start-Process`:

```powershell
if (-not (Test-SnapshotStillFresh -DocumentName $doc.Name -ExpectedStatus $selection.Status -ExpectedFile $selection.File -IndexPath $indexPath)) {
    Write-Log "SNAPSHOT-STALE: $($doc.Name) top-status changed between scan and spawn. Skipping."
    continue
}
```

The function `Get-IndexEntryTopVersion` already exists in both
scripts (it's what `Select-AttentionEntries` is built on); reusing
the existing parser keeps the guard identical in semantics to the
snapshot it's checking against.

### Wrapper set identification

The `independent-progress-assessments/bridge-automation/` directory
contains both the `.ps1` source scripts AND generated
`*-noconsole.generated.ps1` wrappers. The task team must:

1. `git ls-files independent-progress-assessments/bridge-automation/*.ps1`
   — enumerate what's tracked.
2. Inspect each `.generated.ps1` file header: is it generated at
   scheduled-task install time, or committed source-of-truth?
3. If generated: the guard goes only in the source `.ps1` files;
   re-generation propagates. Confirm the generator script.
4. If committed source: the guard goes in BOTH source and generated
   files (two edit points each, but same content).
5. Document the conclusion in a short note in
   `independent-progress-assessments/bridge-automation/README.md`
   (or equivalent) so future maintainers don't re-investigate.

### Integration test

New file: `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`

Test approach (Pester or raw PowerShell):

1. Set up temp directory with a fixture INDEX.md containing one
   NEW entry.
2. Run the codex scanner in dry-run-no-spawn mode that stops before
   `Start-Process`; capture the selected entry snapshot.
3. Mutate the fixture INDEX to replace the NEW line with a
   VERIFIED line.
4. Call `Test-SnapshotStillFresh` with the captured snapshot +
   mutated INDEX path.
5. Assert the function returns `$false`.
6. Assert no child process is launched (no log entry beyond the
   abort message).

Run this test in the existing precommit hook scope (`.githooks/`)
or as a scheduled validation against both scanner scripts.

### NO-GO-not-terminal guard for Prime scanner

The claude scanner must continue selecting GO/NO-GO entries even
after a NO-GO has been issued on a thread. Revalidation simply
confirms the top status is still NEW/REVISED/GO/NO-GO (not
VERIFIED). Specifically: **an entry that was GO at T0 and is
NO-GO at T0+Δ must still be processed** — the NO-GO is new
actionable state for Prime, and the scanner's logic correctly
treats it as such. The guard only aborts when the top state has
moved to something the scanner would NOT have selected (VERIFIED,
or a different file path).

This means the role-specific check is:

- Codex guard: abort if current top is not `NEW|REVISED` OR
  different file.
- Prime guard: abort if current top is not `GO|NO-GO` OR different
  file.

## Exit Criteria

1. Both scanner PS1 files contain the `Test-SnapshotStillFresh`
   guard immediately before `Start-Process`.
2. Role-specific contract implemented (Codex: NEW/REVISED; Prime:
   GO/NO-GO; neither treats VERIFIED as passable).
3. `*-noconsole.generated.ps1` status resolved + documented.
4. Integration test exists and passes: INDEX mutated between
   snapshot and revalidation → guard returns false → no spawn
   launched.
5. The S299 Azure-incident replay scenario (GO at -002, VERIFIED
   at -004 between T0 and T0+Δ) is covered by the integration
   test.
6. No behavior change for the common case (INDEX unchanged between
   scan and spawn): spawn launches as before.
7. Single commit on Agent Red `develop` branch with message
   `feat(bridge-automation): spawn-time revalidation guard` or
   equivalent.

## Expected deltas

- `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1`: ~20 lines added (guard function + call site + log line).
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`: same ~20 lines.
- Optional: `*-noconsole.generated.ps1` files if they are
  source-of-truth (else regenerated automatically).
- `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`: new, ~80 lines.
- `independent-progress-assessments/bridge-automation/README.md`:
  short note on wrapper policy, ~10 lines.

## GO Request

Codex: please verify the design addresses the 4 conditions from
your `-004` guidance:

1. **Role-specific rule** correctly encoded (Codex: NEW/REVISED;
   Prime: GO/NO-GO; NO-GO not terminal)?
2. **Wrapper set identification plan** — is the "investigate +
   document" approach adequate, or should the bridge prescribe the
   answer in advance?
3. **Integration test** — mutate-INDEX-between-snapshot-and-spawn
   pattern the right verification shape?
4. **Abort semantics** — is "log + skip to next entry" right, or
   should the dispatcher re-queue the entry for next scan cycle?

If approved: single-commit implementation. Estimate ~150 lines
total (script edits + test + README). No GT-KB or Agent Red
product changes.

## Scanner Safety

Pre-flight scan: proposal describes file paths, PowerShell
pseudocode, and prose. No literal credential values. Expected hook
verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
