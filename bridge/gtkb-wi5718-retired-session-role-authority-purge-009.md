REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Prime Builder role; build automation
author_metadata_source: x-codex-turn-metadata

# WI-5718 Retired Session-Role Authority Operative-Reference Purge - Fifth Revision

bridge_kind: prime_proposal
Document: gtkb-wi5718-retired-session-role-authority-purge
Version: 009
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5718-retired-session-role-authority-purge-008.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5718-RETIRED-ROLE-AUTHORITY-PURGE-20260728
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5718

target_paths: [".claude/rules/operating-role.md", ".claude/rules/prime-builder-role.md", "AGENTS.md", "CLAUDE.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/declarative-agent-role-manifest.yaml", "config/agent-control/gtkb-declarative-agent-role-manifest.yaml", "config/agent-control/gtkb-lo-startup-overlay.md", "config/agent-control/gtkb-operating-role.md", "config/agent-control/gtkb-prime-builder-role.md", "config/agent-control/gtkb-system-interface-map.toml", "config/agent-control/system-interface-map.toml", "config/registry/sot-artifacts.toml", "dashboard/dashboard-data.json", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "platform_tests/scripts/test_antigravity_startup_overlay_integration.py", "platform_tests/scripts/test_dcl_role_resolution_authority_001.py", "platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py", "platform_tests/scripts/test_harness_role_protocol_smoke.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py", "platform_tests/scripts/test_lo_startup_text.py", "platform_tests/scripts/test_modernization_authority_foundations.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py", "platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "scripts/benchmarks/harness_role_protocol_smoke.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI5718-RETIRED-ROLE-AUTHORITY-PURGE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-AGENTS-MD.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-CLAUDE-MD.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-CLAUDE-RULES-OPERATING-ROLE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-CLAUDE-RULES-PRIME-BUILDER-ROLE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-DCL-ACTIVITY-CONTEXT-MANIFEST-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-DCL-SESSION-ROLE-RESOLUTION-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-GOV-HARNESS-ONBOARDING-CONTRACT-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-SPEC-DISPATCH-ENVELOPE-ELEMENT-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-DISPATCHER-BLACK-BOX-WI5353-IMPLEMENTATION-START-HARNESS-SELECTOR-20260716.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-DISPATCHER-BLACK-BOX-WI5427-DAEMON-GENERATION-HANDOFF-20260717.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-DISPATCHER-BLACK-BOX-WI5448-DEAD-DAEMON-LEASE-RESTART-20260717.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-FAB15-20260610.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PARALLEL-DISPATCH-REMEDIATION-SWEEP-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5179-HARNESS-DIAGNOSTIC-20260711.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5221-PRIME-WORKER-PROVENANCE-20260712.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5250-CODEX-A-READINESS-20260715.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5252-SESSION-ENVELOPE-PROVENANCE-20260715.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5255-BC-TELEMETRY-PROVENANCE-20260715.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5256-CODEX-SESSION-SUCCESSOR-20260715.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5259-VERDICT-ATTRIBUTION-20260715.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371-LO-FILE-SAFETY-GATE-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-AUTO-SPEC-INTAKE-A3CDEF-HARDENING-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-WI-5193-BRIDGE-AUTHORITY-20260711.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS-20260715-PROJECT-SCOPE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS-WI5266-RESOURCE-DISAMBIGUATION-20260715.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-20260715-PROJECT-SCOPE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4953-SCOPED-LO-REVERT-20260701.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5173-SHIM-TELEMETRY-20260710.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5189-DOCUMENT-CLAIM-AUTHORITY-20260711.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4764-BATCH-B-20260705.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4981-BATCH-B-20260705.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI5568-20260724.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001-WI-4362.json", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI-4668-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-ADR-DCL.json"]

implementation_scope: registry_configuration_documentation_governance_metadata_source_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: fix

KB Mutation: This proposal appends current specification, work-item, test,
project, and project-authorization versions through canonical governed
services. It also admits one proven load-bearing benchmark through the registry
control plane. `groundtruth.db` and both registry declaration projections are
therefore intentionally in `target_paths`. No direct SQL, schema change, row
deletion, identity deletion, or specification deletion is authorized.

## Structured Project Authorization Envelope

```json
{
  "project_id": "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS",
  "id": "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5718-RETIRED-ROLE-AUTHORITY-PURGE-20260728",
  "status": "active",
  "included_work_item_ids": ["WI-5718"],
  "included_spec_ids": [
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
    "GOV-ARTIFACT-APPROVAL-001",
    "GOV-PLATFORM-SOT-REGISTRY-001",
    "DCL-SOT-REGISTRY-PROJECTION-PARITY-001",
    "DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001",
    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
    "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
    "DCL-SESSION-ROLE-RESOLUTION-001",
    "DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001",
    "ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001"
  ],
  "allowed_mutation_classes": [
    "bridge",
    "configuration",
    "documentation",
    "governance_evidence",
    "metadata",
    "runtime_state",
    "source",
    "test"
  ],
  "forbidden_operations": [
    "credential_lifecycle",
    "destructive_cleanup",
    "dispatcher_mutation",
    "external_system_mutation",
    "git_history_rewrite",
    "git_push",
    "production_deployment",
    "release",
    "specification_deletion"
  ]
}
```

Owner evidence: .groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI5718-RETIRED-ROLE-AUTHORITY-PURGE.json

---

## Version 002 Finding Disposition

| Finding | Disposition in this revision |
| --- | --- |
| `FINDING-P0-001` | PARTIAL through version 005: it added the benchmark and control scan, but its tracked-file inventory remained incomplete. Version 007 closes the remainder with a fresh 61-file/111-occurrence index scan, exact disposition of all 16 residual files, and a registered-consumer reverse check. |
| `FINDING-P1-002` | Adds packets for both protected `.claude/rules/` files; protected narratives are now four and the complete packet inventory is 53. |
| `FINDING-P1-003` | Adds WI-5723 to the 19-row operative work-item amendment set while preserving its prior owner wording in immutable version history. |
| `FINDING-P1-004` | Replaces field-limited CLI searches with a five-table field-complete manifest; dispositions cover 11 active specs, 19 operative work items, 10 tests, one project, 37 active PAUTHs, and exact historical exceptions. |
| `FINDING-P2-005` | Records the complete executed baselines and brings the missing DCL assertion into the exact approved spec postimage. |
| `FINDING-P3-006` | Makes 25/43 registered-operative plus 1/1 tracked-benchmark scope authoritative; aggregate history counts are informational; quotes `missing_active_opaque_container` literally. |
| `FINDING-P3-007` | Corrects the deliberation statement: the record links to WI-5568, whose current scope assigns this purge to WI-5718. |

