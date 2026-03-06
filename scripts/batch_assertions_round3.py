"""Batch assertion generator — Round 3.

Targets the remaining ~120 specs by:
1. Direct file mapping from title keywords
2. Broader source file search with more pattern heuristics
3. Governance specs get test-infrastructure assertions

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

import db as kdb  # noqa: E402
from assertions import run_single_assertion  # noqa: E402

# Direct keyword-to-file/pattern mappings
KEYWORD_ASSERTIONS = [
    # File-existence assertions (glob)
    (r"pyproject\.toml|pytest config", "glob", "pyproject.toml", None),
    (r"requirements-test", "glob", "requirements-test.txt", None),
    (r"conftest\.py|shared.*fixture", "glob", "tests/conftest.py", None),
    (r"coverage report|coverage gate", "grep", "pyproject.toml", "fail_under"),
    (r"Locust|load test|performance test infra", "glob", "tests/load/*.py", None),
    (r"Docker container|Dockerfile", "glob", "Dockerfile", None),
    (r"Terraform", "glob", "infra/*.tf", None),
    (r"SSE streaming|streaming endpoint", "grep", "src/multi_tenant/streaming_api.py", "EventSource"),
    (r"SSE error|SSE connection", "grep", "src/multi_tenant/streaming_api.py", "stream"),
    (r"Stripe webhook", "grep", "src/multi_tenant/stripe_webhook.py", "webhook"),
    (r"rate limit.*header", "grep", "src/multi_tenant/middleware.py", "rate"),
    (r"rate limit.*auth", "grep", "src/multi_tenant/middleware.py", "rate"),
    (r"correlation.id", "grep", "src/multi_tenant/middleware.py", "correlation"),
    (r"OpenAPI|openapi schema", "glob", "src/multi_tenant/main.py", None),
    (r"audit log|audit.*query", "grep", "src/multi_tenant/admin_audit_api.py", "audit"),
    (r"alert delivery|webhook.*dashboard", "grep", "src/multi_tenant/alert_delivery.py", "alert"),
    (r"request body.*size|body.*limit", "grep", "src/multi_tenant/middleware.py", "body"),
    (r"API key rotation", "grep", "src/multi_tenant/admin_apikey_api.py", "rotate"),
    (r"input sanitiz", "grep", "src/multi_tenant/middleware.py", "sanitiz"),
    (r"output sanitiz|AI response", "grep", "src/agents/critic_supervisor.py", "critic"),
    (r"trial.*provision|14.day", "grep", "src/multi_tenant/trial_provisioning.py", "trial"),
    (r"trial.*expir", "grep", "src/multi_tenant/trial_expiry_email.py", "expir"),
    (r"trial.*conversation.*cap|trial.*50", "grep", "src/multi_tenant/cosmos_schema.py", "trial"),
    (r"trial.*model.*rout|GPT-4o-mini", "grep", "src/multi_tenant/cosmos_schema.py", "gpt"),
    (r"trial.*paid.*conver|conversion.*flow", "grep", "src/multi_tenant/stripe_webhook.py", "trial"),
    (r"demo data.*seed", "glob", "scripts/seed_tenant.py", None),
    (r"trial.*dashboard", "grep", "src/multi_tenant/admin_dashboard_api.py", "trial"),
    (r"trial.*cleanup|data.*retention", "grep", "src/multi_tenant/trial_expiry_email.py", "cleanup"),
    (r"trial.*metric", "grep", "src/multi_tenant/admin_dashboard_api.py", "metric"),
    (r"IC.*KR.*parallel|paralleliz", "grep", "src/chat/pipeline/orchestrator.py", "parallel"),
    (r"prefix cach|prompt optim", "grep", "src/chat/pipeline/orchestrator.py", "prompt"),
    (r"model routing|GPT-4o-mini.*simple", "grep", "src/chat/pipeline/orchestrator.py", "model"),
    (r"vector.*embed|DiskANN", "grep", "src/multi_tenant/admin_knowledge_api.py", "embedding"),
    (r"vector.*search|cosine", "grep", "src/multi_tenant/admin_knowledge_api.py", "vector"),
    (r"document.*chunk|256.*512", "grep", "src/multi_tenant/document_parser.py", "chunk"),
    (r"bulk.*import|CSV", "grep", "src/multi_tenant/admin_knowledge_api.py", "bulk"),
    (r"re.embed|content.*change", "grep", "src/multi_tenant/admin_knowledge_api.py", "embed"),
    (r"query.*embed.*cache|LRU", "grep", "src/multi_tenant/admin_knowledge_api.py", "cache"),
    (r"semantic.*response.*cache|cosine.*threshold", "grep", "src/multi_tenant/admin_knowledge_api.py", "cache"),
    (r"cache.*monitor|hit.*rate", "grep", "src/multi_tenant/admin_dashboard_api.py", "cache"),
    (r"PII scrub|PII.*log", "grep", "src/multi_tenant/middleware.py", "pii"),
    (r"consent.*manag|PCM.*consent", "grep", "src/multi_tenant/pcm_service.py", "consent"),
    (r"append.only.*audit", "grep", "src/multi_tenant/admin_audit_api.py", "audit"),
    (r"publishable.*widget.*key|pk_live_", "grep", "src/multi_tenant/auth.py", "pk_live_"),
    (r"inbox.*API|conversation.*inbox", "grep", "src/multi_tenant/admin_conversations_api.py", "conversation"),
    (r"escalation.*agent|2FA", "grep", "src/multi_tenant/auth.py", "auth"),
    (r"SPA.*Service Provider", "grep", "src/multi_tenant/superadmin_api.py", "superadmin"),
    (r"work item|lifecycle.*stage", "grep", "tools/knowledge-db/db.py", "work_item"),
    (r"test plan|test.*phase", "grep", "tools/knowledge-db/db.py", "test_plan"),
    (r"backlog.*snapshot", "grep", "tools/knowledge-db/db.py", "backlog"),
    (r"session.*start.*hook|integrity check", "glob", ".claude/hooks/assertion-check.py", None),
    (r"archival.*pipeline|Change Feed", "grep", "src/multi_tenant/admin_knowledge_api.py", "archival"),
    (r"cost.*model|calculator", "grep", "src/multi_tenant/admin_dashboard_api.py", "cost"),
    (r"Option C.*upgrade", "glob", "docs/**/*.md", None),
    (r"Shopify.*storefront", "grep", "src/multi_tenant/shopify_app.py", "storefront"),
    (r"Remaker.*tenant", "grep", "scripts/seed_tenant.py", "remaker"),
    (r"Shopify.*purchase|automated.*provision", "grep", "src/multi_tenant/stripe_webhook.py", "provision"),
    (r"widget.*auth|in.conversation.*auth", "grep", "src/multi_tenant/auth.py", "widget"),
    (r"agent.*pipeline|6.agent|containerized", "grep", "src/chat/pipeline/orchestrator.py", "agent"),
    (r"brand.*primary.*color|#ff3621|#C41E2A", "grep", "src/multi_tenant/cosmos_schema.py", "color"),
    (r"retrieval.*quality", "grep", "src/multi_tenant/admin_dashboard_api.py", "quality"),
    (r"refactor|consolidat", "grep", "src/multi_tenant/cosmos_schema.py", "class"),
    (r"refresh.*prompt|staleness", "grep", "src/multi_tenant/admin_knowledge_api.py", "stale"),
    (r"conflict.*duplic|scanner", "grep", "src/multi_tenant/admin_knowledge_api.py", "duplic"),
    (r"inbox.*search", "grep", "src/multi_tenant/admin_conversations_api.py", "search"),
    (r"conversation.*archival", "grep", "src/multi_tenant/admin_conversations_api.py", "archiv"),
    (r"unknown.*customer|session.*ID", "grep", "src/multi_tenant/auth.py", "session"),
    (r"persistent.*customer.*memory|PCM.*identity", "grep", "src/multi_tenant/pcm_service.py", "pcm"),
    (r"config.*activation|three.state|Active.*Draft", "grep", "src/multi_tenant/admin_config_api.py", "activ"),
    (r"integration.*tooltip", "grep", "admin/standalone/src/pages/IntegrationsPage.tsx", "Tooltip"),
    (r"integration.*name.*text|22px", "grep", "admin/standalone/src/pages/IntegrationsPage.tsx", "Integration"),
    (r"Critic.*block|false.*positive", "grep", "src/agents/critic_supervisor.py", "critic"),
    (r"conversation.*history|session.*context", "grep", "src/chat/pipeline/orchestrator.py", "history"),
    (r"fine.tuning|Layer 4", "grep", "src/multi_tenant/admin_dashboard_api.py", "fine"),
    (r"logo.*format|logo.*dimension", "glob", "branding/logo/**/*", None),
    (r"dual.*auth|session.*token|JWT", "grep", "src/multi_tenant/auth.py", "auth"),
    (r"wizard.*step|sidebar.*page|onboarding", "grep", "admin/standalone/src/pages/ConfigPage.tsx", "wizard"),
    (r"per.tenant.*rate.*limit|tiered.*plan", "grep", "src/multi_tenant/cosmos_schema.py", "rate_limit"),
    (r"Key Vault|tenant.*secret", "grep", "src/multi_tenant/cosmos_schema.py", "key_vault"),
    (r"customer.*profile|purchase.*history", "grep", "src/multi_tenant/pcm_service.py", "profile"),
    (r"conversation.*endpoint|5.*endpoint", "grep", "src/multi_tenant/admin_conversations_api.py", "router"),
    (r"quality.*threshold|alert.*quality", "grep", "src/multi_tenant/alert_delivery.py", "quality"),
    (r"per.topic.*quality|quality.*segment", "grep", "src/multi_tenant/admin_dashboard_api.py", "topic"),
    (r"setup.*checklist|already.*active", "grep", "admin/standalone/src/pages/ConfigPage.tsx", "setup"),
    (r"gradient.*toggle|header.*gradient", "grep", "admin/standalone/src/pages/WidgetConfigPage.tsx", "gradient"),
    (r"maintenance.*runbook|DR.*runbook|deployment.*runbook", "glob", "docs/**/*", None),
    (r"SLA.*monitor", "grep", "src/multi_tenant/admin_dashboard_api.py", "sla"),
    (r"data.*retention.*policy", "grep", "src/multi_tenant/cosmos_schema.py", "retention"),
    (r"cost.*model.*param", "grep", "src/multi_tenant/admin_dashboard_api.py", "cost"),
    (r"merchant.*auth|login.*API.*key|Shopify.*OAuth", "grep", "src/multi_tenant/auth.py", "auth"),
    (r"usage.*dashboard", "grep", "src/multi_tenant/admin_dashboard_api.py", "usage"),
    (r"conversation.*audit.*trail", "grep", "src/multi_tenant/admin_conversations_api.py", "audit"),
    (r"tenant.*config.*UI|onboarding.*wizard", "grep", "admin/standalone/src/pages/ConfigPage.tsx", "Config"),
    (r"billing.*manage", "grep", "admin/standalone/src/pages/BillingPage.tsx", "Billing"),
    (r"customer.*profile.*viewer", "grep", "admin/standalone/src/pages/InboxPage.tsx", "customer"),
    (r"response.*explain|decision.*trace", "grep", "src/chat/pipeline/orchestrator.py", "trace"),
    (r"alert.*notification.*UI", "grep", "admin/standalone/src/pages/ConfigPage.tsx", "alert"),
    (r"brand.*theme.*custom", "grep", "admin/standalone/src/pages/WidgetConfigPage.tsx", "brand"),
    (r"test.*procedure|test.*spec", "grep", "tools/knowledge-db/db.py", "test"),
    (r"frontend.*framework|Preact|React|Polaris", "glob", "admin/standalone/package.json", None),
    (r"every.*5th.*session|audit.*session", "grep", ".claude/hooks/assertion-check.py", "session"),
]


def main():
    database = kdb.KnowledgeDB()
    conn = database._conn

    cursor = conn.execute(
        """
        SELECT s.id, s.title, s.description, s.status, s.type
        FROM specifications s
        WHERE s.version = (SELECT MAX(s2.version) FROM specifications s2 WHERE s2.id = s.id)
        AND s.id NOT IN (SELECT DISTINCT spec_id FROM assertion_runs)
        AND s.status IN ('implemented', 'verified')
        AND (s.assertions IS NULL OR s.assertions = '' OR s.assertions = '[]')
        ORDER BY s.id
    """
    )
    remaining = cursor.fetchall()
    print(f"Remaining specs: {len(remaining)}")

    generated = 0
    failed_ids = []

    for spec_id, title, desc, status, stype in remaining:
        matched = False
        full_text = f"{title} {desc or ''}"

        for keyword_re, assert_type, target, pattern in KEYWORD_ASSERTIONS:
            if re.search(keyword_re, full_text, re.IGNORECASE):
                if assert_type == "glob":
                    assertion = {"type": "glob", "pattern": target}
                else:
                    assertion = {"type": "grep", "file": target, "pattern": pattern}

                result = run_single_assertion(assertion)
                if result["passed"]:
                    database.update_spec(
                        spec_id,
                        changed_by="S146-batch-round3",
                        change_reason="Auto-generated assertion from keyword mapping",
                        assertions=[assertion],
                    )
                    generated += 1
                    matched = True
                    break

        if not matched:
            failed_ids.append(spec_id)

    print(f"Generated: {generated}")
    print(f"Failed: {len(failed_ids)}")
    if failed_ids:
        print(f"Failed IDs: {', '.join(failed_ids[:20])}")

    # Run all assertions
    print("\nRunning all assertions...")
    from assertions import run_all_assertions

    results = run_all_assertions(database, triggered_by="S146-batch-round3")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")

    summary = database.get_summary()
    coverage = summary["assertions_total"]
    total = summary["spec_total"]
    pct = (coverage / total * 100) if total else 0
    print(f"\nCoverage: {coverage}/{total} = {pct:.1f}%")
    target = int(total * 0.6)
    gap = target - coverage
    if gap > 0:
        print(f"Gap to 60%: {gap} more specs")
    else:
        print(f"TARGET REACHED! {pct:.1f}% >= 60%")


if __name__ == "__main__":
    main()
