"""GT-KB stable MCP harness surface (Slice 1: foundation + proof-of-pattern).

Read-only MCP convenience surface providing GT-KB state lookups under a strict
authority/boundary/role contract. Per the GT-KB MCP stable harness surface
bridge thread (Slice 1 GO at
`bridge/gtkb-mcp-stable-harness-surface-conversion-004.md`):

- All tools are read-only.
- All responses are wrapped in an authority envelope that distinguishes
  `authoritative` payloads (canonical source rows) from `generated-summary`
  payloads (computed at request time).
- All filesystem access is gated through ``boundary.assert_in_root`` to keep
  the surface inside ``E:\\GT-KB``.
- Role awareness is read-only in Slice 1; mutation-class tools are deferred to
  Slice 4.

Subsequent slices add additional read-only tools (Slice 2), harness
registration in ``.mcp.json`` / Codex config (Slice 3), owner-approval-required
tools (Slice 4), and plugin packaging (Slice 5).
"""

from groundtruth_kb.mcp_surface.authority import (
    AuthorityLabel,
    build_envelope,
)
from groundtruth_kb.mcp_surface.boundary import (
    MCPBoundaryError,
    assert_in_root,
    resolve_safe_path,
)
from groundtruth_kb.mcp_surface.roles import (
    CANONICAL_ROLES,
    COMPATIBILITY_ROLES,
    current_role,
)

__all__ = [
    "AuthorityLabel",
    "build_envelope",
    "MCPBoundaryError",
    "assert_in_root",
    "resolve_safe_path",
    "CANONICAL_ROLES",
    "COMPATIBILITY_ROLES",
    "current_role",
]
