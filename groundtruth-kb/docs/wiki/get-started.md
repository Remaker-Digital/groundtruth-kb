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

The following capture adds a selected-workspace view. Cancellation behavior,
resolved-path verification, persistence, provider or credential setup, and a
successful first response still need a version-pinned walkthrough. See the
[workspace picker review checklist](Known-Issues#workspace-picker-review).

### Home with a selected workspace

Home now displays **GT-KB** above the composer and as a workspace in the sidebar,
with **New Session** beneath it. The mode menu is open. The earlier **Choose a
workspace to start** message is no longer shown; a partially obscured prompt
placeholder appears instead.

![GTKB Home with GT-KB displayed above the composer and in the Workspaces sidebar, New Session beneath it, and the mode menu open with Standard mode checked above PTC, Minimal, and Creator. The right-hand composer selector displays @preset/gtkb-openrouter-deepseek-v4-flash; no prompt or response is shown.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-session-modes.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. The workspace name is this installation's example,
not a required directory name. Only its short name is visible here, not the
resolved path. This is a captured selected state, not a reviewer-executed test
of the transition from the picker. No workspace or preset was changed and no
request was sent for this review.

| Visible label | What to check before the first request |
| --- | --- |
| **GT-KB** beside the folder icon | This is the displayed workspace, not a model or project. Verify the intended full working path through the supported workspace interface; this short name alone cannot distinguish similarly named checkouts. |
| **Standard mode**, checked in the open menu | This is the agent-mode choice. The menu also shows PTC, Minimal, and Creator with descriptions; see [Agent presets](Agent-Presets#choose-a-mode-from-home). A selected label does not establish effective permissions or tested tools. |
| `@preset/gtkb-openrouter-deepseek-v4-flash` on the right | This separate composer control is explicitly labeled **Model** in a later [open-popover capture](Models#read-the-home-composer-reference). The Model row repeats the reference and has a right-facing chevron; its destination, alternatives, and resolved provider/model are not shown. Do not confuse it with the Standard agent-mode preset or copy it as a required API model identifier. |
| **New Session** in the sidebar | The captured view has a session entry under the workspace, but no submitted prompt or response. This does not establish a completed session, persisted history, application registration, or a canonical project/work item. |

The open mode menu obscures part of the composer, including its left-hand
controls. Do not infer the complete permission label or placeholder from that
covered text; the later [Home permission capture](Settings#session-permission-menu-on-home)
shows Workspace Write checked in a separate menu. The visible send arrow does
not prove that submission is enabled or that a provider request will succeed.
Check workspace, mode, permissions, and the
resolved model/provider separately before using non-sensitive sample content.

### Understand the session mode and permissions

The open **Standard mode** menu above shows four choices and a checkmark beside
Standard. The separate [Agent presets guide](Agent-Presets) also shows the
matching built-in card marked **In use**, compares the four descriptions, and
documents the Home selector. Switching behavior, effective scope, and effects
on active sessions still need testing. A preset does not assign a governed role.
**New Session** is a session entry point, not evidence
that a canonical project or work item has been created. Creating a custom preset
is not a documented first-session prerequisite.

The [Home permission menu](Settings#session-permission-menu-on-home) is a separate
control at the lower left of the composer. The supplied capture lists **Read
Only**, **Workspace Write** (checked), and **Full access**. These are permission
choices, not the Standard/PTC/Minimal/Creator agent modes or the model reference.

The [General Settings reference](Settings#general-settings) describes a default
permission mode for new sessions. Its relationship to the composer selection,
and each choice's exact permitted operations, still need testing. Inspect the
displayed permission before the first request; do not select Full access merely
to resolve an unexplained refusal. Neither a permission label nor a mode
selection authorizes project work.

### Check the model/provider setup for your intended session

**Settings → Models** exposes the provider-management view illustrated in
[Models and providers](Models). The documented example lists **GTKB OpenRouter**
with a Custom badge and a green dot; it does not show a selected model or prove
that credentials and requests work. Do not copy that provider name as a required
configuration or assume that selecting a workspace also selects a working model.

The later [Home Model popover](Models#read-the-home-composer-reference) identifies
the separate right-hand composer control: open the reference-labeled control
and locate **Model**. The capture shows that row and a right-facing chevron,
not its destination, alternative models, or resolved provider/model.
Confirm the provider/model route required by your intended workflow using the
installed release's supported setup procedure. The exact Add/Edit dialogs,
reference resolution and selection behavior, and first-response sequence still
need a verified walkthrough. Keep credentials out of prompts and screenshots,
confirm any usage charges and data destination, and use non-sensitive sample
content for the first request. If a setup step is missing, use [Support](Support) rather than
guessing an endpoint or manually editing generated harness configuration.

### Find conversation commands

The composer's plus-shaped control has a **Commands** tooltip in the
[illustrated Commands menu](GTKB-Home#commands-menu). It lists compact, export,
feedback, goal, permission, plan, and model with short explanations. The `model`
helper specifies **this conversation**; the `permission` helper describes a
preset combining sandbox mode and approval policy. Their effects remain
untested. The composer also advertises `/ commands, @ files or sessions`, not
a verified syntax reference. You do not need to compact history, export a log,
submit feedback, or set a goal just to begin a first-session walkthrough.

### Recognize the sidebar view options

The sliders-shaped control beside **Workspaces** exposes separate **Group by**
and **Order by** sections. The [sidebar reference](GTKB-Home#sidebar-grouping-and-ordering)
illustrates Workspace and Last updated checked, with In one list and Manual
also offered. These organize the navigation view; they are not the working
directory picker, agent mode, permission setting, or canonical work priority.
The actual switching, manual-ordering method, and persistence remain untested.
Leave view customization out of the first-session prerequisites.

A further [session-search capture](GTKB-Home#sidebar-session-search) shows an
empty **Search sessions...** field and an X-shaped control. It identifies the
feature but does not demonstrate a match, its search scope, or how to clear or
close it. The GT-KB/New Session row shown beneath the empty field is not a
verified search hit. Use the supported search procedure for the installed
release; do not assume a shortcut or enter private text to discover its scope.

### Recognize an in-progress session

The [in-progress session reference](GTKB-Home#read-an-in-progress-session) now
shows a submitted message, Chat selected beside Trajectory, context and tool
activity, **Deep diving...**, a square-marked control, **Session log**, and
cache/token figures. This closes the missing activity-view illustration gap.
A later [rendered response](#recognize-a-rendered-response) adds the next display
checkpoint, but neither capture qualifies the complete first-use sequence.
Activity rows and output-token counts do not by themselves establish successful
tool execution or a finished answer.

The captured `::init gtkb pb` message is historical example content, not a
generic first-use prompt to copy. Do not infer role initialization, authority,
or the next action from its title. Use the procedure and assignment appropriate
to the intended workflow. A qualified first-session example must still show
completion or failure, explain waiting and cancellation, and preserve the
distinction between UI activity and canonical results. Keep private prompt,
context, tool output, and unreviewed session logs out of public reports.

A later capture supplies a [Trajectory view reference](GTKB-Home#read-the-trajectory-view):
Duration/Turns/Calls controls, Input/Model/Tools lanes, labeled event rows, a
turn marker, and a separate Search field. It shows some tool-request details
and a clipped skill-response preview, not a completed first response or measured
performance. The raw image is withheld because it exposes instruction/tool
payload previews. Keep this an optional inspection step, not an onboarding
prerequisite; do not execute the displayed payloads or confuse Trajectory's
Search field with the sidebar's session search.

### Recognize a rendered response

The [response and turn-statistics reference](GTKB-Home#read-a-rendered-response-and-turn-statistics)
now describes a readable assistant answer, a **10 tool calls · 1 message**
summary, an upward-arrow composer control, and turn/step/timing/cache/token
figures. The response-display checkpoint is no longer missing. Read the answer,
then check the expected result through the appropriate supported procedure;
generated prose claiming initialization is not independent verification. A
lower-response capture now shows the **Conclusion** and the response action row,
including **Usage 128K tok**, **Ran for 1m 48s**, and a timestamp. These are
historical displayed values, not validated accounting or measured performance.

The Conclusion describes waiting for an assignment. A valid waiting response
need not be a failure: distinguish role binding, selecting an activity, and
receiving the specific work to perform. An activity marker alone does not
identify or dispatch a task. Follow the intended workflow rather than copying
the screenshot's next-step example or choosing work from its state summary.
The overlapping-sheets, thumbs-up/down, and branching-line icons still need
documented names and tested effects; do not assume the last icon shares or forks.

The raw capture is withheld because it contains session identifiers and bridge
details. Its reported queue is not an instruction to select work, and its role
marker is not a universal first prompt. A scrolled response and changed icon do
not prove every tool succeeded or that all work stopped. The footer's counters
measure different named quantities whose scope still needs documentation;
Output is truncated, and the displayed times must not be added into an assumed
elapsed duration. Leave advanced metric interpretation out of first-use setup.
A version-pinned, reproducible non-sensitive request with a verified outcome and
clear next step is still needed for the completed Get Started walkthrough.

The circular indicator immediately left of the composer arrow is now identified
by its [context-usage popover](GTKB-Home#read-the-context-usage-popover), not as an
activity indicator. The capture shows **7% of context used**, **~17.9K / 262K**,
and approximate System prompt, Tools, and Messages categories. This describes
context occupancy, not remaining account credit or the separate response-row
Usage count. The capacity, estimation method, category reconciliation, and
opening/dismissal behavior still need qualification; the shown values are not
universal defaults. Keep the meter optional in first-use guidance, and do not
invoke compaction or change models merely because it is visible.

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
