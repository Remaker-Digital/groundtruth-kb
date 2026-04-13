# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-04-12

### Added
- **Start Here** first-run guide with verified command sequence
- **CLI Reference** documenting all 14 commands with options and examples
- **Configuration Reference** with full `groundtruth.toml` field inventory
- **Deliberation Archive Guide** for the review/decision capture system
- 10+ Mermaid diagrams across method, architecture, and reference docs
- Examples and templates sections in docs site navigation
- Docs drift prevention CI workflow (version pins, CLI coverage, link checks)
- `gt config` now displays `chroma_path` when configured or defaulted
- SonarCloud analysis workflow with coverage reporting
- CodeQL weekly security scanning
- Semgrep SAST and pip-audit dependency scanning
- Dependabot for pip and GitHub Actions
- Interrogate docstring coverage check (50% minimum)
- CodeRabbit AI code review on pull requests
- `develop` branch for active development

### Fixed
- All install references updated to v0.3.0 (previously mixed v0.1.2/v0.2.0)
- PyPI-style install examples removed (GitHub-installable only)
- CLI error message for missing ChromaDB uses GitHub install form
- `gt project init` snippets in docs include required PROJECT_NAME argument
- TemplateResponse updated to keyword-arg API for Starlette 0.37+
- ruff format applied to all source files
- pip-audit `mkdir` for output directory in CI
- CI installs `[web]` extras for test imports

## [0.2.1] - 2026-04-12

### Fixed
- Text-match contract test monkeypatches `HAS_CHROMADB` for
  ChromaDB-enabled environments

_Note: Git tag v0.2.1 exists but `__version__` was not updated in this
release. The package reports 0.2.0 when installed from the v0.2.1 tag._

## [0.2.0] - 2026-04-07

### Added
- **Layer 2: Project Scaffold** — `gt project init` with three profiles:
  `local-only`, `dual-agent`, `dual-agent-webapp`
- **Layer 3: Workstation Doctor** — `gt project doctor` with auto-install
  and profile-aware readiness checking
- `gt project upgrade` for scaffold file maintenance (dry-run and apply)
- Bridge runtime extracted from production (6 modules: runtime, worker,
  poller, handshake, launcher, context)
- `gt bootstrap-desktop` for same-day prototype setup
- `gt export` and `gt import` for database portability
- Project manifest persistence in groundtruth.toml
- Template sets for hooks, rules, CI workflows, dual-agent, and webapp
- Copilot coding agent instructions (`.github/copilot-instructions.md`)
- Operational configuration capture (method guide 11)
- Desktop setup guide for client workstation bootstrap

### Changed
- Governance gates now support `gate_config` for per-gate configuration
- `GateRegistry.from_config()` accepts `include_builtins` parameter
- Assertion engine expanded with `count`, `json_path`, `all_of`, `any_of` types

## [0.1.2] - 2026-03-28

### Fixed
- Publish workflow targets GitHub Releases (not PyPI)
- Removed stale PyPI install references from documentation
- Version sourced from single location (`__init__.py`)

## [0.1.1] - 2026-03-27

### Fixed
- Publish workflow corrected for GitHub-only distribution

## [0.1.0] - 2026-03-26

### Added
- Core knowledge database with append-only versioning (SQLite)
- 9 artifact types: specifications, tests, work items, operational
  procedures, documents, environment config, testable elements,
  test coverage, backlog snapshots
- Assertion engine with `grep`, `glob`, `grep_absent`, `file_exists`
  types and path confinement
- Pluggable governance gates (ADR/DCL assertion gate, owner approval gate)
- CLI (`gt`): init, seed, assert, summary, history, config, serve
- Web UI (FastAPI + Jinja2) with branding and 11 read-only routes
- 10 method documentation guides
- Example project (task-tracker) with 14-step walkthrough
- CI/CD templates for test, build, and deploy workflows
- Process templates (CLAUDE.md, MEMORY.md, hooks, rules)
- AGPL-3.0-or-later license

[Unreleased]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Remaker-Digital/groundtruth-kb/releases/tag/v0.1.0
