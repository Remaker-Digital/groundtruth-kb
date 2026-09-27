# Agent presets

**Status:** Illustrated built-in preset overview; selection and custom authoring untested

**Reviewed:** 2026-09-26

In [GTKB Home](GTKB-Home), open **Settings → Agent presets**. The UI describes a
preset as the plugin composition used by one session's agent: its tools, prompt,
and capabilities. It offers built-in presets and an entry point for drafting a
custom preset with Creator mode.

Use this page to compare the descriptions visible in the supplied captures. A
preset is not a model/provider, a session permission level, or a governed role.

## Read the Agent presets pane

![Agent presets selected in GTKB Home Settings, showing built-in Standard mode marked In use, PTC mode, Minimal mode, and Creator mode, with a Custom section and Draft a custom preset with Creator mode button.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-agent-presets.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The exact
build/version is not visible. All four visible cards have a **Built-in** badge;
only **Standard mode** has an **In use** badge. The panel has a scrollbar, so
this capture is not proof of the complete preset inventory or the absence of
custom presets elsewhere. No preset was selected, duplicated, edited, or drafted
for this review, and no tool, workflow, goal, or subagent was launched through
GTKB to test a card's description.

| Visible preset and identifier | Capability description shown by the UI | What remains unverified |
| --- | --- | --- |
| **Standard mode** — `standard` | Described as a full coding agent with file editing, shell, file and web search, skills, planning, goals, subagents, and workflows. It is marked **In use**. | The actual tool availability and behavior, selected model, meaning/scope of In use, and whether this is a factory default are not established. |
| **PTC mode** — `ptc` | Described as a full coding agent without the workflow tool; other tools are exposed through the PTC mode SDK so the model can combine multi-step operations in one TypeScript program. The Settings card is clipped, but the later [Home menu](Get-Started#home-with-a-selected-workspace) shows that final sentence in full. | The acronym, SDK requirements, supported operations, practical tradeoffs, and runtime behavior still need a verified reference and tests. A complete UI description is not an executed capability test. |
| **Minimal mode** — `minimal` | Described as a two-tool coding agent with persistent bash and `str_replace_editor`. | Windows shell prerequisites, persistence lifetime, permitted effects, and practical limitations have not been tested. Minimal describes the advertised tool set, not a read-only or safer permission level. |
| **Creator mode** — `cordis` | Described as a custom-preset authoring mode with all Standard mode capabilities plus runtime inspection, plugin experiments, and preset-authoring guidance. | The authoring sequence, model/provider usage, resulting changes, review, save/apply behavior, and recovery are not shown. The relationship between the displayed Creator name and `cordis` identifier is not explained in the capture. |

These are displayed capability descriptions, not executed capability tests or
recommendations to enable every listed tool. In particular, persistent bash in
the Minimal description does not establish that it uses PowerShell or how bash
is provisioned on Windows.

Each card has two icon-only controls at its lower right. The page helper invites
users to duplicate an existing preset, but this image does not establish which
icon performs that action, what the other icon does, or whether either opens a
read-only view. Their labels/tooltips and behavior need inspection before a
step-by-step procedure can name them.

Under **Custom**, **Draft a custom preset with Creator mode** is visible. It is
an authoring entry point, not evidence that a preset has been created, saved,
selected, or tested. No custom editor or resulting artifact is shown.

## Standard mode on Home and In use here

The earlier [Home capture](GTKB-Home#recognize-the-first-screen) shows a
**Standard mode** selector. The Settings capture provides a matching built-in
preset name, its advertised capabilities, and the **In use** badge. A later
[selected-workspace capture](Get-Started#home-with-a-selected-workspace) shows
the Home menu open, with Standard checked. This establishes a visible selected
state in each view, not a tested switch or proof that their state remains in
sync across sessions.

The helper refers to one session's agent. The screenshot does not establish
whether **In use** identifies the current session, a pending new session, or a
broader default, nor whether a change affects an active conversation. The
walkthrough must explain and test those distinctions before recommending a
switch. Do not infer persistence from the badge or treat its selected value as a
universal default.

## Choose a mode from Home

On the illustrated Home screen, the mode selector is next to the workspace
name, above the composer. Opening it reveals **Standard mode**, **PTC mode**,
**Minimal mode**, and **Creator mode**, each with a capability description. A
checkmark identifies Standard in this capture. Use the comparison above to
understand these descriptions before changing a mode; custom authoring is not
a prerequisite for a first session.

This Home menu reveals the complete PTC description: tools other than the
workflow tool are exposed through the PTC mode SDK so the model can combine
multi-step operations in one TypeScript program. It does not expand the acronym
or demonstrate execution. Minimal still describes persistent bash and
`str_replace_editor`; Creator still describes custom-preset work plus Standard
capabilities.

The separate right-hand composer selector displays
`@preset/gtkb-openrouter-deepseek-v4-flash`. Despite the shared word *preset*,
that reference is not one of the four agent-mode names. Its underlying
model/provider mapping is not established by the text; see
[Models and providers](Models#read-the-home-composer-reference).

Before documenting a switching procedure, test selecting each supported mode,
closing without a change, keyboard operation, checkmark/label updates, and the
effect on pending versus active sessions. Inspect the resulting effective
configuration through the supported interface, and establish persistence and
recovery. No menu option was selected by the reviewer.

## Keep presets separate from permissions and authorization

[Models and providers](Models) concerns provider configuration and model-choice
guidance. [Plugins](Plugins) concerns plugin configuration and inventory.
[General Settings](Settings) shows a separately labeled session Permission
control. A preset describes a composition of tools, prompt, and capabilities;
none of its labels establishes the actual permission boundary by itself.

Selecting a preset does not assign Prime Builder or Loyal Opposition, authorize
a project, establish independent review, or grant durable ownership of a work
item. See [Core concepts](Core-Concepts). Likewise, listing goals, workflows, or
subagents in a capability description is not an instruction to execute them.

## Complete the preset walkthrough

The next release-specific walkthrough should demonstrate a bounded first session
with a documented built-in preset, using the illustrated Home selector. Show how
to verify the effective preset and model, and the effect of changes on new versus
existing sessions. Keep custom authoring out of the normal [Get started](Get-Started)
prerequisites.

A separate advanced walkthrough should cover the supported duplicate and Creator
routes: inspect the resulting prompt/tools/capabilities, name the preset,
validate it, save or cancel, apply it deliberately, and recover the prior setup.
These are evaluation requirements, not a claim that those exact buttons or
steps already exist. Confirm supported storage and editing routes; do not
manually edit generated harness configuration or infer the shared **Open
configuration file** button's target from this screen.

Use non-sensitive examples. Before any provider-backed authoring or tool test,
establish the intended provider/model, data destination, and usage limits. Keep
credentials and private prompt content out of screenshots, recordings, and
public support output. A drafted preset is not evidence that its capabilities
have been validated.

See the [Agent presets review checklist](Known-Issues#agent-presets-review),
[Training](Training), and [Support](Support) for the remaining coverage and
follow-up routes.
