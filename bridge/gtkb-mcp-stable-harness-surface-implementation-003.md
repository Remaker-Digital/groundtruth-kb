REVISED
author_identity: Prime Builder (antigravity/pb)
author_harness_id: C
author_session_context_id: 289a2f12-2a8f-494d-be22-ebfb4abcbf16
author_model: Gemini 3.5 Flash
author_model_version: gemini-3.5-flash
author_model_configuration: Antigravity IDE on Windows 11

# Implementation Proposal — GT-KB MCP Stable Harness Surface

**Status:** REVISED
**Document name:** `gtkb-mcp-stable-harness-surface-implementation`
**Version:** 003
**Builds on:** `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` (adopted via owner agreement to proceed with Option A)

## Specification Links

- [GOV-FILE-BRIDGE-AUTHORITY-001](file:///E:/GT-KB/config/governance/gov-file-bridge-authority-001.md) — Live bridge index authority.
- [DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Bridge proposal spec linkage must be complete.
- [DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Verification must execute spec-derived tests.
- [ADR-ISOLATION-APPLICATION-PLACEMENT-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Placement contract for application isolation.
- [GOV-HARNESS-ONBOARDING-CONTRACT-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Harness onboarding validation contract.

## Prior Deliberations

- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` (NO-GO) — The originating advisory recommending a typed MCP adapter instead of ad-hoc prompt/file scraping.
- `bridge/gtkb-mcp-stable-harness-surface-implementation-002.md` (NO-GO) — The LO review of proposal version 001 raising findings on missing specs, target paths, dependencies, and role guard designs.

## Implementation Scope

- **Project:** `PROJECT-HARNESS-REGISTRY-REFACTOR` (or `PROJECT-GT-KB-INFRASTRUCTURE` fallback)
- **Work Item:** `WI-3297` (or new WI tracking the MCP surface)
- **Requirement Sufficiency:** Existing requirements sufficient.
- **target_paths:**
  - `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py`
  - `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`
  - `groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py`
  - `groundtruth-kb/src/groundtruth_kb/mcp_surface/authority.py`
  - `groundtruth-kb/tests/framework/test_mcp_surface_tools.py`

All target paths reside in-root under the project directory (`E:\GT-KB`), satisfying the placement requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Resolution of Findings

### 1. Specification Links (FINDING-P0-001)
Added mandatory specification links and references to governing specs in this proposal.

### 2. Implementation Scope and Target Paths (FINDING-P0-002)
Formally declared the target paths listing package files under `groundtruth_kb/mcp_surface/` and the test file under `tests/`. Requirement Sufficiency is declared as sufficient.

### 3. Advisory Adoption (FINDING-P0-003)
Advisory `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` was formally adopted through the owner's choice to proceed with this implementation thread.

### 4. Dependency Declaration (FINDING-P1-001)
The python `mcp` SDK package (specifically version `mcp>=1.0`) natively includes `fastmcp` under `mcp.server.fastmcp`. The `mcp` dependency is already declared under optional `bridge` dependencies in `groundtruth-kb/pyproject.toml`. No separate PyPI dependency package is required.

### 5. Role-Based Access Control Design (FINDING-P1-002)
Role-awareness is implemented in `groundtruth_kb.mcp_surface.roles.current_role` by:
1. Identifying the host harness name from environment variables (e.g., Claude or Codex indicators).
2. Querying `groundtruth_kb.harness_projection.read_roles` to find the corresponding harness record from the canonical registry `harness-state/harness-registry.json`.
3. Normalizing the multi-valued role-set to a display/label role scalar token (e.g., `prime-builder` or `loyal-opposition`).
4. Defaulting to `"unknown"` (fail-closed) when the process cannot resolve the hosting environment or registry matches.

## Specification-Derived Verification Plan

### Test Scenarios
- **Test Server Initialization:** Verify `build_server()` correctly constructs the `Server` instance with the `gt_status_summary` tool registered.
- **Test Role Identification:** Verify `current_role` correctly resolves from a mock or real `harness-registry.json` without failing.
- **Test Path Boundary Guard:** Verify `resolve_safe_path` throws `MCPBoundaryError` when traversing outside the project root.
- **Test Authority Envelope:** Verify that responses from `gt_status_summary` are properly wrapped in the authority envelope showing `generated-summary` status.

### Automated Tests
- Run: `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/ -k mcp_surface` (or equivalent test command)

## target_paths

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py`
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py`
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/authority.py`
- `groundtruth-kb/tests/test_mcp_surface_foundation.py`

## Requirement Sufficiency

Existing requirements sufficient

---
Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
