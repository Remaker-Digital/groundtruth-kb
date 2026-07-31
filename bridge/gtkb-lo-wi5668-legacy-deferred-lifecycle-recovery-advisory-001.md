ADVISORY
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)
bridge_kind: governance_advisory
Document: gtkb-lo-wi5668-legacy-deferred-lifecycle-recovery-advisory
Version: 001
Author: Loyal Opposition (Codex A)
Date: 2026-07-29

## Source

Loyal Opposition review of `bridge/gtkb-wi5668-sweep-completion-gate-011.md` and its full WI-5668 lifecycle evidence. The owner consolidation is recorded in `DELIB-202667525`.

## Claim

The bridge lifecycle cannot honor the owner-directed `DEFERRED` disposition for `gtkb-wi5668-skill-rename-sweep-completion-gate` because its immutable historical v007 lacks a mandatory `Responds to:` link. Typed publication rejects an append-only v015 candidate with `WRONG_RESPONDS_TO_LINK`, leaving the legacy line mechanically stranded at `NO-GO` even though the owner ordered it parked, not active.

## Evidence

- `DELIB-202667525` directs the legacy implementation line to `DEFERRED`, with an append-only metadata-recovery and packet-success resume trigger.
- `bridge/gtkb-wi5668-sweep-completion-gate-011.md` records that a compliant v015 DEFERRED candidate was prepared but rejected before file creation because v007 omits its mandatory `Responds to` link.
- `bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-007.md` is the historical stop report and uses `Responds to GO:` rather than the canonical `Responds to:` metadata required by the immutable lifecycle resolver.
- `bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-014.md` independently confirms the approved scope cannot receive an implementation packet because earlier author/lifecycle metadata is unreadable.
- Duplicate search found no existing WI-5668-specific ADVISORY that covers the owner-directed-DEFERRED publication failure. Related general malformed-chain records (including WI-5629 and WI-5636) do not disposition this stranded WI-5668 lifecycle.

## Impact

The controlling thread remains correctly non-executable, but bridge state cannot represent the owner's intended parked lifecycle state. Future automation and reviewers may misinterpret the residual `NO-GO` as an active correction obligation or try to bypass the packet gate.

## Recommended Prime Action

Route this through governed bridge-lifecycle recovery: design an append-only compatibility/disposition mechanism that can represent the owner-directed `DEFERRED` state for a historical chain whose immutable predecessor lacks canonical `Responds to` metadata. The mechanism must preserve audit history, fail closed for implementation authorization, and be covered by resolver and packet-gate regression tests. Do not rewrite v007 or authorize any legacy three-path implementation while recovery remains incomplete.

## Prior Deliberations

- `DELIB-202667525` — owner decision requiring this thread to be DEFERRED and defining its resume trigger.
- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE` — preserves the dual-authority boundary and does not waive implementation-start authorization.

## Owner Decision Needed

None to capture this advisory. Prime Builder should perform normal advisory intake and seek any new authority required for a bridge-lifecycle recovery proposal.

## Classification Slot

Bridge lifecycle and governance-reliability defect; recommended downstream route: advisory intake followed by a separately authorized bridge-recovery proposal if accepted.

## Non-Approval Statement

This ADVISORY is not implementation approval. It authorizes no rewrite of historical bridge files, no protected source/configuration mutation, no implementation-start packet, and no resumption of the legacy WI-5668 three-path scope.
