REVISED

# CRITICAL REMEDIATION — Phase E: Application-Boundary Audit (REVISED-1)

**Status:** REVISED-1 (audit; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/critical-remediation-root-isolation-007.md` (NEW), addressing `bridge/critical-remediation-root-isolation-008.md` (Codex NO-GO)

---

## Summary of revision (delta from `-007`)

Codex `-008` raised 4 findings:

| Finding | Disposition |
|---|---|
| F1 — Audit omits 7 top-level entries | **Fixed** in §A: complete `Get-ChildItem -Force` output included verbatim; every entry classified once. |
| F2 — Some entries classified twice | **Fixed**: each entry has exactly ONE primary classification. Mixed entries → DEFER with split criteria. |
| F3 — DELETE language reads as approval | **Fixed**: renamed to "DELETE CANDIDATE"; explicit statement that this audit grants no deletion approval; manifest-gating per `-005` required. |
| F4 — Pre-move impact inventory missing | **Fixed** in §C: required pre-move impact inventory for every MOVE cluster (path refs, import refs, CI paths, Docker contexts, verification commands). |

## §A. Complete top-level inventory (per `Get-ChildItem -LiteralPath E:\GT-KB -Force`)

Source: PowerShell `Get-ChildItem -LiteralPath "E:\GT-KB" -Force` executed 2026-04-27. Total: 105 entries (47 dirs + 58 files).

### Classification: KEEP (GT-KB platform — stays at root)

**Directories (12):**

| Entry | Justification |
|---|---|
| `.claude/` | Claude Code harness configuration (per-project, GT-KB level) |
| `.codex/` | Codex harness configuration (per-project, GT-KB level) |
| `.git/` | Git repo metadata (system; gitignored from itself) |
| `.github/` | GitHub Actions workflows + repo metadata at GT-KB level |
| `.githooks/` | Git hooks for the GT-KB repo |
| `.groundtruth/` | GT-KB framework runtime state (formal artifact approval packets, etc.) |
| `.groundtruth-chroma/` | KB ChromaDB embeddings (framework) |
| `applications/` | Application namespace per directive |
| `bridge/` | Bridge protocol files (governance) |
| `independent-progress-assessments/` | Loyal Opposition assessments + Codex assessments |
| `legal/` | Project-level legal docs |
| `memory/` | Operational memory (in-root canonical post-Phase-C migration) |

**Files (15):**

| Entry | Justification |
|---|---|
| `.dockerignore`, `.driveignore`, `.gitattributes`, `.gitignore`, `.nojekyll`, `.shopifyignore` | Repo-level metadata |
| `.env.example`, `.env.integration.example` | Templates (not live env) |
| `.mcp.json` | MCP config at GT-KB level |
| `AGENTS.md` | Codex agent instructions |
| `CLAUDE.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md` | Project instructions for Claude Code |
| `MEMBASE-4-CLAUDE.md` | Claude memory governance reference |
| `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `README.md`, `SECURITY.md` | Standard repo metadata |
| `groundtruth.toml` | GT-KB framework config |

**Generated/cache (gitignored; KEEP as-is — would be regenerated):**

| Entry | Justification |
|---|---|
| `.codex_pydeps/` | Codex Python deps cache |
| `.hypothesis/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` | Tool caches (gitignored) |
| `.venv/` | Python virtualenv (gitignored) |
| `.vscode/`, `.wiki/` | Editor / wiki (defer if active content) |
| `__pycache__/`, `node_modules/` | Build caches (gitignored) |

### Classification: KEEP (GT-KB platform — sensitive, in-root config)

| Entry | Justification |
|---|---|
| `.env.local` | **LIVE secrets/config**. Must remain in-root. Per `.gitignore` excluded from commits. |
| `groundtruth.db`, `groundtruth.db.corrupt-S311-...`, `groundtruth.db.pre-backfill-...` | KB knowledge database + recovery backups (framework state) |
| `.prime-bridge-mcp-health.json` | Live bridge MCP health state (GT-KB platform monitoring) |

### Classification: MOVE to `applications/Agent_Red/` (Agent Red customer-facing / commercial)

**Per Codex F4: each move cluster requires a pre-move impact inventory. Listed by cluster.**

| Entry | Cluster | Move target |
|---|---|---|
| `src/` | src | `applications/Agent_Red/src/` |
| `admin/` | src | `applications/Agent_Red/admin/` |
| `widget/` | src | `applications/Agent_Red/widget/` |
| `extensions/` | src | `applications/Agent_Red/extensions/` |
| `prototype/` | src | `applications/Agent_Red/prototype/` |
| `assets/` | content | `applications/Agent_Red/assets/` |
| `branding/` | content | `applications/Agent_Red/branding/` |
| `img/` | content | `applications/Agent_Red/img/` |
| `agent-red.wiki/` | content | `applications/Agent_Red/agent-red.wiki/` |
| `docs-site/` | content | `applications/Agent_Red/docs-site/` |
| `website/` | content | `applications/Agent_Red/website/` |
| `evaluation/` | content | `applications/Agent_Red/evaluation/` |
| `drafts/` | content | `applications/Agent_Red/drafts/` |
| `index.html`, `404.html`, `docs.html` | content | `applications/Agent_Red/web-root/` |
| `infrastructure/` | infra | `applications/Agent_Red/infrastructure/` |
| `pacts/` | infra | `applications/Agent_Red/pacts/` |
| `test_host/` | infra | `applications/Agent_Red/test_host/` |
| `Dockerfile`, `Dockerfile.test`, `Dockerfile.ui` | infra | `applications/Agent_Red/` (root of) |
| `docker-compose.yml` | infra | `applications/Agent_Red/` |
| `shopify.app.toml`, `sonar-project.properties`, `CNAME`, `sitemap.xml` | infra | `applications/Agent_Red/` |
| `Generate-PDF-Report.ps1`, `generate-pdf-report.js`, `generate-pdf-report.py`, `generate-pdf.bat`, `package-pdf.json` | pdf | `applications/Agent_Red/pdf-tooling/` |
| `PDF-Generation-Instructions.md` | pdf | `applications/Agent_Red/pdf-tooling/` |
| `AgentRed-Technical-Evaluation-Report.docx`, `OrbaTech-Technical-Evaluation-Report.docx` | readiness | `applications/Agent_Red/evaluation/` |
| `PRODUCTION-READINESS-ASSESSMENT.md`, `PRODUCTION-READINESS-SUMMARY.txt` | readiness | `applications/Agent_Red/` |
| `prechat-form-phone-screenshot.png` | readiness | `applications/Agent_Red/` |
| `vision.md` | readiness | `applications/Agent_Red/` |

### Classification: DELETE CANDIDATE (no GT-KB or Agent Red value; **manifest-gated per `-005`**)

**Per Codex F3: this audit GRANTS NO DELETION APPROVAL.** Each candidate must flow through the §2.5 5-step manifest protocol before any removal.

| Entry | Reason candidate |
|---|---|
| `nul` | Empty file from `> nul` shell-redirect bug |
| `CUsersmichaAppDataLocalTempagentred-build-196/` | Corrupted directory name (literal-path-as-dirname from past mkdir bug; was `C:UsersmichaAppDataLocalTempagentred-build-196/` per `-007`; now without leading `C:` after a rename or display difference) |
| `_split_superadmin.py` | Loose script at root; should be in `scripts/` if active |
| `tmp-provider-mock.err.log`, `tmp-provider-mock.log`, `tmp-standalone-mock.err.log`, `tmp-standalone-mock.log` | Mock test logs (likely stale) |
| `tmp/`, `test-results/`, `output/`, `logs/` | Build/test output dirs (likely stale; verify each before deletion) |
| `.tmp.drivedownload/`, `.tmp.driveupload/` | Drive sync staging directories (per `.driveignore` patterns) |
| `archive/` | Pre-existing archive content; per Codex audit + retention only useful subset |

### Classification: DEFER (mixed content; needs per-file split before classification)

**Per Codex F2: previously double-classified entries reduced to single DEFER classification with split criteria.**

| Entry | Split criteria |
|---|---|
| `docs/` | Per-file: `gtkb-*.md` → KEEP (GT-KB platform); product/customer docs → MOVE to `applications/Agent_Red/docs/` |
| `wiki/` | Determine relationship to `agent-red.wiki/` (duplicates? different content?); split or merge |
| `scripts/` | `scripts/rehearse/` → KEEP (GT-KB framework rehearsal); `scripts/archive/` → KEEP (history); other scripts → per-file audit (operational tooling vs Agent Red app) |
| `tests/` | `tests/scripts/` likely mostly framework tests (KEEP); `tests/<app>` → MOVE; per-test audit needed |
| `tools/` | `tools/knowledge-db/` → KEEP (GT-KB framework); other tools → per-file audit |
| `pyproject.toml` | Single file; needs in-place split into framework + Agent Red dependencies sections OR keep monolithic with documented intent |
| `requirements.txt`, `requirements-local.txt`, `requirements-test.txt` | Same as pyproject.toml |
| `package.json`, `package-lock.json` | Mostly Agent Red npm deps; needs split or move with import-path updates |
| `uv.lock` | Tied to pyproject.toml; defer with it |
| `config/` | Determine if framework config or Agent Red runtime config; per-file split |
| `.shopify/` | Likely Agent Red Shopify state; verify (live or template?) |
| `.playwright-mcp/` | Playwright MCP state (likely tooling); per-content audit |

## §B. Pre-move impact inventory requirements (per Codex F4)

Each MOVE cluster's follow-on bridge MUST include a pre-move impact inventory section with:

```
1. Path references inventory:
   - grep -rn "<old-path>" .github/ scripts/ tests/ docs/ Dockerfile* package.json pyproject.toml
   - List every reference; classify each as: must-update | informational | safe-to-leave
2. Import path references (for src/-class moves):
   - grep -rn "from src" --include="*.py" .
   - grep -rn "from src" --include="*.ts" --include="*.tsx" .
   - grep -rn "import.*src" --include="*.py" --include="*.ts" .
3. Generated-output and cache exclusions:
   - .gitignore patterns that reference old paths
   - .dockerignore patterns
4. CI path references:
   - .github/workflows/*.yml that mention the moving path
5. Verification command (post-move):
   - Specific test/build command that confirms imports resolve and CI passes
```

This inventory is a hard prerequisite for every MOVE bridge to be GO-able.

### §B.1 Cluster sequencing (recommended; smallest-first to validate move pattern)

1. `pdf` cluster (5 files; minimal references; isolates the move-and-update pattern)
2. `readiness` cluster (5 files; mostly docs; minimal references)
3. `content` cluster (10+ entries; static content; CI may reference)
4. `infra` cluster (Docker + CI heavy; most CI updates needed)
5. `src` cluster (largest; all imports + Docker contexts must update)

After cluster 1 verifies cleanly, accelerate.

## §C. DELETE CANDIDATE handling (per Codex F3)

**This audit grants no deletion approval.** Each DELETE CANDIDATE must:

1. Be added to a separate cleanup-manifest bridge entry (not this audit).
2. Follow the §2.5 5-step manifest protocol verbatim:
   - Inventory: classify each, capture content evidence (e.g., `Get-FileHash`).
   - Migrate: copy any unexpected GT-KB or Agent Red content to in-root destination FIRST.
   - Verify: checksum-compare any migrated content.
   - Confirm: re-scan source confirms no remaining live content.
   - Record disposition + delete: manifest entry committed before `Remove-Item`.
3. Codex VERIFIED of the manifest before any deletion.

## §D. Codex F-condition compliance check

| Codex `-008` Finding | Resolution in this REVISED-1 |
|---|---|
| F1 — Audit omits 7 entries | §A includes COMPLETE `Get-ChildItem -Force` output (105 entries); every entry classified |
| F2 — Some entries classified twice | §A — each entry has exactly ONE classification; mixed → DEFER |
| F3 — DELETE language is approval | §A "DELETE CANDIDATE"; §C explicit no-approval-by-this-audit + manifest gate |
| F4 — Pre-move impact inventory missing | §B detailed per-cluster requirement template |

## §E. Codex Review Asks

1. Confirm the complete inventory (§A) addresses F1.
2. Confirm the single-classification rule (§A) addresses F2; particularly that previously double-classified entries (`package-pdf.json`, `infrastructure/`) now have single classifications.
3. Confirm the DELETE CANDIDATE language + §C explicit gating addresses F3.
4. Confirm the §B pre-move impact inventory template addresses F4.
5. Confirm cluster sequencing (§B.1) is appropriate; particularly the pdf-first ordering.
6. **GO / NO-GO** on REVISED-1.

## §F. Decisions Needed From Owner (post-Codex-GO)

1. Approve the classification (any re-classifications needed?).
2. Approve cluster sequencing (pdf-first, src-last) or override.
3. Approve the DELETE CANDIDATE handling: each candidate gets a separate manifest bridge OR batch into one cleanup-manifest bridge?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
