REVISED

# WI-4540 (REVISED): Per-session/per-context session-role marker — additive transition design + id-reconciliation adjudication

bridge_kind: prime_proposal
Document: gtkb-wi4540-per-session-role-marker-context-envelope
Version: 003
Author: Prime Builder (Claude Code, harness B — auto-dispatched bridge worker)
Date: 2026-06-14 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T09-21-30Z-prime-builder-B-1a0a0a
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Auto-dispatched cross-harness bridge worker (GTKB_BRIDGE_POLLER_RUN_ID set); Prime Builder durable role (harness B); explanatory output style; model claude-opus-4-8[1m]

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4540-PER-SESSION-MARKER
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-4540

target_paths: ["scripts/workstream_focus.py", "scripts/bridge_work_intent_registry.py", "scripts/session_start_dispatch_core.py", "scripts/session_role_resolution.py", "scripts/gtkb_session_id.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/hooks/test_session_start_marker_invalidation.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

## Revision Scope (why -001's GO needs re-review before implementation)

This REVISED supersedes the `-001` proposal (GO at `-002`). During GO'd implementation, the auto-dispatched Prime worker performed read-only substrate analysis (no source mutation) and found two issues that block faithful implementation of `-001` **as literally specified** within its declared `target_paths`. Both are evidence-based and were verified against live source. The revision keeps the owner-decided per-session-marker direction (advisory AUQ Option A) and the `DELIB-20263212` context-lifetime invariant; it corrects the *transition mechanics* and the *id-reconciliation contract*, and expands `target_paths` to cover the test migration the per-session keying requires.

### Finding A — Change 1 as worded breaks a non-target test (back-compat / scope gap)

`-001` change 1 says: *"Replace the single-file path with a per-session file … Retain the legacy single-file path as a read-only transition fallback."* "Read-only" means the writer **stops writing** `.claude/session/active-session-role.json`.

Evidence: `platform_tests/hooks/test_workstream_focus_session_role_marker.py` (NOT in `-001`'s `target_paths`) asserts the writer **writes** the legacy single file and pins the freshness-heuristic **clobber-rejection** that change 1 removes:
- `test_marker_written_on_interactive_init_keyword` reads `active-session-role.json` after `_consume_discard_first_prompt_gate(...)` (lines 123-131).
- `test_marker_clobber_rejection` asserts a different-session write returns `False` while a fresh marker exists (lines 497-525) — the exact heuristic change 1 deletes.

The mechanical implementation-start gate restricts writes to `target_paths`, and this test file is excluded, so the GO cannot be implemented as worded without breaking the build. `-002`'s verification table itself requires **"no regression"** and **"legacy single-file marker still readable during the transition"** — consistent with an *additive transition*, not a hard cutover. This REVISED resolves the contradiction by (a) adopting an explicitly **additive transition** (legacy writer retained for the transition window; the per-session file becomes the authority the guard/resolver/sweep read), and (b) **adding `platform_tests/hooks/test_workstream_focus_session_role_marker.py` to `target_paths`** so its per-session coverage can be extended without breaking it.

### Finding B — Change 4 id-reconciliation is under-specified and is the load-bearing crux

`-001` change 4 says the writer and guard *"must resolve the SAME context id"* and to *"prefer the live CLAUDE_CODE_SESSION_ID / hook-payload session_id"* — but it does not adjudicate the divergence below, and getting it wrong leaves the lockout unfixed (the per-session keying alone does nothing if the guard looks the marker up under a different id).

Evidence (verified live this session):
- **Marker writer** (`scripts/workstream_focus.py::_resolve_session_id`) is **payload-first**, then `MARKER_CONTINUITY_ORDER = ('GTKB_SESSION_ID','CODEX_SESSION_ID','CODEX_THREAD_ID','CLAUDE_SESSION_ID','CLAUDE_CODE_SESSION_ID')` — `CLAUDE_CODE_SESSION_ID` is **last**.
- **go_implementation guard / claim** (`scripts/bridge_work_intent_registry.py` via the claim's `resolve_session_id`) uses `BRIDGE_WORK_INTENT_ORDER = ('GTKB_BRIDGE_POLLER_RUN_ID','CLAUDE_CODE_SESSION_ID', …)` — `CLAUDE_CODE_SESSION_ID` is **2nd** (1st for interactive, where no poller run-id is set).
- For interactive Claude, the UserPromptSubmit payload `session_id` is the **transcript UUID**, which differs from the `CLAUDE_CODE_SESSION_ID` env var (documented runtime behavior; the proposal's own Defect 2 cites a marker written under `1d33598a…` while the live session was `62a726da…`).

Consequence: the marker is keyed by the transcript UUID, but the guard validates against `CLAUDE_CODE_SESSION_ID` → `current_session_id` mismatch → `durable_marker_stale_session` → "marker role None" → interactive Prime locked out. This is exactly the symptom `-001` describes.

The unresolved tension: the **compaction-stable** id (transcript UUID, constant across the contiguous context per the advisory) and the **guard-claim** id (`CLAUDE_CODE_SESSION_ID`) come from different sources, and whether `CLAUDE_CODE_SESSION_ID` is itself stable across compaction is **not established**. A wrong choice either (i) keys by `CLAUDE_CODE_SESSION_ID` and risks violating the `DELIB-20263212` compaction-survival invariant, or (ii) keys by the transcript UUID and leaves the guard unable to find the marker unless the **claim-side** id resolution (`resolve_session_id` / `scripts/bridge_claim_cli.py`, which is headless-dispatch-coupled) is also changed. This is a load-bearing, *implementation-authority-gating* decision; the dispatched worker will not guess on it.

## Proposed Resolution (for Loyal Opposition adjudication)

### R-A (Finding A): additive transition, not hard cutover
1. `scripts/workstream_focus.py`: the writer continues to write the legacy single file (existing `_write_session_role_marker`, unchanged → all current unit tests stay green) AND additionally writes a per-session file `.claude/session/role-<sanitized_session_id>.json` (new, no clobber-rejection — per-session means no contention). Keep `_session_role_marker_path(project_root)` returning the legacy path (path-parity tests stay green); add a separate per-session path helper.
2. Read paths (`session_role_resolution.py`, `bridge_work_intent_registry.py`) read the per-session file first, legacy single file as fallback — preserving the `-002` "legacy still readable" criterion.
3. `platform_tests/hooks/test_workstream_focus_session_role_marker.py` (newly in scope) gains per-session-write coverage without removing its legacy assertions.

### R-B (Finding B): canonical interactive context-id + matched guard lookup
Adopt the **transcript UUID** (the documented compaction-stable id) as the canonical interactive context id for BOTH writer and guard, and make the guard discover the marker under that id. Two implementable sub-options for LO to choose:
- **R-B1 (preferred):** the writer keys the per-session marker under the transcript UUID AND, defensively, also under each currently-set env candidate (incl. `CLAUDE_CODE_SESSION_ID`) so the guard's claim-id lookup matches during the transition; the guard accepts a per-session marker whose recorded `session_id` matches the querying id. (Keeps `scripts/bridge_claim_cli.py` out of scope.)
- **R-B2:** unify `resolve_session_id`'s interactive precedence so the claim path and the marker writer resolve the identical id; this implicates `scripts/gtkb_session_id.py` ordering and its drift-lock test, and must preserve headless `GTKB_BRIDGE_POLLER_RUN_ID`-first behavior.

LO is asked to confirm R-B1 vs R-B2 and to confirm the canonical-id choice, since it gates whether the compaction-survival invariant and the guard match can both hold. Changes 2 (context-id-scoped SessionStart sweep), 3 (session-id-validating guard reader), and 5 (stale-marker sweeper) are unchanged from `-001` and are not blocked by either finding.

### In-flight work preserved (carried from `-002` constraint #2)
`scripts/bridge_work_intent_registry.py` contains live WI-4527 `maybe_auto_extend` changes (lines 519-579). The implementation will merge around them, never overwrite or stage them as WI-4540.

## Specification Links

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — interactive-session role-override contract; per-context keying realizes it; the additive transition preserves the `-002` no-regression criterion.
- `DCL-SESSION-ROLE-RESOLUTION-001` — deterministic marker>durable resolution table; the session-id-validating reader (change 3) enforces assertion 6 uniformly; R-B fixes the id under which the assertion is evaluated.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable-vs-stated authority split; unchanged (headless dispatch still keys to the durable role).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant governing specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage triple cites the bounded WI-4540 PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps each behavior to a spec-derived test.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the change preserves the WI-4534 write-time guard; it removes the false-negative (marker-not-found), not the enforcement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — no `bridge/INDEX.md` write surface; the marker fix restores interactive Prime's ability to hold `go_implementation` claims through the governed claim path.
- `GOV-STANDING-BACKLOG-001` — `WI-4540` is the backlog authority (P2, defect, `bridge_dispatch`); also addresses `WI-4463` and the advisory's Defect 2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all `target_paths` are in-root (`scripts/`, `platform_tests/`).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — durable, tested fix; advisory→proposal lifecycle; explicit deferral of the contract-doc revision.

## Requirement Sufficiency

Existing requirements sufficient for the *source mechanics*. The owner's context-lifetime invariant is durably captured in `DELIB-20263212`; `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` / `DCL-SESSION-ROLE-RESOLUTION-001` govern the resolution mechanics. The R-B id-reconciliation choice is a *technical-design* adjudication for Loyal Opposition (which id is canonical; R-B1 vs R-B2), not a new owner requirement. The canonical-terminology + `DCL-SESSION-ROLE-RESOLUTION-001` contract-doc revision aligning the documented "does not survive compaction or resume" clause remains a deferred follow-on with its own `narrative-artifact-approval` + `formal-artifact-approval` packets (outside this PAUTH's `source` + `test_addition` scope).

## Prior Deliberations

- `bridge/gtkb-session-role-marker-architecture-advisory-001.md` (ADVISORY, prior interactive PB session `7752bc97`, 2026-06-14 ~06:42Z) — the umbrella advisory converted by `-001`. Owner AUQ chose per-session marker files (Option A; rejected Option C minimal-patch and Option D defer). This REVISED preserves Option A; it does not revert to the rejected minimal patch.
- `DELIB-20263212` (2026-06-14) — owner context-lifetime envelope requirement + "author now, anchor on WI-4540". Source of the compaction-survival invariant that R-B must not violate.
- `bridge/gtkb-wi4540-per-session-role-marker-context-envelope-001.md` / `-002.md` — the `-001` proposal and its `-002` GO; this `-003` REVISES `-001` per Findings A and B discovered during GO'd implementation.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-003.md` — Slice 2 landed the single-file marker writer being amended (additively).
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation` thread — Slice 3 landed the unconditional SessionStart invalidation; change 2 amends it to be context-id-scoped.
- `WI-4534` (guard), `WI-4463` (attribution bleed), `WI-4527` (`maybe_auto_extend`, in-flight, preserved) — related work; declared work item is `WI-4540`. No additional prior deliberations were found for the per-session-marker / session-id-resolution topic beyond these (`search_deliberations` returned no further matches).

## Owner Decisions / Input

Authorized by durable owner-decision evidence; **no new owner AskUserQuestion is pending** to file this REVISED. The findings are technical-design and back-compat scope corrections within the existing PAUTH; the only added decision is a Loyal-Opposition technical adjudication (R-B1 vs R-B2), not an owner decision.

- `DELIB-20263212` — owner AUQ (2026-06-14): "Capture spec + scope fix now" then "Author now, anchor on WI-4540". Authorizes this conversion/revision under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4540-PER-SESSION-MARKER` (allowed: `source` + `test_addition`; forbids formal-artifact, narrative-artifact, KB bulk status, config/hook registration, deploy/release, force pushes, credential lifecycle). Adding `platform_tests/hooks/test_workstream_focus_session_role_marker.py` to `target_paths` stays within `test_addition`.
- The prior advisory's owner AUQ (2026-06-14 ~06:42Z) — per-session marker files (Option A), P1, drive implementation. Preserved; this REVISED does not change the owner-decided direction.

## Spec-Derived Verification Plan

Run with the repo venv (`-o addopts=` per the venv's missing `pytest-timeout`):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/hooks/test_session_start_marker_invalidation.py platform_tests/hooks/test_workstream_focus_session_role_marker.py -q
```

| Behavior / spec | Test |
|---|---|
| Per-context marker write+read round-trips for the querying session id (DCL-SESSION-ROLE-RESOLUTION-001) | per-session keying write/read test |
| Legacy single-file marker still WRITTEN and READ during the transition (no regression — Finding A) | legacy-write + legacy-fallback tests (existing, retained) |
| A peer session's SessionStart invalidation does NOT delete another live session's marker (WI-4463; advisory Defect 1) | concurrent-session non-interference test |
| The current context's marker SURVIVES a SessionStart carrying the same context id; a different/stale context id is swept (DELIB-20263212) | context-id-scoped invalidation test |
| The WI-4534 guard's interactive branch validates session-id and finds the marker under the canonical interactive id (Finding B / R-B) | guard validated-reader test |
| Stale marker (transcript mtime older than threshold) swept; live one retained | sweeper test |

Plus `ruff check` and `ruff format --check` on every changed file. The full session-role substrate suite (the ~10 sibling test files referencing the marker/guard) must also pass — the additive design is chosen specifically so none regress.

## Risk / Rollback

- **Risk — additive dual-write leaves the legacy file's clobber-rejection latent.** Accepted for the transition: the legacy file is no longer the guard authority (guard reads per-session first), so the legacy clobber-rejection cannot lock out an owner-Prime session.
- **Risk — R-B id choice wrong → invariant or guard breaks.** Mitigated by deferring the R-B1/R-B2 choice to LO adjudication before implementation, plus a dedicated dispatched-eligibility-preserved test.
- **Rollback.** Additive — the per-session write and per-session read are layered on top of unchanged legacy behavior; a single-commit revert restores prior behavior. No KB schema change, no bridge-authority change, no hook registration change.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` with a `REVISED` entry inserted at the top of the `gtkb-wi4540-per-session-role-marker-context-envelope` document list in `bridge/INDEX.md`; append-only. `bridge/INDEX.md` remains canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs two coupled reliability defects (cross-session marker clobber + mid-context vanish/lockout) blocking interactive owner-Prime implementation. Per-session keying + id reconciliation are structural changes in service of the fix.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
