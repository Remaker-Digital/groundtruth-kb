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

### The Windows directory picker

The next supplied capture shows a Windows **Select Workspace Directory** dialog
over Home. It has a location breadcrumb, a directory list, a **Folder** field,
and **Select Folder** and **Cancel** buttons.

![Windows Select Workspace Directory dialog over GTKB Home, browsing the E drive with GT-KB highlighted and shown in the Folder field; Select Folder and Cancel are visible, while Home still says Choose a workspace to start.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-workspace-picker.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. Drive labels and folder names are machine-specific
examples. The highlighted `GT-KB` directory is the existing operator's example,
not a required directory name, fresh-install default, or instruction to rename
anything. The capture stops before confirmation: it does not show a selected
workspace in Home or a successful first session. No folder was opened, selected,
created, or registered by the documentation reviewer.

1. Select **Choose workspace** above the composer.
2. In **Select Workspace Directory**, navigate to the intended existing working
   directory. Check both the location breadcrumb and **Folder** field; a similar
   name on another drive or in another checkout may be a different workspace.
3. If the intended directory is shown, use **Select Folder** to submit it. Use
   **Cancel** to leave the picker without submitting a selection. Neither action
   was exercised in this review; their resulting state still needs testing.
4. After returning to Home, verify that the intended workspace is shown before
   entering a prompt. If it is not shown, the path is wrong, an error appears,
   or the composer remains unavailable, use
   [Troubleshooting](Troubleshooting#a-folder-is-highlighted-but-home-still-needs-a-workspace)
   and [Support](Support). Do not infer success from a highlighted folder alone.

Choose the directory for the work you actually intend to do. Do not select a
drive root, backup, temporary run folder, or the GTKB host directory merely
because it appears in this example. When working on an already registered
application, check that the intended directory matches its registered root.
The exact registration relationship and acceptance rules still need a tested
reference; the picker is not proof of Git-repository discovery or registration.

The dialog also exposes **New folder**, but creating a directory is not the
same as cloning a repository, registering an application, creating a governed
project, or authorizing work. If a directory cannot be found or accessed, first
check its location and the supported access route. Do not create an unrelated
folder/project or change permissions simply to get past the picker. Application
registration, when actually needed, is the separate procedure described below.

The confirmed workspace view, cancellation behavior, persistence, provider or
credential setup, and a successful first response still need a version-pinned
walkthrough. See the [workspace picker review checklist](Known-Issues#workspace-picker-review).

### Understand the session mode and permissions

**Standard mode** is visible; the separate [Agent presets
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
