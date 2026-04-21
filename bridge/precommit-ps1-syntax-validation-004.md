# Verification: Pre-Commit PowerShell Syntax Validation

Verdict: VERIFIED

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/precommit-ps1-syntax-validation-003.md`
Prior approval: `bridge/precommit-ps1-syntax-validation-002.md`

## Claim

The implementation satisfies the approved constraints for a local pre-commit
PowerShell syntax validator. It creates new hook infrastructure, documents local
activation, parses staged `.ps1` blobs rather than worktree files, avoids a new
repo-wide CI gate, and exits before invoking PowerShell when no staged `.ps1`
files are present.

## Evidence

Created hook files are present under the new `.githooks/` directory:

```text
.githooks/pre-commit
.githooks/pre-commit-ps1-parse.ps1
.githooks/setup-hooks.sh
```

The bash pre-commit entrypoint documents the local activation command at
`.githooks/pre-commit:5`-`.githooks/pre-commit:6`, checks for staged `.ps1`
files before delegation at `.githooks/pre-commit:23`-`.githooks/pre-commit:26`,
and invokes the PowerShell validator from the repo root at
`.githooks/pre-commit:29`-`.githooks/pre-commit:31`.

The validator enumerates staged added/copied/modified `.ps1` paths at
`.githooks/pre-commit-ps1-parse.ps1:12`-`.githooks/pre-commit-ps1-parse.ps1:16`,
reads the staged blob with `git show ":$f"` at
`.githooks/pre-commit-ps1-parse.ps1:20`-`.githooks/pre-commit-ps1-parse.ps1:28`,
and parses that staged content with `Parser.ParseInput()` at
`.githooks/pre-commit-ps1-parse.ps1:30`-`.githooks/pre-commit-ps1-parse.ps1:37`.
Parse failures are collected with file and line output and exit non-zero at
`.githooks/pre-commit-ps1-parse.ps1:39`-`.githooks/pre-commit-ps1-parse.ps1:53`.

The setup helper performs the local activation command at
`.githooks/setup-hooks.sh:29` and attempts to mark the pre-commit entrypoint
executable at `.githooks/setup-hooks.sh:30`. I did not run this helper because
it would modify local `.git/config`; `git config --get core.hooksPath` currently
returns no configured value in this checkout.

Command verification:

```text
PARSE-OK: independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1
PARSE-OK: independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1
PARSE-OK: independent-progress-assessments/bridge-automation/start-bridge-scan-monitor.ps1
PARSE-OK: independent-progress-assessments/bridge-automation/watch-bridge-scan.ps1
```

Known-bad S291-style content is detected by the same parser API:

```text
DETECTED: line 2: Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to delimit the name.
DETECTED: line 2: Unexpected token '1' in expression or statement.
```

The current index has no staged files from `git diff --cached --name-only
--diff-filter=ACM`, and the hook path works when invoked through Git without
mutating config:

```text
git -c core.hooksPath=.githooks hook run pre-commit
exit code: 0
```

CI scope check found no hook/parser terms under `.github`:

```text
NO CI MATCHES for hook/parser terms under .github
```

## Findings

No blocking findings.

One non-blocking operational note: invoking `bash .githooks/pre-commit` directly
from this PowerShell environment fails because `bash` resolves to a broken WSL
shim. That does not block this verification because Git's own hook runner
successfully executed the configured hook path, and the activation command is
also documented as the direct `git config core.hooksPath .githooks` command.
A future convenience improvement could add a PowerShell-native setup helper.

## Required Actions

None.

## Owner Decision

No owner decision is required for this bridge item.
