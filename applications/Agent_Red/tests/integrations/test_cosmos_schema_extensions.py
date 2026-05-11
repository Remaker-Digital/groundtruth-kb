"""Tests for Cosmos DB Schema Extensions (SPEC-1773).

Tests cover:
  - New integration container constants exist
  - Container configs included in get_collection_configs()
  - TTL settings correct
  - Unique key policies
  - Indexing policies for events container
  - Integration with existing schema (no collisions)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.cosmos_schema import (
    ALL_COLLECTIONS,
    COLLECTION_INTEGRATION_CREDENTIALS,
    COLLECTION_INTEGRATION_EVENTS,
    COLLECTION_INTEGRATION_SYNC_STATE,
    COLLECTION_NORMALIZED_CONTACTS,
    COLLECTION_NORMALIZED_TICKETS,
    TTL_INTEGRATION_EVENTS,
    get_collection_configs,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INTEGRATION_CONTAINERS = [
    COLLECTION_INTEGRATION_CREDENTIALS,
    COLLECTION_INTEGRATION_SYNC_STATE,
    COLLECTION_INTEGRATION_EVENTS,
    COLLECTION_NORMALIZED_TICKETS,
    COLLECTION_NORMALIZED_CONTACTS,
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestContainerConstants:
    def test_integration_credentials_name(self):
        assert COLLECTION_INTEGRATION_CREDENTIALS == "integration_credentials"

    def test_integration_sync_state_name(self):
        assert COLLECTION_INTEGRATION_SYNC_STATE == "integration_sync_state"

    def test_integration_events_name(self):
        assert COLLECTION_INTEGRATION_EVENTS == "integration_events"

    def test_normalized_tickets_name(self):
        assert COLLECTION_NORMALIZED_TICKETS == "normalized_tickets"

    def test_normalized_contacts_name(self):
        assert COLLECTION_NORMALIZED_CONTACTS == "normalized_contacts"

    def test_all_integration_containers_in_all_collections(self):
        for container in INTEGRATION_CONTAINERS:
            assert container in ALL_COLLECTIONS, f"{container} not in ALL_COLLECTIONS"

    def test_ttl_integration_events_is_30_days(self):
        assert TTL_INTEGRATION_EVENTS == 30 * 24 * 60 * 60


class TestCollectionConfigs:
    @pytest.fixture
    def configs(self):
        return get_collection_configs()

    @pytest.fixture
    def config_map(self, configs):
        return {c.name: c for c in configs}

    def test_all_integration_containers_have_configs(self, config_map):
        for name in INTEGRATION_CONTAINERS:
            assert name in config_map, f"No config for {name}"

    def test_credentials_partition_key(self, config_map):
        cfg = config_map[COLLECTION_INTEGRATION_CREDENTIALS]
        assert cfg.partition_key == "/tenant_id"

    def test_credentials_unique_keys(self, config_map):
        cfg = config_map[COLLECTION_INTEGRATION_CREDENTIALS]
        assert len(cfg.unique_keys) == 1
        assert "/tenant_id" in cfg.unique_keys[0]
        assert "/integration_id" in cfg.unique_keys[0]
        assert "/secret_type" in cfg.unique_keys[0]

    def test_sync_state_partition_key(self, config_map):
        cfg = config_map[COLLECTION_INTEGRATION_SYNC_STATE]
        assert cfg.partition_key == "/tenant_id"

    def test_sync_state_unique_keys(self, config_map):
        cfg = config_map[COLLECTION_INTEGRATION_SYNC_STATE]
        assert len(cfg.unique_keys) == 1
        assert "/tenant_id" in cfg.unique_keys[0]
        assert "/integration_id" in cfg.unique_keys[0]

    def test_events_has_ttl(self, config_map):
        cfg = config_map[COLLECTION_INTEGRATION_EVENTS]
        assert cfg.default_ttl == TTL_INTEGRATION_EVENTS

    def test_events_indexing_policy_excludes_payload(self, config_map):
        cfg = config_map[COLLECTION_INTEGRATION_EVENTS]
        assert cfg.indexing_policy is not None
        excluded = [p["path"] for p in cfg.indexing_policy.get("excludedPaths", [])]
        assert "/payload/*" in excluded

    def test_events_indexes_event_type(self, config_map):
        cfg = config_map[COLLECTION_INTEGRATION_EVENTS]
        assert cfg.indexing_policy is not None
        included = [p["path"] for p in cfg.indexing_policy.get("includedPaths", [])]
        assert "/event_type/?" in included

    def test_normalized_tickets_partition_key(self, config_map):
        cfg = config_map[COLLECTION_NORMALIZED_TICKETS]
        assert cfg.partition_key == "/tenant_id"

    def test_normalized_tickets_excludes_raw(self, config_map):
        cfg = config_map[COLLECTION_NORMALIZED_TICKETS]
        assert cfg.indexing_policy is not None
        excluded = [p["path"] for p in cfg.indexing_policy.get("excludedPaths", [])]
        assert "/raw/*" in excluded

    def test_normalized_contacts_partition_key(self, config_map):
        cfg = config_map[COLLECTION_NORMALIZED_CONTACTS]
        assert cfg.partition_key == "/tenant_id"

    def test_no_duplicate_container_names(self, configs):
        names = [c.name for c in configs]
        assert len(names) == len(set(names)), "Duplicate container names found"

    def test_total_container_count(self, configs):
        # Should be 25 total (20 original + 5 integration)
        assert len(configs) >= 25
