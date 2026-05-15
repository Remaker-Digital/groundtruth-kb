# GT-KB Skill: `grill-me-for-clarification` — Implementation Proposal — Revision 1 (003)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, harness B)
**Date:** 2026-05-15
**Session:** S353
**Thread:** gtkb-grill-me-for-clarification-skill
**Supersedes:** bridge/gtkb-grill-me-for-clarification-skill-001.md (NO-GO at -002)

Project Authorization: PAUTH-PROJECT-GT-KB-CLARIFICATION-TOOLING-GRILL-ME-FOR-CLARIFICATION-SKILL-IMPLEMENTATION
Project: PROJECT-GT-KB-CLARIFICATION-TOOLING
Work Item: WI-3321

**Governing spec:** SPEC-INTAKE-1262c1
**Operative requirement:** INTAKE-45c006c4 v2 (owner-confirmed)
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

## Response to Codex NO-GO (-002)

- **F1 (P1) — project-linkage metadata — RESOLVED.** The three machine-readable
  metadata lines are now present in the header. The owner selected a new
  dedicated project via AskUserQuestion (2026-05-15), captured as
  `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15`. Created:
  `PROJECT-GT-KB-CLARIFICATION-TOOLING` (active), its authorization
  `PAUTH-PROJECT-GT-KB-CLARIFICATION-TOOLING-GRILL-ME-FOR-CLARIFICATION-SKILL-IMPLEMENTATION`
  v2 (active; `included_work_item_ids` contains `WI-3321`), and a canonical
  bridge-conforming work item `WI-3321`. The `spec-intake` auto-created WI
  `WI-AUTO-SPEC-INTAKE-1262C1` is non-conforming for the compliance-gate
  `Work Item:` regex (`WI-\d+|GTKB-*|WORKLIST-*`), so `WI-3321` is the
  canonical work item for this thread; the auto-WI remains a project member
  for provenance.
- **F2 (P1) — KB mutation outside `target_paths` — RESOLVED.** The
  spec-assertion mutation is removed from this slice. `target_paths` covers
  only the three skill/test files; no `groundtruth.db` write occurs.
  Deliverable #4 and the prior implementation step 5 are dropped.
- **F3 (P2) — requirement-sufficiency overclaim — RESOLVED.** The Requirement
  Sufficiency section now cites `INTAKE-45c006c4` v2 as the operative
  owner-confirmed requirement source and acknowledges the thin
  `SPEC-INTAKE-1262c1` row. The GOV-12 linked KB test `TEST-11137` now links
  `SPEC-INTAKE-1262c1`.
- **F4 (P2) — wrong bridge id — RESOLVED.** The implementation-authorization
  command uses the document name `gtkb-grill-me-for-clarification-skill`.

## Scope

One procedural skill installed into GT-KB's own harness skill set. No DB schema
change, no hook registration, no new runtime dependency, no Python helper, no
MemBase mutation in the implementation phase.

### Deliverables

1. `.claude/skills/grill-me-for-clarification/SKILL.md` — the skill
   (frontmatter + five-phase body).
2. `.codex/skills/grill-me-for-clarification/SKILL.md` — Codex harness-parity
   adapter.
3. `tests/skills/test_grill_me_for_clarification_skill.py` — structural +
   parity assertions.

### Out of scope

- Adopter scaffold/upgrade delivery (`templates/skills/`, `_MANAGED_SKILLS`,
  doctor check). SPEC-INTAKE-1262c1 scopes the skill to GT-KB's own Prime
  Builder skill set; adopter packaging is a separate follow-on if the owner
  requests it.
- Any Python helper or DB writer — the skill drives existing skills
  (`gtkb-decision-capture`, `gtkb-spec-intake`); it adds no new writer surface.
- Populating the `SPEC-INTAKE-1262c1` row body / assertions — a tracked
  follow-on, deliberately excluded to keep this slice to the skill files
  (per F2/F3 above).
- The first invocation ("next 10-20 backlog-project sessions"). That is a
  *use* of the skill, not part of this implementation.

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

- SPEC-INTAKE-1262c1 — governing spec ID for this skill; type=requirement, status=specified, confirmed from INTAKE-45c006c4 this session.
- INTAKE-45c006c4 — operative owner-confirmed requirement record (v2); carries the full requirement text.
- GOV-01 — spec-first: this proposal follows a spec created before any code.
- GOV-09 — owner input classification: the owner's "add a skill" request was classified as specification language and routed through spec-intake.
- GOV-12 — work item creation triggers test creation: WI-3321 carries linked KB test TEST-11137.
- `.claude/rules/file-bridge-protocol.md` — the protocol this proposal is filed under.
- `.claude/rules/codex-review-gate.md` — mandates this proposal plus Codex GO before any implementation.
- `.claude/rules/deliberation-protocol.md` — the persistence mandate the skill's Phase 3 operationalizes.
- `.claude/rules/prime-builder-role.md` — the AUQ-only owner-decision channel the skill's Phase 2 uses.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` — the AUQ-only enforcement rule.
- ADR-0001 — three-tier memory architecture; the skill routes resolutions into the Deliberation Archive and MemBase tiers.
- `.claude/rules/operating-model.md` — the operating-model goal of reducing the owner role to specifications, clarifications, and decisions.
- DELIB-S324-PB-INTERROGATION-DIRECTIVE — the interrogative default this skill operationalizes.
- GOV-FILE-BRIDGE-AUTHORITY-001 — live bridge index authority; `bridge/INDEX.md` is the canonical workflow state for this thread.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — mandatory specification linkage; this section satisfies it by citing every governing spec.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verified spec-derived testing; the Tests section maps each test to a behavior clause.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — bridge-proposal project-linkage; satisfied by the three header metadata lines.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 — work item must belong to an approved project; WI-3321 is a member of PROJECT-GT-KB-CLARIFICATION-TOOLING under an active authorization.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — application/platform placement; this skill is a GT-KB platform artifact under `.claude/skills/`, not an adopter-application file.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — artifact-oriented governance; the skill and its requirement are tracked as formal artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — artifact-oriented development; advisory, consistent with routing this work through the spec → project → work item → bridge path.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle triggers; advisory, the requirement-candidate → spec → work-item lifecycle was triggered via `spec-intake` this session.

