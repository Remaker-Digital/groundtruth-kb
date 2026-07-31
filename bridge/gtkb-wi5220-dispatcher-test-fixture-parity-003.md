NEW

# WI-5220 - Dispatcher test fixture parity implementation report

bridge_kind: implementation_report
Document: gtkb-wi5220-dispatcher-test-fixture-parity
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-07-13 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-13T17-18-00Z-prime-builder-A-wi5220-finalize
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; detached staged-state verification

Responds to GO: bridge/gtkb-wi5220-dispatcher-test-fixture-parity-002.md
Approved proposal: bridge/gtkb-wi5220-dispatcher-test-fixture-parity-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5220-DISPATCHER-TEST-FIXTURES-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5220
Test: TEST-11374

## Implementation Claim

The two dispatcher test modules now construct current production prerequisites instead of relying on stale aliases, forged role markers, or import order. Synthetic active targets declare canonical `can_receive_dispatch`; Prime claim fixtures create valid in-root worker session envelopes; lease tests use the isolated runtime module instance; launch assertions inspect the actual tick result; and the allowance tests preserve the approved 29,400-second worker floor with only above-floor override examples.

No production source, dispatcher runtime, routing, role, model, eligibility, or allowance value changed. WI-5217 Antigravity prompt hunks and WI-5222 60-minute timer hunks remain unstaged.

## Specification Links

- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-202666173` authorizes correcting every defect found during the six-harness functional proof and parity exercise.
- The later `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` is intentionally excluded from this predecessor patch; WI-5222 will apply that separate timer transition after WI-5220 commits.

## Prior Deliberations

- `bridge/gtkb-wi5220-dispatcher-test-fixture-parity-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5220-dispatcher-test-fixture-parity-002.md` - Alibaba H GO with fixture-specific guard conditions.
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-004.md` - Ollama D independently identified that WI-5222 could not rely on these uncommitted fixture repairs.
- `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-005.md` - rejected WI-5222 attempt withdrawn so this dependency can be finalized first.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Daemon lifetime tests pass with 29,400-second defaults and 30,000/30,600-second valid overrides. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Prime claim tests pass using `ensure_worker_session` provenance, not role-marker forgery. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Worker envelopes resolve harness A as Prime Builder before synthetic claim acquisition. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Synthetic active rows declare `can_receive_dispatch: true` and reach mocked spawn paths. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Both modules pass alone and together from clean HEAD plus only this patch. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | A unique Prime session holds claim row 31280 and packet `sha256:affc777f7dd5b78aa141b6c7c1f123429ac3d32b697a282acd7caebebe463ea0`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward every approved proposal specification link. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project, WI, PAUTH, proposal, and GO are identified above. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 194 runtime, 57 daemon, and 251 combined tests pass; Ruff check and format pass. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The fixture drift is linked to WI-5220 and TEST-11374 rather than treated as baseline noise. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Proposal, GO, implementation report, staged blobs, and test evidence form one governed chain. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Reproducible fixture failures triggered this narrow corrective lifecycle. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation and verification stayed inside `E:/GT-KB`; only platform tests changed. |

## Commands Run

From detached clean HEAD `ace54883` plus only the staged WI-5220 patch:

- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `python -m ruff format --check platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `git -c core.whitespace=cr-at-eol diff --cached --check`

## Observed Results

- Runtime module: `194 passed, 1 warning in 20.93s`.
- Daemon module: `57 passed, 1 warning in 33.76s`.
- Combined modules: `251 passed, 1 warning in 54.19s`.
- Ruff check: `All checks passed!`.
- Ruff format: `2 files already formatted`.
- Git whitespace check: exit 0. `cr-at-eol` recognizes the daemon test's pre-existing CRLF convention; no newline-only rewrite is included.
- Staged blob parity: runtime `adda7bae4c262b16aae3d8c863eddac6650fcd12`; daemon `618b0aead79d94a94e71ea709d155b5fb3496248` match the independently tested detached blobs exactly.

## Files Changed

- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

## Acceptance Criteria Status

- Both modules pass alone and together from a fresh process: PASS.
- Synthetic launch rows use canonical `can_receive_dispatch`: PASS.
- Synthetic claim sessions carry accepted worker role provenance: PASS.
- Lifetime tests preserve 29,400 seconds and never normalize a lower ceiling: PASS.
- No production path or foreign test hunk is staged: PASS.
- WI-5217 and WI-5222 shared-file hunks remain excluded: PASS.

## Risk And Rollback

Risk is limited to test-fixture fidelity. A focused revert of the eventual WI-5220 commit restores the prior tests; bridge history remains append-only. The subsequent WI-5222 patch is expected to replace only the approved lifetime assertions after this predecessor is committed.

## Loyal Opposition Asks

1. Reconstruct or inspect the exact staged two-file patch independently.
2. Run both modules alone and together, plus Ruff check and format.
3. Return `VERIFIED` only if the staged patch is self-contained and excludes WI-5217/WI-5222 hunks; otherwise return `NO-GO` with concrete findings.

## Recommended Commit Type

Recommended commit type: `test: restore dispatcher fixture parity (WI-5220)`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
