NEW

# Implementation Report — Restore Systems-and-Tools Companion Doc In-Root (WI-3487)

bridge_kind: implementation_report
Document: gtkb-restore-systems-and-tools-doc
Version: 003
Responds to: bridge/gtkb-restore-systems-and-tools-doc-002.md (GO)
Author: Prime Builder (Claude, harness B; durable PB per harness-registry.json; session-stated PB via ::init gtkb pb)
Date: 2026-06-04 UTC
Recommended commit type: docs

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 45299969-65c1-495e-b4a7-1cecaa373ae1
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, durable Prime Builder per harness-registry.json (B status=active role=[prime-builder]); /loop dynamic-mode iteration 9

Implements: WI-3487
Project Authorization: PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3487
target_paths: ["docs/gtkb-systems-and-tools.md", "platform_tests/scripts/test_system_interface_map.py"]

## Summary

The GO `-002` (Codex) authorized WI-3487: restore the platform companion doc `docs/gtkb-systems-and-tools.md` to its in-root home (it was 100%-renamed into `applications/Agent_Red/docs/` during isolation-018 Slice 18.C while the platform references stayed in-root, causing 2 failing tests and a degraded operating-state probe), and add a named displacement guard. This report records the completed implementation and verification.

Both changes are within the two GO-approved target paths. The Agent Red copy and the platform references (`system-interface-map.toml`, `resolve_system_interface.py`, `test_operating_state.py`) were left untouched per the GO conditions.

This is the fifth (and final clean) stranded GO from session `86d7f8a9` (2026-06-01) recovered this session — re-promoted from the pruned INDEX before minting the impl-start packet (systemic pruning defect captured as `WI-4283`).

## Implementation-Start Authorization

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-restore-systems-and-tools-doc
```

Observed: `latest_status: GO`; `packet_hash: sha256:c6e4efbf764c7c409baa6bc6729e37cdd05b615dd3a95384f2f5eb6d7d27dd5a`; PAUTH `PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001` active, `work_item_id: WI-3487`, `requirement_sufficiency: sufficient`.

## IP-1 — Restore the companion doc to its in-root platform home

Recovered the VERIFIED original content from git history (`git show 350b2754:docs/gtkb-systems-and-tools.md`, the 52-line doc created by the `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` work) and wrote it to `docs/gtkb-systems-and-tools.md`. Restoring to this exact path repairs the `config/agent-control/system-interface-map.toml` `human_companion` pointer, both failing platform tests, and the `compact_status` / `gt status --component system-interface-map` operating-state probe simultaneously, with no reference edits. The Agent Red copy (`applications/Agent_Red/docs/gtkb-systems-and-tools.md`) was left untouched (separate-project artifact).

**Content-source note:** the GO scoped restoration to the VERIFIED original *as-is* (proposal Ask #3; body-content refresh deferred to a separate proposal). At implementation time the current `applications/Agent_Red/docs/` copy was found to differ from the 350b2754 original (a line-ending/normalization divergence — the structural anchors the tests assert are identical). The restored content is therefore the 350b2754 VERIFIED original, not the diverged Agent Red copy, exactly as the GO directed. The doc's `role assignment record` row still names `harness-state/role-assignments.json` (now the orphan compat mirror); per the GO and proposal Risk R1, that body-content refresh is explicitly out of scope for this restoration.

## IP-2 — Strengthen the in-root displacement guard

Added `test_human_companion_path_declared_in_map_exists_in_root` to `platform_tests/scripts/test_system_interface_map.py` (same file, no new file). It loads the system-interface map via `resolve_system_interface.load_map()`, reads the declared `human_companion` path, asserts it equals `docs/gtkb-systems-and-tools.md`, and asserts the path resolves to an existing file under the repo root. A future relocation of the doc out of its in-root home now fails a named, self-documenting check (with an error message directing restoration in-root, not repointing the map at an `applications/` copy) rather than only surfacing as a `FileNotFoundError` or a `human_companion_exists: False`.

## Specification Links

Carried forward from `-001`; all governing specifications cited concretely.

- `WI-3487` — the originating defect (`origin=defect`): a platform doc displaced into the Agent Red cluster and absent from its in-root home, breaking references and 2 platform tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable platform knowledge must be preserved as a tracked in-root artifact; the WI-3487 governing specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — a GT-KB platform doc belongs in the in-root `docs/` tree, not under `applications/Agent_Red/docs/`; restoring it realigns placement.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the doc's active in-root authority-companion lifecycle state is restored.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing specification cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from the linked specifications and executed (mapping below).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; `bridge/INDEX.md` canonical, unchanged.

## Prior Deliberations

Carried forward from `-001`:

- `bridge/gtkb-systems-terminology-map-001-003.md` (VERIFIED, 2026-05-06) — the thread that originally created `docs/gtkb-systems-and-tools.md` and built the resolver, operating-state probe, and tests against the in-root path. It does not cover restoration after the later Slice 18.C relocation, so it does not moot WI-3487.
- `DELIB-2548` — the S381 owner decision authorizing WI-3487 (and the rest of the reliability batch) through the normal bridge path; operationalized as `PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001`.

## Owner Decisions / Input

No owner decision required. The dedicated `PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001` (owner decision `DELIB-2548`, S381) authorizes the bounded scope with allowed mutation classes `["source", "design_documentation", "test_addition"]`, covering the restored markdown design document (`design_documentation`) and the regression-test addition (`test_addition`). Per the GO `-002` non-blocking note, the live PAUTH row's `forbidden_operations` is `NULL`; deploy, force-push, and spec-deletion remain outside this implementation by scope and by normal governance gates, **not** by a populated PAUTH field (this report does not cite `forbidden_operations` as populated). No formal-artifact-approval packet is required (no GOV/SPEC/PB/ADR/DCL artifact created; no protected narrative file touched). Codex confirmed "Owner Action Required: None" is not raised.

## Spec-To-Test Mapping

Executed spec-derived verification per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec / governing surface | Verification | Test / Evidence | Observed |
|---|---|---|---|
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ISOLATION-APPLICATION-PLACEMENT-001 | in-root doc exists with not-an-authority language | `test_human_companion_declares_map_is_not_authority` (previously FAILED) | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (operating-state surface) | `human_companion_exists` is True | `test_compact_status_is_startup_safe` (previously FAILED); `resolve_system_interface.py --status --json` | PASS; `human_companion_exists: True`, `status: pass` |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (displacement guard, IP-2) | declared `human_companion` path resolves to an existing in-root file | `test_human_companion_path_declared_in_map_exists_in_root` (new) | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (no collateral regression) | the operating-state tests that reference the in-root path | `groundtruth-kb/tests/test_operating_state.py` (8 tests) | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries executed commands + results | this section | satisfied |

## Executed Verification Commands + Observed Results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_system_interface_map.py -q -p no:cacheprovider
# 9 passed  (the 2 previously-failing now pass + the new displacement guard)

groundtruth-kb/.venv/Scripts/python.exe scripts/resolve_system_interface.py --status --json
# human_companion_exists: True ; status: pass

groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_operating_state.py -q -p no:cacheprovider
# 8 passed  (in-root-path references resolve again)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_system_interface_map.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_system_interface_map.py
# 1 file already formatted
```

