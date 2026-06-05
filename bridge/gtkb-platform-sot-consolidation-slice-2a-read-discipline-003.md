REVISED

# Slice 2A: Read-Discipline — REVISED-2 addressing Codex NO-GO -002 (F0 target_paths shape, F1 harness-specific hook contract)

bridge_kind: implementation_proposal
Document: gtkb-platform-sot-consolidation-slice-2a-read-discipline
Version: 003
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Parent umbrella: bridge/gtkb-platform-sot-consolidation-umbrella-008.md (GO)
Sibling: bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md (VERIFIED)
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE
Work Item: WI-4340
Secondary Work Item: WI-4343

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: aa899d25-f289-48c2-8583-812e53973e98
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session, dispatched via REVISED chip from prior session 56a13045-... (skip-own rule)

## target_paths

- `groundtruth.db`
- `.groundtruth/formal-artifact-approvals/2026-06-05-GOV-SOURCE-OF-TRUTH-FRESHNESS-001-v2.json`
- `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-SOT-REGISTRY-RECORD-SCHEMA-001-v2.json`
- `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-SOT-READ-HOOK-CONTRACT-001.json`
- `.groundtruth/formal-artifact-approvals/2026-06-05-RULE-sot-read-discipline.json`
- `.claude/rules/sot-read-discipline.md`
- `.claude/hooks/sot-read-discipline.py`
- `.claude/settings.json`
- `.codex/hooks.json`
- `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py`
- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py`
- `platform_tests/scripts/test_sot_read_discipline_hook.py`
- `platform_tests/scripts/test_check_sot_read_discipline.py`

requires_verification: true
implementation_scope: implementation

## What changed in REVISED-2 vs -001

This revision addresses BOTH P1 findings in Codex NO-GO `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-002.md`:

- **F0 fix (target_paths parser-consumable shape).** The `target_paths:` bullet-list form in -001 was not consumable by `scripts/implementation_authorization.py:extract_target_paths` — the `TARGET_PATHS_RE` regex requires an inline JSON list (single-line) after the colon, and the heading-fallback requires backtick-wrapped paths in a `## target_paths` or `## Files Expected To Change` section. REVISED-2 uses the `## target_paths` heading-section form with backtick-wrapped paths; `extract_target_paths` will accept it. The renamed Codex hook path (see F1 below) is reflected.

- **F1 fix (harness-specific read hook contract).** Codex's live hook surface in this workspace is `Bash`/`apply_patch` (per `.claude/hooks/lo-file-safety-gate.py:755-757` and `.codex/hooks.json` PreToolUse matchers — all `"Bash"` or `"apply_patch"`, none `"Read"`/`"Grep"`/`"Glob"`). A Codex registration that only asserts `Read/Grep/Glob` parity would create a non-intercepting hook — the false-green case that directly undermines this slice's purpose. REVISED-2 rewrites `DCL-SOT-READ-HOOK-CONTRACT-001` to a **two-surface harness-specific contract**: Claude-side intercepts Read/Grep/Glob tool-call payloads; Codex-side intercepts Bash payloads with command parsing for `Get-Content`, `Select-String`, `Get-ChildItem` (incl. `-Recurse`), `gc`, `gci`, `cat`, `rg`, and `grep`. Implementation follows the existing `*-bash-adapter.py` precedent (canonical hook payload-dispatches by `tool_name`; thin Codex adapter pipes stdin via subprocess with `GTKB_HARNESS_NAME=codex`). Doctor `_check_sot_read_discipline` is rewritten to verify **effective matcher coverage** (asserts Codex registration is the Bash adapter, not an unsupported Read/Grep/Glob matcher; asserts Claude registration matcher contains Read, Grep, AND Glob; asserts adapter command is present). Test suite gains Codex-shaped fixtures.

Codex parity is RETAINED in this slice (not deferred to WI-4351) because the falsifying class identified by `DELIB-20260670` (always-loaded and shell-readable substitutes) is exactly the Codex-shell-read attack surface; deferring it would leave the highest-risk substitute path uncovered after Slice 2A reports VERIFIED.

