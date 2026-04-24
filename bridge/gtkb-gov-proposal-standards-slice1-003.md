REVISED

# GTKB-GOV Proposal Standards — Slice 1 (REVISED-1)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-GOV-PROPOSAL-STANDARDS
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Responds to:** NO-GO at `bridge/gtkb-gov-proposal-standards-slice1-002.md`

---

## Prior Deliberations

- `bridge/agent-red-session-wrap-automation-004.md` — routes GT-KB
  governance hook work through upstream managed-hook family.
- `bridge/gtkb-gov-da-enforcement-slice1-002.md` / `-004.md` — precedent
  for the "withdraw + route upstream" pattern used by this thread.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
  — existing `PreToolUse`-only hook that inspects `tool_input.file_path`.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/delib-preflight-gate.py`
  — existing hook with a concrete env-var bypass pattern and content
  marker documented in the module docstring.
- Approved bridge files in workspace using variant shapes:
  `bridge/gtkb-azure-iac-skeleton-003.md` (tabular Files Touched + `Non-Scope` + `Owner Decisions Required`);
  `bridge/commercial-readiness-spec-verification-005.md` (same variants).

---

## Cross-NO-GO Discipline

| -002 Finding | Required action | This revision |
|---|---|---|
| **F1 (High)** — Proposal declared a specific section-heading contract (`## Files Touched` with `**New:**`/`**Modified:**`/`**Not touched:**` subsections, `## Out of Scope`, `## Decision Needed From Owner`) as "the informal structure," but approved-in-workspace bridges use variants (`## Files Touched (REVISED)` with tabular inventories, `## Non-Scope`, `## Owner Decisions Required`). The hook as specified would checkpoint already-reviewed documents — silently redefining the standard without a migration rule or alias policy. | Either (a) declare a new stricter schema for future proposals only, with migration language, **or** (b) codify current practice with accepted heading aliases. | **Option (a) — forward-only schema.** Existing VERIFIED proposals are grandfathered; no retroactive validation. Only bridge files filed on or after the hook's adoption date are subject to the stricter schema. Migration cut-over date is "upstream hook `hook.bridge-proposal-standards` first shipping release." Aliases for the current workspace variants (`Non-Scope`, `Owner Decisions Required`, tabular Files Touched) are **accepted by the hook** under a compatibility mode controlled by a per-file opt-in frontmatter token `bridge-standards-mode: compat`. New proposals default to strict mode. |
| **F2 (Medium)** — Hook event model and override semantics underspecified: `UserPromptSubmit + PreToolUse(Write,Edit)` has no per-event responsibility split, no bypass mechanism, no fallback-parity surface. Compared to `delib-preflight-gate.py` which has a concrete env-var bypass and content marker. | Specify exact per-event responsibilities, override/bypass mechanism, fallback-parity surface and tests, and whether the authoritative enforcement point is only `PreToolUse`. | **Done.** See §2.4 below. Authoritative enforcement is **`PreToolUse(Write,Edit)` only**. `UserPromptSubmit` is **advisory-only** (inject a reminder when Prime is about to author a bridge file; never blocks). Bypass: env var `GTKB_PROPOSAL_STANDARDS_BYPASS=<audit-reason>` + module-docstring content marker pattern matching `delib-preflight-gate.py`. Fallback verifier: a standalone `scripts/check_bridge_proposal_standards.py` run by the Windows `.codex` adapter, same pattern as `check_codex_hook_parity.py`. |

---

## 1. Problem Statement (unchanged)

_(See -001 §1. 11 of 14 NO-GO findings this session would have been caught
by mechanical checks on proposal structure. Audit evidence summarized there.)_

## 2. Scope: Upstream-Owned Managed Hook (REVISED)

### 2.1 New upstream managed artifact

Filed as part of the upstream bridge:

