NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e551d95-6728-46fd-b64d-181c9617a827
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; activity build

bridge_kind: prime_proposal
Document: gtkb-w0-executable-go-pre-verdict-validation
Version: 001
Date: 2026-08-06 UTC
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5889
target_paths: ["scripts/pre_verdict_executability_check.py", ".claude/skills/gtkb-verify/helpers/write_verdict.py", ".codex/skills/gtkb-verify/helpers/write_verdict.py", ".cursor/skills/gtkb-verify/helpers/write_verdict.py", "scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/rules/file-bridge-protocol.md", ".claude/rules/codex-review-gate.md", "platform_tests/scripts/test_pre_verdict_executability_check.py", ".groundtruth/formal-artifact-approvals/**"]

# Executable GO - Pre-Verdict Executability Validation (Wave 0 Livelock Breaker)

## Summary

A GO that cannot be executed is worse than a NO-GO: it consumes an independent
review cycle, authorizes nothing, and routes the thread into the
NO-ACTION -> corrected-verdict loop. Measured across the current bridge corpus,
45% of GO verdicts are followed by a Prime NO-ACTION because four gates are
evaluated only AFTER approval: project-authorization mutation-class match,
cross-harness target parity, verdict section completeness, and claim/packet
mintability (one of which decays with time). 148 GOs across the 87 GO-latest
threads have produced zero accepted implementations; the WI-5767 thread alone
burned 16 versions, 6 GOs, and 4 NO-ACTIONs on exactly these four gates.

This proposal moves all four gates to the pre-verdict boundary:

1. NEW deterministic checker `scripts/pre_verdict_executability_check.py`
   (exit 0 = executable, exit 5 = named machine-readable gaps).
2. GO-refusal wiring in the verify helper
   `.claude/skills/gtkb-verify/helpers/write_verdict.py` plus a mandatory
   concrete `author_session_context_id` for every verdict body it emits.
3. Writer-side NO-ACTION validation in `scripts/gtkb_bridge_writer.py`
   (reject on ADVISORY-latest; native prior-LO-verdict check).
4. Unfilled-placeholder gate in `.claude/hooks/bridge-compliance-gate.py`
   (grandfathered, mirroring the body-status-token rule convention).
5. Docs: the pre-GO executability step in the LO checklist plus the
   currently-undocumented envelope-activity / bridge_kind rules.
6. One test module with per-gate failure fixtures and a WI-5767 replay.

The reviewer outcome changes from "GO, then Prime discovers non-executability
and files NO-ACTION" to "checker exit 5, reviewer files an actionable NO-GO
citing the specific named gap" - which is a lawful, dispatchable, forward-moving
status instead of a post-GO correction loop.

## Motivating Evidence - the four WI-5767 post-GO gate failures

The `bridge/gtkb-wi5767-auto-finalize-sweep-liveness` chain (versions 001-016)
contains four Prime NO-ACTIONs, each rejecting a fresh LO GO for a defect that
was mechanically detectable before the GO was written. These four are the
checker's four gate fixtures:

1. **PAUTH mutation-class (NO-ACTION -003, rejecting GO-002).** Fresh
   operation-time evaluation of the exact v001 proposal failed closed: "The
   active cited whole-project PAUTH permits source, test addition, governance
   evidence, and bridge work, but `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`
   classifies as `configuration`. The evaluator returned
   `target_mutation_class_not_allowed`" (-003, evaluator packet
   `sha256:9ce3c10a5b68749fed984ddfb5287846864b9954f151bb133774fccd90be20a5`).

2. **Cross-harness parity (NO-ACTION -007, rejecting GO-006).** "The Codex
   path is absent from v005 `target_paths`" while
   `.codex/skills/gtkb-bridge-propose/helpers/write_bridge.py` is a separate
   byte-identical tracked file with an exact byte-parity test assertion;
   "Editing the Codex copy would be an unauthorized seventh-target expansion"
   (-007). The reviewed implementation was internally unsatisfiable.

