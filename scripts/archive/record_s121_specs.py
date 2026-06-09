#!/usr/bin/env python3
"""Record S121 specifications — Widget Configuration page baseline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
from db import KnowledgeDB

kb = KnowledgeDB()

# Get next spec ID
row = (
    kb._get_conn()
    .execute('SELECT MAX(CAST(REPLACE(id, "SPEC-", "") AS INTEGER)) FROM specifications WHERE id LIKE "SPEC-%"')
    .fetchone()
)
next_id = (row[0] or 0) + 1
print(f"Starting at SPEC-{next_id}")

# ---- SPEC: Widget Configuration Page Layout ----
kb.insert_spec(
    id=f"SPEC-{next_id}",
    title="Widget Configuration Page — Full-Width Two-Column Layout",
    status="verified",
    section="WIDGET_UI",
    type="requirement",
    description=(
        "Widget Configuration page layout baseline (production reference 2026-02-28).\n\n"
        "OUTER STRUCTURE:\n"
        '- Root wrapper: Stack gap="lg" pos="relative" — NO maxWidth constraint\n'
        "- Page body expands to fill browser window (matches all other admin pages)\n"
        "- LoadingOverlay visible while config loads\n\n"
        "PAGE HEADER:\n"
        '- Title order={2}: "Widget configuration"\n'
        '- Subtitle Text c="dimmed" size="sm": "Customize how your chat widget looks and behaves"\n'
        "- Wrapped in plain <div>\n\n"
        "TWO-COLUMN LAYOUT:\n"
        '- Group align="flex-start" wrap="nowrap" gap="lg" style={{ minHeight: 600 }}\n'
        '- Left column: Box flex="0 0 55%" maxWidth="55%"\n'
        '  - Inner Stack gap="md" with 4 Paper sections + action buttons\n'
        '- Right column: Box flex="0 0 calc(45% - 16px)" position="sticky" top=16\n'
        '  - Paper p="md" radius="md" withBorder containing Live preview\n\n'
        "PAPER SECTIONS (all identical props):\n"
        '- Paper p="lg" radius="md" withBorder\n'
        '- Each has: SectionHeader (Text size="sm" fw={700} c="dimmed" mb={4}) + HelpTooltip\n'
        '- Each has: Divider mb="md" after header\n'
        "- Sections: Installation, Appearance, Behavior, Content\n\n"
        "ACTION BUTTONS:\n"
        '- Group justify="flex-end" gap="sm"\n'
        '- Reset: Button variant="default" text "Reset to defaults"\n'
        '- Save: Button color="action" text "Save draft inputs" loading={saving}\n\n'
        "FORM CONTROLS:\n"
        '- All Switch: color="action"\n'
        '- All Slider: color="action"\n'
        '- All SegmentedControl: color="action"\n'
        "- Widget key/API URL inputs: monospace font at 12px\n"
        '- Rotate key: Button color="red" variant="outline"'
    ),
    assertions=[
        {"description": "Page outer Stack has no maxWidth — fills browser window", "type": "source_inspection"},
        {
            "description": "Two-column Group: align=flex-start wrap=nowrap gap=lg minHeight=600",
            "type": "source_inspection",
        },
        {"description": "Left column: flex 0 0 55% maxWidth 55%", "type": "source_inspection"},
        {"description": "Right column: flex 0 0 calc(45%-16px) position sticky top 16", "type": "source_inspection"},
        {"description": "Exactly 4 form Paper sections with p=lg radius=md withBorder", "type": "source_inspection"},
        {"description": "Preview Paper has p=md radius=md withBorder", "type": "source_inspection"},
        {"description": "SectionHeader: Text size=sm fw=700 c=dimmed mb=4", "type": "source_inspection"},
        {"description": "At least 4 Divider mb=md after section headers", "type": "source_inspection"},
        {"description": "Action buttons: Group justify=flex-end gap=sm", "type": "source_inspection"},
    ],
    changed_by="S121",
    change_reason="Exhaustive baseline for Widget page layout regression prevention",
)
print(f"  SPEC-{next_id}: Widget Configuration Page Layout")
next_id += 1

# ---- SPEC: Live Preview Chat UI Styling ----
kb.insert_spec(
    id=f"SPEC-{next_id}",
    title="Widget Live Preview — Chat UI Styling Specification",
    status="verified",
    section="WIDGET_UI",
    type="requirement",
    description=(
        "Chat UI styling in the Widget Configuration Live Preview panel.\n"
        "These values define the target styling for the storefront widget.\n\n"
        "PREVIEW CONTAINER:\n"
        "- minHeight: 580, borderRadius: 12, padding: 20\n"
        "- Simulated browser chrome with traffic light dots (10px circles)\n\n"
        "DARK MODE COLOR TOKENS:\n"
        "- panelBg: #292524, msgAreaBg: #1c1917\n"
        "- agentBubbleBg: #292524, agentBubbleBorder: #44403c, agentBubbleText: #f5f5f4\n"
        "- dateSepBg: #292524, dateSepText: #57534e\n"
        "- inputBg: #292524, inputText: #57534e\n"
        "- inputBarBg: #0c0a09, inputBarBorder: #44403c\n"
        "- brandingText: #57534e\n"
        "- pageBg: #1c1917, pageBorder: #44403c\n"
        "- chromeBg: #0c0a09, chromeBorder: #44403c\n\n"
        "LIGHT MODE COLOR TOKENS:\n"
        "- panelBg: #fff, msgAreaBg: #fafafa\n"
        "- agentBubbleBg: #fff, agentBubbleBorder: #e9ecef, agentBubbleText: #1f2937\n"
        "- dateSepBg: #f1f3f5, dateSepText: #6b7280\n"
        "- inputBg: #f1f3f5, inputText: #9ca3af\n"
        "- inputBarBg: #fff, inputBarBorder: #e9ecef\n"
        "- brandingText: #9ca3af\n\n"
        "HEADER:\n"
        "- padding: 16px 18px, color: #fff\n"
        "- Avatar: 36x36px circle, bg rgba(255,255,255,0.2)\n"
        '- Initials: (agentDisplayName || headerTitle || "AR").slice(0,2).toUpperCase()\n'
        '- Title: Text size="sm" fw={700} c="#fff" lh={1.3}\n'
        '- Subtitle: Text size="xs" c="rgba(255,255,255,0.8)" lh={1.3}\n'
        '- Online indicator: 7x7px circle #69db7c, text "Online" rgba(255,255,255,0.7)\n'
        "- Gradient: linear-gradient(135deg, primaryColor 0%, headerGradientEnd 100%)\n\n"
        "MESSAGE BUBBLES:\n"
        "- Agent: borderRadius 4px 16px 16px 16px, padding 10px 14px, maxWidth 78%\n"
        "- Customer: borderRadius 16px 16px 4px 16px, padding 10px 14px, maxWidth 78%\n"
        "- Customer bg: config.primaryColor, text #fff\n"
        "- In-message avatar: 28x28px circle, bg primaryColor, fontSize 10, fw 700\n\n"
        "QUICK ACTION PILLS:\n"
        "- flexDirection: column, alignItems: center, gap: 6\n"
        "- padding 5px 12px, borderRadius 16, fontSize 12\n"
        "- Dark: border #44403c bg #292524; Light: border #e5e7eb bg #f7f7f8\n\n"
        "INPUT BAR:\n"
        "- borderTop: 1px solid inputBarBorder, padding: 10px 12px\n"
        "- Input: borderRadius 20 (if borderRadius>12) else 8, padding 8px 14px, fontSize 12\n"
        "- Send button: 32x32px circle, bg primaryColor\n\n"
        "BRANDING FOOTER:\n"
        '- fontSize 10, ta="center" mt={6}\n'
        '- "Powered by" + "Agent Red" (fw 600, color primaryColor)\n\n'
        "LAUNCHER BUTTON:\n"
        "- Absolute, borderRadius 50%, bg primaryColor\n"
        "- boxShadow: 0 4px 16px rgba(0,0,0,0.2), zIndex 3\n"
        "- Chat panel zIndex 2"
    ),
    assertions=[
        {"description": "Dark panelBg=#292524 msgAreaBg=#1c1917", "type": "source_inspection"},
        {"description": "Dark agentBubbleBorder=#44403c agentBubbleText=#f5f5f4", "type": "source_inspection"},
        {"description": "Dark inputBarBg=#0c0a09 inputBarBorder=#44403c", "type": "source_inspection"},
        {"description": "Light panelBg=#fff msgAreaBg=#fafafa", "type": "source_inspection"},
        {"description": "Light agentBubbleBorder=#e9ecef inputBarBg=#fff", "type": "source_inspection"},
        {"description": "Header padding 16px 18px with 36px avatar circle", "type": "source_inspection"},
        {"description": "Agent bubble borderRadius 4px 16px 16px 16px maxWidth 78%", "type": "source_inspection"},
        {"description": "Customer bubble borderRadius 16px 16px 4px 16px", "type": "source_inspection"},
        {"description": "Input bar padding 10px 12px with 32px send button", "type": "source_inspection"},
        {"description": "Branding footer fontSize 10 Powered by Agent Red", "type": "source_inspection"},
        {"description": "Launcher boxShadow 0 4px 16px rgba(0,0,0,0.2) zIndex 3", "type": "source_inspection"},
    ],
    changed_by="S121",
    change_reason="Live Preview chat UI styling — defines target storefront widget appearance",
)
print(f"  SPEC-{next_id}: Live Preview Chat UI Styling")
next_id += 1

# ---- SPEC: Theme Token System ----
kb.insert_spec(
    id=f"SPEC-{next_id}",
    title="Admin Theme Token System — Dark/Light Mode Values",
    status="verified",
    section="WIDGET_UI",
    type="requirement",
    description=(
        "Three-layer design token system baseline.\n\n"
        "DARK MODE (default):\n"
        "- chrome: #0c0a09, page: #1c1917, surface: #292524, border: #44403c\n"
        "- text-primary: #fafaf9, text-secondary: #f5f5f4, text-muted: #a8a29e, text-tertiary: #57534e\n"
        "- action: #3B82F6, action-hover: #2563EB, danger: #D32F2F, brand: #ff3621\n\n"
        "LIGHT MODE:\n"
        "- chrome: #f5f5f5, page: #f0f0ef, surface: #ffffff, border: #e5e3e0\n"
        "- text-primary: #1c1917, text-muted: #78716c\n\n"
        "PAPER BORDER OVERRIDE:\n"
        '- [data-mantine-color-scheme="dark"] .mantine-Paper-root\n'
        "  --_paper-border-color: var(--ar-border); border-color: var(--ar-border); border-width: 1px\n\n"
        "MANTINE THEME:\n"
        "- primaryColor: action, defaultRadius: md, cursorType: pointer\n"
        "- dark[6]=#44403c, dark[7]=#292524, dark[8]=#1c1917, dark[9]=#0c0a09\n"
        "- action[7]=action[8]=#3B82F6, brand[5]=#ff3621\n"
        "- fontFamily: Inter, headings fontWeight: 600"
    ),
    assertions=[
        {
            "description": "Dark: chrome=#0c0a09 page=#1c1917 surface=#292524 border=#44403c",
            "type": "source_inspection",
        },
        {
            "description": "Paper border override: border-color var(--ar-border) border-width 1px",
            "type": "source_inspection",
        },
        {"description": "Mantine primaryColor=action defaultRadius=md", "type": "source_inspection"},
    ],
    changed_by="S121",
    change_reason="Theme token baseline for regression prevention",
)
print(f"  SPEC-{next_id}: Theme Token System")
next_id += 1

# ---- SPEC: Panel Size and Shadow Presets ----
kb.insert_spec(
    id=f"SPEC-{next_id}",
    title="Widget Panel Size and Shadow Presets",
    status="verified",
    section="WIDGET_UI",
    type="requirement",
    description=(
        "Panel dimension presets and shadow CSS values.\n\n"
        "PREVIEW-SCALE WIDTHS: compact=300, standard=350, wide=400\n"
        "REAL WIDGET WIDTHS: compact=320px, standard=380px, wide=440px\n"
        "PREVIEW-SCALE HEIGHTS: short=380, standard=460, tall=530\n\n"
        "SHADOW PRESETS (dark/light):\n"
        "- none: none\n"
        "- subtle: 0 4px 12px rgba(0,0,0,0.20/0.08)\n"
        "- standard: 0 10px 25px rgba(0,0,0,0.30/0.15), 0 4px 10px rgba(0,0,0,0.20/0.10)\n"
        "- heavy: 0 16px 40px rgba(0,0,0,0.45/0.25), 0 6px 16px rgba(0,0,0,0.30/0.15)\n\n"
        "DEFAULT CONFIG:\n"
        "- primaryColor: #ff3621, headerGradientEnd: #8B1520, gradient disabled\n"
        "- borderRadius: 16, launcherSize: 60, position: bottom-right, offsets: 20/20\n"
        "- shadowIntensity: standard, panelWidth: standard, panelHeight: standard\n"
        "- colorMode: auto, headerTitle: Support\n"
        "- headerSubtitle: We typically reply within minutes\n"
        "- inputPlaceholder: Type your message..."
    ),
    assertions=[
        {"description": "Preview widths: compact=300 standard=350 wide=400", "type": "source_inspection"},
        {"description": "Real widths: compact=320px standard=380px wide=440px", "type": "source_inspection"},
        {"description": "Preview heights: short=380 standard=460 tall=530", "type": "source_inspection"},
        {"description": "Default: primaryColor=BRAND_RED borderRadius=16 launcherSize=60", "type": "source_inspection"},
    ],
    changed_by="S121",
    change_reason="Panel size/shadow presets baseline",
)
print(f"  SPEC-{next_id}: Panel Size and Shadow Presets")

print("\nAll 4 specifications recorded.")
