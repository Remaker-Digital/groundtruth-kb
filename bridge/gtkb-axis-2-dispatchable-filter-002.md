NO-GO

bridge_kind: review_verdict
Document: gtkb-axis-2-dispatchable-filter
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-axis-2-dispatchable-filter-001.md

## Applicability Preflight

- packet_hash: `sha256:2ef8ef8297b14c149d1eb3da152bcf9fd8f97b5b998357b0cebaf90a92fdbb88`
- bridge_document_name: `gtkb-axis-2-dispatchable-filter`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-axis-2-dispatchable-filter-001.md`
- operative_file: `bridge/gtkb-axis-2-dispatchable-filter-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-axis-2-dispatchable-filter`
- Operative file: `bridge\gtkb-axis-2-dispatchable-filter-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-2154` - compressed VERIFIED history for `gtkb-claude-axis-2-userpromptsubmit-bridge-surface`; relevant as the original AXIS 2 surface authorization.
- `DELIB-2105` - compressed VERIFIED history for `gtkb-reliability-fast-lane`; relevant to the standing reliability fast-lane framing.
- Bridge thread `smart-poller-kind-aware-routing-2026-04-30-009` - cited by the proposal as the source of the `dispatchable` field and dispatchability contract.
- Bridge thread `gtkb-axis-2-scoping-terminal-classifier-fix-002` - cited by the proposal as direct precedent for suppressing non-dispatchable AXIS 2 noise.

## Positive Confirmations

- The defect is real. `.claude/hooks/bridge-axis-2-surface.py` currently selects role-specific actionable items at line 164 and then computes the signature over every selected item without consuming the `dispatchable` flag.
- The source-side contract exists. `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` defines `ActionablePending.dispatchable`, marks `governance_review` as terminal-kind, and returns `dispatchable=False` for GO entries whose classification is terminal.
- The cross-harness trigger already uses compatibility-safe `getattr(item, "dispatchable", True)` filtering in `scripts/cross_harness_bridge_trigger.py`.
- WI-4278 exists as an open defect under `PROJECT-GTKB-RELIABILITY-FIXES`, and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active with `source`, `test_addition`, and `hook_upgrade` mutation classes.
- Existing AXIS 2 role/work-intent tests passed when rerun with a repo-local basetemp: 14 passed.

## Findings

### FINDING-P1-001 - Exact proposed filter breaks existing compatibility stubs

**Observation:** The proposal requires the exact implementation line `items = [item for item in items if item.dispatchable]` and repeats that line in the acceptance criteria. Existing AXIS 2 tests use lightweight item stubs with only `document_name`, `top_status`, and `top_file`, not `dispatchable`.

**Evidence:** Proposal lines 119-131 prescribe direct `item.dispatchable`; proposal line 170 repeats the same semantic line. `platform_tests/hooks/test_bridge_axis_2_role_aware.py` defines `_PRIME_ITEMS` / `_CODEX_ITEMS` stubs without `dispatchable`. The existing compatibility-safe precedent in `scripts/cross_harness_bridge_trigger.py` filters with `getattr(item, "dispatchable", True)`.

**Deficiency rationale:** The proposal's own verification plan says existing role-aware and work-intent AXIS 2 tests must continue to pass without modification. Direct attribute access makes the hook less tolerant than its sibling dispatch consumer and can fail existing monkeypatched test doubles even though legacy/ambiguous actionable items should continue to default to dispatchable.

**Impact:** Prime could implement exactly what the proposal authorizes and either break existing tests or need to modify unlisted existing test stubs. That would create avoidable target-path and acceptance drift in a small reliability fast-lane fix.

**Recommended action:** Revise the proposal to specify the compatibility-safe filter:

```python
items = [item for item in items if getattr(item, "dispatchable", True)]
```

Keep the existing new regression tests, and keep existing role/work-intent tests unchanged. If Prime intentionally wants direct attribute access, the proposal must explicitly authorize and justify the required existing-test updates.

## Required Revisions

- Replace the proposed and accepted direct `item.dispatchable` filter with `getattr(item, "dispatchable", True)`.
- Preserve the proposed terminal-kind GO regression and non-regression tests.
- Keep `platform_tests/hooks/test_bridge_axis_2_role_aware.py` and `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py` unchanged unless a revised proposal explicitly expands target scope and explains why compatibility with existing stubs should be dropped.

## Commands Executed

```powershell
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-axis-2-dispatchable-filter --format json --preview-lines 260
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-axis-2-dispatchable-filter
rg -n "dispatchable|_compute_actionable_for_role|ActionablePending|compute_actionable_pending|_derive_dispatchable|_KIND_TERMINAL_TOKENS" .claude/hooks/bridge-axis-2-surface.py groundtruth-kb/src/groundtruth_kb/bridge/notify.py scripts/cross_harness_bridge_trigger.py platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py -q --tb=short -p no:cacheprovider --basetemp .pytest-lo-axis2
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt backlog list --id WI-4278 --json
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt projects show PROJECT-GTKB-RELIABILITY-FIXES --json
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt deliberations search "GOV-RELIABILITY-FAST-LANE AXIS 2 surface bridge" --limit 8
```

Observed results: applicability preflight passed with no missing required or advisory specs; clause preflight exited 0 with zero blocking gaps; existing AXIS 2 role/work-intent tests passed with repo-local basetemp; the default pytest temp path previously failed on the known Windows temp ACL issue before the repo-local rerun.

## Owner Action Required

None.

## Opportunity Radar

No separate advisory filed. The deterministic improvement is already the subject of this bridge thread; the only additional efficiency point is to reuse the existing `getattr(..., True)` dispatch-trigger idiom rather than introduce a second compatibility rule.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
