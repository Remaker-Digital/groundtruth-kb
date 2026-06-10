NEW

bridge_kind: governance_advisory
Document: gtkb-wi-4225-scaffold-golden-fixture-regen
Version: 009
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-008.md (GO)
Implements: bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-007.md (REVISED-2)

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 068e5131-24ab-4f19-ae9d-6015cfd8bb7b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4225

target_paths: ["groundtruth-kb/templates/hooks/spec-event-surfacer.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**"]

implementation_scope: governance
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

# WI-4225 — Post-Implementation Report (REVISED-2 plan; addresses NO-GO -006)

## Summary

The REVISED-2 plan at `-007` (GO'd at `-008`) is implemented:

1. Template `groundtruth-kb/templates/hooks/spec-event-surfacer.py` was
   `ruff format`-cleaned — a single 2-line→1-line collapse of the
   `EVENT_FORMAT` implicit-concat string. Runtime value byte-identical
   (verified by load + repr; 105 chars, same 7 placeholders in same order).
2. Scaffold goldens regenerated. Net diff: **13 files** (1 template + 10
   dual-agent + 2 local-only). One drift class (the previously-flagged
   `spec-event-surfacer.py` fixture) was **retired by the source-sweep** —
   it is now byte-identical to its committed baseline, so it no longer
   appears in the diff (an improvement over the `-007` plan's predicted 14).
3. Both mandatory code-quality gates are GREEN on all 9 Python files
   (template + 8 fixtures): `ruff check` clean; `ruff format --check` clean.
   This closes Codex NO-GO `-006` P1.
4. The three RED byte-equality tests are GREEN. `test_scaffold_bridge_index`
   still passes (Option A guard for the AUQ Q1 INDEX-row strip).
5. Phantom sweep, credential scan, dynamic-field scan all clean. Diff stays
   strictly inside the REVISED-2 `target_paths` envelope (template + the
   two profile dirs); no other files touched.

## Owner Decisions / Input

Three AskUserQuestion decisions captured 2026-06-03 (this session) are the
owner-decision authority for this implementation:

- **AUQ Q1 — `bridge/INDEX.md` golden disposition → Option A ("Let regen strip the rows").**
  Honored. The regenerated `dual-agent/bridge/INDEX.md` is the minimal queue
  header emitted by the unmodified `_generate_bridge_index` generator;
  ADVISORY/DEFERRED/WITHDRAWN rows and skip-notes are removed.
  `test_scaffold_bridge_index.py` confirms the minimal INDEX still satisfies
  the required `NEW`/`GO`/`VERIFIED` content (7 passed). This AUQ is the
  explicit owner approval for the 3 golden row removals under the
  Protected-Behaviors removal gate.
- **AUQ Q2 — Sequencing vs WI-4279 → Option 1 ("Sequence after WI-4279 lands").**
  Honored: WI-4279 is VERIFIED -004 and committed (`c4e7dfd3`); phantom
  precondition re-verified at execution.
- **AUQ Q3 — NO-GO -006 fix path → Option A ("Fix template + recapture (Recommended)").**
  Honored: the template was ruff-formatted before recapture; the fixture
  follows. Both `ruff check` and `ruff format --check` pass on the template
  and all 8 changed Python fixtures (commands + per-gate results below).

No additional owner decisions were required at implementation time; the GO
at `-008` had no owner-action requirements.

## Implementation Steps Executed

1. **Clean baseline.** Reset `scaffold_golden/` + template to HEAD so the new
   packet's evidence is unambiguous (the prior round's regen state was discarded
   since it was based on the now-superseded REVISED `-003`).
2. **Implementation-start packet minted** under
   `PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001`, target_path_globs
   widened to include the template (3 globs total).
3. **Template format-fix.**
   `python -m ruff format groundtruth-kb/templates/hooks/spec-event-surfacer.py`
   → `1 file reformatted`. Diff:
   ```diff
   -    "[KB-SPEC-EVENT] {spec_id} v{version} -- {kind} -- {title} "
   -    "[type={type} status={status} section={section}]"
   +    "[KB-SPEC-EVENT] {spec_id} v{version} -- {kind} -- {title} [type={type} status={status} section={section}]"
   ```
   Byte-equivalent runtime value (formatter-only). Re-ran both gates on the
   template: `ruff check` → `All checks passed!`; `ruff format --check` →
   `1 file already formatted`.
4. **Windows ReadOnly attribute clearance** (per the prior round's lesson —
   `os.rmdir` refuses `ReadOnly` dirs even when empty; `git checkout`
   re-stamps them):
   `Get-ChildItem -Recurse 'scaffold_golden' -Force -Directory | %{ $_.Attributes = 'Normal' }`
   plus the three outer dirs.
5. **`python scripts/_capture_scaffold_golden.py` → exit 0.** Captured 31
   (local-only) + 66 (dual-agent) files on the first attempt (no retries).
6. **`groundtruth.toml` `created_at` revert** on both profiles.
7. **Diff-scope check.** `git diff --name-only` over template + both profile
   dirs returned exactly the 13 expected paths (no others). Notably,
   `dual-agent/.claude/hooks/spec-event-surfacer.py` is **absent** from the
   diff — the template format-fix retired that drift class because the
   regenerated golden now matches its pre-existing committed baseline.
8. **Phantom sweep clean.**
   `rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001"
   groundtruth-kb/tests/fixtures/scaffold_golden/
   groundtruth-kb/templates/hooks/spec-event-surfacer.py`
   → exit 1 (no matches).
9. **Mandatory separate Python code-quality gates** (per
   `.claude/rules/file-bridge-protocol.md` § "Pre-File Code-Quality Gates";
   this is the per-file evidence the prior report `-005` omitted).
   See "Code-Quality Gate Results (per-file)" below.
10. **Credential / secret scan + dynamic-field scan.** 0 credential hits; 0
    dynamic-field hits across 13 diff files.
11. **Tests run.** See "Test Results" below.
12. **Semantic-equivalence proof for the template fix.** Loaded the
    formatted module, printed `EVENT_FORMAT`: `'[KB-SPEC-EVENT] {spec_id}
    v{version} -- {kind} -- {title} [type={type} status={status}
    section={section}]'`, length 105, 7 placeholders in original order
    (`spec_id, version, kind, title, type, status, section`). The formatter
    collapsed implicit-concat into one literal; no character changed.

## Code-Quality Gate Results (per-file; closes NO-GO -006 P1)

Files audited: the 1 template + 8 changed Python fixtures (9 total).

| # | File | `ruff check` | `ruff format --check` |
|---|------|---|---|
| 1 | `groundtruth-kb/templates/hooks/spec-event-surfacer.py` | PASS | PASS |
| 2 | `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/hooks/bridge-compliance-gate.py` | PASS | PASS |
| 3 | `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/hooks/spec-event-surfacer.py` | PASS | PASS |
| 4 | `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge-propose/helpers/write_bridge.py` | PASS | PASS |
| 5 | `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/impl_report_bridge.py` | PASS | PASS |
| 6 | `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/revise_bridge.py` | PASS | PASS |
| 7 | `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/scan_bridge.py` | PASS | PASS |
| 8 | `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/show_thread_bridge.py` | PASS | PASS |
| 9 | `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/.claude/hooks/bridge-compliance-gate.py` | PASS | PASS |

Commands and aggregate results:

- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <9 files>` → `All checks passed!`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <9 files>` → `9 files already formatted`

(Files #3 and #9 are byte-identical re-photographs of files #1 and #2's
template/source counterparts respectively, but they are tested independently
because the file-bridge-protocol gate applies per-changed-Python-file.)

## Files Changed (the GO'd inventory; 13 files)

Template (1 — the source-sweep that closes NO-GO -006):
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (format-only collapse of `EVENT_FORMAT`)

Dual-agent (10; one fewer than the `-007` prediction because the template-fix retired the `spec-event-surfacer.py` fixture drift):
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/rules/bridge-essential.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/rules/canonical-terminology.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/rules/file-bridge-protocol.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/impl_report_bridge.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/revise_bridge.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/scan_bridge.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge/helpers/show_thread_bridge.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/skills/bridge-propose/helpers/write_bridge.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge/INDEX.md` (Option-A row strip; AUQ Q1)

Local-only (2):
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/.claude/rules/canonical-terminology.md`

## Test Results

| Specification | Command | Result |
|---|---|---|
| GTKB-ISOLATION-017 byte-equality contract (3 tests green) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture groundtruth-kb/tests/test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py::test_clean_adopter_byte_matches_golden_fixture -q -p no:cacheprovider` | **3 passed in 1.87s** |
| `test_scaffold_bridge_index` still green under Option A (minimal INDEX) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_scaffold_bridge_index.py -q -p no:cacheprovider` | **7 passed in 4.37s** |
| WI-4279 precondition held (no phantom re-blessed) | `rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/tests/fixtures/scaffold_golden/ groundtruth-kb/templates/hooks/spec-event-surfacer.py` | exit 1 (0 hits) |
| Mandatory Python LINT gate | `ruff check <9 files>` | All checks passed! |
| Mandatory Python FORMAT gate (SEPARATE) | `ruff format --check <9 files>` | 9 files already formatted |
| Template fix is format-only / byte-identical runtime | module load + `repr(EVENT_FORMAT)` | `'[KB-SPEC-EVENT] {spec_id} v{version} -- {kind} -- {title} [type={type} status={status} section={section}]'` (105 chars; 7 placeholders in original order) |
| Diff scope = expected inventory | `git diff --name-only` over template + 2 profile dirs | **13 paths** (1+10+2; the `-007` prediction of 14 was conservative — template fix retired one drift class) |
| No secret leak | DELIB-0687 canonical pattern scan over 13 diff files | 0 hits |
| No unmasked dynamic-field leak | timestamp/session-id/uuid/sha scan over diff lines | 0 hits (post `created_at` revert) |
| Mutation stayed within PAUTH envelope | `git diff --name-only` shows only paths inside the 3 target_path_globs | confirmed; `source` (template) + `test_fixture_update` (fixtures) — both in `allowed_mutation_classes` |

## Specification Links

- `GTKB-ISOLATION-017` — byte-equality contract this restored to green.
- `gtkb-deferred-authority-protocol-alignment` **VERIFIED -011** — drift files #1–#7 (rules + skill helpers) source authority.
- `gtkb-session-id-shared-resolver-unification` **VERIFIED** (WI-4270) — bridge-compliance-gate.py drift source authority.
- `gtkb-wi-4279-scaffold-phantom-spec-citation-repoint` **VERIFIED -004** (commit `c4e7dfd3`) — sequencing precondition; cleared.
- Commit `28cb7c7a` (2026-04-29) — origin of the `spec-event-surfacer.py` template line-wrap; format-debt closed by this implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope; `source` + `test_fixture_update` mutation classes both used + both authorized.
- `.claude/rules/file-bridge-protocol.md` § "Pre-File Code-Quality Gates (lint AND format are separate)" — the mandatory separate-gate evidence now provided (Codex NO-GO -006 P1 directly addressed).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; INDEX-canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec linkage + spec-derived verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-4225 backlog home.
- `DELIB-0687` — canonical credential-scan pattern set used in step 10.

## Prior Deliberations

- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-008.md` (GO) — the verdict this report implements; clean GO with two residual-risk reminders (template fix must be format-only/semantic-free; target paths strictly limited). Both honored: format-only diff captured above; diff scope = exactly the 3 target_path_globs' contents.
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-007.md` (REVISED-2) — implementation plan; carried forward.
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-006.md` (NO-GO) — P1 closed: both separate gates evidenced per-file; root cause (template format-debt) eliminated.
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-005.md` (prior NEW report) — superseded by this report.
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-004.md` (prior GO on `-003`) — residual-risk reminder honored by the scope-widening through REVISED-2.
- `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-004.md` (VERIFIED) — precondition cleared.
- Owner AUQ 2026-06-03 (this session, three rounds) — INDEX Option A, sequencing Option 1, fix-path Option A; all honored.

## Requirement Sufficiency

Existing requirements sufficient. The byte-equality contract is restored;
the separate code-quality gate evidence is now per-file present; both
chosen mutation classes (`source`, `test_fixture_update`) are explicitly
in the PAUTH's `allowed_mutation_classes`.

## Risk / Rollback

Low. 13 mutated files inside the 3 PAUTH-authorized `target_path_globs`. No
runtime behavior change (template fix is byte-equivalent at runtime per the
load+repr proof). No KB mutation. Rollback = single-commit revert. Every
absorbed byte traces to a VERIFIED/landed source change or a documented
template format-fix; nothing is freshly invented in the goldens.

## Recommended Commit Type

`test` — primary intent is bringing 3 byte-equality fixture tests to green
plus closing the mandatory `ruff format --check` gate at its source. The
template format-fix is byte-equivalent at runtime (formatter-only,
load+repr-proven) and is bundled here only because the regenerated fixture
inherits its bytes from the template, so they MUST land together to satisfy
both contracts simultaneously. Commit scope: the 13 mutated files + this
bridge thread's audit trail (per the inventory-drift `governance_review`
valve). The 6 unrelated working-tree modifications already present at
session start are explicitly **not** staged.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` as `NEW: bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-009.md`
at the top of the existing `gtkb-wi-4225-scaffold-golden-fixture-regen`
document version list in `bridge/INDEX.md`; append-only — full chain
preserved (NEW -001 → NO-GO -002 → REVISED -003 → GO -004 → NEW -005 →
NO-GO -006 → REVISED -007 → GO -008 → this NEW -009). `bridge/INDEX.md`
remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`. Awaiting Codex
`VERIFIED`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
