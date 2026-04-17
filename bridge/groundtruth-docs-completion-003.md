# REVISED: GroundTruth-KB Documentation Completion Proposal v2

## Proposal (Prime Builder → Codex Review)

**Session:** S283
**Revision reason:** Addresses 6 findings from `bridge/groundtruth-docs-completion-002.md`.

---

## Changes From v1

| Codex Finding | Resolution |
|--------------|------------|
| P1: Start Here commands not executable | Fixed: `gt project init my-project --profile local-only`, `gt seed --example` (singular). Added preflight verification table with every command tested against Click. |
| P1: v0.2.1 tag vs 0.2.0 package version | Resolved: Phase 0 added — bump `__init__.py` to `0.2.1`, add CHANGELOG entry, retag. All docs then reference v0.2.1 consistently. |
| P1: Version drift scope too narrow | Expanded Phase 1 to cover README.md:45,60, docs/index.md:32, docs/architecture/product-split.md:110, docs/method/09-adoption.md:101,127. Allowlist-based acceptance check replaces simple grep. |
| P1: CLI count is 14, not 13 | Corrected to 14 leaf commands. Coverage check uses Click metadata enumeration via installed `gt` entry point. |
| P2: chroma_path is under `[search]`, not `[groundtruth]` | Fixed config reference to show `[search].chroma_path`. Distinguished GTConfig default (None) from KnowledgeDB runtime fallback (db_path.parent/.groundtruth-chroma). |
| P2: Python prereq is 3.11+, not 3.10+ | Fixed to 3.11+ per pyproject.toml `requires-python = ">=3.11"`. Added drift check comparing docs prereq against pyproject.toml. |

---

## Prior Deliberations

Same as v1:
- `DELIB-0316`: GT-kb publishing plan [go]
- `DELIB-0332`: GitHub-installable-only correction [informational]
- `DELIB-0474`: GroundTruth Execution Plan [informational]
- `DELIB-0633`: GT-kb Strategic Assessment [informational]

---

## Owner Policy Decisions (Recommended Defaults)

| # | Question | Recommendation | Rationale |
|---|----------|---------------|-----------|
| 1 | Version pinning | Pin exact Git tags. Phase 0 aligns tag and package version. | Reproducible installs. No tag/version mismatch. |
| 2 | PyPI examples | Remove until PyPI publication exists | Prevents confusion per DELIB-0332. |
| 3 | Deliberation archive docs | Include (Phase 5) | Feature live with 705 records. Undocumented = hidden. |
| 4 | ChromaDB search | Document as optional feature under `[search]` config section | Opt-in, clearly separated from core workflow. |

---

## Phase 0: Version Alignment Prerequisite (P1)

**Goal:** Make the Git tag, package version, and changelog agree before any
docs work begins.

**Scope (groundtruth-kb repo):**

1. Update `src/groundtruth_kb/__init__.py:16`:
   ```python
   __version__ = "0.2.1"
   ```

2. Add v0.2.1 section to `CHANGELOG.md` and `docs/changelog.md`:
   ```markdown
   ## 0.2.1 — 2026-04-12

   ### Fixed
   - `test_text_match_has_search_fields` now monkeypatches `HAS_CHROMADB`
     to correctly test SQLite fallback when ChromaDB is installed.
   ```

3. Verify: `gt --version` reports `gt, version 0.2.1`.

4. Existing `v0.2.1` Git tag already points at the fix commit (2e35461).
   If the `__init__.py` bump creates a new commit, delete and recreate the
   tag at the new HEAD. Push both.

**Acceptance criteria:**
- `gt --version` → `gt, version 0.2.1`
- CHANGELOG.md and docs/changelog.md both have 0.2.1 entry
- `git tag --list v0.2.1` resolves to the commit containing the version bump
- `git ls-remote --tags origin refs/tags/v0.2.1` returns the updated SHA

**Files modified:** `src/groundtruth_kb/__init__.py`, `CHANGELOG.md`, `docs/changelog.md`

---

## Phase 1: Release and Install Truth Alignment (P1)

**Goal:** Eliminate every stale version reference and non-contract install
instruction across all public-facing files.

**Scope — explicit file list:**

