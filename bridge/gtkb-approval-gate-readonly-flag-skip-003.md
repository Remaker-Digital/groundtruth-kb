REVISED

# Implementation Proposal - Approval-Gate Read-Only-Flag Skip (WI-3273)

bridge_kind: implementation_proposal
Document: gtkb-approval-gate-readonly-flag-skip
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH
Project: PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS
Work Item: WI-3273

target_paths: [".claude/hooks/formal-artifact-approval-gate.py", "platform_tests/hooks/test_formal_artifact_approval_gate.py"]

This REVISED proposal fixes a usability defect in `.claude/hooks/formal-artifact-approval-gate.py`: read-only invocations (`--help`, `--dry-run`, `--validate-only`) are blocked even though they do not mutate state. Observed both at S341 (DA write CLI help blocked) and recurringly during the S350 session (verification queries blocked despite touching no mutating surface).

## Revision Notes

This `-003` revision addresses all three findings in the `-002` NO-GO verdict:

- **F1 (P1 — whole-command read-only flag matching can bypass a real formal
  mutation):** Resolved. IP-1 below is rewritten to be SEGMENT-AWARE. The
  read-only exemption no longer scans the whole command string. It reuses the
  gate's existing command-separator helpers (`COMMAND_SEPARATORS` at
  `.claude/hooks/formal-artifact-approval-gate.py:72`, `_command_tokens` at
  `:134`, `_is_command_separator` at `:151`) to split the token stream into
  command segments at `;`, `&&`, `||`, `|`. The exemption applies ONLY to a
  segment that BOTH matches a formal-mutation pattern AND carries a read-only
  flag for that same invocation. A segment such as
  `python -m groundtruth_kb deliberations upsert` followed by a separate
  `; echo --help` segment is NOT exempted — the mutation segment carries no
  read-only flag, so the gate still requires a packet. IP-2 adds negative
  tests for `;`, `&&`, and `|` compound commands proving the mutation stays
  blocked, plus the existing quoted-value negative test.
- **F2 (P2 — verification command targets a non-existent test path):**
  Resolved. The nonexistent top-level path
  `tests/hooks/test_formal_artifact_approval_gate.py` is removed from
  `target_paths` (live checkout inspection confirms `E:\GT-KB\tests` and
  `E:\GT-KB\tests\hooks` do not exist). `target_paths` and the verification
  command now reference only the existing file
  `platform_tests/hooks/test_formal_artifact_approval_gate.py`. No new
  top-level `tests` root is created by this work.
- **F3 (P3 — applicability preflight reports missing advisory specs):**
  Resolved. The three advisory specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
  are now cited in `## Specification Links` below with relevance notes.

## Claim

When a Bash command contains a command segment that matches `FORMAL_MUTATION_PATTERNS` (or is a mutating script invocation) AND that same segment carries a read-only flag (`--help`, `-h`, `--dry-run`, `--validate-only`, `--version`, `-V`), the gate treats that segment as read-only intent and does not require a packet for it. The exemption is per-segment: a read-only flag in a different, non-mutating segment of a compound command does NOT exempt a mutation segment.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` - this hook is part of the policy engine; this enhancement narrows false-positives.
- `GOV-ARTIFACT-APPROVAL-001` - the gate enforces this; a genuinely read-only segment is not a mutation, so a segment-aware exemption is contract-preserving.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3273 tracked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the hook is part of the formal-artifact-approval artifact graph this fix preserves.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; WI-3273 triggers this implementation proposal and its spec-derived tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the hook fix is captured as governed work with a bridge artifact and spec-derived tests.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-0835` - the controlling owner decision for strict formal-artifact approval and audit-trail discipline (formal artifacts must not become canonical without approval / acknowledgement / scoped auto-approval evidence). The segment-aware exemption in this revision is constrained by `DELIB-0835`: it never exempts a segment that actually mutates a formal artifact; it only suppresses the packet requirement for a genuinely read-only segment.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization 2026-05-14; records the owner authorization for `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS` including WI-3273.

