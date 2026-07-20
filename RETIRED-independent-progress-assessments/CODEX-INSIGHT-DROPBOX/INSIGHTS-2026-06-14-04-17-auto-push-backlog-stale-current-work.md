Specs: GOV-STANDING-BACKLOG-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: GTKB-AUTO-PUSH-INVESTIGATION-001

# Loyal Opposition Advisory: Auto-Push Backlog Row Is Stale After VERIFIED Bridge Closure

Date: 2026-06-14
Role: Loyal Opposition, Codex harness A
Scope: Read-only backlog and bridge review; no MemBase mutation performed.

## Claim

`GTKB-AUTO-PUSH-INVESTIGATION-001` remains live in MemBase as `resolution_status=open`, `stage=backlogged`, with `status_detail` saying the investigation is "not yet started", even though the live bridge has terminal `VERIFIED` evidence for both the investigation slice and its remediation slice.

This is a backlog/current-work drift issue, not a new auto-push investigation.

## Finding

### P2 - Current-work state contradicts terminal bridge evidence

#### Observation

The live bridge index shows both auto-push investigation slices terminal:

- `bridge/INDEX.md:815` through `bridge/INDEX.md:820` lists `gtkb-auto-push-investigation-slice-2` latest `VERIFIED: bridge/gtkb-auto-push-investigation-slice-2-005.md`.
- `bridge/INDEX.md:2274` through `bridge/INDEX.md:2280` lists `gtkb-auto-push-investigation-slice-1` latest `VERIFIED: bridge/gtkb-auto-push-investigation-slice-1-006.md`.

Slice 1 verified the report-only investigation:

- `bridge/gtkb-auto-push-investigation-slice-1-006.md:15` states the post-implementation report satisfies the approved report-only scope.
- `bridge/gtkb-auto-push-investigation-slice-1-006.md:22` says remediation was not verified there and the residual `scripts/build.py` push-capable surface remained future Slice 2 work.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INVESTIGATION-AUTO-PUSH-2026-05-14.md:133` through `:150` records `partial_evidence_inconclusive`, identifies no hook or enabled scheduled-task push initiator, and recommends Slice 2 gating/removal of implicit `git push` in `scripts/build.py`.

Slice 2 verified the remediation:

- `bridge/gtkb-auto-push-investigation-slice-2-004.md:33` claims default execution no longer runs `git push` or downstream remote mutation unless `--push` is supplied.
- `bridge/gtkb-auto-push-investigation-slice-2-004.md:39` explicitly left the MemBase work item open until Loyal Opposition returned `VERIFIED` or separately directed closure evidence.
- `bridge/gtkb-auto-push-investigation-slice-2-005.md:16` through `:21` records `VERIFIED` and states the implementation satisfies the approved Slice 2 scope.

The live backlog row still reports stale state:

```json
{
  "id": "GTKB-AUTO-PUSH-INVESTIGATION-001",
  "priority": "P2",
  "stage": "backlogged",
  "approval_state": "auq_resolved",
  "resolution_status": "open",
  "status_detail": "S344 capture; investigation not yet started. Identified via scope-bundling incident on commit 5611dc44.",
  "completion_evidence": null,
  "changed_at": "2026-05-28T15:40:44+00:00",
  "changed_by": "prime-builder/claude/B"
}
```

#### Deficiency Rationale

The stale row makes autonomous work selection less reliable. Loyal Opposition fallback selection sees an apparently open, AUQ-resolved investigation and must spend cycles re-proving that the investigation and remediation are already complete. That creates duplicate-effort risk and can distract from genuinely unfinished work.

The mismatch also weakens traceability under `GOV-STANDING-BACKLOG-001`: current work state should point to the terminal bridge evidence or else explicitly state what evidence is still missing. Here, the post-implementation report anticipated the exact handoff by leaving the item open "until Loyal Opposition returns VERIFIED or separately directs closure evidence"; Loyal Opposition has now returned `VERIFIED`.

#### Proposed Solution / Enhancement

Prime Builder should reconcile `GTKB-AUTO-PUSH-INVESTIGATION-001` through the governed backlog path.

Minimal scope:

1. Re-read the live bridge entries for `gtkb-auto-push-investigation-slice-1` and `gtkb-auto-push-investigation-slice-2`.
2. Update the work item's status detail and completion evidence to cite:
   - `bridge/gtkb-auto-push-investigation-slice-1-006.md`
   - `bridge/gtkb-auto-push-investigation-slice-2-005.md`
   - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INVESTIGATION-AUTO-PUSH-2026-05-14.md`
3. If governed resolution is permitted for this row, move the row out of open/backlogged state using the standard MemBase/backlog command path.
4. If any closure precondition is still missing, record that specific precondition in `status_detail` instead of "investigation not yet started".

#### Option Rationale

Do not reopen the investigation or file another bridge implementation thread. The live bridge already carries terminal verification for the investigation and the bounded remediation.

Do not have Loyal Opposition mutate MemBase directly. This advisory is evidence-only; a current-work resolution or status update is a governed backlog mutation and should be performed by Prime Builder with the normal approval/authorization checks.

## Prime Builder Implementation Context

Objective: reconcile `GTKB-AUTO-PUSH-INVESTIGATION-001` so live backlog/current-work state matches terminal bridge evidence.

Preconditions:

- Confirm `bridge/INDEX.md` still lists both auto-push slices as latest `VERIFIED`.
- Confirm no newer bridge entry supersedes either terminal verdict.
- Use the governed backlog update/resolution path; do not edit `groundtruth.db` directly.

Evidence paths:

- `bridge/INDEX.md:815`
- `bridge/INDEX.md:2274`
- `bridge/gtkb-auto-push-investigation-slice-1-006.md:15`
- `bridge/gtkb-auto-push-investigation-slice-1-006.md:22`
- `bridge/gtkb-auto-push-investigation-slice-2-004.md:39`
- `bridge/gtkb-auto-push-investigation-slice-2-005.md:16`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INVESTIGATION-AUTO-PUSH-2026-05-14.md:133`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INVESTIGATION-AUTO-PUSH-2026-05-14.md:150`

Expected file touchpoints:

- No source files should be required.
- Expected mutation is MemBase/backlog state for `GTKB-AUTO-PUSH-INVESTIGATION-001`, via CLI/API only.
- Optional follow-up bridge/report artifact only if the governed backlog command requires new closure evidence.

Verification steps:

```text
python -m groundtruth_kb.cli backlog list --json --id GTKB-AUTO-PUSH-INVESTIGATION-001
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-auto-push-investigation-slice-1 --format json
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-auto-push-investigation-slice-2 --format json
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
```

Expected result: the backlog row no longer claims the investigation is unstarted, and no new Loyal Opposition-actionable bridge entry is created solely to rediscover this same state.

Rollback notes: if the backlog update is too broad, create a new versioned backlog row restoring the previous fields and cite this advisory as the correction source.

Open decisions: none for this advisory. If the backlog command requires owner approval to resolve the row, surface that as a separate single owner decision rather than broadening this Loyal Opposition report.
