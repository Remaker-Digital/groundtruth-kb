NEW
author_identity: claude
author_harness_id: B
author_session_context_id: ad3221a1-e3bc-4d3e-bcec-d3d608598322
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Defect-Fix Proposal - Regression: 5 Codex skill adapters fail strict-YAML load (unquoted bracketed argument-hint) despite WI-4264 marked resolved

bridge_kind: prime_proposal
Document: gtkb-codex-skill-adapter-frontmatter-strict-yaml
Version: 001
Date: 2026-06-11 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4461

target_paths: ["scripts/generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", ".codex/skills/kb-query/SKILL.md", ".codex/skills/kb-spec/SKILL.md", ".codex/skills/kb-work-item/SKILL.md", ".codex/skills/run-tests/SKILL.md", ".codex/skills/seed-tenant/SKILL.md"]

## Claim

This proposal asserts that 5 generated Codex skill adapters (`.codex/skills/{kb-query, kb-spec, kb-work-item, run-tests, seed-tenant}/SKILL.md`) fail to load in Codex because their `argument-hint` frontmatter value is an unquoted multi-bracket string that strict YAML parses as a flow sequence followed by an unexpected second `[`. This breaks Codex skill/hook parity (`ADR-CODEX-HOOK-PARITY-FALLBACK-001`). The fix normalizes `argument-hint` quoting in the adapter generator (`scripts/generate_codex_skill_adapters.py`) and adds a strict `yaml.safe_load` fail-closed validation of generated frontmatter, so the failure class WI-4264 was meant to close is caught at generation time rather than at Codex runtime.

## Defect / Reproduction

**Root cause.** The adapter generator copies source frontmatter verbatim into each `.codex` adapter (`render_adapter`, `scripts/generate_codex_skill_adapters.py:147-155`), and its `validate_skill_frontmatter` (`:101-135`) performs only line-based `key: value` parsing - it never runs a strict YAML parse. The canonical `.claude` sources carry `argument-hint` values such as `argument-hint: [query-type] [filter]`. Claude Code's lenient frontmatter parser tolerates this, but strict YAML (libyaml / Codex's parser) reads the leading `[` as a flow sequence, parses `[query-type]`, then encounters ` [filter]` and raises `expected <block end>, but found '['`.

**Reproduction (strict YAML, this session 2026-06-11).** Parsing each adapter's frontmatter with `yaml.safe_load`:

| Adapter | Error | Offending line |
|---|---|---|
| `kb-query` | expected `<block end>`, but found `[` (col 29) | `argument-hint: [query-type] [filter]` |
| `kb-spec` | expected `<block end>`, but found `[` (col 29) | `argument-hint: [new|update] [SPEC-ID]` |
| `kb-work-item` | expected `<block end>`, but found `[` (col 24) | `argument-hint: [title] [--spec SPEC-ID] [--origin ...]` |
| `run-tests` | expected `<block end>`, but found `[` (col 37) | `argument-hint: [unit|live|pipeline] [options]` |
| `seed-tenant` | expected `<block end>`, but found `[` (col 28) | `argument-hint: [--execute] [--demo] [--embed]` |

This matches the live Codex dispatch stderr (2026-06-11T14:15Z): `ERROR codex_core::session: failed to load skill ...kb-query/SKILL.md: invalid YAML: did not find expected key`. Codex continues but loses these 5 KB-operation skills, degrading its Loyal-Opposition review capability.

**Blast radius.** Exactly these 5 adapters carry the multi-bracket `argument-hint` pattern (grep `^argument-hint:\s*\[.*\]\s*\[` over `.codex/skills/**/SKILL.md` returns 5 files). No other adapter is affected.

