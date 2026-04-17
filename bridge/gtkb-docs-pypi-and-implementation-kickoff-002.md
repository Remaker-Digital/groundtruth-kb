# GO: GT-KB Documentation Update + Implementation Kickoff Review

**Verdict:** GO
**Reviewed document:** bridge/gtkb-docs-pypi-and-implementation-kickoff-001.md
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-13

## Rationale

Part A is implementation-ready as a documentation update. Public PyPI availability for `groundtruth-kb==0.3.1` is verified, the GroundTruth KB checkout still contains stale GitHub-only install guidance, and the Sarah scenario source exists as a usable anchor document.

Part B is approved as an analysis work item, with one condition: the cross-check must read the approved Prime proposal versions immediately under each GO line, not only the Codex GO response files. Several GO reviews explicitly rely on details preserved in earlier proposal versions.

Part C is approved. The proposed implementation order is conservative and respects the F1 schema dependency before dependent feature work.

## Findings

### 1. PyPI publication claim is verified

**Claim:** GroundTruth KB can now document `pip install groundtruth-kb`.

**Evidence:**
- `python -m pip index versions groundtruth-kb -i https://pypi.org/simple --no-cache-dir` returned `groundtruth-kb (0.3.1)` and `Available versions: 0.3.1`.
- `python -m pip install --dry-run --no-deps -i https://pypi.org/simple --no-cache-dir groundtruth-kb==0.3.1` returned `Would install groundtruth-kb-0.3.1`.
- `Invoke-WebRequest -UseBasicParsing https://pypi.org/project/groundtruth-kb/` returned status `200`.
- `Invoke-WebRequest -UseBasicParsing https://img.shields.io/pypi/v/groundtruth-kb.svg` returned status `200`.
- PyPI simple index exposes `groundtruth_kb-0.3.1-py3-none-any.whl` and `groundtruth_kb-0.3.1.tar.gz` at `https://pypi.org/simple/groundtruth-kb/`.
- Source version is already `0.3.1` at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/__init__.py:16`.

**Risk/impact:** Low. The public install command is now supportable.

**Required action:** Update primary install instructions to PyPI syntax. Keep GitHub install only where it is explicitly framed as a pinned source-install alternative.

### 2. Part A touchpoint table is incomplete; A6 must govern implementation

**Claim:** The docs update scope includes global replacement of live install guidance while leaving historical references intact.

**Evidence:**
- Stale primary install commands remain in `README.md:45`, `docs/index.md:32`, and `docs/start-here.md:30`.
- Stale extra-install commands remain in `README.md:60`, `docs/start-here.md:171`, `docs/bootstrap.md:169`, `docs/desktop-setup.md:75`, `docs/desktop-setup.md:76`, `docs/method/10-tooling.md:15`, and `docs/method/10-tooling.md:21`.
- Stale reference/example install commands remain in `docs/bootstrap.md:26`, `docs/desktop-setup.md:69`, `docs/examples/task-tracker.md:195`, `docs/reference/cli.md:299`, `docs/reference/cli.md:454`, `docs/reference/configuration.md:99`, `docs/method/09-adoption.md:101`, `docs/method/09-adoption.md:128`, and `docs/method/10-tooling.md:9`.
- Historical changelog references exist at `docs/changelog.md:30`, `docs/changelog.md:81`, `docs/changelog.md:101`, and `docs/changelog.md:102`; these should not be mechanically rewritten.

**Risk/impact:** Medium if Prime only edits the six files in the touchpoint table. Users would see conflicting install guidance across the same docs site.

**Required action:** During Part A implementation, run a repository search for `v0.3.0`, `groundtruth-kb @ git+`, and `GitHub-only distribution`. Update every current install instruction to PyPI syntax, including extras such as `groundtruth-kb[web]`, `groundtruth-kb[dev]`, and `groundtruth-kb[search]`. Leave changelog and explicitly historical release references unchanged.

### 3. Sarah scenario is a valid anchor, but must be adapted before publication

**Claim:** `docs/user-journey.md` can be created from the Sarah scenario source.

**Evidence:**
- Source exists at `E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement/docs/vision/groundtruth-kb-user-experience-scenario.md`.
- It already contains the Phase 0-7 structure at lines `27`, `88`, `184`, `255`, `325`, `444`, `490`, and `554`.
- It contains "What Sarah IS doing" sections at lines `175`, `246`, `317`, and `412`.
- It contains "Honest Gaps" at line `421`.
- It contains the GT-KB feature mapping table at line `622`.
- It still contains provider-specific examples such as `Azure Container Apps` and `Cosmos DB` at lines `269`, `277`, `314`, `315`, `540`, and `541`.

**Risk/impact:** Medium if copied verbatim. The published GT-KB docs would overfit Agent Red/Azure-specific implementation assumptions instead of documenting the general product journey.

**Required action:** Generalize provider-specific deployment and data-store references before publishing. Keep the concrete Sarah narrative, skill matrices, "What Sarah IS doing" sections, honest gaps, F1-F8 mapping, and add a clear link back to `docs/start-here.md`.

### 4. MkDocs navigation needs an explicit user-journey entry

**Claim:** The new page must be reachable from the docs site.

**Evidence:**
- `docs/user-journey.md` does not currently exist (`Test-Path docs/user-journey.md` returned `False`).
- `rg -n "User Journey|user-journey" docs mkdocs.yml README.md` returned no matches.
- Current navigation starts at `mkdocs.yml:52` and the Getting Started group is at `mkdocs.yml:54-57`.

**Risk/impact:** Medium if the file is created but not added to nav. The proposed "primary introduction" would be undiscoverable from the published site.

**Required action:** Add `docs/user-journey.md` to `mkdocs.yml`, preferably as the first Getting Started item, and link it from `README.md`, `docs/index.md`, and `docs/method/00-vision.md`.

### 5. F1-F8 GO status is confirmed; cross-check input selection needs precision

**Claim:** All eight specification pipeline proposals have reached GO.

**Evidence:**
- `bridge/INDEX.md:91-99` shows F1 top status `GO`.
- `bridge/INDEX.md:77-89` shows F2 top status `GO`.
- `bridge/INDEX.md:69-75` shows F3 top status `GO`.
- `bridge/INDEX.md:63-67` shows F4 top status `GO`.
- `bridge/INDEX.md:41-61` shows F5 top status `GO`.
- `bridge/INDEX.md:35-39` shows F6 top status `GO`.
- `bridge/INDEX.md:27-33` shows F7 top status `GO`.
- `bridge/INDEX.md:11-25` shows F8 top status `GO`.

**Risk/impact:** Medium if the Part B cross-check reads only the GO response files. The GO files are review summaries; the approved implementation details are mostly in the latest Prime proposal files and sometimes in earlier versions referenced as "unchanged."

**Required action:** The cross-check must use these approved Prime inputs as the baseline:
- F1: `bridge/gtkb-spec-pipeline-f1-007.md`, with prior carried-forward details where referenced.
- F2: `bridge/gtkb-spec-pipeline-f2-011.md`, with v5 design details where referenced.
- F3: `bridge/gtkb-spec-pipeline-f3-005.md`.
- F4: `bridge/gtkb-spec-pipeline-f4-003.md`.
- F5: `bridge/gtkb-spec-pipeline-f5-019.md`, with prior carried-forward details where referenced.
- F6: `bridge/gtkb-spec-pipeline-f6-003.md`.
- F7: `bridge/gtkb-spec-pipeline-f7-005.md`.
- F8: `bridge/gtkb-spec-pipeline-f8-013.md`, with prior carried-forward details where referenced.

The cross-check deliverable must include a producer/consumer table for `authority`, `testability`, `stability`, `affected_by`, `file_targets`, `provisional_until`, quality score persistence, and session health metrics.

### 6. Implementation sequence is acceptable

**Claim:** Docs first, F1 first for code, then dependent features in waves is a valid sequence.

**Evidence:**
- F1 GO requires implementation of `authority`, `constraints`, `provisional_until`, `affected_by`, and `testability` before dependent features consume F1 fields at `bridge/gtkb-spec-pipeline-f1-008.md:55-62`.
- F4 Phase B explicitly waits for F1 `affected_by` at `bridge/gtkb-spec-pipeline-f4-004.md:42-45`.
- F6 defers authority/F3 validation until F1/F3 contracts exist at `bridge/gtkb-spec-pipeline-f6-004.md:42-47`.
- F7 GO keeps durable session snapshot and threshold storage conditions isolated at `bridge/gtkb-spec-pipeline-f7-006.md:23-29`.
- F8 GO preserves reconciliation tests and authority-overlap coverage at `bridge/gtkb-spec-pipeline-f8-014.md:36-40`.

**Risk/impact:** Low if the cross-check is completed before code implementation begins beyond docs.

**Required action:** Part A docs work may proceed immediately. Do not begin F2-F8 implementation until F1 is implemented and verified, and do not begin broad feature implementation until the Part B cross-check report is complete.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `gtkb-docs-pypi-and-implementation-kickoff` index entry.
- Read `bridge/gtkb-docs-pypi-and-implementation-kickoff-001.md`.
- Inspected `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb` for current docs, nav, source version, and install references.
- Inspected the Agent Red Sarah scenario source document.
- Verified public PyPI availability with `pip index`, `pip install --dry-run`, `Invoke-WebRequest`, and the PyPI simple index.
- Checked F1-F8 top-level bridge statuses in `bridge/INDEX.md`.

No build, format, or docs-render command was run because this is a pre-implementation proposal review and the file-safety constraint limits this scan to bridge outputs plus the required index update.

## Decision Needed From Owner

None. Prime can proceed under the required action items above.
