REVISED

# Implementation Report — Bridge Poller Event-Driven Replacement (Slice 1 corrected + Slice 2)

bridge_kind: post_implementation_report
Document: gtkb-bridge-poller-event-driven-replacement-001
Version: 007 (REVISED post NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-005.md`

## Claim

This report consolidates two distinct deliverables under the same bridge thread:

1. **Slice 1 governance supersession (corrected)** — re-files the Slice 1 verification surface that was NO-GO'd at `-006` for two report-completeness defects (F1 missing INDEX-as-canonical evidence; F2 expected-not-observed verification rows). The substantive Slice 1 mutations are unchanged from `-005` and were independently validated as substantive-correct by Codex's `-006` Supporting Verification (rowids 8463, 1551 in MemBase; approval-packet hashes recompute correctly).
2. **Slice 2 cross-harness trigger detection script (new)** — implements the harness-agnostic detection + dispatch script per the GO'd proposal at `-004` Slice 2. Per the GO'd proposal at `-004`: "Slice 2 may be authored as a non-live development phase even before Slice 1 reaches VERIFIED, but Slice 3 (hook registrations) cannot ship until Slice 1 is VERIFIED." This Slice 2 work is non-live — the script + tests are present, but no hook registers it yet.

## Prior Deliberations

- `DELIB-0836` (rowid 844) — predecessor; superseded by Slice 1.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical foundation.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551) — Slice 1 supersession.

## Specification Links

Carried forward from the GO'd proposal at `-004`:

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved; this report cites the live INDEX block below as filing audit evidence (addresses `-006` F1).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Specification-Derived Verification table below has observed (not expected) outcomes per `-006` F2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Slice 2 artifacts under `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py`, `tests/scripts/test_cross_harness_bridge_trigger.py`. Default state directory `<project_root>/.gtkb-state/cross-harness-trigger/` is in-root.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — observed in this report's structure.

**Domain-specific:**

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 — Slice 1 inserted (rowid 8463); v2 status verified.
- `GOV-ARTIFACT-APPROVAL-001` v3 — Slice 1's three packets pass.
- `.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" — Slice 1 narrative edit applied; passed narrative-artifact-approval gate at the commit boundary in commit `2647848e`.

**Slice 2 specifications:**

- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` GO'd at `-004` Slice 2 §B1-B3 — drove the implementation.
- Smart-poller signature scheme reference: `groundtruth-kb/scripts/bridge_poller_runner.py::_pending_signature` lines 215-225 (byte-identical reproduction in the new script).

## Owner Decisions / Input

Slice 1 carries forward the scoped auto-approval batch `event-driven-replacement-slice-1-batch-2026-05-09` under `GOV-ARTIFACT-APPROVAL-001` v3, owner-acknowledged via AskUserQuestion before the first packet of the batch landed.

Slice 2 has NO new owner-decision dependence:

- The script + tests are non-live development artifacts.
- No formal artifact (spec, deliberation, GOV/ADR/DCL/PB) is created or mutated by Slice 2.
- No narrative file is edited by Slice 2.
- The hook registrations that activate the script live in Slice 3 and are explicitly gated by Slice 1 VERIFIED per the GO'd proposal at `-004`.

The S337 owner directive history relevant to this thread (carried forward from `-003`):

| Question | Answer |
|---|---|
| Project stance is stale — what's the next concrete step? | "Run the empirical retest now" |
| Codex hooks confirmed live on Windows — next step? | "Capture as DELIB, then file scoping bridge for full architecture" |
| Two threads, one GO + one NO-GO — next action? | "Address NO-GO -002 first (REVISED-1 on event-driven)" |
| (S337 most recent) | "Please proceed with the implementation of the gtkb-bridge-poller-event-driven-replacement" |

## Bridge INDEX-as-canonical-state Evidence (F1 fix)

Per `-006` F1 and `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: the live `bridge/INDEX.md` working-tree block for this thread at filing time of this report (`-007`):

```
Document: gtkb-bridge-poller-event-driven-replacement-001
REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-007.md
NO-GO: bridge/gtkb-bridge-poller-event-driven-replacement-006.md
NEW: bridge/gtkb-bridge-poller-event-driven-replacement-005.md
GO: bridge/gtkb-bridge-poller-event-driven-replacement-004.md
REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-003.md
NO-GO: bridge/gtkb-bridge-poller-event-driven-replacement-002.md
NEW: bridge/gtkb-bridge-poller-event-driven-replacement-001.md
```

INDEX update method: this version (`-007`) is inserted as a `REVISED:` line at the top of the document's version list per `.claude/rules/file-bridge-protocol.md` Index File / Statuses contract. The audit chain is monotonic and append-only: the prior `NO-GO -006`, `NEW -005`, `GO -004`, `REVISED -003`, `NO-GO -002`, `NEW -001` lines are preserved in their original order.

## Slice 1 Substantive Evidence (carried forward from `-005`)

Independent positive verification by Codex at `-006` confirmed:

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 rowid 8463; status `verified`; `changed_by=claude/harness-B/prime-builder`; `change_reason` cites the approval packet at `.groundtruth/formal-artifact-approvals/2026-05-09-ADR-CODEX-HOOK-PARITY-FALLBACK-001-V2.json`.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` rowid 1551; `source_type=owner_conversation`; `outcome=owner_decision`.
- Approval packet full-content hashes recompute correctly:
  - ADR packet: `787dc3fe0f0958f6e3fd8104f287165003f9a0b8829dbe446e2d87cf4f3d7740`
  - narrative packet: `20036d88ad486800d0fd42b6ff21508f46f16ba8567840080962eec4dd80b17e`
  - DELIB packet: `5b64d2451d259fbff50ab28f1f7675c80a7f2282c8cf51b6a28a3679c225f97a`
- ADR v2 DB description matches the ADR approval packet `full_content`.
- DELIB DB content matches the DELIB approval packet `full_content`.
- `.claude/rules/acting-prime-builder.md` normalized text hash matches the narrative approval packet hash.
- No `DCL-CODEX-HOOK-PARITY-FALLBACK-001` row exists (consistent with `-003` REVISED scope after F4 dropped the DCL).

Slice 1 commit: `2647848e` ("feat(governance): GTKB-BRIDGE-POLLER-EVENT-DRIVEN-REPLACEMENT-001 Slice 1").

## Slice 2 Implementation Evidence (NEW)

### B1. Script: `scripts/cross_harness_bridge_trigger.py`

Created. 374 lines. Key design decisions:

- **Live-INDEX-signature dispatch (per F1 of REVISED-1)**: `_read_index_live` reads `<project_root>/bridge/INDEX.md` from the working tree on every fire. No git involvement; uncommitted edits drive dispatch.
- **Signature scheme byte-identical to smart-poller**: `_signature` produces the same SHA-256 hex as `bridge_poller_runner._pending_signature` for the same input items (verified by test `test_dispatch_state_schema_matches_smart_poller_signature_scheme`). This means Slice 4 (smart-poller retirement) does not require a signature reset.
- **Loop prevention**: `GTKB_NO_CROSS_HARNESS_TRIGGER=1` env var short-circuits at the entry of `run_trigger`. Set on subprocess env in `_spawn_harness` so the dispatched harness's tool-use hooks during its turn do NOT recursively re-fire.
- **Fire-and-forget exit semantics**: `main()` always returns `0`. Internal failures are caught by the catch-all in `main`, logged to stderr, and recorded to `<state-dir>/dispatch-failures.jsonl` when state-dir is resolvable.
- **Path parameterization**: `--state-dir` flag accepts override; default `<project_root>/.gtkb-state/cross-harness-trigger/`. Slice 4 may decide to reuse smart-poller path; tests do not encode the path.
- **Kind-aware dispatch filter (per smart-poller-kind-aware-routing-009 §1.5)**: filters on `dispatchable=True` before signature/spawn so terminal-kind GO entries don't spawn redundant Prime harnesses.

### B2. Tests: `tests/scripts/test_cross_harness_bridge_trigger.py`

Created. 8 tests; all passing. Mapping to T-2-* test plan rows:

| Test plan row | Test name |
|---|---|
| T-2-signature-computation | `test_signature_computation_is_deterministic_per_recipient` |
| T-2-uncommitted-INDEX-triggers | `test_uncommitted_index_edit_triggers_dispatch` |
| T-2-stale-commit-no-replay | `test_unchanged_signature_does_not_replay` |
| T-2-dispatch-state-idempotence | `test_dispatch_state_idempotent_writes_on_unchanged_signature` |
| T-2-dispatch-on-changed-signature (proposal §B2 implicit) | `test_dispatch_fires_on_signature_change` |
| T-2-loop-prevention | `test_loop_prevention_env_var_no_ops` |
| T-2-fire-and-forget | `test_main_returns_zero_even_on_internal_failure` |
| T-2-codex-hook-firing-regression (schema half) | `test_dispatch_state_schema_matches_smart_poller_signature_scheme` |

### B3. Harness-agnostic invocation

`_harness_command` produces `claude -p ...` for `recipient=prime` and `codex exec ...` for `recipient=codex`. Slice 3's hook registrations on EITHER harness invoke the same script (Codex's hook fires it for prime-actionable signature changes; Claude's hook fires it for codex-actionable signature changes).

## Specification-Derived Verification (observed, not expected — F2 fix)

| Verification | Spec | Observed result |
|---|---|---|
| Slice 1 ADR v2 inserted | ADR-CODEX-HOOK-PARITY-FALLBACK-001 (governance supersession) | rowid 8463 present, status verified, change_reason cites approval packet path. Independently confirmed by Codex `-006` Supporting Verification. |
| Slice 1 deliberation supersession | DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08 | rowid 1551 present, source_type=owner_conversation, outcome=owner_decision; references DELIB-0836 + DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08. Confirmed by Codex `-006`. |
| Slice 1 narrative edit | acting-prime-builder.md "Harness Hook Parity Fallback Principle" reflects v2 stance | Narrative-artifact-approval gate accepted at commit time of `2647848e`; pre-commit log line `PASS narrative-artifact evidence (1 cleared)` (from session record). Codex `-006` independently confirmed normalized text hash matches narrative approval packet hash. |
| Applicability preflight (Slice 1 + Slice 2 combined) | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Command `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001` returned `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:df66b3b016947714634dd18e1efa34b023eed7ec8b36ffcc3d26d83cc2880894`. Run at filing time of this `-007`. |
| Clause preflight (Slice 1 + Slice 2 combined) | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 / GOV-FILE-BRIDGE-AUTHORITY-001 | Command `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001` exit `0`. Evidence gaps in must_apply clauses: 0. Blocking gaps: 0. Run at filing time of `-007` against the operative file at the time of preflight execution. |
| Slice 2 script presence | proposal §B1 | `scripts/cross_harness_bridge_trigger.py` exists; ruff clean. |
| Slice 2 test pass | proposal §B2 (8 tests) | `python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -x -v` → 8 passed in 1.50s. |
| Slice 2 ruff clean | code-quality default | `python -m ruff check scripts/cross_harness_bridge_trigger.py tests/scripts/test_cross_harness_bridge_trigger.py` → "All checks passed!" |
| Slice 2 signature byte-equivalence with smart-poller | Slice 4 forward-compat invariant | `test_dispatch_state_schema_matches_smart_poller_signature_scheme` passes — script `_signature` matches `bridge_poller_runner._pending_signature` byte-for-byte for the same INDEX state. |

## Acceptance Criteria — Status

For Slice 1 VERIFIED (per `-004` GO):

- [x] ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 inserted with packet — `-005` evidence + `-006` Supporting Verification.
- [x] Narrative edit reflects new live-on-Windows reality — `-005` evidence + `-006` Supporting Verification.
- [x] Deliberation references DELIB-0836 + DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST — `-005` evidence + `-006` Supporting Verification.
- [x] Pre-commit narrative-artifact gate passed at commit `2647848e` — narrative-artifact gate cleared in pre-commit run.
- [x] (NEW per `-006` F1) INDEX-as-canonical evidence in this report — section above.
- [x] (NEW per `-006` F2) Verification rows are observed, not expected — table above.
- [x] (NEW per `-006`) Clause preflight exit 0 observed — recorded above.

For Slice 2 (non-live development phase per `-004`):

- [x] B1 script present, lint-clean, harness-agnostic, fire-and-forget, loop-prevention env var honored.
- [x] B2 tests present and all 8 passing.
- [x] B3 hook registrations remain OUT OF SCOPE for Slice 2; Slice 3 lands them gated on Slice 1 VERIFIED.

## Files Changed (cumulative across Slice 1 commit `2647848e` + Slice 2)

**Slice 1 (committed `2647848e`):**

- `groundtruth.db` — rows for `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (rowid 8463) and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551).
- `.groundtruth/formal-artifact-approvals/2026-05-09-ADR-CODEX-HOOK-PARITY-FALLBACK-001-V2.json` (approval packet).
- `.groundtruth/formal-artifact-approvals/2026-05-09-DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08.json` (approval packet).
- `.groundtruth/formal-artifact-approvals/2026-05-09-ACTING-PRIME-BUILDER-MD-HOOK-PARITY-REFRESH.json` (narrative-artifact approval packet).
- `.claude/rules/acting-prime-builder.md` — narrative edit applied.
- `bridge/gtkb-bridge-poller-event-driven-replacement-005.md` (initial Slice 1 post-impl, now superseded by this `-007`).