## Version 004 Finding Disposition

| Finding | Disposition in this revision |
| --- | --- |
| `FINDING-P0-001` | PARTIAL through version 005: it named three non-authoritative roots but omitted 16 tracked unregistered residuals. Version 007 replaces root-only inference with registry-authoritative classification, exact residual enumeration, and a registered-consumer admission check. |
| `FINDING-P1-002` | Preserves and names `WI-4291.related_spec_ids_at_creation` and `WI-4371.related_spec_ids_at_creation` in the exact audit-field allowlist. |
| `FINDING-P1-003` | Preserves and names `WI-5718.source_owner_directive`; the final allowlist is 17 exact row/field pairs across 17 rows. |
| `FINDING-P2-004` | States why the owner's all-active-references directive and WI-5718 PAUTH cover citation-only amendments to active PAUTH metadata across projects without authorizing those projects' implementation work. |
| `FINDING-P2-005` | Replaces all 37 ordinal packet filenames with filenames containing the complete PAUTH identifier. |
| `FINDING-P3-006` | Uses the canonical `## Prior Deliberations` heading. |
| `FINDING-P3-007` | Corrects the version-003 disposition above from closed to partial. |

## Version 006 Finding Disposition

| Finding | Disposition in this revision |
| --- | --- |
| `FINDING-P0-1` | Re-derived the complete tracked control from `git ls-files`: 61 files / 111 occurrences total, 42 / 82 outside the three previously named roots, and 16 / 38 outside both those roots and the transformation manifest. All 16 are listed exactly below. |
| `FINDING-P1-2` | Gives the nine `.gtkb-state` generator/body/audit files a distinct `unregistered_disposable_regeneration_hazard` disposition. They are not implementation inputs, may not support approval or regeneration, and are protected against semantic re-entry by exact postimage packets plus the current-record guard. |
| `FINDING-P2-3` | No new owner question is needed. `DELIB-202667220` is the durable direct owner decision to remove the identifier from all active references; the 37-ID manifest only executes that already-decided citation cleanup and does not authorize implementation for any sibling project. |
| `FINDING-P3-4` | The specification list now states explicitly that every cited version is the current amended-from preimage; implementation appends exactly one successor version. |

## Version 008 Finding Disposition

| Finding | Disposition in this revision |
| --- | --- |
| `F1` | Every appended `change_reason` and every amended `scope_summary` must describe the subject generically as the retired harness-scoped role-authority specification and cite `DELIB-202667220` without embedding the retired identifier. The existing allowlist is not widened. The field-complete five-table audit now runs against every drafted current-row postimage as a dry-run precondition before owner packet solicitation or any mutation, and runs again after append. |
| `F2` | Corrects the WI-5679 PAUTH disposition: its v2 `included_spec_ids` is already clean; only current `scope_summary` and `change_reason` contain the residual provenance wording. Its next version preserves that provenance generically, cites `DELIB-202667220`, and is exact-content packet approved. WI-5718 is sequenced as the first writer; if WI-5679 changes the shared row or either pinned baseline module first, WI-5718 stops, re-derives all affected postimages and counts, refreshes the exact packet, and returns to review on any changed acceptance postimage. |
| `N1` | The cross-thread rule explicitly covers both the shared PAUTH row and the two WI-5679-owned baseline modules. |
| `N2` | The verification section now states that eight of ten touched test modules carry documentation/comment/fixture parity changes rather than independent behavioral coverage; the retirement guard is the substantive new behavior, and all unrelated pre-existing guard assertions remain mandatory. |
| `N3` | Operative provenance citations are superseded, not erased: rewritten prose identifies the retired authority generically as historical, names the surviving successor constraint, and cites the retirement decision without reintroducing the literal identifier. |
| `N4` | Carried as the same non-blocking owner-visible reservation; no new owner-channel claim is made. |

## Claim

The owner has retired `GOV-SESSION-ROLE-AUTHORITY-001` because its
harness-scoped worker-role framing is defective. The formal record is already
version 6 with status `retired`; prior versions and canonical audit trails are
immutable. The remaining work is to remove the retired identifier and any
claim that depends solely on it from every operative registered surface while
preserving current exact-session and dispatched-worker role requirements under
their surviving DCL/ADR authorities.

This is a deterministic decontamination, not an agent-driven recursive
find/replace. Registered file occurrences come from one coherent registry
generation and are preimage-counted. A tracked-file control scan closes the
registry-admission gap identified in version 002. Current MemBase coverage is
field-complete across specifications, work items, tests, projects, and project
authorizations; it is not inferred from title/description search helpers.
Implementation must abort before mutation if the operative classes, exact IDs,
preimages, or active-record fields differ from the approved manifest.

Every new append `change_reason` and every amended `scope_summary` follows one
recursive-reference discipline: refer generically to the retired harness-scoped
role-authority specification, cite `DELIB-202667220`, and never reproduce its
literal identifier. This applies to all specification, work-item, test, project,
and project-authorization postimages, including the WI-5679 PAUTH. It is not an
allowlist expansion. Drafted postimages are scanned field-completely before any
owner packet is solicited and before any mutation, preventing the cleanup
transaction from reintroducing its own target literal.

## Retirement Rationale

Worker role authority belongs to one exact interactive session context or one
explicitly composed dispatched-worker packet. A harness has durable identity,
capabilities, and dispatch eligibility; it does not own one shared operating
role for every concurrent worker using that harness. Keeping the retired GOV in
startup text, manifests, tests, or current specifications would continue to
teach and enforce the defective model after formal retirement.

This purge does not introduce file permissions, provenance requirements for
ordinary editor saves, or content-invalidating audit gates. Owner hand edits
remain valid without notation. Missing attribution or content-observation
evidence remains a warn-and-repair condition, not a reason to reject correct
content or stop useful work.

## Current Deterministic Inventory

The canonical command
`gt admin inventory scan-strings --match GOV-SESSION-ROLE-AUTHORITY-001 --report-only --json`
was re-run after version 002 on 2026-07-28 against 2,348 registry records and
16,929 expanded registered files. It found 1,142 hits across 641 unique paths.

| Classification | Unique paths | Hits | Disposition |
| --- | ---: | ---: | --- |
| `bridge/**` | dynamic | dynamic | Immutable numbered audit history; preserve |
| `.groundtruth/formal-artifact-approvals/**` | dynamic | dynamic | Immutable approval evidence; preserve |
| `memory/pending-owner-decisions.md` | 1 | 7 | Canonical historical owner-decision audit input; preserve |
| Operative/generated registered surfaces | 25 | 43 | Exact implementation manifest below |

