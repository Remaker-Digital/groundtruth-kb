NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; WI-5742 emergency-bootstrap implementation worker under DELIB-202667740/-741/-743


bridge_kind: prime_proposal
Document: gtkb-wi5742-emergency-bootstrap-after-action
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5742

target_paths: []
implementation_scope: emergency_bootstrap_after_action_record
requires_review: false
requires_verification: false
kb_mutation_in_scope: false

# After-Action Record — WI-5742 Emergency-Bootstrap Repair of the VERIFIED Finalization Path

This entry is the after-action record required by clause (b) of
`.claude/rules/governance-emergency-bootstrap-protocol.md`. It is an audit
artifact, not an actionable proposal; the thread is closed at `-002` with
status `WITHDRAWN` per that protocol. No review or verification is requested
here. WI-5742's own governed cycle continues separately through its
implementation report at
`bridge/gtkb-wi5742-bound-protected-commit-evaluation-004.md`.

## Commit SHA

- **Emergency-bootstrap commit: `45fedc3993130e1a23e38cfd3177d1663745678c`**
  (`45fedc399`), subject
  `fix(governance): bound protected-commit evaluation and decouple capability lifetime (WI-5742)`.
- HEAD immediately before this commit: `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`.
- HEAD immediately after: `45fedc3993130e1a23e38cfd3177d1663745678c`.
- 7 files changed, 1410 insertions(+), 16 deletions(-).

## Deadlock Rationale (clause (a) conditions)

All three sanctioned conditions in the emergency-bootstrap protocol were met.

**(a1) A foundational governance subsystem was broken and actively failing.**
The protected-commit authorization gate
(`scripts/check_protected_commit_authorization.py --staged`) ran unbounded
while the bridge-publication capability it gates lives at most 120 seconds
(`mint_bridge_publication_capability`, `ttl_seconds: int = 120`, hard rejection
above 300 at `registry_control_plane.py:2663`). Measured on the live repository
this session, the gate cost **241.664s wall / 137.969s CPU** on an 812-path
staged set containing 94 protected paths — **2.01x the capability TTL**. Every
governed `--finalize-verified` therefore had its capability expire mid-gate.

Five implementation reports carried green, independently re-run test evidence
and were each NO-GO'd for that single reason: `wi5824`, `wi5827`, `wi5826`,
`wi5694` cycle 2, and `wi5694` cycle 3. The recorded causes were verbatim:
`bridge publication requires a current registry generation`;
`timed out acquiring registry lock ... control-plane.lock`; and
`BRIDGE_PUBLICATION_REPAIR_REQUIRED` compensation failure leaving an orphan
VERIFIED requiring quarantine.

**(a2) The normal bridge path was blocked by the very defect being repaired.**
WI-5742 is the repair for that finalization path. Its own implementation could
not start through the governed route because the implementation-start packet
gate refused (see § Bypasses), and the threads whose terminal state would clear
the way could only reach terminal state through the VERIFIED finalization that
WI-5742 repairs.

**(a3) The change is the minimal repair that restores the subsystem.** Scope was
held to Layers A and B of the GO'd design. Layer C was deliberately excluded
(see § Repair Scope).

## Repair Scope

Implemented, strictly within the nine `target_paths` declared in the GO'd
proposal:

- **Layer A — fail-closed wall-clock bound.** The full staged evaluation runs
  inside a monotonic budget with per-phase markers (`index_snapshot`,
  `classification`, `registry_assessment`, `live_go_evidence`,
  `verified_evidence`, `transaction_evidence`, `per_path`). On exhaustion the
  gate returns a deterministic **deny** naming the executing phase, elapsed
  time, configured bound, bound source, and remediation. It never passes on
  timeout and never hangs. The value is resolved through a new single
  resolution path, `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`,
  reading `config/governance/protected-commit-timers.toml` with precedence
  env-local → config file → relaxed in-code fallback. **Zero hard-coded timer
  literals** are introduced outside the two documented fallback constants, per
  `DELIB-202667722`. The gate bound and the capability TTL are externalized as
  an invariant-coupled pair (per WI-5806), and the validated accessor **refuses
  to return a bound greater than or equal to the paired TTL**, making the
  stranding precondition unrepresentable in configuration.
- **Layer B1 — invocation-scoped registry snapshot cache** in
  `scripts/controlled_artifact_paths.py`. Disabled by default, so no existing
  caller changes behavior; a single read-only evaluation opens the scope and
  collapses N+1 exclusive-lock snapshot loads to 1. Deliberately not a
  process-global cache, which the proposal rejected as a stale-authority risk.
