NEW

# Phase-1 Mirror-Retirement: delete harness-state/role-assignments.json + remove its drift-registry/inventory references (Child 4, final)

bridge_kind: prime_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-8
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
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

# KB-mutation note: groundtruth.db is intentionally NOT in target_paths. Per Codex
# rule-files -002 F1, WI-lifecycle resolution is not a PAUTH-covered mutation class;
# WI-4336/WI-4214 (and WI-4335 literal-acceptance closure) terminal resolution is
# deferred to a project-completion reconciliation bridge. This child performs the
# deletion + supporting cleanup only.

requires_verification: true
implementation_scope: implementation

## Why this proposal

This is the final child (Child 4) of harness-state SoT consolidation Phase-1. It deletes the orphaned legacy mirror `harness-state/role-assignments.json` — the end goal of the consolidation. All three prerequisites are VERIFIED:
- Foundation (-012): canonical reader entrypoint `groundtruth_kb.harness_projection` landed.
- scripts-source (-010): all direct code readers migrated to the entrypoint; stale config authority cleaned.
- rule-files (-010): legacy-mirror narrative removed from governance files; 2 overlay files deleted.

The RETIRE-SPEC's hard precondition — `PAUTH forbid: delete_active_referencer_without_migration` — is satisfied: a fresh grep of active Python (`scripts/`, `groundtruth-kb/src/`) finds ZERO `json.load`/`read_text`/`open`/`tomllib` reads of `harness-state/role-assignments.json`.

## Authorization

- **RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001** (specified v1) authorizes deletion under WI-4336 after migration. Its assertions: (a) file-absent post-WI-4336; (b) grep_absent — no live code references outside whitelisted bridge/audit/packet contexts. Successor: all read access flows through `groundtruth_kb.harness_projection` reading `harness-state/harness-registry.json`.
- **Owner AUQ** for the deletion was captured this session ("Phase-1 batch AUQ 4 of 4"; the RETIRE-SPEC records it) and re-affirmed via the rule-files implementation approval AUQ.
- **PAUTH rowid 134 v2** `allowed_mutation_classes` includes `file_deletion`, `config_file`, `source_file`, `test_file`; WI-4336 + WI-4214 are in `included_work_item_ids`.

## Scope — deletion + 3 coupled surfaces

A clean deletion requires handling the surfaces that reference the file, or the pre-commit inventory-drift gate and the dev-environment inventory break:

| # | Path | Action |
|---|------|--------|
| 1 | `harness-state/role-assignments.json` | **DELETE** (the legacy mirror; 1315 bytes). |
| 2 | `config/governance/protected-artifact-inventory-drift.toml` | **EDIT** — remove the `"harness-state/role-assignments.json",` pattern (L44) from the `[[protected_artifacts]] id="harness-identity-and-role-state"` block, leaving `harness-state/harness-identities.json` (still a live SoT). This block is `route = "governance_review"`, `accept_with_inventory_baseline_update = false`, `required_evidence = ["bridge report", ...]` — i.e., the deletion is EXPECTED to arrive via a governance-reviewed bridge with a report, which this child is. |
| 3 | `scripts/collect_dev_environment_inventory.py` | **EDIT** — repoint the `role_record_resolution` capability evidence (~L500) from `"harness-state/role-assignments.json"` → `"harness-state/harness-registry.json"` (the successor canonical SoT). Capability semantics unchanged; evidence path corrected. |
| 4 | `.groundtruth/inventory/dev-environment-inventory.json` | **REGENERATE** — the baseline currently cites `role-assignments.json` as evidence at 3 lines (374/451/528). Regenerate via `scripts/collect_dev_environment_inventory.py` so the public inventory reflects #1+#3 and the inventory-drift gate passes (governance_review route satisfied by this bridge report). |
| 5 | `platform_tests/scripts/test_mirror_retirement_role_assignments.py` | **CREATE** — assert (a) `harness-state/role-assignments.json` absent; (b) grep_absent for live-code reads of the retired path outside whitelisted contexts; (c) drift-registry no longer lists it. Mirrors DCL-HARNESS-STATE-SOT-ASSERTION-001 assertions. |

