NEW

# Phase-1 Foundation: 4 spec inserts + canonical reader entrypoint module + doctor `_check_harness_state_sot_consistency`

bridge_kind: implementation_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-foundation
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Parent umbrella: bridge/gtkb-harness-state-sot-consolidation-phase-1-004.md (GO)
Parent grand-umbrella: bridge/gtkb-platform-sot-consolidation-umbrella-008.md (GO)
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4327

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 56a13045-e679-45e9-b6ee-064dd92483a3
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session, /loop dynamic-pacing iter 4

target_paths:
- groundtruth.db
- .groundtruth/formal-artifact-approvals/2026-06-05-GOV-HARNESS-STATE-SOT-CONSOLIDATION-001.json
- .groundtruth/formal-artifact-approvals/2026-06-05-DCL-HARNESS-STATE-SOT-READER-CONTRACT-001.json
- .groundtruth/formal-artifact-approvals/2026-06-05-DCL-HARNESS-STATE-SOT-ASSERTION-001.json
- .groundtruth/formal-artifact-approvals/2026-06-05-RETIRE-SPEC-harness-state-role-assignments.json
- groundtruth-kb/src/groundtruth_kb/harness_projection.py
- groundtruth-kb/src/groundtruth_kb/project/doctor.py
- groundtruth-kb/src/groundtruth_kb/cli.py
- groundtruth-kb/tests/test_harness_projection.py
- groundtruth-kb/tests/test_doctor_harness_state_sot.py
- platform_tests/scripts/test_check_harness_state_sot_consistency.py

requires_verification: true
implementation_scope: implementation

## Why this proposal

The umbrella `gtkb-harness-state-sot-consolidation-phase-1` GO at -004 authorizes Phase-1 work via 4 child bridges; this is the Foundation child (WI-4327 + WI-4328 + WI-4329). The other 3 children (rule-files, scripts-source, mirror-retirement) DEPEND on the Foundation: the canonical reader entrypoint exported here is what the 36+ referencer migrations target; the doctor check enforces consistency once the referencers are migrated; the retire-spec authorizes the eventual deletion.

Primary WI is WI-4327 (4 formal-artifact-approval packets); secondaries WI-4328 (canonical entrypoint extension) and WI-4329 (doctor check).

## Summary

**Governance (4 formal-artifact-approval packets):**

- **`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`** v1 (NEW) — designates 3 SoT surfaces (roles via `harness-state/harness-registry.json`; identities via `harness-state/harness-identities.json`; capabilities via `config/agent-control/harness-capability-registry.toml`); establishes canonical reader entrypoint contract; enumerates retired paths.
- **`DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`** v1 (NEW) — mechanical reader-entrypoint discipline; direct file reads outside `groundtruth_kb.harness_projection` in committed code are assertion-failing.
- **`DCL-HARNESS-STATE-SOT-ASSERTION-001`** v1 (NEW) — machine-checkable consistency assertions evaluated by `gt assert`; doctor roll-up.
- **Retire-spec** for `harness-state/role-assignments.json` v1 (NEW) — authorizes WI-4336 deletion AFTER all referencers have migrated. Pre-deletion, file exists as orphan compatibility surface.

Each draft body is in the umbrella `bridge/gtkb-harness-state-sot-consolidation-phase-1-001.md` §"Spec Drafts" (lines 124-220).

**Module + doctor + CLI (operational mutations):**

- Extend `groundtruth-kb/src/groundtruth_kb/harness_projection.py` with three canonical reader functions:
  - `read_roles() -> dict` — reads `harness-state/harness-registry.json`; raises on missing/malformed.
  - `read_identity() -> dict` — reads `harness-state/harness-identities.json`.
  - `read_capabilities() -> dict` — reads `config/agent-control/harness-capability-registry.toml`.
- Extend `groundtruth-kb/src/groundtruth_kb/project/doctor.py` with `_check_harness_state_sot_consistency`:
  - Layer 1: 3 SoT files parse cleanly via the canonical entrypoint.
  - Layer 2: grep_absent — no committed code outside `groundtruth_kb.harness_projection` reads `harness-state/*.json` or `harness-capability-registry.toml` directly.
  - Layer 3: grep_absent — no references to retired paths (`harness-state/role-assignments.json`, `harness-state/{claude,codex}/operating-role.md`) outside bridge files, audit archives, formal-artifact-approval packets, and `harness_projection.py` itself.
- Extend `groundtruth-kb/src/groundtruth_kb/cli.py` with `gt harness` subcommand wiring (commands: `roles`, `identity`, `capabilities`); each delegates to the canonical entrypoint and prints JSON.

**Tests:**

