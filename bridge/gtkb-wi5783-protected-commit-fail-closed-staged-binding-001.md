NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb072-9be2-7b10-b0ae-a7974f125f20
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; approval_policy=never; sandbox=danger-full-access


# Implementation Proposal - WI-5783 protected-commit fail-closed selection and staged-content binding

bridge_kind: prime_proposal
Document: gtkb-wi5783-protected-commit-fail-closed-staged-binding
Version: 001
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5783
target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair two P0 fail-open classes. Explicit path selection must canonicalize in-root absolute paths and fail closed on empty, invalid, ambiguous, out-of-root, or protected-target-free input. Committed terminal VERIFIED bridge evidence must stop acting as replayable path-glob authority. VERIFIED clearance must be transaction-local and bound to the exact current staged path, status, mode, object id, content digest, complete staged manifest, and an unexpired finalized implementation-start packet.

## Claim

Prime Builder proposes a two-file source-and-test repair for WI-5783. Valid live-GO clearance and transaction-local independent-VERIFIED clearance remain. Implementation is forbidden until independent Loyal Opposition GO, a matching work-intent claim, and a valid implementation-start packet exist.

## Reproduced Defects

### F1 - Absolute protected paths are misclassified

This command currently exits 0/PASS, leaves `protected_paths` empty, and places the absolute protected path under `skipped_unprotected`:

```powershell
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts/check_protected_commit_authorization.py --paths E:\GT-KB\scripts\check_protected_commit_authorization.py --json
```

At the filing baseline, `_normalize_rel` only trims and slash-normalizes; it never root-relativizes an in-root absolute path before classification.

### F2 - Empty explicit selection passes

This command also exits 0/PASS:

```powershell
& 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe' scripts/check_protected_commit_authorization.py --paths --json
```

`_evaluate_selected` does not distinguish an explicit empty authorization request from a legitimate staged transaction containing no protected paths.

### F3 - Committed terminal evidence is path-only and replayable

`_load_verified_evidence` reduces a historical terminal thread to `(bridge_id, chain.target_paths)`; `_verified_authorization` clears later selected protected paths solely by historical glob match. This route does not validate current staged object/content identity or packet expiry. The existing `test_evaluation_pins_one_head_oid_across_index_and_terminal_evidence` stages a new post-terminal source mutation and expects `terminal_verified_bridge_thread` to clear it, directly locking in the unsafe replay behavior.

## Requirement Sufficiency

Requirements are sufficient. WI-5783 and DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION define the bypasses, exact targets, fail-closed selection, staged-content binding, validity-window enforcement, live-GO preservation, and focused regressions. The singleton PAUTH allows only source/test and forbids dispatcher mutation and Git commit.

## In-Root Placement Evidence

Both targets are under E:\GT-KB:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

No adopter/application path or dispatcher configuration/routing path is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - role-correct append-only lifecycle.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - exact owner-backed project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace GO, work intent, or implementation start.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time PAUTH validation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - deterministic evidence instead of narrative path claims.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - fail-closed protected Git lifecycle bound to current transaction evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete spec linkage before GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact PAUTH/project/WI/target linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent spec-derived evidence before VERIFIED.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - preserve valid live GO and atomic finalization behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve governed artifacts and lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keep platform governance outside adopter scope.

## Prior Deliberations

- `DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION` - binding owner authorization.
- `DELIB-202667184`, `DELIB-202667185`, `DELIB-202667186`, and `DELIB-202667187` - prior WI-5659 performance/hermetic-snapshot context, not semantic-change authority.
- `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-006.md` - canonical current checker baseline.
- `bridge/gtkb-lo-protected-commit-gate-stall-finalization-advisory-001.md` - separate WI-5742 stall scope, not absorbed.
- `bridge/gtkb-lo-false-terminal-recurrence-and-recovery-termination-gap-advisory-001.md` - canonical later WI-5629 recovery context.

## Owner Decisions / Input

- Owner approval: `APPROVE WI5783 PROTECTED-COMMIT FAIL-CLOSED REPAIR`.
- Canonical decision: `DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION`.
- Active PAUTH: `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR`.

No further owner input is required for the two-file proposal. Git commit remains forbidden by PAUTH.

## Proposed Scope

### 1. Canonical explicit-path validation

- Reject blank inputs.
- Convert native absolute paths inside the project root to repository-relative POSIX paths.
- Reject out-of-root absolute paths, relative escapes, Git-internal paths, globs, directory shorthand, duplicate normalized paths, and Unicode/case collisions.
- Keep staged paths sourced from the immutable copied Git index.
- In explicit `--paths` mode only, emit structured failure/nonzero exit for empty input or no protected target. A normal `--staged` transaction with no protected path may pass.

### 2. Remove committed-terminal path-glob clearance

Committed terminal VERIFIED threads may remain historical/diagnostic context, but cannot clear a new mutation merely because a historical proposal glob matches. Remove `terminal_verified_bridge_thread` as standalone authority. Explicit `--paths` mode has no staged snapshot and may clear only through a currently valid live-GO packet.

### 3. Bind VERIFIED clearance to the current transaction

Transaction-local independent VERIFIED clearance must bind:

- normalized path and staged status;
- Git mode and exact copied-index object id;
- SHA-256 content digest for blobs, or explicit deletion binding;
- complete equality between staged paths and Same-transaction path set;
- exact resolver-approved proposal, GO, report, and independent VERIFIED candidate;
- schema-v3 finalized implementation-start evidence;
- allowed operation-time PAUTH decision; and
- packet expiry that has not elapsed.

Revalidate from the immutable copied index before clearance. Missing/extra paths, stale/expired packet, object/content substitution, post-snapshot drift, or any mismatch fails closed.

### 4. Preserve legitimate behavior and boundaries

- Preserve valid live-GO clearance.
- Preserve role, independence, lifecycle, manifest, PAUTH, isolated-compliance, registry, and publication-capability checks.
- Do not change dispatcher routing/configuration, work-intent services, packet generation, verdict writers, registry schemas, or finalizer helpers.
- Do not absorb WI-5742.

## Cross-Harness Disposition

This is a shared repository Git-governance service. All harnesses inherit it. No harness configuration, capability registry, dispatcher rule, or routing mutation. Independent review must use a distinct LO session context.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5783; DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION; exact singleton PAUTH",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and governed Git lifecycle requirements",
  "primary_route": "scripts/check_protected_commit_authorization.py --staged",
  "before_behavior": "Absolute in-root protected paths and empty explicit selections pass; historical terminal globs clear later bytes after packet expiry.",
  "after_behavior": "Explicit selections fail closed; live GO remains; VERIFIED clearance is current-transaction-only with exact object/content and packet-validity binding.",
  "self_descriptive_naming": "Failures identify the exact selection or binding defect.",
  "obsolete_guidance_disposition": "Output/tests stop calling committed terminal globs reusable mutation authority.",
  "history_preservation": "Historical terminal threads remain append-only evidence without new clearance power.",
  "baseline": {
    "work_item": "WI-5783",
    "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
    "target_paths": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
    ]
  },
  "expected_result": {
    "summary": "Every protected clearance is a valid live GO or exact transaction-local independent VERIFIED binding.",
    "scope": [
      "Canonical explicit-path validation",
      "No committed-terminal path-only clearance",
      "Exact staged object/content binding",
      "Focused/full regressions"
    ]
  },
  "rollback": {
    "instructions": "Revert only the two targets under separate governed authority.",
    "verification": "Rerun focused regressions, full suite, Ruff, format, and preflights."
  },
  "hard_invariants": [
    "No dispatcher/routing mutation",
    "No implementation before GO/claim/start",
    "No historical path glob authorizes new bytes",
    "Live GO and transaction-local independent verification remain"
  ],
  "fail_closed_conditions": [
    "Explicit selection invalid or has no protected target",
    "Terminal evidence lacks exact staged binding",
    "Packet stale, expired, malformed, or PAUTH-denied",
    "Manifest differs from complete staged set"
  ],
  "essential_context_preservation": "PAUTH, decision, targets, chain, bindings, tests, and verification remain explicit."
}
```

## Specification-Derived Verification Plan

| Requirement | Test or command | Required result |
| --- | --- | --- |
| Empty/invalid explicit selection | CLI tests for empty, blank, duplicate, escaped, globbed, directory, out-of-root, and protected-target-free `--paths --json` | Structured fail/nonzero |
| Absolute in-root normalization | CLI test with absolute protected path under temporary root | Repository-relative protected path; never skipped |
| No terminal replay | Invert current committed-terminal replay test and stage new same-path bytes | FAIL; no terminal clearance |
| Exact staged binding | Tests for path/status/mode/OID/SHA-256/deletion/manifest/index snapshot | Only exact binding clears |
| Packet validity | Expired, malformed, stale, tampered, PAUTH-denied packet tests | All fail; valid unexpired passes |
| Live-GO non-impairment | Existing/focused live-GO tests | Approved target clears |
| Full suite | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | PASS |
| Static quality | Explicit venv Ruff check/format-check and `git diff --check` | PASS |
| Governance | Applicability and clause preflights | PASS/no blocking gaps |

## Acceptance Criteria

1. Empty `--paths` exits nonzero with machine-readable failure under `--json`.
2. In-root absolute protected paths normalize to repository-relative protected paths.
3. Out-of-root, escaped, blank, globbed, directory, duplicate, or ambiguous input fails closed.
4. Explicit no-protected input fails; staged no-protected mode remains a valid no-op.
5. Committed terminal threads cannot authorize new matching-path bytes or post-expiry reuse.
6. Transaction-local VERIFIED requires exact current path/status/mode/OID/content digest, complete manifest, approved chain, independent verdict, PAUTH, and unexpired packet.
7. Any binding mismatch, object substitution, missing/extra path, packet tamper/expiry, or snapshot drift fails.
8. Valid live-GO clearance remains.
9. Full tests, focused regressions, Ruff, format, diff check, applicability, and clause preflight pass.
10. Only the two declared paths change; dispatcher/routing/configuration files stay untouched.

## Risks / Rollback

High risk because this is the protected Git lifecycle. The intentional compatibility break is that historical terminal globs no longer authorize later mutations. Recovery flows must use current transaction-local VERIFIED evidence or a separately governed future content-binding protocol.

Rollback requires separate authority and may touch only the two approved targets. Governance artifacts remain append-only. No rollback may restore the bypasses without a new owner decision.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`fix`
