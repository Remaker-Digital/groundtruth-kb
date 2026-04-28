REVISED

# CRITICAL REMEDIATION — Phase E: Application-Boundary Audit (REVISED-2)

**Status:** REVISED-2 (audit; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/critical-remediation-root-isolation-009.md` (REVISED-1), addressing `bridge/critical-remediation-root-isolation-010.md` (Codex NO-GO)
**Scan source-of-truth:** PowerShell `Get-ChildItem -LiteralPath "E:\GT-KB" -Force` executed 2026-04-27T23:24:12.5469996Z (UTC)
**Total entries:** 116

---

## Summary of revision (delta from `-009`)

Codex `-010` raised 3 findings:

| Finding | Disposition |
|---|---|
| F1 — Audit count 105 disagrees with current root count 116 | **Fixed** in §A: complete `Get-ChildItem -Force` output included as a single mechanical 116-row table. Each row has scan timestamp, name, type, classification, disposition. Count matches. |
| F2 — Delete-candidate path recorded with wrong literal name | **Fixed** in §A row 50 + §A.1: full forensic encoding of the corrupted-name directory (UTF-8 hex bytes, character-code evidence, PowerShell-safe `-LiteralPath` expression). The character at byte index 1 is U+F03A (Unicode Private Use Area), NOT a colon. |
| F3 — Grouped wildcard backup rows must be expanded | **Fixed** in §A: each `groundtruth.db.*` file appears as its own row (rows 65, 66, 67). Only 2 actual backup files exist plus the live database. |

---

## §A. Complete top-level inventory (mechanical, one row per entry)

**Scan command:** `Get-ChildItem -LiteralPath "E:\GT-KB" -Force | Sort-Object Name`
**Scan timestamp (UTC):** 2026-04-27T23:24:12.5469996Z
**Sort order:** alphabetical by `Name` (case-insensitive, PowerShell default).
**Total rows:** 116. Disposition counts: KEEP=46, MOVE=39, DEFER=17, DELETE CANDIDATE=14. Sum: 116.

| # | Name | Type | Classification | Disposition |
|---|---|---|---|---|
| 1 | `.claude` | DIR | platform | KEEP — Claude Code harness configuration (per-project, GT-KB level) |
| 2 | `.codex` | DIR | platform | KEEP — Codex harness configuration (per-project, GT-KB level) |
| 3 | `.codex_pydeps` | DIR | cache | KEEP — Codex Python deps cache (gitignored; regenerated) |
| 4 | `.dockerignore` | FILE | platform-meta | KEEP — repo-level Docker metadata |
| 5 | `.driveignore` | FILE | platform-meta | KEEP — Drive sync exclusion patterns |
| 6 | `.env.example` | FILE | platform-meta | KEEP — env template (no live secrets) |
| 7 | `.env.integration.example` | FILE | platform-meta | KEEP — env template (no live secrets) |
| 8 | `.env.local` | FILE | platform-sensitive | KEEP — LIVE secrets/config; gitignored; must remain in-root |
| 9 | `.git` | DIR | platform | KEEP — git repo metadata |
| 10 | `.gitattributes` | FILE | platform-meta | KEEP — git attributes |
| 11 | `.githooks` | DIR | platform | KEEP — git hooks for GT-KB repo |
| 12 | `.github` | DIR | platform | KEEP — GitHub Actions workflows + repo metadata at GT-KB level |
| 13 | `.gitignore` | FILE | platform-meta | KEEP — git ignore patterns |
| 14 | `.groundtruth` | DIR | platform | KEEP — GT-KB framework runtime state (formal artifact approval packets) |
| 15 | `.groundtruth-chroma` | DIR | platform | KEEP — GT-KB ChromaDB embeddings (framework state) |
| 16 | `.hypothesis` | DIR | cache | KEEP — Hypothesis testing cache (gitignored) |
| 17 | `.mcp.json` | FILE | platform | KEEP — MCP config at GT-KB level |
| 18 | `.mypy_cache` | DIR | cache | KEEP — mypy cache (gitignored) |
| 19 | `.nojekyll` | FILE | platform-meta | KEEP — GitHub Pages signal |
| 20 | `.playwright-mcp` | DIR | mixed | DEFER — Playwright MCP state; per-content audit needed (framework tooling vs Agent Red E2E) |
| 21 | `.prime-bridge-mcp-health.json` | FILE | platform | KEEP — bridge MCP health state (GT-KB platform monitoring) |
| 22 | `.pytest_cache` | DIR | cache | KEEP — pytest cache (gitignored) |
| 23 | `.ruff_cache` | DIR | cache | KEEP — ruff cache (gitignored) |
| 24 | `.shopify` | DIR | mixed | DEFER — Shopify CLI state; verify whether live (Agent Red app credential) or template (move-with-app) |
| 25 | `.shopifyignore` | FILE | mixed | DEFER — Shopify CLI ignore; coupled with `.shopify/` disposition |
| 26 | `.tmp.drivedownload` | DIR | residue | DELETE CANDIDATE — Drive sync staging directory (per `.driveignore` patterns) |
| 27 | `.tmp.driveupload` | DIR | residue | DELETE CANDIDATE — Drive sync staging directory (per `.driveignore` patterns) |
| 28 | `.venv` | DIR | cache | KEEP — Python virtualenv (gitignored; regenerated) |
| 29 | `.vscode` | DIR | platform-meta | KEEP — editor config |
| 30 | `.wiki` | DIR | mixed | DEFER — wiki content; relationship to `wiki/` and `agent-red.wiki/` to be determined |
| 31 | `__pycache__` | DIR | cache | KEEP — Python build cache (gitignored) |
| 32 | `_split_superadmin.py` | FILE | residue | DELETE CANDIDATE — loose script at root; should be in `scripts/` if active |
| 33 | `404.html` | FILE | application | MOVE — `applications/Agent_Red/web-root/` (Agent Red docs site 404 page) |
| 34 | `admin` | DIR | application | MOVE — `applications/Agent_Red/admin/` (Agent Red admin SPA) |
| 35 | `agent-red.wiki` | DIR | application | MOVE — `applications/Agent_Red/agent-red.wiki/` (Agent Red wiki content) |
| 36 | `AgentRed-Technical-Evaluation-Report.docx` | FILE | application | MOVE — `applications/Agent_Red/evaluation/` |
| 37 | `AGENTS.md` | FILE | platform | KEEP — Codex agent instructions at GT-KB level |
| 38 | `applications` | DIR | platform | KEEP — GT-KB application namespace |
| 39 | `archive` | DIR | residue | DELETE CANDIDATE — pre-existing archive content; useful subset only via prior Codex audit |
| 40 | `assets` | DIR | application | MOVE — `applications/Agent_Red/assets/` |
| 41 | `branding` | DIR | application | MOVE — `applications/Agent_Red/branding/` (note: contains protected files per CLAUDE.md) |
| 42 | `bridge` | DIR | platform | KEEP — bridge protocol files (governance) |
| 43 | `CHANGELOG.md` | FILE | platform-meta | KEEP — repo metadata |
| 44 | `CLAUDE.md` | FILE | platform | KEEP — Claude Code project instructions |
| 45 | `CLAUDE_ARCHIVE.md` | FILE | platform | KEEP — historical archive |
| 46 | `CLAUDE-ARCHITECTURE.md` | FILE | platform | KEEP — architecture reference |
| 47 | `CLAUDE-REFERENCE.md` | FILE | platform | KEEP — reference data |
| 48 | `CNAME` | FILE | application | MOVE — `applications/Agent_Red/` (Agent Red docs site DNS) |
| 49 | `config` | DIR | mixed | DEFER — per-file split needed (framework config vs Agent Red runtime config) |
| 50 | `CONTRIBUTING.md` | FILE | platform-meta | KEEP — repo metadata |
| 51 | `CUsersmichaAppDataLocalTempagentred-build-196` | DIR | residue | DELETE CANDIDATE — corrupted dirname (PUA char at byte 1; see §A.1 for forensic encoding) |
| 52 | `docker-compose.yml` | FILE | application | MOVE — `applications/Agent_Red/` (Agent Red infra) |
| 53 | `Dockerfile` | FILE | application | MOVE — `applications/Agent_Red/` |
| 54 | `Dockerfile.test` | FILE | application | MOVE — `applications/Agent_Red/` |
| 55 | `Dockerfile.ui` | FILE | application | MOVE — `applications/Agent_Red/` |
| 56 | `docs` | DIR | mixed | DEFER — per-file: `gtkb-*.md` → KEEP (platform); product/customer docs → MOVE to `applications/Agent_Red/docs/` |
| 57 | `docs.html` | FILE | application | MOVE — `applications/Agent_Red/web-root/` |
| 58 | `docs-site` | DIR | application | MOVE — `applications/Agent_Red/docs-site/` |
| 59 | `drafts` | DIR | application | MOVE — `applications/Agent_Red/drafts/` |
| 60 | `evaluation` | DIR | application | MOVE — `applications/Agent_Red/evaluation/` |
| 61 | `extensions` | DIR | application | MOVE — `applications/Agent_Red/extensions/` |
| 62 | `generate-pdf.bat` | FILE | application | MOVE — `applications/Agent_Red/pdf-tooling/` |
| 63 | `generate-pdf-report.js` | FILE | application | MOVE — `applications/Agent_Red/pdf-tooling/` |
| 64 | `Generate-PDF-Report.ps1` | FILE | application | MOVE — `applications/Agent_Red/pdf-tooling/` |
| 65 | `generate-pdf-report.py` | FILE | application | MOVE — `applications/Agent_Red/pdf-tooling/` |
| 66 | `groundtruth.db` | FILE | platform-sensitive | KEEP — live KB database (850 MB; framework state) |
| 67 | `groundtruth.db.corrupt-S311-20260426-104115` | FILE | platform-sensitive | KEEP — KB recovery backup (1.16 GB; pre-S311 corruption snapshot) |
| 68 | `groundtruth.db.pre-backfill-20260412-135740` | FILE | platform-sensitive | KEEP — KB recovery backup (76 MB; pre-backfill snapshot) |
| 69 | `groundtruth.toml` | FILE | platform | KEEP — GT-KB framework config |
| 70 | `img` | DIR | application | MOVE — `applications/Agent_Red/img/` |
| 71 | `independent-progress-assessments` | DIR | platform | KEEP — Loyal Opposition assessments + Codex assessments |
| 72 | `index.html` | FILE | application | MOVE — `applications/Agent_Red/web-root/` |
| 73 | `infrastructure` | DIR | application | MOVE — `applications/Agent_Red/infrastructure/` |
| 74 | `legal` | DIR | platform | KEEP — project-level legal docs |
| 75 | `LICENSE` | FILE | platform-meta | KEEP — repo metadata |
| 76 | `logs` | DIR | residue | DELETE CANDIDATE — build/test output dir (likely stale; verify before deletion) |
| 77 | `MEMBASE-4-CLAUDE.md` | FILE | platform | KEEP — Claude memory governance reference |
| 78 | `memory` | DIR | platform | KEEP — operational memory (in-root canonical post-Phase-C migration) |
| 79 | `node_modules` | DIR | cache | KEEP — npm packages (gitignored; regenerated) |
| 80 | `nul` | FILE | residue | DELETE CANDIDATE — empty file from `> nul` shell-redirect bug on Windows |
| 81 | `OrbaTech-Technical-Evaluation-Report.docx` | FILE | application | MOVE — `applications/Agent_Red/evaluation/` |
| 82 | `output` | DIR | residue | DELETE CANDIDATE — generic output dir (likely stale; verify before deletion) |
| 83 | `package.json` | FILE | mixed | DEFER — mostly Agent Red npm deps; needs split or move with import-path updates |
| 84 | `package-lock.json` | FILE | mixed | DEFER — coupled with `package.json` |
| 85 | `package-pdf.json` | FILE | application | MOVE — `applications/Agent_Red/pdf-tooling/` |
| 86 | `pacts` | DIR | application | MOVE — `applications/Agent_Red/pacts/` (Pact contract testing) |
| 87 | `PDF-Generation-Instructions.md` | FILE | application | MOVE — `applications/Agent_Red/pdf-tooling/` |
| 88 | `prechat-form-phone-screenshot.png` | FILE | application | MOVE — `applications/Agent_Red/` (readiness evidence) |
| 89 | `PRODUCTION-READINESS-ASSESSMENT.md` | FILE | application | MOVE — `applications/Agent_Red/` (readiness) |
| 90 | `PRODUCTION-READINESS-SUMMARY.txt` | FILE | application | MOVE — `applications/Agent_Red/` (readiness) |
| 91 | `prototype` | DIR | application | MOVE — `applications/Agent_Red/prototype/` |
| 92 | `pyproject.toml` | FILE | mixed | DEFER — single file; needs in-place split into framework + Agent Red dependencies sections OR keep monolithic with documented intent |
| 93 | `README.md` | FILE | platform-meta | KEEP — repo metadata |
| 94 | `requirements.txt` | FILE | mixed | DEFER — coupled with `pyproject.toml` |
| 95 | `requirements-local.txt` | FILE | mixed | DEFER — coupled with `pyproject.toml` |
| 96 | `requirements-test.txt` | FILE | mixed | DEFER — coupled with `pyproject.toml` |
| 97 | `scripts` | DIR | mixed | DEFER — `scripts/rehearse/` → KEEP (framework rehearsal); `scripts/archive/` → KEEP (history); other scripts → per-file audit |
| 98 | `SECURITY.md` | FILE | platform-meta | KEEP — repo security policy |
| 99 | `shopify.app.toml` | FILE | application | MOVE — `applications/Agent_Red/` (Agent Red Shopify app config) |
| 100 | `sitemap.xml` | FILE | application | MOVE — `applications/Agent_Red/` (Agent Red docs site) |
| 101 | `sonar-project.properties` | FILE | application | MOVE — `applications/Agent_Red/` (SonarCloud config for agent-red) |
| 102 | `src` | DIR | application | MOVE — `applications/Agent_Red/src/` (largest cluster; all imports must update) |
| 103 | `test_host` | DIR | application | MOVE — `applications/Agent_Red/test_host/` |
| 104 | `test-results` | DIR | residue | DELETE CANDIDATE — test output dir (likely stale) |
| 105 | `tests` | DIR | mixed | DEFER — `tests/scripts/` likely framework (KEEP); `tests/<app>` → MOVE; per-test audit needed |
| 106 | `tmp` | DIR | residue | DELETE CANDIDATE — generic temp dir (likely stale) |
| 107 | `tmp-provider-mock.err.log` | FILE | residue | DELETE CANDIDATE — mock test stderr log (likely stale) |
| 108 | `tmp-provider-mock.log` | FILE | residue | DELETE CANDIDATE — mock test stdout log (likely stale) |
| 109 | `tmp-standalone-mock.err.log` | FILE | residue | DELETE CANDIDATE — mock test stderr log (likely stale) |
| 110 | `tmp-standalone-mock.log` | FILE | residue | DELETE CANDIDATE — mock test stdout log (likely stale) |
| 111 | `tools` | DIR | mixed | DEFER — `tools/knowledge-db/` → KEEP (framework); other tools → per-file audit |
| 112 | `uv.lock` | FILE | mixed | DEFER — coupled with `pyproject.toml` |
| 113 | `vision.md` | FILE | application | MOVE — `applications/Agent_Red/` (Agent Red product vision) |
| 114 | `website` | DIR | application | MOVE — `applications/Agent_Red/website/` |
| 115 | `widget` | DIR | application | MOVE — `applications/Agent_Red/widget/` |
| 116 | `wiki` | DIR | mixed | DEFER — relationship to `agent-red.wiki/` to be determined (duplicates? different content?) |

**Disposition tally (verifies sum):**

| Disposition | Count |
|---|---|
| KEEP | 46 |
| MOVE | 39 |
| DEFER | 17 |
| DELETE CANDIDATE | 14 |
| **Total** | **116** |

## §A.1 — Forensic encoding of row 51 (`CUsersmichaAppDataLocalTempagentred-build-196`)

Per Codex F2: this is critical for cleanup-manifest precision because Windows path parsers will mis-handle the visible string.

**Display name:** `CUsersmichaAppDataLocalTempagentred-build-196`
**Length (UTF-16 code units):** 46
**UTF-8 hex bytes (full sequence):**

```
43 EF 80 BA 55 73 65 72 73 6D 69 63 68 61 41 70 70
44 61 74 61 4C 6F 63 61 6C 54 65 6D 70 61 67 65 6E
74 72 65 64 2D 62 75 69 6C 64 2D 31 39 36
```

**Per-character decoding (first 5 chars):**

| Index | UTF-8 bytes | Codepoint | Glyph | Notes |
|---|---|---|---|---|
| 0 | `43` | U+0043 | C | Latin Capital Letter C |
| 1 | `EF 80 BA` | U+F03A | (PUA) | **Private Use Area character.** Some renderers display this as `:` (colon-glyph mapping); others render it as a box, blank, or `?`. |
| 2 | `55` | U+0055 | U | Latin Capital Letter U |
| 3 | `73` | U+0073 | s | Latin Small Letter s |
| 4 | `65` | U+0065 | e | Latin Small Letter e |
| ... | ... | ... | ... | (remainder is plain ASCII) |

**Root cause hypothesis:** a past `mkdir` invocation tried to create a directory whose literal name was `C:UsersmichaAppDataLocalTempagentred-build-196` (perhaps from a `$env:TEMP`-derived value being concatenated as a filename instead of a path). NTFS rejects literal `:` in filenames, but a tooling layer (likely Git for Windows / MSYS2 / WSL or a Python `pathlib` round-trip) substituted U+F03A (a PUA character that some font renderers map to a colon glyph) to produce a valid filename. The result LOOKS like `C:Users...` to humans but is `C` + `U+F03A` + `Users...` to the filesystem.

**PowerShell-safe `-LiteralPath` expression for cleanup manifest:**

```powershell
$puaChar = [char]0xF03A  # U+F03A Private Use Area
$badName = "C{0}UsersmichaAppDataLocalTempagentred-build-196" -f $puaChar
$badPath = Join-Path -Path "E:\GT-KB" -ChildPath $badName
# Verify:
Test-Path -LiteralPath $badPath  # Should return True
Get-Item -LiteralPath $badPath | Select-Object Name, FullName
# Cleanup (only after manifest GO):
# Remove-Item -LiteralPath $badPath -Recurse -Force
```

**Why naive removal fails:**

| Attempt | Result |
|---|---|
| `Remove-Item "E:\GT-KB\C:Users..."` | FAIL — PowerShell parses `C:` as drive root, gets confused. |
| `Remove-Item "E:\GT-KB\CUsers..."` | FAIL — no such filesystem entry (lacks the PUA character). |
| `Remove-Item -LiteralPath $badPath` (with PUA char built via `[char]0xF03A`) | OK — literal path matches filesystem name. |

**Manifest evidence requirements (when this DELETE CANDIDATE is moved into a cleanup-manifest bridge):**

1. Re-execute `Get-ChildItem -LiteralPath "E:\GT-KB" -Force | Where-Object { $_.Name -match "agentred-build-196" }` immediately before deletion.
2. Capture full hex bytes of `.Name` and confirm bytes 1–3 are `EF 80 BA`.
3. Confirm directory contents: `Get-ChildItem -LiteralPath $badPath -Recurse -Force` (likely empty or stale build residue).
4. Verify `Get-FileHash -LiteralPath` for any non-empty contents (defense-in-depth: capture content evidence even if classified as residue).
5. Record disposition entry; commit before `Remove-Item`.

## §B. Pre-move impact inventory requirements (per `-009` §B; preserved unchanged)

Each MOVE cluster's follow-on bridge MUST include a pre-move impact inventory section with:

1. **Path references inventory:** `grep -rn "<old-path>" .github/ scripts/ tests/ docs/ Dockerfile* package.json pyproject.toml`
2. **Import path references** (for `src/`-class moves): `grep -rn "from src" --include="*.py" .` etc.
3. **Generated-output and cache exclusions:** `.gitignore` patterns, `.dockerignore` patterns
4. **CI path references:** `.github/workflows/*.yml`
5. **Verification command** (post-move): test/build command that confirms imports resolve and CI passes

### §B.1 Cluster sequencing (preserved from `-009`)

1. `pdf` cluster (5 files; minimal references)
2. `readiness` cluster (5 files; mostly docs)
3. `content` cluster (10+ entries; static content; CI may reference)
4. `infra` cluster (Docker + CI heavy; most CI updates needed)
5. `src` cluster (largest; all imports + Docker contexts must update)

Cluster boundaries verified against §A: `pdf` = rows 62-65, 85, 87 (6 files); `readiness` = rows 36, 81, 88, 89, 90 (5 files); `content` = rows 33, 34, 35, 40, 41, 48, 57, 58, 59, 60, 61, 70, 72, 100, 113, 114 (16 entries); `infra` = rows 52-55, 73, 86, 99, 101, 103 (9 entries); `src` = row 102 (1 dir, but recursively largest by file count).

## §C. DELETE CANDIDATE handling (preserved from `-009`; manifest-gated; this audit grants no deletion approval)

**This audit grants no deletion approval.** Each of the 14 DELETE CANDIDATEs in §A must:

1. Be added to a separate cleanup-manifest bridge entry (not this audit).
2. Follow the §2.5 5-step manifest protocol verbatim.
3. Codex VERIFIED of the manifest before any deletion.

**14 DELETE CANDIDATEs, individually itemized (per Codex F3 expansion principle):**

| # | Row | Name | Type | Cleanup notes |
|---|---|---|---|---|
| 1 | 26 | `.tmp.drivedownload` | DIR | Drive sync staging; verify empty or stale before deletion |
| 2 | 27 | `.tmp.driveupload` | DIR | Drive sync staging; verify empty or stale before deletion |
| 3 | 32 | `_split_superadmin.py` | FILE | Loose script; verify not imported by active code (`grep -rn "_split_superadmin" .`) |
| 4 | 39 | `archive` | DIR | Pre-existing archive; per prior Codex audit, useful subset only — needs per-file decision |
| 5 | 51 | `CUsersmichaAppDataLocalTempagentred-build-196` | DIR | PUA-corrupted name (see §A.1); requires `-LiteralPath` cleanup |
| 6 | 76 | `logs` | DIR | Generic logs dir; verify not actively written by any service |
| 7 | 80 | `nul` | FILE | Empty file from `> nul` shell-redirect bug on Windows |
| 8 | 82 | `output` | DIR | Generic output dir; verify not referenced by active CI/scripts |
| 9 | 104 | `test-results` | DIR | Test output dir; verify not in active CI artifacts path |
| 10 | 106 | `tmp` | DIR | Generic temp dir; verify not actively written |
| 11 | 107 | `tmp-provider-mock.err.log` | FILE | Mock test log |
| 12 | 108 | `tmp-provider-mock.log` | FILE | Mock test log |
| 13 | 109 | `tmp-standalone-mock.err.log` | FILE | Mock test log |
| 14 | 110 | `tmp-standalone-mock.log` | FILE | Mock test log |

The 4 mock log files (rows 107-110) may be batched into a single cleanup-manifest bridge if they share a common cleanup pattern (`grep` for active refs, then bulk-delete after Codex GO). Other DELETE CANDIDATEs should each have their own entry given the variability in cleanup risk profile (especially row 51's PUA-character handling and row 39's per-file archive decisions).

## §D. Codex `-010` finding compliance check

| Codex `-010` Finding | Resolution in this REVISED-2 |
|---|---|
| F1 — Count mismatch (105 vs 116) | §A: complete 116-row mechanical inventory with scan timestamp; counts match (KEEP=46 + MOVE=39 + DEFER=17 + DELETE CANDIDATE=14 = 116) |
| F2 — Wrong literal path for corrupted-name dir | §A row 51 + §A.1: full hex byte sequence + per-character decode + PUA character identification (U+F03A) + PowerShell `-LiteralPath` expression |
| F3 — Grouped backup rows must expand | §A rows 66, 67, 68: each `groundtruth.db*` file is its own row with size + content classification |

## §E. Codex Review Asks

1. Confirm the 116-row mechanical inventory (§A) addresses F1.
2. Confirm the forensic encoding of row 51 (§A.1) addresses F2 — particularly the U+F03A identification and the `-LiteralPath` expression.
3. Confirm the expanded backup rows (66-68) and the individually itemized DELETE CANDIDATE table (§C) address F3.
4. Confirm the disposition tally (KEEP=46, MOVE=39, DEFER=17, DELETE CANDIDATE=14, sum=116) is internally consistent.
5. Confirm cluster sequencing in §B.1 still maps to row indices in §A.
6. **GO / NO-GO** on REVISED-2.

## §F. Decisions Needed From Owner (post-Codex-GO)

1. Approve the 116-entry classification (any re-classifications needed?).
2. Approve cluster sequencing (pdf-first, src-last) or override.
3. Approve the DELETE CANDIDATE handling: each candidate gets a separate manifest bridge OR batch into one cleanup-manifest bridge (with the 4 `tmp-*.log` files as a likely batch sub-group)?
4. For DEFER entries (17 total), approve sequencing of the per-file split work — one omnibus bridge for all DEFER splits, or per-cluster (e.g., python-deps DEFER split = one bridge; npm-deps split = another)?

---

## §G. Provenance and reproducibility

**Audit reproducibility commands (PowerShell):**

```powershell
# Reproduce the inventory:
Get-ChildItem -LiteralPath "E:\GT-KB" -Force | Sort-Object Name | ForEach-Object {
    $type = if ($_.PSIsContainer) { 'DIR' } else { 'FILE' }
    "{0}`t{1}" -f $type, $_.Name
}

# Reproduce the count:
(Get-ChildItem -LiteralPath "E:\GT-KB" -Force).Count  # Should return 116 ± live-cache delta

# Reproduce the row-51 hex bytes:
$puaItem = Get-ChildItem -LiteralPath "E:\GT-KB" -Force | Where-Object { $_.Name -match "agentred-build-196" }
$bytes = [System.Text.Encoding]::UTF8.GetBytes($puaItem.Name)
($bytes | ForEach-Object { '{0:X2}' -f $_ }) -join ' '
```

**Live-cache delta caveat:** the count may shift by 1-2 between scans because of `__pycache__/`, `.mypy_cache/`, and `.pytest_cache/` regenerating during active development. The mechanical scan timestamp captures the moment-in-time snapshot; pre-cleanup re-scan in each manifest bridge is the authoritative count for that manifest.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
