"""
Phase 3: Map existing test functions to SPEC-NNNN specifications.

Strategy:
1. Map test files to KB sections using directory/filename patterns
2. Extract keywords from test function names (snake_case → word set)
3. Score matches against spec titles in the matching section(s)
4. Apply confidence levels: high (≥3 keyword match), medium (2), low (1)
5. Insert high+medium mappings into KB test_coverage table

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import io
import json
import os
import re
import sys
from pathlib import Path

# Windows encoding safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add knowledge-db to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB

# --- File → Section Mapping ---
# Maps test file path patterns to KB section(s) they test
FILE_SECTION_MAP = {
    # Agent modules
    "tests/agents/test_analytics_collector": ["AGENTS"],
    "tests/agents/test_base_agent": ["AGENTS"],
    "tests/agents/test_critic_supervisor": ["AGENTS"],
    "tests/agents/test_escalation_handler": ["AGENTS"],
    "tests/agents/test_intent_classifier": ["AGENTS"],
    "tests/agents/test_knowledge_retrieval": ["AGENTS"],
    "tests/agents/test_response_generator": ["AGENTS"],
    "tests/agents/test_agent_app": ["AGENTS"],
    # Chat / SSE / Widget
    "tests/chat/test_consent": ["AUTH", "WIDGET_UI"],
    "tests/chat/test_identity": ["AUTH"],
    "tests/chat/test_pipeline_escalation": ["AGENTS"],
    "tests/chat/test_session_escalation": ["AGENTS"],
    "tests/chat/test_session_pii": ["GENERAL"],
    "tests/chat/test_sse": ["WIDGET_UI", "INFRASTRUCTURE"],
    "tests/chat/test_system_prompt": ["AGENTS", "CONFIG"],
    # E2E (Playwright)
    "tests/e2e/test_configuration_page": ["ADMIN_UI", "CONFIG"],
    "tests/e2e/test_dashboard_page": ["ADMIN_UI"],
    "tests/e2e/test_knowledge_base_page": ["ADMIN_UI"],
    "tests/e2e/test_memory_privacy_page": ["ADMIN_UI"],
    "tests/e2e/test_navigation": ["ADMIN_UI"],
    "tests/e2e/test_team_page": ["ADMIN_UI"],
    "tests/e2e/test_widget_page": ["ADMIN_UI", "WIDGET_UI"],
    # Evaluation
    "tests/evaluation/": ["TESTING"],
    # Integration
    "tests/integration/test_azure": ["INFRASTRUCTURE"],
    "tests/integration/test_integration_real": ["INFRASTRUCTURE"],
    # Integrations (Shopify, Stripe, billing)
    "tests/integrations/test_http_billing": ["BILLING"],
    "tests/integrations/test_provisioning_webhooks": ["PROVISIONING"],
    "tests/integrations/test_shopify": ["SHOPIFY"],
    "tests/integrations/test_spa_provisioning": ["PROVISIONING"],
    "tests/integrations/test_stripe": ["BILLING"],
    "tests/integrations/test_usage": ["BILLING"],
    "tests/integrations/test_widget_key": ["AUTH", "PROVISIONING"],
    # Migrations
    "tests/migrations/": ["INFRASTRUCTURE"],
    # Multi-tenant (largest group — needs fine-grained mapping)
    "tests/multi_tenant/test_abuse": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_access_expiry": ["AUTH"],
    "tests/multi_tenant/test_activation": ["CONFIG"],
    "tests/multi_tenant/test_admin_analytics": ["API", "ADMIN_UI"],
    "tests/multi_tenant/test_admin_apikey": ["AUTH", "API"],
    "tests/multi_tenant/test_admin_conversation": ["API"],
    "tests/multi_tenant/test_admin_customer_profile": ["API"],
    "tests/multi_tenant/test_admin_ingestion": ["API"],
    "tests/multi_tenant/test_admin_integration": ["API"],
    "tests/multi_tenant/test_admin_knowledge": ["API"],
    "tests/multi_tenant/test_admin_mfa": ["AUTH"],
    "tests/multi_tenant/test_admin_quick_action": ["API"],
    "tests/multi_tenant/test_admin_team": ["API", "AUTH"],
    "tests/multi_tenant/test_agntcy": ["AGENTS"],
    "tests/multi_tenant/test_alert": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_api_models": ["API"],
    "tests/multi_tenant/test_apikey_reset": ["AUTH"],
    "tests/multi_tenant/test_archival": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_audit_log": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_auth_middleware": ["AUTH"],
    "tests/multi_tenant/test_chunking": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_config_api_activation": ["CONFIG", "API"],
    "tests/multi_tenant/test_config_locking": ["CONFIG"],
    "tests/multi_tenant/test_config_suggestion": ["CONFIG"],
    "tests/multi_tenant/test_config_yaml": ["CONFIG"],
    "tests/multi_tenant/test_conversation_meter": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_conversation_repository": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_conversation_vectorizer": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_cosmos_repository": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_cost": ["BILLING"],
    "tests/multi_tenant/test_critic_policy": ["AGENTS"],
    "tests/multi_tenant/test_customer_profile": ["API"],
    "tests/multi_tenant/test_data_retention": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_document_parser": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_email": ["EMAIL"],
    "tests/multi_tenant/test_fcr_metric": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_gdpr": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_idle_scanner": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_incident": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_kb_conflict": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_knowledge_repository": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_knowledge_vectorizer": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_magic_link": ["AUTH"],
    "tests/multi_tenant/test_mcp": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_mfa_totp": ["AUTH"],
    "tests/multi_tenant/test_middleware": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_mutation": ["CONFIG"],
    "tests/multi_tenant/test_nats": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_otel": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_pcm": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_pipeline_resilience": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_preferences": ["CONFIG"],
    "tests/multi_tenant/test_rbac": ["AUTH"],
    "tests/multi_tenant/test_response_explainability": ["AGENTS"],
    "tests/multi_tenant/test_retrieval_config": ["CONFIG"],
    "tests/multi_tenant/test_security_middleware": ["AUTH"],
    "tests/multi_tenant/test_semantic_cache": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_sla": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_staleness": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_standalone_test_mode": ["CONFIG", "ADMIN_UI"],
    "tests/multi_tenant/test_storefront_ingestion": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_structured_logging": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_superadmin": ["API", "INFRASTRUCTURE"],
    "tests/multi_tenant/test_support_diagnostics": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_system_prompt": ["AGENTS", "CONFIG"],
    "tests/multi_tenant/test_template_loader": ["EMAIL"],
    "tests/multi_tenant/test_tenant_config": ["CONFIG"],
    "tests/multi_tenant/test_tenant_secret": ["AUTH"],
    "tests/multi_tenant/test_trial": ["PROVISIONING"],
    "tests/multi_tenant/test_usage": ["BILLING"],
    "tests/multi_tenant/test_vectorization_scanner": ["INFRASTRUCTURE"],
    "tests/multi_tenant/test_welcome_email": ["EMAIL"],
    # Performance
    "tests/performance/": ["TESTING"],
    # Persistent memory
    "tests/persistent_memory/": ["INFRASTRUCTURE"],
    # Regression
    "tests/regression/": ["TESTING"],
    # Security
    "tests/security/test_adversarial": ["AUTH"],
    "tests/security/test_config_pipeline": ["CONFIG", "API"],
    "tests/security/test_data_integrity": ["INFRASTRUCTURE"],
    "tests/security/test_live_penetration": ["AUTH"],
    "tests/security/test_rate_limiting": ["INFRASTRUCTURE"],
    "tests/security/test_resilience": ["INFRASTRUCTURE"],
    "tests/security/test_tenant_isolation": ["INFRASTRUCTURE"],
    # Root-level tests
    "tests/test_conftest_smoke": ["TESTING"],
    "tests/test_cross_module": ["TESTING"],
    "tests/test_env_loader": ["INFRASTRUCTURE"],
    "tests/test_error_handling": ["INFRASTRUCTURE"],
    "tests/test_forgot_password": ["AUTH"],
    "tests/test_health": ["INFRASTRUCTURE"],
    "tests/test_multi_tenant_isolation": ["INFRASTRUCTURE"],
    # Unit tests
    "tests/unit/test_addon_checkout": ["BILLING"],
    "tests/unit/test_admin_conversation": ["API"],
    "tests/unit/test_admin_knowledge": ["API"],
    "tests/unit/test_alert_delivery": ["INFRASTRUCTURE"],
    "tests/unit/test_avatar_upload": ["API"],
    "tests/unit/test_chat_endpoints": ["API"],
    "tests/unit/test_chat_session": ["INFRASTRUCTURE"],
    "tests/unit/test_config_processor": ["CONFIG"],
    "tests/unit/test_customer_profile": ["API"],
    "tests/unit/test_document_parser": ["INFRASTRUCTURE"],
    "tests/unit/test_memory_dashboard": ["API"],
    "tests/unit/test_profile_linkage": ["API"],
    "tests/unit/test_security_hardening": ["AUTH"],
    "tests/unit/test_shopify_billing": ["SHOPIFY"],
    "tests/unit/test_shopify_customer": ["SHOPIFY"],
    "tests/unit/test_sse_manager": ["INFRASTRUCTURE"],
    "tests/unit/test_stripe_webhooks": ["BILLING"],
    "tests/unit/test_tenant_secret": ["AUTH"],
    "tests/unit/test_tier_upgrade": ["BILLING"],
    "tests/unit/test_trial_scanner": ["PROVISIONING"],
    "tests/unit/test_widget_otp": ["AUTH"],
    # Visual tests
    "tests/visual/": ["WIDGET_UI"],
}


def get_sections_for_file(filepath: str) -> list[str]:
    """Map a test file path to KB section(s)."""
    # Normalize path separators
    fp = filepath.replace("\\", "/")
    # Try longest prefix match first
    matches = []
    for pattern, sections in FILE_SECTION_MAP.items():
        if fp.startswith(pattern):
            matches.append((len(pattern), sections))
    if matches:
        # Take the longest (most specific) match
        matches.sort(key=lambda x: -x[0])
        return matches[0][1]
    return ["GENERAL"]


def extract_keywords(name: str) -> set[str]:
    """Extract meaningful keywords from a test function/class name.

    'test_eh_01_extracts_reason_and_urgency' → {'extracts', 'reason', 'urgency'}
    'test_tc01_brand_name_required' → {'brand', 'name', 'required'}
    """
    # Remove 'test_' prefix
    name = re.sub(r"^test_", "", name)
    # Remove numeric-only segments (test IDs like 'eh_01', 'tc05')
    parts = name.split("_")
    words = set()
    for part in parts:
        # Skip short non-word tokens, pure numbers, and test ID prefixes
        if len(part) <= 1 or part.isdigit() or re.match(r"^[a-z]{1,3}\d+$", part):
            continue
        words.add(part.lower())
    return words


# Stopwords that don't carry matching value
STOPWORDS = {
    "test",
    "when",
    "then",
    "should",
    "must",
    "shall",
    "with",
    "without",
    "returns",
    "return",
    "given",
    "that",
    "not",
    "none",
    "empty",
    "null",
    "true",
    "false",
    "valid",
    "invalid",
    "default",
    "case",
    "for",
    "from",
    "the",
    "and",
    "are",
    "has",
    "does",
    "this",
    "new",
    "get",
    "set",
}


def extract_spec_keywords(title: str) -> set[str]:
    """Extract keywords from a spec title."""
    # Lowercase, split on word boundaries
    words = re.findall(r"[a-z][a-z0-9]+", title.lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def score_match(test_kw: set[str], spec_kw: set[str]) -> tuple[int, float]:
    """Score overlap between test and spec keywords.

    Returns (overlap_count, jaccard_similarity).
    """
    if not test_kw or not spec_kw:
        return (0, 0.0)
    overlap = test_kw & spec_kw
    jaccard = len(overlap) / len(test_kw | spec_kw) if (test_kw | spec_kw) else 0.0
    return (len(overlap), jaccard)


def extract_tests_from_file(filepath: str) -> list[dict]:
    """Extract test functions with their class context from a Python test file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    tests = []
    current_class = None

    for line in content.split("\n"):
        # Track class context
        class_match = re.match(r"^class (Test\w+)", line)
        if class_match:
            current_class = class_match.group(1)
            continue

        # Check for dedent (back to module level)
        if line and not line[0].isspace() and not line.startswith("#"):
            if not line.startswith("def ") and not line.startswith("async def "):
                current_class = None

        # Extract test function
        func_match = re.match(r"^\s+(?:def|async def) (test_\w+)", line)
        if not func_match:
            func_match = re.match(r"^(?:def|async def) (test_\w+)", line)
            if func_match:
                current_class = None

        if func_match:
            func_name = func_match.group(1)
            tests.append(
                {
                    "file": filepath.replace("\\", "/"),
                    "class": current_class,
                    "function": func_name,
                    "keywords": extract_keywords(func_name),
                }
            )

    return tests