- **Layer B2 — cheap packet pre-filter** in
  `scripts/implementation_authorization.py`, exposed as a backwards-compatible
  optional `candidate_paths` parameter on `list_named_packets`.
- **Layer B3 — single-pass classification** and exactly one
  `_registry_commit_assessment` per invocation.

**Layer C was NOT implemented and is deferred**, with the reason recorded here
rather than silently omitted. Layer C (C-ii late-mint publication reorder plus
C-iii compensation robustness) lives entirely in
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`. At the
time implementation began that file was dirty with ~632 staged lines belonging
to **WI-5758 / WI-5825**, which the owner had not authorized this commit to
carry. Reordering the publication transaction — the most fragile path in the
system, with five threads queued to finalize through it — under an
emergency-bootstrap exception and without independent pre-review would also be
precisely the scope creep clause (a3) forbids. The delivered guarantee in its
place is the strict bound/TTL inequality above. The known residual is disclosed
in `config/governance/protected-commit-timers.toml` and in the docstring of
`platform_tests/scripts/test_bridge_publication_finalization_atomicity.py`,
where the two Layer-C tests are explicitly `skip`-marked rather than stubbed as
passing, so no false coverage is claimed.

## Before/After Gate Timing (the headline evidence)

| Measurement | Wall | CPU |
|---|---|---|
| **Pre-fix**, 812-path staged set (94 protected), `--staged` route | **241.664s** | 137.969s |
| Post-fix, identical 812-path corpus, run 1 | 59.367s | 11.922s |
| Post-fix, identical 812-path corpus, run 2 | 84.286s | 14.953s |
| Post-fix, realistic 7-path staged finalization, `--staged` route | 38.744s | — |
| Post-fix, realistic 7-path set, post-commit | **9.927s** | — |

Controlled per-phase A/B on the identical 812-path corpus, same process:

| Cost driver | Before | After | Factor |
|---|---|---|---|
| Classification / snapshot loads (B1) | 34.863s | 0.306s | 114x |
| Packet evidence validation (B2) | 75.467s | 1.766s | 43x |

**Relationship to the capability TTL — the point of the whole repair:**

- Before: 241.664s against a 120s TTL = **2.01x the TTL**; every finalization
  necessarily outlived its capability.
- After: worst observed 84.286s, realistic case 9.9–38.7s, against a **110s
  configured bound** and a **120s TTL**. The gate now fits inside the
  capability lifetime with margin in every measurement taken.

The bound was set to 110s rather than the initially drafted 90s after the
812-path corpus showed run-to-run variance of 59s → 84s under concurrent
control-plane lock contention; 90s left only 5.7s of headroom over the worst
observation, which is not the relaxed-first posture `DELIB-202667722` requires.

## Verdict-Identity Evidence (the optimization changes no authorization outcome)

The B2 pre-filter's admission test **is** the clearance matcher
(`path_authorized`), and both exclusion criteria are necessary conditions for
clearance: an expired packet is rejected by `_validate_packet` and can never be
`valid=True`; a packet matching none of the candidate paths cannot authorize any
of them. Empirically, over the live 548-packet corpus:

```text
valid_packet_sets_identical: true
row_counts_identical: true
valid packets (both arms): .gtkb-state/implementation-authorizations/by-bridge/
                           gtkb-wi5638-committed-terminal-archive-reconciliation.json
