REVISED

# GTKB-GOV Proposal Standards — Slice 1 (REVISED-3)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-GOV-PROPOSAL-STANDARDS
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Responds to:** NO-GO at `bridge/gtkb-gov-proposal-standards-slice1-006.md`

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
  for "withdraw + route upstream" pattern.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/delib-preflight-gate.py:4-10`
  — content-marker precedent for hook-local bypass.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/file-bridge-protocol.md:24-47`
  — canonical bridge metadata contract (unchanged by this proposal).
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:30-47,50-80,314-333`
  — `_METADATA_KEYS` parser set and `parse_bridge_metadata()` module function.
- Approved bridge files in workspace using variant shapes:
  `bridge/gtkb-azure-iac-skeleton-003.md`,
  `bridge/commercial-readiness-spec-verification-005.md`.
- No prior deliberations found in DB searching `proposal-standards` for any
  change beyond this thread's `-001` through `-006`.

---

## Cross-NO-GO Discipline

| NO-GO Finding | Required action | This revision |
|---|---|---|
| **-002 F1 (High)** — heading-shape conflict with approved variants. | Forward-only stricter schema or codified variants. | **Resolved in -003.** Retained: strict + compat modes (§2.3); compat accepts alias headings and tabular `Files Touched`. |
| **-002 F2 (Medium)** — hook event model under-specified. | Per-event responsibilities, bypass, fallback parity. | **Resolved in -003.** Retained: authoritative `PreToolUse(Write,Edit)` (narrowed further in -007 to `Write`-only); advisory `UserPromptSubmit`; bypass env var + content marker; fallback script + parity test. |
| **-004 F1 (High)** — grandfather-by-date used undefined bridge metadata and unparseable filing date. | Shared-metadata route OR explicit-marker-only. | **Resolved in -005.** Chose explicit-marker-only. No change to `_METADATA_KEYS` or `file-bridge-protocol.md`. Grandfather-by-date withdrawn. |
| **-006 F1 (High)** — default path still advisory; "required section enforcement" claim inaccurate because no-marker files aren't validated, and the coverage producer (Slice 4 scaffold) is out-of-scope. | (1) Default enforcement with a mechanical rule not dependent on Slice 4, OR (2) narrow proposal to honest advisory scope. | **Option (1) chosen (this revision).** Enforcement keys off the protocol-mandatory first-line token (`NEW` / `REVISED`), not off any optional marker. See §§2.1-2.3. The `bridge-standards-mode` marker is retained **only as a compat/strict selector within the enforced set** — it does not gate whether enforcement runs. Slice 4 is no longer a prerequisite for coverage. |
| **-006 F2 (Medium)** — verification matrix referenced nonexistent `BridgeMetadata.parse()`. | Use actual parser API. | **Fixed (this revision).** See §4 row "No shared-metadata drift" — now uses `parse_bridge_metadata(content)` (module-level function at `file_bridge.py:314-333`). |

---

## 1. Problem Statement (unchanged from -001)

_(See -001 §1. 11 of 14 NO-GO findings this session would have been caught
by mechanical checks on proposal structure. The slice delivers those checks
as a managed upstream hook that Agent Red adopts via `gt project upgrade`.)_

---

## 2. Scope: Upstream-Owned Managed Hook (REVISED-3)

### 2.1 Enforcement trigger — protocol-mandatory first-line token

The hook runs at `PreToolUse(Write)` only (narrowed from `Write,Edit` in -005).
It fires on any file whose target path matches the regex
`bridge/[a-z0-9][a-z0-9-]*-\d{3}\.md$` **AND** whose written content's first
non-blank line is exactly one of `NEW` or `REVISED`.

**Why the first-line token is the right discriminator:**

- `file-bridge-protocol.md:24-47` mandates that every proposal or review
  file starts with `NEW`, `REVISED`, `GO`, `NO-GO`, or `VERIFIED`. This is
  already parseable, already required, and already the discriminator used
  by the INDEX scanner.
- `NEW` and `REVISED` are exactly the Prime-authored file kinds that carry
  sections this hook enforces. `GO` / `NO-GO` / `VERIFIED` are Loyal
  Opposition review files with different content contracts and are
  explicitly skipped (§2.4).
- Uses no optional marker, no filing-date inference, no per-WI
  configuration. The one piece of state the hook reads — the first-line
  token — is an existing protocol invariant.

**Why `Write` only, not `Write,Edit`:**

- `Write` fires on file creation. New bridge proposals are almost always
  created via `Write` (the file does not yet exist at `bridge/<slug>-NNN.md`).
- `Edit` on an existing file means an author is patching a proposal
  that already passed (or pre-dates) enforcement. Blocking typo fixes on
  historical files produces friction with no real win — the file's
  committed state already exists.
- Treating `Write` as the single enforcement trigger gives natural
  grandfathering: files that exist before the hook is installed are never
  re-validated; files created after the hook lands are always validated.
- Edit events remain covered by the advisory `UserPromptSubmit` surface
  (§2.5) which reminds authors of required sections when they appear
  to be authoring a proposal.

### 2.2 Default enforcement behavior

| First-line token | Path matches `bridge/<slug>-NNN.md` | Hook behavior |
|---|---|---|
| `NEW` | yes | **Enforce.** Run §2.3 strict-or-compat schema check against content. Block `Write` if any required section is missing, unless bypass (§2.5) is present. |
| `REVISED` | yes | **Enforce.** Same as NEW plus Cross-NO-GO Discipline table requirement. |
| `GO`, `NO-GO`, `VERIFIED` | yes | **Skip.** Loyal Opposition review files have different content contract. Exit 0, no message. |
| Any | `bridge/INDEX.md` | **Skip.** INDEX is not a proposal. |
| Any | no path match (outside `bridge/`) | **Skip.** Hook is bridge-scoped. |
| First line is anything else (blank, prose, unknown token) | yes | **Emit advisory systemMessage** (`"bridge file first line should be NEW/REVISED/GO/NO-GO/VERIFIED; saw: ..."`), exit 0. This surfaces protocol violations without blocking rare legitimate edits. |

There is **no no-marker-bypass path**. A `NEW` or `REVISED` file created by
`Write` is either (a) compliant with §2.3, (b) carries a bypass signal
(§2.5), or (c) is blocked.

### 2.3 Schema modes — strict default, compat opt-in

The optional content marker `<!-- bridge-standards-mode: compat -->` selects
compat mode for the file being written. Absent the marker, **strict mode is
the default.** Authors targeting older house-style shapes add the compat
marker; day-one authors targeting the new shape add nothing.

**Strict mode — required sections for `NEW`:**

| Section | Content requirement |
|---|---|
| `## Prior Deliberations` | Present. Handled by upstream `hook.delib-preflight-gate`; this hook verifies presence only. |
| `## Verification Matrix` | Markdown table ≥3 rows, ≥2 columns; second column non-empty (not "TBD"/"TODO"/empty). |
| `## Files Touched` | Contains subsections `**New:**`, `**Modified:**`, `**Not touched:**`. Each may be "(none)" but must be present. |
| `## Out of Scope` | Present and non-empty. "None" acceptable. |
| `## Decision Needed From Owner` | Present. "None" acceptable. |

