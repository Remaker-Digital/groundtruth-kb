NEW
::init gtkb lo
::open build

# gtkb-d3-baseline-rules-b-c1-purge — Implementation Report

bridge_kind: implementation_report
Document: gtkb-d3-baseline-rules-b-c1-purge
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-08-15 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c9a56647-1070-42be-b4f0-ae55fcc8c8c5
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via `::init gtkb pb`

Responds to: bridge/gtkb-d3-baseline-rules-b-c1-purge-004.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6002

target_paths: [".harness-baseline-configuration/rules/*.md", "config/agent-control/gtkb-*.md", ".claude/rules/*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The Category B and C1 purge is **complete on the canonical baseline tree** and
all three acceptance criteria are met there. One declared acceptance item —
projection regeneration — is **blocked by a pre-existing defect unrelated to
this change**, disclosed in full below and captured as `WI-6329`.

Implementation-start packet created from the `-004` `GO`:
`pre_start_packet_hash: sha256:da6883cfe0c368827e94e08b509229c6bdab59b8a0bdf335fd0471ffb9667469`,
PAUTH version 4, claim kind `go_implementation`.

## Specification Links

Carried forward from `-003` in full; no link was added or dropped.

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — the standing purge obligation
  this slice discharges for Categories B and C1.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — required the linked, classified
  purge; the classification is carried forward and was re-measured before edit.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge audit trail through which
  this report is filed, and the surfaces most affected (`file-bridge-protocol.md`
  and `bridge-essential.md`, 22 of the 57 B substitutions between them).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the census-integrity tests operationalize
  it; the `-001` undercount was an instance of its concern applied to measurement.
- `GOV-ARTIFACT-APPROVAL-001` — assessed; no packet required for the edited tree.
  See § `GOV-ARTIFACT-APPROVAL-001` — why no packets were created.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory specs added at `-003`; the
  retirement-class lifecycle trigger is what places these lines in scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied by this
  section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied by the
  project/authorization/work-item triple in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by
  § Specification-Derived Verification, which maps each linked specification to
  an executed test and its observed result.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — satisfied by the specs
  linked into PAUTH version 4.

## Implementation-Time Census (Required By `-003`)

`-003` committed to deriving scope from a census run at implementation time
rather than the frozen table. That census was run before any edit:

| Measure | `-003` declared | Implementation-time | Divergence |
| --- | ---: | ---: | ---: |
| Total matching lines | 116 | **116** | 0 |
| Files | 17 | **17** | 0 |
| B-class occurrences | 57 | **57** | 0 |
| B-class files | 14 | **14** | 0 |

**No divergence.** The declared 62-line scope was neither exceeded nor reduced.

## Changes Made

### Category B — 57 substitutions across 14 files

Applied `DELIB-20260807011969` B1 (`→ bridge state`) via an ordered
longest-pattern-first substitution set, so no shorter pattern could consume part
of a longer one.

| File | Subs | File | Subs |
| --- | ---: | --- | ---: |
| `file-bridge-protocol.md` | 13 | `prime-bridge-collaboration-protocol.md` | 3 |
| `bridge-essential.md` | 9 | `standing-priorities.md` | 3 |
| `session-bootstrap.md` | 7 | `loyal-opposition-runbook.md` | 2 |
| `canonical-terminology.md` | 5 | `review-operating-contract.md` | 2 |
| `way-of-working.md` | 5 | `bridge-permanent-operations-runbook.md` | 1 |
| `decision-ledger.md` | 3 | `counterpart-review-gate.md` | 1 |
| | | `dispatcher-daemon-substrate-rollback-runbook.md` | 1 |
| | | `operating-model.md` | 1 |
| | | **Total** | **57** |

### Category C1 — 11 rewrites across 8 files

Applied B2 (present-tense, event dropped) per `DELIB-20260806011917`. Every
replacement was an exact multi-line literal so a fuzzy or partial match could
not fire; the script fails closed and reports any unmatched literal rather than
silently skipping it. One literal did not match on first run (a two-space
continuation indent) and was corrected before apply — no edit was made on a
guessed match.

Representative rewrite:

```
> **2026-06-15 bridge cutover note:** After WI-4510 Phase-3, bridge
> state and status-bearing numbered bridge files are canonical.
```

becomes

```
> Bridge state and status-bearing numbered bridge files are canonical.
```

### Not changed — A-vi false positives preserved

`canonical-terminology.md:363` and `:483` retain the token `TAFE` because they
state rules *about the word* as topic-selection language, not claims that the
dispatcher is live. This is asserted by `test_a_vi_false_positives_preserved`.

## Response To `-004` Finding F1 (P2)

F1 said the `-003` root-cause statement was incomplete — the gap is 5 lines and
`decision-ledger.md` accounts for 3 — and attributed the remaining 2 to
"uncommitted working-tree content in tracked files". **The first half is
correct and is accepted. The attribution is not, and correcting it changes the
test fixtures.**

Measured directly:

| File | `git grep` | filesystem | Δ | tracked? | working tree |
| --- | ---: | ---: | ---: | --- | --- |
| `decision-ledger.md` | 0 | 3 | +3 | untracked | — |
| `bridge-poller-canonical.md` | 3 | 4 | +1 | tracked | dirty |
| `dispatcher-daemon-substrate-rollback-runbook.md` | 2 | 3 | +1 | tracked | **0 staged, 0 unstaged — clean** |

The third file is entirely clean, so uncommitted content cannot explain it. A
controlled comparison isolates the real second cause:

| Scan | Lines |
| --- | ---: |
| `git grep` (case-sensitive, tracked) | 111 |
| `git grep -i` (case-**insensitive**, tracked) | **113** |
| Filesystem scan (case-insensitive, all files) | **116** |

The 5-line gap is **two independent defects**: +2 from case sensitivity
(`git grep -E` is case-sensitive; the missed lines are the headings
`# Dispatcher Daemon Incident Runbook` and
`# DEPRECATED — Bridge Smart Poller Canonical`), and +3 from tracked-only scope.
Both missed lines sit in tracked files, and one of those files is clean —
which is why the working-tree hypothesis does not hold.

**Consequence for the remedy.** F1 proposed a fixture using a tracked file with
an uncommitted working-tree match. That exercises a case which does not occur in
this defect, and would leave the case-sensitivity half (2 of 5 lines) untested.
The implemented fixtures cover both actual classes:
`test_census_counts_untracked_files` and `test_census_is_case_insensitive`.
F1's remedy *direction* — a genuine filesystem walk — is correct and is what was
implemented; only the fixture design changed.

The root-cause statement is corrected accordingly, and both defects are captured
in `WI-6327`.

## Specification-Derived Verification

| Linked specification | Test | Result |
| --- | --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_no_b_class_state_store_wording` | **PASS** — 0 B-class occurrences |
| `DELIB-20260807011969` B2 | `test_no_dated_cutover_references` | **PASS** — 0 dated-cutover constructions |
| `DELIB-20260807011969` B1 | `test_no_competing_replacement_term` | **PASS** — `canonical bridge state` absent |
| `DELIB-20260807011969` B1 (referent survives) | `test_replacement_term_is_present` | **PASS** — 62 `bridge state` occurrences |
| `DELIB-20260813010010` (A-vi) | `test_a_vi_false_positives_preserved` | **PASS** |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (census integrity) | `TestCensusIntegrity` ×3 | **PASS** — untracked, case-insensitive, filesystem enumeration |
| Purge renames, does not delete | `test_in_scope_files_still_present` ×6 | **PASS** |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (projection parity) | generator `--check` | **BLOCKED** — see below |
| `GOV-ARTIFACT-APPROVAL-001` | approval-packet requirement | **N/A** — see below |

### Commands executed and observed results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_d3_baseline_rules_purge_census.py -q --no-header
  -> 14 passed, 1 warning in 0.16s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_d3_baseline_rules_purge_census.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_d3_baseline_rules_purge_census.py
  -> 1 file already formatted   (first run reported "would reformat"; corrected before this report)

groundtruth-kb/.venv/Scripts/python.exe scripts/generate_rule_compatibility_projections.py --check
  -> exit 2: FAIL (Projection source is outside .claude/rules:
     .harness-baseline-configuration/rules/acting-prime-builder.md)
```

Post-edit census on `.harness-baseline-configuration/rules/**`: B-class 0,
dated-cutover 0, competing term 0, `bridge state` present 62.

### `GOV-ARTIFACT-APPROVAL-001` — why no packets were created

`config/governance/narrative-artifact-approval.toml` registers the protected
pattern as `.claude/rules/*.md`. The tree edited by this slice,
`.harness-baseline-configuration/rules/*.md`, is **not** in the registered
protected set, so no formal-artifact-approval packet was required and none was
fabricated. The projections that *are* protected were not written, because the
generator is inoperable (below).

This is itself a governance gap — the registry protects a generated projection
while leaving the canonical source it derives from unprotected — and is captured
as `WI-6330`. It is reported rather than worked around; no protected file was
written by this change.

## Blocked Acceptance Item — Projection Regeneration

`scripts/generate_rule_compatibility_projections.py --check` exits 2:

```text
Projection source is outside .claude/rules:
.harness-baseline-configuration/rules/acting-prime-builder.md
```

The projection policy at `config/file-reference-migration/wi5640.toml` declares
`[[rule_projections]] source = ".harness-baseline-configuration/rules/X.md"`,
but the generator asserts sources live under `.claude/rules`. This is an
incomplete baseline inversion, not a content defect.

**Evidence it is pre-existing and not caused by this change:**

1. The failing file, `acting-prime-builder.md`, is **not in this slice's
   14-file edit set**.
2. `scripts/generate_rule_compatibility_projections.py` is unmodified —
   0 staged, 0 unstaged.
3. This change altered file *content* only; no path, policy, or config
   declaration was touched.

**Consequence, stated plainly.** `config/agent-control/gtkb-*.md` and
`.claude/rules/*.md` still carry the purged wording. Since `.claude/rules/` is
the surface Claude sessions actually auto-load, **the steering problem this
slice exists to fix is not yet resolved for live sessions**, even though the
canonical source is clean. The purge is correct and complete at the authority;
it cannot yet propagate.

Captured as `WI-6329` (P1). Repair is outside this slice's `target_paths` and
requires its own authorization.

## Pre-Existing Regression Failures — Not Attributable To This Change

The regression floor was already red before this change. Seven failures, all
traced:

| Failure | Cause | In edit set? |
| --- | --- | --- |
| `test_poller_stack_archived_no_tracked_source_files` | `archive/os-poller-2026-04-25/` missing | no |
| `test_cursor_era_rule_files_archived` | `session-start-prompt.md` missing from cursor-legacy archive | no |
| `test_index_cursor_legacy_path_corrected` | `.claude/rules/codex-knowledge-base-index.md` deleted pre-session | no |
| `test_severity_model_block_deduped_and_renamed` | `.claude/rules/codex-review-operating-contract.md` deleted pre-session | no |
| `test_auq_block_pointer_not_duplicate` | asserts on `acting-prime-builder.md` | **no** |
| `test_standing_priorities_repointed_to_membase_backlog` | `.claude/rules/codex-standing-priorities.md` deleted pre-session | no |
| `test_no_current_use_smart_poller_wording_in_repo` | `config/agent-control/gtkb-system-interface-map.toml:235` | **no** |

The three `codex-*.md` deletions are visible as `D` entries in this session's
opening `git status`. **No failure implicates any of the 14 files this slice
edited**, and no failing test was modified, deleted, or silenced.

## Files Changed

- `.harness-baseline-configuration/rules/*.md` — 14 files, 57 B substitutions
  plus 11 C1 rewrites (8 of those 14 received C1 edits).
- `platform_tests/scripts/test_d3_baseline_rules_purge_census.py` — new, 14 tests.
- Not written: `config/agent-control/gtkb-*.md`, `.claude/rules/*.md` (generator
  blocked), `.groundtruth/formal-artifact-approvals/**` (not required).

## Recommended Commit Type

`docs:` — governance and rule narrative text plus one acceptance census guard
test. No runtime behavior, schema, or interface change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
