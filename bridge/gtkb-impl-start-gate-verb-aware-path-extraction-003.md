REVISED

# Impl-Auth and Impl-Start-Gate Parser Hygiene — REVISED-3 addressing Codex NO-GO -002 F1/F2/F3 + R2 scope expansion (extract_spec_links table-format)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-verb-aware-path-extraction
Version: 003
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE
Work Item: WI-4355
Secondary Work Item: WI-4368
Related Work Item: WI-3358

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: cf272bb0-aac6-48dd-94ce-3653a82e93f7
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session; REVISED-3 addresses Codex NO-GO -002 (F1 bridge_kind + missing PAUTH/WI metadata; F2 missing packet evidence; F3 WI-4355 reconciliation) AND expands scope per DECISION-1090 + cf272bb0 session AUQs

## target_paths

- `groundtruth.db`
- `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.json`
- `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001.json`
- `scripts/implementation_start_gate.py`
- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate_verb_aware.py`
- `platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py`

requires_verification: true
implementation_scope: implementation

## What changed in REVISED-3 vs -001 / -002

This revision addresses all three findings in Codex NO-GO `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-002.md` AND folds in the R2 scope expansion authorized by cf272bb0 session AUQ at 2026-06-05 ~06:31 UTC ("Expand existing -001 via REVISED-2") and 2026-06-05 ~06:43 UTC ("Mint new PAUTH covering WI-4355 + new R2 WI").

**F1 fix (bridge_kind + PAUTH/WI metadata).** -001 declared `bridge_kind: governance_review` (metadata-exempt) but requested source/test/DB/formal-artifact mutations. REVISED-3 declares `bridge_kind: implementation_proposal` and `implementation_scope: implementation`. The `Project Authorization:` / `Project:` / `Work Item:` / `Secondary Work Item:` / `Related Work Item:` metadata lines are added at file top to bind this proposal to the just-minted PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE (DELIB-20260882 owner-decision provenance).

**F2 fix (formal-artifact-approval packet evidence).** -001 promised packets but the packet path did not exist on disk. REVISED-3 includes the exact DCL body text for BOTH `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` and the new `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` inline in §Summary > Governance below; the packet JSON files at the target_paths are to be authored as the first step of Phase 1 implementation (pre-MemBase-insert) with owner approval recorded via AUQ. The packet WILL exist on disk at GO time per §Phased Implementation Plan Phase 1.

**F3 fix (backlog reconciliation).** -001 cited `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` and did not reconcile against the related `WI-4355` (Implementation-start gate path extraction and classification...) or `WI-3358` (gate misclassifies mutating-command keywords inside quoted command arguments). REVISED-3 corrects the project to `PROJECT-GTKB-RELIABILITY-FIXES` (where WI-4355 + WI-3358 actually live), cites WI-4355 as primary `Work Item:`, WI-4368 (newly minted for R2-S1) as `Secondary Work Item:`, and WI-3358 as `Related Work Item:`. WI-3358 is included in the new PAUTH for forward flexibility (a future REVISED-N can fold the quoting-aware fix in without re-minting authorization).

**R2 scope expansion (extract_spec_links table-format).** During interactive Prime Builder session `cf272bb0-aac6-48dd-94ce-3653a82e93f7` at 2026-06-05 05:43-06:26Z, implementation of `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-003.md` (Codex GO'd at -004) was blocked at impl-auth-begin time with error `"Approved proposal has no concrete specification links"`. Root cause: `extract_spec_links` (`scripts/implementation_authorization.py:457-477`) iterates section body lines and skips anything not starting with `-` or `*`. Proposal -003 §Specification Links uses `| Spec | Severity | Trigger | How... |` markdown-table format (lines 116-138). Parser returns empty list, raises `AuthorizationError`. Memory evidence: `memory/project_2026_06_05_sot_slice2a_impl_blocked_extract_spec_links_table_format.md`. REVISED-3 folds the extract_spec_links table-format recognition fix into this bridge per cf272bb0 AUQ direction; both fixes share the same module class (`scripts/implementation_*.py`) and the same parser-hygiene theme (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`).

