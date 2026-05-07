# Persistent Customer Memory — Test Cases & Metrics Framework

| Attribute | Value |
|-----------|-------|
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-01-30 |
| **Owner** | Remaker Digital |
| **References** | [Research Foundation](PER-CUSTOMER-AI-PERSONALIZATION-RESEARCH.md) |

---

## 1. Metrics Framework

### 1.1 Direct Impact Metrics

These metrics are instrumented within Agent Red and measured automatically.

| Metric | Definition | Measurement Method | Layer(s) |
|--------|------------|-------------------|----------|
| **Repeat Explanation Rate** | % of conversations where the customer re-states information from a prior session | Semantic similarity (>0.85 threshold) between current message and prior session summaries | L1, L2 |
| **Context Accuracy Score** | % of memory-injected facts that are correct when verified against source data | Automated cross-check of injected profile fields against live integration data; sampled weekly | L1, L3 |
| **Memory Hit Rate** | % of conversations where at least one memory/context item was surfaced and used | Log whether response generator incorporated context from Layers 1-3; tag at generation time | L1, L2, L3 |
| **First-Contact Resolution Rate** | % of conversations resolved without escalation or follow-up within 72 hours | Conversation closure + absence of new conversation from same customer/intent within 72 hours | L1, L2, L3 |
| **Time-to-Resolution (TTR)** | Average elapsed time from first customer message to confirmed resolution | Timestamp difference: conversation.started → conversation.ended (automated resolution) | L1, L2 |
| **Escalation Rate** | % of conversations routed to human agents | Existing metric; segmented by memory-enabled vs. control | L1, L2, L3 |
| **Response Personalization Score** | Degree to which the response references customer-specific information | Count of personalization tokens (name, order refs, preference acknowledgements) / total responses | L1, L3 |
| **Average Handle Time (AHT)** | Average total conversation duration | Sum of message timestamps from first to last per conversation | L1, L2 |
| **Customer Effort Score (CES)** | Post-conversation survey: "How easy was it to get your issue resolved?" (1-5) | Optional inline survey widget | L1, L2, L3 |
| **CSAT Score** | Post-conversation satisfaction rating | Existing satisfaction survey; segmented by memory tier | All |

### 1.2 Layer 4 Specific Metrics

These metrics apply only to Enterprise customers with Dedicated Model Training enabled.

| Metric | Definition | Measurement Method |
|--------|------------|-------------------|
| **Style Match Score** | How closely the AI's communication style matches the customer's historical style | LLM-as-judge evaluation comparing response formality/verbosity/tone against customer profile |
| **Proactive Suggestion Accuracy** | % of proactive suggestions (upsell, tip, known-issue warning) the customer finds relevant | Track click-through on suggestions + explicit feedback |
| **Hallucination Rate Delta** | Change in hallucination rate between base model and fine-tuned model | Automated fact-check pipeline comparing response assertions against knowledge base |
| **Fine-Tune Quality Gate Pass Rate** | % of retraining cycles where the new model passes automated evaluation | Count of pass/fail outcomes in the retraining pipeline |

### 1.3 Business Outcome Metrics

These are measured by the customer and reported via the Agent Red analytics dashboard.

| Metric | Baseline Source | Target Improvement |
|--------|----------------|-------------------|
| Support cost per conversation | Customer's current cost (from ROI calculator) | 10-25% reduction attributable to memory |
| Customer retention / churn | Customer's existing churn rate | 5-15% reduction |
| Repeat contact rate (same issue) | 30-day window, same customer + same intent | 20-40% reduction |
| Support-influenced conversion rate | GA4 attribution | 5-15% improvement |

---

## 2. Test Cases

### 2.1 Layer 1: Customer Context (Structured Profile Injection)

