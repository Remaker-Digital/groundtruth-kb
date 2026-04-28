---
name: Transport hierarchy directive
description: Owner-defined transport priority for agent communication — SLIM required for internal, HTTP only for external
type: feedback
---

Owner directive (S188): MCP and SLIM are imperative for internal system communications. All agents must be independent containers. Transport hierarchy:

1. **SLIM** — REQUIRED for all internal inter-agent communication (MCP-native)
2. **NATS JetStream** — Fallback only when SLIM fails or is disabled for reasons outside our control
3. **HTTP** — Reserved for communication with external agents that do not support SLIM or NATS JetStream

HTTP-only mode for internal agents is a VIOLATION of PB-AGNTCY-001. The system must fail-loud, not silently degrade to HTTP for internal dispatch.

Specs: SPEC-1802 (transport priority), PB-AGNTCY-001 (enforcement), SPEC-1534 (AGNTCY mandatory)
