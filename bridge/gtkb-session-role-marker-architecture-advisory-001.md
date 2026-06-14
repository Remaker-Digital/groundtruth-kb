ADVISORY

bridge_kind: governance_advisory
Document: gtkb-session-role-marker-architecture-advisory
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7752bc97-4760-42ce-ad94-6bc75bac943e
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive Prime Builder session 7752bc97; `::init gtkb pb` declared at session start; owner-directed advisory authoring with AUQ-captured owner decisions; non-implementing governance scope
Date: 2026-06-14 UTC

Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE

# Session-Role Marker Architecture Advisory

## Summary

Two distinct architectural defects in the session-role-marker substrate
(`.claude/session/active-session-role.json`, written by
`scripts/workstream_focus.py::_write_session_role_marker`) surfaced by
read-only diagnostic in interactive Prime Builder session `7752bc97-…` on
2026-06-14:

1. **Single-file marker representing multi-session state** — N concurrent
   sessions on the same workstation compete for one marker slot; the
   time-based freshness heuristic mis-fires; live owner-Prime sessions get
   locked out of their own `go_implementation` claims while another session's
   marker is < 30 min old.
2. **Marker silently wiped between owner turns** — Independent defect with
   separate (unidentified) root cause. The marker is reliably present at one
   turn and deleted at the next, with no owner-visible `::init` or perceived
   SessionStart between them.

Owner direction (AUQ-captured this advisory, 2026-06-14 ~06:42Z): commit
**per-session marker files** as the architectural fix direction; treat both
defects in **one umbrella advisory**; **drive implementation as the next
available session** under `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`.

## Evidence (this session)

- `CLAUDE_CODE_SESSION_ID=7752bc97-4760-42ce-ad94-6bc75bac943e` stable from
  session start (~16:40 PDT 2026-06-13) through advisory authoring
  (~23:44 PDT 2026-06-13 / 06:44Z 2026-06-14); confirmed by transcript file
  ctime / mtime continuity (`~/.claude/projects/E--GT-KB/7752bc97-….jsonl`,
  same UUID, continuous mtime updates across ~7 hours of contiguous turns).
- ≥ 4 concurrent transcripts active in the same window:
  `7752bc97-…` (this session, mtime 06:34Z), `62a726da-…` (06:33Z),
  `ce76da9c-…` (06:30Z), `aa9e2530-…` (06:29Z; recorded holder of an
  active bridge claim per AXIS-2 surface).
- Marker observed in three states across the session: pointing at
  `ce76da9c-…` (a prior session's marker, freshness-protected); deleted
  entirely; then pointing at `1d33598a-…` (yet another session that wrote it
  at 06:13Z). The owner declared `::init gtkb pb` on this session's first
  owner prompt; this session's `7752bc97-…` never owned a marker at any
  observed point — every marker write resolved to a different `session_id`.
- Resulting symptom: this session's `bridge_claim_cli.py claim … (go_implementation)`
  consistently rejected with
  "session '7752bc97-…' resolves to interactive session marker role None
  (not prime-eligible)" per the WI-4534 role-eligibility guard. Guard fired
  correctly; substrate failed to provide the positive Prime evidence that
  should have existed.

## Defect 1 — Single-file marker for multi-session state

### Root cause

The marker is a single-file resource representing multi-session state. The
freshness logic in `_write_session_role_marker` refuses an overwrite when an
existing marker for a different `session_id` was written ≤ 30 minutes ago.
The threat model behind this heuristic is "another session is still alive
and shouldn't be clobbered." But:

1. The substrate already exposes per-session identity through stable
   transcript UUIDs (`~/.claude/projects/E--GT-KB/<uuid>.jsonl`) — both via
   `CLAUDE_CODE_SESSION_ID` env and the hook payload `session_id` field.
2. Per-session liveness is directly observable from the same UUIDs via
   transcript-file mtime.
3. A workstation can host N concurrent live sessions (today: ≥ 4 observed).
   A single marker slot inherently cannot represent which session holds
   which role.

The time heuristic is a poor approximation of information the substrate
already provides.

### Owner-committed fix direction (AUQ this advisory — Option A)

**Per-session marker files.** `.claude/session/role-<session_id>.json` per
session. Each session writes / reads its own marker keyed to its own
transcript UUID. A periodic sweeper removes stale files when
`transcript_for(session_id).mtime < now - N_minutes`. The WI-4534
role-eligibility guard looks up the marker for the *querying* session's
`session_id` directly. No contention, no freshness heuristic, no lockout
of legitimate owner-Prime sessions.

Rejected alternatives recorded in the AUQ:

- **Option B — Multi-entry manifest** (`{session_id: role}` in one file):
  same correctness; trades per-file locking for whole-file locking on every
  write; slightly more contention but one inspection point.
- **Option C — Active-session detection patch** (replace `age <= 1800` with
  transcript-mtime check, single-file model retained): cheapest patch but
  preserves the structurally wrong single-file model.
- **Option D — Defer**: rejected; the friction is impacting workflow today.

## Defect 2 — Marker silently wiped between owner turns

### Symptom

The marker is observed present in one owner turn and absent in the next,
without an owner-visible `::init` or perceived SessionStart between them.
This session observed: marker present at 06:13Z (pointing at `1d33598a-…`),
deleted by ~06:36Z; subsequent owner turn confirmed absent. Multiple wipe
cycles across the session.

### Root cause hypothesis (UNCONFIRMED — investigation needed)

Candidates: a SessionStart event firing within what the owner perceives as
one conversation (per the canonical-glossary clause for session-stated role:
"invalidated at the next SessionStart … does not survive compaction or
resume"); a session-end hook from a peer / concurrent session wiping the
shared file; the AXIS-2 surface hook or another periodic hook
side-effecting on the marker. Substrate-side investigation is independent
of Defect 1's fix.

### Why bundled in this advisory (per owner AUQ — umbrella scope)

Per-session marker files (Defect 1's fix) neutralize the cross-session wipe
path structurally: no session would be writing into another session's file,
so wipes of one session's marker by another session's hook become
structurally impossible. Any remaining wipes would be same-session — a
more tractable investigation surface. Splitting the advisory in two would
duplicate context without yielding independent action paths.

## Specification Links

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — owner-declared interactive
  session role override; the contract this advisory's defects break.
- `DCL-SESSION-ROLE-RESOLUTION-001` — deterministic role-resolution table
  (marker > durable); per-session marker keying is consistent with this
  DCL's session-stated-role precedence.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable-vs-stated authority split;
  advisory does not modify this.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; advisory
  respects bridge as canonical workflow state and proposes no INDEX write
  surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — advisory cites
  every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — cited for cross-cutting
  applicability completeness; advisory has no test surface (governance scope,
  `requires_verification: false`), so the spec-to-test-mapping clause
  evaluates as `may_apply: —` (no evidence required) per the clause
  preflight. Any follow-on implementation proposal will fully comply with
  this DCL.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — advisory is itself
  a durable governed artifact under this ADR; owner decisions captured as
  durable DELIB records via AUQ.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — advisory lifecycle:
  ADVISORY → LO review → GO/NO-GO → implementation proposal (per owner
  posture); marker-wipe surface remains under investigation (`unconfirmed`
  status) until follow-on proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — owner decisions, work
  item references, project linkage, and specification citations all
  concretely linked; no implicit specifications introduced.
- `WI-4534` — the role-eligibility guard correctly enforces the
  session-stated-role contract; the defects here are substrate-side
  (marker writer / lookup keying), not guard-side.
- `WI-4545` — chronic TAFE-pilot peer-claim churn captured this session;
  same family of dispatched-worker / per-session-context architecture
  concerns, but independent fix surface (worker bootstrap vs marker keying).

## Prior Deliberations

- **AUQ this advisory** (2026-06-14 ~06:42Z, interactive PB session
  `7752bc97-…`) — fix direction = per-session marker files (Option A);
  scope = umbrella covering both defects; posture = drive implementation
  next available session. The owner-decision-tracker hook captures these
  as durable DELIB records; this advisory is their bridge-side anchor.
- This session's prior diagnostic chain across multiple turns: marker
  state observation, `bridge_claim_cli.py` rejection,
  `_write_session_role_marker` source read, multi-transcript enumeration,
  owner architectural correction ("transcripts reflecting the user's view
  of a contiguous series of turns exist") which sharpened the diagnosis
  from "stable identifier may not be available" to "stable identifier
  exists; the marker architecture fails to use it."
- `WI-4545` (this session, 2026-06-14 ~06:16Z) — chronic TAFE peer-claim
  churn (5+ Prime-B dispatched workers claimed and bailed on
  `gtkb-tafe-live-impl-flow-pilot` GO -004 without filing -005 or touching
  the on-disk impl). Same family of per-session-context substrate gaps.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-003.md`
  — Slice 2 of `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`; landed the
  current marker writer in `scripts/workstream_focus.py`. This advisory
  recommends amendment of that writer's keying model and the corresponding
  reader path.

## Owner Decisions / Input

Captured via `AskUserQuestion` in this session, 2026-06-14 ~06:42Z, prior
to advisory authoring. Each answer is durable owner direction for this
advisory and any follow-on implementation proposal:

1. **Fix direction (contention defect): Per-session marker files
   (Option A).** Rejected: Option B (multi-entry manifest), Option C
   (active-session detection patch), Option D (defer).
2. **Scope: One umbrella advisory** covering both defects (contention +
   marker-wiping). Rejected: two separate advisories; contention-only with
   marker-wiping deferred.
3. **Posture: Drive implementation as next available session.** P1
   priority — marker drift is actively impacting interactive Prime sessions
   (this session's lockout; chronic TAFE churn pattern). Implementation
   proposal becomes the next active work item for
   `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` (formal WI + PAUTH to
   be raised against this project at proposal time). Rejected:
   backlog-queue (P2), passive (P3).

## Implementation Recommendation (for the follow-on proposal)

The implementation proposal building on this advisory should, at minimum:

1. Replace `_write_session_role_marker` / `_session_role_marker_path`
   keying so each session writes / reads `.claude/session/role-<session_id>.json`.
2. Update the WI-4534 role-eligibility guard's lookup path
   (`scripts/bridge_work_intent_registry.py::_go_implementation_eligible`)
   to look up the marker for the querying session's `session_id` rather
   than the legacy single-file path.
3. Add a stale-marker sweeper (transcript-mtime-based) callable from
   session-wrap and / or a periodic hook.
4. Investigate and capture the marker-wipe surface (Defect 2) — identify
   the hook(s) wiping the marker; either retire that wipe (no longer
   needed under per-session keying) or restrict it to same-session
   targets.
5. Specification-derived tests covering: per-session keying,
   concurrent-session non-interference, transcript-mtime-based liveness,
   the legacy-single-file migration path, and the WI-4534 guard's updated
   lookup.

## Risk / Reversibility

Per-session keying is additive and reversible — the legacy single-file
path can be retained as a transition fallback, then removed once the
guard's lookup is migrated. No bridge-protocol authority change. No
`bridge/INDEX.md` write surface. No KB schema change. The marker-wipe
investigation may surface a hook with legitimate single-file-wipe
semantics that need preservation; the follow-on implementation proposal
will surface and resolve that.

## Out of Scope (Advisory Bounds)

- Specific stale-marker sweeper interval, transcript-mtime threshold, or
  implementation-class fix details — those land in the follow-on
  implementation proposal.
- Changes to `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (the contract
  still holds), `GOV-SESSION-ROLE-AUTHORITY-001` (authority split
  preserved), or the WI-4534 guard's role-resolution semantics (only its
  lookup path changes).
- Dispatched-worker bootstrap context (separately captured as `WI-4545`);
  related but independent architectural concern.

## Recommended Commit Type

`docs:` — pure governance advisory; no source mutation, no test mutation,
no KB mutation; advisory body + INDEX entry only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