```

## Gates Run

| Gate | Result |
|---|---|
| `ruff check` (all 6 changed/new `.py`) | **All checks passed** |
| `ruff format --check` (separate gate) | 2 files reformatted, then **all formatted** |
| `scan_secrets.py --staged` | **0 potential secrets, exit 0** — never bypassed; the commit was made conditional on this |
| `pytest` protected-commit suite + 2 new modules | **214 passed, 1 failed, 2 skipped** |
| Work-intent claim | **Acquired through the governed path — no bypass** |

**On the single remaining test failure.**
`test_schema_v2_verdict_hash_passes_live_and_real_index_only_audits` fails with
`BridgeComplianceError: Verdict applicability freshness check rejected a stale
packet_hash`. This is **pre-existing and not a WI-5742 regression**, proven
empirically rather than asserted: all WI-5742 changes were backed up and fully
removed from the worktree, the HEAD versions restored, the new config file
deleted, and the test re-run — it failed identically. The work was then restored
from backup. The likely cause is the concurrent custodial sweep-commit
`02e12e7b0`, which rewrote many `bridge/` files.

**A genuine regression was found and fixed during this work, not hidden.** The
initial B2 implementation called `list_named_packets` with a new keyword
argument. Three existing tests monkeypatch that function with the old
single-argument signature, so the call raised `TypeError`, which
`_load_live_go_evidence`'s broad fail-closed `except` swallowed into "no live GO
evidence" — silently **denying** a path a live packet should have cleared. That
is an authorization regression, not a performance one. The fix degrades
gracefully to the exhaustive enumeration on `TypeError`. All three tests then
passed **without any test being modified**, which is the strongest available
evidence that authorization semantics are unchanged. Test totals moved from
`4 failed / 172 passed` to `1 failed / 214 passed / 2 skipped`.

## Bypasses (each recorded verbatim)

Two bypasses were used, both within the owner-authorized set. Everything in the
never-bypass set held: credential scanning was run and the commit made
conditional on it, the project-root boundary was respected, bridge files remain
append-only, and no content was reported as verified that was not.

**Bypass 1 — implementation-start packet gate.** Attempted through the governed
path first. Verbatim output of
`python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5742-bound-protected-commit-evaluation`:

```json
{
  "authorized": false,
  "error": "Bridge thread is NO-ACTION; the prior GO is non-dispatchable. A later corrected GO is required before implementation authorization."
}
```

Exit code 2. This is exactly the blockage `DELIB-202667743` addresses.

**Bypass 2 — protected-commit authorization gate at commit time.** `--no-verify`
was used on the commit, which is the only gate the owner authorized `--no-verify`
for. The gate's own refusal was observed first and is reproduced here:

```text
FAIL protected-commit authorization
  - config/governance/protected-commit-timers.toml: protected path lacks live GO
    authorization packet or committed terminal VERIFIED bridge evidence or valid
    transaction-local VERIFIED evidence
