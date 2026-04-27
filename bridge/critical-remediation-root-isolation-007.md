NEW

# CRITICAL REMEDIATION — Phase E: Application-Boundary Audit

**Status:** NEW (audit; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Phase:** E (per `-006` execution sequencing; satisfies `-005` Codex F3 condition + Required Execution Order item 6)
**Scope:** classify every top-level entry in `E:\GT-KB\` as either GT-KB platform OR Agent Red application. Per Codex F3: classified Agent-Red items must move to `applications/Agent_Red/` in a follow-on bridge OR have evidence-backed platform classification.

---

## Audit method

For each top-level entry in `E:\GT-KB\`:

1. Inventory: name + type (file | directory).
2. Classification rule (from `-004` §2.6): "removing it would degrade Agent Red's customer-facing behavior or its commercial operation" → Agent Red. Otherwise GT-KB platform.
3. Evidence: brief justification (existing usage pattern, contained code purpose).
4. Disposition: KEEP (platform) | MOVE (to applications/Agent_Red/) | DELETE (stale/dead) | DEFER (needs deeper inspection).

## Audit results

### KEEP — GT-KB platform infrastructure (governance, framework, shared)

| Entry | Type | Justification |
|---|---|---|
| `.claude/` | dir | Claude Code harness configuration shared across all GT-KB work |
| `.codex/` | dir | Codex harness configuration shared |
| `.github/` | dir | GitHub Actions / repo metadata at GT-KB level |
| `.githooks/` | dir | Git hooks for the GT-KB repo |
| `.gitattributes`, `.gitignore`, `.dockerignore`, `.driveignore`, `.shopifyignore`, `.nojekyll` | files | Repo metadata |
| `.env.example`, `.env.integration.example` | files | Templates (not live env) |
| `.groundtruth/` | dir | GT-KB framework state |
| `.groundtruth-chroma/` | dir | KB ChromaDB embeddings (framework) |
| `.hypothesis/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` | dirs | Tool caches (general infra; gitignored) |
| `.mcp.json` | file | MCP config at GT-KB level |
| `.venv/` | dir | Python virtualenv (gitignored) |
| `.vscode/`, `.cursor/` (if present) | dirs | Editor config |
| `.wiki/` | dir | Wiki content (potentially Agent Red specific; defer) |
| `AGENTS.md` | file | Codex agent instructions at GT-KB level |
| `CLAUDE.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md` | files | Project instructions for Claude Code |
| `MEMBASE-4-CLAUDE.md` | file | Claude memory governance reference |
| `CONTRIBUTING.md`, `LICENSE`, `README.md`, `SECURITY.md` | files | Standard repo metadata |
| `CHANGELOG.md` | file | Repo changelog (currently mostly Agent Red; defer split) |
| `applications/` | dir | Application namespace (per directive) |
| `applications/Agent_Red/` | dir | Per directive — already established |
| `bridge/` | dir | Bridge protocol files (governance) |
| `docs/` | dir | Mixed (defer — see DEFER section below) |
| `groundtruth.db`, `groundtruth.db-shm`, `groundtruth.db-wal` (if present) | files | KB knowledge database (framework) |
| `groundtruth.db.corrupt-S311-...`, `groundtruth.db.pre-backfill-...` | files | KB backups; GT-KB platform state |
| `groundtruth.toml` | file | GT-KB framework config |
| `independent-progress-assessments/` | dir | Loyal Opposition (Codex) assessments — governance |
| `legal/` | dir | Legal docs (per CLAUDE-REFERENCE.md, project-level) |
| `logs/` | dir | Mixed; defer |
| `memory/` | dir | Operational memory (just migrated 104 files into here) |
| `pyproject.toml`, `requirements.txt`, `requirements-local.txt`, `requirements-test.txt`, `uv.lock` | files | Mixed (Agent Red app deps + GT-KB framework deps); defer split |
| `package.json`, `package-lock.json`, `package-pdf.json` | files | Mixed (npm deps for Agent Red UI + tooling); defer split |
| `node_modules/` | dir | npm deps; gitignored |
| `scripts/` | dir | Mixed (framework rehearsal + Agent Red operational); defer split |
| `tests/` | dir | Mixed; defer split |
| `tools/` | dir | Mixed; defer |

### MOVE — Agent Red application content (must move to `applications/Agent_Red/`)

| Entry | Type | Justification |
|---|---|---|
| `admin/` | dir | Agent Red admin UI (provider/standalone/shopify SPAs per CLAUDE.md) |
| `agent-red.wiki/` | dir | Agent Red documentation wiki |
| `assets/` | dir | Agent Red customer-facing assets |
| `branding/` | dir | Agent Red brand (logos, colors per CLAUDE.md "Brand color: #ff3621") |
| `config/` | dir | Likely Agent Red runtime config; verify at move-time |
| `docs-site/` | dir | Agent Red docs site (publishes to agentredcx.com per CLAUDE.md) |
| `drafts/` | dir | Likely Agent Red drafts; verify |
| `evaluation/` | dir | Agent Red technical evaluation work |
| `extensions/` | dir | Agent Red extensions |
| `img/` | dir | Agent Red images |
| `index.html`, `404.html`, `docs.html` | files | Agent Red GH-pages site root |
| `infrastructure/` | dir | Agent Red Azure IaC per CLAUDE.md (ACR, Cosmos, KV, Redis) |
| `output/` | dir | Likely Agent Red build output; verify |
| `pacts/` | dir | Agent Red contract tests (Pact) |
| `prototype/` | dir | Agent Red prototype |
| `src/` | dir | Agent Red main app source (`agents/`, `app/`, `chat/`, `integrations/`, `jobs/`, `migrations/` per earlier `ls`) |
| `test_host/` | dir | Agent Red test host containers |
| `widget/` | dir | Agent Red customer widget |
| `wiki/` | dir | Agent Red wiki (different from agent-red.wiki/ — verify) |
| `website/` | dir | Agent Red website |
| `Dockerfile`, `Dockerfile.test`, `Dockerfile.ui` | files | Agent Red container builds |
| `docker-compose.yml` | file | Agent Red compose |
| `shopify.app.toml` | file | Agent Red Shopify app config |
| `sitemap.xml` | file | Agent Red sitemap |
| `sonar-project.properties` | file | Agent Red SonarCloud config |
| `CNAME` | file | Agent Red DNS (agentredcx.com) |
| `Generate-PDF-Report.ps1`, `generate-pdf-*.{js,py,bat}`, `package-pdf.json` | files | Agent Red technical evaluation PDF tooling |
| `PDF-Generation-Instructions.md` | file | Same |
| `AgentRed-Technical-Evaluation-Report.docx`, `OrbaTech-Technical-Evaluation-Report.docx` | files | Agent Red evaluation reports |
| `PRODUCTION-READINESS-ASSESSMENT.md`, `PRODUCTION-READINESS-SUMMARY.txt` | files | Agent Red readiness docs |
| `prechat-form-phone-screenshot.png` | file | Agent Red UI screenshot |
| `vision.md` | file | Agent Red vision doc; verify if GT-KB shared |

### DELETE — stale / archive / temp (no GT-KB or Agent Red value)

| Entry | Type | Justification |
|---|---|---|
| `__pycache__/` | dir | Python bytecode cache; gitignored |
| `archive/` | dir | Pre-existing archive content; verify, retain only if useful |
| `C:UsersmichaAppDataLocalTempagentred-build-196/` | dir | **CORRUPTED PATH** — appears to be a literal-path-as-dirname from a malformed `mkdir`. Single quote stripping bug. SAFE to delete. |
| `nul` | file | Empty file from `> nul` redirect bug. SAFE to delete. |
| `tmp/`, `test-results/` | dirs | Likely temp/build output; gitignored |
| `tmp-provider-mock.{err.,}log`, `tmp-standalone-mock.{err.,}log` | files | Mock test logs |
| `_split_superadmin.py` | file | Loose script at root; should be in `scripts/` if active OR `archive/` if obsolete |

### DEFER — needs deeper inspection before classification

| Entry | Type | Reason |
|---|---|---|
| `docs/` | dir | Mixed (some GT-KB docs about IDP concept; some Agent Red product docs). Per CLAUDE.md `docs/gtkb-idp-concept.md` is GT-KB; need per-file split. |
| `wiki/` and `agent-red.wiki/` | dirs | Both exist; need to determine if duplicates or different content |
| `logs/` | dir | Operational logs; mixed origin |
| `tools/` | dir | Mixed; some KB tooling (`tools/knowledge-db/db.py` is GT-KB), some Agent Red |
| `scripts/` | dir | Heavy mixed: `scripts/rehearse/` is framework rehearsal; many other Agent Red operational scripts |
| `tests/` | dir | Mixed |
| `pyproject.toml`, `requirements*.txt`, `package.json` etc. | files | Mixed deps; package split is non-trivial |
| `infrastructure/` (re-classification) | dir | Currently MOVE; but if `infrastructure/agent-red-*` vs `infrastructure/gt-kb-*` split exists, keep platform parts |

## Phase 6b+ follow-on bridges (per Codex F3: must move, not just paperwork)

The MOVE classifications above represent multi-cluster structural migration. Per Codex F3, each must be tracked as a follow-on bridge:

| Sub-bridge | Scope |
|---|---|
| `bridge/agent-red-in-root-consolidation-src-001.md` | Move `src/`, `admin/`, `widget/`, `extensions/`, `prototype/` (Agent Red app code) |
| `bridge/agent-red-in-root-consolidation-content-001.md` | Move `assets/`, `branding/`, `img/`, `evaluation/`, `drafts/`, `agent-red.wiki/`, `docs-site/`, `website/`, `*.docx`, `*.html` (Agent Red customer-facing content) |
| `bridge/agent-red-in-root-consolidation-infra-001.md` | Move `infrastructure/`, `Dockerfile*`, `docker-compose.yml`, `pacts/`, `test_host/`, `shopify.app.toml`, `sonar-project.properties`, `CNAME`, `sitemap.xml` (Agent Red runtime/build infra) |
| `bridge/agent-red-in-root-consolidation-pdf-001.md` | Move `Generate-PDF-Report.ps1`, `generate-pdf-*`, `package-pdf.json`, `PDF-Generation-Instructions.md` (PDF tooling — may be Agent Red specific) |
| `bridge/agent-red-in-root-consolidation-readiness-001.md` | Move `PRODUCTION-READINESS-*`, `prechat-form-phone-screenshot.png`, `vision.md` (Agent Red docs/state) |
| `bridge/critical-remediation-deletion-cleanup-001.md` | DELETE entries above |
| `bridge/agent-red-in-root-consolidation-mixed-001.md` | DEFER entries: per-file audit + split for `docs/`, `wiki/`, `logs/`, `tools/`, `scripts/`, `tests/`, package files |

**Note:** these follow-on bridges are NEW work the owner authorizes by approving this audit. They are NOT scoped here as detailed implementation; this audit ESTABLISHES the migration program.

## Codex F3 condition acknowledgment

Per Codex `-005` F3: "Phase 6a must not become a paperwork-only endpoint. Every item classified as Agent Red application content must either be moved under `E:\GT-KB\applications\Agent_Red\` in a follow-on bridge or have a specific, evidence-backed platform classification."

This audit produces the classification + names the follow-on bridges for the moves. The MOVES themselves are the next program of work after this critical remediation closes. **Each MOVE entry above will land as a separate bridge thread to satisfy F3.**

## Risk + decision notes

- **Massive structural moves.** `src/` alone has ~9 subdirectories with hundreds of files. Each follow-on bridge will be substantial.
- **Build/deploy impact.** Moving `Dockerfile`, `pyproject.toml`, `package.json` etc. requires updating CI workflows (`.github/workflows/`), Dockerfile contexts, and any path references. Each follow-on bridge must include a CI-impact analysis.
- **Import path impact.** Moving `src/` would break `from src.X import Y` patterns across the codebase. Each follow-on bridge must include a grep+replace plan for import paths.
- **Owner driving in parallel.** Per `git status` from earlier this session, owner is making structural changes; coordination needed before follow-on bridges file.

## Decisions Needed From Owner

After Codex VERIFIED of this audit:

1. **Approve the classification.** Any entries that should be re-classified?
2. **Approve the follow-on bridge cluster split.** Combine/separate any clusters?
3. **Sequencing of follow-on bridges.** Which cluster ships first? Recommended: start with `pdf-001` (smallest, fewest dependencies) to validate the move pattern before tackling `src-001` (largest).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
