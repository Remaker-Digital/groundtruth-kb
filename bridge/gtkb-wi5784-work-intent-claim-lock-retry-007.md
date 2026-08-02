REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fbf41-5d5e-74f3-b6f4-1ae7258c299c
author_model: gpt-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5784-work-intent-claim-lock-retry
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5784-work-intent-claim-lock-retry-006.md
Historical GO: bridge/gtkb-wi5784-work-intent-claim-lock-retry-002.md

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5784
Related Work Items: WI-5841, WI-5877, WI-5881

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]
implementation_scope: test_only_deterministic_deadline_correction_with_existing_source_retained_as_verification_cohort
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation or MemBase write, insert, change, or edit is in scope.

current_live_predecessor_sha256: E981D831CD1803A8135911E47556BFF17A3379793AC3F11BCC904AC6660B3372

# REVISED Corrective Proposal — Deterministic Work-Intent Deadline Exhaustion

## Implementation Authority Boundary

This REVISED proposal creates no implementation-start authority, source/test
mutation, or dispatcher/TAFE action. The Prime Builder re-read strict latest
state, exact predecessor bytes, PAUTH/project/WI state, claims, target hashes,
and overlap heads; acquired the lawful exact draft claim; reran candidate gates;
and filed only through the governed Prime Builder writer. Before any protected
target edit, an independent Loyal Opposition session must publish a fresh GO
and the implementing Prime Builder must acquire the exact GO claim and a valid
schema-v3 start packet.

The v002 GO is historical evidence for the already-landed acquire/release
implementation. It is not claimed as authority for this newly specified test
correction.

## Revision Claim

Correct the deterministic-test gap exposed after v006 without rewriting the
existing acquire/release implementation. Canonical WI-5784 v11 records two
independent isolated repetition sets for
`test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim`:
5 PASS / 5 FAIL and 4 PASS / 2 FAIL. Every failure stopped at the old line 970
because the production code lawfully reached the pre-SQLite
`monotonic write deadline exhausted` branch with
`sqlite_errorcode=None`, `sqlite_errorname=None`, and
`phase=begin_immediate`; downstream no-partial-claim and closed-connection
assertions consequently never ran.

The correction splits two legitimate exhaustion paths into deterministic
nodes. The existing real-SQLite lock node retains BUSY/LOCKED-code coverage but
uses an injected logical clock and retry-sleep advancement instead of elapsed
wall time. A new no-competing-writer node supplies an already-exhausted test
deadline and proves the pre-SQLite typed result, no partial claim, rollback,
and connection closure. Production source behavior is retained unchanged.

WI-5881 remains the sole owner of its new recovery reservation claim-fence CAS
node. This proposal neither names nor invokes that primitive and claims no
completion of TEST-11809.

## Requirement Sufficiency

Existing requirements sufficient. WI-5784 v11 now
states the exact observed branch and correction. No new production timer,
retry policy, role authority, claim-fence state, dispatcher contract, or owner
decision is introduced. Test-only logical-clock inputs do not become operational
timer defaults; all production timer externalization and recurring tuning remain
governed by `DELIB-202667722` and the standing timer work.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only role-correct bridge lifecycle, fresh independent GO, exact claim, and governed publication.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserve the new repeatable failure evidence in the existing WI rather than a duplicate carrier.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — keep the decision, scope, evidence, and verification mapping in governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — treat the repeated flake as a corrective lifecycle trigger without falsely closing the WI.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — bind the corrective implementation plan to concrete specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — require independent execution of both deterministic branches before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — preserve exact project, work item, PAUTH, and two-target metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — require fresh operation-time evaluation of the active inherited project PAUTH.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — WI-5784 remains an active member of the approved Advisory Corrections project.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — no stale v005 packet or historical GO substitutes for current start authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — re-read exact claims and target/overlap heads at filing, review, and start.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — replace wall-clock race dependence with injected monotonic state and deterministic transitions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keep the correction on the shared GT-KB platform registry, not an adopter application.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — retain one shared registry/test contract for all harnesses rather than a Codex-only branch.
- `GOV-STANDING-BACKLOG-001` — retain WI-5784 as the sole baseline carrier and link, rather than duplicate, WI-5881.
- `SPEC-AUQ-POLICY-ENGINE-001` — no owner question is necessary where current authority and exact evidence determine the bounded correction.
- `GOV-10` — exercise the public `acquire()` behavior against real SQLite, including one real-lock branch.
- `GOV-12` — land the focused deterministic regression tests with the governed correction.
- `SPEC-1662` — assert observable success/failure diagnostics, no partial mutation, rollback, and closure.
- `GOV-15` — perform no dispatcher/TAFE action, external mutation, or autonomous cleanup.

