NEW

# Implementation Report — GTKB-CORE-001 Phase 5: Documentation & Adoption Evidence

bridge_kind: implementation_report
Document: gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence
Version: 005
Author: Claude Code Prime Builder (harness B)
author_identity: claude-code-prime-builder
author_harness_id: B
author_session_context_id: 1d33598a-6bc1-4317-b63e-bf2fbe22ce6b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
Date: 2026-06-14 UTC
Work Item: GTKB-CORE-001
Project: PROJECT-GTKB-CORE-001
Project Authorization: PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-5-DOCUMENTATION-AND-ADOPTION-EVIDENCE
Responds to: bridge/gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence-004.md (GO)
Recommended commit type: docs
kb_mutation_in_scope: false

## Summary

Implemented Phase 5 (the final planned phase) of GTKB-CORE-001 per the GO at `-004` on the
authoritative REVISED proposal `-003` (which expanded the documentation scope from 3 to 6 GT-KB
doc surfaces in response to the NO-GO at `-002`). This slice documents the core-spec-intake default
behavior across all six authorized documentation surfaces and adds adoption-evidence tests proving
the end-to-end init→session-start and upgrade paths. The feature behavior itself was built and
VERIFIED in Phases 1–4; this slice adds no production code.

Implementation note: the prior two sibling Prime sessions (661c3d, 536f4f) claimed this GO but
stalled (the impl-start gate was quiescing on unrelated sibling reports mid-review, blocking their
mutations) and never filed a report; their work-intent claims lapsed. This session took over the
genuinely-available thread once the gate cleared, implementing the `-003` scope.

## Specification Links

- **SPEC-CORE-INTAKE-001** — GT-KB prompts for missing core application specifications (documented + proven).
- **SPEC-CORE-INTAKE-002** — prompting stops at persisted completion (documented + proven).
- **ADR-CORE-INTAKE-001** — completion derives from persisted MemBase evidence (reflected in docs).
- **DCL-CORE-INTAKE-001** — non-interactive / automation-safe, explicit opt-out, scaffold/automation
  backward compatibility (proven by the upgrade + backward-compat adoption evidence).
- Cross-cutting: **GOV-FILE-BRIDGE-AUTHORITY-001**, **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**,
  **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001**, **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
- Advisory: **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**,
  **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001**.

## Prior Deliberations

- **DELIB-20263209** — owner authorization for Phase 5 ("Build CORE-001 Phase 5").
- **DELIB-20263207** — owner authorization for Phase 4 (now VERIFIED).
- **DELIB-0875** — Phase 0 direction (default enrollment, opt-out, persisted stop conditions, repeat loop).
- **DELIB-20261578** — prior NO-GO precedent (scope/claim mismatch) cited by the `-002` NO-GO; addressed by
  aligning `target_paths` with the claimed "final Phase 5" scope (six doc surfaces).
- `bridge/gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-004.md` — Phase 4 VERIFIED.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`
  § Phase 5 — plan source.

## Owner Decisions / Input

- **DELIB-20263209** (AskUserQuestion `AUQ-2026-06-14-CORE-001-PHASE5`, owner answer
  **"Build CORE-001 Phase 5"**) authorizes this implementation. The bounded
  `PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-5-DOCUMENTATION-AND-ADOPTION-EVIDENCE` (active, expires
  2026-06-27) covers WI GTKB-CORE-001 and the cited specs. The expanded six-surface documentation scope
  falls within the same authorization (all are GT-KB documentation files). No further owner decision was
  required to implement within this scope.

## Implementation

Eight files, all within the GO'd `-003` target paths:

**Documentation (6):**

1. **`docs/reference/cli.md`** — new "Core Specification Intake" section documenting `gt core-specs status`
   and `gt core-specs next-question` (flags, JSON, exit codes), the default cross-session prompt behavior,
   and the opt-out paths.
2. **`docs/changelog.md`** — `[Unreleased] → ### Added` entry (slots, `gt core-specs` CLI, `refresh_intake_prompt`
   driver + doctor check + adopter session-start wiring, default-on + opt-out) plus a `### Migration notes`
   subsection (existing projects gain the capability on `gt project upgrade`; `gt project doctor` to verify).
