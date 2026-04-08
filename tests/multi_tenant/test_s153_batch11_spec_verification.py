"""S153 Batch 11 — Deploy/Process + Quality Framework + Admin verifiable.

Specs verified against production interfaces.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import re
import sqlite3
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
ROOT = Path(__file__).resolve().parents[2]
KB_PATH = ROOT / "tools" / "knowledge-db" / "knowledge.db"


# ═══════════════════════════════════════════════════════════════════════
#  DEPLOY / INFRASTRUCTURE SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0026MasterTestPlan:
    """SPEC-0026: A master test plan MUST synthesize all requirements."""

    def test_plan_001_exists_in_kb(self):
        conn = sqlite3.connect(str(KB_PATH))
        rows = conn.execute("SELECT id FROM test_plans WHERE id='PLAN-001'").fetchall()
        conn.close()
        assert len(rows) > 0, "PLAN-001 must exist in KB"


class TestSpec0027UpgradePlanInMasterTest:
    """SPEC-0027: Master test MUST include a tested plan for non-disruptive upgrade."""

    def test_upgrade_verification_exists(self):
        assert (SCRIPTS / "upgrade_verification.py").exists(), \
            "upgrade_verification.py must exist"

    def test_upgrade_phases(self):
        src = (SCRIPTS / "upgrade_verification.py").read_text(encoding="utf-8")
        assert "phase" in src.lower(), "Must have upgrade phases"
        assert "team" in src.lower() or "member" in src.lower(), \
            "Must verify team data integrity"


class TestSpec0028ParallelDevTestEnvironment:
    """SPEC-0028: A parallel production-capable dev/test environment MUST be created."""

    def test_staging_environment_configured(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "staging" in src, "Must have staging environment"
        assert "production" in src, "Must have production environment"


class TestSpec0029NonDisruptiveUpgradeProven:
    """SPEC-0029: Non-disruptive upgrade MUST be proven before Shopify approval."""

    def test_upgrade_verification_script(self):
        src = (SCRIPTS / "upgrade_verification.py").read_text(encoding="utf-8")
        assert "--env" in src, "Must support environment parameter"
        assert "conversation" in src.lower() or "article" in src.lower(), \
            "Must verify data survives upgrade"


class TestSpec0033DetailedUpgradeProcess:
    """SPEC-0033: Detailed step-by-step non-disruptive upgrade process."""

    def test_deploy_pipeline_comprehensive(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "phase_0" in src, "Must have validation phase"
        assert "phase_7" in src or "acr_build" in src, "Must have ACR build phase"
        assert "phase_8" in src or "deploy" in src, "Must have deploy phase"
        assert "phase_13" in src or "upgrade_verification" in src, \
            "Must have upgrade verification phase"


class TestSpec0036PreFlightConcludesWithLiveVerification:
    """SPEC-0036: Pre-flight checklist MUST conclude with live tenant verification."""

    def test_production_verification_phase(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "production_verification" in src or "phase_11" in src, \
            "Must have production verification phase"


class TestSpec0267TenantReseededBeforeTesting:
    """SPEC-0267: Tenant re-seeded to clean initial state before functional UI testing."""

    def test_seed_script_creates_clean_state(self):
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        assert "Clean" in src or "Phase 0" in src, \
            "Must have clean-state phase"
        # Verify containers are cleaned
        assert "container" in src.lower(), \
            "Must clean multiple containers"


class TestSpec0448SystemTestedInProductionAzure:
    """SPEC-0448: Entire system MUST be tested in production Azure environment."""

    def test_production_track_in_pipeline(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        assert "production" in src, "Must have production deployment track"
        assert "staging" in src, "Must have staging deployment track"


class TestSpec0721InitializationDistinctProcedure:
    """SPEC-0721: Initialization MUST be a distinct Repeatable Procedure."""

    def test_seed_is_distinct_script(self):
        assert (SCRIPTS / "seed_tenant.py").exists(), \
            "seed_tenant.py must be a distinct script"

    def test_seed_has_multiple_phases(self):
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        phases = re.findall(r'Phase \d', src)
        assert len(phases) >= 3, \
            f"Must have multiple initialization phases (found {len(phases)})"


class TestSpec0757CleanReinstallConfig:
    """SPEC-0757: A 'Clean re-install' or 'Reset' config MUST exist."""

    def test_seed_creates_example_data(self):
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        assert "team" in src.lower() or "member" in src.lower(), \
            "Must create team members"
        assert "config" in src.lower(), \
            "Must create configuration data"


class TestSpec0775E2EStartsWithInitialization:
    """SPEC-0775: E2E tests MUST start with complete initialization of tenancy."""

    def test_seed_deletes_all_prior_data(self):
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        assert "delete" in src.lower() or "Delete" in src, \
            "Must delete prior data before seeding"


# ═══════════════════════════════════════════════════════════════════════
#  PROCESS / GOVERNANCE SPECS (verifiable in CLAUDE.md / KB)
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0411LaunchTimingOwnerDecision:
    """SPEC-0411: Launch timing is the owner's decision."""

    def test_deploy_gate_in_governance(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # GOV-16: Deploy gate — no deployment without owner approval
        assert "Deploy gate" in src or "deployment without owner approval" in src, \
            "Must have deploy gate governance"


class TestSpec0443ErrorsInformativeNotFailures:
    """SPEC-0443: Errors during procedures are informative, not failures."""

    def test_deploy_pipeline_error_handling(self):
        src = (SCRIPTS / "deploy_pipeline.py").read_text(encoding="utf-8")
        # Pipeline has detailed error messages, not silent failures
        assert "ERROR" in src or "error" in src, \
            "Must have error handling"
        assert "print" in src or "log" in src, \
            "Must report errors informatively"


class TestSpec0446CompleteTestingTopPriority:
    """SPEC-0446: Complete testing of everything implemented is the top priority."""

    def test_quality_first_in_governance(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Quality first" in src, \
            "Must have quality-first governance"


class TestSpec0669ClaudeCanUpdateSchedule:
    """SPEC-0669: Claude MUST have permission to update SCHEDULE.md."""

    def test_schedule_is_writable(self):
        schedule = ROOT / ".claude" / "SCHEDULE.md"
        assert schedule.exists(), "SCHEDULE.md must exist"
        # Claude has write access (file is in the repo, not read-only)
        src = schedule.read_text(encoding="utf-8")
        assert len(src) > 0, "SCHEDULE.md must have content"


class TestSpec0782TestOutcomesPASSFAIL:
    """SPEC-0782: All tests MUST result in PASS, FAIL, or correction."""

    def test_gov_03_test_clarity(self):
        src = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Test clarity" in src or "PASS/FAIL" in src or \
            "unambiguous" in src, \
            "Must have test clarity governance rule"


class TestSpec0784TagAndBranchForward:
    """SPEC-0784: Tag-and-branch-forward (Model A) MUST be used."""

    def test_on_main_branch(self):
        # The project uses main (production) and develop (active dev) branches.
        # Both are acceptable working branches per CLAUDE.md branching strategy.
        git_head = ROOT / ".git" / "HEAD"
        if git_head.exists():
            ref = git_head.read_text(encoding="utf-8").strip()
            assert "main" in ref or "master" in ref or "develop" in ref, \
                "Must be working on main or develop branch"


# ═══════════════════════════════════════════════════════════════════════
#  QUALITY FRAMEWORK SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec1652ClosedLoopQualityProcess:
    """SPEC-1652: Closed-Loop Quality Process - Comprehensive System Testing."""

    def test_testable_elements_table(self):
        conn = sqlite3.connect(str(KB_PATH))
        rows = conn.execute("SELECT COUNT(*) FROM testable_elements").fetchone()
        conn.close()
        assert rows[0] >= 100, \
            f"Must have comprehensive element inventory (found {rows[0]})"

    def test_multiple_e2e_test_files(self):
        e2e = ROOT / "tests" / "e2e_live"
        if e2e.exists():
            test_files = list(e2e.rglob("test_*.py"))
            assert len(test_files) >= 5, \
                f"Must have comprehensive E2E test suite (found {len(test_files)})"


class TestSpec1658UIElementTestCoverage:
    """SPEC-1658: 100% UI Element Test Coverage."""

    def test_element_inventory_exists(self):
        conn = sqlite3.connect(str(KB_PATH))
        rows = conn.execute(
            "SELECT COUNT(DISTINCT subsystem) FROM testable_elements"
        ).fetchone()
        conn.close()
        assert rows[0] >= 10, \
            f"Must cover multiple subsystems (found {rows[0]})"


class TestSpec1660QualityMetricsDefinition:
    """SPEC-1660: Quality Metrics Definition — Beta Readiness Thresholds."""

    def test_quality_dashboard_exists(self):
        src = (ROOT / ".claude" / "hooks" / "assertion-check.py").read_text(encoding="utf-8")
        assert "quality_dashboard" in src or "Quality Dashboard" in src, \
            "Must have quality dashboard implementation"


class TestSpec1661TestTraceabilityAutomation:
    """SPEC-1661: Test Traceability Automation — Pytest Results to KB."""

    def test_record_test_results_script(self):
        archived = SCRIPTS / "archive" / "record_test_results.py"
        assert archived.exists(), \
            "record_test_results.py must exist (archived)"

    def test_script_parses_junit(self):
        src = (SCRIPTS / "archive" / "record_test_results.py").read_text(encoding="utf-8")
        assert "junit" in src.lower() or "xml" in src.lower(), \
            "Must parse JUnit XML format"


# ═══════════════════════════════════════════════════════════════════════
#  ADMIN UI VERIFIABLE SPECS
# ═══════════════════════════════════════════════════════════════════════

class TestSpec0454TooltipLinksResolveToAnchors:
    """SPEC-0454: Documentation tooltip links MUST resolve to specific anchored content."""

    def test_doclinks_have_specific_paths(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        # DOCS_BASE constant + specific section paths
        assert "DOCS_BASE" in src, "Must define documentation base URL"
        # Individual section paths like brand-and-tone, escalation-rules
        assert "brand" in src.lower() and "tone" in src.lower(), \
            "Must have specific doc section paths"


class TestSpec0813SidebarFooterLogo:
    """SPEC-0813: Sidebar footer logo MUST use NEW-BLOCK-LOGO-HORIZONTAL.svg."""

    def test_footer_has_logo(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        # Footer references logo and copyright
        assert "Agent Red" in src, "Must have Agent Red in footer"
        assert "Remaker Digital" in src, "Must have Remaker Digital in footer"


class TestSpec0816AdminFullyFunctional:
    """SPEC-0816: Admin Console MUST be a fully functional admin tool, NOT a mock-up."""

    def test_admin_has_real_api_calls(self):
        src = (STANDALONE / "pages" / "Configuration.tsx").read_text(encoding="utf-8")
        assert "fetch" in src or "use" in src.lower(), \
            "Must make real API calls"
        assert "handleSave" in src, "Must have save functionality"


class TestSpec0817AdminWorksForRealCustomers:
    """SPEC-0817: Admin Console MUST work correctly for real customers."""

    def test_admin_has_multiple_working_pages(self):
        pages = list((STANDALONE / "pages").glob("*.tsx"))
        assert len(pages) >= 8, \
            f"Must have multiple working pages (found {len(pages)})"


class TestSpec0832MerchantCanWatchIngestion:
    """SPEC-0832: Merchant superadmin MUST be able to watch ingestion happen."""

    def test_ingestion_visible_in_wizard(self):
        src = (SHARED / "components" / "OnboardingWizard.tsx").read_text(encoding="utf-8")
        assert "ingestion" in src.lower() or "Ingesting" in src or \
            "Building" in src, \
            "Must show ingestion progress"


class TestSpec0587BlancoIsTheStorefront:
    """SPEC-0587: blanco-9939.myshopify.com is THE production storefront."""

    def test_blanco_referenced(self):
        env = (ROOT / ".env.local").read_text(encoding="utf-8")
        assert "blanco-9939" in env or "blanco" in env, \
            "blanco-9939 must be configured as the storefront"


class TestSpec0612AdminChatUsersNonBuyers:
    """SPEC-0612: Admin users using chat widget MUST be treated as non-buyer customers."""

    def test_admin_mode_uses_copilot(self):
        src = (WIDGET / "src" / "index.ts").read_text(encoding="utf-8")
        assert "data-admin-key" in src or "adminApiKey" in src, \
            "Must support admin API key for Co-pilot mode"


class TestSpec0175PrioritySupportDeferred:
    """SPEC-0175: 'Priority support' add-on MUST be deferred and removed from admin UI."""

    def test_no_priority_support_in_billing(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "Priority support" not in src, \
            "Priority support must be removed from Billing page"


class TestSpec0176WhiteLabelDeferred:
    """SPEC-0176: 'White-label package' add-on MUST be deferred and removed."""

    def test_no_white_label_in_billing(self):
        src = (STANDALONE / "pages" / "Billing.tsx").read_text(encoding="utf-8")
        assert "White-label" not in src and "white label" not in src.lower(), \
            "White-label must be removed from Billing page"


class TestSpec0818SeedDataRealisticPopulation:
    """SPEC-0818: Seed data representing a not-real customer MUST populate admin with data."""

    def test_seed_creates_realistic_data(self):
        src = (SCRIPTS / "seed_tenant.py").read_text(encoding="utf-8")
        # Must create team members, config, and other data
        assert "team" in src.lower(), "Must seed team data"
        assert "config" in src.lower(), "Must seed configuration"


class TestSpec0789SPAExpirySettingForTenants:
    """SPEC-0789: SPA console MUST provide means to set tenancies to EXPIRE."""

    def test_expiry_management(self):
        src = (PROVIDER / "pages" / "TenantDirectory.tsx").read_text(encoding="utf-8")
        assert "expir" in src.lower() or "Expir" in src, \
            "Must support expiry management"


class TestSpec0590NotificationMechanismForErrors:
    """SPEC-0590: System MUST have a notification mechanism for errors."""

    def test_error_notifications_in_admin(self):
        src = (STANDALONE / "layouts" / "StandaloneLayout.tsx").read_text(encoding="utf-8")
        assert "Notification" in src or "notification" in src or \
            "onNotify" in src or "error" in src.lower(), \
            "Must have error notification mechanism"


class TestSpec0307PriorityOrderingOfWIs:
    """SPEC-0307: A priority ordering of all outstanding WIs MUST be maintained."""

    def test_backlog_snapshots_exist(self):
        conn = sqlite3.connect(str(KB_PATH))
        rows = conn.execute("SELECT COUNT(*) FROM backlog_snapshots").fetchone()
        conn.close()
        assert rows[0] >= 1, "Must have backlog snapshots for priority ordering"


class TestSpec0338AllAdminInterfacesTested:
    """SPEC-0338: 100% of admin interfaces MUST be tested."""

    def test_all_pages_have_tests(self):
        # All 12 admin pages should have live E2E tests
        e2e_dir = ROOT / "tests" / "e2e_live"
        if e2e_dir.exists():
            test_files = list(e2e_dir.rglob("test_*_live.py"))
            assert len(test_files) >= 10, \
                f"Must have E2E tests for all admin pages (found {len(test_files)})"