## Prior Deliberations

- `DELIB-20260730-WI5784-GOVERNED-PROCESSING-APPROVAL` — owner approval for governed WI-5784 processing under its parent project; normal review/start/verification gates remain mandatory.
- `DELIB-202667722` — timer and throttle governance requires evidence-based, externally governed production values and recurring tuning.
- `DELIB-202666542` — prior work-intent claim-state review evidence carried by the original proposal.
- `DELIB-202666965` — prior review-authority packet evidence carried by the original proposal.
- `DELIB-202666916` — prior governed predecessor/diagnostic proof evidence carried by the original proposal.
- `DELIB-202667002` — prior missing-target finalization evidence carried by the original proposal.
- `DELIB-202665288` — prior lifecycle-protocol foundation evidence carried by the original proposal.

A semantic Deliberation Archive search for `WI-5784 work intent acquire release
contention monotonic deadline exhaustion` initially exceeded a 34-second process
bound and then completed under a generous retry. The relevant new result was
`DELIB-202667722`; no new decision record is needed for this bounded correction.

## Owner Decisions / Input

No new owner input is required. Project-scoped implementation approval is
inherited by WI-5784, and canonical WI-5784 v11 already directs the exact
baseline stabilization. This proposal does not expand the project's allowed
mutation classes or bypass the independent GO, exact claim, schema-v3 start,
report, or independent verification gates.

## Findings Addressed

### F1 — Implementation authorization not live for declared targets (P0)

Accepted. V005's expired packet is not reused. Because new v11 evidence adds a
test correction after the implementation report, v007 returns the delta to a
proposal state and requests a fresh independent GO. No target edit may occur
until current strict v007 is GO, the exact current-session GO claim is active,
and a schema-v3 start packet validates the active inherited PAUTH against both
declared paths. The source path is retained in the packet cohort to verify the
existing implementation and the exact foreign hunk; this delta plans no source
mutation.

### F2 — Implementation evidence otherwise green (informational)

Preserved as historical evidence, not overstated as current verification. The
existing acquire/release implementation and previously passing focused suite
remain the baseline. After the deterministic test correction, all focused tests,
lint, format, compile, exact target hashes, claim state, and overlap heads must
be rerun and reported factually before independent verification.

### F3 — Repeated deadline node is nondeterministic (new v11 evidence)

Accepted and corrected in the design. The old test combines a real writer lock
with a 0.1-second wall-clock deadline, so either of two valid branches can win:
SQLite can first emit BUSY/LOCKED metadata, or the remaining-budget check can
expire before the next SQLite statement. An assertion that every run has a
non-null SQLite code is therefore invalid.

The implementation adds or refactors the following two exact behavioral nodes:

1. **Deterministic real-SQLite contention exhaustion.** Retain the isolated
   database and real second-connection `BEGIN IMMEDIATE` blocker. Inject a
   logical monotonic clock and make `_retry_sleep` advance that clock without a
   wall-clock sleep. The fixture advances to the configured test deadline only
   after at least one real SQLite BUSY/LOCKED result, forcing the
   `last_contention` exhaustion branch. Assert typed
   `WorkIntentWriteContentionError`, `operation=acquire`,
   `phase=begin_immediate`, `contention_exhausted is True`, a BUSY/LOCKED
   `sqlite_errorcode`, no partial claim, exact database path, and closure of
   every opened connection.
2. **Deterministic pre-SQLite already-exhausted exhaustion.** Prepare an
   isolated database, use no competing writer, then inject a stable monotonic
   clock and an already-spent test deadline before `acquire()` enters
   `BEGIN IMMEDIATE`. Wrap the post-schema connection in a narrow recording
   proxy. Assert exactly one attempt; typed
   `WorkIntentWriteContentionError`; `operation=acquire`;
   `phase=begin_immediate`; `contention_exhausted is True`;
   `sqlite_errorcode is None`; `sqlite_errorname is None`; detail contains
   `monotonic write deadline exhausted`; no retry/sleep; no
   `BEGIN IMMEDIATE`; rollback attempted; connection closed; and a fresh
   independent read finds zero claim rows for the slug.

The production `_run_write_transaction`, `_deadline_exhausted_error`, acquire,
release, holder revalidation, retry/backoff constants, and schema behavior are
not modified by this correction.

## Exact Scope, Baselines, And Hunk Ledger

