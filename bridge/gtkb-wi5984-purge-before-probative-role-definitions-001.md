NEW
::init gtkb pb
::open build

# gtkb-wi5984-purge-before-probative-role-definitions — Add the purge-before-probative-language standing directive to the Prime Builder rule set

bridge_kind: prime_proposal
Document: gtkb-wi5984-purge-before-probative-role-definitions
Version: 001
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-08-07 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8038611d-3a31-49fb-ad15-9f00b0ef3d25
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5984

target_paths: [".claude/rules/prime-builder.md", ".groundtruth/formal-artifact-approvals/2026-08-07-prime-builder-rule-set.json"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner standing directive `DELIB-20260806011917` (2026-08-07) establishes that
probative language is a last resort: when a surface carries obsolete, incorrect,
or superseded direction, the correct remedy is deletion at the source. The
owner's verbatim change request, captured in the approval packet, is: *"This
instruction needs to be added to the base PB and LO role definitions. It is very
important."*

This proposal implements the **Prime Builder half** of that directive: append a
`## Correcting Direction - Purge Before Probative Language` section to
`.claude/rules/prime-builder.md`, the Prime Builder rule set (the
mandatory-behavior contract, distinct from `prime-builder-role.md`, the
role-assignment record, per the HYG-027 scope note).

The change is fully pre-approved and byte-pinned. The narrative-artifact
approval packet at
`.groundtruth/formal-artifact-approvals/2026-08-07-prime-builder-rule-set.json`
carries `artifact_type: narrative_artifact`, `action: update`,
`target_path: .claude/rules/prime-builder.md`, `approval_mode: approve`,
`presented_to_user: true`, `transcript_captured: true`,
`source_ref: DELIB-20260806011917`, and the complete 3,559-character approved
post-edit content with
`full_content_sha256: 8903abf36b990a1b2e37fd2a6743ca66eccbc4e43ae5370f37804f8de485b95c`.

Implementation is therefore mechanical rather than authored: write the packet's
`full_content` verbatim to the target path. No content is composed by Prime
Builder.

**Why the approval-packet path appears in `target_paths`.** The second declared
path,
`.groundtruth/formal-artifact-approvals/2026-08-07-prime-builder-rule-set.json`,
is declared for approval-evidence completeness per the bridge publication
guard's `target_paths` check, which requires a proposal citing approval-packet
evidence to name the concrete packet. The packet is **read-only** in this
implementation: it is the authority for the content and its hash, and Prime
Builder neither creates, edits, nor consumes it. The concrete file is declared
rather than the `.groundtruth/formal-artifact-approvals/**` envelope so the
authorized surface stays minimal.

**Verified pre-implementation state (this session, read-only):**

- Packet integrity confirmed: `full_content` hashes to its own declared
  `full_content_sha256` **under UTF-8 with LF line endings**. The same content
  encoded CRLF hashes to `5e40abf6...` and does **not** match. The
  implementation must therefore write LF-only; a CRLF write silently breaks the
  approval-gate hash match.
- Current file hash is `ce57dfe5ef7ac26c8eacc92cbb20348590143046d7e6563e32f6474274b8e892`,
  which differs from the packet hash, so the edit is **not yet applied**.
- The diff is a single append-only hunk of 27 added lines at line 46, following
  `If something looks wrong — ASK rather than act.` No existing line is modified
  or deleted.

**Scope boundary — the Loyal Opposition half is deliberately excluded.** The
owner directive names both role definitions, but no narrative-artifact approval
packet exists for `.claude/rules/loyal-opposition.md` under this directive; the
LO packets present in `.groundtruth/formal-artifact-approvals/` are older and
unrelated (2026-06-03 through 2026-07-18, covering Agent Red reference-adopter
framing, investigation methodology, peer-review weighting, and WI-5492).
Implementing the LO half without a packet would violate
`GOV-ARTIFACT-APPROVAL-001`. This proposal therefore covers PB only and records
the LO gap explicitly rather than silently dropping half of an owner directive
marked "very important." The LO half requires its own owner-presented approval
packet before it can be proposed; that is stated here as the concrete follow-on
condition, not deferred without trace.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` — the formal/narrative artifact approval gate.
  This work is executable precisely because a conforming narrative packet with
  matching content hash already exists; the LO half is excluded because one does
  not.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority; this proposal
  is filed as the append-only `-001` of a new numbered chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires citation
  of every governing specification; satisfied by this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the
  project/PAUTH/work-item triple; supplied in the header and validated read-only
  against MemBase by `scripts/gtkb_propose_scaffold.py`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must execute
  tests derived from the linked specs; the plan below is hash- and
  gate-based rather than prose assertion.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds only
  under the cited active PAUTH plus a live bridge `GO` and an
  implementation-start packet.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — no bypass is claimed; the
  pre-existing approval packet authorizes the *content*, not the implementation,
  which still requires independent `GO`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every hash, packet field, and diff claim
  above derives from a fresh read of live state at proposal time.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the single target path
  `.claude/rules/prime-builder.md` is inside `E:/GT-KB`; no artifact is created,
  read as a live dependency, or written outside the platform root, and nothing
  under `applications/` is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — this proposal propagates an already
  captured owner directive into the durable agent-visible role surface rather
  than leaving it as conversation-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the directive becomes a durable
  narrative artifact under change control, not transient session guidance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the owner directive crossed the
  capture threshold at `DELIB-20260806011917`; installing it in the role rule set
  is the corresponding artifact-update trigger.

## Prior Deliberations

- `DELIB-20260806011917` — *Standing directive: purge obsolete information
  before writing probative language*. The authorizing owner directive and the
  packet's `source_ref`. This proposal implements it rather than reinterpreting
  it; the section text is taken verbatim from the approved packet content.
- `.groundtruth/formal-artifact-approvals/2026-08-07-prime-builder-rule-set.json`
  — the narrative approval packet, read in full and integrity-checked before
  drafting.
- No prior bridge thread exists for WI-5984; `bridge/` contains no `*wi5984*`
  files at proposal time, so this is the first version of a new chain and there
  is no prior verdict history to build on or differ from.

## Owner Decisions / Input

This proposal depends on owner approval. The authorizing evidence is the owner
directive captured in two places, both read fresh at proposal time:

1. `DELIB-20260806011917` (`source_type: owner_conversation`,
   `source: owner-directive-2026-08-07-purge-before-probative`) — the standing
   directive itself, including the owner's verbatim statement of the rule and
   its purge → replace → probative ordering.
2. The approval packet's `explicit_change_request` field, recording the owner's
   verbatim scope instruction: *"This instruction needs to be added to the base
   PB and LO role definitions. It is very important."* The packet further
   records `presented_to_user: true` and `transcript_captured: true`, satisfying
   the `GOV-ARTIFACT-APPROVAL-001` display-and-audit requirement.

No further owner decision is required to review or implement the Prime Builder
half. The Loyal Opposition half **does** require a new owner decision — namely
presentation and approval of an LO narrative packet — and is excluded from this
proposal's scope for exactly that reason.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed
before implementation. The governing requirements are `GOV-ARTIFACT-APPROVAL-001`
(approval-packet gate), `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` with
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (authorization chain), and
`GOV-FILE-BRIDGE-AUTHORITY-001` (bridge protocol). The directive being installed
is itself already a captured owner standing directive at `DELIB-20260806011917`;
this proposal does not create policy, it propagates approved policy text into the
agent-visible role surface.

## Spec-Derived Verification Plan

| Linked specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` | `(Get-FileHash .claude/rules/prime-builder.md -Algorithm SHA256).Hash` after the edit | equals `8903abf36b990a1b2e37fd2a6743ca66eccbc4e43ae5370f37804f8de485b95c` (the packet's `full_content_sha256`) |
| `GOV-ARTIFACT-APPROVAL-001` | the `narrative-artifact-approval-gate.py` PreToolUse hook fires on the Write | Write permitted (packet present, content hash matches); a CRLF write must be caught here as a hash mismatch |
| `GOV-ARTIFACT-APPROVAL-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_narrative_artifact_evidence.py --staged` at commit time | PASS for the staged narrative path |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `git diff --stat -- .claude/rules/prime-builder.md` | 27 insertions, 0 deletions — append-only, no existing line modified |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5984-purge-before-probative-role-definitions` | chain is append-only; the report version follows `GO` |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5984-purge-before-probative-role-definitions` after `GO` | `authorized: true`, scoped to the single declared `target_path` |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | re-read the packet and re-hash the target immediately before editing | packet unchanged; target still at `ce57dfe5...` (edit not applied by another session in the interim) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5984-purge-before-probative-role-definitions` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5984-purge-before-probative-role-definitions` | `preflight_passed: true`, `missing_required_specs: []`, blocking gaps `0` |

### Spec-to-Test Mapping

Executed spec-derived tests, not assertions. Each linked specification that has
a mechanical enforcement surface maps to an existing test that exercises that
surface; all are run before the implementation report is filed.

| Specification | Test (spec-derived) | Command | Expected |
| --- | --- | --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` | `platform_tests/hooks/test_narrative_artifact_approval.py` — exercises the PreToolUse gate that admits a narrative write only on packet presence + content-hash match, the exact mechanism admitting this edit | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_narrative_artifact_approval.py -q --no-header` | all pass |
| `GOV-ARTIFACT-APPROVAL-001` | `platform_tests/scripts/test_check_narrative_artifact_evidence.py` — exercises the pre-commit evidence checker that gates the commit of this staged narrative path | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_narrative_artifact_evidence.py -q --no-header` | all pass |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `platform_tests/scripts/test_groundtruth_governance_adoption.py` — asserts the governed `.claude/rules/*.md` adoption contract over the rule-file set this edit modifies | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_groundtruth_governance_adoption.py -q --no-header` | all pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_fab15_role_narrative.py` — role-narrative contract over the PB/LO role surfaces, the specific artifact class this proposal edits | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab15_role_narrative.py -q --no-header` | all pass |

A pre-implementation baseline run of all four suites is captured before the edit
and re-run after, so any delta is attributable to this change rather than to
pre-existing tree state. That baseline discipline is adopted deliberately: in
this same session, six failures in adjacent implementation-authorization suites
were only shown to be pre-existing by re-running them against `HEAD`.

## Risk / Rollback

**Risk surface.** One narrative rule file, append-only. No source, test,
configuration, MemBase, PAUTH, dispatcher/TAFE, or bridge file is modified. The
added text is owner-approved verbatim, so there is no authoring risk.

**Principal risk — line-ending encoding.** The approval gate matches on content
hash. Writing the packet content with CRLF produces `5e40abf6...` instead of
`8903abf3...` and fails the gate. On Windows this is a live hazard: git's
`core.autocrlf` and several editors normalize silently. The implementation must
write LF-only and verify by re-hashing before staging. This is called out
explicitly because the failure is silent at authoring time and only surfaces at
the gate.

**Secondary risk — partial directive.** Implementing PB without LO leaves an
owner directive marked "very important" half-applied. Mitigated by recording the
LO packet requirement explicitly in this proposal rather than closing WI-5984 on
the PB half alone; WI-5984 should remain open until the LO half lands.

**Rollback.** Single-commit `git revert <sha>` restores the prior file exactly;
the edit is a pure append with no deletions, so revert cannot lose adjacent
content. No database, dispatcher, or PAUTH state changes, so there is no
non-git rollback component.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5984-purge-before-probative-role-definitions`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs:` — a governance/rule-file-only edit. Per the Conventional Commits type
discipline in `.claude/rules/file-bridge-protocol.md`, `docs:` covers
governance/rule/runbook-only changes. No module, script, interface, or test is
added, so `feat:` would overstate the diff; the change is directive content
rather than maintenance, so `chore:` would understate it.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
