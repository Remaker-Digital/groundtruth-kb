# AGNTCY Platform Adoption — Verification Procedure

# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: —
# Last corrected: 2026-02-16 — 5 assertions corrected to match actual SDK API (AgntcyFactory, not BaseAgent/AgentFactory; factory.create_client("MCP"), not create_mcp_client(); transport manages connections, not ConnectionPool)

---

## Purpose

Periodic verification of Agent Red's completeness and quality as a consumer of the
AGNTCY multi-agent customer service platform
(https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service/wiki).

This procedure measures progress across 6 phases of platform realignment. Each
assertion is independently testable and scored PASS / FAIL / SKIP. The aggregate
score expresses adoption completeness as a percentage.

### Governing Principle

Adopt the AGNTCY platform (SDK + superior components) as Agent Red's foundation.
Keep Agent Red's commercial SaaS layer wherever it is equivalent or superior. No
customer/merchant-visible functional regression. No substantial cost regression.
Take the best of both.

### Retained from AGNTCY (adopted into Agent Red)

| Component | Rationale |
|-----------|-----------|
| `agntcy-app-sdk` (AgntcyFactory, protocols, transports) | Core SDK — mandatory |
| NATS/SLIM transport with mTLS | Agent isolation, independent scaling, fault containment |
| 6-agent containerized architecture with A2A protocol | Per-agent observability, independent deployment |
| MCP client framework (`factory.create_client("MCP", ...)`) | No Agent Red equivalent exists |
| UCP commerce protocol via MCP bindings | Enables universal commerce beyond Shopify |
| OpenTelemetry per-agent tracing with cost attribution | Per-agent cost breakdown and execution tree |
| PII tokenization at transport layer | Infrastructure-level enforcement vs. prompt-based |

### Retained from Agent Red (not replaced by AGNTCY)

| Component | Rationale |
|-----------|-----------|
| Chat widget (session mgmt, Shopify embedding) | Multi-tenant, production-tested, 172 UI assertions |
| Admin UI (10 pages, configuration management) | Purpose-built for merchant self-service SaaS |
| KB Content Management admin UI | In-browser article creation/editing, superior for merchants |
| Multi-tenant isolation (47 modules) | No AGNTCY equivalent |
| Save-Activate two-phase configuration (9 states) | No AGNTCY equivalent |
| 4-role auth + per-user API keys | No AGNTCY equivalent |
| Shopify app integration + Stripe billing | Commercial SaaS capabilities |
| 4-layer persistent customer memory | No AGNTCY equivalent |
| Tier-gated feature system | No AGNTCY equivalent |

### Omitted from AGNTCY (inferior to Agent Red)

| Component | Rationale |
|-----------|-----------|
| AGNTCY chat widget | Agent Red's widget is multi-tenant with Shopify embedding |
| Merchant Content Management CLI | Agent Red's admin UI is superior for merchant self-service |
| Operations Dashboard (Azure Workbooks) | Agent Red's admin dashboard is more comprehensive |
| KEDA auto-scaling profiles | Azure Container Apps native scaling is sufficient at current scale |

---

## Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `PROJECT_ROOT` | `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement` | |
| `PROD_URL` | `https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` | |
| `AGNTCY_WIKI` | `https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service/wiki` | Platform reference |
| `AGNTCY_REPO` | `https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service` | Public repo |
| `SDK_PACKAGE` | `agntcy-app-sdk` | PyPI package name |
| `SDK_MIN_VERSION` | `0.4.7` | Minimum SDK version (current release; provides A2A, MCP, SLIM) |
| `NATS_PORT` | `4222` | NATS client connection port |
| `NATS_MONITOR_PORT` | `8222` | NATS HTTP monitoring port |
| `ACR_LOGIN_SERVER` | `acragentredeastus.azurecr.io` | Container registry |
| `TENANT_ID` | `remaker-digital-001` | Test tenant |
| `WIDGET_KEY` | (from `.env.local` `PREVIEW_WIDGET_KEY`; rotates on every re-seed) | |
| `SUPERADMIN_KEY` | (from `.env.local` `SUPERADMIN_PREVIEW_API_KEY`; rotates on every re-seed) | |
| `EXPECTED_AGENTS` | `intent_classifier, knowledge_retrieval, response_generator, escalation_handler, analytics_collector, critic_supervisor` | The 6 AGNTCY agents |
| `EXPECTED_UNIT_TESTS_MIN` | `2646` | Must not regress from current count (updated session 37) |