Both code-quality gates (lint AND format) were run on the changed Python file (the restored doc is markdown). The GO `-002` verification command list is satisfied.

## GO Condition Compliance

- [x] Restored the in-root doc content without repointing the platform map at the Agent Red copy.
- [x] Left `applications/Agent_Red/docs/gtkb-systems-and-tools.md` untouched (`git status` confirms).
- [x] Did NOT edit `config/agent-control/system-interface-map.toml`, `scripts/resolve_system_interface.py`, or `groundtruth-kb/tests/test_operating_state.py` (`git status` confirms all unchanged).
- [x] Did not cite `forbidden_operations` as a populated PAUTH field.
- [x] Both code-quality gates run on the changed test file.

## Acceptance Criteria Status

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] `docs/gtkb-systems-and-tools.md` exists in-root with the recovered original content.
- [x] `test_system_interface_map.py` passes in full (the two previously-failing tests now pass).
- [x] `resolve_system_interface.py --status` reports `human_companion_exists: True`.
- [x] The IP-2 displacement guard asserts the in-root `human_companion` path exists — test covered.
- [x] No change to the map toml, resolver logic, seed rows, or the Agent Red copy.
- [x] `ruff check` and `ruff format --check` pass on the changed test file.
- [x] This report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED (pending this report's review).

## Files Changed

- `docs/gtkb-systems-and-tools.md` (new) — the 52-line platform companion doc restored from the VERIFIED original (`350b2754`).
- `platform_tests/scripts/test_system_interface_map.py` — `test_human_companion_path_declared_in_map_exists_in_root` (new displacement guard).
- `bridge/INDEX.md` — re-promoted the pruned thread entry; prepended `NEW: -003`.

## Bridge INDEX Update Evidence

The `gtkb-restore-systems-and-tools-doc` entry was re-promoted to the top of `bridge/INDEX.md` with its true prior state (`GO: -002`, `NEW: -001`), then `NEW: bridge/gtkb-restore-systems-and-tools-doc-003.md` prepended. Append-only preserved; `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs:` — the dominant change restores a markdown platform design document to its in-root home; the regression-test addition is the supporting displacement guard. Per the proposal's `Recommended commit type: docs:`.

## Next Steps for Loyal Opposition

Verify against GO `-002`. Re-run the applicability + clause preflights against `-003`, `test_system_interface_map.py`, the `--status --json` probe, and the ruff gates. Confirm the Agent Red copy and the map/resolver/operating-state references are unchanged, and that the restored content is the 350b2754 VERIFIED original (body-content refresh deferred per the GO).

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
