# Testing Infrastructure Proposal: Automated Quality & Completeness
### Agent Red Customer Experience — Implementation Proposal
**Authored:** S201 (2026-03-17)
**Status:** Proposal — awaiting owner prioritization
**Audience:** Claude Code (fresh session) + Owner

---

> **How to use this document:** This is a self-contained implementation guide. Read it top-to-bottom in a fresh session. Each section maps to actionable work items. The proposal is sequenced by ROI: § 3 (immediate, high-leverage) → § 4 (medium-term quality) → § 5 (long-term maturity). Every recommendation includes the KB spec it implements or should generate.

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
| E2E (mocked) | ~24 files | Playwright | Vite dev server + API mocking |
| E2E (live) | ~30 files | Playwright | Real staging environment |
| Visual | ~4 files | Playwright | Widget iframe, Vite port 3100 |
| Security | ~11 files | pytest | Adversarial, penetration |
| Performance | ~5 files | Locust | Load testing |
| Property-based | ~5 files | Hypothesis | Partially implemented |
| Regression | ~3 files | pytest | Tier 0/1/2 blocking gates |
| **TOTAL** | **~399 files** | | **~244,329 lines of test code** |

**Test execution infrastructure:**
- `scripts/run-tests-thermal-safe.ps1` — Windows-native batched execution with thermal cooling pauses
- `scripts/test_pipeline.py` — 18-phase PLAN-001 autonomous pipeline (E2E, live, fuzzing, property)
- `.github/workflows/python-tests.yml` — 5 parallel shards × 2 Python versions (3.12, 3.13)
- Coverage target: 75% line (currently ~73%; ramp plan to 80%)

**Recent numbers (S200):**
- 6,920 tests passing (unit + multi_tenant + chat + integrations)
- E2E pipeline: 1,039/1,050 passed (11 UI selector failures, no code defects)
- 46/46 regression tests passed

### 1.2 Critical Gaps

These gaps were identified by codebase inspection and must be addressed:

**Dependency gaps (missing from `requirements-test.txt`):**
```
playwright      # imported by 50+ test files — critical
hypothesis      # tests/property/ uses @given
schemathesis    # Phase 17 of test_pipeline.py — not installed
mutmut          # SPEC-1842 mutation testing — not installed
```

**UI testing gaps:**
- No visual regression baseline / snapshot comparison system
- Shadow DOM launcher inaccessible to Playwright assertions
- No cross-browser testing (Firefox, Safari/WebKit)
- No screenshot/video capture on test failure
- `tests/widget/` files are NOT browser-automation tests (use httpx, not Playwright)
- No accessibility (a11y) testing
- No Storybook / component workbench for the React widget

**Quality metric gaps:**
- Coverage is measured as line coverage, not branch coverage (branch reveals 2x more defects)
- No mutation score tracking (the "oracle gap" — see § 2.4)
- No contract testing (widget ↔ chat API)
- No OpenAPI diff gate on PRs

**CI/CD gaps:**
- E2E tests not in CI pipeline (staging access only — reasonable but undocumented)
- No post-failure artifact uploads (screenshots, traces, Playwright HTML report)
- No flaky test detection or smart retry

---

## 2. Research Foundation

### 2.1 Industry Consensus: The Testing Pyramid

The most established model (Google, Martin Fowler) recommends:
- **70% unit tests** — fast, isolated, cheap to write
- **20% integration tests** — real dependencies (DB, Redis, APIs), no mocking
- **10% end-to-end tests** — browser automation, full stack

This project's distribution is approximately: 55% unit+multi_tenant / 35% integration+chat / 10% E2E. This is reasonable but the integration layer (Cosmos, Redis) relies heavily on mocking, which carries the risk of mock-production divergence. The **Spotify Honeycomb model** (designed for microservices) inverts this and prefers integration tests with real dependencies — relevant for the Cosmos and Redis-backed features.

**Key insight from Google Testing Blog (March 2026):** "The Way of TDD" — empirical research confirms TDD improves coverage, reduces defect rates, and increases developer confidence. The project's spec-first workflow (GOV-01) is structurally aligned with TDD.

### 2.2 AI-Assisted Test Generation