---

## Preconditions

| # | Condition | Verification | On Fail |
|---|-----------|-------------|---------|
| PRE-1 | Python 3.12+ available | `python --version` | Install Python |
| PRE-2 | pytest installed | `python -m pytest --version` | `pip install pytest` |
| PRE-3 | Working directory is PROJECT_ROOT | `cd $PROJECT_ROOT` | Navigate to project |
| PRE-4 | AGNTCY SDK installed | `python -c "from agntcy_app_sdk.factory import AgntcyFactory; print('OK')"` | `pip install $SDK_PACKAGE>=$SDK_MIN_VERSION` |
| PRE-5 | Production endpoint reachable | `curl $PROD_URL/health` → 200 | Check Azure Container Apps |
| PRE-6 | NATS reachable (if Phase 1+ complete) | `curl http://localhost:$NATS_MONITOR_PORT/varz` → 200 | Start NATS |
| PRE-7 | Docker available (if Phase 2+ complete) | `docker info` | Start Docker |
| PRE-8 | Unit test suite passing | `python -m pytest tests/ -x -q --tb=short` → 0 failures | Fix tests before proceeding |

---

## Phase 1: SDK Adoption + SLIM Transport

**Goal:** `agntcy-app-sdk` is actively imported and used (not just declared). NATS/SLIM
transport is operational between components with mTLS.

**AGNTCY wiki reference:** Architecture, Overview (SDK framework, SLIM transport)

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 1.1 | `agntcy-app-sdk` is in `requirements.txt` | `grep agntcy-app-sdk $PROJECT_ROOT/requirements.txt` | Line exists with version constraint |
| 1.2 | SDK is importable at runtime | `python -c "from agntcy_app_sdk.factory import AgntcyFactory, ProtocolTypes, TransportTypes; print('OK')"` | Prints "OK", exit code 0 |
| 1.3 | At least one `src/` module imports from `agntcy_app_sdk` | `grep -r "from agntcy_app_sdk\|import agntcy_app_sdk" $PROJECT_ROOT/src/ --include="*.py"` | At least 1 match (currently 0) |
| 1.4 | `AgntcyFactory` singleton is used for transport/client creation | Inspect agent initialization code for `AgntcyFactory` usage | Factory creates transports and protocol clients, not ad-hoc construction |
| 1.5 | Agent implementations use `BaseAgentProtocol`-compatible message handling | `grep -r "BaseAgentProtocol\|handle_message" $PROJECT_ROOT/src/ --include="*.py"` | Each agent implements `handle_message(Message) -> Message` per SDK protocol contract |
| 1.6 | NATS connection uses SLIM protocol | Inspect NATS client configuration for SLIM transport settings | SLIM configured, not raw NATS |
| 1.7 | mTLS is configured for agent-to-agent transport | Inspect NATS/SLIM TLS configuration | TLS 1.3 with mutual certificate authentication |
| 1.8 | SLIM health check passes | Dedicated health check endpoint or test for SLIM connectivity | Returns healthy status |
| 1.9 | Transport layer manages connections via SDK (`SLIMTransport` or `NatsTransport`) | Inspect transport initialization for SDK transport classes | SDK transport instances, not independent httpx/nats-py connections for agent communication |
| 1.10 | Unit tests pass after SDK adoption | `python -m pytest tests/ -x -q --tb=short` | >= $EXPECTED_UNIT_TESTS_MIN passed, 0 failed |

---

## Phase 2: Pipeline Decomposition — 6 Agent Containers via A2A

**Goal:** The monolithic `pipeline.py` is replaced by 6 containerized agents
communicating via the A2A protocol over NATS/SLIM. Each agent is independently
deployable, observable, and scalable.

**AGNTCY wiki reference:** Architecture (6 agents), Overview (agent descriptions)

### 2A: Agent Container Existence

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 2.1 | Intent Classification agent exists as a separate container image | `az acr repository show --name $ACR_NAME --image agent-intent-classifier` or `docker images` | Image exists in registry |
| 2.2 | Knowledge Retrieval agent exists as a separate container image | Same pattern | Image exists |
| 2.3 | Response Generation agent exists as a separate container image | Same pattern | Image exists |
| 2.4 | Escalation Handler agent exists as a separate container image | Same pattern | Image exists |
| 2.5 | Analytics Collector agent exists as a separate container image | Same pattern | Image exists |
| 2.6 | Critic/Supervisor agent exists as a separate container image | Same pattern | Image exists |

