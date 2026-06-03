<!--
GTKB-STARTUP-REFRACTOR-001 Slice A (WI-4268). Role-capability manifest.
Authority: GOV-SESSION-SELF-INITIALIZATION-001;
bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md (GO).
Covers advisory STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02 finding F8
(skills/commands/agents installed but no role-capability manifest). Companion to
config/agent-control/SESSION-STARTUP-CONTROL-MAP.md.
-->

# Role-Capability Manifest

Answers, at startup, "which capabilities are installed and expected to work for
this role?" (advisory F8). Grouped by the role that primarily uses each
capability: **Prime Builder**, **Loyal Opposition**, **Shared** (both roles),
and **Owner-Gated** (destructive / deploy / credential / data capabilities that
require explicit owner authorization before use). Inventory of *where these load*
is in `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`.

Skills are repo-tracked under `.claude/skills/<name>/SKILL.md`; agents under
`.claude/agents/<name>.md`; commands under `.claude/commands/<name>.md`.
Marketplace/plugin skills available in the runtime are noted under Shared.

## Prime Builder

Implementation, KB mutation, proposal authoring, and session-wrap capabilities.

| Capability | Kind | Notes / verification |
|---|---|---|
| `gtkb-propose` | skill | Scaffold a gate-compliant bridge proposal body before filing. |
| `bridge-propose` | skill | Governed bridge-propose writer (credential scan + INDEX insert). |
| `send-review` | skill | Create an implementation proposal for Loyal Opposition review. |
| `kb-spec` / `kb-adr` / `kb-work-item` | skill | Create/update specifications, ADRs, work items in MemBase. |
| `kb-promote` / `kb-batch` | skill | Promote spec status / batch KB ops (dry-run + GOV-15 gate). |
| `spec-intake` / `decision-capture` | skill | Capture requirements / owner decisions into KB + DA. |
| `kb-session-wrap` | skill | Prime Builder 5-phase session wrap. |
| `run-tests` | skill | Execute test suites. |
| `assertion-triage` | skill | Categorize failing assertions (drift/noise/flaky/healthy). |
| `gtkb-hygiene-sweep` | skill | Orchestrate `gt hygiene sweep` + owner-gated remediation. |

## Loyal Opposition

Review, critique, verdict-authoring, and advisory capabilities.

| Capability | Kind | Notes / verification |
|---|---|---|
| `proposal-review` | skill | Review NEW/REVISED proposals; author GO/NO-GO. |
| `verify` | skill | Author VERIFIED/NO-GO post-implementation verdicts. |
| `code-review-audit` | skill | Code-review audit pass. |
| `alternatives-investigation` | skill | Investigate alternative approaches for a proposal. |
| `lo-opportunity-radar` | skill | Bias review toward token-savings / automation opportunities. |
| `loyal-opposition-hygiene-assessment` | skill | Assess project hygiene without mutating files. |
| `codex-report` | skill | Generate a Loyal Opposition INSIGHTS report. |
| `code-reviewer` | agent | Confidence-filtered code-review agent. |
| `quick-review` | command | Run the code-reviewer agent on recent changes. |

## Shared

Capabilities both roles use; harness-agnostic.

| Capability | Kind | Notes / verification |
|---|---|---|
| `bridge` | skill | Full bridge protocol (file/scan/verdict/report/navigate). |
| `kb-query` | skill | Read-only MemBase queries. |
| `kb-assert` | skill | Run ADR/DCL architecture assertions. |
| `check-deliberations` | skill | Deliberation-archive health check. |
| `kb-session-wrap-scan` | skill | Read-only wrap-up scanner suite. |
| `arch-audit` | skill | Horizontal ADR/DCL compliance audit. |
| `structural-hygiene-review` | skill | Review structure/naming/authority drift. |
| `harness-parity-review` | skill | Review Claude/Codex harness parity. |
| `projects` | skill | MemBase-backed project lifecycle commands. |
| `gtkb-benchmarks` | skill | Read-only measurement benchmarks. |
| `grill-me-for-clarification` | skill | Structured owner clarification interview. |
| `check-db` / `open-items` | command | KB health check / open-work dashboard. |
| `security-analyzer` | agent | OWASP pattern-table security analysis. |
| `check-security` | command | Run the security-analyzer agent on a path. |
| Marketplace/plugin skills + MCP servers | runtime | Available per session (Browser, GitHub, Documents, Presentations, Spreadsheets; MCP servers). Not repo-tracked; presence is session-dependent. |

## Owner-Gated

Destructive, deployment, credential, or data capabilities that require explicit
owner authorization before use (per credential-safety + deploy/release gates).

| Capability | Kind | Notes / verification |
|---|---|---|
| `deploy` | skill | Deployment operations — GOV-16 deploy-gate; owner approval required. |
| `release-candidate-gate` | skill | Non-deploying RC gate; precedes any deploy decision. |
| `seed-tenant` | skill | Seed tenant data — data-mutating; owner-gated. |
| `refresh-creds` | command | Refresh test credentials from Azure Key Vault — credential-handling; owner-gated. |
| `preflight` | command | Pre-deployment checklist against staging/production — owner-gated. |

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
