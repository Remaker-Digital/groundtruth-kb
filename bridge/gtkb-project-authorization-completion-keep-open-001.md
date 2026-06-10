NEW

# Add keep-project-open opt-out to complete_project_authorization() so multi-slice projects are not auto-retired on sole-authorization completion (WI-3329)

bridge_kind: prime_proposal
Document: gtkb-project-authorization-completion-keep-open
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001; GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001; WI-3329
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3329
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/scripts/test_project_authorization.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

`ProjectLifecycleService.complete_project_authorization()` unconditionally retires the parent project (and collectively retires all of the project's associated work items and membership links) whenever the completed authorization is the project's sole active authorization. There is no opt-out parameter, so a caller cannot complete an authorization while deliberately keeping the project open as a program home for documented future slices.

Evidence — the auto-retire branch fires with no guard and no caller-supplied opt-out:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:586-605` — `complete_project_authorization(self, authorization_id, *, project_root, changed_by, change_reason)` has no `retire_project` / keep-open parameter in its signature.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:656-675` — Step 4 computes `other_active = [a for a in self.db.list_project_authorizations(project_id, status="active") if a.get("id") != norm_auth_id]` and then, `if not other_active:`, unconditionally calls `self.retire_project(...)` (line 662) and `self._retire_project_work_items(...)` (line 671), setting `project_retired = True`. There is no branch by which a caller can complete the authorization but skip retirement.
- `groundtruth-kb/src/groundtruth_kb/cli.py:1610-1650` — the `gt projects complete-authorization` command exposes `--changed-by`, `--change-reason`, and `--json`, but no flag to keep the project open; it calls `service.complete_project_authorization(...)` (line 1634) with no keep-open argument.

Observed symptom (recorded on WI-3329 itself, S353 2026-05-15): completing `PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE` auto-retired `PROJECT-GTKB-LO-OPPORTUNITY-RADAR` even though owner decision `DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15` explicitly chose to keep the project open as a program home for future slices; the project required a manual `gt projects update --status active` to restore. A second instance of the same eagerness pattern is recorded for `PROJECT-GTKB-PUSH-GATE` (S368): the design-packet authorization completed and the project auto-retired while Slices 1+ implementation gates lived on a not-yet-filed follow-on thread (`memory/project_push_gate_auto_retirement_premature_S368.md`).

This proposal adds an opt-in `retire_project: bool = True` parameter to `complete_project_authorization()` and a corresponding `--keep-project-open` flag to the `gt projects complete-authorization` CLI. The default value preserves byte-identical current behavior (sole-authorization completion still auto-retires), so every existing caller — including the parity `project-completion-surface` hooks and `auto_complete_ready_authorizations()` — is unchanged. The opt-out is a deterministic mechanism for the legitimate "complete the authorization but keep the project open" case the owner already exercises by manual restore today. It is a genuine small single-concern defect fix with no change to the default automatic-retirement contract.

## Specification Links

- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (v4) — governs the automatic completion-and-retirement trigger. Its Rule is the all-work-items-VERIFIED *trigger* for automatic retirement, and its Owner-AUQ boundary confirms owner-AUQ gates project START, not completion/retirement. This proposal does NOT change that trigger or that boundary for the default path: the default `retire_project=True` keeps automatic retirement exactly as specified. The new opt-out is an additive caller election outside the automatic path and does not alter the spec's stated behavior; this is the WI-3329 governing specification and is cited here per the source-spec linkage requirement.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — the project-authorization envelope governance. `complete_project_authorization()` is the authorization-completion surface; this proposal keeps the authorization-completion semantics intact and only adds an opt-out for the *project*-retirement side effect, so authorization completion and project retirement become independently expressible.
- GOV-RELIABILITY-FAST-LANE-001 — governs small single-concern defect fixes with no new behavior beyond removing the defect; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` remains canonical workflow state; this fix touches lifecycle/CLI source and tests only and does not alter the bridge protocol.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries this forward.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation across proposal, deliberation, and report (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions; the project/work-item retirement transition is the lifecycle event this opt-out makes electable (advisory).
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all target paths are under `E:\GT-KB`; the in-root clause is satisfied (advisory placement clause).

## Fast-Lane Eligibility

This thread claims eligibility under GOV-RELIABILITY-FAST-LANE-001 and the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (covers-by-membership: WI-3329 is an active member of PROJECT-GTKB-RELIABILITY-FIXES, confirmed live in the `work_items` table — `origin=defect`, `priority=P3`, `project_name=PROJECT-GTKB-RELIABILITY-FIXES`, `resolution_status=open`). The four eligibility criteria:

1. **Origin defect/regression** — met. WI-3329 has `origin=defect`; the title and description name the exact defect ("auto-retires the project when the sole authorization completes, with no keep-open option") and prescribe the exact minimal fix ("add a keep-project-open / retire flag to complete_project_authorization() (default preserving current behavior)"). The defect was observed twice in production lifecycle operations (S353, S368).
2. **No new API/CLI/behavior beyond removing the defect** — met with one bounded caveat. The fix adds one optional keyword parameter (`retire_project: bool = True`) to an existing method and one optional flag (`--keep-project-open`) to an existing CLI command. The DEFAULT path is byte-identical to current behavior: with `retire_project=True` (the default), sole-authorization completion still calls `retire_project()` and `_retire_project_work_items()` exactly as today. The only new behavior is reachable solely by explicitly opting out — which is the defect-removal itself (giving callers a way to express the keep-open case that the owner currently must reconstruct by hand). No new GOV/SPEC/PB/ADR/DCL artifact is created, and the governing spec's automatic-retirement Rule is untouched for every existing caller.
3. **No new requirement** — met. GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 already establishes the authorization-completion surface, and GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4 already separates project START (owner-gated) from completion/retirement (automatic on the VERIFIED trigger). The keep-open opt-out is a deterministic expression of an outcome the owner already produces manually; it does not introduce a new owner-stated capability requirement. The original design intent even contemplated optional retirement — `bridge/gtkb-project-verified-completion-auq-trigger-001.md:106` reads "Optionally call retire_project(project_id) if the authorization was the sole active one" — so this restores intended optionality rather than adding a new requirement.
4. **Small single-concern scope** — met. One concern: make the project-retirement side effect of authorization completion electable. Two source files (the lifecycle service and its CLI command) plus their two existing test modules; no cross-cutting change, no schema change, no migration.

Honest scope note: this fix is fast-lane eligible *because* the default preserves the spec-mandated automatic-retirement behavior and the opt-out is additive. If review judges that adding an electable keep-open path materially changes GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001's stated semantics (rather than sitting alongside them as a caller election), the correct disposition is NO-GO with a redirect to an owner-AUQ + formal-artifact-approval-packet path for a spec version bump. See Owner Decisions / Input for the explicit on/off-ramp.

## Prior Deliberations

This defect sits inside a dense project-completion/retirement prior-art cluster. WI-3329 is genuinely distinct from each:

- `bridge/gtkb-gov-project-retirement-spec-006.md` (VERIFIED) captured GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 **v2** ("Completion and Retirement Are Automatic — No Owner Confirmation"). That thread settled the *policy* that completion/retirement take no owner AUQ. It did NOT add a caller-level opt-out for the project-retirement side effect when an authorization completes. WI-3329 is the implementation-level gap: the service offers no parameter to honor a legitimate keep-open decision. The default in this proposal preserves that v2/v4 automatic policy exactly.
- `bridge/gtkb-project-verified-completion-auq-trigger-001.md` … `-008.md` introduced the `complete_project_authorization()` orchestration in `ProjectLifecycleService`. `-001.md:106` explicitly framed retirement as "Optionally call retire_project(...) if the authorization was the sole active one", but the landed code wired it unconditionally (lifecycle.py:661-670). WI-3329 restores the intended optionality as an explicit parameter. This is the most direct prior-art anchor for the fix shape.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-*` and `gtkb-project-completion-scanner-wi-auto-regex-fix-*` (v4 work, S372) corrected *which* threads count toward the all-WIs-VERIFIED trigger (the `implements`-linkage discriminator + the fail-safe that prevents spurious retirement when no implements-linked thread covers a project's gating WIs — lifecycle.py:759-785). Those threads tightened the *trigger condition*. WI-3329 is orthogonal: it is about whether a caller may complete an authorization and decline the project-retirement side effect at all, independent of how the trigger set is computed.
- `bridge/gtkb-bridge-verified-backlog-retirement-*` / `gtkb-legacy-gov-wi-cleanup-*` concern work-item-level retirement dispositions (keep-open vs retire for individual backlog items), not the `complete_project_authorization()` parameter. The keep-open language there is about WI dispositions, not the authorization-completion surface.
- The reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001, PROJECT-GTKB-RELIABILITY-FIXES, PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) is VERIFIED at `bridge/gtkb-reliability-fast-lane-006.md`; its owner-decision record is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. This proposal uses that standing authorization.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` is the structural exemplar for a reliability-fast-lane defect fix under the same standing authorization; this proposal mirrors its scope discipline.

A repository-wide search of `bridge/` for `WI-3329`, `retire_project`, `keep-open`, and `keep project open` confirms no existing thread proposes the `complete_project_authorization()` keep-open parameter; the matches are the unrelated WI-disposition and trigger-condition threads above.

## Owner Decisions / Input

No owner decision is required to land this fix as scoped, because the default (`retire_project=True`) preserves the spec-mandated automatic-retirement behavior exactly and the keep-open opt-out is additive (reachable only by an explicit caller election). It is a reliability-fast-lane defect fix covered by the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through active project membership; no formal-artifact-approval packet and no new owner AUQ are required for the default-preserving, additive change.

Conditional on-ramp (honest boundary): if Loyal Opposition concludes that introducing an electable keep-open path changes GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001's stated semantics rather than complementing them, then this work is NOT fast-lane and requires: (a) owner approval via AskUserQuestion to change the retirement semantics, and (b) a GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 version bump captured through the formal-artifact-approval-packet path per GOV-ARTIFACT-APPROVAL-001. In that case this proposal should be NO-GO'd and re-filed under that governance path; Prime Builder will route the owner AUQ before re-filing.

## Requirement Sufficiency

Existing requirements sufficient. GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 establishes the authorization-completion surface and GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4 separates owner-gated project start from automatic completion/retirement; the defect is the absence of a deterministic caller election for the keep-open case the owner already exercises by manual restore. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation for the default-preserving, additive change scoped here. (If the conditional on-ramp in Owner Decisions / Input is triggered, a new or revised requirement *would* be required before implementation — but that is the explicit NO-GO redirect, not this proposal's scope.)

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix to one lifecycle service method, one CLI command, and their two existing test modules. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3329) is this proposal's own implementing work item under the mandatory project-linkage metadata. Note: the *runtime* effect being made electable (project + work-item collective retirement) is a real lifecycle mutation, but this proposal changes only the code path's parameterization and adds tests; it performs no retirement and mutates no live project or work-item rows.

## Scope

### IP-1: Add a keep-open opt-out to `complete_project_authorization()` and `gt projects complete-authorization`

In `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`:

- Add a keyword-only parameter `retire_project: bool = True` to `complete_project_authorization()` (signature at lines 586-593). The default preserves current behavior exactly.
- In Step 4 (lines 656-675), gate the existing auto-retire block on the new parameter: retain the `other_active` computation (lines 656-658), and change the retirement condition from `if not other_active:` to `if retire_project and not other_active:`. When `retire_project=False`, the authorization is still completed (Step 3 is unchanged), but the project and its associated work items are NOT retired; `project_retired` stays `False` and `retired_work_items` stays `[]`. When `retire_project=True` (default) with no other active authorization, behavior is byte-identical to today.
- Update the method docstring (lines 594-605) to document the parameter and that the default preserves the GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 automatic-retirement contract; opting out is the caller's explicit election to keep the project open as a program home (e.g., honoring an owner keep-open decision such as DELIB-S353).

In `groundtruth-kb/src/groundtruth_kb/cli.py`:

- Add a `--keep-project-open` boolean flag (`is_flag=True`, default `False`) to the `complete-authorization` command (decorators at lines 1610-1615; handler at lines 1616-1650).
- Pass its negation through to the service: `service.complete_project_authorization(..., retire_project=not keep_project_open)` (call at line 1634). The default flag value (`False`) maps to `retire_project=True`, preserving current CLI behavior.
- Keep the human-readable echo (lines 1648-1650) correct: when `--keep-project-open` is supplied and the authorization was sole-active, the message must NOT claim "Project retired." (the existing `result["project_retired"]` value already drives this, so it remains correct without further change).

The `auto_complete_ready_authorizations()` caller (lifecycle.py:740-748) is intentionally NOT changed: it continues to call `complete_project_authorization()` without `retire_project`, so it keeps the default automatic-retirement behavior. The parity `project-completion-surface` hooks invoke that scanner path and are likewise unaffected.

### IP-2: Regression tests

In `groundtruth-kb/tests/test_project_artifacts.py` (service-level), alongside the existing `test_complete_sole_active_authorization_retires_project` (line 400) and `test_complete_with_other_active_authorization_keeps_project_active` (line 415):

- Add a test asserting the default is unchanged (sole active authorization, default call) — `result["project_retired"] is True` and `db.get_project("PROJECT-X")["status"] == "retired"` (mirrors the existing line-400 test; included so the default-preservation is locked by an assertion adjacent to the new opt-out test).
- Add a test asserting `retire_project=False` on a sole active authorization completes the authorization but keeps the project active: `result["authorization"]["status"] == "completed"`, `result["project_retired"] is False`, `result["retired_work_items"] == []`, and `db.get_project("PROJECT-X")["status"] == "active"`.

In `platform_tests/scripts/test_project_authorization.py` (CLI-level):

- Add a test invoking `gt projects complete-authorization <id> --keep-project-open` on a sole-active authorization and asserting the project remains active and the echo does not claim retirement; and a test that the default invocation (no flag) still retires, confirming the CLI default is preserved.

## Out Of Scope

- Changing GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001's automatic-retirement Rule, the all-WIs-VERIFIED trigger, the `implements`-linkage discriminator, or the v4 fail-safe — the default path is unchanged and no spec text is touched.
- Changing `auto_complete_ready_authorizations()` or the `project-completion-surface` parity hooks — they retain default automatic retirement by design.
- A "remaining non-terminal slices" heuristic guard — WI-3329 prescribes an explicit flag, which is deterministic and owner-decision-aligned; an inferred heuristic is not requested and is not implemented here.
- Reversing any past auto-retirement (e.g., re-activating PROJECT-GTKB-LO-OPPORTUNITY-RADAR or PROJECT-GTKB-PUSH-GATE) — those are separate runtime/owner actions, not this code fix.
- Any schema change, migration, or change to `retire_project()` / `_retire_project_work_items()` internals.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` — add `retire_project: bool = True` to `complete_project_authorization()`; gate the Step-4 retire block on it; update the docstring (IP-1).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — add the `--keep-project-open` flag to `complete-authorization` and thread it through as `retire_project=not keep_project_open` (IP-1).
- `groundtruth-kb/tests/test_project_artifacts.py` — service-level default-preservation and keep-open regression tests (IP-2).
- `platform_tests/scripts/test_project_authorization.py` — CLI-level `--keep-project-open` and default-retirement regression tests (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (default unchanged) | Service test: sole active authorization with the default call still sets `project_retired=True` and project status `retired` (default automatic-retirement contract preserved). |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 (keep-open election) | Service test: `retire_project=False` on a sole active authorization completes the authorization (`status=completed`) but keeps the project `active` with `project_retired=False` and `retired_work_items=[]`. |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (CLI surface) | CLI test: `gt projects complete-authorization <id> --keep-project-open` keeps the project active and the echo does not claim retirement; default invocation still retires. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | No bridge-protocol change; `bridge/INDEX.md` remains canonical. Verified by inspection. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility (or triggers the on-ramp). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py -q -k "complete and (retire or keep)"`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_project_authorization.py -q -k "keep or retire"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-authorization-completion-keep-open`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-authorization-completion-keep-open`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal (or triggers the Owner Decisions / Input on-ramp with NO-GO).
- [ ] `complete_project_authorization()` accepts a keyword-only `retire_project: bool = True`; with the default, a sole-active-authorization completion still retires the project and its work items (byte-identical to current behavior); covered by a test.
- [ ] With `retire_project=False`, a sole-active-authorization completion completes the authorization but keeps the project `active` (`project_retired=False`, `retired_work_items=[]`); covered by a test.
- [ ] `gt projects complete-authorization --keep-project-open` keeps the project active and the echo does not claim retirement; the default invocation still retires; covered by tests.
- [ ] `auto_complete_ready_authorizations()` and the parity `project-completion-surface` hooks are unchanged and retain default automatic retirement.
- [ ] No change to GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 text, the all-WIs-VERIFIED trigger, or the v4 fail-safe.
- [ ] `ruff check` and `ruff format --check` pass on the four changed files.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): the gating change accidentally alters the default path.** Mitigation: the condition becomes `if retire_project and not other_active:` with `retire_project` defaulting to `True`, so the default truth table is identical to today's `if not other_active:`. A dedicated default-preservation test asserts the sole-active default call still retires.

**Risk R2 (medium, governance): review judges the opt-out a semantics change to GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001.** Mitigation: the Owner Decisions / Input section provides an explicit on-ramp — NO-GO and re-file under an owner-AUQ + formal-artifact-approval-packet path for a spec version bump. The default-preserving, additive design is specifically chosen to keep the change within the fast lane; if review disagrees, the redirect is clean and no code lands prematurely.

**Risk R3 (low): a caller relies on the new opt-out and forgets the project must be retired later.** Mitigation: the opt-out is explicit (a non-default parameter / flag), so keeping a project open is always a deliberate caller action; the existing `gt projects update --status active|retired` surface remains available to retire later. Out of scope for this fix; noted for caller awareness.

Rollback: the change is contained to two source files plus two test modules. Reverting `lifecycle.py` (restore the `if not other_active:` condition and drop the parameter) and `cli.py` (drop the flag) restores prior behavior exactly; the added tests are independently removable. No data migration and no canonical-artifact mutation are involved.

## Loyal Opposition Asks

1. Confirm the central fast-lane judgment: that adding a default-`True` `retire_project` opt-out (default byte-identical to current behavior) complements GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001's automatic-retirement Rule rather than changing it — and therefore stays in the reliability fast lane. If you judge otherwise, NO-GO and direct the owner-AUQ + version-bump on-ramp.
2. Confirm the fix shape matches WI-3329's prescription (an explicit keep-open / retire flag, default preserving current behavior) and that the explicit-flag approach is preferred over an inferred "remaining slices" heuristic.
3. Confirm the scope boundary: leaving `auto_complete_ready_authorizations()` and the parity hooks on the default automatic-retirement path (so only explicit, owner-decision-driven callers opt out) is the correct boundary.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