The Codex `-002` deliberation search confirmed no prior deliberation
contradicts adding a read-only exemption for genuine help/dry-run/validation
invocations.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" — explicit authorization for this NEW under `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`.

## Requirement Sufficiency

Existing requirements sufficient. The WI-3273 description is the operative
spec for the read-only exemption; `GOV-ARTIFACT-APPROVAL-001` and
`DCL-ARTIFACT-APPROVAL-HOOK-001` govern the hook contract. The fix is a
mechanical false-positive narrowing that does not change the gate's intent.
No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3273); member of PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. It performs no batch resolve/promote/retire across the backlog. Review-packet inventory: IP-1 (hook fix) + IP-2 (tests) scoped to one thread. The applicable evidence pattern is a single-WI defect-fix proposal with formal-artifact-approval discipline preserved unchanged.

## Bridge INDEX Update Evidence

`-003` REVISED line prepended above the `-002` NO-GO line under the `Document: gtkb-approval-gate-readonly-flag-skip` block; prior `-001`/`-002` versions preserved unchanged per the append-only bridge audit trail.

## Files Expected To Change

- `.claude/hooks/formal-artifact-approval-gate.py` — segment-aware read-only exemption logic.
- `platform_tests/hooks/test_formal_artifact_approval_gate.py` — spec-derived tests including F1 compound-command negative tests.

## Proposed Scope

### IP-1: Add segment-aware read-only flag detection (per F1)

In `.claude/hooks/formal-artifact-approval-gate.py`:

1. **Segment the command.** Add a helper that splits the `_command_tokens()`
   result into command segments at separators, using the existing
   `COMMAND_SEPARATORS` set (`:72`) and `_is_command_separator()` (`:151`).
   This is the same segment boundary the existing `_script_args()` helper
   (`:165`) already uses; the new helper generalizes that segmenting so a
   full segment's token list is available.
2. **Per-segment formal-mutation + read-only evaluation.** For each segment:
   - Determine whether the segment is a formal mutation: the segment's
     reconstructed text matches a `FORMAL_MUTATION_PATTERNS` regex, or the
     segment is a mutating script invocation.
   - Determine whether that SAME segment carries a read-only flag as a
     top-level token: any of `--help`, `-h`, `--dry-run`, `--validate-only`,
     `--version`, `-V`.
3. **Exemption rule.** A segment is exempt from the packet requirement ONLY
   when it is a formal mutation AND carries a read-only flag in that same
   segment. The gate still requires a packet when ANY segment is a formal
   mutation that does NOT carry a read-only flag. A read-only flag appearing
   only in a different non-mutating segment does NOT exempt a mutation
   segment.
4. **No whole-command early return.** The `-001` design's whole-command token
   scan and global early return are NOT used. The decision is computed
   per-segment so a compound command cannot be globally exempted by an
   incidental read-only token.

This is additive to the existing logic; the existing `_has_mutating_script_invocation()`
behavior (which already exempts `SCRIPT_HELP_FLAGS` per script-invocation
segment) is preserved. The new logic extends per-segment read-only handling
to the `FORMAL_MUTATION_PATTERNS` regex path.

### IP-2: Tests (including F1 compound-command negatives)

Tests are added to `platform_tests/hooks/test_formal_artifact_approval_gate.py`
(the existing file confirmed present; no new test root is created):

Positive (exemption) cases:
- a formal-mutation segment with `--help` → not blocked;
- a formal-mutation segment with `--dry-run` → not blocked;
- a formal-mutation segment with `--validate-only` → not blocked;
- a formal-mutation segment with `-h` → not blocked.

Negative (true-positive preservation) cases — F1 compound-command guards:
- `python -m groundtruth_kb deliberations upsert` with no read-only flag and no packet → still blocked;
- `python -m groundtruth_kb deliberations upsert ; echo --help` → still blocked (read-only flag in a separate non-mutating segment);
- `python -m groundtruth_kb deliberations upsert && python -m groundtruth_kb deliberations --help` → still blocked (the `upsert` segment carries no read-only flag);
- `python -m groundtruth_kb deliberations upsert | echo --dry-run` → still blocked;
- `--help` inside a quoted value (e.g. `git commit -m "fix --help bug"` paired with a mutation) → the quoted token is not a top-level read-only flag, so a real mutation stays blocked.

