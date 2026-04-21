GO

# GT-KB Tier A Adoption Prepare - REVISED-2 Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-prepare-005.md`
**Prior reviews:** `bridge/gtkb-skills-tier-a-adoption-prepare-002.md`, `bridge/gtkb-skills-tier-a-adoption-prepare-004.md`

## Verdict

GO for the Prepare implementation bridge, limited to the scope in `-005`.

This authorizes the Prepare phase only: write `groundtruth.toml`, run the specified runtime proof, registry enumeration, dry-run, and reconciliation evidence commands, classify the reconciliation surface, commit only `groundtruth.toml`, and file the post-implementation report as the next available bridge version after this GO. It does not authorize `--apply`, GT-KB source writes, hook/skill runtime validation, clean-tree remediation, or the Apply bridge.

## Rationale

The only blocking issue from `-004` was the non-executable B.6 command. `-005` replaces it with a PowerShell-safe `python -c` command using `%` formatting and a positional header tuple (`bridge/gtkb-skills-tier-a-adoption-prepare-005.md:93`, `:98`).

I ran the exact `-005` B.6 command from the Agent Red repository root in PowerShell. It exited successfully and printed the required fields: `class`, `target_exists`, `template_exists`, `equal`, `target_path`, and `template_path`. The output contained 28 `FileArtifact` rows, with templates present for all rows, and surfaced the expected nine existing divergent managed targets:

```text
.claude/hooks/assertion-check.py
.claude/hooks/credential-scan.py
.claude/hooks/destructive-gate.py
.claude/hooks/scheduler.py
.claude/hooks/spec-classifier.py
.claude/rules/bridge-essential.md
.claude/rules/deliberation-protocol.md
.claude/rules/file-bridge-protocol.md
.claude/rules/loyal-opposition.md
```

The rest of the revised evidence model remains sound. The active runtime reports `gt, version 0.6.1`; `artifacts_for_upgrade("dual-agent")` returns 34 rows with the expected class distribution: 12 hooks, 10 rules, 6 skills, 5 settings-hook registrations, and 1 gitignore pattern. The GT-KB planner code also matches the bridge model: missing managed files, settings registrations, and gitignore patterns are planned unconditionally, while existing managed-file drift is gated behind `manifest.scaffold_version != __version__` (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:640`, `:689`, `:690`, `:691`, `:697`).

The bridge-numbering issue from `-002` remains fixed. `-005` says the post-implementation report uses the next available bridge version after Codex GO (`bridge/gtkb-skills-tier-a-adoption-prepare-005.md:181`, `:183`). Since this GO is `-006`, the expected post-implementation report is `bridge/gtkb-skills-tier-a-adoption-prepare-007.md` unless another coordination update changes the sequence before Prime writes.

## Findings

No blocking findings.

## Evidence Checked

- File bridge protocol requires Codex to save review findings as the next incremented version and insert the verdict at the top of the document entry (`.claude/rules/file-bridge-protocol.md:76`, `:77`).
- The current entry's latest version before this review was `REVISED: bridge/gtkb-skills-tier-a-adoption-prepare-005.md` (`bridge/INDEX.md:84`, `:85`), so this review correctly occupies `bridge/gtkb-skills-tier-a-adoption-prepare-006.md`.
- Prior NO-GO `-004` required replacing B.6 with a command that runs in Windows PowerShell (`bridge/gtkb-skills-tier-a-adoption-prepare-004.md:41`, `:58`).
- `python -m groundtruth_kb --version` from Agent Red returned `gt, version 0.6.1`.
- `python -m groundtruth_kb project upgrade --dry-run --dir .` currently returns the expected manifest-missing skip because `groundtruth.toml` does not yet exist; `groundtruth.db` does exist. That matches the pre-implementation state expected by the bridge.
- `bridge/gtkb-skills-tier-a-adoption-prepare-005.md:168` continues to require every B.6 `file-diverge` row to be classified before the post-implementation report.

## Required Conditions

1. Prepare may modify only Agent Red `groundtruth.toml`. Do not run `--apply`.
2. Capture Evidence B.1 through B.8 in the post-implementation report.
3. Classify every mutating row from B.5 and every `file-diverge` row from B.6.
4. Every A2/A3 row must have an owner disposition before the Apply bridge proceeds.
5. If the runtime proof differs from `gt, version 0.6.1`, stop and file a revised bridge report instead of continuing.
6. File the post-implementation report as the next available bridge version after this GO. Expected next version: `bridge/gtkb-skills-tier-a-adoption-prepare-007.md`.

## Decision Needed

No owner decision is needed before Prime executes Prepare. Owner dispositions are required later for any A2/A3 rows found in the reconciliation table before Apply can proceed.
