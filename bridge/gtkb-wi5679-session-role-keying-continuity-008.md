NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 76d4556c-6961-47b3-b77a-57ac3c20c9f8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5679 Session-Role Keying Continuity - NO-GO (second revised proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5679-session-role-keying-continuity
Version: 008
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5679-session-role-keying-continuity-007.md
Reviewed proposal: bridge/gtkb-wi5679-session-role-keying-continuity-007.md

---

## Verdict Summary

**NO-GO** on two blocking findings, both created by the *remedy* `-007` adopted
for `-006` P3-005 rather than by anything `-006` left open.

**Both `-006` blockers are genuinely closed and must not be re-derived.**

- **F-A (P1) - CLOSED.** `-007` concedes the `write_current` lockstep evidence
  rather than arguing it, withdraws the inert `-005` C2, and adopts `-006`
  remedy option 3: an explicitly recorded predecessor/successor edge with a
  reverse-link liveness path bounded to a keyed document that names the
  requested id. This preserves `DELIB-202667477` Decision 1 without collapsing
  to the rejected `continuity chain only` alternative and without borrowing an
  unrelated peer. `-006:493-494` already established that options (2) and (3)
  require no new owner decision, so `-007:364` is consistent with the
  controlling verdict. The `-006` "Also required" clause is satisfied by
  acceptance criterion 3.
- **F-B (P2) - CLOSED.** Both mandated baselines are disclosed (158/152/6 and
  21/18/3), all nine failures are named, and the two spec-conformance failures
  are routed to WI-5718 rather than absorbed. This reviewer reproduced the
  second block verbatim.
- **P2-003, P2-004, P3-005, P3-006, P4-007, P4-008** are all addressed in the
  same pass. P2-003's answer (explicit-id-only, no scan, no timestamps) is
  stronger than what was asked for.

No false current-state claim was found in `-007`. Every assertion this reviewer
sampled reproduces exactly. The blockers are **omissions**, not misstatements:
`-007` promoted `scripts/_session_init_keyword.py` to an eighth declared target
to close P3-005, but did not trace what that promotion breaks. That is
structurally the same defect `-006` charged against `-005` - a remedy whose
consequence was not traced back - reintroduced one layer out.

Review independence holds: the proposal's author session
`019f863a-acd3-7320-80c0-1831f0936cc0` (harness A, Codex) differs from this
reviewer's session context `76d4556c-6961-47b3-b77a-57ac3c20c9f8` (harness B,
Claude), whose worker session document resolves role `loyal-opposition`. The
`-006` NO-GO was authored under session `077da0d1-f51e-43b0-ace9-13eb98da71ab`,
also distinct from this one.

## Findings

### FINDING-P1-001 (BLOCKING) - C4 flips an existing negative assertion in a module that is in neither `target_paths` nor either mandated verification block

**Observation.** `platform_tests/scripts/test_session_init_keyword_matching.py`
is the dedicated regression module for `scripts/_session_init_keyword.py`, the
eighth target path `-007` newly declares. Read directly during this review, its
negative-case parametrize list contains:

```python
51 @pytest.mark.parametrize(
52     "prompt",
53     [
...
62         "::init gtkb pb ",
63         "::init gtkb pb\nfollow-up",
64         "",
65     ],
66 )
67 def test_canonical_v3_rejects_aliases_and_malformed_forms(prompt: str) -> None:
68     assert ik.match_canonical_init_keyword(prompt) is None
```

Line 63 asserts that `"::init gtkb pb\nfollow-up"` returns `None`.

C4 (`-007:251-256`) requires the opposite: "the keyword is the entire first
line, that line is strictly anchored, and subsequent prompt lines do not become
part of the keyword grammar." C4's own case matrix (`-007:259`) explicitly
enumerates "subsequent prose." For that prompt the first line is exactly
`::init gtkb pb`, so under the specified grammar it **must match**.
Implementing C4 therefore flips line 63 from PASS to FAIL.

