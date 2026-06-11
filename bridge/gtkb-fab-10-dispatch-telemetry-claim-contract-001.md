NEW

bridge_kind: prime_proposal
Document: gtkb-fab-10-dispatch-telemetry-claim-contract
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4422
Project Authorization: PAUTH-FAB10-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 07ef97df-2cb3-45a4-9c32-be60d702f29c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-compliance-gate.py", ".codex/hooks.json", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/**"]

No KB mutation: all changes are source/config/doctor; no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-10 — Dispatch telemetry + claim contract + INDEX write perimeter

WI-4422 (FAB-10) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-005, HYG-006, HYG-007, HYG-039.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`. Coupled to FAB-01.

## Summary

The dispatch substrate's reliability + measurement layer:

- **HYG-005:** the trigger claims work-intent under a 120 s TTL + a holder-id the spawned worker
  can't renew (CLI default 600 s) → duplicate workers + **1,593 contention records / 2 h** (wasted sessions).
- **HYG-006:** role-suffixed dispatch ids contain `:` → worker logs land in invisible NTFS
  alternate-data-streams; AND the worker-outcome telemetry is a **daemon thread that dies at the
  ~1 s process exit** → 0 records after 1,041 launches; dispatch economics are unmeasurable.
- **HYG-007:** the retry/circuit-breaker uses `OLLAMA_*` knobs for all harnesses and **can never
  auto-reset** once tripped → permanent silent shutdown (both LO recipients 2 failures away).
- **HYG-039:** `bridge/INDEX.md` (canonical workflow state, parsed by both dispatch substrates) has
  **no enforced write path** — the compliance gate exempts it; a gate-bypassing writer corrupted it
  on 2026-06-10 (malformed append, hand-repaired).

HYG-006's telemetry revival is the measurement foundation the orchestrator
(`DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610`) needs to route by efficacy/cost.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge INDEX-as-canonical authority (HYG-039 core).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4422 is the governed backlog authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the INDEX well-formedness lint adds a `.codex/hooks.json`
  adapter so the validation fires on the Codex harness too.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` — the cross-harness trigger's dispatch contract (claim/breaker/telemetry).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — FAB-10 edits in-root scripts/hooks/config + the in-root
  doctor module; it writes **no** out-of-root artifacts (this bridge file is under `E:\GT-KB\bridge\`)
  and relocates nothing. No application-placement change.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-005/006/007/039).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB10-REMEDIATION-20260610` — this cluster's owner-decision set.
- `DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610` — the orchestrator measurement layer HYG-006 enables.
- _FAB-01 (`gtkb-fab-01-dispatch-substrate-revival`) is the coupled launchability/event-source cluster;
  FAB-01 lands first per the advisory sequencing._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB10-REMEDIATION-20260610`:

1. **HYG-005 = Bare-id claim + 600 s TTL + dedup logging** — claim under the bare dispatch_id the child
   resolves (worker IS the holder) + raise the trigger TTL to ≥600 s + suppress repeat held-thread
   logging per holder+slug + align the role-asymmetric signature update.
2. **HYG-006 = Sanitize ':' + revive telemetry** — replace `:` with a filesystem-safe separator in
   dispatch-id filenames + fix the worker-outcome poll so it records (not a daemon thread killed at exit).
3. **HYG-007 = Half-open + neutral knobs + doctor WARN** — timed half-open probe + `GTKB_DISPATCH_*`
   knobs (back-compat read) + doctor WARN on tripped state.
4. **HYG-039 = Lint now + helper-only follow-on** — INDEX well-formedness lint (compliance-gate + Codex
   adapter + doctor parse check) now; helper-only CAS writes for all harnesses as a follow-on slice.

## Requirement Sufficiency

**Existing requirements sufficient.** Governed by `GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-SMART-POLLER-AUTO-TRIGGER-001`, and `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; the dispositions are fixed
by `DELIB-FAB10-REMEDIATION-20260610`. No new requirement needed.

## Scope and Boundaries

In scope: the four fixes above (claim contract, telemetry, breaker, INDEX lint). Out of scope: the
helper-only-INDEX-writes migration (follow-on slice); the FAB-01 launchability/event-source design; the
orchestrator routing engine (captured separately). Optional cleanup: repair the grandfathered
non-canonical first line of `gtkb-architecture-governance-hygiene-investigation-001.md`.

## Proposed Implementation

1. **HYG-005:** `cross_harness_bridge_trigger.py` — export the prefixed holder id to the child (or claim
   under the bare dispatch_id); raise `WORK_INTENT_TRIGGER_TTL_SECONDS` to ≥600; dedup held-thread logging
   per holder+slug; align Prime/LO `last_dispatched_signature` update timing.
2. **HYG-006:** sanitize `:` → `-` in `_new_dispatch_id`/filename uses; re-architect `_post_dispatch_poll`
   so the verdict poll survives process exit (e.g., a detached subprocess or a Stop-hook-driven record)
   and writes `dispatch-diagnostic-post.jsonl`.
3. **HYG-007:** add a timed half-open probe to the breaker; rename knobs to `GTKB_DISPATCH_*` (read old
   names for back-compat); add a doctor WARN when any recipient is tripped.
4. **HYG-039:** extend `bridge-compliance-gate.py` (+ the `.codex/hooks.json` adapter) to validate INDEX
   well-formedness on any Write/Edit touching it (parseable `Document:` blocks, top-insertion, no literal
   escape sequences) instead of blanket-exempting it; add a `doctor.py` check that parses INDEX with the
   canonical detector and FAILs on parse errors.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` (claim contract) | test: the spawned worker resolves the same id as the claim holder; TTL ≥600 s; held-thread log emitted once per state change |
| HYG-006 telemetry | test: generated artifact paths contain no `:` (visible files); a dispatch produces a `dispatch-diagnostic-post.jsonl` record |
| HYG-007 breaker | test: a tripped breaker allows a probe launch after the half-open timeout and resets on exit-0; doctor WARNs on tripped |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX integrity) | test: the lint FAILs on a malformed INDEX entry (literal `\n`, non-top-insertion); the doctor INDEX-parse check FAILs on a corrupt INDEX |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check`/`format --check` |

## Acceptance Criteria

1. The trigger claim makes the worker the holder; TTL ≥600 s; no duplicate-worker contention flood.
2. Dispatch-id filenames are ordinary visible files; worker-outcome telemetry records to `dispatch-diagnostic-post.jsonl`.
3. The breaker is half-open-recoverable with `GTKB_DISPATCH_*` knobs; a doctor WARN surfaces a tripped state.
4. The INDEX well-formedness lint (gate + Codex adapter + doctor check) FAILs on malformed INDEX; tests pass; ruff-clean.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md` with a matching `NEW` entry at the
top of `bridge/INDEX.md`; append-only, no prior bridge version deleted or rewritten. FAB-10 **strengthens**
`bridge/INDEX.md` as canonical workflow state — the HYG-039 lint adds protection that was missing, and the
HYG-005/006/007 fixes harden the dispatch substrate that consumes the INDEX. `GOV-FILE-BRIDGE-AUTHORITY-001`
is reinforced, not weakened.

## Risk and Rollback

- **Risk:** the INDEX lint could block a legitimate protocol edit → it validates well-formedness, not
  content, and preserves the existing protocol-edit exemption; tests cover legitimate top-insertions.
- **Risk:** the telemetry re-architecture changes process lifecycle → covered by a record-produced test;
  the detached recorder is fire-and-forget like the existing dispatch audit log.
- **Rollback:** revert the trigger/gate/doctor edits; no MemBase mutation; INDEX integrity reverts to the
  manual-repair convention.

## Recommended Implementation Routing

**Opus/Codex-supervised** — the dispatch trigger + the bridge-compliance-gate are load-bearing safety
surfaces; not a cheap-model candidate. Coordinate with FAB-01 (shared trigger file).

## Recommended Commit Type

`fix:` — repairs the claim contract, dead telemetry, fail-dead breaker, and unguarded INDEX write path
(with `feat:`-class INDEX lint + telemetry recorder).
