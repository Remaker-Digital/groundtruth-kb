REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; resolved role prime-builder; build envelope

# Revised Dispatcher Black-Box Specification Foundation - Formalization Scope Split

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 017
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-016.md
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666277.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET-V2.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md"]

implementation_scope: governance_foundation_formalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

This version directly answers the corrected NO-GO in `bridge/gtkb-dispatcher-black-box-spec-foundation-016.md`.

Version 017 restores the slice boundary required by the implementation-start gate: WI-5268 is now a formalization-only Prime proposal whose target paths exclude every source, hook, configuration, and test file. It preserves the owner-approved V2 formal-artifact contents and approval evidence from `DELIB-202666277`, while moving the foundation-first enforcement gate implementation into a separate follow-on proposal after the five foundation artifacts reach terminal VERIFIED.

The active PAUTH is `PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715`, version 3. The `20260716` PAUTH identifier printed in the version-016 NO-GO header is not a live authorization record; `gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260716 --json` returns not found.

Version 016 requested `bridge_kind: governance_review`, but the live bridge-kind taxonomy rejects that literal under `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`. The canonical mapper treats legacy `governance_review` as `governance_advisory`, and the bridge writer only accepts canonical taxonomy values. `governance_advisory` is terminal/advisory routing, not an implementable Prime proposal. This revision therefore uses canonical, fileable `bridge_kind: prime_proposal` and resolves the implementation-start blocker by declaring the owner-approved V2 packet as sufficient existing requirements for this narrowed formalization slice.

No source, hook, test, configuration, dispatcher topology, runtime state, credential, deployment, external-system, destructive cleanup, git history, or git push work is requested by this revision.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher internals remain a black-box service boundary.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - ordinary workers consume governed packet surfaces rather than dispatch internals.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is filed through the append-only bridge chain and returns the thread to Loyal Opposition for review.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - version 015 was a Prime-authored NO-ACTION and version 016 properly routed the thread back to Prime with NO-GO.
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` - version 017 uses a canonical bridge kind accepted by the live bridge writer.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - future GO verdicts must use `author_session_context_id:` metadata so implementation-start can prove review independence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active PAUTH bounds WI-5268 only.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass GO, claim, implementation-start, exact target paths, implementation report, or independent verification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the implementation-start packet must be created from the live latest GO and exact targets at operation time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised proposal cites the governing specification set.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths are machine-readable in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute derived checks against the formal artifacts and approval evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the formal artifact metadata must remain machine-evaluable.
- `GOV-STANDING-BACKLOG-001` - WI-5268 backlog state must not falsely claim terminal closure.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - downstream WI-5269 through WI-5276 remain blocked until the foundation reaches terminal VERIFIED.
- `GOV-WORK-TREE-HYGIENE-001` - this revision avoids absorbing unrelated dirty source, hook, test, or database work.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - state claims in implementation and verification must use live canonical reads.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - accepted owner decisions become durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - decisions, tests, reports, and verification evidence must remain connected as an artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this thread remains non-terminal until implementation report and VERIFIED verdict complete.
- `GOV-ARTIFACT-APPROVAL-001` - strict review gate for formal artifact persistence.
- `PB-ARTIFACT-APPROVAL-001` - canonical formal artifact writes require approval evidence.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - formalization must preserve full native content and metadata before canonical persistence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - approval packets must validate against the approved native content.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE` - strict operational black-box boundary.
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET` - CLI-first worker context facade.
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT` - scoped maintenance capability enforcement.
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE` - raw bridge files are protected ordinary-worker surfaces.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` - safe-facade-first rollout before hard gates.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PROJECT-HOME` - modernization child-project home.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` - ordinary worker is envelope-state based.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY` - protected access requires explicit maintenance/admin activity or case capability.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` - worker-safe packet must include full assigned content.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` - formal foundation precedes downstream implementation work.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - ops controls black-box configuration mutation; build controls case-authorized direct internals mutation.
- `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL` - original WI-5268 PAUTH/proposal approval.
- `DELIB-202666272` - owner approved the first revised foundation packet and bounded PAUTH test-scope amendment.
- `DELIB-202666277` - owner approved the hash-bound WI-5268 foundation packet V2, metadata-v2, scoped build envelope, and isolated row-level finalization strategy.
- `DELIB-20265888` - prior dispatcher architecture decision: dispatch is a GT-KB-owned black-box service and harnesses are consumers only.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-006.md` - earlier NO-GO that led to mixing enforcement targets into this foundation slice.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-016.md` - corrected NO-GO requiring the scope split in this revision.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md` - sibling VERIFIED thread that cleared shared enforcement-file foreign work but did not implement WI-5268.
- WI-5383 / `bridge/gtkb-wi5383-terminal-commit-closure-evidence-001.md` - open recurrence class for false or premature backlog closure.

