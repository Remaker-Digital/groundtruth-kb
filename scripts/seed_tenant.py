"""
seed_tenant.py — Unified tenant seed for Agent Red Customer Experience
Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
Last verified: 2026-02-15
Last corrected: 2026-02-24 — Switched to canonical auth imports (auth.generate_widget_key + hash_api_key + hash_widget_key); seed now produces production-format widget keys

VARIABLES:
  TENANT_ID       = remaker-digital-001
  SHOP_DOMAIN     = blanco-9939.myshopify.com
  CUSTOMER_EMAIL  = mike@remakerdigital.com
  TIER            = professional
  COSMOS_ENDPOINT = (from .env.local COSMOS_DB_ENDPOINT)
  COSMOS_KEY      = (from .env.local COSMOS_DB_KEY)
  COSMOS_DATABASE = agentred

PRECONDITIONS:
  [ ] Python 3.12+ available                           — python --version
  [ ] .env.local exists with Cosmos credentials        — ls .env.local
  [ ] Cosmos DB endpoint reachable                     — az cosmosdb show --name cosmos-agentred-eastus
  [ ] Project dependencies installed                   — python -c "import azure.cosmos"

POSTCONDITIONS:
  [ ] All prior tenant data deleted from 11 containers (clean slate)
  [ ] 12 Cosmos DB containers created/verified
  [ ] Tenant document with API key + widget key
  [ ] Preferences document (config_state=draft, all fields empty, zero quick actions)
  [ ] 1 team member (superadmin) with per-user API key
  [ ] Zero KB articles (tests create via CRUD)
  [ ] 4 tier_defaults platform config documents
  [ ] Credentials printed to stdout (SAVE THESE)
  [ ] Key Vault ADMIN-PREVIEW-API-KEY updated with new superadmin key  (MANDATORY — see POST-SEED STEPS)
  [ ] Container App revision restarted to pick up new Key Vault secret  (MANDATORY — see POST-SEED STEPS)
  [ ] Production admin UI loads and authenticates with new key           (MANDATORY — verify /api/tenants/lookup returns tenant data)
  [ ] .env.local SUPERADMIN_PREVIEW_API_KEY and PREVIEW_WIDGET_KEY updated  (MANDATORY — see POST-SEED STEPS)
  [ ] Dashboard shows 0 conversations (unless --demo was used)

POST-SEED STEPS (MANDATORY — skipping these leaves production broken):

  Re-seeding generates new API key hashes. The production admin UI
  authenticates via ADMIN-PREVIEW-API-KEY stored in Azure Key Vault.
  If this secret is not updated, the admin UI will fail to load tenant
  context (no tier badge, no sidebar data, broken functionality).

  STEP 1: Update Key Vault with new superadmin API key
    ACTION:    az keyvault secret set --vault-name kv-agentred-eastus \
                 --name ADMIN-PREVIEW-API-KEY --value "<NEW_SUPERADMIN_KEY>"
    VERIFY:    az keyvault secret show --vault-name kv-agentred-eastus \
                 --name ADMIN-PREVIEW-API-KEY --query value -o tsv
    PREREQ:    CLI user needs "Key Vault Secrets Officer" RBAC role on the vault
    ON FAIL:   If 403 Forbidden, assign role via Azure Portal or REST API, wait
               15s for RBAC propagation, retry.

  STEP 2: Restart Container App revision
    ACTION:    az containerapp revision restart --name agent-red-api-gateway \
                 --resource-group agent-red --revision <CURRENT_REVISION>
    VERIFY:    curl https://<FQDN>/health → 200
    NOTE:      The container reads Key Vault secrets on startup via env refs.
               Without a restart, it continues using the cached (now-invalid) key.

  STEP 3: Verify admin UI authentication
    ACTION:    curl -s https://<FQDN>/api/tenants/lookup \
                 -H "X-API-Key: <NEW_SUPERADMIN_KEY>"
    EXPECTED:  {"found": true, "tenant_id": "remaker-digital-001", ...}
    ON FAIL:   If "Invalid API key" → Key Vault secret not updated or revision
               not restarted. Go back to Step 1.

  STEP 4: Update .env.local and regression conftest with new credentials
    ACTION:    Set SUPERADMIN_PREVIEW_API_KEY and PREVIEW_WIDGET_KEY in .env.local.
               Also update the WIDGET_KEY fallback in tests/regression/conftest.py.
    VERIFY:    grep -E "SUPERADMIN_PREVIEW_API_KEY|PREVIEW_WIDGET_KEY" .env.local
               grep "WIDGET_KEY" tests/regression/conftest.py
               — all values must match the seed output (Phase 8 summary)
    NOTE:      .env.local is used for local development and test runs.
               conftest.py fallback is used when WIDGET_KEY env var is not set.
               Stale keys in either location cause silent auth failures.

  STEP 5: Update MEMORY.md with new credentials
    ACTION:    Update "Widget key" and "Superadmin API key" in Quick Reference
    NOTE:      Every re-seed generates new keys. Old keys in MEMORY.md are invalid.

  See also: REPEATABLE-PROCEDURES.md Section 7 — No Hardcoded Transient Values

KNOWN FAILURE MODES:
  | Failure | Classification | Resolution |
  |---------|---------------|------------|
  | Vector search not propagated (knowledge_bases, memory_vectors fail) | Environment transient | Wait 15 min after EnableNoSQLVectorSearch, re-run |
  | Config state was "active" instead of "draft" | Procedure defect (corrected 2026-02-14) | Changed to "draft" — new tenants must activate after providing mandatory inputs |
  | Stale data after re-seed (badge shows Active, form shows defaults) | Procedure defect (corrected 2026-02-14) | Added Phase 0 partition cleanup — all tenant docs deleted before seeding |
  | Seed pre-fills merchant fields (brand_name, brand_voice, etc.) | Procedure defect (corrected 2026-02-14) | All merchant-configurable fields must be empty — tenant starts Pending |
  | Key regeneration invalidates existing keys | By design | Every run generates new keys. MUST update Key Vault + restart revision (see POST-SEED STEPS). |
  | Admin UI broken after re-seed (no tier badge, no tenant context) | Procedure defect (corrected 2026-02-15) | Post-seed steps were not documented. Added mandatory Key Vault update + revision restart + verification. |
  | Stale demo conversations after re-seed without --demo | Procedure defect (corrected 2026-02-15) | Phase 0 deletes all docs including conversations. Do NOT use --demo for clean initial state testing. |
  | CLI user lacks Key Vault write access (403 Forbidden) | Environment (one-time RBAC setup) | Assign "Key Vault Secrets Officer" to CLI user on kv-agentred-eastus via Azure Portal or REST API. |
  | Regression tests fail after re-seed (stale WIDGET_KEY fallback in conftest.py) | Procedure defect (corrected 2026-02-15) | Update fallback in tests/regression/conftest.py or set WIDGET_KEY env var. |

Creates all Cosmos DB containers and provisions
a complete tenant environment with sensible defaults.

Orchestrates 8 phases:
    1. Containers   — 12 Cosmos DB containers with indexes
    0. Clean        — Delete ALL existing tenant docs (clean slate)
    2. Tenant       — TenantDocument (active, professional) + API/widget keys
    3. Preferences  — PreferencesDocument v1 (draft config, brand, widget, quick actions)
    4. Team         — 1 TeamMemberDocument (superadmin only)
    6. Platform     — 4 tier_defaults documents
    7. Demo Data    — Conversations, profiles, memory (with --demo flag)
    8. Summary      — Print all credentials, URLs, phase results

NOTE: Phase 5 (KB article seeding) was removed in S26. Initialization produces
a clean tenant with zero articles. Use seed_knowledge_base.py separately if
you need to populate KB articles for testing.

Usage:
    # Dry-run preview (no DB writes):
    python scripts/seed_tenant.py

    # Write to DB (initialization — clean tenant, zero articles):
    python scripts/seed_tenant.py --execute

    # Write + seed demo conversations:
    python scripts/seed_tenant.py --execute --demo

Requires Azure credentials in .env.local:
    COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Project setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local

load_env_local()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Suppress verbose Azure SDK HTTP logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# Tenant configuration — override via env vars or .env.local.
# Defaults are the canonical Remaker Digital test tenant.
# See REPEATABLE-PROCEDURES.md §7.4 for documented-default policy.
# ---------------------------------------------------------------------------

TENANT_ID = os.environ.get("SEED_TENANT_ID", "remaker-digital-001")
SHOP_DOMAIN = os.environ.get("SEED_SHOP_DOMAIN", "blanco-9939.myshopify.com")
CUSTOMER_EMAIL = os.environ.get("SEED_CUSTOMER_EMAIL", "mike@remakerdigital.com")
TIER = os.environ.get("SEED_TIER", "professional")
BILLING_CHANNEL = os.environ.get("SEED_BILLING_CHANNEL", "shopify")
INTERVAL = os.environ.get("SEED_INTERVAL", "month")

FQDN = os.environ.get("SEED_FQDN", "")
if not FQDN:
    print("ERROR: SEED_FQDN environment variable is required (SPEC-0058).")
    print("  Staging:    SEED_FQDN=<staging FQDN from .env.local STAGING_URL>")
    print("  Production: SEED_FQDN=<production FQDN from .env.local PROD_URL>")
    print("  Set SEED_FQDN explicitly to prevent accidental environment targeting.")
    sys.exit(1)

# Team members to create during provisioning.
# The superadmin is the platform operator's hidden safety-net account.
# The customer admin (SPEC-0761) is the standard admin account handed off
# to the customer email address — a different email from the superadmin.
# Additional team members (escalation agents, viewers) are added by the
# merchant through the Admin UI after onboarding.
TEAM_MEMBERS = [
    {
        "email": "mike@remakerdigital.com",
        "display_name": "Owner",
        "role": "superadmin",
        "escalation_categories": [],
    },
    {
        "email": CUSTOMER_EMAIL,
        "display_name": "Account Administrator",
        "role": "admin",
        "escalation_categories": [],
    },
]

# Quick action starters (embedded in preferences)
QUICK_ACTIONS = [
    {
        "id": str(uuid.uuid4()),
        "label": "Track my order",
        "prompt_template": "I'd like to track my recent order. Can you help me find the status?",
        "icon": "📦",
        "is_active": True,
        "sort_order": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "label": "Return or exchange",
        "prompt_template": "I need help with a return or exchange. What's the process?",
        "icon": "🔄",
        "is_active": True,
        "sort_order": 1,
    },
    {
        "id": str(uuid.uuid4()),
        "label": "Product question",
        "prompt_template": "I have a question about one of your products. Can you help?",
        "icon": "❓",
        "is_active": True,
        "sort_order": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "label": "Shipping info",
        "prompt_template": "What are your shipping options and delivery times?",
        "icon": "🚚",
        "is_active": True,
        "sort_order": 3,
    },
]

# Quick action assignments (all pages get all 4 actions)
QUICK_ACTION_ASSIGNMENTS = [
    {
        "page_type": "all",
        "page_handle": None,
        "slot_1_action_id": QUICK_ACTIONS[0]["id"],
        "slot_2_action_id": QUICK_ACTIONS[1]["id"],
    },
]

# ---------------------------------------------------------------------------
# Phase results tracker
# ---------------------------------------------------------------------------

phase_results: dict[str, str] = {}
generated_credentials: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Phase 0: Clean tenant partition (delete all existing documents)
# ---------------------------------------------------------------------------

# All containers that hold tenant-scoped data (partition key = /tenant_id).
TENANT_CONTAINERS = [
    "tenants",
    "preferences",
    "team_members",
    "conversations",
    "customer_profiles",
    "knowledge_bases",
    "memory_vectors",
    "usage",
    "audit_log",
    "agent_overlays",
    "agent_bindings",
]
# platform_config uses /tenant_id="platform" — not tenant-specific, skip.


async def phase_0_clean_partition(dry_run: bool) -> None:
    """Delete ALL documents for TENANT_ID from every tenant-scoped container.

    This ensures a fresh seed starts with a completely clean slate —
    no stale config_state, no orphaned preferences, no leftover team
    members.  Must run AFTER Phase 1 (containers exist) but is listed
    as Phase 0 because it conceptually precedes data creation.
    """
    print()
    print("=" * 65)
    print("  PHASE 0: Clean Tenant Partition")
    print("=" * 65)

    if dry_run:
        for name in TENANT_CONTAINERS:
            print(f"  [DRY RUN] Would purge all {TENANT_ID!r} docs from {name}")
        phase_results["0_clean_partition"] = f"DRY RUN — {len(TENANT_CONTAINERS)} containers"
        return

    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.cosmos_schema import DATABASE_NAME

    cosmos = get_cosmos_manager()
    await cosmos._ensure_client()
    assert cosmos._client is not None

    database_name = os.environ.get("COSMOS_DB_DATABASE", DATABASE_NAME)
    db = cosmos._client.get_database_client(database_name)

    total_deleted = 0
    for name in TENANT_CONTAINERS:
        try:
            container = db.get_container_client(name)
            # Query all document ids in this tenant's partition
            query = "SELECT c.id FROM c WHERE c.tenant_id = @tid"
            params: list[dict] = [{"name": "@tid", "value": TENANT_ID}]
            items = container.query_items(
                query=query,
                parameters=params,
                partition_key=TENANT_ID,
                max_item_count=500,
            )
            doc_ids: list[str] = []
            async for item in items:
                doc_ids.append(item["id"])

            if not doc_ids:
                print(f"  [OK] {name}: empty (no docs to delete)")
                continue

            for doc_id in doc_ids:
                await container.delete_item(item=doc_id, partition_key=TENANT_ID)

            print(f"  [OK] {name}: deleted {len(doc_ids)} doc(s)")
            total_deleted += len(doc_ids)
        except Exception as e:
            err_msg = str(e)
            if "NotFound" in err_msg or "does not exist" in err_msg.lower():
                print(f"  [SKIP] {name}: container does not exist yet")
            else:
                print(f"  [ERROR] {name}: {err_msg[:120]}")

    phase_results["0_clean_partition"] = (
        f"OK — deleted {total_deleted} doc(s) across {len(TENANT_CONTAINERS)} containers"
    )


# ---------------------------------------------------------------------------
# Phase 1: Create Cosmos DB containers
# ---------------------------------------------------------------------------


async def phase_1_containers(dry_run: bool) -> None:
    """Create all 12 Cosmos DB containers with indexes.

    Uses a tolerant approach: creates each container individually so that
    failures (e.g., vector search capability not yet propagated) don't block
    the remaining containers from being created.
    """
    print()
    print("=" * 65)
    print("  PHASE 1: Cosmos DB Containers")
    print("=" * 65)

    from src.multi_tenant.cosmos_schema import get_collection_configs

    if dry_run:
        configs = get_collection_configs()
        for cfg in configs:
            print(f"  [DRY RUN] Would create: {cfg.name} (partition: {cfg.partition_key})")
        phase_results["1_containers"] = f"DRY RUN — {len(configs)} containers"
        return

    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.cosmos_schema import DATABASE_NAME

    cosmos = get_cosmos_manager()
    database_name = os.environ.get("COSMOS_DB_DATABASE", DATABASE_NAME)

    # Ensure client is connected
    await cosmos._ensure_client()
    assert cosmos._client is not None

    # Try creating database (idempotent)
    try:
        await cosmos._client.create_database_if_not_exists(id=database_name)
        print("  [OK] Database ready")
    except Exception as e:
        print(f"  [ERROR] Database: {e}")

    db = cosmos._client.get_database_client(database_name)

    configs = get_collection_configs()
    ok_count = 0
    err_count = 0

    for config in configs:
        try:
            kwargs: dict = {
                "id": config.name,
                "partition_key": {"paths": [config.partition_key], "kind": "Hash"},
            }
            if config.unique_keys:
                kwargs["unique_key_policy"] = {
                    "uniqueKeys": [{"paths": paths} for paths in config.unique_keys],
                }
            if config.default_ttl is not None:
                kwargs["default_ttl"] = config.default_ttl
            if config.indexing_policy is not None:
                kwargs["indexing_policy"] = config.indexing_policy
            if config.vector_embedding_policy is not None:
                kwargs["vector_embedding_policy"] = config.vector_embedding_policy

            await db.create_container_if_not_exists(**kwargs)
            print(f"  [OK] {config.name}")
            ok_count += 1
        except Exception as e:
            err_msg = str(e)
            if "Vector" in err_msg and "not been enabled" in err_msg:
                print(f"  [WARN] {config.name} — vector search capability not yet propagated (retry later)")
            else:
                print(f"  [ERROR] {config.name} — {err_msg[:100]}")
            err_count += 1

    if err_count > 0:
        phase_results["1_containers"] = f"PARTIAL — {ok_count}/{len(configs)} ok, {err_count} failed"
    else:
        phase_results["1_containers"] = f"OK — {ok_count} containers"


# ---------------------------------------------------------------------------
# Phase 2: Create tenant document
# ---------------------------------------------------------------------------


async def phase_2_tenant(dry_run: bool) -> None:
    """Create the TenantDocument with API key and widget key."""
    print()
    print("=" * 65)
    print("  PHASE 2: Tenant Document")
    print("=" * 65)

    from src.multi_tenant.auth import (
        generate_widget_key,
        hash_api_key,
        hash_widget_key,
    )
    from src.multi_tenant.cosmos_schema import (
        BillingChannel,
        ConsentStatus,
        TenantDocument,
        TenantStatus,
        TenantTier,
    )

    # Tenant-level API key — simple random token (no canonical generator
    # in auth.py; per-user keys use generate_user_api_key instead).
    api_key = "ar_" + secrets.token_hex(24)
    widget_key = generate_widget_key(TENANT_ID)
    now = datetime.now(timezone.utc).isoformat()

    # SPEC-1673: Only the widget_key is retained temporarily (needed by
    # Phase 3 preferences).  The tenant API key is hashed and discarded.
    generated_credentials["widget_key"] = widget_key
    generated_credentials["seeded_tenant_api_key"] = True

    tenant_doc = TenantDocument(
        id=TENANT_ID,
        tenant_id=TENANT_ID,
        status=TenantStatus.ACTIVE,
        billing_channel=BillingChannel(BILLING_CHANNEL),
        tier=TenantTier(TIER),
        interval=INTERVAL,
        addons=[],
        shopify_shop_domain=SHOP_DOMAIN,
        customer_email=CUSTOMER_EMAIL,
        consent_status=ConsentStatus.GRANTED,
        api_key_hash=hash_api_key(api_key),
        widget_key_hash=hash_widget_key(widget_key),
        rate_limit_rpm=None,  # Fall through to TIER_DEFAULTS (S139/S140 fix)
        max_concurrent=10,
        created_at=now,
        updated_at=now,
    )

    print(f"  Tenant ID:      {TENANT_ID}")
    print(f"  Shop domain:    {SHOP_DOMAIN}")
    print(f"  Tier:           {TIER}")
    print(f"  Channel:        {BILLING_CHANNEL}")
    print(f"  Status:         active")
    print(f"  Email:          {CUSTOMER_EMAIL}")

    if dry_run:
        print(f"  [DRY RUN] Would create tenant document")
        phase_results["2_tenant"] = "DRY RUN"
        return

    from src.multi_tenant.repository import TenantRepository

    repo = TenantRepository()
    try:
        await repo.create(TENANT_ID, tenant_doc)
        print("  [OK] Tenant document created.")
        phase_results["2_tenant"] = "OK — created"
    except Exception as e:
        if "409" in str(e) or "Conflict" in str(e) or "already exists" in str(e):
            await repo.upsert(TENANT_ID, tenant_doc)
            print("  [OK] Tenant document updated (upsert).")
            phase_results["2_tenant"] = "OK — upserted"
        else:
            print(f"  [ERROR] {e}")
            phase_results["2_tenant"] = f"ERROR: {e}"

    # SPEC-1851: Sync domain_index for O(1) Shopify domain lookups
    try:
        from src.multi_tenant.repositories.domain_index import DomainIndexRepository

        domain_index = DomainIndexRepository()
        await domain_index.upsert(SHOP_DOMAIN, TENANT_ID, "shopify")
        print("  [OK] Domain index synced.")
    except Exception as e:
        print(f"  [WARN] Domain index sync failed: {e}")

    # SPEC-1673: Raw tenant API key discarded after hashing — never retained.
    del api_key


# ---------------------------------------------------------------------------
# Phase 3: Create preferences document
# ---------------------------------------------------------------------------


async def phase_3_preferences(dry_run: bool) -> None:
    """Create PreferencesDocument v1 with draft config (all merchant fields empty)."""
    print()
    print("=" * 65)
    print("  PHASE 3: Preferences (Draft — merchant fields empty)")
    print("=" * 65)

    from src.multi_tenant.cosmos_schema import PreferencesDocument

    now = datetime.now(timezone.utc).isoformat()

    # Quick actions are NOT seeded — tests exercise full CRUD on these.
    # A fresh tenant starts with zero quick actions.
    qa_with_timestamps: list[dict] = []

    # Retrieve the widget key generated in Phase 2 (required for activation)
    widget_key = generated_credentials.get("widget_key")
    if not widget_key:
        logger.warning("widget_key not found in generated_credentials — widget will not load")

    prefs_doc = PreferencesDocument(
        id=f"{TENANT_ID}:1",
        tenant_id=TENANT_ID,
        version=1,
        is_current=True,
        config_state="draft",
        activated_at=None,
        activated_by=None,
        config_name="Default",
        appearance_name="Default",
        # Widget key (must match tenant widget_key_hash — set during provisioning)
        widget_key=widget_key,
        # ---------------------------------------------------------------
        # Merchant-configurable fields — ALL EMPTY for fresh tenant.
        # The merchant must fill these in and Activate before the widget
        # goes live.  See Page 0 in ui-test-procedure.md.
        # ---------------------------------------------------------------
        brand_name="",
        brand_voice="",
        custom_instructions="",
        return_policy="",
        shipping_info="",
        escalation_keywords=[],
        escalation_email=None,
        escalation_threshold=0.7,
        greeting_message=None,
        farewell_message=None,
        warranty_info=None,
        support_hours=None,
        custom_policies=None,
        # ---------------------------------------------------------------
        # System defaults — sensible values, not merchant input.
        # ---------------------------------------------------------------
        primary_language="en",
        additional_languages=[],
        response_length="standard",
        formality_level="balanced",
        memory_enabled=True,
        pattern_learning_enabled=True,
        data_retention_days=365,
        consent_collection_enabled=True,
        # Widget appearance — platform defaults
        widget_primary_color="#ff3621",
        widget_background_color="#141414",
        widget_position="bottom-right",
        widget_offset_x=20,
        widget_offset_y=20,
        widget_agent_display_name="",
        widget_agent_title="",
        widget_show_branding=True,
        widget_mobile_enabled=True,
        widget_dark_mode=True,
        widget_color_mode="auto",
        # Widget behavior — platform defaults
        widget_auto_open=False,
        widget_auto_open_delay=5,
        widget_offline_behavior="ai_only",
        widget_offline_message="",
        widget_chat_rating_enabled=True,
        widget_sound_enabled=True,
        widget_file_upload_enabled=False,
        widget_greeting_enabled=True,
        # widget_greeting_message intentionally omitted — platform_default
        # "Hi there! How can I help you today?" applies via resolve_defaults().
        widget_offline_form_enabled=True,
        # Widget content — empty for merchant to fill
        widget_header_text="",
        widget_input_placeholder="",
        widget_page_rules=[],
        # Quick actions (embedded directly)
        quick_actions=qa_with_timestamps,
        quick_action_assignments=[],  # Tests create assignments via CRUD
        widget_quick_actions_enabled=True,
        # Metadata
        created_at=now,
        created_by="seed_tenant.py",
    )

    print(f"  Brand:          {prefs_doc.brand_name}")
    print(f"  Config state:   {prefs_doc.config_state}")
    print(f"  Quick actions:  {len(qa_with_timestamps)}")
    print(f"  Widget color:   {prefs_doc.widget_primary_color}")

    if dry_run:
        print("  [DRY RUN] Would create preferences document")
        phase_results["3_preferences"] = "DRY RUN"
        return

    from src.multi_tenant.repository import PreferencesRepository

    repo = PreferencesRepository()
    try:
        await repo.create(TENANT_ID, prefs_doc)
        print("  [OK] Preferences document created.")
        phase_results["3_preferences"] = "OK — created"
    except Exception as e:
        if "409" in str(e) or "Conflict" in str(e) or "already exists" in str(e):
            await repo.upsert(TENANT_ID, prefs_doc)
            print("  [OK] Preferences document updated (upsert).")
            phase_results["3_preferences"] = "OK — upserted"
        else:
            print(f"  [ERROR] {e}")
            phase_results["3_preferences"] = f"ERROR: {e}"

    # SPEC-1673: Raw widget key discarded after use — never retained.
    generated_credentials.pop("widget_key", None)
    del widget_key


# ---------------------------------------------------------------------------
# Phase 4: Create team members
# ---------------------------------------------------------------------------


async def phase_4_team(dry_run: bool) -> None:
    """Create superadmin TeamMemberDocument with per-user API key."""
    print()
    print("=" * 65)
    print("  PHASE 4: Team Members")
    print("=" * 65)

    from src.multi_tenant.auth import generate_user_api_key, hash_api_key
    from src.multi_tenant.cosmos_schema import TeamMemberDocument, TeamMemberRole

    now = datetime.now(timezone.utc).isoformat()
    role_map = {
        "superadmin": TeamMemberRole.SUPERADMIN,
        "admin": TeamMemberRole.ADMIN,
        "escalation_agent": TeamMemberRole.ESCALATION_AGENT,
        "viewer": TeamMemberRole.VIEWER,
    }

    for member_cfg in TEAM_MEMBERS:
        email = member_cfg["email"]
        display_name = member_cfg["display_name"]
        role = role_map[member_cfg["role"]]
        member_id = f"{TENANT_ID}:{email}"

        user_api_key = generate_user_api_key(TENANT_ID)
        key_hash = hash_api_key(user_api_key)
        key_prefix = user_api_key[:12] + "..."

        # SPEC-1673: Track that a key was generated (no raw value stored)
        generated_credentials[f"user_key_{email}"] = "[generated]"
        del user_api_key  # Raw key discarded after hashing

        doc = TeamMemberDocument(
            id=member_id,
            tenant_id=TENANT_ID,
            email=email,
            display_name=display_name,
            role=role,
            is_active=True,
            escalation_categories=member_cfg["escalation_categories"],
            max_concurrent_conversations=0 if role == TeamMemberRole.SUPERADMIN else 5,
            user_api_key_hash=key_hash,
            user_api_key_prefix=key_prefix,
            created_at=now,
            updated_at=now,
            last_login_at=None,
            invited_by="seed_tenant.py",
        )

        print(f"  {display_name} <{email}> — {member_cfg['role']}")

        if dry_run:
            print(f"    [DRY RUN] Would create team member")
            continue

        from src.multi_tenant.repository import TeamMemberRepository

        repo = TeamMemberRepository()
        try:
            await repo.create(TENANT_ID, doc)
            print(f"    [OK] Created.")
        except Exception as e:
            if "409" in str(e) or "Conflict" in str(e) or "already exists" in str(e):
                await repo.upsert(TENANT_ID, doc)
                print(f"    [OK] Updated (upsert).")
            else:
                print(f"    [ERROR] {e}")

    phase_results["4_team"] = f"{'DRY RUN' if dry_run else 'OK'} — {len(TEAM_MEMBERS)} members"


# ---------------------------------------------------------------------------
# Phase 5: Seed knowledge base
# ---------------------------------------------------------------------------


async def phase_5_knowledge_base(dry_run: bool, embed: bool) -> None:
    """Seed 48 KB articles via seed_knowledge_base module."""
    print()
    print("=" * 65)
    print("  PHASE 5: Knowledge Base")
    print("=" * 65)

    from scripts.seed_knowledge_base import TOTAL_ARTICLES, load_to_cosmos

    print(f"  Articles to seed: {TOTAL_ARTICLES}")

    if dry_run:
        print("  [DRY RUN] Would seed knowledge base articles")
        phase_results["5_knowledge_base"] = f"DRY RUN — {TOTAL_ARTICLES} articles"
        return

    try:
        await load_to_cosmos(
            tenant_id=TENANT_ID,
            dry_run=False,
            embed=embed,
        )
        phase_results["5_knowledge_base"] = f"OK — {TOTAL_ARTICLES} articles"
        if embed:
            phase_results["5_knowledge_base"] += " (with embeddings)"
    except Exception as e:
        print(f"  [ERROR] {e}")
        phase_results["5_knowledge_base"] = f"ERROR: {e}"


# ---------------------------------------------------------------------------
# Phase 6: Platform config (tier defaults)
# ---------------------------------------------------------------------------


async def phase_6_platform_config(dry_run: bool) -> None:
    """Seed platform_config with tier defaults + comprehensive entitlements v1.

    Creates:
      - 4 legacy tier_defaults documents (backward compatibility)
      - 6 entitlement documents (SPEC-1814 schema v1):
          tier_config, pricing, sla_targets, website_limits,
          integration_gates + field_gates, global_config
    """
    print()
    print("=" * 65)
    print("  PHASE 6: Platform Config (Tier Defaults + Entitlements v1)")
    print("=" * 65)

    from src.multi_tenant.cosmos_schema import (
        TIER_DEFAULTS,
        PlatformConfigDocument,
    )
    from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS

    now = datetime.now(timezone.utc).isoformat()
    doc_count = 0

    # --- Legacy tier_defaults documents (backward compat) ---
    print("\n  [Legacy] Tier defaults:")
    for tier_name, tier_values in TIER_DEFAULTS.items():
        doc = PlatformConfigDocument(
            id=f"tier_defaults:{tier_name}",
            config_type="tier_defaults",
            config_key=tier_name,
            value=tier_values,
            version=1,
            updated_at=now,
            updated_by="seed_tenant.py",
        )

        print(f"    {tier_name}: {tier_values['included_conversations']} convos, {tier_values['rate_limit_rpm']} rpm")

        if not dry_run:
            from src.multi_tenant.repository import PlatformConfigRepository

            repo = PlatformConfigRepository()
            try:
                await repo.set_config(doc)
                print(f"      [OK] Upserted.")
            except Exception as e:
                print(f"      [ERROR] {e}")

        doc_count += 1

    # --- Entitlement v1 documents (SPEC-1814) ---
    entitlement_docs: list[tuple[str, str, Any]] = [
        ("tier_config", "all_tiers", FROZEN_ENTITLEMENTS["tiers"]),
        ("entitlements", "pricing", FROZEN_ENTITLEMENTS["pricing"]),
        ("entitlements", "pack_pricing", FROZEN_ENTITLEMENTS["pack_pricing"]),
        ("entitlements", "sla_targets", FROZEN_ENTITLEMENTS["sla_targets"]),
        ("entitlements", "website_limits", FROZEN_ENTITLEMENTS["website_limits"]),
        ("entitlements", "integration_gates", FROZEN_ENTITLEMENTS["integration_gates"]),
        ("entitlements", "field_gates", FROZEN_ENTITLEMENTS["field_gates"]),
        ("entitlements", "global_config", FROZEN_ENTITLEMENTS["global_config"]),
    ]

    print("\n  [v1] Entitlement documents:")
    for config_type, config_key, value in entitlement_docs:
        doc = PlatformConfigDocument(
            id=f"{config_type}:{config_key}",
            config_type=config_type,
            config_key=config_key,
            value=value,
            version=1,
            updated_at=now,
            updated_by="seed_tenant.py",
        )

        # Display summary
        if isinstance(value, dict):
            summary = f"{len(value)} entries"
        else:
            summary = str(value)[:60]
        print(f"    {config_type}:{config_key} — {summary}")

        if not dry_run:
            from src.multi_tenant.repository import PlatformConfigRepository

            repo = PlatformConfigRepository()
            try:
                await repo.set_config(doc)
                print(f"      [OK] Upserted.")
            except Exception as e:
                print(f"      [ERROR] {e}")

        doc_count += 1

    # --- Health sentinel document (SPEC-1833) ---
    print("\n  [Health] Sentinel document:")
    sentinel_doc = PlatformConfigDocument(
        id="health_sentinel",
        config_type="health_sentinel",
        config_key="health_sentinel",
        value={"status": "ok", "updated_at": now},
        version=1,
        updated_at=now,
        updated_by="seed_tenant.py",
    )
    print("    health_sentinel — readiness probe target")

    if not dry_run:
        from src.multi_tenant.repository import PlatformConfigRepository

        repo = PlatformConfigRepository()
        try:
            await repo.set_config(sentinel_doc)
            print("      [OK] Upserted.")
        except Exception as e:
            print(f"      [ERROR] {e}")

    doc_count += 1

    phase_results["6_platform_config"] = (
        f"{'DRY RUN' if dry_run else 'OK'} — {doc_count} platform config docs "
        f"(4 legacy tier_defaults + {doc_count - 5} entitlement v1 + 1 health sentinel)"
    )


# ---------------------------------------------------------------------------
# Phase 7: Demo data (optional)
# ---------------------------------------------------------------------------


async def phase_7_demo_data(dry_run: bool, demo: bool) -> None:
    """Seed demo conversations, profiles, and memory vectors."""
    print()
    print("=" * 65)
    print("  PHASE 7: Demo Data")
    print("=" * 65)

    if not demo:
        print("  [SKIP] Demo data not requested (use --demo flag)")
        phase_results["7_demo_data"] = "SKIPPED — use --demo flag"
        return

    if dry_run:
        print("  [DRY RUN] Would seed demo conversations, profiles, and memory")
        phase_results["7_demo_data"] = "DRY RUN"
        return

    try:
        from scripts.seed_demo_data import seed as seed_demo

        await seed_demo(dry_run=False, seed_kb=False)
        phase_results["7_demo_data"] = "OK — conversations, profiles, memory"
    except Exception as e:
        print(f"  [ERROR] {e}")
        phase_results["7_demo_data"] = f"ERROR: {e}"


# ---------------------------------------------------------------------------
# Phase 8: Summary
# ---------------------------------------------------------------------------


def phase_8_summary() -> None:
    """Print seed summary — SPEC-1673: raw keys are NEVER displayed."""
    print()
    print()
    print("=" * 65)
    print("  PHASE 8: SEED SUMMARY")
    print("=" * 65)

    # Key generation status (SPEC-1673: no raw keys displayed)
    print()
    print("-" * 65)
    print("  KEYS GENERATED AND HASHED (SPEC-1673)")
    print("-" * 65)
    print()

    if generated_credentials.get("seeded_tenant_api_key"):
        print("  Tenant API Key:  [GENERATED — hash stored in Cosmos]")
    print("  Widget Key:      [GENERATED — hash stored in Cosmos]")

    print()
    print("  User API Keys:")
    for member_cfg in TEAM_MEMBERS:
        email = member_cfg["email"]
        key_name = f"user_key_{email}"
        if key_name in generated_credentials:
            print(f"    {member_cfg['display_name']} <{email}>")
            print(f"      [GENERATED — hash stored in Cosmos]")
            print()

    print("  Raw keys are NOT displayed or saved (SPEC-1673).")
    print("  Tenant superadmins will receive keys via email (WI-1106).")
    print()

    # URLs
    print("-" * 65)
    print("  URLS")
    print("-" * 65)
    print()
    print(f"  Admin UI:          https://{FQDN}/admin/standalone/")
    print(f"  API Docs:          https://{FQDN}/docs")
    print(f"  Health:            https://{FQDN}/health")
    print(f"  Widget JS:         https://{FQDN}/widget.js")
    print(f"  Storefront:        https://blanco-9939.myshopify.com/")
    print()

    # Phase results
    print("-" * 65)
    print("  PHASE RESULTS")
    print("-" * 65)
    print()
    for phase_name, result in phase_results.items():
        phase_num = phase_name.split("_")[0]
        label = phase_name.split("_", 1)[1].replace("_", " ").title()
        print(f"  Phase {phase_num}: {label:25s} {result}")
    print()
    print("=" * 65)
    print()


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


async def phase_3b_preset(dry_run: bool, preset_id: str | None) -> None:
    """Apply a vertical preset after preferences are created (SPEC-1878).

    Uses direct repository writes — the same pattern as Phase 3 — to avoid
    dependency on app-startup singletons (ActivationService, QA repo).
    """
    print()
    print("=" * 65)
    print("  PHASE 3b: Vertical Preset")
    print("=" * 65)

    if not preset_id:
        print("  [SKIP] No preset requested (use --preset <id>)")
        phase_results["3b_preset"] = "SKIPPED — use --preset flag"
        return

    from src.presets.preset_service import PresetService, CONFIG_SAVE_FIELDS

    svc = PresetService()
    preset = svc.get_preset(preset_id)
    if preset is None:
        available = [p.id for p in svc.list_presets()]
        print(f"  [ERROR] Preset '{preset_id}' not found. Available: {available}")
        phase_results["3b_preset"] = f"ERROR: unknown preset '{preset_id}'"
        return

    config_fields = svc._extract_config_fields(preset)
    qa_list = preset.get("quick_actions", [])
    kb_articles = preset.get("knowledge_seed", [])

    if dry_run:
        print(f"  [DRY RUN] Would apply preset: {preset['display_name']}")
        print(f"            Config fields: {len(config_fields)}")
        print(f"            Quick actions: {len(qa_list)}")
        print(f"            KB articles:   {len(kb_articles)}")
        phase_results["3b_preset"] = f"DRY RUN — {preset_id}"
        return

    from src.multi_tenant.repository import PreferencesRepository
    import uuid as _uuid

    repo = PreferencesRepository()
    now = datetime.now(timezone.utc).isoformat()
    qa_created = 0
    kb_created = 0

    try:
        # Step 1: Merge config fields into the preferences document
        prefs = await repo.get_draft(TENANT_ID)
        if prefs is None:
            print("  [ERROR] Preferences document not found (Phase 3 must run first)")
            phase_results["3b_preset"] = "ERROR: no preferences document"
            return

        prefs_dict = prefs if isinstance(prefs, dict) else prefs.model_dump()
        for key, value in config_fields.items():
            prefs_dict[key] = value
        # Map widget fields to their prefs-document names
        widget = preset.get("widget", {})
        if "greeting_message" in widget:
            prefs_dict["widget_greeting_message"] = widget["greeting_message"]
        if "input_placeholder" in widget:
            prefs_dict["widget_input_placeholder"] = widget["input_placeholder"]

        # Step 2: Add quick-action prompts directly to the prefs document
        existing_qa = prefs_dict.get("quick_actions", [])
        created_ids = []
        for i, qa in enumerate(qa_list):
            action_id = str(_uuid.uuid4())
            existing_qa.append(
                {
                    "id": action_id,
                    "label": qa.get("label", ""),
                    "prompt_template": qa.get("message", ""),
                    "icon": qa.get("icon", ""),
                    "is_active": True,
                    "sort_order": i * 10,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            created_ids.append(action_id)
        prefs_dict["quick_actions"] = existing_qa
        qa_created = len(created_ids)

        # Step 3: Add page assignment for first 2 actions
        if created_ids:
            assignment = {
                "page_type": "all",
                "page_handle": None,
                "auto_open": False,
                "auto_open_delay_ms": 3000,
            }
            if len(created_ids) >= 1:
                assignment["slot_1_action_id"] = created_ids[0]
            if len(created_ids) >= 2:
                assignment["slot_2_action_id"] = created_ids[1]
            existing_assignments = prefs_dict.get("quick_action_assignments", [])
            existing_assignments.append(assignment)
            prefs_dict["quick_action_assignments"] = existing_assignments

        # Upsert the merged preferences document
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        updated_prefs = PreferencesDocument(**prefs_dict)
        await repo.upsert(TENANT_ID, updated_prefs)
        print(f"  Config fields merged: {len(config_fields)}")
        print(f"  Quick actions added:  {qa_created}")

        # Step 4: Seed KB articles directly via KB repository
        if kb_articles:
            from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
            from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument

            kb_repo = KnowledgeBaseRepository()
            for article in kb_articles:
                try:
                    entry_id = str(_uuid.uuid4())
                    doc = KnowledgeBaseDocument(
                        id=entry_id,
                        tenant_id=TENANT_ID,
                        entry_type="article",
                        title=article.get("title", ""),
                        content=article.get("content", ""),
                        metadata={"preset_source": preset_id},
                        tags=[],
                        language="en",
                        category=article.get("category", "general"),
                        status="published",
                        is_active=True,
                        source_type="preset",
                        created_at=now,
                        updated_at=now,
                    )
                    await kb_repo.create(TENANT_ID, doc)
                    kb_created += 1
                except Exception as exc:
                    print(f"  [WARN] KB article failed: {exc}")

        agents = preset.get("agents_recommended", [])
        print(f"  KB articles created:  {kb_created}")

        # Step 5: Agent overlay/binding provisioning (WI-3025)
        agents_enabled = 0
        agents_skipped = 0
        if agents and not dry_run:
            from src.agents.plugins.bindings import SkillBindingService
            from src.agents.plugins.overlay import clear_resolution_cache
            from src.agents.plugins.registry import PluginAgentRegistry
            from src.multi_tenant.repositories.agent_bindings import (
                AgentSkillBindingRepository,
            )
            from src.multi_tenant.repositories.agent_overlays import (
                TenantAgentOverlayRepository,
            )

            registry = PluginAgentRegistry.get_instance()
            overlay_repo = TenantAgentOverlayRepository()
            binding_repo = AgentSkillBindingRepository()
            tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
            tenant_tier_level = tier_order.get(TIER.lower(), 0)

            for rec in agents:
                agent_id = rec.get("agent_id", "")
                agent_def = registry.get(agent_id) if agent_id else None
                if agent_def is None:
                    print(f"  [WARN] Agent {agent_id!r} not in registry, skipping")
                    continue

                required_level = tier_order.get(agent_def.tier_gate.lower(), 0)
                if tenant_tier_level < required_level:
                    print(f"  [SKIP] Agent {agent_id}: tier {TIER} < {agent_def.tier_gate}")
                    agents_skipped += 1
                    continue

                existing = await overlay_repo.get_overlay(TENANT_ID, agent_id)
                if existing is not None:
                    print(f"  [SKIP] Agent {agent_id}: overlay already exists")
                    agents_skipped += 1
                    continue

                await overlay_repo.upsert_overlay(TENANT_ID, agent_id, enabled=True)
                for skill_def in agent_def.skills:
                    existing_b = await binding_repo.get_binding(TENANT_ID, skill_def.skill_id)
                    if existing_b is None:
                        await binding_repo.upsert_binding(
                            TENANT_ID,
                            agent_id,
                            skill_def.skill_id,
                            mode=skill_def.mode,
                            enabled=True,
                        )
                agents_enabled += 1
                print(f"  [OK] Agent {agent_id}: overlay + {len(agent_def.skills)} bindings")

            if agents_enabled > 0:
                clear_resolution_cache()
                SkillBindingService.get_instance().invalidate(TENANT_ID)

        if agents:
            print(f"  Agents enabled:       {agents_enabled} (skipped: {agents_skipped})")

        phase_results["3b_preset"] = (
            f"OK — {preset_id}: config={len(config_fields)}, qa={qa_created}, kb={kb_created}, agents={agents_enabled}"
        )
    except Exception as e:
        print(f"  [ERROR] {e}")
        phase_results["3b_preset"] = f"ERROR: {e}"


async def seed(
    dry_run: bool = True,
    demo: bool = False,
    embed: bool = False,
    preset: str | None = None,
) -> None:
    """Run all seed phases in sequence (initialization)."""

    print()
    print("+" + "=" * 63 + "+")
    print("|  AGENT RED -- UNIFIED TENANT SEED" + " " * 29 + "|")
    print("|  Tenant: " + TENANT_ID + " " * (53 - len(TENANT_ID)) + "|")
    mode_str = "DRY RUN" if dry_run else "EXECUTE"
    print("|  Mode:   " + mode_str + " " * (53 - len(mode_str)) + "|")
    if preset:
        print("|  Preset: " + preset + " " * (53 - len(preset)) + "|")
    print("+" + "=" * 63 + "+")

    await phase_1_containers(dry_run)
    await phase_0_clean_partition(dry_run)
    await phase_2_tenant(dry_run)
    await phase_3_preferences(dry_run)
    await phase_3b_preset(dry_run, preset)
    # Phase 5 (KB articles) removed — initialization yields zero articles.
    # Use seed_knowledge_base.py separately if KB data is needed.
    await phase_6_platform_config(dry_run)
    await phase_7_demo_data(dry_run, demo)
    # Phase 4 runs AFTER demo data so superadmin with API key hash
    # overwrites any demo data record that lacks a key hash.
    await phase_4_team(dry_run)
    phase_8_summary()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified tenant seed for Agent Red Customer Experience",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Write to Cosmos DB (omit for dry-run preview)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Also seed demo conversations and customer profiles",
    )
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Also embed KB articles (requires Azure OpenAI)",
    )
    parser.add_argument(
        "--preset",
        type=str,
        default=None,
        metavar="PRESET_ID",
        help="Apply a vertical preset after seeding (e.g. returns_agent, order_support)",
    )
    args = parser.parse_args()

    dry_run = not args.execute

    # Safety gate: warn when targeting production database
    if not dry_run:
        db_name = os.environ.get("COSMOS_DB_DATABASE", "")
        if db_name and "staging" not in db_name and "dev" not in db_name:
            print(
                f"WARNING: COSMOS_DB_DATABASE={db_name} looks like production. "
                "Seeding will write to the production database."
            )
            if not os.environ.get("SEED_ALLOW_PRODUCTION"):
                print("Set SEED_ALLOW_PRODUCTION=1 to confirm, or change COSMOS_DB_DATABASE.")
                return

    await seed(dry_run=dry_run, demo=args.demo, embed=args.embed, preset=args.preset)


if __name__ == "__main__":
    asyncio.run(main())