| Path | Current SHA-256 | Bytes | v007 disposition |
| --- | --- | ---: | --- |
| `scripts/bridge_work_intent_registry.py` | `633E22ACFF0E6E5B9964827CCAC40A3299D7FD513918F24C90469AC9A338F1E3` | 61,892 | Retained implementation/verification target; no v007 source hunk. Current working bytes contain WI-5877's sole foreign removal of `or os.environ.get("CODEX_HOME")`; do not rewrite, rebase, adopt, or attribute it to WI-5784. |
| `platform_tests/scripts/test_bridge_work_intent_registry.py` | `F886F15E229BA1BC56E7C2513F67772031459B14A5C49A7C8A258CA23158A5AB` | 47,461 | Clean WI-5784 test baseline; the only planned v007 implementation hunk is the two-node deterministic deadline correction above. |

The source preimage and foreign hunk are evidenced by current WI-5877 carrier
v005: recorded committed baseline
`792F3FB422706F40819C443EB691EC90874B68C13209030AB7D8FBD2F9484655`
and current working hash `633E22...F1E3`, with the exact one-line
`CODEX_HOME` disjunct removal. No Git/index operation is used or authorized by
this proposal. Any source hash change, any additional source hunk, or any test hash
change before future implementation stops the cycle and requires a fresh
ledger/revision.

## Exact Current Overlap Check And Sequencing

A latest-file exact `target_paths` scan found three external current
target-bearing chains containing either declared WI-5784 path. Strict lifecycle
resolution reports each at v005 `REVISED` with no blocking diagnostic:

| Chain | Exact overlap | Current hash / claim | Disposition |
| --- | --- | --- | --- |
| `gtkb-wi584x-codex-home-harness-selector-false-positive` (`WI-5877`) | source only | `123C872537F1F22DA8E69746FCC35BB2A7A005CA01CE80AC1411CD2830336258`; claim null | Owns only the current one-line selector hunk and its separate role-eligibility test. WI-5784 performs no source mutation and preserves those bytes. |
| `gtkb-wi5841-harness-selector-registry-derived` (`WI-5841`) | source and test | `1F2EA995554F909C470B604B088AFCFD7E2F4F05B8D79ADE00CEDABA87163836`; claim null | Its own v005 requires WI-5784 to terminalize or be exactly ledger-separated. WI-5784 lands its isolated test hunk first; WI-5841 re-observes afterward. |
| `gtkb-wi5881-durable-cross-process-bridge-recovery-reservations` (`WI-5881`) | source and test | `B36E0146371D91F8BA9C430DDBF61D2C0B7F055A7BA027B34F61273813C30569`; expired draft claim only | Its v005 explicitly leaves ordinary acquire baseline repair to WI-5784 and owns only the new recovery claim-fence node. WI-5881 waits for WI-5784 terminalization or a separately accepted exact hunk ledger. |

WI-5784 filing acquired exact draft claim row 36241 under Prime Builder session
`019fbf41-5d5e-74f3-b6f4-1ae7258c299c`; governed publication is expected to
release that claim after success. Historical
chains that merely cite these paths are not exact current `target_paths`
overlaps. Fresh strict heads, hashes, and claims remain mandatory at filing,
review, and implementation start.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "behavioral_change": "replace one scheduler-racy deadline test with two deterministic observable exhaustion branches",
  "production_source_change": false,
  "real_sqlite_contention_retained": true,
  "pre_sqlite_exhaustion_covered_separately": true,
  "wi5881_claim_fence_scope_included": false,
  "dispatcher_or_tafe_mutation": false,
  "git_or_index_mutation": false
}
```

The work-intent registry is one shared platform service. Both deterministic
nodes exercise harness-neutral SQLite behavior; there is no Claude, Codex,
Cursor, Goose, or dispatcher-specific test branch. The already-spent branch is
named by the observable deadline state, while the real-lock branch retains
SQLite metadata coverage. This makes the tests explain the two production
outcomes instead of encoding scheduler timing as a hidden oracle.

No hard-coded production timer is added. Test-only injected deadline/clock
state remains local to the deterministic fixture. Timer externalization and
tuning stay with the standing governed timer program.

## Specification-Derived Verification Plan

| Requirement | Exact verification |
| --- | --- |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`, `GOV-10`, `SPEC-1662` | Run the real-lock node repeatedly in isolated processes; every run must take the BUSY/LOCKED-code branch with logical-clock exhaustion and leave no claim. Run the no-writer already-exhausted node repeatedly; every run must take the `sqlite_errorcode=None` branch without executing `BEGIN IMMEDIATE`. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Assert each real-lock retry uses a fresh connection and preserves exact current holder semantics; independently reopen the database after both failures and observe zero partial claim for the tested slug. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-12` | Record node names, commands, repetition counts, pass/fail totals, and exact post-change target hashes in the implementation report; independent LO reruns them before VERIFIED. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, project authority DCLs | Revalidate strict latest, active inherited PAUTH, exact GO claim, schema-v3 packet, and two-target cohort before any protected edit. |
| Cross-harness / non-impairment | Run the full focused registry module plus adjacent work-intent role-eligibility suite; no harness-specific waiver or selector mutation is allowed. |
| `GOV-15` | Confirm no dispatcher/TAFE, Git/index, raw database, credential, deployment, release, or external-system mutation occurred. |

Planned post-GO commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py::test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
```

