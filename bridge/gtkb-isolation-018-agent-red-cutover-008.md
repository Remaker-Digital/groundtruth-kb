GO

# Loyal Opposition Review - GTKB-ISOLATION-018 Agent Red Child-Directory Cutover REVISED-3

Document: gtkb-isolation-018-agent-red-cutover
Version reviewed: bridge/gtkb-isolation-018-agent-red-cutover-007.md
Verdict: GO
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-06-05 UTC

## Summary

The `-007` revision resolves the `-006` blockers. It preserves the
production-effects legacy-root probe instead of changing it to an already
relocated path, adds a defense-in-depth no-double-prefix acceptance check, and
narrows the Python ruff scope to the two Python files still proposed for edit.

No owner input is requested in this auto-dispatch response. Prime Builder may
implement the revised proposal after creating the normal implementation-start
authorization packet from this live GO entry.

## Prior Deliberations

The normal `gt deliberations search` CLI was unavailable in this dispatch shell
and the default interpreter could not import `groundtruth_kb.cli`; I therefore
used read-only SQLite queries against `groundtruth.db` / `current_deliberations`.

- `DELIB-20260875` records owner authorization for the ISOLATION-018 Agent Red
  child-directory cutover PAUTH and next-session scheduling.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` records the pending-migration
  waiver for Agent Red root files until the migration is VERIFIED.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` records the owner topology
  rule that Agent Red files belong under `E:\GT-KB\applications\Agent_Red\`.
- `DELIB-S334-OQ-E3-OPTION-A` records the owner decision to keep platform tests
  at the GT-KB root.
- `DELIB-1915` and `DELIB-1907` record related VERIFIED ISOLATION-018 sub-slice
  precedent.
- `DELIB-1952` records the prior `gtkb-isolation-018-agent-red-file-migration`
  bridge thread.
- `DELIB-1382`, `DELIB-1384`, and `DELIB-1385` record related
  production-effects-map review history.

## Findings

No blocking findings.

## Positive Evidence

- The live latest status in `bridge/INDEX.md` was
  `REVISED: bridge/gtkb-isolation-018-agent-red-cutover-007.md`, making the
  entry Loyal Opposition-actionable.
- `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-isolation-018-agent-red-cutover --format json --preview-lines 0`
  returned `drift: []` and a coherent version chain from `-001` through `-007`.
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-agent-red-cutover`
  passes on `-007` with no missing required or advisory specs.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-agent-red-cutover`
  exits 0 on `-007` with no blocking clause gaps.
- `bridge/gtkb-isolation-018-agent-red-cutover-007.md:47` selects the prior
  NO-GO's recommended Option 1: keep `_production_effects.py` and
  `test_rehearse_production_effects.py` unchanged so the legacy-root probe
  remains the source of closure evidence.
- `scripts/rehearse/_production_effects.py:328` still contains the
  `shopify.app.toml` probe, while `scripts/rehearse/_production_effects.py:928`
  and `scripts/rehearse/_production_effects.py:930` still implement the MOVE
  renderer's `applications/Agent_Red/<path>` target prefix. That current-state
  evidence supports the revised no-edit interpretation.
- `bridge/gtkb-isolation-018-agent-red-cutover-007.md:246` and
  `bridge/gtkb-isolation-018-agent-red-cutover-007.md:288` add the
  no-double-prefix verification/acceptance check for
  `applications/Agent_Red/applications/Agent_Red/`.
- `bridge/gtkb-isolation-018-agent-red-cutover-007.md:274` and
  `bridge/gtkb-isolation-018-agent-red-cutover-007.md:275` limit ruff check and
  format verification to `scripts/session_self_initialization.py` and
  `scripts/rehearse/_dashboard_regen.py`, matching the remaining proposed
  Python edits after `_production_effects.py` and the platform test were removed
  from scope.

## Implementation Context For Prime Builder

Before editing, run:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-isolation-018-agent-red-cutover
```

Implementation should remain scoped to the target paths in `-007`. Preserve the
`scripts/rehearse/_production_effects.py:328` legacy-root probe and do not edit
`platform_tests/scripts/test_rehearse_production_effects.py` as part of this
slice. The post-implementation report should carry forward the `-007`
specification links and include the full spec-derived command evidence,
including the no-double-prefix production-effects-map assertion and the two
separate ruff gates.

## Applicability Preflight

- packet_hash: `sha256:638513aa05d384983f67495630efe54cb487eaba02933b5960151e85c2a28a58`
- bridge_document_name: `gtkb-isolation-018-agent-red-cutover`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-agent-red-cutover-007.md`
- operative_file: `bridge/gtkb-isolation-018-agent-red-cutover-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-agent-red-cutover`
- Operative file: `bridge\gtkb-isolation-018-agent-red-cutover-007.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and no
`Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with
`enforcement_mode = "advisory"` are reported but never gate._

## Verification Limits

- This is proposal review, not implementation verification; no post-change tests
  were run.
- The normal deliberation CLI surfaces were unavailable, so the DA search used
  direct read-only SQLite queries against `groundtruth.db`.
- The LO file-safety hooks blocked several broad read-only shell scans when the
  command named protected proposal target paths such as
  `applications/Agent_Red/CLAUDE.md`, `.github/workflows/build-test-host.yml`,
  `platform_tests/scripts/test_rehearse_production_effects.py`, and
  `memory/topics/testing.md`. The verdict therefore relies on the mandatory
  preflights, the current script-surface scan that was permitted, the proposal's
  own target-path inventory, and the prior thread evidence for those protected
  surfaces.

## Required Post-Implementation Report Evidence

Prime Builder's post-implementation report must include:

1. destination/root absence checks for the three moved files;
2. `git ls-files` and `git log --follow` evidence for root removal and history
   preservation;
3. verification that `scripts/session_self_initialization.py`,
   `scripts/rehearse/_dashboard_regen.py`, `Dockerfile.test`,
   `memory/topics/deployment.md`, and `memory/topics/testing.md` were updated as
   proposed;
4. confirmation that `scripts/rehearse/_production_effects.py` still contains
   the legacy-root `shopify.app.toml` probe;
5. a production-effects-map assertion showing no
   `applications/Agent_Red/applications/Agent_Red/` output;
6. `python -m pytest platform_tests/scripts/test_rehearse_production_effects.py -q --tb=short --timeout=60`;
7. `python -m pytest groundtruth-kb/tests/ -k "isolation or registry or root_boundary" --tb=short -q --timeout=60`;
8. `python -m groundtruth_kb project doctor`;
9. `ruff check scripts/session_self_initialization.py scripts/rehearse/_dashboard_regen.py`;
10. `ruff format --check scripts/session_self_initialization.py scripts/rehearse/_dashboard_regen.py`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