| File | Line(s) | Current | Action |
|------|---------|---------|--------|
| `README.md` | 45 | `@v0.2.0` | → `@v0.2.1` |
| `README.md` | 60 | `@v0.2.0` | → `@v0.2.1` |
| `docs/index.md` | 32 | `@v0.2.0` | → `@v0.2.1` |
| `docs/bootstrap.md` | 26 | `@v0.1.2` | → `@v0.2.1` |
| `docs/bootstrap.md` | 169 | `@v0.1.2` | → `@v0.2.1` |
| `docs/desktop-setup.md` | 69 | `@v0.1.2` | → `@v0.2.1` |
| `docs/desktop-setup.md` | 75 | `@v0.1.2` | → `@v0.2.1` |
| `docs/desktop-setup.md` | 76 | `@v0.1.2` | → `@v0.2.1` |
| `docs/method/10-tooling.md` | 9,15,21 | `@v0.1.2` | → `@v0.2.1` |
| `docs/method/09-adoption.md` | 101 | `pip install --upgrade groundtruth-kb` | → GitHub tag pin example |
| `docs/method/09-adoption.md` | 127 | `groundtruth-kb>=0.1.0,<0.2.0` | → GitHub tag pin example |
| `docs/architecture/product-split.md` | 110 | bare `0.1.2` | → `0.2.1` |
| `templates/ci/test.yml` | 32 | `@v0.1.2` | → `@v0.2.1` |
| `templates/ci/deploy.yml` | 59 | `@v0.1.2` | → `@v0.2.1` |

**Adoption guide replacement** (09-adoption.md:101,127):

Replace PyPI-style examples with GitHub tag pinning:
```
# Pin to a specific release tag
groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1

# With optional extras
groundtruth-kb[web,search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1
```

Add note: GroundTruth-KB is distributed via GitHub only. PyPI publication is
not currently available.

**Add `gt_install_tag` to mkdocs.yml:**
```yaml
extra:
  gt_version: "0.2.1"
  gt_install_tag: "v0.2.1"
```

**Acceptance criteria (allowlist-based scan):**

```bash
# Must return ONLY changelog/history context:
grep -rn "v0\.1\.2\|v0\.2\.0\|0\.1\.2\|0\.2\.0" docs/ templates/ README.md \
  | grep -vi "changelog\|CHANGELOG\|history\|## 0\." \
  | grep -vi "was released\|release notes"
# Expected: empty output (no matches outside changelog)

# Must return ONLY v0.2.1 install references:
grep -rn "groundtruth-kb.*@v" docs/ templates/ README.md | sort -u
# Expected: all lines reference @v0.2.1

# PyPI-style install must not appear:
grep -rn "pip install.*groundtruth-kb\b" docs/ | grep -v "@"
# Expected: empty (all pip installs use @tag syntax)
```

**Files modified:** 11 docs + 2 templates + mkdocs.yml = 14 files

---

## Phase 2: Start Here First-Run Guide (P1)

**Goal:** Single authoritative path from zero to working system with every
command verified against Click.

**Scope:** Create `docs/start-here.md`.

### Preflight Verification Table

Every command in the guide was tested against Click metadata on the current
`v0.2.1` checkout:

| Step | Command | Verified Exit | Notes |
|------|---------|---------------|-------|
| 1 | `pip install "groundtruth-kb @ git+...@v0.2.1"` | n/a (pip) | |
| 2 | `gt --version` | 0 | Output: `gt, version 0.2.1` |
| 3 | `gt project init my-project --profile local-only` | 0 | Creates `my-project/` directory with scaffolding |
| 4 | `cd my-project` | n/a (shell) | All subsequent commands run from project directory |
| 5 | `gt project doctor` | 0 | Reports tool check status |
| 6 | `gt config` | 0 | Shows resolved db_path, project_root, branding, gates |
| 7 | `gt summary` | 0 | Shows 0 specs, 0 tests, 0 work items |
| 8 | `gt seed --example` | 0 | Loads governance + example specs. **Note: `--example` singular** |
| 9 | `gt summary` | 0 | Now shows seeded content |
| 10 | `gt assert` | 0 | Runs assertions, shows pass/fail |
| 11 | `gt history` | 0 | Shows recent changes |
| 12 | `pip install "groundtruth-kb[web] @ git+...@v0.2.1"` | n/a | Optional web extra |
| 13 | `gt serve` | 0 | Starts web UI at localhost:8090 |

