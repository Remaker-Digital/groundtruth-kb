"""Module-level singleton for ChatPipeline.

Provides get_chat_pipeline(), configure_chat_pipeline(), and
_create_openai_client() for application lifecycle management.

R10 refactoring — extracted from pipeline.py (session 39).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from src.chat.pipeline.constants import USE_AGENT_CONTAINERS
from src.chat.pipeline.orchestrator import ChatPipeline
from src.chat.session import ConversationSession
from src.multi_tenant.conversation_meter import ConversationMeter
from src.multi_tenant.conversation_vectorizer import ConversationVectorizer
from src.multi_tenant.critic_policy import CriticPolicy
from src.multi_tenant.customer_profile_service import CustomerProfileService
from src.multi_tenant.system_prompt_builder import SystemPromptBuilder

# Azure OpenAI direct integration (WI #207)
try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

_pipeline: ChatPipeline | None = None


def _create_openai_client() -> Any:
    """Create an AsyncAzureOpenAI client from environment variables.

    Returns None if credentials are not configured (development mode).
    """
    if AsyncAzureOpenAI is None:
        logger.warning("openai package not installed — direct Azure OpenAI calls disabled")
        return None

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")

    if not endpoint or not api_key:
        logger.warning(
            "AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY not set — "
            "direct Azure OpenAI calls disabled"
        )
        return None

    return AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-10-21",
    )


def get_chat_pipeline() -> ChatPipeline:
    """Get the module-level ChatPipeline singleton.

    Returns a pipeline with default dependencies. For testing, use
    ChatPipeline() directly with injected mocks.
    """
    global _pipeline
    if _pipeline is None:
        from src.multi_tenant.customer_profile_service import get_profile_service
        from src.multi_tenant.system_prompt_builder import get_prompt_builder

        from src.chat.session import get_conversation_session

        _pipeline = ChatPipeline(
            session=get_conversation_session(),
            prompt_builder=get_prompt_builder(),
            profile_service=get_profile_service(),
            openai_client=_create_openai_client(),
        )
    return _pipeline


def configure_chat_pipeline(
    session: ConversationSession,
    prompt_builder: SystemPromptBuilder,
    profile_service: CustomerProfileService,
    vectorizer: ConversationVectorizer | None = None,
    critic: CriticPolicy | None = None,
    meter: ConversationMeter | None = None,
    agent_urls: dict[str, str] | None = None,
    openai_client: Any | None = None,
    kb_repo: Any | None = None,
) -> ChatPipeline:
    """Configure the module-level singleton with explicit dependencies.

    Called during app startup (main.py) after all services are initialized.

    When openai_client is not provided, a default AsyncAzureOpenAI client
    is created from environment variables. The client is needed for both
    direct mode and as a fallback when HTTP container calls fail.
    """
    if openai_client is None:
        openai_client = _create_openai_client()

    global _pipeline
    _pipeline = ChatPipeline(
        session=session,
        prompt_builder=prompt_builder,
        profile_service=profile_service,
        vectorizer=vectorizer,
        critic=critic,
        meter=meter,
        agent_urls=agent_urls,
        openai_client=openai_client,
        kb_repo=kb_repo,
    )
    return _pipeline
