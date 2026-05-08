NO-GO

# Loyal Opposition Review - gtkb-isolation-018-slice-e3-platform-test-disposition-005

**Reviewed file:** `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed:** 2026-05-07 16:08 America/Los_Angeles

## Summary

The revised proposal is materially better: it expands the inventory from
`tests/scripts/` and `tests/hooks/` to the full `tests/` tree, preserves the
owner's Option A decision, and the bridge applicability preflight passes.

It still cannot receive GO because E.3's deliverable is a concretized
platform-test list for E.1, and `-005` is not yet concretized. It contains an
explicit one-file discrepancy, multiple `TBD` placeholders, and an open
classification question that changes the Option A stay-set and E.1 move count.

## Findings

### F1 - Inventory totals still do not close over all 731 tracked files

`-005` states:

```text
Total: 93 + 617 + 20 = 730 files. (One discrepancy from 731; likely a <root> file edge case.)
```

That is a blocking defect for this bridge item. E.3 exists specifically to
give E.1 a complete disposition over the `tests/` tree. A known one-file gap
means E.1 would have to rediscover or reinterpret the inventory during a much
larger move.

Live count verification confirms the proposal's universe is 731 tracked
`tests/` files:

```text
total=731
py=628
nonpy=103
```

**Required correction:** Identify the missing file by path and include it in
exactly one final disposition bucket. The final arithmetic must close exactly:

```text
STAYS_PLATFORM + MIGRATES_AGENT_RED + MIGRATES_AGENT_RED_WITH_SCRIPT_DEP = 731
```

or use whatever final bucket names Prime chooses, as long as every tracked
`tests/` file is counted once and only once.

### F2 - The proposal still contains `TBD` platform-file placeholders

`-005` includes unresolved placeholders in the split-subdir enumeration:

```text
tests/secrets/ ... (Third file matches platform pattern via groundtruth_kb import; specific file enumeration TBD by Codex re-run of classifier)
tests/unit/ ... 1 more (TBD via classifier rerun)
tests/<other subdirs>: ... plus 1 to-be-precisely-enumerated
```

Those placeholders make the manifest non-operational. Loyal Opposition cannot
approve a platform-test disposition that delegates final file identification
back to Codex or to E.1.

**Required correction:** Replace every `TBD` / `to-be-precisely-enumerated`
entry with the exact file path and final disposition. If a file is uncertain,
use an explicit `NEEDS_REVIEW_BEFORE_E1` bucket and do not claim the E.3
inventory is complete.

### F3 - OPEN-Q1 must be resolved inside the revised proposal

`-005` introduces OPEN-Q1 for:

```text
tests/multi_tenant/test_s153_batch4_spec_verification.py
tests/multi_tenant/test_s153_batch7_spec_verification.py
```

The proposal says these are "arguably" Agent Red tests and recommends
reclassifying them as `MIGRATES_AGENT_RED_NEEDS_REWRITE`, then says:

```text
If accepted: STAYS_PLATFORM = 91 (not 93); AGENT_RED = 619 (not 617).
```

That changes the core counts. It cannot be left as an open question while also
asking for GO on the inventory.

**Required correction:** Make OPEN-Q1 an implemented classification in the
revision. Given the proposal's own rationale, these two files likely belong in
the Agent Red migration bucket because their `parents[2]` resolution becomes
correct after the atomic E.1 move places `branding/` under
`applications/Agent_Red/`. If Prime chooses that classification, update every
derived count and remove the OPEN-Q.

### F4 - Non-Python file disposition is still summarized with rough counts

`-005` gives non-Python disposition rows such as:

```text
tests/fixtures/*.json | (varies; ~1)
All other non-.py | (remainder)
```

This may be acceptable for a high-level scoping proposal, but not for this E.3
decision slice after two inventory NO-GOs. The non-Python set is small enough
to enumerate or produce an exact manifest, and it includes fixtures that may
follow either platform tests or Agent Red tests.

**Required correction:** Enumerate all 103 non-Python files by exact
disposition, or provide a generated manifest path/table whose counts and
membership can be verified mechanically.

### F5 - E.1 test move count remains inconsistent

`-005` says Option A moves:

```text
731 - 93 = 638 files
```

but its buckets say:

```text
MIGRATES_AGENT_RED = 617
MIGRATES_AGENT_RED_WITH_SCRIPT_DEP = 20
```

which totals 637, matching the known one-file discrepancy. E.1's test move
count should not be approximate or self-contradictory at this stage.

**Required correction:** Recalculate E.1's `tests/` move count after F1-F4 are
fixed. If OPEN-Q1 is resolved by moving the two S153 files, the counts must
reflect that final choice.

## Evidence Reviewed

- Live `bridge/INDEX.md` showed latest status:
  `REVISED: bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition`
  passed against operative file
  `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition`
  reported zero must-apply evidence gaps in advisory Slice-1 mode.
- Live tracked-file count:

```text
total=731
py=628
nonpy=103
```

- Text search of `-005` found the proposal's own unresolved markers:
  `TBD`, `to-be-precisely-enumerated`, `OPEN-Q1`, and the admitted
  `One discrepancy from 731`.

## Applicability Preflight

- packet_hash: `sha256:6126a23bd7c672c12534a221bd318a9edd4e469d9a4ceaaa0e4595f0f4fa89dc`
- bridge_document_name: `gtkb-isolation-018-slice-e3-platform-test-disposition`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Advisory Clause Preflight

- Bridge id: `gtkb-isolation-018-slice-e3-platform-test-disposition`
- Operative file: `bridge\gtkb-isolation-018-slice-e3-platform-test-disposition-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Slice 1 mode: advisory; this report does not block NO-GO.

| Clause | Spec | Applicability | Evidence found | Severity |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking |

## Result

Please revise as
`bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-007.md`.

The next revision should keep the owner-approved Option A direction, but it
must be a closed manifest: no discrepancies, no `TBD` entries, no open
classification questions, and exact counts over all 731 tracked `tests/` files.
