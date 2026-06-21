NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Bridge work-intent registry raises on legacy/unrecognized bridge status tokens (e.g. PAUSED), blocking governed writes to those threads

bridge_kind: prime_proposal
Document: gtkb-work-intent-registry-tolerates-legacy-status
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4660

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The direct work-intent claim path in `scripts/bridge_work_intent_registry.py` raises on any versioned bridge file whose first-line token is not in `BRIDGE_FILE_STATUS_RE` (e.g. the legacy `PAUSED` token). `acquire()` scans **all** versions of a thread (`acquire` -> `_claim_values` -> `_latest_status` -> `_thread_version_entries` -> `_bridge_file_status`), and `_bridge_file_status` raises `MalformedBridgeStatusError` on the first unrecognized token. Because `acquire()` only catches `sqlite3.Error`, that exception propagates to the claim CLI (exit 3). Since the governed Write path requires a work-intent claim (enforced by `bridge-compliance-gate`), and bridge files are append-only (the legacy token cannot be deleted), any thread shadowed by a single legacy-token version becomes permanently un-claimable and therefore impossible to transition to a canonical terminal status (`WITHDRAWN`) through the governed path.

## Defect / Reproduction

Observed live on 2026-06-18 while executing the owner-approved Bucket C `WITHDRAWN` disposition: the three `commercial-readiness-spec-*` threads each carry a `-003.md` version whose first non-blank line is exactly `PAUSED` (paused 2026-04-23). `PAUSED` is not in `BRIDGE_FILE_STATUS_RE` (`^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)$`), so:

- `bridge/commercial-readiness-spec-1831-startup-wiring-003.md`
- `bridge/commercial-readiness-spec-1833-ready-propagation-003.md`
- `bridge/commercial-readiness-spec-verification-007.md`

are each un-claimable: a work-intent claim against any of these slugs raises `WorkIntentRegistryError: Bridge file has unrecognized status line: ...: 'PAUSED'`, so the claim CLI exits 3, and `bridge-compliance-gate` then blocks the governed Write of the next (WITHDRAWN) version. The thread is stuck.

Reproduction (logical, deterministic): create a thread with two versions — `-001.md` with a canonical token (e.g. `NEW`) and `-002.md` whose first non-blank line is `PAUSED`. Call `acquire(slug, session_id)`. Expected: the claim is acquired (the legacy-token version is tolerated/skipped so the thread can be transitioned). Actual: `acquire()` raises `MalformedBridgeStatusError`.

Distinction from the already-VERIFIED sibling fix (critical, see Prior Deliberations): the WI-4658 quarantine fix (`gtkb-dispatch-malformed-status-token-quarantine`, VERIFIED at `-004`) added the typed `MalformedBridgeStatusError` and made the **headless dispatch batch-acquire** path (`scripts/cross_harness_bridge_trigger.py::_acquire_prime_work_intent_batch`, which catches `MalformedBridgeStatusError` at line 1044) quarantine-and-continue. It deliberately did **not** change `_bridge_file_status` to stop raising (the typed raise is the contract its tests assert) and did **not** touch the direct-claim path (`acquire`/`current_holder`/`claim_status`/`_latest_status`). WI-4660 is the distinct, complementary gap: the direct-claim path that the governed Write requires.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_work_intent_registry.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the numbered `bridge/<slug>-NNN.md` chain is the authoritative workflow surface and is append-only; the registry that reads those tokens for the governed-write claim path must handle a grandfathered legacy token as drift rather than permanently blocking the thread's lawful transition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable artifact lifecycle by letting a legacy-token-shadowed thread reach its canonical terminal `WITHDRAWN` state through the governed path instead of being stranded.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing specification it is constrained by (mandatory linkage gate).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from a cited spec clause (mandatory spec-derived testing gate).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Project Authorization / Project / Work Item triple is declared in the metadata block above (mandatory project-linkage gate).
- `SPEC-AUQ-POLICY-ENGINE-001` - governs owner-decision (AUQ) routing; relevant here only to confirm no new owner-decision surface is introduced — this defect fix is authorized under the standing fast-lane PAUTH and creates no new AUQ requirement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform script module (`scripts/...`) and platform tests; no application/adopter placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4660 is the already-tracked standing-backlog item under PROJECT-GTKB-RELIABILITY-FIXES (no duplicate work item created; backlog checked pre-filing, including the related WI-4658 threads).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - governs Claude/Codex hook parity; relevant only to confirm scope — this fix touches a shared Python registry module consumed by the governed-write claim path on both harnesses, and changes no hook registration, so harness parity is preserved without edits to `.claude`/`.codex` hook surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposal -> review -> implement -> verify lifecycle for this fix is preserved as durable bridge artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the registry source brings the spec-to-test mapping under change control via the verification plan; tolerating a legacy-token version is a deterministic lifecycle-drift handling, not a silent skip.