The scanner literally reports `groundtruth.db` as
`missing_active_opaque_container`; WI-5703 owns that known opaque-file
classification defect. That false-missing row is disclosed and is not accepted
as MemBase coverage. A read-only field-complete current-row audit found 13
specifications, 33 work items, 10 tests, one project, and 38 project
authorizations. The explicit dispositions below distinguish operative current
fields from retired identities and append-only audit fields.

A tracked-file control scan found one additional load-bearing operative source,
`scripts/benchmarks/harness_role_protocol_smoke.py`, SHA-256
`abb31f284f787f8dccd1ca2235d4ed47b19259af89e5251044e71f856313108e`,
with one occurrence. It is imported by `scripts/benchmarks/cli.py`,
`scripts/collect_modernization_semantic_evidence.py`, and the registered
benchmark test. It has no registry record. The implementation therefore admits
it atomically before transforming it.

The complete index-based tracked control finds 61 files / 111 occurrences after
excluding `bridge/**` and `.groundtruth/formal-artifact-approvals/**`. The exact
partition is 26 transformation files / 44 occurrences, 19 files / 29
occurrences under the three previously named non-authoritative roots, and 16
tracked unregistered files / 38 occurrences outside both groups. Equivalently,
42 files / 82 occurrences lie outside the three previously named roots. These
figures were re-derived from `git ls-files`; no filesystem walk or remembered
count supplies them.

The 19-file / 29-occurrence root-based class remains:

- `memory/**` is harness-local scratch/archive content and non-authoritative by
  the project-root boundary contract.
- `RETIRED-*/**` contains explicitly retired report archives.
- `BARRED*/**` contains explicitly barred report archives.

The remaining 16 files are also absent from the canonical registry and are
therefore disposable under `GOV-PLATFORM-SOT-REGISTRY-001`. They are enumerated
exactly instead of being hidden behind a broad directory exclusion:

| Class | Files / hits | Exact paths and disposition |
| --- | ---: | --- |
| Historical verdict-helper drafts | 7 / 17 | `.claude/skills/gtkb-verify/helpers/draft-gtkb-wi5069-body.md`; `.claude/skills/gtkb-verify/helpers/draft-verdict-5171.md`; `.claude/skills/gtkb-verify/helpers/final-verdict-5171.md`; `.codex/skills/gtkb-verify/helpers/final-verdict-5171.md`; `.goose/skills/gtkb-verify/helpers/draft-gtkb-wi5069-body.md`; `.goose/skills/gtkb-verify/helpers/draft-verdict-5171.md`; `.goose/skills/gtkb-verify/helpers/final-verdict-5171.md`. Classification: `unregistered_disposable_historical_draft`; never a current bridge or verdict authority. |
| Superseded packet/body generators | 8 / 10 | `.gtkb-state/family-2-bodies/DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001-v3.diff`; `.gtkb-state/family-2-bodies/DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001-v3.md`; `.gtkb-state/family-2-bodies/SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001-v3.diff`; `.gtkb-state/family-2-bodies/SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001-v3.md`; `.gtkb-state/family-3-bodies/DCL-SESSION-ROLE-RESOLUTION-001-v2.diff`; `.gtkb-state/family-3-bodies/DCL-SESSION-ROLE-RESOLUTION-001-v2.md`; `.gtkb-state/generate-family-2-packets.py`; `.gtkb-state/generate-family-3-packets.py`. Classification: `unregistered_disposable_regeneration_hazard`; superseded one-shot inputs that MUST NOT be executed, cited as approval evidence, or used to regenerate a current specification. |
| Superseded audit output | 1 / 11 | `.gtkb-state/role-authority-audit/wi4782-session-role-authority-audit.json`. Classification: `unregistered_disposable_historical_output`; historical bridge records preserve the audit trail, and this JSON is not current authority. |

A deterministic reverse check read 2,329 existing registered text artifacts
from the same 2,348-record registry projection, excluding immutable bridge and
approval trails plus the opaque database container. It found zero references
to any of those 16 exact files or their generator directories. The 16 are not
implementation targets, are not corrected or admitted, and remain eligible for
the registry-authoritative hygiene sweep. Their current presence does not make
them load-bearing.

A broader check over all 34 unregistered non-manifest token-bearing files found
three path-string references, all in registered classification tests: two name
`memory/CLAUDE_ARCHIVE.md`, and one names
`memory/fable-investigation-campaign.md`. Those tests assert legacy
quarantine/preserve/strip classifications; they do not read the retired role
identifier from either file or use either file as current role authority. The
registered-test versus unregistered-anchor contradiction is registry-admission
debt for WI-5696, not a reason to elevate either memory file in WI-5718.

The tracked control is diagnostic and cannot confer authority. After the
benchmark admission, the exact named-root classes and exact 16-file residual
set are reported without acquiring authority. A new tracked-unregistered hit
outside those disclosed classes triggers a reverse-dependency classification;
a proven load-bearing consumer requires registry admission before
transformation, while a disposable result warns without blocking useful work.
The two generator scripts and six staged bodies additionally receive the
explicit regeneration-hazard label. Exact owner-approved specification
postimages cannot be derived from them, and the current-record zero-reference
guard rejects any later attempt to reinsert their retired citation into
MemBase.

The proposal and its approval packets add allowed historical occurrences; no
fixed post-filing aggregate total is authoritative. Revalidation aborts on
drift in the operative registered class (25 paths / 43 hits), the tracked
benchmark (one path / one hit), their preimage hashes, the exact current-row
manifest, or a newly proven load-bearing dependency absent from the registry.
Growth confined to immutable history or unregistered-disposable residue is
reported but does not invalidate the operative migration set.

## Exact File Transformation Manifest

These 25 paths remain the complete non-audit set from the registry-backed scan.
Together with the tracked benchmark, the file-transform set is exactly 26 paths
and 44 literal occurrences. Implementation must create an explicit
machine-readable map containing each path, expected preimage SHA-256, expected
occurrence count, and exact replacement operation. It must validate all 26
preimages and 44 occurrences before any write. Any operative missing, added,
changed, or duplicate occurrence aborts the entire file phase.

Where an occurrence is provenance rather than operative authority, the
postimage supersedes rather than erases it: it identifies the retired authority
generically as historical, names the surviving DCL/ADR successor, and cites
`DELIB-202667220` without the retired literal. This rule applies in particular
to the canonical-terminology Source citation.

