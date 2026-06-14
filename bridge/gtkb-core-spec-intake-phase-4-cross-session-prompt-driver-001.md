NEW

# Implementation Proposal — GTKB-CORE-001 Phase 4: Cross-Session Core-Spec-Intake Prompt Driver

bridge_kind: prime_proposal
Document: gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
Version: 001
Author: Claude Code Prime Builder (harness B)
author_identity: claude-code-prime-builder
author_harness_id: B
author_session_context_id: 1d33598a-6bc1-4317-b63e-bf2fbe22ce6b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
Date: 2026-06-13 UTC
Work Item: GTKB-CORE-001
Project: PROJECT-GTKB-CORE-001
Project Authorization: PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-4-CROSS-SESSION-PROMPT-DRIVER
Recommended commit type: feat
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/templates/hooks/session-start-governance.py", "groundtruth-kb/tests/test_core_spec_intake.py"]
kb_mutation_in_scope: false

> **KB-mutation scope:** The production driver READS MemBase (`is_complete`, `next_question`)
> and writes only `MEMORY.md` (a file); it performs **no** canonical `groundtruth.db` mutation,
> so `groundtruth.db` is intentionally excluded from `target_paths`. The verification tests use
> the existing `mark_slot_complete` primitive against a **temporary** project fixture db (never
> the canonical MemBase) for setup only.

## Summary

Implement Phase 4 of GTKB-CORE-001 (TOP-priority, owner-directed 2026-04-22): the
**cross-session core-spec-intake prompt driver**. Slice 1
(`gtkb-core-spec-intake-default`, VERIFIED) delivered default enrollment, the
one-time initial `MEMORY.md` prompt at scaffold time, opt-out threading, and the
MemBase slot/completion primitives. Phase 3 (`gtkb-core-spec-intake-current-root-phase3a-cli`,
VERIFIED) delivered the read-only `gt core-specs status` surface. The genuine remaining
gap — confirmed unimplemented in code — is the **repeat-until-complete driver**: nothing
re-emits the next missing core-spec question on *later* session starts, and nothing
ceases prompting once the slots are complete.

This proposal adds a deterministic driver that, on each adopter session start (and via a
doctor health check), reconciles `MEMORY.md` to the current intake state — re-emitting
exactly one next-missing-slot question while any required slot is missing, and clearing
the pending block once every required slot is owner-stated or explicitly not-applicable —
using persisted MemBase evidence, with an explicit opt-out and full backward compatibility.

## Specification Links

Feature requirements (this work satisfies these; status `specified` → `implemented`):
- **SPEC-CORE-INTAKE-001** — "GT-KB Prompts For Missing Core Application Specifications":
  after init and **during later startup or doctor-style health checks**, identify the next
  missing slot and present **exactly one** deterministic question.
- **SPEC-CORE-INTAKE-002** — "Core Specification Prompting Stops At Persisted Completion":
  continue while any required slot is missing/inferred/needs-clarity; **stop** once every
  required slot is owner-stated or explicitly not-applicable; inferred candidates must not
  suppress prompting until owner-confirmed; not-applicable counts as complete.
- **ADR-CORE-INTAKE-001** — "Core Spec Completion Uses Persisted MemBase Evidence":
  completion is derived from persisted MemBase evidence, not conversation memory or a
  transient session flag; prefer stable slot handles over fuzzy title matching.
- **DCL-CORE-INTAKE-001** — "Core Intake Preserves Scaffold And Automation Compatibility":
  non-interactive / JSON-safe paths must not emit interactive prompts; explicit opt-out
  required; existing minimal/full scaffold behavior stays backward-compatible.

