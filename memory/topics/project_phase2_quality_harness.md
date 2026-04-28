---
name: Phase 2 Quality Harness Plan
description: Approved external tool integrations for groundtruth-kb and agent-red, with production validation plan
type: project
---

Phase 2 of groundtruth-kb expands the development harness with external quality tools.

**Why:** Owner wants quantitative quality signals feeding into KB assertions before the production re-launch and beta customer onboarding. The extended harness will be exercised during the POR Steps 10-15 production recovery, then formally validated during a sustainment release cycle.

**How to apply:** All new tools are deterministic scanners producing SARIF/JSON/JUnit. AI tools (Copilot review, CodeRabbit) are advisory only — never canonical assertion sources. Use the `.quality/` manifest pattern for CI signal aggregation.

**Approved stack (2026-04-10):**

| Tool | Repo | Cost | Status |
|------|------|------|--------|
| Copilot Pro | Both | $10/mo | Active (trial) |
| CodeQL | groundtruth-kb | $0 | To enable |
| Semgrep | Both | $0 | To add to CI |
| Bandit | agent-red | $0 | To add to CI |
| pip-audit | Both | $0 | To add to CI |
| Docker Scout | agent-red | $0 | To add to CI |
| Dependabot | Both | $0 | To enable |
| SonarCloud | groundtruth-kb | $0 | To set up |
| CodeRabbit | groundtruth-kb | $0-15/mo | To pilot |
| GitHub MCP Server | Both | $0 | To add to .mcp.json |

**Validation plan (post-production-deploy):**
After production re-launch with beta customers, run a full release cycle that tests:
1. Sustainment procedures (non-disruptive upgrades)
2. Quantitative measurement of each tool's contribution (findings caught, false positive rate, time saved)
3. Whether the assertion-based quality gate model works in practice