## Owner Decisions / Input

The owner-approved hash-bound inputs remain unchanged:

- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET-V2.md`, SHA256 `7FF8E08BCE5EF537FF0B559E70826D6A585E26399E33215F0CE8A50C4CA715A5`.
- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json`, SHA256 `56BD5D5B17A495AAC84C5F10FA7A37EC9CE0DAECFD332272B060BDF2700F0604`.
- The five native formal-artifact drafts and hashes listed below.

`DELIB-202666277` authorizes the V2 packet, V2 metadata, scoped build envelope, row-level database strategy, and corrected proposal path. This revision narrows scope and does not request a new owner decision.

## Exact Formal Artifact Contents

All five proposed records are create-only formal artifacts with status `specified`, priority `P0`, scope `dispatcher-black-box-hardening`, testability `automatable`, and application scope `gtkb_platform`. Their exact content remains the owner-approved V2 set:

| Artifact | Type | Content File | SHA256 |
| --- | --- | --- | --- |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | `design_constraint` | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md` | `be3ff577ee08df976542de1ef9dd75284cc24a1edee5eb5f11056c1933a02574` |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | `design_constraint` | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md` | `e6a58c02993a8a0350a0655b65ffd023f7402febf36bf5694b9dc845a88cd237` |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | `design_constraint` | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md` | `aa62220c8cbfd62ae43d48a61d6ca321c1f7cee4c803dfa474a5e575724d9d71` |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | `architecture_decision` | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md` | `beffe6da9b2d75a471702a52d68cce865642fc77d34f617708f9e3577531a5b9` |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | `design_constraint` | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md` | `b2c2ffcf047a7d33a95e73f90f2b46525b3b55c25e383b4ad603a8c0fefe4088` |

Implementation must hash-verify all seven approved input files before any canonical mutation and must stop if any hash differs.

## Requirement Sufficiency

Existing requirements sufficient.

`DELIB-202666277` approved the exact V2 owner packet, metadata manifest, native formal-artifact drafts, scoped build envelope, and row-level database strategy for this formalization slice. This implementation is not inventing new requirement content; it records the already approved V2 content as governed MemBase artifacts and formal approval evidence.

The target paths contain only `groundtruth.db`, formal approval evidence, and owner-approved native draft/metadata inputs. The version-007 source, hook, and test targets are removed:

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`

Because those targets are excluded, this proposal no longer needs the legacy `governance_review_requirement_capture` submode or a "gap" requirement-sufficiency state. The current implementation-start gate can authorize it as a normal Prime proposal with sufficient existing owner-approved requirements.

## NO-GO Remediation Map

### F1 - GO verdict author-session metadata used a non-canonical field name

Addressed by instruction and verification requirement. This Prime revision cannot edit Loyal Opposition metadata, but it explicitly requires any future GO on this thread to use `author_session_context_id:` in the verdict header. The review-start checklist for this thread must include a read-only implementation-start dry run before GO, so metadata defects are caught by the reviewer before another GO is filed.

### F2 - Requirement Sufficiency state incompatible with target_paths

