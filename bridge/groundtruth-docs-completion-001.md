# GroundTruth-KB Documentation Completion Proposal

## Proposal (Prime Builder → Codex Review)

**Session:** S283
**Source:** `INSIGHTS-2026-04-12-14-36-GROUNDTRUTH-DOCS-COMPLETION-ADVISORY.md`
**Owner direction:** "Prepare an extensive implementation proposal to bring the GroundTruth-KB project up to our standards for published work."

---

## Prior Deliberations

```
DELIB-0316: S251 GroundTruth-KB publishing and Agent Red integration plan review [go]
DELIB-0332: S251 Correction Audit — GroundTruth distribution model GitHub-installable [informational]
DELIB-0474: GroundTruth Execution Plan for Prime [informational]
DELIB-0633: GroundTruth-KB Strategic Assessment [informational]
DELIB-0245: S243 G3e Example Project Proposal Review [no_go]
```

Key prior decisions: GT-kb is GitHub-installable only (no PyPI). The example project
was accepted after revision in S243. Documentation site is live at
`remaker-digital.github.io/groundtruth-kb`.

---

## Context

The owner evaluated GT-kb documentation readiness and asked three questions:
1. Does the documentation adequately explain intended use?
2. Does it fully explain install → configure → use?
3. Does it use visual aids extensively?

Assessment: the core method is well-written (12 parts, ~2,400 lines), but the
documentation has significant gaps that prevent it from meeting published-work
standards. Codex's advisory identified 8 areas and 4 owner decisions.

### Current State

| Metric | Value |
|--------|-------|
| Doc files | 21 (2,398 lines total) |
| CLI commands | 13 implemented, 8 documented in tooling guide |
| Config fields | 10 in GTConfig, 9 in `gt config` output (chroma_path missing) |
| Version pins | v0.1.2 in 7 locations, v0.2.0 in 3 locations, v0.2.1 is current |
| Visual aids | 0 diagrams, 0 images, 0 Mermaid blocks |
| Deliberation docs | 0 (feature fully implemented but invisible) |
| Example project | Present but not in docs nav |
| Nav sections | 6 (missing: Examples, Templates, CLI Reference, Config Reference) |

---

## Owner Policy Decisions (Recommended Defaults)

These decisions are embedded in the proposal with recommended defaults. Owner
may override any during approval.

| # | Question | Recommendation | Rationale |
|---|----------|---------------|-----------|
| 1 | Version pinning | Pin exact Git tags (currently v0.2.1) | Reproducible installs. Single `GT_VERSION` variable in docs config makes updates atomic. |
| 2 | PyPI examples | Remove until PyPI publication exists | Prevents confusion. Add back when PyPI is real. |
| 3 | Deliberation archive docs | Include in this proposal (not deferred) | Feature is live in Agent Red with 705 records. Undocumented features create hidden support burden. |
| 4 | ChromaDB search | Document as optional advanced feature | Clearly separate from core workflow. Extra dependency should be opt-in with clear setup guide. |

---

## Phases

### Phase 1: Version Alignment and Install Hygiene (P1)

**Goal:** Eliminate all stale version references. Single source of truth for
current version.

**Scope:**

1. Add `GT_INSTALL_TAG` variable to `mkdocs.yml` extra config:
   ```yaml
   extra:
     gt_version: "0.2.1"
     gt_install_tag: "v0.2.1"
   ```

2. Update all install commands to use the current tag. Affected files (7 locations):
   - `docs/bootstrap.md:26` — v0.1.2 → v0.2.1
   - `docs/bootstrap.md:169` — v0.1.2 → v0.2.1
   - `docs/desktop-setup.md:69` — v0.1.2 → v0.2.1
   - `docs/desktop-setup.md:75` — v0.1.2 → v0.2.1
   - `docs/desktop-setup.md:76` — v0.1.2 → v0.2.1
   - `templates/ci/test.yml:32` — v0.1.2 → v0.2.1
   - `templates/ci/deploy.yml:59` — v0.1.2 → v0.2.1

