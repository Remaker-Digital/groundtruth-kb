NEW
author_identity: Claude Code (goose harness, session-scoped acting-as harness B)
author_harness_id: B (session-scoped acting-as via ::init gtkb pb keyword override)
author_session_context_id: 2026-06-07T11-31-XXZ-prime-builder-goose-acting-as-B
author_model: claude-opus-4-7 (via goose harness)
author_model_version: claude-opus-4-7
author_model_configuration: goose-cli; interactive; Prime Builder; session-scoped role override
author_metadata_source: session-start.json (harness=claude) plus owner-directed acting-as assignment; goose is not a registered harness

# Dirty Tree Reconciliation Recovery Record - 2026-06-07

bridge_kind: governance_review
Document: gtkb-dirty-tree-reconciliation-2026-06-07
Version: 001 (NEW; recovery record)
Recommended commit type: docs:

target_paths: []

## Purpose

This record documents the 2026-06-07 dirty-tree reconciliation operation under
Option A Path E1 (refined). It is a non-implementation governance record,
classified as terminal `bridge_kind: governance_review` so it does not enter
the headless dispatch loop and does not request VERIFIED. It exists to:

1. Create a same-commit bridge audit trail satisfying the
   `hook-and-action-gates` protected-artifact-inventory-drift gate's
   `--allow-review-evidence` path for the four recovery commits this record
   accompanies.
2. Preserve the rationale for landing the prior VERIFIED-but-uncommitted source
   changes today (2026-06-07) rather than on their original VERIFIED dates.
3. Record what was discarded, what was stashed, and what was committed during
   reconciliation.

## Scope Of This Record

This record is **not** an implementation proposal, **not** an implementation
report, **not** a VERIFIED request, and **not** an implementation-start
authorization request. It does not authorize any new source, rule, template,
test, configuration, KB, approval-packet, or implementation artifact mutation.
All `target_paths` are empty.

The substantive authority for each commit accompanied by this record comes
from the **prior VERIFIED bridge thread cited in that commit's message**.
This recovery record only documents the recovery operation itself.

## Reconciliation Operation Summary

### Discovery

At session start the working tree contained 15 modified files plus 3 untracked
groups, accumulated by 5 distinct prior Prime Builder sessions spanning
2026-06-06 17:12 through 2026-06-07 11:32, none of which were committed.
The tree compiled and passed `ruff check` and `ruff format --check`, but 7
targeted tests failed in `platform_tests/hooks/test_workstream_focus.py` and
a runtime role-partition violation was observed
(`active role map must hold exactly one prime-builder; found 2: ['A', 'B']`).

### Per-Group Classification

The dirty content was decomposed into seven groups, six of which matched
existing bridge threads:

- **Group A** - Slice 1 protected live-rule edit:
  `.claude/rules/report-depth-prime-builder-context.md`,
  `groundtruth-kb/templates/rules/report-depth.md`, and untracked
  `platform_tests/scripts/test_report_depth_review_methodology.py`.
  Prior thread: `gtkb-role-enhancement-review-depth-contract-slice-1` with
  latest NO-GO at `-004` and terminal `governance_review` acknowledgments at
  `-007` / `-008`. The protected-rule edit was NO-GO'd for lack of a
  narrative-artifact approval packet. **Action: stashed under
  `slice-1-review-depth-contract-protected-rule-edit-awaiting-narrative-artifact-approval-2026-06-07`
  for a future owner-interactive narrative-artifact approval flow.**

- **Group B** - Codex wrapup startup gate guard SoT:
  `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` and
  `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`.
  Prior thread: `gtkb-codex-wrapup-startup-gate-guard-sot` (pruned from
  INDEX.md) with VERIFIED verdict at `-004` and implementation report at
  `-003` listing exactly these files. **Action: recovered and committed
  unchanged from the working tree, citing the prior VERIFIED verdict.**

