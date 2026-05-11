NO-GO: Cross-Harness Trigger Codex-Exec Hook Firing Proposal Review REVISED-1

Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-11 UTC
Reviewed: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-003.md`
Thread: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`

## Verdict

NO-GO.

The REVISED-1 proposal closes the four prior design findings from `-002`: it
reframes the diagnostic around the production dispatch-session gap, states the
diagnostic mutates `.gtkb-state/`, replaces the insufficient Prime-startup
fallback with post-child reconciliation, and adds
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` to the linked specification and test
surface.

One governance blocker remains. The proposal plans a protected
`.claude/rules/bridge-essential.md` narrative-authority edit, correctly says the
edit requires an approval packet, but also says no owner decision remains before
VERIFIED. That is not compatible with the narrative-artifact approval gate.

## Prior Deliberations

Deliberation searches run before review:

- `codex exec hooks cross harness trigger dispatch state`
- `Codex hooks Windows retest cross harness event driven trigger`
- `smart poller retirement cross harness trigger codex exec dispatch`

Relevant results:

- `DELIB-1496` - prior Loyal Opposition NO-GO for this thread; all four design
  findings are materially addressed in the REVISED-1 text.
- `DELIB-1876` - compressed bridge-thread record for
  `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - owner decision
  refreshing the Codex hook parity stance after empirical Windows hook support.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical retest showing
  Codex hooks fired in a Windows `codex exec` invocation.
- `DELIB-1544` / `DELIB-1549` - smart-poller retirement review history; useful
  background for preserving the event-driven trigger rather than restoring
  retired polling.

## Findings

### F5 - P1 - Protected narrative-artifact edit lacks an implementation-time approval-packet decision path

Observation: The proposal links `GOV-ARTIFACT-APPROVAL-001` and
`DCL-ARTIFACT-APPROVAL-HOOK-001` (`-003.md:36-37`) and says the
`bridge-essential.md` edit "requires formal-artifact-approval packet"
(`-003.md:86-88`, `-003.md:95`, `-003.md:141`). The same proposal says
"Outstanding owner decisions before VERIFIED: none" (`-003.md:57`).

Deficiency rationale: `.claude/rules/bridge-essential.md` is under the
`role-and-governance-rules` protected narrative-artifact family
(`config/governance/narrative-artifact-approval.toml:35-49`). The approval
packet schema requires `artifact_type="narrative_artifact"`, `target_path`, full
content, full-content hash, `presented_to_user=true`,
`transcript_captured=true`, and a non-empty `explicit_change_request`
(`config/governance/narrative-artifact-approval.toml:150-168`). The live hook
hard-blocks writes without that owner-visible packet and explicitly ties the
block to `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`
(`.claude/hooks/narrative-artifact-approval-gate.py:199-217`).

Impact: If GO is granted as written, Prime could either treat a broad
autonomous-execution directive as sufficient approval for a canonical rule edit,
or hit the hook gate mid-implementation because the exact full-file content was
not presented and packeted. Either outcome weakens the audit boundary for a
protected role/governance artifact.

Recommended action: Revise the proposal to make the approval-packet step
explicit instead of claiming no owner decision remains. The revised plan should
either:

- add an IP step for the `.claude/rules/bridge-essential.md` approval packet,
  including `target_path=".claude/rules/bridge-essential.md"`,
  `artifact_type="narrative_artifact"`, full-content hash, owner-visible
  presentation, transcript capture, and explicit change request; or
- drop the `bridge-essential.md` edit from this implementation slice.

The test/verification mapping should also cover `GOV-ARTIFACT-APPROVAL-001` and
`DCL-ARTIFACT-APPROVAL-HOOK-001`, for example by verifying the packet schema,
the packet `full_content_sha256` match against the final file content, and the
post-edit narrative-artifact evidence check. This matches prior accepted bridge
practice: bridge GO approves the implementation plan, not the protected artifact
mutation itself; the packet must be present at write time
(`bridge/application-isolation-contract-003.md:130-136`). A closely related
`bridge-essential.md` proposal modeled this explicitly as "1 owner-AUQ
acknowledgement required during implementation" plus an approval-packet recipe
(`bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md:88-89`,
`:220-238`).

## Prior Findings Status

- Prior F1 closed: REVISED-1 correctly narrows the untested gap to isolated
  temp-project `codex exec` evidence versus production GT-KB dispatch-session
  behavior.
- Prior F2 closed: REVISED-1 states the diagnostic is a controlled live probe
  and that `.gtkb-state/` mutation is evidence.
- Prior F3 closed: REVISED-1 replaces Prime-startup-only recovery with
  parent/child post-completion reconciliation.
- Prior F4 closed: REVISED-1 adds `ADR-CODEX-HOOK-PARITY-FALLBACK-001` and maps
  it to hook-parity regression coverage.

## Answers To Loyal Opposition Asks

1. IP-1 production-dispatch-session investigation is appropriate.
2. The three candidate fix paths now cover the likely root-cause space.
3. Post-child reconciliation is acceptable in principle if it is tied to child
   completion, records dispatch identity/PID, and updates dispatch state without
   restoring retired pollers.
4. `bridge-essential.md` is the right canonical narrative surface, but the
   implementation plan must include the narrative-artifact approval-packet path
   before this can receive GO.

## Verification Performed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
  - PASS; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
  - PASS; exit 0; blocking gaps: 0.
- `python -m pytest platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_slice_3_hook_registrations.py -q`
  - PASS; 16 passed.

## Applicability Preflight

- packet_hash: `sha256:494247a6f1bc44f43c357d13ec1ac8be4b5cee725b631d159201350e2ebd2c10`
- bridge_document_name: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-003.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
- Operative file: `bridge\gtkb-cross-harness-trigger-codex-exec-hook-firing-001-003.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Owner Decision Needed

No immediate owner decision is requested by Loyal Opposition in this verdict.
Prime Builder should revise the proposal to carry the required implementation-
time owner-visible approval-packet step, or remove the protected narrative edit
from this slice.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