### 2B: A2A Communication

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 2.7 | Agents communicate via A2A protocol (not HTTP or in-process calls) | Inspect message flow between agents | Messages routed through NATS/SLIM with A2A envelope |
| 2.8 | Intent Classifier receives raw customer message and publishes classified intent | Send test message, observe NATS subject for classification output | Intent classification result published to correct NATS subject |
| 2.9 | Knowledge Retrieval subscribes to classified intents and publishes retrieval results | Observe NATS subjects | Retrieval results published after receiving intent |
| 2.10 | Response Generator subscribes to retrieval results and publishes draft response | Observe NATS subjects | Draft response published |
| 2.11 | Critic/Supervisor subscribes to draft responses and publishes validated/rejected result | Observe NATS subjects | Validation result published |
| 2.12 | Escalation Handler receives escalation-flagged messages | Send test message with escalation trigger (e.g., "refund request"), observe routing | Escalation handler receives and processes |
| 2.13 | Analytics Collector receives span data from all other agents | Check analytics agent subscription | Span data from all 5 other agents collected |

### 2C: Pipeline Behavior Preservation

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 2.14 | 17-intent taxonomy is preserved | Compare agent intent categories against INTENT_TAXONOMY from current `pipeline.py` | All 17 intents recognized |
| 2.15 | Critic blocks profanity, PII leakage, harmful content | Send adversarial test messages through pipeline | Critic rejects all test cases that current Critic rejects |
| 2.16 | Escalation triggers match current rules | Test escalation keywords and confidence threshold triggers | Same escalation behavior as current pipeline |
| 2.17 | Response quality is equivalent | Compare responses to a 20-message test corpus against baseline | No degradation in response relevance, tone, or accuracy |
| 2.18 | `USE_AGENT_CONTAINERS` flag is removed or set to `true` | `grep USE_AGENT_CONTAINERS $PROJECT_ROOT/src/ -r` | Flag is `true` or removed entirely (no bypass path) |
| 2.19 | `pipeline.py` monolithic Azure OpenAI direct calls are removed | Inspect `pipeline.py` | No direct `openai.chat.completions.create()` calls in pipeline orchestration |
| 2.20 | Multi-tenant context injection is preserved | Verify system prompt builder still feeds tenant config into Response Generation agent | Tenant-specific brand voice, policies, and custom instructions appear in responses |
| 2.21 | Unit tests pass after decomposition | `python -m pytest tests/ -x -q --tb=short` | >= $EXPECTED_UNIT_TESTS_MIN passed, 0 failed |
| 2.22 | Production regression suite passes | Run per `REPEATABLE-PROCEDURES.md` Production Regression Suite | Tier 0: all pass. Tier 1: >= 10 pass. |
| 2.23 | End-to-end conversation test | `POST /api/chat/conversations` then `POST /api/chat/messages` with widget key | 200 response with coherent AI-generated reply |

---

## Phase 3: MCP Client Framework + Tenant-Scoped Server Registry

**Goal:** Agent Red can connect to external MCP servers using the AGNTCY SDK's
`factory.create_client("MCP", ...)`. Each tenant configures their own MCP server
connections, isolated from other tenants.

**AGNTCY wiki reference:** Model Context Protocol (MCP)

### 3A: MCP Client Implementation

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 3.1 | `AgntcyFactory.create_client("MCP", ...)` is used (not a custom MCP client) | `grep -r "create_client.*MCP" $PROJECT_ROOT/src/ --include="*.py"` | At least 1 usage in production code |
| 3.2 | MCP client connects to a test MCP server | Start a test MCP server, configure tenant, verify connection | Client connects, discovers tools, returns tool list |
| 3.3 | MCP client invokes a tool and returns results | Call a test tool via MCP client | Tool result returned to calling agent |
| 3.4 | MCP transport uses SLIM (not raw stdio/HTTP) | Inspect MCP client transport configuration | SLIM transport with TLS 1.3 |
| 3.5 | Knowledge Retrieval agent is the primary MCP consumer | Verify MCP tool invocation originates from Knowledge Retrieval agent | MCP calls traced to Knowledge Retrieval agent |

