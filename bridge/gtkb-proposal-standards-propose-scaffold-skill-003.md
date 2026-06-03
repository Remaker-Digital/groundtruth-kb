NEW

# Proposal-Standards Slice 4 — /gtkb-propose Scaffolding Skill — Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-proposal-standards-propose-scaffold-skill
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-03T13-55-00Z-prime-builder-s382-resume
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE4

target_paths: ["scripts/gtkb_propose_scaffold.py", ".claude/skills/gtkb-propose/SKILL.md", "platform_tests/scripts/test_gtkb_propose_scaffold.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Implements: GO at `bridge/gtkb-proposal-standards-propose-scaffold-skill-002.md`.

---

## Summary

Implemented Slice 4 (final slice) of PROJECT-GTKB-GOV-PROPOSAL-STANDARDS exactly
as the GO'd `-001` design specified: the `/gtkb-propose` interactive composer
that emits a structurally gate-compliant bridge-proposal scaffold + a self-review
checklist, handing off to the existing `gtkb-bridge-propose` writer. The skill is
registered and discoverable. No deviation from the GO'd design.

## Specification Links

Carried forward from `-001` / `-002`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) — scaffold encodes the bridge
  protocol's required proposal structure; slug collision check honors
  INDEX-is-canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) —
  scaffold pre-populates `## Specification Links` from the always-applicable set.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) — scaffold
  fills the three project-linkage metadata lines.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) — helper is
  unit-tested; the scaffold's verification heading satisfies the gate.
- `GOV-STANDING-BACKLOG-001` v5 (verified) — Slice 4 WI active under the PAUTH.
- `SPEC-2098` v3 (implemented) — Deliberation Archive consumed for seeding.
- Composes with `.claude/skills/bridge-propose/SKILL.md` (writer; unchanged).

## Files Changed (3)

1. **`scripts/gtkb_propose_scaffold.py`** — deterministic helper. `scaffold`
   subcommand validates the slug (kebab + `bridge/INDEX.md` collision check),
   seeds `## Prior Deliberations` from a read-only Deliberation Archive search,
   pre-lists the always-applicable governing specs in `## Specification Links`,
   emits a compliant scaffold (NEW status token first line; 6-field author
   metadata; project-linkage lines filled from validated inputs; inline-JSON
   `target_paths`; every required section; verification heading containing a
   `VERIFICATION_HEADING_TOKENS` substring) to
   `.gtkb-state/propose-drafts/<slug>-001.md`, and prints the self-review
   checklist (both mandatory preflights + phantom-spec sweep + inline-JSON +
   heading-token checks). Read-only against MemBase; writes only the draft.
2. **`.claude/skills/gtkb-propose/SKILL.md`** — orchestration: collect inputs →
   invoke helper → author fills `TODO:` → run self-review checklist → hand off to
   `gtkb-bridge-propose` for the write. Defers the file write to the writer skill.
3. **`platform_tests/scripts/test_gtkb_propose_scaffold.py`** — 11-test unit suite.

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — owner Slice-4 inclusion +
  the S382 resume re-activation of Claude Code as Prime Builder.
- `DELIB-0782` / `DELIB-1191` — `gtkb-deliberation-cli` precedent (DA read surface).
- GO `-002` (Antigravity LO) — approved this design with 0 blocking gaps.

## Owner Decisions / Input

Authorized by `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` ("Include Slice 4")
under `PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4` (active; covers
`GTKB-GOV-PROPOSAL-STANDARDS-SLICE4`; mutation classes `skill_addition`,
`cli_extension`, `test_addition`), plus the S382 resume AUQ re-activating Claude
Code as Prime Builder for this session. No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. The `/gtkb-propose` scaffold operationalizes
existing bridge-protocol structural requirements; it introduces no new system
requirement.

## Spec-Derived Verification Plan

Executed against the final implemented tree (repo venv interpreter; reproducible,
no uv home-cache dependency).

| Specification | Acceptance criterion | Test | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | slug validity + INDEX collision detection | `test_slug_validation`, `test_slug_collision_against_index` | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | always-applicable specs seeded | `test_always_applicable_specs_seeded_by_default`, `test_scaffold_has_all_required_sections` | PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | project-linkage metadata filled | `test_scaffold_has_all_required_sections` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | verification-heading token + inline-JSON target_paths + status-token first line | `test_scaffold_verification_heading_token`, `test_scaffold_target_paths_inline_json`, `test_scaffold_first_line_is_status_token` | PASS |
| `SPEC-2098` | Prior-Deliberations seeding + empty-justification | `test_prior_deliberations_seeding`, `test_prior_deliberations_empty_justification` | PASS |
| design boundary | helper writes only the draft path, never `bridge/` | `test_helper_writes_only_draft_path` | PASS |
| design | self-review checklist lists both preflights + handoff | `test_self_review_checklist_commands` | PASS |

Unit suite:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py -q --no-header -p no:cacheprovider
11 passed in 0.13s
```

CLI smoke (emits scaffold + checklist; exit 0):

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_propose_scaffold.py scaffold --slug demo-smoke-test-thread --work-item WI-9999 --project PROJECT-DEMO --pauth PAUTH-DEMO --slice 4 --no-write
```

Ruff lint + format:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
2 files already formatted
```

## Risk / Rollback

Low. The helper is read-only against MemBase and writes only draft scaffolds
under `.gtkb-state/`; it adds no bridge or KB write path. The skill is additive.
Single-commit revert removes all three files with no effect on existing surfaces.

## Bridge Filing (INDEX-Canonical)

This report is filed as the next version under the
`gtkb-proposal-standards-propose-scaffold-skill` document in `bridge/INDEX.md`;
no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains
the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` — adds the `/gtkb-propose` interactive scaffolding skill + its
deterministic helper + an 11-test unit suite.

## Acceptance Criteria Check

- [x] `/gtkb-propose` helper emits a gate-compliant scaffold (status token, project
      linkage, inline-JSON target_paths, seeded Prior Deliberations, verification
      heading, all required sections).
- [x] Self-review checklist lists both mandatory preflights + phantom-spec sweep + handoff.
- [x] Helper read-only against MemBase; writes only `.gtkb-state/propose-drafts/`.
- [x] SKILL.md composes with `gtkb-bridge-propose` (no duplicate write path); skill registered.
- [x] 11/11 unit tests pass (final tree); ruff lint + format clean.
- [x] All 3 target paths in-root and within the GO'd `-001`/`-002` target_paths.

## Decision Needed From Owner

None. Standing PAUTH + S382 AUQ.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
