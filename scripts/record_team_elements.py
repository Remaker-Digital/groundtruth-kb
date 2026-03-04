"""Record Team Members page testable elements in the Knowledge Database.

Elements inventoried from:
  - admin/standalone/pages/Team.tsx (Mantine)
  - admin/shared/TeamManager.tsx (inline styles)

Sections:
  A: Page Header
  B: Invite Form
  C: Team Table Structure
  D: Member Row Elements
  E: Escalation Category Controls
  F: Member Actions
  G: Empty & Loading States

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
CHANGE_REASON = "S136: Team Members element inventory per SPEC-1652/1653"

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
    # ── Section A: Page Header ───────────────────────────────────────────
    {
        "id": "EL-team-001", "name": "Page title",
        "element_type": "text",
        "expected_behavior": "Text: 'Team members' — page heading.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-002", "name": "Page subtitle",
        "element_type": "text",
        "expected_behavior": (
            "Text: 'Manage team members, assign roles, and configure escalation categories.' "
            "Dimmed, below title."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-003", "name": "Member count display",
        "element_type": "text",
        "expected_behavior": "Shows total number of team members (e.g., 'N members').",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-004", "name": "Invite member button",
        "element_type": "button",
        "expected_behavior": (
            "'+ Invite member' button. Toggles invite form visibility. "
            "Only visible to superadmin/admin roles."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, SECURITY],
        "page": "Team.tsx",
    },

    # ── Section B: Invite Form ───────────────────────────────────────────
    {
        "id": "EL-team-005", "name": "Invite form container",
        "element_type": "container",
        "expected_behavior": (
            "Collapsible form that appears when '+ Invite member' is clicked. "
            "Contains email, name, role fields and action buttons."
        ),
        "dims": [EXISTS, STYLE, MODAL],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-006", "name": "Invite email input",
        "element_type": "input",
        "expected_behavior": (
            "Required email input with email validation. "
            "Placeholder or label indicates email address."
        ),
        "dims": [EXISTS, VALUE, INPUT, FAIL],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-007", "name": "Invite name input",
        "element_type": "input",
        "expected_behavior": "Optional name input for the new team member display name.",
        "dims": [EXISTS, VALUE, INPUT],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-008", "name": "Invite role dropdown",
        "element_type": "dropdown",
        "expected_behavior": (
            "Role selector dropdown showing available roles. "
            "Label shows currently selected role."
        ),
        "dims": [EXISTS, VALUE, INPUT, ACTION],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-009", "name": "Invite submit button",
        "element_type": "button",
        "expected_behavior": (
            "'Invite' button. Submits invite form. "
            "Disabled until required fields are filled. Shows loading state."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, LOAD, FAIL],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-010", "name": "Invite cancel button",
        "element_type": "button",
        "expected_behavior": "'Cancel' button. Closes invite form and resets fields.",
        "dims": [EXISTS, VALUE, ACTION],
        "page": "Team.tsx",
    },

    # ── Section C: Team Table Structure ──────────────────────────────────
    {
        "id": "EL-team-011", "name": "Team table",
        "element_type": "table",
        "expected_behavior": (
            "Table displaying all team members. Headers: Team member, Role, "
            "Joined, Last active, Escalations, Actions."
        ),
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-012", "name": "Table header: Team member",
        "element_type": "text",
        "expected_behavior": "Column header 'Team member'.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-013", "name": "Table header: Role",
        "element_type": "text",
        "expected_behavior": "Column header 'Role'.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-014", "name": "Table header: Joined",
        "element_type": "text",
        "expected_behavior": "Column header 'Joined'.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-015", "name": "Table header: Last active",
        "element_type": "text",
        "expected_behavior": "Column header 'Last active'.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-016", "name": "Table header: Escalations",
        "element_type": "text",
        "expected_behavior": "Column header 'Escalations'.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-017", "name": "Table header: Actions",
        "element_type": "text",
        "expected_behavior": "Column header 'Actions'.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },

    # ── Section D: Member Row Elements ───────────────────────────────────
    {
        "id": "EL-team-018", "name": "Member display name + email",
        "element_type": "text",
        "expected_behavior": "Shows member display name (bold) and email (dimmed, below).",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-019", "name": "Member role selector",
        "element_type": "dropdown",
        "expected_behavior": (
            "Role dropdown for changing member's role. "
            "Disabled for superadmin rows (cannot change own role). "
            "Options: admin, escalation_agent, viewer."
        ),
        "dims": [EXISTS, VALUE, INPUT, ACTION, SECURITY],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-020", "name": "Member joined date",
        "element_type": "text",
        "expected_behavior": "Formatted date when member was added (e.g., 'Mar 1, 2026').",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-021", "name": "Member last active date",
        "element_type": "text",
        "expected_behavior": "Relative time since last activity (e.g., '2h ago', 'Never').",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-022", "name": "Member unresolved escalation count",
        "element_type": "text",
        "expected_behavior": "Number of unresolved escalations assigned to this member.",
        "dims": [EXISTS, VALUE, STYLE, FRESH],
        "page": "Team.tsx",
    },

    # ── Section E: Escalation Category Controls ──────────────────────────
    {
        "id": "EL-team-023", "name": "Escalation category chips",
        "element_type": "badge",
        "expected_behavior": (
            "Toggleable category chips for escalation_agent role members. "
            "6 categories: Sales, Support, Service, Account, Technical, General. "
            "Clicking toggles assignment. Hidden for non-escalation_agent roles."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, CONFIG, SECURITY],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-024", "name": "Role tooltip",
        "element_type": "tooltip",
        "expected_behavior": (
            "Hover tooltip on role selector showing role descriptions. "
            "Explains permissions for each role level."
        ),
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },

    # ── Section F: Member Actions ────────────────────────────────────────
    {
        "id": "EL-team-025", "name": "Active/Disabled toggle",
        "element_type": "button",
        "expected_behavior": (
            "Toggle button switching member between active and disabled states. "
            "Hidden for superadmin rows. Changes member's is_active status."
        ),
        "dims": [EXISTS, VALUE, STYLE, ACTION, SECURITY, FAIL],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-026", "name": "Delete member button",
        "element_type": "button",
        "expected_behavior": (
            "Trash icon button for removing a team member. "
            "Hidden for superadmin rows. Opens confirmation dialog."
        ),
        "dims": [EXISTS, STYLE, ACTION, MODAL, SECURITY],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-027", "name": "Delete confirmation dialog",
        "element_type": "modal",
        "expected_behavior": (
            "Confirmation modal asking 'Are you sure you want to remove [name]?' "
            "with Cancel and Remove buttons."
        ),
        "dims": [EXISTS, VALUE, STYLE, MODAL, ACTION],
        "page": "Team.tsx",
    },

    # ── Section G: Empty & Loading States ────────────────────────────────
    {
        "id": "EL-team-028", "name": "Team table loading state",
        "element_type": "loader",
        "expected_behavior": "Loading spinner shown while team members are fetched from API.",
        "dims": [EXISTS, STYLE, LOAD],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-029", "name": "Empty team message",
        "element_type": "text",
        "expected_behavior": "'No team members yet' message with invitation prompt when table is empty.",
        "dims": [EXISTS, VALUE, STYLE],
        "page": "Team.tsx",
    },
    {
        "id": "EL-team-030", "name": "Team API error state",
        "element_type": "alert",
        "expected_behavior": "Error banner when team member fetch fails. Shows retry option.",
        "dims": [EXISTS, VALUE, STYLE, FAIL],
        "page": "Team.tsx",
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
                subsystem="team",
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

    print(f"\nRecorded {inserted} team elements in KB ({skipped} skipped).")


if __name__ == "__main__":
    main()
