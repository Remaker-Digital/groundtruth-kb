NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; WI-5742 emergency-bootstrap implementation worker under DELIB-202667740/-741/-743


bridge_kind: implementation_report
Document: gtkb-wi5742-emergency-bootstrap-implementation-report
Version: 001
Date: 2026-08-01 UTC
Controlling GO: bridge/gtkb-wi5742-bound-protected-commit-evaluation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5742

target_paths: ["scripts/check_protected_commit_authorization.py", "scripts/controlled_artifact_paths.py", "scripts/implementation_authorization.py", "groundtruth-kb/src/groundtruth_kb/project/timer_config.py", "config/governance/protected-commit-timers.toml", "platform_tests/scripts/test_protected_commit_evaluation_bound.py", "platform_tests/scripts/test_bridge_publication_finalization_atomicity.py"]
implementation_scope: bounded_protected_commit_evaluation_and_stranding_prevention
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

# WI-5742 Implementation Report - Bounded Protected-Commit Evaluation

## Thread-Routing Note (why this report is not on the WI-5742 thread)

This report was intended to be filed as
`bridge/gtkb-wi5742-bound-protected-commit-evaluation-004.md`. **The bridge
publication validator lawfully refused it**, and that refusal was respected
rather than forced:

```text
RegistryAuthorizationError: invalid candidate bridge lifecycle:
INVALID_BRIDGE_TRANSITION: Invalid bridge transition NO-ACTION -> NEW
```

The WI-5742 thread's latest status is `NO-ACTION` at `-003`, filed by a Goose
session. Per the post-verdict transition table in
`.claude/rules/file-bridge-protocol.md`, the only lawful successors to
`NO-ACTION` are `GO`, `NO-GO`, and `VERIFIED` - **all Loyal Opposition-authored**.
Prime Builder therefore cannot lawfully file any status on that thread.
`DELIB-202667743` anticipated exactly this: "the bridge transition table permits
only GO, NO-GO, or VERIFIED out of NO-ACTION, all Loyal Opposition authored, so
Prime cannot lawfully self-restore the GO."

The owner's declaration made GO-002 operative for **implementation**; it did not
authorize forging an unlawful status transition, and append-only bridge
discipline was explicitly outside the bypassable set. An earlier attempt with
`Responds to: ...-002.md` was also refused (`WRONG_RESPONDS_TO_LINK`), since the
validator requires the immediate chain predecessor.

This report is therefore filed as a **sibling thread opening at `NEW`**, which is
lawful and puts the work into the Loyal Opposition queue for independent
verification. `Controlling GO:` names the operative authorization at the original
thread's `-002`.

**Two things the reviewer should note:**

1. The original thread `gtkb-wi5742-bound-protected-commit-evaluation` remains at
   `NO-ACTION`. It still needs a Loyal Opposition corrected verdict to unstick
   it. This report does not and cannot clear that.
2. The `-003` entry has not been modified or deleted and remains on disk as
   append-only audit history.

The emergency-bootstrap after-action record for this work is the separate thread
`bridge/gtkb-wi5742-emergency-bootstrap-after-action-001.md` (closed `WITHDRAWN`
at `-002`).

## Summary

The protected-commit authorization gate ran unbounded while the
bridge-publication capability it gates lived at most 120 seconds. Measured on the
live repository, the gate cost 241.664s wall / 137.969s CPU for an 812-path
staged set containing 94 protected paths - 2.01x the capability TTL. Every
governed `--finalize-verified` therefore had its capability expire mid-gate,
leaving terminal `VERIFIED` verdicts file-only with no backing commit.

Layers A and B of the approved design are implemented. The gate is now bounded
fail-closed at a configuration-sourced 110 seconds, and its measured cost fell to
a worst-observed 84.286s on the same pathological corpus and 9.9-38.7s on
realistic finalization-shaped path sets. The gate now fits inside the capability
lifetime with margin in every measurement taken.

Layer C is not implemented and is deferred - stated here plainly rather than
implied by omission. See the Scope Deviation section.

Commit: `45fedc3993130e1a23e38cfd3177d1663745678c`
(HEAD `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af` -> `45fedc399`), 7 files changed,
1410 insertions(+), 16 deletions(-).

## Implemented Changes

