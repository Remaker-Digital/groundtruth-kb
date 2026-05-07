# Testing Infrastructure Proposal v2: Automated Quality & Completeness
### Agent Red Customer Experience — Revised Implementation Guide
**Original:** S201 (2026-03-17) | **Revised:** S202 (2026-03-17)
**Status:** Proposal — awaiting owner prioritization
**Audience:** Claude Code (fresh session) + Owner

> **Changes from v1:** Removed completed items (branch coverage, Phase 17/18, property tests).
> Corrected factual errors (spec statuses, API references, Playwright stack).
> Removed embedded credentials. Focused on genuinely new work only.

---

> **How to use this document:** This is a self-contained implementation guide. Read it
> top-to-bottom in a fresh session. Each section maps to actionable work items. The
> proposal is sequenced by ROI: § 3 (immediate, high-leverage) → § 4 (medium-term
> quality) → § 5 (long-term maturity). Every recommendation references the KB spec it
> implements or should generate.

---

## 1. Current State Assessment

### 1.1 What Exists

The project has a sophisticated, multi-layer test infrastructure:

| Layer | Count | Framework | Notes |
|-------|-------|-----------|-------|
| Unit | ~28 files | pytest | Isolated, fast |
| Multi-tenant | ~189 files | pytest | Largest suite; tenant isolation, config |
| Chat / Agents | ~23 files | pytest-asyncio | Async conversation pipeline |
| Integration | ~13 files | pytest + httpx | Shopify, Stripe, external APIs |
| E2E (mocked) | ~24 files | Playwright (Python) | Vite dev server + API mocking |
| E2E (live) | ~30 files | Playwright (Python) | Real staging environment |
| Visual | ~4 files | Playwright (Python) | Widget iframe, Vite port 3100 |
| Security | ~11 files | pytest | Adversarial, penetration |
| Performance | ~5 files | Locust | Load testing |
| Property-based | 5 files | Hypothesis | `tests/property/` — 46 tests (S201) |
| API Fuzzing | 2 files | Schemathesis | `tests/fuzzing/` — in-process ASGI (S201) |
| Regression | ~3 files | pytest | Tier 0/1/2 blocking gates |
| **TOTAL** | **~399 files** | | **~244,329 lines of test code** |

**Test execution infrastructure:**
- `scripts/run-tests-thermal-safe.ps1` — Windows-native batched execution with thermal cooling pauses
- `scripts/test_pipeline.py` — 18-phase PLAN-001 autonomous pipeline (E2E, live, fuzzing, property)
- `.github/workflows/python-tests.yml` — 5 parallel shards × 2 Python versions (3.12, 3.13)
- Branch coverage enabled (`pyproject.toml`); CI gate at 70% (`python-tests.yml` merged-coverage step)
- Mutation testing runner: `scripts/run_mutation_tests.py` (git-diff based, 70% target)

**Recent numbers (S200–S201):**
- 6,920 tests passing (unit + multi_tenant + chat + integrations)
- E2E pipeline: 1,039/1,050 passed (11 UI selector failures, no code defects)
- 46/46 regression tests passed
- 46 Hypothesis property tests passing (tests/property/)
- Schemathesis in-process fuzzing: 307 API operations discovered (tests/fuzzing/)

### 1.2 Remaining Gaps

These gaps were identified by codebase inspection and confirmed during the v1 review:

**Dependency gap (missing from `requirements-test.txt`):**
```
playwright      # imported by 50+ test files — critical for CI reproducibility
hypothesis      # tests/property/ uses @given — installed locally, not declared
schemathesis    # tests/fuzzing/ uses schemathesis.openapi — installed locally, not declared
mutmut          # scripts/run_mutation_tests.py — installed locally, not declared
```
These are installed on the development machine but not declared in the test requirements file, which means CI and fresh environments cannot run Phases 17–18 or the mutation testing runner.

**UI testing gaps:**
- No visual regression baseline / snapshot comparison system
- Shadow DOM launcher inaccessible to Playwright assertions
- No cross-browser testing (Firefox, Safari/WebKit)
- No screenshot/video capture on test failure
- `tests/widget/` files are NOT browser-automation tests (use httpx, not Playwright)
- No accessibility (a11y) testing
- No Storybook / component workbench for the React widget

