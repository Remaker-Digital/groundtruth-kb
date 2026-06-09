"""S170 KB artifact recording — config-vs-KB authority + email template cleanup.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()

# ─────────────────────────────────────────────────────────────────────
# Track 1: Config-vs-KB Authority (SPEC-1713/1714/1715, WI-1229/1230/1231)
# ─────────────────────────────────────────────────────────────────────

# Promote specs to implemented
for spec_id in ["SPEC-1713", "SPEC-1714", "SPEC-1715"]:
    kdb.update_spec(
        spec_id,
        changed_by="S170",
        change_reason="Implementation complete and tested (40/40 pass)",
        status="implemented",
    )
    print(f"  OK: {spec_id} promoted to implemented")

# Resolve WIs
for wi_id, spec_id in [
    ("WI-1229", "SPEC-1713"),
    ("WI-1230", "SPEC-1714"),
    ("WI-1231", "SPEC-1715"),
]:
    kdb.update_work_item(
        wi_id,
        changed_by="S170",
        change_reason=f"Implementation complete, {spec_id} promoted to implemented",
        resolution_status="resolved",
        stage="resolved",
    )
    print(f"  OK: {wi_id} resolved")

# Insert test artifacts for config-vs-KB authority tests
# File: tests/multi_tenant/test_config_vs_kb_authority.py
config_kb_tests = [
    # TestConfigAuthoritySystemPrompt (SPEC-1713)
    (
        "test_config_field_produces_authority_block",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Config authority block appears in prompt when config fields are set",
    ),
    (
        "test_empty_config_no_authority_block",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "No authority block when all config fields are empty/default",
    ),
    (
        "test_authority_block_lists_each_field",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Authority block lists each configured field name",
    ),
    (
        "test_authority_block_override_wording",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Authority block uses 'override' wording",
    ),
    (
        "test_authority_block_position_after_persona",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Authority block placed after persona section in prompt",
    ),
    (
        "test_multiple_config_fields_all_listed",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Multiple configured fields are all listed in authority block",
    ),
    (
        "test_partial_config_only_set_fields_listed",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Only explicitly set fields appear in authority block",
    ),
    (
        "test_config_authority_with_custom_instructions",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Custom instructions config field triggers authority block",
    ),
    (
        "test_config_authority_with_brand_name",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Brand name config field triggers authority block",
    ),
    (
        "test_config_authority_with_language",
        "TestConfigAuthoritySystemPrompt",
        "SPEC-1713",
        "Language config field triggers authority block",
    ),
    # TestKBConflictScanner (SPEC-1714)
    (
        "test_no_conflicts_when_config_empty",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner returns no conflicts when config fields are empty",
    ),
    (
        "test_detects_language_conflict",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner detects KB article conflicting with language config",
    ),
    (
        "test_detects_brand_name_conflict",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner detects KB article conflicting with brand name config",
    ),
    (
        "test_detects_persona_conflict",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner detects KB article conflicting with persona config",
    ),
    (
        "test_multiple_conflicts_detected",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner detects multiple simultaneous conflicts",
    ),
    (
        "test_no_false_positive_on_unrelated_article",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner does not flag unrelated KB articles as conflicts",
    ),
    (
        "test_conflict_includes_article_id",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Conflict result includes the conflicting article ID",
    ),
    (
        "test_conflict_includes_config_field_name",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Conflict result includes the authoritative config field name",
    ),
    (
        "test_conflict_includes_severity",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Conflict result includes severity level",
    ),
    (
        "test_scanner_handles_empty_kb",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner handles empty KB article list gracefully",
    ),
    (
        "test_scanner_case_insensitive_matching",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner matches conflicts case-insensitively",
    ),
    (
        "test_scanner_partial_match_on_instruction_keywords",
        "TestKBConflictScanner",
        "SPEC-1714",
        "Scanner detects partial instruction keyword matches",
    ),
    # TestConfigConflictWarningUI (SPEC-1715)
    (
        "test_warning_banner_when_conflicts_detected",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Warning banner shown when config-vs-KB conflicts detected",
    ),
    (
        "test_no_warning_when_no_conflicts",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "No warning banner when no conflicts exist",
    ),
    (
        "test_warning_lists_conflicting_articles",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Warning banner lists the conflicting KB article titles",
    ),
    (
        "test_warning_links_to_kb_page",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Warning includes link to KB page for resolution",
    ),
    (
        "test_warning_on_configuration_page",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Configuration page shows conflict warning",
    ),
    (
        "test_warning_on_kb_page",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Knowledge Base page shows conflict warning",
    ),
    ("test_warning_dismissible", "TestConfigConflictWarningUI", "SPEC-1715", "Warning banner can be dismissed"),
    (
        "test_warning_reappears_on_new_conflict",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Warning reappears when new conflict is introduced",
    ),
    (
        "test_warning_severity_color_coding",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Warning uses appropriate severity color coding",
    ),
    (
        "test_warning_config_field_name_displayed",
        "TestConfigConflictWarningUI",
        "SPEC-1715",
        "Warning shows which config field is authoritative",
    ),
    # TestConfigVsKBIntegration
    (
        "test_full_flow_config_set_then_kb_conflict_detected",
        "TestConfigVsKBIntegration",
        "SPEC-1713",
        "Full integration: config set → KB article added → conflict detected → warning shown",
    ),
    (
        "test_full_flow_conflict_resolved_by_removing_article",
        "TestConfigVsKBIntegration",
        "SPEC-1714",
        "Full integration: conflict resolved by removing conflicting KB article",
    ),
    (
        "test_full_flow_conflict_resolved_by_clearing_config",
        "TestConfigVsKBIntegration",
        "SPEC-1714",
        "Full integration: conflict resolved by clearing config field",
    ),
    (
        "test_authority_rule_in_prompt_with_active_conflicts",
        "TestConfigVsKBIntegration",
        "SPEC-1713",
        "Authority rule present in prompt even when KB conflicts exist",
    ),
    (
        "test_scanner_invoked_on_config_save",
        "TestConfigVsKBIntegration",
        "SPEC-1714",
        "Conflict scanner invoked automatically on config save",
    ),
    (
        "test_scanner_invoked_on_kb_article_save",
        "TestConfigVsKBIntegration",
        "SPEC-1714",
        "Conflict scanner invoked automatically on KB article save",
    ),
    (
        "test_prompt_builder_uses_config_over_kb",
        "TestConfigVsKBIntegration",
        "SPEC-1713",
        "Prompt builder uses config field value over conflicting KB content",
    ),
    (
        "test_warning_count_matches_conflict_count",
        "TestConfigVsKBIntegration",
        "SPEC-1715",
        "Warning banner count matches actual conflict count",
    ),
]

test_id = 9685  # Start after current max TEST-9684
test_file = "tests/multi_tenant/test_config_vs_kb_authority.py"
for func_name, class_name, spec_id, desc in config_kb_tests:
    tid = f"TEST-{test_id}"
    kdb.insert_test(
        id=tid,
        title=f"{class_name}.{func_name}",
        spec_id=spec_id,
        test_type="unit",
        expected_outcome=desc,
        changed_by="S170",
        change_reason="Config-vs-KB authority test artifacts",
        test_file=test_file,
        test_class=class_name,
        test_function=func_name,
        last_result="PASS",
    )
    test_id += 1

print(f"  OK: {test_id - 9685} config-vs-KB test artifacts recorded (TEST-9685..TEST-{test_id - 1})")

# ─────────────────────────────────────────────────────────────────────
# Track 2: Email template cleanup (SPEC-1723, WI-1241)
# ─────────────────────────────────────────────────────────────────────

# New spec for email template key removal
kdb.insert_spec(
    id="SPEC-1723",
    title="Email templates must not contain API key or widget key blocks (SPEC-1673 enforcement)",
    status="implemented",
    changed_by="S170",
    change_reason="Owner directive: remove grey 'ADMIN API KEY' and 'WIDGET KEY' blocks from all email templates",
    description=(
        "Welcome email template must NOT contain grey key display blocks for "
        "'Admin API Key' or 'Widget Key'. Keys are accessible from admin console only (SPEC-1673). "
        "Template directs users to sign in to admin dashboard to find keys. "
        "send_welcome_email() retains superadmin_key and widget_key parameters for call-site "
        "compatibility but silently ignores them. [Source: src/multi_tenant/welcome_email.py]"
    ),
    assertions=[
        {"type": "grep_absent", "pattern": "Admin API Key", "file": "src/multi_tenant/welcome_email.py"},
        {"type": "grep_absent", "pattern": "Widget Key", "file": "src/multi_tenant/welcome_email.py"},
        {"type": "grep", "pattern": "admin dashboard", "file": "src/multi_tenant/welcome_email.py"},
    ],
)
print("  OK: SPEC-1723 created (email key block removal)")

# New spec for email template admin URLs
kdb.insert_spec(
    id="SPEC-1724",
    title="All transactional email templates must include clickable admin dashboard URL",
    status="implemented",
    changed_by="S170",
    change_reason="Owner directive: each email must have clickable URL to admin UI",
    description=(
        "All transactional email templates must include a prominently styled CTA button linking "
        "to the admin dashboard. Templates use _build_admin_login_url() from welcome_email.py "
        "for URL resolution (explicit > STANDALONE_ADMIN_URL > PROD_URL > fallback). "
        "Applies to: welcome, login notification, SPA recovery, access expiry, trial expiry. "
        "Magic link, tenant recovery, email verification, and email change have their own "
        "purpose-specific URLs. [Source: src/multi_tenant/login_notification.py]"
    ),
    assertions=[
        {"type": "grep", "pattern": "Sign in to Dashboard", "file": "src/multi_tenant/login_notification.py"},
        {"type": "grep", "pattern": "_build_admin_login_url", "file": "src/multi_tenant/login_notification.py"},
        {"type": "grep", "pattern": "Sign in to Dashboard", "file": "src/multi_tenant/spa_recovery.py"},
        {"type": "grep", "pattern": "_build_admin_login_url", "file": "src/multi_tenant/spa_recovery.py"},
    ],
)
print("  OK: SPEC-1724 created (email admin URLs)")

# WI for the email work
kdb.insert_work_item(
    id="WI-1241",
    title="Remove key blocks from welcome email + add admin URLs to login_notification and spa_recovery",
    origin="new",
    component="email",
    resolution_status="resolved",
    changed_by="S170",
    change_reason="Owner directive completed — key blocks removed, admin URLs added, 109 tests pass",
    source_spec_id="SPEC-1723",
    stage="resolved",
    description=(
        "S170: (1) Removed ADMIN API KEY and WIDGET KEY grey blocks from _WELCOME_EMAIL_BODY. "
        "(2) Added _build_admin_login_url() + CTA button to login_notification.py. "
        "(3) Added _build_admin_login_url() + CTA button to spa_recovery.py. "
        "(4) Updated 3 test files. 109/109 email tests pass."
    ),
)
print("  OK: WI-1241 created and resolved (email template cleanup)")

# Insert test artifacts for email template tests
email_tests = [
    # test_welcome_email.py updates
    (
        "test_template_does_not_contain_key_blocks",
        "TestWelcomeEmailTemplate",
        "SPEC-1723",
        "tests/multi_tenant/test_welcome_email.py",
        "Welcome email template does not contain Admin API Key or Widget Key blocks",
    ),
    (
        "test_template_directs_to_admin_console_for_keys",
        "TestWelcomeEmailTemplate",
        "SPEC-1723",
        "tests/multi_tenant/test_welcome_email.py",
        "Welcome email directs users to admin dashboard for keys",
    ),
    (
        "test_template_contains_admin_login_url",
        "TestWelcomeEmailTemplate",
        "SPEC-1724",
        "tests/multi_tenant/test_welcome_email.py",
        "Welcome email contains admin login URL",
    ),
    (
        "test_template_admin_url_in_next_steps",
        "TestWelcomeEmailTemplate",
        "SPEC-1724",
        "tests/multi_tenant/test_welcome_email.py",
        "Welcome email Next Steps links to admin dashboard",
    ),
    (
        "test_template_admin_url_button",
        "TestWelcomeEmailTemplate",
        "SPEC-1724",
        "tests/multi_tenant/test_welcome_email.py",
        "Welcome email has CTA button with admin URL and brand color",
    ),
    (
        "test_acs_email_contains_admin_url",
        "TestSendWelcomeEmail",
        "SPEC-1724",
        "tests/multi_tenant/test_welcome_email.py",
        "ACS email body includes admin login URL",
    ),
    (
        "test_explicit_admin_url_overrides_env",
        "TestSendWelcomeEmail",
        "SPEC-1724",
        "tests/multi_tenant/test_welcome_email.py",
        "Explicit admin_login_url param overrides environment variable",
    ),
]

for func_name, class_name, spec_id, tfile, desc in email_tests:
    tid = f"TEST-{test_id}"
    kdb.insert_test(
        id=tid,
        title=f"{class_name}.{func_name}",
        spec_id=spec_id,
        test_type="unit",
        expected_outcome=desc,
        changed_by="S170",
        change_reason="Email template cleanup test artifacts",
        test_file=tfile,
        test_class=class_name,
        test_function=func_name,
        last_result="PASS",
    )
    test_id += 1

print(
    f"  OK: {test_id - 9685 - len(config_kb_tests)} email test artifacts recorded (TEST-{9685 + len(config_kb_tests)}..TEST-{test_id - 1})"
)
print(f"\n  Total: {test_id - 9685} new test artifacts, 2 specs, 1 WI, 3 spec promotions, 3 WI resolutions")
