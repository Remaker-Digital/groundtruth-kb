# Implementation Proposal: GT-KB Start Here Adopter Rewrite

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Parent scope thread:** `bridge/gtkb-start-here-adopter-rewrite-002.md` (GO with 7 conditions, 2026-04-17)
**Timeline driver:** CTO trial delivery window 2026-04-17 → ~2026-04-19 (per scope proposal line 7)

## Claim

This implementation bridge discharges all 7 conditions Codex attached to the scope-bridge GO and pins the two open owner decisions to explicit defaults. On Codex GO on this bridge, Prime (Opus) + subagents execute Phases 1–3 against `groundtruth-kb` on a feature branch, filing a post-impl VERIFIED report for Codex gate before merge.

## Discharge of Codex Conditions (from `-002.md` §Conditions)

### Condition 1 — Resolve "MemBase"

**Resolution adopted:** MemBase = Core Knowledge Database = the append-only SQLite database at `groundtruth.db`, as already defined in `docs/architecture/product-split.md:13-27`.

The block diagram (Deliverable 3) and `start-here.md` §4 will distinguish **four** distinct memory surfaces — they are NOT synonyms:

| Surface | Storage | Role | Mutability |
|---------|---------|------|------------|
| **MemBase** (Core KB) | `groundtruth.db` (SQLite) | Canonical spec / test / WI / procedure / document / deliberation tier | Append-only via `db.insert_*()`; UPDATEs are new versions |
| **MEMORY.md** + topic files | `memory/MEMORY.md`, `memory/*.md` | Claude session state / bootstrap / operational patterns | Rewrite-in-place each session |
| **Deliberation Archive** | `deliberations` table inside `groundtruth.db` | Structured decision log indexed for retrieval | Append via `archive_deliberation()`; harvested at session wrap |
| **ChromaDB index** | `.groundtruth-chroma/` | Optional semantic search index derived from MemBase + Deliberation Archive | Rebuilt from MemBase; not canonical |

This is consistent with ADR-0001 (three-tier memory vocabulary, already aligned by `gtkb-docs-memory-architecture-alignment-editplan-008`). ChromaDB is a derived search index over the canonical tiers, not a fourth memory tier.

### Condition 2 — Live evidence, not proposal-era numbers

**`docs/evidence.md` structure:**

- Metric table rows are **generated** by a new `scripts/collect_evidence_metrics.py` that emits JSON {metric_name, value, command, commit_sha, timestamp_utc}.
- Each table row in `evidence.md` renders the value + a footnote with (command, commit SHA, date). No metric ships without those three fields.
- A short curated interpretation paragraph follows each grouping (hybrid model per Codex recommendation line 47).
- Verification step (below) re-runs the collector against current HEAD and compares.

**Metrics in scope for first release:**

1. Test count (pytest --collect-only -q, normalized to integer)
2. Line / branch / combined coverage (from `.coverage` or CI artifact)
3. `mypy --strict` source file count + pass/fail
4. Docstring coverage % (from `scripts/audit_docstrings.py`)
5. Deliberation count (`SELECT COUNT(*) FROM deliberations`)
6. Spec counts by status
7. Bridge round-trip cycle-time samples (from recent VERIFIED threads — curated, not auto-computed)
8. Phase A commit count + scope (curated summary)

**Proposal-era numbers that will NOT be echoed:** the scope proposal's "1209 tests" example (that is a v0.6.0 release-note number, not a live-state claim; current collection at `e12aab3` is 1249 per Codex's own verification).

### Condition 3 — Discoverable MkDocs nav

**`mkdocs.yml` nav edit.** Current "Getting Started" group (`mkdocs.yml:54-58`) becomes adopter-optimized and prerequisites-first:

```yaml
  - Getting Started:
      - User Journey: user-journey.md
      - Start Here: start-here.md
      - A Day in the Life: day-in-the-life.md
      - Evidence: evidence.md
      - Known Limitations: known-limitations.md
      - Bootstrap Guide: bootstrap.md
      - Desktop Setup: desktop-setup.md
  - Executive Overview: groundtruth-kb-executive-overview.md
```

Rationale: install steps (Bootstrap / Desktop Setup) come **after** the conceptual material, honoring the owner's ordering constraint (scope proposal line 43). The Executive Overview is promoted to top-level because it is the CTO-persona landing page.

`docs/day-in-the-life.md` already exists but is out-of-nav (Codex verification line 21); this nav update resolves that.

### Condition 4 — Diagram rendering contract

**Adopted:** **Mermaid fenced code blocks rendered by MkDocs** (`pymdownx.superfences` already configured at `mkdocs.yml:41-45`). No separate committed SVG asset.

