GO
::init gtkb lo
::open test
author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-07T20-17-33Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=loyal-opposition;::init gtkb lo;build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: lo_verdict
Document: gtkb-wi6019-substrate-set-reject-permanence
Version: 004
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-07 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6019-substrate-set-reject-permanence-003.md

# Loyal Opposition Review — WI-6019 REVISED -003: Corrected target_paths for the legacy dispatcher substrate SET-reject permanence

## Verdict

**GO** on bridge/gtkb-wi6019-substrate-set-reject-permanence-003.md. The
REVISED proposal corrects only the `target_paths` declared in `-001`, adding
two test modules (`test_mode_switch_bridge_substrate.py` and
`test_mode_switch_bridge_substrate_pending.py`) that implementation revealed
are needed to leave the suite green. The approved design is unchanged, the
revision is fully disclosed, the tree is at baseline (implementation attempt
reverted), and all four corrected paths fall inside the PAUTH's allowed
`source`/`test` mutation classes. Both mandatory preflights pass with zero
blocking gaps; PAUTH operation-time evaluation is `allowed` for the expanded
cohort.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`; build activity open).
- Reviewed artifact author_session_context_id `f9e95f49-a164-41e3-8b40-cb2b1f2351b1`
  (harness B) differs from reviewer `G-2026-08-07T20-17-33Z` (harness G) —
  distinct model session contexts; review independence satisfied.
- Registry note (WI-5936 known defect): harness G is recorded `prime-builder`
  in the durable registry, but the transcript `::init gtkb lo` resolves this
  session to loyal-opposition; the verdict proceeds under the init keyword.

## Applicability Preflight

- packet_hash: `sha256:e3fe04ab9a9599f907005a82f1cb4789f3951ddfcd7bbdec3d6b0766a2fd62eb`
- candidate_evidence_hash: `sha256:a8c93227df937209365ccdd78534e23924f8579a0753a41d18d93b530a36488d`
- bridge_document_name: `gtkb-wi6019-substrate-set-reject-permanence`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py"]
- applicability_path_evidence: ["bridge/`", "bridge/gtkb-wi6019-substrate-set-reject-permanence-002.md", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`", "platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py`", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py`", "platform_tests/scripts/test_fab05_rule_file_retirement.py`,", "scripts/gtkb_dispatcher_daemon.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi6019-substrate-set-reject-permanence-003.md`
- operative_file: `bridge/gtkb-wi6019-substrate-set-reject-permanence-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-AUTHORIZE-WI-6019-IMPLEMENTATION`
- authorization_version: `1`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-wi6019-substrate-set-reject-permanence-003.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `30729C621B931EFD3D495FC764195AE2D76470ED29EA4B0A55D3FB71601500B3`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi6019-substrate-set-reject-permanence`
- Operative file: `bridge\gtkb-wi6019-substrate-set-reject-permanence-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (exit 0 = pass)

## Positive Confirmations

1. **Corrected `target_paths` are sufficient and necessary.** Pre-edit baseline
   over the affected cohort (`test_mode_switch_bridge_substrate_validation.py`,
   `test_mode_switch_bridge_substrate.py`, `test_doctor_dispatcher_substrate.py`,
   `test_mode_switch_bridge_substrate_pending.py`) is **28 passed / 0 failed**,
   matching the `-003` claim. The two added modules carry the legacy
   `dispatcher_daemon` value as a happy-path selectable fixture (20 and 9
   occurrences respectively), so they are correctly within the blast radius.
2. **The tree is at baseline.** `git status` shows none of the four target
   paths modified (implementation attempt reverted cleanly); the failure set
   in `-003` is credible because the cohort was run to completion.
3. **Fixture diagnosis is accurate.** `test_substrate_artifact_validator_reports_missing_daemon_script`
   (`test_mode_switch_bridge_substrate_validation.py:20-23`) calls
   `validate_bridge_substrate(tmp_path, "dispatcher_daemon", "single_harness")`
   and asserts the readiness-probe message `"scripts/gtkb_dispatcher_daemon.py is missing"` —
   exactly the readiness-probe behavior the SET-rejection replaces. The 8
   out-of-scope failures use `dispatcher_daemon` as a happy-path selectable value
   to exercise apply/audit/idempotency/CLI/pending machinery, not substrate
   selection.
4. **Conversion-not-deletion is the correct discipline.** Substituting `"none"`
   for `"dispatcher_daemon"` as the happy-path fixture preserves coverage of the
   surrounding machinery; `test_dispatcher_daemon_rejects_missing_heartbeat`,
   whose subject is the readiness gate, is correctly converted rather than
   re-fixtured.
5. **PAUTH operation-time evaluation is `allowed`** for all four corrected
   paths (`source`, `test` mutation classes).
6. **Dead-code disclosure is sound.** `_probe_dispatcher_daemon_readiness`
   (`validation.py:196`) has exactly one caller — the branch being replaced —
   and is deliberately left for a follow-on hygiene item rather than removed
   beyond the approved design.

## Residual Risks (non-blocking)

- Re-enabling the legacy dispatcher later requires a fresh owner decision +
  reverting change (intended cost per `DELIB-20260807011938`).
- Dead code (`_probe_dispatcher_daemon_readiness`) left behind; disclosed for a
  follow-on hygiene item.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| DELIB-20260807011938 (SET-reject legacy) | `validate_bridge_substrate(...,"dispatcher_daemon",...)` returns failing result regardless of readiness | yes (proposed new case) | adequate |
| DELIB-20260807011938 (READ accepts) | reading existing `dispatcher_daemon` substrate succeeds | yes (proposed new case) | adequate |
| `"none"` remains selectable | existing coverage re-asserted | yes (existing) | adequate |
| Unknown values rejected distinctly | unknown diagnostic distinct from legacy rejection | yes (proposed new case) | adequate |
| GOV-FILE-BRIDGE-AUTHORITY-001 | numbered chain + preflights | yes | adequate |
| Baseline preserved | `python -m pytest <4-module cohort> -q` -> 28 passed | yes | adequate |

## Commands Executed

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6019-substrate-set-reject-permanence --content-file bridge/gtkb-wi6019-substrate-set-reject-permanence-003.md` -> preflight_passed true, blocking_errors []
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6019-substrate-set-reject-permanence` -> 0 blocking gaps, exit 0
3. `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py -q --tb=no` -> 28 passed
4. `git status --short` on the four target paths -> clean (baseline)
5. `grep -c "dispatcher_daemon"` on the two added modules -> 20 and 9
6. Source inspection of `validation.py` L224-236 -> readiness-probe branch confirmed

## Prior Deliberations

- `DELIB-20260807011938` — owner decision selecting mechanical SET-rejection (AUQ 2026-08-07).
- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` — the standing prohibition enforced mechanically.
- `DELIB-20260807011937` / `DELIB-20260807011940` — D3 purge scope; machine-readable enforcement out of purge scope.
- `DELIB-20260807011939` — owner standing directive: auditability second-class during the build.
- `WI-6014` — same-day registry deletion motivating mechanical enforcement.
- `DELIB-20260806011917` — purge before probative language; governs the positively-stated docstring.
- `DELIB-20260807011965` — prior LO GO verdict on this thread (`-002`).

## Owner Decisions / Input

- `DELIB-20260807011938` — owner selected "Mechanical block on re-selection" (2026-08-07).
- `DELIB-20260807011939` — auditability second-class during the build.
- Owner direction 2026-08-07, session `f9e95f49-...`: "operate autonomously."
- No new owner decision is solicited by this GO.

## Bridge Chain Canonicality

The canonical record is the numbered bridge file chain under `bridge/` for
`gtkb-wi6019-substrate-set-reject-permanence`. Versions are appended
monotonically and never rewritten or deleted; `-001`, `-002`, and `-003` remain
as filed and this `-004` supersedes `-003`'s proposal revision by approving it,
per `GOV-FILE-BRIDGE-AUTHORITY-001`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
