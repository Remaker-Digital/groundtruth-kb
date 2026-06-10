GO
bridge_kind: lo_verdict
Document: gtkb-ollama-dispatch-stall-retry-cap
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-07 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-dispatch-stall-retry-cap-001.md

# Loyal Opposition Review - Ollama Dispatch Stall Retry Cap

## Verdict

GO.

The proposal is a narrow P1 reliability fix for the active bridge dispatch
substrate. It is eligible for the standing reliability fast-lane: live MemBase
shows `WI-4388` is an open defect in `PROJECT-GTKB-RELIABILITY-FIXES`, and the
active standing PAUTH covers source, test addition, and hook-upgrade mutation
classes for small reliability fixes by project membership.

The current live dispatcher state supports the problem statement. A diagnose
run still reports Loyal Opposition pending work with the selected signature
equal to `last_dispatched`, and classifies that state as healthy even though the
selected batch can be stuck behind failed worker launches. The source path also
still has the proposed gap: unchanged selected signatures return `unchanged`
without inspecting prior `last_launch` worker output.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:d47662882a4513878dbd5091b39a54e5be9595cd7ef3a886a3b5a2630e482a4b`
- bridge_document_name: `gtkb-ollama-dispatch-stall-retry-cap`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-dispatch-stall-retry-cap-001.md`
- operative_file: `bridge/gtkb-ollama-dispatch-stall-retry-cap-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing specs are advisory, not blocking. Prime should consider carrying
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` forward in the post-implementation report
if the implementation report discusses artifact lifecycle/retirement evidence.

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-dispatch-stall-retry-cap`
- Operative file: `bridge\gtkb-ollama-dispatch-stall-retry-cap-001.md`
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

Deliberation search was run before review:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "Ollama dispatch stall retry cap WI-4388 reliability fast lane" --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
```

Relevant records:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner decision establishing
  the standing reliability fast-lane while preserving bridge review, work-item
  tracking, and safety gates.
- `DELIB-20260909` - compressed VERIFIED bridge thread for
  `gtkb-ollama-dispatch-failure-hardening`; relevant predecessor baseline, now
  insufficient for the observed selected-signature stall.
- `DELIB-20260897` - compressed VERIFIED bridge thread for
  `gtkb-ollama-integration-phase-2-dispatch`; establishes prior dispatch wiring
  baseline.
- `DELIB-2509` - precedent warning against using the standing reliability
  PAUTH for non-defect feature work. It does not block this proposal because
  live `WI-4388` is a P1 defect and the scope is limited to two dispatcher/test
  paths.

## Backlog And Dependency Check

- Live `WI-4388` is open, priority `P1`, component `bridge-dispatch`, project
  `PROJECT-GTKB-RELIABILITY-FIXES`, origin `defect`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, cites
  `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`, and allows source/test/hook
  mutation classes under the reliability fast-lane.
- Current project membership shows related P1 bridge-dispatch items, but no
  higher-precedence dependency blocks this hotfix. The live failure affects LO
  dispatch throughput itself, so it should precede ordinary bridge cleanup.

## Review Notes

No blocking findings.

Implementation constraints for Prime Builder:

1. Keep the diff confined to `scripts/cross_harness_bridge_trigger.py` and
   `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
2. Preserve `DEFAULT_MAX_ITEMS = 2` for non-Ollama dispatch; the one-item cap
   must be specific to Ollama Loyal Opposition dispatch.
3. Preserve guard-denial behavior. The fix may classify guard-denied workers as
   failed dispatch evidence, but must not bypass the guard.
4. The post-implementation report must include focused regression tests for
   failed-prior-launch retry, Ollama one-item selection, and the mandatory
   preflight wording in the generated dispatch prompt.
5. The current worktree already contains unrelated changes in
   `platform_tests/scripts/test_cross_harness_bridge_trigger.py`; Prime should
   keep commit staging scoped so this hotfix is not bundled with other bridge
   or prompt work unless the post-implementation report explicitly explains the
   shared-file overlap.

## Positive Confirmations

- The full current thread was read with `show_thread_bridge.py`.
- The proposal carries project authorization, project, work-item, target-path,
  requirement-sufficiency, owner-decision, specification-link, and
  specification-derived verification sections.
- Mandatory applicability preflight passed with no missing required specs.
- Mandatory clause preflight passed with zero blocking gaps.
- Live `verify_ollama_dispatch.py --readiness-only` reports Ollama recipient
  `D` ready with required bridge-review tools.
- Live `cross_harness_bridge_trigger.py --diagnose --include-rotated-failures`
  still reports `loyal-opposition` as `last_result=unchanged`, pending work
  present, and selected signature matching `last_dispatched`, which matches the
  proposal's failure mode.

## Commands Executed

```text
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-ollama-dispatch-stall-retry-cap --format json --preview-lines 80
Get-Content -LiteralPath bridge\gtkb-ollama-dispatch-stall-retry-cap-001.md -Raw
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-dispatch-stall-retry-cap
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-dispatch-stall-retry-cap
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4388 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "Ollama dispatch stall retry cap WI-4388 reliability fast lane" --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
python scripts\cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.gtkb-state\bridge-poller --diagnose --include-rotated-failures
python scripts\verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB
rg "last_launch|last_dispatched|unchanged|DEFAULT_MAX_ITEMS|selected|Ollama|ollama|bridge_applicability_preflight|adr_dcl_clause_preflight" scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py -n
git diff -- scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
```

## Owner Action Required

None.

Prime Builder can implement within the approved target paths and file a
post-implementation report for Loyal Opposition verification.