**Quality metric gaps:**
- No mutation score tracking integrated into quality dashboard (SPEC-1838)
- No contract testing (widget ↔ chat API)
- No OpenAPI diff gate on PRs
- Coverage CI gate is 70% line-based; no separate branch coverage threshold

**CI/CD gaps:**
- E2E tests not in CI pipeline (staging access only — reasonable but undocumented)
- No post-failure artifact uploads (screenshots, traces, Playwright HTML report)
- No flaky test detection or smart retry

**NOT gaps (corrected from v1):**
- ~~Branch coverage not enabled~~ → Already enabled: `pyproject.toml` line 43, `branch = true`
- ~~Phase 17/18 placeholders~~ → Fully implemented in `test_pipeline.py` (S201)
- ~~Property tests not started~~ → 46 tests in `tests/property/` (S201)
- ~~Schemathesis not installed~~ → Installed locally; `tests/fuzzing/test_api_fuzz.py` runs in-process

---

## 2. Research Foundation

### 2.1 Industry Consensus: The Testing Pyramid

The most established model (Google, Martin Fowler) recommends:
- **70% unit tests** — fast, isolated, cheap to write
- **20% integration tests** — real dependencies (DB, Redis, APIs), no mocking
- **10% end-to-end tests** — browser automation, full stack

This project's distribution is approximately: 55% unit+multi_tenant / 35% integration+chat / 10% E2E. This is reasonable but the integration layer (Cosmos, Redis) relies heavily on mocking, which carries the risk of mock-production divergence. The **Spotify Honeycomb model** (designed for microservices) inverts this and prefers integration tests with real dependencies — relevant for Cosmos and Redis-backed features.

### 2.2 The Oracle Gap: Why Mutation Testing Matters

**Paper:** "Mind the Gap: Coverage vs Mutation Score" (arXiv:2309.02395, 2023)

The **oracle gap** is the disparity between high code coverage and low mutation score. A file with 95% branch coverage and 30% mutation score has tests that *execute* the code but do not *assert* meaningful outcomes. These are the rubber-stamp assertions that GOV-18 prohibits.

```python
# High-coverage, low-mutation-score test:
def test_rate_limit():
    result = compute_rate_limit("starter")
    assert result is not None  # ← PASSES but misses wrong-value defects

# Mutation-killing test:
def test_rate_limit():
    assert compute_rate_limit("starter") == 10
    assert compute_rate_limit("professional") == 300
```

**Key modules to prioritize for mutation testing:**
- `src/multi_tenant/middleware.py` — tenant isolation logic
- `src/multi_tenant/api_key_audit.py` — security-critical
- `src/multi_tenant/idle_tenant_detection.py` — business logic
- `src/multi_tenant/log_retention.py` — compliance-critical
- `src/chat/endpoints.py` — core product path

### 2.3 AI-Assisted Test Generation (Meta TestGen-LLM)

**Meta's TestGen-LLM approach (FSE 2024, arXiv:2402.09171):**
- 75% of generated tests compile; 57% reliably pass
- 25% increase in coverage in successful cases; 73% engineer acceptance rate
- **Critical gate:** Only promote generated tests that demonstrably increase branch coverage over the baseline

**Practical Claude Code workflow:**
```
1. Run coverage.py --branch to identify uncovered branches per module
2. Feed module source + coverage gap report to Claude
3. Claude generates candidate tests targeting uncovered branches
4. Gate: run pytest --co on generated tests (must compile)
5. Gate: run coverage.py before/after (must increase branch coverage)
6. Gate: run full test suite (must not regress existing tests)
7. Accept passing, coverage-improving tests; reject others
```

### 2.4 Web UI Testing: State of the Art (2025–2026)

**Playwright v1.58.0 (January 30, 2026):**

Key features relevant to this project:

