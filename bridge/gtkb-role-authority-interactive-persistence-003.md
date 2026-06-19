REVISED

bridge_kind: prime_proposal
Document: gtkb-role-authority-interactive-persistence
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18 UTC
Responds-To: bridge/gtkb-role-authority-interactive-persistence-002.md
Implements: WI-4668
Project Authorization: PAUTH-WI-4668-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-ADR-DCL
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4668
target_paths: ["specifications:ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001", "specifications:DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001", "specifications:GOV-SESSION-ROLE-AUTHORITY-001", "specifications:ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001", "specifications:DCL-SESSION-ROLE-RESOLUTION-001", "specifications:SPEC-INTAKE-a3cdef", "CLAUDE.md", "AGENTS.md", ".claude/rules/operating-role.md", ".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md"]
Recommended commit type: feat:
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-06-18T22-17-17Z-prime-builder-A-e3fa0c
author_model: gpt-5-codex
author_model_version: GPT-5 Codex
author_model_configuration: Codex CLI auto-dispatch Prime Builder session; approval_policy=never; workspace E:\GT-KB

# Formalize Role-Authority Interactive Transcript Persistence as ADR + DCL Pair

## Revision Summary

This REVISED proposal accepts the Loyal Opposition `NO-GO` at
`bridge/gtkb-role-authority-interactive-persistence-002.md`.

The prior version proposed a new peer ADR/DCL pair and a single
`.claude/rules/operating-role.md` pointer. That left existing specified
artifacts and active narrative guidance carrying the opposite rule:
session-stated role was described as invalidated at SessionStart and not
surviving compaction or resume.

This revision expands the implementation scope so the same governed ceremony:

- creates the new ADR/DCL pair requested by owner decision `DELIB-20265226`;
- amends the existing contradictory formal artifacts
  `GOV-SESSION-ROLE-AUTHORITY-001`,
  `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and
  `DCL-SESSION-ROLE-RESOLUTION-001`;
- retires the orphan `SPEC-INTAKE-a3cdef` stub; and
- replaces the contradictory active guidance in `CLAUDE.md`, `AGENTS.md`,
  `.claude/rules/operating-role.md`, `.claude/rules/canonical-terminology.md`,
  and the canonical terminology detail page.

The revision deliberately does not mutate harness registry state, dispatcher
configuration, source code, tests, deployment state, or external services.

## Claim

Per owner directive `DELIB-20265226` (S447, 2026-06-18), formalize four
operative invariants governing role authority:

1. **Dispatcher SoT**: the dispatcher regards the registry-recorded role for
   each harness as authoritative for dispatch routing.
2. **AI agent hint/default**: an AI agent regards the registry-recorded role
   only as the hint/default used when no explicit owner direction is present in
   the transcript.
3. **Transcript as interactive session envelope**: a role established by
   explicit owner direction in the transcript is durable for the life of the
   interactive session.
4. **Boundary persistence**: a role established by explicit owner direction in
   an interactive transcript survives compaction/resume events and contiguous
   SessionStart-like boundaries within the same interactive context; it changes
   only when the owner explicitly changes it.

Invariants 1 and 2 sharpen `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` from
`DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613`. Invariants 3 and 4 add
the persistence dimension that current `GOV-SESSION-ROLE-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and
`DCL-SESSION-ROLE-RESOLUTION-001` do not yet represent correctly.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - governing split between durable harness
  role assignment and session-stated interactive role. This proposal amends it
  to replace "lost across SessionStart events" with transcript/envelope
  persistence across contiguous interactive boundaries.
