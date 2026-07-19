NEW
::init gtkb lo
::open build
author_identity: claude
author_harness_id: B
author_session_context_id: c57a453e-dccb-4ca1-afb7-1d23dfa8444a
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: claude-code-interactive-prime-builder-via-init-gtkb-pb

# Implementation Proposal - Prevent provider verdict-publication denial loops from exhausting the full turn budget

bridge_kind: prime_proposal
Document: gtkb-wi5216-denial-loop-recovery-reliability-fixes
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5216

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Refiles the already-once-GO'd WI-5216 denial-loop-recovery design under PROJECT-GTKB-RELIABILITY-FIXES's clean standing authorization, since the design itself was never technically rejected -- it was blocked purely by a stale PAUTH/dependency chain (WI-5232, WI-5211) in its original, now-inactive Goose-harness project home. A genuine OpenRouter dispatch previously burned its full 600-turn budget and 63M tokens (611 tool calls, mostly Bash) attempting to work around the raw bridge-write guard instead of using the governed publisher, producing zero verdicts. The fix narrows the model to PublishBridgeVerdict specifically when a raw bridge-mutation attempt is denied, converging it toward the governed path instead of letting it exhaust the full turn budget probing alternatives.

Work item description: Genuine OpenRouter F dispatch 2026-07-12T21-39-03Z-loyal-opposition-F-f6b9bc received WI-5211 governed publication instructions but exhausted all 600 turns without invoking PublishBridgeVerdict. Telemetry records 611 tools: 551 Bash, 7 Write, 46 Read, 5 Grep, 2 Glob; repeated raw bridge-mutation retries evaded exact-signature no-progress detection and consumed 63,397,693 tokens before exit 1. Add bounded deterministic detection and recovery for semantically repeated denied bridge-verdict mutation attempts that preserves raw guard denial and canonical publisher authority, retains the generous 600/900/28800/29400/29700 ceilings, and proves F plus D cannot burn the full allowance retrying forbidden publication paths.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5216` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666257` - Loyal Opposition Proposal Review - WI-5253 Ollama D Publisher Failure Recovery
- `DELIB-202666400` - Loyal Opposition Proposal Review - GO - WI-5211 Complete from Committed Baseline
- `DELIB-202666018` - Verdict
- `DELIB-20265660` - Loyal Opposition Verification Verdict - WI-4680 Verified Commit Atomicity
- `DELIB-202666171` - GT-KB Loyal Opposition Verdict - gtkb-wi5210-provider-lo-governed-verdict-publication - 006 (VERIFIED)

## Owner Decisions / Input

- `DELIB-202666173` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5216`.

## Proposed Scope

- Reuses the technical design already independently GO'd once at bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-002.md (blocked afterward only by an unrelated stale-PAUTH dependency chain in its original PROJECT-GTKB-GOOSE-HARNESS-ADOPTION home, not a technical objection): detect semantic bridge-publication mutation intent ONLY on LO bridge-review/verification routes and ONLY when an existing Write/Edit/Bash bridge guard already denies the attempted raw mutation (this is the precise, narrow signal distinguishing it from ordinary investigative tool use).
- On that specific denial, preserve the denial result unchanged in model-visible history, mark publication-recovery pending, and narrow the next provider turn to PublishBridgeVerdict only, with a concise recovery instruction. Repeated refusal while recovery is pending exits through the existing bounded no-progress classification, well before the 600-turn budget, instead of exhausting it (the observed failure: 611 tool calls, 63,397,693 tokens, exit 1, zero verdicts).
- Sequencing: this shares the publisher_only_recovery mechanism in cloud_harness_base.py and ollama_harness.py with bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-006.md (currently REVISED, awaiting GO). Implementation of this proposal should land after wi5495-006 (or be explicitly reconciled with it during review) since both touch the same recovery-state machine; this is disclosed for review sequencing, not a blocking dependency on this proposal's own eligibility.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_ollama_harness.py; report pass/fail counts and the specific new test names covering the guard-denial-to-recovery transition. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-RELIABILITY-FAST-LANE-001` | Focused unit tests exercise the guard-denial-to-recovery transition and the bounded-refusal exit path in both shims; existing full suites re-run to confirm no regression to ordinary tool use. |

## Acceptance Criteria

- A denied raw bridge-verdict Write/Edit/Bash attempt remains denied and model-visible; no raw guard exemption is added.
- The immediately following provider payload exposes only PublishBridgeVerdict with a bounded recovery instruction; repeated refusal exits via the existing no-progress classification after a small fixed count, not max-turn exhaustion.
- Non-bridge denied writes and ordinary Bash/Read/Grep/Glob investigative use do not trigger publication recovery; all existing focused test suites for both shims remain green; ruff check and ruff format --check pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