1. **Playwright MCP Server** (github.com/microsoft/playwright-mcp):
   Exposes browser automation to Claude via Model Context Protocol. Uses the accessibility tree (not screenshots) — structured, low token cost, deterministic. Claude can navigate the Provider Console, fill forms, assert outcomes — all from within a Claude Code session.

   **Use case:** Exploratory testing of SPA pages during development sessions.

2. **Chrome for Testing builds** (v1.57):
   Uses Chrome for Testing instead of Chromium, providing more authentic browser behavior.

3. **Timeline visualization** (v1.58):
   HTML reports with merged test results and per-test execution timeline. Essential for CI debugging.

**Important note on test stack:** All existing browser tests in this project are Python/pytest-playwright (in `tests/e2e/` and `tests/e2e_live/`). Any new UI test generation should target the existing Python stack unless a deliberate decision is made to adopt a Node-based `.spec.ts` runner alongside it.

**Chromatic + Storybook — visual regression:**
- Storybook creates a component workbench for `widget/src/components/`
- Every component story becomes a visual test: render → snapshot → diff
- Chromatic runs tests across 4 browsers (Chrome, Safari, Firefox, Edge)
- Free tier available; used by GitHub, Vercel, Square, Adobe, BBC
- `MessageBubble.tsx` and `MessageList.tsx` are prime candidates

### 2.5 Contract Testing

**Pact** (docs.pact.io) implements Consumer-Driven Contract Testing:
- The widget (consumer) generates a contract: "I send messages in shape X and expect responses in shape Y"
- The FastAPI chat endpoint (provider) verifies it satisfies the contract
- If either side changes its shape, Pact catches the break before deployment

The Shopify widget ↔ chat endpoint (`widget/src/transport/http.ts` ↔ `src/chat/endpoints.py`) is the highest-value contract to test.

### 2.6 OpenAPI Breaking Change Detection

**CompaREST** (github.com/typeable/compaREST):
- Detects breaking vs non-breaking changes between two OpenAPI specifications
- GitHub Actions integration: auto-comments on PRs with a compatibility assessment
- Prevents accidental breaking changes to the 39 Control Plane endpoints

---

## 3. Immediate Actions (High ROI, Low Effort)

### 3.1 Fix the Dependency Gap
**Effort:** 30 minutes | **KB:** New WI → SPEC-1844

Add to `requirements-test.txt`:
```
playwright>=1.58.0
hypothesis>=6.151.0
schemathesis>=3.39.0
mutmut>=2.4.4
pytest-playwright>=0.5.0
```

Run:
```bash
pip install -r requirements-test.txt
playwright install chromium
playwright install-deps
```

This unblocks Phases 17 and 18 of `test_pipeline.py` in CI and on fresh environments.

### 3.2 Raise the CI Coverage Gate
**Effort:** 30 minutes | **KB:** New WI → SPEC-1844

Branch coverage is already enabled in `pyproject.toml` (`branch = true`). The CI enforcement is in `.github/workflows/python-tests.yml` at the "Check coverage threshold" step, which uses a hardcoded Python check:

```python
if pct < 70:
    print(f'FAIL: Coverage {pct:.1f}% is below 70% minimum')
    sys.exit(1)
```

**Action:** Raise the threshold from 70 to 75, with a ramp plan to 80:
```python
if pct < 75:
    print(f'FAIL: Coverage {pct:.1f}% is below 75% minimum')
    sys.exit(1)
```

**Rationale:** The project is at ~73% now. A 75% gate is tight but achievable, and creates pressure to maintain coverage as new code is added.

### 3.3 Enable Playwright MCP Server for Development Sessions
**Effort:** 1 hour | **KB:** New WI (no spec needed — development tooling)

Add to project-level `.mcp.json`:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {}
    }
  }
}
```

Once enabled, Claude Code can navigate the Provider Console, interact with the 9 Control Plane pages, and assert behaviors during development sessions.

### 3.4 Schemathesis Against Live Staging
**Effort:** 2 hours | **KB:** New WI → SPEC-1839

The existing `tests/fuzzing/test_api_fuzz.py` runs Schemathesis in-process against the ASGI app. This catches schema violations but misses network-layer and deployment-specific bugs.

**Action:** Run Schemathesis against the live staging endpoint:
```bash
uvx schemathesis run \
  "$STAGING_OPENAPI_URL" \
  --auth-type=apikey \
  --auth="$SPA_CONSOLE_API_KEY" \
  --checks=all \
  --stateful=links \
  --junit-xml=schemathesis-staging-results.xml \
  --report=schemathesis-staging-report.html
