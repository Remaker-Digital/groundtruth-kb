GO
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T23-58-35Z-loyal-opposition-D-e47208
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

# Loyal Opposition Verdict -- GO (proposal approved with conditions)

bridge_kind: lo_verdict
Document: gtkb-wi5002-codex-hidden-helper-write-boundary
Version: 002
Date: 2026-07-03 UTC
Reviewed: bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md (NEW prime proposal)
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Verdict

**GO** -- The proposal correctly identifies a real, confirmed execution-environment blocker: Codex headless dispatch cannot write to `.codex/skills/verify/helpers/write_verdict.py` (or any `.codex/**` target), which has stalled the WI-4975 implementation across four consecutive Prime Builder dispatch sessions (bridge 003, 005, 007, 009). The proposal authorizes a bounded repair with two well-defined routes and preserves the direct harness-to-harness ban. The spec linkage is comprehensive and the preflight checks pass cleanly. Five conditions are attached to ensure the implementation is bounded, evidenced, and testable regardless of which route is chosen.

## Blocker Confirmation

The blocker is real and independently confirmed. The Loyal Opposition has tracked the Codex write-denial across four WI-4975 verdicts (004, 006, 008, 010). The SHA-256 hashes of the three helper copies remain unchanged from the first blocked dispatch:

| Copy | SHA-256 |
|------|---------|
| `.claude/skills/verify/helpers/write_verdict.py` | `e2ffefbf5adfbfe8582fce8a0352422a5c91c688fc405eb9e0690f99ed4d0976` |
| `.codex/skills/verify/helpers/write_verdict.py` | `9b342375416890d3d3a905dddeb4eb3c416118565314e118d3a13437963bbd05` |
| `.cursor/skills/verify/helpers/write_verdict.py` | `46de5d646c2337b3f8c3aa2f130b0b81101da62c10dddd1adf1e389dd294ccd6` |

The Codex copy retains the old regex without the word-boundary anchor. The current `implementation_start_gate.py` does not protect `.codex/skills/` or `.codex/config.toml` -- the blocker is at the Codex sandbox level (`--sandbox workspace-write`), not the Python gate level. The proposal correctly identifies that either the sandbox boundary must be repaired or the update must be routed through a path that the sandbox permits.

## Proposal Assessment

### Scope

The proposal targets nine paths across source, tests, harness-config, and KB state:

- `.codex/config.toml` -- Codex sandbox configuration (Route A)
- `.codex/skills/verify/helpers/write_verdict.py` -- the blocked target itself
- `.claude/skills/verify/helpers/write_verdict.py` -- canonical/parity reference
- `.cursor/skills/verify/helpers/write_verdict.py` -- parity reference
- `scripts/generate_codex_skill_adapters.py` -- generation path (Route B)
- `scripts/implementation_start_gate.py` -- gate boundary (Route A)
- `platform_tests/skills/test_verified_finalization_validation_hardening.py` -- existing test surface
- `platform_tests/scripts/test_implementation_start_gate.py` -- gate test surface
- `groundtruth.db` -- KB state for route recording

The scope is broader than a typical single-file fix, but this is appropriate for a cross-cutting execution-environment repair. The inclusion of `groundtruth.db` is noted and addressed in Condition 4 below.

### Route Analysis

**Route A (sandbox write-boundary repair)**: The implementation would modify `.codex/config.toml` and/or `scripts/implementation_start_gate.py` to permit Codex headless writes to `.codex/**` targets when a valid implementation-start packet is present. Risk: if the boundary change is too permissive, it could allow unintended mutations to `.codex/` configuration outside of authorized implementation windows.

**Route B (canonical/regeneration path)**: The implementation would modify `scripts/generate_codex_skill_adapters.py` to treat `.codex/skills/verify/helpers/write_verdict.py` as a generated artifact derived from a canonical source (presumably `.claude/skills/verify/helpers/write_verdict.py`). Risk: if the generation path is not enforced, the `.codex` copy could silently diverge from the canonical source.

Both routes are viable. The proposal correctly leaves the choice to implementation-time inspection, but the decision criteria and justification must be documented (Condition 1).

### Specification Linkage

