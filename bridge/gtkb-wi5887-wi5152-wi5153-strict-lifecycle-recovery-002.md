GO
::init gtkb lo
::open test

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: db8acfd1-59c4-4849-ae05-dd5a57691aa4
author_model: Composer
author_model_version: Composer
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; NEW/NO-ACTION auto-process loop newest-to-oldest
author_metadata_source: session_envelope

bridge_kind: lo_verdict
Document: gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery
Version: 002
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery-001.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5887
Related Work Items: WI-5152, WI-5153, WI-5316, WI-5721, WI-5755, WI-5761, WI-5825, WI-5827, WI-5881, WI-5904
target_paths: ["groundtruth.db"]
implementation_scope: service_owned_strict_lifecycle_recovery_metadata
requires_review: false
requires_verification: true
kb_mutation_in_scope: true
git_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Loyal Opposition Verdict — WI-5887 WI-5152/WI-5153 Strict Lifecycle Recovery

## Verdict

**GO** for proposal v001. Fresh strict-valid controller recovery of the two
immutable legacy chains is the correct shape: preserve all 14 raw bytes,
recover WI-5153 historical provenance by reference, and keep WI-5152 open for
a separate current-map proposal. This GO does **not** authorize implementation
start until the non-waivable gates below clear.

## Findings

### P2 — Fourteen-file evidence manifest and heads revalidate

- **Claim:** Exact 14-line manifest aggregate and both physical heads match
  the proposal binding.
- **Evidence:** Live recompute — 0 line mismatches; aggregate SHA-256
  `726575F86615577ABCD39FABEF2FE06AF901936EFFBCD45CC9CB6E47AC7AB6E2`;
  WI-5152 v008 `NO-GO` SHA
  `F1BEB46F4515F4F350A5F3473FA4970A16D317A3C103AFB84903904F8C38E1EB`
  (1839 bytes, untracked); WI-5153 v006 `VERIFIED` SHA
  `148B3E7849BB58BEFF328DB65086692EAE47155FF8E512FF60C9D3B8270B6CAC`
  (15791 bytes); malformed v002 hashes match.
- **Impact:** Reservation tuple remains binding; drift would require REVISED.
- **Recommended action:** Recompute the full manifest immediately before any
  future reservation; fail closed on any path/byte/hash/status/Git-state drift.

### P2 — Dual disposition and nonimplementation boundary are correct

- **Claim:** WI-5153 by-reference historical binding and WI-5152
  evidence-only quarantine / open hold match live MemBase and filesystem
  state.
- **Evidence:** WI-5153 MemBase `resolved`/`resolved` while physical
  `VERIFIED` is strict-invalid at v002 (physical status ≠ terminal authority);
  WI-5152 remains `open`/`backlogged`; three implementation targets remain
  absent (`modernization-hard-invariants.toml`,
  `check_modernization_invariant_registry.py`,
  `test_modernization_invariant_registry.py`).
- **Impact:** Prevents false terminalization of WI-5152 and prevents
  treating physical WI-5153 `VERIFIED` as strict authority.
- **Recommended action:** Preserve the dual disposition; never append
  WI-5152 v009 or WI-5153 v007 under this controller.

### P1 — Generic dependency and project-lifecycle start gates remain open

- **Claim:** Implementation start is not yet authorized.
- **Evidence:** Live heads — WI-5881 v005 `REVISED` SHA
  `B36E0146371D91F8BA9C430DDBF61D2C0B7F055A7BA027B34F61273813C30569`;
  WI-5825 v006 `GO` SHA
  `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`;
  neither independently VERIFIED. Project
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is v3 `active` with stale
  `completed_at=2026-06-21T09:48:38Z` (same lifecycle contradiction gated on
  WI-5908 GO `-004` via WI-5761). WI-5887 has no registered incident test yet
  (proposal-declared future gate). Active membership confirmed:
  `project_work_item_memberships` v1 status=`active`.
- **Impact:** Starting now would invent recovery/receipt behavior and would
  ignore incomplete project-lifecycle authority.
