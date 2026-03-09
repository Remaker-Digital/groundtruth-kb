#!/usr/bin/env python3
"""Record Visual Region specifications for all admin pages (top-left quadrant).

Captured from production v1.61.0 reference UI at 1280x702 viewport.
Region: (240,56)-(640,351) = top-left content quadrant (excludes header/navbar).
Session S121.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
import db

kdb = db.KnowledgeDB()

CHANGED_BY = "S121"
CHANGE_REASON = "Visual region spec: top-left quadrant captured from production v1.61.0"

specs = [
    # --- DASHBOARD ---
    {
        "id": "VR-dashboard-s0-topleft",
        "title": "Dashboard page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917 (rgb(28,25,23))", "type": "visual"},
            {"description": 'Tenant name "blanco-9939" in stone-400 text above page title', "type": "visual"},
            {"description": '"Dashboard" as page title in large white/near-white bold text', "type": "visual"},
            {"description": '"Overview of your customer experience performance" subtitle in stone-400', "type": "visual"},
            {"description": 'First stat card: "Total conversations" with help (?) icon, large number, "Billable: N" subtext', "type": "visual"},
            {"description": 'Second row: "Customer satisfaction" stat card visible at bottom', "type": "visual"},
            {"description": "Stat cards use Paper styling: surface bg (#292524), stone-700 border, 8px radius", "type": "visual"},
        ],
    },

    # --- INBOX ---
    {
        "id": "VR-inbox-s0-topleft",
        "title": "Inbox page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": 'Search bar: "Search conversations..." placeholder in dark input field', "type": "visual"},
            {"description": 'Filter tabs: "All (N)", "Active (N)", "Esc (N)", "Resolved (N)", "Archived"', "type": "visual"},
            {"description": "Conversation list items with colored avatar circles (pink, green, etc.)", "type": "visual"},
            {"description": "Each conversation shows: truncated ID, message count, time ago, status badge", "type": "visual"},
            {"description": 'Status badges in colored text: "timed_out" in yellow/olive', "type": "visual"},
        ],
    },

    # --- TEAM MEMBERS ---
    {
        "id": "VR-team-s0-topleft",
        "title": "Team members page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": '"Team members" as page title in large white bold text', "type": "visual"},
            {"description": '"Manage team members, assign roles, and configure es..." subtitle in stone-400', "type": "visual"},
            {"description": 'Paper card with "N team member" count header', "type": "visual"},
            {"description": 'Table headers: "TEAM MEMBER" and "ROLE" with help (?) icon', "type": "visual"},
            {"description": 'First row: "Owner" label, email, "Superadmin" role badge in muted red/pink', "type": "visual"},
            {"description": "Paper card styling: surface bg (#292524), stone-700 border, 8px radius", "type": "visual"},
        ],
    },

    # --- AGENT CONFIGURATION ---
    {
        "id": "VR-agentconfig-s0-topleft",
        "title": "Agent configuration page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": '"Agent configuration" as page title in large white bold text', "type": "visual"},
            {"description": '"Fine-tune your AI agent\'s behavior" subtitle in stone-400', "type": "visual"},
            {"description": 'Paper card with "Saved configurations" heading + help (?) icon', "type": "visual"},
            {"description": 'Table header: "Name" column', "type": "visual"},
            {"description": 'First config row: "Default" with "Active" (green) and "Default" (gray) badges', "type": "visual"},
            {"description": 'Second config row: "Default" with "Default" badge only', "type": "visual"},
        ],
    },

    # --- KNOWLEDGE BASE ---
    {
        "id": "VR-knowledgebase-s0-topleft",
        "title": "Knowledge base page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": '"Knowledge base" as page title in large white bold text', "type": "visual"},
            {"description": '"Manage articles your AI uses to answer customers" subtitle in stone-400', "type": "visual"},
            {"description": 'Search bar: "Search articles..." placeholder', "type": "visual"},
            {"description": 'Filter dropdowns (two "All" selects) + action buttons row', "type": "visual"},
            {"description": 'Stat cards row: "Total articles", "Published", "Draft", "Archived", "Needs attention" with colored numbers', "type": "visual"},
            {"description": '"Knowledge automation" section with "Beta" badge below stats', "type": "visual"},
        ],
    },

    # --- QUICK ACTIONS ---
    {
        "id": "VR-quickactions-s0-topleft",
        "title": "Quick actions page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": '"Quick actions" as page title in large white bold text', "type": "visual"},
            {"description": '"Manage contextual prompt buttons that appear in the chat widget" subtitle in stone-400', "type": "visual"},
            {"description": 'Tab bar: "Prompt library (N)" and "Page assignments" tabs', "type": "visual"},
            {"description": 'Table headers: "Icon", "Label", "Prompt template", "Status", "Actions"', "type": "visual"},
            {"description": 'First row: red ? icon, "Product question", prompt text, green "Active" badge', "type": "visual"},
        ],
    },

    # --- INTEGRATIONS ---
    {
        "id": "VR-integrations-s0-topleft",
        "title": "Integrations page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": '"Integrations" as page title in large white bold text', "type": "visual"},
            {"description": '"Connect third-party services to extend your AI agent\'s capabilities." subtitle in stone-400', "type": "visual"},
            {"description": "First integration card: Shopify logo + name + help icon", "type": "visual"},
            {"description": '"Sync product catalog and customer data from your Shopify store." description', "type": "visual"},
            {"description": '"Deactivate" and "Disconnect" buttons in red/outlined style', "type": "visual"},
            {"description": "Integration cards use Paper styling with stone-700 border", "type": "visual"},
        ],
    },

    # --- MEMORY & PRIVACY ---
    {
        "id": "VR-memoryprivacy-s0-topleft",
        "title": "Memory & privacy page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": '"Memory & privacy" as page title in large white bold text', "type": "visual"},
            {"description": '"Configure how your AI remembers customers and handles their data" subtitle in stone-400', "type": "visual"},
            {"description": 'First Paper card: "Customer context" heading + "All tiers" green badge + "Disabled" toggle (right-aligned)', "type": "visual"},
            {"description": "Description text about structured customer profiles, preferences, account state", "type": "visual"},
            {"description": 'Second Paper card: "Conversation memory" heading + "All tiers" badge + "Enabled" toggle', "type": "visual"},
            {"description": "Paper cards are full-width, stacked vertically with consistent spacing", "type": "visual"},
        ],
    },

    # --- BILLING ---
    {
        "id": "VR-billing-s0-topleft",
        "title": "Billing & usage page: top-left content quadrant (240,56)-(640,351)",
        "assertions": [
            {"description": "Page background is #1c1917", "type": "visual"},
            {"description": '"Billing & usage" as page title in large white bold text', "type": "visual"},
            {"description": '"Manage your subscription and monitor usage" subtitle in stone-400', "type": "visual"},
            {"description": 'Plan card: "Current plan" heading + help icon + "Professional" blue badge + "Active" green badge', "type": "visual"},
            {"description": 'Plan stats: "Included conversations N/mo", "Used this period N", "Remaining N"', "type": "visual"},
            {"description": 'Usage stat cards row: "Conversations used", "Pack balance", "Current overage", "Estimated overage cost"', "type": "visual"},
            {"description": "Paper cards use surface bg (#292524), stone-700 border, 8px radius", "type": "visual"},
        ],
    },

    # --- SHARED STYLE SPEC (applies to ALL pages) ---
    {
        "id": "VR-shared-style",
        "title": "Shared admin UI style: applies to all standalone admin pages",
        "assertions": [
            {"description": "Header bar: dark chrome bg (#0c0a09), bottom border 0.8px #44403c", "type": "visual"},
            {"description": "Navbar: dark chrome bg (#0c0a09), right border 0.8px #44403c, ~240px wide", "type": "visual"},
            {"description": "Main content area: page bg #1c1917 (rgb(28,25,23))", "type": "visual"},
            {"description": "Paper cards: surface bg #292524 (rgb(41,37,36)), border 0.8px #44403c, borderRadius 8px", "type": "visual"},
            {"description": "Page titles: large bold white text, followed by stone-400 subtitle", "type": "visual"},
            {"description": "Text hierarchy: white headings, stone-400 body/subtitles, stone-500 for muted text", "type": "visual"},
            {"description": "Active nav link: brand-red icon (#ff3621), lighter text, subtle background highlight", "type": "visual"},
            {"description": 'Footer: version "Agent Red Customer Experience vN.N.N" + copyright in stone-500', "type": "visual"},
            {"description": "Widget FAB launcher: red circle (#ff3621) with white chat icon, bottom-right corner", "type": "visual"},
        ],
    },
]


def main():
    count = 0
    total_assertions = 0
    for spec in specs:
        kdb.insert_spec(
            id=spec["id"],
            title=spec["title"],
            section="VISUAL_REGION",
            status="verified",
            assertions=spec["assertions"],
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
        )
        n = len(spec["assertions"])
        total_assertions += n
        count += 1
        print(f"  {spec['id']}: {n} assertions")

    print(f"\nRecorded {count} visual region specs with {total_assertions} total assertions")


if __name__ == "__main__":
    main()
