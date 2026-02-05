"""
Update the Shopify storefront homepage content.

Replaces the "Generated test data" placeholder with Agent Red
marketing content using the Shopify Theme Files API.

Usage:
    # Preview changes (no API calls):
    python scripts/update_homepage.py

    # Apply changes:
    python scripts/update_homepage.py --apply

Requires in .env.local:
    SHOPIFY_STORE_URL=blanco-9939.myshopify.com
    SHOPIFY_ACCESS_TOKEN=shpat_...

The access token must have 'write_themes' and 'read_themes' scopes.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local
_env_path = PROJECT_ROOT / ".env.local"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

THEME_ID = "gid://shopify/OnlineStoreTheme/149122777271"

# ---------------------------------------------------------------------------
# Updated homepage template
# ---------------------------------------------------------------------------

HOMEPAGE_TEMPLATE = {
    "sections": {
        # Hero banner
        "6a3bb789-ce10-45f5-ae67-e2063ef8c76b": {
            "type": "image-banner",
            "blocks": {
                "template--18309637636369__6a3bb789-ce10-45f5-ae67-e2063ef8c76b-168016437761699a6e-0": {
                    "type": "heading",
                    "settings": {
                        "heading": "Cut Support Costs 40-60%. Without Cutting Quality.",
                        "heading_size": "h1",
                    },
                },
                "template--18309637636369__6a3bb789-ce10-45f5-ae67-e2063ef8c76b-168016437761699a6e-1": {
                    "type": "text",
                    "settings": {
                        "text": (
                            "Agent Red deploys six AI agents that handle your customer "
                            "conversations \u2014 instantly, accurately, and in your brand "
                            "voice. Your team focuses on what matters. The AI handles the rest."
                        ),
                        "text_style": "body",
                    },
                },
                "template--18309637636369__6a3bb789-ce10-45f5-ae67-e2063ef8c76b-168016437761699a6e-2": {
                    "type": "buttons",
                    "settings": {
                        "button_label_1": "Start Free Trial",
                        "button_link_1": "/pages/pricing",
                        "button_style_secondary_1": False,
                        "button_label_2": "See Features",
                        "button_link_2": "/pages/features",
                        "button_style_secondary_2": True,
                    },
                },
            },
            "block_order": [
                "template--18309637636369__6a3bb789-ce10-45f5-ae67-e2063ef8c76b-168016437761699a6e-0",
                "template--18309637636369__6a3bb789-ce10-45f5-ae67-e2063ef8c76b-168016437761699a6e-1",
                "template--18309637636369__6a3bb789-ce10-45f5-ae67-e2063ef8c76b-168016437761699a6e-2",
            ],
            "custom_css": [],
            "settings": {
                "image": "shopify://shop_images/theme_cover_image.jpg",
                "image_overlay_opacity": 40,
                "image_height": "medium",
                "desktop_content_position": "middle-left",
                "show_text_box": True,
                "desktop_content_alignment": "left",
                "color_scheme": "background-1",
                "image_behavior": "none",
                "mobile_content_alignment": "center",
                "stack_images_on_mobile": True,
                "show_text_below": True,
            },
        },
        # Featured products
        "featured_collection": {
            "type": "featured-collection",
            "settings": {
                "title": "<strong>AI-Powered Customer Service Plans</strong>",
                "heading_size": "h1",
                "description": (
                    "<p>Transparent pricing. Platform fee plus metered AI usage. "
                    "Every plan includes a 14-day free trial.</p>"
                ),
                "show_description": True,
                "description_style": "body",
                "collection": "automated-collection",
                "products_to_show": 10,
                "columns_desktop": 3,
                "full_width": False,
                "show_view_all": True,
                "view_all_style": "solid",
                "enable_desktop_slider": True,
                "color_scheme": "background-1",
                "image_ratio": "portrait",
                "show_secondary_image": True,
                "show_vendor": False,
                "show_rating": False,
                "enable_quick_add": False,
                "columns_mobile": "2",
                "swipe_on_mobile": False,
                "padding_top": 36,
                "padding_bottom": 36,
            },
        },
        # Persistent Customer Memory highlight
        "f1552b18-6017-4231-810d-74e61da22c37": {
            "type": "image-with-text",
            "blocks": {
                "template--18309637636369__f1552b18-6017-4231-810d-74e61da22c37-1680164422d7fb2efc-0": {
                    "type": "heading",
                    "settings": {
                        "heading": "Conversations That Remember",
                        "heading_size": "h1",
                    },
                },
                "template--18309637636369__f1552b18-6017-4231-810d-74e61da22c37-1680164422d7fb2efc-1": {
                    "type": "text",
                    "settings": {
                        "text": (
                            "<p>Every interaction builds on the last. Agent Red remembers "
                            "customer preferences, past issues, and communication style "
                            "\u2014 so customers never repeat themselves and every response "
                            "feels personal. No competitor offers this level of per-customer "
                            "AI memory.</p>"
                        ),
                        "text_style": "body",
                    },
                },
                "template--18309637636369__f1552b18-6017-4231-810d-74e61da22c37-1680164422d7fb2efc-2": {
                    "type": "button",
                    "settings": {
                        "button_label": "Learn More",
                        "button_link": "/pages/features",
                    },
                },
            },
            "block_order": [
                "template--18309637636369__f1552b18-6017-4231-810d-74e61da22c37-1680164422d7fb2efc-0",
                "template--18309637636369__f1552b18-6017-4231-810d-74e61da22c37-1680164422d7fb2efc-1",
                "template--18309637636369__f1552b18-6017-4231-810d-74e61da22c37-1680164422d7fb2efc-2",
            ],
            "settings": {
                "image": "shopify://shop_images/theme_cover_image.jpg",
                "height": "adapt",
                "desktop_image_width": "medium",
                "layout": "image_first",
                "desktop_content_position": "middle",
                "desktop_content_alignment": "left",
                "content_layout": "no-overlap",
                "color_scheme": "accent-1",
                "image_behavior": "none",
                "mobile_content_alignment": "left",
                "padding_top": 60,
                "padding_bottom": 60,
            },
        },
        # Six agents overview (replaces collection-list)
        "38cdf60f-e431-43b5-aac3-7e6215447d67": {
            "type": "rich-text",
            "blocks": {
                "richtext-heading": {
                    "type": "heading",
                    "settings": {
                        "heading": "Six AI Agents. One Seamless Experience.",
                        "heading_size": "h1",
                    },
                },
                "richtext-text": {
                    "type": "text",
                    "settings": {
                        "text": (
                            "<p>Intent Classification (98% accuracy) \u2192 "
                            "Knowledge Retrieval (real-time Shopify sync) \u2192 "
                            "Response Generation (GPT-4o, your brand voice) \u2192 "
                            "Critic Validation (100% content safety) \u2192 "
                            "Smart Escalation (full context handoff) \u2192 "
                            "Analytics (actionable insights).</p>"
                            "<p>Response time under 2 seconds. 3,071 requests per "
                            "second throughput. 99.95% uptime SLA. Starting at "
                            "$149/month.</p>"
                        ),
                        "text_style": "body",
                    },
                },
                "richtext-button": {
                    "type": "button",
                    "settings": {
                        "button_label": "See All Features",
                        "button_link": "/pages/features",
                        "button_style_secondary": False,
                    },
                },
            },
            "block_order": [
                "richtext-heading",
                "richtext-text",
                "richtext-button",
            ],
            "settings": {
                "desktop_content_position": "center",
                "content_alignment": "center",
                "color_scheme": "background-1",
                "full_width": True,
                "padding_top": 40,
                "padding_bottom": 52,
            },
        },
    },
    "order": [
        "6a3bb789-ce10-45f5-ae67-e2063ef8c76b",
        "featured_collection",
        "f1552b18-6017-4231-810d-74e61da22c37",
        "38cdf60f-e431-43b5-aac3-7e6215447d67",
    ],
}


UPSERT_MUTATION = """
mutation themeFilesUpsert($themeId: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
  themeFilesUpsert(themeId: $themeId, files: $files) {
    upsertedThemeFiles {
      filename
    }
    userErrors {
      field
      message
      filename
    }
  }
}
"""


async def update_homepage(*, dry_run: bool = True) -> None:
    """Update the storefront homepage template."""

    from src.integrations.shopify_client import ShopifyGraphQLClient

    store_url = os.environ.get("SHOPIFY_STORE_URL", "")
    access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")

    if not store_url or not access_token:
        logger.error("SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN required")
        sys.exit(1)

    template_json = json.dumps(HOMEPAGE_TEMPLATE, indent=2)

    print("[PLAN] Homepage template update:")
    print(f"  Theme: {THEME_ID}")
    print(f"  File: templates/index.json")
    print(f"  Size: {len(template_json)} bytes")
    print()
    print("  Sections:")
    for section_id in HOMEPAGE_TEMPLATE["order"]:
        section = HOMEPAGE_TEMPLATE["sections"][section_id]
        section_type = section["type"]
        # Get heading from first block if present
        heading = ""
        blocks = section.get("blocks", {})
        for block in blocks.values():
            if block.get("type") == "heading":
                heading = block["settings"].get("heading", "")
                break
        title = section.get("settings", {}).get("title", "")
        display = heading or title or "(no heading)"
        print(f"    [{section_type}] {display}")

    if dry_run:
        print()
        print("[DRY RUN] No changes made. Run with --apply to update.")
        return

    async with ShopifyGraphQLClient(store_url, access_token) as client:
        logger.info("Updating templates/index.json...")
        result = await client.execute(
            UPSERT_MUTATION,
            {
                "themeId": THEME_ID,
                "files": [
                    {
                        "filename": "templates/index.json",
                        "body": {"type": "TEXT", "value": template_json},
                    }
                ],
            },
        )

        upsert_result = result.get("themeFilesUpsert", {})
        errors = upsert_result.get("userErrors", [])

        if errors:
            logger.error("Update failed:")
            for e in errors:
                logger.error("  %s: %s (%s)", e.get("field", "?"), e["message"], e.get("filename", ""))
            sys.exit(1)

        upserted = upsert_result.get("upsertedThemeFiles", [])
        print(f"\n[OK] Updated {len(upserted)} file(s):")
        for f in upserted:
            print(f"  - {f['filename']}")
        print("\nRefresh the storefront to see the changes.")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Update storefront homepage")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()
    await update_homepage(dry_run=not args.apply)


if __name__ == "__main__":
    asyncio.run(main())
