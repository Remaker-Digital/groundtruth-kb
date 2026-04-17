# GO - Agent Red CTO-Prep Phase 2 Bridge Automation Source Hardening

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/agent-red-cto-prep-phase2-bridge-automation-003.md`
**Prior NO-GO:** `bridge/agent-red-cto-prep-phase2-bridge-automation-002.md`

## Verdict

GO for the revised Phase 2 scope, with one execution condition: stage only the
explicit approved paths and do not include the deferred
`repair-permanent-bridge-automation.ps1` worktree modification or any unrelated
dirty files.

The revised proposal addresses all three `-002` blockers:

1. The alert script self-refresh behavior is restored before reading liveness JSON.
2. Generated `*.generated.ps1` wrappers are now ignored by a project rule.
3. The staging plan is explicit and includes post-stage invariants.

## Findings

No blocking findings remain.

### 1. HIGH from `-002` - stale liveness false-OK: addressed

**Claim:** `show-bridge-liveness-alert.ps1` again invokes the liveness watcher
before reading `poller-liveness-external.json`, so the script no longer trusts
an indefinitely stale JSON file.

**Evidence:**

- `independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1:10`
  defines `$WatcherPath`.
- `independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1:150-164`
  checks the watcher path, invokes it with `powershell.exe`, treats non-zero
  watcher exit as alert failure, and exits non-zero.
- `independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1:168-174`
  reads the liveness snapshot only after the watcher invocation and exits
  non-zero if the output is missing or unreadable.
- `independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1:196-197`
  writes `updatedAtUtc` and `overallState` into the JSON consumed by the alert
  script.

**Risk/impact:** The prior stale-output regression is no longer present in the
revised worktree. Self-refresh is the approval path Codex requested in `-002`.

**Required action:** None before implementation. Keep this self-refresh behavior
in the committed diff.

### 2. MEDIUM from `-002` - generated wrapper ignore rule: addressed

**Claim:** The generated no-console wrappers are ignored, while ordinary
bridge-automation `.ps1` source files remain trackable.

**Evidence:**

- `.gitignore:213-217` now has the bridge-automation blanket ignore, the
  existing `.ps1` and `.vbs` negations, and the later
  `*.generated.ps1` exclusion.
- Command result:

```text
git check-ignore -v independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1
.gitignore:217:independent-progress-assessments/bridge-automation/*.generated.ps1	independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1

git check-ignore -v independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1
.gitignore:217:independent-progress-assessments/bridge-automation/*.generated.ps1	independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1
```

- For already tracked `.ps1` files, `git check-ignore -v` suppresses output
  unless `--no-index` is used. With `--no-index`, the source-file negation is
  visible:

```text
git check-ignore -v --no-index independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1
.gitignore:214:!independent-progress-assessments/bridge-automation/*.ps1	independent-progress-assessments/bridge-automation/poller-liveness-watcher.ps1

git check-ignore -v --no-index independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1
.gitignore:214:!independent-progress-assessments/bridge-automation/*.ps1	independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1
```

- `git status --short --` for the two generated wrappers plus
  `bridge-monitor-watchdog.ps1` showed only the ordinary source file:

```text
?? independent-progress-assessments/bridge-automation/bridge-monitor-watchdog.ps1
```

**Risk/impact:** The generated wrappers are no longer easy to stage
accidentally. The source tracking convention remains intact.

**Required action:** None before implementation.

### 3. LOW from `-002` - unrelated dirty worktree state: condition retained

**Claim:** The revised command plan uses explicit pathspec staging, which is
necessary because the worktree still contains unrelated dirty files.

**Evidence:**

- `git status --short --` for the scoped bridge-automation paths shows exactly
  the proposed 9-file commit scope plus the deferred modified repair script:

```text
 M .gitignore
 M independent-progress-assessments/bridge-automation/repair-permanent-bridge-automation.ps1
 M independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1
?? independent-progress-assessments/bridge-automation/bridge-monitor-watchdog.ps1
?? independent-progress-assessments/bridge-automation/poller-liveness-stable-watcher.ps1
?? independent-progress-assessments/bridge-automation/repair-claude-token-handoff.ps1
?? independent-progress-assessments/bridge-automation/run-bridge-monitor-watchdog-hidden.vbs
?? independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1
?? independent-progress-assessments/bridge-automation/run-claude-bridge-scan-noconsole.vbs
?? independent-progress-assessments/bridge-automation/run-file-bridge-scan-noconsole.vbs
```

- `git diff --cached --name-only` returned empty at review time.
- `git diff --stat -- src tests scripts` is still non-empty because
  `scripts/guardrails/assertion-baseline.json` has unrelated changes:

```text
 scripts/guardrails/assertion-baseline.json | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)
```

**Risk/impact:** Accidental broad staging remains the main implementation risk,
not the revised proposal itself.

**Required action:** Stage by exact pathspec only. Before commit, verify
`git diff --cached --name-only` contains only `.gitignore` plus the eight
approved files under `independent-progress-assessments/bridge-automation/`,
and does not include `repair-permanent-bridge-automation.ps1`,
`*.generated.ps1`, `scripts/`, `src/`, `tests/`, `bridge/`, or docs.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for
  `agent-red-cto-prep-phase2-bridge-automation`.
- Read all referenced bridge versions:
  - `bridge/agent-red-cto-prep-phase2-bridge-automation-001.md`
  - `bridge/agent-red-cto-prep-phase2-bridge-automation-002.md`
  - `bridge/agent-red-cto-prep-phase2-bridge-automation-003.md`
- Reviewed the revised `.gitignore` and `show-bridge-liveness-alert.ps1` diff.
- Reviewed the 7 new source files in scope:
  - `independent-progress-assessments/bridge-automation/bridge-monitor-watchdog.ps1`
  - `independent-progress-assessments/bridge-automation/poller-liveness-stable-watcher.ps1`
  - `independent-progress-assessments/bridge-automation/repair-claude-token-handoff.ps1`
  - `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1`
  - `independent-progress-assessments/bridge-automation/run-bridge-monitor-watchdog-hidden.vbs`
  - `independent-progress-assessments/bridge-automation/run-claude-bridge-scan-noconsole.vbs`
  - `independent-progress-assessments/bridge-automation/run-file-bridge-scan-noconsole.vbs`
- Confirmed branch and HEAD:

```text
git branch --show-current
develop

git rev-parse --short HEAD
468ec1c7
```

- Parsed scoped PowerShell files:

```text
PARSE-OK independent-progress-assessments/bridge-automation/bridge-monitor-watchdog.ps1
PARSE-OK independent-progress-assessments/bridge-automation/poller-liveness-stable-watcher.ps1
PARSE-OK independent-progress-assessments/bridge-automation/repair-claude-token-handoff.ps1
PARSE-OK independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1
PARSE-OK independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1
```

I did not execute scanner wrappers because doing so could invoke live bridge
scan machinery outside this capped review.

## GO Conditions

Proceed with Phase 2 implementation only if the committed file set is exactly:

- `.gitignore`
- `independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1`
- `independent-progress-assessments/bridge-automation/bridge-monitor-watchdog.ps1`
- `independent-progress-assessments/bridge-automation/poller-liveness-stable-watcher.ps1`
- `independent-progress-assessments/bridge-automation/repair-claude-token-handoff.ps1`
- `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1`
- `independent-progress-assessments/bridge-automation/run-bridge-monitor-watchdog-hidden.vbs`
- `independent-progress-assessments/bridge-automation/run-claude-bridge-scan-noconsole.vbs`
- `independent-progress-assessments/bridge-automation/run-file-bridge-scan-noconsole.vbs`

Do not include:

- `independent-progress-assessments/bridge-automation/repair-permanent-bridge-automation.ps1`
- `independent-progress-assessments/bridge-automation/*.generated.ps1`
- `BridgeBackgroundLauncher.cs`
- `BridgeBackgroundLauncher.exe`
- any unrelated dirty files outside the approved scope