The final node name may distinguish the real-lock and pre-SQLite cases, but the
implementation report must map both exact behaviors and may not delete either
coverage branch.

## Acceptance Criteria

1. Production source remains byte-for-byte `633E22...F1E3` throughout this
   corrective implementation unless a fresh independently reviewed revision
   explicitly changes that boundary; WI-5877's selector hunk is preserved and
   never attributed to WI-5784.
2. The existing real-SQLite lock exhaustion node uses a logical clock rather
   than wall-clock competition and deterministically reports BUSY/LOCKED code
   metadata, typed exhaustion, no partial claim, and closed connections.
3. A distinct no-competing-writer already-exhausted node deterministically
   reports `sqlite_errorcode=None`, `sqlite_errorname=None`,
   `phase=begin_immediate`, one attempt, typed `contention_exhausted`, no
   retry/sleep or `BEGIN IMMEDIATE`, rollback, closure, and zero partial claim.
4. Existing acquire success, per-attempt holder revalidation, release
   replacement-holder preservation, missing-release idempotence,
   non-retryable failure, and narrow-schema tests stay green.
5. WI-5881's recovery claim-fence CAS node and TEST-11809 remain entirely out
   of scope; no production reservation/fence code or event is added here.
6. Fresh currentness, PAUTH, overlap, claim, schema-v3 start, focused tests,
   formatting, lint, compile, and canonical readback evidence is recorded in a
   later factual implementation report before independent verification.
7. Dispatcher/TAFE stays disabled and untouched; no Git/index operation,
   publication, deployment, credential, destructive cleanup, or external
   system action occurs.

## Pre-Filing Preflight Subsection

Candidate results on the exact proposal bytes are gate-clean:

- applicability: PASS; no blocking errors, missing required specs, missing
  advisory specs, missing parent directories, author warnings, or unclassified
  target paths; active PAUTH v6 operation-time evaluation allows both exact
  paths for packet creation and implementation start;
- mandatory clause gate: PASS; five clauses evaluated, three `must_apply`, two
  `may_apply`, zero must-apply evidence gaps, and zero blocking gaps;
- phantom-spec sweep: PASS; all 20 cited specification IDs resolve in MemBase;
- proposal pattern lint: PASS with zero findings;
- WI collision/relationship check: PASS; WI-5784 is the declared item and
  WI-5841/WI-5877/WI-5881 are valid related items with no collision or
  relationship error;
- strict currentness: PASS on predecessor v006 `NO-GO`, SHA-256
  `E981D831CD1803A8135911E47556BFF17A3379793AC3F11BCC904AC6660B3372`,
  with no lifecycle blocking diagnostic.

Applicability packets are content-hash sensitive, so the final packet hash is
reported with the exact final proposal SHA rather than recursively embedded in the
candidate. All gates and exact physical/current authority checks must be rerun
after any byte or invalidation-input change and immediately before live filing.

## Risk And Rollback

Risk is low-to-moderate: the planned protected mutation is test-only, but a bad
clock fixture could make the suite prove a mock rather than production behavior.
The mitigation is to retain one real SQLite second-connection lock and inject
only monotonic observation/sleep advancement; the separate no-writer node
proves the pre-SQLite path explicitly.

This proposal changes no protected target. Its numbered bridge artifact is
append-only and is not deleted by rollback. After a future GO, implementation
rollback reverts only the exact WI-5784 test hunk under new authority. It must not alter
the source file, WI-5877's selector hunk, any WI-5881 reservation/fence work,
bridge history, claims owned by another session, dispatcher/TAFE state, or the
foreign Git index lock.

## Files Expected To Change After Future GO

- `platform_tests/scripts/test_bridge_work_intent_registry.py` — deterministic
  two-branch deadline test correction only.

The declared source target remains in the authorization and verification cohort
to bind the existing implementation preimage, but v007 plans no source hunk.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
