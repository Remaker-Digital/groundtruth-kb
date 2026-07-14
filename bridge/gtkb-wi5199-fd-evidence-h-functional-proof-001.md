NEW

# WI-5199 - F/D dispatched evidence and one genuine H Loyal Opposition review

bridge_kind: prime_proposal
Document: gtkb-wi5199-fd-evidence-h-functional-proof
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: GPT-5 family (Codex)
author_model_version: not exposed by harness
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5199-H-FUNCTIONAL-PROOF-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5199

target_paths: ["groundtruth.db", "harness-state/harness-registry.json"]

implementation_scope: governed dispatcher configuration and functional evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Disposition WI-5199 with real dispatched-work evidence for the two
guard-adapter cloud harnesses and produce the first genuine committed verdict
from Alibaba Cloud Studio/H after the VERIFIED WI-5198 native-hook repair.

OpenRouter/F and Ollama/D are not exposed to WI-5198 because they use the
guard-adapter-floor path, not `invoke_native_hooks`. Both already have committed
tool-using Loyal Opposition verdicts, but current operating state differs:

- F has multiple committed dispatched verdicts, including substantive NO-GO
  `bridge/gtkb-work-tree-hygiene-slice-d-governance-spec-041.md` and VERIFIED
  `bridge/gtkb-envelope-sharding-taxonomy-baseline-006.md`. The latter is in
  commit `5a3450eedf30e497bc4ff721ddf751f5a8bfbc3b`.
- D has committed dispatched VERIFIED verdict
  `bridge/gtkb-wi5049-headless-sweep-git-and-audit-guard-repair-004.md` in
  commit `30d6abcb9cf9d3c1af68121b83ac9e245477f959`.
- D is nevertheless degraded by the later real dispatch
  `2026-07-10T17-38-49Z-loyal-opposition-D-8077e1`, which exhausted the
  route-configured 200-turn budget after about 1226 seconds and tripped the
  circuit breaker. This proposal records that as an unresolved follow-on
  defect; it does not implement a D source/config repair.

H had zero committed verdicts before WI-5198 and was made ineligible after
repeated real-review failures. WI-5198 is now VERIFIED and committed at
`4442943cb71f56be1b874296f5d5bc19f0161fe9`. This proposal uses the governed
dispatcher control surface to route H one real review of this thread's
implementation report. A READY/canned smoke is explicitly insufficient.

## Proposed Change

1. Preserve the F and D committed verdicts, commit hashes, live role state, and
   retained dispatcher failure evidence in the implementation report.
2. After independent GO, acquire the exact `go_implementation` claim and
   implementation-start packet for the MemBase harness rows and generated
   `harness-state/harness-registry.json` projection.
3. Use only `gt bridge dispatch config set-eligibility` transactions. Never
   edit `rules.toml` directly.
4. Apply the proof sequence in partition-safe order:
   - set H `can_receive_dispatch=true`;
   - set B `can_receive_dispatch=false`;
   - verify the selected Loyal Opposition recipient is H;
   - file the post-implementation report, creating real NEW review work;
   - wait until dispatcher telemetry shows an in-flight `loyal-opposition:H`
     worker for the report;
   - immediately set B `can_receive_dispatch=true`;
   - then set H `can_receive_dispatch=false`;
   - verify B is again the selected normal Loyal Opposition recipient.
5. If H does not launch or exits unsuccessfully, restore B first, preserve the
   failure telemetry, and return this thread for NO-GO/defect remediation.
6. Require H's real worker to inspect the report and evidence, run the mandatory
   preflights, and publish a canonical committed GO/NO-GO/VERIFIED verdict.
7. Record D's later 200-turn exhaustion as the next exact repair candidate.
   No D or F source/config mutation is authorized by this thread.

## Cross-Harness Disposition

- A remains the interactive Prime Builder and authors this proposal/report.
- B performs independent proposal review before any dispatcher mutation and is
  restored as the normal LO recipient immediately after H is in flight.
- F is functionally proven for LO by committed real verdicts; current dispatch
  ineligibility is operating policy, not evidence that the adapter never worked.
- D is functionally proven for bounded LO work but classified DEGRADED because
  a later 200-turn real review exhausted its budget. That flaw remains open.
- H must produce a new real committed verdict after WI-5198; only that closes
  the functional-proof portion of this slice.
- C, E, and G are not mutated by this proposal.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - real artifact-deposit dispatch and
  its audit trail are the only accepted functional-proof path.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - all eligibility changes must use
  governed `gt bridge dispatch config` transactions.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - direct registry, database, or
  `rules.toml` editing is prohibited.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - functional harness claims require
  machine-checkable capability and governed execution evidence.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - H is the native-full,
  Anthropic-compatible non-GUI adopter being proven.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - F and D retain their separate fail-closed
  mutating-tool guard floor.