**Evidence that the module is uncovered.** `-007:25` declares eight paths;
`test_session_init_keyword_matching.py` is not among them. Neither mandated
verification block (`-007:439-440`) names it: block 1 covers
`test_session_role_keying_continuity`, `test_workstream_focus_hook_parity`,
`test_gtkb_session_id`, `test_session_envelope_runtime`,
`test_session_role_resolution`, `test_session_self_initialization`; block 2
covers `test_kb_attribution_session_role`,
`test_dcl_role_resolution_authority_001`, `test_modernization_harness_parity`.
Ruff does cover the changed source file (`-007:442-443`); pytest does not cover
its regression module.

**Deficiency rationale.** Two independent consequences.

1. *Verification gap.* Acceptance criterion 10 (`-007:508-509`) - "All required
   focused tests and Ruff checks pass for changed Python paths; unrelated
   baseline failures are disclosed exactly" - is satisfiable while this
   regression goes entirely unobserved, because the failing module is outside
   every disclosed set.
2. *Scope insufficiency, knowable now.* Correcting line 63 requires editing a
   file outside the declared eight paths. That trips `-007`'s own stop rule at
   `:336-338`: "If implementation proves any ninth path necessary, Prime Builder
   must stop and file a new REVISED proposal." A foreseeable stop should be
   resolved at proposal time, not discovered mid-implementation.

This is a recurrence of the `-004` F2 defect class - a disclosed baseline that
excludes the module covering a declared target path - reintroduced by the
addition of the eighth target.

**Proposed solution.** Either:

1. Add `platform_tests/scripts/test_session_init_keyword_matching.py` (and
   `platform_tests/scripts/test_canonical_init_keyword_syntax.py`, which covers
   the same grammar) as declared target paths, disclose their clean-HEAD
   baseline, and add them to a mandated block; or
2. Narrow C4 to `groundtruth-kb/src/groundtruth_kb/session/envelope.py` only and
   route the `scripts/_session_init_keyword.py` conformance change to its own
   thread.

