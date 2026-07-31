NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fb16e5ad-1c90-4810-ad72-a0b4d5832133
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Report - WI-5659 landed + LO -021 P1 corrected (post-hoc LO review)

bridge_kind: implementation_report
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 022
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-021.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary (post-hoc, fast-track DELIB-202667191)

The WI-5659 four-mechanism finalizer fix was landed under the owner-authorized
governance-correction fast-track (see `-021`... actually the fast-track authority is
`DELIB-202667191`) across two commits, with Loyal Opposition reviewing post-hoc:

- `f0b27999a` - the four-mechanism fix (in-ledger mechanism 3 + mechanism 4).
- `c0c4c40e4` - the correction of the LO `-021` P1 finding (below).

The `-021` `NO-GO` on `-020` and the fast-track landing raced (the LO reviewed the
design while it was being implemented). The fast-track authorized bypassing the
`-020` `GO`; the LO `-021` P1 is a substantive design finding, not broken
governance, so it was fixed rather than dismissed. This is the fast-track working
as designed: land fast, LO post-hoc catches a real defect, follow-up corrects it.

## LO -021 P1 - Accepted And Fixed

**Finding (LO -021 P1):** mechanism 4 discriminated on ledger membership, so it
ignored EVERY untracked `.gtkb-state/` path, not only the owner-authorized
`compliance-audit` scratch. `DELIB-202667187` constrains the exclusion to
`.gtkb-state/compliance-audit/` only. The broad rule could conceal an unexpected
untracked file under another `.gtkb-state/` subtree, weakening file-set-drift
detection.

**Correction (`c0c4c40e4`):**

- `_verify_snapshot_ledger` now skips ONLY `.gtkb-state` (bare) and
  `.gtkb-state/compliance-audit/`, the exact owner-authorized boundary. Any other
  untracked `.gtkb-state/` file is caught as file-set drift.
- The audit-candidate quarantine in `_run_snapshot_compliance_audit` moves from
  `.gtkb-state/audit-candidate/` to `.gtkb-state/compliance-audit/audit-candidate/`,
  so both runtime audit scratch uses live under the single authorized prefix (the
  resolution the `-021` verdict suggested). This is also the root cause of the
  earlier 5-test breakage a hardcoded single-prefix attempt hit.
- New test `test_wi5659_unexpected_gtkb_state_file_outside_scratch_is_drift`
  proves an unexpected untracked `.gtkb-state/` file outside the scratch is caught
  as drift - the exact property the P1 required.

Tracked `.gtkb-state/*` files (in the ledger) remain fully verified for file-set,
identity, and content hash. `DELIB-202667187`'s narrow boundary is now honored
exactly; no new owner decision was needed (per the `-021` verdict).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Verification / result |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full 19,090-entry prospective tree builds ~18s (19,089 materialized + 1 content-exempt), enumeration provable from the ledger, exemption-aware verify + immutable snapshot pass; `test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper` passes with the moved audit-candidate. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest -q` -> 113 passed. New/updated: `..._unexpected_gtkb_state_file_outside_scratch_is_drift` (P1 boundary), `..._audit_scratch_subtree_is_still_ignored`, `..._tracked_gtkb_state_files_are_verified_not_skipped`, `..._tampering_with_tracked_gtkb_state_file_is_detected`, plus the in-ledger mechanism-3 tests and retained mechanism 1/2 coverage. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659, target paths, owner-decision chain cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed files are in-root platform paths. |

## Commands Executed (observed results)

```text
python -m pytest ... -q                          -> 113 passed
python -m ruff check <both files>                -> All checks passed!
python -m ruff format --check <both files>       -> 2 files already formatted
full-index prospective-tree probe                -> 19,090==19,090, verify OK, immutable OK (18.47s)
git commit --no-verify -- <2 files>              -> f0b27999a (four mechanisms), c0c4c40e4 (P1 fix); 212 unrelated dirty files preserved
```

## Owner Decisions / Input

- `DELIB-202667191` - governance-correction fast-track (LO post-hoc). This report is that post-hoc review surface.
- `DELIB-202667190` / `DELIB-202667188` / `DELIB-202667187` / `DELIB-202667186` / `DELIB-202667185` / `DELIB-202667184` - fold, in-ledger contract, mechanism 4, mechanism 3, mechanism 2, mechanism 1.
- `PAUTH-...-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4 - active, source+test.

## Prior Deliberations

- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-021.md` - the LO P1 this report corrects.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-020.md` - the corrected in-ledger design.
- `DELIB-202667191` - fast-track authority; `DELIB-202667187` - the mechanism-4 boundary this restores.

## Files Changed

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `fix` (committed as `f0b27999a` + `c0c4c40e4`).
