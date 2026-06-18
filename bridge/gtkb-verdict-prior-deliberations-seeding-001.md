NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-18T04-40-00Z-prime-builder-B-2770ee
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Verdict-File Prior-Deliberations Seeding Across Interactive Verdict Paths (WI-4639)

bridge_kind: implementation_proposal
Document: gtkb-verdict-prior-deliberations-seeding
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4639

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/verify/helpers/write_verdict.py", ".claude/skills/verify/SKILL.md", ".claude/skills/bridge/SKILL.md", ".claude/skills/proposal-review/SKILL.md", ".codex/skills/verify/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/proposal-review/SKILL.md", "platform_tests/skills/test_verify_prior_deliberations_pre_population.py", "groundtruth-kb/tests/fixtures/scaffold_golden/**"]

implementation_scope: verdict_prior_deliberations_seeding
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
protected_source_mutation_in_scope: true

## Summary

WI-4639 brings the propose-side "review-and-prune, not remember-to-populate"
Prior-Deliberations seeding to the **verdict-authoring** surface. The propose
side auto-seeds a proposal's `## Prior Deliberations` section from the canonical
glossary plus optional semantic search (`pre_populate_prior_deliberations` in
`write_bridge.py`); the verdict side has no equivalent today, so Loyal
Opposition must remember to search deliberations by hand.

An 8-agent investigate→design→adversarial-verify pass established the design and
corrected an initial overclaim. Key facts: (1) verdict authoring is
**prompt-only** — the verdict-authoring skills are `SKILL.md`-only with no
composer code; (2) the seeding primitives live only in the git-ignored skill
helper `write_bridge.py`, are dependency-clean, and are not in the importable
package; (3) "verdict authoring" is **not one surface** — it spans the `verify`
skill (post-impl VERIFIED/NO-GO), the `bridge` skill's Respond step (GO/NO-GO/
VERIFIED), and the `proposal-review` skill (GO/NO-GO). Per owner decision
(AskUserQuestion 2026-06-18), WI-4639 covers **all interactive verdict paths**;
the LLM-harness `.lo-verdict.md` path is a named follow-on (**WI-4648**).

Design: extract the seeding primitives into a new importable module
`groundtruth_kb/bridge/prior_deliberations.py`, re-export from `write_bridge.py`
(behavior-unchanged), add a thin verify-side helper `write_verdict.py` that
calls the shared primitive, and add a documented seeding step to the three
interactive verdict `SKILL.md` surfaces (+ Codex adapter parity). No retrieval/
seeding logic is duplicated.

## Specification Links

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — the canonical glossary is the
  Deliberation Archive's primary read surface; Prior-Deliberations seeding is
  the mechanism that surfaces prior decisions at authoring time. (Governance
  basis for this work.)
- `ADR-DA-READ-SURFACE-PLACEMENT-001` — DA read-surface placement; the
  propose-side Path-D precedent this proposal mirrors onto verdicts.
- `DCL-CONCEPT-ON-CONTACT-001` — glossary/DA-on-contact discipline backing the
  seeding.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — verdict files are part of the canonical
  append-only numbered bridge chain; seeding edits authoring docs, never bridge
  state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps
  each linked specification to executed tests.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / `.claude/rules/sot-read-discipline.md` —
  the shared module is the single canonical home for the seeding primitives;
  logic is reused, not re-derived or duplicated (see § Reuse Rationale).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all added/modified files are
  in-root under `E:\GT-KB`; the new module ships via the installed
  `groundtruth_kb` package (pip), so the adopter scaffold is **not** modified
  and no `applications/`-class path is touched.
- `GOV-STANDING-BACKLOG-001` — `WI-4639` is the durable backlog authority; the
  LLM-harness follow-on is `WI-4648`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` /
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the project authorization is
  additive, bounded to this project/work item/target paths; not a bridge bypass.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

Test derivation from these specs is in § Spec-Derived Verification Plan.

## Prior Deliberations

- `gtkb-verify-verdict-author-skill-slice-1` (VERIFIED at `-004`;
  `DELIB-20261942`, WI-3261) — created the `/verify` skill this WI extends with
  seeding.
- DA Read Surface Correction (`DELIB-1560`, `DELIB-1561`, `DELIB-1538`,
  `DELIB-1899`) — the glossary backfill + expansion hook the seeding relies on;
  the governance lineage for `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`.
- `gtkb-adr-dcl-clause-auto-discovery-slice-5` (VERIFIED at `-008`) — the
  **merged base** for `.claude/skills/verify/SKILL.md`, the `.codex/skills/verify`
  adapter, and `harness-capability-registry.toml`. WI-4639's SKILL.md line
  citations and the `.codex` adapter base are taken from the post-slice-5 state;
  WI-4639's adapter regen supersedes slice-5's prior adapter values for the
  touched skills.
- `gtkb-bridge-thread-read-cli` (WI-4634, NEW) — **no target_path collision**:
  its paths are `bridge/read_commands.py` / `cli.py` /
  `test_bridge_read_commands.py`, none of which WI-4639 touches.
- `gtkb-codex-adapter-references-mirror` (WI-4598/4614, in-flight) — touches the
  generator `scripts/generate_codex_skill_adapters.py` + 8 *other* skills'
  `references/**`; it does **not** touch the verify/bridge/proposal-review
  adapter `SKILL.md` files, so WI-4639's adapter regen does not collide on
  target paths (see § Risk for the generator-version coordination note).
- `WI-4648` — named follow-on for the LLM-harness `.lo-verdict.md` verdict path
  (out of scope here).

This proposal is filed as a versioned file in the append-only numbered bridge
chain (`bridge/gtkb-verdict-prior-deliberations-seeding-001.md`); the
post-implementation report follows as the next numbered file, with no deletion
or rewrite of any prior version.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-2330` — seed=search; bridge_thread; Loyal Opposition Review - Startup Enhancements P2 Freshness Contract REVISED
- DA: `DELIB-20264927` — seed=search; bridge_thread; Loyal Opposition Review - Startup Enhancements P2 Freshness Contract REVISED
- DA: `DELIB-1524` — seed=search; bridge_thread; Loyal Opposition Review - Owner-Decision Tracker Pattern Bounds + AUQ Resolution
- DA: `DELIB-2420` — seed=search; bridge_thread; Loyal Opposition Review - Artifact Recorder CLI Scoping Advance
- DA: `DELIB-20261591` — seed=search; bridge_thread; Loyal Opposition Verification - Owner-Decision-Tracker Baseline Restoration

## Owner Decisions / Input

- AskUserQuestion 2026-06-18 — scope: "All interactive verdict paths" (verify +
  bridge Respond + proposal-review; LLM-harness deferred to **WI-4648**).
- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`
  (`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`) — owner/governance
  authorization to propose implementation for all unimplemented `PROJECT-GTKB-
  MAY29-HYGIENE` work items, including `WI-4639`.

No new owner input is requested. No formal DA/GOV/SPEC/PB/ADR/DCL mutation.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `ADR-DA-READ-SURFACE-PLACEMENT-001`, and
`DCL-CONCEPT-ON-CONTACT-001` already establish that prior decisions must be
surfaced at authoring time via the glossary/DA read surface; WI-4639 extends the
existing propose-side mechanism to the verdict surface. No new specification is
required before implementation.

## Implementation Design

### 1. Shared module (extraction; reuse, no duplication)

Create `groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py` holding
the canonical definitions of `pre_populate_prior_deliberations`,
`_glossary_seed_ids_for_topic`, `_find_prior_deliberations_section`,
`_format_helper_entry`, `_insert_prior_deliberations_block`,
`_try_open_default_db`, and their constants (`_PRIOR_DELIBS_HEADING`,
`DEFAULT_GLOSSARY_PATH`, `DEFAULT_PREPOPULATION_LOG`,
`DEFAULT_PRE_POPULATION_LIMIT`, `DEFAULT_DB_PATH`, `NO_PRIOR_DELIBS_PLACEHOLDER`,
the glossary regexes). Moved verbatim from `write_bridge.py`; sole external dep
is `groundtruth_kb.db.KnowledgeDB`. This is the single canonical home both the
propose and verdict surfaces consume.

`write_bridge.py` (live `.claude/` copy **and** template
`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` copy)
re-exports from the shared module:
`from groundtruth_kb.bridge.prior_deliberations import (...)`. Its public
surface, `__all__`, and the `globals()["pre_populate_prior_deliberations"]`
self-calls (~lines 801/854) keep working unchanged because the re-exported names
land in module globals. The existing top-level `sys.path` injection (lines
49-54) and the proven `import_module("groundtruth_kb.governance.credential_patterns")`
at line 56 confirm `groundtruth_kb` resolves at module-load time even when
`write_bridge.py` is path-loaded under a synthetic name — so the two existing
path-load consumers (`.claude/skills/bridge/helpers/revise_bridge.py`,
`.claude/skills/bridge/helpers/impl_report_bridge.py`) remain green. The template
edit is scoped to the pre_populate region **only**, preserving the template-only
legacy stubs (`compose_index_update`, `_update_bridge_index`, etc.) and their
`__all__` entries that the live copy lacks.

### 2. Verify-side helper

Create `.claude/skills/verify/helpers/write_verdict.py` (first Python under the
verify skill). It inserts `groundtruth-kb/src` on `sys.path` via the same
`_discover_project_root` pattern as `write_bridge.py`, imports the shared module
by package path, and exposes a seeding entry point: given the thread slug (the
verdict shares the proposal thread's kebab slug) and the verdict body, it calls
`pre_populate_prior_deliberations(slug, body, db=None, log_path=<verify-namespaced>)`
and returns the seeded body for the reviewer to prune. It passes an explicit
verify-namespaced `log_path` (`.gtkb-state/bridge-verify-helper/last-prepopulation.json`)
so verdict-side seeding telemetry never collides with the propose-side
`.gtkb-state/bridge-propose-helper/` audit namespace.

### 3. Documented seeding step on all three interactive verdict surfaces

Add a "pre-write Prior-Deliberations seeding" step (mirroring the existing
`gt deliberations search` step) to:
- `.claude/skills/verify/SKILL.md` (post-impl VERIFIED/NO-GO),
- `.claude/skills/bridge/SKILL.md` (Respond step: GO/NO-GO/VERIFIED),
- `.claude/skills/proposal-review/SKILL.md` (GO/NO-GO proposal review).

Each step instructs the reviewer to run `write_verdict.py --slug <slug>` to
pre-populate `## Prior Deliberations`, review/prune the helper-suggested
candidates, then author the verdict via Write. The verdict template's existing
`## Prior Deliberations` heading is retained byte-exact so the shared
`_PRIOR_DELIBS_HEADING = "## Prior Deliberations"` find/insert logic works
without parameterizing the heading.

### 4. Codex adapter parity

Regenerate the Codex adapters for the three touched skills
(`.codex/skills/{verify,bridge,proposal-review}/SKILL.md`) via the standard
`scripts/generate_codex_skill_adapters.py` so a Codex-as-LO interactive session
sees the same seeding step. WI-4639 **runs** the generator; it does not edit it
(generator is owned by the in-flight WI-4598/4614 — see § Risk for sequencing).

### Reuse Rationale (sot-read-discipline / DRY)

Option A (shared module) is the only choice satisfying the WI-4639 mandate
("mirror WITHOUT duplicating") and sot-read-discipline's reuse-canonical-
primitives discipline. It moves the logic out of the git-ignored `.claude/`
skill helper into the correct importable package home (`groundtruth_kb.bridge`,
already on `sys.path`). Rejected: (B) cross-skill path-import of the whole
`write_bridge.py` (drags credential/author-metadata/work-intent imports and
cements a Prime→LO file coupling); (C) duplicating the logic (directly contrary
to the mandate; the placeholder string is already cross-surface-coupled, so
duplication worsens drift).

## Adversarial Verification Findings Incorporated

The 3-lens adversarial pass (all returned "concerns") produced these must-fixes,
all incorporated above and in the verification plan:

- **P1 coverage/overclaim:** "verdict authoring" is 3+ surfaces. → Scope expanded
  per owner AUQ to all interactive paths (verify + bridge + proposal-review); the
  LLM-harness `.lo-verdict.md` path is explicitly **out of scope** (WI-4648), not
  silently omitted.
- **P1 GO-verdict path:** GO verdicts (proposal-review) were uncovered. → Now in
  scope.
- **P1 slice-5 base:** `verify/SKILL.md` + `.codex` adapter + registry were last
  edited by VERIFIED slice-5. → Acknowledged as merged base (§ Prior
  Deliberations); re-confirm at filing.
- **P1 write_bridge path-load consumers:** `revise_bridge.py` /
  `impl_report_bridge.py` (in `.claude/skills/bridge/helpers/`, not
  `bridge-propose/helpers/`) path-load `write_bridge.py`. → Their tests are in
  the regression plan; import-resolution proven (above).
- **P2 golden fixture:** the template `write_bridge.py` is byte-compared by
  `tests/adopter/test_golden_fixture_diff_per_version.py`. → Golden regen step
  added (`scripts/_capture_scaffold_golden.py`); fixture glob in target_paths.
- **P2 honesty:** the verify-side flip is **procedural** (a skippable documented
  step), not the propose side's mechanical auto-call inside `propose_bridge`. →
  Framed honestly; mechanical enforcement is a future slice, not claimed here.
- **P3s:** verify-namespaced `log_path` (incorporated); corrected the
  `revise_bridge.py:102` characterization (a placeholder-**rejection** regex
  literal, not a constant import); `bridge/__init__.py` convention (add a
  one-line re-export of the public names for package consistency); scaffold.py
  **not** modified (the module ships via pip, same dependency class as the
  existing `groundtruth_kb.db` import); glossary-seeding reliability stated
  honestly (high-value only for single-concept-term slugs; multi-word thread
  slugs degrade to semantic-search + placeholder, same as the propose side).

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | No credential literals. | Credential scan at filing. | |
| CQ-PATHS-001 | Yes | All paths in-root; new module ships via pip (no scaffold edit). | Bridge preflight + target-path inspection. | |
| CQ-COMPLEXITY-001 | Yes | Pure extraction + thin helper + doc steps; no new logic. | Source review + tests. | |
| CQ-CONSTANTS-001 | Yes | Single canonical home for primitives/constants; no new magic literals. | Re-export import smoke + parity test. | |
| CQ-SECURITY-001 | Yes | Read-only seeding (no mutation); fail-soft on missing glossary/db. | Tests for novel-topic placeholder + opt-out. | |
| CQ-DOCS-001 | Yes | Three SKILL.md steps + Codex adapter parity document the procedure. | Source review + adapter regen. | |
| CQ-TESTS-001 | Yes | New integration test + regression of path-load consumers + golden. | Verification-plan pytest. | |
| CQ-LOGGING-001 | Yes | Verify-namespaced audit log; no collision with propose namespace. | Test asserts verify log path. | |
| CQ-VERIFICATION-001 | Yes | ruff check + ruff format --check (separate gates) on changed Python. | Commands in verification plan. | |

## Spec-Derived Verification Plan

Spec-to-test mapping. New test:
`platform_tests/skills/test_verify_prior_deliberations_pre_population.py`
(importlib-by-path load of `write_verdict.py` + a `_FakeKnowledgeDB`).

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `ADR-DA-READ-SURFACE-PLACEMENT-001`,
  `DCL-CONCEPT-ON-CONTACT-001` (seeding behavior): glossary-seed membership for a
  single-concept slug; novel-topic `NO_PRIOR_DELIBS_PLACEHOLDER` insertion;
  opt-out flag preserves the body; seed+search dedup.
- Integration (the genuinely new behavior, not just the reused primitive): run
  `write_verdict.py` against a **real verdict-file body** (line-1 verdict token +
  the verify SKILL.md section structure) and assert the seeded block lands inside
  `## Prior Deliberations` and does NOT bleed into the following `## ` section
  (e.g. `## Specifications Carried Forward`); assert slug derivation.
- `CQ-LOGGING-001`: assert the verify path writes to
  `.gtkb-state/bridge-verify-helper/` and NOT to the propose namespace.
- Reuse parity (`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / DRY): assert the
  propose-side and verdict-side seeding produce identical output for the same
  input (single shared implementation), and that the re-export name is present
  in `write_bridge.py` module globals (the `globals()[...]` self-call contract).
- Regression of `write_bridge.py` path-load consumers
  (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q --tb=short`.
- Golden fixture (template parity): regenerate with
  `groundtruth-kb/.venv/Scripts/python.exe scripts/_capture_scaffold_golden.py`,
  then run `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py -q --tb=short` GREEN; also re-point the template string-parity assertion at `test_bridge_propose_helper.py` if present.
- Bridge chain validity: `python scripts/bridge_applicability_preflight.py
  --bridge-id gtkb-verdict-prior-deliberations-seeding` and
  `python scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-verdict-prior-deliberations-seeding` report no missing required specs and
  no blocking clause gaps.
- Lint/format (separate gates) on changed Python:
  `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>` and
  `... -m ruff format --check <changed.py>`.

## Acceptance Criteria

1. `groundtruth_kb/bridge/prior_deliberations.py` is the single canonical home;
   `write_bridge.py` (live + template) re-exports with byte-unchanged propose
   behavior (full propose-helper suite green).
2. `write_verdict.py` seeds `## Prior Deliberations` for a verdict body via the
   shared primitive, with a verify-namespaced audit log.
3. All three interactive verdict `SKILL.md` surfaces (verify, bridge,
   proposal-review) document the seeding step; the three Codex adapters match.
4. The integration test proves seeded content lands in the right section and the
   path-load consumers + golden fixture remain green.
5. ruff check + ruff format --check pass for changed Python; both preflights green.

## Non-Goals

- The LLM-harness `.lo-verdict.md` verdict path (openrouter/ollama system
  prompts) — deferred to **WI-4648**.
- Mechanical (PreToolUse-hook) enforcement of the seeding step — the verify-side
  flip is procedural in this WI; mechanical enforcement is a future slice.
- Editing `scripts/generate_codex_skill_adapters.py` (owned by WI-4598/4614);
  WI-4639 only runs it. No scaffold.py change (module ships via pip).
- No KB mutation, work-item status change, or formal-artifact mutation.

## Risk And Rollback

- **Multi-copy parity:** `write_bridge.py` exists in ≥4 places (live `.claude/`,
  template, golden fixture, installed venv). WI-4639 edits live + template and
  regenerates the golden; the venv copy is refreshed by reinstall, not edited.
- **WI-4598/4614 generator coordination:** WI-4639 runs
  `generate_codex_skill_adapters.py`; if that generator is mid-change under
  WI-4598/4614, run the adapter regen with the generator version current at
  implementation time (or sequence after WI-4598/4614 lands). Open question for
  LO: whether the regen requires `--update-registry` (a
  `harness-capability-registry.toml` touch) for a doc-only SKILL.md change, or
  whether adapter-content-only regen suffices. Default plan: adapter-content-only
  regen, no registry change, unless the generator requires otherwise.
- **Prompt-only reliability:** the seeding step is a documented (skippable)
  instruction, not a mechanical hook — the same residual the propose side
  accepted before its auto-call wrapper. Honestly disclosed; WI-4648 + a future
  mechanical-enforcement slice address the rest.
- **Heading assumption:** find/insert hard-matches `## Prior Deliberations`; the
  SKILL.md edits keep that heading byte-exact.
- Rollback: `git revert` of the target paths + golden regen; no state/schema
  change.

## Pre-Filing Preflight Subsection

Candidate-content preflights are run before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verdict-prior-deliberations-seeding --content-file CANDIDATE --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verdict-prior-deliberations-seeding --content-file CANDIDATE
```

Expected: applicability `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`; clause preflight exits 0 with no blocking gaps.

## Recommended Commit Type

`feat:` — adds a new shared module + verify-side helper + a new capability
(verdict-path Prior-Deliberations seeding) across three skill surfaces.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
