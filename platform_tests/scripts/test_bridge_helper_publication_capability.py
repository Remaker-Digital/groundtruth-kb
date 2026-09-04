# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Specification-derived tests for WI-5942: helper-written bridge files must
gain publication-capability receipts.

Design note (approved proposal
``bridge/gtkb-wi5942-bridge-helper-publication-capability-013.md``, Correction 4):
these assertions are **behavioural**, not literal-symbol. The prior revision of
this module asserted that helper source contained the strings
``mint_bridge_publication_capability`` / ``consume_bridge_publication_capability``.
That mandated inlining the governed writer's two-phase-commit transaction into
every helper copy and *failed* the correct design, which delegates to
``scripts.gtkb_bridge_writer.write_bridge_file``. The property that actually
matters is that a helper-written bridge file yields a ``consumed`` row in
``sot_registry_bridge_publication_capabilities``. Delegation satisfies that;
inlining would also satisfy it; neither is mandated by assertion shape.

Coverage spans every helper copy so parity is enforced mechanically rather
than asserted per-file.

Isolation note: every publication runs against a per-test fixture project root
and fixture database. Canonical ``groundtruth.db`` is never touched. WI-5317
recorded the failure mode where writer fixtures reached real project state.

Hermeticity note (per the ``-016`` NO-GO): this module must produce the same
result in a clean/CI runner and under a live harness. Two distinct ambient
dependencies were removed.

1. *Session-id resolution.* ``resolve_work_intent_session_id`` walks
   ``WORK_INTENT_SESSION_ENV_VARS`` and raises ``BridgeWorkIntentError`` when
   none is set, so the suite silently required an ambient harness session id: it
   passed 8/8 under a harness runner and failed 7/8 in a clean runner before
   reaching any assertion. ``_isolate_session_env`` now clears every candidate
   variable and pins exactly one fixture value, so the resolved id is
   deterministic regardless of what the runner carries.
2. *Canonical-isolation instrument.* The prior revision asserted that canonical
   ``groundtruth.db`` mtime was unchanged across the publication. That is a race
   against every other MemBase reader on the machine: closing the last SQLite
   connection in WAL mode checkpoints the write-ahead log back into the main
   file and moves its mtime. The proxy is unsound in both directions -- an
   unrelated concurrent checkpoint fails a perfectly isolated fixture (false
   positive), while a genuine fixture write absorbed by ``-wal`` leaves the main
   file's mtime untouched (false negative). Isolation is now asserted at content
   level, which is hermetic under concurrent readers and strictly stronger.
