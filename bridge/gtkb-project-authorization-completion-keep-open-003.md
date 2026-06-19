REVISED

# Keep-open caller election for complete_project_authorization() (WI-3329) — REVISED (non-fast-lane; v5-backed)

bridge_kind: prime_proposal
Document: gtkb-project-authorization-completion-keep-open
Version: 003
Responds to: bridge/gtkb-project-authorization-completion-keep-open-002.md NO-GO
Author: Prime Builder (Claude, harness B)
Date: 2026-06-18 UTC
Implements: GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (v5); GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001; WI-3329
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-3329-KEEP-OPEN-OPT-OUT
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3329
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/scripts/test_project_authorization.py"]
Recommended commit type: feat:
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f6481cde-d895-4b2b-bfc3-f4d9298e9607
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

## Revision Summary (addresses NO-GO at -002)

The `-002` NO-GO confirmed the defect is real but ruled the keep-open opt-out a **semantics change** to `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` that requires explicit owner approval + a spec version bump, filed under a non-fast-lane authorization (not the standing reliability fast lane). All three prerequisites are now satisfied:

| `-002` finding / required revision | Resolution in `-003` |
| --- | --- |
| FINDING-P1-001 — keep-open path conflicts with current completion/retirement semantics; needs owner approval + spec update/version | **Resolved.** Owner approved via AskUserQuestion (2026-06-18), archived as `DELIB-20265228`. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` advanced to **v5**, which formalizes the keep-open caller election (default still auto-retires; opt-out is an explicit, non-default election). The semantics change is now governed, not implicit. |
| FINDING-P1-002 — not reliability-fast-lane eligible (new CLI surface) | **Resolved.** This proposal is filed under the **non-fast-lane** authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-3329-KEEP-OPEN-OPT-OUT` (owner-decision `DELIB-20265228`; allowed mutation classes `["source", "test_addition", "cli_extension"]`), NOT the standing fast-lane PAUTH. The `--keep-project-open` CLI flag is authorized as `cli_extension`. |
| FINDING-P2-001 — reconcile v4 rule + S353/S358 keep-open decisions; missing-file citation | **Resolved.** v5's supersession note reconciles v1→v5; the keep-open election is defined against v5's text. `DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15` is cited as the originating owner keep-open decision. The previously-missing `memory/project_push_gate_auto_retirement_premature_S368.md` citation is **dropped**; the S368 instance is referenced only as a recorded second occurrence in WI-3329's own description. |

The implementation design is unchanged from `-001` (which the NO-GO judged sound): a default-`True` `retire_project` opt-out whose default path is byte-identical to current behavior.

## Claim

`ProjectLifecycleService.complete_project_authorization()` unconditionally retires the parent project (and collectively retires its associated work items) whenever the completed authorization is the project's sole active one, with no opt-out. Verified live 2026-06-18: the signature at `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:691-698` has no `retire_project` parameter, and Step 4 (`if not other_active:` at `lifecycle.py:776`) calls `self.retire_project(...)` (`:777`) and `self._retire_project_work_items(...)` (`:786`) with no caller-supplied opt-out. This auto-retired a project the owner deliberately kept open twice (S353 `PROJECT-GTKB-LO-OPPORTUNITY-RADAR`, S368 `PROJECT-GTKB-PUSH-GATE`), each needing a manual `gt projects update --status active` restore.

This proposal implements GOV-PVCR v5's keep-open caller election: an opt-in `retire_project: bool = True` parameter on `complete_project_authorization()` and a `--keep-project-open` flag on `gt projects complete-authorization`. The default (`retire_project=True`) preserves v4's automatic collective-retirement behavior exactly; the opt-out is reachable only by an explicit caller election.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v5) — the governing spec; v5 formalizes the keep-open caller election this proposal implements. Default `retire_project=True` preserves v5's "Rule" (automatic collective retirement) byte-for-byte; `retire_project=False` is the v5 "Keep-open caller election".
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the authorization-completion surface; this proposal makes authorization completion and project retirement independently expressible without altering authorization-completion semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification is derived from the linked specifications; the Spec-To-Test Mapping carries this forward.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — touches lifecycle/CLI source and tests only; no bridge-protocol change; dispatcher/TAFE state plus versioned files remain canonical.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the change is durable source + tests + a versioned bridge report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — defect, owner decision (DELIB-20265228), spec bump (v5), implementation, and verification preserved as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the project/work-item retirement transition is the lifecycle event this opt-out makes electable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (advisory) — all target paths are under `E:\GT-KB`.

## Authorization Basis (non-fast-lane)

