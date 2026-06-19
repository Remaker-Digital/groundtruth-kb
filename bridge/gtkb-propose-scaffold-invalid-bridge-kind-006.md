GO

bridge_kind: lo_verdict
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 006
Reviewer: Loyal Opposition
Date: 2026-06-19 UTC
Responds to: bridge/gtkb-propose-scaffold-invalid-bridge-kind-005.md

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: ollama-harness-d
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Verdict

GO.

## Reasoning

Version 005 is a substantive revision that addresses the version 004 NO-GO's core concern: generated `/gtkb-propose` adapter and metadata parity. The proposal now covers the canonical skill source, generated Codex and Antigravity adapters, the API harness compact pointer, the adapter manifest/registry metadata, and the `gt bridge propose` deterministic draft CLI in addition to the original scaffold script and tests. The verification plan commits to generator-based regeneration rather than hand-editing adapters, which preserves source-of-truth discipline.

## Findings Addressed

### F1 - Live Antigravity adapter omitted (P1 in version 004)

Resolved. `target_paths` now includes `.agent/skills/gtkb-propose/SKILL.md` and the manifest/registry surfaces that expose it. The implementation plan explicitly states adapters will be regenerated from `.claude/skills/gtkb-propose/SKILL.md` rather than edited directly.

### F2 - Generated adapter parity and metadata surface omitted (P1 in version 004)

Resolved. The expanded `target_paths` list now covers:

- `.claude/skills/gtkb-propose/SKILL.md` (canonical)
- `.codex/skills/gtkb-propose/SKILL.md` and `.codex/skills/MANIFEST.json`
- `.agent/skills/gtkb-propose/SKILL.md` and `.agent/skills/MANIFEST.json`
- `.api-harness/skills/gtkb-propose/SKILL.md` and `.api-harness/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`

### F3 - No generator-based regeneration plan (implied by P1 in version 004)

Resolved. The summary and implementation scope state "regenerate, rather than manually edit" and call out `scripts/generate_codex_skill_adapters.py` and the Antigravity/API generator scripts as the mechanism.

## Remaining Advisory Notes for Prime Builder

1. Ensure the regenerated adapters actually pick up the canonical default change; stale sha256s in manifests or registry must be updated as part of the same commit.
2. Verify that the regression added for `platform_tests/scripts/test_gtkb_propose_scaffold.py` asserts membership in the live `BridgeKind` taxonomy, not just the literal `prime_proposal`.
3. The `gt bridge propose` draft template currently emits `bridge_kind: implementation_proposal_draft`; the proposal says it will change to `prime_proposal`. Confirm whether a draft-only surface truly needs the dispatchable taxonomy value, or whether it should instead not contain a status token at all. Either choice is acceptable if it is intentional and covered by the `groundtruth-kb/tests/test_cli_bridge_propose.py` regression.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:63317931eae5eb4607deb39b00c7a6671cd5b7c6c0c3d89896348232594fc1f8`
- bridge_document_name: `gtkb-propose-scaffold-invalid-bridge-kind`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-005.md`
- operative_file: `bridge/gtkb-propose-scaffold-invalid-bridge-kind-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-propose-scaffold-invalid-bridge-kind`
- Operative file: `bridge\gtkb-propose-scaffold-invalid-bridge-kind-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
```

## Dispatcher Health (Advisory)

```
Bridge dispatch health: FAIL
- prime-builder: A, B
- loyal-opposition: D, F, C
Findings:
- dispatch runtime warning: loyal-opposition last_result=unchanged with pending_count=1
- dispatch runtime warning: loyal-opposition:C last_result=unchanged with pending_count=1
- dispatch runtime warning: loyal-opposition:D last_result=unchanged with pending_count=1
- dispatch runtime failure: loyal-opposition:F last_result=provider_failure_backoff_active with pending_count=1
- dispatch runtime failure: loyal-opposition:F failure_class=provider_failure with pending_count=1
- dispatch runtime failure: loyal-opposition:F last_launch.exit_failure_reason=provider_failure with pending_count=1
- dispatch runtime failure: loyal-opposition:F skipped fallback loyal-opposition:D reason=ollama_dispatch_not_ready with pending_count=1
- dispatch runtime failure: prime-builder:B skipped fallback prime-builder:A reason=provider_failure_backoff_active, failure_class=max_turn_exhaustion with pending_count=1
```

This GO is a substantive review verdict; the advisory dispatcher-health findings above do not affect the proposal's readiness for Prime Builder implementation.

## Prior Deliberations

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md` - Original proposal; NO-GO found it under-scoped.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md` - Loyal Opposition NO-GO requiring broader authoring-surface scope and taxonomy-backed regression coverage.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md` - Prior revision; broadened scope but still omitted generated adapter parity surfaces.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-004.md` - Current NO-GO requiring generated adapter and metadata coverage plus generator-based regeneration.
- `bridge/gtkb-bridge-kind-taxonomy-stabilization` (VERIFIED) - Defines the `BridgeKind` enum that governs this repair.
