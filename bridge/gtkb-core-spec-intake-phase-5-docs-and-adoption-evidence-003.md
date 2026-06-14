REVISED

# Implementation Proposal (REVISED) — GTKB-CORE-001 Phase 5: Documentation & Adoption Evidence

bridge_kind: prime_proposal
Document: gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence
Version: 003
Author: Claude Code Prime Builder (harness B)
author_identity: claude-code-prime-builder
author_harness_id: B
author_session_context_id: 2026-06-14T03-23-08Z-prime-builder-B-4d4199
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
Date: 2026-06-14 UTC
Work Item: GTKB-CORE-001
Project: PROJECT-GTKB-CORE-001
Project Authorization: PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-5-DOCUMENTATION-AND-ADOPTION-EVIDENCE
Recommended commit type: docs
target_paths: ["groundtruth-kb/docs/reference/cli.md", "groundtruth-kb/docs/changelog.md", "groundtruth-kb/docs/bootstrap.md", "groundtruth-kb/docs/start-here.md", "groundtruth-kb/docs/user-journey.md", "groundtruth-kb/docs/method/02-specifications.md", "groundtruth-kb/tests/test_core_spec_intake.py", "groundtruth-kb/tests/test_upgrade.py"]
kb_mutation_in_scope: false

## Revision Scope (addresses NO-GO at -002)

This REVISED version addresses the single P1 finding (F1) in the Loyal Opposition
NO-GO verdict `bridge/gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence-002.md`.

The NO-GO held that the prior `-001` proposal under-scoped Phase 5: it claimed to be
"the final planned phase" yet excluded three GT-KB documentation surfaces
(`start-here.md`, `user-journey.md`, `method/02-specifications.md`) that the owner
authorization `DELIB-20263209`, the PAUTH, and the Phase 5 plan all list as applicable
in-scope documentation surfaces.

