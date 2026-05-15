# GT-KB Skill: `grill-me-for-clarification` — Implementation Proposal (001)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, harness B)
**Date:** 2026-05-15
**Session:** S353
**Thread:** gtkb-grill-me-for-clarification-skill
**Governing spec:** SPEC-INTAKE-1262c1
**Work item:** WI-AUTO-SPEC-INTAKE-1262C1
**target_paths:** `.claude/skills/grill-me-for-clarification/SKILL.md`, `.codex/skills/grill-me-for-clarification/SKILL.md`, `tests/skills/test_grill_me_for_clarification_skill.py`

## Summary

Add a reusable Prime Builder skill, `grill-me-for-clarification`, that conducts
a structured, dependency-ordered clarification interview of the owner about an
explicitly-scoped plan or design. The skill asks exactly one question per turn
via AskUserQuestion with the top-3 recommended answers; resolves
codebase-answerable questions by exploration rather than asking; and persists
each resolved branch immediately via `gtkb-decision-capture` or
`gtkb-spec-intake`. It produces durable decisions and a shared-understanding
summary. It writes no code, files no bridge proposals, and promotes no specs
beyond `spec-intake` confirm.

## Scope

One procedural skill installed into GT-KB's own harness skill set. No DB schema
change, no hook registration, no new runtime dependency, no Python helper.

### Deliverables

1. `.claude/skills/grill-me-for-clarification/SKILL.md` — the skill
   (frontmatter + five-phase body).
2. `.codex/skills/grill-me-for-clarification/SKILL.md` — Codex harness-parity
   adapter.
3. `tests/skills/test_grill_me_for_clarification_skill.py` — structural +
   parity assertions.
4. `grep` assertions added to SPEC-INTAKE-1262c1 — clears the current
   `NO_ASSERTIONS` flag (GOV-12 / GOV-18).

### Out of scope

- Adopter scaffold/upgrade delivery (`templates/skills/`, `_MANAGED_SKILLS`,
  doctor check). SPEC-INTAKE-1262c1 scopes the skill to GT-KB's own Prime
  Builder skill set; adopter packaging is a separate follow-on if the owner
  requests it.
- Any Python helper or DB writer — the skill drives existing skills
  (`gtkb-decision-capture`, `gtkb-spec-intake`); it adds no new writer surface.
- The first invocation ("next 10-20 backlog-project sessions"). That is a *use*
  of the skill, not part of this implementation.

## Skill design

**Frontmatter:** `name: grill-me-for-clarification`; owner-supplied
`description` (contains the trigger phrase "grill me for clarification");
`argument-hint: [plan or design or scope to grill]`; `allowed-tools` covering
Read, Grep, Glob, Bash, AskUserQuestion, Skill, Agent.

**Body — five phases:**

- Phase 0 — Scope intake (required). Require an explicit scope argument. With
  no argument the skill stops and requests one. Never defaults.
- Phase 1 — Build the decision tree. Read-only exploration of the in-scope
  artifacts (MemBase specs/work-items/projects, bridge threads, Deliberation
  Archive, rule files, code). Enumerate decision points with dependencies.
  Answer codebase-answerable questions by exploration and exclude them from the
  owner-question set. Emit the tree in dependency (topological) order.
- Phase 2 — Traverse one-at-a-time. For each unresolved decision in dependency
  order: exactly one AskUserQuestion per turn, top-3 recommended answers,
  recommended option first. Re-check the codebase before each question. Insert
  newly-discovered decision points at their correct dependency position.
- Phase 3 — Persist each resolution (checkpoint). Immediately classify and
  route: a pure decision → `gtkb-decision-capture`; a requirement-shaped
  resolution → `gtkb-spec-intake`.
- Phase 4 — Shared-understanding summary. Branch → resolution → DELIB/SPEC ID
  map; deferred branches listed with their revisit triggers.

**Non-goals stated in the SKILL.md body:** no code, no bridge proposals, no
spec promotion beyond `spec-intake` confirm, no work-item creation beyond
`spec-intake` confirm's deterministic behavior.

## Specification Links

- SPEC-INTAKE-1262c1 — governing requirement for this skill; type=requirement, status=specified, confirmed from INTAKE-45c006c4 this session.
- GOV-01 — spec-first: this proposal follows a spec created before any code.
- GOV-09 — owner input classification: the owner's "add a skill" request was classified as specification language and routed through spec-intake.
- `.claude/rules/file-bridge-protocol.md` — the protocol this proposal is filed under.
- `.claude/rules/codex-review-gate.md` — mandates this NEW proposal plus Codex GO before any implementation.
- `.claude/rules/deliberation-protocol.md` — the persistence mandate the skill's Phase 3 operationalizes.
- `.claude/rules/prime-builder-role.md` — the AUQ-only owner-decision channel the skill's Phase 2 uses.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` — the AUQ-only enforcement rule.
- ADR-0001 — three-tier memory architecture; the skill routes resolutions into the Deliberation Archive and MemBase tiers.
- `.claude/rules/operating-model.md` — the operating-model goal of reducing the owner role to specifications, clarifications, and decisions.
- DELIB-S324-PB-INTERROGATION-DIRECTIVE — the interrogative default this skill operationalizes.
- GOV-FILE-BRIDGE-AUTHORITY-001 — live bridge index authority; `bridge/INDEX.md` is the canonical workflow state for this thread.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — mandatory specification linkage; this section satisfies it by citing every governing spec.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verified spec-derived testing; the Tests section maps each test to a SPEC-INTAKE-1262c1 behavior clause.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — application/platform placement; this skill is a GT-KB platform artifact under `.claude/skills/`, not an adopter-application file, consistent with the placement contract.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — artifact-oriented governance; the skill and its requirement are tracked as formal artifacts (SPEC-INTAKE-1262c1, WI-AUTO-SPEC-INTAKE-1262C1, this bridge thread).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — artifact-oriented development; advisory, consistent with routing this work through the spec → work item → bridge path.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle triggers; advisory, the requirement-candidate → spec → work-item lifecycle was triggered via `spec-intake` this session.

