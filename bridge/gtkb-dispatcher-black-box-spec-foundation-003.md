REVISED

# gtkb-dispatcher-black-box-spec-foundation (Slice 1) — Dispatcher Black-Box Governance/Spec Foundation

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 003
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-002.md
Author: Prime Builder (Codex)
Date: 2026-07-15T17:55:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, GT-KB Prime Builder interactive session

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-REVISED-FOUNDATION-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json", "platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/*.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata.json"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## First-Line Role Eligibility Check

PASS. Transcript-defined Prime Builder in session `019f6668-9974-7d72-a456-826f9a67e627` is authorized to write a `REVISED` Prime proposal after Loyal Opposition returned `NO-GO` in `bridge/gtkb-dispatcher-black-box-spec-foundation-002.md`.

## Summary

This REVISED proposal implements `WI-5268` only. It creates the formal governance/specification foundation for the dispatcher/TAFE/harness black-box boundary before downstream source, prompt, hook, CLI, runtime, or configuration implementation proceeds.

The revision addresses the Loyal Opposition NO-GO by adding exact owner-approved native formal-artifact content, strict approval-gate authorities, an executable focused test target, a revised PAUTH with `test_addition` authority, a dirty-SQLite fail-closed finalization plan, and a foundation-first gate that substitutes for unavailable backlog dependency-edge writer support.

This proposal does not authorize `WI-5269` through `WI-5276` implementation, dispatcher topology mutation, bridge/TAFE/harness configuration mutation, source/runtime implementation outside the focused test, production deployment, credential lifecycle work, git push, or direct black-box internals mutation.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatch is a GT-KB-owned black-box service; this slice formalizes the worker-side boundary.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` — harnesses are consumers/producers of artifacts, not dispatch controllers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this revision is filed through the append-only bridge chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-DISPATCHER-BLACK-BOX-WI5268-REVISED-FOUNDATION-20260715` bounds the approved work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not bypass LO GO, target paths, implementation reports, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation-targeting proposal with governing spec links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries PAUTH, project, work-item, and target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requires executable derived checks, not only metadata reads.
- `GOV-STANDING-BACKLOG-001` — `WI-5268` and `TEST-11423` are the durable backlog/test authorities for this slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory and owner decisions crossed the threshold for durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — decisions become artifact-graph nodes rather than transient chat memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — owner decisions and accepted future work move through explicit lifecycle states.
- `GOV-ARTIFACT-APPROVAL-001` — strict review gate requires full native artifact proposal before canonical persistence.
- `PB-ARTIFACT-APPROVAL-001` — canonical artifact writes require approval evidence.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — architecture uses strict formalization gate with scoped approval modes.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — hooks/CLIs must display full native proposal and capture approval evidence.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE` — strict operational black-box boundary.
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET` — CLI-first worker context facade.
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT` — scoped maintenance capability enforcement.
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE` — raw bridge files are protected ordinary-worker surfaces.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` — safe-facade-first rollout before hard gates.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PROJECT-HOME` — modernization child-project home.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` — ordinary worker is envelope-state based.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY` — protected access requires explicit maintenance/admin activity or case capability.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` — safe packet must include full assigned content.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` — formal foundation precedes implementation work.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` — ops controls black-box configuration mutation; build controls case-authorized direct internals mutation.
- `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL` — original WI-5268 PAUTH/proposal approval only.
- `DELIB-202666272` — owner approved the exact revised WI-5268 foundation packet and bounded PAUTH test-scope amendment.
- `DELIB-20265888` — prior dispatcher architecture decision: dispatch is a GT-KB-owned black-box service and harnesses are consumers only.

## Owner Approval Evidence

The owner replied `APPROVE WI5268 REVISED FOUNDATION PACKET`. That approval was recorded as `DELIB-202666272` with content hash `7fdd643a2bde07890a48f4b1853e3c0470539ae488dd3ea82f263aae9f16232d` and approval packet `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666272.json`.

`DELIB-202666272` approves the exact review packet at `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET.md`, the metadata manifest at `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata.json`, the five native draft contents and displayed hashes below, the REVISED bridge proposal, the `test_addition` PAUTH scope, and the foundation-first gate handling. It does not approve canonical implementation before LO GO and implementation-start/work-intent evidence.

## Exact Formal Artifact Contents

All five proposed records are create-only formal artifacts with status `specified`, priority `P0`, scope `dispatcher-black-box-hardening`, testability `automatable`, and application scope `gtkb_platform`. The exact native content files were displayed to the owner and dry-run validated through `gt spec record --dry-run --json`.

| Artifact | Type | Title | Content File | SHA256 |
| --- | --- | --- | --- | --- |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | `design_constraint` | Dispatcher ordinary-worker black-box boundary | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md` | `be3ff577ee08df976542de1ef9dd75284cc24a1edee5eb5f11056c1933a02574` |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | `design_constraint` | Dispatcher worker-safe packet contract | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md` | `e6a58c02993a8a0350a0655b65ffd023f7402febf36bf5694b9dc845a88cd237` |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | `design_constraint` | Dispatcher activity-envelope authority split | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md` | `aa62220c8cbfd62ae43d48a61d6ca321c1f7cee4c803dfa474a5e575724d9d71` |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | `architecture_decision` | Use a worker-context facade for ordinary dispatcher work | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md` | `beffe6da9b2d75a471702a52d68cce865642fc77d34f617708f9e3577531a5b9` |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | `design_constraint` | Dispatcher black-box foundation-first project gate | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md` | `fbc3eeb7f2df289b06e4c0c7243604701fd6c09e2632f29b98111c18916fb765` |

The exact metadata, tags, constraints JSON, affected-by links, source-path lists, and assertion metadata are in `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata.json`.

## Requirement Sufficiency

New or revised requirement required before implementation.

Existing `ADR-DISPATCHER-ARCHITECTURE-001` establishes the dispatcher as a black box, but it does not encode the July 15 owner decisions about envelope-state ordinary workers, full assigned-content safe packets, ops/build authority split, scoped maintenance capabilities, raw bridge-file protection, or foundation-first rollout.

This slice creates those authorities only. Implementation mechanics remain in child WIs after this slice is VERIFIED.

## NO-GO Remediation Map

F1 is addressed by citing the four strict formal-artifact approval authorities, presenting exact native content files, preserving metadata and hashes in `artifact-metadata.json`, and citing owner approval `DELIB-202666272`.

F2 is addressed by adding focused executable test target `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`, adding `test_addition` to the PAUTH, and requiring `TEST-11423` to bind to that file/function during implementation.

F3 is addressed by an implementation-start fail-closed SQLite baseline gate. Before canonical spec or packet writes, Prime Builder must record `git status --short -- groundtruth.db .groundtruth/formal-artifact-approvals platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`, a `groundtruth.db` SHA256 hash, and a row-ledger of exact rows expected from `DELIB-202666272` and this PAUTH. If `groundtruth.db` has unowned dirty changes or a clean exclusive DB baseline cannot be established, implementation must halt and return for an owner-approved isolated row-level import/finalization strategy. The implementation report must not claim a scoped DB commit or DB rollback unless the DB baseline is clean and exclusive. Rollback is append-only corrective/superseding artifact versions, not binary database revert over later unrelated changes.

F4 is addressed by `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`. The public `gt projects` and `gt backlog update` CLIs do not expose a dependency-edge writer for existing work items, so direct dependency-field mutation would bypass governed lifecycle surfaces. Until a governed writer exists, the formal gate plus executable foundation test is the mechanical equivalent: downstream WI-5269 through WI-5276 implementation proposals must fail closed while WI-5268 is not terminal VERIFIED.

## Specification-Derived Verification Plan

Implementation verification must include a spec-to-test mapping from each new foundation artifact to the focused executable test:

```text
python -m pytest platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py -q --tb=short
```

Expected: the test passes and proves:

- all five foundation artifacts exist with correct type, status, title, description content, tags/constraints, affected-by links, source paths, testability, and approval evidence;
- `DELIB-202666272` is linked as owner approval evidence;
- the ordinary-worker boundary is envelope-state based and applies to PB and LO ordinary workers;
- worker-safe packets include full assigned content and exclude raw internals;
- ops and build activity envelopes are non-interchangeable and build requires case-specific authorization;
- foundation-first gate blocks downstream WI-5269 through WI-5276 readiness until WI-5268 is terminal VERIFIED;
- `TEST-11423` is bound to the executable test file/function.

Formal packet validation:

```text
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json
```

Expected: every packet exits 0 and the `full_content_sha256` matches the owner-approved content hashes above.

MemBase row verification:

```text
python -m groundtruth_kb.cli spec show DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001 --json
python -m groundtruth_kb.cli spec show DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001 --json
python -m groundtruth_kb.cli spec show DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001 --json
python -m groundtruth_kb.cli spec show ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001 --json
python -m groundtruth_kb.cli spec show DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001 --json
python -m groundtruth_kb.cli tests show TEST-11423 --json
```

Expected: rows exist with the exact metadata in `artifact-metadata.json`, and `TEST-11423` cites the executable test file/function.

Proposal/verdict preflights:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
```

Expected: applicability passes with no missing required specs and clause preflight reports zero blocking gaps.

## Implementation Start Gate

After GO, before any canonical write, Prime Builder must:

1. Acquire matching bridge work-intent for `gtkb-dispatcher-black-box-spec-foundation`.
2. Record current bridge latest status as GO and confirm the GO responds to this `Version: 003`.
3. Record `git status --short -- groundtruth.db .groundtruth/formal-artifact-approvals platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`.
4. Record SHA256 of `groundtruth.db`.
5. Fail closed if `groundtruth.db` is dirty from unowned changes or if the clean exclusive baseline required for scoped finalization cannot be established.
6. If blocked by DB baseline, stop before formal writes and return for owner-approved isolated row-level finalization strategy.

## Risk / Rollback

Risk: a weak foundation could overexpose black-box internals or overconstrain legitimate ops/build maintenance. Mitigation: exact native content is owner-approved and LO-reviewed before canonical mutation, and mechanics remain out of scope.

Risk: the tracked SQLite database is binary and already dirty in the working tree. Mitigation: implementation must fail closed unless a clean exclusive baseline or owner-approved row-level finalization strategy exists. The implementation report must carry pre/post DB hashes and exact inserted row/version evidence. Rollback is append-only corrective or superseding formal artifact versions, not binary DB blob revert over later unrelated changes.

Risk: a DCL gate is weaker than native backlog dependency edges. Mitigation: the public lifecycle CLI lacks an existing-WI dependency writer, so this slice records a formal gate and executable test now, and allows later backfill of explicit edges if a governed writer becomes available.

## Bridge Filing

This proposal is filed as `bridge/gtkb-dispatcher-black-box-spec-foundation-003.md`, preserving the append-only chain after `-001` NEW and `-002` NO-GO. No retired aggregate queue artifact is used or created.

## Recommended Commit Type

chore — governed metadata/formal-artifact foundation and focused verification test only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
