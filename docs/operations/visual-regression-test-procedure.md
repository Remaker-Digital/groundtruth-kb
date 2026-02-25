# Visual Regression Test Procedure

| Attribute | Value |
|-----------|-------|
| **Type** | Repeatable Procedure |
| **Last verified** | — |
| **Last corrected** | 2026-02-24 (initial creation) |

---

## 1. Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `WIDGET_DIR` | `widget/` | Widget source root |
| `WIDGET_DEV_PORT` | `3100` | Vite dev server port |
| `ADMIN_STANDALONE_PORT` | `3300` | Admin standalone dev server port |
| `ADMIN_PROVIDER_PORT` | `3400` | Admin provider dev server port |
| `BRAND_PRIMARY_COLOR` | `#ff3621` | Agent Red brand primary |
| `BRAND_FONT_FAMILY` | `Inter` | Brand font |
| `PANEL_WIDTH_STANDARD` | `380px` | Default panel width |
| `PANEL_HEIGHT` | `520px` | Panel height |
| `HEADER_HEIGHT` | `64px` | Header height token |
| `SCREENSHOT_DIR` | `tests/visual/screenshots/` | Vision round-trip artifacts |
| `TEST_MARKER` | `visual` | pytest marker for visual tests |

---

## 2. Preconditions

- [ ] `widget/node_modules/` exists (`cd widget && npm install` completed)
- [ ] Playwright browsers installed (`npx playwright install chromium`)
- [ ] `pytest-playwright` package installed (`pip install pytest-playwright`)
- [ ] No other process is listening on port `WIDGET_DEV_PORT`

**Verification:**
```powershell
# Check node_modules
Test-Path widget\node_modules

# Check Playwright browsers
npx playwright install --dry-run chromium

# Check pytest-playwright
pip show pytest-playwright

# Check port availability
Test-NetConnection -ComputerName localhost -Port 3100 -WarningAction SilentlyContinue | Select-Object TcpTestSucceeded
```

---

## 3. Layer 1 — Structural Presence Tests

### Purpose
Verify that key DOM elements (header, input bar, buttons, greeting) exist and are correctly wired. Catches structural regressions from refactoring.

### ACTION
```powershell
pytest tests/visual/test_widget_structure.py -v --timeout=60
```

### EXPECTED
All tests PASS. Test count: 16 (may vary as tests are added).

### ON FAIL
- **Element not found**: Check if component was renamed or restructured. Fix the test or the component.
- **Timeout waiting for iframe**: Widget may fail to boot. Check browser console for errors. Verify config mock is being intercepted.
- **Vite server fails to start**: Check if port 3100 is already in use. Kill the process or change the port.

---

## 4. Layer 2 — CSS Property Assertions

### Purpose
Verify brand-critical computed CSS values: primary color on header, font family, spacing tokens, dark mode derivation, animation keyframes.

### ACTION
```powershell
pytest tests/visual/test_widget_css.py -v --timeout=60
```

### EXPECTED
All tests PASS. Test count: 14 (may vary as tests are added).

### ON FAIL
- **Color mismatch**: Token resolution changed. Check `resolveTokens()` in `widget/src/theme/tokens.ts`.
- **Missing keyframe**: CSS animation was removed from `Panel.tsx` PANEL_STYLES.
- **Font not applied**: Custom font not loading, or fontFamily token resolution changed.

---

## 5. Layer 3 — Claude Vision Round-Trip (Interactive)

### Purpose
Use Claude's multimodal screenshot analysis to check visual quality beyond what DOM/CSS assertions can detect: overall layout balance, color harmony, visual hierarchy, spacing consistency.

This layer is **interactive** — it runs during a Claude Code session using the Claude Preview MCP tools.

### Step 5.1 — Start Widget Dev Server

**ACTION:**
Use Claude Preview to start the widget dev server:
```
preview_start(name="widget-dev")
```

**EXPECTED:** Server starts on port `WIDGET_DEV_PORT`, returns a serverId.

### Step 5.2 — Take Baseline Screenshots

**ACTION:**
Navigate to the dev page and capture screenshots in each state:

1. Navigate to `http://localhost:3100/dev.html`
2. Wait for widget SDK to be ready
3. Capture screenshot of launcher in closed state
4. Open the widget via SDK
5. Capture screenshot of the open panel (light mode)
6. Capture accessibility snapshot for structural reference

**EXPECTED:** Three artifacts captured.

### Step 5.3 — Visual Quality Checklist

**ACTION:**
Review the screenshot using Claude's vision capabilities. Check against this checklist:

| Criterion | Pass Condition |
|-----------|---------------|
| **Header color** | Brand primary (#ff3621) is prominent, not washed out |
| **Text contrast** | White text on header is readable (WCAG AA) |
| **Layout balance** | Header, message area, and input bar are proportionally sized |
| **Spacing consistency** | No elements touching edges; padding is visually uniform |
| **Font rendering** | Inter renders cleanly, no fallback serif visible |
| **Bubble styling** | Agent bubble is light gray, distinct from background |
| **Close button** | X icon is visible and correctly positioned (top-right) |
| **Greeting** | Greeting message is visible in the conversation area |
| **Input bar** | Textarea is visible, placeholder text is readable |
| **Overall polish** | Looks like a commercial product, not a prototype |

### Step 5.4 — CSS Property Spot-Check

**ACTION:**
Use `preview_inspect` to verify specific CSS values:

```
# Header background
preview_inspect(serverId, selector="#ar-panel-root > div > div:first-child", styles=["background-color", "height", "color"])
```

**EXPECTED:** Values match the design tokens defined in `tokens.ts`.

### Step 5.5 — Dark Mode Check (Optional)

**ACTION:**
Switch to dark mode and repeat screenshot:

```
preview_resize(serverId, colorScheme="dark")
preview_screenshot(serverId)
```

**EXPECTED:** Dark background (#1A1A1A), light text, agent bubble adjusts.

---

## 6. Layer 4 — Pixel-Diff Regression (Deferred)

**Status:** Deferred to post-beta.

When implemented, this layer will:
1. Capture reference screenshots (golden images) from a known-good state
2. On each test run, capture new screenshots
3. Pixel-diff against golden images using `pixelmatch` or similar
4. Fail on >0.5% pixel difference (threshold TBD)

Infrastructure needed:
- Golden image storage (committed to repo or external)
- `pixelmatch` or `playwright-visual-comparisons` integration
- CI pipeline step

---

## 7. Postconditions

After successful execution of Layers 1-3:

- [ ] All Layer 1 structural tests PASS
- [ ] All Layer 2 CSS property tests PASS
- [ ] Layer 3 visual quality checklist confirms no regressions
- [ ] No new test failures introduced by recent changes
- [ ] Screenshot artifacts saved to `SCREENSHOT_DIR` (if taken)

---

## 8. Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| Vite port 3100 already in use | Environment transient | Kill existing process, retry |
| Widget init timeout (no SDK ready) | Procedure defect if persistent | Check API mock is intercepting; check widget boot errors |
| iframe not created after open | Procedure defect | Widget architecture changed; update iframe selector |
| CSS color value format differs (hex vs rgb) | Procedure defect | Update assertion to match browser's computed format |
| Closed Shadow DOM blocks launcher access | Not a failure | By design; use SDK methods instead of DOM queries |
| Test flaky due to animation timing | Environment transient | Increase wait timeout value |
| Font not loaded (network font) | Environment transient | Retry; ensure fonts are bundled or CDN-accessible |
| node_modules missing | Environment setup | Run `cd widget && npm install` |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