**Why WI-4264 regressed.** WI-4264 ("Codex skill-loading failure cleanup", resolved) was to repair adapter loadability and add a deterministic parity/doctor check. Its `validate_skill_frontmatter` is line-based and does not strict-parse, so the flow-sequence defect passes the check and reaches Codex runtime. The fix below closes that gap.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/generate_codex_skill_adapters.py`, `platform_tests/scripts/test_generate_codex_skill_adapters.py`, and the 5 `.codex/skills/*/SKILL.md` adapters.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - **Primary.** Codex hook/skill parity is required; broken adapter loading degrades Codex's parity surface. The fix restores loadability of the 5 KB-operation skills so Codex's Loyal-Opposition capability is intact.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Codex consumes these skills while acting on `bridge/INDEX.md`; the fix touches only generated adapters and the generator, not bridge workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites all relevant cross-cutting specs in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The Specification-Derived Verification Plan maps the linked specs to executable tests (strict-YAML parse assertion).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization / Project / Work Item metadata present above.
- `GOV-STANDING-BACKLOG-001` - WI-4461 is the standing-backlog work item; admitted to PROJECT-GTKB-RELIABILITY-FIXES via active membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Defect captured as WI-4461 before implementation; this proposal is the artifact-lifecycle progression from captured regression to a scoped fix.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner approval to implement WI-4461 collected via AskUserQuestion (see Owner Decisions / Input).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are platform paths under `E:\GT-KB`; no application-subtree placement concern.

## Prior Deliberations

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (v2) - Establishes that `.codex/hooks.json` and skill adapters are a live Codex interception/capability boundary on Windows (CLI >= 0.128.0-alpha.1); a non-loading skill adapter is a parity defect against this ADR.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - Empirical foundation that Codex hooks/skills execute on Windows; this fix restores 5 skills to that working surface.
- WI-4264 ("Codex skill-loading failure cleanup", resolved) - The prior remediation this regresses against. Its line-based validation did not strict-parse frontmatter, so the flow-sequence defect was not caught. No prior deliberation proposed or rejected strict-YAML normalization of `argument-hint`; this is the first treatment of that specific defect class.

## Owner Decisions / Input

- **AskUserQuestion (2026-06-11, this session):** Owner answered the "Unblock + fill" question with "I draft the hooks-fix proposals in parallel", authorizing WI-4462 and WI-4461 to move into implementation scope while WI-4459 awaits Codex review. This is the implementation-approval evidence per the backlog-approval-state rule (auq_resolved to implementation_authorized) and the AUQ-only enforcement stack.
- Project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active, project-wide; allows `source` + `test_addition`), covering WI-4461 via active project membership.

## Proposed Scope

**IP-1 - Normalize `argument-hint` quoting + add strict-YAML fail-closed validation in the generator (`scripts/generate_codex_skill_adapters.py`).**

- Add a normalization step in adapter rendering: for a frontmatter `argument-hint:` line whose value contains `[` and is not already quoted, wrap the value in double quotes (`argument-hint: "[query-type] [filter]"`). This is a minimal, content-preserving transformation; the hint text is unchanged, only quoted.
- Strengthen `validate_skill_frontmatter` (or add a companion check) to run `yaml.safe_load` on the normalized emitted frontmatter and raise `SkillFrontmatterError` when it fails. This makes any strict-YAML violation (not just `argument-hint`) a fail-closed generation error rather than a silent Codex-runtime load failure - the deterministic parity check WI-4264 intended.

**IP-2 - Regenerate the 5 affected adapters.**

Run the fixed generator (`python scripts/generate_codex_skill_adapters.py --update-registry` or the in-repo equivalent) to re-emit the 5 `.codex/skills/*/SKILL.md` adapters with quoted `argument-hint`. Only the 5 multi-bracket adapters change; all others are byte-identical (deterministic generation).

**IP-3 - Regression test (`platform_tests/scripts/test_generate_codex_skill_adapters.py`).**

- Add a test asserting every generated `.codex/skills/*/SKILL.md` frontmatter parses with strict `yaml.safe_load` (the structural invariant: all adapters are strict-YAML-valid).
- Add a targeted test that the generator quotes a bracketed `argument-hint` and that the strict-validation gate rejects a deliberately-malformed frontmatter fixture.

## Specification-Derived Verification Plan

| Spec / Clause | Derived Test | Command |
|---|---|---|
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (adapters loadable by Codex) | `test_all_generated_adapters_strict_yaml_valid` - every `.codex/skills/*/SKILL.md` frontmatter passes `yaml.safe_load` | `python -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py -q` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (gate catches regressions) | `test_generator_strict_validation_rejects_malformed_frontmatter` - generator raises on a malformed fixture | same |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (hint normalization) | `test_bracketed_argument_hint_is_quoted_on_emit` - emitted adapter quotes bracketed `argument-hint` | same |
| Code quality | lint + format gates on changed files | `ruff check <changed.py>` and `ruff format --check <changed.py>` |

## Acceptance Criteria

1. All 5 affected adapters' frontmatters parse with strict `yaml.safe_load` after regeneration.
2. The new generation-time strict-validation gate fails against a deliberately-malformed frontmatter fixture (proving it catches the regression class).
3. The existing generator test suite remains green; non-bracket adapters are byte-identical after regeneration.
4. `ruff check` and `ruff format --check` pass on the changed Python files.
5. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-skill-adapter-frontmatter-strict-yaml` reports `missing_required_specs: []`.
6. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-skill-adapter-frontmatter-strict-yaml` reports no blocking gaps.

## Risks / Rollback

- **Risk:** quoting changes adapter content and could trip a drift/parity `--check` comparison. **Mitigation:** the normalization is deterministic, so `--check` regenerates identical output (no drift); the generated `source_sha256` is computed from the source, which is unchanged.
- **Risk:** strict-validation gate could reject other currently-tolerated adapters at generation time. **Mitigation:** the grep shows only these 5 adapters carry the bracket pattern; if the gate surfaces additional adapters, that is the intended fail-closed behavior and those are fixed in the same regeneration. The full adapter set is regenerated and asserted strict-valid before filing the implementation report.
- **Risk:** Codex could depend on the exact unquoted `argument-hint` text. **Mitigation:** the quoted value carries identical hint text; YAML unquotes it on load, so the runtime string is unchanged.
- **Rollback:** revert the generator change and regenerate (restores prior adapter bytes); the new tests are additive. No data migration, no schema change.

## Files Expected To Change

- `scripts/generate_codex_skill_adapters.py`
- `platform_tests/scripts/test_generate_codex_skill_adapters.py`
- `.codex/skills/kb-query/SKILL.md`
- `.codex/skills/kb-spec/SKILL.md`
- `.codex/skills/kb-work-item/SKILL.md`
- `.codex/skills/run-tests/SKILL.md`
- `.codex/skills/seed-tenant/SKILL.md`

## Recommended Commit Type

`fix`
