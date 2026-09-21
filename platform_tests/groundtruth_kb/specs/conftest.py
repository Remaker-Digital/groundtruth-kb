"""Read-only formal fitness tests against an explicitly selected native authority.

GTKB_FORMAL_TEST_AUTHORITY_URL is required for tests using ``formal_record`` or
``executable_test_bindings``.
These tests never select a database from the working directory, import a legacy
SQLite fixture, write canonical records or fall back when the service fails.
Behavioral qualification uses separate disposable-authority native tests.
Reads require active status by default. Retirement checks may explicitly name
the expected retired or superseded status without treating that record as active.
``executable_test_bindings`` reads a record's TEST rows from ``/v1/tests`` and
keeps those that name an executable test module of this repository.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.postgres_kernel import canonical_json_bytes

REPO_ROOT = Path(__file__).resolve().parents[3]
# Historical or non-authoritative trees: a TEST row naming a file there binds nothing executable.
NONAUTHORITATIVE_SOURCE_PREFIXES = (".gtkb-state/", "bridge/", "memory/")
TEST_PAGE_LIMIT = 1000


@pytest.fixture(scope="session")
def formal_record():
    url = os.environ.get("GTKB_FORMAL_TEST_AUTHORITY_URL")
    if not url:
        pytest.fail("Set GTKB_FORMAL_TEST_AUTHORITY_URL explicitly for current formal-corpus tests")
    client = AuthorityClient(url)
    observed = {}

    def read(identifier, *, expected_status="active"):
        row = client.request("GET", f"/v1/specifications/{identifier}")
        assert row["id"] == identifier
        assert row["status"] == expected_status, f"{identifier} is not {expected_status}"
        image = canonical_json_bytes(row)
        assert observed.setdefault(identifier, image) == image, f"{identifier} changed during qualification"
        return row

    yield read

    for identifier, image in observed.items():
        current = client.request("GET", f"/v1/specifications/{identifier}")
        assert canonical_json_bytes(current) == image, f"{identifier} changed during qualification"


def _repository_file(raw_path: object) -> Path | None:
    """The existing repository file a TEST row's ``test_file`` names, or None when it names nothing executable."""
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts or path.as_posix().startswith(NONAUTHORITATIVE_SOURCE_PREFIXES):
        return None
    target = REPO_ROOT / path
    return target if target.is_file() else None


def _defines_function(module: Path, name: str, parsed: dict[Path, set[str]]) -> bool:
    if module not in parsed:
        tree = ast.parse(module.read_bytes(), filename=str(module))
        parsed[module] = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        }
    return name in parsed[module]


def _executable_row(row: dict, parsed: dict[Path, set[str]]) -> bool:
    """Whether a TEST row binds an executable test of this repository (the rule ``executable_test_bindings`` states)."""
    module = _repository_file(row.get("test_file"))
    if module is None:
        return False
    function = row.get("test_function")
    if not function:
        return True
    if not isinstance(function, str):
        return False
    # A parametrized case id (``test_x[param]``) binds the def ``test_x``.
    return _defines_function(module, function.split("[", 1)[0].strip(), parsed)


@pytest.fixture(scope="session")
def executable_test_bindings():
    """Read a record's executable TEST bindings natively; the rows are pinned for the session.

    ``GET /v1/tests?spec_id=<id>&limit=1000`` is paged with the ``after`` cursor until ``next_after`` is null and
    the rows are pinned like ``formal_record`` pins a specification. A row is executable when its ``test_file`` is an
    existing file under the repository root (relative, no ``..``, not a historical tree) and its ``test_function``,
    when named, is defined in that file; a parametrized case id (``test_x[param]``) is matched on the def name before
    the ``[``. ``test_class`` is not checked separately (methods are found in the file's whole AST).
    """
    url = os.environ.get("GTKB_FORMAL_TEST_AUTHORITY_URL")
    if not url:
        pytest.fail("Set GTKB_FORMAL_TEST_AUTHORITY_URL explicitly for current formal-corpus tests")
    client = AuthorityClient(url)
    observed: dict[str, bytes] = {}
    parsed: dict[Path, set[str]] = {}

    def rows(record_id: str) -> list[dict]:
        collected: list[dict] = []
        after = None
        while True:
            query = {"spec_id": record_id, "limit": TEST_PAGE_LIMIT, "after": after}
            page = client.request("GET", "/v1/tests", query=query)
            collected.extend(page["records"])
            after = page.get("next_after")
            if not after:
                return collected

    def read(record_id: str) -> list[dict]:
        current = rows(record_id)
        image = canonical_json_bytes(current)
        assert observed.setdefault(record_id, image) == image, f"{record_id}: TEST rows changed during qualification"
        return [row for row in current if _executable_row(row, parsed)]

    yield read

    for record_id, image in observed.items():
        assert canonical_json_bytes(rows(record_id)) == image, f"{record_id}: TEST rows changed during qualification"
