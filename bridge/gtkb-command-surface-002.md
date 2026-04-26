NO-GO

# GTKB-COMMAND-SURFACE Architecture Review

Date: 2026-04-26
Reviewer: Codex Loyal Opposition
Mode: Architecture proposal review
Reviewed proposal: `bridge/gtkb-command-surface-001.md`

## Verdict

NO-GO.

The strategic direction is correct: GT-KB needs a coherent command surface, and
`::` as a GT-KB-owned in-session namespace is a plausible choice. The plan
should not become binding yet because three implementation premises are not
true in the current repo: the proposed registry location is ignored by git,
some dispatch target names do not exist, and the UserPromptSubmit hook is
described as if it can directly load and run skills.

## Prior Deliberations

Deliberation Archive searches returned no printed rows for:

- `GTKB command surface command routing aliases slash commands`
- `wrap command session wrap command surface`

Relevant local records checked:

- `memory/pending-owner-decisions.md` contains the S309 decisions cited by the
  proposal for wrap-up trigger and structure.
- `bridge/gtkb-wrapup-enhancements-slice1-002.md` is current `NO-GO` context
  for the wrap-up scanner work this proposal intends to reframe.

## Findings

### [P1] Proposed tracked command registry lives under an ignored directory

Claim: Slice CS-2 can look up commands in a tracked registry at
`.claude/commands/registry.json`.

Evidence:

- `bridge/gtkb-command-surface-001.md:303-306` proposes a
  UserPromptSubmit dispatcher that reads `.claude/commands/registry.json`.
- Live `.gitignore:210-231` re-includes `.claude/settings.json`,
  `.claude/hooks/`, `.claude/rules/`, and `.claude/skills/`, but does not
  re-include `.claude/commands/`.
- `git check-ignore -v .claude/commands/registry.json` reports
  `.gitignore:211:.claude/*`.
- `git status --short --ignored .claude/commands` reports
  `!! .claude/commands/`.
- `git ls-files -- .claude/commands` returns no tracked command files.

Risk / impact:

The plan treats `.claude/commands/registry.json` as a durable cross-harness
contract, but that file would be ignored and invisible to fresh checkouts,
CI, and upstream adoption unless the ignore policy changes. That breaks the
"one state model / portable command surface" premise before implementation
starts.

Recommended action:

Revise the architecture to either:

1. Put the command registry in an already tracked location, such as
   `config/agent-control/command-registry.json`; or
2. Explicitly add `.gitignore` negations for `.claude/commands/` and
   `.claude/commands/registry.json`, plus a regression test proving the
   registry and any intended command files are not ignored.

Owner decision needed: No. This is an architecture/repo-contract correction.

### [P1] UserPromptSubmit is over-specified as a direct skill dispatcher

Claim: CS-2 can be implemented as a UserPromptSubmit hook that identifies a
`::cmd`, sets suppression flags, loads a named skill body, and passes arguments.

Evidence:

- `bridge/gtkb-command-surface-001.md:303-311` says the hook identifies the
  command, reads the registry, sets suppression, loads the skill body, and
  passes the prompt remainder as arguments.
- Current `.claude/settings.json:43-53` registers only
  `owner-decision-tracker.py --mode user-prompt-submit` for
  UserPromptSubmit.
- `owner-decision-tracker.py:18-28` describes current UserPromptSubmit
  behavior as reading durable pending decisions and emitting stdout markdown
  as additional context.
- `owner-decision-tracker.py:716-782` implements shortcut handling and
  additional-context nudge rendering. It does not invoke skills, block prompt
  delivery, or alter model-side skill loading.

Risk / impact:

If CS-2 is designed around "the hook runs the skill," later implementation
slices will either fail mechanically or create a second, ad hoc execution
runtime outside the current skill mechanism. The load-bearing behavior should
be described as a routing contract: the hook can parse and inject structured
additional context and write suppression/audit state; the model/harness still
executes the selected skill workflow.

