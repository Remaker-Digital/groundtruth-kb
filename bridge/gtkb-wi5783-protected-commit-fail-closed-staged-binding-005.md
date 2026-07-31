REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb192-8b20-7833-8eeb-a0435f6ad179
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=default; thread_source=automation
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5783-protected-commit-fail-closed-staged-binding
Version: 005
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5783-protected-commit-fail-closed-staged-binding-004.md

# Revised Implementation Proposal — WI-5783 protected-commit fail-closed selection and staged-content binding

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-V3
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-V3","coverage":"exact_singleton","selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5783
target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision replaces the non-executable v001/v002 authorization lineage. It carries forward the two-file, P0 fail-closed repair under the active singleton V3 PAUTH and the leader-reconciled owner decision. No implementation may start until a new independent Loyal Opposition GO, a matching current-session work-intent claim, and a schema-v3 implementation-start packet exist.

The repair must: fail closed on empty, invalid, ambiguous, out-of-root, escaped, duplicate, globbed, directory, or protected-target-free explicit selections; canonicalize in-root absolute paths; remove content-blind committed-terminal replay; bind terminal clearance to the exact current staged path/status/mode/OID/content digest and complete manifest with unexpired validity evidence; and preserve valid live-GO clearance.

## Requirement Sufficiency

Existing requirements sufficient. WI-5783, the original owner authorization, `DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION`, and active V3 PAUTH fully specify the accepted behavior, exact two-path boundary, required tests, and operation-time gates. The correction is authorization lineage only; it introduces no new product requirement.

## Finding Addressed

### P0 executable-authority gap

Version 004 correctly found that v001/v002 cite a revoked, commit-forbidding PAUTH and cannot authorize implementation. This revision cites the active V3 PAUTH, which is scoped exactly to WI-5783 and the two original source/test targets. It preserves v001/v002 as historical non-executable evidence and requests a new independent GO rather than retroactively treating prior review as valid.

## Scope And Boundaries

The target set is unchanged and exclusive:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

No dispatcher, configuration, routing, credential, external-system, destructive-cleanup, history-rewrite, push, deployment, release, or unrelated-path mutation is in scope. One local atomic finalization commit is permitted only through the independent VERIFIED finalizer after all implementation and verification gates succeed; this proposal does not itself authorize a commit.

This proposal performs no MemBase mutation or KB write. The PAUTH and deliberation citations are read-only authority evidence; `groundtruth.db` is not an implementation target.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — role-correct append-only lifecycle.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — exact owner-backed project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not replace GO, claim, or start gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — validate V3 at operation time.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — deterministic evidence rather than path-only claims.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — fail-closed protected Git lifecycle bound to current transaction evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — exact PAUTH/project/WI/target linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent spec-derived evidence before terminal verification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preserve valid live-GO and atomic-finalization behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserve governed lifecycle artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keep all work in-root and outside adopter scope.

## Prior Deliberations

- `DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION` — the underlying owner approval for the two-file repair.
- `DELIB-20260730-CF10-LEADER-TRANSFER-019F9B59` — owner transfer of CF-10 serialization authority.
- `DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION` — fresh leader-backed authorization requiring this append-only revision.

## Owner Decisions / Input

- Owner approval: `APPROVE WI5783 PROTECTED-COMMIT FAIL-CLOSED REPAIR`, recorded in `DELIB-20260730-WI5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-AUTHORIZATION`.
- Owner CF-10 transfer: `TRANSFER`, recorded in `DELIB-20260730-CF10-LEADER-TRANSFER-019F9B59`.
- Active authority: `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5783-PROTECTED-COMMIT-FAIL-CLOSED-REPAIR-V3`, issued from `DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION`.

