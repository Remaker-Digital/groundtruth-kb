REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2b7ecbff-f9cf-437e-a7cb-b436df62ecbd
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-defined ::init gtkb pb
author_metadata_source: open per-session envelope

bridge_kind: implementation_report
Document: gtkb-wi5841-harness-selector-registry-derived
Version: 017
Date: 2026-08-05 UTC
Responds to: bridge/gtkb-wi5841-harness-selector-registry-derived-016.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5841

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_authorization_harness_selector.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_mutation_in_scope: false
tafe_mutation_in_scope: false

# WI-5841 REVISED report — re-request VERIFIED after the evaluation-bound timer was raised

## Revision Claim

This REVISED report responds to version 016 NO-GO. Version 016 recorded:

- **F1 (P1):** atomic VERIFIED blocked because protected-commit authorization
  exceeded `evaluation_bound_seconds` (480s) during phase `per_path`, observed
  **677.2s**. Recommended action: *"Repair/raise the per_path evaluation bound
  ... then REVISED report re-requests VERIFIED. Do not treat as implementation
  defect."*
- **F2 (P2):** implementation substance green (hashes match, tests pass,
  targets clean, finalization PAUTH allows `git_commit`).

This revision does exactly what F1 recommended: it reports that the bound has
since been raised by an independent work item, and re-requests VERIFIED. No
code rework was indicated and none was performed.

## Correction Of The v015 Root-Cause Theory (important)

Version 015 attributed the timer-bound failure to a **stale
`bridge-versioned-files` publication aggregate** and asserted that re-observing
the aggregate removed the condition. **That theory was wrong and is withdrawn
here.** Version 016 falsified it directly: the aggregate was current
(`Stale count 0`) *before* the finalize attempt, and the finalize still failed
at 677.2s against the 480s bound.

The actual cause was the plain one: a full staged evaluation of this cohort
costs ~677s, and the configured budget was 480s. Recording this correction
matters because the v015 theory, left standing, would send the next session to
re-observe an aggregate that was never the problem.

## Explicit Response To F1 (P1) — evaluation bound

The bound was raised by **WI-5839**, landed independently of this thread in
commit `10f0e2eea` (2026-08-04, owner decision `DELIB-20260803084763`):

- `config/governance/protected-commit-timers.toml` now declares
  `evaluation_bound_seconds = 700` and
  `bridge_publication_capability_ttl_seconds = 800`; the file is committed and
  Git-clean.
- Live resolution confirmed this session through the canonical accessor
  `groundtruth_kb.project.timer_config.resolve_protected_commit_timers`:
  `ProtectedCommitTimers(evaluation_bound_seconds=700, bridge_publication_capability_ttl_seconds=800, source='E:\GT-KB\config\governance\protected-commit-timers.toml')`.
- No override exists at either layer above the file: `.env.local` declares
  neither `GTKB_PROTECTED_COMMIT_EVALUATION_BOUND_SECONDS` nor
  `GTKB_BRIDGE_PUBLICATION_CAPABILITY_TTL_SECONDS`, and neither is set in the
  process environment. The 700s value is therefore the effective bound.
- The coupled invariant `evaluation_bound_seconds < capability_ttl_seconds`
  holds (700 < 800).

Against the v016 observation of **677.2s**, the effective budget is now
sufficient. No bypass of the protected-commit gate is requested or performed.

## Known Residual — Disclosed, Not Resolved Here

The margin is **22.8s (3.3%)** between the observed 677.2s and the 700s bound.
`config/governance/protected-commit-timers.toml` itself records run-to-run
variance of 59.4s → 84.3s (~42%) on the pathological corpus, attributed to
concurrent sessions contending for the control-plane lock. A finalize attempt
that lands on a slow run may therefore still exhaust the bound.

This residual is **already tracked and is not re-filed here**:

- `WI-5839` (P0, open) — size the coupled bound/TTL pair against measured
  worst-case pre-commit cost. The 677.2s observation in v016 plus this
  disclosure are fresh evidence for that sizing.
- `WI-5867` (P1, open) — protected-commit authorization gate has an unbounded
  check path.
- `WI-5742 Layer C` (deferred, disclosed in the timer config) — the structural
  cure: mint the publication capability *after* the gates pass, so capability
  lifetime never has to cover a long evaluation.

If this finalize attempt exhausts the bound again, the correct disposition is a
generous coupled raise under `PROJECT-GTKB-TIMER-GOVERNANCE`, not another
implementation revision of WI-5841.

## Explicit Response To F2 (P2) — substance green

Acknowledged; unchanged. Fresh evidence captured this session rather than
carried over from v015:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/scripts/test_bridge_work_intent_registry.py \
  platform_tests/scripts/test_implementation_authorization_harness_selector.py \
  -q --tb=short
