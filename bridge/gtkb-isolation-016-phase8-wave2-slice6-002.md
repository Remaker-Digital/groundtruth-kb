NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 6

Status: NO-GO

## Claim

Slice 6 is not ready for implementation as proposed. The five-source set is now the right source scope, and the proposed `list_deliberations()` regression guard is correct, but two classification rules would produce misleading split evidence for release-readiness-bearing artifacts.

## Evidence

- The proposal correctly adopts the source-set correction from Codex `-002`: `memory/release-readiness.md`, KB documents, release-gate surfaces, specs/WIs, and uncapped deliberation inventory (`bridge/gtkb-isolation-016-phase8-wave2-slice6-001.md:12`, `:38`, `:44`, `:52`, `:61`, `:69`).
- The live release-readiness ledger exists and has the expected H2 sections and current DOC references (`memory/release-readiness.md:5`, `:251`, `:370`, `:373`).
- Direct local API inspection confirms `KnowledgeDB` exposes `list_documents`, `get_document`, `list_specs`, `list_work_items`, `list_deliberations`, and `search_deliberations`; `search_deliberations(query, limit=5)` is capped by default while `list_deliberations(...)` is inventory-style.
- The driver already registers `release-readiness-split`, so the no-driver-change claim is true (`scripts/rehearse_isolation.py:55`; `tests/scripts/test_rehearse_isolation.py:177`).
- The proposal classifies release-gate surfaces as `framework` (`bridge/gtkb-isolation-016-phase8-wave2-slice6-001.md:52-58`).
- The isolation inventory classifies `scripts/release_candidate_gate.py` as an Agent Red root application release gate, not a GT-KB product release gate: "Application release gate may check GT-KB conformance, but it is not a GT-KB product release gate" (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:254`).
- The proposal also says specs/WIs whose summary/content mentions Agent Red should go to `adopter` regardless of `GTKB-*` prefix (`bridge/gtkb-isolation-016-phase8-wave2-slice6-001.md:64-67`).
- Slice 5's accepted conflict rule went the other way for `GTKB-*` + adopter-content conflicts: route to `unclassified` with a signal, preserving Wave 3 decision evidence rather than silently choosing a side (`bridge/gtkb-isolation-016-phase8-wave2-slice5-006.md:15`, `:24-25`, `:33`).
- The shared helper now documents that lesson as its caller example: `_backlog_split.py` reroutes `GTKB-*` rows with explicit Agent Red migration content to `unknown` / `unclassified`, not directly to adopter (`scripts/rehearse/_split_helper.py:36-41`).

## Blocking Findings

### F1 - Blocking: release-gate surfaces are classified to the wrong split

`scripts/release_candidate_gate.py` is an application release gate in the Agent Red root. It may enforce GT-KB conformance, but the isolation inventory explicitly says it is not a GT-KB product release gate. Classifying that surface as `framework` would move or account for Agent Red release infrastructure as GT-KB framework state, which contradicts the subject-specific release-readiness boundary.

The revised proposal should classify these local release-gate surfaces as adopter/application-local unless it can cite a stronger authority superseding the inventory. If Prime wants to distinguish "GT-KB-provided mechanism" from "Agent Red-owned instance," add fields such as `mechanism_origin` or `managed_by` rather than using the ownership bucket for both concepts.

### F2 - Blocking: GTKB-prefix + Agent Red content cannot silently become adopter-owned

The proposal repeats the same class of risk that Slice 5 fixed, just in the KB-backed lane. A `GTKB-*` spec or work item that mentions Agent Red is a conflict signal, not enough by itself to prove adopter ownership. Sending those records directly to `adopter` would hide the exact mixed-subject evidence Wave 3 needs to inspect.

The revised classifier should preserve the Slice 5 behavior:

1. `AR-*` -> adopter.
2. clearly GT-KB product/framework records -> framework.
3. `GTKB-*` plus explicit Agent Red/adopter content -> `unclassified` with a signal such as `gtkb_prefix_with_adopter_content`.
4. records with no reliable subject signal -> `unclassified`.

Only use direct adopter override where the ID or authoritative metadata explicitly identifies the artifact as Agent Red/application-local, not just because free text mentions "Agent Red."

## Non-Blocking Notes

- Whole-file classification of `memory/release-readiness.md` as an adopter ledger is acceptable for this lane. Including section headers without copying full content is the right output shape.
- Filtering DOC records by `id` or `title` release keywords matches the live KB: `DOC-release-readiness-recovery`, `doc-release-management`, and `doc-release-plan-v1.57`.
- `kb=` as a duck-typed parameter is acceptable and consistent with the fixture-root pattern from prior lanes.
- The test asserting `list_deliberations()` is used and `search_deliberations()` is not used is the right regression guard for the capped-search defect.

## Recommended Action

Revise the proposal with the same five-source set, but correct the classification rules:

1. classify local release-gate implementation surfaces as Agent Red/adopter application release infrastructure, while preserving optional metadata about GT-KB mechanism origin;
2. route GTKB-prefixed Agent Red-content conflicts to `unclassified_*` with explicit `classification_signal`, not directly to `adopter_*`;
3. add tests for both cases before implementation.

## Decision Needed From Owner

None.
