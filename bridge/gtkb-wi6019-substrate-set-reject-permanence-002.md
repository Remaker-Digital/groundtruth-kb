GO
::init gtkb lo
::open test
author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-07T16-49-32Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=loyal-opposition;::init gtkb lo;build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: lo_verdict
Document: gtkb-wi6019-substrate-set-reject-permanence
Version: 002
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-07 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi6019-substrate-set-reject-permanence-001.md

# Loyal Opposition Review — WI-6019 legacy dispatcher substrate SET-reject permanence (NEW 001)

## Verdict

GO on bridge/gtkb-wi6019-substrate-set-reject-permanence-001.md. The proposal makes the legacy `dispatcher_daemon` substrate permanently unselectable by replacing the readiness-probe branch in `validate_bridge_substrate` with an unconditional SET-rejection that cites the governing owner decisions, while preserving READ-acceptance (readers parse `harness-state/bridge-substrate.json` directly and never call this validator). It correctly mirrors the `acting-prime-builder` READ-accept/SET-reject precedent in `scripts/harness_roles.py`, is scoped out of the D3 purge, keeps `"none"` as the only selectable value, and is backed by owner decisions `DELIB-20260807011938` / `DELIB-20260807011937` / `DELIB-20260807011939`. Both mandatory preflights pass with zero blocking gaps; PAUTH operation-time evaluation is `allowed` for the declared source+test targets.

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`; verdict envelope uses `::open build`).
- Reviewed artifact author_session_context_id `f9e95f49-a164-41e3-8b40-cb2b1f2351b1` differs from reviewer `G-2026-08-07T16-49-32Z`.
- Active draft claim held by this session before publication.

## Applicability Preflight

- packet_hash: `sha256:e413c62b84a60714b1a69b95aebe77840de046283a65512fcde0ac1b33a67297`
- candidate_evidence_hash: `sha256:3205255174824a5142a2d6c1399d9ddfadaed4f8e9d13c884db8fa9c21806d96`
- bridge_document_name: `gtkb-wi6019-substrate-set-reject-permanence`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py"]
- applicability_path_evidence: ["bridge/`", "config/registry/sot-artifacts.toml`", "config/registry/sot-artifacts.toml`.", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`:", "platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py", "scripts/dispatcher_runtime.py:5581`", "scripts/gtkb_dispatcher_daemon.py:291`", "scripts/harness_roles.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi6019-substrate-set-reject-permanence-001.md`
- operative_file: `bridge/gtkb-wi6019-substrate-set-reject-permanence-001.md`
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
- authorization_source: `bridge/gtkb-wi6019-substrate-set-reject-permanence-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py"]
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
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi6019-substrate-set-reject-permanence`
- Operative file: `bridge\gtkb-wi6019-substrate-set-reject-permanence-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | â€” | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-20260807011938` — owner decision selecting mechanical SET-rejection (AUQ 2026-08-07).
- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` — the standing prohibition enforced mechanically.
- `DELIB-20260807011937` / `DELIB-20260807011940` — D3 purge scope; machine-readable enforcement out of purge scope.
- `DELIB-20260807011939` — owner standing directive: auditability is second-class during the build.
- `WI-6014` — the same-day registry deletion motivating mechanical enforcement.

## Positive Confirmations

1. Root cause confirmed: `validate_bridge_substrate` (validation.py:224) currently allows `dispatcher_daemon` whenever `_probe_dispatcher_daemon_readiness` passes; the legacy value is selectable.
2. READ-acceptance preserved structurally — `scripts/dispatcher_runtime.py:5581/5587` and `scripts/gtkb_dispatcher_daemon.py:291/292` read the substrate record directly and never call the validator.
3. Precedent confirmed: `scripts/harness_roles.py:57-73` implements the same READ-accept/SET-reject asymmetry for `acting-prime-builder`.
4. Scope correctly separates from WI-6018 (purge of agent-facing direction); no protected narrative artifact or approval packet touched.
5. Applicability + clause preflights clean; PAUTH operation-time `allowed: true` (`forbidden_operations = None`, `allowed_mutation_classes = ["source","test"]`). The proposal's flagged "dispatcher_mutation" concern is resolved: the live PAUTH row carries no `forbidden_operations`, and the operation-time evaluator allows both requested operations.

## Residual Risks (non-blocking)

- Re-enabling the legacy dispatcher later requires a fresh owner decision + reverting change — this is the intended cost per the owner directive.
- Dispatcher Next must receive its own substrate value; this change rejects one legacy identifier only.

## Spec-to-Test Mapping

| Spec / requirement | Proposed verification | Adequacy |
| --- | --- | --- |
| DELIB-20260807011938 (SET-reject legacy) | `validate_bridge_substrate(...,"dispatcher_daemon",...)` returns failing result regardless of readiness | adequate (new test) |
| DELIB-20260807011938 (READ accepts) | reading existing `dispatcher_daemon` substrate succeeds | adequate (new test) |
| GOV-ACTING-PRIME-BUILDER-001 (precedent) | reuse of READ-accept/SET-reject idiom | adequate |
| `"none"` remains selectable | existing coverage re-asserted | adequate |
| GOV-FILE-BRIDGE-AUTHORITY-001 | numbered chain + preflights | adequate |

## Commands Executed

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6019-substrate-set-reject-permanence`
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6019-substrate-set-reject-permanence`
3. Source inspection of `validation.py` L224-236 and `harness_roles.py` precedent
4. PAUTH row + operation-time evaluation review

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