```

**Important:**
- Use environment variables for the staging URL and API key — never embed credentials in documents or scripts
- `--checks=all` includes `not_a_server_error` (5xx detection), which is the primary signal — do not exclude it
- `--stateful=links` enables sequential API call testing (create → read → update → delete chains)
- Expected yield: 5–15 real edge-case bugs on first run against the 39 Control Plane endpoints

**KB actions:** Create WIs for any bugs found. Update SPEC-1839 when live-staging fuzzing is operational.

---

## 4. Medium-Term Quality Improvements

### 4.1 Mutation Score Tracking in Quality Dashboard
**Effort:** 1–2 days | **KB:** New WI → SPEC-1838, SPEC-1842

The mutation testing runner (`scripts/run_mutation_tests.py`) and mutmut configuration exist. What's missing is integration with the quality dashboard (SPEC-1838).

**Design needed:**
1. A `src/quality_metrics/mutation_tracking.py` module that:
   - Parses mutmut output into structured data (killed/survived/timeout counts)
   - Computes mutation score per module: `killed / (killed + survived)`
   - Identifies "oracle gap" modules: high branch coverage + low mutation score
2. Storage of mutation scores in KB (new table or document type)
3. Display in the GET `/quality/score` API response alongside existing metrics

```python
# src/quality_metrics/mutation_tracking.py

def compute_mutation_score(killed: int, survived: int, timeout: int) -> float:
    """Mutation score = killed / (killed + survived)."""
    total = killed + survived
    return killed / total if total > 0 else 0.0

def identify_oracle_gap_modules(
    coverage_data: dict, mutation_data: dict,
    coverage_threshold: float = 0.80,
    mutation_threshold: float = 0.50
) -> list[dict]:
    """
    Identify modules with high coverage but low mutation score.
    These are the 'oracle gap' modules — tests that execute code but don't
    assert meaningful outcomes. See arXiv:2309.02395 and GOV-18.
    """
    gap_modules = []
    for module, branch_cov in coverage_data.items():
        mutation_score = mutation_data.get(module, 0.0)
        if branch_cov >= coverage_threshold and mutation_score < mutation_threshold:
            gap_modules.append({
                'module': module,
                'branch_coverage': branch_cov,
                'mutation_score': mutation_score,
                'oracle_gap': branch_cov - mutation_score
            })
    return sorted(gap_modules, key=lambda x: x['oracle_gap'], reverse=True)
```

**Target:** Run mutation testing nightly (not per-commit — too slow). Report as a warning, not a build failure, initially.

### 4.2 Expand Property-Based Tests to New Invariants
**Effort:** 1–2 days | **KB:** New WI → SPEC-1843

The existing 46 Hypothesis tests in `tests/property/` cover tier gating, config validation, and rate limit audit. The next expansion targets should be real module invariants:

**Log retention invariants** (SPEC-1837 — `src/multi_tenant/log_retention.py`):
```python
@given(retention_days=st.integers(min_value=1, max_value=3650))
def test_log_retention_cutoff_is_always_past(retention_days):
    """Computed cutoff is always in the past."""
    from src.multi_tenant.log_retention import compute_cutoff_date
    from datetime import datetime, timezone
    cutoff = compute_cutoff_date(retention_days=retention_days)
    assert cutoff < datetime.now(timezone.utc)
```

**Idle tenant detection invariants** (SPEC-1835 — `src/multi_tenant/idle_tenant_detection.py`):
- Idle classification is monotonic: a tenant idle for 90 days is at least as idle as one idle for 30 days
- Thresholds are ordered: 30 < 60 < 90 < 180

**Chat message invariants** (SPEC-area — `src/chat/endpoints.py`):
- Any valid message content returns 200 or 422, never 500
- All valid Pydantic model shapes parse without error

### 4.3 Storybook + Chromatic for Widget Components
**Effort:** 1–2 days | **KB:** New SPEC + WIs

**Install Storybook in `widget/`:**
```bash
cd widget
npx storybook@latest init --type react
```

**Create stories for key components:**
```typescript
// widget/src/components/MessageBubble.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { MessageBubble } from './MessageBubble';

