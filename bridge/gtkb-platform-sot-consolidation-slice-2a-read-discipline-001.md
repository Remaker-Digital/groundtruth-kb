NEW

# Slice 2A: Read-Discipline — extend FRESHNESS + RECORD-SCHEMA, new DCL-SOT-READ-HOOK-CONTRACT-001, PreToolUse Read hook, new rule, doctor `_check_sot_read_discipline`

bridge_kind: implementation_proposal
Document: gtkb-platform-sot-consolidation-slice-2a-read-discipline
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Parent umbrella: bridge/gtkb-platform-sot-consolidation-umbrella-008.md (GO)
Sibling: bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md (VERIFIED)
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE
Work Item: WI-4340
Secondary Work Item: WI-4343

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 56a13045-e679-45e9-b6ee-064dd92483a3
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session, /loop dynamic-pacing iter 2

target_paths:
- groundtruth.db
- .groundtruth/formal-artifact-approvals/2026-06-05-GOV-SOURCE-OF-TRUTH-FRESHNESS-001-v2.json
- .groundtruth/formal-artifact-approvals/2026-06-05-DCL-SOT-REGISTRY-RECORD-SCHEMA-001-v2.json
- .groundtruth/formal-artifact-approvals/2026-06-05-DCL-SOT-READ-HOOK-CONTRACT-001.json
- .groundtruth/formal-artifact-approvals/2026-06-05-RULE-sot-read-discipline.json
- .claude/rules/sot-read-discipline.md
- .claude/hooks/sot-read-discipline.py
- .claude/settings.json
- .codex/hooks.json
- .codex/gtkb-hooks/sot-read-discipline.py
- config/registry/sot-artifacts.toml
- groundtruth-kb/src/groundtruth_kb/project/sot_registry.py
- groundtruth-kb/src/groundtruth_kb/project/doctor.py
- groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py
- platform_tests/scripts/test_sot_read_discipline_hook.py
- platform_tests/scripts/test_check_sot_read_discipline.py

requires_verification: true
implementation_scope: implementation

## Why this proposal

The umbrella `gtkb-platform-sot-consolidation-umbrella` GO at -008 authorizes the 9-slice sequence and absorbed the withdrawn `PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE`'s 16-AUQ scope (`DELIB-20260672`) as Slice 2A. This is the Read-Discipline child bridge — the mechanical anti-substitution discipline that makes the SoT registry from Slice 1 actually defend the canonical paths against agent-side aliasing.

Slice 1 (`bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md` VERIFIED) inserted `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` and built the `gt registry` CLI + MemBase `sot_artifacts` table + doctor `_check_sot_registry_completeness` at WARN. Slice 2A extends the SCHEMA with a `forbidden_substitutes` metadata column, adds a Read-tool PreToolUse hook that blocks reads against any registered forbidden_substitute path with guidance toward the canonical SoT, adds a `.claude/rules/sot-read-discipline.md` rule file giving the discipline narrative authority, and adds a doctor check that asserts the hook is wired into both `.claude/settings.json` and `.codex/hooks.json`.

Primary tracking WI is WI-4340 (insert read-discipline specs); secondary is WI-4343 (doctor `_check_sot_read_discipline`).

## Summary

Three governance mutations + four operational mutations + two tests:

**Governance (3 formal-artifact-approval packets required at execution time):**

- **`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v1 → v2** — extends with read-discipline clauses: (a) every SoT path in the registry MUST be reachable through its canonical reader/CLI; (b) agent-side reads MUST NOT substitute a non-canonical alias when the canonical path is registered; (c) the registry's `forbidden_substitutes` column is the mechanical floor.
- **`DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v1 → v2** — adds optional `forbidden_substitutes: list[str]` column to the per-record schema. Empty/missing = no aliasing restrictions. Non-empty = listed paths trigger the Read hook.
- **`DCL-SOT-READ-HOOK-CONTRACT-001` v1 (NEW)** — defines the PreToolUse hook contract: hook intercepts Read/Grep/Glob tool calls, consults the registry's `forbidden_substitutes` list, blocks the call if the target matches a forbidden substitute, returns a structured error citing the canonical path.

**Operational (one PreToolUse hook + one rule + one doctor extension + one config seed):**

