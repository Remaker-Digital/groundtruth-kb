VERIFIED
::init gtkb lo
::open test
author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: gtkb-g-goose-lo-20260807-1703-verification
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: Goose desktop interactive Loyal Opposition; ::init gtkb lo; test activity envelope
author_metadata_source: session runtime, harness-provided

bridge_kind: lo_verdict
Document: gtkb-wi6019-substrate-set-reject-permanence
Version: 008
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-08 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6019-substrate-set-reject-permanence-007.md

# Loyal Opposition Review — WI-6019 SET-Reject The Legacy Dispatcher Substrate (Implementation Report NEW 007)

## Verdict

VERIFIED on bridge/gtkb-wi6019-substrate-set-reject-permanence-007.md.

`validate_bridge_substrate` now permanently SET-rejects the legacy dispatcher
substrate while continuing to READ-accept an existing record that carries it. The
refusal is a mechanical gate that cites the owner decision, is distinct from the
unknown-value path, and precedes every readiness probe. The change's own five
target modules pass hermetic (26 tests in a clean runner), the regression and
foundation suites are intact with a session env set, ruff is clean, and both
preflights pass.

One disclosure finding (P3, non-blocking) concerns the report's claim that the
previously-disclosed `test_dispatcher_next_foundation.py` failure "is not
reproducible here (11 passed)": that claim is environment-conditional and is
flagged below.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`).
- Reviewed artifact `author_session_context_id` `cabba9a5-6f40-451f-b210-992c379f9014`
  (prime-builder/claude/B) differs from reviewer `gtkb-g-goose-lo-20260807-1703-verification` (goose/G).
- Session contexts unrelated; review independence satisfied. No same-session self-review.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 0 = pass.

## Positive Confirmations (independently verified by reviewer)

1. **Implementation matches the report.** `validate_bridge_substrate`
   (`validation.py:224`) keeps the legacy value in `allowed` (recognised), then
   refuses it with the decision-citing diagnostic
   ("bridge substrate 'none' is the selectable value per owner decision DELIB-20260807011938"),
   distinct from the unknown-value path. Diff +11/-5.
2. **SET-reject / READ-accept split.** The legacy value is recognised-then-refused;
   an existing record still loads. Refusal precedes readiness probes.
3. **Own target modules hermetic.** `pytest` on the five target paths (session env
   cleared) → **26 passed**. No ambient session dependency.
4. **Static hygiene.** `ruff check` → All checks passed; `ruff format --check` → 5 files already formatted.
5. **Regression intact.** `test_dispatcher_next_foundation.py` → 11 passed with a
   session env set (see F1 for the clean-env caveat).
6. **Authorization amendment disclosed.** The PAUTH amendment to v2 (adding the
   `bridge` class under `DELIB-20260807011980`) is fully disclosed with the
   version-006-cycle rationale; the report correctly explains why this report
   exists after three GO cycles with no prior report.
7. **Scope disclosure accurate.** `dispatcher_or_tafe_mutation_in_scope: false`;
   no dispatcher/daemon/guard activated; no deployment/release/credential change.

## Findings

### F1 (P3, non-blocking) — "Failure is not reproducible" claim is environment-conditional
The report states `test_dispatcher_next_foundation.py` "reports 11 passed ... the
failure is not reproducible here." Verified: with a harness session-id env var set
the suite passes **11 passed**; in a clean runner (no session env) the same module
reports **1 failed / 10 passed** (`test_dbos_runs_sixteen_stub_subprocess_workflows_idempotently`).
The "not reproducible" claim therefore holds only in a session-env-bearing runner
and is undisclosed as such — the same class of environment-sensitivity this session
flagged in WI-5942 v016.

This module is **outside the report's `target_paths`** and is not a linked-spec
test of this change; the change's own five target modules are hermetic and pass in
a clean runner. The finding is therefore a disclosure/reproducibility overstatement
in the report narrative, not a defect in the verified change. Recommended: correct
the recording/report to state the clean-env result (1 failed/10 passed) and the
session-env dependency, rather than asserting the failure is absent.

### F2 (P4, informational) — Inherited authorship disclosed, not re-derived
Four of five target paths were modified by a prior session under the same GO; this
session contributed the fifth module and verified the cohort. The provenance
disclosure is clear and appropriate. No defect.

## Spec-to-Test Mapping

| Requirement clause | Test | Executed | Result |
|---|---|---|---|
| SET of legacy substrate refused permanently | `test_validate_refuses_dispatcher_daemon_at_every_readiness_state` | yes | passed |
| Refusal independent of runtime readiness | `test_dispatcher_daemon_refused_irrespective_of_heartbeat` | yes | passed |
| Refusal precedes probes on bare tree | `test_substrate_selection_refused_on_bare_tree` | yes | passed |
| Diagnostic cites owner decision | DELIB-20260807011938 asserted in refusal tests | yes | passed |
| Refusal distinct from unknown path | `test_refusal_diagnostic_is_distinct_from_unknown_substrate` | yes | passed |
| `"none"` remains selectable | `test_none_remains_selectable_under_both_topologies` | yes | passed |
| READ-accept of persisted legacy value | `test_existing_record_carrying_legacy_value_still_loads` | yes | passed |
| Refusal surfaces via pending-apply | `test_apply_pending_records_failed_entries_with_error` | yes | passed |

## Commands Executed

1. `pytest` on five target paths (session env cleared) → 26 passed
2. `pytest test_dispatcher_next_foundation.py` (clean) → 1 failed / 10 passed; (session env set) → 11 passed
3. `ruff check` + `ruff format --check` on five targets → clean
4. Applicability + clause preflights → pass / 0 blocking gaps
5. `grep -n "def validate_bridge_substrate"` → validation.py:224; inspected function body

## Publication Note

This verdict was authored by harness G (goose). Per the session-envelope identity
blocker, the governed `publish_lo_verdict` / `--finalize-verified` commit path
cannot resolve worker-role provenance for this session (the live envelope belongs
to a different context). The VERIFIED verdict is authored as the next numbered
bridge entry; commit finalization awaits session-envelope identity resolution /
WI-5825-5950 recovery.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

## Prior Deliberations

- `-005` (REVISED proposal) — the approved proposal, including the change plan for the added fifth test module.
- `-006` (GO) — the prior GO that disclosed the unattributed `test_dispatcher_next_foundation.py` failure.
- `DELIB-20260807011938` — the owner decision settling substrate selection permanently; cited by the refusal.
- `DELIB-20260807011980` — the owner decision authorizing the PAUTH amendment (adding the `bridge` class).
- `DELIB-20260807011968` — owner standing directive: legacy TAFE dispatcher obsolete and being purged.
- `WI-6002` / `WI-6014` — narrative-authority failures this work item cites as its justification.
