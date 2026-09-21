"""Application operators use the current layout and fail when an operation fails."""

from __future__ import annotations

import asyncio
import base64
import copy
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_model(monkeypatch, name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / "applications/Agent_Red/src" / relative)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def helpers(monkeypatch):
    monkeypatch.setattr(sys, "path", sys.path.copy())
    for name in (
        "SEED_TENANT_ID",
        "SEED_SHOP_DOMAIN",
        "SEED_CUSTOMER_EMAIL",
        "SEED_TIER",
        "SEED_BILLING_CHANNEL",
        "SEED_INTERVAL",
    ):
        monkeypatch.delenv(name, raising=False)
    env = ModuleType("scripts._env")
    env.load_env_local = Mock()
    monkeypatch.setitem(sys.modules, "scripts._env", env)
    manager = SimpleNamespace(_ensure_client=AsyncMock(), initialize=AsyncMock(), close=AsyncMock())
    kb = SimpleNamespace(
        query=AsyncMock(return_value=[{"id": "kb-1", "title": "One"}]),
        read=AsyncMock(return_value={"title": "One", "content": "Content"}),
        patch=AsyncMock(),
        list_active=AsyncMock(return_value=[]),
        create=AsyncMock(),
    )
    tenant = SimpleNamespace(create=AsyncMock(), upsert=AsyncMock())
    preferences = SimpleNamespace(create=AsyncMock(), upsert=AsyncMock())
    team = SimpleNamespace(create=AsyncMock(), upsert=AsyncMock())
    usage = SimpleNamespace(create=AsyncMock(), upsert=AsyncMock())
    cosmos_factory = Mock(return_value=manager)
    conflict = type("DocumentConflictError", (Exception,), {})
    vectorizer = SimpleNamespace(_configured=True, embed_unembedded=AsyncMock())
    modules = {
        "src": {},
        "src.multi_tenant": {},
        "src.multi_tenant.cosmos_client": {"get_cosmos_manager": cosmos_factory},
        "src.multi_tenant.repository": {
            "KnowledgeBaseRepository": lambda: kb,
            "TenantRepository": lambda: tenant,
            "PreferencesRepository": lambda: preferences,
            "TeamMemberRepository": lambda: team,
            "UsageRepository": lambda: usage,
            "DocumentConflictError": conflict,
        },
        "src.multi_tenant.auth": {
            "generate_user_api_key": lambda _: "fixture-user-key",
            "hash_api_key": lambda _: "fixture-hash",
        },
        "src.multi_tenant.knowledge_vectorizer": {
            "compute_content_hash": lambda *_: "fixture-content-hash",
            "get_knowledge_vectorizer": lambda: vectorizer,
            "EMBEDDING_MODEL": "fixture-model",
            "EMBEDDING_DIMENSIONS": 2,
            "MAX_CONTENT_CHARS": 100,
        },
    }
    for name, values in modules.items():
        module = ModuleType(name)
        module.__path__ = []
        vars(module).update(values)
        monkeypatch.setitem(sys.modules, name, module)
    schema = load_model(monkeypatch, "src.multi_tenant.cosmos_schema", "multi_tenant/cosmos_schema.py")

    def load(name):
        spec = importlib.util.spec_from_file_location(f"application_helper_{name}", ROOT / "scripts" / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, module)
        spec.loader.exec_module(module)
        env.load_env_local.assert_not_called()
        assert module.APP_ROOT == ROOT / "applications" / "Agent_Red"
        return module

    return SimpleNamespace(
        load=load,
        env=env,
        manager=manager,
        factory=cosmos_factory,
        kb=kb,
        tenant=tenant,
        preferences=preferences,
        team=team,
        usage=usage,
        vectorizer=vectorizer,
        conflict=conflict,
        schema=schema,
    )


def test_embedding_preview_reads_without_schema_or_document_writes(helpers):
    mod = helpers.load("embed_knowledge_base")
    asyncio.run(mod.run("selected-tenant"))
    helpers.manager._ensure_client.assert_awaited_once()
    helpers.manager.initialize.assert_not_awaited()
    assert helpers.kb.query.await_args.kwargs["tenant_id"] == "selected-tenant"
    helpers.kb.patch.assert_not_awaited()
    helpers.manager.close.assert_awaited_once()


