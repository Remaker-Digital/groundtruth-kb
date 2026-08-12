NO-GO
::init gtkb pb
::open build
author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: 019fec49-a8d0-7cb0-8dfc-0fcdf7d4bcad
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: independent Loyal Opposition review; transcript-defined ::init gtkb lo
author_metadata_source: transcript init keyword and Codex runtime session-envelope metadata
bridge_kind: lo_verdict

Document: gtkb-wi5950-strict-terminal-recovery
Version: 016
Date: 2026-08-11 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5950-strict-terminal-recovery-015.md

# Loyal Opposition Verification — WI-5950 strict-terminal recovery (NO-GO: finalization packet freshness)

## Verdict

**NO-GO** on terminal finalization of
`bridge/gtkb-wi5950-strict-terminal-recovery-015.md`.

The implementation, tests, PAUTH, clause, executability, and W0P-quarantine
checks are green. The one authorized atomic VERIFIED attempt nevertheless
failed closed before a durable commit because materializing transaction-local
v016 triggers an N+1-to-N+2 applicability-horizon self-invalidation in the
current preflight code. This NO-GO does not authorize an implementation,
finalizer, commit, registry change, W0P action, or dispatcher action.

## First-Line Role Eligibility And Review Independence

- Transcript-resolved role: `loyal-opposition` from `::init gtkb lo`; this
  role is authorized to issue `NO-GO`.
- Reviewer session context: `019fec49-a8d0-7cb0-8dfc-0fcdf7d4bcad`.
- Reviewed v015 author session context:
  `019fe34a-283e-77c1-b7b5-3e94242873e9`.
- The contexts differ. This is independent review, not self-review.

## Positive Confirmations

1. The complete v001–v015 chain was read. v015 remains the live REVISED
   implementation-report head, SHA-256
   `4c04cce357813ddc65411849199e827948978ac92ed20ee31891f94ed3c9b562`,
   16,784 bytes, consumed receipt row `2172`, revision
   `SOTREV-FCD9EE9465CE41EEAE21945EF30CFF97`, and null failure/compensation.
2. The exact two-target mechanics remain green: source
   `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` is
   SHA-256 `3f7a60311de62e312f3d627635788bc109b99f233664461f3c2c86953512105e`,
   `+218/-0`; the focused test is SHA-256
   `7c69b7c16a414794a693ee0e0129f8a6aaba3ba0360345a3280ece2d7d50ccdc`.
   Focused 6/6, registry-control-plane 61/61, and adjacent 5/5 tests passed;
   Ruff check/format, compilation, and target diff checks passed.
3. PAUTH V5 and its exact two-target packet
   `sha256:502868278bf7c94c6fe098febd5ec16f1b2d91883ab2fd14fa45dffb16a7d763`
   remain valid for the bounded lifecycle. Applicability, clause, and
   pre-verdict checks were green before the transaction.
4. Row 14277,
   `DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`,
   SHA-256 `fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`,
   remains controlling. W0P v008, its receipt, and commit `13c9f0f5032e1bcffb3cae60023e2ba20197e86d`
   are frozen quarantined non-closing evidence. Foreign registry currentness
   remains outside WI-5950 and gates only later W0P revalidation/ratification.

## Finding F1 (P0, blocking) — terminal finalization self-invalidates its applicability horizon

**Observation.** Before v016 exists, canonical `build_packet` over the exact
Responds-to v015 report produces the valid pre-materialization packet
`sha256:3adaebc30efd772d32ccfb922e262d20f1d2aa763bb68adbb65c7f18b09b0f01`.
During the authorized atomic attempt, a tentative v016 was materialized. The
old `scripts/bridge_applicability_preflight.py::_pauth_phase_cohort` combines
observed versions with the declared version and then appends `max(...)+1`.
Seeing v016 therefore incorrectly adds v017 to the finalization cohort and
the protected gate rederives
`sha256:027bfde0dd80dedad186599ba6a4775753a0373c905b91ea40091c53448b9864`.
Thus `027...` is a post-materialization, self-shifted N+1-to-N+2 expectation;
it is not a live-v015 packet and `3ada...` is not stale v015 evidence.

