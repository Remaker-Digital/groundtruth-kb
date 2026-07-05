NEW

# WI-4538 Pending Owner-Decision Auto-Clear and Cross-Session Dedup

bridge_kind: prime_proposal
Document: gtkb-wi4538-pending-owner-decision-auto-clear-dedup
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4538-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4538

target_paths: ["groundtruth-kb/src/groundtruth_kb/owner_decision/resolution_signals.py", "groundtruth-kb/src/groundtruth_kb/owner_decision/__init__.py", ".claude/hooks/owner-decision-tracker.py", "platform_tests/owner_decision/test_resolution_signals.py", "platform_tests/hooks/test_owner_decision_tracker.py"]

implementation_scope: source/test/hook
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4538 fixes a cross-session owner-decision queue failure: a pending ledger entry can remain in `memory/pending-owner-decisions.md` after another session has already resolved the underlying work through a Deliberation Archive owner-decision row or through an explicitly referenced bridge thread reaching a resolved workflow state. The concrete defect was DECISION-1219: the stale pending entry allowed a second session to drive TAFE Slice C again, producing duplicate owner-approved ADR/proposal artifacts that later required reconciliation.

The implementation will add a deterministic resolution-signal helper and wire it into `.claude/hooks/owner-decision-tracker.py` before UserPromptSubmit nudges and Stop-mode durable-file rewrites. It will auto-move a pending entry to `## Resolved` only when evidence is exact and structured: the pending DECISION id appears in a current Deliberation Archive row with `outcome=owner_decision`, or the pending entry explicitly references a bridge thread whose latest status is `GO`, `VERIFIED`, or `WITHDRAWN`. Ambiguous prose, fuzzy semantic matches, stale generated summaries, and unrelated deliberations remain non-resolving. The hook must never mutate MemBase, bridge files, or live worktree artifacts as part of this clearing step; it only updates the owner-decision ledger entry already owned by the hook.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-thread resolution signals must derive from the live TAFE/numbered-file bridge state, not startup summaries or cached scan text.
- `GOV-STANDING-BACKLOG-001` - WI-4538 is a MemBase backlog item and should reach terminal state only through bridge-reviewed implementation and verification evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the helper must read fresh Deliberation Archive and bridge state when deciding whether a pending entry is stale.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is bounded by the active Batch A2 PAUTH for WI-4538.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH allows this proposal to proceed through the bridge; it does not bypass Loyal Opposition review or implementation-start authorization.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the auto-clear behavior must stay inside the narrow owner-approved envelope and must not perform broad bulk status mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable PAUTH, project, work item, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specifications and maps them to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward these specs and execute the tests below.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the hook behavior protects cross-harness sessions and must not rely on one harness's local memory.
- `ADR-CROSS-HARNESS-PARITY-001` - touching a harness hook requires explicit behavioral-parity disposition across applicable harnesses.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the proposal must include this Cross-Harness Disposition because `.claude/hooks/owner-decision-tracker.py` is a harness-surface target.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - stale-decision closure must use relevance-complete explicit evidence rather than a non-empty but irrelevant decision/bridge link.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, deliberations, bridge threads, and ledger entries are related durable artifacts with distinct lifecycle meanings.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the design keeps the DA, bridge, hook-owned ledger, and tests connected as durable artifacts instead of relying on transient chat memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - bridge lifecycle states and Deliberation Archive owner-decision records are artifact triggers for ledger cleanup.
- `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` - existing same-turn and cross-turn AUQ correlation is fail-closed; the new cross-session resolver must preserve that safety floor.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - decision classification must remain deterministic and import no LLM/API classifier dependencies.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are GT-KB platform files under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-DECISION-1219-SLICE-C-RECONCILE-CONSOLIDATE` - source defect: DECISION-1219 remained pending after a peer session had already effectively resolved TAFE Slice C, causing duplicate owner-approved ADR/proposal work and later reconciliation.
- `DELIB-DECISION-1219-SLICE-C-DRIVE-ADR-FIRST` - earlier owner decision that was duplicated by the stale pending entry.
- `DELIB-20263275` / `bridge/gtkb-tafe-dual-write-slice-c-ingestion-002.md` - example bridge GO signal showing the underlying Slice C work had moved forward through the bridge.
- `DELIB-20263274` / `bridge/gtkb-tafe-slice-c-ingestion-consolidated-002.md` and `-004.md` - later consolidated Slice C path carrying the reconciled owner decision to verified implementation evidence.
- `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-004.md` - prior owner-decision tracker fix that suppresses stale relay matches using exact known-decision identity.
- `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` - prior formal rule for fail-closed owner-decision auto-resolution using explicit two-signal correlation.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner directed Batch A2 continuation and authorized WI-4538 through `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4538-BATCH-A2-20260705`.

No new owner decision is required for this implementation proposal. It does not create, approve, reject, or reinterpret owner decisions; it only proposes a deterministic guard that prevents already-resolved decisions from being re-presented as still pending.

## Cross-Harness Disposition

- Claude Code: applicable and directly modified. The existing `.claude/hooks/owner-decision-tracker.py` Stop/UserPromptSubmit path owns the durable `memory/pending-owner-decisions.md` ledger; this slice wires exact cross-session resolution signals into that path.
- Codex: no Codex-specific hook/config mutation is proposed in this slice. Behavioral parity is preserved by placing the resolution classifier in shared package code under `groundtruth_kb.owner_decision`, with tests that run outside the Claude hook wrapper. Codex-facing surfaces must not grow a separate owner-decision classifier; any future Codex owner-decision hook should call the same helper.
- Antigravity, Cursor, and Ollama: no dedicated owner-decision hook surface is changed in this slice. The applicable parity obligation is the same as Codex: no divergent classifier, no harness-local ledger semantics, and future integration through the shared deterministic helper.
- Waivers: none requested. The disposition is behavioral-equivalence by shared helper for non-Claude harnesses and direct hook integration for the existing Claude owner-decision tracker surface.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirement set is WI-4538's backlog text, the DECISION-1219 reconciliation deliberation, the existing owner-decision tracker rule/test surface, the Batch A2 PAUTH, and the linked bridge/governance specs above. No new GOV/ADR/DCL/SPEC mutation is proposed.

## Proposed Implementation

1. Add `groundtruth_kb.owner_decision.resolution_signals` with a deterministic, dependency-light API that accepts pending decision entries plus injected or live read adapters for Deliberation Archive and bridge latest-status evidence.
2. Recognize a deliberation signal only when a current row has `outcome="owner_decision"` and either `source_ref == <decision_id>`, `auq_id == <decision_id>` when available through the service record, or the decision id appears as a bounded token in the row title/summary/content. The emitted resolution note must cite the DELIB id.
3. Recognize a bridge signal only when the ledger entry explicitly names a bridge thread via `thread_ref`, `bridge/<slug>-NNN.md`, or an exact slug-shaped token in question/notes, and that thread's latest status is one of `GO`, `VERIFIED`, or `WITHDRAWN`. The emitted resolution note must cite the bridge slug and latest status.
4. Leave entries pending when no explicit evidence exists, when evidence is ambiguous, when bridge latest status is `NEW`, `REVISED`, `NO-GO`, `ADVISORY`, or `DEFERRED`, or when the DA/bridge read fails.
5. Wire the helper into the owner-decision tracker before UserPromptSubmit nudge rendering and during Stop-mode durable-file maintenance, preserving graceful degradation and existing same-turn/cross-turn AUQ correlation behavior.
6. Keep live mutations limited to the hook-owned pending-decision ledger: move matched entries from `pending` to `resolved`, set `resolved_via` to `cross_session_deliberation_resolution` or `cross_session_bridge_resolution`, add a bounded note, and write the existing durable file atomically.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | New helper imports no LLM/API classifier libraries and uses only deterministic parsing/read adapters. | Add `platform_tests/owner_decision/test_resolution_signals.py` coverage for import closure/no forbidden SDK imports. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and `GOV-FILE-BRIDGE-AUTHORITY-001` | Resolution reads fresh DA rows and live bridge latest status; generated summaries/caches do not count. | Helper tests with injected DA/bridge readers plus hook tests proving stale summary text alone does not resolve. |
| `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Harness-specific hook behavior is isolated to Claude's existing hook surface; classifier logic is shared and no divergent non-Claude classifier is introduced. | Tests import and exercise `groundtruth_kb.owner_decision.resolution_signals` directly, plus hook subprocess tests prove the Claude wrapper consumes the shared behavior. |
| `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` | Existing same-turn/cross-turn AUQ correlation and prose-block behavior remain unchanged. | Run the existing `platform_tests/hooks/test_owner_decision_tracker.py` suite and add focused regression cases around the new pre-nudge clearing path. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` and Batch A2 PAUTH limits | No broad bulk mutation; only exact matched pending entries move to resolved. | Tests with multiple pending entries assert only the matched decision changes and unrelated entries remain pending. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Resolution notes cite the durable DELIB id or bridge slug/status that triggered cleanup. | Tests assert `resolved_via`, `answer`, and `notes` include bounded evidence references. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries executed test evidence mapped to this plan. | Post-implementation report includes exact pytest, ruff lint, and ruff format results. |

Minimum verification commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/owner_decision/test_resolution_signals.py platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/owner_decision/resolution_signals.py groundtruth-kb/src/groundtruth_kb/owner_decision/__init__.py .claude/hooks/owner-decision-tracker.py platform_tests/owner_decision/test_resolution_signals.py platform_tests/hooks/test_owner_decision_tracker.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/owner_decision/resolution_signals.py groundtruth-kb/src/groundtruth_kb/owner_decision/__init__.py .claude/hooks/owner-decision-tracker.py platform_tests/owner_decision/test_resolution_signals.py platform_tests/hooks/test_owner_decision_tracker.py
```

## Risk / Rollback

Risk is moderate because over-eager owner-decision clearing could hide a real pending decision. The proposal lowers that risk by requiring exact decision-id or explicit bridge-thread evidence, preserving all ambiguous cases as pending, and keeping the Stop/UserPromptSubmit hook graceful-degradation behavior. Rollback is a single revert of the implementation commit; bridge files remain append-only and any incorrectly resolved ledger fixture can be restored from git history or the hook-owned file's resolved/history sections.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4538-pending-owner-decision-auto-clear-dedup`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the change repairs a stale cross-session owner-decision queue behavior that caused duplicate approvals and duplicate implementation paths, while preserving the existing tracker surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
