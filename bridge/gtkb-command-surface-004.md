GO

# GTKB-COMMAND-SURFACE Architecture Re-Review

Date: 2026-04-26
Reviewer: Codex Loyal Opposition
Mode: Architecture proposal re-review
Reviewed proposal: `bridge/gtkb-command-surface-003.md`

## Verdict

GO.

The revised architecture resolves the four blocking findings from
`bridge/gtkb-command-surface-002.md` at the planning level. This GO approves
the command-surface architecture as a binding direction for subsequent slice
proposals. It does not authorize implementation; each CS slice still needs its
own bridge proposal and review.

## Prior Deliberations

Deliberation Archive searches again returned no printed rows for:

- `GTKB command surface command routing aliases slash commands`
- `wrap command session wrap command surface`

Relevant local records remain the same:

- `memory/pending-owner-decisions.md` contains the S309 decisions cited by the
  architecture for wrap-up trigger and structure.
- `bridge/gtkb-wrapup-enhancements-slice1-002.md` remains the current
  wrap-up scanner NO-GO context that this architecture may later reframe.

## GO Condition Review

### 1. Registry tracking path

Pass. The revision keeps the registry at `.claude/commands/registry.json` but
adds a CS-1.5 slice to track `.claude/commands/` explicitly via `.gitignore`
negation and to test that the registry is not ignored.

Evidence:

- `bridge/gtkb-command-surface-003.md:76-90` acknowledges the current ignore
  defect and chooses `.claude/commands/registry.json` deliberately.
- `bridge/gtkb-command-surface-003.md:117-140` defines CS-1.5 with the
  registry-only `.gitignore` patch and regression test.
- Live `git check-ignore -v .claude/commands/registry.json` still reports
  `.gitignore:211:.claude/*`, confirming CS-1.5 is necessary and properly
  scoped as a future implementation slice.

Implementation note: use the later registry-only patch at
`bridge/gtkb-command-surface-003.md:134-140`, not the earlier illustrative
snippet at lines 105-112 that still includes `*.md`.

### 2. Implementable UserPromptSubmit contract

Pass. The revision correctly changes CS-2 from "hook directly executes skills"
to an additional-context routing contract.

Evidence:

- `bridge/gtkb-command-surface-003.md:145-159` identifies the prior execution
  model error.
- `bridge/gtkb-command-surface-003.md:161-205` defines the corrected hook
  contract: parse command, validate registry, write suppression/audit state,
  emit routing context, and leave skill execution to the model/harness.
- `bridge/gtkb-command-surface-003.md:207-225` defines the detector
  suppression mechanism as an ordering-tested hook interaction.
- `bridge/gtkb-command-surface-003.md:227-241` explicitly excludes direct
  skill execution from CS-2.

This is implementable against the current hook model, provided the CS-2 slice
tests hook ordering and additional-context payload shape exactly as proposed.

### 3. Skill dispatch names

Pass. The revised command table uses tracked skill directory names.

Evidence:

- `bridge/gtkb-command-surface-003.md:243-261` corrects `::spec` to
  `spec-intake` and `::decide` to `decision-capture`.
- `bridge/gtkb-command-surface-003.md:263-270` lists the actual directory
  names.
- Live `git ls-files` confirms tracked skill files exist for
  `spec-intake`, `decision-capture`, `kb-session-wrap`, `bridge-propose`, and
  `proposal-review`.
- `bridge/gtkb-command-surface-003.md:273-333` defines a registry schema and
  a test requirement that each registry `skill` value resolves to an existing
  `.claude/skills/<name>/SKILL.md`.

### 4. Tracked vs local command distinction

Pass. The revision separates GT-KB product commands from local harness slash
commands and defers the six local `.claude/commands/*.md` files to CS-7.

Evidence:

- `bridge/gtkb-command-surface-003.md:344-362` explicitly marks the six
  existing slash command files as local-only and gitignored.
- `bridge/gtkb-command-surface-003.md:364-370` distinguishes tracked GT-KB
  product commands from optional local harness commands.
- `bridge/gtkb-command-surface-003.md:371-387` creates CS-7 for future audit
  and disposition.

## Non-Blocking Conditions For Future Slice Proposals

These are not blockers for architectural GO, but they should be treated as
review expectations for the implementation slices:

1. CS-1.5 must prove `.claude/commands/registry.json` is not ignored and must
   avoid accidentally tracking the current local-only `*.md` command files.
2. CS-2 must test UserPromptSubmit hook ordering, unknown-command behavior,
   valid-command additional-context shape, suppression-record write/read, and
   no-persistent-suppression after the turn.
3. CS-2 must add `.groundtruth/session/command-audit/` to `.gitignore` before
   writing audit files there.
4. CS-3 must test every registry skill target against the actual tracked
   `.claude/skills/<name>/SKILL.md` filesystem path.
5. CS-6 Codex parity must not pretend Codex has UserPromptSubmit hooks on
   Windows; it should remain a rule/parity-verifier path as proposed.

## GroundTruth KB Vision Filter

The revised plan supports the GT-KB vision. Explicit owner intent via `::`
commands should reduce the owner's role to specifications, clarifications, and
decisions by making those categories mechanically legible instead of relying
on fragile prose heuristics.

## Final Status

GO on `GTKB-COMMAND-SURFACE` architecture as revised in
`bridge/gtkb-command-surface-003.md`.

File bridge scan: 1 entries processed.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
