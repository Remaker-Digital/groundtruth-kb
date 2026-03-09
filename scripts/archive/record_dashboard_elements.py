"""Record all testable elements for the merchant admin dashboard pages.

S135: SPEC-1652/1653 — Closed-loop quality process element inventory.
Covers Dashboard.tsx (sales dashboard) and UsageDashboard.tsx (billing dashboard).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))

from db import KnowledgeDB

kb = KnowledgeDB()

CHANGED_BY = "Claude"
CHANGE_REASON = "S135: Dashboard element inventory per SPEC-1652/1653"

# Dimension shorthand
EXISTS = "exists"
VALUE = "correct_value"
STYLE = "correct_style"
ACTION = "action_works"
FRESH = "freshness"
RESP = "responsive"
FAIL = "failure_mode"
LOAD = "load_behavior"

# ──────────────────────────────────────────────
# SECTION A: Page Structure & Header
# ──────────────────────────────────────────────
ELEMENTS = [
    # EL-dashboard-001 already inserted during testing — skip
    {
        "id": "EL-dashboard-002",
        "name": "Page Subtitle",
        "element_type": "text",
        "expected_behavior": "Displays subtitle 'Overview of your customer experience performance'",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-003",
        "name": "Store Name Header",
        "element_type": "text",
        "expected_behavior": "Shows shopDomain or brand_name; hidden if both missing",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION B: Period Filter
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-004",
        "name": "Period Filter - SegmentedControl",
        "element_type": "input",
        "expected_behavior": "Shows 4 options: 7d, 14d, 30d, 90d. Default 30d. Clicking changes chart period.",
        "dims": [EXISTS, VALUE, ACTION, FRESH],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-005",
        "name": "Period Filter - 7d Option",
        "element_type": "button",
        "expected_behavior": "Clicking selects 7d period, updates chart label to 'Last 7 days'",
        "dims": [EXISTS, ACTION, FRESH],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-006",
        "name": "Period Filter - 14d Option",
        "element_type": "button",
        "expected_behavior": "Clicking selects 14d period, updates chart label to 'Last 14 days'",
        "dims": [EXISTS, ACTION, FRESH],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-007",
        "name": "Period Filter - 90d Option",
        "element_type": "button",
        "expected_behavior": "Clicking selects 90d period, updates chart label to 'Last 90 days'",
        "dims": [EXISTS, ACTION, FRESH],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION C: Setup Checklist (conditional)
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-008",
        "name": "Setup Checklist Container",
        "element_type": "alert",
        "expected_behavior": "Visible only when is_active=false. Shows 'Setup progress: N/4 complete'",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-009",
        "name": "Checklist Item - Brand Name",
        "element_type": "text",
        "expected_behavior": "Text 'Brand name configured'. Done when brand_name exists and != 'My Store'. Checkmark/dash indicator.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-010",
        "name": "Checklist Item - AI Instructions",
        "element_type": "text",
        "expected_behavior": "Text 'AI instructions or category selected'. Done when custom_instructions or brand_voice exists.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-011",
        "name": "Checklist Item - Widget Appearance",
        "element_type": "text",
        "expected_behavior": "Done when any widget customization differs from defaults (color, position, gradient, icon, bg).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-012",
        "name": "Checklist Item - System Activated",
        "element_type": "text",
        "expected_behavior": "Done when is_active=true. Checkmark/dash indicator.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION D: Test Mode Alert (conditional)
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-013",
        "name": "Test Mode Alert Container",
        "element_type": "alert",
        "expected_behavior": "Visible only when test_mode_enabled=true. Yellow variant. Title 'Test mode is active'.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-014",
        "name": "Test Mode Alert - 4 List Items",
        "element_type": "text",
        "expected_behavior": "4 items explaining test mode behavior: billing exclusion, banner, analytics, widget behavior.",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION E: Stat Cards (5 cards)
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-015",
        "name": "Stat Cards Grid",
        "element_type": "layout",
        "expected_behavior": "SimpleGrid: 1-col base, 2-col xs, 3-col md. Contains 5 stat cards.",
        "dims": [EXISTS, RESP],
        "page": "Dashboard.tsx",
    },
    # Card 1: Total Conversations
    {
        "id": "EL-dashboard-016",
        "name": "Total Conversations - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Total conversations'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1595",
    },
    {
        "id": "EL-dashboard-017",
        "name": "Total Conversations - Value",
        "element_type": "text",
        "expected_behavior": "Locale-formatted number from summary.totalConversations. Billable-only.",
        "dims": [EXISTS, VALUE, FRESH, FAIL],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1595",
    },
    {
        "id": "EL-dashboard-018",
        "name": "Total Conversations - Tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltip: 'Billable customer conversations in the selected period...'",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-019",
        "name": "Total Conversations - Loading Skeleton",
        "element_type": "skeleton",
        "expected_behavior": "Skeleton height=28 width=60% while loading",
        "dims": [EXISTS, STYLE],
        "page": "Dashboard.tsx",
    },
    # Card 2: Avg Response Time
    {
        "id": "EL-dashboard-020",
        "name": "Avg Response Time - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Avg response time'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1596",
    },
    {
        "id": "EL-dashboard-021",
        "name": "Avg Response Time - Value",
        "element_type": "text",
        "expected_behavior": "Format: 'X.Xs' (e.g. '2.3s'). Shows '--' when null.",
        "dims": [EXISTS, VALUE, FRESH, FAIL],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1596",
    },
    {
        "id": "EL-dashboard-022",
        "name": "Avg Response Time - Tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltip about response time measurement",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Dashboard.tsx",
    },
    # Card 3: Resolution Rate
    {
        "id": "EL-dashboard-023",
        "name": "Resolution Rate - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Resolution rate'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1593",
    },
    {
        "id": "EL-dashboard-024",
        "name": "Resolution Rate - Value",
        "element_type": "text",
        "expected_behavior": "Format: 'XX.X%' (e.g. '90.1%'). Computed from resolutionRate * 100.",
        "dims": [EXISTS, VALUE, FRESH, FAIL],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1593",
    },
    {
        "id": "EL-dashboard-025",
        "name": "Resolution Rate - Detail",
        "element_type": "text",
        "expected_behavior": "Text 'N resolved' where N = round(totalConversations * resolutionRate)",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-026",
        "name": "Resolution Rate - Tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltip about resolution rate",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Dashboard.tsx",
    },
    # Card 4: Customer Satisfaction
    {
        "id": "EL-dashboard-027",
        "name": "Customer Satisfaction - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Customer satisfaction'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-028",
        "name": "Customer Satisfaction - Value",
        "element_type": "text",
        "expected_behavior": "Format: 'X/5' (e.g. '4.2/5'). Shows '--' when null.",
        "dims": [EXISTS, VALUE, FRESH, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-029",
        "name": "Customer Satisfaction - Tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltip about CSAT",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Dashboard.tsx",
    },
    # Card 5: Escalation Rate
    {
        "id": "EL-dashboard-030",
        "name": "Escalation Rate - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Escalation rate'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1597",
    },
    {
        "id": "EL-dashboard-031",
        "name": "Escalation Rate - Value",
        "element_type": "text",
        "expected_behavior": "Format: 'XX.X%'. Computed from escalationRate * 100.",
        "dims": [EXISTS, VALUE, FRESH, FAIL],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1597",
    },
    {
        "id": "EL-dashboard-032",
        "name": "Escalation Rate - Detail",
        "element_type": "text",
        "expected_behavior": "Text 'N escalated' where N = escalationCount",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-033",
        "name": "Escalation Rate - Tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Help tooltip about escalation rate",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION F: Conversation Volume Chart
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-034",
        "name": "Chart Section Header",
        "element_type": "text",
        "expected_behavior": "Text 'Conversation volume'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1594",
    },
    {
        "id": "EL-dashboard-035",
        "name": "Chart Period Label",
        "element_type": "text",
        "expected_behavior": "Right-aligned: 'Last 30 days' (default). Changes with period filter.",
        "dims": [EXISTS, VALUE, FRESH],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-036",
        "name": "Chart Container",
        "element_type": "chart",
        "expected_behavior": "Recharts AreaChart, 320px height, full width",
        "dims": [EXISTS, STYLE, RESP],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-037",
        "name": "Chart X-Axis",
        "element_type": "chart_axis",
        "expected_behavior": "Date labels formatted 'M/D'. Font-size 11.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-038",
        "name": "Chart Y-Axis",
        "element_type": "chart_axis",
        "expected_behavior": "Auto-scaling numeric. Font-size 11.",
        "dims": [EXISTS, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-039",
        "name": "Chart Area Fill",
        "element_type": "chart_series",
        "expected_behavior": "Stroke #ff3621 width 2. Gradient fill. Data key 'total'.",
        "dims": [EXISTS, STYLE, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-040",
        "name": "Chart Tooltip",
        "element_type": "tooltip",
        "expected_behavior": "Shows on hover: date + conversation count. Dark/light mode adaptive.",
        "dims": [EXISTS, ACTION, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-041",
        "name": "Chart Legend",
        "element_type": "text",
        "expected_behavior": "Single item: 'Conversations' with red square. Centered below chart.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-042",
        "name": "Chart Loading Skeleton",
        "element_type": "skeleton",
        "expected_behavior": "Skeleton height=320 while loading",
        "dims": [EXISTS, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-043",
        "name": "Chart Empty State",
        "element_type": "text",
        "expected_behavior": "Text 'No volume data available' when no data and not loading",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION G: Recent Conversations
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-044",
        "name": "Recent Conversations - Section Header",
        "element_type": "text",
        "expected_behavior": "Text 'Recent conversations' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1599",
    },
    {
        "id": "EL-dashboard-045",
        "name": "Recent Conversations - Container Layout",
        "element_type": "layout",
        "expected_behavior": "2-column grid with Top Topics on md+, 1-column on mobile",
        "dims": [EXISTS, RESP],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-046",
        "name": "Conversation Item - Customer Name",
        "element_type": "text",
        "expected_behavior": "Shows customerName. Default 'Unknown Customer'. Line-clamp 1.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-047",
        "name": "Conversation Item - Status Badge",
        "element_type": "badge",
        "expected_behavior": "active=blue, idle=yellow, ended=green, escalated=red",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-048",
        "name": "Conversation Item - Message Count",
        "element_type": "text",
        "expected_behavior": "Text 'N messages'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-049",
        "name": "Conversation Item - Assignment Status",
        "element_type": "text",
        "expected_behavior": "Escalated | Assigned: {name} | Unassigned",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-050",
        "name": "Conversation Item - Last Activity Time",
        "element_type": "text",
        "expected_behavior": "Time format HH:mm. Default '--' if null.",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-051",
        "name": "Recent Conversations - Loading State",
        "element_type": "skeleton",
        "expected_behavior": "5 skeleton items, each height 60px",
        "dims": [EXISTS, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-052",
        "name": "Recent Conversations - Empty State",
        "element_type": "text",
        "expected_behavior": "Text 'No conversations yet' when empty",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION H: Top Topics
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-053",
        "name": "Top Topics - Section Header",
        "element_type": "text",
        "expected_behavior": "Text 'Top topics' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1598",
    },
    {
        "id": "EL-dashboard-054",
        "name": "Topic Item - Label",
        "element_type": "text",
        "expected_behavior": "agentDisplayLabel() transform: 'order-tracking' -> 'Order Tracking'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-055",
        "name": "Topic Item - Count",
        "element_type": "text",
        "expected_behavior": "Locale-formatted invocationCount",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-056",
        "name": "Topic Item - Progress Bar",
        "element_type": "chart",
        "expected_behavior": "Width=percentage%, color=#ff3621, opacity 0.7-1.0 based on percentage",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-057",
        "name": "Top Topics - Loading State",
        "element_type": "skeleton",
        "expected_behavior": "5 skeleton items, each height 48px",
        "dims": [EXISTS, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-058",
        "name": "Top Topics - Empty State",
        "element_type": "text",
        "expected_behavior": "Text 'No topic data available' when empty",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION I: Detailed Analytics Divider
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-059",
        "name": "Detailed Analytics Divider",
        "element_type": "divider",
        "expected_behavior": "Divider with centered label 'Detailed analytics'",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION J: Topic Breakdown Table
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-060",
        "name": "Topic Breakdown - Section Header",
        "element_type": "text",
        "expected_behavior": "Text 'Topic breakdown' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
        "spec": "SPEC-1600",
    },
    {
        "id": "EL-dashboard-061",
        "name": "Topic Breakdown - Table",
        "element_type": "table",
        "expected_behavior": "Striped table with hover highlight. 3 columns: Topic, Count, Distribution.",
        "dims": [EXISTS, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-062",
        "name": "Topic Row - Name Cell",
        "element_type": "text",
        "expected_behavior": "agentDisplayLabel() transform of intent.agent",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-063",
        "name": "Topic Row - Count Cell",
        "element_type": "text",
        "expected_behavior": "Locale-formatted invocationCount",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-064",
        "name": "Topic Row - Distribution Bar",
        "element_type": "chart",
        "expected_behavior": "Progress bar value=percentage, color=brand red, pill-shaped",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-065",
        "name": "Topic Row - Percentage Text",
        "element_type": "text",
        "expected_behavior": "Format: 'X%'. Right-aligned, width 36px.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-066",
        "name": "Topic Breakdown - Empty State",
        "element_type": "text",
        "expected_behavior": "Text 'No topic data available' when empty",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION K: Knowledge Gaps
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-067",
        "name": "Knowledge Gaps - Section Header",
        "element_type": "text",
        "expected_behavior": "Text 'Knowledge gaps' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-068",
        "name": "Knowledge Gaps - Description",
        "element_type": "text",
        "expected_behavior": "Text 'Conversations where the AI could not fully resolve the customer query'",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-069",
        "name": "Knowledge Gaps - Count Badge",
        "element_type": "badge",
        "expected_behavior": "Shows 'N gap(s)' badge. Visible only when gaps > 0. Orange variant.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-070",
        "name": "Knowledge Gaps - Table",
        "element_type": "table",
        "expected_behavior": "5 columns: Conversation, Status, Turns, Messages, Started. Striped + hover.",
        "dims": [EXISTS, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-071",
        "name": "Gap Row - Conversation ID",
        "element_type": "text",
        "expected_behavior": "conversationId, line-clamp 1, tooltip full ID on hover",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-072",
        "name": "Gap Row - Customer ID",
        "element_type": "text",
        "expected_behavior": "customerId below conversation ID. Visible only when exists.",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-073",
        "name": "Gap Row - Status Badge",
        "element_type": "badge",
        "expected_behavior": "escalated=red, ended=green, active=blue, else=gray",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-074",
        "name": "Gap Row - Turn Count",
        "element_type": "text",
        "expected_behavior": "Numeric turnCount, default 0",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-075",
        "name": "Gap Row - Message Count",
        "element_type": "text",
        "expected_behavior": "Numeric messageCount, default 0",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-076",
        "name": "Gap Row - Started Date",
        "element_type": "text",
        "expected_behavior": "Locale date format (e.g. 'Feb 24, 2026'). Default '--' if null.",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-077",
        "name": "Knowledge Gaps - Empty State",
        "element_type": "text",
        "expected_behavior": "Text 'No knowledge gaps detected' when empty",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "Dashboard.tsx",
    },
    {
        "id": "EL-dashboard-078",
        "name": "Knowledge Gaps - Loading State",
        "element_type": "text",
        "expected_behavior": "Text 'Loading knowledge gaps...' while loading",
        "dims": [EXISTS, VALUE],
        "page": "Dashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION L: Usage Dashboard — Page Structure
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-079",
        "name": "Usage Dashboard - Page Title",
        "element_type": "text",
        "expected_behavior": "Text 'Usage dashboard'",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-080",
        "name": "Usage Dashboard - Subtitle",
        "element_type": "text",
        "expected_behavior": "Format: '{tier} tier . {billingPeriod}' (e.g. 'Professional tier . February 2026')",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-081",
        "name": "Billing Period Dropdown",
        "element_type": "input",
        "expected_behavior": "Default 'Current period'. Shows current + past 5 months. Changes usagePeriod state.",
        "dims": [EXISTS, VALUE, ACTION, FRESH],
        "page": "UsageDashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION M: Usage Meter
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-082",
        "name": "Usage Summary - Section Title",
        "element_type": "text",
        "expected_behavior": "Text 'Usage summary'",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-083",
        "name": "Usage Meter - Label",
        "element_type": "text",
        "expected_behavior": "Left: 'Conversations Used' + 'X of Y included'. Right: percentage 'N%'.",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-084",
        "name": "Usage Meter - Progress Bar",
        "element_type": "chart",
        "expected_behavior": "Height 12px. Green <80%, amber 80-99%, red >=100%. Transition 0.4s.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-085",
        "name": "Usage Meter - Overage Indicator",
        "element_type": "chart",
        "expected_behavior": "Visible only when totalConversations > includedAllowance. Red opacity 0.3.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-086",
        "name": "Usage Meter - Overage Text",
        "element_type": "text",
        "expected_behavior": "Format: 'N overage conversation(s) . Estimated cost: $X.XX'. Red. Visible when overage.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION N: Usage Summary Cards (4)
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-087",
        "name": "Remaining Included Card - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Remaining included' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-088",
        "name": "Remaining Included Card - Value",
        "element_type": "text",
        "expected_behavior": "Formatted remainingIncluded count. Detail: 'of {includedAllowance}'.",
        "dims": [EXISTS, VALUE, FRESH],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-089",
        "name": "Pack Balance Card - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Pack balance' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-090",
        "name": "Pack Balance Card - Value",
        "element_type": "text",
        "expected_behavior": "Formatted packBalance. Detail: 'pre-purchased conversations'.",
        "dims": [EXISTS, VALUE, FRESH],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-091",
        "name": "Overage Card - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Overage' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-092",
        "name": "Overage Card - Value",
        "element_type": "text",
        "expected_behavior": "overageConversations count. Red when > 0. Detail shows cost or 'no overage'.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-093",
        "name": "Overage Reported Card - Label",
        "element_type": "text",
        "expected_behavior": "Text 'Overage reported'",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-094",
        "name": "Overage Reported Card - Value",
        "element_type": "text",
        "expected_behavior": "overageReported count. Detail: 'reported to billing'.",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION O: Alerts Panel
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-095",
        "name": "Alerts Panel - Container",
        "element_type": "layout",
        "expected_behavior": "Visible only when alerts exist. Flex column, gap 8px.",
        "dims": [EXISTS, FAIL],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-096",
        "name": "Alert Item",
        "element_type": "alert",
        "expected_behavior": "Amber background (#fef3c7), border #fde68a. Warning icon + text.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION P: Daily Volume Chart (Usage Dashboard)
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-097",
        "name": "Daily Volume - Section Title",
        "element_type": "text",
        "expected_behavior": "Text 'Daily volume' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-098",
        "name": "Daily Volume - Bar Chart Container",
        "element_type": "chart",
        "expected_behavior": "Custom CSS bar chart. Horizontal scroll. Min-height 160px.",
        "dims": [EXISTS, STYLE, RESP],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-099",
        "name": "Daily Volume - Total Bar",
        "element_type": "chart_series",
        "expected_behavior": "Light gray (#d0d0d0). Min height 2px. Rounded top. Hover tooltip 'Total: N'.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-100",
        "name": "Daily Volume - Billable Bar",
        "element_type": "chart_series",
        "expected_behavior": "Brand red (#ff3621). Min height 2px. Hover tooltip 'Billable: N'.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-101",
        "name": "Daily Volume - Day Labels",
        "element_type": "text",
        "expected_behavior": "Short date 'Mon DD'. Font-size 10, centered, nowrap.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-102",
        "name": "Daily Volume - Chart Legend",
        "element_type": "text",
        "expected_behavior": "Two items: gray dot 'Total', red dot 'Billable'. Font-size 12.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-103",
        "name": "Daily Volume - Empty State",
        "element_type": "text",
        "expected_behavior": "Text 'No daily volume data available.' when empty",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION Q: Conversations Table (Usage Dashboard)
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-104",
        "name": "Conversations Table - Section Header",
        "element_type": "text",
        "expected_behavior": "Text 'Conversations' with help tooltip",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-105",
        "name": "Export CSV Button",
        "element_type": "button",
        "expected_behavior": "Text 'Export CSV'. Shows 'Exporting...' during export. Triggers CSV download.",
        "dims": [EXISTS, VALUE, ACTION, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-106",
        "name": "Conversations Table - Headers",
        "element_type": "table",
        "expected_behavior": "10 columns: ID, Status, Customer, Billable, Messages, Turns, Started, Ended, Model, Critic",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-107",
        "name": "Table Row - Conversation ID Cell",
        "element_type": "text",
        "expected_behavior": "Monospace, first 12 chars + '...'. Tooltip shows full ID.",
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-108",
        "name": "Table Row - Status Cell",
        "element_type": "text",
        "expected_behavior": "Status text. Default '--'.",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-109",
        "name": "Table Row - Customer Cell",
        "element_type": "text",
        "expected_behavior": "customerId. Max-width 100px, ellipsis. Tooltip full ID. Default '--'.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-110",
        "name": "Table Row - Billable Badge",
        "element_type": "badge",
        "expected_behavior": "Yes=red bg/dark red text, No=green bg/dark green text",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-111",
        "name": "Table Row - Message Count Cell",
        "element_type": "text",
        "expected_behavior": "Numeric messageCount. Right-aligned.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-112",
        "name": "Table Row - Turn Count Cell",
        "element_type": "text",
        "expected_behavior": "Numeric turnCount. Right-aligned.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-113",
        "name": "Table Row - Started DateTime",
        "element_type": "text",
        "expected_behavior": "Format 'Mon DD, HH:mm'. Default '--'.",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-114",
        "name": "Table Row - Ended DateTime",
        "element_type": "text",
        "expected_behavior": "Same format as started. Default '--'.",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-115",
        "name": "Table Row - Model Used Cell",
        "element_type": "text",
        "expected_behavior": "modelUsed string. Default '--'. Font-size 12.",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-116",
        "name": "Table Row - Critic Badge",
        "element_type": "badge",
        "expected_behavior": "Pass=green, Fail=red, N/A=gray (when null)",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-117",
        "name": "Conversations Table - Loading State",
        "element_type": "text",
        "expected_behavior": "Text 'Loading conversations...' centered, colspan 10",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-118",
        "name": "Conversations Table - Empty State",
        "element_type": "text",
        "expected_behavior": "Text 'No conversations found for this period.' centered",
        "dims": [EXISTS, VALUE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION R: Pagination
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-119",
        "name": "Pagination - Page Info Text",
        "element_type": "text",
        "expected_behavior": "Format: 'Showing {start}-{end} of {total} conversations'",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-120",
        "name": "Pagination - Previous Button",
        "element_type": "button",
        "expected_behavior": "Disabled when offset=0. Enabled otherwise. Navigates to previous page.",
        "dims": [EXISTS, ACTION, STYLE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-121",
        "name": "Pagination - Page Counter",
        "element_type": "text",
        "expected_behavior": "Format: 'Page {current} of {total}'",
        "dims": [EXISTS, VALUE],
        "page": "UsageDashboard.tsx",
    },
    {
        "id": "EL-dashboard-122",
        "name": "Pagination - Next Button",
        "element_type": "button",
        "expected_behavior": "Disabled when at last page. Enabled otherwise. Navigates to next page.",
        "dims": [EXISTS, ACTION, STYLE, FAIL],
        "page": "UsageDashboard.tsx",
    },
    # ──────────────────────────────────────────────
    # SECTION S: API Contracts (data sources)
    # ──────────────────────────────────────────────
    {
        "id": "EL-dashboard-123",
        "name": "API - GET /api/analytics/summary",
        "element_type": "endpoint",
        "expected_behavior": "Returns totalConversations, avgResponseTime, resolutionRate, customerSatisfaction, escalationRate, escalationCount. Billable-only.",
        "dims": [VALUE, FAIL, LOAD],
        "page": "API",
    },
    {
        "id": "EL-dashboard-124",
        "name": "API - GET /api/analytics/daily-volume",
        "element_type": "endpoint",
        "expected_behavior": "Returns days[] with date, total, billable. Period-filtered. Billable-only.",
        "dims": [VALUE, FRESH, FAIL, LOAD],
        "page": "API",
    },
    {
        "id": "EL-dashboard-125",
        "name": "API - GET /api/admin/inbox/conversations",
        "element_type": "endpoint",
        "expected_behavior": "Returns conversations[] filtered billable-only. Limit 5 for dashboard.",
        "dims": [VALUE, FAIL, LOAD],
        "page": "API",
    },
    {
        "id": "EL-dashboard-126",
        "name": "API - GET /api/analytics/intents",
        "element_type": "endpoint",
        "expected_behavior": "Returns intents[] with agent, invocationCount, percentage. Billable-only.",
        "dims": [VALUE, FAIL, LOAD],
        "page": "API",
    },
    {
        "id": "EL-dashboard-127",
        "name": "API - GET /api/analytics/gaps",
        "element_type": "endpoint",
        "expected_behavior": "Returns gaps[] with conversationId, status, customerId, turnCount, messageCount, startedAt.",
        "dims": [VALUE, FAIL, LOAD],
        "page": "API",
    },
    {
        "id": "EL-dashboard-128",
        "name": "API - GET /api/config",
        "element_type": "endpoint",
        "expected_behavior": "Returns config object with brand_name, custom_instructions, brand_voice, test_mode_enabled, widget_* fields.",
        "dims": [VALUE, FAIL],
        "page": "API",
    },
    {
        "id": "EL-dashboard-129",
        "name": "API - GET /api/config/activation-status",
        "element_type": "endpoint",
        "expected_behavior": "Returns is_active, is_configured. Controls setup checklist visibility.",
        "dims": [VALUE, FAIL],
        "page": "API",
    },
]


def main():
    inserted = 0
    skipped = 0

    for el in ELEMENTS:
        existing = kb.get_testable_element(el["id"])
        if existing:
            skipped += 1
            continue

        kb.insert_testable_element(
            id=el["id"],
            subsystem="dashboard",
            page_or_module=el["page"],
            name=el["name"],
            element_type=el["element_type"],
            expected_behavior=el["expected_behavior"],
            applicable_dimensions=el["dims"],
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
            spec_id=el.get("spec"),
        )
        inserted += 1

    # Summary
    coverage = kb.get_element_coverage_summary()
    print(f"Inserted: {inserted}, Skipped (existing): {skipped}")
    print(f"Total dashboard elements: {coverage['total_elements']}")
    print(f"Active: {coverage['total_active']}")

    # Count dimensions
    all_elements = kb.list_testable_elements(subsystem="dashboard")
    dim_counts = {}
    for el in all_elements:
        dims = el.get("applicable_dimensions_parsed", [])
        for d in dims:
            dim_counts[d] = dim_counts.get(d, 0) + 1

    print("\nDimension coverage needed:")
    for dim, count in sorted(dim_counts.items(), key=lambda x: -x[1]):
        print(f"  {dim}: {count} elements")

    total_assertions = sum(dim_counts.values())
    print(f"\nTotal test assertions needed: {total_assertions}")


if __name__ == "__main__":
    main()