- **Recommended action:** Hold claim/start until all Conditions clear; then
  re-read the immutable tuple and project record before mutation.

### P2 — Scope, PAUTH, and DISARM are coherent

- **Claim:** Single service-owned `groundtruth.db` cohort under Bridge
  Protocol Reliability PAUTH v2 is allowed; no legacy-file, Git, dispatcher,
  or WI-5152 target absorption.
- **Evidence:** Applicability `preflight_passed: true`; PAUTH
  `allowed=true` for packet/start operations; clause gate 0 blocking gaps;
  proposal DISARM forbids reservation/mutation until gates clear.
- **Impact:** Low design risk if only exact governed row cohorts mutate after
  gates.
- **Recommended action:** Enforce exact-row CAS, receipt single-consume, and
  zero legacy-byte change.

## Conditions (non-waivable)

1. No claim/start/reservation/capability/receipt/DB mutation until **WI-5881**
   and **WI-5825** are independently **VERIFIED**, receipt-complete, current,
   and clean on shared targets.
2. A governed WI-5887 incident-specific test is registered and phase-assigned
   before implementation claim/start.
3. **WI-5761** (or sole successor owning project-reactivation /
   `completed_at` clearance for
   `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`) reaches independently authored
   **VERIFIED**, **or** owner-evidenced reactivation clears the stale
   `completed_at` while status remains `active`, with MemBase evidence cited
   in the start claim. Live project must no longer present `active` + non-null
   `completed_at` (or an explicit owner-approved exception must exist — none
   today). Bridge-carrier `WITHDRAWN` on WI-5761 does not satisfy this gate.
4. Preserve all 14 legacy bytes/paths/Git identities; never append original
   slugs; never authorize the three absent WI-5152 targets from old GO /
   physical tails.
5. No dispatcher/TAFE activation, Git/index mutation, raw SQLite, whole-DB
   lock, credential/deploy/release/push, history rewrite, or destructive
   cleanup.

## First-Line Role Eligibility And Review Independence

PASS. Interactive session role is Loyal Opposition via `::init gtkb lo`.
Reviewer session `db8acfd1-59c4-4849-ae05-dd5a57691aa4` differs from proposal
author `019fbed5-8044-7c81-b03e-065d9a802210` (prime-builder/codex/A).

## Prior Deliberations

- WI-5904 / WI-5908 / WI-5898 / WI-5907 — fresh controller / invalid-terminal
  recovery family (design precedent; disjoint evidence).
- WI-5761 — project-reactivation invariant (open; WITHDRAWN carrier only).
- Proposal-cited DELIB-202667521 / DELIB-202667724 / DELIB-202667732 and
  WI-5755 stale-map ownership.

## Specs Reviewed

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-BRIDGE-HISTORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Commands Executed

1. NEW/NO-ACTION newest-by-mtime queue scan
2. Read proposal `-001.md`; verify 14-file manifest + aggregate SHA
3. Fresh head SHA/status probes for WI-5152/5153/5881/5825
4. `gt backlog show` for WI-5887/5152/5153/5881/5825; membership SQL;
   `gt projects show` for lifecycle contradiction
5. Applicability + clause preflights

## Applicability Preflight

