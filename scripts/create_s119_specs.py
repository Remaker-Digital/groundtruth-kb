#!/usr/bin/env python3
"""Create specifications for S119 cycle: PCM Layer 4, AGNTCY/SLIM, Scale Testing, Conversation Tracing."""
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB

kdb = KnowledgeDB()

CHANGE_REASON = "S119 cycle: PCM Layer 4 + AGNTCY/SLIM + Scale Testing + Conversation Tracing"

specs = [
    # === PCM LAYER 4 ===
    {
        "id": "SPEC-1519",
        "title": "PCM Layer 4: OpenAI Fine-Tuning API integration",
        "description": (
            "The fine-tuning pipeline MUST connect to the Azure OpenAI Fine-Tuning API for model training. "
            "_call_fine_tuning_api() MUST upload JSONL training data via the Files API, create a fine-tuning job, "
            "and return the job ID. _check_job_status_api() MUST poll for job status and return "
            "status (queued/running/succeeded/failed). Rate limiting and retries MUST be handled."
        ),
        "status": "specified",
        "section": "MEMORY",
        "assertions": [
            {"description": "fine_tuning_pipeline._call_fine_tuning_api does not raise NotImplementedError", "type": "functional"},
            {"description": "fine_tuning_pipeline._check_job_status_api does not raise NotImplementedError", "type": "functional"},
            {"description": "Training data is uploaded as JSONL file before job creation", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1520",
        "title": "PCM Layer 4: Model evaluation against fine-tuned model",
        "description": (
            "The quality gate evaluation stage MUST call the actual fine-tuned model via Azure OpenAI API, "
            "not return hardcoded placeholder responses. _call_model_for_evaluation() MUST accept a model_id "
            "and messages list, call the Azure OpenAI chat completions endpoint, and return the model response."
        ),
        "status": "specified",
        "section": "MEMORY",
        "assertions": [
            {"description": "_call_model_for_evaluation returns actual model output, not hardcoded string", "type": "functional"},
            {"description": "Quality gates score against real model responses", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1521",
        "title": "PCM Layer 4: Cosmos DB persistence for training artifacts",
        "description": (
            "Fine-tuning models, training jobs, and A/B experiments MUST be persisted to Cosmos DB, "
            "not in-memory dev stores. TrainingJobRecord and FineTunedModelRecord MUST use "
            "TenantScopedRepository pattern with /tenant_id partition key."
        ),
        "status": "specified",
        "section": "MEMORY",
        "assertions": [
            {"description": "TrainingJobRecord persisted to Cosmos DB fine_tuning_jobs container", "type": "functional"},
            {"description": "FineTunedModelRecord persisted to Cosmos DB fine_tuned_models container", "type": "functional"},
            {"description": "In-memory dev stores not used in production mode", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1522",
        "title": "PCM Layer 4: Admin API endpoints for fine-tuning management",
        "description": (
            "The admin API MUST expose: POST /api/admin/fine-tuning/trigger (start pipeline), "
            "GET /api/admin/fine-tuning/status (job status + model history), "
            "GET /api/admin/fine-tuning/experiments (A/B experiments), "
            "POST /api/admin/fine-tuning/rollback (rollback). Enterprise tier required."
        ),
        "status": "specified",
        "section": "ADMIN_UI",
        "assertions": [
            {"description": "POST /api/admin/fine-tuning/trigger returns 200 with job_id", "type": "functional"},
            {"description": "GET /api/admin/fine-tuning/status returns model history and job status", "type": "functional"},
            {"description": "POST /api/admin/fine-tuning/rollback reverts to specified model version", "type": "functional"},
            {"description": "Non-Enterprise tier receives 403 Forbidden", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1523",
        "title": "PCM Layer 4: Admin UI controls for fine-tuning",
        "description": (
            "The Memory & Privacy admin page MUST include interactive controls for Layer 4: "
            "enable/disable toggle (Enterprise gated), schedule picker (monthly/weekly/trigger), "
            "min conversation threshold, trigger training button, model version history, "
            "A/B experiment status, and rollback controls."
        ),
        "status": "specified",
        "section": "ADMIN_UI",
        "assertions": [
            {"description": "MemoryPrivacy page renders fine-tuning enable/disable toggle for Enterprise", "type": "ui"},
            {"description": "MemoryPrivacy page renders schedule picker with 3 options", "type": "ui"},
            {"description": "Non-Enterprise users see upgrade prompt instead of controls", "type": "ui"},
        ],
    },
    # === AGNTCY/MCP/SLIM ===
    {
        "id": "SPEC-1524",
        "title": "SLIM transport activation with configured endpoint",
        "description": (
            "When AGNTCY_SLIM_ENDPOINT is configured, the system MUST establish a SLIM transport connection "
            "at startup. SLIM MUST be used for inter-agent A2A communication. Falls back to NATS then HTTP. "
            "Health status MUST report SLIM connection state."
        ),
        "status": "specified",
        "section": "INFRASTRUCTURE",
        "assertions": [
            {"description": "SLIM transport connects when AGNTCY_SLIM_ENDPOINT is configured", "type": "functional"},
            {"description": "System falls back to NATS when SLIM is unavailable", "type": "functional"},
            {"description": "Health endpoint reports SLIM connection status", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1525",
        "title": "A2A message routing through SLIM/NATS transport",
        "description": (
            "The chat pipeline MUST route agent-to-agent messages through configured transport "
            "(SLIM or NATS) instead of in-process calls when transport is available. "
            "Messages MUST include tenant_id, conversation_id, and trace_id in headers."
        ),
        "status": "specified",
        "section": "INFRASTRUCTURE",
        "assertions": [
            {"description": "Pipeline routes messages via SLIM transport when configured", "type": "functional"},
            {"description": "All A2A messages include X-Tenant-Id, X-Conversation-Id, X-Trace-Id headers", "type": "functional"},
            {"description": "Agent responses use reply_to routing", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1526",
        "title": "MCP SDK dependency in production requirements",
        "description": "The mcp Python SDK MUST be listed in requirements.txt as a production dependency.",
        "status": "specified",
        "section": "INFRASTRUCTURE",
        "assertions": [
            {"description": "requirements.txt includes mcp package dependency", "type": "functional"},
        ],
    },
    # === LARGE SCALE TESTING ===
    {
        "id": "SPEC-1527",
        "title": "Locust load test suite for multi-tenant scale validation",
        "description": (
            "A Locust-based load test suite MUST simulate concurrent tenant workloads: "
            "configurable tenant count (50-1000), variable message rates, SSE connections, "
            "and admin API calls. MUST report P50/P95/P99 latency and error rates."
        ),
        "status": "specified",
        "section": "TESTING",
        "assertions": [
            {"description": "Locust test file exists at tests/performance/locustfile.py", "type": "functional"},
            {"description": "Load test simulates configurable number of concurrent tenants", "type": "functional"},
            {"description": "Load test reports P50, P95, P99 latency percentiles", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1528",
        "title": "KEDA scaling validation tests",
        "description": (
            "Automated tests MUST verify KEDA auto-scaling: scale-up on NATS queue depth threshold, "
            "scale-down on reduced load, and scale-to-zero for non-critical services."
        ),
        "status": "specified",
        "section": "TESTING",
        "assertions": [
            {"description": "KEDA scaling test verifies scale-up on queue depth threshold", "type": "functional"},
            {"description": "KEDA scaling test verifies scale-down on reduced load", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1529",
        "title": "Performance baseline benchmarks",
        "description": (
            "Performance baselines MUST be established: single-tenant P95, 50-tenant concurrent P95, "
            "max sustainable RPS, cold-start latency, NATS throughput. Stored as test artifacts."
        ),
        "status": "specified",
        "section": "TESTING",
        "assertions": [
            {"description": "Performance baseline test measures single-tenant P95 latency", "type": "functional"},
            {"description": "Performance baseline test measures 50-tenant concurrent P95", "type": "functional"},
        ],
    },
    # === CONVERSATION TRACING ===
    {
        "id": "SPEC-1530",
        "title": "End-to-end conversation trace ID propagation",
        "description": (
            "Every conversation MUST be assigned a unique trace_id at the API Gateway entry point. "
            "The trace_id MUST propagate through all 6 pipeline agents via message headers, "
            "NATS correlation headers, and OpenTelemetry spans. Persisted on conversation document."
        ),
        "status": "specified",
        "section": "INFRASTRUCTURE",
        "assertions": [
            {"description": "Conversation document includes trace_id field", "type": "functional"},
            {"description": "All pipeline agent calls include X-Trace-Id header", "type": "functional"},
            {"description": "OpenTelemetry spans include trace_id attribute", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1531",
        "title": "Pipeline stage timeline persistence",
        "description": (
            "For each conversation message, a pipeline trace record MUST be created containing: "
            "ordered list of stages, per-stage latency (ms), success/failure, agent output summaries "
            "(intent, knowledge sources, critic verdict), retry info, total latency. "
            "Stored on conversation document and accessible via GET /api/admin/conversations/{id}/trace."
        ),
        "status": "specified",
        "section": "INFRASTRUCTURE",
        "assertions": [
            {"description": "Pipeline trace includes per-stage latency for all agents", "type": "functional"},
            {"description": "Pipeline trace includes agent output summaries", "type": "functional"},
            {"description": "Pipeline trace persisted on conversation document", "type": "functional"},
            {"description": "GET /api/admin/conversations/{id}/trace returns pipeline trace data", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1532",
        "title": "Admin UI conversation trace visualization",
        "description": (
            "The admin SPA Inbox page MUST display a visual pipeline trace for each conversation message: "
            "horizontal timeline of stages (IC->KR->RG->CR), per-stage latency bars, success/failure "
            "indicators, expandable detail per stage, total duration. Aggregate flow data MUST be "
            "visually representable for monitoring purposes."
        ),
        "status": "specified",
        "section": "ADMIN_UI",
        "assertions": [
            {"description": "Inbox conversation detail shows pipeline stage timeline", "type": "ui"},
            {"description": "Each pipeline stage shows latency bar and success/failure indicator", "type": "ui"},
            {"description": "Pipeline stages are expandable to show agent output details", "type": "ui"},
            {"description": "Total pipeline duration is displayed", "type": "ui"},
        ],
    },
    {
        "id": "SPEC-1533",
        "title": "SSE event trace metadata",
        "description": (
            "SSE stream events MUST include trace_id in the event payload. "
            "Stage events MUST include current pipeline stage name and elapsed time."
        ),
        "status": "specified",
        "section": "INFRASTRUCTURE",
        "assertions": [
            {"description": "SSE events include trace_id field in payload", "type": "functional"},
            {"description": "SSE stage events include stage name and elapsed_ms", "type": "functional"},
        ],
    },
]

created = 0
for spec in specs:
    assertions = spec.pop("assertions", [])
    try:
        kdb.insert_spec(
            id=spec["id"],
            title=spec["title"],
            description=spec["description"],
            status=spec["status"],
            section=spec.get("section", "INFRASTRUCTURE"),
            assertions=assertions,
            changed_by="claude",
            change_reason=CHANGE_REASON,
        )
        created += 1
        print(f"  OK {spec['id']}: {spec['title'][:60]}")
    except Exception as e:
        print(f"  FAIL {spec['id']}: {e}")

print(f"\nTotal: {created}/{len(specs)} specifications created")
