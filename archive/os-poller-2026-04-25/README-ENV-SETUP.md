# Bridge Automation — Environment Setup

This document is a teaching-grade reference for the local environment variables
that the bridge-automation pollers need on a fresh GT-KB workstation. It exists
because `bridge/gtkb-root-directory-migration-post-verify-009.md` (the GO that
authorized this work) required that no machine-local absolute paths be embedded
in active bridge code. Setup values that are inherently machine-specific must
be supplied at runtime via environment variables, never hardcoded.

This document is part of the S307 hardcoded-path directive
(`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-24-20-35-HARDCODED-PATH-DIRECTIVE.md`).
Read that directive first if you are an adopter setting up GT-KB on a new
machine.

## Required environment variables

### `GROUNDTRUTH_KB_PATH`

**Purpose.** When a bridge item targets the upstream `groundtruth-kb`
repository (rather than the active Agent Red repository), the Codex bridge
poller (`codex-file-bridge-scan.ps1`) instructs the spawned Codex agent to
inspect that other working tree for evidence. The pollers themselves never
read `groundtruth-kb` directly; they only quote its path into the agent
prompt.

**When required.** Set this if you regularly review bridge items that
reference `groundtruth-kb` and want the bot to point Codex at a concrete
location instead of asking the owner to supply one.

**When optional.** If unset, the bridge poller still works for every
Agent-Red-targeted item. Items that mention `groundtruth-kb` will be flagged
by Codex with a request that the owner provide the path. Nothing fails; the
bot simply prompts for setup.

**How to set on Windows (PowerShell).** Pick one of:

```powershell
# Per-user persistent (recommended for individual workstations)
[Environment]::SetEnvironmentVariable("GROUNDTRUTH_KB_PATH", "E:\path\to\your\groundtruth-kb", "User")

# Per-shell session only
$env:GROUNDTRUTH_KB_PATH = "E:\path\to\your\groundtruth-kb"

# In a Windows scheduled-task action's Environment variables tab
# Variable: GROUNDTRUTH_KB_PATH
# Value:    E:\path\to\your\groundtruth-kb
```

**How to set on Bash.** Add to `~/.bashrc` or `~/.profile`:

```bash
export GROUNDTRUTH_KB_PATH="/c/path/to/your/groundtruth-kb"
```

**How to verify.**

```powershell
# Should print the configured path (no error if unset).
Write-Output "GROUNDTRUTH_KB_PATH=[$env:GROUNDTRUTH_KB_PATH]"
```

### `GTKB_PROJECT_ROOT`

**Purpose.** The Claude Code `UserPromptSubmit` hook
(`.claude/hooks/poller-freshness.py`) tries to resolve the GT-KB repo root
through several mechanisms — git superproject, git common dir, git toplevel,
and `CLAUDE_PROJECT_DIR`. If every one of those fails (rare; happens when
Claude is launched outside a git context), the hook falls back to
`GTKB_PROJECT_ROOT`. If that env var is also unset, the hook returns
`ALARM` rather than silently using a workstation-specific default.

**When required.** Set this only if you regularly invoke Claude from a
location where git resolution and `CLAUDE_PROJECT_DIR` both fail to point at
the GT-KB checkout. Most users never need to set it.

**How to set.** Same pattern as `GROUNDTRUTH_KB_PATH`:

```powershell
[Environment]::SetEnvironmentVariable("GTKB_PROJECT_ROOT", "E:\path\to\your\GT-KB", "User")
```

```bash
export GTKB_PROJECT_ROOT="/c/path/to/your/GT-KB"
```

## Why this is environment-variable-supplied, not configured in a file

The S307 hardcoded-path directive forbids embedding machine-local absolute
paths in any active GT-KB artifact, including documentation that adopters
install on their machines. The values above are intrinsically per-workstation
(your `groundtruth-kb` checkout is not at the same path as mine), so they
cannot live in tracked source.

A configuration file would be a small improvement over hardcoded literals,
but it would still be tracked or required to be present, which couples the
codebase to one workstation's filesystem layout. Environment variables are
the correct primitive: they are intrinsically per-environment, never tracked
in git, and a cold installation on a fresh machine fails clearly rather than
silently using a wrong default.

## Adopter checklist

For someone who just cloned GT-KB onto a new workstation:

1. Decide whether you will work with `groundtruth-kb` from this workstation.
2. If yes: clone groundtruth-kb at a path of your choice. Set
   `GROUNDTRUTH_KB_PATH` to that path. Verify with the command above.
3. If no: skip step 2. Bridge poller will still operate normally for
   Agent-Red-only items.
4. Only set `GTKB_PROJECT_ROOT` if Claude's hook reports that git resolution
   is failing. The vast majority of installations do not need it.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
