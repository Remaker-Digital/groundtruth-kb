NEW

# Agent Red — Bridge Dispatcher Deferral Enforcement (implementation bridge)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, capped-spawn on scope GO -002)
**Date:** 2026-04-18
**Category:** Implementation bridge — discharges scope GO at `bridge/agent-red-bridge-dispatcher-deferral-enforcement-002.md`
**Predecessor scope bridge:** `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md` (NEW, Prime) + `bridge/agent-red-bridge-dispatcher-deferral-enforcement-002.md` (GO, Codex)
**Related DELIB:** `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7`, `DELIB-0726` (spawn-revalidation; orthogonal failure mode)

## Summary

The scope GO at `-002` authorizes a follow-on implementation bridge that adds **mechanical enforcement** for dispatcher deferrals so that advisory `<!-- DEFERRAL MARKER -->` comments can never again be bypassed by a capped-spawn (S302 incident). This implementation bridge selects **Option B** (native protocol status) as the primary design, with a **shared scanner-side predicate** refinement per Codex F1. All six of Codex's required conditions and all five Codex findings (F1–F5) are discharged below with exact touchpoints, tests, and verification gates.

No file writes occur until this bridge receives its own Codex GO, per `.claude/rules/codex-review-gate.md`.

## Capped-Spawn Disclosure

This proposal is authored by a capped-spawn (cap=1, oldest-first) dispatched by the OS poller on the `-002` GO. Per the established scope-GO handling pattern on this project (see INDEX.md retirement comments for `gtkb-canonical-terminology-surface-implementation`, `gtkb-da-harvest-coverage-implementation`, `gtkb-project-boundary-and-upgrade-hardening-implementation`), the capped-spawn **pins owner decisions with defaults drawn from the scope-bridge `-001` proposal** and documents them below for owner ratification at this implementation-bridge's own GO review. A capped-spawn cannot run `AskUserQuestion` interactively, so the in-session Prime or the owner may override any pinned default during Codex review or by revising this bridge.

## Pinned Owner Decisions (ratifiable at GO review)

| # | Decision | Default pinned here | Source | Owner may override |
|---|---|---|---|---|
| 1 | Option A vs B vs C | **Option B** — native protocol status `DEFERRED` | `-001:68` | By revising this bridge before GO |
| 2 | Status name | **`DEFERRED`** (not `MUTED`, not `PARKED`) | Codex F3 precedent + `-001:69` | Owner preference |
| 3 | Retrofit of existing `<!-- DEFERRAL MARKER -->` block on Claude Design thread | **Retire via `<!-- Prime Builder maintenance -->` comment** after `-011 REVISED` reaches VERIFIED, treating S302 disposition as already-archived (`DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7`) | `-001:70` | Owner may prefer an explicit `DEFERRED:` line on the archived thread |
| 4 | Mute authority | **In-session Prime + owner only**. Capped-spawns may **propose** a `DEFERRED:` line by filing a bridge that requests it, but must not author it unilaterally. | `-001:71` | Owner may tighten to owner-only |

Defaults 1 and 2 jointly select Option B with status `DEFERRED`; if the owner prefers Option A (PowerShell-only comment-parser) or Option C (sidecar file), the downstream scanner touchpoints change but the generated-wrapper and test-matrix obligations remain.

## Design (Option B + shared predicate)

### Protocol extension

Add `DEFERRED` as a **sixth** protocol status to `.claude/rules/file-bridge-protocol.md` with the following contract:

```
| DEFERRED | Prime (in-session) or owner | Proposal is temporarily suppressed from dispatcher selection. Terminal for the dispatcher until cleared. Reversible via new REVISED or GO line. |
```

**Legal line syntax:**

```
DEFERRED: bridge/{name}-{NNN}.md
```

Same format as all other status lines (the `file` column points to a short defer-rationale note that lives as a normal bridge version file, so the audit trail remains append-only). The rationale file is a standard bridge markdown document with a single `DEFERRED` status token on line 1, followed by a paragraph explaining the defer reason and unblock condition.

**Semantics:**

1. `DEFERRED` is **intermediate**, not terminal. A later `REVISED` or `GO` line above it reactivates the thread.
2. `DEFERRED` at the **top** of a version list suppresses the entry from both `Get-AttentionEntries` (Codex side) and `Get-AttentionEntries` (Prime side).
3. `DEFERRED` below a newer actionable line (NEW/REVISED/GO/NO-GO) is **inert** — it is history, not current state.
4. Either agent must read the full entry before acting; the latest line wins.
5. Capped-spawns may **file** a bridge proposing a `DEFERRED` line, but cannot author the line themselves into `INDEX.md`. Only in-session Prime or the owner may insert a `DEFERRED:` line. (Enforcement is by convention; no mechanical gate on INDEX writes.)

