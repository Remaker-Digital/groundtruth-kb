GO

# gtkb-wi4678-pytest-timeout-addopts-dependency — restore pytest-timeout support for default addopts — GO

bridge_kind: lo_verdict
Document: gtkb-wi4678-pytest-timeout-addopts-dependency
Verdict: GO
Version: 002
Author: Loyal Opposition (OpenRouter, harness F)
Date: 2026-06-19T08:42:00Z

author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

References:
- Proposal: bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-001.md (NEW, Codex/Harness A)
- Project: PROJECT-GTKB-MAY29-HYGIENE
- PAUTH: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
- WI: WI-4678

---

## Verdict Summary

**GO.** The proposal identifies a genuine test-infrastructure defect: the repository root `pyproject.toml` configures pytest with `--timeout=30` via default addopts, but the GroundTruth-KB managed dependency surface lacks `pytest-timeout`, causing the recommendation `groundtruth-kb/.venv/Scripts/python.exe -m pytest ...` to reject the timeout option. The fix is narrowly scoped — add `pytest-timeout` to the GroundTruth-KB dev extra and lockfile, plus a structural regression test — and properly treats the recurring `-o addopts=""` workaround as historical symptom evidence, not as the fix.

## Bridge Finding

The proposal meets all blocking requirements:

1. **Defect substantiated.** Live LO verification of WI-4672 and WI-4677 recorded the `--timeout=30` rejection in bridge evidence (bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-003.md and bridge/gtkb-wi4677-backlog-json-option-validation-003.md). The root `pyproject.toml` addopts include `--timeout=30` but `groundtruth-kb/pyproject.toml` dev dependencies do not declare `pytest-timeout`. Historical bridge evidence (bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-005.md) confirms this is a recurring workaround pattern, not an isolated incident.

2. **Scope is bounded.** Four target paths: `pyproject.toml` (root — for comment/annotation only since the timeout policy stays intact), `groundtruth-kb/pyproject.toml` (add `pytest-timeout` to dev extra), `groundtruth-kb/uv.lock` (lockfile update), and `platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py` (new structural regression test). No schema migration, no KB mutation, no broader dependency rework.

3. **Authorization is active.** `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` covers WI-4678 as an unimplemented May29 Hygiene work item. `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` provides owner authorization for implementing through the normal bridge/GO process.

4. **Spec linkage is concrete.** All blocking specs cited and preflight-verified: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

5. **The fix is the right one.** The proposal correctly distinguishes between the symptom (per-command `-o addopts=""`) and the root cause (missing dependency). Adding `pytest-timeout` to the managed dependency surface restores the contract that the root addopts already assume. The structural regression test proves the contract holds, creating a durable artifact rather than another chat-note workaround.

6. **No owner decision gap.** The active PAUTH and `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` already authorize this bounded test-infrastructure fix.

## Applicability Preflight

- packet_hash: `sha256:1bf5349827e02c63363ed95830819f8c6dc063af054a48d3d451f4b0d735bab2`
- bridge_document_name: `gtkb-wi4678-pytest-timeout-addopts-dependency`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-001.md`
- operative_file: `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | yes | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

All 5 must_apply clauses have evidence: no blocking gaps. Gate passes.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` — Owner authorization for implementing unimplemented May29 Hygiene work items through the normal bridge/GO process.
- `bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-003.md` — PB implementation evidence recording that the exact proposed pytest command could not collect due to `--timeout=30` rejection.
- `bridge/gtkb-wi4677-backlog-json-option-validation-003.md` — PB implementation evidence recording the same default addopts failure before focused tests could run.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-005.md` — Historical bridge evidence showing the same `-o addopts=""` workaround pattern has appeared before.

## Implementation Conditions

1. `pytest-timeout` must be added to the GroundTruth-KB dev extra in `groundtruth-kb/pyproject.toml`, not to the root `pyproject.toml` (the root already holds the timeout policy; only the dev dependency surface is missing).
2. The lockfile update must be produced by the managed toolchain (`uv lock` or equivalent within the groundtruth-kb venv), not hand-edited.
3. The new structural regression test (`platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py`) must fail if `--timeout=30` is present in root addopts but `pytest-timeout` is not importable from the GroundTruth-KB environment — i.e., it must test the *contract*, not just that the module is installed.
4. No `-o addopts=""` workaround may be introduced into any committed file as part of this fix. The workaround remains historical evidence only.
5. If the root `pyproject.toml` is modified, the change must be limited to clarifying comments/annotations about the dependency contract; the existing `--timeout=30` addopts policy must remain intact.
6. Verification report must include the regression test passing *without* `-o addopts=""` — proving the timeout addopts are now supported by the installed dependency.