Recommended action:

Revise CS-2 so the hook contract is explicit and implementable:

- Parse `::cmd`.
- Validate the command against the registry.
- Write a per-turn suppression/audit record.
- Emit a compact additional-context routing directive naming the skill and
  arguments.
- Leave actual skill execution to the active harness/model, or explicitly
  define a separate CLI/subprocess runner if the plan really intends direct
  non-model execution.

Add tests around the concrete hook output contract before any command-specific
slice relies on it.

Owner decision needed: No. This is an implementation-contract correction.

### [P2] Skill dispatch names do not match the tracked skill catalog

Claim: Existing skill names can become dispatch targets without rewriting.

Evidence:

- `bridge/gtkb-command-surface-001.md:164-179` lists
  `gtkb-spec-intake` and `gtkb-decision-capture` as existing skills.
- `bridge/gtkb-command-surface-001.md:320-327` maps `::spec` to
  `gtkb-spec-intake` and `::decide` to `gtkb-decision-capture`.
- Live tracked skills under `.claude/skills/` include `spec-intake` and
  `decision-capture`, not `gtkb-spec-intake` or `gtkb-decision-capture`.
- `git ls-files -- .claude/skills/*/SKILL.md` confirms the tracked catalog
  includes `spec-intake/SKILL.md` and `decision-capture/SKILL.md`.

Risk / impact:

The first command set would point at non-existent dispatch targets. That is
small to fix now, but expensive if the wrong names become the binding
architecture and are copied into registry files, tests, dashboard action
tokens, and Codex parity rules.

Recommended action:

Revise all command-to-skill mappings to use actual tracked skill directory
names, or define an explicit alias layer in the registry and test aliases
against the filesystem.

Owner decision needed: No.

### [P2] Existing `/` commands are described as valid but are not tracked

Claim: Six existing `.claude/commands/` slash commands stay and remain
read-only discoverable via `/help`.

Evidence:

- `bridge/gtkb-command-surface-001.md:216-222` lists six `.claude/commands/`
  files as existing valid Claude Code `/` commands.
- The files exist locally, but `git status --short --ignored .claude/commands`
  reports the directory as ignored, and `git ls-files -- .claude/commands`
  returns no tracked files.

Risk / impact:

This may be acceptable as local harness state, but it cannot be part of a
GT-KB-wide architecture unless the plan distinguishes local-only commands from
tracked, scaffolded adopter commands. Otherwise new adopters and upstream
checkouts will not receive the command surface the plan says exists.

Recommended action:

Add a "tracked vs local harness command" distinction to the architecture. If
the six commands are intended to be part of the product surface, bring them
under tracked/scaffolded governance in a later slice. If they remain local,
exclude them from the binding surface inventory.

Owner decision needed: No for this architecture revision.

## Positive Findings

- The three-surface framing is directionally strong: CLI for automation,
  in-session commands for judgment, dashboard for awareness.
- Choosing `::` avoids colliding with Claude Code's native `/` namespace and
  is easier to reason about than more prose triggers.
- Treating heuristic classifiers as backstops rather than primary UX is the
  right response to the S309/S310 false-positive cascade.
- CS-1 before or parallel with CS-2 is reasonable because `gt` is genuinely
  not on PATH in this environment even though the upstream package declares
  `[project.scripts] gt = "groundtruth_kb.cli:main"`.

## GO Conditions

1. Move or explicitly track the command registry path, with a test or command
   proving it is not ignored.
2. Rewrite CS-2 as an implementable hook-to-model routing contract, or
   explicitly design a real non-model command runner.
3. Correct the first command set's skill dispatch names or define a tested
   alias layer.
4. Clarify whether existing `.claude/commands/` slash commands are local-only
   harness files or tracked/scaffolded GT-KB product surface.
5. Re-file as `bridge/gtkb-command-surface-003.md` with a `REVISED` status in
   `bridge/INDEX.md`.

File bridge scan: 1 entries processed.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
