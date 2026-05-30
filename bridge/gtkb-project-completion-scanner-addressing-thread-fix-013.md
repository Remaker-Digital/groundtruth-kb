REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-project-completion-scanner-addressing-thread-fix-revised-5
author_model: claude-opus-4
author_model_version: 4.8
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Implementation Proposal - Project-Completion Scanner Addressing-Thread Fix (v4: project-scoped D4 implements-gate; D3 corrected) (WI-3365) (REVISED-5)

bridge_kind: implementation_proposal
Document: gtkb-project-completion-scanner-addressing-thread-fix
Version: 013 (REVISED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Session: S372
Responds to NO-GO: bridge/gtkb-project-completion-scanner-addressing-thread-fix-012.md

Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Work Item: WI-3365
Implements: WI-3365

Supersedes implementation thread: bridge/gtkb-s358-w1-retirement-machinery-correction (latest GO -019; per S372 owner AUQ - "Supersede v3 (Recommended)")

target_paths: ["scripts/project_verified_completion_scanner.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/hooks/test_project_completion_surface.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json"]

Recommended commit type: feat:

## REVISED-5 Changes (closes NO-GO -012 F1 + F2)

NO-GO -012 (Codex verification of the -011 post-implementation report) raised two findings. Both are Prime-acknowledged as correct. This REVISED-5 corrects the design BEFORE re-implementing; per the codex-review-gate the corrected design is routed back to Codex for a fresh GO because the D4 discriminator's behavioral contract changes (global-slug to project-scoped) and the authorization scope expands (F2).

### F1 (P0) — D4 gate was global by thread slug, not project-scoped

The -011 implementation built a single global `set[slug]` of all implements-linked threads, then unioned every `Work Item:` line from those threads into one global verified set. That discards the project dimension: a thread implements-linked to PROJECT-A could complete and retire a PROJECT-B authorization whenever the thread cited a PROJECT-B gating WI — even though PROJECT-B never implements-linked that thread. This re-introduced the same cross-context false-positive-retirement class v4 exists to eliminate, narrowed from "any VERIFIED thread" to "any implements-linked VERIFIED thread for any project."

The v4 spec text (UNCHANGED) already requires the correct semantics — criterion 1: "a bridge thread T linked to **WI-X's project P**." The defect was purely in the -011 implementation, which collapsed the project dimension. The spec is correct; the code must honor it.

**Correction:** coverage is computed project-scoped as `dict[project_id, set[work_item_id]]`. A work item WI-X is VERIFIED *for project P* iff P holds an active `relationship='implements'` link to a VERIFIED-topped thread that cites WI-X. A link held by a different project does not transfer coverage.

**Pre-filing validation evidence** (read-only synthetic two-project fixture, scratch — deleted after capture):

```text
=== BUGGY global-slug set (current -011) ===
  implements_slugs (no project context): ['thread-a']
  -> verified_work_items() unions thread-a's WIs globally -> WI-8002 enters the GLOBAL verified set
  -> PROJECT-B (gating {WI-8002}) FALSELY completion-ready  [F1 defect]

=== CORRECTED project-scoped map ===
  PROJECT-A: implements-linked slugs = ['thread-a']
  PROJECT-B: implements-linked slugs = []
  -> PROJECT-A verified = thread-a's WIs (WI-8002 counts for A only)
  -> PROJECT-B verified = {} (no implements link) -> PROJECT-B NOT completion-ready  [F1 fixed]
```

The single mechanical change at the SQL layer is adding `project_id` to the SELECT and grouping by it in Python; the rest is threading `project_id` through to the completion decision instead of collapsing it.

### F2 (P1) — one edited test file was outside the implementation-start target paths

The -011 implementation edited `platform_tests/hooks/test_project_completion_surface.py` (a fixture-only seed update so the 3 pre-existing hook tests keep passing under the v4 gate) but that path was not in the GO'd -009 target_paths. Codex correctly declined to record VERIFIED while a known out-of-envelope file mutation existed.

**Correction:** `platform_tests/hooks/test_project_completion_surface.py` is added to `target_paths` (the 7th path) so the hook-test fixture update is bridge-authorized. The hook SOURCE files (`.claude/hooks/project-completion-surface.py`, `.codex/gtkb-hooks/project-completion-surface.py`) remain byte-unchanged; only the test fixture's seed gains the project-scoped `implements` link.

### What is UNCHANGED from the -009/-011 work

- The v4 spec text of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` is UNCHANGED (already project-scoped at criterion 1). The v4 row is already inserted in MemBase (version 4, current) and the owner-approved formal-artifact packet (sha256 `bf4baac820fe4b2a6877a38eee92bb1e8caa59dd83c87666ef0c6232bf9cef7f`) already exists. **No v4 re-insertion and no new packet are required** (Codex Required Revision #5: packet/row consistency only if the v4 text or packet changes — it does not). `groundtruth.db` and the packet path remain in `target_paths` for continuity but are not re-touched.
- D3 correction (per-thread all-versions scan, NOT top-version-only) is unchanged.
- The fail-safe direction (auto-completion paused, never spurious retirement) is unchanged.
- Phase-2 separate backfill remains a follow-on thread.
- The supersession of `gtkb-s358-w1-retirement-machinery-correction` per S372 owner AUQ is unchanged.

## Summary

The project-verified-completion automation auto-completes a project authorization and retires its project when its gating work items are all VERIFIED. v4 makes the "VERIFIED work item" determination deterministic and project-scoped via the `implements` bridge-thread link. REVISED-5 corrects the -011 implementation defect (F1) so coverage is attributed to the linking project only, and authorizes the hook-test fixture update (F2).

- **D4 (project-scoped `implements`-linkage gate — load-bearing discriminator)**: WI-X is VERIFIED *for project P* only when P itself implements-links a VERIFIED-topped thread citing WI-X. Cross-project leakage is impossible.
- **D3 (corrected)**: scan the implements-linked thread's versions (all versions, not the top-verdict-only which carries no `Work Item:` metadata).
- **Fail-safe**: absent any `implements` link covering a project's gating WIs, auto-completion does NOT fire; the condition surfaces for manual review (project-scoped: computed per project).

## Owner Decisions / Input

- **S372 AUQ (this session)**: owner selected "Supersede v3 (Recommended)"; "Full D3+D4 + Phase-2 backfill" (backfill scope); the v4 scanner fix as highest-leverage work. These authorize the v4 work and the supersession.
- **S372 AUQ #2 (this session)** = "Approve as shown" on the v4 spec text + sha256 `bf4baac820fe4b2a6877a38eee92bb1e8caa59dd83c87666ef0c6232bf9cef7f`. The v4 spec content is owner-approved and already inserted; REVISED-5 does NOT change the v4 text, so no new owner approval of spec content is required. The owner-approved packet remains valid.
- **S358 owner-decision** (`DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION`): standing S358 PAUTH covers this governance-correction work; includes WI-3365 and `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.
- No NEW owner decision is required for this REVISED-5: F1 is a code-correctness fix and F2 is a target-path scope correction; neither changes owner-facing governance semantics.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 (current `specified`) — the spec whose project-scoped criterion 1 the corrected implementation honors; text UNCHANGED.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant cross-cutting spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-to-Test Mapping maps each behavioral claim, including the new cross-project regression, to executable tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + PAUTH header present; WI-3365 active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — govern the project-scoped authorization vehicle.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — the v4 GOV mutation's formal-artifact packet (already generated + owner-approved; unchanged in this revision).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook source files unchanged; the hook-test fixture (now in target_paths) gains the project-scoped implements-link seed; parity preserved.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root under the platform root; no `applications/**` mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable scanner/lifecycle changes + regression tests; full traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-3365 lifecycle advances on the corrected post-impl report.
- `GOV-STANDING-BACKLOG-001` — WI-3365 active under PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the project-scoped D4 discriminator is deterministic (SQLite query, no LLM).
- `SPEC-AUQ-POLICY-ENGINE-001` — supersession + v4 spec content owner-authorized via AskUserQuestion.

## Requirement Sufficiency

Existing requirements sufficient. The v4 spec text (the `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` revision with the project-scoped `implements`-link discriminator) is already inserted into MemBase and is UNCHANGED by this revision; no additional requirement gathering is needed before implementation. REVISED-5 is a code-correctness fix (F1) plus a target-path scope correction (F2) that bring the implementation into conformance with the already-approved v4 requirement. No new GOV/SPEC/ADR/DCL is required.

## KB Mutation Scope

NO new KB mutation in this revision. The v4 row of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` was already inserted (version 4 current) under the -011 implementation with the owner-approved packet. REVISED-5 changes only Python source + tests. `groundtruth.db` and the packet path remain in `target_paths` for continuity with the prior GO but are not re-mutated. If Codex prefers, they can be dropped from `target_paths`; Prime kept them to avoid a spurious scope-narrowing relative to the -010 GO.

## WI Citation Disclosure

Declares work for **WI-3365** only. WI-3438 (v3-misfire evidence), WI-3442 (sibling classifier-fix WI), and `gtkb-s358-w1-retirement-machinery-correction` bridge references are context only, not implementation declarations.

## Prior Deliberations

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` — S358 owner-decision authorizing governance-correction work (covers v3→v4).
- `DELIB-2502` — the reauth VERIFIED thread that triggered the v3 misfire loop; concrete defect evidence.
- `DELIB-2503` — owner AUQ chain for the comprehensive D3+D4+v4 scanner-fix vehicle and focused PAUTH direction.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic project-linkage discriminator over session judgment.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-012.md` (Codex NO-GO this thread) — the F1 (P0 project-scoping) + F2 (P1 target-path) findings this REVISED-5 closes.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-010.md` (Codex GO of REVISED-4) — the GO under which -011 was implemented; its global-slug design sketch is corrected here.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-011.md` (Prime post-impl report) — the implementation NO-GO'd at -012; the v4 row + packet it produced remain valid and unchanged.
- `bridge/gtkb-s358-w1-retirement-machinery-correction-019.md` (Codex GO of v3 impl; superseded per S372 owner AUQ).

## v4 Spec Text (UNCHANGED — already inserted as GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4)

The v4 spec text is UNCHANGED from -009/-011 and is already the current MemBase row (version 4). It is reproduced here for review continuity; it is NOT re-inserted by this revision. Its criterion 1 already mandates the project-scoped semantics that REVISED-5's code now honors.

```
**Rule.** A backlog project — and its project authorization — is completed
and retired, together with all of the project's associated work items,
automatically when, and only when, every work item explicitly linked to that
project is VERIFIED. As long as any explicitly-linked work item is not
VERIFIED, the project cannot be completed or retired. Completion and
retirement require no owner AskUserQuestion confirmation; the transition is
automatic on the all-work-items-VERIFIED condition. Retirement is collective.

**Owner-AUQ boundary.** Owner AskUserQuestion approval gates project start
(see GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 and
GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001). Owner-AUQ does not gate
project completion or retirement.

**"VERIFIED work item" definition (v4 — deterministic, implements-gated).**
A work item WI-X is VERIFIED when ALL of the following hold:

1. There exists a bridge thread T linked to WI-X's project P via a
   project_artifact_links row with artifact_type = 'bridge_thread',
   artifact_ref = T's slug, relationship = 'implements', and an active
   status (the explicit "addressing thread" linkage, distinct from the
   default 'related' and from incidental 'implementation_proposal' or
   'source_evidence' links).
2. T's top status in bridge/INDEX.md is VERIFIED.
3. WI-X appears in a `Work Item:` metadata line in one of T's version files.

**Fail-safe behavior (v4).** If a project P has gating work items but NO
'implements'-linked VERIFIED bridge thread covers all of them, the
auto-completion pass does NOT fire; P is NOT auto-retired; the condition is
surfaced as a manual-review notification.
```

(The full v4 text — including the "Why not top version only", Supersession, Backfill, and implementation-contract paragraphs — is the current MemBase row and unchanged. The implementation contract clause (a) "linked to ... the thread's slug" is now honored project-scoped: the link must belong to the project whose authorization is being decided.)

## Proposed Scope

### IP-1: project-scoped D4 in scripts/project_verified_completion_scanner.py

Replace the global-slug helper with a project-scoped map, and replace the global `verified_work_items()` decision function with a project-scoped one. The global `verified_work_items()` is REMOVED (it is the footgun that produced F1; no production caller other than the scanner's own `scan()` used it, and `scan()` switches to the project-scoped function).

```python
def _implements_links_by_project(project_root: Path) -> dict[str, set[str]]:
    """Return {project_id: {bridge_thread_slug}} for active implements links.

    v4 project-scoped discriminator: coverage from a thread T accrues ONLY to
    the project(s) that themselves hold an active project_artifact_links row
    (artifact_type='bridge_thread', relationship='implements', status='active')
    for T's slug. A link held by a different project does not transfer (F1).
    """
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return {}
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute(
            "SELECT project_id, artifact_ref FROM current_project_artifact_links "
            "WHERE artifact_type = 'bridge_thread' "
            "AND relationship = 'implements' "
            "AND status = 'active'"
        ).fetchall()
    finally:
        con.close()
    out: dict[str, set[str]] = {}
    for project_id, slug in rows:
        if project_id and slug:
            out.setdefault(str(project_id), set()).add(str(slug))
    return out


def _verified_thread_work_items(project_root: Path) -> dict[str, set[str]]:
    """Return {bridge_thread_slug: {work_item_id}} for VERIFIED-topped threads,
    scanning ALL versions for Work Item metadata (D3 corrected scope)."""
    # parse_index; for each document whose current_top.status == VERIFIED,
    # union the Work Item: lines across every version file into wis_by_thread[slug].


def verified_work_items_by_project(project_root: Path) -> dict[str, set[str]]:
    """Return {project_id: {verified work_item_id}} (project-scoped, closes F1)."""
    links = _implements_links_by_project(project_root)
    wis_by_thread = _verified_thread_work_items(project_root)
    out: dict[str, set[str]] = {}
    for project_id, slugs in links.items():
        verified: set[str] = set()
        for slug in slugs:
            verified |= wis_by_thread.get(slug, set())
        out[project_id] = verified
    return out
```

In `scan()`, the per-authorization loop uses the project's own verified set:

```python
    verified_by_project = verified_work_items_by_project(project_root)
    for authorization in active:
        project_id = str(authorization.get("project_id") or "")
        included = gating_by_project.get(project_id, [])
        project_verified = verified_by_project.get(project_id, set())
        verified_ids = [wi for wi in included if wi in project_verified]
        unverified_ids = [wi for wi in included if wi not in project_verified]
        completion_ready = bool(included) and not unverified_ids
```

### IP-2: project-scoped mirror + fail-safe in groundtruth-kb/src/groundtruth_kb/project/lifecycle.py

The service gains the same project-scoped primitives (`_implements_links_by_project()` via `self.db`, `_verified_thread_work_items()`, `_verified_work_items_by_project()`), plus a global v3 baseline `_all_verified_work_items()` used ONLY by the fail-safe diagnostic to compute "what v3 would have covered." `_authorization_completion_ready(authorization, verified_for_project: set[str])` now receives the project's own verified set (the caller looks it up by `project_id`). `complete_project_authorization()` and `auto_complete_ready_authorizations()` use the project-scoped map for all completion decisions.

The fail-safe surface (`include_fail_safe_pauses=True`, default-off to keep the byte-identical hooks' return shape per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`) emits a `manual_review_required` record when an authorization would complete under the v3 global baseline but is correctly held under the v4 project-scoped set. `covered_under_v3` / `missing_under_v4` are computed from the global baseline vs the project-scoped set.

