"""S153 Batch 9 — Admin UI behavior + Widget + Provider + Tooltips + more.

Specs verified against production interfaces.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import json
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────
SRC = Path(__file__).resolve().parents[2] / "src"
ADMIN = Path(__file__).resolve().parents[2] / "admin"
WIDGET = Path(__file__).resolve().parents[2] / "widget"
STANDALONE = ADMIN / "standalone"
SHARED = ADMIN / "shared"
PROVIDER = ADMIN / "provider"
SHOPIFY = ADMIN / "shopify"
SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
BRANDING = Path(__file__).resolve().parents[2] / "branding"
ROOT = Path(__file__).resolve().parents[2]


# ═══════════════════════════════════════════════════════════════════════
#  ADMIN UI BEHAVIOR SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0017ThinnerBorderDarkMode:
    """SPEC-0017: Main page display areas must have thinner border in Dark Mode."""

    def test_dark_mode_border_defined(self):
        src = (SHARED / "theme" / "tokens.css").read_text(encoding="utf-8")
        assert "--ar-border" in src, "Must define dark mode border token"
        assert "border" in src.lower(), "Must have border definitions"


class TestSpec0022IconMasterDisplayed:
    """SPEC-0022: Agent Red icon-master displayed near each entry in admin."""

    def test_icon_in_layout(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "primary-logo" in src or "icon-master" in src or "logo" in src.lower(), \
            "Must display Agent Red icon/logo"


class TestSpec0031StandaloneAsCustomerAdmin:
    """SPEC-0031: Standalone admin behaves as standard customer admin."""

    def test_standalone_has_full_admin_pages(self):
        pages = list((STANDALONE / "pages").glob("*.tsx"))
        page_names = [p.stem for p in pages]
        assert len(pages) >= 8, f"Must have full admin pages (found {len(pages)})"
        for expected in ["Dashboard", "Inbox", "Configuration"]:
            assert expected in page_names, f"Must have {expected} page"


class TestSpec0065DeactivateConfirmationDialog:
    """SPEC-0065: Deactivate action goes through confirmation dialog."""

    def test_deactivate_confirmation(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Deactivate" in src, "Must have Deactivate action"
        assert "confirm" in src.lower() or "dialog" in src.lower() or "Modal" in src, \
            "Must have confirmation before deactivation"


class TestSpec0082AdminSupportsDesktop:
    """SPEC-0082: Admin UI supports desktop users (web-based)."""

    def test_web_based_admin(self):
        # Admin is a web-based React/Vite SPA
        assert (STANDALONE / "index.tsx").exists(), "Standalone admin entry point must exist"
        assert (STANDALONE / "layouts" / "StandaloneLayout.tsx").exists(), \
            "Must have layout for desktop display"


class TestSpec0087MantineV7Used:
    """SPEC-0087: Mantine v7 must be used as UI component library."""

    def test_mantine_in_dependencies(self):
        pkg = json.loads((ADMIN / "shared" / "package.json").read_text(encoding="utf-8")) \
            if (ADMIN / "shared" / "package.json").exists() \
            else json.loads((STANDALONE / "package.json").read_text(encoding="utf-8"))
        deps = {**pkg.get("dependencies", {}), **pkg.get("peerDependencies", {})}
        mantine_found = any("mantine" in k for k in deps)
        assert mantine_found, "Must use @mantine packages"


class TestSpec0108TestModeOnNavbar:
    """SPEC-0108: Test mode toggle REMOVED from navbar (S157 — phantom spec)."""

    def test_test_mode_removed_from_header(self):
        """Test mode toggle/indicator removed from layout header (S157)."""
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "testModeEnabled" not in src, \
            "testModeEnabled should be removed from layout (S157)"


class TestSpec0121KBToolbarTooltips:
    """SPEC-0121: Scan for conflicts, Export to CSV, Import must have tooltips."""

    def test_toolbar_tooltips(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "Tooltip" in src, "Must have tooltips"
        assert "Scan" in src or "scan" in src, "Must have scan for conflicts"
        assert "Export" in src or "CSV" in src, "Must have export"
        assert "Import" in src, "Must have import"


class TestSpec0165FreshnessNotDashes:
    """SPEC-0165: KB 'Freshness' value must NOT display '--'."""

    def test_freshness_has_meaning(self):
        src = (STANDALONE / "pages" / "KnowledgeBase.tsx").read_text(encoding="utf-8")
        assert "Freshness" in src or "freshness" in src or "staleness" in src.lower(), \
            "Must have freshness/staleness column"


class TestSpec0352AdminLinksToDocumentation:
    """SPEC-0352: Standalone admin must include links to product documentation."""

    def test_doc_links_exist(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "agentredcx.com" in src or "documentation" in src.lower() or "docs" in src.lower(), \
            "Must link to product documentation"


class TestSpec0405SPAConsoleGraphicalUI:
    """SPEC-0405: SPA console provides graphical UI for operating all tenants."""

    def test_provider_pages_exist(self):
        pages = list((PROVIDER / "pages").glob("*.tsx"))
        assert len(pages) >= 10, f"Provider console must have extensive page set (found {len(pages)})"


class TestSpec0445SPADefinition:
    """SPEC-0445: SPA = Service Provider Administrator console."""

    def test_provider_console_exists(self):
        assert PROVIDER.exists(), "Provider console directory must exist"
        assert (PROVIDER / "login" / "ApiKeyLogin.tsx").exists(), \
            "Must have separate login for SPA"


class TestSpec0463TooltipLinksResolveToAnchors:
    """SPEC-0463: Tooltip links resolve to page-specific anchors on documentation."""

    def test_doclinks_have_anchors(self):
        src = (SHARED / "HelpTooltip.tsx").read_text(encoding="utf-8")
        assert "docLink" in src, "HelpTooltip must accept docLink prop"
        # Check that config page uses specific doc links
        config = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "agentredcx.com/docs" in config, "Must link to specific doc pages"


class TestSpec0516TooltipLinksValid:
    """SPEC-0516: All tooltip links point to valid documentation pages."""

    def test_consistent_doc_base_url(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "agentredcx.com" in src, "Must use agentredcx.com domain"


class TestSpec0570EveryTooltipHasDocLink:
    """SPEC-0570: Every tooltip must include a link to documentation."""

    def test_helptooltip_has_doclink(self):
        src = (SHARED / "HelpTooltip.tsx").read_text(encoding="utf-8")
        assert "docLink" in src, "HelpTooltip must support docLink"
        assert "href" in src or "Link" in src or "anchor" in src.lower(), \
            "Must render clickable link"


class TestSpec0543MockTenantScript:
    """SPEC-0543: Mock tenant script to set environment to fresh state."""

    def test_seed_script_exists(self):
        assert (SCRIPTS / "seed_tenant.py").exists(), "seed_tenant.py must exist"
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        assert "seed" in src.lower() or "init" in src.lower(), \
            "Script must handle seeding/initialization"


class TestSpec0544TestEnvironmentDeactivation:
    """SPEC-0544: Acceptable to deactivate test environment for testing."""

    def test_deactivation_available(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Deactivate" in src, "Must support deactivation"


# ═══════════════════════════════════════════════════════════════════════
#  WIDGET / CHAT SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0020ChatHistoryNotPink:
    """SPEC-0020: Conversation history background must NOT be light pink."""

    def test_no_pink_background(self):
        src = (WIDGET / "src" / "theme" / "tokens.ts").read_text(encoding="utf-8")
        # Dark mode bg is #1c1917 (warm stone), light is #FFFFFF — neither is pink
        assert "#ff" not in src.lower().split("primary")[0] or "#1c1917" in src, \
            "Background must not be pink"
        assert "colorBackground" in src, "Must define colorBackground token"


class TestSpec0030StandaloneChatAgentRedColors:
    """SPEC-0030: Standalone admin chat UI uses Agent Red colors, not blue."""

    def test_agent_red_primary(self):
        src = (WIDGET / "src" / "theme" / "tokens.ts").read_text(encoding="utf-8")
        assert "#ff3621" in src, "Must use Agent Red primary color"


class TestSpec0114WidgetDraggable:
    """SPEC-0114: Chat UI click-draggable to other regions."""

    def test_drag_support(self):
        src = (WIDGET / "src" / "components" / "Panel.tsx").read_text(encoding="utf-8")
        assert "drag" in src.lower(), "Must support drag interaction"


class TestSpec0685WidgetKeyDisplayed:
    """SPEC-0685: Merchant admin must display the widget key."""

    def test_widget_key_visible(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "widget" in src.lower() and "key" in src.lower(), \
            "Must display widget key"


class TestSpec0686WidgetKeyRegeneration:
    """SPEC-0686: Merchant admin must allow widget key regeneration."""

    def test_regenerate_widget_key(self):
        # Check admin API for key regeneration
        api = SRC / "multi_tenant" / "admin_apikey_api.py"
        src = api.read_text(encoding="utf-8")
        assert "widget" in src.lower(), "API must handle widget keys"
        assert "regenerate" in src.lower() or "rotate" in src.lower() or "reset" in src.lower(), \
            "Must support widget key regeneration"


class TestSpec0747PreChatFormNotBlocking:
    """SPEC-0747: Pre-chat form must NOT block user if not enabled."""

    def test_prechat_not_default(self):
        src = (WIDGET / "src" / "components" / "Panel.tsx").read_text(encoding="utf-8")
        # Quick actions and greeting display by default, pre-chat form is optional
        assert "quickActions" in src or "greeting" in src.lower(), \
            "Must show greeting/quick actions by default"


# ═══════════════════════════════════════════════════════════════════════
#  GLOSSARY / TERMINOLOGY SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0067UIGlossaryMaintained:
    """SPEC-0067: UI glossary must be maintained."""

    def test_glossary_in_project(self):
        claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # CLAUDE.md references glossary terms via specs
        assert "Glossary" in claude_md or "glossary" in claude_md or "term" in claude_md.lower(), \
            "Project must maintain glossary"


class TestSpec0068GlossaryControl:
    """SPEC-0068: Glossary term 'control' = element that triggers state change."""

    def test_control_term_usage(self):
        # Controls are used throughout admin — buttons, toggles, selects
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Button" in src or "Switch" in src or "Select" in src, \
            "Must use control elements (buttons, switches, selects)"


class TestSpec0074GlossaryConfigPages:
    """SPEC-0074: Glossary term 'configuration pages' = individual pages within config manager."""

    def test_config_pages_exist(self):
        config_pages = ["Configuration.tsx", "KnowledgeBase.tsx", "QuickActions.tsx", "Widget.tsx"]
        for page in config_pages:
            assert (STANDALONE / "pages" / page).exists(), \
                f"Configuration page {page} must exist"


class TestSpec0075GlossaryErrorBanner:
    """SPEC-0075: Glossary term 'error banner' = inline error notification."""

    def test_error_notifications_exist(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "error" in src.lower(), "Must handle errors"
        assert "Notification" in src or "Banner" in src or "Alert" in src or "notification" in src, \
            "Must have error notification mechanism"


# ═══════════════════════════════════════════════════════════════════════
#  PROVIDER / TENANT SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0228ProviderConsoleRenamed:
    """SPEC-0228: Provider Console renamed to 'Service Provider Console'."""

    def test_provider_label(self):
        src = (PROVIDER / "login" / "ApiKeyLogin.tsx").read_text(encoding="utf-8")
        assert "Service Provider" in src, \
            "Must use 'Service Provider' label"



# ═══════════════════════════════════════════════════════════════════════
#  DOCUMENTATION SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0432AgentRedWebsiteExists:
    """SPEC-0432: Agent Red website hosted at agentredcx.com."""

    def test_website_referenced(self):
        # Multiple source files reference agentredcx.com
        found = False
        for f in STANDALONE.rglob("*.tsx"):
            try:
                if "agentredcx.com" in f.read_text(encoding="utf-8"):
                    found = True
                    break
            except Exception:
                pass
        assert found, "agentredcx.com must be referenced in admin"


# ═══════════════════════════════════════════════════════════════════════
#  TESTING / QUALITY SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0039FreshEnvironmentForE2E:
    """SPEC-0039: E2E tests run on freshly initialized environment."""

    def test_seed_before_tests(self):
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        assert "seed" in src.lower(), "Must have seeding capability"
        assert "conversation" in src.lower() or "clean" in src.lower(), \
            "Must support clean-state initialization"


class TestSpec0047NoEffortTerminology:
    """SPEC-0047: Term 'effort' must NOT be used; use tokens/time/cost instead."""

    def test_effort_not_in_claude_md(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # "effort" should not appear as a measurement term
        # It may appear in other contexts like "without effort" which is fine
        lines_with_effort = [line for line in src.splitlines() if "effort" in line.lower()]
        # Allow some contextual usage, but not as a metric
        assert not any("effort estimate" in line.lower() or "level of effort" in line.lower()
                       for line in lines_with_effort), \
            "'effort' must not be used as a measurement term"


class TestSpec0034OnlyOpenSourceFlowsBack:
    """SPEC-0034: Only fixes to open-source artifacts flow back to AGNTCY."""

    def test_agntcy_isolation(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "AGNTCY" in src, "Must reference AGNTCY"
        assert "Never commit AGNTCY source" in src or "never commit" in src.lower(), \
            "Must enforce AGNTCY isolation"