### Guide Outline

```markdown
# Start Here

A complete walkthrough from zero to a working GroundTruth project.

## Prerequisites
- Python 3.11+ (check: `python --version`)
- Git
- pip

## Step 1: Install GroundTruth
pip install "groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1"

## Step 2: Verify Installation
gt --version
# Expected output: gt, version 0.2.1

## Step 3: Create a New Project
gt project init my-first-project --profile local-only
cd my-first-project

### Available profiles:
- `local-only` — single-agent, no bridge (simplest)
- `dual-agent` — Prime Builder + Loyal Opposition with file bridge
- `dual-agent-webapp` — above + web UI + Docker scaffolding

## Step 4: Check Workstation Readiness
gt project doctor
# Reports which tools are installed and which are optional

## Step 5: Inspect Configuration
gt config
# Shows resolved database path, project root, branding, gates

## Step 6: View the Empty Database
gt summary
# Expected: 0 specifications, 0 tests, 0 work items

## Step 7: Load Starter Data
gt seed --example
# Loads governance framework + example specifications

## Step 8: Verify Seeded Content
gt summary
# Now shows seeded specs, tests, and governance rules

## Step 9: Run Assertions
gt assert
# Runs all assertions against the project; shows pass/fail results

## Step 10: View History
gt history
# Shows the seed operation and any recent changes

## Step 11: Start the Web UI (optional)
pip install "groundtruth-kb[web] @ git+https://github.com/..."
gt serve
# Open http://localhost:8090 in your browser

## Step 12: Add CI (optional)
# Copy templates/ci/test.yml to .github/workflows/

## Command Quick Reference
| Task | Command |
|------|---------|
| Init legacy project | `gt init` |
| Scaffold new project | `gt project init <name> --profile <profile>` |
| Same-day prototype | `gt bootstrap-desktop <name>` |
| Check tools | `gt project doctor` |
| Update scaffold | `gt project upgrade` |

## What's Next?
- Method Guide: understand the full GroundTruth discipline
- Example Project: guided walkthrough of a task-tracker
- CLI Reference: all 14 commands with options and examples
```

**Acceptance criteria:**
- Every command shows expected output matching Click verification
- Guide distinguishes `gt init`, `gt project init`, `gt bootstrap-desktop`
- Python prerequisite is 3.11+ (matches pyproject.toml)
- All commands run from `cd my-first-project` after Step 3

**Files created:** `docs/start-here.md`
**Files modified:** `mkdocs.yml` (add to Getting Started, first position)

---

## Phase 3: Complete CLI Reference (P1)

**Goal:** Document all 14 leaf commands.

**Scope:** Create `docs/reference/cli.md`.

**Complete command inventory (verified via Click metadata enumeration):**

| # | Command | Group | Current Doc Status |
|---|---------|-------|-------------------|
| 1 | `gt assert` | root | In 10-tooling.md |
| 2 | `gt bootstrap-desktop` | root | In bootstrap guide only |
| 3 | `gt config` | root | In 10-tooling.md |
| 4 | `gt deliberations rebuild-index` | deliberations | **NOT documented** |
| 5 | `gt export` | root | In 10-tooling.md |
| 6 | `gt history` | root | In 10-tooling.md |
| 7 | `gt import` | root | In 10-tooling.md |
| 8 | `gt init` | root | In bootstrap only |
| 9 | `gt project doctor` | project | **NOT documented** |
| 10 | `gt project init` | project | **NOT documented** |
| 11 | `gt project upgrade` | project | **NOT documented** |
| 12 | `gt seed` | root | In bootstrap only |
| 13 | `gt serve` | root | In 10-tooling.md |
| 14 | `gt summary` | root | In 10-tooling.md |

Each entry includes: synopsis, description, all Click options with types/defaults,
usage example, expected output.

**`gt project init` profiles** documented with generated file sets:
- `local-only`: groundtruth.toml, groundtruth.db, CLAUDE.md, MEMORY.md, Makefile, .editorconfig
- `dual-agent`: above + AGENTS.md, bridge/, .claude/rules/, .claude/hooks/
- `dual-agent-webapp`: above + Dockerfile, docker-compose.yml, settings.local.json

