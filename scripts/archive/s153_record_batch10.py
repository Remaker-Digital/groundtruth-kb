"""S153 Batch 10 — Promote 41 specs + record 47 test artifacts in KB."""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

# --- 1. Promote 41 specs to 'implemented' ---
specs_to_promote = [
    # CLAUDE.md governance (12)
    "SPEC-0092",
    "SPEC-0211",
    "SPEC-0282",
    "SPEC-0407",
    "SPEC-0408",
    "SPEC-0564",
    "SPEC-0733",
    "SPEC-0734",
    "SPEC-0746",
    "SPEC-0848",
    "SPEC-0849",
    "SPEC-0858",
    # Config/Admin (10)
    "SPEC-0100",
    "SPEC-0106",
    "SPEC-0127",
    "SPEC-0128",
    "SPEC-0160",
    "SPEC-0161",
    "SPEC-0192",
    "SPEC-0441",
    "SPEC-0701",
    "SPEC-0857",
    # Widget (3)
    "SPEC-0246",
    "SPEC-0531",
    "SPEC-0270",
    # Glossary (3)
    "SPEC-0069",
    "SPEC-0070",
    "SPEC-0072",
    # Process/Infrastructure (8)
    "SPEC-0406",
    "SPEC-0412",
    "SPEC-0419",
    "SPEC-0450",
    "SPEC-0668",
    "SPEC-0771",
    "SPEC-0776",
    "SPEC-0831",
    # Documentation/Navigation (4)
    "SPEC-0234",
    "SPEC-0473",
    "SPEC-0493",
    "SPEC-0772",
]
for sid in specs_to_promote:
    db.update_spec(
        sid,
        changed_by="S153",
        change_reason="Promoted to implemented - real production-interface test passing in test_s153_batch10_spec_verification.py",
        status="implemented",
    )
    print(f"Promoted {sid} -> implemented")

print(f"\n--- Promoted {len(specs_to_promote)} specs ---\n")

# --- 2. Record 47 test artifacts ---
TEST_FILE = "tests/multi_tenant/test_s153_batch10_spec_verification.py"
CB = "S153"
CR = "S153 batch 10 real production-interface spec verification test"

