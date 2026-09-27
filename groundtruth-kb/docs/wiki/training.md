# Training

**Status:** Training plan; videos not yet published

**Reviewed:** 2026-09-26

Written, versioned instructions remain the primary source. Videos will supplement
them, not replace them.

## Priority training set

1. **What GroundTruth KB is** — a three-minute product and boundary overview.
2. **Home and the first session** — choose a workspace, explain the actual mode
   choices, show any required provider setup, and demonstrate the first response.
   The initial [Home screen guide](GTKB-Home), illustrated [General Settings
   reference](Settings), [Models/provider list guide](Models), and [Agent presets
   overview](Agent-Presets) are available; the complete sequence still needs
   validation and additional screenshots. The [Windows directory picker](Get-Started#the-windows-directory-picker)
   is illustrated before confirmation, and the [selected-workspace Home view](Get-Started#home-with-a-selected-workspace)
   now shows the workspace name, a New Session entry, and the open mode menu
   with Standard checked. Reproduce the transition in a test installation;
   demonstrate Select Folder, Cancel, resolved-path verification, and composer
   readiness rather than treating the screenshots as an interaction test. Use
   a non-sensitive sample directory and distinguish folder selection from
   application registration. Explain the tested built-in mode choice and what
   In use/checkmarks mean without treating them as a governed role or permission
   level. Do not require custom-preset authoring for routine first use.
   Explain Add provider versus Add a custom provider, the status indicator, and
   how the separate composer reference resolves to the provider/model, distinct
   from the agent-mode preset. Keep real keys off-camera, identify usage and
   data-destination implications, and use non-sensitive sample content. The
   [Home permission menu](Settings#session-permission-menu-on-home) now supplies
   Read Only, Workspace Write, and Full access as visible choices. Demonstrate
   the qualified permission scope and correct refusals using disposable sample
   files, distinguish the General default from the composer selection, and
   explain when changes take effect. Do not teach Full access as a routine
   prerequisite or error-recovery shortcut. Include verified busy-input behavior.
3. **Install and first launch** — a clean Windows installation through a healthy
   GTKB Home.
4. **First governed change** — requirement, linked test, proposal, independent
   review, implementation report, verification, and Git result.
5. **Operator essentials** — services, diagnostics, backup, restore, upgrade,
   and uninstall. Include **Settings → GTKB** using the [status guide](Status),
   the difference between unknown session context and service failure, and the
   distinction between a configured dashboard link, reachability, and data
   freshness. Use **Settings → GTKB services** and the [Services guide](Services)
   to explain required versus optional components and application versus task
   state. Demonstrate safe service interruption and recovery only after that
   workflow has been tested in a separate qualification installation.

An **advanced operational tuning** supplement should use the
[GTKB controls reference](Controls) to explain value sources, the actual save
trigger, validation, runtime effect, and restoration of prior settings. Keep it
out of the first-session prerequisites and record it only after the editing and
recovery workflow is verified. Do not present the screenshot's values as a
recommended tuning profile.

A **plugin capabilities and limits** walkthrough should use the [Plugins
overview](Plugins), then show the actual expanded controls and Plugin list after
their behavior is verified. Explain supported tool boundaries, correct refusals,
save/recovery behavior, and provider-backed data/usage implications. Distinguish
harness tool-call dispatch from GTKB workflow dispatch, and subagent model
choices from permission to delegate. Keep advanced tuning out of routine
first-session prerequisites; do not run commands, searches, or subagents simply
to demonstrate that a configuration card exists.

A **custom preset authoring** supplement should demonstrate the verified
duplicate/Creator workflow, review of the resulting prompt and capabilities,
save/cancel, explicit application, and recovery. The Home menu now supplies the
complete PTC description, including one TypeScript program; explain its tested
tradeoffs, Minimal mode's Windows shell requirements, and actual icon actions
in the built-in comparison before making recommendations. Keep secrets and
private prompts out of recordings; a generated preset still needs validation.

Every video must identify the GTKB version, include captions and a transcript,
link to the corresponding Wiki procedure, show expected results, and be reviewed
or retired when the product changes.

Keep improving written Get Started guidance and screenshots while videos are
prepared. A short Home tour can be published once its demonstrated sequence is
verified; it need not wait for a complete training course. Installation and
[First governed change](First-Governed-Change) videos require qualification of
their corresponding procedures before recording or publication.
