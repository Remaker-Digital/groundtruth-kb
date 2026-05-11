# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Pipeline package — 6-agent pipeline orchestrator for the Chat API.

Barrel re-export preserving the original ``from src.chat.pipeline import ...``
import paths. All public symbols that were previously in the monolithic
``pipeline.py`` module are re-exported here.

R10 refactoring — session 39.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from src.chat.pipeline.constants import (
    AGENT_ANALYTICS_PATH,
    AGENT_CLASSIFY_PATH,
    AGENT_ESCALATE_PATH,
    AGENT_GENERATE_PATH,
    AGENT_GENERATE_STREAM_PATH,
    AGENT_RETRIEVE_PATH,
    AGENT_URLS,
    AZURE_CR_MODEL,
    AZURE_EMBEDDING_DIMENSIONS,
    AZURE_EMBEDDING_MODEL,
    AZURE_IC_MODEL,
    AZURE_RG_MODEL,
    ESCALATION_INTENT,
    INTENT_TAXONOMY,
    USE_AGENT_CONTAINERS,
    _classify_openai_error,
)
from src.chat.pipeline.orchestrator import ChatPipeline
from src.chat.pipeline.singleton import (
    _create_openai_client,
    configure_chat_pipeline,
    get_chat_pipeline,
)

# Re-export names that tests patch at the pipeline module level.
# These are imported into the orchestrator and need to resolve here too
# for backward compatibility with @patch("src.chat.pipeline.X") targets.
from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget
from src.multi_tenant.response_explainability import DecisionTraceBuilder

__all__ = [
    # Orchestrator
    "ChatPipeline",
    # Singleton management
    "get_chat_pipeline",
    "configure_chat_pipeline",
    "_create_openai_client",
    # Constants
    "USE_AGENT_CONTAINERS",
    "AGENT_URLS",
    "AGENT_CLASSIFY_PATH",
    "AGENT_RETRIEVE_PATH",
    "AGENT_GENERATE_PATH",
    "AGENT_GENERATE_STREAM_PATH",
    "AGENT_ESCALATE_PATH",
    "AGENT_ANALYTICS_PATH",
    "ESCALATION_INTENT",
    "AZURE_IC_MODEL",
    "AZURE_RG_MODEL",
    "AZURE_CR_MODEL",
    "AZURE_EMBEDDING_MODEL",
    "AZURE_EMBEDDING_DIMENSIONS",
    "INTENT_TAXONOMY",
    "_classify_openai_error",
    # Re-exported for backward-compatible @patch targets
    "PipelineTimeoutBudget",
    "DecisionTraceBuilder",
]