- packet_hash: `sha256:6a48af85443e87a8aafb21001f81be3f8039b0a4c8c89b7eac07c9aff99965f4`
- candidate_evidence_hash: `sha256:0ee9e7494d98bdd78eef77cb2482b311802e2df01de372220d63b4f7c3debacd`
- bridge_document_name: `gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery`
- declared_target_paths: ["groundtruth.db"]
- applicability_path_evidence: ["bridge/gtkb-modernization-gate-1-25-execution-design-001.md`/`-002.md`", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-001.md`", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-001.md|12725|FD3CF44962785C6A3281B1CF84DC08A821C634CB1E10CF85EEE67DFE95082383|NEW|tracked|51d45b4a218dca284ab81bdd20e4a2096e2687aa", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md|6557|558F02EAB236F209FCA4D69DD830B482DAA93F44FD47850236BDCD5C1BFAA9C7|NO-GO|tracked|1b3440b566b35d378f150b4b3e35ddb52b5a8dff", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-003.md|15732|189B213E0300D841AE1F0443A072F9FD82EA123BB759846B7F3FA80960A1627E|REVISED|tracked|6e6cf1fa7a3cf3a806a08db9916c58fea981e903", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-004.md|17293|A8696CA6BBCF395A78252FC62462174B793F899095DBD451CD2E2240B433EF4F|NO-GO|tracked|19e6282d8b9a6f3fd62776922913c7f2797d939b", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-005.md|21233|282A3AECF147B883BDEB10AFA999F8F36615E0582EAF03C2AEDFD0D8EEF4ADD3|REVISED|tracked|ce9fc9efedd718fd7393dd947793077224eee5ca", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-006.md|5698|591F4FE8D8253C50F1588676537DE5C4D3DE5D9D560D7DCCA8E1CD3A21E31062|GO|tracked|50878367735e59b5f5ecdcc357384e9b7bc536b6", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-007.md|1060|CF63358230E5AA8906F5399D756E63BCD9CA2373DF029752EC1FCB3A277F18D1|NO-ACTION|tracked|f05334b73e416ce2850fcb8f69585085c4fc86b7", "bridge/gtkb-wi5152-modernization-hard-invariant-registry-008.md|1839|F1BEB46F4515F4F350A5F3473FA4970A16D317A3C103AFB84903904F8C38E1EB|NO-GO|untracked|-", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-001.md`", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-001.md|12148|0B9C9985D9B9C03505F16726ED5B3112A7B7F05CE7B4E9C58D1BDAAEA77CCBBF|NEW|tracked|b592585a61df2be3f0e2fd0619ea91269a9f76c0", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-002.md|6468|FF5BBBC2DBBE4937C3ED8FBA24570FB0DCC420634A6AC4B92FCBE1E6EB2521F3|NO-GO|tracked|8742b9cd496f9f1beb51f79a082a8e9d6f46ebdb", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-003.md|14409|E38F0B148834B931E762249A4610AE8727BA7AE6D9856C60279F56E8B1EA2BCA|REVISED|tracked|e1b2204f2cf20e7be0a783075e55fef2eafcab75", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-004.md|1812|78F2820215A47ABE4DE9480903DD7AC3A04AF73297CBEEDC1D8388AFC0719D63|GO|tracked|681794cf392deccad1e7f53a510dc4fa62fc659e", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-005.md`", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-005.md|11669|94E8A2E2E9F7A38C9F0E74BB4985DB84C1FF11B48FC91F8880A42169A7F08BE1|NEW|tracked|c3ba5bf4c8c1af6335f421e75d82eae68741d49a", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md`", "bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md|15791|148B3E7849BB58BEFF328DB65086692EAE47155FF8E512FF60C9D3B8270B6CAC|VERIFIED|tracked|fe7d5b91c74a59ef2347bd03487832a66277a314", "bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-006.md`", "bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-005.md`", "bridge/gtkb-wi5904-wi5316-strict-terminal-provenance-recovery-001.md`", "config/governance/modernization-hard-invariants.toml`", "groundtruth-kb/src/groundtruth_kb/assertions.py`", "groundtruth-kb/tests/test_assertions.py`", "groundtruth.db", "platform_tests/scripts/test_modernization_invariant_registry.py`", "scripts/check_modernization_invariant_registry.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery-001.md`
- operative_file: `bridge/gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery-001.md`
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
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth.db"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery`
- Operative file: `bridge\gtkb-wi5887-wi5152-wi5153-strict-lifecycle-recovery-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Mandatory Closing Checklist

- [x] Status token is `GO`
- [x] Responds to exact latest path `-001.md`
- [x] Session-context review independence preserved
- [x] Start gates include WI-5881, WI-5825, registered test, and WI-5761 lifecycle
- [x] No protected-file mutations in this verdict

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
