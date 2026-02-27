#!/usr/bin/env python3
"""
Batch migrate memory topic files to Knowledge DB documents (GOV-08 compliance).
Session S110: Inserts project knowledge as KB documents.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db'))
import db

MEMORY_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..',
    'Users', 'micha', '.claude', 'projects',
    'E--Claude-Playground-CLAUDE-PROJECTS-Agent-Red-Customer-Engagement', 'memory')

# Resolve absolute path
MEMORY_DIR = r"C:\Users\micha\.claude\projects\E--Claude-Playground-CLAUDE-PROJECTS-Agent-Red-Customer-Engagement\memory"

MIGRATIONS = [
    # (doc_id, title, category, filename, tags)
    ("DOC-ACTIVATION-MODEL", "Save-Activate Two-Phase Commit Model", "architecture",
     "activation-model.md", ["activation", "config-state", "draft", "widget-serving"]),
    ("DOC-ADMIN-UI", "Admin UI Patterns and Design System", "design",
     "admin-ui.md", ["ui", "css", "mantine", "design-system", "dark-mode", "components"]),
    ("DOC-APP-ARCHITECTURE", "Application Module Architecture (R1 Split)", "architecture",
     "app-module-architecture.md", ["main-py", "modules", "composition", "patch-targets"]),
    ("DOC-COMPETITIVE-ANALYSIS", "Competitive and Market Analysis Feb 2026", "business",
     "competitive-analysis-2026-02.md", ["market", "firework", "competition", "features"]),
    ("DOC-CONFIG-COMPLIANCE", "Configuration Strategy Compliance", "operations",
     "configuration-compliance.md", ["config", "env-vars", "security", "compliance"]),
    ("DOC-CONVERSATION-QUALITY", "Conversation Quality Evaluation", "architecture",
     "conversation-quality.md", ["quality", "cq", "golden-dataset", "deepeval", "critic"]),
    ("DOC-COSMOS-DB", "Cosmos DB Patterns and Reference", "architecture",
     "cosmos-db.md", ["cosmos", "database", "patch", "preferences", "pitr"]),
    ("DOC-CYCLE9", "Cycle 9 Architecture: Incidents, Alerting, MFA/TOTP", "architecture",
     "cycle9-architecture.md", ["incidents", "alerting", "mfa", "totp", "provider-admin"]),
    ("DOC-DATA-INTEGRITY", "Data Integrity Audit Procedure", "operations",
     "data-integrity-audit.md", ["audit", "pitr", "rollback", "cosmos", "deployment"]),
    ("DOC-DEPLOYMENT", "Deployment Patterns and Infrastructure", "operations",
     "deployment.md", ["deploy", "acr", "container-app", "staging", "azure", "rollback"]),
    ("DOC-EMAIL", "Email Infrastructure Architecture", "architecture",
     "email.md", ["email", "smtp", "titan", "acs", "templates"]),
    ("DOC-ONBOARDING", "Onboarding Polish: Cycle 19 Features", "architecture",
     "onboarding-polish.md", ["widget-key", "welcome-email", "trial", "background-tasks"]),
    ("DOC-OPERATIONAL-PROCEDURES", "Operational Procedures Reference", "operations",
     "operational-procedures.md", ["procedures", "initialization", "upgrade", "deployment"]),
    ("DOC-PCM-VECTORIZATION", "Persistent Customer Memory Vectorization", "architecture",
     "pcm-vectorization.md", ["pcm", "vectorization", "consent", "embedding"]),
    ("DOC-PII-SCRUBBING", "PII Scrubbing Architecture", "architecture",
     "pii-scrubbing.md", ["pii", "privacy", "scrubbing", "compliance"]),
    ("DOC-PIPELINE-QUALITY", "Pipeline Quality and Chat Response", "architecture",
     "pipeline-quality.md", ["pipeline", "rrf", "kb-conflict", "sse", "response"]),
    ("DOC-PROVIDER-ADMIN", "Provider Admin and Monitoring Architecture", "architecture",
     "provider-admin-monitoring.md", ["provider", "superadmin", "spa", "monitoring"]),
    ("DOC-PROVISIONING", "Provisioning Persistence Architecture", "architecture",
     "provisioning-persistence.md", ["provisioning", "cosmos", "tenant", "seed"]),
    ("DOC-REFACTORING", "Refactoring Plan (S31)", "architecture",
     "refactoring-plan.md", ["refactoring", "r1", "r2", "r4", "approved", "deferred"]),
    ("DOC-ROADMAP", "Build/Deploy/Test Roadmap", "business",
     "build-deploy-roadmap.md", ["roadmap", "cycles", "deployment-history", "deferred"]),
    ("DOC-SPEC-DISCIPLINE", "Specification Discipline: History and Evaluation", "governance",
     "specification-discipline.md", ["specs", "gov", "discipline", "phases", "completeness"]),
    ("DOC-SSE-WIDGET", "SSE and Widget Patterns", "architecture",
     "sse-widget.md", ["sse", "widget", "eventsource", "chat-api", "bundle"]),
    ("DOC-TEST-TENANT", "Test Tenant Infrastructure", "operations",
     "test-tenant-infrastructure.md", ["test-tenant", "staging", "seed", "credentials"]),
    ("DOC-UI-TESTING", "UI Testing Repeatable Procedure", "operations",
     "ui-testing.md", ["ui-testing", "10-dimension", "chrome-mcp", "verification"]),
]

def main():
    kb = db.KnowledgeDB()
    inserted = 0
    skipped = 0
    errors = 0

    for doc_id, title, category, filename, tags in MIGRATIONS:
        filepath = os.path.join(MEMORY_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP {doc_id}: file not found ({filename})")
            skipped += 1
            continue

        # Check if document already exists
        existing = kb.get_document(doc_id)
        if existing:
            print(f"  SKIP {doc_id}: already exists in KB")
            skipped += 1
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            kb.insert_document(
                id=doc_id,
                title=title,
                category=category,
                content=content,
                tags=tags,
                status="active",
                source_path=f"memory/{filename}",
                changed_by="Claude",
                change_reason="GOV-08 migration: topic file project knowledge to KB (S110)"
            )
            print(f"  OK   {doc_id}: {title} ({len(content)} chars)")
            inserted += 1
        except Exception as e:
            print(f"  ERR  {doc_id}: {e}")
            errors += 1

    print(f"\nDone: {inserted} inserted, {skipped} skipped, {errors} errors")
    print(f"Total documents now: {len(kb.list_documents())}")

if __name__ == "__main__":
    main()