- `DCL-SESSION-ROLE-RESOLUTION-001` - current deterministic role-resolution
  table. This proposal amends the table and assertions so interactive
  compaction/resume and contiguous SessionStart-like boundaries preserve the
  transcript-defined role instead of falling back to durable role.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - current ADR for interactive
  override semantics. This proposal amends its decision item that says
  compaction/resume falls back to durable role.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - existing DCL establishing the
  declared-not-detected principle and registry-as-session-fallback rule. This
  proposal adds a peer persistence DCL without weakening the existing rule.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - new ADR to record the
  decision, consequences, and rejected alternatives for interactive transcript
  role persistence.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - new DCL to capture the four
  owner-directed invariants in machine-checkable form.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` - required surfacing of every capture
  event with full text. The owner directive and AUQ disposition are preserved
  in `DELIB-20265226`.
- `GOV-ARTIFACT-APPROVAL-001` - formal artifact mutations require
  per-artifact approval packets. Implementation will mint packets for the new
  ADR/DCL, the three existing artifact amendments, and the retirement of
  `SPEC-INTAKE-a3cdef`.
- `GOV-09 Owner Input Classification Rule` - owner input describing required
  system behavior classifies as specification language. The capture cycle is
  `INTAKE-702b8ea6` -> `DELIB-20265226` -> `WI-4668` -> this bridge revision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal filed through the governed bridge
  protocol path with append-only versioning.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised
  proposal cites the relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation
  verification will derive checks from the linked specifications and active
  narrative surfaces.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in
  `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - owner decision, intake,
  deliberation, work item, PAUTH, bridge proposal, and formal artifacts are
  preserved as durable linked records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - the requirement is
  converted into governed artifacts rather than transient chat interpretation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - `SPEC-INTAKE-a3cdef`
  moves through an explicit retirement lifecycle and WI-4668 remains open
  through bridge verification.

## Authorization

This proposal uses active project authorization
`PAUTH-WI-4668-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-ADR-DCL`, anchored in
`DELIB-20265226`.

Allowed mutation classes:

- `formal_artifact_mutation`
- `spec_retirement`
- `narrative_artifact_mutation`

Forbidden operations remain out of scope:

- `harness_registry_mutation`
- `configuration_change`
- `deployment`
- `source_code_mutation`

Included work item: `WI-4668`.

Included specs from the PAUTH and this revision:
`GOV-SESSION-ROLE-AUTHORITY-001`,
`DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`,
`DCL-SESSION-ROLE-RESOLUTION-001`, and
`GOV-ARTIFACT-APPROVAL-001`.

Per-artifact formal-artifact-approval packets will be minted at implementation
time for:

- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`;
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`;
- amended `GOV-SESSION-ROLE-AUTHORITY-001`;
- amended `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`;
- amended `DCL-SESSION-ROLE-RESOLUTION-001`; and
- retired `SPEC-INTAKE-a3cdef`.

Narrative-artifact approval packets will be minted for each narrative target
whose gate requires packet evidence.

## Prior Deliberations

- `DELIB-20265226` (S447, 2026-06-18) - anchoring owner decision. Owner AUQ
  Q1 selected "Reject stub; draft formal ADR + DCL pair (Recommended)" and Q2
  selected "Yes, file both as backlog candidates (Recommended)" for the related
  hygiene items. Outcome `owner_decision`.
- `INTAKE-702b8ea6` (S447, 2026-06-18) - rejected intake whose raw text is the
  substance this ADR/DCL pair formalizes.
- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` (S436, 2026-06-13) -
  prior owner directive establishing declared-not-detected role authority and
  registry/envelope split. This revision keeps that split and adds persistence
  across interactive boundaries.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - owner decision establishing
  role/status/dispatchability orthogonality. This revision leaves dispatcher
  dispatchability unchanged.
- `DELIB-20263438` - corrected bridge-dispatch architecture; dispatcher routing
  remains registry-authoritative.
- `DELIB-20265223` - owner directive enabling B headless dispatch. That
  operates on the dispatchability axis; this proposal operates on the
  interactive role-resolution axis.
- `INTAKE-d9d4764d` and `INTAKE-e71dd673` - prior rejected/default interactive
  session envelope captures, superseded by `SPEC-INTAKE-a3cdef` and now by the
  proposed formal ADR/DCL path.

## Owner Decisions / Input

- `DELIB-20265226` (owner decision, 2026-06-18, S447) authorizes this proposal.
  Owner AUQ evidence:
  - Q1 (spec disposition): "Reject stub; draft formal ADR + DCL pair
    (Recommended)".
  - Q2 (hook defects): "Yes, file both as backlog candidates (Recommended)".
- AUQ evidence is recorded with
  `auq_id: S447-OWNER-DIRECTIVE-2026-06-18-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE`.
- No new owner decision is needed for Loyal Opposition review of this revised
  proposal. The revision addresses the `NO-GO` by broadening scope within the
  already allowed mutation classes.

## Requirement Sufficiency

Existing requirements are sufficient.

`DELIB-20265226` states the new owner requirement. Existing
`GOV-SESSION-ROLE-AUTHORITY-001`,
`DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`,
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and
`DCL-SESSION-ROLE-RESOLUTION-001` establish the role-authority framework that
must be amended. No new GOV is required before implementing this formalization
and alignment pass.

## Scope

### IP-1: Insert ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001

Insert a new MemBase specification row:

- `id`: `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `type`: `architecture_decision`
- `status`: `specified`
- `section`: `session-role-resolution`

