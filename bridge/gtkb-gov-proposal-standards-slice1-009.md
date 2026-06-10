REVISED

# GTKB-GOV Proposal Standards — Slice 1 (REVISED-4)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-GOV-PROPOSAL-STANDARDS
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Responds to:** NO-GO at `bridge/gtkb-gov-proposal-standards-slice1-008.md`

bridge_kind: prime_proposal
work_item_ids: [GTKB-GOV-PROPOSAL-STANDARDS]
spec_ids: []
target_project: groundtruth-kb
target_paths: ["templates/rules/file-bridge-protocol.md", "templates/hooks/bridge-proposal-standards-gate.py", "templates/hooks/bridge-proposal-standards-advisory.py", "templates/managed-artifacts.toml", "scripts/check_bridge_proposal_standards.py", "tests/hooks/test_bridge_proposal_standards.py", "tests/scripts/test_bridge_proposal_standards_parity.py", "tests/test_scaffold_settings.py"]
implementation_scope: protocol
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `bridge/agent-red-session-wrap-automation-004.md` — routes GT-KB governance hook work through upstream managed-hook family.
- `bridge/gtkb-gov-da-enforcement-slice1-002.md` / `-004.md` — "withdraw + route upstream" precedent.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/delib-preflight-gate.py:4-10` — content-marker precedent for hook-local bypass.
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/file-bridge-protocol.md:24-47` — canonical INDEX.md metadata contract. **Modified by this revision** to add a body-level status-token section (see §2.0).
- `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:30-47,50-80,314-333` — `_METADATA_KEYS` parser set (unchanged) and `parse_bridge_metadata()` module function (unchanged; hook consumes read-only).
- No prior deliberations found in DB searching `proposal-standards body status token` or `file-bridge-protocol body-first-line`.

---

## Cross-NO-GO Discipline

| NO-GO Finding | Required action | This revision |
|---|---|---|
| **-002 F1 (High)** — heading-shape conflict with approved variants. | Forward-only stricter schema or codified variants. | **Resolved in -003.** Retained: strict + compat modes (§2.3). |
| **-002 F2 (Medium)** — hook event model under-specified. | Per-event responsibilities, bypass, fallback parity. | **Resolved in -003.** Retained. |
| **-004 F1 (High)** — grandfather-by-date used undefined bridge metadata and unparseable filing date. | Shared-metadata route OR explicit-marker-only. | **Resolved in -005.** Chose explicit-marker-only then replaced with first-line trigger in -007. |
| **-006 F1 (High)** — default path still advisory; enforcement conditional on opt-in marker. | Default enforcement or narrow scope to advisory. | **Resolved in -007.** First-line trigger makes enforcement default. |
| **-006 F2 (Medium)** — nonexistent `BridgeMetadata.parse()` API reference. | Use actual parser API. | **Fixed in -007.** Now `parse_bridge_metadata(content)`. |
| **-008 F1 (High)** — first-line trigger justified as a protocol invariant the shared contract does not document. The status vocabulary is defined for `bridge/INDEX.md` entries and for parser skip-lines, but no protocol section mandates a positional first-line body token. | Either (1) codify the body-level status-token rule in the shared protocol and keep the trigger as the discriminator, or (2) narrow claims to "heuristic derived from corpus practice". | **Option (1) chosen (this revision).** Upstream scope expands by one file: `templates/rules/file-bridge-protocol.md` gets a short new section documenting the body-level status-token convention. The hook then cites the newly-authoritative rule. Rationale: option 1 costs ~5 lines of doc and makes the hook honestly grounded; option 2 weakens the WI's enforcement claims for no protocol-correctness gain, since every existing bridge file in the workspace already follows the convention. See §2.0 for the exact upstream doc addition. |

---

## 1. Problem Statement (unchanged from -001)

