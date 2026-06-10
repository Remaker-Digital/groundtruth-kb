NEW

# Bridge Convenience Verbs — `/bridge scan` and `/bridge show-thread <slug>`

bridge_kind: prime_proposal
target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", ".claude/skills/bridge/helpers/show_thread_bridge.py", ".claude/skills/bridge/SKILL.md", ".codex/skills/bridge/SKILL.md", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_show_thread_bridge.py", "groundtruth.db"]
Document: gtkb-bridge-convenience-verbs-001
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-14 UTC

## Summary

Implement two helper-backed convenience verbs in the `/gtkb-bridge` skill, addressing standing-backlog WI-3260 (P1):

1. **`/bridge scan`** — emit a structured summary of `bridge/INDEX.md` filtered by the calling harness's durable role (Prime gets NO-GO and GO entries; LO gets NEW and REVISED entries; both can see VERIFIED for context). Replaces the current ad-hoc grep+Read+regex sequences that every session performs whenever the owner says "check the bridge" or "scan".

2. **`/bridge show-thread <slug>`** — load the full version chain for a named bridge thread (all `<slug>-NNN.md` files concatenated with version-status headers) so context can be loaded for review/revision without per-version Read calls. Replaces the manual N-Read-call sequence the protocol's "read the full version chain" obligation requires.

Both verbs follow the helper-mediated pattern established by `gtkb-bridge-skill-unified-001` (VERIFIED -006) and reused by `gtkb-bridge-impl-report-skill-001` (VERIFIED -004): Python helper module under `.claude/skills/bridge/helpers/`, documented in `.claude/skills/bridge/SKILL.md` Operations table, regenerated to `.codex/skills/bridge/SKILL.md` for harness parity, covered by `platform_tests/scripts/test_*.py` unit tests.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical for queue state. Both helpers read INDEX as the authoritative input; neither mutates INDEX or any prior bridge file. Append-only invariant unaffected.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Every relevant governing specification cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Each linked spec has at least one derived test in `## Specification-Derived Verification Plan` below.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Owner directive that repetitive plumbing performed by AI is a defect. This work converts two repetitive bridge-probing patterns (INDEX scanning by role, per-thread version-chain loading) into deterministic helper invocations, reducing per-session token cost and inconsistency.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — All target paths are in-root under `E:\GT-KB`. Helper files at `E:\GT-KB\.claude\skills\bridge\helpers\`, tests at `E:\GT-KB\platform_tests\scripts\`, skill-doc at `E:\GT-KB\.claude\skills\bridge\SKILL.md`. No target path resides under the `applications/` tree; this is GT-KB platform infrastructure work.
- `GOV-08` — Updates to `work_items` rows go through the canonical Python API (`KnowledgeDB.update_work_item()`). Only WI-3260's terminal-state mutation is in scope.
- `ADR-0001` — MemBase append-only versioning preserved: WI-3260 receives one new versioned row on completion.
- `GOV-19` (Outside-in testing) — Helper tests exercise the public verb surface and observed output, not internal private functions.
- `GOV-15` — WI-3260's `origin` is `new` (a non-defect, non-regression origin), so the test-fix gate's owner-approval flag is outside scope. Owner approval is recorded via the chat directive cited in `## Owner Decisions / Input` below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — Output of new helpers is structured data; cross-references preserved.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — Traceability across artifacts, tests, reports.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — Helper output exposes the `verified` / `resolved` terminal states it filters against.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (owner_conversation, owner_decision). Authoritative motivation: "repetitive work performed by AI is a defect; deterministic plumbing belongs in services, not in sessions." This proposal is a direct application of that principle to bridge-state probing.
- `DELIB-1564` — `gtkb-bridge-skill-unified-001` GO (Codex Loyal Opposition Review). Established the helper-mediated `/bridge` verb pattern that this proposal extends.
- `DELIB-1565` — `gtkb-bridge-skill-unified-001` Slice 1 + Slice 2 verification. Documented the helper-discipline conventions (helper under `.claude/skills/bridge/helpers/`, canonical skill body at `.claude/skills/bridge/SKILL.md`, Codex adapter regenerated via `scripts/generate_codex_skill_adapters.py`).
- `DELIB-1089` — Bridge Scan Role Authority GOV Failure Correction. Relevant context for the role-filtered scan output (Prime acts on NO-GO/GO; LO acts on NEW/REVISED) per `.claude/rules/file-bridge-protocol.md`.
- `bridge/gtkb-bridge-skill-unified-001-006.md` — VERIFIED post-impl report; latest canonical SKILL.md structure.
- `bridge/gtkb-bridge-impl-report-skill-001-004.md` — VERIFIED post-impl report; helper module organization precedent (the same directory and naming convention this proposal reuses).
- `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-008.md` — VERIFIED 2026-05-14; closed the prior bridge thread in this session. Lesson learned recorded in that thread's `-005` Lesson Learned section: do not edit GO'd proposals in place to satisfy authorization-parser format issues. This proposal applies that lesson by getting the parser format right at filing time.

