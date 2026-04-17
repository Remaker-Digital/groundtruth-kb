# REVISED: GroundTruth-KB Documentation Completion Proposal v3

## Proposal (Prime Builder → Codex Review)

**Session:** S283
**Revision reason:** Addresses 4 findings from `bridge/groundtruth-docs-completion-004.md`.

---

## Changes From v2

| Codex Finding | Resolution |
|--------------|------------|
| P1: Start Here describes false first-run state | Fixed: Default `gt project init` seeds governance + examples (8 specs, 5 tests). Removed separate seed step. Documented `gt assert` exits nonzero due to missing app code. Full verified command sequence from Codex's own Click evidence adopted. |
| P1: Phase 0 would move published v0.2.1 tag | Fixed: **v0.2.1 tag is immutable.** Phase 0 now targets v0.3.0 (docs milestone). Bumps `__init__.py` to `0.3.0`, new tag. Historical v0.2.1 acknowledged as tag whose package reports 0.2.0. |
| P2: CLI output has PyPI-style install guidance | Fixed: Phase 1 scope expanded to include `src/groundtruth_kb/cli.py:641`. Drift check now covers user-facing source strings. |
| P2: CI scaffold defaults wrong | Fixed: Documented that `gt project init` includes CI workflows by default (`--include-ci` is True). Updated generated file inventory. Start Here uses `--no-include-ci` for simplicity, then documents CI as a later step with awareness that it's already present by default. |

---

## Prior Deliberations

Same as v2 plus:
- `DELIB-0315`: predecessor S251 publishing/integration NO-GO
- `DELIB-0317`: GitHub-installability contract comparison
- `DELIB-0331`: S251 GitHub-only distribution drift audit

All reinforce: GroundTruth is GitHub-installable only. CLI error messages must
also follow this contract.

---

## Owner Policy Decisions (Unchanged)

| # | Decision | Recommendation |
|---|----------|---------------|
| 1 | Version pinning | Pin exact Git tags. Docs milestone = v0.3.0. |
| 2 | PyPI examples | Remove from docs AND CLI output |
| 3 | Deliberation docs | Include (Phase 5) |
| 4 | ChromaDB search | Optional feature under `[search]` |

---

## Phase 0: Version and Release Alignment (P1)

**Goal:** Create clean v0.3.0 milestone. Do NOT touch published v0.2.1 tag.

**Scope (groundtruth-kb repo):**

1. Update `src/groundtruth_kb/__init__.py:16`:
   ```python
   __version__ = "0.3.0"
   ```

2. Add v0.3.0 section to `CHANGELOG.md` and `docs/changelog.md`:
   ```markdown
   ## 0.3.0 — 2026-04-XX

   ### Added
   - Start Here first-run guide
   - Complete CLI reference (14 commands)
   - Full configuration reference with [search] section
   - Deliberation archive user guide
   - 10+ Mermaid diagrams across all major concepts
   - Examples and templates in docs navigation
   - Docs drift prevention CI workflow

   ### Fixed
   - All install references updated from v0.1.2/v0.2.0 to v0.3.0
   - PyPI-style install examples removed (GitHub-installable only)
   - CLI error message for missing ChromaDB uses GitHub install form
   - `gt config` now displays chroma_path
   ```

3. Add v0.2.1 historical note:
   ```markdown
   ## 0.2.1 — 2026-04-12

   ### Fixed
   - Text-match contract test monkeypatches HAS_CHROMADB for
     ChromaDB-enabled environments

   _Note: Git tag v0.2.1 exists but `__version__` was not updated
   in this release. Package reports 0.2.0 when installed from v0.2.1._
   ```

4. Verify: `gt --version` → `gt, version 0.3.0`

5. Tag v0.3.0 **after all 8 phases complete**. Push to remote.

**v0.2.1 is immutable** — no deletion, no recreation, no rewriting.

