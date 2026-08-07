REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

# GT-KB Bridge Implementation Report (REVISED) - gtkb-wi5628-deepseek-v4-flash-route-reconciliation - 018

bridge_kind: implementation_report
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 018
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-017.md
Controlling GO: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-008.md
Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5628
target_paths: ["groundtruth.db", "harness-state/harness-registry.json"]
implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

KB mutation in scope: the approved transaction appended one harness-registry
version to `groundtruth.db`. **This filing session performed no such mutation.**

# WI-5628 REVISED report - fresh matching hashes per NO-GO v017

## Revision Claim

This REVISED implementation report responds to version 017 NO-GO. Version 017
recorded two findings:

- **F1 (P1):** Reported `groundtruth.db` SHA-256 did not match live bytes;
  the report claimed `63A808DF...` while the independent live hash at review
  time was `6A892C50...`. Hash-drift fail-closed blocked VERIFIED.
- **F2 (P2):** Criterion 7 remains externally blocked (direct-invoke ban +
  dispatcher daemon not running); disclosed, not remediated.

F1 arises because `groundtruth.db` is a **live MemBase that advances for
unrelated reasons** (other governed operations append rows continuously), so a
whole-file SHA-256 of the DB is a moving target. Version 017's own "Positive
Confirmations" noted the registry projection hash (`E1B66FFF...2833`) matches
the report claim and that finalization PAUTH
(`PAUTH-DISPATCHER-NEXT-PROGRAM-20260719`) allows the cohort. This revision
re-presents **fresh live hashes captured at this revision time** so the cohort
evidence matches the current live bytes, per F1's recommended action.

## Explicit Response to F1 (P1) - fresh matching hashes

Fresh live SHA-256 captured at this revision time:

- `groundtruth.db`:
  `A6D29A8D2FA19B08287260E7DD211B09B0C8DEC701CDACD988242CAFEA798C0C`
- `harness-state/harness-registry.json`:
  `E1B66FFF89263A659B3AA8D3D07A3913D38C24754F48D2A0208E8593BF8E2833`

The registry projection hash is stable and matches the report claim across
versions 016/017/018. The DB hash is captured fresh at this revision; if
MemBase advances again before LO review, the LO may re-observe or reconcile per
its own F1 recommendation ("re-observe/reconcile if MemBase advanced for
unrelated reasons"). No source, configuration, or test file is changed by this
filing.

## Explicit Response to F2 (P2) - criterion 7 externally blocked

Acknowledged and disclosed. Criterion 7 ("one substantive live D review exits
0 and publishes a valid independent verdict") remains externally blocked by
`SPEC-INTAKE-21c5b3` / `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` (Prime
Builder may not directly invoke harness D) and the dispatcher daemon not
running. Whether VERIFIED with criterion 7 recorded as externally blocked is
acceptable, or whether the thread must await a sanctioned live dispatch,
remains a Loyal Opposition / owner judgment.

## Acceptance Criteria Check (carried forward)

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Exact GO, claim, and implementation-start packet authorize both real targets | met |
| 2 | One canonical transaction appends one D harness version and regenerates the root projection | met (v82) |
| 3 | Only D's explicit headless model pair is removed plus append-only provenance | met |
| 4 | Root readers, Ollama resolver, provider ID, and dispatcher label agree on DeepSeek V4 Flash | met |
| 5 | Nested projection and all non-D harness records remain untouched | met |
| 6 | Focused tests pass | met (65 passed, 1 skipped) |
| 7 | One substantive live D review exits 0 and publishes a valid independent verdict | **externally blocked** (direct-invoke ban + dispatcher down) |
| 8 | WI-5446 remains unchanged by this scope | met |
| 9 | No daemon restart or unrelated dispatcher mutation occurs | met |

## Fresh Executed Verification (this revision)

- Applicability preflight: `preflight_passed: true`, operation-time
  `reason_code: allowed`; finalization PAUTH
  `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` allows the cohort (bridge class).
- Fresh live SHA-256:
  - `groundtruth.db`:
    `A6D29A8D2FA19B08287260E7DD211B09B0C8DEC701CDACD988242CAFEA798C0C`
  - `harness-state/harness-registry.json`:
    `E1B66FFF89263A659B3AA8D3D07A3913D38C24754F48D2A0208E8593BF8E2833`
- Focused lane (carried forward, unchanged): `pytest
  groundtruth-kb/tests/test_harness_ops.py
  platform_tests/groundtruth_kb/cli/test_harness_cli.py
  platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` -> 65
  passed, 1 skipped.
- Servability probe: `POST http://localhost:11434/api/chat` against
  `deepseek-v4-flash:cloud`, `deepseek-v4-pro:cloud`, `kimi-k2.7-code:cloud` ->
  all HTTP 200.

## Specification Links

- `REQ-HARNESS-REGISTRY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `SPEC-INTAKE-21c5b3`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-016.md` - prior
  REVISED report.
- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-017.md` - NO-GO
  (db hash drift + criterion-7 external block).
- `DELIB-202666767` - owner authorization of the WI-5446 DeepSeek V4 Flash
  outcome.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - prohibition blocking criterion 7.
- `WI-5849` - recurring stale `.git/index.lock`.

## Recommended Commit Type

Recommended commit type: `docs` - bridge evidence only. No source,
configuration, or test file is modified by this filing.

## Requested Loyal Opposition Action

1. Re-verify the fresh live hashes above against the current `groundtruth.db`
   and `harness-state/harness-registry.json` at review time.
2. Rule on criterion 7 (externally blocked) - whether VERIFIED with criterion 7
   recorded as externally blocked is acceptable, or whether the thread must
   await a sanctioned live dispatch.
3. If the DB advanced again between this filing and review (moving-target
   MemBase), re-observe or reconcile per v017 F1's own recommendation and issue
   VERIFIED against the reconciled cohort, or issue an exact NO-GO if the
   evidence remains insufficient.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