**Meta's TestGen-LLM approach (FSE 2024, arXiv:2402.09171):**
The most rigorous industrial validation of LLM test generation. Key findings:
- 75% of generated tests compile
- 57% reliably pass
- 25% increase in coverage in successful cases
- 73% engineer acceptance rate
- **Critical gate:** Only promote generated tests that demonstrably increase branch coverage over the baseline. Reject others.

**Coverage-guided iterative generation (arXiv:2602.21997, Feb 2026):**
Remove already-covered code segments from the LLM's context iteratively. This forces the LLM to focus on uncovered branches. Outperforms one-shot generation on complex methods.

**Gemini 2.5 Pro benchmark (arXiv:2507.14256, July 2025):**
96.3% branch coverage and 57% mutation score achieved with chain-of-thought prompting + docstrings. Context quality (documentation) matters more than context quantity.

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

### 2.3 Web UI Testing: State of the Art (2025-2026)

**Playwright v1.58.0 (January 30, 2026) — the current standard:**

Key features released in 2025-2026 that are directly actionable:

1. **Playwright Test Agents** (v1.56, October 2024):
   Three Claude-aware agents operating in a loop:
   - `planner` — explores the app, produces a Markdown test plan
   - `generator` — transforms the plan into `.spec.ts` test files
   - `healer` — runs tests, auto-repairs selector failures

   Initialize: `npx playwright init-agents --loop=claude`

   This is the mechanism to generate regression coverage for the 9 Control Plane SPA pages without manual test authoring.

2. **Playwright MCP Server** (github.com/microsoft/playwright-mcp):
   Exposes browser automation to Claude via Model Context Protocol. Uses the accessibility tree (not screenshots) — structured, low token cost, deterministic. Claude can navigate the Provider Console, fill forms, assert outcomes — all from within a Claude Code session.

   Capabilities: navigate, click, fill, drag, upload, handle dialogs, capture network requests, take screenshots, manage tabs.

   **Use case:** Exploratory testing of new SPA pages during development sessions. No test file written first.

3. **Chrome for Testing builds** (v1.57):
   Uses Chrome for Testing instead of Chromium, providing more authentic browser behavior for production testing.

4. **Timeline visualization** (v1.58):
   HTML reports with merged test results and per-test execution timeline. Essential for CI debugging.

**Chromatic + Storybook — visual regression:**
- Storybook creates a component workbench for `widget/src/components/`
- Every component story becomes a visual test: render → snapshot → diff
- Chromatic runs tests across 4 browsers (Chrome, Safari, Firefox, Edge)
- Free tier available; 90-second CI setup
- Used by GitHub, Vercel, Square, Adobe, BBC
- The `MessageBubble.tsx` and `MessageList.tsx` components are prime candidates

**Testim and Mabl** (enterprise AI testing platforms):
Both offer agentic test creation, self-healing locators, and root cause analysis. High cost; overlap with Playwright + AI agents at lower engineering control. **Not recommended** for an engineering-first team with existing Playwright expertise.

**Applitools** (visual AI testing):
Enterprise-scale visual + GenAI testing across browsers and devices. Claims 9x faster test creation, 4x less maintenance. ISO 27001 + SOC 2 Type II. Pricing by contact only. **Chromatic provides 80% of value at lower cost** for component-level visual testing.

### 2.4 The Oracle Gap: Why Mutation Testing Matters

**Paper:** "Mind the Gap: Coverage vs Mutation Score" (arXiv:2309.02395, 2023)

The **oracle gap** is the disparity between high code coverage and low mutation score. A file with 95% branch coverage and 30% mutation score has tests that *execute* the code but do not *assert* meaningful outcomes. These are the rubber-stamp assertions that GOV-18 prohibits.

**Example oracle gap scenario:**
```python
def compute_rate_limit(tier: str) -> int:
    if tier == "starter":
        return 10
    return 300

# High-coverage, low-mutation-score test:
def test_rate_limit():
    result = compute_rate_limit("starter")
    assert result is not None  # ← PASSES but misses the wrong value defect

# Mutation-killing test:
def test_rate_limit():
    assert compute_rate_limit("starter") == 10
    assert compute_rate_limit("professional") == 300
    assert compute_rate_limit("enterprise") == 300
```

