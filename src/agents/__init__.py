# Agent Red Customer Experience — Containerized Agent Package
#
# This package contains the 6 AGNTCY-compatible agent implementations,
# decomposed from the monolithic pipeline.py. Each agent:
#   - Implements BaseAgentProtocol.handle_message(Message) → Message
#   - Is independently deployable as a container
#   - Communicates via A2A protocol over NATS/SLIM transport
#
# Agent modules:
#   from src.agents.intent_classifier import IntentClassifierAgent
#   from src.agents.knowledge_retrieval import KnowledgeRetrievalAgent
#   from src.agents.response_generator import ResponseGeneratorAgent
#   from src.agents.escalation_handler import EscalationHandlerAgent
#   from src.agents.analytics_collector import AnalyticsCollectorAgent
#   from src.agents.critic_supervisor import CriticSupervisorAgent
#
# Base class:
#   from src.agents.base import AgentRedBaseAgent
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
