"""WI-3342 Slice B (IP-6) — harness-registry reader-migration regression tests.

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` (phased reader migration of
harness role/identity consumers from the legacy harness-state JSON files to the
DB-backed registry projection) and FR9 (the single-prime-builder role
partition that IP-RECON restores), plus ``DELIB-2079`` Q7 (phased migration,
legacy JSON retired last).

Three concerns, per ``bridge/gtkb-harness-registry-reader-migration-005.md``
IP-6 and the ``-006`` GO:

* Part B — migrated readers resolve harness role/identity from the registry
  projection ``harness-state/harness-registry.json`` (the foundational loaders
  ``scripts.harness_roles.load_role_assignments`` /
  ``scripts.harness_identity.load_harness_identities``, and migrated raw-reader
  sites), plus a golden-value comparison against pre-migration role resolution.
* IP-RECON agreement — a deliberately-inverted ``harnesses`` table reconciled
  against an authoritative ``role-assignments.json`` yields corrected
  current-version rows, a regenerated projection, and projection-reader
  accessors that all resolve harness A = loyal-opposition / B = prime-builder
  with the FR9 single-prime-builder partition intact.
* Part C — a no-direct-read scan asserts no *executing* read of
  ``role-assignments.json`` / ``harness-identities.json`` remains under
  ``scripts/``, ``.claude/hooks/``, ``.codex/gtkb-hooks/``, and
  ``groundtruth-kb/src/groundtruth_kb/``, distinguishing executing reads from
  comments, docstrings, and static string constants, with the named exclusion
  allowlist.

All fixtures use isolated ``tmp_path`` roots; the real ``E:\\GT-KB\\groundtruth.db``
and ``harness-state/`` are never read or written.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import (  # noqa: E402
    generate_harness_projection,
    read_roles,
)

from scripts.harness_identity import (  # noqa: E402
    load_harness_identities,
    resolved_harness_id,
)
from scripts.harness_projection_reader import (  # noqa: E402
    harness_by_id,
    id_for_name,
    load_harness_projection,
    role_set_for_id,
)
from scripts.harness_roles import (  # noqa: E402
    ROLE_LOYAL_OPPOSITION,
    ROLE_PRIME_BUILDER,
    load_role_assignments,
)

# ---------------------------------------------------------------------------
# Fixtures: an isolated groundtruth.db registry + generated projection.
# ---------------------------------------------------------------------------


def _seed_registry(root: Path, harnesses: dict[str, tuple[str, list[str]]]) -> KnowledgeDB:
    """Seed an isolated groundtruth.db ``harnesses`` table + generated projection.

    ``harnesses`` maps each durable harness id to ``(harness_name, role_set)``.
    Returns the open ``KnowledgeDB`` so callers can append further versions.
    """
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    for harness_id, (harness_name, role_set) in harnesses.items():
        db.insert_harness(
            id=harness_id,
            harness_name=harness_name,
            harness_type=harness_name,
            role=list(role_set),
            changed_by="test",
            change_reason="WI-3342 IP-6 reader-migration fixture",
            status="active",
        )
    generate_harness_projection(db, root)
    return db


# ===========================================================================
# Part B — migrated readers resolve role/identity from the registry projection.
# ===========================================================================


def test_load_role_assignments_resolves_role_from_projection(tmp_path: Path) -> None:
    """IP-3 foundational loader: ``load_role_assignments`` resolves harness roles
    from the DB-backed registry projection, not the legacy role-assignments.json.

    The legacy file is intentionally absent; resolution still succeeds.
    """
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    assert not (tmp_path / "harness-state" / "role-assignments.json").exists()

    document = load_role_assignments(tmp_path)
    assert document["harnesses"]["A"]["role"] == [ROLE_LOYAL_OPPOSITION]
    assert document["harnesses"]["B"]["role"] == [ROLE_PRIME_BUILDER]


def test_load_harness_identities_resolves_identity_from_projection(
    tmp_path: Path,
) -> None:
    """IP-3 foundational loader: ``load_harness_identities`` resolves harness
    identities from the registry projection, not harness-identities.json.
    """
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    assert not (tmp_path / "harness-state" / "harness-identities.json").exists()

    document = load_harness_identities(tmp_path)
    assert document["harnesses"]["codex"]["id"] == "A"
    assert document["harnesses"]["claude"]["id"] == "B"


def test_resolved_harness_id_resolves_from_projection(tmp_path: Path) -> None:
    """A raw-reader-adjacent site: ``resolved_harness_id`` (the identity
    resolution used across migrated call sites) resolves the durable harness id
    from the registry projection.
    """
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    assert resolved_harness_id(tmp_path, harness_name="codex") == "A"
    assert resolved_harness_id(tmp_path, harness_name="claude") == "B"


def test_kb_attribution_raw_reader_resolves_from_projection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Migrated raw-reader site ``scripts/_kb_attribution.py``: ``_load_role_assignments``
    and ``_load_harness_identities`` resolve from the registry projection via
    the IP-3 foundational loaders (WI-3342 IP-4).
    """
    import scripts._kb_attribution as kb_attr

    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    # _kb_attribution resolves against its module-level PROJECT_ROOT; point it
    # at the isolated fixture root for this test.
    monkeypatch.setattr(kb_attr, "PROJECT_ROOT", tmp_path)

    role_map = kb_attr._load_role_assignments()
    identities = kb_attr._load_harness_identities()
    assert role_map["A"]["role"] == [ROLE_LOYAL_OPPOSITION]
    assert role_map["B"]["role"] == [ROLE_PRIME_BUILDER]
    assert identities["codex"]["id"] == "A"
    assert identities["claude"]["id"] == "B"


