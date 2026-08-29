"""Canonical role vocabulary for the GT-KB MCP surface.

A role belongs to a session context, not to a harness. It is established by the
exact ``::init gtkb <pb|lo>`` line the owner supplies in an interactive session
or that appears in the header of a dispatchable bridge item, and it is immutable
for that context.

This module therefore carries the role vocabulary only. It resolves no role: a
harness identity is not an input to role resolution, so there is nothing here to
resolve one from.
"""

from __future__ import annotations

CANONICAL_ROLES: frozenset[str] = frozenset({"prime-builder", "loyal-opposition"})