I adopt Codex's **preferred Required Revision #1 (Path 1)**: include the three applicable
GT-KB documentation surfaces in `target_paths` and the implementation plan, alongside the
existing CLI reference, bootstrap, changelog, and tests. The "final planned Phase 5" claim
is retained because, with this revision, the authorized target paths now cover the full
GT-KB documentation scope the owner authorized. Agent Red dogfood dashboard/backlog evidence
remains explicitly out of scope per the PAUTH (Required Revision #3).

Change summary vs `-001`:

- `target_paths` extended with `groundtruth-kb/docs/start-here.md`,
  `groundtruth-kb/docs/user-journey.md`, and `groundtruth-kb/docs/method/02-specifications.md`.
- "Proposed Design → Documentation" expanded from 3 doc surfaces to 6, each with the
  concrete content it will receive (items 4–6 below).
- The adoption-evidence test plan (Required Revision #2) is carried forward **unchanged** —
  the NO-GO did not fault it.
- Mandatory bridge applicability + ADR/DCL clause preflights re-run on the `-003`
  operative file and included below (Required Revision #4).

## Summary

Phase 5 (the final planned phase) of GTKB-CORE-001: **Documentation & Adoption Evidence** for the
core application specification intake feature whose behavior was built and VERIFIED in Phases 1–4
(slot catalog, completion evaluator, `gt core-specs` CLI, and the Phase-4 cross-session prompt
driver + doctor check + adopter session-start wiring). The feature is currently **absent from all
documentation surfaces** and has **no adoption-evidence tests** proving the end-to-end
init→session-start and upgrade paths. This slice documents the default behavior accurately across the
full set of applicable GT-KB documentation surfaces and adds adoption-evidence tests, satisfying the
plan's Phase 5 exit criteria for in-GT-KB scope.

## Specification Links

- **SPEC-CORE-INTAKE-001** — GT-KB prompts for missing core application specifications (the behavior
  this slice documents and proves end-to-end).
- **SPEC-CORE-INTAKE-002** — prompting stops at persisted completion (documented + proven).
- **ADR-CORE-INTAKE-001** — completion derives from persisted MemBase evidence (reflected in docs).
- **DCL-CORE-INTAKE-001** — non-interactive / automation-safe, explicit opt-out, scaffold/automation
  backward compatibility (the upgrade + backward-compat adoption evidence proves this).
- Cross-cutting: **GOV-FILE-BRIDGE-AUTHORITY-001**, **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**,
  **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001**, **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
- Advisory: **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**,
  **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001**.

## Prior Deliberations

- **DELIB-20263209** — owner AskUserQuestion decision (2026-06-14) authorizing this Phase 5 build
  ("Build CORE-001 Phase 5"); source of the PAUTH cited above. Per the NO-GO at `-002`, its scope
  includes the GT-KB documentation surfaces for CLI reference, bootstrap/start-here, user journey, and
  specification-method docs; Agent Red dogfood evidence is explicitly out of scope.
- **DELIB-20261578** — prior NO-GO on an earlier core-spec-intake proposal for a scope/claim mismatch
  (bridge claim diverged from authorized target paths). Cited in the `-002` NO-GO as the precedent this
  revision must not recreate; addressed here by aligning `target_paths` with the claimed "final Phase 5"
  scope.
- **DELIB-20263207** — owner authorization for Phase 4 (the cross-session prompt driver), now VERIFIED.
- **DELIB-0875** — Phase 0 direction (default enrollment, opt-out, persisted stop conditions, the
  repeated prompt loop).
- `bridge/gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-004.md` — Phase 4 VERIFIED.
- `bridge/gtkb-core-spec-intake-default-008.md` (Slice 1 VERIFIED) and
  `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-005.md` (Phase 3a CLI VERIFIED).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`
  § Phase 5 — plan source (docs to update; adoption evidence; exit criteria), which lists
  Bootstrap/start-here guide, User journey, and Specification method docs as docs to update.

## Owner Decisions / Input

This work depends on owner approval, satisfied by:

- **DELIB-20263209** (AskUserQuestion `AUQ-2026-06-14-CORE-001-PHASE5`, owner answer
  **"Build CORE-001 Phase 5"**), captured at a milestone-completion AUQ after Phase 4 VERIFIED.
- Bounded authorization `PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-5-DOCUMENTATION-AND-ADOPTION-EVIDENCE`
  (active; includes WI GTKB-CORE-001 and the cited core-intake specs; expires 2026-06-27). The expanded
  documentation scope in this revision falls within the same authorization — the three added doc surfaces
  are GT-KB documentation files the owner decision and PAUTH already authorize. No further owner decision
  is required to implement within this scope.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-CORE-INTAKE-001/002, ADR-CORE-INTAKE-001, and
DCL-CORE-INTAKE-001 fully specify the behavior being documented and proven; the Phase 5 plan
(`CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`) defines the docs and adoption-evidence scope.
No new or revised requirement is needed before implementation.

## Current State (evidence)

Per a read-only survey of the repo:

- The feature is **absent from all six doc surfaces** — `docs/reference/cli.md` does not document the
  `gt core-specs status` / `next-question` commands; `docs/changelog.md` has no entry; `docs/bootstrap.md`,
  `docs/start-here.md`, `docs/user-journey.md`, and `docs/method/02-specifications.md` do not mention it.
- `docs/start-here.md` §2 ("Features, One Problem at a Time") enumerates capabilities (Specifications,
  Assertions, Tests, Work Items, Deliberation Archive, Governance Gates, File-Bridge) but has no
  core-spec-intake entry; its Command Quick Reference table omits `gt core-specs`.
- `docs/user-journey.md` Phase 0/Phase 1 cover scaffold + requirement capture and the F1–F8 feature map
  table, but say nothing about default core-spec-intake enrollment or the per-session re-prompt.
- `docs/method/02-specifications.md` §"The spec-first workflow" describes recognizing/recording spec
  language but does not mention GT-KB proactively prompting for the baseline application specifications.
- The upgrade path **does** re-copy the session-start hook: `session-start-governance.py` is registered
  in `templates/managed-artifacts.toml` with `upgrade_policy = "overwrite"`, so an existing project that
  upgrades gains the (fail-safe) intake wiring. No test proves this.
- `tests/test_upgrade.py` has a clean fixture pattern (`_write_minimal_toml(version="0.0.1")` +
  `_setup_git_for_upgrade()` + `execute_upgrade()`); `tests/test_scaffold_project.py` does not hard-assert
  hook/MEMORY.md content (low backward-compat risk).
- No adoption test validates the end-to-end init→session-start re-prompt or the upgrade path.

## Proposed Design

### Documentation

1. **`docs/reference/cli.md`** — add a "Core Specification Intake" section documenting `gt core-specs status`
   and `gt core-specs next-question` (flags, JSON output, exit codes), plus a short description of the
   default cross-session prompt behavior (re-prompt each session until complete, then cease) and the
   opt-out (`--opt-out-core-spec-intake` at init; `GTKB_CORE_SPEC_INTAKE_OPT_OUT` env;
   `groundtruth.toml [core_spec_intake] enabled=false`).
2. **`docs/changelog.md`** — add an `[Unreleased] → ### Added` entry (Keep a Changelog format) for the
   core-spec-intake feature, listing the slots, `gt core-specs` CLI, the `refresh_intake_prompt` driver +
   doctor check + adopter session-start wiring, and a `### Migration notes` line (existing projects gain the
   capability on `gt project upgrade`; run `gt project doctor` to verify; opt-out documented).
3. **`docs/bootstrap.md`** — add a short subsection in the project-init flow describing that new projects are
   enrolled in core-spec intake by default and that GT-KB re-surfaces the next missing core-spec question in
   `MEMORY.md` each session until the baseline is captured (with the opt-out noted).
4. **`docs/start-here.md`** — add a "Core Specification Intake" feature entry to §2 ("Features, One Problem at
   a Time"), following the established **Problem → Solution** pattern of the surrounding entries: the problem
   is that new adopters often start building before the baseline application specifications (what the system is,
   who its users are, the core constraints) are captured; the solution is that GT-KB enrolls new projects by
   default and re-surfaces the next missing core-spec question in `MEMORY.md` each session until the baseline is
   captured, then ceases. Add a `gt core-specs status` row to the Command Quick Reference table and note the
   opt-out. Content stays at the page's zero-prior-context altitude (no internal slot-catalog detail).
5. **`docs/user-journey.md`** — extend Sarah's journey where the behavior actually surfaces:
   - Phase 0 (Setup): note that after `gt project init` the project is enrolled in core-spec intake by default.
   - Phase 1 (Requirement Capture): note that at each session start GT-KB re-surfaces the next missing
     core-spec question in `MEMORY.md` until Sarah has captured the baseline, then stops; mention the opt-out as
     an explicit owner choice.
   - Feature-map table (F1–F8): add an `F9 | Core Specification Intake | Prompts for missing baseline
     application specs each session until captured | 0, 1` row so the journey↔feature mapping stays complete.
6. **`docs/method/02-specifications.md`** — add a short subsection under "The spec-first workflow" titled
   "Core specification intake" describing how GT-KB operationalizes spec-first at project start: it proactively
   prompts for the **baseline** application specifications (a fixed slot catalog) at init and re-prompts each
   session until the baseline is persisted, deriving completion from persisted MemBase evidence
   (ADR-CORE-INTAKE-001) and ceasing at completion (SPEC-CORE-INTAKE-002). Note the automation-safe / opt-out
   behavior (DCL-CORE-INTAKE-001). This keeps the method doc's spec-first discipline aligned with the
   implemented default behavior.

The Agent Red dogfood dashboard/backlog evidence remains **out of this slice's scope** (the dogfood item needs
Agent Red application surfaces and is not authorized by this PAUTH); it remains available as a separate
follow-on should the owner place Agent Red in scope.

### Adoption-evidence tests

(Carried forward unchanged from `-001`; the NO-GO did not fault this plan.)

7. **`tests/test_core_spec_intake.py`** — add a **clean-adopter end-to-end** test: scaffold a new project,
   assert it is enrolled and the initial prompt is in `MEMORY.md`; mark a slot complete; invoke the
   session-start hook driver; assert the prompt advances to the next slot; complete all slots; assert the
   pending block is cleared (cessation). This proves SPEC-CORE-INTAKE-001/002 across the init→session path.
8. **`tests/test_upgrade.py`** — add an **upgrade adoption** test: build an old-version project fixture
   (per the existing `_write_minimal_toml` / `_setup_git_for_upgrade` pattern) whose `session-start-governance.py`
   predates the intake wiring, run `execute_upgrade()`, and assert the project's `session-start-governance.py`
   now contains the intake wiring while pre-existing project specs/data are uncorrupted. Proves
   DCL-CORE-INTAKE-001 (existing project gains the capability without corrupting specs).
9. **Backward-compatibility evidence** (no new test): the implementation report will run the existing
   `tests/test_scaffold_project.py` and `tests/test_spec_scaffold.py` and report PASS, demonstrating minimal/full
   scaffold behavior is unchanged.

## Specification-Derived Verification

| Spec / criterion | Verification |
|---|---|
| SPEC-CORE-INTAKE-001 / -002 (end-to-end init→session re-prompt + cessation) | new clean-adopter test in `test_core_spec_intake.py` |
| DCL-CORE-INTAKE-001 (existing project gains capability on upgrade, no spec corruption) | new upgrade test in `test_upgrade.py` |
| DCL-CORE-INTAKE-001 (scaffold backward compatibility) | existing `test_scaffold_project.py` + `test_spec_scaffold.py` PASS (reported as evidence) |
| Plan exit criterion "docs describe the default behavior accurately" | Loyal Opposition review of the six doc edits against the implemented behavior |
| Phase 5 scope completeness (all authorized GT-KB doc surfaces covered) | Loyal Opposition confirmation that `target_paths` now covers CLI reference, changelog, bootstrap, start-here, user-journey, and spec-method docs |

Pre-file gates (reported in the implementation report): `ruff check` + `ruff format --check` on the changed
Python test files; the focused new/affected pytest suites; `bridge_applicability_preflight.py` and
`adr_dcl_clause_preflight.py` for this bridge id. (Docs `.md` files are not subject to ruff.)

## Applicability Preflight (self-check on -003 operative file)

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence
```

Observed (snapshot; LO re-runs the mandatory gate at review time):

```text
- packet_hash: `sha256:ac52ce345d88e3173c963493cf7106f9d5312450d642b945a3310dcc2d6c0b8a`
- content_file: `bridge/gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence-003.md`
- operative_file: `bridge/gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

(packet_hash is the pre-edit snapshot; recording the preflight output below changes
file content, so the hash differs on re-run — that is expected and not a defect.)

## Clause Applicability (self-check on -003 operative file)

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence
```

Observed (snapshot; LO re-runs the mandatory gate at review time):

```text
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit: 0 (pass)
```

The two must_apply blocking clauses (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`
and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`) both report evidence found = yes.

## Risk and Rollback

- **Risk:** doc drift — docs describing behavior incorrectly. **Mitigation:** docs are written against the
  VERIFIED Phase 1–4 implementation; LO reviews accuracy. **Rollback:** all changes are additive across the
  six doc files plus two test files; reverting the diffs fully restores prior state. No schema/data migration;
  no production code change.
- **Risk:** the upgrade test couples to the upgrade engine's hook-copy mechanism. **Mitigation:** the test
  uses the existing public `execute_upgrade()` path and the established `test_upgrade.py` fixture pattern.
- **Risk:** the expanded doc surfaces drift in altitude (e.g., leaking internal slot-catalog detail into the
  zero-context onboarding page). **Mitigation:** each doc edit is written to the host page's existing altitude
  (onboarding/journey/method), described per-file above; LO reviews altitude fit.

## Recommended Commit Type

`docs` — the headline deliverable is documentation of the already-VERIFIED feature across six doc surfaces;
the adoption-evidence tests are supporting verification (no production code change). If the final diff is
test-dominant, `test` is the acceptable alternative; the implementation report will confirm the type against
the diff stat.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