def test_cross_harness_trigger_raw_readers_resolve_from_projection(
    tmp_path: Path,
) -> None:
    """Migrated raw-reader site ``scripts/cross_harness_bridge_trigger.py``:
    ``_read_role_assignments`` / ``_read_harness_identities`` resolve the legacy
    document shape from the registry projection (WI-3342 IP-4).
    """
    import importlib.util

    trigger_path = _REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"
    spec = importlib.util.spec_from_file_location("cross_harness_bridge_trigger_readermig", trigger_path)
    assert spec is not None and spec.loader is not None
    trigger = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = trigger
    spec.loader.exec_module(trigger)

    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )

    role_map = trigger._read_role_assignments(tmp_path)
    identities = trigger._read_harness_identities(tmp_path)
    # Legacy document shape: {"harnesses": {harness_id: record}}.
    assert role_map["harnesses"]["A"]["role"] == [ROLE_LOYAL_OPPOSITION]
    assert role_map["harnesses"]["B"]["role"] == [ROLE_PRIME_BUILDER]
    # Identity legacy shape: {"harnesses": {harness_name: {"id": harness_id}}}.
    assert identities["harnesses"]["codex"]["id"] == "A"
    assert identities["harnesses"]["claude"]["id"] == "B"


def test_projection_reader_accessors_resolve_from_projection(tmp_path: Path) -> None:
    """The DB-independent projection reader accessors (the IP-1 keyed accessors
    every migrated dict-shaped reader funnels through) resolve role/identity
    from the projection document.
    """
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    document = load_harness_projection(tmp_path)

    assert harness_by_id(document, "A")["harness_name"] == "codex"
    assert role_set_for_id(document, "A") == {ROLE_LOYAL_OPPOSITION}
    assert role_set_for_id(document, "B") == {ROLE_PRIME_BUILDER}
    assert id_for_name(document, "codex") == "A"
    assert id_for_name(document, "claude") == "B"


def test_read_roles_preserves_projection_bytes(tmp_path: Path) -> None:
    """Canonical role reads must not rewrite the hot-path registry projection."""
    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    registry_path = tmp_path / "harness-state" / "harness-registry.json"
    before = registry_path.read_bytes()

    document = read_roles(tmp_path)

    assert [record["id"] for record in document["harnesses"]] == ["A", "B"]
    assert registry_path.read_bytes() == before


