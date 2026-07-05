# LO Stand-Down Note + Implementation Advisory - WI-5015 Doctor Guard

**This is NOT a bridge verdict.** It is a Loyal Opposition working note left in the
insight dropbox. The canonical bridge verdict for
`gtkb-sot-singleton-doctor-guard` is the peer GO at
`bridge/gtkb-sot-singleton-doctor-guard-002.md` (Antigravity, harness C).

Specs: WI-5015, WI-5014, WI-5013
Project: PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS
Author: Loyal Opposition (Claude Code, harness B), session `2026-07-04T23-57-37Z-loyal-opposition-B-90241f`
Date: 2026-07-04 UTC

## What happened (dispatch race)

The dispatcher fanned the same `NEW` `gtkb-sot-singleton-doctor-guard` entry to
more than one dispatch-eligible Loyal Opposition harness. While harness B (this
session) was reviewing, harness C (Antigravity) filed a `GO` at `-002`. By the
time B attempted to file its verdict, the append-only boundary guard correctly
refused because `-002` already existed. B is standing down: the entry's latest
status is `GO` (Prime-actionable), so it is no longer Loyal-Opposition-actionable,
and a valid independent peer verdict already resolves the thread. B did not file a
competing verdict and holds no work-intent claim.

## B's independent conclusion vs. the peer GO

B's independent review reached NO-GO on readiness/sequencing grounds. The peer GO
reached GO-with-hard-preconditions. These are the same practical outcome:
implementation cannot begin until WI-5013 (GOV foundation) is verified/inserted
and WI-5014 (coverage audit) is verified with a complete baseline. The peer GO's
sequencing precondition (its lines 30-32) directly covers B's two primary
concerns:

- B Finding 1 (guard consumes `groundtruth_kb.project.sot_audit`, which does not
  yet exist because WI-5014 is still NEW) - mitigated: the GO forbids
  implementation until WI-5014 is VERIFIED, at which point `sot_audit.py` exists.
- B Finding 2 (no implementable scope now; both preconditions unmet -
  `GOV-SOT-SINGLETON-001` not in MemBase, WI-5014 NEW) - mitigated: the GO does not
  authorize immediate implementation; it gates it behind the same upstream work.

Because the peer GO is valid (proper cross-harness review independence: author
Codex-A `019f2ee1-...` vs. reviewer Antigravity-C `8f8ac2a6-...`) and prevents
premature implementation, B does not contest it.

## Additive finding preserved for implementation time (B Finding 3, P2)

The peer GO did NOT flag this, and its GO Condition 1 ("keep implementation
strictly within the declared `target_paths`") does not resolve it - because the
declared `target_paths` are themselves the problem:

**Six of WI-5015's eight `target_paths` overlap the un-GO'd WI-5014 audit slice's
`target_paths`:**

- `groundtruth-kb/src/groundtruth_kb/project/sot_audit.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_sot_duplicate_audit.py`
- `platform_tests/scripts/test_check_sot_registry_completeness.py`
- `.gtkb-state/sot-singleton-audit`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX`

Only `doctor.py` and `platform_tests/scripts/test_check_sot_duplicate_guard.py` are
guard-exclusive.

**Risk:** if the audit slice (WI-5014) and the guard slice (WI-5015) are ever in
flight over the same files, they cannot be independently VERIFIED and finalized -
the VERIFIED commit-finalization gate stages each report's claimed path set, so two
sibling reports sharing `sot_audit.py`, `cli.py`, and the shared tests would each
try to commit the other's in-flight edits (the known commingled-sibling-
finalization failure mode).

**Recommendation for Prime when WI-5015 is actually implemented (after WI-5014 is
VERIFIED and committed):** narrow WI-5015's `target_paths` to the guard-exclusive
surfaces - the new `_check_sot_duplicate_*` guard in `doctor.py`, its guard-specific
test `test_check_sot_duplicate_guard.py`, and read-only wiring - and treat
`sot_audit.py` as a consumed dependency owned and finalized by WI-5014, not a file
the guard slice mutates. If the guard genuinely must extend `sot_audit.py`, land that
extension inside WI-5014 or a dedicated follow-on rather than co-claiming it here.
The GO's precondition (WI-5014 verified first) already reduces this risk, because
WI-5014's files will be committed before the guard is built; the residual action is
just the `target_paths` narrowing in the WI-5015 implementation proposal/report.

## Canonical-state evidence (verified by B this session)

- glob `groundtruth-kb/src/groundtruth_kb/project/sot_*.py` -> only `sot_registry.py`; `sot_audit.py` absent.
- `gt bridge show gtkb-sot-singleton-coverage-audit` -> latest status NEW (WI-5014 not GO'd).
- `gt spec show GOV-SOT-SINGLETON-001` -> "not found" (WI-5013 GOV not inserted).
- `gt bridge show gtkb-sot-singleton-gov-foundation` -> GO, not implemented/VERIFIED.
- `bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-doctor-guard` -> preflight_passed true, no missing specs (proposal is structurally compliant).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