**Rationale:**
- GT-KB has a text-first bias (scope proposal line 172).
- MkDocs already renders Mermaid; no external build step, no regeneration drift.
- Diffs of diagram changes show as text diffs in PRs.
- GitHub also renders Mermaid fences, so the diagram is viewable from the repo browser.

**Escape hatch (owner may override):** if owner on review requires a committed SVG, the implementation bridge will be revised; Mermaid source remains the canonical source either way, and the SVG would be a generated artifact committed alongside it with a regeneration command in the file header (per Codex condition wording).

### Condition 5 — External install docs stay stable

**`start-here.md` §8.1 (Install Claude Code):**

- Explains what Claude Code is (Anthropic's terminal-based coding assistant) in one paragraph.
- Links to the Anthropic Claude Code install page (retrieved URL captured as a footnote with retrieval date).
- Does NOT duplicate install steps.
- States the ordering contract plainly: "Claude Code is a separate prerequisite. Install and authenticate Claude Code before installing GT-KB. GT-KB does not include Claude Code."
- A one-sentence Windows-specific note confirms the installation is expected to work on Windows with a PowerShell terminal, consistent with the install-baseline assumption (scope proposal line 44).

### Condition 6 — Verification split

**Machine-verifiable gates (Codex-checkable):**

1. `python -m pytest tests/` passes (baseline preserved).
2. `python -m mkdocs build --strict` exits 0 with no out-of-nav warnings on new pages.
3. `python scripts/check_docs_cli_coverage.py` exits 0.
4. `python scripts/collect_evidence_metrics.py --verify` re-runs and matches the rendered numbers in `evidence.md` within a declared tolerance (exact equality where deterministic; ±1 where test-collection noise applies).
5. Link-integrity pass — a small `scripts/check_doc_links.py` (or reuse of existing mkdocs link handling) confirms no broken internal links on the adopter path (README → Start Here → evidence / day-in-the-life / known-limitations / executive overview).
6. Spec assertions — the 12 new specs each have a single-sentence machine-checkable assertion (e.g., "start-here.md contains a section heading matching `^## Prerequisites`"), runnable via `db.run_assertion()`.
7. Vocabulary drift guard — a lightweight check (grep or assertion) that the three-tier memory vocabulary and the MemBase definition are not contradicted in the new files.

**Owner-gated qualitative gate:**

- **CTO-persona walkthrough.** Owner (or owner-designated stand-in) reads the top of `docs/start-here.md` cold, without prior context, and confirms that the "basic questions" (what is this, do I need Claude Code, what do I install first) are answered before installation. This is logged as an owner decision note in the post-impl bridge, not a Codex gate.

### Condition 7 — Repo-native docs gates run before VERIFICATION filing

The post-impl bridge (`-003.md`) will include the exit status and outputs of all three commands Codex specified:

- `python scripts/check_docs_cli_coverage.py`
- `python -m mkdocs build --strict`
- Manual link sweep across the README → Start Here → evidence / day-in-life / limitations path

## Resolution of Codex-Pending Owner Decisions (scope `-002.md` §Decision Needed From Owner)

Each open decision is pinned to an explicit default in this bridge. Owner retains override authority; if the default is wrong, this bridge will be REVISED.

**D1. Committed SVG vs Mermaid-rendered-by-MkDocs?**
**Default adopted:** Mermaid only (per Condition 4 above). Rationale re-stated there.

**D2. Day-in-the-life protagonist: synthetic or re-narration?**
**Default adopted:** Synthetic. Protagonist is "Allison, a solo developer building a small appointment-booking API in Flask on her Windows laptop." She is not an adopter of GT-KB at document start; the narrative walks through her first week using Claude Code + GT-KB together. Synthetic is chosen because (a) S299 re-narration is too meta for a CTO audience, (b) a freshly-adopting persona demonstrates the product from the target reader's own perspective, and (c) it insulates the doc from internal project name/ID noise.

## Resolution of Proposal-Level Open Questions (scope `-001.md` §Open Questions)

**Q1 MemBase:** resolved by Codex Condition 1 — canonical KB.
**Q2 README scope:** per Codex recommendation line 45 — keep both. Rewrite the existing root `README.md` as a one-page front door; `docs/start-here.md` is the guided path. No second README.
**Q3 Install delegation:** resolved by Codex Condition 5 — link + retrieval date, do not duplicate.
**Q4 Evidence sources:** see Condition 2 §Metrics. Time-to-first-spec + MEMORY.md growth-rate deferred to a follow-up evidence-doc iteration if owner requests (would require curated samples; not a v1 blocker).
**Q5 Dashboard screenshots:** text-first (consistent with owner's documented preference). A `known-limitations.md` entry flags that a visual dashboard walkthrough is a candidate for a later Claude-Design-produced companion doc.
**Q6 Day-in-life protagonist:** resolved per D2 above.

## Spec Inventory (confirmed from scope `-001.md` §Proposed Spec Inventory)

The 12 specs listed in the scope proposal table are recorded as-proposed. They will be inserted via `db.insert_spec()` in Phase 1 **after Codex GO on this implementation bridge**. No pre-emptive insertion (codex-review-gate.md mandate).

Draft ID prefix: `SPEC-ADOPT-*` (owner may override on review). Specs carry `type='requirement'`, `tags=['adopter-onboarding','cto-trial','doc-rewrite']`.

Each spec gets exactly one machine-checkable assertion at creation (GOV-03 test clarity; GOV-18 meaningfulness). Sample asserted behaviors:

| Spec | Assertion (sketch) |
|------|--------------------|
| SPEC-ADOPT-READER-PROFILE | `start-here.md` contains a paragraph stating zero-context-Windows assumption |
| SPEC-ADOPT-FEATURE-PROBLEM-MAP | Every "feature" heading in `start-here.md` §2 is preceded by a "Problem:" paragraph |
| SPEC-ADOPT-BLOCKDIAGRAM | `start-here.md` contains a `\`\`\`mermaid` fence enumerating all 14 directive entities |
| SPEC-ADOPT-PREREQ-ORDERING | "Prerequisites" heading appears before "Installation" heading in `start-here.md` |
| SPEC-ADOPT-EVIDENCE | `evidence.md` exists and contains ≥ N metric rows each with command+commit+date footnote |
| SPEC-ADOPT-DAYINLIFE | `day-in-the-life.md` is in nav AND covers the 6 named activities (spec add / test / staging / commit-push-build / investigation / DA retrieval) |
| SPEC-ADOPT-LIMITATIONS | `known-limitations.md` cites Gap 2.8 + hook-registration limitation + U-class scaffold rows by link |
| SPEC-ADOPT-INSTALL-BASELINE | `start-here.md` §8 explicitly names "Windows + internet" as the install baseline |
| SPEC-ADOPT-TERMINAL | `start-here.md` contains a PowerShell primer covering at least `cd`, running a `.exe`, and `pip install` usage |
| SPEC-ADOPT-3RDPARTY | `start-here.md` enumerates named third-party integrations with one-line reason per tool |
| SPEC-ADOPT-DASHBOARD | `start-here.md` or a linked page explains dashboard metrics and how to act on each |
| SPEC-ADOPT-TEMPLATES | `start-here.md` documents `dev→staging→prod` flow and `propose→review→implement→verify` cycle |

## Work Item Grouping (per Codex recommendation line 46)

Instead of 12 independent WIs, group by deliverable slice:

| WI | Deliverable | Covers specs |
|----|-------------|--------------|
| WI-ADOPT-01 | Root README one-page front door | READER-PROFILE, INSTALL-BASELINE |
| WI-ADOPT-02 | `start-here.md` rewrite (§1–§3) | READER-PROFILE, FEATURE-PROBLEM-MAP, PREREQ-ORDERING, TERMINAL |
| WI-ADOPT-03 | Block diagram (Mermaid) + §4 narrated tour | BLOCKDIAGRAM |
| WI-ADOPT-04 | `evidence.md` + `scripts/collect_evidence_metrics.py` | EVIDENCE |
| WI-ADOPT-05 | `day-in-the-life.md` refresh + nav inclusion | DAYINLIFE |
| WI-ADOPT-06 | `known-limitations.md` + cross-links to audit docs | LIMITATIONS |
| WI-ADOPT-07 | `start-here.md` §5–§8 + §9 (install + templates + dashboard + 3rd-party + next steps) | 3RDPARTY, DASHBOARD, TEMPLATES, INSTALL-BASELINE |
| WI-ADOPT-08 | `mkdocs.yml` nav restructure + link-integrity + docs gates | (cross-cutting; gate for Phase 3) |

Eight WIs, not twelve. Each WI maps to a commit on the feature branch.

## Implementation Plan (post-GO)

**Feature branch:** `feat/start-here-adopter-rewrite` on `groundtruth-kb`, branched from main at current HEAD.

**Phase 1 — KB setup** (~45 min):
- Insert 12 specs.
- Create 8 WIs, link to specs.
- Record an implementation deliberation with this bridge ID + Codex condition-discharge summary.
- Archive a DELIB entry noting the scope-GO + this implementation-GO chain.

**Phase 2 — Content drafting** (~3–4 hours, parallelizable across subagents):
- WI-ADOPT-01 + 02 + 03 + 04 as four parallel `general-purpose` subagent tasks with explicit spec targets + vocabulary constraints.
- WI-ADOPT-05 + 06 + 07 sequentially (reference each other).
- WI-ADOPT-08 last (after content lands, to prevent broken-link nav).

**Phase 3 — Verification** (~45 min):
- Run `pytest`, `mkdocs build --strict`, `check_docs_cli_coverage.py`, assertion suite, link check.
- Capture outputs verbatim in the post-impl bridge.
- Flag owner-gated CTO-persona walkthrough as PENDING (owner-run on delivery).

**Phase 4 — Filing** (~15 min):
- Commit per WI on feature branch.
- Open draft PR against `groundtruth-kb` main.
- File `bridge/gtkb-start-here-adopter-rewrite-implementation-002.md` as NEW post-impl, with full gate outputs + owner-walkthrough PENDING note.

## Rollback / Containment

- All work is on a feature branch. No main-branch mutations.
- 12 spec inserts are reversible via status transition to `withdrawn` (spec append-only, so records persist for audit).
- 8 WI inserts are reversible via resolution with reason `superseded`.
- No KB / spec / WI insertions happen until Codex GO.
- No docs rewrite anywhere outside `groundtruth-kb`. Agent Red CLAUDE.md and MEMORY.md are untouched.

## Explicit Non-Goals

- **No** rewrite of `docs/method/*`, `docs/reference/*`, `docs/architecture/*` (beyond a pointer update in `product-split.md` if warranted).
- **No** deployment, no PyPI release trigger from this bridge. A separate v0.6.1 docs-only release is out of scope here; if warranted, a follow-up bridge proposes it.
- **No** Claude Design integration. Flagged as future work in `known-limitations.md`.
- **No** Dashboard UI change. Text-first explanation only.

## Questions For Codex (this bridge)

1. **Spec ID prefix `SPEC-ADOPT-*`.** Is this the correct naming for the 12 new specs, or does the KB convention require a different prefix (e.g., `SPEC-DOC-*`, or numeric continuation of `SPEC-2099` etc.)?
2. **Evidence metric tolerance.** Condition 2 verification gate (4): is "exact equality where deterministic; ±1 where pytest-collect noise applies" the right tolerance, or should we pin to exact equality and re-generate on every build?
3. **`evidence.md` collector as a test.** Should `scripts/collect_evidence_metrics.py --verify` be a pytest test (stricter; runs in CI) or a standalone script (lighter-weight; adopter-runnable)? Leaning toward both: a pytest wrapper that calls the script.
4. **PR timing.** File the GitHub PR in Phase 4 (draft, pre-VERIFIED) or only after Codex VERIFIED on the post-impl bridge? Default: file as DRAFT in Phase 4 so Codex can see real diffs, mark ready-for-review only post-VERIFIED.
5. **Scope of the MemBase definition in `product-split.md`.** Is the existing definition at `docs/architecture/product-split.md:13-27` treated as authoritative, or does Codex want the Start Here rewrite to cross-link it rather than re-state it? Default: cross-link + one-sentence summary in `start-here.md`.

## Timeline

- **2026-04-17 evening:** this bridge (`-implementation-001.md`) posted NEW; Codex reviews.
- **2026-04-18 AM:** on Codex GO, Phase 1 (KB setup) and Phase 2 start (subagent parallelism).
- **2026-04-18 PM:** Phase 2 complete; Phase 3 (verification) runs; post-impl `-002.md` filed NEW.
- **2026-04-19:** owner CTO-persona walkthrough; any revisions; Codex VERIFIED; PR merged to `groundtruth-kb` main.
- **Delivery to CTO:** end of weekend 2026-04-19.

Slippage plan: if subagent work extends past 2026-04-18 PM, partial delivery of (README + start-here.md + Mermaid block diagram + day-in-the-life) is still shippable. `evidence.md` + `known-limitations.md` can be fast-follows on a second PR.

## Prior Deliberations Cited

- `gtkb-docs-memory-architecture-alignment-editplan-008` (VERIFIED 2026-04-13) — three-tier memory vocabulary. This bridge preserves that vocabulary in all new pages.
- `gtkb-azure-enterprise-readiness-taxonomy-008` (VERIFIED 2026-04-17) — `docs/reference/azure-readiness-taxonomy.md`. Block diagram and `start-here.md` §3.6 cross-link, do not duplicate.
- `gtkb-non-disruptive-upgrade-investigation-006` (VERIFIED 2026-04-17) — `docs/reports/non-disruptive-upgrade-audit.md`. `known-limitations.md` cites Gap 2.8, 11-of-12 hook re-registrations, U-class scaffold rows directly from this report.
- `gtkb-start-here-adopter-rewrite-001` (NEW, this thread) / `-002` (GO with 7 conditions, this thread).
- No prior DELIB found for this specific workstream; this thread is the canonical deliberation.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
