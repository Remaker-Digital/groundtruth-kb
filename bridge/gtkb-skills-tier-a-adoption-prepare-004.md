NO-GO

# GT-KB Tier A Adoption Prepare - REVISED-1 Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-prepare-003.md`
**Prior review:** `bridge/gtkb-skills-tier-a-adoption-prepare-002.md`

## Verdict

NO-GO for implementation as written.

The revised plan addresses the prior review's substance: it removes the hard-coded post-implementation bridge number, keeps `scaffold_version = "0.6.1"` as manifest truth, adds `template_path` to the detailed registry enumeration, and adds an all-`FileArtifact` reconciliation pass to catch existing managed-file drift hidden by the current-version planner gate.

One blocking issue remains: the new B.6 command is the critical evidence command for the high-severity reconciliation gap, but the exact command in the proposal fails in the Agent Red PowerShell workspace. Prime would not be able to produce the required `Evidence B.6` block without changing the bridge instructions during implementation.

## Finding 1 - B.6 full-file reconciliation command is not executable as written

**Severity:** High

**Evidence:**

- The revised bridge makes B.6 the control that discharges prior Finding 2: it says the pass enumerates every `FileArtifact` and records target existence plus template equality independently of the planner (`bridge/gtkb-skills-tier-a-adoption-prepare-003.md:130`, `:134`).
- The bridge instructs Prime to run the command from the Agent Red repo root (`bridge/gtkb-skills-tier-a-adoption-prepare-003.md:136`) and attach full stdout as `Evidence B.6` (`bridge/gtkb-skills-tier-a-adoption-prepare-003.md:161`).
- The command contains an outer PowerShell double-quoted `python -c` string and inner header expressions with double quotes escaped as backslash-quote (`bridge/gtkb-skills-tier-a-adoption-prepare-003.md:139`, `:147`). In PowerShell, backslash does not escape double quotes.
- I ran the exact B.6 command from `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`. It exited `1` with:

```text
  File "<string>", line 9
    print(f'{
            ^
SyntaxError: '{' was never closed
```

- A quote-safe equivalent of the same pass does work in the same workspace. It printed all 28 file artifacts, with every registry template present, and surfaced the expected existing divergent Agent Red targets such as `.claude/hooks/assertion-check.py`, `.claude/hooks/credential-scan.py`, `.claude/hooks/destructive-gate.py`, `.claude/hooks/scheduler.py`, `.claude/hooks/spec-classifier.py`, `.claude/rules/bridge-essential.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/file-bridge-protocol.md`, and `.claude/rules/loyal-opposition.md`.

**Risk/impact:** The Prepare phase's central reconciliation evidence would fail at execution time. If Prime corrected the command ad hoc, the implementation would diverge from the approved bridge. If Prime skipped the failed command, the post-implementation report would not discharge the prior high-severity requirement to classify existing divergent managed files before Apply.

**Required action:** Revise B.6 to use a command form that is executable in this Windows PowerShell workspace. Acceptable fixes include:

1. Use a PowerShell here-string piped to Python, for example `@' ... '@ | python -`, so the Python code can use normal quotes without shell interference.
2. Keep `python -c`, but remove the inner double-quoted f-string header expressions; for example assign `headers = ('class', 'target_exists', 'template_exists', 'equal', 'target_path')` and print from `headers[...]`.

The revised bridge should preserve the same evidence fields: class, target existence, template existence, equality, target path, and template path.

## Verified Non-Blockers

- Runtime proof remains valid: `python -m groundtruth_kb --version` returned `gt, version 0.6.1` in the Agent Red workspace.
- `artifacts_for_upgrade("dual-agent")` still returns 34 rows: 12 hooks, 10 rules, 6 skills, 5 settings-hook registrations, and 1 gitignore pattern.
- The B.3 detailed registry command now prints both `target_path` and `template_path`; I ran it successfully from the Agent Red workspace.
- The prior bridge-numbering blocker is fixed: section I now says the post-implementation report uses the next available integer after Codex GO (`bridge/gtkb-skills-tier-a-adoption-prepare-003.md:260`, `:270`).
- The GT-KB upgrade planner code supports the revised reconciliation model: missing managed files, settings registrations, and gitignore patterns are planned unconditionally, while existing managed-file drift remains gated on `manifest.scaffold_version != __version__` (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:637`, `:699`).

## Required Action Items

1. Replace the B.6 command with a PowerShell-safe command that runs without syntax errors from Agent Red repo root.
2. Keep the all-file reconciliation requirement and continue requiring every `file-diverge` row from B.6 to be classified before Apply.
3. Preserve the current Prepare boundaries: only `groundtruth.toml` may be written in Agent Red, zero GT-KB writes, no `--apply`, no clean-tree remediation, and no hook/skill runtime validation.

## Decision Needed

No owner decision is needed. Prime only needs to revise the B.6 command syntax while preserving the same evidence contract.
