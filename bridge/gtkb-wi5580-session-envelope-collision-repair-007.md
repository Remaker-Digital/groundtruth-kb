REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; desktop interactive; Prime Builder; non-live correction draft; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: transcript-defined role and current Codex desktop session

# Prime Builder REVISED Correction Proposal - WI-5580 Explicit Environment Isolation

bridge_kind: prime_proposal
Document: gtkb-wi5580-session-envelope-collision-repair
Version: 007
Responds to: bridge/gtkb-wi5580-session-envelope-collision-repair-006.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5580
Linked Test: TEST-11627
target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/collect_modernization_semantic_evidence.py", ".claude/hooks/workstream-focus.py", "platform_tests/scripts/test_collect_modernization_semantic_evidence.py", "platform_tests/scripts/test_kb_attribution_session_role.py", "platform_tests/hooks/test_workstream_focus.py"]
Recommended commit type: fix:

## Revision Claim

Version 006 identifies a valid trust-boundary defect. An explicitly supplied empty environment mapping is caller-owned input and must remain empty; it must not be replaced by ambient process state merely because the mapping is falsey. The correction must apply both to the shared acting-harness selector and to the two modernization collector entry points that forward environment state into that selector.

This REVISED artifact requests independent Loyal Opposition approval for a bounded correction inside the existing six-path WI-5580 cohort. It is a correction proposal, not an implementation report. No protected source or test edit is claimed or authorized by this draft.

## Response To Version 006

### Finding F1 - Explicit empty mappings consume ambient process state

**Accepted.** Current `groundtruth-kb/src/groundtruth_kb/session/envelope.py` line 227 uses:

```python
env = dict(environ or os.environ)
```

An explicit `{}` is falsey, so a recognized ambient marker is silently consumed. A sterile reproduction against the current bytes observed both prohibited outcomes:

```text
resolve_acting_harness_identity(root, environ={})
=> ('codex', 'A')

resolve_acting_harness_identity(
    root,
    environ={},
    harness_name='claude',
    harness_id='B',
)
=> EnvelopeError: Runtime marker selects harness 'codex', but explicit identity selects 'claude'.
```

The first call should fail because neither a runtime marker nor an explicit producer was supplied. The second should resolve the explicit durable producer `claude` / `B` without consulting ambient markers.

### Scope-completeness correction - Two forwarding sites have the same falsey fallback

The v006 example is in the shared selector, but current inspection found the same semantic defect in the already-approved collector target:

- `resolve_runtime_provenance()` at `scripts/collect_modernization_semantic_evidence.py:496`.
- `Collector.__init__()` at `scripts/collect_modernization_semantic_evidence.py:524`.

Those two sites now feed the selector introduced by WI-5580. Correcting only the inner selector would leave the public collector entry points able to replace an explicit empty mapping before the selector sees it. This revision therefore applies the same `None`-only fallback at all three sites. This is not a new target or a new capability; it closes the exact environment-isolation boundary inside two of the six already-approved paths.

## Current Exact State

- Physical bridge latest: `bridge/gtkb-wi5580-session-envelope-collision-repair-006.md`, status `NO-GO`, SHA-256 `5871C3703A902A677AAAD88A5959786616CADA510C71765644D6D24C35096C56`.
- The six target files remain byte-exact to v005's reported snapshot: `313 insertions, 13 deletions`; no concurrent WI-5580 correction is present.
- Current focused matrix: `111 passed, 3 skipped, 2 failed` in 6.37 seconds. The two failures are the already-disclosed duplicated modernization memberships and absent historical corpus manifest; neither exercises the missing explicit-empty regression.
- Current work-intent claim status: `null`.
- The active project is `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`; WI-5580 is an active project member.
- Active list-free project authorization v5 has no work-item inclusion list, exclusion list, or expiry and allows this proposal's bridge, source, test, configuration, metadata, and governance-evidence classes. The legacy WI `approval_state` field is not operation-time implementation authority.

