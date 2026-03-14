"""S178: Create P1 Integration Ecosystem specifications in Knowledge Database."""
import sys; sys.path.insert(0, 'tools/knowledge-db')
import db

kdb = db.KnowledgeDB()
specs_created = []

def cs(id, title, desc, priority="high", scope="backend", tags=None, assertions=None):
    import sqlite3
    try:
        row = kdb._conn.execute("SELECT id FROM specifications WHERE id=? AND version=(SELECT MAX(version) FROM specifications WHERE id=?)", (id, id)).fetchone()
        if row:
            print(f"  {id}: SKIP (already exists)")
            specs_created.append(id)
            return
    except Exception:
        pass
    kdb.insert_spec(
        id=id, title=title, status="specified",
        changed_by="Claude", change_reason="P1 Integration Ecosystem (S178)",
        type="requirement", priority=priority, scope=scope, section="integrations",
        tags=tags or ["P1", "integration-framework"],
        description=desc, assertions=assertions
    )
    specs_created.append(id)
    print(f"  {id}: {title}")

print("Creating P1 Integration Ecosystem specifications...\n")

# ── FRAMEWORK SPECIFICATIONS ──────────────────────

cs("SPEC-1761", "Integration Plugin Framework - Manifest & Registry",
   priority="critical",
   desc="Agent Red MUST implement a declarative integration plugin framework with: "
        "(1) IntegrationManifest dataclass with integration_id, display_name, category, auth_type, auth_config, capabilities, sync_strategy, poll_interval_seconds, rate_limit_rpm, webhook_signature_header/algo, tier_gate, status. "
        "(2) Capability taxonomy: source.tickets/articles/contacts/conversations, dest.reply/draft/note/status/tag/assign/create, action.order_lookup/refund/customer_lookup/product_search, webhook.receive. "
        "(3) IntegrationRegistry singleton: register(), get_instance(), list_available(), get_capabilities(), health_check(). "
        "(4) Per-tenant instance management with lazy creation and cleanup. "
        "(5) Backward compatibility: wrap existing Shopify/Stripe in adapters. "
        "[Source: src/integrations/registry.py, src/integrations/manifest.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/registry.py"},
               {"type": "glob", "pattern": "src/integrations/manifest.py"}])

cs("SPEC-1762", "Integration Framework - Normalized Data Models",
   priority="critical",
   desc="Normalized data models as integration boundary: "
        "(1) NormalizedTicket: external_id, source, subject, status (TicketStatus enum: OPEN/PENDING/WAITING_ON_AGENT/RESOLVED/CLOSED), priority, channel, requester, assignee, messages, tags, custom_fields, timestamps, raw. "
        "(2) NormalizedMessage: external_id, source, direction (INBOUND/OUTBOUND/INTERNAL), channel (EMAIL/CHAT/SLACK/SMS/SOCIAL/HELPDESK), body_text/html, sender, attachments, timestamp. "
        "(3) NormalizedArticle: external_id, source, title, body_text (for embedding), body_html, url, category, labels, last_modified. Compatible with KnowledgeBaseDocument. "
        "(4) NormalizedContact: external_id, source, email, name, phone, company, metadata. "
        "(5) NormalizedOrder: external_id, source, order_number, status, customer, line_items, total, currency, timestamps. "
        "(6) Per-vendor status mapping tables. "
        "[Source: src/integrations/models.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/models.py"}])

cs("SPEC-1763", "Integration Framework - Adapter Protocol Interfaces",
   priority="critical",
   desc="Four Protocol-based adapter interfaces (typing.Protocol): "
        "(1) HelpdeskAdapter: list_tickets, get_ticket, add_reply, update_status, add_tags, assign_ticket, create_ticket, search_tickets, register_webhook, verify_webhook. "
        "(2) KnowledgeAdapter: list_articles, get_article, search_articles. "
        "(3) ChannelAdapter: send_message, receive_messages, register_webhook, verify_webhook, format_message. "
        "(4) EcommerceAdapter: lookup_customer, lookup_order, search_orders, get_product, search_products, process_refund. "
        "All async. All return normalized models (SPEC-1762). Raise IntegrationError on vendor errors. "
        "[Source: src/integrations/adapters.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/adapters.py"}])

