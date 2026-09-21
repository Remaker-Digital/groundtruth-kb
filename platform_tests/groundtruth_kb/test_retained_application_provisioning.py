"""SPEC-1591 retained provisioning behavior after one-off script retirement.

Exercises the actual hosted application schema function against an in-memory
Cosmos client double. No cloud credentials, cloud effects or server acceptance
are claimed. The configured container arguments and error propagation are real.
"""

from __future__ import annotations

import ast
import asyncio
import builtins
import importlib.util
import logging
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def schema(monkeypatch):
    path = Path(__file__).resolve().parents[2] / "applications/Agent_Red/src/multi_tenant/cosmos_schema.py"
    spec = importlib.util.spec_from_file_location("retained_agent_red_cosmos_schema", path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def _isolated_definition(relative_path, name, bindings):
    """Execute an unchanged source definition without booting the application."""
    path = Path(__file__).resolve().parents[2] / relative_path
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    definitions = [node for node in tree.body if getattr(node, "name", None) == name]
    assert len(definitions) == 1
    future = ast.parse("from __future__ import annotations").body[0]
    selected = ast.Module(body=[future, definitions[0]], type_ignores=[])
    namespace = {"__name__": "retained_provisioning_source", **bindings}
    exec(compile(selected, str(path), "exec"), namespace)
    return namespace[name]


@pytest.fixture(params=["schema", "manager"])
def initializer(request, schema):
    if request.param == "schema":
        return lambda client: schema.initialize_database(client, "qualification-only"), None
    manager_class = _isolated_definition(
        "applications/Agent_Red/src/multi_tenant/cosmos_client.py",
        "CosmosManager",
        {
            "DATABASE_NAME": schema.DATABASE_NAME,
            "initialize_database": schema.initialize_database,
            "os": SimpleNamespace(environ={"COSMOS_DB_DATABASE": "qualification-only"}),
            "logger": logging.getLogger(__name__),
        },
    )
    manager = manager_class()

    def invoke(client):
        manager._client = client
        return manager.initialize()

    return invoke, manager


class MemoryCosmos:
    def __init__(self, fail_at=None):
        self.fail_at = fail_at
        self.databases = set()
        self.containers = {}
        self.requests = []

    async def create_database_if_not_exists(self, *, id):
        if self.fail_at == "database":
            raise RuntimeError("database unavailable")
        self.databases.add(id)
        return self

    async def create_container_if_not_exists(self, **kwargs):
        self.requests.append(kwargs)
        if kwargs["id"] == self.fail_at:
            raise RuntimeError("container unavailable")
        return self.containers.setdefault(kwargs["id"], kwargs)


def test_contact_container_is_provisioned_idempotently_without_throughput(schema, initializer):
    invoke, manager = initializer
    assert schema.ALL_COLLECTIONS[18] == "contact_messages"
    assert schema.get_collection_configs()[18].name == "contact_messages"
    client = MemoryCosmos()
    first = asyncio.run(invoke(client))
    first_containers = dict(client.containers)
    second = asyncio.run(invoke(client))
    assert first == second
    assert client.databases == {"qualification-only"}
    assert client.containers == first_containers
    assert first["containers"]["contact_messages"] == "ready"
    requests = [row for row in client.requests if row["id"] == "contact_messages"]
    assert len(requests) == 2
    assert all(row["partition_key"] == {"paths": ["/tenant_id"], "kind": "Hash"} for row in requests)
    assert all(
        "offer_throughput" not in row and "throughput" not in row and "autoscale_settings" not in row
        for row in requests
    )
    if manager is not None:
        assert manager._initialized is True


@pytest.mark.parametrize("fail_at", ["database", "contact_messages"])
def test_provisioning_failure_is_propagated_instead_of_returning_ready(initializer, fail_at):
    invoke, manager = initializer
    client = MemoryCosmos(fail_at)
    with pytest.raises(RuntimeError, match="unavailable"):
        asyncio.run(invoke(client))
    assert "contact_messages" not in client.containers
    if fail_at == "database":
        assert not client.databases and not client.requests
    if manager is not None:
        assert manager._initialized is False


def test_contact_startup_binds_both_apis_to_the_contact_container(schema, monkeypatch):
    repositories, admin_calls, superadmin_calls = [], [], []

    def make_repository(collection):
        repo = SimpleNamespace(collection=collection)
        repositories.append(repo)
        return repo

    modules = {
        "src.multi_tenant.admin_contact_api": SimpleNamespace(
            configure_contact_repo=lambda **kwargs: admin_calls.append(kwargs)
        ),
        "src.multi_tenant.superadmin_contact_api": SimpleNamespace(
            configure_superadmin_contact_services=lambda **kwargs: superadmin_calls.append(kwargs)
        ),
        "src.multi_tenant.cosmos_schema": schema,
        "src.multi_tenant.repositories.base": SimpleNamespace(TenantScopedRepository=make_repository),
    }
    actual_import = builtins.__import__

    def selected_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("src."):
            assert name in modules, f"Unexpected application dependency: {name}"
            return modules[name]
        return actual_import(name, globals, locals, fromlist, level)

    startup = _isolated_definition(
        "applications/Agent_Red/src/app/lifecycle.py",
        "_startup_contact_messages",
        {"logger": logging.getLogger(__name__)},
    )
    monkeypatch.setattr(builtins, "__import__", selected_import)
    asyncio.run(startup())
    assert len(repositories) == 1
    assert repositories[0].collection == "contact_messages"
    assert len(admin_calls) == len(superadmin_calls) == 1
    assert admin_calls[0]["repo"] is repositories[0]
    assert superadmin_calls[0]["contact_repo"] is repositories[0]
