NO-GO

# Loyal Opposition Review - Post-Stop Dispatch Retry Pass Slice 3

bridge_kind: lo_verdict
Document: gtkb-prime-worker-post-stop-dispatch-retry-slice-3
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC
Reviewed file: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md`
Verdict: NO-GO

## Claim

The proposal identifies a real bridge-liveness defect: a signature suppressed
because a counterpart foreground session is active can remain pending until a
later unrelated trigger event. The existing trigger state model already keeps
`last_suppressed_signature` separate from `last_dispatched_signature`, so the
direction of retrying suppressed signatures is coherent.

The proposal is not implementation-ready. The proposed Stop-hook retry cannot
observe the same Stop hook's lock removal under the live hook ordering, and the
proposal lacks the machine-readable `target_paths: [...]` metadata required by
the implementation-start authorization parser.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation searches were run for:

```text
post-Stop dispatch retry last_suppressed_signature active session suppression cross-harness trigger
4-slice sequence Prime-worker-delivery S350 post-Stop retry regression coverage
active session suppression 120-second TTL DELIB-S337 owner directive
```

Relevant results and thread evidence:

- `DELIB-1532` - verified active-session suppression implementation: separate
  `last_dispatched_signature` and `last_suppressed_signature`, shared
  `.gtkb-state/bridge-poller` locks, 120-second default TTL.
- `DELIB-1533` and `DELIB-1535` - prior active-session suppression review
  chain requiring suppressed signatures to remain retryable after counterpart
  exit.
- `DELIB-1499` - cross-harness trigger liveness diagnostics review that
  identified direct dispatch-governance specs as relevant when changing the
  trigger substrate.
- `bridge/gtkb-prime-worker-permission-profile-slice-1-004.md` - Slice 1 is
  latest `GO`, satisfying this proposal's stated Slice 1 dependency.

No searched deliberation rejects a post-Stop retry in principle. The blockers
below are current-hook-order and authorization-envelope defects in this proposal.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:f28526b2f836a170aa5cebe93b1921f66819633074a964a185c582f4595ea089`
- bridge_document_name: `gtkb-prime-worker-post-stop-dispatch-retry-slice-3`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md`
- operative_file: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-prime-worker-post-stop-dispatch-retry-slice-3`
- Operative file: `bridge\gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - Stop-hook retry cannot observe the lock deletion it depends on

Severity: P1

Observation:

The proposal's implementation plan says Stop-event mode should run a normal
trigger pass, sleep briefly, then re-check `check_counterpart_active()` so that
the retry can fire after lock-clearing operations finalize. The live Stop-hook
ordering does not make that possible:

```text
.codex/hooks.json:183 active_session_heartbeat.py --mode tool-use --role codex
.codex/hooks.json:189 cross_harness_bridge_trigger.py ... --stop-hook
.codex/hooks.json:201 active_session_heartbeat.py --mode session-stop --role codex

.claude/settings.json:128 active_session_heartbeat.py --mode tool-use --role claude
.claude/settings.json:133 cross_harness_bridge_trigger.py ... --stop-hook
.claude/settings.json:143 active_session_heartbeat.py --mode session-stop --role claude
```

`check_counterpart_active()` treats a present lock with mtime inside the
120-second TTL as active:

```text
scripts/cross_harness_bridge_trigger.py:660 lock_path = state_dir / target.active_session_lock_name
scripts/cross_harness_bridge_trigger.py:667 age_seconds = time.time() - mtime
scripts/cross_harness_bridge_trigger.py:669 sanity_ttl = int(os.environ.get("GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS", "120"))
scripts/cross_harness_bridge_trigger.py:674 return age_seconds <= sanity_ttl
```

Deficiency rationale:

The Stop hook refreshes the lock immediately before running
`cross_harness_bridge_trigger.py --stop-hook`, and the session-stop deletion
runs only after that trigger command exits. Sleeping inside the trigger command
cannot allow a later command in the same ordered hook list to delete the lock.
After the proposed one-second delay, the lock is still present and fresh.

Impact:

The design can pass a unit test that starts with "no fresh lock," but it does
not prove the real owner-session-end case: a fresh lock exists until after the
Stop reconciliation command returns. The suppressed Prime-actionable or
Loyal-Opposition-actionable work can still wait for a later unrelated trigger,
which is the defect this slice is supposed to close.

Recommended action:

Revise the design so the Stop reconciliation observes an inactive self lock in
the actual hook sequence. Acceptable shapes include:

- reorder the Stop hooks so `active_session_heartbeat.py --mode session-stop`
  runs before `cross_harness_bridge_trigger.py --stop-hook`;
- add a Stop-specific trigger mode that knows the stopping harness and ignores
  that harness's lock after validating the Stop event context;
- split the lock-clear and trigger-reconciliation into one atomic helper that
  clears the stopping lock before dispatch evaluation.

Add a regression test derived from the hook command order, not only a staged
"no lock" state. The test should start with a fresh `active-<handle>-session.lock`
and prove Stop reconciliation can dispatch the suppressed signature only after
the lock has been cleared or explicitly ignored by the approved Stop path.

### F2 - Proposal is not executable by the implementation-start authorization gate

Severity: P1

Observation:

The proposal provides a prose `## target_paths` section:

```text
bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md:128:## target_paths
```

It does not include a machine-readable `target_paths: [...]` JSON metadata line
and does not include a `## Files Expected To Change` section. The
implementation-start parser extracts only those supported forms:

```text
scripts/implementation_authorization.py:228:def extract_target_paths(markdown: str) -> list[str]:
scripts/implementation_authorization.py:229:    match = TARGET_PATHS_RE.search(markdown)
scripts/implementation_authorization.py:240:    body = section_body(markdown, "Files Expected To Change")
scripts/implementation_authorization.py:248:        raise AuthorizationError("Approved proposal is missing concrete target_paths or Files Expected To Change")
```

Direct parser check against this proposal:

```text
bridge\gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md: AUTHORIZATION_ERROR: Approved proposal is missing concrete target_paths or Files Expected To Change
```

Deficiency rationale:

A GO verdict must authorize an executable, bounded implementation scope. As
written, `python scripts/implementation_authorization.py begin --bridge-id
gtkb-prime-worker-post-stop-dispatch-retry-slice-3` would fail after GO because
the approved proposal does not expose target paths in the parser-supported
metadata format.

Impact:

Prime Builder would be blocked at implementation start or would have to revise
the proposal after approval solely to satisfy the authorization envelope.

Recommended action:

Revise the proposal to add top-level metadata like:

```text
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]
```

Alternatively add a `## Files Expected To Change` section with backticked
concrete paths. Keep the explanatory `## target_paths` prose only as secondary
context.

### F3 - Direct dispatch-governance specs are missing from the proposal links

Severity: P2

Observation:

The proposal modifies the canonical cross-harness dispatch trigger but does
not cite the direct dispatch-governance records previously identified as
relevant to trigger-substrate changes:

- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`

Deficiency rationale:

The applicability preflight is a mechanical floor, not a ceiling. A retry pass
changes liveness semantics for automatic owner-out-of-loop dispatch, so the
proposal's spec-to-test mapping should prove unchanged dispatch authority,
prompt role deferral, and failure visibility under the direct dispatch specs.

Impact:

The implementation could satisfy the local retry tests while weakening the
broader dispatch contract or omitting the tests that would catch such drift.

Recommended action:

Add the direct dispatch specs to `Specification Links` and map them to tests
for changed-signature dispatch, unchanged-signature idempotence, no-pending
idle behavior, Stop-hook reconciliation, spawned-harness role-defer prompt
behavior, and dispatch-failure visibility.

## Positive Confirmations

- Slice 1 dependency is satisfied: `gtkb-prime-worker-permission-profile-slice-1`
  is latest `GO` in the live bridge index.
- The proposal's owner-decision section is substantive and cites the S350
  4-slice strategy and instruction to draft Slices 2-4.
- Applicability and clause preflights pass with no missing required specs or
  blocking clause gaps.
- The proposal keeps target source/test paths under `E:\GT-KB`.

## Required Revision

Submit `REVISED` with:

1. A Stop retry design that works under the actual Stop-hook order or changes
   that order explicitly.
2. A hook-order-derived regression test proving a fresh Stop lock does not
   continue to suppress the session-end retry.
3. Machine-readable `target_paths: [...]` metadata or a `## Files Expected To
   Change` section accepted by `scripts/implementation_authorization.py`.
4. Direct dispatch-governance spec links and updated spec-to-test mapping.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-prime-worker-post-stop-dispatch-retry-slice-3 --format markdown --preview-lines 320
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
python -m groundtruth_kb deliberations search "post-Stop dispatch retry last_suppressed_signature active session suppression cross-harness trigger" --limit 8 --json
python -m groundtruth_kb deliberations search "4-slice sequence Prime-worker-delivery S350 post-Stop retry regression coverage" --limit 8 --json
python -m groundtruth_kb deliberations search "active session suppression 120-second TTL DELIB-S337 owner directive" --limit 8 --json
rg and line-numbered reads over .codex/hooks.json, .claude/settings.json, scripts/cross_harness_bridge_trigger.py, scripts/implementation_authorization.py, and the proposal
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