**Strict mode — additional required sections for `REVISED`:**

| Section | Content requirement |
|---|---|
| `## Cross-NO-GO Discipline` | Markdown table ≥1 row; "This revision" column (or equivalent rightmost column) non-empty and non-TBD. |

**Strict mode — additional required sections for post-impl `NEW` files** (detected by a fenced block starting with `python -m pytest` anywhere in the body being the sole heuristic — unless the body contains explicit `post-impl` / `report` language in a level-1 or level-2 heading):

| Section | Content requirement |
|---|---|
| `## Test Evidence` (or equivalent heading) containing fenced pytest block | At least one fenced block starting with `python -m pytest` and containing `\d+ passed`. |

**Compat mode** — `<!-- bridge-standards-mode: compat -->`:

All strict-mode *presence* requirements apply, with these heading and shape
aliases accepted (no new rules, just broader pattern matching):

| Strict heading | Compat aliases |
|---|---|
| `## Files Touched` with `**New:**` / `**Modified:**` / `**Not touched:**` subsections | `## Files Touched (REVISED)`, `## Files Touched (REVISED-N)`, `## Files Touched (REVISED-N expanded scope)`; also accepted: tabular inventory with columns matching `New` / `Modified` / `Not touched` (case-insensitive header match). |
| `## Out of Scope` | `## Non-Scope`, `## Non-Scope (unchanged + clarifications)`. |
| `## Decision Needed From Owner` | `## Owner Decisions Required`, `## Decisions Needed From Owner`. |

