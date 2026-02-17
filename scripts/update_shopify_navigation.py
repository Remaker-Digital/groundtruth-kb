"""
Update the Shopify storefront main navigation menu.

Queries the existing main-menu, discovers page GIDs, and updates
the navigation to include all Agent Red marketing pages in the
desired order.

Usage:
    # Preview menu changes (no API calls to update):
    python scripts/update_shopify_navigation.py

    # Apply menu update:
    python scripts/update_shopify_navigation.py --apply

Requires in .env.local:
    SHOPIFY_STORE_URL=blanco-9939.myshopify.com
    SHOPIFY_ACCESS_TOKEN=shpat_...

The access token must have 'read_online_store_navigation' and
'write_online_store_navigation' scopes (or legacy 'read_content'
+ 'write_content' may work on some stores).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local
load_env_local()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Desired navigation structure (order matters)
# ---------------------------------------------------------------------------

# These are the pages we want in the main nav, in display order.
# type=FRONTPAGE means the store homepage (no resourceId needed).
# type=PAGE means a Shopify Page (needs resourceId from page GID).
# type=HTTP means a custom URL link.
DESIRED_NAV = [
    {"title": "Home", "type": "FRONTPAGE"},
    {"title": "Features", "type": "PAGE", "handle": "features"},
    {"title": "Pricing", "type": "PAGE", "handle": "pricing"},
    {"title": "Integrations", "type": "PAGE", "handle": "integrations"},
    {"title": "About", "type": "PAGE", "handle": "about"},
    {"title": "Contact", "type": "PAGE", "handle": "contact"},
    {"title": "Catalog", "type": "HTTP", "url": "/collections/all"},
]


# ---------------------------------------------------------------------------
# GraphQL queries and mutations
# ---------------------------------------------------------------------------

GET_MENUS_QUERY = """
query GetMenus {
  menus(first: 10) {
    nodes {
      id
      handle
      title
      items {
        id
        title
        type
        url
        resourceId
      }
    }
  }
}
"""

GET_PAGES_QUERY = """
query GetPages {
  pages(first: 50) {
    nodes {
      id
      title
      handle
    }
  }
}
"""

MENU_UPDATE_MUTATION = """
mutation menuUpdate($id: ID!, $title: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, items: $items) {
    menu {
      id
      handle
      title
      items {
        id
        title
        type
        url
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

async def update_navigation(*, dry_run: bool = True) -> None:
    """Query current menu state, build desired nav, and optionally apply."""

    from src.integrations.shopify_client import ShopifyGraphQLClient

    store_url = os.environ.get("SHOPIFY_STORE_URL", "")
    access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")

    if not store_url or not access_token:
        logger.error("SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN must be set in .env.local")
        sys.exit(1)

    async with ShopifyGraphQLClient(store_url, access_token) as client:

        # --- Step 1: Find the main-menu ---
        logger.info("Querying existing menus...")
        menus_data = await client.execute(GET_MENUS_QUERY)
        menus = menus_data.get("menus", {}).get("nodes", [])

        main_menu = None
        for menu in menus:
            if menu.get("handle") == "main-menu":
                main_menu = menu
                break

        if not main_menu:
            logger.error("Could not find menu with handle 'main-menu'. Available menus:")
            for m in menus:
                logger.error("  - %s (handle: %s)", m.get("title"), m.get("handle"))
            sys.exit(1)

        menu_id = main_menu["id"]
        menu_title = main_menu["title"]
        current_items = main_menu.get("items", [])

        print(f"\n[FOUND] Main menu: {menu_title} ({menu_id})")
        print(f"  Current items ({len(current_items)}):")
        for item in current_items:
            print(f"    - {item['title']} ({item['type']}) {item.get('url', '')}")

        # --- Step 2: Get all pages to resolve handles → GIDs ---
        logger.info("Querying pages...")
        pages_data = await client.execute(GET_PAGES_QUERY)
        pages = pages_data.get("pages", {}).get("nodes", [])

        page_by_handle: dict[str, dict] = {}
        for page in pages:
            page_by_handle[page["handle"]] = page

        print(f"\n[FOUND] {len(pages)} pages:")
        for page in pages:
            print(f"    - {page['title']} (handle: {page['handle']}, id: {page['id']})")

        # --- Step 3: Build the new menu items list ---
        new_items = []
        missing_pages = []

        for nav_item in DESIRED_NAV:
            if nav_item["type"] == "FRONTPAGE":
                new_items.append({
                    "title": nav_item["title"],
                    "type": "FRONTPAGE",
                })
            elif nav_item["type"] == "PAGE":
                handle = nav_item["handle"]
                page = page_by_handle.get(handle)
                if not page:
                    missing_pages.append(handle)
                    logger.warning("Page with handle '%s' not found - skipping", handle)
                    continue
                new_items.append({
                    "title": nav_item["title"],
                    "type": "PAGE",
                    "resourceId": page["id"],
                    "url": f"/pages/{handle}",
                })
            elif nav_item["type"] == "HTTP":
                new_items.append({
                    "title": nav_item["title"],
                    "type": "HTTP",
                    "url": nav_item["url"],
                })

        if missing_pages:
            logger.warning(
                "Missing pages: %s. Create them first with create_shopify_pages.py",
                ", ".join(missing_pages),
            )

        print(f"\n[PLAN] New navigation ({len(new_items)} items):")
        for item in new_items:
            suffix = f" -> {item.get('url', '')}" if item.get("url") else ""
            resource = f" [{item.get('resourceId', '')}]" if item.get("resourceId") else ""
            print(f"    - {item['title']} ({item['type']}){resource}{suffix}")

        # --- Step 4: Apply or dry-run ---
        if dry_run:
            print("\n[DRY RUN] No changes made. Run with --apply to update the menu.")
            return

        logger.info("Updating menu...")
        variables = {
            "id": menu_id,
            "title": menu_title,
            "items": new_items,
        }

        result = await client.execute(MENU_UPDATE_MUTATION, variables)
        menu_result = result.get("menuUpdate", {})
        user_errors = menu_result.get("userErrors", [])

        if user_errors:
            logger.error("Menu update failed:")
            for err in user_errors:
                logger.error("  %s: %s", err.get("field", "?"), err["message"])
            sys.exit(1)

        updated_menu = menu_result.get("menu", {})
        updated_items = updated_menu.get("items", [])

        print(f"\n[OK] Menu updated successfully!")
        print(f"  Menu: {updated_menu.get('title')} ({updated_menu.get('id')})")
        print(f"  Items ({len(updated_items)}):")
        for item in updated_items:
            print(f"    - {item['title']} ({item['type']}) {item.get('url', '')}")


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update the Shopify storefront main navigation menu",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the menu update (omit for dry run)",
    )
    args = parser.parse_args()

    await update_navigation(dry_run=not args.apply)


if __name__ == "__main__":
    asyncio.run(main())
