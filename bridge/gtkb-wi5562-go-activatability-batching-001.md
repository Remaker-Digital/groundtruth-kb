NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata


# WI-5562: Bound Prime GO-Activatability Diagnostics Per Scan

bridge_kind: prime_proposal
Document: gtkb-wi5562-go-activatability-batching
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5562-GO-ACTIVATABILITY-BATCHING-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5562

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py", ".cursor/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source | test | managed helper parity
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

WI-5518 bounds compact numbered-file inventory by current bridge threads, but
its canonical implementation report records a 360.38-second Prime compact scan
because `_role_filter` still calls `create_authorization_packet` independently
for every current implementation `GO`. Each call repeats request-invariant
authorization setup, including a dirty-worktree inventory and a scan of
historical peer packets and implementation reports.

WI-5562 proposes a request-scoped, read-only authorization evaluation context.
One Prime scan may reuse immutable observations gathered during that scan while
every per-GO proposal, GO, PAUTH, target, sufficiency, independence, and denial
check remains mandatory. The default implementation-start and operation-time
paths remain uncached and continue to revalidate live authority on every call.

## Defect And Current Evidence

Canonical evidence comes from:

- `bridge/gtkb-wi5518-compact-bridge-scan-scalability-003.md`, which records a
  4.303-second compact inventory, a 3.94-second Loyal Opposition compact CLI,
  and a 360.38-second Prime compact CLI.
- `scripts/implementation_authorization.py`, where
  `create_authorization_packet` invokes
  `peer_report_dirty_path_collision_reason` for every proposal with targets.
- `peer_report_dirty_path_collision_reason`, which currently executes
  `_dirty_worktree_paths` and scans every named peer packet and each peer's
  current bridge/report state for every GO candidate.
- `.claude/skills/bridge/helpers/scan_bridge.py`, where `_role_filter` invokes
  `_go_activatable` once for every non-terminal-kind Prime GO and
  `_go_activatable` invokes `create_authorization_packet` without a shared
  request context.

The existing checks are semantically required. The defect is repeated setup
within one read-only scan, not the presence of a fail-closed authorization
diagnostic.

## Current Ownership And Sequencing

This proposal intentionally overlaps active, already-governed work and may not
start implementation until those exact bytes are released:

1. WI-5518 currently owns the four scanner helper projections and
   `platform_tests/scripts/test_scan_bridge.py`. Its implementation report is
   latest `NEW` at
   `bridge/gtkb-wi5518-compact-bridge-scan-scalability-003.md`. WI-5562 must
   wait for independent VERIFIED and focused finalization of WI-5518.
2. WI-5382 owns the current 53-line schema-v3 regression hunk in
   `platform_tests/scripts/test_implementation_authorization.py`. Its terminal
   chain remains under canonical finalization repair. WI-5562 must wait for a
   valid terminal/finalized WI-5382 disposition and must not absorb, edit,
   stage, or attribute that foreign hunk.
3. `scripts/implementation_authorization.py` is currently clean, but it is a
   shared authorization surface referenced by other active bridge threads.
   A future WI-5562 start must pass the ordinary peer-report and cross-claim
   collision gates and must refuse mutation if any predecessor or peer still
   reserves an overlapping target.
4. Immediately before any WI-5562 implementation-start transaction, all seven
   declared targets must be clean relative to the then-current focused
   predecessor commits. Any unexplained dirty or untracked target is a hard
   stop requiring a revised disposition, not an adoption opportunity.

Independent GO on this proposal approves the design only. It does not waive
these ordering and clean-preimage conditions.

## In-Root Placement Evidence

All seven targets, all numbered bridge evidence, the active PAUTH, WI-5562, and
TEST-11617 are within `E:/GT-KB`. No outside-root file, retired assessment
directory, harness scratchpad, auto-memory, or other non-canonical artifact is
an input, dependency, or evidence source.

## Specification Links

- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` - governs the bounded, read-only compact bridge workflow and exact role/actionability result.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - preserves dispatcher/TAFE and numbered bridge authority without a competing queue or cache.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct append-only bridge status and canonical numbered-file evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires PAUTH, independent GO, exact claim, implementation-start, report, and verification as separate gates.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - forbids scan optimization from bypassing or weakening implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires uncached live revalidation at protected operation time.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - preserves the exact project, work item, specifications, target paths, and mutation envelope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires every relevant governing specification to be linked before GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to the exact project, PAUTH, and WI-5562.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed tests that derive from every linked specification before VERIFIED.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires measurable bounded work, preserved hard invariants, rollback, and fail-closed evidence.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact hunk ownership and preservation of all foreign work.
- `ADR-CROSS-HARNESS-PARITY-001` - requires equivalent behavior on all applicable scanner projections.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires explicit per-harness applicability and parity evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps every implementation and evidence dependency within the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - WI-5562 and TEST-11617 are the canonical defect and regression carriers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the defect through MemBase, PAUTH, proposal, tests, report, verdict, and focused finalization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps current authority and historical evidence reconstructable without introducing a new authority surface.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps proposal, GO, claim/start, implementation report, VERIFIED, and commit as distinct transitions.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded PAUTH carriers and governed proposals for newly reproduced bridge, TAFE, dispatcher, and harness defects while preserving all downstream gates.
- `DELIB-202666121` records the accepted bounded, read-only compact workflow precedent whose role semantics WI-5562 preserves.
- `DELIB-202665650` records the accepted compactness and no-competing-source-of-truth precedent.

A governed Deliberation Archive search for Prime bridge-scan GO activatability,
authorization diagnostics, batching, and memoization found no decision that
rejects a request-scoped read-only evaluation context. Unrelated search results
were excluded.

## Owner Decisions / Input

No new owner decision is required.
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner-decision
basis for active singleton authorization
`PAUTH-DISPATCHER-BLACK-BOX-WI5562-GO-ACTIVATABILITY-BATCHING-20260718`.

That PAUTH permits this proposal now. Protected implementation remains
prohibited until WI-5518 and WI-5382 are terminal and focused-finalized, all
seven targets are clean, Loyal Opposition independently returns GO, the Prime
session holds the exact work-intent claim, and a schema-v3 start packet
authorizes the exact target set.

The owner's dispatcher-configuration hold remains binding. WI-5562 changes no
dispatcher or TAFE configuration, routing, eligibility, cap, daemon, lease,
claim state, runtime artifact, worker process, harness registration, role
assignment, or external system.

## Requirement Sufficiency

Existing requirements are sufficient. TEST-11617 states the observable
contract: preserve exact Prime actionable and `blocked_non_activatable`
classification and every denial reason while bounding repeated setup within
one read-only scan. No new role, lifecycle state, queue, cache authority, or
operation-time authorization rule is required.

## Proposed Design

1. Add an explicit request-scoped evaluation-context API to
   `scripts/implementation_authorization.py`. The context may retain immutable
   normalized values needed by multiple GO diagnostics in one scan, including
   the dirty-path inventory, historical peer-packet/report collision facts,
   and repeated project/authorization lookup results keyed by their full
   identity.
2. The context must not persist to disk, mutate MemBase, retain an open
   database connection, modify a claim, write an authorization packet, or
   outlive the calling `scan(...)` request.
3. Extend `create_authorization_packet` with an optional context parameter.
   Omitting the parameter must preserve the current uncached behavior exactly.
   The `begin`, `activate`, `validate`, implementation-start, and
   operation-time entry points must not create or reuse the scan context.
4. Update the scanner so one Prime scan creates at most one context and passes
   it to each `_go_activatable` call after terminal-kind filtering. Loyal
   Opposition scans and Prime scans with no implementation GO must not perform
   unnecessary authorization setup.
5. Preserve all per-GO checks and their current error ordering: exact bridge
   chain and approved proposal/GO resolution, proposal parsing, PAUTH status
   and scope, work-item/project membership, structured PAUTH amendment
   validation, review independence, specification-derived verification,
   requirement sufficiency, cross-claim collision when a session is supplied,
   peer-report dirty-path collision, bootstrap binding, and packet shape.
6. Cache only facts whose authority is intentionally snapshotted for that
   single read-only scan. Time-sensitive packet creation fields and per-GO
   content remain per-call. A new scan must observe current files, project
   state, worktree state, and peer reports rather than reuse prior results.
7. Keep the `.claude`, `.codex`, and `.cursor` live helpers byte-identical.
   Apply equivalent behavior to the managed adopter template while preserving
   its existing profile-specific terminal-work-item handling.

## Out Of Scope

- Persistent caches, aggregate indexes, alternate queues, generated authority
  files, background refreshers, telemetry services, or process-global mutable
  memoization.
- Any change to authorization decisions, denial text, denial ordering, role
  actionability, terminal-kind classification, archive policy, or bridge
  status semantics.
- Any weakening or caching of protected operation-time checks, claim
  validation, implementation-start validation, packet liveness, or target
  authorization.
- Dispatcher/TAFE configuration or runtime, routing, eligibility, caps,
  leases, workers, harness configuration, credentials, direct harness contact,
  external systems, deployment, release, Git push, history rewrite, cleanup,
  or unrelated worktree mutation.
- Implementing WI-5521's separate peer-report collision policy changes. This
  slice may reuse current peer-report facts more efficiently but must not
  broaden or narrow that guard's semantics.

## Cross-Harness Disposition

- Harness A (Codex), B (Claude Code), and E (Cursor): applicable. Their live
  scanner helper projections must remain byte-identical.
- Harness C (Antigravity), D (Ollama), F (OpenRouter), and H (Alibaba): not
  applicable to a repo-local `scan_bridge.py` target; their governed dispatch
  routes do not use these manual helper files as authority.
- Harness G (Goose): retired in the canonical harness registry and has no
  repo-local scanner-helper target.
- Managed adopter template: applicable. It receives equivalent request-scoped
  batching while retaining its distinct terminal-work-item profile.
- Shared implementation-authorization engine: applicable to every caller, but
  the new behavior is opt-in by an explicit per-scan context; ordinary callers
  retain current uncached semantics.

No waiver is requested.

## Specification-Derived Verification Plan

| Governing requirement | Executable verification | Required result |
|---|---|---|
| `TEST-11617`; `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` | Add a deterministic many-GO fixture and compare normalized Prime compact output against the current independent-per-GO reference. | `actionable`, `blocked_non_activatable`, and every denial reason and order are identical. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Inspect writes and instrument filesystem/state helpers during the scan. | Zero bridge, dispatcher, TAFE, packet, claim, runtime, MemBase, or cache writes occur. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Unit-test valid and invalid GO packets with and without a shared context, including missing/expired PAUTH, self-review, requirement gaps, and peer collisions. | Context and ordinary evaluation produce the same packet or exact `AuthorizationError`; no denial is suppressed. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Invoke public `begin`/validation paths across two successive requests while changing fixture authority between requests. | Public operation-time paths re-read current authority and the second request observes the change; no scan context crosses requests. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Instrument deterministic setup operations rather than wall-clock thresholds. | Dirty-worktree and peer-corpus setup execute at most once per scan; repeated project/PAUTH facts execute at most once per full cache key; per-GO content checks still execute once per GO. |
| `ADR-CROSS-HARNESS-PARITY-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Hash live helper copies and run equivalent live/template many-GO fixtures. | A/B/E copies are byte-identical; template behavior is equivalent without losing profile-specific logic. |
| `GOV-WORK-TREE-HYGIENE-001` | Confirm terminal/finalized WI-5518 and WI-5382, clean exact preimages, exact claim/start targets, and inspect focused diff/hunks. | No foreign hunk is adopted, edited, staged, or committed; only authorized WI-5562 hunks enter finalization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete focused modules, Ruff check/format, compilation, exact diff check, both bridge preflights, and independent Loyal Opposition rerun. | Every mapped check passes against exact final bytes before VERIFIED and focused commit. |

