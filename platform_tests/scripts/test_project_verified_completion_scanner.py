"""Tests for scripts/project_verified_completion_scanner.py.

W1 of GTKB-GOVERNANCE-CORRECTION-S358 (WI-3365); originally IP-1 of WI-3316.
Under GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 the scanner gates an
authorization's completion readiness on the project's active project-to-work-
item membership links, not on the authorization envelope's
``included_work_item_ids``. Uses isolated tmp_path project roots; the only
dependency on the live repo is the script import path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_PATH = REPO_ROOT / "scripts" / "project_verified_completion_scanner.py"


@pytest.fixture(scope="module")
def scanner():
    spec = importlib.util.spec_from_file_location("project_verified_completion_scanner", SCANNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["project_verified_completion_scanner"] = module
    spec.loader.exec_module(module)
    return module


def _seed(
    project_root: Path,
    *,
    wi_statuses: dict[str, bool],
    linked_work_items: set[str] | None = None,
    implements_link: bool = True,
) -> None:
    """Seed a project root with one active authorization (PAUTH-X) over the WIs
    in ``wi_statuses``. Each WI maps to whether its bridge thread is VERIFIED.

    GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4 gates the auto-completion
    scan on ``project_artifact_links`` rows with ``artifact_type='bridge_thread'``,
    ``relationship='implements'``, ``status='active'``. By default each seeded
    thread is linked to PROJECT-X via such a row so v4-conformant tests need
    not opt in. Pass ``implements_link=False`` to seed the incidental-citation
    case where a VERIFIED thread cites a WI but is NOT the WI's project's
    addressing thread - the case v4's D4 gate explicitly excludes (the S358
    DELIB-2502 mis-retirement defect).

    Membership-link gating (``linked_work_items``) is independent of the
    implements-link gating: membership defines what's IN the gating set;
    implements defines which threads contribute COVERAGE evidence.
    """
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    index_lines = ["# Bridge Index", ""]
    thread_slugs: list[str] = []
    for index, (wi, verified) in enumerate(sorted(wi_statuses.items())):
        slug = f"gtkb-thread-{index}"
        thread_slugs.append(slug)
        top_status = "VERIFIED" if verified else "GO"
        (bridge / f"{slug}-001.md").write_text(f"# Proposal {slug}\n\nWork Item: {wi}\n", encoding="utf-8")
        index_lines += [f"Document: {slug}", f"{top_status}: bridge/{slug}-001.md", ""]
    (bridge / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-SEED",
            "owner_conversation",
            "Owner approved",
            "Owner approved PROJECT-X authorization PAUTH-X.",
            "{}",
            "test",
            "seed",
            outcome="owner_decision",
        )
        db.insert_project("Scanner Project", "test", "seed", id="PROJECT-X", status="active")
        for wi in wi_statuses:
            db.insert_work_item(wi, f"Work item {wi}", "new", "backlog", "open", "test", "seed")
            if linked_work_items is None or wi in linked_work_items:
                db.link_project_work_item("PROJECT-X", wi, "test", "seed")
        db.insert_spec(
            id="SPEC-SEED",
            title="Seed spec",
            status="verified",
            changed_by="test",
            change_reason="seed",
        )
        db.insert_project_authorization(
            "PROJECT-X",
            "Scanner authorization",
            "DELIB-SEED",
            "Bounded scope.",
            "test",
            "seed",
            id="PAUTH-X",
            status="active",
            included_work_item_ids=list(wi_statuses),
            included_spec_ids=["SPEC-SEED"],
        )
        # v4 D4 gate seed: link each VERIFIED thread to PROJECT-X with
        # relationship='implements'. Without this row, the thread is treated
        # as an incidental citation and excluded from auto-completion (the
        # fail-safe direction). Test code that needs the incidental-citation
        # case passes implements_link=False.
        if implements_link:
            for wi, verified in wi_statuses.items():
                if not verified:
                    continue
                # The thread index matches the WI order in sorted(wi_statuses).
                slug_index = sorted(wi_statuses).index(wi)
                slug = f"gtkb-thread-{slug_index}"
                db.add_project_artifact_link(
                    "PROJECT-X",
                    "bridge_thread",
                    slug,
                    "test",
                    "seed implements link",
                    relationship="implements",
                )
    finally:
        db.close()


def test_scanner_marks_all_verified_authorization_completion_ready(scanner, tmp_path):
    _seed(tmp_path, wi_statuses={"WI-8001": True, "WI-8002": True})
    ready = scanner.completion_ready(tmp_path)
    assert [r.authorization_id for r in ready] == ["PAUTH-X"]
    assert ready[0].completion_ready is True
    assert set(ready[0].verified_work_item_ids) == {"WI-8001", "WI-8002"}
    assert ready[0].unverified_work_item_ids == []


def test_scanner_skips_authorization_with_one_non_verified_wi(scanner, tmp_path):
    _seed(tmp_path, wi_statuses={"WI-8001": True, "WI-8002": False})
    assert scanner.completion_ready(tmp_path) == []
    full = scanner.scan(tmp_path)
    auth = next(r for r in full if r.authorization_id == "PAUTH-X")
    assert auth.completion_ready is False
    assert auth.unverified_work_item_ids == ["WI-8002"]
    assert auth.verified_work_item_ids == ["WI-8001"]


def test_scanner_gating_uses_membership_links_not_included_ids(scanner, tmp_path):
    # WI-8002 is in the authorization's included_work_item_ids and its bridge
    # thread is not VERIFIED, but it is not membership-linked to PROJECT-X.
    # GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 gates on the membership
    # links, so PAUTH-X is completion-ready on the linked WI-8001 alone.
    _seed(
        tmp_path,
        wi_statuses={"WI-8001": True, "WI-8002": False},
        linked_work_items={"WI-8001"},
    )
    ready = scanner.completion_ready(tmp_path)
    assert [r.authorization_id for r in ready] == ["PAUTH-X"]
    assert ready[0].verified_work_item_ids == ["WI-8001"]
    assert ready[0].unverified_work_item_ids == []


def test_scanner_makes_no_db_writes(scanner, tmp_path):
    _seed(tmp_path, wi_statuses={"WI-8001": True})
    db_path = tmp_path / "groundtruth.db"
    probe = KnowledgeDB(db_path)
    try:
        before_version = probe.get_project_authorization("PAUTH-X")["version"]
        before_rows = probe._get_conn().execute("SELECT COUNT(*) FROM project_authorizations").fetchone()[0]
    finally:
        probe.close()

    scanner.scan(tmp_path)
    scanner.completion_ready(tmp_path)

    probe = KnowledgeDB(db_path)
    try:
        after_version = probe.get_project_authorization("PAUTH-X")["version"]
        after_rows = probe._get_conn().execute("SELECT COUNT(*) FROM project_authorizations").fetchone()[0]
    finally:
        probe.close()
    assert after_version == before_version
    assert after_rows == before_rows


# --- v4 D4 implements-gate spec-derived tests (IP-5 cases 1-4) ---------------


def test_incidental_citation_thread_does_not_complete_wi(scanner, tmp_path):
    """v4 D4 gate: a VERIFIED thread citing WI-X but NOT implements-linked
    contributes ZERO to the project's verified set.

    Closes the S358 DELIB-2502 over-broad-citation defect: incidental
    citations of a WI in Prior Deliberations / context / evidence by some
    unrelated VERIFIED thread must not satisfy the v4 completion gate.
    """
    _seed(
        tmp_path,
        wi_statuses={"WI-8001": True},
        implements_link=False,  # incidental-citation case
    )

    assert scanner.verified_work_items_by_project(tmp_path).get("PROJECT-X", set()) == set()
    assert scanner.completion_ready(tmp_path) == []
    full = scanner.scan(tmp_path)
    auth = next(r for r in full if r.authorization_id == "PAUTH-X")
    assert auth.completion_ready is False
    assert auth.verified_work_item_ids == []
    assert auth.unverified_work_item_ids == ["WI-8001"]


def test_implements_linked_thread_completes_wi(scanner, tmp_path):
    """v4 D4 gate positive case: a VERIFIED thread that IS implements-linked
    to WI-X's project DOES contribute WI-X to that project's verified set.
    """
    _seed(
        tmp_path,
        wi_statuses={"WI-8001": True},
        implements_link=True,  # default; explicit for clarity
    )

    assert "WI-8001" in scanner.verified_work_items_by_project(tmp_path).get("PROJECT-X", set())
    ready = scanner.completion_ready(tmp_path)
    assert [r.authorization_id for r in ready] == ["PAUTH-X"]
    assert ready[0].completion_ready is True
    assert ready[0].verified_work_item_ids == ["WI-8001"]


def test_top_verdict_has_no_work_item_line_but_report_does(scanner, tmp_path):
    """v4 D3 corrected scope: the per-thread Work-Item scan reads ALL versions
    of an implements-linked thread, not just the top version.

    Regression guarding Defect 1 (the -003 draft's broken "top VERIFIED
    version carries Work Item metadata" clause): the top version of a
    VERIFIED-topped thread is the Codex verdict, which carries NO
    ``Work Item:`` metadata line; the metadata sits in the Prime
    implementation report one or more versions BELOW the verdict. The scan
    must therefore traverse the full version chain.
    """
    # Seed the project + WI + authorization + implements link via _seed,
    # but override the bridge to a multi-version thread shape. The _seed
    # implements link is to slug "gtkb-thread-0", which the override preserves.
    _seed(tmp_path, wi_statuses={"WI-8001": True}, implements_link=True)
    bridge = tmp_path / "bridge"
    # -001 implementation report carries the Work Item line.
    (bridge / "gtkb-thread-0-001.md").write_text(
        "NEW\n\n# Implementation report\n\nWork Item: WI-8001\n",
        encoding="utf-8",
    )
    # -002 Codex VERIFIED verdict carries NO Work Item line.
    (bridge / "gtkb-thread-0-002.md").write_text(
        "VERIFIED\n\n# Codex verdict\n\n(no Work Item metadata in verdict files)\n",
        encoding="utf-8",
    )
    # Index lists both versions; top status is VERIFIED at -002.
    (bridge / "INDEX.md").write_text(
        "# Bridge Index\n"
        "\n"
        "Document: gtkb-thread-0\n"
        "VERIFIED: bridge/gtkb-thread-0-002.md\n"
        "NEW: bridge/gtkb-thread-0-001.md\n"
        "\n",
        encoding="utf-8",
    )

    verified = scanner.verified_work_items_by_project(tmp_path).get("PROJECT-X", set())
    assert verified == {"WI-8001"}, (
        f"D3 corrected scope must traverse all versions; verdict-only scan would miss "
        f"WI-8001 in the report below the verdict. Got {verified}."
    )


def test_fail_safe_no_implements_link_no_completion(scanner, tmp_path):
    """v4 fail-safe direction: when a project's gating WIs are NOT covered by
    any implements-linked VERIFIED thread, no authorization is reported as
    completion-ready. Auto-completion is paused (no spurious retirement).

    This is the canonical transition state when v4 lands and Phase-2 backfill
    has not yet populated ``implements`` links for existing projects.
    """
    _seed(
        tmp_path,
        wi_statuses={"WI-8001": True, "WI-8002": True},
        implements_link=False,  # no implements links → fail-safe holds
    )

    assert scanner.verified_work_items_by_project(tmp_path).get("PROJECT-X", set()) == set()
    assert scanner.completion_ready(tmp_path) == []
    full = scanner.scan(tmp_path)
    auth = next(r for r in full if r.authorization_id == "PAUTH-X")
    assert auth.completion_ready is False
    assert set(auth.unverified_work_item_ids) == {"WI-8001", "WI-8002"}
    assert auth.verified_work_item_ids == []


def test_cross_project_implements_link_does_not_satisfy_other_project(scanner, tmp_path):
    """v4 F1 regression (NO-GO -012): an ``implements`` link held by PROJECT-A
    must NOT satisfy a PROJECT-B authorization, even when PROJECT-A's VERIFIED
    thread cites a WI that gates PROJECT-B.

    Reproduces the exact cross-context false-positive Codex found: the prior
    global-slug implementation unioned thread-a's WIs into one global verified
    set, so WI-8002 (cited by PROJECT-A's thread-a, gating for PROJECT-B) would
    falsely complete PROJECT-B. The project-scoped map attributes thread-a's
    WIs to PROJECT-A only.
    """
    bridge = tmp_path / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    # thread-a is PROJECT-A's VERIFIED addressing thread; it cites WI-8002.
    (bridge / "thread-a-001.md").write_text(
        "NEW\n\n# Impl report\n\nWork Item: WI-8002\n", encoding="utf-8"
    )
    (bridge / "thread-a-002.md").write_text(
        "VERIFIED\n\n# Codex verdict\n", encoding="utf-8"
    )
    (bridge / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: thread-a\n"
        "VERIFIED: bridge/thread-a-002.md\nNEW: bridge/thread-a-001.md\n\n",
        encoding="utf-8",
    )

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-SEED", "owner_conversation", "seed", "seed", "{}", "t", "s",
            outcome="owner_decision",
        )
        db.insert_spec(id="SPEC-SEED", title="Seed", status="verified", changed_by="t", change_reason="s")
        db.insert_project("Project A", "t", "s", id="PROJECT-A", status="active")
        db.insert_project("Project B", "t", "s", id="PROJECT-B", status="active")
        # WI-8002 gates PROJECT-B (membership), but PROJECT-A owns the only
        # implements link to thread-a.
        db.insert_work_item("WI-8002", "shared WI", "new", "backlog", "open", "t", "s")
        db.link_project_work_item("PROJECT-B", "WI-8002", "t", "s")
        db.add_project_artifact_link(
            "PROJECT-A", "bridge_thread", "thread-a", "t", "s", relationship="implements",
        )
        for pid in ("PROJECT-A", "PROJECT-B"):
            db.insert_project_authorization(
                pid, f"Auth {pid}", "DELIB-SEED", "Bounded scope.", "t", "s",
                id=f"PAUTH-{pid[-1]}", status="active",
                included_work_item_ids=["WI-8002"], included_spec_ids=["SPEC-SEED"],
            )
    finally:
        db.close()

    vbp = scanner.verified_work_items_by_project(tmp_path)
    # Coverage is attributed to PROJECT-A only; PROJECT-B has no implements link.
    assert vbp.get("PROJECT-A", set()) == {"WI-8002"}
    assert vbp.get("PROJECT-B", set()) == set()

    # PROJECT-B must NOT be completion-ready (the F1 false positive).
    ready_ids = {r.project_id for r in scanner.completion_ready(tmp_path)}
    assert "PROJECT-B" not in ready_ids, (
        "F1 regression: PROJECT-A's implements link must not complete PROJECT-B"
    )
    # PROJECT-B's WI-8002 is correctly reported unverified for PROJECT-B.
    full = scanner.scan(tmp_path)
    auth_b = next(r for r in full if r.authorization_id == "PAUTH-B")
    assert auth_b.completion_ready is False
    assert auth_b.unverified_work_item_ids == ["WI-8002"]