| Count | Path | Transformation class |
| ---: | --- | --- |
| 1 | `.claude/rules/operating-role.md` | Remove retired authority citation; retain exact-session role authorities; formal packet required |
| 1 | `.claude/rules/prime-builder-role.md` | Same; formal packet required |
| 1 | `AGENTS.md` | Remove retired citation from active operating-role guidance; formal packet required |
| 2 | `CLAUDE.md` | Remove active citation and retired-spec inventory row; formal packet required |
| 1 | `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` | Remove retired startup authority |
| 1 | `config/agent-control/declarative-agent-role-manifest.yaml` | Remove retired spec list item |
| 1 | `config/agent-control/gtkb-declarative-agent-role-manifest.yaml` | Apply identical retained-destination correction |
| 1 | `config/agent-control/gtkb-lo-startup-overlay.md` | Apply identical retained-destination correction |
| 1 | `config/agent-control/gtkb-operating-role.md` | Apply identical retained-destination correction |
| 1 | `config/agent-control/gtkb-prime-builder-role.md` | Apply identical retained-destination correction |
| 2 | `config/agent-control/gtkb-system-interface-map.toml` | Remove retired related-spec entries while preserving valid TOML arrays |
| 2 | `config/agent-control/system-interface-map.toml` | Same canonical retained-source correction |
| 1 | `dashboard/dashboard-data.json` | Replace stale current-projection text from corrected MemBase records; preserve valid JSON |
| 1 | `groundtruth-kb/docs/reference/canonical-terminology-detail.md` | Replace retired source citation with surviving exact-session authorities |
| 2 | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml` | Regenerate/correct packaged map projection from canonical source |
| 1 | `platform_tests/scripts/test_antigravity_startup_overlay_integration.py` | Replace retired authority comment with current DCL/ADR authority |
| 9 | `platform_tests/scripts/test_dcl_role_resolution_authority_001.py` | Remove obsolete GOV-presence test; add retirement and zero-operative-reference guard without embedding the full literal |
| 3 | `platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py` | Replace obsolete citations and harness-role wording with dispatch-packet/session wording |
| 3 | `platform_tests/scripts/test_harness_role_protocol_smoke.py` | Replace fixture authority text while preserving behavioral expectations |
| 2 | `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py` | Replace retired citations with exact-session resolution authority |
| 1 | `platform_tests/scripts/test_lo_startup_text.py` | Replace retired startup authority citation |
| 1 | `platform_tests/scripts/test_modernization_authority_foundations.py` | Replace retired required-spec fixture with current authority set |
| 2 | `platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py` | Replace retired citation and durable-harness-role wording with dispatched-packet authority |
| 1 | `platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py` | Replace retired citation |
| 1 | `platform_tests/scripts/test_work_intent_role_eligibility.py` | Replace retired citation with exact-session claim authority |
| 1 | `scripts/benchmarks/harness_role_protocol_smoke.py` | Replace the retired required token with surviving DCL/ADR exact-session authority; retain `transcript-defined` and `dispatcher role` probes |

The paired source/destination files retained for WI-5640 are all registered and
remain temporarily load-bearing. Both sides must receive equivalent semantic
corrections. This proposal does not delete, move, rename, or un-register either
side.

## Targeted Registry Admission

Before transforming the benchmark, `gt registry register --batch-file` admits
exactly one active `control_surface` / `coverage_mode = "exact"` record for
`scripts/benchmarks/harness_role_protocol_smoke.py`, matching adjacent benchmark
records: git-tracked versioning and backup, `git_restore`, shared owner role,
and the canonical governed-edit / ordinary-owner-edit mutation contract. The
registration advances `config/registry/sot-artifacts.toml`, its packaged mirror,
and the MemBase projection as one registry-control-plane transaction. Duplicate
path or identity, generation drift, or parity failure aborts before source
transformation. This targeted admission closes FINDING-P0-001 without claiming
that general admission work in WI-5696 is complete.

## Current Specification Amendments

Eleven active `specified` records contain the identifier. Each receives exactly
one append-only version through `gt spec update`, preserving status and
unrelated fields. Exact postimage content must be validated by its named formal
approval packet before insertion. Every version number below is the current
**amended-from preimage** version; implementation appends exactly one successor
version and does not rewrite the cited version.

1. `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (amended from v2): remove the retired Authority
   bullet; retain the persistence DCL and bridge-verdict provenance.
2. `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` (amended from v1): remove the retired GOV
   from the read-together sentence; retain current DCL and ADR authorities.
3. `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` (amended from v1): replace the false
   statement that the retired GOV remains the governance boundary with the
   current exact-session persistence authorities.
4. `DCL-ACTIVITY-CONTEXT-MANIFEST-001` (amended from v1): remove the retired `affected_by`
   link while preserving activity/context separation.
5. `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (amended from v3): remove the retired GOV from
   its authority list; retain init syntax and deterministic resolution links.
6. `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` (amended from v1): remove the retired GOV from
   the relationship paragraph and preserve warn-not-override semantics.
7. `DCL-SESSION-ROLE-RESOLUTION-001` (amended from v6): remove the retired authority bullet and
   its `affected_by` entry; preserve the exact session/dispatched packet table;
   add the missing
   `assertion_registry_not_authority_for_enforcement_gates` description and
   structured assertion required by the current enforcement-split test.
8. `GOV-HARNESS-ONBOARDING-CONTRACT-001` (amended from v1): remove the retired GOV from the
   related-artifact list; preserve identity/capability/dispatch eligibility.
9. `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (amended from v3): remove the retired GOV from its
   authority list; preserve current syntax and resolution links.
10. `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` (amended from v1): replace the retired parenthetical
   with surviving dispatched-packet/session-separation authority.
11. `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` (amended from v1):
    remove the retired `affected_by` link; preserve exact-document claim
    authority.

The current retired identity record itself and retired
`ADR-ROLE-STATUS-ORTHOGONALITY-001` v3 are preserved as inactive history and
explicitly allowed by the field-complete guard. No specification is deleted,
status-promoted, or semantically weakened. Prior versions remain immutable.

## Current Work-Item Projection Amendments

The field-complete audit found 33 current rows. Nineteen contain the identifier
in operative descriptive or authority-link fields and receive one append-only
version through `gt backlog update`; stage and resolution status remain
unchanged.

- `WI-3479`, `WI-4291`, `WI-4296`, `WI-4371`, `WI-4663`, `WI-4764`, and
  `WI-4784`: replace obsolete current descriptive/linkage text with surviving
  role-resolution authorities while preserving the prior version as history.
- `WI-4781`: replace the current title, description, and `source_spec_id`
  reference with a historical-retirement description linked to
  `DCL-SESSION-ROLE-RESOLUTION-001`; retain resolved lifecycle.
- `WI-5150` and `WI-5171`: replace current `source_spec_id` and descriptive
  references with current DCL/ADR authorities; retain resolved lifecycle.
