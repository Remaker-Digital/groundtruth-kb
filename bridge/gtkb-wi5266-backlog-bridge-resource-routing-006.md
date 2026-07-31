REVISED

# Revised Defect-Fix Proposal - WI-5266 Deterministic Backlog Versus Bridge Resource Routing

bridge_kind: prime_proposal
Document: gtkb-wi5266-backlog-bridge-resource-routing
Version: 006
Responds to: bridge/gtkb-wi5266-backlog-bridge-resource-routing-005.md
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6642-19e2-7110-a027-96973221fdec
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; bounded WI-5266 revision

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS-WI5266-RESOURCE-DISAMBIGUATION-20260715
Project Authorization Version: 3
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS
Work Item: WI-5266

target_paths: [".claude/rules/canonical-terminology.md", "config/agent-control/system-interface-map.toml", "config/agent-control/activity-disposition-profiles.toml", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/registry/context-manifests.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/context-manifests.toml", "groundtruth-kb/src/groundtruth_kb/context/manifest.py", "groundtruth-kb/src/groundtruth_kb/context/resource_routing.py", "groundtruth-kb/src/groundtruth_kb/context/__init__.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", ".claude/hooks/session-topic-envelope-router.py", "scripts/check_context_manifests.py", "groundtruth-kb/tests/test_wi5266_resource_routing.py", "platform_tests/scripts/test_wi5266_envelope_resource_routing.py", "platform_tests/hooks/test_wi5266_prompt_resource_routing.py", "groundtruth-kb/src/groundtruth_kb/context/freshness.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/governance/canonical-terms-sync.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-envelope-sharding.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py"]

implementation_scope: source | test | configuration | documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision accepts and fully implements the superseding 25-path dependency-closure requirements in version 005. It replaces the prior 17-path implementation envelope and the superseded GO/start evidence; it does not perform protected implementation mutation. All behavior, exclusions, specification-derived acceptance criteria, and resource-routing design in version 001 remain operative except where this revision narrows provenance or expands the exact clean-checkout dependency boundary.

The corrected proposal binds exactly 25 unique in-root paths: the original 17 plus inherited `freshness.py`, six deterministic packaged registry snapshots, and the exact tracked `activity/profiles.py` dependency hunk. Active PAUTH version 3 classifies the same 25 paths and carries both project-authorization envelope specifications required by version 005.

## Findings Addressed

### FINDING-P1-001: Eight package/runtime dependencies are outside the approved envelope

Response: corrected. The inline JSON `target_paths` array contains the prior 17 paths plus all eight paths listed in version 005. PAUTH version 3 classifies the same set as follows:

| Class | Count | Exact targets |
| --- | ---: | --- |
| Documentation | 3 | `.claude/rules/canonical-terminology.md`; `config/agent-control/SESSION-STARTUP-INDEX.md`; `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` |
| Configuration | 10 | The two canonical agent-control TOML files, canonical context registry, packaged context registry, and all six packaged source snapshots |
| Source | 9 | Context/session runtime modules, two prompt adapters, checker, inherited `freshness.py`, and hunk-only `activity/profiles.py` |
| Test | 3 | The three dedicated WI-5266 test modules |

PAUTH version 3 preserves the project, WI, expiry, allowed mutation classes, forbidden operations, and narrow resource-disambiguation scope. It adds `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` under owner packet `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666276.json`.

### Inherited complete-blob provenance

`DELIB-202666273` remains limited to its five exact resulting blobs. `DELIB-202666275` separately permits only the unchanged inherited `freshness.py` blob. Neither decision approves, implements, completes, or verifies WI-5170.

| Path | Bytes | SHA-256 | Authority |
| --- | ---: | --- | --- |
| `config/registry/context-manifests.toml` | 8,387 | `8f410ba59ac0a38cb8ffc2d5b4b93a5bb1cacce104d47a721e929ca441272225` | `DELIB-202666273` |
| `groundtruth-kb/src/groundtruth_kb/context/registries/v1/context-manifests.toml` | 8,387 | `8f410ba59ac0a38cb8ffc2d5b4b93a5bb1cacce104d47a721e929ca441272225` | `DELIB-202666273` |
| `groundtruth-kb/src/groundtruth_kb/context/manifest.py` | 18,180 | `91b02cbf96d1411e8f039fa4f6fa4f7c666b6922a6a6664958b6c093b7be0c5c` | `DELIB-202666273` |
| `groundtruth-kb/src/groundtruth_kb/context/__init__.py` | 756 | `83d2dd627de4ae7c02b42be2dd16d99f4e5f21e5404d382d87ff3dd77d919f7d` | `DELIB-202666273` |
| `scripts/check_context_manifests.py` | 6,294 | `179c66686e675f89af39483a5a680b4112b30609bbc2169cf6fa88de580f4360` | `DELIB-202666273` |
| `groundtruth-kb/src/groundtruth_kb/context/freshness.py` | 6,334 | `5fa7ef8b081f51ba09eb5e269b404d9a3262d34a599084e0af7d17b3f64cd604` | `DELIB-202666275`; unchanged inherited dependency |

### Hunk-only tracked dependency provenance

`groundtruth-kb/src/groundtruth_kb/activity/profiles.py` will be included only through `.gtkb-state/wi5266-clean-candidate/wi5170-activity-profiles.patch`. The 1,192-byte, two-hunk patch has SHA-256 `2948fa9be74bbafb6692bcfeb94abbb2991877dcade4d952c8b8c7358646746a`, applies to HEAD blob `3248f11e5ffaf46976d9f5b5ec34ddb1a85df47b`, and produces a 10,787-byte candidate with SHA-256 `bfcd3ab78ecf4a6746fb67b050d7f173e6d8837ff47ba6d8b7cef45d9043d471`. It only introduces `CANONICAL_ACTIVITY_ORDER`, derives the activity set from that order, and iterates profiles in that order. No unrelated working-tree content is claimed.

### Deterministic generated snapshot provenance

All six packaged snapshots will be copied byte-for-byte from the clean candidate's canonical sources after GO. They will not be copied from dirty working-tree mirrors.

| Canonical source | Packaged snapshot | Bytes | Source/snapshot SHA-256 |
| --- | --- | ---: | --- |
| `config/governance/canonical-terms-sync.toml` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/governance/canonical-terms-sync.toml` | 260 | `1a70ff7b7aec008b2199819f6e724483a546dd3a2a7fc80ec73c4fa9e6c2b0ef` |
| `config/agent-control/activity-disposition-profiles.toml` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml` | 9,318 | `62f1f2a631aef324a7e7195f3ed8264fc0c69542ba3cbdb4619d40626c525d5f` |
| `config/agent-control/activity-envelope-sharding.toml` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-envelope-sharding.toml` | 4,426 | `f0ead46150907ed2a21c77ef39ab119d1c0c0b91435a91b509cbb20950f70b91` |
| `config/agent-control/command-surface.toml` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml` | 6,910 | `51c195520d03b37474759676f0b1f676f60c992f17683221dfc0d29228c27b35` |
| `config/registry/sot-artifacts.toml` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` | 17,462 | `96d9830eb7c2086e48c7dad2ebc1fe9f669ed5143a5435e7aea4c235c4e16851` |
| `config/agent-control/system-interface-map.toml` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml` | 44,383 | `1421c7a02891daa93c8874450b8fe2d6dc16e47afc4688f2b83c9eabe5e91bdf` |

The clean candidate includes verified predecessor commit `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`, the isolated WI-5266 canonical-source hunks, and the exact tracked activity-order dependency. Four snapshots are unchanged from their clean canonical source; activity disposition and system interface are regenerated from their correspondingly updated clean sources.

### Clean-checkout closure evidence

A disposable candidate created from `git archive HEAD` failed collection with the original 17 and then 24 targets. After adding only the exact activity-profile dependency hunk and regenerating all six snapshots from clean canonical sources, it produced:

- 43 passing context/WI tests with no collection failure;
- successful `import groundtruth_kb.context` and packaged-default registry resolution;
- byte-identical source/package parity for all six snapshots;
- context assertions A1-A8 PASS, including A3 `resource_semantics_exact=true`.

This is pre-GO dependency evidence, not terminal verification. The exact 25-path candidate and all required suites will be rerun after fresh GO, claim, and implementation-start authorization.

## Scope Changes

The implementation boundary changes from 17 to exactly 25 paths. No behavioral feature is added beyond version 001. The eight additions exist solely to make the approved resource-routing implementation importable, packaged, reproducible, and verifiable from a clean checkout.

The prior 17-path claim and implementation-start packet are retired evidence and must not be reused. After GO, Prime Builder will acquire a fresh claim and produce a fresh packet binding this proposal, the new GO file, PAUTH version 3, all 25 target paths, classifications, and packet hash.

## Explicit Exclusions

- No implementation, completion, or verification of WI-5170.
- No whole-file finalization of tracked shared files; `activity/profiles.py` and the startup overlay remain hunk-only.
- No use of dirty current mirrors as generated-snapshot source.
- No dispatcher topology, recipient eligibility, routing, lease, telemetry, deployment, credential, destructive cleanup, external-system, Git-history rewrite, broad staging, or broad commit change.
- No change to backlog priority, bridge actionability, role authority, or the rule that the bridge gates protected backlog implementation without becoming the backlog resource.

## Cross-Harness Disposition

- **Codex (A): behavioral parity.** The existing `UserPromptSubmit` adapter invokes the shared resource resolver for ordinary prompts, updates the session-keyed envelope, and emits the compact resource contract while preserving strict topic and wrap branches.
- **Claude Code (B): behavioral parity.** The existing topic-envelope adapter invokes the same resolver and envelope API for ordinary prompts while preserving strict topic-command behavior and the separate Stop-hook wrap lifecycle.
- **Antigravity (C) and Cursor (E): deterministic fallback parity.** The global context manifest, canonical terminology, activity profile, startup index, and Prime Builder overlay carry the exact non-alias and literal-owner-precedence contract. No unsupported native prompt mutation is claimed.
- **Ollama (D), OpenRouter (F), and other provider/headless harnesses: deterministic fallback parity.** Packaged context manifests carry the same resource contract; dispatcher-created envelopes select `bridge_queue` only from explicit nonblank dispatch provenance.
- **Verification gate.** Shared resolver, both native adapters, session/dispatch envelopes, manifest parity, phase-1/phase-2 evaluators, and activity-envelope discovery must pass. Missing native or deterministic fallback coverage is a verification blocker.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001`
- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-SOT-SINGLETON-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`
- `DCL-CONCEPT-ON-CONTACT-001`
- `ADR-DA-READ-SURFACE-PLACEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260715-WI5266-TERMINAL-VERIFICATION-AUTHORIZATION` - authorizes the bounded WI-5266 lifecycle through independent terminal verification.
- `DELIB-202666273` - exact five-path baseline-preservation exception.
- `DELIB-202666275` - exact unchanged `freshness.py` dependency exception.
- `DELIB-202666276` - exact two-spec PAUTH amendment approval.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - establishes the MemBase-backed backlog authority.
- `bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-006.md` and commit `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f` - terminally verified predecessor and clean-candidate base.
- `bridge/gtkb-wi5266-backlog-bridge-resource-routing-001.md` through `-005.md` - complete proposal, superseded GO, Prime NO-ACTION, and two append-only dependency-closure verdicts; version 005 supersedes version 004.

## Owner Decisions / Input

The owner has supplied every decision required before revised review:

1. `DELIB-20260715-WI5266-TERMINAL-VERIFICATION-AUTHORIZATION` authorizes deterministic BACKLOG versus BRIDGE QUEUE disambiguation through terminal VERIFIED.
2. `DELIB-202666273` permits five exact HEAD-absent resulting blobs only in the atomic WI-5266 terminal transaction.
3. `DELIB-202666275` permits the exact unchanged 6,334-byte `freshness.py` dependency only in that transaction.
4. `DELIB-202666276` permits adding the two exact project-authorization specifications to the unchanged 25-path boundary.

Formal packets validate at `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666273.json`, `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666275.json`, and `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666276.json`.

## Requirement Sufficiency

Existing requirements sufficient. This revision adds no new product requirement; it closes package/runtime dependencies and strengthens authorization evidence for the already-approved behavior.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5266; DELIB-20260715-WI5266-TERMINAL-VERIFICATION-AUTHORIZATION; DELIB-202666273; DELIB-202666275; DELIB-202666276; PAUTH version 3; bridge version 005",
  "canonical_authority": "DCL-ACTIVITY-CONTEXT-MANIFEST-001; ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001; GOV-STANDING-BACKLOG-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Honor explicit current-owner resource nouns first: backlog routes to gt backlog list; bridge queue routes to current TAFE/dispatcher state plus numbered bridge files; bridge remains only the protected-change gate for selected backlog work.",
  "before_behavior": "A bridge-heavy build profile, bridge-first startup order, and incomplete envelope state allowed prior context to replace an explicit backlog instruction with bridge-queue work.",
  "after_behavior": "Every deterministic manifest and supported envelope surface exposes mutually distinct backlog and bridge_queue resources, and current literal owner terms outrank defaults, prior context, notes, and conjecture.",
  "self_descriptive_naming": "Canonical identifiers backlog, bridge_queue, resource_selection, authoritative_source, and read_route expose the selected resource and its access path.",
  "obsolete_guidance_disposition": "Bridge-first startup ordering and bare bridge topic words remain available as governance or topic context but cannot select or substitute the bridge queue.",
  "history_preservation": "The numbered bridge chain, verified predecessor, owner deliberations, PAUTH history, WI-5170 backlog state, and unrelated staged hunks remain preserved and separately attributed.",
  "baseline": {
    "observed_owner_resource": "backlog",
    "observed_substitution": "bridge_queue",
    "original_target_count": 17,
    "clean_checkout_closed_target_count": 25,
    "head": "4ba39a438b84ec40c646cfc46c2741d6e7c6a60f"
  },
  "expected_result": {
    "literal_backlog_prompt": "select backlog only",
    "bridge_related_backlog_prompt": "select backlog only",
    "literal_bridge_queue_prompt": "select bridge_queue only",
    "bare_bridge_topic_prompt": "select no resource",
    "swapped_manifest_routes": "fail closed"
  },
  "rollback": {
    "route": "separately governed exact-hunk reversal",
    "preserve": "verified predecessor, unrelated staged hunks, and WI-5170 state"
  },
  "hard_invariants": [
    "backlog and bridge_queue are distinct non-alias resources",
    "literal current-owner resource terms outrank defaults and prior context",
    "the bridge gates protected backlog implementation without replacing the backlog resource",
    "terminal evidence is built from the exact 25-path clean candidate"
  ],
  "fail_closed_conditions": [
    "swapped or aliased resource routes",
    "missing packaged dependency or source/package parity",
    "scope, claim, start-packet, or finalization target mismatch",
    "absorption of unrelated dirty or staged content"
  ],
  "essential_context_preservation": "Session/activity envelopes retain role, activity, project, WI, authorization, selected resource, source, route, and precedence evidence while strict topic and wrap behaviors remain intact."
}
```

## Pre-Filing Preflight Subsection

### Applicability Preflight

- packet_hash: `sha256:5cd23b06b8cd33b693cb2057307ae7c93ca58d8ac9db4d325f37835a26c955f9`
- bridge_document_name: `gtkb-wi5266-backlog-bridge-resource-routing`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-wi5266-backlog-bridge-resource-routing-006.md`
- operative_file: `bridge/gtkb-wi5266-backlog-bridge-resource-routing-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
| --- | --- | --- | --- |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

### Clause Applicability

- Bridge id: `gtkb-wi5266-backlog-bridge-resource-routing`
- Operative file: `.gtkb-state\bridge-revisions\drafts\gtkb-wi5266-backlog-bridge-resource-routing-006.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
| --- | --- | --- | --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Specification-Derived Verification Plan