**Missing-advisory fix.** -001 did not cite `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory; flagged by Codex applicability preflight). REVISED-3 adds it to §Specification Links.

All other technical scope from -001 carries forward; the false-positive cases enumerated in -001 §Why this proposal (heredoc commit messages mentioning paths, grep patterns containing protected tokens, etc.) remain the verb-aware fix's primary acceptance fixtures.

## Why this proposal

Two adjacent parser-hygiene gaps in the same module class block legitimate implementation work:

**Surface 1 — `_paths_from_shell` false-positives in `implementation_start_gate.py:196-207`.** During the 2026-06-05 aa899d25 session, the impl-start-gate fired as false-positive on multiple legitimate Bash commands because `_paths_from_shell` runs `PATH_TOKEN_RE` against the entire command string. Any command that *mentions* a protected path token — heredoc commit messages, grep patterns, pipeline stages whose output contains paths — triggers the gate's mutation check even when the command verb is read-only. Root cause: path-extraction is not verb-aware; the mutation signal check (`_has_mutating_signal`) and path detection are decoupled. Concrete false-positives this session: heredoc commit messages citing the path being discussed, `grep -E "^(scripts/|...)"` patterns, `cat | tr | xargs git restore`-pipeline path conflation. Estimated ~70% of gate fires in the work-tree-cleanup session were false-positives of this class.

**Surface 2 — `extract_spec_links` table-format gap in `implementation_authorization.py:457-477`.** During the 2026-06-05 cf272bb0 session, implementation of a Codex-GO'd Slice 2A proposal was hard-blocked at `impl_auth begin` because `extract_spec_links` only parses bullet-format spec-link sections; the proposal used markdown-table format. The parser returned empty list and raised `AuthorizationError`. The asymmetry is striking: `extract_target_paths` (in the same module) was fixed in REVISED-2 of the SoT slice to handle both formats, but `extract_spec_links` retained the bullet-only behavior. The result: even after Codex GO of a structurally-correct proposal, downstream implementation is impossible until the parser is extended. The fix is additive: bullet-loop behavior preserved unchanged; table-row recognition fallback after the bullet loop returns zero.

Both surfaces are instances of the same defect class: parsers in canonical infrastructure code that recognize only a narrow subset of the formats their inputs may legitimately use, causing legitimate work to be hard-blocked with cryptic error messages. The deterministic-services principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`) explicitly targets this class: the cost of recognizing one more format belongs in the service, not per-session in AI-author memory.

**Expected impact (combined).** Eliminates the ~70% verb-aware false-positive rate AND unblocks impl-auth packet creation for table-format proposals. Both fixes are narrowing (verb-aware) or additive (table-format) — never broader than current behavior, never weakening any guard.

## Summary

Two governance DCLs + two source file refactors + two test files. Both target the parser-hygiene theme. Bullets used throughout §Specification Links below (so this REVISED-3 itself is impl-auth-parseable).

**Governance (2 formal-artifact-approval packets to be authored at Phase 1; exact DCL bodies inline):**

### DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001 v1 (NEW)