No new owner decision is required: V3 expressly authorizes this corrected append-only proposal and retains the original two-target scope.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5783; DELIB-20260730-WI5783-LEADER-RECONCILED-AUTHORIZATION; active singleton V3 PAUTH",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001",
  "primary_route": "scripts/check_protected_commit_authorization.py --staged",
  "before_behavior": "Revoked v001/v002 authority could be misread as executable and historical terminal path globs could clear later staged bytes.",
  "after_behavior": "Only a fresh independently reviewed GO under V3 can begin the two-target repair, and terminal clearance is exact-transaction-bound.",
  "self_descriptive_naming": "Diagnostics identify the invalid selection or failed transaction binding.",
  "obsolete_guidance_disposition": "v001/v002 remain append-only history and are explicitly non-executable authority.",
  "history_preservation": "All prior bridge versions and owner decisions remain cited, unchanged, and reviewable.",
  "baseline": {"work_item": "WI-5783", "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING", "target_paths": ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]},
  "expected_result": {"summary": "Explicit selection and protected-commit clearance fail closed without impairing valid live-GO clearance.", "scope": ["explicit selection validation", "terminal replay removal", "exact staged binding", "focused regressions"]},
  "rollback": {"instructions": "Use a separate governed proposal limited to the same two targets.", "verification": "Rerun the focused checker suite, Ruff, format, diff check, and bridge preflights."},
  "hard_invariants": ["No dispatcher mutation", "No implementation before a fresh GO, claim, and start packet", "No historical path glob authorizes new bytes", "Live-GO clearance remains valid"],
  "fail_closed_conditions": ["Invalid explicit selection", "No protected target", "Stale or malformed packet", "Staged manifest or object/content mismatch"],
  "essential_context_preservation": "The PAUTH, owner decisions, exact targets, required gates, and test mapping remain explicit."
}
```

## Implementation Conditions

1. Re-read and validate V3 immediately before every protected operation.
2. Acquire an exact WI-5783 claim and a fresh schema-v3 implementation-start packet only after a new, independent GO.
3. Stop and file a new revision if a third target path, a different mutation class, or any excluded operation becomes necessary.
4. Keep committed terminal evidence historical/diagnostic only; it must not clear substituted, expired, manifest-divergent, or otherwise new staged bytes.

## Specification-Derived Verification Plan

| Requirement | Test or command | Required result |
| --- | --- | --- |
| Explicit selection validation | Focused CLI regressions for empty, blank, duplicate, escaped, globbed, directory, out-of-root, and protected-target-free `--paths --json` | Each invalid selection fails with structured nonzero result |
| In-root absolute normalization | Temporary-root regression using an absolute protected path | Canonical repository-relative protected path is evaluated, never skipped |
| No terminal replay | Invert the terminal-replay test after staging new same-path bytes | Historical terminal evidence does not clear the mutation |
| Exact staged binding | Regression coverage for path/status/mode/OID/SHA-256/deletion/manifest/index snapshot mismatches | Only exact, current binding clears |
| Packet validity | Expired, malformed, stale, tampered, and PAUTH-denied packet regressions | Every invalid packet fails closed |
| Live-GO non-impairment | Existing and focused live-GO clearance tests | Valid approved target still clears |
| Complete checker suite | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Pass |
| Static quality | Ruff check, Ruff format check, and `git diff --check` on the two targets | Pass |
| Governance | Applicability and clause preflights | Pass with no blocking gap |

## Pre-Filing Preflight

The governed revision helper will validate this exact candidate with `bridge_applicability_preflight.py --content-file` and `adr_dcl_clause_preflight.py --content-file` before it can create the live REVISED entry. Filing must fail if either preflight fails or reports a blocking gap.

## Acceptance Criteria

1. The live proposal names active V3, the leader-reconciled decision, the exact project, WI, and two target paths.
2. Explicit invalid/no-protected selections fail closed, while a normal staged transaction with no protected target remains a valid no-op.
3. Historical terminal path globs cannot authorize later or substituted bytes.
4. Terminal clearance requires exact current staged binding, independent verified lifecycle, operation-time PAUTH, and unexpired validity evidence.
5. Valid live-GO clearance remains available.
6. Focused/full tests, static checks, and bridge preflights pass.
7. No target beyond the declared two paths changes.

## Risks And Rollback

The compatibility break intentionally removes historical terminal-glob clearance. Any rollback needs separate governed authority and must not restore an unsafe bypass. Before a new GO, this revision changes only bridge lifecycle evidence; no source or test target is touched.
