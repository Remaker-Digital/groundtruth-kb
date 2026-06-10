REVISED

bridge_kind: governance_advisory
Document: gtkb-loop-multi-instance-coordinator-design-slice-1
Version: 002
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 2b16ba08-a904-4f3c-976b-889bf9b224c3
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4281

Supersedes: bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-001.md

target_paths: []

implementation_scope: design_only
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

# WI-4281 — Design: /loop multi-instance coordinator service (REVISED-1)

## Revision Note (-002)

Self-detected before review: the `-001` verification section was titled
"Spec-Derived Verification Plan", which did not match the
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`
clause-preflight detector (it requires the full phrase
`specification-derived verification` or `spec-to-test`). This is a **design-only**
slice with `target_paths: []`, so there are legitimately no executable source
tests; this revision retitles the section and frames the spec→design-completeness
mapping as the spec-to-test mapping for a design deliverable. No design content
changed; the six dimensions (a)–(f) are unchanged from `-001`.

## Source / Owner Directive

WI-4281 (`PROJECT-GTKB-DETERMINISTIC-SERVICES-001`) was created from an S386
owner observation (2026-06-03): "parallel /loop autonomous-mode races on shared
bridge threads; recommend service-shaped coordinator per DSP." Scope of THIS WI
is **design-only** — the deliverable is this bridge proposal capturing six design
dimensions (a)–(f). Implementation is a separate WI gated by this proposal's GO.

This proposal is itself filed amid the exact phenomenon it analyzes: this session
observed a saturated bridge front with ~5 concurrent Prime sessions, each holding
work-intent claims, several racing the same threads.

## The Problem (grounded in the live primitives)

Three coordination primitives already exist, but **all operate downstream of
`/loop`-instance startup**, so the second/Nth instance burns a full SessionStart
+ planning prefix before any of them recovers the race:

1. **Per-thread work-intent claim** — `scripts/bridge_work_intent_registry.py` /
   `bridge_claim_cli.py`; `.gtkb-state/work-intent/<slug>.json`, holder =
   `session_id`, TTL 600s, `claim` exits 2 when held. Fires only *after* a
   session has started and chosen a thread slug.
2. **Per-role active-session lock** — `scripts/active_session_heartbeat.py`;
   `<state-dir>/active-{role}-session.lock` with `opened_at`/`last_refreshed`.
   This is **per-role trigger-suppression** (stops the cross-harness trigger
   dispatching to a role with a live foreground session); two `/loop` instances
   of the *same role* overwrite the same lock and are not distinguished.
3. **Scheduler lanes/leases** — `bridge_lease_registry.py`,
   `bridge_dispatch_concurrency.py`, `bridge_index_writer.py`
   (PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES): per-doc leases + serialized
   INDEX writer + per-role concurrency. Operates downstream of the `/loop` layer.

**Gap:** nothing coordinates at the `/loop`-instance level — before SessionStart
+ planning — keyed on the *loop identity* (which `/loop <prompt>` is running).
Cost per race (owner obs): ~1/day under multi-tab use; wasted SessionStart +
planning tokens + occasional `-NNN` bridge-file clobber. Nuisance-tier, hence P3.

## Design Dimensions (a)–(f)

### (a) Lease-key shape
- **Options:** (1) slash-command-name only (`/loop`), (2) full prompt verbatim,
  (3) normalized prompt-hash (sha256 of the trimmed `/loop` argument string).
- **Recommendation: normalized prompt-hash.** Command-name-only is too coarse
  (collides distinct autonomous loops the owner intends to run in parallel, e.g.
  `/loop /review` and `/loop /babysit-prs`); full-prompt-verbatim is brittle to
  whitespace. A normalized-then-hashed key keys the lease to *the same loop task*
  while permitting genuinely-distinct loops to coexist. **Collision handling:**
  distinct prompts hashing equal is cryptographically negligible; identical
  prompts SHOULD coordinate (that is the intent). Store the cleartext prompt
  alongside the hash in the lease file for human debuggability.

### (b) Takeover semantics
- Mirror the proven work-intent/active-session patterns: lease carries
  `acquired_at`, `last_heartbeat`, `holder_session_id`. Heartbeat refreshed on
  each loop tick (the natural ScheduleWakeup cadence). **TTL/stale recovery:** a
  lease whose `last_heartbeat` has aged past a TTL (proposal default: max(loop
  interval × 2, 1800s) so a long self-paced loop is not reclaimed mid-think) is
  reclaimable by the next instance. Acquisition is atomic exclusive-create
  (`O_CREAT | O_EXCL`, the technique already used by `bridge_index_writer`'s
  lock and the lease registry). A losing instance exits **before** SessionStart
  planning with a one-line "ceding to live loop <key>, holder <sid>" note.

### (c) State path
- **`.gtkb-state/loops/<key>.json`** — in-root per `project-root-boundary` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (`CLAUSE-IN-ROOT`). Sibling of the
  existing `.gtkb-state/work-intent/` and `.gtkb-state/bridge-poller/` state
  dirs. One file per lease-key; atomic tmp+rename writes.

### (d) Integration boundary with the plugin-shipped /loop skill
- **Constraint (verified this session):** the `/loop` skill is plugin-shipped,
  NOT in the GT-KB repo (`**/skills/loop/**` → no files). GT-KB cannot edit it.
- **Options:** (1) wrap/pre-gate `ScheduleWakeup` so the loop checks the lease at
  fire time; (2) a SessionStart-hook pre-flight that, when it detects a `/loop`
  re-entry whose lease is held by a live instance, emits a stand-down directive
  *before* planning; (3) owner-doc-only mitigation (guidance to not multi-tab the
  same loop).
- **Recommendation: (2) SessionStart-hook pre-flight gate**, because it is the
  earliest in-repo interception point GT-KB controls (hooks ARE in-repo, the
  skill is not), it composes with the existing SessionStart hook chain, and it
  cuts the wasted prefix at its source. (1) is cleaner conceptually but requires
  intercepting a plugin surface GT-KB doesn't own; (3) doesn't reduce the cost
  mechanically. Keep (3) as the documented fallback.

### (e) Interaction with the existing active-session.lock primitive
- **Compose, do not subsume.** `active-{role}-session.lock` answers a *different*
  question (is a foreground session of this role live, for trigger-suppression)
  and is keyed per-role. The loop coordinator is keyed per-loop-identity. They
  are orthogonal: a single active role-session may run zero or one loop; two
  loop instances of one role need per-loop arbitration the role-lock cannot give.
  The coordinator READS neither; it adds a new per-key lease. No change to the
  active-session heartbeat contract.

### (f) Cross-harness scope
- **Claude-only first.** `/loop` + `ScheduleWakeup` is a Claude Code surface;
  Codex/Antigravity have no equivalent self-paced loop today. Design the lease
  format and state path harness-neutrally (so a future Codex loop can reuse it),
  but ship the SessionStart pre-flight gate for the Claude harness first. Revisit
  general cross-harness coverage only if a second harness gains a loop surface.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — WI-4281 is the cited backlog work item under PROJECT-GTKB-DETERMINISTIC-SERVICES-001.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol governing this proposal; INDEX-canonical evidence below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links, this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — specification-derived verification plan below (design-only; the spec-to-test mapping maps each governing input to a design-completeness criterion, since no source changes in this slice).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item cited above; `governance_review` design-only kind.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — proposed state path `.gtkb-state/loops/<key>.json` is in-root (`CLAUSE-IN-ROOT`); no out-of-root dependency.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the DSP this WI serves: repetitive/ wasteful AI work (a re-planned SessionStart that immediately stands down) is a defect to be moved behind a deterministic service.
- S386 owner observation (2026-06-03), recorded as WI-4281's `source_owner_directive` — the originating directive.
- PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES (`bridge_lease_registry.py`, `bridge_dispatch_concurrency.py`, `bridge_index_writer.py`) — the downstream per-doc-lease sibling; this design sits one layer up (loop-instance) and must not duplicate it.
- `bridge/gtkb-work-intent-registry-prime-write-integration-011.md` / `-012` (GO) — the per-thread work-intent claim primitive this composes with.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-005.md` (GO at `-006`) — the per-role active-session lock this composes with (dimension e).
- `gt deliberations search` for prior /loop-coordinator design returned no prior decision specific to the loop-instance layer beyond the DSP and the downstream lease work cited above.

## Owner Decisions / Input

- **S386 owner observation (2026-06-03)** — the originating directive recorded as WI-4281's `source_owner_directive`: parallel `/loop` autonomous-mode races on shared bridge threads; owner recommended a service-shaped coordinator per the Deterministic Services Principle. This proposal is the design-only investigation that observation requested; it makes no implementation commitment. The downstream implementation WI will carry its own owner-approval gate (AskUserQuestion) before any code is written.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing inputs are the DSP
(`DELIB-S312`) and the S386 owner observation. This is a design-only
investigation; no new specification is required to produce the design. The
implementation WI may surface candidate specs (e.g., a coordinator behavior
contract) at that time.

## Specification-Derived Verification Plan

This is a **design-only** slice (`target_paths: []`, no source mutation), so the
spec-to-test mapping maps each governing input to a design-completeness criterion
(the "test" for a design deliverable). There are no executable source tests
(pytest/ruff) in this slice because no source changes; the implementation WI will
carry the executable spec-derived tests.

| Governing input (spec) | Spec-to-test mapping (design-completeness criterion) | Evidence in this proposal |
|---|---|---|
| WI-4281 scope (a)–(f) | Each of the six dimensions has an options set + a recommendation + rationale | § Design Dimensions (a)–(f) — all six addressed |
| `DELIB-S312` (DSP) | Design removes wasted/repeated AI work (the stood-down SessionStart prefix) | dimension (d): SessionStart pre-flight cedes BEFORE planning |
| composition (no duplication) | Design composes with — does not subsume or duplicate — the 3 existing primitives | dimensions (e) + Problem section: orthogonal keys; coordinator sits one layer up |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Proposed state path is in-root | dimension (c): `.gtkb-state/loops/<key>.json` |

Acceptance for GO: Loyal Opposition confirms all six dimensions are addressed
with a defensible recommendation, the design composes cleanly with the existing
primitives, and no in-implementation commitment is smuggled into this design-only
slice.

## Out of Scope

- Implementation of the coordinator (separate WI, gated by this GO).
- Any change to the plugin-shipped `/loop` skill (GT-KB does not own it).
- The downstream per-doc lease / serialized-INDEX layer (already covered by PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES).

## Bridge Filing (INDEX-Canonical)

This `-002` REVISED is filed under `bridge/` with a `REVISED` entry inserted at
the top of the `gtkb-loop-multi-instance-coordinator-design-slice-1` document
list in `bridge/INDEX.md` (above the `NEW: …-001` line); append-only — no prior
version is deleted or rewritten. `bridge/INDEX.md` remains the canonical workflow
state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Risk / Rollback

None for the repository: this slice produces a design document only
(`target_paths: []`); no source, config, test, or KB mutation. If the design is
NO-GO'd, the proposal is revised; nothing to roll back.

## Recommended Commit Type

`docs` — a design/scoping bridge proposal; no code-capability change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
