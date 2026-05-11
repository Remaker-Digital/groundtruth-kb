# Agent Red — Generic Agent Container Dockerfile
#
# Builds a container image for any of the 7 pipeline agents.
# The AGENT_MODULE build arg selects which agent to run.
#
# Build examples:
#   docker build --build-arg AGENT_MODULE=intent_classifier_app -t agent-intent-classifier .
#   docker build --build-arg AGENT_MODULE=knowledge_retrieval_app -t agent-knowledge-retrieval .
#   docker build --build-arg AGENT_MODULE=response_generator_app -t agent-response-generator .
#   docker build --build-arg AGENT_MODULE=escalation_handler_app -t agent-escalation-handler .
#   docker build --build-arg AGENT_MODULE=analytics_collector_app -t agent-analytics-collector .
#   docker build --build-arg AGENT_MODULE=critic_supervisor_app -t agent-critic-supervisor .
#   docker build --build-arg AGENT_MODULE=co_pilot_app -t agent-co-pilot .
#
# Run:
#   docker run -e AZURE_OPENAI_ENDPOINT=... -e AZURE_OPENAI_API_KEY=... \
#     -e AGNTCY_NATS_ENDPOINT=nats://nats:4222 \
#     -p 8081:8080 agent-intent-classifier
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

FROM python:3.12-slim

# Build arg: which agent module to run
ARG AGENT_MODULE=intent_classifier_app

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/

# Environment defaults
ENV AGENT_MODULE=${AGENT_MODULE}
ENV PORT=8080
ENV LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the agent
EXPOSE ${PORT}
CMD uvicorn src.agents.containers.${AGENT_MODULE}:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --log-level ${LOG_LEVEL}