3. Update `docs/method/10-tooling.md:9,15,21` — 3 install variant examples.

4. Remove PyPI-style version range example from `docs/method/09-adoption.md:126-130`.
   Replace with GitHub tag pinning guidance:
   ```
   groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1
   ```

5. Add upgrade instructions noting users should update the tag when new
   versions are released.

**Acceptance criteria:**
- `grep -r "v0.1.2" docs/ templates/` returns only changelog/history context
- All install commands reference v0.2.1
- No PyPI-style `>=0.1.0,<0.2.0` examples remain

**Files modified:** 6 docs + 2 templates + mkdocs.yml

---

### Phase 2: Start Here First-Run Guide (P1)

**Goal:** Single authoritative path from zero to working system.

**Scope:** Create `docs/start-here.md` — a self-contained guide that replaces
the need to cross-reference README, bootstrap, and desktop-setup.

**Outline:**

```markdown
# Start Here

## Prerequisites
- Python 3.10+
- Git
- (optional) Docker for containerized workflows

## Step 1: Install GroundTruth
pip install "groundtruth-kb @ git+https://github.com/..."

## Step 2: Verify Installation
gt --version
# Expected: groundtruth-kb 0.2.1

## Step 3: Initialize a New Project
gt project init --profile local-only
# Creates: groundtruth.toml, groundtruth.db, .claude/ scaffolding

## Step 4: Check Workstation Readiness
gt project doctor
# Expected: all checks pass or clear guidance on missing tools

## Step 5: Inspect Your Configuration
gt config
# Shows: db_path, project_root, branding, gates

## Step 6: View the Empty Database
gt summary
# Shows: 0 specs, 0 tests, 0 work items

## Step 7: Load Starter Data
gt seed --examples
# Loads governance specs + example specifications

## Step 8: Create Your First Specification
gt summary  # Now shows seeded content

## Step 9: Run Assertions
gt assert
# Shows: assertion results with pass/fail

## Step 10: Start the Web UI (optional)
pip install "groundtruth-kb[web] @ git+..."
gt serve
# Open http://localhost:8090

## Step 11: Add CI (optional)
# Copy templates/ci/test.yml to .github/workflows/

## What's Next?
- Read the Method Guide for the full discipline
- Explore the Example Project for a guided walkthrough
- See the CLI Reference for all available commands
```

Each step shows the exact command AND expected output. Windows/Unix differences
called out where they matter (path separators, shell syntax).

**Acceptance criteria:**
- A new user can follow the guide from zero to `gt serve` without consulting
  other documents
- Every command shows expected success output
- Guide distinguishes `gt init` (legacy), `gt project init` (current), and
  `gt bootstrap-desktop` (same-day prototype)

**Files created:** `docs/start-here.md`
**Files modified:** `mkdocs.yml` (add to Getting Started section, first position)

---

### Phase 3: Complete CLI Reference (P1)

**Goal:** Document all 13 CLI commands with options, examples, and expected output.

**Scope:** Create `docs/reference/cli.md` — generated/verified from Click command
metadata.

**Coverage (all 13 commands):**

| Command | Group | Status in Current Docs |
|---------|-------|----------------------|
| `gt init` | root | Mentioned in bootstrap only |
| `gt bootstrap-desktop` | root | Mentioned in bootstrap only |
| `gt seed` | root | Mentioned in bootstrap only |
| `gt summary` | root | In 10-tooling.md |
| `gt assert` | root | In 10-tooling.md |
| `gt history` | root | In 10-tooling.md |
| `gt export` | root | In 10-tooling.md |
| `gt import` | root | In 10-tooling.md |
| `gt config` | root | In 10-tooling.md |
| `gt serve` | root | In 10-tooling.md |
| `gt project init` | project | NOT documented |
| `gt project doctor` | project | NOT documented |
| `gt project upgrade` | project | NOT documented |
| `gt deliberations rebuild-index` | deliberations | NOT documented |

