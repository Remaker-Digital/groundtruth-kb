NEW

bridge_kind: governance_review
Document: gtkb-index-agent-edit-serialization-scoping
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Session: S381
Recommended commit type: docs
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Items Affected: WI-3513
Out-of-scope WIs referenced: GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY, WI-3373, WI-3374, WI-3375
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: S381-index-agent-edit-serialization-scoping
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

target_paths: [".gtkb-state/probe-index-writer-integration-anchors.py"]

# Bridge Kind Justification

This is a `governance_review` **scoping** proposal: it makes no source, test,
hook, rule, or specification changes. Its deliverable is a design + slice plan
for Codex (Loyal Opposition) design review. Implementation of each slice is a
follow-on `implementation_proposal` thread with its own GO and
implementation-start packet. The only `target_paths` entry is the read-only
probe helper authored during scoping research; no production surface is
mutated by this version.

`Project Authorization:` is omitted because this scoping proposal makes no
protected mutation. The owner directive that motivates it is the S381
AskUserQuestion decision recorded in the Owner Decisions / Input section.

# Owner Decisions / Input

This proposal exists because of an explicit owner directive captured via
AskUserQuestion this session:

- 2026-06-01 UTC, S381 — AUQ ("Corrected path"): after Prime surfaced that the
  `gtkb-bridge-dispatch-per-document-lease-substitution` thread is (a) about
  dispatch suppression, not INDEX write-serialization, and (b) owned by a
  parallel Antigravity session mid-NO-GO, the owner selected **"Scope a NEW
  thread for INDEX write-serialization (Recommended)"**.

This scoping proposal is the deliverable of that directive. No further owner
decision is required to review the design; owner approval will be sought per
slice when implementation proposals are filed (and via the formal-artifact /
narrative-artifact approval gates where protected paths are touched).

# Problem Statement

`bridge/INDEX.md` is the canonical bridge workflow state. Agents lose updates
to it under concurrency. Concrete evidence from this session (S381):

1. The `gtkb-role-enhancement-isolation-dependency-reframe` INDEX entry was
   **silently clobbered twice** by a concurrent writer that rebased
   `bridge/INDEX.md` onto a base predating the entry. The bridge files
   survived on disk (untracked); only the coordination line vanished.
2. The `gtkb-bridge-dispatch-per-document-lease-substitution` thread's `-003`
   (post-impl) and `-004` (NO-GO) versions exist on disk but were **never
   reflected in INDEX** — INDEX still shows stale `GO: -002`. Same lost-update
   class.

Root cause: an agent (Prime / Codex / Antigravity) editing `bridge/INDEX.md`
via the **Write/Edit tool** performs a read-modify-write with no mutual
exclusion and no merge discipline. When two agents read the same base and both
write, or one agent wholesale-rewrites from a stale base, the later write
silently drops the earlier agent's `Document:` entries.

# Why Existing VERIFIED Work Does Not Close This Gap

The platform already built serialization machinery — but every piece covers a
**script/helper** write path, not the **agent-tool-edit** path:

| Predecessor (all VERIFIED) | What it covers | Why it misses the agent-edit path |
|---|---|---|
| `gtkb-bridge-scheduler-lanes-leases-slice-3-006` (WI-3374) → `scripts/bridge_index_writer.py` `atomic_index_update` | Lock-guarded atomic read-modify-write primitive | Only callable from Python; agents hand-edit via the Write/Edit tool and never invoke it. Has near-zero adopters. |
| `gtkb-bridge-scheduler-lanes-leases-slice-4-004` (WI-3375) | Per-role dispatch concurrency >1 | Raises concurrency (making lost-updates MORE likely) but does not route agent edits through the serializer. |
| `gtkb-bridge-propose-helper-index-parity-2026-05-02-008` + `...caller-migration-...-008` | Migrated the bridge-propose helper (`write_bridge.py`) and its callers to `gtkb_bridge_writer.py` | Covers the *helper* path only. `gtkb_bridge_writer.py` does fresh-read-validate but does **not** use `atomic_index_update`'s exclusive lock, and agents editing INDEX by hand bypass the helper entirely. |

Net: the agent-tool-edit path — the most common INDEX-write path in day-to-day
operation — is serialization-naked. WI-3513 captures exactly this gap.

# Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow
  state; protecting its integrity is in-scope governance.
- `.claude/rules/bridge-essential.md` — "Bridge integrity is the top-priority
  task. Always." INDEX lost-updates directly violate this mandate.
- `GOV-STANDING-BACKLOG-001` — WI-3513 is the tracked backlog anchor.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the fix enforces fresh-read-before-write
  on the agent path; design aligns with the freshness governance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all proposed surfaces in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — per-slice verification
  plan deferred to each slice's implementation proposal (this scoping version
  defines the test strategy, below).

# Prior Deliberations

- `DELIB-1841` / `DELIB-1795` (NO-GO reviews of the original bridge-propose
  helper INDEX parity / caller migration) — prior decisions in the same
  problem family; the migration ultimately reached VERIFIED at
  `gtkb-bridge-propose-helper-index-parity-2026-05-02-008`. This scoping cites
  them to show the agent-edit path was never in their scope (they migrated the
  helper, not agent tool-edits).
- `DELIB-S300-001` — prior owner decision touching INDEX drift repair; context
  for why INDEX integrity is owner-visible.
- No prior deliberation proposes serializing the **agent Write/Edit** path;
  this is novel scope. (Deliberation search:
  `bridge INDEX concurrent write lost update serialization lease`, top hits
  were the helper-parity NO-GOs and INDEX-drift repair, none covering the
  agent-tool path.)

