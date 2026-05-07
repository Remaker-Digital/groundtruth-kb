# Agent Red — Quarterly Cost Review Template

Run this review every quarter (Q1 Apr, Q2 Jul, Q3 Oct, Q4 Jan) to validate
that actual Azure spend matches cost_model.py projections.

---

## 1. Azure Billing Actuals

Pull from Azure Portal → Cost Management → Cost Analysis → Last 90 days,
filtered by Resource Group `agentred-prod-rg`.

| Category | Projected (cost_model.py) | Actual | Delta |
|----------|--------------------------|--------|-------|
| Container Apps (compute) | $___/mo | $___/mo | |
| Cosmos DB (RU + storage) | $___/mo | $___/mo | |
| Azure OpenAI (tokens) | $___/mo | $___/mo | |
| Key Vault (operations) | $___/mo | $___/mo | |
| Networking / Ingress | $___/mo | $___/mo | |
| Log Analytics | $___/mo | $___/mo | |
| **Total infrastructure** | $252-436/mo | $___/mo | |

## 2. Per-Conversation AI Cost

| Metric | Projected | Actual | Source |
|--------|-----------|--------|--------|
| Avg tokens per conversation | ~1,500 | | Azure OpenAI usage dashboard |
| Cost per conversation | $0.0073 | | Total AI spend / billable conversations |
| Response Generator % of AI cost | 94.5% | | GPT-4o spend / total AI spend |

## 3. Tenant Economics

| Metric | Value |
|--------|-------|
| Active tenants | |
| Total billable conversations (quarter) | |
| Revenue (quarter) | |
| Infrastructure cost (quarter) | |
| AI cost (quarter) | |
| **Gross margin** | |
| Projected gross margin (cost_model.py) | 76-90% |

## 4. Action Items

- [ ] Update cost_model.py if any category deviates >15% from projection
- [ ] Review KEDA scaling rules if compute spend exceeds projection
- [ ] Check semantic cache hit rate (should reduce AI cost over time)
- [ ] Evaluate night scaling enablement if off-hours compute is significant

---

## Reference

- `src/multi_tenant/cost_model.py` — Parameterized cost model
- `infrastructure/terraform/production.tfvars` — Resource configuration
- Azure Portal → Cost Management → agentred-prod-rg

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
