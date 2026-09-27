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
- The initial Home screenshot is now published in [GTKB Home](GTKB-Home) and
  [Get started](Get-Started). The workspace picker, selected workspace,
  mode choices, settings, and a successful first session still need illustrated,
  version-pinned coverage.
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
| **Should** | No readiness indicator or help/recovery link is visible in this view. | Make the supported health check and troubleshooting route easy to find. Test the route both on a healthy host and when a required component is unavailable. |
| **Should** | Written orientation now has one image, but no completed-session visual sequence. | Add a selected-workspace image and a short, captioned first-session demonstration linked to the written procedure. Check that a new user can reproduce the demonstrated result. |
| **Don't** | The browser displays Home, a **Preview** label, and an empty session list. | Do not treat this as proof of installation completeness, service readiness, missing canonical work, or a successful governed workflow. Check those outcomes separately. |

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