All other sections — Why this proposal, Specification Links, Requirement Sufficiency, Owner Decisions / Input, Acceptance Criteria (renumbered minor edits), Phased Implementation Plan (Phase 3 substantively rewritten; other phases carried forward), Risk and Rollback, Pre-Filing Preflight Subsection — carry forward from -001 with the harness-specific contract substituted everywhere `Read/Grep/Glob` previously appeared as a generic three-tool model.

## Why this proposal

The umbrella `gtkb-platform-sot-consolidation-umbrella` GO at -008 authorizes the 9-slice sequence and absorbed the withdrawn `PROJECT-GTKB-AGENT-SOT-READ-DISCIPLINE`'s 16-AUQ scope (`DELIB-20260672`) as Slice 2A. This is the Read-Discipline child bridge — the mechanical anti-substitution discipline that makes the SoT registry from Slice 1 actually defend the canonical paths against agent-side aliasing.

Slice 1 (`bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md` VERIFIED) inserted `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` and built the `gt registry` CLI + MemBase `sot_artifacts` table + doctor `_check_sot_registry_completeness` at WARN. Slice 2A extends the SCHEMA with a `forbidden_substitutes` metadata column, adds a harness-specific read-interception hook that blocks reads against any registered forbidden_substitute path with guidance toward the canonical SoT, adds a `.claude/rules/sot-read-discipline.md` rule file giving the discipline narrative authority, and adds a doctor check that asserts effective hook coverage on both Claude and Codex sides.

Primary tracking WI is WI-4340 (insert read-discipline specs); secondary is WI-4343 (doctor `_check_sot_read_discipline`).

## Summary

Three governance mutations + four operational mutations + three tests:

**Governance (3 formal-artifact-approval packets required at execution time):**

- **`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v1 → v2** — extends with read-discipline clauses: (a) every SoT path in the registry MUST be reachable through its canonical reader/CLI; (b) agent-side reads MUST NOT substitute a non-canonical alias when the canonical path is registered; (c) the registry's `forbidden_substitutes` column is the mechanical floor; (d) read interception MUST cover the live read-surface for each harness (Claude tool events for Read/Grep/Glob; Codex shell-command events for read/search verbs).
- **`DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v1 → v2** — adds optional `forbidden_substitutes: list[str]` column to the per-record schema. Empty/missing = no aliasing restrictions. Non-empty = listed paths trigger the read hook.
- **`DCL-SOT-READ-HOOK-CONTRACT-001` v1 (NEW)** — two-surface harness-specific hook contract:
  - **Claude surface:** PreToolUse hook fires on `tool_name ∈ {Read, Grep, Glob}`; reads target path(s) from `tool_input.file_path` (Read), `tool_input.path` (Grep), or `tool_input.pattern` (Glob); normalizes; consults the registry's `forbidden_substitutes` list; returns `{"decision": "block", "reason": "..."}` with canonical-path guidance on match. Claude registers matcher `"Read|Grep|Glob"` in PreToolUse.
  - **Codex surface:** PreToolUse hook fires on `tool_name == "Bash"`; parses the `tool_input.command` string for known read/search verbs (`Get-Content`, `Select-String`, `Get-ChildItem` incl. `-Recurse`/`-Filter`, aliases `gc`/`gci`/`cat`, `rg`, `grep`); extracts path/glob arguments via per-verb extractors; normalizes; consults the same registry; blocks on match with the same canonical-path guidance. Codex registers matcher `"Bash"` in PreToolUse pointing at a thin adapter at `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py` that pipes stdin via subprocess into the canonical Claude-side hook (the `lo-file-safety-gate-bash-adapter.py` precedent) with `GTKB_HARNESS_NAME=codex` env override.
  - **Single canonical hook:** the canonical hook at `.claude/hooks/sot-read-discipline.py` payload-dispatches on `tool_name` and contains both branches. The Codex adapter is the only Codex-side file; there is no duplicate Codex hook implementation.
  - **Effective-coverage contract:** doctor MUST assert effective coverage — not just hook command string presence — by checking matcher names match each harness's registered surface (Claude: matcher contains Read AND Grep AND Glob; Codex: matcher is Bash and command resolves to the adapter).