def test_generate_harness_projection_preserves_bytes_when_only_timestamp_differs(tmp_path: Path) -> None:
    """No-op refreshes must not dirty the projection just to update generated_at."""
    db = _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    registry_path = tmp_path / "harness-state" / "harness-registry.json"
    document = json.loads(registry_path.read_text(encoding="utf-8"))
    document["generated_at"] = "2000-01-01T00:00:00Z"
    sentinel = (json.dumps(document, indent=2, sort_keys=True) + "\n").replace("\n", "\r\n").encode("utf-8")
    registry_path.write_bytes(sentinel)

    generate_harness_projection(db, tmp_path)

    assert registry_path.read_bytes() == sentinel


def test_golden_value_role_resolution_matches_pre_migration(tmp_path: Path) -> None:
    """Golden-value: post-migration role resolution equals the pre-migration
    expected values.

    Pre-migration, ``load_role_assignments`` resolved harness A -> codex ->
    loyal-opposition and harness B -> claude -> prime-builder from the legacy
    ``harness-state/role-assignments.json``. Post-migration the same resolution
    is served from the registry projection; the resolved role map must be
    byte-identical to the pre-migration golden values.
    """
    # Pre-migration golden role map (the durable owner-set assignment:
    # codex=A=loyal-opposition, claude=B=prime-builder).
    golden = {"A": [ROLE_LOYAL_OPPOSITION], "B": [ROLE_PRIME_BUILDER]}

    _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_LOYAL_OPPOSITION]),
            "B": ("claude", [ROLE_PRIME_BUILDER]),
        },
    )
    document = load_role_assignments(tmp_path)
    resolved = {hid: record["role"] for hid, record in document["harnesses"].items()}
    assert resolved == golden


# ===========================================================================
# IP-RECON — registry/projection reconciliation against the authoritative
# role-assignments.json (the -005 post-GO scope addition).
# ===========================================================================


def _authoritative_role_assignments(root: Path, role_map: dict[str, list[str]]) -> Path:
    """Write an authoritative legacy ``harness-state/role-assignments.json``.

    IP-RECON derives the corrected roles from this still-authoritative file;
    the file is NOT modified by the reconciliation.
    """
    path = root / "harness-state" / "role-assignments.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {hid: {"role": roles} for hid, roles in role_map.items()},
            }
        ),
        encoding="utf-8",
    )
    return path


def _reconcile_registry_to_role_assignments(db: KnowledgeDB, root: Path, role_assignments_path: Path) -> None:
    """Reconcile the DB ``harnesses`` registry to the authoritative role file.

    Mirrors the IP-RECON step: for each harness, the corrected role is derived
    from ``harness-state/role-assignments.json`` (NOT a hand-typed constant);
    an append-only ``insert_harness`` version carries the corrected role with
    every other column forwarded verbatim from the harness's current row; the
    polluted rows are retained; the projection is then regenerated through the
    generator. The authoritative role file is not modified.
    """
    authoritative = json.loads(role_assignments_path.read_text(encoding="utf-8"))
    authoritative_harnesses = authoritative.get("harnesses", {})
    for harness_id, record in sorted(authoritative_harnesses.items()):
        corrected_role = list(record.get("role", []))
        current = db.get_harness(harness_id)
        assert current is not None, f"harness {harness_id} absent from registry"
        # Forward every column verbatim from the current row; correct only role.
        current_role = current.get("role")
        if isinstance(current_role, str):
            try:
                current_role = json.loads(current_role)
            except json.JSONDecodeError:
                current_role = None
        if sorted(current_role or []) == sorted(corrected_role):
            continue
        invocation = current.get("invocation_surfaces")
        if isinstance(invocation, str):
            try:
                invocation = json.loads(invocation)
            except json.JSONDecodeError:
                invocation = None
        db.insert_harness(
            id=harness_id,
            harness_name=str(current.get("harness_name") or harness_id),
            harness_type=str(current.get("harness_type") or harness_id),
            role=corrected_role,
            changed_by="harness-registry-reconciliation",
            change_reason=(
                "WI-3342 IP-RECON: correct IP-2 smoke-test role pollution; "
                "role derived from authoritative role-assignments.json"
            ),
            status=str(current.get("status") or "registered"),
            reviewer_precedence=current.get("reviewer_precedence"),
            invocation_surfaces=invocation,
            capabilities_ref=current.get("capabilities_ref"),
        )
    generate_harness_projection(db, root)


