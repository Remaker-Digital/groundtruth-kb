# Backup and restore

**Status:** Operator overview; use release-specific qualified procedures
**Reviewed:** 2026-09-26

GTKB's canonical PostgreSQL data requires a verified physical backup together
with the WAL needed to recover beyond that backup. A copy on the same physical
volume is staging, not protection against loss of that volume.

## Required properties

- Keep a verified base backup and its required WAL sequence together.
- Copy recovery material to an out-of-band destination appropriate to the loss
  scenario.
- Do not prune WAL by age alone.
- Protect credentials and recovery material with the intended filesystem access
  controls.
- Test recovery from the off-volume copy, not merely from the live installation.
- Record the recovered schema and application-relevant readback.

The selected release's `infrastructure/postgresql/README.md` contains the exact
operator tools and qualified procedure. This Wiki will carry the complete
customer procedure after the installer and backup registration are unified.

Successful backup creation is not recovery evidence. Release or operational
claims must cite a completed restore appropriate to the asserted failure
scenario.

## Session export is not a platform backup

The [Home Commands menu](GTKB-Home#commands-menu) describes `export` as a ZIP
download of the session log. This is a different purpose from protecting and
recovering canonical PostgreSQL state. No export was generated or inspected in
the documentation review, and no import or recovery path was demonstrated.
Do not count a session archive as a verified database backup, whole-product
recovery, or a redacted support bundle. See [Support](Support#feedback-and-session-log-export-in-home)
before sharing diagnostic content.
