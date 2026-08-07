REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

# GT-KB Bridge Implementation Report (REVISED) - gtkb-wi5628-deepseek-v4-flash-route-reconciliation - 020

bridge_kind: implementation_report
Document: gtkb-wi5628-deepseek-v4-flash-route-reconciliation
Version: 020
Responds to: bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-019.md
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

# WI-5628 REVISED report - non-drifting evidence strategy for the KB mutation

## Revision Claim

This REVISED implementation report responds to version 019 NO-GO. Version 019
recorded two findings:

- **F1 (P1):** Reported `groundtruth.db` whole-file SHA-256 again fails closed
  against live bytes because MemBase continues to advance; recommended action:
  "Stop using whole-file `groundtruth.db` SHA-256 as the fidelity gate for this
  thread. Prefer a stable harness-registry version/row evidence + projection
  hash (already stable) and/or a MemBase harnesses-table version id pinned in
  the report; then re-request VERIFIED. Re-hashing the moving DB alone will
  keep failing."
- **F2 (P2):** Criterion 7 remains externally blocked (direct-invoke ban +
  dispatcher daemon down); disclosed, not remediated.

This revision **adopts the non-drifting evidence strategy** for the KB
mutation cohort, per F1's explicit recommended action. It no longer relies on
the whole-file `groundtruth.db` SHA-256 as the fidelity gate; instead it pins
the stable, immutable harness-registry version row and the stable projection
hash as the attestation anchor.

## Explicit Response to F1 (P1) - non-drifting evidence strategy

### Stable evidence anchor: D harness-registry version row

The WI-5628 approved transaction appended one D harness-registry version to
`groundtruth.db`. The **D row is immutable and stable** at harness version
**`82`**:

- Harness id: `D`
- Harness name: `ollama`
- Version: `82`
- Status: `active`
- Change reason: "WI-5628: remove D model override and use canonical DeepSeek
  V4 Flash bridge-review route"
- Changed at: `2026-07-19T06:37:34+00:00`
- Changed by: `gt-harness-cli`

This row is the durable, non-drifting evidence of the KB mutation. It does not
change when unrelated MemBase rows advance; it is pinned to the exact WI-5628
transaction.

### Stable projection hash

`harness-state/harness-registry.json` SHA-256:
`E1B66FFF89263A659B3AA8D3D07A3913D38C24754F48D2A0208E8593BF8E2833`

This projection hash is stable and matches the report claim across versions
016/017/018/020. It is the reproducible serialization anchor for the registry
file.

### Deprecated whole-file DB hash (for record)

The whole-file `groundtruth.db` SHA-256 is **not** used as the fidelity gate in
this revision because the DB is a live MemBase that advances for unrelated
reasons (a moving target). A current reading at revision time is recorded for
transparency but is not the attestation anchor:
`4BB45726082C554C307BBFA0F968EFF1610BF9A7D7B47C2CFC1F6F8FDF0FC366`
(and it is expected to drift before LO review). The stable D-version-82 row and
projection hash above are the authoritative cohort evidence.

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
| 2 | One canonical transaction appends one D harness version and regenerates the root projection | met (D version 82) |
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
- Stable D harness-registry row: harness `D`, version `82`, status `active`,
  change_reason "WI-5628: remove D model override and use canonical DeepSeek
  V4 Flash bridge-review route" (via `gt harness show --harness D`).
- Stable projection hash `harness-state/harness-registry.json`:
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

- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-018.md` - prior
  REVISED report (fresh-hash strategy).
- `bridge/gtkb-wi5628-deepseek-v4-flash-route-reconciliation-019.md` - NO-GO
  (moving-target DB hash; recommended non-drifting evidence strategy).
- `DELIB-202666767` - owner authorization of the WI-5446 DeepSeek V4 Flash
  outcome.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - prohibition blocking criterion 7.
- `WI-5849` - recurring stale `.git/index.lock`.

## Recommended Commit Type

Recommended commit type: `docs` - bridge evidence only. No source,
configuration, or test file is modified by this filing.

## Requested Loyal Opposition Action

1. Confirm the non-drifting evidence strategy is adequate: the immutable
   D harness-registry version **`82`** row (stable change_reason tied to
   WI-5628) plus the stable projection hash
   `E1B66FFF...2833` attest the KB mutation cohort.
2. Rule on criterion 7 (externally blocked) - whether VERIFIED with criterion 7
   recorded as externally blocked is acceptable, or whether the thread must
   await a sanctioned live dispatch.
3. Issue VERIFIED against the stable evidence anchor, or an exact NO-GO if the
   evidence remains insufficient.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