@pytest.mark.parametrize("failure", ["query", "missing_credentials", "write"])
def test_embedding_failure_propagates_and_closes_clients(helpers, monkeypatch, failure):
    mod = helpers.load("embed_knowledge_base")
    client = SimpleNamespace(
        embeddings=SimpleNamespace(
            create=AsyncMock(return_value=SimpleNamespace(data=[SimpleNamespace(embedding=[0.2, 0.4])]))
        ),
        close=AsyncMock(),
    )
    openai = ModuleType("openai")
    openai.AsyncAzureOpenAI = Mock(return_value=client)
    monkeypatch.setitem(sys.modules, "openai", openai)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fixture.invalid")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "fixture-key")
    if failure == "query":
        helpers.kb.query.side_effect = RuntimeError("query failed")
    elif failure == "missing_credentials":
        monkeypatch.delenv("AZURE_OPENAI_API_KEY")
    else:
        helpers.kb.patch.side_effect = RuntimeError("write failed")
    with pytest.raises(RuntimeError):
        asyncio.run(mod.run("selected-tenant", do_embed=True))
    helpers.manager.close.assert_awaited_once()
    if failure == "write":
        client.close.assert_awaited_once()
    else:
        openai.AsyncAzureOpenAI.assert_not_called()


@pytest.mark.parametrize("field", [None, "title", "content"])
def test_embedding_requires_actual_vector_and_decoded_content(helpers, monkeypatch, field):
    mod = helpers.load("embed_knowledge_base")
    helpers.kb.query.return_value = [
        {"id": "kb-1", "title": "One", "embedding_model": "stale-model", "embedding": None}
    ]
    entry = {"id": "kb-1", "title": "One", "content": "Decoded content"}
    if field:
        entry[field] = base64.b64encode(b"ciphertext-fixture-that-is-not-plaintext").decode("ascii")
    helpers.kb.read.return_value = entry
    client = SimpleNamespace(
        embeddings=SimpleNamespace(
            create=AsyncMock(return_value=SimpleNamespace(data=[SimpleNamespace(embedding=[0.2, 0.4])]))
        ),
        close=AsyncMock(),
    )
    openai = ModuleType("openai")
    openai.AsyncAzureOpenAI = Mock(return_value=client)
    monkeypatch.setitem(sys.modules, "openai", openai)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fixture.invalid")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "fixture-key")
    if field:
        with pytest.raises(RuntimeError, match=f"undecoded {field}"):
            asyncio.run(mod.run("selected-tenant", do_embed=True))
        client.embeddings.create.assert_not_awaited()
        helpers.kb.patch.assert_not_awaited()
    else:
        asyncio.run(mod.run("selected-tenant", do_embed=True))
        assert "Decoded content" in client.embeddings.create.await_args.kwargs["input"][0]
        helpers.kb.patch.assert_awaited_once()
    assert "c.embedding FROM" in helpers.kb.query.await_args.kwargs["query_text"]
    helpers.manager.close.assert_awaited_once()
    client.close.assert_awaited_once()


def test_provision_preview_never_opens_database(helpers):
    mod = helpers.load("provision_tenant_one")
    asyncio.run(mod.provision())
    helpers.factory.assert_not_called()
    helpers.tenant.create.assert_not_awaited()


@pytest.mark.parametrize("failure", [None, "preferences", "team"])
def test_provision_uses_loaded_configuration_and_fails_on_incomplete_write(helpers, monkeypatch, failure):
    mod = helpers.load("provision_tenant_one")
    monkeypatch.setattr(sys, "argv", ["provision_tenant_one.py", "--provision"])

    def load_env(**kwargs):
        assert kwargs["env_file"] == mod.APP_ROOT / ".env.local"
        monkeypatch.setenv("SEED_TENANT_ID", "selected-tenant")
        monkeypatch.setenv("SEED_TIER", "starter")
        monkeypatch.setenv("SEED_BILLING_CHANNEL", "stripe")

    helpers.env.load_env_local.side_effect = load_env
    if failure:
        getattr(helpers, failure).create.side_effect = RuntimeError("storage unavailable")
        with pytest.raises(RuntimeError, match="storage unavailable"):
            asyncio.run(mod.main())
    else:
        asyncio.run(mod.main())
    selected, document = helpers.tenant.create.await_args.args
    assert selected == document.tenant_id == "selected-tenant"
    assert document.tier == "starter"
    assert document.billing_channel == "stripe"
    assert document.rate_limit_rpm is None
    assert document.max_concurrent is None
    helpers.manager.close.assert_awaited_once()
    if failure == "preferences":
        helpers.team.create.assert_not_awaited()


