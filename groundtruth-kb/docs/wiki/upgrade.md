# Upgrade

**Status:** Whole-product upgrade workflow not yet unified
**Reviewed:** 2026-09-26

GTKB currently has component and application upgrade mechanisms, but this Wiki
does not yet claim a single customer-grade whole-product upgrade command.

Before any upgrade:

1. Read release-specific upgrade notes.
2. Verify the current installation and canonical service.
3. Confirm a tested, out-of-band recovery path.
4. Record current component versions and configuration.
5. Stop only the components named by the procedure.
6. Preserve user work and unrelated repository changes.

After an upgrade, re-run [Verify installation](Verify-Installation), perform the
required schema and canonical readbacks, open GTKB Home, and verify behavior
after a controlled Windows restart.

Do not treat successful package replacement as complete product upgrade. Do not
manually edit generated harness projections to simulate an upgrade.