Layer A - fail-closed wall-clock bound
(`scripts/check_protected_commit_authorization.py`,
`groundtruth-kb/src/groundtruth_kb/project/timer_config.py`,
`config/governance/protected-commit-timers.toml`).
`evaluate()` now runs inside a monotonic `_EvaluationBudget` with per-phase
markers (`index_snapshot`, `classification`, `registry_assessment`,
`live_go_evidence`, `verified_evidence`, `transaction_evidence`, `per_path`). On
exhaustion `EvaluationBoundExceeded.as_result()` returns a deterministic deny
verdict naming the executing phase, elapsed time, configured bound, bound source,
and remediation as actionable text. The gate never passes on timeout and never
hangs. The budget is injectable so tests drive it with a fake clock rather than
real elapsed time.

The bound resolves through one new path, `timer_config.py`, with precedence
env-local -> config file -> relaxed in-code fallback. No hard-coded timer literal
is introduced outside the two documented fallback constants, per
`DELIB-202667722`. The gate bound and the capability TTL are externalized
together as an invariant-coupled pair per WI-5806, and
`resolve_protected_commit_timers` refuses to return a bound greater than or equal
to the paired TTL, and refuses a TTL above the 300s mint-time ceiling. An
unusable timer configuration is a `GateError`, never an unbounded evaluation.

Layer B1 - invocation-scoped registry snapshot cache
(`scripts/controlled_artifact_paths.py`). `registry_snapshot_cache_scope()` plus
`load_registry_snapshot_cached()`. The cache is disabled by default, so no
existing caller changes behavior - outside a scope the helper is exactly
`load_registry_snapshot`, same lock, same freshness. `evaluate()` opens the scope
for one invocation, collapsing N+1 exclusive control-plane lock acquisitions to
1. Deliberately not process-global, which the proposal rejected as a
stale-authority risk for mutating callers.

Layer B2 - packet pre-filter (`scripts/implementation_authorization.py`).
`list_named_packets` gains an optional `candidate_paths` parameter;
`candidate_paths=None` (the default) preserves the original exhaustive behavior
byte-for-byte. `_packet_cannot_authorize_any` excludes a packet from expensive
validation only on criteria that are necessary conditions for clearance: an
expired packet (rejected by `_validate_packet`, so never `valid=True`) or one
matching none of the candidate paths. An unparseable `expires_at` is admitted to
full validation so existing fail-closed reporting is preserved. Excluded packets
still emit a row with `valid=False` and a populated `error`, keeping the
fail-closed reporting surface populated.

Layer B3 - single-pass classification. `_evaluate_selected` classifies each
selected path exactly once and derives both partitions from that pass, replacing
a per-path O(n) membership re-scan. `_registry_commit_assessment` runs exactly
once per invocation and `_registry_commit_findings` delegates to it.

## Scope Deviation - Layer C Deferred

The GO'd proposal described Layer C: C-ii (late mint / commit-before-terminal
visibility) and C-iii (compensation robustness). Neither is implemented here.

