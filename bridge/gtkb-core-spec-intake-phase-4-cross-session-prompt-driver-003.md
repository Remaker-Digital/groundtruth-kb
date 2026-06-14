NEW

# Implementation Report — GTKB-CORE-001 Phase 4: Cross-Session Core-Spec-Intake Prompt Driver

bridge_kind: implementation_report
Document: gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
Version: 003
Author: Claude Code Prime Builder (harness B)
author_identity: claude-code-prime-builder
author_harness_id: B
author_session_context_id: 1d33598a-6bc1-4317-b63e-bf2fbe22ce6b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
Date: 2026-06-14 UTC
Work Item: GTKB-CORE-001
Project: PROJECT-GTKB-CORE-001
Project Authorization: PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-4-CROSS-SESSION-PROMPT-DRIVER
Responds to: bridge/gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-002.md (GO)
Recommended commit type: feat
kb_mutation_in_scope: false

## Summary

Implemented the Phase 4 cross-session core-spec-intake prompt driver approved by the GO at
`-002`, within the four authorized target paths. On each adopter session start (and via a
doctor health check), the driver reconciles `MEMORY.md` to the current intake state:
re-emitting exactly one next-missing-slot question while any required slot is missing, and
clearing the pending block once every required slot is owner-stated or explicitly
not-applicable — deriving completion from persisted MemBase evidence, with explicit opt-out
and full backward compatibility with the Slice-1 prompt block.

## Specification Links

Carried forward from the GO'd proposal (`-001`):

- **SPEC-CORE-INTAKE-001** — prompt for missing core application specifications (re-emit the
  next missing slot during later startup or doctor-style health checks; exactly one question).
- **SPEC-CORE-INTAKE-002** — prompting stops at persisted completion; inferred candidates do
  not suppress; not-applicable counts as complete.
- **ADR-CORE-INTAKE-001** — completion derives from persisted MemBase evidence.
- **DCL-CORE-INTAKE-001** — non-interactive / automation-safe; explicit opt-out; scaffold
  backward compatibility.
- Cross-cutting: **GOV-FILE-BRIDGE-AUTHORITY-001**, **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**,
  **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001**, **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
- Advisory: **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**,
  **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001**.

## Prior Deliberations

