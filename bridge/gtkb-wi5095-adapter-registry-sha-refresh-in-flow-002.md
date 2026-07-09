GO

bridge_kind: lo_verdict
Document: gtkb-wi5095-adapter-registry-sha-refresh-in-flow
Version: 002
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-001.md

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 6147bb18-d9cc-41a7-8702-1ca4a8b977cf
author_model: Claude Sonnet 4.6 (Thinking)
author_model_version: claude-sonnet-4-6
author_model_configuration: Antigravity harness, Loyal Opposition role

## Verdict: GO

Loyal Opposition grants GO for WI-5095: Make registry `source_sha256` refresh part of the default adapter-regen flow. The proposal correctly identifies a systemic registry drift defect, the fix is well-scoped and mechanically sound, all preflights pass, and the verification plan is specific and executable. No blocking findings.

## Applicability Preflight

- packet_hash: `sha256:fb0b75c80de78ec076410204b0b873e17a7c5b6b294f04d05ba3029006f5da46`
- bridge_document_name: `gtkb-wi5095-adapter-registry-sha-refresh-in-flow`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-001.md`
- operative_file: `bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5095-adapter-registry-sha-refresh-in-flow`
- Operative file: `bridge\gtkb-wi5095-adapter-registry-sha-refresh-in-flow-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- WI-3407 post-implementation report (`bridge/gtkb-wi3407-composite-delib-workflow-skill-003.md`) — surfaced the registry `source_sha256` lag as an out-of-scope hygiene finding; this proposal is the governed follow-on.
- WI-4840 thread — sibling skill-scaffold whose adapter changes correctly included the registry and MANIFEST; the drift is a consequence of the opt-in rather than default registry refresh.
- Owner AUQ (this session): selected "Systemic: refresh in the flow" — make registry `source_sha256` refresh part of the default adapter-regen flow across all three generators plus a drift-catching test.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — the parity contract the registry `source_sha256` serves.

## Review Analysis

**Root cause:** The three generators (`generate_codex_skill_adapters.py`, `generate_antigravity_skill_adapters.py`, `generate_api_skill_adapters.py`) refresh the registry `source_sha256` only under `--update-registry`, so a standard `generate()` or `--check` run silently lets the registry drift from the adapter bodies it claims to mirror. This is a genuine systemic defect with a concrete confirmed instance (WI-3407 / `decision-capture`).

**Fix correctness:** Making registry refresh part of the default `generate()` path is the right systemic fix. The implementation requirement is clear: fold `update_registry()` into the standard flow; in `--check` mode, report a stale `source_sha256` as drift without writing (consistent with how `--check` handles stale adapter bodies). Idempotence must be preserved: a second default run on an already-current worktree must report no drift.

**Drift-catching test:** Adding `test_registry_source_sha256_consistency.py` as a CI-visible enforcement layer for the registry SHA invariant is the right mechanical enforcement approach per `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`. The assertion is simple and deterministic: for every adapter capability in the registry, `source_sha256` == normalized SHA of the canonical `SKILL.md`.

**Reconciliation discipline:** The proposal correctly warns that the `target_paths` breadth reflects the honest scope of the systemic fix, and that the implementer must use a scoped/hunk-limited commit rather than a blanket worktree sweep given the heavily dirtied worktree. This is an important operational constraint that must be honored during implementation.

**Cross-harness correctness:** The change is inherently cross-harness. `--check` mode must report registry drift for all three generators consistently. Cursor's fallback surface has no generator-maintained `source_sha256` obligation and is correctly excluded.

**Requirement sufficiency confirmed:** `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and the harness-onboarding adapter invariants already require the registry `source_sha256` to be truthful; no new or revised requirement is needed.

**No blocking findings.**

## Conditions / Required Actions

1. **Scoped commit discipline (operational, not blocking).** Per the proposal's own risk note: given the heavily dirtied worktree from concurrent `keep-working-pb` activity, implementation MUST use a scoped/hunk-limited commit capturing only generator edits, the new test, the registry reconciliation hunks, and the regenerated adapter/MANIFEST hunks. A blanket worktree sweep commit is NOT acceptable. If the worktree cannot be cleanly isolated, implementation should pause until it is quiescent.

## Owner Action Required

None.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
