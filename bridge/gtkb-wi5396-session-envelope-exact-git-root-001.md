NEW

# WI-5396 - Contain session-close Git status to the exact project root

bridge_kind: prime_proposal
Document: gtkb-wi5396-session-envelope-exact-git-root
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5396

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_fab13_retention_policy.py"]

implementation_scope: exact-root and bounded session-close Git status attestation only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Prevent session close from running an unbounded `git status` against an ancestor
repository when the supplied project root is merely nested inside that
repository. The exact frozen harness-parity activity timed out before reaching
its parity assertions because a pytest temporary harness root lives below the
dirty GT-KB checkout. Git walked upward, selected the GT-KB root, and scanned
more than 1,000 entries while the envelope helper waited without a timeout.

Require exact top-level identity before collecting status, bound every Git
probe, return explicit fail-soft attestation when the supplied root is not an
independent repository, and preserve complete bounded status evidence for a
real exact root. Do not terminate, suspend, deprioritize, disable, or alter any
harness; this is deterministic process containment inside session evidence.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every implementation target,
  test artifact, and bridge record remains in-root under `E:/GT-KB`; temporary
  fixtures may model nested roots but create no live dependency outside it.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - session-close evidence must be
  durable, attributable to the correct project, and safe to produce.
- `ADR-ENVELOPE-META-MODEL-001` - closeout evidence remains part of the
  canonical session envelope rather than an unrelated ancestor project.
- `DCL-ENVELOPE-META-MODEL-001` - evidence payload and owning activity context
  must remain coherent.
- `GOV-WORK-TREE-HYGIENE-001` - status attestation must describe exactly the
  intended worktree without absorbing foreign dirt.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - Git evidence is meaningful only
  for the bound project/worktree identity.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - unavailable, non-exact,
  or timed-out status evidence must be explicit and fail-soft rather than hang.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - session close and every harness
  remain operational; unrelated Git and dispatch activity is unchanged.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - identical envelope behavior applies to
  all registered harnesses.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - frozen harness parity must
  complete and produce governed evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project scope does not waive
  GO, claim, start, verification, or Git-operation gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live authority
  is rechecked before protected mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - exact targets and
  governing envelope/Git requirements are linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work
  item, and targets are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - exact-root, nested-root,
  timeout, output-bound, and frozen acceptance cases are executed.
- `GOV-STANDING-BACKLOG-001` - WI-5396 durably owns this defect.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - failure evidence, work item,
  implementation, review, and finalization remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the new deterministic timeout creates
  a release-blocking hygiene lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect is preserved rather than
  hidden by increasing pytest timeouts.

## Prior Deliberations

- `DELIB-202666274` - supplies project-scoped modernization authority while
  preserving bridge, review, and exact Git gates.
- Owner directive, 2026-07-16 - fix the Git/console problem without making any
  harness less dispatchable; disabling a harness is unacceptable.
- WI-5371 - owns the corresponding exact-root repair in implementation
  authorization and demonstrates the same ancestor-repository failure class.
- WI-5396 live evidence - the frozen harness-parity activity timed out inside
  session-close status attestation before reaching parity assertions.

## Owner Decisions / Input

No new owner decision is required. The repair is fail-soft evidence collection
and does not modify Git state, terminate a process, change a harness, touch
dispatcher/TAFE/routing, stage, commit, push, deploy, release, or access
credentials.

## Requirement Sufficiency

Existing requirements are sufficient. Session-envelope durability, exact
worktree evidence, nonimpairment, and frozen parity already require this result.

## Proposed Scope

1. Resolve the supplied project root and query Git for its selected top-level
   path with a short fixed timeout.
2. If Git is unavailable, times out, fails, or selects a different top-level
   path, return explicit attestation fields with `available=false`,
   `dirty=null`, and a stable reason; do not run worktree status.
3. Only when top-level identity exactly equals the supplied root, run bounded
   short status collection with the existing line cap and truncation fields.
4. Handle timeout and process errors without escaping session close or leaving
   a descendant process running.
5. Preserve current clean/dirty semantics and bounded output for exact roots.
6. Add focused tests for exact clean/dirty roots, nested non-repository roots,
   top-level and status timeouts, output truncation, and stable result shape.
