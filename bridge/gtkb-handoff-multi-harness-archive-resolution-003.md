REVISED

# gtkb-handoff-multi-harness-archive-resolution — Cross-archive session_id resolution by default; validated --harness-name override

bridge_kind: implementation_proposal
Document: gtkb-handoff-multi-harness-archive-resolution
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-18 UTC
Responds-to: bridge/gtkb-handoff-multi-harness-archive-resolution-002.md (LO NO-GO)

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: 94112412-fe8d-406f-9f4b-d03dc87f2ee1
author_model: claude-opus-4-7
author_model_version: opus-4-7
author_model_configuration: claude-code-cli; durable role prime-builder; session-stated role prime-builder (per owner AUQ init keyword); interactive (no GTKB_BRIDGE_POLLER_RUN_ID)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4659

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/scripts/test_session_handoff_service.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Revision of `-001` per Codex Loyal Opposition NO-GO at `-002`. Both NO-GO findings (P1-001 default-resolver scope; P1-002 unvalidated override path) are addressed substantively.

The corrected design:

1. **Default path with explicit `session_id` (the canonical caller shape):** the resolver retires the `status: "active"` pool-narrowing AND cross-scans every registered harness archive directory for the matching `session_id`. A unique match in any archive succeeds — no `--harness-name` required. Zero or multiple matches raise `HandoffError` with a clear message. This is the deterministic-service behavior `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` already requires (§ Inputs: `<harness_name>` and `<closed_at-ISO>` resolved from `session_id + directory contents`).
2. **`--harness-name` becomes a validated registered-harness override**, not a user-controlled filesystem path segment. The supplied name must (a) exactly match a registered key in `harness-state/harness-identities.json`, (b) contain no path separators, parent-traversal tokens (`.`, `..`), or drive/absolute syntax, and (c) resolve to a path that stays under `harness-state/<registered_name>/`. Unknown/path-like/absolute values fail with `HandoffError` before any path access. When both `--harness-name` and `session_id` are supplied, the resolved envelope inside the registered harness must still match the requested `session_id`.
3. **Default path with omitted `session_id`** preserves the documented behavior: directory-presence is the sole disambiguator (the `status` filter is retired); the multi-candidate `HandoffError` becomes reachable instead of silently picking `antigravity`. This case is explicitly mapped to the spec and covered by a regression test.

The `status` field semantics in `harness-identities.json` remain untouched. A future deliberation can decide whether `status` should be retired, promoted, or formally documented; this scope only removes the resolver's load-bearing dependence on it.

## Specification Links

- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` — governing requirement. Per § Inputs, `<harness_name>` and `<closed_at-ISO>` are resolved "from the `session_id` + directory contents at service invocation time." The corrected default path satisfies this contract by scanning all archive directories for the matching `session_id` rather than first narrowing to a single harness. The current source repeats this contract at `handoff.py::_select_envelope_for_session_id`; this revision extends it across archive directories.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary obligation. The `--harness-name` override path now becomes a runtime root-boundary surface (per Codex P1-002): user-supplied path-syntax values must be rejected before any filesystem access, and the resolved archive path must remain under `harness-state/<registered_name>/`. Path-segment safety and registered-name validation are the in-source enforcement. Added per Codex required-revisions item 3.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this REVISED is filed as the next versioned bridge file under that authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires every implementation proposal to cite every relevant governing specification. This section is the citation surface for that mandate; preflight verification packet is appended in the Applicability Preflight section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires `Project Authorization`, `Project`, and `Work Item` headers in implementation proposals. Headers are present at lines 16-18 above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the implementation report to carry forward this proposal's linked specs and provide spec-to-test mapping with executed evidence before `VERIFIED`. Test plan derived from each linked spec is documented in the Spec-Derived Verification Plan section below.
- `GOV-STANDING-BACKLOG-001` — WI-4659 is admitted to PROJECT-GTKB-RELIABILITY-FIXES per `gt projects add-item` evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation authorization is bounded by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER (allowed mutation classes: source, test_addition; included WI: WI-4659; included spec: SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001).

## Prior Deliberations

- `DELIB-20265222` — owner AUQs approving a fresh WI-4659 bridge thread under SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001 with "CLI flag + resolver fix" scope. The fresh-thread + CLI-flag direction is preserved in this REVISED; the CLI flag is now a validated override, not a required disambiguator.
- `bridge/gtkb-handoff-multi-harness-archive-resolution-002.md` — Codex Loyal Opposition NO-GO this revision addresses. FINDING-P1-001 (default explicit-session resolution must succeed without `--harness-name` by cross-scanning archives) and FINDING-P1-002 (override must be validated registered-harness key with path-segment safety check) are both fully addressed below.
- `DELIB-20261093` — Loyal Opposition NO-GO on `gtkb-handoff-prompt-deterministic-service-impl-006` (2026-06-05). Surfaced the exact symptom this proposal addresses: the live CLI smoke failed because the resolver "selects missing `harness-state\antigravity\session-envelope-archive`."
- `DELIB-20261779` — compressed VERIFIED record for the 11-version `gtkb-handoff-prompt-deterministic-service-impl` thread. The `-008` REVISED report kept the `status: "active"` filter as a "forward compatibility" surface on the broken assumption that no record carries `status` in production. This proposal retires that filter.
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-009.md` / `-010.md` / `-011.md` — prior LO NO-GO/REVISED/VERIFIED cycle closed a defect where `session_id` was not participating in archive-envelope selection. The corrected design preserves their `-010`/`-011` invariant (explicit `session_id` selects a matching envelope) and extends it across multiple archive directories.
- `DELIB-20261091` — original GO verdict on the handoff impl thread; establishes the service's design authority.
- `DELIB-20264109` — VERIFIED for handoff-prompt terminology clarification (DELIB-20260883). No conflict with this scope.