Each entry includes:
- Synopsis: `gt <command> [OPTIONS]`
- Description (from Click help text)
- All options with types and defaults
- Usage example with expected output
- Notes on when to use and common pitfalls

**`gt project init` profiles** require special attention:
- `local-only` — single-agent, no bridge
- `dual-agent` — Prime + Codex with bridge
- `dual-agent-webapp` — above + web UI + Docker

Each profile's generated file set must be documented.

**Acceptance criteria:**
- Every command exposed by `gt --help` has a docs entry
- CLI `--help` output and docs do not materially disagree
- `gt project init` profile options are fully explained

**Files created:** `docs/reference/cli.md`
**Files modified:** `mkdocs.yml` (add to Reference section)

---

### Phase 4: Full Configuration Reference (P2)

**Goal:** Document every `groundtruth.toml` field, environment variable, and
path resolution rule.

**Scope:** Create `docs/reference/configuration.md`.

**Coverage:**

```toml
[groundtruth]
db_path = "./groundtruth.db"          # Path to SQLite database
project_root = "."                     # Project root for assertions
chroma_path = "./.groundtruth-chroma"  # ChromaDB index (optional)
app_title = "GroundTruth KB"           # Web UI title
brand_mark = "GT"                      # Navigation badge
brand_color = "#2563eb"                # Primary CSS color
logo_url = null                        # Optional logo URL
legal_footer = ""                      # Footer text

[gates]
plugins = []                           # Gate plugin module paths

[gates.config.<GateName>]
# Gate-specific key-value pairs
```

**Environment variable overrides:**
- GT_DB_PATH, GT_PROJECT_ROOT, GT_APP_TITLE, GT_BRAND_MARK,
  GT_BRAND_COLOR, GT_LOGO_URL, GT_LEGAL_FOOTER, GT_GOVERNANCE_GATES

**Path resolution rules** (from `config.py:70-110`):
- Paths relative to the config file's directory
- `project_root` resolved relative to config file
- `chroma_path` defaults to beside the SQLite DB if not specified

**`gt config` enhancement:**
Add `chroma_path` to the `gt config` output (cli.py:458-465). Currently omitted
despite being a resolved GTConfig field.

**Acceptance criteria:**
- Every GTConfig field is documented with type, default, and usage
- Environment variable mapping is complete
- Path resolution rules are explicit and testable
- `gt config` shows chroma_path when configured

**Files created:** `docs/reference/configuration.md`
**Files modified:** `mkdocs.yml`, `src/groundtruth_kb/cli.py` (add chroma_path to config output)

---

### Phase 5: Deliberation Archive Guide (P2)

**Goal:** Document the deliberation archive for end users.

**Scope:** Create `docs/method/13-deliberation-archive.md`.

**Outline:**

```markdown
# Deliberation Archive

## Purpose
Durable record of reviews, proposals, owner decisions, and session
harvests with optional semantic search.

## Source Types
- lo_review, bridge_thread, owner_conversation, proposal, report, session_harvest

## Outcomes
- go, no_go, deferred, owner_decision, informational

## Core Workflow
1. Record deliberations via Python API or harvest script
2. Link to specs and work items
3. Search by keyword (SQLite) or natural language (ChromaDB)

## Python API
- db.insert_deliberation()
- db.upsert_deliberation_source()
- db.list_deliberations()
- db.search_deliberations()
- db.link_deliberation_spec()
- db.link_deliberation_work_item()

## Redaction
- Content is redacted before storage
- Credential patterns are automatically scrubbed
- content_hash preserves pre-redaction identity for dedup

## Semantic Search (optional)
- Install: pip install "groundtruth-kb[search]"
- Configure: chroma_path in groundtruth.toml
- Build index: gt deliberations rebuild-index
- Fallback: SQLite LIKE when ChromaDB unavailable
- Results include search_method, score, matched_chunk_preview

## Agent Integration
- Session-wrap harvest automates archival
- Bridge threads archived after VERIFIED status
- Deliberation search mandatory before proposals/reviews
```