def main():
    db = KnowledgeDB()

    # Load all current specs
    specs = db.list_specs()
    print(f"Loaded {len(specs)} specs from KB")

    # Build section → specs index with keywords
    section_specs: dict[str, list[dict]] = {}
    for spec in specs:
        section = spec.get("section", "GENERAL") or "GENERAL"
        if section not in section_specs:
            section_specs[section] = []
        kw = extract_spec_keywords(spec["title"])
        desc_kw = extract_spec_keywords(spec.get("description", "") or "")
        section_specs[section].append(
            {
                "id": spec["id"],
                "title": spec["title"],
                "keywords": kw | desc_kw,
                "title_keywords": kw,
            }
        )

    print(f"Sections: {len(section_specs)}")
    for sec, slist in sorted(section_specs.items(), key=lambda x: -len(x[1])):
        print(f"  {sec}: {len(slist)} specs")
    print()

    # Extract all tests
    all_tests = []
    tests_dir = Path(__file__).parent.parent / "tests"
    for root, dirs, files in os.walk(tests_dir):
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                filepath = os.path.join(root, f)
                rel_path = os.path.relpath(filepath, tests_dir.parent).replace("\\", "/")
                file_tests = extract_tests_from_file(filepath)
                for t in file_tests:
                    t["file"] = rel_path
                    t["sections"] = get_sections_for_file(rel_path)
                all_tests.append(file_tests)

    flat_tests = [t for group in all_tests for t in group]
    print(f"Total test functions extracted: {len(flat_tests)}")

    # Build ALL specs flat index for cross-section search
    all_specs_indexed = []
    for section, slist in section_specs.items():
        for spec in slist:
            all_specs_indexed.append({**spec, "section": section})

    # Section equivalence: map themed sections to canonical ones for matching
    SECTION_ALIASES = {
        "1. Test Infrastructure": "TESTING",
        "2. Merchant Web UI": "ADMIN_UI",
        "3. Trial/Demo Environment": "PROVISIONING",
        "4. Response Streaming (SSE)": "WIDGET_UI",
        "5. Pipeline Optimization": "INFRASTRUCTURE",
        "6. API Completeness": "API",
        "7. Operational Readiness": "OPS",
        "8. Security Hardening": "AUTH",
        "10. Launch Preparation": "OPS",
        "11. RAG Infrastructure": "INFRASTRUCTURE",
        "12. KB Quality Tools": "INFRASTRUCTURE",
        "13. Admin UX Polish": "ADMIN_UI",
        "14. Widget & Quick Actions UX Fixes": "WIDGET_UI",
        "15. Standalone Admin Test Mode": "CONFIG",
        "16. Widget & Chat UI Controls": "WIDGET_UI",
        "17. Dashboard UX Improvements": "ADMIN_UI",
        "18. KB Toolbar Tooltips": "ADMIN_UI",
        "19. Analytics Page Tooltips": "ADMIN_UI",
        "20. Configuration Page UX": "ADMIN_UI",
        "21. Widget Configuration Page UX": "ADMIN_UI",
        "22. Quick Actions Page UX": "ADMIN_UI",
        "23. Team Page UX": "ADMIN_UI",
        "24. Billing & Usage Page UX": "BILLING",
        "25. Sidebar Nav Reorder": "ADMIN_UI",
        "26. Setup Wizard Redesign": "ADMIN_UI",
        "27. Post-Launch": "OPS",
        "28. S95 UI Coverage Findings": "ADMIN_UI",
        "Protected Behaviors — UI": "ADMIN_UI",
        "Protected Behaviors — Error Messages": "API",
        "Protected Behaviors — Email": "EMAIL",
        "Protected Behaviors — Build & Deploy": "OPS",
        "Membase": "GENERAL",
        "GOVERNANCE": "GENERAL",
        "CONVERSATIONS": "INFRASTRUCTURE",
        "KNOWLEDGE_BASE": "INFRASTRUCTURE",
        "TEAM": "AUTH",
        "DOCS": "GENERAL",
    }

    # Match tests to specs
    mappings = []
    unmapped_tests = 0
    for test in flat_tests:
        test_kw = test["keywords"] - STOPWORDS
        # Also extract keywords from class name if present
        class_kw = set()
        if test["class"]:
            class_kw = extract_keywords(test["class"].replace("Test", "")) - STOPWORDS

        combined_kw = test_kw | class_kw
        if len(combined_kw) < 1:
            unmapped_tests += 1
            continue

        best_match = None
        best_score = (0, 0.0)

        # Expand candidate sections to include aliased legacy sections
        candidate_sections = set(test["sections"])
        # Also add all sections whose alias matches a candidate
        for aliased_sec, canonical in SECTION_ALIASES.items():
            if canonical in candidate_sections:
                candidate_sections.add(aliased_sec)

        # Search in matching sections (includes legacy aliased sections)
        for section in candidate_sections:
            for spec in section_specs.get(section, []):
                overlap, jaccard = score_match(combined_kw, spec["keywords"])
                if overlap >= 2 and (overlap, jaccard) > best_score:
                    best_score = (overlap, jaccard)
                    best_match = spec

        # Also search GENERAL as fallback
        if not best_match:
            for spec in section_specs.get("GENERAL", []):
                overlap, jaccard = score_match(combined_kw, spec["keywords"])
                if overlap >= 2 and (overlap, jaccard) > best_score:
                    best_score = (overlap, jaccard)
                    best_match = spec

        # Last resort: cross-section search for high-keyword tests
        if not best_match and len(combined_kw) >= 3:
            for spec in all_specs_indexed:
                overlap, jaccard = score_match(combined_kw, spec["keywords"])
                if overlap >= 3 and (overlap, jaccard) > best_score:
                    best_score = (overlap, jaccard)
                    best_match = spec

        if best_match:
            overlap_count = best_score[0]
            confidence = "high" if overlap_count >= 3 else "medium"
            matched_kw = combined_kw & best_match["keywords"]
            mappings.append(
                {
                    "spec_id": best_match["id"],
                    "test_file": test["file"],
                    "test_class": test["class"],
                    "test_function": test["function"],
                    "confidence": confidence,
                    "match_reason": f"keywords({overlap_count}): {', '.join(sorted(matched_kw)[:5])}",
                }
            )
        else:
            unmapped_tests += 1

    print(f"\nMappings found: {len(mappings)}")
    print(f"Unmapped tests: {unmapped_tests}")
    print(f"Mapping rate: {len(mappings) / len(flat_tests) * 100:.1f}%")

    # Confidence breakdown
    high = sum(1 for m in mappings if m["confidence"] == "high")
    medium = sum(1 for m in mappings if m["confidence"] == "medium")
    print(f"  High confidence: {high}")
    print(f"  Medium confidence: {medium}")

    # How many unique specs are covered?
    covered_specs = {m["spec_id"] for m in mappings}
    print(f"\nUnique specs covered: {len(covered_specs)} / {len(specs)} ({len(covered_specs) / len(specs) * 100:.1f}%)")

    # Section coverage breakdown
    covered_by_section: dict[str, set[str]] = {}
    for m in mappings:
        spec = next((s for s in specs if s["id"] == m["spec_id"]), None)
        if spec:
            sec = spec.get("section", "GENERAL") or "GENERAL"
            if sec not in covered_by_section:
                covered_by_section[sec] = set()
            covered_by_section[sec].add(m["spec_id"])

    print("\nCoverage by section:")
    for sec in sorted(section_specs.keys()):
        total = len(section_specs[sec])
        covered = len(covered_by_section.get(sec, set()))
        pct = covered / total * 100 if total > 0 else 0
        bar = "#" * int(pct / 5)
        print(f"  {sec:25s} {covered:4d}/{total:4d} ({pct:5.1f}%) {bar}")

    # Save mappings to JSON for review
    output_path = Path(__file__).parent.parent / "docs" / "test-spec-mappings.json"
    output_path.write_text(json.dumps(mappings, indent=2), encoding="utf-8")
    print(f"\nMappings saved to {output_path}")

    # Insert into KB?
    if "--insert" in sys.argv:
        print("\nInserting into KB...")
        count = db.insert_test_coverage_batch(mappings, created_by="Claude (S109)")
        print(f"Inserted {count} mappings")
        summary = db.get_test_coverage_summary()
        print(f"Coverage summary: {json.dumps(summary, indent=2)}")
    else:
        print("\nDry run. Use --insert to persist to KB.")


if __name__ == "__main__":
    main()
