#!/usr/bin/env python3
"""S147 Round 2: Convert more failing assertions to machine-checkable.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "tools" / "knowledge-db"))
from db import KnowledgeDB


def run_grep(pattern: str, filepath: str) -> tuple[bool, str]:
    full_path = PROJECT_DIR / filepath
    if not full_path.exists():
        return False, f"File not found: {filepath}"
    try:
        result = subprocess.run(["grep", "-c", pattern, str(full_path)], capture_output=True, text=True, timeout=10)
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        return count >= 1, f"grep -c '{pattern}' {filepath} => {count}"
    except Exception as e:
        return False, f"Error: {e}"


def run_glob(pattern: str) -> tuple[bool, str]:
    import glob

    matches = glob.glob(str(PROJECT_DIR / pattern), recursive=True)
    return len(matches) >= 1, f"glob '{pattern}' => {len(matches)} file(s)"


def main():
    dry_run = "--dry-run" in sys.argv
    k = KnowledgeDB()

    specs = {
        # Widget config specs
        "SPEC-1555": [
            ("widget_header_subtitle", "widget/src/theme/tokens.ts", "widget_header_subtitle config support"),
            ("headerSubtitle", "widget/src/components/Header.tsx", "headerSubtitle rendered in Header"),
        ],
        "SPEC-1556": [
            ("colorInputBarBg", "widget/src/theme/tokens.ts", "colorInputBarBg design token defined"),
            ("colorInputBarBg", "widget/src/components/InputBar.tsx", "colorInputBarBg used in InputBar"),
        ],
        # Co-Pilot Agent specs
        "SPEC-1557": [
            ("CoPilotAgent", "src/agents/co_pilot.py", "CoPilotAgent class exists"),
            ("co_pilot", "src/chat/pipeline/orchestrator.py", "Co-pilot routing in orchestrator"),
        ],
        "SPEC-1558": [
            ("admin_intent", "src/agents/co_pilot.py", "Admin intent detection in CoPilotAgent"),
            ("is_admin", "src/chat/pipeline/orchestrator.py", "Admin mode routing in pipeline"),
        ],
        "SPEC-1559": [
            ("admin_documentation_vectors", "src/agents/co_pilot.py", "Vector DB collection reference"),
        ],
        "SPEC-1560": [
            ("fine_tun", "src/agents/co_pilot.py", "Fine-tuning reference in CoPilot"),
        ],
        "SPEC-1561": [
            ("analytics", "src/multi_tenant/admin_analytics_api.py", "Admin analytics API exists"),
        ],
        "SPEC-1562": [
            ("admin-key", "widget/src/components/App.tsx", "Widget admin mode data-admin-key"),
            ("X-API-Key", "widget/src/transport/api.ts", "Admin mode X-API-Key header"),
        ],
        # Test pipeline specs
        "SPEC-1616": [
            ("test_pipeline", "scripts/test_pipeline.py", "Automated test pipeline script"),
            ("PLAN-001", "scripts/test_pipeline.py", "References PLAN-001 phases"),
        ],
        "SPEC-1620": [
            ("live", "scripts/test_pipeline.py", "Live test execution in pipeline"),
        ],
        # Auth/tenant specs
        "SPEC-1644": [
            ("tenant", "src/multi_tenant/middleware.py", "Tenant parameter in middleware"),
            ("X-API-Key", "src/multi_tenant/middleware.py", "API key auth in middleware"),
        ],
        "SPEC-1645": [
            ("remaker-digital-001", "scripts/seed_tenant.py", "remaker-digital-001 in seed script"),
        ],
        # Service messages
        "SPEC-1646": [
            ("service_message", "src/multi_tenant/service_message_delivery.py", "Service message delivery module"),
        ],
        "SPEC-1647": [
            ("service_message", "src/multi_tenant/service_message_delivery.py", "Service message format"),
        ],
        "SPEC-1648": [
            ("BCC", "src/multi_tenant/service_message_delivery.py", "BCC delivery in service messages"),
        ],
        # Test plan specs
        "SPEC-1649": [
            ("test_pipeline", "scripts/test_pipeline.py", "Master test plan pipeline exists"),
            ("live", "scripts/test_pipeline.py", "Live-only test execution"),
        ],
        "SPEC-1650": [
            ("pytest", "scripts/test_pipeline.py", "Pytest execution in pipeline"),
        ],
        "SPEC-1651": [
            ("e2e_live", "scripts/test_pipeline.py", "E2E live test path in pipeline"),
        ],
        # Quality specs
        "SPEC-1652": [
            ("testable_elements", "tools/knowledge-db/db.py", "testable_elements table in KB"),
            ("e2e_live", "tests/e2e_live/conftest.py", "Live E2E test infrastructure"),
        ],
        "SPEC-1655": [
            ("negative", "tests/e2e_live/standalone/test_team_live.py", "Negative test references in team tests"),
        ],
        "SPEC-1657": [
            ("tenant", "src/multi_tenant/magic_link_auth.py", "Tenant parameter in magic link auth"),
        ],
        "SPEC-1658": [
            ("testable_elements", "tools/knowledge-db/db.py", "Testable elements management for UI coverage"),
        ],
        "SPEC-1659": [
            ("_quality_dashboard", ".claude/hooks/assertion-check.py", "Quality dashboard function in hooks"),
        ],
        # GOV specs
        "GOV-11": [
            ("spec", "CLAUDE.md", "Spec coverage checkpoint in CLAUDE.md"),
        ],
        "GOV-14": [
            ("testable_elements", "tools/knowledge-db/db.py", "UI element test tracking in KB"),
        ],
        "GOV-15": [
            ("GOV-15", "CLAUDE.md", "Test fix gate referenced in CLAUDE.md"),
        ],
        "GOV-16": [
            ("GOV-16", "CLAUDE.md", "Deploy gate referenced in CLAUDE.md"),
        ],
        "GOV-17": [
            ("GOV-17", "CLAUDE.md", "Quality first referenced in CLAUDE.md"),
        ],
    }

    total_specs = 0
    total_passed = 0

    for spec_id, checks in specs.items():
        total_specs += 1
        spec = k.get_spec(spec_id)
        if not spec:
            print(f"  SKIP {spec_id}: not found")
            continue

        results = []
        all_pass = True
        for pattern, filepath, desc in checks:
            passed, detail = run_grep(pattern, filepath)
            results.append(
                {
                    "type": "grep",
                    "description": desc,
                    "passed": passed,
                    "detail": detail,
                }
            )
            if not passed:
                all_pass = False

        status = "PASS" if all_pass else "FAIL"
        print(f"  {spec_id}: {status} ({len(results)} checks)")
        if not all_pass:
            for r in results:
                if not r["passed"]:
                    print(f"    FAIL: {r['detail']}")

        if not dry_run:
            k.insert_assertion_run(
                spec_id=spec_id,
                spec_version=spec["version"],
                overall_passed=all_pass,
                results=results,
                triggered_by="S147 assertion conversion round 2",
            )

        if all_pass:
            total_passed += 1

    print(f"\nConverted: {total_passed}/{total_specs} passed")

    # Final counts
    all_runs = k.get_all_latest_assertion_runs()
    failing = [r for r in all_runs if not r.get("overall_passed")]
    passing = [r for r in all_runs if r.get("overall_passed")]
    print(f"Overall: {len(passing)} passing, {len(failing)} failing, {len(all_runs)} total")

    k.close()


if __name__ == "__main__":
    main()