### IP-3: Phase-2 backfill is a SEPARATE bridge (unchanged)

The `implements`-link backfill for existing projects remains a separate, reviewable Phase-2 bridge filed after this lands VERIFIED. The fail-safe makes this safe: until Phase-2 backfills links, auto-completion is paused (no spurious retirement).

### IP-4: v4 GOV spec mutation — ALREADY DONE (no re-insertion)

The v4 row was inserted under the -011 implementation (version 4 current; owner-approved packet `2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json`, sha256 `bf4baac8...cef7f`). The v4 text is UNCHANGED, so no re-insertion occurs. The post-impl report will re-confirm the row is current.

### IP-5: Regression and unit tests (existing v4 tests updated to project-scoped API; cross-project regression added)

`platform_tests/scripts/test_project_verified_completion_scanner.py`:
1. `test_incidental_citation_thread_does_not_complete_wi` (updated to project-scoped API).
2. `test_implements_linked_thread_completes_wi` (updated).
3. `test_top_verdict_has_no_work_item_line_but_report_does` (D3 regression; updated).
4. `test_fail_safe_no_implements_link_no_completion` (updated).
5. **NEW** `test_cross_project_implements_link_does_not_satisfy_other_project` — PROJECT-A implements-links thread-a (citing WI-8002); WI-8002 gates PROJECT-B; PROJECT-B has NO implements link. Assert PROJECT-B is NOT completion-ready and PROJECT-A's coverage is correct. This is the direct F1 regression.

