NEW

Document: agent-disposition-wi4590-post-action-receipts-slice1
Version: 001
Status: NEW
Date: 2026-06-17
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4590
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Post-action audit receipts - Slice 1 (receipt contract: schema, validator, writer, evidence correlation)

## Summary

Implement the foundational slice of the post-action audit-receipt subsystem: a
durable receipt CONTRACT (schema + validator + writer) plus a read-only
evidence-correlation helper. A post-action receipt is a write-only audit
artifact recorded after an agent performs a mutation; it links the initiating
authority (owner directive / PAUTH / DELIB), bridge thread and version, work
item, target paths, commands run, verification evidence, residual dirty-tree
scope, and a commit/push-appropriateness judgment, plus the authoring harness
provenance. This slice defines the contract that the already-VERIFIED WI-4588
protected-mutation guard defers receipt EMISSION to, and that later sub-slices
wire into the six mutation classes and the cross-harness mutation paths.

Per-class emitters, cross-harness hook/Bash emission integration, and
dispatch-telemetry unification are explicitly DEFERRED to later WI-4590
sub-slices (matching the WI-4588 slice-1 precedent), keeping this slice bounded
and reviewable.

## Specification Links

- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the WI source constraint;
  receipts are durable post-execution verification evidence linking commands run
  and observed results, and this slice's tests derive from it.
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001 - each receipt carries accurate authoring
  harness/model/session provenance; a validation rule enforces the provenance
  fields.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - receipts preserve
  post-action evidence as durable artifacts rather than chat-only context.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the receipt subsystem and
  its decision trail are preserved as durable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - receipts are a new durable
  artifact class produced on mutation events, exercising artifact-lifecycle
  triggers.

## Prior Deliberations

<!-- reviewed -->

- DELIB-20263455 - owner authorization for the Agent Disposition and Protocol
  Enforcement project, its PAUTH, and the ranked child work items including
  WI-4590 (post-action audit receipts) as child #3.
- agent-disposition-protocol-enforcement-umbrella (VERIFIED, GO@-004) -
  planning-only umbrella that sequenced WI-4590 and requires each child slice to
  file its own concrete proposal, target paths, verification plan,
  implementation-start packet, work-intent claim, report, and LO verification.
- agent-disposition-wi4588-protected-mutation-guard-slice1 (VERIFIED) - the
  protected-mutation guard returns structured reasons suitable for later hook
  receipts and defers receipt EMISSION to WI-4590; this slice supplies the
  receipt contract that handoff requires.
- No direct prior deliberation exists on the post-action receipt schema itself;
  the nearest decisions are the umbrella authorization and the WI-4588 guard
  handoff above.

## Requirement Sufficiency

