"""Native ordinary-operation checks use exact assigned-work formal constraints.

These API tests do not operate host services. Controller tests separately prove
that actual registrations, preconditions and constituent effects are observed.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from groundtruth_kb.bridge.native import NativeBridgeService
from psycopg import sql

from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.bridge_fixtures import claim, deliver
from platform_tests.groundtruth_kb.native_fixtures import history_count, put
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = pytest.mark.integration


def _bound(root, *, operation="services.stop-all", targets=None, expiry="claim"):
    targets = targets or ["service:authority", "service:home"]
    service_targets = [target for target in targets if target.startswith("service:")]
    verification = {"states": {target: "stopped" for target in service_targets}}
    if "browser:home" in targets:
        verification["browser_origin"] = "http://127.0.0.1:3080/"
    return {
        "operation": operation,
        "targets": targets,
        "preconditions": {
            "installation_root": str(root),
            "config_path": str(root / "groundtruth.toml"),
            "controller_paths": {target: str(root / "code.py") for target in targets},
            "states": {target: "any" for target in service_targets},
        },
        "permitted_effects": [
            {"target": target, "effect": effect}
            for target in service_targets
            for effect in ("service.stop", "service.start", "task.disable", "process.stop")
        ]
        + ([{"target": "browser:home", "effect": "browser.open"}] if "browser:home" in targets else []),
        "expiry": expiry,
        "verification": verification,
        "containment": {"installation_only": True, "managed_processes_only": True},
        "rollback": {"restore_initial_state": True, "only_invocation_changes": True},
    }


def _setup(bridge, *, transform=None, key="WI-1", holder="pb2", operation="services.stop-all"):
    service, client, contexts, work_root = bridge
    root = work_root.parents[2]
    bound = _bound(root, operation=operation)
    observed_controller_paths = deepcopy(bound["preconditions"]["controller_paths"])
    entries = [bound]
    if transform:
        entries = transform(entries)
    constraints = (
        {"ordinary_operations": {key: entries}}
        if entries is not None
        else {"ordinary_operation_schema": {"eight_substantive_fields_required": True}}
    )
    saved = put(client, "specifications", "SPEC-1", {"constraints": constraints}, expected_version=1)
    assert saved.status_code == 200, saved.text
    deliver(client, contexts, "ops-chain", "pb1", 1, "NEW", spec_versions=json.dumps({"SPEC-1": 2}))
    if holder == "lo1":
        reserved = claim(client, "ops-chain", holder, 1, "GO")
    else:
        deliver(client, contexts, "ops-chain", "lo1", 2, "GO")
        reserved = claim(client, "ops-chain", holder, 2, "READY")
    assert reserved.status_code == 200, reserved.text
    body = {
        "native_context_id": holder,
        "cwd": str(root),
        "activity": "ops",
        "document": "ops-chain",
        "fence": reserved.json()["fence"],
        "installation_root": str(root),
        "config_path": str(root / "groundtruth.toml"),
        "observed_controller_paths": observed_controller_paths,
        "operations": [
            {
                "operation": operation,
                "targets": ["service:all"],
                "effects": [{"target": "service:all", "effect": "service.stop"}],
            }
        ],
    }
    return service, client, root, body, reserved.json()


def _check(client, body):
    return client.post("/v1/bridge/check-effects", json=body)


def _refused(client, body, code):
    result = _check(client, body)
    assert result.status_code in {409, 422}, result.text
    assert result.json()["error"]["code"] == code, result.text


def test_initial_scope_inspection_adds_no_effect_or_permission(bridge):
    service, client, _, body, _ = _setup(bridge)
    before = history_count(service)
    body["operations"][0]["effects"] = []
    result = _check(client, body)
    assert result.status_code == 200, result.text
    checked = result.json()["operations"][0]
    assert checked["targets"] == ["service:authority", "service:home"]
    assert checked["effects"] == []
    assert history_count(service) == before
    body["operations"][0]["effects"] = [{"target": "service:home", "effect": "task.enable"}]
    _refused(client, body, "operation_effect_mismatch")


def test_exact_aggregate_bound_expands_only_canonical_targets_without_retaining_permission(bridge):
    service, client, _, body, reserved = _setup(bridge)
    history = history_count(service)
    before = client.get("/v1/bridge/ops-chain/show", params={"include_content": True}).json()
    formal = client.get("/v1/specifications/SPEC-1").json()
    result = _check(client, body)
    assert result.status_code == 200, result.text
    answer = result.json()
    assert answer["scope"] == "operation"
    assert answer["document"] == "ops-chain" and answer["fence"] == reserved["fence"]
    assert answer["operations"][0]["targets"] == ["service:authority", "service:home"]
    assert answer["operations"][0]["formal_sources"] == [{"id": "SPEC-1", "version": 2}]
    assert datetime.fromisoformat(answer["deadline"]) <= datetime.fromisoformat(reserved["expires_at"])
    assert answer["operations"][0]["bound"]["expiry"] == "claim"
    assert history_count(service) == history
    assert client.get("/v1/bridge/ops-chain/show", params={"include_content": True}).json() == before
    assert client.get("/v1/specifications/SPEC-1").json() == formal
    assert _check(client, body).status_code == 200
    assert history_count(service) == history


@pytest.mark.parametrize(
    "key,transform",
    [
        ("WI-1", lambda _entries: None),
        ("WI-UNRELATED", lambda entries: entries),
    ],
)
def test_generic_contract_and_other_work_bounds_do_not_grant_this_work(bridge, key, transform):
    _, client, _, body, _ = _setup(bridge, key=key, transform=transform)
    _refused(client, body, "operation_bound_required")


@pytest.mark.parametrize(
    "field", ["preconditions", "permitted_effects", "expiry", "verification", "containment", "rollback"]
)
def test_incomplete_formal_bound_fails_closed(bridge, field):
    def remove(entries):
        entries[0].pop(field)
        return entries

    _, client, _, body, _ = _setup(bridge, transform=remove)
    _refused(client, body, "operation_bound_invalid")


def test_conflicting_current_bounds_are_refused(bridge):
    def conflict(entries):
        other = deepcopy(entries[0])
        other["preconditions"]["states"]["service:home"] = "running"
        return [*entries, other]

    _, client, _, body, _ = _setup(bridge, transform=conflict)
    _refused(client, body, "operation_bound_conflict")


def test_equivalent_bound_target_and_effect_order_does_not_create_a_conflict(bridge):
    def reorder(entries):
        other = deepcopy(entries[0])
        other["targets"].reverse()
        other["permitted_effects"].reverse()
        return [*entries, other]

    _, client, _, body, _ = _setup(bridge, transform=reorder)
    result = _check(client, body)
    assert result.status_code == 200, result.text
    assert result.json()["operations"][0]["targets"] == ["service:authority", "service:home"]


def test_equivalent_resolved_controller_paths_do_not_create_a_conflict(bridge):
    def equivalent(entries):
        duplicate = deepcopy(entries[0])
        for target, path in duplicate["preconditions"]["controller_paths"].items():
            original = Path(path)
            duplicate["preconditions"]["controller_paths"][target] = str(original.parent) + "/./" + original.name
        entries.append(duplicate)
        return entries

    _, client, _, body, _ = _setup(bridge, transform=equivalent)
    result = _check(client, body)
    assert result.status_code == 200, result.text


def test_control_boolean_and_numeric_bounds_still_conflict(bridge):
    def conflict(entries):
        bound = entries[0]
        bound["targets"] = ["control:service.ready_seconds"]
        bound["preconditions"]["controller_paths"] = {
            "control:service.ready_seconds": next(iter(bound["preconditions"]["controller_paths"].values()))
        }
        bound["preconditions"]["states"] = {}
        bound["permitted_effects"] = [{"target": "control:service.ready_seconds", "effect": "control.set", "value": 1}]
        bound["verification"] = {"control_values": {"service.ready_seconds": 1}}
        other = deepcopy(bound)
        other["permitted_effects"][0]["value"] = True
        other["verification"]["control_values"]["service.ready_seconds"] = True
        return [bound, other]

    _, client, _, body, _ = _setup(bridge, operation="controls.set", transform=conflict)
    body["operations"] = [
        {
            "operation": "controls.set",
            "targets": ["control:service.ready_seconds"],
            "effects": [{"target": "control:service.ready_seconds", "effect": "control.set", "value": 1}],
        }
    ]
    _refused(client, body, "operation_bound_conflict")


def test_claim_expiry_after_fence_validation_cannot_return_current(bridge, monkeypatch):
    service, client, _, body, _ = _setup(bridge)
    original = NativeBridgeService._fenced

    def expire_after_validation(self, tx, document, request):
        binding, attempt, reserved = original(self, tx, document, request)
        # Simulate the elapsed claim deadline after its initial successful fence check.
        reserved = {**reserved, "expires_at": datetime.now(UTC) - timedelta(seconds=1)}
        return binding, attempt, reserved

    monkeypatch.setattr(NativeBridgeService, "_fenced", expire_after_validation)
    before = history_count(service)
    _refused(client, body, "operation_bound_expired")
    assert history_count(service) == before


@pytest.mark.parametrize(
    "change,code",
    [
        ({"activity": "build"}, "operation_activity_required"),
        ({"activity": None}, "operation_activity_required"),
        ({"fence": None}, "operation_selector_required"),
        ({"document": None}, "operation_selector_required"),
        ({"fence": 999999}, "stale_artifact_fence"),
        ({"installation_root": None}, "operation_installation_required"),
        ({"observed_controller_paths": {}}, "operation_controller_mismatch"),
    ],
)
def test_activity_exact_selectors_and_controller_observations_are_required(bridge, change, code):
    _, client, _, body, _ = _setup(bridge)
    _refused(client, {**body, **change}, code)


def test_immutable_lo_role_cannot_perform_an_ordinary_operation(bridge):
    _, client, _, body, _ = _setup(bridge, holder="lo1")
    _refused(client, body, "operation_role_required")


def test_config_root_and_controller_identity_cannot_be_substituted(bridge):
    _, client, root, body, _ = _setup(bridge)
    _refused(client, {**body, "config_path": str(root / "another.toml")}, "operation_installation_mismatch")
    _refused(client, {**body, "installation_root": str(root / "another")}, "operation_installation_mismatch")
    observed = {**body["observed_controller_paths"], "service:home": str(root / "second.py")}
    _refused(client, {**body, "observed_controller_paths": observed}, "operation_controller_mismatch")


def test_every_command_target_effect_and_full_controller_aggregate_is_covered(bridge):
    _, client, _, body, _ = _setup(bridge)
    actual = deepcopy(body)
    actual["operations"][0]["targets"] = ["service:authority", "service:home"]
    actual["operations"][0]["effects"] = [{"target": "service:authority", "effect": "process.stop"}]
    assert _check(client, actual).status_code == 200  # A terminal suffix retains the full aggregate set.
    missing = deepcopy(actual)
    missing["operations"][0]["targets"] = ["service:authority"]
    _refused(client, missing, "operation_target_mismatch")
    uncovered = deepcopy(actual)
    uncovered["operations"][0]["targets"].append("service:postgresql")
    _refused(client, uncovered, "operation_target_mismatch")
    uncovered_effect = deepcopy(actual)
    uncovered_effect["operations"][0]["effects"] = [{"target": "service:home", "effect": "task.start"}]
    _refused(client, uncovered_effect, "operation_effect_mismatch")
    mixed = deepcopy(body)
    mixed["operations"].append(
        {
            "operation": "controls.set",
            "targets": ["control:service.ready_seconds"],
            "effects": [{"target": "control:service.ready_seconds", "effect": "control.set", "value": 10}],
        }
    )
    _refused(client, mixed, "operation_bound_required")


@pytest.mark.parametrize("expiry", ["2000-01-01T00:00:00Z", "2000-01-01T00:00:00", "forever"])
def test_expired_or_malformed_bound_has_no_success(bridge, expiry):
    def expire(entries):
        entries[0]["expiry"] = expiry
        return entries

    _, client, _, body, _ = _setup(bridge, transform=expire)
    code = "operation_bound_expired" if expiry.endswith("Z") else "operation_bound_invalid"
    _refused(client, body, code)


def test_explicit_earlier_expiry_is_capped_by_the_existing_claim(bridge):
    earlier = datetime.now(UTC) + timedelta(seconds=90)

    def expiry(entries):
        entries[0]["expiry"] = earlier.isoformat()
        return entries

    _, client, _, body, reserved = _setup(bridge, transform=expiry)
    result = _check(client, body)
    assert result.status_code == 200, result.text
    assert datetime.fromisoformat(result.json()["deadline"]) == min(
        earlier, datetime.fromisoformat(reserved["expires_at"])
    )


def test_claim_expiry_and_formal_drift_are_rechecked_without_consuming_claim(bridge):
    service, client, _, body, _ = _setup(bridge)
    assert _check(client, body).status_code == 200
    assert (
        put(
            client, "specifications", "SPEC-1", {"description": "Changed current constraints"}, expected_version=2
        ).status_code
        == 200
    )
    _refused(client, body, "scope_changed")
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL(
                "UPDATE {}.work_intent_claims SET expires_at=clock_timestamp()-interval '1 second' WHERE attempt_id=%s"
            ).format(sql.Identifier(tx.schema)),
            ("ops-chain",),
        )
    _refused(client, body, "stale_artifact_fence")


def test_operational_success_does_not_bypass_ordinary_file_scope(bridge):
    _, client, _, body, _ = _setup(bridge)
    opened = client.post(
        "/v1/bridge/ops-chain/worktree",
        json={
            "native_context_id": "pb2",
            "fence": body["fence"],
        },
    )
    assert opened.status_code == 200, opened.text
    checkout = Path(opened.json()["path"])
    combined = {**body, "cwd": str(checkout), "paths": ["code.py"]}
    result = _check(client, combined)
    assert result.status_code == 200, result.text
    assert result.json()["files"]["scope"] == "implementation"
    _refused(client, {**combined, "paths": ["second.py"]}, "effect_outside_claim")
    files_only = {"native_context_id": "pb2", "cwd": str(checkout), "paths": ["code.py"]}
    assert _check(client, files_only).json()["scope"] == "implementation"


def _installation_setup(bridge, *, amend=None):
    def installation(entries):
        value = entries[0]
        destination = Path(value["preconditions"]["installation_root"]) / ".groundtruth" / "tools" / "grafana"
        value["targets"] = ["service:dashboard"]
        value["preconditions"]["controller_paths"] = {"service:dashboard": str(destination)}
        value["preconditions"]["states"] = {}
        value["permitted_effects"] = [
            {"target": "service:dashboard", "effect": effect}
            for effect in ("installation.publish", "installation.remove", "process.start", "process.stop")
        ]
        value["verification"] = {"states": {}, "installation": "pinned_grafana_sqlite"}
        if amend:
            amend(value)
        return entries

    result = _setup(bridge, operation="dashboard.install", transform=installation)
    body = result[3]
    body["observed_controller_paths"] = {"service:dashboard": str(result[2] / ".groundtruth" / "tools" / "grafana")}
    body["operations"][0]["targets"] = ["service:dashboard"]
    body["operations"][0]["effects"] = []
    return result


def test_installation_bound_inspection_and_each_actual_effect_are_stateless(bridge):
    service, client, root, body, _ = _installation_setup(bridge)
    before = history_count(service)
    answer = _check(client, body)
    assert answer.status_code == 200, answer.text
    bound = answer.json()["operations"][0]["bound"]
    assert bound["verification"] == {
        "states": {},
        "task_enabled": {},
        "control_values": {},
        "shortcut_arguments": [],
        "installation": "pinned_grafana_sqlite",
    }
    assert (
        Path(bound["preconditions"]["controller_paths"]["service:dashboard"])
        == root / ".groundtruth" / "tools" / "grafana"
    )
    for effect in ("installation.publish", "installation.remove", "process.start", "process.stop"):
        body["operations"][0]["effects"] = [{"target": "service:dashboard", "effect": effect}]
        result = _check(client, body)
        assert result.status_code == 200, result.text
        assert result.json()["operations"][0]["effects"] == body["operations"][0]["effects"]
    assert history_count(service) == before


@pytest.mark.parametrize(
    "amend",
    [
        lambda value: value["preconditions"]["controller_paths"].update(
            {"service:dashboard": value["preconditions"]["config_path"]}
        ),
        lambda value: value["preconditions"]["states"].update({"service:dashboard": "any"}),
        lambda value: value["verification"].pop("installation"),
        lambda value: value["verification"]["states"].update({"service:dashboard": "running"}),
        lambda value: value["verification"].update({"browser_origin": "http://127.0.0.1:3080/"}),
        lambda value: value["permitted_effects"].pop(),
        lambda value: value["permitted_effects"].append({"target": "service:dashboard", "effect": "service.start"}),
    ],
)
def test_installation_bound_refuses_nonstandard_incomplete_or_service_mutation_scope(bridge, amend):
    _, client, _, body, _ = _installation_setup(bridge, amend=amend)
    _refused(client, body, "operation_bound_invalid")


@pytest.mark.parametrize(
    "addition",
    [
        lambda value: value["verification"].update({"installation": "pinned_grafana_sqlite"}),
        lambda value: value["permitted_effects"].append(
            {"target": "service:dashboard", "effect": "installation.publish"}
        ),
    ],
)
def test_other_operation_cannot_admit_installation_predicate_or_effect(bridge, addition):
    def change(entries):
        addition(entries[0])
        return entries

    _, client, _, body, _ = _setup(bridge, transform=change)
    _refused(client, body, "operation_bound_invalid")


def test_installation_scope_inspection_does_not_allow_undeclared_existing_service_effect(bridge):
    _, client, _, body, _ = _installation_setup(bridge)
    body["operations"][0]["effects"] = [{"target": "service:dashboard", "effect": "service.stop"}]
    _refused(client, body, "operation_effect_mismatch")
    body["operations"][0]["effects"] = [{"target": "service:home", "effect": "installation.remove"}]
    _refused(client, body, "operation_bound_invalid")
