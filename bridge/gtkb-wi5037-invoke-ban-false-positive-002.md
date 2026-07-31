GO

# Loyal Opposition Review - WI-5037 Invoke Ban False Positive

bridge_kind: lo_verdict
Document: gtkb-wi5037-invoke-ban-false-positive
Version: 002
Responds-To: bridge/gtkb-wi5037-invoke-ban-false-positive-001.md
Reviewer: Loyal Opposition (Antigravity, harness C)
Date: 2026-07-07 UTC
Verdict: GO

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 85ac6109-1992-4afd-937d-292987d5a90b
author_model: Gemini 3.5 Flash (High)
author_model_version: current Gemini runtime via Antigravity
author_model_configuration: auto-dispatched Loyal Opposition session

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5037-INVOKE-BAN-FALSE-POSITIVE-20260707
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5037

## Verdict

GO. The implementation proposal for WI-5037 is approved to proceed.

This GO authorizes narrowing the DIRECT-HARNESS-INVOKE-BAN PreToolUse hook matcher to prevent false positives on legitimate governed `gt` status/deliberation/backlog commands that merely reference or mention harness/provider names in their arguments or prose. The core requirement (SPEC-INTAKE-21c5b3 / DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN) prohibiting direct harness-to-harness process spawning must remain fully intact and verified by unit tests.

## Separation Check

The proposal was authored by Prime Builder (Codex) session `019f337a-009a-7f51-8dce-b6c3f1d91b1c`. This verdict is authored from a separate Loyal Opposition session context (Antigravity harness ID C, session ID `85ac6109-1992-4afd-937d-292987d5a90b`), satisfying the review independence boundary.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5037-invoke-ban-false-positive
```

Observed:

- packet_hash: `sha256:a908bc9ba1faaf09db20dace1f1f6052aff71aa199b000a476fb92fe5248e225`
- bridge_document_name: `gtkb-wi5037-invoke-ban-false-positive`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5037-invoke-ban-false-positive-001.md`
- operative_file: `bridge/gtkb-wi5037-invoke-ban-false-positive-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5037-invoke-ban-false-positive
```

Observed:

- clauses evaluated: `5`
- must_apply: `3`
- may_apply: `2`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - Owner/governance decision prohibiting direct harness-to-harness launch.
- `DELIB-20260707-WI5037-IMPLEMENTATION-APPROVAL` - Owner authorized Prime Builder to file this proposal.
- `gtkb-wi5037-invoke-ban-false-positive-advisory-001` - LO advisory surfacing the false positive class and scoping remediation.

## Spec-Derived Verification Expectations

- Verify the narrowed matcher prevents false-positives for commands like `gt bridge dispatch status | select-string "claude"` and deliberations containing provider descriptions.
- Unit/regression tests must verify that direct harness launches (`claude -p ...`, `codex exec ...`, etc.) remain blocked with exit code > 0 and correct remediation text.
- Verify equivalent enforcement and test coverage across Claude and Codex hook surfaces (behavioral parity).
