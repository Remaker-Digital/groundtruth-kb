GO

# Loyal Opposition Review - WI-4982 Init-Keyword Grammar Reconciliation

bridge_kind: lo_verdict
Document: gtkb-wi4982-init-keyword-grammar-reconciliation
Version: 002
Responds-To: bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-001.md
Reviewer: Loyal Opposition (Antigravity, harness C)
Date: 2026-07-07 UTC
Verdict: GO

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 85ac6109-1992-4afd-937d-292987d5a90b
author_model: Gemini 3.5 Flash (High)
author_model_version: current Gemini runtime via Antigravity
author_model_configuration: auto-dispatched Loyal Opposition session

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4982

## Verdict

GO. The implementation proposal for WI-4982 is approved to proceed.

This GO authorizes the reconciliation of the divergent init-keyword matchers into a single, unified parser that strictly implements `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 (`^::init (gtkb|application)( (pb|lo))?$`). It enforces the v3 decision split (role-token present establishes session/transcript role, role-token absent preserves durable/resolver fallback without writing session role markers), maintains the backward compatibility of `::init gtkb pb/lo` dispatcher emissions, and preserves the Agent Red separateness boundary by resolving `application` through the active work-subject state rather than off-root hardcoding.

## Separation Check

The proposal was authored by Prime Builder (Codex) session `019f3170-d706-77d3-b3e1-be39d47f3eda`. This verdict is authored from a separate Loyal Opposition session context (Antigravity harness ID C, session ID `85ac6109-1992-4afd-937d-292987d5a90b`), satisfying the review independence boundary.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation
```

Observed:

- packet_hash: `sha256:c723f3ac8fa5f0185473071861e66f1c6d25f552f58ea4d678ee212b278ce2bb`
- bridge_document_name: `gtkb-wi4982-init-keyword-grammar-reconciliation`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-001.md`
- operative_file: `bridge/gtkb-wi4982-init-keyword-grammar-reconciliation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4982-init-keyword-grammar-reconciliation
```

Observed:

- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Prior Deliberations

- `DELIB-20260707-WI4982-IMPLEMENTATION-APPROVAL` - Owner implementation authorization for WI-4982.
- `DELIB-20260648` - Envelope init-keyword optionality clarification.
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` - Owner role-authority boundary correction program approval.

## Spec-Derived Verification Expectations

- Verify the single canonical parser accepts exactly the six v3 canonical forms (`::init gtkb`, `::init gtkb pb`, `::init gtkb lo`, `::init application`, `::init application pb`, `::init application lo`) and strictly rejects synonyms, case variants, malformed whitespace, wrong subjects, and trailing garbage.
- Verify that subject-only declarations (`::init gtkb` or `::init application`) do not write `.claude/session/active-session-role.json` or per-session role markers, fallback to durable/resolver configuration properly, and do not trigger auditing mismatch warnings.
- Verify that role-token declarations (`::init gtkb pb`, `::init gtkb lo`, etc.) correctly write active-session-role and per-session markers on interactive turns while keeping dispatcher/headless execution unaffected.
- Verify that both Claude and Codex SessionStart wrappers are structurally checked by `scripts/check_codex_hook_parity.py` and pass parity checks with no errors.
- Run the full suite of unit, hook, workstream-focus, and resolver tests to confirm zero regressions.