### 3B: Tenant-Scoped MCP Server Registry

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 3.6 | Admin UI Integrations page supports MCP server configuration | Navigate to Integrations page, verify MCP server add/edit/remove UI | UI allows server URL, transport type, credentials |
| 3.7 | MCP server configurations are stored per-tenant in Cosmos DB | Query tenant preferences for MCP server entries | Stored in tenant partition, not global |
| 3.8 | Tenant A's MCP servers are invisible to Tenant B | Query Tenant B's integrations API | Returns only Tenant B's servers |
| 3.9 | MCP server credentials are stored in Key Vault (not Cosmos DB) | Inspect storage location for MCP server auth tokens | Credentials in Key Vault with tenant-scoped secret names |
| 3.10 | Hardcoded integration registry is replaced or extended | Inspect `admin_integration_api.py` | MCP servers are dynamically registered, not hardcoded |

### 3C: Safety and Validation

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 3.11 | PII tokenization occurs before MCP external calls | Send message containing PII, trace MCP request payload | No raw PII in MCP request |
| 3.12 | Critic validates MCP tool results before inclusion in response | Trace flow: MCP result → Critic validation → Response | Critic stage runs on MCP-augmented response |
| 3.13 | MCP server connection failure is graceful | Disconnect test MCP server, send customer message | Response generated without MCP data; no 500 error; degradation logged |
| 3.14 | Unit tests pass after MCP integration | `python -m pytest tests/ -x -q --tb=short` | >= $EXPECTED_UNIT_TESTS_MIN passed, 0 failed |

---

## Phase 4: UCP Commerce Protocol via MCP

**Goal:** Agent Red supports Universal Commerce Protocol operations through MCP
bindings, enabling standardized commerce operations beyond Shopify-only.

**AGNTCY wiki reference:** UCP Integration Guide, Model Context Protocol (MCP)

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 4.1 | UCP MCP client is implemented using SDK's `create_mcp_client()` | Inspect UCP integration code | UCP operations route through MCP client |
| 4.2 | Catalog search capability works via UCP | Send product search query through conversation | Agent returns product results from UCP catalog endpoint |
| 4.3 | Order status lookup works via UCP | Send "where is my order" query with order ID | Agent returns order status from UCP fulfillment endpoint |
| 4.4 | Existing Shopify integration is preserved (no regression) | Run Shopify-specific test flows | All current Shopify functionality works |
| 4.5 | UCP operations work for non-Shopify UCP-compliant merchants | Configure a non-Shopify UCP test endpoint, send commerce query | Agent returns commerce data from non-Shopify source |
| 4.6 | Checkout handoff via UCP | Send purchase-intent message | Agent generates UCP checkout session URL |
| 4.7 | UCP operations respect tier gates | Test UCP operations on Starter tier (if gated) | Tier enforcement matches configured gates |
| 4.8 | Unit tests pass after UCP integration | `python -m pytest tests/ -x -q --tb=short` | >= $EXPECTED_UNIT_TESTS_MIN passed, 0 failed |

---

## Phase 5: OpenTelemetry Per-Agent Tracing + Cost Attribution

**Goal:** All agent interactions are instrumented with OpenTelemetry spans. Each span
carries agent identity, token usage, and cost. An execution tree can be reconstructed
from traces.

**AGNTCY wiki reference:** Overview (execution tracing), Operations Dashboard

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 5.1 | OpenTelemetry SDK is installed and configured | `python -c "from opentelemetry import trace; print('OK')"` | Importable, exit code 0 |
| 5.2 | Each agent emits OTel spans with agent name attribute | Send test message, inspect exported spans | Spans contain `agent.name` attribute matching $EXPECTED_AGENTS |
| 5.3 | Spans include token usage (prompt_tokens, completion_tokens) | Inspect span attributes | Token counts present on LLM-calling spans |
| 5.4 | Spans include cost attribution (estimated_cost_usd) | Inspect span attributes | Cost estimate present, calculated from token count × model rate |
| 5.5 | Execution tree is reconstructable from span parent-child relationships | Trace a single conversation message through all agents | Tree shows: Intent → Knowledge → Response → Critic with timing |
| 5.6 | Traces feed into Agent Red's admin dashboard (not a separate AGNTCY dashboard) | Check dashboard data source | OTel data queryable from Agent Red's existing Application Insights or replacement |
| 5.7 | Per-agent latency breakdown is available | Query traces for P50/P95 per agent | Latency data per agent retrievable |
| 5.8 | Tracing does not degrade response latency by more than 10% | Compare response times with/without tracing | P95 latency increase < 10% |
| 5.9 | Unit tests pass after tracing integration | `python -m pytest tests/ -x -q --tb=short` | >= $EXPECTED_UNIT_TESTS_MIN passed, 0 failed |

