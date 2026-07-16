NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed fleet stabilization; reasoning high

# Defect-Fix Proposal - WI-5254 PAUTH Amendment Evidence Preflight

bridge_kind: prime_proposal
Document: gtkb-wi5254-pauth-amendment-packet-preflight
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5254-PAUTH-AMENDMENT-PREFLIGHT-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5254

target_paths: ["scripts/implementation_authorization.py", "scripts/bridge_applicability_preflight.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py"]

## Claim

Prime Builder proposes a bounded fail-earlier correction for project-authorization specification amendments. A proposal that carries a structured replacement PAUTH envelope must prove that its cited, read-only owner evidence is valid and exactly covers the spec delta during proposal applicability checks and again during implementation authorization. The existing mutation-time database guard remains unchanged as defense in depth.

## Defect / Reproduction

WI-5232 carried an independent `GO`, a matching Prime Builder work-intent claim, and a successful implementation-start packet. Its approved `gt projects authorize` operation then failed before mutation because the `change_reason` omitted the formal owner-evidence path required by `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`.

The proposal, applicability preflight, clause preflight, and implementation authorization all accepted the incomplete amendment envelope. The defect therefore consumes independent LO and Prime claim/start capacity before surfacing a deterministic prerequisite that can be checked from the proposal itself. `TEST-11409` requires both the early rejection and the valid-evidence success path.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` already defines the exact owner-evidence requirement; WI-5254 changes enforcement timing and does not create a new approval policy.

## In-Root Placement Evidence

All implementation and test targets are inside `E:\GT-KB`. The implementation reads existing in-root proposal, MemBase, and owner-evidence state. It does not create, update, or authorize mutation of any formal owner-evidence file, `groundtruth.db`, dispatcher runtime JSON, or lease file.

## Proposed Scope

### IP-1 - Structured PAUTH amendment detection

Add one reusable validator in `scripts/implementation_authorization.py` that:

1. examines fenced JSON objects only, never free-form prose, for a PAUTH envelope containing `id`, `project_id`, `included_spec_ids`, and `excluded_spec_ids`;
2. loads the current authorization version read-only and computes the exact added and removed specification sets;
3. treats a missing current authorization, ambiguous multiple envelopes, malformed field types, or conflicting project/id metadata as a blocking diagnostic rather than guessing;
4. returns no extra requirement when the structured envelope does not change either specification set; and
5. for a real spec delta, parses the proposed `change_reason`, resolves the cited in-root owner-evidence file, validates its schema and owner provenance, and checks exact project/authorization/spec-delta coverage using the same shared helpers as the mutation-time database guard.

The validator must not mutate MemBase or the cited evidence file. The existing database check remains authoritative at effect time.

### IP-2 - Proposal applicability enforcement

Call the shared validator from `scripts/bridge_applicability_preflight.py`. Add a stable `blocking_errors` array to the packet and define `preflight_passed` as no missing required specs and no blocking errors. Preserve the existing packet hash, Markdown, and missing-spec fields while adding concise amendment-evidence diagnostics.

Update the live and scaffolded `bridge-compliance-gate.py` copies so pending proposal writes honor `preflight_passed=false` even when `missing_required_specs` is empty. Infrastructure execution/parsing failures keep the gate's existing fail-soft behavior; a successfully returned semantic denial fails closed.

### IP-3 - Implementation-authorization backstop

Run the same validator inside `create_authorization_packet` before any implementation-start packet is issued. This covers already-filed proposal chains such as WI-5232 and rejects incomplete amendment evidence before a claim-backed start packet can be written. Keep final operation-time PAUTH evaluation and the database mutation-time guard intact.

### IP-4 - Focused regression coverage

Use hermetic proposal, MemBase, and owner-evidence fixtures to cover missing path, out-of-root path, unreadable or malformed JSON, invalid packet schema, non-owner provenance, mismatched project/authorization/spec delta, ambiguous structured envelopes, no-spec-delta exemption, and exact valid coverage. Prove the live and scaffold hook copies reject a semantic applicability failure with no missing-spec gap.

## Cross-Harness Disposition

- Claude live hook: receives the semantic applicability denial directly.
- Codex A: the canonical non-bypass bridge writer invokes the same live hook in audit-only mode, so filing behavior remains equivalent.
- Dispatcher workers B/C/D/F/H: proposals they consume are already filed; implementation authorization supplies the same backstop independent of authoring harness.
- Scaffolded adopters: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` is updated and parity-tested with the live hook.
- No typed waiver is requested.

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - defines the owner-evidence prerequisite and exact spec-delta coverage that must be surfaced earlier.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the implementation-start path must continue evaluating the current PAUTH without weakening effect-time checks.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the structured replacement envelope is compared with the active PAUTH version.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - applicability remains relevance-complete and gains a second semantic blocking class.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries exact PAUTH, project, and WI linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - TEST-11409 maps the amendment prerequisite to executable tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation remains blocked pending independent GO, claim, and start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - early validation cannot mint authority or bypass the database effect-time guard.
- `GOV-ARTIFACT-APPROVAL-001` - existing owner evidence is validated read-only; this slice does not create or alter approval evidence.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex proposal filing reaches the same live compliance logic through the governed non-bypass helper.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the scaffold template changes with the live hook so adopter projection stays portable and root-contained.
- `SPEC-AUQ-POLICY-ENGINE-001` - only exact durable owner evidence satisfies the approval requirement; model inference does not.
- `GOV-STANDING-BACKLOG-001` - the observed late failure is preserved in WI-5254 rather than bypassed ad hoc.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - defect, test, PAUTH, proposal, implementation, report, and verdict remain linked lifecycle artifacts.

