GO

bridge_kind: lo_verdict
Document: gtkb-wi4480-dispatch-starvation-telemetry
Version: 002
Author: Loyal Opposition (Codex, harness A)
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-14T02-01-37Z
Date: 2026-06-14 UTC
Reviewer: Loyal Opposition
Author-Harness-ID: A
Responds to: bridge/gtkb-wi4480-dispatch-starvation-telemetry-001.md
Recommended commit type: feat:

# Loyal Opposition GO Verdict: WI-4480 Dispatch-Starvation Telemetry

## Verdict

GO.

Prime Builder may implement the WI-4480 Slice A detector within the declared
target paths:

- `scripts/bridge_dispatch_starvation_telemetry.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`

This GO is limited to observational telemetry for per-entry non-selection. It
does not authorize changing dispatch ordering, `_selected_oldest_first`,
`_signature`, actionable-signature semantics, fairness/priority selection,
single-harness dispatch integration, deployment, formal artifact mutation, or
any edit outside the target paths.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4480-dispatch-starvation-telemetry
```

Result:

- packet_hash: `sha256:2782bf9438e5c24a69469be08ef70e4b3c80312a47c6474cbabba6c0297af377`
- bridge_document_name: `gtkb-wi4480-dispatch-starvation-telemetry`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi4480-dispatch-starvation-telemetry-001.md`
- operative_file: `bridge/gtkb-wi4480-dispatch-starvation-telemetry-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4480-dispatch-starvation-telemetry
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4480-dispatch-starvation-telemetry`
- Operative file: `bridge\gtkb-wi4480-dispatch-starvation-telemetry-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

Commands:

```powershell
python -m groundtruth_kb.cli deliberations search "WI-4480 dispatch starvation telemetry" --limit 10
python -m groundtruth_kb.cli deliberations search "dispatch starvation" --limit 10
python -m groundtruth_kb.cli deliberations get DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION
python -m groundtruth_kb.cli deliberations get DELIB-0502
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-scheduler-lanes-leases-slice-6 --format json --preview-lines 40
```

Relevant results:

- `DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION` records owner approval to admit WI-4480 and eight sibling standalone defects to `PROJECT-GTKB-RELIABILITY-FIXES` under the bounded batch PAUTH.
- `DELIB-0502` is older bridge-recovery context describing queue starvation and false-health signaling as bridge reliability risks.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-004.md` VERIFIED the standalone `scripts/bridge_dispatch_priority.py` scoring primitive. That prior work is not a blocker here because it explicitly left live dispatch wiring for a later integration slice; WI-4480 observes the current live oldest-first selector rather than replacing it.
- The exact query `"WI-4480 dispatch starvation telemetry"` returned no direct semantic deliberation hits.

## Evidence Reviewed

- Live bridge authority: `bridge/INDEX.md` read directly before review.
- Proposal under review: `bridge/gtkb-wi4480-dispatch-starvation-telemetry-001.md`.
- Live backlog row: `python -m groundtruth_kb.cli backlog list --id WI-4480 --json` confirms WI-4480 is open, P2, component `bridge-dispatch`, and describes the cap-2 oldest-first starvation hazard.
- Live project authorization: `python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` confirms `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1` is active, includes WI-4480, and permits `source` plus `test_addition` while forbidding formal artifact mutation, deployment, force push, credential lifecycle work, and broad bulk status mutation.
- Current dispatch code: `scripts/cross_harness_bridge_trigger.py` still computes `selected = _selected_oldest_first(filtered, target_max_items)` and `signature = _signature(selected)` before the recipient state update.
- Current selector: `_selected_oldest_first` remains pure oldest-first cap behavior.
- Current duplicate-risk surface: `scripts/bridge_dispatch_priority.py` exists and is tested, but its module docstring says live wiring is deferred and current dispatch behavior is unchanged.
- Target pre-state: `scripts/bridge_dispatch_starvation_telemetry.py` and `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py` do not yet exist.

## Review Findings

### Authorization And Linkage

PASS. The proposal cites the active PAUTH, project, WI, target paths, and
governing bridge/spec-derived verification requirements. The mechanical
applicability preflight reports no missing required or advisory specs, and the
mandatory clause preflight reports zero blocking gaps.

### Duplicate And Precedence Risk

PASS with implementation note. The existing scheduler Slice 6 priority module
is relevant prior work, but it is not wired into the live cross-harness trigger
and therefore does not resolve WI-4480's current evidence gap. Prime Builder
should not import or integrate `scripts/bridge_dispatch_priority.py` in this
Slice A implementation; that belongs to a later Slice B or scheduler integration
proposal that deliberately changes selection behavior.

### Scope Boundary

PASS. The design adds one telemetry module, one focused test file, and one
exception-swallowed observational call after `filtered`, `selected`, and the
selected-batch signature are computed. That is a minimal-risk detector slice and
does not change selection behavior by design.

### Verification Plan

PASS. The proposed tests cover increment/reset/prune/threshold behavior,
`first_starved_at` preservation, persistence, fail-safe behavior, and the
selected-batch signature invariant. The required implementation report should
also run the existing cross-harness trigger tests that protect `_signature` and
selected-batch semantics.

## Required Implementation Verification

Prime Builder's implementation report should include, at minimum:

```powershell
python -m pytest platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts/bridge_dispatch_starvation_telemetry.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py
python -m ruff format --check scripts/bridge_dispatch_starvation_telemetry.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4480-dispatch-starvation-telemetry
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4480-dispatch-starvation-telemetry
```

The report should also show:

- telemetry failures cannot raise into dispatch;
- unchanged selected-batch signature behavior remains byte-identical;
- telemetry state is separate from dispatch-state signature fields;
- entries selected on a later dispatch reset their non-selection counters;
- entries no longer actionable are pruned;
- no selector fairness or priority integration was implemented in this slice.

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
