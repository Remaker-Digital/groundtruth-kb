#!/usr/bin/env python3
"""Record specification for making live widget visually match the WidgetPreview mockup.

This specification captures every visual difference between the reference mockup
(WidgetPreview component in Widget.tsx) and the live widget (widget/src/), with
exact values from the source code to guide implementation.

Session S121.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
import db

kdb = db.KnowledgeDB()

CHANGED_BY = "S121"
CHANGE_REASON = "Visual matching spec: align live widget with WidgetPreview mockup reference"

specs = [
    # --- DARK MODE COLOR PALETTE ---
    {
        "id": "SPEC-1547",
        "title": "Widget dark mode color palette must use warm/stone grays matching the WidgetPreview mockup",
        "assertions": [
            {"description": "colorBackground in dark mode is #1c1917 (was #1A1A1A)", "type": "requirement"},
            {"description": "colorSurface in dark mode is #292524 (was #2A2A2A)", "type": "requirement"},
            {"description": "colorSurfaceHover in dark mode is #44403c (was #333333)", "type": "requirement"},
            {"description": "colorBorder in dark mode is #44403c (was #3A3A3A)", "type": "requirement"},
            {"description": "colorText in dark mode is #f5f5f4 (was #F0F0F0)", "type": "requirement"},
            {"description": "colorTextSecondary in dark mode is #a8a29e (was #AAAAAA)", "type": "requirement"},
            {"description": "colorTextMuted in dark mode is #57534e (was #777777)", "type": "requirement"},
            {"description": "colorAgentBubble in dark mode defaults to #292524 (was #2A2A2A)", "type": "requirement"},
            {
                "description": "colorAgentBubbleText in dark mode defaults to #f5f5f4 (was #F0F0F0)",
                "type": "requirement",
            },
        ],
    },
    # --- HEADER ---
    {
        "id": "SPEC-1548",
        "title": "Widget header must match WidgetPreview mockup layout and sizing",
        "assertions": [
            {"description": "Header avatar size is 36px (was 40px)", "type": "requirement"},
            {
                "description": "Default avatar (no URL) shows first 2 uppercase chars of headerTitle, not a person icon SVG",
                "type": "requirement",
            },
            {
                "description": "Header has 3-row layout: title / subtitle / (green dot + 'Online')",
                "type": "requirement",
            },
            {
                "description": "Header subtitle is configurable via widget_header_subtitle field (default: 'We typically reply within minutes')",
                "type": "requirement",
            },
            {
                "description": "Online indicator is on its own row with green dot (6px) + 'Online' text at fontSize 10px, opacity 0.8",
                "type": "requirement",
            },
            {"description": "Title uses fontSize sm (12-14px), fontWeight 600, white color", "type": "requirement"},
            {
                "description": "Subtitle uses fontSize xs (11px), rgba(255,255,255,0.85), lineHeight 1.3",
                "type": "requirement",
            },
        ],
    },
    # --- GREETING PRESENTATION ---
    {
        "id": "SPEC-1549",
        "title": "Widget greeting must display as a left-aligned chat bubble, not a centered welcome screen",
        "assertions": [
            {
                "description": "Greeting message renders as a left-aligned agent message bubble with avatar, not centered welcome text",
                "type": "requirement",
            },
            {
                "description": "Greeting avatar is 28px (avatarSizeSm), red primary bg, 'AR' text (2 chars)",
                "type": "requirement",
            },
            {
                "description": "Greeting bubble has bg colorAgentBubble, border 1px solid colorAgentBubbleBorder, borderRadius '4px 16px 16px 16px'",
                "type": "requirement",
            },
            {"description": "Greeting bubble padding is '10px 14px', maxWidth '78%'", "type": "requirement"},
            {"description": "'Today' date separator pill is shown above the greeting bubble", "type": "requirement"},
            {
                "description": "Quick actions appear below the greeting bubble, not below centered text",
                "type": "requirement",
            },
        ],
    },
    # --- QUICK ACTION PILLS ---
    {
        "id": "SPEC-1550",
        "title": "Widget quick action pills must use horizontal inline layout with compact styling",
        "assertions": [
            {
                "description": "Quick action pills use horizontal inline layout (flex-row wrap), not vertical column",
                "type": "requirement",
            },
            {"description": "Pill borderRadius is 16px (was 9999px/full)", "type": "requirement"},
            {"description": "Pill padding is '5px 12px' (was '8px 16px')", "type": "requirement"},
            {"description": "Pill fontSize is 12px", "type": "requirement"},
            {"description": "Pill border is 1px solid colorBorder", "type": "requirement"},
            {
                "description": "Pill background is colorSurface, text color is colorAgentBubbleText",
                "type": "requirement",
            },
        ],
    },
    # --- MESSAGE BUBBLES ---
    {
        "id": "SPEC-1551",
        "title": "Widget message bubbles must match WidgetPreview mockup border-radius, padding, and sizing",
        "assertions": [
            {
                "description": "Customer bubble borderRadius is '16px 16px 4px 16px' (top-left, top-right, bottom-right flat, bottom-left)",
                "type": "requirement",
            },
            {
                "description": "Agent bubble borderRadius is '4px 16px 16px 16px' (top-left flat, top-right, bottom-right, bottom-left)",
                "type": "requirement",
            },
            {"description": "Both bubble types have padding '10px 14px' (was '8px 12px')", "type": "requirement"},
            {"description": "Both bubble types have maxWidth '78%' (was '75%')", "type": "requirement"},
            {
                "description": "Agent bubble has explicit border: 1px solid colorAgentBubbleBorder (new token needed)",
                "type": "requirement",
            },
            {
                "description": "Message text fontSize is xs (11-12px) to match mockup density (was 14px/fontSizeMd)",
                "type": "requirement",
            },
        ],
    },
    # --- INPUT BAR ---
    {
        "id": "SPEC-1552",
        "title": "Widget input bar must match WidgetPreview mockup styling",
        "assertions": [
            {
                "description": "Input field has visible background (colorSurface in dark = #292524) and borderRadius (8px or config-based)",
                "type": "requirement",
            },
            {
                "description": "Input bar background is #0c0a09 in dark mode (was colorBackground #1c1917)",
                "type": "requirement",
            },
            {"description": "Input bar top border uses colorBorder (#44403c dark)", "type": "requirement"},
            {
                "description": "Send button is always primaryColor (#ff3621) regardless of input state (was colorSurface when empty)",
                "type": "requirement",
            },
            {
                "description": "Send icon is paper-plane line-stroke SVG (line x1=22 y1=2 x2=11 y2=13 + polygon), not filled arrow",
                "type": "requirement",
            },
            {"description": "Input field padding is '8px 14px' with fontSize 12px", "type": "requirement"},
            {
                "description": "Default input placeholder is 'Type your message...' (was 'Type a message...')",
                "type": "requirement",
            },
        ],
    },
    # --- BRANDING FOOTER ---
    {
        "id": "SPEC-1553",
        "title": "Widget branding footer must show 'Agent Red' in bold primaryColor",
        "assertions": [
            {
                "description": "'Powered by' text in colorTextMuted, 'Agent Red' in fontWeight 600 + primaryColor (#ff3621)",
                "type": "requirement",
            },
            {"description": "Branding fontSize is 10px (was 11px)", "type": "requirement"},
            {"description": "Branding has marginTop 6px above input bar bottom", "type": "requirement"},
        ],
    },
    # --- NEW TOKEN: AGENT BUBBLE BORDER ---
    {
        "id": "SPEC-1554",
        "title": "Widget design tokens must include colorAgentBubbleBorder for agent message bubble outline",
        "assertions": [
            {"description": "New token colorAgentBubbleBorder added to DesignTokens interface", "type": "requirement"},
            {"description": "Dark mode default: #44403c (stone-700)", "type": "requirement"},
            {"description": "Light mode default: #e9ecef", "type": "requirement"},
            {
                "description": "Configurable via widget_agent_bubble_border_color config field (future)",
                "type": "requirement",
            },
        ],
    },
    # --- NEW CONFIG FIELD: HEADER SUBTITLE ---
    {
        "id": "SPEC-1555",
        "title": "Widget config must support widget_header_subtitle for configurable header subtitle text",
        "assertions": [
            {
                "description": "widget_header_subtitle field added to WidgetConfig interface (string | null)",
                "type": "requirement",
            },
            {"description": "Default value: 'We typically reply within minutes'", "type": "requirement"},
            {
                "description": "Rendered as second line in header below title, above online indicator",
                "type": "requirement",
            },
            {"description": "Styled: fontSize xs, rgba(255,255,255,0.85), lineHeight 1.3", "type": "requirement"},
        ],
    },
    # --- INPUT BAR DARK BG TOKEN ---
    {
        "id": "SPEC-1556",
        "title": "Widget design tokens must include colorInputBarBg for input area background",
        "assertions": [
            {"description": "New token colorInputBarBg added to DesignTokens interface", "type": "requirement"},
            {"description": "Dark mode value: #0c0a09 (stone-950, darkest admin chrome color)", "type": "requirement"},
            {"description": "Light mode value: #fff (white)", "type": "requirement"},
            {
                "description": "InputBar component uses colorInputBarBg instead of colorBackground",
                "type": "requirement",
            },
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
            section="WIDGET_UI",
            status="specified",
            assertions=spec["assertions"],
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
        )
        n = len(spec["assertions"])
        total_assertions += n
        count += 1
        print(f"  {spec['id']}: {n} assertions")

    print(f"\nRecorded {count} visual matching specs with {total_assertions} total assertions")


if __name__ == "__main__":
    main()