- `ADR-CROSS-HARNESS-PARITY-001` - harness parity must be assessed by role and
  operational capability rather than vendor labels.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - evidence must distinguish
  supported, degraded, suspended, and unproven surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO, role-correct report/verdict
  authorship, and append-only lifecycle evidence are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing carriers
  and evidence are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, work
  item, PAUTH, and target path metadata are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute
  the mapped control-plane and artifact checks before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - WI-5199 remains the authority for this bounded
  functional-proof check; D repair remains tracked rather than hidden.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - owner decision, PAUTH, proposal,
  report, dispatch evidence, and verdict form one durable graph.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the discovered D flaw receives an
  explicit lifecycle disposition.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - observed failures trigger durable
  defect/proposal handling rather than informal notes.

## Prior Deliberations

- `DELIB-202666172` - owner authorization for WI-5199 plus one genuine H proof
  dispatch, with B routing restored afterward.
- `DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION` - bounded owner
  authorization for the native-hook empty-allow repair now VERIFIED.
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` - selected H
  as the non-GUI replacement and retired G.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` - placed native
  hook behavior in the shared cloud-harness base.
- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - prior owner goal to test and
  repair A/C/D/F in their assigned roles.
- `bridge/gtkb-wi5198-native-hook-empty-allow-004.md` - independent VERIFIED
  verdict for H's shared-base blocker.
- `bridge/gtkb-wi5060-ollama-route-max-turn-budget-004.md` - VERIFIED increase
  of D's route budget to 200 turns; the later exhaustion shows residual debt.
- `bridge/gtkb-envelope-sharding-taxonomy-baseline-006.md` - committed real F
  verification evidence.
- `bridge/gtkb-wi5049-headless-sweep-git-and-audit-guard-repair-004.md` -
  committed real D verification evidence.

## Owner Decisions / Input

- `DELIB-202666172` records Mike's explicit response
  `Authorize WI-5199 + H proof` to the standalone owner-action request.
- The active exact PAUTH is
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5199-H-FUNCTIONAL-PROOF-20260711`.
- D/F source or config implementation is expressly excluded. A later exact
  owner authorization and bridge cycle is required for any D repair.

## Requirement Sufficiency

Existing requirements sufficient. The centralized dispatcher service/control
specifications, harness onboarding/parity carriers, Alibaba adoption ADR, and
WI-5199 acceptance criteria fully specify this evidence-and-routing slice.

## Spec-Derived Verification Plan

| Governing specification | Executed evidence required | Expected result |
| --- | --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` | Run `set-eligibility` dry-runs, then live transactions only after GO; inspect MemBase/projection transaction output and final state. | No direct file edit; each transaction validates; final state is B=true and H=false. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | `gt bridge dispatch report --json --compact`, retained dispatch result, H verdict file, and Git commit lookup. | A real `loyal-opposition:H` worker launches for this report, exits successfully, and publishes a committed canonical verdict. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Inspect H verdict metadata and worker result, including `author_harness_id: H`, non-canned substantive review, canonical bridge status, and exit status. | H demonstrates assigned-role capability through real tool-using review. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001`, parity carriers | Inspect committed F/D verdicts and D retained failure record. | F is proven; D is proven-but-DEGRADED, with the later max-turn defect explicitly carried forward. |
| Bridge/project/lifecycle carriers | Both mandatory preflights, exact PAUTH/project/work-item linkage, claim, implementation-start packet, and one-path diff. | No missing specs, no blocking clause gaps, and no out-of-scope path. |
| Transaction regressions | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py -q --tb=short` | Governed eligibility transactions and partition validation pass. |

No direct harness invocation or READY smoke is permitted.

## Risk / Rollback

Primary risk is temporarily removing B from recipient selection before H is
ready. The sequence enables H first, confirms H selection, and restores B first
immediately after H is in flight. Any failure path restores B before recording
the failed proof.

Secondary risk is mistaking old success for current health. The matrix retains
committed historical proof separately from current eligibility and later
failures; D remains DEGRADED until its residual defect is corrected and proven.

Rollback uses the same governed CLI, never Git or a direct file edit: set B
eligible, then H ineligible, and verify B selection. The final explicit B=true,
H=false overlay is the intended steady state for this bounded proof.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi5199-fd-evidence-h-functional-proof`; no prior version
is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are
the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore(config):` - records governed recipient eligibility for a bounded
functional-proof operation without changing harness source behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
