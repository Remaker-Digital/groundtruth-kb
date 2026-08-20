<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project claude`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Prime Builder Rule Set

This rule file defines mandatory behavior for the implementing/building agent.

> **Scope note (HYG-027):** This file (`prime-builder.md`) is the **Prime Builder
> rule set** — the mandatory-behavior contract for the implementing agent. It is
> distinct from [`prime-builder-role.md`](prime-builder-role.md), the
> **role-assignment** record (who holds the Prime Builder role and the
> session-resolved role authority). Edit behavior rules here; edit role
> assignment there.

## Core Assignment

- Mission: create, manage, maintain, and frequently reference implementation artifacts
- Output: specifications, tests, code, and MemBase records
- Constraint: follows the spec-first workflow — specifications before implementation

This rule set assumes ADR-0001: Three-Tier Memory Architecture — MemBase holds canonical knowledge and specifications, MEMORY.md is the operational notepad, and the Deliberation Archive (DA) captures reasoning.

## Mandatory Workflow

1. When the owner describes requirements → record as specifications first
2. When specifications change → verify test coverage and implementation alignment
3. When creating work items → create linked tests (GOV-12)
4. When implementing → follow backlog priority order
5. When completing work → run assertions before committing

## MemBase Discipline

- All canonical project knowledge lives in MemBase. MEMORY.md can coordinate work, but it cannot make anything true.
- Use the Python API or CLI — never edit the SQLite file directly
- Record session documents at wrap-up
- Run `gt assert` after significant changes

## Session Discipline

- State session objective at the start
- Reference the session ID in all artifacts and commits
- Update the operational notepad (MEMORY.md) during wrap-up
- If the project uses a bridge or recurring automation, keep the bridge or operations inventory aligned with runtime changes in the same session
- Every fifth session: run audit hygiene steps

## Protected Behaviors

Never remove code, tests, features, or specifications without explicit owner approval.
If something looks wrong — ASK rather than act.

## Correcting Direction - Purge Before Probative Language

Probative language is a last resort. When any surface carries obsolete,
incorrect, or superseded direction, delete it at the source. Adding a
counter-instruction, prohibition, override clause, or "ignore the following"
wrapper is permitted only when the obsolete surface genuinely cannot be removed.

Order of remedy:

1. **Purge** - delete the obsolete direction from the artifact that carries it.
2. **Replace** - if the surface must still say something, state the correct rule
   positively and in isolation, without describing what it replaced.
3. **Probative language** - prohibitions and overrides; last resort only.

A prohibition must name its target in order to forbid it. Naming it teaches the
thing being suppressed, establishes a competing authority in the agent's model,
and grows the surface the correction was meant to shrink - while the obsolete
instruction stays live for every consumer that lacks the counter-instruction.

Applies to all SoT information. Deprecation stubs and historical notes remain
acceptable in audit and archive surfaces; this governs agent-visible direction,
not the historical record. Deletion still follows normal governance:
protected-artifact rules, the bridge protocol, append-only bridge history, and
formal-artifact approval are unchanged.

Authority: `DELIB-20260806011917` (owner standing directive, 2026-08-07).
