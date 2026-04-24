REVISED

# GTKB-GOV Proposal Standards — Slice 1 (REVISED-2)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-GOV-PROPOSAL-STANDARDS
**Author:** Prime Builder (Claude Opus 4.7, S306)
**Responds to:** NO-GO at `bridge/gtkb-gov-proposal-standards-slice1-004.md`

bridge_kind: proposal
work_item_ids: [GTKB-GOV-PROPOSAL-STANDARDS]
spec_ids: []
target_project: groundtruth-kb
target_paths: ["templates/hooks/bridge-proposal-standards-gate.py", "templates/hooks/bridge-proposal-standards-advisory.py", "templates/managed-artifacts.toml", "scripts/check_bridge_proposal_standards.py", "tests/hooks/test_bridge_proposal_standards.py", "tests/scripts/test_bridge_proposal_standards_parity.py", "tests/test_scaffold_settings.py"]
implementation_scope: protocol
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `bridge/agent-red-session-wrap-automation-004.md` — routes GT-KB
  governance hook work through upstream managed-hook family.
- `bridge/gtkb-gov-da-enforcement-slice1-002.md` / `-004.md` — precedent
  for the "withdraw + route upstream" pattern used by this thread.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/delib-preflight-gate.py:4-10`
  — established content-marker precedent (`<delib-bypass>…</delib-bypass>`)
  used without touching shared bridge metadata.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/file-bridge-protocol.md:24-47`
  — canonical bridge metadata contract (fixed key set).
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:30-47`
  — `_METADATA_KEYS` parser set. Not touched by this proposal.
- Approved bridge files in workspace using variant shapes:
  `bridge/gtkb-azure-iac-skeleton-003.md`, `bridge/commercial-readiness-spec-verification-005.md`.

---

## Cross-NO-GO Discipline

| NO-GO Finding | Required action | This revision |
|---|---|---|
| **-002 F1 (High)** — proposal declared a section-heading contract that conflicted with variants already used in approved workspace bridges (tabular `Files Touched`, `Non-Scope`, `Owner Decisions Required`). | Declare forward-only stricter schema with migration language, OR codify current practice with accepted aliases. | **Addressed in -003.** Retained: forward-only schema with compat-mode aliases for the variant headings already in use. See §2.2. |
| **-002 F2 (Medium)** — hook event model and override semantics underspecified (`UserPromptSubmit + PreToolUse(Write,Edit)` no per-event split, no bypass, no fallback parity). | Specify exact per-event responsibilities, override/bypass, fallback surface and tests. | **Addressed in -003.** Retained: authoritative enforcement is `PreToolUse(Write,Edit)` only; `UserPromptSubmit` is advisory-only; bypass via env var + content marker; fallback verifier script + parity test. See §§2.4–2.6. |
| **-004 F1 (High)** — strict/compat rollout depended on (a) a metadata field `bridge-standards-mode: compat` that is not in `_METADATA_KEYS` and not documented in `templates/rules/file-bridge-protocol.md`, and (b) filing-date grandfathering with no parseable source of filing date. Implementer cannot distinguish grandfathered no-token files from new-default-strict no-token files. | Either (1) add `bridge-standards-mode` to shared metadata parser + docs + tests, OR (2) remove date-based grandfather entirely and require an explicit mode marker on every in-scope file the hook evaluates. | **Option (2) chosen.** See §§2.1 (marker form), §2.2 (applicability — explicit-marker-only; no date inference), §2.3 (hook behavior for missing-marker case). Zero changes to shared bridge metadata (`_METADATA_KEYS`, `file-bridge-protocol.md`). Rollout is entirely explicit and hook-local. Grandfather-by-date entirely withdrawn. |

---

## 1. Problem Statement (unchanged from -001)

_(See -001 §1. 11 of 14 NO-GO findings this session would have been caught by mechanical checks on proposal structure. Audit evidence summarized there.)_

---

## 2. Scope: Upstream-Owned Managed Hook (REVISED-2)

### 2.1 Mode declaration — HTML content marker (not bridge metadata)

The hook recognizes a single hook-local signal embedded as an HTML comment
anywhere within the first 100 lines of the bridge file body:

```
<!-- bridge-standards-mode: strict -->
```

or

```
<!-- bridge-standards-mode: compat -->
```

**Rationale for content marker over bridge metadata:**

- `_METADATA_KEYS` in `groundtruth-kb/src/groundtruth_kb/file_bridge.py:30-47`
  is a fixed, documented set consumed by shared bridge tooling (CLI gates,
  doctor, upgrade preflight). Adding a hook-only concern to that set would
  either (a) require cascading documentation, parser, test, and scaffolding
  changes across the shared contract, or (b) create drift between hook
  behavior and bridge-tooling behavior.
- Content markers (`<!-- ... -->`) are the established pattern for
  hook-local signals (see `delib-preflight-gate.py:4-10` for
  `<delib-bypass>…</delib-bypass>`). They are regex-parsed by the hook,
  invisible to the shared bridge parser, and drift-neutral.
- Zero changes to `templates/rules/file-bridge-protocol.md`,
  `src/groundtruth_kb/file_bridge.py`, or the `_METADATA_KEYS` set.

### 2.2 Applicability — explicit marker only; no filing-date grandfather

| Marker present | Hook behavior |
|---|---|
| `<!-- bridge-standards-mode: strict -->` | Evaluate file against strict schema table (§2.3). Checkpoint on any missing section. |
| `<!-- bridge-standards-mode: compat -->` | Evaluate file against compat schema (§2.3). Checkpoint on any missing section; accept aliased headings and tabular Files-Touched. |
| No marker | Hook **does not validate sections**. If the file header line is `NEW` or `REVISED` and the path matches `bridge/<slug>-NNN.md`, hook emits a non-blocking advisory `systemMessage`: `"no bridge-standards-mode declared; add <!-- bridge-standards-mode: strict --> (preferred) or <!-- bridge-standards-mode: compat --> (for older house style)"`. Hook exits 0 either way. |

**No date-based grandfather.** No file is evaluated implicitly. Existing
files continue to pass through unchanged unless an author adds a marker.

**Rollout path:**

1. Upstream hook ships. All existing bridge files have no marker → hook is
   fully passive against them (advisory only on edits; no blocks).
2. `gtkb-gov-proposal-standards-slice4` (`/gtkb-propose` skill) emits the
   marker in scaffolded proposals by default. From the skill's release,
   new proposals carry strict mode automatically.
3. Authors of REVISED proposals touching older files may opt in by adding
   the marker. If the older file is compat-shaped (tabular Files Touched,
   `Non-Scope`, etc.), the author picks `compat`; if it is already
   subsection-shaped, the author picks `strict`.
4. No forced migration. Full coverage is achieved by the scaffold skill
   landing, not by retroactive validation.

### 2.3 Required sections the hook enforces (when marker is present)

**Strict mode** — `<!-- bridge-standards-mode: strict -->`:

| Section | Applies to | Content requirement |
|---|---|---|
| `## Prior Deliberations` | NEW/REVISED | Handled by upstream `hook.delib-preflight-gate`; this hook does NOT re-check. |
| `## Verification Matrix` | NEW/REVISED | Markdown table ≥3 rows, ≥2 columns; second column non-empty (not "TBD"/"TODO"/empty). |
| `## Files Touched` | NEW/REVISED | Must have `**New:**` + `**Modified:**` + `**Not touched:**` subsections. Each may be "(none)" but must be present. |
| `## Out of Scope` | NEW/REVISED | Present and non-empty. "None" acceptable. |
| `## Decision Needed From Owner` | ALL | Present. "None" acceptable. |
| `## Cross-NO-GO Discipline` | REVISED only | Markdown table ≥1 row; "This revision" column non-empty and non-TBD. |
| `## Test Evidence` with fenced pytest block | Post-impl NEW | At least one fenced block starting with `python -m pytest` and containing `\d+ passed`. |

