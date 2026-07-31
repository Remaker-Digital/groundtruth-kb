# WI-4365 Prompt-Submit Surface Classification

Date: 2026-06-29 UTC
Project: PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY
Work item: WI-4365
Bridge: bridge/gtkb-wi4365-prompt-submit-surface-classification-001.md
GO: bridge/gtkb-wi4365-prompt-submit-surface-classification-002.md
Project authorization: PAUTH-PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY-BRIDGE-SIGNAL-QUALITY-BOUNDED-IMPLEMENTATION-2026-06-23
Implementation-start packet: sha256:c704eda78135b6f3ede4a86e49d35cbfb771953e035c9acbd50ea1ca50471f72

## Claim

The live Claude and Codex prompt-submit surfaces are intentionally asymmetric for
`owner-decision-tracker` and `bridge-axis-2-surface`, because both are
prompt-driven Claude behaviors with owner-approved Codex parity waivers.
`session-topic-envelope-routing` is an adjacent accepted adapter difference with
native coverage on both harnesses. The live gap/noise item is
`glossary-expansion`: Claude registers it on `UserPromptSubmit`, Codex contains a
copied hook file, but Codex has no live hook registration and the capability
registry does not currently record a capability row or waiver for that surface.

Cancelled prompt-submit poller surfaces should stay cancelled. Reintroducing
poller-freshness prompt hooks would reverse the 2026-04-25 token-cost decision
and add operator noise without improving live bridge authority.

## Source Inventory

This classification uses only live in-root files. It does not treat automation
memory, generated dashboard copies, worktree snapshots, or previous chat
summaries as authority.

| Source | Evidence | Relevance |
| --- | --- | --- |
| `.claude/settings.json` | Lines 264, 286, 291, 301, and 311 register Claude `UserPromptSubmit` hooks for owner-decision tracking, AXIS 2 bridge surfacing, glossary expansion, and session-topic routing. Line 228 registers owner-decision tracking on `Stop`. Line 3 records the 2026-04-25 poller-freshness hook removal. | Live Claude prompt-submit configuration. |
| `.codex/hooks.json` | File content is `{"hooks":{}}`. | Codex has no live project-level hook registration through this surface. |
| `config/agent-control/harness-capability-registry.toml` | Lines 785-801 define `hook.session-topic-envelope-routing` with Claude and Codex native surfaces. Lines 1103-1114 define `hook.bridge-axis-2-surface` as Claude prompt-driven AXIS 2 with Codex app-thread automation instead. Lines 1229-1240 define `hook.owner-decision-tracker` as Claude UserPromptSubmit plus Stop. Lines 1372-1377 and 1444-1449 record Codex waivers under `DELIB-20266285`. | Live parity authority and waiver source. |
| `config/agent-control/system-interface-map.toml` | Lines 752-766 define the Claude AXIS 2 UserPromptSubmit bridge surface and state that Claude is pull-based while Codex is push-based app-thread automation. Line 280 records a Codex app UI prompt-submit trace location, not a live `.codex/hooks.json` registration. | Cross-harness interface map. |
| `.claude/hooks/owner-decision-tracker.py` | Hook documentation identifies Claude Stop/UserPromptSubmit behavior and the pending-owner-decision memory surface. | Behavior source for owner-action surfacing. |
| `.claude/hooks/bridge-axis-2-surface.py` | Hook documentation identifies the Claude UserPromptSubmit AXIS 2 bridge surface. | Behavior source for prompt-time bridge surfacing. |
| `.claude/hooks/glossary-expansion.py` | Documentation identifies a Claude Code UserPromptSubmit glossary expansion hook. | Behavior source for live Claude glossary expansion. |
| `.codex/gtkb-hooks/glossary-expansion.py` | File has the same Claude Code UserPromptSubmit documentation, but `.codex/hooks.json` does not register it. | Dormant Codex copy, not live Codex hook authority. |

## Classification Matrix

