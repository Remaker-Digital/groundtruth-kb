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
  [GTKB status guide](Status) now covers the **Settings → GTKB** pane. The workspace
  picker, selected workspace, mode and permission choices, remaining settings
  panes, and a successful first session still need version-pinned coverage and
  interaction checks.
- Training videos and transcripts are not yet published.
- A redacted automated support bundle is not yet documented as available.
- Cross-platform host installation is not currently established.

## Home first-run review

These findings use the owner-supplied Preview screenshot received 2026-09-26.
They apply to that visible empty state, not to every product screen. No
interaction, keyboard, screen-reader, or service-health test was performed from
the image. The improvements below are recommendations, not shipped features.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Workspace selection is required, but no first-run guide or documentation link is visible. | Provide a short in-context path to Get Started. A first-time evaluator should identify the next action and select the intended workspace without source-code inspection or operator coaching. Record time and assistance needed. |
| **Must** | **Standard mode** is shown without an explanation in this view. | Explain each actual mode, its effects, and any relationship to governed work. Verify the explanation against the selected release; do not infer capabilities from the label. |
| **Must** | Several controls are represented only by icons. | Test accessible names, keyboard focus and activation, and discoverable labels/tooltips. The screenshot cannot establish a pass or failure for those behaviors. |
| **Should** | No readiness indicator or help/recovery link is visible on the empty Home view. A subsequent capture establishes a status pane under **Settings → GTKB**. | Make the existing status and troubleshooting route easy to find from Home. Test it both on a healthy host and when a required component is unavailable; do not assume a status view must be built from scratch. |
| **Should** | The captured empty state does not show a completed-session sequence. | Add a selected-workspace image and a short, captioned first-session demonstration linked to the written procedure. Check that a new user can reproduce the demonstrated result. |
| **Don't** | The browser displays Home, a **Preview** label, and an empty session list. | Do not treat this as proof of installation completeness, service readiness, missing canonical work, or a successful governed workflow. Check those outcomes separately. |

## Settings review

These additional findings use the owner-supplied General Settings screenshot
received 2026-09-26. The [Settings reference](Settings) records the visible values
without treating them as shipped defaults or tested behavior. The newly visible
**GTKB services** tab provides a navigation lead; its contents and health
indicators have not been inspected. The separate **GTKB** tab is now illustrated
in the [status guide](Status). Neither observation changes what was visible on
the earlier Home empty state.

| Priority | Evidence in the captured view | Improvement and evaluation check |
| --- | --- | --- |
| **Must** | Permission is **Workspace Write**, and the helper describes a default for new sessions. | Document every actual permission option, allowed operations, scope, and approval behavior. Test new versus existing sessions and distinguish session permissions from project authorization. |
| **Must** | No Save, Apply, or Reset control is visible in the General pane. | Make save/apply timing and recovery clear. Test persistence after closing/reopening settings and restarting Home, and state which changes require a new session. Do not assume automatic saving from the absence of a button. |
| **Must** | **Enter behavior while busy** is **Queue**; the helper calls Cmd/Ctrl+Enter's action only the other behavior. | Name both actions and explain what happens to the active turn and subsequent input. Verify Enter and Ctrl+Enter on Windows in a safe test session. Do not invent the alternate action's name. |
| **Should** | **Compact** controls process content, but its exact visible effect is not illustrated. | Provide a before/after example using non-sensitive sample content. Explain what becomes hidden and whether it can be revealed again. |
| **Should** | **Open configuration file** does not name its target in the visible label. | Identify the target and settings scope, supported editing route, and recovery instructions before asking customers to use it. Do not direct manual edits to generated harness configuration. |
| **Don't** | Selected values and six additional settings-section labels are visible. | Do not present these selected values as factory defaults, a permission label as proven enforcement, or a settings tab as evidence that its services or integrations are configured and healthy. |

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
