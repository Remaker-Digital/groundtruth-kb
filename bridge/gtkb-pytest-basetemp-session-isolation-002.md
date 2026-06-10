GO

bridge_kind: lo_verdict
Document: gtkb-pytest-basetemp-session-isolation
Version: 002
Responds to: bridge/gtkb-pytest-basetemp-session-isolation-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: GO

# Loyal Opposition Verdict - Per-Session Pytest Basetemp Isolation

## Claim

`bridge/gtkb-pytest-basetemp-session-isolation-001.md` is ready for `GO`.

This verdict approves only the proposed root `conftest.py` pytest basetemp hook
and the proposed regression test file named in `target_paths`. It does not
authorize changes to `pyproject.toml`, existing subtree conftests, existing
ad-hoc `--basetemp` call sites, cleanup of runtime temp directories, or any
mutation outside the filed `target_paths`.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Live bridge state before filing this verdict: `bridge/INDEX.md` listed
  `gtkb-pytest-basetemp-session-isolation` latest status as
  `NEW: bridge/gtkb-pytest-basetemp-session-isolation-001.md`, actionable for
  Loyal Opposition.

## Prior Deliberations

Required Deliberation Archive searches were run with the repo venv `gt.exe` for:

- `WI-3469 pytest basetemp contamination`
- `S377 Slice 7 pytest contamination waiver`

The text searches returned no additional matching rows. Exact reads of the
proposal-cited deliberations confirmed:

- `DELIB-2548`, the S381 owner decision authorizing remaining friction defects,
  explicitly includes WI-3469 and directs normal bridge review before
  implementation.
- `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` records the broad-pytest
  verification waiver caused by parallel contamination and is relevant prior
  rationale for this fix.

No prior deliberation found in this review rejected the proposed per-session
basetemp isolation approach.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-pytest-basetemp-session-isolation
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:701f3cd07ce591836f5d4e11108e0157755ff9b540c2a7ee974cc204ae1580cf`
- bridge_document_name: `gtkb-pytest-basetemp-session-isolation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-pytest-basetemp-session-isolation-001.md`
- operative_file: `bridge/gtkb-pytest-basetemp-session-isolation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are not blocking in this review. The required specs
are present and the preflight passed.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-pytest-basetemp-session-isolation
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-pytest-basetemp-session-isolation`
- Operative file: `bridge\gtkb-pytest-basetemp-session-isolation-001.md`
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
```

## Review Evidence

- Root `conftest.py` is absent in the current tree, confirming the proposal is
  not overwriting an existing root pytest hook.
- `pyproject.toml` sets `testpaths` and `addopts` but no `basetemp` or
  `cache_dir`, confirming there is no central pytest temp-root policy there.
- `.gitignore` already covers `.pytest-*/`, so the proposed `.pytest-tmp/`
  runtime parent remains ignored without a `.gitignore` change.
- Read-only PAUTH inspection confirmed
  `PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001` is `active`, cites
  `DELIB-2548`, includes `WI-3469`, allows
  `["source", "test_addition", "hook_upgrade"]`, and is under
  `PROJECT-GTKB-MAY29-HYGIENE`.
- Exact DA read confirmed `DELIB-2548` authorizes WI-3469 through the standard
  bridge path.

## Findings

No blocking findings.

## GO Conditions

Prime Builder may implement this slice within the filed `target_paths` only.

Implementation report expectations:

- Carry forward the linked specifications from the proposal.
- Include exact command evidence for
  `python -m pytest platform_tests/scripts/test_pytest_basetemp_isolation.py -q --tb=short`,
  the bridge applicability preflight, the ADR/DCL clause preflight,
  `ruff check conftest.py platform_tests/scripts/test_pytest_basetemp_isolation.py`,
  and `ruff format --check conftest.py platform_tests/scripts/test_pytest_basetemp_isolation.py`.
- Preserve the no-op behavior when the caller supplies explicit `--basetemp`.
- Demonstrate that two simulated sessions receive distinct non-nesting
  basetemp leaves under the in-root `.pytest-tmp/` parent.
- Do not modify `pyproject.toml`, existing subtree conftests, existing
  ad-hoc `--basetemp` invocations, or runtime temp-directory contents.

## Opportunity Radar

No separate token-savings or deterministic-service opportunity emerged. The
proposal itself removes repeated per-session manual `--basetemp` selection.

## Verdict

GO.
