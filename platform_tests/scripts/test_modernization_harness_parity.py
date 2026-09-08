"""Objective acceptance tests for the frozen modernization harness-parity scope."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.session.envelope import (
    TOPIC_TYPES,
    EnvelopeError,
    close_session,
    ensure_worker_session,
    load_current,
    open_session,
    open_topic,
    resolve_worker_role_provenance,
    worker_session_envelope_path,
)

from scripts.check_harness_parity import check_harness_parity
from scripts.gtkb_session_id import per_session_role_marker_path
from scripts.harness_projection_reader import load_harness_projection
from scripts.session_role_resolution import resolve_interactive_session_role_details

REPO_ROOT = Path(__file__).resolve().parents[2]
ROLE_PRIME = "prime-builder"
ROLE_LO = "loyal-opposition"
VALID_ROLES = {ROLE_PRIME, ROLE_LO}
REQUIRED_ENVELOPE_CAPABILITIES = {
    "activity_envelope.activity_envelope_projection_mode",
    "activity_envelope.compact_result_envelope_mode",
    "activity_envelope.compact_session_envelope_mode",
    "activity_envelope.full_transcript_archive_independence",
}


def _active_harness_rows(project_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    projection = load_harness_projection(project_root)
    rows = [row for row in projection.get("harnesses", []) if isinstance(row, dict) and row.get("status") == "active"]
    assert len(rows) >= 2, "harness parity requires a multi-harness active population"
    for row in rows:
        name = row.get("harness_name")
        assert isinstance(name, str) and name
        assert isinstance(row.get("id"), str) and row["id"]
        roles = row.get("role")
        assert isinstance(roles, list) and roles and set(roles).issubset(VALID_ROLES), name
        surfaces = row.get("invocation_surfaces")
        assert isinstance(surfaces, dict), name
        headless = surfaces.get("headless")
        assert isinstance(headless, dict) and headless.get("argv"), name
    return sorted(rows, key=lambda row: str(row["id"]))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_harness_state(root: Path, rows: list[dict[str, Any]]) -> None:
    _write_json(
        root / "harness-state" / "harness-identities.json",
        {
            "schema_version": 1,
            "harnesses": {str(row["harness_name"]): {"id": str(row["id"])} for row in rows},
        },
    )
    _write_json(
        root / "harness-state" / "harness-registry.json",
        {"schema_version": 1, "harnesses": rows},
    )


def _durable_role(row: dict[str, Any]) -> str:
    roles = row["role"]
    assert isinstance(roles, list) and roles
    role = str(roles[0])
    assert role in VALID_ROLES
    return role


def _opposite_role(role: str) -> str:
    return ROLE_LO if role == ROLE_PRIME else ROLE_PRIME


@pytest.fixture
def active_harness_rows() -> list[dict[str, Any]]:
    return _active_harness_rows()


@pytest.fixture
def harness_root(tmp_path: Path, active_harness_rows: list[dict[str, Any]]) -> Path:
    _seed_harness_state(tmp_path, active_harness_rows)
    return tmp_path


def test_active_harnesses_have_required_production_parity(
    active_harness_rows: list[dict[str, Any]],
) -> None:
    """Every active headless lane satisfies the production envelope parity contract."""
    report = check_harness_parity(REPO_ROOT, harness="all", include_all=True)
    active_names = {str(row["harness_name"]) for row in active_harness_rows}

    assert report.errors == []
    assert active_names.issubset(report.selected_harnesses)
    for harness_name in active_names:
        results = {
            result.capability_id: result.state
            for result in report.results
            if result.harness == harness_name and result.parity_class == "required"
        }
        assert REQUIRED_ENVELOPE_CAPABILITIES.issubset(results), harness_name
        assert {capability_id: results[capability_id] for capability_id in REQUIRED_ENVELOPE_CAPABILITIES} == {
            capability_id: "PASS" for capability_id in REQUIRED_ENVELOPE_CAPABILITIES
        }


def test_required_target_set_tracks_every_enabled_registry_harness(tmp_path: Path) -> None:
    """Enabling a registry row automatically adds it to the required parity population."""
    projection = load_harness_projection(REPO_ROOT)
    rows = json.loads(json.dumps(projection["harnesses"]))
    template = next(row for row in rows if row.get("status") == "active")
    enabled = dict(template)
    enabled.update(
        {
            "harness_name": "future-enabled-harness",
            "harness_type": "test",
            "id": "FUTURE-ENABLED",
            "status": "active",
        }
    )
    rows.append(enabled)
    _seed_harness_state(tmp_path, rows)

    required_ids = {str(row["id"]) for row in _active_harness_rows(tmp_path)}

    assert required_ids == {str(row["id"]) for row in rows if row.get("status") == "active"}
    assert enabled["id"] in required_ids


def test_explicit_roles_context_and_routes_are_equivalent_across_harnesses(
    harness_root: Path,
    active_harness_rows: list[dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit role outranks durable fallback without changing topic semantics."""
    baseline_routes: dict[str, tuple[str, str]] | None = None

    for row in active_harness_rows:
        harness_name = str(row["harness_name"])
        durable_role = _durable_role(row)
        explicit_role = _opposite_role(durable_role)
        session_id = f"interactive-{row['id']}"
        monkeypatch.setenv("GTKB_SESSION_ID", session_id)
        envelope = open_session(
            harness_root,
            harness_name=harness_name,
            session_id=session_id,
            init_keyword=f"::init gtkb {'pb' if explicit_role == ROLE_PRIME else 'lo'}",
            role=explicit_role,
            subject="gtkb",
        )

        assert envelope["role_asserted"] == explicit_role
        assert envelope["role_resolved"] == explicit_role
        assert envelope["role_resolution"]["interactive_resolved_role"] == explicit_role
        assert envelope["role_resolution"]["durable_registry_role"] == durable_role
        assert envelope["role_resolution"]["interactive_role_source"] == "transcript_init_keyword"
        assert envelope["role_resolution"]["authority_mode"] == "interactive_transcript"
        assert "non-overriding" in envelope["role_resolution"]["durable_registry_authority"]

        observed_routes: dict[str, tuple[str, str]] = {}
        for topic_type in TOPIC_TYPES:
            topic = open_topic(harness_root, topic_type, harness_name=harness_name)
            observed_routes[topic_type] = (
                str(topic["route_target"]),
                json.dumps(topic["preload_state"], sort_keys=True),
            )

        if baseline_routes is None:
            baseline_routes = observed_routes
        else:
            assert observed_routes == baseline_routes, harness_name
        assert load_current(harness_root, harness_name)["role_resolved"] == explicit_role

    assert baseline_routes is not None
    assert set(baseline_routes) == set(TOPIC_TYPES)


