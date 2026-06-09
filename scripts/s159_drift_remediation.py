#!/usr/bin/env python3
"""
S159: Specification Drift Remediation

Fixes drift findings from version-history analysis:
  Fix 1: Remap 8 mislinked tests on SPEC-0295 to correct specs
  Fix 2: Document 5 lost v1 spec topics from S121 ID reuse (create DOC record)
  Fix 3: Review 78 tests created before their spec's last title change
  Report: Spec ID reuse inventory for future prevention

Safety:
  - All changes use append-only update_test() (new version, no data loss)
  - Dry-run by default (--apply to execute)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
KB_DIR = PROJECT_ROOT / "tools" / "knowledge-db"

sys.path.insert(0, str(KB_DIR))
from db import KnowledgeDB  # noqa: E402


# ── Fix 1: SPEC-0295 test mislinks ─────────────────────────────────────────
# SPEC-0295 = "An append-only audit log shall be maintained for all tenant operations"
# 8 tests are about GDPR consent or magic link auth, not audit logging
SPEC_0295_REMAP = {
    "TEST-8118": "SPEC-0292",  # GDPR consent manager -> Consent management for PCM
    "TEST-8119": "SPEC-0292",  # consent required layers
    "TEST-8120": "SPEC-0292",  # layer 1 allowed without consent
    "TEST-8121": "SPEC-0292",  # layer 2 blocked without consent
    "TEST-0071": "SPEC-0292",  # consent audit logged -> consent management
    "TEST-8685": "SPEC-1280",  # magic link module exists -> Send magic link endpoint
    "TEST-8686": "SPEC-1280",  # magic link request endpoint
    "TEST-8687": "SPEC-1281",  # magic link rate limiting -> Rate-limit magic link
    # TEST-0854 stays on SPEC-0295 (audit log repo scope is correctly audit-related)
}


def fix_1_remap_spec0295(db: KnowledgeDB, *, apply: bool = False) -> dict:
    """Remap mislinked tests from SPEC-0295 to correct specs."""
    remapped = 0
    for test_id, new_spec_id in SPEC_0295_REMAP.items():
        remapped += 1
        if apply:
            db.update_test(
                test_id,
                changed_by="S159-drift",
                change_reason=f"Remap from SPEC-0295 (audit log) to {new_spec_id} (correct spec, drift Fix 1)",
                spec_id=new_spec_id,
            )

    print(f"  Fix 1: SPEC-0295 mislinked tests remapped: {remapped}")
    if not apply and remapped:
        print(f"         (dry-run -- use --apply to execute)")
    for tid, sid in SPEC_0295_REMAP.items():
        print(f"         {tid} -> {sid}")
    return {"remapped": remapped}


# ── Fix 2: Lost v1 spec topics ─────────────────────────────────────────────
# S121 reused 7 spec IDs by overwriting v1 content with v2.
# Analysis of each lost topic:
LOST_V1_ANALYSIS = {
    "SPEC-1549": {
        "v1_title": "Widget displays saved config on all non-configuration admin pages",
        "v2_title": "Widget greeting must display as a left-aligned chat bubble",
        "status": "SUPERSEDED",
        "reason": "Current widget behavior uses live preview; saved config display is the default behavior and doesn't need a separate spec",
    },
    "SPEC-1550": {
        "v1_title": "Config page layout: full-width form panel, no inline preview column",
        "v2_title": "Widget quick action pills must use horizontal inline layout with compact styling",
        "status": "CONTRADICTED",
        "reason": "SPEC-1327 restored the two-column layout (55/45 form/preview). The full-width no-preview layout was intentionally reversed.",
    },
    "SPEC-1551": {
        "v1_title": "Widget Configuration Page - Full-Width Two-Column Layout",
        "v2_title": "Widget message bubbles must match WidgetPreview mockup border-radius, padding, and sizing",
        "status": "SUPERSEDED",
        "reason": "Baseline snapshot from S121. Current layout covered by SPEC-1327 and VR-* visual regression specs.",
    },
    "SPEC-1553": {
        "v1_title": "Admin Theme Token System - Dark/Light Mode Values",
        "v2_title": "Widget branding footer must show 'Agent Red' in bold primaryColor",
        "status": "SUPERSEDED",
        "reason": "Theme token values are implementation details captured in agentRedTheme.ts. VR-* specs cover visual regression of theme appearance.",
    },
    "SPEC-1554": {
        "v1_title": "Widget Panel Size and Shadow Presets",
        "v2_title": "Widget design tokens must include colorAgentBubbleBorder for agent message bubble outline",
        "status": "SUPERSEDED",
        "reason": "Panel dimensions are implementation details in tokens.ts. No business requirement mandates specific pixel values.",
    },
    "SPEC-1567": {
        "v1_title": "Peak Concurrency Factor for Scalability Testing",
        "v2_title": "Shopify app configuration (shopify.app.toml) must match active Dev Dashboard version",
        "status": "PARTIALLY_LOST",
        "reason": "15% concurrency factor is testing methodology. DOC-144/145 cover load test results. The specific factor could be re-documented if needed.",
    },
    "SPEC-1552": {
        "v1_title": "Widget Live Preview - Chat UI Styling Specification",
        "v2_title": "Widget input bar must match WidgetPreview mockup styling",
        "status": "SUPERSEDED",
        "reason": "Live preview styling covered by multiple VR-widget-s0-preview-* specs and SPEC-1327.",
    },
}


def fix_2_document_lost_specs(db: KnowledgeDB, *, apply: bool = False) -> dict:
    """Document the 7 lost v1 spec topics as a KB document for audit trail."""
    print(f"  Fix 2: Lost v1 spec topics documented")
    for spec_id, info in LOST_V1_ANALYSIS.items():
        print(f"         {spec_id}: [{info['status']}] {info['v1_title'][:50]}")

    if apply:
        content = "S159 Drift Audit: S121 Spec ID Reuse Analysis\n\n"
        content += "7 spec IDs were reused in S121 by overwriting v1 content with completely different v2 content.\n"
        content += "The v1 requirements are preserved in version history but no longer tracked by any active spec.\n\n"
        for spec_id, info in LOST_V1_ANALYSIS.items():
            content += f"## {spec_id}\n"
            content += f"- v1: {info['v1_title']}\n"
            content += f"- v2 (current): {info['v2_title']}\n"
            content += f"- Status: {info['status']}\n"
            content += f"- Analysis: {info['reason']}\n\n"
        content += "## Conclusion\n"
        content += "All 7 lost v1 topics are either SUPERSEDED (covered by other specs/VR baselines), "
        content += "CONTRADICTED (intentionally reversed), or PARTIALLY_LOST (testing methodology detail). "
        content += (
            "No new specs are needed. Future sessions should create new spec IDs instead of reusing existing ones."
        )

        db.insert_document(
            id="DOC-s159-drift-audit",
            title="S159 Drift Audit: Spec ID Reuse Analysis",
            category="audit_report",
            status="final",
            changed_by="S159-drift",
            change_reason="Document 7 lost v1 spec topics from S121 spec ID reuse",
            content=content,
        )
        print(f"         Document created in KB")

    return {"topics_analyzed": len(LOST_V1_ANALYSIS)}


# ── Fix 3: Stale tests (created before spec title changed) ─────────────────
def fix_3_review_stale_tests(db: KnowledgeDB, *, apply: bool = False) -> dict:
    """Review tests created before their spec's last title change.

    Strategy:
    - For each test, compare test title keywords against CURRENT spec title
    - If overlap is < 20%, the test likely targets the OLD spec meaning
    - Only report findings; remapping requires individual judgment
    """
    conn = db._get_conn()

    # Find specs with title changes (more than 1 distinct title)
    changed_specs = conn.execute("""
        SELECT id, MIN(version) as first_ver, MAX(version) as last_ver
        FROM specifications
        GROUP BY id
        HAVING COUNT(DISTINCT title) > 1
    """).fetchall()

    stale_tests = []

    for spec_row in changed_specs:
        spec_id = spec_row["id"]

        # Get earliest and latest titles
        first = conn.execute(
            "SELECT title FROM specifications WHERE id = ? ORDER BY version LIMIT 1", (spec_id,)
        ).fetchone()
        latest = conn.execute(
            "SELECT title FROM specifications WHERE id = ? ORDER BY version DESC LIMIT 1", (spec_id,)
        ).fetchone()

        if not first or not latest:
            continue

        first_title = (first["title"] or "").lower()
        latest_title = (latest["title"] or "").lower()

        # Skip if titles are essentially the same
        first_words = set(w for w in first_title.split() if len(w) >= 3)
        latest_words = set(w for w in latest_title.split() if len(w) >= 3)
        if not first_words or not latest_words:
            continue
        overlap = len(first_words & latest_words) / max(len(first_words), len(latest_words))
        if overlap > 0.5:
            continue  # Title changed but similar meaning

        # Get tests linked to this spec
        tests = conn.execute("SELECT id, title FROM current_tests WHERE spec_id = ?", (spec_id,)).fetchall()

        for t in tests:
            test_title = (t["title"] or "").lower()
            test_words = set(w for w in test_title.split() if len(w) >= 3)
            if not test_words:
                continue

            # Check if test title matches current spec or old spec
            current_match = len(test_words & latest_words) / max(len(test_words), 1)
            old_match = len(test_words & first_words) / max(len(test_words), 1)

            if old_match > current_match and current_match < 0.2:
                stale_tests.append(
                    {
                        "test_id": t["id"],
                        "test_title": t["title"],
                        "spec_id": spec_id,
                        "old_spec_title": first["title"],
                        "current_spec_title": latest["title"],
                        "old_match": f"{old_match:.0%}",
                        "current_match": f"{current_match:.0%}",
                    }
                )

    print(f"  Fix 3: Tests likely targeting old spec meaning: {len(stale_tests)}")
    for item in stale_tests[:10]:
        print(
            f"         {item['test_id']} on {item['spec_id']}: "
            f"matches old={item['old_match']} current={item['current_match']}"
        )
        print(f"           Test: {(item['test_title'] or '')[:50]}")
        print(f"           Old:  {(item['old_spec_title'] or '')[:50]}")
        print(f"           Now:  {(item['current_spec_title'] or '')[:50]}")
    if len(stale_tests) > 10:
        print(f"         ... and {len(stale_tests) - 10} more")

    return {"stale_count": len(stale_tests), "details": stale_tests}


def main():
    parser = argparse.ArgumentParser(description="S159 Drift Remediation")
    parser.add_argument("--apply", action="store_true", help="Actually execute fixes (default is dry-run)")
    parser.add_argument("--fix", nargs="+", type=int, default=None, help="Run specific fixes only (e.g., --fix 1 2)")
    args = parser.parse_args()

    fixes = set(args.fix) if args.fix else {1, 2, 3}

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{'=' * 60}")
    print(f"  S159 Drift Remediation [{mode}]")
    print(f"  Fixes: {sorted(fixes)}")
    print(f"{'=' * 60}")

    db = KnowledgeDB()
    results = {}

    if 1 in fixes:
        results["fix_1"] = fix_1_remap_spec0295(db, apply=args.apply)
    if 2 in fixes:
        results["fix_2"] = fix_2_document_lost_specs(db, apply=args.apply)
    if 3 in fixes:
        results["fix_3"] = fix_3_review_stale_tests(db, apply=args.apply)

    print(f"\n{'=' * 60}")
    total = sum(v.get("remapped", 0) + v.get("topics_analyzed", 0) for v in results.values())
    print(f"  Total actions: {total}")
    if not args.apply:
        print(f"  Mode: DRY-RUN (re-run with --apply to execute)")
    print(f"{'=' * 60}")

    db.close()


if __name__ == "__main__":
    main()
