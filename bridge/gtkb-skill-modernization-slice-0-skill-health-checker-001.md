NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 58f826b2-6551-47df-8edf-ceba6461be29
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-SLICE-0-SKILL-HEALTH-CHECKER
Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-3451

# Skill Modernization Slice 0 — Skill-Health Static Checker (Implementation)

bridge_kind: implementation_proposal

Document: gtkb-skill-modernization-slice-0-skill-health-checker
Version: 001 (NEW; implementation proposal for Slice 0 of the GO'd skill-modernization umbrella)
Date: 2026-05-29 UTC

## Summary

Implements Slice 0 of the GO'd skill-modernization umbrella (`gtkb-skill-modernization-scoping`, Codex GO at `-004`). Introduces a read-only static checker `scripts/check_skill_health.py` plus its platform test that detects, in skill markdown, the CLI-bypass patterns the umbrella targets: (a) fenced Python blocks, (b) direct DB-mutation snippets, and (c) direct `bridge/INDEX.md` write instructions outside governed helper paths. This is the lightweight, scoped-first detector that mechanically proves the S373 Gap 3 bypass (`kb-work-item`/`kb-batch` instruct inline `db.insert_*`) and becomes the regression gate that will verify every later kb-* thin-wrapper migration slice.

Scope is checker + tests only. The optional `harness-capability-registry.toml` refresh is explicitly OUT of scope (owner AUQ S364: "Authorize checker + tests only"). No skill markdown is rewritten in this slice; the checker only reports.

## target_paths

- `scripts/check_skill_health.py`
- `platform_tests/scripts/test_check_skill_health.py`

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance; the checker is a deterministic detector that makes the skill-surface health a measurable artifact. **Primary governing spec (in the Slice 0 PAUTH).**
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — modernization work preserves durable traceability; the checker emits a structured report artifact. **In the Slice 0 PAUTH.**
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic plumbing belongs in services, not session markdown; the checker enforces this at the skill-surface layer (a deliberation, cited as the motivating principle).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Slice 0 is read-only (no lifecycle mutation); later kb-* slices mutate. The checker is the gate that the later mutation slices are verified against.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Slice 0 artifacts stay in-root within `E:\GT-KB`: the checker under `scripts/`, its test under `platform_tests/scripts/`, and the run output under `.gtkb-state/skill-health/`. No application-directory placement is involved.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal carries the `Project Authorization:` / `Project:` / `Work Item:` triple; the cited PAUTH is active and includes WI-3451.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section is the satisfaction.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-to-Test Mapping below derives executable tests from the linked specs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under the canonical bridge protocol; `bridge/INDEX.md` is authoritative; this entry inserts the new version at the top of the thread version list with no deletion or rewrite of prior versions.

## Requirement Sufficiency

Existing requirements sufficient. The GO'd umbrella scoping (`gtkb-skill-modernization-scoping-003`) defines Slice 0's scope (the checker + its detections); `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DELIB-S312` supply the governing intent. No new requirement is needed; Slice 0 builds the detector the umbrella already approved.

## Prior Deliberations

- `gtkb-skill-modernization-scoping` (GO at `-004`) — the umbrella scoping that defined Slice 0 (skill-health checker) as the first slice; this proposal implements that slice with its own per-slice authorization (the scoping granted none).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the operating-model principle motivating the checker.
- `INSIGHTS-2026-05-27-06-50-GTKB-SKILLS-GUIDANCE-COMPLIANCE-ADVISORY.md` — the LO advisory that originated the skill-modernization umbrella.
- S373 backlog assessment Gap 3 — surfaced the `kb-work-item`/`kb-batch` CLI-bypass that this checker detects.
- Deliberation Archive search for `skill health checker bypass detection` (run S364 2026-05-29) returned no prior Slice 0 implementation; this is the first.

## Implementation Plan

`scripts/check_skill_health.py` — a read-only static checker over skill markdown (`.claude/skills/**/SKILL.md` and `.codex/skills/**/SKILL.md`). It mutates nothing (no file writes to skills, no DB access). Detections:

1. **Fenced Python blocks** — fenced ` ```python ` … ` ``` ` regions in skill bodies (the umbrella's deterministic-services concern: skills should instruct CLI calls, not embed executable mutation snippets).
2. **Direct DB-mutation snippets** — `db.(insert|update|delete)_<name>(`, `KnowledgeDB(`, `INSERT INTO`, `UPDATE … SET` appearing in skill markdown (the exact `kb-work-item` Step 3/4 pattern: inline `db.insert_work_item(...)` / `db.insert_test(...)`).
3. **Direct `bridge/INDEX.md` write instructions** — prose instructing manual editing/insertion into `bridge/INDEX.md` not routed through the governed `bridge-propose` helper (`write_bridge.py`).

Output: a structured JSON report + human-readable summary written to `.gtkb-state/skill-health/<run-id>/` (in-root, regenerable evidence). Per-finding fields: `skill_path`, `finding_type`, `line`, `snippet`. Exit code: `0` when clean; nonzero when findings are present, with a `--warn-only` flag for the advisory phase (so the checker can run informationally before any enforcement hook is wired in a later slice). Governed-helper allowlist (e.g., `bridge-propose`, `write_bridge.py`, `gt` CLI references) suppresses false positives where a skill correctly delegates.

This slice ships the checker + tests only. It does NOT rewrite any skill, register any hook, or touch config/registry — those are later authorized slices.

## Spec-to-Test Mapping

| Linked Spec | Test (in `platform_tests/scripts/test_check_skill_health.py`) | Assertion |
|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DELIB-S312` | `test_detects_inline_db_mutation` | A fixture skill containing `db.insert_work_item(` is flagged with `finding_type=db_mutation` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_detects_fenced_python_block` | A fixture skill with a ` ```python ` block is flagged with `finding_type=fenced_python` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_detects_direct_index_write_instruction` | A fixture skill instructing manual `bridge/INDEX.md` insertion is flagged with `finding_type=index_write` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_clean_skill_passes` | A fixture skill that delegates to the `gt` CLI / bridge-propose helper produces zero findings |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_emits_structured_report` | The run writes a JSON report with the documented per-finding fields under `.gtkb-state/skill-health/<run-id>/` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_checker_is_read_only` | The checker performs no skill-file mutation and no DB write (verified via fixture-tree mtime + no-DB-handle assertion) |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_warn_only_exit_zero` | With `--warn-only`, findings produce exit 0 (advisory phase); without it, findings produce nonzero exit |

Execution command: `python -m pytest platform_tests/scripts/test_check_skill_health.py -v` (project venv).

## Acceptance Criteria

- [ ] `scripts/check_skill_health.py` exists, is read-only, and implements the three detections.
- [ ] `platform_tests/scripts/test_check_skill_health.py` covers all rows above and passes.
- [ ] Running the checker against the live skill tree flags `kb-work-item` (proving Gap 3); reported as post-impl evidence.
- [ ] Implementation confined to the two `target_paths`; no skill rewrite, no hook registration, no config/registry edit.
- [ ] Applicability + clause preflights pass; no credential-shaped tokens.

## Risk / Rollback

- **Risk:** LOW. New read-only script + tests; no mutation of any existing artifact, no hook wired. False positives are mitigated by the governed-helper allowlist and `--warn-only` advisory mode.
- **Rollback:** `git checkout -- scripts/check_skill_health.py platform_tests/scripts/test_check_skill_health.py` (or `git revert` post-commit). MemBase rows (WI-3451, PAUTH) are append-only and remain.

## Owner Decisions / Input

- **Gap 3 entry** (AskUserQuestion, S364 2026-05-29): Owner chose "Slice 0 first: skill-health checker (Recommended)" — enter the skill-modernization work at the lightweight detector before the kb-* CLI-building slices.
- **Slice 0 authorization** (AskUserQuestion, S364 2026-05-29): Owner chose "Authorize checker + tests only" — establishing PAUTH `PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-SLICE-0-SKILL-HEALTH-CHECKER` (owner-decision `DELIB-S364-SKILL-MODERNIZATION-SLICE-0-PAUTH`; mutation classes `script_create` + `test_create`; registry refresh excluded).
- No further owner decision is required to review this implementation proposal.

## Notes for Loyal Opposition

- AXIS-1 dispatchable implementation review; no owner input needed to GO/NO-GO.
- This slice does NOT rewrite `kb-work-item`/`kb-batch` — it ships the detector that the later (separately-authorized) kb-* thin-wrapper slices will be verified against. Running the checker against the live tree (post-GO) is expected to flag those skills, which is the intended Gap 3 evidence.
- **Recommended commit type:** `feat:` — a new deterministic checker capability + its tests.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