cs("SPEC-1764", "Integration Framework - Multi-Tenant OAuth Manager",
   priority="critical",
   tags=["P1", "integration-framework", "oauth", "security"],
   desc="Multi-tenant OAuth2 flow manager: "
        "(1) OAuthManager: get_authorization_url(), handle_callback(), get_valid_token() with auto-refresh, revoke_token(). "
        "(2) CSRF: state = signed JWT (tenant_id + integration_id + nonce + 10min expiry). "
        "(3) Token refresh with asyncio.Lock per (tenant, integration) to prevent concurrent refresh races. "
        "(4) Callback: GET /api/integrations/oauth/callback (auth-exempt). Validates state, exchanges code, stores encrypted tokens, redirects to admin UI. "
        "(5) Tokens encrypted via CredentialVault (SPEC-1765). Never logged plaintext. "
        "(6) Supports OAuth2 Authorization Code and PKCE. "
        "[Source: src/integrations/oauth.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/oauth.py"}])

cs("SPEC-1765", "Integration Framework - Two-Layer Credential Vault",
   priority="critical",
   tags=["P1", "integration-framework", "security", "credentials"],
   desc="Two-layer encryption credential vault extending TenantSecretService: "
        "(1) Master KEK in Azure Key Vault. Per-tenant DEK encrypted by KEK stored in Cosmos DB. "
        "(2) CredentialVault: store_credential(), get_credential(), delete_credential(), rotate_credential(), _get_or_create_dek(). "
        "(3) Cosmos container: integration_credentials (PK: tenant_id). "
        "(4) TenantSecretType extension: OAUTH_ACCESS_TOKEN, OAUTH_REFRESH_TOKEN, INTEGRATION_API_KEY, INTEGRATION_WEBHOOK_SECRET. "
        "(5) Encryption: Fernet (AES-128-CBC + HMAC-SHA256). Rationale: Key Vault ~2000 txn/10s limit. "
        "[Source: src/integrations/credential_vault.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/credential_vault.py"}])

cs("SPEC-1766", "Integration Framework - Universal Webhook Receiver",
   priority="critical",
   tags=["P1", "integration-framework", "webhooks"],
   desc="Universal webhook receiver: "
        "(1) POST /webhooks/{tenant_id}/{integration_id} (auth-exempt). "
        "(2) Flow in <1s: verify signature, dedup check (event_id), enqueue, return 200. "
        "(3) Per-integration signature: Zendesk (HMAC-SHA256 x-zendesk-webhook-signature), Intercom (x-hub-signature-256), Shopify (x-shopify-hmac-sha256 base64), Slack (x-slack-signature + timestamp). "
        "(4) Event ID extraction per vendor for idempotency. "
        "(5) Dedup: Redis SET with 24h TTL. "
        "(6) Async processing: background asyncio task with error isolation. "
        "[Source: src/integrations/webhook_receiver.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/webhook_receiver.py"}])

cs("SPEC-1767", "Integration Framework - Polling Scheduler & Cursor Management",
   tags=["P1", "integration-framework", "polling"],
   desc="Background polling scheduler: "
        "(1) PollingScheduler: schedule(), cancel(), execute_poll(). Asyncio background tasks. "
        "(2) Cursor/state in Cosmos integration_sync_state: last_cursor, last_sync_at, sync_status, error_count. "
        "(3) Strategies: incremental (cursor), full (daily sweep), hybrid (webhook + poll). "
        "(4) Adaptive interval: exponential backoff on errors (max 1hr). "
        "(5) After 5 consecutive failures: pause, mark error, notify admin. "
        "[Source: src/integrations/polling.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/polling.py"}])

cs("SPEC-1768", "Integration Framework - Bidirectional Sync with Echo Prevention",
   tags=["P1", "integration-framework", "sync"],
   desc="Echo prevention for bidirectional sync: "
        "(1) BidirectionalSyncManager: record_outbound(), is_echo(), handle_inbound(). "
        "(2) Redis TTL markers (30s). Mark BEFORE sending. Remove marker if outbound fails. "
        "(3) Same anti-loop pattern as cache_invalidation.py _publish=False. "
        "[Source: src/integrations/sync_manager.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/sync_manager.py"}])

