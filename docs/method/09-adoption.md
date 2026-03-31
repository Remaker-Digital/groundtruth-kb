# 9. Adoption & Promotion

GroundTruth is designed as **upstream infrastructure** that downstream projects consume. This document defines the contract between GroundTruth (the method and toolkit) and the projects that adopt it.

## Upstream/downstream model

```
groundtruth-kb (upstream)
    │
    ├── Method documentation
    ├── KB engine + CLI + web UI
    ├── Governance gates (built-in + plugin)
    ├── Process templates
    └── CI/CD templates
         │
         ▼
   Your project (downstream)
    │
    ├── groundtruth.toml          ← project-specific config
    ├── groundtruth.db            ← project-specific data
    ├── CLAUDE.md                 ← project-specific rules (from template)
    ├── MEMORY.md                 ← project-specific state
    ├── hooks/                    ← mix of GT-managed + project-specific
    └── src/                      ← your application code
```

**GroundTruth** provides the method, the toolkit, and the templates. **Your project** provides the domain knowledge, specifications, tests, and implementation. The boundary between them is explicit and enforced.

## Managed vs project-owned files

Every file in a GroundTruth project falls into one of two categories:

### Managed files (GroundTruth controls)

These files originate from GroundTruth and are updated when you pull a new upstream release. You should not edit them — your changes will be overwritten on the next update.

| File/directory | Purpose |
|----------------|---------|
| `groundtruth_kb/` (installed package) | KB engine, CLI, web UI, gates |
| Template originals in upstream repo | CLAUDE.md template, hook templates |
| Built-in governance gates | ADRDCLAssertionGate, OwnerApprovalGate |

### Project-owned files (you control)

These files are generated from templates during `gt init` or created by you. GroundTruth never overwrites them after initial creation.

| File | Purpose |
|------|---------|
| `groundtruth.toml` | Project configuration (DB path, branding, gate plugins) |
| `groundtruth.db` | Your project's knowledge database |
| `CLAUDE.md` | Your project's rules and procedures |
| `MEMORY.md` | Your project's operational state |
| Project-specific hooks | Hooks you write for your workflow |
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
- Adds a process template that codifies a general engineering practice
- Fixes a CI/CD template that was broken or incomplete

**Keep project-local** when the change:

- Is specific to your domain (e.g., a gate that checks your particular spec IDs)
- Adds project-specific branding, configuration, or workflow customization
- Extends the KB schema for your project's needs (via migrations in your codebase)
- Implements business logic that only applies to your product

**Gray area — ask yourself:** "Would a stranger starting a new GroundTruth project benefit from this?" If yes, promote upstream. If only your team would use it, keep it local.

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
2. **Update the dependency.**
   ```bash
   pip install --upgrade groundtruth-kb
   ```
3. **Run assertions.** Verify that your existing specifications and assertions still pass with the new version.
   ```bash
   gt assert
   ```
4. **Check for new templates.** If the release includes updated process templates, compare them against your project-owned copies and merge relevant improvements manually.
5. **Test the web UI and CLI.** Verify that `gt serve` and `gt summary` still work with your database.
6. **Run your project's test suite.** Ensure no regressions in code that interacts with the KB.

### Breaking changes

GroundTruth follows semantic versioning:

- **Patch** (0.1.x): bug fixes, no behavioral changes
- **Minor** (0.x.0): new features, backward compatible
- **Major** (x.0.0): breaking changes to the API or database schema

Breaking changes always include a migration guide. Database schema changes are handled automatically by the KB engine's migration system — your existing `groundtruth.db` will be upgraded in place when you first open it with the new version.

## Version pinning

Pin your `groundtruth-kb` dependency to a minor version range:

```
# requirements.txt or pyproject.toml
groundtruth-kb>=0.1.0,<0.2.0
```

This accepts patch releases (bug fixes) automatically while requiring a conscious decision to adopt minor or major releases.

## Feedback loop

The upstream/downstream relationship is bidirectional:

```
GroundTruth ──publish──→ Downstream projects
     ↑                         │
     └──── feedback ←──────────┘
```

Downstream projects are the proving ground for the method. When you discover that a governance rule is too strict, a template is missing a step, or the CLI doesn't handle an edge case — that feedback improves GroundTruth for everyone.

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
