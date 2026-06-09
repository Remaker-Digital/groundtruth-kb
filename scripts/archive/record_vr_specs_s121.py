#!/usr/bin/env python3
"""Record Visual Region specifications for Widget Configuration page.

Captured from production v1.61.0 reference UI at 1280x702 viewport.
Session S121.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
import db

kdb = db.KnowledgeDB()

CHANGED_BY = "S121"
CHANGE_REASON = "Visual region spec captured from production v1.61.0 reference UI"

specs = [
    # --- HEADER BAR ---
    {
        "id": "VR-widget-s0-header-left",
        "title": "Widget page: header left region (0,0)-(240,56)",
        "assertions": [
            {"description": "Background is dark chrome color (#0c0a09 / rgb(12,10,9))", "type": "visual"},
            {"description": "Agent Red logo present: {r} icon (white text on red square)", "type": "visual"},
            {
                "description": 'Brand name "agent_red" displayed: "agent_" in white, "red" in brand color (#ff3621)',
                "type": "visual",
            },
            {"description": "Subtitle text 'Customer Experience' in stone-400 gray", "type": "visual"},
            {"description": "Bottom border: thin line (~0.8px) in stone-700 (#44403c)", "type": "visual"},
        ],
    },
    {
        "id": "VR-widget-s0-header-center",
        "title": "Widget page: header center region (240,0)-(640,56)",
        "assertions": [
            {"description": "Background is dark chrome color (#0c0a09), mostly empty space", "type": "visual"},
            {"description": "Bottom border: thin line (~0.8px) in stone-700 (#44403c)", "type": "visual"},
        ],
    },
    {
        "id": "VR-widget-s0-header-right",
        "title": "Widget page: header right region (850,0)-(1280,56)",
        "assertions": [
            {"description": "Background is dark chrome color (#0c0a09)", "type": "visual"},
            {"description": 'Storefront link: home icon + "blanco-9939" text + external-link icon', "type": "visual"},
            {"description": 'Tier badge: "Professional" with green border and green text', "type": "visual"},
            {
                "description": "Action icons row: 5 icons (docs/book, chat, comments, settings/gear, exit/logout)",
                "type": "visual",
            },
            {"description": "Bottom border: thin line in stone-700 (#44403c)", "type": "visual"},
        ],
    },
    # --- NAVBAR ---
    {
        "id": "VR-widget-s0-nav-top",
        "title": "Widget page: navbar top region (0,56)-(240,256)",
        "assertions": [
            {"description": "Background is dark chrome color (#0c0a09)", "type": "visual"},
            {"description": "Right border: thin line (~0.8px) in stone-700 (#44403c)", "type": "visual"},
            {"description": "Navigation links top-to-bottom: Dashboard, Inbox, Team members", "type": "visual"},
            {"description": "Each nav link has icon (left) + label (right) in stone-400 text", "type": "visual"},
            {"description": 'Section header "AI CONFIGURATION" with green "Active" badge', "type": "visual"},
            {
                "description": 'First AI config link: "Agent configuration" partially visible at bottom',
                "type": "visual",
            },
        ],
    },
    {
        "id": "VR-widget-s0-nav-mid",
        "title": "Widget page: navbar middle region (0,256)-(240,490)",
        "assertions": [
            {"description": "Background is dark chrome color (#0c0a09)", "type": "visual"},
            {
                "description": "Navigation links: Knowledge base, Quick actions, Widget configuration, Setup wizard",
                "type": "visual",
            },
            {
                "description": "Widget configuration link is ACTIVE: highlighted with brand-red icon, lighter text, subtle background tint",
                "type": "visual",
            },
            {
                "description": 'Three action buttons at bottom: "Deactivate" (red bg), "Discard" (dark bg, light border), "Roll back" (dark bg, light border)',
                "type": "visual",
            },
        ],
    },
    {
        "id": "VR-widget-s0-nav-bottom",
        "title": "Widget page: navbar bottom region (0,490)-(240,702)",
        "assertions": [
            {"description": "Background is dark chrome color (#0c0a09)", "type": "visual"},
            {"description": "Navigation links: Integrations, Memory & privacy, Billing", "type": "visual"},
            {"description": 'Footer text: "Agent Red Customer Experience" + version number', "type": "visual"},
            {
                "description": 'Copyright notice: "2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved"',
                "type": "visual",
            },
        ],
    },
    # --- MAIN CONTENT (form column) ---
    {
        "id": "VR-widget-s0-title",
        "title": "Widget page: page title region (240,56)-(540,200)",
        "assertions": [
            {"description": "Background is page color (#1c1917 / rgb(28,25,23))", "type": "visual"},
            {"description": 'Page title: "Widget configuration" in large white/near-white text', "type": "visual"},
            {
                "description": 'Subtitle: "Customize how your chat widget looks and behaves" in stone-400 gray',
                "type": "visual",
            },
            {
                "description": 'Installation card starts: Paper section with "Installation" heading + help (?) icon',
                "type": "visual",
            },
            {
                "description": "Paper card has surface background (#292524), border in stone-700 (#44403c), rounded corners (8px)",
                "type": "visual",
            },
        ],
    },
    {
        "id": "VR-widget-s0-install-body",
        "title": "Widget page: installation card body (240,200)-(540,400)",
        "assertions": [
            {"description": "Paper card surface background (#292524) continues", "type": "visual"},
            {
                "description": 'Field: "Widget key" label in white, value in monospace code font inside dark input',
                "type": "visual",
            },
            {
                "description": 'Field: "API URL" label in white, value in monospace showing gateway FQDN',
                "type": "visual",
            },
            {
                "description": 'Helper text: "Shopify merchants: paste this URL into the..." in stone-400',
                "type": "visual",
            },
            {"description": '"Embed code" section heading visible at bottom', "type": "visual"},
        ],
    },
    {
        "id": "VR-widget-s0-install-right",
        "title": "Widget page: installation card right side (540,200)-(830,400)",
        "assertions": [
            {
                "description": 'Widget key field continues: shows key tail + copy icon + "Rotate key" button (outlined, blue text)',
                "type": "visual",
            },
            {"description": "API URL field continues: shows FQDN tail + copy icon", "type": "visual"},
            {"description": 'Helper text continues: "...Agent Red theme block settings."', "type": "visual"},
            {"description": '"Copy snippet" link in blue text visible', "type": "visual"},
        ],
    },
    {
        "id": "VR-widget-s0-embed-code",
        "title": "Widget page: embed code region (240,400)-(540,600)",
        "assertions": [
            {
                "description": "Embed code section with instruction text about pasting before closing </body> tag",
                "type": "visual",
            },
            {
                "description": "Code block: dark background with <script> tag in monospace font showing src, data-widget-key, data-api-url attributes",
                "type": "visual",
            },
            {"description": "Code block has horizontal scrollbar at bottom", "type": "visual"},
        ],
    },
    {
        "id": "VR-widget-s0-appearance-start",
        "title": "Widget page: appearance section start (240,600)-(830,702)",
        "assertions": [
            {"description": 'New Paper card begins: "Appearance" heading with help (?) icon', "type": "visual"},
            {
                "description": 'First field row: "Header left color" and "Header right color" labels visible',
                "type": "visual",
            },
            {"description": "Paper card has surface background (#292524) with stone-700 border", "type": "visual"},
        ],
    },
    # --- PREVIEW PANEL (production only -- removed in local build) ---
    {
        "id": "VR-widget-s0-preview-header",
        "title": "Widget page: live preview panel header (830,56)-(1130,256)",
        "assertions": [
            {"description": "Page background (#1c1917) visible at top before card starts", "type": "visual"},
            {"description": 'Paper card with "Live preview" heading in white text', "type": "visual"},
            {
                "description": "Mock browser chrome: three colored dots (red/yellow/green) in top-left of preview area",
                "type": "visual",
            },
            {
                "description": "Red header bar (#ff3621 gradient) with 'Support' heading visible below mock chrome",
                "type": "visual",
            },
        ],
    },
    {
        "id": "VR-widget-s0-preview-chat",
        "title": "Widget page: live preview chat area (830,256)-(1130,456)",
        "assertions": [
            {
                "description": 'Support header continues: "We typically reply within minutes", green "Online" indicator',
                "type": "visual",
            },
            {"description": '"Today" divider text in gray', "type": "visual"},
            {
                "description": 'Agent message bubble (dark bg): "Hi there! How can I help you today?" with red AR avatar',
                "type": "visual",
            },
            {
                "description": 'Quick action chips: "Product question" and partial "Shipping info" visible',
                "type": "visual",
            },
        ],
    },
    {
        "id": "VR-widget-s0-preview-input",
        "title": "Widget page: live preview input area (830,456)-(1130,656)",
        "assertions": [
            {"description": 'Quick action chip: "Shipping info" with truck emoji visible', "type": "visual"},
            {
                "description": 'User message bubble (red/brand bg): "Hi, I have a question about m..." (truncated)',
                "type": "visual",
            },
            {
                "description": 'Agent response bubble: "Of course! I\'d be happy to help. Could you share your order number?"',
                "type": "visual",
            },
            {"description": '"Type your message..." placeholder in message input field at bottom', "type": "visual"},
        ],
    },
    {
        "id": "VR-widget-s0-preview-fab",
        "title": "Widget page: preview FAB/launcher (1130,620)-(1280,702)",
        "assertions": [
            {"description": "Large circular FAB button in brand red (#ff3621)", "type": "visual"},
            {"description": "White chat bubble icon centered in FAB", "type": "visual"},
            {
                "description": '"Powered by Agent Red" text with brand-colored "Agent Red" link below input',
                "type": "visual",
            },
        ],
    },
    # --- LAYOUT STRUCTURE (structural, not tile-based) ---
    {
        "id": "VR-widget-s0-layout",
        "title": "Widget page: two-column layout structure (production v1.61.0)",
        "assertions": [
            {
                "description": "Page uses two-column layout: left form column (~55% width) + right preview column (~45% width)",
                "type": "visual",
            },
            {
                "description": "Left column contains: Installation card, Embed code, Appearance section (scrollable)",
                "type": "visual",
            },
            {
                "description": 'Right column contains: "Live preview" Paper card with sticky positioning',
                "type": "visual",
            },
            {
                "description": "Preview panel has mock browser chrome, chat conversation mockup, message input, and FAB launcher",
                "type": "visual",
            },
            {"description": "Navbar is 240px wide on the left, fixed full-height", "type": "visual"},
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