**Retained as retired-historical-evidence (NOT mutated):** `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md:67` and `SESSION-STARTUP-INDEX.md:26` document the mirror's retirement (framed "deprecated"/"orphan"); these remain accurate retirement records post-deletion and are intentionally left as provenance per the scripts-source disposition. The `.claude/rules/sot-read-discipline.md` historical-motivation reference (DELIB-20260673) is likewise archival evidence and stays.

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as NEW versioned bridge file; INDEX entry inserted at top; no prior-version deletion/rewrite. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps RETIRE-SPEC + assertion DCL to the deletion test + doctor check. |
| `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` | blocking | content:retire, deletion | The operative authorization; assertions (a)+(b) become the verification. |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | blocking | content:machine-checkable assertions | file-absent + grep-absent assertions hold post-deletion; doctor rolls them up. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | blocking | content:3 SoT surfaces, retired paths | Retired path removed; canonical registry remains sole roles SoT. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Eliminates the stale mirror; single-sourced on the registry. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | Deletion of orphan mirror; no role-set VALUE changes; registry unaffected. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:protected-artifact change | The drift-registry block requires a bridge report (governance_review route); this child IS that report. No formal-artifact-approval packet needed (no MemBase spec/GOV/DCL mutation and no protected NARRATIVE file edited — the toml + py + json are config/source, not narrative). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH rowid 134 v2; `file_deletion`+`config_file`+`source_file`+`test_file` covered; WI-4336+WI-4214 included. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260668 + DELIB-20260880. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs + the harness-state SoT specs. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4336 primary; WI-4214 covered. WI lifecycle resolution deferred to reconciliation bridge (no groundtruth.db mutation here). |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 1 new platform test (deletion assertions). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | content:E:\GT-KB | All paths within `E:\GT-KB`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry SoT canonical; mirror removed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item | Deletion + supporting cleanup as governed artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:retired | RETIRE-SPEC terminal action; mirror lifecycle → deleted. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Deletion + supporting cleanup tracked as governed artifacts; deliberation evidence in §Prior Deliberations. |

## Requirement Sufficiency

