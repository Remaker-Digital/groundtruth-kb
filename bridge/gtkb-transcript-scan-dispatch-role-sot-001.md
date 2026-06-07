NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 2026-06-07T01-02-49Z-prime-builder-transcript-scan-p1
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop Prime Builder; owner-directed PROJECT-GTKB-RELIABILITY-FIXES P1 chase-through
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Cross-Harness Dispatch Prompt Uses Harness Registry Role SoT (WI-4390)

bridge_kind: implementation_proposal
Document: gtkb-transcript-scan-dispatch-role-sot
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Codex Prime Builder
Date: 2026-06-07 UTC
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4390
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]
Recommended commit type: fix:

## Claim

The cross-harness bridge dispatch prompt still tells auto-dispatched workers to read their durable role from a forbidden substitute, .claude/rules/operating-role.md, even though the current role source of truth is harness-state/harness-registry.json after resolving the harness identity from harness-state/harness-identities.json.

The last-24h transcript scan found 131 stale prompt occurrences across Claude and Codex auto-dispatch records. Live source inspection found the remaining source at scripts/cross_harness_bridge_trigger.py:_dispatch_prompt. scripts/single_harness_bridge_dispatcher.py already uses harness-registry wording, so this proposal fixes the remaining cross-harness trigger gap.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-RELIABILITY-FAST-LANE-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-SOT-READ-HOOK-CONTRACT-001
- GOV-SESSION-ROLE-AUTHORITY-001
- DCL-SESSION-ROLE-RESOLUTION-001

## Reliability Fast-Lane Eligibility

1. Origin defect/regression: met. WI-4390 is an observed SoT miss in active auto-dispatch prompts.
2. No new public API/CLI: met. The implementation changes prompt wording and tests only.
3. No forbidden operations: met. No deploy, force-push, spec deletion, or data migration.
4. Small single-concern scope: met. One source prompt and one focused regression test.

## Prior Deliberations

- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: standing reliability fast-lane direction and PAUTH basis.
- GOV-SESSION-ROLE-AUTHORITY-001 / DCL-SESSION-ROLE-RESOLUTION-001 history: role authority now resolves through harness identity plus harness registry, not rule-file prose.
- WI-4390 transcript-scan evidence: owner-requested scan on 2026-06-06 captured the concrete remaining prompt occurrences.

## Owner Decisions / Input

No new owner decision required. Mike explicitly directed this session to elevate these PROJECT-GTKB-RELIABILITY-FIXES items and chase them through to completion. The standing PAUTH covers small source/test reliability fixes by active project membership.

## Scope

IP-1: Replace the stale role line in scripts/cross_harness_bridge_trigger.py so it instructs workers to resolve harness identity from harness-state/harness-identities.json and role from harness-state/harness-registry.json through the canonical role reader.

IP-2: Add or extend a focused regression in platform_tests/scripts/test_cross_harness_bridge_trigger.py asserting the dispatch prompt includes the canonical registry paths and excludes .claude/rules/operating-role.md and harness-state/{harness}/operating-role.md as current role authorities.

## Out Of Scope

- Changing dispatch selection logic, bridge INDEX parsing, worker spawning, or implementation-authorization packet behavior.
- Editing .claude/rules/operating-role.md or other narrative governance artifacts.
- Changing single_harness_bridge_dispatcher.py, which already uses the canonical registry wording.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| DCL-SOT-READ-HOOK-CONTRACT-001 | Test asserts the forbidden rule-file substitute is absent from the generated dispatch prompt. |
| GOV-SESSION-ROLE-AUTHORITY-001 / DCL-SESSION-ROLE-RESOLUTION-001 | Test asserts the prompt names harness identity plus harness registry as role authority. |
| GOV-RELIABILITY-FAST-LANE-001 | Manual target-path inspection confirms source + test-only, one-concern fast-lane scope. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Post-implementation report will carry executed pytest/ruff evidence. |

Implementation verification will run:

- python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q -k "dispatch_prompt" --tb=short
- python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
- python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py

## Acceptance Criteria

- [ ] Loyal Opposition returns GO.
- [ ] Dispatch prompt names harness-state/harness-identities.json and harness-state/harness-registry.json as role-authority inputs.
- [ ] Dispatch prompt no longer presents .claude/rules/operating-role.md or harness-local operating-role.md as current role authority.
- [ ] Focused regression test fails before and passes after the fix.
- [ ] Post-implementation report carries observed verification commands and results.
- [ ] Loyal Opposition returns VERIFIED before WI-4390 is closed.

## Risk And Rollback

Risk is low: the change is prompt wording only. Rollback is file-level revert of the prompt text and test assertion. The canonical init keyword and selected bridge entries remain unchanged.