| Governing behavior | Executed evidence required before report |
| --- | --- |
| Explicit resource identity, non-alias semantics, and literal-owner precedence | Dedicated resolver tests in `groundtruth-kb/tests/test_wi5266_resource_routing.py` |
| Exact manifest source/read-route semantics and packaged resolution | `groundtruth-kb/tests/test_context_manifest.py` plus `scripts/check_context_manifests.py --json` A1-A8 |
| Session and dispatched-worker envelope evidence | `platform_tests/scripts/test_wi5266_envelope_resource_routing.py` |
| Claude/Codex prompt routing and strict topic/wrap preservation | `platform_tests/hooks/test_wi5266_prompt_resource_routing.py` plus adjacent hook regressions |
| Cross-harness native/fallback parity | phase-1 and phase-2 parity evaluators and activity-envelope discovery checks |
| Exact clean-checkout closure | disposable exact 25-path candidate; context import; packaged-default load; 43-test context/WI suite; source/package byte parity |
| Code and patch hygiene | targeted Ruff check; Ruff format check; `git diff --check`; exact hunk and blob/hash verification |

The dedicated WI-5266 suite must remain 29 passing tests, and the clean candidate must run an equal or superseding 43-test context/WI command. Terminal VERIFIED additionally requires adjacent regressions and the complete spec-to-test mapping carried into the implementation report.

## Risk And Rollback

The primary risks are accidental reliance on untracked package files, copying dirty snapshots, or absorbing unrelated shared-file hunks. Exact clean-candidate generation, byte hashes, hunk-only patches, and independent finalization contain those risks.

Rollback removes only the exact WI-5266 hunks, generated snapshots, authorized complete blobs, and dedicated tests through a separately governed change. It must preserve verified predecessor commit `4ba39a43`, unrelated staged work, and WI-5170 backlog state.

## Recommended Commit Type

`fix` - prevents deterministic initialization from substituting bridge-queue work for an explicit backlog instruction while preserving exact package/runtime closure.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