@pytest.mark.parametrize("record", ["tenant", "preferences", "team"])
@pytest.mark.parametrize("typed_conflict", [True, False])
def test_provision_updates_only_typed_existing_record_conflicts(helpers, record, typed_conflict):
    mod = helpers.load("provision_tenant_one")
    repository = getattr(helpers, record)
    error = helpers.conflict if typed_conflict else RuntimeError
    repository.create.side_effect = error("409 Conflict already exists in an unrelated service response")
    if typed_conflict:
        asyncio.run(mod.provision(dry_run=False))
        repository.upsert.assert_awaited_once()
    else:
        with pytest.raises(RuntimeError, match="unrelated service response"):
            asyncio.run(mod.provision(dry_run=False))
        repository.upsert.assert_not_awaited()
    helpers.manager.close.assert_awaited_once()


def test_seed_summary_stays_offline(helpers, monkeypatch):
    mod = helpers.load("seed_knowledge_base")
    monkeypatch.setattr(sys, "argv", ["seed_knowledge_base.py"])
    asyncio.run(mod.main())
    helpers.env.load_env_local.assert_not_called()
    helpers.factory.assert_not_called()


@pytest.mark.parametrize("failure", ["write", "embedding"])
def test_seed_failure_is_not_reported_as_success_and_closes_database(helpers, monkeypatch, failure):
    mod = helpers.load("seed_knowledge_base")
    monkeypatch.setattr(mod, "SEED_ARTICLES", [{"title": "One", "content": "Content", "entry_type": "faq"}])
    monkeypatch.setattr(sys, "argv", ["seed_knowledge_base.py", "--load", "--embed"])
    if failure == "write":
        helpers.kb.create.side_effect = RuntimeError("storage unavailable")
    else:
        embedding = ModuleType("scripts.embed_knowledge_base")
        embedding.run = AsyncMock(side_effect=RuntimeError("embedding unavailable"))
        monkeypatch.setitem(sys.modules, "scripts.embed_knowledge_base", embedding)
    with pytest.raises(RuntimeError):
        asyncio.run(mod.main())
    helpers.env.load_env_local.assert_called_once_with(env_file=mod.APP_ROOT / ".env.local")
    helpers.manager.initialize.assert_not_awaited()
    helpers.manager.close.assert_awaited_once()


def test_seed_retries_embedding_when_all_articles_already_exist(helpers, monkeypatch):
    mod = helpers.load("seed_knowledge_base")
    article = {"title": "Existing", "content": "Content", "entry_type": "faq"}
    monkeypatch.setattr(mod, "SEED_ARTICLES", [article])
    helpers.kb.list_active.return_value = [article]
    embedding = ModuleType("scripts.embed_knowledge_base")
    embedding.run = AsyncMock()
    monkeypatch.setitem(sys.modules, "scripts.embed_knowledge_base", embedding)
    asyncio.run(mod.load_to_cosmos("selected-tenant", embed=True))
    helpers.kb.create.assert_not_awaited()
    embedding.run.assert_awaited_once_with(tenant_id="selected-tenant", do_embed=True)


def test_demo_preview_never_opens_database(helpers):
    mod = helpers.load("seed_demo_data")
    asyncio.run(mod.seed())
    helpers.factory.assert_not_called()


