# Known issues and documentation gaps

**Status:** Current first-pass customer-facing list

**Reviewed:** 2026-09-26

This page records material adoption gaps, not every internal development item.

## Installation and lifecycle

- GTKB does not yet provide one unified customer-grade Windows installer.
- Package installation alone does not provision a complete host.
- Whole-product repair and uninstall are not yet unified.
- Minimum and recommended hardware sizing has not completed customer-facing
  qualification.
- Start-menu and optional desktop launch entries are not yet part of a unified
  installer.

## Learning and support

- The clean-machine, command-by-command first governed change tutorial is not yet
  independently qualified.
- The Home empty state is illustrated in [GTKB Home](GTKB-Home) and
  [Get started](Get-Started); the [General Settings reference](Settings) now
  illustrates the selected values and visible settings sections. The
  [GTKB status guide](Status) covers **Settings → GTKB**, and the [Services
  guide](Services) illustrates **Settings → GTKB services** and its visible
  controls. The [GTKB controls reference](Controls) illustrates the operational
  tuning fields and their displayed ranges. The [Models guide](Models) now shows
  the provider list and Add/Edit entry points. The [Plugins guide](Plugins)
  illustrates the collapsed configuration sections and Plugin list tab. The
  [Agent presets guide](Agent-Presets) now covers the four visible built-in
  modes and custom-authoring entry point. Get Started illustrates both the
  [Windows directory picker](Get-Started#the-windows-directory-picker) and
  [Home with a selected workspace](Get-Started#home-with-a-selected-workspace),
  including the open mode menu and separate composer reference. The latter
  capture reveals PTC's complete description. The [Home permission menu](Settings#session-permission-menu-on-home)
  now illustrates Read Only, Workspace Write (checked), and Full access.
  The [Home Model popover](Models#read-the-home-composer-reference) now confirms
  the right-hand control's purpose and shows its Model row and chevron, not the
  next view or alternative models.
  The [Commands menu](GTKB-Home#commands-menu) identifies the plus-shaped entry
  point and seven commands with helper text; their execution and results remain
  untested.
  The [sidebar grouping and ordering menu](GTKB-Home#sidebar-grouping-and-ordering)
  now identifies the sliders-shaped control and shows Workspace and Last updated
  checked, with In one list and Manual also visible. Switching, actual ordering,
  and preference persistence remain untested.
  The [session-search view](GTKB-Home#sidebar-session-search) now illustrates an
  empty Search sessions field and its X-shaped control. Search scope, matching,
  result states, and clear/dismiss behavior remain untested.
  The [in-progress session view](GTKB-Home#read-an-in-progress-session) adds a
  submitted message, Chat/Trajectory labels, context and tool activity, busy
  indicators, a square-marked control, Session log, and cache/token figures.
  It does not show a completed response, tool result, or confirmed role binding;
  view interactions, cancellation, logging, and usage definitions remain open.
  Resolved workspace path, selection/cancellation and persistence behavior,
  mode-switching and permission
  behavior, provider Add/Edit dialogs, model-reference resolution and selection,
  expanded plugin controls, plugin inventory, custom authoring, and a successful
  first session still need version-pinned coverage and interaction checks.
- Training videos and transcripts are not yet published.
- A redacted automated support bundle is not yet documented as available. The
  visible `export` command advertises a session-log ZIP, not verified redaction
  or platform recovery; the in-session Session log control supplies another
  visible entry point without demonstrated contents or equivalence to export.
  `feedback` has no demonstrated destination or result.
- Cross-platform host installation is not currently established.

## Home first-run review

These findings use the owner-supplied Preview screenshot received 2026-09-26.
They apply to that visible empty state, not to every product screen. No
interaction, keyboard, screen-reader, or service-health test was performed from
the image. The improvements below are recommendations, not shipped features.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Workspace selection is required, but no first-run guide or documentation link is visible. | Provide a short in-context path to Get Started. A first-time evaluator should identify the next action and select the intended workspace without source-code inspection or operator coaching. Record time and assistance needed. |
| **Must** | **Standard mode** has no explanation while closed; later Settings and [open Home menu captures](Agent-Presets#choose-a-mode-from-home) supply descriptions for four modes and a visible Standard selection. | Make that help discoverable and link to a clear comparison. Explain how mode choice takes effect, verify advertised capabilities and effects on new versus active sessions, and distinguish it from the separate composer reference. Do not treat the label as a governed role or project authorization. |
| **Must** | Later captures identify the plus-shaped Commands control, the sidebar's sliders-shaped grouping/ordering control, and an expanded Search sessions field with an X-shaped control. | Keep their purposes discoverable and test accessible names, keyboard focus/activation, and labels for remaining icons. Commands has a visible tooltip; the sidebar tooltip is partly obscured. The search field's purpose is explicit, but its opening route and X action remain untested. None of these images proves keyboard or screen-reader support. |
| **Should** | No readiness indicator or help/recovery link is visible on the empty Home view. A subsequent capture establishes a status pane under **Settings → GTKB**. | Make the existing status and troubleshooting route easy to find from Home. Test it both on a healthy host and when a required component is unavailable; do not assume a status view must be built from scratch. |
| **Should** | Later captures show a selected workspace/mode menu and an in-progress session with a message and activity, but no completed response. | Continue from those illustrated checkpoints to a short, captioned first-session demonstration linked to the written procedure. Show a bounded request reaching an explicit outcome, not just a busy indicator or token count. Check that a new user can reproduce it and record where assistance was needed. |
| **Don't** | The browser displays Home, a **Preview** label, and an empty session list. | Do not treat this as proof of installation completeness, service readiness, missing canonical work, or a successful governed workflow. Check those outcomes separately. |

## In-progress session review

The owner-supplied screenshot received 2026-09-26 shows a message and activity
in the selected **Chat** view, with **Deep diving...** displayed. It establishes
an in-progress presentation, not a completed response, successful shell action,
or confirmed initialization. See the [session-view reference](GTKB-Home#read-an-in-progress-session).
These are pending documentation and validation checks, not confirmed runtime
defects. Use disposable, non-sensitive test sessions to qualify interactions.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Chat is selected; Trajectory and System prompt are visible but their alternate/expanded contents are not shown. | Explain each supported view and control, then test switching, expansion/dismissal, keyboard focus, accessible labels, and readable layout at zoom. Preserve session selection, scroll position where intended, and unsent input; do not invent replay or audit guarantees for Trajectory. |
| **Must** | Context injection labels, a clipped Think preview, a Skill row, and a Pwsh summary appear without tool results. | Distinguish context sources and versions, activity summaries, requested/running/completed/failed tool states, approvals, outputs, and exit status. Test useful error/refusal feedback and safe display/redaction with synthetic content. Explain source precedence and truncation without treating labels as proof of compliance or reprinting private prompts/environment values. |
| **Must** | Deep diving..., an activity indicator, and a square-marked blue control appear, but no final response or elapsed duration does. | Provide understandable running, waiting, stalled/error, completed, and cancelled states with next actions. Verify the actual stop label and effect on model generation, running tools/child processes, queued input, and partial changes; show when cancellation is confirmed and how to recover. Do not promise rollback, process termination, or stopped billing from the icon alone. |
| **Must** | A composer, permission/model labels, a session title matching the submitted marker, and time labels remain visible during activity. | Test busy-message queue/steer behavior and its General setting, supported permission/model changes, title/path/session identity, reload/reconnect and history retention, and preservation of drafts. Explain timestamps rather than reading them as duration. Ensure titles and activity rows are not presented as canonical role, authorization, claim, or durable work-item ownership evidence. |
| **Must** | Session log has a download icon; the separate Commands menu advertises a ZIP export. | Verify both routes' format, scope, included prompts/context/tool data, destination, sensitive-data handling, retention, and failure/retry behavior. Establish whether they are equivalent using non-secret test data. Keep logs distinct from platform backup and authoritative state; do not upload an unreviewed archive or expose environment values. |
| **Must** | Cache hit 0%, Input 12.4K tok, and Output 564 tok are visible. | Define units, scope, rounding, update timing, cache numerator/denominator, and context/tool/retry inclusion. Reconcile against the supported provider's usage reporting and disclose gaps before publishing costs or savings; a local UI and an output count do not establish local-only processing or a completed answer. |
| **Should** | There is now a real activity-view illustration, but no explicit terminal outcome or recovery example. | Extend the short first-session tour through a bounded successful response, a useful failure/refusal, and a controlled cancellation after those paths are qualified. Explain the activity labels in plain language, link to written recovery guidance, and measure whether a novice understands when to wait, intervene, or seek help. |
| **Don't** | The role marker is captured message/title content; the screenshot stops during activity. | Do not treat the screenshot as an instruction to initialize the reviewer, a copy-and-run onboarding prompt, successful canonical initialization, proof of tool execution, completion, a full audit trail, measured cost, or permission to inspect live private context. Do not launch, stop, or export an active session merely to document this view. |

## Sidebar session search review

The owner-supplied screenshot received 2026-09-26 shows an empty **Search
sessions...** field, a magnifying-glass icon, and an X-shaped control. A workspace
and New Session row remain visible. This establishes the interface, not a query
or its results. See the [session-search reference](GTKB-Home#sidebar-session-search).

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | The placeholder says Search sessions, without a scope description or entered query. | Document supported search fields and scope: titles and/or conversation content, current versus other workspaces, and which retained sessions are included. Verify those boundaries with synthetic sessions and state query processing/logging behavior before using sensitive text. Do not assume full-text, knowledge-base, or canonical work-item search. |
| **Must** | No matching result, count, loading state, or no-results message is shown. | Test known matches and non-matches, case/substring behavior, spaces, non-ASCII text, duplicate names, and renamed or newly updated sessions. Explain when matching runs and distinguish no results from loading or failure with useful recovery. Measure response time at a representative session count; do not publish an unmeasured speed claim. |
| **Must** | An X-shaped control appears even with an empty field; no opening, clearing, dismissal, or keyboard action is demonstrated. | Establish the actual opening route, X behavior for empty/nonempty queries, clear/dismiss actions, and any supported shortcuts. Test keyboard focus, accessible labels, announced results, selection, and focus return. Verify whether the query persists after navigating or reopening Home, without losing the current session or unsent input. |
| **Must** | GT-KB and New Session remain visible with an empty query; separate captures expose grouping and ordering options. | Verify result identity and workspace context, including similarly named sessions across workspaces. Test search with both grouping modes and ordering choices, opening the intended result, clearing search, and returning to the previous view. Avoid stale results or list movement directing an action to a different session. |
| **Should** | The search field provides a readable purpose, but no successful example is illustrated. | Add a short find-and-return example to the navigation tour using non-sensitive sample sessions, including a no-match case. Check that a novice can locate the intended session and recover the unfiltered view without coaching; keep search optional for the first response. |
| **Don't** | The field is empty and the visible rows have no demonstrated relation to a query. | Do not call these rows search hits, assert a complete inventory, infer full-text or local-only processing, invent shortcuts or X behavior, treat an empty result as data loss, or enter private queries merely to document this capture. Session navigation does not establish work ownership, authorization, or canonical search results. |

## Sidebar grouping and ordering review

The owner-supplied screenshot received 2026-09-26 shows **Group by** with
Workspace checked and In one list available, and **Order by** with Last updated
checked and Manual available. It establishes the menu and selected labels,
not a tested sort or preference change. See the [sidebar reference](GTKB-Home#sidebar-grouping-and-ordering).

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Group by and Order by are separate sections, each with one checked choice. | Document the scope of both preferences and test every combination using multiple workspaces and sessions. Verify selection markers, dismissal without change, persistence across reload/reopen, and preservation of the active session, working directory, and unsent input. Keep grouping distinct from choosing a workspace or changing project membership. |
| **Must** | Manual is offered, but no reordering action is shown. | Document and test the actual supported method, which items can be reordered, within-group versus cross-group effects, a keyboard-accessible route, and whether the manual order survives switching away and back. Do not invent drag-and-drop or imply that moving a row transfers a session or work item to another workspace/project. |
| **Must** | Last updated is checked, but the menu obscures the list and no timestamps or sort direction are shown. | Define the timestamp/event used, direction, tie behavior, and when the display reorders. Test new sessions, messages, ongoing activity, and equal timestamps with a stable, understandable result. Verify that a refresh or reorder does not make a user act on a different session accidentally; sidebar order must not be taught as canonical dispatch priority. |
| **Must** | The menu is reached through a sliders-shaped icon; its tooltip is partly obscured and checkmarks are visible. | Provide a discoverable accessible label and test keyboard opening, navigation, selection, dismissal, focus return, and announced group/selected state. Check readable labels and menu placement at supported zoom/viewport sizes; a screenshot does not establish keyboard or screen-reader behavior. |
| **Should** | Workspace grouping and a one-list alternative are available. | Add a short navigation segment using distinct sample workspaces and multiple sessions after the behavior is tested. Check whether a novice can find and return to the intended session, distinguish similarly named workspaces, and restore a preferred view without coaching. Keep this optional for first use. |
| **Don't** | One historical pair of selections is visible; the list is partly covered. | Do not infer factory defaults, a complete session inventory, actual sort results, persistence, a reordering gesture, file movement, project membership, durable work ownership, or authorization from this view. Do not change live preferences or reorder active sessions merely to document the capture. |

## Commands review

The owner-supplied screenshot received 2026-09-26 identifies the plus-shaped
**Commands** control and shows seven rows with helper text. See the illustrated
[command reference](GTKB-Home#commands-menu). It documents advertised purposes,
not command execution. These checks remain open; qualify them in a separate
test installation with non-sensitive, disposable session content.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Commands has a tooltip, seven named rows, and a highlighted compact row; the composer advertises / commands and @ files or sessions. | Document actual menu/typed invocation, required arguments, context-dependent availability, result/error feedback, and cancellation. Test keyboard navigation, accessible labels, selected/highlighted state, dismissal, and focus return. Keep conversation commands separate from terminal CLI syntax; a highlight is not execution. |
| **Must** | compact advertises compaction of older conversation history; General separately offers Conversation display → Compact. | Explain the different purposes. Test what is summarized, removed, retained, or still retrievable; state persistence, recovery, and any provider usage. Do not claim lossless compaction, a reversible display-only action, or a backup substitute from the label. |
| **Must** | export advertises a session-log ZIP download. | Document archive contents, scope, destination, sensitive-data handling/redaction, failures, and any supported import. Test with non-secret canary values and synthetic content before sharing a real archive. Separate session export from a redacted support bundle and independently qualified platform/database recovery. |
| **Must** | feedback says it records feedback about the session, without showing a destination or submission result. | Show the actual destination, included content/metadata, consent/confirmation, and success/failure/retry behavior. Verify privacy and retention guidance; do not claim GitHub issue creation, canonical defect intake, or automatic redaction without evidence. |
| **Must** | goal offers set/view for a long-running task; plan offers entering/leaving plan mode. | Test actual inputs, state visibility, both plan transitions, tool effects, goal progress/cancellation and lifetime across reopen/restart, and any provider charges. Distinguish these harness controls from governed activities and project authorization; do not infer unattended/background execution, persistence, or universally read-only behavior. |
| **Must** | permission names sandbox mode + approval policy; model specifies this conversation. | Use the helper text to explain intended purpose and scope, then test consistency with the composer controls and General default. Document actual choices, effective state, cancellation, persistence, busy-turn change timing, and useful refusals. Reuse the [Settings checks](#settings-review) and [Models checks](#models-review); labels alone do not verify enforcement or a resolved model. |
| **Should** | Short helper text explains seven otherwise terse command names. | Keep this help discoverable and add a concise, captioned command walkthrough after behavior is qualified. Keep advanced history/goal operations out of first-use prerequisites; measure whether novices can find the right control without guessing command syntax or broadening permissions. |
| **Don't** | A single menu is shown, with no command arguments, confirmation, output, export, or response. | Do not claim a complete cross-release command inventory or tested behavior, upload an unreviewed log, create a goal/feedback submission, compact active history, or change model/permissions merely to document the screenshot. |

## Workspace picker review

The owner-supplied screenshot received 2026-09-26 shows a Windows **Select
Workspace Directory** dialog over Home, with a highlighted directory and
**Select Folder** and **Cancel** buttons. A later capture shows Home with the
short workspace name and a New Session entry. These close the picker-image and
selected-state-image gaps, not interaction qualification or the first-response
gap. No folder-selection interaction or application-registration operation was
performed for this review. See [Get started](Get-Started#the-windows-directory-picker).

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | The picker breadcrumb is on the E drive and Folder contains GT-KB; later Home shows only the short GT-KB name. | Explain how to choose the intended working directory and display/verify its resolved path after confirmation. The matching short name alone does not prove path identity. Test nested paths, similar names on different drives/checkouts, and names with spaces or non-ASCII characters. Do not imply that the example host root is every user's application workspace. |
| **Must** | The dialog selects a directory and also exposes New folder. | Document the actual relationship between directory selection, workspace state, registered application roots, and Git repositories. Establish what exists or changes at each step; creating or selecting a folder does not by itself prove application registration, project creation, or project authorization. |
| **Must** | Select Folder and Cancel are visible; a later Home image adds a selected state, not a recorded interaction or Cancel result. | Reproduce confirmation and cancellation in a separate test workspace, including the resulting Home state and restoration of focus. Test missing/inaccessible paths and rejected selections with a useful error, no silent fallback to another root, and no unintended partial setup. |
| **Must** | Later Home displays GT-KB, New Session, a changed composer placeholder, a checked Standard mode, and a separate reference selector. | Use the selected-state image as a checkpoint, then qualify when input/submission becomes ready. Document persistence after reopening Home and the effect on new versus active sessions; keep workspace, agent mode, model/provider reference, and permissions distinct. A send arrow is not proof of successful submission. |
| **Should** | The picker is a native Windows dialog, while the initiating interface is in a browser. | Make this transition clear in Get Started and a short first-session video. Use a non-sensitive example directory, demonstrate the confirmation checkpoint, and measure whether a new user can complete it without operator coaching. |
| **Should** | The dialog contains keyboard navigation controls, a path field, and drive/network entries. | Verify accessible names, keyboard navigation, cancellation, and return of focus to Home. State the qualified platform and storage support; native dialog entries alone do not establish support for every browser, cloud drive, removable drive, or network location. |
| **Don't** | A machine-specific directory is highlighted, and a later Home capture shows a matching short name but no prompt or response. | Do not treat these as a successful session, proof of full-path identity, a required installation path, a cloned or registered repository, a healthy host, or permission to expose all files. Do not publish private directory content or credential-bearing paths in follow-up captures. |

## Settings review

These additional findings use the owner-supplied General Settings and Home
permission-menu screenshots received 2026-09-26. The [Settings reference](Settings)
records visible values and the three composer-menu choices without treating
them as shipped defaults or tested behavior. Separate captures
now illustrate **GTKB** in the [status guide](Status) and **GTKB services** in the
[Services guide](Services), with **GTKB controls** in its own [reference](Controls).
These observations do not change what was visible on the earlier Home empty
state, and service actions and configuration edits remain untested.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | General labels Permission as a default for new sessions; the Home menu shows Read Only, Workspace Write (checked), and Full access; the later permission command helper describes sandbox mode + approval policy. | Document the scope and relationship of these routes: inheritance/overrides, actual General and command choices, changes to pending/new/active sessions, and persistence. Matching labels do not prove synchronization or enforcement. Distinguish permission from agent mode, model reference, and project authorization. |
| **Must** | Permission names and a checkmark are visible, but no allowed/refused operation is shown. | Define and test each mode's actual filesystem boundary, tool/shell/network effects, approval behavior, and correct refusals in a separate test workspace with disposable files. Verify outside-workspace handling, useful diagnostics, no unintended partial mutation on refusal, and the effect of changes during a busy turn. Do not claim a tested sandbox or unrestricted OS privileges from labels alone. |
| **Must** | No Save, Apply, or Reset control is visible in the General pane. | Make save/apply timing and recovery clear. Test persistence after closing/reopening settings and restarting Home, and state which changes require a new session. Do not assume automatic saving from the absence of a button. |
| **Must** | **Enter behavior while busy** is **Queue**; the helper calls Cmd/Ctrl+Enter's action only the other behavior. | Name both actions and explain what happens to the active turn and subsequent input. Verify Enter and Ctrl+Enter on Windows in a safe test session. Do not invent the alternate action's name. |
| **Should** | **Compact** controls process content, but its exact visible effect is not illustrated; a separate compact command advertises history compaction. | Provide a before/after display example using non-sensitive sample content. Explain what becomes hidden and whether it can be revealed again; distinguish presentation from history compaction, whose data effects need the separate Commands checks. |
| **Should** | **Open configuration file** does not name its target in the visible label. | Identify the target and settings scope, supported editing route, and recovery instructions before asking customers to use it. Do not direct manual edits to generated harness configuration. |
| **Should** | The Home permission menu offers three short names without explaining their precise effects in the captured view. | Provide concise, accessible scope guidance and clearly explain broader access before it takes effect. Verify keyboard selection/dismissal, focus, announced selected state, and any confirmation/recovery flow. The screenshot does not prove a later escalation warning is present or absent. |
| **Don't** | Selected values, permission choices, and other settings-section labels are visible. | Do not present these values as factory defaults, a permission label as proven enforcement, or a settings tab as service health. Do not equate Minimal with Read Only, treat Read Only as offline or free of provider charges, or teach Full access as a prerequisite or generic workaround for a refusal. |

## Status pane review

The owner-supplied **Settings → GTKB** screenshot received 2026-09-26 confirms an
existing status view, a Refresh button, and dashboard navigation. The findings
below concern interpretation, discoverability, and untested behavior; they do
not establish a live outage or authorize a product change.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | The dashboard row is green **PASS** while its explanation says **not contacted**. | Distinguish configured/available links from successfully contacted, healthy endpoints. Document the actual check behind each label; test with the dashboard reachable and unreachable so an uncontacted target cannot be mistaken for measured health. |
| **Must** | Overall is **UNKNOWN**; the session row explains that no native context id was supplied. | Explain aggregation and the next action for unknown results. Test host-only inspection separately from session-bound inspection. Do not infer identities or change a legitimate unknown to PASS merely to make the overview green. |
| **Must** | The status header shows 6:09:13 PM while the dashboard card says Last refreshed 1:44:39 PM on the same date. | Define each timestamp, timezone, data source, acceptable age, and Refresh behavior. Test which results and timestamps change. The image alone does not establish a stale-data failure threshold. |
| **Should** | The bridge summary exposes identifiers such as `active_status_mix` without the underlying status names. | Provide plain-language labels, metric definitions, and a supported detail view. Verify that users can distinguish applications, projects, declarations, attempts, and claims without interpreting raw field names. |
| **Should** | **Open dashboard** and **Overview page** are both visible. | Explain their different destinations and failure/recovery paths, and check both links against the selected installation. Include a route to the status view in Get Started and operator training. |
| **Don't** | PASS results, an UNKNOWN session, historical counts, and an explicitly uncontacted dashboard appear together. | Do not turn this screenshot into a current health report, a release qualification, evidence of authorized work, or a reason to restart services automatically. |

## Service controls review

The owner-supplied **Settings → GTKB services** screenshot received 2026-09-26
establishes an existing service-management panel, not just a navigation label.
It shows task/service integration and Start/Stop controls for some components.
The following checks are still open; no service was started, stopped, or
reconfigured for this review. See the illustrated [Services guide](Services).

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Authority and PostgreSQL show **Stop**; Dashboard shows **Start**. | Document action scope, dependency effects, active-work interruption, confirmation, progress, failure, and the supported recovery route. Test intentional stop and restart in an isolated qualification installation, not by interrupting the owner's active work. |
| **Must** | Services shows Dashboard **stopped** at port 8766; the separate status capture shows dashboard **PASS**, **not contacted**, at port 3000. | Map each label to the actual component, endpoint, probe, and time. Test both views against controlled reachable/unreachable states. Do not call the separate captures a demonstrated contradiction or treat an uncontacted link as a health pass. |
| **Must** | Home shows **running** with **task Ready**, while Authority shows **task Running**. | Explain application readiness versus scheduler state and test their combinations. Identify the source of each field; do not equate task registration or scheduler state with a healthy application. |
| **Must** | Ollama shows **stopped**, **task missing**, and no action button. | Distinguish required components from optional provider integrations. Provide a supported setup/recovery route when needed and an understandable not-required state when not selected. Test missing registration separately from an installed but unreachable service. |
| **Must** | Home displays **this page** rather than a Start/Stop control. | Document and test recovery when Home itself is unavailable, using a supported route outside this panel. Verify fresh-install registration, boot/logon startup, unexpected-stop recovery, and intentional-stop behavior separately. The screenshot does not prove those outcomes. |
| **Should** | **Refresh** is visible but no last-checked time or probe definition is shown. | Display or make discoverable result age and what was actually checked. Test refresh, pending/error states, keyboard operation, accessible names, and non-color status cues. |
| **Should** | Existing service controls are inside Settings; no launch shortcut is shown in this capture. | Prioritize a discoverable, supported launch entry and a short operator walkthrough. Evaluate a tray icon only for a demonstrated unmet need, not to duplicate controls already present. The capture cannot establish whether a shortcut exists elsewhere. |
| **Don't** | Historical green/red states and local addresses appear in a settings screen. | Do not treat this as current health, universal port requirements, missing startup support, or permission to stop a service, install Ollama, expose a listener, or change generated configuration. |

## Operational controls review

The owner-supplied **Settings → GTKB controls** screenshot received 2026-09-26
shows eight operational fields under **GTKB configuration**, each with a
description, value, unit, and allowed range. That is useful existing guidance;
the remaining work concerns safe use and precise meaning, not adding a controls
page from scratch. See the illustrated [GTKB controls reference](Controls).
The checks below have not been executed against the running application.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Editable-looking numeric fields and Refresh are visible, but no Save, Apply, Cancel, or Reset button is shown. | Explain and test the exact save trigger, unsaved/pending/success/error feedback, persistence, and restoration of the previous value. Check blur, Enter, close, and Refresh without assuming any of them saves or discards changes. |
| **Must** | Values and a path ending in `config/governance/operational-controls.toml` are displayed without a value-source label. | Distinguish definitions, defaults, overrides, and effective runtime values; identify scope, consumers, precedence, and when changes take effect. Verify the actual target of Open configuration file rather than inferring it from the subtitle. |
| **Must** | Each row displays a numeric allowed range and a seconds or ratio unit. | Test types, precision, units, blank/non-numeric input, boundary values, and out-of-range input through the UI and supported writer. Verify a clear error and no partial configuration change on rejection; do not count a printed range as validation evidence. |
| **Must** | Minimum and maximum jitter ratios, and initial and maximum backoff values, appear as separate fields. | Define and test cross-field relationships, including individually in-range but incompatible combinations. Verify recovery from a failed combined edit and handling of competing edits without silently losing the operator's change. |
| **Must** | Descriptions concern probes and checkout-mutex acquisition/retry. | Document the operation and consequence of each control and verify runtime consumption. Do not interpret acquisition wait as lock-holding time, a bridge-claim lease, or ownership of a work item; do not treat increasing a timeout as a fix for an undiagnosed fault. |
| **Should** | Technical dotted keys, backoff, jitter, and mutex terminology dominate the view. | Preserve the keys but add plain-language labels, impact guidance, and a clearly advanced-operator route. Keep tuning out of the first-session prerequisites; evaluate whether a novice can complete Get Started without changing these fields. |
| **Should** | Descriptions and units are adjacent to input fields; the capture contains no interaction evidence. | Test keyboard focus/order, accessible names and units, decimal entry, error announcements, and readable layout at zoom. Add a version-pinned tuning/recovery walkthrough after the behavior is verified. |
| **Don't** | One installation's selected values and ranges are visible. | Do not publish them as universal defaults or a performance recommendation, infer autosave or the button's file target, prescribe manual generated-configuration edits, or test invalid values on an active host. |

## Models review

The owner-supplied **Settings → Models** screenshot received 2026-09-26 shows
API-key guidance, a **GTKB OpenRouter** entry marked **Custom**, a green dot,
**Edit**, **Add provider**, and **Add a custom provider**. Provider management
is an existing interface; its complete setup path and status meaning remain
unverified. A later Home capture explicitly labels the separate composer
popover **Model**, repeats the displayed reference, and exposes a right-facing
chevron. Its destination, alternatives, and reference resolution remain unseen.
The later `model` command's helper specifies **this conversation**, adding an
explicit scope description but not a tested selection or persistence result.
No credentials were opened or entered, no model was changed, and no request was
made. See [Models and providers](Models).

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Add provider and Add a custom provider are separate buttons; neither dialog is open. | Explain when to use each route, document actual required fields and supported choices, and qualify a path from an unconfigured installation to a successful first response. Test save, cancel, persistence, duplicate handling, and recovery without exposing keys. |
| **Must** | The provider entry has a green dot but no visible text status or check time. | Define the indicator and distinguish an entry being present from credentials being valid, a service being reachable, and a model request succeeding. Test missing/invalid credentials, unreachable endpoints, unavailable models, and usage-limit errors with useful next actions. |
| **Must** | Home's popover labels the reference Model and shows a chevron without its destination; the model command helper specifies this conversation. | Document both routes' actual choices and reference-to-provider/model mapping. Verify the effective endpoint/model/account, advertised conversation scope, inheritance, persistence, and changes to new versus active sessions. Test unresolved references and unavailable models with useful recovery, not silent substitution. Distinguish the model reference from the agent-mode preset; do not treat its display name as an API model ID or working credential. |
| **Must** | The helper asks for API keys; no secret-entry or storage details are shown. | Verify masking, save/replacement/removal behavior, storage protection, and redaction from logs, exports, screenshots, and support output. Explain provider-side revocation separately from removing a local entry. Use non-secret placeholders in training. |
| **Must** | The view does not explain request charges or where model data goes. | Before the first-request step, identify the selected provider/account, endpoint, model, usage limits, and data destination. Link to the provider's current official guidance for the tested setup; do not imply included usage or local-only processing from a local GTKB interface. |
| **Should** | The Settings list exposes Edit and two Add routes; Home reveals Model only after opening the reference-labeled control. | Add concise in-context guidance distinguishing provider setup, model selection, and agent mode, plus a captioned first-response demonstration. Test discoverability, keyboard navigation into/out of the Model row, dismissal, focus restoration, accessible names, and a non-color explanation for the provider dot. |
| **Don't** | One custom-named provider entry and a green dot are visible in Settings; Home repeats one reference on its trigger and Model row without showing alternatives. | Do not count these as two models or a complete inventory, claim a successful API call, infer a default or required provider, invent endpoint/model/price values, publish a key, or run a potentially billable request merely to confirm the screenshot. |

## Plugins review

The owner-supplied **Settings → Plugins** screenshot received 2026-09-26 shows
**Plugin configuration**, an unselected **Plugin list** tab, and four collapsed
sections. Plugin configuration already has a UI; the remaining work concerns
its detailed controls, inventory, and behavior. No settings were changed and no
plugin tool was executed through GTKB for this review. See [Plugins](Plugins).

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Shell, Agent loop, Subagent, and Web search are all collapsed. | Document the actual expanded fields, meanings, defaults versus current values, valid choices/units, and scope. Verify save/cancel, persistence, restoration, error feedback, and effects on active versus new sessions. |
| **Must** | Plugin list exists, but its contents are not shown. | Establish the real inventory and document identifiers, sources/versions, required versus optional components, and loaded/disabled/error states where supported. Explain actual lifecycle and recovery operations; missing or unclear information remains a finding, not permission to invent controls. |
| **Must** | Shell says it limits every command the agent runs. | Define the exact limits and enforcement boundary, then test allowed and correctly refused commands in a controlled installation. Verify useful diagnostics and recovery without bypassing intended restrictions; do not treat this helper as a proven sandbox guarantee. |
| **Must** | Agent loop describes tool-call dispatch, while Subagent describes model choice. | Explain their actual behavior and distinguish it from GTKB workflow dispatch, project authorization, agent-role assignment, and independent review. Test documented selection and scheduling rules; do not imply durable work-item ownership or treat a model setting as delegation permission. |
| **Must** | Web search names a provider without showing its configuration. | Document the supported setup, data destination, credentials, usage implications, and failure/recovery path. Qualify a non-sensitive search only with the intended provider and limits established; do not expose secrets or infer connectivity from the label. |
| **Should** | The overview offers short descriptions and collapsed cards, but no expanded example in this capture. | Add a version-pinned capabilities/limits tour and task-oriented examples after behavior is tested. Verify keyboard expansion, focus order, accessible names, and understandable error/status feedback; keep advanced tuning out of routine first-run prerequisites. |
| **Don't** | Configuration cards are visible, but inventory, values, and tool results are not. | Do not count cards as installed plugins, claim enabled or healthy tools, infer autosave or provider exclusivity, edit generated configuration, or execute commands, searches, or subagents merely to confirm this screenshot. |

## Agent presets review

The owner-supplied **Settings → Agent presets** screenshot received 2026-09-26
shows four built-in mode cards, **Standard mode** marked **In use**, and a
custom-preset drafting entry point. A later Home capture shows the four-mode
menu open, Standard checked, and PTC's complete description. This closes the
missing-menu-image and clipped-description gaps, not switch behavior,
authoring, persistence, or executed capabilities. No preset was changed or
drafted. See [Agent presets](Agent-Presets).

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Standard, PTC, Minimal, and Creator have capability descriptions; Minimal names persistent bash and `str_replace_editor`. | Provide a task-oriented comparison, prerequisites, limitations, and tested capabilities for each supported preset. Verify Windows shell requirements and persistence lifetime. Fewer advertised tools do not establish read-only access or a safer permission level. |
| **Must** | Standard has an In use badge in Settings and a checkmark in the later open Home menu. | Define the scope of each marker and qualify switching, cancellation, label/checkmark updates, effective preset/model, persistence, and behavior for new versus active sessions. Do not assume a factory default, synchronization across views, or that a click changes an existing session. |
| **Must** | The helper defines a preset by tools, prompt, and capabilities; Home also has a separate `@preset/...` composer reference. | Explain how agent-mode composition relates to the model/provider reference, effective plugin settings, and session permissions. Keep governed roles, project authorization, independent review, and per-artifact claims separate; do not imply durable ownership of work or permission to launch every advertised capability. |
| **Must** | The helper offers duplication; Custom offers Draft a custom preset with Creator mode. No authoring result is shown. | Document and test the actual duplicate/draft, review, validation, save/cancel, apply, and recovery routes with non-sensitive examples. Establish storage, scope, and provider usage before recording; do not treat generated prompt/tool configuration as already validated or manually edit generated harness files. |
| **Must** | Card actions are icon-only; PTC's Settings card is clipped but its Home menu description now fully mentions one TypeScript program; Creator displays `cordis` in Settings. | Verify discoverable labels/tooltips, keyboard operation, accessible names, and descriptions that remain readable at supported viewport/text sizes. Explain the PTC acronym and user-facing name/identifier mapping; do not infer SDK behavior or icon functions from the text or appearance alone. |
| **Should** | Both the Settings overview and open Home menu provide descriptions and a visible selected-state marker. | Use the illustrated Home menu in a short mode-choice segment and first-session video, based on a tested built-in path. Keep Creator/plugin experiments in an advanced supplement; measure whether a novice can distinguish mode from model reference and choose appropriately without writing a custom preset. |
| **Don't** | One historical selection and a scrollable set of capability cards are shown. | Do not infer a complete inventory, a universal default, enforcement, lower cost, provider connectivity, completed custom authoring, or working tools from this capture. Do not launch goals, workflows, searches, commands, or subagents merely to confirm it. |

## Documentation migration

- Older repository and Wiki pages contain retired product terminology and
  architecture. The current Wiki pages are replacing those descriptions in
  stages.
- Historical pages may mention Deliberation Archive, TAFE, SQLite,
  PAUTH, DECISION records, `.gtkb-state`, or `harness-state`. Those references
  do not describe the current authority model.
- GitHub Pages previously served an application documentation site and is not
  the GTKB product-documentation home. This Wiki is the designated product
  documentation surface.

Report a newly discovered customer-impacting issue through [Support](Support).
