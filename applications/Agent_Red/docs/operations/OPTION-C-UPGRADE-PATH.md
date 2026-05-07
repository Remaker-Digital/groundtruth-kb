# Option C Upgrade Path — Geo-Replication

> **WI #156 / WI #62**: Document the upgrade path from Option A (single region + backup) to Option C (geo-replication).

## Current Architecture (Option A)

- **Single region**: East US 2
- **Cosmos DB**: Serverless, continuous 7-day PITR
- **Archival**: Warm (Blob Cool, 90d) → Cold (Blob Archive, 7+ years)
- **RTO**: Enterprise 4hr, Professional 8hr, Starter 24hr
- **Monthly cost**: ~$252-436

## Trigger Criteria

Upgrade to Option C when **any** of the following conditions are met:

| Trigger | Threshold | Rationale |
|---------|-----------|-----------|
| Tenant count | 50+ active tenants | Revenue supports geo-replication cost (~$200-300/mo additional) |
| Enterprise tenants | 5+ Enterprise tenants | Enterprise SLA (99.95% uptime, 4hr RTO) is hard to guarantee single-region |
| Revenue | >$25,000 MRR | Infrastructure investment justified at this revenue level |
| Regulatory | EU/APAC tenant demand | Data residency requirements for GDPR/regional compliance |
| Incident | >1 regional outage in 12 months | Pattern indicates single-region risk is material |

## Option C Architecture

### Cosmos DB Multi-Region

```hcl
# dr_security.tf — add geo_location block
resource "azurerm_cosmosdb_account" "main" {
  # ... existing config ...

  geo_location {
    location          = "eastus2"
    failover_priority = 0
  }

  geo_location {
    location          = "westus2"
    failover_priority = 1
  }

  # Enable multi-region writes if needed
  enable_multiple_write_locations = false  # Start with single-write
}
```

**Cost impact**: ~$100-150/mo additional for Cosmos DB replication (serverless RU charges apply to both regions).

### Container Apps — Secondary Region

Deploy identical Container Apps environment in West US 2:

```bash
# Create secondary resource group
az group create --name agntcy-prod-westus2-rg --location westus2

# Deploy secondary Container Apps environment
az containerapp env create \
  --name agntcy-prod-westus2-env \
  --resource-group agntcy-prod-westus2-rg \
  --location westus2
```

**Cost impact**: ~$100-150/mo for secondary containers (can run at reduced scale until failover).

### Traffic Manager

Add Azure Traffic Manager for DNS-based failover:

```hcl
resource "azurerm_traffic_manager_profile" "main" {
  name                = "agntcy-prod-tm"
  resource_group_name = "agntcy-prod-rg"

  traffic_routing_method = "Priority"

  dns_config {
    relative_name = "agntcy-api"
    ttl           = 60
  }

  monitor_config {
    protocol = "HTTPS"
    port     = 443
    path     = "/health"
  }
}
```

### Revised RTO Targets

| Tier | Option A RTO | Option C RTO |
|------|-------------|-------------|
| Enterprise | 4 hours | <15 minutes (automatic failover) |
| Professional | 8 hours | <30 minutes |
| Starter | 24 hours | <1 hour |

## Migration Steps

1. **Prepare** (Week 1):
   - Enable Cosmos DB geo-replication to West US 2
   - Verify data sync (monitor replication lag in Azure Portal)
   - Create secondary Container Apps environment (scaled to 0)

2. **Deploy** (Week 2):
   - Deploy all 9 containers to secondary region at min scale
   - Configure Traffic Manager with East US 2 primary, West US 2 secondary
   - Update Application Gateway to point to Traffic Manager

3. **Validate** (Week 3):
   - Run failover drill (disable East US 2 endpoint in Traffic Manager)
   - Verify all APIs respond from West US 2
   - Measure failover time and data consistency
   - Re-enable East US 2 as primary

4. **Operationalize** (Week 4):
   - Update runbooks with Option C procedures
   - Schedule quarterly failover drills
   - Update SLA documentation with improved RTO targets
   - Notify Enterprise tenants of improved SLA

## Cost Summary

| Component | Option A (Current) | Option C (Geo-Rep) | Delta |
|-----------|-------------------|--------------------|----|
| Cosmos DB | ~$50-100/mo | ~$150-250/mo | +$100-150 |
| Container Apps | ~$150-250/mo | ~$250-400/mo | +$100-150 |
| Traffic Manager | $0 | ~$5/mo | +$5 |
| **Total** | **~$252-436/mo** | **~$455-655/mo** | **+$200-300** |

At 50+ tenants with mixed tiers, platform revenue exceeds $10,000 MRR, making the ~$200-300/mo investment in geo-replication (<3% of revenue) clearly justified.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
