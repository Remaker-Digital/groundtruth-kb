REVISED
::init gtkb lo
::open build

# WI-6216 Slice 1 — REVISED: template parity path, and D2 withdrawn as unverifiable

bridge_kind: prime_proposal
Document: gtkb-wi6216-tool-and-gate-defect-corpus-slice-1
Version: 007
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: a0dbbe63-b24f-42eb-9274-e0fec8b23a00
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6216
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", ".harness-baseline-configuration/hooks/bridge-compliance-gate.py", ".goose/hooks/bridge-compliance-gate.py", ".goose/.projection-manifest.json", "platform_tests/scripts/test_bridge_compliance_gate_pending_banner.py", "platform_tests/scripts/test_report_no_go_resume_tolerance.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation.

Responds to: bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-006.md

---

## Why This Revision Exists

D1 and D3 are implemented, tested and green. Implementation surfaced two scope
problems that cannot be resolved inside the approved `target_paths`:

1. **A third copy of the gate hook exists** and must stay byte-identical to the
   active one. It is not in `target_paths`.
2. **D2's mechanism claim cannot be verified at source**, and the file it names
   contains no logic of the kind the repair describes.

D1 and D3 are unchanged from `-005`. Nothing else moves.

## Change 1 — Add the activation template to `target_paths`

`platform_tests/scripts/test_bridge_compliance_gate_disposition.py` states:

> "The active hook and the activation template must be byte-identical; the
> `test_template_and_active_hook_byte_identical` asserts parity."

with `TEMPLATE_HOOK = groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.
`.claude/rules/file-bridge-protocol.md` says the same: the gate is "activated
byte-for-byte from `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`".

The D1 repair therefore breaks that invariant until the template carries it too.
Measured, like-for-like over the same six modules:

| | failures |
|---|---:|
| at `HEAD` | 19 |
| with D1 + D3 applied | 21 |

The delta is **exactly two**, both `test_template_and_active_hook_byte_identical`
(in `test_bridge_compliance_gate_disposition.py` and
`test_bridge_compliance_requirement_sufficiency.py`). The other 19 are
pre-existing and unrelated — they fail identically at `HEAD` with the working
copies restored afterwards.

**Requested:** add `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` to
`target_paths` so the D1 repair lands in all three copies (active, template,
neutral baseline) and the parity assertions hold.

## Change 2 — D2 withdrawn from this slice as unverifiable

`-001` described D2 as "destructive-gate target misresolution", citing a
single-file `Remove-Item .git/index.lock` blocked as "Remove-Item on system path
'E:\GT-KB'", and scoped the repair as "resolve targets only from parsed command
ARGUMENTS (never message/prose flag values like `-m` bodies)". `-002` accepted
D2 without change.

Two findings from attempting it:

**(a) The quoted message does not exist in the codebase.** A repository-wide
search for `on system path` across all Python sources returns no matches. The
message in the proposal is a paraphrase, not a source string, so the emitting
surface cannot be identified from it.

**(b) `.claude/hooks/destructive-gate.py` contains no target resolution.** Read
in full: it is 279 lines of regex families (`_DELETE_PATTERNS_*`,
`_GIT_DESTRUCTIVE`, `_HOOK_BYPASS`, `_DB_DESTRUCTIVE`, `_AZURE_DESTRUCTIVE`,
`_PROD_ENV_PATTERNS`, `_EXFIL_PATTERNS`) matched against the command string,
plus `_mask_quoted_spans` and `_is_safe_path`. There is no path resolver to
scope to arguments, and no code that could produce a "system path" message. The
nearest real emitter found is
`groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py:340`
("Command contains blocked path argument: …"), which is the root-boundary
checker — a different surface, not in `target_paths`, and governed by
`.claude/rules/project-root-boundary.md` rather than the destructive gate.

**Requested:** drop D2 from this slice. It should be re-filed against the surface
that actually emits the block, with a verbatim reproduction rather than a
paraphrase. `WI-6216` remains open for it; the corpus is unchanged.

This is the same defect class `-002` F1 identified in D3 — a repair derived from
a mechanism claim that does not hold — and it is worth noting it survived into an
*accepted* finding. Implementing it as scoped would have meant editing a file
that cannot exhibit the described behaviour.

## Scope (revised)

1. **D1 repair** — unchanged from `-005`, and implemented: live-packet
   suppression, recency preference, root-anchored matching, parked-thread aging.
2. ~~D2~~ — withdrawn per Change 2.
3. **D3 repair (PARTIAL, by design)** — unchanged from `-005`: tolerate a
   trailing parenthetical annotation; `WI-6237` stays open for the index gate and
   the contract conflict, pinned by a residual-gap test.
4. **Projection parity** — the repaired hook lands in the active copy, the
   activation template (Change 1) and the neutral baseline, and is projected to
   `.goose`.
5. **Two regression modules** (the destructive-gate module is withdrawn with D2).

## Implementation Status At Time Of Filing

- `.claude/hooks/bridge-compliance-gate.py`: D1 implemented.
- `.harness-baseline-configuration/hooks/bridge-compliance-gate.py`: same change
  spliced (the baseline is not byte-identical to the active copy, so the logical
  change was applied rather than the file copied); parses cleanly.
- `.goose/`: projected — `--check` reported `1 drifted of 127 managed` before,
  `0 drifted of 127 managed` after.
- `scripts/implementation_authorization.py`: D3 implemented.
- `test_bridge_compliance_gate_pending_banner.py`: **11 passed**.
- `test_report_no_go_resume_tolerance.py`: **7 passed**.
- Red-first: against the `HEAD` hook, **6 of 11** D1 tests fail — covering all
  four sub-repairs — while the 5 guard tests pass, confirming the new assertions
  exercise the changed mechanism rather than co-occurring with it.
- `ruff check`: All checks passed. `ruff format --check`: all files formatted
  (two files needed `ruff format` first; the gates are separate).
- The template copy is NOT yet updated — that is what Change 1 requests.

## Specification-Derived Verification

| Requirement | Test | Executed | Result |
|---|---|---|---|
| D1(a) live-packet suppression | `test_live_packet_suppresses_the_banner` | yes | pass |
| D1(a) guard | `test_expired_packet_does_not_suppress`, `test_packet_for_a_different_path_does_not_suppress` | yes | pass |
| D1(b) recency | `test_most_recently_active_thread_is_named` | yes | pass |
| D1(c) root-anchored | `test_suffix_collision_does_not_claim_the_path`, `test_glob_target_claims_the_path`, `test_directory_prefix_claims_children`, `test_exact_target_claims_the_path` | yes | pass |
| D1(d) parked aging | `test_long_parked_no_go_does_not_claim` | yes | pass |
| D1(d) guards | `test_recent_no_go_still_claims`, `test_long_parked_new_is_not_aged_out` | yes | pass |
| D3 tolerance | `test_trailing_parenthetical_annotation_is_tolerated` | yes | pass |
| D3 fail-closed | `test_second_path_on_the_line_still_fails_closed`, `test_unclosed_parenthesis_fails_closed` | yes | pass |
| D3 residual gap (WI-6237) | `test_index_gate_still_rejects_intervening_non_report` | yes | pass |
| D3 drift guard | `test_regex_in_source_matches_the_tested_pattern` | yes | pass |
| Change 1 (after GO) | `test_template_and_active_hook_byte_identical` x2 | pending | currently failing; the reason for this revision |

```
python -m pytest platform_tests/scripts/test_bridge_compliance_gate_pending_banner.py -q   -> 11 passed
python -m pytest platform_tests/scripts/test_report_no_go_resume_tolerance.py -q           -> 7 passed
python -m ruff check <changed>                                                             -> All checks passed!
python -m ruff format --check <changed>                                                    -> all formatted
python scripts/harness_projection/project_harness.py --harness goose --check               -> 0 drifted of 127
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — D1/D3 repair the bridge protocol's own
  guidance and recovery surfaces.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — D3's stranded path is the lawful
  post-NO-GO revision route.
- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — obligation 2: the repair lands in the
  baseline and projects mechanically; Change 1 extends that to the activation
  template, which the same obligation implies.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — the failure counts, the absent
  `on system path` string and the projection results are fresh measurements.
- `SPEC-1662` (GOV-18) — behavioral assertions, with red-first evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1.

## Requirement Sufficiency

Existing requirements sufficient. Both changes correct the slice's own scope
against verified evidence; neither creates a requirement surface. Withdrawing D2
leaves an already-tracked corpus item open rather than closing it on an
unverifiable mechanism.

## Owner Decisions / Input

- Owner standing directive (2026-08-13/14): capture and fix tool defects;
  `WI-6216` is the owner-created carrier for this corpus.
- Owner directive (2026-08-14): the verifying Loyal Opposition commits the work
  and uses commit success as the trigger to emit VERIFIED. **This implementation
  has deliberately NOT been committed** — the changes sit in the worktree for the
  verifying LO to commit.
- No new owner decision is required. Withdrawing D2 and adding a parity path are
  scope corrections put through review rather than made unilaterally.

## Prior Deliberations

- `bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-006.md` — the GO this
  revises.
- `bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-002.md` F1 — the NO-GO
  that caught the same defect class in D3; Change 2 applies its lesson to D2.
- `bridge/gtkb-operation-taxonomy-baseline-path-rules-006.md` F2 — establishes
  the two barriers D3 leaves open.
- `DELIB-20260813-TOOL-AND-GATE-FLAWS` — the 13-item corpus.
- `WI-6237` / `TEST-11901` — D3's work item, deliberately left open.

## Cross-Harness Disposition

- **Claude Code** (`.claude/hooks/`): repaired in place; byte-identical to the
  activation template once Change 1 lands.
- **Goose** (`.goose/hooks/`): mechanical re-projection from the repaired
  baseline; `--check` 0-drift evidence above.
- **Codex, Cursor, Antigravity, API harnesses**: carry no copy of the affected
  gate. No behavioral change reaches them this slice. Typed disposition:
  `deferred-to-projector-cutover`.

## Risk / Rollback

D1 loosens a banner (a guidance surface, not a gate), so the risk is a genuinely
unauthorized edit going un-bannered. Three guard tests bound it: an expired
packet does not suppress, a packet for a different path does not suppress, and a
recent NO-GO still claims. D3 narrows a parse and keeps every other check;
its fail-closed cases are pinned by two tests.

Rollback is reverting two source files, the template, the baseline copy, and
re-projecting.

## Recommended Commit Type

Recommended commit type: `fix` — repairs to broken gate behaviour with
regression tests; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