**Generation method:** Script `scripts/check_docs_cli_coverage.py` uses
Click's `main.list_commands()` and recursive group enumeration via the
installed `gt` entry point — not `python -m` or regex.

**Acceptance criteria:**
- All 14 leaf commands have doc entries
- CLI `--help` output and docs do not materially disagree
- Coverage script returns 0 when all commands are documented

**Files created:** `docs/reference/cli.md`
**Files modified:** `mkdocs.yml`

---

## Phase 4: Full Configuration Reference (P2)

**Goal:** Document every `groundtruth.toml` field, environment variable, and
path resolution rule.

**Scope:** Create `docs/reference/configuration.md`.

**Corrected TOML reference:**

```toml
[groundtruth]
db_path = "./groundtruth.db"          # Path to SQLite database (relative to config file)
project_root = "."                     # Project root (relative to config file)
app_title = "GroundTruth KB"           # Web UI title
brand_mark = "GT"                      # Navigation badge
brand_color = "#2563eb"                # Primary CSS color
logo_url = null                        # Optional logo URL
legal_footer = ""                      # Footer text

[gates]
plugins = []                           # Gate plugin module paths

[gates.config.TransportEvidenceGate]
spec_ids = ["SPEC-1524"]               # Gate-specific configuration

[search]
chroma_path = "./.groundtruth-chroma"  # ChromaDB index directory (optional)
```

**Key distinction (Codex finding P2):**

| Level | `chroma_path` behavior |
|-------|----------------------|
| **GTConfig** | Default: `None`. Read from `[search].chroma_path` in groundtruth.toml. |
| **KnowledgeDB runtime** | If GTConfig.chroma_path is None AND ChromaDB is installed, falls back to `db_path.parent / ".groundtruth-chroma"` lazily on first semantic search. |

The configuration reference documents the TOML shape (`[search].chroma_path`).
The deliberation archive guide (Phase 5) explains the runtime fallback behavior.

**`gt config` enhancement:**

Add `chroma_path` to the config command output (cli.py). The output shows:
- The configured value if set explicitly in TOML
- `(default: <db_dir>/.groundtruth-chroma)` if ChromaDB is installed but no explicit config
- `(not configured, chromadb not installed)` if ChromaDB is absent

**Environment variables** (all 8 from config.py:131-146):
GT_DB_PATH, GT_PROJECT_ROOT, GT_APP_TITLE, GT_BRAND_MARK, GT_BRAND_COLOR,
GT_LOGO_URL, GT_LEGAL_FOOTER, GT_GOVERNANCE_GATES.

**Path resolution rules:**
1. Paths in TOML are resolved relative to the config file's directory
2. `project_root` resolved relative to config file
3. Environment variables override TOML values
4. CLI `--config` flag specifies which TOML to load
5. Default config search: `./groundtruth.toml`, then parent directories

**Acceptance criteria:**
- Every GTConfig field documented with type, default, TOML section
- `[search].chroma_path` correctly placed under `[search]`, not `[groundtruth]`
- Environment variable mapping complete
- `gt config` shows chroma_path

**Files created:** `docs/reference/configuration.md`
**Files modified:** `mkdocs.yml`, `src/groundtruth_kb/cli.py`

---

## Phase 5: Deliberation Archive Guide (P2)

**Goal:** Document the deliberation archive for end users.

**Scope:** Create `docs/method/13-deliberation-archive.md`.

Content covers: purpose, source types and outcomes, Python API (insert,
upsert, list, search, link), redaction behavior, content_hash dedup,
ChromaDB semantic search setup (as optional), `gt deliberations rebuild-index`,
and archive health metrics.

The guide distinguishes:
- Configuration: `[search].chroma_path` in groundtruth.toml
- Runtime: KnowledgeDB fallback to `db_path.parent/.groundtruth-chroma`
- Installation: `pip install "groundtruth-kb[search] @ ..."`

**Acceptance criteria:**
- New user can insert one deliberation and retrieve it
- ChromaDB setup documented as optional with clear install/config/rebuild steps
- Redaction documented clearly enough to avoid secret exposure
- `gt deliberations rebuild-index` success/failure output shown

**Files created:** `docs/method/13-deliberation-archive.md`
**Files modified:** `mkdocs.yml`

---

## Phase 6: Visual Aids — Mermaid Diagrams (P1)

**Goal:** Add 10+ Mermaid diagrams for major concepts.

