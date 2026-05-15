VERIFIED

# Loyal Opposition Verification - Project Authorize Spec-Linkage Gate

Document: gtkb-project-authorize-spec-linkage-gate
Version: 008
Responds to: bridge/gtkb-project-authorize-spec-linkage-gate-007.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Work Item: WI-3312

## Verdict

VERIFIED.

The implementation report carries forward the linked specifications, maps the
source governance requirement to executable tests, and the current code/test
state satisfies the GO conditions from `bridge/gtkb-project-authorize-spec-linkage-gate-006.md`.
The active project authorization gate now requires at least one cited MemBase
specification row with lifecycle status in `{specified, implemented, verified}`,
and no replacement `type` allowlist was introduced.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW`, actionable for Loyal Opposition.
- Read the full bridge thread from `-001` through `-007`.
- Skipped selected `gtkb-core-spec-intake-default` because live `bridge/INDEX.md` already had latest status `NO-GO`, not `NEW`.
- Reviewed the implementation report at `bridge/gtkb-project-authorize-spec-linkage-gate-007.md`.
- Inspected current implementation in:
  - `groundtruth-kb/src/groundtruth_kb/db.py`
  - `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
  - `groundtruth-kb/src/groundtruth_kb/cli.py`
  - `groundtruth-kb/tests/test_db.py`
  - `groundtruth-kb/tests/test_cli_projects.py`
- Ran mandatory bridge preflights, Deliberation Archive search, targeted pytest, targeted ruff check, and a spec-status check.

## Prior Deliberations

Deliberation Archive search was run before verification:

```text
python -c "from groundtruth_kb.cli import main; main()" deliberations search "WI-3312 project authorize spec linkage gate ProjectAuthorizationSpecLinkageError GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS" --limit 8 --json
```

Relevant results:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive establishing the spec -> project -> work item -> bridge enforcement chain and authorizing this project scope.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - later owner direction to keep parallelizing remaining P0/P1 work; contextual, not conflicting.
- Prior bridge evidence in this thread: `bridge/gtkb-project-authorize-spec-linkage-gate-002.md`, `-004.md`, and `-006.md`.

No prior deliberation found that contradicts the approved predicate of
MemBase specifications-table membership plus lifecycle status.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:0fbf1c377f1dfaee9ef1edd43b531d4a576151c6207580152adfa7ed8d592b2d`
- bridge_document_name: `gtkb-project-authorize-spec-linkage-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-authorize-spec-linkage-gate-007.md`
- operative_file: `bridge/gtkb-project-authorize-spec-linkage-gate-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

No required specification omissions were reported.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-project-authorize-spec-linkage-gate`
- Operative file: `bridge\gtkb-project-authorize-spec-linkage-gate-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

No blocking clause gaps were reported.

## Verification Evidence

### Claim: active project authorization validation is implemented at the DB layer

Evidence:

- `groundtruth-kb/src/groundtruth_kb/db.py:3938` defines `_validate_active_authorization_specs()`.
- `groundtruth-kb/src/groundtruth_kb/db.py:3950` uses `{"specified", "implemented", "verified"}` as the approved lifecycle set.
- `groundtruth-kb/src/groundtruth_kb/db.py:3959-3966` resolves each candidate through `self.get_spec(spec_id)` and increments `resolved` for any row with approved status.
- `groundtruth-kb/src/groundtruth_kb/db.py:4005-4006` calls the validator when `status == "active"`.
- `groundtruth-kb/src/groundtruth_kb/db.py:4078-4152` shows `update_project_authorization()` delegates to `insert_project_authorization()` and carries `included_spec_ids` through.

Result: PASS. The implementation matches IP-1 and GO Condition 1. No `type`
allowlist was introduced.

### Claim: service and CLI expose the linkage failure as a usage error

Evidence:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:19-26` defines `ProjectAuthorizationSpecLinkageError(ProjectLifecycleError)`.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:314-321` re-raises linkage-specific `ValueError`s as the typed subclass when the source spec ID is present.
- `groundtruth-kb/src/groundtruth_kb/cli.py:37-42` imports the typed subclass.
- `groundtruth-kb/src/groundtruth_kb/cli.py:908-910` maps `ProjectAuthorizationSpecLinkageError` to `click.UsageError`; generic `ProjectLifecycleError` still maps to `click.ClickException` at `cli.py:911-912`.

Result: PASS. The implementation matches IP-2 and GO Condition 2.

### Claim: specification-derived test coverage exists and passes

Evidence:

- `bridge/gtkb-project-authorize-spec-linkage-gate-007.md:71-99` carries the spec-to-test mapping and reported 76 passing tests.
- `groundtruth-kb/tests/test_db.py:991-1125` defines the 11 DB-layer tests covering missing, empty, unknown, retired, positive heterogeneous `type` values, valid/invalid mix, draft, non-active version, and grandfathered read behavior.
- `groundtruth-kb/tests/test_cli_projects.py:60-71` covers the CLI usage-error path and source-spec citation.

Reviewer rerun:

```text
python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py -v
```

Observed result: `76 passed, 1 warning in 19.50s`.

The 13 WI-3312 tests all passed, including:

- `test_authorize_active_with_specification_type_spec_succeeds`
- `test_authorize_active_with_requirement_type_spec_succeeds`
- `test_authorize_active_with_governance_type_spec_succeeds`
- `test_cli_authorize_missing_specs_emits_usage_error`
- `test_cli_error_cites_source_spec`

Result: PASS. This satisfies the mandatory specification-derived verification
gate and GO Conditions 3 and 5. The implementation report used `-q`; the
reviewer reran the exact `-v` command from the GO conditions and observed the
same 76-test pass set.

### Claim: source spec was not promoted prematurely

Command:

```text
python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); row=db.get_spec('GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001'); print(row.get('id'), row.get('status'), row.get('type'), row.get('version'))"
```

Observed result:

```text
GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 specified governance 1
```

Result: PASS. `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains
`specified`, satisfying IP-4 and GO Condition 4.

## Additional Checks

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py
```

Observed result: `All checks passed!`

Non-blocking formatter note:

```text
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py
```

Observed result: `Would reformat` three files (`cli.py`, `test_db.py`,
`test_cli_projects.py`). This is not treated as a verification blocker for this
thread because the linked requirements and GO conditions do not make formatter
cleanliness an acceptance gate, and the current GroundTruth KB workflow check
reviewed during this verification does not enforce `ruff format --check` for
these package targets. Prime should still format before committing to reduce
future churn.

## Findings

No blocking findings.

## Decision

VERIFIED.

File bridge scan: 1 entry processed. One selected stale entry
(`gtkb-core-spec-intake-default`) was skipped because its live latest status was
already `NO-GO`.
