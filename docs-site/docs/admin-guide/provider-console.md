---
sidebar_position: 20
title: Provider Console
---

# Provider Console

The Provider console is a platform-level administration dashboard for service providers operating Agent Red on behalf of multiple tenants (merchants). It provides operational monitoring, compliance oversight, and tenant management capabilities.

## Accessing the Provider console

Navigate to `/admin/provider/` and sign in with your provider API key. If MFA is enabled, you'll also need to enter a TOTP code from your authenticator app.

## Dashboard pages

The Provider console organizes its pages into four navigation groups:

### Overview
- **Health Dashboard** — Real-time system health metrics, uptime indicators, and resource utilization.
- **Tenant Directory** — List of all provisioned tenants with status, tier, and configuration health. Includes a "Create Tenant" action for manually provisioning new tenants with auto-activation and optional superadmin key generation.

### Operations
- **Deployment History** — Chronological log of production deployments with revision numbers and rollback status.
- **Queue Health** — Real-time depth and throughput metrics for all background processing queues.
- **Integration Health** — Health check status for external service connections (Shopify, Stripe, Azure OpenAI, etc.).
- **Status Page** — Active incidents and overall system status. The public endpoint (`/api/status`) requires no authentication.

### Compliance & Security
- **Alert Configuration** — Define threshold-based alert rules for queue depth, secret expiry, circuit breaker trips, SLA breaches, and incidents. Configure notification channels and cooldown periods.
- **Compliance Dashboard** — Configuration compliance scoring across all tenants with remediation tracking.
- **Secret Posture** — Key Vault secret rotation status, expiry dates, and renewal recommendations.
- **Billing Health** — Stripe subscription status, payment failures, and revenue metrics across tenants.
- **SLA Trends** — Historical SLA performance with error budget tracking and trend visualization.

### Account
- **MFA Settings** — Enable, disable, and manage TOTP-based two-factor authentication.

## Alerting engine

The alerting engine evaluates metric thresholds every 5 minutes using 6 built-in collectors:

| Rule type | Description |
|-----------|-------------|
| `queue_depth` | Fires when a processing queue exceeds the configured depth threshold. |
| `secret_expiry` | Fires when a Key Vault secret is within the configured days-to-expiry window. |
| `circuit_breaker` | Fires when an external service circuit breaker trips. |
| `sla_breach` | Fires when SLA error budget drops below the configured percentage. |
| `incident` | Fires on new incident creation or severity escalation. |

Each rule supports a cooldown period to prevent alert fatigue.

## Incident management

Create, acknowledge, update, and resolve incidents from the Status Page. Incidents follow a lifecycle:

**Open** → **Acknowledged** → **Resolved**

Each status change is timestamped and logged. Active incidents are visible on the public status endpoint.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