def test_role_resolution_orders_marker_then_envelope_then_durable_fallback(
    harness_root: Path,
    active_harness_rows: list[dict[str, Any]],
) -> None:
    """Fallback preserves transcript authority until no session authority remains."""
    for row in active_harness_rows:
        harness_name = str(row["harness_name"])
        durable_role = _durable_role(row)
        envelope_role = _opposite_role(durable_role)
        query_session_id = f"role-order-{row['id']}"
        open_session(
            harness_root,
            harness_name=harness_name,
            session_id=query_session_id,
            init_keyword=f"::init gtkb {'pb' if envelope_role == ROLE_PRIME else 'lo'}",
            role=envelope_role,
        )

        details = resolve_interactive_session_role_details(
            harness_root,
            current_session_id=query_session_id,
            harness_name=harness_name,
        )
        assert details["interactive_resolved_role"] == envelope_role
        assert details["interactive_role_source"] == "session_envelope"
        assert details["authority_mode"] == "interactive_transcript"

        marker_path = per_session_role_marker_path(harness_root, query_session_id)
        _write_json(
            marker_path,
            {"role": durable_role, "session_id": f"stale-{query_session_id}"},
        )
        stale_details = resolve_interactive_session_role_details(
            harness_root,
            current_session_id=query_session_id,
            harness_name=harness_name,
        )
        assert stale_details["interactive_resolved_role"] == envelope_role
        assert stale_details["interactive_role_source"] == "session_envelope_marker_stale_session"
        assert stale_details["authority_mode"] == "interactive_transcript"

        _write_json(marker_path, {"role": durable_role, "session_id": query_session_id})
        marker_details = resolve_interactive_session_role_details(
            harness_root,
            current_session_id=query_session_id,
            harness_name=harness_name,
        )
        assert marker_details["interactive_resolved_role"] == durable_role
        assert marker_details["interactive_role_source"] == "marker"
        assert marker_details["authority_mode"] == "interactive_transcript"

        marker_path.unlink()
        close_session(harness_root, harness_name=harness_name, session_id=query_session_id)
        fallback_details = resolve_interactive_session_role_details(
            harness_root,
            current_session_id=query_session_id,
            harness_name=harness_name,
        )
        assert fallback_details["interactive_resolved_role"] is None
        assert fallback_details["interactive_role_source"] == "durable_marker_absent"
        assert fallback_details["authority_mode"] == "unresolved"