const meta: Meta<typeof MessageBubble> = {
  title: 'Chat/MessageBubble',
  component: MessageBubble,
};
export default meta;

export const UserMessage: StoryObj = {
  args: { role: 'user', content: 'Hello, I need help with my order.' }
};

export const AgentMessage: StoryObj = {
  args: { role: 'assistant', content: 'I can help you with that.' }
};

export const LongMessage: StoryObj = {
  args: { role: 'assistant', content: 'A'.repeat(500) }
};
```

**Connect Chromatic:**
```bash
npx chromatic --project-token=$CHROMATIC_TOKEN --build-script-name=build-storybook
```

**What this gives you:**
- Every component renders as a story (smoke test — fails if component crashes)
- Chromatic captures pixel-perfect snapshots across 4 browsers
- PR builds show visual diff with approval/rejection workflow
- Free tier covers development use; ~$149/mo for CI at scale

### 4.4 Accessibility Testing
**Effort:** 1 day | **KB:** New SPEC + WI

```bash
pip install axe-playwright-python
```

Integrate with the existing E2E conftest (not by replacing the `page` fixture, but by adding a separate a11y assertion helper):

```python
# tests/e2e/a11y_helpers.py
from axe_playwright_python.sync_playwright import Axe

def assert_no_critical_a11y_violations(page):
    """Run axe-core and fail on critical/serious WCAG 2.1 AA violations."""
    axe = Axe()
    results = axe.run(page)
    violations = [v for v in results.violations if v['impact'] in ('critical', 'serious')]
    assert len(violations) == 0, f"Accessibility violations: {violations}"
```

Call `assert_no_critical_a11y_violations(page)` at the end of key E2E tests rather than wiring it into a fixture teardown (which would conflict with the existing Playwright setup).

### 4.5 CI Failure Artifacts (Screenshots + Traces)
**Effort:** 2 hours | **KB:** New WI (CI improvement)

Add to `.github/workflows/python-tests.yml`:
```yaml
- name: Upload Playwright artifacts on failure
  uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: playwright-traces-${{ matrix.shard }}
    path: test-artifacts/
    retention-days: 7
```

Enable Playwright's built-in failure capture via pytest-playwright CLI flags:
```bash
pytest tests/e2e/ \
  --tracing=retain-on-failure \
  --screenshot=only-on-failure \
  --video=retain-on-failure \
  --output=test-artifacts/
```

This makes CI E2E failures debuggable without local reproduction.

### 4.6 Pact Contract Testing for Widget ↔ Chat API
**Effort:** 2–3 days | **KB:** New SPEC + WIs

Install:
```bash
pip install pact-python
npm install @pact-foundation/pact --save-dev  # in widget/
```

**Consumer side (TypeScript widget — `widget/src/transport/http.test.ts`):**
```typescript
import { Pact } from '@pact-foundation/pact';

const provider = new Pact({
  consumer: 'AgentRedWidget',
  provider: 'AgentRedChatAPI',
  port: 1234,
});

it('sends a chat message and receives a response', async () => {
  await provider.addInteraction({
    state: 'a chat session exists',
    uponReceiving: 'a chat message',
    withRequest: {
      method: 'POST',
      path: '/chat',
      body: { message: 'Hello', tenant_id: 'test-tenant', session_id: 'sess-1' }
    },
    willRespondWith: {
      status: 200,
      body: { response: like('Hello! How can I help?'), session_id: 'sess-1' }
    }
  });
});
```

**Provider side (Python — `tests/contract/test_chat_provider.py`):**
```python
from pact import Verifier

def test_provider_satisfies_widget_contract():
    verifier = Verifier(
        provider='AgentRedChatAPI',
        provider_base_url='http://localhost:8000'
    )
    output, _ = verifier.verify_pacts(
        pact_urls=['pacts/widget-chat.json']
    )
    assert output == 0
