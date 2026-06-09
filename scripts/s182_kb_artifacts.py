"""S182: Record KB artifacts for agent containerization (Builds 4-5).

Creates 4 specs (SPEC-1794..1797), 4 work items (WI-1292..1295),
and 39 test artifacts (TEST-10332..10370).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()

# ---------------------------------------------------------------------------
# Specifications
# ---------------------------------------------------------------------------

specs = [
    {
        "id": "SPEC-1794",
        "title": "7 pipeline agents deployed as separate Azure Container Apps",
        "description": (
            "Each of the 7 pipeline agents (intent-classifier, knowledge-retrieval, "
            "response-generator, escalation-handler, analytics-collector, critic-supervisor, "
            "co-pilot) runs as a separate Azure Container App. All containers reuse the "
            "api-gateway Docker image with command overrides to start the correct agent module "
            "via uvicorn. Internal ingress only. Same managed environment (agent-red-env). "
            "0.5 CPU, 1Gi memory, min 1 / max 3 replicas.\n"
            "[Source: src/agents/containers/agent_app.py]"
        ),
        "status": "implemented",
        "type": "requirement",
    },
    {
        "id": "SPEC-1795",
        "title": "Agent containers expose gateway-compatible short path aliases",
        "description": (
            "Each agent container registers short path aliases matching gateway dispatch "
            "constants. IC: /classify, KR: /retrieve, RG: /generate + /generate/stream, "
            "EH: /escalate, AC: /collect, CS: /validate, CP: /process. _GATEWAY_PATHS dict "
            "in agent_app.py maps agent_type to path list.\n"
            "[Source: src/agents/containers/agent_app.py]"
        ),
        "status": "implemented",
        "type": "requirement",
    },
    {
        "id": "SPEC-1796",
        "title": "API gateway dispatches to agent containers via HTTP (Tier 2)",
        "description": (
            "When USE_AGENT_CONTAINERS=true, API gateway dispatches pipeline requests to "
            "agent containers via HTTP using AGENT_*_URL env vars. AGENT_URLS dict in "
            "constants.py maps 7 agent names to URLs.\n"
            "[Source: src/chat/pipeline/constants.py]"
        ),
        "status": "implemented",
        "type": "requirement",
    },
    {
        "id": "SPEC-1797",
        "title": "Co-pilot agent has a dedicated container entry point",
        "description": (
            "co_pilot_app.py provides the 7th agent container entry point, using "
            "create_agent_app() factory with CoPilotAgent class and _configure function "
            "that injects AsyncAzureOpenAI client.\n"
            "[Source: src/agents/containers/co_pilot_app.py]"
        ),
        "status": "implemented",
        "type": "requirement",
    },
]

for spec in specs:
    kdb.insert_spec(
        id=spec["id"],
        title=spec["title"],
        description=spec["description"],
        status=spec["status"],
        type=spec["type"],
        changed_by="claude",
        change_reason="S182: Agent containerization (Builds 4-5)",
    )
    print(f"  Created {spec['id']}: {spec['title']}")

# ---------------------------------------------------------------------------
# Work Items
# ---------------------------------------------------------------------------

work_items = [
    {
        "id": "WI-1292",
        "title": "Deploy 7 agent containers to staging",
        "spec_id": "SPEC-1794",
        "status": "resolved",
        "origin": "new",
        "component": "infrastructure",
    },
    {
        "id": "WI-1293",
        "title": "Add gateway-compatible path aliases to agent_app.py",
        "spec_id": "SPEC-1795",
        "status": "resolved",
        "origin": "new",
        "component": "agents",
    },
    {
        "id": "WI-1294",
        "title": "Add co-pilot and critic-supervisor to AGENT_URLS",
        "spec_id": "SPEC-1796",
        "status": "resolved",
        "origin": "new",
        "component": "pipeline",
    },
    {
        "id": "WI-1295",
        "title": "Create co-pilot container entry point",
        "spec_id": "SPEC-1797",
        "status": "resolved",
        "origin": "new",
        "component": "agents",
    },
]

for wi in work_items:
    kdb.insert_work_item(
        id=wi["id"],
        title=wi["title"],
        source_spec_id=wi["spec_id"],
        resolution_status=wi["status"],
        origin=wi["origin"],
        component=wi["component"],
        changed_by="claude",
        change_reason="S182: Agent containerization (Builds 4-5)",
    )
    print(f"  Created {wi['id']}: {wi['title']}")

# ---------------------------------------------------------------------------
# Test Artifacts
# ---------------------------------------------------------------------------

test_file = "tests/integration/test_agent_containers.py"
test_id_start = 10332

tests = [
    # TestContainerEntryPoints (14 tests = 7 modules x 2 tests)
    ("test_entry_point_importable[intent_classifier_app]", "SPEC-1794", "Entry point importable: intent-classifier"),
    (
        "test_entry_point_importable[knowledge_retrieval_app]",
        "SPEC-1794",
        "Entry point importable: knowledge-retrieval",
    ),
    ("test_entry_point_importable[response_generator_app]", "SPEC-1794", "Entry point importable: response-generator"),
    ("test_entry_point_importable[escalation_handler_app]", "SPEC-1794", "Entry point importable: escalation-handler"),
    (
        "test_entry_point_importable[analytics_collector_app]",
        "SPEC-1794",
        "Entry point importable: analytics-collector",
    ),
    ("test_entry_point_importable[critic_supervisor_app]", "SPEC-1794", "Entry point importable: critic-supervisor"),
    ("test_entry_point_importable[co_pilot_app]", "SPEC-1797", "Entry point importable: co-pilot"),
    ("test_entry_point_has_fastapi_app[intent_classifier_app]", "SPEC-1794", "FastAPI app: intent-classifier"),
    ("test_entry_point_has_fastapi_app[knowledge_retrieval_app]", "SPEC-1794", "FastAPI app: knowledge-retrieval"),
    ("test_entry_point_has_fastapi_app[response_generator_app]", "SPEC-1794", "FastAPI app: response-generator"),
    ("test_entry_point_has_fastapi_app[escalation_handler_app]", "SPEC-1794", "FastAPI app: escalation-handler"),
    ("test_entry_point_has_fastapi_app[analytics_collector_app]", "SPEC-1794", "FastAPI app: analytics-collector"),
    ("test_entry_point_has_fastapi_app[critic_supervisor_app]", "SPEC-1794", "FastAPI app: critic-supervisor"),
    ("test_entry_point_has_fastapi_app[co_pilot_app]", "SPEC-1797", "FastAPI app: co-pilot"),
    # TestGatewayPathAliases (7 tests)
    ("test_gateway_path_registered[intent_classifier_app]", "SPEC-1795", "Path alias /classify: intent-classifier"),
    ("test_gateway_path_registered[knowledge_retrieval_app]", "SPEC-1795", "Path alias /retrieve: knowledge-retrieval"),
    ("test_gateway_path_registered[response_generator_app]", "SPEC-1795", "Path alias /generate: response-generator"),
    ("test_gateway_path_registered[escalation_handler_app]", "SPEC-1795", "Path alias /escalate: escalation-handler"),
    ("test_gateway_path_registered[analytics_collector_app]", "SPEC-1795", "Path alias /collect: analytics-collector"),
    ("test_gateway_path_registered[critic_supervisor_app]", "SPEC-1795", "Path alias /validate: critic-supervisor"),
    ("test_gateway_path_registered[co_pilot_app]", "SPEC-1795", "Path alias /process: co-pilot"),
    # TestResponseGeneratorStreaming (1 test)
    ("test_generate_stream_route_exists", "SPEC-1795", "RG exposes /generate/stream"),
    # TestAgentAppFactory (4 tests)
    ("test_health_endpoint_exists", "SPEC-1794", "Container /health endpoint"),
    ("test_ready_endpoint_exists", "SPEC-1794", "Container /ready endpoint"),
    ("test_a2a_process_endpoint_exists", "SPEC-1794", "Container /agents/{type}/process endpoint"),
    ("test_agent_stored_in_app_state", "SPEC-1794", "Agent stored in app.state"),
    # TestCoPilotContainerConfig (2 tests)
    ("test_co_pilot_agent_type", "SPEC-1797", "Co-pilot agent type correct"),
    ("test_co_pilot_has_configure_fn", "SPEC-1797", "Co-pilot has configure function"),
    # TestAgentURLConfiguration (2 tests)
    ("test_all_agents_in_urls", "SPEC-1796", "AGENT_URLS covers all 7 agents"),
    ("test_agent_urls_have_env_overrides", "SPEC-1796", "Agent URLs are HTTP and non-empty"),
    # TestAgentPathConstants (6 tests)
    ("test_classify_path", "SPEC-1795", "AGENT_CLASSIFY_PATH = /classify"),
    ("test_retrieve_path", "SPEC-1795", "AGENT_RETRIEVE_PATH = /retrieve"),
    ("test_generate_path", "SPEC-1795", "AGENT_GENERATE_PATH = /generate"),
    ("test_generate_stream_path", "SPEC-1795", "AGENT_GENERATE_STREAM_PATH = /generate/stream"),
    ("test_escalate_path", "SPEC-1795", "AGENT_ESCALATE_PATH = /escalate"),
    ("test_collect_path", "SPEC-1795", "AGENT_ANALYTICS_PATH = /collect"),
    # TestDeployScript (2 tests)
    ("test_deploy_script_defines_all_agents", "SPEC-1794", "Deploy script covers all agents"),
    ("test_deploy_script_module_paths_match_containers", "SPEC-1794", "Deploy script module paths importable"),
    # TestVersionBump (1 test)
    ("test_product_version", "SPEC-1794", "Product version 1.85.0"),
]

for i, (test_func, spec_id, title) in enumerate(tests):
    test_id = f"TEST-{test_id_start + i}"
    kdb.insert_test(
        id=test_id,
        title=title,
        spec_id=spec_id,
        test_type="behavioral",
        expected_outcome="pass",
        test_file=test_file,
        test_function=test_func,
        changed_by="claude",
        change_reason="S182: Agent containerization (Builds 4-5)",
    )

print(f"  Created {len(tests)} test artifacts (TEST-{test_id_start}..TEST-{test_id_start + len(tests) - 1})")

kdb.close()
print("\nDone. 4 specs, 4 WIs, 39 test artifacts recorded.")
