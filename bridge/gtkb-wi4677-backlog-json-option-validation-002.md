GO

# Backlog JSON Option Validation — GO

bridge_kind: lo_verdict
Document: gtkb-wi4677-backlog-json-option-validation
Verdict: GO
Version: 002
Author: Loyal Opposition (OpenRouter, harness F)
Date: 2026-06-19 UTC

author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

References:
- Proposal: bridge/gtkb-wi4677-backlog-json-option-validation-001.md (NEW, Codex/Harness A)
- Project: PROJECT-GTKB-MAY29-HYGIENE
- PAUTH: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
- WI: WI-4677

---

## Verdict Summary

**GO.** The proposal identifies a real defect — malformed JSON-list CLI option values silently persist into MemBase `work_items` linkage fields — and prescribes a narrow, well-bounded fix: validate JSON-list fields before service-layer writes in `gt backlog add` and `gt backlog update`/`gt backlog resolve`. Scope is correctly limited to source and tests with no schema migration, no direct DB mutation, and no historical cleanup.

## Bridge Finding

The proposal meets all blocking requirements:

1. **Defect substantiated.** The malformed value `[bridge/gtkb-bridge-thread-read-cli-004.md,bridge/gtkb-bridge-thread-read-cli-commands-002.md]` (unquoted strings, not parseable JSON) was observed during WI-4634 reconciliation and required manual `KnowledgeDB.update_work_item(...)` correction. Source code review confirms `cli_backlog_add.py` has no JSON validation on `related_spec_ids`, `related_deliberation_ids`, `related_bridge_threads`, or `depends_on_work_items` fields. `cli_backlog_update.py` similarly lacks JSON validation on `related_bridge_threads`.

2. **Scope is bounded.** Only two source files and two test files are targeted. No schema changes, no direct DB mutations, no historical cleanup beyond the already-corrected WI-4634 row. The fix is "validate before write" — fail closed with actionable CLI guidance for malformed values, preserve valid JSON arrays exactly.

3. **Authorization is active.** `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` covers WI-4677 as an unimplemented May29 Hygiene work item. `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` provides owner authorization for implementing through the normal bridge/GO process.

4. **Spec linkage is concrete.** All blocking specs are cited and preflight-verified: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

5. **No owner decision gap.** The proposal correctly identifies that no new owner decision is required — the active PAUTH and Mike's automation instruction already authorize this work.

## Applicability Preflight

- packet_hash: `sha256:2b4907007982a13a695bfe2a8eed8a5edc56e22545f5aa744a3f69dbfb80e27f`
- bridge_document_name: `gtkb-wi4677-backlog-json-option-validation`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4677-backlog-json-option-validation-001.md`
- operative_file: `bridge/gtkb-wi4677-backlog-json-option-validation-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

All 4 must_apply clauses have evidence: no blocking gaps. Gate passes.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` — Owner authorization for implementing unimplemented May29 Hygiene work items through the normal bridge/GO process.
- `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` — Backlog/project CLI precedent for adding bounded command-surface behavior with focused tests.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — Proposal-standards context for producing machine-readable target paths, project linkage, and spec-derived verification.

## Implementation Conditions

1. JSON validation must be applied at the service layer (in `_validate_request` for `cli_backlog_add.py` and in `update_backlog_item` for `cli_backlog_update.py`) before any DB write path, not in the Click CLI layer alone.
2. Error messages for malformed JSON must identify which option field is invalid and provide actionable guidance (e.g., "expected a JSON array of strings").
3. Valid JSON arrays must pass through unmodified — no reformatting, reordering, or canonicalization that could break round-trip expectations.
4. The fix must cover `related_bridge_threads` in the `gt backlog resolve` path as well as `gt backlog update`, since the defect was discovered through the resolve subcommand.
5. Verification report must include test runs proving malformed `[unquoted,list]`, `{not an array}`, and bare-string values are rejected at the CLI.