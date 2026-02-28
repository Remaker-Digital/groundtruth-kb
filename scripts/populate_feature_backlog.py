#!/usr/bin/env python3
"""
S117 Migration: Populate KB backlog from frozen backlog feature candidates.

Converts ~55 open feature items from the frozen backlog (WI #226-294 + #138-139)
into proper KB work items and creates a backlog snapshot.

Skips 14 items already completed in S97-S103 or retired:
  #239, #246, #247, #248, #261(retired), #266, #267, #270, #277, #280,
  #287, #288, #289, #292

Idempotent: checks for existing work items before creating.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))

import db

CHANGED_BY = "S117-backlog-migration"
SESSION = "S117"

# ─────────────────────────────────────────────────────────────────────────────
# Feature candidates — organized by category
# ─────────────────────────────────────────────────────────────────────────────

FEATURES = [
    # ── Infrastructure (deferred post-launch) ────────────────────────────
    {
        "old_wi": 138,
        "title": "Customer context pre-computation / warm-up on session start",
        "component": "agent_implementation",
        "priority": "P3",
        "description": "Profile pre-caching on session start to reduce first-response latency.",
    },
    {
        "old_wi": 139,
        "title": "Investigate Azure OpenAI PTU at scale (50+ tenants)",
        "component": "infrastructure_automation",
        "priority": "P3",
        "description": "Provisioned Throughput Units become cost-effective at 50+ concurrent tenants ($3,300/mo minimum). Defer until scale justifies.",
    },
    # ── Admin UI: Help tooltips with doc links ───────────────────────────
    {
        "old_wi": 226,
        "title": "Admin contextual tooltips with documentation links",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Add help icon tooltips across all admin pages linking to relevant documentation on agentredcx.com.",
    },
    {
        "old_wi": 259,
        "title": "Dashboard metric cards: help tooltips with doc links",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Each dashboard metric card (conversations, response time, resolution rate, satisfaction, escalation) should have a help tooltip with doc link.",
    },
    {
        "old_wi": 260,
        "title": "KB toolbar buttons: help tooltips with doc links",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Scan for conflicts, Export CSV, and Import buttons on Knowledge Base page need on-hover tooltips explaining function and linking to docs.",
    },
    {
        "old_wi": 263,
        "title": "Configuration section help tooltips with doc links",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Each config section (Brand & persona, Policies, Escalation, Custom instructions, Language, Test mode) should include a help tooltip.",
    },
    {
        "old_wi": 272,
        "title": "Widget page section help tooltips with doc links",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Each Widget configuration section (Appearance, Content, Behavior) should include a help icon tooltip with doc link.",
    },
    {
        "old_wi": 281,
        "title": "Billing metric cards: help tooltips with doc links",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Each Billing metric card (plan, conversations used, pack balance, overage cost) should have a help tooltip with doc link.",
    },
    # ── Admin UI: Naming & labeling improvements ─────────────────────────
    {
        "old_wi": 258,
        "title": "Display storefront name prominently on Dashboard",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Dashboard should display the merchant's storefront name in large type above the metric cards for quick identification.",
    },
    {
        "old_wi": 262,
        "title": "Rename 'Configuration' to 'Agent configuration'",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Page title, sidebar nav label, and breadcrumbs should read 'Agent configuration' to clarify this configures the AI agent, not general settings.",
    },
    {
        "old_wi": 268,
        "title": "Rename 'Widget' nav/page to 'Widget configuration'",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Sidebar nav label and page title should read 'Widget configuration' instead of 'Widget configurator' / 'Widget'.",
    },
    {
        "old_wi": 269,
        "title": "Rename color fields: 'Header left color' / 'Header right color'",
        "component": "customer_interface",
        "priority": "P1",
        "description": "'Primary color' renamed to 'Header left color'. 'Header gradient end' renamed to 'Header right color'. Clearer for non-designers.",
    },
    {
        "old_wi": 276,
        "title": "Rename 'Member' column to 'Team member'",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Team page column heading 'Member' should read 'Team member' for clarity.",
    },
    {
        "old_wi": 278,
        "title": "Rename 'Agent' role to 'Escalation agent'",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Role label 'Agent' renamed to 'Escalation agent' throughout UI to distinguish from the AI agent. Update API enum and all display surfaces.",
    },
    {
        "old_wi": 293,
        "title": "Rename 'Review and launch' to 'Custom AI instructions'",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Current 'Review and launch' wizard step should be renamed. Should NOT include a launch button (launching is via setup checklist).",
    },
    # ── Admin UI: Layout & interaction improvements ──────────────────────
    {
        "old_wi": 264,
        "title": "Escalation threshold slider label alignment",
        "component": "customer_interface",
        "priority": "P1",
        "description": "'Conservative' and 'Aggressive' labels extend beyond slider width. Left-justify 'Conservative' and right-justify 'Aggressive'.",
    },
    {
        "old_wi": 271,
        "title": "Side-by-side color pickers for header colors",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Header left and right color pickers are stacked vertically. Place them side-by-side in a two-column layout with live gradient preview between.",
    },
    {
        "old_wi": 273,
        "title": "Page assignments: single-column list instead of dropdown",
        "component": "customer_interface",
        "priority": "P1",
        "description": "'Page assignments' tab currently uses a dropdown to select one page at a time. Replace with a single-column list showing all page types simultaneously.",
    },
    {
        "old_wi": 274,
        "title": "Template variables inline below prompt input",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Remove 'Template variables' tab. Display clickable variable chips ({{product_title}}, {{collection_name}}, etc.) inline below the prompt input field.",
    },
    {
        "old_wi": 275,
        "title": "Role selector out of Actions column, replace textual badges",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Move role dropdown from Actions column to its own column. Replace textual role badges with the selector directly.",
    },
    {
        "old_wi": 282,
        "title": "'Purchase' button hover color consistency",
        "component": "customer_interface",
        "priority": "P1",
        "description": "On-hover background for conversation pack Purchase buttons should match sidebar nav item hover color for visual consistency.",
    },
    # ── Admin UI: Feature additions ──────────────────────────────────────
    {
        "old_wi": 240,
        "title": "Widget does not apply saved color configuration",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Widget ignores color settings saved via Widget page. After saving a new primary color or header gradient, the live widget still shows default colors.",
    },
    {
        "old_wi": 241,
        "title": "Widget does not display custom greeting message",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Greeting message configured in admin is not rendered in the widget. The generic placeholder appears instead of the custom text.",
    },
    {
        "old_wi": 242,
        "title": "Quick actions page: starter examples on first visit",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Empty prompt library on first visit with no guidance. Add pre-populated example quick actions that merchants can edit or delete.",
    },
    {
        "old_wi": 243,
        "title": "Quick action 'Icon' field: format guidance",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Icon input shows only a rocket emoji placeholder. Add guidance on format (emoji, icon name) and provide a picker or suggestion list.",
    },
    {
        "old_wi": 244,
        "title": "Quick action 'Sort order' field is redundant",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Per-prompt 'Sort order' is unnecessary because ordering is set via Page Assignments tab (Slot 1, 2, 3). Remove the field.",
    },
    {
        "old_wi": 245,
        "title": "Quick actions not previewable in admin widget",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Quick actions created in admin don't appear in the live widget preview on the Widget page or the floating widget on the admin.",
    },
    {
        "old_wi": 251,
        "title": "Pre-chat form and offline form: explanatory descriptions",
        "component": "customer_interface",
        "priority": "P1",
        "description": "The Pre-chat form and Offline form toggles on Widget page have no description or tooltip explaining what they do.",
    },
    {
        "old_wi": 265,
        "title": "Named configuration save/restore",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Add ability to save current configuration with a user-defined name, and select/apply a previously saved configuration.",
    },
    {
        "old_wi": 279,
        "title": "Escalation category assignment per team member",
        "component": "customer_interface",
        "priority": "P2",
        "description": "When a team member has Escalation agent role, show multi-select for escalation categories (Sales, Support, Service, Billing).",
    },
    # ── Widget: Mobile & responsive ──────────────────────────────────────
    {
        "old_wi": 227,
        "title": "Mobile position + offset config fields",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Add widget_mobile_position, widget_mobile_offset_x, widget_mobile_offset_y fields to schema, runtime, and admin.",
    },
    {
        "old_wi": 228,
        "title": "Mobile fullscreen mode",
        "component": "customer_interface",
        "priority": "P2",
        "description": "widget_mobile_fullscreen field — panel takes full viewport on mobile devices when enabled.",
    },
    {
        "old_wi": 229,
        "title": "Panel width/height config",
        "component": "customer_interface",
        "priority": "P3",
        "description": "widget_panel_width, widget_panel_height fields for desktop panel dimensions.",
    },
    {
        "old_wi": 230,
        "title": "Mobile layout switching in widget runtime",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Launcher + panel responsive layout based on mobile config fields. Auto-switch layout on small screens.",
    },
    {
        "old_wi": 257,
        "title": "Launcher position offset controls",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Vertical (Y) and horizontal (X) offset numeric controls for launcher position. Needed for sites with fixed footers or sidebars.",
    },
    # ── Widget: Chat UI improvements ─────────────────────────────────────
    {
        "old_wi": 249,
        "title": "Widget drop-shadow control",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Shadow intensity selector (none/subtle/standard/heavy) in Widget admin. Apply via CSS box-shadow in widget runtime.",
    },
    {
        "old_wi": 250,
        "title": "Widget launcher icon and agent avatar customization",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Image upload or selection for floating launcher icon and AR agent avatar in chat header. Store as data URIs in config.",
    },
    {
        "old_wi": 252,
        "title": "Chat UI resizable width",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Drag handle on left edge for horizontal resize, or width presets (compact/standard/wide). Persist position across sessions.",
    },
    {
        "old_wi": 253,
        "title": "Chat UI draggable/repositionable",
        "component": "customer_interface",
        "priority": "P3",
        "description": "Click-drag to reposition chat panel on header bar. Persist position across page navigations.",
    },
    {
        "old_wi": 254,
        "title": "Auto-open per page via Quick Actions config",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Auto-open configurable per page type (product, collection, homepage) as part of Quick Actions page assignments.",
    },
    {
        "old_wi": 255,
        "title": "Chat input area height: 3 text lines default",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Chat input is single-line. Increase default to 3 lines with auto-grow up to ~5. Use <textarea> with dynamic resize.",
    },
    {
        "old_wi": 256,
        "title": "Chat display area scroll controls",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Add subtle scrollbar styling, scroll-to-bottom button, and new-message indicator when scrolled up during streaming.",
    },
    # ── Widget: Targeting & automation ────────────────────────────────────
    {
        "old_wi": 231,
        "title": "Targeting rules schema (widget_rules)",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Structured ruleset model: URL include/exclude, referrer, UTM, time-on-page, scroll depth, exit-intent conditions.",
    },
    {
        "old_wi": 232,
        "title": "Lightweight rule evaluator in widget",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Client-side rule engine evaluating conditions at init and on page events. Determines widget visibility per targeting rules.",
    },
    {
        "old_wi": 233,
        "title": "Targeting rules admin UI",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Rule builder in WidgetConfigurator with condition/action pairs for configuring targeting rules visually.",
    },
    {
        "old_wi": 234,
        "title": "Exit-intent and scroll-depth triggers",
        "component": "customer_interface",
        "priority": "P3",
        "description": "Browser event listeners for exit-intent (mouseleave) and scroll percentage to trigger widget auto-open.",
    },
    # ── Widget: Internationalization ─────────────────────────────────────
    {
        "old_wi": 235,
        "title": "Locale packs infrastructure",
        "component": "customer_interface",
        "priority": "P2",
        "description": "widget_locale field (auto/en/es/fr-ca/...), locale file loading, fallback chain for multi-language widget UI.",
    },
    {
        "old_wi": 236,
        "title": "Localized header/offline text per locale",
        "component": "customer_interface",
        "priority": "P2",
        "description": "Per-locale overrides for user-visible strings (header, offline message, placeholder text).",
    },
    # ── Widget: Runtime JS API ───────────────────────────────────────────
    {
        "old_wi": 237,
        "title": "Runtime JS API: setTheme / setLocale",
        "component": "customer_interface",
        "priority": "P2",
        "description": "window.AgentRed.setTheme({...}), setLocale(locale) for per-page theme/locale overrides via JavaScript.",
    },
    {
        "old_wi": 238,
        "title": "Runtime JS API: setConfigPartial / setTargetingRules",
        "component": "customer_interface",
        "priority": "P3",
        "description": "setConfigPartial({...}), setTargetingRules(rules) for advanced JS integrations allowing programmatic widget control.",
    },
    # ── Onboarding / Wizard restructuring ────────────────────────────────
    {
        "old_wi": 285,
        "title": "Wizard mode selector: Standard / Test toggle (Step 0)",
        "component": "customer_interface",
        "priority": "P1",
        "description": "First wizard step is a toggle between 'Primary configuration' (initial setup) and 'Test group configuration' (test mode).",
    },
    {
        "old_wi": 286,
        "title": "Remove wizard steps that belong on dedicated pages",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Remove from wizard: Brand & tone (to Agent config), Languages (to Agent config), Memory & privacy (to new page).",
    },
    {
        "old_wi": 290,
        "title": "New sidebar page: Memory and privacy",
        "component": "customer_interface",
        "priority": "P2",
        "description": "'Memory and privacy' removed from wizard and becomes a dedicated page in sidebar nav.",
    },
    {
        "old_wi": 291,
        "title": "'Inactive' system state indicator in nav bar",
        "component": "customer_interface",
        "priority": "P1",
        "description": "When system not yet activated (no Go Live completed), nav bar shows an Inactive badge. Changes to Active after Go Live.",
    },
    {
        "old_wi": 294,
        "title": "Relocate fields from removed wizard steps to target pages",
        "component": "customer_interface",
        "priority": "P1",
        "description": "Ensure fields removed from wizard (WI #286) are present on target pages: Brand & tone to Agent config, Languages to Agent config, Memory to new Memory page.",
    },
]


def create_work_items(kdb: db.KnowledgeDB) -> list[str]:
    """Create KB work items from feature candidates. Returns list of created WI IDs."""
    # Find next available WI number
    existing = kdb.list_work_items()
    if existing:
        max_num = max(int(w["id"].replace("WI-", "")) for w in existing)
    else:
        max_num = 0

    created_ids = []
    next_num = max_num + 1

    for feat in FEATURES:
        wi_id = f"WI-{next_num:04d}"

        # Check idempotency by title match
        already_exists = any(
            w["title"] == feat["title"] for w in existing
        )
        if already_exists:
            print(f"  SKIP (title exists): {feat['title'][:60]}")
            # Still track the ID for the backlog
            match = next((w for w in existing if w["title"] == feat["title"]), None)
            if match:
                created_ids.append(match["id"])
            continue

        kdb.insert_work_item(
            id=wi_id,
            title=feat["title"],
            origin="new",
            component=feat["component"],
            resolution_status="open",
            changed_by=CHANGED_BY,
            change_reason=f"{SESSION}: feature candidate from frozen backlog WI #{feat['old_wi']}",
            description=feat.get("description"),
            priority=feat.get("priority"),
        )
        print(f"  CREATED {wi_id}: #{feat['old_wi']} {feat['title'][:60]}")
        created_ids.append(wi_id)
        next_num += 1

    return created_ids


def create_backlog_snapshot(kdb: db.KnowledgeDB, feature_wi_ids: list[str]) -> None:
    """Create a backlog snapshot with the new feature work items."""
    # Count by component and priority
    items = [kdb.get_work_item(wi_id) for wi_id in feature_wi_ids]
    items = [i for i in items if i]  # Filter None

    by_origin = dict(Counter(i["origin"] for i in items))
    by_component = dict(Counter(i["component"] for i in items))

    snapshot_id = "BACKLOG-001"
    existing = kdb.get_backlog_snapshot(snapshot_id)

    if existing:
        print(f"  Backlog snapshot {snapshot_id} already exists — skipping")
        return

    kdb.insert_backlog_snapshot(
        id=snapshot_id,
        title="Feature Backlog — Post-Launch Candidates (S117)",
        work_item_ids=feature_wi_ids,
        changed_by=CHANGED_BY,
        change_reason=f"{SESSION}: initial feature backlog from frozen backlog WI #138-294",
        description=(
            f"55 feature candidates migrated from frozen backlog. "
            f"Categories: Admin UI polish, Widget enhancements, Mobile/responsive, "
            f"Targeting/automation, Internationalization, Runtime API, Onboarding, Infrastructure."
        ),
        summary_by_origin=by_origin,
        summary_by_component=by_component,
    )
    print(f"  CREATED {snapshot_id}: {len(feature_wi_ids)} work items")


def main() -> None:
    kdb = db.KnowledgeDB()

    print("=" * 70)
    print("S117: Populate Feature Backlog")
    print("=" * 70)

    # Phase 1: Create work items
    print("\n--- Phase 1: Create Work Items ---")
    wi_ids = create_work_items(kdb)
    print(f"  Total: {len(wi_ids)} work items")

    # Phase 2: Create backlog snapshot
    print("\n--- Phase 2: Create Backlog Snapshot ---")
    create_backlog_snapshot(kdb, wi_ids)

    # Summary
    print("\n--- Summary ---")
    all_wi = kdb.list_work_items()
    open_wi = [w for w in all_wi if w["resolution_status"] == "open"]
    resolved_wi = [w for w in all_wi if w["resolution_status"] == "resolved"]

    by_component = Counter(w["component"] for w in open_wi)
    by_priority = Counter(w.get("priority", "NONE") for w in open_wi)

    print(f"  Total work items: {len(all_wi)}")
    print(f"  Open (feature candidates): {len(open_wi)}")
    print(f"  Resolved (test coverage): {len(resolved_wi)}")
    print(f"\n  Open by component:")
    for comp, cnt in by_component.most_common():
        print(f"    {comp}: {cnt}")
    print(f"\n  Open by priority:")
    for prio, cnt in sorted(by_priority.items()):
        print(f"    {prio}: {cnt}")

    snapshots = kdb.list_backlog_snapshots()
    print(f"\n  Backlog snapshots: {len(snapshots)}")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