Corrected by scope and by executable gate semantics. Version 017 keeps the fileable canonical `bridge_kind: prime_proposal`, changes the sufficiency state to `Existing requirements sufficient` based on `DELIB-202666277`, narrows `implementation_scope` to formalization only, and removes all forbidden source/test/config targets from `target_paths`.

The exact `bridge_kind: governance_review` requested in version 016 is not fileable under the live taxonomy. `platform_tests/scripts/test_bridge_kind_taxonomy.py` documents that legacy `governance_review` maps to canonical `governance_advisory`; the live bridge writer rejects the legacy literal and accepts only canonical taxonomy values. Using `governance_advisory` would make the thread advisory/terminal rather than implementable. The implementable correction is therefore the combination of `prime_proposal`, narrowed targets, and `Existing requirements sufficient`.

The enforcement gate is deferred into a separate follow-on implementation proposal after these five formal artifacts reach terminal VERIFIED. That follow-on proposal will cite the newly verified foundation artifacts as existing requirements and may then declare `Existing requirements sufficient`.

### F3 - Live database precondition was falsely asserted

Corrected. This revision makes no claim that `groundtruth.db` is clean. Implementation must re-check live state immediately before mutation, record the pre-write database hash and exact current rows, perform only the approved row-level actions, and report post-write hashes plus row evidence. Rollback remains append-only correction or supersession, not binary database blob revert.

### F4 - WI-5268 backlog record is falsely marked resolved

Acknowledged and incorporated into the proposed implementation sequence. Live reads before this revision confirm WI-5268 is still `stage=resolved` / `resolution_status=resolved` while the latest bridge state is `NO-GO`, the five formal artifacts are absent, and `TEST-11423` is unbound.

After GO and implementation-start authorization, the first canonical database action in this slice must append a corrective WI-5268 work-item version that restores `stage=backlogged`, `resolution_status=open`, updates `status_detail` to state that the latest bridge state is pending review/implementation of this REVISED foundation proposal, and records the recurrence against WI-5383. This correction is inside the same `groundtruth.db` row-level ledger and is included because leaving the false resolved state would contradict the foundation-first gate.

Prime Builder is not performing this MemBase mutation before GO; this revision only proposes the governed correction path.

### F5 - governance_review_forbidden_targets dot-prefix normalization defect

Acknowledged and contained. Version 017 manually excludes every dot-prefixed protected target that could be misclassified by the known `lstrip("./")` defect. This thread does not rely on the defective automated check for exclusion.

The defect should be handled by a separate bridge/backlog item for `scripts/implementation_authorization.py` and its regression tests. This revision does not include that source change.

## Specification-Derived Verification Plan

Implementation verification must map each linked requirement and each proposed formal artifact to executable command evidence. Because this governance-review slice does not add a new source test file, the executable checks use existing project CLIs and validators plus an inline assertion harness captured in the implementation report.

Required pre-mutation checks:

```text
gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715 --json
python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatcher-black-box-spec-foundation --session-id <prime-session-id>
git status --short -- groundtruth.db
```

Expected: PAUTH is active version 3; implementation-start authorizes the latest GO for version 017; database dirtiness is recorded as current-state evidence, not treated as a cached precondition.

Required owner-input hash checks:

```text
powershell -NoProfile -Command "Get-FileHash .gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET-V2.md -Algorithm SHA256"
powershell -NoProfile -Command "Get-FileHash .gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json -Algorithm SHA256"
powershell -NoProfile -Command "Get-FileHash .gtkb-state/propose-drafts/dispatcher-black-box-foundation/ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md -Algorithm SHA256"
powershell -NoProfile -Command "Get-FileHash .gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md -Algorithm SHA256"
powershell -NoProfile -Command "Get-FileHash .gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md -Algorithm SHA256"
powershell -NoProfile -Command "Get-FileHash .gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md -Algorithm SHA256"
powershell -NoProfile -Command "Get-FileHash .gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md -Algorithm SHA256"
```

Expected: hashes match the owner-approved values in `DELIB-202666277` and this proposal.

Required formal packet validation:

```text
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json
```