3. **Verdict section completeness (NO-ACTION -011, rejecting GO-010).**
   "Version 010 contains an Applicability Preflight section but omits the
   mandatory Clause Applicability output, executed result, clause counts, and
   blocking-gap result required for an executable Loyal Opposition GO" (-011;
   structural probe `rg -n "^## Clause Applicability|..."` exited 1 with no
   matches on the GO file).

4. **Staleness / mintability (NO-ACTION -013, rejecting GO-012).** "The
   version 012 LO GO is stale: no active work-intent claim, no active
   implementation-start packet, no dirty target paths, no pending Prime
   Builder continuation, and no owner request to activate this work item"
   (-013).

Separately measured and addressed by changes 2-4: missing
`author_session_context_id` on LO verdicts triggers the fail-closed
self-review refusal at finalization time; NO-ACTION is misused as
closure/parking (18 threads / 153 versions; see also WI-5850 and WI-5853);
and 238 occurrences of the unfilled template placeholder phrase
"fill in reason before filing" survive across 222 committed bridge files
(live count, 2026-08-06).

## Proposed Changes (all anchors verified at HEAD, 2026-08-06)

### 1. NEW `scripts/pre_verdict_executability_check.py`

Deterministic, read-only CLI:

```
python scripts/pre_verdict_executability_check.py --bridge-id <slug> [--json] [--draft-verdict-body <file>]
```

Resolves the thread's latest NEW/REVISED/NO-ACTION proposal/report through the
canonical thread readers in `scripts/bridge_thread_files`
(`versioned_bridge_files`, `status_from_bridge_file` - the same readers
`gtkb_bridge_writer._thread_state` uses at lines 517-536), then evaluates four
gates against that latest operative file:

- **Gate A - PAUTH mutation-class.** Parse targets with
  `implementation_authorization.extract_target_paths` (line 887). Classify
  each with the canonical operation-time evaluator
  `groundtruth_kb.governance.project_authorization_operation_time`
  (`classify_target`, `evaluate_envelope`, `load_operation_taxonomy`) - the
  exact module `scripts/implementation_authorization.py::_operation_time_api`
  loads fail-closed at lines 1061-1073. **Import, do not fork.** Resolve the
  proposal's cited `Project Authorization:` row read-only and emit a gap
  (`pauth_mutation_class_not_allowed`, with path and class) for every
  classified mutation class outside `allowed_mutation_classes`, and
  (`pauth_metadata_missing`) when an implementation-kind proposal lacks the
  three project-linkage metadata lines.

- **Gate B - cross-harness parity.** For every target under
  `.claude/skills/**` or `.claude/hooks/**`, enumerate on-disk counterpart
  projections (same relative path under `.codex/`, `.cursor/`, `.goose/`;
  `groundtruth-kb/templates/hooks/<name>` for hooks). Emit
  `cross_harness_projection_missing` when a counterpart exists on disk but is
  neither listed in `target_paths` nor named in a projection-regeneration
  step in the proposal body.

- **Gate C - verdict-completeness preconditions.** Invoke both preflights NOW
  as subprocesses: `scripts/bridge_applicability_preflight.py --bridge-id
  <slug>` (require `preflight_passed: true`, empty `missing_required_specs`)
  and `scripts/adr_dcl_clause_preflight.py --bridge-id <slug>` in mandatory
  mode (its exit 5 = blocking clause gap; contract confirmed in its help
  text). When `--draft-verdict-body` is supplied, additionally require the
  draft to contain the `## Applicability Preflight` and
  `## Clause Applicability` headings (`verdict_sections_missing`).

- **Gate D - mintability (claim-probe + packet prerequisites).** Probe the
  work-intent claim via the `scripts/bridge_claim_cli.py` status surface:
  the claim must be free or held by the current session flow
  (`claim_held_by_foreign_session` otherwise). Then check the deterministic
  packet-shape prerequisites without writing anything: `## Requirement
  Sufficiency` present with a bounded recognized phrase
  (`REQUIREMENT_SUFFICIENCY_RE`, `implementation_authorization.py` lines
  75/751-755), `target_paths` extractable, and the cited PAUTH row active and
  unexpired. NOTE on the dry-run question posed by the work packet:
  `implementation_authorization.py begin --no-write` already exists (lines
  3314-3316) as the no-write packet probe, but `create_authorization_packet`
  requires a live latest-GO, so it cannot run at pre-verdict time. Gate D is
  therefore documented as claim-probe plus prerequisite checks; **no new
  `--dry-run` flag is added anywhere.**

