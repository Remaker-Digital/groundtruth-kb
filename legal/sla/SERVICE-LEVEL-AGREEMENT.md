# Agent Red Customer Engagement — Service Level Agreement

> **Status:** DRAFT — For internal review only. Not yet published.
> **Version:** 0.1.0
> **Last Updated:** 2026-01-29
> **Legal Review Required:** Yes — must be reviewed by qualified legal counsel before publication.

---

## Service Level Agreement (SLA)

**Effective Date:** [TO BE SET AT PUBLICATION]

This Service Level Agreement ("SLA") is part of the Terms of Service between VanDusen & Palmeter, LLC, doing business as Remaker Digital ("Company", "we", "us", or "our"), and you ("Customer") for the Agent Red Customer Engagement platform ("Service"). Capitalized terms not defined here have the meanings given in the Terms of Service.

---

### 1. Service Availability

#### 1.1 Uptime Commitment

We commit to the following monthly uptime targets based on your Subscription tier:

| Tier | Monthly Uptime Target |
|------|----------------------|
| **Starter** | 99.5% |
| **Professional** | 99.9% |
| **Enterprise** | 99.95% |

**"Uptime"** is calculated as the percentage of total minutes in a calendar month during which the Service is available, excluding Scheduled Maintenance and Excluded Events (defined in Section 4).

**Formula:**

```
Uptime % = ((Total Minutes - Downtime Minutes) / Total Minutes) × 100
```

#### 1.2 Downtime Equivalents

| Uptime | Maximum Monthly Downtime |
|--------|--------------------------|
| 99.95% | ~22 minutes |
| 99.9% | ~43 minutes |
| 99.5% | ~3 hours 36 minutes |

---

### 2. Performance Targets

#### 2.1 Response Time

We target the following API response times under normal operating conditions:

| Metric | Target |
|--------|--------|
| API Response Time (P50) | < 500 ms |
| API Response Time (P95) | < 2,000 ms |
| API Response Time (P99) | < 5,000 ms |

Response time is measured from receipt of the API request to delivery of the response, excluding network transit time outside our infrastructure.

#### 2.2 AI Processing Time

AI-generated responses involve external model processing and may have variable latency:

| Metric | Target |
|--------|--------|
| Simple inquiry response | < 3 seconds |
| Complex inquiry response | < 8 seconds |
| Knowledge retrieval query | < 2 seconds |

These targets represent best-effort goals and are not subject to Service Credits.

#### 2.3 Throughput

| Tier | Conversations per Day | Concurrent Requests |
|------|----------------------|---------------------|
| **Starter** | 500 | 10 |
| **Professional** | 2,000 | 50 |
| **Enterprise** | 10,000 | 200 |

---

### 3. Service Credits

#### 3.1 Eligibility

If we fail to meet the Monthly Uptime Target for your Subscription tier, you may be eligible for Service Credits, subject to the conditions in this section.

#### 3.2 Credit Schedule

| Monthly Uptime | Service Credit (% of Monthly Fee) |
|----------------|-----------------------------------|
| 99.0% – below target | 10% |
| 98.0% – 98.99% | 20% |
| 95.0% – 97.99% | 30% |
| Below 95.0% | 50% |

#### 3.3 Credit Limitations

- Service Credits are calculated as a percentage of the monthly Subscription fee for the affected month only
- Service Credits are applied to future invoices and are not redeemable for cash
- Maximum Service Credit for any single month shall not exceed 50% of the monthly Subscription fee for that month
- Service Credits are your sole and exclusive remedy for any failure to meet the uptime commitment

#### 3.4 How to Request Credits

To request a Service Credit:

1. Submit a request to support@remakerdigital.com within 30 days of the end of the affected month
2. Include the dates and times of the downtime events
3. We will verify the claim against our monitoring data and respond within 10 business days
4. Approved credits will be applied to your next invoice

---

### 4. Exclusions

The following are excluded from Uptime calculations and do not qualify for Service Credits:

#### 4.1 Scheduled Maintenance

- Routine maintenance performed during our maintenance window: **Sundays 02:00–06:00 UTC**
- We will provide at least 72 hours' notice for scheduled maintenance via email and in-Service notification
- We will use commercially reasonable efforts to limit scheduled maintenance to no more than 4 hours per month

#### 4.2 Excluded Events

The following events are excluded from Uptime calculations:

- **Force Majeure:** Events beyond our reasonable control, including natural disasters, pandemics, war, terrorism, government actions, or failure of third-party services (including but not limited to Microsoft Azure, Azure OpenAI Service, and internet service providers)
- **Customer-Caused Issues:** Downtime resulting from Customer's actions, code, integrations, or misuse of the Service
- **Planned Maintenance:** Maintenance performed during the scheduled maintenance window with proper notice
- **Emergency Maintenance:** Urgent maintenance required to address security vulnerabilities or prevent imminent service degradation (we will provide notice as soon as reasonably practicable)
- **Third-Party Integrations:** Unavailability of third-party services connected by the Customer (e.g., Shopify, Zendesk)
- **API Abuse:** Downtime caused by requests that exceed the rate limits or throughput limits of your Subscription tier
- **Beta Features:** Any features labeled as "Beta", "Preview", or "Experimental"

---

### 5. Support

#### 5.1 Support Channels

| Channel | Availability |
|---------|-------------|
| Email (support@remakerdigital.com) | All tiers |
| In-app support widget | All tiers |
| Priority support queue | Priority Support add-on |

#### 5.2 Response Times

| Severity | Description | Starter | Professional | Enterprise |
|----------|-------------|---------|--------------|------------|
| **Critical** | Service is completely unavailable | 4 hours | 2 hours | 1 hour |
| **High** | Major feature is non-functional | 8 hours | 4 hours | 2 hours |
| **Medium** | Feature is impaired but workaround exists | 24 hours | 12 hours | 8 hours |
| **Low** | General question or minor issue | 48 hours | 24 hours | 12 hours |

Response times are measured during business hours (Monday–Friday, 09:00–17:00 Eastern Time), except for Critical severity issues which are measured 24/7 for Enterprise tier.

Customers with the **Priority Support** add-on receive Professional-tier response times (or better, if already on Professional or Enterprise tier).

#### 5.3 Severity Definitions

- **Critical:** The Service is completely unavailable or a security breach has occurred. No workaround exists.
- **High:** A major feature of the Service is non-functional, significantly impacting business operations. No reasonable workaround exists.
- **Medium:** A feature is impaired but a workaround is available, or a non-critical feature is unavailable.
- **Low:** A general question, feature request, documentation issue, or minor cosmetic defect.

#### 5.4 Escalation

If you are not satisfied with the support response, you may escalate:

1. **Level 1:** Reply to the support ticket requesting escalation
2. **Level 2:** Email escalation@remakerdigital.com with the ticket reference
3. **Level 3:** Contact your Account representative (Enterprise tier)

---

### 6. Monitoring and Reporting

#### 6.1 Service Status

We maintain a public status page at [status.remakerdigital.com] (to be established) that displays:

- Current service status
- Active incidents
- Scheduled maintenance
- Historical uptime data

#### 6.2 Incident Communication

During service disruptions, we will:

- Post updates to the status page within 30 minutes of incident detection
- Provide updates at least every 60 minutes during ongoing incidents
- Publish a post-incident report within 5 business days for Critical and High severity incidents

#### 6.3 Monthly Reports

Enterprise tier Customers receive a monthly Service report including:

- Uptime percentage
- API performance metrics
- Conversation volume and trends
- Incident summary

---

### 7. Data Protection

#### 7.1 Backup and Recovery

| Aspect | Commitment |
|--------|-----------|
| **Backup Frequency** | Daily automated backups |
| **Backup Retention** | 30 days |
| **Recovery Point Objective (RPO)** | 24 hours |
| **Recovery Time Objective (RTO)** | 4 hours (Enterprise), 8 hours (Professional), 24 hours (Starter) |

#### 7.2 Data Durability

Customer Data stored in Azure Cosmos DB benefits from:

- Automatic replication within the Azure region
- Encryption at rest (AES-256)
- Point-in-time restore capability

#### 7.3 Data Export

Customers may export their data at any time through:

- The Service's built-in data export feature
- The API using their API Key
- Request to support@remakerdigital.com

---

### 8. Changes to This SLA

We may update this SLA from time to time. We will provide at least 30 days' notice of material changes. Changes will not apply retroactively and will take effect at the start of the next billing cycle following the notice period.

If a change materially reduces the service commitments, you may terminate your Subscription without penalty within 30 days of the change notification.

---

### 9. Contact

For SLA-related inquiries:

**VanDusen & Palmeter, LLC (DBA Remaker Digital)**
Email: support@remakerdigital.com
Website: https://remakerdigital.com

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

> **IMPORTANT NOTICE:** This document is an AI-generated draft provided for internal planning purposes only. It is NOT legal advice. This document must be reviewed and approved by qualified legal counsel before publication or use. Do not rely on this draft as a binding legal document.
