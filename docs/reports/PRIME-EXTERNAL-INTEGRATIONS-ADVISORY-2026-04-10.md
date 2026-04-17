# External AI & Quality Tool Integrations — Prime Builder Advisory Report

**Date:** 2026-04-10
**Author:** Prime Builder (Opus 4.6)
**Status:** Awaiting Codex parallel report for synthesis
**Scope:** GitHub Copilot, Docker Desktop AI, and external quality/testing tool integrations for groundtruth-kb and the Agent Red development harness

---

## Executive Summary

The groundtruth-kb assertion system can consume structured quality signals from external tools, turning it from a code governance system into a **full-spectrum quality governance platform**. The highest-value integrations produce machine-readable output (SARIF, JUnit XML, JSON) that maps directly to KB assertions.

**Three tiers of opportunity:**

1. **Immediate (this week):** GitHub MCP Server, Dependabot, Bandit, pip-audit, Semgrep — trivial setup, structured output, high governance value
2. **Near-term (this sprint):** SonarCloud, Copilot Code Review (automatic), Docker Scout in CI, CodeRabbit, Pyright
3. **Strategic (this month):** Copilot Coding Agent for WI automation, SARIF aggregation pipeline, Lighthouse CI, pytest-benchmark

---

## Category 1: GitHub Copilot Ecosystem

### 1.1 GitHub MCP Server — CRITICAL

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **Tools** | 51 tools (repos, issues, PRs, code security, reviews, notifications) |
| **Key capability** | Programmatic access to issues, PRs, code scanning alerts, and Copilot review from Claude Code |
| **Output format** | JSON (all tools) |
| **Integration effort** | Trivial (add to .mcp.json) |
| **Governance value** | ★★★★★ |
| **Recommendation** | **ADOPT IMMEDIATELY** |

**Why it matters:** Enables spec-to-implementation tracing (`search_issues` → match KB specs to GitHub issues), automated Copilot review requests (`request_copilot_review`), security alert monitoring (`list_code_scanning_alerts`), and PR management — all from within the Claude Code session.

### 1.2 Copilot Code Review (Automatic) — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA (agentic architecture, March 2026) |
| **Trigger** | Branch ruleset auto-request, CLI (`gh pr edit --add-reviewer copilot`), MCP (`request_copilot_review`) |
| **Output** | PR review comments (JSON via REST API) |
| **Integration effort** | Trivial (branch rule config) |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT** — configure auto-review on develop branch |

### 1.3 Copilot Coding Agent — STRATEGIC

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA (March 2026) |
| **Trigger** | Assign GitHub issue to Copilot (UI or API) |
| **Output** | PRs, commits, Actions logs (all via GitHub API) |
| **Integration effort** | Moderate |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **EVALUATE** — could automate WI implementation by assigning KB work items as issues |

### 1.4 Copilot Autofix (Code Scanning) — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA + REST API preview |
| **Output** | JSON (alert details, fix suggestions, commit status) |
| **Integration effort** | Trivial |
| **Governance value** | ★★★★★ |
| **Recommendation** | **ADOPT** — enable CodeQL + Autofix; track alert counts as assertions |

### 1.5 GitHub Actions AI Inference — MODERATE VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **What it does** | Invoke LLMs in CI steps (OpenAI, Meta, DeepSeek via GitHub Models) |
| **Output** | Step outputs (text/JSON) |
| **Integration effort** | Trivial |
| **Governance value** | ★★★☆☆ |
| **Recommendation** | **EVALUATE** — custom spec-conformance checks or test-gap analysis in CI |

### 1.6 GitHub Desktop — NO VALUE

Interactive commit message suggestions only. No API, no automation. **Skip.**

---

## Category 2: Docker Desktop AI

### 2.1 Docker Scout — CRITICAL

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **CLI** | `docker scout cves`, `docker scout sbom`, `docker scout quickview` |
| **Output** | **JSON, SARIF, SPDX, CycloneDX** |
| **GitHub Action** | `docker/scout-action` (PR comments, SARIF upload, policy gates) |
| **Integration effort** | Trivial (CLI in CI step) |
| **Governance value** | ★★★★★ |
| **Recommendation** | **ADOPT IMMEDIATELY** — vulnerability gate + SBOM generation + supply chain policy |

**Assertion examples:**
- `scout_critical_cves == 0`
- `scout_policy_no_high_profile_vulns == "passed"`
- `sbom_generated == true`

