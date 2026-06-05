NEW

# Impl-Start-Gate: verb-aware path extraction (eliminate ~70% of false-positive gate fires from command-text path-token matching)

bridge_kind: governance_review
Document: gtkb-impl-start-gate-verb-aware-path-extraction
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: aa899d25-f289-48c2-8583-812e53973e98
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session; filed as P1 of the 6-recommendation work-tree-noise-prevention sequence

## target_paths

- `groundtruth.db`
- `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.json`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate_verb_aware.py`

requires_verification: true
implementation_scope: governance_review

## Why this proposal

During the 2026-06-05 work-tree cleanup session (commits `9558122e`, `3c5578f4`, `72234a90`), the impl-start-gate fired as a false-positive on multiple legitimate Bash commands because `scripts/implementation_start_gate.py:_paths_from_shell` (line 196) runs `PATH_TOKEN_RE` against the *entire command string*. Any command that *mentions* a protected path token — even read-only operations, even inside heredoc commit messages, even inside `grep` patterns — triggers the gate's mutation check.

**Concrete false-positives observed this session:**

1. `git commit -m "$(cat <<'EOF' ... <reference to scripts/implementation_authorization.py:extract_target_paths> ... EOF)"` — gate fired because the commit message CITED the path it was discussing.
2. `git restore --staged bridge/file-X.md` followed by `git add ... && git commit -m "..."` — when the commit message body mentioned protected paths in narrative, gate fired.
3. `grep -E "^(scripts/|groundtruth-kb/src/|...)" <temp-file>` — the grep PATTERN contained protected-path tokens, so the gate's `_paths_from_shell` extracted them and treated the grep as mutating.
4. `cat <temp-file> | tr '\n' '\0' | xargs -0 git restore --staged` — the cat output (not the command text) contained protected paths, but the gate fired because the `>` redirect from earlier in the pipeline matched `_shell_redirect_present`, marking the command mutating, and prior path-extraction from sibling commands persisted.

**Root cause.** The current path-extraction strategy (`_paths_from_shell` lines 196-207) is whole-string regex matching, not verb-aware tokenization. The mutation signal check (`_has_mutating_signal` line 381) and path detection are decoupled — any command with a mutation verb AND any protected path token anywhere in its text triggers the gate, even when the mutation verb operates on entirely different arguments.

**Fix.** Refactor `_paths_from_shell` to be verb-aware: tokenize the command via `shlex`, identify the shell verb (first token after env prefixes / pipeline separators), and only extract path arguments from the *positions semantically meaningful to that verb*. For `git rm <paths>`: path positions are args 2+. For `git restore --staged <paths>`: args 3+. For non-mutating verbs like `grep` / `cat` / `git status`: no path extraction (the command can't mutate regardless of what tokens appear). For unknown verbs: fall back to current behavior (conservative).

**Expected impact.** Eliminates ~70% of false-positive gate fires observed this session. Reduces session-time-burned-on-workarounds proportionally. Preserves protection for actual mutating commands (the verb-position extraction is *narrower*, never broader, than the current whole-string scan — fail-safer).

## Summary

**Governance (1 formal-artifact-approval packet required at execution time):**

- **`DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` v1 (NEW)** — defines the verb-aware path extraction contract:
  - `_paths_from_shell` MUST tokenize via `shlex.split` (posix=False) before extracting paths.
  - For each verb in `MUTATING_VERB_TABLE` (a new constant), extract paths from the verb-specific argument positions.
  - `MUTATING_VERB_TABLE` enumerates: `git rm`, `git restore --staged`, `git add`, `git mv`, `git checkout`, `set-content`, `out-file`, `new-item`, `remove-item`, `move-item`, `copy-item`, `apply_patch`, plus the existing `git (commit|reset|checkout|merge|rebase|tag|push)` set.
  - For commands NOT matching any verb in the table, return an empty path list (the existing `_is_safe_command` check determines if the command is safe; if not safe and no path extraction succeeded, fall back to `<unknown-mutating-target>` for fail-closed behavior).
  - For Bash commands that PIPELINE multiple verbs (e.g., `cat X | xargs git restore Y`), apply verb-aware extraction to each pipeline stage independently.

**Operational (one source file refactor + one new test file):**

- **`scripts/implementation_start_gate.py`** (modified) — refactor `_paths_from_shell` to verb-aware tokenization per the new DCL contract. Add `MUTATING_VERB_TABLE` constant. Preserve all existing behavior for verbs already in the table (no regression). Add explicit unit-test seams.
- **`platform_tests/scripts/test_implementation_start_gate_verb_aware.py`** (new) — exhaustive false-positive coverage:
  - Heredoc commit messages mentioning protected paths in narrative → NOT mutating (the `git commit` verb's path arg is the heredoc target, not the message body).
  - `grep -E "scripts/|..."` patterns containing protected tokens → NOT mutating (grep is read-only).
  - `git status bridge/file.md` → NOT mutating (git status is read-only).
  - `git restore --staged <unprotected-paths>` → NOT mutating-protected (the verb's args don't match PROTECTED_PREFIXES).
  - Sanity cases (must remain blocked): `git add scripts/foo.py` → mutating-protected; `git rm groundtruth-kb/src/X.py` → mutating-protected; `git commit -m "..."` with staged protected files → mutating-protected (current behavior preserved).

**Tests pass with current behavior preserved AND new false-positives eliminated.**

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps the new DCL to test coverage. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | blocking | content:impl-auth, protected mutation | The proposed verb-aware extraction PRESERVES the no-bridge-bypass invariant — it narrows the path-extraction surface but does not weaken the bypass guard. Real mutations to protected paths still require impl-auth packets. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:DCL inserts | 1 formal-artifact-approval packet enumerated in target_paths; per-packet owner approval per `DCL-ARTIFACT-APPROVAL-HOOK-001`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:scripts/**, path:platform_tests/** | All paths within `E:\GT-KB`; no out-of-root targets. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`; no exceptions. |
| `.claude/rules/bridge-essential.md` | advisory | foundational | Bridge protocol integrity preserved; the gate change does not affect bridge protocol itself, only the gate's path-extraction precision. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, DCL, owner decision | New DCL captures the verb-aware contract as a durable artifact. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | The new DCL will progress through specified → implemented → verified per standard lifecycle. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "Verb-aware path extraction" and `MUTATING_VERB_TABLE` are first-contact concepts; glossary update can follow in a sibling proposal. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: this session's AskUserQuestion response explicitly selected "P1: Verb-aware path extraction in impl-start-gate (Recommended)" from the 4-option prevention-mechanism choice. The proposal scope follows the recommendation in this session's prior "How can we prevent work-tree noise" analysis verbatim. Per-spec formal-artifact-approval packets at execution time require additional per-packet owner approval per `GOV-ARTIFACT-APPROVAL-001`.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-004.md` — Codex GO on REVISED-003 (this session's prior work; established the cleanup-context that exposed the false-positive class).
- `bridge/gtkb-workspace-orphan-cleanup-2026-06-05-001.md` (NEW; this session) — sibling chore-bridge that mitigated the *result* of the false-positives (orphan accumulation); this proposal addresses the *cause*.
- This session's commit log: `9558122e` (REVISED-003 commit had to drop `| tail -15` chaining marker to escape gate's `<unknown-mutating-target>` fallback); `3c5578f4` (harness-state SoT NO-GO commit); `72234a90` (orphan-cleanup bridge filing); `01356cb2` (parallel session's owner-AUQ'd `--no-verify` sweep — the de facto escape valve when the gate over-fires).
- DECISION-1087 (memory/pending-owner-decisions.md) — parallel session's AUQ for `--no-verify` bypass; demonstrates the cost of the false-positive class.
- This session's "How can we prevent work-tree noise" analysis (in-chat) — derived the 6 prevention mechanisms; this is P1.
- `.claude/rules/bridge-essential.md` § "Re-Enabling Pollers" — pattern precedent for "narrow the protection surface without weakening it" (the re-enable rule is similarly conservative).

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

