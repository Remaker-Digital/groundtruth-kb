NEW

# Implementation Report - WI-5267 Alibaba Thinking-Mode Publisher Recovery

bridge_kind: implementation_report
Document: gtkb-wi5267-alibaba-thinking-mode-publisher-recovery
Version: 003
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; resumed governed fleet goal

Responds to GO: bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-002.md
Approved proposal: bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5267-ALIBABA-THINKING-TOOL-CHOICE-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5267
Recommended commit type: fix

target_paths: ["scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

## Implementation Claim

Alibaba H publisher-only recovery no longer sends the object-valued Anthropic `tool_choice` that `deepseek-v4-pro` rejects in thinking mode. `AdopterProfile` now has a strictly validated `force_anthropic_publisher_tool_choice` boolean whose compatible default is `true`; Alibaba alone sets it to `false`. Recovery still exposes exactly one schema, `PublishBridgeVerdict`, and the existing response parser, atomic wrong-tool rejection, publisher-result checks, and retry bounds remain unchanged.

This report claims deterministic implementation correctness only. Per the GO, H fleet viability remains unproven until a separately owner-authorized, substantive H dispatcher run publishes a canonical verdict and H is restored to ineligible afterward.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of defects discovered during the active governed fleet proof.
- The owner directed: "You must fix Alibaba and make it work."
- The owner-authorized H dispatch ended before this implementation. H was restored to `can_receive_dispatch=false`; this report does not request or imply provider-contact authorization.

## Prior Deliberations

- `DELIB-202666173` - active fleet proof and defect-correction direction.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-004.md` - predecessor publisher-only completion guard.
- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-006.md` - predecessor diagnostic repair; its forced-selection behavior is changed only for incompatible H thinking mode.
- `bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-002.md` - independent GO and implementation conditions.

## Implementation Details

1. Added `AdopterProfile.force_anthropic_publisher_tool_choice: bool = True`.
2. Added exact-type validation so integers, strings, and `None` fail closed instead of being truthiness-coerced.
3. Conditioned only the Anthropic publisher-only `{"type": "any"}` insertion on that capability.
4. Set the Alibaba H profile capability to `false`; ordinary turns and the one-tool publisher recovery schema are otherwise unchanged.
5. Added a shared Anthropic regression proving the default still forces `{"type": "any"}` and updated Alibaba regressions to require omission on every publisher-only recovery request.

## Exact Candidate Evidence

- Immediately before mutation, `git status --short -- <four authorized paths>` produced no output: all four targets were clean relative to HEAD.
- After implementation, `git diff --name-only -- <four authorized paths>` listed exactly:
  - `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
  - `platform_tests/scripts/test_cloud_harness_base.py`
  - `scripts/alibaba_cloud_studio_harness.py`
  - `scripts/cloud_harness_base.py`
- Exact four-path binary-diff Git object ID: `a298c618c4fcf9ad7628e8d567b42de3754032dc`.
- Diff stat: 4 files changed, 69 insertions, 3 deletions.
- No file was staged or committed. Unrelated owner and parallel-session worktree changes were not modified or included.

## Commands Run

1. `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short`
2. `groundtruth-kb\.venv\Scripts\ruff.exe check scripts/cloud_harness_base.py scripts/alibaba_cloud_studio_harness.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
3. `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/cloud_harness_base.py scripts/alibaba_cloud_studio_harness.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
4. `git diff --check -- scripts/cloud_harness_base.py scripts/alibaba_cloud_studio_harness.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
5. `git diff --name-only -- scripts/cloud_harness_base.py scripts/alibaba_cloud_studio_harness.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py`

## Observed Results

- Pytest: `116 passed, 1 warning in 2.87s`. The warning is the repository's existing unknown `asyncio_mode` pytest configuration warning, not a test failure.
- Ruff lint: `All checks passed!`
- Ruff format: `4 files already formatted`.
- Diff check: exit 0 with no whitespace errors. Git emitted only the repository's LF-to-CRLF working-copy notices.
- Exact path check: only the four authorized source/test targets listed above.

## Specification-Derived Verification

| Governing requirement | Executed evidence | Result |
| --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | Alibaba full suite proves provider-compatible recovery payloads and retains 600 turns, 900-second operation timeout, and 3600-second session/model allowance assertions. | PASS |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | `test_anthropic_publisher_only_recovery_forces_tool_choice_by_default` proves compatible Anthropic profiles retain forced-any behavior; strict invalid-value parametrization proves fail-closed configuration. | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Alibaba recovery tests expose only `PublishBridgeVerdict`; existing valid-publisher, malformed, failed-result, missing-path, prose, and mixed wrong-tool cases all passed in the complete suites. | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal `-001` carries the full spec list plus PAUTH/project/WI metadata; independent GO `-002` reports both preflights PASS. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps every linked requirement to executed full-suite, lint, format, and exact-diff evidence. | PASS |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Matching claim acquired at `2026-07-15T16:54:08Z`; implementation-start packet finalized at `2026-07-15T16:54:34Z` with PAUTH decision `allowed` for exactly four paths. | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Genuine H failure is linked through WI-5267, TEST-11422, PAUTH, proposal, GO, implementation, tests, and this verification request. | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Every implementation and test target is under `E:\GT-KB`; no external path is a live dependency. | PASS |
| `GOV-STANDING-BACKLOG-001` | This report explicitly leaves fresh H target-authored dispatcher proof outstanding after deterministic verification. | PASS |

## Acceptance Criteria Status

- [x] Alibaba publisher-only recovery sends no object or required `tool_choice` in thinking mode.
- [x] Every Alibaba recovery request exposes only the governed publisher schema.
- [x] A valid publisher call advances exactly one canonical bridge verdict in the deterministic test path.
- [x] Prose, blank, malformed, failed-publisher, missing-path, or non-publisher output cannot create false completion and remains bounded.
- [x] Compatible Anthropic profiles retain their current forced-selection default.
- [x] WI-5258 sanitized HTTP diagnostics and H's 600/900/3600 allowances remain unchanged and green.
- [x] Complete cloud-base and Alibaba suites, Ruff lint/format, and diff checks pass.
- [ ] Independent Loyal Opposition verification precedes any focused commit.
- [ ] Fresh H target-authored dispatcher publication proof is obtained under separate owner authorization.

## Risk And Rollback

Residual risk is provider behavior under a real Alibaba thinking-mode request; deterministic tests cannot prove the model will choose the sole exposed tool. The existing prompt, one-tool schema, parser, atomic wrong-tool rejection, publisher result validation, and bounded retry cap prevent omission from becoming false completion. Rollback is a focused revert of the boolean profile capability, Alibaba override, and associated tests; the WI/test/bridge history remains append-only.

## Loyal Opposition Asks

1. Verify deterministic implementation correctness against the GO and linked specifications.
2. Return VERIFIED if the four-path candidate and evidence satisfy the approved scope; otherwise return NO-GO with concrete findings.
3. Preserve the explicit distinction between deterministic VERIFIED and the later fresh H fleet-viability proof.
