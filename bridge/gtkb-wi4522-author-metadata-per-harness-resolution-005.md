NEW

bridge_kind: implementation_report
Document: gtkb-wi4522-author-metadata-per-harness-resolution
Version: 005
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T15-26-14Z-prime-builder-B-27f08e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: headless bridge auto-dispatch worker; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4522
target_paths: ["scripts/bridge_author_metadata.py", "platform_tests/scripts/test_bridge_author_metadata.py"]
implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:
Responds to: bridge/gtkb-wi4522-author-metadata-per-harness-resolution-004.md (GO)

# WI-4522 Implementation Report: per-harness author-metadata resolution at filing time (current.json baseline removed)

## Summary

Implemented the GO'd REVISED-2 design (`-003`, GO at `-004`) exactly. `load_author_metadata`
no longer reads the shared mutable `.gtkb-state/bridge-author-metadata/current.json`
baseline. It now composes author metadata from two correctly-scoped sources:

- the **two durable fields** (`author_identity`, `author_harness_id`) resolved per
  call from the harness registry projection at the filing harness's `project_root`;
- the **four per-session runtime fields** sourced ONLY from the filing harness's own
  runtime envelope (env) or explicit values.

When the runtime envelope is absent, `validate_author_metadata` raises and the helper
**fails closed** rather than inheriting another harness's cached `current.json` values —
the provenance-safe answer to the S389 concurrent-harness wrong-stamp incident
(`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`). The `ensure_author_metadata` short-circuit for
self-authored headers is untouched, so interactive and self-authoring sessions are
unaffected (this report itself was filed by a headless worker via that short-circuit).

Implementation start was authorized by packet
`sha256:6782c29b1f1251383745efe8c0dc12a4b8d4e5b6883854551cf1ce58384cbdf4`
(`implementation_authorization.py begin`, derived from live GO `-004`), scoped to the
two declared `target_paths`.

## Files Changed (diff stat)

```text
 platform_tests/scripts/test_bridge_author_metadata.py | 186 +++++++++++++++++++--
 scripts/bridge_author_metadata.py                     | 114 ++++++++++++-
 2 files changed, 278 insertions(+), 22 deletions(-)
```

Both files are in-root under `E:\GT-KB` (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`).

## Required Implementation Evidence (per GO `-004`)

### 1. `load_author_metadata` no longer reads `AUTHOR_METADATA_RELATIVE_PATH` / `current.json`

The loader's baseline line (previously
`merged.update(normalize_author_metadata(_load_json_metadata(root / AUTHOR_METADATA_RELATIVE_PATH)))`)
is replaced by `merged.update(_resolve_durable_identity_fields(root, env=environ))`.

Verification that the stale path has no call site (definition-only remains, per the
GO-approved one-slice deprecation):

```text
$ grep -n "_load_json_metadata\|AUTHOR_METADATA_RELATIVE_PATH" scripts/bridge_author_metadata.py
38:AUTHOR_METADATA_RELATIVE_PATH = Path(".gtkb-state") / "bridge-author-metadata" / "current.json"
211:def _load_json_metadata(path: Path) -> dict[str, Any]:
```

Line 38 (constant) and line 211 (helper def) are the ONLY remaining references; neither
is a loader read. A deprecation comment at the constant records the one-slice retention
and the follow-on removal once external writers are migrated.

New precedence in `load_author_metadata`: **explicit > env runtime envelope >
durable identity (registry)**. The four runtime fields can only come from env/explicit.

New helper `_resolve_durable_identity_fields(project_root, *, env=None)` returns ONLY
`{author_identity, author_harness_id}` (or `{}` on ambiguity — zero/multiple active
Prime Builders, no registry id, or no role assignment) and NEVER the runtime fields. It
threads `project_root` through the projection-backed loaders
(`harness_roles.load_role_assignments`, `harness_identity.load_harness_identities`) so it
reads the intended registry. Per-harness name resolution mirrors
`scripts/_kb_attribution.resolve_changed_by` (env `GTKB_HARNESS_NAME` -> single ACTIVE
Prime Builder); imports are local to avoid a module import cycle.

### 2. Spec-to-Test Mapping (each acceptance criterion -> executed test)

| Acceptance criterion (spec clause) | Test | Result |
|---|---|---|
| Durable fields resolve from the registry per call; runtime fields NEVER returned (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`) | `test_durable_identity_fields_resolve_from_registry` | PASS |
| Stale `current.json` for another harness is NOT read as a baseline — S389 regression (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`); replaces `test_load_author_metadata_uses_project_session_file` | `test_stale_current_json_is_not_read_as_baseline` | PASS |
| Env runtime envelope + durable identity compose a complete, correct stamp (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) | `test_runtime_envelope_supplies_session_model_fields` | PASS |
| Incomplete sources fail closed, never a wrong stamp (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`) | `test_incomplete_sources_fail_closed_not_wrong_stamp` | PASS |
| Explicit > env > durable-identity precedence preserved | `test_explicit_overrides_env_and_identity` | PASS |
| `ensure_author_metadata` short-circuit on embedded metadata preserved | `test_embedded_metadata_short_circuit_preserved` | PASS |

The S389 regression test directly proves the NO-GO `-002` scenario: a stale `current.json`
holding Codex/A metadata + a registry resolving Claude/B + an env runtime envelope yields
a complete, correct Claude/B stamp with none of the Codex/A values leaking. The
fail-closed test proves the impossible-source case (env unset, no header) raises rather
than mis-stamping — the provenance-safe behavior the REVISED escalated for owner
attention if a complete-stamp-with-env-unset were ever required (it was not required by
the GO).