cs("SPEC-1769", "Integration Framework - Action Executor with HITL Gating",
   tags=["P1", "integration-framework", "actions"],
   desc="Action Executor routing AI requests to adapters: "
        "(1) ActionExecutor: execute(tenant_id, action) -> ActionResult. Routes by integration_id + action_type. "
        "(2) AIAction: integration_id, action_type, params, conversation_id, requested_by, hitl_required. "
        "(3) HITL gating: per-action-type toggle, per-priority. Drafts default HITL, refunds always HITL. "
        "(4) Audit logging to integration_events container. "
        "(5) Respects per-integration rate limits. "
        "[Source: src/integrations/action_executor.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/action_executor.py"}])

cs("SPEC-1770", "Integration Framework - Multi-Source Knowledge Ingestion Pipeline",
   tags=["P1", "integration-framework", "knowledge", "rag"],
   desc="Multi-source knowledge ingestion extending knowledge_vectorizer.py: "
        "(1) ContentNormalizer: HTML, Markdown, Notion blocks, Confluence storage, PDF/DOCX/CSV to plaintext. "
        "(2) KnowledgeIngestionPipeline: ingest_article(), sync_source(). Normalize, chunk (512 tokens, 50 overlap), embed (text-embedding-3-large), store in Cosmos DiskANN. "
        "(3) Incremental: content hash, re-embed on change only, delete old chunks first. "
        "(4) Source metadata: integration_id, article_id, title, URL for attribution in AI responses. "
        "(5) Ingested articles appear in admin KB alongside manual. Source field distinguishes. Integration-sourced are read-only. "
        "[Source: src/integrations/knowledge_ingestion.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/knowledge_ingestion.py"}])

cs("SPEC-1771", "Integration Framework - Admin API Extensions",
   tags=["P1", "integration-framework", "api"],
   desc="Extend admin_integration_api.py with new endpoints: "
        "(1) GET /setup - instructions + auth URL. "
        "(2) POST /test - connection test via adapter.health_check(). "
        "(3) GET/POST /sync - sync status and manual trigger. "
        "(4) GET /logs - recent events (paginated, last 100). "
        "(5) GET/PUT /actions - available actions + HITL config. "
        "(6) GET /api/integrations/oauth/callback - universal OAuth redirect (auth-exempt). "
        "Migration: _INTEGRATION_META replaced by IntegrationRegistry.list_available(). "
        "[Source: src/multi_tenant/admin_integration_api.py]",
   assertions=[{"type": "grep", "file": "src/multi_tenant/admin_integration_api.py", "pattern": "setup|sync|oauth"}])

cs("SPEC-1772", "Integration Framework - Admin UI Setup & Dashboard",
   scope="frontend",
   tags=["P1", "integration-framework", "admin-ui"],
   desc="Admin UI enhancements: "
        "(1) Integration cards with real-time status, last sync, article/ticket counts. "
        "(2) OAuth setup wizard and API key inline form with test button. "
        "(3) Sync dashboard with timing, counts, errors, Sync Now button. "
        "(4) Action configuration with HITL toggles. "
        "(5) Source selection (folder/page browser for knowledge integrations). "
        "(6) Connection logs with error details. "
        "(7) Integration detail page combining config, sync, actions, logs. "
        "[Source: admin/shared/IntegrationsManager.tsx]",
   assertions=[{"type": "grep", "file": "admin/shared/IntegrationsManager.tsx", "pattern": "OAuth|setup|sync"}])

cs("SPEC-1773", "Integration Framework - Cosmos DB Schema Extensions",
   tags=["P1", "integration-framework", "cosmos-db"],
   desc="New Cosmos DB containers (both production and staging): "
        "(1) integration_credentials (PK: tenant_id) - encrypted tokens, API keys. "
        "(2) integration_sync_state (PK: tenant_id) - cursors, sync status, errors. "
        "(3) integration_events (PK: tenant_id, TTL: 30d) - webhook events, action logs. "
        "(4) normalized_tickets (PK: tenant_id) - ingested helpdesk tickets. "
        "(5) normalized_contacts (PK: tenant_id) - unified customer contacts. "
        "Existing containers leveraged: knowledge_base, conversations, tenants. "
        "[Source: src/multi_tenant/cosmos_schema.py]",
   assertions=[{"type": "grep", "file": "src/multi_tenant/cosmos_schema.py", "pattern": "integration_credentials|integration_sync"}])

