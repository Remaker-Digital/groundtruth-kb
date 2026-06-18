NEW

# gtkb-handoff-multi-harness-archive-resolution — Retire status:active pool-narrowing in handoff resolver; add --harness-name CLI override

bridge_kind: implementation_proposal
Document: gtkb-handoff-multi-harness-archive-resolution
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-18 UTC

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: 94112412-fe8d-406f-9f4b-d03dc87f2ee1
author_model: claude-opus-4-7
author_model_version: opus-4-7
author_model_configuration: claude-code-cli; durable role prime-builder; session interactive (no GTKB_BRIDGE_POLLER_RUN_ID)

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

`gt session handoff generate` silently selects the wrong harness archive when the live `harness-state/harness-identities.json` contains a `status: "active"` field on some records and not others — which became the production state after the 2026-05-31 antigravity registration and 2026-06-09 openrouter registration. The CLI reports `No archived envelope matches session_id='B-...' in harness-state/antigravity/session-envelope-archive` even when the requested envelope lives in `harness-state/claude/session-envelope-archive/`. The deterministic handoff-prompt service is therefore unusable on the canonical multi-harness install steady state.

Root cause: `_resolve_active_harness_name` (handoff.py:185) first narrows the resolver pool to records with `status == "active"` (lines 214-217) and only falls back to the full pool when that set is empty. The directory-presence disambiguator then runs against the narrowed pool, leaves `antigravity` as a single candidate, and the documented multi-candidate `HandoffError` (line 229) is unreachable. The `-008` REVISED report explicitly kept the `status` filter "for forward compatibility with fixtures that supply it" under the assumption no live records would carry `status`; that assumption broke when antigravity/openrouter were registered.

This proposal:

1. Retires the `status: "active"` pool-narrowing in `_resolve_active_harness_name` so directory-presence is the sole disambiguator per the function's own docstring contract.
2. Adds an optional `harness_name` parameter to `generate(...)` and a corresponding `--harness-name` CLI flag on `gt session handoff generate` (mirroring the `gt session wrap` pattern at `cli_session_handoff.py:131`). When supplied, the explicit name is used and resolution is skipped; when omitted, the (fixed) resolver runs.
3. Adds two regression tests covering the live registry shape (status on some records, archives only on no-status records) and the explicit-override path.

The `status` field semantics in `harness-identities.json` are NOT touched in this scope. The field remains in the schema; this fix only removes the resolver's load-bearing dependence on it. A future deliberation can decide whether `status` should be retired, promoted, or formally documented.

## Specification Links

- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` — governing requirement for the deterministic handoff-prompt service. Per § Inputs, `<harness_name>` is resolved "from the `session_id` + directory contents at service invocation time." The current resolver violates this contract by interposing a `status: "active"` filter that prevents directory-presence from disambiguating against the full enumerated pool. This proposal restores directory-presence as the sole disambiguator and adds an explicit-override path for callers that need to bypass resolution entirely.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed as the next versioned bridge file under that authority. Authorizes the NEW/REVISED/GO/NO-GO/VERIFIED status flow this thread will follow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires every implementation proposal to cite every relevant governing specification. This section is the citation surface for that mandate; preflight verification packet is appended in the Applicability Preflight section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires `Project Authorization`, `Project`, and `Work Item` headers in implementation proposals. Headers are present at lines 18-20 above (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER / PROJECT-GTKB-RELIABILITY-FIXES / WI-4659).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the implementation report to carry forward this proposal's linked specs and provide spec-to-test mapping with executed evidence before `VERIFIED`. Test plan derived from each linked spec is documented in the Spec-Derived Verification Plan section below.
- `GOV-STANDING-BACKLOG-001` — WI-4659 is admitted to PROJECT-GTKB-RELIABILITY-FIXES per `gt projects add-item` evidence (membership PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation authorization is bounded by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER (allowed mutation classes: source, test_addition; included WI: WI-4659; included spec: SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001).

## Prior Deliberations

- `DELIB-20265222` — owner AUQs (this session, 2026-06-18) approving fix scope (CLI flag + resolver fix) and fresh bridge thread under SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001. Carried into the Owner Decisions / Input section below.
- `DELIB-20261093` — Loyal Opposition NO-GO on `gtkb-handoff-prompt-deterministic-service-impl-006` (2026-06-05). Surfaced the exact symptom this proposal addresses: the live CLI smoke at the time failed because the resolver "selects missing `harness-state\antigravity\session-envelope-archive`." This proposal's fix is the logical completion of the partial fix attempted at `-007`/`-008` (see DELIB-20261779).
- `DELIB-20261779` — compressed VERIFIED record for the 11-version `gtkb-handoff-prompt-deterministic-service-impl` thread. The `-008` REVISED report (FINDING-P1-002 revision-1) explicitly kept the `status: "active"` filter as a "forward compatibility" surface on the now-broken assumption that "no record carries `status`" in production. This proposal retires that filter; it does not contradict the prior fix's direction (directory-presence as disambiguator) — it removes the load-bearing dependence on `status` that the prior fix left in place.
- `DELIB-20261091` — original GO verdict on the impl thread; establishes the service's design authority and is preserved as the spec's adoption record. This proposal makes no design change to the service contract; it repairs the resolver's adherence to that contract.
- `DELIB-20264109` — VERIFIED for handoff-prompt terminology clarification (DELIB-20260883). Establishes "handoff prompt" as the canonical term for the generated output. No conflict with this scope.

The seeded `INTAKE-*` and `DELIB-WI4546-PHASE-B-*` candidates returned by the scaffold helper's semantic search are unrelated to handoff resolver behavior and have been pruned.

## Owner Decisions / Input

Owner approval for this scope was captured via two AskUserQuestion calls in the interactive Prime Builder session 94112412-fe8d-406f-9f4b-d03dc87f2ee1 on 2026-06-18 UTC. Full text and rationale archived at `DELIB-20265222` (formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-06-18-DELIB-20265222.json`, content sha256 `1c1db8b2dbbeb291dbe17c776767716d18e8b09c4e6d4f770afddaae31b30997`).

| AUQ | Question | Owner answer |
|---|---|---|
| AUQ-2026-06-18-HANDOFF-RESOLVER-SCOPE-AND-HOME (q1) | Which fix scope should the bridge proposal cover? | Option 1 — CLI flag + resolver fix |
| AUQ-2026-06-18-HANDOFF-RESOLVER-SCOPE-AND-HOME (q2) | Should the proposal file under the existing handoff spec or as a fresh thread? | Option 1 — Fresh bridge thread under SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001 |

