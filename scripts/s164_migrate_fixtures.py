"""S164: Migrate read-only E2E test classes to class-scoped fixtures.

Usage:
    python scripts/s164_migrate_fixtures.py              # Dry run
    python scripts/s164_migrate_fixtures.py --apply       # Apply changes
"""

import re
import sys
from pathlib import Path

MUTATION_CLASSES = {
    "TestInviteForm",
    "TestRoleChange",
    "TestEscalationCategories",
    "TestActiveDisabledToggle",
    "TestDeleteMember",
    "TestSuperadminProtection",
    "TestSaveConfig",
    "TestConfigHistory",
    "TestAddArticleModal",
    "TestDeleteArticle",
    "TestArticleActions",
    "TestDraftReply",
    "TestQuickActions",
    "TestCreateAction",
    "TestEditAction",
    "TestDeleteAction",
    "TestSaveWidget",
    "TestDisconnectButton",
    "TestMemoryToggle",
    "TestRetentionSettings",
    # S164 round 2: Additional mutation classes found during validation
    "TestNegativeInviteForm",
    "TestConfigActions",
    "TestConversationActions",
    "TestContactUsButton",
    "TestEscalationMutations",
    "TestArticleCRUD",
    "TestMobileLayout",
}

STANDALONE_FIXTURE_MAP = {
    "live_admin_page": "shared_admin_page",
    "live_dashboard_page": "shared_dashboard_page",
    "live_team_page": "shared_team_page",
    "live_config_page": "shared_config_page",
    "live_widget_page": "shared_widget_page",
    "live_inbox_page": "shared_inbox_page",
    "live_kb_page": "shared_kb_page",
    "live_billing_page": "shared_billing_page",
    "live_integrations_page": "shared_integrations_page",
    "live_memory_page": "shared_memory_page",
    "live_quick_actions_page": "shared_quick_actions_page",
}

PROVIDER_FIXTURE_MAP = {
    "live_provider_page": "shared_provider_page",
    "live_health_dashboard_page": "shared_health_dashboard_page",
    "live_tenant_directory_page": "shared_tenant_directory_page",
    "live_deployment_history_page": "shared_deployment_history_page",
    "live_queue_health_page": "shared_queue_health_page",
    "live_integration_health_page": "shared_integration_health_page",
    "live_status_page_page": "shared_status_page_page",
    "live_alert_config_page": "shared_alert_config_page",
    "live_diagnostics_page": "shared_diagnostics_page",
    "live_copilot_knowledge_page": "shared_copilot_knowledge_page",
    "live_pipeline_page": "shared_pipeline_page",
    "live_contact_messages_page": "shared_contact_messages_page",
    "live_service_messages_page": "shared_service_messages_page",
    "live_compliance_page": "shared_compliance_page",
    "live_secrets_page": "shared_secrets_page",
    "live_billing_health_page": "shared_billing_health_page",
    "live_cost_analytics_page": "shared_cost_analytics_page",
    "live_sla_trends_page": "shared_sla_trends_page",
    "live_abuse_detection_page": "shared_abuse_detection_page",
    "live_mfa_settings_page": "shared_mfa_settings_page",
}

SHOPIFY_FIXTURE_MAP = {
    "live_shopify_page": "shared_shopify_page",
    "live_shopify_dashboard": "shared_shopify_dashboard",
    "live_shopify_inbox": "shared_shopify_inbox",
    "live_shopify_configuration": "shared_shopify_configuration",
    "live_shopify_knowledge_base": "shared_shopify_knowledge_base",
    "live_shopify_widget": "shared_shopify_widget",
    "live_shopify_billing": "shared_shopify_billing",
    "live_shopify_settings": "shared_shopify_settings",
}


def get_fixture_map(filepath):
    parts = filepath.parts
    if "provider" in parts:
        return PROVIDER_FIXTURE_MAP
    if "shopify" in parts:
        return SHOPIFY_FIXTURE_MAP
    return STANDALONE_FIXTURE_MAP


def find_classes_in_file(content):
    classes = []
    lines = content.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"^class (Test\w+)", line)
        if m:
            classes.append((m.group(1), i, -1))
    for j in range(len(classes)):
        if j + 1 < len(classes):
            classes[j] = (classes[j][0], classes[j][1], classes[j + 1][1])
        else:
            classes[j] = (classes[j][0], classes[j][1], len(lines))
    return classes


def migrate_file(filepath, dry_run=True):
    content = filepath.read_text(encoding="utf-8")
    fixture_map = get_fixture_map(filepath)
    classes = find_classes_in_file(content)
    if not classes:
        return 0, 0, []

    lines = content.split("\n")
    migrated = 0
    skipped = 0
    changes = []
    modified = False

    for class_name, start, end in classes:
        if class_name in MUTATION_CLASSES:
            skipped += 1
            changes.append(f"  SKIP {class_name} (mutation class)")
            continue

        class_block = "\n".join(lines[start:end])
        has_live_fixture = any(old in class_block for old in fixture_map)
        if not has_live_fixture:
            continue

        for i in range(start, min(end, len(lines))):
            for old_name, new_name in fixture_map.items():
                if old_name in lines[i]:
                    lines[i] = lines[i].replace(old_name, new_name)
                    modified = True

        migrated += 1
        changes.append(f"  MIGRATE {class_name}")

    if modified and not dry_run:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return migrated, skipped, changes


def main():
    dry_run = "--apply" not in sys.argv
    base = Path(__file__).resolve().parent.parent / "tests" / "e2e_live"
    test_files = sorted(f for f in base.rglob("test_*.py") if f.name != "conftest.py")

    total_migrated = 0
    total_skipped = 0
    total_files = 0
    mode = "DRY RUN" if dry_run else "APPLYING"
    print(f"\n=== S164 Fixture Migration ({mode}) ===\n")

    for filepath in test_files:
        rel = filepath.relative_to(base)
        migrated, skipped, changes = migrate_file(filepath, dry_run)
        if changes:
            total_files += 1
            print(f"{rel}:")
            for c in changes:
                print(c)
            total_migrated += migrated
            total_skipped += skipped
            print()

    print("--- Summary ---")
    print(f"Files modified: {total_files}")
    print(f"Classes migrated to shared fixtures: {total_migrated}")
    print(f"Mutation classes kept on live fixtures: {total_skipped}")
    if dry_run:
        print("\nRun with --apply to write changes.")


if __name__ == "__main__":
    main()
