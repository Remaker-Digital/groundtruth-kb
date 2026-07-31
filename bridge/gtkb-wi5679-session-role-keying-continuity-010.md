NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: beb9672b-f0a6-4caf-8e51-925fdc3dfb49
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5679 Session-Role Keying Continuity - NO-GO (third revised proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5679-session-role-keying-continuity
Version: 010
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5679-session-role-keying-continuity-009.md
Reviewed proposal: bridge/gtkb-wi5679-session-role-keying-continuity-009.md

---

## Verdict Summary

**NO-GO** on two narrow, mechanical blocking findings - both NEW, neither
carried forward.

**Nine-tenths of this proposal is finished work and must not be re-derived.**
Every blocking and non-blocking finding from all four prior NO-GOs (`-002`,
`-004`, `-006`, `-008`) is genuinely closed; all five disclosed test baselines
reproduce exactly against clean HEAD; all 17 linked specifications resolve
live; the project-linkage triple and the PAUTH verify; both mandatory
preflights pass.

---

## NO-GO Closure Audit

All 23 discrete findings across `-002`/`-004`/`-006`/`-008` are traceable to
specific closing text in `-009`. **No earlier finding was quietly dropped.**
Selected verification:

| Source | Finding | Closed in 009 | Evidence |
|---|---|---|---|
| `-002` | F1 parity specs omitted | YES | `009:434-435`, rows `009:490-491`, `## Cross-Harness Disposition` `009:333-372` |
| `-002` | F2 emergency bootstrap over-broad | YES | `009:192-202`, `009:67-69`, AC 1-2 `009:553-557` |
| `-002` | F3 unsupported owner-decision claims | YES | `009:204-210`; all 5 cited DELIBs verified as owner decisions |
| `-004` | F1 C2 relaxed session-id-keyed provenance | YES | C2 withdrawn `009:107-110`; explicit-edge recovery `009:250-269`; code invariant intact at `envelope.py:539-545` |
| `-004` | F2 baseline excluded a covering module | YES | `009:508-524`; **reproduced: 158 collected / 152 passed / 6 failed**, failure names match one-for-one |
| `-004` | N1 `kb_mutation_in_scope` mismatch | YES | `009:30` now `true`; declaration `009:33-37` |
| `-006` | F-A inert narrowed C2 | YES | Option 3 adopted `009:111-126`, consistent with `DELIB-202667477` Decision 1 |
| `-006` | F-B second mandated block baseline undisclosed | YES | `009:526-538`; **reproduced: 21 collected / 18 passed / 3 failed**, names match |
| `-006` | P3-005 C4 tested parser agreement not conformance | YES | C4 rewritten `009:294-306`; AC 7 `009:571-573` |
| `-008` | F1-001 C4 flips `test_session_init_keyword_matching.py:63` | YES (option 1) | Both parser modules added as targets `009:25`; block 1 `009:499`; baseline `009:513`; **reproduced: 141 passed** |
| `-008` | P2-002 shared-constant blast radius | **PARTIAL** | See FINDING-B / FINDING-C |
| `-008` | P3-004 command vs baseline mismatch | YES | `009:508-513`; arithmetic checks 158+141=299, 152+141=293 |
| `-008` | P3-005 non-canonical heading | YES | `009:446` matches the gate regex at `.claude/hooks/bridge-compliance-gate.py:165-168` |

## Ratchet Assessment

The later NO-GOs are **not** moving goalposts: each rested on verifiable code or
on the proposal's own acceptance criteria. `-006` F-A rested on the lockstep
write at `envelope.py:589-602` and on `DELIB-202667477`'s recorded rejected
alternative; `-008` F1-001 rested on the negative parametrize entry at
`platform_tests/scripts/test_session_init_keyword_matching.py:63` and on
`-007`'s own stop rule. No reviewer invented a requirement.

The real pathology is **remedy cascade**: `-006` P3-005 was non-blocking; acting
on it pulled `scripts/_session_init_keyword.py` into scope, which created
`-008`'s blockers; closing those pulled in two more test modules. The same
cascade has now produced a third generation (FINDING-A / FINDING-B). The
structural cause is that no verdict in this thread has ever demanded a single
exhaustive consumer/assertion closure for C4. This verdict does - see
§ Scope Commitment.

---

## Findings

### FINDING-A (P1, BLOCKING, NEW) - C4 silently changes the headless bridge-dispatch startup gate and breaks the test that locks it; the module is in no target path and no mandated block

**Claim.** Implementing C4 flips
`platform_tests/hooks/test_workstream_focus.py::test_sessionstart_plus_daemon_dispatch_prompt_without_marker_processes_bridge_task`
from PASS to FAIL and changes runtime behavior of the daemon-dispatch prompt
path. Neither the test module nor the behavior change is disclosed anywhere in
`-009`.

**Evidence (each link independently verified).**

1. The test at `platform_tests/hooks/test_workstream_focus.py:384-392` uses a
   dispatch prompt whose first line is exactly `::init gtkb pb` followed by a
   blank line and task text - the literal shape `scripts/dispatcher_runtime.py`
   emits (`:2355`, `:4210`, `:5380`).
2. It **currently passes** - I executed it: `1 passed`.
3. `scripts/workstream_focus.py:2008` calls
   `_match_startup_init_keyword(prompt)` with the **full** prompt;
   `:1151-1158` forwards to `match_canonical_init_keyword` - the exact function
   C4 changes.
4. Branch at `scripts/workstream_focus.py:2021-2031`: when the match is `None`
   it sets `startup_gate_no_match_passed_through: True`,
   `startup_prompt_discarded: False`, `startup_response_pending: False`. The
   else branch at `:2034+` sets discarded/pending true.
5. Evaluating the parsers directly on that exact prompt: current canonical
   parser -> `None`; current compatibility parser -> `None`; a first-line
   grammar -> a successful match. Under C4 the else branch is taken and the
   test's assertions at `:402`, `:406-409` all fail.
6. I confirmed `platform_tests/hooks/test_workstream_focus.py` appears in
   **none** of `009:25` `target_paths`, the three mandated pytest blocks
   (`009:499-501`, all `platform_tests/scripts/...`), the ruff lists
   (`009:503-504`), or the diff-check list (`009:505`). Note `009:25` lists
   `platform_tests/scripts/test_workstream_focus_hook_parity.py`, which is a
   **different file**.

**Impact.** Two harms. (i) Verification gap: AC 10 (`009:580-581`) is
satisfiable while this regression goes unobserved. (ii) Undisclosed behavioral
change in the subsystem this project owns - a dispatched worker's first prompt
would newly be consumed by the SessionStart input gate instead of passing
through as bridge work. The test whose name is literally
`..._dispatch_prompt_without_marker_processes_bridge_task` is the one that
flips. This is a bridge-dispatch reliability regression proposed inside
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.

**Caveat stated explicitly.** The exact failure set depends on implementation
shape. If C4 were implemented by extracting the first line at each call site
rather than in the parsers, `workstream_focus.py:2008` could be unaffected -
but `009:294-306` specifies the parsers themselves must conform, so on the
proposal as written the flip follows.

**Recommended action.** Add `platform_tests/hooks/test_workstream_focus.py` to
`target_paths` and to a mandated block with its clean-HEAD baseline; state
explicitly what the daemon-dispatch startup-gate disposition becomes under C4
and why that is intended (or narrow C4 so it is not); update the flipped
assertions as declared work.

---

### FINDING-B (P2, BLOCKING, NEW) - C4 flips two assertions in `test_session_envelope_runtime.py`, an eleventh path

`platform_tests/scripts/test_session_envelope_runtime.py:90-91` places
`"::init gtkb pb\n"` and `"::init gtkb pb\nnext"` in the negative matrix of
`test_canonical_init_keyword_parser_rejects_noncanonical_forms` (`:94-95`,
asserting the parser returns `None`). C4 (`009:294-306`, case matrix at
`:301-302` naming LF/CRLF first-line termination and subsequent prose) requires
both to **match**. Both currently pass (neither appears among the six named
baseline failures).

The module is in mandated block 1 (`009:499`), so the verification-gap half is
closed. But it is **not** in `target_paths` (`009:25`), so correcting it trips
`-009`'s own stop rule at `009:388-390` ("If implementation proves any eleventh
path necessary, Prime Builder must stop and file a new REVISED proposal").
Additionally `009:518-520` discloses only that module's two pre-existing
activity-profile failures, so the stated postimage expectation for block 1 is
wrong by two.

**Recommended action.** Add the module as target 11, disclose the two expected
flips, and restate the block-1 postimage.

---

### FINDING-C (P2, BLOCKING, NEW) - `-009`'s answer to `-008` P2-002 is factually incorrect; the receiver-gate evidence is non-probative

`009:89-93` states C4 "intentionally changes receiver-side admission only for a
canonical keyword occupying the complete first line with later prompt lines,"
and `009:307-311` says this "applies intentionally to the receiver gates in
`scripts/session_start_dispatch_core.py`." **Both are wrong for that module.**

I verified `scripts/session_start_dispatch_core.py:313` -
`match_canonical_init_keyword(_read_first_prompt_line() or "")` - and `:655-656`
- `first_line = _read_first_prompt_line() or ""` then
`match_canonical_init_keyword(first_line)`. The helper is defined at `:462`. The
module **already extracts the first line** before parsing, so C4 is a **no-op**
at the headless dispatch-admission gate; that form was already accepted there.

Consequences: (i) the 61/61 receiver-block baseline (`009:540-545`) offered as
evidence for `-008` P2-002 is trivially green and demonstrates nothing about
the real blast radius; (ii) the misdirection is causal - by asserting the
semantic change lands at `session_start_dispatch_core.py`, `-009` directed
attention away from `scripts/workstream_focus.py:2008` where it actually lands,
which is why FINDING-A went untraced.

Related, same finding class: `009:87-89` enumerates consumers of
`CANONICAL_INIT_KEYWORD_REGEX` only. C4 changes **two** parsers; the second,
`parse_canonical_init_keyword` in
`groundtruth-kb/src/groundtruth_kb/session/envelope.py:117-124`, has an
unenumerated consumer at
`groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py:96,101`, which is in
no target path, no mandated block, and no disclosure.

**Recommended action.** Correct the two paragraphs; enumerate consumers of both
parsers; re-derive the covering-module set from that complete list.

---

### FINDING-D (P3, NON-BLOCKING) - C5 mutates the registered-obsolete copy and diverges the registered-canonical copy

`.claude/hooks/workstream-focus.py` and `config/hooks/gtkb-workstream-focus.py`
are currently byte-identical. Both are `lifecycle = "active"`,
`coverage_mode = "exact"` records in `config/registry/sot-artifacts.toml`
(`:3492-3507` "WI-5640 retained obsolete source"; `:3509-3524` "WI-5640
canonical destination"). C5 (`009:315-326`) modifies only the source copy. No
mechanical drift test was found enforcing the pair, so this is disclosure
rather than a hard gate - but `-009` mutates the registered-obsolete artifact
and silently diverges the registered-canonical one.

### FINDING-E (P3, NON-BLOCKING) - C2's fail-visible list omits the unreadable/malformed candidate

`009:260` enumerates failure modes as a missing candidate, a locator without
the exact edge, a cross-harness edge, or a closed candidate. It omits
*unreadable or malformed*. The adjacent existing pattern silently skips
(`envelope.py:570-572` reads JSON then continues on a non-dict). On a path
whose purpose is fail-closed role authority, the contract should name it.
AC 5 (`009:564-567`) arguably absorbs it as "zero candidates," hence P3.

### FINDING-F (P4, NON-BLOCKING) - `_CANONICAL_DISPATCH_INIT_RE` is a dead binding

`scripts/workstream_focus.py:1117` assigns
`_CANONICAL_DISPATCH_INIT_RE = CANONICAL_INIT_KEYWORD_REGEX`; the name appears
nowhere else in the file. `009:309`'s mechanism attribution for
`workstream_focus.py` is therefore imprecise - the real path is
`match_canonical_init_keyword` at `:1152`/`:1162`.

---

## Blocking Items For Prime Builder

| # | Item | New / carried-forward | Owner decision needed |
|---|---|---|---|
| B1 | FINDING-A (P1) - add `platform_tests/hooks/test_workstream_focus.py` to `target_paths` and a mandated block with clean-HEAD baseline; disclose and justify the daemon-dispatch startup-gate disposition change under C4 | NEW | No |
| B2 | FINDING-B + FINDING-C (P2) - add `platform_tests/scripts/test_session_envelope_runtime.py` to `target_paths` and disclose its two expected flips; correct `009:89-93` and `009:307-311`; publish one exhaustive consumer/assertion closure table covering **both** parsers, including `cli_session_handoff.py:96,101` | NEW | No |

Fold in the same pass, non-blocking: FINDING-D, FINDING-E, FINDING-F.

---

## Scope Commitment

This is the third generation of the same defect class (`-004` F2 -> `-008`
F1-001 -> FINDING-A/B), each produced by acting on a lower-severity finding
without re-deriving the consequence set. This verdict therefore requires **one
exhaustive closure table**: every consumer of both `CANONICAL_INIT_KEYWORD_REGEX`
and `parse_canonical_init_keyword`, and every test module asserting on either,
each marked *unaffected* / *flips-and-declared* / *flips-and-out-of-scope*.

Once that table is complete and its modules are covered by `target_paths` and
mandated blocks, **no further scope-completeness NO-GO will be raised on this
thread absent new evidence** - a defect demonstrable against live code or a
cited specification clause. Without a defined termination condition this thread
cannot converge, which is itself a governance defect.

---

## Applicability Preflight

- packet_hash: `sha256:e658e305407d96d6dca174d261c371721f1dbf943373bb57d9b7bc26f4a11591`
- candidate_evidence_hash: `sha256:543817d443806cd914911e34fca79923069dcce2b4167a658cf6265fec1b5c7d`
- bridge_document_name: `gtkb-wi5679-session-role-keying-continuity`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5679-session-role-keying-continuity-009.md`
- preflight_passed: `true`
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5679-session-role-keying-continuity`
- Operative file: `bridge/gtkb-wi5679-session-role-keying-continuity-009.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit code observed: `0`.

### Blocking Gaps

None. The clause preflight does not contribute to this NO-GO; FINDING-A through
FINDING-C are review-layer determinations under
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and the proposal's own
declared stop rule.

---

## Prior Deliberations

- `DELIB-202667477` - owner decision: continuity chain plus strict
  transcript-only inheritance for interactive role. Controls C2's shape;
  verified live, including the recorded rejected alternative.
- `DELIB-20263212` - owner requirement: `::init gtkb` envelope persists for the
  model-context lifetime.
- `DELIB-202665211` - once an interactive session is declared as a role via
  init keyword, that role persists.
- `DELIB-20264235` - Loyal Opposition Review, Interactive Session Role Override
  Slice 2.
- `DELIB-20260648` - envelope init-keyword optionality: subject mandatory, role
  optional.
- `DELIB-202665708` - WI-4981 mid-session init role switch verification verdict.
- Thread chain: `-002`, `-004`, `-006`, `-008` (all four closure-audited above).

---

## Review Methodology

- Read the full nine-version chain and extracted every discrete finding from all
  four NO-GOs into the closure table above.
- Re-ran three disclosed baselines (158/152/6; 21/18/3; 141 passed) and
  confirmed failure names match one-for-one.
- Executed
  `platform_tests/hooks/test_workstream_focus.py::test_sessionstart_plus_daemon_dispatch_prompt_without_marker_processes_bridge_task`
  (1 passed) and traced the call path through
  `scripts/workstream_focus.py:2008` -> `:1151-1158` -> the parser.
- Read `scripts/session_start_dispatch_core.py:313`, `:462`, `:655-656` to
  falsify the receiver-gate claim.
- Verified all 10 declared `target_paths` and confirmed
  `platform_tests/hooks/test_workstream_focus.py` is absent from every declared
  surface.
- Verified all 17 linked specifications, the PAUTH, and WI-5679 in MemBase.
- Ran both mandatory preflights and a deliberation search.

## Review Independence

Reviewer session context `beb9672b-f0a6-4caf-8e51-925fdc3dfb49` (harness B,
Claude). Proposal author session context
`019f863a-acd3-7320-80c0-1831f0936cc0` (harness A, Codex). All four prior LO
verdicts were authored under distinct session contexts. Independence gate
satisfied.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.*
