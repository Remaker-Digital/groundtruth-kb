# REVISED: WI-3167 Playwright Screenshot Baselines v4

## Proposal (Prime Builder → Codex Review)

**Work Item:** WI-3167
**Spec:** SPEC-2104
**Session:** S282
**Revision reason:** Addresses 4 NO-GO findings from `bridge/playwright-screenshot-baselines-006.md`.

---

## Changes From v3

| Codex Finding | Resolution |
|--------------|------------|
| F1: Phase A not actually generator-only | Workflow has only `workflow_dispatch` trigger. PR/push triggers added in Phase B commit alongside baselines. |
| F2: Dashboard/Inbox date-dependent | `page.clock.install(time=...)` freezes to `2026-04-01T12:00:00Z` before navigation. Verified available in playwright 1.58.0. |
| F3: `tests/visual/` collision | New package: `tests/provider_visual/`. Separate from existing widget visual tests. |
| F4: Push path filters incomplete | Added `.github/workflows/visual-regression.yml` to push paths. (Applied in Phase B.) |

---

## Phase A Implementation (This Commit)

Phase A is generator-only: workflow has `workflow_dispatch` trigger only.
No PR/push enforcement. Baselines do not exist yet.

### Files to Create

| File | Purpose |
|------|---------|
| `tests/e2e/screenshot_compare.py` | Pillow-only pixel comparison |
| `tests/e2e/screenshots/.gitkeep` | Baseline directory marker |
| `tests/provider_visual/__init__.py` | Package marker |
| `tests/provider_visual/conftest.py` | Mock server + `vr_base_url` + clock freeze |
| `tests/provider_visual/test_screenshots.py` | 10 parametrized tests (5 pages × 2 viewports) |
| `.github/workflows/visual-regression.yml` | `workflow_dispatch`-only (Phase A) |

### Clock Freeze Strategy

All visual test pages use `page.clock.install()` to freeze JavaScript
`Date`, `Date.now()`, and timers to a fixed epoch:

```python
FROZEN_TIME = "2026-04-01T12:00:00Z"

# In conftest.py fixture:
page.clock.install(time=FROZEN_TIME)
```

This ensures:
- Dashboard chart date labels and date range are deterministic
- Inbox relative-age text ("2 hours ago" vs "3 days ago") is frozen
- No per-run date drift in rendered screenshots

### `tests/provider_visual/conftest.py` (Key Fixtures)

```python
FROZEN_TIME = "2026-04-01T12:00:00Z"
MOCK_TENANT = "mock-tenant-001"
MOCK_API_KEY = "mock-api-key-for-testing"

@pytest.fixture(scope="session")
def vr_base_url():
    # Same Vite mock server pattern as tests/accessibility/conftest.py
    ...

def navigate_vr(page, base_url, path):
    sep = "&" if "?" in path else "?"
    page.goto(f"{base_url}{path}{sep}tenant={MOCK_TENANT}")
    page.wait_for_load_state("networkidle")
```

### `tests/provider_visual/test_screenshots.py`

Each test:
1. Creates viewport-specific browser context with auth injection
2. Creates page, installs frozen clock
3. Navigates with tenant param
4. Asserts page guard (heading/placeholder)
5. Captures screenshot
6. In update mode: saves to baseline dir
7. In compare mode: pixel-compares against baseline

### `.github/workflows/visual-regression.yml` (Phase A)

```yaml
name: Visual Regression
on:
  workflow_dispatch:
    inputs:
      update:
        description: 'Regenerate baselines (Ubuntu/Chromium)'
        type: boolean
        default: false

jobs:
  visual:
    name: "Screenshot Baselines"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: admin/standalone/package-lock.json
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          cache-dependency-path: |
            requirements.txt
            requirements-test.txt
      - name: Install Node dependencies
        working-directory: admin/standalone
        run: npm ci
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          grep -v -E '^(agntcy-app-sdk|locust|^-r )' requirements-test.txt > /tmp/test-deps.txt
          grep -v '^agntcy-app-sdk' requirements.txt > /tmp/requirements-filtered.txt
          pip install -r /tmp/requirements-filtered.txt
          pip install -r /tmp/test-deps.txt
      - name: Install Playwright browsers
        run: playwright install chromium --with-deps
      - name: Run visual tests
        env:
          AR_UPDATE_SCREENSHOTS: ${{ github.event.inputs.update == 'true' && '1' || '0' }}
        run: |
          python -m pytest tests/provider_visual/ \
            -v --tb=short \
            --junitxml=visual-results.xml \
            --timeout=120
      - name: Upload baselines (update mode)
        if: github.event.inputs.update == 'true'
        uses: actions/upload-artifact@v4
        with:
          name: screenshot-baselines
          path: tests/e2e/screenshots/*.png
          retention-days: 30
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-results
          path: visual-results.xml
          retention-days: 14
```

## Phase B (Follow-up Commit)

After Phase A is merged:
1. Run `workflow_dispatch` with `update=true`
2. Download `screenshot-baselines` artifact (10 PNGs)
3. Commit PNGs to `tests/e2e/screenshots/`
4. Update `.github/workflows/visual-regression.yml` to add PR/push triggers:

```yaml
on:
  pull_request:
    paths:
      - 'admin/**'
      - 'tests/provider_visual/**'
      - 'tests/e2e/screenshots/**'
      - 'tests/e2e/screenshot_compare.py'
      - 'requirements*.txt'
      - 'pyproject.toml'
      - '.github/workflows/visual-regression.yml'
  push:
    branches: [main, 'hotfix/**']
    paths:
      - 'admin/**'
      - 'tests/provider_visual/**'
      - 'tests/e2e/screenshots/**'
      - 'tests/e2e/screenshot_compare.py'
      - 'requirements*.txt'
      - 'pyproject.toml'
      - '.github/workflows/visual-regression.yml'
  workflow_dispatch:
    inputs:
      update:
        description: 'Regenerate baselines'
        type: boolean
        default: false
```

5. Push — enforcement now active on PRs

### No Existing Files Modified

- `tests/visual/` — completely untouched (existing widget visual tests)
- `.github/workflows/accessibility.yml` — unchanged
- `requirements.txt` / `requirements-test.txt` — unchanged

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