**Deficiency rationale.** No immutable terminal candidate can bind both the
valid pre-materialization v015 packet and the erroneous post-materialization
N+2 packet. Terminal finalization is mechanically impossible under the current
horizon code. The resulting focused-test authorization diagnostic is
consequential; it is not a new defect in the two-target implementation, test,
or PAUTH scope.

**Governed failure evidence.** Publication capability row `2173` is
compensated: capability
`sha256:488fc30bb09d0d3c9d06ea7c74a05f8f24b62fb37fe79ff6769a317c76cacdf2`,
temporary content digest
`sha256:ece80b48d2c3ebd50a5725d1ef586daef5b7b72369e92d82e8bd5e83060c618d`,
temporary result digest
`sha256:6e7059677843771300e9e4dac5186cf436097b71a38f9833ea90f06fb89d51c3`,
publication revision `SOTREV-3360B3D0AC474052BA04589CF87CB8F1`, and
compensation revision `SOTREV-60076C11023F408CB5E2E76A3ADA6B93` with digest
`sha256:c4e3410b8522a5fc7ca1ca2fa9aad7fce4dcc07c7d8e7b25cdf728b6639ce83c`.
The temporary file was removed; HEAD remains
`de467cbc93bbad9f8d826ffd9fa96733f76c504a` and no local commit was created.

## Required Revision

1. Do not cure this finding with a Prime Builder report restamp or a fixed
   `027...` binding. Stop WI-5950 terminal retries until a separately
   governed cycle-breaker corrects the WI-6140 exact-source-horizon defect.
2. Preserve the governing sequence without treating it as a waiver: row 14277
   requires WI-5950 terminal before WI-5953; WI-5953 repairs the receipt
   prerequisite for WI-6140; and WI-6140 owns this horizon correction. That
   WI-5950 → WI-5953 → WI-6140 dependency cycle is unresolved and blocks
   terminalization.
3. After the dependency is corrected, Prime Builder may append a fresh
   `REVISED` report against current evidence, followed by a new independent
   LO terminal review. Do not change the source, focused test, PAUTH, registry
   TOMLs, W0P state, database records, real index, or Git history merely to
   correct report evidence; do not reuse or retry compensated capability 2173.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- GOV-WORK-TREE-HYGIENE-001
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- DCL-SOT-REGISTRY-PROJECTION-PARITY-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-STANDING-BACKLOG-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001

## Spec-to-Test Mapping

| Specification | Verification | Executed | Result |
| --- | --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | role, claim, chain, row-2173 reconciliation | yes | correct fail-closed compensation |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | focused 6 + registry 61 + adjacent 5 | yes | 72 passed; horizon self-invalidation rejected terminal commit |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | PAUTH V5 and exact packet readback | yes | two-target implementation authority remains bounded |
| GOV-WORK-TREE-HYGIENE-001 | HEAD/index/source/test preservation readback | yes | source +218 hunk and foreign index state preserved |
| GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 | protected-commit gate record | yes | N+1-to-N+2 horizon shift blocked commit |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | row-2173 authoritative failure detail | yes | valid pre-materialization `3ada...` diverged from self-shifted `027...` |
| DCL-SOT-REGISTRY-PROJECTION-PARITY-001 | row-14277 foreign-boundary readback | yes | registry parity remains later W0P-only work |
| SPEC-AUQ-POLICY-ENGINE-001 | row-14277 deliberation readback | yes | unresolved WI-5950 → WI-5953 → WI-6140 sequence preserved |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | exact in-root paths | yes | root boundary maintained |
| GOV-STANDING-BACKLOG-001 | WI-5950 lifecycle review | yes | bounded work remains traceable |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | protected commit and parity evidence | yes | hook enforcement acted fail-closed |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | bridge/capability/compensation artifacts | yes | exact failure is durably recorded |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | v015 to NO-GO lifecycle transition | yes | append-only corrective report required |
| GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 | static and test matrix | yes | no implementation regression identified |

## Prior Deliberations

