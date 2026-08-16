NEW
::init gtkb lo
::open build

# Envelope Protocol Slice D Recovery - Implementation Report

bridge_kind: implementation_report
Document: gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery
Version: 003
Date: 2026-08-10 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb353-97ef-74b1-9310-09761b16938a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=not-exposed-by-host; thread_source=codex-desktop-interactive
author_metadata_source: x-codex-turn-metadata

Responds to GO: bridge/gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-002.md
Approved proposal: bridge/gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5376
Latest Bridge Status At Implementation: GO
Recommended commit type: fix

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

No KB/MemBase mutation is performed by this implementation or report.

## Implementation Claim

Implemented the approved two-path Slice D recovery. An explicit `application`
work subject now suppresses Prime Builder dispatch before either Prime
work-intent filtering or target-path filtering. The existing suppression
receipt remains deterministic, and the GT-KB infrastructure negative control
remains unsuppressed.

The canonical writer bootstrap defect was repaired by owner-authorized commit
`9c50146e2f0f88e3d98da502f93eeb0a375e9e6e`. This report is therefore eligible
for governed helper publication as
`NEW\n::init gtkb lo\n::open build` for independent verification; no hand-filed
or alternate-writer bypass is used.

## Start-Gate Evidence

- Live recovery head before mutation:
  `gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery-002.md`, GO.
- Independent reviewer session:
  `33ad40f0-18df-4414-8f55-a11ecc7ad070`, distinct from this implementation
  session.
- WI-5629 recovery prerequisite:
  `gtkb-wi5786-wi5629-false-terminal-recovery-018.md`, VERIFIED.
- Projection prerequisite:
  `gtkb-retire-ipa-refs-skill-projections-006.md`, VERIFIED.
- Capability registry: clean relative to HEAD immediately before mutation.
- Active PAUTH: version 1, operation-time evaluation `allowed` for the exact
  source/test cohort.
- Work-intent claim: row `37794`, session
  `019fb353-97ef-74b1-9310-09761b16938a`, exact thread and project.
- Schema-v3 implementation-start packet:
  `sha256:d35c64ddce374ce55b0a16f818f815f6b55ac7d862200968b69748acc205ce49`.
- Pre-start packet hash:
  `sha256:9a32e7a209b439bc46bf8e48bf3744563aeab33e93efa30761783711f33dffdb`.
- Both target paths were tracked and clean at HEAD
  `bde0203557dcc395777ec2ca31b9faa32f0fea42` before mutation; no competing
  claim was held.
- TAFE/dispatcher supervisor remained deliberately disabled under the active
  owner quiesce record. No dispatcher process or scheduled supervisor was
  enabled.

Pre-publication freshness revalidation at HEAD
`9c50146e2f0f88e3d98da502f93eeb0a375e9e6e` confirmed the latest recovery head
is still v002 `GO`; the two implementation hashes remain exactly the values
recorded below; the report planner identifies exactly two in-scope dirty files
and 944 excluded dirty paths; neither implementation path is staged; the four
forbidden/configuration paths remain clean; and TAFE remains disabled.

## Files Changed

- `scripts/dispatcher_runtime.py`
  - performs the application-subject check in the Prime selected-item branch
    before `_filter_prime_selected_by_work_intent()` and
    `_filter_prime_selected_by_target_paths()`;
  - records the same deterministic suppression result and receipt, then exits
    that recipient cycle without acquiring/releasing claims or spawning;
  - retains the prior late suppression path for non-Prime targets, avoiding an
    unrelated behavior change.
- `platform_tests/scripts/test_dispatcher_runtime.py`
  - strengthens the application-subject regression with fail-if-called
    monkeypatches on both Prime filter helpers, in addition to the existing
    acquisition, release, and spawn prohibitions.

Scoped diff: 45 insertions and 1 deletion across exactly two files. Binary diff
object hash: `3b4f710377dfc1ab585586e9247dfd4fd0a17934`.

Post-change SHA-256:

- `scripts/dispatcher_runtime.py`:
  `f78de8366906c57b30763551477987c564feabdda655347d778b11e9e988d650`
- `platform_tests/scripts/test_dispatcher_runtime.py`:
  `c010d3cc390294804e16b07b38c127ef51cf4011b5d913fa62c45a8594dc3f8e`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves independent GO, exact claim/start, report, and independent VERIFIED lifecycle.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active project PAUTH covers the exact two-path source/test change.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the authorization packet is bound to the current project, WI, GO, session, and target cohort.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the complete linked requirement set from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - every linked requirement below has executed verification evidence or an explicit observable check.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - the worker/session dispatch path retains its governed session-envelope behavior while suppression happens before Prime authorization filters.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the change preserves telemetry, GT-KB dispatch behavior, historical evidence, disabled TAFE, and unrelated shared work.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5786 and the projection prerequisite were terminal VERIFIED before implementation start.

