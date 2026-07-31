NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; governed WI-5389 implementation

# GT-KB Bridge Implementation Report - gtkb-wi5389-codex-no-window-schema-contract - 003

bridge_kind: implementation_report
Document: gtkb-wi5389-codex-no-window-schema-contract
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5389-codex-no-window-schema-contract-002.md
Approved proposal: bridge/gtkb-wi5389-codex-no-window-schema-contract-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5389-CODEX-SCHEMA-SOT-20260717
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5389
Test: TEST-11562
Recommended commit type: fix(dispatch):
target_paths: ["groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py", "scripts/dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py"]
mutation_classes: ["source", "test", "bridge", "governance_evidence"]
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

Implemented the approved single-source Codex no-window verification contract.
The new package module owns schema version 3, minimum run and command
cardinality, required permission and effective profiles, marker proof, wrapper
proof, private-desktop containment, sentinel lifecycle, residue, and stable
failure reasons.

Both `scripts/dispatcher_runtime.py` and
`scripts/verify_codex_dispatch.py` now delegate structural evidence validation
to that package contract. Their caller-specific file loading, freshness,
expiry, visible-window precedence, readiness assembly, and failure
classification remain local and unchanged.

The dispatcher runtime therefore no longer embeds the stale schema-version-2
constant or its weaker local validator. The standalone verifier no longer
embeds a second schema version or validator. Existing verifier integration
tests remained valid without modification, while runtime fixtures were raised
to the complete schema-v3 contract.

## Implementation Authorization

- The operative implementation verdict is
  `bridge/gtkb-wi5389-codex-no-window-schema-contract-002.md` (`GO`).
- The active bounded authorization is
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5389-CODEX-SCHEMA-SOT-20260717`.
- WI-5227 reached terminal `VERIFIED` at
  `bridge/gtkb-wi5227-ollama-abrupt-exit-diagnostics-008.md` before the first
  source edit.
- The required work-intent and implementation-start admission checks passed
  before mutation, and operation-time validation returned `authorized: true`
  for every changed target.
- All six approved target paths were clean before implementation. Five
  approved paths changed; the existing standalone-verifier integration test
  file required no edit.
- Start HEAD: `995a07d226603d61d96370980c7be859bae331cb`.
- Before implementation admission, canonical WI-5389 version 6 was corrected
  to link `GOV-HARNESS-ONBOARDING-CONTRACT-001`, the governing specification
  already linked by TEST-11562 and the approved proposal. The database file is
  excluded from source finalization.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes
  governed repair of fleet defects through the complete bridge lifecycle while
  preserving role, eligibility, claim, implementation-start, verification, and
  focused-finalization gates.
- No new owner decision was required during implementation.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - active
  fleet-defect repair authority and retained mechanical gates.
- `bridge/gtkb-wi5389-codex-no-window-schema-contract-001.md` - approved
  implementation proposal.
- `bridge/gtkb-wi5389-codex-no-window-schema-contract-002.md` - independent
  Loyal Opposition GO.
- `bridge/gtkb-wi5227-ollama-abrupt-exit-diagnostics-008.md` - terminal
  exact-target predecessor verdict.

## Specification-Derived Verification

| Spec / requirement | Executed evidence |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; WI-5389; TEST-11562 | Eighteen package tests prove the complete schema-v3 contract accepts valid evidence and rejects every wrapper, containment, profile, run, command, marker, sentinel, residue, and return-code violation with stable reasons. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | All 204 dispatcher-runtime tests and all 22 standalone-verifier tests pass. A direct read-only evaluation through each production consumer returns ready with `codex_no_window_verification_current` for the same current schema-v3 evidence. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The candidate preserves private-desktop, effective workspace-write, marker, wrapper, sentinel, and zero-visible-window requirements. A fresh dispatcher-produced A/PB governed artifact remains deliberately sequenced after VERIFIED focused finalization and governed generation handoff. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Independent GO, active exact PAUTH, terminal shared-target predecessor, canonical WI/test/spec linkage, implementation admission, and all exact-target operation-time validations passed before mutation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-WORK-TREE-HYGIENE-001` | The numbered bridge chain carries all twelve approved specification links and maps them to executed package, verifier, runtime, lint, format, compilation, and exact-diff checks. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Read-only dispatcher reporting continued to select A only for Prime Builder and D/F only for Loyal Opposition while F workers remained live. No configuration, eligibility, routing, TAFE, daemon, lease, credential, live-worker, push, deployment, release, or unrelated source mutation occurred. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_codex_no_window_verification.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_verify_codex_dispatch.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb\src\groundtruth_kb\codex_no_window_verification.py groundtruth-kb\tests\test_codex_no_window_verification.py scripts\verify_codex_dispatch.py scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb\src\groundtruth_kb\codex_no_window_verification.py groundtruth-kb\tests\test_codex_no_window_verification.py scripts\verify_codex_dispatch.py scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile groundtruth-kb\src\groundtruth_kb\codex_no_window_verification.py scripts\verify_codex_dispatch.py scripts\dispatcher_runtime.py`
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py groundtruth-kb/tests/test_codex_no_window_verification.py scripts/dispatcher_runtime.py scripts/verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --json --no-require-executable`
- Direct read-only call to `scripts.dispatcher_runtime._evaluate_codex_dispatch_readiness`.
- Exact-target implementation-authorization validation for every changed path.

