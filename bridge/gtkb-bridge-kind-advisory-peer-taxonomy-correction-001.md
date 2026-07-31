ADVISORY
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bff-bdfc-7c42-a63c-1663409f04d7
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; explicit ::init gtkb pb; approval_policy=never

# Advisory: Bridge kind taxonomy needs a peer-level advisory kind

bridge_kind: governance_advisory
Document: gtkb-bridge-kind-advisory-peer-taxonomy-correction
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

implementation_scope: none (advisory capture only; no code, test, config, or KB mutation proposed or performed by this document)
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Compatibility Disclosure

This file carries `bridge_kind: governance_advisory` solely because that is the current enforced enum value accepted by the live bridge compliance gate. That value is not endorsed by this advisory. It is the defect being captured: ADVISORY artifacts need a peer-level advisory bridge kind distinct from governance-specific work.

## Source

Owner correction in the active 2026-07-16 Prime Builder session: `governance_advisory` is wrong because an ADVISORY bridge artifact is a peer to the NEW artifact, and Advisory Proposals are not necessarily related to governance. Live code inspection confirms the current tooling cannot represent that distinction without using the misleading value.

Primary evidence inspected before filing:

- `groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py` defines `BridgeKind.GOVERNANCE_ADVISORY = "governance_advisory"` and has no neutral peer-level `advisory` value.
- `scripts/migrate_bridge_kind_taxonomy.py` maps `governance_review`, `loyal_opposition_advisory`, `advisory_report`, and even `advisory` into `governance_advisory`.
- `platform_tests/scripts/test_bridge_kind_taxonomy.py` locks the migration behavior from `loyal_opposition_advisory` to `governance_advisory`.
- `.claude/rules/canonical-terminology.md` still describes Loyal Opposition advisory files with `bridge_kind: loyal_opposition_advisory`, which is stale and invalid under the current enum.
- `.claude/hooks/bridge-compliance-gate.py` validates bridge kinds against the current enum and therefore rejects the owner-corrected neutral value today.

## Claim

The live bridge-kind taxonomy collapses all advisory-shaped artifacts into `governance_advisory`, which misstates their semantics. ADVISORY is a status-bearing bridge artifact class that can capture technical, product, operational, process, or governance findings. It should have a neutral peer-level bridge kind, recommended default `advisory`, rather than a governance-only label.

The current taxonomy also creates repair pressure in the wrong direction: stale references to `loyal_opposition_advisory` are currently expected to become `governance_advisory`, but the owner correction says that destination is itself wrong. A future fix must supersede both the stale value and the misleading current value without doing another broad rewrite to `governance_advisory`.

## Owner Decision Needed

No owner decision is needed to preserve this advisory. A later implementation proposal should ask one bounded owner question before mutation: whether the canonical replacement value should be exactly `advisory` or a more specific peer-level value. Recommended default: `advisory`, because it mirrors the first-line `ADVISORY` status and avoids implying governance-only scope.

## Recommended Prime Action

1. Register this finding as a MemBase work item once KB mutation is unblocked and governed authorization is available.
2. Draft a bounded implementation proposal to add the owner-selected neutral advisory bridge kind, update bridge-kind validation, migration, lane classification, disposition/routing helpers, tests, and documentation.
3. Correct stale references in `.claude/rules/canonical-terminology.md` and the auto-memory guidance for findings-become-advisory-proposals to the new neutral value once it exists.
4. Do not resolve those references by rewriting them to `governance_advisory`; that would preserve the semantic error this advisory captures.

## Classification Slot

adopt. The owner correction is explicit, the live enum and migration behavior confirm the representational defect, and the next artifact should be a tracked work item followed by a normal governed implementation proposal.

## Specification Links

- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-ADVISORY-REPORT-TEMPLATE-001`

## Prior Deliberations

- Current owner correction in this Prime Builder session: `governance_advisory` is a misleading value for general ADVISORY bridge artifacts.
- `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md` records adjacent drift caused by stale advisory bridge-kind guidance.
- `bridge/gtkb-wi5330-governance-gate-bypass-advisory-002.md` records another live advisory thread that is forced to use the current misleading bridge kind.

## Owner Decisions / Input

The owner explicitly corrected the taxonomy interpretation in this session. No implementation approval is inferred from that correction; it authorizes preserving the advisory finding only.

## Non-Approval Statement

This ADVISORY entry is not implementation approval. It does not authorize any source, test, configuration, KB, database, Git, dispatcher, migration, or documentation mutation. It records a confirmed taxonomy problem and the recommended next artifact path.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