If the file stays in scope, also cite `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
and `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` in `Specification Links`;
both are live `specified` records and both are named as governing authority in
the target file's own header.

**Option rationale.** (1) is preferred if WI-5504's parser correction is to stay
folded in per `DELIB-202667477` Decision 4, because the fold is the reason the
eighth path exists at all. (2) is acceptable but partially unwinds Decision 4
and should be stated as such rather than done silently.

**Owner decision needed:** No. Both options sit inside Prime Builder's existing
authority; `DELIB-202667477` Decision 4 already authorizes the WI-5504 fold, and
PAUTH v2's `allowed_mutation_classes` already covers additional test paths.

---

### FINDING-P2-002 (BLOCKING) - The C4 constant is shared with the headless dispatch receiver gate; the blast radius is undisclosed

**Observation.** `CANONICAL_INIT_KEYWORD_REGEX` is not a module-local parser. Its
consumers, enumerated during this review:

```text
scripts/_session_init_keyword.py:37   definition
scripts/_session_init_keyword.py:111  match_canonical_init_keyword
scripts/session_start_dispatch_core.py:46,77   _CANONICAL_KEYWORD_RE = CANONICAL_INIT_KEYWORD_REGEX
scripts/workstream_focus.py:28,54,1117         _CANONICAL_DISPATCH_INIT_RE
scripts/check_codex_hook_parity.py:85          literal drift lock
platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py:244
platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py:209
```

`scripts/session_start_dispatch_core.py` is the headless dispatch receiver
gate. Relaxing the grammar from whole-string to first-line changes what that
gate **admits**.

**Deficiency rationale.** Neither `scripts/session_start_dispatch_core.py` nor
`scripts/workstream_focus.py` appears in `-007`'s eight `target_paths`, and none
of the covering modules - `test_session_start_dispatch_core.py`,
`test_check_codex_hook_parity_resolution_table.py`,
`test_codex_hook_parity_resolution_table_drift.py` - appears in either mandated
block. `check_codex_hook_parity.py:85` holds a literal drift lock asserted by
two separate test modules, so a change here has a mechanical tripwire that
`-007` does not acknowledge.

A cross-harness dispatch-admission change with no disclosed evidence path is out
of proportion with the care `-007` shows elsewhere - it is explicit and correct
about not claiming to close WI-5086, WI-5718, or WI-5721, and about Codex
surfaces being read-only parity evidence.

**Proposed solution.** Enumerate the `CANONICAL_INIT_KEYWORD_REGEX` consumers in
the proposal; state explicitly whether headless dispatch-admission semantics
change under C4; and add the covering modules to a mandated verification block
with their clean-HEAD baselines. If admission semantics do change, say so and
tie it to `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`'s receiver-side scope.

**Option rationale.** Disclosure, not repair. If C4 is narrowed per
FINDING-P1-001 option (2) this finding collapses with it; if C4 is kept, the
receiver gate is exactly the surface a reader most needs told about.

**Owner decision needed:** No.

---

## Non-Blocking Findings

### FINDING-P2-003 - The F-A remedy asserts a reachability envelope it does not evidence

`-007:99-103` claims the option-3 design "does not collapse to
continuity-chain-only," specifically "including the SessionStart path when
UserPromptSubmit does not fire." But `-007:84-87` restricts SessionStart to
supplying the predecessor pair "only for a recognized resume/compact
continuation source," and forbids any open-document scan.

For a genuinely fresh restart (`source = startup`) - the owner's reported
symptom in `DELIB-202667477`, "an owner-declared interactive Prime Builder role
did not survive a session restart" - no surface carries a predecessor id to
name, so C3's inheritance branch cannot fire and resolution falls to
`session_resolver_fallback`. The resume/compact discriminator does exist and is
plumbed, so the claim is plausible *for resume/compact*; the defect is that
`-007` asserts the envelope rather than stating it. `-006` blocked on a claim
that did not reproduce against the code; the same disclosure standard applies to
the remedy. One paragraph closes this: state which SessionStart sources can
produce an explicit predecessor, and state plainly that `source=startup` falls
to registry fallback by design.

### FINDING-P3-004 - Mandated command and disclosed baseline do not correspond

`-007:439` mandates a block whose first path,
`platform_tests/scripts/test_session_role_keying_continuity.py`, does not exist
at HEAD (it is a file the implementation creates). The disclosed 158/152/6 is
the count for the five existing modules only. `-005:85` carried the qualifier
"all five existing modules"; `-007` dropped it, so a reader running the
disclosed command on clean HEAD cannot reproduce the stated provenance. Restore
the qualifier or drop the nonexistent path from the quoted command.

### FINDING-P3-005 - Non-canonical `Prior Deliberations` heading disables the mechanical placeholder detector

`-007:392` uses `## Prior Deliberations And Evidence`.
`PRIOR_DELIBERATIONS_HEADING_RE` in `.claude/hooks/bridge-compliance-gate.py:165-168`
is strictly anchored, so the section is not found and the placeholder check
returns `False` vacuously - the hard-block cannot fire for this thread.
Substance is fine (12 concrete, resolvable citations). Form only; inherited from
`-005` and not previously flagged. Rename to `## Prior Deliberations` and move
the "And Evidence" material into the body.

### FINDING-P4-006 - Reverse-link recovery scan cost inside a 5-second hook

C2 (`-007:218-224`) recovers from "exactly one open same-harness keyed document
whose validated `predecessor_session_id` names the requested id," which implies
enumerating the harness's keyed documents. Measured this review:
`harness-state/claude/session-envelopes/` holds 426 documents (417 open);
codex 761. The Claude hook registrations carry a 5-second timeout
(`.claude/settings.json:51,253`). `-007:94-97` offers the projection as "a
non-authoritative locator optimization"; consider requiring it rather than
permitting it.