Spec-to-test derivation: the tests derive from the behavior clauses of the operative owner-confirmed requirement `INTAKE-45c006c4` v2. Structural assertions verify the SKILL.md surface exists and declares the five phases, the scope-required rule, the persistence routing, and the non-goals; the parity test verifies the Codex adapter mirrors the contract. The skill's interview behavior is an LLM procedure; per GOV-19 the testable surface is the skill file itself. The KB test artifact `TEST-11137` records `test_file` = the pytest path.

## Requirement Sufficiency

Existing requirements sufficient. The operative owner-confirmed requirement is
`INTAKE-45c006c4` v2 — the requirement-candidate deliberation confirmed this
session — which carries the full requirement text (scope rule, five-phase
behavior, persistence routing, non-goals). `SPEC-INTAKE-1262c1` is the spec-ID
anchor created by `spec-intake` confirm from that intake; its row currently
carries the title and status but an unpopulated `description`/`assertions`
body. For this slice that is acceptable: the durable, owner-confirmed substance
lives in `INTAKE-45c006c4` v2 (an append-only Deliberation Archive record),
the tests derive from its behavior clauses, and `SPEC-INTAKE-1262c1` links the
work via `WI-3321` and `TEST-11137`. Populating the `SPEC-INTAKE-1262c1` row
body and assertions through the governed path is a tracked follow-on,
deliberately excluded here to keep this slice to the skill files. No new or
revised requirement is needed before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a single procedural skill file plus a Codex parity adapter
and one test file. It performs no bulk operation over work items, specs, or the
standing backlog. References to "work item" and "backlog" describe the skill's
read-only exploration inputs and the single work item `WI-3321`, not a batch
mutation. The change is governed by the formal-artifact-approval and
spec-intake inventory path already exercised this session;
GOV-STANDING-BACKLOG-001 bulk-operation clauses do not apply.

## Prior Deliberations

- INTAKE-45c006c4 — requirement candidate captured this session via
  `gtkb-spec-intake` (outcome=deferred), then confirmed into SPEC-INTAKE-1262c1
  (v2, owner-confirmed).
- DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15 — owner decision (AskUserQuestion)
  selecting a new dedicated project to home `WI-3321`; the basis for
  `PROJECT-GT-KB-CLARIFICATION-TOOLING` and its authorization.
- The confirmation-version deliberation recorded by `spec-intake` confirm
  (outcome=owner_decision) on 2026-05-15.
- DELIB-S324-PB-INTERROGATION-DIRECTIVE — owner directive establishing the
  Prime Builder interrogative default; this skill is a structured
  operationalization of that directive.
- Codex NO-GO at `bridge/gtkb-grill-me-for-clarification-skill-002.md` — the
  prior verdict this revision answers (see Response to Codex NO-GO above).
- Deliberation Archive searched 2026-05-15: no prior deliberation proposes or
  pre-decides a clarification/interview skill. Closest related records are
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
- Project home (NO-GO F1) — owner selected "New dedicated project": authorized
  creating PROJECT-GT-KB-CLARIFICATION-TOOLING and its project authorization.
  Captured as DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15.

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

The KB test artifact `TEST-11137` links `SPEC-INTAKE-1262c1` and records
`test_file` = the pytest path; the pytest suite above is the executable
verification. No spec-assertion mutation occurs in this slice.

Net test delta: +6 tests, 0 removed.

## Risk / rollback

- Risk: low. The change adds two markdown skill files and one test file. No
  executable runtime path, no DB schema change, no hook registration, no
  MemBase mutation in the implementation phase.
- Rollback: delete the three added files. The skill is inert until invoked.
- The skill is constrained by its stated non-goals and its `allowed-tools`
  set; it cannot mutate code or file bridge proposals.

## Recommended Commit Type

`feat:` — adds a new skill, a net-new capability surface, not a repair or a
maintenance-only change.

## Implementation Sequence (post-GO)

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-grill-me-for-clarification-skill`.
2. Create `.claude/skills/grill-me-for-clarification/SKILL.md`.
3. Create `.codex/skills/grill-me-for-clarification/SKILL.md` (parity adapter).
4. Create `tests/skills/test_grill_me_for_clarification_skill.py`.
5. Run `pytest tests/skills/test_grill_me_for_clarification_skill.py -q`;
   capture output.
6. File the post-implementation report as the next bridge version.

## Pre-Filing Preflight

After the INDEX entry is updated, run
`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-grill-me-for-clarification-skill`
and
`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-grill-me-for-clarification-skill`.
Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking
clause gaps.

## GO Request

Codex review requested, with attention to: (a) whether structural + parity
tests are sufficient given the skill's behavior is an LLM procedure (GOV-19);
(b) whether adopter scaffold delivery should be in-scope rather than a
follow-on; (c) the `allowed-tools` set.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
