NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 8cd56f34-2ccb-41c3-86e3-e099620f487d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Codex skill-adapter generator must mirror canonical references/ (fixes 8-skill packaging drift)

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4598

target_paths: ["scripts/generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", ".codex/skills/kb-work-item/references/**", ".codex/skills/kb-session-wrap/references/**", ".codex/skills/deploy/references/**", ".codex/skills/kb-promote/references/**", ".codex/skills/kb-query/references/**", ".codex/skills/kb-spec/references/**", ".codex/skills/run-tests/references/**", ".codex/skills/seed-tenant/references/**"]

## Summary

WI-4598 (P3, hygiene) and WI-4614 (its sibling) report that the Codex skill
adapter `.codex/skills/kb-work-item/SKILL.md` references `references/taxonomy.md`
and `.codex/skills/kb-session-wrap/SKILL.md` references its `references/`, but
those reference files are absent from the Codex adapter packages — only the
canonical Claude copies (`.claude/skills/<skill>/references/`) exist, forcing a
fallback. The root cause is that `scripts/generate_codex_skill_adapters.py`
generates only the `SKILL.md` adapter and never mirrors the skill's
`references/` directory. This affects an entire class: **8 canonical skills have
a `references/` directory that is missing from their Codex adapter** — `deploy`,
`kb-promote`, `kb-query`, `kb-session-wrap`, `kb-spec`, `kb-work-item`,
`run-tests`, `seed-tenant`. This proposal fixes the generator to mirror
`references/` and regenerates the adapters, resolving WI-4598, WI-4614, and the
remaining 6 drifting skills in one change.

## Problem (root cause, verified)

`generate_codex_skill_adapters.py` builds adapters only from `*/SKILL.md`:

- `_remove_orphan_adapters` (L313-334) globs `skills_root.glob("*/SKILL.md")`
  and only ever touches `SKILL.md` adapter files.
- `generate` (L336+) renders and writes each `SKILL.md` adapter (preserving
  `generated_at` via `_existing_generated_at`, so unchanged adapters do not
  churn) but never copies the canonical skill's `references/` directory.

Consequently a Codex session that follows an adapter `SKILL.md` referencing
`references/<file>.md` finds the file absent and must fall back to the Claude
copy (cross-package coupling) — the exact failure WI-4598/WI-4614 observed. A
verified directory sweep confirms 8 skills drift (canonical `references/`
present, Codex adapter `references/` absent).

## Proposed fix

Extend `generate_codex_skill_adapters.py` so each adapter generation also mirrors
the canonical skill's `references/` directory into the Codex adapter package:

1. In `generate()`, for each adapter whose canonical source skill directory
   (`.claude/skills/<skill>/references/`) contains a `references/` directory,
   mirror its contents (deterministically, all files — not just `*.md`) into
   `.codex/skills/<skill>/references/`, creating the directory as needed and
   overwriting stale copies so the Codex package is a faithful mirror. Reference
   files are copied verbatim (they are reference content, not rendered adapters,
   so they carry no `GENERATED_MARKER`).
2. Extend `--check` mode to report references drift (a missing or stale Codex
   `references/` file) the same way it reports adapter drift, so the
   harness-parity / drift checks surface this class going forward rather than
   letting it silently recur.
3. Extend orphan cleanup so a Codex reference file with no canonical counterpart
   is removed on regeneration (mirroring `_remove_orphan_adapters`'s discipline
   for the reference surface), keeping the mirror exact. (Scoped to
   reference files the generator itself manages.)

Regenerating the adapters then materializes the 8 missing `references/`
directories. Because `generated_at` is preserved for unchanged `SKILL.md`
adapters, the regeneration adds only the `references/` mirrors and does not churn
existing adapter `SKILL.md` content. The fix is scoped strictly to the Codex
generator (`generate_codex_skill_adapters.py`); the Antigravity adapter
generator (in-flight under WI-4441) and the API adapter generator are untouched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-mediated implementation/verification
  authority (applies to all bridge proposals).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the required
  generator regression test (references are mirrored) and spec-derived
  verification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — harness skill-adapter completeness:
  a Codex adapter package must carry the reference material its `SKILL.md`
  depends on, so the Codex harness has parity with the canonical skill.