**Slice 2 (this filing, pending commit):**

- `scripts/cross_harness_bridge_trigger.py` (NEW, 374 lines).
- `tests/scripts/test_cross_harness_bridge_trigger.py` (NEW, 8 tests).
- `bridge/gtkb-bridge-poller-event-driven-replacement-007.md` (this report, NEW).
- `bridge/INDEX.md` (REVISED line for this entry).

## Recommended Commit Type

`feat:` — adds net-new operational capability surface (`scripts/cross_harness_bridge_trigger.py` + 8-test suite). Even though hooks remain unregistered until Slice 3, the script is a new module that downstream Slice 3 + Slice 4 work depends on. `feat:` matches per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline (>20-line net-new capability with tests = `feat`).

## Risk / Rollback

Slice 1 risk + rollback: unchanged from `-005` (append v3 to ADR if reverting; no narrative-edit revert needed since the v2 stance is empirically correct per the retest evidence).

Slice 2 risk + rollback (cumulative):

- **Pre-Slice-3 state**: the script exists but no hook invokes it. Working trees that fire `python scripts/cross_harness_bridge_trigger.py` manually will write to `.gtkb-state/cross-harness-trigger/dispatch-state.json` and may dispatch a real subprocess. The `--dry-run` flag prevents subprocess spawn (used in tests).
- **Rollback**: revert the script + tests; no dispatch state remains active because no hook is wired yet.
- **Forward-compat with Slice 4**: signature byte-equivalence with smart-poller means Slice 4 can either reuse `.gtkb-state/bridge-poller/dispatch-state.json` or migrate to `.gtkb-state/cross-harness-trigger/dispatch-state.json` without a signature reset cascade.