## Owner Decisions / Input

This proposal proceeds under the owner's explicit chat directive on 2026-05-14:

- **Earlier owner AUQ (2026-05-13, this session):** "Which standing-backlog item should this session advance?" → Answer: "Hygiene: close 6 stale WIs (Recommended)" — completed at `gtkb-completed-bridge-wi-hygiene-2026-05-13` VERIFIED `-008`, committed as `d1448d43`.
- **Earlier owner delegation (2026-05-14, this session):** "Please continue. Parallelize work whenever possible and continue by selecting priority backlog items if/when you become idle." This delegated next-backlog-pick authority to Prime Builder for the remainder of the session.
- **Current owner directive (2026-05-14, this session, immediately preceding this proposal):** "proceed with WI-3260" — explicit confirmation of the WI-3260 selection that I had previously surveyed and presented as the prep target (P1, "Bridge convenience verbs: `/bridge show-thread <slug>` and `/bridge scan`", origin=`new`, source_spec_id=`None`).
- **detected_via:** chat directive (not AUQ). The chat directive is a confirmation of a previously-surveyed and previously-briefed Prime Builder selection, operating under the prior AUQ-delegated authority. No new AUQ was requested or generated by this proposal preparation; the owner's confirmation is the operative approval.

This is `origin=new` work in the standing backlog. `GOV-15`'s defect/regression gate does not fire. No formal-artifact-approval packet is required (this work creates Python helpers + tests + edits to a non-protected `.claude/skills/bridge/SKILL.md` — operational platform infrastructure).

## Requirement Sufficiency

**Existing requirements sufficient.** No new requirement, specification, or candidate-requirement creation is needed. WI-3260 is an in-backlog work item with clear scope from its description. The helper-mediated pattern's requirements are inherited from the VERIFIED `gtkb-bridge-skill-unified-001` and `gtkb-bridge-impl-report-skill-001` precedents. `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` is the active governing decision; no new principle is being introduced.

## Plan

### Helper modules

**`.claude/skills/bridge/helpers/scan_bridge.py`** — new module, ~150 LOC. Exports:

- `scan(role: Literal["prime-builder", "loyal-opposition"], index_path: Path | None = None) -> dict` — returns a structured dict with keys `actionable` (list of thread entries the role should act on), `terminal_verified` (recent VERIFIED threads for context), `summary` (counts by status), `generated_at` (ISO timestamp).
- Each `actionable` entry is `{document, latest_status, latest_path, version_chain (list of (status, path) tuples)}`.
- Filter rules (per `.claude/rules/file-bridge-protocol.md`):
  - Prime acts on `NO-GO` (revise) and latest `GO` (implement).
  - LO acts on `NEW` and `REVISED`.
  - `VERIFIED` is terminal for both; included in `terminal_verified` for context, not in `actionable`.
- Reads `bridge/INDEX.md` line-by-line; parses `Document:` blocks; tracks first status line per block as latest.
- No mutations. Stateless. Idempotent.

**`.claude/skills/bridge/helpers/show_thread_bridge.py`** — new module, ~100 LOC. Exports:

- `show(slug: str, bridge_dir: Path | None = None) -> dict` — returns `{slug, document_entry (INDEX entry text), versions (list of {version, status, path, head_first_line, content_preview})}`.
- Resolves all `bridge/<slug>-*.md` files; sorts by zero-padded version number; reads each file's first line (verdict) plus head-of-file preview (up to ~200 lines).
- Cross-references INDEX entry's status chain against on-disk files (flags any divergence).
- No mutations. Stateless.

### Skill-doc updates

**`.claude/skills/bridge/SKILL.md`** — append two subsections under existing `## Operations`:

- Under existing `### Scan` subsection: add a note that `python .claude/skills/bridge/helpers/scan_bridge.py --role <role>` invokes the deterministic helper.
- Under existing `### Status` subsection: add a reference to `python .claude/skills/bridge/helpers/show_thread_bridge.py <slug>` as the canonical thread-loading invocation.
- Update the existing "Companion per-action skills" table footer to mention the new helpers exist (no new sibling SKILL.md needed; these are helper invocations under the umbrella `gtkb-bridge` skill).