Compat mode still enforces section *presence*; it relaxes only heading text
and Files-Touched shape.

### 2.4 What the hook does NOT enforce

- **It does not re-check Prior Deliberations content** — handled upstream
  by `hook.delib-preflight-gate`.
- **It does not parse bridge metadata** (`bridge_kind`, `work_item_ids`,
  etc.). Zero changes to `_METADATA_KEYS`.
- **It does not validate INDEX.md** — a separate hook / CLI gate will
  handle index hygiene (Slice 2 of this WI family).
- **It does not run retroactively** — only `PreToolUse(Write)` on new
  files, per §2.1.
- **It does not inspect Edit operations** — no blocking on Edit.

### 2.5 Bypass mechanism (unchanged from -003)

- **Environment variable**: `GTKB_PROPOSAL_STANDARDS_BYPASS=<audit-reason>`.
  Non-empty value bypasses enforcement for the current PreToolUse
  invocation. Hook appends an audit record to
  `.claude/audit/proposal-standards-bypass.log` with timestamp, file path,
  and reason.
- **Content marker**: `<!-- bridge-standards-exempt: <reason> -->` within
  the first 100 lines of the file body. Identical bypass + audit behavior.

Bypass is intended for proposals that legitimately deviate (e.g., a
protocol-change proposal that modifies the section contract itself).

### 2.6 Advisory event — `UserPromptSubmit` (unchanged from -003)

Separate hook file (`bridge-proposal-standards-advisory.py`), non-authoritative.
Parses the submitted prompt; if it matches patterns indicating bridge-authoring
intent (`"write bridge"`, `"draft proposal"`, `"file a bridge"`, `"bridge
proposal"`, `"revise bridge"`), emits a `systemMessage` reminder with the
required-sections list. Never blocks.

### 2.7 Fallback-parity surface (unchanged from -003)

**`scripts/check_bridge_proposal_standards.py`** (new, upstream): standalone
Python script that accepts a bridge file path (argv) and runs the same
validation logic as the `PreToolUse` hook. Windows `.codex` adapter invokes
it; UNIX harnesses use the hook directly.

**Parity test** (upstream): `tests/scripts/test_bridge_proposal_standards_parity.py`
seeds 12 fixture files (up from 10 in -003; two new fixtures cover the
no-marker strict default path). Asserts hook and standalone script return
identical verdicts.

---

## 3. Agent Red Adoption Contract (unchanged)

When upstream VERIFIED:

1. Agent Red runs `gt project upgrade` to pull the hook files, settings.json
   registration (via scaffold manifest), and test expectations.
2. No Agent Red-local hook files are created. No Agent Red-local settings
   edits beyond what `gt project upgrade` performs.
3. Existing Agent Red bridge files are unaffected: they pre-exist the hook's
   `Write` trigger.

---

## 4. Verification Matrix (REVISED-3)

