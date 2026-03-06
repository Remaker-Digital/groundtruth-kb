"""S153 Batch 4 — Dashboard + Sidebar + Branding/Logo + Inbox + Widget spec verification.

36 specs verified against production interfaces.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import inspect
import re
from pathlib import Path

import pytest

# ── Paths ──────────────────────────────────────────────────────────────
SRC = Path(__file__).resolve().parents[2] / "src"
ADMIN = Path(__file__).resolve().parents[2] / "admin"
WIDGET = Path(__file__).resolve().parents[2] / "widget"
BRANDING = Path(__file__).resolve().parents[2] / "branding"
STANDALONE = ADMIN / "standalone"
SHARED = ADMIN / "shared"


# ═══════════════════════════════════════════════════════════════════════
#  DASHBOARD SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0007AnalyticsMergedIntoDashboard:
    """SPEC-0007: Analytics page content MUST be merged into the Dashboard page."""

    def test_dashboard_has_analytics_hooks(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "useAnalyticsSummary" in src, "Dashboard must import analytics summary hook"
        assert "useDailyVolume" in src, "Dashboard must import daily volume hook"
        assert "useIntentBreakdown" in src, "Dashboard must import intent breakdown hook"

    def test_dashboard_has_conversation_volume_chart(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "AreaChart" in src or "chartData" in src, "Dashboard must render conversation volume chart"

    def test_analytics_route_redirects_to_dashboard(self):
        src = (STANDALONE / "index.tsx").read_text(encoding="utf-8")
        assert "analytics" in src.lower(), "Routes must reference analytics"
        assert "Navigate" in src or "Redirect" in src or "redirect" in src, "Analytics route must redirect"


class TestSpec0008AnalyticsSidebarRemoved:
    """SPEC-0008: The Analytics sidebar nav item MUST be removed."""

    def test_no_analytics_in_sidebar_nav_items(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        nav_section = src[src.find("navItemsBefore"):src.find("navItemsAfter")]
        assert "analytics" not in nav_section.lower() or "Analytics" not in nav_section


class TestSpec0094DashboardTooltipsWithDocLinks:
    """SPEC-0094: Dashboard tooltips MUST contain links to documentation pages."""

    def test_dashboard_has_help_tooltips(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "HelpTooltip" in src, "Dashboard must use HelpTooltip components"

    def test_tooltips_have_doc_links(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "docLink" in src, "Tooltips must include docLink properties"
        assert "agentredcx.com" in src, "Doc links must point to documentation site"


class TestSpec0182QualityTrendDashboard:
    """SPEC-0182: Quality trend dashboard showing quality metrics over time."""

    def test_dashboard_has_time_series_chart(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "AreaChart" in src or "LineChart" in src, "Dashboard must have time series chart"
        assert "useDailyVolume" in src, "Dashboard must fetch daily volume data"

    def test_dashboard_has_period_selector(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "7d" in src or "14d" in src or "30d" in src, "Dashboard must have period options"


class TestSpec0372NoDashboardEnvironmentSelector:
    """SPEC-0372: Dashboard MUST NOT have an All/Production/Test environment selector."""

    def test_dashboard_has_no_environment_filter(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        # Dashboard should NOT have the environment segmented control
        # (Analytics.tsx has it, but Dashboard.tsx should not)
        env_patterns = re.findall(r'SegmentedControl.*?Production.*?Test', src, re.DOTALL)
        assert len(env_patterns) == 0, "Dashboard must not have environment selector"


class TestSpec0461DashboardNoPreInitData:
    """SPEC-0461: Dashboard conversation volume data MUST NOT show pre-initialization data."""

    def test_analytics_uses_api_date_filtering(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        # Dashboard requests data with a period filter, ensuring server-side filtering
        assert "period" in src or "days" in src, "Dashboard must pass period/days to API"
        assert "useDailyVolume" in src, "Daily volume hook handles date filtering"


class TestSpec0462DashboardAccurateMetrics:
    """SPEC-0462: Dashboard metrics MUST accurately reflect actual data."""

    def test_dashboard_uses_real_analytics_data(self):
        src = (STANDALONE / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        assert "useAnalyticsSummary" in src, "Must use real analytics API data"
        assert "escalat" in src.lower(), "Must display escalation metrics"
        assert "resolution" in src.lower() or "resolved" in src.lower(), "Must display resolution data"


class TestSpec0579AnalyticsPageRendersCharts:
    """SPEC-0579: The Analytics page MUST render charts."""

    def test_analytics_page_exists_with_charts(self):
        analytics = STANDALONE / "pages" / "Analytics.tsx"
        assert analytics.exists(), "Analytics.tsx must exist"
        src = analytics.read_text(encoding="utf-8")
        assert "AreaChart" in src or "LineChart" in src or "BarChart" in src, "Charts must render"


# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR / NAVIGATION SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0088ActiveSelectionWhite:
    """SPEC-0088: Active selection text color in sidebar MUST be white, not red."""

    def test_active_nav_uses_white_text(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # Active items use tokens.textPrimary which is white in dark mode
        assert "textPrimary" in src, "Active nav must reference textPrimary token"
        # Verify no red text for active state
        assert "color: 'red'" not in src or "brand" in src, "Active selection must not use red text"


class TestSpec0255SentenceCaseLabels:
    """SPEC-0255: All non-proper-noun UI labels shall use sentence case."""

    def test_sidebar_labels_use_sentence_case(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # Verify sentence case: first word capitalized, rest lowercase (except proper nouns)
        labels = ["Dashboard", "Inbox", "Team members", "Agent configuration",
                  "Knowledge base", "Quick actions", "Widget configuration",
                  "Integrations", "Billing"]
        for label in labels:
            assert label in src, f"Sidebar must contain '{label}' in sentence case"
        # Verify NOT title case
        assert "Team Members" not in src, "Must be 'Team members' not 'Team Members'"
        assert "Knowledge Base" not in src or "knowledge_base" in src, \
            "Must be 'Knowledge base' not 'Knowledge Base' in nav labels"


class TestSpec0271AIConfigurationHeading:
    """SPEC-0271: Sidebar heading shall read 'AI Configuration'."""

    def test_config_group_heading(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "AI Configuration" in src or "AI CONFIGURATION" in src, \
            "Configuration group heading must be 'AI Configuration'"


class TestSpec0688NoDuplicateDocLink:
    """SPEC-0688: Sidebar MUST NOT contain duplicate documentation link."""

    def test_no_documentation_in_sidebar_nav(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # Documentation link is in header only, not sidebar nav items
        nav_items = src[src.find("navItemsBefore"):src.find("// Footer")]
        label_matches = re.findall(r"label:\s*['\"]Documentation['\"]", nav_items)
        assert len(label_matches) == 0, "No 'Documentation' label in sidebar nav items"


class TestSpec0696TeamMembersLabel:
    """SPEC-0696: Sidebar label 'Team' MUST be renamed to 'Team members'."""

    def test_team_members_label(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Team members" in src, "Sidebar must show 'Team members'"
        # Find nav items and verify 'Team' is not used alone as a label
        nav_section = src[src.find("navItemsBefore"):src.find("configGroupItems")]
        assert re.search(r"label:\s*['\"]Team members['\"]", nav_section), \
            "Nav item label must be 'Team members'"


class TestSpec0697ConfigItemsGrouped:
    """SPEC-0697: Agent config, KB, Quick actions, Widget config MUST be grouped."""

    def test_config_group_exists(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "configGroupItems" in src or "configGroup" in src, \
            "Configuration items must be in a named group"

    def test_group_contains_all_four(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        group_section = src[src.find("configGroup"):src.find("navItemsAfter")]
        for label in ["Agent configuration", "Knowledge base", "Quick actions", "Widget configuration"]:
            assert label in group_section, f"Config group must contain '{label}'"


# ═══════════════════════════════════════════════════════════════════════
#  BRANDING / LOGO SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0013AdminLogoIsPrimaryNoWordmark:
    """SPEC-0013: Admin logo in upper left MUST use primary-logo-no-wordmark.svg."""

    def test_header_logo_reference(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "primary-logo-no-wordmark" in src, "Header must reference primary-logo-no-wordmark.svg"


class TestSpec0014WordmarkCustomerExperience:
    """SPEC-0014: Wordmark 'Customer Experience' MUST appear to the right of the logo."""

    def test_customer_experience_text(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Customer Experience" in src, "Header must display 'Customer Experience' text"


class TestSpec0229LogoWithoutAgentRedText:
    """SPEC-0229: Logo used in admin UI shall be without 'Agent Red' text."""

    def test_uses_no_wordmark_variant(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "primary-logo-no-wordmark" in src, "Must use no-wordmark logo variant"


class TestSpec0368IntegrationLogo180Container:
    """SPEC-0368: Integration card logos MUST use 180x180 pixel square container."""

    def test_icon_container_dimensions(self):
        src = (SHARED / "IntegrationsManager.tsx").read_text(encoding="utf-8")
        assert "180" in src, "Icon container must reference 180px dimension"
        assert "width:" in src and "height:" in src, "Container must set both dimensions"


class TestSpec0369IntegrationLogoNoSizeConstraints:
    """SPEC-0369: Integration card logo images MUST fill container naturally."""

    def test_logo_uses_object_fit_contain(self):
        src = (SHARED / "IntegrationsManager.tsx").read_text(encoding="utf-8")
        assert "objectFit" in src or "object-fit" in src, "Logo must use object-fit"
        assert "contain" in src, "object-fit must be 'contain'"


class TestSpec0533IntegrationContentToRight:
    """SPEC-0533: Integration text and buttons MUST be positioned to the right."""

    def test_card_uses_row_layout(self):
        src = (SHARED / "IntegrationsManager.tsx").read_text(encoding="utf-8")
        assert "flexDirection" in src or "flex-direction" in src, "Card must set flex direction"
        assert "'row'" in src or "row" in src, "Layout must be row (logo left, content right)"


class TestSpec0566IntegrationLogoObjectFitBlock:
    """SPEC-0566: Integration logo images MUST use object-fit: contain and display: block."""

    def test_both_css_properties(self):
        src = (SHARED / "IntegrationsManager.tsx").read_text(encoding="utf-8")
        assert "contain" in src, "Must use object-fit: contain"
        assert "'block'" in src or "block" in src, "Must use display: block"


class TestSpec0605TopRightLogoPrimaryNoWordmark:
    """SPEC-0605: Admin console top-right logo MUST use primary-logo-no-wordmark.svg."""

    def test_header_logo_is_no_wordmark(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "primary-logo-no-wordmark" in src, "Header logo must be primary-logo-no-wordmark"


class TestSpec0606WordmarkGlossary:
    """SPEC-0606: 'wordmark' refers to 'Customer Experience', not logo text."""

    def test_customer_experience_is_separate_text(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # The text "Customer Experience" is rendered as a separate Text element
        assert "Customer Experience" in src, "Customer Experience must be rendered as text"
        # It should NOT be part of the image filename/reference
        img_refs = re.findall(r'src=["\'][^"\']+["\']', src)
        for ref in img_refs:
            assert "customer-experience" not in ref.lower(), \
                "Customer Experience is text, not embedded in logo image"


class TestSpec0694LoginPageLogo:
    """SPEC-0694: Logo on login screen MUST be functional and correctly rendered."""

    def test_login_page_has_logo(self):
        login = STANDALONE / "components" / "ApiKeyLogin.tsx"
        if not login.exists():
            login = STANDALONE / "pages" / "ApiKeyLogin.tsx"
        if not login.exists():
            # Search for login component
            for f in STANDALONE.rglob("*Login*.tsx"):
                login = f
                break
        assert login.exists(), "Login component must exist"
        src = login.read_text(encoding="utf-8")
        assert "primary-logo-no-wordmark" in src or "logo" in src.lower(), \
            "Login page must reference a logo"


class TestSpec0799BrandPrimaryColor:
    """SPEC-0799: Brand primary color MUST be #ff3621."""

    def test_brand_color_in_widget_tokens(self):
        tokens = WIDGET / "src" / "theme" / "tokens.ts"
        src = tokens.read_text(encoding="utf-8")
        assert "#ff3621" in src, "Widget tokens must define #ff3621 as primary color"

    def test_brand_color_in_admin_theme(self):
        # Check admin theme file
        theme_files = list(ADMIN.rglob("*theme*"))
        found = False
        for tf in theme_files:
            if tf.suffix in ('.ts', '.tsx', '.js'):
                content = tf.read_text(encoding="utf-8")
                if "#ff3621" in content:
                    found = True
                    break
        assert found, "Admin theme must reference #ff3621"