"""

from __future__ import annotations

import importlib.util
import shutil
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    apply_registry_transaction,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

from scripts.bridge_work_intent_registry import acquire

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Every copy of the bridge-filing helper. Per the approved proposal's
# Correction 1, .claude / .codex / .cursor already delegate and are correct;
# .goose and both scaffold templates were the defective direct-write copies.
HELPER_COPIES: dict[str, str] = {
    # The shared single-source helper is covered first: it is the copy every
    # projection routes to after the Phase B shared-helpers move
    # (gtkb-baseline-correction-and-goose-projector-slice-1, GO -004), so
    # exempting the source would invert the parity contract. Goose routes to
    # it and carries no local copy; remaining per-harness copies persist
    # until their own projector cutovers.
    "shared": "scripts/skill-helpers/gtkb-bridge-propose/write_bridge.py",
    "claude": ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py",
    "codex": ".codex/skills/gtkb-bridge-propose/helpers/write_bridge.py",
    "cursor": ".cursor/skills/gtkb-bridge-propose/helpers/write_bridge.py",
    "template_gtkb": "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py",
    "template_legacy": "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py",
}

BRIDGE_AGGREGATE_GLOB = "bridge/*-[0-9][0-9][0-9].md"


def _propose_fn(helper):
    """Resolve the filing entry point across copy generations.

    The shared single-source copy carries the neutral name ``propose_bridge``
    (baseline neutralization, GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 3);
    per-harness copies keep the legacy harness-named symbol until their own
    projector cutovers retire them.
    """
    fn = getattr(helper, "propose_bridge_codex_non_bypass", None)
    if fn is None:
        # Shared copy: the harness-named symbol was neutralized to
        # ``propose_bridge_inline_compliance`` (identical signature); legacy
        # copies keep the harness-named symbol until their own projector
        # cutovers retire them.
        fn = helper.propose_bridge_inline_compliance
    return fn


# The helper's compliance audit enforces live work-item / project / project-
# authorization membership
# (DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP
# and DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-AUTH-LIVE-CHECK)
# against MemBase at the resolved project root. The fixture seeds its OWN
# records so the test depends on no canonical state and cites nothing real.
FIXTURE_SPEC_ID = "SPEC-WI5942-FIXTURE"
FIXTURE_DELIB_ID = "DELIB-WI5942-FIXTURE"
FIXTURE_PROJECT_ID = "PROJECT-WI5942-FIXTURE"
FIXTURE_WORK_ITEM_ID = "WI-9942"
FIXTURE_PAUTH_ID = "PAUTH-WI5942-FIXTURE"
FIXTURE_MUTATION_CLASSES = ["bridge", "source", "test", "configuration"]


def _aggregate_record() -> SoTArtifact:
    """Registry declaration for the bridge versioned-file aggregate."""
    return SoTArtifact(
        id="bridge-versioned-files",
        domain="control_surface",
        lifecycle="active",
        storage_path=BRIDGE_AGGREGATE_GLOB,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="gt registry register",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode="glob",
    )


def _seed_governance_records(db_path: Path) -> None:
    """Seed the fixture MemBase with the spec / project / work-item / PAUTH set
    the bridge compliance audit requires for a live membership check."""
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_spec(
            id=FIXTURE_SPEC_ID,
            title="WI-5942 helper publication fixture spec",
            status="specified",
            changed_by="test",
            change_reason="seed spec",
        )
        db.insert_deliberation(
            id=FIXTURE_DELIB_ID,
            source_type="owner_conversation",
            title="Owner decision for the WI-5942 helper publication fixture",
            summary="Synthetic fixture authorization.",
            content="Synthetic fixture authorization.",
            outcome="owner_decision",
            changed_by="test",
            change_reason="seed owner decision",
        )
        db.insert_project("WI-5942 Helper Publication Fixture", "test", "seed project", id=FIXTURE_PROJECT_ID)
        db.insert_work_item(
            id=FIXTURE_WORK_ITEM_ID,
            title="Helper publication capability fixture",
            description="Synthetic work item backing the WI-5942 parity fixture.",
            origin="improvement",
            component="bridge-tooling",
            source_spec_id=FIXTURE_SPEC_ID,
            resolution_status="open",
            priority="P3",
            changed_by="test",
            change_reason="seed work item",
        )
        db.link_project_work_item(FIXTURE_PROJECT_ID, FIXTURE_WORK_ITEM_ID, "test", "seed membership")
    finally:
        db.close()


def _build_fixture_root(tmp_path: Path, session_id: str, slug: str) -> Path:
    """Create an isolated project root with a live registry generation and claim.

    Paths follow the conventional layout so ``write_bridge_file`` resolves the
    registry, packaged registry, and database from ``project_root`` alone.
    """
    (tmp_path / "bridge").mkdir()

    # The compliance guard's _work_intent_project_root only accepts the root it
    # derives from the bridge file's parent when groundtruth.toml is present
    # there; otherwise it falls back to the canonical repository and looks for
    # the fixture's claim in the wrong store.
    (tmp_path / "groundtruth.toml").write_text(
        f'[groundtruth]\ndb_path = "{(tmp_path / "groundtruth.db").as_posix()}"\n'
        f'project_root = "{tmp_path.as_posix()}"\napp_title = "WI-5942 Fixture"\n',
        encoding="utf-8",
    )

    # write_bridge_file resolves PROVIDER_VERDICT_GUARDS relative to project_root
    # and refuses to publish when one is absent, so the fixture root carries its
    # own copies of the two guards.
    for relative_guard in (
        ".claude/hooks/scanner-safe-writer.py",
        ".claude/hooks/bridge-compliance-gate.py",
    ):
        source = PROJECT_ROOT / relative_guard
        if not source.is_file():
            pytest.skip(f"provider verdict guard absent from repo: {relative_guard}")
        destination = tmp_path / relative_guard
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        tmp_path
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    registry.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)

    records = [_aggregate_record()]
    payload = serialize_registry(records)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)

    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(records, db_path, changed_by="test", change_reason="wi5942 fixture")
    _seed_governance_records(db_path)

    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        actor_session=session_id,
        changed_by="test/prime-builder",
        change_reason="WI-5942 helper publication fixture",
        start_packet_hash="sha256:test-start",
        pauth_id="PAUTH-WI5942-TEST",
        bridge_id=slug,
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    # Pre-acquire under the SAME session id the helper resolves for itself. The
    # publication guard requires a prior claim for the thread, and the helper's
    # own re-acquire renews rather than conflicts when the holder matches.
    # Acquiring under any other id would lock the helper out of its own write.
    assert acquire(slug, session_id, project_root=tmp_path)
    return tmp_path


def _isolate_session_env(helper: Any, monkeypatch: pytest.MonkeyPatch, session_id: str) -> None:
    """Make session-id resolution hermetic.

    ``resolve_work_intent_session_id`` walks ``WORK_INTENT_SESSION_ENV_VARS`` and
    raises ``BridgeWorkIntentError`` when none is set. Without this the suite
    silently depends on an ambient harness session id: it passes under a harness
    runner and fails outright in a clean/CI runner. Every candidate var is
    cleared and exactly one fixture value is set, so the resolved id is
    deterministic regardless of what the runner carries.
    """
    for name in helper.WORK_INTENT_SESSION_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GTKB_SESSION_ID", session_id)


def _load_helper(copy_key: str) -> Any:
    """Import one helper copy under a unique module name."""
    path = PROJECT_ROOT / HELPER_COPIES[copy_key]
    if not path.is_file():
        pytest.skip(f"helper copy absent: {HELPER_COPIES[copy_key]}")
    spec = importlib.util.spec_from_file_location(f"write_bridge_{copy_key}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _proposal_body(slug: str, session_id: str) -> str:
    return (
        f"NEW\n"
        # The envelope names the NEXT RESPONDER, not the author. A NEW proposal is
        # authored by Prime Builder but answered by Loyal Opposition, so the responder
        # is lo. Authority: ENVELOPE_RESPONDER_BY_STATUS in gtkb_bridge_writer.py.
        f"::init gtkb lo\n"
        f"::open build\n"
        f"author_identity: prime-builder/test\n"
        f"author_harness_id: test\n"
        f"author_session_context_id: {session_id}\n"
        f"author_model: fixture\n"
        f"author_model_version: fixture\n"
        f"author_model_configuration: unit-test\n"
        f"author_metadata_source: unit-test\n"
        f"\n"
        f"bridge_kind: prime_proposal\n"
        f"Document: {slug}\n"
        f"Version: 001\n"
        f"Project Authorization: {FIXTURE_PAUTH_ID}\n"
        f"Project: {FIXTURE_PROJECT_ID}\n"
        f"Work Item: {FIXTURE_WORK_ITEM_ID}\n"
        f'target_paths: ["scripts/example.py"]\n'
        f"\n"
        f"# WI-5942 Helper Publication Fixture\n"
        f"\n"
        f"## Specification Links\n"
        f"\n"
        f"- GOV-FILE-BRIDGE-AUTHORITY-001\n"
        f"\n"
        f"## Prior Deliberations\n"
        f"\n"
        f"_No prior deliberations: synthetic test fixture._\n"
        f"\n"
        f"## Requirement Sufficiency\n"
        f"\n"
        f"Existing requirements sufficient. Synthetic fixture; no requirement capture needed.\n"
        f"\n"
        f"## Owner Decisions / Input\n"
        f"\n"
        f"- Synthetic test fixture; no owner decision is claimed or required.\n"
        f"\n"
        f"## Specification-Derived Verification Plan\n"
        f"\n"
        f"| Specification | Test | Expected |\n"
        f"|---|---|---|\n"
        f"| GOV-FILE-BRIDGE-AUTHORITY-001 | this fixture | consumed capability row |\n"
        f"\n"
        f"## Risk And Rollback\n"
        f"\n"
        f"Synthetic fixture written to an isolated tmp project root; discard the tmp tree.\n"
    )


def _consumed_capability_versions(db_path: Path, slug: str) -> list[int]:
    """Versions of ``slug`` holding a consumed publication capability."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT version FROM sot_registry_bridge_publication_capabilities "
            "WHERE document_name = ? AND capability_state = 'consumed'",
            (slug,),
        ).fetchall()
    finally:
        conn.close()
    return sorted(int(r[0]) for r in rows)


