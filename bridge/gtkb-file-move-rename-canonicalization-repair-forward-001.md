NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5640 Repair-Forward Recovery for the File Move/Rename Migration

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-repair-forward
Version: 001
Author: Codex Prime Builder (harness A)
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth.db", "scripts/gtkb_file_reference_migration.py", "config/file-reference-migration/wi5640.toml", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_implementation_start_gate.py", "scripts/generate_rule_compatibility_projections.py", "platform_tests/scripts/test_generate_rule_compatibility_projections.py", "scripts/generate_cursor_skill_adapters.py", "platform_tests/scripts/test_generate_cursor_skill_adapters.py", "scripts/generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "config/hooks/gtkb-*", "config/agent-control/gtkb-*", ".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-bridge/helpers/scan_bridge.py", ".claude/skills/gtkb-bridge/helpers/show_thread_bridge.py", ".codex/skills/gtkb-bridge/**", ".gtkb-state/file-reference-migration/wi5640/**"]

implementation_scope: source | test | configuration | runtime_state | governance_evidence | kb_projection
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Repair WI-5640 forward from local commit
`db07f9dcfe7e7de8addc850729209278472cb0fe` without rewriting or concealing
that commit. The commit remains incident evidence; its 90 existing
destinations and related repairs are candidate state, not authorized or
verified migration output. This fresh chain replaces neither the commit nor
the prior `gtkb-file-move-rename-canonicalization-v4` audit chain.

After WI-5441's canonical-registry completeness work, the implementation will
repair the bounded candidate defects, register every temporarily retained
migration source and every destination, synchronize the MemBase projection,
and use the deterministic migration engine to apply a closed reference-repair
plan over registered artifacts only. This is a programmatic scan/apply
operation, never an agent-driven recursive find/replace.

## Controlling Invariants

1. `config/registry/sot-artifacts.toml` is the human-edit registry authority;
   root `groundtruth.db` is its derived projection and is updated through
   `gt registry sync` and canonical `groundtruth_kb.project.sot_registry` APIs.
2. Before reference apply, all 90 retained sources and all 90 destinations must
   resolve exactly once through the canonical registry reader. Existing IDs
   are preserved; missing migration-scoped records receive stable path-derived
   IDs; duplicate storage paths fail closed.
3. WI-5441 owns global registry completeness and fail-closed mutation
   enforcement. WI-5640 re-baselines on it and may add only missing records
   among its exact 180-path compatibility set.
4. The scan inventory is the canonical registered-artifact set after registry
   sync, expanding registered file, directory, glob, and MemBase records.
   Unregistered files are disposable and are not repaired or used as evidence.
5. `bridge/` and canonical audit-history records are report-only exclusions:
   obsolete strings there are counted separately but never rewritten.
6. All 90 obsolete sources remain through repeated closure checks. No source
   deletion, scratch-index deletion, history rewrite, commit, push, release,
   or deployment is authorized.
7. Writes are limited to inline `target_paths`. A required write outside those
   paths stops apply and returns the exact path for independent review.
8. The eight tracked `.gtkb-index-*/index` files are unregistered disposable
   contamination and ignored by closure. Their deletion or untracking is
   deferred because the PAUTH forbids destructive cleanup and git mutation.

## Implementation Procedure

### Stage 0 - Re-baseline and authorization

- Confirm HEAD, worktree, PAUTH, fresh bridge GO, and matching WI-5640 claim.
- Re-baseline on completed WI-5441 registry work. If WI-5441 or the registry
  completeness gate is not green, stop without mutation.
- Require exactly 90 unique CSV pairs, 90 present sources, 90 present
  destinations, no no-op rows, and no duplicate mappings.

### Stage 1 - Repair candidate state

- Repair malformed TOML in
  `config/agent-control/gtkb-activity-envelope-sharding.toml`.
- Replace stale `.claude/skills/bridge` references in canonical `gtkb-bridge`
  skill/helper sources, regenerate Codex adapters, and verify parity.
- Correct implementation-start-gate fixtures lacking required bridge `Version`
  metadata without weakening production gate behavior.
- Repair migration-engine closure gaps only where deterministic preflight and
  tests demonstrate them.

### Stage 2 - Atomic migration registry admission

- In one registry transaction, upsert only missing records among the exact 90
  sources and 90 destinations, preserving IDs and rejecting duplicate paths.
- Run `gt registry sync`; compare `load_toml` and `load_projection`; require all
  180 paths to resolve once with matching fields.
- Do not remove, retire, or repoint a source record while its source remains in
  the compatibility set.

### Stage 3 - Deterministic plan and apply

- Regenerate the plan from the CSV and canonical registered-artifact inventory
  in a quiescent runtime context.
- Detect direct strings, slash-normalized variants, decoded JSON/TOML/YAML,
  Python literal concatenations, PowerShell command segments, and registered
  MemBase text. Classify and report binary content; never blindly replace it.
- Emit plan hash, inventory and closure fingerprints, exact write set,
  excluded-audit and unresolved-reference reports, and preimage hashes.
- Apply only the reviewed plan within `target_paths`, using structured writers
  for structured artifacts.
- Repeat closure from a fresh process and require zero actionable obsolete
  references and identical zero-result fingerprints.

### Stage 4 - Evidence and handoff

- File a `NO-ACTION` report with commands, counts, hashes, registry parity,
  changed paths, exclusions, and residuals for independent terminal review.
- Retain all old sources. No cleanup or commit is included.

## Cross-Harness Disposition

- Claude: `.claude/skills/gtkb-bridge/**` remains the canonical skill source;
  repaired references are verified directly in that source.
- Codex: `.codex/skills/gtkb-bridge/**` is regenerated from the canonical source
  and must pass adapter generator check mode and parity tests.
- Cursor: no Cursor behavioral surface is changed; the existing Cursor adapter
  generator and tests must remain green because migration tooling is shared.
- API, Antigravity, Ollama, OpenRouter, and Goose: no owned adapter path is
  changed by this proposal; deterministic scan reports any registered consumer
  reference but cannot write outside `target_paths`.
- Typed waiver: none requested. Applicable canonical/generated pairs must have
  behavioral parity before the implementation report is filed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5640; DELIB-20260724-WI5640-REPAIR-FORWARD; DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE; bridge/gtkb-file-move-rename-canonicalization-v4-008.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-PLATFORM-SOT-REGISTRY-001, DCL-SOT-REGISTRY-PROJECTION-PARITY-001, DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001, and GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "Fresh bridge NEW, independent Loyal Opposition GO, matching WI-5640 claim, implementation-start authorization, deterministic registry-scoped repair, NO-ACTION report, and independent terminal verdict.",
  "before_behavior": "Commit db07f9dc contains candidate migration output without a valid terminal authorization chain; the canonical registry contains 50 records and none of the 90 destinations; candidate defects and obsolete references remain open.",
  "after_behavior": "The preserved candidate commit is repaired through authorized forward changes; all 90 retained sources and 90 destinations are registered; deterministic registered-artifact closure reports zero actionable obsolete references while old sources remain available.",
  "self_descriptive_naming": "The fresh bridge slug, WI-5640 migration config, registry records, plan records, and evidence carry the file-move-rename repair-forward identity and stable path-derived names.",
  "obsolete_guidance_disposition": "Historical bridge and deliberation records remain unchanged and are report-only scan exclusions. Obsolete live references in registered non-audit artifacts are mechanically replaced; unregistered artifacts are disposable and ignored.",
  "history_preservation": "Commit db07f9dc, prior numbered bridge files, Deliberation Archive records, MemBase versions, and old source files are preserved; no history rewrite or deletion is permitted.",
  "baseline": {
    "head": "db07f9dcfe7e7de8addc850729209278472cb0fe",
    "migration_pairs": "90 sources and 90 destinations present and tracked",
    "registry": "50 TOML records, 50 projection records, zero destination admissions",
    "prior_bridge": "gtkb-file-move-rename-canonicalization-v4 latest NO-GO"
  },
  "expected_result": {
    "registry": "All exact 180 compatibility paths resolve once through canonical TOML and projection readers",
    "closure": "Two fresh-process scans return zero actionable obsolete references with identical fingerprints",
    "compatibility": "All 90 old sources and all 90 destinations remain present",
    "review": "A complete NO-ACTION report is ready for independent terminal review"
  },
  "rollback": {
    "instructions": "Use deterministic preimage hashes and the registry transaction to reverse only repair-forward writes before terminal verification; preserve commit and bridge history.",
    "verification": "Re-run registry parity, source and destination presence, focused tests, syntax checks, and two-process deterministic closure."
  },
  "hard_invariants": [
    "No source deletion, scratch-index deletion, history rewrite, commit, push, release, deployment, or credential mutation.",
    "No consumer write outside inline target_paths and no scan authority outside canonical registered artifacts.",
    "No manual recursive find/replace and no direct raw SQLite mutation.",
    "WI-5441 registry readiness is a precondition; WI-5640 seeds only its exact compatibility set.",
    "Status token and append-only bridge history remain intact."
  ],
  "fail_closed_conditions": [
    "Fresh GO, matching claim, active PAUTH, or implementation-start authorization is absent or stale.",
    "WI-5441 registry completion is not green or concurrent registry mutation is detected.",
    "CSV cardinality, uniqueness, path presence, registry uniqueness, or projection parity differs from the required baseline.",
    "Plan hashes, fingerprints, preimages, or exact write set cannot be reproduced.",
    "A required write falls outside target_paths or an actionable obsolete reference remains after apply.",
    "Any old source is missing before separately authorized deletion."
  ],
  "essential_context_preservation": "Preserve the CSV intent, prior v4 findings, repair-forward decision, registry-only authority, old-source retention, WI-5441 ownership, exact hashes and counts, and independent terminal review."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires a valid fresh NEW to independent
  GO chain and matching claim before protected repair work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the
  proposal and verification plan to identify operative requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds the work to
  WI-5640, its project, and active PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires terminal
  evidence derived from linked requirements and exact migration behavior.
- `GOV-STANDING-BACKLOG-001` - preserves WI-5640 as the accountable recovery
  unit despite its incorrect resolved projection.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the TOML registry authority for
  retained and canonical artifacts.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - requires MemBase projection parity.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - requires mechanical
  authorization and atomic registry treatment for moved and retained artifacts.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires preservation of GT-KB
  operation while old sources remain available.
- `ADR-CROSS-HARNESS-PARITY-001` - requires canonical/generated adapter parity.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires this proposal's explicit
  per-harness disposition and parity evidence.

## Prior Deliberations

- `DELIB-20260724-WI5640-REPAIR-FORWARD` - preserve `db07f9dc`, reject history
  rewrite, and recover through a fresh reviewed chain.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - retain old sources through
  repeated deterministic verification and govern deletion separately.
- `DELIB-202666274` - active project authorization and forbidden operations.
- `DELIB-202667191` - project authorization clarification for bounded work.
- `DELIB-202667182` - platform-modernization program authorization evidence.
- `bridge/gtkb-file-move-rename-canonicalization-v4-001.md` through
  `bridge/gtkb-file-move-rename-canonicalization-v4-008.md` - prior audit chain
  and terminal NO-GO; not current authorization.

## Owner Decisions / Input

The owner selected repair-forward in
`DELIB-20260724-WI5640-REPAIR-FORWARD`. No additional owner decision is
required to review this proposal. Destructive cleanup, history rewrite, commit,
push, release, and deployment remain outside scope.

## Requirement Sufficiency

Existing requirements are sufficient for this bounded recovery. Global
registry completeness remains WI-5441's prerequisite and is not absorbed into
WI-5640.

## Spec-Derived Verification Plan

1. Bridge authority: run the strict lifecycle resolver and
   `implementation_start_gate.py begin` for every planned write. Expected:
   `NEW -> GO`, active PAUTH, matching claim, and exact target authorization.
2. Registry: run `gt registry validate --json`, `gt registry sync`, and compare
   `load_toml` with `load_projection`. Expected: 180 compatibility paths each
   resolve once, fields match, and no duplicate storage path exists.
3. Migration: run focused migration and rule/Cursor/Codex generator tests.
   Expected: all structured-format, AST, PowerShell, MemBase, audit-exclusion,
   deterministic-hash, and fail-closed scope cases pass.
4. Governance: run
   `platform_tests/scripts/test_implementation_start_gate.py`. Expected: all
   tests pass and 41 missing-Version fixture failures disappear without
   weakening production checks.
5. Syntax/parity: parse changed TOML with `tomllib`; run adapter generators in
   check mode. Expected: parse success and zero generated drift.
6. Closure: run migration preflight twice in fresh processes. Expected: zero
   blockers before apply; after apply, zero actionable obsolete references,
   identical fingerprints, 90 retained sources, and 90 destinations.
7. Quality: run Ruff check and format-check over changed Python target paths.
   Expected: both pass.

## Risk / Rollback

Risks are making candidate state look authorized, missing encoded references,
colliding with WI-5441, or breaking compatibility by removing old sources.
Controls are clean re-baseline, WI-5441 completion, canonical-reader inventory,
stable preimages, exact authorization, two-process closure, and source
retention. Recovery uses deterministic preimages and a registry transaction;
no history rewrite is permitted. No commit is requested or authorized.

## Bridge Filing

This proposal starts fresh append-only chain
`gtkb-file-move-rename-canonicalization-repair-forward` at version 001. It does
not revise, delete, or treat the prior v4 chain as authorization.

## Recommended Commit Type

`fix` if a later owner-authorized commit records an independently VERIFIED
recovery. This proposal does not authorize a commit.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