def test_ip_recon_reconciles_inverted_registry_to_authoritative_role_file(
    tmp_path: Path,
) -> None:
    """IP-RECON agreement: a deliberately-INVERTED ``harnesses`` table reconciled
    against the authoritative ``role-assignments.json`` yields corrected
    current-version rows, a regenerated projection, and projection-reader
    accessors that all resolve harness A = loyal-opposition / B = prime-builder.

    Reproduces the post-GO-discovered inversion (IP-2 transitional-mirror
    smoke-test pollution) and the IP-RECON closure.
    """
    # Authoritative role file: the correct owner-set assignment.
    role_file = _authoritative_role_assignments(
        tmp_path,
        {"A": [ROLE_LOYAL_OPPOSITION], "B": [ROLE_PRIME_BUILDER]},
    )

    # Deliberately-inverted registry: A=prime-builder, B=loyal-opposition.
    db = _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_PRIME_BUILDER]),
            "B": ("claude", [ROLE_LOYAL_OPPOSITION]),
        },
    )
    # Pre-reconciliation: the registry (and projection) are inverted vs the
    # authoritative role file.
    assert json.loads(db.get_harness("A")["role"]) == [ROLE_PRIME_BUILDER]
    assert json.loads(db.get_harness("B")["role"]) == [ROLE_LOYAL_OPPOSITION]

    # Run the reconciliation (derive corrected roles from the role file).
    _reconcile_registry_to_role_assignments(db, tmp_path, role_file)

    # (1) Corrected current-version DB rows.
    assert json.loads(db.get_harness("A")["role"]) == [ROLE_LOYAL_OPPOSITION]
    assert json.loads(db.get_harness("B")["role"]) == [ROLE_PRIME_BUILDER]
    # Append-only history preserved: the polluted version is retained, the
    # corrected version is appended on top.
    assert db.get_harness("A")["version"] >= 2
    assert db.get_harness("B")["version"] >= 2

    # (2) The regenerated projection agrees with the authoritative role file.
    document = load_harness_projection(tmp_path)
    assert role_set_for_id(document, "A") == {ROLE_LOYAL_OPPOSITION}
    assert role_set_for_id(document, "B") == {ROLE_PRIME_BUILDER}

    # (3) The projection-reader accessors and the foundational loader all
    # resolve the corrected assignment.
    role_document = load_role_assignments(tmp_path)
    assert role_document["harnesses"]["A"]["role"] == [ROLE_LOYAL_OPPOSITION]
    assert role_document["harnesses"]["B"]["role"] == [ROLE_PRIME_BUILDER]

    # FR9 single-prime-builder partition: exactly one prime-builder harness.
    primes = [hid for hid in ("A", "B") if ROLE_PRIME_BUILDER in role_set_for_id(document, hid)]
    assert primes == ["B"]

    # IP-RECON does NOT modify the authoritative role-assignments.json.
    after = json.loads(role_file.read_text(encoding="utf-8"))
    assert after["harnesses"]["A"]["role"] == [ROLE_LOYAL_OPPOSITION]
    assert after["harnesses"]["B"]["role"] == [ROLE_PRIME_BUILDER]


def test_ip_recon_audit_trail_distinguishes_corrective_writes(tmp_path: Path) -> None:
    """IP-RECON preserves append-only history and stamps the corrective writes
    with a distinguishable ``changed_by`` so the audit trail separates the
    correction from the IP-2 smoke-test pollution.
    """
    role_file = _authoritative_role_assignments(
        tmp_path,
        {"A": [ROLE_LOYAL_OPPOSITION], "B": [ROLE_PRIME_BUILDER]},
    )
    db = _seed_registry(
        tmp_path,
        {
            "A": ("codex", [ROLE_PRIME_BUILDER]),
            "B": ("claude", [ROLE_LOYAL_OPPOSITION]),
        },
    )
    _reconcile_registry_to_role_assignments(db, tmp_path, role_file)

    # The current (corrected) version carries the reconciliation attribution.
    conn = db._get_conn()
    for harness_id in ("A", "B"):
        row = conn.execute("SELECT changed_by FROM current_harnesses WHERE id = ?", (harness_id,)).fetchone()
        assert row[0] == "harness-registry-reconciliation"
        # The polluted version is retained in history (>= 2 versions total).
        count = conn.execute("SELECT COUNT(*) FROM harnesses WHERE id = ?", (harness_id,)).fetchone()[0]
        assert count >= 2


