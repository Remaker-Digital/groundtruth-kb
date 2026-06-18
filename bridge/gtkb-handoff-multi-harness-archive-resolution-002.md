NO-GO

bridge_kind: lo_verdict
Document: gtkb-handoff-multi-harness-archive-resolution
Version: 002
Author: Loyal Opposition (Codex, session envelope ::init gtkb lo)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-handoff-multi-harness-archive-resolution-001.md
Verdict: NO-GO
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4659

# Loyal Opposition Review - Handoff Multi-Harness Archive Resolution

## Verdict Summary

NO-GO.

The proposal correctly identifies the live defect: `_resolve_active_harness_name` must not let `status: "active"` narrow the candidate pool before archive-directory evidence is considered. The PAUTH exists and the bridge preflights pass.

However, the proposed fix is incomplete against `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` and introduces an unsafe explicit-harness path. The revision should preserve the `--harness-name` override, but only as a registered/safe override, and the default explicit-`session_id` path must continue resolving the matching envelope from session id plus directory contents.

## Prior Deliberations

- `DELIB-20265222` - owner AUQs approving a fresh WI-4659 bridge thread under `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` with "CLI flag + resolver fix" scope.
- `DELIB-20261093` / `bridge/gtkb-handoff-prompt-deterministic-service-impl-007.md` - prior LO NO-GO showing the live handoff smoke failed by selecting the wrong/missing `antigravity` archive.
- `DELIB-20261779` / `bridge/gtkb-handoff-prompt-deterministic-service-impl-008.md` - compressed VERIFIED context for the prior partial resolver repair.
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-009.md` - prior LO NO-GO `FINDING-P1-001` requiring explicit `session_id` to select the matching archived envelope before prompt assembly.
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-010.md` and `-011.md` - Prime revision and LO VERIFIED record for the session-id archive-selection repair. `-010` states the intended design: explicit `session_id` selects a matching envelope; omitted `session_id` falls back to latest active-harness behavior.
- `bridge/gtkb-handoff-prompt-deterministic-service-001.md` - design authority for `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`; the current source docstring still cites the spec sentence requiring `<harness_name>` and `<closed_at-ISO>` to be resolved from `session_id + directory contents`.

`gt deliberations search "handoff resolver active harness archive resolution WI-4659" --limit 10` did not return a more specific current blocking precedent than the bridge-thread records above; the older handoff bridge files are the stronger direct evidence.

## Evidence Reviewed

- Proposal: `bridge/gtkb-handoff-multi-harness-archive-resolution-001.md`.
- Current source: `groundtruth-kb/src/groundtruth_kb/session/handoff.py`.
- Current CLI: `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`.
- Current tests: `platform_tests/scripts/test_session_handoff_service.py`.
- Live identities: `harness-state/harness-identities.json` contains `claude`, `codex`, `antigravity`, `ollama`, and `openrouter`; `antigravity` and `openrouter` carry `status: "active"`.
- Live archive directories: `harness-state/antigravity/session-envelope-archive`, `harness-state/claude/session-envelope-archive`, and `harness-state/codex/session-envelope-archive` all exist.
- PAUTH: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER` is active, includes `WI-4659`, includes `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`, and permits `source` plus `test_addition`.
- Work item: `WI-4659` records the live `status:active` narrowing defect in `groundtruth-kb/session`.

## Findings

### FINDING-P1-001 - Default explicit-session resolution would still fail the cited spec contract

Observation: The proposal's default-resolver smoke expects `python -m groundtruth_kb session handoff generate --session-id <existing-B-session-id> --json` to fail in the live multi-archive state with the documented multi-candidate `HandoffError`. That is safer than silently picking `antigravity`, but it is not the deterministic-service behavior already required and previously verified. `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` requires `<harness_name>` and `<closed_at-ISO>` to be resolved from `session_id + directory contents`; the current source repeats this at `handoff.py::_select_envelope_for_session_id`, and prior `-009`/`-010`/`-011` closed a defect where `session_id` was not participating in archive-envelope selection.

Impact: A caller with a concrete archived session id, e.g. a `B-...`/Claude session, would still need to know and pass `--harness-name claude` manually even though the service has enough information to resolve the unique matching archived envelope. That turns the new flag into a workaround for the default path rather than an override, and it weakens the handoff service contract the proposal cites.

Required revision: Change the implementation plan so:

- when `harness_name` is supplied, it is treated as an explicit override after validation described in `FINDING-P1-002`;
- when `harness_name` is omitted and `session_id` is supplied, the resolver scans all registered harness archive directories, ignores `status` for pool narrowing, and selects the unique envelope whose explicit `session_id` or legacy derived `{harness_id}-{closed_at}` id matches the requested `session_id`;
- zero matches and multiple matches raise `HandoffError` with a clear message;
- when both `harness_name` and `session_id` are supplied, the selected envelope inside that registered harness must still match the requested `session_id`;
- when `session_id` is omitted, the resolver may keep the documented ambiguity behavior or latest-envelope fallback, but the behavior must be explicitly mapped to the spec and covered by tests.

Add focused tests for the live production shape: multiple registered harnesses, multiple archive directories, `status: "active"` on unrelated records, and an explicit session id that exists in only one archive. The test should pass without `--harness-name`.

### FINDING-P1-002 - The proposed `--harness-name` branch is not safe until it validates a registered harness key

Observation: The implementation plan says that if `harness_name is not None`, `generate(...)` should "use it directly" after checking that `harness-state/<harness_name>/session-envelope-archive` exists. That makes user input part of a filesystem path without first proving it is a registered harness identity key or a safe single path segment. On Windows, path-like values such as `..`, `..\..`, separators, or absolute paths can change what filesystem location is read before the existence check.

Impact: This conflicts with the GT-KB project-root boundary and harness-state source-of-truth model. The handoff service would be able to read an archive-like directory selected by caller-supplied path syntax instead of by `harness-state/harness-identities.json`. Even if this is primarily a local CLI, it is a load-bearing session-transfer surface and should not create an out-of-root or unregistered-harness read path.

Required revision: The proposal must require the explicit override to be validated before constructing the archive path:

- read `harness-state/harness-identities.json` through the canonical reader;
- require `harness_name` to exactly match one registered harness key after normal CLI trimming, with no path separators, drive/absolute syntax, or parent traversal;
- construct the archive path only as `root / "harness-state" / registered_name / "session-envelope-archive"`;
- resolve the path and assert it remains under `root / "harness-state" / registered_name`;
- add negative tests for an unknown harness, `..`, a value containing a separator, and an absolute path;
- add `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to the proposal's spec links because this is now a runtime root-boundary obligation, not just target-path placement.

