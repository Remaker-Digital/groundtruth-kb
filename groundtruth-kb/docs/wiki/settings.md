# Settings

**Status:** Illustrated General Settings and Home permission reference; interaction checks pending

**Reviewed:** 2026-09-26

Open **Settings** at the lower left of [GTKB Home](GTKB-Home), then select
**General**. This page describes the supplied General view and the separate
permission menu on Home. It records visible choices, not tested enforcement,
and does not change any settings.

For the **GTKB** tab, see the separate illustrated [GTKB status guide](Status).
For **GTKB services**, see the illustrated [service-management guide](Services).
For **GTKB controls**, see the illustrated [operational-controls reference](Controls).
For **Models**, see the illustrated [models and providers guide](Models).
For **Plugins**, see the illustrated [plugin configuration overview](Plugins).
For **Agent presets**, see the illustrated [built-in modes guide](Agent-Presets).

## General Settings

![GTKB Home Settings with General selected: Permission is Workspace Write, Language is English, Appearance is System, Font size is 14 px, Conversation display is Compact, and Enter behavior while busy is Queue.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-settings-general.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The exact
build/version is not visible. The values below are selected in this capture;
they are not established factory defaults or recommendations for every user.

| Setting | Value shown | Explanation supported by the visible UI |
| --- | --- | --- |
| **Permission** | **Workspace Write** | The helper text identifies this as the default permission mode for **new sessions**. This General dropdown is closed; the later Home capture below shows three composer-menu choices, not proof of identical options or synchronized state in both places. Precise allowed operations remain untested. |
| **Language** | **English** | English is selected. The list of supported languages is not expanded. |
| **Appearance** | **System** | System is highlighted; Light and Dark are also offered. Theme switching and system-theme tracking have not been tested in this review. |
| **Font size** | **14 px** | The helper text says this affects conversation content only. It does not promise to resize the complete interface. |
| **Conversation display** | **Compact** | The helper text says this controls process content in completed turns. The exact content collapsed or retained, and other display choices, are not shown. |
| **Enter behavior while busy** | **Queue** | The setting applies while busy. The helper text says Cmd/Ctrl+Enter uses the other behavior, but does not name that behavior in this view. |

## Session permission menu on Home

On the supplied Home screen, the **Workspace Write** control is at the lower
left of the composer, beside the plus-shaped control. Its open menu shows
**Read Only**, **Workspace Write**, and **Full access**. Workspace Write has a
checkmark and remains the label on the composer control.

![GTKB Home with the composer permission menu open, showing Read Only, Workspace Write with a checkmark, and Full access. The composer control also reads Workspace Write; the sidebar shows GT-KB and New Session, and the right-hand model-reference selector remains visible. No prompt or response is shown.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-permissions.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. This captures a selected permission label, not a
reviewer-executed permission change or enforcement test. The workspace name
and model-reference label are examples from this installation. The reviewer did
not change permissions or execute commands, access files, or send a model
request through GTKB.

| Visible choice | State in this capture | Boundary the documentation still needs to establish |
| --- | --- | --- |
| **Read Only** | Listed; no checkmark. | Which reads, tool calls, shell operations, network requests, and side effects are allowed or refused. The name alone is not proof that every tool is side-effect-free, that requests stay local, or that provider usage has no cost. |
| **Workspace Write** | Checked; also displayed on the composer control. | The exact workspace boundary, supported writes and other operations, access outside that boundary, and approval/refusal behavior. A short workspace name does not establish the resolved filesystem scope. |
| **Full access** | Listed; no checkmark. | Which restrictions change, what remains restricted, and any confirmation or approval behavior. The label does not establish unrestricted operating-system privileges or permission to perform every advertised action. |

The menu identifies these three choices in this captured build. It does not
demonstrate switching, dismissal without a change, saving, persistence, or
behavior during an active turn. It also does not show an escalation warning;
that does not prove no warning appears after selecting a broader option.

Before the first request, inspect the displayed permission and consult the
installed release's supported scope guidance. Do not choose **Full access**
simply to get past an unexplained refusal or setup problem. If the required
scope or effect of a change is unclear, use [Support](Support) rather than
testing broader access against production files. See the
[permission troubleshooting guidance](Troubleshooting#a-permission-label-does-not-explain-a-refusal).

## Session permissions and governed work

Session permissions and project authorization are separate concepts. Choosing a
harness permission mode is not authorization to implement a project and does
not replace the review requirements in [Core concepts](Core-Concepts).

Do not infer the precise file boundary, permitted operations, or approval-prompt
behavior from any permission name alone. Those details need a tested
permission-mode reference. The **Standard mode** selector on Home describes
the agent's tool/prompt/capability preset, not its permission level. The separate
right-hand `@preset/...` [composer reference](Models#read-the-home-composer-reference)
is another control; it does not establish permission scope either.

The General Permission helper explicitly refers to a default for new sessions.
The Home menu is presented in the composer. Both supplied captures display
Workspace Write, but matching labels do not establish inheritance, overrides,
synchronization, or persistence. Test changing the default separately from
changing the composer selection; document effects on pending, new, and already
running sessions, including a busy turn and later tool calls. Do not assume a
change retroactively alters a running operation or a prior permission grant.

## Other visible settings sections

The navigation also includes **GTKB**, **GTKB services**, **GTKB controls**,
**Models**, **Plugins**, and **Agent presets**. Their contents are not visible in
the General capture. Separate screenshots now document the **GTKB**
[status pane](Status), **GTKB services** [panel](Services), including its visible
Start/Stop controls, and **GTKB controls** [reference](Controls), including
numeric values, units, and ranges. The [Models guide](Models) now illustrates a
provider entry and the Edit/Add entry points. The [Plugins guide](Plugins)
illustrates four collapsed configuration sections and the separate Plugin list
tab. The [Agent presets guide](Agent-Presets) illustrates four built-in cards,
Standard mode marked In use, and a custom-authoring entry point. These images
now cover the landing views of all seven settings sections, not every control
or interaction. Provider setup, model selection, expanded plugin controls, the
plugin inventory, preset selection, and custom authoring still need walkthroughs.
The presence of a tab does not establish which providers, plugins, presets, or
controls are available or configured.

Use the checks in [Services](Services) and
[Verify installation](Verify-Installation) for the selected installation.

## Configuration-file access and saving

An **Open configuration file** button and an X-shaped close control are visible
at the top of the dialog. The screenshot does not identify the file opened, its
scope, or the application used to open it. Do not assume it is `groundtruth.toml`
or use it as a reason to edit generated harness configuration manually. This
page does not prescribe a manual configuration-file edit.

The separate [GTKB controls capture](Controls#configuration-path-and-value-source)
shows an operational-controls path in its subtitle. That does not establish the
target of this shared dialog-level button, or whether it changes between tabs.

No Save, Apply, or Reset control is visible in the supplied General pane. This
does not prove that changes are saved automatically or that recovery controls
are absent elsewhere. A tested procedure still needs to establish when each
change is applied, whether it survives reopening Home, whether a new session is
required, and how to restore the previous value.

For documentation and usability follow-up, see
[Known issues: Settings review](Known-Issues#settings-review). For a problem with
the installed product, use [Troubleshooting](Troubleshooting) and
[Support](Support). Do not post configuration files or credentials in a public
support request.
