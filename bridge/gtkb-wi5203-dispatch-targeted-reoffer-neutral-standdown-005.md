REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

# WI-5203 REVISED - Targeted dispatcher reoffer only

bridge_kind: prime_proposal
Document: gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown
Version: 005 (REVISED after NO-GO)
Responds to: bridge/gtkb-wi5203-dispatch-targeted-reoffer-neutral-standdown-004.md (NO-GO)
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5203-DISPATCH-RECOVERY-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5203
Linked Test: TEST-11357

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_bridge_dispatch_reset.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py"]

implementation_scope: canonical targeted reoffer control and focused tests only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Summary

This revision accepts the corrected NO-GO in full. It removes the rejected neutral NO-ACTION stand-down from the design, target paths, implementation scope, and verification plan. Latest `NO-ACTION` remains nonterminal Loyal-Opposition-actionable work and must receive a corrected governance-compliant verdict under `DCL-NO-ACTION-STATUS-SEMANTICS-001`. WI-5205 implemented the separate systemic consumer parity repair and reached independent VERIFIED commit `4abb6ed2`.

The only retained WI-5203 defect is the missing governed operator control for reoffering one exact recipient/document pair. The canonical soft reset intentionally preserves `last_dispatched_signatures_by_document`; a stale per-document signature can therefore suppress an open actionable thread indefinitely. This revision adds an audited, dry-runnable `gt bridge dispatch reset --recipient <recipient> --document <document>` path that clears only the selected document's dispatch signature and thread-reoffer record while preserving every unrelated recipient, document, launch-ledger, failure, and compatibility field.

## Finding Response

The `-004` finding is accepted:

- Neutral NO-ACTION completion is removed entirely.
- `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are removed from `target_paths`.
- No runtime verdict or completion semantics change is proposed.
- The retained targeted-reoffer control stays in the canonical dispatcher CLI and reset service.
- WI-5205 owns and has completed canonical NO-ACTION consumer parity.

## Proposed Behavior

1. Require both exact `--recipient` and normalized `--document` arguments for targeted reoffer mode.
2. Support `--dry-run` and JSON output through the existing canonical reset transaction.
3. Refuse mutation when the exact document has a live dispatcher lease.
4. Remove only that document from the selected recipient's `last_dispatched_signatures_by_document` map and from top-level `thread_reoffers`.
5. Clear aggregate signature fields only when they can suppress the selected document; preserve unrelated per-document signatures, launch ledger, last actual launch, last attempt, failure/backoff/circuit evidence, and every other recipient.
6. Return deterministic `changed`, `not_found`, `lease_held`, and invalid-argument outcomes with audit evidence.
7. Do not edit dispatcher runtime JSON or lease files directly; all mutation flows through `gt bridge dispatch reset`.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires canonical governed dispatcher mutation rather than direct JSON editing.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires deterministic eligibility and operator-safe recovery.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - forbids the removed neutral stand-down and preserves corrected-verdict routing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct append-only proposal, verdict, report, and verification artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project, work item, PAUTH, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-to-test evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - WI-5203 / TEST-11357 preserve the targeted-reoffer defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the reproduction, correction, revision, implementation, and verification traceable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the split from rejected semantics to the narrow lifecycle repair.

## Prior Deliberations

- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` - controlling owner decision; latest NO-ACTION requires corrected LO review.
- `DELIB-202666173` - owner directive to correct every defect discovered during genuine six-harness proof.
- `DELIB-202666172` - authorizes the WI-5199 H functional-proof sequence that needs targeted reoffer.
- `INTAKE-f8bc08a3` - establishes Dispatcher/Bridge CLI as the canonical mutating UI.
- WI-5205 / commit `4abb6ed2` - completed the separate NO-ACTION consumer parity correction.

## Owner Decisions / Input

Mike explicitly directed genuine A/B/C/D/F/H proof and correction of every discovered defect, recorded as `DELIB-202666173`. The active bounded authority is `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5203-DISPATCH-RECOVERY-20260711`. No new owner decision is required.

## Requirement Sufficiency

Existing requirements are sufficient. The dispatcher control-surface and centralized-service specifications define the operator-safe mutation; the canonical NO-ACTION DCL constrains the removed behavior; bridge, project-linkage, verification, backlog, and artifact-governance controls define the implementation lifecycle.

## Spec-Derived Verification Plan

1. Targeted dry-run returns the exact recipient/document mutation plan without changing state.
2. Apply removes only the selected document's per-document dispatch signature and thread-reoffer entry; unrelated documents and recipients remain byte-equivalent.
3. Matching live lease returns `lease_held` and changes nothing.
4. Missing recipient/document and partial argument pairs fail closed with deterministic JSON/CLI outcomes.
5. Aggregate signatures are cleared only when required to rearm the selected document; launch-ledger, `last_launch`, `last_attempt`, provider failure, retry, and circuit fields remain unchanged.
6. Existing soft and hard reset behavior remains compatible.
7. CLI tests prove the operation is available only through the canonical `gt bridge dispatch reset` surface.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
```

## Acceptance Criteria

- [ ] Exact recipient/document targeted reoffer is dry-runnable and audited.
- [ ] Apply removes only the selected document's signature and reoffer state.
- [ ] Matching live lease refuses mutation.
- [ ] Unrelated recipient/document state and WI-5208 launch-ledger evidence remain unchanged.
- [ ] Existing soft/hard reset behavior remains compatible.
- [ ] No NO-ACTION completion or dispatcher-runtime semantics change is present.
- [ ] Focused tests, lint, format, independent VERIFIED, and focused commit complete.

## Risk / Rollback

The risk is clearing too much state or bypassing a live lease. Exact recipient/document matching, dry-run, lease refusal, before/after audit evidence, and byte-equivalence assertions bound that risk. Rollback is one focused commit. Runtime JSON and lease files remain canonical control outputs, never direct edit targets.

## Recommended Commit Type

`fix` - adds a missing governed recovery operation for a demonstrated suppression defect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
