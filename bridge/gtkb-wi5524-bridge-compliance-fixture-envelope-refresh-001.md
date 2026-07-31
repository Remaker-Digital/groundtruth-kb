NEW
::init gtkb lo
::open build

# WI-5524 Bridge-Compliance Fixture Envelope Refresh

bridge_kind: prime_proposal
Document: gtkb-wi5524-bridge-compliance-fixture-envelope-refresh
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; governed implementation proposal

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5524

target_paths: ["platform_tests/hooks/test_bridge_author_metadata_gate.py", "platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py", "platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", "platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py", "platform_tests/hooks/test_bridge_compliance_gate_prior_deliberations.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py", "platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py", "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py", "platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Refresh twelve clean bridge-compliance test modules so status-bearing synthetic
artifacts satisfy the mandatory line-1 status and line-2/3 responder/activity
envelope before each test evaluates its intended downstream governance clause.
Use the governed production envelope normalizer for fixture construction where
practical, and isolate unrelated earlier or later checks only within the test
fixture. Do not weaken, reorder, or bypass the production gate.

The focused baseline collects 176 tests: 79 pass and 97 fail. Ninety-five
failures stop at the artifact-head envelope before reaching their named clause.
Two additional failures assert the pre-cutover implementation-kind set and omit
the currently governed `prime_implementation_proposal` token. This proposal
updates those fixture assumptions while preserving the fail-closed production
contract.

Explicitly out of scope are production hook changes, active/template hook
content, dirty non-impairment fixtures, Codex or harness configuration parity,
WI-5438 verdict-anchor work, aggregate queue compatibility tests, dispatcher or
TAFE state/configuration, runtime leases, and database mutation.

## Inventory And Review Packet

The bounded inventory artifact is the focused execution of the twelve declared
modules: 176 tests collected, 79 passed, and 97 failed. This proposal is the
review packet for that exact inventory and maps each declared target to the
same linked test obligation, TEST-11590.

DECISION DEFERRED: dirty non-impairment fixtures, Codex/configuration parity,
WI-5438 verdict-anchor fixtures, and aggregate compatibility tests remain in
their own governed work streams. They are not adopted, modified, or used to
justify this implementation.

## Specification Links

- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` - status-bearing bridge artifacts
  expose the responder role and activity immediately after the status token.
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` - the governed writer
  derives the responder line, validates activity, and fixes the envelope at
  lines 2 and 3.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only bridge governance and
  independent review remain mandatory; test repair does not relax bridge
  authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  names every governing requirement and verifies that compliant proposal
  fixtures still traverse specification-linkage enforcement correctly.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project-linkage tests
  must reach their own clause after satisfying the earlier envelope contract.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - membership fixtures
  must remain hermetic and preserve every active, missing, excluded, inactive,
  and expired authorization outcome.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED fixtures retain
  specification-to-test and executed-command evidence requirements.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the correction preserves
  intuitive fixture intent and cannot trade away a production denial to make a
  test pass.
- `GOV-STANDING-BACKLOG-001` - the broad WI-5445 diagnostic was durably
  captured as WI-5524 and linked TEST-11590 rather than hidden.
- `GOV-WORK-TREE-HYGIENE-001` - only the twelve declared clean targets may be
  changed; dirty parallel-session files remain untouched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, test obligation,
  proposal, implementation report, and verification remain linked governed
  artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - implementation starts only after
  independent GO, a matching claim, and implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this bounded remediation preserves
  canonical evidence and excludes ephemeral or retired surfaces.

## Prior Deliberations

- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS` selected
  responder-role semantics: NEW/REVISED/NO-ACTION route to LO and
  GO/NO-GO/VERIFIED route to PB.
- `DELIB-20260716-ENVELOPE-GRILL-B2-LINE-AUTHORING-AUTHORITY` selected
  writer-derived responder lines and closed-vocabulary activity validation.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` kept the status
  token on line 1 and fixed the envelope at lines 2 and 3.
- `DELIB-20260717-ENVELOPE-LEGACY-ROUTING-MIGRATION-POLICY` selected the
  thread-ratchet migration and prohibits rewriting historical artifacts merely
  to backfill envelopes.
- `DELIB-202666851` records the adjacent lesson that a one-time fixture refresh
  without a drift-resistant construction path recurs; this proposal therefore
  reuses the governed normalizer instead of duplicating envelope literals where
  practical. Its separate scaffold-golden work remains out of scope.

## Owner Decisions / Input

No new owner decision is required to request review. WI-5524 is an open P1
hygiene item under the active project authorization, and the standing backlog
governance authorizes preservation of the diagnosed defect. This filing is not
implementation approval: independent GO, a matching claim, implementation-start
authorization, independent VERIFIED, and a focused commit remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. The artifact-head ADR/DCL define the exact
fixture prerequisite, the linked clause specifications define the outcomes that
must remain observable, and TEST-11590 defines the integration acceptance
result. No new production behavior or requirement is introduced.

## Implementation Plan

1. Normalize synthetic NEW, REVISED, NO-ACTION, GO, NO-GO, and VERIFIED fixture
   bodies through the governed envelope constructor so each body carries the
   correct responder and default activity at fixed lines 2 and 3.
2. Keep intentionally malformed envelope cases exclusively in the dedicated
   envelope-head tests, which are outside this target set.
3. Where a test targets a late gate, isolate unrelated live membership,
   self-review, evidence-anchor, or preflight dependencies with narrowly scoped
   monkeypatches that are restored even when the tested path raises.
4. Update the requirement-sufficiency token-set assertion to include the
   governed `prime_implementation_proposal` token; do not remove existing
   accepted tokens.
5. Preserve all negative assertions and require their named denial token or
   message, so an unexpected earlier denial cannot satisfy the test.
6. Leave production hooks, templates, dispatcher configuration, runtime state,
   database state, and every undeclared dirty path byte-for-byte unchanged.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`; `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_author_metadata_gate.py platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py platform_tests/hooks/test_bridge_compliance_gate_prior_deliberations.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py -q --tb=short` | All 176 focused tests pass; malformed and incomplete artifacts still produce their intended fail-closed denials. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb/.venv/Scripts/ruff.exe check <the twelve declared target files>` and `groundtruth-kb/.venv/Scripts/ruff.exe format --check <the twelve declared target files>` | Both commands pass with no production or undeclared file mutation. |
| `GOV-WORK-TREE-HYGIENE-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Scoped before/after `git status --short -- <the twelve declared target files>` plus production-hook SHA-256 readback | Only declared test files change; active/template hook bytes and hashes remain unchanged. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO review of the focused diff and executed evidence | VERIFIED only if each test reaches its named clause and no denial behavior is weakened. |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5524, TEST-11590, and the focused 176-test baseline executed by Prime Builder Codex A",
  "canonical_authority": "ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001; DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "groundtruth-kb/.venv/Scripts/python.exe -m pytest against the twelve declared fixture modules",
  "before_behavior": "97 of 176 focused tests fail; 95 stop at the mandatory envelope before their named clause and 2 assert a stale implementation-kind token set",
  "after_behavior": "all 176 focused tests reach and preserve their named governance-clause outcomes under the current envelope and implementation-kind contracts",
  "self_descriptive_naming": "existing test names continue to identify the exact downstream denial, allowance, membership, provenance, evidence, or sufficiency behavior",
  "obsolete_guidance_disposition": "replace stale synthetic fixture construction and token expectations only; production enforcement and historical bridge artifacts are unchanged",
  "history_preservation": "the governed WI, linked test, append-only proposal chain, implementation report, independent verdict, and focused commit preserve the correction history",
  "baseline": {
    "collected": 176,
    "passed": 79,
    "failed": 97,
    "declared_target_files": 12
  },
  "expected_result": {
    "collected": 176,
    "passed": 176,
    "failed": 0,
    "production_hook_files_modified": false
  },
  "rollback": "revert only the focused test-fixture commit; production hook behavior requires no rollback because it is not modified",
  "hard_invariants": [
    "status remains line 1",
    "responder and activity remain fixed at lines 2 and 3",
    "negative tests assert their intended denial",
    "active and template production hooks remain byte-identical and untouched"
  ],
  "fail_closed_conditions": [
    "an unexpected earlier denial satisfies a test",
    "a production gate or template is changed",
    "a dirty or undeclared path enters the diff",
    "the focused suite has any failure"
  ],
  "essential_context_preservation": "fixture helpers keep status, metadata, project linkage, specification links, verdict evidence, and intended clause variables visible in each test"
}
```

## Risk / Rollback

The main risk is over-isolation: a monkeypatch could hide the very clause a test
is meant to verify. Mitigate by scoping substitutions to unrelated gates,
restoring them in `finally` blocks or pytest-managed monkeypatch lifetimes, and
asserting the exact intended denial token. A second risk is collision with
parallel changes; any target that becomes dirty or claimed before
implementation must be removed through a reviewed revision or deferred.

Rollback is a single focused test-only commit revert. No production source,
configuration, dispatcher state, runtime lease, database row, deployment, or
release action is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
file for `gtkb-wi5524-bridge-compliance-fixture-envelope-refresh`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test(bridge)`: the implementation updates only governed test fixtures and
their assertions while preserving production behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
