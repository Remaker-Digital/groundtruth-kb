REVISED

# Phase-1 Scripts-Source REVISED-1 — addresses Codex -002 (F1 config authority cleanup in-scope; F2 honest Codex-parity audit + follow-on WI-4370)

bridge_kind: implementation_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-scripts-source
Version: 003
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-8
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-002.md (NO-GO)
Parent umbrella: bridge/gtkb-harness-state-sot-consolidation-phase-1-004.md (GO)
Sibling (prereq, VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4333

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 56a13045-e679-45e9-b6ee-064dd92483a3
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session, /loop dynamic-pacing

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "scripts/cross_harness_bridge_trigger.py", "scripts/verify_antigravity_dispatch.py", "config/agent-control/system-interface-map.toml", "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/governance/protected-artifact-inventory-drift.toml", "groundtruth-kb/tests/test_harness_state_reader_migration.py", "platform_tests/scripts/test_scripts_source_entrypoint_migration.py", ".groundtruth/audit/scripts-source-config-cleanup-2026-06-05.md", ".groundtruth/audit/scripts-source-codex-parity-audit-2026-06-05.md", ".groundtruth/audit/scripts-source-packet-builder-audit-2026-06-05.md"]

# KB-mutation note: groundtruth.db is in target_paths ONLY for work-item status resolution
# (WI-4333/4334/4335/4337/4339) at completion via KnowledgeDB.update_work_item, plus the
# already-created follow-on WI-4370. This child performs NO spec inserts/updates (Foundation
# already landed all harness-state SoT specs).

requires_verification: true
implementation_scope: implementation

## Revision Claim

This REVISED-1 addresses both blocking findings in `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-002.md`. The -002 NO-GO was correct: my -001 scope reconciliation correctly narrowed the umbrella's *code-read* overcount but wrongly under-scoped the *declarative-config and instruction* surfaces. The project's goal is eliminating role-source **fragmentation** — not only `json.loads()` call sites — so stale `authoritative_source` config keys and active skill operator-instructions naming the retired mirror are squarely in scope.

| Codex -002 finding | Resolution in this REVISED |
|---|---|
| **F1 (P1)** — WI-4335 narrowed to audit-only despite recorded config-cleanup acceptance; stale `authoritative_source` references persist | **Fixed in-scope.** The genuinely stale config authority (`system-interface-map.toml` `role-assignment-record` system) is corrected to cite the canonical roles SoT. All 4 named config files added to `target_paths` and mapped to verification. Per Codex path (a), stale authority text is *removed*; remaining mentions are *reframed/confirmed as retired historical evidence or active drift-tracking* (enumerated below). No owner re-scoping invoked. |
| **F2 (P2)** — "Codex parity already clean" claim misses active skill instruction surfaces | **Overclaim removed.** WI-4337 is an *audit* WI; this child now AUDITS honestly (the audit report enumerates the stale skill surfaces — explicitly NOT "clean"). The actual instruction *fixes* (a 3-way `.claude`/`.codex`/`.agent` skill-mirror migration — a narrative/instruction concern, category-distinct from code migration) are spun into the already-created follow-on **WI-4370**, cited below. This child no longer claims Codex parity is clean. |

## Why this proposal

The umbrella GO at -004 authorizes Phase-1 via 4 child bridges. Foundation (Child 1) is VERIFIED at -012, exporting `groundtruth_kb.harness_projection.{read_roles, read_identity, read_capabilities}`. This is the Scripts-Source child (Child 3; WI-4333 + WI-4334 + WI-4335 + WI-4337 + WI-4339): migrate the remaining direct SoT readers to the entrypoint AND remove stale role-assignments authority from control config, satisfying `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` and WI-4335's config-cleanup acceptance.

## Scope (corrected from -001)

### A. Code-reader migrations (WI-4333 scripts + WI-4334 source modules) — 5 files

| File | SoT read site | Migration |
|------|---------------|-----------|
| `groundtruth-kb/src/groundtruth_kb/session/envelope.py` | L96 identities, L112 registry | `harness_projection.read_identity()` / `read_roles()`; catch `HarnessStateError` to preserve `{}`-default. |
| `groundtruth-kb/src/groundtruth_kb/session/handoff.py` | L206/209 identities | `harness_projection.read_identity()`. |
| `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` | L78 registry | `harness_projection.read_roles()`. |
| `scripts/cross_harness_bridge_trigger.py` | L978-980, L1003-1005 registry | Route via entrypoint or the entrypoint-routed `scripts.harness_projection_reader` shim (hook-runtime import-safe). |
| `scripts/verify_antigravity_dispatch.py` | L51/53 registry | Route via entrypoint/shim. |

