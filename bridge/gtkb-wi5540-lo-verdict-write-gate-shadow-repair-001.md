NEW
::init gtkb lo
::open build

# gtkb-wi5540-lo-verdict-write-gate-shadow-repair — Repair controlled_artifact_paths.py shadowing lo-file-safety-gate.py's new-LO-verdict allow-rule

bridge_kind: prime_proposal
Document: gtkb-wi5540-lo-verdict-write-gate-shadow-repair
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-18 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6834c55b-a1b4-44de-98d1-8f49d316296c
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; session-stated role overridden to prime-builder via ::init gtkb pb (durable registry role for harness B is loyal-opposition; this session's resolved role is prime-builder for the remainder of the interactive context per DCL-SESSION-ROLE-RESOLUTION-001)

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5540

target_paths: ["scripts/controlled_artifact_paths.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: source | test | governance-hook-classification-fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
hook_registration_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

---

## Summary

`.claude/hooks/lo-file-safety-gate.py::_bridge_file_decision()` (lines 62-63,
455-472) already implements the correct, intended policy for Loyal Opposition
verdict authoring: a `Write` creating a **new** `bridge/<slug>-NNN.md` file
whose first non-blank line is `GO`, `NO-GO`, `VERIFIED`, or `ADVISORY` is
explicitly allowed (`LO_STATUS_TOKENS` + `VERSIONED_BRIDGE_PATH_RE`). But
`scripts/controlled_artifact_paths.py::classify_controlled_artifact()` — which
feeds the separate, independently-AND-gated `scripts/implementation_start_gate.py`
PreToolUse hook — classifies **every** path matching `VERSIONED_BRIDGE_FILE_RE`
(`bridge/<slug>-NNN.md`) as `direct_write_blocked=True`
(`reason_code=bridge_status_file_direct_mutation`) with zero awareness of
file-existence or first-line content. Because PreToolUse hooks are
independently AND-gated (any one hook's block wins), `lo-file-safety-gate.py`'s
correct, content-aware allowance is silently overridden by
`implementation_start_gate.py`'s cruder, content-blind block. The net effect,
confirmed live on bridge thread `gtkb-wi5343-lo-review-authority-packet`: a
direct `Write` of a new `-006.md` verdict file (first line `GO`) was blocked
with `BLOCKED (GTKB-CONTROLLED-ARTIFACT-DIRECT-MUTATION):
PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, even though that is exactly
the shape of write `lo-file-safety-gate.py` was built to allow. Loyal
Opposition sessions have been routing around this with disposable,
per-thread wrapper scripts (`.claude/skills/verify/helpers/file_go_verdict_wi5438.py`,
`file_go_verdict_wi5518.py`, `file_no_go_verdict_wi5343.py`,
`file_no_go_verdict_wi5445.py`, `write_bridge_5171.py`,
`write_bridge_gtkb_retire_ipa_refs_006.py`) since 2026-07-16, each one's own
docstring documenting the workaround as a deliberate "precedent," not a
one-off — direct evidence this is a systemic gap actively costing session
effort across the LO-actionable queue, not a single misfire.

This proposal threads Write/Edit/MultiEdit candidate **content** through
`implementation_start_gate.py::changed_paths()` into
`controlled_artifact_paths.py::classify_controlled_artifact()` (currently a
pure path-string classifier with no content parameter) so it can apply the
exact same new-file-plus-valid-status-token exemption `lo-file-safety-gate.py`
already implements, restoring the two hooks to policy agreement instead of one
silently overriding the other.

Out of scope for this proposal (documented for a follow-on owner/Codex
sequencing decision, not silently absorbed):

- **No sanctioned one-command CLI for filing a GO/NO-GO verdict.**
  `.claude/skills/verify/helpers/write_verdict.py` only exposes
  `--finalize-verified`. The validated primitive
  `scripts/gtkb_bridge_writer.py::publish_lo_verdict()` already supports
  GO/NO-GO/VERIFIED with real role/claim/transition/guard-hook validation, but
  is only ever called in-process by headless provider-harness shims
  (`scripts/ollama_harness.py` etc. via `harness-state/harness-registry.json`'s
  `headless.argv`), never exposed to interactive Claude/Codex sessions. This
  is why the ad hoc wrapper scripts above call the lower-level
  `write_bridge_file()` directly instead, bypassing `publish_lo_verdict()`'s
  validation entirely. Recommend a follow-on WI to expose `publish_lo_verdict`
  (or a narrower purpose-built wrapper) via CLI, replacing the ad hoc
  precedent scripts — open design question below on whether
  `_resolve_lo_worker`/`resolve_worker_role_provenance` actually resolves for
  an interactive (non-headless-worker) session.
- **Heredoc/stdin-fed Bash source false-positiving the redirect/mutating-signal
  scan.** Both `lo-file-safety-gate.py` (`WRITEISH_COMMAND_RE`) and
  `implementation_start_gate.py` (`_shell_redirect_present`,
  `MUTATING_COMMAND_RE`) scan the full multi-line Bash command text — including
  a heredoc body — for shell-mutation signals, with no way to distinguish a
  real `>` redirect from a `>` comparison/type-hint/f-string-spec, or a
  backtick-quoted jargon token, embedded in piped source or markdown prose.
  WI-5540's own description independently reproduced a variant of this (a
  false-positive on backtick-quoted jargon inside a large single Bash command
  line carrying `write_bridge.py`'s `propose_bridge()`). Fixing this properly
  touches `.claude/hooks/lo-file-safety-gate.py`, which is the exact file
  `bridge/gtkb-wi5497-lo-file-safety-live-carrier-hardening-001.md` (currently
  `NEW`, Codex-queued, `PAUTH-...-WI5497-...` scoped to WI-5497 only) is
  actively refactoring into a new shared `scripts/lo_file_safety_payloads.py`
  normalizer. Recommend this land only after WI-5497 reaches `VERIFIED`,
  targeting the new normalizer rather than the pre-refactor regex soup, to
  avoid the exact live target-path-collision pattern
  `bridge/gtkb-wi5343-lo-review-authority-packet-006.md` (read directly this
  session; NO-GO for an unrelated reason) just described for a different
  thread pair (WI-5343 vs. WI-5389).

## In-Root Placement Evidence

Every implementation target is inside `E:/GT-KB`:

- `scripts/controlled_artifact_paths.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_controlled_artifact_paths.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

All four already exist; no new top-level surface, external dependency, or
out-of-root evidence source is introduced.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — defines the bridge protocol's GO / NO-GO /
  VERIFIED / ADVISORY statuses and Loyal Opposition's authority to author
  them; this proposal restores, rather than changes, that authority's
  mechanical enforcement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites every governing specification it touches.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project, PAUTH, Work
  Item, and `target_paths` are named above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent `VERIFIED`
  requires executed tests derived from the linked authorities; see the
  Spec-Derived Verification Plan below.
- `GOV-STANDING-BACKLOG-001` — `WI-5540` (and its GOV-12 linked test
  `TEST-11601`) are the canonical work and test carriers for this defect; no
  duplicate work item is created. (Backlog check performed this session:
  `gt projects show PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` surfaced three
  related-but-distinct open items — `WI-5480` chained-read-only-command false
  positives in `_is_safe_command()`, `WI-5481` the PowerShell-tool matcher
  exclusion bypass, `WI-5505` stale-claim citation plus KnowledgeDB-mutation
  incorrectly requiring GO — none of which cover this specific
  content-blind/existence-blind bridge-status-file classification gap; they
  are cited as siblings in Prior Deliberations, not folded into this scope.)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
  / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this defect was captured as a
  standing work item (`WI-5540`) with a linked test (`TEST-11601`) per the
  artifact-lifecycle-trigger discipline before this proposal was drafted.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — author metadata above is concrete,
  session-resolved (not synthetic), matching the current interactive session.

## Prior Deliberations

- **`WI-5540`** (MemBase work item, this proposal's governing WI) —
  "LO-file-safety allow-rule for fresh ADVISORY bridge files is shadowed by a
  stricter controlled-artifact-mutation gate." Filed 2026-07-18 by an
  independent prior Loyal Opposition session (harness B, durable-registry-role
  session, session id `8e0b4e69-e221-4d23-9bfd-e5d9591e66f2`) that hit this
  exact wall while trying to file an LO ADVISORY for WI-5533 and could not
  find any working mechanical path — it reported findings to the owner
  directly in chat instead. This proposal is the implementation response to
  that WI; independent re-derivation this session (before discovering WI-5540
  existed) reached the same root-cause diagnosis via direct code reading,
  confirming WI-5540's finding rather than merely repeating it.
- **`TEST-11601`** (MemBase test, GOV-12-linked to WI-5540) — states the exact
  expected outcome this proposal must satisfy: "FAIL if a Claude Write (or the
  documented helper-mediated Bash path) of a new `bridge/<slug>-NNN.md` file,
  first non-blank line one of GO/NO-GO/VERIFIED/ADVISORY, authored under a
  session resolved to loyal-opposition, is blocked by any hook requiring a
  bridge-GO implementation-authorization packet or work-intent claim." No test
  code exists yet (`test_file`/`test_class`/`test_function` are null); this
  proposal's Spec-Derived Verification Plan below specifies where that test
  code lands.
- **`WI-5533`** — the session-envelope work-item-tracking defect the
  originating LO session was drafting an advisory for when it hit this wall.
  Cited for provenance only; unrelated to this proposal's substance.
- **`bridge/gtkb-wi5343-lo-review-authority-packet-001.md` through `-006.md`**
  — read in full this session. Version `-006.md` (status `NO-GO`, unrelated
  substantive reason: a live target-path collision with
  `gtkb-wi5389-codex-no-window-schema-contract`) is direct, current-state
  evidence that a **different** independent LO sub-agent session
  (`author_session_context_id: 6863e929-50d6-4dc2-8bd0-6f2295e0f562`)
  successfully filed a new versioned verdict file — but only via the
  disk-resident-wrapper-script workaround, after the original
  defect-discovering sub-agent (whose report initiated this investigation)
  gave up on the same thread using a direct `Write` and a heredoc-fed
  `write_bridge_file()` call.
- **`DELIB-2492`** — "Loyal Opposition Review - LO File-Safety PreToolUse
  Enforcement Slice 1," the original review that produced
  `lo-file-safety-gate.py`'s current allow-list design, including the
  new-verdict-file exemption this proposal is restoring parity with. Searched
  this session (`lo-file-safety-gate opaque shell mutation`); no prior
  deliberation record addresses the specific two-hook shadowing this proposal
  fixes.
- **`DELIB-20264182`** / **`DELIB-20264178`** — "Loyal Opposition Review /
  Verification - implementation_start_gate Finalization Quoting Fix"
  (WI-3357). A **different**, already-resolved defect in the same file
  (shell-quoting in finalization commit messages), surfaced by the same
  deliberation search; cited to show `implementation_start_gate.py` has a
  documented history of narrow edge-case gaps requiring targeted fixes, of
  which this is another instance, not a first occurrence.
- **`INTAKE-b4928376`** (seeded by the propose-scaffold tool) — "Bridge review
  eligibility is harness-agnostic; durable role is a fallback, not a
  review/verdict gate." Directly supportive: reinforces that verdict-authoring
  eligibility should turn on role/content, not on an unrelated Prime-Builder
  implementation-authorization mechanism.
- **`INTAKE-9d534667`** / **`INTAKE-9314e628`** / **`INTAKE-743f4dfb`** (seeded)
  — LO GO / VERIFIED / NO-GO verdict required-fields intake records. Adjacent
  (verdict-content shape), not substantively overlapping with this
  classification-gate defect; not pruned because a reviewer may want the
  cross-reference when touching the same verdict-writing surface.
- `INTAKE-e226b05a` ("LO Advisory Owner-Grilling Gate") was seeded by the
  propose-scaffold tool but is not relevant to a gate-classification defect;
  pruned.

## Owner Decisions / Input

No fresh owner approval was sought to **file** this proposal — filing a
bridge implementation proposal is standing-authorized ordinary Prime Builder
work per `CLAUDE.md` and does not itself require `AskUserQuestion` evidence.

`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
(owner decision `DELIB-202666274`) is an active, project-scoped authorization
covering "all source, test, configuration... required to complete the active
Assurance project," explicitly stated to have "no per-work-item inclusion
restriction." `WI-5540` is a confirmed member work item of
`PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE` (`gt projects show
PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`, checked live this session), so
this PAUTH's scope applies. That PAUTH explicitly preserves "independent
proposal GO, matching work-intent claim, implementation-start authority,
spec-derived tests, independent VERIFIED, and nonimpairment" as mandatory —
this proposal does not treat the PAUTH as a substitute for Codex GO or the
implementation-start packet.

Open item for Codex / owner (not blocking filing, but should be resolved
before or during review): should the new-file-plus-status-token exemption in
`classify_controlled_artifact` additionally check that the *current session's
resolved role* is `loyal-opposition` (defense in depth), given that function
is otherwise a pure, role-blind path/content classifier? Content alone
(`GO`/`NO-GO`/`VERIFIED`/`ADVISORY` are exclusively `LOYAL_OPPOSITION_STATUSES`
per `scripts/gtkb_bridge_writer.py`; Prime never legitimately authors them)
already makes this safe in practice, and `lo-file-safety-gate.py`'s own
existing exemption is likewise role-blind at the content-check layer (its
role gate is a separate, earlier check — `_is_lo_enforced` only restricts
Prime-authored writes elsewhere in that hook, not this specific allow
branch). Recommend keeping `classify_controlled_artifact` role-blind for
symmetry with the hook it is being brought into parity with, but flagging this
explicitly rather than deciding it silently.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already
establishes Loyal Opposition's authority to author GO/NO-GO/VERIFIED/ADVISORY
verdicts, and `.claude/hooks/lo-file-safety-gate.py` already correctly
mechanizes that authority for new bridge-status files. The defect is an
inconsistency between two enforcement points for the same already-specified
policy, not an unresolved policy question. No new role, status token,
dispatcher rule, or artifact authority is required.

## Spec-Derived Verification Plan

| Governing requirement | Test | Expected result |
|---|---|---|
| `TEST-11601` / `GOV-FILE-BRIDGE-AUTHORITY-001` | New parametrized test in `platform_tests/scripts/test_implementation_start_gate.py` (implements `TEST-11601`'s recorded `expected_outcome`; sets `test_file`/`test_class`/`test_function` on the KB row at implementation time): a `Write` creating a **new** `bridge/<slug>-NNN.md` file with first line `GO`, `NO-GO`, `VERIFIED`, or `ADVISORY` returns `gate_decision(payload) == {}` (no block). | PASS for all four status tokens. |
| Existing regression: `test_raw_write_bridge_status_path_aliases_remain_direct_mutation_denials` (`platform_tests/scripts/test_implementation_start_gate.py:1094-1105`) | This test currently asserts `decision == "block"` for a `Write` with `content: "GO\n"` at a path that does not exist on disk under a fresh `tmp_path` — exactly the case this proposal changes to `allow`. Must be split: (a) retain alias coverage (`path` vs. `file_path` keys both recognized) using a scenario that **remains blocked** — e.g. the same content but simulating an **existing** file at that path, or non-status content — and (b) add a new assertion (or a new adjacent test) proving the **new-file, valid-status-token** case for both key aliases now returns `{}`. | (a) still blocks; (b) newly allows. Zero net regression in alias coverage. |
| `test_bridge_status_file_write_blocks_without_governed_helper` (`:1080-1091`, `apply_patch` "Add File" with content `NEW`) | Unaffected — `NEW` is not in `LO_STATUS_TOKENS`; must remain `block`. | Unchanged, still PASS. |
| `test_non_status_bridge_note_write_remains_open_without_authorization` (`:1108-1115`) and `test_direct_controlled_artifacts_are_block_classified` / `test_diagnostic_and_non_status_bridge_paths_remain_open` (`platform_tests/scripts/test_controlled_artifact_paths.py`) | Unaffected by this change (non-status-bearing bridge notes, `groundtruth.db`, runtime-authority paths, other `PROTECTED_PREFIXES`); must remain green with no source or assertion changes. | Unchanged, still PASS. |
| New: EXISTING-file case | New test: a `Write` to an EXISTING `bridge/<slug>-NNN.md` file (any content, including a valid status token) still returns `block` — the exemption is new-file-only, matching `lo-file-safety-gate.py`'s own `not change.abs_path.exists()` guard exactly. | PASS (still blocked). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full focused run plus repo-wide regression: | All PASS. |

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_implementation_start_gate.py -q --no-header
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/controlled_artifact_paths.py scripts/implementation_start_gate.py platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_implementation_start_gate.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/controlled_artifact_paths.py scripts/implementation_start_gate.py platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_implementation_start_gate.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/controlled_artifact_paths.py scripts/implementation_start_gate.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5540-lo-verdict-write-gate-shadow-repair
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5540-lo-verdict-write-gate-shadow-repair
```

Additionally: a live end-to-end reproduction against a real new bridge file in
a disposable temp bridge dir (not `tmp_path`-mocked `gate_decision()` calls
alone) — construct a payload identical in shape to the one that blocked
`bridge/gtkb-wi5343-lo-review-authority-packet-006.md` and confirm it now
returns `{}` pre-fix-reproduction / post-fix-pass.

## Risk / Rollback

**Risk surface:** the change adds content-inspection to a function
(`classify_controlled_artifact`) that today only inspects a path string; it
must thread `content` through `implementation_start_gate.py::changed_paths()`'s
Write/Edit/MultiEdit branch (currently extracts only `path`) without changing
behavior for any other tool type or any existing-file case. The narrowest-risk
implementation mirrors `lo-file-safety-gate.py::_bridge_file_decision()`'s
existing three guards exactly (new file only, `bridge/<slug>-NNN.md` shape
only, first-non-blank-line token match only) rather than inventing new
classification logic — reducing this to a parity fix, not a new design.
Residual risk: `MultiEdit`/`Edit` payload shapes for a **new** file are
unusual (those tools normally target existing files); the implementation must
confirm `data.get("content")` is only trusted for `Write`, and that
`Edit`/`MultiEdit` against a nonexistent target continue to fall through to
existing behavior (they are not the shape LO verdict-authoring uses).

**Rollback:** single-commit revert of the four target files; no schema,
dispatcher, TAFE, or MemBase state is touched, so rollback has no
downstream cleanup.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5540-lo-verdict-write-gate-shadow-repair`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(governance)` — repairs a defect (two hooks disagreeing on already-specified
policy); adds no new capability, role, or artifact type.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
