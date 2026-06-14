GO

bridge_kind: lo_verdict
Document: gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-14 UTC
Reviewer: Loyal Opposition
Author-Harness-ID: A
Responds to: bridge/gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-001.md

# Loyal Opposition GO Verdict: GTKB-CORE-001 Phase 4 Prompt Driver

## Verdict

GO.

Prime Builder may implement the cross-session core-spec-intake prompt driver
within the declared target paths:

- `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/templates/hooks/session-start-governance.py`
- `groundtruth-kb/tests/test_core_spec_intake.py`

This GO does not authorize formal GOV/ADR/DCL/SPEC/PB creation without a
separate approval packet, canonical `groundtruth.db` mutation, GT-KB's own
SessionStart payload redesign, production deployment, credential work, or edits
outside the target paths.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
```

Result:

- packet_hash: `sha256:8cb15c5b72efdb4d6601b233ae921fa72f54b09b5852476f6863b5aeeb1b0f15`
- bridge_document_name: `gtkb-core-spec-intake-phase-4-cross-session-prompt-driver`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-001.md`
- operative_file: `bridge/gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: `[]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-core-spec-intake-phase-4-cross-session-prompt-driver`
- Operative file: `bridge\gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-001.md`
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
```

## Prior Deliberations

Commands:

```powershell
python -m groundtruth_kb.cli deliberations search GTKB-CORE-001 --limit 10
python -m groundtruth_kb.cli deliberations search "core spec intake" --limit 10
```

Relevant results:

- `DELIB-20263207` - owner authorized building GTKB-CORE-001 Phase 4, the cross-session prompt driver.
- `DELIB-0875` - owner approved the core spec intake target behavior and compatibility posture.
- `DELIB-20261911` - compressed VERIFIED Slice 1 core-spec-intake-default bridge thread.
- `DELIB-20261760` / `DELIB-20261168` - compressed VERIFIED Phase 3A current-root CLI bridge thread.
- Prior NO-GO/GO deliberations on Slice 1 and Phase 3A were reviewed as history; they do not block this Phase 4 proposal.

## Evidence Reviewed

- Live `bridge/INDEX.md`.
- Proposal file: `bridge/gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-001.md`.
- Live backlog: `python -m groundtruth_kb.cli backlog list --id GTKB-CORE-001 --json`.
- Live authorization: `python -m groundtruth_kb.cli projects authorizations PROJECT-GTKB-CORE-001 --json`.
- Source search over `core_spec_intake.py`, `scaffold.py`, `doctor.py`, `templates/hooks/session-start-governance.py`, and `test_core_spec_intake.py`.

## Review Findings

### Scope and Authorization

PASS. Live PAUTH `PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-4-CROSS-SESSION-PROMPT-DRIVER` is active, includes `GTKB-CORE-001`, includes the cited core-intake specs, and expires 2026-06-27. The proposal stays inside source/template/test changes and excludes formal-artifact creation and GT-KB's own SessionStart payload redesign.

### Current-State Claim

PASS. Source search confirms the existing implementation has core-intake primitives and one-time scaffold prompting, but no `refresh_intake_prompt` driver, no cross-session session-start wiring, and no `_check_core_spec_intake` doctor check. That supports the proposal's gap claim.

### Specification Linkage and Test Mapping

PASS. The proposal links the feature specs (`SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, `DCL-CORE-INTAKE-001`) and all triggered cross-cutting governance surfaces. The verification table maps repeat prompting, stop-at-completion, persisted evidence, opt-out, fail-safe session start, and backward compatibility to tests.

### Residual Risk

ACCEPTED. The main risk is session-start hook fragility in adopter projects. The proposal mitigates it with fail-safe no-op behavior when project resolution fails or `groundtruth.db` is absent. The implementation report must prove this behavior with tests and must distinguish adopter-facing template hooks from GT-KB's own SessionStart payload.

## Required Implementation Verification

Prime Builder's implementation report should include, at minimum:

```powershell
python -m pytest groundtruth-kb/tests/test_core_spec_intake.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/templates/hooks/session-start-governance.py groundtruth-kb/tests/test_core_spec_intake.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/templates/hooks/session-start-governance.py groundtruth-kb/tests/test_core_spec_intake.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
```

The report must also show that the session-start change is limited to the adopter-facing scaffold template and that canonical `groundtruth.db` is not mutated by the driver during normal prompt refresh.

## Verdict

GO. The implementation proposal is approved for Prime Builder implementation
within the target paths and constraints above.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
