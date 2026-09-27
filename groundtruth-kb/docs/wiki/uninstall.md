# Uninstall

**Status:** Whole-product uninstaller not yet unified
**Reviewed:** 2026-09-26

GTKB does not yet document a single command that safely removes every component
of a complete Windows host.

A complete uninstaller must distinguish:

- product binaries;
- Windows services and scheduled tasks;
- Start-menu and optional desktop launch entries;
- logs and caches;
- canonical PostgreSQL data;
- credentials;
- backups and WAL archives;
- application repositories; and
- user-authored configuration.

Data, credentials, backups, or application repositories must not be silently
deleted. The user should select a retention policy and see the exact targets
before removal.

The current GTKB Home installer has a component-specific uninstall operation,
but that does not uninstall PostgreSQL, the native service, applications, or
retained data. Until a qualified whole-product uninstaller exists, removal is an
operator procedure and should be planned with [Support](Support).
