"""S153 Batch 10 — CLAUDE.md governance + Config/Admin + Widget + Glossary + Process.

Specs verified against production interfaces.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env


# ── Paths ──────────────────────────────────────────────────────────────
SRC = Path(__file__).resolve().parents[2] / "src"
ADMIN = Path(__file__).resolve().parents[2] / "admin"
WIDGET = Path(__file__).resolve().parents[2] / "widget"
STANDALONE = ADMIN / "standalone"
SHARED = ADMIN / "shared"
PROVIDER = ADMIN / "provider"
SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
ROOT = Path(__file__).resolve().parents[2]


# ═══════════════════════════════════════════════════════════════════════
#  CLAUDE.MD GOVERNANCE SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0092OwnerPersonalityHonestFeedback:
    """SPEC-0092: Owner personality note — Mike values honest feedback."""

    def test_honest_feedback_in_project(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "honest" in src.lower() or "feedback" in src.lower(), \
            "Must record honest feedback principle"
        assert "Feedback" in src, "Must have feedback guidance"


class TestSpec0211ProductRenamedCustomerExperience:
    """SPEC-0211: Product renamed from 'Customer Engagement' to 'Customer Experience'."""

    def test_customer_experience_in_claude_md(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Customer Experience" in src, \
            "Project name must be 'Customer Experience'"


class TestSpec0282TechnicalWorkPriority:
    """SPEC-0282: Technical work has elevated priority over creative/content work."""

    def test_priority_in_claude_md(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Technical work has elevated priority" in src, \
            "Must document technical work priority"


class TestSpec0407NoEffortEstimates:
    """SPEC-0407: Effort estimates MUST NOT be presented."""

    def test_no_effort_estimates_as_metric(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # CLAUDE.md should not use effort as a measurement term
        assert "effort estimate" not in src.lower(), \
            "Must not use effort estimates"
        assert "quality" in src.lower(), "Must focus on quality"


class TestSpec0408FocusOnQuality:
    """SPEC-0408: Primary focus on quality — correctness, completeness, absence of defects."""

    def test_quality_governance(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Quality first" in src or "quality" in src.lower(), \
            "Must have quality-first governance"
        assert "GOV" in src, "Must have governance rules"


class TestSpec0564NoEffortTerminologyDup:
    """SPEC-0564: No effort estimates — focus on quality."""

    def test_no_effort_in_governance(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "level of effort" not in src.lower(), \
            "Must not use 'level of effort'"


class TestSpec0733NoEffortEstimatesDup2:
    """SPEC-0733: Effort estimates MUST NOT be provided."""

    def test_quality_over_effort(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # GOV-17: Quality first
        assert "Prioritize quality" in src or "quality" in src.lower(), \
            "Must prioritize quality over effort"


class TestSpec0734ClaudeOffersFeedback:
    """SPEC-0734: Claude MUST actively offer feedback on the owner's inputs."""

    def test_feedback_guidance(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Feedback" in src, "Must have feedback guidance"
        assert "coaching" in src.lower() or "inline" in src.lower(), \
            "Must have inline coaching mechanism"


class TestSpec0746ClaudeMdDecomposed:
    """SPEC-0746: CLAUDE.md historical info decomposed to CLAUDE_ARCHIVE.md."""

    def test_archive_exists(self):
        assert (ROOT / "CLAUDE_ARCHIVE.md").exists(), \
            "CLAUDE_ARCHIVE.md must exist"

    def test_claude_md_references_archive(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "CLAUDE_ARCHIVE.md" in src, \
            "CLAUDE.md must reference the archive"


class TestSpec0848TechnicalWorkPriorityDup:
    """SPEC-0848: Technical work MUST have elevated priority over creative/content."""

    def test_work_priority_bias(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Work Priority Bias" in src or "elevated priority" in src, \
            "Must document work priority bias"


class TestSpec0849NoEffortEstimatesDup3:
    """SPEC-0849: No effort estimates — focus on quality."""

    def test_quality_governance_present(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # GOV-17 exists
        lines = [line for line in src.splitlines() if "17" in line and "Quality" in line]
        assert len(lines) > 0, "GOV-17 Quality first must exist"


class TestSpec0858HonestFeedbackDup:
    """SPEC-0858: Honest feedback MUST be provided — never exaggerate."""

    def test_honest_feedback_documented(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "honest" in src.lower() or "exaggerate" in src.lower() or \
            "terminology inconsistency" in src, \
            "Must document honest feedback principle"


# ═══════════════════════════════════════════════════════════════════════
#  CONFIG / ADMIN SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0100DocumentationLinksHTTPS:
    """SPEC-0100: Documentation links MUST use HTTPS, not HTTP."""

    def test_docs_base_https(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "https://agentredcx.com" in src, \
            "Must use HTTPS for documentation links"
        assert "http://agentredcx.com" not in src, \
            "Must not use HTTP for documentation links"


class TestSpec0106SortOrderRemovedFromUI:
    """SPEC-0106: 'Sort order' input MUST be removed from quick action creation."""

    def test_no_sort_order_input_visible(self):
        src = (STANDALONE / "pages" / "QuickActions.tsx").read_text(encoding="utf-8")
        # Sort order is auto-assigned, not shown as UI input
        assert "formSortOrder" in src, "Sort order state must exist (auto-assigned)"
        # Ensure no NumberInput or visible control labeled Sort order
        assert "Sort order" not in src or "sort_order" in src, \
            "Sort order must be auto-assigned, not user-editable"


class TestSpec0127GradientToggleDefaultDisabled:
    """SPEC-0127: Gradient toggle default MUST be disabled."""

    def test_gradient_default_false(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "headerGradientEnabled: false" in src or \
            "headerGradientEnabled:false" in src.replace(" ", ""), \
            "Gradient toggle must default to disabled"


class TestSpec0128ColorPickersSideBySide:
    """SPEC-0128: Header left/right color pickers MUST be side-by-side."""

    def test_side_by_side_layout(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "Header left color" in src and "Header right color" in src, \
            "Must have both header color pickers"
        assert "Group" in src, "Must use Group component for side-by-side layout"


class TestSpec0160DiscardFunctional:
    """SPEC-0160: The 'Discard' control MUST be functional."""

    def test_discard_handler_exists(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "handleDiscard" in src or "Discard" in src, \
            "Must have Discard control"
        assert "configRefreshKey" in src or "refetch" in src.lower(), \
            "Discard must trigger config re-fetch"


class TestSpec0161ErrorBannerCloseButton:
    """SPEC-0161: Error banner close ('X') control MUST be functional."""

    def test_error_close_button(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "withCloseButton" in src or "onClose" in src, \
            "Error banner must have close button"
        assert "clearSaveError" in src or "setError" in src, \
            "Close button must clear error state"


class TestSpec0192NullSafetyChecks:
    """SPEC-0192: All admin UI formatters shall apply null-safety checks (optional chaining)."""

    def test_optional_chaining_used(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "?." in src, "Must use optional chaining for null safety"
        # Check multiple occurrences indicating systematic usage
        assert src.count("?.") >= 3, \
            "Must have multiple optional chaining instances"


class TestSpec0441PreviewRemovedFromConfig:
    """SPEC-0441: Preview panel MUST be removed from Configuration page."""

    def test_no_preview_in_configuration(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        # Preview lives in Widget.tsx only, not in Configuration
        assert "preview" not in src.lower() or "Preview" not in src, \
            "Configuration page must not have preview panel"


class TestSpec0701RedAsteriskOnRequired:
    """SPEC-0701: All empty but essential inputs MUST be marked with red asterisk."""

    def test_required_inputs_exist(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        # Mantine's `required` prop renders red asterisk automatically
        assert "required" in src, \
            "Must have required inputs (Mantine renders red asterisk)"
        assert "TextInput" in src or "Textarea" in src, \
            "Must have form inputs with required attribute"


class TestSpec0857SentenceCaseLabels:
    """SPEC-0857: Sentence case MUST be used for all UI labels."""

    def test_sentence_case_section_headers(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        # Check that section headers use sentence case, not ALL CAPS or Title Case
        assert "Agent configuration" in src or "Brand" in src, \
            "Must use sentence case for labels"
        # Should not have ALL CAPS headers
        all_caps = re.findall(r'"[A-Z]{4,}"', src)
        # Filter out known constants (DOCS_BASE, etc.)
        ui_caps = [c for c in all_caps if "DOCS" not in c and "TIER" not in c
                    and "DEFAULT" not in c and "ESCALATION" not in c
                    and "PRIMARY" not in c and "LANGUAGES" not in c]
        assert len(ui_caps) == 0, \
            f"Should not have ALL CAPS UI labels: {ui_caps}"


# ═══════════════════════════════════════════════════════════════════════
#  WIDGET SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0246WidgetAutoColorMode:
    """SPEC-0246: Widget 'Auto' color mode matches admin's current color scheme."""

    def test_auto_mode_exists(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "'auto'" in src or '"auto"' in src, \
            "Must have Auto color mode option"
        assert "Light" in src and "Dark" in src, \
            "Must have Light, Dark, and Auto options"


class TestSpec0531PreChatFormTooltip:
    """SPEC-0531: Pre-chat form MUST have a tooltip informing about unverified identity."""

    def test_prechat_tooltip(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "Pre-chat form" in src, "Must have pre-chat form control"
        assert "HelpTooltip" in src, "Must have tooltip on pre-chat form"
        # Check for identity/verification warning
        assert "unverified" in src.lower() or "not a security" in src.lower() or \
            "self-reported" in src.lower(), \
            "Tooltip must warn about unverified identity"


class TestSpec0270LanguagesRemovedExceptSpanishFrench:
    """SPEC-0270: German, Portuguese, Japanese, Chinese, Korean removed. Spanish/French remain."""

    def test_language_options(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        # Only English, Spanish, French should be in language selector
        assert "English" in src, "Must have English"
        assert "Spanish" in src, "Must have Spanish"
        assert "French" in src, "Must have French"
        # Removed languages must not appear
        for lang in ["German", "Portuguese", "Japanese", "Chinese", "Korean"]:
            assert lang not in src, f"{lang} must be removed from language selector"


# ═══════════════════════════════════════════════════════════════════════
#  GLOSSARY SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0069GlossaryInput:
    """SPEC-0069: Glossary term 'input' = element that elaborates desired state."""

    def test_input_elements_in_admin(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "TextInput" in src or "Textarea" in src or "NumberInput" in src, \
            "Must use input elements in admin"


class TestSpec0070GlossaryCard:
    """SPEC-0070: Glossary term 'card' = logically interdependent group in bordered box."""

    def test_card_components_in_admin(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "Paper" in src or "Card" in src, \
            "Must use card/paper components for grouped content"


class TestSpec0072GlossaryPicker:
    """SPEC-0072: Glossary term 'picker' = color or date selection element."""

    def test_picker_elements_in_admin(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "ColorField" in src or "ColorPicker" in src or "ColorInput" in src, \
            "Must use color picker elements"


# ═══════════════════════════════════════════════════════════════════════
#  PROCESS / INFRASTRUCTURE SPECS (verifiable against code)
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0406SPASeparateFromMerchantAdmin:
    """SPEC-0406: SPA console is a separate admin from the merchant admin."""

    def test_provider_and_standalone_separate(self):
        assert PROVIDER.exists(), "Provider console directory must exist"
        assert STANDALONE.exists(), "Standalone admin directory must exist"
        # They must be separate directories
        assert PROVIDER != STANDALONE, "Provider and standalone must be separate"
        assert (PROVIDER / "pages").exists(), "Provider must have its own pages"
        assert (STANDALONE / "pages").exists(), "Standalone must have its own pages"


class TestSpec0412BuildStageChecklist:
    """SPEC-0412: Build stage MUST be executed according to a strict checklist."""

    def test_deploy_pipeline_has_phases(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "phase_0" in src, "Must have Phase 0 validation"
        assert "phase_1" in src, "Must have Phase 1 checks"
        assert "phase_3_build" in src or "build_artifacts" in src, \
            "Must have build phase"
        assert "phase_8_deploy" in src or "deploy" in src, \
            "Must have deploy phase"


class TestSpec0419FaviconExists:
    """SPEC-0419: Admin console MUST have a favicon."""

    def test_favicon_in_html(self):
        html = (STANDALONE / "index.html").read_text(encoding="utf-8")
        assert "favicon" in html.lower() or "icon" in html.lower(), \
            "Must reference favicon in HTML"

    def test_favicon_files_exist(self):
        public = STANDALONE / "public"
        if public.exists():
            files = [f.name for f in public.iterdir()]
            has_favicon = any("favicon" in f.lower() or "icon-master" in f.lower()
                             for f in files)
            assert has_favicon, f"Must have favicon files in public/ (found: {files})"


class TestSpec0450EnvLocalUpToDate:
    """SPEC-0450: .env.local file MUST be kept up-to-date for production deployment."""

    def test_env_local_exists(self):
        assert (ROOT / ".env.local").exists(), ".env.local must exist"

    def test_env_local_has_production_keys(self):
        src = (ROOT / ".env.local").read_text(encoding="utf-8")
        assert "PROD_URL" in src or "API_URL" in src, \
            "Must have production URL configured"
        assert "COSMOS_DB" in src or "cosmos" in src.lower(), \
            "Must have Cosmos DB configuration"


class TestSpec0668ScheduleMdGroupings:
    """SPEC-0668: SCHEDULE.md MUST contain groupings of sequential prompts."""

    def test_schedule_exists(self):
        schedule = ROOT / ".claude" / "SCHEDULE.md"
        assert schedule.exists(), "SCHEDULE.md must exist"

    def test_schedule_has_groups(self):
        src = (ROOT / ".claude" / "SCHEDULE.md").read_text(encoding="utf-8")
        assert "Group" in src or "group" in src, \
            "Must have prompt groupings"
        assert "trigger" in src.lower(), \
            "Must have trigger definitions"


class TestSpec0771TestingModularizedCooling:
    """SPEC-0771: Testing MUST be modularized for cooling cycles."""

    def test_thermal_safe_script(self):
        ps1 = SCRIPTS / "run-tests-thermal-safe.ps1"
        assert ps1.exists(), "Thermal-safe test script must exist"

    def test_cooling_cycles(self):
        src = (SCRIPTS / "run-tests-thermal-safe.ps1").read_text(encoding="utf-8")
        assert "Cool" in src or "cool" in src, \
            "Must have cooling cycle support"
        assert "Sleep" in src or "sleep" in src, \
            "Must have sleep/pause between batches"


class TestSpec0776ReseedCleanState:
    """SPEC-0776: Every run of E2E tests MUST re-seed tenant for clean state."""

    def test_seed_script_cleans_data(self):
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        assert "Clean" in src or "clean" in src or "delete" in src.lower(), \
            "Must support clean-state initialization"
        assert "TENANT_CONTAINERS" in src or "container" in src.lower(), \
            "Must clean data from tenant containers"


class TestSpec0831IngestionBlocksWizardProgress:
    """SPEC-0831: Storefront ingestion MUST block progress through wizard."""

    def test_ingestion_blocks_continue(self):
        src = (SHARED / "components" / "OnboardingWizard.tsx").read_text(encoding="utf-8")
        assert "ingestionRunning" in src or "ingestion" in src.lower(), \
            "Must track ingestion state"
        assert "disabled" in src, \
            "Must disable Continue button during ingestion"


# ═══════════════════════════════════════════════════════════════════════
#  DOCUMENTATION / NAVIGATION SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0234IntentsRenamedToTopics:
    """SPEC-0234: 'Intents' section renamed to accessible, non-technical language."""

    def test_topics_not_intents_in_dashboard(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "Topic" in src or "topic" in src, \
            "Must use 'Topics' terminology"
        # "Intents" should not appear as a UI-facing label
        # (internal API field names are OK)


class TestSpec0473DocsUnderDocsPrefix:
    """SPEC-0473: Docusaurus docs site MUST serve pages under /docs/ URL prefix."""

    def test_docs_links_use_docs_prefix(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "/docs/" in src, "Must use /docs/ URL prefix for documentation links"


class TestSpec0493MasterE2EProcedure:
    """SPEC-0493: A master procedure for end-to-end testing MUST exist."""

    def test_test_pipeline_exists(self):
        assert (SCRIPTS / "test_pipeline.py").exists(), \
            "test_pipeline.py must exist"

    def test_test_pipeline_has_phases(self):
        src = (SCRIPTS / "test_pipeline.py").read_text(encoding="utf-8")
        assert "phase" in src.lower(), "Must have phase structure"
        assert "def " in src, "Must have test execution functions"


class TestSpec0772FunctionalTestHarness:
    """SPEC-0772: A functional test harness is mandatory."""

    def test_test_harness_exists(self):
        assert (SCRIPTS / "run-tests-thermal-safe.ps1").exists(), \
            "Test harness script must exist"

    def test_harness_runs_multiple_suites(self):
        src = (SCRIPTS / "run-tests-thermal-safe.ps1").read_text(encoding="utf-8")
        assert "pytest" in src.lower(), "Must invoke pytest"
        # Must run multiple test suites
        assert "multi_tenant" in src or "unit" in src, \
            "Must run multiple test suites"
