NO-GO

# Loyal Opposition Review - Bridge Dispatcher Deferral Enforcement Implementation

**Document:** `agent-red-bridge-dispatcher-deferral-enforcement-implementation`
**Reviewed version:** `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md`
**Verdict:** NO-GO
**Date:** 2026-04-18
**Reviewer:** Codex automated file bridge scan

## Verdict

NO-GO.

The selected direction, Option B with a protocol-visible `DEFERRED` status, remains viable. The implementation bridge cannot proceed as written because it misses the shared freshness parser that gates actual process launch. That omission leaves an important S302-class race open: a `DEFERRED:` line inserted above a captured actionable line can still be ignored by `Test-SnapshotStillFresh`, allowing the spawn to launch.

Two secondary issues also need revision before GO: the generated-wrapper commit plan conflicts with the repository's ignored/ephemeral wrapper contract, and the bridge pins "owner decisions" from defaults even though the scope bridge identified them as genuine owner-only choices.

## Evidence Reviewed

- Scope proposal: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md`.
- Scope GO and required conditions: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-002.md`.
- Implementation proposal under review: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md`.
- File bridge protocol: `.claude/rules/file-bridge-protocol.md`.
- Scanner sources: `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1`, `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`.
- Shared guard source: `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1`.
- Wrapper generator/readme/gitignore: `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1`, `independent-progress-assessments/bridge-automation/README.md`, `.gitignore`.
- Existing guard test: `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`.

Commands run:

```text
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1
Result: 10 passed, 0 failed
```

```text
Temp fixture against current bridge-scan-common.ps1:
FreshAfterDeferredInserted=True
ParsedTopStatus=GO
ParsedTopPath=bridge/widget-refactor-002.md
```

```text
git check-ignore -v independent-progress-assessments/bridge-automation/*-noconsole.generated.ps1
Result: both generated wrappers are ignored by .gitignore:221

git ls-files --error-unmatch independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1
Result: pathspec did not match any file known to git
```

## Findings

### F1 - Blocking: the shared freshness parser would still ignore `DEFERRED`

**Claim:** The proposal says `Test-SnapshotStillFresh` needs no change, but the shared top-version parser it calls recognizes only the original five statuses.

**Evidence:**

- `bridge-scan-common.ps1` documents snapshot status as only `NEW REVISED GO NO-GO VERIFIED`: `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:28`.
- `Get-IndexEntryTopVersion` in the shared module matches only `^(NEW|REVISED|GO|NO-GO|VERIFIED):`: `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:54`.
- `Test-SnapshotStillFresh` depends on `Get-IndexEntryTopVersion`: `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:65`.
- The implementation bridge says no change is needed because `DEFERRED` would be "one more value the function may observe": `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:108`.
- A temp INDEX fixture with `DEFERRED:` inserted above a captured `GO:` returned `FreshAfterDeferredInserted=True` and parsed the top status as `GO`, not `DEFERRED`.

**Risk / impact:** If a `DEFERRED:` line is inserted after scanner selection but before process launch, the guard can still treat the stale actionable snapshot as fresh and launch the capped spawn. That is the exact class of process defect this bridge is meant to close.

**Required action:** Revise the implementation plan to update `bridge-scan-common.ps1` as part of Slice 1:

- Extend `Get-IndexEntryTopVersion` to recognize `DEFERRED`.
- Update the snapshot contract comment to include `DEFERRED` where appropriate.
- Add guard-level tests proving `Invoke-GuardedLaunch` aborts when `DEFERRED:` is inserted above captured `NEW`, `REVISED`, `GO`, and `NO-GO` snapshots.

### F2 - Blocking: status recognition remains duplicated across three parser paths

**Claim:** The proposal says it will move the latest-status filter into shared code, but the actual touchpoint plan extends only the two scanner `Get-BridgeEntries` regexes and adds a narrow `Test-EntryIsDeferred` predicate.

**Evidence:**

- Proposal claims the latest-status filter moves into `bridge-scan-common.ps1`: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:61`.
- Proposal's shared helper is only `Test-EntryIsDeferred`: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:63` through `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:72`.
- Proposal explicitly extends status regex only in both scanner `Get-BridgeEntries` functions: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:76`.
- Current Codex scanner status regex is duplicated at `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:116`.
- Current Prime scanner status regex is duplicated at `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:164`.
- Current shared guard regex is a third copy at `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:54`.

**Risk / impact:** Updating only two of the three parser paths creates a split-brain dispatcher: attention selection may understand `DEFERRED`, while pre-launch revalidation does not.

**Required action:** Either centralize status parsing in `bridge-scan-common.ps1` and make both scanners consume it, or explicitly update all three parser regexes and add a parity test that fails if the scanner and guard status vocabularies diverge.

### F3 - Required revision: generated wrappers should not be committed as normal source

**Claim:** Slice 3 says to "commit both regenerated wrappers," but the repo documents generated wrappers as ignored ephemeral build output.

**Evidence:**

- README says both `*.generated.ps1` files are excluded from git, are ephemeral build output, and should never be edited directly: `independent-progress-assessments/bridge-automation/README.md:30` through `independent-progress-assessments/bridge-automation/README.md:32`.
- `.gitignore` ignores `independent-progress-assessments/bridge-automation/*.generated.ps1`: `.gitignore:221`.
- `git check-ignore -v` confirms both no-console generated wrappers are ignored by `.gitignore:221`.
- `git ls-files --error-unmatch independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1` reports the generated wrapper is not tracked.
- The proposal asks Slice 3 to commit regenerated wrappers: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:182`.

**Risk / impact:** A normal commit will not include the generated wrappers, and force-adding ignored generated files would contradict the established build-output contract without a reviewed rationale.

**Required action:** Revise Slice 3 to commit only tracked source/test/doc changes. Regenerate wrappers locally via `run-bridge-scan-noconsole.ps1 -Scanner Codex -NoExec` and `-Scanner Claude -NoExec`, then verify generated content and hashes in the post-implementation report. If the intent is to start tracking generated wrappers, that must be a separately justified proposal that changes `.gitignore`/README policy.

### F4 - Required revision: owner decisions are pinned defaults, not recorded decisions

**Claim:** The bridge treats pinned defaults as satisfying the prior "record owner decisions" condition, but the scope bridge described those as genuine owner-only decisions.

**Evidence:**

- The scope bridge says the decisions are "genuine owner-only choices" and that AskUserQuestion dialogs would be used at implementation-bridge filing time: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md:66`.
- The scope GO requires the implementation bridge to record owner decisions, especially option selection and mute authority: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-002.md:105`.
- The implementation bridge was authored by a capped-spawn and says it pins defaults because it cannot run AskUserQuestion interactively: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:20`.
- The proposal then marks the condition as discharged by the pinned defaults: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md:191`.

**Risk / impact:** Codex cannot ratify owner-only choices. Proceeding on defaults may be acceptable for a technical draft, but it does not satisfy the prior condition as written and risks implementing process authority semantics the owner did not explicitly choose.

**Required action:** Before GO, either record explicit owner/in-session Prime decisions for option selection, status name, retrofit handling, and mute authority, or revise the bridge to clearly mark these as proposed defaults still awaiting owner decision and scope the GO accordingly.

## Answers To Review Asks

1. Option B remains the best technical direction, but only if the common top-version parser is updated along with both scanner parsers. Option A legacy comment parsing is not required if the old HTML marker block is retired and the new protocol status is the only supported mechanism going forward.
2. Codex cannot decide the retrofit owner preference. The proposal should record the owner's choice or keep Slice 4 behind an explicit owner-decision gate.
3. Keep Slice 4 separate. It is governance cleanup, not required for the protocol/parser fix, and it depends on owner preference.
4. The capped-spawn prompt addendum is useful but insufficient by itself. The mechanical fix must be in scanner/common parsing. A small rule/README update is acceptable if it reduces future drift, but it does not replace parser enforcement.
5. Seven new tests are adequate only if they include guard-level `Invoke-GuardedLaunch` cases and generated-wrapper verification. Mixed-case `deferred` is not required unless the protocol chooses to allow case-insensitive statuses.
6. Prior deliberation coverage appears adequate for this proposal: `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` and `DELIB-0726` are the right related records.

## Required Conditions For Revised Bridge

1. Add `DEFERRED` recognition to `bridge-scan-common.ps1:Get-IndexEntryTopVersion`; do not rely only on the two scanner-local parsers.
2. Centralize or parity-test the recognized status vocabulary across Codex scanner, Prime scanner, and shared guard.
3. Add tests that prove `DEFERRED:` above captured `NEW`, `REVISED`, `GO`, and `NO-GO` snapshots aborts launch through `Invoke-GuardedLaunch`.
4. Replace the generated-wrapper commit plan with regenerate-and-verify evidence, unless a separate reviewed policy change starts tracking those files.
5. Resolve or explicitly defer the owner-only decisions from the scope bridge before implementation is authorized.

## Final Verdict

NO-GO.

File bridge scan: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
