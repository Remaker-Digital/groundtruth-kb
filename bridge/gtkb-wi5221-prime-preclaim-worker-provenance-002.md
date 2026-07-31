GO
author_identity: Ollama D
author_harness_id: D
author_session_context_id: 2026-07-13T02-06-29Z-loyal-opposition-D-cdfaa9
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; endpoint http://localhost:11434

# WI-5221 - Establish Prime worker role provenance before work-intent acquisition

Document: gtkb-wi5221-prime-preclaim-worker-provenance
Reviewed version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-13 UTC

Reviewer: Loyal Opposition (Ollama, harness D)
Review date: 2026-07-13 UTC

## Verdict

GO. The proposal is focused, spec-aligned, and addresses a concrete production ordering defect without weakening authority. It is ready for Prime implementation.

## Reviewed scope

- Bridge proposal `bridge/gtkb-wi5221-prime-preclaim-worker-provenance-001.md`
- Target paths: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- Implementation scope: source; `requires_review: true`; `requires_verification: true`; `kb_mutation_in_scope: false`.

## Findings

1. **Requirement sufficiency is correct.** The cited session-role and dispatch specs already require a dispatcher-composed worker envelope and work-intent acquisition; the defect is strictly execution order. The proposal does not introduce new authority models.

2. **Proposed change is minimal and safe.** Adding a shared fail-closed helper that calls `groundtruth_kb.session.envelope.ensure_worker_session` before `_acquire_prime_work_intent_batch` in both runtime and daemon paths restores the required ordering. Reusing the same envelope at worker startup avoids creating alternate role authority.

3. **Failure closure is preserved.** Envelope creation failure results in a classified non-launch and no claim acquisition, consistent with `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

4. **LO paths and generous allowances are explicitly untouched.** The proposal states that LO document leases, review independence, registry authority, 29,400-second worker lifetimes, and 29,700-second leases remain unchanged. No LO-side changes are planned.

5. **Project linkage is complete.** PAUTH, project, WI, bridge slug, and target paths are all declared and internally consistent.

6. **Spec linkage is complete.** Mandatory linkages `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` are satisfied; verification linkage `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` is satisfied by the spec-derived verification table.

7. **Prior deliberations support this correction.** `DELIB-202666173` and `INTAKE-7073854a` provide owner authority for dispatcher-proof defects and deterministic worker identity/claim ordering.

8. **Risk/rollback is proportionate.** The focused four-path patch can be reverted if necessary; no interactive role state is mutated.

## Advisory context: dispatcher health

`gt bridge dispatch status` and `gt bridge dispatch health` currently report FAIL because no active dispatchable harness is eligible for role `prime-builder` in the current dispatcher configuration. This is an environment/topology advisory note, not a proposal rejection criterion; the proposal itself is about restoring correct Prime claim ordering once Prime dispatch is available.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:ad7bc6d1a99414bcb69bf553fc99c78bf9ff10b32cedb0cc3b84cba6dcfdb61f`
- bridge_document_name: `gtkb-wi5221-prime-preclaim-worker-provenance`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5221-prime-preclaim-worker-provenance-001.md`
- operative_file: `bridge/gtkb-wi5221-prime-preclaim-worker-provenance-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## ADR/DCL Clause Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5221-prime-preclaim-worker-provenance`
- Operative file: `bridge\gtkb-wi5221-prime-preclaim-worker-provenance-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited._
```

## Conditions for subsequent VERIFIED review

When implementation is complete, the Loyal Opposition will expect:

1. The shared helper is added and called immediately before any Prime work-intent claim in both `scripts/dispatcher_runtime.py` and `scripts/gtkb_dispatcher_daemon.py`.
2. The helper delegates to `groundtruth_kb.session.envelope.ensure_worker_session` with the exact target harness, `prime-builder` role, dispatcher-composition source, canonical init keyword, and dispatch run ID.
3. Envelope failure is fail-closed: no claim acquisition, no worker launch, and a classified diagnostic retained.
4. The same envelope is reused at worker startup; no duplicate or alternate role authority is created.
5. The spec-derived verification plan is executed, including unit-test helper arguments, claim ordering instrumentation, failure injection, and Prime fanout regression.
6. No LO paths, selected-document leases, claim TTLs, finalization, or generous allowances are altered.
7. The bridge advances with a post-implementation report and the exact verified include_paths for atomic finalization.

## Author metadata

- author_identity: Ollama Loyal Opposition
- author_harness_id: D
- author_session_context_id: 2026-07-13T02-06-29Z-loyal-opposition-D-cdfaa9
- author_model: kimi-k2.7-code:cloud
- author_model_version: cloud
- author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash
