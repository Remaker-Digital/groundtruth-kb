"""
Migrate internal knowledge markdown files to Knowledge DB (GOV-08 compliance).

Reads each internal markdown file and inserts it into the documents table.
External-facing files (wiki, website, legal, branding, README) are excluded.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import os
import glob
from pathlib import Path

# Add knowledge-db to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB

# Windows encoding safety
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", errors="replace", closefd=False)

db = KnowledgeDB()
base = Path(__file__).parent.parent
migrated = 0
skipped = 0
errors = []

# Define all internal knowledge files to migrate
# Format: (doc_id, title, category, tags, filepath)
FILES = [
    # --- Operations / Procedures not already in KB ---
    ("doc-session-wrap-up", "Session Wrap-Up Procedure", "procedure",
     ["operations", "session", "wrap-up"], "docs/operations/session-wrap-up-procedure.md"),
    ("doc-pre-flight-checklist", "Pre-Flight Deployment Checklist", "procedure",
     ["operations", "deployment", "pre-flight"], "docs/operations/pre-flight-deployment-checklist.md"),
    ("doc-release-plan-v1.57", "Release Plan v1.57", "procedure",
     ["operations", "release", "deployment"], "docs/operations/release-plan-v1.57.md"),
    ("doc-repeatable-procedures", "Repeatable Procedures Master Doc", "procedure",
     ["operations", "procedures"], "docs/operations/REPEATABLE-PROCEDURES.md"),
    ("doc-catastrophic-recovery", "Catastrophic Recovery Runbook", "procedure",
     ["operations", "recovery", "runbook"], "docs/operations/CATASTROPHIC-RECOVERY-RUNBOOK.md"),
    ("doc-deployment-runbook", "Deployment Runbook", "procedure",
     ["operations", "deployment", "runbook"], "docs/operations/DEPLOYMENT-RUNBOOK.md"),
    ("doc-launch-checklist", "Launch Checklist", "procedure",
     ["operations", "launch"], "docs/operations/LAUNCH-CHECKLIST.md"),
    ("doc-load-test-baseline", "Load Test Baseline", "procedure",
     ["operations", "load-test", "baseline"], "docs/operations/LOAD-TEST-BASELINE.md"),
    ("doc-option-c-upgrade", "Option C Upgrade Path", "procedure",
     ["operations", "upgrade", "geo-replication"], "docs/operations/OPTION-C-UPGRADE-PATH.md"),
    ("doc-pre-ga-verification", "Pre-GA Verification Checklist", "procedure",
     ["operations", "verification", "pre-ga"], "docs/operations/PRE-GA-VERIFICATION-CHECKLIST.md"),
    ("doc-quarterly-cost-review", "Quarterly Cost Review", "procedure",
     ["operations", "cost", "review"], "docs/operations/QUARTERLY-COST-REVIEW.md"),
    ("doc-release-management", "Release Management", "procedure",
     ["operations", "release"], "docs/operations/RELEASE-MANAGEMENT.md"),
    ("doc-shopify-app-review-preflight", "Shopify App Review Preflight Checklist", "procedure",
     ["operations", "shopify", "app-review"], "docs/operations/SHOPIFY-APP-REVIEW-PREFLIGHT-CHECKLIST.md"),
    ("doc-agntcy-adoption", "AGNTCY Platform Adoption Procedure", "procedure",
     ["operations", "agntcy", "adoption"], "docs/operations/agntcy-platform-adoption-procedure.md"),
    ("doc-knowledge-automation-proc", "Knowledge Automation Procedure", "procedure",
     ["operations", "knowledge", "automation"], "docs/operations/knowledge-automation-procedure.md"),
    ("doc-upgrade-runbook-1.0-1.1", "Upgrade Runbook 1.0 to 1.1", "procedure",
     ["operations", "upgrade", "runbook"], "docs/operations/UPGRADE-RUNBOOK-1.0-TO-1.1.md"),
    ("doc-external-url-reachability", "External URL Reachability Procedure", "procedure",
     ["operations", "testing", "url-reachability"], "docs/operations/external-url-reachability-procedure.md"),
    # Test procedures (full doc content — KB test_procedures table has structured metadata only)
    ("doc-api-security-procedure", "API Security Test Procedure (full doc)", "test-procedure",
     ["testing", "security", "api"], "docs/operations/api-security-test-procedure.md"),
    ("doc-cq-procedure", "Conversation Quality Test Procedure (full doc)", "test-procedure",
     ["testing", "quality"], "docs/operations/conversation-quality-test-procedure.md"),
    ("doc-data-integrity-procedure", "Data Integrity Test Procedure (full doc)", "test-procedure",
     ["testing", "data-integrity"], "docs/operations/data-integrity-test-procedure.md"),
    ("doc-rate-limit-procedure", "Rate Limit Test Procedure (full doc)", "test-procedure",
     ["testing", "rate-limit"], "docs/operations/rate-limit-test-procedure.md"),
    ("doc-resilience-procedure", "Resilience & Failover Test Procedure (full doc)", "test-procedure",
     ["testing", "resilience"], "docs/operations/resilience-failover-test-procedure.md"),
    ("doc-tenant-isolation-procedure", "Tenant Isolation Test Procedure (full doc)", "test-procedure",
     ["testing", "tenant-isolation"], "docs/operations/tenant-isolation-test-procedure.md"),
    ("doc-ui-test-procedure", "UI Test Procedure (full doc)", "test-procedure",
     ["testing", "ui"], "docs/operations/ui-test-procedure.md"),
    ("doc-chrome-ui-procedure", "Chrome MCP UI Test Procedure (full doc)", "test-procedure",
     ["testing", "ui", "chrome-mcp"], "docs/operations/chrome-ui-test-procedure.md"),
    ("doc-load-test-procedure", "Load Test Procedure (full doc)", "test-procedure",
     ["testing", "load"], "docs/operations/load-test-procedure.md"),
    ("doc-visual-regression-procedure", "Visual Regression Test Procedure (full doc)", "test-procedure",
     ["testing", "visual-regression"], "docs/operations/visual-regression-test-procedure.md"),
    ("doc-upgrade-verification-proc", "Upgrade Verification Procedure (full doc)", "test-procedure",
     ["testing", "upgrade"], "docs/operations/upgrade-verification-procedure.md"),
    ("doc-initialization-procedure", "Initialization Procedure (full doc)", "procedure",
     ["operations", "initialization"], "docs/operations/initialization-procedure.md"),
    ("doc-build-deploy-procedure", "Build & Deploy Procedure (full doc)", "procedure",
     ["operations", "deployment"], "docs/operations/build-deploy-procedure.md"),
    # --- Key docs ---
    ("doc-master-test-plan", "Master Test Plan 1.0", "test-plan",
     ["testing", "master-plan", "ga-release"], "docs/MASTER-TEST-PLAN-1.0.md"),
    ("doc-protected-behaviors", "Protected Behaviors Registry", "governance",
     ["protected-behaviors", "regression"], "docs/PROTECTED-BEHAVIORS.md"),
    ("doc-frozen-backlog", "Frozen Backlog (New Work Items)", "backlog",
     ["backlog", "work-items", "frozen"], "docs/archive/BACKLOG-NEW-WORK-ITEMS-FROZEN.md"),
    # --- Architecture ---
    ("doc-admin-design-system", "Admin Design System", "architecture",
     ["admin", "design-system", "ui"], "docs/architecture/admin-design-system.md"),
    ("doc-cdn-static-hosting", "CDN Static Hosting Architecture", "architecture",
     ["cdn", "hosting", "infrastructure"], "docs/architecture/CDN-STATIC-HOSTING-ARCHITECTURE.md"),
    ("doc-ecommerce-eval", "E-Commerce Platform Evaluation", "architecture",
     ["ecommerce", "evaluation"], "docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md"),
    ("doc-knowledge-automation-arch", "Knowledge Automation Architecture", "architecture",
     ["knowledge", "automation"], "docs/architecture/knowledge-automation.md"),
    ("doc-ai-personalization", "Per-Customer AI Personalization Research", "architecture",
     ["ai", "personalization", "research"], "docs/architecture/PER-CUSTOMER-AI-PERSONALIZATION-RESEARCH.md"),
    ("doc-pcm-metrics", "Persistent Customer Memory Metrics", "architecture",
     ["pcm", "memory", "metrics"], "docs/architecture/PERSISTENT-CUSTOMER-MEMORY-METRICS.md"),
    ("doc-rag-gap-analysis", "RAG Gap Analysis", "architecture",
     ["rag", "gap-analysis"], "docs/architecture/RAG-GAP-ANALYSIS.md"),
    ("doc-rewardful", "Rewardful Integration", "architecture",
     ["rewardful", "affiliate", "integration"], "docs/architecture/REWARDFUL-INTEGRATION.md"),
    ("doc-ui-enhancement", "UI Enhancement Proposal 2026-02-17", "architecture",
     ["ui", "enhancement", "proposal"], "docs/architecture/UI-ENHANCEMENT-PROPOSAL-2026-02-17.md"),
    ("doc-ui-ux-decisions", "UI/UX Architecture Decisions", "architecture",
     ["ui", "ux", "decisions"], "docs/architecture/UI-UX-ARCHITECTURE-DECISIONS.md"),
    # --- Research ---
    ("doc-hugo-comparison", "Agent Red vs Hugo AI Comparison", "research",
     ["competitive", "hugo-ai"], "docs/research/AGENT-RED-VS-HUGO-AI-COMPARISON.md"),
    ("doc-competitor-docs", "Competitor Documentation Analysis", "research",
     ["competitive", "documentation"], "docs/research/COMPETITOR-DOCUMENTATION-ANALYSIS.md"),
    ("doc-cq-improvement-report", "Conversation Quality Improvement Report", "research",
     ["conversation-quality", "improvement"], "docs/research/CONVERSATION-QUALITY-IMPROVEMENT-REPORT-2026-02-17.md"),
    ("doc-shopify-research", "Shopify Partner App Store Research", "research",
     ["shopify", "partner", "research"], "docs/research/SHOPIFY-PARTNER-APP-STORE-RESEARCH.md"),
    ("doc-stripe-eval", "Stripe Platform Evaluation", "research",
     ["stripe", "payments", "evaluation"], "docs/research/STRIPE-PLATFORM-EVALUATION.md"),
    ("doc-ui-ux-competitive", "UI/UX Competitive Analysis", "research",
     ["ui", "ux", "competitive"], "docs/research/UI-UX-COMPETITIVE-ANALYSIS.md"),
    # --- Root docs ---
    ("doc-agntcy-baseline", "AGNTCY Baseline Verification Report", "assessment",
     ["agntcy", "baseline"], "docs/AGNTCY-BASELINE-VERIFICATION-REPORT.md"),
    ("doc-commercial-saas", "Commercial SaaS Proposal", "proposal",
     ["commercial", "saas"], "docs/COMMERCIAL-SAAS-PROPOSAL.md"),
    ("doc-comprehensive-test", "Comprehensive Test Plan", "test-plan",
     ["testing", "comprehensive"], "docs/COMPREHENSIVE-TEST-PLAN.md"),
    ("doc-integration-testing", "Integration Testing Setup", "test-plan",
     ["testing", "integration"], "docs/INTEGRATION-TESTING-SETUP.md"),
    ("doc-master-plan-review", "Master Plan Review 2026-01-30", "assessment",
     ["planning", "review"], "docs/Master-Plan-Review-01-30-2026.md"),
    ("doc-product-features-rag", "Product Features RAG Reference", "reference",
     ["product", "features", "rag"], "docs/PRODUCT-FEATURES-RAG.md"),
    ("doc-project-plan", "Project Plan", "reference",
     ["project", "planning"], "docs/PROJECT-PLAN.md"),
    ("doc-rag-config-enhancements", "RAG Config Management Enhancements", "proposal",
     ["rag", "configuration"], "docs/RAG-CONFIGURATION-MANAGEMENT-ENHANCEMENTS-PROPOSAL.md"),
    ("doc-strategic-assessment", "Strategic Assessment 2026-02-07", "assessment",
     ["strategic", "assessment"], "docs/STRATEGIC-ASSESSMENT-2026-02-07.md"),
    # --- Tests ---
    ("doc-launch-ui-test", "Launch UI Test Standalone Admin", "test-results",
     ["testing", "ui", "launch"], "docs/tests/LAUNCH-UI-TEST-STANDALONE-ADMIN.md"),
    ("doc-luit-sa-results", "LUIT-SA Test Results", "test-results",
     ["testing", "ui", "results"], "docs/tests/LUIT-SA-TEST-RESULTS.md"),
    ("doc-master-test-results", "Master Test Execution Results 1.0", "test-results",
     ["testing", "execution", "results"], "docs/tests/MASTER-TEST-EXECUTION-RESULTS-1.0.md"),
    # --- Workflows ---
    ("doc-wf-storefront", "Workflow: Storefront Overview", "workflow",
     ["workflow", "storefront"], "docs/workflows/01-Storefront-Overview.md"),
    ("doc-wf-admin-dashboard", "Workflow: Embedded Admin Dashboard", "workflow",
     ["workflow", "admin", "dashboard"], "docs/workflows/02-Embedded-Admin-Dashboard.md"),
    ("doc-wf-widget-activation", "Workflow: Widget Activation", "workflow",
     ["workflow", "widget", "activation"], "docs/workflows/03-Widget-Activation.md"),
    # --- Marketing / Vision ---
    ("doc-linkedin-launch", "LinkedIn Article: Agent Red Launch", "marketing",
     ["marketing", "linkedin"], "docs/marketing/linkedin-article-agent-red-launch.md"),
    ("doc-agent-red-vision", "Agent Red Vision", "vision",
     ["vision", "product"], "docs/marketing/agent-red-vision.md"),
    ("doc-conversational-commerce", "Conversational Commerce Vision", "vision",
     ["vision", "commerce"], "docs/vision/conversational-commerce-vision.md"),
    # --- Specs summary ---
    ("doc-specs-summary", "Specs Summary for Review", "reference",
     ["specifications", "summary"], "docs/specs-summary-for-review.md"),
    # --- Root-level governance docs ---
    ("doc-claude-reference", "CLAUDE Reference Data", "reference",
     ["claude", "reference"], "CLAUDE-REFERENCE.md"),
    ("doc-claude-architecture", "CLAUDE Architecture", "reference",
     ["claude", "architecture"], "CLAUDE-ARCHITECTURE.md"),
    ("doc-claude-archive", "CLAUDE Archive (Session History)", "reference",
     ["claude", "archive", "history"], "CLAUDE_ARCHIVE.md"),
    ("doc-changelog", "Changelog", "reference",
     ["changelog", "releases"], "CHANGELOG.md"),
    ("doc-vision-root", "Vision (Root)", "vision",
     ["vision", "product"], "vision.md"),
]

# Auto-discover independent assessments
for f in sorted(glob.glob(str(base / "independent-progress-assments" / "**" / "*.md"), recursive=True)):
    rel = os.path.relpath(f, base).replace("\\", "/")
    fname = os.path.basename(f).replace(".md", "")
    doc_id = "doc-ia-" + fname.lower().replace(" ", "-")[:45]
    FILES.append((doc_id, fname.replace("-", " ").title()[:80], "assessment",
                  ["independent-assessment"], rel))

# Auto-discover drafts
for f in sorted(glob.glob(str(base / "drafts" / "*.md"))):
    rel = os.path.relpath(f, base).replace("\\", "/")
    fname = os.path.basename(f).replace(".md", "")
    doc_id = "doc-draft-" + fname.lower().replace(" ", "-")[:45]
    FILES.append((doc_id, fname.replace("-", " ").title()[:80], "draft",
                  ["draft"], rel))


def main():
    global migrated, skipped, errors

    print(f"Migrating {len(FILES)} files to Knowledge DB...")
    print()

    for doc_id, title, category, tags, filepath in FILES:
        path = base / filepath
        if not path.exists():
            errors.append(f"NOT FOUND: {filepath}")
            continue

        # Skip if already migrated
        existing = db.get_document(doc_id)
        if existing:
            skipped += 1
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            db.insert_document(
                id=doc_id,
                title=title,
                category=category,
                status="active",
                changed_by="Claude (S109)",
                change_reason=f"GOV-08 migration: internal knowledge from {filepath}",
                content=content,
                tags=tags,
                source_path=filepath,
            )
            migrated += 1
        except Exception as e:
            errors.append(f"ERROR {filepath}: {e}")

    print(f"Migrated: {migrated}")
    print(f"Skipped (already exists): {skipped}")
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    print()

    summary = db.get_summary()
    print(f"Knowledge DB now has {summary['document_count']} documents")
    print(f"  Specs: {summary['spec_total']}")
    print(f"  Test procedures: {summary['test_procedure_count']}")
    print(f"  Op procedures: {summary['op_procedure_count']}")
    print(f"  Documents: {summary['document_count']}")
    print(f"  Env config: {summary['env_config_count']}")


if __name__ == "__main__":
    main()