- `DELIB-20260810-W0P-SLICE-D-QUARANTINED-FORWARD-RECOVERY-AUTHORIZATION-001`
  (row 14277; SHA-256
  `fe2e247937e14445e608e39511ec237440a6e8abe3d7f4eeb70fc1c537bd9578`) —
  W0P quarantine and the bounded WI-5950-first sequence.
- `bridge/gtkb-wi5950-strict-terminal-recovery-014.md` — prior LO report
  evidence corrections accepted by v015.
- Publication capability row 2173 — compensated terminal-attempt evidence,
  not terminal closure.

## Applicability Preflight

- packet_hash: `sha256:3adaebc30efd772d32ccfb922e262d20f1d2aa763bb68adbb65c7f18b09b0f01`
- candidate_evidence_hash: `sha256:a0c20341864639aa91d630d81dcfdb1e787dd9f61e1173e11d098c5c2cc7d7ac`
- bridge_document_name: `gtkb-wi5950-strict-terminal-recovery`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
- applicability_path_evidence: ["bridge/gtkb-wi5950-strict-terminal-recovery-010.md`", "bridge/gtkb-wi5950-strict-terminal-recovery-011.md", "bridge/gtkb-wi5950-strict-terminal-recovery-011.md`", "bridge/gtkb-wi5950-strict-terminal-recovery-011.md`.", "bridge/gtkb-wi5950-strict-terminal-recovery-012.md", "bridge/gtkb-wi5950-strict-terminal-recovery-012.md`", "bridge/gtkb-wi5950-strict-terminal-recovery-012.md`.", "bridge/gtkb-wi5950-strict-terminal-recovery-013.md`", "bridge/gtkb-wi5950-strict-terminal-recovery-014.md", "bridge/gtkb-wi5950-strict-terminal-recovery-014.md`", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py`", "platform_tests/scripts/test_bridge_publication_preimage_scoping.py", "scripts/adr_dcl_clause_preflight.py", "scripts/bridge_applicability_preflight.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5950-strict-terminal-recovery-015.md`
- operative_file: `bridge/gtkb-wi5950-strict-terminal-recovery-015.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `finalization`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
- authorization_version: `5`
- project_id: `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`
- authorization_source: `bridge/gtkb-wi5950-strict-terminal-recovery-011.md`
- requested_operations: ["git_commit", "protected_mutation"]
- cohort: ["bridge/gtkb-wi5950-strict-terminal-recovery-001.md", "bridge/gtkb-wi5950-strict-terminal-recovery-002.md", "bridge/gtkb-wi5950-strict-terminal-recovery-003.md", "bridge/gtkb-wi5950-strict-terminal-recovery-004.md", "bridge/gtkb-wi5950-strict-terminal-recovery-005.md", "bridge/gtkb-wi5950-strict-terminal-recovery-006.md", "bridge/gtkb-wi5950-strict-terminal-recovery-007.md", "bridge/gtkb-wi5950-strict-terminal-recovery-008.md", "bridge/gtkb-wi5950-strict-terminal-recovery-009.md", "bridge/gtkb-wi5950-strict-terminal-recovery-010.md", "bridge/gtkb-wi5950-strict-terminal-recovery-011.md", "bridge/gtkb-wi5950-strict-terminal-recovery-012.md", "bridge/gtkb-wi5950-strict-terminal-recovery-013.md", "bridge/gtkb-wi5950-strict-terminal-recovery-014.md", "bridge/gtkb-wi5950-strict-terminal-recovery-015.md", "bridge/gtkb-wi5950-strict-terminal-recovery-016.md", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`
- taxonomy: v`2` `C0DA33114C9B3FD2B3DFD816043B458D8C0171143D014B79B812AA354F0EE450`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `git_commit` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `protected_mutation` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Boundary And Preservation

- The ordinary verdict claim was null before filing and must be released after
  publication.
- The real index SHA-256 remains
  `b8e7bb45f3526ebba4ff586879b4890706f95526a666f45f0083936110dc4791`.
  The two foreign staged registry TOMLs remain unmodified at index blob
  `d4a1aca0e15172acad63f218f32c9814b2055677`.
- No legacy TAFE dispatcher was queried, enabled, started, restarted,
  reconfigured, or used.

---

When you are finished working, close your session envelope by invoking ::wrap.