Layer C lives entirely in
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`. When
implementation began, that file carried roughly 632 staged lines belonging to
WI-5758 and WI-5825, which `DELIB-202667741` did not authorize this commit to
carry; that file was consequently dropped from this change's target set.
Independently, reordering the publication transaction - the most fragile path in
the system, with five threads queued to finalize through it - under an
emergency-bootstrap exception and without independent pre-review is the scope
creep clause (a3) of
`.claude/rules/governance-emergency-bootstrap-protocol.md` forbids.

What Layer A delivers in its place is the goal of Layer C by a different
mechanism: because the accessor enforces bound < capability TTL and the bound is
enforced fail-closed at runtime, a gate can no longer outlive the capability
minted for the publication it gates. The residual - a passing gate near the bound
leaving only the remaining margin for publish-and-commit - is disclosed, not
resolved, in `config/governance/protected-commit-timers.toml` and in the
docstring of
`platform_tests/scripts/test_bridge_publication_finalization_atomicity.py`. The
two Layer-C tests in that module are skip-marked with reasons rather than stubbed
as passing, so no false coverage is claimed. Layer C is recommended as its own
governed cycle.

## Measurements

| Measurement | Wall | CPU |
|---|---|---|
| Pre-fix, 812-path staged set (94 protected), `--staged` | 241.664s | 137.969s |
| Post-fix, identical 812-path corpus, run 1 | 59.367s | 11.922s |
| Post-fix, identical 812-path corpus, run 2 | 84.286s | 14.953s |
| Post-fix, realistic 7-path staged finalization, `--staged` | 38.744s | - |
| Post-fix, realistic 7-path set, post-commit | 9.927s | - |

Controlled per-phase A/B on the identical corpus, same process, using the new
code's own backwards-compatible switches (so the "old" arm is byte-identical to
pre-WI-5742 behavior):

| Cost driver | Before | After | Factor |
|---|---|---|---|
| Classification / snapshot loads (B1) | 34.863s | 0.306s | 114x |
| Packet evidence validation (B2) | 75.467s | 1.766s | 43x |

Relationship to the 120s capability TTL - the property the work exists to
restore: before, 2.01x the TTL; after, worst observed 0.70x and realistic
0.08-0.32x.

The bound was set to 110s rather than the drafted 90s: the 812-path corpus showed
59s -> 84s run-to-run variance under concurrent control-plane lock contention,
and 90s left only 5.7s of headroom over the worst observation, which is not the
relaxed-first posture `DELIB-202667722` requires.

## Verdict-Identity Evidence

The B2 pre-filter's admission test is the clearance matcher (`path_authorized`),
so the two cannot diverge; a dedicated test asserts that equivalence across glob
shapes. Empirically, over the live 548-packet corpus:

```text
valid_packet_sets_identical: true
row_counts_identical: true
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - required (blocking) - append-only numbered
  bridge chain; no chain file was rewritten, and `-003` remains unmodified.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - required (blocking)
  - linkage carried forward from the proposal; every governing specification is
  cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - required (blocking) - the
  Spec-to-Test Mapping below is the derivation record for verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - required (blocking) - the
  project-scoped authorization chain; the PAUTH triple proceeds under it.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - required
  (blocking) - the WI-5742 source specification; operation-time enforcement is
  the property violated when a capability expires mid-operation.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - required (blocking) - governed Git
  lifecycle; this work restores a governed finalization's ability to produce a
  backing commit.
- `GOV-WORK-TREE-HYGIENE-001` - required (blocking) - the frozen-HEAD hygiene
  failure cleared by this change.
- `GOV-ARTIFACT-APPROVAL-001` - required (blocking) - no formal MemBase artifact
  is mutated; owner-approval capture is `DELIB-202667740`, `DELIB-202667741`, and
  `DELIB-202667743`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - required (blocking) - root-boundary
  containment; every target path is in-root.
- `GOV-ENV-LOCAL-AUTHORITY-001` - required (blocking) - scopes the env-local
  layer of the Layer A timer resolution precedence.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - advisory - the
  gate is a mechanical enforcement layer; its fail-closed posture is preserved
  and strengthened.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - advisory - all evidence derives from
  fresh canonical reads and measurements made this session.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - advisory - the bound, phase
  evidence, and timer resolution replace per-incident manual diagnosis with a
  deterministic surface.
- `SPEC-1662` - advisory - assertion quality: the tests assert behavioral
  outcomes, and unimplemented Layer C is skip-marked rather than falsely covered.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory - the config surface and
  phase evidence are durable artifacts.
- `GOV-STANDING-BACKLOG-001` - advisory - WI-5742 in MemBase is the sole work
  authority; no parallel authority is created.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