`groundtruth-kb/tests/test_project_artifacts.py`:
6. `test_lifecycle_verified_work_items_implements_gate` (updated to `_verified_work_items_by_project` + `_all_verified_work_items`).
7. `test_auto_complete_fail_safe_emits_manual_review` (updated to project-scoped fail-safe).
8. **NEW** `test_auto_complete_does_not_cross_project_retire` — same two-project setup; assert `auto_complete_ready_authorizations()` does NOT complete or retire PROJECT-B, and PROJECT-B stays active.

`platform_tests/hooks/test_project_completion_surface.py` (now in target_paths per F2): the `_seed()` helper's `implements_link` parameter (project-scoped) keeps the 4 pre-existing hook tests green under v4.

All pre-existing scanner/lifecycle/hook tests MUST continue to PASS.

## Spec-to-Test Mapping

| Specification / Behavior | Test | Expected |
|---|---|---|
| v4 F1 — cross-project implements link does NOT satisfy another project (scanner) | `test_cross_project_implements_link_does_not_satisfy_other_project` | PASS |
| v4 F1 — cross-project auto-complete does NOT retire another project (lifecycle) | `test_auto_complete_does_not_cross_project_retire` | PASS |
| v4 — incidental citation excluded (project-scoped D4) | `test_incidental_citation_thread_does_not_complete_wi`, `test_lifecycle_verified_work_items_implements_gate` | PASS |
| v4 — implements-linked thread completes WI (positive) | `test_implements_linked_thread_completes_wi` | PASS |
| v4 — Defect-1 regression: scan is NOT top-version-only | `test_top_verdict_has_no_work_item_line_but_report_does` | PASS |
| v4 fail-safe — no implements link → no completion / manual-review record | `test_fail_safe_no_implements_link_no_completion`, `test_auto_complete_fail_safe_emits_manual_review` | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook parity preserved | `platform_tests/hooks/test_project_completion_surface.py` (4 tests) + byte-identical hook source | PASS |
| no-regression on all existing scanner/lifecycle/hook tests | full targeted pytest across the 3 files | PASS |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic project-scoped discriminator | inspection: SQLite query carries project_id, no LLM | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal filed; INDEX updated | (this filing) | PASS |