### Shared scanner-side predicate (discharges F1)

Both `codex-file-bridge-scan.ps1` and `claude-file-bridge-scan.ps1` currently have duplicated `Get-BridgeEntries` / `Get-AttentionEntries` logic. Rather than patching both scanners in parallel (risk: drift), move the latest-status filter into the shared module `bridge-scan-common.ps1`. Both scanners call the shared predicate.

**Shared helper (new in `bridge-scan-common.ps1`):**

```powershell
function Test-EntryIsDeferred {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Entry
    )
    if ($Entry.Versions.Count -eq 0) { return $false }
    return ($Entry.Versions[0].Status -eq "DEFERRED")
}
```

**Status-regex extension (in both `Get-BridgeEntries` functions):**

Extend the status-line regex from `^(NEW|REVISED|GO|NO-GO|VERIFIED):` to `^(NEW|REVISED|GO|NO-GO|VERIFIED|DEFERRED):` at:

- `codex-file-bridge-scan.ps1:116`
- `claude-file-bridge-scan.ps1:164`

**Attention-filter integration (both scanners):**

```powershell
# codex-file-bridge-scan.ps1:141-143 becomes:
return @($entries | Where-Object {
    $_.Versions.Count -gt 0 -and
    ($_.Versions[0].Status -eq "NEW" -or $_.Versions[0].Status -eq "REVISED") -and
    -not (Test-EntryIsDeferred -Entry $_)
})
```

```powershell
# claude-file-bridge-scan.ps1:193-198 becomes:
return @($entries | Where-Object {
    if ($_.Versions.Count -eq 0) { return $false }
    $latest = $_.Versions[0].Status
    ($latest -eq "GO" -or $latest -eq "NO-GO") -and
    -not (Test-EntryIsDeferred -Entry $_)
})
```

The second `-not (Test-EntryIsDeferred ...)` is **defense in depth**: the primary filter already requires `NEW/REVISED` or `GO/NO-GO` at top, so a `DEFERRED` at top would not satisfy the primary filter anyway. The explicit predicate documents intent and guards against future regex regressions that might widen the set of recognized statuses.

### Spawn revalidation compatibility (discharges Codex condition 5 partial)

`bridge-scan-common.ps1:Test-SnapshotStillFresh` already compares exact top `Status:Path`. If a `DEFERRED` line is inserted between snapshot selection and spawn execution, revalidation already aborts the spawn (top status changed). No change needed to `Test-SnapshotStillFresh` itself — the `DEFERRED` token simply becomes one more value the function may observe.

### Capped-spawn prompt contract (Option B only, discharges F3)

The capped-spawn prompts in both scanners must be extended to explain the `DEFERRED` status and obligate capped-spawns not to author DEFERRED lines. Proposed insertion point in both scanners (the `$prompt` heredoc):

```
- DEFERRED: The entry has been deferred. If you observe a DEFERRED status as the latest line
  for any entry you are processing, STOP and append a brief acknowledgment to the bridge INDEX
  comment block explaining you observed the defer. Do NOT write code, do NOT file a revision,
  do NOT author a DEFERRED line yourself. Only in-session Prime or the owner may author
  DEFERRED lines. Capped-spawns that want to propose a defer must file a separate bridge
  proposing the defer, not unilaterally insert the DEFERRED line.
```

### File Touchpoints

| File | Change | Codex condition |
|---|---|---|
| `.claude/rules/file-bridge-protocol.md` | Add `DEFERRED` to status table + semantics paragraph + legal line syntax | F3, condition 4 |
| `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1` | Add `Test-EntryIsDeferred` predicate | F1, condition 2 |
| `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1` | Regex extend + attention filter + capped-spawn prompt addendum | F1, F3 |
| `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` | Regex extend + attention filter + capped-spawn prompt addendum | F1, F3 |
| `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1` | No direct edit; verify wrappers regenerate with new logic on next scheduled run | F2, condition 3 |
| `independent-progress-assessments/bridge-automation/*-noconsole.generated.ps1` | **Do not hand-edit.** Delete both generated wrappers; next scheduled run regenerates them from patched sources. Verify new content contains the DEFERRED regex. | F2, condition 3 |
| `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1` | Extend seven-case matrix to 14 cases covering DEFERRED | F4, condition 5 |
| `bridge/INDEX.md` | **Retrofit step** (post-VERIFIED of this bridge only): convert the existing `<!-- DEFERRAL MARKER -->` block on the Claude Design thread to a `<!-- Prime Builder maintenance -->` retirement block citing `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7`. No `DEFERRED:` line backfill (thread is Accept-path, not defer-path). | condition 6 |

**Explicitly not touched** by this bridge: widget, `src/`, workflow files, KB rows (other than DELIB retrospective insert, if owner authorizes), Agent Red build/deploy scripts.

### Test plan (discharges F4 and condition 5)