## Specification-Derived Verification

| Governing requirement | Executed evidence | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live GO readback; exact claim row 37794; schema-v3 packet; scoped diff; report draft | Pass |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | PAUTH v1 readback plus operation-time `allowed` decision | Pass |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `implementation_authorization.py validate` on both exact targets | Pass; `authorized: true` for each |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on the operative proposal | Pass; `missing_required_specs: []`, `blocking_errors: []` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused positive/negative tests, full dispatcher file, Ruff, format, applicability, and clause preflights | Focused requirements pass; one unrelated full-file baseline failure disclosed below |
| `DCL-SESSION-ENVELOPE-DURABILITY-001` | Application suppression receipt assertions and GT-KB negative control | Pass |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Exact diff review, clean forbidden/config/registry paths, no in-scope staged files, disabled dispatcher state | Pass |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | WI-5786 v018 VERIFIED and projection v006 VERIFIED readback before start | Pass |

### Commands and Observed Results

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_application_subject_suppresses_prime_dispatch_before_acquire_or_spawn platform_tests/scripts/test_dispatcher_runtime.py::test_gtkb_subject_allows_cross_harness_dispatch_negative_control -q --tb=short
```

Result: `2 passed, 1 warning in 1.15s`.

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
```

Result: `210 collected; 209 passed; 1 failed; 1 warning in 10.60s`.
The sole failure is
`test_prime_spawn_creates_dispatch_authorization_packet_and_env`, whose direct
`_spawn_harness()` call returns `reason: all_impl_auth_quarantined`. The changed
run-cycle ordering is not invoked by that test, and `_spawn_harness()` is
outside the diff. This is disclosed as an unrelated existing authorization
fixture failure; Prime Builder does not relabel it as a pass or weaken it.

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
```

Results: `All checks passed!`; `2 files already formatted`.

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery
```

Results: applicability `preflight_passed: true`,
`missing_required_specs: []`, `blocking_errors: []`, packet hash
`sha256:19292783603f4355966e061dfe8ba94feb6e13034c40ef5c093f3cee5fc29665`;
clause gate exit 0, four must-apply clauses satisfied, zero blocking gaps.

## Acceptance-Criteria Disposition

- PASS: `application` short-circuits Prime dispatch before both filter helpers
  and worker spawn; fail-if-called tests prove the ordering.
- PASS: suppression telemetry still records reason, signature, selected and
  pending counts, document names, and work-subject metadata.
- PASS: the test is deterministic and contains no sleep, timeout race, or
  contention-dependent assertion.
- PASS: the GT-KB infrastructure negative control remains unsuppressed.
- PASS: no forbidden routing/configuration file, capability registry, skill,
  hook, database, or unrelated dirty file changed.
- PASS: WI-5786, projection, PAUTH, target cleanliness, exact claim, and
  schema-v3 start gates were all satisfied before mutation.
- PENDING independent review: disposition of the unrelated
  `all_impl_auth_quarantined` fixture failure and atomic VERIFIED finalization.

## Non-Impairment / Shared-Work Evidence

- `.api-harness/routing.toml`, `.claude/settings.json`,
  `config/dispatcher/rules.toml`, and
  `config/agent-control/harness-capability-registry.toml` remain clean at HEAD.
- Neither implementation target is staged. Three unrelated paths were already
  staged by another workstream and remain preserved outside this report. No
  Slice D commit, push, deployment, release, credential action, dispatcher
  activation, or historical bridge rewrite occurred.
- The original Slice D v001-v024 chain remains byte-preserved historical
  evidence. This recovery carrier does not revive that chain's authority.
- All 944 other dirty/untracked paths reported by the implementation-report
  planner were excluded from this implementation.

## Risks / Rollback

The early Prime suppression block intentionally duplicates the existing receipt
construction rather than refactoring unrelated dispatch paths. The remaining
risk is drift between the early Prime and late non-Prime receipt blocks; exact
receipt assertions and independent diff review cover this slice. A future
deduplication requires its own governed proposal.

Before VERIFIED, rollback is a scoped revert of only these two target paths and
a REVISED report. After VERIFIED, use a governed forward correction. Never
rewrite bridge history or absorb unrelated worktree content.

## Independent Verification Request

Loyal Opposition should independently inspect the two-path diff; rerun the two
focused tests, the full dispatcher test file, Ruff, format, applicability, and
clause preflights; verify the live claim/start evidence and all forbidden-path
invariants; independently disposition the disclosed full-file fixture failure;
and use atomic VERIFIED finalization only if every required gate passes.

## Recommended Commit Type

`fix(dispatcher): suppress application subject before prime filters`

---

When you are finished working, close your session envelope by invoking ::wrap.