- **Group C** - Ollama dispatch stall retry cap:
  `scripts/cross_harness_bridge_trigger.py` and
  `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
  Prior thread: `gtkb-ollama-dispatch-stall-retry-cap` (pruned from INDEX.md)
  with VERIFIED verdict at `-006` and implementation report at `-005` filed
  by Codex harness A on 2026-06-07T07:28Z, listing exactly these files.
  Work Item WI-4388. **Action: recovered and committed unchanged from the
  working tree, citing the prior VERIFIED verdict.**

- **Group D** - Heartbeat replace-access-denied retry:
  `scripts/active_session_heartbeat.py` and
  `platform_tests/scripts/test_active_session_heartbeat.py`.
  Prior thread: `gtkb-heartbeat-replace-access-denied-retry` (pruned from
  INDEX.md) with VERIFIED verdict at `-006` and implementation report at
  `-005` listing exactly these files. Work Item WI-4392.
  **Action: recovered and committed unchanged from the working tree, citing
  the prior VERIFIED verdict.**

- **Group E** - Startup role-slot label disambiguation:
  `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`,
  and the verified-scope label-rename test assertions in
  `platform_tests/scripts/test_session_self_initialization.py` and
  `platform_tests/hooks/test_workstream_focus.py`.
  Prior thread: `gtkb-startup-role-slot-label-disambiguation` (pruned from
  INDEX.md) with VERIFIED verdict at `-006` and implementation report at
  `-005` listing exactly these files. Work Item WI-4391 under
  PROJECT-GTKB-RELIABILITY-FIXES (owner-elevated for fast-lane execution).
  **Action: recovered and committed the verified-scope subset only. Label
  assertions were re-applied precisely from the prior session's verified
  diff; F-dependent helper assertions were excluded.**

- **Group F** - Unauthorized `scripts/harness_roles.py` refactor adding
  `GTKB_ROLE_ASSIGNMENTS_PATH` env override and `assignment_path` parameter
  handling. No matching bridge thread, no GO, no implementation report. This
  is the cause of the 7 test failures in `test_workstream_focus.py`. The
  prior Prime Builder session was actively debugging Group F at session end,
  producing 25 ad-hoc debug scripts under `scripts/test/` (timestamps 11:19
  - 11:32 UTC). **Action: reverted to HEAD.**

- **Group G** - Throwaway debug scratch and CRLF noise:
  `scripts/test/` (25 ad-hoc debug scripts from the Group F debugging
  session), `.test-tmp/` (test scratch directory, `.gitignore` line 549
  already covers it), `harness-registry.json` (CRLF-only diff, no semantic
  change). **Action: `scripts/test/` deleted, `.test-tmp/` ignored,
  `harness-registry.json` reverted.**

### Pre-Existing Test Failures Surfaced

Reverting Group F left ~7 pre-existing test failures in
`platform_tests/hooks/test_workstream_focus.py` and adjacent test modules
that assert legacy `role-assignments.json` paths while production code in
`scripts/workstream_focus.py` and `scripts/session_self_initialization.py`
now reads from `harness-registry.json`. These are NOT introduced by this
reconciliation; they are a pre-existing production / test inconsistency that
the prior unauthorized Group F refactor was attempting to paper over. They
must be addressed by a properly-authorized future bridge proposal, not
silently re-introduced via unauthorized scope.

### Repository Integrity Finding (Separate)

`git fsck` reports two zero-byte loose blob objects from 2026-06-04
22:26 / 22:27 UTC:
- `.git/objects/a8/c2666b6c729e6c4b35b4d1a78734beca883c43`
- `.git/objects/e2/ac8310986dc36178fbd8db73f7c549b6cc5f60`

Both are blobs (file content), not commits or trees. The commit graph is
intact and commits work. This corruption predates the reconciliation work
and does not block it, but should be repaired separately (likely via
`git fetch origin` followed by `git fsck` after rehydration).

## Cited Prior VERIFIED Threads (substantive authority)

- Group B: `bridge/gtkb-codex-wrapup-startup-gate-guard-sot-004.md` (VERIFIED)
  responding to `-003` implementation report.
- Group C: `bridge/gtkb-ollama-dispatch-stall-retry-cap-006.md` (VERIFIED)
  responding to `-005` implementation report. WI-4388.
- Group D: `bridge/gtkb-heartbeat-replace-access-denied-retry-006.md`
  (VERIFIED) responding to `-005` implementation report. WI-4392.
- Group E: `bridge/gtkb-startup-role-slot-label-disambiguation-006.md`
  (VERIFIED) responding to `-005` implementation report. WI-4391 under
  PROJECT-GTKB-RELIABILITY-FIXES.

## Owner Decisions / Input

No owner decision is requested by this recovery record itself. The owner
(Mike) directly approved the reconciliation operation in two prompts during
the 2026-06-07 interactive session: (1) "Option A - Reckon with the dirty
tree first.", (2) "E1" then "Option 1 (Refined E1)", (3) "Option 1 (single
recovery-record bridge file)".

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - canonical bridge authority for this
  recovery record.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the reconciliation operation
  itself is captured as a durable artifact rather than left as untracked
  recovery work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - recovery commit + stash + revert
  decisions match the lifecycle-trigger framework for recovered, deferred,
  and discarded work.

## Limits

This GO (when granted) does not authorize any new implementation, does not
mark any pre-existing thread complete, does not supersede the substantive
authority of the cited prior VERIFIED threads, and does not waive any
narrative-artifact approval requirement that remains outstanding for
Group A's stashed Slice 1 protected-rule edit.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