def _canonical_capability_rows(slug: str) -> int:
    """Count canonical publication-capability rows for ``slug``.

    Opened ``mode=ro`` deliberately. A read-write connection would be able to
    checkpoint canonical MemBase's write-ahead log back into the main database
    file on close, so a probe intended to observe isolation would itself perturb
    the state other tests observe. Read-only cannot checkpoint.

    Returns ``0`` when canonical MemBase or the capability table is absent, so a
    fresh clone and CI both evaluate the same predicate as a live checkout.
    """
    canonical = PROJECT_ROOT / "groundtruth.db"
    if not canonical.exists():
        return 0
    conn = sqlite3.connect(f"file:/{canonical.resolve().as_posix()}?mode=ro", uri=True)
    try:
        present = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            ("sot_registry_bridge_publication_capabilities",),
        ).fetchone()
        if present is None:
            return 0
        return int(
            conn.execute(
                "SELECT COUNT(*) FROM sot_registry_bridge_publication_capabilities WHERE document_name = ?",
                (slug,),
            ).fetchone()[0]
        )
    finally:
        conn.close()


@pytest.mark.parametrize("copy_key", sorted(HELPER_COPIES))
def test_helper_write_yields_consumed_publication_capability(
    copy_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every helper copy must produce a consumed publication-capability receipt.

    This is the WI-5942 acceptance property: a bridge file written through any
    harness's filing helper must be accompanied by exact publication-capability
    evidence, otherwise ``check_protected_commit_authorization`` denies staging
    and terminal VERIFIED strands (WI-5825-class).
    """
    slug = "wi5942-helper-publication-fixture"
    helper = _load_helper(copy_key)
    # Pin the session id before resolving it, so the suite is hermetic in a
    # clean/CI runner. The resolved value is then what the claim holder and the
    # declared author session must agree on at the publication authority check.
    _isolate_session_env(helper, monkeypatch, f"wi5942-fixture-{copy_key}")
    session_id = helper.resolve_work_intent_session_id()
    root = _build_fixture_root(tmp_path, session_id, slug)
    # The compliance guard resolves its project root from CLAUDE_PROJECT_DIR
    # before falling back to cwd; without this it would look for the fixture's
    # work-intent claim in the real repository.
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(root))

    written = _propose_fn(helper)(
        slug,
        _proposal_body(slug, session_id),
        version=1,
        status="NEW",
        bridge_dir=root / "bridge",
        pre_populate_prior_deliberations=False,
    )

    assert Path(written).is_file(), f"{copy_key}: helper did not write the bridge file"
    assert _consumed_capability_versions(root / "groundtruth.db", slug) == [1], (
        f"{copy_key}: helper-written bridge file has no consumed publication capability; "
        "this is the WI-5825-class stranding defect"
    )


def test_canonical_groundtruth_db_is_untouched(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture publications must never reach canonical project state (WI-5317).

    Isolation is asserted at content level -- no canonical capability row and no
    canonical bridge file bearing the fixture slug -- rather than by comparing
    canonical ``groundtruth.db`` mtime. See the module docstring's hermeticity
    note: mtime is a proxy that races every concurrent MemBase reader and is
    unsound in both directions, whereas the fixture slug is unique to this test
    and its presence in canonical state is exactly the WI-5317 defect.
    """
    slug = "wi5942-isolation-fixture"
    canonical_bridge_file = PROJECT_ROOT / "bridge" / f"{slug}-001.md"

    # Pre-state. A leaked artifact from an earlier run would make the post-state
    # assertions vacuously true, so the absence is established first.
    assert _canonical_capability_rows(slug) == 0, "fixture slug already present in canonical MemBase before the run"
    assert not canonical_bridge_file.exists(), "fixture bridge file already present in canonical bridge/ before the run"

    # The shared single-source copy is the one Goose (and every future
    # projection) routes to; it is therefore the isolation-critical copy.
    helper = _load_helper("shared")
    _isolate_session_env(helper, monkeypatch, "wi5942-fixture-isolation")
    session_id = helper.resolve_work_intent_session_id()
    root = _build_fixture_root(tmp_path, session_id, slug)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(root))
    _propose_fn(helper)(
        slug,
        _proposal_body(slug, session_id),
        version=1,
        status="NEW",
        bridge_dir=root / "bridge",
        pre_populate_prior_deliberations=False,
    )

    # The publication landed in the fixture root ...
    assert _consumed_capability_versions(root / "groundtruth.db", slug) == [1]
    # ... and nowhere in canonical project state.
    assert _canonical_capability_rows(slug) == 0, "fixture publication reached canonical MemBase"
    assert not canonical_bridge_file.exists(), "fixture publication wrote into the canonical bridge/ directory"


def test_all_helper_copies_are_enumerated() -> None:
    """Guard against a new harness copy escaping parity coverage."""
    discovered = {
        p.relative_to(PROJECT_ROOT).as_posix()
        for p in PROJECT_ROOT.glob("*/skills/gtkb-bridge-propose/helpers/write_bridge.py")
    } | {
        p.relative_to(PROJECT_ROOT).as_posix()
        for p in PROJECT_ROOT.glob("groundtruth-kb/templates/skills/*/helpers/write_bridge.py")
    }
    missing = discovered - set(HELPER_COPIES.values())
    assert not missing, f"helper copies not covered by parity tests: {sorted(missing)}"