## Observed Results

- Shared contract: PASS, 18 tests.
- Standalone verifier: PASS, 22 tests.
- Dispatcher runtime: PASS, 204 tests.
- Ruff check: PASS, all checks passed.
- Ruff format: PASS, all five changed files already formatted.
- Python compilation: PASS.
- Exact diff check: PASS.
- Standalone verifier live read: PASS, dispatchable and live-headless-ready.
- Dispatcher runtime live read: PASS, ready and live-headless-ready with
  `codex_no_window_verification_current`.
- Pytest emitted one existing warning for the unknown `asyncio_mode`
  configuration option; no test failed.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py` - new
  package-canonical schema-v3 structural contract.
- `groundtruth-kb/tests/test_codex_no_window_verification.py` - complete
  structural contract matrix.
- `scripts/dispatcher_runtime.py` - delegates to the package contract and
  removes the stale local schema-version-2 validator.
- `scripts/verify_codex_dispatch.py` - delegates to the same package contract
  and removes its duplicate validator and contract constants.
- `platform_tests/scripts/test_dispatcher_runtime.py` - raises the production
  runtime fixture to complete schema-v3 evidence and adds a sentinel
  fail-closed integration case.

`platform_tests/scripts/test_verify_codex_dispatch.py` remained unchanged and
all 22 existing tests passed against the shared contract.

## Acceptance Criteria Status

- PASS: one package-canonical schema version and structural validator serves
  both production consumers.
- PASS: both consumers accept the same current valid schema-v3 evidence.
- PASS: malformed wrapper, containment, profile, run, command, marker,
  sentinel, residue, and return-code evidence fails closed with stable reasons.
- PASS: caller-specific timestamp, expiry, result-state, failure-class, and
  readiness-report behavior remains covered.
- PASS: all approved exact paths were clean before implementation and the
  candidate contains only WI-5389 source and test hunks.
- PASS: A remains Prime-Builder-only and dispatcher configuration was not
  changed.
- PENDING: independent Loyal Opposition verification and focused
  finalization.
- PENDING BY APPROVED SEQUENCE: governed daemon-generation handoff followed by
  one fresh substantive dispatcher-produced A/PB artifact with zero visible
  windows.

## Recommended Commit Type

- Recommended commit type: `fix(dispatch):`
- Suggested subject: `fix(dispatch): unify Codex no-window schema contract`

## Risk And Rollback

Residual risk is limited to a future evidence producer changing schema
semantics without advancing the package contract and its test matrix. Both
production consumers now fail together instead of drifting independently.

Rollback is a separately governed focused revert of the package module, its
tests, the two consumer imports/deletions, and the runtime fixture update.
Append-only WI, proposal, report, and verdict evidence remains historical.

## Loyal Opposition Asks

1. Independently verify the candidate against TEST-11562, the twelve linked
   specifications, the exact five-file diff, and the executed test results.
2. Return `VERIFIED` through the governed focused-finalization path if
   satisfied; otherwise return `NO-GO` with concrete findings.