Verification commands:

- `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/hooks/test_project_completion_surface.py -q --tb=short`
- `python -m ruff check scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/hooks/test_project_completion_surface.py`
- `python .claude/hooks/project-completion-surface.py` (smoke: silent under fail-safe direction)

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-5 (project-scoped design + expanded target_paths).
- [ ] Fresh implementation-start packet activated from the REVISED-5 GO.
- [ ] IP-1 + IP-2 landed: coverage is project-scoped `dict[project_id, set[wi]]`; global `verified_work_items()` removed from the scanner.
- [ ] IP-5 landed: 2 new cross-project regression tests PASS; the 6 updated v4 tests PASS; all pre-existing scanner/lifecycle/hook tests PASS.
- [ ] `ruff check` clean on all 5 changed source/test files.
- [ ] `python .claude/hooks/project-completion-surface.py` smoke does NOT auto-retire any project lacking an implements-linked VERIFIED thread.
- [ ] v4 row confirmed current (version 4); no re-insertion; packet unchanged.
- [ ] F2 resolved: `platform_tests/hooks/test_project_completion_surface.py` change is within the authorized target_paths.
- [ ] Codex returns VERIFIED on the post-impl report.
- [ ] Phase-2 `implements`-link backfill bridge filed as follow-on.

## Risk and Rollback