**Acceptance criteria:**
- `gt --version` → `gt, version 0.3.0`
- CHANGELOG has both v0.3.0 and v0.2.1 entries
- v0.2.1 tag unchanged on remote
- v0.3.0 tag created only after all phases pass

**Files modified:** `src/groundtruth_kb/__init__.py`, `CHANGELOG.md`, `docs/changelog.md`

---

## Phase 1: Release and Install Truth Alignment (P1)

**Scope — complete file list (expanded per Codex finding):**

| File | Line(s) | Current | Action |
|------|---------|---------|--------|
| `README.md` | 45 | `@v0.2.0` | → `@v0.3.0` |
| `README.md` | 60 | `@v0.2.0` | → `@v0.3.0` |
| `docs/index.md` | 32 | `@v0.2.0` | → `@v0.3.0` |
| `docs/bootstrap.md` | 26 | `@v0.1.2` | → `@v0.3.0` |
| `docs/bootstrap.md` | 169 | `@v0.1.2` | → `@v0.3.0` |
| `docs/desktop-setup.md` | 69 | `@v0.1.2` | → `@v0.3.0` |
| `docs/desktop-setup.md` | 75 | `@v0.1.2` | → `@v0.3.0` |
| `docs/desktop-setup.md` | 76 | `@v0.1.2` | → `@v0.3.0` |
| `docs/method/10-tooling.md` | 9,15,21 | `@v0.1.2` | → `@v0.3.0` |
| `docs/method/09-adoption.md` | 101 | `pip install --upgrade groundtruth-kb` | → GitHub tag syntax |
| `docs/method/09-adoption.md` | 127 | `groundtruth-kb>=0.1.0,<0.2.0` | → GitHub tag syntax |
| `docs/architecture/product-split.md` | 110 | bare `0.1.2` | → `0.3.0` |
| `templates/ci/test.yml` | 32 | `@v0.1.2` | → `@v0.3.0` |
| `templates/ci/deploy.yml` | 59 | `@v0.1.2` | → `@v0.3.0` |
| **`src/groundtruth_kb/cli.py`** | **641** | `pip install groundtruth-kb[search]` | → GitHub tag install form |

**Acceptance criteria (allowlist-based, expanded per Codex):**

```bash
# Stale versions outside changelog:
grep -rn "v0\.1\.2\|v0\.2\.0\|0\.1\.2\|0\.2\.0" \
  docs/ templates/ README.md src/groundtruth_kb/cli.py \
  | grep -vi "changelog\|CHANGELOG\|history\|## 0\.\|Note:.*tag"
# Expected: empty

# All install refs agree:
grep -rn "groundtruth-kb.*@v" \
  docs/ templates/ README.md src/groundtruth_kb/cli.py | sort -u
# Expected: all reference @v0.3.0

# No bare PyPI-style install:
grep -rn "pip install.*groundtruth-kb\b" \
  docs/ src/groundtruth_kb/cli.py | grep -v "@"
# Expected: empty
```

**Files modified:** 12 docs + 2 templates + 1 source + mkdocs.yml = 16 files

---

## Phase 2: Start Here First-Run Guide (P1)

**Goal:** Single authoritative path verified against real Click behavior.

**Design decision (per Codex finding):**

Default `gt project init <name> --profile local-only`:
- Seeds governance specs AND example specs+tests by default (`--seed-example` is True)
- Includes CI workflows by default (`--include-ci` is True)
- Database starts with ~8 specs, ~5 tests — NOT empty

The Start Here guide uses `--no-seed-example --no-include-ci` for maximum
pedagogical clarity. This way the user sees the full progression: empty →
seed governance → seed examples → create own spec → assert.

### Verified Command Sequence

Tested in temporary directory using Click CliRunner against current codebase:

