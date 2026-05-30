NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-work-intent-registry-prime-write-integration
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-28 UTC
Responds to: bridge/gtkb-work-intent-registry-prime-write-integration-001.md
Verdict: NO-GO

# Loyal Opposition Review - Work-Intent Registry Prime Write Integration

## Claim

NO-GO. The proposal passes the mechanical preflight floor and the standing PAUTH appears to cover the declared source, hook, and test-addition mutation classes, but the proposed acquisition boundary does not close the duplicated-drafting race it claims to close, and the target scope omits the managed scaffold/template surface for the bridge-propose helper.

File bridge scan contribution: 1 selected entry processed.

## Prior Deliberations

Deliberation search command:

```text
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "work intent registry prime write integration WI-3414 bridge parallel session collision" --limit 8 --json
```

Observed result: `[]`.

Relevant prior bridge records were verified directly:

- `bridge/gtkb-bridge-parallel-session-collision-006.md:15` verifies the registry foundation module as foundation-only and explicitly not bridge-writer, compliance-gate, hook, startup, or AXIS-2 integration.
- `bridge/gtkb-bridge-parallel-session-collision-006.md:31` confirms the foundation implementation exposes `acquire`, `release`, `current_holder`, and `revalidate_thread_version`.
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md:65` through `:72` cites the sibling quiesce thread and prior trigger race history.

## Positive Confirmations

- Live bridge state was re-read before this verdict. Latest status remained `NEW` for `bridge/gtkb-work-intent-registry-prime-write-integration-001.md`; no thread drift was reported by `show_thread_bridge.py`.
- Applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- Clause preflight exited cleanly with zero blocking gaps.
- `PROJECT-GTKB-RELIABILITY-FIXES` is active, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, and its `allowed_mutation_classes` are `["source", "test_addition", "hook_upgrade"]`.
- `WI-3414` is an active member of `PROJECT-GTKB-RELIABILITY-FIXES` in the live project membership output.

## Findings

### P1-001 - Work-intent acquisition happens after duplicated drafting can already occur

Observation: The proposal claims the integration prevents concurrent Prime sessions from independently drafting and filing the same bridge thread version (`bridge/gtkb-work-intent-registry-prime-write-integration-001.md:25`) and cites the observed S365 waste where two Prime instances independently chose the same NO-GO thread and one spent about 30 minutes drafting redundantly (`:33` through `:35`). The proposed trigger integration only checks `current_holder(slug)` before spawn, then says the spawned Prime session will acquire later through the helper (`:96` through `:101`). The proposed helper integration acquires only when the bridge-propose helper starts (`:84` through `:91`).

Current-state evidence: The existing helper API already receives a completed `body` argument (`.claude/skills/bridge-propose/helpers/write_bridge.py:845` through `:855`), performs helper-side processing afterward (`:920` through `:933`), then writes the bridge file (`:935` through `:942`). That means a Prime agent can spend the drafting tokens before the helper has a chance to acquire a work-intent record. The registry primitive itself only blocks another session after a non-expired holder exists (`scripts/bridge_work_intent_registry.py:140` through `:166`).

Deficiency rationale: In the exact S365 sequence described by the proposal, an interactive Prime session can begin drafting without any holder record. The cross-harness trigger then sees `current_holder(slug) == None` and still spawns a headless Prime worker. If the worker later acquires in the helper, the hook may prevent the interactive session's final write, but the duplicate drafting and token burn have already happened. This does not satisfy the proposal's own implementation claim.

Impact: The implementation would likely improve final overwrite safety, but it would not reliably close the duplicate-work race or the stated token-waste failure mode. The bridge would still permit two Prime sessions to independently plan and draft the same response until one reaches the helper/write boundary.

Required revision: Move or add acquisition to the first durable "Prime is taking this thread" boundary, not only the file-write helper. The revision should define how both auto-dispatched and interactive Prime sessions acquire and refresh the holder before substantive drafting begins, how the holder is released or transferred, and how the trigger handles a pre-spawn acquisition or dispatch-owned holder without consuming dispatch budget incorrectly. Add a regression test that simulates: no holder exists, an interactive Prime has selected the thread but has not yet written, and the trigger attempts to spawn a second Prime worker.

### P1-002 - Proposal omits the managed template/scaffold surface for the bridge-propose helper

Observation: The target paths include the installed helper `.claude/skills/bridge-propose/helpers/write_bridge.py`, but omit the managed template source `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` and the template/package tests that load that helper (`bridge/gtkb-work-intent-registry-prime-write-integration-001.md:19`, `:109`, `:112`, and `:125`).

Current-state evidence: The managed artifact registry marks `skill.bridge-propose.helper` as `gt-kb-managed`, with template path `skills/bridge-propose/helpers/write_bridge.py`, target path `.claude/skills/bridge-propose/helpers/write_bridge.py`, and managed profiles `dual-agent` and `dual-agent-webapp` (`groundtruth-kb/templates/managed-artifacts.toml:508` through `:519`). The package test surface imports the helper from the template tree (`groundtruth-kb/tests/test_bridge_propose_helper.py:25` through `:47`). Platform tests also track template helper and SKILL paths for parity (`platform_tests/skills/test_bridge_propose_helper.py:31` through `:35`).

Deficiency rationale: The bridge-propose helper is not merely a local session file; it is a product-managed bridge-creation contract distributed through the scaffold/upgrade template system. Updating only the installed helper would create product/template drift and would leave new or upgraded dual-agent installations without the work-intent behavior. The proposal's verification plan would also fail to exercise the product template helper path that the package test suite uses.

Impact: Even if the live checkout works, the GT-KB platform distribution could remain stale. That undermines the bridge reliability fix for adopter/scaffolded projects and makes later upgrade behavior ambiguous.

Required revision: Add the managed template helper and any necessary template skill documentation to `target_paths`, and add/extend tests against the template helper path. At minimum include `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` and `groundtruth-kb/tests/test_bridge_propose_helper.py`; if behavior or operator expectations change, include `groundtruth-kb/templates/skills/bridge-propose/SKILL.md` and its parity assertions as well. Consider whether the bridge-compliance hook template needs the same treatment for new scaffolds.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:00a74522016ea452165b808ff565d5bac286c7627206adb6bfa640b7ad40edd1`
- bridge_document_name: `gtkb-work-intent-registry-prime-write-integration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-intent-registry-prime-write-integration-001.md`
- operative_file: `bridge/gtkb-work-intent-registry-prime-write-integration-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-work-intent-registry-prime-write-integration`
- Operative file: `bridge\gtkb-work-intent-registry-prime-write-integration-001.md`
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

## Decision

NO-GO. Revise the proposal to establish the work-intent holder before substantive Prime drafting can begin, and include the managed scaffold/template helper surface in implementation and verification scope.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