Cross-cutting governance (path/content-triggered):
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` is canonical; this thread adds a new
  versioned entry without rewriting prior versions.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal cites all relevant
  specs and maps tests to them (below).
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the post-implementation report will
  carry the spec-to-test mapping and executed-test evidence below.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all touched paths are in-root under
  `E:\GT-KB\groundtruth-kb\`; the session-start wiring targets the adopter-facing scaffold
  template (`groundtruth-kb/templates/hooks/`), not GT-KB's own SessionStart payload.

Advisory (artifact-oriented governance; content-triggered, non-blocking):
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**,
  **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** — this slice is captured as durable artifacts
  (owner-decision DELIB-20263207, PAUTH, bridge thread, spec-derived tests) rather than
  transient session work, consistent with the artifact-oriented governance posture.

## Prior Deliberations

- **DELIB-20263207** — owner AskUserQuestion decision (2026-06-13) authorizing this Phase 4
  build ("Authorize & build Phase 4"); source of the PAUTH cited above.
- **DELIB-0875** — Phase 0 owner direction: default enrollment, explicit opt-out, persisted
  stop conditions, **and the broader repeated prompt loop** (this slice implements that loop).
- **DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS** — prior owner batch authorization
  including GTKB-CORE-001 (cited by the Slice 1 VERIFIED verdict).
- **bridge/gtkb-core-spec-intake-default-008.md** (VERIFIED) — Slice 1; explicitly scoped the
  cross-session prompt driver OUT of Slice 1 ("The cross-session prompt driver and
  pre-existing-project enable command remain out of scope").
- **bridge/gtkb-core-spec-intake-current-root-phase3a-cli-005.md** (VERIFIED) — Phase 3a CLI
  (`gt core-specs status` read surface).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`
  — Phase 4 ("Project Init, Doctor, And Session Startup Integration"): "Session startup repeats
  the next missing question" / "Startup stops repeating once all slots are complete."

## Owner Decisions / Input

This work depends on owner approval, satisfied by:

- **DELIB-20263207** (AskUserQuestion `AUQ-2026-06-13-CORE-001-PHASE4`, owner answer:
  **"Authorize & build Phase 4"**) — authorizes capturing the decision, creating the PAUTH,
  filing this proposal, and driving it through the bridge to implementation + verification.
- The bounded authorization is recorded as
  `PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-4-CROSS-SESSION-PROMPT-DRIVER` (active; includes
  WI GTKB-CORE-001 and specs SPEC-CORE-INTAKE-001/002, ADR-CORE-INTAKE-001, DCL-CORE-INTAKE-001;
  expires 2026-06-27). No further owner decision is required to implement within this scope.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-CORE-INTAKE-001 and SPEC-CORE-INTAKE-002 fully
specify the repeat-until-complete and cessation behavior; ADR-CORE-INTAKE-001 fixes the
completion-evidence source; DCL-CORE-INTAKE-001 fixes the compatibility/opt-out constraints.
No new or revised requirement is needed before implementation; this slice wires the already-
specified behavior to the already-built primitives.

## Current State (evidence)

- `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` provides the primitives:
  `slot_names`, `next_missing_slot`, `next_question`, `slot_statuses`, `is_complete`,
  `mark_slot_complete`, `enroll_project_for_intake`, `render_initial_prompt`,
  `append_initial_prompt`.
- The **only** runtime wiring is `scaffold.py:453` — `append_initial_prompt(target / "MEMORY.md", first_missing)`
  at `gt project init` time (one-time, initial slot only).