-> 62 passed, 5 warnings in 13.06s   (exit 0)
```

The count moved 59 → 62 because WI-5881 added `TEST-11809` coverage to
`platform_tests/scripts/test_bridge_work_intent_registry.py` (see next
section). All 62 pass, including the WI-5841 focused coverage.

## Target Fidelity — Current Live Hashes And A Disclosed Change

Fresh SHA-256 of the four declared targets at this session:

- `scripts/bridge_work_intent_registry.py`
  `C2434A165CB4C7AAEF13021B722D079F8DA31C1FA20D427C3A348D8A7747F20B`
  **(differs from the value recorded in v015)**
- `scripts/implementation_authorization.py`
  `34CEC094B29F218124F5587E0E24CB1F122876C8999497859260B18C42C04A12`
  (unchanged from v015)
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
  `CBB4AA4DA61AB2AD0440F4A340D2A1B4710D76A2E30A9AC69219868B55CEBDF3`
  **(differs from the value recorded in v015)**
- `platform_tests/scripts/test_implementation_authorization_harness_selector.py`
  `0D948A40177506612CE6C3CFC728F33E1BA1DB4CF5207FF84ACDE70E300DD586`
  (unchanged from v015)

**Disclosure of the two changed hashes.** Both changed because **WI-5881**
landed the reservation claim-fence CAS primitive in commit `662361613`
(2026-08-05), which appended 163 lines to `scripts/bridge_work_intent_registry.py`
and 56 test lines to the paired test module. That change is:

- **additive** (insertions only, no deletion of WI-5841 behavior);
- **already committed** in `HEAD`, not uncommitted worktree bytes; and
- **independently authorized** under its own work item and thread.

All four targets are **Git-clean at `HEAD` (`7d6b00f68`)** — verified this
session by `git status --short` returning empty for each path and
`git cat-file -e HEAD:<path>` succeeding for each. WI-5841's own implementation
(the registry-derived harness selector in `scripts/implementation_authorization.py`
and the `sqlite_errorcode` determinism fix in `scripts/bridge_work_intent_registry.py`)
remains intact and is unmodified by the WI-5881 addition.

Because every target is clean and already committed, the VERIFIED finalization
transaction has no source bytes left to stage: it needs only to commit the
terminal verdict artifact itself. Nothing from WI-5881 can be captured by that
commit, since WI-5881's bytes are already in history.

## Out Of Scope (unchanged)

- Dispatcher or TAFE configuration, activation, routing, ranking, eligibility,
  role maps, identities, provider selection, runtime state, lease files, live
  workers, or process control. The dispatch substrate remains `none` and this
  report neither changes nor re-enables it.
- MemBase/database mutation, credentials, deployment, release, push, history
  rewrite, destructive cleanup, or unrelated dirty-byte mutation.
- Raising the evaluation bound or capability TTL. That is WI-5839 / WI-5867
  work and is deliberately not performed from this thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-HARNESS-SELECTOR-REGISTRY-DERIVED-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`

## Spec-To-Test Mapping

| Specification | Derived verification | Evidence this session |
| --- | --- | --- |
| `DCL-HARNESS-SELECTOR-REGISTRY-DERIVED-001` | Harness selection is registry-derived rather than env-sniffed | `platform_tests/scripts/test_implementation_authorization_harness_selector.py` — included in the 62-passed run |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Deterministic typed outcome on claim write-deadline exhaustion (`sqlite_errorcode` propagation) | `platform_tests/scripts/test_bridge_work_intent_registry.py` — included in the 62-passed run |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Effective timer resolved from the canonical accessor, not a cached or assumed value | `resolve_protected_commit_timers` returned 700/800 from the canonical TOML this session |
| `GOV-WORK-TREE-HYGIENE-001` | No uncommitted target bytes at finalization | `git status --short` empty for all four targets; all present in `HEAD` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Executed spec-derived tests precede VERIFIED | 62 passed, exit 0, recorded above |

## Prior Deliberations

- `bridge/gtkb-wi5841-harness-selector-registry-derived-015.md` — prior REVISED
  report; its publication-aggregate root-cause theory is withdrawn above.
- `bridge/gtkb-wi5841-harness-selector-registry-derived-016.md` — NO-GO under
  response here.
- `DELIB-202668153` — Loyal Opposition review, WI-5841 registry-derived harness
  selector.
- `DELIB-20260803084763` — owner decision authorizing the WI-5839 bound/TTL
  raise consumed by this revision.
- `DELIB-202667722` — timer and throttle governance as a first-class concern
  with relaxed-first defaults.

## Recommended Commit Type

`fix` — the implementation is already committed; the finalization transaction
commits the terminal verdict artifact for a defect fix in the harness selector
and claim-registry determinism path.

## Request

**VERIFIED** is re-requested on the basis that (a) the sole blocking finding
F1 was environmental and its cause has been removed by an independent, landed,
owner-authorized change, and (b) the substance finding F2 was already green and
remains green under fresh evidence.

Loyal Opposition is asked to re-run the atomic finalization against the now
effective 700s bound. If that attempt exhausts the bound again, the disclosed
residual above — not WI-5841's implementation — is the correct target, and the
appropriate response is a generous coupled raise under WI-5839 / WI-5867 rather
than a sixth implementation revision of this thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
