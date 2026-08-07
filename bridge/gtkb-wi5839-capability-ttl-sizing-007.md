NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6d5cabf5-dc7d-418a-a495-6f23186a6638
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role via ::init gtkb pb; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

# GT-KB Bridge Implementation Report — WI-5839 configured-value slice — 007

bridge_kind: implementation_report
Document: gtkb-wi5839-capability-ttl-sizing
Version: 007
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5839-capability-ttl-sizing-006.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5839

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/timer_config.py", "config/governance/protected-commit-timers.toml", "platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py"]
implementation_scope: centralized_capability_ttl_configuration_and_mint_admission_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This implementation performs no MemBase or KB mutation, write, insert, change or edit of any kind.

## Scope Delivered And Scope Deliberately Deferred

**Exactly one of the four declared target paths changed:** `config/governance/protected-commit-timers.toml`. The other three are untouched.

This report claims **only the configured-value portion** of Slices A and B — setting the coupled pair to a generous, evidence-supported posture and correcting the surrounding documentation. It does **not** claim:

- Slice A resolver hardening (removing production default/ceiling/headroom declarations from `registry_control_plane.py`, forbidding silent fallbacks in `timer_config.py`);
- Slice B snapshot-coherence rejection rules beyond the already-implemented paired-bound check;
- Slice C mint-time admission; or
- Slice D the dedicated `test_bridge_publication_capability_ttl_sizing.py` module.

Acceptance criteria covering those slices are **not claimed** by this report.

The reason for the split is recorded in the Owner Decisions section: Slice C necessarily edits `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, and that file currently carries uncommitted WI-5825 Change B bytes. WI-5839's own Mandatory Ordering and Collision Ledger requires that file to be clean before WI-5839 touches it. Editing it now would commingle two threads in one file and would commit WI-5825's implementation under WI-5839's authority. The configured-value change needs none of that, so it is delivered alone.

## Why This Change Is Needed Now

Two terminal verdicts were denied on 2026-08-06 by the protected-commit evaluation bound, both with green substance:

- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-010.md` — "Independent substance checks passed where claimed, but atomic VERIFIED finalization failed closed."
- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-014.md` — "Substance remains green (17 passed; timers 700/800; targets clean; waiver packet hash matches)."

The WI-5825 denial quoted the gate verbatim:

```text
FAIL protected-commit authorization
  - <evaluation-bound>: protected-commit evaluation exceeded its configured 700s
    wall-clock bound while executing phase 'per_path'
    evidence error: elapsed: 721.6s
    evidence error: configured bound: 700s
