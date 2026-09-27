# Plugins

**Status:** Illustrated configuration overview; expanded controls and inventory untested

**Reviewed:** 2026-09-26

In [GTKB Home](GTKB-Home), open **Settings → Plugins**. The captured view offers
two tabs: **Plugin configuration**, which is selected, and **Plugin list**, whose
contents are not shown. This guide explains the visible entry points; it is not
an installation, enablement, or plugin-testing procedure.

## Read the Plugins pane

![Plugins selected in GTKB Home Settings, with Plugin configuration selected beside Plugin list, and four collapsed sections: Shell, Agent loop, Subagent, and Web search.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-plugins.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The exact
build/version is not visible. All four sections are collapsed. No plugin
settings were changed, and no shell command, subagent, or web search was run
through GTKB for this review.

| Visible element | What the capture establishes | What remains unverified |
| --- | --- | --- |
| **Plugin configuration** | The selected tab contains four collapsed configuration sections. | The fields, current values, defaults, scope, and save behavior are not visible. Configuration sections are not proof that their tools are enabled or available in a session. |
| **Plugin list** | A separate tab is available. | Its contents have not been inspected. The capture does not establish a complete inventory, versions, loaded state, or installation/update/removal controls. |
| **Shell** | The helper says it limits every command the agent runs. | The actual limits, enforcement boundary, supported exceptions, and refusal/recovery behavior have not been tested. The helper text is a UI claim, not a demonstrated sandbox guarantee. |
| **Agent loop** | The helper describes how the agent dispatches tool calls. | Scheduling options, defaults, and effects on running or queued calls are not shown. This label does not establish GTKB project/work-item dispatch behavior. |
| **Subagent** | The helper describes controlling which models agents may choose for subagents. | The available model choices, selection rules, fallback behavior, and enforcement are not shown. A model-choice setting does not authorize delegation or establish an independent reviewer. |
| **Web search** | The helper names the DeepSeek search provider. | Configuration, authentication, availability, data destination, usage charges, and actual search results are not established. The label does not prove that this is the only supported search provider. |

Four visible configuration cards do not mean exactly four plugins are installed.
The page helper describes configuring and inspecting plugins in this deployment,
but only an inspected inventory and tested behavior can establish what is
actually loaded and usable.

## Configuration, permissions, and governed work

Plugin configuration, model/provider setup, session permissions, and project
authorization are separate concerns. Use [Models and providers](Models) for the
captured provider-management entry points and [Settings](Settings) for session
permission guidance.

In particular, **Agent loop** refers here to tool-call dispatch. Do not identify
it with **Dispatcher Next** or infer project authorization from it. Likewise,
**Subagent** model controls do not assign governed roles, grant ownership of a
work item, or satisfy independent-review requirements. See
[Core concepts](Core-Concepts) for the operating model. The presence of these
controls is not an instruction to launch agents or execute tools.

The shared **Open configuration file** button is visible, but its target is not
identified by this view. See
[Settings: configuration-file access and saving](Settings#configuration-file-access-and-saving).
Do not use an unverified file path or manually edit generated harness
configuration to work around missing plugin instructions.

## Complete the plugin walkthrough

The next release-specific procedure should establish the following in a
separate test installation:

1. Expand each configuration section and record its actual fields, meanings,
   defaults versus current values, valid choices or units, and scope.
2. Establish how a change is saved, cancelled, restored, and applied to new
   versus active sessions, including any restart requirement and clear failure
   feedback. Do not infer automatic saving from the collapsed overview.
3. Inspect **Plugin list** and document the inventory information it actually
   provides, required versus optional components, and supported lifecycle
   operations. Do not invent install, enable, update, or remove buttons.
4. Verify the intended tool boundaries with bounded, non-sensitive examples,
   including both allowed behavior and correctly refused behavior. A correct
   refusal under a documented limit is not a defect to bypass.
5. Before a provider-backed search or subagent test, establish the selected
   provider/model, data destination, credentials required, and any charges or
   limits. Keep real credentials and private prompts out of recordings and
   public diagnostics; a local browser address does not establish local-only
   processing.

These are coverage requirements, not claims that the corresponding controls or
behaviors already exist. Keep advanced plugin tuning out of first-session
prerequisites unless the tested setup actually requires it. A short capabilities
and limits tour can accompany [Get started](Get-Started); detailed configuration
belongs in the follow-up [training plan](Training).

See the [Plugins review checklist](Known-Issues#plugins-review) for ongoing
evaluation. If a tool is unavailable or refused, use
[Troubleshooting](Troubleshooting#a-plugin-section-is-visible-but-a-tool-is-unavailable-or-refused)
and [Support](Support) rather than relaxing limits or installing an unrelated
plugin to make the screen appear healthy.
