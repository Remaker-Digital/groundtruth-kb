NEW

# Implementation Proposal — GT-KB MCP Stable Harness Surface

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-mcp-stable-harness-surface-implementation`
**Builds on:** `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md`

## 1. Scope

Implements an MCP (Model Context Protocol) server surface providing stable access to MemBase, Deliberation Archive, and Dashboard services for AI harnesses.

## 2. Deliverables

### 2.1 MCP Server (`groundtruth_kb.mcp_surface.server`)

- FastMCP-based implementation.
- Tools: `read_spec`, `search_deliberations`, `get_dash_summary`, `record_work_item`.
- Guards: Authority check for the active role (Prime vs. LO).

### 2.2 Harness Configuration

- Configuration templates for Claude Code and Codex to connect to the MCP server.

### 2.3 Test Suite

- `tests/framework/test_mcp_surface_tools.py`

## 3. Execution Plan

1. Implement the tool-mapping layer in `groundtruth_kb.mcp_surface`.
2. Implement the server entry point.
3. Verify tool responses against direct DB queries.

## 4. Reversibility

- The MCP server is a secondary surface. Core CLI and DB access remain authoritative.