**Operational (one canonical hook + one Codex adapter + one rule + one doctor extension + one config seed):**

- **`.claude/hooks/sot-read-discipline.py`** (new) — canonical Python hook. Payload-dispatches on `tool_name`:
  - Claude branch (Read/Grep/Glob): extract path/pattern from `tool_input`; normalize; check forbidden_substitutes; block on match.
  - Codex branch (Bash): parse `tool_input.command` for the read/search verb set above; extract path arguments; normalize; check forbidden_substitutes; block on match.
  - Reads registry projection from MemBase via `groundtruth_kb.project.sot_registry.load_projection` (NOT TOML — projection is canonical per `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`).
- **`.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py`** (new) — thin Codex adapter following the `lo-file-safety-gate-bash-adapter.py` precedent: pipes stdin via `subprocess.run` into the canonical hook with `GTKB_HARNESS_NAME=codex`, `GTKB_HARNESS_ID=A` env, returns the canonical exit code.
- **`.claude/rules/sot-read-discipline.md`** (new protected narrative) — discipline rule citing `DCL-SOT-READ-HOOK-CONTRACT-001`, listing the two-surface runtime behavior, the bypass path (explicit owner authorization), and the historical motivation (the agent-side fragmentation evidence in `DELIB-20260673` plus the falsifying-class evidence in `DELIB-20260670`).
- **`groundtruth_kb.project.doctor._check_sot_read_discipline`** (new) — 4-layer doctor check:
  1. Canonical hook file exists at `.claude/hooks/sot-read-discipline.py`.
  2. Codex adapter exists at `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py`.
  3. Claude registration: `.claude/settings.json` PreToolUse contains an entry whose matcher string includes `Read` AND `Grep` AND `Glob`, and whose command resolves to the canonical hook.
  4. Codex registration: `.codex/hooks.json` PreToolUse contains an entry with matcher `"Bash"` whose command resolves to the adapter (NOT a Read/Grep/Glob matcher — explicit anti-false-green check that fails with a guidance message if Codex registration uses unsupported tool-event names).
  5. Registry referential integrity: every `forbidden_substitutes` entry references a real `path` in the same registry record.
  Severity WARN initially per Slice 2A scope; promotion to FAIL is a Slice 2B candidate.
- **`config/registry/sot-artifacts.toml`** — populate `forbidden_substitutes` on the existing entries identified by `DELIB-20260670` (manual-triage survey of 8 forbidden-substitute candidates). Initial population is conservative; downstream slices may extend.

**Tests:**

- `platform_tests/scripts/test_sot_read_discipline_hook.py` — exercises the canonical hook against BOTH harness-shaped fixtures:
  - **Claude-shape fixtures:** `tool_name=Read` + `file_path=<forbidden>` → block; `tool_name=Grep` + `path=<forbidden>` → block; `tool_name=Glob` + `pattern=<forbidden>/**` → block; `tool_name=Read` + `file_path=<allowed>` → no block.
  - **Codex-shape fixtures:** `tool_name=Bash` + `command="Get-Content <forbidden>"` → block; `command="Select-String -Path <forbidden> -Pattern X"` → block; `command="Get-ChildItem -Path <forbidden> -Recurse"` → block; `command="gc <forbidden>"` → block (PowerShell alias for Get-Content); `command="cat <forbidden>"` → block; `command="rg pattern <forbidden>"` → block; `command="grep pattern <forbidden>"` → block; `command="Get-Content <allowed>"` → no block (non-forbidden target).
  - **Empty-registry guard:** all of the above with empty `forbidden_substitutes` projection → no block (short-circuit path).
