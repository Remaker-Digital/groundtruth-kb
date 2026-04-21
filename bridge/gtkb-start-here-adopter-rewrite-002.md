# GO Review: GT-KB Start Here Adopter Rewrite

**Verdict:** GO with conditions
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-start-here-adopter-rewrite-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The proposed adopter-onboarding rewrite is the right scope for the CTO feedback and should proceed to implementation. The current Start Here path begins with installation prerequisites and `pip install groundtruth-kb`, which does not answer the CTO's first-order questions before setup. The proposed README + Start Here + diagram + day-in-life + evidence + limitations stack directly addresses that gap.

## Evidence

- The proposal captures the target repo and urgent CTO trial window at `bridge/gtkb-start-here-adopter-rewrite-001.md:6` and `bridge/gtkb-start-here-adopter-rewrite-001.md:7`.
- The current `docs/start-here.md` opens with technical prerequisites at `docs/start-here.md:6` and install-first flow at `docs/start-here.md:27` / `docs/start-here.md:30`.
- The current README still directs the evaluation path as "install, create a project, and run your first assertion" at `README.md:81`, which matches the reported adopter confusion.
- The proposal's in-scope deliverables cover the required new artifacts at `bridge/gtkb-start-here-adopter-rewrite-001.md:54`, with the block diagram, evidence doc, and limitations doc called out at lines 60, 62, and 63.
- `MemBase` is not actually undefined in the current docs: `docs/architecture/product-split.md:13` defines "Core Knowledge Database (MemBase)", `docs/architecture/product-split.md:15` says it is an append-only SQLite database, and `docs/architecture/product-split.md:27` identifies it as the canonical knowledge and specifications tier.
- The repo already supports Mermaid in MkDocs through `mkdocs.yml:41` and `mkdocs.yml:43`, so Mermaid is a suitable source format for the block diagram.
- The current MkDocs nav includes Start Here but not the proposed new evidence/limitations pages (`mkdocs.yml:52`, `mkdocs.yml:56`). Existing `docs/day-in-the-life.md` is also not in nav; `python -m mkdocs build --strict --site-dir _site_bridge_review` exited 0 but reported it as a page outside nav.
- Current live test count is not the same as the proposal's example number. Command run from `groundtruth-kb` at HEAD `e12aab3`: `python -m pytest --collect-only -q` collected **1249 tests**. The v0.6.0 release note still records **1209 passed** at `release-notes-0.6.0.md:84`.

## Conditions For Implementation

1. **Resolve `MemBase` before drafting the diagram.** Treat `MemBase` as the Core Knowledge Database / local SQLite `groundtruth.db` canonical spec tier, not ChromaDB and not the MEMORY.md file family. The diagram must distinguish MemBase, MEMORY.md, Deliberation Archive, and optional ChromaDB/search.

2. **Use live evidence, not proposal-era numbers.** `docs/evidence.md` must cite command, commit, date, and source for each metric. Do not copy the proposal's "1209 tests" as a current-state claim; current collection at `e12aab3` is 1249 tests, while 1209 is a v0.6.0 release-note metric.

3. **Make the docs discoverable in MkDocs.** Update `mkdocs.yml` so the new adopter-facing pages are reachable from the published docs navigation, not only from inline links. At minimum, Start Here, Day in the Life, Evidence, Known Limitations, and the executive overview/front-door path should be visible or intentionally linked from visible pages.

4. **Define the diagram rendering contract.** Mermaid is approved as the text source because the repo already supports Mermaid fences. If a committed SVG asset remains required, the implementation bridge must name the rendering tool/command or commit the SVG plus source with a short regeneration note. If MkDocs-rendered Mermaid is accepted as the "rendered" form, state that explicitly and drop the separate SVG asset requirement.

5. **Keep external install docs stable.** The adopter docs must answer ordering in plain language: Claude Code is a separate prerequisite tool; GT-KB does not include Claude Code; install/authenticate Claude Code before using the dual-agent workflow. For exact Claude Code install steps, link to the official Anthropic instructions and cite retrieval/version date rather than freezing copied steps that may drift.

6. **Split owner-gated validation from Codex verification.** The CTO-persona walkthrough is useful and should remain, but it is owner acceptance, not a machine-verifiable Codex gate. The implementation bridge should list it separately from command-based verification.

7. **Run the repo-native docs gates.** Before filing implementation for verification, run:
   - `python scripts/check_docs_cli_coverage.py`
   - `python -m mkdocs build --strict`
   - A focused link/manual check for the new README -> Start Here -> evidence/day-in-life/limitations path

## Recommendations

- Keep both README and `docs/start-here.md`. Rewrite the root README as a one-page front door and make `docs/start-here.md` the guided path. Do not create a second competing README.
- Group work items by deliverable or validation slice rather than forcing 12 independent WIs. A spec-to-section compliance matrix in the implementation bridge is more useful than excessive WI fragmentation.
- Use a hybrid evidence model: generated/reproducible metric table plus short curated interpretation. A script is worthwhile for volatile numbers such as tests, coverage, docs build, deliberation count, and bridge cycle metrics.
- The day-in-the-life protagonist is not GO-blocking. Pick a synthetic but concrete scenario during implementation, unless Mike wants an actual S299 re-narration.
- Preserve the "problem before feature" ordering throughout: basic problem, why Claude Code alone is insufficient, how each GT-KB feature answers that problem, then installation.

## Risk / Impact

Main risk is not implementation complexity; it is credibility. A CTO-facing rewrite that includes stale evidence numbers, ambiguous memory vocabulary, or hidden docs pages would recreate the same trust gap it is meant to close. The conditions above are targeted to keep the rewrite adopter-readable, verifiable, and consistent with the current GT-KB architecture vocabulary.

## Decision Needed From Owner

- Confirm whether a committed SVG asset is required, or whether Mermaid rendered by MkDocs satisfies the block-diagram requirement.
- Confirm whether the day-in-the-life scenario should be synthetic or based on an actual recent GT-KB session.

## Verification Commands Run

- `python -m pytest --collect-only -q` in `groundtruth-kb` -> 1249 tests collected, 1 ChromaDB deprecation warning.
- `python -m mkdocs build --strict --site-dir _site_bridge_review` in `groundtruth-kb` -> exit 0; reported existing pages outside nav and one existing anchor info message. Temporary `_site_bridge_review` output was removed after inspection.
- `git rev-parse --short HEAD` in `groundtruth-kb` -> `e12aab3`.
- `git ls-files templates/ | Measure-Object | Select-Object -ExpandProperty Count` in `groundtruth-kb` -> 56 tracked template files.
