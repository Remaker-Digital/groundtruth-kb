REVISED

# WI-5222 Current-HEAD Verification and Finalization Correction

bridge_kind: implementation_report
Document: gtkb-wi5222-60-minute-generous-dispatch-envelope-successor
Version: 005
Responds to: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-004.md
Approved proposal: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-001.md
GO verdict: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-002.md
Prior implementation report: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-successor-003.md
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5222
Test: TEST-11376
target_paths: [".api-harness/routing.toml", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_lo_harness_turn_budget.py"]

implementation_scope: current_head_verification_and_finalization_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

## Revision Claim

The version-004 NO-GO had two blockers: four failures in the exact seven-module
verification command on its then-current HEAD, and the absence of the canonical
disposable-index finalizer. Both premises are now obsolete.

On current HEAD `42a252ab`, the owner-calibrated values are committed and all
nine proposal paths are clean. D/F/H use 900-second operations, 3,600-second
sessions, and 600 turns; the shared worker lifetime is 4,200 seconds; lease and
reset derivation is 4,500 seconds. The exact seven-module command now collects
515 tests and passes every one. The committed VERIFIED finalizer creates a
HEAD-seeded disposable index and tolerates unrelated shared-index dirt.

No implementation byte changed in this revision. It supersedes only the stale
verification/finalization instructions in version 003 and asks Loyal
Opposition to evaluate the current committed implementation directly.

The retained historical patch
`bridge/hunks/gtkb-wi5222-60m-envelope-successor-current-head.patch` is not
valid finalization evidence: its stored length is 10,058 bytes rather than the
10,079 bytes claimed by version 003, and `git apply --check` fails as corrupt
at line 134. This revision explicitly excludes that artifact from terminal
evidence and finalization. The systemic exact-byte/applicability gate is
separately tracked by hygiene work item WI-5401 and linked TEST-11512.

## Specification Links

- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` controls the numeric
  policy and accepts the bounded historical outliers.
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` carries the earlier
  generous-envelope and provider-recovery direction.
- Version 002 is the independent OpenRouter F GO for the successor proposal.
- Version 004 is the independent Ollama D NO-GO whose exact current-HEAD test
  and finalizer findings this revision addresses.
- WI-5236 owns the historical current-HEAD fixture drift; its four failures no
  longer reproduce in the exact WI-5222 verification command.
- WI-5401 / TEST-11512 owns the newly proven malformed retained-patch defect.

## Owner Decisions / Input

No new owner decision is required. The owner already selected the 60-minute
model window, 900-second operation limit, 600-turn budget, 600-second
session-to-worker margin, and 300-second worker-to-lease/reset margin. This
revision performs no routing, role, model, eligibility, dispatcher, TAFE,
lease, runtime, source, test, credential, Git staging, push, deployment,
release, or destructive-cleanup mutation.

## Findings Addressed

### F1 - Exact prescribed suite failed on current HEAD

Response: resolved by current committed state. The exact command from versions
001 and 003 now collects 515 tests and exits 0 with `515 passed, 1 warning in
171.38s`. The sole warning is the pre-existing unknown `asyncio_mode` option.
The four named failures from version 004 all pass.

### F2 - Canonical disposable-index finalizer was unavailable

Response: resolved. `.claude/skills/verify/helpers/write_verdict.py` is tracked
and clean at `42a252ab`. Its `finalize_verified_commit` creates a temporary
`GIT_INDEX_FILE`, reads HEAD, stages only the exact include set and verdict,
checks the temporary staged set, commits it, and realigns the shared index.
Unrelated shared-index paths are explicitly tolerated and cannot be captured.

### F3 - Version 003 hunk artifact cannot support finalization

Response: removed from this terminal request. The exact current implementation
is already committed and clean, so no hunk application is needed. The malformed
artifact is preserved as evidence for WI-5401 rather than silently trusted,
rewritten, deleted, or passed to the finalizer.

## Scope Changes

No implementation scope change and no source/test change. The terminal review
uses the five paths that contain the committed WI-5222 policy values. The four
additional proposal test modules remain part of the exact executed suite but
carry no WI-5222 implementation delta.

## Pre-Filing Preflight Subsection

- Applicability preflight: executed against this completed pending content;
  PASS with no missing required or advisory specifications.
- Mandatory clause preflight: executed against this completed pending content;
  PASS with zero blocking gaps.
- Exact current-HEAD target status: PASS; all nine proposal paths are clean.
- Historical hunk artifact: FAIL as terminal evidence; excluded and tracked by
  WI-5401 / TEST-11512.

## Spec-to-Test Mapping

| Specification / contract | Current executed evidence | Result |
| --- | --- | --- |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Routing values plus runtime/daemon/budget assertions for 900 / 3,600 / 600 / 4,200 / 4,500 | PASS |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_dispatcher_runtime.py` and `test_gtkb_dispatcher_daemon.py` | PASS |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Cloud base, Alibaba H, Ollama D, OpenRouter F, runtime, daemon, and budget modules together | PASS |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Provider routing and turn-budget assertions | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | Exact nine-path status is clean; malformed old patch is excluded and separately governed | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact seven-module pytest plus Ruff check and format check | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Numbered 001-005 chain, independent GO, current report, and independent terminal review request | PASS pending LO verdict |

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py
git status --short -- <the nine approved proposal paths>
git apply --check bridge/hunks/gtkb-wi5222-60m-envelope-successor-current-head.patch
```

## Observed Results

- Pytest: `515 passed, 1 warning in 171.38s`; exit 0.
- Ruff check: `All checks passed!`; exit 0.
- Ruff format check: `8 files already formatted`; exit 0.
- Exact nine-path status: clean.
- Current values: D/F/H session timeout 3,600; worker lifetime 4,200;
  lease/reset threshold 4,500.
- Historical patch check: exit 1, `corrupt patch at line 134`; excluded from
  this report's positive evidence and preserved for WI-5401.

## Files Changed

No implementation file changed in this revision. The committed implementation
reviewed for terminal disposition is:

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`

## Acceptance Criteria Status

- PASS: D/F/H resolve to 900-second operations, 3,600-second sessions, and 600 turns.
- PASS: A/B/C/D/F/H default workers resolve to 4,200 seconds.
- PASS: session-to-worker and worker-to-lease/reset margins resolve to 600 and 300 seconds.
- PASS: all 515 tests in the prescribed current-HEAD suite pass.
- PASS: Ruff and formatting checks pass.
- PASS: all nine approved proposal paths are tracked and clean.
- PASS: the canonical isolated finalizer is tracked and clean.
- PASS: the malformed historical patch is not used as positive evidence.

## Requested Loyal Opposition Action

Independently rerun or evaluate the current-HEAD evidence. If the committed
policy and tests satisfy the linked specifications, issue terminal VERIFIED
without applying the malformed historical hunk artifact. Finalization must be
focused on this correction/verdict chain and must not capture unrelated shared
worktree or index paths.

## Risk And Rollback

The revision changes no executable behavior. The principal risk is accepting
current HEAD without the historical patch; that is bounded by direct clean-path
inspection, exact numeric assertions, the full 515-test suite, and independent
review. A failed premise must produce NO-GO. Rollback of this bridge correction
is append-only; no source or runtime rollback is required.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
