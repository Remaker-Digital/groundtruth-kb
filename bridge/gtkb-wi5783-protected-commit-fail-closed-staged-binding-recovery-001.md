NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-97ef-74b1-9310-09761b16938a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; approval_policy=never; sandbox=danger-full-access
author_metadata_source: current session metadata

bridge_kind: prime_proposal
Document: gtkb-wi5783-protected-commit-fail-closed-staged-binding-recovery
Version: 001
Date: 2026-08-01 UTC

# Recovery Implementation Proposal — WI-5783 protected-commit fail-closed staged binding

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-V3
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5783
target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

KB Mutation: This proposal performs no MemBase or `groundtruth.db` mutation.
The database is not an implementation target.

## Recovery Claim

This is a fresh recovery carrier for the still-open WI-5783 objective. It does
not modify the append-only `gtkb-wi5783-protected-commit-fail-closed-staged-binding`
v001-v011 chain. That chain's v011 is an untracked Prime-Builder-authored
`VERIFIED` document, lacks an atomic finalization commit, and embeds a failed
applicability preflight; it cannot provide independent verified implementation
authority. Because its terminal status has no lawful `REVISED` successor, this
new slug starts at `NEW` and preserves the older chain as historical evidence.

No source or test mutation may start until an independent Loyal Opposition `GO`,
an exact current-session work-intent claim, and a fresh schema-v3
implementation-start packet are all present.

## Defect / Reproduction

The protected-commit checker must fail closed when explicit `--paths` input is
empty, invalid, ambiguous, out of root, escaped, duplicate, globbed, a
directory, or resolves to no protected target. It must canonicalize valid
in-root absolute paths before protection classification. Its terminal clearance
must bind the exact current staged path, status, mode, object identifier,
content digest, complete manifest, and unexpired validity evidence rather than
replaying historical terminal path-glob evidence. Valid live-`GO` clearance
must remain available.

## Requirement Sufficiency

Existing requirements sufficient. WI-5783, the owner approval recorded in
`DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION`, the
leader reconciliation recorded in
`DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION`, and the active V3
PAUTH specify the exact two-path repair, operation-time limits, and required
verification. This carrier corrects a malformed terminal lifecycle; it does
not introduce a new product requirement.

## Scope And Boundaries

The exclusive implementation target set is:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

No dispatcher, routing, harness configuration, capability registry,
credential, external-system, destructive-cleanup, history-rewrite, push,
deployment, release, database, or unrelated-path mutation is in scope. No
historical bridge artifact may be edited, deleted, renumbered, staged, or
committed. One local atomic finalization commit is permitted only through an
independent Loyal Opposition `VERIFIED` finalizer after all gates pass.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — role-correct append-only bridge lifecycle
  and atomic commit-finalization.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — exact owner-backed V3
  project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not replace GO,
  claim, start, reporting, or verification gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — V3 must remain
  valid at each protected operation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — terminal clearance must
  derive from deterministic current-transaction evidence.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — protected Git lifecycle is bound to
  current staged content.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete
  specification linkage and verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — exact PAUTH, project,
  work-item, and target-path linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent executed
  specification-derived verification is required before terminal verification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preserve valid live-GO behavior
  while removing unsafe historical clearance.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — retain both malformed and recovery
  lifecycle evidence append-only.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets and evidence remain
  inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION` —
  owner authorization for the exact two-path repair.
- `DELIB-20260730-CF10-LEADER-TRANSFER-019F9B59` — owner transfer of CF-10
  serialization authority.
- `DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION` — active V3
  authorization lineage for this work item.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — historical
  authority interpretation preserved by the V3 recovery boundary.

## Owner Decisions / Input

- `APPROVE WI5783 PROTECTED-COMMIT FAIL-CLOSED REPAIR`, captured in
  `DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION`.
- `TRANSFER`, captured in `DELIB-20260730-CF10-LEADER-TRANSFER-019F9B59`.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-V3`
  is active, non-expiring, and limits the repair to the two targets above.