- `groundtruth-kb/tests/test_harness_projection.py` — unit tests for the 3 new functions: parse success on canonical fixtures; raises `HarnessStateError` on missing/malformed.
- `groundtruth-kb/tests/test_doctor_harness_state_sot.py` — unit tests for `_check_harness_state_sot_consistency`: 3-layer fixture coverage (clean = PASS; out-of-entrypoint read = FAIL; retired-path reference outside whitelist = FAIL).
- `platform_tests/scripts/test_check_harness_state_sot_consistency.py` — platform-tests check the doctor surface end-to-end against the live project.

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps each new spec to test coverage. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Parent authority of `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`; cited in spec draft. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | PAUTH `included_spec_ids` cites this; doctor + assertions preserve the SoT pattern this governs. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:GOV/DCL/retire-spec inserts | 4 formal-artifact-approval packets enumerated in target_paths; per-packet owner approval per `DCL-ARTIFACT-APPROVAL-HOOK-001`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | `PAUTH-...-PHASE-1-IMPLEMENTATION-ENVELOPE` (rowid 134 v2) cited; covers WI-4327 + WI-4328 + WI-4329 + WI-4214 (12 more WIs reserved for sibling child bridges). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites `DELIB-20260668` + `DELIB-20260880` (recent amendment AUQ adding WI-4214) as owner-decision authority. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs (GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-ARTIFACT-APPROVAL-001, GOV-HARNESS-ROLE-PORTABILITY-001) + the 4 Foundation specs being created. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4327 primary; WI-4328 + WI-4329 secondary; all in PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 3 new test files in target_paths; spec-to-test mapping in §Specification-Derived Verification Plan. |
| `GOV-09` (owner input classification) | blocking | content:owner directive | `DELIB-20260668` 8-AUQ + `DELIB-20260880` PAUTH-amendment AUQ already classified as specification-language. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/src/groundtruth_kb/project/**, content:E:\GT-KB | All paths within `E:\GT-KB`; module extension at `groundtruth-kb/src/groundtruth_kb/harness_projection.py`; doctor at `groundtruth-kb/src/groundtruth_kb/project/doctor.py`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`; no exceptions. |
| `GOV-08` (KB is truth) | blocking | foundational | Canonical entrypoint contract resolves harness state against the registered SoT files; doctor enforces parity. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 4 governance specs + concrete implementation plan + spec-derived verification. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation, MemBase | Foundation establishes the canonical-entrypoint pattern for harness-state SoT. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified, retired | 4 new specs land at `specified`; retire-spec sets `harness-state/role-assignments.json` lifecycle to `retired` (deletion authorized in WI-4336 final child). |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "canonical reader entrypoint", "harness-state SoT consolidation", "retired path inventory" — first-contact concepts; glossary updates land via WI-4338 (rule-files child). |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: `DELIB-20260668` (8-AUQ on harness-state SoT consolidation scope) + `DELIB-20260669` (drift evidence motivation) + `DELIB-20260880` (recent PAUTH-amendment AUQ adding WI-4214 to v2 scope). Per-spec formal-artifact-approval packets require per-packet owner approval at execution time per `GOV-ARTIFACT-APPROVAL-001`.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO (9-slice plan).
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md` — sibling VERIFIED (provides Slice 1 SoT registry pattern this Foundation parallels for harness-state subset).
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella thread; GO at -004; spec drafts inline in -001 §"Spec Drafts" lines 124-220.
- `DELIB-20260668` — 8-AUQ harness-state SoT consolidation scope authority.
- `DELIB-20260669` — drift evidence motivating consolidation.
- `DELIB-20260880` — PAUTH-amendment AUQ (v1 → v2, adds WI-4214).
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor that marked role-assignments.json "orphan" without deletion; this Phase-1 is the follow-through.
- `bridge/gtkb-managed-artifact-registry-008.md` — registry pattern precedent.

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

Owner-decision evidence authorizing this proposal:

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Phase-1 scope ratification | AskUserQuestion | DELIB-20260668 (8-AUQ) | Foundation as a Phase-1 child of the umbrella |
| Drift evidence motivation | Manual-triage + owner ratification | DELIB-20260669 | Mechanical reader-entrypoint discipline |
| PAUTH amendment (WI-4214 add) | AskUserQuestion | DELIB-20260880 | Mirror-retirement scope alignment (final child) |
| PAUTH coverage of WI-4327/4328/4329 | Original PAUTH mint | PAUTH rowid 122 v1 (carried forward to v2) | Foundation scope inclusion |

No NEW owner AUQ is required for THIS proposal. Per-spec formal-artifact-approval packets at execution time require per-packet owner approval as separate AUQ events per `GOV-ARTIFACT-APPROVAL-001`.

## Acceptance Criteria

1. **4 specs land in MemBase:** `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` v1, `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` v1, `DCL-HARNESS-STATE-SOT-ASSERTION-001` v1, retire-spec v1. All via formal-artifact-approval packets with owner approval.
2. **Canonical entrypoint implemented:** `groundtruth_kb.harness_projection` exports `read_roles`, `read_identity`, `read_capabilities`; each reads the canonical SoT file and raises `HarnessStateError` on missing/malformed.
3. **Doctor check implemented:** `_check_harness_state_sot_consistency` in `groundtruth_kb/project/doctor.py`; 3-layer assertion (parse + grep_absent direct-read + grep_absent retired-path); severity WARN initially.
4. **CLI wiring:** `gt harness roles`/`identity`/`capabilities` subcommands delegate to canonical entrypoint and print JSON output.
5. **Tests pass:** `pytest groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_doctor_harness_state_sot.py platform_tests/scripts/test_check_harness_state_sot_consistency.py` GREEN.
6. **Ruff clean:** `ruff check` + `ruff format --check` GREEN on all changed Python files.
7. **No project-root-boundary violation:** all target_paths within `E:\GT-KB`.
8. **Doctor surfaces grep findings as WARN, not FAIL:** initial deployment must be advisory until rule-files + scripts-source children land. Severity promotion to FAIL happens after WI-4336 (mirror retirement) lands.

## Phased Implementation Plan

**Phase 1 — Spec governance landing (4 formal-artifact-approval packets):**

1. Generate packets for the 4 specs from the drafts in `bridge/gtkb-harness-state-sot-consolidation-phase-1-001.md` §"Spec Drafts" (lines 124-220). Owner approval gate fires per packet.
2. Insert all 4 via `KnowledgeDB.insert_spec` per packet evidence.

**Phase 2 — Module extension:**

3. Extend `groundtruth-kb/src/groundtruth_kb/harness_projection.py` with `read_roles`, `read_identity`, `read_capabilities` functions and `HarnessStateError` exception class. Existing imports/exports preserved.

**Phase 3 — Doctor check:**

4. Add `_check_harness_state_sot_consistency` to `groundtruth-kb/src/groundtruth_kb/project/doctor.py`. Register in doctor pipeline. Severity WARN.

**Phase 4 — CLI wiring:**

5. Add `gt harness` group to `groundtruth-kb/src/groundtruth_kb/cli.py` with `roles`/`identity`/`capabilities` subcommands.

**Phase 5 — Tests:**

6. Write the 3 test files. Run pytest + ruff. Verify GREEN before filing post-impl report.

**Phase 6 — Implementation report:**

7. File `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-002.md` as NEW post-impl report with spec-to-test mapping + observed test results + applicability+clause preflights.

## Specification-Derived Verification Plan

| Spec (new) | Test file | Acceptance check |
|---|---|---|
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (designates 3 SoT surfaces + reader contract + retired paths) | `groundtruth-kb/tests/test_harness_projection.py` | The 3 canonical reader functions exist and parse the 3 SoT files; retired-path references trigger doctor finding |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` (mechanical reader-entrypoint discipline) | `groundtruth-kb/tests/test_doctor_harness_state_sot.py` (Layer 2) | Doctor flags `json.load.*harness-state/` outside `harness_projection.py` |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` (machine-checkable consistency assertions) | `groundtruth-kb/tests/test_doctor_harness_state_sot.py` (all layers) | `gt assert` evaluates the assertions field; doctor rolls them up |
| Retire-spec (role-assignments.json) | `platform_tests/scripts/test_check_harness_state_sot_consistency.py` | Doctor Layer 3 enumerates retired paths; reports `role-assignments.json` lifecycle as `retired` (pre-deletion) |

## Risk and Rollback

**Risk 1 — Reader entrypoint becomes a single point of failure.** Any consumer reading harness-state via `harness_projection.read_*` depends on the module loading cleanly. Mitigation: simple parse-and-return implementation; exceptions surface to caller with clear context; doctor catches malformed SoT files at WARN.

**Risk 2 — Doctor grep_absent overmatches.** The Layer-2 grep for `json.load.*harness-state/` could match comments or string literals in non-reading contexts. Mitigation: grep restricted to .py files; whitelist `groundtruth_kb.harness_projection` + bridge files + audit archives + formal-artifact-approval packets.

**Risk 3 — Initial doctor WARN floods.** Existing referencers in scripts/, src/, config/ will trigger Layer-2 findings until the rule-files + scripts-source children land. Mitigation: doctor severity WARN initially; severity promotion to FAIL deferred until WI-4336 (mirror-retirement child) lands.

**Rollback:** Per-phase reversibility:
- Phase 1: spec inserts are append-only versioned — withdraw via `withdrawn` status.
- Phases 2-4: file-level reversible via git.
- Phase 5: tests are file-level reversible.

If Codex NO-GO this proposal: no source mutations occur; rollback is trivial (this bridge file alone is reverted/superseded by REVISED-N).

## Pre-Filing Preflight Subsection

Both mandatory preflights to be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-foundation
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green (no blocking gaps).

---

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