**Existing requirements sufficient.** RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001 is the operative authorization; owner AUQ captured (Phase-1 batch AUQ 4 of 4). Owner evidence: `DELIB-20260668` (8-AUQ, AUQ#3 clean-delete decision), `DELIB-20260669` (drift evidence), `DELIB-20260880` (PAUTH v2). No new requirement.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella; GO at -004; Child 4 scope at §"Child 4 — mirror-retirement".
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md` / `-scripts-source-010.md` / `-rule-files-010.md` — the three VERIFIED prerequisites.
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` — operative deletion authorization.
- `DELIB-20260668` — 8-AUQ scope (AUQ#3 = clean delete, no preservation).
- `DELIB-20260669` — drift evidence (registry vs mirror divergence on Antigravity harness A).
- `DELIB-20260880` — PAUTH v2 amendment.
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor slice that marked the mirror orphan (VERIFIED).

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Clean-delete the mirror (no preservation) | AskUserQuestion | DELIB-20260668 AUQ#3 | The deletion itself |
| Phase-1 deletion batch approval | AskUserQuestion | RETIRE-SPEC "Phase-1 batch AUQ 4 of 4" | Authorizes WI-4336 deletion |
| PAUTH v2 (covers WI-4336+WI-4214) | AskUserQuestion | DELIB-20260880 | PAUTH coverage |

No NEW owner AUQ required. No protected narrative files edited (config/source/test/json only), so no formal-artifact-approval packets needed; the drift-registry's governance_review route is satisfied by this bridge report.

## Acceptance Criteria

1. `harness-state/role-assignments.json` deleted (absent).
2. `protected-artifact-inventory-drift.toml` no longer lists the path; `harness-identity-and-role-state` block retains `harness-identities.json`.
3. `collect_dev_environment_inventory.py` `role_record_resolution` evidence cites `harness-registry.json`.
4. `.groundtruth/inventory/dev-environment-inventory.json` regenerated; contains no `role-assignments.json` reference; inventory-drift pre-commit gate passes.
5. New test asserts file-absent + grep-absent + drift-registry-absent; GREEN.
6. `gt project doctor` `_check_harness_state_sot_consistency` clean (no retired-path findings).
7. `ruff check` + `ruff format --check` GREEN on the changed `.py`.
8. Commit lands cleanly (inventory-drift gate satisfied via governance_review + regenerated baseline).
9. No project-root-boundary violation.

## Phased Implementation Plan

1. **Pre-grep**: confirm 0 live readers of the retired path (re-run the grep; record evidence).
2. **Repoint generator**: edit `collect_dev_environment_inventory.py` `role_record_resolution` evidence → `harness-registry.json`.
3. **Remove drift-registry entry**: edit `protected-artifact-inventory-drift.toml` (drop the role-assignments.json pattern line).
4. **Delete** `harness-state/role-assignments.json`.
5. **Regenerate** `.groundtruth/inventory/dev-environment-inventory.json` via `python scripts/collect_dev_environment_inventory.py` (or the documented regen entrypoint); confirm no role-assignments.json reference remains.
6. **Write** `platform_tests/scripts/test_mirror_retirement_role_assignments.py` (3 assertions).
7. **Verify**: run the new test + `gt project doctor` harness-state SoT check + the DCL-HARNESS-STATE-SOT-ASSERTION-001 assertions via `gt assert`; ruff on the `.py`.
8. **File** `-002.md` post-impl report (NEW) with spec-to-test mapping + executed results + applicability+clause preflights + bridge-index audit-trail evidence (per the rule-files -002 lesson: include explicit INDEX-entry/no-rewrite language so `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` evidence matches). Inline-JSON target_paths; `extract_target_paths` self-check.

## Specification-Derived Verification Plan

| Spec / requirement | Test / check | Acceptance |
|---|---|---|
| RETIRE-SPEC assertion (a) file-absent | `test_mirror_retirement_role_assignments.py` | `harness-state/role-assignments.json` does not exist |
| RETIRE-SPEC assertion (b) grep-absent | same test | no live-code read of the retired path outside whitelist |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | `gt assert` + `_check_harness_state_sot_consistency` | assertions pass; doctor clean |
| drift-registry consistency | same test | `protected-artifact-inventory-drift.toml` no longer lists the path |
| inventory regeneration | inventory-drift pre-commit gate | regenerated baseline has no role-assignments.json reference; gate passes |

## Risk and Rollback

**Risk 1 — inventory-drift gate blocks the commit.** Deleting a `governance_review`-routed protected artifact triggers the drift gate. Mitigation: the block is `accept_with_inventory_baseline_update = false` + `required_evidence = ["bridge report"]` — this child provides the bridge report; the baseline is regenerated in the same change. If the gate still blocks at commit time, the governance_review route is satisfied by citing this bridge id; implementation will follow the hook's documented governance_review acceptance path rather than `git add -A`/baseline-only bypass.

**Risk 2 — a non-code reference breaks.** Mitigation: pre-grep confirms 0 live code readers; non-code references are enumerated (drift-registry → removed; inventory generator → repointed; SESSION-STARTUP-* → retained retired-evidence). Codex review invited to flag any missed reference.

**Risk 3 — inventory regen pulls in unrelated drift.** Mitigation: regenerate immediately before commit; stage ONLY the 5 target_paths via explicit `git add` (never `git add -A`); if the regen surfaces unrelated harness drift from parallel sessions, reconcile per the Foundation-011 lesson (declare-and-explain vs corrective) and keep this commit scoped to the deletion.

**Rollback:** `file_deletion` reversible via `git restore`; config/source/json edits file-level reversible. No spec mutations, no protected narrative, no WI mutation. If Codex NO-GO: nothing deleted yet (impl is post-GO); this bridge file superseded by REVISED-N.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green.

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
