REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5458 v2 - Validated Proposal PAUTH Selection And Currentness - Revised

bridge_kind: prime_proposal
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 003
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-002.md
Date: 2026-07-29 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

KB-mutation completeness: this implementation performs no MemBase mutation.
It does not write `groundtruth.db`; it changes only the three declared
source/test files, and runtime transaction behavior is exercised against
isolated test databases.

## Claim

Implement the remaining WI-5458 proposal-filing repair in exactly three files.
The canonical command gains a validated explicit project-authorization selector,
filters currentness before ranking, evaluates operation and exact target classes
without fallback broadening, and emits complete machine-readable decision
evidence. The implementation also preserves the owner-approved
`--create-missing-state` route by deriving a least-privilege authorization from
the exact normalized target classes and by proving every denial is side-effect
free.

The structurally invalid predecessor thread remains untouched. This strict-valid
v2 chain is the executable continuation.

## Requirement Sufficiency

Existing requirements sufficient. This revision changes no authorization model
and grants no implementation authority. It makes the existing operation-time
contract executable at the proposal-filing enforcement point. Cross-gate parity
remains owned by WI-5178.

## NO-GO v002 Finding Disposition

| Finding | Revision disposition |
|---|---|
| F1, spec-to-test mapping | Replaced the thematic verification table with explicit specification-ID rows covering all 17 linked specifications. Added a cross-harness disposition. |
| F2, create-missing-state contradiction | Added an explicit disposition. Auto-created PAUTH classes are the exact canonical target classes plus bridge and metadata, derived only after owner-decision and spec validation. Source/test targets therefore do not run under a bridge-and-metadata-only envelope. |
| F2 secondary, durable writes before denial | Membership and PAUTH creation move behind complete in-memory validation. A denied run leaves zero new MemBase rows, claim, packet, preflight call, writer call, or bridge file. |
| F3, prune versus deny | Pruning is limited to well-formed expired or superseded candidates. Malformed currentness, unresolvable owner authority, forbidden operation, disallowed target class, and invalidation-input defects deny the whole request without fallback. |
| F4, incomplete evidence object | Added acting session/role, bridge/WI/spec identity, currentness inputs, owner decision, invalidation inputs, and candidate disposition fields. |
| F5, currentness blast radius | Recorded the measured 577 active / 21 expiring rows and the governed renewal/new-bounded-PAUTH recovery route. |

## Proposed Implementation

### 1. Validated explicit selector

Add `--project-authorization <PAUTH-ID>` to
`gt bridge file-implementation-proposal` and carry it through
`FilingRequest`, resolution, generated proposal metadata, `FilingResult`, JSON
output, and text output.

Automatic deterministic ranking remains the default. An explicit selector may
choose only among equally best-ranked current covering candidates. It cannot
select a lower-specificity or broader authorization while a more-specific
candidate exists.

### 2. Currentness and deterministic failure precedence

Build a current candidate set before ranking. Apply these outcomes exactly:

| Candidate condition | Automatic mode | Explicit selector |
|---|---|---|
| Well-formed expired row | Prune, disclose reason | Deny selected stale row |
| Well-formed superseded row | Prune, disclose reason | Deny selected stale row |
| Unknown row or cross-project row | Not eligible | Deny |
| WI/spec exclusion or non-covering row | Not eligible | Deny |
| Malformed expiry/currentness | Deny whole request | Deny |
| Missing or unresolvable owner decision | Deny whole request | Deny |
| Forbidden requested operation | Deny whole request; do not try broader PAUTH | Deny |
| Disallowed canonical target class | Deny whole request; do not try broader PAUTH | Deny |
| Missing or inconsistent invalidation input | Deny whole request | Deny |

Exclusions and forbidden-operation rules remain dominant. A narrow candidate
that denies the operation cannot be discarded in order to obtain broader
authority from a fallback candidate.

### 3. Canonical operation and target evaluation

