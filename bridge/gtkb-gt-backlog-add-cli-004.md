NO-GO

# Loyal Opposition Review - gt backlog add CLI REVISED-1

bridge_kind: loyal_opposition_review
Document: gtkb-gt-backlog-add-cli
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-gt-backlog-add-cli-003.md`
Verdict: NO-GO

## Verdict

NO-GO. The revision fixes the earlier dry-run, same-connection membership, auto-ID, and mechanical preflight issues, but it still cannot receive GO because the CLI scope treats WI-3270's provenance fields as optional even though the live work item says the command must require normal evidence fields and preserve source directive / related specification / bridge-thread context. The proposal also omits the standing-backlog DB authority and schema specifications that directly govern this implementation surface.

## Reviewed Materials

- `bridge/INDEX.md`
- `bridge/gtkb-gt-backlog-add-cli-001.md`
- `bridge/gtkb-gt-backlog-add-cli-002.md`
- `bridge/gtkb-gt-backlog-add-cli-003.md`
- `groundtruth.db` current `WI-3270` row, queried with `KnowledgeDB.get_work_item("WI-3270")`
- `groundtruth.db` current specs queried with `KnowledgeDB.get_spec(...)`: `GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- Mandatory applicability and clause preflights below

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner authorization for `PROJECT-GTKB-BACKLOG-CAPTURE-001`, including WI-3270.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - owner decision that future-work candidates flow to MemBase, not `MEMORY.md`, while implementation approval remains separate.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing backlog as a DB-backed source of truth with provenance and linkage fields.
- `DELIB-1790` / `DELIB-1791` - prior GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH NO-GO records relevant to backlog authority and verification strictness.

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "WI-3270 gt backlog add CLI GOV-STANDING-BACKLOG" --limit 8`
- `python -m groundtruth_kb deliberations search "standing backlog formal source of truth work_items review consideration candidate dry-run related specs bridge threads" --limit 8`

## Findings

### F1 - P1 - Evidence/provenance fields are still optional despite WI-3270 requiring normal evidence

Observation: The live WI-3270 row says the command should "require the normal evidence fields, preserve source owner directive and related specs/bridge threads, support dry-run output, and emit the created WI id." The `-003` proposal instead defines only `--title`, `--origin`, `--component`, and `--description` as required, and classifies `--source-owner-directive`, `--source-deliberation-query`, `--related-deliberation-ids`, `--related-spec-ids`, and `--related-bridge-threads` as "Evidence/provenance options" (`bridge/gtkb-gt-backlog-add-cli-003.md:32`). The risk section reinforces that interpretation by saying "evidence options are optional but recommended" (`bridge/gtkb-gt-backlog-add-cli-003.md:194`). The test plan also includes `test_backlog_add_minimum_args_creates_wi`, which would prove that the command can create a work item without the evidence fields (`bridge/gtkb-gt-backlog-add-cli-003.md:164`).

Deficiency rationale: The prior NO-GO's F1 was not just about exposing extra option names. It was about preventing low-fidelity MemBase work-item rows at the capture point. A CLI that can write candidate work items with no source owner directive, no source deliberation query, no related specs, and no related bridge threads still permits the exact evidence-loss failure WI-3270 was created to avoid. `KnowledgeDB.insert_work_item()` exposes these fields (`groundtruth-kb/src/groundtruth_kb/db.py:3296` through `groundtruth-kb/src/groundtruth_kb/db.py:3300`), and `groundtruth-kb/src/groundtruth_kb/backlog.py` already treats `source_owner_directive`, `related_spec_ids_at_creation`, and `related_bridge_threads` as structured migration metadata.

Impact: Agents could use `gt backlog add` as a low-friction write path, but future reviewers would receive rows that lack the "why", source directive, governing-spec snapshot, and bridge-thread context needed for prioritization and later implementation proposals. That shifts evidence reconstruction back onto the owner or a future agent.

Recommended action: Revise the command contract and tests so the normal evidence fields are enforced, not merely accepted. At minimum, require `--source-owner-directive` and a source context field (`--source-deliberation-query` and/or `--related-deliberation-ids`), and require an explicit related-specs/related-bridge-threads value or an explicit no-related-artifacts reason. Replace or split the minimum-args test so it proves required evidence is enforced rather than proving evidence-free creation succeeds.

### F2 - P1 - Standing-backlog DB authority and schema specs are missing from Specification Links

Observation: The proposal cites `GOV-STANDING-BACKLOG-001`, but does not cite `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` or `DCL-STANDING-BACKLOG-DB-SCHEMA-001` in `## Specification Links` (`bridge/gtkb-gt-backlog-add-cli-003.md:40` through `bridge/gtkb-gt-backlog-add-cli-003.md:49`). The current `GOV-STANDING-BACKLOG-001` v4 states that the post-migration implementation surface is the MemBase `work_items` table extended with backlog columns, queried via `current_work_items`, "per `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3 + `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3." Current `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3 makes `current_work_items` backed by append-only `work_items` the standing-backlog authority, and current `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3 names the backlog columns this CLI writes, including `source_owner_directive`, `source_deliberation_query`, `related_deliberation_ids`, `related_spec_ids_at_creation`, and `related_bridge_threads`.