```

### The prior sizing basis no longer describes this repository

The measurement block preserved in the configuration file records the WI-5742 basis: an 812-path staged corpus, and "post-fix, realistic 7-path staged finalization: 38.744s wall". The observed 2026-08-06 finalization was an 8-path staged set at **721.6s** — roughly 18x the recorded realistic case for a comparable path count.

The variable that moved is the bridge aggregate, not the staged set. `ls bridge/*.md | wc -l` returns **15,417** files. The gate's full-check path loads terminal-VERIFIED bridge evidence across that aggregate, so its cost tracks corpus growth rather than the number of staged paths. That is the condition WI-5867 describes as an unbounded full-check path.

## Change Implemented

`config/governance/protected-commit-timers.toml`:

1. `evaluation_bound_seconds` raised **700 -> 790**. The coupled invariant requires the bound to be strictly less than the paired capability TTL of 800, so 790 is the most relaxed value representable while that TTL holds. It clears the 721.6s observation by 68.4s.
2. The `evaluation_bound_seconds` comment block replaced. It previously read "110s is ~2.8x the realistic 7-path finalization cost (38.7s) ... while holding 10s under the paired TTL" beside a live value of 700 — describing neither the live value nor the live TTL. It now records the 2026-08-06 failure evidence, the corpus size, the derivation of 790, and an explicit disclosure that this is a ceiling rather than a fix.
3. The `bridge_publication_capability_ttl_seconds` comment corrected. It previously read "must be >= 1 and <= 300. The 300-second ceiling mirrors the hard rejection in `mint_bridge_publication_capability`" beside a live value of 800 and a live `_CAPABILITY_TTL_CEILING_SECONDS = 800`. That drift understated the available envelope by 500 seconds to anyone sizing the pair.

No production code, resolver logic, ceiling constant, or mint behavior was changed. No timer value other than the bound was changed.

## Executed Verification

```text
python -c "from groundtruth_kb.project.timer_config import resolve_protected_commit_timers; print(resolve_protected_commit_timers())"
ProtectedCommitTimers(evaluation_bound_seconds=790, bridge_publication_capability_ttl_seconds=800,
                      source='E:\GT-KB\config\governance\protected-commit-timers.toml')
INVARIANT OK: bound 790 < 800
headroom over observed 721.6s: 68.4 seconds

python -m pytest platform_tests/scripts/test_protected_commit_evaluation_bound.py platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_timer_inventory.py -q --tb=short
1 failed, 46 passed, 2 skipped

git status --short -- <the four declared targets>
 M config/governance/protected-commit-timers.toml
```

| Requirement | Evidence | Result |
|---|---|---|
| Coupled pair resolves from the single SoT through the typed resolver | `resolve_protected_commit_timers()` returns 790/800 with the config file as `source` | pass |
| Paired invariant `bound < TTL` holds after the change | asserted in the command above | pass |
| Configured posture is generous and supported by fresh evidence | 790 clears the measured 721.6s denial by 68.4s; derivation recorded in the file | pass |
| Ongoing tuning changes the SoT, not production code | only the TOML changed; three declared targets untouched | pass |
| No new hard-coded timer literal enters production code | no source file modified | pass |
| Documentation matches runtime | both stale comment blocks corrected against live values | pass |

### Disclosed pre-existing failure (not caused by this change)

`test_protected_commit_evaluation_bound.py::test_capability_ttl_ceiling_matches_mint_time_rejection` fails, and it failed before this change. It asserts that a configured TTL of 301 is rejected against "the 300s mint-time ceiling", but the live ceiling is `_CAPABILITY_TTL_CEILING_SECONDS = 800` in `timer_config.py`. The test is hermetic — it writes its own configuration under `tmp_path` and clears both override environment variables — so this repository's configuration cannot influence it. A direct repro confirms a TTL of 301 resolves successfully against the live ceiling.

The test went stale when the ceiling moved from 300 to 800 and was not updated. It is **outside this thread's declared `target_paths`**, so it is disclosed here rather than repaired under this authority. Repairing it belongs with Slice D.

## Known Residual, Disclosed

This change buys headroom; it does not remove the failure mode.

- Remaining envelope in the config-only lane is 68.4 seconds over the last observation, and the bound cannot be raised to or past the 800s TTL — the accessor rejects that outright because it re-creates the publication-stranding precondition documented in the file and across WI-5368, WI-5758, WI-5759 and WI-5824.
- Raising the TTL above 800 requires changing the mint-time ceiling, which is Slice C and is deferred.
- Because gate cost now scales with a 15,417-file bridge corpus that continues to grow, this bound is expected to be reached again. The durable remedy is **WI-5867** (bound and cache the unbounded full-check path). A WI-5867 proposal is the intended follow-on.
- `WI-5742 Layer C` (mint the capability after the gates pass, so capability lifetime never covers the long evaluation) remains the structural removal of the residual and is unchanged by this report.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the finalization path this bound gates.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active list-free PAUTH cited in this header, operation-time gated.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time evaluation recorded in the start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried forward from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed evidence presented above.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item and exact target linkage.
- `GOV-ENV-LOCAL-AUTHORITY-001` — the env-local override layer named in the resolution precedence this file documents.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every claim here derives from a fresh canonical read this session.
- `GOV-WORK-TREE-HYGIENE-001` — exactly one declared path changed; nothing outside the declared set.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable traceability and the GO to post-implementation lifecycle transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the changed path is in-root.
- `GOV-STANDING-BACKLOG-001` — WI-5867 remains the separate tracked carrier for the durable fix; no duplicate carrier is created here.

## Prior Deliberations

- `DELIB-202667722` — timer and throttle governance as a first-class concern with relaxed-first defaults; this change follows its relaxed-first posture and changes the SoT rather than production code.
- `DELIB-20260803084763` — the prior owner decision that raised the bound to 700 and the TTL to 800.
- `bridge/gtkb-wi5839-capability-ttl-sizing-006.md` — the GO authorizing this implementation.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-010.md` — the denial evidence quoted above.
- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-014.md` — the second blocked finalization.
- `bridge/gtkb-wi5715-registry-read-scalability-008.md` — VERIFIED, which cleared ordering item 1 of this thread's collision ledger.

## Owner Decisions / Input

This report depends on owner approval for its scope split. The authorizing evidence is:

1. **AskUserQuestion, 2026-08-06, timer deadlock.** Question: WI-5825 finalization is blocked by the 700s bound; raising it is WI-5839's job, but WI-5839 needs `registry_control_plane.py` clean and it holds uncommitted Change B — how should Prime Builder break this? Owner answer: **"Config-only bound raise now, then propose WI-5867"** — change only the TOML under WI-5839's existing GO, raise the bound to just under the paired TTL, correct the stale comments, then file a WI-5867 proposal for the durable fix. This is the sole authority for delivering the configured-value portion alone and deferring Slices A, C and D.
2. **Standing owner directive on timers** — be generous with timers and throttles, and file a correction work item for any evidence-based undersized value unless it is already tracked. The undersized bound is already tracked by this work item and by WI-5867, so no duplicate carrier was created.
3. **`DELIB-202667731`-class project authority** — the active list-free whole-project PAUTH cited in this header covers the configuration mutation class.
4. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This change does not activate, dispatch through, configure, or mutate either.

No new owner decision is requested by this filing.

## Requested Loyal Opposition Action

Verify the configured-value slice and record **VERIFIED**, or **NO-GO** with concrete findings. Reviewers are specifically asked to check:

1. That 790 is the correct maximum under the coupled invariant given the paired TTL of 800, and that the derivation from the 721.6s observation is sound.
2. That delivering the configured-value portion alone is acceptable, with Slices A, C and D explicitly not claimed, given the collision-ledger constraint on `registry_control_plane.py`.
3. That the disclosed pre-existing `test_capability_ttl_ceiling_matches_mint_time_rejection` failure is correctly attributed as stale and out of scope rather than introduced here.
4. That the residual disclosure is honest about this being a ceiling rather than a fix.

Note for finalization: this thread's own atomic VERIFIED will itself be gated by the bound this report raises. The raised value is read live from the configuration file, so it applies to the verifying transaction.

## Recommended Commit Type

Recommended commit type: `fix` — repairs an undersized governance timer that was denying valid terminal verdicts, plus documentation that had drifted from live values. No capability surface is added and no production code changes.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
