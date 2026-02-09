"""Capture Shopify App Store screenshots from the prototype at 1600x900."""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "shopify" / "screenshots"
PROTOTYPE_URL = "http://localhost:3000"
WIDTH = 1600
HEIGHT = 900

# Pages to capture: (nav_label, filename, scroll_y, pre_action)
PAGES = [
    ("Dashboard", "01-dashboard.png", 0, None),
    ("Inbox", "02-conversation-inbox.png", 0, None),
    ("Knowledge Base", "03-knowledge-base.png", 0, None),
    ("Widget", "04-widget-configurator.png", 0, None),
    ("Configuration", "05-ai-configuration.png", 0, None),
    ("Analytics", "06-analytics.png", 70, None),  # slight scroll to show chart
]


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})

        # Navigate to prototype
        await page.goto(PROTOTYPE_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)  # let React render

        # Hide shell switcher
        await page.evaluate("""
            document.querySelectorAll('button').forEach(btn => {
                if (btn.textContent.includes('Standalone') || btn.textContent.includes('Shopify (Polaris)')) {
                    btn.parentElement.style.display = 'none';
                }
            });
        """)

        for nav_label, filename, scroll_y, pre_action in PAGES:
            # Click nav item
            await page.evaluate(f"""
                document.querySelectorAll('.mantine-NavLink-label').forEach(el => {{
                    if (el.textContent.trim() === '{nav_label}') el.closest('a, button').click();
                }});
            """)
            await page.wait_for_timeout(1000)  # let page render

            # Scroll if needed
            if scroll_y > 0:
                await page.evaluate(f"window.scrollTo(0, {scroll_y})")
                await page.wait_for_timeout(500)

            # Run pre_action if any
            if pre_action:
                await page.evaluate(pre_action)
                await page.wait_for_timeout(500)

            # Capture screenshot
            filepath = OUTPUT_DIR / filename
            await page.screenshot(path=str(filepath), type="png")
            print(f"Saved: {filepath} ({WIDTH}x{HEIGHT})")

        await browser.close()

    print(f"\nAll {len(PAGES)} screenshots saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