Required focused commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py scripts/implementation_authorization.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_implementation_authorization.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py scripts/implementation_authorization.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_implementation_authorization.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py scripts/implementation_authorization.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_implementation_authorization.py
git diff --check -- .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py scripts/implementation_authorization.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_implementation_authorization.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5562-go-activatability-batching
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5562-go-activatability-batching
```

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5562; TEST-11617; bridge/gtkb-wi5518-compact-bridge-scan-scalability-003.md; DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5562-GO-ACTIVATABILITY-BATCHING-20260718",
  "canonical_authority": "dispatcher/TAFE state, status-bearing numbered bridge files, live MemBase project authorization, current claims, and operation-time validation remain authoritative",
  "primary_route": "one request-scoped authorization evaluation context created by a Prime scan and passed explicitly to GO diagnostics",
  "before_behavior": "each current Prime GO independently repeats dirty-worktree, peer-corpus, and repeated authorization setup before returning its activatability result",
  "after_behavior": "one read-only scan snapshots request-invariant observations once and reuses them across per-GO diagnostics while every per-GO rule and every ordinary operation-time call remains live and fail-closed",
  "self_descriptive_naming": "the context and call sites identify scan-scoped authorization evaluation rather than presenting a persistent cache or a new authority",
  "obsolete_guidance_disposition": "the per-GO setup loop is replaced only on the explicit scanner call path; the default create_authorization_packet route remains uncached",
  "history_preservation": "numbered bridge history, full scan output, denial reasons, WI-5518 evidence, WI-5562 evidence, and focused predecessor commits remain reconstructable",
  "baseline": {
    "compact_inventory_seconds": 4.303,
    "loyal_opposition_compact_seconds": 3.94,
    "prime_builder_compact_seconds": 360.38,
    "residual_source": "per-GO _go_activatable calls into create_authorization_packet"
  },
  "expected_result": {
    "classification": "exact normalized actionable and blocked_non_activatable equivalence",
    "setup_bound": "request-invariant work once per scan or once per full immutable cache key",
    "per_go_validation": "all proposal, GO, PAUTH, sufficiency, independence, target, and collision checks retained",
    "operation_time": "ordinary implementation-start and validation entry points remain uncached and live"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused WI-5562 seven-file hunks",
    "verification": "rerun both focused modules, parity hashes, deterministic setup counters, exact classification equivalence, and both bridge preflights"
  },
  "hard_invariants": [
    "no authorization outcome, reason text, or reason ordering changes",
    "no context persists beyond one scan or becomes canonical authority",
    "no protected operation-time path reuses scan observations",
    "no persistent cache, alternate queue, dispatcher/TAFE mutation, or harness mutation is introduced",
    "live A/B/E helper copies remain byte-identical and the template retains its distinct profile",
    "WI-5518 and WI-5382 terminal focused finalization plus clean preimages precede implementation"
  ],
  "fail_closed_conditions": [
    "batched and independent-per-GO classifications differ",
    "any denial disappears, changes text, or changes order",
    "a second scan fails to observe changed fixture authority",
    "operation-time validation accepts a stale scan observation",
    "request-invariant setup scales with GO count in deterministic instrumentation",
    "any target is dirty, reserved, or not released by its predecessor at implementation start",
    "independent GO, exact claim, schema-v3 start, independent VERIFIED, or focused finalization is absent"
  ],
  "essential_context_preservation": "current bridge state, exact proposal and GO, PAUTH and project/work-item scope, specification links, requirement sufficiency, review independence, target paths, collision diagnostics, denial reasons, and full archival evidence remain available"
}
```