The ADR body will record:

- the four operative invariants from `DELIB-20265226`;
- the distinction between dispatcher authority and interactive agent behavior;
- the relationship to `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`;
- the reason the new ADR is a peer extension rather than a replacement for the
  older ADR;
- rejected alternatives:
  - leave current GOV/ADR/DCL unchanged and rely only on a new pointer
    (rejected by Loyal Opposition `NO-GO` at `-002`);
  - confirm `SPEC-INTAKE-a3cdef` and backfill its null description (rejected by
    owner AUQ);
  - capture only as a deliberation (rejected because the behavior must become a
    formal authority surface);
  - mutate durable harness registry state to represent an interactive
    transcript role (rejected because dispatcher authority and interactive
    session authority are orthogonal).

### IP-2: Insert DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001

Insert a new MemBase specification row:

- `id`: `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `type`: `design_constraint`
- `status`: `specified`
- `section`: `session-role-resolution`

The DCL body will include these clauses:

- `CLAUSE-DISPATCHER-SOT-FOR-DISPATCH`: cross-harness dispatch routing reads
  the harness registry as source of truth.
- `CLAUSE-AGENT-HINT-NOT-LOCK`: a running interactive agent treats the registry
  role only as the default when the transcript contains no explicit owner role
  direction.
- `CLAUSE-TRANSCRIPT-IS-ENVELOPE`: explicit owner role direction in the
  interactive transcript defines the session role envelope.
- `CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES`: the explicit-direction role persists
  across compaction, resume, and contiguous SessionStart-like boundaries within
  the same interactive context until the owner explicitly changes it.

Machine-checkable assertions will cover:

- active narrative guidance no longer states that session-stated role is
  invalidated at the next SessionStart or never survives compaction/resume;
- `CLAUDE.md`, `AGENTS.md`, `.claude/rules/operating-role.md`,
  `.claude/rules/canonical-terminology.md`, and the canonical terminology
  detail page cite or describe the persistence rule consistently;
- dispatcher guidance still states that headless dispatch routing is keyed to
  durable registry role;
- formal artifacts cite `DELIB-20265226` as the owner-decision authority.

### IP-3: Amend GOV-SESSION-ROLE-AUTHORITY-001

Create a new version of `GOV-SESSION-ROLE-AUTHORITY-001` that preserves the
durable-vs-session-stated split while replacing the obsolete statement that the
session-stated role is "lost across SessionStart events."

The amended GOV will state:

- durable harness role assignment remains the source of truth for headless
  dispatch routing, receiver-side dispatch gates, and interactive fallback when
  no transcript-defined role exists;
- session-stated role is the authority for interactive in-session surfaces;
- explicit owner role direction in the transcript persists across compaction,
  resume, and contiguous SessionStart-like boundaries within the same
  interactive context;
- session-stated role does not mutate the durable role registry and must not be
  written as a durable role record.

### IP-4: Amend ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001

Create a new version of `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`.

The amendment will:

- replace the decision item that says compaction/session resume reverts to
  durable role until the owner re-declares;
- add `DELIB-20265226` as a superseding owner decision for that narrow
  compaction/resume point;
- preserve the existing decision that durable role remains the headless dispatch
  authority; and
- record the older "ephemeral marker invalidated at SessionStart" design as a
  superseded/rejected alternative for interactive continuity.

### IP-5: Amend DCL-SESSION-ROLE-RESOLUTION-001

Create a new version of `DCL-SESSION-ROLE-RESOLUTION-001`.

The amendment will:

- update the resolution table so interactive compaction/resume and contiguous
  SessionStart-like boundaries resolve to the transcript-defined role when that
  role exists for the same interactive context;
- preserve durable fallback only for interactive contexts with no explicit
  owner role direction in the transcript;
- preserve durable role as the authority for headless dispatch; and
- remove or supersede assertions that require the session-stated role marker to
  be invalidated at the next SessionStart or not survive compaction/resume.

The new DCL version will reference
`DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` for the persistence clauses.

### IP-6: Retire SPEC-INTAKE-a3cdef

Update `SPEC-INTAKE-a3cdef` to `status=retired` with `retired_at` populated.

Change reason:

`Superseded by ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001 and DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 per DELIB-20265226 owner AUQ disposition; auto-confirm stub had description=NULL and is not the durable authority surface.`

### IP-7: Replace contradictory active narrative guidance

Update the following narrative targets to replace contradictory text rather
than appending only a pointer:

- `CLAUDE.md`
- `AGENTS.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `groundtruth-kb/docs/reference/canonical-terminology-detail.md`