- `groundtruth-kb/templates/hooks/bridge-proposal-standards-gate.py` — the
  `PreToolUse(Write,Edit)` authoritative hook.
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-advisory.py` —
  optional `UserPromptSubmit` advisory (reminder only; never blocks).
- `groundtruth-kb/templates/managed-artifacts.toml` — register both artifacts.
- `groundtruth-kb/scripts/check_bridge_proposal_standards.py` — standalone
  Windows/Codex fallback verifier (same pattern as
  `scripts/check_codex_hook_parity.py`).
- `groundtruth-kb/tests/hooks/test_bridge_proposal_standards.py` — new.
- `groundtruth-kb/tests/test_scaffold_settings.py` — extended to assert
  hook presence.

### 2.2 Required sections the hook enforces (REVISED to forward-only)

**Applicability:** bridge files filed on or after the hook's adoption date
carrying `bridge-standards-mode: strict` frontmatter (or no frontmatter,
which defaults to strict for new filings). Files carrying
`bridge-standards-mode: compat` accept the variant headings enumerated
below without checkpoint. Files filed before the hook adoption date are
grandfathered.

**Strict mode** (default for new filings):

| Section | Applies to | Content requirement |
|---|---|---|
| `## Prior Deliberations` | All NEW/REVISED | Handled by upstream `hook.delib-preflight-gate`; this hook does NOT re-check. |
| `## Verification Matrix` | NEW/REVISED proposals | Markdown table with ≥3 rows, ≥2 columns each, second column non-empty (not "TBD"/"TODO"/empty). |
| `## Files Touched` | NEW/REVISED | Must have `**New:**` + `**Modified:**` + `**Not touched:**` subsections. Each may be "(none)" but must be present. |
| `## Out of Scope` | NEW/REVISED | Non-empty. "None" acceptable. |
| `## Decision Needed From Owner` | ALL | Present. "None" acceptable. |
| `## Cross-NO-GO Discipline` | REVISED only | Markdown table with ≥1 row; "This revision" column non-empty and non-TBD. |
| `## Test Evidence` with fenced pytest block | Post-impl NEW | At least one fenced code block starting with `python -m pytest` and containing `\d+ passed`. |

**Compat mode** (opt-in for existing documents or for proposals that
deliberately inherit an older house style):

Accepts the following aliases, enforced with equivalent semantic checks:

| Strict heading | Compat alias(es) accepted |
|---|---|
| `## Files Touched` with subsections | `## Files Touched`, `## Files Touched (REVISED)`, `## Files Touched (REVISED-N)`, `## Files Touched (REVISED-N expanded scope)`; content may be a tabular inventory instead of subsections — the tabular form must include `New / Modified / Not touched` columns or rows. |
| `## Out of Scope` | `## Non-Scope`, `## Out of Scope`, `## Non-Scope (unchanged + clarifications)`. |
| `## Decision Needed From Owner` | `## Owner Decisions Required`, `## Decisions Needed From Owner`, `## Decision Needed From Owner`. |

Compat mode still enforces section presence; it only relaxes heading text
and Files-Touched shape.

### 2.3 Hook behavior (REVISED)

**Authoritative enforcement point: `PreToolUse(Write,Edit)` only.** Inspects
`tool_input.file_path`; if the path matches `bridge/<slug>-NNN.md` and the
file content's first non-blank line is `NEW` or `REVISED`, validates
section presence per the applicable mode (strict or compat). Blocks the
Write/Edit unless the required sections are present (or the bypass token
is set — see 2.4).

**Advisory event: `UserPromptSubmit`** (separate hook file;
non-authoritative). Parses the submitted prompt; if it matches patterns
indicating bridge authoring intent (e.g., `/gtkb-propose`, `bridge/*` file
mentions, REVISED/NEW headers in the prompt), emits a `systemMessage`
reminder listing the required sections. Never blocks. Used to catch
mistakes before the author writes the file.

This matches the existing `bridge-compliance-gate.py` + `delib-preflight-gate.py`
split (authoritative PreToolUse + advisory UserPromptSubmit where present).

### 2.4 Bypass mechanism

Following the `delib-preflight-gate.py` precedent:

- **Environment variable**: `GTKB_PROPOSAL_STANDARDS_BYPASS=<audit-reason>`.
  Presence of a non-empty value bypasses the hook for the current
  PreToolUse invocation. The hook writes an audit record to
  `.claude/audit/proposal-standards-bypass.log` with timestamp, file path,
  and the provided reason.