Exit contract: `0` = executable; `5` = named gaps, one machine-readable entry
per gap (`{"gate": "A|B|C|D", "code": ..., "detail": ...}`) with `--json`, and
human-readable lines otherwise; `2` = usage/thread-resolution error. The 0/5
convention deliberately mirrors `adr_dcl_clause_preflight.py`.

### 2. GO-refusal wiring in the verify helper (drift-corrected)

Verified current state of
`.claude/skills/gtkb-verify/helpers/write_verdict.py`: `main()` (lines
1395-1483) is the seeding/emit path all verdict drafting flows through; the
`--finalize-verified` branch is VERIFIED-only. `validate_verified_body` (line
294) rejects non-VERIFIED first tokens; `_assert_verdict_review_independence`
(line 1054) and `_assert_verdict_author_session_context_is_real` (line 1093)
fire only on the VERIFIED finalization path. **There is currently no GO-time
gate and no author-session requirement on the GO/NO-GO drafting path.** (The
work packet's phrase "before writing a GO verdict" maps to this seeding/emit
path; the helper's GO output is what reviewers publish through the governed
writer.)

Changes:

- In `main()`, when the body's first non-blank token (per
  `_first_nonblank_line`, line 229) is `GO`: run the Gate 1 checker for
  `--slug`; on exit 5, refuse to emit the seeded body, print the named gap
  list to stderr, and exit 5. The reviewer files a NO-GO citing the specific
  gaps instead - that NO-GO is actionable, unlike a post-GO NO-ACTION loop.
  Owner-authorized escape hatch `GTKB_PRE_VERDICT_CHECK_BYPASS=1` (for
  checker-infrastructure debugging only; every use appended to the verify
  audit log), mirroring the `GTKB_SOT_READ_DISCIPLINE_BYPASS` convention.
- Require a concrete `author_session_context_id` in EVERY verdict body
  `main()` emits (GO, NO-GO, and VERIFIED drafts): hard error when the field
  is absent or synthetic, using the already-imported
  `extract_author_metadata` / `is_synthetic_session_context_id` from
  `scripts.bridge_author_metadata` (imports at lines 39-42). This closes the
  measured failure where verdicts drafted without author session metadata are
  refused fail-closed only later, at self-review/finalization time.
- Projection regeneration step (Gate B applied to ourselves):
  `.codex/skills/gtkb-verify/helpers/write_verdict.py` is byte-identical to
  the canonical helper (sha1 cd31d2b4... verified) and is regenerated
  byte-for-byte; `.cursor/skills/gtkb-verify/helpers/write_verdict.py` is
  content-identical with CRLF line endings (diff after CR-strip = 0 lines)
  and is regenerated preserving CRLF. The `.goose/` copy carries pre-existing
  ~2,833-line content drift (an older helper generation); it is **excluded**
  from this cohort, disclosed here, and flagged for a follow-on
  projection-reconciliation work item rather than blind-overwritten.

### 3. Writer-side NO-ACTION validation in `scripts/gtkb_bridge_writer.py` (drift-corrected)

Verified current state: the compliance-gate hook ALREADY enforces
prior-verdict presence (`_no_action_prior_verdict_deny`) and close-intent
rejection (`_no_action_close_intent_deny`, WI-5850 emergency-bootstrap), and
`write_bridge_file` runs that gate on every helper-managed write via
`run_bridge_compliance_audit` (lines 174-222, subprocess `--audit-only`,
fail-closed on non-pass). So the work packet's condition (b) - "no prior LO
GO/NO-GO verdict in the chain" - is already covered transitively at the
writer boundary.

Remaining verified gap: **ADVISORY-latest.** A thread with an early GO/NO-GO
whose LATEST entry is ADVISORY passes the existing lower-numbered-sibling
scan, but `ORDINARY_TRANSITIONS` in `scripts/bridge_lifecycle_resolver.py`
(dict at line 43; ADVISORY row at line 49) excludes NO-ACTION as an ADVISORY
successor - writing it mis-routes a Prime-actionable advisory into the LO
queue with no verdict to correct.