cs("SPEC-1774", "Integration Framework - Adaptive Rate Limiter for External APIs",
   priority="medium",
   tags=["P1", "integration-framework", "rate-limiting"],
   desc="Adaptive outbound rate limiter: "
        "(1) AdaptiveRateLimiter: acquire(), record_429(). Per-vendor limits (Zendesk 700/min, Intercom 1000/min, Freshdesk 50/min, Shopify 40/s, Slack 50/min). "
        "(2) RetryExecutor: retryable 429/500/502/503/504, exponential backoff with jitter, Retry-After header, max 3 retries. "
        "(3) OUTBOUND rate limiting (TO external APIs), separate from INBOUND (SPEC-1745). "
        "[Source: src/integrations/rate_limiter.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/rate_limiter.py"}])

# ── STARTER INTEGRATION SPECS ──────────────────────

cs("SPEC-1775", "Zendesk Integration - Full Helpdesk Adapter",
   priority="critical",
   tags=["P1", "integration-zendesk", "helpdesk"],
   desc="Full Zendesk integration (first helpdesk adapter): "
        "Auth: OAuth2. Scopes: read, write, tickets:read, tickets:write. "
        "Sources: tickets with history, Guide help center articles, requester contacts. "
        "Destinations: public reply, draft, internal note, status update, tag, assign, create. "
        "Actions: customer lookup by email. "
        "Webhooks: ticket.created/updated. HMAC-SHA256 x-zendesk-webhook-signature. "
        "Status: new/open->OPEN, pending->PENDING, hold->WAITING, solved->RESOLVED, closed->CLOSED. "
        "API: REST v2, cursor pagination, 700 req/min. "
        "[Source: src/integrations/zendesk/]",
   assertions=[{"type": "glob", "pattern": "src/integrations/zendesk/*.py"}])

cs("SPEC-1776", "Slack Integration - Channel Adapter for AI Bot",
   tags=["P1", "integration-slack", "channel"],
   desc="Slack channel adapter (first channel integration): "
        "Auth: OAuth2. Scopes: chat:write, channels:history/read, groups:read, im:read/write, app_mentions:read, users:read. "
        "Capabilities: dest.reply (Block Kit), webhook.receive (Events API). "
        "Bot behavior: @mention trigger, threaded responses, source citations, escalation, Block Kit formatting. "
        "Webhooks: app_mention, message.channels. HMAC-SHA256 x-slack-signature + timestamp. "
        "Setup: Connect -> OAuth -> bot appears -> admin configures channels. "
        "[Source: src/integrations/slack/]",
   assertions=[{"type": "glob", "pattern": "src/integrations/slack/*.py"}])

cs("SPEC-1777", "Google Docs Integration - Knowledge Source Adapter",
   tags=["P1", "integration-google-docs", "knowledge"],
   desc="Google Docs/Drive knowledge source (first knowledge adapter): "
        "Auth: OAuth2. Scopes: drive.readonly, documents.readonly. "
        "Capabilities: source.articles (Docs, Sheets, PDF, TXT, MD, CSV). "
        "Ingestion: folder selection, HTML export, normalize, chunk, embed. Sheets as CSV records. "
        "Sync: Poll (Drive changes.list incremental), default 1hr, daily full sweep. "
        "Content hash tracking, skip unchanged. "
        "Setup: Connect -> OAuth -> folder selection -> initial sync -> periodic. "
        "[Source: src/integrations/google_docs/]",
   assertions=[{"type": "glob", "pattern": "src/integrations/google_docs/*.py"}])

cs("SPEC-1778", "Integration Framework - Internal Event Bus",
   priority="medium",
   tags=["P1", "integration-framework", "events"],
   desc="Internal event bus for integration events: "
        "(1) IntegrationEventBus: on(event_type, handler), emit(event_type, payload). Fire-and-forget with error isolation. "
        "(2) Events: ticket.created/updated, article.created/updated, message.received, action.completed, integration.connected/disconnected, sync.completed/failed. "
        "(3) Handlers: AI pipeline (auto-response), knowledge ingestion (re-embed), analytics, notifications. "
        "(4) Uses _background_tasks pattern. Compatible with Redis pub/sub for cross-replica. "
        "[Source: src/integrations/event_bus.py]",
   assertions=[{"type": "glob", "pattern": "src/integrations/event_bus.py"}])

print(f"\nTotal: {len(specs_created)} specifications created")
print(f"IDs: {', '.join(specs_created)}")
kdb.close()