**`.codex/skills/bridge/SKILL.md`** — regenerated from the Claude canonical via `python scripts/generate_codex_skill_adapters.py`. No manual edit; the script handles the adapter regeneration.

### Tests

**`platform_tests/scripts/test_scan_bridge.py`** — unit tests for `scan_bridge.py`:

- T1: Empty INDEX yields empty `actionable` and zero counts.
- T2: Single Document with latest `NEW:` → LO sees in actionable; Prime sees nothing.
- T3: Single Document with latest `GO:` → Prime sees in actionable; LO sees nothing.
- T4: Single Document with latest `NO-GO:` → Prime sees in actionable; LO sees nothing.
- T5: Single Document with latest `REVISED:` → LO sees in actionable; Prime sees nothing.
- T6: Single Document with latest `VERIFIED:` → both see in terminal_verified; neither in actionable.
- T7: Mixed INDEX (5 documents at varying latest statuses) — Prime and LO see correct partitioning.
- T8: INDEX with comment header is correctly skipped.

**`platform_tests/scripts/test_show_thread_bridge.py`** — unit tests for `show_thread_bridge.py`:

- T1: Slug with no matching files → returns empty `versions` list and a not-found indicator.
- T2: Slug with `-001.md` through `-003.md` on disk → returns 3 versions sorted by version number; each has first-line verdict.
- T3: Slug with version-numbered files using compound suffix (e.g., `-001-002.md` for sub-versioned threads) — handled correctly.
- T4: INDEX cross-reference detects on-disk files missing from INDEX entry (drift warning).
- T5: Content preview is bounded (≤ 200 lines per version) so output doesn't balloon for long bodies.

### MemBase update

After implementation lands and verification passes, file post-impl report. Within the implementation script under the auth packet, call `KnowledgeDB.update_work_item(id='WI-3260', resolution_status='resolved', stage='resolved', changed_by='prime-builder/claude-code', change_reason='<bridge-slug>: implementation complete and Codex VERIFIED at <verdict-file>.')`.

## Specification-Derived Verification Plan

Verification is empirical, derived from the linked specifications. Each test runs as part of the post-implementation evidence in the eventual `-NNN.md` post-impl report.

| Spec | Verification Step | Command (read-only) |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run `scan_bridge.scan(role="prime-builder")` against the live `bridge/INDEX.md`; assert latest-status filter logic matches the manual rule (Prime: NO-GO + latest GO; LO: NEW + REVISED). | `python .claude/skills/bridge/helpers/scan_bridge.py --role prime-builder --format json` and validate keys + filtering |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the test suite covering both helpers; report PASS counts. | `python -m pytest platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_show_thread_bridge.py -v` |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Show that the deterministic helper produces the same output as the manual procedure on a representative INDEX. | Side-by-side diff of helper JSON vs. hand-built reference output (recorded in post-impl report). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm every modified or created file path is in-root under `E:\GT-KB` and outside `applications/`. | `git diff --stat HEAD~1 HEAD` after commit; manually inspect the path list. |
| `GOV-08` | After WI-3260's terminal-state update via `update_work_item()`, query the latest version: `resolution_status='resolved'`, `stage='resolved'`. | `python -c "import sqlite3; db=sqlite3.connect('file:groundtruth.db?mode=ro', uri=True); print(db.execute('SELECT w.id, w.resolution_status, w.stage FROM work_items w INNER JOIN (SELECT id AS xid, MAX(version) AS mv FROM work_items GROUP BY id) l ON w.id=l.xid AND w.version=l.mv WHERE w.id=?', ('WI-3260',)).fetchone())"` |
| `ADR-0001` | Confirm append-only on WI-3260: row count equals max version after the update. | `python -c "import sqlite3; db=sqlite3.connect('file:groundtruth.db?mode=ro', uri=True); print(db.execute('SELECT COUNT(*), MAX(version) FROM work_items WHERE id=?', ('WI-3260',)).fetchone())"` |
| `GOV-19` (outside-in) | Tests exercise public helper-function signatures and JSON output structure, not internal private functions. | Inspect test file: every test imports the public function (`scan`, `show`) and asserts on its returned dict structure. |

## Acceptance Criteria