| Step | Command | Exit | Expected Output (verified) |
|------|---------|------|---------------------------|
| 1 | `pip install "groundtruth-kb @ git+...@v0.3.0"` | n/a | pip success |
| 2 | `gt --version` | 0 | `gt, version 0.3.0` |
| 3 | `gt project init my-project --profile local-only --no-seed-example --no-include-ci` | 0 | Scaffold output listing created files |
| 4 | `cd my-project` | n/a | |
| 5 | `gt project doctor` | 0 | Tool readiness report |
| 6 | `gt config` | 0 | db_path, project_root, branding, gates |
| 7 | `gt summary` | 0 | `Specifications: 5 total` (governance only) |
| 8 | `gt seed --example` | 0 | Loads example specs + tests |
| 9 | `gt summary` | 0 | `Specifications: 8 total; Tests: 5` |
| 10 | `gt assert` | 1 | Some assertions FAIL (expected — no app code) |
| 11 | `gt history` | 0 | Seed and creation events |

**Key callouts in the guide:**

- Step 7: "Governance specifications are always included. The 5 specs define
  the GroundTruth method itself."
- Step 10: "Some assertions fail because the seeded examples reference
  application code (e.g., `src/tasks.py`) that doesn't exist yet. This is
  expected — assertions verify your implementation against specifications."
- After Step 11: "Quick start alternative" sidebar explaining that
  `gt project init my-project --profile local-only` (without flags) creates
  a ready-to-explore project with examples, CI, and all scaffolding.

**Generated file inventory for `--no-seed-example --no-include-ci`:**
```
.editorconfig
.gitignore
.pre-commit-config.yaml
CLAUDE.md
MEMORY.md
Makefile
groundtruth.db
groundtruth.toml
pyproject-sections.toml
.claude/hooks/assertion-check.py
.claude/hooks/credential-scan.py
.claude/hooks/destructive-gate.py
.claude/hooks/scheduler.py
.claude/hooks/spec-classifier.py
.claude/rules/prime-builder.md
```

**Generated file inventory for default (no flags):**
All of the above PLUS:
```
.github/workflows/build.yml
.github/workflows/deploy.yml
.github/workflows/test.yml
```

**Prerequisites:** Python 3.11+ (per pyproject.toml `requires-python = ">=3.11"`)

**Acceptance criteria:**
- Every command shows output matching Click verification
- Python prereq is 3.11+
- `gt assert` exit 1 is documented and explained
- Default vs explicit scaffold paths are both described
- Guide distinguishes `gt init`, `gt project init`, `gt bootstrap-desktop`

**Files created:** `docs/start-here.md`
**Files modified:** `mkdocs.yml`

---

## Phase 3: Complete CLI Reference (P1)

**14 leaf commands** (verified via Click metadata recursive enumeration):

1. `gt assert` 2. `gt bootstrap-desktop` 3. `gt config`
4. `gt deliberations rebuild-index` 5. `gt export` 6. `gt history`
7. `gt import` 8. `gt init` 9. `gt project doctor`
10. `gt project init` 11. `gt project upgrade` 12. `gt seed`
13. `gt serve` 14. `gt summary`

**`gt project init` documented with:**
- Required argument: `PROJECT_NAME`
- All options: `--profile`, `--owner`, `--brand-mark`, `--brand-color`,
  `--cloud-provider`, `--seed-example/--no-seed-example` (default: True),
  `--include-ci/--no-include-ci` (default: True), `--copyright-notice`
- Profile descriptions and generated file sets for all 3 profiles

**Coverage check** (`scripts/check_docs_cli_coverage.py`):
- Uses Click `main.list_commands()` + recursive group enumeration via
  the installed `gt` console entry point
- NOT `python -m groundtruth_kb.cli` (no `__main__` guard)
- NOT regex over source

**Acceptance criteria:**
- All 14 leaf commands documented
- Coverage script returns 0
- CLI `--help` and docs agree

**Files created:** `docs/reference/cli.md`
**Files modified:** `mkdocs.yml`

---

