Status: NEW
Author: prime-builder (claude harness B)
Date: 2026-05-14
Session: S350
Source: WI-3178, WI-3179, WI-3180, WI-3181, WI-3182 (cluster)
Recommended commit type: docs
target_paths: ["scripts/inventory_verified_untested_spec_hygiene_cluster.py", "tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py", "bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-*.md", ".gtkb-state/verified-untested-spec-hygiene-cluster/inventory-manifest.json", ".gtkb-state/verified-untested-spec-hygiene-cluster/inventory-summary.md"]

## Summary

Five low-priority hygiene work items (WI-3178, WI-3179, WI-3180, WI-3181, WI-3182) sit on the standing backlog under the heading "Verified-but-untested spec hygiene: SPEC-<id> needs real test coverage." They were created on 2026-04-14 by the precedent thread `spec-hygiene-untested-verified-001..008` (VERIFIED at -008 on 2026-04-15), which downgraded the five specs from `verified` to `implemented` because no current non-stale passing test evidence could be linked. Subsequently on 2026-04-16, the POR Step 16.C Stream A A3 work bound one replacement test per spec (TEST-11082, TEST-11086, TEST-11092, TEST-11093, TEST-11099) — all five replacement tests currently report `last_result='fail'`. The WIs remain open because the bound tests do not yet provide passing evidence.

This is a BULK-ADJACENT operation (5 specs, 5 WIs, 5 replacement tests). To stay safely inside the bulk-ops clause and the GOV-15 test-fix gate, this slice produces an **inventory deliverable only** — one classification report per spec recording current MemBase state, current test binding, plausible disposition path, and recommended Slice 2 action. **No status mutation, no test creation, no WI closure occurs in this slice.** All five spec mutations / test repairs are deferred to a separate Slice 2 proposal authored after owner reviews the inventory.

## Affected Specs Inventory Pre-Read

Probed via `groundtruth_kb.db.KnowledgeDB.get_spec()` + `list_tests(spec_id=...)` at 2026-05-14:

| Spec ID | Current status | Currently linked tests | Latest test result |
|---------|---------------|------------------------|--------------------|
| SPEC-1076 | `implemented` | TEST-11092 (`tests/regression/test_upgrade_regression.py::TestTier1Cycle9Endpoints::test_t1_24_superadmin_alert_history`) | `fail` (2026-04-16) |
| SPEC-1078 | `implemented` | TEST-11093 (`tests/regression/test_upgrade_regression.py::TestTier1Cycle9Endpoints::test_t1_25_superadmin_mfa_status`) | `fail` (2026-04-16) |
| SPEC-0661 | `implemented` | TEST-11082 (`tests/performance/test_performance.py::TestCostModelPerformance::test_cost_model_tier_pricing`) | `fail` (2026-04-16) |
| SPEC-0811 | `implemented` | TEST-11086 (`tests/performance/test_performance.py::TestThroughputConcurrency::test_perf_17_pipeline_budget_stage_timeout`) | `fail` (2026-04-16) |
| SPEC-1138 | `implemented` | TEST-11099 (`tests/unit/test_chat_endpoints.py::TestReportIssue::test_report_issue_conversation_not_found`) | `fail` (2026-04-16) |

All five replacement tests were created during POR Step 16.C Stream A A3 on 2026-04-16 with `change_reason="POR Step 16.C Stream A A3: replacement test binding for SPEC-<id> after test_id <orig> was recycled; historical row v<n> used as template (pytest outcome=fail, DB last_result=fail)"`. No specification currently sits at `verified`; the WI titles ("Verified-but-untested") encode the historical condition that originally created them, not the live MemBase state.

## Specification Links