# ===========================================================================
# Part C — no-direct-read scan: no executing read of the legacy harness JSON.
# ===========================================================================

# Roots whose production code must no longer execute a read of the legacy
# harness-state JSON files (the migrated reader surfaces).
_SCAN_ROOTS = (
    "scripts",
    ".claude/hooks",
    ".codex/gtkb-hooks",
    "groundtruth-kb/src/groundtruth_kb",
)

# The two legacy harness-state JSON filenames retired by the WI-3342 migration.
_LEGACY_JSON_FILENAMES = ("role-assignments.json", "harness-identities.json")

# Exclusion allowlist (paths relative to the repo root, POSIX form):
#   * scripts/seed_harness_registry.py — the seed source legitimately reads the
#     legacy JSON until the gated physical-deletion follow-on.
#   * scripts/check_codex_hook_parity.py and scripts/rehearse/_dashboard_regen.py
#     reference the legacy filenames only as static, non-executing string
#     constants; they are allowlisted per the IP-6 named-allowlist contract.
_SCAN_ALLOWLIST = frozenset(
    {
        "scripts/seed_harness_registry.py",
        "scripts/check_codex_hook_parity.py",
        "scripts/rehearse/_dashboard_regen.py",
    }
)

# Attribute calls that constitute an executing read of a path.
_READ_ATTRS = frozenset({"read_text", "read_bytes"})


def _legacy_python_files() -> list[Path]:
    """Every ``*.py`` under the scan roots, excluding the allowlist."""
    files: list[Path] = []
    for root in _SCAN_ROOTS:
        for path in sorted((_REPO_ROOT / root).rglob("*.py")):
            if path.as_posix().replace(_REPO_ROOT.as_posix() + "/", "") in _SCAN_ALLOWLIST:
                continue
            files.append(path)
    return files


def _expr_text(node: ast.AST) -> str:
    """Best-effort source text for an AST node (empty string on failure)."""
    try:
        return ast.unparse(node)
    except Exception:  # noqa: BLE001 - tolerate any unparse edge case
        return ""


def _contains_legacy_filename(node: ast.AST) -> bool:
    """True iff the node's source text mentions a legacy JSON filename."""
    text = _expr_text(node)
    return any(name in text for name in _LEGACY_JSON_FILENAMES)


