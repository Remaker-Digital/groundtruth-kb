REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0d4-5f20-7f62-83ce-c50d98c17952
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; harness A; resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# gtkb-wi6067-shared-envelope-pointer-purge - REVISED: fail-closed wrap and complete verification scope

bridge_kind: prime_proposal
Document: gtkb-wi6067-shared-envelope-pointer-purge
Version: 005
Author: Prime Builder (codex, harness A)
Date: 2026-08-08 UTC
Responds to: bridge/gtkb-wi6067-shared-envelope-pointer-purge-004.md

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-6067

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py", "groundtruth-kb/src/groundtruth_kb/session/wrap.py", "scripts/harness_envelope_equivalence.py", "scripts/session_role_resolution.py", "scripts/harness_probe_dsv4pro-r1.py", "scripts/harness_probe_dsv4pro_r2.py", "scripts/harness_probe_dsv4pro_r3.py", "scripts/harness_probe_q37flash_r3.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_harness_envelope_equivalence.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_modernization_harness_parity.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_harness_probe_dsv4pro-r1.py", "platform_tests/scripts/test_harness_probe_dsv4pro_r2.py", "platform_tests/scripts/test_harness_probe_dsv4pro_r3.py", "platform_tests/scripts/test_harness_probe_q37flash_r3.py"]

## Why This Post-GO Revision Is Required

Implementation under the `-004` GO exposed a blocking defect that cannot be
corrected inside the approved `-003` target paths. A context with no envelope
of its own can invoke wrap and receive success because both `run_wrap` and
`close_session` use creating fallbacks. The operation mints a new per-session
document and archive entry for a session that never opened. This is not a
cross-context leak -- the foreign context remains untouched -- but it violates
the owner's explicit no-envelope fail-closed ruling.

The first intended unit regression does not actually invoke wrap, so it cannot
detect this behavior. The CLI regression correctly remains red and must not be
changed to accept exit zero.

A broader test sweep also found that the approved production conversions left
their dedicated tests outside `target_paths`. Seventeen failures across seven
out-of-scope test modules still seed or expect the removed pointer/projection.
Four tracked capability-probe scripts also still inspect
`.claude/session/envelope.json`, contradicting the accepted zero-reader end
state even though their path constants are split and escaped a literal path
scan. Filing only `wrap.py` would therefore repeat the scope-completeness defect
that caused the `-002` NO-GO.

## Response To The `-004` GO

The `-004` GO remains correct for the proposal it reviewed, including its
condition to remove the legacy migration read in `envelope.py`. This revision
does not dispute that review. It reports implementation-time evidence that the
approved scope is insufficient for a correct, verifiable implementation and
extends the same thread before any implementation report is filed.

The earlier eight paths are retained. Sixteen paths are added: one production
wrap path, four tracked probe readers, seven directly affected regression
modules, and four probe regression modules. All additions classify as
`source` or `test`, both already permitted by the active non-expiring project
authorization. No new owner decision or authorization class is required.

## Corrected Design

1. `ensure_current` keeps its create-on-miss behavior for OPEN and topic paths.
   That behavior is not used by WRAP.
2. `run_wrap` no longer calls `ensure_current`.
3. `close_session` resolves the explicit `session_id` when supplied, otherwise
   the invoking ambient session id, exactly once. It loads that exact
   per-session document through `load_worker_session`.
4. Closing is non-creating and fail-closed: an unavailable session id, missing
   document, already-closed document, or otherwise non-open document raises
   `EnvelopeError`. `close_session` never calls `open_session`.
5. The existing single-context guard remains as defense in depth. The normal
   no-envelope diagnostic describes the missing invoking-context envelope; it
   does not claim that a foreign shared envelope was reached.
6. An explicit `session_id` takes precedence over a different ambient id, so
   direct API and CLI calls close the requested existing document rather than
   reminting or resolving another context.

This makes the close itself atomic with respect to the existence check and
avoids a wrapper precheck/load race.

