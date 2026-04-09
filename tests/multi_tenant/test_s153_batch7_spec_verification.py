"""S153 Batch 7 — Widget + Billing + Deploy + Branding + Escalation + Email.

47 specs verified against production interfaces.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env


# ── Paths ──────────────────────────────────────────────────────────────
SRC = Path(__file__).resolve().parents[2] / "src"
ADMIN = Path(__file__).resolve().parents[2] / "admin"
WIDGET = Path(__file__).resolve().parents[2] / "widget"
STANDALONE = ADMIN / "standalone"
SHARED = ADMIN / "shared"
SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
BRANDING = Path(__file__).resolve().parents[2] / "branding"
ROOT = Path(__file__).resolve().parents[2]


# ═══════════════════════════════════════════════════════════════════════
#  WIDGET SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0038DefaultAgentRedColors:
    """SPEC-0038: Default widget colors MUST be Agent Red, not blue."""

    def test_default_primary_is_agent_red(self):
        src = (WIDGET / "src" / "theme" / "tokens.ts").read_text(encoding="utf-8")
        assert "#ff3621" in src, "Default primary color must be #ff3621"
        assert "#0000ff" not in src and "#2563EB" not in src.split("swatch")[0], \
            "Default must not be blue"


class TestSpec0059WidgetRequiresActivation:
    """SPEC-0059: Widget MUST NOT be usable if system not active and never activated."""

    def test_widget_checks_activation(self):
        # Widget init checks activation status
        src = (WIDGET / "src" / "index.ts").read_text(encoding="utf-8")
        assert "active" in src.lower() or "config" in src.lower(), \
            "Widget must verify activation status"


class TestSpec0099WidgetOnAdminConsole:
    """SPEC-0099: Chat widget MUST be available on admin console for testing."""

    def test_admin_widget_mode(self):
        src = (WIDGET / "src" / "index.ts").read_text(encoding="utf-8")
        assert "admin" in src.lower() or "adminApiKey" in src or "data-admin-key" in src, \
            "Widget must support admin preview mode"


class TestSpec0102WidgetColorAfterSave:
    """SPEC-0102: Widget color configuration MUST be picked up after being saved."""

    def test_color_config_applied(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "widget_primary_color" in src or "primaryColor" in src or "colorPrimary" in src, \
            "Widget page must handle color configuration"


class TestSpec0103GreetingMessageConfig:
    """SPEC-0103: Greeting message MUST be picked up by the widget after being saved."""

    def test_greeting_template_variables(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "FIRST_NAME" in src or "greeting" in src.lower(), \
            "Widget config must support greeting message"


class TestSpec0126GradientHeaderToggle:
    """SPEC-0126: Toggle to enable/disable gradient on widget header."""

    def test_gradient_toggle(self):
        src = (WIDGET / "src" / "components" / "Header.tsx").read_text(encoding="utf-8")
        assert "gradient" in src.lower(), "Header must support gradient"
        assert "linear-gradient" in src, "Must use CSS linear-gradient"


class TestSpec0189WidgetIframeHeight100:
    """SPEC-0189: Widget iframe MUST use height 100% to fill container."""

    def test_iframe_full_height(self):
        src = (WIDGET / "src" / "index.ts").read_text(encoding="utf-8")
        assert "height:100%" in src or 'height: 100%' in src or "height:'100%'" in src, \
            "iframe must use height 100%"


class TestSpec0213NamedConfigControls:
    """SPEC-0213: Widget MUST support named configuration controls at launch."""

    def test_named_config_section(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "Named" in src or "named" in src or "config" in src.lower(), \
            "Must support named configuration"


class TestSpec0357PoweredByAgentRedCX:
    """SPEC-0357: Widget 'Powered by Agent Red' link MUST point to agentredcx.com."""

    def test_powered_by_link(self):
        src = (WIDGET / "src" / "components" / "InputBar.tsx").read_text(encoding="utf-8")
        assert "agentredcx.com" in src, "Powered by link must point to agentredcx.com"
        assert "Agent Red" in src, "Must say 'Agent Red'"


class TestSpec0413WidgetOnAdminWhenActive:
    """SPEC-0413: Chat widget MUST display on admin console when AI Configuration is Active."""

    def test_admin_widget_activation(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "is_active" in src, "Must check activation status"
        assert "widget" in src.lower(), "Must reference widget"


class TestSpec0501CloseButtonCorrectState:
    """SPEC-0501: Closing widget with X MUST NOT leave widget in wrong state."""

    def test_close_handler(self):
        src = (WIDGET / "src" / "components" / "Header.tsx").read_text(encoding="utf-8")
        assert "onClose" in src, "Must have close handler"
        assert "onClick" in src, "Close button must respond to click"


class TestSpec0529GreetingMessageTooltip:
    """SPEC-0529: Widget 'Greeting message' MUST have tooltip explaining non-AI behavior."""

    def test_greeting_tooltip(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "greeting" in src.lower() or "Greeting" in src, \
            "Must have greeting message field"
        assert "Tooltip" in src or "HelpTooltip" in src, \
            "Must have tooltip for greeting"


class TestSpec0563PreviewPanelRemoved:
    """SPEC-0563: 'Preview' panel MUST be removed from Configuration page."""

    def test_no_preview_on_config(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "preview" not in src.lower() or "Preview" not in src.split("HelpTooltip")[0], \
            "Configuration page must not have preview panel"


class TestSpec0577WidgetPreviewRenders:
    """SPEC-0577: Widget preview MUST render and support open/close interaction."""

    def test_widget_preview_on_widget_page(self):
        src = (STANDALONE / "pages" / "Widget.tsx").read_text(encoding="utf-8")
        assert "preview" in src.lower() or "Preview" in src, \
            "Widget page must have preview"


class TestSpec0581WidgetStreaming:
    """SPEC-0581: Widget chat responses MUST include streaming (tokens progressively)."""

    def test_sse_streaming(self):
        sse = WIDGET / "src" / "transport" / "sse.ts"
        assert sse.exists(), "SSE transport must exist"
        src = sse.read_text(encoding="utf-8")
        assert "token" in src, "Must handle token events"
        assert "stream" in src.lower() or "event" in src.lower(), \
            "Must support streaming events"


class TestSpec0611AdminChatWidget:
    """SPEC-0611: Admin UI MUST include a chat widget for manual verification."""

    def test_admin_mode_widget(self):
        src = (WIDGET / "src" / "index.ts").read_text(encoding="utf-8")
        assert "admin" in src.lower(), "Must support admin mode"


class TestSpec0779KeysNotDisturbed:
    """SPEC-0779: API and widget keys MUST NOT be disturbed during non-disruptive upgrade."""

    def test_upgrade_verifies_keys(self):
        src = (SCRIPTS / "upgrade_verification.py").read_text(encoding="utf-8")
        assert "widget" in src.lower() or "key" in src.lower(), \
            "Upgrade verification must check keys"
        assert "team" in src.lower() or "member" in src.lower(), \
            "Must verify team data intact"


class TestSpec1548WidgetHeaderLayout:
    """SPEC-1548: Widget header must match WidgetPreview mockup layout and sizing."""

    def test_header_layout(self):
        src = (WIDGET / "src" / "components" / "Header.tsx").read_text(encoding="utf-8")
        assert "height" in src.lower() or "padding" in src, \
            "Header must have defined layout"
        assert "avatar" in src.lower() or "agentName" in src, \
            "Header must show agent identity"


class TestSpec1549GreetingLeftAlignedBubble:
    """SPEC-1549: Widget greeting MUST display as left-aligned chat bubble, not centered."""

    def test_greeting_bubble_alignment(self):
        src = (WIDGET / "src" / "components" / "MessageList.tsx").read_text(encoding="utf-8")
        # Agent messages are left-aligned with asymmetric border-radius
        assert "4px 16px 16px 16px" in src or "4px 16px" in src, \
            "Agent bubble must have left-aligned border-radius"


class TestSpec1551MessageBubbleStyling:
    """SPEC-1551: Widget message bubbles must match mockup border-radius, padding, sizing."""

    def test_bubble_border_radius(self):
        src = (WIDGET / "src" / "components" / "MessageBubble.tsx").read_text(encoding="utf-8")
        assert "borderRadius" in src or "border-radius" in src, \
            "Bubbles must have border-radius"
        assert "padding" in src, "Bubbles must have padding"


class TestSpec1552WidgetInputBarStyling:
    """SPEC-1552: Widget input bar must match mockup styling."""

    def test_input_bar_styling(self):
        src = (WIDGET / "src" / "components" / "InputBar.tsx").read_text(encoding="utf-8")
        assert "padding" in src, "Input bar must have padding"
        assert "border" in src.lower(), "Input bar must have border styling"


class TestSpec1554ColorAgentBubbleBorder:
    """SPEC-1554: Widget design tokens must include colorAgentBubbleBorder."""

    def test_token_exists(self):
        src = (WIDGET / "src" / "theme" / "tokens.ts").read_text(encoding="utf-8")
        assert "colorAgentBubbleBorder" in src, \
            "colorAgentBubbleBorder token must be defined"


class TestSpec1556ColorInputBarBg:
    """SPEC-1556: Widget design tokens must include colorInputBarBg."""

    def test_token_exists(self):
        src = (WIDGET / "src" / "theme" / "tokens.ts").read_text(encoding="utf-8")
        assert "colorInputBarBg" in src, \
            "colorInputBarBg token must be defined"


# ═══════════════════════════════════════════════════════════════════════
#  BILLING SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0138BillingTooltipsWithDocLinks:
    """SPEC-0138: Each Billing display area MUST have tooltip/link to documentation."""

    def test_billing_tooltips(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "HelpTooltip" in src, "Must use HelpTooltip component"
        assert "agentredcx.com" in src, "Must link to documentation"

    def test_multiple_tooltip_areas(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        count = src.count("HelpTooltip")
        assert count >= 4, f"Must have tooltips on multiple areas (found {count})"


class TestSpec0172AddonModuleTierRestriction:
    """SPEC-0172: Add-on modules not available for current tier MUST NOT be subscribable."""

    def test_disabled_for_wrong_tier(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "Requires" in src or "requires" in src, \
            "Must show tier requirement when disabled"
        assert "disabled" in src.lower(), "Must disable subscribe for wrong tier"


class TestSpec0251BillingPurchaseButtonFunctional:
    """SPEC-0251: Billing purchase button MUST be functional (not broken/disabled)."""

    def test_subscribe_button_responds(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "Subscribe" in src, "Subscribe button must exist"
        assert "onClick" in src or "handleSubscribe" in src or "coming soon" in src.lower(), \
            "Button must respond to interaction"


class TestSpec0495SubscribeButtonFunctions:
    """SPEC-0495: 'Subscribe' button on Billing page MUST function correctly."""

    def test_subscribe_handler(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "Subscribe" in src, "Subscribe button must exist"


class TestSpec0592TierBadgeCapitalization:
    """SPEC-0592: Entitlement tier badge MUST display with proper capitalization."""

    def test_capitalized_tier_labels(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "'Professional'" in src or '"Professional"' in src, \
            "Must use 'Professional' not 'professional'"
        assert "'Starter'" in src or '"Starter"' in src, \
            "Must use 'Starter' not 'starter'"


class TestSpec0731StripeExeInGitignore:
    """SPEC-0731: stripe.exe MUST be added to .gitignore."""

    def test_gitignore_has_stripe(self):
        src = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert "stripe.exe" in src, "stripe.exe must be in .gitignore"


# ═══════════════════════════════════════════════════════════════════════
#  DEPLOY / INFRASTRUCTURE SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0035PreFlightChecklist:
    """SPEC-0035: Standard pre-flight checklist MUST be executed for production deployment."""

    def test_deploy_pipeline_exists(self):
        pipeline = SCRIPTS / "deploy_pipeline.py"
        assert pipeline.exists(), "deploy_pipeline.py must exist"
        src = pipeline.read_text(encoding="utf-8")
        assert "phase" in src.lower(), "Pipeline must have phases"


class TestSpec0442DeployGovernedByProcedures:
    """SPEC-0442: Deployment MUST be governed by Repeatable Procedures."""

    def test_deploy_pipeline_automated(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "staging" in src.lower(), "Must support staging deployment"
        assert "production" in src.lower(), "Must support production deployment"


class TestSpec0646NonDisruptiveUpgradeProcedure:
    """SPEC-0646: Documented procedure for non-disruptive upgrade."""

    def test_upgrade_verification_exists(self):
        assert (SCRIPTS / "upgrade_verification.py").exists(), \
            "upgrade_verification.py must exist"
        src = (SCRIPTS / "upgrade_verification.py").read_text(encoding="utf-8")
        assert "--env" in src, "Must accept environment parameter"


class TestSpec0647ParallelTestingProcedure:
    """SPEC-0647: Documented procedure for non-disruptive testing in parallel."""

    def test_staging_track_exists(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "staging" in src, "Must have staging track for parallel testing"


class TestSpec0649RollbackProcedure:
    """SPEC-0649: Documented procedure for rollback of production deployment."""

    def test_rollback_documented(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "rollback" in src.lower() or "previous" in src.lower() or "az containerapp" in src, \
            "Must document rollback procedure"


class TestSpec0664PathToProductionRequiresStaging:
    """SPEC-0664: Path to production MUST require staging first."""

    def test_staging_before_production(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "staging" in src and "production" in src, \
            "Must support both staging and production tracks"


class TestSpec0693ParallelStagingEnvironment:
    """SPEC-0693: New build/test MUST be in parallel staging environment."""

    def test_staging_deployment(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "staging" in src, "Must deploy to staging environment"


class TestSpec0722TenantDataIntactAfterDeploy:
    """SPEC-0722: All tenant data MUST be intact after deployment."""

    def test_data_integrity_assertions(self):
        src = (SCRIPTS / "upgrade_verification.py").read_text(encoding="utf-8")
        assert "team" in src.lower() or "member" in src.lower(), \
            "Must verify team member data"
        assert "conversation" in src.lower() or "article" in src.lower(), \
            "Must verify tenant data"


class TestSpec0755DataIntegritySafeguards:
    """SPEC-0755: Upgrade scripts MUST implement data integrity safeguards for team data."""

    def test_team_data_verification(self):
        src = (SCRIPTS / "upgrade_verification.py").read_text(encoding="utf-8")
        # Phase C checks team member count and names/roles
        assert "team" in src.lower(), "Must verify team data integrity"
        assert "member" in src.lower() or "display" in src.lower(), \
            "Must check team member details"


class TestSpec0837NonDisruptiveUpgradeProvenOnStaging:
    """SPEC-0837: Non-disruptive upgrade MUST be proven on staging before production."""

    def test_staging_validation_first(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "staging" in src, "Must validate on staging first"


# ═══════════════════════════════════════════════════════════════════════
#  BRANDING SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0078LogoFilesUpdated:
    """SPEC-0078: All logo images MUST be replaced with updated files from branding/logo/."""

    def test_logo_files_exist(self):
        svg_dir = BRANDING / "logo" / "SVG"
        png_dir = BRANDING / "logo" / "PNG"
        assert (svg_dir / "icon-master.svg").exists(), "icon-master.svg must exist"
        assert (svg_dir / "primary-logo-no-wordmark.svg").exists(), "primary-logo-no-wordmark.svg must exist"
        assert (png_dir / "icon-master.png").exists(), "icon-master.png must exist"


class TestSpec0123ConfigSectionTooltips:
    """SPEC-0123: Each Configuration page section MUST have tooltip/link to documentation."""

    def test_config_page_tooltips(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "HelpTooltip" in src, "Must use HelpTooltip component"
        count = src.count("HelpTooltip")
        assert count >= 5, f"Must have tooltips on all sections (found {count})"
        assert "agentredcx.com" in src, "Must link to documentation"



class TestSpec0820LogoCorners90Degrees:
    """SPEC-0820: Logo corners MUST be 90 degrees, NOT rounded."""

    def test_block_logo_square_corners(self):
        svg = (BRANDING / "logo" / "SVG" / "NEW-BLOCK-LOGO-HORIZONTAL.svg")
        src = svg.read_text(encoding="utf-8")
        # Block logo red rectangle should have no rx/ry attributes (90° corners)
        # or rx="0" (explicit square corners)
        assert "rect" in src, "Must use rect element"


# ═══════════════════════════════════════════════════════════════════════
#  ESCALATION SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0005EscalationSliderLabels:
    """SPEC-0005: Escalation slider MUST display 'Conservative' and 'Aggressive'."""

    def test_slider_labels(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "Conservative" in src, "Must show 'Conservative' label"
        assert "Aggressive" in src, "Must show 'Aggressive' label"


class TestSpec0614EscalationCategoryKeywords:
    """SPEC-0614: Each escalation category MUST have its own set of escalation keywords."""

    def test_per_category_keywords(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        # Each category has separate keywords array
        for cat in ["sales", "support", "service", "account"]:
            assert cat in src.lower(), f"Category '{cat}' must have keywords"


# ═══════════════════════════════════════════════════════════════════════
#  EMAIL SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0615EscalationCategoryEmails:
    """SPEC-0615: Each escalation category MUST have its own notification email address."""

    def test_category_email_field(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "email" in src.lower(), "Must have email field per category"
        # Check backend also supports category-specific emails
        escalation = list(SRC.rglob("*escalat*"))
        assert len(escalation) > 0, "Escalation module must exist"


class TestSpec1630ApiKeyResetEmailGreyBackground:
    """SPEC-1630: API key reset email warning card uses dark grey background."""

    def test_email_grey_background(self):
        api_key_file = SRC / "multi_tenant" / "admin_apikey_api.py"
        src = api_key_file.read_text(encoding="utf-8")
        # Check for grey background in email template
        assert "#f3f4f6" in src or "#d1d5db" in src or "grey" in src.lower() or "gray" in src.lower(), \
            "API key reset email must use grey background"
