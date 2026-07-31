NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8acf3d52-8dbb-4759-a1b7-41424e4c6cb6
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker; envelope-resolved loyal-opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# LO Proposal Review - WI-5741 spec approval packet postimage completeness - 002

bridge_kind: lo_verdict
Document: gtkb-wi5741-spec-packet-postimage-completeness
Version: 002
Date: 2026-07-29 UTC
Author: Loyal Opposition (claude, harness B)
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5741-spec-packet-postimage-completeness-001.md
Reviewed proposal: bridge/gtkb-wi5741-spec-packet-postimage-completeness-001.md

## Verdict Summary

**NO-GO** on one P1 and two P2 findings.

The defect this proposal identifies is **real, correctly diagnosed, and
correctly located**. I reproduced it: the live v7 packet for
`DCL-SESSION-ROLE-RESOLUTION-001` carries a `full_content` of exactly 10,409
characters, matching the MemBase `description` length exactly, while the
`assertions` field approved in the same write is 7,061 characters and appears
nowhere in the packet. That is a genuine `GOV-ARTIFACT-APPROVAL-001` violation
and the remedial direction is right.

The proposal is blocked because the fix changes `full_content_sha256` for
structured-field updates without analyzing `_autodiscover_packet`, the live
formal-artifact gate path that binds packets by comparing that hash against the
hash of the `--content-file` text. The proposal's explicit risk rebuttal is
false for that consumer, the consequence lands on the named motivating case, the
only gate-facing test proposed cannot detect it, and both copies of the affected
hook are outside `target_paths` so the coupling cannot be repaired under this
authorization.

## Review Independence

Reviewer session context `8acf3d52-8dbb-4759-a1b7-41424e4c6cb6`
(loyal-opposition/claude, harness B). Proposal author session context
`de7aad12-9b24-41c8-849c-de48e349ff62` (prime-builder/claude, harness B).
Present, readable, and distinct. Shared harness ID is not a review boundary
under `.claude/rules/file-bridge-protocol.md` § Review Independence Boundary;
the session contexts are unrelated. No self-review condition.

## Findings

### [P1] F1 - The fix silently breaks the FAB-14 packet-autodiscovery gate; the proposal's risk claim is false for that consumer

**Claim.** Appending postimage blocks to `full_content` changes
`full_content_sha256`, which severs the binding the live formal-artifact
approval gate uses to auto-discover packets - for exactly the class of
invocation this fix targets.

**Evidence.**

1. `gt spec update` / `gt spec record` are in gate scope:
   `.claude/hooks/formal-artifact-approval-gate.py:55` -
   `\b(?:gt(?:\.exe)?|python\s+-m\s+groundtruth_kb)\s+spec\s+(?:record|update)\b`.

2. `_autodiscover_packet` binds on the **content file's** hash, not the packet's
   internal self-consistency (`formal-artifact-approval-gate.py:264-286`, read
   directly):

   ```
   267:  content = content_path.read_text(encoding="utf-8")
   274:  target_hash = _content_hash(content)
   285:  if packet.get("full_content_sha256") != target_hash:
   286:      continue
   ```

   The comparison operand is derived externally from the `--content-file` text
   and does **not** change when the packet changes.

3. The self-consistency validator is a different check
   (`:346-348`): `expected_hash = _content_hash(full_content)` compared against
   the packet's own `full_content`. The proposal's rebuttal - that "appended
   blocks cannot break hash-verification consumers because hash and content
   change together" (lines 152-154) - is true for this validator and **false**
   for `_autodiscover_packet`.

4. The contract is codified in
   `platform_tests/scripts/test_fab14_formal_autodiscovery.py:37-51`: a packet
   whose `full_content` equals the content-file text **is** discovered for
   `gt spec update --id ... --content-file ...`;
   `test_formal_autodiscover_rejects_content_mismatch` (line 69) asserts the
   negative.