---

## Phase 6: PII Tokenization at Transport Layer

**Goal:** Customer PII is replaced with UUIDs before any external AI API call. Mappings
are stored in Key Vault per-tenant. Prompt-based PII avoidance is replaced by
infrastructure-level enforcement.

**AGNTCY wiki reference:** Architecture (PII tokenization), Overview (security)

| # | Assertion | Verification | Pass Criteria |
|---|-----------|-------------|---------------|
| 6.1 | PII tokenizer module exists | `ls $PROJECT_ROOT/src/**/pii_tokenizer*` or equivalent | Module exists with tokenize/detokenize functions |
| 6.2 | Customer name is tokenized before external LLM call | Send message "Hi, I'm John Smith", inspect outbound LLM request | "John Smith" replaced with UUID in LLM prompt |
| 6.3 | Email address is tokenized | Send message containing email, inspect outbound LLM request | Email replaced with UUID |
| 6.4 | Phone number is tokenized | Send message containing phone number, inspect outbound LLM request | Phone replaced with UUID |
| 6.5 | Order number / account number is tokenized | Send message with order number, inspect outbound LLM request | Order number replaced with UUID |
| 6.6 | UUID mappings are stored in Key Vault per-tenant | Inspect Key Vault after tokenization | Mapping stored with tenant-scoped secret name |
| 6.7 | Detokenization occurs before response is sent to customer | Send message with PII, verify response uses original values (not UUIDs) | Customer sees their actual name/email, not UUIDs |
| 6.8 | Tokenization works across all 6 agents (not just at gateway) | Trace PII through agent pipeline | No raw PII visible in any inter-agent A2A message |
| 6.9 | PII tokenization before MCP external calls | Send message with PII that triggers MCP tool, inspect MCP request | No raw PII in MCP request payload |
| 6.10 | Prompt-based PII avoidance instructions are removed or demoted to defense-in-depth | Inspect system prompt builder | Tokenization is primary PII protection; prompt instructions are secondary |
| 6.11 | Tokenization does not degrade response quality | Compare 20-message test corpus responses pre/post tokenization | No degradation in relevance, accuracy, or natural language quality |
| 6.12 | Unit tests pass after PII tokenization | `python -m pytest tests/ -x -q --tb=short` | >= $EXPECTED_UNIT_TESTS_MIN passed, 0 failed |

---

## Postconditions (Full Adoption)

When all 6 phases are complete and all assertions pass, the following must be true:

| # | Condition | Verification |
|---|-----------|-------------|
| POST-1 | All Phase 1-6 assertions pass (0 FAIL) | Run this procedure end-to-end |
| POST-2 | `USE_AGENT_CONTAINERS` is `true` or removed | `grep -r USE_AGENT_CONTAINERS $PROJECT_ROOT/src/` |
| POST-3 | No direct Azure OpenAI calls in pipeline orchestration | `grep -r "openai.chat.completions" $PROJECT_ROOT/src/chat/pipeline.py` returns 0 matches |
| POST-4 | `agntcy-app-sdk` has active import statements (not just requirements.txt) | `grep -r "from agntcy_app_sdk\|import agntcy_app_sdk" $PROJECT_ROOT/src/ --include="*.py"` returns >= 6 matches |
| POST-5 | All 6 agents run as separate containers | `docker ps` or Azure Container Apps list shows 6 agent containers |
| POST-6 | MCP client framework is operational with at least 1 configured server | Admin UI shows connected MCP server |
| POST-7 | Unit test count has not regressed | Pass count >= $EXPECTED_UNIT_TESTS_MIN |
| POST-8 | Production regression suite passes | Run per REPEATABLE-PROCEDURES.md |
| POST-9 | Customer-facing conversation flow works end-to-end | Widget → conversation → AI response → no errors |
| POST-10 | No customer/merchant-visible functional regression | All 172 UI test assertions from `ui-test-procedure.md` still pass (PASS + SKIP counts unchanged) |
| POST-11 | No substantial cost regression | Monthly Azure spend delta < 15% from pre-realignment baseline |