## Acceptance Criteria

1. A deterministic many-GO fixture proves request-invariant dirty-worktree,
   peer-corpus, project, and PAUTH setup is bounded per scan or exact immutable
   key rather than repeated for every GO.
2. The same fixture proves normalized `actionable`,
   `blocked_non_activatable`, `go_file`, denial reason text, and denial reason
   ordering are identical to independent per-GO evaluation.
3. Every current format, PAUTH, review-independence, requirement-sufficiency,
   specification-derived verification, collision, bootstrap, and packet-shape
   check remains green, including negative-path fixtures.
4. Omitting the context preserves current `create_authorization_packet`
   behavior. Public `begin`, target validation, activation, and operation-time
   checks never reuse a scan context and observe changed authority on the next
   request.
5. The context performs no writes, persists no file or database state, retains
   no open database connection, and is unreachable after the scan call
   returns.
6. The three live helper copies remain byte-identical. The managed template
   has equivalent batching and preserves its distinct terminal-work-item
   behavior.
7. WI-5518 and WI-5382 are independently VERIFIED and focused-finalized, every
   target is clean, and no active claim or non-terminal peer owns an exact
   target before WI-5562 begins.
8. Focused pytest, Ruff check, Ruff format check, compilation, exact diff
   check, applicability preflight, clause preflight, independent VERIFIED, and
   focused finalization all pass.

## Pre-Filing Preflight

Candidate-content applicability preflight passed before helper filing:

- packet hash:
  `sha256:e58d76dbb37c4b0f2a578dd145562c06b92aec1cb8025144bd56318b9c3173fe`
- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`
- one non-blocking partial-suffix warning for
  `bridge/helpers/scan_bridge.py`; all seven declared target paths exist and
  are explicit.

Candidate-content mandatory clause preflight also passed:

- clauses evaluated: 5
- `must_apply`: 4
- `may_apply`: 1
- evidence gaps in `must_apply`: 0
- blocking gaps: 0
- exit code: 0

After helper filing, both commands must pass again against the operative
numbered proposal with the same zero-gap result.

## Risks And Rollback

The principal risk is accidentally turning a read-only diagnostic snapshot into
stale implementation authority. The opt-in context is therefore confined to
the scanner call graph, carries immutable values rather than open resources,
and is absent from every mutation-capable entry point. A second risk is
silently altering denial precedence while combining lookups; exact reason text
and ordering are regression-locked against independent evaluation.

Rollback requires separate authority and reverts only the focused WI-5562
hunks after checking they do not contain predecessor or peer work. The
numbered bridge chain, MemBase work item, test artifact, PAUTH, independent
verdicts, and WI-5518/WI-5382 predecessor history remain append-only.

## Files Expected To Change

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/bridge/helpers/scan_bridge.py`
- `.cursor/skills/bridge/helpers/scan_bridge.py`
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`
- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_scan_bridge.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`perf(bridge)`: bound repeated read-only GO diagnostics without changing
authorization or role semantics.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
