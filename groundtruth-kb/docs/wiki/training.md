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
   reference](Settings), and [Models/provider list guide](Models) are available;
   the complete sequence still needs validation and additional screenshots.
   Explain Add provider versus Add a custom provider, the status indicator, and
   where model selection occurs. Keep real keys off-camera, identify usage and
   data-destination implications, and use non-sensitive sample content. Include
   session permission scope and the verified busy-input behavior.
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

Every video must identify the GTKB version, include captions and a transcript,
link to the corresponding Wiki procedure, show expected results, and be reviewed
or retired when the product changes.

Keep improving written Get Started guidance and screenshots while videos are
prepared. A short Home tour can be published once its demonstrated sequence is
verified; it need not wait for a complete training course. Installation and
[First governed change](First-Governed-Change) videos require qualification of
their corresponding procedures before recording or publication.