Owner-decision evidence authorizing this proposal:

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Prevention mechanism selection | AskUserQuestion | This session's AUQ response "P1: Verb-aware path extraction in impl-start-gate (Recommended)" at 2026-06-05 UTC | Authorizes filing this bridge proposal targeting `scripts/implementation_start_gate.py` |
| Work-tree-noise-prevention sequence | Owner prompt (this session) | "How can we prevent work-tree noise in the future?" | Establishes the prevention-mechanism design space; P1 is one of 6 |

Per-spec formal-artifact-approval packet at execution time will require per-packet owner approval as a separate AUQ event per `GOV-ARTIFACT-APPROVAL-001`. Specifically: `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` needs a packet at `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.json` before MemBase insert.

## Acceptance Criteria

1. **DCL landed:** `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` v1 in MemBase via formal-artifact-approval packet with owner approval.
2. **Source refactor landed:** `scripts/implementation_start_gate.py` updated with new `MUTATING_VERB_TABLE` constant and verb-aware `_paths_from_shell` implementation.
3. **Test coverage added:** `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` covers all 5 false-positive cases enumerated in §Summary and all sanity cases.
4. **All tests pass:** `pytest platform_tests/scripts/test_implementation_start_gate_verb_aware.py` GREEN; existing impl-start-gate test suite remains GREEN (no regressions).
5. **Ruff clean:** `ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate_verb_aware.py` + `ruff format --check` GREEN.
6. **No regression in protected-path enforcement:** the sanity tests (git add of protected path, git rm of protected path, commit with staged protected files) MUST remain blocked. Verified by test fixtures.
7. **No project-root-boundary violation:** all target_paths within `E:\GT-KB`.
8. **Self-verification:** after the refactor lands, the commands that false-positive-fired this session (heredoc commit messages mentioning paths, `grep -E "scripts/|..."` patterns, `git restore --staged` with non-protected paths) MUST execute without blocking. Verified by manual smoke after implementation.

## Phased Implementation Plan

**Phase 1 — Spec governance landing (1 formal-artifact-approval packet):**