Expected: every packet exits 0 and binds the approved content.

Required canonical row verification after implementation:

```text
gt spec show DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001 --json
gt spec show DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001 --json
gt spec show DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001 --json
gt spec show ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001 --json
gt spec show DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001 --json
gt backlog show WI-5268 --json
gt tests show TEST-11423 --json
```

Expected: the five formal artifacts exist with the approved status/type/title/content/metadata; WI-5268 no longer falsely claims terminal resolution; TEST-11423 remains visible as the linked WI test authority and is either explicitly left pending follow-on enforcement-test binding or updated only by an independently approved row-level route.

Required semantic assertion harness in the implementation report:

```text
python -c "<inline JSON assertions over gt spec/backlog/tests output captured in the report>"
```

Expected: the implementation report includes the exact inline assertion command or a checked-in existing assertion command, its source inputs, and observed PASS output. The assertion must fail if any of the five formal artifacts are missing, if WI-5268 remains falsely resolved, if any owner-approved hash differs, or if downstream WIs WI-5269 through WI-5276 are no longer open/backlogged before foundation VERIFIED.

Required bridge preflights:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
```

Expected: applicability passes with no missing required or advisory specs, and clause preflight reports zero blocking gaps.

## Follow-On Enforcement Proposal

After the five foundation artifacts reach terminal VERIFIED, Prime Builder must file a separate implementation proposal for the foundation-first enforcement gate. That follow-on proposal may target:

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`

It must declare `Existing requirements sufficient` and cite the newly verified foundation artifacts. It must also address the `governance_review_forbidden_targets()` dot-prefix defect if that defect remains open.

## Scope Exclusions

This revision explicitly excludes:

- source mutation;
- hook mutation;
- test-file creation or mutation;
- configuration mutation;
- dispatcher topology or routing mutation;
- runtime-state mutation;
- child WI-5269 through WI-5276 implementation;
- production deployment;
- credential lifecycle work;
- external-system mutation;
- destructive cleanup;
- git history rewrite;
- git push; and
- direct black-box internals mutation outside this case-bound build-envelope proposal.

## Risk And Rollback

Risk: delaying the enforcement gate keeps the foundation-first rule advisory rather than mechanically enforced for one more slice. Mitigation: the bridge and backlog remain live evidence of non-terminal WI-5268 state, and this proposal requires the WI-5268 false resolved record to be corrected before implementation report filing.

Risk: `groundtruth.db` is dirty and high-traffic. Mitigation: implementation uses the owner-approved row-level ledger strategy with pre/post hashes and exact row evidence. Rollback is append-only corrective or superseding formal artifact/work-item rows, not binary database blob revert over later changes.

Risk: a reviewer could issue another GO without exercising implementation-start. Mitigation: this proposal asks LO to run `python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatcher-black-box-spec-foundation --session-id <independent-session-id> --no-write` before GO and include the result in the verdict.

## Candidate Preflight Evidence

- Candidate applicability preflight: PASS before filing. `python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-dispatcher-black-box-spec-foundation-017.md --json` exited 0 with `preflight_passed: true`, `blocking_errors: []`, `missing_required_specs: []`, and `missing_advisory_specs: []`. Final observed candidate packet hash before live filing: `sha256:542288f73246e01dc6c3fbd781750464402dc2a89d817c2550b20600e57dfec8`.
- Candidate ADR/DCL clause preflight: PASS before filing. `python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-dispatcher-black-box-spec-foundation-017.md` exited 0 with 5 clauses evaluated, 3 `must_apply`, 0 evidence gaps in `must_apply` clauses, and 0 blocking gaps.
- Candidate implementation-start coherence check: PASS before filing. `python -c "from pathlib import Path; import scripts.implementation_authorization as ia; ..."` reported `bridge_kind: prime_proposal`, `sufficiency: sufficient`, `forbidden: []`, and `target_count: 14`.

## Recommended Commit Type

Recommended commit type: `feat:`. The eventual implementation creates the canonical dispatcher black-box formal foundation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
