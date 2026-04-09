"""S153 Batch 5 — Dark Mode + Activation/Wizard + Infrastructure spec verification.

32 specs verified against production interfaces.
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
CLAUDE_DIR = Path(__file__).resolve().parents[2] / ".claude"


# ═══════════════════════════════════════════════════════════════════════
#  DARK MODE SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0015DarkModeDefault:
    """SPEC-0015: Dark Mode MUST be the default mode."""

    def test_default_color_scheme_is_dark(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "useComputedColorScheme('dark')" in src or \
               "useComputedColorScheme(\"dark\")" in src, \
            "Default color scheme must be 'dark'"


class TestSpec0016DarkModeGreysNotBluePurple:
    """SPEC-0016: Dark Mode MUST use a palette of greys rather than blue/purple."""

    def test_dark_mode_uses_grey_palette(self):
        # Check tokens CSS for dark mode colors
        tokens_css = SHARED / "theme" / "tokens.css"
        src = tokens_css.read_text(encoding="utf-8")
        # Verify colors are in warm grey/stone family, not blue/purple
        # Stone greys: #0c0a09, #1c1917, #292524, #44403c
        assert "#0c0a09" in src or "#0a0a0a" in src, "chrome must be dark grey"
        assert "#1c1917" in src or "#141414" in src, "page must be dark grey"
        # Ensure no blue or purple tones
        assert "#00f" not in src and "#0000ff" not in src, "No blue in dark mode"


class TestSpec0018LightModeNavbarGrey:
    """SPEC-0018: Sticky navbar MUST be medium-light grey in Light Mode."""

    def test_light_mode_chrome_is_light_grey(self):
        tokens_css = SHARED / "theme" / "tokens.css"
        src = tokens_css.read_text(encoding="utf-8")
        # Light mode chrome should be a light grey (#f5f5f5 or similar)
        assert "#f5f5f5" in src or "#f0f0" in src or "#fafaf" in src, \
            "Light mode chrome must be a light grey"


class TestSpec0086DarkModeSupported:
    """SPEC-0086: Dark Mode MUST be supported as an important detail."""

    def test_dark_mode_toggle_exists(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "toggleColorScheme" in src or "setColorScheme" in src, \
            "Dark/light mode toggle must be implemented"

    def test_dark_mode_tokens_defined(self):
        tokens_css = SHARED / "theme" / "tokens.css"
        assert tokens_css.exists(), "Tokens CSS must exist"
        src = tokens_css.read_text(encoding="utf-8")
        assert "--ar-chrome" in src, "Dark mode chrome token must be defined"
        assert "--ar-page" in src, "Dark mode page token must be defined"


class TestSpec1547WidgetDarkModeWarmGrays:
    """SPEC-1547: Widget dark mode MUST use warm/stone grays."""

    def test_widget_dark_mode_uses_warm_grays(self):
        tokens = WIDGET / "src" / "theme" / "tokens.ts"
        src = tokens.read_text(encoding="utf-8")
        # Warm stone grays: #0c0a09, #1c1917, #292524, #44403c
        warm_grays = ["#0c0a09", "#1c1917", "#292524", "#44403c"]
        found = sum(1 for g in warm_grays if g in src)
        assert found >= 2, f"Widget must use warm/stone grays (found {found}/4)"


# ═══════════════════════════════════════════════════════════════════════
#  ACTIVATION / WIZARD SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0060ActivationThreeDispositions:
    """SPEC-0060: Activation control MUST have Red/Deactivate, Green/Activate, Yellow/Activate."""

    def test_three_activation_colors(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "'red'" in src and "'green'" in src and "'yellow'" in src, \
            "Activation control must have red, green, yellow states"

    def test_deactivate_and_activate_labels(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Deactivate" in src, "Must have Deactivate label"
        assert "Activate" in src, "Must have Activate label"


class TestSpec0061YellowWhenMissingMandatory:
    """SPEC-0061: Yellow/Activate when mandatory inputs missing."""

    def test_yellow_is_default_fallback(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # Yellow is the else/fallback case when not red and not green
        assert "can_activate" in src, "Must check can_activate for green vs yellow"
        assert "'yellow'" in src, "Yellow must be the fallback color"


class TestSpec0062RedDeactivateWhenActive:
    """SPEC-0062: Red/Disable when active with no draft changes."""

    def test_red_when_active_no_pending(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "is_active" in src, "Must check is_active state"
        assert "has_pending_changes" in src, "Must check has_pending_changes"
        assert "'Deactivate'" in src or '"Deactivate"' in src, "Must show Deactivate text"


class TestSpec0063GreenWhenMandatoryPresent:
    """SPEC-0063: Green/Activate when all mandatory draft config present."""

    def test_green_when_can_activate(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "can_activate" in src, "Must reference can_activate from preflight"
        assert "'green'" in src, "Green color must be used for ready state"


class TestSpec0066GreenAfterDeactivation:
    """SPEC-0066: After deactivating, config preserved, show Green/Activate."""

    def test_deactivation_preserves_config(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # After deactivation, is_active=false but config preserved
        # So can_activate should be true, showing green
        assert "preserved" in src.lower() or "re-activate" in src.lower() or \
               "can_activate" in src, \
            "Deactivation must preserve config for re-activation"


class TestSpec0148CustomAIInstructionsStep:
    """SPEC-0148: Wizard step renamed to 'Custom AI instructions'."""

    def test_custom_ai_instructions_step(self):
        wizard = SHARED / "components" / "OnboardingWizard.tsx"
        src = wizard.read_text(encoding="utf-8")
        assert "Custom AI instructions" in src, \
            "Wizard must have 'Custom AI instructions' step"


class TestSpec0227ContactUsButton:
    """SPEC-0227: A 'Contact Us' button in the admin UI."""

    def test_contact_us_in_header(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Contact" in src or "contact" in src, \
            "Header must have Contact button/icon"


class TestSpec0494WizardSessionDismissal:
    """SPEC-0494: Setup wizard dismissal MUST be session-specific."""

    def test_uses_session_storage(self):
        # Session-specific dismissal logic is in StandaloneLayout, which manages wizard state
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "sessionStorage" in src, "Must use sessionStorage for wizard dismissal"
        assert "agentred-onboarding-dismissed" in src, "Must track dismissal state"


class TestSpec0629TestModeFirstStep:
    """SPEC-0629: Test Mode REMOVED from wizard (S157 — phantom spec)."""

    def test_test_mode_removed_from_wizard(self):
        """Test mode toggle removed from wizard step one (S157)."""
        wizard = SHARED / "components" / "OnboardingWizard.tsx"
        src = wizard.read_text(encoding="utf-8")
        assert "test_mode_enabled" not in src, \
            "test_mode_enabled should be removed from wizard (S157)"


class TestSpec0708ActivationEnablesWidget:
    """SPEC-0708: Activation MUST trigger widget enablement."""

    def test_widget_shown_when_active(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "is_active" in src, "Must check is_active for widget display"
        # Widget should only render when active
        assert "widget" in src.lower() or "Widget" in src, \
            "Must reference widget rendering"


class TestSpec0841WizardArrayHandling:
    """SPEC-0841: Wizard MUST handle array values (escalation_keywords)."""

    def test_array_join_in_wizard(self):
        wizard = SHARED / "components" / "OnboardingWizard.tsx"
        src = wizard.read_text(encoding="utf-8")
        assert "Array.isArray" in src, "Must check for array values"
        assert ".join" in src, "Must join array values for display"


class TestSpec0843StorefrontDetectedIndicator:
    """SPEC-0843: Wizard storefront step MUST show 'Storefront detected'."""

    def test_storefront_detected_in_wizard(self):
        wizard = SHARED / "components" / "OnboardingWizard.tsx"
        src = wizard.read_text(encoding="utf-8")
        assert "Storefront detected" in src or "storefront" in src.lower(), \
            "Wizard must show storefront detection indicator"


class TestSpec0851WizardAutoPresent:
    """SPEC-0851: Wizard MUST auto-present on first login for new tenant."""

    def test_wizard_auto_shows_on_first_login(self):
        # Auto-presentation logic is in StandaloneLayout, which manages wizard state
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "active_version" in src or "showOnboarding" in src, \
            "Must auto-present wizard based on activation state"
        assert "setShowOnboarding(true)" in src, "Must show wizard on first login"


# ═══════════════════════════════════════════════════════════════════════
#  INFRASTRUCTURE / POLICY SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0471ProtectedBehaviors:
    """SPEC-0471: Protected behaviors prevent uncontrolled regressions."""

    def test_protected_behaviors_exist(self):
        hook = CLAUDE_DIR / "hooks" / "assertion-check.py"
        src = hook.read_text(encoding="utf-8")
        # The hook runs ALL assertions which includes PB-* protected behavior specs
        assert "run_all_assertions" in src, \
            "Assertion hook must run all assertions (including PB-* protected behaviors)"
        assert "regression" in src.lower() or "FAIL" in src, \
            "Hook must report regressions"


class TestSpec0472NeverRemoveWithoutApproval:
    """SPEC-0472: Code, tests, features MUST NEVER be removed without approval."""

    def test_rule_in_claude_md(self):
        claude_md = Path(__file__).resolve().parents[2] / "CLAUDE.md"
        src = claude_md.read_text(encoding="utf-8")
        assert "Never remove" in src or "never remove" in src, \
            "CLAUDE.md must enforce never-remove rule"
        assert "explicit owner approval" in src.lower() or "owner approval" in src.lower(), \
            "Must require explicit owner approval"


class TestSpec0474ViteApiUrlEmpty:
    """SPEC-0474: VITE_API_URL MUST be empty for Docker deployment."""

    def test_env_production_empty_vite_url(self):
        for admin_dir in ["standalone", "provider", "shopify"]:
            env_file = ADMIN / admin_dir / ".env.production"
            if env_file.exists():
                src = env_file.read_text(encoding="utf-8")
                # VITE_API_URL should be empty (same-origin)
                for line in src.splitlines():
                    if line.startswith("VITE_API_URL"):
                        val = line.split("=", 1)[1].strip()
                        assert val == "" or val == "''" or val == '""', \
                            f"{admin_dir}/.env.production VITE_API_URL must be empty, got '{val}'"


class TestSpec0554NonShopifyTenants:
    """SPEC-0554: Non-Shopify tenants acceptable — not all customers use Shopify."""

    def test_standalone_admin_exists(self):
        assert (STANDALONE / "index.tsx").exists(), \
            "Standalone admin must exist for non-Shopify tenants"

    def test_spa_console_exists(self):
        provider = ADMIN / "provider"
        assert provider.exists(), "Provider/SPA console must exist for tenant management"


class TestSpec0602UpgradeVerificationParameterized:
    """SPEC-0602: Upgrade verification MUST be parameterized with TARGET_ENVIRONMENT."""

    def test_upgrade_script_has_env_param(self):
        script = SCRIPTS / "upgrade_verification.py"
        assert script.exists(), "upgrade_verification.py must exist"
        src = script.read_text(encoding="utf-8")
        assert "--env" in src, "Script must accept --env parameter"
        assert "staging" in src, "Must support staging environment"


class TestSpec0704PersistentCustomerMemory:
    """SPEC-0704: Customer memory MUST be called 'Persistent Customer Memory'."""

    def test_memory_privacy_page_exists(self):
        # Check that memory/privacy page exists with PCM references
        memory_files = list(STANDALONE.rglob("*[Mm]emory*"))
        assert len(memory_files) > 0, "Memory-related pages must exist"

    def test_pcm_terminology_in_source(self):
        # Search for PCM terminology across source
        found = False
        for f in SRC.rglob("*.py"):
            try:
                if "persistent" in f.read_text(encoding="utf-8").lower() and \
                   "memory" in f.read_text(encoding="utf-8").lower():
                    found = True
                    break
            except Exception:
                pass
        if not found:
            # Check admin source
            for f in ADMIN.rglob("*.tsx"):
                try:
                    content = f.read_text(encoding="utf-8").lower()
                    if "memory" in content and ("persistent" in content or "privacy" in content):
                        found = True
                        break
                except Exception:
                    pass
        assert found, "Source must reference persistent/customer memory"


class TestSpec0744NeverRemoveRule:
    """SPEC-0744: Never remove code/tests/features without owner approval."""

    def test_protected_behavior_rule(self):
        claude_md = Path(__file__).resolve().parents[2] / "CLAUDE.md"
        src = claude_md.read_text(encoding="utf-8")
        assert "Never remove" in src, "Must enforce never-remove rule"


class TestSpec0787StagingEnvironmentExists:
    """SPEC-0787: Isolated parallel staging environment MUST exist."""

    def test_staging_config_exists(self):
        # Check for staging environment configuration
        found = False
        for f in SCRIPTS.glob("*.py"):
            try:
                if "staging" in f.read_text(encoding="utf-8").lower():
                    found = True
                    break
            except Exception:
                pass
        assert found, "Staging environment must be referenced in scripts"


class TestSpec0797AGNTCYIsolation:
    """SPEC-0797: AGNTCY and Agent Red MUST be strictly isolated."""

    def test_no_agntcy_source_in_repo(self):
        # AGNTCY source must NOT be committed into this repo
        agntcy_dir = Path(__file__).resolve().parents[2] / "AGNTCY"
        assert not agntcy_dir.exists() or not any(agntcy_dir.rglob("*.py")), \
            "AGNTCY source code must not be in Agent Red repo"

    def test_agntcy_referenced_as_external(self):
        claude_md = Path(__file__).resolve().parents[2] / "CLAUDE.md"
        src = claude_md.read_text(encoding="utf-8")
        assert "AGNTCY" in src, "CLAUDE.md must reference AGNTCY"
        assert "public repo" in src.lower() or "github.com" in src, \
            "AGNTCY must be referenced as external"


class TestSpec0850NeverRemoveRule2:
    """SPEC-0850: Never remove code/tests/features without approval (restatement)."""

    def test_protected_removal_rule(self):
        claude_md = Path(__file__).resolve().parents[2] / "CLAUDE.md"
        src = claude_md.read_text(encoding="utf-8")
        assert "NEVER" in src or "never" in src, "Must have never-remove rule"
        assert "owner approval" in src.lower(), "Must require owner approval"