## Reader And Verification-Surface Disposition

- The three tracked `harness_probe_*` scripts stop inspecting the removed
  shared projection and report presence from the authoritative per-session
  surface. Their dedicated tests move with that semantic change.
- Role-resolution tests seed `session-envelopes/<session_id>.json` and pass the
  matching context id instead of constructing `session-envelope.json`.
- Envelope equivalence tests seed per-session documents and retain dated
  archive coverage.
- CLI-provenance and SessionStart/writeback tests assert authoritative
  per-session documents and the absence of both shared artifacts.
- Modernization parity tests stop importing/asserting
  `current_envelope_path`, exercise every marker-scope harness with exact
  session ids, and retain close/fallback parity.
- The LO file-safety regression seeds a per-session document keyed by the
  invoking session id rather than a shared pointer.
- The already-scoped runtime test is corrected to invoke `run_wrap` and assert
  failure plus absence of side effects.

The untracked local files `scripts/harness_probe_glm52_r3.py` and
`platform_tests/scripts/test_harness_probe_glm52_r3.py` are not repository
artifacts and are not claimed or modified by this thread. Zero-reader evidence
is measured over tracked source and script files so unrelated concurrent
untracked work is neither appropriated nor silently mutated.

## Baseline Classification

The two topic-context failures in
`platform_tests/scripts/test_session_envelope_runtime.py` reproduce against the
exact HEAD package and configuration. Their stale five-skill assertion predates
the committed additions of `advisory-intake` and `gtkb-work-item`; they are
ambient committed config/test drift, not a WI-6067 regression. The
implementation report will disclose them separately and will not misattribute
or modify them under this thread.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v3 -- the per-session document is
  the sole authority; decision 2's no-envelope case must fail closed.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` -- neither runtime nor capability probes
  may derive current session state from a second shared surface.
- `ADR-CROSS-HARNESS-PARITY-001` -- role, marker-scope, and equivalence behavior
  remain uniform across harnesses after the pointer removal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -- the expanded
  specification-to-test mapping below is executed and carried into the report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -- all governing
  requirements are cited.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` -- this revision records
  the scope change before implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` -- the implementation-time defect,
  baseline evidence, and expanded verification scope remain linked to their
  governed work-item and bridge carrier.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` -- the discovered defect and scope gap
  are preserved in the existing governed carrier rather than normalized into
  passing output.
- `GOV-STANDING-BACKLOG-001` -- WI-6067 remains the tracked implementation
  carrier.

## Prior Deliberations

- `DELIB-20260808-WI6067-WRAP-FABRICATES-ENVELOPE` -- measured defect and root
  cause: wrap fabricates a document/archive for a context that never opened.
- `DELIB-20260808-WI6067-GUARD-CONTRACT-READING` -- structural impossibility
  satisfies the single-context contract, but the no-envelope case must fail.
- `DELIB-20260808-CURRENT-ENVELOPE-OBSOLETE-DESIGN` -- the shared current
  concept is obsolete and erroneous.
- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE` -- purge both
  shared artifacts; do not retain the pointer in a reduced role.