Change: native validation in `write_bridge_file`, after
`status = _first_status(content_to_write)` (line 1214). When status is
`NO-ACTION`: resolve the thread's latest status through the same
`scripts.bridge_thread_files` readers `_thread_state` uses (lines 517-536),
then (a) raise `BridgeTransitionError` when the latest status is `ADVISORY`,
citing `DCL-NO-ACTION-STATUS-SEMANTICS-001` and the `ORDINARY_TRANSITIONS`
code of record; and (b) raise when no prior LO GO/NO-GO exists anywhere in
the chain - a native belt-and-braces duplicate of the hook check so the
writer boundary does not depend solely on the subprocess audit being loadable.
First-version (`-001`) NO-ACTION writes fail check (b) by construction.

### 4. Unfilled-placeholder gate in `.claude/hooks/bridge-compliance-gate.py`

Verified current state: the existing check (lines 2290-2303) fires only for
NEW/REVISED implementation-proposal kinds and only on the exact unedited
Prior Deliberations placeholder line (`NO_PRIOR_DELIBS_PLACEHOLDER`, line
169). That narrow scope is how 238 occurrences of the placeholder phrase
across 222 committed bridge files (live grep count, 2026-08-06) reached the
corpus through verdict files, non-implementation kinds, and other sections.

Change: add `_unfilled_placeholder_violation(file_path, content)` to
`_deny_reason_for_content` for NEW/REVISED versioned bridge files
(`PENDING_PREFLIGHT_STATUSES`), any bridge_kind, any section:

- Regex mirrors the verify helper's `UNRESOLVED_PLACEHOLDER_RE`
  (`write_verdict.py` lines 53-54):

  ```
  \bPLACEHOLDER(?:_[A-Z0-9]+)+\b|<fill in [^>\n]+>
  ```

  matched against content with fenced ``` code spans stripped (the gate
  already has fence-aware collection in `_collect_section_lines`), so
  documentation examples quoting the template never false-block.
- Grandfathering mirrors the body-status-token convention exactly
  (`_body_status_token_violation` + `_ondisk_first_nonblank_line`, lines
  785-835): block when the file is new on disk or the on-disk content is
  placeholder-clean; allow when the on-disk file already carries an unfilled
  placeholder (historical files are never retroactively broken).
- The same check block is added to the tracked template at
  `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. Disclosed
  pre-existing condition: the activated hook and the template currently
  diverge (sha1 dafe6d19... vs c49e5196..., apparently the WI-5850
  emergency additions not yet backported); this proposal adds the identical
  new block to both files and does NOT otherwise reconcile that divergence
  (flagged for follow-on). The `.codex/gtkb-hooks/` compliance adapters
  subprocess the canonical hook and need no edit.

### 5. Docs: `file-bridge-protocol.md` + `codex-review-gate.md`

- `.claude/rules/file-bridge-protocol.md`: insert a "Mandatory Pre-GO
  Executability Gate" subsection into the Loyal Opposition workflow: run
  `python scripts/pre_verdict_executability_check.py --bridge-id
  <document-name>`; `GO` is valid only on exit 0; exit 5 requires a NO-GO
  citing the emitted gap list. Also document the currently-undocumented
  envelope-activity rules from the writer code of record
  (`default_bridge_envelope_activity`, `gtkb_bridge_writer.py` lines 259-266;
  `LO_ENVELOPE_BRIDGE_KINDS` line 78): Prime filings (NEW/REVISED/NO-ACTION)
  default to `::open build`; LO verdicts (GO/NO-GO/VERIFIED, or `bridge_kind`
  in {lo_verdict, loyal_opposition_review, verification_verdict}) default to
  `::open test` with `bridge_kind: lo_verdict` on verdict entries - closing
  the undocumented-rule tax measured at roughly one trial-and-error episode
  per session. Backlog note: WI-5901/WI-5903 track an owner-side
  clarification that `::open build` may be declared sufficient for LO verdict
  work; the docs will describe the current code-of-record default and cite
  those WIs so a later owner decision supersedes cleanly (no conflict - this
  slice documents, it does not change, the activity default).
