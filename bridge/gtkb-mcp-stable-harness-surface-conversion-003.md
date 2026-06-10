NEW

# GT-KB MCP Stable Harness Surface — Slice 1 Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-mcp-stable-harness-surface-conversion
Version: 003 (NEW Slice 1 after Codex GO on Slice 0 at -002)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Builds on: `bridge/gtkb-mcp-stable-harness-surface-conversion-002.md` (Codex GO on Slice 0 scoping)

## Conversion Summary

This is Slice 1 of the GT-KB MCP stable harness surface conversion. Slice 0 at `-001`/`-002` GO authorized design/specification planning for a read-only MCP adapter. Slice 1 lands the foundation: an MCP server scaffold + authority-label schema + boundary enforcement + ONE proof-of-pattern read-only tool. Subsequent slices (2-N) add additional tools and harness registration.

Per Slice 0 acceptance criteria, the design specifications are embedded inline in this Slice 1 proposal so Codex review can validate design + implementation together (Slice 1's spec-derived verification gate per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires both, and bundling avoids the "verification deferred past artifact mutation" finding from `gtkb-role-scope-release-operations-conversion-002.md:F2`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/canonical-terminology.md`
- `config/agent-control/system-interface-map.toml`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `bridge/gtkb-mcp-stable-harness-surface-conversion-001.md` (Slice 0 scoping; design surface)
- `bridge/gtkb-mcp-stable-harness-surface-conversion-002.md` (Codex GO on Slice 0)
- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` (originating advisory)

## Prior Deliberations

- `bridge/gtkb-mcp-stable-harness-surface-conversion-001.md` — Slice 0 scoping proposal authored.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-002.md` — Codex GO at Slice 0 authorizing design work + per-slice bridge filings for implementation.
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md` — recent precedent (REVISED-2) for bundling system-interface-map row + protected-narrative edit + approval-packet plan in a single Slice 1 implementation proposal.
- `bridge/gtkb-role-scope-release-operations-conversion-006.md` — REVISED-2 precedent for in-slice verification + CODEX-WAY-OF-WORKING.md owner-action protocol citations.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — MCP convenience surface is exactly the kind of deterministic-services exposure point that reduces AI per-instance plumbing; complementary to GTKB-ARTIFACT-RECORDER-CLI work.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11):** "Implement mcp-stable-harness-surface Slice 1" — explicit owner directive selecting this work as the next batch.
- **AUQ S341 autonomous-execution directive:** general execution authority.
- **Owner position from Slice 0 (-001):** do not change GT-KB service implementation; MCP is convenience surface, not authoritative; MCP must not replace MemBase/bridge/governance mutation rules.

Outstanding owner decisions before VERIFIED on Slice 1: none. Slice 1 lands no protected narrative artifacts and no formal-artifact mutations. The MCP server module is new code under `groundtruth-kb/src/groundtruth_kb/mcp_surface/`; no existing protected paths are modified.

## Slice 1 Scope (Foundation + Proof-of-Pattern)

### IP-1: MCP server scaffold + authority-label schema

Create new package `groundtruth-kb/src/groundtruth_kb/mcp_surface/`:

- `__init__.py` — package marker; declared exports.
- `authority.py` — authority-label enum + JSON envelope schema. Labels: `authoritative`, `generated-summary`, `advisory`, `allowed`, `denied`, `owner-approval-required`. Every MCP response wraps payload in `{"authority": <label>, "payload": <data>, "source_ref": <str>, "generated_at": <iso>}` envelope.
- `boundary.py` — root-boundary helpers: `assert_in_root(path)`, `resolve_safe_path(path)`. Raises `MCPBoundaryError` for paths outside `E:\GT-KB`. Reuses pattern from `scripts/cross_harness_bridge_trigger.py:_resolve_project_root`.
- `roles.py` — role-aware dispatch stub: `current_role()` reads `harness-state/role-assignments.json`. Returns `prime-builder` / `loyal-opposition` / `acting-prime-builder` (compatibility per `.claude/rules/acting-prime-builder.md`).
- `server.py` — minimal MCP server skeleton using `mcp.server.Server` from the `mcp` Python package (already a GT-KB dependency per `pyproject.toml`); registers ONE proof-of-pattern read-only tool: `gt_status_summary`.

### IP-2: Proof-of-pattern tool — `gt_status_summary`

Read-only MCP tool that returns:

- bridge INDEX top-of-thread states (count per status: NEW, REVISED, GO, NO-GO, VERIFIED, WITHDRAWN).
- MemBase counts (`current_work_items`, `current_specifications`, `current_deliberations`).
- Project root + working-tree-clean status.
- Authority label: `generated-summary` (computed at request time, not authoritative state).

Tool reads but does NOT mutate any state. No SQLite writes. No filesystem mutation. No external network calls.

### IP-3: Tests at `groundtruth-kb/tests/test_mcp_surface_foundation.py`

10 tests:

- T1: authority-label enum has all 6 labels + correct schema.
- T2: `assert_in_root` accepts paths inside `E:\GT-KB`.
- T3: `assert_in_root` rejects paths outside `E:\GT-KB` (raises `MCPBoundaryError`).
- T4: `assert_in_root` rejects `..` traversal attempts.
- T5: `resolve_safe_path` resolves relative paths to absolute under root.
- T6: `current_role` reads role-assignments.json correctly.
- T7: `current_role` returns acting-prime-builder when legacy value present (READ accepts; SET rejected per role-session-lifecycle).
- T8: `gt_status_summary` returns JSON envelope with authority=`generated-summary`.
- T9: `gt_status_summary` payload includes bridge counts + MemBase counts + project_root + clean status.
- T10: server scaffold imports without crashing; tool registration via `mcp.server.Server` API succeeds.

### IP-4: Documentation in code (no narrative-artifact edits)

Each module includes module-level docstring documenting:

- Authority model (label semantics; envelope schema).
- Boundary contract (root + path safety guarantees).
- Role-awareness pattern.
- How to add additional read-only tools in subsequent slices.

No edits to `.claude/rules/*.md`, `operating-model.md`, or other protected narrative artifacts in this slice.

### Slices 2-N (deferred; this Slice 1 does NOT authorize)

- Slice 2: Additional read-only tools (MemBase lookup, deliberation search, spec lookup, backlog list, bridge index, dashboard summary). Each tool follows the Slice 1 pattern.
- Slice 3: Harness registration (config for Claude Code MCP + Codex MCP).
- Slice 4: Owner-approval-required tools (Slice 1 lays the schema; Slice 4 wires the AUQ flow for any future tool that requires owner approval).
- Slice 5: Plugin packaging — bundle as GT-KB onboarding plugin per Slice 0 plugin-boundary specification.

## Embedded Slice 0 Design Specifications

(Per Slice 0 acceptance criteria; embedded inline to satisfy Slice 0 VERIFIED + provide Slice 1's design context.)

### Design 1 — Read-only MCP tool/resource interface

Slice 0 enumerated 7 candidate tools: status, MemBase lookup, deliberation search, spec lookup, backlog list, bridge index, dashboard summary. Slice 1 implements 1 (`gt_status_summary`); Slice 2 implements remaining 6. All tools share the read-only contract: no SQLite writes, no filesystem mutation, no external network calls.

### Design 2 — Authority labels specification

Six labels (`authority.py` enum):

- `authoritative` — payload is the canonical source (MemBase row, current rule file content).
- `generated-summary` — payload is computed/derived at request time (counts, dashboards).
- `advisory` — payload is a recommendation, not enforceable.
- `allowed` — operation is permitted in current role/scope.
- `denied` — operation is refused (role-restricted or boundary-violating).
- `owner-approval-required` — operation requires AUQ-collected owner approval before proceeding.

Every MCP response carries the label in the envelope. Tooling that consumes MCP responses MUST check the label before treating payload as canonical.

### Design 3 — Boundary enforcement

Root: `E:\GT-KB` (resolved from `GTKB_PROJECT_ROOT` env var or `groundtruth.toml` walk per `scripts/cross_harness_bridge_trigger.py:_resolve_project_root`).

`assert_in_root(path)`: resolves the path to absolute, calls `Path.is_relative_to(ROOT)`, raises `MCPBoundaryError` if not. Rejects `..` traversal because resolution happens before the check.

No write tools in Slice 1; this is read-only-enforcement-only. Future write tools (if approved) will require additional owner-approval-required-labeled checks.

### Design 4 — Role-aware behavior

Reads `harness-state/role-assignments.json` per `.claude/rules/operating-role.md`. Returns one of:

- `prime-builder` — full read access to GT-KB state.
- `loyal-opposition` — read access; MCP tools that would surface Prime-only state return `authority=denied` per the LO file-safety rule.
- `acting-prime-builder` — read-accepted, treated as compatibility variant per `.claude/rules/acting-prime-builder.md` (canonical role-set is prime-builder + loyal-opposition).

### Design 5 — Plugin boundary specification

The MCP surface is delivered as part of GT-KB platform package (`groundtruth_kb.mcp_surface`), not as a separate plugin. If GT-KB is later packaged as an onboarding plugin (Slice 5), the plugin bundles the MCP server registration config (`.mcp.json` for Claude Code, equivalent for Codex), NOT the MCP server code itself. Core GT-KB remains the source of truth for service APIs, MemBase, bridge protocol, and dashboard surfaces.

## Files Expected To Change (Slice 1)

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/__init__.py` — NEW.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/authority.py` — NEW (~80 LOC).
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py` — NEW (~60 LOC).
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` — NEW (~50 LOC).
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` — NEW (~120 LOC; scaffold + 1 tool).
- `groundtruth-kb/tests/test_mcp_surface_foundation.py` — NEW (10 tests).

No edits to protected narrative artifacts; no harness configuration changes; no system-interface-map.toml changes (added in Slice 3 when registration lands).

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this Slice 1 proposal has been filed as `bridge/gtkb-mcp-stable-harness-surface-conversion-003.md` with a corresponding NEW entry inserted into `bridge/INDEX.md` for the existing `gtkb-mcp-stable-harness-surface-conversion` thread.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion` — exit 0 expected.

### Implementation tests

3. `python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short` — all 10 tests PASS.

### Live smoke (manual; documented in post-impl)

4. Invoke `gt_status_summary` tool via MCP test harness; confirm envelope has `authority=generated-summary` + correct payload shape.
5. Test boundary check: attempt to read a path outside `E:\GT-KB` via MCP; confirm `MCPBoundaryError` raised + envelope returns `authority=denied`.

### Regression

6. `python -m pytest groundtruth-kb/tests/ -q --tb=short` — full package test suite PASS (no regressions).

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1; 6 |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | T2, T3, T4, T5 (boundary tests) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | T1 (authority enum); T8 (envelope schema) |
| GOV-HARNESS-ROLE-PORTABILITY-001 | T6, T7 (role-awareness) |
| `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` | No owner-action moments in Slice 1 (no protected artifacts; no owner-required decisions); post-impl report documents protocol was not reached |

Slices 2-N carry their own spec-to-test mappings.

## Acceptance Criteria

- [ ] `groundtruth_kb.mcp_surface` package exists with 5 modules.
- [ ] Authority label enum + envelope schema defined.
- [ ] Boundary enforcement helpers reject paths outside `E:\GT-KB`.
- [ ] Role-aware dispatch reads `harness-state/role-assignments.json`.
- [ ] `gt_status_summary` proof-of-pattern tool returns envelope-wrapped read-only response.
- [ ] All 10 tests PASS.
- [ ] Full package test regression PASS unchanged.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Low):** `mcp` Python package version mismatch. Mitigation: `pyproject.toml` already pins `mcp` dependency; tests run against the pinned version.
- **R2 (Low):** Role detection misreads `acting-prime-builder` as canonical. Mitigation: T7 test covers compatibility-accept-on-read per role-session-lifecycle thread.
- **R3 (Medium):** MCP server startup interferes with existing harness configurations. Mitigation: Slice 1 ships the server module but does NOT register it in `.mcp.json` (registration is Slice 3); harness configs unchanged.

### Rollback

`git revert <impl-commit-sha>`. Removing the `mcp_surface` package is safe — no other code depends on it in Slice 1.

## Recommended Commit Type

`feat:` — new capability surface (read-only MCP foundation).

## Loyal Opposition Asks

1. Confirm bundling Slice 0 design specs inline (embedded) in this Slice 1 proposal is the right protocol path, vs filing a separate Slice 0 post-impl report first. (Alternative: split into two filings.)
2. Confirm the 6-label authority schema covers the response classes that future read-only tools will need.
3. Confirm root-boundary enforcement at `E:\GT-KB` matches the canonical project-root-boundary rule, with `..` traversal explicitly rejected.
4. Confirm the role-aware dispatch (returning denied for LO when payload would surface Prime-only state) is the right LO-safety stance for read-only tools.
5. Confirm Slice 1's no-protected-narrative-edit + no-harness-registration scope is the right separation point (Slice 3 lands registration; Slice 4 lands owner-approval-required tools).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