Reuse
`groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`
and its root-bound target classifier. The operation is
`bridge_proposal_filing`. Normalize all target paths before project-state
mutation, content construction, candidate preflights, writer invocation, or
bridge publication. No second taxonomy is introduced.

### 4. Create-Missing-State Disposition

Preserve the owner-approved route with least privilege:

1. Resolve the owner-decision deliberation and approved linked specifications.
2. Normalize and canonically classify every exact target path in memory.
3. Construct an in-memory candidate authorization scoped to the exact work item,
   approved specs, operation, and required target classes. Its allowed classes
   are `bridge`, `metadata`, plus only the canonical classes required by the
   exact targets. For the existing source-target fixture that means `source` is
   present; a bridge-and-metadata-only authorization never authorizes source or
   test work.
4. Run complete currentness, operation, target-class, exclusion, and evidence
   validation against that candidate before durable mutation.
5. Only after validation succeeds, create the membership and PAUTH in one
   bounded MemBase transaction, then build proposal content and run preflights.

The existing positive create-missing-state test remains a success case but now
asserts the derived `source` class and operation-time evidence. New negatives
prove that missing owner authority, missing approved specs, malformed target
classification, or a denied envelope creates zero membership and zero PAUTH
rows. The implementation does not grant classes unrelated to the exact target
set.

### 5. Side-effect boundary

All selector, currentness, owner-authority, operation, target-class, and
create-missing-state validation failures occur before:

- MemBase membership or PAUTH insertion;
- work-intent claim or implementation packet creation;
- proposal content or candidate-preflight invocation;
- bridge writer invocation or bridge-file creation.

Tests use recording preflight and writer probes plus before/after MemBase row
counts. A denial must leave every counter and target path unchanged.

### 6. Complete decision evidence

Return and render one stable decision object containing:

- selector mode, requested ID, selected ID, all candidate IDs/ranks, and each
  candidate disposition;
- authorization ID/version/status, expiry, supersession state, owner-decision
  deliberation ID, normalized envelope hash, and invalidation inputs;
- acting exact session context ID and resolved role;
- project, work item, bridge slug/version candidate, linked specifications,
  and exclusions;
- normalized operation, each normalized target path/class, allowed classes,
  forbidden operations, evaluator/taxonomy versions and hashes;
- decision time, decision, stable reason code, and recovery route.

Generated proposal metadata, JSON output, and text output disclose the same
decision identity. No output relies on body-inferred session identity.

## Cross-Harness Disposition

The implementation is in the shared Python `gt` CLI and proposal-filing
service. No harness-specific hook, prompt, adapter, or dispatcher route changes.
The same JSON decision object is therefore the parity surface for Claude,
Codex, Cursor, Antigravity, Ollama, OpenRouter, Goose, and Alibaba callers that
invoke the canonical CLI. Tests invoke the production CLI entry point and pin
identical automatic/explicit selection semantics in text and JSON modes.
Generated skill adapters are unchanged because no skill source changes.

## Currentness Blast Radius And Recovery

The v002 review measured 577 active PAUTH rows and 21 rows carrying expiries,
with sampled expiries already past. This implementation may cause work covered
only by a stale row to fail closed. The diagnostic must name the stale PAUTH
and recovery route: obtain owner-approved renewal or create a new bounded PAUTH
through the governed project-authorization service. There is no stale-row
bypass and no mutation of PAUTH state in this WI.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Specification-Derived Verification Plan

| Linked specification IDs | Executable verification |
|---|---|
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Exact-singleton, bounded multi-WI, unrestricted fallback, explicit exclusion, cross-project, unknown, and equal-rank fixtures; assert selected envelope and decision evidence. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Active, expired, superseded, malformed currentness, unresolvable owner decision, forbidden operation, disallowed target class, narrow-deny-plus-broad-fallback, and invalidation-input fixtures; every denial asserts zero side effects. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Candidate and live applicability/clause preflights; generated proposal asserts exact project/PAUTH/WI/target/spec metadata; implementation report maps every linked spec to executed evidence. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Query WI-5458 bridge/backlog state before report and prove WI-5166 does not proceed until terminal VERIFIED. |
| `ADR-CROSS-HARNESS-PARITY-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Invoke the shared CLI in automatic and explicit modes; compare text and JSON decision identity; confirm no harness-specific source or generated adapter drift. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Preserve the old invalid chain, this v2 chain, WI history, and every finding disposition; no hidden work or lifecycle mutation outside the report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Preserve project-root normalization and Agent Red out-of-scope rejection fixtures. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact three-file `git status`, diff, and `git diff --check`; no unrelated tracked mutation. |

Required commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2
```