## Prior Deliberations

- `gtkb-dispatch-malformed-status-token-quarantine` (VERIFIED at `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md`, WI-4658) - the sibling fix that added `MalformedBridgeStatusError` and the **dispatch-path** quarantine-and-continue. WI-4660 is scoped to the **direct-claim path** it did not change; this proposal does not reopen, modify, or duplicate that landed work.
- `gtkb-work-intent-registry-failsoft-status-parse` (closed/superseded at `bridge/gtkb-work-intent-registry-failsoft-status-parse-004.md`, WI-4658) - a narrower fail-soft-parse proposal closed as a duplicate of the quarantine thread. Its NO-GO (`-002`) correctly warned that broadening `_bridge_file_status` itself to *parse* a malformed token (e.g. treating `GO test` as `GO`) could convert a broken placeholder into spurious GO authorization. This proposal deliberately does NOT broaden `_bridge_file_status`'s parse semantics; it only makes the direct-claim version scan **skip** a permanently-unparseable version, preserving the typed-raise contract that the dispatch quarantine relies on.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - S382 owner decision establishing the body-status-token rule and the canonical token vocabulary; `PAUSED` predates that vocabulary, which is why it is a grandfathered legacy token rather than a malformed new write.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-4660 (P2, origin=defect) is in scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - the standing reliability fast-lane authorization. WI-4660 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the defect, adds no new/revised requirement or spec, and is bounded to ~1 source module + 1 test file (well under the fast-lane size guide), so it is covered through active project membership in PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items; this WI-4660 proposal is one of that batch. No further owner decision is required to implement after Loyal Opposition `GO` plus the implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes the append-only numbered-file chain as the authoritative surface and treats divergence as drift to be handled deterministically; the canonical-token vocabulary is fixed by `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`. This fix brings the direct-claim registry path into conformance with that existing contract (a grandfathered legacy token must not permanently block a thread's lawful governed transition). No new or revised requirement/specification is introduced; in particular, `PAUSED` is NOT promoted to a canonical status token — it remains a tolerated/skipped legacy token.

## Proposed Scope

1. In `scripts/bridge_work_intent_registry.py`, make `_thread_version_entries` **skip** a version whose first-line token cannot be parsed (a permanent `MalformedBridgeStatusError`) instead of letting it propagate, mirroring the compliance gate's `_status_from_versioned_bridge_file` (which returns `None` and skips). Concretely: wrap the `_bridge_file_status(path)` call in `_thread_version_entries` in a targeted `except MalformedBridgeStatusError` that records the offending path/line as a structured warning (e.g. via `warnings.warn` or a logged message carrying `exc.path` / `exc.offending_line`) and `continue`s to the next version.
   - Do NOT change `_bridge_file_status` itself: it MUST keep raising `MalformedBridgeStatusError` so the already-VERIFIED dispatch quarantine contract (`cross_harness_bridge_trigger` catching the typed error) and its tests (`test_bridge_file_status_raises_malformed_on_unrecognized_first_line`, `test_bridge_file_status_raises_malformed_on_empty_file`) remain intact.
   - Keep the `WorkIntentRegistryError` raised for a genuinely unreadable file (the `OSError` path in `_bridge_file_status`) and the duplicate-version `WorkIntentRegistryError` in `_thread_version_entries` propagating — only the permanent per-file *parse* error (`MalformedBridgeStatusError`) is skipped. This keeps transient/structural failures loud while tolerating grandfathered legacy tokens.
   - Effect through the call chain: `_latest_status`, `acquire`, `current_holder`, `claim_status`, and `release` (all of which reach `_thread_version_entries`) tolerate a legacy-token-shadowed version, so a thread with a non-latest `PAUSED` version becomes claimable and can be transitioned to `WITHDRAWN` through the governed Write path.
