NEW

# Antigravity Onboarding WI-3347: LO-role-scoped Antigravity capability adapters

bridge_kind: implementation_proposal
Document: gtkb-antigravity-capability-adapters
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-19 UTC
Implements: WI-3347 (LO-role-scoped Antigravity capability adapters and registry entries; Antigravity Onboarding sub-project of PROJECT-ANTIGRAVITY-INTEGRATION)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3347
target_paths: ["scripts/generate_antigravity_skill_adapters.py", ".agent/skills/**", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"]
Recommended commit type: feat:

## Summary

This is the second implementation proposal of the Antigravity Onboarding sub-project (WI-3346, the integration directory, is VERIFIED). It delivers role-scoped capability parity for the Antigravity harness (identity C): the GT-KB skill capabilities required for the loyal-opposition role, made available as Antigravity-native skill adapters.

DELIB-2079 Q8 decided role-scoped parity, not full parity: build the capabilities whose capability-registry `required_for_roles` includes `loyal-opposition` or `both` (a list containing both `loyal-opposition` and `prime-builder`). Of the 32 skill capabilities in the registry, exactly 21 qualify. Codex (a both-role-equivalent reviewer harness) carries adapters for all 32 in `.codex/skills/`; Antigravity, onboarded solely in the loyal-opposition role per DELIB-2079 Q1, receives only the 21 LO-scoped adapters.

WI-3347 produces a deterministic generator, the 21 generated adapter files, and the capability-registry entries that make the adapters first-class. It deliberately defers harness-parity-tool coverage and the harness registry record to follow-on work (see Out Of Scope).

## Specification Links

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - v3 (harness-general, just VERIFIED for WI-3346) governs cross-harness adapter generation; canonical skills are edited and regenerated, never edited per-harness. WI-3347 is the Antigravity application of that contract.
- REQ-HARNESS-REGISTRY-001 - the governing requirement; the Antigravity Onboarding sub-project implements its harness-roster clause, and WI-3347 is the capability-adapter step.
- GOV-HARNESS-ROLE-PORTABILITY-001 - the Antigravity harness is onboarded in the loyal-opposition role; role-scoped parity reflects that role assignment.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - every artifact WI-3347 creates is in-root under the project root; no path outside it and no applications/ path.
- GOV-FILE-BRIDGE-AUTHORITY-001 - this work proceeds through the file bridge; bridge/INDEX.md remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives verification from the linked specifications.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - generating 21 adapter files is deterministic plumbing; WI-3347 delivers it as a service (a generator), not as 21 hand-authored files. The Design Alternatives section surfaces the two-generator consolidation candidate per this principle.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the generator, the adapters, and the registry entries are durable governed artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the Antigravity Onboarding sub-project is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the generated adapters are lifecycle-tracked artifacts regenerated from canonical sources (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design. Q8 is the controlling clause for WI-3347: role-scoped parity, build the capabilities whose `required_for_roles` includes `loyal-opposition` or `both`; full parity and hooks-plus-bridge-skill-only were the rejected alternatives. Q1 places Antigravity at identity C in the loyal-opposition role.
- DELIB-2080 - the role-portability amendment; records the Gemini CLI headless invocation form.
- DELIB-2081 - the Antigravity project authorization amendment under which this work is authorized.
- DOC-ANTIGRAVITY-IDE-RESEARCH-001 - the WI-3345 research spike findings. RQ2 determined-with-evidence that Antigravity's skill system is a directory-per-skill model at `.agent/skills/<name>/SKILL.md` with YAML frontmatter (`name` optional, `description` mandatory), mapping almost one-to-one onto the canonical `.claude/skills/` convention. Section 7 states skill parity IS achievable for WI-3347.
- bridge/gtkb-antigravity-integration-directory-001.md through -004.md - the VERIFIED WI-3346 thread. Its `.antigravity/config.toml` records `skills_dir = ".agent/skills"` as the location later slices populate; WI-3347 is that population step.
- bridge/gtkb-antigravity-ide-research-spike-001.md through -004.md - the VERIFIED WI-3345 spike thread.

## Owner Decisions / Input

The Antigravity Integration project was owner-decided in the 2026-05-16 eleven-question AskUserQuestion clarification interview (DELIB-2079), amended by DELIB-2080, and authorized by PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION (owner decision DELIB-2081; status active, unexpired; scope explicitly includes REQ-HARNESS-REGISTRY-001 and states every change still requires a bridge proposal and Loyal Opposition GO). On 2026-05-18 the owner directed via AskUserQuestion that the Antigravity onboarding be carried out. WI-3347's scope - role-scoped parity, the 21 LO-scoped capabilities - is the direct application of the owner's DELIB-2079 Q8 decision. No new owner decision is requested by this proposal; it implements an owner-decided, owner-authorized work item. The adapters and registry entries are generated artifacts, not formal artifacts (GOV/ADR/DCL/PB/SPEC/REQ), so no formal-artifact-approval packet is required.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 plus DELIB-2079 Q8 govern WI-3347 fully; the WI-3345 spike (DOC-ANTIGRAVITY-IDE-RESEARCH-001) closed the implementation unknown (the Antigravity skill format). No new or revised GOV/SPEC/REQ/ADR/DCL artifact is required before implementing WI-3347.

## Stale Work-Item Description (surfaced, not a blocker)

The MemBase WI-3347 description reads "Build `.antigravity/skills/` adapters ...". That path is a pre-research guess: WI-3347 was created on 2026-05-16 (DELIB-2079 Q11), before the WI-3345 spike. The spike (DOC-ANTIGRAVITY-IDE-RESEARCH-001, 2026-05-18) determined-with-evidence that Antigravity's actual skill convention is `.agent/skills/<name>/SKILL.md` - `.antigravity/skills/` is not a path Antigravity reads. The owner's 2026-05-19 work order, and the VERIFIED WI-3346 `.antigravity/config.toml` (`skills_dir = ".agent/skills"`), both confirm `.agent/skills/`. This proposal implements `.agent/skills/` (spike-determined, owner-confirmed, config-recorded). Recommendation: the WI-3347 MemBase description should be corrected to `.agent/skills/` during a future work-item hygiene pass; that correction is not bundled into this implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal creates one generator script, 21 generated adapter files plus one generated manifest, and one test module, and appends per-capability `[capabilities.antigravity]` blocks to the existing capability registry. It does not resolve, retire, promote, or batch-mutate work items; it produces no work-item inventory. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not applicable. The single work item cited (WI-3347) is this proposal's own implementing work item under the mandatory project-linkage metadata. The registry edit is an append of declarative per-capability adapter entries generated deterministically from canonical sources, gated by Loyal Opposition GO, not a bulk operation.

## In-Root Placement Evidence

Per ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT, every artifact this proposal creates or mutates is within the project root:

- `scripts/generate_antigravity_skill_adapters.py` - new generator, in-root.
- `.agent/skills/<name>/SKILL.md` (21 files) plus `.agent/skills/MANIFEST.json` - new generated adapters, in-root. `.agent/` is git-tracked: there is no `.agent` pattern in `.gitignore`, so these files version normally (unlike the gitignored `groundtruth.db`).
- `config/agent-control/harness-capability-registry.toml` - existing in-root registry, append-extended.
- `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` - new test module, in-root.

The Antigravity harness installation maintains its own user-profile configuration directory outside the project root. That directory belongs to the harness installation; it is not a GT-KB artifact and is neither created, mutated, nor required as a live dependency by this work. No applications/ path is touched.

## Scope

### Deliverable 1 - the generator `scripts/generate_antigravity_skill_adapters.py`

A deterministic generator analogous to `scripts/generate_codex_skill_adapters.py`. It reads `config/agent-control/harness-capability-registry.toml`, selects skill capabilities whose `required_for_roles` includes `loyal-opposition`, reads each canonical `.claude/skills/<name>/SKILL.md`, and renders an Antigravity adapter at `.agent/skills/<name>/SKILL.md`. It writes `.agent/skills/MANIFEST.json`, removes orphaned generated adapters, supports a `--check` drift mode (report without writing), and supports `--update-registry` to point the `[capabilities.antigravity]` registry blocks at the generated adapters. The `source_sha256` is the canonical-body hash computed exactly as the Codex generator computes it (generated-block stripped, `rstrip` plus trailing newline) so the two harnesses share one hash contract.

Two behaviors differ from the Codex generator and justify a harness-specific generator:

1. Role filter. The Codex generator emits all 32 skills; the Antigravity generator emits only the 21 whose `required_for_roles` includes `loyal-opposition` (DELIB-2079 Q8 role-scoped parity).
2. BOM-aware frontmatter placement. Some canonical `.claude/skills/` sources carry a UTF-8 BOM, which defeats a naive `first-line == "---"` check; the Codex generator then prepends its comment block before the frontmatter. Antigravity parses `.agent/skills/<name>/SKILL.md` YAML frontmatter to obtain the mandatory `description` trigger, so the generated marker block MUST sit after the closing frontmatter `---`. The Antigravity generator strips a leading BOM before the frontmatter check so the block is always placed after the frontmatter.

To minimize duplication, the generator imports the pure, harness-agnostic helpers from `generate_codex_skill_adapters.py` (hashing, generated-block stripping, registry loading) rather than copying them; `generate_codex_skill_adapters.py` itself is not modified.

### Deliverable 2 - the 21 generated adapters

`.agent/skills/<name>/SKILL.md` for each of the 21 LO-scoped skills, plus `.agent/skills/MANIFEST.json`. The 21 directories: alternatives-investigation, arch-audit, bridge, check-deliberations, code-review-audit, codex-report, decision-capture, harness-parity-review, kb-assert, kb-query, kb-session-wrap, kb-session-wrap-scan, kb-work-item, lo-opportunity-radar, projects, proposal-review, release-candidate-gate, run-tests, send-review, structural-hygiene-review, verify. Each adapter is the canonical SKILL.md body with an Antigravity generated-marker block recording the canonical source path, the canonical-body sha256, and the generator name, placed after the YAML frontmatter.

### Deliverable 3 - capability-registry entries

For each of the 21 LO-scoped capabilities, a `[capabilities.antigravity]` block is appended recording `surface = ".agent/skills/<name>/SKILL.md"`, `status = "adapter"`, `adapter_source`, and `source_sha256`. This makes the Antigravity adapters first-class registered capabilities, written by the generator's `--update-registry` path. The 11 prime-builder-only skills and the one shared hook receive no Antigravity entry (role-scoped parity).

### Deliverable 4 - test module

`platform_tests/scripts/test_generate_antigravity_skill_adapters.py`, modelled on `test_generate_codex_skill_adapters.py`: asserts the role filter excludes a prime-builder-only skill, the marker block lands after frontmatter for a BOM-bearing source, `--check` reports drift without writing, current adapters pass `--check`, the manifest is correct, and `--update-registry` writes the `[capabilities.antigravity]` block.

## Out Of Scope (deferred follow-on)

- `scripts/check_harness_parity.py` antigravity-awareness. The parity tool hard-codes `KNOWN_HARNESSES = ("claude", "codex")` and a Codex-only adapter marker. Teaching it the Antigravity harness is a distinct tooling change WI-3347 does not require: the Antigravity adapters are drift-protected by this generator's own `--check` mode and the test module. A follow-on work item should extend `check_harness_parity.py`; this proposal recommends it but does not bundle it.
- WI-3348 (the `gt harness register` harness-C MemBase record) and WI-3349 (end-to-end Gemini CLI dispatch verification) remain their own work items.

## Files Expected To Change

- `scripts/generate_antigravity_skill_adapters.py` - NEW generator.
- `.agent/skills/<name>/SKILL.md` x21 plus `.agent/skills/MANIFEST.json` - NEW generated adapters.
- `config/agent-control/harness-capability-registry.toml` - 21 `[capabilities.antigravity]` blocks appended.
- `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` - NEW test module.

No existing source, hook, or dispatch-path file is modified. `generate_codex_skill_adapters.py` is imported from, not modified.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| DELIB-2079 Q8 role-scoped parity | A test asserts the generator emits adapters only for capabilities whose `required_for_roles` includes `loyal-opposition`; a prime-builder-only fixture skill is excluded. Post-impl: the 21 expected `.agent/skills/` directories exist; the 11 PB-only skills have no `.agent/skills/` directory. |
| DOC-ANTIGRAVITY-IDE-RESEARCH-001 / SKILL.md format | A test asserts a generated adapter with a BOM-bearing canonical source has its YAML frontmatter (the mandatory `description`) at the start of the file and the marker block after the closing `---`. Post-impl: each adapter TOML/YAML-frontmatter-parses with a `description`. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 / adapter hash contract | A test asserts the `source_sha256` equals the canonical-body hash (generated-block stripped, normalized) - identical methodology to the Codex generator. Post-impl: `generate_antigravity_skill_adapters.py --check` reports no drift. |
| REQ-HARNESS-REGISTRY-001 / capability-registry entries | A test asserts `--update-registry` writes a `[capabilities.antigravity]` block with surface/status/adapter_source/source_sha256. Post-impl: the registry TOML-parses and contains 21 `[capabilities.antigravity]` blocks. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Path inspection confirms all created files are under the project root; no applications/ path. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed commands and observed results. |

Verification commands for the post-implementation report: `python -m pytest platform_tests/scripts/test_generate_antigravity_skill_adapters.py`; `python scripts/generate_antigravity_skill_adapters.py --check`; a TOML parse of the registry counting `[capabilities.antigravity]` blocks; a directory listing of `.agent/skills/`; plus the two bridge preflights.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/generate_antigravity_skill_adapters.py` exists, role-filters to the 21 LO-scoped skills, places the marker block after frontmatter, and shares the Codex hash contract.
- [ ] `.agent/skills/<name>/SKILL.md` exists for each of the 21 LO-scoped skills, plus `.agent/skills/MANIFEST.json`; no adapter exists for any prime-builder-only skill.
- [ ] `config/agent-control/harness-capability-registry.toml` carries a `[capabilities.antigravity]` block for each of the 21 LO-scoped capabilities and none for the others.
- [ ] `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` exists and passes.
- [ ] `generate_antigravity_skill_adapters.py --check` reports no drift after generation.
- [ ] `generate_codex_skill_adapters.py` is unmodified; the existing Codex adapters and `test_generate_codex_skill_adapters.py` are unaffected.
- [ ] Loyal Opposition returns VERIFIED before WI-3347 is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this -001 draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing. Expected: applicability `preflight_passed: true`, `missing_required_specs: []`; clause preflight exit 0, no blocking gaps. Any non-empty missing-specs list is a self-detected defect to be corrected before INDEX update. The resulting packet hashes are recorded below after the run.

Applicability preflight (--content-file, pre-INDEX): `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:2ed4f9525b2c6e3bee808989092f19b8401f8426e33268f8d8ebfb7b1c29cdde`. All 7 triggered cross-cutting specs report `Cited: yes`.
Clause preflight (--content-file, pre-INDEX): 5 clauses evaluated, all must_apply, 0 evidence gaps, 0 blocking gaps, exit 0.

## Design Alternatives

The recommended design is a dedicated `generate_antigravity_skill_adapters.py` that imports pure helpers from the Codex generator. The considered alternative is to consolidate both generators into one harness-general core (a `HarnessProfile`-parameterized generator) with the Codex and Antigravity entry points as thin shims.

Recommended (dedicated generator) - rationale: WI-3347's scope is the Antigravity adapters; the codebase precedent is harness-named generators (`generate_codex_skill_adapters.py` is itself harness-named); a dedicated generator carries zero regression risk to the VERIFIED Codex generator and its drift-gate; the genuine non-parity (role filter, BOM handling) is cleanly localized.

Rejected for WI-3347 (consolidation now) - it refactors a VERIFIED file and expands WI-3347 beyond its stated scope. Per DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE, the right disposition is to surface the two-generator structural overlap and file it as a backlog candidate: a future work item to consolidate `generate_codex_skill_adapters.py` and `generate_antigravity_skill_adapters.py` into one harness-general generator. Prime Builder will file that backlog item; this proposal flags it here so the overlap is governed, not silently absorbed.

If Loyal Opposition judges consolidation should happen now, NO-GO with that direction and Prime will re-file.

## Risk And Rollback

- R1 (low): the role filter or the 21-skill set is wrong. Mitigation: the set is mechanically derived from the registry `required_for_roles` field; a test asserts the filter; the post-impl report enumerates the 21 directories for review.
- R2 (low): the BOM-handling diverges from Antigravity's parser expectations. Mitigation: a test asserts frontmatter-first placement for a BOM-bearing source; the spike (DOC-ANTIGRAVITY-IDE-RESEARCH-001 RQ2) confirms the `name`/`description` frontmatter contract.
- R3 (low): the registry append corrupts the existing TOML. Mitigation: the generator's `--update-registry` reuses the Codex generator's block-rewrite approach; a test exercises it; the registry is TOML-parse-verified post-write.
- R4 (low): two near-structural generators drift. Mitigation: the shared hash contract is exercised by both test modules; the consolidation backlog item is filed.

Rollback: the generator and test module are new files deletable with no residue; the 21 adapters and the manifest are deletable; the registry `[capabilities.antigravity]` blocks are removable with a corrective edit. No existing file is modified, so there is nothing to revert.

## Loyal Opposition Asks

1. Confirm the 21-skill LO-scoped set is correct: every capability whose registry `required_for_roles` includes `loyal-opposition`, excluding the 11 prime-builder-only skills and the one shared hook. Confirm role-scoped parity (DELIB-2079 Q8) is the correct reading versus full parity.
2. Confirm the dedicated-generator design (import Codex helpers, do not modify the Codex generator) over consolidation-now, and confirm the two-generator consolidation belongs as a deterministic-services backlog item rather than in WI-3347.
3. Confirm `.agent/skills/` is the correct target (spike-determined, owner-confirmed, WI-3346-config-recorded) and that implementing it despite the stale `.antigravity/skills/` WI description is correct.
4. Confirm deferring `check_harness_parity.py` antigravity-awareness to a follow-on work item is acceptable, given the generator's own `--check` mode and the test module drift-protect the adapters.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
