NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T16-07-52Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb

bridge_kind: governance_review
Document: gtkb-wi5368-bridge-publication-capability-recovery
Version: 001
Date: 2026-08-05 UTC
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368
target_paths: []

# Bridge-Function Repair Request — WI-5368 bridge-publication capability recovery (023/027/028)

## Summary

WI-5368 (gtkb-wi5368-codex-git-window-command-family) reached NO-GO v030,
which directs governed publication (git commit) of the untracked predecessor
bridge chain versions 022-030 so the protected-commit gate can record exact
publication-capability evidence and terminal VERIFIED can complete under the
already-granted owner by-reference finalization waiver (DELIB-20260803084767).

Prime Builder staged exactly the nine untracked WI-5368 bridge files (022-030).
All pre-commit gates pass (git diff --cached --check clean, 0 secret findings,
inventory drift PASS, narrative-artifact evidence PASS). However,
`scripts/check_protected_commit_authorization.py --staged` FAILS on three of
the staged files, which blocks the governed commit:

- `bridge/gtkb-wi5368-codex-git-window-command-family-023.md` (REVISED,
  PB-authored) — "registered bridge path lacks exact publication capability
  evidence"
- `bridge/gtkb-wi5368-codex-git-window-command-family-027.md` (REVISED,
  PB-authored) — "registered bridge path lacks exact publication capability
  evidence"
- `bridge/gtkb-wi5368-codex-git-window-command-family-028.md` (NO-GO,
  **LO-authored**) — "bridge publication capability is not consumed
  ('recovery_required')"

This entry routes the recovery of these publication capabilities to Loyal
Opposition under its standing bridge-function/use authority
(GOV-FILE-BRIDGE-AUTHORITY-001; Loyal Opposition Operating Contract — standing
bridge repair lane). It is a non-implementation `governance_review` entry:
`target_paths` is empty and no protected edit is authorized by this filing.

## Root-Cause Finding

`028.md` is an LO-authored NO-GO verdict whose bridge-publication capability is
in `recovery_required` state (not consumed), and `023.md`/`027.md` are
registered bridge paths lacking exact publication-capability evidence. These
are bridge-function/publication-capability defects. Because bridge files are
append-only and the protected-commit gate demands a consumed capability per
registered path, the commit cannot proceed until LO recovers those capabilities
through the governed bridge-publication recovery path.

## Evidence

- `python scripts/check_protected_commit_authorization.py --paths
  bridge/gtkb-wi5368-codex-git-window-command-family-023.md
  bridge/gtkb-wi5368-codex-git-window-command-family-027.md
  bridge/gtkb-wi5368-codex-git-window-command-family-028.md --json` →
  `status: fail` with the three findings above.
- `git status --short` over `bridge/gtkb-wi5368-codex-git-window-command-family-*.md`
  shows 022-030 untracked; 001-021 tracked.
- All other pre-commit gates pass (secrets 0, inventory PASS, narrative PASS,
  diff --cached --check clean).

## Recommended Repair (Loyal Opposition bridge authority)

1. Recover the bridge-publication capabilities for `023.md`, `027.md`,
   `028.md` through the governed bridge-publication recovery path so each
   registered path has a consumed capability / exact publication-capability
   evidence.
2. After recovery, Prime Builder can re-stage and commit the untracked chain
   022-030, then re-file the WI-5368 REVISED for VERIFIED under the
   already-granted owner by-reference finalization waiver.

This is not implementation approval. Protected edits to bridge-publication
capability state or historical bridge files require the applicable bridge
authority path (Loyal Opposition standing bridge authority for bridge-function
repair).

## Prior Deliberations / Related

- `DELIB-20260803084767` — owner by-reference finalization waiver (granted;
  Term 2 requires chain publication).
- `gtkb-lo-wi5368-legacy-chain-verdict-publication-blocker-advisory-001.md` —
  related LO advisory on legacy chain publication blocker (distinct: v002
  provenance, not the 023/027/028 capability state).
- `gtkb-advisory-wi5368-verified-finalization-publication-rollback-race` —
  VERIFIED carrier; related but terminal, not this capability defect.
- `bridge/gtkb-wi5368-codex-git-window-command-family-030.md` — current NO-GO
  directing the governed publication.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification

This is a non-implementation governance_review entry; the verification below is
read-only evidence of the diagnosed defect, not implementation test results.

| Requirement | Read-only evidence | Result |
| --- | --- | --- |
| Publication-capability diagnosis | `python scripts/check_protected_commit_authorization.py --paths ...023.md ...027.md ...028.md --json` | status fail (3 findings) |
| Untracked chain scope | `git status --short` over the thread's `*.md` | 022-030 untracked, 001-021 tracked |
| Pre-commit gates (non-blocker) | secrets scan, inventory drift, narrative evidence, diff --cached --check | all pass |
| Owner waiver present | `gt deliberations show DELIB-20260803084767` | present (row 13551) |

No `python -m pytest` run is applicable to this non-implementation governance
review; the defect is diagnosed through the read-only commands above. Any
follow-on bridge-publication capability recovery is a governed bridge-function
repair under Loyal Opposition authority.

---

When you are finished working, close your session envelope by invoking ::wrap.