### 2.2 Docker Hub MCP Server — MODERATE VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | Beta |
| **Governance value** | ★★★☆☆ |
| **Recommendation** | **EVALUATE** — useful for image discovery, not critical |

### 2.3 Gordon (Ask Gordon) — LOW VALUE

Interactive conversational agent. No batch API. **Skip for governance.**

### 2.4 Docker MCP Catalog — MODERATE VALUE

270+ MCP servers discoverable. Container isolation for MCP server execution. Useful as a discovery mechanism. **Keep as reference.**

### 2.5 Testcontainers — MODERATE VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **Governance value** | ★★★☆☆ |
| **Recommendation** | **EVALUATE** — useful for integration testing infrastructure (Cosmos emulator, Redis) |

---

## Category 3: Static Analysis & Security

### 3.1 Semgrep — CRITICAL

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **Output** | **SARIF, JSON, JUnit XML** |
| **MCP server** | **Yes (official, built into CLI)** |
| **Integration effort** | Trivial |
| **Governance value** | ★★★★★ |
| **Recommendation** | **ADOPT IMMEDIATELY** |

**Why it matters:** Custom YAML rules can encode architectural governance: "all files must have copyright", "no direct DB access outside repository layer", "no UPDATE/DELETE on KB tables." The MCP server means Claude Code can run security scans during development.

### 3.2 SonarCloud — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **Output** | **SARIF**, JSON API |
| **MCP server** | **Yes (official)** |
| **Quality Gate** | Built-in pass/fail gate → maps to KB assertions |
| **Integration effort** | Moderate |
| **Governance value** | ★★★★★ |
| **Recommendation** | **ADOPT** — Quality Gate concept is a natural KB assertion source |

### 3.3 Bandit — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA (PyCQA) |
| **Output** | **JSON, SARIF** |
| **Integration effort** | Trivial |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT IMMEDIATELY** — Python-specific security, zero cost |

### 3.4 Pyright — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **Output** | JSON |
| **Integration effort** | Moderate |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT** — start with `basic` checking level |

---

## Category 4: Dependency & Supply Chain

### 4.1 Dependabot — CRITICAL

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA (built into GitHub) |
| **Integration effort** | Trivial (5-minute config) |
| **Governance value** | ★★★★★ |
| **Recommendation** | **ADOPT IMMEDIATELY** |

### 4.2 pip-audit — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA (PyPA) |
| **Output** | JSON, **CycloneDX SBOM** |
| **Integration effort** | Trivial |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT** — CycloneDX SBOM output increasingly required for enterprise customers |

---

## Category 5: Code Review (AI-Powered)

### 5.1 CodeRabbit — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **MCP server** | **Yes (official)** |
| **Integration effort** | Trivial (GitHub App) |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT** — already available as Claude Code plugin |

### 5.2 Codacy — MODERATE VALUE

| Attribute | Value |
|-----------|-------|
| **Maturity** | GA |
| **MCP server** | **Yes (official)** |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **EVALUATE** — overlaps with SonarCloud; MCP server is the differentiator |

---

## Category 6: Performance & Frontend

### 6.1 Lighthouse CI — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Output** | JSON, JUnit XML assertions |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT** (for React admin SPAs and docs site) |

### 6.2 pytest-benchmark — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Output** | JSON |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT** — critical-path performance regression detection |

### 6.3 axe-core (via Playwright) — HIGH VALUE

| Attribute | Value |
|-----------|-------|
| **Output** | JSON |
| **Governance value** | ★★★★☆ |
| **Recommendation** | **ADOPT** — WCAG compliance via existing Playwright infrastructure |

---

## Category 7: Documentation Quality

### 7.1 Spectral / Redocly — MODERATE VALUE

| Attribute | Value |
|-----------|-------|
| **Output** | JSON, JUnit |
| **Governance value** | ★★★☆☆ |
| **Recommendation** | **ADOPT** — OpenAPI spec linting in CI |

---

## The Integration Architecture