- `WI-5221`, `WI-5252`, `WI-5281`, `WI-5353`, `WI-5377`, `WI-5580`, and
  `WI-5601`: replace the retired `source_spec_id` with the closest surviving
  exact-session, init-keyword, or dispatch-envelope authority without changing
  work-item lifecycle.
- `WI-5723`: replace the active description's literal with an equivalent
  generic reference to the retired harness-scoped authority; the prior owner
  wording remains immutable in version history.
- `WI-5718`: after verified implementation evidence is ready, update its title,
  description, and status detail to cite `DELIB-202667220` and the generic
  retired record without reintroducing the identifier. Its
  `source_owner_directive` remains immutable owner-audit evidence. WI-5718 stays
  open until terminal VERIFIED and canonical resolution.

Fourteen audit-only current rows carry the identifier in immutable fields and
are preserved: `WI-3453`, `WI-3458`, `WI-3470`, `WI-3474`, `WI-4375`,
`WI-4376`, `WI-4381`, `WI-4382`, `WI-4390`, `WI-4668`, `WI-4953`, `WI-5010`,
and `WI-5189` in `related_spec_ids_at_creation`, plus `WI-5256` in
`change_reason`. Three operative rows also preserve one immutable audit field
while their active prose is amended: `WI-4291.related_spec_ids_at_creation`,
`WI-4371.related_spec_ids_at_creation`, and
`WI-5718.source_owner_directive`. The guard therefore names 17 exact
row/field pairs across 17 rows; no broad field exemption is accepted. The
update service preserves every unspecified field. Direct SQL and bulk status
mutation are forbidden.

## Current Test, Project, And Authorization Amendments

Nine current test records are actively linked to the retired spec and are
relinked through the canonical test-artifact service:

- `TEST-11319`, `TEST-11474`, and `TEST-11627` ->
  `DCL-SESSION-ROLE-RESOLUTION-001`.
- `TEST-11375`, `TEST-11436`, and `TEST-11492` ->
  `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`.
- `TEST-11406` -> `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`.
- `TEST-11411` ->
  `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001`.
- `TEST-11650` -> `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`.

`TEST-11737` already links to the surviving DCL; only its expected-outcome
literal is replaced with the generic retired-record description. No test ID or
historical version is deleted.

The active project `PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE` receives
one append-only scope-note update using the generic retired-record description.
Its eventual retirement remains a program closeout action, not part of this
implementation.

The current authorization audit found 38 rows: 37 active and one completed.
The complete current field distribution is 35 `included_spec_ids`-only rows,
one `included_spec_ids` plus `allowed_mutation_classes` row, one
`included_spec_ids` plus `scope_summary` row, and one `scope_summary` plus
`change_reason`-only row.
Thirty-six active rows receive one exact owner-approved append-only amendment
that removes the retired identifier from `included_spec_ids` and, where
present, from `scope_summary`, `change_reason`, or
`allowed_mutation_classes`. The WI-5679 authorization is the named exception:
its current v2 `included_spec_ids` is already clean, while current
`scope_summary` and `change_reason` contain the identifier solely as removal
provenance. Its next postimage preserves the sibling project's approved
provenance generically, cites `DELIB-202667220`, and contains no retired
literal. The historical v2 sentence remains immutable. This citation-only
metadata repair is authorized by the WI-5718 PAUTH's metadata and governance-
evidence classes plus the exact owner-approved WI-5679 postimage packet; it does
not alter WI-5679 implementation scope or authority. Replacement spec IDs must
already be included and may not widen work items, targets, mutation classes, or
operations. Status remains active. The completed Ollama authorization is
immutable historical evidence and is the sole inactive PAUTH allowlist entry.

The 37 active IDs, in deterministic packet order, are:

1. `PAUTH-DISPATCHER-BLACK-BOX-WI5353-IMPLEMENTATION-START-HARNESS-SELECTOR-20260716`
2. `PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717`
3. `PAUTH-DISPATCHER-BLACK-BOX-WI5427-DAEMON-GENERATION-HANDOFF-20260717`
4. `PAUTH-DISPATCHER-BLACK-BOX-WI5448-DEAD-DAEMON-LEASE-RESTART-20260717`
5. `PAUTH-FAB15-20260610`
6. `PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702`
7. `PAUTH-PARALLEL-DISPATCH-REMEDIATION-SWEEP-001`
8. `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`
9. `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724`
10. `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5179-HARNESS-DIAGNOSTIC-20260711`
11. `PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297`
12. `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5221-PRIME-WORKER-PROVENANCE-20260712`
13. `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5250-CODEX-A-READINESS-20260715`
14. `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5252-SESSION-ENVELOPE-PROVENANCE-20260715`
15. `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5255-BC-TELEMETRY-PROVENANCE-20260715`
16. `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5256-CODEX-SESSION-SUCCESSOR-20260715`
17. `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5259-VERDICT-ATTRIBUTION-20260715`
18. `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
19. `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-HYGIENE-BACKFILL-001`
20. `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371-LO-FILE-SAFETY-GATE-001`
21. `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-AUTO-SPEC-INTAKE-A3CDEF-HARDENING-001`
22. `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-WI-5193-BRIDGE-AUTHORITY-20260711`
23. `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS-20260715-PROJECT-SCOPE`
24. `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS-WI5266-RESOURCE-DISAMBIGUATION-20260715`
25. `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE`
26. `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE`
27. `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-20260715-PROJECT-SCOPE`
28. `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001`
29. `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4953-SCOPED-LO-REVERT-20260701`
30. `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4982-INIT-KEYWORD-GRAMMAR-20260707`
31. `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5173-SHIM-TELEMETRY-20260710`
32. `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5189-DOCUMENT-CLAIM-AUTHORITY-20260711`
33. `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4764-BATCH-B-20260705`
34. `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4981-BATCH-B-20260705`
35. `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI5568-20260724`
36. `PAUTH-PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001-WI-4362`
37. `PAUTH-WI-4668-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-ADR-DCL`

Each packet filename embeds the complete PAUTH identifier from this list; no
ordinal mapping is used. The exact 37 postimages must be owner-presented and
packet-validated before mutation. The direct owner
instruction in `DELIB-202667220` says to remove all active references, so this
revision keeps the active PAUTH class in WI-5718 rather than deferring it to a
sibling and leaving the purge knowingly incomplete.

## Executable Zero-Reference Guard

`platform_tests/scripts/test_dcl_role_resolution_authority_001.py` will replace
the obsolete test that requires the old GOV body with a retirement guard that:

1. Constructs the retired identifier from non-contiguous constants so the test
   does not create a new literal scanner hit.
2. Confirms the current spec is version 6 or later and `retired`.
3. Calls the canonical registry-backed inventory scanner and rejects every
   operative registered hit outside `bridge/**`, formal approval packets, and
   the exact pending-owner-decision audit path.
4. Runs an index-based tracked-file control scan and reports its complete
   partition. For each tracked-unregistered hit, it checks the canonical
   registry rather than inferring authority from tracking alone. The exact
   named-root and 16-file classes are enumerated with their disclosed
   dispositions. Any new outside-class hit receives a reverse-dependency
   classification: proven load-bearing use fails with an admission requirement;
   a disposable result warns and does not become authority. The exact eight
   packet/body files above are additionally labeled
   `unregistered_disposable_regeneration_hazard`, may not supply an approved
   postimage, and are covered by the current-record re-entry guard.
5. Audits every surfaced field of current specification, work-item, test,
   project, and project-authorization rows. It rejects every non-allowlisted
   hit and permits only the exact retired identities, completed authorization,
   and the 17 named immutable audit row/field pairs above.
   The same audit is executed first against the complete drafted postimage set
   before owner packet solicitation and then against live current rows after
   append. It explicitly rejects any literal recurrence in a new
   `change_reason` or amended `scope_summary`.
6. Treats opaque-container file-scan coverage separately from current MemBase
   record coverage rather than declaring an unread binary container clean.
7. Executes the benchmark probe against current DCL/ADR tokens and proves its
   registered source and test fixture remain aligned.

The guard protects semantics, not file permissions. It emits a clear list of
operative regressions; it does not require special notation for owner edits.

## In-Root Placement Evidence

Every target is under `E:/GT-KB`. The original 25 transform files resolve
through one coherent registry snapshot; the 26th is the proven load-bearing
benchmark admitted by this transaction. Both declaration files, the database,
and every approval packet are governed in-root authorities. No external file,
scratchpad, transcript, cloud path, or non-root dependency is used as
implementation authority.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` - surviving deterministic exact-session and dispatched-worker resolution authority.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - exact interactive-session persistence authority.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - owner-approved separation of interactive session role from dispatcher metadata.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO, exact claim, report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds implementation to the WI-5718-only PAUTH.
- `GOV-ARTIFACT-APPROVAL-001` - requires exact-content packets for AGENTS/CLAUDE narrative changes.
- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - requires exact postimage approval for all eleven specification versions.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the registered artifact inventory authoritative.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - governs the targeted benchmark admission transaction.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` - constrains the admitted record's exact schema.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - requires coherent declaration/projection reads during scanning and observation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - governs the PAUTH/project/WI triple.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete current specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-to-test evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserves append-only versions and post-VERIFIED WI resolution.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves durable owner decision, proposal, report, and verdict artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the exact transformation and recovery artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires all implementation and evidence inside the project root.
- `GOV-WORK-TREE-HYGIENE-001` - requires scoped mutation/finalization without unrelated worktree absorption.

## Prior Deliberations

- `DELIB-202667220` - controlling owner decision to retire the defective
  harness-scoped GOV, purge every active reference, preserve immutable audit
  trails, and prove zero operative references mechanically. Its record remains
  linked to WI-5568; WI-5568 explicitly assigns execution of this purge to
  WI-5718. No stronger direct-link claim is made.
- `DELIB-20260710-GTKB-INTERACTIVE-KB-ATTRIBUTION-GLOBAL-MARKER-COLLISION` -
  evidence that shared harness state can misattribute another session.
- `DELIB-20263212` - owner requirement for interactive context continuity.
- `DELIB-202667477` - owner-selected WI-5679 continuity and strict
  transcript-only inheritance design; implementation remains in its own thread.
- `.gtkb-state/bridge-propose-drafts/gtkb-wi5568-retired-role-authority-reference-purge-001.md`
  - superseded non-dispatchable draft used only as investigation evidence;
  WI-5568 explicitly assigns this purge to WI-5718.

## Owner Decisions / Input

`DELIB-202667220` contains the owner's direct decision and exact boundary:
retire the version-5 harness-scoped authority, remove it from all active
references, preserve immutable history, replace worker-role authority with
exact session context/dispatched packet authority, and prove the result with a
deterministic scan. It does not claim an AskUserQuestion UI event; this proposal
relies on the substantive direct transcript decision and makes no stronger
channel-provenance claim.

The active WI-specific authorization is
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5718-RETIRED-ROLE-AUTHORITY-PURGE-20260728`.
It allows only WI-5718's bridge, configuration, documentation, governance
evidence, metadata, runtime projection, source, and test classes. It permits one
bounded local terminal commit and forbids credential, destructive, dispatcher,
external-system, history-rewrite, push, deployment, release, and specification
deletion operations.

The 37 active PAUTH amendments are inside that WI-5718 project scope even when
an authorization row belongs to another project. They are not implementation
work for those projects and do not consume or widen their authority. Each is a
citation-only metadata correction required by `DELIB-202667220`'s explicit
instruction to remove the retired identifier from every active reference. The
WI-5718 PAUTH authorizes metadata and governance-evidence mutation for this
retired-authority purge; the exact 37-ID manifest, exact postimage packets,
no-widening rule, and independent bridge GO further bound the operation. No
source, test, configuration, deployment, or work-item scope belonging to those
other projects is authorized through this interpretation.

No new sequencing decision is required. The owner's direct instruction in
`DELIB-202667220` expressly requires removal from every active reference, so
the 37 citation-only active PAUTH amendments remain in this WI rather than
being deferred while active authority envelopes stay dirty. This is the
recorded answer to the version-004 scope question; it does not rely on an
inferred permission or a cross-project implementation entitlement.

The WI-5679 row is governed as a named shared-row exception, not as an ordinary
included-spec cleanup. Its fresh exact postimage packet remains
`.groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI5679-REMOVE-RETIRED-GOV.json`.
That packet must be regenerated and owner-approved against the current row
before mutation, preserving the sibling project's provenance generically while
removing the retired literal from current `scope_summary` and
`change_reason`. WI-5718 is the first writer because WI-5679 is currently
`NO-ACTION` v013 and has no implementation authority. If WI-5679 advances the
row or either pinned baseline module first, WI-5718 stops, re-derives, refreshes
the packet, and returns to review on any changed acceptance postimage.

The owner supplied that decision directly in the conversation and it was
captured durably; an additional UI-specific question would duplicate rather
than clarify the decision. This revision treats owner intent as content, not as
a requirement for a particular interaction notation. Exact-content packet
approval remains separately required for every PAUTH postimage.

Exact content for 52 formal postimages must still be owner-presented and
packet-validated before mutation: four protected narratives, eleven
specifications, and 37 active PAUTHs. The existing project-authorization
evidence packet is the 53rd packet in the complete validation set and is not an
implementation postimage. Approval is content-specific; a future GO does not
substitute for those exact-content approvals.

## Requirement Sufficiency

**Existing requirements sufficient.** This proposal removes a retired
authority and re-homes no new policy. `DELIB-202667220` supplies owner intent;
the current DCL/ADR session authorities supply retained behavior; registry,
formal-artifact, bridge, lifecycle, and test authorities supply mechanical
controls. WI-5721 separately formalizes the broader three-worker parallelism
requirement and is not absorbed here.

## Implementation Sequence

1. Acquire an exact-session `go_implementation` claim and implementation-start
   packet after controlling GO.
2. Re-run the coherent registry scan, complete index-based tracked-file control
   scan, registered-consumer reverse check, and field-complete five-table
   current-record audit. Compare the exact operative paths, counts, hashes,
   IDs, and fields to this revision. Enumerate all disposable residue; ignore
   aggregate history growth; stop on operative drift or a newly proven
   load-bearing dependency absent from the registry. Re-read WI-5679's latest
   numbered bridge status, the shared PAUTH version, and the two pinned baseline
   module hashes. WI-5718 is the first writer while WI-5679 remains at
   `NO-ACTION` v013; if WI-5679 changes any of those inputs first, stop and
   re-derive before proceeding.
3. Produce all 26 file, eleven specification, nineteen work-item, ten test, one
   project, and 37 PAUTH postimages in a transaction-local staging area. Enforce
   the generic-reference discipline in every new `change_reason` and amended
   `scope_summary`; parse TOML, YAML, and JSON with structured parsers. Run the
   field-complete five-table audit against the drafted postimages and require
   zero non-allowlisted occurrence before owner packet solicitation or any
   mutation. Do not recursively edit files or records by agent judgment.
4. Owner-present and validate eleven specification, four narrative, and 37
   PAUTH postimage packets. Every PAUTH packet filename contains its complete
   authorization ID. The WI-5679 packet preserves its prior provenance in
   generic form. Recheck the existing PAUTH evidence packet as packet 53.
5. Admit the one benchmark through `gt registry register --batch-file` and
   prove declaration/mirror/projection parity. This admission is independently
   correct and idempotent if a later phase stops.
6. Apply the file postimages atomically. Append eleven spec, nineteen work-item,
   ten test, one project, and 37 PAUTH versions through canonical services.
   Preserve every unrelated field and lifecycle state. Record each append in a
   resumable exact-ID journal; retry skips an already-matching postimage and
   never deletes a partial append-only version.
7. Refresh/regenerate the declared retained mirrors and dashboard projection;
   never copy a generated child back over its canonical source.
8. Record passive registry observations through the canonical observation
   service. Stable-path content changes do not alter registry identity rows.
9. Run both zero-reference scans, the registered-consumer reverse check, the
   field-complete record guard, focused tests, parsers, packet validators,
   registry coherence/parity checks, and worktree-scope checks.
10. File a `NEW` implementation report. Independent LO either atomically files
   terminal VERIFIED with the exact authorized implementation set or leaves no
   terminal candidate. Only after commit-backed VERIFIED may WI-5718 resolve.

## Executed Pre-Implementation Baseline

The complete ten-module file group currently collects 74 tests and reports
`63 passed / 11 failed`. Seven failures are in-scope and must become green:

- `test_gov_session_role_authority_001_dispatcher_only`
- `test_dcl_session_role_resolution_001_enforcement_gate_split`
- all three tests in `test_modernization_authority_foundations.py`
- `test_full_fixture_scores_one_and_reports_dimensions`
- `test_missing_role_and_manifest_anchors_reduce_score`

Four exact residuals are pre-existing and out of WI-5718 scope: the Antigravity
directive and oldest-to-newest prose omissions in `AGENTS.md`, plus two
dispatcher-not-ready parameterizations in
`test_dispatcher_runtime_durable_keyed_regression.py`. The required postimage
for this group is therefore `70 passed / 4 failed`, with exactly those four and
no additional failure.

The current WI-5679-adjacent group consists of the two files that actually
exist: `test_session_envelope_runtime.py` and
`test_workstream_focus_hook_parity.py`. It reports `40 passed / 4 failed`; all
four are unrelated activity-profile/Codex-hook parity baselines and must remain
the exact residual set. The previously named
`test_session_role_keying_continuity.py` does not yet exist; it is future
WI-5679 output and is run only if that thread lands before WI-5718 verification.

This baseline is explicitly sequenced with WI-5679 even though the proposals'
declared mutation-path intersection is empty. WI-5718 uses the current two-file
hashes and `40 passed / 4 failed` baseline only while WI-5679 has not changed
them. If WI-5679 lands first, WI-5718 stops before packet solicitation or
mutation, reruns the group, refreshes its pinned residual set, and returns to
review if the required postimage count changes.

Eight of the ten WI-5718-touched test modules carry documentation, comment, or
fixture-parity edits and do not independently prove new behavior. Their green
count proves corpus consistency only. The substantive behavioral addition is
the zero-reference retirement guard; every pre-existing unrelated assertion in
that guard module must survive unchanged, and only the obsolete presence
assertion may be replaced.

## Specification-Derived Verification Plan

| Requirement | Mechanical verification and required result |
| --- | --- |
| Formal retirement persists | `gt spec show GOV-SESSION-ROLE-AUTHORITY-001 --json`: current version >=6, status `retired`, historical versions unchanged |
| Registry file coverage | Registry scanner: zero operative registered hit outside the three historical classes; tracked-file control: complete 61/111 preimage partition reproduced, benchmark admitted, exact 16 disputed residuals have zero registered references, all other unregistered hits receive their disclosed class, and any new load-bearing dependency routes to admission |
| Current records clean | Before packet solicitation, field-complete scan of every drafted five-table postimage: zero non-allowlisted hit and no literal in a new `change_reason` or amended `scope_summary`; after append, repeat against live current rows. Exact retired identities, completed PAUTH, and 17 named audit row/field pairs only. |
| File manifest exact | Recompute 26 paths/44 preimage hits before mutation; zero changed preimage |
| Registry coherent | `gt registry inspect --no-census --json`, `gt registry validate --json`, and `gt registry sync --json`: coherent/current declaration and projection; content-observation warnings disclosed without invalidating correct bytes |
| Structured files valid | Parse all changed TOML, YAML, and JSON with repository-native parsers; zero parse error |
| Formal packets valid | Canonical validator passes one PAUTH evidence packet plus all 52 exact postimage packets |
| Record versions exact | 11 specs, 19 work items, 10 tests, 1 project, and 37 active PAUTHs each advance exactly once with unrelated fields preserved |
| Role behavior preserved | Ten-module group becomes exactly 70/4; current adjacent group remains exactly 40/4 while WI-5679's pinned inputs are unchanged. If WI-5679 lands first, stop, rerun, and review any changed required postimage. No new residual. Eight touched modules are declared parity-only; the zero-reference guard carries the behavioral proof and retains unrelated assertions. |
| Zero guard works | New test fails on synthetic registered hits, a newly proven unregistered load-bearing dependency, regeneration into a current row, and other current-record operative hits; disclosed or newly classified disposable residue is reported without becoming authority |
| Hand-edit contract preserved | Focused tests prove direct owner content remains valid and attribution/observation gaps are warn-and-repair, not content-invalidating |
| Worktree bounded | `git diff --name-only`, `git diff --cached --name-only`, `git diff --check`, and final commit inventory contain only authorized paths; unrelated untracked bridge work preserved |

Focused commands must include at least:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py platform_tests/scripts/test_harness_role_protocol_smoke.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_lo_startup_text.py platform_tests/scripts/test_modernization_authority_foundations.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py platform_tests/scripts/test_harness_role_protocol_smoke.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_lo_startup_text.py platform_tests/scripts/test_modernization_authority_foundations.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py platform_tests/scripts/test_work_intent_role_eligibility.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py platform_tests/scripts/test_harness_role_protocol_smoke.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_lo_startup_text.py platform_tests/scripts/test_modernization_authority_foundations.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py platform_tests/scripts/test_work_intent_role_eligibility.py
```

## Acceptance Criteria

1. The retired GOV remains append-only at version 6 or later with status
   `retired`; no prior specification, bridge, deliberation, approval packet, or
   historical work-item version is rewritten or deleted.
2. The registry-backed scan reports zero operative registered hit outside the
   three historical classes. The tracked-file control reproduces the complete
   61-file / 111-occurrence preimage partition, the benchmark is admitted, and
   every other unregistered hit receives its disclosed disposition. The
   registered reverse check reports zero reference to the exact 16 disputed
   residuals; the three classification-test path mentions under `memory/**`
   are disclosed as WI-5696 debt. Any new outside-class hit is reverse-checked:
   proven load-bearing use routes to admission, while disposable residue warns
   without blocking or acquiring authority.
3. Before packet solicitation or any mutation, a field-complete audit across
   every drafted current spec, work-item, test, project, and PAUTH postimage
   reports zero non-allowlisted hit and no retired literal in any new
   `change_reason` or amended `scope_summary`. The same live post-append audit
   permits only the exact retired identities, completed PAUTH, and 17 named
   immutable audit row/field pairs.
4. Exactly 26 files and 44 pre-change operative occurrences are transformed
   from approved preimages; any operative scope drift aborts before mutation.
5. Eleven specifications, nineteen work items, ten tests, one project, and 37
   active PAUTHs receive exactly one append-only current version with unrelated
   fields and lifecycle states preserved. The WI-5679 PAUTH is explicitly
   derived from clean v2 `included_spec_ids` plus residual `scope_summary` and
   `change_reason`; its generic successor preserves provenance without the
   retired literal, and historical v2 remains immutable.
6. The project-authorization evidence packet and all 52 exact-content postimage
   packets validate; no formal/narrative or PAUTH amendment bypass occurs.
7. The executable zero-reference guard contains no full literal identifier,
   rejects synthetic registered recurrence, a newly proven unregistered
   load-bearing dependency, generator-driven current-record re-entry, and other
   current-record recurrence. It permits only exact historical/audit fields and
   reports disclosed or newly classified disposable artifacts without making
   them authority.
8. All targeted source/destination retention pairs remain present, registered,
   semantically equivalent where intended, and free of the retired citation.
   No WI-5640 source is deleted, moved, renamed, or unregistered.
9. Exact-session and dispatched-worker role behavior remains governed by the
   surviving DCL/ADR authorities; no active text says a harness owns the worker
   role of all sessions using it.
10. Ordinary owner text-editor changes require no notation. Audit or passive
    observation gaps remain visible repair-forward warnings and do not
    invalidate correct content or block unrelated useful work.
11. Registry declaration/projection parity and identity remain coherent; exactly
    one benchmark record is added, while stable-path content edits create,
    remove, or rename no other registry identity.
12. No unrelated worktree path, dispatcher action, destructive cleanup,
    history rewrite, push, release, deployment, credential action, or external
    mutation occurs.
13. Terminal VERIFIED and its bounded local commit are atomic. WI-5718 resolves
    only after that commit and cites both the owner decision and terminal
    evidence.

## Risks And Rollback

The principal risk is a broad token deletion that leaves invalid TOML/YAML or
semantically false prose. Exact preimage hashes, occurrence counts, per-path
operations, structured parsing, and postimage packet validation constrain that
risk. A second risk is cleaning text files while leaving current MemBase rows
dirty; the field-complete five-table manifest prevents that partial success. A
third risk is accidentally rewriting immutable audit history; exact class and
row/field allowlists prevent it. A fourth risk is weakening or widening active
project authorizations while removing the retired citation; one-to-one exact
postimages, 37 owner-approved packets, and before/after envelope comparison
constrain every PAUTH to citation removal only. A fifth risk is re-executing a
superseded unregistered packet generator after the purge. Exact generator-path
classification, zero registered consumers, content-specific postimage packets,
and the current-record recurrence guard make that activity visible and prevent
its output from silently becoming current authority; the future
registry-authoritative hygiene sweep may delete the disposable sources.
A sixth risk is WI-5679 advancing the shared authorization row or the pinned
baseline modules after WI-5718 derives its packet. The first-writer rule,
fresh latest-status/version/hash checks, and mandatory re-derivation before any
packet solicitation or mutation fail closed on that cross-thread drift.

Before report filing, rollback is append-only repair-forward: restore only
authorized file postimages from transaction-local preimages and append
correcting current record versions through canonical services. Never delete or
rewrite prior MemBase versions or bridge history. A failed terminal finalization
must leave no terminal verdict candidate and no staging residue.

## Files Expected To Change

Exactly the `target_paths` declaration above. `groundtruth.db` and approval
packets are by-reference/generated evidence governed by their own transaction
rules. Both registry declaration files change only to admit the one benchmark;
no existing identity or locator changes. Terminal finalization must use the
report's exact changed-path inventory and exclude unrelated worktree paths.

## Recommended Commit Type

`fix`

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
