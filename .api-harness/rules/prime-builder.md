<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project openrouter`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Prime Builder Rule Set

This rule file defines mandatory behavior for the implementing/building agent.

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

### Standing Delete Authorization — DERIVED and CACHED Only

This is a bounded relaxation of the removal rule above, and only for objects whose class
is **proven from evidence**. It does not relax anything else in this section.

Prime Builder may delete an object without a fresh per-item owner approval when, and only
when, the deterministic classifier establishes one of:

- **DERIVED** — a named generator exists **and** regeneration has been demonstrated. The
  object must be reproducible from its source. The absence of a generator is not evidence
  of derivation, and a generator that is named but not demonstrated does not qualify.
- **CACHED** — a named source of truth exists **and** the object corresponds to it at byte
  or digest level. A named SoT whose digest diverges does not qualify.

Every other disposition is unchanged:

- **UNREGISTERED** objects are never deleted directly. They route to receipted quarantine
  with fixed 30-day retention, and reach permanent deletion only through the governed
  expiry path with all operation-time checks passing.
- **Any object whose class cannot be established from evidence remains owner-gated**,
  exactly as before. The classifier fails closed: uncertainty is not a licence.

Every action taken under this authorization emits a mandatory post-hoc audit record naming
the object acted on and the evidence for its class. An action without that record is a
defect, not a permitted shortcut.

This authorization is deliberately narrow. It exists because deletion of provably
regenerable material otherwise costs a proposal plus an owner approval while its addition
costs only a proposal, and that asymmetry accumulates. It does not authorize removing code,
tests, features, or specifications, none of which can satisfy the DERIVED or CACHED
evidence conditions.

Authority: `DELIB-20260825183500` (owner decision, Route B).

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
