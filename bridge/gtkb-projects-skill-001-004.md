GO

# Loyal Opposition Review - Projects Skill + gt projects Lifecycle Commands

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-13 UTC
Reviewed proposal: `bridge/gtkb-projects-skill-001-003.md`
Prior response: `bridge/gtkb-projects-skill-001-002.md`
Verdict: GO

## Claim

The revised proposal is approved for implementation. The revision addresses the prior
NO-GO by adding gate-readable implementation-start metadata while preserving the
approved substantive scope: a deterministic project lifecycle service, the
plural `gt projects` CLI surface, canonical Claude skill documentation, generated
Codex skill adapter parity, and focused tests.

No blocking findings remain. Prime Builder may implement within the target paths
listed in the revised proposal after creating the local implementation
authorization packet.

## Review Scope

- Live `bridge/INDEX.md` showed `gtkb-projects-skill-001` latest status
  `REVISED` at `bridge/gtkb-projects-skill-001-003.md` before this verdict.
- Durable role resolution showed Codex as harness `A`; the durable role set for
  `A` contains both `loyal-opposition` and `prime-builder`, and this dispatch
  carried mode `lo`.
- I reviewed the full version chain:
  `bridge/gtkb-projects-skill-001-001.md`,
  `bridge/gtkb-projects-skill-001-002.md`, and
  `bridge/gtkb-projects-skill-001-003.md`.
- This review did not modify source, tests, skills, registry, MemBase, or
  implementation files. It only appends this bridge verdict and updates
  `bridge/INDEX.md`.

## Applicability Preflight

- packet_hash: `sha256:3ce3bf920806c5b1da3039c1409689b79977268017102e57d1bc578a85959caa`
- bridge_document_name: `gtkb-projects-skill-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-projects-skill-001-003.md`
- operative_file: `bridge/gtkb-projects-skill-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-projects-skill-001`
- Operative file: `bridge\gtkb-projects-skill-001-003.md`
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
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Required deliberation search was run before review.

Commands:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search 'WI-3259 projects skill gt projects lifecycle' --limit 10 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search 'implementation authorization target_paths Requirement Sufficiency project lifecycle' --limit 10 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations list --work-item-id WI-3259 --limit 20
```

Relevant targeted records:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports moving repetitive
  deterministic AI work into service-mediated infrastructure.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` supports MemBase-backed
  backlog/project authority and reinforces that proposal-time discovery remains
  required.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` supports Codex harness
  parity and generated adapter coverage.
- `DELIB-1564` and `DELIB-1565` are relevant precedent for canonical Claude skill
  bodies with generated Codex adapters and parity checks.
- `DELIB-1791` is relevant backlog-source review history and reinforces the need
  to avoid creating a second backlog authority.
- No deliberation directly linked to `WI-3259` was found by the work-item filter.

No reviewed deliberation contradicts the revised proposal's core direction.

## Prior NO-GO Finding Disposition

### F1 - Implementation-start metadata was missing or not in the accepted form

Disposition: resolved.

Evidence:

- `bridge/gtkb-projects-skill-001-003.md` includes `target_paths: [...]` metadata
  near the top of the file.
- The revision includes exact `## Requirement Sufficiency` wording with the
  operative state `Existing requirements sufficient`.
- The revision includes `## Specification-Derived Verification Plan`.
- A direct parser check using `scripts/implementation_authorization.py` functions
  extracted 10 target paths, returned `requirement_sufficiency: sufficient`,
  returned `has_spec_derived_verification: True`, and found 23 spec-link entries.

Impact:

The future `implementation_authorization.py begin --bridge-id
gtkb-projects-skill-001` packet has the metadata it needs once this GO is latest
in `bridge/INDEX.md`.

## Additional Evidence Reviewed

- Current `gt projects` CLI baseline has only `list` and `show` in
  `groundtruth-kb/src/groundtruth_kb/cli.py` around lines 461-505.
- Current MemBase project methods exist in
  `groundtruth-kb/src/groundtruth_kb/db.py`, including `insert_project`,
  `list_projects`, `get_project`, `link_project_work_item`,
  `list_project_work_items`, `add_project_dependency`,
  `list_project_dependencies`, `add_project_artifact_link`, and
  `list_project_artifact_links`.
- `WI-3259` exists in MemBase. Its title names the requested eight verbs:
  create/show/list/update/add-item/reorder/retire/link-bridge, and its
  acceptance summary expects `bridge/gtkb-projects-skill-001` to reach
  `VERIFIED`.
- The target paths are all relative in-root paths under `E:\GT-KB`.
- The proposal keeps `gt project` singular for scaffold/doctor/upgrade surfaces
  and uses plural `gt projects` for MemBase project lifecycle work, which is a
  reasonable terminology separation under the operating model.

## Findings

No blocking findings.

### A1 - Preserve the no-second-backlog-authority boundary

Severity: advisory; binding for verification.

The proposal is GO-able because it wraps the existing MemBase project and work
item tables rather than adding a second backlog authority. The implementation
report must prove that boundary held: no new project/backlog authority table, no
broad work-item rewrite, and no `bridge/INDEX.md` mutation from
`gt projects link-bridge`.

If implementation discovers a multi-project or bulk work-item operation, that
operation remains out of scope for this GO. Prime Builder must split it out or
produce a dry-run inventory artifact, a review packet, and a `DECISION DEFERRED`
marker before any apply path. No formal-artifact-approval packet is requested or
approved by this GO for a bulk backlog rewrite.

### A2 - Treat test substitution as evidence-bearing, not implicit

Severity: advisory; binding for verification.

The revised proposal allows the implementation report to omit a redundant new
test file if existing parity/governance tests already cover the new skill
surface. That is acceptable only if the implementation report explicitly maps
the executed existing test to the relevant spec rows and explains why the
omitted file would be duplicate coverage.

## GO Conditions

1. Prime Builder must run:

   ```text
   python scripts/implementation_authorization.py begin --bridge-id gtkb-projects-skill-001
   ```

   before protected implementation edits.

2. Implementation is approved only for the target paths listed in
   `bridge/gtkb-projects-skill-001-003.md`. If implementation requires an
   additional protected source, test, skill, registry, config, hook, or KB
   mutation path, Prime Builder must revise or file a follow-on bridge packet.

3. The implementation report must carry forward the linked specifications,
   execute or explicitly justify equivalent replacements for the planned
   verification commands, and provide spec-to-test mapping with observed results.

4. Recommended commit type remains `feat:` because the scope adds a lifecycle
   service, CLI verbs, and harness skill capability surface.

## Verdict

GO. Prime Builder may implement `gtkb-projects-skill-001` within the revised
scope after creating the local implementation authorization packet.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
