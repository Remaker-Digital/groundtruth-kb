NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 58f826b2-6551-47df-8edf-ceba6461be29
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-SLICE-3-KB-WORK-ITEM-MIGRATION
Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-3455

# Skill Modernization Slice 3 — kb-work-item → gt CLI Thin Wrapper — Implementation Proposal

bridge_kind: lo_verdict

Document: gtkb-skill-modernization-slice-3-kb-work-item-migration
Version: 001 (NEW)
Date: 2026-05-29 UTC
Project: PROJECT-GTKB-SKILL-MODERNIZATION (this slice work item WI-3455)
Implements: Slice 3+ of gtkb-skill-modernization-scoping (Codex GO at -004)
Recommended commit type: feat

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` — new module: the GOV-12/13 work-item-create verb (WI + linked test + optional phase assignment).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — register `add-work-item` under the `backlog` command group.
- `platform_tests/scripts/test_cli_backlog_add_work_item.py` — new spec-derived tests.
- `.claude/skills/kb-work-item/SKILL.md` — rewrite body as a thin wrapper around the new verb (remove inline `db.insert_*` snippets).
- `.codex/skills/kb-work-item/SKILL.md` — same rewrite for the Codex adapter copy.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — deterministic governed operations belong in services; the verb makes the WI+test+phase chain a deterministic CLI artifact. Primary; in the Slice 3 PAUTH.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-first delivery; in the Slice 3 PAUTH.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive plumbing belongs in services, not session markdown; this slice moves the GOV-12/13 plumbing out of skill markdown.
- GOV-12 (work item triggers test creation) — the verb creates a linked test in the same invocation as the work item.
- GOV-13 (every test assigned to a test-plan phase) — the verb supports optional, parameterized phase assignment via append-only `test_plan_phases.test_ids` versioning.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI + test + phase lifecycle mutations are governed; the verb resolves attribution fail-closed via the mutating resolver.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the platform verb is application-agnostic (phase is a parameter); PLAN-001 phase numbers are supplied by the Agent-Red-flavored kb-work-item skill, not hardcoded in the platform CLI. All artifacts in-root.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — metadata triple present; PAUTH active and includes the declared work item.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section cites all relevant governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below; tests derived from the linked specs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under the canonical bridge protocol; `bridge/INDEX.md` is authoritative; new-version-at-top, append-only.

## Requirement Sufficiency

Existing requirements sufficient. The umbrella scoping (`gtkb-skill-modernization-scoping` GO at -004) defines Slice 3+ as "design and implement `gt` CLI subcommands for deterministic operations; rewrite skill bodies as thin wrappers around governed CLI calls; preserve each skill's governance semantics." GOV-12 and GOV-13 are existing governance specifications. No new requirement is needed; this slice transcribes the GOV-12/13 chain into a deterministic verb.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the motivating principle.
- `DELIB-S364-KB-WORK-ITEM-MIGRATION-SLICE-PAUTH` — owner AUQ authorizing this slice + its PAUTH (S364).
- `gtkb-skill-modernization-slice-0-skill-health-checker` (VERIFIED at -004) — the Slice 0 detector that flagged kb-work-item's inline `db.insert_work_item`/`db.insert_test` (4 findings); this slice removes that bypass. The detector also found kb-batch already compliant (0 findings), so kb-batch is out of scope for this slice.
- `gtkb-gt-backlog-add-cli` (WITHDRAWN at -007) — `gt backlog add` exists (WI candidate capture only); this slice adds the richer GOV-12/13 sibling verb rather than overloading `add`.
- No prior deliberation rejected this approach.

## Implementation Plan

### New verb: `gt backlog add-work-item`

A new module `cli_backlog_add_work_item.py` that composes the existing governed primitives:

1. **Work item (reuses `add_backlog_item`)** — same validated fields + fail-closed harness attribution as `gt backlog add`. No duplication of the allocation/attribution logic; the new module imports and calls it.
2. **Linked test (GOV-12)** — `db.insert_test(id, title, spec_id, test_type, expected_outcome, changed_by, change_reason, ...)`. Verb params: `--test-title`, `--test-type` (choice: assertion|e2e|integration|unit|manual), `--test-spec-id` (defaults to the work item's `--source-spec-id`), `--test-expected-outcome`. Test id allocated monotonically (`TEST-NNNN`).
3. **Phase assignment (GOV-13, optional + parameterized)** — `--test-plan-phase <phase-id>`: when supplied, read the current `test_plan_phases` row, append the new test id to its `test_ids`, and insert a new append-only phase version. When omitted, the test is created unassigned (the caller decides; keeps the platform verb application-agnostic — PLAN-001 is not hardcoded).
4. **Output** — JSON with `work_item_id`, `test_id`, and `phase_assignment` (or `null`). `--dry-run` reports allocations without writing.

Attribution: same fail-closed mutating resolver as `add_backlog_item` (no `--changed-by`, no fallback literal). The verb is registered under the existing `backlog` group in `cli.py`.

### Skill rewrite (thin wrapper)

`.claude/skills/kb-work-item/SKILL.md` and `.codex/skills/kb-work-item/SKILL.md` rewritten: remove the inline `db.insert_work_item(...)` / `db.insert_test(...)` Python snippets (Steps 3-4); replace with an invocation of `gt backlog add-work-item ... --test-title ... --test-type ... --test-plan-phase ...`. The skill retains its GOV-12/13 governance narrative and taxonomy reference; only the mechanical mutation moves to the CLI. The Slice 0 checker re-run must report zero `db_mutation`/`fenced_python` findings for kb-work-item after the rewrite (regression evidence).

## Spec-to-Test Mapping

| Linked Spec | Test (in `test_cli_backlog_add_work_item.py`) | Assertion |
|---|---|---|
| GOV-12 | `test_creates_work_item_and_linked_test` | one `gt backlog add-work-item` call creates a work item row + a linked test row |
| GOV-12 | `test_test_links_to_source_spec_by_default` | `--test-spec-id` defaults to the work item `--source-spec-id` |
| GOV-13 | `test_phase_assignment_appends_test_id` | `--test-plan-phase` appends the test id to that phase's `test_ids` (new version) |
| GOV-13 | `test_phase_assignment_optional` | omitting `--test-plan-phase` creates the test unassigned (no phase mutation) |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_dry_run_writes_nothing` | `--dry-run` reports allocations without work-item/test/phase mutation |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_fail_closed_attribution` | unresolved harness attribution exits non-zero before any DB write |
| `DELIB-S312` (skill-rewrite regression) | `test_kb_work_item_skill_has_no_inline_db_mutation` | Slice 0 checker `scan_text` reports zero `db_mutation`/`fenced_python` findings for both rewritten SKILL.md files |

Test execution command: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cli_backlog_add_work_item.py -v`.