## Acceptance Criteria

1. This v2 chain remains strict-valid and receives independent GO before source
   or test mutation.
2. Explicit selection is limited to equally best-ranked current covering
   candidates and passes the complete operation-time evaluator.
3. Only well-formed expired/superseded candidates are pruned. Malformed
   currentness, unresolvable owner authority, forbidden operation, disallowed
   target class, or inconsistent invalidation input denies globally without
   fallback.
4. Create-missing-state derives exact least-privilege target classes, never
   authorizes source/test through bridge+metadata alone, and leaves zero durable
   rows on denial.
5. Every authorization denial leaves zero MemBase, claim, packet, preflight,
   writer, and filesystem side effects.
6. Generated metadata, JSON, and text expose the complete decision-evidence
   object, including acting session/role and currentness/invalidation inputs.
7. Existing deterministic specificity, insertion-order, root-boundary, and
   successful create-missing-state behavior remains passing with strengthened
   assertions.
8. All 17 linked specifications map to the verification table above; focused
   pytest, Ruff check, Ruff format check, diff check, and both preflights pass.
9. Only the three declared target files change. No PAUTH/project/backlog,
   dispatcher/TAFE, harness, credential, external, Git commit/push, deployment,
   release, or cleanup operation is in implementation scope.
10. A fresh implementation report receives independent terminal VERIFIED
    before WI-5458 resolves or WI-5166 proceeds.

## Prior Deliberations

- `DELIB-20266083` - restrictive `included_work_item_ids` semantics.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded WI-5458 repair authority.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - dispatcher mutation remains prohibited.
- `DELIB-20263760` - project-membership validation posture.
- `DELIB-20264663` - project-authorization lifecycle currentness.
- `DELIB-20264465` - validate candidate state before durable write.
- `DELIB-202665533` - single-source authority resolution precedent.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-002.md` - controlling NO-GO and bounded findings.

## Intuitiveness / Non-Impairment Disposition

The common path remains one command with automatic selection. Ambiguity names
the equal-ranked candidates and offers a validated selector. Stale or denying
authority produces a specific recovery message before side effects. The
create-missing-state route remains usable with exact least-privilege classes.
Ordinary content and owner hand edits are not invalidated by missing notation;
this slice governs only which authorization a proposal-filing transaction may
cite.

## Risks

- Explicit selection could broaden authority. Mitigation: equal-best-rank only,
  full evaluator, exclusions and forbidden operations dominant.
- Candidate pruning could fall through to broader authority. Mitigation: prune
  only expired/superseded; all substantive envelope denials stop globally.
- Derived create-missing-state classes could overgrant. Mitigation: canonical
  classifier, exact target set, owner decision, and negative no-extra-class
  assertions.
- Currentness enforcement will expose 21 stale active rows. Mitigation: bounded
  diagnostics and governed renewal/new-PAUTH route, never bypass.
- Semantics could diverge from WI-5178. Mitigation: reuse the canonical evaluator
  and leave cross-gate parity to WI-5178.

## Recommended Commit Type

`fix(bridge)`

## Authority Boundary

This REVISED proposal grants only independent Loyal Opposition review
actionability. It authorizes no source/test mutation, implementation-start
packet, MemBase mutation, bridge verdict, Git action, dispatcher/TAFE or harness
change, credential operation, cleanup, deployment, release, or peer-worker
launch. Implementation remains paused until independent GO plus an exact-session
claim and implementation-start packet.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