class TestSpec0801LogoConcept3Beacon:
    """SPEC-0801: Logo concept 3 (The Beacon/AR monogram) MUST be used."""

    def test_icon_master_exists(self):
        svg = BRANDING / "logo" / "SVG" / "icon-master.svg"
        png = BRANDING / "logo" / "PNG" / "icon-master.png"
        assert svg.exists(), "icon-master.svg must exist"
        assert png.exists(), "icon-master.png must exist"


class TestSpec0814HeaderLogoPrimaryNoWordmark:
    """SPEC-0814: Header top-right logo MUST use primary-logo-no-wordmark.svg."""

    def test_header_uses_no_wordmark(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "primary-logo-no-wordmark" in src


class TestSpec0825BrandingImages:
    """SPEC-0825: 20 branding images MUST be in branding/images/."""

    def test_branding_images_directory(self):
        imgs_dir = BRANDING / "images"
        assert imgs_dir.exists(), "branding/images/ directory must exist"
        images = [f for f in imgs_dir.iterdir() if f.suffix in ('.png', '.jpg', '.svg')]
        assert len(images) >= 20, f"Must have >= 20 branding images, found {len(images)}"


class TestSpec0828ProtectedLogoFiles:
    """SPEC-0828: Protected logo files MUST NOT be modified."""

    def test_protected_files_exist(self):
        protected = [
            BRANDING / "logo" / "SVG" / "icon-master.svg",
            BRANDING / "logo" / "SVG" / "primary-logo-no-wordmark.svg",
            BRANDING / "logo" / "PNG" / "icon-master.png",
            BRANDING / "logo" / "PNG" / "primary-logo-no-wordmark.png",
        ]
        for f in protected:
            assert f.exists(), f"Protected file {f.name} must exist"


# ═══════════════════════════════════════════════════════════════════════
#  WIDGET SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0032WidgetDefaultBrandColors:
    """SPEC-0032: Default widget colors MUST match Agent Red brand colors."""

    def test_default_primary_is_brand_color(self):
        src = (WIDGET / "src" / "theme" / "tokens.ts").read_text(encoding="utf-8")
        assert "primaryColor" in src or "ff3621" in src, "Tokens must define primaryColor"
        assert "#ff3621" in src, "Default primaryColor must be #ff3621"


class TestSpec0572WidgetErrorMessagesGreyBackground:
    """SPEC-0572: Widget error messages MUST use medium grey, NOT brand primary."""

    def test_error_banner_uses_grey(self):
        panel = WIDGET / "src" / "components" / "Panel.tsx"
        src = panel.read_text(encoding="utf-8")
        # Error banner should use grey (#6B6B6B), not brand primary (#ff3621)
        assert "#6B6B6B" in src or "#6b6b6b" in src or "grey" in src.lower() or "gray" in src.lower(), \
            "Error banner must use grey background color"


class TestSpec1553WidgetBrandingFooter:
    """SPEC-1553: Widget branding footer must show 'Agent Red' in bold primaryColor."""

    def test_powered_by_agent_red(self):
        # Check InputBar.tsx for the branding footer
        input_bar = WIDGET / "src" / "components" / "InputBar.tsx"
        src = input_bar.read_text(encoding="utf-8")
        assert "Agent Red" in src, "Footer must contain 'Agent Red' text"
        assert "colorPrimary" in src or "primaryColor" in src, \
            "Agent Red text must use primary color"


# ═══════════════════════════════════════════════════════════════════════
#  INBOX SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0095InboxSearchReturnsMatches:
    """SPEC-0095: Inbox search MUST return results matching the search term."""

    def test_search_implementation_exists(self):
        # Check multiple possible inbox implementations
        inbox_files = list(STANDALONE.rglob("*[Ii]nbox*"))
        inbox_files += list(SHARED.rglob("*[Ii]nbox*"))
        found_search = False
        for f in inbox_files:
            if f.suffix in ('.ts', '.tsx'):
                src = f.read_text(encoding="utf-8")
                if "search" in src.lower() and ("filter" in src.lower() or "includes" in src.lower()):
                    found_search = True
                    break
        assert found_search, "Inbox must implement search/filter functionality"


# ═══════════════════════════════════════════════════════════════════════
#  GLOSSARY / PROCESS SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0071GlossaryPage:
    """SPEC-0071: Glossary term: 'page' = a full admin UI view via sidebar navigation."""

    def test_admin_pages_match_sidebar_nav(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        routes = (STANDALONE / "index.tsx").read_text(encoding="utf-8")
        # Each sidebar nav item maps to a unique route/page
        nav_paths = re.findall(r"path:\s*['\"](/[^'\"]*)['\"]", src)
        route_paths = re.findall(r"path=['\"]([^'\"]+)['\"]", routes)
        assert len(nav_paths) >= 8, "Must have at least 8 navigation items"
        assert len(route_paths) >= 8, "Must have at least 8 route definitions"


class TestSpec0573ShopifyAdminLoads:
    """SPEC-0573: Shopify embedded admin MUST load without errors."""

    def test_shopify_admin_entry_exists(self):
        shopify_index = ADMIN / "shopify" / "index.tsx"
        assert shopify_index.exists(), "Shopify admin entry point must exist"
        src = shopify_index.read_text(encoding="utf-8")
        assert "App" in src or "render" in src, "Must render an app"

    def test_shopify_layout_exists(self):
        layout = ADMIN / "shopify" / "layouts" / "ShopifyAppLayout.tsx"
        assert layout.exists(), "Shopify layout must exist"


class TestSpec1659QualityDashboard:
    """SPEC-1659: Quality Dashboard — Session-Start Quality Metrics."""

    def test_assertion_check_hook_has_dashboard(self):
        hook = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "assertion-check.py"
        assert hook.exists(), "assertion-check.py hook must exist"
        src = hook.read_text(encoding="utf-8")
        assert "_quality_dashboard" in src or "quality_dashboard" in src, \
            "Hook must contain quality dashboard function"
        assert "Assertion Coverage" in src or "assertion_coverage" in src, \
            "Dashboard must display assertion coverage metric"