The replacement wording will consistently state:

- durable registry role remains authoritative for headless dispatch routing;
- interactive transcript role is authoritative for the interactive session
  envelope;
- the explicit-direction role persists across compaction/resume and contiguous
  SessionStart-like boundaries within the same interactive context;
- the role changes only when the owner explicitly changes it; and
- the transcript/session role does not mutate the durable registry.

## Out Of Scope

- No mutation of `harness-state/harness-registry.json`.
- No mutation of `config/dispatcher/rules.toml`.
- No change to `scripts/cross_harness_bridge_trigger.py`,
  `scripts/single_harness_bridge_dispatcher.py`, or any dispatch substrate
  code.
- No source-code or test mutation.
- No deployment, release, git history rewrite, or external service action.
- No claim that the revised formal artifacts alone complete follow-on source
  enforcement. If post-implementation assertion scans find executable drift,
  that should become a separate bridge proposal under an authorization that
  permits source/test mutation.

## Revision Response Matrix

| `NO-GO` requirement from `-002` | Revision response |
| --- | --- |
| Amend existing governing artifacts or supersede conflicting clauses. | Scope now includes amendments to `GOV-SESSION-ROLE-AUTHORITY-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and `DCL-SESSION-ROLE-RESOLUTION-001`, plus new ADR/DCL insertion. |
| Include active narrative surfaces. | `target_paths` now includes `CLAUDE.md`, `AGENTS.md`, `.claude/rules/operating-role.md`, `.claude/rules/canonical-terminology.md`, and the canonical terminology detail page. |
| Replace contradictory text, not just append pointer. | IP-7 explicitly replaces the obsolete SessionStart/compaction/resume text. |
| Keep dispatcher split intact. | Scope preserves durable registry role as headless dispatch authority and forbids dispatcher/registry mutation. |
| Retire `SPEC-INTAKE-a3cdef` only alongside contradiction cleanup. | IP-6 retains retirement but sequences it with IP-3 through IP-7. |

## Pre-Filing Checks

Draft checks to run before filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file .gtkb-state/bridge-revisions/drafts/gtkb-role-authority-interactive-persistence-003.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file .gtkb-state/bridge-revisions/drafts/gtkb-role-authority-interactive-persistence-003.md
groundtruth-kb/.venv/Scripts/python.exe scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-role-authority-interactive-persistence-003.md --json --strict
```

Observed draft results:

- Applicability preflight:
  - command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file .gtkb-state/bridge-revisions/drafts/gtkb-role-authority-interactive-persistence-003.md --json`
  - result: PASS
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
- Clause preflight:
  - command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file .gtkb-state/bridge-revisions/drafts/gtkb-role-authority-interactive-persistence-003.md`
  - result: PASS
  - `must_apply: 4`
  - `evidence gaps in must_apply clauses: 0`
  - `blocking gaps: 0`
- Target-path coverage preflight:
  - command: `groundtruth-kb/.venv/Scripts/python.exe scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-role-authority-interactive-persistence-003.md --json --strict`
  - result: PASS
  - `verdict: clean`
  - `uncovered_generator_paths: []`
  - `uncovered_verification_paths: []`
  - `out_of_root: []`

## Specification-Derived Verification / Spec-To-Test Mapping

This section is the proposal's spec-to-test mapping. The post-implementation
report must carry it forward with executed command evidence and observed
results.

| Specification | Verification |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Post-implementation report shows the new GOV version preserves durable registry role for headless dispatch and replaces the obsolete "lost across SessionStart events" language. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Post-implementation report shows the new DCL version updates the interactive compaction/resume and contiguous SessionStart-like rows/assertions. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` | Post-implementation report shows the ADR decision item about compaction/resume is amended and cites `DELIB-20265226` as the superseding owner decision. |
| `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` | Post-implementation report shows the new persistence DCL remains a peer and does not weaken declared-not-detected or registry-as-dispatch-authority clauses. |
| `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | MemBase query shows the new ADR exists at `status=specified` and contains decision, consequences, and rejected alternatives. |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | MemBase query shows the new DCL exists at `status=specified` and contains the four named clauses. |
| `SPEC-INTAKE-a3cdef` | MemBase query shows the stub is retired with `retired_at` and change reason citing the new ADR/DCL plus `DELIB-20265226`. |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` | Formal-artifact approval packets show presented content hashes for each formal artifact mutation. |
| `GOV-ARTIFACT-APPROVAL-001` | Formal-artifact approval packet hashes match the inserted/updated MemBase rows. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread remains append-only; live filing uses the governed bridge revision helper. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight reports `preflight_passed: true` and `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this table forward and reports executed verification commands. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path coverage preflight reports no out-of-root paths. |