- SPEC-1076 — POST /alerts/history/{alert_id}/acknowledge endpoint in superadmin_api (in-scope spec; WI-3178)
- SPEC-1078 — GET /mfa/status endpoint in superadmin_api (in-scope spec; WI-3179)
- SPEC-0661 — Pricing MUST include usage-based overage charges with documented thresholds (in-scope spec; WI-3180)
- SPEC-0811 — The pipeline budget MUST reflect a P50 of 7,000ms and a stage timeout of 8,000ms (in-scope spec; WI-3181)
- SPEC-1138 — Define widget views: closed, prechat, otp, conversation, rating, offline_form, issue_report (in-scope spec; WI-3182)
- GOV-FILE-BRIDGE-AUTHORITY-001 — file bridge as live workflow authority
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — mandatory specification linkage
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — mandatory spec-derived tests
- GOV-STANDING-BACKLOG-001 — standing backlog governance (WI-3178..3182 selection authority)
- GOV-ARTIFACT-APPROVAL-001 — formal artifact approval (informational; no MemBase mutation in this slice)
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — applications/* placement convention (project-root boundary; inventory output stays in-root under `.gtkb-state/`)
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — artifact-oriented governance (inventory IS an artifact)
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — artifact-as-record-of-decision
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle triggers
- `.claude/rules/file-bridge-protocol.md` — bridge protocol (this proposal's form)
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review gate
- `.claude/rules/project-root-boundary.md` — root-boundary discipline (all outputs within `E:\GT-KB`)

## Prior Deliberations

- DELIB-0094 — bridge thread `spec-hygiene-untested-verified-001..008` (VERIFIED at -008, 2026-04-15). Direct precedent: SAME 5 specs were downgraded from `verified` to `implemented` and the SAME 5 WIs (WI-3178..3182) were created. See `bridge/spec-hygiene-untested-verified-007.md` (post-implementation report) and `bridge/spec-hygiene-untested-verified-008.md` (VERIFIED verdict).
- DELIB-0750 — bridge thread `por-step16c-implemented-untested-remediation` (VERIFIED). Direct precedent for the replacement-test-binding pattern that produced TEST-11082/11086/11092/11093/11099 on 2026-04-16.
- DELIB-0751 — bridge thread `por-step16b-methodology-review` (VERIFIED). Methodology baseline that constrains the spec-hygiene remediation pattern (per-spec disposition; revert-vs-restore evidence rubric).
- DELIB-1268 — bridge thread `por-step16a-verified-spec-closure` (10 versions, ORPHAN). Background context on the closure flow that originally promoted these 5 specs to `verified`.
- DELIB-0871 — Loyal Opposition Review: Commercial Readiness Spec Verification (NO-GO). Wider context on the rigor required for verified-state evidence.
- bridge thread `spec-hygiene-spa-remediation-001..006` (VERIFIED at -006, 2026-04-15). Sibling cluster precedent: 10 control-plane specs downgraded from `verified` to `implemented` under the same revert-rather-than-restore discipline. Established the "single bulk hygiene WI; per-spec mutations recorded; SPEC-1837 baseline preserved" pattern that this thread's Slice 2 should adopt.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" + "Please continue to parallelize work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 — AUQ-resolved batch authorization). The 5 WIs in this cluster (WI-3178..WI-3182) share a single inventory deliverable in this slice; per-spec mutations are deferred to Slice 2.

## Clause Scope Clarification (Bulk-Adjacent Operation)

The bulk-ops clause of `GOV-STANDING-BACKLOG-001` (CLAUSE-VISIBILITY-BULK-OPS) may be read to apply because this proposal references five work items (WI-3178..3182), five specifications, and the standing backlog. To remove ambiguity for the clause preflight:

- The operative deliverable of Slice 1 is a SINGLE `inventory` manifest file plus a SINGLE markdown summary plus ZERO MemBase mutations. No work_item is closed, retired, reordered, or created. No specification is promoted, demoted, or retired. No test is created, updated, retired, or re-bound. No deliberation row is inserted other than the optional single `session_harvest` row recording inventory completion (governed by the existing harvest scripts under content-hash idempotence per `SPEC-DA-RETROACTIVE-SWEEP`).
- The downstream Slice 2 proposal — which IS the per-spec disposition mutation (each spec may need test repair, status preservation, or WI closure) — is a separate bridge thread that must carry its own owner approval and its own Codex review GO. Slice 2 is where any actual bulk-operation gating applies.
- The `formal-artifact-approval` packet workflow per `GOV-ARTIFACT-APPROVAL-001` does NOT apply to Slice 1 because no canonical artifact (GOV / ADR / DCL / PB / SPEC / narrative-artifact) is created or modified by this slice.
- Tokens for clause-preflight scope evidence: `inventory`, `formal-artifact-approval`.

## Requirement Sufficiency

Existing requirements sufficient. The applicable governing specifications (the five in-scope SPEC- IDs whose hygiene state this inventory measures, plus GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001, GOV-ARTIFACT-APPROVAL-001, and the bridge-protocol rule set) collectively constrain the inventory output shape, the audit-trail requirement, and the boundary between Slice 1 (inventory) and Slice 2 (mutation). No new specification capture is required for this slice. If Slice 2 surfaces disposition ambiguity not covered by the existing precedent (e.g., a sixth disposition class beyond "fix test", "revert binding", "preserve as-is with note"), that slice's proposal will surface the gap as a candidate SPEC update.

## Investigation Methodology

The inventory script (`scripts/inventory_verified_untested_spec_hygiene_cluster.py`) performs **read-only** MemBase access for the five in-scope specs and emits one record per spec.

**Per-spec resolution (read-only):**

1. Resolve current `specifications` row via `db.get_spec(spec_id)` — capture `id`, `version`, `status`, `type`, `title` (truncated to 200 chars), `change_reason`, `changed_by`, `changed_at`.
2. Resolve currently linked tests via `db.list_tests(spec_id=spec_id)` — for each test capture `id`, `version`, `last_result`, `last_executed_at`, `test_file`, `test_class`, `test_function`, `change_reason`, `changed_by`, `changed_at`.
3. Look up the originating WI via `db.list_work_items(source_spec_id=spec_id, status='open')` and record the WI id, title, origin, stage, priority.
4. Probe the test file on disk: confirm `test_file` exists and the `test_class::test_function` symbol is present (static parse via `ast`, not execution). Record `file_present`, `symbol_present` booleans.
5. Compute the test-result history shape from `tests` version chain: `result_history` = list of `(version, last_result, changed_at)` newest-first, truncated to 5.
6. Classify each spec into one of five disposition buckets (rules below). Record `classification` and `classification_reason`.

**Classification rules (per spec; deterministic):**

- `fixable_test_present` — `file_present=True` AND `symbol_present=True` AND latest test `last_result='fail'` AND `test_file` is in a unit/regression directory that does NOT require a live external server (no `tests/regression/test_upgrade_regression.py` and no `tests/performance/` for SPEC-0661/0811). The Slice 2 disposition path is "fix the test or the implementation it exercises until it passes; promote spec back to `verified`".
- `live_server_required_test` — `test_file` matches `tests/regression/test_upgrade_regression.py` (live PROD_URL required). Bound test cannot pass under standard CI. Slice 2 disposition: re-bind to a unit-level test fixture OR explicitly mark the binding as live-only with an environment-gated runner. Applies to SPEC-1076 and SPEC-1078 by current evidence.
- `performance_oracle_required_test` — `test_file` matches `tests/performance/test_performance.py`. Bound test asserts performance characteristics that require a measurement harness. Slice 2 disposition: confirm the performance oracle is implementable; either fix the harness or split the spec into an executable unit-level slice plus a measurement-tier sub-spec. Applies to SPEC-0661 and SPEC-0811 by current evidence.
- `behavioral_mismatch` — test exists and passes on its own merits but does not assert the spec's stated behavior (precedent for SPEC-1138 per the -007 post-implementation report: backend 404 test bound to a frontend widget-view spec). Slice 2 disposition: re-bind to a test that does assert the spec's behavior or split the spec.
- `unresolvable_in_scope` — none of the above classifications apply; spec is parked for owner review and possible retirement. Emitted as a fallback.

**Output shape.** Two files written to `.gtkb-state/verified-untested-spec-hygiene-cluster/`:

- `inventory-manifest.json` — JSON array, one record per spec: `{ spec_id, spec_status, spec_version, spec_title, spec_changed_at, current_tests, wi_id, wi_title, wi_stage, wi_priority, file_present, symbol_present, result_history, classification, classification_reason, recommended_slice2_action }`. Plus a `_meta` block: `{ generated_at, gt_repo_root, script_sha256, db_path, source_thread }`.
- `inventory-summary.md` — human-readable summary: per-spec one-block summary (~10 lines each), table of `classification` counts, recommended Slice 2 ordering.

A single optional DA row of `source_type='session_harvest'` MAY be inserted recording inventory completion (manifest content hash + generated_at + cluster WI references), governed by the existing harvest infrastructure under content-hash idempotence per `SPEC-DA-RETROACTIVE-SWEEP`. The script supports `--dry-run` (default — manifest written but no DA write) and `--apply` (DA write enabled).

## Deliverables

Single deliverable cluster:

1. `scripts/inventory_verified_untested_spec_hygiene_cluster.py` — the inventory script.
2. `tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py` — the test module per the Test Mapping below.
3. `.gtkb-state/verified-untested-spec-hygiene-cluster/inventory-manifest.json` — the JSON manifest (generated; not source-controlled by default; attached to the post-implementation report).
4. `.gtkb-state/verified-untested-spec-hygiene-cluster/inventory-summary.md` — the human-readable summary (generated; not source-controlled by default; attached to the post-implementation report).
5. Optional single DA `session_harvest` row recording inventory completion (idempotent via content-hash; written only in `--apply` mode after Codex GO).

No mutations to `specifications`, `tests`, `work_items`, or any other governed record set occur in Slice 1.

## Test Mapping

Tests are derived from the linked specifications. All tests live in `tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py`.

| Test | Specification(s) covered |
|------|---------------------------|
| `test_resolver_returns_current_spec_row_per_id` | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001 (deterministic resolver against MemBase) |
| `test_resolver_emits_one_record_per_in_scope_spec` | The five in-scope SPEC- IDs (output cardinality invariant) |
| `test_classification_fixable_test_present_rule` | SPEC-1076/1078/0661/0811/1138, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |
| `test_classification_live_server_required_test_rule` | SPEC-1076, SPEC-1078 (test_file is upgrade_regression — live PROD_URL required) |
| `test_classification_performance_oracle_required_test_rule` | SPEC-0661, SPEC-0811 (test_file is performance harness — oracle required) |
| `test_classification_behavioral_mismatch_rule` | SPEC-1138 (behavioral mismatch precedent from -007 report) |
| `test_output_is_idempotent_for_fixed_inputs` | GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (regenerable evidence; same inputs → same outputs) |
| `test_no_mutation_in_dry_run_mode` | GOV-ARTIFACT-APPROVAL-001 (Slice 1 carries no MemBase mutation) |
| `test_audit_trail_completeness_meta_block` | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (audit metadata: generated_at, script_sha256, db_path) |
| `test_root_boundary_outputs_under_gtkb_state` | ADR-ISOLATION-APPLICATION-PLACEMENT-001, `.claude/rules/project-root-boundary.md` |
| `test_summary_lists_recommended_slice2_action_per_spec` | The five in-scope SPEC- IDs (deliverable completeness) |

11 tests; all unit-level; no live server, no performance harness, no external network.

## Risk and Rollback

**Risk.** Read-only against MemBase under dry-run mode. Output writes are confined to `.gtkb-state/verified-untested-spec-hygiene-cluster/` (a runtime evidence directory, not a canonical authority surface). No specification is promoted or demoted; no test is created or retired; no work item is closed or reordered. The five WIs (WI-3178..3182) remain open after Slice 1 completes; closure is Slice 2's responsibility.

**Rollback.** Delete the two output files under `.gtkb-state/verified-untested-spec-hygiene-cluster/`. If the optional `session_harvest` DA row was inserted, it is content-hash-idempotent and self-supersedes on re-run; no rollback required for the DA row beyond simply not citing it. The script and tests are conventional file additions and can be removed by reverting the commit.

## Acceptance Criteria

1. `scripts/inventory_verified_untested_spec_hygiene_cluster.py` exists and runs to completion in dry-run mode against the live `groundtruth.db` without raising.
2. The output manifest at `.gtkb-state/verified-untested-spec-hygiene-cluster/inventory-manifest.json` contains exactly 5 spec records (one per SPEC-1076, SPEC-1078, SPEC-0661, SPEC-0811, SPEC-1138).
3. Each record carries `classification` in the closed set `{fixable_test_present, live_server_required_test, performance_oracle_required_test, behavioral_mismatch, unresolvable_in_scope}` with non-empty `classification_reason`.
4. Each record carries the current MemBase status (`implemented` at proposal time, but the manifest reads live state) and the currently linked test id (TEST-11092, TEST-11093, TEST-11082, TEST-11086, TEST-11099 at proposal time).
5. The summary at `.gtkb-state/verified-untested-spec-hygiene-cluster/inventory-summary.md` lists per-spec recommended Slice 2 action.
6. All 11 unit tests in `tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py` pass.
7. No `specifications`, `tests`, or `work_items` row is mutated by Slice 1.
8. All output paths are inside `E:\GT-KB`.

## Verification Plan

Post-implementation report will include:

1. The full inventory-manifest.json output pasted under triple-backtick fence.
2. The full inventory-summary.md output pasted under triple-backtick fence.
3. `python -m pytest tests/scripts/test_inventory_verified_untested_spec_hygiene_cluster.py -v` output (all 11 tests passing).
4. Pre-write and post-write counts for `specifications`, `tests`, `work_items` confirming zero delta.
5. Pre-write and post-write `groundtruth.db` SHA-256 hash confirming the database file was not modified (dry-run mode).
6. SPEC-1837 baseline preservation check (a sibling-cluster precedent invariant): 35 current rows; verify unchanged after Slice 1 completes.
7. The recommended Slice 2 disposition path for each of the five specs in narrative form.
8. Optional DA `session_harvest` row id + content-hash, if `--apply` mode was used after Codex GO.

## Applicability Preflight

Generated via `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory --content-file <this-file>`:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
packet_hash: <recorded at file time>
```

(Authoritative result captured in the file-author report; the preflight is re-run by Loyal Opposition during review.)

End of proposal.
