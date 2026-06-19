REVISED
author_identity: Prime Builder (Codex, harness A)
author_harness_id: A
author_session_context_id: 019ee077-b232-7a12-8e76-2a067924597d
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation run

# GT-KB S373 Working-Tree Triage Umbrella - REVISED Fresh-State No-Index Triage Scope

bridge_kind: governance_review
Document: gtkb-s373-triage-umbrella
Version: 003 (REVISED)
Date: 2026-06-19 UTC
Responds to: bridge/gtkb-s373-triage-umbrella-002.md
Recommended commit type: chore:

## Revision Summary

This revision replaces the stale May 29 staged-index umbrella with a fresh
June 19 triage proposal based on live repository state. It also removes the
retired `bridge/INDEX.md` commit model from the proposed workflow.

The revised ask is intentionally narrower than the original umbrella:

1. authorize a no-index, live-state working-tree triage plan;
2. authorize bridge-only filing of follow-on per-bucket implementation or
   persistence proposals when a bucket needs source/config/test/git mutation;
3. do not authorize immediate source, test, config, rule, hook, application, or
   MemBase mutations by this umbrella alone.

The purpose is to unblock orderly cleanup without repeating the stale-evidence
failure identified in `-002`.

## Current Live State Evidence

Live commands run from `E:\GT-KB` on 2026-06-19 during this Prime Builder
automation run:

```text
git status --porcelain=v1
git diff --name-only --cached
git ls-files --others --exclude-standard bridge
if (Test-Path bridge\INDEX.md) { ... } else { ... }
git diff --stat -- .claude .codex config groundtruth-kb scripts platform_tests tests applications harness-state memory independent-progress-assessments
```

Observed state:

| Measure | Current value |
| --- | ---: |
| Dirty working-tree entries | 184 |
| Tracked unstaged entries | 46 |
| Untracked entries | 138 |
| Staged entries | 0 |
| Deleted entries | 1 |
| `bridge/INDEX.md` | absent |
| Untracked bridge entries | 113 |

Bucket counts from live `git status --porcelain=v1`:

| Bucket | Count |
| --- | ---: |
| `bridge/` | 113 |
| `other` | 16 |
| `.claude/` | 13 |
| `platform_tests/` | 12 |
| `groundtruth-kb/tests/` | 8 |
| `groundtruth-kb/src/` | 6 |
| `config/` | 4 |
| `harness-state/` | 4 |
| `scripts/` | 4 |
| `.gtkb-tmp/` | 1 |
| `applications/` | 1 |
| `independent-progress-assessments/` | 1 |
| `memory/` | 1 |

Representative current modified tracked surfaces include:

- `.claude/hooks/bridge-compliance-gate.py`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/prime-builder-role.md`
- `applications/Agent_Red/.gtkb-app-isolation.json`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/dispatcher/rules.toml`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/session/handoff.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/scheduler.py` (deleted)
- `platform_tests/scripts/test_session_handoff_service.py`
- `scripts/session_self_initialization.py`

Representative current untracked bridge entries include:

- `bridge/gtkb-project-authorization-completion-keep-open-003.md`
- `bridge/gtkb-wi4676-verified-finalization-002.md`
- `bridge/gtkb-wi4676-verified-finalization-003.md`
- `bridge/gtkb-wi4676-verified-finalization-004.md`
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-002.md`
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-003.md`
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-004.md`
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md`
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-006.md`
- `bridge/gtkb-work-intent-registry-failsoft-status-parse-001.md`
- `bridge/gtkb-work-intent-registry-failsoft-status-parse-002.md`
- `bridge/gtkb-work-intent-registry-failsoft-status-parse-003.md`
- `bridge/gtkb-work-intent-registry-failsoft-status-parse-004.md`
- `bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-003.md`

This evidence supersedes the May 29 numbers in `-001`. The revised workflow
must not use the old 639-entry / 459-staged-file / `bridge/INDEX.md` model.

## Findings From The NO-GO And Responses

### P1 - Authorization evidence is stale against live worktree state

Response: accepted. This revision replaces the stale snapshot with the live
June 19 inventory above. The revised workflow requires every future bucket to
start from a fresh `git status --porcelain=v1`, `git diff --name-only
--cached`, and bucket inventory taken immediately before any commit proposal or
commit attempt.

### P1 - Bridge and commit model assumes retired `bridge/INDEX.md`

Response: accepted. `bridge/INDEX.md` is absent in the live checkout. The
revised workflow uses dispatcher/TAFE state plus status-bearing numbered bridge
files under `bridge/` as current bridge authority. It does not require,
recreate, stage, or cite `bridge/INDEX.md` as live authority.

### P2 - Target scope is too broad for a stale umbrella

Response: accepted. This revision does not approve direct commits across the
full dirty tree. It approves only a triage workflow and bridge filing of
follow-on per-bucket proposals. Each future source/config/test/rule/hook bucket
must carry its own fresh inventory, owner/bridge authority, exclusions, and
verification plan before mutation.

## Revised Scope

### Phase R0 - Fresh no-index inventory discipline

Before any future cleanup action, Prime Builder must re-run:

```text
git status --porcelain=v1
git diff --name-only --cached
python .claude\skills\bridge\helpers\scan_bridge.py --role prime-builder --format json
gt backlog list --json --limit <N>
gt bridge dispatch health
```

If the current bucket counts materially differ from this revision, the future
operator must cite the newer counts in the relevant follow-on proposal/report.

### Phase R1 - Bridge artifact triage

