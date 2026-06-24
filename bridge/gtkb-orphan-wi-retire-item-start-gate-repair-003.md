NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef3c1-ca61-7e01-aabd-9747922b391a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop auto-builder Prime Builder run; approval_policy=never; workspace=E:\GT-KB
author_metadata_source: automation prompt plus bridge work-intent claim

# GT-KB Bridge Implementation Report - gtkb-orphan-wi-retire-item-start-gate-repair - 003

bridge_kind: implementation_report
Document: gtkb-orphan-wi-retire-item-start-gate-repair
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-orphan-wi-retire-item-start-gate-repair-002.md
Approved proposal: bridge/gtkb-orphan-wi-retire-item-start-gate-repair-001.md
Recommended commit type: feat

## Implementation Claim

Implemented the approved three-file service/CLI/test slice for governed per-work-item retire/exclude handling.

- Added `ProjectLifecycleService.retire_project_work_item()` in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`.
- Added `gt projects retire-item` in `groundtruth-kb/src/groundtruth_kb/cli.py`.
- Added focused CLI regression coverage in `platform_tests/scripts/test_projects_cli.py`.

The new service appends a non-active project membership version only after `change_reason` cites an in-root `.groundtruth/formal-artifact-approvals/*.json` packet that validates through the shared formal approval packet validator, is owner-approved, and covers the exact `project_id`, `work_item_id`, derived lifecycle action (`retire` or `exclude`), and requested non-active status. Mismatched, missing, malformed, schema-invalid, non-owner, or out-of-root packet evidence fails closed before mutation.

No deferred-action drain, data-migration execution, `groundtruth.db` mutation, or `scripts/resolve_orphan_wi_memberships.py` edit was performed.

## Implementation-Start Authorization

- Command: `python scripts\bridge_claim_cli.py claim gtkb-orphan-wi-retire-item-start-gate-repair`
- Result: acquired `go_implementation` claim for `PROJECT-GTKB-RELIABILITY-FIXES`, `WI-3464`; `ttl_expires_at=2026-06-23T10:45:22Z`.
- Command: `python scripts\implementation_authorization.py begin --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair`
- Result: authorized; `latest_status=GO`; `requirement_sufficiency=sufficient`; `packet_hash=sha256:98f1334d5a8a72b3e27be3a83c31df6f2c46eb5592514444b2c9c4c02cc7a8fb`.
- Authorized target paths:
  - `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
  - `groundtruth-kb/src/groundtruth_kb/cli.py`
  - `platform_tests/scripts/test_projects_cli.py`

## Commit

- `ef45ce5e4 feat: add governed project retire-item command`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Owner Decisions / Input

No new owner decision was required. This implementation used the active project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23`, backed by `DELIB-20265586`, and remained inside the approved bridge target paths.

Runtime use of `gt projects retire-item` still requires separate owner-approval-packet evidence for each concrete project/work-item/status transition.

## Prior Deliberations

- `DELIB-2509` - owner AUQ answer selecting per-WI PAUTH plus assign-only scope for the parent orphan-WI backfill driver.
- `DELIB-20260745` - append-only non-active membership precedent from `gt projects remove-item`.
- `DELIB-20265542` - prior NO-GO requiring exact approval-packet binding and excluding deferred-action drain from this slice.
- `DELIB-20265586` - bounded implementation authorization for this project/WI set.
- `bridge/gtkb-orphan-wi-retire-item-start-gate-repair-001.md` - approved implementation proposal.
- `bridge/gtkb-orphan-wi-retire-item-start-gate-repair-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / obligation | Executed verification evidence |
| --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` - governed lifecycle mutation needs valid owner approval evidence | `python -m pytest platform_tests/scripts/test_projects_cli.py -q --tb=short`: `14 passed`. Positive test proves exact matching packet appends the non-active membership version and removes the WI from active project membership lookup. |
| `GOV-ARTIFACT-APPROVAL-001` - approval evidence must bind to this requested mutation | Same pytest run: mismatch tests reject another project, another work item, wrong action, and wrong status without mutation. |
| `GOV-ARTIFACT-APPROVAL-001` - missing or unsafe packet evidence fails closed | Same pytest run: missing packet reference, malformed JSON, schema-invalid packet, and out-of-root packet path all fail without mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - append-only non-active lifecycle state | Same pytest run: idempotency/status test preserves prior active version, rejects duplicate retire with no active membership, and rejects empty/`active`/`removed` statuses. |
| `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision provenance is preserved | Same pytest run: change-reason provenance test verifies the appended membership version stores the approval-packet-bearing `change_reason`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair`: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair`: exit 0, `Blocking gaps (gate-failing): 0`. |
| Proposal scope discipline | `git diff --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db` returned only the three approved source/test paths before commit. |

## Commands Run

```text
python -m pytest platform_tests/scripts/test_projects_cli.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair
git diff --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
git commit --only groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py -m "feat: add governed project retire-item command"
```

## Observed Results

```text
python -m pytest platform_tests/scripts/test_projects_cli.py -q --tb=short
14 passed in 21.16s
```

```text
python -m ruff check ...
All checks passed!
```

```text
python -m ruff format --check ...
3 files already formatted
```

```text
bridge_applicability_preflight
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

```text
adr_dcl_clause_preflight
Blocking gaps (gate-failing): 0
```

```text
scoped diff inspection before commit
groundtruth-kb/src/groundtruth_kb/cli.py
groundtruth-kb/src/groundtruth_kb/project/lifecycle.py
platform_tests/scripts/test_projects_cli.py
```

```text
commit
[develop ef45ce5e4] feat: add governed project retire-item command
 3 files changed, 462 insertions(+)
```

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_projects_cli.py`

## Acceptance Criteria Status

- [x] Implementation-start gate authorized this operative proposal after GO and active Prime work-intent claim.
- [x] `ProjectLifecycleService.retire_project_work_item()` exists and refuses mutation unless `change_reason` cites an in-root valid owner-approval packet that binds to the exact project, work item, lifecycle action, and requested non-active status.
- [x] `gt projects retire-item` exposes `project_id`, `work_item_id`, `--status` defaulting to `retired`, `--changed-by`, required `--change-reason`, and `--json`.
- [x] Valid execution appends an audit-preserving non-active membership version and keeps the prior active version for history.
- [x] Mismatched, missing, malformed, schema-invalid, and out-of-root packets fail closed without membership mutation.
- [x] No canonical live drain of `deferred_actions.json`, no `groundtruth.db` mutation, and no edit to `scripts/resolve_orphan_wi_memberships.py` occurred.
- [x] Focused CLI tests, ruff check, and ruff format check passed on the approved target set.

## Residual Scope Note

`WI-3464` remains broader than this verified slice. Deferred-action drain/data-migration work is still excluded and needs separate bridge authorization before implementation.

## Risk And Rollback

Risk is limited to the new CLI/service surface and tests. Rollback is path-local: revert commit `ef45ce5e4`, which touches only the three approved files. No live data migration or database mutation was performed by this implementation.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