- **`.claude/hooks/sot-read-discipline.py`** (new) — Python hook that reads the registry projection from MemBase, normalizes the tool-call target path, and blocks-with-guidance when the target matches any registered `forbidden_substitutes` entry. Codex parity copy at `.codex/gtkb-hooks/sot-read-discipline.py`.
- **`.claude/rules/sot-read-discipline.md`** (new protected narrative) — discipline rule citing `DCL-SOT-READ-HOOK-CONTRACT-001`, listing the runtime behavior, the bypass path (explicit owner authorization), and the historical motivation (the agent-side fragmentation evidence in `DELIB-20260673`).
- **`groundtruth_kb.project.doctor._check_sot_read_discipline`** (new) — 3-layer doctor check: (1) hook file exists at both Claude + Codex paths; (2) `.claude/settings.json` + `.codex/hooks.json` register the hook in PreToolUse for Read/Grep/Glob; (3) the live registry projection's `forbidden_substitutes` entries all reference real registered records.
- **`config/registry/sot-artifacts.toml`** — populate `forbidden_substitutes` on the existing entries identified by `DELIB-20260670` (manual-triage survey of 8 forbidden-substitute candidates). Initial population is conservative; downstream slices may extend.

**Tests:**

- `platform_tests/scripts/test_sot_read_discipline_hook.py` — exercises the hook against synthetic registry payloads (3 fixtures: empty list = pass, matching forbidden = block, unmatched target = pass).
- `platform_tests/scripts/test_check_sot_read_discipline.py` — exercises the doctor check against 3 fixture project states (clean = PASS; missing hook file = WARN; settings.json missing registration = WARN).
- `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` — unit test for loader handling of the new column (presence, absence, type validation).

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps each new/extended spec to test coverage. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth, cited paths | Being EXTENDED to v2; new read-discipline clauses derive from existing clauses + `DELIB-20260672` Q3/Q11. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | blocking | parent of `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` extension | Slice 1 v1 cited; Slice 2A extension extends the registry schema row. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | blocking | content:registry record schema | v1 (Slice 1) cited; v2 extension adds `forbidden_substitutes`. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | blocking | content:projection parity | v1 cited; the schema extension MUST projection-round-trip; verification ensures parity. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:GOV/DCL inserts | 3 formal-artifact-approval packets enumerated in target_paths; per-packet owner approval per `DCL-ARTIFACT-APPROVAL-HOOK-001`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | `PAUTH-...-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE` (rowid 133 v1) cited; covers WI-4340 + WI-4343. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260672 + recent PAUTH-mint AUQ as owner-decision authority. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs + Slice 2A's 3 governance specs. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4340 primary; WI-4343 secondary; both in PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 3 new test files in target_paths; spec-to-test mapping in §Specification-Derived Verification Plan. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/**, path:.claude/**, path:config/** | All paths within `E:\GT-KB`; no out-of-root targets. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`; no exceptions. |
| `GOV-08` (KB is truth) | blocking | foundational | Hook reads registry via MemBase projection; TOML is edit-surface, projection is canonical. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 3 governance specs + concrete implementation plan + spec-derived verification. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Slice 2A extends Slice 1's artifact-registry with mechanical anti-substitution. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Slice 1's specs at `verified` (per bridge `gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md`); Slice 2A extensions create v2 rows. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "Read-discipline", "forbidden_substitutes column", "SoT read hook" — first-contact concepts; glossary updates included. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: `DELIB-20260671` (umbrella 7-AUQ) + `DELIB-20260672` (peer's 16-AUQ adopted via S408 reconciliation; specifically establishes Slice 2A scope) + `DELIB-20260670` (manual-triage survey identifying 8 forbidden-substitute candidates) + `DELIB-20260869` (work-item text alignment) + the recent owner AUQ that minted `PAUTH-...-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE` (rowid 133 v1). Per-spec formal-artifact-approval packets require additional per-packet owner approval at execution time per `GOV-ARTIFACT-APPROVAL-001`.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-001..008` — umbrella thread; GO at -008.
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md` — sibling, VERIFIED. Provides the base schema Slice 2A extends.
- `bridge/gtkb-agent-sot-read-discipline-phase-1-002.md` (WITHDRAWN) — predecessor; scope absorbed into Slice 2A.
- `DELIB-20260671` — umbrella 7-AUQ.
- `DELIB-20260672` — Slice 2A authority (peer's 16-AUQ).
- `DELIB-20260670` — 8 forbidden-substitute candidates from manual triage.
- `DELIB-20260673` — parallel-session fragmentation evidence motivating mechanical anti-substitution.
- `DELIB-20260869` — work-item text alignment AUQ (WI-4340 + WI-4343 v2).
- `DELIB-20260868` — work-item disposition AUQ (subsumed WIs).
- (PAUTH-mint AUQ for `PAUTH-...-SLICE-2A-...-IMPLEMENTATION-ENVELOPE` — captured as part of `gt projects authorize` execution; DELIB id to be cited in §Owner Decisions / Input once landed in DA.)
- `memory/research_sot_consolidation_2026_06_04.md` — research file informing the 22 SoT classes.
- `bridge/gtkb-managed-artifact-registry-008.md` — registry pattern precedent.

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

Owner-decision evidence authorizing this proposal:

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Umbrella scope ratification | AskUserQuestion | DELIB-20260671 (7-AUQ) | Slice 2A as a child of the umbrella |
| Read-discipline scope adoption | AskUserQuestion | DELIB-20260672 (16-AUQ adopted via S408) | Slice 2A subject area |
| 8 forbidden-substitute candidates | Manual-triage + owner ratification | DELIB-20260670 | Initial `forbidden_substitutes` population in registry TOML |
| Schema authority alignment | AskUserQuestion | DELIB-20260869 | WI-4340 + WI-4343 v2 text |
| Slice 2A PAUTH mint | AskUserQuestion | `gt projects authorize` execution (recent) | PAUTH coverage of WI-4340 + WI-4343 |

No NEW owner AUQ is required for THIS proposal. Per-spec formal-artifact-approval packets at execution time will require per-packet owner approval as separate AUQ events per `GOV-ARTIFACT-APPROVAL-001`.

## Acceptance Criteria

1. **Spec extensions land:** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 in MemBase with read-discipline clauses; `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 with `forbidden_substitutes` column; `DCL-SOT-READ-HOOK-CONTRACT-001` v1 inserted. All via formal-artifact-approval packets with owner approval.
2. **Registry seeded:** `config/registry/sot-artifacts.toml` updated to populate `forbidden_substitutes` on the entries identified in `DELIB-20260670` (8 candidates). The MemBase projection regeneration (via `gt registry sync` from Slice 1) reflects the new column.
3. **Hook implemented:** `.claude/hooks/sot-read-discipline.py` + Codex parity copy at `.codex/gtkb-hooks/sot-read-discipline.py`. Hook reads MemBase projection (NOT TOML — projection is canonical per `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`).
4. **Hook registered:** `.claude/settings.json` PreToolUse for Read/Grep/Glob references the hook; same in `.codex/hooks.json`.
5. **Rule file landed:** `.claude/rules/sot-read-discipline.md` (protected narrative; via formal-artifact-approval packet).
6. **Doctor check landed:** `_check_sot_read_discipline` in `groundtruth_kb/project/doctor.py`; 3-layer assertion; severity WARN initially.
7. **Tests pass:** `pytest platform_tests/scripts/test_sot_read_discipline_hook.py platform_tests/scripts/test_check_sot_read_discipline.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` GREEN.
8. **Ruff clean:** `ruff check` + `ruff format --check` GREEN on all changed Python files.
9. **No project-root-boundary violation:** all target_paths within `E:\GT-KB`.

## Phased Implementation Plan

**Phase 1 — Spec governance landing (3 formal-artifact-approval packets):**

1. Generate packet for `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 — content extension with the 3 read-discipline clauses. Owner approval gate fires.
2. Generate packet for `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 — content extension with `forbidden_substitutes: list[str]` optional column + validation rule. Owner approval gate fires.
3. Generate packet for `DCL-SOT-READ-HOOK-CONTRACT-001` v1 — new DCL defining the hook contract. Owner approval gate fires.
4. Insert all 3 via `KnowledgeDB.update_spec` / `KnowledgeDB.insert_spec` per packet evidence.

**Phase 2 — Registry seed:**

5. Update `config/registry/sot-artifacts.toml` to populate `forbidden_substitutes` on the 8 candidate entries from `DELIB-20260670`. Use `gt registry sync` (Slice 1 CLI) to regenerate the MemBase projection.

**Phase 3 — Loader extension + hook:**

6. Extend `groundtruth_kb/project/sot_registry.py` `SoTArtifact` dataclass with `forbidden_substitutes: list[str] = field(default_factory=list)`; update validation + projection helpers.
7. Author `.claude/hooks/sot-read-discipline.py` (Python; reads MemBase via `groundtruth_kb.project.sot_registry.load_projection`). On Read/Grep/Glob PreToolUse, normalize the target path; if it matches any registered `forbidden_substitutes` entry, return `{"decision": "block", "reason": "..."}` with guidance citing the canonical path.
8. Mirror at `.codex/gtkb-hooks/sot-read-discipline.py` (Codex parity per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`).
9. Register in `.claude/settings.json` PreToolUse(Read|Grep|Glob) array + `.codex/hooks.json` parity.

**Phase 4 — Rule file (protected narrative; formal-artifact-approval packet):**

10. Generate packet for `RULE-sot-read-discipline` — content of `.claude/rules/sot-read-discipline.md`. Owner approval gate fires.
11. Write `.claude/rules/sot-read-discipline.md`. Cite `DCL-SOT-READ-HOOK-CONTRACT-001`, summarize hook runtime, document the explicit-owner-authorization bypass, motivate with `DELIB-20260673`.

**Phase 5 — Doctor check:**

12. Add `_check_sot_read_discipline` to `groundtruth_kb/project/doctor.py`. Implement the 3-layer check (hook file presence at both Claude + Codex paths; settings registration; registry `forbidden_substitutes` entry validation). Severity WARN.

**Phase 6 — Tests:**

13. Write the 3 test files. Run pytest + ruff. Verify GREEN before filing post-impl report.

**Phase 7 — Implementation report:**

14. File `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-002.md` as NEW post-impl report with spec-to-test mapping + observed test results + applicability+clause preflights.

## Specification-Derived Verification Plan

| Spec (extended/new) | Test file | Acceptance check |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 (read-discipline clauses) | `platform_tests/scripts/test_sot_read_discipline_hook.py` | Hook BLOCKS a Read against any registered forbidden_substitute path; returns canonical-path guidance |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 (forbidden_substitutes column) | `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` | Loader accepts entries with the column populated; accepts entries without it; rejects entries where the column is not a list-of-strings |
| `DCL-SOT-READ-HOOK-CONTRACT-001` v1 (hook contract) | `platform_tests/scripts/test_sot_read_discipline_hook.py` | Hook honors contract: (a) returns `{"decision": "block", ...}` on forbidden match; (b) returns `{"decision": "allow"}` (or absent decision) on non-forbidden; (c) error message cites canonical path |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` (parity preserved across v2 schema) | `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` (parity assertion) | TOML round-trips through `gt registry sync` without drift; projection matches TOML on `forbidden_substitutes` |
| Doctor `_check_sot_read_discipline` | `platform_tests/scripts/test_check_sot_read_discipline.py` | 3-layer assertion: hook file at both paths; settings registration; registry forbidden_substitutes referential integrity |

## Risk and Rollback

**Risk 1 — Hook over-blocks legitimate reads.** The PreToolUse hook intercepts ALL Read/Grep/Glob tool calls. Mitigation: initial `forbidden_substitutes` population is conservative (8 paths from `DELIB-20260670`); hook short-circuits on empty registry projection; tests cover edge cases (path normalization, glob expansion semantics).

**Risk 2 — Hook performance regression.** Reading MemBase projection on every Read tool call could slow agent sessions. Mitigation: projection is small (22 SoT classes); loader uses module-level cache invalidated on registry update.

**Risk 3 — Schema migration breaks Slice 1 loader.** Adding `forbidden_substitutes` to the schema could break readers that don't expect the column. Mitigation: column is OPTIONAL with default empty list; existing TOML entries without the column continue to load unchanged; explicit unit test asserts back-compat.

**Rollback:** Per-phase reversibility:
- Phases 1, 4: spec mutations are append-only versioned — withdraw via `withdrawn` status.
- Phase 2: registry TOML edits are file-level reversible via git.
- Phase 3: hook addition + registration are file-level reversible.
- Phase 5: doctor check addition is file-level reversible.
- Phase 6: tests are file-level reversible.

If Codex NO-GO this proposal: no source mutations occur; rollback is trivial (this bridge file alone is reverted/superseded by REVISED-N).

## Pre-Filing Preflight Subsection

Both mandatory preflights to be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green (no blocking gaps).

This proposal cites every spec triggered by its paths and content per `config/governance/spec-applicability.toml`. Slice 2A adds no new bridge protocol clauses; reuses the Slice 1 enforcement footprint.

---

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
