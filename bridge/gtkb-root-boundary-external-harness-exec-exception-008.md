VERIFIED

bridge_kind: verification_verdict
Document: gtkb-root-boundary-external-harness-exec-exception
Version: 008
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-root-boundary-external-harness-exec-exception-007.md
Recommended commit type: feat:

# Loyal Opposition Verification - External Harness Executable Root-Boundary Exception

## Verdict

VERIFIED. The post-implementation report at `bridge/gtkb-root-boundary-external-harness-exec-exception-007.md` carries forward the approved proposal scope, includes substantive owner-decision evidence, includes spec-to-test mapping for the linked requirements, and its target verification commands pass under the repo venv. The full project doctor command still reports unrelated existing baseline failures, but the implemented external-harness-bound check is registered and reports OK; those unrelated baseline failures are not regressions in this bridge scope.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:6f80ff8a7e820fce68891a4afa97b4c9d73887200b72b40afb3ce4ef78dcbc8d`
- bridge_document_name: `gtkb-root-boundary-external-harness-exec-exception`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-root-boundary-external-harness-exec-exception-007.md`
- operative_file: `bridge/gtkb-root-boundary-external-harness-exec-exception-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-root-boundary-external-harness-exec-exception`
- Operative file: `bridge\gtkb-root-boundary-external-harness-exec-exception-007.md`
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

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`: owner decision authorizing the bounded exception.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-006.md`: Loyal Opposition GO for the final revised proposal.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`: revised implementation proposal and approval-packet plan.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-004.md`: prior NO-GO findings closed by the revised proposal.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-002.md`: initial NO-GO finding closed by the revised proposal.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` and `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md`: prior root-boundary conflict that motivated this governance amendment.
- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` and `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`: related decision context cited by Prime Builder.

`gt` was not available on PATH in this Codex shell, so the deliberation search requirement was satisfied by the thread's cited DELIB records and full version-chain review.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `config/governance/narrative-artifact-approval.toml`
- `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `REQ-HARNESS-REGISTRY-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `GOV-20`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---:|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full thread read via `show_thread_bridge.py`; this verdict updates `bridge/INDEX.md` | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect `.claude/rules/project-root-boundary.md` External Harness Executable Resolution Exception section | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_external_harness_exec_boundary.py -v` using the repo venv and workspace temp | yes | PASS, 4 passed |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Inspect report header Project / Work Item / Project Authorization metadata | yes | PASS |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | `python scripts/check_narrative_artifact_evidence.py --staged` using the repo venv | yes | PASS |
| `config/governance/narrative-artifact-approval.toml` and `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` | Inspect `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json` | yes | PASS |
| `GOV-ENV-LOCAL-AUTHORITY-001`, `REQ-HARNESS-REGISTRY-001`, `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `GOV-20` | `python -m groundtruth_kb project doctor 2>&1 | Select-String -Pattern 'External harness|cross-harness exec'` using the repo venv | yes | PASS for the implemented check |
| `SPEC-AUQ-POLICY-ENGINE-001` | Inspect `Owner Decisions / Input` and approval packet fields `approved_by`, `presented_to_user`, `transcript_captured` | yes | PASS |

## Positive Confirmations

- The latest bridge state was `NEW` on a post-GO implementation report, so verification was the correct Loyal Opposition action.
- The applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- The clause preflight passed with zero must-apply evidence gaps and zero blocking gaps.
- The bounded root-boundary exception is present in `.claude/rules/project-root-boundary.md` and preserves the root-contained project-artifact invariant.
- `_check_external_harness_exec_boundary` is implemented in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and registered in the doctor check sequence.
- The spec-derived test file contains all four required cases: registry-enumerated PASS, non-harness literal FAIL, missing-registry WARN, and deterministic/read-only behavior.
- The approval packet exists at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`, records `approval_mode: approve`, `approved_by: owner`, `presented_to_user: true`, and `transcript_captured: true`.
- `Recommended commit type: feat:` is appropriate for a net-new governance exception, doctor check, and spec-derived tests.

## Commands Executed

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-root-boundary-external-harness-exec-exception --format json --preview-lines 1000
```

Result: full version chain loaded, no thread drift reported.

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
```

Result: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
```

Result: zero evidence gaps in must-apply clauses; zero blocking gaps; exit 0.

```powershell
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m pytest platform_tests/scripts/test_external_harness_exec_boundary.py -v
```

Initial result: blocked by default temp path permissions under `C:\Users\micha\AppData\Local\Temp\pytest-of-micha`; not an implementation failure.

```powershell
$env:TEMP='E:\GT-KB\.pytest-tmp'; $env:TMP='E:\GT-KB\.pytest-tmp'; & 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m pytest platform_tests/scripts/test_external_harness_exec_boundary.py -v
```

Result: 4 passed, 1 cache warning.

```powershell
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_external_harness_exec_boundary.py
```

Result: All checks passed.

```powershell
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts/check_narrative_artifact_evidence.py --staged
```

Result: `PASS narrative-artifact evidence (1 cleared)`.

```powershell
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' -m groundtruth_kb project doctor
```

Result: overall command reports pre-existing unrelated project doctor failures, but the implemented check reports:

```text
[OK]  cross-harness exec resolution bounded to registry-enumerated harness commands (3 enumerated: ['claude', 'codex', 'gemini']); no literal non-harness commands in scanned surface(s)
```

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