Mutation testing runs modified copies of the code (mutants) through the test suite. If a test suite doesn't kill a mutant (i.e., passes when the code is wrong), that's a surviving mutant — a sign of a weak oracle.

**Key modules to prioritize for mutation testing:**
- `src/multi_tenant/middleware.py` — tenant isolation logic
- `src/multi_tenant/api_key_audit.py` — security-critical
- `src/multi_tenant/idle_tenant_detection.py` — business logic
- `src/multi_tenant/log_retention.py` — compliance-critical
- `src/chat/endpoints.py` — core product path

### 2.5 API Fuzzing at Scale

**Schemathesis** is used in production by Netflix, SAP, Red Hat, IBM, and JetBrains. A single command:
```bash
uvx schemathesis run https://staging-url/openapi.json \
  --auth-type=apikey --auth="ar_spa_plat_..." \
  --checks=all \
  --stateful=links \
  --junit-xml=fuzzing-results.xml
```

The `--stateful=links` flag enables sequential API call testing (create → read → update → delete chains), which catches stateful bugs invisible to single-call testing.

**Expected yield:** 5–15 real edge-case bugs on first run against the 39 Control Plane endpoints.

Schemathesis directly implements SPEC-1839 (API fuzzing).

### 2.6 Property-Based Testing Patterns

**Hypothesis** (v6.151.9) generates hundreds of test inputs from a specification:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=500))
async def test_chat_message_any_content(content):
    """Any valid message content must return 200 or 422, never 500."""
    response = await client.post("/chat", json={"message": content, "tenant_id": "t1"})
    assert response.status_code in (200, 422)  # Never 500
```

**Key invariants to test with Hypothesis:**
1. Any tenant_id pair has non-overlapping data (tenant isolation invariant)
2. Rate limit invariants: floor (10 RPM) ≤ effective limit ≤ cap (300 RPM) for all inputs
3. All valid Pydantic model shapes parse without error
4. All valid API key formats authenticate successfully
5. Log retention cutoff is always in the past for all valid retention-days values

**Stateful testing** with `RuleBasedStateMachine` models the allowed state transitions of the chat system and checks that invariants hold across all reachable states.

### 2.7 Contract Testing

**Pact** (docs.pact.io) implements Consumer-Driven Contract Testing:
- The widget (consumer) generates a contract during its tests: "I send messages in shape X and expect responses in shape Y"
- The FastAPI chat endpoint (provider) verifies it satisfies the contract
- If the backend changes the response shape, Pact catches the break before deployment — no full integration environment needed

The Shopify widget ↔ chat endpoint is the highest-value contract to test. The widget's `transport/http.ts` defines the exact API calls made.

### 2.8 OpenAPI Breaking Change Detection

**CompaREST** (github.com/typeable/compaREST):
- Detects breaking vs non-breaking changes between two OpenAPI specifications
- GitHub Actions integration: auto-comments on PRs with a compatibility assessment
- Output: markdown/HTML reports with JSONPath-pinpointed changes
- Prevents accidental breaking changes to the 39 Control Plane endpoints as the API evolves

---

## 3. Immediate Actions (High ROI, Low Effort)

### 3.1 Fix the Dependency Gap [1 hour]

Add to `requirements-test.txt`:
```
playwright>=1.58.0
hypothesis>=6.151.0
schemathesis>=3.39.0
mutmut>=2.4.4
pytest-playwright>=0.5.0
axe-playwright-python>=0.1.4
```

Run:
```bash
pip install -r requirements-test.txt
playwright install chromium
playwright install-deps
```

**KB action:** Create WI for this if not already tracked. It unblocks Phases 17 and 18 of `test_pipeline.py`.

### 3.2 Switch to Branch Coverage [30 minutes]

In `pyproject.toml`, change:
```toml
[tool.coverage.run]
branch = true   # Add this line
source = ["src"]
```

In CI (`.github/workflows/python-tests.yml`), change the coverage gate:
```yaml
--cov-fail-under=80  # was 70%, branch coverage is stricter
```

**Rationale:** Branch coverage catches twice as many defects as line coverage. Switching to branch coverage with the same numeric threshold (75-80%) is the single highest-leverage quality improvement with near-zero implementation cost.

### 3.3 Playwright MCP Server in Claude Code Sessions [2 hours]

Enable the Playwright MCP server for use during development and exploratory testing:

```json
// .mcp.json (project-level MCP config)
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