- `DELIB-20260808-ENVELOPE-ABANDONMENT-NORMAL` -- exiting without formal wrap
  is normal; no design may require recalling an exited session to wrap.
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION` and
  `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION` -- active v2
  project authorization covers the source/test additions.
- `DELIB-20260807011939` -- independent Loyal Opposition GO and VERIFIED remain
  required while redundant ceremony is removed.

## Owner Decisions / Input

No new owner decision is requested. The owner has already ruled both questions
that control this revision: the shared pointer/projection must be purged, and a
wrap from a context with no open envelope must fail. This revision implements
those rulings without revisiting them.

## Requirement Sufficiency

**Existing requirements are sufficient.** This revision corrects scope and
implementation behavior under the cited DCL and owner deliberations. It does
not introduce a new capability or requirement.

## Specification-Derived Verification

| Linked requirement | Derived verification |
|---|---|
| Single-context decision 2 | Context A open, context B wraps: `EnvelopeError`; no B document; no new archive; A remains byte-for-byte open. |
| Single-context decisions 1 and 4 | Positive wrap closes the exact existing per-session document and preserves its topics; explicit id wins over a different ambient id. |
| No-envelope fail-closed ruling | Missing id, missing document, and already-closed document all return nonzero/fail without minting any artifact. |
| Source-of-truth freshness | Tracked-source scan finds no live reader or writer of either shared pointer/projection; split path constants are included in the scan. |
| Cross-harness parity | Role resolution, SessionStart writeback, marker-scope behavior, envelope equivalence, and no-envelope isolation pass across the supported harness set. |
| Probe-reader disposition | Each tracked capability probe resolves/checks the authoritative per-session surface and its dedicated suite passes. |
| Mandatory spec-derived testing | Commands, counts, and any ambient failures are reported separately in the implementation report. |

Primary verification command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest `
  platform_tests/scripts/test_session_envelope_runtime.py `
  platform_tests/scripts/test_gtkb_session_id.py `
  platform_tests/scripts/test_session_envelope_cli_provenance.py `
  platform_tests/scripts/test_harness_envelope_equivalence.py `
  platform_tests/scripts/test_session_role_resolution.py `
  platform_tests/hooks/test_session_role_resolution.py `
  platform_tests/scripts/test_modernization_harness_parity.py `
  platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py `
  platform_tests/scripts/test_session_self_initialization.py `
  platform_tests/scripts/test_harness_probe_dsv4pro-r1.py `
  platform_tests/scripts/test_harness_probe_dsv4pro_r2.py `
  platform_tests/scripts/test_harness_probe_dsv4pro_r3.py `
  platform_tests/scripts/test_harness_probe_q37flash_r3.py `
  platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py `
  -q --tb=short
```

`ruff check` and `ruff format --check` run separately on every declared Python
path. The repository scan uses the tracked-file set rather than the ambient
filesystem so concurrent untracked work cannot be mistaken for this change.

## Acceptance Criteria

1. WRAP never opens or fabricates an envelope.
2. A context with no open envelope fails with a nonzero result and creates no
   per-session document or archive entry.
3. A foreign context's open document is not read, changed, or archived by the
   failing wrap.
4. Explicit-id and ambient-id positive wraps close only the exact existing open
   document, preserve its topics, and archive it once.
5. A second wrap of the same closed document fails without a second archive.
6. No tracked source or script reads or writes the shared pointer or shared
   projection, including path constants split across tuple elements.
7. Dedicated role-resolution, equivalence, CLI provenance, SessionStart,
   marker-scope, modernization parity, and probe suites use the per-session
   authority and pass, apart from separately evidenced ambient failures.
8. The `-004` legacy migration-read condition is satisfied.
9. WI-6055's session-id resolver behavior is preserved.
10. The two known topic-profile failures are disclosed as exact-HEAD ambient
    drift and are not made green by weakening their assertions here.

## Risk And Rollback

**Risk.** The scope is wider because the first implementation audit found that
the production change had more dedicated verification surfaces and tracked
probe readers than the literal pointer-reader census revealed. The added paths
are tightly coupled to the same authority migration; leaving them out would
produce false parity confidence and a knowingly incomplete zero-reader claim.

**Concurrency risk.** Two untracked GLM probe files belong to unrelated local
work. This thread will not edit, delete, stage, or claim them. Verification
distinguishes the tracked repository from unrelated ambient files.

**Rollback.** Revert only the declared source and test paths. The change performs
no MemBase mutation, credential operation, on-disk envelope deletion, external
system mutation, or git-history rewrite. Legacy artifact deletion remains the
separately ordered follow-on tranche.

## Recommended Commit Type

`fix:` -- make session wrap fail closed and finish the authority migration in
the affected tracked readers and tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