- `platform_tests/scripts/test_check_sot_read_discipline.py` — exercises the doctor check against fixture project states:
  - Clean fixture (both Claude + Codex registrations correct) → PASS.
  - Missing canonical hook file → WARN with file-path guidance.
  - Missing Codex adapter → WARN with adapter-path guidance.
  - Claude settings.json matcher missing Read or Grep or Glob → WARN naming the missing tool-event.
  - Codex hooks.json registers Read/Grep/Glob (unsupported) → WARN with explicit "Codex hook surface is Bash; matcher Read/Grep/Glob will not fire" guidance.
  - Codex hooks.json missing Bash adapter entirely → WARN.
- `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` — unit test for loader handling of the new column (presence, absence, type validation, projection round-trip parity).

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as REVISED versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps each new/extended spec to test coverage; harness-specific fixtures cover Codex Bash event surface per F1. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth, cited paths | Being EXTENDED to v2; new read-discipline clauses derive from existing clauses + `DELIB-20260672` Q3/Q11; harness-specific clause (d) added per Codex F1. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | blocking | parent of `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` extension | Slice 1 v1 cited; Slice 2A extension extends the registry schema row. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | blocking | content:registry record schema | v1 (Slice 1) cited; v2 extension adds `forbidden_substitutes`. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | blocking | content:projection parity | v1 cited; the schema extension MUST projection-round-trip; verification ensures parity. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | blocking | content:Codex hook, content:.codex/hooks.json | Codex-side hook registration is the Bash adapter (live Codex hook surface per v2 of this ADR, `codex_hooks stable true`); contract acknowledges Bash/apply_patch surface, not Read/Grep/Glob — directly satisfies the v2 ADR's empirical foundation. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:GOV/DCL inserts | 4 formal-artifact-approval packets enumerated in target_paths (3 spec packets + 1 rule packet); per-packet owner approval per `DCL-ARTIFACT-APPROVAL-HOOK-001`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | `PAUTH-...-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE` (rowid 133 v1) cited; covers WI-4340 + WI-4343. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260672 + DELIB-20260879 (mint AUQ) as owner-decision authority. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs + Slice 2A's 3 governance specs. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4340 primary; WI-4343 secondary; both in PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 3 new test files in target_paths; spec-to-test mapping in §Specification-Derived Verification Plan. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/**, path:.claude/**, path:config/** | All paths within `E:\GT-KB`; no out-of-root targets. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`; no exceptions. |
| `GOV-08` (KB is truth) | blocking | foundational | Canonical hook reads registry via MemBase projection; TOML is edit-surface, projection is canonical. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 3 governance specs + concrete implementation plan + spec-derived verification. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Slice 2A extends Slice 1's artifact-registry with mechanical anti-substitution. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified | Slice 1's specs at `verified` (per bridge `gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md`); Slice 2A extensions create v2 rows. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "Read-discipline", "forbidden_substitutes column", "two-surface read hook" — first-contact concepts; glossary updates included. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: `DELIB-20260671` (umbrella 7-AUQ) + `DELIB-20260672` (peer's 16-AUQ adopted via S408 reconciliation; specifically establishes Slice 2A scope) + `DELIB-20260670` (manual-triage survey identifying 8 forbidden-substitute candidates AND the always-loaded / shell-readable falsifying-class evidence motivating Codex parity in this slice) + `DELIB-20260869` (work-item text alignment) + `DELIB-20260879` (PAUTH mint authority). The Codex F1 finding refines the IMPLEMENTATION contract; no new owner decision is required because owner-authority for harness-specific parity is already encoded in `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (live Codex hook surface is Bash/apply_patch). Per-spec formal-artifact-approval packets require additional per-packet owner approval at execution time per `GOV-ARTIFACT-APPROVAL-001`.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-001..008` — umbrella thread; GO at -008.
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md` — sibling, VERIFIED. Provides the base schema Slice 2A extends.
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md` — NEW (prior version of this thread; superseded by REVISED-2).
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-002.md` — Codex NO-GO with F0 (target_paths shape) + F1 (harness-specific hook contract). This REVISED-2 addresses both.
- `bridge/gtkb-agent-sot-read-discipline-phase-1-002.md` (WITHDRAWN) — predecessor; scope absorbed into Slice 2A.
- `DELIB-20260671` — umbrella 7-AUQ.
- `DELIB-20260672` — Slice 2A authority (peer's 16-AUQ).
- `DELIB-20260670` — 8 forbidden-substitute candidates from manual triage; also identifies always-loaded + shell-readable surfaces as the substitution risk class motivating Codex parity in this slice.
- `DELIB-20260673` — parallel-session fragmentation evidence motivating mechanical anti-substitution.
- `DELIB-20260869` — work-item text alignment AUQ (WI-4340 + WI-4343 v2).
- `DELIB-20260868` — work-item disposition AUQ (subsumed WIs).
- `DELIB-20260879` — PAUTH-mint authority for `PAUTH-...-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE` (per Codex -002 Prior Deliberations confirmation).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 — live Codex hook surface evidence (Bash/apply_patch); foundation for the harness-specific contract.
- `.claude/rules/acting-prime-builder.md:140-151` — corroborates `.codex/hooks.json` as a live Codex interception boundary on Windows for CLI ≥ 0.128.0-alpha.1 (the empirical basis for ADR v2).
- `.claude/hooks/lo-file-safety-gate.py:755-757` — implementation precedent for payload-dispatching on `tool_name` (Bash branch); informs the canonical hook's structure.
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` — implementation precedent for the thin Codex adapter pattern this slice replicates.
- `memory/research_sot_consolidation_2026_06_04.md` — research file informing the 22 SoT classes.
- `bridge/gtkb-managed-artifact-registry-008.md` — registry pattern precedent.

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

Owner-decision evidence authorizing this proposal:

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Umbrella scope ratification | AskUserQuestion | DELIB-20260671 (7-AUQ) | Slice 2A as a child of the umbrella |
| Read-discipline scope adoption | AskUserQuestion | DELIB-20260672 (16-AUQ adopted via S408) | Slice 2A subject area |
| 8 forbidden-substitute candidates | Manual-triage + owner ratification | DELIB-20260670 | Initial `forbidden_substitutes` population in registry TOML; also identifies the Codex-shell-read attack class informing F1 retention scope |
| Schema authority alignment | AskUserQuestion | DELIB-20260869 | WI-4340 + WI-4343 v2 text |
| Slice 2A PAUTH mint | AskUserQuestion | DELIB-20260879 (per Codex -002 confirmation) | PAUTH coverage of WI-4340 + WI-4343 with mutation classes for source, config, protected narrative file, MemBase spec insert, CLI extension, tests |
| Codex hook parity surface | Prior owner ratification via ADR | `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 + `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` | Authorizes treating `.codex/hooks.json` Bash matcher as the live Codex interception boundary; no NEW AUQ required for the F1 harness-specific contract — the authority is already encoded |

No NEW owner AUQ is required for THIS proposal. Per-spec formal-artifact-approval packets at execution time will require per-packet owner approval as separate AUQ events per `GOV-ARTIFACT-APPROVAL-001`.

## Acceptance Criteria

1. **Spec extensions land:** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 in MemBase with read-discipline clauses (including harness-specific clause d); `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 with `forbidden_substitutes` column; `DCL-SOT-READ-HOOK-CONTRACT-001` v1 inserted with two-surface harness-specific contract. All via formal-artifact-approval packets with owner approval.
2. **Registry seeded:** `config/registry/sot-artifacts.toml` updated to populate `forbidden_substitutes` on the entries identified in `DELIB-20260670` (8 candidates). MemBase projection regeneration (via `gt registry sync` from Slice 1) reflects the new column.
3. **Canonical hook implemented:** `.claude/hooks/sot-read-discipline.py` exists; payload-dispatches on `tool_name`; Claude branch handles Read/Grep/Glob; Codex branch handles Bash with per-verb command parsing for at least `Get-Content`, `Select-String`, `Get-ChildItem` (incl. `-Recurse`), `gc`, `gci`, `cat`, `rg`, `grep`. Reads MemBase projection (NOT TOML).
4. **Codex adapter implemented:** `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py` exists; pipes stdin via subprocess into the canonical hook with `GTKB_HARNESS_NAME=codex`, `GTKB_HARNESS_ID=A` env (mirroring `lo-file-safety-gate-bash-adapter.py`).
5. **Registrations correct:**
   - `.claude/settings.json` PreToolUse contains an entry with matcher containing `Read` AND `Grep` AND `Glob` and command resolving to the canonical hook.
   - `.codex/hooks.json` PreToolUse contains an entry with matcher `"Bash"` and command resolving to the adapter.
6. **Rule file landed:** `.claude/rules/sot-read-discipline.md` (protected narrative; via formal-artifact-approval packet) cites `DCL-SOT-READ-HOOK-CONTRACT-001`, documents the two-surface contract, and lists the explicit-owner-authorization bypass.
7. **Doctor check landed:** `_check_sot_read_discipline` in `groundtruth_kb/project/doctor.py`; 4-layer assertion as described in §Summary > Operational; explicitly fails the Codex-registers-Read/Grep/Glob case with a guidance message; severity WARN.
8. **Tests pass:** `pytest platform_tests/scripts/test_sot_read_discipline_hook.py platform_tests/scripts/test_check_sot_read_discipline.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` GREEN. Test suite includes BOTH Claude-shape and Codex-shape fixtures per §Summary > Tests.
9. **Ruff clean:** `ruff check` + `ruff format --check` GREEN on all changed Python files.
10. **No project-root-boundary violation:** all target_paths within `E:\GT-KB`.
11. **No false-green:** if Slice 2A reports VERIFIED, a manual smoke against the canonical hook with a Codex-shape Bash fixture (e.g., `Get-Content harness-state/role-assignments.json` if that path is registered as a forbidden substitute) MUST return `{"decision": "block", ...}`. Smoke command + result documented in the post-impl report.

## Phased Implementation Plan

**Phase 1 — Spec governance landing (3 formal-artifact-approval packets):**

1. Generate packet for `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 — content extension with the 4 read-discipline clauses (including harness-specific clause d). Owner approval gate fires.
2. Generate packet for `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 — content extension with `forbidden_substitutes: list[str]` optional column + validation rule. Owner approval gate fires.
3. Generate packet for `DCL-SOT-READ-HOOK-CONTRACT-001` v1 — new DCL defining the two-surface harness-specific contract. Owner approval gate fires.
4. Insert all 3 via `KnowledgeDB.update_spec` / `KnowledgeDB.insert_spec` per packet evidence.

**Phase 2 — Registry seed:**

5. Update `config/registry/sot-artifacts.toml` to populate `forbidden_substitutes` on the 8 candidate entries from `DELIB-20260670`. Use `gt registry sync` (Slice 1 CLI) to regenerate the MemBase projection.

**Phase 3 — Loader extension + canonical hook + Codex adapter (substantively rewritten vs -001):**

6. Extend `groundtruth_kb/project/sot_registry.py` `SoTArtifact` dataclass with `forbidden_substitutes: list[str] = field(default_factory=list)`; update validation + projection helpers.
7. Author `.claude/hooks/sot-read-discipline.py` (canonical Python hook):
   - Top-level `_load_payload()` and `_tool_name(payload)` helpers (lo-file-safety-gate precedent).
   - `_check_target_path(rel_path, projection)` helper: normalizes path; iterates registry records; returns `(matched_record, matched_substitute)` or `None`.
   - **Claude branch** (`tool_name in {"Read", "Grep", "Glob"}`): extract target from `tool_input.file_path` (Read), `tool_input.path` (Grep), `tool_input.pattern` (Glob); for Glob, treat the pattern's base directory as the target; call `_check_target_path`; emit block decision on match.
   - **Codex branch** (`tool_name == "Bash"`): parse `tool_input.command` via a per-verb extractor table:
     - `Get-Content <path>` / `gc <path>` / `cat <path>` → `<path>`
     - `Select-String -Path <path> [-Pattern X]` / `sls -Path <path>` → `<path>` (may be glob)
     - `Get-ChildItem -Path <path> [-Recurse] [-Filter X]` / `gci -Path <path>` / `gci <path>` → `<path>`
     - `Get-ChildItem <path>` (positional) → `<path>`
     - `rg [flags] <pattern> <path>` → `<path>` (last positional arg)
     - `grep [flags] <pattern> <path>` → `<path>` (last positional arg)
     - For each extracted path, call `_check_target_path`; on first match, emit block decision with canonical-path guidance.
   - Reads registry projection via `groundtruth_kb.project.sot_registry.load_projection` with module-level cache invalidated on file mtime.
8. Author `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py` (thin Codex adapter): copy the structure of `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`; CANONICAL_HOOK constant points at `.claude/hooks/sot-read-discipline.py`; env override `GTKB_HARNESS_NAME=codex`, `GTKB_HARNESS_ID=A`; return canonical exit code.
9. Register hooks:
   - `.claude/settings.json` PreToolUse: add entry with `"matcher": "Read|Grep|Glob"` and command `python "$CLAUDE_PROJECT_DIR/.claude/hooks/sot-read-discipline.py"` with timeout 5.
   - `.codex/hooks.json` PreToolUse: add entry with `"matcher": "Bash"` and command `python "<repo>/.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py"` with timeout 5 (follow existing Codex Bash adapter command convention).

**Phase 4 — Rule file (protected narrative; formal-artifact-approval packet):**

10. Generate packet for `RULE-sot-read-discipline` — content of `.claude/rules/sot-read-discipline.md`. Owner approval gate fires.
11. Write `.claude/rules/sot-read-discipline.md`. Cite `DCL-SOT-READ-HOOK-CONTRACT-001`; summarize the two-surface contract (Claude tool-event branch + Codex Bash-command branch); enumerate the supported Codex command verbs; document the explicit-owner-authorization bypass; motivate with `DELIB-20260673` (fragmentation evidence) and `DELIB-20260670` (falsifying-class evidence — always-loaded and shell-readable surfaces).

**Phase 5 — Doctor check:**

12. Add `_check_sot_read_discipline` to `groundtruth_kb/project/doctor.py`. Implement the 4-layer check (canonical hook file presence; Codex adapter presence; Claude registration with effective Read+Grep+Glob coverage; Codex registration with Bash matcher pointing at adapter — explicitly fails the Codex-Read/Grep/Glob false-green case; registry referential integrity). Severity WARN.

**Phase 6 — Tests:**

13. Write the 3 test files per §Summary > Tests. Run `pytest <paths> -v` + `ruff check` + `ruff format --check`. Verify GREEN before filing post-impl report.

**Phase 7 — Implementation report:**

14. File `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-004.md` as NEW post-impl report with spec-to-test mapping + observed test results + Phase-3 hook+adapter file listings + manual Codex-shape smoke evidence + applicability+clause preflights.

## Specification-Derived Verification Plan

| Spec (extended/new) | Test file | Acceptance check |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 (read-discipline clauses, incl. harness-specific clause d) | `platform_tests/scripts/test_sot_read_discipline_hook.py` | Hook BLOCKS a Read against any registered forbidden_substitute path on BOTH Claude tool-event payloads AND Codex Bash-command payloads (per-verb fixtures); returns canonical-path guidance |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 (forbidden_substitutes column) | `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` | Loader accepts entries with the column populated; accepts entries without it; rejects entries where the column is not a list-of-strings |
| `DCL-SOT-READ-HOOK-CONTRACT-001` v1 (two-surface harness-specific contract) | `platform_tests/scripts/test_sot_read_discipline_hook.py` | Hook honors contract: (a) Claude branch returns block on Read/Grep/Glob forbidden match; (b) Codex branch returns block on Bash forbidden match for each supported verb (`Get-Content`, `Select-String`, `Get-ChildItem` ±`-Recurse`, `gc`, `gci`, `cat`, `rg`, `grep`); (c) error message cites canonical path; (d) empty projection short-circuits to no-block; (e) canonical hook is single-sourced and dispatches by `tool_name` |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` (parity preserved across v2 schema) | `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` (parity assertion) | TOML round-trips through `gt registry sync` without drift; projection matches TOML on `forbidden_substitutes` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (live Codex Bash surface) | `platform_tests/scripts/test_sot_read_discipline_hook.py` (Codex fixtures) + `platform_tests/scripts/test_check_sot_read_discipline.py` (doctor) | Codex parity is via `.codex/hooks.json` Bash matcher → adapter → canonical hook; doctor explicitly fails the Codex-Read/Grep/Glob false-green case |
| Doctor `_check_sot_read_discipline` | `platform_tests/scripts/test_check_sot_read_discipline.py` | 4-layer assertion: canonical hook file presence; Codex adapter presence; Claude effective Read+Grep+Glob coverage; Codex Bash matcher pointing at adapter (NOT Read/Grep/Glob); registry referential integrity |

## Risk and Rollback

**Risk 1 — Hook over-blocks legitimate reads.** The hook intercepts ALL Read/Grep/Glob (Claude) and ALL Bash (Codex) tool calls. Mitigation: initial `forbidden_substitutes` population is conservative (8 paths from `DELIB-20260670`); hook short-circuits on empty registry projection; tests cover edge cases (path normalization, glob expansion semantics, per-verb argument extraction). For Codex Bash, the parser only blocks when a recognized read/search verb appears AND its extracted path matches a forbidden substitute; arbitrary Bash commands are not blocked.

**Risk 2 — Hook performance regression.** Reading MemBase projection on every Read/Grep/Glob/Bash tool call could slow agent sessions. Mitigation: projection is small (22 SoT classes); loader uses module-level cache invalidated on registry file mtime. Bash-branch parser is single-pass over the command string; short-circuits before MemBase read if no recognized verb appears.

**Risk 3 — Schema migration breaks Slice 1 loader.** Adding `forbidden_substitutes` to the schema could break readers that don't expect the column. Mitigation: column is OPTIONAL with default empty list; existing TOML entries without the column continue to load unchanged; explicit unit test asserts back-compat.

**Risk 4 (NEW per F1) — Codex command-parser misses a verb form.** A future Codex session might use a read/search verb not in the initial parser table (e.g., `Format-Hex`, `Tee-Object -InputObject (Get-Content ...)`, complex pipeline forms). Mitigation: the parser table is documented in the rule file and the DCL; new verbs can be added incrementally in subsequent slices without schema migration. Doctor severity stays WARN initially to surface the gap without blocking; promotion to FAIL is a Slice 2B candidate after a coverage audit.

**Rollback:** Per-phase reversibility:
- Phases 1, 4: spec mutations are append-only versioned — withdraw via `withdrawn` status.
- Phase 2: registry TOML edits are file-level reversible via git.
- Phase 3: hook addition + adapter + registration are file-level reversible.
- Phase 5: doctor check addition is file-level reversible.
- Phase 6: tests are file-level reversible.

If Codex NO-GO this proposal: no source mutations occur; rollback is trivial (this bridge file alone is superseded by REVISED-N+1).

## Pre-Filing Preflight Subsection

Both mandatory preflights will be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green (no blocking gaps).

This proposal cites every spec triggered by its paths and content per `config/governance/spec-applicability.toml`, plus `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 which is foundational for the F1 harness-specific contract. Slice 2A adds no new bridge protocol clauses; reuses the Slice 1 enforcement footprint.

## Verification note for F0 (target_paths parser-consumability)

To confirm the F0 fix is effective, the reviewer (or Prime at GO time) can run:

```text
python -c "from scripts.implementation_authorization import extract_target_paths; import pathlib; print(extract_target_paths(pathlib.Path('bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-003.md').read_text(encoding='utf-8')))"
```

Expected: a Python list of 16 normalized paths, the same ones enumerated in the §target_paths section, no `AuthorizationError`. This satisfies F0's "Include a verification note showing `extract_target_paths` or the implementation authorization begin path succeeds for the revised bridge file."

---

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
