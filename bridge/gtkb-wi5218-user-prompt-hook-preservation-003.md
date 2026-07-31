NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Post-Implementation Report - WI-5218 UserPromptSubmit preservation

bridge_kind: implementation_report
Document: gtkb-wi5218-user-prompt-hook-preservation
Version: 003
Date: 2026-07-12 UTC
Approved proposal: bridge/gtkb-wi5218-user-prompt-hook-preservation-001.md
GO verdict: bridge/gtkb-wi5218-user-prompt-hook-preservation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5218-USER-PROMPT-HOOK-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5218

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

implementation_scope: source
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

WI-5218 is implemented in the exact three approved paths. `UserPromptSubmit` execution timeout, nonzero exit, malformed JSON, and non-object informational output now continue fail-soft while retaining the original user prompt and running later registered enrichment hooks. Empty output remains the pre-existing no-op. Valid explicit block output still raises before provider invocation. PreToolUse, guard-adapter, SessionStart, PostToolUse, Stop, dispatcher, routing, registry, and all generous limits are unchanged.

## Governed Authority And Independent GO

- Owner decision: `DELIB-202666173`.
- PAUTH: `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5218-USER-PROMPT-HOOK-20260712`.
- Prime claim row: `31256`, acquired `2026-07-12T23:25:53Z` by session `019f5474-93a6-7f70-8e54-d6d8b0a31bb4`.
- Implementation packet: `sha256:f126e91c1692dafefe0241691226bb43bfa7e2e6ecf5aeacf44edf1a5f790ef8`, expires `2026-07-13T01:25:58Z`.
- Independent GO: `bridge/gtkb-wi5218-user-prompt-hook-preservation-002.md`, authored by Ollama D in dispatcher session `2026-07-12T23-01-09Z-loyal-opposition-D-b32163`.
- Genuine D run: 91/600 turns, 112 tool calls, four `PublishBridgeVerdict` calls, final canonical GO, `stop_reason=verdict_emitted`, exit 0, zero stderr, exact-once ledger reconciliation and lease release.

## Implementation Details

- Added a `user_prompt_event` classification to the shared native hook executor and included it in the existing fail-soft execution-outcome branch used by non-mutating lifecycle maintenance.
- Timeout and nonzero execution outcomes now continue to later UserPromptSubmit hooks.
- Malformed and non-object informational output now continue without replacing the prompt.
- Empty output remains the existing unconditional `continue`; no new special case was added.
- Valid object output remains available as `last_output`.
- Valid output containing a block reason remains fail-closed through the existing `CloudHarnessError` path before provider invocation.
- Configuration-contract failures remain fail-closed because settings parsing, registration validation, hook type validation, and timeout validation occur outside the new execution-outcome branch.

## Exact Diff Attribution

The three targets were clean before implementation. HEAD blob IDs:

- `scripts/cloud_harness_base.py`: `2e27c95a898b374ca489b48a168a41dae72576af`
- `platform_tests/scripts/test_cloud_harness_base.py`: `26d29877b9d27a83597cc3a412f2a7406f1dcc70`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`: `c78e12becbad473bb4c8b7903b7e9075baac6028`

Current scoped numstat is 6 insertions/4 deletions in shared source, 83 test insertions in the shared suite, and 42 test insertions in the Alibaba suite. `git diff --check` is clean apart from informational Windows LF-to-CRLF notices. No foreign hunk or owner waiver is required for these targets.

## Commands Executed And Observed Results

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short` -> 98 passed, one existing unknown-`asyncio_mode` warning.
- Combined four-provider command over cloud base, Alibaba, OpenRouter, and Ollama suites -> 217 passed, one existing warning.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` -> 163 passed, two existing warnings.
- Canonical writer plus VERIFIED atomicity suites -> 40 passed, one existing warning.
- Dispatcher lifetime selection for worker lifetime profile, target lifetime forwarding, and document lease TTL -> 9 passed, 181 deselected, one existing warning.
- Ruff check on the three targets -> all checks passed.
- Ruff format check on the three targets -> three files already formatted.
- `git diff --check` on the three targets -> clean, with informational line-ending notices only.
- Applicability preflight -> `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Mandatory clause preflight -> exit 0, zero must-apply evidence gaps, zero blocking gaps.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Verification Mapping

| Specification | Test or evidence | Expected | Observed |
| --- | --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Fresh D GO run and required fresh H report review | Genuine assigned-role governed work | D succeeded; H verification requested on this report |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Shared parameterized lifecycle tests | Shared native-full behavior | timeout/nonzero/malformed/non-object and later-hook continuation pass |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | Alibaba original-prompt integration test | H provider sees original prompt after timeout | passed |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Writer and atomicity suites | No publication authority change | 40 passed |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Existing publisher metadata tests in provider suites | Trusted metadata retained | 217-provider suite passed |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Dispatcher lifetime selection | 600/900/28800/29400/29700 unchanged | focused lifetime tests passed; D launch telemetry confirms values |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | PreToolUse and implementation-start guard suites | Mutating authorization remains fail-closed | provider and 163-gate suites passed |
| Cross-harness parity carriers | Combined four-provider suite | No F/D/shared regression | 217 passed |
| Proposal/verification linkage carriers | Both mandatory preflights | No missing or blocking evidence | clean |
| Artifact lifecycle carriers | WI-5218, TEST-11372, PAUTH, proposal, GO, report | Durable defect graph | complete through verification request |
| Isolation placement | Exact target list and root checks | All work in GT-KB platform root | passed |

## GO Findings Disposition

- **P3 empty output:** confirmed as pre-existing unconditional no-op; implementation does not add a redundant event branch.
- **P3 explicit block:** retained as fail-closed `CloudHarnessError`, which prevents provider invocation. A dedicated test asserts the exact block reason. Returning a block object is unnecessary because the UserPromptSubmit caller does not consume a block decision; raising is the existing effective enforcement path.
- **Hunk interleave:** none in the three WI-5218 targets at implementation start.

## Acceptance Criteria Status

- PASS: UserPromptSubmit execution failures cannot discard or replace the original prompt.
- PASS: later registered enrichment hooks execute after maintenance failure.
- PASS: valid explicit block output prevents provider invocation.
- PASS: PreToolUse and guard failures remain fail-closed.
- PASS: PostToolUse and Stop behavior remains unchanged.
- PASS: generous turn/operation/session/worker/lease limits remain unchanged.
- PENDING INDEPENDENT CHECK: fresh H review of this report must reach provider turns and publish VERIFIED or expose another governed defect.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of every defect discovered during the six-harness proof goal.
- No additional owner waiver is used; target files were clean and exactly scoped.

## Prior Deliberations

- `DELIB-202666173` - complete six-harness governed proof and correct every discovered defect.
- `DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION` - native-hook empty-output predecessor.
- `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-004.md` - Stop event preservation predecessor.
- `bridge/gtkb-wi5213-posttooluse-completion-preservation-004.md` - PostToolUse event preservation predecessor.

## Risk And Rollback

Residual risk is limited to an informational UserPromptSubmit hook silently losing enrichment when it fails; the original prompt remains available and configuration defects plus explicit blocks remain fail-closed. Rollback reverts the three source/test targets. Bridge and MemBase evidence remains append-only.

## Loyal Opposition Verification Request

Re-run the mapped tests and both mandatory preflights, inspect the exact three-path diff, and verify through this genuine H-dispatched report that the previously timing-out UserPromptSubmit hook no longer prevents provider work or canonical verdict publication.

Recommended commit type: fix