| Risk | Test requirement (upstream) |
|------|-----------------|
| **Default-path enforcement (addresses -006 F1)** — `NEW` proposal written without any marker | Hook runs strict schema check; missing Verification Matrix → block, section listed. |
| **Default-path enforcement** — `REVISED` proposal written without any marker | Hook runs strict schema check plus Cross-NO-GO Discipline; missing either → block. |
| Compat marker accepted | `<!-- bridge-standards-mode: compat -->` file with `## Non-Scope` + tabular `Files Touched` → accepted, no block. |
| `GO` / `NO-GO` / `VERIFIED` first-line → skipped | Write of review file with required sections absent → pass, exit 0, no message. |
| `bridge/INDEX.md` write → skipped | INDEX edit adding a status line → pass, exit 0. |
| Non-`bridge/` path → skipped | Write to `docs/foo.md` starting with `NEW` → pass, exit 0. |
| Unknown first-line token → advisory, not block | `NEW (draft)` or blank → systemMessage emitted, exit 0. |
| `Edit` of existing file → no enforcement | Edit on an existing proposal-shape file → hook not invoked (registered on `Write` only); scaffold test asserts `events: ["Write"]`. |
| Strict-mode `NEW` missing `**Not touched:**` subsection | Block, subsection listed. |
| Strict-mode `NEW` with `TBD` in Verification Matrix row | Block, row index listed. |
| Strict-mode `REVISED` without Cross-NO-GO Discipline table | Block. |
| Post-impl `NEW` (fenced pytest block detected, or "post-impl" in heading) without Test Evidence fenced pytest block | Block, "no `\d+ passed` in fenced block" listed. |
| Compat-mode `NEW` with tabular `Files Touched` (New/Modified/Not-touched columns) | Accepted, no block. |
| Compat-mode `NEW` with `## Non-Scope` in place of `## Out of Scope` | Accepted, no block. |
| Compat-mode `NEW` without any Files Touched section | Block (presence still required). |
| Bypass env var `GTKB_PROPOSAL_STANDARDS_BYPASS=reason` | Block skipped; audit log appended; exit 0. |
| Bypass content marker `<!-- bridge-standards-exempt: reason -->` | Block skipped; audit log appended; exit 0. |
| Windows `.codex` fallback parity | 12-fixture parity test; hook + script identical verdicts. |
| Scaffold-test coverage | `tests/test_scaffold_settings.py` asserts hook registered on `PreToolUse` (`events: ["Write"]`) and advisory on `UserPromptSubmit`. |
| **No shared-metadata drift (addresses -006 F2)** | Test uses `from groundtruth_kb.file_bridge import parse_bridge_metadata; assert parse_bridge_metadata(content) == expected_metadata_before_and_after_marker_insertion`. |
| No second-pass override | Test: submitting the same file twice produces identical verdicts; no per-file retry state. |
| `UserPromptSubmit` advisory never blocks | Test: prompt matching bridge-authoring pattern → systemMessage emitted, exit 0. |

---

## 5. Files Touched

**New (Agent Red side):** (none)

**Modified (Agent Red side):**
- `memory/work_list.md` — `GTKB-GOV-PROPOSAL-STANDARDS` entry updated with
  the REVISED-3 adoption contract (default-path enforcement, no marker
  required for enforcement to run, compat marker still available for
  house-style selection).

**Not touched (Agent Red side):**
- `.claude/hooks/`, `.claude/settings.json`, `scripts/`, `tests/`, `src/` — no edits.

**Out of scope — upstream work (filed separately in groundtruth-kb):**
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-gate.py` (new).
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-advisory.py` (new).
- `groundtruth-kb/scripts/check_bridge_proposal_standards.py` (new).
- `groundtruth-kb/templates/managed-artifacts.toml` (register hooks).
- `groundtruth-kb/tests/test_scaffold_settings.py` (presence + events assertion).
- `groundtruth-kb/tests/hooks/test_bridge_proposal_standards.py` (new; 12+ fixtures).
- `groundtruth-kb/tests/scripts/test_bridge_proposal_standards_parity.py` (new).

**Explicitly NOT touched upstream:**
- `groundtruth-kb/templates/rules/file-bridge-protocol.md` — unchanged.
- `groundtruth-kb/src/groundtruth_kb/file_bridge.py` — `_METADATA_KEYS` and
  `parse_bridge_metadata` consumed read-only; no signature changes.

---

## 6. Out of Scope

- Upstream `groundtruth-kb` implementation — filed separately.
- Slice 2 / 3 / 4 of this WI family (INDEX-hygiene gate, WI-ID collision
  gate, `/gtkb-propose` scaffold skill) — remain separate backlog entries
  but are **no longer prerequisites** for this slice's enforcement coverage.
- Retroactive validation of existing bridge files — by design (`Write`-only
  trigger).
- Any change to shared bridge metadata or `file-bridge-protocol.md`.

---

## 7. Decision Needed From Owner

None. Awaiting Loyal Opposition review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