def test_headless_worker_authority_is_isolated_by_session_and_harness(
    harness_root: Path,
    active_harness_rows: list[dict[str, Any]],
) -> None:
    """A current projection or another harness cannot replace exact worker authority."""
    for row in active_harness_rows:
        harness_name = str(row["harness_name"])
        durable_role = _durable_role(row)
        first_role = _opposite_role(durable_role)
        first_session = f"{row['id']}-worker-one"
        second_session = f"{row['id']}-worker-two"

        ensure_worker_session(
            harness_root,
            harness_name=harness_name,
            session_id=first_session,
            role=first_role,
            role_source="dispatcher_composition",
            dispatch_run_id=f"run-{first_session}",
        )
        ensure_worker_session(
            harness_root,
            harness_name=harness_name,
            session_id=second_session,
            role=durable_role,
            role_source="dispatcher_composition",
            dispatch_run_id=f"run-{second_session}",
        )

        first = resolve_worker_role_provenance(
            harness_root,
            current_session_id=first_session,
            harness_name=harness_name,
        )
        second = resolve_worker_role_provenance(
            harness_root,
            current_session_id=second_session,
            harness_name=harness_name,
        )
        assert first["role"] == first_role
        assert first["dispatch_run_id"] == f"run-{first_session}"
        assert second["role"] == durable_role
        worker_document = json.loads(
            worker_session_envelope_path(harness_root, harness_name, second_session).read_text(encoding="utf-8")
        )
        assert worker_document["session_id"] == second_session
        assert (
            resolve_worker_role_provenance(
                harness_root,
                current_session_id=first_session,
            )["harness_name"]
            == harness_name
        )

    collision_session = "cross-harness-collision"
    for row in active_harness_rows[:2]:
        ensure_worker_session(
            harness_root,
            harness_name=str(row["harness_name"]),
            session_id=collision_session,
            role=_durable_role(row),
            role_source="dispatcher_composition",
            dispatch_run_id=f"run-{row['id']}-collision",
        )

    with pytest.raises(EnvelopeError, match="ambiguous across session envelopes"):
        resolve_worker_role_provenance(
            harness_root,
            current_session_id=collision_session,
        )

    for row in active_harness_rows[:2]:
        provenance = resolve_worker_role_provenance(
            harness_root,
            current_session_id=collision_session,
            harness_name=str(row["harness_name"]),
        )
        assert provenance["harness_id"] == row["id"]