Once enabled, Claude Code can navigate the Provider Console, interact with the 9 Control Plane pages, and assert behaviors — all from within the conversation. This makes exploratory testing a first-class activity during development sessions.

**Use it for:** Verifying new SPA pages as they're built, smoke-testing after deployments, generating Playwright test plans for new UI features.

### 3.4 Schemathesis Against Staging [2 hours]

Run immediately against the staging environment. This requires no code changes:

```bash
# Against staging (read-only checks first)
uvx schemathesis run \
  https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/openapi.json \
  --auth-type=apikey \
  --auth="ar_spa_plat_ukgY1GK594QUxICKJfIXFWiNrWxnkhvB" \
  --checks=all \
  --exclude-checks=not_a_server_error \
  --junit-xml=schemathesis-results.xml \
  --report=schemathesis-report.html
```

**Then add to `test_pipeline.py` Phase 17** (currently a placeholder):
```python
# Phase 17: API Fuzzing (Schemathesis)
result = subprocess.run([
    "uvx", "schemathesis", "run", f"{STAGING_FQDN}/openapi.json",
    "--auth-type=apikey", f"--auth={SPA_KEY}",
    "--checks=all",
    "--stateful=links",
    f"--junit-xml={RESULTS_DIR}/phase-17-schemathesis.xml"
], capture_output=True, timeout=300)
```

**KB actions:**
- Update SPEC-1839 (API fuzzing) implementation status
- Create WI for any bugs found

### 3.5 Playwright Test Agents for the SPA [4 hours]

The Playwright Test Agents system generates a regression suite for the 9 Control Plane pages without manual test authoring:

```bash
cd "e:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
npx playwright init-agents --loop=claude
```

The three-phase loop:
1. **Planner agent:** Explores the Provider Console, documents all 9 Control Plane pages, their forms, inputs, and expected behaviors
2. **Generator agent:** Transforms the plan into `.spec.ts` test files with selectors and assertions
3. **Healer agent:** Runs generated tests, auto-repairs selector failures

Run against a live staging instance or the Vite dev server (`npm run dev` in `widget/`).

**Expected output:** 30-60 new `.spec.ts` tests covering the Control Plane SPA. These become the baseline for UI regression testing on every release.

---

## 4. Medium-Term Quality Improvements

### 4.1 Mutation Testing on Business-Critical Modules [1-2 days]

**Setup `mutmut` in CI (nightly, not per-commit):**

```toml
# pyproject.toml (already has [tool.mutmut] section — verify it's correct)
[tool.mutmut]
paths_to_mutate = "src/multi_tenant/,src/chat/"
backup = false
runner = "python -m pytest tests/multi_tenant/ tests/chat/ -x --timeout=30"
tests_dir = "tests/"
```

**Run locally first:**
```bash
mutmut run --paths-to-mutate src/multi_tenant/api_key_audit.py
mutmut results
mutmut show <surviving_mutant_id>  # Inspect what tests don't cover
```

**Quality gate (warning, not failure, initially):**
```bash
# In CI nightly job
mutmut run --paths-to-mutate src/multi_tenant/ src/chat/
MUTATION_SCORE=$(mutmut results | grep "survived" | awk '{print $2}')
# Report to quality dashboard
python tools/knowledge-db/db.py record_mutation_score "$MUTATION_SCORE"
```

**Integration with `src/quality_metrics/`:** Extend `normalize.py` to accept mutation score as a quality dimension alongside line/branch coverage. Display in the quality dashboard (SPEC-1838).

**Target:** Identify the oracle gap files (high branch coverage, low mutation score). Write targeted assertion-strengthening tests for those files.

**KB actions:**
- Implement SPEC-1842 (mutation testing)
- Create WI for each oracle-gap file discovered

