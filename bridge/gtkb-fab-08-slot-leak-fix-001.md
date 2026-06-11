NEW

bridge_kind: prime_proposal
Document: gtkb-fab-08-slot-leak-fix
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4420
Project Authorization: PAUTH-FAB08-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 07ef97df-2cb3-45a4-9c32-be60d702f29c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb; body drafted by local Ollama qwen3.6, finalized by Opus

target_paths: ["groundtruth-kb/tests/adopter/conftest.py", "groundtruth-kb/tests/test_scaffold_isolation.py", "groundtruth-kb/tests/test_cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "applications/_test_*/**", "platform_tests/scripts/**"]

No KB mutation: the purge is a file deletion of leaked test skeletons; the doctor auto-prune is code. No `groundtruth.db` mutation; it is intentionally NOT in target_paths.

Drafting provenance: the body sections (Summary, Scope, Proposed Implementation, Verification, Acceptance, Risk) were drafted by the local Ollama `qwen3.6` model (the validated cheap-drafting pipeline) and finalized by Opus, which added the gate metadata + the Specification Links / Prior Deliberations / Owner Decisions / Requirement Sufficiency sections and ran the preflights. First production use of the cost-saving loop.

---

# FAB-08 — Fix the applications/_test_* slot leak (Windows rmtree root cause)

WI-4420 (FAB-08) of PROJECT-FABLE-INVESTIGATION. Finding: HYG-053. (HYG-022 — Agent_Red
`application.toml` backfill — goes to a separate Agent-Red-scoped bridge per the owner decision.)
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4420 is the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the purge removes **leaked test skeletons**
  under `applications/` (a test-fixture defect), relocating **no** real application and
  writing **no** out-of-root artifacts (this bridge file is under `E:\GT-KB\bridge\`). The
  fix restores the application-slot contract's signal-to-noise; no placement change.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-053/022).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB08-REMEDIATION-20260610` — this cluster's owner-decision set (fix+purge+auto-clean;
  Agent_Red registration deferred to a separate AR bridge).
- _No prior bridge thread covers the slot leak or the rmtree defect._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB08-REMEDIATION-20260610`:

1. **HYG-053 = Fix + purge + doctor auto-clean** — `_force_rmtree` onexc helper + one-time purge of
   the 229 skeletons + a doctor WARN/auto-prune for stale `_test_*` slots >24h. (Rejected:
   fix+purge-only; purge-only.)
2. **HYG-022 = Backfill via a separate Agent-Red bridge** — the Agent_Red `application.toml` backfill
   is NOT in FAB-08; it is a separate Agent-Red-scoped thread after this purge clears the noise.

## Requirement Sufficiency

**Existing requirements sufficient.** The fix restores the application-slot registration contract's
truthfulness (no new requirement); the disposition is fixed by `DELIB-FAB08-REMEDIATION-20260610`.

## Summary

Resolve 229 leaked `applications/_test_*` sandbox skeletons caused by silent failures in
`shutil.rmtree` on Windows read-only `.git` trees. The current cleanup in the clean-adopter pytest
fixtures leaves stale directories that trigger a persistent P0 + ~230 P1s in every doctor run,
obscuring genuine findings, and the leak is active (newest 2026-06-09). This implements a robust
cross-platform removal helper, purges the existing leaks, and adds automated pruning for future
stale slots.

## Scope and Boundaries

In scope: the `_force_rmtree` helper reused across the 4 fixture sites; the one-time purge of the 229
skeletons; the doctor auto-prune for stale `_test_*` slots >24h. Out of scope: the Agent_Red
`application.toml` backfill (HYG-022 → separate AR bridge) and the larger absorbed Agent_Red debt
(~925 MB regenerable `node_modules` on the Drive-synced volume; no repo-correspondence marker).

## Proposed Implementation

1. **`_force_rmtree` helper:** add a shared utility in `groundtruth-kb/tests/adopter/conftest.py`. On
   Windows, intercept `onexc` errors during `shutil.rmtree`, apply `os.chmod(path, stat.S_IWRITE)` to
   the read-only `.git` object files, and retry the removal.
2. **Refactor the fixtures:** replace `shutil.rmtree(sandbox, ignore_errors=True)` at the 4 fixture
   sites (`conftest.py:90-92`, `test_scaffold_isolation.py`, `test_cli.py`) with calls to `_force_rmtree`.
3. **One-time purge:** remove all 229 existing `applications/_test_*` skeletons (supervised).
4. **Doctor auto-prune:** add logic to `doctor.py` to detect `_test_*` slots older than 24 h, emit a
   WARN, and auto-prune them on the next doctor run.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| HYG-053 root cause | `pytest` on Windows verifies `_force_rmtree` removes a read-only `.git` tree without silent failure; no `_test_*` directory remains in `applications/` after a fixture run |
| application-slot contract | the doctor no longer emits the slot-leak P0/~230 P1s on a clean state |
| doctor auto-prune | a synthetic stale `_test_*` slot (>24 h) is detected, WARNed, and pruned by the doctor |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check`/`format --check` on the changed `.py` |

## Acceptance Criteria

1. All 229 existing `applications/_test_*` skeletons are removed; the live `applications/` holds only real slots.
2. `_force_rmtree` is implemented and used at all 4 fixture sites; Windows read-only `.git` cleanup works.
3. The doctor no longer reports the HYG-053 P0/P1 spam; it auto-prunes stale `_test_*` slots >24 h with a WARN.
4. Tests pass; ruff-clean.

## Risk and Rollback

- **Risk:** low — the change is isolated to test fixtures + the doctor; the one-time purge affects only
  gitignored test artifacts, not production code.
- **Rollback:** revert the fixture/doctor edits restoring the prior `shutil.rmtree(...)`; the purge is of
  regenerable test skeletons (no restore needed). No MemBase mutation to undo.

## Recommended Implementation Routing

**Cheap-model candidate (supervised):** the `_force_rmtree` helper + fixture refactor + purge are
mechanical; the doctor auto-prune touches the project module so Claude/Codex reviews that edit. This
cluster is a natural fit for the tiered local→cheap implementation routing once GO'd.

## Recommended Commit Type

`fix:` — corrects the Windows rmtree slot-leak defect (with a small `feat:`-class doctor auto-prune).