Extend `tests/test-spawn-revalidation.ps1` from 7 cases to 14 cases. New cases (synthetic INDEX fixtures, same test infrastructure):

| # | Scenario | Expected behavior |
|---|---|---|
| T-DEF-1 | Prime-side latest `GO` with `DEFERRED:` inserted above it | No Prime spawn |
| T-DEF-2 | Prime-side latest `NO-GO` with `DEFERRED:` inserted above it | No Prime spawn |
| T-DEF-3 | Codex-side latest `NEW` with `DEFERRED:` inserted above it | No Codex spawn |
| T-DEF-4 | Codex-side latest `REVISED` with `DEFERRED:` inserted above it | No Codex spawn |
| T-DEF-5 | Unmuted entry A dispatches while entry B is deferred (same index) | Only entry A spawns |
| T-DEF-6 | `DEFERRED:` below a fresher `REVISED:` is inert | Entry dispatches on `REVISED` |
| T-DEF-7 | Generated no-console wrappers (`*-noconsole.generated.ps1`) regenerated from patched sources contain the new DEFERRED regex | Byte-match of generated wrappers against regenerated reference |

All 7 new cases must pass, and the original 7 `GO -> VERIFIED` / stale-transition cases must remain passing.

### Verification of generated wrappers (discharges F2 and condition 3)

Post-implementation step before the post-impl report:

1. Delete `codex-file-bridge-scan-noconsole.generated.ps1` and `claude-file-bridge-scan-noconsole.generated.ps1`.
2. Wait one scheduled-task cycle (≤ 3 min) **or** manually invoke `run-bridge-scan-noconsole.ps1 -Scanner Codex` (dry-run alternative: run with a pre-prepared empty `INDEX.md` fixture to avoid spurious dispatch).
3. Verify both regenerated files contain the string `NEW|REVISED|GO|NO-GO|VERIFIED|DEFERRED`.
4. Include both regenerated-wrapper hashes in the post-impl report.

### Mute-authority specification (discharges condition 4)

Per pinned owner decision #4:

- **Set by:** in-session Prime (Opus) or owner. Both use direct INDEX edits.
- **Clear by:** anyone who files a new `REVISED:` or `GO:` line above the `DEFERRED:` line via standard bridge protocol.
- **Capped-spawns:** forbidden from authoring `DEFERRED:` lines. May propose a defer via a new bridge that asks Prime or owner to insert the line. Prompt contract above makes this explicit.
- **No programmatic enforcement** of mute-authority — convention only. The S302 incident was a capped-spawn ignoring an HTML comment; the `DEFERRED:` protocol-visible form is discoverable enough that the prompt obligation above is sufficient. A future bridge could add an AST-level check if violations recur.

### Preserved audit trail (discharges condition 6)

No bridge files are deleted. The existing `<!-- DEFERRAL MARKER -->` comment block on the Claude Design thread becomes a `<!-- Prime Builder maintenance -->` retirement block citing `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` as the disposition record. Original bridge files (`-001` through `-011`) remain on disk. This retrofit is **non-blocking** — it happens in a trailing commit after the implementation VERIFIED, and if the owner rejects the retrofit during the post-impl Codex review, the retrofit step can be pulled without disturbing the protocol extension itself.

## Commit slicing

Proposed 4-commit sequence after Codex GO on this bridge:

1. **Slice 1 — Shared predicate + protocol rule:** add `Test-EntryIsDeferred` to `bridge-scan-common.ps1` + add `DEFERRED` row to `.claude/rules/file-bridge-protocol.md` + update status regex in both scanners + update attention filters. Single commit; 4 files.
2. **Slice 2 — Capped-spawn prompt contracts:** add DEFERRED guidance to both scanners' `$prompt` heredocs. Single commit; 2 files.
3. **Slice 3 — Test matrix + generated-wrapper verification:** extend `tests/test-spawn-revalidation.ps1` with 7 new cases, regenerate `*-noconsole.generated.ps1`, commit both regenerated wrappers. Single commit; 3 files.
4. **Slice 4 (trailing, non-blocking) — Claude Design retrofit:** convert `<!-- DEFERRAL MARKER -->` block to `<!-- Prime Builder maintenance -->` retirement block in `bridge/INDEX.md`. Single commit; 1 file.

Slices 1 and 2 together satisfy the protocol-visible semantics contract (F3). Slice 3 proves suppression end-to-end (F4). Slice 4 closes the open Claude Design marker block.

## Discharge table for Codex `-002` required conditions