5. `main()` (`:421-432`): with no explicit `GTKB_FORMAL_APPROVAL_PACKET` or
   `--formal-approval-packet`, and autodiscovery returning None, the invocation
   is **hard-blocked** with `missing-formal-approval-packet`.

Under the proposal, a structured-field update produces
`full_content = description + appended JSON blocks`, so
`full_content_sha256 != sha256(content-file text)` and autodiscovery can never
match.

**Impact.** The DCL v8 re-derivation - the proposal's own named motivating case,
which carries `--assertions-json` - would produce a packet the gate cannot bind,
forcing either an undocumented workflow change (explicit env var) or a hard
block. A second copy of the same logic exists at
`config/hooks/gtkb-formal-artifact-approval-gate.py:288`, so the divergence is
duplicated across the harness-parity surface. Neither hook file is in
`target_paths`, so the coupling cannot be repaired within the approved scope. No
migration or back-compat story for the hash change is present.

**Recommended action.** Revise to preserve the autodiscovery binding. The
cleanest option, and the one I recommend: leave `full_content` byte-unchanged
(equal to the content-file text, preserving the hash contract for *all* updates)
and carry the structured postimage in **new dedicated packet fields** - for
example `postimage_structured_fields` plus `postimage_sha256` - extending the
packet validator to require them when the invocation supplies structured fields.
This satisfies `GOV-ARTIFACT-APPROVAL-001` completeness without touching the
hash the gate matches on, and keeps the change inside the current
`target_paths`.

Alternatives - teaching `_autodiscover_packet` the serializer, or requiring an
explicit `--formal-approval-packet` for structured updates - both require
expanding `target_paths` to the two hook copies and must be analyzed explicitly
with a migration story for packets already on disk.

### [P2] F2 - `DCL-ARTIFACT-APPROVAL-HOOK-001` is the derivation source of test 3 but is absent from Specification Links

**Claim.** Mandatory specification-linkage gate failure.

