# Agent Red — Knowledge Retrieval Container Entry Point
#
# Run: uvicorn src.agents.containers.knowledge_retrieval_app:app --port 8082
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

from src.agents.containers.agent_app import create_agent_app
from src.agents.knowledge_retrieval import KnowledgeRetrievalAgent


async def _configure(agent: KnowledgeRetrievalAgent) -> None:
    """Inject KB repository and vectorizer."""
    try:
        from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer
        vectorizer = get_knowledge_vectorizer()
        agent.configure(knowledge_vectorizer=vectorizer)
    except Exception:
        pass  # Will use keyword fallback


app = create_agent_app(KnowledgeRetrievalAgent, configure_fn=_configure)