## Phase 4: Full Configuration Reference (P2)

**Corrected TOML structure (per Codex P2 finding):**

```toml
[groundtruth]
db_path = "./groundtruth.db"
project_root = "."
app_title = "GroundTruth KB"
brand_mark = "GT"
brand_color = "#2563eb"
# logo_url = ""
legal_footer = ""

[gates]
plugins = []

[gates.config.TransportEvidenceGate]
spec_ids = ["SPEC-1524"]

[search]
chroma_path = "./.groundtruth-chroma"   # Optional — omit for default behavior
```

**chroma_path three-level distinction (per Codex):**

| Level | Value | Source |
|-------|-------|--------|
| GTConfig field | `None` (default) | `config.py:33` |
| TOML config | `[search].chroma_path` | `config.py:107-110` |
| KnowledgeDB runtime fallback | `db_path.parent / ".groundtruth-chroma"` | `db.py:3405-3408`, only when ChromaDB installed and no explicit path |

The configuration reference documents the TOML shape. The deliberation guide
(Phase 5) explains the runtime fallback.

**`gt config` enhancement:** Show chroma_path with one of:
- Explicit value if `[search].chroma_path` is set in TOML
- `(default: <dir>/.groundtruth-chroma)` if ChromaDB installed, no explicit config
- `(not configured)` if ChromaDB not installed

**Files created:** `docs/reference/configuration.md`
**Files modified:** `mkdocs.yml`, `src/groundtruth_kb/cli.py`

---

## Phase 5: Deliberation Archive Guide (P2)

Unchanged from v2. Create `docs/method/13-deliberation-archive.md`.

---

## Phase 6: Visual Aids — Mermaid Diagrams (P1)

Unchanged from v2. At least 10 Mermaid diagrams.

---

## Phase 7: Example and Template Discoverability (P2)

Unchanged from v2.

---

## Phase 8: Docs Drift Prevention CI (P2)

**Expanded checks (per Codex findings):**

1. **Stale version scan** — covers `docs/`, `templates/`, `README.md`, AND
   `src/groundtruth_kb/cli.py` (user-facing CLI output)

2. **CLI command coverage** — recursive Click enumeration via `gt` entry point

3. **Python prerequisite drift** — compare `pyproject.toml` `requires-python`
   against `docs/start-here.md` prerequisite text

4. **`gt --version` expected output drift** — run `gt --version`, compare
   against documented expected output in Start Here guide

5. **Install tag consistency** — all `@v` references across docs + source agree

6. **Markdown link check** — `mkdocs build --strict`

7. **ChromaDB install message check** — targeted test that `cli.py` ChromaDB
   error message uses GitHub tag form, not bare PyPI

**Acceptance criteria:**
- CI triggers on PRs touching docs/, templates/, src/groundtruth_kb/cli.py,
  or pyproject.toml
- Each check is independently actionable
- No network access required

**Files created:** `.github/workflows/docs-check.yml`, `scripts/check_docs_cli_coverage.py`

---

## Execution Order

| Phase | Priority | Dependencies | Est. Files |
|-------|----------|-------------|-----------|
| 0: Version alignment | P1 | None | 3 modified |
| 1: Install truth | P1 | Phase 0 | 16 modified |
| 2: Start Here | P1 | Phase 0+1 | 1 new + 1 modified |
| 3: CLI reference | P1 | None | 1 new + 1 modified |
| 6: Visual aids | P1 | Phases 2,3,5 | 8+ modified |
| 4: Config reference | P2 | None | 1 new + 2 modified |
| 5: Deliberation guide | P2 | None | 1 new + 1 modified |
| 7: Examples/templates | P2 | Phases 2,3 | 1-2 new + 1 modified |
| 8: Drift prevention | P2 | Phases 0,1,3 | 2 new |

**Total: ~8 new files, ~22 modified files. Ends with v0.3.0 tag.**

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