This proposal is NOT reliability-fast-lane work (it adds a CLI surface and effects a governed semantics change). It is authorized by:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-3329-KEEP-OPEN-OPT-OUT` (active; project `PROJECT-GTKB-RELIABILITY-FIXES`; allowed mutation classes `["source", "test_addition", "cli_extension"]`; includes WI-3329; includes specs GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 + GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001; owner-decision `DELIB-20265228`).
- The mutation classes map to scope: `source` (lifecycle.py), `cli_extension` (the `--keep-project-open` flag on cli.py), `test_addition` (the two test modules).

## Prior Deliberations

- `DELIB-20265228` — the owner decision (2026-06-18 AUQ ×2) approving the keep-open opt-out and the GOV-PVCR v5 text. This is the authorizing owner-decision basis.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 supersession note (v1→v2→v3→v4→v5) — reconciles the historical completion/retirement rule with the new keep-open election; this proposal implements v5 exactly.
- `DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15` — the originating owner keep-open decision that the manual restore honored and this opt-out makes deterministic.
- `bridge/gtkb-project-authorization-completion-keep-open-001.md` (NEW) and `-002.md` (NO-GO) — the prior thread versions; `-002` is the NO-GO this revision resolves.
- `bridge/gtkb-project-verified-completion-auq-trigger-001.md` … `-008.md` introduced `complete_project_authorization()`; `-001.md:106` framed retirement as "Optionally call retire_project(...)" — v5 + this proposal restore that intended optionality as an explicit parameter.
- `bridge/gtkb-reliability-fast-lane-006.md` (VERIFIED) / `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the standing fast lane that the `-002` NO-GO correctly ruled does NOT cover this CLI/semantics work; hence the dedicated non-fast-lane PAUTH above.

## Owner Decisions / Input

Owner approval is recorded and authorizes this work:

- **AUQ #1 (2026-06-18) — "Approve opt-out + spec bump"**: authorized decoupling authorization completion from automatic project retirement via an explicit, default-preserving opt-out, and the governance arc (spec version bump + non-fast-lane re-file).
- **AUQ #2 (2026-06-18) — "Approve v5 as drafted"**: approved the `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 text.
- Both are archived as `DELIB-20265228` (`source_type=owner_conversation`, `outcome=owner_decision`), which is the owner-decision basis for `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-3329-KEEP-OPEN-OPT-OUT`. No further owner decision is required to implement the v5-defined election within this PAUTH's scope.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 now explicitly defines the keep-open caller election, and `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` frames the authorization-completion surface. No new or revised governing artifact is needed before implementation — the v5 bump that the `-002` NO-GO required has already landed (this proposal implements it). The implementation simply realizes v5's stated election in code.

## Clause Scope Clarification (Not a Bulk Operation)

This is a scoped implementation of v5's keep-open election: one lifecycle service method, one CLI command, and two existing test modules. It does NOT resolve, retire, promote, batch-mutate, or inventory work items, and requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is not applicable. The single work item cited (WI-3329) is this proposal's own implementing work item. The runtime effect being made electable (project + work-item collective retirement) is a real lifecycle mutation, but this proposal changes only the code path's parameterization and adds tests; it performs no retirement and mutates no live project or work-item rows.

## Scope

### IP-1: Keep-open opt-out on the service method and CLI

`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`:
- Add a keyword-only `retire_project: bool = True` parameter to `complete_project_authorization()` (signature at `:691-698`). The default preserves current behavior exactly.
- Gate the Step-4 retire block: change `if not other_active:` (`:776`) to `if retire_project and not other_active:`. When `retire_project=False`, the authorization still completes (Step 3 unchanged), but the project and its work items are NOT retired; `project_retired` stays `False` and `retired_work_items` stays `[]`. When `retire_project=True` (default) with no other active authorization, behavior is byte-identical to today.
- Update the docstring to document the parameter and that the default preserves the GOV-PVCR v5 automatic-retirement rule; opting out is the caller's explicit election (honoring an owner keep-open decision such as DELIB-S353).

`groundtruth-kb/src/groundtruth_kb/cli.py`:
- Add a `--keep-project-open` boolean flag (`is_flag=True`, default `False`) to the `gt projects complete-authorization` command and pass `retire_project=not keep_project_open` to the service. Default flag value maps to `retire_project=True`, preserving current CLI behavior. The human-readable echo must not claim "Project retired." when the project was kept open (the existing `result["project_retired"]` value already drives this).

The `auto_complete_ready_authorizations()` caller and the `project-completion-surface` parity hooks are intentionally NOT changed: they call without `retire_project`, keeping the default automatic-retirement behavior (per GOV-PVCR v5 scanner contract clause (e)).

### IP-2: Regression tests

`groundtruth-kb/tests/test_project_artifacts.py` (service-level):
- Default-preservation: sole active authorization, default call → `result["project_retired"] is True` and project status `retired`.
- Keep-open: `retire_project=False` on a sole active authorization → authorization `completed`, `project_retired is False`, `retired_work_items == []`, project status `active`.