Existing requirements sufficient. The slice implements the owner directive
S20260616-CODEX-INTERACTIVE ("all actions must leave durable audit evidence
after execution") and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, scoped by
the umbrella GO@-004 and DELIB-20263455. It introduces no new or revised
requirement or specification, no policy or architecture sign-off, and no
destructive, deployment, or credential action (receipts are write-only audit
artifacts that RECORD mutations; they do not perform any external mutation).

## Problem / Background

Agent mutation evidence in GT-KB is real but fragmented: implementation-start
packets (scripts/implementation_authorization.py and the implementation-
authorizations runtime dir), work-intent claims (the SQLite work_intent_claims
table via scripts/bridge_work_intent_registry.py), formal-artifact-approval
packets (the formal-artifact-approvals runtime dir), bridge thread/version
state, owner directive / PAUTH / DELIB linkage, and live git dirty-tree scope
each live in a different place. After an agent performs a mutation there is no
single durable record that correlates them and states whether a
commit/push is appropriate. The WI-4588 guard slice already produces structured
reasons "suitable for later hook receipts" but defers the receipt itself to
WI-4590. This slice supplies the missing unified receipt contract.

## Proposed Change

Add a single new module scripts/post_action_receipt.py providing:

1. A frozen receipt dataclass (PostActionReceipt) with fields: receipt_id,
   generated_at, mutation_class (one of file, config, bridge, membase,
   cloud_deployment, external_service), action_summary, initiating_authority
   (owner-directive id / PAUTH id / DELIB id), bridge_thread, bridge_version,
   work_item, target_paths (list), commands_run (list), verification_evidence
   (commands + observed results + preflight/packet hashes), residual_dirty_tree
   (list of dirty paths in scope), commit_push_recommended (bool) with
   commit_push_rationale, and the authoring provenance fields (author_identity,
   author_harness_id, author_session_context_id, author_model).
2. validate_receipt(receipt) -> list[str]: returns validation errors without
   mutating anything; enforces required fields, the mutation_class vocabulary,
   presence of an initiating_authority, and the provenance fields
   (GOV-DOCUMENT-AUTHOR-PROVENANCE-001). require_valid_receipt raises on errors.
3. write_receipt(receipt, *, project_root=None): validates then atomically
   writes the receipt JSON to a runtime evidence directory under
   .gtkb-state/post-action-receipts/<UTC-date>/<receipt_id>.json. Write-only
   audit artifact; never overwrites an existing receipt_id (raises instead).
4. gather_evidence(...): a READ-ONLY correlation helper that assembles a
   candidate receipt from the existing fragmented sources - the session's
   work-intent claim, the live implementation-start authorization packet, an
   applicable formal-artifact-approval packet, and the current git dirty-tree
   (git diff --name-only HEAD --) - so callers do not re-implement evidence
   collection. It performs no mutation and tolerates missing sources
   defensively.

target_paths: ["./scripts/post_action_receipt.py", "./platform_tests/scripts/test_post_action_receipt.py"]

## Verification Plan (spec-derived)

- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 -> tests assert: validate_receipt
  rejects a receipt missing any required field; write_receipt produces a
  schema-valid receipt that round-trips (read back equals written); gather_evidence
  correlates a fixture work-intent claim + implementation-start packet + git
  dirty-tree into a candidate receipt.
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001 -> test asserts a receipt missing the author
  provenance fields fails validation.
- Negative paths -> tests assert an unknown mutation_class is rejected, a missing
  initiating_authority is rejected, and write_receipt refuses to overwrite an
  existing receipt_id.
- Isolation -> test asserts write_receipt writes only under
  .gtkb-state/post-action-receipts/ and performs no MemBase/bridge mutation.
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_post_action_receipt.py -q ; plus ruff check and
  ruff format --check on the new files.

## Risk / Rollback

- Risk: the correlation helper reads several existing evidence formats that may
  drift. Mitigation: defensive, tolerant reads (missing/unreadable sources yield
  absent fields, not failures); tests fixture each source. The helper is
  read-only, so a misread degrades the receipt's completeness but cannot corrupt
  any source.
- Rollback: delete the two new files; receipts are regenerable runtime evidence
  under .gtkb-state/ (no canonical MemBase or bridge state is written). No data
  migration.
- Blast radius: one additive module plus its test suite; read-only correlation
  from existing sources; no change to any existing mutation path (emitter
  wiring is a later deferred sub-slice).

## Authorization

Authorized for proposal filing by PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-
ENFORCEMENT-UMBRELLA (active; lists WI-4590 in the ranked child set; owner
DELIB-20263455). Per the umbrella GO@-004 conditions, this child proposal
carries its own narrow target_paths and verification plan; source/test
implementation proceeds only after this child receives its own Loyal Opposition
GO and a work-intent claim is taken (standard bridge protocol). The parent
umbrella GO is NOT cited as implementation authority. No fresh owner decision is
required (the project, PAUTH, and ranked children were owner-authorized via
DELIB-20263455).

## Recommended Commit Type

`feat:` - a net-new post-action receipt subsystem module plus tests, not a
defect repair or refactor.