## Claim And Implementation-Start Boundary

The live thread is latest `NO-GO`. A fresh `go_implementation` claim cannot be acquired from that state because there is no current independent `GO` authorizing correction writes. The packet previously created from GO v004 is historical/evidence-only for this revision and must not be treated as permission to edit after v006.

The required sequence is:

1. File this complete v007 as `REVISED` through the governed physical/typed bridge path without TAFE or dispatcher activation.
2. Receive a new independent Loyal Opposition `GO` on v007.
3. Recheck the exact six-path cohort for byte drift and overlapping live claims.
4. Acquire a fresh exact `go_implementation` work-intent claim.
5. Create a fresh implementation-start packet from the new GO and active Assurance PAUTH v5.
6. Apply only the approved correction hunks, execute the full verification plan, and file a corrected implementation report as the next lawful post-GO `NEW` entry.

No protected edit may occur before steps 2 through 5 succeed.

## Publication-Recovery Boundary

The v005 physical report remains bound to typed publication capability row 822 in `recovery_required` state. The exact pending sidecar remains:

`.gtkb-state/bridge-publication-pending/gtkb-wi5580-session-envelope-collision-repair-005-7079b5644cd1966e.json`

Its SHA-256 is `1E35532FA6E53F982A938FE9E1F8A4CE1A94E31A8221E024EED2A8C14DAB70BD`. The capability's failure reason is `bridge publication aggregate preimage cannot be restored exactly`. Version 006 has no matching publication-capability row.

This revision does not delete, rewrite, compensate, finalize, or otherwise mutate that recovery evidence. Generic publication-capability recovery and attested receipt work remain delegated to WI-5825. Filing or implementation of WI-5580 must preserve the sidecar and recovery row exactly; no direct database or registry edit is permitted.

## Cross-Harness Disposition

- **Claude:** `.claude/hooks/workstream-focus.py` remains verification-only and
  byte-preserved. Its focused test must prove the shared selector correction
  does not change Claude workstream-focus behavior except to honor an explicit
  empty caller environment.
- **Codex:** the shared `envelope.py` selector and collector correction applies
  directly to Codex runtime markers; sterile-environment and explicit-producer
  regressions must cover Codex ambient-marker non-consumption.
- **Cursor, Antigravity, Ollama, OpenRouter, and Goose:** no harness-specific
  hook or configuration target changes. These harnesses consume the same
  vendor-neutral None-versus-empty selector contract, so behavioral parity is
  preserved through the shared source and exact regression matrix. No typed
  waiver or harness exclusion is requested.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - environment and runtime markers may select an envelope document but never grant role authority.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - existing exact-session documents and collision evidence remain immutable.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the correction must not impair any harness, dispatcher path, or normal workflow.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - environment isolation and fail-closed selection require executable regressions.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - project, claim, bridge, and publication-state claims use fresh canonical reads.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bound to active project-level authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - active PAUTH must be reevaluated at the new start and finalization operations.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the new implementation-start packet must bind the new GO and exact six paths.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - WI-5580 remains linked to live requirement authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization cannot bypass independent GO, claim, start, report, or verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this Prime Builder revision requests independent review and preserves the numbered file chain.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, and work-item linkage are explicit above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the correction and tests are mapped to governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute the exact environment-isolation regressions and carried-forward matrix.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the three semantic changes and exact tests remain independently evaluable.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - the six-path cohort and WI-5825 recovery ownership are kept distinct.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, reproduction, correction, tests, and report remain linked to WI-5580 and TEST-11627.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - NO-GO correction proceeds through REVISED, new GO, implementation report, and VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable bridge, project, test, and recovery evidence control completion.

## Requirement Sufficiency