```
┌─────────────────────────────────────────────────────┐
│                  CI/CD Pipeline                      │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Semgrep  │ │ Bandit   │ │ Scout    │ │ pytest │ │
│  │ (SARIF)  │ │ (SARIF)  │ │ (JSON)   │ │(JUnit) │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│       │             │            │            │      │
│       └─────────────┴────────────┴────────────┘      │
│                         │                            │
│              ┌──────────▼──────────┐                 │
│              │  SARIF/JSON/JUnit   │                 │
│              │    Aggregator       │                 │
│              │  (GH Actions step)  │                 │
│              └──────────┬──────────┘                 │
│                         │                            │
│              ┌──────────▼──────────┐                 │
│              │  groundtruth-kb     │                 │
│              │  Assertion Recorder │                 │
│              │  (gt assert --ci)   │                 │
│              └─────────────────────┘                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              Development Session (MCP)               │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ GitHub   │ │ Semgrep  │ │SonarQube │            │
│  │ MCP      │ │ MCP      │ │ MCP      │            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘            │
│       │             │            │                   │
│       └─────────────┴────────────┘                   │
│                     │                                │
│          ┌──────────▼──────────┐                     │
│          │    Claude Code      │                     │
│          │  (session context)  │                     │
│          └──────────┬──────────┘                     │
│                     │                                │
│          ┌──────────▼──────────┐                     │
│          │  groundtruth-kb     │                     │
│          │  (KB + assertions)  │                     │
│          └─────────────────────┘                     │
└─────────────────────────────────────────────────────┘
```

---

## Ranked Recommendations

### Tier 1: Adopt Immediately (this week, trivial effort)

| # | Tool | Category | Output | Assertion Example |
|---|------|----------|--------|-------------------|
| 1 | **GitHub MCP Server** | Platform | JSON (51 tools) | Issue-to-spec tracing, security alerts |
| 2 | **Dependabot** | Supply chain | Auto-PRs | `critical_dependency_vulns == 0` |
| 3 | **Bandit** | Python security | SARIF | `bandit_high_severity == 0` |
| 4 | **pip-audit** | Dependencies | JSON, SBOM | `pip_audit_critical == 0` |
| 5 | **Semgrep** | SAST + custom rules | SARIF + MCP | `semgrep_critical == 0` |
| 6 | **Docker Scout** | Container security | SARIF, JSON | `scout_critical_cves == 0` |

### Tier 2: Adopt This Sprint (moderate effort, high value)

| # | Tool | Category | Assertion Example |
|---|------|----------|-------------------|
| 7 | **SonarCloud** | Quality gate | `sonar_quality_gate == "passed"` |
| 8 | **Copilot Code Review** | AI review | `copilot_review_requested == true` |
| 9 | **CodeRabbit** | AI review + MCP | Review findings as context |
| 10 | **Pyright** | Type checking | `pyright_errors == 0` |
| 11 | **Copilot Autofix** | Security remediation | `autofix_pending == 0` |

### Tier 3: Adopt This Month (strategic value)

| # | Tool | Category | Assertion Example |
|---|------|----------|-------------------|
| 12 | **Copilot Coding Agent** | WI automation | Issue → PR automation |
| 13 | **Lighthouse CI** | Frontend perf | `lhci_performance >= 90` |
| 14 | **pytest-benchmark** | Backend perf | `benchmark_regression == false` |
| 15 | **axe-core** | Accessibility | `wcag_violations_critical == 0` |
| 16 | **SARIF aggregation pipeline** | Meta | Unified quality dashboard |

### Tier 4: Evaluate Later

| # | Tool | Why Later |
|---|------|-----------|
| 17 | Codacy | Overlaps SonarCloud; evaluate MCP server value |
| 18 | Copilot SDK | Preview; wait for GA |
| 19 | Chromatic/Percy | Needs Storybook adoption |
| 20 | GitHub Agentic Workflows | Technical preview |

---

## Key MCP Servers for the Dev Harness

| Server | Category | Maturity | Value |
|--------|----------|----------|-------|
| **GitHub MCP** (official) | Platform | GA | ★★★★★ |
| **Semgrep MCP** | Security | GA | ★★★★★ |
| **SonarQube MCP** | Quality | GA | ★★★★☆ |
| **CodeRabbit MCP** | Review | GA | ★★★★☆ |
| **Codacy MCP** | Quality | GA | ★★★☆☆ |
| **Docker Hub MCP** | Containers | Beta | ★★★☆☆ |

---

## groundtruth-kb Integration Pattern

The key architectural insight: **assertions are assertions regardless of source.** The existing `gt assert` system can be extended with a new assertion operator (e.g., `ci_signal`) that reads structured output files from the CI pipeline:

```python
# New assertion type in groundtruth-kb
{
    "type": "ci_signal",
    "source": "sarif",
    "file": ".quality/semgrep-results.sarif",
    "metric": "critical_count",
    "operator": "==",
    "expected": 0
}
```

This turns every external tool into a governance signal without changing the KB's core architecture.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
