"""A target column's type must agree with the API annotation for that column (WI-7714).

``postgresql_v1.sql`` declares nine columns ``JSONB`` that ``KnowledgeDB``'s write API declares
``str | None`` and SQLite declares ``TEXT``. A stored ``application_scope`` of ``gtkb_platform``, or a
``related_deliberation_ids`` of a bare ``DELIB-...`` id, is therefore exactly what the API contract
specifies -- correct data -- and it fails export only because ``_json_from_sqlite`` is asked to
JSON-decode a column that was never JSON. 3,088 values are affected.

This was misdiagnosed twice before it was measured. It was first recorded as 7,907 values
double-encoded including all of ``deliberations.participants`` (that column is clean, and the loaded
``specifications.assertions`` is 2,154 correct arrays against 7 strings -- the opposite of the claim).
It was then recorded as data corruption needing an owner ruling on what a bare id means. The API
already answers that, and repairing the 3,088 as data would have rewritten correct records to match an
incorrect schema.

A type disagreement between two declarations of the same column is the kind of fact a machine should
assert and a reader should not have to re-derive. That is what this file is for.

Bound to TEST-12601. Governed by ``DCL-POSTGRES-TARGET-SCHEMA-INVARIANTS-001``, whose structural
family this is the second instalment of.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET_DDL = REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "postgresql_v1.sql"
KERNEL = REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "postgres_kernel.py"

#: The nine columns the target declares ``JSONB`` while the write API declares them scalar.
#:
#: This set is a **pin, not a tolerance**. A tenth disagreement fails
#: :func:`test_the_known_type_disagreements_are_exactly_these_nine`, and so does a repaired one --
#: the assertion is an equality on the set, so the list can only shrink by a deliberate edit rather
#: than rot into a permanent allowance.
KNOWN_TYPE_DISAGREEMENTS = frozenset(
    {
        ("specifications", "application_scope"),
        ("tests", "application_scope"),
        ("work_items", "related_deliberation_ids"),
        ("work_items", "related_spec_ids_at_creation"),
        ("work_items", "related_bridge_threads"),
        ("work_items", "depends_on_work_items"),
        ("work_items", "blocks_work_items"),
        ("work_items", "supersedes"),
        ("work_items", "superseded_by"),
    }
)

#: Table -> the ``KnowledgeDB`` writer whose signature declares that table's column types.
API_WRITERS = {
    "specifications": "insert_spec",
    "tests": "insert_test",
    "work_items": "insert_work_item",
    "documents": "insert_document",
    "deliberations": "insert_deliberation",
    "test_plan_phases": "insert_test_plan_phase",
    "operational_procedures": "insert_operational_procedure",
}


def _ddl_jsonb_columns() -> set[tuple[str, str]]:
    """``(table, column)`` pairs the v1 target declares ``JSONB``.

    The DDL qualifies every table name with a ``{schema}`` placeholder substituted at apply time, so
    a pattern that ignores the prefix matches nothing and reports an empty target schema -- which
    reads as "no tables declared" rather than as a parse failure. That error was made and caught while
    this work was measured, so the prefix is part of the pattern here.
    """
    if not TARGET_DDL.exists():
        pytest.skip("PostgreSQL v1 target DDL not present in this checkout")
    text = TARGET_DDL.read_text(encoding="utf-8")
    found: set[tuple[str, str]] = set()
    for block in re.finditer(
        r"CREATE TABLE (?:IF NOT EXISTS )?\{schema\}\.([a-z_]+)\s*\((.*?)\n\);", text, re.S | re.I
    ):
        table = block.group(1)
        for column in re.findall(r"^\s*([a-z_]+)\s+JSONB", block.group(2), re.M | re.I):
            found.add((table, column))
    return found


def _kernel_json_columns() -> set[tuple[str, str]]:
    """``(table, column)`` pairs the kernel lists in ``json_columns``, read by AST.

    Parsed rather than imported on purpose. ``postgres_kernel.py`` cannot currently be imported at
    all -- its sole first-party import, ``PostgreSQLConfig``, is absent from ``groundtruth_kb.config``
    -- so an import-based reader would make this file uncollectable for a reason unrelated to what it
    asserts. Reading the source keeps the check independent of that repair.
    """
    if not KERNEL.exists():
        pytest.skip("PostgreSQL kernel not present in this checkout")
    tree = ast.parse(KERNEL.read_text(encoding="utf-8"))
    found: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        keywords = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        if "json_columns" not in keywords:
            continue
        name = keywords.get("name")
        table = name.value if isinstance(name, ast.Constant) and isinstance(name.value, str) else None
        if table is None:
            # The spec builder takes the table name positionally in some call sites.
            first = node.args[0] if node.args else None
            table = first.value if isinstance(first, ast.Constant) and isinstance(first.value, str) else None
        if table is None:
            continue
        columns = keywords["json_columns"]
        if isinstance(columns, (ast.Tuple, ast.List)):
            for element in columns.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    found.add((table, element.value))
    return found


def _api_annotation(table: str, column: str) -> str | None:
    """The annotation the write API declares for a column, or ``None`` if it exposes no parameter."""
    writer = API_WRITERS.get(table)
    if not writer:
        return None
    method = getattr(KnowledgeDB, writer, None)
    if method is None:
        return None
    parameter = inspect.signature(method).parameters.get(column)
    return None if parameter is None else str(parameter.annotation)


def _is_collection(annotation: str) -> bool:
    return "list" in annotation or "dict" in annotation or "Any" in annotation


# --- the conformance family -----------------------------------------------


def test_jsonb_columns_have_collection_annotations() -> None:
    """Every JSONB column the API exposes carries a collection annotation, bar the known nine.

    A scalar annotation on a JSONB column means the kernel will JSON-decode a value the contract says
    is a plain string, which raises ``invalid_source`` at the SQLite read.
    """
    offenders: list[str] = []
    for table, column in sorted(_ddl_jsonb_columns()):
        annotation = _api_annotation(table, column)
        if annotation is None:
            continue  # not an API parameter; nothing declares a competing type
        if not _is_collection(annotation) and (table, column) not in KNOWN_TYPE_DISAGREEMENTS:
            offenders.append(f"{table}.{column}: JSONB in the target, {annotation} in the API")
    assert offenders == [], (
        f"new target/API column-type disagreements: {offenders}. Either correct the column type or "
        "add it to KNOWN_TYPE_DISAGREEMENTS with a reviewed reason."
    )


def test_the_known_type_disagreements_are_exactly_these_nine() -> None:
    """The pin: equality, so it fails in both directions.

    A tenth disagreement fails this. So does a repaired one — the set can only change by a deliberate
    edit to the list above, which is what makes it a pin rather than a standing allowance. A subset
    check would let the real gap grow silently, and a superset check would let a repair go unnoticed.
    """
    observed: set[tuple[str, str]] = set()
    for table, column in _ddl_jsonb_columns():
        annotation = _api_annotation(table, column)
        if annotation is not None and not _is_collection(annotation):
            observed.add((table, column))

    assert observed == KNOWN_TYPE_DISAGREEMENTS, (
        f"the measured disagreement set changed. "
        f"newly disagreeing: {sorted(observed - KNOWN_TYPE_DISAGREEMENTS)}; "
        f"no longer disagreeing: {sorted(KNOWN_TYPE_DISAGREEMENTS - observed)}. "
        "A repair must shrink KNOWN_TYPE_DISAGREEMENTS in the same change."
    )


def test_ddl_jsonb_and_kernel_json_columns_agree() -> None:
    """Two hand-maintained lists of the same fact must not drift apart.

    ``postgresql_v1.sql`` and the kernel's ``json_columns`` each independently decide which columns
    are JSON. Nothing reconciles them, so this does.
    """
    ddl = _ddl_jsonb_columns()
    kernel = _kernel_json_columns()
    if not kernel:
        pytest.skip("no json_columns declarations parsed from the kernel")

    ddl_only = sorted(c for c in ddl - kernel if c[0] in {t for t, _ in kernel})
    kernel_only = sorted(kernel - ddl)
    assert ddl_only == [] and kernel_only == [], (
        f"JSONB declarations disagree: in the DDL but not json_columns={ddl_only}; "
        f"in json_columns but not the DDL={kernel_only}"
    )


def test_every_pinned_disagreement_is_still_declared_jsonb() -> None:
    """The pinned nine must remain JSONB in the target.

    If one is retyped to TEXT the disagreement is resolved, and this fails so the pin is updated
    rather than left describing a column that no longer matches it.
    """
    ddl = _ddl_jsonb_columns()
    vanished = sorted(pair for pair in KNOWN_TYPE_DISAGREEMENTS if pair not in ddl)
    assert vanished == [], (
        f"pinned disagreements no longer declared JSONB in the target: {vanished}. "
        "Remove them from KNOWN_TYPE_DISAGREEMENTS in the same change that retyped them."
    )