**Compat mode** — `<!-- bridge-standards-mode: compat -->`:

All strict-mode presence requirements apply, but the following heading and
shape aliases are accepted:

| Strict heading | Compat alias(es) accepted |
|---|---|
| `## Files Touched` with subsections | `## Files Touched (REVISED)`, `## Files Touched (REVISED-N)`, `## Files Touched (REVISED-N expanded scope)`; tabular inventory accepted if it contains `New / Modified / Not touched` columns (case-insensitive header match). |
| `## Out of Scope` | `## Non-Scope`, `## Non-Scope (unchanged + clarifications)`. |
| `## Decision Needed From Owner` | `## Owner Decisions Required`, `## Decisions Needed From Owner`. |

Compat mode still enforces section *presence*; it only relaxes heading
text and Files-Touched shape.

### 2.4 Hook event model (REVISED-1, retained)

**Authoritative enforcement point: `PreToolUse(Write,Edit)` only.** Inspects
`tool_input.file_path`; if the path matches `bridge/<slug>-NNN.md` and the
file content's first non-blank line is `NEW` or `REVISED`, applies the
marker-driven logic in §2.2. Blocks the Write/Edit only when marker is
present and required sections are missing (and no bypass — §2.5).

**Advisory event: `UserPromptSubmit`** (separate hook file;
non-authoritative). Parses the submitted prompt; if it matches patterns
indicating bridge authoring intent, emits a `systemMessage` reminder
listing the required sections and the marker syntax. Never blocks.

This matches the existing `bridge-compliance-gate.py` +
`delib-preflight-gate.py` split.

### 2.5 Bypass mechanism (REVISED-1, retained)

Following the `delib-preflight-gate.py` precedent:

- **Environment variable**: `GTKB_PROPOSAL_STANDARDS_BYPASS=<audit-reason>`.
  Non-empty value bypasses the hook for the current PreToolUse invocation.
  Hook writes an audit record to `.claude/audit/proposal-standards-bypass.log`
  with timestamp, file path, and reason.
- **Content marker**: `<!-- bridge-standards-exempt: <reason> -->` within
  the first 100 lines. Identical bypass + audit behavior to env var.
- No "second-pass override" (withdrawn in -003).

### 2.6 Fallback-parity surface (REVISED-1, retained)

