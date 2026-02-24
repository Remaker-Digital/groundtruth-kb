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
  [ ] All prior tenant data deleted from 9 containers (clean slate)
  [ ] 10 Cosmos DB containers created/verified
  [ ] Tenant document with API key + widget key
  [ ] Preferences document (config_state=draft, all merchant-configurable fields empty)
  [ ] 1 team member (superadmin) with per-user API key
  [ ] 54 KB articles seeded
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
    1. Containers   — 10 Cosmos DB containers with indexes
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

FQDN = os.environ.get("SEED_FQDN", "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io")

# Team members to create — ONLY the superadmin.
# A freshly provisioned tenant has exactly one team member: the owner
# who is logging in for the first time. Additional team members
# (escalation agents, admins, viewers) are added by the merchant
# through the Admin UI after onboarding.
TEAM_MEMBERS = [
    {
        "email": "mike@remakerdigital.com",
        "display_name": "Owner",
        "role": "superadmin",
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

    phase_results["0_clean_partition"] = f"OK — deleted {total_deleted} doc(s) across {len(TENANT_CONTAINERS)} containers"


# ---------------------------------------------------------------------------
# Phase 1: Create Cosmos DB containers
# ---------------------------------------------------------------------------

async def phase_1_containers(dry_run: bool) -> None:
    """Create all 10 Cosmos DB containers with indexes.

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

    generated_credentials["tenant_api_key"] = api_key
    generated_credentials["widget_key"] = widget_key

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
        rate_limit_rpm=50,
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

    # Add timestamps to quick actions
    qa_with_timestamps = []
    for qa in QUICK_ACTIONS:
        qa_copy = dict(qa)
        qa_copy["created_at"] = now
        qa_copy["updated_at"] = now
        qa_with_timestamps.append(qa_copy)

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
        quick_action_assignments=QUICK_ACTION_ASSIGNMENTS,
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

        # Store generated keys for summary
        generated_credentials[f"user_key_{email}"] = user_api_key

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

    phase_results["4_team"] = (
        f"{'DRY RUN' if dry_run else 'OK'} — {len(TEAM_MEMBERS)} members"
    )


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
    """Create 4 tier_defaults documents in platform_config."""
    print()
    print("=" * 65)
    print("  PHASE 6: Platform Config (Tier Defaults)")
    print("=" * 65)

    from src.multi_tenant.cosmos_schema import (
        TIER_DEFAULTS,
        PlatformConfigDocument,
    )

    now = datetime.now(timezone.utc).isoformat()
    tier_count = 0

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

        print(f"  {tier_name}: {tier_values['included_conversations']} convos, "
              f"{tier_values['rate_limit_rpm']} rpm")

        if not dry_run:
            from src.multi_tenant.repository import PlatformConfigRepository
            repo = PlatformConfigRepository()
            try:
                await repo.set_config(doc)
                print(f"    [OK] Upserted.")
            except Exception as e:
                print(f"    [ERROR] {e}")

        tier_count += 1

    phase_results["6_platform_config"] = (
        f"{'DRY RUN' if dry_run else 'OK'} — {tier_count} tier defaults"
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
    """Print all generated credentials and phase results."""
    print()
    print()
    print("=" * 65)
    print("  PHASE 8: SEED SUMMARY")
    print("=" * 65)

    # Credentials
    print()
    print("-" * 65)
    print("  CREDENTIALS (save these — they cannot be retrieved later)")
    print("-" * 65)
    print()

    if "tenant_api_key" in generated_credentials:
        print(f"  Tenant API Key:    {generated_credentials['tenant_api_key']}")
    if "widget_key" in generated_credentials:
        print(f"  Widget Key:        {generated_credentials['widget_key']}")

    print()
    print("  User API Keys:")
    for member_cfg in TEAM_MEMBERS:
        email = member_cfg["email"]
        key_name = f"user_key_{email}"
        if key_name in generated_credentials:
            print(f"    {member_cfg['display_name']} <{email}>")
            print(f"      {generated_credentials[key_name]}")
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

    # Next steps
    print("-" * 65)
    print("  NEXT STEPS")
    print("-" * 65)
    print()
    print("  1. Update .env.local ADMIN_PREVIEW_API_KEY with the superadmin User API Key")
    print("  2. Update MEMORY.md with the new widget key")
    print("  3. Open the Admin UI to verify dashboard data")
    print("  4. Test the widget on the storefront with the new widget key")
    print()
    print("=" * 65)
    print()


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

async def seed(
    dry_run: bool = True,
    demo: bool = False,
    embed: bool = False,
) -> None:
    """Run all seed phases in sequence (initialization)."""

    print()
    print("+" + "=" * 63 + "+")
    print("|  AGENT RED -- UNIFIED TENANT SEED" + " " * 29 + "|")
    print("|  Tenant: " + TENANT_ID + " " * (53 - len(TENANT_ID)) + "|")
    mode_str = "DRY RUN" if dry_run else "EXECUTE"
    print("|  Mode:   " + mode_str + " " * (53 - len(mode_str)) + "|")
    print("+" + "=" * 63 + "+")

    await phase_1_containers(dry_run)
    await phase_0_clean_partition(dry_run)
    await phase_2_tenant(dry_run)
    await phase_3_preferences(dry_run)
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
    args = parser.parse_args()

    dry_run = not args.execute
    await seed(dry_run=dry_run, demo=args.demo, embed=args.embed)


if __name__ == "__main__":
    asyncio.run(main())