**Evidence.** Proposal line 99 states test 3 "Derives from
`DCL-ARTIFACT-APPROVAL-HOOK-001`." That ID does not appear in
`## Specification Links` (lines 105-119). It exists in MemBase at v5 ("Artifact
approval hook must display full native proposal").
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` requires citing every
relevant governing specification, and
`.claude/rules/file-bridge-protocol.md` makes omission a `NO-GO`.

**Impact.** The specification most directly governing the surface being modified
- the approval hook contract - is unlinked. That omission is the plausible root
cause of F1 going unanalyzed. The mechanical applicability preflight did not
catch it because the registry does not trigger on that spec: a textbook case of
the preflight being a floor, not a ceiling.

**Recommended action.** Add `DCL-ARTIFACT-APPROVAL-HOOK-001` to
`## Specification Links` and analyze the proposal against its clauses, including
autodiscovery behavior.

### [P2] F3 - The test plan structurally cannot detect the F1 regression; fast-lane criterion 3 is contested

**Claim.** Proposed test 3 is the only gate-facing test and provably cannot catch
the autodiscovery break. Separately, the change introduces an unspecified
evidence format on which a governance gate's matching semantics would depend.

**Evidence.** `scripts/validate_formal_artifact_packet.py:84-90` calls only
`gate._load_packet` and `gate._validate_packet` - self-consistency validation
only. It never invokes `_autodiscover_packet`. A packet with appended blocks
passes it trivially while being undiscoverable by the live gate.

Separately, the proposal invents a canonical evidence format (fenced JSON
blocks, fixed field order, LF-normalized; lines 70-74) with no specification
defining it. `GOV-RELIABILITY-FAST-LANE-001` criterion 3 requires "no new or
revised requirement or specification"; the proposal asserts "Existing
requirements sufficient" (line 143).

**Fast-lane eligibility overall.** Criterion 1 (origin) PASS - WI-5741 is
`origin=defect`. Criterion 2 (no new API/CLI surface) PASS - the serializer is
private, no new flags. Criterion 4 (small) PASS - 2 source + 2 test files.
Criterion 3 CONTESTED. The work is otherwise legitimately fast-lane-shaped; it
is not too broad for the lane.

**Recommended action.** Add a test exercising `_autodiscover_packet` against a
CLI-generated structured-field packet. Confirm with the owner whether the
postimage evidence format needs a DCL clause - likely yes, given that a
governance gate would depend on it.

### [P3] F4 - `.groundtruth/formal-artifact-approvals/**` in `target_paths` is unnecessary and may fail the implementation-start gate

**Claim.** The proposal declares write authorization over the entire
governance-evidence store while asserting it writes nothing there.

**Evidence.** Lines 26-31 state the envelope "appears in target_paths
declaratively" and "the implementation itself creates or edits no live packet
under that envelope." I confirmed that claim is internally consistent: the
described change is confined to the serializer plus tests, and tests write to
temp paths. But `target_paths` is the authorization surface consumed by
`scripts/implementation_authorization.py`, and
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` permits
`allowed_mutation_classes = ["source", "test_addition", "hook_upgrade"]`. A
governance-evidence path plausibly classifies outside those three classes,
risking a fail-closed at `implementation_authorization.py begin`.

**Impact.** Over-broad authorization on the approval-packet store, contrary to
least privilege, for zero benefit by the proposal's own account, plus a
plausible gate failure at implementation start.

**Recommended action.** Remove the entry.

### [P3] F5 - Record path lacks the backward-compatibility guard the update path gets

**Claim/Evidence.** Test 2 (lines 92-96) pins byte-identical description-only
packets for `cli_spec_update.py`. No equivalent exists for `cli_spec_record.py`;
test 4 (lines 101-103) covers only the structured case. `spec record` is equally
in gate scope (hook line 55), so the record path carries the same hash-stability
exposure with no guard.

**Recommended action.** Mirror test 2 into `test_spec_record.py`.

### [P4] F6 - Imprecise line-range citation

**Claim/Evidence.** Lines 44-45 cite `_merged_fields` at `:157-174` as where the
"row built from the same text PLUS the structured fields" appears. Line 174 is
`fields = {"description": full_content}`; the structured-field assignments are at
`:189-198`. The cited range does not contain the evidence it is offered for.

**Recommended action.** Correct to `:157-201`.

## Gate Checklist

| Gate | Result | Evidence |
|---|---|---|
| `## Specification Links` present | PASS | Lines 105-119, 13 specs |
| Cited specs exist in MemBase | PASS | All 13 verified present. No fabricated IDs. |
| `GOV-ARTIFACT-APPROVAL-001` cited | PASS | Line 107 |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` cited | **FAIL** | Absent from Specification Links yet cited at line 99 as a derivation source. See F2. |
| Spec-to-test mapping complete | **PARTIAL FAIL** | Update path mapped; record path has one test and no backward-compat guard. See F5. |
| `## Prior Deliberations` substantive | PASS | Lines 121-127; all four DELIB IDs verified real |
| `## Owner Decisions / Input` non-empty | PASS | Lines 129-139; fast-lane waiver of per-fix approval packets recorded |
| Project-linkage metadata lines | PASS | Lines 16-18 |
| PAUTH active / unexpired / covers WI-5741 | PASS | `status=active`, `expires_at=null`, `included_work_item_ids=null` (covers by active project membership); WI-5741 `project_name=PROJECT-GTKB-RELIABILITY-FIXES`, project `status=active` |
| `## Requirement Sufficiency`, one operative state | PASS (contested) | Lines 141-145. See F3. |
| Risk/rollback present | PRESENT BUT DEFECTIVE | Lines 147-154 contain the false claim in F1 |
| Acceptance criteria / verification plan | PASS | Lines 158-163 |
| Root-boundary compliance | PASS | All five paths in-root |
| `Recommended commit type` | PASS | Line 156, `fix` |
| Body status token first non-blank line | PASS | `NEW` |
| Version chain | PASS | `-001` is the only file for this slug |

## Defect Reality Assessment

The defect is **real**. In `cli_spec_update.py`, `full_content` is the raw
`--content-file` text (line 213), passed unmodified to `_build_packet` (line
244) and on to `construct_approval_packet(full_content=full_content)` (lines
141-154). Separately, `_merged_fields` (lines 157-201) builds the row as
`description=full_content` **plus** `assertions` (191-192), `constraints`
(193-194), `tags` (189-190), `affected_by` (195-196), and `source_paths`
(197-198). Those structured fields mutate the row and never enter the packet.
`cli_spec_record.py` shares the pattern (`_build_packet` at 168-181;
`description=full_content` at 265; `assertions=assertions` at 274).

Empirically: the live v7 packet carries a `full_content` of exactly 10,409
characters; MemBase `DCL-SESSION-ROLE-RESOLUTION-001` v7 has
`description=10409` and `assertions=7061`. The packet length equals the
description length exactly, so 7,061 characters of assertions approved in the
same write are absent from the approval evidence. The proposal's factual claims
are accurate and the direction of the fix is sound. Only the design is unsafe.

## Prior Deliberations

- `DELIB-202667528`, `DELIB-202667526`, `DELIB-202667220`, `DELIB-202667523` -
  cited by the proposal; all four verified to resolve in the Deliberation
  Archive.
- `DELIB-20264088` - GTKB-GOV-CODE-QUALITY-BASELINE Slice 2 Review (REVISED-2).
  Prior treatment of packet/evidence completeness expectations.
- `DELIB-20263065` - Loyal Opposition Review, TAFE Candidate Spec Promotion.
  Precedent on spec-postimage completeness at promotion time.
- `bridge/gtkb-wi5679-session-role-keying-continuity-016.md` and
  `bridge/gtkb-wi5718-retired-session-role-authority-purge-012.md` - surfaced by
  the applicability preflight as path evidence; both touch the same
  approval-packet surface.

## Applicability Preflight

- packet_hash: `sha256:3ac46611e8247a5f86e98d64e1aba339bb3e0f15cba42aade6189d014a33e5bf`
- candidate_evidence_hash: `sha256:6e1fa7af629feb147296e6908c20ee3b05b6d7764f230e4424f7f23cd98dcfe8`
- bridge_document_name: `gtkb-wi5741-spec-packet-postimage-completeness`
- declared_target_paths: [".groundtruth/formal-artifact-approvals/**", "groundtruth-kb/src/groundtruth_kb/cli_spec_record.py", "groundtruth-kb/src/groundtruth_kb/cli_spec_update.py", "platform_tests/groundtruth_kb/cli/test_spec_record.py", "platform_tests/groundtruth_kb/cli/test_spec_update.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5741-spec-packet-postimage-completeness-001.md`
- operative_file: `bridge/gtkb-wi5741-spec-packet-postimage-completeness-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Exit code: 0.

Note: `missing_required_specs` is empty, yet F2 identifies a genuinely missing
specification link. The registry does not trigger on
`DCL-ARTIFACT-APPROVAL-HOOK-001` for these paths. The mechanical floor passed;
reviewer judgment supplies the ceiling, exactly as
`.claude/rules/file-bridge-protocol.md` § Mandatory Applicability Preflight Gate
requires.

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5741-spec-packet-postimage-completeness`
- Operative file: `bridge\gtkb-wi5741-spec-packet-postimage-completeness-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

Exit code: 0. No blocking gap; no owner waiver required.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5741-spec-packet-postimage-completeness`
  -> exit 0, `missing_required_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5741-spec-packet-postimage-completeness`
  -> exit 0, 0 blocking gaps.
- Direct read of `.claude/hooks/formal-artifact-approval-gate.py:264-289`
  -> confirmed `target_hash = _content_hash(content)` at 274 and the
  `full_content_sha256 != target_hash` continue at 285.
- `Select-String -Path .claude/hooks/formal-artifact-approval-gate.py -Pattern '_content_hash|full_content_sha256|target_hash'`
  -> hits at 86, 229, 274, 285, 346, 347, 348; confirms the two distinct
  comparison sites.
- Direct reads of `groundtruth-kb/src/groundtruth_kb/cli_spec_update.py` and
  `cli_spec_record.py` -> confirmed the packet/row divergence.
- MemBase queries for all 13 cited specifications, the four cited deliberations,
  `current_project_authorizations`, and WI-5741 -> all resolve.
- Live packet inspection for `DCL-SESSION-ROLE-RESOLUTION-001` v7 ->
  `full_content` 10,409 chars vs `description` 10,409 / `assertions` 7,061.

## Prime Builder Implementation Context

| Element | Detail |
|---|---|
| Objective | Carry the complete spec postimage into approval packets without breaking the FAB-14 autodiscovery binding. |
| Preconditions | The defect diagnosis stands and needs no re-derivation. |
| Evidence paths | `.claude/hooks/formal-artifact-approval-gate.py:55`, `:264-286`, `:346-348`, `:421-432`; `config/hooks/gtkb-formal-artifact-approval-gate.py:288`; `platform_tests/scripts/test_fab14_formal_autodiscovery.py:37-51`, `:69`; `groundtruth-kb/src/groundtruth_kb/cli_spec_update.py:141-154`, `:157-201`, `:213`, `:244`; `cli_spec_record.py:168-181`, `:265`, `:274`; `scripts/validate_formal_artifact_packet.py:84-90`. |
| File touchpoints | The two CLI modules and two test modules already in `target_paths`, if the dedicated-postimage-fields option is chosen. The two hook copies only if an autodiscovery-teaching option is chosen, which requires widened `target_paths`. |
| Implementation sequence | 1. Choose the binding-preserving design. 2. Add `DCL-ARTIFACT-APPROVAL-HOOK-001` to Specification Links with clause analysis. 3. Add the `_autodiscover_packet` test. 4. Mirror the backward-compat test to the record path. 5. Drop the `.groundtruth/formal-artifact-approvals/**` target. 6. Correct the line-range citation. 7. Re-file as `REVISED`. |
| Verification steps | A CLI-generated structured-field packet must still be discovered by `_autodiscover_packet`; description-only packets must remain byte-identical on both CLI paths; both preflights re-run clean. |
| Rollback notes | Additive packet fields are revertible without touching already-issued packets, which is a further argument for that option. |
| Open decisions | Whether the postimage evidence format requires a DCL clause (bears on fast-lane criterion 3) - owner input, see below. |

## Owner Decisions / Input

The proposal's own `## Owner Decisions / Input` (lines 129-139) is non-empty and
substantive: it cites the fast-lane waiver of per-fix approval packets and
`AUQ-20260729-DCL-V8-REDERIVATION`, which I corroborated against WI-5741's
`source_owner_directive`. That section satisfies the mandatory gate and is not a
basis for this NO-GO.

One owner decision is raised by F3 and is **not** blocking for the revision: the
proposal introduces a canonical postimage evidence format on which a governance
gate would depend. `GOV-RELIABILITY-FAST-LANE-001` criterion 3 requires no new
or revised specification for fast-lane eligibility. Prime Builder should confirm
with the owner, via `AskUserQuestion`, whether that format is to be pinned by a
DCL clause, and record the answer in the revised proposal. Prime Builder may
draft the revision addressing F1, F2, F4, F5, and F6 without waiting on that
answer.

## Owner Action Required

None blocking this verdict. The F3 format-specification question should be put to
the owner via `AskUserQuestion` during revision, not before it.

## Recommended Commit Type

Not applicable - this is a `NO-GO` verdict, not an implementation. The revised
proposal should retain `fix`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
