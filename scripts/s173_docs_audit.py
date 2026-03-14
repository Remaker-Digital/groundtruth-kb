"""S173 — Documentation audit KB artifacts.

Creates DOC-150 (audit report), SPEC-1725..1739 (15 specs), WI-1245..1259 (15 WIs).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

kdb = KnowledgeDB()
BY = "claude-s173"
REASON = "Documentation site audit — agentredcx.com"

# DOC-150
kdb.insert_document(
    id="DOC-150",
    title="Documentation Site Audit - agentredcx.com (S173)",
    category="audit_report",
    status="active",
    changed_by=BY,
    change_reason=REASON,
    content="Full audit of 33 markdown files + 60+ tooltips. 3 CRITICAL, 9 HIGH, 5 MEDIUM, 2 LOW doc issues + 5 tooltip issues. See SPEC-1725..1739 and WI-1245..1259.",
    tags=["documentation", "audit", "s173"]
)
print("DOC-150 created")

specs = [
    ("SPEC-1725", "DOC: Fix rate limit values in overview.md - all tiers 500 RPM",
     "overview.md line 97 shows stale per-tier rate limits (Starter 10/min, Professional 50/min, Enterprise 200/min). Since S137, all tiers use uniform 500 RPM.",
     [{"type": "grep", "file": "docs-site/docs/getting-started/overview.md", "pattern": "500"}]),

    ("SPEC-1726", "DOC: Fix auth header format in setup.md - X-API-Key not Bearer",
     "setup.md lines 73-81 show Authorization: Bearer but actual auth uses X-API-Key header for tenant keys and X-Widget-Key for widget keys.",
     [{"type": "grep", "file": "docs-site/docs/getting-started/setup.md", "pattern": "X-API-Key"}]),

    ("SPEC-1727", "DOC: Update changelog through v1.82.1",
     "Changelog last entry is v1.76.0. Production is at v1.82.1. Add entries for v1.77.0 through v1.82.1.",
     [{"type": "grep", "file": "docs-site/docs/changelog.md", "pattern": "v1.82"}]),

    ("SPEC-1728", "DOC: Fix welcome email description in setup.md",
     "setup.md line 61 says Welcome email with API key. S170 removed key blocks. Email now directs to admin dashboard.",
     [{"type": "grep", "file": "docs-site/docs/getting-started/setup.md", "pattern": "dashboard"}]),

    ("SPEC-1729", "DOC: Replace click Save with auto-save in save-and-activate.md",
     "save-and-activate.md references click Save throughout. S168 replaced Save buttons with auto-save on focusout.",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/save-and-activate.md", "pattern": "auto-save"}]),

    ("SPEC-1730", "DOC: Add widget_launcher_color to widget-appearance.md",
     "widget-appearance.md does not document the dedicated widget_launcher_color field added in S160.",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/widget-appearance.md", "pattern": "launcher_color"}]),

    ("SPEC-1731", "DOC: Fix analytics chart name - Daily usage not Conversation Volume",
     "analytics.md says Conversation Volume Chart. Actual is Daily usage with dual-series (total + billable).",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/analytics.md", "pattern": "Daily usage"}]),

    ("SPEC-1732", "DOC: Update team-management.md role access table",
     "Role access table shows Billing (should be Account and billing) and Agent configuration (now Agent identity).",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/team-management.md", "pattern": "Account"}]),

    ("SPEC-1733", "DOC: Update business-policies.md - policies moved to KB page",
     "Policies described on Configuration page. S168 moved to Knowledge Base page as Policy overrides.",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/business-policies.md", "pattern": "Knowledge Base"}]),

    ("SPEC-1734", "DOC: Update brand-and-tone.md - merged into Agent identity",
     "Describes standalone Brand and tone section. S168 merged into Agent identity section.",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/brand-and-tone.md", "pattern": "Agent identity"}]),

    ("SPEC-1735", "DOC: Add config-vs-KB authority to conflict-scanner.md",
     "Missing S170 config authority feature. Config fields declared authoritative over KB articles.",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/conflict-scanner.md", "pattern": "authority"}]),

    ("SPEC-1736", "DOC: Add widget behavior features - exit-intent scroll-depth panel dimensions",
     "widget-behavior.md missing exit-intent auto-open, scroll-depth, panel width/height, widget language.",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/widget-behavior.md", "pattern": "exit-intent"}]),

    ("SPEC-1737", "DOC: Fix fields.yaml doc_link domain - docs.agentred.ai to agentredcx.com",
     "All 30+ doc_link values use docs.agentred.ai. Actual site is agentredcx.com. Bulk replace.",
     [{"type": "grep", "file": "src/multi_tenant/schema/fields.yaml", "pattern": "agentredcx.com"}]),

    ("SPEC-1738", "DOC: Fix tier-upgrades.md rate limit claim",
     "Says Rate limits increase to match your new tier. All tiers have same 500 RPM since S137.",
     [{"type": "grep", "file": "docs-site/docs/billing/tier-upgrades.md", "pattern": "500"}]),

    ("SPEC-1739", "DOC: Update custom-instructions.md for Agent identity merge",
     "Describes standalone page. S168 merged into Agent identity section on Configuration page.",
     [{"type": "grep", "file": "docs-site/docs/admin-guide/custom-instructions.md", "pattern": "Agent identity"}]),
]

for sid, title, desc, assertions in specs:
    kdb.insert_spec(
        id=sid,
        title=title,
        status="specified",
        changed_by=BY,
        change_reason=REASON,
        description=desc,
        priority="high" if int(sid.split("-")[1]) <= 1728 else "medium",
        type="documentation",
        tags=["documentation", "s173-audit"],
        assertions=assertions
    )
    print(f"{sid} created")

wis = [
    ("WI-1245", "SPEC-1725", "Fix rate limit values in overview.md", "high"),
    ("WI-1246", "SPEC-1726", "Fix auth header format in setup.md", "high"),
    ("WI-1247", "SPEC-1727", "Update changelog through v1.82.1", "high"),
    ("WI-1248", "SPEC-1728", "Fix welcome email description in setup.md", "high"),
    ("WI-1249", "SPEC-1729", "Replace Save refs with auto-save in save-and-activate.md", "medium"),
    ("WI-1250", "SPEC-1730", "Add widget_launcher_color to widget-appearance.md", "medium"),
    ("WI-1251", "SPEC-1731", "Fix analytics chart name in analytics.md", "medium"),
    ("WI-1252", "SPEC-1732", "Update role access table in team-management.md", "medium"),
    ("WI-1253", "SPEC-1733", "Update policies location in business-policies.md", "medium"),
    ("WI-1254", "SPEC-1734", "Update brand-and-tone.md for Agent identity merge", "medium"),
    ("WI-1255", "SPEC-1735", "Add config-vs-KB authority to conflict-scanner.md", "medium"),
    ("WI-1256", "SPEC-1736", "Add widget behavior features documentation", "medium"),
    ("WI-1257", "SPEC-1737", "Fix fields.yaml doc_link domain to agentredcx.com", "medium"),
    ("WI-1258", "SPEC-1738", "Fix tier-upgrades.md rate limit claim", "low"),
    ("WI-1259", "SPEC-1739", "Update custom-instructions.md for Agent identity merge", "low"),
]

for wid, spec_ref, title, priority in wis:
    kdb.insert_work_item(
        id=wid,
        title=title,
        origin="defect",
        component="documentation",
        resolution_status="open",
        changed_by=BY,
        change_reason=REASON,
        description=f"Remediate documentation issue per {spec_ref}. See DOC-150.",
        source_spec_id=spec_ref,
        priority=priority
    )
    print(f"{wid} created")

print(f"\nAll KB artifacts created: DOC-150 + 15 specs (SPEC-1725..1739) + 15 WIs (WI-1245..1259)")