- `groundtruth-kb/templates/hooks/session-start-governance.py` reads only `bridge/INDEX.md`;
  it does **not** call any intake primitive.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` has **no** core-spec-intake completion
  check (the `intake` matches there are the unrelated `intake-classifier.py` hook check and the
  `_check_spec_intake_skill_present` skill-presence check).
- `gt core-specs status` (cli.py) reports completion state read-only but does not drive
  re-prompting across sessions.

## Proposed Design

### 1. Driver function (`core_spec_intake.py`)

`refresh_intake_prompt(db, project_id, memory_path, *, enabled=True) -> dict[str, str]`:

- If `enabled` is False → return `{"status": "disabled"}` with **no file I/O** (DCL-CORE-INTAKE-001 opt-out).
- `nxt = next_question(db, project_id)` (completion + next-slot derive from persisted MemBase
  evidence — ADR-CORE-INTAKE-001; inferred-but-unconfirmed candidates are not counted complete,
  so they do not suppress — SPEC-CORE-INTAKE-002).
- If `nxt is None` → remove the pending intake block from `MEMORY.md` if present; return
  `{"status": "complete"}` (SPEC-CORE-INTAKE-002 cessation).
- Else → reconcile `MEMORY.md` so it contains **exactly one** pending intake block for
  `nxt["name"]`, replacing any stale block; return `{"status": "prompted", "slot": nxt["name"]}`
  (SPEC-CORE-INTAKE-001 exactly-one-question).
- The pending block uses stable delimiters
  (`<!-- gtkb:core-spec-intake:start -->` … `<!-- gtkb:core-spec-intake:end -->`) for idempotent
  find/replace/remove. The Slice-1 `render_initial_prompt` text is wrapped/migrated into the
  delimited form on first refresh so there is no duplication (DCL-CORE-INTAKE-001 backward compat).
- Pure file + MemBase operations; returns a JSON-safe dict; never reads stdin / never blocks
  (DCL-CORE-INTAKE-001 non-interactive).

### 2. Opt-out resolution

A small helper `intake_enabled(target) -> bool` resolves opt-out from (a) env
`GTKB_CORE_SPEC_INTAKE_OPT_OUT=1` and (b) `groundtruth.toml` `[core_spec_intake] enabled=false`
if present; default enabled. Callers (hook, doctor) pass the result as `enabled=`.

### 3. Session-start wiring (`templates/hooks/session-start-governance.py`)

Add a guarded, **fail-safe** block to the adopter-facing scaffold template hook: when a local
`groundtruth.db` + an enrolled project + `MEMORY.md` are resolvable and opt-out is not set,
call `refresh_intake_prompt`. Any resolution failure or exception → silent no-op (the hook must
never break an adopter's session start). This is the "later startup repeats the question" surface
(SPEC-CORE-INTAKE-001). It modifies only the scaffold **template** (adopter-facing); it does not
touch GT-KB's own SessionStart payload (PAUTH forbid-line; ADR-ISOLATION-APPLICATION-PLACEMENT-001).

### 4. Doctor check (`doctor.py`)

`_check_core_spec_intake(target) -> ToolCheck` — read-only; resolves the project and returns
`pass` when complete (or no enrolled project / opted-out) and `warning` with the next missing slot
label when incomplete. This is the "doctor-style health checks" surface (SPEC-CORE-INTAKE-001),
registered alongside the existing `_check_*` functions.

## Specification-Derived Verification

New/updated tests in `groundtruth-kb/tests/test_core_spec_intake.py`, executed with the project
venv against a temp project fixture:

| Spec clause | Test |
|---|---|
| SPEC-CORE-INTAKE-001 — re-emit exactly one next question on later startup | driver on an incomplete enrolled project writes exactly one delimited pending block for `next_missing_slot`; a second call is idempotent (no duplicate block) |
| SPEC-CORE-INTAKE-001 — advances to the next slot | after `mark_slot_complete` of the current slot, the next driver call re-emits the *next* missing slot's block |
| SPEC-CORE-INTAKE-001 — doctor health surface | `_check_core_spec_intake` returns `warning` + the missing slot label when incomplete, `pass` when complete |
| SPEC-CORE-INTAKE-002 — cease at completion | driver on a fully-complete project removes the pending block and returns `{"status": "complete"}` |
| SPEC-CORE-INTAKE-002 — not-applicable = complete | a slot explicitly marked not-applicable is treated as complete (no re-prompt) |
| SPEC-CORE-INTAKE-002 — inferred does not suppress | an inferred (not owner-confirmed) candidate still yields a prompt for that slot |
| ADR-CORE-INTAKE-001 — persisted evidence | completion/next-slot derive from MemBase rows; a fresh `KnowledgeDB` handle (no session state) yields the same result |
| DCL-CORE-INTAKE-001 — opt-out | `enabled=False` (and env opt-out) → no file write, `{"status": "disabled"}` |
| DCL-CORE-INTAKE-001 — non-interactive / fail-safe | driver returns a dict and never blocks; the session-start hook no-ops (no exception) when `groundtruth.db` is absent |
| DCL-CORE-INTAKE-001 — backward compat | a `MEMORY.md` containing the Slice-1 initial-prompt text is migrated into the delimited block without duplication; minimal/full scaffold output unchanged |

Pre-file gates to run on changed Python (reported in the implementation report):
`ruff check` and `ruff format --check` on the four target files; the focused
`test_core_spec_intake.py` suite; `bridge_applicability_preflight.py` and
`adr_dcl_clause_preflight.py` for this bridge id.

## Risk and Rollback

- **Risk:** the session-start hook runs in every adopter session — a crash would break adopter
  startup. **Mitigation:** the wiring is fully guarded (resolution failure / any exception → silent
  no-op); a dedicated test asserts no-op on missing db. **Rollback:** the change is additive across
  four files; reverting the four diffs fully restores prior behavior. No schema or data migration.
- **Risk:** stale Slice-1 prompt-block format. **Mitigation:** one-time in-place migration to the
  delimited form, covered by a backward-compat test.
- **Risk:** scope creep into GT-KB's own SessionStart. **Mitigation:** only the adopter-facing
  scaffold template is touched (PAUTH forbid-line; ADR-ISOLATION-APPLICATION-PLACEMENT-001).

## Recommended Commit Type

`feat` — net-new capability surface (cross-session driver, doctor check, hook wiring) realizing
SPEC-CORE-INTAKE-001/002.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