## Prior Deliberations

- `DELIB-202666173` authorizes correction of defects discovered during the active A/B/C/D/F/H governed fleet proof.
- `DELIB-202666140` records the verified WI-5189/WI-5195 corrective PAUTH amendment and its exact owner-evidence precedent.
- `DELIB-202665933` rejects scope-defective canonical-authority carrier work.
- `DELIB-20265493` records the earlier narrative evidence scope correction.
- `DELIB-20263210` authorizes the bridge applicability-preflight heading correction and confirms pre-filing enforcement as the intended surface.
- `bridge/gtkb-wi5232-wi5216-pauth-registered-vocabulary-001.md` is the concrete accepted-then-late-rejected reproduction.

## Owner Decisions / Input

- `DELIB-202666173` is the owner directive to correct every proof-blocking defect found during fleet stabilization.
- No new owner evidence is created or inferred by this proposal. Any future PAUTH spec amendment still requires separately presented, transcript-captured, owner-approved evidence that exactly covers that amendment.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| TEST-11409 missing-evidence rejection | `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short` proves a structured spec amendment without valid owner evidence is rejected before packet issuance. |
| Exact coverage and no-delta behavior | The same focused suites prove exact valid coverage passes and an unchanged spec set does not invent an additional prerequisite. |
| Hook semantic denial | `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short` proves both live and scaffold hooks reject `preflight_passed=false` with an empty missing-spec list. |
| Existing mutation-time guard | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short` preserves the database/effect-time PAUTH amendment checks. |
| Static quality | `python -m ruff check scripts/implementation_authorization.py scripts/bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`. |

## Acceptance Criteria

- A pending proposal with a structured PAUTH spec delta and missing, malformed, non-owner, out-of-root, or non-covering owner evidence fails the applicability preflight with a stable actionable diagnostic.
- A bridge proposal write is denied on that semantic failure even when all required specification links are present.
- An already-filed GO chain with the same defect cannot receive an implementation-start packet.
- Exact valid evidence passes both proposal and start checks; a structured envelope with no spec delta remains unaffected.
- The database mutation-time guard remains unchanged and all focused regression tests pass.
- No owner-evidence file, `groundtruth.db`, dispatcher state, lease, harness eligibility, runtime allowance, Git remote, or unrelated dirty worktree content is mutated.

## Risks / Rollback

The primary risk is false-positive amendment detection from illustrative JSON. Fenced-object-only parsing, exact required keys, ambiguity rejection, and explicit no-delta behavior bound that risk. The second risk is live/template hook drift; parameterized parity tests cover both copies. Rollback is a focused revert of this slice; the unchanged database guard continues to fail closed at mutation time.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `scripts/bridge_applicability_preflight.py`
- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`
- `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`

## Recommended Commit Type

`fix`
