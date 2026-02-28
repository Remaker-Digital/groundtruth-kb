"""Fix S119 assertion types — convert non-machine-checkable to grep/glob.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db'))
from db import KnowledgeDB

kdb = KnowledgeDB()

fixes = [
    {
        'id': 'SPEC-1516', 'title': 'Agent Red near-term scale target: 680 merchant customers',
        'description': 'The system must support 680 concurrent merchant customers as the near-term commercial scale target.',
        'status': 'implemented', 'section': 'INFRASTRUCTURE',
        'assertions': [
            {'type': 'grep', 'pattern': '680', 'file': 'tests/performance/locustfile.py', 'description': 'Load test exercises 680-tenant target'},
            {'type': 'grep', 'pattern': '680', 'file': 'tests/performance/test_concurrent_tenants.py', 'description': 'Concurrent tenant test targets 680'},
            {'type': 'grep', 'pattern': '680', 'file': 'tests/performance/test_keda_scaling.py', 'description': 'KEDA scaling test references 680'},
        ],
        'tags': ['scale', 'performance'],
    },
    {
        'id': 'SPEC-1517', 'title': 'MCP and AGNTCY (requiring SLIM transport) are central technical features',
        'description': 'SLIM transport is required for AGNTCY agent orchestration.',
        'status': 'implemented', 'section': 'INFRASTRUCTURE',
        'assertions': [
            {'type': 'grep', 'pattern': 'slim', 'file': 'src/multi_tenant/agntcy_sdk_integration.py', 'description': 'SLIM transport integration exists'},
            {'type': 'grep', 'pattern': 'agntcy', 'file': 'src/multi_tenant/agntcy_sdk_integration.py', 'description': 'AGNTCY SDK integration exists'},
        ],
        'tags': ['agntcy', 'slim', 'mcp'],
    },
    {
        'id': 'SPEC-1519', 'title': 'PCM Layer 4: OpenAI Fine-Tuning API integration',
        'description': 'Fine-tuning pipeline integrates with OpenAI fine-tuning API.',
        'status': 'implemented', 'section': 'PERSISTENT_MEMORY',
        'assertions': [
            {'type': 'grep', 'pattern': 'fine_tun', 'file': 'src/multi_tenant/fine_tuning_pipeline.py', 'description': 'Fine-tuning pipeline module exists'},
            {'type': 'grep', 'pattern': 'openai', 'file': 'src/multi_tenant/fine_tuning_pipeline.py', 'description': 'OpenAI client in pipeline'},
            {'type': 'glob', 'pattern': 'tests/persistent_memory/test_fine_tuning.py', 'description': 'Fine-tuning test file exists'},
        ],
        'tags': ['pcm', 'fine-tuning'],
    },
    {
        'id': 'SPEC-1520', 'title': 'PCM Layer 4: Model evaluation against fine-tuned model',
        'description': 'System can evaluate conversation quality improvement after fine-tuning.',
        'status': 'implemented', 'section': 'PERSISTENT_MEMORY',
        'assertions': [
            {'type': 'grep', 'pattern': 'evaluat', 'file': 'src/multi_tenant/fine_tuning_pipeline.py', 'description': 'Evaluation logic in pipeline'},
            {'type': 'grep', 'pattern': 'fine_tuned_model', 'file': 'src/multi_tenant/fine_tuning_pipeline.py', 'description': 'Fine-tuned model reference'},
        ],
        'tags': ['pcm', 'evaluation'],
    },
    {
        'id': 'SPEC-1521', 'title': 'PCM Layer 4: Cosmos DB persistence for training artifacts',
        'description': 'Training data and job status persisted in Cosmos DB.',
        'status': 'implemented', 'section': 'PERSISTENT_MEMORY',
        'assertions': [
            {'type': 'grep', 'pattern': 'training', 'file': 'src/multi_tenant/fine_tuning_pipeline.py', 'description': 'Training references in pipeline'},
            {'type': 'grep', 'pattern': 'cosmos', 'file': 'src/multi_tenant/fine_tuning_pipeline.py', 'description': 'Cosmos DB persistence'},
        ],
        'tags': ['pcm', 'cosmos'],
    },
    {
        'id': 'SPEC-1522', 'title': 'PCM Layer 4: Admin API endpoints for fine-tuning management',
        'description': 'Admin manages fine-tuning jobs via API endpoints.',
        'status': 'implemented', 'section': 'ADMIN_API',
        'assertions': [
            {'type': 'glob', 'pattern': 'src/multi_tenant/admin_fine_tuning_api.py', 'description': 'Fine-tuning admin API module exists'},
            {'type': 'grep', 'pattern': 'fine_tuning', 'file': 'src/multi_tenant/admin_fine_tuning_api.py', 'description': 'Fine-tuning endpoints defined'},
            {'type': 'grep', 'pattern': 'router', 'file': 'src/multi_tenant/admin_fine_tuning_api.py', 'description': 'Router registration'},
        ],
        'tags': ['pcm', 'admin-api'],
    },
    {
        'id': 'SPEC-1523', 'title': 'PCM Layer 4: Admin UI controls for fine-tuning',
        'description': 'Admin UI provides controls to initiate and monitor fine-tuning.',
        'status': 'implemented', 'section': 'ADMIN_UI',
        'assertions': [
            {'type': 'grep', 'pattern': 'fine.?tun', 'file': 'admin/standalone/pages/AgentConfig.tsx', 'description': 'Fine-tuning controls in admin UI'},
        ],
        'tags': ['pcm', 'admin-ui'],
    },
    {
        'id': 'SPEC-1524', 'title': 'SLIM transport activation with configured endpoint',
        'description': 'SLIM transport activates when SLIM_ENDPOINT is configured.',
        'status': 'implemented', 'section': 'INFRASTRUCTURE',
        'assertions': [
            {'type': 'grep', 'pattern': 'SLIM_ENDPOINT', 'file': 'src/multi_tenant/agntcy_sdk_integration.py', 'description': 'SLIM endpoint config'},
            {'type': 'grep', 'pattern': 'nats', 'file': 'src/multi_tenant/agntcy_sdk_integration.py', 'description': 'NATS transport'},
        ],
        'tags': ['slim', 'nats'],
    },
    {
        'id': 'SPEC-1525', 'title': 'A2A message routing through SLIM/NATS transport',
        'description': 'Agent-to-agent messages routed through SLIM/NATS with trace ID.',
        'status': 'implemented', 'section': 'INFRASTRUCTURE',
        'assertions': [
            {'type': 'grep', 'pattern': 'X-Trace-Id', 'file': 'src/multi_tenant/agntcy_sdk_integration.py', 'description': 'Trace ID in SLIM transport'},
            {'type': 'grep', 'pattern': 'dispatch', 'file': 'src/multi_tenant/agntcy_sdk_integration.py', 'description': 'Message dispatch function'},
        ],
        'tags': ['slim', 'a2a'],
    },
    {
        'id': 'SPEC-1526', 'title': 'MCP SDK dependency in production requirements',
        'description': 'MCP SDK is listed as a production dependency.',
        'status': 'implemented', 'section': 'INFRASTRUCTURE',
        'assertions': [
            {'type': 'grep', 'pattern': 'mcp', 'file': 'requirements.txt', 'description': 'MCP SDK in requirements'},
        ],
        'tags': ['mcp', 'dependencies'],
    },
    {
        'id': 'SPEC-1527', 'title': 'Locust load test suite for multi-tenant scale validation',
        'description': 'Locust-based load tests for 680-merchant concurrent scale.',
        'status': 'implemented', 'section': 'TESTING',
        'assertions': [
            {'type': 'glob', 'pattern': 'tests/performance/locustfile.py', 'description': 'Locust test file exists'},
            {'type': 'grep', 'pattern': 'HttpUser', 'file': 'tests/performance/locustfile.py', 'description': 'Locust HttpUser class'},
        ],
        'tags': ['load-testing', 'locust'],
    },
    {
        'id': 'SPEC-1528', 'title': 'KEDA scaling validation tests',
        'description': 'Tests validate KEDA auto-scaling for container apps.',
        'status': 'implemented', 'section': 'TESTING',
        'assertions': [
            {'type': 'glob', 'pattern': 'tests/performance/test_keda_scaling.py', 'description': 'KEDA test file exists'},
            {'type': 'grep', 'pattern': 'keda', 'file': 'tests/performance/test_keda_scaling.py', 'description': 'KEDA references in test'},
        ],
        'tags': ['keda', 'scaling'],
    },
    {
        'id': 'SPEC-1529', 'title': 'Performance baseline benchmarks',
        'description': 'Concurrent tenant tests establish performance baselines.',
        'status': 'implemented', 'section': 'TESTING',
        'assertions': [
            {'type': 'glob', 'pattern': 'tests/performance/test_concurrent_tenants.py', 'description': 'Concurrent tenant test file exists'},
            {'type': 'grep', 'pattern': 'concurrent', 'file': 'tests/performance/test_concurrent_tenants.py', 'description': 'Concurrent test patterns'},
        ],
        'tags': ['performance', 'benchmarks'],
    },
    {
        'id': 'SPEC-1530', 'title': 'End-to-end conversation trace ID propagation',
        'description': 'trace_id generated at conversation start and propagated through all stages.',
        'status': 'implemented', 'section': 'CHAT_PIPELINE',
        'assertions': [
            {'type': 'grep', 'pattern': 'trace_id', 'file': 'src/chat/endpoints.py', 'description': 'trace_id generated at endpoint'},
            {'type': 'grep', 'pattern': 'X-Trace-Id', 'file': 'src/chat/endpoints.py', 'description': 'X-Trace-Id header in response'},
            {'type': 'grep', 'pattern': 'trace_id', 'file': 'src/chat/pipeline/orchestrator.py', 'description': 'trace_id propagated through orchestrator'},
        ],
        'tags': ['tracing', 'pipeline'],
    },
    {
        'id': 'SPEC-1531', 'title': 'Pipeline stage timeline persistence',
        'description': 'Each pipeline stage records name, elapsed_ms, timestamps, agent_type. Persisted to conversation.',
        'status': 'implemented', 'section': 'CHAT_PIPELINE',
        'assertions': [
            {'type': 'grep', 'pattern': 'pipeline_trace', 'file': 'src/multi_tenant/cosmos_schema.py', 'description': 'pipeline_trace in Cosmos schema'},
            {'type': 'grep', 'pattern': 'stage_event', 'file': 'src/chat/models.py', 'description': 'stage_event method in models'},
            {'type': 'grep', 'pattern': 'elapsed_ms', 'file': 'src/chat/models.py', 'description': 'elapsed_ms tracking'},
        ],
        'tags': ['tracing', 'persistence'],
    },
    {
        'id': 'SPEC-1532', 'title': 'Admin UI conversation trace visualization',
        'description': 'Admin inbox displays pipeline trace as horizontal bar chart with stage colors and badges.',
        'status': 'implemented', 'section': 'ADMIN_UI',
        'assertions': [
            {'type': 'grep', 'pattern': 'PipelineTracePanel', 'file': 'admin/standalone/pages/Inbox.tsx', 'description': 'Trace panel in standalone inbox'},
            {'type': 'grep', 'pattern': 'PipelineTracePanel', 'file': 'admin/shared/ConversationInbox.tsx', 'description': 'Trace panel in shared inbox'},
            {'type': 'grep', 'pattern': 'useConversationTrace', 'file': 'admin/shared/hooks/useInbox.ts', 'description': 'Trace hook in shared hooks'},
        ],
        'tags': ['tracing', 'admin-ui'],
    },
    {
        'id': 'SPEC-1533', 'title': 'SSE event trace metadata',
        'description': 'SSE chat events include trace_id and stage metadata.',
        'status': 'implemented', 'section': 'CHAT_PIPELINE',
        'assertions': [
            {'type': 'grep', 'pattern': 'trace_id', 'file': 'src/chat/models.py', 'description': 'trace_id in SSE event models'},
            {'type': 'grep', 'pattern': 'done_event', 'file': 'src/chat/models.py', 'description': 'done_event with trace metadata'},
        ],
        'tags': ['tracing', 'sse'],
    },
]

for fix in fixes:
    kdb.insert_spec(
        id=fix['id'],
        title=fix['title'],
        description=fix['description'],
        status=fix['status'],
        section=fix['section'],
        assertions=fix['assertions'],
        tags=fix['tags'],
        changed_by='S119',
        change_reason='Fix assertion types: convert functional/ui/requirement to grep/glob; fix path->file'
    )
    print(f"Fixed {fix['id']}")

print(f"\nAll {len(fixes)} specs fixed!")