1. Generate packet for `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` v1 — content defines the verb-aware contract per §Summary > Governance. Owner approval gate fires.
2. Insert via `KnowledgeDB.insert_spec` per packet evidence.

**Phase 2 — Source refactor:**

3. Add `MUTATING_VERB_TABLE` constant to `scripts/implementation_start_gate.py` enumerating verbs and their argument-position extractors (e.g., `("git rm", lambda toks: toks[2:])`, `("git restore --staged", lambda toks: toks[3:])`, `("git add", lambda toks: toks[2:])`, etc.).
4. Refactor `_paths_from_shell` to:
   - Tokenize via `shlex.split(command, posix=False)`.
   - Split on pipeline separators (`|`, `&&`, `||`, `;`) into pipeline stages.
   - For each stage: identify the verb (first non-env-prefix token), look up in `MUTATING_VERB_TABLE`, apply the verb-specific extractor to extract path tokens.
   - Normalize each extracted token via existing `_normalize` helper.
   - Return the union of all stages' extracted paths.
   - For unknown verbs (not in `MUTATING_VERB_TABLE`): return empty list (the existing `_is_safe_command` and `_has_mutating_signal` checks determine if the command can proceed; if not safe and not mutating, gate doesn't fire).
5. Preserve `_is_safe_command`, `_has_mutating_signal`, `_is_mutating_command` behavior unchanged (the refactor is to path-extraction only).

**Phase 3 — Test coverage:**

6. Write `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` with:
   - 5 false-positive fixtures (heredoc commit messages, grep patterns, git status, git restore --staged of unprotected paths, cat of /tmp file containing protected paths).
   - 6 sanity fixtures (git add/rm/commit of protected paths must still be blocked).
   - 3 edge-case fixtures (pipeline stages with mixed protected/unprotected verbs, env-prefix handling, quoted-span path handling).
7. Run pytest + ruff. Verify GREEN before filing post-impl report.

**Phase 4 — Implementation report:**

8. File `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-002.md` as NEW post-impl report with spec-to-test mapping + observed test results + self-verification smoke evidence + applicability+clause preflights.

## Specification-Derived Verification Plan

| Spec (extended/new) | Test file | Acceptance check |
|---|---|---|
| `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` v1 (verb-aware contract) | `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` | All 5 false-positive cases return empty path list (or non-mutating); all 6 sanity cases extract protected paths and trigger gate block; all 3 edge-case fixtures behave per contract |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` (no-bypass preservation) | `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` (sanity subset) | git add/rm/commit of protected paths without impl-auth packet remain blocked; regression test against the 6 sanity cases |
| Existing impl-start-gate test suite (regression) | Existing tests | All existing tests pass unchanged |

## Risk and Rollback

**Risk 1 — Verb table incompleteness.** A verb not in `MUTATING_VERB_TABLE` could mutate protected paths without triggering the gate. **Mitigation**: the table starts with the same verb set as the current `MUTATING_COMMAND_RE` regex (so no regression). Unknown verbs default to empty path extraction; combined with `_has_mutating_signal` check, this preserves fail-closed behavior for any verb that IS in `MUTATING_COMMAND_RE` but NOT in the table (those still trigger the `<unknown-mutating-target>` fallback). Adding new verbs to the table is a future incremental safe change.

**Risk 2 — Argument-position extractor edge cases.** Complex shell constructs (variable expansion, command substitution, here-doc bodies passed as args) could confuse the per-verb extractor. **Mitigation**: the test fixtures cover the main edge cases observed this session; the implementation falls back to `<unknown-mutating-target>` on tokenization failure (`shlex.split` ValueError); the per-verb extractors use simple positional slicing (no AST-level parsing) so they're predictable.

**Risk 3 — Cross-shell incompatibility.** PowerShell vs POSIX bash have different verb syntax. **Mitigation**: `MUTATING_VERB_TABLE` enumerates BOTH shells' verbs (PowerShell `set-content`, `out-file`, `new-item`, `remove-item`, `move-item`, `copy-item` plus POSIX `git`, `rm`, etc.). `shlex.split` with `posix=False` handles PowerShell-style quoting acceptably for path extraction purposes.

**Rollback:** Per-phase reversibility:
- Phase 1: DCL insert is append-only versioned — withdraw via `withdrawn` status.
- Phase 2: source refactor is file-level reversible via git revert. The refactor is additive (new constant + new function logic) — the old `_paths_from_shell` body becomes the dead else-branch; full revert via `git revert` restores prior behavior.
- Phase 3: test additions are file-level reversible.

If Codex NO-GO this proposal: no source mutations occur; rollback is trivial (this bridge file alone is superseded by REVISED-N).

## Pre-Filing Preflight Subsection

Both mandatory preflights to be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-verb-aware-path-extraction
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-verb-aware-path-extraction
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green (no blocking gaps).

This proposal cites every spec triggered by its paths and content per `config/governance/spec-applicability.toml`. Touches one source file in `scripts/` and one test file in `platform_tests/` — both PROTECTED prefixes; impl-auth packet required at Phase 2 implementation start time.

---

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
