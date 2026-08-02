ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 469b6155-827b-44cb-a56d-f838893bffa3
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task system-statusprogress-check; resolved role loyal-opposition

bridge_kind: governance_advisory
Document: gtkb-lo-sysprobe-runtime-residue-census-cost
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-08-01 UTC

## Source

Scheduled system status/progress probe (system-statusprogress-check), 2026-08-01,
session context 469b6155-827b-44cb-a56d-f838893bffa3. Timing measured with
Measure-Command around gt invocations; footprint measured with recursive
Get-ChildItem over the project root. This advisory supplies the CAUSAL MECHANISM
for the latency that gtkb-lo-sysprobe-cli-latency-and-gate-false-positives-001.md
(2026-07-31) measured but attributed to the wrong driver.

## Claim

The dominant cost in the slow gt surfaces is whole-root FILE CENSUS over ~1.3 M
ephemeral residue files, not MemBase corpus size. The 2026-07-31 advisory
attributes latency to "corpus size ... MemBase is 844 MB with 1.5 M pipeline
events". That attribution is not supported: an isolating measurement shows the
same registry command running in 2.1 s with the census disabled and 43.8 s with
it enabled, against an unchanged MemBase.

## Evidence

Isolating measurement (same session, same MemBase, same commit):

| Command | Wall clock |
| --- | --- |
| gt registry inspect --no-census | 2.1 s |
| gt registry validate (census on) | 43.8 s |
| gt registry audit-duplicates | > 420 s (backgrounded; later exit 1) |
| gt project doctor | 1,753.97 s (29.2 min), overall FAIL |
| gt deliberations search | 12.5 s |
| gt bridge dispatch status | 1.44 s |
| gt backlog list --limit 1 | 0.43 s |
| gt harness roles | 0.32 s |

The no-census versus census delta is 2.1 s to 43.8 s on the same command family.
MemBase is identical across both. Corpus size does not explain it.

What the census walks. Project-root footprint is 188.5 GB across 2,018,437 files.

| Directory | Size | Files |
| --- | --- | --- |
| .pytest-tmp | 124.61 GB | 1,608,278 |
| .git | 41.23 GB | 12,259 |
| .gtkb-state | 11.34 GB | 244,719 |
| .claude | 2.52 GB | 59,559 |
| groundtruth-kb | 1.97 GB | 68,341 |

gt registry audit-duplicates reports registry_count=2348 against
persistent_file_count=1,318,672 (registered_file_count=261,422). The registry
tracks 2,348 governed artifacts; the census examines 1.32 M paths, ~99.8% of
which are ephemeral residue.

Residue detail inside .gtkb-state (11.34 GB, no reaping): six .gtkb-lifecycle
directories totalling ~1.45 GB across ~82,000 files; single work-item scratch
directories of 2.16 GB (wi5492-projection-isolation), 1.65 GB (hygiene-reclaim),
1.43 GB (codex-verify-wi5492-3784), 1.03 GB (integration-worktrees), 801 MB
(wi5411), 49.8 MB (wi5381); plus roughly 30 empty pytest-basetemp directories,
54.9 MB bridge-poller, 42.8 MB dispatcher-daemon (including a 42.5 MB
shadow-decisions.jsonl), and 34.0 MB lo-verdicts.

Corroborating symptom observed the same session: a Glob tool call over
.claude/hooks file-safety patterns timed out at 20 s and had to be reissued
through PowerShell. Generic file-search tooling is degraded by the same file
count.

## Risk / Impact

- gt project doctor is the canonical predicate for several rule-cited conditions
  including the session-start health surface. At 29.2 minutes it cannot be run
  inside a normal session, so those preconditions are asserted but not evaluated.
  The 2026-07-31 advisory made this point; this advisory identifies the fixable
  cause.
- Two doctor FAIL conditions are direct consequences: the duplicate-SoT audit
  baseline is declared incomplete precisely because persistent_file_count is
  dominated by residue.
- Misattributing latency to MemBase size would send remediation at the wrong
  target. A pipeline_events prune (see companion advisory
  gtkb-lo-sysprobe-membase-pipeline-events-unbounded-growth) is worth doing on its
  own merits but will NOT materially move doctor runtime.
- The residue is a Clean-Before-You-Leave violation at scale; that principle
  requires session-only artifacts to be cleaned before session end.

## Owner Decision Needed

None to file this advisory. Retention windows for the pytest temp root and the
gtkb-state scratch root are owner-facing policy and should be captured via
AskUserQuestion when Prime Builder scopes the work. Deletion of any existing
residue is a destructive action requiring separate owner approval; this advisory
does not request or authorize it.

## Recommended Prime Action

1. Determine whether the whole-root census must traverse known-ephemeral roots at
   all. Excluding the pytest temp root and gtkb-state scratch subtrees is the
   highest-leverage single change and is independent of any deletion.
2. Establish reaping policy and retention windows for both roots. Roughly 30
   empty pytest-basetemp directories suggest creation is instrumented but
   teardown is not.
3. Re-baseline gt project doctor, gt registry validate, and gt registry
   audit-duplicates after exclusion, and report the delta. Do NOT credit any
   improvement to a MemBase prune without this control.
4. Coordinate with WI-5724 (bound deep registry reconciliation output and census
   cost). WI-5724 bounds OUTPUT volume; this bounds traversal SCOPE. They are
   complementary, not duplicates.
5. Coordinate with WI-5431 (git object-store bloat), separately tracked and not
   addressed here.
6. Consider a fast doctor subset suitable for session-start use, so the
   rule-cited health predicate is actually evaluable.

## Related Backlog

- WI-5855 (filed this session, P1) - records this defect in MemBase work_items.
- WI-5724 (open) - registry reconciliation output and census cost bounding.
- WI-5431 (open) - git object-store bloat.
- WI-5371, WI-5597 (open) - pytest root scanning and basetemp ACL resilience;
  adjacent, neither covers accumulation or reaping.

## Prior Deliberations

- gtkb-lo-sysprobe-cli-latency-and-gate-false-positives-001.md (2026-07-31) - the
  advisory this one corrects on causation and extends with the isolating
  measurement. Its latency observations stand; its attribution does not.
- gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md (2026-07-30) -
  append-only growth cost at the SoT-access layer; adjacent surface.
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 - repetitive deterministic work belongs
  in services; a health check too slow to run is the failure mode that principle
  exists to prevent.

## Classification Slot

adapt.

This advisory is not implementation approval. It does not authorize protected
edits, does not authorize deletion of any file or directory, does not open an
implementation-start packet, and does not bypass the Prime Builder proposal,
Loyal Opposition GO, or verification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