Spec-to-test derivation: the tests derive from SPEC-INTAKE-1262c1's stated behavior clauses. Structural assertions verify the SKILL.md surface exists and declares the five phases, the scope-required rule, the persistence routing, and the non-goals; the parity test verifies the Codex adapter mirrors the contract. The skill's interview behavior is an LLM procedure; per GOV-19 the testable surface is the skill file itself.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-INTAKE-1262c1 governs this implementation
completely — it states the scope rule (reusable, scope-required), the
five-phase behavior, the persistence routing, and the non-goals. No new or
revised requirement is needed before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a single procedural skill file plus a Codex parity adapter
and one test file. It performs no bulk operation over work items, specs, or the
standing backlog. References to "work item" and "backlog" describe the skill's
read-only exploration inputs and the single auto-created work item
WI-AUTO-SPEC-INTAKE-1262C1, not a batch mutation. The change is governed by the
formal-artifact-approval and spec-intake inventory path already exercised this
session; GOV-STANDING-BACKLOG-001 bulk-operation clauses do not apply.

## Prior Deliberations

- INTAKE-45c006c4 — requirement candidate captured this session via
  `gtkb-spec-intake` (outcome=deferred), then confirmed into SPEC-INTAKE-1262c1.
- The confirmation-version deliberation recorded by `spec-intake` confirm
  (outcome=owner_decision) on 2026-05-15.
- DELIB-S324-PB-INTERROGATION-DIRECTIVE — owner directive establishing the
  Prime Builder interrogative default; this skill is a structured
  operationalization of that directive.
- Deliberation Archive searched 2026-05-15 ("owner clarification interview
  skill"; "grill requirements stress-test plan"; "decision tree clarification
  backlog"): no prior deliberation proposes or pre-decides a
  clarification/interview skill. Closest related records are
  spec-quality-by-clarity-of-intent advisories and the interrogative-default
  directive — supporting, not conflicting.

## Owner Decisions / Input

This proposal implements an owner-requested skill and depends on owner
approval, collected via AskUserQuestion this session (2026-05-15):

- Skill scope — owner selected "Reusable, scope required": the skill always
  requires an explicit scope argument and never defaults. Folded into
  SPEC-INTAKE-1262c1.
- Proceed decision — owner selected "File through governance": authorized the
  spec-intake → spec → work item → bridge proposal path.
- Spec confirmation — owner selected "Confirm into a spec": the formal-artifact
  approval promoting INTAKE-45c006c4 to SPEC-INTAKE-1262c1.

No further owner decision is pending for this proposal. Implementation begins
only after Codex GO.

## Tests

`tests/skills/test_grill_me_for_clarification_skill.py` (new):

1. `test_skill_file_exists_with_valid_frontmatter` — the SKILL.md exists; YAML
   frontmatter parses; `name == "grill-me-for-clarification"`; `description`
   contains "grill me for clarification".
2. `test_skill_body_declares_five_phases` — body contains the Phase 0–4
   markers (scope intake, build decision tree, traverse one-at-a-time, persist,
   summary).
3. `test_skill_body_states_scope_required_no_default` — body states the scope
   argument is required and there is no default scope.
4. `test_skill_body_routes_persistence_to_capture_and_intake` — body cites
   `gtkb-decision-capture` and `gtkb-spec-intake` as the Phase 3 persistence
   targets.
5. `test_skill_body_declares_non_goals` — body states the no-code /
   no-bridge-proposal / no-spec-promotion non-goals.
6. `test_codex_adapter_parity` — the Codex adapter exists and carries the same
   `name` and five-phase contract as the Claude skill.

SPEC-INTAKE-1262c1 gains `grep` assertions targeting the SKILL.md path and the
five-phase markers, clearing the `NO_ASSERTIONS` flag.

Net test delta: +6 tests, 0 removed.

## Risk / rollback

- Risk: low. The change adds two markdown skill files and one test file. No
  executable runtime path, no DB schema change, no hook registration.
- Rollback: delete the three added files and revert the SPEC-INTAKE-1262c1
  assertion version. The skill is inert until invoked.
- The skill is constrained by its stated non-goals and its `allowed-tools`
  set; it cannot mutate code or file bridge proposals.

## Recommended Commit Type

`feat:` — adds a new skill, a net-new capability surface, not a repair or a
maintenance-only change.

## Implementation Sequence (post-GO)

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-grill-me-for-clarification-skill-001`.
2. Create `.claude/skills/grill-me-for-clarification/SKILL.md`.
3. Create `.codex/skills/grill-me-for-clarification/SKILL.md` (parity adapter).
4. Create `tests/skills/test_grill_me_for_clarification_skill.py`.
5. Add `grep` assertions to SPEC-INTAKE-1262c1.
6. Run `pytest tests/skills/test_grill_me_for_clarification_skill.py -q` and
   the assertion check; capture output.
7. File `gtkb-grill-me-for-clarification-skill-002.md` as the
   post-implementation report.

## Pre-Filing Preflight

After the INDEX entry is added, run
`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-grill-me-for-clarification-skill-001`
and
`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-grill-me-for-clarification-skill-001`.
Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking
clause gaps.

## GO Request

Codex review requested, with attention to: (a) whether structural + parity
tests are sufficient given the skill's behavior is an LLM procedure (GOV-19),
or whether additional verification is warranted; (b) whether adopter scaffold
delivery should be in-scope rather than a follow-on; (c) the `allowed-tools`
set.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
