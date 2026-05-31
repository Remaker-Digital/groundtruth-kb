"""Authority-label enum + JSON envelope schema for the GT-KB MCP surface.

Every MCP response wraps its payload in an envelope that names its authority
class. Consumers MUST inspect the label before treating the payload as
canonical. The six labels are:

- ``authoritative`` -- payload is the canonical source-of-truth row (e.g., a
  MemBase work-item record, the current text of a rule file).
- ``generated-summary`` -- payload is computed or derived at request time
  (counts, dashboards, audit summaries). Not canonical.
- ``advisory`` -- payload is a recommendation, not enforceable.
- ``allowed`` -- the requested operation is permitted in the current role/scope.
- ``denied`` -- the requested operation is refused (role-restricted or
  boundary-violating).
- ``owner-approval-required`` -- the requested operation requires owner
  approval (via AskUserQuestion) before proceeding.

Slice 1 ships the schema and the proof-of-pattern ``gt_status_summary`` tool,
which emits ``generated-summary`` payloads. Subsequent slices add additional
tools that emit other authority classes.
"""

from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import Any


class AuthorityLabel(StrEnum):
    """Authority class of an MCP response payload.

    Subclassing ``str`` keeps JSON serialization trivial (``json.dumps``
    encodes the value as the bare string).
    """

    AUTHORITATIVE = "authoritative"
    GENERATED_SUMMARY = "generated-summary"
    ADVISORY = "advisory"
    ALLOWED = "allowed"
    DENIED = "denied"
    OWNER_APPROVAL_REQUIRED = "owner-approval-required"


# Canonical label set in declaration order. Consumers MAY iterate this for
# exhaustiveness checks; the order is stable across releases.
ALL_LABELS: tuple[AuthorityLabel, ...] = tuple(AuthorityLabel)


def build_envelope(
    *,
    authority: AuthorityLabel,
    payload: Any,
    source_ref: str,
    generated_at: dt.datetime | None = None,
) -> dict[str, Any]:
    """Wrap an MCP tool result in the canonical authority envelope.

    Parameters
    ----------
    authority:
        The authority class of the payload. Tools MUST pick the most
        restrictive accurate label.
    payload:
        The tool-specific result body. May be any JSON-serializable structure.
    source_ref:
        A canonical, in-root reference identifying where the payload came from
        (e.g., ``"bridge/INDEX.md"``, ``"groundtruth.db#work_items"``). Used by
        consumers to chase provenance.
    generated_at:
        Timestamp the envelope was constructed. Defaults to the current UTC
        instant. Use the explicit parameter only for deterministic tests.

    Returns
    -------
    dict
        A JSON-ready envelope with the four canonical fields. The shape is
        stable across the GT-KB MCP surface releases.
    """

    if not isinstance(authority, AuthorityLabel):
        raise TypeError(f"authority must be an AuthorityLabel, got {type(authority).__name__}")
    if generated_at is None:
        generated_at = dt.datetime.now(dt.UTC)
    return {
        "authority": authority.value,
        "payload": payload,
        "source_ref": source_ref,
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
    }
