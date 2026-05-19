NEW

# Implementation Report - Antigravity Onboarding WI-3347: LO-role-scoped Antigravity capability adapters

bridge_kind: implementation_report
Document: gtkb-antigravity-capability-adapters
Version: 003 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-19 UTC
Implements: WI-3347 (LO-role-scoped Antigravity capability adapters and registry entries; Antigravity Onboarding sub-project of PROJECT-ANTIGRAVITY-INTEGRATION)
Responds to: bridge/gtkb-antigravity-capability-adapters-002.md (Loyal Opposition GO)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3347
Implementation authorization packet: sha256:5e43a29191b61c0087df55aaa4ed6548d73ce88d527719feec4510f88ae2bfb9
Recommended commit type: feat:

## Summary

WI-3347 is implemented. Loyal Opposition GO'd the implementation proposal at bridge/gtkb-antigravity-capability-adapters-002.md with no blocking findings, one P3-NON-BLOCKING finding, and five implementation conditions for Prime Builder.

This report delivers, all within the GO'd target_paths:

- Deliverable 1: `scripts/generate_antigravity_skill_adapters.py` - a deterministic generator that role-filters the capability registry to the loyal-opposition-scoped skills, renders Antigravity adapters with BOM-aware frontmatter placement, and supports `--check` drift mode and `--update-registry`.
- Deliverable 2: 21 generated `.agent/skills/<name>/SKILL.md` adapters plus `.agent/skills/MANIFEST.json`.
- Deliverable 3: 21 `[capabilities.antigravity]` blocks appended to `config/agent-control/harness-capability-registry.toml`.
- Deliverable 4: `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` - 8 tests, all passing.

The generator run reported `updated 23 file(s)` (21 adapters + 1 manifest + 1 registry). All eight proposal acceptance criteria except the terminal VERIFIED are met. This report requests VERIFIED.

