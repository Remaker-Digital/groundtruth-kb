# Get started

Open GTKB Home, identify the intended workspace, and check the settings that
matter before a request. This guide is for an **already installed host**.

**Status:** Preview orientation, not a qualified end-to-end tutorial

**Reviewed:** 2026-09-28

## Before you start

- Complete [Verify installation](Verify-Installation). If you do not have a
  working host, start with [Install on Windows](Install-on-Windows).
- Know the full path of the working directory you intend to use. Use
  non-sensitive sample content when learning the interface.
- Have the selected release's supported model/provider setup and, for governed
  work, an explicitly assigned task. A workspace selection is not an assignment
  or project authorization.

The interface examples come from owner-supplied Preview screenshots received
2026-09-26. Their exact build is not shown. The review did not exercise the
controls or qualify provider setup, permission enforcement, or a complete first
request. The checkpoints below tell you what to inspect, not what has passed a
release test.

## 1. Open GTKB Home

Run this command with your installation's configuration path. `E:\GTKB` is an
example, not a directory to create or rename as part of this guide.

```powershell
gt --config E:\GTKB\groundtruth.toml home open
```

**Checkpoint:** Home opens for the intended installation. If it does not, use
[Home does not open](Troubleshooting#gtkb-home-does-not-open).

Open **Settings → GTKB** and read the reason beside each status result. A missing
session context is different from a service outage. The browser opening does
not prove that all required services are healthy. See [Status](Status) and
[Services](Services) for those checks.

## 2. Recognize the five controls

![Illustration of GTKB Home with numbered workspace, agent mode, permission, model, and Settings controls. The descriptions below explain what to check.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-orientation.svg)

*Illustration, not a screenshot or a proposed UI change. Labels are simplified;
the selected values are examples, not required defaults.*

| Control | Check before a request |
| --- | --- |
| **1. Workspace** | The working directory is the one you intend. A short name does not verify its full path. |
| **2. Agent mode** | The mode's tools and behavior suit the task. It is separate from the model and permissions. See [Agent presets](Agent-Presets). |
| **3. Permission** | The selected permission is appropriate for the intended operation. Do not switch to Full access to clear an unexplained refusal. See [Settings](Settings#session-permission-menu-on-home). |
| **4. Model** | The session uses the intended provider/model configuration. A preset label or green dot does not prove a request will succeed. See [Models](Models). |
| **5. Settings** | Use the GTKB and GTKB services tabs for status and component checks. Leave advanced [Controls](Controls) unchanged during orientation. |

## 3. Choose a workspace

When no workspace is selected, the composer says **Choose a workspace to start**.
Use **Choose workspace** above it.

### The Windows directory picker

1. In **Select Workspace Directory**, navigate to the intended existing working
   directory. Check the location breadcrumb and **Folder** field.
2. Use **Select Folder** to submit that directory, or **Cancel** if it is not the
   directory you intend.
3. Check the returned Home view before entering a prompt. A highlighted folder
   in the dialog is not evidence that Home accepted it.

Choose the directory for your work, not a drive root, backup, temporary folder,
or GTKB host directory simply because it appears in an example. For an already
registered application, check its intended registered root. Selecting or
creating a folder does not clone a repository, register an application, create
a governed project, or authorize work.

The [workspace picker reference](GTKB-Home) preserves the original screenshot
and its evidence limits. If selection fails, see
[workspace troubleshooting](Troubleshooting#a-folder-is-highlighted-but-home-still-needs-a-workspace).

### Home with a selected workspace

**Checkpoint:** The intended workspace name appears above the composer. The
captured example also shows it in the sidebar with **New Session** beneath it.
Verify the full working path through the supported interface before proceeding:
the displayed short name alone cannot distinguish similarly named checkouts.

<details>
<summary>See the captured selected-workspace example</summary>

![GTKB Home showing GT-KB as the workspace, New Session in the sidebar, and the mode menu open with Standard mode selected. No prompt or response is shown.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-session-modes.png)

Original screenshot, reproduced unchanged. `GT-KB` and the model preset are this
installation's examples, not required values. This is a captured state, not a
tested transition from the picker or proof of a successful request.

</details>

## 4. Check the session before sending

Check **workspace → agent mode → permission → model** using the table above.
The permission menu shows **Read Only**, **Workspace Write**, and **Full access**.
Their exact enforcement and the timing of changes need a release-specific
contract. A permission label is not a guarantee that every tool is sandboxed.

The General settings permission is a default for new sessions. Do not assume
that changing it changes an existing session. Likewise, **Standard mode** is an
agent preset, not a provider/model choice or a grant of project authorization.

If the provider/model has not been configured through the supported setup route,
stop here and use [Models](Models) or [Support](Support). Do not copy the
`@preset/...` reference from a screenshot as an API model identifier, paste a
key into chat, or guess which configuration file to edit.

## 5. Continue with an explicit task

For governed work, use the task and exact role/activity instructions supplied
by the owner or dispatcher. The `::init gtkb pb` text in the interface reference
belongs to one captured session. It is **not** a universal first prompt and
does not assign this reader a role.

For evaluation, ask the operator for the release's approved, non-sensitive
sample task and expected result. A reproducible first-session exercise is still
missing from this documentation set. Until it is qualified, this page is an
orientation path, not evidence that a new user can complete onboarding unaided.

### Recognize a rendered response

The captured [session reference](GTKB-Home) shows **Chat** and **Trajectory**
views, a rendered reply, and usage information. A reply proves neither that
governed work is assigned nor that a requested change was completed correctly.
Compare the result with the explicit task and its expected outcome.

If the agent reports that initialization succeeded but no work is assigned,
request an assignment. Do not manufacture work or treat initialization as a
completed project. If a request fails, collect the exact redacted error and use
[Troubleshooting](Troubleshooting). Avoid repeated retries that may incur cost.

## Where to go next

- [Core concepts](Core-Concepts): the operating model and its terms.
- [First governed change](First-Governed-Change): review and work boundaries.
- [GTKB Home](GTKB-Home): commands, sidebar organization, Chat, Trajectory,
  system-prompt display, and usage indicators.
- [Training](Training): available material and planned walkthroughs.

Application registration, provider setup, the first successful request, restart
recovery, and permission behavior still need version-pinned walkthroughs. These
are tracked as [known gaps](Known-Issues); interface illustrations and additional
page coverage do not close them.