7. Rerun the unchanged frozen harness-parity command; do not edit its assertions
   or raise the repository-wide pytest timeout.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact worktree identity; `GOV-WORK-TREE-HYGIENE-001` | Create an exact temporary repository and a nested non-repository directory inside another repository. | Exact root reports its own clean/dirty state; nested root never scans or reports the ancestor. |
| Bounded evaluability | Simulate top-level and status subprocess timeouts and failures. | Helper returns promptly with stable unavailable reason and no exception from session close. |
| Output preservation | Create more changes than the current status line limit in an exact repository. | Dirty/count/truncation fields remain correct and output stays bounded. |
| Envelope durability | Close a session rooted at each fixture and inspect wrap-step evidence. | Close succeeds and status attestation remains structurally explicit in every case. |
| Frozen harness parity | Run the exact three-module harness-parity acceptance command unchanged. | The activity completes within its manifest timeout and reaches parity assertions. |
| Nonimpairment and scope | Inspect two-path diff, process state, and independent review evidence. | No harness/process/routing/Git mutation occurs; VERIFIED precedes finalization. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5396; frozen AT-HARNESS-PARITY timeout on 2026-07-17; WI-5371 related failure class","canonical_authority":"DCL-SESSION-ENVELOPE-DURABILITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"exact Git top-level identity followed by bounded status attestation","before_behavior":"Session close from a nested non-repository root silently selects the ancestor GT-KB repository and can hang past the per-test timeout while scanning foreign dirt.","after_behavior":"Only an exact project repository receives status attestation; nested, unavailable, failing, or timed-out roots return explicit bounded fail-soft evidence and session close continues.","self_descriptive_naming":"Exact-root and reason fields identify whether status evidence belongs to the supplied project.","obsolete_guidance_disposition":"No timeout is increased and no harness is disabled; implicit ancestor-repository fallback is rejected as invalid evidence.","history_preservation":"WI-5371 implementation-authorization scope, WI-5396 envelope scope, frozen timeout trace, focused tests, and independent verdict remain distinct.","baseline":{"harness_parity":"timed out before assertions","git_probe":"unbounded ancestor fallback","targets":"clean tracked files"},"expected_result":{"harness_parity":"completes","nested_root":"explicit unavailable without ancestor scan","exact_root":"bounded complete status evidence"},"rollback":{"instructions":"Revert only the two WI-5396 target hunks through a governed successor.","verification":"focused envelope retention tests plus unchanged frozen harness parity"},"hard_invariants":["no harness termination, suspension, deprioritization, disablement, or eligibility change","no dispatcher, TAFE, routing, role, or credential mutation","no Git index or worktree mutation","exact roots retain clean/dirty evidence","all probes are bounded","concurrent bytes outside exact targets are preserved"],"fail_closed_conditions":["top-level identity differs from supplied root","Git probe timeout or error","status output cannot be bounded","frozen assertions are weakened","GO, claim, start, or independent verification is absent"],"essential_context_preservation":"Retain project-root identity, session close continuity, bounded full status semantics, timeout reason, WI-5371 separation, and harness nonimpairment."}
```

## Acceptance Criteria

1. A nested non-repository project root never scans or reports its ancestor
   repository.
2. An exact repository root retains clean/dirty/count/truncation evidence.
3. Top-level and status probes are time-bounded and fail soft with stable reason.
4. Session close completes for unavailable, nested, failed, and timed-out Git.
5. No Git or harness process is left running by a timed-out probe.
6. The unchanged frozen harness-parity command completes and reaches assertions.
7. No harness or dispatcher/TAFE/routing/eligibility state changes.
8. Independent VERIFIED precedes exact mechanical finalization.

## Risk / Rollback

The principal risk is labeling a valid nested worktree unavailable. Exact Git
worktrees report their own top-level path, so they remain accepted; only a plain
directory borrowing an ancestor repository is rejected. Timeout handling must
not leave a child process; focused tests inspect completion and process state.
Rollback restores the two target hunks through a governed successor and reruns
focused envelope plus frozen parity evidence.

## Bridge Filing

File through the governed Codex non-bypass helper as the next numbered bridge
file. The numbered bridge file chain is append-only; no prior version is
deleted or rewritten. Deterministic TAFE routing remains external.

## Recommended Commit Type

`fix` - make session-close Git evidence exact, bounded, and nonimpairing.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