## Owner Decisions / Input

Owner approval for this scope was captured via two AskUserQuestion calls in the interactive Prime Builder session 94112412-fe8d-406f-9f4b-d03dc87f2ee1 on 2026-06-18 UTC. Full text and rationale archived at `DELIB-20265222` (formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-06-18-DELIB-20265222.json`).

| AUQ | Question | Owner answer |
|---|---|---|
| AUQ-2026-06-18-HANDOFF-RESOLVER-SCOPE-AND-HOME (q1) | Which fix scope should the bridge proposal cover? | Option 1 — CLI flag + resolver fix |
| AUQ-2026-06-18-HANDOFF-RESOLVER-SCOPE-AND-HOME (q2) | Should the proposal file under the existing handoff spec or as a fresh thread? | Option 1 — Fresh bridge thread under SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001 |

The owner answer "CLI flag + resolver fix" is interpreted in this REVISED as Codex's preferred shape: the resolver fix is the default behavior that satisfies the spec contract; the CLI flag is an optional validated override. No new owner decision is required for the revision direction — both NO-GO findings are textual/architectural refinements within the AUQ-approved scope.

Implementation begins only after Codex GO on this REVISED + implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-handoff-multi-harness-archive-resolution`).

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` already specifies the deterministic resolution contract (§ Inputs: `<harness_name>` and `<closed_at-ISO>` resolved from `session_id + directory contents`); the corrected default path implements that contract literally. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` already establishes the root-boundary obligation; the validated `--harness-name` override implements that obligation at the override surface. No new requirement or spec amendment is needed.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
|---|---|---|
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (cross-archive default-path resolution; addresses Codex P1-001 required revision) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_default_path_resolves_session_id_across_archives -q` | Fixture: identities = `{"claude":{"id":"B"},"antigravity":{"id":"C","status":"active"},"openrouter":{"id":"F","status":"active"},"codex":{"id":"A"}}`. Archive only on `harness-state/claude/`. Call `generate(session_id="B-2026-...", project_root=..., db=...)` with NO `harness_name`. Expected: resolves to claude's envelope; no `HandoffError`. |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (cross-archive ambiguity) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_default_path_raises_when_session_id_matches_multiple_archives -q` | Fixture: same session_id appears in TWO archive directories. Expected: `HandoffError` with "ambiguous" message. |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (cross-archive no-match) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_default_path_raises_when_session_id_matches_no_archive -q` | Fixture: requested `session_id` does not match any archived envelope. Expected: `HandoffError` with "no archived envelope matches" message listing scanned harness names. |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (default with omitted session_id) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_default_path_resolves_active_harness_when_session_id_omitted -q` | Fixture: identities with one record carrying `status:"active"`, archives only on a non-status record. Expected: directory-presence selects the non-status record; resolver returns the latest envelope. The `status` filter is retired. |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` + `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (validated override happy-path; addresses Codex P1-002) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_explicit_harness_name_override_resolves_within_registered_archive -q` | Fixture: identities + archives in multiple locations. Call `generate(harness_name="claude", session_id="B-...", ...)`. Expected: resolves to claude's envelope; the resolved path remains under `harness-state/claude/`. |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (override + non-matching session_id) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_explicit_harness_name_override_with_non_matching_session_id_fails -q` | Fixture: `harness_name="claude"`, `session_id="C-not-in-claude-archive"`. Expected: `HandoffError`; the resolver does NOT silently fall through to scan other archives when an explicit override is supplied. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (override rejection — unknown name) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_explicit_harness_name_override_rejects_unknown_name -q` | `harness_name="unregistered"`. Expected: `HandoffError` with explicit "not a registered harness" message; no filesystem access to `harness-state/unregistered/...`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (override rejection — parent traversal) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_explicit_harness_name_override_rejects_parent_traversal -q` | `harness_name=".."` and `harness_name="../claude"`. Expected: `HandoffError` with "invalid harness name" message; rejected before filesystem access. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (override rejection — separator) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_explicit_harness_name_override_rejects_path_separators -q` | `harness_name="claude/extra"` and `harness_name="claude\\extra"`. Expected: `HandoffError`; rejected before filesystem access. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (override rejection — absolute path) | `python -m pytest platform_tests/scripts/test_session_handoff_service.py::test_explicit_harness_name_override_rejects_absolute_path -q` | `harness_name="C:/claude"` and `harness_name="/claude"`. Expected: `HandoffError`; rejected before filesystem access. |
| Live CLI smoke (matches the P1-001 acceptance criterion) | `python -m groundtruth_kb session handoff generate --session-id <existing-B-session-id> --json` against the live registry (claude + codex + antigravity all have archive dirs; antigravity/openrouter have status:active) — NO `--harness-name` | Exits 0; resolves envelope from `harness-state/claude/session-envelope-archive/`; emits a deterministic prompt; CLI does NOT error with `harness-state/antigravity/...` in the failure message. |
| Live CLI smoke (validated override) | `python -m groundtruth_kb session handoff generate --harness-name claude --session-id <existing-B-session-id> --json` | Exits 0; same resolution outcome as the default path; demonstrates the override is a stable secondary path. |
| Live CLI smoke (override rejection) | `python -m groundtruth_kb session handoff generate --harness-name ".." --session-id ... --json` | Exits non-zero with the "invalid harness name" error; no filesystem access outside the project root. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-handoff-multi-harness-archive-resolution` | `preflight_passed: true`, `missing_required_specs: []`. Packet hash appended to verdict by Loyal Opposition. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight (above) | Same. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header inspection on this file | PAUTH/Project/Work Item headers present at lines 16-18 above. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This Spec-Derived Verification Plan section + implementation report carry-forward | Spec-to-test mapping carried forward in implementation report. |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-4659` after VERIFIED | WI-4659 resolution evidence cites this thread. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES` | PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER active; includes WI-4659; mutation classes `source` + `test_addition` only. |
| Pre-file code-quality gates | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>` AND `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed.py>` | Both pass cleanly per file-bridge-protocol § "Pre-File Code-Quality Gates." |

## Implementation Plan

1. **`groundtruth-kb/src/groundtruth_kb/session/handoff.py` — resolver redesign:**

   a. **Add `harness_name: str | None = None` parameter to `generate(...)`.** Dispatch by case:
      - if `harness_name is not None`: validate via `_validate_harness_name_override(root, harness_name)` (defined below), then use the validated registered name; archive path is `root / "harness-state" / validated_name / "session-envelope-archive"`. If `session_id` is supplied, the envelope inside that archive must match.
      - elif `session_id is not None`: cross-scan all registered harness archive directories via the new `_select_envelope_across_archives(root, session_id)` (defined below).
      - else: fall back to `_resolve_active_harness_name(root)` for backward-compatible latest-envelope path (with status filter retired).

   b. **Add `_validate_harness_name_override(project_root, harness_name) -> str`.** Steps in order:
      - strip leading/trailing whitespace from `harness_name`;
      - reject empty string with `HandoffError("invalid harness name: empty")`;
      - reject any of the strings `.`, `..`, or any value containing `/`, `\`, or `:` with `HandoffError("invalid harness name: contains path syntax")`;
      - reject `Path(harness_name).is_absolute()` with `HandoffError("invalid harness name: absolute path")`;
      - read identities via the canonical `read_identity(project_root)` reader;
      - require `harness_name` to exactly match a key in `data["harnesses"]` (or `data["identities"]`) with `HandoffError("not a registered harness: {harness_name}")` otherwise;
      - assert the constructed archive path is under `root / "harness-state" / validated_name` via `Path.resolve().relative_to(...)` (raises `HandoffError` on escape, defense in depth);
      - return the validated registered name string.

   c. **Add `_select_envelope_across_archives(project_root, session_id) -> tuple[str, Path]`.** Steps in order:
      - read identities via `read_identity(project_root)`;
      - for each registered harness name whose `harness-state/<name>/session-envelope-archive/` directory exists, scan its envelope files and collect `(harness_name, envelope_path)` pairs where the envelope's explicit `session_id` (or derived `{harness_id}-{closed_at}` form per the existing `_derive_session_id` helper) matches the requested `session_id`;
      - exactly one match → return it;
      - zero matches → raise `HandoffError("No archived envelope matches session_id={!r} in any scanned harness archive. Scanned: {names}")`;
      - multiple matches → raise `HandoffError("Ambiguous archive selection: session_id={!r} matches envelopes in multiple harness archives: {harness_names}")`.

   d. **In `_resolve_active_harness_name`**: remove lines 214-217 (the `explicit_active = [...]; pool = explicit_active or ...` block). Replace with `pool = list(harnesses.keys())` so directory-presence is the sole disambiguator. Update the docstring to describe the corrected behavior and note that the function is now only invoked when both `harness_name` and `session_id` are omitted.

2. **`groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` — CLI flag:**

   - Add `@click.option("--harness-name", default=None, help="Optional explicit harness override. When omitted, the resolver disambiguates by directory presence and (when --session-id is given) by cross-scanning all registered harness archives for the matching envelope. The override is validated against harness-state/harness-identities.json.")` to `generate_cmd`.
   - Add `harness_name: str | None` parameter to `generate_cmd(...)` signature.
   - Pass `harness_name=harness_name` through to `generate(...)`.

3. **`platform_tests/scripts/test_session_handoff_service.py` — 10 new regression tests** matching the Spec-Derived Verification Plan table:
   - `test_default_path_resolves_session_id_across_archives`
   - `test_default_path_raises_when_session_id_matches_multiple_archives`
   - `test_default_path_raises_when_session_id_matches_no_archive`
   - `test_default_path_resolves_active_harness_when_session_id_omitted`
   - `test_explicit_harness_name_override_resolves_within_registered_archive`
   - `test_explicit_harness_name_override_with_non_matching_session_id_fails`
   - `test_explicit_harness_name_override_rejects_unknown_name`
   - `test_explicit_harness_name_override_rejects_parent_traversal`
   - `test_explicit_harness_name_override_rejects_path_separators`
   - `test_explicit_harness_name_override_rejects_absolute_path`

4. **No formal artifact mutation, no narrative-rule mutation, no KB schema change.** PAUTH allowed classes are `source` and `test_addition`; this plan stays within them.

## Risk / Rollback

**Risk surface:**

- The default-path cross-scan now reads from every registered harness's archive directory rather than a single resolved one. Read-only filesystem operations; no mutation. Performance impact is bounded — archive directories typically contain ≤100 envelope files per harness, and the scan terminates on first ambiguity or full enumeration.
- The cross-scan changes the failure mode for an explicit `session_id` that no archive contains: previously it would be "no envelope matches in harness-state/antigravity/..."; now it would be "no envelope matches in any scanned archive." This is the *intended* fix; any caller depending on the prior misleading message will see a clearer one.
- The validated `--harness-name` override hardens a previously-unvalidated path-segment surface. No existing caller depends on the unvalidated path because the flag is new.
- The `status` filter retirement may change behavior for any test fixture that depends on `status: "active"` being load-bearing. Audit: the existing `test_session_handoff_service.py` fixtures that supply `status: "active"` also have the archive directory present on the same record, so directory-presence still picks the right harness; fixtures continue to pass.

**Rollback:** Single-commit revert restores the prior behavior. The implementation report's recommended commit type is `fix:` so commit-history-driven tooling can identify the change. No data migration; no schema change; no KB row to revert.

## Bridge Filing

This REVISED is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-handoff-multi-harness-archive-resolution`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repair of broken resolver behavior with no new capability surface. The `--harness-name` CLI flag is a defensive validated override path that exists only because the resolver previously failed silently in the multi-archive case; it does not constitute a new feature in the SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001 contract sense.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
