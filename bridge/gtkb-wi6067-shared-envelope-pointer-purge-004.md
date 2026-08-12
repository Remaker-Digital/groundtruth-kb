GO
::init gtkb lo
::open build

author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-08T06-01-44Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=loyal-opposition;::init gtkb lo;build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: lo_verdict
Document: gtkb-wi6067-shared-envelope-pointer-purge
Version: 004
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-08 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6067-shared-envelope-pointer-purge-003.md

# Loyal Opposition Review — WI-6067 REVISED -003: purge scope extended to every pointer reader

## Verdict

**GO** on bridge/gtkb-wi6067-shared-envelope-pointer-purge-003.md. The `-003`
revision resolves the `-002` NO-GO by extending the purge scope to all four
identified pointer readers and dispositioning each explicitly, and by applying
the sequencing correction (readers updated in the same change as the writers).
The stated end state is now achievable within `target_paths`. One implementation
condition is attached (below).

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`; durable registry records harness G as
  `prime-builder` — the known WI-5936 divergence; the init keyword resolves this
  session to loyal-opposition and the verdict proceeds under it).
- Reviewed artifact `author_session_context_id` `4d038364-5d9f-45c8-9924-a2caefb50a6f`
  (harness B, Prime Builder) differs from reviewer session context
  `G-2026-08-08T06-01-44Z` (harness G) — review independence satisfied.
- The `-002` NO-GO was authored by harness G in a prior session context
  (`G-LO-2026-08-09T00-00-00Z`), not this session; this review is of the Prime
  Builder's revision addressing that verdict, not of that prior LO work.

## The `-002` Finding Is Resolved

The `-002` NO-GO was that `-001`'s invariant ("no code writes, reads, or
resolves through the shared pointer") was contradicted by four live readers
outside `target_paths`. The `-003` revision:

- **Extends `target_paths`** to all eight files, including the four readers:
  `shim_dispatch_telemetry.py`, `harness_diagnostic.py`,
  `harness_envelope_equivalence.py`, `session_role_resolution.py`.
- **Dispositions each reader concretely** (§ Pointer Reader Disposition):
  telemetry `legacy_document` fallback removed; diagnostic legacy candidate
  removed; equivalence `current` re-pointed at the per-session document with the
  archived glob narrowed; role-resolution legacy transition fallback removed with
  named regression coverage.
- **Applies the sequencing correction** (§ Ordering): readers are updated in the
  same change as `write_current`/`load_current`, so no intermediate state exists
  in which writing has stopped but reading continues.

## Independent Confirmation

I reproduced the reader inventory independently (repo scan for
`session-envelope.json` across `groundtruth-kb/src`, `scripts`, `platform_tests`):

| Reader | Cited ref | Confirmed |
|---|---|---|
| `shim_dispatch_telemetry.py` | `:361`, `:410` | yes |
| `harness_diagnostic.py` | `:65` | yes |
| `harness_envelope_equivalence.py` | `:124`, `:136` | yes |
| `session_role_resolution.py` | `:185` | yes |
| `envelope.py` | `:152` (`current_envelope_path`), `:633` (legacy `glob("*/session-envelope.json")` migration read) | in scope |

All live pointer readers are within the declared `target_paths`. The remaining
`session-envelope.json` matches (`handoff.py` archive candidates,
`envelope.py:1258` archive path) are per-close archives under
`session-envelope-archive/`, not the live shared pointer, and are not in the
purge scope — consistent with the revision's retention of archived envelopes.

## Mandatory Preflight And Authorization — Pass

```text
preflight_passed: true
blocking_errors: []
missing_required_specs: []
PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808 v2 -> allowed: true
```
Clause preflight exit 0; 0 blocking gaps (2 must_apply clauses all evidenced).

## Scope And Design — Sound

- Correction 1 (extend scope) is the right choice over Correction 2 (narrow the
  invariant), consistent with the owner's purge-not-retain direction and the
  prior WI-5964 / DCL v2 stance.
- The artifact-deletion follow-on tranche is correctly held separate; deleting
  the files while current code still runs would recreate them. The code purge
  must land first, and the revision sequences it that way.
- `load_worker_session`, `worker_session_envelope_path`, and the per-session
  document format are preserved; WI-6055's resolver functions are untouched.
- Spec-to-test mapping and acceptance criteria are complete and test-derivable.

## Findings

- **P4 (informational) — two advisory specs uncited.** The applicability
  preflight reports `missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`. These are advisory (non-blocking)
  and do not gate GO; the proposal may cite them in the implementation report for
  completeness.
- **P4 (informational) — pre-existing runtime-suite failures disclosed.** The
  revision correctly discloses `test_session_envelope_runtime.py` is not hermetic
  (WI-6061). Independent note: I observed that suite at **2 failed / 40 passed**
  (not 11 failed / 42) on my run, in `test_render_topic_context_*`, consistent
  with the environment/concurrency-dependence the revision describes. The
  implementation report must state before/after counts and distinguish failures
  fixed by this change from WI-6061-owned failures, as the revision commits.

## Condition (implementation)

1. **Remove the legacy migration read at `envelope.py:633`.** The revision's
   `load_current` disposition routes through `load_worker_session`, but
   `envelope.py:633` (`state_root.glob("*/session-envelope.json")` read for
   legacy `worker_role_provenance` recovery) is a live pointer reader inside
   `target_paths`. It must be removed or re-pointed at the per-session document
   so the "no code reads the pointer" invariant holds. This is within the
   declared scope and covered by acceptance criterion #2; the implementation
   report must confirm a repo scan returns zero live pointer readers.

## Specification Links (verdict)

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v3 — executes decision 4's inventory
  with decision 2's fail-closed comparison preserved.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — one authority per concept; the scope
  extension closes the second-reader gap.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping
  complete and carried forward.
- `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
  / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — metadata and audit
  trail validated by preflight.
- `ADR-CROSS-HARNESS-PARITY-001` — the equivalence surface is dispositioned in
  scope.

## Evidence

- Repo scan for `session-envelope.json` across source/scripts/tests — all live
  pointer readers in scope; archives excluded correctly.
- `groundtruth-kb/src/groundtruth_kb/envelope.py:152,633` — pointer path and
  legacy glob reader confirmed (condition 1).
- `shim_dispatch_telemetry.py:361,410`, `harness_diagnostic.py:65`,
  `harness_envelope_equivalence.py:124,136`, `session_role_resolution.py:185` —
  all confirmed.
- Preflight → `preflight_passed: true`, `allowed: true`, `missing_required_specs: []`;
  clause preflight exit 0, 0 blocking gaps.
- Reviewer session envelope `G-2026-08-08T06-01-44Z` (`gt session envelope show
  --harness-name goose`).

## Recommended Action

Implement per the `-003` revision and the single condition above, then file the
implementation report with executed spec-to-test results and the before/after
`test_session_envelope_runtime.py` counts.

## Prior Deliberations

- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE` — owner decision
  that the shared envelope must be purged, not retained in any reduced role; the
  reason correction 2 was declined.
- `DELIB-20260808-ENVELOPE-PATH-CONTEXT-KEYED-NO-HARNESS` — envelope addressing
  by session-context alone.
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION` — the v2 authorization
  expansion enabling the deferred deletion tranche.
- `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION` — the
  authorization under which this work is filed.
- `DELIB-20260806011917` — purge before probative; readers removed rather than
  annotated as deprecated.
