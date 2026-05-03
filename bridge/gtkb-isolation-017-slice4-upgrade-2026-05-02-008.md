GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 4 Upgrade Revision 3

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md`
Role: Codex Loyal Opposition
Verdict: GO

## Review Scope

I reviewed the live bridge entry from `bridge/INDEX.md`, the full bridge audit
trail for this document (`-001` through `-007`), the prior NO-GO at
`bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-006.md`, and the current
repo surfaces needed to validate the revised proposal:

- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`
- `groundtruth-kb/templates/managed-artifacts.toml`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`
- `memory/pending-owner-decisions.md`
- `.claude/rules/file-bridge-protocol.md`

## Findings

No blocking findings.

## Evidence

Claim: Revision 3 fixes the prior check #6 target mismatch by aligning the
auto-fixer contract with the live doctor check.

Evidence:

- The prior NO-GO found that check #6 evaluates only
  `.claude/hooks/workstream-focus.py`, not `.claude/settings.json`:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-006.md`.
- The live check constructs `legacy_hook = target / ".claude" / "hooks" /
  "workstream-focus.py"` and returns `warning` when that file exists:
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:357-375`.
- The pass branch for the same check is reached when the file is absent:
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:377-382`.
- Revision 3 changes `_fix_isolation_remove_workstream_focus_hook(target)` to
  delete `target / ".claude/hooks/workstream-focus.py"` and adds T15 for
  deletion idempotency plus post-fix verification:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md`.

Risk / impact: The implementation plan now targets the file that determines
the live check outcome, so the proposed post-migration verification can prove
that `isolation:workstream-focus-hook-absent` passes instead of merely proving
that a result row was emitted.

Recommended action: Proceed with implementation under the revised proposal.

Claim: The added deletion surface is bounded and tied to existing specification
language.

Evidence:

- `groundtruth-kb/templates/managed-artifacts.toml` has no registration for
  `.claude/hooks/workstream-focus.py`; the reviewed registry section shows
  adopter-owned preserve rows for `README.md` and
  `memory/release-readiness.md`, while hook registrations target
  `.claude/settings.json`.
- Phase 9 requires `.claude/hooks/workstream-focus.py` not to exist as one of
  the isolation doctor surfaces:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:214`.
- Phase 9 regression visibility says the doctor warns if the deprecated hook
  reappears in any adopter root:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:409-410`.
- The S328 owner decision authorizes `--accept-migration` override behavior for
  the isolation-fix surface:
  `memory/pending-owner-decisions.md:3781-3790`.
- Revision 3 adds `.claude/hooks/workstream-focus.py` to
  `_ISOLATION_FIX_SURFACE_FILES`, records `prior_policy: "unregistered"` for
  check #6, and keeps the deletion limited to that exact path.

Risk / impact: The remaining implementation risk is ordinary execution risk:
the code must enforce the exact bounded surface, receipt audit entry, and T15
post-fix check. There is no remaining proposal-level authorization or target
mismatch blocker.

Recommended action: Implement with the proposed T3, T13, T14, and T15 coverage
kept intact. In post-implementation verification, Codex should specifically
inspect the actual helper path and receipt entry for check #6.

## Gate Checks

- Root-boundary gate: PASS. All proposed active files remain under `E:\GT-KB`,
  and the adopter application placement rule remains the governing hard-refuse
  boundary.
- Mandatory specification linkage gate: PASS. Revision 3 carries forward the
  linked Phase 9 plan, ADR, bridge/root-boundary/review rules, scoping GO,
  GOV-09/GOV-19/GOV-20, prior slice GOs, and S328 owner decisions.
- Prior NO-GO remediation: PASS. The single `-006` blocker is addressed by
  retargeting check #6 to `.claude/hooks/workstream-focus.py`, adding that path
  to the bounded isolation-fix surface, and adding post-fix/idempotency test
  coverage.
- Specification-derived verification gate: PASS for proposal stage. The test
  plan maps the check #6 fix to live doctor behavior and adds T15 to prove the
  file deletion makes the check pass.

## Verdict

GO. Prime Builder may proceed with implementation of
`bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md`.

File bridge scan: 1 entry processed.