Existing requirements sufficient. The requirement is already implied by `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ENVELOPE-DURABILITY-001`, `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`, and TEST-11627: explicit caller input must not be replaced by unrelated ambient process state. Version 006 supplies the missing edge-case evidence; no new or revised formal requirement is necessary before this bounded correction.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "baseline": {
    "six_path_state": "Current bytes remain the exact v005 implementation cohort with no concurrent correction.",
    "focused_matrix": "111 passed, 3 skipped, and 2 disclosed unrelated baseline failures.",
    "sterile_environment_reproduction": "environ={} consumes an ambient Codex marker and falsely conflicts with an explicit Claude/B producer."
  },
  "provenance": {
    "work_item": "WI-5580",
    "linked_test": "TEST-11627",
    "source_no_go": "bridge/gtkb-wi5580-session-envelope-collision-repair-006.md"
  },
  "canonical_authority": [
    "GOV-SESSION-ROLE-AUTHORITY-001",
    "DCL-SESSION-ENVELOPE-DURABILITY-001",
    "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
  ],
  "primary_route": "REVISED v007, independent GO, fresh exact claim, fresh implementation-start packet, bounded correction, implementation report, independent VERIFIED",
  "before_behavior": "An explicitly supplied empty environment mapping is silently replaced by ambient process state at the selector and at two collector forwarding sites.",
  "after_behavior": "Only None selects ambient process state; every supplied mapping, including an empty mapping, is consumed exactly as caller-owned input.",
  "self_descriptive_naming": "The existing environ parameter retains its ordinary Python meaning: None means absent, while an empty mapping means present and empty.",
  "obsolete_guidance_disposition": "No guidance is retired; the implementation is aligned with the function signature and the approved trust-boundary narrative.",
  "history_preservation": "Existing session envelopes, collision diagnostics, the v005 recovery row, and its pending sidecar remain byte-for-byte unchanged.",
  "expected_result": {
    "ambient_markers_consumed_when_environ_is_empty": 0,
    "explicit_durable_producer_false_conflicts": 0,
    "foreign_envelope_mutations": 0,
    "dispatcher_tafe_mutations": 0
  },
  "rollback": {
    "instructions": "Revert only the three None-versus-empty fallback hunks and their exact regression tests through a governed successor.",
    "test": "Rerun selector, collector, provenance, hook, parity, nonimpairment, lint, format, compile, and diff checks."
  },
  "hard_invariants": [
    "Role authority remains exclusively inside validated worker_role_provenance.",
    "An explicit mapping is never replaced based on truthiness.",
    "No session envelope, publication recovery artifact, dispatcher, TAFE, registry, role, eligibility, or routing state is mutated."
  ],
  "fail_closed_conditions": [
    "Empty mapping with no explicit producer",
    "Conflicting markers inside the supplied mapping",
    "Explicit producer name/id mismatch",
    "Selected envelope durable-identity or provenance mismatch"
  ],
  "essential_context_preservation": "The supplied mapping, selected durable producer, document-authoritative role provenance, exact six-path diff, known unrelated baseline failures, and publication-recovery ownership remain explicit."
}
```

## Prior Deliberations

- `DELIB-202667714` - owner-approved active list-free Assurance PAUTH v5 with bridge, claim, start, independent verification, and nonimpairment controls retained.
- `DELIB-20260801-WI5580-BACKLOG-APPROVAL` - owner confirmed WI-5580 for the governed proposal path; the record expressly does not bypass implementation gates.
- `DELIB-202667304` - prior independent GO on the original six-target design, including selector/role separation and exact hunk isolation.
- `bridge/gtkb-wi5580-session-envelope-collision-repair-006.md` - independent NO-GO that identifies the explicit-empty environment defect corrected by this revision.
- `WI-5825` - separate publication-capability recovery owner; no recovery target is absorbed into WI-5580.

## Owner Decisions / Input

- `DELIB-202667714` authorizes the active Assurance project as a list-free project scope. All WI-5580 implementation work inherits that project authority through active membership; legacy WI `approval_state` is not the controlling implementation gate.
- `DELIB-20260801-WI5580-BACKLOG-APPROVAL` confirms the item may proceed through the governed proposal path but does not itself authorize protected edits.
- No new owner decision is requested. Independent GO, claim, start, implementation report, and VERIFIED remain mandatory.
- The owner has directed that TAFE/dispatcher remain deliberately disabled for repairs. This revision neither activates nor mutates them.

## Proposed Scope

### IP-R1 - Correct shared selector None-versus-empty semantics

In `resolve_acting_harness_identity()`, replace truthiness selection with an explicit `None` check:

```python
env = dict(os.environ if environ is None else environ)
```

Preserve all existing conflict, durable-identity, and role-authority checks.

### IP-R2 - Correct both collector forwarding sites

Apply the identical `None`-only ambient fallback in:

- `resolve_runtime_provenance()`.
- `Collector.__init__()`.

This prevents an explicit empty mapping from being replaced before it reaches the shared selector. No other collector behavior changes.

### IP-R3 - Add exact regressions

In `platform_tests/scripts/test_kb_attribution_session_role.py`:

1. Seed an ambient recognized Codex marker.
2. Pass `environ={}` with no explicit producer and assert the selector fails with the existing unavailable-identity error rather than selecting Codex.
3. Pass `environ={}` plus explicit `claude` / `B` and assert successful durable identity resolution despite the ambient Codex marker.

In `platform_tests/scripts/test_collect_modernization_semantic_evidence.py`:

1. Seed ambient session/harness markers.
2. Call `resolve_runtime_provenance(..., environ={})` and assert the ambient session is not consumed.
3. Construct the collector with `environ={}` and assert its stored environment remains exactly empty and issuer resolution fails closed without evidence mutation.
4. Retain existing Codex collision, selected-envelope, foreign-immutability, and receipt tests.

### IP-R4 - Preserve the complete six-path cohort

The new correction hunks are expected only in `envelope.py`, the collector, and their two direct test modules. `.claude/hooks/workstream-focus.py` and `platform_tests/hooks/test_workstream_focus.py` remain in the target cohort because their existing WI-5580 hunks are part of the unfinalized implementation and must be rerun, hashed, reviewed, and finalized atomically without new behavior changes.

## Specification-Derived Verification Plan

| Requirement | Deterministic verification |
|---|---|
| Explicit empty selector input is sterile | Monkeypatch ambient Codex/Claude markers; pass `environ={}` without a producer; assert unavailable-identity failure and no ambient selection. |
| Explicit durable producer is independent of ambient state | With the same ambient markers, pass `environ={}`, `harness_name='claude'`, and `harness_id='B'`; assert exact `('claude', 'B')`. |
| Collector forwarding preserves supplied mapping | Exercise `resolve_runtime_provenance` and `Collector(environ={})`; assert the mapping remains empty and ambient session markers are not consumed. |
| Existing role authority remains document-derived | Rerun the complete attribution and collector selection tests, including forged ambient role and selected-envelope durable-id mismatch cases. |
| Existing collision history remains immutable | Rerun the three-way collision byte-hash test and deterministic ignored-path diagnostics. |
| Claude producer ownership remains intact | Rerun the complete workstream-focus hook suite; require foreign override refusal and valid Claude/B persistence. |
| Modernization nonimpairment | Rerun hard-invariant, harness-parity, fresh-worker, and scope-semantic applicable sets; disclose unrelated baseline failures without hiding them. |
| Six-path quality | Run Ruff check, Ruff format check, Python compile, exact file hashes, `git diff --check`, and hunk-isolation review across all six paths. |
| Publication recovery nonimpairment | Re-read the v005 recovery row and pending-sidecar hash after tests; assert no deletion, rewrite, compensation, finalization, or registry/DB mutation. |

## Verification Commands

```text
python -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short --timeout=600
python -m pytest platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short --timeout=600 -k "not live_program_reconciliation_is_executable_and_duplicate_free and not pre_modernization_baseline_binds_historical_observations_and_explicit_gaps"
python -m pytest platform_tests/scripts/test_modernization_scope_semantics.py -q --tb=short --timeout=600 -k "not mod_ad09_proves_query_quarantine_and_no_historical_worker_dependency"
python -m pytest platform_tests/scripts/test_modernization_hard_invariants.py -q --tb=short --timeout=600
python -m pytest platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short --timeout=600
python -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --timeout=600 -k "not fresh_worker_bootstraps_from_only_copied_product_assets"
python -m ruff check <the six approved paths>
python -m ruff format --check <the six approved paths>
python -m py_compile groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/collect_modernization_semantic_evidence.py .claude/hooks/workstream-focus.py
git diff --check -- <the six approved paths>
```

The explicit `--timeout=600` values are invocation-level containment while the already-filed timer-governance work externalizes repository timeout policy; this revision adds no hard-coded timer to product or test source.

## Acceptance Criteria

1. `resolve_acting_harness_identity(..., environ={})` never reads ambient process markers.
2. An empty mapping without an explicit producer fails closed with the existing unavailable-identity error.
3. An empty mapping with explicit durable `claude` / `B` succeeds even when ambient Codex markers exist.
4. `resolve_runtime_provenance(..., environ={})` and `Collector(environ={})` preserve the supplied empty mapping and do not consume ambient session identity.
5. All existing WI-5580 selector, role-authority, collision-immutability, producer-ownership, and applicable collector tests remain green.
6. The two known full-matrix modernization baseline failures remain reported separately and are not misclassified as WI-5580 correction failures.
7. Only the three approved None-versus-empty semantic sites and their exact regression tests receive new hunks; the complete six-path WI-5580 cohort remains isolated from unrelated work.
8. The v005 `recovery_required` row and pending sidecar remain byte-identical and owned by WI-5825.
9. Dispatcher/TAFE, harness roles, eligibility, routing, credentials, Git index/history, deployment, release, live envelope history, MemBase, and registry state remain unchanged by implementation.
10. A new independent GO, fresh exact claim, and fresh implementation-start packet exist before any protected edit.

## Risks / Rollback

The primary risk is changing the meaning of omitted input rather than only explicit input. The exact `environ is None` branch preserves ambient behavior when callers omit the argument; only supplied mappings avoid ambient fallback. The second risk is fixing the shared selector while leaving a forwarding layer to reintroduce ambient state; all three sites are therefore corrected and tested together. The third risk is absorbing publication recovery work or unrelated dirty bytes; the six-path cohort remains exact, while WI-5825 recovery artifacts are read-only preservation evidence.

Rollback is a governed successor that reverses only the three `None`-versus-empty hunks and their regression tests. It must not rewrite session envelopes, bridge history, the v005 sidecar, the publication capability row, or any unrelated path.

## Explicit Exclusions

- No protected source, test, hook, configuration, or runtime edit before independent GO, fresh claim, and fresh start authority.
- No TAFE or dispatcher activation, dispatch, configuration mutation, routing, harness contact, role/eligibility change, or lease manipulation.
- No database, MemBase, registry, publication-capability, pending-sidecar, recovery-row, or evidence mutation.
- No session-envelope deletion, closure, rewrite, merge, relocation, or synthetic backfill.
- No Git staging, commit, push, history rewrite, deployment, release, credential lifecycle, external-system mutation, or destructive cleanup.
- No new target path, formal requirement, or capability beyond exact explicit-environment isolation.

## Files Expected To Receive New Correction Hunks

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `scripts/collect_modernization_semantic_evidence.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`
- `platform_tests/scripts/test_collect_modernization_semantic_evidence.py`

## Verification-Only Preserved Cohort Paths

- `.claude/hooks/workstream-focus.py`
- `platform_tests/hooks/test_workstream_focus.py`

## Recommended Commit Type

`fix:` - correct hidden ambient-state consumption without adding a new capability.
