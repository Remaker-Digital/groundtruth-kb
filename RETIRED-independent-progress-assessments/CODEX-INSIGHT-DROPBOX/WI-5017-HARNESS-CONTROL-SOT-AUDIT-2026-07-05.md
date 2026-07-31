# WI-5017 Harness and Control-Surface SoT Audit

Specs: GOV-HARNESS-STATE-SOT-CONSOLIDATION-001, DCL-HARNESS-STATE-SOT-READER-CONTRACT-001, REQ-HARNESS-REGISTRY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-PLATFORM-SOT-REGISTRY-001
WIs: WI-5017, WI-5012, WI-5011

## Claim

WI-5017 is complete as an audit-only lane. The harness/control-surface duplicate-SoT scan found one duplicate-SoT violation class, `duplicate-dispatch-harness-fields`, and confirmed it is already covered by remediation work item `WI-5012`. No new uncovered duplicate-SoT violation class was found, and this slice did not remediate source, configuration, registry, or MemBase state directly.

## Authorization And Scope

- Bridge thread: `gtkb-sot-singleton-harness-control-audit`
- Latest implementation-authorizing verdict: `bridge/gtkb-sot-singleton-harness-control-audit-002.md` (`GO`)
- Prime work-intent claim: rowid `30005`, acting role `prime-builder`, acquired `2026-07-05T06:38:36Z`
- Implementation authorization packet: `sha256:d07fe0c7359fa8f69ce0b1ad953094cd69a29257e295676c7e218bb04abc4cf0`
- Authorized target paths used: `.gtkb-state/sot-singleton-audit` and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX`

## Evidence

- `gt registry audit-duplicates --json --output-dir .gtkb-state/sot-singleton-audit/wi5017-harness-control` exited `0`.
- Evidence files written:
  - `.gtkb-state/sot-singleton-audit/wi5017-harness-control/sot-singleton-duplicate-audit.json`
  - `.gtkb-state/sot-singleton-audit/wi5017-harness-control/sot-singleton-duplicate-audit.md`
- Audit summary: `registry_count=25`, `persistent_file_count=93409`, `registered_file_count=10200`, `coverage_complete=true`, `violation_count=1`, `uncovered_violation_count=0`, `mutated_audited_artifacts=false`.
- Regression test: `python -m pytest groundtruth-kb/tests/test_sot_duplicate_audit.py -q --tb=short` produced `4 passed in 1.88s`.
- Bridge applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-harness-control-audit --json` passed with `missing_required_specs=[]` and `missing_advisory_specs=[]`.
- Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-sot-singleton-harness-control-audit` exited `0`, with `blocking gaps: 0`.
- WI-5012 state: `gt backlog show WI-5012 --json` reports `priority=P1`, `stage=backlogged`, `resolution_status=open`, and acceptance criteria requiring consolidation of the five duplicated dispatch fields.

## Finding

The audit classified the harness/control registry surfaces as registered SoTs, including `harness-identities`, `harness-registry`, `harness-bridge-substrate`, `harness-capability-registry`, and `session-startup-control-map`.

The one duplicate-SoT violation candidate is:

- Candidate: `duplicate-dispatch-harness-fields`
- Paths: `config/dispatcher/rules.toml` and `harness-state/harness-registry.json`
- Duplicated fields: `can_fire_events`, `can_receive_dispatch`, `dispatch_availability`, `dispatch_cost`, `dispatch_quality`
- Remediation: `WI-5012`
- Remediation status: `existing_covering_work_item`

The missing `bridge-index` registry artifact appears as an archive-lifecycle registry miss in the WI-5014 audit baseline, not as a WI-5017 duplicate-SoT violation class.

## Read-Only And Parser Checks

The audit engine reads audited artifacts and writes only evidence output. `groundtruth-kb/src/groundtruth_kb/project/sot_audit.py` reports `mutated_audited_artifacts: False`, reads candidate files through `read_text`, and confines evidence writes to `write_report_files(...)` output paths. The registry parser is not duplicated: `sot_audit.py` imports `load_toml` from `groundtruth_kb.project.sot_registry` and calls that registry loader for SoT registry records.

## Architecture Alignment Ledger

- OPS consolidation: keeps authoritative harness/control facts in registered SoT surfaces and treats reports as evidence, not replacement authority.
- Dispatcher daemon architecture: does not edit dispatcher configuration or runtime state; the known dispatcher/rules overlap remains delegated to WI-5012.
- Lifecycle-first / scoring-last precedence: does not activate scoring or ranking changes; it preserves the selection-binding remediation for the dedicated dispatch self-optimization lane.
- Portfolio reconciliation: avoids duplicate remediation work by linking the only confirmed violation class to the existing P1 WI-5012 rather than creating a competing work item.

## Risk / Impact

The immediate risk is bounded: duplicate dispatch fields still exist until WI-5012 completes, but WI-5017 confirms the risk is already tracked and uncovered duplicate-SoT violation count is zero. The report intentionally leaves remediation untouched to avoid conflicting with the dispatch self-optimization project.

## Recommended Action

Proceed with WI-5012 as the remediation lane for the five dispatch fields. No new WI-5017 remediation item is needed.

## Decision Needed From Owner

None.