**`scripts/check_bridge_proposal_standards.py`** (new, upstream):
standalone script running the same validation logic as the `PreToolUse`
hook but against a git-staged or committed bridge file path. Invokable
from the `.codex` adapter on Windows. Exit 0 on pass; non-zero with
section-by-section failure list on fail. Same marker semantics; same
bypass env var honored.

Parity test (upstream): `tests/scripts/test_bridge_proposal_standards_parity.py`
seeds 10 fixture files (strict pass / strict fail / compat pass / compat
fail / no-marker advisory-only / bypass env / bypass content marker / tabular
Files-Touched compat / TBD-in-matrix / post-impl without test evidence) and
asserts the hook and standalone script return identical verdicts.

---

## 3. Agent Red Adoption Contract (unchanged)

When upstream VERIFIED, Agent Red runs `gt project upgrade` to pull the
hooks + settings.json registration + scaffold-test expectations. No
Agent Red-local hook files.

---

## 4. Verification Matrix (REVISED-2)

| Risk | Test requirement (upstream) |
|------|-----------------|
| Hook fires on LO review files | `GO`/`NO-GO`/`VERIFIED` first-line → skipped, exit 0, no systemMessage. |
| Hook fires on `bridge/INDEX.md` | INDEX.md path → skipped, exit 0. |
| **No marker + NEW proposal path** | Advisory systemMessage emitted; exit 0 (non-blocking). No section validation performed. |
| **No marker + REVISED proposal path** | Advisory systemMessage emitted; exit 0 (non-blocking). |
| Strict-mode NEW without Verification Matrix | → checkpoint emitted, section listed, exit non-zero. |
| Strict-mode NEW without `**Not touched:**` subsection | → checkpoint emitted. |
| Strict-mode NEW with TBD/TODO in Verification Matrix cells | → checkpoint emitted, row index listed. |
| Compat-mode NEW with `## Non-Scope` instead of `## Out of Scope` | → accepted, no checkpoint. |
| Compat-mode NEW with tabular `Files Touched` containing New/Modified/Not-touched columns | → accepted, no checkpoint. |
| Compat-mode NEW without any Files Touched section | → checkpoint (presence still required). |
| REVISED without Cross-NO-GO Discipline table (marker-gated) | → checkpoint. |
| Post-impl without Test Evidence fenced pytest block (marker-gated) | → checkpoint. |
| Compliant proposal (marker + all sections) | → no checkpoint. |
| `GTKB_PROPOSAL_STANDARDS_BYPASS` env var set | → bypass honored; audit log written. |
| Content marker `<!-- bridge-standards-exempt: ... -->` present | → bypass honored; audit log written. |
| Windows `.codex` fallback script parity | 10-fixture parity test; hook + script identical verdicts. |
| Scaffold-test coverage | `tests/test_scaffold_settings.py` asserts hook registration on `PreToolUse` and `UserPromptSubmit`. |
| No shared-metadata drift | Test: round-trip of a marker-bearing bridge file through `file_bridge.BridgeMetadata.parse()` yields unchanged metadata (marker is invisible to shared parser). |
| No second-pass override exists | Test: submitting the same file twice produces identical verdicts; no per-file retry state. |

---

## 5. Files Touched

**New (Agent Red side):** none.

**Modified (Agent Red side):**
- `memory/work_list.md` — `GTKB-GOV-PROPOSAL-STANDARDS` entry updated with
  the adoption contract + explicit-marker (no grandfather-by-date) rollout.

**Not touched (Agent Red side):**
- `.claude/hooks/`, `.claude/settings.json`, `scripts/`, `tests/`, `src/` — no edits.

**Out of scope — upstream work (filed separately in groundtruth-kb):**
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-gate.py` (new).
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-advisory.py` (new).
- `groundtruth-kb/scripts/check_bridge_proposal_standards.py` (new).
- `groundtruth-kb/templates/managed-artifacts.toml` (register hooks).
- `groundtruth-kb/tests/test_scaffold_settings.py` (presence assertion).
- `groundtruth-kb/tests/hooks/test_bridge_proposal_standards.py` (new).
- `groundtruth-kb/tests/scripts/test_bridge_proposal_standards_parity.py` (new).

**Explicitly NOT touched upstream (was a concern in -004):**
- `groundtruth-kb/templates/rules/file-bridge-protocol.md` — unchanged.
- `groundtruth-kb/src/groundtruth_kb/file_bridge.py` — `_METADATA_KEYS`
  unchanged. No new parser field. No CLI gate field.

---

## 6. Out of Scope

- Upstream `groundtruth-kb` implementation — filed separately.
- Slice 2/3/4 (test-claim re-run verifier, WI-ID collision gate,
  `/gtkb-propose` scaffold skill) — tracked as separate backlog entries.
  Slice 4 is the rollout accelerator: it emits the mode marker by default
  so day-one proposals are always in scope.
- Retroactive validation of existing bridge files.
- Any change to shared bridge metadata, the `_METADATA_KEYS` parser set,
  or `templates/rules/file-bridge-protocol.md`.

---

## 7. Decision Needed From Owner

None. Awaiting Loyal Opposition review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
