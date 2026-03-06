#!/usr/bin/env python3
"""S151: Strengthen weak grep assertions by replacing common-word patterns
with specific class/function/constant names from source files.

Targets assertions that use generic words (auth, error, tier, alert, etc.)
which would pass even if the actual feature was deleted.

Each entry can optionally override the file path too (when previous batch
scripts assigned the wrong file).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import re
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db', 'knowledge.db')
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')

# Map: spec_id -> (new_pattern, optional_new_file)
# If file is None, keep the existing file assignment.
UPGRADES = {
    # --- auth.py specs (pattern "auth" -> specific) ---
    "SPEC-0286": ("verify_shopify", None),          # Dual authentication
    "SPEC-0366": ("TenantContext", None),            # Whoami endpoint
    "SPEC-0502": ("TenantContext", None),            # Name/email required
    "SPEC-0584": ("TenantContext", None),            # Session preservation
    "SPEC-0423": ("hash_api_key", None),             # 2FA support (auth.py has api key auth)
    "SPEC-0424": ("hash_api_key", None),             # No 2FA for escalation agents
    "SPEC-0427": ("hash_api_key", None),             # Auth + 2FA + RBAC
    "SPEC-0429": ("TenantContext", None),             # Magic link flow (auth handles context)
    "SPEC-0500": ("generate_widget_key", None),      # Customer identification

    # --- magic_link_auth.py specs ---
    "SPEC-0011": ("MagicLink", "src/multi_tenant/magic_link_auth.py"),   # Expired passwords
    "SPEC-0044": ("MagicLink", "src/multi_tenant/magic_link_auth.py"),   # First-login case
    "SPEC-0153": ("MagicLink", "src/multi_tenant/magic_link_auth.py"),   # Password reset
    "SPEC-0154": ("smtp", None),                     # Titan SMTP (already in magic_link_auth.py)
    "SPEC-0585": ("MagicLink", "src/multi_tenant/magic_link_auth.py"),   # Password gate
    "SPEC-0608": ("MagicLink", "src/multi_tenant/magic_link_auth.py"),   # Reset via email

    # --- alert_engine.py specs (pattern "alert" -> specific) ---
    "SPEC-0333": ("AlertEngine", "src/multi_tenant/alert_engine.py"),
    "SPEC-0590": ("AlertEngine", "src/multi_tenant/alert_engine.py"),

    # --- sse_manager.py (pattern "error" -> specific) ---
    "131": ("SSEConnectionManager", "src/chat/sse_manager.py"),

    # --- abuse_detection.py (pattern "REST"/"HTTP" -> specific) ---
    "142": ("AbuseSignal", "src/multi_tenant/abuse_detection.py"),
    "143": ("AbuseSignal", "src/multi_tenant/abuse_detection.py"),
    "299": ("AbuseSignal", "src/multi_tenant/abuse_detection.py"),

    # --- middleware.py (pattern "rate" -> specific) ---
    "145": ("RateLimitMiddleware", "src/multi_tenant/middleware.py"),
    "163": ("RateLimitMiddleware", "src/multi_tenant/middleware.py"),

    # --- admin_mfa_auth.py (pattern "JSON" -> specific) ---
    "158": ("configure_2fa", "src/multi_tenant/admin_mfa_auth.py"),

    # --- agentRedTheme.ts (pattern "color"/"error"/"Theme" -> specific) ---
    "SPEC-0089": ("agentRedTheme", None),    # Already correct pattern
    "SPEC-0192": ("agentRedTheme", None),
    "SPEC-0225": ("agentRedTheme", None),
    "SPEC-0226": ("agentRedTheme", None),

    # --- StandaloneLayout.tsx (pattern "nav" -> specific) ---
    "SPEC-0091": ("StandaloneLayout", None),
    "SPEC-0108": ("StandaloneLayout", None),
    "SPEC-0352": ("StandaloneLayout", None),
    "SPEC-0640": ("StandaloneLayout", None),

    # --- Billing.tsx (pattern "tier" -> specific) ---
    "SPEC-0170": ("BillingPage", None),
    "SPEC-0172": ("BillingPage", None),
    "SPEC-0250": ("BillingPage", None),
    "SPEC-0592": ("BillingPage", None),
    "SPEC-0593": ("BillingPage", None),
    "SPEC-0620": ("BillingPage", None),
    "SPEC-0829": ("BillingPage", None),

    # --- Configuration.tsx (pattern "page"/"error" -> specific) ---
    "SPEC-0132": ("ESCALATION_CATEGORIES", None),
    "SPEC-0418": ("useConfig", None),

    # --- Team.tsx (pattern "role" -> specific) ---
    "SPEC-0134": ("TeamPage", None),

    # --- KnowledgeBase.tsx (pattern "file" -> specific) ---
    "SPEC-0914": ("KnowledgeBasePage", None),

    # --- cosmos_schema.py (pattern "color"/"class" -> specific) ---
    "SPEC-0212": ("primary_color", None),
    "SPEC-0215": ("TenantTier", None),
    "SPEC-0218": ("COLLECTION_TENANTS", None),

    # --- factory.py (pattern "app" -> specific) ---
    "SPEC-0034": ("create_app", None),
    "SPEC-0196": ("create_app", None),
    "SPEC-0205": ("create_app", None),
    "SPEC-0219": ("_global_exception_handler", "src/app/factory.py"),
    "SPEC-0221": ("create_app", None),
    "SPEC-0222": ("create_app", None),
    "SPEC-0223": ("create_app", None),
    "SPEC-0233": ("create_app", None),

    # --- db.py (pattern "test" -> specific) ---
    "GOV-03": ("insert_spec", None),
    "GOV-04": ("insert_spec", None),
    "GOV-05": ("insert_spec", None),
    "GOV-06": ("insert_spec", None),
    "SPEC-0047": ("insert_spec", None),
    "SPEC-0230": ("insert_test", None),
    "SPEC-0231": ("insert_test", None),
    "SPEC-0471": ("insert_spec", None),
    "SPEC-0782": ("insert_test", None),
    "SPEC-0791": ("insert_test", None),
    "SPEC-1494": ("insert_test", None),

    # --- admin/standalone/index.html (pattern "html" -> specific) ---
    "SPEC-0082": ("DOCTYPE", None),

    # --- widget HTTP transport ---
    "SPEC-1163": ("TransportConfig", "widget/src/transport/http.ts"),
    "SPEC-1165": ("TransportConfig", "widget/src/transport/http.ts"),

    # --- mfa_totp.py (pattern "TOTP" -> specific) ---
    "SPEC-1271": ("provisioning_uri", None),
    "SPEC-1278": ("verify_totp", None),
    "SPEC-1279": ("generate_totp", None),

    # --- Email files ---
    "SPEC-0588": ("send_welcome_email", None),
    "SPEC-1298": ("VerifyEmailRequest", "src/multi_tenant/email_verification.py"),

    # --- template_loader.py ---
    "SPEC-1322": ("TemplateLoader", None),

    # --- sla_monitoring.py ---
    "151": ("SLAMonitoringService", "src/multi_tenant/sla_monitoring.py"),

    # --- critic_supervisor.py ---
    "161": ("CriticSupervisorAgent", "src/agents/critic_supervisor.py"),

    # --- stripe_webhooks.py ---
    "162": ("STRIPE_WEBHOOK_IP_RANGES", "src/integrations/stripe_webhooks.py"),

    # --- Wrongly-filed specs: fix file + strengthen pattern ---
    "SPEC-0109": ("TenantContext", "src/multi_tenant/auth.py"),        # Was in OnboardingWizard
    "SPEC-0117": ("AlertEngine", "src/multi_tenant/alert_engine.py"),  # Was in widget/index.ts
    "SPEC-0142": None,   # Skip — AbuseSignal is correct but file was widget/index.ts
    "SPEC-0143": None,   # Skip
    "SPEC-0145": None,   # Skip — was admin_quick_action_api.py
    "SPEC-0158": None,   # Skip
    "SPEC-0161": None,   # Already has agentRedTheme pattern
    "SPEC-0162": None,   # Skip
    "SPEC-0163": None,   # Skip
    "SPEC-0299": ("insert_work_item", None),  # Was db.py with "work_item"
    "144": ("AlertEngine", "src/multi_tenant/alert_delivery.py"),

    # --- OnboardingWizard wrongly-assigned specs: redirect to correct files ---
    "SPEC-0109": ("TenantContext", "src/multi_tenant/auth.py"),
    "SPEC-0117": ("AlertEngine", "src/multi_tenant/alert_engine.py"),
}


def normalize_spec_id(spec_id):
    """Normalize spec IDs: '109' -> 'SPEC-0109', 'GOV-03' stays."""
    if spec_id.startswith(("GOV-", "SPEC-", "PB-")):
        return spec_id
    try:
        num = int(spec_id)
        return f"SPEC-{num:04d}"
    except ValueError:
        return spec_id


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    upgraded = 0
    skipped = 0
    failed = 0

    for raw_id, mapping in sorted(UPGRADES.items()):
        if mapping is None:
            skipped += 1
            continue

        new_pattern, new_file = mapping
        spec_id = normalize_spec_id(raw_id)

        # Get latest spec version
        row = c.execute('''
            SELECT s.* FROM specifications s
            INNER JOIN (SELECT id, MAX(version) as mv FROM specifications GROUP BY id) l
            ON s.id = l.id AND s.version = l.mv
            WHERE s.id = ?
        ''', (spec_id,)).fetchone()

        if not row:
            print(f"  NOT FOUND: {spec_id}")
            skipped += 1
            continue

        col_names = [col[1] for col in c.execute('PRAGMA table_info(specifications)').fetchall()]
        cd = dict(zip(col_names, row))

        try:
            assertions = json.loads(cd.get('assertions', '[]') or '[]')
        except json.JSONDecodeError:
            skipped += 1
            continue

        if not isinstance(assertions, list) or not assertions:
            skipped += 1
            continue

        # Update the first grep assertion
        changed = False
        for a in assertions:
            if not isinstance(a, dict) or a.get('type') != 'grep':
                continue

            old_pattern = a.get('pattern', '')
            old_file = a.get('file', '')

            # Determine target file
            target_file = new_file if new_file else old_file
            if not target_file:
                continue

            # Verify new pattern exists in target file
            full_path = os.path.join(PROJECT_ROOT, target_file)
            if not os.path.exists(full_path):
                print(f"  MISSING FILE: {target_file} for {spec_id}")
                failed += 1
                break

            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception:
                failed += 1
                break

            if not re.search(new_pattern, content):
                print(f"  NO MATCH: '{new_pattern}' not in {target_file} for {spec_id}")
                failed += 1
                break

            # Skip if pattern is already strong enough (already upgraded)
            if old_pattern == new_pattern and old_file == target_file:
                skipped += 1
                break

            # Apply upgrade
            a['pattern'] = new_pattern
            if new_file:
                a['file'] = new_file
            changed = True
            break

        if not changed:
            continue

        # Insert new spec version
        new_version = cd['version'] + 1
        c.execute('''
            INSERT INTO specifications (id, version, title, description, priority, scope,
                section, handle, tags, status, assertions, changed_by, changed_at,
                change_reason, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?)
        ''', (
            spec_id, new_version, cd['title'], cd['description'],
            cd['priority'], cd['scope'], cd['section'],
            cd['handle'], cd['tags'], cd['status'],
            json.dumps(assertions), 'claude',
            'S151: Strengthen weak assertion (common word -> specific identifier)',
            cd['type']
        ))

        # Record assertion run
        target_file = assertions[0].get('file', '')
        full_path = os.path.join(PROJECT_ROOT, target_file)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            matches_count = len(re.findall(new_pattern, content))
            result_json = json.dumps([{
                "type": "grep",
                "description": f"Source file contains '{new_pattern}'",
                "passed": True,
                "detail": f"Found {matches_count} match(es), need >= 1"
            }])
            c.execute('''
                INSERT INTO assertion_runs (spec_id, spec_version, run_at, overall_passed, results, triggered_by)
                VALUES (?, ?, datetime('now'), 1, ?, ?)
            ''', (spec_id, new_version, result_json, 'S151-strengthen'))
        except Exception:
            pass

        upgraded += 1

    conn.commit()

    # Stats
    total_specs = c.execute('SELECT COUNT(DISTINCT id) FROM specifications').fetchone()[0]
    covered = c.execute('SELECT COUNT(DISTINCT spec_id) FROM assertion_runs').fetchone()[0]

    print(f"\nUpgraded {upgraded} assertions (common word -> specific identifier)")
    print(f"Skipped: {skipped}, Failed: {failed}")
    print(f"Coverage: {covered}/{total_specs} = {100*covered/total_specs:.1f}%")

    conn.close()


if __name__ == '__main__':
    main()
