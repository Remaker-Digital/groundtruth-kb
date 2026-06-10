REVISED

# Phase-1 Mirror-Retirement REVISED-1 — verification narrowed to RETIRE-SPEC assertions (file-absent + no-live-reads); doctor-clean deferred to WI-4372

bridge_kind: prime_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
Version: 003
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-8
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-002.md (NO-GO)
Parent umbrella: bridge/gtkb-harness-state-sot-consolidation-phase-1-004.md (GO)
Prereq (VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md
Prereq (VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-010.md
Prereq (VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-010.md
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4336

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 56a13045-e679-45e9-b6ee-064dd92483a3
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session, /loop dynamic-pacing

target_paths: ["harness-state/role-assignments.json", "config/governance/protected-artifact-inventory-drift.toml", "scripts/collect_dev_environment_inventory.py", ".groundtruth/inventory/dev-environment-inventory.json", "platform_tests/scripts/test_mirror_retirement_role_assignments.py"]

# KB-mutation note: groundtruth.db intentionally NOT in target_paths (WI-lifecycle
# resolution deferred to project-completion reconciliation per rule-files -002 F1).
# Deletion + supporting cleanup only.

requires_verification: true
implementation_scope: implementation

## Revision Claim

This REVISED-1 addresses both findings in `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-002.md`. The -002 NO-GO was correct: -001's acceptance criterion required `_check_harness_state_sot_consistency` doctor to be CLEAN, which is not achievable within the declared scope and conflates the over-broad WARN-level doctor with the RETIRE-SPEC's actual assertion.

| Codex -002 finding | Resolution in this REVISED |
|---|---|
| **F1 (P1)** — proposed verification ("doctor clean") cannot pass within scope; doctor reports ~61 findings (L2 direct-reads + L3 retired-path token mentions) across ~10+ files outside the 5 target_paths | **Acceptance narrowed (Codex path c).** "doctor `_check_harness_state_sot_consistency` clean" is REMOVED as an acceptance criterion. The spec-derived verification is now the RETIRE-SPEC's actual assertions, provable within scope: **(a)** `harness-state/role-assignments.json` absent; **(b)** grep_absent for **live code READS** (`json.load`/`open`/`read_text`/`tomllib` of the path) in `scripts/` + `groundtruth-kb/src/`, outside whitelisted contexts. The broad doctor predicate (which flags legitimate retired-historical-evidence — deprecation records, glossary provenance, the predicate's own token string, the sot-read-discipline rule's motivation — plus remaining genuine L2 direct-readers) is WARN-only and out of this child's scope; its refinement is deferred to **WI-4372** (created this session). This child explicitly does NOT claim doctor-clean. |
| **F2 (P2)** — DCL-HARNESS-STATE-SOT-ASSERTION-001 mapped to `gt assert`, but the DCL has no registered assertion definition | **Corrected.** Verified the DCL's `assertions` field is empty; `gt assert` has nothing to run for it. The mapping now cites the explicit deletion test as the spec-derived check that proves both the RETIRE-SPEC assertions and the intent of DCL-HARNESS-STATE-SOT-ASSERTION-001. No `gt assert` claim. |

## Doctor Scope Clarification (F1)

The doctor `_check_harness_state_sot_consistency` (doctor.py:492-522) is WARN severity (non-blocking; shipped at WARN in Foundation). Its L3 predicate flags ANY textual mention of `harness-state/role-assignments.json` (whitelisting only `harness_projection.py` + `harness_projection_reader.py`), so it currently reports legitimate **retained retired-historical-evidence** as findings:
- `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` / `SESSION-STARTUP-INDEX.md` — deprecation records (kept by design per scripts-source disposition).
- `.claude/rules/canonical-terminology.md` — glossary provenance (kept per rule-files disposition).
- `.claude/rules/sot-read-discipline.md` — historical-motivation evidence (DELIB-20260673).
- `config/registry/sot-artifacts.toml` — SoT registry record.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — the predicate's OWN token literal.
- Plus remaining L2 "direct SoT read" findings (`check_codex_hook_parity.py`, `mode_switch/*.py`, `session_self_initialization.py`, `session_start_dispatch_core.py`) that read live SoT files beyond scripts-source's migrated 5.

Making the doctor fully clean requires (i) a predicate refinement to distinguish live reads from retired-historical-evidence, and (ii) migrating the remaining genuine L2 direct-readers — both captured in **WI-4372** (origin=hygiene, P2, project PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION, depends-on WI-4336). That work is intentionally NOT in this deletion child: it touches protected narrative + many out-of-scope source files and is a distinct concern from the file deletion.

## Why this proposal

This is the final child (Child 4) of harness-state SoT consolidation Phase-1: delete the orphaned legacy mirror `harness-state/role-assignments.json`. All three prerequisites are VERIFIED (foundation -012, scripts-source -010, rule-files -010). The RETIRE-SPEC's hard precondition — `forbid: delete_active_referencer_without_migration` — is satisfied: a fresh grep of active Python finds ZERO live reads (`json.load`/`read_text`/`open`/`tomllib`) of the retired path.

## Authorization

- **RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001** (specified v1): authorizes deletion under WI-4336 after migration. Assertions: (a) file-absent post-deletion; (b) grep_absent — no live code references outside whitelisted bridge/audit/packet contexts. Successor: reads flow through `groundtruth_kb.harness_projection` (`harness-state/harness-registry.json`).
- **Owner AUQ** captured ("Phase-1 batch AUQ 4 of 4"; recorded in the RETIRE-SPEC) + re-affirmed via the rule-files implementation approval.
- **PAUTH rowid 134 v2**: `file_deletion`+`config_file`+`source_file`+`test_file` covered; WI-4336+WI-4214 included.

## Scope — deletion + 3 coupled surfaces (unchanged from -001)

| # | Path | Action |
|---|------|--------|
| 1 | `harness-state/role-assignments.json` | **DELETE** (legacy mirror; 1315 bytes). |
| 2 | `config/governance/protected-artifact-inventory-drift.toml` | **EDIT** — remove the `"harness-state/role-assignments.json",` pattern (L44) from `[[protected_artifacts]] id="harness-identity-and-role-state"`, leaving `harness-identities.json`. Block is `route="governance_review"`, `accept_with_inventory_baseline_update=false`, `required_evidence=["bridge report"]` — this child IS that report. |
| 3 | `scripts/collect_dev_environment_inventory.py` | **EDIT** — repoint `role_record_resolution` capability evidence (~L500) from `role-assignments.json` → `harness-registry.json`. |
| 4 | `.groundtruth/inventory/dev-environment-inventory.json` | **REGENERATE** — baseline cites the path at L374/451/528; regenerate so the inventory-drift gate passes (governance_review route + bridge report). |
| 5 | `platform_tests/scripts/test_mirror_retirement_role_assignments.py` | **CREATE** — assert (a) file absent; (b) grep_absent for live-code READS of the retired path; (c) drift-registry no longer lists it. |

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as REVISED versioned file; INDEX entry at top; no prior-version deletion/rewrite. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Spec-Derived Verification maps RETIRE-SPEC assertions → the deletion test (executable in scope). |
| `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` | blocking | content:retire, deletion | Operative authorization; assertions (a)+(b) become the test. |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | blocking | content:assertions | Intent proven by the deletion test (DCL `assertions` field empty; no `gt assert` to run — F2). |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | blocking | content:3 SoT surfaces, retired paths | Retired path removed; registry sole roles SoT. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Eliminates the stale mirror. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | Orphan deletion; no role-set VALUE changes. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:protected-artifact change | Drift-registry block requires a bridge report (governance_review); this child IS it. No formal-artifact-approval packet (no MemBase spec/GOV/DCL mutation; no protected NARRATIVE edited — toml/py/json are config/source). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH 134 v2; classes covered; WI-4336+WI-4214 included. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260668 + DELIB-20260880. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites framing specs + harness-state SoT specs. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4336 primary; WI-4214 covered; WI lifecycle resolution deferred (no groundtruth.db). WI-4372 follow-on created for doctor refinement. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 1 new platform test (deletion assertions). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | content:E:\GT-KB | All paths within `E:\GT-KB`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry SoT canonical; mirror removed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item | Deletion + cleanup + WI-4372 follow-on as governed artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Governed deletion; deliberation evidence cited. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:retired | RETIRE-SPEC terminal action; mirror lifecycle → deleted. |

## Requirement Sufficiency

**Existing requirements sufficient.** RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001 is operative; owner AUQ captured. Evidence: DELIB-20260668 (AUQ#3 clean-delete), DELIB-20260669 (drift), DELIB-20260880 (PAUTH v2). No new requirement. The verification narrowing is a correction of the acceptance check to the spec's actual assertion, not a requirement change.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella; GO at -004.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-{foundation-012,scripts-source-010,rule-files-010}.md` — VERIFIED prerequisites.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-002.md` — Codex NO-GO that drove this revision (F1 doctor-clean unachievable; F2 empty DCL assertions). Both correct; both addressed.
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` — operative authorization.
- `DELIB-20260668` (AUQ#3 clean delete) / `DELIB-20260669` (drift) / `DELIB-20260880` (PAUTH v2).
- `DELIB-20260763` / `DELIB-2750` — prior mirror-repoint review context (surfaced by Codex search).
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor (VERIFIED).

No previously rejected approach is being revisited.

## Owner Decisions / Input

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Clean-delete the mirror (no preservation) | AskUserQuestion | DELIB-20260668 AUQ#3 | The deletion |
| Phase-1 deletion batch approval | AskUserQuestion | RETIRE-SPEC "Phase-1 batch AUQ 4 of 4" | Authorizes WI-4336 |
| PAUTH v2 (WI-4336+WI-4214) | AskUserQuestion | DELIB-20260880 | PAUTH coverage |

No NEW owner AUQ required. No protected narrative edited; no formal-artifact-approval packet needed; drift-registry governance_review route satisfied by this bridge report.

## Acceptance Criteria (revised)

1. `harness-state/role-assignments.json` deleted (absent).
2. `protected-artifact-inventory-drift.toml` no longer lists the path; block retains `harness-identities.json`.
3. `collect_dev_environment_inventory.py` `role_record_resolution` evidence cites `harness-registry.json`.
4. `.groundtruth/inventory/dev-environment-inventory.json` regenerated; no `role-assignments.json` reference; inventory-drift pre-commit gate passes.
5. New test asserts file-absent + grep-absent-for-live-reads + drift-registry-absent; GREEN. **This is the spec-derived proof of RETIRE-SPEC assertions (a)+(b)** — NOT a doctor-clean claim.
6. `ruff check` + `ruff format --check` GREEN on the changed `.py`.
7. Commit lands cleanly (inventory-drift gate satisfied via governance_review + regenerated baseline; explicit-path `git add` only).
8. No project-root-boundary violation.
9. **Explicitly NOT claimed:** doctor `_check_harness_state_sot_consistency` fully clean. The doctor is WARN-only; remaining findings (retained retired-historical-evidence + out-of-scope L2 direct-readers) are tracked in **WI-4372**.

## Phased Implementation Plan

1. **Pre-grep**: confirm 0 live READS of the retired path (record evidence).
2. **Repoint generator**: `collect_dev_environment_inventory.py` `role_record_resolution` → `harness-registry.json`.
3. **Remove drift-registry entry**: `protected-artifact-inventory-drift.toml`.
4. **Delete** `harness-state/role-assignments.json`.
5. **Regenerate** `.groundtruth/inventory/dev-environment-inventory.json`; confirm no role-assignments.json reference.
6. **Write** `test_mirror_retirement_role_assignments.py` (3 assertions; (b) targets live READ patterns, not all mentions).
7. **Verify**: run the new test; `ruff` on the `.py`. (No `gt assert` for the empty-assertions DCL; no doctor-clean claim.)
8. **File** `-004.md` post-impl report (NEW) with spec-to-test mapping + executed results + applicability+clause preflights + explicit bridge-index audit-trail evidence (`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: filed under bridge/ with INDEX entry, no prior-version rewrite). Inline-JSON target_paths; `extract_target_paths` self-check.

## Specification-Derived Verification Plan (revised)

| Spec / requirement | Test / check (executable in scope) | Acceptance |
|---|---|---|
| RETIRE-SPEC assertion (a) file-absent | `test_mirror_retirement_role_assignments.py::test_file_absent` | `harness-state/role-assignments.json` does not exist |
| RETIRE-SPEC assertion (b) grep-absent (live reads) | `test_mirror_retirement_role_assignments.py::test_no_live_reads` | no `json.load`/`open`/`read_text`/`tomllib` of the path in `scripts/`+`groundtruth-kb/src/` outside whitelist |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` (intent) | same test (assertions field empty → no `gt assert`) | the test embodies the DCL's file-absent + no-direct-read intent |
| drift-registry consistency | `test_mirror_retirement_role_assignments.py::test_drift_registry_absent` | `protected-artifact-inventory-drift.toml` no longer lists the path |
| inventory regeneration | inventory-drift pre-commit gate | regenerated baseline has no role-assignments.json reference; gate passes |

## Risk and Rollback

**Risk 1 — inventory-drift gate blocks the commit.** Mitigation: governance_review route + bridge report + regenerated baseline; explicit-path `git add` of only the 5 targets; if still blocked, follow the hook's governance_review acceptance path (cite this bridge id), never `git add -A`.

**Risk 2 — a non-code reference breaks.** Mitigation: pre-grep confirms 0 live reads; non-code references enumerated (drift-registry → removed; inventory generator → repointed; retained retired-historical-evidence → unchanged, tracked under WI-4372 for the doctor refinement).

**Risk 3 — verification under-proves the retirement.** Mitigation: the test directly proves RETIRE-SPEC assertions (a)+(b), the operative authorization's own success criteria. The broader doctor-clean goal is a WARN-level hygiene target deferred to WI-4372, not a precondition of the deletion.

**Rollback:** `file_deletion` reversible via `git restore`; config/source/json edits file-level reversible. No spec mutation, no protected narrative, no WI mutation. If Codex NO-GO: nothing deleted (impl post-GO); superseded by REVISED-N.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green.

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