**Type**: design_constraint
**Status**: specified
**Authority**: `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (path-extraction precision preserves the no-bridge-bypass invariant)

**Constraint body**:

`_paths_from_shell(root: Path, command: str) -> list[str]` in `scripts/implementation_start_gate.py` MUST tokenize the command via `shlex.split(command, posix=False)` and identify the shell verb (first non-env-prefix token) BEFORE extracting protected-path arguments. Path extraction MUST be verb-aware: for each verb in `MUTATING_VERB_TABLE` (a new module-level constant), only the argument positions semantically meaningful to that verb are scanned for paths.

The `MUTATING_VERB_TABLE` enumerates:

- `git rm` → args 2+ are paths
- `git restore --staged` → args 3+ are paths
- `git add` → args 2+ are paths (excluding `-A`, `--all`, `-u`, `--update`, `-p`, `--patch` flags)
- `git mv` → args 2+ are paths
- `git checkout` → args 2+ when not branch-switching (heuristic: presence of `--` separator or path-shaped tokens)
- `git commit` → no positional path args (`-m` message body is NOT a path)
- `git reset` → args 2+ when `--hard`/`--mixed`/`--soft` not in scope-changing mode
- `git merge` / `git rebase` / `git tag` / `git push` → no positional path args
- `set-content <path>` / `Set-Content -Path <path>` → path arg
- `out-file <path>` / `Out-File -FilePath <path>` → path arg
- `new-item <path>` / `New-Item -Path <path>` → path arg
- `remove-item <path>` / `Remove-Item -Path <path>` → path arg
- `move-item <src> <dst>` / `Move-Item -Path <src> -Destination <dst>` → both paths
- `copy-item <src> <dst>` / `Copy-Item -Path <src> -Destination <dst>` → both paths
- `apply_patch` → paths extracted via `_paths_from_apply_patch` (existing logic preserved)

For pipelines (separators `|`, `&&`, `||`, `;`), each stage is tokenized independently and per-verb extraction applies to that stage's verb only. For commands NOT matching any verb in `MUTATING_VERB_TABLE`, `_paths_from_shell` returns an empty list (the existing `_is_safe_command` check determines if the command may proceed; the `<unknown-mutating-target>` fallback applies only when `_has_mutating_signal` reports True AND no path was extracted).

**Acceptance assertions**:

- `_paths_from_shell("git commit -m \"$(cat <<'EOF' ...scripts/foo.py... EOF)\"", root)` returns `[]` (commit-body path mentions are NOT extracted as targets).
- `_paths_from_shell("grep -E '^scripts/' tmp.txt", root)` returns `[]` (grep is read-only; pattern-string contents NOT extracted).
- `_paths_from_shell("git restore --staged unrelated/path", root)` returns `["unrelated/path"]` (path extracted; if unrelated/path is NOT protected, gate does not fire).
- `_paths_from_shell("git add scripts/protected.py", root)` returns `["scripts/protected.py"]` (path extracted; gate fires).

**Rejected alternatives**:

- AST-level shell parsing (too brittle; cross-shell incompatibility; deferred).
- Per-command pre-flagging via inline magic comments (places burden on authors; deferred).

### DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001 v1 (NEW)

**Type**: design_constraint
**Status**: specified
**Authority**: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (the parser implements consumption of the linkage section this DCL mandates)

**Constraint body**:

`extract_spec_links(markdown: str) -> list[str]` in `scripts/implementation_authorization.py` MUST recognize spec-link citations in BOTH bullet format (existing behavior at lines 457-477; `-` or `*` line prefix) AND markdown-table format (NEW behavior; pipe-delimited rows where the first non-header cell contains a backtick-quoted token matching `_SPEC_ID_RE`).

Bullet-format recognition is the primary branch; table-format recognition is an additive fallback triggered only when the bullet branch returns zero links. Header rows (first row of a table block) and separator rows (`|---|---|...`) are filtered. Per-row placeholder checking (`PLACEHOLDER_RE`) applies identically to both branches: a row with no concrete citation that matches `PLACEHOLDER_RE` raises `AuthorizationError`.

**Acceptance assertions**:

- `extract_spec_links(BULLET_ONLY_PROPOSAL)` returns the spec IDs from the bullet branch unchanged (regression).
- `extract_spec_links(TABLE_ONLY_PROPOSAL)` returns the spec IDs from the first non-header cell of each data row.
- `extract_spec_links(MIXED_BULLET_AND_TABLE_PROPOSAL)` returns bullet results only (bullet branch precedence; table fallback dormant).
- `extract_spec_links(EMPTY_TABLE_PROPOSAL)` raises `AuthorizationError("Approved proposal has no concrete specification links")`.
- `extract_spec_links(TABLE_WITH_HEADER_AND_SEPARATOR)` correctly filters header + separator rows.
- `extract_spec_links(TABLE_ROW_WITH_PLACEHOLDER_TEXT)` raises `AuthorizationError` per `PLACEHOLDER_RE`.
- `extract_spec_links(SLICE_2A_PROPOSAL_003_CONTENT)` returns the expected ~21 spec-ID tokens from the real Slice 2A -003 §Specification Links section.

**Rejected alternatives**:

- Replace bullet branch entirely with table branch (regression risk; existing bullet-format proposals would break).
- Refactor body parser to a unified format-detector (scope creep; out of slice).

**Operational (TWO source file refactors + TWO new test files):**

- **`scripts/implementation_start_gate.py`** (modified) — refactor `_paths_from_shell` per `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001`. Add `MUTATING_VERB_TABLE` constant. Preserve all existing behavior for verbs already in the table (no regression).
- **`scripts/implementation_authorization.py`** (modified) — extend `extract_spec_links` per `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001`. Additive change after bullet loop fall-through.
- **`platform_tests/scripts/test_implementation_start_gate_verb_aware.py`** (new) — false-positive + sanity fixtures per DCL-1 acceptance assertions.
- **`platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py`** (new) — table-format spec-link recognition fixtures per DCL-2 acceptance assertions, including self-verification against Slice 2A -003 content.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking — Filed via `bridge/INDEX.md` as REVISED-3 versioned bridge file; REVISED status inserted at top of -001/-002 version chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking — This section. Bullet format used intentionally (eat dogfood for what the parser currently handles; the table-format extension authorized by this proposal is additive, never replacing bullets).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking — §Specification-Derived Verification Plan maps each new DCL to test coverage; both new test files exercise DCL acceptance assertions via concrete fixtures.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — blocking — Both parser changes PRESERVE the no-bridge-bypass invariant. Verb-aware path extraction narrows the path-extraction surface (fail-safer). Table-format recognition grows the format-recognition surface without weakening any guard check; real mutations to protected paths still require impl-auth packets regardless of which spec-link format the proposal uses.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — blocking — `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE` (active; DELIB-20260882 owner-decision provenance) covers WI-4355 + WI-4368 + WI-3358 with allowed mutation classes `source` / `test_addition` / `membase_spec_insert` / `governance_evidence`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — advisory — PAUTH cites DELIB-20260882 (mint AUQ) as owner-decision authority; envelope is bounded per the scope summary.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — blocking — PAUTH cites 2 framing specs (DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 + PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001); this proposal adds the 2 new DCLs as outputs.
- `GOV-STANDING-BACKLOG-001` — blocking — WI-4355 (primary) + WI-4368 (R2-S1, just minted; rowid 6209 / TEST-11139) + WI-3358 (related) all in PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-12` — blocking — WI-4368 created via `gt backlog add-work-item` with linked test TEST-11139 ("extract_spec_links extracts spec IDs from markdown-table-format Specification Links section"); WI-4355's linked test inherits from its prior creation.
- `GOV-ARTIFACT-APPROVAL-001` — blocking — 2 formal-artifact-approval packets enumerated in target_paths; per-packet owner approval per `DCL-ARTIFACT-APPROVAL-HOOK-001` will be recorded as separate AUQ events during Phase 1 of implementation (packet contents are inline above for Codex review).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking — All paths within `E:\GT-KB`; no out-of-root targets.
- `.claude/rules/project-root-boundary.md` — blocking — All target_paths under `E:\GT-KB`; no exceptions.
- `.claude/rules/bridge-essential.md` — advisory — Bridge protocol integrity preserved; gate change does not affect bridge protocol itself, only the gate's path-extraction precision and the auth-packet builder's spec-link extraction.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — Two new DCLs capture the parser contracts as durable artifacts; PAUTH + WI + DELIB provenance chain is captured.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — (added per Codex -002 finding 5; missing advisory citation flagged by applicability preflight) — Two new DCLs are concrete instances of artifact-oriented development of the parser-hygiene contract.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — Both new DCLs progress through specified → implemented → verified per standard lifecycle.
- `DCL-CONCEPT-ON-CONTACT-001` — advisory — "Verb-aware path extraction", `MUTATING_VERB_TABLE`, "table-format spec-link recognition", "per-row placeholder check parity" are first-contact concepts; glossary updates can follow in a sibling proposal.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — advisory — Both parser fixes operationalize the deterministic-service principle: recurring per-session format friction belongs in the service, not in AI-author memory. R2-E1 (Slice 2A impl block) is a concrete recent instance.

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence chain:

- For verb-aware path extraction (Surface 1): aa899d25 session AskUserQuestion response "P1: Verb-aware path extraction in impl-start-gate (Recommended)" 2026-06-05 UTC + "How can we prevent work-tree noise" prompt analysis (6 prevention mechanisms identified; this is P1).
- For extract_spec_links table-format (Surface 2 / R2): DECISION-1090 owner direction 2026-06-05 ~06:30 UTC "file gtkb-impl-start-gate-verb-aware-path-extraction-001 as a separate parser-fix bridge (Path A, recommended)" + cf272bb0 session AskUserQuestion response 2026-06-05 ~06:31 UTC "Expand existing -001 via REVISED-2".
- For PAUTH mint: cf272bb0 session AskUserQuestion response 2026-06-05 ~06:43 UTC "Approve as proposed" → DELIB-20260882 recorded → PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE minted 2026-06-05 06:53:28Z.

Per-spec formal-artifact-approval packets require additional per-packet owner approval at Phase 1 implementation start per `GOV-ARTIFACT-APPROVAL-001` (recorded as separate AUQ events; packet contents are inline above for Codex review at this stage).

## Prior Deliberations

- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-001.md` (NEW) — Original proposal authored by aa899d25; addressed verb-aware Surface 1 only.
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-002.md` (NO-GO) — Codex review of -001; findings F1 (bridge_kind + PAUTH/WI metadata), F2 (missing packet evidence), F3 (WI-4355 reconciliation), and missing ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 citation. This REVISED-3 addresses all four.
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-003.md` (REVISED-2 GO'd at -004) — The R2-E1 evidence proposal whose impl was blocked by `extract_spec_links` table-format gap; motivates the new Surface 2 scope.
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-004.md` (GO) — Codex GO with Opportunity Radar flagging deterministic-service parser-validation opportunity (foreshadowed this gap class).
- `bridge/gtkb-workspace-orphan-cleanup-2026-06-05-001.md` (NEW) — Sibling chore-bridge that mitigated the *result* of false-positives (orphan accumulation); this proposal addresses the *cause* on both parser surfaces.
- aa899d25 session's commit log: `9558122e`, `3c5578f4`, `72234a90`, `01356cb2` — context for the prevention-mechanism analysis.
- `DELIB-20260882` — Owner AUQ 2026-06-05 06:43Z approving PAUTH mint; recorded via `gt deliberations record`; bound to WI-4368 + session cf272bb0.
- DECISION-1087 (memory/pending-owner-decisions.md) — Parallel session's AUQ for `--no-verify` bypass; demonstrates the cost of false-positives motivating Surface 1.
- DECISION-1090 (memory/pending-owner-decisions.md, resolved 2026-06-05 ~06:30 UTC) — Owner direction selecting Path A: file parser-fix bridge.
- `memory/project_2026_06_05_sot_slice2a_impl_blocked_extract_spec_links_table_format.md` — Concrete session-level evidence of Surface 2 blocker.
- aa899d25 session's "How can we prevent work-tree noise" analysis — derived the 6 prevention mechanisms; this is P1 (verb-aware) + R2 (table-format).
- `WI-4355` (current_work_items, P3, project PROJECT-GTKB-RELIABILITY-FIXES) — Pre-existing work-item for verb-aware path extraction; this proposal is the implementation path.
- `WI-4368` (current_work_items, P2, project PROJECT-GTKB-RELIABILITY-FIXES) — Newly created for R2-S1 extract_spec_links table-format; linked test TEST-11139.
- `WI-3358` (current_work_items, P3, project GTKB-RELIABILITY-FIXES) — Related quoting-aware fix; included in the new PAUTH for forward flexibility but NOT addressed in this REVISED-3 source scope (a future REVISED-N may fold it in).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Owner directive operationalizing the deterministic-services bias; both parser fixes are concrete instances.
- `.claude/rules/bridge-essential.md` § "Re-Enabling Pollers" — Pattern precedent for "narrow the protection surface without weakening it"; both parser fixes follow this conservative principle.

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

