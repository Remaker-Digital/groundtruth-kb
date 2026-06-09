#!/usr/bin/env python3
"""S168: Record config-vs-KB conflict detection specs, WIs, and tests.
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db as kdb

d = kdb.KnowledgeDB()

# ── SPEC-1713: Config-vs-KB Authority Rule ──
d.insert_spec(
    id="SPEC-1713",
    title="Config fields are authoritative over KB articles for their specific domain",
    status="specified",
    changed_by="claude-s168",
    change_reason="Owner-identified risk: config and KB can contain contradictory policy/brand information with no priority rule",
    description=(
        "When tenant configuration fields (return_policy, shipping_info, brand_voice, "
        "business_description, support_hours, custom_policies, warranty_info) conflict with "
        "knowledge base articles, the configuration field values MUST be treated as authoritative. "
        "The system prompt MUST include an explicit instruction: 'If the MERCHANT CONFIGURATION "
        "section conflicts with a KNOWLEDGE BASE article on policy values (durations, prices, "
        "terms, brand voice), the CONFIGURATION values are authoritative.' "
        "This rule applies to all fields with injected_in_prompt: true in fields.yaml. "
        "KB articles enrich and supplement config fields but cannot override them. "
        "[Source: src/multi_tenant/system_prompt_builder.py]"
    ),
    priority="high",
    scope="chat_pipeline",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/system_prompt_builder.py",
            "pattern": "authoritative|CONFIGURATION.*override|config.*priority",
        }
    ],
)
print("SPEC-1713 recorded")

# ── SPEC-1714: Extend KB Conflict Scanner ──
d.insert_spec(
    id="SPEC-1714",
    title="KB conflict scanner MUST cross-check config fields against KB articles",
    status="specified",
    changed_by="claude-s168",
    change_reason="Owner-identified risk: kb_conflict_scanner.py only checks KB-vs-KB, not config-vs-KB",
    description=(
        "The KB conflict scanner (kb_conflict_scanner.py) MUST be extended to compare tenant "
        "configuration field values (return_policy, shipping_info, warranty_info, support_hours, "
        "custom_policies, brand_voice, business_description) against all KB articles. "
        "Detection method: extract factual values (durations, prices, percentages, boolean phrases) "
        "from config fields and compare against KB article content using the existing factual "
        "conflict regex patterns. Conflicts are reported with severity levels: "
        "HIGH = numerical contradiction (e.g. 14 days vs 30 days), "
        "MEDIUM = qualitative mismatch (e.g. 'free shipping' vs 'shipping fee applies'), "
        "LOW = potential ambiguity. "
        "Results MUST appear in the existing scan endpoint response (POST /api/admin/knowledge/scan). "
        "Config-vs-KB conflicts MUST be labeled with source_type='config_vs_kb' to distinguish "
        "from article-vs-article conflicts. "
        "[Source: src/multi_tenant/kb_conflict_scanner.py]"
    ),
    priority="high",
    scope="knowledge_base",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/kb_conflict_scanner.py",
            "pattern": "config_vs_kb|config.*conflict|cross.check.*config",
        }
    ],
)
print("SPEC-1714 recorded")

# ── SPEC-1715: Admin UI Warning ──
d.insert_spec(
    id="SPEC-1715",
    title="Admin UI MUST warn when config fields conflict with KB articles",
    status="specified",
    changed_by="claude-s168",
    change_reason="Owner-identified risk: merchants have no visibility into config-vs-KB contradictions",
    description=(
        "The admin UI MUST display a warning when a tenant configuration field value conflicts "
        "with knowledge base article content. Two trigger points: "
        "(1) When saving agent configuration (Policies section): after PUT /api/admin/config, "
        "run a lightweight conflict check against top KB articles matching each policy field. "
        "Display yellow Alert component listing each conflict with the specific field, config value, "
        "and conflicting KB article title + excerpt. "
        "(2) When uploading or editing KB articles: after successful save, check the new article "
        "content against current config field values. Display warning if contradictions found. "
        "Warning format: 'Your [field_name] says [config_value] but KB article [article_title] "
        "says [kb_value]. Which is correct?' with action buttons to update config or edit article. "
        "Warning is advisory -- merchant can dismiss without action. "
        "[Source: admin/shared/ConfigurationPage.tsx, admin/shared/KnowledgeBasePage.tsx]"
    ),
    priority="medium",
    scope="admin_ui",
    assertions=[{"type": "grep", "file": "admin/shared/ConfigurationPage.tsx", "pattern": "conflict|warning|mismatch"}],
)
print("SPEC-1715 recorded")

# ── Work Items ──
d.insert_work_item(
    id="WI-1229",
    title="Add config-vs-KB authority rule to system prompt builder",
    description=(
        "SPEC-1713: Add explicit instruction to system_prompt_builder.py stating that "
        "MERCHANT CONFIGURATION values are authoritative over KB articles for policy fields. "
        "This prevents the model from blending contradictory values when config and KB disagree."
    ),
    component="chat_pipeline",
    origin="new",
    resolution_status="open",
    change_reason="New WI for SPEC-1713",
    changed_by="claude-s168",
)
print("WI-1229 recorded")

d.insert_work_item(
    id="WI-1230",
    title="Extend KB conflict scanner to cross-check config fields",
    description=(
        "SPEC-1714: Extend kb_conflict_scanner.py to compare tenant config field values "
        "(return_policy, shipping_info, etc.) against KB articles using existing factual "
        "conflict regex. Add source_type='config_vs_kb' to conflict results. "
        "Include in POST /api/admin/knowledge/scan response."
    ),
    component="knowledge_base",
    origin="new",
    resolution_status="open",
    change_reason="New WI for SPEC-1714",
    changed_by="claude-s168",
)
print("WI-1230 recorded")

d.insert_work_item(
    id="WI-1231",
    title="Add admin UI warnings for config-KB conflicts",
    description=(
        "SPEC-1715: Add conflict warning UI to ConfigurationPage (on save) and "
        "KnowledgeBasePage (on article upload/edit). Yellow Alert component showing "
        "specific field vs article contradictions with actionable resolution options."
    ),
    component="admin_ui",
    origin="new",
    resolution_status="open",
    change_reason="New WI for SPEC-1715",
    changed_by="claude-s168",
)
print("WI-1231 recorded")

# ── Tests ──
tests = [
    # SPEC-1713 tests (authority rule)
    (
        "TEST-9650",
        "SPEC-1713",
        "System prompt contains config authority instruction",
        "grep",
        "system_prompt_builder.py contains explicit instruction that config fields override KB for policy values",
        "test_config_kb_authority.py",
        "TestConfigAuthority",
        "test_prompt_contains_authority_instruction",
    ),
    (
        "TEST-9651",
        "SPEC-1713",
        "Config values appear before KB section in prompt",
        "structural",
        "MERCHANT CONFIGURATION section appears before VERIFIED KNOWLEDGE BASE section in assembled prompt",
        "test_config_kb_authority.py",
        "TestConfigAuthority",
        "test_config_before_kb_in_prompt_ordering",
    ),
    (
        "TEST-9652",
        "SPEC-1713",
        "Authority rule covers all injected_in_prompt fields",
        "structural",
        "Authority instruction references return_policy, shipping_info, brand_voice, support_hours, warranty_info",
        "test_config_kb_authority.py",
        "TestConfigAuthority",
        "test_authority_covers_all_injected_fields",
    ),
    (
        "TEST-9653",
        "SPEC-1713",
        "fields.yaml injected_in_prompt fields match authority list",
        "structural",
        "All fields with injected_in_prompt: true in fields.yaml are covered by the authority rule",
        "test_config_kb_authority.py",
        "TestConfigAuthority",
        "test_fields_yaml_injected_match_authority_list",
    ),
    # SPEC-1714 tests (scanner extension)
    (
        "TEST-9654",
        "SPEC-1714",
        "Scanner detects numerical duration contradiction between config and KB",
        "functional",
        "Scanner returns HIGH severity conflict when config return_policy says 14 days and KB article says 30 days",
        "test_config_kb_conflict_scanner.py",
        "TestConfigKBConflictScanner",
        "test_detects_numerical_duration_contradiction",
    ),
    (
        "TEST-9655",
        "SPEC-1714",
        "Scanner detects price contradiction between config and KB",
        "functional",
        "Scanner returns HIGH severity when config says free shipping over $50 and KB says $75",
        "test_config_kb_conflict_scanner.py",
        "TestConfigKBConflictScanner",
        "test_detects_price_contradiction",
    ),
    (
        "TEST-9656",
        "SPEC-1714",
        "Conflict results include config_vs_kb source_type",
        "structural",
        "Conflict results from config-vs-KB checks include source_type config_vs_kb",
        "test_config_kb_conflict_scanner.py",
        "TestConfigKBConflictScanner",
        "test_conflict_source_type_is_config_vs_kb",
    ),
    (
        "TEST-9657",
        "SPEC-1714",
        "Scanner checks all policy config fields",
        "functional",
        "Scanner compares return_policy, shipping_info, warranty_info, support_hours, custom_policies against KB",
        "test_config_kb_conflict_scanner.py",
        "TestConfigKBConflictScanner",
        "test_checks_all_policy_fields",
    ),
    (
        "TEST-9658",
        "SPEC-1714",
        "Scan endpoint includes config-vs-KB results",
        "functional",
        "POST /api/admin/knowledge/scan response contains config_vs_kb conflicts alongside article conflicts",
        "test_config_kb_conflict_scanner.py",
        "TestConfigKBConflictScanner",
        "test_scan_endpoint_includes_config_conflicts",
    ),
    (
        "TEST-9659",
        "SPEC-1714",
        "No false positive when config and KB agree",
        "functional",
        "Scanner returns no config_vs_kb conflicts when config and KB articles state the same values",
        "test_config_kb_conflict_scanner.py",
        "TestConfigKBConflictScanner",
        "test_no_false_positive_when_aligned",
    ),
    (
        "TEST-9660",
        "SPEC-1714",
        "Empty config fields skip conflict check",
        "functional",
        "Scanner skips comparison for config fields that are null or empty string",
        "test_config_kb_conflict_scanner.py",
        "TestConfigKBConflictScanner",
        "test_empty_config_fields_skip_check",
    ),
    # SPEC-1715 tests (admin UI warnings)
    (
        "TEST-9661",
        "SPEC-1715",
        "Config save triggers conflict check against KB",
        "functional",
        "After PUT /api/admin/config, UI runs conflict check and displays warning if contradictions found",
        "test_config_kb_warning_ui.py",
        "TestConfigKBWarningUI",
        "test_config_save_triggers_conflict_check",
    ),
    (
        "TEST-9662",
        "SPEC-1715",
        "Warning displays specific field and conflicting article",
        "functional",
        "Warning Alert shows field name, config value, KB article title, and conflicting KB excerpt",
        "test_config_kb_warning_ui.py",
        "TestConfigKBWarningUI",
        "test_warning_shows_field_and_article_details",
    ),
    (
        "TEST-9663",
        "SPEC-1715",
        "KB article upload triggers conflict check against config",
        "functional",
        "After saving a KB article, UI checks content against current config field values",
        "test_config_kb_warning_ui.py",
        "TestConfigKBWarningUI",
        "test_kb_upload_triggers_conflict_check",
    ),
    (
        "TEST-9664",
        "SPEC-1715",
        "Warning is dismissible without action",
        "functional",
        "Merchant can close the conflict warning without making changes -- advisory only",
        "test_config_kb_warning_ui.py",
        "TestConfigKBWarningUI",
        "test_warning_is_dismissible",
    ),
    (
        "TEST-9665",
        "SPEC-1715",
        "No warning shown when no conflicts exist",
        "functional",
        "Config save with no KB contradictions shows no warning Alert",
        "test_config_kb_warning_ui.py",
        "TestConfigKBWarningUI",
        "test_no_warning_when_no_conflicts",
    ),
]

for t_id, spec_id, title, t_type, expected, t_file, t_class, t_func in tests:
    d.insert_test(
        id=t_id,
        title=title,
        spec_id=spec_id,
        test_type=t_type,
        expected_outcome=expected,
        changed_by="claude-s168",
        change_reason=f"New test for {spec_id} -- config-vs-KB conflict detection",
        test_file=f"tests/multi_tenant/{t_file}",
        test_class=t_class,
        test_function=t_func,
    )
    print(f"{t_id} recorded")

print("\nDone: 3 specs, 3 WIs, 16 tests")