3. **`docs/bootstrap.md`** — "Core specification intake (default)" subsection in the project-init flow.
4. **`docs/start-here.md`** — "Core Specification Intake" feature entry to §2 following the established
   Problem → Solution pattern.
5. **`docs/user-journey.md`** — Phase 0 enrollment note, Phase 1 per-session re-prompt note, and an
   `F9 | Core Specification Intake | … | 0, 1` row in the feature-map table.
6. **`docs/method/02-specifications.md`** — "Core specification intake" subsection under "The spec-first
   workflow" (init prompting, persisted-evidence completion, automation-safe / opt-out).

**Adoption-evidence tests (2):**

7. **`tests/test_core_spec_intake.py`** — `test_clean_adopter_end_to_end_intake_journey`: scaffold → enrolled
   + initial prompt → mark slot → hook re-prompt advances to next slot → complete all → cessation.
8. **`tests/test_upgrade.py`** — `test_upgrade_existing_project_gains_core_spec_intake_wiring`: old-version
   project with a pre-intake session-start hook + a pre-existing spec → `execute_upgrade()` → upgraded hook
   carries the intake wiring AND the pre-existing spec is uncorrupted.

Agent Red dogfood dashboard/backlog evidence remains out of scope per the PAUTH (separate Agent Red surfaces).

## Specification-Derived Verification

| Spec / criterion | Verification | Result |
|---|---|---|
| SPEC-CORE-INTAKE-001 / -002 (end-to-end init→session re-prompt + cessation) | `test_clean_adopter_end_to_end_intake_journey` | PASS |
| DCL-CORE-INTAKE-001 (existing project gains capability on upgrade, no spec corruption) | `test_upgrade_existing_project_gains_core_spec_intake_wiring` | PASS |
| DCL-CORE-INTAKE-001 (scaffold backward compatibility) | existing `test_scaffold_project.py` + `test_spec_scaffold.py` PASS | PASS |
| Plan exit criterion "docs describe the default behavior accurately" | six doc edits written against the VERIFIED Phase 1–4 behavior | for LO accuracy review |
| Phase 5 scope completeness (all authorized GT-KB doc surfaces) | all six doc surfaces in `-003` `target_paths` edited (cli, changelog, bootstrap, start-here, user-journey, method/02) | DONE |

### Commands executed and observed results

```text
python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests \
  --basetemp=E:/GT-KB/.tmp/pytest-ci-pb5b \
  groundtruth-kb/tests/test_core_spec_intake.py groundtruth-kb/tests/test_upgrade.py \
  groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_spec_scaffold.py -q
  -> 72 passed in 40.98s
     (includes the 2 new adoption tests + the 2 backward-compat suites)

python -m ruff check <2 changed test files>      -> All checks passed!
python -m ruff format --check <2 changed test files> -> 2 files already formatted

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence
  -> preflight_passed: true; missing_required_specs: [];
     packet_hash: sha256:0784055f428b8539bb04f0ed34376e69e80fee39d1c8693a3cd3efab4799b195

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-phase-5-docs-and-adoption-evidence
  -> Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0; exit 0
```

The six `.md` documentation files are not subject to ruff. The in-root pytest temp uses a session-unique
`--basetemp` under the probed-writable `.tmp` directory (the default temp root is not writable in this sandbox).

## Recommended Commit Type

`docs` — the headline deliverable is documentation of the already-VERIFIED feature across six doc surfaces;
the two adoption-evidence tests are supporting verification (no production code change). The diff is
documentation-dominant (6 doc files + 2 test files).

## Files Changed

- `groundtruth-kb/docs/reference/cli.md`
- `groundtruth-kb/docs/changelog.md`
- `groundtruth-kb/docs/bootstrap.md`
- `groundtruth-kb/docs/start-here.md`
- `groundtruth-kb/docs/user-journey.md`
- `groundtruth-kb/docs/method/02-specifications.md`
- `groundtruth-kb/tests/test_core_spec_intake.py` (+1 clean-adopter end-to-end test)
- `groundtruth-kb/tests/test_upgrade.py` (+1 upgrade adoption test)

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