| Requirement source | Test | Behavior asserted | Result |
|---|---|---|---|
| WI-5742 (bound) / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | `test_delayed_evaluation_terminates_within_bound` | A delayed evaluation terminates and denies; never passes on timeout | PASS |
| WI-5742 (bound) / `DELIB-202667722` | `test_bound_is_configuration_sourced` | Precedence env-local, config file, relaxed fallback | PASS |
| WI-5806 coupling / `DELIB-202667722` | `test_bound_cannot_exceed_paired_capability_ttl` (3 cases) | A bound at or above the paired TTL is rejected by the accessor | PASS |
| WI-5806 coupling | `test_capability_ttl_ceiling_matches_mint_time_rejection` | TTL above the 300s mint ceiling rejected at config time | PASS |
| WI-5742 (fail-closed) | `test_invalid_timer_values_fail_closed` (4 cases), `test_gate_fails_closed_on_unusable_timer_config` | Malformed or invariant-violating config is a gate error, not an unbounded run | PASS |
| WI-5742 (phase evidence) | `test_bound_exhaustion_names_executing_phase`, `test_every_declared_phase_is_reportable` | Deny names phase, elapsed, bound, source, remediation | PASS |
| WI-5742 (deny semantics) | `test_evaluate_returns_deny_result_rather_than_raising`, `test_budget_does_not_fire_before_exhaustion` | Exhaustion becomes a deny verdict; no premature firing | PASS |
| WI-5742 (B1) / `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_single_snapshot_load_per_invocation` | Exactly one snapshot load per invocation regardless of path count | PASS |
| WI-5742 (B1 safety) | `test_cache_is_disabled_outside_a_scope`, `test_cache_scope_does_not_outlive_the_invocation`, `test_nested_scope_does_not_leak_into_enclosing_caller` | No caching leaks beyond one invocation | PASS |
| WI-5742 (B2) | `test_packet_prefilter_preserves_verdict` | Filtered and unfiltered agree on the valid-packet set and row count | PASS |
| WI-5742 (B2 safety) | `test_prefilter_matching_is_identical_to_clearance_matching` | Pre-filter admission equals clearance matcher across glob shapes | PASS |
| WI-5742 (B2 compat) | `test_default_enumeration_is_unchanged_for_existing_callers`, `test_corrupt_packet_row_shape_is_preserved`, `test_non_object_packet_root_is_a_clean_deny` | Default path unchanged; malformed packets stay clean denies | PASS |
| WI-5742 (B3) | `test_registry_assessment_runs_once`, `test_registry_commit_findings_delegates_to_one_assessment`, `test_classification_partitions_are_complete_and_disjoint` | One assessment per invocation; complete disjoint partition | PASS |
| WI-5742 (stranding) / `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | `test_gate_failure_leaves_no_terminal_artifact` | A bound-exhausted evaluation creates, deletes, and modifies no file | PASS |
| WI-5742 (stranding) / `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_shipped_bound_fits_inside_capability_ttl`, `test_stranding_precondition_is_unrepresentable_in_configuration`, `test_env_override_cannot_break_the_invariant`, `test_measured_gate_cost_headroom_is_documented` | Bound below TTL holds in shipped config, cannot be overridden, and exceeds worst measured cost | PASS |
| WI-5742 (deny totality) | `test_bound_exhaustion_never_clears_a_path`, `test_bound_exhaustion_is_actionable_not_a_stack_trace` | Exhaustion clears nothing; message is actionable text | PASS |
| WI-5742 Layer C (deferred) | `test_finalize_verified_near_bound_is_atomic`, `test_compensation_succeeds_after_sibling_aggregate_append` | Not implemented - explicitly skip-marked, not stubbed as passing | SKIPPED |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (authorization lock) | existing `test_check_protected_commit_authorization.py` suite | Authorization semantics unchanged by the performance work | PASS (175 of 176; 1 pre-existing failure) |

## Commands Executed

```text
python .gtkb-state/wi5742-scratch/measure_gate.py baseline-before
  -> wall 241.664s, cpu 137.969s, 94 protected, 812 selected, status fail

python -m ruff check scripts/check_protected_commit_authorization.py \
    scripts/controlled_artifact_paths.py scripts/implementation_authorization.py \
    groundtruth-kb/src/groundtruth_kb/project/timer_config.py
  -> All checks passed!

python -m ruff format --check <same four files>
  -> Would reformat: 2 files    (SEPARATE GATE - caught before filing)
python -m ruff format scripts/check_protected_commit_authorization.py \
    scripts/controlled_artifact_paths.py
  -> 2 files reformatted
python -m ruff format --check <all six changed/new .py>
  -> already formatted

python -m ruff check platform_tests/scripts/test_protected_commit_evaluation_bound.py \
    platform_tests/scripts/test_bridge_publication_finalization_atomicity.py
  -> All checks passed!

python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py \
    platform_tests/scripts/test_protected_commit_evaluation_bound.py \
    platform_tests/scripts/test_bridge_publication_finalization_atomicity.py -q
  -> 1 failed, 214 passed, 2 skipped in 120.32s

python .gtkb-state/wi5742-scratch/ab_measure.py
  -> classification 34.863s -> 0.306s; packets 75.467s -> 1.766s
  -> valid_packet_sets_identical: true; row_counts_identical: true

