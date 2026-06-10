REVISED

# Implementation Proposal - implementation_authorization.py Gate False-Positive Cluster (WI-3333)

bridge_kind: prime_proposal
Document: gtkb-impl-auth-parser-false-positive-fix
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S356

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3333

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

## Revision Note (-003 vs -001)

-003 responds to the `-002` NO-GO and expands scope per a 2026-05-16 owner decision.

- NO-GO `-002` F1 (P2): the operative `-001` proposal omitted two triggered
  advisory specifications and had no `## Pre-Filing Preflight` evidence
  section. -003 adds `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to `## Specification Links` and adds a
  `## Pre-Filing Preflight` section with the filing-time preflight results.
- Scope expansion (owner decision, 2026-05-16): a third defect in the same
  gate file - the post-GO authorization-resume asymmetry between
  `approved_files_for_go()` and `_validate_packet()` - is added as Bug 3 / IP-3.
  The owner selected "Fix auth-gate keystone" via AskUserQuestion when this
  defect was surfaced as the blocker preventing revision of the
  `gtkb-startup-relay-truncation-fix-refile` post-implementation `NO-GO`.
- Bugs 1 and 2 are unchanged from `-001`; the `-002` review confirmed both
  technical descriptions against current code ("Current code confirms the two
  proposed defect mechanisms").

## Summary

The implementation-start authorization gate `scripts/implementation_authorization.py`
has three false-positive / asymmetry defects that reject legitimate,
correctly-formed bridge work at `begin`. This proposal corrects all three. The
gate stays equally strict against genuine defects; it stops false-rejecting
legitimate authorization requests.

Bug 1 - `extract_target_paths()`: the function recognizes an inline
`target_paths` JSON metadata line and a `## Files Expected To Change`
section, but NOT the `## target_paths` heading-plus-backtick-bullet section
that roughly 17 proposal files actually use. Those proposals fail `begin`
with "Approved proposal is missing concrete target_paths or Files Expected
To Change".

Bug 2 - `extract_spec_links()` / `PLACEHOLDER_RE`: the placeholder check
runs `PLACEHOLDER_RE.search()` over the entire `## Specification Links`
body, so a bullet that cites a real specification but uses an ordinary
English word such as "pending" in its prose description false-fails with
"Approved proposal has placeholder text in Specification Links".

Bug 3 - `approved_files_for_go()` / `_validate_packet()` post-GO asymmetry:
`approved_files_for_go()` (the `begin`-path function) hard-requires the bridge
thread's latest INDEX status to be exactly `GO`. Once a thread files a
post-implementation report, its latest status becomes `NEW`, then `NO-GO` or
`VERIFIED` - so `begin` can never mint a fresh authorization packet to revise
an implementation in response to a post-implementation-report `NO-GO`.
Meanwhile `_validate_packet()` (the gate-check-path function) already walks the
version chain and treats a post-GO `NO-GO` as a valid resume state. The two
functions disagree about whether post-GO-NO-GO is authorizable. The
consequence: an authorization packet that is still alive survives a
post-impl-report `NO-GO` (Prime can keep revising), but once that packet
expires no replacement can be minted - every post-implementation-report
revision cycle is then blocked. This was hit directly this session: revising
`gtkb-startup-relay-truncation-fix-refile` (GO at `-004`, post-impl report
`-005`, `NO-GO` at `-006`) is impossible because `begin` returns
`{"authorized": false, "error": "Implementation authorization requires latest GO; found NO-GO"}`.

None of the three bugs is exercised by the applicability or clause preflights,
so all three escaped Codex GO-time review on every affected thread.

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`:
`scripts/implementation_authorization.py` and
`platform_tests/scripts/test_implementation_authorization.py`. No
`applications/` paths; no paths outside `E:\GT-KB`.
`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the file-bridge authority; the implementation-start authorization gate is bridge-protocol infrastructure and this fix keeps its scoping contract intact.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the constraint the gate mechanizes for the target_paths metadata and the Specification Links section; the fix aligns the mechanization with the rule's intent.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below; each behavior maps to a named test.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - both target paths are in-root.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the authorization gate is a governed tooling artifact; this corrects its behavior.
- GOV-STANDING-BACKLOG-001 - WI-3333 is tracked in the standing backlog under PROJECT-GTKB-RELIABILITY-FIXES.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the authorization packet, the bridge thread, and the linked specs form the artifact graph for this work; the gate is a durable governed artifact.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the lifecycle-trigger discipline; a post-implementation-report NO-GO triggers a revision, which is the lifecycle transition Bug 3 currently blocks.
- `.claude/rules/file-bridge-protocol.md` section "Mandatory Implementation-Start Authorization Metadata" - the rule defining the target_paths metadata requirement the gate parses.
- `.claude/rules/codex-review-gate.md` section "Mechanical Implementation-Start Gate" - the rule describing the authorization packet the gate produces and the post-GO revision cycle Bug 3 blocks.

## Prior Deliberations

- DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT - the direct precedent: the same gate, the same defect class (a mechanization narrower than the rule's intent). The verified thread `gtkb-impl-auth-verification-heading-gate-alignment` corrected the verification-plan heading whitelist and refactored `section_body()` to delegate to a `_iter_sections()` helper. This proposal reuses that `_iter_sections()`-backed `section_body()` helper for the new `## target_paths` heading recognition rather than adding a parallel parser. No overlap: that thread did not touch `extract_target_paths`, `extract_spec_links`, `TARGET_PATHS_RE`, `PLACEHOLDER_RE`, `approved_files_for_go`, or `_validate_packet`.
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION - reinforces DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 as the governing enforcement specs.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - frames recurring authorization-gate friction as a defect worth a deterministic service-side fix. Bug 3 is exactly such recurring friction: every post-implementation-report revision cycle hits it once the original packet expires.
- Sibling impl-gate threads `gtkb-impl-gate-friction-hygiene` (latest NO-GO) and `gtkb-implementation-gate-friction-hygiene` (latest NO-GO) are acknowledged for non-duplication: both target `scripts/implementation_start_gate.py` (the downstream Write-time gate), not `scripts/implementation_authorization.py`, and neither proposes changes to `extract_target_paths`, `PLACEHOLDER_RE`, `approved_files_for_go`, or `_validate_packet`. This proposal does not duplicate or supersede them.
- A `search_deliberations` scan found no prior deliberation addressing the `## target_paths` heading recognition gap, the whole-body placeholder scan, or the post-GO begin/validate authorization asymmetry.

## Owner Decisions / Input

- 2026-05-15 UTC, S354: owner answered an AskUserQuestion choosing "Fix the authorization gate" when presented the systemic gate-blocker (the two parser false-positives blocking the GO bridge backlog). That AskUserQuestion answer authorizes Bugs 1 and 2.
- 2026-05-16 UTC, S356: owner answered an AskUserQuestion choosing "Fix auth-gate keystone" when the post-GO authorization-resume asymmetry (Bug 3) was surfaced as the blocker preventing revision of the `gtkb-startup-relay-truncation-fix-refile` post-implementation `NO-GO`. That answer authorizes adding Bug 3 / IP-3 to this thread.
- This work is filed through the reliability fast-lane: WI-3333 is a member of PROJECT-GTKB-RELIABILITY-FIXES, covered by the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (active, no expiry; allowed mutation classes include `source` and `test_addition`). No per-fix deliberation or new project authorization is created.

## Requirement Sufficiency

Existing requirements sufficient. The target_paths metadata requirement
(`.claude/rules/file-bridge-protocol.md`), the Specification Links requirement
(DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001), and the
implementation-start authorization contract (`.claude/rules/codex-review-gate.md`)
are unchanged. This proposal corrects the gate's mechanization to match those
existing requirements; it does not create or revise a requirement. Bug 3 in
particular makes the `begin` path consistent with the post-GO revision cycle
the file-bridge protocol already prescribes.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. This proposal covers one work item (WI-3333), a member
of PROJECT-GTKB-RELIABILITY-FIXES per the standing authorization. The change
is a three-defect source correction in one file plus its regression tests; it
performs no inventory sweep, no batch promotion, and no multi-item
standing-backlog mutation. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`
is not triggered: no formal-artifact-approval packet for a bulk action is
required, and no review-packet inventory artifact is produced.

## Pre-Filing Preflight

Both mandatory pre-filing preflights are run against the indexed operative
`-003` file after the `bridge/INDEX.md` entry is filed (the applicability
preflight resolves the operative file from the index). Commands:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-auth-parser-false-positive-fix
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-auth-parser-false-positive-fix
```

Observed results (run 2026-05-16 against the indexed operative `-003`):

Applicability preflight - PASS:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `content_file: bridge/gtkb-impl-auth-parser-false-positive-fix-003.md`
- `packet_hash: sha256:ae22c4012a1c609853b91f9a22fa654efe765442d7c658521615a5b6c4372949`
- All 7 triggered specs are cited in `## Specification Links`:
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`.

Clause preflight (mandatory gate) - PASS:

- Clauses evaluated: 5; `must_apply`: 5; evidence gaps in `must_apply` clauses: 0;
  blocking gaps (gate-failing): 0.
- Exit code `0` (pass).

Both mandatory pre-filing preflights pass on the operative `-003` file; the
`-002` F1 advisory-spec gap is closed.

## Proposed Scope

### IP-1: Recognize the `## target_paths` heading form in `extract_target_paths`

In `scripts/implementation_authorization.py`, `extract_target_paths()` keeps
its current precedence: the inline `target_paths` JSON metadata line is tried
first, then a section fallback. The section fallback is extended:

- `## Files Expected To Change` keeps its established extraction unchanged
  (every backtick span on each bullet line). No regression to that format.
- When `## Files Expected To Change` is absent, the function also reads a
  `## target_paths` heading section via the existing `section_body()` helper
  (the `_iter_sections()`-backed helper from DELIB-S352). Proposals using the
  `## target_paths` heading place the path first in backticks and may add
  parenthetical annotations in additional backtick spans, so this branch
  takes only the FIRST backtick span per bullet line as the path. The
  asymmetry is deliberate and documented in-code: each section name keeps the
  extraction matched to its observed real-world convention.

No change to `TARGET_PATHS_RE` or the inline-JSON branch. The
"missing concrete target_paths" error is still raised when none of the three
forms is present.

### IP-2: Make the Specification Links placeholder check per-bullet

In `extract_spec_links()`, replace the whole-body `PLACEHOLDER_RE.search(body)`
with a per-bullet scan. A new helper `_bullet_has_citation(text)` returns True
when a bullet carries a concrete citation: a backtick-quoted token, or an
uppercase identifier token (matching a `GOV-`/`SPEC-`/`ADR-`/`DCL-`/`DELIB-`
style ID via a regex such as `\b[A-Z][A-Z0-9]*-[A-Z0-9][A-Z0-9-]*\b`). A
bullet with a concrete citation is a real specification link; ordinary words
in its prose description are not flagged. A bullet with NO concrete citation
that matches `PLACEHOLDER_RE` is a genuine placeholder bullet and still raises
"Approved proposal has placeholder text in Specification Links".

`PLACEHOLDER_RE` itself is unchanged - a bullet that is only a placeholder
token (for example a lone `- TBD` bullet) is still rejected. The fix narrows
WHERE the check applies (placeholder-only bullets), not WHAT it rejects.

### IP-3: Symmetric post-GO authorization-resume in `approved_files_for_go()` and `_validate_packet()`

Both gate functions are aligned on a single lifecycle rule: a revised
*proposal* always precedes its GO in the bridge lifecycle (proposals are
revised, then GO'd), so any `NEW` or `REVISED` version *after* the latest GO
is a post-implementation report, never a superseding proposal. The latest
overall status therefore determines whether implementation may resume.

A new shared helper - `_post_go_chain_state(entry)` - locates the newest `GO`
in `entry.versions` (newest-first) and classifies the chain as exactly one of:

- `latest_is_go` - the GO is the latest version (today's happy path);
- `resumable` - the latest version is a post-GO `NO-GO` (a post-implementation
  report was NO-GO'd; the GO still authorizes the revision);
- `awaiting_review` - the latest version is a post-GO `NEW` or `REVISED` (a
  post-implementation report is awaiting Loyal Opposition review; authorizing
  mutations now would invalidate the report snapshot under review);
- `terminal` - the latest version is a post-GO `VERIFIED` (the implementation
  phase for this proposal is closed);
- `no_go_in_chain` - no `GO` exists anywhere in the chain.

`approved_files_for_go()` is rewritten to use this classification: it raises
for `no_go_in_chain`, `awaiting_review`, and `terminal`; it returns
`(proposal_file, go_file)` for `latest_is_go` and `resumable`. The proposal
file remains the first `NEW`/`REVISED` version immediately below the GO. The
previous `entry.latest_status != "GO"` hard gate is removed.

`_validate_packet()`'s post-GO block is aligned to the same rule. Its current
`if any(status == "REVISED" for status in statuses_after_go)` rejection
("...superseded by REVISED proposal...") is incorrect - it treats a post-GO
revised *report* as a superseding *proposal* - and is replaced by the
latest-status classification: a latest `NEW` or `REVISED` raises
`awaiting_review`; a latest `VERIFIED` raises `terminal`; a latest `NO-GO`
(with or without an intervening NO-GO'd `REVISED` report below it in the
chain) is `resumable` and does not raise. The existing "newer GO exists after
the pinned go_file" rejection in `_validate_packet()` is preserved unchanged -
a packet pins one `go_file`, and a genuinely newer GO means the packet must be
re-issued from the new GO.

This removes the begin/validate asymmetry permanently: both functions consult
one helper, so they cannot drift apart again.

### IP-4: Regression tests

Add 21 tests to `platform_tests/scripts/test_implementation_authorization.py`
(the single canonical test file; it uses an importlib-loaded `auth_module`
fixture and synthetic-artifact helpers under `tmp_path`). New target_paths
tests construct the `## target_paths` heading form explicitly; new Bug-3 tests
construct synthetic bridge chains with explicit version sequences.

| ID | Test name | Behavior |
|----|-----------|----------|
| T1 | test_extract_target_paths_accepts_target_paths_heading | `## target_paths` heading, one backtick path per bullet -> paths extracted |
| T2 | test_extract_target_paths_target_paths_heading_first_span_only | `## target_paths` bullets with path + parenthetical backtick annotation -> only the path (first span) extracted |
| T3 | test_extract_target_paths_inline_json_unchanged | inline JSON metadata line -> unchanged behavior (regression) |
| T4 | test_extract_target_paths_files_expected_to_change_unchanged | `## Files Expected To Change`, multi-span bullet -> all spans (regression) |
| T5 | test_extract_target_paths_raises_when_all_forms_absent | none of the three forms -> AuthorizationError still raised |
| T6 | test_extract_target_paths_inline_json_precedence | proposal has both inline JSON and `## target_paths` heading -> inline JSON wins |
| T7 | test_extract_spec_links_substantive_word_in_cited_bullet_not_flagged | bullet citing a backticked spec whose prose contains a placeholder-shaped word -> no raise |
| T8 | test_extract_spec_links_placeholder_only_bullet_still_flagged | lone placeholder-token bullet (no citation) -> raises |
| T9 | test_extract_spec_links_bare_placeholder_word_bullet_still_flagged | bullet that is a bare placeholder word -> raises |
| T10 | test_extract_spec_links_id_token_bullet_with_placeholder_word_not_flagged | bullet citing a bare uppercase ID token (no backticks) + placeholder-shaped word in prose -> no raise |
| T11 | test_extract_spec_links_normal_section_returns_links | normal section, all real citations -> links returned (regression) |
| T12 | test_create_authorization_packet_accepts_target_paths_heading_proposal | end-to-end: a synthetic GO'd proposal using the `## target_paths` heading -> packet created, target_path_globs correct |
| T13 | test_approved_files_for_go_authorizes_post_go_no_go | chain NEW/NO-GO/REVISED/GO/NEW/NO-GO, latest NO-GO -> returns (proposal_file, go_file) |
| T14 | test_approved_files_for_go_raises_on_post_go_new_awaiting_review | latest is a post-GO `NEW` report -> raises (awaiting review) |
| T15 | test_approved_files_for_go_raises_on_post_go_revised_awaiting_review | latest is a post-GO `REVISED` report -> raises (awaiting review) |
| T16 | test_approved_files_for_go_raises_on_post_go_verified | latest is post-GO `VERIFIED` -> raises (terminal) |
| T17 | test_approved_files_for_go_raises_when_no_go_in_chain | chain has no `GO` -> raises (no GO in chain) |
| T18 | test_approved_files_for_go_latest_is_go_unchanged | latest IS `GO` -> returns (proposal_file, go_file) (regression) |
| T19 | test_validate_packet_accepts_post_go_no_go_after_revised_report | chain GO/NEW/NO-GO/REVISED/NO-GO -> `_validate_packet` does not raise (recursion case) |
| T20 | test_validate_packet_raises_on_post_go_revised_report_awaiting_review | latest is a post-GO `REVISED` report -> `_validate_packet` raises (awaiting review) |
| T21 | test_begin_creates_packet_for_post_go_no_go_thread | end-to-end `begin` against a synthetic thread whose latest is a post-GO `NO-GO` -> packet created |

## Specification-Derived Verification Plan

| Linked spec / clause | Verification step | Expected result |
|---|---|---|
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | T1-T6 (target_paths recognition), T7-T11 (spec-links placeholder precision) | 11 PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | T12 end-to-end packet creation; T13-T21 post-GO authorization-resume consistency | 10 PASS |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | T13/T19/T21 confirm a post-implementation-report NO-GO triggers an authorizable revision cycle | 3 PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this table is the spec-to-test mapping; each behavior maps to a named test | 21 tests cover 21 distinct behaviors |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | both target paths in-root | confirmed in In-Root Placement Evidence |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | `bridge/INDEX.md` updated to insert this `REVISED` entry at the top of the thread version list; no deletion or rewrite | confirmed at filing time |

Commands at implementation time (executed after Codex GO):

1. `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short` - all 21 new tests PASS and the existing suite continues to PASS.
2. `python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` - zero new errors.
3. `python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` - clean for the added code.
4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-auth-parser-false-positive-fix` - `preflight_passed: true`.
5. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-auth-parser-false-positive-fix` - exit 0; no blocking gaps.
6. Live evidence: after the fix, `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-relay-truncation-fix-refile` (a post-GO-NO-GO thread) authorizes successfully where it previously failed.

## Risks and Rollback

- Risk: the `## target_paths` first-span-per-bullet rule mis-extracts if a future proposal places a non-path token first in backticks. Mitigation: the inline JSON form remains the recommended primary metadata form and is tried first; the heading form is a compatibility path for the existing corpus.
- Risk: `_bullet_has_citation` exempts a bullet that has a backtick span but no genuine spec. Mitigation: a bullet with a backtick span is, by the Specification Links convention, citing an artifact; a genuinely empty placeholder bullet has no backtick span and no ID token, so it is still flagged. T8/T9 pin this.
- Risk (Bug 3): the lifecycle rule assumes a revised proposal always precedes its GO. If a thread re-files a revised *proposal* after a GO (a protocol-unusual re-scoping), the post-GO `REVISED` is classified `awaiting_review` and `approved_files_for_go()` raises - a conservative refusal, never a wrong authorization. If that revised proposal then receives a new GO, the newest-GO selection in `_post_go_chain_state` authorizes from the new GO. T15/T20 pin the conservative refusal.
- Risk (Bug 3): aligning `_validate_packet()` could weaken a real protection. Mitigation: the "newer GO after the pinned go_file" rejection and the GO-file-status-changed rejection are preserved unchanged; only the incorrect post-GO-`REVISED`-report rejection is replaced. T19/T20 pin both the accept and the raise.
- Rollback: revert the `extract_target_paths` section-fallback extension, restore the whole-body `PLACEHOLDER_RE.search`, remove `_bullet_has_citation`, restore the `entry.latest_status != "GO"` gate and the `any(REVISED)` rejection, remove `_post_go_chain_state`, and remove the 21 tests.

## Recommended Commit Type

`fix` - corrects three false-positive / asymmetry defects in an existing gate.
A bounded source change in one file plus 21 regression tests; no new
capability surface, no spec promotion, no behavior change for genuine defects.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