```

**Value:** If `widget/src/transport/http.ts` changes the request shape, or `src/chat/endpoints.py` changes the response shape, Pact catches the contract break in CI before it reaches staging.

---

## 5. Long-Term Investments

### 5.1 AI-Assisted Test Generation Skill (Meta Pattern)

Implement the Meta TestGen-LLM filter-gated approach as a Claude Code skill:

```markdown
<!-- .claude/skills/generate-tests.md -->
---
name: generate-tests
description: Generate branch-coverage-increasing tests for a module using Claude
---

1. Run `coverage.py --branch --json -o /tmp/before.json` to capture baseline
2. Read the target module source code
3. Identify uncovered branches from the coverage report
4. Generate pytest tests targeting those specific branches
5. Run `pytest <generated_test_file>` — must compile and pass
6. Run `coverage.py --branch --json -o /tmp/after.json`
7. Compare before/after: only keep tests that increase branch coverage
8. Add accepted tests to the test suite
9. Record new test records in KB
```

The key innovation: **test gating by coverage improvement**, not by human review alone.

### 5.2 CompaREST OpenAPI Breaking Change Detection

Add to `.github/workflows/python-tests.yml` for PRs touching `src/`:
```yaml
- name: Check OpenAPI compatibility
  if: github.event_name == 'pull_request'
  run: |
    python -c "from src.main import app; import json; print(json.dumps(app.openapi()))" > /tmp/new-schema.json
    curl -s "$STAGING_OPENAPI_URL" > /tmp/old-schema.json
    npx compaREST --output-format markdown /tmp/old-schema.json /tmp/new-schema.json \
      > /tmp/api-compat-report.md
    cat /tmp/api-compat-report.md
```

**Value:** Prevents accidental breaking changes to the 39 Control Plane endpoints.

### 5.3 Flaky Test Detection

```yaml
# .github/workflows/python-tests.yml — nightly job
- name: Run tests with flakiness detection
  run: |
    pytest --count=3 --randomly-seed=12345 tests/regression/ \
      --junit-xml=flaky-detection.xml
  continue-on-error: true
```

Track flaky test occurrence in the KB as a quality metric.

### 5.4 Performance Benchmarking in E2E Tests

Add Core Web Vitals measurement to E2E tests:
```python
# tests/e2e/test_performance_benchmarks.py
def test_provider_console_load_time(page):
    """Provider Console dashboard must load in under 3 seconds."""
    start = time.time()
    page.goto("/provider/dashboard")
    page.wait_for_load_state("networkidle")
    load_time = time.time() - start
    assert load_time < 3.0, f"Page load time {load_time:.2f}s exceeds 3s threshold"