- **DELIB-20263207** — owner authorization (AUQ "Authorize & build Phase 4").
- **DELIB-0875** — Phase 0 direction including the broader repeated prompt loop.
- **DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS** — prior owner batch authorization.
- `bridge/gtkb-core-spec-intake-default-008.md` (Slice 1 VERIFIED; scoped the driver OUT).
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-005.md` (Phase 3a CLI VERIFIED).

## Owner Decisions / Input

- **DELIB-20263207** (AskUserQuestion `AUQ-2026-06-13-CORE-001-PHASE4`, owner answer
  **"Authorize & build Phase 4"**) authorizes this implementation. The bounded
  `PAUTH-PROJECT-GTKB-CORE-001-CORE-001-PHASE-4-CROSS-SESSION-PROMPT-DRIVER` (active,
  expires 2026-06-27) covers WI GTKB-CORE-001 and the cited specs. No further owner decision
  was required to implement within this scope.

## Implementation

Four files (all within the GO's authorized target paths):

1. **`groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py`** — added:
   - `refresh_intake_prompt(db, project_id, memory_path, *, enabled=True) -> dict[str, str]`:
     the driver. Reads `next_question` (persisted MemBase evidence); reconciles `MEMORY.md`
     to contain exactly one delimited pending block for the next missing slot, or removes the
     block when complete. JSON-safe return; no interactive I/O; no `groundtruth.db` mutation.
   - Stable block delimiters `<!-- gtkb:core-spec-intake:start -->` / `:end`; `_strip_intake_block`
     removes the delimited block AND migrates the legacy un-delimited Slice-1 block (no duplication).
   - `intake_enabled(target)` — opt-out from env `GTKB_CORE_SPEC_INTAKE_OPT_OUT` or
     `groundtruth.toml [core_spec_intake] enabled=false`.
   - `is_enrolled` / `find_enrolled_project_id` — enrollment discovery for the hook/doctor.
2. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** — added `_check_core_spec_intake(target)`
   (read-only ToolCheck: `warning` + next missing slot when incomplete, `pass` when complete /
   not enrolled / opted out) and registered it in `run_doctor` after `_check_db_schema`.
3. **`groundtruth-kb/templates/hooks/session-start-governance.py`** — added the guarded,
   fail-safe `_refresh_core_spec_intake(cwd)` and a call in `main()`. Any resolution / import /
   I/O failure is a silent no-op (the hook never breaks an adopter session start).
4. **`groundtruth-kb/tests/test_core_spec_intake.py`** — 18 new spec-derived tests.

## Specification-Derived Verification

| Spec clause | Test(s) | Result |
|---|---|---|
| SPEC-CORE-INTAKE-001 — re-emit exactly one next question; idempotent | `test_refresh_emits_single_block_and_is_idempotent` | PASS |
| SPEC-CORE-INTAKE-001 — advance to next slot after completion | `test_refresh_advances_to_next_slot` | PASS |
| SPEC-CORE-INTAKE-001 — doctor-style health surface | `test_doctor_check_warns_when_incomplete`, `test_doctor_check_passes_when_complete` | PASS |
| SPEC-CORE-INTAKE-001 — adopter session-start re-emit wiring | `test_session_start_hook_refreshes_enrolled_project` | PASS |
| SPEC-CORE-INTAKE-002 — cease at completion | `test_refresh_ceases_at_completion` | PASS |
| SPEC-CORE-INTAKE-002 — not-applicable = complete | `test_refresh_not_applicable_counts_complete` | PASS |
| SPEC-CORE-INTAKE-002 — inferred does not suppress | `test_refresh_inferred_candidate_does_not_suppress` | PASS |
| ADR-CORE-INTAKE-001 — persisted MemBase evidence (fresh handle) | `test_refresh_uses_persisted_membase_evidence` | PASS |
| DCL-CORE-INTAKE-001 — opt-out (arg / env / toml) | `test_refresh_disabled_makes_no_write`, `test_intake_enabled_env_opt_out`, `test_intake_enabled_toml_opt_out` | PASS |
| DCL-CORE-INTAKE-001 — non-interactive / fail-safe hook | `test_session_start_hook_no_op_on_missing_db` | PASS |
| DCL-CORE-INTAKE-001 — backward compat (legacy block migration) | `test_refresh_migrates_legacy_block_without_duplication` | PASS |
| Enrollment discovery | `test_find_enrolled_project_id` | PASS |

### Commands executed and observed results

```text
python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests \
  --basetemp=E:/GT-KB/.tmp/pytest-ci-pb2 groundtruth-kb/tests/test_core_spec_intake.py -q
  -> 26 passed in 7.75s   (8 pre-existing + 18 new)

python -m ruff check <4 target files>
  -> All checks passed!

python -m ruff format --check <4 target files>
  -> 4 files already formatted

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
  -> preflight_passed: true; missing_required_specs: [];
     packet_hash: sha256:8cb15c5b72efdb4d6601b233ae921fa72f54b09b5852476f6863b5aeeb1b0f15

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-core-spec-intake-phase-4-cross-session-prompt-driver
  -> Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0; exit 0
```

Note on the in-root pytest temp: the default temp root is not writable in this sandbox
(`Access denied` on `.pytest-tmp`); a session-unique `--basetemp` under the probed-writable
`.tmp` directory was used. This is a known in-root pytest temp surface friction, not a defect.

## GO Conditions Addressed

1. **Session-start change limited to the adopter-facing template.** The only hook change is
   `groundtruth-kb/templates/hooks/session-start-governance.py` (the scaffold template copied
   to adopter projects). GT-KB's own SessionStart hooks under `.claude/hooks/` are untouched —
   no GT-KB SessionStart payload redesign. `test_session_start_hook_refreshes_enrolled_project`
   loads the template file directly and exercises the wiring against a temp scaffolded project.
2. **No canonical `groundtruth.db` mutation by the driver.** `refresh_intake_prompt` only READS
   MemBase (`next_question` / `is_complete`) and WRITES `MEMORY.md` (a file); `kb_mutation_in_scope: false`.
   Test setup uses `mark_slot_complete` against temporary fixture databases only — never the
   canonical MemBase.

## Recommended Commit Type

`feat` — net-new capability surface (cross-session driver, doctor check, adopter session-start
wiring) realizing SPEC-CORE-INTAKE-001/002 against the verified Phase 1–3 primitives.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/core_spec_intake.py` (driver + opt-out + enrollment helpers)
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (`_check_core_spec_intake` + registration)
- `groundtruth-kb/templates/hooks/session-start-governance.py` (guarded fail-safe wiring)
- `groundtruth-kb/tests/test_core_spec_intake.py` (+18 spec-derived tests)

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
