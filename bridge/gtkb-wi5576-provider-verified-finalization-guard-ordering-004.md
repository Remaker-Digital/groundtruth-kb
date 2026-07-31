REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - Preserve Full Compliance After VERIFIED Finalization Evidence

bridge_kind: prime_proposal
Document: gtkb-wi5576-provider-verified-finalization-guard-ordering
Version: 004
Responds to: bridge/gtkb-wi5576-provider-verified-finalization-guard-ordering-003.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5576

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Narrow the provider `VERIFIED` publication repair without dropping or
replicating any bridge-compliance rule.

`publish_lo_verdict` currently invokes both provider guards before entering
the canonical atomic finalizer. The bridge-compliance guard therefore sees
the provider body before the finalizer has appended mandatory Commit
Finalization Evidence and denies a body that only the finalizer can complete.

The revised mechanism splits only the timing of those already-required
guards:

1. Provider `VERIFIED` runs `scanner-safe-writer.py` before finalization.
2. The canonical finalizer appends deterministic Commit Finalization Evidence.
3. The finalizer calls `write_bridge_file` with the evidence-complete bytes.
4. `write_bridge_file` invokes `run_bridge_compliance_audit`, so the complete
   bridge-compliance gate still runs before any verdict write or commit.
5. `GO` and `NO-GO` retain the existing two-guard pre-write sequence unchanged.

This does not defer the whole compliance gate past the write. It moves the
single full compliance evaluation for provider `VERIFIED` to the existing
evidence-complete canonical write chokepoint.

The earlier description of this defect as a recurrence of WI-5040 is removed.
WI-5576 is a provider-writer guard-ordering defect, not a dispatcher
capability-routing defect.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`

## Requirement Sufficiency

Existing requirements remain sufficient. WI-5576, TEST-11623, the active
project PAUTH, the atomic VERIFIED finalization contract, and the bridge
authority specifications define the complete correction. No new formal
requirement or owner decision is needed.

## In-Root Placement Evidence

All declared targets are within the GT-KB root:

- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch`

## Owner Decisions / Input

No new owner decision is required. The active project authorization is
`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`, backed by
owner decision `DELIB-202666274`. Its separate prohibitions on dispatcher
mutation, credentials, destructive cleanup, push, deployment, and release
remain unchanged.

## Prior Deliberations

- `DELIB-20265334` - WI-4680 atomic VERIFIED finalization GO; establishes that
  the verdict and verified path set form one transaction, with pre-commit
  evidence in the verdict and the final SHA emitted after commit.
- `DELIB-202666183` - provider verdict-denial-loop review context; requires
  bounded governed publication without weakening verdict gates.
- No prior deliberation authorizes skipping the bridge-compliance gate or
  treating WI-5576 as a dispatcher capability-routing change.

## Findings Addressed

### Finding 1 (Blocking): deferring the whole compliance gate drops Applicability-Preflight enforcement

The revision does not defer or remove the complete compliance gate. The
canonical finalizer already appends Commit Finalization Evidence and then
calls `scripts.gtkb_bridge_writer.write_bridge_file`; that function runs
`run_bridge_compliance_audit` on the final evidence-complete content before
creating the numbered verdict file. The implementation will preserve this
existing chokepoint.

The new regression must use the real compliance path rather than mocking
`_run_provider_verdict_guards` wholesale. It will prove that a provider
`VERIFIED` body without a clean Applicability Preflight remains denied by the
finalizer's `write_bridge_file` call, creates no verdict or commit, and retains
the claim. A valid body that lacks only pre-authored Commit Finalization
Evidence must reach the finalizer, receive that deterministic section, pass
the full compliance gate, commit atomically, and release the claim exactly
once.

The alternative of duplicating the finalizer's private evidence builder in
the provider writer is intentionally rejected. The existing finalizer remains
the single authority for evidence construction and the existing
`write_bridge_file` path remains the single authority for evidence-complete
bridge compliance.

### Finding 2 (Non-blocking): shared writer target carried concurrent metadata work

The concurrent writer work is now committed and the three WI-5576 targets
were clean at revision preparation. That observation is not implementation
authority. Prime Builder must re-run exact target status and diff checks
immediately before claim and implementation start. Any foreign dirty byte
fails closed.

Implementation remains hunk-isolated: the patch artifact must identify only
the reviewed WI-5576 writer hunk, include its exact hash and size in the later
implementation report, and pass forward/reverse Git apply checks. No metadata,
model-provenance, applicability-service, dispatcher, or provider retry hunk is
attributable to WI-5576.

## Revised Scope

- Add a bounded provider-guard selection mechanism in
  `scripts/gtkb_bridge_writer.py`.
- For `VERIFIED`, run scanner-safe credential validation before the atomic
  finalizer and rely on the finalizer's evidence-complete `write_bridge_file`
  call for the full bridge-compliance gate.
- For `GO` and `NO-GO`, preserve both existing provider guards before
  `write_bridge_file`.
- Preserve role, transition, author metadata, exact claim, hunk integrity,
  include-path, finalizer, rollback, and claim-release checks.