**Acceptance criteria:**
- A new user can insert one deliberation and retrieve it
- ChromaDB setup is documented as optional
- Redaction behavior is documented clearly enough to avoid secret exposure
- `gt deliberations rebuild-index` success/failure output is shown

**Files created:** `docs/method/13-deliberation-archive.md`
**Files modified:** `mkdocs.yml` (add to Method section)

---

### Phase 6: Visual Aids — Diagrams and Architecture (P1)

**Goal:** Add Mermaid diagrams for all major concepts. MkDocs Material supports
Mermaid natively.

**Scope:** Add diagrams to existing and new docs. Minimum 8 diagrams:

| # | Diagram | Type | Location |
|---|---------|------|----------|
| 1 | **Method Workflow** | Flowchart | `docs/method/01-overview.md` |
|   | spec → WI → test → backlog → implement → assert → promote | | |
| 2 | **Architecture Layers** | Block diagram | `docs/index.md` (replace ASCII) |
|   | SQLite DB → CLI → Web UI → Python API | | |
| 3 | **Dual-Agent Interaction** | Sequence diagram | `docs/method/06-dual-agent.md` |
|   | Prime ↔ bridge files ↔ Codex review cycle | | |
| 4 | **File Bridge State Machine** | State diagram | `docs/method/12-file-bridge-automation.md` |
|   | NEW → GO/NO-GO → REVISED → VERIFIED | | |
| 5 | **Append-Only Versioning** | Diagram | `docs/method/01-overview.md` |
|   | Insert v1 → Insert v2 → current_view shows latest | | |
| 6 | **Governance Gate Pipeline** | Flowchart | `docs/method/05-governance.md` |
|   | Pre-gate check → assertion → pass/block → evidence | | |
| 7 | **ADR/DCL/IPR/CVR Flow** | Flowchart | `docs/method/08-architecture.md` |
|   | Decision → ADR → DCL → IPR (pre-impl) → CVR (post-impl) | | |
| 8 | **Deliberation Archive Flow** | Flowchart | `docs/method/13-deliberation-archive.md` |
|   | Source → redact → hash → insert → optional Chroma index | | |

**Additional visual aids:**

| # | Visual | Type | Location |
|---|--------|------|----------|
| 9 | **Project Profile Comparison** | Table/diagram | `docs/start-here.md` |
|   | local-only vs dual-agent vs dual-agent-webapp | | |
| 10 | **Config Resolution Order** | Flowchart | `docs/reference/configuration.md` |
|    | defaults → toml file → env vars → CLI flags | | |

**Implementation:** Mermaid code blocks in markdown. MkDocs Material renders
them natively with the `pymdownx.superfences` extension (already configured
in mkdocs.yml via `markdown_extensions`).

**Verify Mermaid support** — check that `pymdownx.superfences` with
`custom_fences` for mermaid is in mkdocs.yml. Add if missing:

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

**Acceptance criteria:**
- At least 8 Mermaid diagrams across docs
- Each diagram renders correctly on the docs site
- Complex concepts (dual-agent, bridge, governance) have visual representation
- Diagrams use consistent styling

**Files modified:** 8+ existing docs + mkdocs.yml (Mermaid extension)

---

### Phase 7: Example and Template Discoverability (P2)

**Goal:** Make examples and templates findable from the docs site.

**Scope:**

1. Add example project to mkdocs.yml navigation:
   ```yaml
   - Examples:
       - Task Tracker Walkthrough: examples/task-tracker/WALKTHROUGH.md
   ```
   Requires either copying WALKTHROUGH.md to `docs/` or configuring mkdocs
   to serve from the examples directory.

2. Add templates reference to mkdocs.yml:
   ```yaml
   - Reference:
       - CLI: reference/cli.md
       - Configuration: reference/configuration.md
       - Assertion Language: reference/assertion-language.md
       - Templates: reference/templates.md
   ```

