NEW

# Phase-1 Scripts-Source: migrate 5 remaining direct harness-state readers to canonical entrypoint + audit configs/Codex/packet-builders

bridge_kind: prime_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-scripts-source
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-8
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Parent umbrella: bridge/gtkb-harness-state-sot-consolidation-phase-1-004.md (GO)
Sibling (prereq, VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md
Parent grand-umbrella: bridge/gtkb-platform-sot-consolidation-umbrella-008.md (GO)
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4333

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 56a13045-e679-45e9-b6ee-064dd92483a3
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session, /loop dynamic-pacing

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "scripts/cross_harness_bridge_trigger.py", "scripts/verify_antigravity_dispatch.py", "groundtruth-kb/tests/test_harness_state_reader_migration.py", "platform_tests/scripts/test_scripts_source_entrypoint_migration.py", ".groundtruth/audit/scripts-source-codex-parity-audit-2026-06-05.md", ".groundtruth/audit/scripts-source-packet-builder-audit-2026-06-05.md"]

# KB-mutation note: groundtruth.db is in target_paths ONLY for work-item status resolution
# (WI-4333/4334/4335/4337/4339) at completion via KnowledgeDB.update_work_item. This child
# performs NO spec inserts/updates (Foundation already landed all harness-state SoT specs).

requires_verification: true
implementation_scope: implementation

## Why this proposal

The umbrella `gtkb-harness-state-sot-consolidation-phase-1` GO at -004 authorizes Phase-1 work via 4 child bridges. Foundation (Child 1) is VERIFIED at -012, exporting the canonical reader entrypoint `groundtruth_kb.harness_projection.{read_roles, read_identity, read_capabilities}` and the `_check_harness_state_sot_consistency` doctor at WARN. This is the Scripts-Source child (Child 3; WI-4333 + WI-4334 + WI-4335 + WI-4337 + WI-4339): migrate the remaining committed code that reads harness-state SoT files directly so all reads route through the canonical entrypoint, satisfying `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`.

## Scope Reconciliation (interrogative-default finding)

The umbrella -001 projected this child as "12 scripts + 4 source modules + 4 config files." A fresh evidence-based inventory of the live tree at HEAD `c153b30f` finds the ACTUAL remaining direct-reader surface is materially smaller, because intervening slices (the role-assignments mirror-retirement slices 1-3, the role-status-orthogonality dispatch work, and `harness_projection_reader.py` / `harness_roles.py` adoption) already migrated the majority of referencers. This proposal reflects the actual remaining work, not the stale projection.

**Evidence (grep against active Python at HEAD `c153b30f`):**

- Files reading live SoT files (`harness-registry.json` / `harness-identities.json`) DIRECTLY, outside the entrypoint: **5**.
- Files reading the RETIRED `harness-state/role-assignments.json` as a role data source: **0**. All remaining `role-assignments.json` mentions in active Python are (a) leftover path CONSTANTS no longer used as live read sources (`scripts/harness_roles.py:81` — already migrated per its own docstring lines 5/230/290; `scripts/check_codex_hook_parity.py:23`), (b) inventory/sandbox path enumerations (`scripts/collect_dev_environment_inventory.py:497`, `scripts/rehearse/_dashboard_regen.py:73,351`), or (c) narrative/docstring text in startup-disclosure builders and `_build_*packet*.py` scripts. None are role-data reads.

This finding is favorable for the eventual mirror-retirement child (Child 4): the `forbid: delete_active_referencer_without_migration` PAUTH constraint is substantially satisfied already; only this child's 5 entrypoint migrations + leftover-constant cleanup remain before the mirror is deletable.

## Migration Targets (WI-4333 scripts + WI-4334 source modules)

| File | SoT read site | Current pattern | Migration |
|------|---------------|-----------------|-----------|
| `groundtruth-kb/src/groundtruth_kb/session/envelope.py` | L96 (`harness-identities.json`), L112 (`harness-registry.json`) | `_read_json(project_root / "harness-state" / ...)` | Replace with `harness_projection.read_identity()` / `read_roles()`; preserve the `{}`-default-on-missing behavior by catching `HarnessStateError`. |
| `groundtruth-kb/src/groundtruth_kb/session/handoff.py` | L206/209 (`harness-identities.json`) | `json.loads(identities_path.read_text(...))` | Replace with `harness_projection.read_identity()`. |
| `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` | L78 (`harness-registry.json`) | `json.loads(registry_path.read_text(...))` | Replace with `harness_projection.read_roles()`; identities already removed here (L29 comment). |
| `scripts/cross_harness_bridge_trigger.py` | L978-980, L1003-1005 (`harness-registry.json`) | `json.loads(path.read_text(...))` in `_read_harness_roles()` / `_read_harness_identities()` | Route through `harness_projection.read_roles()` / `read_identity()`. Note: this runs as a PostToolUse/Stop hook; verify `groundtruth_kb` is importable in the hook runtime, else use the `scripts.harness_projection_reader` shim (already entrypoint-routed) rather than re-importing the package directly. |
| `scripts/verify_antigravity_dispatch.py` | L51/53 (`harness-registry.json`) | `json.loads(registry_path.read_text(...))` | Route through the entrypoint or `scripts.harness_projection_reader`. |