# ---------------------------------------------------------------------------
# WI-5935 Slice F: cross-harness wrap fail-closed parity + marker-coverage guard.
# Marker scope is the identity-active population that carries a RUNTIME_HARNESS_MARKERS
# entry after Slice C GO-006: codex, claude, antigravity, cursor, goose. The three
# identity-active but unmarked harnesses (ollama, openrouter, alibaba-cloud-studio) are
# an explicit scoped deliberate-deferral (tracked under WI-5936 Slice 2), guarded here.
# ---------------------------------------------------------------------------
MARKER_SCOPE = {"codex", "claude", "antigravity", "cursor", "goose"}
DEFERRED_UNMARKED_HARNESSES = {"ollama", "openrouter", "alibaba-cloud-studio"}


def _identity_harness_names(project_root: Path = REPO_ROOT) -> set[str]:
    data = json.loads((project_root / "harness-state" / "harness-identities.json").read_text(encoding="utf-8"))
    return set(data.get("harnesses", {}).keys())


def _marker_scope_harness_ids(project_root: Path = REPO_ROOT) -> dict[str, str]:
    data = json.loads((project_root / "harness-state" / "harness-identities.json").read_text(encoding="utf-8"))
    harnesses = data.get("harnesses", {})
    return {n: str(r["id"]) for n, r in harnesses.items() if n in MARKER_SCOPE}


def test_marker_coverage_guard_covers_every_identity_harness() -> None:
    """WI-5935 Slice F: every identity harness is in the marker matrix or the typed deferral list."""
    from groundtruth_kb.session.envelope import RUNTIME_HARNESS_MARKERS

    identity = _identity_harness_names()
    marker_scope = set(RUNTIME_HARNESS_MARKERS)
    assert marker_scope >= MARKER_SCOPE
    silent_gap = identity - marker_scope - DEFERRED_UNMARKED_HARNESSES
    assert not silent_gap, f"silent marker gap: {sorted(silent_gap)}"
    assert not (DEFERRED_UNMARKED_HARNESSES & marker_scope), "deferred harnesses must be genuinely unmarked"


def test_marker_scope_session_ids_resolve_via_uniform_resolver() -> None:
    """WI-5935 Slice F: each marker-scope harness session-id marker resolves via the uniform resolver."""
    from groundtruth_kb.session.envelope import RUNTIME_HARNESS_MARKERS

    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id

    for name in sorted(MARKER_SCOPE):
        marker = RUNTIME_HARNESS_MARKERS[name][0]
        env = {marker: f"{name}-marker-id"}
        assert resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ=env) == f"{name}-marker-id"


def test_wrap_fail_closed_parity_across_marker_scope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-5935 Slice F: identical fail-closed wrap parity across every marker-scope harness.

    For each harness a concurrent same-harness two-context wrap fails closed without
    reaching the other context's document.
    """
    from groundtruth_kb.session.envelope import (
        EnvelopeError,
        load_current,
        open_session,
        worker_session_envelope_path,
    )
    from groundtruth_kb.session.wrap import run_wrap

    scope = _marker_scope_harness_ids()
    assert set(scope) == MARKER_SCOPE
    rows = [
        {
            "harness_name": n,
            "id": i,
            "status": "active",
            "role": ["prime-builder"],
            "invocation_surfaces": {"headless": {"argv": ["python"]}},
        }
        for n, i in scope.items()
    ]
    _seed_harness_state(tmp_path, rows)

    for name in sorted(MARKER_SCOPE):
        open_session(tmp_path, harness_name=name, session_id=f"{name}-ctx-a")
        monkeypatch.setenv("GTKB_SESSION_ID", f"{name}-ctx-b")
        with pytest.raises(EnvelopeError, match="no open session envelope exists"):
            run_wrap(tmp_path, harness_name=name)
        live = load_current(tmp_path, name)
        assert live is None
        assert not (tmp_path / "harness-state" / name / "session-envelope.json").exists()
        assert (
            json.loads(worker_session_envelope_path(tmp_path, name, f"{name}-ctx-a").read_text(encoding="utf-8"))[
                "status"
            ]
            == "open"
        )
        monkeypatch.delenv("GTKB_SESSION_ID", raising=False)