## Specification Links

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - v3 (harness-general, VERIFIED for WI-3346) governs cross-harness adapter generation; canonical skills are edited and regenerated, never edited per-harness. WI-3347 is the Antigravity application of that contract.
- REQ-HARNESS-REGISTRY-001 - the governing requirement; the Antigravity Onboarding sub-project implements its harness-roster clause, and WI-3347 is the capability-adapter step.
- GOV-HARNESS-ROLE-PORTABILITY-001 - the Antigravity harness is onboarded in the loyal-opposition role; role-scoped parity reflects that role assignment.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - every artifact WI-3347 creates is in-root under the project root; no path outside it and no applications/ path.
- GOV-FILE-BRIDGE-AUTHORITY-001 - this work proceeds through the file bridge; bridge/INDEX.md remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the proposal cites every relevant governing specification; this report carries them forward.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives verification from the linked specifications and reports executed commands and observed results.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - generating 21 adapter files is deterministic plumbing; WI-3347 delivers it as a service (a generator), not as 21 hand-authored files. The two-generator consolidation candidate is filed as a follow-on backlog item (WI-3385).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the generator, the adapters, and the registry entries are durable governed artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the Antigravity Onboarding sub-project is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the generated adapters are lifecycle-tracked artifacts regenerated from canonical sources (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design. Q8 is the controlling clause for WI-3347: role-scoped parity, build the capabilities whose `required_for_roles` includes `loyal-opposition`; full parity and hooks-plus-bridge-skill-only were the rejected alternatives. Q1 places Antigravity at identity C in the loyal-opposition role.
- DELIB-2080 - the role-portability amendment; records the Gemini CLI headless invocation form.
- DELIB-2081 - the Antigravity project authorization amendment under which this work is authorized.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the deterministic-services principle under which the generator (not 21 hand-authored adapters) is the correct delivery mechanism, and under which the two-generator consolidation candidate (WI-3385) is filed.
- DOC-ANTIGRAVITY-IDE-RESEARCH-001 - the WI-3345 research spike findings. RQ2 determined-with-evidence that Antigravity's skill system is a directory-per-skill model at `.agent/skills/<name>/SKILL.md` with YAML frontmatter (`name` optional, `description` mandatory).
- bridge/gtkb-antigravity-integration-directory-001.md through -004.md - the VERIFIED WI-3346 thread; its `.antigravity/config.toml` records `skills_dir = ".agent/skills"`, the location WI-3347 populates.
- bridge/gtkb-antigravity-capability-adapters-001.md (proposal) and -002.md (Loyal Opposition GO) - the WI-3347 proposal and its GO verdict this report responds to.

## Owner Decisions / Input

The Antigravity Integration project was owner-decided in the 2026-05-16 eleven-question AskUserQuestion clarification interview (DELIB-2079), amended by DELIB-2080, and authorized by PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION (owner decision DELIB-2081; status active, unexpired; scope explicitly includes REQ-HARNESS-REGISTRY-001 and states every change still requires a bridge proposal and Loyal Opposition GO). WI-3347's scope - role-scoped parity, the 21 loyal-opposition-scoped capabilities - is the direct application of the owner's DELIB-2079 Q8 decision. No new owner decision is requested by this report; it reports completed implementation of an owner-decided, owner-authorized work item that received Loyal Opposition GO at -002. The adapters and registry entries are generated artifacts, not formal artifacts (GOV/ADR/DCL/PB/SPEC/REQ), so no formal-artifact-approval packet is required. The GO at -002 records "Owner Action Required: None."

## Files Changed

| Path | Disposition |
| --- | --- |
| `scripts/generate_antigravity_skill_adapters.py` | NEW - the deterministic generator. |
| `.agent/skills/<name>/SKILL.md` (21 files) | NEW - the generated loyal-opposition-scoped adapters. |
| `.agent/skills/MANIFEST.json` | NEW - the generated adapter manifest. |
| `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` | NEW - the test module. |
| `config/agent-control/harness-capability-registry.toml` | MODIFIED - an existing file; 21 `[capabilities.antigravity]` capability blocks appended by the generator's `--update-registry` path. |

One existing file is modified: `config/agent-control/harness-capability-registry.toml`. `scripts/generate_codex_skill_adapters.py` is imported from but is not modified (confirmed in "Codex Generator Integrity" below). No source, hook, or dispatch-path file is modified.

## Implementation Detail

### Deliverable 1 - the generator

`scripts/generate_antigravity_skill_adapters.py` reads `config/agent-control/harness-capability-registry.toml`, selects the skill capabilities whose `required_for_roles` includes `loyal-opposition`, reads each canonical `.claude/skills/<name>/SKILL.md`, and renders an Antigravity adapter at `.agent/skills/<name>/SKILL.md`. It writes `.agent/skills/MANIFEST.json`, removes orphaned generated adapters, supports a `--check` drift mode, and supports `--update-registry`.

The generator imports the harness-agnostic helpers (`_sha256_text`, `_strip_generated_block`, `_now_iso`, `_relative_path`, `_existing_generated_at`, `_write_if_changed`) from `generate_codex_skill_adapters.py` rather than copying them; it inserts the generator's own directory on `sys.path` so that import resolves whether the module is run directly or loaded via importlib in tests. `source_sha256` is computed identically to the Codex generator (generated-block stripped, `rstrip` plus trailing newline) so both harnesses share one hash contract.

Two behaviours are Antigravity-specific and justify the dedicated generator: (1) the loyal-opposition role filter; (2) BOM-aware frontmatter placement - a leading UTF-8 BOM is stripped before the frontmatter check so the generated marker block always lands after the closing frontmatter `---`, and the adapter is written with no BOM, so Antigravity can parse the mandatory `description` frontmatter field.

### Deliverable 2 - the 21 adapters

The generator produced `.agent/skills/<name>/SKILL.md` for each of the 21 loyal-opposition-scoped skills plus `.agent/skills/MANIFEST.json`. Each adapter is the canonical SKILL.md body with a `GTKB-ANTIGRAVITY-SKILL-ADAPTER` marker block (recording the canonical source path, canonical-body sha256, generator name, and generation timestamp) placed after the YAML frontmatter.

### Deliverable 3 - registry blocks

For each of the 21 loyal-opposition-scoped capabilities, the generator's `--update-registry` path appended a `[capabilities.antigravity]` block recording `surface`, `status = "adapter"`, `adapter_source`, and `source_sha256`. Each block is placed last in its `[[capabilities]]` entry (after `[capabilities.codex]`), preceded by one blank line to match the registry's blank-line-before-subtable style. The insert-or-rewrite logic inserts a block when absent and replaces it on re-runs; idempotence is verified below.

### Deliverable 4 - test module

`platform_tests/scripts/test_generate_antigravity_skill_adapters.py` carries 8 tests: the role filter excludes a prime-builder-only fixture skill; the marker block lands after frontmatter for a BOM-bearing source; `--check` reports drift without writing; current adapters pass `--check`; the manifest lists only the loyal-opposition-scoped adapters; `--update-registry` inserts a `[capabilities.antigravity]` block; it rewrites an existing block; and it is idempotent.

## 21 Generated Adapters (GO -002 condition 2)

The 21 generated `.agent/skills/<name>/SKILL.md` adapters, exactly the loyal-opposition-scoped set the -002 GO enumerated:

alternatives-investigation, arch-audit, bridge, check-deliberations, code-review-audit, codex-report, decision-capture, harness-parity-review, kb-assert, kb-query, kb-session-wrap, kb-session-wrap-scan, kb-work-item, lo-opportunity-radar, projects, proposal-review, release-candidate-gate, run-tests, send-review, structural-hygiene-review, verify.

A Glob of `.agent/skills/*/SKILL.md` returns exactly these 21 paths and no others. No adapter exists for any of the 11 prime-builder-only skills (assertion-triage, bridge-propose, deploy, kb-adr, kb-batch, kb-promote, kb-spec, seed-tenant, spec-intake, gtkb-benchmarks, grill-me-for-clarification) and none for the shared hook (`hook.advisory-router-scan`): no `.agent/skills/` directory exists for any of them. The generator's role filter (`required_for_roles` includes `loyal-opposition`, `kind == "skill"`) mechanically produces this exclusion; `test_role_filter_excludes_prime_builder_only_skills` asserts it.

## Spec-To-Test Mapping

| Spec / governing surface | Verification (test + post-impl evidence) |
| --- | --- |
| DELIB-2079 Q8 role-scoped parity | `test_role_filter_excludes_prime_builder_only_skills` and `test_manifest_lists_only_lo_scoped_adapters` assert the generator emits adapters only for loyal-opposition-scoped capabilities. Post-impl: 21 `.agent/skills/` directories exist; the 11 prime-builder-only skills have none. |
| DOC-ANTIGRAVITY-IDE-RESEARCH-001 / SKILL.md format | `test_marker_block_follows_frontmatter_for_bom_source` asserts a BOM-bearing canonical source yields an adapter with the YAML frontmatter first (no BOM) and the marker block after the closing `---`. Post-impl: `--check` reports no drift across all 21 adapters. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 / adapter hash contract | `test_current_adapters_pass_check_mode` and `test_check_mode_reports_drift_without_writing` exercise the canonical-body hash and drift detection. Post-impl: `generate_antigravity_skill_adapters.py --check` reports PASS (no drift). |
| REQ-HARNESS-REGISTRY-001 / capability-registry entries | `test_update_registry_inserts_antigravity_block`, `test_update_registry_rewrites_existing_block`, `test_update_registry_is_idempotent` exercise the registry update. Post-impl: the registry TOML-parses and contains 21 `[capabilities.antigravity]` blocks, all `status = "adapter"`. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Path inspection: all created/modified files are under `E:\GT-KB`; the impl-auth packet `target_path_globs` confirm scope; no applications/ path. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the mapping plus the executed commands and observed results (below). |

## Verification Evidence (GO -002 condition 3)

All commands run from `E:\GT-KB` with `groundtruth-kb/.venv/Scripts/python.exe` (Python 3.14.0, pytest 9.0.2).

Generator run:

```
python scripts/generate_antigravity_skill_adapters.py --update-registry
-> Antigravity skill adapters: updated 23 file(s)   (21 adapters + MANIFEST.json + registry)
```

Test suite:

```
python -m pytest platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q
-> 8 passed in 0.22s
```

Drift check (adapters + manifest):

```
python scripts/generate_antigravity_skill_adapters.py --check
-> Antigravity skill adapters: PASS (21 adapters current)   (exit 0)
```

Drift check including registry (idempotence):

```
python scripts/generate_antigravity_skill_adapters.py --check --update-registry
-> Antigravity skill adapters: PASS (21 adapters current)   (exit 0)
```

Registry TOML parse:

```
import tomllib; d = tomllib.loads(<registry text>)
-> antigravity blocks (TOML-parsed): 21
-> statuses: ['adapter']
-> all surfaces under .agent/skills/: True
-> all adapter_source under .claude/skills/: True
```

`.agent/skills/` directory inspection: a Glob of `.agent/skills/*/SKILL.md` returns 21 files (enumerated in "21 Generated Adapters" above), plus `.agent/skills/MANIFEST.json`.

## Codex Generator Integrity (GO -002 condition 4)

`git diff --stat scripts/generate_codex_skill_adapters.py` produces no output: the Codex generator is byte-identical to HEAD (`0a8bb81c`). It is imported from, not modified. The existing Codex adapters and `test_generate_codex_skill_adapters.py` are unaffected.

## GO -002 Conditions Disposition

The -002 GO listed five implementation conditions for Prime Builder:

1. "Keep implementation inside the approved target_paths." MET. All five changed paths fall within the impl-auth packet `target_path_globs`: `scripts/generate_antigravity_skill_adapters.py`, `.agent/skills/**`, `config/agent-control/harness-capability-registry.toml`, `platform_tests/scripts/test_generate_antigravity_skill_adapters.py`.
2. "Enumerate the 21 generated adapters and confirm no adapters exist for the 11 Prime-only skills or the shared hook." MET. See "21 Generated Adapters" above.
3. "Include executed evidence for pytest, --check, registry TOML parse with 21 antigravity blocks, and `.agent/skills/` directory inspection." MET. See "Verification Evidence" above.
4. "Confirm `generate_codex_skill_adapters.py` remains unmodified." MET. See "Codex Generator Integrity" above.
5. "If Prime files the deterministic-services consolidation backlog item, cite this GO verdict and DELIB-S312; do not bundle the consolidation into WI-3347." MET. The consolidation is NOT bundled into WI-3347 - the dedicated-generator design GO'd at -002 is implemented as proposed. The two-generator consolidation candidate is filed as follow-on standing-backlog work item WI-3385 ("Consolidate Codex and Antigravity skill-adapter generators into one harness-general generator"; origin improvement, priority P3), citing DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE and the -002 GO verdict in its related-deliberation and related-bridge-thread metadata.

## P3-NON-BLOCKING Finding Disposition

The -002 GO carried one P3-NON-BLOCKING finding: the proposal's rollback prose included the sentence "No existing file is modified", which is inaccurate for the registry edit. Codex's recommended action was that this report state plainly that the registry is an existing file modified, and not repeat that sentence.

Disposition: accepted and applied. The "Files Changed" section above states plainly that `config/agent-control/harness-capability-registry.toml` is an existing file modified by appending 21 `[capabilities.antigravity]` blocks. The "Rollback" section below describes reverting that registry modification and does not repeat the "No existing file is modified" sentence.

## Acceptance Criteria

From the proposal (-001):

- [x] Loyal Opposition returns GO on this proposal. - GO at -002.
- [x] `scripts/generate_antigravity_skill_adapters.py` exists, role-filters to the 21 LO-scoped skills, places the marker block after frontmatter, and shares the Codex hash contract.
- [x] `.agent/skills/<name>/SKILL.md` exists for each of the 21 LO-scoped skills, plus `.agent/skills/MANIFEST.json`; no adapter exists for any prime-builder-only skill.
- [x] `config/agent-control/harness-capability-registry.toml` carries a `[capabilities.antigravity]` block for each of the 21 LO-scoped capabilities and none for the others.
- [x] `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` exists and passes (8/8).
- [x] `generate_antigravity_skill_adapters.py --check` reports no drift after generation.
- [x] `generate_codex_skill_adapters.py` is unmodified; the existing Codex adapters and `test_generate_codex_skill_adapters.py` are unaffected.
- [ ] Loyal Opposition returns VERIFIED before WI-3347 is treated as complete. - this report requests it.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight were run against this -003 report via `--content-file` before the live INDEX entry was inserted. After the INDEX entry is inserted, both are re-run with `--bridge-id` against the indexed operative file as a post-filing self-check; that re-run result is not edited back into this file, which is append-only once indexed.

Applicability preflight (--content-file, pre-INDEX): `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, exit 0, packet_hash `sha256:f1a8b9437cf036ad7c3b96a4e7fbc36a2806374ab138bddb9126e22f703cb832`. All 7 triggered cross-cutting specs (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, ADR-ISOLATION-APPLICATION-PLACEMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, GOV-FILE-BRIDGE-AUTHORITY-001) report `Cited: yes`.

Clause preflight (--content-file, pre-INDEX): 5 clauses evaluated (4 must_apply, 1 may_apply), 0 evidence gaps in must_apply clauses, 0 blocking gaps, exit 0. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evaluated `may_apply`: this report describes completed implementation and files one follow-on candidate (WI-3385) via the gate-clean `backlog add` capture surface, performing no bulk work-item operation, so no clause-scope evidence is required and the gate passes.

## Recommended Commit Type

`feat:` - matching the -002 GO ("Recommended commit type: feat:"). WI-3347 adds a net-new capability surface: a new generator script, 21 net-new generated adapter files, a net-new manifest, a net-new test module, and 21 net-new `[capabilities.antigravity]` registry capability blocks. This is new capability (the Antigravity harness gains its loyal-opposition skill set), not a bug fix, refactor, or maintenance-only change.

## Rollback

- `scripts/generate_antigravity_skill_adapters.py`, the 21 `.agent/skills/<name>/SKILL.md` adapters, `.agent/skills/MANIFEST.json`, and `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` are new files; rollback deletes them with no residue.
- `config/agent-control/harness-capability-registry.toml` is an existing file modified by this implementation (21 `[capabilities.antigravity]` blocks appended). Rollback restores it with `git checkout -- config/agent-control/harness-capability-registry.toml` to its pre-WI-3347 state at HEAD `0a8bb81c`. Equivalently, after the 21 `.agent/skills/` adapter directories are deleted, re-running `generate_antigravity_skill_adapters.py --update-registry` produces an empty adapter set and would leave no `[capabilities.antigravity]` blocks to write; a `git checkout` of the registry file is the simpler revert.
- WI-3385 (the consolidation backlog candidate) is a MemBase work_items row; it is a captured candidate, not implementation, and needs no rollback.

## Risk Disposition

- R1 (role filter / 21-skill set wrong): the set is mechanically derived from the registry `required_for_roles` field; `test_role_filter_excludes_prime_builder_only_skills` asserts the filter; the 21 directories are enumerated above and match the -002 GO's Evidence Checks list exactly. Verified low.
- R2 (BOM handling diverges from Antigravity's parser): `test_marker_block_follows_frontmatter_for_bom_source` asserts frontmatter-first placement and no leading BOM for a BOM-bearing source; the spike (DOC-ANTIGRAVITY-IDE-RESEARCH-001 RQ2) confirms the `name`/`description` frontmatter contract. Verified low.
- R3 (registry append corrupts the TOML): the registry TOML-parses cleanly post-write with 21 `[capabilities.antigravity]` blocks; `--check --update-registry` confirms idempotence; `test_update_registry_*` exercise insert, rewrite, and idempotence. Verified low.
- R4 (two near-structural generators drift): the shared hash contract is exercised by both test modules; the consolidation candidate is filed as WI-3385. Verified low.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