### 4.2 Hypothesis Property-Based Tests [2-3 days]

Complete the implementation of SPEC-1843. Key test cases:

```python
# tests/property/test_rate_limiting_invariants.py
from hypothesis import given, strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

@given(
    rpm=st.integers(min_value=0, max_value=10000),
    tier=st.sampled_from(["starter", "professional", "enterprise"])
)
def test_effective_rate_limit_is_within_bounds(rpm, tier):
    """Effective rate limit is always between floor and cap, regardless of input."""
    from src.multi_tenant.rate_limiting import compute_effective_limit
    result = compute_effective_limit(tier=tier, requested_rpm=rpm)
    assert 10 <= result <= 300, f"Rate limit {result} outside bounds [10, 300]"

@given(
    tenant_a=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))),
    tenant_b=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N")))
)
def test_tenant_isolation_invariant(tenant_a, tenant_b):
    """Any two distinct tenant IDs share no data."""
    if tenant_a == tenant_b:
        return  # Same tenant — not the isolation case
    # Assert data namespaces are non-overlapping
    key_a = build_redis_key(tenant_id=tenant_a, resource="session")
    key_b = build_redis_key(tenant_id=tenant_b, resource="session")
    assert key_a != key_b, "Tenant key collision"
    assert tenant_a not in key_b
    assert tenant_b not in key_a
```

**Log retention invariants** (directly maps to SPEC-1837):
```python
@given(retention_days=st.integers(min_value=1, max_value=3650))
def test_log_retention_cutoff_is_always_past(retention_days):
    """Computed cutoff is always in the past."""
    from src.multi_tenant.log_retention import compute_cutoff_date
    from datetime import datetime, timezone
    cutoff = compute_cutoff_date(retention_days=retention_days)
    assert cutoff < datetime.now(timezone.utc), "Cutoff must be in the past"
```

**KB actions:**
- Implement SPEC-1843 (property-based testing)
- Each invariant becomes a KB test record

### 4.3 Storybook + Chromatic for Widget Components [1-2 days]

**Install Storybook in `widget/`:**
```bash
cd widget
npx storybook@latest init --type react
# Select: Vite builder (already using Vite)
```

**Create stories for the key components:**
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
  args: { role: 'assistant', content: 'I can help you with that. What is your order number?' }
};

export const LongMessage: StoryObj = {
  args: {
    role: 'assistant',
    content: 'A'.repeat(500) // Tests overflow handling
  }
};
```

**Connect Chromatic:**
```bash
npx chromatic --project-token=<token> --build-script-name=build-storybook
```

**What this gives you:**
- Every component renders as a story (smoke test — fails if component crashes)
- Chromatic captures pixel-perfect snapshots across 4 browsers
- PR builds show visual diff with approval/rejection workflow
- Free tier covers development use; ~$149/mo for CI at scale

**KB actions:**
- Create SPEC for widget visual regression testing
- Create WI for Storybook setup
- Create WI for Chromatic CI integration

### 4.4 Accessibility Testing [1 day]

```bash
pip install axe-playwright-python
```

Add to E2E test conftest:
```python
# tests/e2e/conftest.py — add to page fixture
from axe_playwright_python.sync_playwright import Axe

@pytest.fixture
def page_with_a11y(page):
    axe = Axe()
    yield page
    # Run accessibility check after each test
    results = axe.run(page)
    violations = [v for v in results.violations if v['impact'] in ('critical', 'serious')]
    assert len(violations) == 0, f"Accessibility violations: {violations}"
```

**WCAG 2.1 AA compliance** is the standard for SaaS products. Critical violations (keyboard navigation, ARIA, color contrast) block users with disabilities. The Provider Console's 29 pages should all pass a11y checks.

### 4.5 Screenshot and Trace on Failure [2 hours]

Add to `tests/e2e/conftest.py` and `tests/e2e_live/conftest.py`:
```python
@pytest.fixture
def page(playwright_fixture):
    page = playwright_fixture.chromium.launch(headless=True).new_page()
    yield page
    # On test failure, capture artifacts
    if pytest.current_test_failed():
        page.screenshot(path=f"test-artifacts/{pytest.current_test_name()}.png", full_page=True)
        page.context.tracing.stop(path=f"test-artifacts/{pytest.current_test_name()}.zip")