Owner-decision evidence authorizing this proposal:

- aa899d25 session AskUserQuestion "P1: Verb-aware path extraction in impl-start-gate (Recommended)" at 2026-06-05 UTC → Authorizes Surface 1 (verb-aware) scope.
- aa899d25 session prompt "How can we prevent work-tree noise in the future?" → Establishes the prevention-mechanism design space.
- DECISION-1090 owner directive 2026-06-05 ~06:30 UTC "file gtkb-impl-start-gate-verb-aware-path-extraction-001 as a separate parser-fix bridge (Path A, recommended)" → Authorizes filing this bridge for cf272bb0 session's parser-fix blocker.
- cf272bb0 session AskUserQuestion 2026-06-05 ~06:31 UTC "Expand existing -001 via REVISED-2" → Authorizes folding R2-S1 (extract_spec_links table-format) into this bridge rather than filing a sibling.
- cf272bb0 session AskUserQuestion 2026-06-05 ~06:43 UTC "Approve as proposed" (PAUTH mint) → DELIB-20260882 → PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE minted.

Per-spec formal-artifact-approval packets at execution time require per-packet owner approval per `GOV-ARTIFACT-APPROVAL-001`:

- `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` packet at `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.json` — exact DCL body inline in §Summary > Governance above; AUQ at Phase 1 start.
- `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` packet at `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001.json` — exact DCL body inline in §Summary > Governance above; AUQ at Phase 1 start.