| Surface | Claude behavior | Codex behavior | Classification | Operator impact | Follow-up action |
| --- | --- | --- | --- | --- | --- |
| `owner-decision-tracker` | Registered on `Stop` and `UserPromptSubmit` in `.claude/settings.json`; tracks pending owner decisions and can nudge/block prose decision prompts. | No `.codex/hooks.json` registration. Registry records Codex waiver `DELIB-20266285` because the hook is prompt-driven Claude behavior. | Accepted asymmetry. | Claude interactive sessions get prompt-time owner-decision reminders. Codex automation should not be expected to reproduce that through a project-level UserPromptSubmit hook. | No hook/config change in WI-4365. Re-evaluate only at the next cross-harness parity audit or if Codex gains an equivalent prompt-submit hook contract. |
| `bridge-axis-2-surface` | Registered on `UserPromptSubmit`; reads live dispatcher/TAFE plus bridge files and emits newly actionable bridge work into Claude prompt context. | No `.codex/hooks.json` registration. Registry and system-interface map state that Codex AXIS 2 is app-thread automation, not a UPS hook. | Accepted asymmetry. | Claude gets pull-based prompt-time bridge surfacing. Codex gets push-based automation/thread wake behavior. Treating Codex absence as missing parity would create false drift. | No hook/config change in WI-4365. Keep the waiver and system-interface caveat as the live explanation. |
| `glossary-expansion` | Registered on `UserPromptSubmit`; reads canonical terminology and emits bounded glossary/DA candidate context. | A copied `.codex/gtkb-hooks/glossary-expansion.py` exists with Claude UserPromptSubmit documentation, but `.codex/hooks.json` is empty and no registry capability/waiver was found for `glossary-expansion`. | Parity gap / noisy dormant surface. | Operators can infer Codex support from the copied file or generated snapshots even though no live Codex hook registration exists. The gap is not urgent behavior loss for automation, but it is real signal drift. | File governed follow-up to choose one disposition: activate/register Codex glossary expansion under Codex-compatible semantics, or retire/remove the dormant Codex copy and add an explicit waiver or registry note. |
| Cancelled prompt-submit poller/freshness surfaces | `.claude/settings.json` records that OS Claude/Codex bridge pollers were halted and the poller-freshness UserPromptSubmit hook was removed on 2026-04-25. | `.codex/hooks.json` is empty; any copied/generated prompt-submit traces are not live authority. | Accepted cancellation; stale-signal cleanup candidate if copied surfaces continue to appear in generated artifacts. | Re-adding prompt-submit freshness checks would restore token-cost noise and compete with live dispatcher/TAFE plus versioned bridge files as authority. | Do not restore retired poller prompt hooks. If stale generated surfaces continue to confuse operators, file cleanup work to label or remove stale copies. |
| `session-topic-envelope-routing` | Registered in Claude `UserPromptSubmit` as `.claude/hooks/session-topic-envelope-router.py`. | Registry records native Codex surface `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`, with both adapters calling shared `groundtruth_kb.session.topic_router`. | Accepted adapter difference. | Both harnesses have topic-envelope routing coverage, but through different adapters. This is not a missing prompt-submit parity issue. | No action beyond preserving the registry row during future parity audits. |

## Follow-Up Recommendations

1. Create a bounded follow-up item for `glossary-expansion` disposition. The
   owner-facing decision is binary: register and validate a Codex-compatible
   glossary expansion path, or retire the dormant Codex copy and document the
   asymmetry.
2. Add `glossary-expansion` to the harness capability registry in the same
   follow-up. The registry should either record native Codex coverage or an
   owner-approved waiver, so future parity checks do not rediscover the same
   ambiguity.
3. Keep cancelled poller-freshness prompt hooks out of live startup and
   prompt-submit paths. If dashboard/worktree/generated copies imply otherwise,
   treat that as generated-surface cleanup, not as live hook authority.

## Acceptance Checklist

- The report exists at the approved target path.
- Each named prompt-submit difference is classified with evidence, impact, and
  follow-up.
- Accepted asymmetries cite live registry or system-interface authority.
- The parity gap/noisy surface is recorded as future governed work rather than
  being implemented directly.
- No hook source, hook configuration, MemBase, GOV, SPEC, ADR, DCL, PAUTH, or
  bridge protocol file is modified by this implementation.

## Verification Results

`python scripts/bridge_applicability_preflight.py --bridge-id
gtkb-wi4365-prompt-submit-surface-classification` passed. The proposal metadata,
project linkage, work item linkage, PAUTH, and target path remained valid.

`python scripts/adr_dcl_clause_preflight.py --bridge-id
gtkb-wi4365-prompt-submit-surface-classification` passed. The mandatory
spec-derived verification clause had evidence and no blocking gaps were found.

`python -m pytest platform_tests/scripts/test_codex_hook_parity.py
platform_tests/hooks/test_owner_decision_tracker.py
platform_tests/hooks/test_glossary_expansion.py
platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short` collected
103 tests: 97 passed and 6 failed. All focused behavior suites passed for
owner-decision tracking, glossary expansion, and AXIS 2 bridge surfacing. The
six failures were confined to `platform_tests/scripts/test_codex_hook_parity.py`
and assert that live Codex hook configuration is absent or incomplete:
`.codex/config.toml` does not enable hooks and `.codex/hooks.json` does not
register the expected PreToolUse, UserPromptSubmit, SessionStart, or Stop hook
groups. Those failures are not fixed in WI-4365 because the approved target path
is report-only and hook/config mutation is explicitly out of scope. They support
the classification that Codex prompt-submit hook coverage needs separate
governed disposition rather than silent parity assumptions.

## Verification Plan Used

The implementation should be verified with:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4365-prompt-submit-surface-classification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4365-prompt-submit-surface-classification
python -m pytest platform_tests/scripts/test_codex_hook_parity.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/hooks/test_glossary_expansion.py platform_tests/scripts/test_bridge_axis_2_surface.py -q --tb=short
```

Any targeted test failure should be interpreted against this report-only scope
before filing implementation completion.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