Deficiency rationale: This implementation is not merely "a CLI under GOV-STANDING-BACKLOG-001." It is a write surface for the exact authority and schema defined by the standing-backlog ADR/DCL pair. The file-bridge protocol requires every relevant governing specification to be linked before GO; relying on the parent GOV to imply the ADR/DCL leaves the implementation and test plan without the schema authority it must satisfy.

Impact: Prime could implement the command in a way that passes the listed tests while missing authority/schema constraints that are central to the backlog migration pivot, especially around field format and `current_work_items` read-back semantics.

Recommended action: Add `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` to `## Specification Links`, then add explicit spec-to-test rows proving the created WI is visible through the canonical `current_work_items`/`gt backlog list` read path and that all backlog schema evidence fields are persisted in the expected field names/formats.

## Positive Checks

- The live latest status was `REVISED` for `gtkb-gt-backlog-add-cli`; the thread was actionable for Loyal Opposition.
- `show_thread_bridge.py` reported no drift for the `gtkb-gt-backlog-add-cli` version chain before this verdict.
- The mandatory applicability preflight passed on the operative `-003` proposal with no missing required or advisory specs reported by the mechanical registry.
- The mandatory clause preflight exited 0 with no blocking gaps.
- The revised proposal specifies same-connection project membership through `db.link_project_work_item(...)`, and the current DB layer exposes that API at `groundtruth-kb/src/groundtruth_kb/db.py:3730`.
- The revised proposal specifies `BEGIN IMMEDIATE` around max-id allocation plus insert; that is directionally appropriate for the auto-ID race called out in `-002`.

## Applicability Preflight

- packet_hash: `sha256:db7ec20000d0939f5d832effbebdcaef91b7c019d870938fe12405da3b76ea0a`
- bridge_document_name: `gtkb-gt-backlog-add-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gt-backlog-add-cli-003.md`
- operative_file: `bridge/gtkb-gt-backlog-add-cli-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-gt-backlog-add-cli`
- Operative file: `bridge\gtkb-gt-backlog-add-cli-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Verification Commands

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-gt-backlog-add-cli --format json --preview-lines 400` - no drift before verdict filing.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gt-backlog-add-cli` - passed; output embedded above.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gt-backlog-add-cli` - exit 0; output embedded above.
- `python -m groundtruth_kb deliberations search "WI-3270 gt backlog add CLI GOV-STANDING-BACKLOG" --limit 8` - found `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` and `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` among relevant results.
- `python -m groundtruth_kb deliberations search "standing backlog formal source of truth work_items review consideration candidate dry-run related specs bridge threads" --limit 8` - found `DELIB-1790` / `DELIB-1791` backlog source-of-truth review history among relevant results.
- `KnowledgeDB.get_work_item("WI-3270")` - confirmed the operative work-item wording requiring normal evidence fields, source owner directive / related specs / bridge-thread preservation, dry-run output, and WI id emission.
- `KnowledgeDB.get_spec(...)` for `GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - confirmed the omitted ADR/DCL are current standing-backlog DB authority/schema specifications.

## Conditions For GO

1. Make the evidence requirement explicit: either require the normal provenance fields at CLI validation time, or include an explicit owner/spec clarification explaining which evidence fields may be absent and what no-evidence marker must be stored.
2. Update the tests so evidence-free creation is not the success baseline. Tests should prove required evidence is enforced and that the persisted row carries the expected `source_owner_directive`, `source_deliberation_query` or deliberation IDs, related specs, and related bridge-thread context or explicit no-related-artifacts reason.
3. Add `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` to `## Specification Links`.
4. Add spec-to-test rows for the standing-backlog DB authority/schema surfaces, including canonical read-back through `current_work_items`/`gt backlog list` and schema-field persistence.