## Acceptance Criteria

1. **DCL-1 landed:** `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` v1 in MemBase via formal-artifact-approval packet with owner approval.
2. **DCL-2 landed:** `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` v1 in MemBase via formal-artifact-approval packet with owner approval.
3. **Source refactor 1:** `scripts/implementation_start_gate.py` updated with `MUTATING_VERB_TABLE` constant and verb-aware `_paths_from_shell` per DCL-1.
4. **Source refactor 2:** `scripts/implementation_authorization.py:extract_spec_links` extended with table-row fallback per DCL-2.
5. **Test coverage 1:** `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` covers all DCL-1 acceptance assertions + sanity cases for non-regression.
6. **Test coverage 2:** `platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py` covers all DCL-2 acceptance assertions + bullet-only regression + self-verification on Slice 2A -003 content.
7. **All tests pass:** `pytest platform_tests/scripts/test_implementation_start_gate_verb_aware.py platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py` GREEN; existing impl-start-gate and impl-auth test suites remain GREEN (no regressions).
8. **Ruff clean:** `ruff check scripts/implementation_start_gate.py scripts/implementation_authorization.py platform_tests/scripts/test_implementation_start_gate_verb_aware.py platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py` + `ruff format --check` GREEN.
9. **No regression in protected-path enforcement:** sanity tests (git add of protected path, git rm of protected path, commit with staged protected files) remain blocked.
10. **No project-root-boundary violation:** all target_paths within `E:\GT-KB`.
11. **Self-verification 1 (verb-aware):** the commands that false-positive-fired in aa899d25 session (heredoc commit messages mentioning paths, `grep -E "scripts/|..."` patterns, `git restore --staged` with non-protected paths) execute without blocking after refactor.
12. **Self-verification 2 (table-format):** after refactor, `python scripts/implementation_authorization.py begin --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline` succeeds (`authorized: true`) — directly unblocking Slice 2A.

## Phased Implementation Plan

**Phase 1 — DCL spec governance landing (2 formal-artifact-approval packets):**

1. Generate packet for `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` v1 with the exact DCL body from §Summary > Governance. Owner approval AUQ fires.
2. Generate packet for `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` v1 with the exact DCL body from §Summary > Governance. Owner approval AUQ fires.
3. Insert both via `KnowledgeDB.insert_spec` per packet evidence; changed_by attribution per harness identity.

**Phase 2 — Source refactor 1 (impl-start-gate verb-aware):**

4. Add `MUTATING_VERB_TABLE` constant to `scripts/implementation_start_gate.py` with per-verb extractor lambdas.
5. Refactor `_paths_from_shell` to tokenize via `shlex.split(posix=False)` → split on pipeline separators → per-stage verb lookup → per-verb extraction.
6. Preserve `_is_safe_command`, `_has_mutating_signal`, `_is_mutating_command` behavior unchanged.

**Phase 3 — Source refactor 2 (impl-auth extract_spec_links table-format):**

7. Locate `extract_spec_links` at `scripts/implementation_authorization.py:457-477`.
8. After the existing bullet-loop, add a fallback branch: if `links` is still empty, scan `body.splitlines()` for pipe-delimited rows.
9. Implement header/separator filtering via separator-row-successor detection.
10. For each data row, extract the first non-empty cell, take backtick-quoted tokens; apply per-row placeholder check; append to `links`.

**Phase 4 — Test coverage:**

11. Write `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` with all DCL-1 acceptance fixtures + non-regression sanity fixtures.
12. Write `platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py` with all DCL-2 acceptance fixtures + bullet-only regression + Slice 2A -003 self-verification.
13. Run `pytest <both files> -v` + `ruff check` + `ruff format --check`. Verify GREEN before Phase 5.

**Phase 5 — Implementation report:**

