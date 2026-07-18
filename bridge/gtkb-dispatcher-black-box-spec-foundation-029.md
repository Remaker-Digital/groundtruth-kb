REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5268 Foundation Reimplementation - Terminal-Stage Correction

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 029
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-028.md
Supersedes for implementation authority: bridge/gtkb-dispatcher-black-box-spec-foundation-027.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268
Related Work Items: WI-5487, WI-5491
Related Test Artifacts: TEST-11578, TEST-11580
target_paths: ["groundtruth.db", "work_area/wi5268-DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md", "work_area/wi5268-DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md", "work_area/wi5268-DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md", "work_area/wi5268-ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md", "work_area/wi5268-DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md", ".groundtruth/formal-artifact-approvals/2026-07-17-DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-17-DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-17-DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-17-ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-17-DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001-v2.json"]
implementation_scope: governance_foundation_formalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: fix:

## Review Scope

Version 028 approved version 027, but the first durable operation failed
closed before mutation. Current WI-5268 is version 8 with
`resolution_status=resolved` and `stage=resolved`. The governed work-item
writer permits only an idempotent `resolved -> resolved` stage transition;
owner approval does not authorize a reverse stage transition. Therefore the
approved instruction to append `open/backlogged` is not executable through the
governed CLI.

The implementation claim and schema-v3 start packet acquired for version 027
were released after that failure. No MemBase row, formal artifact, content
carrier, approval output, source file, harness surface, dispatcher
configuration, or dispatcher runtime state was changed under version 028.

This revision changes only the work-item lifecycle sequence. The five
owner-approved native artifact bodies, exact SHA-256 values, machine metadata,
assertions, specification-derived verification, operational targets, and
owner decisions remain exactly those in canonical version 024 and the
execution-carrier closure in version 027.

## Canonical Authority

Canonical evidence for this revision is limited to current MemBase records,
Deliberation Archive records, and this numbered bridge chain. The same-session
`work_area/` content carriers and deterministic formal-approval outputs remain
declared operational targets only. They are never evidence, citations,
cross-session inputs, or dependencies.

## Lifecycle Correction

The supported append-only sequence is:

1. Before formal-artifact repair, append WI-5268 version 9 with
   `resolution_status=open`, retain immutable historical `stage=resolved`, and
   record that the five formal artifacts are undergoing governed
   reimplementation.
2. Keep the WI at `open/resolved` through implementation reporting and
   independent read-only verification. This state is intentionally temporary:
   resolution truth is open while the stage field preserves the historical
   terminal transition.
3. Only after an independent `VERIFIED` verdict, use the governed verified
   finalization path to append a terminal version with
   `resolution_status=resolved`, `stage=resolved`, and accurate completion
   evidence.

This sequence uses only supported CLI transitions, does not reopen the
terminal stage, and leaves the program in a truthful terminal state after
verification.

## Exact Preserved Foundation Outcome

The five version-2 native-body SHA-256 values remain:

| Artifact | SHA-256 |
| --- | --- |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | `be3ff577ee08df976542de1ef9dd75284cc24a1edee5eb5f11056c1933a02574` |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | `e6a58c02993a8a0350a0655b65ffd023f7402febf36bf5694b9dc845a88cd237` |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | `aa62220c8cbfd62ae43d48a61d6ca321c1f7cee4c803dfa474a5e575724d9d71` |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | `beffe6da9b2d75a471702a52d68cce865642fc77d34f617708f9e3577531a5b9` |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | `b2c2ffcf047a7d33a95e73f90f2b46525b3b55c25e383b4ad603a8c0fefe4088` |

All five retain version 024's exact `specified`, P0,
`dispatcher-black-box-hardening`, `automatable`, `gtkb_platform`, types,
titles, sections, tags, constraints, affected-by IDs, canonical source paths,
AUQ evidence, and one executable outer assertion each.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Requirement Sufficiency

Existing requirements are sufficient. The failed operation exposed an
execution-plan mismatch with the enforced terminal-stage model; it did not
change the owner's black-box requirements or approved artifact content.

## Owner Decisions / Input

- `APPROVE WI5268 FOUNDATION PACKET V2` remains the artifact-content and
  eleven-target approval.
- The owner-defined ordinary-worker, ops-envelope, build-envelope, and
  case-by-case build authorization decisions remain exactly as captured in
  version 024.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` remains
  controlling: this work performs no dispatcher configuration or runtime-state
  mutation.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` and
  `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` remain
  controlling evidence boundaries.

## Prior Deliberations

- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`
- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- The foundation owner-decision records enumerated in
  `bridge/gtkb-dispatcher-black-box-spec-foundation-024.md`

## Implementation Plan

After a fresh independent GO responding to version 029:

1. Acquire a fresh exact claim and schema-v3 start packet for version 029, its
   GO, WI-5268, the active PAUTH, this Prime Builder session, and all eleven
   exact targets.
2. Re-run applicability and clause preflights against version 029. Confirm
   WI-5268 remains version 8/resolved/resolved and the five specs remain exact
   version-1 records with `assertions=null`. Any drift stops.
3. Run governed `gt backlog update` without a stage argument to append
   WI-5268 as `resolution_status=open`, retaining `stage=resolved`, with
   truthful bridge linkage and status detail.
4. In the same Prime Builder session, extract each exact native Markdown body
   from canonical version 024 into its declared content-carrier target. Require
   exact SHA-256 match before use.
5. Run governed `gt spec update` for each ID using exact version-024 metadata.
   Permit only the five declared formal-approval outputs.
6. Delete the five content carriers immediately. Never cite either operational
   file class as evidence.
7. In a separate process, compare WI-5268 and all five specs to the approved
   packet and run all five canonical assertions.
8. After at least two normal dispatcher cycles, repeat the six canonical reads
   without inspecting or mutating dispatcher configuration or runtime state.
9. File an implementation report only if every immediate and delayed check
   passes. WI-5268 must remain `open/resolved` until independent verification.
10. Independent verification must use the governed VERIFIED finalization path
    so the terminal readback is `resolved/resolved` with accurate completion
    evidence.

## Pre-Flight Evidence

Candidate applicability and clause preflights are run against this complete
content before filing. Filing is permitted only with
`preflight_passed=true`, `missing_required_specs=[]`, and zero blocking clause
gaps.

## Specification-Derived Verification

| Requirement | Executed evidence | Required result |
| --- | --- | --- |
| Project/bridge/start authority | Active PAUTH, latest GO, claim, start readback | Version 029 and eleven exact targets |
| Supported interim lifecycle | Separate `gt backlog show WI-5268` read | Version at least 9, open/resolved, truthful repair detail |
| Five version-024 formal artifacts | Separate `gt spec show` reads and SHA-256 comparison | Exact version-2 records, metadata, bodies, and five assertions |
| Evaluability | `gt assert --spec` for all five IDs | Five exact outer assertions PASS; zero unsupported or missing |
| Carrier freshness and WI-5487 | Immediate and delayed separate-process reads | All six records persist; no restore or substitution |
| Canonical-reference boundary and WI-5491 | Report/verdict citation review | Only MemBase, Deliberation Archive, and numbered bridge evidence |
| CLI execution closure | Exact target and post-use path checks | Five content files removed; five declared approval outputs generated but not cited |
| Troubleshooter hold | Action/target review | No dispatcher configuration or runtime-state mutation |
| Foundation-first gate | WI-5269 through WI-5276 reads | Downstream implementation remains blocked until independent VERIFIED |
| Terminal closure | Post-VERIFIED `gt backlog show WI-5268` | New terminal version, resolved/resolved, accurate completion evidence |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY; bridge/gtkb-dispatcher-black-box-spec-foundation-024.md; bridge/gtkb-dispatcher-black-box-spec-foundation-028.md",
  "canonical_authority": "MemBase versioned records, Deliberation Archive owner decisions, and numbered bridge artifacts",
  "primary_route": "gt backlog update plus gt spec update",
  "before_behavior": "The approved plan requests a reverse stage transition rejected by the governed writer.",
  "after_behavior": "Resolution truth becomes open during repair while immutable historical stage remains resolved; verified finalization returns both fields to terminal truth.",
  "self_descriptive_naming": "Each operational target names its exact spec ID and purpose.",
  "obsolete_guidance_disposition": "Version 028 GO is superseded before any durable implementation mutation.",
  "history_preservation": "Every correction is append-only; no terminal stage or prior bridge version is rewritten.",
  "baseline": {
    "wi_5268": "version 8 resolved/resolved",
    "foundation_specs": "five exact version-1 records with assertions null"
  },
  "expected_interim": {
    "wi_5268": "open/resolved",
    "foundation_specs": "five exact version-2 records with executable assertions"
  },
  "expected_terminal": {
    "wi_5268": "resolved/resolved after independent VERIFIED finalization"
  },
  "rollback": {
    "instructions": "Append a reviewed corrective version; never restore or replace groundtruth.db.",
    "verification": "Repeat separate-process canonical reads and hashes."
  }
}
```

## Acceptance Criteria

- [x] The failed version-028 start caused no durable implementation mutation.
- [x] The exact five artifact bodies and eleven operational targets are
  unchanged.
- [x] The corrected sequence uses only supported work-item transitions.
- [x] Canonical authority excludes every scratch, retired, generated-output,
  harness-local, and runtime-log surface.
- [x] The dispatcher troubleshooter hold remains explicit.
- [ ] Fresh independent GO approves version 029.
- [ ] Fresh claim/start covers all eleven exact targets.
- [ ] WI-5268 is open/resolved during implementation and resolved/resolved only
  after independent VERIFIED finalization.
- [ ] All five exact version-2 records persist through immediate and delayed
  readback and all five assertions pass.

## Risks and Rollback

The temporary `open/resolved` pair is intentionally asymmetric because the
stage model makes `resolved` irreversible. Resolution status is the truthful
current-work signal; the bridge latest status remains the implementation gate.
The asymmetry ends at independent VERIFIED finalization.

Rollback is append-only correction or supersession of the six MemBase records.
It is never checkout, reset, byte replacement, whole-carrier restore, or
dispatcher mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