## Audit Deliverables (WI-4335 configs, WI-4337 Codex parity, WI-4339 packet-builders)

These three WIs were projected as migrations but the evidence shows they are AUDITS with no code changes required:

- **WI-4335 (configs):** `config/` references to `role-assignments.json` / harness-state paths are SoT DECLARATIONS (`config/registry/sot-artifacts.toml`), inventory-drift registries, and interface maps — not role-data reads. No config migration is required. The audit report documents each reference and confirms it is a declaration/enumeration, not a read.
- **WI-4337 (Codex parity):** `.codex/` contains only documentation/SKILL.md references and generated startup logs — no executable direct reads of harness-state. The audit report confirms Codex-side parity is already clean.
- **WI-4339 (packet-builders):** The 7 `scripts/_build_*packet*.py` scripts contain `role-assignments.json` mentions in docstrings/narrative STRING content (the packets they emit describe the role-assignment wire format) — not reads. These are intentional narrative content. The audit report confirms no migration required.

Audit reports land at `.groundtruth/audit/scripts-source-codex-parity-audit-2026-06-05.md` and `.groundtruth/audit/scripts-source-packet-builder-audit-2026-06-05.md` as durable evidence.

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps the reader contract to grep-absent + test coverage. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | blocking | content:harness-state reads, canonical entrypoint | The operative spec this child satisfies: all 5 direct readers migrate to the entrypoint. |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | blocking | content:machine-checkable assertions | Post-migration, the Layer-2 grep_absent assertion (no `json.load`/`read_text` of harness-state outside the entrypoint) holds for these files. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | blocking | content:3 SoT surfaces | Reads consolidated onto the entrypoint contract designated by this GOV. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Parent authority; reads route through the canonical reader so freshness is single-sourced. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | PAUTH `included_spec_ids`; migration preserves role-set semantics (read-path only, no value changes). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH rowid 134 v2 cited; covers WI-4333/4334/4335/4337/4339 (all in the 14-WI envelope). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites `DELIB-20260668` + `DELIB-20260880`. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs; this child cites them + the 3 Foundation specs it satisfies. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4333 primary; WI-4334/4335/4337/4339 bundled; all in PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 2 new test files in target_paths. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/src/**, content:E:\GT-KB | All paths within `E:\GT-KB`; source mutations under `groundtruth-kb/src/groundtruth_kb/` + `scripts/`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`; no exceptions. |
| `GOV-08` (KB is truth) | blocking | foundational | Entrypoint resolves harness state from the registered SoT; this child enforces single-read-path. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item, owner decision | Migration + audit reports as durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Foundation VERIFIED prerequisite cited; this child advances toward mirror-retirement readiness. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Migration + 3 durable audit-report artifacts; deliberation evidence cited in §Prior Deliberations. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "canonical reader entrypoint" already glossarized in rule-files child scope; this child consumes it. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: `DELIB-20260668` (8-AUQ harness-state SoT consolidation scope) + `DELIB-20260669` (drift evidence) + `DELIB-20260880` (PAUTH v2 amendment). The reader contract (`DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, VERIFIED via Foundation) is the operative requirement; no new requirement needed. The scope reconciliation is a factual narrowing of already-authorized work, not a new requirement.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO (9-slice plan).
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella; GO at -004; child mapping at §"Child Bridges Filed After Umbrella GO".
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md` — sibling VERIFIED; provides the entrypoint this child migrates to.
- `DELIB-20260668` — 8-AUQ harness-state SoT consolidation scope authority.
- `DELIB-20260669` — drift evidence.
- `DELIB-20260880` — PAUTH v2 amendment (adds WI-4214).
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor mirror-retirement slice (VERIFIED); part of why the referencer surface is already small.
- `.claude/rules/operating-model.md` §1 — interrogative-default mandate motivating the scope reconciliation.

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Phase-1 scope ratification | AskUserQuestion | DELIB-20260668 (8-AUQ) | Scripts-Source as a Phase-1 child |
| Reader-entrypoint discipline | AskUserQuestion | DELIB-20260669 + reader-contract spec | Migration target = canonical entrypoint |
| PAUTH v2 (covers WI-4333..4339) | AskUserQuestion | DELIB-20260880 | PAUTH coverage |

No NEW owner AUQ is required for THIS proposal. This child mutates only `source_file` / `test_file` / `config_file` class paths (all PAUTH-covered); it touches NO protected narrative files, so no formal-artifact-approval packets are required.

## Acceptance Criteria

1. **5 direct readers migrated:** `session/envelope.py`, `session/handoff.py`, `mcp_surface/roles.py`, `cross_harness_bridge_trigger.py`, `verify_antigravity_dispatch.py` all route harness-state reads through `groundtruth_kb.harness_projection` (or the entrypoint-routed `scripts.harness_projection_reader` shim where package import is unavailable in a hook runtime).
2. **Behavior preserved:** missing-file / malformed-file fallback behavior is preserved (callers that previously defaulted to `{}` on missing now catch `HarnessStateError` and default identically). No role-state VALUE changes (read-path only).
3. **3 audit reports filed:** configs, Codex parity, packet-builders each documented as no-migration-required with evidence.
4. **Doctor Layer-2 clears for these files:** `_check_harness_state_sot_consistency` Layer-2 grep_absent no longer flags the 5 migrated files.
5. **Tests pass:** new `test_harness_state_reader_migration.py` + `test_scripts_source_entrypoint_migration.py` GREEN; all existing session/envelope/handoff/roles/trigger tests remain GREEN.
6. **Ruff clean:** `ruff check` + `ruff format --check` GREEN on all changed Python files.
7. **No project-root-boundary violation.**

## Phased Implementation Plan

**Phase 1 — Source-module migrations (3 files):**
1. `session/envelope.py`: replace L96/L112 `_read_json(...)` with `harness_projection.read_identity()` / `read_roles()` wrapped to preserve `{}`-default.
2. `session/handoff.py`: replace L206/209 direct read with `read_identity()`.
3. `mcp_surface/roles.py`: replace L78 direct read with `read_roles()`.

**Phase 2 — Script migrations (2 files):**
4. `cross_harness_bridge_trigger.py`: route `_read_harness_roles()` / `_read_harness_identities()` through the entrypoint or the `scripts.harness_projection_reader` shim (verify hook-runtime importability first; the shim is already entrypoint-routed and import-safe).
5. `verify_antigravity_dispatch.py`: route L51/53 through the entrypoint/shim.

**Phase 3 — Audits (3 reports):**
6. Write the configs audit, Codex-parity audit, packet-builder audit reports under `.groundtruth/audit/`.

**Phase 4 — Tests:**
7. `test_harness_state_reader_migration.py` (unit; asserts the migrated modules import + use the entrypoint, and preserve missing-file fallback).
8. `test_scripts_source_entrypoint_migration.py` (platform; grep-absent assertion that the 5 files contain no direct `harness-state/` json/text read outside the entrypoint import).

**Phase 5 — Implementation report:**
9. File `-002.md` NEW post-impl report with spec-to-test mapping + executed results + applicability+clause preflights.

## Specification-Derived Verification Plan

| Spec | Test / check | Acceptance |
|---|---|---|
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | `test_scripts_source_entrypoint_migration.py` (grep-absent) | The 5 files contain no direct harness-state read outside the entrypoint import |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | `_check_harness_state_sot_consistency` Layer-2 | Doctor no longer flags the 5 migrated files |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (reader contract) | `test_harness_state_reader_migration.py` | Migrated modules call `read_roles`/`read_identity`; behavior preserved on missing/malformed |
| `GOV-HARNESS-ROLE-PORTABILITY-001` (no value change) | existing session/role tests | All pre-existing tests for the 5 files remain GREEN (read-path only) |

## Risk and Rollback

**Risk 1 — Hook-runtime import availability.** `cross_harness_bridge_trigger.py` runs as a PostToolUse/Stop hook; `groundtruth_kb` may not be importable in that runtime. Mitigation: route through `scripts.harness_projection_reader` (already entrypoint-routed, import-safe as a sibling script) rather than the package; implementation verifies importability before choosing the path.

**Risk 2 — Fallback-behavior drift.** Callers that defaulted to `{}` on a missing file must preserve that. Mitigation: wrap entrypoint calls in `try/except HarnessStateError` returning the same default; unit test asserts the missing-file path.

**Risk 3 — Scope under-count.** If Codex's independent grep finds additional direct readers I missed, that is a real omission. Mitigation: the verification grep is broad (`json.load`, `read_text`, `open(`, path constants for all 4 SoT files); Codex review is invited to surface any additional target as a NO-GO finding and I will fold it in.

**Rollback:** All mutations are `source_file`/`test_file` class, file-level reversible via git. No spec mutations, no protected narrative, no deletions. If Codex NO-GO: no source mutations occur (the impl happens post-GO); this bridge file alone is superseded by REVISED-N.

## Pre-Filing Preflight Subsection

Both mandatory preflights to be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-scripts-source
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-scripts-source
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green (no blocking gaps).

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