## Open Follow-Ons (carried forward from `-003`)

1. Codex narrative-artifact-gate live promotion (per F5 of REVISED-1) — to be filed as `gtkb-narrative-artifact-approval-extension-codex-live-promotion-001` after THIS thread reaches VERIFIED.
2. `gt bridge` CLI subcommand foundation — shared with `gtkb-bridge-skill-unified-001` Slice 3 (deferred).
3. Decision: dispatch-state file path reuse vs new path — resolved during Slice 4 implementation.

## Loyal Opposition Asks

1. Confirm `-006` F1 is addressed: this report contains the live INDEX block in §"Bridge INDEX-as-canonical-state Evidence" and the clause preflight observed exit 0 in §"Specification-Derived Verification".
2. Confirm `-006` F2 is addressed: §"Specification-Derived Verification" rows are now observed. No row reads "expected" or "will validate at commit time."
3. Confirm Slice 2's non-live development scope per `-004` GO is acceptable for this report's combined-Slice-1-Slice-2 framing — i.e., that VERIFIED on Slice 1's substantive mutations + filed-but-unregistered Slice 2 script-and-tests is the correct intermediate state before Slice 3.
4. If VERIFIED, the next thread version should commit Slice 2's two new files plus the INDEX update plus this report, then file Slice 3 separately as a fresh NEW.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
