"""Record Inbox page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/Inbox.tsx (Mantine, 3-panel layout)
  - admin/shared/ConversationInbox.tsx (inline styles, 2-panel)
  - admin/shared/hooks/useInbox.ts
  - admin/shared/types/index.ts

Sections:
  A: Left Panel — Search & Filters
  B: Left Panel — Conversation List Items
  C: Center Panel — Thread Header & Actions
  D: Center Panel — Message Bubbles
  E: Right Panel — Customer Details
  F: Right Panel — Pipeline Trace
  G: Escalation Modal
  H: Empty & Loading States
  I: Notification Toast

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
CHANGE_REASON = "S136: Inbox element inventory per SPEC-1652/1653"

# Dimension shorthand
EXISTS = "exists"
VALUE = "correct_value"
STYLE = "correct_style"
ACTION = "action_works"
FRESH = "freshness"
RESP = "responsive"
FAIL = "failure_mode"
LOAD = "load_behavior"
URL = "correct_url"
MODAL = "modal_behavior"
INPUT = "input_behavior"
CONFIG = "config_propagation"
SECURITY = "security"
PERF = "performance"

# fmt: off
ELEMENTS = [
    # ── Section A: Left Panel — Search & Filters ─────────────────────────
    {
        "id": "EL-inbox-001", "name": "Search conversations input",
        "element_type": "input",
        "expected_behavior": (
            "TextInput with placeholder 'Search conversations...', search icon left section. "
            "350ms debounce. Shows loading spinner while searching. Clears on empty."
        ),
        "dims": [EXISTS, VALUE, STYLE, INPUT, LOAD, PERF],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-002", "name": "Status filter tabs",
        "element_type": "segmented_control",
        "expected_behavior": (
            "SegmentedControl with 5 segments: 'All (N)', 'Active (N)', 'Esc (N)', "
            "'Resolved (N)', 'Archived'. Counts update from API data. Filters conversation list."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, FRESH],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-003", "name": "All filter tab",
        "element_type": "tab",
        "expected_behavior": "Shows total conversation count. Default active tab on page load.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-004", "name": "Active filter tab",
        "element_type": "tab",
        "expected_behavior": "Shows count of active conversations. Filters to status=active only.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-005", "name": "Escalated filter tab",
        "element_type": "tab",
        "expected_behavior": "Shows count of escalated conversations. Label: 'Esc (N)'.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-006", "name": "Resolved filter tab",
        "element_type": "tab",
        "expected_behavior": "Shows count of resolved conversations. Filters to status=resolved.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-007", "name": "Archived filter tab",
        "element_type": "tab",
        "expected_behavior": "Filters to archived conversations (archivedAt != null). No count shown.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Inbox.tsx",
    },

    # ── Section B: Left Panel — Conversation List Items ──────────────────
    {
        "id": "EL-inbox-008", "name": "Conversation list item",
        "element_type": "list_item",
        "expected_behavior": (
            "Clickable row showing avatar, customer name, time ago, message count, "
            "status badge. Selected state: light pink bg (#FFF1F2) with red left border. "
            "Hover: light gray bg."
        ),
        "dims": [EXISTS, STYLE, ACTION],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-009", "name": "Conversation avatar",
        "element_type": "avatar",
        "expected_behavior": (
            "38px circle with customer initials. Color derived from name hash. "
            "Falls back to first letter of conversationId if no customer name."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-010", "name": "Conversation customer name",
        "element_type": "text",
        "expected_behavior": (
            "Customer name or truncated conversationId. Bold if conversation is unread "
            "(active/escalated status). Truncated with ellipsis if long."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-011", "name": "Conversation time ago",
        "element_type": "text",
        "expected_behavior": (
            "Relative time since last activity (e.g., '2h', '1d', '5h'). "
            "Right-aligned, dimmed text."
        ),
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-012", "name": "Conversation message count",
        "element_type": "text",
        "expected_behavior": "Shows 'N messages' below customer name. Dimmed, small text.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-013", "name": "Conversation status badge",
        "element_type": "badge",
        "expected_behavior": (
            "Color-coded status badge: blue=active, green=ended/resolved, "
            "red=escalated/error, yellow=idle/timed_out. Compact, left-aligned below message count."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-014", "name": "Conversation assigned agent text",
        "element_type": "text",
        "expected_behavior": "Shows assigned team member name if assignedTo is set. Dimmed, xs text.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-015", "name": "Unread indicator dot",
        "element_type": "indicator",
        "expected_behavior": (
            "Small red dot shown for conversations with active or escalated status, "
            "indicating they need attention."
        ),
        "dims": [EXISTS, STYLE, CONFIG],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-016", "name": "Selected conversation highlight",
        "element_type": "visual_state",
        "expected_behavior": (
            "Light pink background (#FFF1F2) with 3px red left border on selected conversation. "
            "Dark mode: tokens.surface background."
        ),
        "dims": [EXISTS, STYLE, ACTION],
        "page": "Inbox.tsx",
    },

    # ── Section C: Center Panel — Thread Header & Actions ────────────────
    {
        "id": "EL-inbox-017", "name": "Thread header customer name",
        "element_type": "text",
        "expected_behavior": (
            "Large customer name or conversationId displayed at top of center panel. "
            "Truncated if too long."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-018", "name": "Thread header status badge",
        "element_type": "badge",
        "expected_behavior": "Color-coded status badge matching conversation status in thread header.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-019", "name": "Thread header message count",
        "element_type": "text",
        "expected_behavior": "'N messages' count displayed in thread header area.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-020", "name": "Escalate button",
        "element_type": "button",
        "expected_behavior": (
            "Orange button labeled 'Escalate'. Opens escalation modal. "
            "Hidden when status is already escalated or resolved."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, MODAL],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-021", "name": "Resolve button",
        "element_type": "button",
        "expected_behavior": (
            "Green button labeled 'Resolve'. POSTs to mark conversation resolved. "
            "Hidden when status is already resolved."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-022", "name": "Archive button",
        "element_type": "button",
        "expected_behavior": (
            "Gray button labeled 'Archive'. POSTs to archive conversation. "
            "Only shown for resolved/timed_out conversations that aren't already archived."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-023", "name": "Unarchive button",
        "element_type": "button",
        "expected_behavior": (
            "Blue button labeled 'Unarchive'. POSTs to restore archived conversation. "
            "Only shown for archived conversations."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-024", "name": "Warning action icon",
        "element_type": "icon",
        "expected_behavior": "Warning triangle icon in header action area for flagging conversations.",
        "dims": [EXISTS, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-025", "name": "Check action icon",
        "element_type": "icon",
        "expected_behavior": "Checkmark icon in header action area for marking conversations.",
        "dims": [EXISTS, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-026", "name": "Trash action icon",
        "element_type": "icon",
        "expected_behavior": "Trash/delete icon in header action area.",
        "dims": [EXISTS, STYLE],
        "page": "Inbox.tsx",
    },

    # ── Section D: Center Panel — Message Bubbles ────────────────────────
    {
        "id": "EL-inbox-027", "name": "Customer message bubble",
        "element_type": "container",
        "expected_behavior": (
            "Left-aligned bubble with light blue background (#e8eaf6). "
            "'Customer' label above. Rounded corners except bottom-left (2px). "
            "Max width 70%. Dark mode: tokens.surface background."
        ),
        "dims": [EXISTS, VALUE, STYLE, RESP],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-028", "name": "AI message bubble",
        "element_type": "container",
        "expected_behavior": (
            "Right-aligned bubble with brand red tint (BRAND_PRIMARY + 14% opacity). "
            "'Agent Red AI' label with icon above. Rounded except bottom-right (2px). "
            "Max width 70%."
        ),
        "dims": [EXISTS, VALUE, STYLE, RESP],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-029", "name": "System message",
        "element_type": "container",
        "expected_behavior": (
            "Centered message with light gray background, italic dimmed text. "
            "Used for escalation events, status changes, etc."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-030", "name": "Message timestamp",
        "element_type": "text",
        "expected_behavior": (
            "Time displayed below each message bubble (e.g., '6:53 PM'). "
            "Left-aligned for customer, right-aligned for AI, center for system."
        ),
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-031", "name": "Message role label",
        "element_type": "text",
        "expected_behavior": (
            "'Customer' label above customer bubbles, 'Agent Red AI' with icon above AI bubbles. "
            "Bold, small text."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-032", "name": "Message thread scroll area",
        "element_type": "container",
        "expected_behavior": (
            "Scrollable area containing all messages. Auto-scrolls to bottom when new "
            "conversation selected or messages loaded."
        ),
        "dims": [EXISTS, STYLE, ACTION, PERF],
        "page": "Inbox.tsx",
    },

    # ── Section E: Right Panel — Customer Details ────────────────────────
    {
        "id": "EL-inbox-033", "name": "Detail panel large avatar",
        "element_type": "avatar",
        "expected_behavior": (
            "64px avatar with customer initials and color-coded background. "
            "Centered at top of right panel."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-034", "name": "Detail panel customer name",
        "element_type": "text",
        "expected_behavior": "Customer name or conversationId displayed below avatar. Center-aligned.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-035", "name": "Detail panel status badge",
        "element_type": "badge",
        "expected_behavior": "Color-coded status badge shown below customer name in detail panel.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-036", "name": "Conversation info section header",
        "element_type": "text",
        "expected_behavior": "'Conversation info' section header with bold text.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-037", "name": "Messages count field",
        "element_type": "text",
        "expected_behavior": "Label 'Messages' with count value. Shows total message count.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-038", "name": "Started date field",
        "element_type": "text",
        "expected_behavior": (
            "Label 'Started' with formatted date (e.g., 'Mar 3, 6:53 PM'). "
            "Uses Intl.DateTimeFormat."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-039", "name": "Last activity field",
        "element_type": "text",
        "expected_behavior": "Label 'Last activity' with relative time (e.g., '5h').",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-040", "name": "Assigned to field",
        "element_type": "text",
        "expected_behavior": (
            "Label 'Assigned to' with team member name. "
            "Only shown when conversation has an assigned agent."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-041", "name": "Escalation category badge",
        "element_type": "badge",
        "expected_behavior": (
            "Shows escalation category (Sales, Support, etc.) as a red badge "
            "when conversation is escalated."
        ),
        "dims": [EXISTS, VALUE, STYLE, CONFIG],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-042", "name": "Customer profile section header",
        "element_type": "text",
        "expected_behavior": "'Customer profile' section header with bold text.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-043", "name": "Verified status badge",
        "element_type": "badge",
        "expected_behavior": (
            "Label 'Verified' with badge: green 'Verified' if customerVerified=true, "
            "gray 'Anonymous' if false."
        ),
        "dims": [EXISTS, VALUE, STYLE, SECURITY],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-044", "name": "Customer identity message",
        "element_type": "text",
        "expected_behavior": (
            "'No customer identity collected in this conversation.' shown when anonymous. "
            "Shows name/email/customer ID when verified."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },

    # ── Section F: Right Panel — Pipeline Trace ──────────────────────────
    {
        "id": "EL-inbox-045", "name": "Pipeline trace section header",
        "element_type": "text",
        "expected_behavior": "'Pipeline trace' header with wave/spark icon. Shown in right panel.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-046", "name": "Pipeline trace intent badge",
        "element_type": "badge",
        "expected_behavior": "Light blue badge showing detected intent (e.g., 'product_inquiry').",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-047", "name": "Pipeline trace critic badge",
        "element_type": "badge",
        "expected_behavior": (
            "Green 'Approved' if criticPassed=true, red 'Retracted' if false. "
            "Shows Critic evaluation result."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-048", "name": "Pipeline trace total latency",
        "element_type": "text",
        "expected_behavior": "Total latency in ms displayed as monospace text (e.g., '1234ms').",
        "dims": [EXISTS, VALUE, STYLE, PERF],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-049", "name": "Pipeline trace stage bars",
        "element_type": "chart",
        "expected_behavior": (
            "Horizontal bar for each pipeline stage (Intent Classifier, Knowledge Retrieval, "
            "Response Generator, Critic). Color-coded: #2563EB, #059669, #D97706, #7C3AED. "
            "Width proportional to elapsed time. Opacity 0.4 if stage failed."
        ),
        "dims": [EXISTS, VALUE, STYLE, PERF],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-050", "name": "Pipeline trace model name",
        "element_type": "text",
        "expected_behavior": "Model name in monospace font below stage bars.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-051", "name": "Pipeline trace ID",
        "element_type": "text",
        "expected_behavior": "Truncated trace ID prefix in monospace font.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-052", "name": "No pipeline trace message",
        "element_type": "text",
        "expected_behavior": "'No pipeline trace available for this conversation.' shown when trace is null.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },

    # ── Section G: Escalation Modal ──────────────────────────────────────
    {
        "id": "EL-inbox-053", "name": "Escalation modal",
        "element_type": "modal",
        "expected_behavior": (
            "Modal titled 'Escalate to human'. Contains category dropdown (required), "
            "agent dropdown (optional), Cancel and Escalate buttons."
        ),
        "dims": [EXISTS, VALUE, STYLE, MODAL],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-054", "name": "Escalation category dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Required dropdown with 6 categories: Sales, Support, Service, Account, "
            "Technical, General. Red asterisk indicates required."
        ),
        "dims": [EXISTS, VALUE, INPUT, ACTION],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-055", "name": "Escalation agent dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Optional agent dropdown listing active team members. "
            "Helper text: 'No team members available...' when empty."
        ),
        "dims": [EXISTS, VALUE, INPUT],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-056", "name": "Escalation modal cancel button",
        "element_type": "button",
        "expected_behavior": "Default variant button that closes the modal without action.",
        "dims": [EXISTS, VALUE, ACTION, MODAL],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-057", "name": "Escalation modal submit button",
        "element_type": "button",
        "expected_behavior": (
            "Red 'Escalate' button. Disabled until category is selected. "
            "POSTs escalation request on click."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Inbox.tsx",
    },

    # ── Section H: Empty & Loading States ────────────────────────────────
    {
        "id": "EL-inbox-058", "name": "Conversation list loading spinner",
        "element_type": "loader",
        "expected_behavior": "Spinner shown while conversations are loading from API.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-059", "name": "Empty conversation list message",
        "element_type": "text",
        "expected_behavior": (
            "Chat bubble SVG icon + 'No conversations yet' (when list truly empty) "
            "or 'No matching conversations' (when filter yields zero results)."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-060", "name": "Select a conversation prompt",
        "element_type": "text",
        "expected_behavior": "'Select a conversation' centered in center panel when none is selected.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-061", "name": "Messages loading spinner",
        "element_type": "loader",
        "expected_behavior": "Small gray spinner shown while messages for selected conversation load.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-062", "name": "Failed to load messages error",
        "element_type": "text",
        "expected_behavior": "'Failed to load messages' with error detail when API call fails.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-063", "name": "No messages yet text",
        "element_type": "text",
        "expected_behavior": "'No messages in this conversation yet' when conversation has 0 messages.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },

    # ── Section I: Notification Toast ────────────────────────────────────
    {
        "id": "EL-inbox-064", "name": "Action notification toast",
        "element_type": "alert",
        "expected_behavior": (
            "Bottom-right toast (24px from edges). Color-coded: orange=escalated, "
            "green=resolved, gray=archived, blue=unarchived, red=error. "
            "Auto-dismiss after 4s. Close button included."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, PERF],
        "page": "Inbox.tsx",
    },

    # ── Section J: 3-Panel Layout Structure ──────────────────────────────
    {
        "id": "EL-inbox-065", "name": "Left panel container",
        "element_type": "container",
        "expected_behavior": (
            "320px fixed-width panel with border-right. Contains search, filters, "
            "and conversation list. Scrollable when list overflows."
        ),
        "dims": [EXISTS, STYLE, RESP],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-066", "name": "Center panel container",
        "element_type": "container",
        "expected_behavior": (
            "Flex-1 center panel with #fafafa background (light) or tokens.chrome (dark). "
            "Contains thread header, message area, and message input."
        ),
        "dims": [EXISTS, STYLE, RESP],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-067", "name": "Right panel container",
        "element_type": "container",
        "expected_behavior": (
            "280px fixed-width panel with border-left. Contains customer details, "
            "conversation info, and pipeline trace. Scrollable."
        ),
        "dims": [EXISTS, STYLE, RESP],
        "page": "Inbox.tsx",
    },

    # ── Section K: Search Results ────────────────────────────────────────
    {
        "id": "EL-inbox-068", "name": "Search result item",
        "element_type": "list_item",
        "expected_behavior": (
            "Search result showing avatar, customer name, matched snippet preview, "
            "status badge, and 'Matched in' badge (e.g., 'body', 'name')."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION],
        "page": "Inbox.tsx",
    },
    {
        "id": "EL-inbox-069", "name": "Search matched-in badge",
        "element_type": "badge",
        "expected_behavior": "Badge indicating where the search matched: 'body', 'name', etc.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Inbox.tsx",
    },
]
# fmt: on


def main():
    inserted = 0
    skipped = 0

    for el in ELEMENTS:
        try:
            kb.insert_testable_element(
                id=el["id"],
                subsystem="inbox",
                page_or_module=el["page"],
                name=el["name"],
                element_type=el["element_type"],
                expected_behavior=el["expected_behavior"],
                applicable_dimensions=el["dims"],
                changed_by=CHANGED_BY,
                change_reason=CHANGE_REASON,
            )
            inserted += 1
            print(f"  {el['id']}: {el['name']}")
        except Exception as exc:
            if "UNIQUE constraint" in str(exc):
                skipped += 1
                print(f"  {el['id']}: (already exists, skipped)")
            else:
                raise

    print(f"\nRecorded {inserted} inbox elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