Risk: moderate — touches auto-retirement affecting every active project. Mitigation: the project-scoped fix is strictly narrower than the -011 global behavior (it can only REMOVE false-positive completions, never add them), and the fail-safe direction remains conservative (auto-completion paused, never spurious retirement).

- **Project-scoped coverage is a superset of correctness over -011**: any authorization that completed under -011's global set AND was project-correct still completes; only cross-project false positives are removed. Proven by the cross-project regression tests + the unchanged positive tests.
- **Auto-completion paused until Phase-2 backfill**: unchanged from -011; zero `implements` links at landing → no project auto-completes until backfilled.
- **Hook parity drift**: scanner + lifecycle duplicate logic; mitigated by the shared test fixtures exercising both call paths.
- **v4 row / packet drift**: none — v4 text unchanged; no re-insertion.

Rollback: `git restore` the 5 source/test files; the v4 spec row is append-only and already landed (no spec rollback needed — reverting the code restores the conservative paused behavior); the packet JSON is unchanged.

## Loyal Opposition Asks

1. Confirm the project-scoped `dict[project_id, set[work_item_id]]` design closes F1: an `implements` link for PROJECT-A cannot satisfy a PROJECT-B authorization even when the PROJECT-A thread cites a PROJECT-B gating WI. The pre-filing validation block + the two new cross-project regression tests are the evidence.
2. Confirm removing the global `verified_work_items()` from the scanner (replaced by `verified_work_items_by_project()`) is acceptable, and that the lifecycle's global `_all_verified_work_items()` is appropriately confined to the fail-safe v3-comparison diagnostic.
3. Confirm F2 is resolved by adding `platform_tests/hooks/test_project_completion_surface.py` to `target_paths` (vs splitting it into a separate thread). Codex's -012 recommended action favored inclusion given F1 requires test revision anyway.
4. Confirm that NOT re-inserting v4 and NOT regenerating the packet is correct (the v4 text is unchanged; Codex Required Revision #5 conditioned re-do on a text/packet change).
5. Confirm keeping `groundtruth.db` + the packet path in `target_paths` (authorized-but-unused) is acceptable, or direct their removal.
6. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
