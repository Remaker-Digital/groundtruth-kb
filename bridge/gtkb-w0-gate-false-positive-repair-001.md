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
Document: gtkb-w0-gate-false-positive-repair
Version: 001
Date: 2026-08-06 UTC
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5480
target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", ".claude/hooks/scanner-safe-writer.py", "scripts/implementation_start_gate.py", "scripts/_kb_attribution.py", "scripts/adr_dcl_clause_preflight.py", ".claude/settings.json", ".cursor/hooks.json", ".claude/hooks/spec-before-code.py", ".claude/hooks/kb-not-markdown.py", "config/governance/gate-fp-corpus.toml", "platform_tests/scripts/test_gate_fp_corpus.py", "platform_tests/hooks/test_scanner_safe_writer_md_prose.py", "platform_tests/hooks/test_implementation_start_gate_invalid_payload.py", "platform_tests/hooks/test_claude_settings_hook_dedupe.py", "platform_tests/hooks/test_cursor_hooks_single_invocation.py", "platform_tests/scripts/test_gate_message_remedies.py"]

# W0.3 — Make the Gates Honest: governance-gate false-positive repair, gate-message remedies, and duplicate-registration dedupe

## Summary

The governance gates are producing a measured, high-volume stream of false
positives that (a) burn agent turns on byte-identical re-blocks, (b) train
sessions to treat gate denials as noise, and (c) mask the true-positive
denials the gates exist for. This proposal repairs six precision defects in
the enforcement/gate surfaces WITHOUT weakening any boundary or removing any
defense layer: the project-root boundary itself is unchanged, the C:-drive
user-profile blanket block stays, and the two-layer credential defense
(scanner-safe-writer + credential-scan) is preserved.

Measured context (live re-derivation, 2026-08-06, from
`.gtkb-state/gate-denials.jsonl`; window 2026-07-01 -> 2026-08-06, 7,347
records; prior-audit figures dated 2026-08-06 were 7,329 records):

- 31.8% of all gate denials are byte-identical re-blocks (same gate +
  command_hash + pattern_id; prior audit: 32.2%). Worst identical run: 509
  consecutive blocks of one identical command by `implementation-start-gate`
  (`protected-target-without-go`, single command_hash).
- Per-gate volume: implementation-start-gate 3,787; bridge-compliance-gate
  1,911; directive-enforcement-claude-adapter 1,130; the formal-artifact gate
  252; codex-directive-enforcement 148; the narrative-artifact gate 103;
  scanner-safe-writer 16. (This proposal performs no approval-evidence work;
  those two gates appear here only as denial-count statistics.)
- Top false-positive classes: harness-scratchpad path blocks 610 (prior 607);
  `.cursor` path blocks 121 (prior 113); PowerShell-backtick path mangling 69
  of 951 boundary denials (prior 63); the project's own `gt.cmd` shim 13;
  scanner-safe-writer `-p` prose matches 16 (16/16 false in production per the
  prior audit). The `<unknown-mutating-target>` sentinel appears 2,728 times.
- Live demonstration during the drafting of this very proposal (2026-08-06):
  the directive-enforcement Write gate blocked this session's own
  harness-scratchpad write under `%LOCALAPPDATA%/Temp/claude/...` with
  "resolves to blocked location" — the exact 610-denial class item 1 repairs.

Two registered PreToolUse hooks are verified no-op stubs (exit 0, emit
nothing), and five duplicate hook registrations exist in
`.claude/settings.json`. `.cursor/hooks.json` double-invokes three gates on
both `beforeShellExecution` and `preToolUse`.

## Specification Links

- `GOV-17` — Automation script modification approval gate. Every file in
  `target_paths` is (or registers) an automation script/hook; **this proposal
  and its Loyal Opposition GO constitute exactly that approval.** No gate or
  hook is modified before GO.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — two-layer
  defense in depth (write-time + review-time) is retained. The
  scanner-safe-writer change is context-gating of one pattern's application,
  not layer removal; `credential-scan.py` remains the general write-time
  layer, and LO review remains the review-time layer.