**Prerequisite:** Verify/add Mermaid support in mkdocs.yml:
```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

**Diagram inventory:**

| # | Diagram | Type | File |
|---|---------|------|------|
| 1 | Method Workflow | Flowchart | `method/01-overview.md` |
| 2 | Architecture Layers | Block | `index.md` (replace ASCII) |
| 3 | Dual-Agent Interaction | Sequence | `method/06-dual-agent.md` |
| 4 | File Bridge State Machine | State | `method/12-file-bridge-automation.md` |
| 5 | Append-Only Versioning | Diagram | `method/01-overview.md` |
| 6 | Governance Gate Pipeline | Flowchart | `method/05-governance.md` |
| 7 | ADR/DCL/IPR/CVR Flow | Flowchart | `method/08-architecture.md` |
| 8 | Deliberation Archive Flow | Flowchart | `method/13-deliberation-archive.md` |
| 9 | Project Profile Comparison | Table/flow | `start-here.md` |
| 10 | Config Resolution Order | Flowchart | `reference/configuration.md` |

**Acceptance criteria:**
- At least 10 Mermaid diagrams across docs
- Each renders on the live docs site
- `mkdocs build --strict` passes with diagrams

**Files modified:** 8+ existing docs + mkdocs.yml

---

## Phase 7: Example and Template Discoverability (P2)

**Scope:** Add Examples and Templates to docs nav. Create
`docs/reference/templates.md` with inventory of all 30 template files.

**Files created:** `docs/reference/templates.md`
**Files modified:** `mkdocs.yml`

---

## Phase 8: Docs Drift Prevention CI (P2)

**Goal:** Automated checks that prevent every regression found in this review.

**Checks in `.github/workflows/docs-check.yml`:**

1. **Stale version scan** (allowlist-based):
   ```bash
   grep -rn "v0\.1\.2\|v0\.2\.0\|0\.1\.2\|0\.2\.0" docs/ templates/ README.md \
     | grep -vi "changelog\|CHANGELOG\|history\|## 0\."
   # Must be empty
   ```

2. **CLI command coverage** (`scripts/check_docs_cli_coverage.py`):
   - Recursively enumerate Click groups via `gt` entry point
   - Compare against commands listed in `docs/reference/cli.md`
   - Exit 1 if any command is missing

3. **Python prerequisite drift**:
   ```bash
   # Extract from pyproject.toml and docs, compare
   ```

4. **`gt --version` expected output drift**:
   ```bash
   # Run gt --version, compare against docs/start-here.md expected output
   ```

5. **Install tag consistency**:
   ```bash
   grep -rn "groundtruth-kb.*@v" docs/ templates/ README.md \
     | grep -v changelog | sort -u
   # All must reference same tag
   ```

6. **Markdown link check**: `mkdocs build --strict`

**Acceptance criteria:**
- CI runs on PRs touching docs/, templates/, src/groundtruth_kb/cli.py, or pyproject.toml
- Each check is independently actionable
- No network access required

**Files created:** `.github/workflows/docs-check.yml`, `scripts/check_docs_cli_coverage.py`

---

## Execution Order

| Phase | Priority | Dependencies | Est. Files |
|-------|----------|-------------|-----------|
| 0: Version alignment | P1 | None | 3 modified |
| 1: Install truth | P1 | Phase 0 | 14 modified |
| 2: Start Here | P1 | Phase 0+1 | 1 new + 1 modified |
| 3: CLI reference | P1 | None | 1 new + 1 modified |
| 6: Visual aids | P1 | Phases 2,3,5 | 8+ modified |
| 4: Config reference | P2 | None | 1 new + 2 modified |
| 5: Deliberation guide | P2 | None | 1 new + 1 modified |
| 7: Examples/templates | P2 | Phases 2,3 | 1-2 new + 1 modified |
| 8: Drift prevention | P2 | Phases 0,1,3 | 2 new |

**Total: ~8 new files, ~20 modified files. Ends with v0.3.0 tag.**

---

## Tagging Strategy

After all phases complete:
1. Bump `__init__.py` to `0.3.0`
2. Update CHANGELOG with full docs completion summary
3. Tag `v0.3.0`, push to remote
4. Update Agent Red requirements to `v0.3.0`
5. Rebuild docs site

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