### 3. Focused pytest (exact commands + observed results)

```text
$ python -m pytest platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short
10 passed in 0.68s
```

### 4. Related call-site regression coverage (`ensure_author_metadata`-dependent paths)

`ensure_author_metadata`'s signature and its embedded-metadata short-circuit are
unchanged; the behavior change is confined to `load_author_metadata`'s baseline source.
The bridge proposal/revision/implementation-report helper paths reach author metadata
through `ensure_author_metadata`, and the dispatch paths exercise them end to end:

```text
$ python -m pytest platform_tests/scripts/test_bridge_author_metadata.py \
    platform_tests/scripts/test_cross_harness_bridge_trigger.py \
    platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
101 passed in 3.76s
```

`test_embedded_metadata_short_circuit_preserved` proves a self-authoring caller (the
dominant dispatched-worker and interactive path) is unaffected even with no registry/env.

### 5. Code-quality gates (lint AND format — separate gates)

```text
$ python -m ruff check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py
All checks passed!

$ python -m ruff format --check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py
2 files already formatted
```

### 6. WI-4468 disposition (explicit)

**WI-4468 remains OPEN.** This slice did not implement or prove the Codex
implementation-report helper metadata-source case. WI-4522 hardens the shared-`current.json`
provenance surface in `load_author_metadata`, which overlaps WI-4468's concern, but the
Codex-side implementation-report helper path was neither modified nor regression-tested
here (it is out of the declared `target_paths`). Residual WI-4468 scope: prove (or fix)
the Codex implementation-report helper's author-metadata source behavior directly.

## Existing-Test Disposition (protected-behavior discipline)

`test_load_author_metadata_uses_project_session_file` asserted the exact behavior this
fix removes (trusting `current.json` as a complete baseline — the test that codified the
S389 hazard). Per GOV-06 spec-first correction it was **updated in place** (renamed to
`test_stale_current_json_is_not_read_as_baseline` with the corrected assertion), not
deleted for convenience. All other pre-existing tests in the module are unchanged and
still pass. A new autouse `_clear_author_env` fixture makes the suite hermetic against the
live dispatch session's environment (it derives the full env-var set from the module's own
`FIELD_ENV_NAMES`), and a temp registry-projection fixture exercises the `project_root`
threading.

## Out-of-Scope Pre-Existing Failure (transparency)

`platform_tests/scripts/test_dispatch_author_meets_reviewer.py::test_dispatch_emits_author_meets_reviewer_refused_diagnostic_record_on_refusal`
**fails on pristine code with this slice's changes stashed** (verified via `git stash`):
it asserts dispatch reason `author_meets_reviewer_refused` but observes
`no_ready_target_for_role`. This is a dispatcher target-selection routing assertion,
not an author-metadata-stamping path, and is unrelated to and unaffected by this slice.
Reported here so the verifier does not attribute it to WI-4522; it should be triaged
separately (candidate standalone defect).

## Specification Links

Carried forward from `-003`:

- **GOV-STANDING-BACKLOG-001** — WI-4522 backlog authority (P3 bridge-protocol provenance defect).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4522; allows `source` + `test_addition`).
- **GOV-DOCUMENT-AUTHOR-PROVENANCE-001** — the provenance invariant restored (fail-closed, not wrong-stamp).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge; no `bridge/INDEX.md` workflow-state mutation beyond this entry.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH/project/work-item/target-path metadata concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (table above).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory).

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4522 under `PAUTH-…-BATCH-2`.
- **Cycle-12 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Per-harness resolution at filing time"; this implementation honors that choice (durable identity + own runtime envelope; not a keyed cache).
- **Loyal Opposition NO-GO `-002` + GO `-004` (Codex, harness A)** — `-002` established the design correction (durable identity cannot supply the full set; no-env path must not read the stale shared baseline); `-004` approved the REVISED-2 design implemented here.
- _Live semantic deliberation search was not run from this headless auto-dispatch worker (no interactive `gt deliberations` surface in the dispatch context); prior-decision context was gathered from the live bridge thread and the cited rule/spec evidence._

## Owner Decisions / Input

No new owner AskUserQuestion is required. Implementation proceeded under durable
owner-decision evidence carried forward from `-003`:

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ
  (2026-06-13) admitting WI-4522 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`).
- **Cycle-12 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected
  "Per-harness resolution at filing time", the approach implemented here.

The GO `-004` records "No owner action is required for this GO." No owner-blocking decision
arose during implementation.

## Recommended Commit Type

`fix:` — repairs broken behavior (concurrent-harness wrong-stamp under `current.json`
sharing) and restores a `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` invariant; no new public API
or capability surface. The diff is net-additive (a small helper + a corrected test
module) but its purpose is a defect repair, not a feature, per the Conventional Commits
discipline in `.claude/rules/file-bridge-protocol.md`.

## Risk / Rollback

- **Risk: low-moderate.** One source change at one call site + one small side-effect-free
  helper; removes shared mutable state rather than adding it.
- **Bounded intended behavior change:** a non-self-authoring caller in a no-env context
  that previously returned `current.json`'s (possibly wrong) metadata now raises
  `BridgeAuthorMetadataError`. The dispatcher env-injection follow-on (a sibling WI, out of
  this slice's `target_paths`) restores correct filing for non-self-authoring workers.
- **Rollback:** revert `load_author_metadata` + delete `_resolve_durable_identity_fields`
  + restore the original `test_load_author_metadata_uses_project_session_file`. No schema,
  KB, or migration impact.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
