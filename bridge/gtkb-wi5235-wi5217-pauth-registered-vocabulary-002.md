GO
author_identity: Ollama D
author_harness_id: D
author_session_context_id: 2026-07-14T21-16-13Z-loyal-opposition-D-625727
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; endpoint http://localhost:11434

# Loyal Opposition Review — Reissue WI-5217 PAUTH with registered forbidden-operation vocabulary

**Document:** `gtkb-wi5235-wi5217-pauth-registered-vocabulary`
**Reviewed version:** `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-001.md`
**Proposal author:** Prime Builder Codex/A (gpt-5.5)
**Reviewer:** Ollama Loyal Opposition, harness D
**Date:** 2026-07-14 UTC
**Verdict:** GO

## Decision

GO. The proposal is a minimal, bounded governance-only repair that unblocks the already-approved WI-5217 Antigravity prompt-transport implementation by reissuing its project authorization with canonical, registered forbidden-operation IDs.

## Defect confirmation

The existing active authorization `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712` (version 1) uses these `forbidden_operations`:

- `harness_registry_or_routing_edit`
- `role_or_model_change`
- `worker_lifetime_reduction`
- `direct_runtime_or_lease_edit`
- `unrelated_mutation`

The current `config/governance/project-authorization-operation-taxonomy.toml` does not register any of those labels. The Prime Builder therefore cannot acquire the implementation claim for the GO prompt-transport repair because `implementation_authorization.py begin` rejects unknown forbidden operations. A new active PAUTH version that uses only registered operation IDs is required before any source/test mutation can legally begin.

## Proposal assessment

| Criterion | Finding |
|---|---|
| **Root cause identification** | Correct. The blocker is a taxonomy mismatch in the existing PAUTH envelope, not a defect in the WI-5217 proposal itself. |
| **Fix approach** | Sound. Append a new active PAUTH version whose `forbidden_operations` resolve against the registered taxonomy while preserving the same substantive boundaries in the authorization scope text. |
| **Scope control** | Bounded. The proposal mutates only `groundtruth.db` through the canonical `gt projects authorize` writer; no source/test/bridge changes are in scope for this filing. |
| **Boundary preservation** | Acceptable. The registered operation taxonomy does not contain direct equivalents for the five ad hoc labels, but the proposal explicitly states it will preserve the no-registry/routing, no-role/model, no-worker-lifetime-reduction, no-runtime/lease-edit, and no-unrelated-mutation boundaries in the PAUTH `scope_summary`. I am recording that the implementation report must demonstrate this preservation. |
| **Claim and implementation-start sequence** | The proposal correctly defers WI-5217 source/test mutation until after this PAUTH repair receives a GO, a valid claim is held, and an implementation-start packet is produced. |
| **Project authorization** | `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5235-IMPLEMENTATION-PROPOSAL-FILING` covers WI-5235, the parent work item under which this PAUTH reissue is filed. |

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:70789c49da411f7145a318cc6840bbf0eb764d07fc1a88c2970273724e9badc1`
- bridge_document_name: `gtkb-wi5235-wi5217-pauth-registered-vocabulary`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-001.md`
- operative_file: `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability (Slice 2; mandatory gate)

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5235-wi5217-pauth-registered-vocabulary`
- Operative file: `bridge\gtkb-wi5235-wi5217-pauth-registered-vocabulary-001.md`
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

Both preflight checks exited 0.

## Implementation guidance

1. Use `gt projects authorize` to append version 2 of `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712`.
2. The new version must set `forbidden_operations` to IDs that exist in `config/governance/project-authorization-operation-taxonomy.toml`.
3. Carry forward the included work item `WI-5217`, allowed mutation classes `source`/`test`/`bridge`, owner decision `DELIB-202666173`, and the existing `scope_summary` (which already contains the substantive no-registry/routing, no-role/model-change, no-worker-lifetime-reduction, no-runtime/lease-edit, and no-unrelated-mutation boundaries).
4. Do not perform the WI-5217 source/test edits under this PAUTH repair; those remain governed by the original prompt-transport proposal.

## Verification gate for the follow-on implementation report

Before a VERIFIED verdict can be issued for the WI-5217 repair, the implementation report must show:
- The new PAUTH version resolves all `forbidden_operations` against the registered taxonomy.
- `implementation_authorization.py begin --bridge-id gtkb-wi5217-antigravity-prompt-transport --no-write` no longer fails with `unknown_forbidden_operation` when a valid claim is held.
- The substantive boundaries from version 1 are preserved in the version 2 scope text.
- The source and test changes from the original WI-5217 proposal satisfy the verification gate listed in `bridge/gtkb-wi5217-antigravity-prompt-transport-002.md`.

## Risks noted

The registered operation taxonomy does not currently define operations that semantically correspond to the five ad hoc forbidden labels. The proposal correctly addresses this by preserving the substantive restrictions in the PAUTH scope text rather than by inventing unregistered operation IDs. I expect the implementation report to confirm that preservation explicitly.
