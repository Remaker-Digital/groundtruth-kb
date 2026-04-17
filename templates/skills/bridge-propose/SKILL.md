---
name: gtkb-bridge-propose
description: Write a bridge proposal to ``bridge/<topic>-001.md`` and insert its entry into ``bridge/INDEX.md`` under governance-safe credential-scan and concurrency controls. Use when drafting a new NEW or REVISED proposal through the helper path (non-Claude-Write).
---

This skill implements the helper-mediated bridge-write path. It is the
safe alternative to persisting proposal bodies through non-Write code
paths (``file.write_bytes``, ``shutil.copy2``, etc.) that are outside
the ``scanner-safe-writer`` hook's Write-tool trigger scope.

# /gtkb-bridge-propose

## What this skill does

Takes a topic slug and a proposal body, scans the body against the
canonical credential catalog (``CREDENTIAL_PATTERNS + BASH_EXTRAS``,
PII excluded), writes ``bridge/<topic>-001.md``, and inserts a
``Document: <topic>`` + ``NEW: bridge/<topic>-001.md`` entry at the
top of ``bridge/INDEX.md``.

Two options are offered on a credential hit:

- **Abort** — no file is written, no INDEX entry is added.
- **Redact** — credential-shaped spans are replaced with
  ``[REDACTED:<label>]`` markers. Redacted content is re-scanned. If
  the second scan still finds hits, the skill aborts with an
  explicit ``RedactionResidualError`` — this is a bug, not a
  recoverable user state.

**There is no Force option.** Helper writes are outside the
``scanner-safe-writer`` hook's Write-tool trigger scope, so a bypass
here would silently persist credential-shaped text without an
auditable deny record. Callers who genuinely need to document
credential-shaped values (test fixtures, rotation runbooks) should
use prose descriptions or runtime-assembled test fixtures — not a
helper bypass.

## When to invoke

Use this skill when:

- Drafting a new NEW bridge proposal from session context
- Writing a REVISED version after a NO-GO (pick a fresh file name
  with incremented version suffix)
- Any helper-driven code path that needs to persist a bridge
  proposal body to disk under governance

Do NOT use for:

- Editing an existing bridge file (Edit tool is the correct path)
- Writing non-bridge files (``bridge/INDEX.md`` is managed by the
  skill; other files are out of scope)
- Persisting credential-shaped content (redaction is the only
  legitimate path; force-write is not available)

## How it works

Invokes ``helpers/write_bridge.py``'s ``propose_bridge()`` with the
caller-supplied ``topic_slug``, ``body``, and optional metadata.

### Phase 1 — Pre-flight scan

``scan_credential_hits(body)`` iterates ``CREDENTIAL_PATTERNS +
BASH_EXTRAS`` (PII patterns are intentionally excluded, same policy
as ``scanner-safe-writer``). Returns list of hits; empty list means
the body is clean.

### Phase 2 — Hit resolution

If hits are non-empty, the caller must pass ``mode="abort"`` or
``mode="redact"``:

- ``abort`` raises ``CredentialHitsFoundError`` with the first hit's
  ``pattern_name`` and description.
- ``redact`` normalizes hit intervals (sort by ``(start, -end)``,
  merge overlaps, outer label wins), applies replacements in
  reverse-start order, then re-scans the redacted body. If the
  second scan returns any hits, ``RedactionResidualError`` is
  raised.

### Phase 3 — File-first write

``bridge/<topic_slug>-001.md`` is written atomically. If the file
already exists (for example, from a prior partial attempt with the
same slug), ``BridgeFileAlreadyExistsError`` is raised before any
INDEX touch. The skill never silently overwrites.

### Phase 4 — INDEX insertion with retry

The ``Document: <topic_slug>`` + ``NEW: bridge/<topic_slug>-001.md``
entry is inserted at the top of ``bridge/INDEX.md`` (after leading
comment lines). The write uses a temp-file + atomic ``os.replace``
pattern. If INDEX.md changes between the read and the rename, or if
another writer already inserted an entry for the same topic, the
write is retried once. Total budget: **2 attempts** (1 initial + 1
retry). On second failure, ``BridgeIndexConflictError`` surfaces
with an actionable message (the bridge file is already on disk;
manually add an INDEX entry or retry the skill).

## Errors

- ``CredentialHitsFoundError`` — hits found and ``mode="abort"``.
- ``RedactionResidualError`` — second scan after redaction still
  finds hits. Indicates a catalog/redactor bug, not a user state.
- ``BridgeFileAlreadyExistsError`` — target file already on disk;
  skill refuses to overwrite.
- ``BridgeIndexConflictError`` — INDEX.md changed during the write,
  or another writer inserted an entry for the same topic. Retry
  budget exhausted after 2 total attempts.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
