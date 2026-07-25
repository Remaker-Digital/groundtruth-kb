REVISED
::init gtkb pb
::open build

# Bridge lifecycle resolver grandfathers legacy pre-provenance versions (GOV-DOCUMENT-AUTHOR-PROVENANCE-001 conformance)

bridge_kind: prime_proposal
Document: gtkb-wi5670-resolver-legacy-provenance-tolerance
Version: 003
Responds to: bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-002.md
Author: Prime Builder (Claude B)
Date: 2026-07-24 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 302c4543-bd90-4fe9-b169-e90390e528b1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (session-stated override; durable registry role loyal-opposition)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5670

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Disposition

The `-002` NO-GO accepted the legacy-tolerance design, the WI-5153-independent
reasoning, the spec linkage, and both preflights, and independently confirmed
the resolver tests (46 passed) and ruff clean. It raised exactly one blocking
finding — **F1**: both declared target files already carry uncommitted foreign
hunks unrelated to WI-5670, so a GO could let a later commit misattribute those
bytes to WI-5670. Per owner direction (AskUserQuestion, 2026-07-24), this
revision keeps the design unchanged and adds an exact foreign-hunk-isolation and
verification plan (the NO-GO's sanctioned fallback), because the foreign hunks
cannot be cleanly reconciled through a single owning thread (see F1 response).
Design, scope, target paths, and acceptance criteria are otherwise unchanged
from `-001`.

## Finding Response — F1 (Pre-GO foreign hunk isolation)

**Acknowledged.** Both target files carry pre-existing uncommitted foreign hunks
that are not the WI-5670 legacy-`author_identity` change. This revision preserves
them and commits only the WI-5670 change.

**Foreign hunks named (per the NO-GO requirement):**

- `scripts/bridge_lifecycle_resolver.py` (19 add / 3 context): a `NEW -> REVISED`
  post-GO transition in `_validate_ordinary_transitions` plus
  `owner_deferred_reproposal` handling in `_ordinary_resolution` — the
  "owner-deferred post-GO report -> corrective REVISED proposal" lifecycle
  feature.
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py` (39 add): two tests,
  `test_owner_deferred_post_go_report_can_be_followed_by_revised_proposal` and
  `test_no_go_on_owner_deferred_corrective_proposal_does_not_resume_old_go`.

**Provenance / owner.** These are uncommitted working-tree changes vs HEAD
`9373c5231`, not attributable to a single live/finalizable thread: no bridge
proposal names this feature or these tests; the candidate long-running chains
(`gtkb-wi5629-corrected-malformed-verdict-chain`,
`gtkb-wi5633-protected-commit-corrected-chain-evidence`) are terminal `VERIFIED`
with latest slices targeting other files (WI-5629 v029 explicitly records "no
resolver test ... mutation occurred"). They are orphaned/uncommitted work within
the current 61-path `research`-branch drift, whose remediation is the remit of
the in-flight finalization-recovery threads
(`…terminal-finalization-audit-recovery`, `…terminal-evidence-recovery`,
`…bridge-helper-reconciliation-recovery`). WI-5670 does **not** revert, stage,
stash, or finalize them.

**Separability (why isolation is feasible).** The WI-5670 change and the foreign
hunks do not textually collide: in `_ordinary_resolution` the foreign
`owner_deferred_reproposal` hunk sits at the GO-index computation while WI-5670's
operative re-validation is appended after the `implementation_artifact` /
`implementation_verdict` selection, separated by the unchanged
`if latest_status == "GO" …` block; WI-5670's `_parse_version` legacy
classification and `BridgeVersion.is_legacy` additions are in different
functions; and WI-5670's new tests are appended as distinct functions. `git
add -p` therefore presents the WI-5670 hunks as independently selectable.

**Exact isolation + verification procedure (implementation phase, post-GO):**

1. Implement the WI-5670 legacy-tolerance change by editing the two target files
   on top of the current working tree (which retains the foreign hunks).
2. Stage ONLY the WI-5670 hunks:
   `git add --patch scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py`
   — select exclusively the legacy-classification / operative-re-validation /
   `is_legacy` / new-test hunks; reject every `owner_deferred_reproposal`,
   `NEW -> REVISED` transition, and `test_owner_deferred_*` /
   `test_no_go_on_owner_deferred_*` hunk. (Deterministic equivalent:
   `git apply --cached <reviewed WI-5670 patch>`.)
3. Verify the staged set is exactly WI-5670:
   `git diff --cached -- scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py`
   MUST show only legacy-tolerance changes and MUST NOT contain
   `owner_deferred_reproposal`, `test_owner_deferred_post_go_report`, or the
   `NEW -> REVISED` post-GO transition comment.
4. Verify the foreign hunks are preserved unstaged:
   `git diff -- scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py`
   MUST still contain the foreign hunks intact.
5. Commit only the staged hunks (single WI-5670 commit).
6. Post-commit confirmation: `git diff -- <two files>` MUST still show the
   foreign hunks unstaged and intact — proving the commit neither captured nor
   destroyed foreign work.

Because the working tree retains BOTH the foreign feature and the WI-5670 change
during test execution, `pytest` exercises WI-5670's legacy tolerance in the
presence of the foreign feature, while the committed diff excludes the foreign
feature. The independent VERIFIED reviewer re-checks staged-diff isolation from a
clean read.

## Summary

`scripts/bridge_lifecycle_resolver.py::_parse_version` hard-requires the
`author_identity` metadata field on **every** canonical-status bridge version,
contradicting `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, whose Contract is explicitly
forward-only: "Existing files at implementation time are grandfathered and are
not required to be backfilled." Because `implementation_authorization.py begin`
resolves the full thread via `resolve_bridge_lifecycle`, any thread containing a
single pre-provenance verdict cannot produce an implementation-start packet, so
the `implementation_start_gate` denies all protected writes. Concrete live
impact: `bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` (a
valid `NO-GO` authored 2026-07-16 by Cursor-E in the pre-contract prose format,
no `author_identity:` header) makes `begin` fail with `MISSING_BRIDGE_METADATA`,
blocking the already-`GO`'d, PAUTH-authorized P0 WI-5152. The fix makes the
resolver honor the grandfathering clause while preserving the review-independence
guarantee the `author_identity` parse serves.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the governing spec; forward-only
  grandfathering the resolver must honor for pre-implementation versions.
- `GOV-RELIABILITY-FAST-LANE-001` — eligibility: origin `defect`, no new public
  API/CLI/behavior beyond removing the defect, no new/revised requirement, two
  files (~<150 net lines); under `PROJECT-GTKB-RELIABILITY-FIXES` +
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail infrastructure; the fix
  preserves append-only history and GO/NO-GO/VERIFIED discipline, and (per F1)
  guarantees the commit carries only WI-5670 bytes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — cites every
  governing spec.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project, PAUTH, WI, and
  inline-JSON `target_paths` explicit above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification executes every
  changed behavior and the hunk-isolation proof.
- `GOV-STANDING-BACKLOG-001` — WI-5670 is the durable owner.

## Prior Deliberations

- `DELIB-20261032` — Document Artifact Author Provenance Gap Advisory.
- `DELIB-20260683` — LO Verdict, Document Artifact Author Provenance Contract
  (established the forward-only / grandfathering contract).
- `DELIB-20260666` — PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE PAUTH Authorization.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` — the
  concrete legacy failure this fix unblocks.
- _No prior deliberation addresses resolver legacy-tolerance specifically; this
  thread is the first to reconcile `resolve_bridge_lifecycle` with the
  grandfathering clause._

## Owner Decisions / Input

No per-fix owner approval is required (fast-lane, `GOV-RELIABILITY-FAST-LANE-001`,
covered by the standing PAUTH through active project membership). Owner-directed
this session via `AskUserQuestion` (2026-07-24, session `302c4543…`): (1) "Fix
the resolver (root fix)" over v002 backfill/deferral; (2) after the `-002` NO-GO,
"Reconcile foreign work first"; (3) once that proved un-tractable (foreign hunks
unattributable to a finalizable thread), "Hunk-isolation REVISED" — the basis
for this v003. Recorded by the owner-decision tracker.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (forward-only author provenance with
explicit grandfathering). The fix makes `resolve_bridge_lifecycle` conform; no
new or revised requirement or specification is created.

## Design (exact change)

**File 1 — `scripts/bridge_lifecycle_resolver.py`:**

1. `_parse_version`: a canonical-status version lacking `author_identity` becomes
   `classification="legacy"` (`author_identity=None`, `author_role=None`) instead
   of hard-failing, and skips `_validate_author_role`. Document / Version /
   Responds-to structural checks still apply.
2. `BridgeVersion`: add `is_legacy` (`classification == "legacy"`); `is_strict`
   and `is_malformed` stay `False` for legacy versions (single-malformed
   correction path and count unaffected).
3. `_ordinary_resolution` / `_correction_resolution`: after selecting the
   operative proposal + GO by status, **re-validate both** for complete,
   role-correct provenance (`author_identity` present; GO `author_role ==
   "loyal-opposition"`; proposal `author_role == "prime-builder"`); **fail
   closed** (new stable code `OPERATIVE_VERSION_MISSING_PROVENANCE`) if either
   operative version is legacy/incomplete. Implementation authority never
   derives from a grandfathered version.

**Why safe:** transition validation uses status only; operative selection is by
status; the operative pair is re-checked. New bridge files always carry
`author_identity` (the write-time `document_author_provenance_gate` enforces it),
so only historical files can be legacy — exactly what
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` grandfathers. The `_go_self_review_error`
backstop in `implementation_authorization.py` remains the independent
operative-pair guard. Net observable change: non-operative legacy versions stop
blocking; operative-legacy stays blocked.

**File 2 — `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:** add the
fixtures in the verification plan; existing strict-path tests remain green.

## Spec-Derived Verification Plan

| Requirement / behavior | Verification | Expected result |
| --- | --- | --- |
| Grandfather non-operative legacy version (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`) | New test: `NEW` -> legacy `NO-GO` (no `author_identity`) -> `REVISED` -> `GO` | Resolves; operative pair = strict `REVISED` + `GO` |
| Legacy is not malformed | New test asserts `is_malformed is False`, `is_legacy is True` | Ordinary resolution path used |
| Operative `GO` fail-closed | New test: operative `GO` lacks `author_identity` | Raises `BridgeLifecycleResolutionError` |
| Operative proposal fail-closed | New test: operative `NEW`/`REVISED` lacks `author_identity` | Raises |
| No regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --no-header` | All existing + new tests pass |
| Real-world unblock | `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5152-modernization-hard-invariant-registry` | `authorized: true` |
| **F1 staged-diff isolation** | `git diff --cached -- scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py` | Only legacy-tolerance change; NO `owner_deferred_reproposal` / `test_owner_deferred_*` / `NEW -> REVISED` transition |
| **F1 foreign-hunk preservation** | `git diff -- <two files>` before and after the WI-5670 commit | Foreign hunks present and intact both times |
| Lint / format | `ruff check` + `ruff format --check` on both target files | Clean |
| Bridge preflights | applicability + clause preflight on this thread | `preflight_passed: true`; 0 blocking gaps |

## Acceptance Criteria

1. Resolver grandfathers non-operative legacy versions; operative pair stays
   strictly re-validated (fail-closed).
2. Existing resolver tests remain green; new fixtures pass.
3. `begin` on `gtkb-wi5152-modernization-hard-invariant-registry` succeeds.
4. The WI-5670 commit contains ONLY the legacy-tolerance change; the foreign
   hunks are preserved unstaged and intact (F1).
5. Only the two declared files are implementation scope.

## Risk / Rollback

Risk: the resolver feeds the review-independence gate; an over-broad relaxation
could let implementation authority derive from an unverified version — mitigated
by the operative re-validation, the unchanged `_go_self_review_error` backstop,
and the write-time provenance gate. Commit-hygiene risk (F1) — mitigated by the
staged-diff isolation proof above. Rollback: revert the two files' WI-5670 hunks
in a single commit; no bridge history, MemBase, foreign hunk, or other path is
touched.

## Bridge Filing

Filed as the next append-only numbered bridge file (`-003`) for
`gtkb-wi5670-resolver-legacy-provenance-tolerance`; no prior version is deleted
or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs `resolve_bridge_lifecycle` to conform to
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`; adds no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
