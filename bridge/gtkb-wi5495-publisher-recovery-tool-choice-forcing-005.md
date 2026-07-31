REVISED
::init gtkb lo
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e2d6e619-2337-4c83-8571-6bf6ebb6c972
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via gt session envelope open

# Implementation Proposal REVISED - Publisher-only recovery tool_choice forcing (F/OpenRouter only, split from D)

bridge_kind: prime_proposal
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 005
Responds to: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-004.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The version-004 NO-GO (bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-004.md) independently re-verified, via direct read of current HEAD, that the F/OpenRouter half of the original two-harness proposal is mechanically correct, complete, and test-covered, while the D/Ollama half was based on a factually incorrect protocol assumption (Ollama's native `/api/chat` has no `tool_choice` field; the earlier D-side source/test hunks were already reverted under the released implementation claim, per the version-003 NO-ACTION). Per the NO-GO's Required Revision item 4 ("splitting F ... from D ... into separate proposals ... this is Prime Builder's scoping choice to make"), this revision refiles ONLY the confirmed-correct F/OpenRouter half.

## Response to NO-GO (version 004)

Accepted in full. This revision:

1. Preserves exactly the F/OpenRouter `DIALECT_OPENAI_CHAT` forced-function fix in `scripts/cloud_harness_base.py` and its test coverage in `platform_tests/scripts/test_cloud_harness_base.py`, both independently re-verified correct in version 004.
2. Drops `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness.py` from `target_paths` entirely. The D/Ollama fix is deliberately NOT re-attempted here; it requires a protocol-appropriate redesign tracked separately (see below), not a resubmission of the same mechanism against a different transport.
3. Requires a fresh claim and fresh implementation-start authorization packet before any further mutation, per Required Revision item 5 -- acquired for this revision (claim acquired 2026-07-18T05:01:23Z, session e2d6e619-2337-4c83-8571-6bf6ebb6c972).

## Additional Finding Since Version 004 (D-side context, informational only -- does not affect this F-only scope)

During investigation of the D-side redesign, empirical testing found that Ollama's OpenAI-compatible `/v1/chat/completions` endpoint (confirmed live and reachable for the `deepseek-v4-flash:cloud` route) does NOT reliably honor `tool_choice` forcing for this model either: with the tool schema correctly restricted to only `PublishBridgeVerdict` and `tool_choice` explicitly forced, the model returned a blank/prose response declining to call any tool, rather than complying. This means a transport switch alone (native `/api/chat` -> OpenAI-compatible `/v1/chat/completions`) would not fully resolve D's publisher-recovery defect the way `tool_choice` forcing resolves it for F. This finding is carried forward as context for the D-side follow-on work item; it does not change anything in this F-only revision's scope, acceptance criteria, or target paths.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5495 remains a bounded reliability defect under the active standing project authorization; this revision narrows scope to the confirmed-correct half. No new owner decision is required.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `platform_tests/scripts/test_cloud_harness_base.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only numbered-file discipline for this revision.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the version-004 NO-GO's substantive basis; this revision's claims are grounded in the same fresh-read discipline.
- `GOV-RELIABILITY-FAST-LANE-001` - re-checked eligibility per version-004: origin=defect, no new public API/CLI/behavior beyond defect removal, current scope (2 files, few lines) is small/single-concern.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing specification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain in-root.

## Prior Deliberations

- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md` - original two-harness proposal.
- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-002.md` - original GO (superseded).
- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-003.md` - Prime Builder NO-ACTION identifying the D-side protocol mismatch.
- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-004.md` - corrected NO-GO, independently re-verifying the F-side fix as correct and recommending the F/D split this revision implements.
- `DELIB-202666257`, `DELIB-202666266`, `DELIB-202666227`, `DELIB-202666174`, `DELIB-202666256` - prior governed Ollama/OpenRouter publisher-recovery review and verification deliberations, carried forward.

## Owner Decisions / Input

No new owner decision is requested. WI-5495 remains within the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` authorization for this narrowed F-only scope.

## Proposed Scope

- In `cloud_harness_base.py`'s `run_tool_loop`, extend the existing publisher-only-recovery `tool_choice` forcing block (currently gated to `profile.dialect == DIALECT_ANTHROPIC_MESSAGES`) with a parallel `elif profile.dialect == DIALECT_OPENAI_CHAT` branch that sets `payload["tool_choice"] = {"type": "function", "function": {"name": PUBLISH_BRIDGE_VERDICT_TOOL}}`, the standard OpenAI Chat Completions forced-function-call directive.
- Add test coverage in `test_cloud_harness_base.py` asserting `tool_choice` is absent on pre-recovery and post-publish turns and present with the exact forced-function shape only during the recovery turn, for the openai-chat dialect specifically.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest `platform_tests/scripts/test_cloud_harness_base.py`; assert new dialect-specific `tool_choice` assertions pass and existing `DIALECT_ANTHROPIC_MESSAGES` coverage remains green (no regression). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Direct read of current HEAD `scripts/cloud_harness_base.py` confirming `_openai_build_payload` / `DIALECT_OPENAI_CHAT` is the live transport for F/OpenRouter, not assumed from prose. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability + clause preflights against this revision's operative file. |
| `GOV-RELIABILITY-FAST-LANE-001` | Re-verify WI-5495 origin=defect and PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING active/covering, matching version-004's re-check. |

## Acceptance Criteria

- `payload["tool_choice"]` equals the exact forced-function-call shape targeting `PublishBridgeVerdict` by name during publisher-only recovery for `DIALECT_OPENAI_CHAT`, and is absent on ordinary (non-recovery) turns.
- `ruff check` and `ruff format --check` pass on `scripts/cloud_harness_base.py`.
- The full existing test suite for `cloud_harness_base.py` passes with the new assertions added; no regression to existing `DIALECT_ANTHROPIC_MESSAGES` coverage.

## Risks / Rollback

Risk is low: this is a narrow, additive `elif` branch mirroring an already-shipped pattern in the same `if` block, touching only the openai-chat dialect path. Rollback is a revert of the source and test changes; no bridge, KB, or dispatcher state is touched.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