- `.claude/rules/project-root-boundary.md` (DIR-ROOT-BOUNDARY-001) — **the
  root boundary itself is unchanged.** All active GT-KB artifacts remain
  required to live under `E:\GT-KB`; `E:\Claude-Playground` and other
  out-of-root locations remain blocked; the user-profile blanket block stays.
  This proposal changes only false-positive *classification precision* (which
  strings are recognized as genuine out-of-root path/command usage) plus
  narrow, enumerated exemptions consistent with the existing harness-directory
  exemption already present at `enforcement/__init__.py:279`.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — gate-parser changes must exercise the
  cross-gate false-positive regression corpus
  (`config/governance/gate-fp-corpus.toml` +
  `platform_tests/scripts/test_gate_fp_corpus.py`); this proposal extends that
  corpus as its primary regression surface.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` / `SPEC-AUQ-POLICY-ENGINE-001` — the
  corpus-governing specs cited by `test_gate_fp_corpus.py`; deterministic
  parser behavior only, no classifier heuristics added.
- `DCL-SOT-READ-HOOK-CONTRACT-001` — context: the PreToolUse interception
  surfaces changed here are siblings of the SoT read-discipline surface; the
  two-surface (Claude/Codex) contract is not altered.
- `GOV-CLAUDE-MD` § Protected Behaviors & Removal Rule (CLAUDE.md) — the no-op
  stub disposition is routed as an explicit LO/owner decision item, not a
  silent removal (see Decision Item below).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the bridge numbered-file chain is
  canonical and append-only; this thread follows the standard propose -> GO ->
  implement -> report -> VERIFIED lifecycle and repairs no bridge files.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linked governing
  specs are explicit.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/work-item
  linkage is explicit (WI-5480 under
  PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, covered by the cited list-free
  whole-project authorization).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  below derives tests from the linked specifications; VERIFIED requires their
  execution evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — scope guard: no dispatcher
  files, no bridge writer/publisher files, no lifecycle-resolver files are
  touched; concurrent threads (WI-5314, WI-5827) are unimpaired.
- `GOV-WORK-TREE-HYGIENE-001` — scoped edits only; no concurrent bridge bytes
  overwritten.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — governed artifact lifecycle applies;
  stub retirement (if selected) is recorded with tombstones, not silent
  deletion.

## Prior Deliberations

Deliberation search run 2026-08-06 via `gt deliberations search` with queries
"directive enforcement root boundary false positive", "scanner safe writer
credential scan", and "gate denial false positive hygiene friction" (limit 5
each). Relevant priors:

- `DELIB-0736` — bridge thread `gtkb-hook-scanner-safe-writer` (12 versions,
  VERIFIED): the originating scanner-safe-writer thread. This proposal narrows
  ONE pattern's application context (`bash_password_flag_p` on `.md` prose);
  it does not revisit the hook's mandate or its canonical-catalog sourcing.
- `DELIB-0693` — NO-GO: WI-3142 Credential Scan Narrowing Re-Review: a prior
  credential-scan narrowing attempt was rejected. Acknowledged and honored:
  this proposal does **not** modify `credential-scan.py` or the canonical
  catalog (`groundtruth_kb/governance/credential_patterns.py`). The
  scanner-safe-writer change is application-context gating in the bridge-scoped
  hook only, with an explicit BLOCK regression case for a real
  credential-shaped value in `.md` content.
- `DELIB-20264201` — NO-GO: Implementation Gate Friction Hygiene REVISED-015:
  prior gate-friction thread; its lesson (bounded scope, per-change regression
  evidence) shapes this proposal's per-item test matrix.
- `DELIB-20263741` — VERIFIED: bridge-compliance-gate `SPEC_TEST_HEADING_RE`
  re.MULTILINE fix: precedent that surgical gate-regex fixes with regression
  tests are the accepted repair shape.
- Backlog conflict check (GOV-STANDING-BACKLOG-001): open WIs `WI-5480`
  (impl-start-gate false-positive-blocks chained read-only commands — the
  cited anchor WI), `WI-5676` (DIRECT-HARNESS-INVOKE-BAN false positives on
  GTKB_AUTHOR_IDENTITY), `WI-5877` (CODEX_HOME false positive), `WI-5886`
  (governance-gate false-positive hardening batch 2), `WI-5859` (gate false
  positives on read-only work), and `WI-5932` (bash parser false positives on
  harness identifiers in prose) are adjacent. This thread implements the
  denial-log-measured classes; it does not implement WI-5676/WI-5877/WI-5886's
  distinct classes, and any overlap discovered at implementation time is
  brought forward here rather than duplicated.

## Owner Decisions / Input

- Owner AUQ, 2026-08-06: **"Expand Wave 0 now"** — owner selected expanding
  Wave 0 remediation immediately.
- Owner AUQ, 2026-08-06: **"Yes — file W0.1/W0.3/W0.4 now"** — split-phase
  adoption: file the Wave-0 proposals now (this filing is W0.3 PHASE 1);
  implementation remains gated on LO GO (PHASE 2). Filing now is authorized;
  implementation is not authorized by this filing.
- Owner AUQ, 2026-08-05: the four Wave-0 plan answers approving the
  remediation plan shape (measured-evidence-first, one bridge thread per work
  packet, no boundary weakening, regression-test mandate per behavioral
  claim).
- Standing authority: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  (active, unexpired, list-free whole-project authorization; WI-5480 is an
  active member). Per `.claude/rules/codex-review-gate.md`, project
  authorization is additive: implementation still requires this proposal's GO
  plus an implementation-start packet.
- The no-op stub disposition (item 7) is explicitly deferred to LO/owner
  decision in this thread; the recommendation below is not self-approval.

## Requirement Sufficiency

Existing requirements sufficient. The governing specifications above already
require (a) mechanical enforcement of cross-cutting requirements with
two-layer defense, (b) root-boundary containment, and (c) corpus-backed
regression coverage for gate-parser changes. No requirement text changes: the
boundary rules are unchanged and only enforcement *precision* is fixed. GOV-17
approval is supplied by this thread's GO.

## Proposed Changes (anchors verified live 2026-08-06)

### 1. `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` — boundary-classifier precision

Verified anchors: harness-parts exemption set at line 279
(`{".claude", ".codex", ".gemini", ".api-harness"}` inside
`check_path_boundary`); `PATH_DELIMITER_RE` at line 29 (prompt-packet anchor
said ~26 — drifted +3; `_DRIVE_ABSOLUTE`/`_UNC_ABSOLUTE`/`_ROOTED` component
patterns at lines 26-28); `_COMMAND_SEGMENT_RE` at line 36; `REDIRECTION_RE`
at line 12.

- **Exemption set (line 279):** extend the existing harness-directory
  exemption with: `.cursor` parts (121 denials; mirrors the four
  already-exempt harness directories); the harness scratchpad tree
  (`%LOCALAPPDATA%/Temp/claude/**/scratchpad/**` — 610 denials; matched by
  normalized prefix, not a user-profile-wide allow); the in-root
  `E:\GT-KB\scratchpad` prefix (defensive; already in-root-allowed, pinned by
  a corpus ALLOW case); and the user-local `gt.cmd` CLI shim (13 denials;
  exact-basename `gt.cmd` invocation-surface exemption, not a directory
  allow). **The user-profile (`C:`-drive `Users`) blanket block otherwise
  stays**, and `E:\Claude-Playground` remains blocked.
- **`PATH_DELIMITER_RE` (lines 26-29):** exclude the backtick character from
  the path-token character classes so PowerShell escape backticks stop being
  glommed onto path tokens and producing denials of the shape "Path
  'E:\GT-KB`' resolves outside allowed root 'E:\GT-KB'" (69 live boundary
  denials carry a backtick).
- **`_COMMAND_SEGMENT_RE` (line 36) + `REDIRECTION_RE` (line 12):**
  minimum-viable quote awareness — a `|` inside a quoted string is not a
  pipe/segment separator, and tokens inside heredoc/string bodies are not
  classified as command-initial. If full quote-state tracking proves out of
  scope during implementation, the declared fallback is: scope the
  git-lifecycle match to command-initial `git` tokens only, and say so
  explicitly in the post-implementation report. Either way the corpus BLOCK
  case for a genuine command-initial `git` lifecycle command must still pass.

### 2. `.claude/hooks/scanner-safe-writer.py` — `bash_password_flag_p` md-prose exemption

Verified anchors: fallback pattern triple at lines 215-219
(`re.compile(r"-p\s+['\"]?[^\s]+['\"]?\s")`, name `bash_password_flag_p`);
canonical source `groundtruth_kb/governance/credential_patterns.py:329`
(scope `Scope.BASH_CREDENTIAL`). Live log: 16 scanner-safe-writer denials,
16/16 false per the prior audit.

Change: in the bridge-scoped hook only, `bash_password_flag_p` (a
BASH_CREDENTIAL-scoped pattern) must not fire on `.md` prose or inside fenced
code blocks unless an adjacent secret-shaped value is present. The canonical
catalog is NOT modified; `credential-scan.py` remains the general layer
(two-layer defense preserved per
GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001).

Divergence finding (follow-on WI candidate, explicitly NOT in scope here):
`scanner-safe-writer.py` sources the canonical catalog
(`CREDENTIAL_PATTERNS + BASH_EXTRAS`) with a synchronized fallback, while
`credential-scan.py` hand-rolls 35 `re.compile` patterns with no canonical
import. Consolidation should be captured as a backlog work item, not done in
this thread (respecting `DELIB-0693`).

### 3. `scripts/implementation_start_gate.py` — empty/unparseable payload fail-open; name the real target

Verified anchors: `_read_payload` at line 2057 (empty stdin -> line 2060;
malformed JSON -> line 2064; non-dict -> line 2066, each setting
`INVALID_HOOK_PAYLOAD_KEY`, line 162); `gate_decision` fail-closed branch at
lines 1903-1913 ("invalid_hook_payload ... The gate fails closed because tool
intent cannot be verified."); `UNKNOWN_MUTATING_TARGET =
"<unknown-mutating-target>"` at line 252.

- **Empty/unparseable PreToolUse payload -> fail-OPEN** with a logged warning
  record appended to `.gtkb-state/gate-denials.jsonl` (existing schema:
  `schema_version`, `gate`, `pattern_id` = `invalid-payload-fail-open`,
  `reason`, `command_hash`, `timestamp_utc`). Rationale: an empty payload is
  an infrastructure/plumbing fault, not a policy violation; the current
  fail-closed branch produced identical-run storms (worst run: 509
  byte-identical blocks). Parseable payloads keep the exact current
  fail-closed policy path — no change to real denials.
- **When denying for real, resolve and name the actual target** instead of
  emitting the `<unknown-mutating-target>` sentinel (2,728 occurrences in the
  live log) wherever the payload permits resolution; the sentinel remains only
  for genuinely unresolvable output shapes.

This is the riskiest single item in the proposal; see Risk / Rollback.

### 4. Gate-message remedies

- **`scripts/_kb_attribution.py`** (verified: line 36 raises
  `RuntimeError("resolve_changed_by: current session id is missing; worker
  role provenance is required.")`): extend the error text of the
  missing/mismatched-session failures to state the fix verbatim: "open an
  envelope: gt session envelope open --harness-name <h> --init-keyword ...;
  then set <H>_SESSION_ID to the printed id". Per the canonical-terminology
  worker-role-provenance entry, the fix is opening an envelope, not setting
  more env vars — the message must say so.
- **`scripts/adr_dcl_clause_preflight.py`** (anchor partially drifted from the
  prompt packet, verified live): the Blocking Gaps markdown section ALREADY
  prints per-clause `Evidence required:` and `Evidence pattern:` hints (lines
  428-438), and `evaluate_evidence` emits a gap summary with both (line 322).
  Remaining scoped work: guarantee the per-clause expected-evidence hint
  reaches every exit-5 output path (including the `--out` file path and the
  lifecycle-error/no-operative-file branches where only the error code is
  printed today), and add a regression test asserting hint presence in exit-5
  output. No change to gate semantics or exit codes.

### 5. `.claude/settings.json` — remove the 5 duplicate registrations

Verified live (line anchors current at HEAD): `assertion-check.py` x2 in
SessionStart (lines 131 and 145 — the second is a redundant matcher-less
group at lines 141-149); `spec-event-surfacer.py` x2 in PostToolUse (164,
178) and `owner-decision-capture.py` x2 in PostToolUse (160, 186 — redundant
groups at 174-181 and 182-189); `intake-classifier.py` x2 (236, 278) and
`gov09-capture.py` x2 (240, 286) in UserPromptSubmit (redundant groups at
274-281 and 282-289). Dedupe to one registration each, keeping the
first-group entries. `platform_tests/hooks/test_claude_settings_hook_no_window.py`
is inspected and extended so the dedupe is regression-locked.

### 6. `.cursor/hooks.json` — stop double-invocation

Verified live: `destructive-gate.py`, `credential-scan.py`, and
`bridge-compliance-gate.py` are each registered under BOTH
`beforeShellExecution` (lines 32-50) and `preToolUse` (lines 78-90). Keep the
`preToolUse` registrations; remove the three duplicates from
`beforeShellExecution`. Other `beforeShellExecution` entries are untouched.

### 7. DECISION ITEM (LO/owner): no-op stub disposition

Verified live: `.claude/hooks/spec-before-code.py` and
`.claude/hooks/kb-not-markdown.py` are both recovery stubs that emit nothing
and exit 0 (their docstrings say so, citing WI-4449), yet both are registered
first in the PreToolUse chain (`.claude/settings.json` lines 10 and 14).

WI-4449 history: six governance hooks were registered while their on-disk
files were missing; commit `e90b2f03` restored files, and these two were
restored as explicit recovery stubs pending re-implementation that never
happened. They now cost a process spawn per PreToolUse event and misrepresent
the enforcement surface (registered-but-inert).

Options for the reviewing LO / owner:

- **(a) Retire with tombstone (recommended):** remove both registrations from
  `.claude/settings.json`; replace each file with a tombstone header (or
  delete with a tombstone note in the post-impl report) citing WI-4449 and
  this thread. Rationale: two years of stub status, zero enforcement value,
  per-event spawn cost, and honest-surface accounting. Routed as an explicit
  decision per CLAUDE.md Protected Behaviors & Removal Rule — this proposal
  does not self-approve the removal.
- **(b) Restore real enforcement logic:** re-implement spec-before-code and
  kb-not-markdown enforcement. This is materially larger scope and, if
  selected, should become its own WI + thread; this thread would then leave
  the stubs untouched.

The GO verdict should state which option is selected (or defer the item
explicitly); implementation follows the selection.

## Specification-Derived Verification

Spec-to-test mapping. Every behavioral claim above gets a regression test;
the primary parser surface is the established corpus
(`config/governance/gate-fp-corpus.toml` +
`platform_tests/scripts/test_gate_fp_corpus.py`, the mandated regression
surface per DCL-CROSS-HARNESS-ENFORCEMENT-001), extended with the cases
below; hook-level behavior gets dedicated modules under `platform_tests/`.

| Linked spec | Derived test (new or extended) | Expected |
| --- | --- | --- |
| project-root-boundary (unchanged boundary) | corpus: `E:\Claude-Playground` write/path case | still BLOCK |
| project-root-boundary (unchanged boundary) | corpus: harness launch outside root; direct hook-script exec | still BLOCK |
| DIR-ROOT-BOUNDARY-001 precision (item 1) | corpus: harness-scratchpad path ALLOW; `.cursor` path ALLOW (sanctioned locations); in-root scratchpad ALLOW; `gt.cmd` shim ALLOW | ALLOW |
| DIR-ROOT-BOUNDARY-001 precision (item 1) | corpus: backtick-escaped in-root path ALLOW; `/etc/` inside doc-string ALLOW; quoted-pipe ALLOW | ALLOW |
| DIR-ROOT-BOUNDARY-001 precision (item 1) | corpus: command-initial `git` lifecycle command | still BLOCK |
| GOV-CROSS-CUTTING-...-001 two-layer defense (item 2) | `test_scanner_safe_writer_md_prose.py`: `-p` in md prose ALLOW; `-p` adjacent to secret-shaped value BLOCK; real credential-shaped value in md BLOCK | ALLOW / BLOCK / BLOCK |
| GOV-17 + item 3 | `test_implementation_start_gate_invalid_payload.py`: empty payload -> allow + `invalid-payload-fail-open` record present in denial log; malformed JSON -> same; parseable protected mutation without GO -> BLOCK, message names the resolved target (no `<unknown-mutating-target>` when resolvable) | fail-open-logged / BLOCK |
| item 4 remedies | `test_gate_message_remedies.py`: resolve_changed_by error text contains the verbatim envelope-open remedy; adr_dcl_clause_preflight exit-5 output contains per-clause `Evidence required:` hint on every output path | asserted |
| item 5 dedupe | extended settings-hook test: each of the five hook commands appears exactly once per event in `.claude/settings.json` | asserted |
| item 6 | `test_cursor_hooks_single_invocation.py`: the three gates appear only under `preToolUse` in `.cursor/hooks.json` | asserted |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | full replay matrix (below) executed in the post-impl report | matrix in report |

**ALLOW/BLOCK replay matrix** (executed post-implementation and included as
evidence in the report; the four documented false-positive commands come from
the denial register):

| # | Replay case | Pre-fix | Post-fix required |
| --- | --- | --- | --- |
| R1 | Write to harness scratchpad (`%LOCALAPPDATA%/Temp/claude/<proj>/<session>/scratchpad/...`) | BLOCK (610-class) | ALLOW |
| R2 | `.cursor`-path operation (sanctioned harness config surface) | BLOCK (121-class) | ALLOW |
| R3 | PowerShell command with backtick-escaped in-root path | BLOCK (69-class) | ALLOW |
| R4 | `gt.cmd` shim invocation from user-local bin | BLOCK (13-class) | ALLOW |
| R5 | Quoted string containing `|` in an in-root command | BLOCK | ALLOW |
| R6 | `.md` Write containing a p-flag (`-p`) with a following prose word, no secret value | BLOCK (16-class) | ALLOW |
| R7 | Empty PreToolUse payload to implementation-start gate | BLOCK (509-run class) | ALLOW + logged warning |
| T1 | Write/path under `E:\Claude-Playground` | BLOCK | BLOCK |
| T2 | Harness launch outside root | BLOCK | BLOCK |
| T3 | Direct hook-script execution | BLOCK | BLOCK |
| T4 | Real credential-shaped value in a bridge `.md` Write | BLOCK | BLOCK |
| T5 | Command-initial `git` lifecycle command without authorization | BLOCK | BLOCK |
| T6 | Parseable protected-target mutation without GO | BLOCK | BLOCK (names real target) |

Commands: `python -m pytest platform_tests/scripts/test_gate_fp_corpus.py
platform_tests/hooks/ -q` plus the targeted new modules; `ruff check` AND
`ruff format --check` on every changed Python file (both gates, run
separately).

## Acceptance Criteria

- [ ] All six change items implemented as specified, each with its regression
      test(s) green; decision item 7 resolved per the LO/owner selection.
- [ ] Replay matrix R1-R7 all ALLOW (R7 with logged warning record);
      T1-T6 all still BLOCK. Matrix included in the post-impl report.
- [ ] The four documented false-positive commands from the denial register
      replay as ALLOW.
- [ ] `ruff check` and `ruff format --check` both green on changed files.
- [ ] No unrelated hook edited; no dispatcher, bridge writer/publisher, or
      lifecycle-resolver file touched.
- [ ] Boundary non-weakening demonstrated: corpus BLOCK cases unchanged or
      strengthened; user-profile blanket block still present in source.

## Risk / Rollback

- **Riskiest single item — impl-start-gate fail-open on empty payload (item
  3).** Mitigations: (1) fail-open applies ONLY to the
  empty/unparseable-payload branch — an infrastructure fault class in which
  the gate has no tool intent to evaluate; every parseable payload keeps the
  identical fail-closed policy path; (2) every fail-open event appends a
  warning record to `.gtkb-state/gate-denials.jsonl`
  (`pattern_id=invalid-payload-fail-open`), so the denial-log evidence trail
  is preserved and the class remains measurable; (3) a regression test
  asserts both the allow AND the log record; (4) rollback is a single-commit
  revert of the `_read_payload`/`gate_decision` branch.
- **Exemption over-broadening (item 1).** The `.cursor`/scratchpad/`gt.cmd`
  exemptions are enumerated and narrow (parts-match mirroring the existing
  harness-directory exemption, normalized scratchpad prefix, exact-basename
  shim); the corpus BLOCK cases (T1-T3, T5) mechanically pin that Playground,
  out-of-root launches, and genuine git-lifecycle commands remain blocked.
  Rollback: revert the exemption commit; the classifier is stateless.
- **Regex precision changes (item 1).** Backtick exclusion and quote awareness
  could under-match a genuinely malicious path. Mitigation: corpus BLOCK cases
  retain genuine out-of-root paths in plain, quoted, and redirected forms; the
  declared fallback (command-initial `git` scoping) is strictly narrower than
  full quote parsing and is called out for LO scrutiny if used.
- **Dedupe regressions (items 5-6).** Removing duplicate registrations cannot
  remove coverage (the retained registration is byte-identical); the
  settings/cursor assertion tests pin single-registration state. Rollback:
  revert the JSON edits.
- **Stub retirement (item 7, if selected).** The stubs enforce nothing today
  (exit 0, no output), so retirement cannot reduce live enforcement; the
  tombstone preserves provenance. Rollback: restore files + registrations from
  git history.
- All changes are hook/config/parser-local and stateless; no data migration,
  no dispatcher state, no bridge-chain bytes. Full rollback = `git revert` of
  the implementation commit(s).

## Scope Guard / Non-Impairment

No dispatcher files, no bridge writer/publisher files, no
`bridge_lifecycle_resolver.py`, no `dispatcher_runtime.py`. Concurrent
threads on WI-5314 and WI-5827 touch none of this proposal's `target_paths`.
The `credential-scan.py` <-> canonical-catalog divergence is explicitly
deferred to a follow-on WI candidate.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5480; friction investigation register 2026-08-06 (F-046..F-055, F-110, F-122); gate-denial log 2026-07-01..2026-08-06 (7,347 records)",
  "canonical_authority": "GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001; GOV-17; project-root-boundary rule; DCL-CROSS-HARNESS-ENFORCEMENT-001 (gate-fp corpus vehicle)",
  "primary_route": "precision repairs to six gate surfaces: exemption-set + delimiter/segment regex fixes in enforcement/__init__.py, scanner-safe-writer md-prose scoping, implementation-start-gate invalid-payload fail-open-with-logged-record, remedy-bearing gate messages, settings.json dedupe, cursor single-invocation",
  "before_behavior": "610 harness-scratchpad, 121 .cursor, 69 backtick, 13 gt.cmd false denials; 16/16 scanner-safe-writer production denials false; empty-payload fail-closed with 509-identical-block worst run; 31.8% of all denials are byte-identical re-blocks",
  "after_behavior": "sanctioned scratchpad/tooling paths ALLOW while Playground, harness-launch, credential, and direct-hook-exec classes still BLOCK; invalid payloads produce logged invalid-payload-fail-open records instead of unbounded retry loops; every replay-matrix case regression-locked in gate-fp-corpus",
  "self_descriptive_naming": "no renames; existing gate and corpus names retained (gate-fp-corpus.toml gains new corpus rows named by denial class)",
  "obsolete_guidance_disposition": "no-op stubs spec-before-code.py and kb-not-markdown.py routed as an explicit LO/owner retire-or-restore decision item citing WI-4449 history; no guidance silently removed",
  "history_preservation": "denial evidence trail preserved: fail-open events append invalid-payload-fail-open records to .gtkb-state/gate-denials.jsonl; no log rewritten; append-only bridge protocol untouched",
  "baseline": {
    "denial_records_window": "7,347 (2026-07-01..2026-08-06)",
    "byte_identical_reblock_share": "31.8%",
    "false_positive_classes": {"scratchpad": 610, "cursor": 121, "backtick": 69, "gt_cmd": 13, "scanner_safe_writer": 16},
    "duplicate_hook_registrations": 5,
    "no_op_stub_hooks": 2
  },
  "expected_result": {
    "replay_matrix": "R1-R7 ALLOW/BLOCK outcomes per Specification-Derived Verification section, regression-locked in test_gate_fp_corpus.py",
    "false_positive_classes_post": "0 recurrences of the six named classes in gate-denials.jsonl during verification window",
    "true_positive_retention": "Playground write, out-of-root harness launch, credential-shaped write, direct hook-script exec all still BLOCK"
  },
  "rollback": "single revert of the implementing commit restores prior gate behavior; corpus rows are additive and revert with it; no data migration involved",
  "hard_invariants": "project-root boundary unchanged (E:\\GT-KB containment); C:\\Users\\ blanket block retained outside enumerated exemptions; two-layer credential defense retained (scanner-safe-writer + credential-scan); fail-closed retained for parseable protected mutations without GO",
  "fail_closed_conditions": "implementation-start gate still fails closed on every parseable protected mutation lacking a valid packet; only the unparseable/empty-payload branch converts to logged fail-open; directive gate still blocks command-initial git and out-of-root paths",
  "essential_context_preservation": "every fail-open event is logged with payload snapshot to gate-denials.jsonl so the audit trail loses no information relative to the fail-closed behavior it replaces"
}
```

## Cross-Harness Disposition

Per-harness parity declaration (per `ADR-CROSS-HARNESS-PARITY-001` Q8 /
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`):

- **claude (B)**: primary surface. enforcement/__init__.py fixes apply to the shared
  library consumed by the Claude adapter; settings.json dedupe is Claude-side only
  (duplicates exist only there). Behavioral parity: shared-library changes flow to
  every adapter equally.
- **codex (A)**: consumes the same `groundtruth_kb.enforcement` library through
  `.codex/gtkb-hooks/` adapters — inherits the exemption/regex fixes with no
  Codex-side edit. `codex-directive-enforcement` denial behavior otherwise unchanged.
- **cursor (E)**: `.cursor/hooks.json` single-invocation fix is cursor-specific by
  design (the double registration exists only there); the shared-library fixes flow
  through `scripts/cursor_hook_adapter.py` unchanged.
- **goose (G) / ollama (D) / openrouter (F) / antigravity (C) / alibaba (H)**: no
  harness-local hook copies of the touched surfaces; these harnesses interact with
  the gates only via shared scripts (implementation_start_gate.py,
  adr_dcl_clause_preflight.py, _kb_attribution.py), which change uniformly.
- No owner-approved typed waiver requested: full behavioral parity via the shared
  library is the mechanism; harness-local edits are confined to surfaces that exist
  only on that harness (settings.json dedupe, cursor double-invocation).

## Pre-Filing Preflight Evidence (self-check)

Run 2026-08-06 against this draft via `--content-file`
(`.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight
Subsection):

- `scripts/bridge_applicability_preflight.py`: `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`; packet_hash
  `sha256:be826bbc74e968dbf7c3d690a9d3abc5cd68d358d13745da901b6791b2c31f67`
  (computed on the pre-record draft; the filing session re-runs the preflight
  at file time and LO re-runs it at review time). Project-authorization
  operation-time evaluation: `allowed: true` for
  `implementation_packet_create` and `implementation_start` across the full
  declared cohort under the cited PAUTH (v2, active, unexpired).
- `scripts/adr_dcl_clause_preflight.py`: exit 0; 4 `must_apply` clauses, all
  with satisfying evidence; 0 blocking gaps.

## Recommended Commit Type

fix — repairs incorrect gate behavior (false-positive classification,
duplicate invocation, misleading denial messages); no new capability surface.

---

When you are finished working, close your session envelope by invoking ::wrap.