No new owner decision is required for this recovery proposal. Independent Loyal
Opposition review remains mandatory.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5783; DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION; active singleton V3 PAUTH; malformed terminal-chain recovery",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001",
  "primary_route": "scripts/check_protected_commit_authorization.py --staged",
  "before_behavior": "Invalid explicit selections can be accepted and historical terminal evidence can clear later staged bytes without current content binding.",
  "after_behavior": "Only a fresh independently reviewed GO under V3 may begin the exact two-target repair, and terminal clearance remains bound to the current staged transaction.",
  "self_descriptive_naming": "Diagnostics identify invalid selections and failed transaction bindings.",
  "obsolete_guidance_disposition": "The original v001-v011 chain remains append-only historical evidence and grants no implementation authority.",
  "history_preservation": "All prior bridge versions and owner decisions remain cited, unchanged, and reviewable.",
  "baseline": {
    "work_item": "WI-5783",
    "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
    "target_paths": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
    ]
  },
  "expected_result": {
    "summary": "Explicit selection and protected-commit clearance fail closed without impairing valid live-GO clearance.",
    "scope": ["explicit selection validation", "terminal replay removal", "exact staged binding", "focused regressions"]
  },
  "rollback": {
    "instructions": "Use a separate governed proposal limited to the same two targets.",
    "verification": "Rerun focused checker tests, Ruff, format, diff check, and bridge preflights."
  },
  "hard_invariants": [
    "No dispatcher mutation",
    "No implementation before a fresh GO, claim, and start packet",
    "No historical path glob authorizes new bytes",
    "Live-GO clearance remains valid"
  ],
  "fail_closed_conditions": [
    "Invalid explicit selection",
    "No protected target",
    "Stale or malformed packet",
    "Staged manifest or object/content mismatch"
  ],
  "essential_context_preservation": "The PAUTH, owner decisions, exact targets, required gates, and test mapping remain explicit."
}
```

## Implementation Conditions

1. Revalidate V3 immediately before every protected operation.
2. Acquire an exact WI-5783 implementation claim and a fresh schema-v3 start
   packet only after an independent GO on this recovery slug.
3. Stop and file a new proposal if a third target, different mutation class, or
   excluded operation becomes necessary.
4. Treat all committed or untracked terminal evidence from the superseded chain
   as diagnostic only; it cannot clear substituted, expired, or
   manifest-divergent staged bytes.

## Specification-Derived Verification Plan

| Requirement | Test or command | Required result |
| --- | --- | --- |
| Explicit selection validation | Focused CLI regressions for empty, blank, duplicate, escaped, globbed, directory, out-of-root, and protected-target-free `--paths --json` | Every invalid selection fails with a structured nonzero result. |
| In-root absolute normalization | Temporary-root regression using an absolute protected path | The canonical repository-relative protected path is evaluated, never skipped. |
| No terminal replay | Invert the terminal-replay test after staging new same-path bytes | Historical terminal evidence cannot clear newer staged bytes. |
| Exact staged binding | Tests for path, status, mode, OID, SHA-256, deletion, manifest, and index-snapshot mismatches | Only exact, current staged binding clears. |
| Packet validity | Expired, malformed, stale, tampered, and PAUTH-denied packet regressions | Each invalid packet fails closed. |
| Live-GO non-impairment | Existing and focused live-GO clearance tests | A valid approved target still clears. |
| Complete checker suite | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Pass. |
| Static quality | `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`; `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`; `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | All pass. |
| Governance | Applicability and clause preflights on this exact filed proposal | No missing required/advisory specification and zero blocking clause gaps. |

## Acceptance Criteria

1. The recovery proposal cites active V3, exact project and work item, and only
   the two original targets.
2. Invalid or no-protected explicit selections fail closed; an ordinary staged
   transaction with no protected target remains a valid no-op.
3. Historical terminal path globs cannot authorize later or substituted bytes.
4. Terminal clearance requires exact staged binding, independent verified
   lifecycle, operation-time PAUTH, and unexpired validity evidence.
5. Valid live-GO clearance remains available.
6. Focused tests, static checks, and bridge preflights pass.
7. No path beyond the declared two changes.
8. An independent finalizer atomically commits only the verified implementation,
   report, and VERIFIED verdict; otherwise no terminal status is published.

## Risks / Rollback

The compatibility break intentionally removes historical terminal-glob
clearance. A rollback requires a separate governed proposal and must not restore
an unsafe bypass. Before a new GO, this recovery changes only bridge lifecycle
evidence; no source or test target is touched. The older malformed chain remains
preserved as audit evidence throughout.

## Pre-Filing Preflight

Before live filing, run `bridge_applicability_preflight.py --content-file` and
`adr_dcl_clause_preflight.py --content-file` against this exact body. Filing
must fail if either reports a missing specification or blocking clause gap.

## Pre-Filing Preflight Evidence

- Applicability preflight against this candidate passed with
  `missing_required_specs: []` and `missing_advisory_specs: []`.
- The operation-time evaluator admitted both declared targets under V3 for
  `implementation_packet_create` and `implementation_start`.
- Mandatory ADR/DCL clause preflight passed: four must-apply clauses, zero
  evidence gaps, and zero blocking gaps.
