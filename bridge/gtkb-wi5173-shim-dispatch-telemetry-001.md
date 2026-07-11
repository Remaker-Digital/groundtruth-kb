NEW

# Implementation Proposal - Instrument shim-harness per-run turn/tool diagnostic telemetry (unblocks WI-5060 max-turn budget question, first slice of owner diagnostic-mode requirement)

bridge_kind: prime_proposal
Document: gtkb-wi5173-shim-dispatch-telemetry
Version: 001
Date: 2026-07-10 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder
author_metadata_source: Codex system runtime context plus explicit session document


Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5173-SHIM-TELEMETRY-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5173

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py"]

Implementation proposal for a bounded code or platform change.

## Claim

Implement `gtkb.shim_dispatch_telemetry.v1`: one atomic, privacy-bounded JSON
envelope per dispatcher-launched shim run plus a bounded read-only distribution
query. The envelope supplies measured turn/tool evidence for the WI-5060 budget
question without changing dispatch selection, turn budgets, stdout/stderr
contracts, or bridge verdict behavior.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` is owner-approved and specifies the
schema identifier, storage location, every required data group, null semantics,
privacy exclusions, stop reasons, partial reconciliation, query semantics, and
test matrix. The approved `source_spec_id` backfill on WI-5173 is fail-closed
until the independent document-role writer verdict; this proposal binds to the
approved specification and active PAUTH without bypassing that correction.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `scripts/openrouter_harness.py`, `scripts/dispatcher_runtime.py`, `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_ollama_harness.py`, `platform_tests/scripts/test_openrouter_harness.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py`.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - controls the v1 envelope,
  privacy, null semantics, failure isolation, query, and acceptance tests.
- `SPEC-TAFE-R6`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and
  `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - provide the existing dispatch and
  telemetry context this slice specializes without replacing it.
- `GOV-SESSION-ROLE-AUTHORITY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` - require `worker.role` to come only from
  the validated worker session document. Dispatcher intent is confirmation,
  never role authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - preserve PAUTH,
  bridge, claim, and implementation-start gates.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived
  tests across normal, partial, failure, and privacy paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the owner requirement's
  formal lineage from approved specification through PAUTH, bridge, tests, and
  independent verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `GOV-STANDING-BACKLOG-001` - keep all targets in GT-KB platform scope and
  extend the existing WI rather than create duplicate standing work.

## Prior Deliberations

- `DELIB-202666074` - owner approval for the bounded telemetry implementation
  authorization.
- `DELIB-202665303` - owner decision to measure real per-harness worker timing
  before changing operational budgets.
- `DELIB-20265026` - provider failure evidence relevant to safe partial
  telemetry and failure isolation.

## Owner Decisions / Input

- `DELIB-202666074` - owner approved the telemetry scope, explicitly excluding
  automatic turn-budget and production selection changes.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5173-SHIM-TELEMETRY-20260710` -
  active PAUTH; protected changes still require independent LO GO, matching
  claim, and implementation-start evidence.

## Proposed Scope

1. Add a small telemetry module that validates and atomically writes exactly one
   `dispatch-runs/<dispatch_id>.telemetry.json` v1 envelope. It accepts only
   the schema's privacy-safe primitives and rejects unsupported schema values.
2. Instrument the shared cloud tool loop and the Ollama/OpenRouter shim paths
   with an observer/result object that records turn ordinal and canonical tool
   names, tool totals, normalized stop reason, timing, and observed provider
   usage. It must not add provider bodies, prompts, arguments, results, or
   generated text to telemetry or existing stdout/stderr.
3. Resolve the worker identity and role from the validated session document
   artifact. A missing or invalid document produces `role_document_invalid` and
   null/partial fields rather than a registry or dispatcher-derived role.
4. Let dispatcher exit reconciliation complete a partial envelope only from
   known runtime facts after worker failure or external termination. Unknown
   usage, cost, and worker measurements stay `null`, never zero or guessed.
5. Add a bounded read-only query under the established harness surface that
   filters/groups successful reconciled reviews by harness, model, role, stop
   reason, and raw thread-complexity dimensions. The query does not enrich the
   dispatcher report; that remains WI-5175 scope.
6. Keep telemetry-write errors observational: emit bounded diagnostic state but
   preserve the original verdict, process exit result, and dispatch outcome.

## Specification-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| V1 envelope | Assert required groups, schema ID, atomic replace behavior, and one current record per dispatch ID. |
| Turn/tool accounting | Simulate multiple provider turns and multiple tool calls in one turn; assert canonical names, total, and by-name counts. |
| Null semantics | Assert absent/partial provider usage, cache, and cost are null with coverage state, while directly observed zero stays zero. |
| Role authority | Supply a validated document role and a conflicting dispatcher intent; assert only the document role persists. Assert invalid/missing document yields `role_document_invalid`. |
| Stop reasons | Cover verdict, final response, max turn, no-progress, timeout, provider/guard/process errors, external termination, and role-document invalid. |
| Privacy | Scan serialized envelopes for prompt/message content, tool arguments/results, provider bodies, credentials, environment values, and free-form error details. |
| Failure isolation | Force telemetry-write failure and assert verdict, exit code, and existing stdout/stderr behavior are unchanged. |
| Reconciliation/query | Cover partial completion after worker termination and bounded successful-review distributions with filters/groupings. |

## Acceptance Criteria

- Every dispatched shim run leaves the approved v1 envelope or a reconciled
  partial envelope containing only known facts.
- Roles are document-derived; dispatcher intent cannot supply or override them.
- Unknown provider usage and cost are null, not fabricated as zero.
- The complete prohibited-content list is absent from persisted telemetry.
- A bounded distribution query makes real turns-used evidence available for
  future human decisions, without silently changing a turn budget or selection.
- Existing runtime and bridge outcome contracts remain intact when telemetry
  succeeds or fails.

## Risks / Rollback

- Risk: observability alters shim behavior. Mitigation: use a side-effect
  isolated observer and make write errors non-fatal; lock stdout/stderr and
  outcome compatibility in tests.
- Risk: provider payloads leak through a convenience serializer. Mitigation:
  construct envelopes from an allowlist of primitives and test forbidden
  content explicitly.
- Risk: dispatch routing is mistakenly used as role authority. Mitigation:
  require the worker document in the telemetry constructor and test conflicting
  intent.
- Risk: partial reconciliation fabricates data. Mitigation: represent unknowns
  as null with coverage and only merge known exit/runtime facts.
- Rollback: disable envelope persistence/query while leaving dispatch and shim
  behavior unchanged; no tuning or selection change requires reversal.
- Filing uses the next numbered bridge file under `bridge/` and remains
  append-only; no prior bridge file is rewritten or deleted.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py`

## Recommended Commit Type

`feat`
