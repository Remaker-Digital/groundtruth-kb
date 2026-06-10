VERIFIED

# Loyal Opposition Verification - First-Class Project Artifacts Revision

bridge_kind: lo_verdict
Document: gtkb-first-class-project-artifacts
Version: 009
Reviewer: Codex (harness A, Loyal Opposition dispatch mode)
Date: 2026-05-13 UTC
Reviewed file: `bridge/gtkb-first-class-project-artifacts-008.md`
Prior NO-GO: `bridge/gtkb-first-class-project-artifacts-007.md`
Verdict: VERIFIED

## Claim

The revised implementation report is verified. The prior formatter blocker
from `-007` is resolved in the live worktree, and the implementation remains a
project layer over canonical `work_items` / `current_work_items` without
introducing `backlog_items`, `backlog_entries`, a wrapper backlog queue, or a
`subjects` table.

## Role Authority

- `harness-state/harness-identities.json` maps Codex to durable harness ID `A`.
- `harness-state/role-assignments.json` assigns harness `A` both
  `loyal-opposition` and `prime-builder`.
- This dispatch carried mode `lo`, so only live latest `NEW` / `REVISED`
  bridge entries were actionable.
- Live `bridge/INDEX.md` listed
  `bridge/gtkb-first-class-project-artifacts-008.md` as the latest `REVISED`
  entry before this verdict.

## Prior Deliberations

Deliberation search was run before review:

```text
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "first class project artifacts current_work_items project membership backlog authority" --limit 8
```

Relevant surfaced records included
`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-1791`,
`DELIB-0183`, `DELIB-0838`, `DELIB-0835`, `DELIB-0874`,
`DELIB-0839`, and `DELIB-1466`. The controlling constraint remains that
project artifacts extend current `work_items` / `current_work_items` backlog
authority unless a separate owner-approved supersession is proposed.

## Applicability Preflight

- packet_hash: `sha256:713178c8f7e85184cf56f5bef22f0dbe2177e0cc5f53dd99c782b928c6a78da4`
- bridge_document_name: `gtkb-first-class-project-artifacts`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-first-class-project-artifacts-008.md`
- operative_file: `bridge/gtkb-first-class-project-artifacts-008.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-first-class-project-artifacts`
- Operative file: `bridge\gtkb-first-class-project-artifacts-008.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Verification Evidence

Commands executed:

```text
python -m pytest groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_operating_state.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py
```

Observed results:

- Project-artifact test lane: `52 passed, 1 warning`.
- Exact changed-file ruff check: `All checks passed!`.
- Exact changed-file ruff format check: `3 files already formatted`.

Source inspection confirmed the implementation has project, membership,
dependency, artifact-link tables and current views in
`groundtruth-kb/src/groundtruth_kb/db.py`; read-only project CLI surfaces in
`groundtruth-kb/src/groundtruth_kb/cli.py`; and tests asserting
`work_items` / `current_work_items` remain authoritative while
`backlog_items`, `backlog_entries`, and `subjects` are absent.

## Findings

No blocking findings. The implementation satisfies the approved first-class
project artifact scope, and the `-007` formatter blocker is closed.

File bridge scan: 2 entries processed in this dispatch.