# Run with:
# playwright install
# pytest --tracing=retain-on-failure --screenshot=only-on-failure --video=retain-on-failure
```

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

This makes CI E2E failures debuggable without local reproduction.

### 4.6 Pact Contract Testing for Widget ↔ Chat API [2-3 days]

Install:
```bash
pip install pact-python
npm install @pact-foundation/pact --save-dev
```

**Consumer side (TypeScript widget):**
```typescript
// widget/src/transport/http.test.ts
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
  // ... run the transport code
});
```

**Provider side (Python FastAPI):**
```python
# tests/contract/test_chat_provider.py
from pact import Verifier

def test_provider_satisfies_widget_contract():
    verifier = Verifier(
        provider='AgentRedChatAPI',
        provider_base_url='http://localhost:8000'
    )
    output, _ = verifier.verify_with_broker(
        broker_url='https://your-pact-broker',
        provider_version='1.91.0'
    )
    assert output == 0
```

**Value:** If `widget/src/transport/http.ts` changes the request shape, or `src/chat/endpoints.py` changes the response shape, Pact catches the contract break in CI before it reaches staging.

---

## 5. Long-Term Investments

### 5.1 Mutation Score Quality Dashboard Integration

Extend `src/quality_metrics/` (already tracking coverage) to include mutation scores:

```python
# src/quality_metrics/mutation_tracking.py

def parse_mutmut_results(mutmut_output: str) -> dict:
    """Parse mutmut results into structured data."""
    # Extract killed/survived/timeout counts
    ...

def compute_mutation_score(killed: int, survived: int, timeout: int) -> float:
    """Mutation score = killed / (killed + survived)."""
    total = killed + survived
    return killed / total if total > 0 else 0.0