3. Create `docs/reference/templates.md`:
   - Inventory of all 30 template files organized by category
   - Which templates are required vs optional
   - Customization guidance (which files to edit, which to leave as-is)
   - How `gt project init` and `gt bootstrap-desktop` use templates
   - CI template setup instructions

**Acceptance criteria:**
- Docs site nav includes Examples and Templates
- A new user can find the example project and templates from the docs homepage
- Template ownership rules (managed vs project-owned) are clear

**Files created:** `docs/reference/templates.md`, possibly `docs/examples/` copies
**Files modified:** `mkdocs.yml`

---

### Phase 8: Docs Drift Prevention (P2)

**Goal:** Automated checks that prevent documentation from going stale again.

**Scope:** Create `.github/workflows/docs-check.yml` CI workflow.

**Checks:**

1. **Stale version references:**
   ```bash
   # Fail if v0.1.2 appears outside changelog
   grep -rn "v0\.1\.2" docs/ templates/ --include="*.md" --include="*.yml" \
     | grep -v changelog | grep -v CHANGELOG
   ```

2. **CLI command coverage:**
   ```python
   # Extract Click commands from cli.py, compare against docs/reference/cli.md
   # Fail if any command is missing from docs
   ```

3. **Install tag consistency:**
   ```bash
   # All pip install commands in docs/ should reference the same tag
   grep -rn "groundtruth-kb.*@v" docs/ templates/ | sort -u
   ```

4. **Markdown link validation:**
   ```bash
   # Use mkdocs build --strict to catch broken internal links
   mkdocs build --strict
   ```

5. **Mermaid syntax check:**
   ```bash
   # Verify all mermaid blocks parse without errors
   # (mkdocs build --strict catches rendering failures)
   ```

**Acceptance criteria:**
- CI runs on every PR touching docs/ or templates/
- Stale version pins fail the build
- New CLI commands without doc entries fail the build
- Broken links fail the build

**Files created:** `.github/workflows/docs-check.yml`, `scripts/check_docs_cli_coverage.py`
**Files modified:** None

---

## Execution Order

| Phase | Priority | Dependencies | Scope | Est. Files |
|-------|----------|-------------|-------|-----------|
| 1: Version alignment | P1 | None | 9 file edits | 9 modified |
| 2: Start Here guide | P1 | Phase 1 (correct versions) | 1 new + 1 edit | 2 |
| 3: CLI reference | P1 | None | 1 new + 1 edit | 2 |
| 6: Visual aids | P1 | Phases 2, 3, 5 (diagram targets exist) | 8+ modified | 8+ |
| 4: Config reference | P2 | None | 1 new + 2 edits | 3 |
| 5: Deliberation guide | P2 | None | 1 new + 1 edit | 2 |
| 7: Examples/templates | P2 | Phases 2, 3 (nav established) | 1-2 new + 1 edit | 2-3 |
| 8: Drift prevention | P2 | Phases 1, 3 (content to check) | 2 new | 2 |

**Total scope:** ~10 new files, ~15 modified files, all in the groundtruth-kb
repository. No Agent Red code changes.

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Version tag drift recurs | Phase 8 CI check catches it |
| Mermaid rendering issues | Test locally with `mkdocs serve` before pushing |
| Docs/CLI divergence | Phase 8 coverage check + CI |
| Large diff size | Phase by phase — each independently reviewable |
| GT-kb tag immutability | Phases 1-8 land on develop, tag after all phases complete |

---

## Tagging Strategy

After all 8 phases are complete and verified:
1. Update `__init__.py` version to `0.3.0`
2. Update CHANGELOG.md
3. Tag `v0.3.0` on main
4. Update Agent Red requirements to `v0.3.0`
5. Rebuild docs site

This gives the documentation completion a clean version milestone.

---

## Owner Decisions Embedded

The proposal assumes:
- Pin exact Git tags (Phase 1)
- Remove PyPI examples (Phase 1)
- Include deliberation docs (Phase 5)
- ChromaDB as optional advanced feature (Phase 5)

Override any of these during approval.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
