NEW

# Restore GT-KB Systems-and-Tools Companion Doc to Its In-Root Platform Home (WI-3487)

bridge_kind: implementation_proposal
Document: gtkb-restore-systems-and-tools-doc
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-ARTIFACT-ORIENTED-GOVERNANCE-001; WI-3487
Project Authorization: PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3487
target_paths: ["docs/gtkb-systems-and-tools.md", "platform_tests/scripts/test_system_interface_map.py"]
Recommended commit type: docs:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

The GT-KB platform document `docs/gtkb-systems-and-tools.md` — the human-readable companion to the platform map `config/agent-control/system-interface-map.toml` — is missing from its correct in-root platform home. It was added there on 2026-05-06 and then wrongly relocated into the Agent Red application docs cluster during the isolation-018 Slice 18.C "docs cluster move," and the references that depend on the in-root path were never repointed. The result is two currently-failing platform tests and a degraded operating-state probe.

Evidence:

- **Add commit** `350b2754` (2026-05-06 15:24 -0700, "chore: record GT-KB governance bridge updates") created `docs/gtkb-systems-and-tools.md` (52 lines), as part of the VERIFIED `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` work (`bridge/gtkb-systems-terminology-map-001-003.md`, "Files Changed" lists `docs/gtkb-systems-and-tools.md - human-readable companion").
- **Move commit** `687f4707` (2026-05-06 21:20 -0700, "docs: gtkb-isolation-018 Slice 18.C - docs cluster move (re-run, strict 8-edit scope, inventory to platform path)") renamed it 100% (content-identical) to `applications/Agent_Red/docs/gtkb-systems-and-tools.md`. `git show 687f4707 --summary -M` reports: `rename {docs => applications/Agent_Red/docs}/gtkb-systems-and-tools.md (100%)`.
- **Current absence at the in-root path**: `git ls-files` shows the only tracked copy is `applications/Agent_Red/docs/gtkb-systems-and-tools.md`. There is no `docs/gtkb-systems-and-tools.md`.
- **Broken references** still point at the in-root path. `config/agent-control/system-interface-map.toml:3` declares `human_companion = "docs/gtkb-systems-and-tools.md"`; `platform_tests/scripts/test_system_interface_map.py:73` reads `REPO_ROOT / "docs" / "gtkb-systems-and-tools.md"`; `groundtruth-kb/tests/test_operating_state.py:151,158` reference the same in-root path. None were updated by the Slice 18.C move.
- **Two platform tests fail now.** `E:/GT-KB/groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_system_interface_map.py -q` reports `2 failed, 6 passed`: `test_human_companion_declares_map_is_not_authority` fails with `FileNotFoundError` for the in-root `docs\gtkb-systems-and-tools.md`, and `test_compact_status_is_startup_safe` fails because `human_companion_exists` is `False` instead of `True`.
- **Live operating-state degradation.** `scripts/resolve_system_interface.py:156-163` (`compact_status`) computes `companion = project_root / system_map["human_companion"]` and reports `human_companion_exists = companion.exists()`. With the file absent from `docs/`, the `gt status --component system-interface-map` surface reports `human_companion_exists: False`.

This is both a placement defect (a GT-KB platform doc living under `applications/Agent_Red/` rather than its in-root home) and a broken-reference/failing-test defect. WI-3487 directs restoring the doc. The minimal, evidence-grounded fix is to restore the original content (recovered from `git show 350b2754:docs/gtkb-systems-and-tools.md`) to `docs/gtkb-systems-and-tools.md`, the exact path the platform map pointer, both tests, and the operating-state probe already expect — no reference edits required.

## Specification Links

- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable platform knowledge (the system/interface companion) must be preserved as a tracked in-root artifact; a platform doc displaced into the Agent Red application cluster and absent from its in-root home is non-compliance with artifact-oriented preservation. This is the WI-3487 governing specification.
- GOV-FILE-BRIDGE-AUTHORITY-001 — this proposal is filed through the live bridge authority at `bridge/INDEX.md`, which remains canonical workflow state and is unchanged by this fix.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — establishes the `applications/<name>/` placement convention and the platform/application boundary; a GT-KB platform doc belongs in the in-root `docs/` tree, not under `applications/Agent_Red/docs/`. Restoring the doc to `docs/` realigns placement with this decision. (Agent Red is a separate project per `.claude/rules/project-root-boundary.md`; its copy is a separate-project artifact and is left untouched.)
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the doc's lifecycle state (active, in-root authority companion) is restored.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries this forward.

## Authorization

This work is authorized by the dedicated project-scoped authorization `PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001` under project `PROJECT-GTKB-RELIABILITY-FIXES`, owner decision `DELIB-2548`. The authorization records `allowed_mutation_classes = ["source", "design_documentation", "test_addition"]` and forbids deploy, git_push_force, and spec_deletion. This proposal stays strictly within the allowed classes: restoring a markdown design document (`design_documentation`) and adding/strengthening a regression test (`test_addition`); it performs no deployment, no force-push, and no specification deletion. The authorization is additive to the bridge gate: this proposal still requires Loyal Opposition `GO`, and Prime Builder will create the implementation-start packet from that `GO` (`python scripts/implementation_authorization.py begin --bridge-id gtkb-restore-systems-and-tools-doc`) before any protected mutation.

## Prior Deliberations

- `bridge/gtkb-systems-terminology-map-001-003.md` (VERIFIED implementation report, 2026-05-06) is the thread that originally ADDED `docs/gtkb-systems-and-tools.md` and built the resolver, the operating-state probe, and the tests against that in-root path. It documents the doc as the in-root "human-readable companion." It does NOT cover restoration after the later Slice 18.C relocation, so it does not moot WI-3487.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` and `bridge/gtkb-startup-relay-cache-ttl-self-heal-001.md` are the structural exemplars for scoped reliability/defect fixes under `PROJECT-GTKB-RELIABILITY-FIXES`; this proposal mirrors their single-concern scope discipline.
- A repo-wide grep (`Grep bridge/ for "systems-and-tools"`) confirms no non-terminal or VERIFIED bridge thread already restores or repoints the relocated doc; the only matches are the original creation thread (`gtkb-systems-terminology-map-001-001/-003`) and an incidental mention in `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md`.

## Owner Decisions / Input

- 2026-06-01 (S381): via AskUserQuestion the owner approved authorizing WI-3487 for implementation, recorded as owner decision `DELIB-2548` and operationalized as the dedicated project-scoped authorization `PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001` (project `PROJECT-GTKB-RELIABILITY-FIXES`; allowed mutation classes `source`, `design_documentation`, `test_addition`; forbidden deploy / git_push_force / spec_deletion).
- No further owner decision is required before GO. The work is covered by the dedicated authorization and does not create or mutate any formal GOV/SPEC/PB/ADR/DCL artifact, so no formal-artifact-approval packet and no additional AskUserQuestion are required.

## Requirement Sufficiency

Existing requirements sufficient. GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (durable in-root artifact preservation), ADR-ISOLATION-APPLICATION-PLACEMENT-001 (platform/application placement boundary), and the platform map's own `human_companion` pointer already require this companion to exist at its in-root home; the relocation is non-compliance with those existing requirements. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped restoration of a single displaced platform document plus a regression test. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3487) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Restore the companion doc to its in-root platform home

Recover the original content from git history (`git show 350b2754:docs/gtkb-systems-and-tools.md`) and write it to `docs/gtkb-systems-and-tools.md`. The content is byte-identical to the copy currently tracked at `applications/Agent_Red/docs/gtkb-systems-and-tools.md` (the Slice 18.C rename was a 100% rename with zero content change), so either source yields the same 52-line document. Restoring to this exact path repairs the `config/agent-control/system-interface-map.toml` `human_companion` pointer, both failing platform tests, and the `compact_status` / `gt status --component system-interface-map` operating-state probe simultaneously, with no reference edits. The in-root `docs/` directory already exists, so this is a single file write.

The Agent Red copy (`applications/Agent_Red/docs/gtkb-systems-and-tools.md`) is a separate-project artifact and is left untouched; this proposal restores the platform doc without deleting the application copy.

### IP-2: Strengthen the in-root existence guard

The existing platform test `platform_tests/scripts/test_system_interface_map.py::test_human_companion_declares_map_is_not_authority` already serves as the regression guard that the companion exists at its in-root home and contains the not-an-authority language; it currently fails and will pass after IP-1. Add a focused, explicit assertion (within the same test file, no new file) that the resolved `human_companion` path from `config/agent-control/system-interface-map.toml` exists relative to the repo root, so a future displacement of the doc fails a named, self-documenting check rather than only surfacing as a `FileNotFoundError`. This keeps the guard within `target_paths` and adds no new public surface.

## Out Of Scope

- Deleting, moving, or editing the Agent Red copy at `applications/Agent_Red/docs/gtkb-systems-and-tools.md` — it is a separate-project artifact governed by the Agent Red project, not a GT-KB live artifact, and is out of scope for this platform restoration.
- Editing `config/agent-control/system-interface-map.toml`, `scripts/resolve_system_interface.py`, or `groundtruth-kb/tests/test_operating_state.py` — restoring the doc to the path they already expect makes reference edits unnecessary; changing those references would be the wrong fix (it would point platform infrastructure at an application path).
- Refreshing or correcting the doc's body content (e.g., the `memory/work_list.md` row, which post-dates the doc) — restoration preserves the VERIFIED original; any content refresh is a separate proposal.
- Any change to the system/interface map seed rows, resolver logic, or operating-state schema.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `docs/gtkb-systems-and-tools.md` — restored (created at the in-root platform path) from the recovered original content (IP-1).
- `platform_tests/scripts/test_system_interface_map.py` — add the explicit in-root existence assertion strengthening the displacement guard (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Test: `platform_tests/scripts/test_system_interface_map.py::test_human_companion_declares_map_is_not_authority` reads `REPO_ROOT / "docs" / "gtkb-systems-and-tools.md"` and asserts the not-an-authority language — passes only when the platform doc exists at its in-root home. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (operating-state surface) | Test: `test_compact_status_is_startup_safe` asserts `human_companion_exists is True`; the restored in-root doc makes `compact_status` (`scripts/resolve_system_interface.py:156-163`) report the companion present. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (displacement guard) | Test (IP-2): explicit assertion that the `human_companion` path declared in `config/agent-control/system-interface-map.toml` resolves to an existing file under the repo root, so a future displacement fails a named check. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `bridge/INDEX.md` remains canonical; this proposal changes no bridge automation or dispatch state. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run (Windows / PowerShell-valid, repo-venv interpreter):
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_system_interface_map.py -q --tb=short`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts/resolve_system_interface.py --status --json`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-restore-systems-and-tools-doc`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-restore-systems-and-tools-doc`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `docs/gtkb-systems-and-tools.md` exists at the in-root platform path with the recovered original content (companion to `config/agent-control/system-interface-map.toml`).
- [ ] `platform_tests/scripts/test_system_interface_map.py` passes in full (the previously-failing `test_human_companion_declares_map_is_not_authority` and `test_compact_status_is_startup_safe` now pass).
- [ ] `scripts/resolve_system_interface.py --status` / `gt status --component system-interface-map` reports `human_companion_exists: True`.
- [ ] The IP-2 displacement guard asserts the in-root `human_companion` path exists; covered by a test.
- [ ] No change to `config/agent-control/system-interface-map.toml`, the resolver logic, the map seed rows, or the Agent Red copy.
- [ ] `ruff check` and `ruff format --check` pass on the changed test file.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): the restored content is stale relative to the live system map.** The doc's body (recovered from the 2026-05-06 VERIFIED original) names `memory/work_list.md` as a backlog row, which has since been retired. Mitigation: restoration deliberately reinstates the VERIFIED original to fix the placement/reference defect with a minimal, auditable change; a content refresh is explicitly out of scope and tracked as a separate concern. The tests assert structural anchors (not-an-authority language, the bridge-queue caveat) that the original satisfies.

**Risk R2 (low): duplicate copies (in-root + Agent Red) cause confusion.** Mitigation: the in-root copy is the platform authority companion that the map pointer and platform tests target; the Agent Red copy is a separate-project artifact. The Out Of Scope section records the boundary; dispositioning the Agent Red copy (keep as Agent-Red-specific or remove as a leftover) is a separate Agent-Red-scoped decision, not a GT-KB platform concern.

**Risk R3 (very low): the restoration path is wrong.** Mitigation: the target path is fixed by `config/agent-control/system-interface-map.toml:3` and three test references; the verification re-runs the platform tests and the `--status` probe to confirm resolution.

Rollback: the change is contained to one restored doc plus one test edit. Removing `docs/gtkb-systems-and-tools.md` and reverting the test file restores the prior (defective) state. No data migration and no canonical-artifact mutation are involved.

## Loyal Opposition Asks

1. Confirm that restoring the doc to its in-root platform home `docs/gtkb-systems-and-tools.md` (rather than repointing `config/agent-control/system-interface-map.toml` and the tests at the `applications/Agent_Red/docs/` copy) is the correct fix direction given ADR-ISOLATION-APPLICATION-PLACEMENT-001 and the platform/application boundary.
2. Confirm that leaving the Agent Red copy untouched (restoring the platform doc without deleting the application copy) is the right scope boundary, versus folding an Agent-Red-copy disposition into this thread.
3. Confirm that reinstating the VERIFIED original content as-is (deferring any body-content refresh to a separate proposal) is the right minimal-change posture for this restoration.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