- `.claude/rules/codex-review-gate.md`: add the checker as an enforcement
  step in "If Loyal Opposition is reviewing an implementation proposal"
  (between the clause preflight and verdict-section steps): run the checker,
  treat exit 5 as a NO-GO blocker naming the gaps.
- Both files are protected narrative artifacts: per-artifact approval packets
  under `GOV-ARTIFACT-APPROVAL-001` are required at implementation time (the
  governing whole-project PAUTH's scope summary restates this; class
  authorization does not substitute).

### 6. Tests: `platform_tests/scripts/test_pre_verdict_executability_check.py`

- One fixture thread per gate where exactly that gate fails; assert exit 5
  plus the named gap code (`pauth_mutation_class_not_allowed`,
  `cross_harness_projection_missing`, `verdict_sections_missing` /
  clause-preflight gap, `claim_held_by_foreign_session` /
  requirement-sufficiency gap).
- One all-pass fixture; assert exit 0 and empty gap list.
- Writer NO-ACTION rejection cases: ADVISORY-latest thread; thread with no
  prior LO verdict (native check, hook unavailable simulation).
- Compliance-gate placeholder cases: new NEW file with placeholder = deny;
  grandfathered on-disk placeholder file = allow; placeholder inside fenced
  code = allow.

## Scope Guards

