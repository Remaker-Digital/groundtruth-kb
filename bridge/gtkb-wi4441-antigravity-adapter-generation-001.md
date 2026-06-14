NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4441-antigravity-adapter-generation
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4441
target_paths: ["scripts/generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4441: Antigravity skill-adapter generator out of sync with the 36 registry-declared adapters (parity unreachable)

## Summary

WI-4441 (P2, `cross-harness-tooling`, origin=defect): `config/agent-control/harness-capability-registry.toml` declares 36 antigravity skill adapters, but `scripts/generate_antigravity_skill_adapters.py` produces a set out of sync with that declaration, so `check_harness_parity.py --harness antigravity` stays **FAIL (22 STALE + 14 MISSING)** after regen — the regen acceptance gate (0 stale / 0 missing) is unreachable. This blocks downstream work (FAB-16 / HYG-061 Area 2 was re-scoped out behind this defect).

**Cycle-5 triage (this session) confirms WI-4441 is GENUINELY OPEN, and corrects a mis-framed premise in the WI text:**

- The WI's headline evidence (".antigravity/ holds only 5 files … no generated adapters") checked the **wrong directory**. The generator writes antigravity adapters to **`.agent/skills/`** (`ANTIGRAVITY_SKILLS_RELATIVE_PATH = Path(".agent") / "skills"`, `generate_antigravity_skill_adapters.py:39`), not `.antigravity/`. The authoritative signal is the **parity FAIL (22 STALE + 14 MISSING = the 36 declared)**, not the `.antigravity/` file count.
- Root cause is localized to **`build_adapters()`** (`:127`): it reads the registry and builds one `SkillAdapter` per `_skill_capabilities(registry)`, reading each capability's `canonical_source` (`:133`). `generate()` (`:269`) writes exactly what `build_adapters()` returns (`:271`, `:286`). So the produced adapter set diverges from the 36 the parity check expects — either `_skill_capabilities()` yields a subset, or a missing/unreadable `canonical_source` raises mid-loop and aborts generation (leaving 22 stale leftovers + 14 never-written).

This proposal fixes the generator so the produced antigravity adapter set reconciles with the registry-declared set and `check_harness_parity --harness antigravity` reaches **0 stale / 0 missing**.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4441 is the backlog authority for this fix (P2 cross-harness-tooling defect; blocks HYG-061 Area 2).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1` (includes WI-4441; allows `source` + `test_addition`).
- **GOV-HARNESS-ONBOARDING-CONTRACT-001**, **GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001** — harness skill-adapter parity (each capable harness exposes the canonical skill set) is a multi-harness-readiness surface; antigravity (harness C) parity reaching 0/0 is the contract this fix restores.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger). It is a cross-harness-tooling fix that does NOT modify `bridge/INDEX.md`, bridge workflow state, or any bridge file beyond this proposal's own thread; bridge authority and the canonical-INDEX invariant are preserved unchanged.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, with parity 0/0 as the gate.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — `target_paths` are in-root under `E:\GT-KB`; the regenerated adapters land in the in-root `.agent/skills/` tree.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked fix to a generated-artifact surface; the corrected premise and root-cause localization are recorded.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4441 + the parity FAIL), cycle-5 triage confirmed it open and localized the root cause, the bounded PAUTH authorizes the `source` + `test_addition` work, and harness-parity contracts (GOV-HARNESS-ONBOARDING-CONTRACT-001) define the 0/0 target. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ admitting WI-4441 (and 8 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-STANDALONE-DEFECT-BATCH-1`.
- **`bridge/gtkb-fab-16-harness-parity-remediation` (VERIFIED, WI-4428)** — harness-parity remediation during which WI-4441 surfaced; HYG-061 Area 2 was re-scoped out behind this defect. Cited as the originating context; this proposal completes the antigravity-parity gap FAB-16 deferred.
- **`scripts/generate_codex_skill_adapters.py`** — the sibling Codex adapter generator (shared hash contract per `_kb` parity); a working reference for "generate() emits the registry-declared adapter set," useful to the implementer for diffing why the antigravity generator diverges.
- _Live semantic deliberation search was not run during authoring (the `gt deliberations search` ChromaDB path's first-embed hang risk; per the session's standing caution I cited known threads/code instead)._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4441 to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-STANDALONE-DEFECT-BATCH-1` (allowed: `source`, `test_addition`; forbids formal-artifact mutation). This fix stays within that scope: it edits the generator (source) + adds a test, and (by running the fixed generator) regenerates `.agent/skills/` adapter files as tool output. No formal-artifact or KB mutation.

## Design

In `scripts/generate_antigravity_skill_adapters.py`:

1. **Diagnose the divergence in `build_adapters()` / `_skill_capabilities()`** (`:127`/`:131`): determine whether `_skill_capabilities(registry)` yields fewer than the 36 registry-declared antigravity capabilities, or whether a missing/unreadable `canonical_source` (`:133` `read_text()`) raises mid-loop and aborts generation. The sibling `generate_codex_skill_adapters.py` is the working reference contract.
2. **For each of the 14 MISSING**, the implementation determines per-adapter whether a valid `canonical_source` exists:
   - source exists → fix `build_adapters()`/`generate()` to emit the adapter (the common case if an abort or filter is dropping it);
   - source absent / registry over-declares → reconcile the registry-declared set down to the resolvable adapters (so the declaration and the generator agree).
3. **Make `build_adapters()` resilient**: a single missing/unreadable `canonical_source` must report a clear, actionable error (and skip that one) rather than aborting the whole generation — so one bad source can never zero out the other 35.
4. **Regenerate**: running the fixed `generate_antigravity_skill_adapters.py --update-registry` writes the reconciled adapter set to `.agent/skills/` + the `MANIFEST.json`, removing the 22 stale and creating the missing, so parity reaches 0/0. The regenerated `.agent/skills/` files are committed as tool output of the fix (not hand-authored; analogous to the committed `.codex/skills/` adapters).

No change to the shared source-hash contract, the Codex generator, or any other harness's adapters.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_generate_antigravity_skill_adapters.py`) | Method |
|---|---|---|
| `build_adapters()` yields the registry-declared antigravity adapter set (WI-4441 root cause) | `test_build_adapters_matches_registry_declared_set` | fixture registry with N capabilities (valid sources) → `build_adapters()` returns N `SkillAdapter`s with correct ids/paths |
| `generate()` emits an adapter file per declared adapter to `.agent/skills/` | `test_generate_emits_all_declared_adapters` | run `generate()` on the fixture → one rendered adapter file per capability under `.agent/skills/` + a MANIFEST |
| Resilience: one missing/unreadable `canonical_source` does not abort the rest | `test_missing_source_skips_one_not_all` | fixture with one bad `canonical_source` → the other adapters still generate; a clear error/skip is reported for the bad one |
| Parity gate reaches 0 stale / 0 missing (GOV-HARNESS-ONBOARDING-CONTRACT-001, WI-4441 acceptance) | `test_parity_zero_after_regen` | after regen on the fixture, the parity computation (`check_harness_parity` antigravity logic) reports 0 stale + 0 missing |
| No regression to the Codex generator / shared hash contract | `test_codex_generator_unaffected` (or run existing codex-adapter test) | the Codex adapter generator + shared `source_sha256` contract are unchanged |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on changed files; `python -m pytest platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q --tb=short`; plus an end-to-end `python scripts/check_harness_parity.py --harness antigravity` reporting 0 stale / 0 missing.

## Risk / Rollback

- **Risk: moderate-low.** The change is confined to the antigravity generator (`build_adapters`/`generate` reconciliation + resilience) and its test. It does NOT touch dispatch, the Codex generator, the shared source-hash contract, or any other harness. The regenerated `.agent/skills/` adapters are deterministic tool output verifiable by the parity gate.
- **Reconciliation-direction note:** if some of the 14 MISSING lack a valid `canonical_source`, the fix trims/corrects the registry declaration rather than fabricating sources — the acceptance (parity 0/0) holds either way, and the implementation records which adapters were generated vs which declarations were reconciled.
- **Rollback:** revert the generator edit + test + the regenerated `.agent/skills/` adapters. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (the antigravity adapter generator failing to produce the registry-declared set / aborting on a bad source), restoring an existing capability (harness parity); no new capability surface. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