def _names_in(node: ast.AST) -> set[str]:
    """Return the set of ``Name`` identifiers referenced anywhere in ``node``."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _executing_reads_of_legacy_json(tree: ast.AST) -> list[tuple[int, str]]:
    """Return ``(lineno, expr)`` for every executing read of a legacy JSON file.

    Two-pass deterministic AST analysis:

    * Pass 1 collects names bound to an expression whose source text contains a
      legacy JSON filename (e.g. ``ROLE_ASSIGNMENTS_PATH = root /
      "role-assignments.json"``).
    * Pass 2 finds executing-read calls — ``X.read_text(...)`` /
      ``X.read_bytes(...)``, ``open(X)``, ``json.load(X)`` / ``json.loads(X)`` —
      whose read target ``X`` either textually contains a legacy filename
      (inline read) or references a Pass-1 legacy-path name (constant-then-read).

    Comments and docstrings never appear inside ``Call`` nodes, so they are
    structurally excluded. A string constant assigned to a name that is never
    read (a path constant used only for ``.name`` / ``.is_file()`` / the unused
    legacy file-writers) is likewise not flagged — only an actual executing
    read is reported.
    """
    legacy_path_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _contains_legacy_filename(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    legacy_path_names.add(target.id)
        elif (
            isinstance(node, ast.AnnAssign)
            and node.value is not None
            and isinstance(node.target, ast.Name)
            and _contains_legacy_filename(node.value)
        ):
            legacy_path_names.add(node.target.id)

    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        read_target: ast.AST | None = None
        if isinstance(func, ast.Attribute) and func.attr in _READ_ATTRS:
            read_target = func.value
        elif (
            (
                isinstance(func, ast.Attribute)
                and func.attr in ("load", "loads")
                and isinstance(func.value, ast.Name)
                and func.value.id == "json"
            )
            or isinstance(func, ast.Name)
            and func.id == "open"
        ):
            read_target = node.args[0] if node.args else None
        if read_target is None:
            continue
        target_text = _expr_text(read_target)
        references_legacy_name = bool(_names_in(read_target) & legacy_path_names)
        if _contains_legacy_filename(read_target) or references_legacy_name:
            findings.append((getattr(node, "lineno", -1), target_text[:120]))
    return findings


def test_no_executing_read_of_legacy_harness_json() -> None:
    """No executing read of ``role-assignments.json`` / ``harness-identities.json``
    remains in migrated production code.

    Regression coverage for ``REQ-HARNESS-REGISTRY-001`` (phased reader
    migration) and ``DELIB-2079`` Q7: after IP-3/IP-4/IP-5 every production
    reader resolves harness role/identity from the registry projection
    ``harness-state/harness-registry.json``; the legacy files are no longer
    read at runtime. The scan distinguishes executing reads from comments,
    docstrings, and static string constants, and honours the named exclusion
    allowlist.
    """
    offenders: dict[str, list[tuple[int, str]]] = {}
    for path in _legacy_python_files():
        # utf-8-sig tolerates a UTF-8 BOM so BOM-prefixed files still parse.
        source = path.read_text(encoding="utf-8-sig")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:  # pragma: no cover - defensive
            pytest.fail(f"could not parse {path} for the no-direct-read scan: {exc}")
        findings = _executing_reads_of_legacy_json(tree)
        if findings:
            offenders[path.as_posix()] = findings

    assert not offenders, (
        "Executing read(s) of a legacy harness-state JSON file found in migrated "
        "production code (every reader must resolve from the registry projection "
        "harness-state/harness-registry.json):\n"
        + "\n".join(
            f"  {path}: " + ", ".join(f"line {ln}: {expr}" for ln, expr in finds)
            for path, finds in sorted(offenders.items())
        )
    )


def test_no_direct_read_scan_detects_a_planted_executing_read(tmp_path: Path) -> None:
    """The no-direct-read scan's detector is not vacuous.

    A planted module that executes a read of ``role-assignments.json`` — both
    inline and via a path constant — must be flagged; a sibling module that
    mentions the filename only in a docstring, a comment, and a static string
    constant (with no executing read) must NOT be flagged.
    """
    # Planted offender: inline read + constant-then-read.
    offender = tmp_path / "planted_offender.py"
    offender.write_text(
        "from pathlib import Path\n"
        "import json\n"
        "ROLE_PATH = Path('harness-state') / 'role-assignments.json'\n"
        "def read_inline(root: Path):\n"
        "    return json.loads((root / 'harness-identities.json').read_text())\n"
        "def read_via_constant():\n"
        "    return ROLE_PATH.read_text(encoding='utf-8')\n",
        encoding="utf-8",
    )
    offender_tree = ast.parse(offender.read_text(encoding="utf-8"))
    offender_findings = _executing_reads_of_legacy_json(offender_tree)
    offender_lines = {ln for ln, _ in offender_findings}
    # The inline json.loads(...read_text()) read and the ROLE_PATH.read_text()
    # constant-then-read are both detected.
    assert 5 in offender_lines, offender_findings
    assert 7 in offender_lines, offender_findings

    # Clean sibling: legacy filename only in docstring / comment / static const.
    clean = tmp_path / "clean_sibling.py"
    clean.write_text(
        '"""References harness-state/role-assignments.json in this docstring."""\n'
        "# harness-state/harness-identities.json mentioned only in a comment\n"
        "LEGACY_NAME = 'role-assignments.json'  # static constant, never read\n"
        "def describe() -> str:\n"
        "    return LEGACY_NAME\n",
        encoding="utf-8",
    )
    clean_tree = ast.parse(clean.read_text(encoding="utf-8"))
    assert _executing_reads_of_legacy_json(clean_tree) == []