@pytest.mark.parametrize("failure", [None, "conversations", "usage"])
def test_demo_seeder_uses_selected_tenant_and_reports_write_failures(helpers, monkeypatch, failure):
    mod = helpers.load("seed_demo_data")
    monkeypatch.setenv("SEED_TENANT_ID", "selected-tenant")
    monkeypatch.setattr(sys, "argv", ["seed_demo_data.py", "--seed"])
    containers = {
        name: SimpleNamespace(upsert_item=AsyncMock())
        for name in ("conversations", "customer_profiles", "memory_vectors")
    }
    helpers.manager.get_container = containers.__getitem__
    if failure:
        writer = helpers.usage.create if failure == "usage" else containers[failure].upsert_item
        writer.side_effect = RuntimeError("write unavailable")
        with pytest.raises(RuntimeError, match="demo data writes failed"):
            asyncio.run(mod.main())
    else:
        asyncio.run(mod.main())
    for container in containers.values():
        assert container.upsert_item.await_count > 0
        assert all(call.args[0]["tenant_id"] == "selected-tenant" for call in container.upsert_item.await_args_list)
    assert helpers.team.create.await_count == len(mod.TEAM_MEMBERS)
    assert all(call.args[1].tenant_id == "selected-tenant" for call in helpers.team.create.await_args_list)
    helpers.team.upsert.assert_not_awaited()
    assert helpers.usage.create.await_args.args[1].tenant_id == "selected-tenant"
    helpers.usage.upsert.assert_not_awaited()
    helpers.manager.close.assert_awaited_once()
    helpers.env.load_env_local.assert_called_once_with(env_file=mod.APP_ROOT / ".env.local")


def test_demo_seeding_preserves_provisioned_accounts_and_billing_on_repeated_runs(helpers, monkeypatch):
    demo = helpers.load("seed_demo_data")
    monkeypatch.setenv("SEED_CUSTOMER_EMAIL", demo.TEAM_MEMBERS[0]["email"])
    provision = helpers.load("provision_tenant_one")
    asyncio.run(provision.provision(dry_run=False))
    owner = helpers.team.create.await_args.args[1].model_dump(mode="json")
    before = copy.deepcopy(owner)
    stored = {owner["id"]: owner}

    async def create(tenant, document):
        assert tenant == document.tenant_id
        if document.id in stored:
            raise helpers.conflict("existing account")
        stored[document.id] = document.model_dump(mode="json")

    helpers.team.create.side_effect = create
    demo.TENANT_ID = owner["tenant_id"]
    counter = demo.build_usage_counter_doc(987)
    counter["overage_reported"] = 654
    counter["stripe_meter_total"] = 321
    counter_before = copy.deepcopy(counter)

    async def replace_team(document):
        stored[document["id"]] = copy.deepcopy(document)

    async def replace_usage(document):
        counter.clear()
        counter.update(copy.deepcopy(document))

    containers = {
        "team_members": SimpleNamespace(upsert_item=AsyncMock(side_effect=replace_team)),
        "usage": SimpleNamespace(upsert_item=AsyncMock(side_effect=replace_usage)),
    }
    helpers.manager.get_container = lambda name: containers.get(name, SimpleNamespace(upsert_item=AsyncMock()))

    async def create_counter(tenant, document):
        assert tenant == counter["tenant_id"]
        assert document.id == counter["id"]
        raise helpers.conflict("existing billing counter")

    helpers.usage.create.side_effect = create_counter
    asyncio.run(demo.seed(dry_run=False))
    first = copy.deepcopy(stored)
    asyncio.run(demo.seed(dry_run=False))
    assert stored == first
    assert stored[owner["id"]] == before
    assert before["role"] == "superadmin"
    assert before["user_api_key_hash"] == "fixture-hash"
    assert before["user_api_key_prefix"]
    assert len(stored) == len(demo.TEAM_MEMBERS)
    assert counter == counter_before
    assert helpers.usage.create.await_count == 2
    helpers.team.upsert.assert_not_awaited()
    helpers.usage.upsert.assert_not_awaited()


def test_demo_documents_match_current_application_models(helpers, monkeypatch):
    mod = helpers.load("seed_demo_data")
    chat = load_model(monkeypatch, "application_chat_models", "chat/models.py")
    conversations = mod.build_conversation_docs() + mod.build_memory_conversation_docs()
    assert conversations
    for conversation in conversations:
        helpers.schema.ConversationDocument.model_validate(conversation)
        if conversation["status"] == "active":
            assert conversation["ended_at"] is None
        elif conversation["status"] == "resolved":
            assert conversation["ended_at"] is not None
        for message in conversation["messages"]:
            chat.ChatMessage.model_validate(message)
    for member in mod.build_team_member_docs():
        helpers.schema.TeamMemberDocument.model_validate(member)
    helpers.schema.UsageCounterDocument.model_validate(mod.build_usage_counter_doc(len(conversations)))