| Test ID | Scenario | Input | Expected Behavior | Pass Criteria |
|---------|----------|-------|-------------------|---------------|
| L1-01 | **Returning customer greeting** | Customer with 5+ prior interactions sends "Hi, I need help" | AI greets by name, references plan tier, acknowledges relationship | Response contains customer first name and at least one profile-derived fact |
| L1-02 | **Plan-aware feature guidance** | Starter customer asks about a Professional feature | AI acknowledges current tier, explains feature availability, offers upgrade path | Response correctly identifies current tier AND does not hallucinate feature availability |
| L1-03 | **Integration-aware troubleshooting** | Customer with Shopify + Zendesk asks "my orders aren't syncing" | AI targets Shopify sync troubleshooting; references their specific integration config | Response references the customer's specific active integrations, not a generic list |
| L1-04 | **Communication style matching** | Customer profile says "casual, concise"; asks a pricing question | AI responds in casual tone with short sentences, no formal salutation | Flesch-Kincaid grade level <10 and word count <100 |
| L1-05 | **Empty profile handling** | New customer with no profile data asks a question | AI responds with high-quality generic response; no errors or placeholder text | Response is complete; does not contain "unknown", "N/A", or template remnants |
| L1-06 | **Stale profile detection** | Customer profile last updated 90+ days ago; plan has since changed | AI uses stale profile gracefully; triggers background profile refresh | No incorrect tier reference; system logs a refresh event |

### 2.2 Layer 2: Conversation Memory (Vectorized Transcript RAG)

| Test ID | Scenario | Input | Expected Behavior | Pass Criteria |
|---------|----------|-------|-------------------|---------------|
| L2-01 | **Prior conversation reference** | Customer who discussed a return 3 days ago says "Any update on my return?" | AI retrieves prior return conversation, references specific product and status | Response mentions the specific product from the prior conversation without re-statement |
| L2-02 | **Cross-session continuity** | Customer asks "Did you ever fix that webhook issue I reported?" (2 weeks ago) | AI retrieves the prior webhook discussion, provides current status | Response references the specific technical issue from the prior session |
| L2-03 | **Multi-topic history** | Customer with 10+ conversations asks "What did we discuss about my shipping policy?" | AI retrieves only shipping-policy-relevant conversations | Retrieved context is semantically relevant (>0.85 similarity); no unrelated topic mixing |
| L2-04 | **No relevant history** | Customer asks about a topic never discussed before | AI responds normally without hallucinating prior conversations | Response does not fabricate prior interactions |
| L2-05 | **Tenant isolation** | Cross-tenant query: Customer A's memory must not appear in Customer B's retrieval | Intentional cross-tenant query returns zero results | Zero documents from another tenant's partition; security audit log generated |
| L2-06 | **High-volume history search** | Customer with 500+ historical conversations asks about a specific old issue | Retrieval returns relevant results within latency budget | Vector search completes in <500ms; top result is semantically correct |

### 2.3 Layer 3: Cross-Session Learning (Memory Framework)

| Test ID | Scenario | Input | Expected Behavior | Pass Criteria |
|---------|----------|-------|-------------------|---------------|
| L3-01 | **Preference learning** | Customer has consistently asked for detailed technical explanations across 5+ sessions | AI proactively provides technical detail without being asked | Response verbosity and technical depth match extracted preference profile |
| L3-02 | **Recurring issue recognition** | Customer has reported the same webhook error 3 times in 30 days | AI acknowledges the pattern and suggests escalation or permanent fix | Response explicitly references the recurrence pattern |
| L3-03 | **Preference update** | Customer who preferred email now says "Can we just chat here instead?" | Memory framework updates communication preference | Profile updated within 1 session; next session reflects new preference |
| L3-04 | **Memory consolidation accuracy** | After 20 sessions, verify extracted memories are factually correct | Compare extracted memory facts against raw transcripts | >95% factual accuracy of memory entries vs. source transcripts |
| L3-05 | **Memory staleness handling** | Customer's business changed (new store, different products) | Memory framework detects context shift via semantic drift; triggers refresh | Old memories deprecated (not deleted); new memories weighted higher |
| L3-06 | **Escalation pattern recognition** | Customer has escalated 3 of last 5 interactions due to billing frustration | AI acknowledges pattern, offers direct CSM contact, adjusts tone | Response demonstrates awareness of escalation history; offers proactive resolution |

