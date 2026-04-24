"""Tests for the GT-KB dashboard control-plane registry and refresh-service dispatch.

Covers the Phase 5 first-slice boundaries set by
bridge/gtkb-dashboard-control-plane-baseline-implementation-002.md (GO):

- Registry exposes exactly three operations with required metadata.
- Unknown operation IDs fail closed.
- Browser-supplied path overrides are rejected.
- dashboard.refresh is the only apply-capable op; dry_run does not write.
- Token is required for apply; read-only ops and dry-run previews are not gated.
- Legacy POST /refresh dispatches through the registry.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from http import HTTPStatus
from pathlib import Path
from typing import Any, Mapping

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "scripts" / "gtkb_dashboard" / "control_plane_registry.py"


def _load_registry():
    spec = importlib.util.spec_from_file_location(
        "control_plane_registry_under_test", REGISTRY_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["control_plane_registry_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _load_refresh_service():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    return importlib.import_module("scripts.gtkb_dashboard.refresh_service")


def _build_context(registry, tmp_path, *, apply_result=None, state_extras=None):
    default_apply = apply_result or {
        "status": "completed",
        "trigger": "dashboard.refresh",
        "record_counts": {"refresh_runs": 1},
    }
    snapshot: dict[str, Any] = {
        "last_result": None,
        "last_error": "",
        "refreshing": False,
        "token_configured": True,
        "interval_seconds": 3600,
    }
    if state_extras:
        snapshot.update(state_extras)
    calls: list[str] = []

    def apply_op(op_id: str) -> Mapping[str, Any]:
        calls.append(op_id)
        return default_apply

    return (
        registry.OperationContext(
            project_root=tmp_path,
            dashboard_db=tmp_path / "dashboard.sqlite",
            subject="dashboard",
            apply_operation=apply_op,
            read_state=lambda: snapshot,
        ),
        calls,
    )


def test_registry_exposes_three_operations_with_required_metadata():
    registry = _load_registry()
    expected_ids = {"dashboard.read", "dashboard.refresh", "control_plane.status"}
    assert set(registry.list_operation_ids()) == expected_ids
    for op_id in expected_ids:
        descriptor = registry.get_descriptor(op_id)
        assert descriptor.operation_id == op_id
        assert descriptor.display_name
        assert descriptor.allowed_subjects
        assert descriptor.target_root_policy in {"app_local", "none"}
        assert descriptor.effective_timing == "immediate"


def test_dashboard_refresh_is_the_only_apply_capable_operation():
    registry = _load_registry()
    assert registry.get_descriptor("dashboard.refresh").supports_dry_run is True
    assert registry.get_descriptor("dashboard.refresh").required_role_slots == (
        "dashboard-refresh-token",
    )
    assert registry.get_descriptor("dashboard.read").supports_dry_run is False
    assert registry.get_descriptor("dashboard.read").required_role_slots == ()
    assert registry.get_descriptor("control_plane.status").supports_dry_run is False
    assert registry.get_descriptor("control_plane.status").required_role_slots == ()


def test_dispatch_rejects_unknown_operation_ids(tmp_path):
    registry = _load_registry()
    ctx, _ = _build_context(registry, tmp_path)
    with pytest.raises(registry.UnknownOperationError):
        registry.dispatch({"operation_id": "dashboard.write"}, ctx)


def test_dispatch_rejects_missing_operation_id(tmp_path):
    registry = _load_registry()
    ctx, _ = _build_context(registry, tmp_path)
    with pytest.raises(registry.InvalidRequestError, match="operation_id is required"):
        registry.dispatch({}, ctx)


@pytest.mark.parametrize(
    "forbidden_key",
    ["project_root", "dashboard_db", "target_path", "script", "command"],
)
def test_dispatch_rejects_browser_supplied_path_overrides(tmp_path, forbidden_key):
    registry = _load_registry()
    ctx, _ = _build_context(registry, tmp_path)
    with pytest.raises(registry.InvalidRequestError, match=forbidden_key):
        registry.dispatch(
            {"operation_id": "dashboard.read", forbidden_key: "attacker-value"},
            ctx,
        )


def test_dispatch_rejects_dry_run_on_operation_without_support(tmp_path):
    registry = _load_registry()
    ctx, _ = _build_context(registry, tmp_path)
    with pytest.raises(registry.InvalidRequestError, match="does not support dry_run"):
        registry.dispatch({"operation_id": "dashboard.read", "dry_run": True}, ctx)


def test_dispatch_rejects_non_boolean_dry_run(tmp_path):
    registry = _load_registry()
    ctx, _ = _build_context(registry, tmp_path)
    with pytest.raises(registry.InvalidRequestError, match="dry_run must be a boolean"):
        registry.dispatch(
            {"operation_id": "dashboard.refresh", "dry_run": "yes"},
            ctx,
        )


def test_dashboard_read_returns_typed_envelope_with_required_fields(tmp_path):
    registry = _load_registry()
    ctx, calls = _build_context(registry, tmp_path)
    response = registry.dispatch({"operation_id": "dashboard.read"}, ctx)
    required_fields = {
        "operation_id",
        "status",
        "effective_timing",
        "subject",
        "project_root",
        "dashboard_db",
        "dry_run",
        "details",
    }
    assert required_fields <= set(response.keys())
    assert response["operation_id"] == "dashboard.read"
    assert response["status"] == "ok"
    assert response["dry_run"] is False
    assert response["project_root"] == str(tmp_path)
    assert response["dashboard_db"] == str(tmp_path / "dashboard.sqlite")
    assert calls == []  # read-only must not invoke apply


def test_dashboard_refresh_dry_run_does_not_apply(tmp_path):
    registry = _load_registry()
    ctx, calls = _build_context(registry, tmp_path)
    response = registry.dispatch(
        {"operation_id": "dashboard.refresh", "dry_run": True}, ctx
    )
    assert response["status"] == "dry_run"
    assert response["dry_run"] is True
    assert response["details"]["would_refresh"] is True
    assert response["details"]["target_root_policy"] == "app_local"
    assert calls == []


def test_dashboard_refresh_apply_invokes_handler_and_wraps_result(tmp_path):
    registry = _load_registry()
    ctx, calls = _build_context(
        registry,
        tmp_path,
        apply_result={
            "status": "completed",
            "trigger": "dashboard.refresh",
            "record_counts": {"refresh_runs": 2},
        },
    )
    response = registry.dispatch(
        {"operation_id": "dashboard.refresh", "dry_run": False}, ctx
    )
    assert response["status"] == "completed"
    assert response["dry_run"] is False
    assert calls == ["dashboard.refresh"]
    assert response["details"]["record_counts"] == {"refresh_runs": 2}


def test_control_plane_status_lists_all_registered_operations(tmp_path):
    registry = _load_registry()
    ctx, _ = _build_context(registry, tmp_path)
    response = registry.dispatch({"operation_id": "control_plane.status"}, ctx)
    operations = response["details"]["operations"]
    reported_ids = {op["operation_id"] for op in operations}
    assert reported_ids == set(registry.list_operation_ids())
    refresh_entry = next(
        op for op in operations if op["operation_id"] == "dashboard.refresh"
    )
    assert refresh_entry["supports_dry_run"] is True
    assert refresh_entry["required_role_slots"] == ["dashboard-refresh-token"]


# --- refresh_service.handle_control_plane_request -----------------------------


def _make_state(tmp_path, *, token: str = "shared-token"):
    service = _load_refresh_service()
    return service, service.RefreshState(
        db_path=tmp_path / "dashboard.sqlite",
        project_root=tmp_path,
        interval_seconds=3600,
        token=token,
    )


def test_refresh_service_read_does_not_require_token(tmp_path):
    service, state = _make_state(tmp_path)
    status, body = service.handle_control_plane_request(
        {"operation_id": "dashboard.read"}, state, supplied_token=""
    )
    assert status == HTTPStatus.OK
    assert body["operation_id"] == "dashboard.read"
    assert body["status"] == "ok"


def test_refresh_service_status_does_not_require_token(tmp_path):
    service, state = _make_state(tmp_path)
    status, body = service.handle_control_plane_request(
        {"operation_id": "control_plane.status"}, state, supplied_token=""
    )
    assert status == HTTPStatus.OK
    assert "operations" in body["details"]


def test_refresh_service_refresh_dry_run_does_not_require_token(tmp_path):
    service, state = _make_state(tmp_path)
    status, body = service.handle_control_plane_request(
        {"operation_id": "dashboard.refresh", "dry_run": True},
        state,
        supplied_token="",
    )
    assert status == HTTPStatus.OK
    assert body["status"] == "dry_run"
    assert body["dry_run"] is True


def test_refresh_service_refresh_apply_requires_configured_token(tmp_path):
    service, state = _make_state(tmp_path, token="")
    status, body = service.handle_control_plane_request(
        {"operation_id": "dashboard.refresh", "dry_run": False},
        state,
        supplied_token="anything",
    )
    assert status == HTTPStatus.SERVICE_UNAVAILABLE
    assert "not configured" in body["error"]


def test_refresh_service_refresh_apply_rejects_wrong_token(tmp_path):
    service, state = _make_state(tmp_path, token="correct")
    status, body = service.handle_control_plane_request(
        {"operation_id": "dashboard.refresh", "dry_run": False},
        state,
        supplied_token="wrong",
    )
    assert status == HTTPStatus.UNAUTHORIZED
    assert body["error"] == "invalid refresh token"


def test_refresh_service_refresh_apply_calls_refresh_now(tmp_path, monkeypatch):
    service, state = _make_state(tmp_path, token="shared")
    captured: list[str] = []

    def fake_refresh_now(trigger: str) -> dict[str, Any]:
        captured.append(trigger)
        return {"status": "completed", "trigger": trigger}

    monkeypatch.setattr(state, "refresh_now", fake_refresh_now)
    status, body = service.handle_control_plane_request(
        {"operation_id": "dashboard.refresh", "dry_run": False},
        state,
        supplied_token="shared",
    )
    assert status == HTTPStatus.OK
    assert body["status"] == "completed"
    assert body["dry_run"] is False
    assert captured == ["dashboard.refresh"]


def test_refresh_service_unknown_operation_returns_404(tmp_path):
    service, state = _make_state(tmp_path)
    status, body = service.handle_control_plane_request(
        {"operation_id": "dashboard.write"}, state, supplied_token=""
    )
    assert status == HTTPStatus.NOT_FOUND
    assert body["status"] == "error"


def test_refresh_service_invalid_request_returns_400(tmp_path):
    service, state = _make_state(tmp_path)
    status, body = service.handle_control_plane_request(
        {"operation_id": "dashboard.read", "project_root": "/etc"},
        state,
        supplied_token="",
    )
    assert status == HTTPStatus.BAD_REQUEST
    assert "project_root" in body["error"]


def test_refresh_service_context_paths_come_from_state_not_caller(tmp_path):
    service, state = _make_state(tmp_path)
    context = service._make_context(state)
    assert context.project_root == tmp_path
    assert context.dashboard_db == tmp_path / "dashboard.sqlite"
    assert context.subject == "dashboard"
