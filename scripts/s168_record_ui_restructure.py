#!/usr/bin/env python3
"""S168: Record UI restructure specs, WIs, and tests.
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db as kdb

d = kdb.KnowledgeDB()

# SPEC-1716: Agent identity grouping
d.insert_spec(
    id="SPEC-1716",
    title="Configuration page groups Brand & Persona + Custom Instructions into Agent identity section",
    status="implemented",
    changed_by="claude-s168",
    change_reason="Owner directive during manual UI testing",
    description=(
        "The Configuration page MUST group the Brand & Persona fields and Custom Instructions "
        "into a single Paper block titled Agent identity. Sub-sections are labeled as "
        "Brand & persona and Custom instructions with dimmed headings. "
        "Section order: Saved Configurations > Escalation > Agent identity > Language. "
        "[Source: admin/standalone/pages/Configuration.tsx]"
    ),
    priority="medium",
    scope="admin_ui",
    assertions=[{"type": "grep", "file": "admin/standalone/pages/Configuration.tsx", "pattern": "Agent identity"}],
)
print("SPEC-1716 recorded")

# SPEC-1717: Policy overrides on Knowledge Base page
d.insert_spec(
    id="SPEC-1717",
    title="Knowledge Base page includes Policy overrides section for config policy fields",
    status="implemented",
    changed_by="claude-s168",
    change_reason="Owner directive during manual UI testing",
    description=(
        "The Knowledge Base page MUST include a Policy overrides section at the top of the page "
        "(before the search/filter bar). This section contains return_window, return_policy, "
        "and shipping_info config fields. These values are authoritative over KB articles. "
        "The section uses the shared useAutoSaveDraft hook for automatic saving on focusout. "
        "Policy fields remain in the config API (PUT /api/config) -- only the UI location changes. "
        "[Source: admin/standalone/pages/KnowledgeBase.tsx]"
    ),
    priority="medium",
    scope="admin_ui",
    assertions=[{"type": "grep", "file": "admin/standalone/pages/KnowledgeBase.tsx", "pattern": "Policy overrides"}],
)
print("SPEC-1717 recorded")

# SPEC-1718: Auto-save on focusout
d.insert_spec(
    id="SPEC-1718",
    title="AI Configuration pages auto-save draft on focusout with subtle indicator",
    status="implemented",
    changed_by="claude-s168",
    change_reason="Owner directive during manual UI testing",
    description=(
        "All AI Configuration pages (Agent configuration, Widget configuration, Memory & privacy) "
        "MUST auto-save draft changes when any form field loses focus (blur event). "
        "The explicit Save draft inputs button is removed. A shared useAutoSaveDraft hook "
        "debounces blur events (500ms) and calls the page-specific save function. "
        "A subtle AutoSaveIndicator component shows a checkmark Saved text that fades after 1.5s. "
        "Error notifications are preserved -- only success toasts are replaced by the indicator. "
        "[Source: admin/shared/hooks/useAutoSaveDraft.ts, admin/shared/components/AutoSaveIndicator.tsx]"
    ),
    priority="medium",
    scope="admin_ui",
    assertions=[{"type": "grep", "file": "admin/shared/hooks/useAutoSaveDraft.ts", "pattern": "useAutoSaveDraft"}],
)
print("SPEC-1718 recorded")

# Work Items
for wi_id, title, desc, status in [
    (
        "WI-1234",
        "Group Brand & Persona + Custom Instructions into Agent identity section",
        "SPEC-1716: Wrap Brand & Persona and Custom Instructions into a single Agent identity Paper block on Configuration page.",
        "fixed",
    ),
    (
        "WI-1235",
        "Move Policies to Knowledge Base page as Policy overrides",
        "SPEC-1717: Remove Policies section from Configuration page and add Policy overrides section to Knowledge Base page with auto-save.",
        "fixed",
    ),
    (
        "WI-1236",
        "Replace Save draft inputs button with auto-save on focusout",
        "SPEC-1718: Remove manual save button from Configuration, Widget, and MemoryPrivacy pages. Add useAutoSaveDraft hook and AutoSaveIndicator component.",
        "fixed",
    ),
]:
    d.insert_work_item(
        id=wi_id,
        title=title,
        description=desc,
        component="admin_ui",
        origin="new",
        resolution_status=status,
        change_reason="Owner directive during manual UI testing",
        changed_by="claude-s168",
    )
    print(f"{wi_id} recorded")

# Tests
tests = [
    (
        "TEST-9667",
        "SPEC-1716",
        "Agent identity section exists in Configuration page",
        "structural",
        "Configuration.tsx contains Agent identity section header",
        "test_configuration.py",
        "TestConfigSectionOrder",
        "test_agent_identity_section_exists",
    ),
    (
        "TEST-9668",
        "SPEC-1716",
        "Agent identity contains Brand & persona sub-section",
        "structural",
        "Agent identity Paper contains Brand & persona subheading",
        "test_configuration.py",
        "TestConfigSectionOrder",
        "test_agent_identity_has_brand_persona",
    ),
    (
        "TEST-9669",
        "SPEC-1716",
        "Agent identity contains Custom instructions sub-section",
        "structural",
        "Agent identity Paper contains Custom instructions subheading",
        "test_configuration.py",
        "TestConfigSectionOrder",
        "test_agent_identity_has_custom_instructions",
    ),
    (
        "TEST-9670",
        "SPEC-1717",
        "Knowledge Base page has Policy overrides section",
        "structural",
        "KnowledgeBase.tsx contains Policy overrides section header",
        "test_knowledge_base.py",
        "TestPolicyOverrides",
        "test_policy_overrides_section_exists",
    ),
    (
        "TEST-9671",
        "SPEC-1717",
        "Policy overrides section contains return window field",
        "structural",
        "Policy overrides contains NumberInput for return window",
        "test_knowledge_base.py",
        "TestPolicyOverrides",
        "test_policy_overrides_has_return_window",
    ),
    (
        "TEST-9672",
        "SPEC-1717",
        "Policy overrides auto-saves via useAutoSaveDraft",
        "structural",
        "KnowledgeBase.tsx uses useAutoSaveDraft hook for policy section",
        "test_knowledge_base.py",
        "TestPolicyOverrides",
        "test_policy_overrides_uses_auto_save",
    ),
    (
        "TEST-9673",
        "SPEC-1718",
        "AutoSaveIndicator component renders Saved text",
        "structural",
        "AutoSaveIndicator shows checkmark Saved when saveCount > 0",
        "test_auto_save.py",
        "TestAutoSave",
        "test_indicator_renders_saved",
    ),
    (
        "TEST-9674",
        "SPEC-1718",
        "useAutoSaveDraft debounces blur events",
        "structural",
        "useAutoSaveDraft hook uses setTimeout for debouncing",
        "test_auto_save.py",
        "TestAutoSave",
        "test_hook_debounces_blur",
    ),
    (
        "TEST-9675",
        "SPEC-1718",
        "Configuration page has no Save draft inputs button",
        "structural",
        "Configuration.tsx does not contain Save draft inputs button text",
        "test_configuration.py",
        "TestAutoSave",
        "test_no_save_button_on_config",
    ),
    (
        "TEST-9676",
        "SPEC-1718",
        "Widget page has no Save draft inputs button",
        "structural",
        "Widget.tsx does not contain Save draft inputs button",
        "test_widget.py",
        "TestAutoSave",
        "test_no_save_button_on_widget",
    ),
    (
        "TEST-9677",
        "SPEC-1718",
        "MemoryPrivacy page has no Save draft inputs button",
        "structural",
        "MemoryPrivacy.tsx does not contain Save draft inputs button",
        "test_memory_privacy.py",
        "TestAutoSave",
        "test_no_save_button_on_memory",
    ),
    (
        "TEST-9678",
        "SPEC-1718",
        "Configuration page has AutoSaveIndicator",
        "structural",
        "Configuration.tsx renders AutoSaveIndicator component",
        "test_configuration.py",
        "TestAutoSave",
        "test_config_has_auto_save_indicator",
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
        change_reason=f"New test for {spec_id}",
        test_file=f"tests/e2e_mock/{t_file}",
        test_class=t_class,
        test_function=t_func,
    )
    print(f"{t_id} recorded")

print("\nDone: 3 specs, 3 WIs, 12 tests")
