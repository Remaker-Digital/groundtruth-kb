# Per-Customer Persistent AI Agent Personalization — Feasibility Research

> **Project:** Agent Red Customer Engagement
> **Date:** 2026-01-30
> **Type:** Technical Research & Architecture Analysis
> **Status:** Research Complete — Awaiting Decision

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Per-Customer Fine-Tuning Feasibility](#2-per-customer-fine-tuning-feasibility)
3. [Alternative Personalization Approaches](#3-alternative-personalization-approaches)
4. [Periodic Retraining Pipeline Design](#4-periodic-retraining-pipeline-design)
5. [Agent State Persistence Patterns](#5-agent-state-persistence-patterns)
6. [Comparative Analysis](#6-comparative-analysis)
7. [Production Case Studies](#7-production-case-studies)
8. [Recommendations for Agent Red](#8-recommendations-for-agent-red)

---

## 1. Executive Summary

This research evaluates the feasibility of per-customer persistent AI agents that are periodically retrained on accumulated historical interaction data. The analysis covers five distinct approaches to customer-specific AI personalization, their cost structures, quality tradeoffs, and production viability.

**Key Finding:** Per-customer full fine-tuning is technically feasible but economically impractical for Agent Red at launch scale. The recommended architecture is a **three-layer personalization stack**: (1) dynamic context injection with customer preference profiles, (2) RAG over vectorized transcripts, and (3) a memory framework (Mem0 or OpenAI Agents SDK `RunContextWrapper`) for session-spanning state. Fine-tuning should be reserved as a premium Enterprise-tier feature for high-volume customers with 1,000+ historical interactions.

---

## 2. Per-Customer Fine-Tuning Feasibility

### 2.1 OpenAI Fine-Tuning API Pricing (as of January 2026)

| Model | Training Cost (per 1M tokens) | Inference Input (per 1M tokens) | Inference Output (per 1M tokens) |
|-------|-------------------------------|----------------------------------|----------------------------------|
| GPT-4o-mini | $3.00 | $0.30 | $1.20 |
| GPT-4.1 | $25.00 | Higher than base | Higher than base |
| GPT-4.1-mini | ~$3.00 | ~$0.40 | ~$1.60 |
| o4-mini (Reinforcement FT) | $100/hr | Varies | Varies |

**No hosting fee** — OpenAI API fine-tuned models are served on-demand with no per-model hosting charge.

**Inference discount** available if data sharing is enabled during fine-tune job creation.

### 2.2 Azure OpenAI Fine-Tuning Pricing

| Cost Component | Amount | Notes |
|----------------|--------|-------|
| Training | Varies by model, similar to OpenAI | Per-token during training |
| **Hosting (deployed model)** | **~$1,836/month minimum** | Per fine-tuned model deployment, charged whether used or not |
| Non-deployed storage | Free | Up to 100 models per resource |
| Inference tokens | Standard rates | On top of hosting fee |

**Critical difference from OpenAI direct:** Azure charges a continuous hosting fee of approximately $1,836/month per deployed fine-tuned model. This makes per-customer fine-tuning on Azure economically prohibitive — 10 customers would cost $18,360/month in hosting alone.

**Mitigation:** Azure stores up to 100 non-deployed models for free. Models can be deployed on-demand and undeployed when not in use, but this introduces cold-start latency.

### 2.3 Per-Customer Fine-Tuning Cost Modeling

**Scenario: 100 Agent Red customers, each with fine-tuned model**

| Approach | Monthly Cost | Feasibility |
|----------|-------------|-------------|
| OpenAI API (GPT-4o-mini, all deployed) | ~$0/mo hosting + inference | Feasible at scale |
| Azure OpenAI (all deployed) | ~$183,600/mo hosting alone | Not feasible |
| Azure OpenAI (deploy-on-demand) | ~$0 idle + cold-start latency | Feasible but degraded UX |

**OpenAI API is the only viable path for per-customer fine-tuning** due to zero hosting costs.

### 2.4 Minimum Data Requirements

| Dataset Size | Expected Outcome |
|-------------|-----------------|
| 10 examples | OpenAI minimum; marginal improvement |
| 50-100 examples | Noticeable format/tone alignment |
| 200+ examples | Meaningful behavioral changes begin |
| 1,000+ examples | Robust domain adaptation |
| 5,000-50,000 examples | Production-grade specialization |

**When fine-tuning becomes meaningful vs. RAG:**
- **Below 200 interactions:** RAG with dynamic context injection outperforms fine-tuning. The model lacks sufficient signal to learn customer-specific patterns.
- **200-1,000 interactions:** Hybrid approach viable — RAG for knowledge retrieval, light fine-tuning for tone/style.
- **Above 1,000 interactions:** Fine-tuning delivers measurable quality improvements in communication style matching, recurring issue recognition, and proactive suggestion accuracy.
- **Quality threshold:** For every linear increase in training data error rate, expect a roughly quadratic increase in fine-tuned model error rate. Data curation is more important than volume.

### 2.5 Fine-Tuning Training Cost Per Customer

Assuming an average customer support transcript is ~500 tokens (input + output):

| Customer History | Total Tokens | GPT-4o-mini Training Cost | GPT-4.1 Training Cost |
|-----------------|-------------|--------------------------|----------------------|
| 200 transcripts | ~100K tokens | $0.30 | $2.50 |
| 1,000 transcripts | ~500K tokens | $1.50 | $12.50 |
| 5,000 transcripts | ~2.5M tokens | $7.50 | $62.50 |
| 50,000 transcripts | ~25M tokens | $75.00 | $625.00 |

These training costs are one-time per retraining cycle and are very low. The cost barrier for per-customer fine-tuning is not training — it is operational complexity, data pipeline maintenance, and quality assurance across potentially hundreds of models.

---

## 3. Alternative Personalization Approaches

### 3.1 Dynamic System Prompts with Customer Context

**How it works:** At the start of each conversation, the system prompt is dynamically populated with customer-specific context: account details, product usage patterns, communication preferences, recent interactions summary, and known issues.

**Architecture:**
```
Customer Request → Context Retrieval Service → Build System Prompt → LLM Call
                      ↓
              Customer Profile DB
              (preferences, history summary,
               product config, known issues)
```

**Advantages:**
- Zero training cost
- Instant updates (no retraining lag)
- Works with any LLM (no vendor lock-in)
- Token-efficient if context is well-summarized
- Easy to audit and debug

**Disadvantages:**
- Context window limits constrain how much history can be included
- Requires careful prompt engineering to avoid overwhelming the model
- Does not encode behavioral patterns into model weights

**Cost:** Near-zero incremental cost — only the additional input tokens for context injection (~200-500 tokens per request, approximately $0.0001 per conversation with GPT-4o-mini).

### 3.2 Dynamic Few-Shot Examples from Customer History

**How it works:** For each new customer query, the system retrieves the most semantically similar past interactions (question-answer pairs) from that customer's history and injects them as few-shot examples in the prompt.

**Architecture:**
```
Customer Query → Embed Query → Vector Search (customer's history) → Top-K Similar
                                                                       ↓
                                                              Build Prompt with
                                                              2-3 Few-Shot Examples
                                                                       ↓
                                                                    LLM Call
```

**Advantages:**
- Teaches the model the customer's preferred interaction style by example
- No training required
- Automatically adapts as new interactions accumulate
- Research shows diminishing returns after 2-3 examples, keeping costs low

**Disadvantages:**
- Increases prompt size (token cost)
- Retrieval quality depends on embedding model and vector DB indexing
- May surface irrelevant examples if history is sparse or noisy

**Cost:** Embedding cost (~$0.0001 per query for text-embedding-3-large) + vector DB storage ($5-15/month per customer at moderate scale) + additional prompt tokens (~500-1,500 tokens per request).

### 3.3 LoRA Adapters Per Customer

**How it works:** Low-Rank Adaptation (LoRA) creates lightweight adapter layers (~1-5% of base model size) that can be swapped at inference time. Each customer gets their own adapter trained on their interaction history.

**Architecture:**
```
Base Model (shared) + Customer LoRA Adapter (swapped per request)
     ↓
  Inference
```

**Advantages:**
- Adapters are small (typically <1% of base model size)
- Data isolation — no cross-customer leakage
- Can be hot-swapped during inference
- Training is fast and cheap

**Disadvantages:**
- Requires self-hosted model infrastructure (not available via OpenAI API)
- Dynamic adapter loading in production is an emerging (not mature) capability
- vLLM currently requires pre-declaration of LoRA modules (no true dynamic loading without redeployment)
- Operational complexity of managing hundreds of adapters

**Production readiness (2025-2026):**
- **LoRAServe** (Nov 2025): Achieves 2x throughput, 9x lower TTFT, 50% fewer GPUs via workload-aware adapter placement
- **EdgeLoRA** (Jul 2025): 4x throughput boost on edge devices, heterogeneous memory management
- **AWS SageMaker**: Production-grade multi-tenant LoRA serving
- **Anyscale/Ray Serve**: Multi-LoRA with runtime adapter switching
- **vLLM**: Active development for dynamic LoRA module loading (RFC #12174)

**Cost:** Requires GPU infrastructure ($1,000-5,000/month for a single A100/H100 instance). Economically viable only at 50+ customers sharing a base model. Not viable for Agent Red at launch scale.

**Verdict for Agent Red:** LoRA is not feasible for Launch 1.0 due to infrastructure requirements and operational complexity. It becomes a compelling option if Agent Red later moves to self-hosted models at Enterprise tier.

### 3.4 Customer Preference Profiles Extracted from Interaction History

**How it works:** An offline pipeline periodically processes customer interaction history to extract structured preference profiles: communication style preferences, commonly referenced products, recurring issues, sentiment patterns, escalation triggers, and domain vocabulary.

**Architecture:**
```
Interaction History → Extraction Pipeline (LLM-based) → Structured Profile JSON
                                                            ↓
                                                   Cosmos DB (per customer)
                                                            ↓
                                                   Injected into System Prompt
```

**Profile schema example:**
```json
{
  "customer_id": "cust_abc123",
  "communication_style": {
    "formality": "casual",
    "verbosity": "concise",
    "preferred_language": "en-US"
  },
  "product_context": {
    "plan": "professional",
    "primary_integrations": ["shopify", "zendesk"],
    "usage_volume": "3,200 conversations/month"
  },
  "known_patterns": {
    "recurring_issues": ["webhook delivery delays", "Zendesk sync latency"],
    "escalation_triggers": ["billing disputes", "data loss concerns"],
    "positive_triggers": ["new feature announcements", "usage reports"]
  },
  "interaction_summary": {
    "total_interactions": 847,
    "avg_satisfaction": 4.2,
    "last_updated": "2026-01-28T14:30:00Z"
  }
}
```

**Advantages:**
- Structured, auditable, and debuggable
- Very small token footprint when injected (~100-200 tokens)
- Can be combined with any other approach
- Updates are incremental — no full reprocessing needed
- Supports human review and override

**Disadvantages:**
- Extraction pipeline needs careful prompt engineering
- May miss nuanced patterns that fine-tuning would capture
- Requires periodic reprocessing as profiles drift

**Cost:** Extraction cost ~$0.01-0.05 per customer per update cycle (using GPT-4o-mini for extraction). Storage in Cosmos DB: negligible (~$0.001/month per profile).

### 3.5 Memory Layer Frameworks (Mem0, Zep, OpenAI Agents SDK)

#### Mem0

**What it is:** An open-source (Apache 2.0) universal memory layer for LLM applications. Provides automatic extraction, consolidation, and retrieval of conversational memories.

**Architecture:**
- **Extraction Phase:** Processes latest exchange + rolling summary + recent messages → extracts candidate memories via LLM
- **Update Phase:** Compares new facts against existing vector store entries → chooses ADD, UPDATE, DELETE, or NO-OP
- **Enhanced variant (Mem0g):** Graph-based memory using Neo4j for complex relational structures
- **Default LLM:** gpt-4.1-nano (for extraction/updates)

**Benchmark performance (LOCOMO):**
- 26% improvement over OpenAI baseline on LLM-as-a-Judge metric
- P95 latency: 1.44s (vs. 17.12s for full-context methods — 91% reduction)
- Token consumption: ~1.8K tokens/conversation (vs. 26K for full-context — 90% reduction)

**Cost:** Open-source self-hosted (free) or Mem0 Platform (managed). Requires vector DB (Qdrant, Pinecone, etc.) and graph DB (Neo4j) for Mem0g variant.

#### Zep

**What it is:** A long-term memory service for AI assistants with temporal knowledge graphs and entity extraction.

**Performance notes:** Zep's graph construction involves multiple asynchronous LLM calls and extensive background processing. In benchmarks, Zep consumed over 600K tokens (primarily due to caching full abstractive summaries at each node), making it impractical for high-throughput, real-time applications. However, there is ongoing debate about benchmarking fairness.

#### OpenAI Agents SDK RunContextWrapper

**What it is:** A built-in state management mechanism in the OpenAI Agents SDK that enables structured state persistence across agent runs.

**Key capabilities:**
- **State Management:** Persistent state via `RunContextWrapper` class
- **Memory Injection:** Inject relevant state portions at session start
- **Memory Distillation:** Capture insights during active turns via tool calls (memory-as-a-tool pattern)
- **Memory Consolidation:** Merge session notes into conflict-free global memories
- **Session storage:** SQLite-based (in-memory default; file path for persistence)

**Memory design patterns from OpenAI Cookbook:**
- **Stability:** Preferences that rarely change (e.g., preferred communication style)
- **Drift:** Gradual changes over time (e.g., evolving product usage patterns)
- **Contextual variance:** Preferences that depend on situation (e.g., different behavior for billing vs. technical issues)

**Limitation:** Does not provide durable semantic memory out of the box. For cross-session persistence, external storage (Cosmos DB, PostgreSQL, etc.) or integration with Mem0 is required.

---

## 4. Periodic Retraining Pipeline Design

### 4.1 Pipeline Architecture

For Agent Red customers with sufficient interaction history (1,000+ transcripts) who opt into fine-tuned models:

```
┌─────────────────────────────────────────────────────────────┐
│                  PERIODIC RETRAINING PIPELINE                │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │ Collect  │───→│ Cleanse  │───→│ Format   │───→│ Train  │ │
│  │ New      │    │ & Filter │    │ as JSONL │    │ (API)  │ │
│  │ Transcr. │    │          │    │          │    │        │ │
│  └──────────┘    └──────────┘    └──────────┘    └────┬───┘ │
│                                                       │     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐        │     │
│  │ Deploy   │←───│ Evaluate │←───│ Compare  │←───────┘     │
│  │ if Pass  │    │ Quality  │    │ Baseline │              │
│  └──────────┘    └──────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Pipeline Stages

| Stage | Description | Duration | Cost |
|-------|------------|----------|------|
| **1. Collect** | Pull new transcripts since last training from Cosmos DB | Minutes | ~$0 |
| **2. Cleanse** | PII removal (existing tokenization pipeline), filter low-quality interactions, remove system messages, normalize format | 5-15 min | ~$0.01 (LLM-assisted filtering) |
| **3. Format** | Convert to OpenAI JSONL fine-tuning format (system/user/assistant turns) | Minutes | ~$0 |
| **4. Train** | Submit to OpenAI Fine-Tuning API | 30-120 min | $1.50-75 (depending on dataset size) |
| **5. Compare** | Run evaluation suite against baseline model on held-out test set | 10-30 min | ~$0.10-1.00 (inference on test set) |
| **6. Evaluate** | Check quality metrics (BLEU/ROUGE, customer satisfaction correlation, hallucination rate, format compliance) | Minutes | ~$0 |
| **7. Deploy** | If metrics improve or hold, swap fine-tuned model ID in customer config | Seconds | ~$0 |

### 4.3 Retraining Schedule Options

| Schedule | When to Use | Cost/Month (per customer) |
|----------|-------------|--------------------------|
| **Weekly** | High-volume Enterprise customers (5,000+ conv/mo) | $6-300 |
| **Bi-weekly** | Professional tier with active usage | $3-150 |
| **Monthly** | Standard retraining cadence | $1.50-75 |
| **Trigger-based** | When quality metrics drop below threshold | Variable |

### 4.4 Latency Considerations

- **Training latency:** 30 minutes to 2 hours per fine-tune job (OpenAI API)
- **Deployment latency:** Near-instant (model ID swap in customer configuration)
- **End-to-end pipeline:** 1-3 hours from trigger to deployment
- **No user-facing downtime:** Old model serves requests until new model passes evaluation

### 4.5 Retraining Pipeline for Memory/Profile Approach (Recommended Path)

For the recommended profile-based approach, the retraining pipeline is simpler and cheaper:

```
┌────────────────────────────────────────────────────────┐
│          PROFILE UPDATE PIPELINE (daily/weekly)         │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Collect  │───→│ Extract  │───→│ Merge    │          │
│  │ New      │    │ Patterns │    │ into     │          │
│  │ Sessions │    │ (LLM)   │    │ Profile  │          │
│  └──────────┘    └──────────┘    └──────────┘          │
│                                                         │
│  Cost: ~$0.01-0.05 per customer per cycle               │
│  Latency: Minutes (no training required)                │
│  Downtime: None                                         │
└────────────────────────────────────────────────────────┘
```

---

## 5. Agent State Persistence Patterns

### 5.1 Framework Comparison for Long-Term Memory

| Framework | State Persistence | Long-Term Memory | Multi-Session | Production Readiness |
|-----------|------------------|-----------------|---------------|---------------------|
| **LangGraph** | Checkpointing (reducer-driven state schemas) | Via external vector DB | Yes (persistent checkpoints) | High — 600-800 companies in production (est. end 2025) |
| **CrewAI** | Role-based memory per agent | Limited built-in | Partial | Medium — scalability limitations reported at 6-12 months |
| **AutoGen → Microsoft Agent Framework** | Message lists + external integrations | Via Foundry Agent Service (managed) | Yes (GA Q1 2026) | High — enterprise SLAs, SOC 2, HIPAA |
| **Semantic Kernel → Microsoft Agent Framework** | IStorage interface (Blob/CosmosDB) | Native long-term memory in Foundry | Yes (native) | High — multi-language (C#, Python, Java) |
| **OpenAI Agents SDK** | `RunContextWrapper` + SQLite sessions | Via Mem0 integration or custom | Yes (with external storage) | Medium-High — newer SDK, active development |
| **Mem0** | Vector DB + Graph DB (Neo4j) | Native (core feature) | Yes | High — 29K+ GitHub stars, Apache 2.0 |

### 5.2 What State to Persist

For Agent Red customer engagement agents, the following state categories should persist across sessions:

| State Category | Examples | Update Frequency | Storage |
|---------------|---------|-------------------|---------|
| **Customer Profile** | Company name, plan tier, integrations enabled | On account change | Cosmos DB |
| **Communication Preferences** | Formality, verbosity, language, preferred channels | Extracted weekly | Cosmos DB |
| **Product Usage Patterns** | Conversation volumes, peak hours, most-used features | Daily aggregation | Cosmos DB / App Insights |
| **Recurring Issues** | Repeated problem categories, known workarounds | Extracted weekly | Cosmos DB |
| **Interaction History Summary** | Rolling summary of recent interactions | Per-session update | Cosmos DB |
| **Escalation Patterns** | What triggers escalation, preferred escalation path | Extracted monthly | Cosmos DB |
| **Satisfaction Signals** | CSAT scores, sentiment trends, feedback | Per-interaction | Cosmos DB |

### 5.3 Microsoft Agent Framework (Recommended for Agent Red)

Given Agent Red's existing Azure infrastructure, the Microsoft Agent Framework (converging Semantic Kernel + AutoGen, GA Q1 2026) is the natural fit for agent state persistence:

- **Native Azure integration** with Cosmos DB, Blob Storage, Key Vault
- **Foundry Agent Service** provides managed long-term memory (chat summaries, user preferences, task outcomes)
- **Process Framework** for stateful, long-running workflows (GA Q2 2026)
- **Multi-language support** (C#, Python, Java)
- **Enterprise compliance** (SOC 2, HIPAA)

However, the GA timeline (Q1 2026) overlaps with Agent Red's launch timeline. A pragmatic approach is to build on the OpenAI Agents SDK for initial launch (with custom Cosmos DB persistence) and plan migration to Microsoft Agent Framework when it reaches GA.

---

## 6. Comparative Analysis

### 6.1 Approach Comparison Matrix

| Dimension | RAG over Vectorized Transcripts | Periodic Fine-Tuning | Dynamic Context Injection | Memory Frameworks (Mem0) |
|-----------|-------------------------------|---------------------|--------------------------|------------------------|
| **Setup Cost** | Medium ($50-200 for embedding + vector DB) | Low-Medium ($1.50-75 per training) | Low (~$0) | Low-Medium ($20-50 for infrastructure) |
| **Ongoing Cost/Customer/Month** | $5-15 (vector DB + embedding) | $1.50-300 (depending on frequency) | ~$0.01 (extra prompt tokens) | $5-20 (vector DB + LLM extraction) |
| **Quality (Tone/Style Match)** | Medium (depends on retrieval) | High (encoded in weights) | Medium-High (depends on prompt) | Medium-High (improves over time) |
| **Quality (Knowledge Accuracy)** | High (retrieves actual data) | Medium (can hallucinate) | Medium (limited by context window) | Medium (memory quality varies) |
| **Latency** | +100-300ms (retrieval step) | No additional latency | No additional latency | +50-200ms (memory retrieval) |
| **Data Freshness** | Real-time (index new docs immediately) | Stale until next retrain cycle | Real-time (profile updated per interaction) | Near-real-time (memory extracted per session) |
| **Maintainability** | Medium (vector DB ops, index management) | Low-Medium (automated pipeline) | High (simple DB reads) | Medium (memory quality monitoring) |
| **Scalability** | High (vector DBs scale well) | Medium (one model per customer) | High (no per-customer infrastructure) | High (shared infrastructure) |
| **Auditability** | High (can trace retrieval sources) | Low (black box weights) | High (prompt is inspectable) | Medium (memory entries visible but LLM-generated) |
| **Vendor Lock-in** | Medium (vector DB choice) | High (OpenAI fine-tuning API) | Low (works with any LLM) | Low-Medium (Mem0 is open-source) |

### 6.2 When to Use Each Approach

| Approach | Best For | Not Suitable For |
|----------|---------|-----------------|
| **RAG** | Knowledge-heavy queries (product docs, policies, order history) | Style/tone matching, behavioral pattern learning |
| **Fine-Tuning** | High-volume customers needing deep style adaptation, compliance-critical formatting | Low-volume customers, rapidly changing knowledge |
| **Dynamic Context Injection** | All customers as baseline personalization, customer profile injection | Deep behavioral pattern recognition |
| **Memory Frameworks** | Cross-session continuity, preference learning, recurring pattern detection | Large-scale knowledge retrieval, structured data queries |

### 6.3 Recommended Layered Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    PERSONALIZATION STACK                     │
│                                                              │
│  Layer 4: Fine-Tuned Model (Enterprise only, optional)      │
│  ──────────────────────────────────────────────────────────  │
│  Layer 3: Memory Framework (Mem0 / RunContextWrapper)       │
│           Cross-session state, preference learning           │
│  ──────────────────────────────────────────────────────────  │
│  Layer 2: RAG (Vectorized Transcripts + Knowledge Base)     │
│           Customer-specific knowledge retrieval              │
│  ──────────────────────────────────────────────────────────  │
│  Layer 1: Dynamic Context Injection (ALL customers)         │
│           Customer profile, preferences, account context     │
└────────────────────────────────────────────────────────────┘
```

**Layer 1** is included for every customer at no additional cost. Layers 2-4 are progressively available by tier.

---

## 7. Production Case Studies

### 7.1 Sierra AI — Agent Data Platform

**Approach:** Proprietary Agent Data Platform (ADP) with per-customer memory and context.

- Every interaction builds the agent's understanding of the customer
- Single agent per company spanning all channels (product discovery, sales, support, retention)
- Agent OS 2.0 introduced Agent Studio for building production-ready agents
- Data isolation: customer data used only for that customer's agent, PII encrypted and masked
- Positions itself as a "vertical AI company for customer experience"

### 7.2 Intercom — Fin AI Agent

**Approach:** Patented Fin AI Engine with purpose-built RAG architecture.

- Custom LLMs trained on real customer service interactions (retrieval model, reranker model, summary model)
- Data connectors to external systems for personalized answers
- Multi-step reasoning with sub-agent orchestration and validation layers
- Claims to resolve customer queries without human intervention in many cases

### 7.3 Zendesk AI

**Approach:** AI natively embedded in ticketing ecosystem, trained on 18B+ interactions.

- AI copilot with conversational intelligence for proactive, contextual agent assistance
- Personalized suggestions based on customer needs and preferences
- Intent detection, summarization, and agent assist powered by generative AI
- 99.9% uptime, SOC 2 and ISO 27001 certified

### 7.4 Blip (Azure OpenAI + .NET)

**Approach:** RAG-based AI assistant integrated into customer care platform.

- Handles 1B+ messages monthly
- AI assistant helps agents complete 2x more loans
- Acceptance rates for AI-recommended replies: 80% (up from 20-30%)

### 7.5 Key Observations from Production Systems

1. **No major production system uses per-customer fine-tuning.** All rely on RAG, context injection, or proprietary memory systems.
2. **Sierra is closest to "persistent per-customer agent"** with its Agent Data Platform, but uses memory/context approaches, not fine-tuning.
3. **Intercom invests in custom LLMs** but trains them on aggregate customer service data across all customers, not per-customer fine-tuning.
4. **The production consensus is:** dynamic context + RAG + memory layers, with fine-tuning reserved for aggregate model improvement (not per-customer).

---

## 8. Recommendations for Agent Red

### 8.1 Recommended Architecture for Launch 1.0

**Implement Layers 1-2 for all customers; Layer 3 for Professional+; Layer 4 deferred to post-launch.**

#### Layer 1: Dynamic Context Injection (All Tiers — Starter, Professional, Enterprise)

**Implementation:**
- Build customer preference profiles in Cosmos DB (structured JSON)
- Populate system prompt dynamically with: customer name, plan tier, enabled integrations, communication style preference, recent interaction summary (last 3-5 interactions)
- Use existing AGNTCY PII tokenization for data safety

**Cost per customer:** ~$0 incremental (100-200 extra tokens per request)

**Implementation effort:** 2-3 days (profile schema + system prompt template + Cosmos DB integration)

#### Layer 2: RAG over Customer-Specific Knowledge (All Tiers)

**Implementation:**
- Already have knowledge retrieval agent with text-embedding-3-large (100% retrieval@1)
- Extend vector index to include per-customer data: their product configuration, past ticket resolutions, custom workflows
- Partition vector index by tenant for data isolation

**Cost per customer:** $5-15/month (vector storage + embedding compute)

**Implementation effort:** 1-2 weeks (tenant-partitioned vector index + retrieval pipeline extension)

#### Layer 3: Memory Framework (Professional + Enterprise)

**Implementation:**
- Integrate Mem0 (open-source, Apache 2.0) with existing agent architecture
- Store memory facts in Cosmos DB (vector search capability already available)
- Extract preferences, recurring patterns, and satisfaction signals per session
- Memory consolidation runs as background job after each session

**Cost per customer:** $5-20/month (Mem0 LLM extraction costs + storage)

**Implementation effort:** 2-3 weeks (Mem0 integration + Cosmos DB memory store + consolidation pipeline)

**Alternative:** OpenAI Agents SDK `RunContextWrapper` with custom Cosmos DB persistence. Simpler but less feature-rich than Mem0.

#### Layer 4: Per-Customer Fine-Tuning (Enterprise — Future, Post-Launch)

**Implementation (when ready):**
- Offer as premium Enterprise add-on ($299/month per customer)
- Minimum requirement: 1,000+ historical interactions
- Monthly retraining on GPT-4o-mini via OpenAI Fine-Tuning API
- Automated quality evaluation before deployment
- Customer opt-in with data consent

**Cost to Agent Red:** ~$5-15/month per customer (training + evaluation)
**Price to customer:** $299/month (add-on)
**Margin:** ~95%+

### 8.2 Tier Mapping

| Personalization Feature | Starter ($149) | Professional ($399) | Enterprise ($999) |
|------------------------|----------------|--------------------|--------------------|
| Dynamic context injection | Yes | Yes | Yes |
| Customer preference profiles | Basic | Advanced | Advanced |
| RAG over customer knowledge | Standard KB | Custom KB + history | Custom KB + full history |
| Memory framework (Mem0) | No | Yes | Yes |
| Cross-session preference learning | No | Yes | Yes |
| Dynamic few-shot examples | No | No | Yes |
| Per-customer fine-tuning | No | No | Add-on ($299/mo) |

### 8.3 Implementation Priority for Launch 1.0

| Priority | Feature | Tier | Effort | Dependencies |
|----------|---------|------|--------|-------------|
| 1 | Customer preference profile schema | All | 1 day | Cosmos DB |
| 2 | Dynamic system prompt builder | All | 2 days | Profile schema |
| 3 | Tenant-partitioned vector index | All | 1 week | Existing knowledge retrieval agent |
| 4 | Mem0 integration (or custom memory) | Pro+ | 2-3 weeks | Cosmos DB vector search |
| 5 | Profile extraction pipeline | All | 1 week | Historical transcripts |
| 6 | Few-shot example retrieval | Enterprise | 1 week | Vector index |
| 7 | Fine-tuning pipeline | Enterprise add-on | 2-3 weeks | OpenAI API, evaluation framework |

### 8.4 Key Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Memory quality degradation over time | Weekly memory consolidation with quality scoring; human-reviewable memory entries |
| Profile drift (customer preferences change) | Sliding window extraction (last 90 days weighted higher); manual override capability |
| Fine-tuned model quality regression | Automated evaluation gate before deployment; rollback to base model |
| Data isolation in multi-tenant | Tenant-partitioned Cosmos DB containers; PII tokenization before memory extraction |
| Cost overrun on LLM extraction | Use GPT-4o-mini/GPT-4.1-nano for extraction tasks; batch processing during off-peak |

---

## Sources

### Fine-Tuning Pricing & Feasibility
- [OpenAI API Pricing](https://platform.openai.com/docs/pricing)
- [Azure OpenAI Fine-Tuning Cost Management](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/fine-tuning-cost-management)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/)
- [Save Big on Fine-Tuning with Azure OpenAI](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/save-big-on-hosting-your-fine-tuned-models-on-azure-openai-service/4195386)
- [Fine-Tuning Costs: OpenAI vs Azure OpenAI](https://vladiliescu.net/finetuning-costs-openai-vs-azure-openai/)
- [OpenAI Pricing in 2026](https://www.finout.io/blog/openai-pricing-in-2026)
- [Fine-Tuning LLMs on Small Datasets](https://www.sapien.io/blog/strategies-for-fine-tuning-llms-on-small-datasets)
- [OpenAI Fine-Tuning Best Practices](https://platform.openai.com/docs/guides/fine-tuning-best-practices)

### Memory Frameworks
- [Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory (arXiv)](https://arxiv.org/abs/2504.19413)
- [Mem0 GitHub](https://github.com/mem0ai/mem0)
- [Mem0 Research — 26% Accuracy Boost](https://mem0.ai/research)
- [OpenAI Cookbook: Context Engineering for Personalization](https://cookbook.openai.com/examples/agents_sdk/context_personalization)
- [OpenAI Agents SDK Memory Reference](https://openai.github.io/openai-agents-python/ref/memory/)
- [Mem0 + OpenAI Agents SDK Integration](https://docs.mem0.ai/integrations/openai-agents-sdk)

### Framework Comparisons
- [AI Agent Memory: Comparative Analysis of LangGraph, CrewAI, AutoGen](https://dev.to/foxgem/ai-agent-memory-a-comparative-analysis-of-langgraph-crewai-and-autogen-31dp)
- [Mastering LangGraph State Management in 2025](https://sparkco.ai/blog/mastering-langgraph-state-management-in-2025)
- [Microsoft Agent Framework: Convergence of AutoGen and Semantic Kernel](https://cloudsummit.eu/blog/microsoft-agent-framework-production-ready-convergence-autogen-semantic-kernel)
- [Top AI Agent Frameworks 2026](https://www.lindy.ai/blog/best-ai-agent-frameworks)

### LoRA Multi-Tenant Serving
- [AWS SageMaker Multi-Tenant LoRA Serving](https://aws.amazon.com/blogs/machine-learning/efficient-and-cost-effective-multi-tenant-lora-serving-with-amazon-sagemaker/)
- [LoRAServe: Serving Heterogeneous LoRA Adapters](https://arxiv.org/abs/2511.22880)
- [EdgeLoRA: Multi-Tenant LLM Serving on Edge Devices](https://arxiv.org/abs/2507.01438)
- [Anyscale Multi-LoRA Serving](https://docs.anyscale.com/llm/serving/multi-lora)
- [Overcoming LLM Scaling Challenges with LoRA](https://www.kaboom.ai/blog/overcoming-llm-scaling-challenges-building-personalized-ai-with-lora)

### RAG vs Fine-Tuning
- [RAG vs Fine-Tuning: Cost Game Long-Term](https://dev.to/remojansen/rag-vs-fine-tuning-which-one-wins-the-cost-game-long-term-12dg)
- [RAG vs Fine-Tuning for Help Centers (2025)](https://www.eesel.ai/blog/rag-vs-fine-tuning-for-help-centers)
- [RAG vs Fine-Tuning: Enterprise AI Strategy Guide](https://www.matillion.com/blog/rag-vs-fine-tuning-enterprise-ai-strategy-guide)
- [LLM Fine-Tuning vs RAG vs Agents: Practical Comparison](https://mitrix.io/blog/llm-fine%E2%80%91tuning-vs-rag-vs-agents-a-practical-comparison/)

### Retraining Pipelines
- [Automating LLM Retraining and Fine-Tuning Pipelines](https://apxml.com/courses/mlops-for-large-models-llmops/chapter-6-advanced-llmops-systems-workflows/automating-llm-retraining)
- [Re-training Strategy for Fine-Tuned LLMs](https://www.linkedin.com/pulse/re-training-strategy-fine-tuned-llms-debmalya-biswas-o63te)
- [Model Retraining 2026: Why & How](https://research.aimultiple.com/model-retraining/)

### Dynamic Prompting & Personalization
- [Optimizing AI Agents with Dynamic Few-Shot Prompting](https://medium.com/@stefansipinkoski/optimizing-ai-agents-with-dynamic-few-shot-prompting-585919f694cc)
- [Dynamic Context-Aware Prompt Recommendation](https://arxiv.org/html/2506.20815)
- [OpenAI Cookbook: Context Personalization](https://cookbook.openai.com/examples/agents_sdk/context_personalization)
- [Reinforced Prompt Personalization for Recommendation (ACM)](https://dl.acm.org/doi/10.1145/3716320)

### Production Case Studies
- [Sierra AI — Agent OS 2.0](https://sierra.ai/blog/agent-os-2-0)
- [Intercom — Fin AI Agent](https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained)
- [Zendesk AI Service Desk](https://www.zendesk.com/service/help-desk-software/ai-help-desk/)
- [AI Agent Productivity 2026](https://research.aimultiple.com/ai-agent-productivity/)
- [Customer Experience Predictions 2026](https://www.cxtoday.com/contact-center/customer-experience-predictions-2026/)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
