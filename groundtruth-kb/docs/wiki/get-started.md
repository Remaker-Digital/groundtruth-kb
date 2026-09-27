# Get started

**Status:** Current orientation for an already installed host

**Reviewed:** 2026-09-26

This guide starts after [Verify installation](Verify-Installation) succeeds. It
does not provision a GTKB host.

## 1. Open GTKB Home

```powershell
gt --config E:\GTKB\groundtruth.toml home open
```

Use [Verify installation](Verify-Installation) and [Services](Services) for the
host checks. Seeing the browser interface alone does not confirm that all
required services are healthy.

The **Settings → GTKB** tab contains the [status pane](Status). Read the reason
beside each result: an unknown session context and a dashboard that has not been
contacted need different follow-up from a service outage.

## 2. Choose a workspace

The Preview screen below is the starting point when no workspace has been
selected. Its prompt composer says **Choose a workspace to start**.

![GTKB Home Preview before workspace selection, showing Choose workspace above the unavailable prompt composer and No sessions yet in the sidebar.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-empty-state.png)

Owner-supplied screenshot received 2026-09-26; exact build/version not shown.
See [GTKB Home](GTKB-Home) for the visible-control guide.

1. Select **Choose workspace** above the composer.
2. Choose the intended existing workspace. If it is not available, use the
   supported application-registration route described below; do not create an
   unrelated project just to get past the empty screen.
3. Before entering a prompt, check that the intended workspace is selected. If
   the composer remains unavailable, use [Troubleshooting](Troubleshooting) and
   [Support](Support).

The image documents the empty state only. Workspace selection, any provider or
credential setup, and a successful first response still need a version-pinned
walkthrough. **Standard mode** is visible; the separate [Agent presets
guide](Agent-Presets) now shows a matching built-in preset marked **In use** and
describes the four visible built-in modes. Their selection behavior, effective
scope, and effects on active sessions still need testing. A preset does not
assign a governed role. **New Session** is a session entry point, not evidence
that a canonical project or work item has been created. Creating a custom preset
is not a documented first-session prerequisite.

The [Settings reference](Settings) shows the General pane, including the default
permission mode for new sessions and conversation preferences. Review that
distinction before treating any displayed permission value as a project
authorization or a recommendation to change it.

### Check the model/provider setup for your intended session

**Settings → Models** exposes the provider-management view illustrated in
[Models and providers](Models). The documented example lists **GTKB OpenRouter**
with a Custom badge and a green dot; it does not show a selected model or prove
that credentials and requests work. Do not copy that provider name as a required
configuration or assume that selecting a workspace also selects a working model.

Confirm the provider/model route required by your intended workflow using the
installed release's supported setup procedure. The exact Add/Edit dialogs,
model-selection location, and first-response sequence still need a verified
walkthrough. Keep credentials out of prompts and screenshots, confirm any usage
charges and data destination, and use non-sensitive sample content for the
first request. If a setup step is missing, use [Support](Support) rather than
guessing an endpoint or manually editing generated harness configuration.

## 3. Understand the separation

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

## 4. Inspect current work

```powershell
gt --config E:\GTKB\groundtruth.toml projects list --json
gt --config E:\GTKB\groundtruth.toml backlog list --json
```

For an assigned work item, use the installed release's current context command
to read its project, formal requirements, linked tests, dependencies, and
coordination state. Do not select work from a cached report.

## 5. Add an application only through the supported route

Application registration and initialization require an owner-selected
application, project, repository boundary, and supported harness profile. Do not
invent an ad hoc project or manually edit generated harness projections.

The existing source-tree bootstrap guide contains detailed current CLI examples,
but the complete clean-customer tutorial still requires qualification against
the unified installer and current release. This Wiki will absorb that tutorial
as the workflow stabilizes.

## 6. Complete a representative workflow

Continue with [First governed change](First-Governed-Change). If any command or
required interface is absent from the installed release, stop and use
[Support](Support); do not create a competing state store or authority surface.