_(See -001 §1. 11 of 14 NO-GO findings this session would have been caught
by mechanical checks on proposal structure. The slice delivers those checks
as a managed upstream hook, plus one small protocol-documentation addition
that makes the hook's trigger rule cite-able.)_

---

## 2. Scope: Upstream-Owned Managed Hook + Small Protocol Clarification (REVISED-4)

### 2.0 Upstream protocol doc addition — body-level status token (NEW in REVISED-4)

**File:** `groundtruth-kb/templates/rules/file-bridge-protocol.md`

**Addition** (proposed text, to be placed in a new subsection under the existing "Statuses" section that documents the INDEX.md status vocabulary):

```markdown
## Body-level status token

Each versioned bridge file (`bridge/<slug>-NNN.md`) begins its body with a
single line containing exactly one of the canonical status tokens
(`NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`). This line mirrors the status
recorded for the file in `bridge/INDEX.md` and is the same vocabulary
documented in the "Statuses" section above.

Rationale: reviewers and tooling consume the file body directly (not only
through the index), and a positional first-line token lets both surfaces
resolve a file's role identically without parsing prose. The convention is
already universal in the bridge corpus; this section documents it so
hooks and validators can cite it as an authoritative rule rather than an
empirical heuristic.
```

Approximately 8 lines of documentation. Zero changes to `_METADATA_KEYS`, to `parse_bridge_metadata()`, to any other shared parser, or to any CLI gate. The existing parser's behavior (skip status-token lines wherever they appear) remains a strict superset of what the new doc requires — no parser breakage.

### 2.1 Enforcement trigger — now citing a documented rule

The hook runs at `PreToolUse(Write)` only. It fires on any file whose target path matches
`bridge/[a-z0-9][a-z0-9-]*-\d{3}\.md$` **AND** whose written content's first
non-blank body line is exactly one of the canonical status tokens
(`NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`) per the new `file-bridge-protocol.md`
"Body-level status token" section (§2.0).

**Why this is now well-grounded:**

- The discriminator is defined in the shared bridge protocol document (§2.0).
- The vocabulary is the same used for `bridge/INDEX.md` entries; no parallel universe.
- No inference from corpus is needed; the protocol doc is the authority.
- No parser change is needed; the existing skip-behavior is unaffected.

**Why `Write` only, not `Write,Edit`:** unchanged from -007.
- `Write` fires on file creation; new proposals are almost always `Write`.
- `Edit` on an existing file means patching a proposal that already passed (or pre-dates) enforcement; blocking typo fixes adds friction with no real win.
- Natural grandfathering by trigger: files that exist before hook lands are not re-validated; files created after are always validated.
- Edit events remain covered by the advisory `UserPromptSubmit` hook (§2.6).

### 2.2 Default enforcement behavior (unchanged from -007)

| First-line token | Path matches `bridge/<slug>-NNN.md` | Hook behavior |
|---|---|---|
| `NEW` | yes | **Enforce.** Run §2.3 strict-or-compat schema check. Block `Write` if any required section is missing, unless bypass (§2.5) is present. |
| `REVISED` | yes | **Enforce.** Same as NEW plus Cross-NO-GO Discipline table requirement. |
| `GO`, `NO-GO`, `VERIFIED` | yes | **Skip.** Review files have different content contract. Exit 0, no message. |
| Any | `bridge/INDEX.md` | **Skip.** |
| Any | no path match (outside `bridge/`) | **Skip.** |
| Any line that is not one of the five canonical tokens | yes | **Emit advisory systemMessage** (`"bridge file first body line should be one of NEW/REVISED/GO/NO-GO/VERIFIED per file-bridge-protocol.md \"Body-level status token\"; saw: ..."`), exit 0. |

There is **no no-marker-bypass path**. A `NEW` or `REVISED` file created by `Write` is either (a) compliant with §2.3, (b) carries a bypass signal (§2.5), or (c) is blocked.

### 2.3 Schema modes — strict default, compat opt-in (unchanged from -007)

The optional content marker `<!-- bridge-standards-mode: compat -->` selects
compat mode. Absent the marker, **strict mode is the default.**

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
| `## Cross-NO-GO Discipline` | Markdown table ≥1 row; rightmost column non-empty and non-TBD. |

**Strict mode — additional required sections for post-impl `NEW` files** (detected by a fenced `python -m pytest` block in the body, or by "post-impl" / "report" language in an H1/H2 heading):

| Section | Content requirement |
|---|---|
| `## Test Evidence` (or equivalent) containing fenced pytest block | At least one fenced block starting with `python -m pytest` and containing `\d+ passed`. |

**Compat mode** — `<!-- bridge-standards-mode: compat -->`:

| Strict heading | Compat aliases |
|---|---|
| `## Files Touched` with `**New:**` / `**Modified:**` / `**Not touched:**` | `## Files Touched (REVISED)`, `## Files Touched (REVISED-N)`, `## Files Touched (REVISED-N expanded scope)`; also: tabular inventory with `New` / `Modified` / `Not touched` columns (case-insensitive). |
| `## Out of Scope` | `## Non-Scope`, `## Non-Scope (unchanged + clarifications)`. |
| `## Decision Needed From Owner` | `## Owner Decisions Required`, `## Decisions Needed From Owner`. |

Compat mode enforces section *presence*; relaxes only heading text and Files-Touched shape.

### 2.4 What the hook does NOT enforce (unchanged from -007)

- Prior Deliberations content — handled by `hook.delib-preflight-gate`.
- Bridge metadata parsing — zero changes to `_METADATA_KEYS`.
- INDEX.md validation — separate hook.
- Retroactive validation — `Write`-only, per §2.1.
- Edit operations — no blocking on Edit.

### 2.5 Bypass mechanism (unchanged from -003)

- Env var: `GTKB_PROPOSAL_STANDARDS_BYPASS=<audit-reason>`. Audit log at `.claude/audit/proposal-standards-bypass.log`.
- Content marker: `<!-- bridge-standards-exempt: <reason> -->` in first 100 lines. Same audit.

### 2.6 Advisory event — `UserPromptSubmit` (unchanged from -003)

Separate hook file (`bridge-proposal-standards-advisory.py`), non-authoritative. Emits systemMessage reminder on bridge-authoring prompts. Never blocks.

### 2.7 Fallback-parity surface (unchanged from -003)

`scripts/check_bridge_proposal_standards.py` — standalone Python script invoked by the Windows `.codex` adapter. Parity test: `tests/scripts/test_bridge_proposal_standards_parity.py` with 12 fixtures.

---

## 3. Agent Red Adoption Contract (unchanged)

On upstream VERIFIED, Agent Red runs `gt project upgrade` to pull the hook files, the updated `file-bridge-protocol.md` (the rule addition is pulled through the same scaffold update), settings.json registration, and test expectations. No Agent Red-local hook files or settings edits.

---

## 4. Verification Matrix (REVISED-4)

| Risk | Test requirement (upstream) |
|------|-----------------|
| **Body status-token rule cite-able (addresses -008 F1)** | Test: read `templates/rules/file-bridge-protocol.md`; assert the phrase "Body-level status token" appears as an H2 heading; assert the paragraph lists the five tokens `NEW, REVISED, GO, NO-GO, VERIFIED`. |
| **Default-path enforcement** — `NEW` proposal without any marker | Hook runs strict schema check; missing Verification Matrix → block. |
| **Default-path enforcement** — `REVISED` without any marker | Hook runs strict check plus Cross-NO-GO Discipline; missing either → block. |
| Compat marker accepted | `<!-- bridge-standards-mode: compat -->` with `## Non-Scope` + tabular `Files Touched` → accepted. |
| `GO` / `NO-GO` / `VERIFIED` first-line → skipped | Write of review file with required sections absent → pass, exit 0. |
| `bridge/INDEX.md` write → skipped | INDEX edit adding a status line → pass. |
| Non-`bridge/` path → skipped | Write to `docs/foo.md` starting with `NEW` → pass. |
| Unknown first-line token → advisory | `NEW (draft)` or blank → systemMessage emitted, exit 0. |
| `Edit` of existing file → no enforcement | Edit on existing proposal-shape file → hook not invoked; scaffold test asserts `events: ["Write"]`. |
| Strict-mode `NEW` missing `**Not touched:**` subsection | Block. |
| Strict-mode `NEW` with `TBD` in Verification Matrix row | Block. |
| Strict-mode `REVISED` without Cross-NO-GO Discipline table | Block. |
| Post-impl `NEW` without Test Evidence fenced pytest block | Block. |
| Compat-mode `NEW` with tabular `Files Touched` | Accepted. |
| Compat-mode `NEW` with `## Non-Scope` | Accepted. |
| Compat-mode `NEW` without any Files Touched section | Block (presence still required). |
| Bypass env var `GTKB_PROPOSAL_STANDARDS_BYPASS=reason` | Block skipped; audit log appended. |
| Bypass content marker `<!-- bridge-standards-exempt: reason -->` | Same. |
| Windows `.codex` fallback parity | 12-fixture parity test; hook + script identical verdicts. |
| Scaffold-test coverage | `tests/test_scaffold_settings.py` asserts hook on `PreToolUse` (`events: ["Write"]`) and advisory on `UserPromptSubmit`. |
| **No shared-parser drift** | Test uses `from groundtruth_kb.file_bridge import parse_bridge_metadata; assert parse_bridge_metadata(content) == expected_metadata` — metadata parsing unchanged before/after the protocol doc addition. |
| No second-pass override | Test: submitting the same file twice produces identical verdicts. |
| `UserPromptSubmit` advisory never blocks | Test: prompt matching bridge-authoring pattern → systemMessage, exit 0. |

---

## 5. Files Touched

**New (Agent Red side):** (none)

**Modified (Agent Red side):**
- `memory/work_list.md` — `GTKB-GOV-PROPOSAL-STANDARDS` entry updated with the REVISED-4 adoption contract (default-path enforcement grounded in the body-status-token protocol section).

**Not touched (Agent Red side):**
- `.claude/hooks/`, `.claude/settings.json`, `scripts/`, `tests/`, `src/` — no edits.

**Out of scope — upstream work (filed separately in groundtruth-kb):**
- `groundtruth-kb/templates/rules/file-bridge-protocol.md` (**new subsection added**, ~8 lines; otherwise unchanged). (Addresses -008 F1.)
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-gate.py` (new).
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-advisory.py` (new).
- `groundtruth-kb/scripts/check_bridge_proposal_standards.py` (new).
- `groundtruth-kb/templates/managed-artifacts.toml` (register hooks).
- `groundtruth-kb/tests/test_scaffold_settings.py` (presence + events assertion).
- `groundtruth-kb/tests/hooks/test_bridge_proposal_standards.py` (new; 12+ fixtures).
- `groundtruth-kb/tests/scripts/test_bridge_proposal_standards_parity.py` (new).

**Explicitly NOT touched upstream:**
- `groundtruth-kb/src/groundtruth_kb/file_bridge.py` — `_METADATA_KEYS` and `parse_bridge_metadata` consumed read-only. No signature changes. No new parser field. No CLI gate field. The body-status-token rule lives in protocol doc only; parsers remain a strict superset.

---

## 6. Out of Scope

- Upstream `groundtruth-kb` implementation — filed separately in groundtruth-kb/bridge/.
- Slice 2 / 3 / 4 of this WI family — separate backlog entries, no longer prerequisites.
- Retroactive validation of existing bridge files.
- Any change to `_METADATA_KEYS` or to the bridge metadata parser.

---

## 7. Decision Needed From Owner

None. Awaiting Loyal Opposition review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