```

This is the expected consequence of Bypass 1: with no packet mintable, no
protected path can clear. Because `--no-verify` suppresses all pre-commit hooks
rather than only this one, the other gates were run manually and are recorded in
§ Gates Run above.

**Not bypassed:** the work-intent claim gate. The governed claim succeeded
(`acting_role: prime-builder`, `project_id: PROJECT-GTKB-HOUSEKEEPING-HARDENING`).

## Owner Declaration Over the Malformed NO-ACTION (DELIB-202667743)

A Goose session (`prime-builder/goose/G`, session `G-2026-07-31T19-28-58Z`) filed
`bridge/gtkb-wi5742-bound-protected-commit-evaluation-003.md` with status
`NO-ACTION` and this verbatim reason:

> "NO-ACTION: Stale GO. No active claim or implementation. Disposition-close."

Its rationale stated the GO "is stale and carries no live work authorization.
Closing under disposition-close."

This is a documented misuse of the status contract.
`DCL-NO-ACTION-STATUS-SEMANTICS-001` and `.claude/rules/file-bridge-protocol.md`
require a `NO-ACTION` to (a) sit atop a prior Loyal Opposition verdict, (b) state
what the reviewing role must fix, and (c) route the thread back to Loyal
Opposition for a corrected verdict. The protocol states explicitly that
`NO-ACTION` "MUST NOT be used to record a Prime Builder 'no further action'
close." The filed entry closes a valid GO on staleness grounds and names no
verdict defect to correct. Its factual premise is also incorrect: implementation
was not un-initiated by choice — it was blocked first by the
interactive-role-persistence defect (repaired at `451956a13`) and then by the
implementation-start packet gate.

Per `DELIB-202667743`, the owner declared the Loyal Opposition GO at
`bridge/gtkb-wi5742-bound-protected-commit-evaluation-002.md` **OPERATIVE** for
emergency-bootstrap purposes notwithstanding that `NO-ACTION`. This work
proceeded on that authority.

**The `-003` entry remains on disk unmodified as append-only audit history.** It
was not edited, deleted, superseded, or rewritten by this work, consistent with
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Predecessor Threads (WI-5824 and WI-5823)

`DELIB-202667741` authorized this commit to carry WI-5824's and WI-5823's ~1,269
staged lines, because git could not separate them at file granularity from
WI-5742's target files.

**That authorization ultimately did not need to be exercised, and the record
should reflect what actually happened rather than the anticipated shape.**
Mid-session, a concurrent custodial sweep-commit
`02e12e7b0 chore(gtkb): custodial sweep-commit of 812 orphaned paths (owner
sweep exemption)` committed the entire staged tree, including all WI-5824 and
WI-5823 work, into HEAD. By the time the WI-5742 commit was made, those changes
were already ancestors of it. The WI-5742 commit therefore contains **only
WI-5742 work** — verified by inspecting every `WI-` and `DELIB-` marker in the
staged additions before committing — and lands cleanly inside the original
minimal-repair scope of `DELIB-202667740`.

Both predecessor threads carry independent Loyal Opposition GO verdicts and
green independently re-run test evidence, and **their own governed cycles
continue to independent verification**; nothing in this emergency bootstrap
terminates, supersedes, or substitutes for them:

- **WI-5824** — `bridge/gtkb-wi5824-protected-commit-checker-null-safety-ordering-*`,
  GO at `-002`, latest status NO-GO at `-004` whose sole finding was an expired
  implementation-start packet. Its Fix A (null-safe capability clearance) and
  Fix B (transaction-local terminal-evidence ordering) are present in HEAD via
  the sweep commit.
- **WI-5823** — implementation-authorization spec-linkage harvesting (Slices A
  and B), likewise present in HEAD via the sweep commit.

## Counterpart Verification Evidence

Clause (b) of the emergency-bootstrap protocol requires counterpart
verification evidence. That evidence is **not yet available and is not claimed
here.** No Loyal Opposition verification of this repair exists at the time of
writing, and this session cannot supply it — a session may not review its own
work. The governed route to that evidence is WI-5742's implementation report,
filed as `bridge/gtkb-wi5742-bound-protected-commit-evaluation-004.md`, which
enters the Loyal Opposition queue for independent verification. This after-action
record should be read as complete on every other clause and **open on this one**
until that verification lands.

## Owner Decisions / Input

1. **DELIB-202667740** — emergency-bootstrap authorization for WI-5742,
   answering `AUQ-20260731-WI5742-EMERGENCY-BOOTSTRAP` with "Emergency bootstrap
   WI-5742 (Recommended)".
2. **DELIB-202667741** — keystone route, role, and combined commit scope,
   answering `AUQ-20260731-WI5742-KEYSTONE-ROUTE` with "Re-init me as PB, commit
   includes predecessors (Recommended)".
3. **DELIB-202667743** — GO-002 declared operative over the malformed
   `NO-ACTION`, answering `AUQ-20260731-WI5742-GO-OPERATIVE` with "Declare GO-002
   operative, proceed (Recommended)".
4. **DELIB-202667735** — delegated implementation mandate for the
   parallel-operation program.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — append-only numbered
  bridge chain and audit-trail authority. This record is itself an audit-trail
  artifact; the `-003` NO-ACTION entry was left unmodified on disk under it.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — the owner-approval capture
  for this emergency action is `DELIB-202667740`, refined by `DELIB-202667741`
  and `DELIB-202667743`; no formal MemBase artifact was mutated.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — required (blocking) — the status
  contract misused by the `-003` entry, quoted verbatim above.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — required
  (blocking) — the WI-5742 source specification; operation-time enforcement is
  the property violated when a capability expires mid-operation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — the
  project-scoped authorization chain under which the PAUTH triple proceeds.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — required (blocking) — governed Git
  lifecycle; this repair restores a governed finalization's ability to produce a
  backing commit.
- `GOV-WORK-TREE-HYGIENE-001` — required (blocking) — the frozen-HEAD hygiene
  failure this action cleared.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) —
  root-boundary containment; every touched path is in-root.
- `GOV-ENV-LOCAL-AUTHORITY-001` — required (blocking) — scopes the env-local
  layer of the Layer A timer resolution precedence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking)
  — this record's own linkage obligation; every governing specification is cited
  in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) —
  governs the downstream verification of the repair this record documents; the
  spec-to-test mapping lives in WI-5742's implementation report at `-004`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — every measurement and status
  claim here derives from fresh canonical reads made this session.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the
  protected-commit gate is a mechanical enforcement layer; its fail-closed
  posture is preserved.
- `SPEC-1662` — advisory — assertion quality; the new tests assert behavioral
  outcomes, and the two unimplemented Layer-C tests are skip-marked rather than
  stubbed as passing.

## Prior Deliberations

- **DELIB-202667740**, **DELIB-202667741**, **DELIB-202667743** — the three owner
  authorizations governing this action, as above.
- **DELIB-202667722** — timer and throttle governance with relaxed-first
  defaults and a single resolution path; the direct authority for sourcing the
  Layer A bound from configuration and for choosing 110s over 90s.
- **DELIB-202667723** — terminal-evidence sufficiency for expired
  implementation-start packets; the adjacent failure mode that produced WI-5824's
  NO-GO.
- **DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS** — exact recovery of stranded
  terminal transactions; the recovery discipline this repair is designed to stop
  needing.

## Related Finding Recorded, Not Actioned

A stale-arm of the startup-input gate blocked tool use mid-implementation with
`BLOCKED (GTKB-STARTUP-INPUT-GATE)` after a session-envelope boundary at
`2026-08-01T00:30:33Z`, then self-cleared. It cost no work and required no
bypass, but it fired during an active implementation rather than at a genuine
fresh start. Recorded here for whoever owns startup-gate re-arm behavior; not
actioned in this scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