### 2.4 Layer 4: Dedicated Model Training (Enterprise Add-On)

| Test ID | Scenario | Input | Expected Behavior | Pass Criteria |
|---------|----------|-------|-------------------|---------------|
| L4-01 | **Style adaptation** | Customer's historical style is casual with emoji usage | Fine-tuned model matches casual + emoji communication style | LLM-as-judge style match score >0.8 (vs. <0.5 for base model) |
| L4-02 | **Domain vocabulary adoption** | Customer uses specific industry jargon consistently | Fine-tuned model uses the same jargon naturally | Response contains customer-specific terminology without prompt engineering |
| L4-03 | **Quality gate enforcement** | Fine-tuned model produces higher hallucination rate than baseline | Evaluation gate rejects the model; system falls back to base model + L1-L3 | Deployment blocked; alert generated; base model continues serving |
| L4-04 | **Retraining improvement** | Model retrained with 500 new interactions | New model scores equal or better on held-out test set | Quality metrics (BLEU/ROUGE, hallucination rate, style match) do not regress |
| L4-05 | **Data consent verification** | Customer has not opted into fine-tuning | System excludes their data from all training jobs | Training pipeline filters by consent flag; audit log confirms exclusion |
| L4-06 | **Insufficient data handling** | Customer requests fine-tuning but has only 50 interactions | System informs customer of 1,000-interaction minimum; offers timeline estimate | Clear message with interaction count and projected date to reach threshold |

### 2.5 Cross-Layer Integration Tests

| Test ID | Scenario | Layers Tested | Pass Criteria |
|---------|----------|--------------|---------------|
| CL-01 | **Full stack activation** | L1+L2+L3+L4 | Enterprise customer with all layers active; response quality scores higher than any single layer alone |
| CL-02 | **Graceful degradation** | L1+L2+L3 (L4 unavailable) | Fine-tuned model unavailable (retraining); system falls back to L1+L2+L3 with no user-facing error |
| CL-03 | **Layer conflict resolution** | L1 vs L3 | Context injection (L1) has stale data, memory framework (L3) has newer data; system prefers fresher source |
| CL-04 | **New customer onboarding** | L1 only (L2, L3 empty) | First conversation with zero history delivers quality baseline; profile creation begins |
| CL-05 | **Tier upgrade migration** | L1 → L1+L2+L3 | Customer upgrades from Starter to Professional; memory framework activates; existing data preserved |
| CL-06 | **Data deletion compliance** | All layers | Customer requests deletion; all profile data, memories, vectors, and fine-tuned models purged within SLA |

---

## 3. A/B Testing Methodology

### 3.1 Experimental Design

| Parameter | Value |
|-----------|-------|
| **Control group** | Standard six-agent pipeline, zero memory layers |
| **Treatment T1** | Layer 1 only (context injection) |
| **Treatment T2** | Layers 1+2 (context + transcript RAG) |
| **Treatment T3** | Layers 1+2+3 (context + RAG + memory framework) |
| **Treatment T4** | Layers 1+2+3+4 (full stack, Enterprise only) |
| **Assignment method** | Customer-level random assignment (not conversation-level) |
| **Minimum sample** | 100 customers per group |
| **Statistical power** | 80% at 5% significance level |
| **Detectable effect** | 10% relative improvement in primary metric |
| **Minimum duration** | 30 days (captures cross-session effects) |

### 3.2 Metrics Priority

| Priority | Metric | Rationale |
|----------|--------|-----------|
| **Primary** | First-contact resolution rate | Most objective, least survey-dependent |
| **Secondary** | CSAT, CES, escalation rate, repeat contact rate, TTR | Complementary quality and efficiency signals |
| **Exploratory** | Memory hit rate, personalization score, AHT | Mechanism validation |

