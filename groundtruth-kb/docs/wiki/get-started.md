# Get started

**Status:** Current orientation for an already installed host
**Reviewed:** 2026-09-26

This guide starts after [Verify installation](Verify-Installation) succeeds. It
does not provision a GTKB host.

## 1. Open GTKB Home

```powershell
gt --config E:\GTKB\groundtruth.toml home open
```

Review the services and status pages before beginning work.

## 2. Understand the separation

- The GTKB host supplies the canonical service, shared baseline, and operator
  facilities.
- Each application has its own registered root and Git repository.
- A work item belongs to one project.
- Project authorization controls whether new work may be dispatched.
- A dispatched agent claims the next bridge artifact, not durable ownership of
  the work item.
- Bridge messages coordinate work but are not durable authority.

Read [Core concepts](Core-Concepts) before administering projects or review
workflows.

## 3. Inspect current work

```powershell
gt --config E:\GTKB\groundtruth.toml projects list --json
gt --config E:\GTKB\groundtruth.toml backlog list --json
```

For an assigned work item, use the installed release's current context command
to read its project, formal requirements, linked tests, dependencies, and
coordination state. Do not select work from a cached report.

## 4. Add an application only through the supported route

Application registration and initialization require an owner-selected
application, project, repository boundary, and supported harness profile. Do not
invent an ad hoc project or manually edit generated harness projections.

The existing source-tree bootstrap guide contains detailed current CLI examples,
but the complete clean-customer tutorial still requires qualification against
the unified installer and current release. This Wiki will absorb that tutorial
as the workflow stabilizes.

## 5. Complete a representative workflow

Continue with [First governed change](First-Governed-Change). If any command or
required interface is absent from the installed release, stop and use
[Support](Support); do not create a competing state store or authority surface.