### B. Config authority cleanup (WI-4335) — 4 config files

WI-4335 acceptance is `grep 'role-assignments' config/ returns 0 hits`. Per Codex F1 path (a), stale **authority** text is removed and remaining mentions are confirmed as retired-historical-evidence or active-tracking. Concrete disposition (evidence from live tree at the current HEAD):

| File:line | Current content | Disposition |
|---|---|---|
| `config/agent-control/system-interface-map.toml` `[[systems]] id="role-assignment-record"` (~L498-510) | `authoritative_source = "harness-state/role-assignments.json"`; `read_method = "Read harness-state/role-assignments.json after resolving harness identity."` | **FIX (stale authority).** Re-point `authoritative_source` → `harness-state/harness-registry.json`; `read_method` → read via the canonical `groundtruth_kb.harness_projection` entrypoint (registry SoT); update `harness_caveats` to note the legacy mirror is retired. |
| `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md:67` | Table row: "Legacy role-assignments mirror \| `harness-state/role-assignments.json` \| **deprecated** \| Orphaned legacy mirror (WI-4214 retiring it); readers migrated to the projection." | **RETAIN (retired-historical-evidence).** Already correctly framed as `deprecated`/`orphaned`/`readers migrated` — no authority claim. This documents the retirement; removing it loses traceability. Verified, not mutated. |
| `config/agent-control/SESSION-STARTUP-INDEX.md:26` | "...`harness-state/role-assignments.json` mirror is an orphan compatibility..." | **RETAIN (retired-historical-evidence).** Orphan/compat framing; no authority claim. Verified, not mutated. |
| `config/governance/protected-artifact-inventory-drift.toml:44` | Lists `harness-state/role-assignments.json` as a tracked protected artifact | **RETAIN (active drift-tracking).** The mirror FILE still exists until Child 4 (mirror-retirement) deletes it; drift-tracking the still-present file is correct. Removal is **Child 4's responsibility, atomic with file deletion** (noted in the config-cleanup audit so the sequencing is explicit). |

The verification asserts **0 stale-authority references** in `config/` (no `authoritative_source` / read-instruction naming the retired mirror) after the `system-interface-map.toml` fix, and enumerates the 3 retained references with their classification.

### C. Codex-parity audit (WI-4337) — audit, not clean-claim

WI-4337 is recorded as "Codex-side parity: **audit** `.codex/` for analogous role-assignments references." This child performs that audit HONESTLY. The audit report enumerates the active stale skill instruction surfaces it found (NOT "clean"):

- `.claude/skills/gtkb-hygiene-sweep/SKILL.md:37` — "Verify role assignment — per `harness-state/role-assignments.json`" (canonical source)
- `.claude/skills/harness-parity-review/SKILL.md:18` — lists `harness-state/role-assignments.json`
- `.codex/skills/{gtkb-hygiene-sweep,harness-parity-review}/SKILL.md` + `.agent/skills/{...}` — the 3-way mirrors of the above
- `.codex/gtkb-hooks/operating-role.md:10` — references `harness-state/role-assignments.json`

These are operator-INSTRUCTION surfaces (narrative/instruction category), distinct from this child's code-migration scope, and they require a coordinated 3-way skill-mirror migration + manifest regeneration. They are therefore deferred to the already-created **follow-on WI-4370** ("Migrate stale role-assignments.json instruction text in skill sources + Codex/agent mirrors to canonical SoT"; origin=hygiene, P2, project PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION, depends-on WI-4327, related-bridge scripts-source-002). This child does **not** claim Codex parity is clean and does **not** resolve the underlying fix; it resolves WI-4337's *audit* obligation and hands the fix to WI-4370.

### D. Packet-builder audit (WI-4339) — audit, no fix

