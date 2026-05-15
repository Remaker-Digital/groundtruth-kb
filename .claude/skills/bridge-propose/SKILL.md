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

**Project-linkage metadata (per ``DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001``)**:
the proposal body for an implementation-targeting NEW/REVISED proposal MUST
include three machine-readable header lines near the top::

    Project Authorization: PAUTH-<authorization-id>
    Project: <PROJECT-ID>
    Work Item: <WI-NNNN | GTKB-* | WORKLIST-*>

``bridge-compliance-gate.py`` hard-blocks the Write when any line is absent.
Non-implementation proposals self-declare exemption with a ``bridge_kind:``
header in ``{spec_intake, governance_review, loyal_opposition_advisory}``;
verdict files (GO/NO-GO/VERIFIED/WITHDRAWN) are exempt by status.

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

### Phase 0 — Prior Deliberations pre-population (default-on)

Per Phase 2 of the GTKB-DA-READ-SURFACE-CORRECTION program
(``ADR-DA-READ-SURFACE-PLACEMENT-001`` Path D), the helper pre-populates
the proposal's ``## Prior Deliberations`` section before the credential
scan. Two-stage retrieval:

1. **Glossary-source seeding (deterministic).** The helper reads
   ``.claude/rules/canonical-terminology.md`` and looks for a
   ``### <heading>`` matching the topic slug (kebab-case → space-separated,
   case-insensitive). If matched, the heading's ``**Source:**`` block is
   parsed and ``DELIB-*`` / MemBase spec IDs are extracted as deterministic
   seed candidates.
2. **Semantic search (broad coverage; default-on).** The helper opens a
   default ``KnowledgeDB("groundtruth.db")`` automatically and queries
   ``search_deliberations(query, limit=...)``. Results are added on top
   of the seeds, deduplicated. Pass ``db=`` to override with an explicit
   instance, or ``db=False`` to disable semantic search entirely. If the
   default DB cannot be opened (missing file, import error), the helper
   silently falls back to glossary-only seeding.

When the topic is genuinely novel (no glossary entry, no DA matches), the
helper inserts an ``_No prior deliberations: <fill in reason before
filing>._`` placeholder so the proposal does not fail the LO review-side
check that NO-GOs empty Prior Deliberations sections.

Combined candidates are formatted as Markdown bullets and inserted into
the body's ``## Prior Deliberations`` section under the marker comment
``<!-- Pre-populated by helper; review and prune. -->``. If the section
is absent, it is appended at end of body. If the section already has
author content, helper-suggested candidates land under a
``### Helper-suggested candidates`` subheading instead of overwriting
prior content.

The author then reviews and prunes irrelevant entries before the
proposal is filed. The Loyal Opposition review-side check (``codex-review-gate.md``
sixth review obligation) NO-GOs proposals with empty Prior Deliberations
sections lacking justification (a ``_No prior deliberations: <reason>._``
line is the explicit empty-justification convention for novel topics).

**Opt out:** pass ``pre_populate_prior_deliberations=False`` to
``propose_bridge()``. Opt-out callers must include the empty-justification
line per the LO review check.

**Audit log:** every invocation writes
``.gtkb-state/bridge-propose-helper/last-prepopulation.json`` with the
timestamp, topic slug, derived query, glossary-seed IDs, search-result
IDs, similarity threshold, and total candidate count. Pass
``pre_populate_log_path=False`` to disable logging.

**S331 anti-regression.** The original S331 wrong-frame failure was an
agent producing an evaluation of "GT-KB isolation" without consulting the
DA, which contained four lifecycle-independence anchor records. With this
helper enabled, authoring a proposal on the topic ``"isolation"`` reads
the Phase 1 glossary entry's ``**Source:**`` block and deterministically
seeds those four DELIB IDs into the populated section. The mechanism is
seed extraction, not semantic-search ranking — making the anti-regression
mechanically grounded.

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
- The Phase 0 pre-population stage is non-fatal; failures during
  glossary read, semantic search, or audit-log write are swallowed
  (graceful degradation). The proposal proceeds without pre-populated
  candidates if any stage fails.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