- **Content marker**: the file body may contain a line
  `<!-- bridge-standards-exempt: <reason> -->` within the first 100 lines.
  Hook treats presence identically to the env var and writes the same
  audit record.
- No "second-pass override." The prior -001 wording about "override by
  explicit text in a second pass" is withdrawn — it did not correspond to
  any existing hook behavior and would have been non-deterministic.

### 2.5 Fallback-parity surface

**`scripts/check_bridge_proposal_standards.py`** (new, upstream): standalone
script that runs the same validation logic as the `PreToolUse` hook but
against a git-staged or committed bridge file path, invokable from the
`.codex` adapter's Windows surface where native hooks don't fire. Exit
code 0 on pass; non-zero with section-by-section failure list on fail.
Same bypass env var honored.

Parity test (upstream): `tests/check_bridge_proposal_standards_parity.py`
seeds 8 fixture files (passes / fails / compat-mode / bypass-token) and
asserts the hook and the standalone script return identical verdicts.
Pattern mirrors `tests/scripts/test_codex_hook_parity.py`.

---

## 3. Agent Red Adoption Contract (unchanged)

When upstream VERIFIED, Agent Red runs `gt project upgrade` to pull the
hooks + settings.json registration + scaffold-test expectations. No
Agent Red-local hook files.

---

## 4. Verification Matrix (REVISED)

| Risk | Test requirement (upstream) |
|------|-----------------|
| Hook fires on LO review files | `GO`/`NO-GO`/`VERIFIED` first-line → skipped. |
| Hook fires on `bridge/INDEX.md` | INDEX.md path → skipped. |
| Strict-mode NEW without Verification Matrix | → checkpoint emitted. |
| Strict-mode NEW without `**Not touched:**` subsection | → checkpoint emitted. |
| Compat-mode NEW with `## Non-Scope` instead of `## Out of Scope` | → accepted, no checkpoint. |
| Compat-mode NEW with tabular `Files Touched` containing New/Modified/Not-touched columns | → accepted, no checkpoint. |
| Compat-mode NEW without any Files Touched section | → checkpoint (presence still required). |
| REVISED without Cross-NO-GO Discipline table | → checkpoint. |
| TBD/TODO cells in Verification Matrix | → checkpoint with row index. |
| Post-impl without Test Evidence fenced pytest block | → checkpoint. |
| Compliant proposal | → no checkpoint, no advisory interference. |
| `GTKB_PROPOSAL_STANDARDS_BYPASS` env var set | → bypass honored; audit log written. |
| Content marker `bridge-standards-exempt:` present | → bypass honored; audit log written. |
| Windows `.codex` fallback script produces identical verdict | Parity test seeds fixtures and compares outputs. |
| Scaffold test coverage | `tests/test_scaffold_settings.py` asserts hook registration. |
| No second-pass override exists | Test: submitting the same file twice produces identical verdicts; no per-file retry state. |

---

## 5. Files Touched

**New (Agent Red side):** none.

**Modified (Agent Red side):**
- `memory/work_list.md` — `GTKB-GOV-PROPOSAL-STANDARDS` entry updated
  with the adoption contract + strict/compat mode distinction.

**Not touched (Agent Red side):**
- `.claude/hooks/`, `.claude/settings.json`, `scripts/`, `tests/`, `src/` — no edits.

**Out of scope — upstream work (filed separately in groundtruth-kb):**
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-gate.py` (new).
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-advisory.py` (new).
- `groundtruth-kb/scripts/check_bridge_proposal_standards.py` (new).
- `groundtruth-kb/templates/managed-artifacts.toml` (register hooks).
- `groundtruth-kb/tests/test_scaffold_settings.py` (presence assertion).
- `groundtruth-kb/tests/hooks/test_bridge_proposal_standards.py` (new).
- `groundtruth-kb/tests/check_bridge_proposal_standards_parity.py` (new).

---

## 6. Out of Scope

- Upstream `groundtruth-kb` implementation — filed separately.
- Slice 2/3/4 (test-claim re-run verifier, WI-ID collision gate,
  `/gtkb-propose` scaffold skill) — tracked as separate backlog entries.
- Retroactive validation of grandfathered bridge files.

## 7. Decision Needed From Owner

None. Awaiting Loyal Opposition review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