- `.claude/rules/project-root-boundary.md` + `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
  — all generated reference mirrors are in-root (`.codex/skills/**`), with no
  out-of-root path.
- (advisory) `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Prior Deliberations

- Topic survey of `bridge/` found no existing thread proposing a Codex
  adapter `references/` mirror fix; the recent adapter-generator threads concern
  distinct surfaces: `gtkb-skill-generator-registry-formatting` (VERIFIED;
  registry formatting convergence) and `gtkb-wi4441-antigravity-adapter-generation`
  (the Antigravity generator, a different file). Neither addresses Codex
  `references/` packaging drift.
- WI-4612 (resolved, registry-formatting convergence) is the nearest precedent
  for generator-surface hygiene; this proposal extends generator completeness to
  the reference surface without touching registry formatting.
- This proposal is filed as a versioned bridge file in the append-only numbered
  chain (`bridge/gtkb-codex-adapter-references-mirror-001.md`); the
  post-implementation report follows as the next numbered bridge file with no
  deletion or rewrite of prior versions.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-2638` — seed=search; bridge_thread; Loyal Opposition Verdict - Skill Modernization Slice 3 kb-work-item Migration Re
- DA: `DELIB-20260917` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-06-08T19:51:47Z
- DA: `DELIB-20260964` — seed=search; bridge_thread; Verification Verdict - gtkb-sweep-commit Skill Parity Registration
- DA: `DELIB-20261163` — seed=search; bridge_thread; Verification Verdict - gtkb-sweep-commit Skill Parity Registration
- DA: `DELIB-20261559` — seed=search; bridge_thread; Loyal Opposition Verification - Bridge-Propose Helper Non-Bypass Redesign

## Requirement Sufficiency

Existing requirements are sufficient. WI-4598/WI-4614 prescribe the behavior
(the Codex adapter must carry the referenced material), and
`GOV-HARNESS-ONBOARDING-CONTRACT-001` establishes the adapter-completeness /
harness-parity requirement this fix satisfies. No new or revised requirement is
needed before implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping — tests in
`platform_tests/scripts/test_generate_codex_skill_adapters.py`:

- References mirrored (WI-4598/WI-4614 core +
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):
  `test_generate_mirrors_canonical_references` builds a fixture skill with a
  `references/<file>.md`, runs `generate`, and asserts the file is mirrored into
  the Codex adapter `references/` byte-for-byte.
- Whole-class coverage:
  `test_generate_materializes_all_drifting_references` asserts that after
  `generate`, every canonical skill with a `references/` directory has a
  corresponding non-empty Codex adapter `references/` (no drift remains).
- `--check` reports references drift:
  `test_check_reports_missing_reference_as_drift` asserts `generate(check=True)`
  reports a missing Codex reference file as drift (non-empty changed list),
  parity with adapter drift reporting.
- Orphan reference cleanup:
  `test_generate_removes_orphan_reference` asserts a Codex reference file with no
  canonical counterpart is removed on regeneration.
- SKILL.md adapters unchanged (no churn):
  `test_generate_does_not_churn_existing_adapter` asserts an unchanged canonical
  `SKILL.md` yields a byte-identical adapter (preserved `generated_at`) after the
  references-mirroring change.

Commands (resolved against the GT-KB venv interpreter, which carries ruff):

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py -q
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/generate_codex_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/generate_codex_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py

Plus the regeneration evidence command (materializes the 8 mirrors):

    groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --update-registry

Expected: all tests pass; ruff check and ruff format --check clean on the changed
source/test; regeneration creates the 8 missing `.codex/skills/<skill>/references/`
mirrors with no `SKILL.md` adapter churn.

## Acceptance Criteria

1. The Codex adapter generator mirrors each canonical skill's `references/`
   directory into `.codex/skills/<skill>/references/`.
2. After regeneration, all 8 drifting skills (`deploy`, `kb-promote`, `kb-query`,
   `kb-session-wrap`, `kb-spec`, `kb-work-item`, `run-tests`, `seed-tenant`)
   have their `references/` present (WI-4598 and WI-4614 resolved).
3. `--check` reports references drift; orphan Codex reference files are removed
   on regeneration.
4. Existing `SKILL.md` adapters are not churned (preserved `generated_at`).
5. All mirrors are in-root; the Antigravity and API generators are untouched.
6. ruff check and ruff format --check clean on the changed source and test.

## Risk and Rollback

- Risk: LOW–MEDIUM. The change is additive to the generator (a references-mirror
  pass) plus regenerated reference content. The main risk is unintended churn or
  over-deletion; mitigated by the preserved-`generated_at` no-churn test and by
  scoping orphan cleanup to generator-managed reference files only.
- Blast radius: the Codex generator + its test + the 8 regenerated `references/`
  mirrors. No change to `SKILL.md` adapter rendering, the registry formatter, the
  Antigravity/API generators, dispatch, `cross_harness_bridge_trigger.py`, or
  `scan_bridge.py` (so no conflict with in-flight WI-4600 / WI-4618 / WI-4441).
- Rollback: revert the generator change and delete the regenerated `references/`
  mirrors; the prior (drifting) state returns. No state, schema, or routing
  change.

## Owner Decisions / Input

None required. Implementation authority derives from the active,
owner-decision-backed project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`). WI-4598 and
WI-4614 are unimplemented work items in PROJECT-GTKB-MAY29-HYGIENE; the WI text
prescribes the behavior and the fix is owner-policy-free. No AskUserQuestion
decision is needed.

## Recommended Commit Type

`fix:` — repairs Codex skill-adapter packaging drift (missing reference
material) with no new user-facing capability surface.
