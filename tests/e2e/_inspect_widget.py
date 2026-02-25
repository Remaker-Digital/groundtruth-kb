"""Inspect Widget page DOM to identify actual elements for E2E test fixes."""
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent))

from playwright.sync_api import sync_playwright
from tests.e2e.conftest import AdminApiMocker, ADMIN_VITE_PORT

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page()

mocker = AdminApiMocker(tier="professional")
page.route("**/api/**", mocker.handle_route)
page.add_init_script("sessionStorage.setItem('agentred_api_key', 'test_key');")
page.goto(f"http://localhost:{ADMIN_VITE_PORT}/admin/standalone/", wait_until="networkidle")
page.wait_for_selector("text=Dashboard", timeout=15_000)

# Navigate to Widget page
page.get_by_text("Widget configuration", exact=True).first.click()
page.wait_for_timeout(1500)

print("=== WIDGET PAGE BUTTONS ===")
buttons = page.locator("button")
for i in range(min(buttons.count(), 30)):
    btn = buttons.nth(i)
    txt = (btn.text_content() or "").strip()[:80]
    aria = btn.get_attribute("aria-label") or ""
    title = btn.get_attribute("title") or ""
    print(f"  [{i}] text={txt!r}  aria={aria!r}  title={title!r}")

print("\n=== WIDGET PAGE INPUTS ===")
inputs = page.locator("input")
for i in range(min(inputs.count(), 20)):
    inp = inputs.nth(i)
    val = (inp.input_value() or "")[:60]
    typ = inp.get_attribute("type") or ""
    ro = inp.get_attribute("readonly")
    print(f"  [{i}] type={typ!r}  value={val!r}  readonly={ro!r}")

# Check for text containing key-related words
print("\n=== KEY-RELATED TEXT ===")
body_text = page.text_content("body") or ""
for keyword in ["key", "Key", "pk_", "copy", "Copy", "rotate", "Rotate", "widget_key"]:
    idx = body_text.find(keyword)
    if idx >= 0:
        context = body_text[max(0, idx-30):idx+50].strip()
        print(f"  Found '{keyword}' at {idx}: ...{context!r}...")

# Navigate to Knowledge Base page
print("\n\n=== KNOWLEDGE BASE PAGE ===")
page.get_by_text("Knowledge base", exact=True).first.click()
page.wait_for_timeout(1500)

body_text = page.text_content("body") or ""
for keyword in ["Website", "website", "Source", "source", "testco", "crawl"]:
    idx = body_text.find(keyword)
    if idx >= 0:
        context = body_text[max(0, idx-30):idx+50].strip()
        print(f"  Found '{keyword}' at {idx}: ...{context!r}...")

# Check API calls made
print("\n=== API CALLS (KB page) ===")
kb_calls = [c for c in mocker.api_calls if "knowledge" in c["url"].lower()]
for c in kb_calls:
    print(f"  {c['method']} {c['url']}")

# Navigate to Memory & Privacy to check viewport
print("\n\n=== MEMORY & PRIVACY PAGE ===")
page.get_by_text("Memory & privacy", exact=True).first.click()
page.wait_for_timeout(1500)

switches = page.locator('input[type="checkbox"], [role="switch"]')
print(f"Total switches: {switches.count()}")
for i in range(min(switches.count(), 10)):
    sw = switches.nth(i)
    bb = sw.bounding_box()
    print(f"  [{i}] checked={sw.is_checked()}  visible={sw.is_visible()}  bbox={bb}")

viewport = page.viewport_size
print(f"Viewport: {viewport}")

browser.close()
p.stop()