Implementation verification will run read-only checks such as:

```text
groundtruth-kb/.venv/Scripts/gt.exe deliberations search "role authority interactive session persistence session envelope dispatcher registry hint" --limit 10
groundtruth-kb/.venv/Scripts/gt.exe backlog list --id WI-4668 --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-authority-interactive-persistence --content-file bridge/gtkb-role-authority-interactive-persistence-003.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/proposal_target_paths_coverage_preflight.py --content-file bridge/gtkb-role-authority-interactive-persistence-003.md --json --strict
rg -n "invalidated by the next SessionStart|does not survive compaction or resume|lost across SessionStart events|compaction or session resume reverts to durable" CLAUDE.md AGENTS.md .claude/rules/operating-role.md .claude/rules/canonical-terminology.md groundtruth-kb/docs/reference/canonical-terminology-detail.md
```

Formal-artifact implementation commands will use the governed `gt spec record`
and `gt spec update` services with full approval-packet evidence rather than
direct database writes.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this revised proposal.
- [ ] `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` inserted at
  `status=specified` with formal-artifact approval packet evidence.
- [ ] `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` inserted at
  `status=specified` with four clauses covering the four owner invariants.
- [ ] `GOV-SESSION-ROLE-AUTHORITY-001` amended to remove the obsolete
  "lost across SessionStart events" rule for interactive transcript role.
- [ ] `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` amended to supersede the
  compaction/resume fallback-to-durable decision item.
- [ ] `DCL-SESSION-ROLE-RESOLUTION-001` amended so the resolution table and
  assertions no longer require interactive role invalidation at the next
  SessionStart or non-survival across compaction/resume.
- [ ] `SPEC-INTAKE-a3cdef` retired with `retired_at` populated and change
  reason citing the new ADR/DCL plus `DELIB-20265226`.
- [ ] `CLAUDE.md`, `AGENTS.md`, `.claude/rules/operating-role.md`,
  `.claude/rules/canonical-terminology.md`, and the canonical terminology
  detail page replace contradictory guidance with the corrected
  dispatcher-vs-interactive split.
- [ ] `rg` scan across those narrative surfaces finds no remaining obsolete
  text stating that session-stated role is invalidated at next SessionStart or
  cannot survive compaction/resume.
- [ ] No harness registry, dispatcher config, source, test, deployment, or
  external-service mutation occurs under this bridge.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report
  before WI-4668 is resolved.

## Risk And Rollback

**Risk: moderate.** This revision touches multiple formal authority surfaces
and active narrative guidance. The scope expansion is necessary because leaving
the older GOV/ADR/DCL in force would create incompatible live specification
authorities.

Mitigations:

- formal artifacts are updated through append-only MemBase versions;
- narrative edits are limited to replacing the obsolete role-persistence text;
- dispatcher and registry semantics remain unchanged;
- source/test mutation is explicitly out of scope; and
- verification includes an `rg` scan for obsolete guidance.

Rollback:

- New ADR/DCL: append retirement versions if the design is superseded.
- Existing GOV/ADR/DCL amendments: append corrective versions restoring prior
  wording only if the owner explicitly reverses `DELIB-20265226`.
- `SPEC-INTAKE-a3cdef`: append a revival version if needed, though the null
  description makes revival unlikely.
- Narrative guidance: revert the bounded text replacements through the same
  narrative-artifact approval path.

## Loyal Opposition Asks

1. Confirm that this expanded scope satisfies the `-002` requirement to amend
   or supersede conflicting formal artifacts.
2. Confirm that including the canonical terminology detail page with the four
   named active narrative surfaces is acceptable scope tightening.
3. Confirm that source/test enforcement remains a follow-on bridge item because
   the active PAUTH forbids `source_code_mutation` and this work item is the
   formalization/narrative-alignment pass.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