---

## Scoring Model

### Per-Run Scoring

After each execution, calculate:

```
Total assertions:  57 (Phase 1: 10, Phase 2: 23, Phase 3: 14, Phase 4: 8, Phase 5: 9, Phase 6: 12)
                      (minus any assertions marked SKIP for phases not yet started)

Adoption score = PASS count / (PASS count + FAIL count) × 100%

Phase score    = Phase PASS count / Phase total assertions × 100%
```

**Note:** SKIP is used for assertions in phases that have not yet begun. Once a phase
is started, all its assertions must resolve to PASS or FAIL (no SKIP within an
active phase).

### Completeness Thresholds

| Score | Meaning |
|-------|---------|
| 0% | No AGNTCY platform adoption (current state) |
| 15-20% | Phase 1 complete (SDK + transport) |
| 50-55% | Phase 1 + Phase 2 complete (agents containerized) |
| 70-75% | Phase 1-4 complete (MCP + UCP operational) |
| 85-90% | Phase 1-5 complete (observability aligned) |
| 100% | Full platform adoption — all 57 assertions pass |

### Run Log

| Date | Operator | Score | PASS | FAIL | SKIP | Phases Active | Notes |
|------|----------|-------|------|------|------|---------------|-------|
| 2026-02-16 | Claude (session 25) | 15% | Phase 1: 6/10, Phase 2: partial (2A: 0/6, 2B: 0/7, 2C: 2/10) | — | Phase 3-6: SKIP | Phase 1+2 | Phase 1 SDK adoption complete. Phase 2 code-level decomposition complete (agents extracted, pipeline rewritten, 100 tests). Container images not yet built/pushed to ACR. A2A over NATS not yet operational (using in-process delegation). |
| 2026-02-17 | Claude (session 37) | — | Phase 3: **14/14** | 0 | Phase 4-6: SKIP | Phase 1+2+3 | **AGNTCY Phase 3 COMPLETE.** Cycle 4 (session 36): MCP client + Shopify Storefront (3.1-3.5, 3.11-3.14). Cycle 5 (session 37): Stripe MCP + credential cache + mutation safety + Admin UI (3.6-3.10). All assertions pass — AGNTCY SDK mandatory for all agent communication. 2,646 unit tests, 0 failures. |
| 2026-02-28 | Claude (session 120) | — | Phase 2: complete, Phase 5-6: in progress | 0 | — | Phase 1+2+3+5+6 | **Erroneous artifacts corrected (SPEC-1534).** Removed false opt-out language from run log and docs. `mcp_client.py` refactored to use `AgntcyFactory.create_client("MCP", ...)`. `USE_AGENT_CONTAINERS` default set to `true`. Phase 5: OTel per-agent tracing + cost attribution. Phase 6: reversible PII tokenization. |

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| `agntcy-app-sdk` import fails (package not installed) | Environment | `pip install agntcy-app-sdk>=$SDK_MIN_VERSION` |
| NATS not running for SLIM transport tests | Environment | Start NATS: `docker run -p 4222:4222 -p 8222:8222 nats:latest` |
| Docker not available for container assertions | Environment | Start Docker Desktop |
| Agent container image not in ACR | Phase incomplete | Build and push agent image per deployment procedure |
| MCP test server not available | Environment | Start test MCP server per Phase 3 setup instructions |
| Unit test count drops below $EXPECTED_UNIT_TESTS_MIN | Procedure defect (if tests removed) or Phase defect (if code broke them) | Investigate — update $EXPECTED_UNIT_TESTS_MIN only if tests were intentionally consolidated |
| SDK version mismatch (API changed between versions) | Environment | Pin SDK version in requirements.txt; update procedure $SDK_MIN_VERSION |
| PII tokenization degrades response quality | Phase defect | Tune tokenization boundaries; add to test corpus |
| Response latency exceeds SLA after agent decomposition | Phase defect | Profile per-agent latency; optimize slow agent or reduce A2A hops |
| Azure Container Apps revision fails after adding agent containers | Environment transient or Phase defect | Check ACR build logs; verify container health probes |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Created: 2026-02-16 (Session 25)*
*Version: 1.0.0*
