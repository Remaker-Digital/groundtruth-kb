NEW

# WI-5392 implementation report: root-relative rehearsal fixture

bridge_kind: implementation_report
Document: gtkb-wi5392-rehearse-outside-root-fixture
Version: 003
Responds to GO: bridge/gtkb-wi5392-rehearse-outside-root-fixture-002.md
Approved proposal: bridge/gtkb-wi5392-rehearse-outside-root-fixture-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5392
Recommended commit type: test

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb

target_paths: ["platform_tests/scripts/test_rehearse_isolation.py"]

## Implementation Claim

The stale positive fixture now models an outside-legacy target relative to a
synthetic legacy root under governed `tmp_path` storage. It patches only the
imported rehearsal module's `LEGACY_ROOT` and `APPLICATIONS_NAMESPACE`
constants, asserts that the target is outside that synthetic root, and invokes
the unchanged production validator. Production code and every refusal fixture
remain unchanged. All scratch and generated evidence remains in-root under
`E:/GT-KB`; the bridge report resides under `E:/GT-KB/bridge`.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-GTKB-INDEPENDENT-TEST-SUITE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

`DELIB-202666274` supplies active Assurance project authority while preserving
the independent GO, claim, implementation-start, verification, and Git gates.
No new owner decision was required or inferred.

## Prior Deliberations

- `DELIB-20265227` - application-placement authority.
- `DELIB-202666274` - active Assurance project authorization.
- Owner directive, 2026-07-16 - repair modernization blockers while preserving
  the project-root boundary.

## Implementation Authorization Evidence

- Latest bridge status was `GO` at version 002.
- Claim row 31779 was acquired as `go_implementation` by Prime Builder session
  `A-2026-07-16T12-17-36Z`.
- A finalized schema-v3 named packet was issued with packet hash
  `sha256:5b53f1fd4534c364c5a25715c84d3c45b743055391f6255075015d8df23e5831`.
- Pre-start packet hash:
  `sha256:e2900a6ae1d8aac34375dd846527612f554f93f17a8e0a08e5deb62c2852190e`.
- Target validation returned `authorized: true` for exactly
  `platform_tests/scripts/test_rehearse_isolation.py`.

## Specification-Derived Verification

| Governing requirements | Executed evidence and observed result |
| --- | --- |
| Application placement and non-impairment | The positive case now uses a synthetic boundary while the complete 68-test rehearsal module, including all refusal cases, passes. Production source is unchanged. |
| Independent suite and evaluability | The sole target completed with `68 passed, 1 warning in 1.72s`; Ruff check, Ruff format check, and `git diff --check` pass. |
| Frozen acceptance contract | The exact 72-test activity was attempted and collected all tests, but the invoking wrapper terminated after the first displayed pass without a pytest summary. This report makes no whole-activity green claim. |
| Governance and lifecycle | Project PAUTH, claim row 31779, schema-v3 start packet, exact target validation, bounded diff, and this NEW report preserve the required handoff. |

## Commands Run And Observed Results

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=600`
   - `68 passed, 1 warning in 1.72s`.
2. `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_rehearse_isolation.py`
   - All checks passed.
3. `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_rehearse_isolation.py`
   - One file already formatted.
4. `git diff --check -- platform_tests/scripts/test_rehearse_isolation.py`
   - Exit zero.
5. Frozen `AT-AGENT-RED-PORTABILITY` command over both declared modules.
   - Collected 72 tests, then the command wrapper terminated after the first
     displayed pass and produced no final summary; it is not cited as green.

## Files Changed

- `platform_tests/scripts/test_rehearse_isolation.py` - corrected only
  `test_target_root_allowed_outside_legacy_root`.
- This implementation report is the only additional durable artifact.

No production source, dependencies, dispatcher, TAFE, harness, credential,
release, deployment, or Git-finalization state was changed.

## Acceptance Criteria Status

- [x] Positive fixture uses an explicit synthetic boundary under `tmp_path`.
- [x] Production application-placement code and constants are unchanged.
- [x] Complete rehearsal module, including refusal cases, passes.
- [x] Ruff and diff checks pass.
- [x] WI-5381 remains separate and is not masked or waived.
- [ ] Independent Loyal Opposition verification remains pending.
- [ ] Git finalization remains separately gated.

## Risk And Rollback

The remaining verification risk is the incomplete whole-activity wrapper run.
The complete directly affected module is green and the report does not infer a
result for the other activity module. Rollback is the one test hunk through a
governed successor.

## Loyal Opposition Asks

Independently rerun the complete rehearsal module and frozen portability
activity, confirm the synthetic target is outside the patched legacy root,
confirm all refusal cases remain green, and return VERIFIED only if the bounded
fixture repair satisfies the cited contracts.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
