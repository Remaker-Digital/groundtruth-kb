# GTKB Home

**Status:** Current component overview

**Reviewed:** 2026-09-26

GTKB Home is GroundTruth KB's integrated harness GUI and primary interactive
interface. The current implementation is a pinned local web application bound to
`127.0.0.1:3080` and opened in the user's browser.

## Open Home

```powershell
gt --config E:\GTKB\groundtruth.toml home open
```

The command obtains the current launch URL and opens it in the default browser.
Do not store or publish the launch URL as a permanent shortcut; it contains
launch authentication material intended for the browser.

## Recognize the first screen

![GTKB Home Preview in a browser, with New Session and an empty Workspaces sidebar, Choose workspace and Standard mode selectors, and a composer saying Choose a workspace to start.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-empty-state.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The UI is
marked **Preview**; its exact build/version is not visible. This is an orientation
image, not an installation, service-health, or end-to-end workflow test.

| Visible control or message | How to read it |
| --- | --- |
| **Choose workspace** | Start here to choose the intended working directory. Follow-up captures illustrate the [Windows directory picker](Get-Started#the-windows-directory-picker) and [Home with a selected workspace](Get-Started#home-with-a-selected-workspace). The selected state is visible; the transition, full-path identity, cancellation, and persistence remain untested. |
| **Choose a workspace to start** | This is a prerequisite message in the prompt composer, not an instruction to type a workspace path into the prompt. |
| **Standard mode** | A mode selector is shown with this value. The [Agent presets guide](Agent-Presets#choose-a-mode-from-home) covers the later open Home menu with Standard checked and PTC, Minimal, and Creator also visible. Switching behavior and scope still need testing; a preset is not a governed role or project authorization. |
| **New Session** | The sidebar's session entry point. Later captures show a selected workspace, [in-progress activity](#read-an-in-progress-session), and a [rendered response with turn statistics](#read-a-rendered-response-and-turn-statistics). These checkpoints do not qualify the complete first-use sequence. |
| **Workspaces / No sessions yet** | The displayed navigation view has no sessions. That does not establish whether canonical projects or work items exist. |
| **Settings** | The settings entry point is at the lower left. See the illustrated [General Settings reference](Settings) for a separate capture of the open dialog. |

The capture also contains icon-only controls beside **Workspaces** and inside the
composer. A later capture identifies the composer's plus-shaped control with a
**Commands** tooltip and shows the [Commands menu](#commands-menu). A further
capture identifies the sliders-shaped control beside **Workspaces**
as the entry point for [grouping and ordering](#sidebar-grouping-and-ordering).
A separate [session-search capture](#sidebar-session-search) now shows the
expanded **Search sessions...** field. Its opening/closing interactions,
accessible names, and keyboard behavior remain unverified.
The separate directory-picker capture is documented through the
labeled **Choose workspace** route; it does not establish what the sidebar's
folder-shaped icon does. The [selected-workspace view](Get-Started#home-with-a-selected-workspace)
also exposes a separate right-hand composer control labeled with an
`@preset/...` reference. Its later [open popover](Models#read-the-home-composer-reference)
explicitly shows **Model** and a right-facing chevron, but not the next view or
alternative models. Keep the workspace, agent mode, model/provider
configuration, and session permissions distinct; a visible name or send arrow
is not a completed first-response test. A further [Home permission capture](Settings#session-permission-menu-on-home)
shows Read Only, Workspace Write (checked), and Full access at the lower left
of the composer. This documents the menu, not the enforcement boundary or an
instruction to broaden access.

Continue with [Get started](Get-Started) for the next steps. The remaining
first-run guidance and screenshot coverage are listed in
[Known issues](Known-Issues).

## Read an in-progress session

This capture moves beyond the empty composer: a user message is visible and the
session displays context, skill, and shell activity while **Deep diving...** is
shown. **Chat** is selected. No completed assistant response, tool result, exit
code, or confirmed governed initialization is visible.

![GTKB Home in-progress Chat view with a user message and session title showing ::init gtkb pb, Standard mode, Chat and Trajectory tabs, System prompt and Context injection entries, Think, Skill and Pwsh activity rows, and Deep diving... text. Session log is at the upper right. The composer shows Workspace Write, a model reference, a square-marked blue control, and historical cache and token figures beneath it.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-session-in-progress.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. The `::init gtkb pb` text is part of the captured
message and title, not an instruction to the documentation reader or reviewer,
and not a generic first-use prompt. It does not establish that a role binding,
activity, claim, project authorization, or canonical mutation succeeded. The
reviewer did not send this message or run the displayed skill or shell action.

| Visible element | How to read it | What remains unverified |
| --- | --- | --- |
| Session title, **GT-KB** group, **now**, and message time **18:19** | The message text also appears as the session title and sidebar label. The short workspace name is this installation's example. | Naming/renaming behavior, resolved workspace path, persistence, and the meaning/timezone of timestamps. A matching title is not a canonical session identifier, and 18:19 is not an elapsed duration. |
| **Standard mode**, selected **Chat**, and **Trajectory** tab | The agent mode and two view labels are visible; the displayed contents belong to Chat. A later capture supplies the [Trajectory reference](#read-the-trajectory-view). | Switching behavior, tab persistence, and the completeness of either view. The later event display does not establish replay, an authoritative audit record, or complete execution history. |
| **System prompt** and three **Context injection** rows | Labels identify AGENTS.md / CLAUDE.md, @deepseek-ai/dsh-system-prompt, and skill-catalog. They are not expanded in this activity capture; a later [System prompt view](#read-the-expanded-system-prompt) shows part of that panel's text. | Full content, source/version, precedence, truncation, and provider transmission. The later panel does not establish the contents of the separate Context injection rows or prove that displayed instructions were applied. |
| **Think**, **Skill · gtkb-bridge**, and **Pwsh** rows | Activity summaries are displayed; the shell row describes showing the working directory and DSH environment variables. The later [Trajectory view](#read-the-trajectory-view) exposes some arguments and a clipped skill-response preview. | Complete arguments/results, approval, execution state, exit status, and effects. Neither the Think preview nor a named skill proves correct reasoning, successful execution, or governing authority. Do not reproduce an environment dump to illustrate this row. |
| **Deep diving...**, circular composer indicator, and blue square-marked control | The text and square-marked control present an in-progress state. A later [context-usage popover](#read-the-context-usage-popover) identifies the circular indicator's context-related purpose, correcting the earlier activity-indicator description. | Progress versus waiting/stalling, elapsed time, accessible names, cancellation effects, and terminal state. The circular indicator alone is not evidence of activity; no stop action, cancellation, or rollback is demonstrated. |
| **Session log** with a download icon | A session-log entry point is present at the upper right. | Its output format, contents, redaction, destination, and equivalence to the Commands `export` route. See [Support](Support#feedback-and-session-log-export-in-home) before sharing logs. |
| **Workspace Write** and the model reference in the composer | The permission label and @preset/gtkb-openrouter-deepseek-v4-flash reference remain visible during activity. | Effective permissions, resolved provider/model, and change timing. Keep these separate from Standard mode and the message's role marker. See [Settings](Settings#session-permission-menu-on-home) and [Models](Models#read-the-home-composer-reference). |
| **Cache hit 0% · Input 12.4K tok · Output 564 tok** | These are the historical figures displayed beneath the composer. | Per-request/turn/session scope, rounding, update timing, inclusion of context/tool activity, cache definition, and reconciliation with provider usage. Output tokens are not a completed answer, and the figures do not establish a bill or savings. |

The activity display is a useful orientation checkpoint, not a completed
first-response test. A later capture now shows a [rendered response and turn
statistics](#read-a-rendered-response-and-turn-statistics). A qualified walkthrough
still needs a bounded, non-sensitive request with a verified successful or failed
outcome, relevant tool results, and the supported recovery route. It should also
distinguish sending or queueing another message from stopping active work;
the composer's presence does not establish busy-input behavior.

Treat prompt/context previews, tool details, conversation content, and logs as
potentially sensitive. Check what a supported view or export contains before
sharing it; do not assume automatic redaction, complete history, or local-only
processing. The [in-progress session checklist](Known-Issues#in-progress-session-review)
records the remaining checks, including stop behavior, accessibility, usage
definitions, and retention/recovery. No live session was opened, stopped, or
exported for this documentation pass.

## Read the expanded System prompt

In **Chat**, **System prompt** appears above the user message and grouped
tool-call summary. A further owner-supplied capture received 2026-09-26 shows
it expanded, with a downward chevron and a bounded monospaced text region.
This adds an expanded-panel example; the exact build/version and the action
that opened it are not shown. Only the upper portion of the text is visible.

Prompt inspection is an optional diagnostic view, not a first-session
prerequisite. The raw capture is not published because it exposes prompt text,
a machine-specific path, and session identifiers in the surrounding answer.
No prompt payload or identifiers are transcribed here, and the reviewer did
not open a live prompt, edit configuration, or execute the displayed text.

| Visible element | How to read it | What still needs definition or testing |
| --- | --- | --- |
| **System prompt**, downward chevron, and open text region | The panel is visibly expanded. No editing or save control is demonstrated. | Opening/collapse behavior, accessible name and expanded state, keyboard activation, focus return, persistence across reload/session changes, and draft preservation. Do not describe this as a prompt editor or assume collapse changes the agent's input. |
| Monospaced text with an inner vertical scrollbar near the top | A portion of the prompt is readable within a separately bounded region; the bottom is clipped. | Whether this is an initial snapshot, current assembled prompt, or another representation; source/version, refresh timing, completeness, and relationship to Context injection, tools, messages, provider requests, and the context meter. Test with known synthetic content. Visible text alone does not prove what was transmitted, applied, or counted. |
| Main conversation scrollbar and a separate circular down-chevron control above the composer | The capture exposes both an inner prompt scroll region and conversation navigation affordances. The down-chevron is separate from the composer's upward arrow. | Exact accessible name, destination, availability, keyboard behavior, nested-scroll handling, focus/scroll restoration, and behavior as new messages arrive. Do not label it Jump to latest or assume it resumes generation, follows new output, or sends a message until tested. |

The visible wording refers to the underlying harness and a local checkout.
Explain how those terms relate to GroundTruth KB without treating the shown
path as a required installation location or the selected workspace. Neither
the displayed instruction text nor a role marker elsewhere in the capture
changes the reader's task or grants permission to execute it.

For support, report the version, view state, and a synthetic reproduction rather
than copying the full prompt. Collapsing a panel is not demonstrated redaction;
clipped text may still be present in a copy or export. See the [session-view
evaluation checklist](Known-Issues#in-progress-session-review) and
[safe-sharing guidance](Support#feedback-and-session-log-export-in-home).

## Read a rendered response and turn statistics

A further owner-supplied capture received 2026-09-26 returns to **Chat** and
shows a readable assistant response with headings and bullet points. A grouped
activity summary appears above it, the composer has an upward-arrow control,
and additional turn/timing figures appear below. This supplies the previously
missing response-display checkpoint; it is not an independently tested
initialization, installation, or completed governed workflow.

A subsequent capture, also received 2026-09-26, shows the lower portion of the
response: a **Conclusion** heading and an action/usage row beneath the answer.
The conclusion describes waiting for an assignment, not a completed product
change. This extends the same reference; it does not establish that the answer's
state report is accurate or current.

The raw images are not reproduced because the response includes native/session
identifiers and bridge details. Those values and details are intentionally not
transcribed here. Use synthetic content or supported concealment for a public
illustration. Exact build/version is not visible, and both captures are scrolled;
they do not show the complete conversation or all underlying tool results.

| Visible element | How to read it | What remains unverified |
| --- | --- | --- |
| Selected **Chat**, a rendered response, and **Session bound** / **Bridge state** headings | Home displays the assistant's account of initialization and state, including a claimed readback. This is more than the earlier activity-only view. | Accuracy and freshness of those claims, the underlying results, and the final lifecycle state. Narrative assertions, identifiers, and headings are not independent verification, current canonical state, or instructions for this reviewer to initialize or take work. |
| **10 tool calls · 1 message** with a right-facing chevron | A grouped activity summary and an apparent disclosure control are visible above the response. | Expansion/collapse behavior, scope of the counts, which message is counted, tool outcomes, ordering, retries, and missing/duplicate results. A count of calls is not a count of successful calls. |
| **Conclusion** and text about waiting for an assignment | The lower capture shows an explicit narrative ending and a stated reason for not proceeding. It adds a next-step explanation, not proof of a completed work item or a verified empty queue. | The next-step wording needs to distinguish role binding, activity selection, and a specific work assignment. An activity marker selects an activity; it does not by itself identify or dispatch work. Do not copy the captured instruction example as a generic onboarding command or select a target from the reported state. |
| Overlapping-sheets, thumbs-up, thumbs-down, and branching-line icons beneath the answer | Four icon-only controls are visible in the response action row. Their appearance suggests possible purposes, but no tooltip or accessible name is shown. | Exact names and effects, disabled/selected states, keyboard operation, copy scope, feedback destination and consent, and any sharing or branching behavior. Do not label the branching-line icon as Share or Fork, equate these controls with the Commands menu, or assume these actions keep all data local until qualified. |
| **Usage 128K tok** beside a cylinder-shaped icon | A response-level usage label appears separately from the footer's Input/Output/cache figures and the later [context-usage popover](#read-the-context-usage-popover). These are distinct labeled displays, not interchangeable measurements. | Whether Usage is per-message, per-turn, or per-session; which tokens it includes; rounding; click/hover behavior; and reconciliation with the footer and provider reporting. The context popover is beside the composer, not proof of this Usage label's interaction. Do not reconstruct the clipped Output value by subtraction or treat either display as a price or bill. |
| Clock icon, **Ran for 1m 48s**, and **18:21** beneath the answer | A duration is now explicitly displayed in the response row, together with a clock-style timestamp. These are historical UI values, not an independently timed run. | What starts/stops the duration, inclusion of waits and tool/model overlap, timestamp event/timezone, accessible details, and relation to LLM/tool times or sidebar age. A numerically plausible sum does not establish metric semantics, and the row does not prove successful execution or a latency guarantee. |
| Composer upward arrow, permission/model labels, and **Session log** | The upward arrow differs from the earlier square-marked control; the session composer and log entry point remain available on screen. | Whether the turn is terminal, input is enabled or queued, work remains active, and what follow-up or export does. Do not infer successful completion, cancellation, or stopped background work from an icon change alone. |
| **1 turns · 8 steps** in the footer | The footer exposes turn and step counters alongside the separate ten-call summary. | Definitions, aggregation scope, update timing, and mapping between turns, steps, messages, and tool calls. The differing counts are a documentation question, not proof of a counting defect; one step need not equal one call. |
| **LLM 37.4s · Tool call 1m11s · TTFT avg 3.1s · 193 tok/s** | These are the displayed historical timing/rate figures. TTFT commonly means time to first token; the release's actual measurement and averaging rules still need documentation. | Start/end boundaries, wall-clock versus accumulated time, overlap, waits/retries, averaging population, and the rate's token/time denominator. Do not sum LLM and tool time into an elapsed duration, infer concurrency, or use one capture as a performance benchmark. |
| **Cache hit 86% · Input 125K tok · Output 2...** | The footer shows cache/input figures and a visibly truncated Output field. | Cache numerator/denominator, token scope, rounding, provider reconciliation, full Output value, and access to untruncated details. Do not reconstruct the missing digits, subtract figures from earlier captures as a per-request measurement, or infer price, savings, billing, or local-only processing. |
| Sidebar time shows **1min**, **2min**, then **47min** across the response/context-popover captures | Relative-looking labels appear beside the selected session title, while the displayed response duration remains 1m 48s in the later views. | Which event age measures, refresh/rounding rules, and its relation to the response timestamp/duration and footer. A larger age is not evidence that a request ran that long, stayed active, or that its state report remains current. |

For ordinary use, read the response and distinguish its proposed next action
from a verified result before acting. For diagnostics, identify the installed
version and the exact metric/control being reported; use the [response and
statistics checklist](Known-Issues#response-and-turn-statistics-review) rather
than treating the footer as a performance or cost report. A qualified first-use
walkthrough must still show a reproducible non-sensitive request, its expected
outcome, and a useful next step. An answer that appropriately waits for an
assignment should say what input is missing; waiting is not by itself an error
or evidence that the platform contains no work. Keep role, activity, assignment,
and completed result distinct. Keep detailed diagnostics optional in that tour.
See [Support](Support#feedback-and-session-log-export-in-home) before sharing
response text, screenshots, or session logs.

### Read the context-usage popover

A further owner-supplied capture received 2026-09-26 shows a popover above the
circular indicator immediately left of the composer's upward arrow. The
explicit **of context used** label establishes a context-usage purpose; the
earlier description of that circle as an activity indicator is superseded.
The capture does not demonstrate whether hover, click, or keyboard focus opens
it, or how it is dismissed. It is separate from **Usage 128K tok** beneath the
response and the Input/Output/cache figures in the bottom footer.

The raw image is withheld because the surrounding answer contains session
identifiers and bridge details. Only the visible popover labels and historical
estimates are described here. No live context was inspected or changed, and
no prompt content, tool definitions, or messages were opened for this review.

| Visible element | How to read it | What still needs definition or testing |
| --- | --- | --- |
| Circular indicator beside the composer arrow, with a popover above it | The popover gives the indicator an explicit context-related purpose. | Actual opening/dismissal controls, accessible name, keyboard/touch support, focus behavior, and preservation of draft text. Do not describe the ring as a progress spinner or assume that opening it sends a request. |
| **7% of context used · ~17.9K / 262K** | The UI advertises an approximate used amount against a displayed context capacity, plus a percentage. | Units, tokenizer/estimator, numerator/denominator source, rounding, update timing, input/output reservation, and whether 262K follows the selected model or configuration. This is not a verified model limit, provider quota, billing allowance, persistent-memory size, or guarantee that any prompt under the displayed capacity will succeed. |
| **System prompt ~1.8K · Tools ~6.9K · Messages ~9.5K** | Three labeled categories with approximate values are shown. Their displayed values sum to about 18.2K, while the headline is about 17.9K. | Category membership, inclusion of tool definitions versus results and hidden/injected content, overlap, estimator rules, and synchronized snapshots. The difference needs explanation; the capture does not establish its cause or justify declaring a token-counting defect. Do not assume the estimates form an exact additive partition. |
| Gray, purple, and blue legend markers and segments in a horizontal bar | The bar supplies a visual counterpart to the three named categories. | Scale and segment mapping, readable values at zoom, non-color alternatives, threshold/warning behavior, and near-capacity recovery. No warning, automatic compaction, context expansion, or recovery action is demonstrated in this low-usage capture. |

Read this as a context-occupancy display, not a substitute for token-usage or
cost accounting. The substantially different response-row Usage value is not
by itself contradictory: the named measurements may have different scope and
must be defined before comparison. The screenshot does not establish that
either figure is current, exact, or provider-reconciled.

For a first-session tour, identify the meter and leave detailed interpretation
optional. Before recommending any capacity-management action, qualify the
selected release's warnings and recovery behavior, including data effects.
The [compact command](#commands-menu) is a separately advertised conversation
action; this popover does not prove that it runs automatically or preserves
all detail. Never treat low context usage as permission to broaden a task or
as a measure of remaining account credit. The existing [response and statistics
checklist](Known-Issues#response-and-turn-statistics-review) includes the pending
context-specific checks.

## Read the Trajectory view

A later owner-supplied capture received 2026-09-26 shows **Trajectory** selected
beside **Chat**. It exposes a lane display, a toolbar, and labeled event rows.
This closes the missing view-description gap; the reviewer did not switch tabs,
search events, open payloads, or run any displayed instruction or tool call.
The exact build/version is not visible, and the captures do not establish that
the two views are synchronized or contain a complete session history.

The source image is not reproduced here because it exposes instruction and
tool-payload previews. This reference describes the interface without copying
those payloads. A publication-safe illustration using synthetic content or
concealed previews remains needed; do not publish temporary operating guidance,
private prompts or paths, or environment values merely to document the UI.

| Visible element | What the capture establishes | What remains unverified |
| --- | --- | --- |
| Selected **Trajectory** tab beside **Chat** | A second session view is open under the same displayed title and Standard mode label. | Switching behavior, retained selection/scroll/draft state, live updates, and correspondence with Chat. A matching title is not a durable session or work-item identity. |
| **Duration**, **Turns**, and **Calls** toolbar labels | Three labeled controls appear above the lanes. | Their interaction, selected state, units, grouping/scaling rules, and whether they change the lane display, event list, or both. Do not infer toggle behavior or a default mode from appearance alone. |
| **Input**, **Model**, and **Tools** lanes with colored segments | The view separates three named lanes and displays colored spans. | Color meanings, segment identity, time origin/scale, duration values, overlap/concurrency, and links to rows. No numeric timing scale is visible; bar widths alone do not establish elapsed time, latency, cost, or a performance problem. |
| Empty **Search** field at the upper right | A search entry point is present within Trajectory, distinct from the sidebar's [Search sessions field](#sidebar-session-search). | Searchable fields, current-turn/session scope, hidden or clipped content, matching/filtering versus navigation behavior, and query processing/retention. No query or result is demonstrated. |
| **SYSTEM**, **USER**, **CONTEXT**, **ASSISTANT**, and **TOOL** row labels; **Turn 1** | The view distinguishes event categories, labels an initial system-prompt row, and shows a turn marker. Some previews are clipped. | Row ordering, turn boundaries, completeness, expansion/copy behavior, timestamps, and error/cancellation markers. These are displayed event categories, not new instructions to the reader, canonical authority, or proof that an assistant message is a final answer. |
| Tool rows for **skill** and **pwsh** | Request details are visible. The skill row also has an arrow followed by a clipped response preview; the shell row shows arguments without a visible result or exit status. | Full request/response pairing, status, timing, approval, side effects, and success/failure. A response fragment is more evidence than a tool name alone, but not a complete successful result or proof that the shell command finished. Do not copy or execute displayed payloads to inspect this view. |
| **Session log**, composer, permission/model labels, square-marked control, and usage figures | These remain visible alongside Trajectory. | Whether log contents match this view, busy-input and stop effects, and usage definitions. The [in-progress session reference](#read-an-in-progress-session) covers those shared controls; the new view does not qualify them. |

Use Trajectory as an observed session-inspection interface, not a demonstrated
replay mechanism, permanent audit archive, platform backup, or substitute for
canonical results. Before relying on it to diagnose a run, qualify event
ordering, tool request/response association, missing or truncated content,
search scope, timing definitions, and the distinction between active and
terminal states. See the [Trajectory review checklist](Known-Issues#trajectory-review).

Keep context and tool previews private unless they have been reviewed for the
intended audience. Labels such as SYSTEM or CONTEXT do not authorize the reader
to follow their contents, and the role marker in the captured session does not
change the documentation reviewer's role. For safe reporting, use [Support](Support#feedback-and-session-log-export-in-home).

## Sidebar session search

The sidebar now shows an empty **Search sessions...** field beneath **New
Session**, with a magnifying-glass icon on the left and an X-shaped control on
the right. **GT-KB** and its **New Session** entry remain visible below it. No
query text, matching result, result count, or no-results message is shown.

![GTKB Home with an empty Search sessions... field in the sidebar below New Session, a magnifying-glass icon at the field's left, and an X-shaped control at its right. GT-KB and a New Session row remain below. The main composer shows GT-KB, Standard mode, Workspace Write, and the model reference; no search query, prompt, or response is present.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-session-search.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. The field's placeholder identifies the intended search
subject as sessions. No query was entered, result opened, field cleared, or
search dismissed for this documentation pass.

| Visible element | What the capture establishes | What remains unverified |
| --- | --- | --- |
| **Search sessions...** field and magnifying-glass icon | A session-search interface is open with no entered query. | How it is opened, whether matching uses titles or conversation content, current-workspace versus wider scope, search timing, and query processing/storage. |
| X-shaped control | An icon is present at the right of the empty field. | Its label and whether it clears text, closes search, or behaves differently when a query is present. Do not teach it as a delete action or assume Escape has the same effect. |
| **GT-KB / New Session** below the field | A workspace group and session row are visible while the query is empty. | These are not demonstrated matches, a complete inventory, or evidence that results include every workspace or retained session. |

This is session navigation, not a demonstrated search of canonical work items,
projects, source files, or the knowledge base. The capture also does not
establish that searches run locally or that queries are never logged or sent
elsewhere. Use non-sensitive sample text when qualifying the search flow.

A complete walkthrough needs an entered query, a known match, a no-match case,
and the supported way to clear or dismiss search and return to the previous
view. Verify the intended session and workspace before resuming work; similar
names are not sufficient identity. Test the interaction with [grouping and
ordering](#sidebar-grouping-and-ordering), preservation of unsent input, and
query persistence separately. See the [session-search checklist](Known-Issues#sidebar-session-search-review).

## Sidebar grouping and ordering

The sliders-shaped control beside **Workspaces**, between the magnifying-glass
and folder-shaped icons, has a menu open in this capture. It separates **Group
by** from **Order by**, with a checkmark in each section. Its partly obscured
tooltip is not used here to invent a complete button label.

![GTKB Home with the sidebar grouping and ordering menu open beneath the sliders-shaped control beside Workspaces. Group by offers Workspace with a checkmark and In one list; Order by offers Manual and Last updated with a checkmark. The menu covers part of the session list; GT-KB, Standard mode, Workspace Write, and the model reference remain visible in the main view.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-sidebar-options.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. These are the selections visible in this installation,
not established factory defaults. No sidebar option was changed, session
reordered, or workspace switched for this documentation pass.

| Section | Visible option | State in the capture | Meaning and remaining questions |
| --- | --- | --- | --- |
| **Group by** | **Workspace** | Checked. | Advertises workspace grouping. The image does not demonstrate switching groups, full-path identification, or handling similarly named workspaces. |
| **Group by** | **In one list** | Not checked. | Advertises an ungrouped list. The resulting view, workspace labels retained there, and return to grouped view are not shown. |
| **Order by** | **Manual** | Not checked. | Offers manual ordering. The actual method, items affected, keyboard alternative, and saved-order behavior are not shown; do not assume drag-and-drop. |
| **Order by** | **Last updated** | Checked. | Names an update-based order. Which updates count, sort direction, tie handling, and behavior during active work remain unverified. |

Grouping and ordering are separate navigation choices. **Workspace** here is a
grouping criterion, not a replacement for the **Choose workspace** control that
selects the working directory. Do not use sidebar order as evidence of canonical
work priority, dispatch order, project membership, or an agent's ownership of
work. See [Core concepts](Core-Concepts) for those distinctions.

The open menu obscures part of the list, so this image does not demonstrate the
resulting order or a complete session inventory. A tested walkthrough still
needs to show switching and dismissal, preference scope and persistence,
retention of the selected session and unsent input, and restoration of a prior
view. Changing this view is not a first-session prerequisite. Use the
[sidebar review checklist](Known-Issues#sidebar-grouping-and-ordering-review)
to qualify these behaviors with non-sensitive sample sessions.

## Commands menu

The plus-shaped control at the lower left of the composer is labeled
**Commands** in this capture. Its open panel lists seven conversation commands
and their helper text. The composer also advertises **/ commands, @ files or
sessions**; exact typed syntax, arguments, and keyboard behavior have not been
tested. These are Home conversation controls, not terminal CLI commands.

![GTKB Home with the Commands panel open above the composer, listing compact, export, feedback, goal, permission, plan, and model with helper text. The plus-shaped control has a Commands tooltip; compact is highlighted, Workspace Write and the model reference remain visible, and no command result is shown.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-commands.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. The highlighted compact row is not proof that it ran.
No command was invoked, history compacted, export downloaded, feedback sent,
goal set, plan mode entered, permission changed, or model selected for this
documentation pass.

| Command | Purpose stated by the visible helper | Before relying on it |
| --- | --- | --- |
| `compact` | Compact older conversation history. | Establish what is summarized or removed, what remains available, persistence, and recovery. This is not the **Conversation display → Compact** presentation setting. |
| `export` | Download this Session log as a ZIP archive. | Inspect contents and handling using non-sensitive test data. Redaction, destination, and import/recovery are unverified. A session-log ZIP is not a [platform backup](Backup-And-Restore#session-export-is-not-a-platform-backup). |
| `feedback` | Record feedback about this session. | Establish destination, included data, confirmation/consent, and failure handling. Do not assume this creates a GitHub issue or canonical defect record; see [Support](Support#feedback-and-session-log-export-in-home). |
| `goal` | Set or view the goal for a long-running task. | Document the actual set/view flow, scope, progress, cancellation, persistence, and any provider usage. The menu does not demonstrate unattended execution or a startup service. |
| `permission` | Switch the permission preset (sandbox mode + approval policy). | The helper names the advertised combination, not tested enforcement. Compare the actual command flow with the [Home permission menu](Settings#session-permission-menu-on-home) before recommending a change. |
| `plan` | Enter or leave plan mode. | Qualify both transitions and their effect on tool execution. Harness plan mode is not a GTKB governed activity or project authorization, nor proof that all actions are read-only. |
| `model` | Select the model for this conversation. | This states the intended conversation scope. Available choices, reference resolution, change timing, and persistence still require testing; see [Models](Models#read-the-home-composer-reference). |

These are the rows visible in this build, not a complete command inventory for
every release or preset. The screenshot does not show command arguments,
confirmations, results, or failure states. No conversation command is established
as a first-session prerequisite. Follow the [Commands review checklist](Known-Issues#commands-review)
when qualifying behavior in a separate test installation, and keep private
conversation content and credentials out of public exports and recordings.

## Startup behavior

The production design registers `GTKB-Home` as a logon task. It starts Home at
owner logon and can restart an unexpected stop. Supported service controls pause
the task before an intentional stop so that the stop remains effective.

```powershell
gt --config E:\GTKB\groundtruth.toml home status
gt --config E:\GTKB\groundtruth.toml services status --json
```

## Windows launch affordances

A standard Start-menu entry and optional desktop shortcut are desired product
improvements, but they are not yet documented as part of a unified installer.
Any future shortcut should invoke the supported Home opener rather than embed a
fixed URL or secret.

GTKB does not currently require a taskbar icon. A system-tray controller should
be added only if measured user needs justify persistent health visibility or
frequent service controls. **Settings → GTKB services** already exposes a
[service-management panel](Services); do not assume that these controls need
to be built from scratch. Its presence does not replace a convenient launch
entry or prove startup and recovery qualification.

## Privacy and network boundary

Home is intended to remain on loopback. Telemetry and credential behavior must
be verified against the selected release. Do not expose Home to another network
or assume that browser reachability establishes host qualification.