2. Add regression tests in `platform_tests/scripts/test_bridge_work_intent_registry.py` (see verification plan), reusing the existing `_write_bridge_file` helper and the `env` fixture.

This is the defect-removal path only. Broadening `_bridge_file_status` to *parse* malformed tokens (the rejected approach from the failsoft thread's NO-GO) and any modeling/display change are explicitly out of scope.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (append-only legacy token must not permanently block the governed claim path) | `test_acquire_tolerates_legacy_status_shadowed_thread` | A thread with `-001.md` = `NEW` and `-002.md` = `PAUSED` is claimable: `acquire(slug, session_id)` returns `True` and does NOT raise `MalformedBridgeStatusError`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (latest status derived from remaining parseable versions) | `test_latest_status_skips_legacy_token_version` | `_thread_version_entries` / `_latest_status` for that thread skip the `PAUSED` version and derive the latest status from the parseable versions (returns `NEW`), without raising. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (deterministic drift handling, not silent) | `test_legacy_token_version_skip_emits_warning` | Scanning the legacy-token-shadowed thread emits a structured warning carrying the offending path and line (e.g. via `pytest.warns`), proving the skip is recorded rather than silent. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (typed-raise contract preserved; no over-broadening) | `test_bridge_file_status_still_raises_on_unrecognized_token_regression` | `_bridge_file_status` itself STILL raises `MalformedBridgeStatusError` on a `PAUSED` first line (regression guard: the dispatch quarantine contract is unchanged; the fix lives in the version-scan caller, not the parser). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (transient/structural errors stay loud) | `test_unreadable_or_duplicate_version_still_raises` | An unreadable file (OSError path) and a duplicate-version condition still raise `WorkIntentRegistryError` — only the permanent parse error is skipped. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short`
- `python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py`
- `python -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py`

## Acceptance Criteria

1. `acquire()` (and `current_holder`/`claim_status`/`_latest_status`/`release`) succeed against a thread whose non-latest version carries a legacy/unrecognized first-line token (e.g. `PAUSED`), enabling the governed transition of the three live `commercial-readiness-spec-*` threads to `WITHDRAWN`.
2. `_bridge_file_status` is unchanged and still raises `MalformedBridgeStatusError` on an unrecognized token and on an empty file (the dispatch quarantine contract and its existing tests still pass).
3. Genuinely unreadable files and duplicate-version conditions still raise `WorkIntentRegistryError` (transient/structural failures remain loud); each version skip emits a structured warning carrying the offending path/line.
4. The five derived tests pass; the full `test_bridge_work_intent_registry.py` suite is green; `ruff check` and `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: skipping a legacy-token version could mask a genuinely corrupt **latest** version. Mitigation: every skip emits a structured warning carrying the offending path/line; the body-status-token PreToolUse gate (`bridge-compliance-gate`) already blocks new malformed writes, so this tolerance applies only to grandfathered/legacy artifacts.
- Risk: over-broadening could re-introduce the failsoft NO-GO failure mode (treating a broken placeholder as a valid status). Mitigation: `_bridge_file_status` parse semantics are unchanged — a skipped version contributes NO status, so a `PAUSED`/`GO test` version can never be read as a valid GO; it is simply excluded from the version set.
- Risk: a thread whose ONLY version is a legacy token would now be claimable but have no derivable status. Mitigation: that is the correct posture for the WITHDRAWN-transition use case (the governed Write then files a canonical version); duplicate-version and unreadable-file errors still raise, so structural problems remain visible.
- Rollback: revert the single guarded `except MalformedBridgeStatusError ... continue` in `_thread_version_entries` plus the added tests; the change is additive and fully reversible with no migration or state change.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

## Recommended Commit Type

`fix`