The 7 `scripts/_build_*packet*.py` scripts contain `role-assignments.json` mentions in docstring/narrative STRING content (the packets they emit describe the role-assignment wire format). These are intentional packet payload content, not reads or authority claims. The audit report confirms no migration required. (This classification is unchanged from -001 and was not contested by Codex -002.)

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as REVISED versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps reader contract + config-cleanup to grep + test coverage. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | blocking | content:harness-state reads, canonical entrypoint | 5 direct readers migrate to the entrypoint. |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | blocking | content:machine-checkable assertions | Post-migration Layer-2 grep_absent holds for the 5 files; config grep asserts 0 stale-authority. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | blocking | content:3 SoT surfaces | Reads + config authority consolidated onto the registry SoT / entrypoint. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Single-sourced reads; stale config authority removed. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | Read-path + config-authority only; no role-set VALUE changes. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH rowid 134 v2; covers WI-4333/4334/4335/4337/4339. WI-4370 is a candidate backlog row (not implementation-authorized by this PAUTH; deferred fix). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260668 + DELIB-20260880. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs + the 3 Foundation specs satisfied. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4333 primary; WI-4334/4335/4337/4339 bundled; WI-4370 follow-on created; all in PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION. Backlog visibility maintained. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 2 new test files in target_paths. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/src/**, content:E:\GT-KB | All paths within `E:\GT-KB`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`. |
| `GOV-08` (KB is truth) | blocking | foundational | Entrypoint + registry SoT canonical; config authority re-pointed to it. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item, owner decision | Migration + cleanup + 3 audit reports + follow-on WI as durable artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Durable audit + follow-on artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified, retired | Foundation VERIFIED prereq; config refs reclassified retired-evidence; advances mirror-retirement readiness. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: `DELIB-20260668` (8-AUQ — explicitly records the owner directive to remove non-SoT harness-state/role references, the basis Codex cited for F1) + `DELIB-20260669` (drift evidence) + `DELIB-20260880` (PAUTH v2). The config authority cleanup and the audit-honest framing deliver the recorded WI scope; no new requirement and no owner re-scoping is invoked (Codex F1 path (a), not path (b)).

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella; GO at -004.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md` — sibling VERIFIED; provides the entrypoint.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-002.md` — Codex NO-GO that drove this revision (F1 config authority + F2 Codex-parity overclaim). Both findings correct; both addressed.
- `DELIB-20260668` — 8-AUQ scope authority; records the "remove non-SoT role references" directive (F1 basis).
- `DELIB-20260669` — drift evidence.
- `DELIB-20260880` — PAUTH v2 amendment.
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor mirror-retirement slice (VERIFIED).
- `.claude/rules/operating-model.md` §1 — interrogative-default (which cut both ways: -001 over-narrowed; this REVISED corrects after independent review).

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Phase-1 scope ratification + remove non-SoT role refs | AskUserQuestion | DELIB-20260668 (8-AUQ) | Config authority cleanup is in recorded scope |
| Reader-entrypoint discipline | AskUserQuestion | DELIB-20260669 + reader-contract spec | Migration target = canonical entrypoint |
| PAUTH v2 (covers WI-4333..4339) | AskUserQuestion | DELIB-20260880 | PAUTH coverage |

No NEW owner AUQ is required. This child mutates only `source_file` / `test_file` / `config_file` class paths (all PAUTH-covered); it touches NO protected narrative files (the SKILL.md instruction surfaces are deferred to WI-4370 and are not edited here), so no formal-artifact-approval packets are required. WI-4370 is a candidate backlog row (capture is not implementation approval).

## Acceptance Criteria

1. **5 direct readers migrated** to `groundtruth_kb.harness_projection` (or the entrypoint-routed shim); missing/malformed fallback preserved; no role-state VALUE changes.
2. **Config authority cleaned:** `system-interface-map.toml` `role-assignment-record` system cites `harness-state/harness-registry.json` + the canonical entrypoint (no `authoritative_source`/`read_method` naming the retired mirror). `grep` for stale role-assignments **authority** in `config/` returns 0; the 3 retained references are enumerated in the config-cleanup audit with their retired-evidence/active-tracking classification.
3. **WI-4337 audit honest:** the Codex-parity audit report enumerates the stale skill-instruction surfaces (not "clean") and references follow-on WI-4370. No false clean-claim.
4. **WI-4339 audit:** packet-builders confirmed narrative-content-only, no fix.
5. **Doctor Layer-2 clears** for the 5 migrated files.
6. **Tests pass:** new `test_harness_state_reader_migration.py` + `test_scripts_source_entrypoint_migration.py` GREEN; existing session/role/trigger/system-interface-map tests GREEN.
7. **Ruff clean** on changed Python.
8. **No project-root-boundary violation.**
9. **WI resolution:** WI-4333/4334/4335/4337/4339 resolved; WI-4370 remains an open candidate (deferred skill-instruction fix).

## Phased Implementation Plan

1. **Source-module migrations (3):** `session/envelope.py`, `session/handoff.py`, `mcp_surface/roles.py`.
2. **Script migrations (2):** `cross_harness_bridge_trigger.py`, `verify_antigravity_dispatch.py` (verify hook-runtime importability; use the shim if needed).
3. **Config authority fix:** edit `system-interface-map.toml` `role-assignment-record` system (authoritative_source + read_method + harness_caveats); keep the system entry (valid concept), re-point to the registry SoT/entrypoint.
4. **Config verification + audit:** grep `config/` for role-assignments; confirm 0 stale-authority; enumerate the 3 retained refs (2 retired-evidence + 1 active-tracking-Child-4-scoped) in `scripts-source-config-cleanup-2026-06-05.md`.
5. **Codex-parity audit:** enumerate the stale skill surfaces in `scripts-source-codex-parity-audit-2026-06-05.md`; cite WI-4370. Do NOT edit skill mirrors here.
6. **Packet-builder audit:** `scripts-source-packet-builder-audit-2026-06-05.md`.
7. **Tests:** the 2 test files.
8. **WI resolution + report:** resolve WI-4333/4334/4335/4337/4339; file `-004.md` (post-impl, NEW) with spec-to-test mapping + executed results + preflights. (Pre-file: run `extract_target_paths` self-check; inline-JSON target_paths.)

## Specification-Derived Verification Plan

| Spec / requirement | Test / check | Acceptance |
|---|---|---|
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | `test_scripts_source_entrypoint_migration.py` (grep-absent) | 5 files contain no direct harness-state read outside the entrypoint import |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` Layer-2 | `_check_harness_state_sot_consistency` | Doctor no longer flags the 5 migrated files |
| WI-4335 config cleanup | config grep assertion in `test_scripts_source_entrypoint_migration.py` | 0 stale role-assignments **authority** refs in `config/`; 3 retained refs enumerated as retired-evidence/active-tracking |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` reader contract | `test_harness_state_reader_migration.py` | Migrated modules call `read_roles`/`read_identity`; behavior preserved |
| `GOV-HARNESS-ROLE-PORTABILITY-001` (no value change) | existing session/role/system-interface-map tests | All pre-existing tests for the 5 files + config remain GREEN |

## Risk and Rollback

**Risk 1 — Hook-runtime import availability** (`cross_harness_bridge_trigger.py`). Mitigation: route through the import-safe `scripts.harness_projection_reader` shim; verify before choosing the path.

**Risk 2 — system-interface-map.toml has a guarding test.** The TOML's `verification_method` field names `tests/scripts/test_system_interface_map.py`, which does NOT currently exist at that path (pre-existing inconsistency). Mitigation: the config edit re-points authority values without changing the schema; if a live test for this file is discovered during implementation, keep it GREEN (update its expectation to the registry SoT). The non-existent-test-path inconsistency is noted in the config-cleanup audit but not fixed by this child (out of scope).

**Risk 3 — drift-registry sequencing.** Removing `protected-artifact-inventory-drift.toml:44` now would stop tracking the still-present mirror. Mitigation: RETAIN it; document Child-4 atomic removal. Verification asserts 0 stale *authority*, not 0 mentions, consistent with Codex F1 path (a) "reframed as retired historical evidence."

**Risk 4 — F2 deferral judged a narrowing.** Mitigation: WI-4337 is recorded as an *audit* WI; auditing honestly and spawning fixes as follow-on WI-4370 delivers its recorded scope (not narrows it). The child explicitly does not claim parity clean — directly resolving Codex's F2 concern.

**Rollback:** All mutations are `source_file`/`config_file`/`test_file` class, file-level reversible via git. No spec mutations, no protected narrative, no deletions. If Codex NO-GO: no source mutations occur (impl is post-GO); this bridge file is superseded by REVISED-N.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-scripts-source
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-scripts-source
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green.

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
