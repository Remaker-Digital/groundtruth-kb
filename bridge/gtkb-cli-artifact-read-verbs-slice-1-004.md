VERIFIED
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: codex-keep-working-lo-2026-06-19T00-54Z
author_model: GPT-5
author_model_version: 2026-06-19
author_model_configuration: Codex desktop automation; PowerShell; approval_policy_never

# Loyal Opposition Verification - gtkb-cli-artifact-read-verbs-slice-1 - 004

bridge_kind: verification_verdict
Document: gtkb-cli-artifact-read-verbs-slice-1
Version: 004 (VERIFIED)
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-19T00:54:22Z
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-cli-artifact-read-verbs-slice-1-003.md
Recommended commit type: feat:

## Claim

VERIFIED. Prime Builder implemented the approved first slice of deterministic
CLI artifact read verbs as an additive, read-only command-surface change. The
new `gt spec`, `gt projects`, `gt deliberations`, and `gt tests` read verbs are
covered by focused CLI tests against temporary MemBase databases, and the
existing compatibility surface remains intact.

No owner action is required.

## Applicability Preflight

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-cli-artifact-read-verbs-slice-1

preflight_passed: true
packet_hash: sha256:89188c834445bbe90829fee4136f903592627df34cc517e4adaad931e0ad8edd
missing_required_specs: []
missing_advisory_specs: []
```

## Clause Applicability

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-cli-artifact-read-verbs-slice-1

must_apply: 3
may_apply: 2
blocking_gaps: 0
```

## Prior Deliberations

- `WI-4635` is the governed backlog authority for this CLI read-surface slice.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports moving repetitive
  artifact inspection from agent judgment into deterministic CLI services.
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` and
  `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` provide
  the project authorization cited by the proposal and implementation report.
- `bridge/gtkb-cli-artifact-read-verbs-slice-1-001.md` is the approved
  proposal.
- `bridge/gtkb-cli-artifact-read-verbs-slice-1-002.md` is the GO verdict.

## Specifications Carried Forward

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-to-Test Mapping

| Specification / governing surface | Verification evidence | Result |
| --- | --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation report cites packet hash `sha256:7c582631ca5df2f14bd8aeafeecc1202d7f42a5c126c331e6fbf8eaabe63ad97`; preflights pass against the report. | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Live `WI-4635` readback shows open May29 Hygiene backlog authority for the CLI read verbs. | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This verdict is the next numbered bridge response to `-003`. | PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and report carry Project Authorization, Project, and Work Item metadata. | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and clause preflights pass with no missing required specs or blocking gaps. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-ran focused pytest for the new CLI verbs and compatibility assertions. | PASS: 4 passed |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Tests seed specs, deliberations, project authorizations, and tests, then read them through CLI commands. | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | New commands expose current/history/list read surfaces without creating artifact versions. | PASS |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001`; `SPEC-AUQ-POLICY-ENGINE-001` | Source inspection confirms deterministic Click wrappers over `KnowledgeDB` read methods, not LLM classification. | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Touched source/test/bridge paths remain under `E:\GT-KB`. | PASS |

## Positive Confirmations

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cli_artifact_read_verbs.py platform_tests\scripts\test_project_authorization.py -q --tb=short -o addopts=`
  passed with `4 passed, 2 warnings in 51.61s`.
- The warnings were the existing unknown `asyncio_mode` pytest configuration
  warning and a ChromaDB Python 3.16 deprecation warning.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_cli_artifact_read_verbs.py platform_tests\scripts\test_project_authorization.py`
  reported `All checks passed!`.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_cli_artifact_read_verbs.py platform_tests\scripts\test_project_authorization.py`
  reported `3 files already formatted`.
- Source inspection found the expected additive command surfaces:
  - `gt spec show`
  - `gt spec list`
  - `gt projects show-authorization`
  - `gt deliberations show`
  - `gt tests show`
  - `gt tests list`
- Focused tests assert the deliberation `show` alias matches `get`, and that
  spec/test/project-authorization readbacks return JSON-shaped deterministic
  payloads.

## Findings

No blocking findings.

The implementation touches the large shared CLI module, so the residual risk
is ordinary command-surface regression risk. The change is additive and
covered by focused tests plus existing project-authorization regression
coverage, which is sufficient for this slice.

## Commands Executed

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-cli-artifact-read-verbs-slice-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-cli-artifact-read-verbs-slice-1
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cli_artifact_read_verbs.py platform_tests\scripts\test_project_authorization.py -q --tb=short -o addopts=
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_cli_artifact_read_verbs.py platform_tests\scripts\test_project_authorization.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_cli_artifact_read_verbs.py platform_tests\scripts\test_project_authorization.py
rg -n "def .*spec|show_authorization|tests|deliberations" groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_cli_artifact_read_verbs.py platform_tests\scripts\test_project_authorization.py
python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); r=db.get_work_item('WI-4635'); print(r.get('id'), r.get('resolution_status'), r.get('stage'), r.get('priority'), r.get('project_name'), r.get('title'))"
```

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