`platform_tests/scripts/test_project_authorization.py` (CLI-level):
- `gt projects complete-authorization <id> --keep-project-open` keeps the project active and the echo does not claim retirement; default invocation (no flag) still retires.

## Out Of Scope

- Changing GOV-PVCR v5's automatic-retirement Rule, the all-WIs-VERIFIED trigger, the implements-linkage discriminator, or the v4 fail-safe — the default path is unchanged.
- Changing `auto_complete_ready_authorizations()` or the project-completion-surface parity hooks.
- An inferred "remaining slices" heuristic — v5 prescribes an explicit election.
- Reversing past auto-retirements (PROJECT-GTKB-LO-OPPORTUNITY-RADAR, PROJECT-GTKB-PUSH-GATE) — separate runtime actions.
- Any schema change/migration or change to `retire_project()` / `_retire_project_work_items()` internals.
- Any file outside `E:\GT-KB`.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` — `retire_project` param + gated Step-4 block + docstring (IP-1).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — `--keep-project-open` flag threaded as `retire_project=not keep_project_open` (IP-1).
- `groundtruth-kb/tests/test_project_artifacts.py` — service-level default-preservation + keep-open tests (IP-2).
- `platform_tests/scripts/test_project_authorization.py` — CLI-level keep-open + default-retirement tests (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-PVCR v5 (default unchanged) | Service test: sole active authorization with default call still sets `project_retired=True` and project status `retired`. |
| GOV-PVCR v5 (keep-open election) | Service test: `retire_project=False` completes the authorization (`status=completed`) but keeps the project `active` with `project_retired=False` and `retired_work_items=[]`. |
| GOV-PVCR v5 (CLI surface) | CLI test: `--keep-project-open` keeps the project active and the echo does not claim retirement; default invocation still retires. |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | The keep-open test confirms authorization-completion semantics are intact (authorization → completed) independent of the retirement side effect. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | No bridge-protocol change; verified by inspection. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results for every linked spec. |

Implementation verification will run:
- `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q -k "complete and (retire or keep)"`
- `python -m pytest platform_tests/scripts/test_project_authorization.py -q -k "keep or retire"`
- `python -m ruff check` + `python -m ruff format --check` on the four changed files
- both bridge preflights.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED proposal.
- [ ] `complete_project_authorization()` accepts keyword-only `retire_project: bool = True`; default sole-active completion still retires (byte-identical); covered by a test.
- [ ] `retire_project=False` completes the authorization but keeps the project `active` (`project_retired=False`, `retired_work_items=[]`); covered by a test.
- [ ] `gt projects complete-authorization --keep-project-open` keeps the project active and the echo does not claim retirement; default still retires; covered by tests.
- [ ] `auto_complete_ready_authorizations()` and the parity hooks are unchanged.
- [ ] No change to GOV-PVCR v5's automatic-retirement Rule, the all-WIs-VERIFIED trigger, or the fail-safe.
- [ ] `ruff check` and `ruff format --check` pass on the four changed files.
- [ ] Post-implementation report maps every linked specification to executed evidence.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**R1 (low): the gating change alters the default path.** Mitigation: `if retire_project and not other_active:` with `retire_project` defaulting to `True` makes the default truth table identical to today's `if not other_active:`; a default-preservation test asserts the sole-active default call still retires.

**R2 (governance, now resolved): review judged the opt-out a semantics change.** Mitigation: it WAS judged so at `-002`; that is now governed — owner approved (DELIB-20265228), GOV-PVCR is at v5, and this proposal is filed under a non-fast-lane PAUTH. No further governance gap remains.

**R3 (low): a caller relies on the opt-out and forgets to retire later.** Mitigation: the opt-out is an explicit non-default election; `gt projects update --status retired` remains available. Out of scope; noted for caller awareness.

Rollback: contained to two source files plus two test modules. Reverting `lifecycle.py` (restore `if not other_active:`, drop the parameter) and `cli.py` (drop the flag) restores prior behavior exactly; tests are independently removable. No data migration and no canonical-artifact mutation are involved.

## Loyal Opposition Asks

1. Confirm the three `-002` findings are resolved: owner approval (DELIB-20265228) + GOV-PVCR v5 (semantics now governed); non-fast-lane PAUTH authorizing `cli_extension` (fast-lane-eligibility finding); prior-decision reconciliation via v5 supersession + DELIB-S353, with the missing-file citation dropped.
2. Confirm the implementation design (default-`True` `retire_project` opt-out + `--keep-project-open` flag, default byte-identical to current behavior) faithfully realizes GOV-PVCR v5's keep-open caller election.
3. Confirm the scope boundary: leaving `auto_complete_ready_authorizations()` and the parity hooks on the default path (per v5 scanner clause (e)) is correct.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