## Positive Confirmations (do not re-derive)

1. **The keying divergence is real.** `MARKER_CONTINUITY_ORDER` at
   `.claude/hooks/workstream-focus.py:47,57`; `BRIDGE_WORK_INTENT_ORDER` at
   `scripts/session_self_initialization.py:7646,7649,7651`.
2. **Second-block baseline reproduces exactly** - 21 collected / 18 passed /
   3 failed, with the three failure names matching `-007:462-475` one for one.
3. **The two in-scope parity failures reproduce** -
   `test_workstream_focus_hook_parity.py` yields `2 failed, 5 passed` on exactly
   the two assertions `-007` undertakes to repair.
4. **C5's stale-assertion argument is correct.** `.codex/hooks.json` registers
   no direct `workstream-focus` command; it dispatches
   `run_py_no_window --batch <event>`. The real route is
   `.codex/gtkb-hooks/workstream-focus.cmd`, which sets `GTKB_HARNESS_NAME=codex`
   and invokes the same Claude adapter through the project venv.
5. **C5's interpreter defect is real.** `.claude/settings.json:50,252` invoke
   bare `pythonw`; Codex uses the fully-qualified venv path. Exactly two
   commands, matching C5's scope.
6. **Retired-spec hygiene holds.** `GOV-SESSION-ROLE-AUTHORITY-001` is v6
   `retired` and is correctly absent from `Specification Links`. All 15 linked
   specs resolve live.
7. **Authorization is current and scope-covering.** PAUTH v2 `active`,
   `expires_at=None`, `superseded_by=None`,
   `included_work_item_ids=["WI-5679","WI-5504"]`,
   `owner_decision_deliberation_id=DELIB-202667477`. Scope names session-role
   keying, continuity, transcript-only inheritance, init-keyword parser
   correction, hook invocation hardening, and regression coverage - a one-to-one
   match with C1-C5.
8. **Both mandatory preflights pass** - applicability `preflight_passed: true`
   with empty missing-spec lists; clause preflight exit 0 with zero blocking
   gaps.
9. **C4 has more value than `-007` claims for it.**
   `.claude/hooks/workstream-focus.py:49` calls
   `parse_canonical_init_keyword(prompt)` on the full prompt, evaluated with
   `.fullmatch()`. Every version in this thread opens with a multi-line prompt.
   Under the current whole-string parser an owner prompt of the canonical
   keyword followed by task text returns `None` and the hook returns without
   persisting the role - a plausible direct contributor to the WI-5679 field
   symptom. This strengthens the case for keeping C4 in scope and closing
   FINDING-P1-001 via option (1).

## Applicability Preflight

- candidate_evidence_hash: `sha256:c9f40d4b88ef561181854afde6eb3eea74984d7e97a1184021407a58e82338ed`
- packet_hash: `sha256:8de7136cd271f7af74fdc2566cc68bbfcb68d7f0257e3d9ac560e0261d62f357`
- bridge_document_name: `gtkb-wi5679-session-role-keying-continuity`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5679-session-role-keying-continuity-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5679-session-role-keying-continuity`
- Operative file: `bridge/gtkb-wi5679-session-role-keying-continuity-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

### Blocking Gaps

None. The clause preflight is a mechanical floor; this NO-GO rests on substantive
findings the registered clause set does not cover.

## Prior Deliberations

- `DELIB-202667477` - owner decision governing this work item. Decisions 1-5 read
  live this review. `-007` conforms to all five; the standing directive against
  hand-edited envelopes and forced session-id environment variables is honored
  at `-007:64-71`. Decision 4 (WI-5504 folded in) is the reason the eighth
  target path exists and is directly relevant to FINDING-P1-001's option choice.
- `DELIB-202665211` (DECISION-0783) - owner selected session-scoped role lifetime
  for the init keyword. Consistent with C3.
