REVISED

# gtkb-dispatcher-black-box-spec-foundation (Slice 1) - Dispatcher Black-Box Governance/Spec Foundation V2

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 005
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-004.md
Author: Prime Builder (Codex)
Date: 2026-07-15T19:10:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, GT-KB Prime Builder interactive session

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666277.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/*.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json", ".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py"]

implementation_scope: governance_foundation_and_gate
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## First-Line Role Eligibility Check

PASS. Transcript-defined Prime Builder in session `019f6668-9974-7d72-a456-826f9a67e627` is authorized to write a `REVISED` Prime proposal after Loyal Opposition returned `NO-GO` in `bridge/gtkb-dispatcher-black-box-spec-foundation-004.md`.

## Summary

This REVISED proposal implements `WI-5268` only. It creates the formal governance/specification foundation for the dispatcher/TAFE/harness black-box boundary before downstream source, prompt, hook, CLI, runtime, or configuration implementation proceeds.

Version 005 specifically corrects the four findings in `-004`:

- replaces unsupported `python` assertion metadata with assertion-runner-supported `all_of`, `file_exists`, and `grep` assertions in `artifact-metadata-v2.json`;
- identifies the append-only `KnowledgeDB.update_test` route that binds `TEST-11423` to the exact pytest file/function after the test passes;
- names real enforcement targets for the foundation-first condition: `.claude/hooks/bridge-compliance-gate.py`, `scripts/implementation_authorization.py`, and `scripts/implementation_start_gate.py`;
- carries owner-approved row-level MemBase finalization because `groundtruth.db` is already dirty; and
- hash-binds both the owner packet V2 and metadata manifest V2 in `DELIB-202666277`.

This proposal does not authorize `WI-5269` through `WI-5276` implementation, dispatcher topology/routing mutation, production deployment, credential lifecycle work, external system mutation, destructive cleanup, git history rewrite, git push, unrelated runtime mutation, or direct black-box internals mutation outside the case-bound WI-5268 build envelope.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatch is a GT-KB-owned black-box service; this slice formalizes the worker-side boundary.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - harnesses are consumers/producers of artifacts, not dispatch controllers.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is filed through the append-only bridge chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - `PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715` bounds the approved work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass LO GO, target paths, implementation reports, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation-targeting proposal with governing spec links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal carries PAUTH, project, work-item, and target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires executable derived checks, not only metadata reads.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - formal artifacts need machine-evaluable, supported assertion metadata.
- `GOV-STANDING-BACKLOG-001` - `WI-5268` and `TEST-11423` are the durable backlog/test authorities for this slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory and owner decisions crossed the threshold for durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - decisions become artifact-graph nodes rather than transient chat memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner decisions and accepted future work move through explicit lifecycle states.
- `GOV-ARTIFACT-APPROVAL-001` - strict review gate requires full native artifact proposal before canonical persistence.
- `PB-ARTIFACT-APPROVAL-001` - canonical artifact writes require approval evidence.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - architecture uses strict formalization gate with scoped approval modes.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hooks/CLIs must display full native proposal and capture approval evidence.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-facing hook behavior must preserve parity or record a typed waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - proposals touching harness-surface files must include cross-harness disposition.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE` - strict operational black-box boundary.
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET` - CLI-first worker context facade.
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT` - scoped maintenance capability enforcement.
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE` - raw bridge files are protected ordinary-worker surfaces.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` - safe-facade-first rollout before hard gates.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PROJECT-HOME` - modernization child-project home.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` - ordinary worker is envelope-state based.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY` - protected access requires explicit maintenance/admin activity or case capability.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` - safe packet must include full assigned content.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` - formal foundation precedes implementation work.
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - ops controls black-box configuration mutation; build controls case-authorized direct internals mutation.
- `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL` - original WI-5268 PAUTH/proposal approval only.
- `DELIB-202666272` - owner approved the first revised WI-5268 foundation packet and bounded PAUTH test-scope amendment.
- `DELIB-202666277` - owner approved the hash-bound WI-5268 foundation packet V2, metadata-v2, scoped build envelope, and isolated row-level finalization strategy.
- `DELIB-20265888` - prior dispatcher architecture decision: dispatch is a GT-KB-owned black-box service and harnesses are consumers only.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-004.md` - Loyal Opposition NO-GO findings addressed by this revision.

## Owner Decisions / Input

The owner replied `APPROVE WI5268 FOUNDATION PACKET V2` after being shown the V2 packet and hashes.

The approval was recorded as `DELIB-202666277` with content hash `e407fac783b685214d2bc26d39b6cb47feb1a251e5a98865bd25acba90386d68` and approval packet `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666277.json`.

The owner-approved hash-bound packet is:

- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET-V2.md`
- packet SHA256: `7FF8E08BCE5EF537FF0B559E70826D6A585E26399E33215F0CE8A50C4CA715A5`
- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json`
- metadata SHA256: `56BD5D5B17A495AAC84C5F10FA7A37EC9CE0DAECFD332272B060BDF2700F0604`

`DELIB-202666277` approves filing this corrected REVISED proposal and creating the V2 PAUTH. It does not approve implementation before Loyal Opposition `GO`, work-intent claim, and implementation-start evidence.

## Exact Formal Artifact Contents

All five proposed records are create-only formal artifacts with status `specified`, priority `P0`, scope `dispatcher-black-box-hardening`, testability `automatable`, and application scope `gtkb_platform`. The exact native content files were displayed to the owner and dry-run validated through `gt spec record --dry-run --json`.

| Artifact | Type | Title | Content File | SHA256 |
| --- | --- | --- | --- | --- |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | `design_constraint` | Dispatcher ordinary-worker black-box boundary | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md` | `be3ff577ee08df976542de1ef9dd75284cc24a1edee5eb5f11056c1933a02574` |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | `design_constraint` | Dispatcher worker-safe packet contract | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md` | `e6a58c02993a8a0350a0655b65ffd023f7402febf36bf5694b9dc845a88cd237` |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | `design_constraint` | Dispatcher activity-envelope authority split | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md` | `aa62220c8cbfd62ae43d48a61d6ca321c1f7cee4c803dfa474a5e575724d9d71` |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | `architecture_decision` | Use a worker-context facade for ordinary dispatcher work | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md` | `beffe6da9b2d75a471702a52d68cce865642fc77d34f617708f9e3577531a5b9` |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | `design_constraint` | Dispatcher black-box foundation-first project gate | `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md` | `b2c2ffcf047a7d33a95e73f90f2b46525b3b55c25e383b4ad603a8c0fefe4088` |

The exact metadata, tags, constraints JSON, affected-by links, source-path lists, supported assertion metadata, downstream gate targets, test binding route, and database finalization strategy are in `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json`.

## Requirement Sufficiency

New or revised requirement required before implementation.

Existing `ADR-DISPATCHER-ARCHITECTURE-001` establishes the dispatcher as a black box, but it does not encode the July 15 owner decisions about envelope-state ordinary workers, full assigned-content safe packets, ops/build authority split, scoped maintenance capabilities, raw bridge-file protection, foundation-first rollout, or the actual downstream enforcement targets.

This slice creates those authorities and the first enforcement gate only. The broader mechanics remain in child WIs after this slice is VERIFIED.

## NO-GO Remediation Map

### F1 - Supported Assertion Metadata And TEST-11423 Binding

`artifact-metadata-v2.json` replaces every unsupported `type: "python"` assertion with the supported assertion types `all_of`, `file_exists`, and `grep`. The manifest has no remaining `type: "python"` entry.

The executable verification carrier is still `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`, but it is now represented as supported assertion metadata plus a normal pytest command in the verification plan.

The governed append-only route for binding `TEST-11423` is `KnowledgeDB.update_test`, because the public `gt tests` surface is read-only. During implementation, after the focused pytest passes, Prime Builder will create a new test row version setting:

- `test_file`: `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`
- `test_function`: `test_wi5268_dispatcher_black_box_foundation`
- `last_result`: `pass`

The implementation report must include the exact pre/post `TEST-11423` rows and change reason.

### F2 - Mechanical Foundation-First Gate

The foundation-first condition is no longer only declarative. This proposal authorizes the exact production enforcement targets needed to reject downstream work before WI-5268 is terminal VERIFIED:

- `.claude/hooks/bridge-compliance-gate.py` rejects downstream WI-5269 through WI-5276 proposal filings that attempt implementation before the WI-5268 foundation is terminal VERIFIED or omit the required foundation citations.
- `scripts/implementation_authorization.py` rejects implementation-start authorization for downstream WI-5269 through WI-5276 when the foundation is not terminal VERIFIED.
- `scripts/implementation_start_gate.py` provides the protected-mutation backstop for the same foundation condition where start packets are consulted.
- `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py` exercises those production enforcement points, not only the proposed DCL text.

The public lifecycle CLI still does not expose a dependency-edge writer for existing work items, so this gate is the governed equivalent for this slice. A later governed dependency-edge writer may backfill explicit work-item dependency edges, but this slice does not depend on that future capability.

### F3 - Dirty DB Row-Level Finalization

The database fail-closed condition is acknowledged as already true: `groundtruth.db` is dirty in the live worktree. Version 005 therefore does not require a clean exclusive binary DB baseline before refiling.

Instead, `DELIB-202666277` approves an isolated row-level finalization strategy. Implementation must:

1. record pre-write `groundtruth.db` SHA256;
2. record exact pre-write current rows for the five proposed spec IDs and `TEST-11423`;
3. perform only the owner-approved `gt spec record` creates and `TEST-11423` `KnowledgeDB.update_test` row-version update;
4. record post-write `groundtruth.db` SHA256;
5. record exact inserted spec rows, approval packet paths, `TEST-11423` version delta, and change reasons;
6. avoid claims of hunk staging or binary rollback for `groundtruth.db`; and
7. use append-only corrective/superseding rows for rollback.

### F4 - Hash-Bound Metadata Manifest

`DELIB-202666277` hash-binds both packet files:

- `OWNER-REVIEW-PACKET-V2.md`: `7FF8E08BCE5EF537FF0B559E70826D6A585E26399E33215F0CE8A50C4CA715A5`
- `artifact-metadata-v2.json`: `56BD5D5B17A495AAC84C5F10FA7A37EC9CE0DAECFD332272B060BDF2700F0604`

The LO-identified unsupported assertion now lives only in superseded `artifact-metadata.json`; V2 uses `artifact-metadata-v2.json`.

## Specification-Derived Verification Plan

Implementation verification must include a spec-to-test mapping from each new foundation artifact to the focused executable test:

```text
python -m pytest platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py -q --tb=short
```

Expected: the test passes and proves:

- all five foundation artifacts exist with correct type, status, title, description content, tags/constraints, affected-by links, source paths, testability, supported assertion metadata, and approval evidence;
- `DELIB-202666277` is linked as owner approval evidence and hash-binds the owner packet V2 plus metadata V2;
- the ordinary-worker boundary is envelope-state based and applies to PB and LO ordinary workers;
- worker-safe packets include full assigned content and exclude raw internals;
- ops and build activity envelopes are non-interchangeable and build requires case-specific authorization;
- `.claude/hooks/bridge-compliance-gate.py`, `scripts/implementation_authorization.py`, and `scripts/implementation_start_gate.py` enforce the foundation-first gate for WI-5269 through WI-5276 until WI-5268 is terminal VERIFIED;
- `TEST-11423` is bound to `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py::test_wi5268_dispatcher_black_box_foundation`.

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

Expected: rows exist with the exact metadata in `artifact-metadata-v2.json`, and `TEST-11423` cites the executable test file/function.

Proposal/verdict preflights:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatcher-black-box-spec-foundation
```

Expected: applicability passes with no missing required specs and clause preflight reports zero blocking gaps.

## Implementation Start Gate

After GO, before any canonical write, Prime Builder must:

1. acquire matching bridge work-intent for `gtkb-dispatcher-black-box-spec-foundation`;
2. run `python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatcher-black-box-spec-foundation`;
3. record current bridge latest status as GO and confirm the GO responds to this `Version: 005`;
4. record `git status --short -- groundtruth.db .groundtruth/formal-artifact-approvals .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py`;
5. record SHA256 of `groundtruth.db`;
6. execute only the owner-approved row-level finalization and named enforcement/test target changes; and
7. stop immediately if implementation-start authorization rejects the scope or the row ledger reveals an unexpected conflicting current row for any of the five proposed spec IDs.

## Cross-Harness Disposition

This proposal targets `.claude/hooks/bridge-compliance-gate.py`, which is a harness-surface file. The behavioral disposition is parity-preserving:

- Claude Write/Edit bridge proposal paths continue to use `.claude/hooks/bridge-compliance-gate.py` as the live hook script.
- Codex helper-mediated bridge proposal paths already run the same `.claude/hooks/bridge-compliance-gate.py --audit-only` script before writing, so the foundation-first proposal gate applies to Codex bridge filing through the shared script.
- The proposed implementation must not introduce a Claude-only semantic branch. Any new WI-5268 foundation-first predicate must be implemented in the shared hook logic that both Claude and the Codex helper execute.
- No `.codex/hooks.json`, `.codex/gtkb-hooks/**`, `.claude/skills/**`, or `.codex/skills/**` mutation is requested in this slice.
- Antigravity, Cursor, Ollama, OpenRouter, API, and other harnesses remain out of direct hook-file scope for WI-5268; their ordinary-worker prompt/skill rewrites are deferred to child WIs and remain blocked by this foundation-first gate until WI-5268 is terminal VERIFIED.

No owner waiver is requested. The implementation report must explicitly show that the updated gate is exercised through the shared hook path and that the Codex helper audit path still passes for an allowed WI-5268 proposal while rejecting downstream WI-5269 through WI-5276 before the foundation is terminal VERIFIED.

## Risk / Rollback

Risk: a weak foundation could overexpose black-box internals or overconstrain legitimate ops/build maintenance. Mitigation: exact native content is owner-approved and LO-reviewed before canonical mutation, and the implementation scope is limited to the foundation and first enforcement gate.

Risk: the tracked SQLite database is binary and already dirty in the working tree. Mitigation: implementation uses the owner-approved row-level ledger strategy. The implementation report must carry pre/post DB hashes and exact inserted row/version evidence. Rollback is append-only corrective or superseding formal artifact versions, not binary DB blob revert over later unrelated changes.

Risk: enforcement could accidentally block legitimate future work. Mitigation: the gate is narrowly keyed to WI-5269 through WI-5276 and the WI-5268 terminal VERIFIED condition; ops/build activity-envelope work remains available when separately authorized by the appropriate PAUTH and bridge GO.

## Bridge Filing

This proposal is filed as `bridge/gtkb-dispatcher-black-box-spec-foundation-005.md`, preserving the append-only chain after `-001` NEW, `-002` NO-GO, `-003` REVISED, and `-004` NO-GO. No retired aggregate queue artifact is used or created.

## Recommended Commit Type

feat - the eventual implementation adds a new governed black-box foundation and enforcement gate for dispatcher-related work.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
