REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; automated bridge continuation

# Revised Dispatcher Black-Box Specification Foundation - Exact Targets And Sequenced Integration

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 007
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-006.md
Date: 2026-07-15 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666277.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET-V2.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md", ".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py"]

implementation_scope: governance_foundation_and_gate
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

Version 007 preserves the owner-approved V2 formal-artifact content, metadata, row-level database strategy, and foundation-first enforcement design from version 005. It changes only the two implementation boundaries identified by the version 006 NO-GO:

1. the mutable draft-directory wildcard is replaced by exact paths for the seven owner-approved V2 input files; and
2. WI-5268 implementation is sequenced after the current foreign changes in the two dirty shared targets reach a stable committed baseline.

No source, test, database, approval packet, or owner-approved V2 content is changed by this revision. No new owner decision is required.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher internals remain a black-box service boundary.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - ordinary workers consume governed packets rather than dispatch internals.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only revision and independent verdict authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the V2 PAUTH remains the exact operation-time envelope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass GO, claim, implementation-start, exact target, report, or verification gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - implementation must remain inside the PAUTH at operation time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all governing authorities remain linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and exact target paths are machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification remains executable and specification-derived.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the five formal artifacts use supported machine-evaluable assertions.
- `GOV-STANDING-BACKLOG-001` - `WI-5268` and `TEST-11423` remain the durable work/test authorities.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001` - foreign dirty work must not be absorbed into WI-5268.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE`
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET`
- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT`
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING`
- `DELIB-20260715-DISPATCHER-BLACKBOX-PROJECT-HOME`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES`
- `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL`
- `DELIB-202666272`
- `DELIB-202666277` - owner-approved V2 packet, V2 metadata, scoped build envelope, and row-level database strategy.
- `DELIB-20265888`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-006.md` - exact-target and dirty-shared-target findings addressed here.

## Owner Decisions / Input

The owner-approved hash-bound inputs remain unchanged:

- `OWNER-REVIEW-PACKET-V2.md` SHA256 `7FF8E08BCE5EF537FF0B559E70826D6A585E26399E33215F0CE8A50C4CA715A5`;
- `artifact-metadata-v2.json` SHA256 `56BD5D5B17A495AAC84C5F10FA7A37EC9CE0DAECFD332272B060BDF2700F0604`; and
- the five native formal-artifact drafts and hashes recorded in version 005.

`DELIB-202666277` authorizes the corrected proposal and bounded implementation after independent GO. This revision narrows target authority and adds a clean-baseline precondition, so it does not broaden that owner decision.

## Findings Addressed

### F1 - Wildcard Target Authorized Superseded And Unrelated Drafts

Corrected. The wildcard `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/*.md` is removed. The target list names exactly:

- `OWNER-REVIEW-PACKET-V2.md` and `artifact-metadata-v2.json` as immutable owner-approved inputs;
- the five exact native formal-artifact content drafts as immutable formalization inputs;
- the six exact formal-approval JSON outputs;
- `groundtruth.db` under the previously approved row-level ledger strategy; and
- the three enforcement files plus focused test that implement and verify the foundation-first gate.

The following existing files are explicitly excluded from mutation, staging, finalization, and WI-5268 evidence claims:

- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET.md`;
- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata.json`;
- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/WI5268-REVISED-FOUNDATION-PACKET-APPROVAL.md`;
- `.gtkb-state/propose-drafts/dispatcher-black-box-foundation/WI5268-FOUNDATION-PACKET-V2-APPROVAL.md`; and
- any file later added under the draft directory that is not an exact `target_paths` member.

The two V2 packet inputs and five native drafts are read/hash-verify inputs only. Implementation must fail closed if any owner-approved hash differs and must not rewrite those files.

### F2 - Dirty Shared Enforcement Targets Lacked Isolation

Corrected through explicit sequencing to a stable committed baseline.

Current inspection at repository HEAD `6d9a906cedb56002921ce04be65de3413d151dff` identifies the foreign changes:

- `.claude/hooks/bridge-compliance-gate.py` has 101 additions and 3 deletions after end-of-line normalization, worktree SHA256 `C30EA0A0C035AA75A9CEB56875EFEAC0A442E4D24680C6410B3E2268CE84AA87`, HEAD blob `5fb53b2fa8c50c2edd525d3a8a2c0cc436e45971`, and normalized foreign-diff object `fdc54ec49065626b5b38d1e85f72a69caa00c06f`. Its substantive delta is the modernization non-impairment proposal gate owned by terminal VERIFIED thread `gtkb-modernization-trust-enforcement-slice` and overlaps WI-5254's approved surface.
- `scripts/implementation_authorization.py` has 508 additions and 24 deletions after end-of-line normalization, worktree SHA256 `CC0C2DD861709826EE5755696BC10D1240DAC39024BF72F67C86185A925B57E3`, HEAD blob `0e2290034d64c8b84f6946bbf83c1e8404b37f3e`, and normalized foreign-diff object `8b68d6c0d9257db1dae12142eb9ab0ae117c6a42`. Its substantive deltas include VERIFIED WI-5220 start-packet APIs and active WI-5254 structured PAUTH-amendment work; WI-5254 is latest NO-GO and therefore not yet terminal.

Those bytes are foreign to WI-5268 and must not be absorbed, reverted, reformatted, staged, or attributed by this thread. WI-5268 implementation authorization may be created after GO, but protected mutation must not begin until both shared targets are clean relative to the then-current committed HEAD and their owning work has been finalized through its own governed lifecycle.

Implementation-start evidence must record:

1. `git status --short -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py` with no output;
2. the then-current HEAD commit and blob IDs for both files;
3. `git diff --check --` for both files with no foreign delta;
4. the implementation authorization packet bound to version 007 and its eventual GO; and
5. a fail-closed stop if either file becomes dirty again before the first WI-5268 write.

The implementation report must show the clean pre-start baseline, the WI-5268-only post-edit diff for both files, and the focused tests. This sequencing avoids a speculative clean candidate and makes every resulting hunk attributable to WI-5268.

## Exact Scope Classification

| Class | Exact paths | Disposition |
| --- | --- | --- |
| Immutable approved inputs | V2 owner packet, V2 metadata, five native drafts | Hash-verify only; no rewrite or staging claim |
| Generated formal evidence | Six exact `.groundtruth/formal-artifact-approvals/*.json` paths | Create/validate only as specified; the DELIB packet remains immutable if already present |
| Canonical row mutation | `groundtruth.db` | Owner-approved exact row ledger; no binary rollback or unrelated-row claim |
| Production enforcement | Three named gate/start files | Mutate only after GO, matching claim/packet, and clean committed shared-target baseline |
| Executable verification | `platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py` | Focused specification-derived test only |
| Superseded/unrelated draft files | Every unlisted draft-directory file | MUST_NOT_CHANGE and MUST_NOT_STAGE |

## Requirement Sufficiency

New or revised requirement required before implementation. Version 007 preserves the exact five owner-approved foundation artifacts and their requirement content from version 005. No additional requirement is introduced by narrowing target paths and sequencing shared-target integration.

## Specification-Derived Verification Plan

After independent GO and a matching implementation-start packet, run:

```text
python -m pytest platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py -q --tb=short
```

Expected: the focused test proves exact formal rows/metadata, owner-decision links, ordinary-worker and safe-packet boundaries, ops/build authority split, foundation-first enforcement at all three production gates, and the `TEST-11423` binding.

Validate each exact formal approval packet:

```text
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json
```

Read back the five formal artifacts and `TEST-11423` through the canonical `gt spec show` / `gt tests show` surfaces. Confirm exact approved metadata and append-only test binding.

Required quality gates:

```text
python -m ruff check .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py
python -m ruff format --check .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_dispatcher_black_box_spec_foundation.py
```

Proposal preflights must pass against version 007 with no missing required specifications and zero blocking clause gaps.

## Cross-Harness Disposition

The shared `.claude/hooks/bridge-compliance-gate.py` path is also executed by the Codex helper audit route. WI-5268 must implement one shared foundation-first predicate with no Claude-only branch. Other harness prompt/skill migrations remain deferred to WI-5269 through WI-5276 and remain blocked until this foundation is VERIFIED.

## Risk And Rollback

Risk: waiting for the dirty shared targets to reach a committed baseline may delay implementation. This is intentional fail-closed sequencing and is preferable to absorbing active WI-5254 or terminal-but-unfinalized work.

Risk: a future owner-approved input hash could drift. Implementation stops before mutation and returns to proposal review; it does not regenerate or silently replace owner-approved bytes.

Rollback for formal artifacts remains append-only correction or supersession. Source/test rollback is limited to the WI-5268-attributable hunks created from the clean committed baseline. `groundtruth.db` is never rolled back as a whole binary blob over later rows.

## Applicability Preflight

- packet_hash: `sha256:8c50acb2c9ea573e5e5f5f6df4a88d90c342ca5f532f2fc48d4d847da16aea63`
- bridge_document_name: `gtkb-dispatcher-black-box-spec-foundation`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-black-box-spec-foundation-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: `[]`
- warnings.spec_links_section: `harvested`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability Preflight

- Clauses evaluated: `5`
- must_apply: `3`
- may_apply: `2`
- not_applicable: `0`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`
- Result: `PASS`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
