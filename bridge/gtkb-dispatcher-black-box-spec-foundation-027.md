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

# WI-5268 Foundation Reimplementation - Execution-Carrier Closure

bridge_kind: prime_proposal
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 027
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-026.md
Supersedes for implementation authority: bridge/gtkb-dispatcher-black-box-spec-foundation-026.md
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

This is a delta-only revision. The five owner-approved native artifact bodies,
machine metadata, executable assertions, hashes, canonical history, and
specification-derived verification requirements remain exactly those in
`bridge/gtkb-dispatcher-black-box-spec-foundation-024.md`. Loyal Opposition
already approved that substantive packet in
`bridge/gtkb-dispatcher-black-box-spec-foundation-025.md`.

Version 025 cannot be consumed because version 024 declared only
`groundtruth.db`, prohibited generated scratch input, and said generated
approval files were not outputs. The governed `gt spec update` command
requires an in-root `--content-file` and writes one formal-approval packet
before each MemBase update. Implementing under version 025 would therefore
mutate undeclared paths and contradict the approved procedure.

Version 026 corrected that target closure but repeated the full packet and its
review claim expired without a verdict. Version 027 asks the reviewer to
evaluate only this execution-carrier correction. It does not change a
requirement, body, hash, assertion, field value, owner approval, or durable
MemBase outcome from version 024.

## Canonical Authority

Canonical evidence for this revision is limited to:

- current MemBase records for WI-5268, WI-5487, WI-5491, TEST-11578,
  TEST-11580, the five version-1 foundation records, and the active PAUTH;
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`;
- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT`;
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`;
- the owner-decision records and numbered bridge history cited by version 024;
- `bridge/gtkb-dispatcher-black-box-spec-foundation-024.md`;
- `bridge/gtkb-dispatcher-black-box-spec-foundation-025.md`; and
- `bridge/gtkb-dispatcher-black-box-spec-foundation-026.md`.

The five `work_area/` paths are same-session operational content carriers.
The five `.groundtruth/` paths are deterministic operation-time outputs of the
governed CLI. They are declared targets, not canonical authorities, evidence,
citations, or cross-session inputs. No pre-existing file at any of those ten
paths may be read or reused.

## Exact Preserved Foundation Outcome

Version 024 remains the canonical exact packet for these five version-2
records and hashes:

| Specification | Exact native-body SHA-256 |
| --- | --- |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | `be3ff577ee08df976542de1ef9dd75284cc24a1edee5eb5f11056c1933a02574` |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | `e6a58c02993a8a0350a0655b65ffd023f7402febf36bf5694b9dc845a88cd237` |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | `aa62220c8cbfd62ae43d48a61d6ca321c1f7cee4c803dfa474a5e575724d9d71` |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | `beffe6da9b2d75a471702a52d68cce865642fc77d34f617708f9e3577531a5b9` |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | `b2c2ffcf047a7d33a95e73f90f2b46525b3b55c25e383b4ad603a8c0fefe4088` |

All five retain version 024's exact `specified`, P0,
`dispatcher-black-box-hardening`, `automatable`, `gtkb_platform`, tags,
constraints, affected-by IDs, source paths, AUQ evidence, and one executable
outer assertion each. WI-5268 is first corrected from false resolved state to
open/backlogged.

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

Existing requirements sufficient. This revision closes an execution-target
declaration defect only. It introduces no new foundation semantics and requires
no new owner decision. The owner approval remains:
`APPROVE WI5268 FOUNDATION PACKET V2`.

## Implementation Plan

After a fresh independent GO responding to version 027:

1. Acquire a fresh `go_implementation` claim and schema-v3 start packet bound
   to version 027, its GO, WI-5268, the active PAUTH, this Prime Builder
   session, and all eleven exact targets.
2. Re-run applicability and mandatory-clause preflights. Confirm WI-5268 is
   version 8/resolved and all five specs are version 1, `specified`, exact
   native-body hashes above, and `assertions=null`. Any drift stops.
3. Append the WI-5268 correction to open/backlogged with truthful bridge
   linkage and status detail.
4. In this same Prime Builder session, extract each native Markdown body from
   canonical version 024 into its declared `work_area/wi5268-*.md` target.
   Require exact SHA-256 match before use.
5. Run governed `gt spec update` for each ID with the exact version-024
   metadata. Permit only the five declared approval-packet outputs.
6. Delete the five content carriers immediately. Do not cite either
   operational file class in the implementation report.
7. Close the writer. In a separate process, compare WI-5268 and all five specs
   to version 024. Run the five canonical assertions.
8. After at least two normal dispatcher cycles, repeat the six canonical reads
   without inspecting or mutating dispatcher configuration or runtime state.
9. File an implementation report only if all immediate and delayed checks pass.

Raw SQL, another database, whole-file restore, checkout, reset, binary
replacement, dispatcher mutation, Git staging/commit/push, credential,
deployment, release, and external-system effects are prohibited.

## Specification-Derived Verification

| Requirement | Executed evidence | Required result |
| --- | --- | --- |
| Project/bridge/start authority | Active PAUTH, latest GO, claim, start readback | Version 027 and eleven exact targets |
| Five version-024 formal artifacts | Separate `gt spec show` reads and SHA-256 comparison | Exact version 2 records, metadata, bodies, and five assertions |
| WI-5268 lifecycle truth | Separate `gt backlog show WI-5268` reads | Version at least 9, open/backlogged, truthful detail |
| Evaluability | `gt assert --spec` for all five IDs | Five exact outer assertions PASS; zero unsupported or missing |
| Carrier freshness and WI-5487 | Immediate and delayed separate-process reads | All six records persist; no restore or substitution |
| Canonical-reference boundary and WI-5491 | Report/verdict citation review | Only MemBase, Deliberation Archive, and numbered bridge evidence |
| CLI execution closure | Exact target and post-use path checks | Five content files removed; five declared approval outputs generated but not cited |
| Troubleshooter hold | Action/target review | No dispatcher configuration or runtime-state mutation |
| Foundation-first gate | WI-5269 through WI-5276 reads | Downstream implementation remains blocked until independent VERIFIED |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY; bridge/gtkb-dispatcher-black-box-spec-foundation-024.md; bridge/gtkb-dispatcher-black-box-spec-foundation-025.md",
  "canonical_authority": "MemBase versioned records, Deliberation Archive owner decisions, and numbered bridge artifacts",
  "primary_route": "gt backlog update plus gt spec update",
  "before_behavior": "The approved proposal omits unavoidable governed-CLI file effects.",
  "after_behavior": "Every durable and transient mutation is declared while canonical evidence remains limited to canonical artifacts.",
  "self_descriptive_naming": "Each operational target names its exact spec ID and purpose.",
  "obsolete_guidance_disposition": "Version 025 is withdrawn before implementation because its one-target scope is not executable.",
  "history_preservation": "WI and spec correction is append-only; transient content carriers are removed after use.",
  "baseline": {
    "wi_5268": "version 8 false-resolved",
    "foundation_specs": "five exact version-1 records with assertions null"
  },
  "expected_result": {
    "wi_5268": "open/backlogged",
    "foundation_specs": "five exact version-2 records with executable assertions"
  },
  "rollback": {
    "instructions": "Append a reviewed corrective version; never restore or replace groundtruth.db.",
    "verification": "Repeat separate-process canonical reads and hashes."
  },
  "hard_invariants": [
    "no dispatcher configuration or runtime-state mutation",
    "no noncanonical evidence citation",
    "no whole-carrier restore",
    "no downstream WI-5269 through WI-5276 implementation before foundation VERIFIED"
  ],
  "fail_closed_conditions": [
    "any precondition version or hash drifts",
    "any target is absent from the claim or start packet",
    "a transient path pre-exists or is reused",
    "any immediate or delayed canonical read differs"
  ],
  "essential_context_preservation": "Version 024 remains the exact reviewed content packet; version 027 changes execution closure only."
}
```

## Acceptance Criteria

- [x] Version 027 is delta-only and cites canonical version 024 for exact content.
- [x] All eleven unavoidable operational targets are declared.
- [x] Noncanonical operational files are excluded from evidence.
- [x] Applicability and mandatory-clause preflights pass with no blocking gap.
- [ ] Fresh independent GO approves version 027.
- [ ] Fresh claim/start covers all eleven targets.
- [ ] WI-5268 and all five specs pass immediate and delayed canonical readback.
- [ ] Independent Loyal Opposition issues VERIFIED without carrier replacement.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