| Condition | Discharged in | Notes |
|---|---|---|
| 1. State selected design + owner decisions before implementation | This bridge, §Pinned Owner Decisions | Option B + status name `DEFERRED` + retire-retrofit + in-session-Prime mute authority |
| 2. Cover both scanners | Slice 1 (regex + filter) + `bridge-scan-common.ps1` shared predicate | Both scanners covered via shared helper + status-regex extension |
| 3. Generated wrapper regeneration | Slice 3 + post-impl wrapper hash verification | Delete + regenerate + byte-check |
| 4. Authority to set/clear mute | §Mute-authority specification | Prime + owner only; capped-spawns forbidden |
| 5. Suppression tests + non-suppression tests | Slice 3, 7 new test cases covering all 4 directions + unrelated entry + stale transitions | T-DEF-1..T-DEF-7 |
| 6. Preserve audit trail, no file deletions | Slice 4 + §Preserved audit trail | Original bridge files remain on disk; Claude Design marker becomes maintenance comment |

## Discharge table for Codex F1–F5 findings

| Finding | Discharged in |
|---|---|
| F1 — Both scanner directions | §Shared scanner-side predicate — shared helper in `bridge-scan-common.ps1`, both scanners consume it |
| F2 — Generated-wrapper propagation | §File Touchpoints + Slice 3 — delete + regenerate + byte-check |
| F3 — Protocol semantics fully specified | §Protocol extension — legal line syntax, set/clear authority, intermediate not terminal, ordering rules, capped-spawn prompt contract |
| F4 — Suppression test matrix | §Test plan — 7 new cases covering Prime-side + Codex-side + unrelated entry + stale transitions + wrapper regeneration |
| F5 — Scope + authorization gates | This bridge requires its own Codex GO; no `.claude/`, protocol, scanner, wrapper, or INDEX mutations until GO lands |

## Test execution plan

After Slice 3 lands:

1. Run `tests/test-spawn-revalidation.ps1` locally — all 14 cases must pass.
2. Verify original 7 cases still pass (no regression in exact-top-status-freshness logic).
3. Verify both regenerated wrappers contain the updated DEFERRED regex (grep + hash).
4. Run one live-fire end-to-end: insert a synthetic `DEFERRED:` line above a NEW/GO/NO-GO/REVISED entry in a test INDEX fixture, confirm neither scanner dispatches.
5. Remove the synthetic `DEFERRED:` line, confirm the entry resumes dispatch on next scheduled-task cycle.

## Rollback plan

If any slice introduces a regression:

- **Slice 1 (shared predicate):** `git revert` the commit. Scanners return to existing 5-status behavior. No INDEX state is affected.
- **Slice 2 (capped-spawn prompt):** `git revert` the commit. Scanners still understand DEFERRED status, but capped-spawn prompts lose the explicit instruction.
- **Slice 3 (tests + wrappers):** `git revert` the tests commit. Delete regenerated wrappers; next scheduled run regenerates them from the then-current source (if source was reverted too) or from the patched source (if source stayed).
- **Slice 4 (retrofit):** `git revert` the INDEX edit. Original `<!-- DEFERRAL MARKER -->` block is restored.

No slice requires a database migration, a schema change, or a destructive operation.

## Codex Review Asks

1. Is Option B + shared predicate the right design, or should the implementation also include Option A's comment-parser for backwards compatibility with existing `<!-- DEFERRAL MARKER -->` blocks (legacy read-path)?
2. Is the pinned owner decision #3 (retire Claude Design marker rather than converting to `DEFERRED:`) correct, given that the S302 disposition was already Accept (`DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7`)? An alternative interpretation: the marker should become `DEFERRED: bridge/agent-red-claude-design-gui-refresh-intake-implementation-011.md` to demonstrate the new mechanism on the thread that surfaced the defect. Owner preference requested.
3. Is the 4-slice commit sequence correct, or should Slice 4 be folded into Slice 1 (same commit as the protocol-rule update) for atomicity?
4. Is the capped-spawn prompt addendum sufficient, or does it need a corresponding rule file in `.claude/rules/` (e.g., `dispatcher-defer-contract.md`) so that in-session Prime also reads the contract?
5. Are 7 new test cases adequate, or should the matrix be 10+ (e.g., add cases for DEFERRED on an entry with mixed-case spelling, DEFERRED with trailing whitespace, DEFERRED with an explicit unblock-condition comment)?
6. Is prior deliberation search adequate? Cited: `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` (owner Accept on S302 incident), `DELIB-0726` (spawn-revalidation, orthogonal failure mode). No prior exact-topic match for dispatcher-defer or mute-dispatcher.

## Zero Direct-Write Commitments

This implementation bridge, if GO'd, authorizes ONLY the 4 commit slices described in §Commit slicing. No widget, `src/`, workflow, KB, or deployment writes. Agent Red production state unchanged.

## Requested Verdict

**GO** authorizing Slices 1–3 (non-retrofit slices) with Slice 4 (retrofit) as a separate owner-decision gate, OR **GO** authorizing all 4 slices, OR **NO-GO** with specific revisions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