def identify_oracle_gap_modules(
    coverage_data: dict, mutation_data: dict,
    coverage_threshold: float = 0.80,
    mutation_threshold: float = 0.50
) -> list[str]:
    """
    Identify modules with high coverage but low mutation score.
    These are the 'oracle gap' modules — tests that execute code but don't
    assert meaningful outcomes. See arXiv:2309.02395.
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

Display in the quality dashboard alongside the existing coverage metrics (SPEC-1838).

### 5.2 AI-Assisted Test Generation Workflow (Meta Pattern)

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

This implements the validated Meta production approach for this codebase. The key innovation: **test gating by coverage improvement**, not by human review alone.

### 5.3 CompaREST OpenAPI Breaking Change Detection

Add to `.github/workflows/python-tests.yml` for any PR touching `src/`:
```yaml
- name: Check OpenAPI compatibility
  if: github.event_name == 'pull_request'
  run: |
    # Generate OpenAPI schema from current branch
    python -c "from src.main import app; import json; print(json.dumps(app.openapi()))" > /tmp/new-schema.json
    # Download schema from main branch (or production)
    curl -s https://staging-url/openapi.json > /tmp/old-schema.json
    # Compare
    npx compaREST --output-format markdown /tmp/old-schema.json /tmp/new-schema.json \
      > /tmp/api-compat-report.md
    cat /tmp/api-compat-report.md
    # Post as PR comment (optional)
```

**Value:** Prevents accidental breaking changes to the 39 Control Plane endpoints. Breaking changes should be intentional and versioned.

### 5.4 Flaky Test Detection

Add flaky test detection to the CI pipeline:
```yaml
# .github/workflows/python-tests.yml
- name: Run tests with flakiness detection
  run: |
    pytest --count=3 --randomly-seed=12345 tests/regression/ \
      --junit-xml=flaky-detection.xml
  continue-on-error: true  # Don't fail the build; report flakiness
```

Track flaky test occurrence in the KB as a test quality metric. A test that passes sometimes and fails sometimes is worse than a consistently failing test (it masks real defects).

### 5.5 Performance Benchmarking in E2E Tests

Add Core Web Vitals measurement to the Playwright E2E tests:
```python
# tests/e2e/test_performance_benchmarks.py
def test_provider_console_load_time(page):
    """Provider Console dashboard must load in under 3 seconds."""
    start = time.time()
    page.goto("/provider/dashboard")
    page.wait_for_load_state("networkidle")
    load_time = time.time() - start

    # Measure Core Web Vitals via JavaScript
    lcp = page.evaluate("""
        new Promise((resolve) => {
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                resolve(entries[entries.length - 1].startTime);
            }).observe({ type: 'largest-contentful-paint', buffered: true });
        })
    """)

    assert load_time < 3.0, f"Page load time {load_time:.2f}s exceeds 3s threshold"
    assert lcp < 2500, f"LCP {lcp}ms exceeds 2.5s threshold (Google's 'Good' threshold)"
```

---

## 6. KB Specifications and Work Items to Create

### New Specifications Needed

| Spec ID | Title | Priority | Implements |
|---------|-------|----------|-----------|
| New | Widget Visual Regression (Storybook + Chromatic) | High | § 4.3 |
| New | Playwright Test Agents SPA Coverage | High | § 3.5 |
| New | Accessibility Testing (WCAG 2.1 AA) | Medium | § 4.4 |
| New | Widget ↔ Chat Contract Testing (Pact) | Medium | § 4.6 |
| New | OpenAPI Breaking Change Detection (CompaREST) | Medium | § 5.3 |
| New | AI-Assisted Test Generation Workflow | Low | § 5.2 |
| SPEC-1839 | API Fuzzing (Schemathesis) | Critical | § 3.4 — implement this session |
| SPEC-1842 | Mutation Testing (mutmut) | High | § 4.1 — implement this session |
| SPEC-1843 | Property-Based Testing (Hypothesis) | High | § 4.2 — implement this session |

### Immediate Work Items

| WI | Description | Effort | Section |
|----|-------------|--------|---------|
| New | Add playwright, hypothesis, schemathesis, mutmut to requirements-test.txt | 30 min | § 3.1 |
| New | Enable branch coverage in pyproject.toml | 30 min | § 3.2 |
| New | Add Playwright MCP server to .mcp.json | 1 hour | § 3.3 |
| New | Run Schemathesis against staging 39 endpoints | 2 hours | § 3.4 |
| New | Run Playwright Test Agents against Provider Console | 4 hours | § 3.5 |
| New | Add screenshot/trace capture on E2E failure | 2 hours | § 4.5 |
| WI-1453 | OTEL exporter (SPEC-1834) | TBD | Pre-existing |
| WI-1454 | App Insights integration (SPEC-1834) | TBD | Pre-existing |

---

## 7. Tool Evaluation Summary

### Primary Recommendations

| Tool | Category | Priority | Cost | Notes |
|------|----------|----------|------|-------|
| **Playwright v1.58** | Browser automation | Critical | Free | Already in use; upgrade to latest, enable Test Agents |
| **Playwright MCP** | Exploratory testing | Critical | Free | Add to .mcp.json for Claude Code sessions |
| **Schemathesis** | API fuzzing | Critical | Free/OSS | One command against /openapi.json; implements SPEC-1839 |
| **Hypothesis v6** | Property-based testing | High | Free | Already planned; implement SPEC-1843 |
| **mutmut** | Mutation testing | High | Free | Run nightly on business-critical modules; implements SPEC-1842 |
| **coverage.py --branch** | Branch coverage | High | Free (in use) | Switch from line to branch; single config change |
| **Chromatic** | Visual regression | High | Free tier | Storybook integration for widget components |
| **Storybook** | Component workbench | High | Free | Widget/React component testing foundation |
| **axe-playwright-python** | Accessibility | Medium | Free | WCAG 2.1 AA compliance for Provider Console |
| **Qodo (CodiumAI)** | AI test generation | Medium | Free/paid | IDE plugin for incremental test authoring |
| **Pact** | Contract testing | Medium | Free/OSS | Widget ↔ Chat API contract |
| **CompaREST** | API compatibility | Low | Free/OSS | PR comment on OpenAPI breaking changes |

### Not Recommended

| Tool | Reason |
|------|--------|
| Testim / Mabl | Enterprise platforms; overlap with Playwright + AI at higher cost and lower control |
| Applitools | Chromatic provides 80% value for component testing at lower cost |
| EvoSuite / Diffblue Cover | Java only |
| Pynguin | Research-grade; vacuous assertions; limited async support |
| Symflower | Model benchmarking utility; not a direct test generator |

---

## 8. Implementation Sequence

### Phase 1: Foundation (1 session)
1. Fix dependency gap in `requirements-test.txt`
2. Enable branch coverage in CI (single config change)
3. Add Playwright MCP to `.mcp.json`
4. Run Schemathesis against staging; record findings as WIs
5. Implement SPEC-1839 Phase 17 in `test_pipeline.py`

### Phase 2: Quality Gates (1-2 sessions)
1. Implement SPEC-1843 (Hypothesis property-based tests)
2. Implement SPEC-1842 (mutmut nightly mutation testing)
3. Add screenshot/trace capture on E2E failure
4. Add E2E failure artifact upload to CI

### Phase 3: UI Coverage (1-2 sessions)
1. Run Playwright Test Agents against Provider Console SPA
2. Establish Storybook for widget components
3. Connect Chromatic for visual regression
4. Add accessibility testing to E2E suite

### Phase 4: Advanced Quality (2-3 sessions)
1. Implement Pact contract testing (widget ↔ chat)
2. Add CompaREST to PR pipeline
3. Extend quality dashboard with mutation score tracking
4. Implement oracle gap identification (`identify_oracle_gap_modules`)

### Phase 5: AI-Assisted Generation (ongoing)
1. Implement `generate-tests` Claude Code skill
2. Run Meta-pattern gated test generation on lowest-coverage modules
3. Track coverage improvement per generated test batch

---

## 9. References

### Academic Papers
- Meta TestGen-LLM (FSE 2024): https://arxiv.org/abs/2402.09171
- Mind the Gap — Oracle Gap: https://arxiv.org/abs/2309.02395
- Coverage-guided LLM generation: https://arxiv.org/abs/2602.21997
- Gemini 2.5 Pro test generation benchmark: https://arxiv.org/abs/2507.14256
- ChatUniTest: https://arxiv.org/abs/2305.04764
- SpecOps GUI Agent Testing: https://arxiv.org/abs/2603.10268
- Coverage-Guided Multi-Agent Fuzzing: https://arxiv.org/abs/2603.08616

### Tool Documentation
- Playwright Python: https://playwright.dev/python/docs/intro
- Playwright MCP: https://github.com/microsoft/playwright-mcp
- Playwright Test Agents: https://playwright.dev/docs/release-notes#version-156
- Schemathesis: https://schemathesis.readthedocs.io
- Hypothesis: https://hypothesis.readthedocs.io
- mutmut: https://mutmut.readthedocs.io
- Chromatic: https://www.chromatic.com
- Storybook: https://storybook.js.org/docs
- Pact: https://docs.pact.io
- CompaREST: https://github.com/typeable/compaREST
- axe-playwright-python: https://github.com/dequelabs/axe-playwright-python
- Qodo: https://qodo.ai

### Industry Standards
- Martin Fowler Testing: https://martinfowler.com/testing/
- Google Testing Blog: https://testing.googleblog.com
- Google Testing Pyramid: https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
- Spotify Honeycomb Model: https://engineering.atspotify.com/2018/01/testing-of-microservices/
- ISTQB Foundation Level v4.0: https://www.istqb.org

### Project-Internal References
- SPEC-1838: Quality score dashboard (implemented)
- SPEC-1839: Schemathesis API fuzzing (specified)
- SPEC-1840: Data normalization (implemented)
- SPEC-1841: Untested spec backfill (implemented)
- SPEC-1842: Mutation testing with mutmut (specified)
- SPEC-1843: Property-based testing with Hypothesis (specified)
- SPEC-1844: Line coverage enforcement (implemented)
- GOV-03: Every test must produce unambiguous PASS/FAIL
- GOV-17: Quality first — prioritize quality over effort
- GOV-18: Assertion quality — meaningfulness over coverage; no rubber-stamp assertions

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Generated: S201 (2026-03-17). For implementation: create KB work items before coding.*