14. File `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-004.md` as NEW post-impl report with:
    - spec-to-test mapping (both DCLs to both test files);
    - observed test results (PASS/FAIL counts);
    - self-verification smoke evidence for BOTH surfaces (verb-aware false-positive replay + impl-auth begin success on Slice 2A -003);
    - applicability+clause preflights;
    - recommended commit type per `gtkb-governance-hygiene-bundle-001` Change B (likely `feat:` since two new DCLs + new behavior).

## Specification-Derived Verification Plan

- `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` v1 — verified by `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` covering all 4 acceptance assertions in the DCL body + edge cases + non-regression sanity fixtures.
- `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` v1 — verified by `platform_tests/scripts/test_implementation_authorization_extract_spec_links_table.py` covering all 7 acceptance assertions in the DCL body including self-verification on `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-003.md`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (no-bypass preservation) — verified by sanity-subset fixtures in both test files: git add/rm/commit of protected paths without impl-auth remain blocked; new spec inserts require packet + PAUTH; no bypass surface is created.
- Existing impl-start-gate and impl-auth test suites (regression) — run in full; no failures permitted.

## Risk and Rollback

**Risk 1 — Verb table incompleteness.** A verb not in `MUTATING_VERB_TABLE` could mutate protected paths without triggering the gate. Mitigation: table starts with the same verb set as the current `MUTATING_COMMAND_RE` regex (no regression). Unknown verbs default to empty path extraction; combined with `_has_mutating_signal` check, preserves fail-closed behavior via `<unknown-mutating-target>` fallback. Adding new verbs to the table is a future incremental safe change.

**Risk 2 — Argument-position extractor edge cases.** Complex shell constructs could confuse per-verb extractors. Mitigation: tests cover main edge cases; tokenization failure (`shlex.split` ValueError) falls back to `<unknown-mutating-target>`; per-verb extractors use simple positional slicing.

**Risk 3 — Cross-shell incompatibility.** PowerShell vs POSIX bash syntax differences. Mitigation: `MUTATING_VERB_TABLE` enumerates both shells' verbs; `shlex.split(posix=False)` handles PowerShell-style quoting acceptably.

**Risk 4 — Table-format heuristic mis-recognizes prose pipes.** Inline `|` characters in prose body could be misread as table rows. Mitigation: the fallback branch only triggers when bullet loop returns zero links AND at least one row has a separator-row successor matching `|----|`. The check is conservative; it skips ambiguous prose-pipe usage rather than misclassifying it.

**Risk 5 — Placeholder check parity drift between bullet and table branches.** Mitigation: both branches use the same `PLACEHOLDER_RE` check applied to full row/line text; test fixture explicitly verifies parity.

**Rollback:** Per-phase reversibility:

- Phase 1: DCL inserts are append-only versioned — withdraw via `withdrawn` status.
- Phases 2-3: source refactors are file-level reversible via git revert. Both refactors are additive (new constant + new branch logic).
- Phase 4: test additions are file-level reversible.

If Codex NO-GO this REVISED-3: no source mutations occur (none happened in -001 or -002 either); rollback is trivial (this bridge file alone is superseded by REVISED-N+1).

## Pre-Filing Preflight Subsection

Both mandatory preflights to be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-verb-aware-path-extraction
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-verb-aware-path-extraction
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green (no blocking gaps); `missing_advisory_specs` either `[]` or only specs not yet triggered by content (the previously-flagged `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is now cited).

This proposal cites every spec triggered by its paths and content per `config/governance/spec-applicability.toml`. Touches two source files in `scripts/` and two test files in `platform_tests/` — all PROTECTED prefixes; impl-auth packet required at Phase 2 and Phase 3 implementation-start time per the just-minted PAUTH. The §Specification Links section uses BULLET format so this proposal itself is impl-auth-parseable; the table-format support added by this proposal is additive (recognized AS WELL AS bullets).

## Verification note (parser-recognition self-check)

After Codex GO, Prime can confirm bullet-format spec-links extraction succeeds on this file:

```text
python -c "from scripts.implementation_authorization import extract_spec_links; import pathlib; print(extract_spec_links(pathlib.Path('bridge/gtkb-impl-start-gate-verb-aware-path-extraction-003.md').read_text(encoding='utf-8')))"
```

Expected: a Python list containing each backtick-cited spec/DCL/ADR/GOV/PB/DELIB/WI token from this §Specification Links section (~17 tokens), no `AuthorizationError`. Post-Phase-3, the same probe against Slice 2A -003 should ALSO succeed.

---

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