No additional owner decision is required before Loyal Opposition review. Implementation begins only after Codex GO on this thread + implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-handoff-multi-harness-archive-resolution`).

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` already specifies the deterministic resolution contract — its § Inputs require `<harness_name>` to be resolved from the session_id + directory contents at invocation time, which directory-presence-only disambiguation satisfies. The `--harness-name` CLI flag is an explicit-override path that lets callers supply the value the spec mandates be resolved; it does not change the spec's resolution contract. No new requirement or spec amendment is needed.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
|---|---|---|
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_handoff_service.py -q --no-header` | All existing tests still pass; two new regression tests pass (multi-harness-with-status-active-elsewhere case; explicit `harness_name` override case). |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (live CLI smoke) | `python -m groundtruth_kb session handoff generate --harness-name claude --session-id <existing-B-session-id> --json` | Exits 0; resolves the envelope from `harness-state/claude/session-envelope-archive/`; emits a deterministic prompt; CLI never errors with `harness-state/antigravity/...` in the failure message. |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (default-resolver smoke) | `python -m groundtruth_kb session handoff generate --session-id <existing-B-session-id> --json` against the live registry (claude + codex + antigravity all have archive dirs; antigravity/openrouter have status:active) | Exits non-zero with the documented multi-candidate `HandoffError` ("Cannot deterministically resolve active harness: multiple harnesses have session-envelope archives ..."), demonstrating the documented error path is now reachable in production. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-handoff-multi-harness-archive-resolution` | `preflight_passed: true`, `missing_required_specs: []`. Packet hash appended to verdict by Loyal Opposition. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight (above) | Same. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header inspection on this file | PAUTH/Project/Work Item headers present at lines 18-20 above. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This Spec-Derived Verification Plan section + implementation report carry-forward | Spec-to-test mapping carried forward in implementation report. |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-4659` after VERIFIED | WI-4659 admitted to PROJECT-GTKB-RELIABILITY-FIXES; resolution evidence cites this thread. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES` | PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4659-HANDOFF-RESOLVER active; includes WI-4659; mutation classes `source` + `test_addition` only. |
| Pre-file code-quality gates | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>` AND `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed.py>` | Both pass cleanly per file-bridge-protocol § "Pre-File Code-Quality Gates." |

## Implementation Plan

1. **`groundtruth-kb/src/groundtruth_kb/session/handoff.py` — resolver and `generate()` signature:**
   - Add `harness_name: str | None = None` parameter to `generate(...)`.
   - In `generate(...)`, after `root = ... .resolve()`: if `harness_name is not None`, use it directly (after validation that `harness-state/<harness_name>/session-envelope-archive` exists, raising `HandoffError` with explicit name if not). Otherwise call `_resolve_active_harness_name(root)`.
   - In `_resolve_active_harness_name`: remove lines 214-217 (`explicit_active = [...]; pool = explicit_active or list(harnesses.keys())`). Replace with `pool = list(harnesses.keys())` (directory-presence is the sole disambiguator per the function's docstring contract).
   - Update the docstring (lines 192-202) to describe the corrected behavior: directory-presence is the sole disambiguator regardless of any `status` field on identity records.

2. **`groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` — CLI flag:**
   - Add `@click.option("--harness-name", default=None, help="Explicit harness name to resolve archives from. When omitted, the resolver disambiguates by directory presence among enumerated harnesses.")` to `generate_cmd` (around line 181).
   - Add `harness_name: str | None` parameter to `generate_cmd(...)` signature.
   - Pass `harness_name=harness_name` through to `generate(...)` (around line 212).

3. **`platform_tests/scripts/test_session_handoff_service.py` — regression tests:**
   - Add `test_resolve_active_harness_ignores_status_active_when_archive_lives_on_no_status_record`. Fixture: identities = `{"harnesses": {"claude": {"id": "B"}, "antigravity": {"id": "C", "status": "active"}, "openrouter": {"id": "F", "status": "active"}}}`. Archive only on `harness-state/claude/`. Assert resolver returns `"claude"`.
   - Add `test_generate_accepts_explicit_harness_name_override`. Fixture: identities with multiple status:active records and archives in multiple locations. Call `generate(harness_name="claude", session_id=..., project_root=..., db=...)`. Assert the resolved archive path is `harness-state/claude/...`, not the alphabetically-first or status-narrowed candidate.

4. **No formal artifact mutation, no narrative-rule mutation, no KB schema change.** PAUTH allowed classes are `source` and `test_addition`; this plan stays within them.

## Risk / Rollback

**Risk surface:**

- The retirement of the `status: "active"` filter changes resolver behavior for any caller that depends on `status` being load-bearing. Audit: a `Grep` for `status.*active` references in test fixtures of `test_session_handoff_service.py` shows two fixture cases (lines 64, 80 setup) that supply `status: "active"` on a record. These tests' assertions are about the explicit-active selection working; under the new behavior, directory-presence still picks the right harness in those fixtures because the same record also has its archive directory present. The fixtures will continue to pass; the test names may be slightly less precise but no test will break.
- The `--harness-name` flag is additive (default `None`); no existing CLI caller breaks.
- The CLI's default-resolver path may now error in production where it previously succeeded silently (because antigravity/claude/codex all have archive dirs → multi-candidate error reachable). This is the *intended* fix outcome — silently picking the wrong harness is the bug being repaired — but operators who depend on the silent-pick behavior (none expected) will need to start passing `--harness-name`.

**Rollback:** Single-commit revert restores the prior behavior. The implementation report's recommended commit type is `fix:` so commit-history-driven tooling can identify the change. No data migration; no schema change; no KB row to revert.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-handoff-multi-harness-archive-resolution`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repair of broken resolver behavior with no new capability surface. The `--harness-name` CLI flag is a defensive override path that exists only because the resolver previously failed silently; it does not constitute a new feature in the SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001 contract sense.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