1. `.claude/skills/bridge/helpers/scan_bridge.py` exists and exposes a `scan(role, index_path=None)` function returning the documented dict shape.
2. `.claude/skills/bridge/helpers/show_thread_bridge.py` exists and exposes a `show(slug, bridge_dir=None)` function returning the documented dict shape.
3. `.claude/skills/bridge/SKILL.md` Operations table references both new helper invocations under `### Scan` and `### Status` subsections respectively.
4. `.codex/skills/bridge/SKILL.md` regenerated via `scripts/generate_codex_skill_adapters.py`; canonical source sha256 in the generated adapter header matches the Claude-side canonical.
5. `platform_tests/scripts/test_scan_bridge.py` and `platform_tests/scripts/test_show_thread_bridge.py` exist; all tests PASS under `pytest`.
6. WI-3260 in MemBase has `resolution_status='resolved'`, `stage='resolved'`, `changed_by='prime-builder/claude-code'` in its latest version.
7. Append-only invariant preserved on WI-3260: rows count equals max version.
8. Every modified or created file path is in-root under `E:\GT-KB` and outside `applications/`.

## Risks and Rollback

- **Risk: helper output format drifts from manual procedure.** If `scan_bridge.scan()` filters differently from the SKILL.md-documented manual procedure, agents using the helper get different actionable lists than agents reading INDEX manually. **Mitigation:** Tests T2-T6 mechanically lock the filter rules to the SKILL.md text. Any future filter-rule change must update tests and SKILL.md atomically.
- **Risk: `show_thread_bridge` returns too much content and balloons the calling session's context.** **Mitigation:** Per-version content preview is bounded at ~200 lines; full file content is not loaded. Test T5 enforces this.
- **Risk: Codex-side adapter drifts.** If the regeneration step (`scripts/generate_codex_skill_adapters.py`) is skipped, Codex sees stale SKILL.md without the new verbs. **Mitigation:** Acceptance criterion 4 requires the regenerated adapter's sha256 header to match the canonical; verification step inspects this.
- **Rollback:** All changes are additive (new helper files, additive SKILL.md edits, new tests, one new WI-3260 versioned row). Rollback is `git revert <commit-sha>` plus an append-only WI-3260 row setting `resolution_status='open'` with a rollback-reason `change_reason`. The append-only contract means no destructive operations are needed.

## Audit Evidence

- Bridge filing: this proposal is filed at `bridge/gtkb-bridge-convenience-verbs-001.md` with a `Document: gtkb-bridge-convenience-verbs-001` + `NEW:` entry inserted at the top of `bridge/INDEX.md` (after the comment header block). No prior bridge file or INDEX entry is deleted or rewritten; the INDEX update is additive.
- WI-3260 origin probe (read-only): `origin='new'`, `priority='P1'`, `resolution_status='open'`, `stage='backlogged'`, `component='groundtruth-kb'`, `source_spec_id=None`. Title: "Bridge convenience verbs: /bridge show-thread <slug> and /bridge scan". Description names `WI-3257` and `WI-3258` as related (now both RESOLVED).
- Sibling thread inventory (read-only): `gtkb-bridge-skill-unified-001` is VERIFIED at `-006`; `gtkb-bridge-impl-report-skill-001` is VERIFIED at `-004`. Both established the helper-mediated pattern this proposal reuses.
- Owner directive: chat-line "proceed with WI-3260" from owner on 2026-05-14. No new AUQ generated; operating under earlier session delegation.
- In-root placement: every target path is in-root under `E:\GT-KB`. No path resides under `applications/**`. Bridge file at `E:\GT-KB\bridge\gtkb-bridge-convenience-verbs-001.md`.
- formal-artifact-approval — outside scope. Target files are operational platform infrastructure (Python helpers, tests, non-protected SKILL.md). No GOV/ADR/DCL/SPEC/PB mutations.

## Recommended Commit Type

`feat:` — net-new capability (two new bridge convenience verbs). Adds Python helper modules, tests, and skill-doc updates. Conventional Commits classification matches the diff stat (new files + new test coverage + new public verb surface).

## Implementation Sequence (After Codex GO)

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-convenience-verbs-001` to mint the local authorization packet.
2. Implement `.claude/skills/bridge/helpers/scan_bridge.py`.
3. Implement `.claude/skills/bridge/helpers/show_thread_bridge.py`.
4. Write `platform_tests/scripts/test_scan_bridge.py` and `platform_tests/scripts/test_show_thread_bridge.py`; iterate implementations until all tests PASS.
5. Edit `.claude/skills/bridge/SKILL.md` to add helper invocations under existing `### Scan` and `### Status` subsections.
6. Regenerate `.codex/skills/bridge/SKILL.md` via `python scripts/generate_codex_skill_adapters.py`; confirm header sha256 matches.
7. Run pytest one more time as defense-in-depth.
8. Apply the WI-3260 terminal-state mutation via `KnowledgeDB.update_work_item(...)`.
9. File post-impl report as `bridge/gtkb-bridge-convenience-verbs-001-NNN.md` with `NEW` status (next version after Codex's GO).
10. After Codex VERIFIED, commit with `feat:` per § Recommended Commit Type.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
