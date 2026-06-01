NO-GO
author_identity: Codex Loyal Opposition
author_harness_id: A
dispatch_id: 2026-06-01T01-07-48Z-loyal-opposition-713f70

# Loyal Opposition Review - gtkb-backlog-update-cli-slice-1

Document: gtkb-backlog-update-cli-slice-1
Version: 002 (NO-GO)
Reviewed proposal: bridge/gtkb-backlog-update-cli-slice-1-001.md
Date: 2026-06-01 UTC

## Verdict Summary

NO-GO. The proposal is well-scoped, has valid project authorization, and passes the mandatory bridge preflights, but it has one blocking GOV-15 safety gap: the planned `gt backlog update --resolution-status resolved` surface can resolve a defect/regression work item without owner approval if it changes only `resolution_status` and leaves `stage` unchanged.

This is not hypothetical. The current `KnowledgeDB.update_work_item()` implementation runs the owner-approval gate through `_validate_stage_transition(...)`, and that validator returns immediately when `new_stage == current_stage`. A temporary DB probe showed `update_work_item(..., resolution_status="resolved", owner_approved=False)` on a defect work item succeeds with `resolution_status=resolved`, `stage=created`, `version=2`.

Prime should revise the proposal so the CLI treats any terminal `resolution_status` transition to `resolved` for `origin in {"defect", "regression"}` as GOV-15-gated, regardless of whether `--stage resolved` is also supplied.

## Prior Deliberations

Read/search evidence:

- `gt deliberations get DELIB-2546 --json` returned the S379 owner AUQ authorization for WI-3436 and confirms the owner-selected scope: `gt backlog update` / `gt backlog resolve` CLI plus tests.
- `gt deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE --json` returned the deterministic-services owner principle; this proposal is aligned with that principle.
- `gt deliberations get DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM --json` returned the owner decision establishing the reconciler path that motivates `related_bridge_threads` backfill.
- Broad searches for `WI-3436 backlog update CLI`, `DELIB-2546 gt backlog update WI-3436`, `bridge verified backlog reconciler related_bridge_threads DELIB-S345`, and `deterministic services principle backlog update CLI` returned `[]`; exact `get` lookups above provided the relevant DA records.

## Findings

### P1-001 - GOV-15 can be bypassed by status-only resolution

Observation:

The proposal claims the CLI preserves GOV-15 by threading `--owner-approved` to `KnowledgeDB.update_work_item(owner_approved=...)` and tests that resolving defect/regression work items without the flag fails. It also exposes `--resolution-status` and `--stage` as independent options, and defines `resolve` as a convenience wrapper that supplies both `--resolution-status resolved` and `--stage resolved`.

Evidence:

- Proposal claim: `bridge/gtkb-backlog-update-cli-slice-1-001.md:35` says `KnowledgeDB.update_work_item()` already enforces GOV-15 via `owner_approved`.
- Proposal options: `bridge/gtkb-backlog-update-cli-slice-1-001.md:95` exposes independent `--resolution-status`, `--stage`, and `--owner-approved`.
- Proposal test: `bridge/gtkb-backlog-update-cli-slice-1-001.md:110` says defect/regression resolution without `--owner-approved` must fail.
- Proposal risk mitigation: `bridge/gtkb-backlog-update-cli-slice-1-001.md:130` says threading `owner_approved` to `update_work_item()` is sufficient.
- Current DB implementation: `groundtruth-kb/src/groundtruth_kb/db.py:3351` returns from `_validate_stage_transition(...)` when `new_stage == current_stage`; `groundtruth-kb/src/groundtruth_kb/db.py:3374` runs GOV-15 only when `new_stage == "resolved"`.
- Current DB update path: `groundtruth-kb/src/groundtruth_kb/db.py:3567` reads `resolution_status` independently from fields, and `groundtruth-kb/src/groundtruth_kb/db.py:3569`/`:3570` default `new_stage` to the current stage when no stage field is supplied.
- Current gate implementation: `groundtruth-kb/src/groundtruth_kb/gates.py:90` documents the owner-approval gate for defect/regression resolution, and `groundtruth-kb/src/groundtruth_kb/gates.py:98`-`:103` blocks only when the gate is invoked with `resolution == "resolved"`.

Probe command and observed result:

```powershell
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'
@'
from pathlib import Path
import tempfile
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry
base = Path(r'E:\GT-KB\.gtkb-state\tmp')
base.mkdir(parents=True, exist_ok=True)
p = Path(tempfile.mkdtemp(dir=str(base))) / 'gate_probe.db'
registry = GateRegistry.from_config([], include_builtins=True)
db = KnowledgeDB(db_path=p, gate_registry=registry)
db.insert_work_item(
    id='WI-PROBE-001', title='probe', origin='defect', component='test',
    resolution_status='open', stage='created', changed_by='probe', change_reason='seed'
)
try:
    db.update_work_item(
        'WI-PROBE-001', changed_by='probe', change_reason='resolve status only',
        resolution_status='resolved', owner_approved=False
    )
except Exception as exc:
    print(type(exc).__name__, str(exc))
else:
    row = db.get_work_item('WI-PROBE-001')
    print('NO_EXCEPTION', row['resolution_status'], row['stage'], row['version'])
finally:
    db.close()
'@ | groundtruth-kb\.venv\Scripts\python.exe -u -
```

Observed:

```text
NO_EXCEPTION resolved created 2
```

Deficiency rationale:

GOV-15 is a defect/regression resolution gate, not merely a stage-transition gate. The proposed CLI would become a governed mutation surface for work-item lifecycle fields, so it must not allow a user to set `--resolution-status resolved` on a defect/regression row without owner approval just because `--stage resolved` was omitted. If Prime implements the proposal as written, T6 can pass through the `resolve` convenience wrapper while the lower-level `update` command still bypasses the rule.

Impact:

The new command would provide a first-class, governed-looking path that can close defect/regression work items without the explicit owner approval GOV-15 requires. That is a governance regression in the exact surface this proposal is trying to harden.

Recommended action:

Revise the proposal and test plan to require one of these fail-closed designs:

1. When `--resolution-status resolved` is supplied, the CLI must either require `--stage resolved` or internally treat the operation as a resolution transition and invoke the same owner-approval check before any write.
2. Add a specific test for `gt backlog update WI-X --resolution-status resolved --change-reason ...` on a defect/regression work item without `--owner-approved`, with no `--stage` argument. Expected: non-zero exit and no new row.
3. Add the positive counterpart with `--owner-approved` and explicit or derived `stage=resolved`, proving both `resolution_status` and `stage` end in a coherent terminal state.

Option rationale:

The minimal fix is to bind terminal `resolution_status` semantics to the same approval gate that currently sits behind `stage="resolved"`. This preserves the proposal's intended API reuse while preventing a status/stage split from becoming a policy bypass. A broader DB-layer change may also be reasonable later, but this bridge proposal can be corrected by making the CLI fail closed and expanding T6.

## Confirmed Non-Blocking Checks

- Live `bridge/INDEX.md` still had latest `NEW: bridge/gtkb-backlog-update-cli-slice-1-001.md` before this verdict was written.
- Durable role resolution: `harness-state/harness-identities.json` maps Codex to harness ID `A`; `harness-state/role-assignments.json` maps `A` to `loyal-opposition`.
- Project authorization exists and is active: `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` returned `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-CLI-WI-3436` with `included_work_item_ids=["WI-3436"]`, `included_spec_ids=["GOV-STANDING-BACKLOG-001", "GOV-08"]`, and `allowed_mutation_classes=["cli_extension", "test_addition"]`.
- Work item exists and is in scope: `gt backlog show WI-3436 --json` returned `origin="improvement"`, `resolution_status="open"`, `stage="backlogged"`, component `cli`, and the expected title.

## Applicability Preflight

- packet_hash: `sha256:9902ff162c95f5c9d6f447b75ce74e908e26ff29ffa3531b4d29c66332c9589b`
- bridge_document_name: `gtkb-backlog-update-cli-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-update-cli-slice-1-001.md`
- operative_file: `bridge/gtkb-backlog-update-cli-slice-1-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-backlog-update-cli-slice-1`
- Operative file: `bridge\gtkb-backlog-update-cli-slice-1-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Implementation Context For Prime Builder

Revision scope:

- Update the proposal's Implementation Plan, Risk / Rollback, and Spec-Derived Verification Plan.
- Keep `target_paths` unchanged unless the correction requires a DB-layer helper or shared status vocabulary update. If adding DB-layer enforcement, add the changed DB file and corresponding tests to `target_paths`.
- Preserve the existing PAUTH and WI scope; no new owner decision is needed for this NO-GO unless Prime changes the mutation classes or target paths materially.

Minimum acceptance for REVISED:

- Explicitly state how `gt backlog update --resolution-status resolved` handles GOV-15 when `--stage` is omitted.
- Include the status-only defect/regression negative test described above.
- Include the positive owner-approved terminal update test and require coherent terminal state (`resolution_status="resolved"` and `stage="resolved"` or a documented, governed alternative).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
