# Zero-Knowledge Shared-Nothing Architecture Plan

**Document Type:** Architecture Decision & Implementation Plan
**Status:** DRAFT — Owner decisions recorded, awaiting implementation review
**Author:** Claude (Prime Builder, Opus 4.6)
**Date:** 2026-03-23
**Session:** Handoff document for fresh-session review
**Governing Specifications:** SPEC-1843, SPEC-1844, SPEC-1644, SPEC-1840
**Related Work Items:** WI-0321 (auth regression), WI-0320 (widget domain restriction)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Legal Mandate & Threat Model](#2-legal-mandate--threat-model)
3. [Current State Assessment](#3-current-state-assessment)
4. [Architecture Plan: Four Pillars](#4-architecture-plan-four-pillars)
   - [Pillar 1: Application-Level Envelope Encryption](#pillar-1-application-level-envelope-encryption)
   - [Pillar 2: Operator-Blind Key Management](#pillar-2-operator-blind-key-management)
   - [Pillar 3: SPA Admin API Surface Remediation](#pillar-3-spa-admin-api-surface-remediation)
   - [Pillar 4: Audit Log Sanitization](#pillar-4-audit-log-sanitization)
5. [Detailed File-Level Impact Analysis](#5-detailed-file-level-impact-analysis)
6. [Deployment Strategy & Phasing](#6-deployment-strategy--phasing)
7. [Migration Plan for Existing Tenants](#7-migration-plan-for-existing-tenants)
8. [Cost & Performance Impact](#8-cost--performance-impact)
9. [Open Decisions for Owner](#9-open-decisions-for-owner)
10. [Verification & Acceptance Criteria](#10-verification--acceptance-criteria)
11. [Risk Register](#11-risk-register)
12. [Appendix A: SPA Endpoint Audit Detail](#appendix-a-spa-endpoint-audit-detail)
13. [Appendix B: Encryption Field Inventory](#appendix-b-encryption-field-inventory)

---

## 1. Executive Summary

The owner has mandated a **shared-nothing, zero-knowledge architecture** where the
platform operator (Remaker Digital) is cryptographically unable to read tenant data.
This is driven by legal liability: if the operator CAN access tenant data, the operator
becomes legally responsible for tenant actions.

**Four specifications govern this mandate:**

| Spec | Title | Status | Priority |
|------|-------|--------|----------|
| SPEC-1843 | Platform operator MUST NOT read tenant data | specified | critical |
| SPEC-1844 | Platform operator MUST NOT access tenant API keys | specified | critical |
| SPEC-1644 | API keys MUST NOT identify tenants | implemented (broken deploy) | critical |
| SPEC-1840 | Widget keys MUST be domain-restricted | specified | high |

**Current reality:** The codebase has strong tenant isolation at the data-partition layer
(Cosmos partition key = tenant_id, repository-layer scoping), but the platform operator
retains broad access through: (a) Azure Portal access to Cosmos DB (service-managed
encryption means data is plaintext to the account owner), (b) 60+ SPA admin API endpoints
that perform cross-partition reads exposing tenant conversations, customer emails, secret
inventories, and TOTP seeds, (c) audit logs containing unsanitized PII, and (d) API key
generation endpoints that return raw keys in the HTTP response body.

**This plan proposes four pillars of remediation**, each independently valuable,
collectively achieving the zero-knowledge mandate.

---

## 2. Legal Mandate & Threat Model

### 2.1 Legal Reasoning (SPEC-1843)

The core legal argument:

> If Remaker Digital physically cannot decrypt tenant data — because decryption requires
> a tenant-specific key that is only unwrapped during authenticated tenant requests — then
> Remaker Digital cannot be held legally responsible for tenant actions performed through
> the platform.

This is not about preventing external attackers (standard security handles that). This is
about preventing the **platform operator from having technical capability** to access
tenant data, even if they wanted to.

### 2.2 Threat Model: "Honest but Capable" Operator

| Threat | Current Exposure | Target State |
|--------|-----------------|--------------|
| Operator reads tenant conversations via Azure Portal | **EXPOSED** — service-managed encryption, operator has Cosmos RBAC | BLOCKED — application-level encryption, operator cannot decrypt |
| Operator reads tenant data via SPA API | **EXPOSED** — 6+ endpoints return tenant-internal data | BLOCKED — endpoints return only aggregate metrics |
| Operator sees API keys during generation | **EXPOSED** — raw key in HTTP response body | BLOCKED — key delivered directly to tenant email |
| Operator enumerates tenant secrets | **EXPOSED** — `GET /secrets/posture` lists all | BLOCKED — endpoint removed or returns only health flags |
| Operator reads audit logs with PII | **EXPOSED** — `details` field unsanitized | BLOCKED — sanitizer strips PII before write |
| Operator reads TOTP seeds | **EXPOSED** — raw Key Vault name access | BLOCKED — TOTP seeds encrypted with tenant DEK |
| Azure support reads Cosmos data | **EXPOSED** — Microsoft holds service encryption keys | MITIGATED — application-level encryption makes data opaque |

### 2.3 What the Operator MAY Still See

The following are **permissible** for platform operation and do not violate the mandate:

- Tenant count, tier distribution, billing channel distribution
- Aggregate conversation volume (total across all tenants)
- System health: error rates, latency percentiles, uptime
- Tenant existence (tenant_id, creation date, tier, status)
- Billing metadata (Stripe customer ID, subscription status)
- Infrastructure metrics (Cosmos RU consumption, NATS throughput)

---

## 3. Current State Assessment

### 3.1 Cosmos DB Encryption

**Current:** Azure service-managed encryption (Microsoft-owned keys, automatic).
- Cosmos DB account: `cosmos-agentred-eastus` (serverless, NoSQL)
- Database: `agentred`, 20 containers (see CLAUDE-ARCHITECTURE.md)
- Partition key: `/tenant_id` for all tenant-scoped containers
- No Customer-Managed Key (CMK) currently active
- Terraform variable `enable_cmk` exists but is optional and defaults to off

**Impact:** Anyone with Cosmos DB RBAC read access (including Remaker Digital via Azure
Portal) can read ALL tenant data in plaintext. The encryption protects against Azure
infrastructure compromise, NOT against the account owner.

### 3.2 Key Vault Secrets

**Current:** Per-tenant secrets stored with naming convention `tenant-{id}-{type}`.
- 11 secret types defined in `TenantSecretType` enum
- Key Vault RBAC grants container apps Get/UnwrapKey/WrapKey
- `CMK_KEY_ID` type exists (line 75 of tenant_secret_service.py) but is unused
- Dev-mode fallback to in-memory store (unencrypted, shared)

**Impact:** Application code can enumerate and read all tenant secrets. The SPA API
`GET /secrets/posture` calls `list_tenant_secrets(tid)` for every tenant.

### 3.3 Integration Credential Encryption

**Current:** Two-layer envelope encryption implemented in `src/integrations/credential_vault.py`.
- Master KEK in Key Vault at `integration-master-kek`
- Per-tenant DEK derived from KEK, stored encrypted in Cosmos `integration_credentials`
- Fernet encryption (AES-128-CBC + HMAC-SHA256)
- DEK rotation interval: 90 days

**This is the right pattern.** Pillar 1 extends this to ALL tenant data, not just
integration credentials.

### 3.4 API Key Generation

**Current:** Two paths exist for key generation:

1. **Tenant-facing** (`admin_apikey_api.py`):
   - `POST /api/admin/api-keys` → returns `ApiKeyGeneratedResponse` with `api_key` field (line 93)
   - `POST /api/admin/api-keys/rotate` → same response model
   - `POST /api/admin/api-keys/reset` → sends key via email (already compliant!)

2. **SPA-facing** (superadmin_api/_platform.py):
   - `POST /platform-admin/regenerate-key` → returns `RegenerateKeyResponse` with raw key
   - Tenant provisioning (`_tenants.py` line 462) generates widget keys during tenant creation

**Impact:** When the platform operator triggers key generation via the SPA console, the
raw key appears in the HTTP response. SPEC-1844 says the operator must never see it.

### 3.5 SPA Admin API Surface

**Current:** 60+ endpoints across 13 submodules in `superadmin_api/`. Full audit in
Appendix A. Critical violations:

| Endpoint | File:Line | Data Exposed |
|----------|-----------|--------------|
| `GET /secrets/posture` | _dashboard.py:813-993 | All tenant secret types, TOTP seeds, metadata |
| `GET /pipeline/tenants/{id}/metrics` | _platform.py:514-544 | Recent conversations with intent + timestamps |
| `GET /costs` | _operations.py:945-1081 | Conversation messages, KB article counts |
| `GET /pipeline/tenants` | _platform.py:425-511 | Customer emails, brand names, usage |
| `GET /abuse/signals` | _operations.py:1134-1257 | Per-tenant conversation error patterns |
| `GET /tenants` | _tenants.py:179-250 | Customer emails, Shopify domains |

### 3.6 Audit Logs

**Current:** Append-only audit log in Cosmos (`audit_log` container, partition: `/time_partition`).
- 12 event types defined
- `details` field is a free-form dict — NOT auto-scrubbed
- Config changes scrub PII-classified fields, but custom details are unvalidated
- SPA can query all audit events cross-partition via `GET /audit`
- 1-year retention (Decision #13)

### 3.7 MCP Credential Cache

**Current:** In-memory Python dict, 5-minute TTL, 500-entry max.
- Credentials held in plaintext in application memory
- Container compromise exposes all cached credentials
- Partitioned by `(tenant_id, secret_type)` tuple

---

## 4. Architecture Plan: Four Pillars

### Pillar 1: Application-Level Envelope Encryption

#### 4.1.1 Why Not Cosmos CMK?

Azure Cosmos DB's native CMK feature encrypts the entire account with a single key that
the account owner controls. This protects against Azure infrastructure compromise but
does **NOT** prevent the account owner (Remaker Digital) from reading data — the CMK
just moves key custody from Microsoft to Remaker Digital.

For true zero-knowledge, we need **application-level encryption** where data is encrypted
before it reaches Cosmos, and the decryption keys are bound to **tenant identity**, not
operator identity.

Alternative considered: **One Cosmos account per tenant.** This provides native isolation
but costs ~$25/month per account minimum (serverless minimum throughput charges) and
creates operational complexity (N accounts to manage). Not viable at scale.

#### 4.1.2 Envelope Encryption Design

```
                    ┌──────────────────────────────────────┐
                    │        Azure Key Vault (HSM)         │
                    │                                       │
                    │  Master KEK (RSA-2048, HSM-backed)   │
                    │  ├── wrap(tenant-abc-dek) → wrapped  │
                    │  └── unwrap(wrapped) → tenant-abc-dek│
                    └──────────────────────────────────────┘
                                    │
                         wrap / unwrap operations
                                    │
                    ┌──────────────────────────────────────┐
                    │     Per-Tenant DEK (AES-256-GCM)     │
                    │                                       │
                    │  Stored: Key Vault secret             │
                    │    Name: tenant-{id}-dek              │
                    │    Value: wrapped(DEK) by Master KEK  │
                    │                                       │
                    │  Cached: Application memory (5 min)   │
                    │    Unwrapped DEK for active tenants   │
                    └──────────────────────────────────────┘
                                    │
                         encrypt / decrypt operations
                                    │
                    ┌──────────────────────────────────────┐
                    │        Cosmos DB Documents            │
                    │                                       │
                    │  { "tenant_id": "abc",               │
                    │    "id": "conv-123",                  │
                    │    "type": "conversation",            │
                    │    "_encrypted": {                    │
                    │      "messages": "base64(ciphertext)",│
                    │      "customer_intent": "base64(...)",│
                    │      "nonce": "base64(12-byte-nonce)" │
                    │    },                                 │
                    │    "message_count": 7,     ← CLEAR   │
                    │    "started_at": "2026-...", ← CLEAR  │
                    │    "status": "completed"    ← CLEAR   │
                    │  }                                    │
                    └──────────────────────────────────────┘
```

#### 4.1.3 Encryption Scope by Collection

| Container | Encrypted Fields | Clear Fields (for indexing/querying) |
|-----------|-----------------|--------------------------------------|
| `conversations` | `messages`, `customer_intent`, `escalation_reason`, `transcript` | `tenant_id`, `id`, `status`, `started_at`, `ended_at`, `message_count`, `billing_status` |
| `knowledge_bases` | `content`, `title`, `description`, `source_text` | `tenant_id`, `id`, `category`, `status`, `created_at`, `updated_at`, `embedding_status` |
| `customer_profiles` | `name`, `email`, `phone`, `address`, `notes`, `preferences` | `tenant_id`, `id`, `created_at`, `updated_at`, `segment` |
| `memory_vectors` | `chunk_text`, `source_conversation_id` | `tenant_id`, `id`, `embedding` (vector index needs clear), `created_at` |
| `preferences` | `custom_config`, `webhook_urls`, `notification_settings` | `tenant_id`, `id`, `version`, `updated_at` |
| `team_members` | `email`, `name`, `totp_seed_ref` | `tenant_id`, `id`, `role`, `status`, `created_at` |
| `tenants` | `customer_email`, `shopify_shop_domain`, `brand_name` | `tenant_id`, `id`, `status`, `tier`, `billing_channel`, `created_at` |
| `audit_log` | `details`, `actor`, `customer_id` | `time_partition`, `event_type`, `timestamp`, `tenant_id` |

**Note on vector search:** `memory_vectors.embedding` must remain unencrypted for DiskANN
vector index to function. The embedding alone does not reveal plaintext content — it is a
3072-dimensional float array. The `chunk_text` that generated it IS encrypted.

#### 4.1.4 Implementation: New Module `envelope_encryption.py`

**Location:** `src/multi_tenant/envelope_encryption.py`

**Public API:**

```python
class EnvelopeEncryptionService:
    """Per-tenant envelope encryption using Azure Key Vault HSM."""

    async def get_tenant_dek(self, tenant_id: str) -> bytes:
        """Retrieve and unwrap the tenant's DEK. Cached 5 minutes."""

    async def create_tenant_dek(self, tenant_id: str) -> None:
        """Generate a new AES-256-GCM DEK, wrap with KEK, store in KV."""

    async def rotate_tenant_dek(self, tenant_id: str) -> None:
        """Generate new DEK, re-encrypt all tenant data, retire old DEK."""

    def encrypt_fields(
        self, dek: bytes, document: dict, field_names: list[str],
    ) -> dict:
        """Encrypt specified fields in-place. Returns modified document."""

    def decrypt_fields(
        self, dek: bytes, document: dict,
    ) -> dict:
        """Decrypt all fields in document['_encrypted']. Returns modified document."""
```

**Encryption algorithm:** AES-256-GCM (authenticated encryption with associated data).
- 256-bit key (the DEK)
- 96-bit random nonce per document write
- AAD (Additional Authenticated Data): `tenant_id + document_id` to bind ciphertext
  to its document and prevent cross-document substitution attacks
- Library: `cryptography` (already in requirements.txt for Fernet usage)

#### 4.1.5 Repository Layer Integration

**Modified file:** `src/multi_tenant/repositories/base.py`

The `TenantScopedRepository` base class gains two hooks:

```python
class TenantScopedRepository:
    async def _pre_write(self, tenant_id: str, document: dict) -> dict:
        """Hook: encrypt sensitive fields before Cosmos write."""
        if self._encryption_fields:
            svc = get_envelope_encryption_service()
            dek = await svc.get_tenant_dek(tenant_id)
            return svc.encrypt_fields(dek, document, self._encryption_fields)
        return document

    async def _post_read(self, tenant_id: str, document: dict) -> dict:
        """Hook: decrypt sensitive fields after Cosmos read."""
        if document.get("_encrypted"):
            svc = get_envelope_encryption_service()
            dek = await svc.get_tenant_dek(tenant_id)
            return svc.decrypt_fields(dek, document)
        return document
```

Each repository subclass declares `_encryption_fields`:

```python
class ConversationRepository(TenantScopedRepository):
    _encryption_fields = ["messages", "customer_intent", "escalation_reason", "transcript"]
```

#### 4.1.6 DEK Lifecycle

| Event | Action |
|-------|--------|
| Tenant provisioned | `create_tenant_dek()` → new AES-256-GCM key, wrapped by KEK, stored as `tenant-{id}-dek` |
| Tenant request (any) | `get_tenant_dek()` → unwrap from cache or Key Vault |
| DEK rotation (90 days) | `rotate_tenant_dek()` → new DEK, re-encrypt all documents, retire old |
| Tenant deprovisioned | DEK deleted from Key Vault → all tenant data becomes permanently unreadable |
| Master KEK rotation | All wrapped DEKs re-wrapped with new KEK (Key Vault handles this natively) |

---

### Pillar 2: Operator-Blind Key Management

#### 4.2.1 Current Key Generation Flow (VIOLATES SPEC-1844)

```
Operator → POST /api/superadmin/tenants/{id}/provision
         → generate_api_key(tenant_id) → raw key
         → Response body: { "api_key": "ar_live_tn8f3c_AbCdEf..." }  ← OPERATOR SEES KEY
```

#### 4.2.2 Target Key Generation Flow

```
Operator → POST /api/superadmin/tenants/{id}/trigger-key-generation
         → generate_api_key(tenant_id) → raw key
         → send_api_key_email(tenant_email, raw_key) → email sent
         → key = None  (scrubbed from memory after email send)
         → Response body: { "status": "delivered", "to": "m***@example.com" }  ← OPERATOR SEES NOTHING
```

#### 4.2.3 Endpoints to Modify

| Endpoint | File | Current Behavior | Target Behavior |
|----------|------|-----------------|-----------------|
| `POST /api/superadmin/tenants` (provisioning) | `_tenants.py:380-520` | Returns API key + widget key in response | Trigger email delivery, response contains only masked email |
| `POST /api/superadmin/tenants/{id}/secrets/rotate` | `_tenants.py:540-600` | Returns new key in response | Trigger email delivery of new key |
| `POST /platform-admin/regenerate-key` | `_platform.py:883-977` | Returns new SPA key in response | **Exception:** SPA keys are operator keys — operator MAY see their own key (this is NOT a tenant key) |
| `POST /api/admin/api-keys` | `admin_apikey_api.py:190-250` | Returns key to authenticated tenant | **No change needed** — tenant is requesting their own key via their own authenticated session |
| `POST /api/admin/api-keys/rotate` | `admin_apikey_api.py:432-480` | Returns key to authenticated tenant | **No change needed** — same reasoning |

**Key insight:** SPEC-1844 applies to **operator-triggered** key generation for tenants.
Tenant-facing endpoints where the tenant authenticates and requests their own key are
already compliant — the tenant sees their own key, not the operator.

#### 4.2.4 Email Delivery Implementation

The email delivery infrastructure already exists:

- `admin_apikey_api.py:169-180` — `_send_api_key_email()` function (SMTP primary, ACS fallback)
- `alert_delivery.py` — shared email wrapper for visual consistency

**Changes required:**
1. Provisioning flow (`_tenants.py`) calls `_send_api_key_email()` instead of returning key
2. Response models updated to remove `api_key` field, add `delivered_to` (masked) field
3. Audit log records key generation event WITHOUT the key value

#### 4.2.5 Widget Key Domain Restriction (SPEC-1840)

Widget keys (`pk_live_*`) are visible in page source. Protection:

1. **Tenant registers approved domains** via admin dashboard (`PUT /api/config`)
2. **Server validates Origin header** on every widget API request
3. **CORS `Access-Control-Allow-Origin`** header returns only the requesting origin IF it
   matches an approved domain; otherwise no CORS header (browser blocks the request)
4. **Fallback:** If no domains registered, widget key works from any origin (backward compat
   during migration period, with deprecation warning)

**Implementation:** Add `approved_widget_origins: list[str]` to tenant config schema.
Modify `TenantAuthMiddleware._auth_widget_key()` in `middleware.py` to check Origin
against the list.

---

### Pillar 3: SPA Admin API Surface Remediation

#### 4.3.1 Remediation Matrix

| Priority | Endpoint | Violation | Remediation | Effort |
|----------|----------|-----------|-------------|--------|
| **P0** | `GET /secrets/posture` | Full secret inventory + TOTP seeds | **Remove endpoint entirely.** Replace with `GET /health/secrets` returning only: `{ "tenants_with_api_key": 12, "tenants_with_widget_key": 10, "tenants_missing_keys": 2 }` — no per-tenant detail | S |
| **P0** | `GET /pipeline/tenants/{id}/metrics` | `recent_conversations` with intent | **Remove `recent_conversations` field** from `TenantDetailMetrics` response. Keep: `total_conversations`, `avg_latency_ms`, `error_rate`, `escalation_rate` | XS |
| **P1** | `GET /costs` | Queries `c.messages` from conversation repo | **Replace** Cosmos query with pre-aggregated counters. Query ONLY: `SELECT c.id, c.message_count, c.started_at FROM c WHERE ...` — never access `c.messages` | M |
| **P1** | `GET /pipeline/tenants` | `customer_email`, `brand_name` | **Redact** PII: return `tenant_id`, `tier`, `status`, aggregate metrics only. Remove `customer_email` and `brand_name` from response model | S |
| **P1** | `GET /abuse/signals` | Per-tenant conversation error details | **Aggregate:** Return risk score + category only, not per-conversation status | S |
| **P1** | `GET /tenants` | `customer_email`, `shopify_shop_domain` | **Mask:** `m***@domain.com`, `***.myshopify.com` | S |
| **P2** | `GET /dashboard` | `tenant_summary()` detail | **Verify** only aggregate counts (by_status, by_tier). Should already be safe. | XS |
| **P2** | `GET /billing/health` | Per-tenant billing reconciliation | **Aggregate:** Return overall billing health score, not per-tenant detail | S |

Effort: XS = < 1 hour, S = 1-3 hours, M = 3-8 hours

#### 4.3.2 New Design Principle (Updated per Owner Decision 4)

Add to SPA API module docstring and enforce in code review:

> **Zero-Knowledge API Design Rule:** SPA endpoints MUST NOT return any data that would
> disclose a tenant's proprietary content, user identities, or business secrets. Tenant
> data exposed to the SPA is **cleansed**: operational metadata only, never content or PII.
>
> **Permitted (operational metadata):** Per-tenant conversation count, error rate,
> escalation rate, cost attribution, billing status, resource utilization metrics,
> tier, status, billing_channel, creation date. System-wide aggregates (total MRR,
> fleet error rate, infrastructure health). Tenant-initiated disclosures (admin
> messages to the platform operator).
>
> **Prohibited (content and PII):** Conversation messages, customer intent text,
> escalation reasons, knowledge base articles/titles, customer PII (email, name,
> phone, address), team member identities, TOTP seeds, API key values, Shopify
> domains, brand names, webhook URLs, or any other proprietary tenant data.
>
> **Principle:** Operational metadata MUST NOT include PII or proprietary tenant data
> (textual inputs, knowledge articles, user identities, API keys), but MAY include
> metadata that describes activity/resource utilization and the operational state of
> the tenancy.

#### 4.3.3 Provider Console Frontend Impact

The Provider Console SPA (20 pages, `admin/provider/`) consumes these endpoints. Pages
affected:

| Page | Endpoint Used | Impact |
|------|--------------|--------|
| Dashboard | `GET /dashboard` | P2 — likely already safe |
| Tenant List | `GET /tenants` | P1 — email/domain masking will appear in UI |
| Tenant Detail → Secrets | `GET /secrets/posture` | P0 — page section must be removed or replaced with health summary |
| Pipeline Overview | `GET /pipeline/tenants` | P1 — email/brand columns removed |
| Pipeline Detail | `GET /pipeline/tenants/{id}/metrics` | P0 — recent conversations section removed |
| Cost Analysis | `GET /costs` | P1 — cost calculation method changes |
| Abuse Detection | `GET /abuse/signals` | P1 — detail view replaced with risk score |

**Frontend file:** `admin/provider/pages/DeploymentManagement.tsx` is already modified
(per git status). Other pages need corresponding updates.

---

### Pillar 4: Audit Log Sanitization

#### 4.4.1 Sanitization Gate

**New module:** `src/multi_tenant/audit_sanitizer.py`

All audit log writes pass through a sanitizer before persistence:

```python
ALLOWED_DETAIL_FIELDS = {
    "action", "resource_type", "resource_id", "result", "reason",
    "old_value_hash", "new_value_hash",  # hash, not value
    "count", "duration_ms", "status_code",
}

PII_PATTERNS = [
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # email
    r"ar_live_\w+",  # API key
    r"pk_live_\w+",  # widget key
    r"ar_spa_\w+",   # SPA key
    r"sk_\w+",       # Stripe key
    r"shpat_\w+",    # Shopify token
]

def sanitize_audit_details(details: dict) -> dict:
    """Strip PII and restrict to allow-listed fields."""
    sanitized = {}
    for key, value in details.items():
        if key not in ALLOWED_DETAIL_FIELDS:
            continue
        if isinstance(value, str):
            for pattern in PII_PATTERNS:
                value = re.sub(pattern, "[REDACTED]", value)
        sanitized[key] = value
    return sanitized
```

#### 4.4.2 SPA Audit Query Restriction

**Modified:** `admin_audit_api.py` and `superadmin_api/_operations.py`

- SPA audit query returns: `event_type`, `timestamp`, `tenant_id` (ID only, not email),
  `action` (from sanitized details)
- `details` field NEVER returned in cross-partition (SPA) queries
- Per-tenant audit queries (tenant admin dashboard) return full sanitized details

#### 4.4.3 Audit Log Encryption

With Pillar 1 active, audit log `details` and `actor` fields are encrypted with the
tenant's DEK. Cross-partition queries return only the clear-text metadata fields.

**Special case:** Platform-level audit events (e.g., deployment, SPA login) use a
platform DEK (not tenant-scoped). These are visible to the operator because they
describe operator actions, not tenant actions.

---

## 5. Detailed File-Level Impact Analysis

### 5.1 New Files

| File | Purpose | Estimated Lines |
|------|---------|----------------|
| `src/multi_tenant/envelope_encryption.py` | Envelope encryption service (KEK/DEK, encrypt/decrypt) | ~400 |
| `src/multi_tenant/audit_sanitizer.py` | Audit log PII sanitization gate | ~150 |
| `src/jobs/run_dek_rotation.py` | Cron job: rotate tenant DEKs every 90 days | ~100 |
| `src/jobs/run_data_encryption_migration.py` | One-time job: encrypt existing tenant data | ~250 |
| `tests/multi_tenant/test_envelope_encryption.py` | Unit tests for encryption service | ~300 |
| `tests/multi_tenant/test_audit_sanitizer.py` | Unit tests for sanitization | ~150 |
| `tests/security/test_zero_knowledge.py` | Integration tests: verify operator cannot read tenant data | ~200 |

### 5.2 Modified Files

| File | Changes | Risk |
|------|---------|------|
| `src/multi_tenant/repositories/base.py` | Add `_pre_write` / `_post_read` encryption hooks | MEDIUM — touches all data paths |
| `src/multi_tenant/repositories/conversation.py` | Declare `_encryption_fields` | LOW |
| `src/multi_tenant/repositories/knowledge.py` | Declare `_encryption_fields` | LOW |
| `src/multi_tenant/repositories/customer.py` | Declare `_encryption_fields` | LOW |
| `src/multi_tenant/repositories/memory.py` | Declare `_encryption_fields` (exclude `embedding`) | LOW |
| `src/multi_tenant/repositories/preferences.py` | Declare `_encryption_fields` | LOW |
| `src/multi_tenant/repositories/team.py` | Declare `_encryption_fields` | LOW |
| `src/multi_tenant/repositories/tenant.py` | Declare `_encryption_fields` | LOW |
| `src/multi_tenant/cosmos_schema.py` | Add `_encrypted` field to document models | LOW |
| `src/multi_tenant/superadmin_api/_dashboard.py` | Remove/replace `GET /secrets/posture` | LOW |
| `src/multi_tenant/superadmin_api/_platform.py` | Remove `recent_conversations`; redact PII | LOW |
| `src/multi_tenant/superadmin_api/_operations.py` | Fix `GET /costs` query; aggregate abuse signals | MEDIUM |
| `src/multi_tenant/superadmin_api/_tenants.py` | Mask PII; blind key delivery | MEDIUM |
| `src/multi_tenant/admin_apikey_api.py` | No change (tenant-facing, already compliant) | NONE |
| `src/multi_tenant/middleware.py` | Add Origin validation for widget keys (SPEC-1840) | MEDIUM |
| `src/multi_tenant/tenant_secret_service.py` | Add DEK secret type; adjust list_tenant_secrets | LOW |
| `src/multi_tenant/admin_audit_api.py` | Integrate sanitizer; restrict SPA query | LOW |
| `src/integrations/provisioning.py` | Blind key delivery during provisioning | MEDIUM |
| `src/app/lifecycle.py` | Wire envelope encryption service at startup | LOW |
| `admin/provider/pages/*.tsx` | Remove/update UI for redacted endpoints | MEDIUM |
| `infrastructure/terraform/dr_security.tf` | Enforce CMK; add HSM-backed KEK policy | LOW |

### 5.3 Files NOT Changed

| File | Reason |
|------|--------|
| `admin_apikey_api.py` | Tenant-facing — tenant sees their own key (compliant) |
| `auth.py` | Hash functions unchanged; auth flow unchanged |
| `cosmos_client.py` | Cosmos connection unchanged (encryption is at application layer) |
| `mcp_credential_cache.py` | Cache already partitioned by tenant_id (P3 hardening later) |
| `credential_vault.py` | Integration credentials already have envelope encryption |

---

## 6. Deployment Strategy & Phasing

### Phase 0: Immediate (no code changes, < 1 day)

1. **Feature-flag block** P0 endpoints:
   - Set env var `DISABLE_SECRETS_POSTURE=true` → `GET /secrets/posture` returns 404
   - Set env var `DISABLE_RECENT_CONVERSATIONS=true` → response omits field
2. **Deploy v1.98.18** (WI-0321 fix already committed):
   - lifecycle.py exception handling fix
   - Fallback SPA resolver ensures platform console survives Cosmos failures

### Phase 1: SPA API Remediation + Audit Sanitization (Sprint 1, ~1 week)

1. Create `audit_sanitizer.py`
2. Integrate sanitizer into audit log write path
3. Remediate all P0 and P1 SPA endpoints (see matrix in 4.3.1)
4. Update Provider Console frontend pages
5. Deploy SPEC-1840 widget domain restriction (WI-0320)
6. **141 existing tests must still pass** (no behavioral regression)
7. Add ~30 new zero-knowledge assertion tests

### Phase 2: Operator-Blind Key Management (Sprint 2, ~3 days)

1. Modify provisioning flow for blind key delivery
2. Update response models (remove `api_key` field from SPA responses)
3. Test email delivery reliability (SMTP + ACS fallback)
4. Update Provider Console provisioning wizard UI
5. Add ~15 new tests for key delivery flow

### Phase 3: Envelope Encryption (Sprint 3, ~2 weeks)

1. Create `envelope_encryption.py`
2. Provision Master KEK in Key Vault (HSM-backed)
3. Modify repository base class with encryption hooks
4. Declare encryption fields per repository
5. Deploy dual-mode reads (handles encrypted + unencrypted)
6. **Batch migration:** Maintenance window, encrypt all existing tenant data
7. Add DEK rotation cron job
8. **This is the highest-risk phase** — touches all data read/write paths
9. Add ~50 new encryption tests

### Phase 4: Verification & Hardening (Sprint 4, ~3 days)

1. Run full test suite (6,053 offline + 141 SPEC-1644 tests)
2. Penetration test: operator account attempts to read tenant data
3. Verify Azure Portal shows only ciphertext for encrypted fields
4. Document emergency decryption procedure (if legally compelled)
5. Update SPEC-1843 and SPEC-1844 status to `implemented`
6. Owner review and approval for `verified` promotion

---

## 7. Migration Plan for Existing Tenants

### 7.1 Strategy: Batch Migration (Owner Decision: maintenance window acceptable)

**Batch approach** (tenants are free/beta, brief downtime acceptable):

1. **Pre-migration:** Deploy encryption-aware code with dual-mode reads (handles both
   encrypted and unencrypted documents). Verify in staging.

2. **Migration window (~30 minutes):**
   - Announce maintenance to beta tenants
   - Scale API to zero replicas (no concurrent writes)
   - Run `run_data_encryption_migration.py` — iterates all tenants sequentially,
     generates DEK per tenant, encrypts all sensitive fields in all documents
   - Validation pass: scan for remaining unencrypted documents (expect zero)
   - Scale API back up

3. **Post-migration:** All documents encrypted. Dual-mode reads handle any edge cases.
   Run smoke test suite against each tenant.

### 7.2 Migration Job Design

```python
async def migrate_tenant(tenant_id: str, svc: EnvelopeEncryptionService):
    """Encrypt all existing documents for a single tenant."""
    dek = await svc.get_tenant_dek(tenant_id)
    for collection_name, fields in ENCRYPTION_MANIFEST.items():
        repo = get_repository(collection_name)
        async for doc in repo.iterate_all(tenant_id):
            if doc.get("_encrypted"):
                continue  # already encrypted
            encrypted = svc.encrypt_fields(dek, doc, fields)
            await repo.upsert(tenant_id, encrypted)
```

### 7.3 Rollback

If encryption causes issues:
1. The `_post_read` hook checks for `_encrypted` field — unencrypted documents read
   normally without any decryption attempt
2. To roll back: deploy code without encryption hooks. Encrypted documents become
   unreadable until hooks are re-enabled.
3. **Emergency decryption:** A standalone script can decrypt all documents given the
   Master KEK. This script is NOT deployed to production — it exists only in a
   secure offline repository for legal/compliance scenarios.

---

## 8. Cost & Performance Impact

### 8.1 Key Vault Costs

| Operation | Volume | Cost |
|-----------|--------|------|
| DEK unwrap (per tenant request) | ~100K/month (cached, so ~1K actual KV calls) | ~$0.03/month |
| DEK creation (new tenants) | ~50/month | Negligible |
| DEK rotation (quarterly) | ~200 tenants × 1 unwrap + 1 wrap | Negligible |
| Master KEK operations | Rare (only for DEK wrap/unwrap) | Negligible |
| **Total Key Vault increment** | | **~$0.50/month** |

### 8.2 Compute Costs

| Operation | Latency Impact |
|-----------|---------------|
| AES-256-GCM encrypt (per document write) | +0.1-0.5ms |
| AES-256-GCM decrypt (per document read) | +0.1-0.5ms |
| DEK cache miss (Key Vault unwrap) | +50-100ms (amortized over 5-min cache window) |
| **Net impact per request** | **+0.5-2ms** (within noise for Cosmos latency ~5-15ms) |

### 8.3 Storage Costs

Encrypted fields are ~33% larger (base64 encoding of ciphertext + 12-byte nonce + 16-byte
auth tag). For a typical conversation document with 2KB of messages:

- Plaintext: 2,000 bytes
- Encrypted: ~2,700 bytes (+35%)
- Cosmos DB cost: ~$0.25/GB/month serverless → negligible per-document

### 8.4 Migration Costs (One-Time)

Estimating ~10,000 existing documents across all tenants:
- Cosmos RU for read + write: ~20,000 RU total → ~$0.05 at serverless rates
- Key Vault operations: ~10,000 unwrap calls → ~$0.30
- **Total migration cost: < $1.00**

### 8.5 Workflow Latency Impact Analysis (Owner-Requested)

This section traces the exact Cosmos operations for two critical user-facing workflows
and calculates the cumulative encryption overhead.

#### 8.5.1 Tenant Admin: Inbox Page Load

**Baseline (no encryption):**

| # | Operation | Type | Container | Baseline Latency |
|---|-----------|------|-----------|-----------------|
| 1 | `count_filtered()` — conversation count | Query | conversations | ~5-10ms |
| 2 | `list_filtered()` — conversation list (50 items) | Query | conversations | ~10-20ms |
| 3 | Team members query | Query | team_members | ~5-10ms |
| | **Total (parallel: 1+2 sequential, 3 parallel)** | | | **~15-30ms Cosmos** |

**With encryption (Pillar 1):**

| # | Operation | Encryption Overhead | Notes |
|---|-----------|-------------------|-------|
| 1 | count_filtered | **+0ms** | Count queries don't return document bodies — no decryption needed |
| 2 | list_filtered (50 docs) | **+2.5-5ms** | 50 documents × 0.05-0.1ms decrypt each (AES-256-GCM is hardware-accelerated) |
| 3 | Team members | **+0.5-1ms** | ~10 team members × 0.05-0.1ms decrypt each |
| DEK | Cache hit (5-min TTL) | **+0ms** | DEK already cached from prior request |
| DEK | Cache miss (cold start) | **+50-100ms** | One-time per tenant per 5-minute window |
| | **Added overhead (warm cache)** | **+3-6ms** | |
| | **Added overhead (cold start)** | **+53-106ms** | First request only |

**Inbox page load total:**
- **Warm:** ~18-36ms (was ~15-30ms) — **+3-6ms, imperceptible to user**
- **Cold start:** ~68-136ms (was ~15-30ms) — **+53-106ms on first load only**, then cached

**Polling (every 5 seconds):** Each poll decrypts 50 conversation summaries. The DEK is
cached, so overhead is +3-6ms per poll. At 12 polls/minute, that's +36-72ms of cumulative
CPU time per minute — trivial.

**When user selects a conversation:**
- +1 point read (conversation detail): +0.1ms decrypt
- Messages array decrypt: +0.5-2ms depending on conversation length (10-100 messages)
- **Total for conversation selection: +0.6-2.1ms**

#### 8.5.2 Widget Chat: Customer Message → AI Response

**Baseline operations traced from codebase:**

| Phase | Operation | Type | Container | Parallelizable |
|-------|-----------|------|-----------|---------------|
| **Message Receipt** | | | | |
| 1 | Read conversation (turn limit check) | Point read | conversations | - |
| 2 | Read preferences (activation check) | Point read | preferences | Yes with #1 |
| 3 | Append customer message | Write (patch) | conversations | Sequential |
| **Stream Open** | | | | |
| 4 | Read conversation state | Point read | conversations | - |
| 5 | Read tenant document | Point read | tenants | Yes with #4 |
| 6 | Read preferences (prompt context) | Point read | preferences | Yes with #4 |
| 7 | Customer profile warm-up | Point read | customer_profiles | Background |
| **Pipeline (parallel phase)** | | | | |
| 8 | Customer profile fetch | Point read | customer_profiles | Yes |
| 9 | Memory vector search (Layer 2) | Vector search | memory_vectors | Yes |
| 10 | Knowledge vector search (KB) | Vector search | knowledge_bases | Yes |
| **Response** | | | | |
| 11 | Append AI response | Write (patch) | conversations | Sequential |
| 12 | Pipeline trace metadata | Write (patch) | conversations | Fire-and-forget |

**Total: 10 reads + 3 writes per chat round-trip**

**Encryption overhead per operation:**

| Operation | Encrypt/Decrypt? | Overhead |
|-----------|-----------------|----------|
| #1 Read conversation | Decrypt messages, intent | +0.5-2ms |
| #2 Read preferences | Decrypt custom_config | +0.05ms |
| #3 Write message | Encrypt message content | +0.05-0.1ms |
| #4 Read conversation | Decrypt (same as #1, cached in-process) | +0ms (cached) |
| #5 Read tenant | Decrypt email, domain, brand | +0.05ms |
| #6 Read preferences | Decrypt (cached from #2) | +0ms (cached) |
| #7 Profile warm-up | Decrypt PII fields | +0.1ms (background) |
| #8 Profile fetch | Decrypt (cached from #7) | +0ms (cached) |
| #9 Memory vector search | Decrypt chunk_text (5 results) | +0.25ms |
| #10 KB vector search | Decrypt content (3-5 results) | +0.25-0.5ms |
| #11 Write AI response | Encrypt response content | +0.1-0.5ms |
| #12 Write trace | Encrypt trace details | +0.05ms (fire-and-forget) |
| **Total encryption overhead** | | **+1.3-3.5ms** |

**Context: What dominates chat latency?**

| Component | Typical Latency | % of Total |
|-----------|----------------|-----------|
| Azure OpenAI intent classification (gpt-4o-mini) | 200-500ms | 10-15% |
| Azure OpenAI text embedding (2 calls) | 100-200ms | 5-10% |
| Azure OpenAI response generation (gpt-4o, streaming) | 800-3000ms | 50-70% |
| Azure OpenAI critic validation | 200-500ms | 10-15% |
| Cosmos DB reads (10 operations, partially parallel) | 30-80ms | 3-5% |
| Cosmos DB writes (3 operations) | 15-30ms | 1-2% |
| **Encryption overhead** | **1.3-3.5ms** | **< 0.2%** |
| **Total typical chat round-trip** | **1500-4000ms** | |

**Conclusion:** Encryption adds +1.3-3.5ms to a 1500-4000ms chat round-trip. This is
**0.1-0.2% of total latency** and is completely imperceptible to the end user. The
bottleneck is and will remain Azure OpenAI inference, which accounts for 75-90% of
the round-trip time.

#### 8.5.3 Summary: Human-Observed Impact

| Workflow | Current Latency | With Encryption | Delta | Perceptible? |
|----------|----------------|-----------------|-------|-------------|
| Inbox page load (warm) | ~200-400ms total | ~203-406ms | +3-6ms | **No** |
| Inbox page load (cold) | ~200-400ms total | ~253-506ms | +53-106ms | **Barely** (first load only) |
| Conversation detail | ~50-100ms | ~51-102ms | +0.6-2ms | **No** |
| Chat round-trip | 1500-4000ms | 1501-4004ms | +1.3-3.5ms | **No** |
| Inbox poll (5s interval) | ~30-60ms | ~33-66ms | +3-6ms | **No** |
| KB article retrieval | ~20-40ms | ~20.5-41ms | +0.25-0.5ms | **No** |

**The only scenario where encryption overhead might be noticed** is the very first
request for a tenant after a 5-minute cache expiry (DEK unwrap from Key Vault: +50-100ms).
This happens once per tenant per 5-minute window, not per request. For an active tenant
with steady traffic, it occurs at most 12 times per hour.

---

## 9. Owner Decisions (Recorded 2026-03-23)

### Decision 1: Encryption Field Scope → OPTION A (Sensitive fields only)

**Selected:** Encrypt only sensitive fields (messages, PII, credentials). Clear metadata
fields remain queryable. This is the approach described in this plan.

**Owner note:** Acceptable latency. See Section 8.5 for detailed workflow impact analysis.

### Decision 2: Email Provider for Key Delivery → ACS (Azure Communication Services)

**Selected:** Azure Communication Services — already in the Azure stack, used for SMS
verification (SPEC-1686). No additional vendor dependency.

**Rejected:** SendGrid. While it offers better deliverability tracking and dedicated IP
options, it adds another vendor dependency, another billing relationship, another set of
API credentials to manage, and another potential PII-processing third party subject to
its own DPA/privacy obligations. ACS is already in-stack, already covered by our Azure
DPA, and the marginal deliverability improvement does not justify the complexity.

### Decision 3: Existing Tenant Data Migration → BATCH (maintenance window)

**Selected:** Maintenance-window batch encryption. Tenants are currently free/beta so a
brief downtime window is acceptable. Simpler code, deterministic completion, easier to
verify all documents were encrypted.

**Migration procedure:**
1. Announce maintenance window to beta tenants (30-minute window)
2. Scale API to zero replicas
3. Run `run_data_encryption_migration.py` — iterates all tenants, encrypts all documents
4. Validation pass: scan for any remaining unencrypted documents
5. Scale API back up
6. Verify via smoke tests

### Decision 4: SPA Dashboard Operational Visibility → MAXIMUM ANONYMIZATION

**Owner directive (verbatim):** "The SPA Console is limited to the information exposed by
the tenants, i.e., the tenant's privacy is the highest priority: we prefer that everything
the SPA can access is anonymized, aggregated and cleansed of information that would
disclose the tenant's activities, users, products, chat messages, etc."

**Implementation principle:** The SPA console operates on a zero-knowledge basis for tenant
*content and PII*, while retaining full visibility into *operational metadata*. Tenants may
export cleansed data; the operator may gather per-tenant metrics, verify billing, monitor
errors, and receive admin messages. Specifically:

| Data Category | SPA May See (operational metadata) | SPA Must NOT See (content/PII) |
|--------------|-------------|-----------------|
| **Tenant identity** | tenant_id (UUID), tier, status, billing_channel, created_at | customer_email, brand_name, shopify_shop_domain |
| **Conversations** | Per-tenant conversation count, error rate, escalation rate, latency | Conversation messages, customer intent text, escalation reasons, transcripts |
| **Knowledge bases** | Per-tenant article count, embedding status | Article content, titles, descriptions, source text |
| **Customer profiles** | Per-tenant customer count | Any customer PII (name, email, phone, address, notes) |
| **Team members** | Per-tenant member count | Names, emails, roles, TOTP seeds, MFA status |
| **Secrets** | Aggregate health ("N tenants have complete key setup") | Per-tenant secret types, TOTP seeds, API key values |
| **Usage** | Per-tenant and system-wide conversation counts, resource utilization | Textual content of any kind |
| **Audit logs** | Platform-level events (deployments, SPA logins), per-tenant event counts | Tenant-scoped event details, actor identities, PII in details |
| **Billing** | Per-tenant billing status, cost attribution, aggregate MRR, churn rate | Stripe customer details beyond subscription status |
| **Admin messages** | Tenant-initiated messages to the platform operator | N/A (tenant chose to disclose) |

**Clarification (Owner, 2026-03-23):** Operational metadata MUST NOT include PII or
proprietary tenant data (textual inputs, knowledge articles, user identities, API keys),
but MAY include metadata that describes activity/resource utilization and the operational
state of the tenancy.

### Decision 5: Emergency Decryption → DEFERRED (requires legal counsel)

**Status:** Not decided. Owner will consult legal counsel on CLOUD Act and subpoena
obligations before selecting between:
- Option A: Offline two-person decryption capability
- Option B: "Technically unable to comply"

**Implementation note:** The architecture supports both options. The Master KEK can be
placed in an HSM with or without an offline backup. The decision can be made after
Pillar 1 is implemented without any code changes.

---

## 10. Verification & Acceptance Criteria

### 10.1 Per-Specification Acceptance

**SPEC-1843 (operator cannot read tenant data):**
- [ ] Cosmos DB documents contain ciphertext in sensitive fields (verified via Azure Portal)
- [ ] SPA API endpoints return no tenant-internal data (verified by test suite)
- [ ] Audit logs contain no PII in cross-partition queries (verified by test suite)
- [ ] Operator cannot decrypt data without tenant's DEK (verified by key isolation test)

**SPEC-1844 (operator cannot access tenant API keys):**
- [ ] Provisioning flow delivers key via email, not HTTP response (verified by test)
- [ ] SPA rotation endpoints deliver key via email (verified by test)
- [ ] No audit log entry contains raw key value (verified by sanitizer test)
- [ ] Operator-facing API responses contain only masked email confirmation

**SPEC-1644 (API keys do not identify tenants):**
- [ ] All 141 existing tests pass (including 21 HTTP intrusion tests)
- [ ] v1.98.18 deploys successfully with lifecycle.py fix
- [ ] Cross-partition key lookups return deprecation warnings in logs

**SPEC-1840 (widget keys domain-restricted):**
- [ ] Origin header validated against approved domains list
- [ ] CORS headers returned only for approved origins
- [ ] Unapproved origins receive 403 Forbidden
- [ ] No domains configured → key works from any origin (backward compat with warning)

### 10.2 Integration Test Scenarios

| Test | Method | Pass Criteria |
|------|--------|---------------|
| Operator reads Cosmos via Portal | Manual | Sensitive fields show base64 ciphertext |
| SPA `GET /tenants` | Automated | Email masked as `m***@domain.com` |
| SPA `GET /secrets/posture` | Automated | Returns 404 or aggregate-only health |
| SPA `GET /pipeline/tenants/{id}/metrics` | Automated | No `recent_conversations` in response |
| SPA `GET /costs` | Automated | No `messages` field in Cosmos query |
| Provisioning creates tenant | Automated | Response has no `api_key` field; email sent |
| Audit log cross-partition query | Automated | No `details` field in response |
| Widget request from unapproved origin | Automated | 403 + no CORS headers |
| DEK rotation | Automated | Old DEK retired; data re-encrypted; reads succeed |
| Tenant deletion | Automated | DEK deleted; data permanently unreadable |

---

## 11. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Encryption breaks existing queries | Medium | High | Extensive test coverage; encrypt-on-write allows gradual rollout |
| Key Vault outage blocks all reads | Low | Critical | 5-minute DEK cache; circuit breaker falls back to cached DEK |
| Migration job corrupts data | Low | High | Dry-run mode; per-document validation; Cosmos PITR backup |
| Performance regression from encryption | Low | Medium | AES-256-GCM is hardware-accelerated on Azure VMs; benchmarks before deploy |
| Email delivery failure for API keys | Medium | Medium | Dual provider (SMTP + ACS); retry with exponential backoff; audit trail |
| Operator loses ability to troubleshoot | Medium | Medium | Aggregate metrics preserved; tenant can grant temporary access via debug token |
| Legal challenge to zero-knowledge claim | Low | High | External legal review of architecture; maintain technical documentation |
| DEK loss renders data unrecoverable | Very Low | Critical | Key Vault soft-delete + purge protection (90-day retention); backup KEK in HSM |

---

## Appendix A: SPA Endpoint Audit Detail

### Critical Violations (P0)

**1. GET /secrets/posture** (`_dashboard.py:813-993`)
- Calls `_secret_service.list_tenant_secrets(tid)` for each active tenant
- Returns per-tenant `TenantSecretInfo` with: secret types, metadata (created_at,
  updated_at, disabled), Shopify/Stripe integration flags, API key presence,
  TOTP seed counts
- Iterates team members to check for TOTP seeds via Key Vault raw name access

**2. GET /pipeline/tenants/{id}/metrics** (`_platform.py:514-544`)
- Returns `TenantDetailMetrics` with `recent_conversations` list
- Each conversation includes: ID, timestamp, customer intent, latency, critic
  pass/fail, LLM execution details

### High Violations (P1)

**3. GET /costs** (`_operations.py:945-1081`)
- Cosmos query: `SELECT c.id, c.message_count, c.messages FROM c WHERE ...`
- Accesses `c.messages` (full conversation content) for token estimation
- Returns per-tenant cost attribution with conversation metadata

**4. GET /pipeline/tenants** (`_platform.py:425-511`)
- Cross-partition query returns: customer_email, brand_name, conversation counts,
  cost attribution, error rates, escalation rates

**5. GET /abuse/signals** (`_operations.py:1134-1257`)
- Per-tenant conversation error patterns from last 24h
- Conversation status and volume metrics per tenant

**6. GET /tenants** (`_tenants.py:179-250`)
- Cross-partition listing: customer_email, shopify_shop_domain, billing_channel,
  consent_status, deactivation dates

### Full Endpoint Inventory

(60+ endpoints across _tenants.py, _dashboard.py, _operations.py, _platform.py,
_copilot.py, _entitlements.py, _blocklists.py, _rate_limits.py, _alerts.py,
_diagnostics.py, _feedback.py, _quality.py, _deployments.py)

See Section 4.3 for the remediation matrix for affected endpoints.

---

## Appendix B: Encryption Field Inventory

### Conversations Container

| Field | Encrypted? | Reason |
|-------|-----------|--------|
| `messages` | YES | Contains customer conversation text |
| `customer_intent` | YES | Reveals what customer asked about |
| `escalation_reason` | YES | May contain customer complaint details |
| `transcript` | YES | Full conversation transcript |
| `tenant_id` | NO | Partition key — must be queryable |
| `id` | NO | Document ID — must be queryable |
| `status` | NO | Query filter for active/completed |
| `started_at` | NO | Query filter for date ranges |
| `ended_at` | NO | Query filter for date ranges |
| `message_count` | NO | Aggregate metric — no PII |
| `billing_status` | NO | Billing reconciliation |

### Knowledge Bases Container

| Field | Encrypted? | Reason |
|-------|-----------|--------|
| `content` | YES | Merchant's proprietary product/FAQ data |
| `title` | YES | May reveal business-sensitive categories |
| `description` | YES | May contain proprietary information |
| `source_text` | YES | Raw uploaded document text |
| `tenant_id` | NO | Partition key |
| `id` | NO | Document ID |
| `category` | NO | Aggregate categorization |
| `status` | NO | Workflow state |
| `embedding_status` | NO | Processing state |

### Customer Profiles Container

| Field | Encrypted? | Reason |
|-------|-----------|--------|
| `name` | YES | PII |
| `email` | YES | PII |
| `phone` | YES | PII |
| `address` | YES | PII |
| `notes` | YES | May contain sensitive details |
| `preferences` | YES | Customer behavior data |
| `tenant_id` | NO | Partition key |
| `id` | NO | Document ID |
| `segment` | NO | Aggregate classification |

### Memory Vectors Container

| Field | Encrypted? | Reason |
|-------|-----------|--------|
| `chunk_text` | YES | Conversation excerpt text |
| `source_conversation_id` | YES | Links to conversation content |
| `embedding` | NO | DiskANN vector index requires clear float array |
| `tenant_id` | NO | Partition key |
| `id` | NO | Document ID |

### Team Members Container

| Field | Encrypted? | Reason |
|-------|-----------|--------|
| `email` | YES | PII |
| `name` | YES | PII |
| `totp_seed_ref` | YES | MFA credential reference |
| `tenant_id` | NO | Partition key |
| `id` | NO | Document ID |
| `role` | NO | Access control |
| `status` | NO | Account state |

### Tenants Container

| Field | Encrypted? | Reason |
|-------|-----------|--------|
| `customer_email` | YES | PII |
| `shopify_shop_domain` | YES | Business identity |
| `brand_name` | YES | Business identity |
| `tenant_id` | NO | Partition key |
| `id` | NO | Document ID |
| `status` | NO | Operational state |
| `tier` | NO | Billing classification |
| `billing_channel` | NO | Billing routing |
| `created_at` | NO | Operational metadata |

---

*This document is a DRAFT. No implementation will begin until the owner reviews and
approves the approach, phasing, and open decisions.*

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