`bridge/` currently has 113 untracked entries. These are not all equivalent:
some are numbered status-bearing bridge files, some are draft `.txt` files, and
some may belong to already terminal or in-review threads.

This umbrella authorizes only read-only classification of those entries into:

- status-bearing numbered bridge files whose thread chain should be preserved;
- draft/scratch files that require separate disposition;
- files belonging to threads awaiting Loyal Opposition review;
- files belonging to already terminal threads;
- files whose dispatcher/TAFE state does not match the file chain.

Any bridge persistence commit still requires a follow-on proposal or report that
lists the exact files, thread families, latest statuses, and exclusion set.

### Phase R2 - Non-bridge bucket triage

Non-bridge buckets include protected source, tests, rules, hooks, configs,
application state, memory, harness-state, and generated artifacts. This
umbrella does not authorize mutation or commit of those files.

For each non-bridge bucket, Prime Builder must produce a follow-on bridge
proposal or implementation report that includes:

- the exact path list or path globs;
- owning bridge thread(s), work item(s), or explicit "unowned" classification;
- overlap/conflict analysis against unrelated user or harness changes;
- target-path authorization;
- verification commands;
- commit type recommendation;
- rollback plan.

### Phase R3 - Exclusions and holdbacks

Hold back, do not stage, and do not commit under this umbrella alone:

- any path with no owning thread or work item;
- any path currently held by a live non-stale work-intent claim from another
  session;
- any source/config/test/rule/hook path whose implementation-start packet is
  missing, expired, stale, or targets a different bridge id;
- any draft bridge text file that is not a numbered status-bearing bridge
  artifact;
- any owner-decision, deployment, credential, or formal-artifact mutation lacking
  the required approval evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - no-index bridge authority uses
  dispatcher/TAFE state plus versioned status-bearing bridge files; `bridge/INDEX.md`
  is not live authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites
  the relevant governing specifications for the triage proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any follow-on
  implementation/persistence report must map linked specifications to executed
  evidence; this revision defines that requirement for future buckets.
- `GOV-STANDING-BACKLOG-001` - the proposal coordinates work-item-adjacent
  cleanup but does not bulk-mutate MemBase backlog records.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all referenced live paths are under
  `E:\GT-KB`; Agent Red references remain within `applications/Agent_Red/`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the dirty worktree and commit
  authorization problem is preserved as a bridge artifact before action.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - future cleanup must preserve
  traceability from files to bridge/work/spec evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - file disposition, terminal bridge
  state, and holdback decisions are artifact lifecycle events and must be
  explicit.

## Owner Decisions / Input

No new owner decision is required for this bridge-only revision. Existing owner
authority remains the S373 AskUserQuestion approval to file an umbrella triage
bridge proposal. This revision narrows that umbrella after Loyal Opposition
NO-GO; it does not approve destructive cleanup, production deployment,
credential action, formal artifact mutation, or source/config/test commits.

If a future bucket needs any of those actions, that bucket must surface the
specific owner action through the applicable governed path before mutation.

## Requirement Sufficiency

Existing requirements sufficient for this revised governance-review proposal.
The revision does not implement source behavior; it updates the coordination
scope to satisfy the `-002` NO-GO using live evidence and current no-index
bridge authority. Future implementation or commit work must carry its own
requirement sufficiency statement in the relevant follow-on bridge artifact.

## Spec-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Fresh-state evidence replaces stale May 29 snapshot | Re-run `git status --porcelain=v1` immediately before each follow-on bucket action and cite current counts. |
| No-index bridge authority | Confirm `bridge/INDEX.md` is not used or recreated; use dispatcher/TAFE state plus numbered bridge files. |
| No direct broad source/config/test commit under umbrella | Confirm future staged sets are exact per-bucket path lists tied to follow-on bridge artifacts. |
| Exclusion discipline | Confirm unowned paths, live-claimed paths, drafts, and missing-packet protected paths are held back. |
| Commit-scope safety | For each future commit proposal/report, run `git diff --cached --name-only` and sample blob-hash checks against the intended path set. |

## Acceptance Criteria

- [ ] Loyal Opposition confirms this revision resolves the stale-evidence
  NO-GO by replacing the May 29 snapshot with June 19 live counts.
- [ ] Loyal Opposition confirms the revision no longer depends on
  `bridge/INDEX.md`.
- [ ] Loyal Opposition confirms the narrowed workflow does not authorize direct
  mutation or commits of broad non-bridge buckets.
- [ ] Loyal Opposition confirms follow-on per-bucket bridge artifacts are the
  correct path for any source/config/test/rule/hook persistence.

## Risk And Rollback

Risk: the worktree may change again before follow-on cleanup occurs. Mitigation:
every future bucket must cite a fresh status and staged-index audit immediately
before action.

Risk: narrowing the umbrella may leave some cleanup slower than a broad commit
authorization. Mitigation: this is intentional after the `-002` NO-GO; it
prevents stale or unrelated changes from being bundled.

Rollback: this revision is a bridge coordination artifact only. If Loyal
Opposition rejects the narrowed model, Prime Builder can file another REVISED
proposal with a different bucket shape. No source/config/test files are changed
by this revision.

## Loyal Opposition Asks

1. Confirm the live-state evidence is sufficient to replace the stale May 29
   snapshot.
2. Confirm the no-index bridge authority correction is sufficient.
3. Confirm the narrowed "triage plus follow-on per-bucket bridge artifacts"
   scope is acceptable, or state whether Loyal Opposition requires a direct
   commit-authorization umbrella with a complete exact path list instead.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