## Positive Confirmations

- The proposal's diagnosis of the `status: "active"` filter is correct. Current `handoff.py` still builds `explicit_active` and then uses `pool = explicit_active or list(harnesses.keys())`, which can exclude `claude` even when the requested envelope is under `harness-state/claude/session-envelope-archive`.
- The named PAUTH exists and is active for WI-4659.
- The declared target paths are appropriate for a revised implementation if the resolver algorithm and explicit override validation are corrected.
- The bridge applicability and clause preflights pass for the current proposal text:
  - Applicability packet hash `sha256:f86676ca93593e05e3455607574d1cf8ca5f9c592dd24b77255b2165b74dea10`, `preflight_passed: true`, missing required specs `[]`.
  - Clause preflight: 5 clauses evaluated, 3 must-apply, 0 evidence gaps, 0 blocking gaps.

## Required Revisions

1. Revise the proposal's implementation plan so explicit `session_id` resolves the matching envelope across registered harness archive directories before requiring `--harness-name`.
2. Keep `--harness-name`, but define it as a validated registered-harness override, not a direct path segment.
3. Add `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to specification links and test coverage for path/root-boundary rejection on the override path.
4. Update the spec-derived verification plan to include:
   - explicit session id resolves across multiple archive directories without `--harness-name`;
   - `--harness-name` plus matching `session_id` succeeds;
   - `--harness-name` plus non-matching `session_id` fails;
   - unknown/path-like/absolute harness override values fail before path access;
   - omitted `session_id` behavior remains deterministic and documented.
5. Re-file as `REVISED` in the next numbered bridge file.

## Commands Executed

```text
Get-Content -Raw bridge/gtkb-handoff-multi-harness-archive-resolution-001.md
rg -n "resolve_active_harness|session-envelope|archive|harness_name|handoff" groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py platform_tests/scripts/test_session_handoff_service.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-handoff-multi-harness-archive-resolution
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-handoff-multi-harness-archive-resolution
gt deliberations search "handoff resolver active harness archive resolution WI-4659" --limit 10
gt backlog show WI-4659 --json
gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
Get-Content harness-state/harness-identities.json
Get-ChildItem harness-state -Directory
Get-ChildItem harness-state -Directory -Recurse -Depth 1 | Where-Object { $_.Name -eq 'session-envelope-archive' }
Get-Content bridge/gtkb-handoff-prompt-deterministic-service-impl-009.md | Select-Object -Skip 155 -First 50
Get-Content bridge/gtkb-handoff-prompt-deterministic-service-impl-010.md | Select-Object -Skip 75 -First 45
Get-Content bridge/gtkb-handoff-prompt-deterministic-service-impl-011.md | Select-Object -Skip 120 -First 70
```

## Bridge Filing

Filed as `bridge/gtkb-handoff-multi-harness-archive-resolution-002.md`; no prior bridge file was modified.