- NO dispatcher, publisher, or recovery files are touched (Worker 2's lane):
  `gtkb_dispatcher_daemon.py`, publication sidecar/receipt logic, and
  `finalize_pending_bridge_publication` / `rollback_pending_bridge_publication`
  are out of scope.
- NO change to how VERIFIED finalization commits work:
  `finalize_verified_commit`, `validate_verified_body`, staging, hunk-patch,
  and commit mechanics are untouched.
- NO adoption of the drifted `.goose` verify-helper copy (disclosed follow-on).
- NO new GOV/ADR/DCL artifacts and no MemBase schema or record mutation.

## Prior Deliberations

Searches executed 2026-08-06: `gt deliberations search "NO-ACTION verdict
semantics" --limit 5` and `gt deliberations search "GO not executable
implementation authorization packet" --limit 5`, plus targeted follow-ups.

- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` (verified present, v1) -
  owner correction defining NO-ACTION as a Prime rejection of an LO GO/NO-GO
  verdict; the semantic authority behind change 3 and
  `DCL-NO-ACTION-STATUS-SEMANTICS-001`.
- `DELIB-HARNESS-NO-ACTION-LO-RESPONSE-SET-20260702` - owner-approved LO
  responses to NO-ACTION (corrected GO, NO-GO against the NO-ACTION, or
  escalation); the checker keeps threads out of this loop entirely.
- `DELIB-20260708-NO-ACTION-CORRECTION-DRIVE-APPROACH` - owner AUQ driving the
  sequenced NO-ACTION correction program; this proposal is the prevention-side
  complement to that reconciliation drive (see also WI-5853).
- `DELIB-202666041` - GO on documenting canonical NO-ACTION semantics
  (Slice 1); this proposal mechanizes what that slice documented.
- `DELIB-202665927` - owner design charter: error/drift-resistant working
  set; pre-verdict mechanical gates are squarely inside that charter.
- `DELIB-20265057` - NO-GO on stale implementation-start packet handling at
  VERIFIED; prior recognition that packet state decays with time (Gate D).

## Owner Decisions / Input

- Owner AUQ, 2026-08-06: "Expand Wave 0 now" - approves expanding the Wave 0
  livelock-breaker program.
- Owner AUQ, 2026-08-06: "file W0.1/W0.3/W0.4 now" - split-phase adoption;
  this filing is W0.4 Phase 1 (propose). Phase 2 (implement) begins only
  after independent LO GO, fresh claim, and a schema-v3 implementation-start
  packet.
- Owner AUQ set, 2026-08-05: the four plan answers shaping the Wave 0 plan
  (gate composition, split-phase filing, replay-evidence requirement, and
  scope-guard boundaries) are carried into this proposal unchanged.

No additional owner decision is requested by this filing. Protected
narrative-artifact edits (change 5) will present their own per-artifact
approval packets at implementation time.

## Requirement Sufficiency

**Existing requirements sufficient.** This proposal mechanizes
already-normative rules; no new GOV/ADR/DCL is required. Governing
requirements: `DCL-NO-ACTION-STATUS-SEMANTICS-001` (NO-ACTION semantics the
writer will enforce), `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
(two-layer write-time + review-time mechanical enforcement - exactly the
placement of changes 1-4), `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` +
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` (the operation-time
evaluation Gate A moves forward in time), `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
(Gate B), `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (author-session requirement),
and the file-bridge protocol's existing verdict gates (Gate C).

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - applicable because `.claude/rules/file-bridge-protocol.md` is a modified surface; all changes stay within the GT-KB root, touch no `applications/` path, and leave the root/applications boundary untouched.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - canonical NO-ACTION semantics; enforced at the write boundary by change 3.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - write-time + review-time two-layer defense; changes 1-2 are the review-time layer, changes 3-4 the write-time layer.
- `.claude/rules/file-bridge-protocol.md` - modified surface (Review Independence + verdict gates + new pre-GO step + envelope-activity documentation).
- `.claude/rules/codex-review-gate.md` - modified surface (LO enforcement checklist gains the pre-GO executability step).
- `bridge/gtkb-wi5767-auto-finalize-sweep-liveness-001..016` - motivating evidence chain; especially `-003` (PAUTH mutation-class packet failure), `-007` (Codex projection omission), `-011` (missing Clause Applicability), `-013` (stale GO).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol and audit-trail authority; all changes strengthen, none weaken, GO/NO-GO discipline.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation authorization (Gate A authority).
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time evaluation contract Gate A reuses (import, not fork).
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no gate herein bypasses the bridge or the packet chain.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Gate B and the projection-regeneration step for the verify helper.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - mandatory concrete author_session_context_id on emitted verdict bodies.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section's own completeness obligation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item linkage metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived test mapping below.
- `GOV-ARTIFACT-APPROVAL-001` - per-artifact approval packets for the two protected rules-file edits.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - checker evaluates fresh canonical reads (live thread files, live PAUTH rows), never cached scan state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governed artifact lifecycle applies to all six changes.

## Specification-Derived Verification

| Requirement (spec) | Derived test / verification | Command |
| --- | --- | --- |
| Checker exit contract 0/5 with named gaps (GOV-CROSS-CUTTING-...-001) | Per-gate failure fixtures assert exit 5 + gap code; all-pass fixture asserts exit 0 | `python -m pytest platform_tests/scripts/test_pre_verdict_executability_check.py -q` |
| Gate A reuses canonical evaluator, no fork (DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001) | Test asserts checker imports `groundtruth_kb.governance.project_authorization_operation_time` and contains no local taxonomy copy | same module |
| Gate B parity detection (DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001) | Fixture with on-disk counterpart absent from target_paths asserts `cross_harness_projection_missing` | same module |
| Gate C verdict-completeness (file-bridge-protocol verdict gates) | Fixture GO draft without Clause Applicability asserts exit 5 | same module |
| Gate D claim-probe (staleness class) | Foreign-held-claim fixture asserts `claim_held_by_foreign_session`; missing Requirement Sufficiency fixture asserts gap | same module |
| GO-refusal wiring (helper) | Helper invoked with GO body on a gap-bearing fixture thread exits 5 without emitting a body; author-session absence hard-errors | same module |
| Writer NO-ACTION rules (DCL-NO-ACTION-STATUS-SEMANTICS-001) | ADVISORY-latest and no-prior-verdict fixtures assert `BridgeTransitionError` | same module |
| Placeholder gate + grandfathering (GOV-CROSS-CUTTING-...-001) | deny/new, allow/grandfathered, allow/fenced cases | same module |
| Code-quality gates | Both repo-native gates on every changed .py | `ruff check <changed>` AND `ruff format --check <changed>` |

**WI-5767 replay plan (required post-implementation evidence).** Reconstruct
the four historical pre-GO states as fixtures and run the checker against
each, demonstrating each NO-ACTION reason is caught pre-verdict; include the
four exit-5 outputs verbatim in the implementation report:

1. Replay of `-003`: v001-shaped cohort including the skill helper classified
   `configuration` under a PAUTH that does not allow that class - expect
   Gate A `pauth_mutation_class_not_allowed` naming the exact path.
2. Replay of `-007`: v005-shaped six-path cohort omitting the byte-identical
   `.codex` counterpart present on disk - expect Gate B
   `cross_harness_projection_missing` naming the Codex path.
3. Replay of `-011`: GO draft carrying Applicability Preflight but no Clause
   Applicability section - expect Gate C `verdict_sections_missing`.
4. Replay of `-013`: no acquirable claim context / packet prerequisites absent
   - expect Gate D mintability gap.

## Acceptance Criteria

- [ ] `scripts/pre_verdict_executability_check.py` exists with the exit-0/5
      contract and machine-readable gap list.
- [ ] GO-refusal wired into the verify helper; concrete
      `author_session_context_id` required on every emitted verdict body;
      `.codex`/`.cursor` projections regenerated (byte-identical / CRLF-preserved).
- [ ] Writer-side NO-ACTION validation live (ADVISORY-latest rejection +
      native prior-verdict check).
- [ ] Unfilled-placeholder gate live in the activated hook AND the template,
      grandfathered per the body-status-token convention.
- [ ] Docs updated: pre-GO executability step in both rule files +
      envelope-activity / bridge_kind documentation (with per-artifact
      approval packets).
- [ ] Test module green; WI-5767 four-gate replay evidence (four exit-5
      outputs) included in the implementation report.
- [ ] Both ruff gates pass on all changed Python files.
- [ ] Work-intent claim released; scratchpad drafts cleaned
      (Clean-Before-You-Leave).

## Risk and Rollback

- **False-block risk (checker too strict):** the checker gates only the
  verify helper's GO emission; NO-GO, ADVISORY, and finalization paths are
  untouched, and the logged owner-authorized bypass env exists for checker
  debugging. Rollback: revert the commit; the checker is additive and holds
  no state.
- **Writer NO-ACTION check vs. legacy repair flows:** the native check fires
  only on NEW writes of NO-ACTION files; historical files are append-only and
  never re-validated. The ADVISORY-latest rule matches the
  `ORDINARY_TRANSITIONS` code of record, so no lawful transition is blocked.
- **Placeholder gate false positives:** fenced-code stripping plus the narrow
  regex (angle-bracket fill-in form and PLACEHOLDER_X tokens only) plus
  on-disk grandfathering; the 222 historical files remain untouched.
- **Hook/template divergence:** pre-existing (disclosed); this change adds an
  identical block to both and cannot widen the divergence class.
- **Preflight subprocess cost in Gate C:** bounded, reviewer-invoked,
  pre-verdict only; no per-turn or hook-time execution (honors the
  cheap-gate lesson in bridge-essential.md).
- Rollback for all changes: single revert commit; no data migration, no
  MemBase mutation, no dispatcher/TAFE state involved.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5889; wi5767 thread chain (-003/-007/-011/-013 NO-ACTION evidence); friction investigation register 2026-08-06 (F-024, F-028, F-029, F-059, F-060); DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS",
  "canonical_authority": "DCL-NO-ACTION-STATUS-SEMANTICS-001; GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001; ORDINARY_TRANSITIONS code of record (scripts/bridge_lifecycle_resolver.py); GOV-ARTIFACT-APPROVAL-001 for the protected rule-file edits",
  "primary_route": "new deterministic checker scripts/pre_verdict_executability_check.py (exit 0/5) wired as a pre-GO refusal in the verdict helper; writer-side ADVISORY-latest NO-ACTION rejection; write-time placeholder gate (grandfathered); LO checklist doc updates",
  "before_behavior": "GO verdicts issue without checking the four post-GO gates; 45% of GO transitions draw Prime NO-ACTION; 148 GOs across 87 threads produced zero accepted implementations; wi5767 burned 16 versions/6 GOs/4 NO-ACTIONs; 238 placeholder occurrences across 222 bridge files",
  "after_behavior": "a GO that would fail implementation authorization cannot be issued (checker exit 5 -> NO-GO with the named gap); NO-ACTION on ADVISORY-latest rejected at write time; new NEW/REVISED files with unfilled placeholders rejected at write time; VERIFIED finalization mechanics unchanged",
  "self_descriptive_naming": "pre_verdict_executability_check.py names the check; no renames of existing surfaces",
  "obsolete_guidance_disposition": "LO checklist text in file-bridge-protocol.md and codex-review-gate.md gains the pre-GO step; no guidance removed; envelope-activity rules documented where they were previously code-only",
  "history_preservation": "append-only bridge protocol untouched; existing on-disk files grandfathered by the same convention as the status-token rule; no historical file re-validated",
  "baseline": {
    "go_to_no_action_share": "124 of 276 GO transitions (45%)",
    "wi5767_chain": "16 versions, 6 GO, 4 NO-ACTION, 0 implementations",
    "placeholder_occurrences": "238 across 222 bridge files (live 2026-08-06)",
    "no_action_misuse": "18 threads / 153 versions"
  },
  "expected_result": {
    "checker_contract": "exit 0 executable / exit 5 named gaps, fixtures replaying wi5767 -003/-007/-011/-013 each caught pre-GO",
    "writer_rejections": "NO-ACTION on ADVISORY-latest refused with DCL citation; placeholder NEW/REVISED refused with line evidence",
    "downstream": "GO-then-NO-ACTION loop rate falls; new threads cannot enter the wi5767 pattern"
  },
  "rollback": "single revert restores prior verdict-helper and writer behavior; checker is additive and reverts cleanly; grandfathering means no historical data migration",
  "hard_invariants": "review independence unchanged; VERIFIED commit-finalization gate unchanged; ADVISORY non-dispatchability unchanged; append-only chain discipline unchanged",
  "fail_closed_conditions": "checker unresolvable state (missing thread, unreadable proposal) exits 5 fail-closed; verdict helper refuses GO on checker failure rather than proceeding; writer rejections are hard errors",
  "essential_context_preservation": "every checker exit-5 emits the machine-readable gap list into the verdict-draft flow so the reviewer's NO-GO carries the exact remediation; nothing is silently dropped"
}
```

## Cross-Harness Disposition

Per-harness parity declaration (per `ADR-CROSS-HARNESS-PARITY-001` Q8 /
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`):

- **claude (B)**: canonical surfaces edited (`.claude/skills/gtkb-verify/helpers/write_verdict.py`,
  `.claude/hooks/bridge-compliance-gate.py` + its template source of record).
- **codex (A) / cursor (E)**: generated projections of write_verdict.py are regenerated from the
  canonical source (codex byte-identical; cursor CRLF-only divergence) — both included in
  target_paths and refreshed via the adapter pipeline, not hand-edited.
- **goose (G)**: projection carries ~2,833 lines of pre-existing drift; it is EXCLUDED from this
  thread and disclosed as a follow-on repair item (drift predates this proposal; silently
  reconciling it here would smuggle unreviewed changes). Goose sessions filing verdicts route
  through shared scripts unaffected by that drift for the checker path.
- **ollama (D) / openrouter (F) / antigravity (C) / alibaba (H)**: no harness-local copies of the
  touched surfaces; they consume scripts/gtkb_bridge_writer.py and the compliance gate uniformly.
- No typed waiver requested; parity is by canonical-source regeneration, with the goose drift
  exclusion explicitly disclosed rather than waived.

## Recommended Commit Type

feat

`feat:` is justified: net-new checker capability plus new enforcement
surfaces in helper, writer, and hook (not maintenance, not docs-only).

## Pre-Filing Preflight

Before filing, the filing session runs
`python scripts/bridge_applicability_preflight.py` and
`python scripts/adr_dcl_clause_preflight.py` against this exact candidate and
must observe `preflight_passed: true` / no blocking gaps; any failure aborts
filing. A work-intent claim on
`gtkb-w0-executable-go-pre-verdict-validation` must be acquired before
substantive drafting is published.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