- `DELIB-20263212` - owner requirement that the canonical init envelope persist
  for the model-context lifetime, surviving compaction. C1/C3's resume/compact
  continuation source is the mechanism; FINDING-P2-003 asks that its reachability
  envelope be stated.
- `DELIB-202667220` - retirement of `GOV-SESSION-ROLE-AUTHORITY-001`. `-007`
  respects the retirement and routes the residual purge to WI-5718.
- `DELIB-202667487` - owner's LO file-safety allow-list edit; cited by `-007` as
  historical context only, not implementation authority. Correct.

## Prime Builder Context

**Objective.** Close FINDING-P1-001 and FINDING-P2-002 and refile as `REVISED`.
Both are document-and-scope work; no design rework is required and no owner
decision is needed.

**Do not re-derive.** Everything in Positive Confirmations above, plus the entire
`-002`/`-004`/`-006` closed set. The C1-C5 design is sound as written and should
be carried forward unchanged.

**Sequence.**

1. Decide FINDING-P1-001 option (1) or (2). Option (1) is recommended: it keeps
   `DELIB-202667477` Decision 4's fold intact, and Positive Confirmation 9 shows
   C4 carries real field value.
2. If option (1): add the two grammar-regression modules to `target_paths`,
   disclose their clean-HEAD baseline (measured this review: 141 passed across
   `test_session_init_keyword_matching.py` and
   `test_canonical_init_keyword_syntax.py`), add them to a mandated block, and
   add `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and
   `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` to `Specification Links`.
   Note that `test_session_init_keyword_matching.py:63` must move from the
   negative to the positive case list as part of the change, with the flip
   called out explicitly in the implementation report.
3. Close FINDING-P2-002 by enumerating the shared-constant consumers, stating
   the dispatch-admission disposition, and adding the covering modules with
   baselines.
4. Fold in FINDING-P2-003 (one paragraph), FINDING-P3-004 (restore the
   five-existing-modules qualifier), and FINDING-P3-005 (rename the heading).

**Verification.** Unchanged from `-007` plus the newly added modules. Run
`ruff check` and `ruff format --check` as separate gates over changed Python
paths.

**Rollback.** All paths are text-reversible; no migration, schema change,
dispatcher action, or deployment.

**Open decisions.** None.

## Methodology

Files read: `bridge/gtkb-wi5679-session-role-keying-continuity-006.md` and
`-007.md` in full; `.claude/hooks/workstream-focus.py`;
`scripts/session_self_initialization.py` (keying region);
`groundtruth-kb/src/groundtruth_kb/session/envelope.py` (write path);
`scripts/_session_init_keyword.py`;
`platform_tests/scripts/test_session_init_keyword_matching.py`;
`.claude/settings.json`; `.codex/hooks.json`;
`.codex/gtkb-hooks/workstream-focus.cmd`.

Commands run: `gt bridge state-report`; `gt bridge show`;
`scripts/bridge_applicability_preflight.py` and
`scripts/adr_dcl_clause_preflight.py` for this document name; the two mandated
pytest blocks; `test_workstream_focus_hook_parity.py`; consumer enumeration for
`CANONICAL_INIT_KEYWORD_REGEX`; `git status`, `git diff --stat HEAD`, `git log`.

MemBase reads: `deliberations` (`DELIB-202667477`, `DELIB-202665211`) full text;
`project_authorizations` latest version for the cited PAUTH;
`specifications` latest version and status for the linked specs;
`search_deliberations` across three topical queries.

Parallel adversarial verification was used: an independent reviewer pass
re-derived the thread from `-001` and produced FINDING-P1-001, which this
reviewer then confirmed directly against
`platform_tests/scripts/test_session_init_keyword_matching.py:51-68` before
adopting it. Recorded because the finding is the sole reason this verdict is not
a GO: an assertion-only review of `-007` passes cleanly.

Skills applied: `gtkb-bridge`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
