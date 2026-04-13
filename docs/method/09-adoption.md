# 9. Adoption & Promotion

GroundTruth is designed as **upstream infrastructure** that downstream projects consume. This document defines the contract between **groundtruth-kb** (the core toolkit) and the projects that adopt it.

> **Note:** Project scaffolding (`gt project init`), bootstrap profiles,
> and environment doctor (`gt project doctor`) are included in the
> `groundtruth-kb` package.  See the
> [product architecture](../architecture/product-split.md) for the full
> architecture.  The contract below applies to groundtruth-kb.

## Upstream/downstream model

```
groundtruth-kb (upstream)
    │
    ├── Method documentation
    ├── KB engine + CLI + web UI
    ├── Governance gates (built-in + plugin)
    ├── Project scaffolding       ← gt project init (profiles, doctor, upgrade)
    └── Bridge runtime            ← groundtruth_kb.bridge module
         │
         ▼
   Your project (downstream)
    │
    ├── groundtruth.toml          ← project-specific config (created by gt init)
    ├── groundtruth.db            ← project-specific data (created by gt init)
    ├── Rules/state files         ← you create these per your workflow
    ├── Gate plugins              ← project-specific governance enforcement
    └── src/                      ← your application code
```

**GroundTruth** provides the method documentation, the knowledge database engine, the governance gate framework, and reference [process templates](https://github.com/Remaker-Digital/groundtruth-kb/tree/main/templates) for project setup, including templates for capturing bridge and automation configuration. **Your project** provides the domain knowledge, specifications, tests, implementation, and any project-specific automation. The boundary between them is explicit.

## Managed vs project-owned files

Every file in a GroundTruth project falls into one of two categories:

### Managed files (GroundTruth controls)

These files originate from GroundTruth and are updated when you pull a new upstream release. You should not edit them — your changes will be overwritten on the next update.

| File/directory | Purpose |
|----------------|---------|
| `groundtruth_kb/` (installed package) | KB engine, CLI, web UI, gates |
| Built-in governance gates | ADRDCLAssertionGate, OwnerApprovalGate |

### Project-owned files (you control)

These files are created by `gt init` or by you. GroundTruth never overwrites them after initial creation.

| File | Purpose |
|------|---------|
| `groundtruth.toml` | Project configuration (DB path, branding, gate plugins) — created by `gt init` |
| `groundtruth.db` | Your project's knowledge database — created by `gt init` |
| Rules and state files | Your project's rules file and operational state (you create these as needed for your workflow) |
| Gate plugins | Custom governance gates for your domain |
| `src/`, `tests/`, etc. | Your application code |

### The rule

If you need to change a managed file's behavior, the correct path is: file an issue upstream, contribute the change, and consume it through the next release. Do not fork or patch managed files locally — it creates drift that compounds over time.

## When to promote upstream vs keep project-local

Not every improvement discovered in a downstream project belongs upstream. Use this decision framework:

**Promote upstream** when the change:

- Fixes a bug in the KB engine, CLI, web UI, or built-in gates
- Adds a governance gate that would benefit any GroundTruth project (not just yours)
- Improves a method document with a correction or clarification
- Adds a reusable pattern (e.g., a governance gate, a seed data set) that would benefit any GroundTruth project
- Improves the generic capture contract or reference templates for bridges, automations, or control-surface configuration

**Keep project-local** when the change:

- Is specific to your domain (e.g., a gate that checks your particular spec IDs)
- Adds project-specific branding, configuration, or workflow customization
- Extends the KB schema for your project's needs (via migrations in your codebase)
- Implements business logic that only applies to your product

**Gray area — ask yourself:** "Would a stranger starting a new GroundTruth project benefit from this?" If yes, promote upstream to groundtruth-kb. If only your team would use it, keep it local.

## Promotion workflow

When you discover an improvement that belongs upstream:

1. **File an issue** on the GroundTruth repository. Tag it with `method-feedback` if it concerns the engineering method, or use the standard bug/feature templates for tooling changes.
2. **Describe the problem**, not just the solution. Upstream maintainers need to understand the context to evaluate whether the change is general enough.
3. **Submit a pull request** if you have a working implementation. Follow the contributing guidelines — tests required, ruff-clean, no project-specific references.
4. **Wait for review.** The upstream maintainers assess whether the change is general, safe, and compatible with the existing contract.
5. **Consume the release.** Once merged and released, update your project's `groundtruth-kb` dependency to the new version.

## Downstream update procedure

When a new GroundTruth release is available:

1. **Read the changelog.** Identify breaking changes, new features, and deprecations.
2. **Update the dependency** (update the tag in your requirements file):
   ```
   groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.3.0
   ```
   Then reinstall: `pip install -r requirements.txt`
3. **Run assertions.** Verify that your existing specifications and assertions still pass with the new version.
   ```bash
   gt assert
   ```
4. **Check for new features.** Review any new governance gates, seed data, or CLI commands. Evaluate whether they apply to your project.
5. **Test the web UI and CLI.** Verify that `gt serve` and `gt summary` still work with your database.
6. **Run your project's test suite.** Ensure no regressions in code that interacts with the KB.

### Breaking changes

GroundTruth follows semantic versioning:

- **Patch** (0.1.x): bug fixes, no behavioral changes
- **Minor** (0.x.0): new features, backward compatible
- **Major** (x.0.0): breaking changes to the API or database schema

Breaking changes always include a migration guide. Database schema changes are handled automatically by the KB engine's migration system — your existing `groundtruth.db` will be upgraded in place when you first open it with the new version.

## Version pinning

Pin your `groundtruth-kb` dependency to an exact Git tag:

```
# requirements.txt or pyproject.toml
groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.3.0
```

GroundTruth-KB is distributed via GitHub only (not PyPI). Pinning to an exact tag ensures reproducible installs. Update the tag when upgrading to a new release.

## Feedback loop

The upstream/downstream relationship is bidirectional:

```
GroundTruth ──publish──→ Downstream projects
     ↑                         │
     └──── feedback ←──────────┘
```

Downstream projects are the proving ground for the method. When you discover that a governance rule is too strict, the CLI doesn't handle an edge case, or a method document is unclear — that feedback improves GroundTruth for everyone.

The `method-feedback` label on the issue tracker is specifically for observations about the engineering method itself (not just tooling bugs). These are reviewed monthly and incorporated into method documentation updates.

## Multi-project isolation

A single `groundtruth-kb` installation supports multiple projects. Each project has its own:

- **Configuration file** (`groundtruth.toml`) — points to the project's database and defines branding
- **Database** (`groundtruth.db`) — completely isolated data
- **Assertions** — scoped to the project's codebase via `project_root`
- **Gate plugins** — loaded from the project's TOML config

Projects share the installed package but nothing else. There is no cross-project data access, no shared state, and no implicit coupling.

To work with multiple projects, use the `--config` flag:

```bash
gt --config /path/to/project-a/groundtruth.toml summary
gt --config /path/to/project-b/groundtruth.toml summary
```

Each command operates on the database and project root defined in that project's configuration file.