```

---

## 6. Decision Required: UI Test Stack

The existing browser test suite is entirely **Python/pytest-playwright** (`tests/e2e/`, `tests/e2e_live/`). The Playwright Test Agents feature (`npx playwright init-agents`) generates **Node/.spec.ts** test files.

**Options:**

| Approach | Pros | Cons |
|----------|------|------|
| **A. Stay Python-only** | Single stack, existing CI, consistent | No access to Playwright Test Agents |
| **B. Add Node .spec.ts alongside Python** | Test Agent generation, self-healing | Two test runners, two CI configs, maintenance burden |
| **C. Migrate to Node** | Full Playwright ecosystem access | Large migration cost, lose existing 50+ Python test files |

**Recommendation:** Option A (stay Python-only) unless AI-generated UI test coverage becomes a priority. The Playwright MCP server (§ 3.3) provides Claude-assisted exploratory testing within the existing Python stack.

**This requires an owner decision before any UI test generation work begins.**

---

## 7. Tool Evaluation Summary

### Recommended

| Tool | Category | Priority | Cost | Notes |
|------|----------|----------|------|-------|
| **Playwright MCP** | Exploratory testing | Critical | Free | Add to .mcp.json for Claude Code sessions |
| **Schemathesis (live)** | Network API fuzzing | Critical | Free/OSS | Run against staging; extends existing in-process suite |
| **coverage.py --branch** | Branch coverage gate | High | Free (in use) | Raise CI threshold from 70% to 75% |
| **Chromatic** | Visual regression | High | Free tier | Storybook integration for widget components |
| **Storybook** | Component workbench | High | Free | Widget/React component testing foundation |
| **mutmut + dashboard** | Mutation score tracking | High | Free | Extend quality dashboard with oracle gap detection |
| **Hypothesis (expand)** | Property-based testing | High | Free | Expand from 46 tests to new module invariants |
| **axe-playwright-python** | Accessibility | Medium | Free | WCAG 2.1 AA compliance for Provider Console |
| **Pact** | Contract testing | Medium | Free/OSS | Widget ↔ Chat API contract |
| **CompaREST** | API compatibility | Low | Free/OSS | PR comment on OpenAPI breaking changes |

### Not Recommended

| Tool | Reason |
|------|--------|
| Testim / Mabl | Enterprise platforms; overlap with Playwright + AI at higher cost and lower control |
| Applitools | Chromatic provides 80% value for component testing at lower cost |
| EvoSuite / Diffblue Cover | Java only |
| Pynguin | Research-grade; vacuous assertions; limited async support |

---

## 8. Implementation Sequence

### Phase 1: Foundation (1 session)
1. Fix dependency gap in `requirements-test.txt` (WI-1494)
2. Raise CI coverage gate from 70% to 75% (WI-1495)
3. Add Playwright MCP to `.mcp.json` (WI-1496)
4. Run Schemathesis against live staging; record findings (WI-1497)

### Phase 2: Quality Gates (1–2 sessions)
5. Design + implement mutation score tracking in quality dashboard (WI-1498)
6. Expand Hypothesis property tests to new invariants (WI-1499)
7. Add CI failure artifact upload (WI-1500)

### Phase 3: UI Coverage (1–2 sessions)
8. Establish Storybook for widget components (new spec + WI)
9. Connect Chromatic for visual regression (new spec + WI)
10. Add accessibility testing to E2E suite (new spec + WI)

### Phase 4: Contracts & Safety (2–3 sessions)
11. Implement Pact contract testing — widget ↔ chat (new spec + WI)
12. Add CompaREST to PR pipeline (WI)
13. Add flaky test detection to nightly CI (WI)

### Phase 5: AI-Assisted Generation (ongoing)
14. Implement `generate-tests` Claude Code skill
15. Run Meta-pattern gated test generation on lowest-coverage modules

---

## 9. References

### Academic Papers
- Meta TestGen-LLM (FSE 2024): arXiv:2402.09171
- Mind the Gap — Oracle Gap: arXiv:2309.02395
- Coverage-guided LLM generation: arXiv:2602.21997
- Gemini 2.5 Pro test generation benchmark: arXiv:2507.14256

### Tool Documentation
- Playwright Python: playwright.dev/python/docs/intro
- Playwright MCP: github.com/microsoft/playwright-mcp
- Schemathesis: schemathesis.readthedocs.io
- Hypothesis: hypothesis.readthedocs.io
- mutmut: mutmut.readthedocs.io
- Chromatic: chromatic.com
- Storybook: storybook.js.org/docs
- Pact: docs.pact.io
- CompaREST: github.com/typeable/compaREST
- axe-playwright-python: github.com/nicolo-ribaudo/axe-playwright-python

### Project-Internal References
- SPEC-1838: Quality score dashboard (implemented)
- SPEC-1839: Schemathesis API fuzzing (implemented — in-process; staging TBD)
- SPEC-1842: Mutation testing with mutmut (implemented — runner exists; dashboard TBD)
- SPEC-1843: Property-based testing with Hypothesis (implemented — 46 tests; expansion TBD)
- SPEC-1844: Line coverage enforcement (implemented)
- GOV-03: Every test must produce unambiguous PASS/FAIL
- GOV-17: Quality first — prioritize quality over effort
- GOV-18: Assertion quality — meaningfulness over coverage; no rubber-stamp assertions

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Revised: S202 (2026-03-17). For implementation: create KB work items before coding.*