### 3.3 Statistical Methods

| Metric Type | Test | Notes |
|-------------|------|-------|
| Binary (FCR, escalation rate) | Two-sample proportional z-test | Standard A/B comparison |
| Ordinal (CSAT, CES) | Mann-Whitney U test | Non-parametric for Likert scales |
| Continuous (TTR, AHT) | Bayesian A/B testing | Enables early stopping with posterior credible intervals |

### 3.4 Safeguards

- All treatment groups receive the full six-agent pipeline (no quality degradation)
- Control group receives standard Agent Red quality (already high baseline)
- Any treatment showing statistically significant **degradation** on any primary metric is halted immediately
- Customer assignment is sticky (no mid-experiment reassignment)

---

## 4. Benchmark Targets

Targets are set at 30-50% of maximum observed improvements in industry research to account for early implementation maturity.

| Metric | Baseline (No Memory) | L1 Target | L1+L2 Target | L1+L2+L3 Target | Full Stack Target |
|--------|---------------------|-----------|-------------|-----------------|-------------------|
| First-contact resolution | 70% | 75% (+7%) | 80% (+14%) | 85% (+21%) | 88% (+26%) |
| Repeat explanation rate | 40% | 25% (-38%) | 15% (-63%) | 8% (-80%) | 5% (-88%) |
| Escalation rate | 30% | 27% (-10%) | 23% (-23%) | 20% (-33%) | 18% (-40%) |
| CSAT score | 4.0/5.0 | 4.1 (+2.5%) | 4.3 (+7.5%) | 4.4 (+10%) | 4.5 (+12.5%) |
| Customer effort score | 3.5/5.0 | 3.3 (-6%) | 3.0 (-14%) | 2.8 (-20%) | 2.5 (-29%) |
| Average handle time | 120s | 110s (-8%) | 95s (-21%) | 85s (-29%) | 80s (-33%) |
| Time-to-resolution | 180s | 165s (-8%) | 140s (-22%) | 120s (-33%) | 110s (-39%) |

### Rationale

- **Sierra AI** Agent Data Platform achieves near-elimination of repeat explanations for SiriusXM
- **Mem0** memory framework shows 26% improvement on LOCOMO benchmark over OpenAI baseline
- **Blip** reports 80% AI-recommended reply acceptance with context-aware responses
- **Zendesk 2026 CX Trends**: 81% of consumers want representatives to pick up where they left off
- Targets are conservative (30-50% of maximum observed) to account for early implementation maturity

---

## 5. Dashboard Requirements

### 5.1 Memory Performance Panel

| Widget | Type | Data Source |
|--------|------|-------------|
| Memory Hit Rate (30-day trend) | Line chart | Response generator logs |
| Repeat Explanation Rate (30-day trend) | Line chart | Semantic similarity pipeline |
| Personalization Score (distribution) | Histogram | Response analysis |
| Context Accuracy (weekly sample) | Gauge | Automated cross-check pipeline |

### 5.2 Resolution Impact Panel

| Widget | Type | Data Source |
|--------|------|-------------|
| FCR Rate: Memory vs. No Memory | Bar comparison | A/B test segmentation |
| Escalation Rate (30-day trend) | Line chart | Escalation agent logs |
| TTR Distribution (memory-enabled) | Box plot | Conversation timestamps |
| AHT Trend (30-day) | Line chart | Conversation timestamps |

### 5.3 Customer Experience Panel

| Widget | Type | Data Source |
|--------|------|-------------|
| CSAT Score (30-day trend) | Line chart | Post-conversation survey |
| CES Score (30-day trend) | Line chart | Post-conversation survey |
| Repeat Contact Rate (30-day rolling) | Line chart | Conversation deduplication |
| Memory Layer Utilization (by tier) | Stacked bar | Memory system telemetry |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