python .gtkb-state/wi5742-scratch/e2e_measure.py
  -> run 1: 59.367s wall / 11.922s cpu; run 2: 84.286s wall / 14.953s cpu

python scripts/check_protected_commit_authorization.py --staged
  -> 38.744s wall (7-path staged finalization)

python scripts/scan_secrets.py --staged
  -> Scanning 7 staged files; Found 0 potential secret(s); exit 0

git commit --no-verify -m "fix(governance): ..." -- <7 target paths>
  -> [research 45fedc399] 7 files changed, 1410 insertions(+), 16 deletions(-)
```

## Implementation Start Evidence

The governed path was attempted first and is reported exactly as it behaved.

Work-intent claim - SUCCEEDED, no bypass:

```text
python scripts/bridge_claim_cli.py claim gtkb-wi5742-bound-protected-commit-evaluation
  -> acquired_at 2026-08-01T00:55:57Z, acting_role prime-builder,
     project_id PROJECT-GTKB-HOUSEKEEPING-HARDENING,
     session_id bba2e933-5d36-4c5b-ad04-08a653c8700f
```

Implementation-start packet - REFUSED (authorized bypass, verbatim):

```json
{
  "authorized": false,
  "error": "Bridge thread is NO-ACTION; the prior GO is non-dispatchable. A later corrected GO is required before implementation authorization."
}
```

This is precisely the blockage `DELIB-202667743` addresses by declaring GO-002
operative. There is therefore no implementation-start packet backing this work,
and the reviewer should evaluate it on the owner declaration plus the evidence in
this report rather than on packet evidence.

Protected-commit gate at commit time - bypassed via `--no-verify` (the only gate
the owner authorized `--no-verify` for), a direct consequence of having no
mintable packet. Because `--no-verify` suppresses all pre-commit hooks rather
than only that one, every other gate was run manually and is recorded under
Commands Executed. Credential scanning was not bypassed - it was run explicitly
and the commit was made conditional on its zero-finding result.

## Regression Disclosure

A genuine regression was introduced during implementation, found, and fixed -
recorded here rather than omitted. The first B2 implementation called
`list_named_packets` with a new keyword argument; three existing tests
monkeypatch that function with the old single-argument signature, so the call
raised `TypeError`, which `_load_live_go_evidence`'s broad fail-closed `except`
swallowed into "no live GO evidence" - silently denying a path a live packet
should have cleared. That is an authorization regression, not a performance one.
The fix degrades gracefully to the exhaustive enumeration on `TypeError`. All
three tests then passed without any test being modified.

## Pre-Existing Failure (not caused by this work, proven)

`test_schema_v2_verdict_hash_passes_live_and_real_index_only_audits` fails with
`BridgeComplianceError: Verdict applicability freshness check rejected a stale
packet_hash ... for bridge/gtkb-schema-v2-index-fixture-001.md`. This was proven
pre-existing empirically, not asserted: all WI-5742 changes were backed up and
removed, HEAD versions restored, the new config file deleted, and the test re-run
- it failed identically. The work was then restored from backup. The likely cause
is the concurrent custodial sweep-commit `02e12e7b0`, which rewrote many
`bridge/` files. Test totals moved from 4 failed / 172 passed (pre-fix, including
three since-fixed regressions of mine) to 1 failed / 214 passed / 2 skipped.

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file
   (separate gates) - MET.
2. The three-module pytest run passes green - MET with one documented
   pre-existing failure proven unrelated, and two deliberate Layer-C skips.
3. A delayed evaluation terminates within the bound with a fail-closed deny
   carrying phase evidence - MET.
4. One staged evaluation performs exactly one registry snapshot load, and the
   packet phase resolves chains only for pre-filter survivors - MET.
5. Atomicity regression demonstrating atomic commit or clean failure - PARTIAL,
   disclosed: the gate-failure branch (no orphan artifact, nothing written) is
   covered; the Layer-C atomic-commit branch is deferred and skip-marked.
6. Zero new hard-coded timer literals outside the documented fallback constants -
   MET.
7. Authorization semantics unchanged for the existing suite's fixtures - MET,
   evidenced by the existing suite passing with no test modified.

## Risk And Rollback

- Bound too low. Mitigated by relaxed-first 110s (2.8x the realistic case, 1.3x
  the worst pathological observation) and by the deny message naming the slow
  phase and the tuning ceiling.
- Pre-filter dropping an authorizing packet. Mitigated by construction (both
  criteria are necessary conditions for clearance), by using the clearance
  matcher itself for admission, by a divergence test, and by live A/B showing
  identical valid-packet sets.
- Cache masking a mid-gate registry change. Bounded: the gate is a read-only
  evaluation; a consistent snapshot across it is more correct than the previous
  per-path re-reads, which could already observe different generations within one
  verdict.
- Residual stranding window. Disclosed above; Layer C is the structural removal
  and is deferred to its own cycle.
- Rollback is `git revert 45fedc399`. No MemBase mutation, no dispatcher/TAFE
  state change, no bridge chain rewrite.

## Owner Decisions / Input

1. `DELIB-202667740` - emergency-bootstrap authorization for WI-5742
   (`AUQ-20260731-WI5742-EMERGENCY-BOOTSTRAP`, answer: "Emergency bootstrap
   WI-5742 (Recommended)"). Authorizes implementing and committing WI-5742 alone
   under the emergency-bootstrap exception.
2. `DELIB-202667741` - keystone route, role, and commit scope
   (`AUQ-20260731-WI5742-KEYSTONE-ROUTE`, answer: "Re-init me as PB, commit
   includes predecessors (Recommended)"). The predecessor-carrying clause was
   ultimately not exercised: a concurrent custodial sweep-commit had already
   landed WI-5824 and WI-5823 in HEAD, so this commit contains only WI-5742 work.
3. `DELIB-202667743` - GO-002 declared operative over the malformed `NO-ACTION`
   at `-003` (`AUQ-20260731-WI5742-GO-OPERATIVE`, answer: "Declare GO-002
   operative, proceed (Recommended)"). This is the authority under which
   implementation proceeded without an implementation-start packet.
4. `DELIB-202667735` - delegated implementation mandate for the
   parallel-operation program.

## Prior Deliberations

- `DELIB-202667740`, `DELIB-202667741`, `DELIB-202667743` - the three owner
  authorizations above.
- `DELIB-202667735` - delegated implementation mandate.
- `DELIB-202667722` - timer and throttle governance with relaxed-first defaults
  and a single resolution path; direct authority for the configuration-sourced
  bound and for choosing 110s over 90s.
- `DELIB-202667721` and `DELIB-202667734` - the list-free whole-project PAUTH and
  its repair, under which the cited authorization is operative.
- `DELIB-202667723` - terminal-evidence sufficiency for expired
  implementation-start packets; the adjacent failure mode behind WI-5824's NO-GO.
- `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS` - the stranded-transaction
  recovery discipline this repair exists to stop needing.

## DISARM - KB Mechanics

This change creates and modifies source, configuration, and test files only. No
MemBase records, specifications, ADRs, DCLs, GOV records, work items, or
Deliberation Archive entries are created, updated, or retired; no
`groundtruth.db` write occurs. `kb_mutation_in_scope: false` accurately reflects
a pure source, configuration, and test change. Registry reads performed during
measurement are read-only.

## Recommended Commit Type

Recommended commit type: fix - repairs a defect (an unbounded authorization gate
whose duration structurally exceeded the capability lifetime it ran under,
stranding terminal publications and freezing HEAD) with regression coverage. The
timer-config module is remediation plumbing required to source the bound without
a hard-coded literal, not a new capability surface. The landed commit uses
`fix(governance):`.

## Loyal Opposition Verification Questions

1. Is the deferral of Layer C acceptable for this cycle, given that the coupled
   bound/TTL invariant delivers Layer C's goal by a different mechanism and the
   residual is disclosed rather than hidden?
2. Is 110s the right relaxed-first bound given 59s/84s variance on the
   pathological corpus and 9.9-38.7s on realistic sets, or should the pair be
   re-tuned once the capability TTL itself becomes configurable?
3. Is the `TypeError` fallback in `_load_live_go_evidence` the right resilience
   choice, or should an arity mismatch be a hard failure instead of a silent
   degrade to the slower path?
4. Does the pre-filter's error-channel text preserve enough diagnostic value,
   given it replaces the previous per-packet validation error text for
   non-authorizing packets?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