## Acceptance Criteria

- [ ] `gt backlog add-work-item` creates work item + linked test in one invocation (GOV-12); optional `--test-plan-phase` assigns the test (GOV-13).
- [ ] Verb reuses `add_backlog_item` (no duplicated allocation/attribution); fail-closed attribution preserved.
- [ ] Platform verb does not hardcode PLAN-001; phase is a parameter.
- [ ] kb-work-item SKILL.md (.claude + .codex) rewritten as thin wrappers; Slice 0 checker reports zero db_mutation/fenced_python findings for kb-work-item afterward.
- [ ] All mapped tests pass; ruff clean.
- [ ] Implementation confined to the five target_paths; applicability + clause preflights pass.

## Risk / Rollback

- **Risk:** MEDIUM. New CLI verb that mutates work_items + tests + test_plan_phases. Mitigations: reuses the verified `add_backlog_item` primitive + fail-closed attribution; `--dry-run`; phase assignment is opt-in and append-only (no destructive update); skill rewrite is documentation-class.
- **Rollback:** `git checkout` the five target files. All MemBase writes are append-only; no destructive migration. The new verb is additive — `gt backlog add` and the existing skill behavior are unaffected until the skill rewrite lands.
- **Scope boundary:** kb-batch (already compliant per Slice 0), other kb-* skills, send-review (Slice 1), the authoring standard (Slice 2), and metadata caps (Slice N) are out of scope and require their own proposals.

## Owner Decisions / Input

- **Gap 3 selection** (AskUserQuestion, S364): owner directed Gap 3 (kb-work-item/kb-batch skills bypass CLI).
- **Next-step after Slice 0 VERIFIED** (AskUserQuestion, S364): owner chose "Scope the kb-work-item migration slice (Recommended)" — design+build the `gt` verb for the GOV-12/13 chain, rewrite kb-work-item as a thin wrapper, capture the work item, and authorize the PAUTH (script/CLI + skill-doc + test mutation classes). Recorded as `DELIB-S364-KB-WORK-ITEM-MIGRATION-SLICE-PAUTH`; PAUTH `PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-SLICE-3-KB-WORK-ITEM-MIGRATION` active.
- No further owner decision is required to review this proposal. The CLI-verb shape is a Prime/Loyal-Opposition design matter under this slice's authorization.

## Notes for Loyal Opposition

- The phase-assignment design is intentionally parameterized to avoid hardcoding the Agent-Red PLAN-001 taxonomy into the platform CLI (per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`). If LO prefers GOV-13 deferred to a follow-on sub-slice (work-item + test only this slice), that is an acceptable scope reduction — flag it and I will revise.
- This is AXIS-1 dispatchable review; no owner-AUQ-mid-stream is needed for the verdict.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
