"""S181: Record KB artifacts for Build 2 (AGNTCY enforcement)."""
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

kdb = KnowledgeDB()

# 1. Promote specs to implemented
for spec_id in ["SPEC-1780", "SPEC-1781", "SPEC-1788"]:
    kdb.update_spec(spec_id, changed_by="S181", change_reason="Build 2 implementation", status="implemented")
    print(f"Promoted {spec_id} to implemented")

# 2. Record test artifacts
test_file = "tests/integration/test_nats_jetstream.py"
tests = [
    # TestHelperFunctions (6)
    ("test_tenant_topic_format", "TestHelperFunctions", "SPEC-1781", "Tenant topic format is {tenant_id}.{agent}"),
    ("test_tenant_wildcard_format", "TestHelperFunctions", "SPEC-1781", "Tenant wildcard format is {tenant_id}.>"),
    ("test_stream_name_format", "TestHelperFunctions", "SPEC-1781", "Stream name format is tenant-{tenant_id}"),
    ("test_extract_tenant_from_subject", "TestHelperFunctions", "SPEC-1781", "Extract tenant ID from dotted subject"),
    ("test_extract_tenant_from_subject_no_dot", "TestHelperFunctions", "SPEC-1781", "Returns None for subject without dot"),
    ("test_extract_tenant_uuid_style", "TestHelperFunctions", "SPEC-1781", "Extracts UUID-style tenant IDs"),
    # TestCircuitBreaker (6)
    ("test_initial_state_closed", "TestCircuitBreaker", "SPEC-1781", "Circuit breaker starts in CLOSED state"),
    ("test_opens_after_threshold_failures", "TestCircuitBreaker", "SPEC-1781", "Opens after 3 failures within window"),
    ("test_success_resets_to_closed", "TestCircuitBreaker", "SPEC-1781", "Success resets to CLOSED"),
    ("test_reset_clears_state", "TestCircuitBreaker", "SPEC-1781", "Manual reset clears all state"),
    ("test_half_open_after_recovery_period", "TestCircuitBreaker", "SPEC-1781", "Transitions to HALF_OPEN after recovery"),
    ("test_failures_outside_window_not_counted", "TestCircuitBreaker", "SPEC-1781", "Expired failures not counted"),
    # TestAuthorization (5)
    ("test_authorize_own_topic_passes", "TestAuthorization", "SPEC-1781", "Tenant authorized for own topic"),
    ("test_authorize_cross_tenant_raises", "TestAuthorization", "SPEC-1781", "Cross-tenant access raises NATSAuthorizationError"),
    ("test_authorize_platform_topic_raises", "TestAuthorization", "SPEC-1781", "Platform topic rejected for tenants"),
    ("test_authorize_all_agent_topics", "TestAuthorization", "SPEC-1781", "All 6 agent topics authorizable"),
    ("test_authorize_all_platform_topics_rejected", "TestAuthorization", "SPEC-1781", "All platform topics rejected"),
    # TestCorrelationHeaders (5)
    ("test_build_headers_all_fields", "TestCorrelationHeaders", "SPEC-1781", "Headers include all correlation fields"),
    ("test_build_headers_no_trace", "TestCorrelationHeaders", "SPEC-1781", "Headers omit trace when not provided"),
    ("test_extract_headers_from_message", "TestCorrelationHeaders", "SPEC-1781", "Extracts correlation from NATS message"),
    ("test_extract_headers_missing_fields", "TestCorrelationHeaders", "SPEC-1781", "Missing headers return None"),
    ("test_extract_headers_none_headers", "TestCorrelationHeaders", "SPEC-1781", "None headers return None"),
    # TestHealthCheck (3)
    ("test_health_not_connected", "TestHealthCheck", "SPEC-1781", "Health reports not connected"),
    ("test_is_connected_initially_false", "TestHealthCheck", "SPEC-1781", "Initially not connected"),
    ("test_circuit_breaker_state_initially_closed", "TestHealthCheck", "SPEC-1781", "Initial CB state is closed"),
    # TestConnectionGuard (3)
    ("test_publish_requires_connection", "TestConnectionGuard", "SPEC-1781", "Publish raises when not connected"),
    ("test_subscribe_requires_connection", "TestConnectionGuard", "SPEC-1781", "Subscribe raises when not connected"),
    ("test_provision_requires_connection", "TestConnectionGuard", "SPEC-1781", "Provision raises when not connected"),
    # TestFailLoudDispatch (5)
    ("test_require_transport_noop_in_development", "TestFailLoudDispatch", "SPEC-1780", "No-op in development environment"),
    ("test_require_transport_raises_503_in_staging", "TestFailLoudDispatch", "SPEC-1780", "Raises 503 in staging"),
    ("test_require_transport_raises_503_in_production", "TestFailLoudDispatch", "SPEC-1780", "Raises 503 in production"),
    ("test_transport_available_returns_false_when_no_transport", "TestFailLoudDispatch", "SPEC-1780", "Returns False when no transport"),
    ("test_transport_available_returns_true_when_transport_exists", "TestFailLoudDispatch", "SPEC-1780", "Returns True when transport exists"),
    # TestReadyEndpointEnforcement (2)
    ("test_ready_returns_503_in_staging_without_transport", "TestReadyEndpointEnforcement", "SPEC-1780", "/ready returns 503 in staging without transport"),
    ("test_ready_returns_200_in_development_without_transport", "TestReadyEndpointEnforcement", "SPEC-1780", "/ready returns 200 in development without transport"),
    # TestSingletonManagement (2)
    ("test_get_nats_manager_returns_instance", "TestSingletonManagement", "SPEC-1781", "Singleton returns TenantNATSManager"),
    ("test_get_nats_manager_returns_same_instance", "TestSingletonManagement", "SPEC-1781", "Singleton returns same instance"),
    # TestLiveConnection (3)
    ("test_connect_and_close", "TestLiveConnection", "SPEC-1781", "Connect and close lifecycle"),
    ("test_connect_idempotent", "TestLiveConnection", "SPEC-1781", "Connect is idempotent"),
    ("test_close_idempotent", "TestLiveConnection", "SPEC-1781", "Close is idempotent"),
    # TestLiveStreamProvisioning (6)
    ("test_provision_starter_stream", "TestLiveStreamProvisioning", "SPEC-1781", "Provisions starter tier stream"),
    ("test_provision_professional_stream", "TestLiveStreamProvisioning", "SPEC-1781", "Provisions professional tier stream"),
    ("test_update_stream_tier", "TestLiveStreamProvisioning", "SPEC-1781", "Updates stream on tier change"),
    ("test_deprovision_stream", "TestLiveStreamProvisioning", "SPEC-1781", "Deprovisions tenant stream"),
    ("test_deprovision_absent_stream", "TestLiveStreamProvisioning", "SPEC-1781", "Deprovision absent stream succeeds"),
    ("test_update_nonexistent_provisions", "TestLiveStreamProvisioning", "SPEC-1781", "Update nonexistent provisions new stream"),
    # TestLivePublishSubscribe (4)
    ("test_publish_and_receive", "TestLivePublishSubscribe", "SPEC-1781", "Publish and receive message"),
    ("test_cross_tenant_publish_rejected", "TestLivePublishSubscribe", "SPEC-1781", "Cross-tenant publish rejected"),
    ("test_cross_tenant_subscribe_rejected", "TestLivePublishSubscribe", "SPEC-1781", "Cross-tenant subscribe rejected"),
    ("test_correlation_headers_propagated", "TestLivePublishSubscribe", "SPEC-1781", "Correlation headers propagated"),
    # TestLiveQueueGroups (2)
    ("test_queue_group_competing_consumers", "TestLiveQueueGroups", "SPEC-1788", "Queue group distributes to one subscriber"),
    ("test_default_deliver_group_name", "TestLiveQueueGroups", "SPEC-1788", "Default deliver_group name works"),
    # TestLiveHealthCheck (2)
    ("test_health_connected", "TestLiveHealthCheck", "SPEC-1781", "Health reports connected"),
    ("test_health_shows_provisioned_streams", "TestLiveHealthCheck", "SPEC-1781", "Health shows provisioned streams"),
    # TestLiveStreamInspection (2)
    ("test_get_stream_info", "TestLiveStreamInspection", "SPEC-1781", "Gets stream info"),
    ("test_get_nonexistent_stream_info", "TestLiveStreamInspection", "SPEC-1781", "Nonexistent stream returns None"),
]

test_id = 10276
for func, cls, spec, expected in tests:
    tid = f"TEST-{test_id:05d}"
    kdb.insert_test(
        id=tid,
        title=f"{cls}.{func}",
        spec_id=spec,
        test_type="integration",
        expected_outcome=expected,
        changed_by="S181",
        change_reason="Build 2 NATS integration tests",
        test_file=test_file,
        test_class=cls,
        test_function=func,
    )
    test_id += 1

print(f"Recorded {len(tests)} test artifacts (TEST-10276..TEST-{test_id - 1})")

# 3. Resolve WIs
for wi_id in ["WI-1287", "WI-1288", "WI-1291"]:
    try:
        kdb.update_work_item(
            wi_id,
            changed_by="S181",
            change_reason="Build 2 implementation complete",
            resolution_status="resolved",
        )
        print(f"Resolved {wi_id}")
    except Exception as e:
        print(f"Error resolving {wi_id}: {e}")

print("Done.")