- Add focused tests to
  `platform_tests/scripts/test_lo_verified_commit_atomicity.py` proving the
  successful ordering and the missing-applicability fail-closed path.
- Create only the exact reviewed hunk carrier under
  `bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch`.
- Do not modify the canonical finalizer, either bridge-compliance hook copy,
  provider harnesses, dispatcher configuration/runtime, TAFE, leases, roles,
  eligibility, routing, caps, allowances, credentials, or unrelated files.

## Start Conditions And Shared-File Sequencing

Implementation may begin only when all conditions hold simultaneously:

1. The latest thread status is an independent `GO` on this revision.
2. The active project PAUTH still covers WI-5576 and all exact target paths.
3. No active work-intent claim exists for this slug; Prime acquires one exact
   claim and a schema-v3 implementation-start packet.
4. `git status --short --` and `git diff --` show no foreign bytes on the
   source, test, or hunk targets immediately before implementation start.
5. Operation-time authorization returns `authorized: true` immediately before
   each protected mutation.
6. A current live worker or another governed slice does not own an overlapping
   target or hunk.

If any condition fails, implementation stops without editing, staging,
committing, or changing dispatcher/TAFE state.

## Pre-Filing Preflight Subsection

The governed revision helper's candidate applicability preflight evaluated the
completed v004 content before live filing.

Observed result: `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, and
`blocking_errors: []`.

The governed revision helper's mandatory candidate clause preflight evaluated
the same completed v004 content before live filing.

Observed result: five clauses evaluated, four `must_apply`, zero must-apply
evidence gaps, zero blocking gaps, exit 0.

## Specification-Derived Verification Plan

| Specification | Required verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | TEST-11623, focused provider atomic-finalization tests, and a fresh substantive F dispatcher review after independent verification. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Prove evidence-complete `write_bridge_file` still invokes the full compliance gate; run existing transition, role, self-review, claim, and append-only tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve WI-5576, TEST-11623, numbered proposal/verdict/report artifacts, and exact implementation evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live applicability preflights must pass with no missing required specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Map every linked specification to executed focused/adjacent tests in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Read back active PAUTH, project membership, WI-5576, TEST-11623, and exact targets before implementation. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Candidate and live preflights must pass; no new owner decision may be inferred. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Exact target resolution and `git diff --check` must prove all artifacts remain in-root. |
| `GOV-STANDING-BACKLOG-001` | WI-5576 remains the single hygiene carrier for this guard-ordering defect. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact target status/diff checks must be clean before claim/start; implementation report must disclose excluded foreign paths. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Self-enforce GO, claim, start, and operation-time target validation before mutation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Preserve the complete proposal, review, implementation, test, verification, and commit evidence chain. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | File a NEW implementation report and require independent VERIFIED before focused finalization. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Validate exact hunk hash/size, forward/reverse applyability, and final candidate evidence before VERIFIED. |

Focused behavioral cases:

1. A valid provider `VERIFIED` body lacking only Commit Finalization Evidence
   runs scanner-safe validation, reaches the finalizer, gains the deterministic
   section, passes full bridge compliance, writes once, commits the exact path
   set, and releases the claim once.
2. A provider `VERIFIED` body without a clean Applicability Preflight reaches
   the evidence-complete compliance chokepoint but is denied before verdict or
   commit; the claim remains held.
3. `GO` and `NO-GO` still invoke both configured provider guards before write.
4. Invalid status/body combinations, unsafe include paths, missing hunk
   coverage, fabricated evidence, self-review, finalization failure, and commit
   failure remain fail closed.

Required commands include:

- `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short`
- the focused provider-writer and bridge-compliance suites selected by the
  implementation diff;
- `ruff check` and `ruff format --check` on all source/test targets;
- `python -m py_compile scripts/gtkb_bridge_writer.py`;
- exact hunk integrity checks and `git diff --check`.

## Acceptance Criteria

- Provider `VERIFIED` no longer fails merely because Commit Finalization
  Evidence is absent before entering the component that creates it.
- Scanner-safe credential validation still runs before finalization.
- Full bridge compliance runs on evidence-complete bytes before the verdict
  write and still rejects a missing or failing Applicability Preflight.
- `GO` and `NO-GO` retain both existing pre-write provider guards.
- Atomic finalization creates the exact focused local commit or rolls back the
  verdict; claim release occurs exactly once only after success.
- No dispatcher/TAFE/harness configuration or non-WI-5576 hunk changes.
- Focused and adjacent suites, Ruff, compile, hunk integrity, and diff checks
  pass before independent verification.

## Risk And Rollback

The main risk is accidentally converting a timing repair into a governance
bypass. The explicit missing-applicability regression and use of the existing
`write_bridge_file` chokepoint prevent that failure mode. Hunk-isolated
implementation prevents attribution of concurrent writer changes.

Rollback reverts only the exact reviewed WI-5576 source/test hunk. Numbered
bridge artifacts remain append-only. Rollback does not mutate dispatcher
configuration/runtime, TAFE, leases, roles, eligibility, routing, caps,
allowances, credentials, push, deployment, or release.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `bridge/hunks/gtkb-wi5576-provider-verified-finalization-guard-ordering.patch`

## Recommended Commit Type

`fix`
