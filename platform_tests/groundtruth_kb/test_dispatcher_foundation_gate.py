"""The dispatcher foundation-first gate is checked against MemBase, not against a bridge file (WI-6661).

``DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`` is an active ``P0`` design constraint. Its
assertions previously required an ephemeral bridge file as evaluation evidence: one ``file_exists``
and four ``grep`` checks against ``bridge/gtkb-dispatcher-black-box-spec-foundation-024.md``. That
path is untracked and ignored by ``.gitignore`` line 621, so the assertion passed in a working tree
that happened to hold the file and failed in every clone.

Live ``GOV-FILE-BRIDGE-AUTHORITY-001`` holds bridge items ephemeral and not sources of truth, so a
formal assertion contract may not depend on one.

The substitution is lossless, which is measurable rather than asserted: all four grep patterns appear
verbatim in the DCL's own description, so the specification was greping an ephemeral copy of text it
already carried canonically. This file checks the constraint the DCL *states* instead of the presence
of a document that states it.

Bound to TEST-12621.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_DB = REPO_ROOT / "groundtruth.db"

DCL_ID = "DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001"
FOUNDATION = "WI-5268"
DOWNSTREAM = tuple(f"WI-{n}" for n in range(5269, 5277))

#: States meaning a work item has finished, one way or another.
TERMINAL = frozenset({"resolved", "closed", "superseded", "withdrawn", "cancelled", "retired", "wont_fix", "verified"})

#: States meaning implementation actually completed, as opposed to being abandoned.
COMPLETED = frozenset({"resolved", "verified"})

#: The normative phrases the DCL's description must keep carrying. These are the exact strings the
#: retired assertions grepped for in the bridge file; keeping them asserted here is what makes the
#: substitution lossless rather than merely smaller.
NORMATIVE_PHRASES = (
    "WI-5268 is the foundation work item",
    "WI-5269 through WI-5276 are downstream",
    "The gate must fail closed",
    "Absence of those citations is a blocking proposal defect",
)


def _connect() -> sqlite3.Connection:
    if not LIVE_DB.exists():
        pytest.skip("live MemBase not present in this checkout")
    return sqlite3.connect(f"file:{LIVE_DB}?mode=ro", uri=True)


def _latest_spec(conn: sqlite3.Connection, spec_id: str) -> tuple[str, str | None]:
    row = conn.execute(
        "SELECT description, assertions FROM specifications WHERE id = ? ORDER BY version DESC LIMIT 1",
        (spec_id,),
    ).fetchone()
    if row is None:
        pytest.skip(f"{spec_id} not present in this checkout")
    return row[0] or "", row[1]


def _latest_status(conn: sqlite3.Connection, work_item_id: str) -> str | None:
    row = conn.execute(
        "SELECT resolution_status FROM work_items WHERE id = ? ORDER BY version DESC LIMIT 1",
        (work_item_id,),
    ).fetchone()
    return None if row is None else str(row[0])


def test_the_dcl_asserts_no_bridge_path() -> None:
    """No assertion of this DCL may depend on an ephemeral bridge file.

    Walks the assertion tree's path-bearing fields rather than grepping the serialized blob. That
    distinction matters: a substring sweep for ``bridge/`` across all specifications returns five
    hits, of which only this one was actionable — one targets
    ``groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py``, a tracked source module whose directory
    is coincidentally named ``bridge``, and two mention bridge paths only in prose descriptions.
    """
    conn = _connect()
    _, raw = _latest_spec(conn, DCL_ID)
    offenders: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"file", "path", "target"} and isinstance(value, str) and value.startswith("bridge/"):
                    offenders.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(json.loads(raw) if raw else [])
    assert offenders == [], (
        f"{DCL_ID} asserts against ephemeral bridge paths: {sorted(set(offenders))}. "
        "GOV-FILE-BRIDGE-AUTHORITY-001 holds bridge items ephemeral and not sources of truth."
    )


def test_foundation_and_downstream_work_items_are_declared() -> None:
    """The work items the constraint names must exist in MemBase.

    A gate naming work items that do not exist enforces nothing, and the failure would be invisible
    while the constraint still read as active.
    """
    conn = _connect()
    missing = [wid for wid in (FOUNDATION, *DOWNSTREAM) if _latest_status(conn, wid) is None]
    assert missing == [], f"{DCL_ID} names work items absent from MemBase: {missing}"


def test_downstream_items_are_gated_on_the_foundation() -> None:
    """The fail-closed direction: no downstream item completes ahead of the foundation.

    This is the constraint's substance. While ``WI-5268`` is non-terminal, none of ``WI-5269`` through
    ``WI-5276`` may be in a completed state, because completing downstream implementation before its
    governance foundation is exactly what the gate exists to prevent.

    Abandonment is not completion: an item that is ``retired`` or ``wont_fix`` never implemented
    anything, so it does not violate the ordering and is not counted here.
    """
    conn = _connect()
    foundation = _latest_status(conn, FOUNDATION)
    if foundation in TERMINAL:
        premature = []
    else:
        premature = [wid for wid in DOWNSTREAM if _latest_status(conn, wid) in COMPLETED]
    assert premature == [], (
        f"{FOUNDATION} is {foundation!r} (non-terminal) while downstream items have completed: "
        f"{premature}. The foundation-first gate requires the reverse ordering."
    )


def test_the_constraint_text_survives_in_membase() -> None:
    """The four normative phrases must remain in the DCL's own description.

    These are the strings the retired bridge assertions grepped for. Asserting them here against
    MemBase is what makes the substitution lossless: the constraint text is now checked where it
    canonically lives instead of in an ignored copy of itself.
    """
    conn = _connect()
    description, _ = _latest_spec(conn, DCL_ID)
    missing = [phrase for phrase in NORMATIVE_PHRASES if phrase not in description]
    assert missing == [], (
        f"{DCL_ID}'s description no longer carries its normative phrases: {missing}. "
        "The constraint text is the specification; losing it silently empties the gate."
    )
