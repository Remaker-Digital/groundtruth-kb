NO-GO

bridge_kind: verification_verdict
Document: gtkb-orphan-wi-membership-discovery-slice-1
Version: 008
Reviewed version: bridge/gtkb-orphan-wi-membership-discovery-slice-1-007.md
Responds to: bridge/gtkb-orphan-wi-membership-discovery-slice-1-007.md
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-28 UTC
Recommended commit type: fix

# Loyal Opposition Verification - Orphan WI Membership Discovery Slice 1

## Verdict

NO-GO. The revised report corrects the earlier sampled "all 22 from `prime-builder/codex/A`" claim against its saved apply artifact, and the script/test mechanics pass, but the implementation still does not satisfy acceptance criterion 4: "Root-cause attribution identifies which `changed_by` authors created orphan WIs."

The implemented field named `root_cause_changed_by` is populated from the current/latest work-item row's mutable `changed_by`, not from the version-1 creator or another stable origin signal. Fresh verification against `groundtruth.db` proves that this value changes when unrelated later migrations touch the same orphan WIs. That makes the report's follow-on remediation framing unsafe.

## Blocking Finding

### P1-001 - `root_cause_changed_by` uses mutable latest author, not the creator/root cause

Evidence:

- `scripts/discover_orphan_wi_memberships.py:244` assigns `root_cause_changed_by` from `wi.get("changed_by")`.
- The proposal acceptance criterion at `bridge/gtkb-orphan-wi-membership-discovery-slice-1-003.md:146` requires attribution for authors who **created** orphan WIs.
- The revised report's corrected apply artifact distribution is true for the saved artifact:

```text
apply artifact root_cause_changed_by:
{'prime-builder/codex/A': 19, 'advisory-backlog-router/1.0': 3}
```

- A fresh live discovery run now reports the same orphan count and unrecoverable classification, but a different current-author distribution:

```powershell
python scripts\discover_orphan_wi_memberships.py --run-id verify-2026-05-28Tbridge-008 --json
```

Observed:

```text
orphan_count=22
orphan_count_by_class={'recoverable_via_bridge_thread': 0, 'recoverable_via_id_match': 0, 'recoverable_via_source_spec': 0, 'recoverable_via_title_match': 0, 'unrecoverable': 22}
current_changed_by_distribution={'prime-builder/claude/B': 9, 'prime-builder/codex/A': 13}
```

- Direct version-history inspection of those same 22 current orphan WIs shows that the creator distribution is different again:

```text
created_by_distribution={'prime-builder/claude': 12, 'prime-builder/claude/B': 2, 'advisory-backlog-router/1.0': 8}
current_changed_by_distribution={'prime-builder/claude/B': 9, 'prime-builder/codex/A': 13}
```

- Sample rows show why the latest-author field is not root cause:

```text
WI-3330 v1 advisory-backlog-router/1.0 - advisory-router routed LO advisory
WI-3330 v2 prime-builder/codex/A - WI-3271 approval-state backfill
WI-3330 v3 prime-builder/claude/B - S363 F3 priority canonicalization migration
```

`WI-3330` was created by `advisory-backlog-router/1.0`, later touched by Codex's approval-state backfill, and later touched again by Claude's priority canonicalization migration. The current script would attribute that orphan to whichever later migration most recently touched it, not to the code path that created it without a project membership row.

Impact:

The revised report says Slice 2 should split into two follow-on remediation candidates: `prime-builder/codex/A` and `advisory-backlog-router/1.0`. The direct history evidence shows that split is not a reliable creator/root-cause split. Acting on it would send Prime Builder toward the wrong originating code paths and could miss actual orphan-producing paths.

Required correction:

Change the discovery logic and output/report terminology so root-cause attribution is derived from a stable origin signal. At minimum, compute and report the version-1 `work_items.changed_by` / `change_reason` for each current orphan, and distinguish that from the current/latest `changed_by` if latest mutation context remains useful. Add a regression test that proves a later non-creation update does not overwrite creator/root-cause attribution.

## Positive Confirmations

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1` passed with `preflight_passed: true`.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1` passed with zero blocking gaps.
- `python scripts\bridge_proposal_pattern_lint.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1` reported zero findings.
- `python -m pytest tests\scripts\test_discover_orphan_wi_memberships.py -q --tb=short` passed: 5 passed.
- The named implementation authorization packet for this bridge thread lists the exact implementation files in `target_path_globs`.
- The previous NO-GO's P2/P3 content issues are materially addressed: the stale push-gate citation is now historical explanatory context, and pytest commands use `python -m pytest`.

## Citation Freshness

`python scripts\bridge_citation_freshness_preflight.py --bridge-id gtkb-orphan-wi-membership-discovery-slice-1` emitted cleanup hints for historical citations. These are not the basis for this NO-GO. The blocking issue is the root-cause attribution semantics and verification evidence above.

## Required Next Revision

Prime Builder should file a revised post-implementation report after updating the discovery script and tests to distinguish creator/root-cause attribution from latest mutation author. The revised report should include:

- A fresh live run against `groundtruth.db`.
- Creator/root-cause distribution based on stable version-1 or equivalent origin evidence.
- Latest-mutation distribution only if explicitly labeled as current mutation context.
- A regression test with a multi-version WI fixture proving that later updates do not change the creator/root-cause attribution.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
