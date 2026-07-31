NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# WI-5221 - Prime preclaim worker provenance implementation report

bridge_kind: implementation_report
Document: gtkb-wi5221-prime-preclaim-worker-provenance
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5221-prime-preclaim-worker-provenance-002.md
Approved proposal: bridge/gtkb-wi5221-prime-preclaim-worker-provenance-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5221-PRIME-WORKER-PROVENANCE-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5221
target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]
verified_include_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]
Recommended commit type: fix:

## Implementation Claim

The runtime now establishes a canonical dispatcher-composed worker session document for the exact Prime target and dispatch ID before any `go_implementation` claim in both direct runtime and daemon paths. Envelope failure is recorded as `worker_session_authority_failed`; no claim or worker launch occurs.

During claim acquisition, a scoped context removes an inherited parent `GTKB_HARNESS_NAME`, supplies the exact `GTKB_BRIDGE_POLLER_RUN_ID`, and restores both values in `finally`. This closes the residual cross-harness defect in which ambient Codex state caused a Claude/B claim to ignore the exact B envelope.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - headless role authority is dispatcher-composed and document-backed.
- `DCL-SESSION-ROLE-RESOLUTION-001` - the worker resolves the exact harness, role, and dispatch provenance.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - headless authority remains separate from interactive parent state.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - valid selected Prime work reaches the selected harness after claim acquisition.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - GO claims and bridge lifecycle remain canonical.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - worker envelopes and 29,400-second lifetimes remain consistent.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Prime-capable harnesses receive equivalent prelaunch authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - role and dispatch requirements were linked before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, WI, PAUTH, and exact targets remain linked.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification executes focused and full dispatcher regressions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the production correction remains distinct from fixture parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - WI, TEST-11375, PAUTH, bridge, source, and tests are linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the deterministic non-launch was governed before correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every envelope and changed path remains within `E:/GT-KB`.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of every defect discovered during genuine governed harness proof.
- No new owner decision is required.

## Prior Deliberations

- `DELIB-202666173` - genuine dispatcher proof and correction of discovered defects.
- `INTAKE-7073854a` - infrastructure owns deterministic worker identity and claim ordering.
- `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-004.md` - verified per-dispatch identity and reconciliation precedent.
- `bridge/gtkb-wi5221-prime-preclaim-worker-provenance-002.md` - Ollama D genuine governed GO.

## Specification-Derived Verification Plan

| Governing surface | Executed evidence | Observed result |
| --- | --- | --- |
| Session role authority, role resolution, isolation | `pytest ... -k wi5221` | 5 passed; exact B envelope fields, failure classification, runtime/daemon ordering, and parent-selector restoration verified. |
| Central dispatch and cross-harness parity | Full daemon module | 57 passed; ambient Codex parent state no longer blocks Claude/B Prime dispatch. |
| Bridge authority and fail-closed behavior | Focused WI-5221 tests plus full runtime module | 5 focused and 196 runtime tests passed; claim follows authority and failure branch continues before claim/spawn. |
| Envelope rules and generous allowances | Full daemon module and unchanged allowance constants | 57 passed; 29,400-second worker and 29,700-second lease contracts remain unchanged. |
| Specification/project linkage and artifact governance | WI-5221 proposal, GO, claim row 31270, packet `sha256:fd736be28152de0bf41cc3e83ccf8cf3454123be469f8199c93aa39d0abd784d` | Exact four-path authorization remained active during source edits. |
| Spec-derived full regression | Both modules together | 253 passed in one fresh process. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -k wi5221 -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/ruff.exe check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `git diff --check -- scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

## Observed Results

- Focused WI-5221: 5 passed, 248 deselected.
- Runtime module independently: 196 passed.
- Daemon module independently: 57 passed.
- Combined modules: 253 passed.
- Ruff check: all checks passed.
- Ruff format check: four files already formatted.
- Git diff check: exit 0; only expected Windows line-ending advisories.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

## Scope Separation

- WI-5217 Antigravity sidecar hunks in `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are not part of WI-5221.
- WI-5220 lease-import, eligibility, manual-provenance, lifetime, and stale assertion fixture hunks in both test modules are not part of WI-5221.
- Finalization must stage only WI-5221 hunks from the four verified include paths; no foreign worktree path or separately governed hunk is included.

## Acceptance Status

- PASS - exact Prime worker authority exists before every runtime and daemon claim.
- PASS - envelope failure acquires no claim and launches no worker.
- PASS - inherited interactive harness selectors cannot redirect cross-harness claim resolution.
- PASS - parent environment values are restored after scoped claim resolution.
- PASS - Prime fanout/quarantine and combined dispatcher regressions are green.
- PASS - LO leases, finalization, role registry authority, 29,400-second workers, and 29,700-second document leases are unchanged.

## Risk / Rollback

The scoped environment mutation lasts only for the synchronous registry call and restores prior values in `finally`. Rollback reverts the WI-5221 hunks in the four verified include paths.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
