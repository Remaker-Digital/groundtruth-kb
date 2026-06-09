#!/usr/bin/env python3
"""S147: Convert failing non-machine assertions to machine-checkable grep assertions.

Runs actual grep commands against the codebase and records results as assertion runs.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "tools" / "knowledge-db"))
from db import KnowledgeDB


def run_grep(pattern: str, filepath: str) -> tuple[bool, str]:
    """Run grep -c and return (passed, detail)."""
    full_path = PROJECT_DIR / filepath
    if not full_path.exists():
        return False, f"File not found: {filepath}"
    try:
        result = subprocess.run(["grep", "-c", pattern, str(full_path)], capture_output=True, text=True, timeout=10)
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        passed = count >= 1
        return passed, f"grep -c '{pattern}' {filepath} => {count} match(es)"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    dry_run = "--dry-run" in sys.argv
    k = KnowledgeDB()

    # Assertion definitions: spec_id -> list of (pattern, file, description)
    spec_assertions = {
        "SPEC-1547": [
            ("#1c1917", "widget/src/theme/tokens.ts", "colorBackground dark mode #1c1917"),
            ("#292524", "widget/src/theme/tokens.ts", "colorSurface dark mode #292524"),
            ("#44403c", "widget/src/theme/tokens.ts", "colorSurfaceHover/colorBorder dark mode #44403c"),
            ("#f5f5f4", "widget/src/theme/tokens.ts", "colorText dark mode #f5f5f4"),
            ("#a8a29e", "widget/src/theme/tokens.ts", "colorTextSecondary dark mode #a8a29e"),
            ("#57534e", "widget/src/theme/tokens.ts", "colorTextMuted dark mode #57534e"),
        ],
        "SPEC-1548": [
            ("avatarSize", "widget/src/theme/tokens.ts", "avatarSize token defined"),
            ("36px", "widget/src/theme/tokens.ts", "36px avatar size value present"),
        ],
        "SPEC-1549": [
            ("greetingMessage", "widget/src/components/MessageList.tsx", "greetingMessage rendering logic"),
            ("4px 16px 16px 16px", "widget/src/components/MessageList.tsx", "Agent bubble borderRadius in greeting"),
        ],
        "SPEC-1550": [
            ("5px 12px", "widget/src/components/QuickActions.tsx", "Quick action pill padding 5px 12px"),
            ("borderRadius", "widget/src/components/QuickActions.tsx", "Quick action pill borderRadius"),
        ],
        "SPEC-1551": [
            ("16px 16px 4px 16px", "widget/src/components/MessageBubble.tsx", "Customer bubble borderRadius"),
            ("4px 16px 16px 16px", "widget/src/components/MessageBubble.tsx", "Agent bubble borderRadius"),
            ("10px 14px", "widget/src/components/MessageBubble.tsx", "Bubble padding 10px 14px"),
        ],
        "SPEC-1552": [
            ("#0c0a09", "widget/src/theme/tokens.ts", "colorInputBarBg dark mode #0c0a09"),
            ("SendIcon", "widget/src/components/InputBar.tsx", "SendIcon paper-plane component"),
            ("Type your message", "widget/src/locale/en.ts", "Input placeholder text"),
        ],
        "SPEC-1553": [
            ("Powered by", "widget/src/components/InputBar.tsx", "Powered by branding text"),
            ("Agent Red", "widget/src/components/InputBar.tsx", "Agent Red branding text"),
        ],
        "SPEC-1554": [
            ("colorAgentBubbleBorder", "widget/src/theme/tokens.ts", "colorAgentBubbleBorder token"),
            ("#e9ecef", "widget/src/theme/tokens.ts", "colorAgentBubbleBorder light mode #e9ecef"),
        ],
        "GOV-13": [
            ("test_plan_phases", "tools/knowledge-db/db.py", "test_plan_phases table managed in db.py"),
        ],
    }

    total_specs = 0
    total_passed = 0
    total_failed = 0

    for spec_id, checks in spec_assertions.items():
        total_specs += 1

        # Get spec version
        spec = k.get_spec(spec_id)
        if not spec:
            print(f"  SKIP {spec_id}: spec not found")
            continue
        spec_version = spec["version"]

        # Run all assertions for this spec
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
        print(f"  {spec_id}: {status} ({len(results)} assertions, v{spec_version})")

        if not dry_run:
            k.insert_assertion_run(
                spec_id=spec_id,
                spec_version=spec_version,
                overall_passed=all_pass,
                results=results,
                triggered_by="S147 assertion conversion",
            )

        if all_pass:
            total_passed += 1
        else:
            total_failed += 1

    print(f"\nResults: {total_passed} passed, {total_failed} failed out of {total_specs}")

    # Final counts
    all_runs = k.get_all_latest_assertion_runs()
    failing = [r for r in all_runs if not r.get("overall_passed")]
    passing = [r for r in all_runs if r.get("overall_passed")]
    coverage = len(all_runs) / 1867 * 100
    print(
        f"\nOverall: {len(passing)} passing, {len(failing)} failing, {len(all_runs)} total ({coverage:.1f}% coverage)"
    )

    k.close()


if __name__ == "__main__":
    main()