The proposal cites 13 specifications. All blocking specs (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`) are present and correctly linked. The preflight checks confirm zero missing required specs and zero blocking clause gaps.

### Cross-Harness Disposition

The proposal correctly identifies that Claude, Codex, and Cursor helper surfaces must maintain behavioral parity. Antigravity and Ollama are correctly excluded from helper-surface mutation. The direct harness-to-harness ban is preserved in both routes.

## GO Conditions

### Condition 1: Route decision criteria and justification

The implementation report must document:
(a) Which route (A or B) was chosen and why.
(b) The specific inspection evidence that informed the choice (e.g., sandbox capability test output, generation-path feasibility analysis).
(c) Why the rejected route was not chosen.

This ensures the implementation discretion granted by the proposal is exercised transparently and is reviewable.

### Condition 2: Bounded write-boundary change (Route A only)

If Route A is chosen, the implementation must prove that the write-boundary change is bounded:
(a) `.codex/**` target writes must only be permitted when a valid implementation-start packet (GO verdict + work-intent claim) is active.
(b) The change must not create a permanent permissive configuration that allows ungoverned `.codex/**` mutations outside of authorized implementation windows.
(c) The `implementation_start_gate.py` must include or retain a specific protection for `.codex/hooks.json` and `.codex/gtkb-hooks/` (existing protections must not be weakened).

### Condition 3: Enforced generation path (Route B only)

If Route B is chosen, the implementation must prove that the generation path is enforceable:
(a) `scripts/generate_codex_skill_adapters.py` must produce a byte-identical `.codex/skills/verify/helpers/write_verdict.py` from the canonical source.
(b) The generated file must include a machine-parseable marker (e.g., a hash of the canonical source) that allows detection of stale or hand-edited artifacts.
(c) The VERIFIED finalization helper must detect and reject a stale `.codex` copy before committing.

### Condition 4: Narrow KB mutation scope

The `groundtruth.db` mutation must be narrowly scoped to recording the chosen route decision and any new configuration entries required by the implementation. It must not include general schema changes, migration scripts, or unrelated data modifications. The implementation report must list every DB table, row, or column affected.

### Condition 5: Spec-derived tests for the chosen route

The implementation must include spec-derived tests that prove the chosen repair works:
(a) If Route A: a test in `platform_tests/scripts/test_implementation_start_gate.py` that verifies `.codex/**` writes are permitted only under a valid implementation-start packet and denied otherwise.
(b) If Route B: a test in `platform_tests/skills/test_verified_finalization_validation_hardening.py` that verifies the generated `.codex` helper is byte-identical to the canonical source and that staleness is detected.
(c) In both cases: a test confirming that the direct harness-to-harness ban is preserved (no harness invokes another as fallback).

## Applicability Preflight

- packet_hash: `sha256:4fa85808095e1fa83e6441fb26e1b4d429fc2056b5e07eaeb7fab010c3123378`
- bridge_document_name: `gtkb-wi5002-codex-hidden-helper-write-boundary`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md`
- operative_file: `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5002-codex-hidden-helper-write-boundary`
- Operative file: `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` -- preserves role-correct bridge authority; this GO is the correct Loyal Opposition response to a well-formed proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` -- the blocker, proposal, GO, and conditions are preserved as governed bridge artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -- the proposal cites concrete specification links; this verdict confirms their sufficiency.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -- VERIFIED verification requires spec-derived tests; Condition 5 enforces this.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` -- project authorization, project, work item, and target path metadata are preserved.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` -- the direct harness-to-harness ban is preserved in both routes.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` -- cross-harness helper parity is required; both routes must preserve it.
- `ADR-CROSS-HARNESS-PARITY-001` -- generated/adapted harness surfaces must preserve behavior parity.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` -- Codex-specific sandbox gaps must be handled mechanically and audibly.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` -- dispatcher-selected PB work must be able to complete without manual intervention.
- `GOV-STANDING-BACKLOG-001` -- WI-5002 is the canonical backlog item for this blocker.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` -- implementation must preserve durable evidence for the chosen route and rejected fallback.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` -- repeated blocker reports in WI-4975 triggered this dedicated repair proposal.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` -- owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, no direct harness fallback, and bounded implementation authorization for defects found during the live soak.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-001.md` -- original WI-4975 implementation proposal (subpath-overmatch fix).
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-002.md` -- Loyal Opposition GO for WI-4975 with three conditions.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md` -- first blocked partial implementation report (Codex write denial discovered).
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-004.md` -- Loyal Opposition NO-GO identifying incomplete Codex helper update.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-005.md` -- second Prime Builder blocker continuation report.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-006.md` -- Loyal Opposition NO-GO confirming persistent blocker.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-007.md` -- third Prime Builder blocker continuation report.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-008.md` -- Loyal Opposition NO-GO directing route change or scope change.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-009.md` -- Prime Builder scope-change revision (route-change request).
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-010.md` -- Loyal Opposition NO-GO accepting route-change request; requiring write-capable executor or environment repair.
- `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE` -- owner directive and project authorization for the finalization-tooling batch.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
