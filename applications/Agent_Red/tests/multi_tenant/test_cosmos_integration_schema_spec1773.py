"""SPEC-1773 integration-framework Cosmos schema coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import pytest

from src.multi_tenant import cosmos_schema as schema

pytestmark = pytest.mark.local_env

INTEGRATION_COLLECTIONS = {
    "credentials": schema.COLLECTION_INTEGRATION_CREDENTIALS,
    "sync_state": schema.COLLECTION_INTEGRATION_SYNC_STATE,
    "events": schema.COLLECTION_INTEGRATION_EVENTS,
    "tickets": schema.COLLECTION_NORMALIZED_TICKETS,
    "contacts": schema.COLLECTION_NORMALIZED_CONTACTS,
}


def _configs_by_name() -> dict[str, schema.CollectionConfig]:
    return {config.name: config for config in schema.get_collection_configs()}


def test_spec1773_integration_collection_constants_are_registered() -> None:
    assert INTEGRATION_COLLECTIONS == {
        "credentials": "integration_credentials",
        "sync_state": "integration_sync_state",
        "events": "integration_events",
        "tickets": "normalized_tickets",
        "contacts": "normalized_contacts",
    }

    for collection_name in INTEGRATION_COLLECTIONS.values():
        assert collection_name in schema.ALL_COLLECTIONS
        assert collection_name in _configs_by_name()


def test_spec1773_integration_collections_are_tenant_partitioned() -> None:
    configs = _configs_by_name()

    for collection_name in INTEGRATION_COLLECTIONS.values():
        assert configs[collection_name].partition_key == "/tenant_id"


def test_spec1773_integration_events_have_thirty_day_ttl() -> None:
    configs = _configs_by_name()

    assert schema.TTL_INTEGRATION_EVENTS == 30 * 24 * 60 * 60
    assert configs[schema.COLLECTION_INTEGRATION_EVENTS].default_ttl == schema.TTL_INTEGRATION_EVENTS


def test_spec1773_tenant_scoped_unique_keys_are_configured() -> None:
    configs = _configs_by_name()

    assert configs[schema.COLLECTION_INTEGRATION_CREDENTIALS].unique_keys == [
        ["/tenant_id", "/integration_id", "/secret_type"]
    ]
    assert configs[schema.COLLECTION_INTEGRATION_SYNC_STATE].unique_keys == [["/tenant_id", "/integration_id"]]
    assert configs[schema.COLLECTION_NORMALIZED_TICKETS].unique_keys == [["/tenant_id", "/external_id", "/source"]]
    assert configs[schema.COLLECTION_NORMALIZED_CONTACTS].unique_keys == [["/tenant_id", "/external_id", "/source"]]


def test_spec1773_leveraged_existing_collections_remain_registered() -> None:
    configs = _configs_by_name()
    leveraged_collections = {
        schema.COLLECTION_KNOWLEDGE_BASES,
        schema.COLLECTION_CONVERSATIONS,
        schema.COLLECTION_TENANTS,
    }

    assert leveraged_collections <= set(schema.ALL_COLLECTIONS)
    assert leveraged_collections <= set(configs)