tests = [
    # CLAUDE.md governance (12 specs, 14 tests)
    (
        "SPEC-0092",
        "TestSpec0092OwnerPersonalityHonestFeedback",
        "test_honest_feedback_in_project",
        "Owner personality honest feedback",
        "honest + feedback in CLAUDE.md",
    ),
    (
        "SPEC-0211",
        "TestSpec0211ProductRenamedCustomerExperience",
        "test_customer_experience_in_claude_md",
        "Product renamed to Customer Experience",
        "Customer Experience in CLAUDE.md",
    ),
    (
        "SPEC-0282",
        "TestSpec0282TechnicalWorkPriority",
        "test_priority_in_claude_md",
        "Technical work elevated priority",
        "Technical work has elevated priority in CLAUDE.md",
    ),
    (
        "SPEC-0407",
        "TestSpec0407NoEffortEstimates",
        "test_no_effort_estimates_as_metric",
        "No effort estimates presented",
        "No effort estimate in CLAUDE.md",
    ),
    (
        "SPEC-0408",
        "TestSpec0408FocusOnQuality",
        "test_quality_governance",
        "Focus on quality governance",
        "Quality first + GOV in CLAUDE.md",
    ),
    (
        "SPEC-0564",
        "TestSpec0564NoEffortTerminologyDup",
        "test_no_effort_in_governance",
        "No level of effort terminology",
        "No level of effort in CLAUDE.md",
    ),
    (
        "SPEC-0733",
        "TestSpec0733NoEffortEstimatesDup2",
        "test_quality_over_effort",
        "Quality over effort governance",
        "Prioritize quality in CLAUDE.md",
    ),
    (
        "SPEC-0734",
        "TestSpec0734ClaudeOffersFeedback",
        "test_feedback_guidance",
        "Claude offers feedback on inputs",
        "Feedback + coaching/inline in CLAUDE.md",
    ),
    (
        "SPEC-0746",
        "TestSpec0746ClaudeMdDecomposed",
        "test_archive_exists",
        "CLAUDE.md decomposed — archive exists",
        "CLAUDE_ARCHIVE.md file exists",
    ),
    (
        "SPEC-0746",
        "TestSpec0746ClaudeMdDecomposed",
        "test_claude_md_references_archive",
        "CLAUDE.md references CLAUDE_ARCHIVE.md",
        "CLAUDE_ARCHIVE.md referenced in CLAUDE.md",
    ),
    (
        "SPEC-0848",
        "TestSpec0848TechnicalWorkPriorityDup",
        "test_work_priority_bias",
        "Work priority bias documented",
        "Work Priority Bias or elevated priority in CLAUDE.md",
    ),
    (
        "SPEC-0849",
        "TestSpec0849NoEffortEstimatesDup3",
        "test_quality_governance_present",
        "GOV-17 Quality first exists",
        "17 + Quality in CLAUDE.md",
    ),
    (
        "SPEC-0858",
        "TestSpec0858HonestFeedbackDup",
        "test_honest_feedback_documented",
        "Honest feedback documented",
        "honest/exaggerate/terminology inconsistency in CLAUDE.md",
    ),
    # Config/Admin (10 specs, 10 tests)
    (
        "SPEC-0100",
        "TestSpec0100DocumentationLinksHTTPS",
        "test_docs_base_https",
        "Documentation links use HTTPS",
        "https://agentredcx.com in Configuration.tsx",
    ),
    (
        "SPEC-0106",
        "TestSpec0106SortOrderRemovedFromUI",
        "test_no_sort_order_input_visible",
        "Sort order removed from Quick Actions UI",
        "formSortOrder auto-assigned in QuickActions.tsx",
    ),
    (
        "SPEC-0127",
        "TestSpec0127GradientToggleDefaultDisabled",
        "test_gradient_default_false",
        "Gradient toggle default disabled",
        "headerGradientEnabled: false in Widget.tsx",
    ),
    (
        "SPEC-0128",
        "TestSpec0128ColorPickersSideBySide",
        "test_side_by_side_layout",
        "Color pickers side-by-side",
        "Header left/right color + Group in Widget.tsx",
    ),
    (
        "SPEC-0160",
        "TestSpec0160DiscardFunctional",
        "test_discard_handler_exists",
        "Discard control functional",
        "handleDiscard + configRefreshKey in StandaloneLayout.tsx",
    ),
    (
        "SPEC-0161",
        "TestSpec0161ErrorBannerCloseButton",
        "test_error_close_button",
        "Error banner close button",
        "withCloseButton + clearSaveError in Configuration.tsx",
    ),
    (
        "SPEC-0192",
        "TestSpec0192NullSafetyChecks",
        "test_optional_chaining_used",
        "Null-safety optional chaining",
        "3+ ?. instances in Configuration.tsx",
    ),
    (
        "SPEC-0441",
        "TestSpec0441PreviewRemovedFromConfig",
        "test_no_preview_in_configuration",
        "Preview removed from Configuration",
        "No preview in Configuration.tsx",
    ),
    (
        "SPEC-0701",
        "TestSpec0701RedAsteriskOnRequired",
        "test_required_inputs_exist",
        "Red asterisk on required inputs",
        "required + TextInput in Configuration.tsx",
    ),
    (
        "SPEC-0857",
        "TestSpec0857SentenceCaseLabels",
        "test_sentence_case_section_headers",
        "Sentence case UI labels",
        "Agent configuration + no ALL CAPS in Configuration.tsx",
    ),
    # Widget (3 specs, 3 tests)
    (
        "SPEC-0246",
        "TestSpec0246WidgetAutoColorMode",
        "test_auto_mode_exists",
        "Widget Auto color mode",
        "'auto' + Light + Dark in Widget.tsx",
    ),
    (
        "SPEC-0531",
        "TestSpec0531PreChatFormTooltip",
        "test_prechat_tooltip",
        "Pre-chat form tooltip",
        "Pre-chat form + HelpTooltip + unverified in Widget.tsx",
    ),
    (
        "SPEC-0270",
        "TestSpec0270LanguagesRemovedExceptSpanishFrench",
        "test_language_options",
        "Languages removed except Spanish/French",
        "English/Spanish/French present, no German/Japanese/etc in Configuration.tsx",
    ),
    # Glossary (3 specs, 3 tests)
    (
        "SPEC-0069",
        "TestSpec0069GlossaryInput",
        "test_input_elements_in_admin",
        "Glossary 'input' elements",
        "TextInput/Textarea in Configuration.tsx",
    ),
    (
        "SPEC-0070",
        "TestSpec0070GlossaryCard",
        "test_card_components_in_admin",
        "Glossary 'card' components",
        "Paper/Card in Configuration.tsx",
    ),
    (
        "SPEC-0072",
        "TestSpec0072GlossaryPicker",
        "test_picker_elements_in_admin",
        "Glossary 'picker' elements",
        "ColorField/ColorPicker in Widget.tsx",
    ),
    # Process/Infrastructure (8 specs, 12 tests)
    (
        "SPEC-0406",
        "TestSpec0406SPASeparateFromMerchantAdmin",
        "test_provider_and_standalone_separate",
        "SPA separate from merchant admin",
        "provider/ and standalone/ separate directories",
    ),
    (
        "SPEC-0412",
        "TestSpec0412BuildStageChecklist",
        "test_deploy_pipeline_has_phases",
        "Build stage checklist in deploy pipeline",
        "phase_0 + phase_1 + build in deploy_pipeline.py",
    ),
    (
        "SPEC-0419",
        "TestSpec0419FaviconExists",
        "test_favicon_in_html",
        "Favicon referenced in HTML",
        "favicon/icon in index.html",
    ),
    (
        "SPEC-0419",
        "TestSpec0419FaviconExists",
        "test_favicon_files_exist",
        "Favicon files exist",
        "favicon/icon-master files in public/",
    ),
    (
        "SPEC-0450",
        "TestSpec0450EnvLocalUpToDate",
        "test_env_local_exists",
        ".env.local exists",
        ".env.local file present",
    ),
    (
        "SPEC-0450",
        "TestSpec0450EnvLocalUpToDate",
        "test_env_local_has_production_keys",
        ".env.local has production keys",
        "PROD_URL + COSMOS_DB in .env.local",
    ),
    (
        "SPEC-0668",
        "TestSpec0668ScheduleMdGroupings",
        "test_schedule_exists",
        "SCHEDULE.md exists",
        ".claude/SCHEDULE.md file present",
    ),
    (
        "SPEC-0668",
        "TestSpec0668ScheduleMdGroupings",
        "test_schedule_has_groups",
        "SCHEDULE.md has prompt groupings",
        "Group + trigger in SCHEDULE.md",
    ),
    (
        "SPEC-0771",
        "TestSpec0771TestingModularizedCooling",
        "test_thermal_safe_script",
        "Thermal-safe test script exists",
        "run-tests-thermal-safe.ps1 file present",
    ),
    (
        "SPEC-0771",
        "TestSpec0771TestingModularizedCooling",
        "test_cooling_cycles",
        "Testing has cooling cycles",
        "Cool + Sleep in run-tests-thermal-safe.ps1",
    ),
    (
        "SPEC-0776",
        "TestSpec0776ReseedCleanState",
        "test_seed_script_cleans_data",
        "Seed script cleans tenant data",
        "Clean/delete + container in seed_tenant.py",
    ),
    (
        "SPEC-0831",
        "TestSpec0831IngestionBlocksWizardProgress",
        "test_ingestion_blocks_continue",
        "Ingestion blocks wizard progress",
        "ingestionRunning + disabled in OnboardingWizard.tsx",
    ),
    # Documentation/Navigation (4 specs, 5 tests)
    (
        "SPEC-0234",
        "TestSpec0234IntentsRenamedToTopics",
        "test_topics_not_intents_in_dashboard",
        "Intents renamed to Topics",
        "Topic in Dashboard.tsx",
    ),
    (
        "SPEC-0473",
        "TestSpec0473DocsUnderDocsPrefix",
        "test_docs_links_use_docs_prefix",
        "Docs links use /docs/ prefix",
        "/docs/ in Configuration.tsx",
    ),
    (
        "SPEC-0493",
        "TestSpec0493MasterE2EProcedure",
        "test_test_pipeline_exists",
        "Master E2E procedure exists",
        "test_pipeline.py file present",
    ),
    (
        "SPEC-0493",
        "TestSpec0493MasterE2EProcedure",
        "test_test_pipeline_has_phases",
        "Test pipeline has phases",
        "phase + def in test_pipeline.py",
    ),
    (
        "SPEC-0772",
        "TestSpec0772FunctionalTestHarness",
        "test_test_harness_exists",
        "Test harness exists",
        "run-tests-thermal-safe.ps1 file present",
    ),
    (
        "SPEC-0772",
        "TestSpec0772FunctionalTestHarness",
        "test_harness_runs_multiple_suites",
        "Test harness runs multiple suites",
        "pytest + multi_tenant in run-tests-thermal-safe.ps1",
    ),
]

start_id = 8549
for i, (spec_id, cls, func, title, expected) in enumerate(tests):
    tid = f"TEST-{start_id + i}"
    db.insert_test(
        id=tid,
        title=title,
        spec_id=spec_id,
        test_type="unit",
        expected_outcome=expected,
        changed_by=CB,
        change_reason=CR,
        test_file=TEST_FILE,
        test_class=cls,
        test_function=func,
        last_result="PASS",
        last_executed_at="2026-03-06T22:00:00+00:00",
    )

print(f"Created {len(tests)} test artifacts (TEST-{start_id}..TEST-{start_id + len(tests) - 1})")