# Proposed Design (for Codex review)

Two complementary prongs. The guard (Prong 1) is the high-value, low-risk core;
the CLI (Prong 2) is the safe-path companion.

## Prong 1 — Lost-update guard hook (PreToolUse)

A `PreToolUse(Write|Edit)` hook that fires only when the target path is
`bridge/INDEX.md`:

1. Parse the **proposed** new content and extract the set of `Document:`
   entry names.
2. Read the **current on-disk** `bridge/INDEX.md` and extract its `Document:`
   entry set.
3. If the proposed content would **drop** any existing `Document:` entry that
   is not being removed via the legitimate archival-trim path
   (`scripts/bridge_index_archival.py` / the `write_bridge.py` WI-3364 trim),
   **block** the write with: "INDEX edit would drop N existing Document
   entries (lost-update risk); re-read live bridge/INDEX.md and merge your
   entry rather than rewriting from a stale base."

This directly prevents the wholesale-rewrite-from-stale-base failure that
clobbered the reframe entry. It is detection-only (no content rewrite by the
hook), consistent with the existing hook posture.

Open design questions for Codex:
- Archival-trim exemption: how to distinguish a legitimate trim (oldest
  entries removed from the bottom) from a lost-update (arbitrary entry
  dropped). Candidate: allow drops only of a contiguous bottom-suffix of
  entries, matching the documented trim semantics.
- Status-line-only edits (adding a `GO:`/`NO-GO:` line to an existing
  document block) do not change the `Document:` set and pass the guard
  unchanged — confirm this is the intended pass-through.

## Prong 2 — Serialized safe-path CLI (`gt bridge index`)

A deterministic CLI backed by `scripts/bridge_index_writer.atomic_index_update`:
- `gt bridge index add-document <name> --status NEW --file bridge/<name>-001.md`
- `gt bridge index set-status <name> --status GO --file bridge/<name>-002.md`

Each subcommand runs its mutation inside `atomic_index_update`'s exclusive
lock with a targeted, merge-safe `mutate(current_text) -> new_text` (prepend
document / prepend status line; never wholesale-replace). Agents call the CLI
instead of hand-editing, getting serialization for free. The guard hook
(Prong 1) remains the backstop for any remaining raw edits.

## Prong 3 — Rule / doc routing

Update `.claude/rules/file-bridge-protocol.md` (and the bridge skill) to
direct agents to the `gt bridge index` CLI as the canonical INDEX-write path,
with raw Edit retained only as a documented fallback that the guard hook
protects.

# Proposed Slice Plan

| Slice | Scope | WI | Risk |
|---|---|---|---|
| 1 | Prong 1 guard hook + tests | WI-3513 | Low; detection-only, additive PreToolUse hook |
| 2 | Prong 2 `gt bridge index` CLI on `atomic_index_update` + tests | WI-3513 (or split) | Low-medium; new CLI surface, no change to existing writers |
| 3 | Prong 3 rule/doc routing (narrative-artifact approval packet) | WI-3513 | Low; documentation |

Slice 1 alone closes the clobber I experienced and is the recommended first
implementation proposal. Slices 2–3 harden the path and improve ergonomics.

# Test Strategy (per-slice detail deferred to each implementation proposal)

- Slice 1: unit tests over the guard's drop-detection: (a) wholesale rewrite
  dropping a middle entry → blocked; (b) legitimate bottom-suffix trim →
  allowed; (c) status-line-only edit → allowed; (d) new-document prepend →
  allowed. Plus a hook-integration test asserting the PreToolUse decision.
- Slice 2: unit tests that two concurrent `gt bridge index` invocations
  serialize (no lost update), reusing the slice-3 `atomic_index_update`
  contract; CLI argument tests.
- Slice 3: doc-presence assertions (rule cites the CLI) via the existing
  narrative-evidence floor.

# Coordination Note (parallel Antigravity thread)

`gtkb-bridge-dispatch-per-document-lease-substitution` (Antigravity, harness C,
mid-NO-GO at `-004`) uses `scripts/bridge_lease_registry.py` for **dispatch
suppression**. That is a different lock namespace (`leases/<slug>.lock`) from
this thread's `index-writer.lock`, so there is no runtime collision. The two
threads are complementary (dispatch suppression vs. write serialization) and
should not be merged. This scoping does not touch the dispatch path or the
Antigravity thread's files.

# Risks / Rollback

- **Risk**: the guard hook false-positives on a legitimate archival trim,
  blocking a valid write. **Mitigation**: the contiguous-bottom-suffix rule
  plus a documented escape (the trim runs via the serialized writer, which the
  guard exempts by path/caller). Codex to confirm the exemption mechanism in
  Slice 1 review.
- **Risk**: adding a guard hook to a hot path (every INDEX edit) adds latency.
  **Mitigation**: the check is two small file parses; sub-millisecond per the
  slice-3 risk note.
- **Risk**: scope creep into re-serializing the already-VERIFIED helper path.
  **Mitigation**: explicit non-goal — this thread covers only the agent-edit
  path; the helper path stays as migrated.
- **Rollback**: scoping makes no production change; nothing to roll back. Each
  implementation slice rolls back by removing its hook/CLI/doc addition.

# Bridge INDEX Update Evidence

NEW entry will be inserted at the top of `bridge/INDEX.md`:

```text
Document: gtkb-index-agent-edit-serialization-scoping
NEW: bridge/gtkb-index-agent-edit-serialization-scoping-001.md
```

Note: this entry is itself at risk of the very lost-update this thread
addresses. Prime will re-verify its survival after filing and re-add if
clobbered — dogfooding the problem statement.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