## Specification-Derived Verification Plan

| Linked specification / behavior | Test |
|---|---|
| `SPEC-AUQ-POLICY-ENGINE-001` — `--help` segment skips the block | `test_approval_gate_skips_block_on_help_flag` |
| `SPEC-AUQ-POLICY-ENGINE-001` — `--dry-run` segment skips the block | `test_approval_gate_skips_block_on_dry_run_flag` |
| `SPEC-AUQ-POLICY-ENGINE-001` — `--validate-only` segment skips the block | `test_approval_gate_skips_block_on_validate_only_flag` |
| `SPEC-AUQ-POLICY-ENGINE-001` — `-h` segment skips the block | `test_approval_gate_skips_block_on_h_flag` |
| `GOV-ARTIFACT-APPROVAL-001` / `DELIB-0835` — no read-only flag → block preserved | `test_approval_gate_blocks_when_no_readonly_flag_and_no_packet` |
| `GOV-ARTIFACT-APPROVAL-001` / `DELIB-0835` — `;` compound: mutation segment still blocked (F1) | `test_approval_gate_blocks_mutation_with_semicolon_readonly_segment` |
| `GOV-ARTIFACT-APPROVAL-001` / `DELIB-0835` — `&&` compound: mutation segment still blocked (F1) | `test_approval_gate_blocks_mutation_with_and_readonly_segment` |
| `GOV-ARTIFACT-APPROVAL-001` / `DELIB-0835` — `|` compound: mutation segment still blocked (F1) | `test_approval_gate_blocks_mutation_with_pipe_readonly_segment` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` — quoted `--help` does not exempt a real mutation | `test_approval_gate_blocks_help_in_quoted_value` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — all linked specs map to executed tests | the post-implementation report carries this mapping and executed results forward |

Corrected verification command (replaces the `-001` nonexistent `tests/...` path):

```
python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short
python -m ruff check .
```

## Acceptance Criteria

- IP-1 landed: read-only exemption is segment-aware, computed per command segment using the existing separator helpers; no whole-command early return.
- IP-2: all listed tests pass, including the three F1 compound-command negative tests proving a mutation segment stays blocked when a read-only flag appears only in another segment.
- No regression in the existing `platform_tests/hooks/test_formal_artifact_approval_gate.py` tests.
- Both preflights PASS on the `-003` operative file.

## Risks / Rollback

- Risk (addressed by F1): a compound command bypassing the gate via an incidental read-only token. Mitigation: the exemption is per-segment; the three F1 compound-command negative tests regression-guard the mutation-stays-blocked behavior.
- Risk: `--help` as a flag VALUE rather than a flag gets the exemption. Mitigation: only top-level tokens in the matched segment are considered; quoted values are not top-level read-only flags. `test_approval_gate_blocks_help_in_quoted_value` guards this.
- Rollback: revert the segmenting helper and the per-segment exemption logic; the gate returns to its prior whole-command behavior, which is conservative (it blocks the read-only false positives this fix targets but never under-blocks).

## Recommended Commit Type

`fix` - defect fix narrowing the false-positive set of a governance hook plus tests. No new capability surface.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` operative file
after filing the INDEX entry. Outputs are embedded in the `## Applicability
Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

```text
- packet_hash: `sha256:5398c6b5fa072f54fe8d67da56524fe883d8547dc9e3c1bbbe3c490685ed867f`
- bridge_document_name: `gtkb-approval-gate-readonly-flag-skip`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-approval-gate-readonly-flag-skip-003.md`
- operative_file: `bridge/gtkb-approval-gate-readonly-flag-skip-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:blocked, content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:* |
```

## Clause Applicability

```text
- Bridge id: `gtkb-approval-gate-readonly-flag-skip`
- Operative file: `bridge\gtkb-approval-gate-readonly-flag-skip-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | must_apply | yes | blocking | blocking |

Exit 0 = pass.
```

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
