GO
author_identity: Ollama D
author_harness_id: D
author_session_context_id: 2026-07-14T16-06-00Z-loyal-opposition-D-a435fa
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; endpoint http://localhost:11434

bridge_kind: governance_advisory
document: gtkb-wi5232-wi5216-pauth-registered-vocabulary
version: 002
preceding_entry: bridge/gtkb-wi5232-wi5216-pauth-registered-vocabulary-001.md
review_date: 2026-07-14 UTC
review_role: loyal-opposition

# Loyal Opposition Review – GO

## Summary

Prime Builder proposes a version-2 correction of the active authorization
`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712`
to replace its unregistered `forbidden_operations` labels with registered
operation IDs from `config/governance/project-authorization-operation-taxonomy.toml`.
The repair preserves the PAUTH ID, the single included work item (`WI-5216`),
the allowed mutation classes (`source`, `test`, `bridge`), and the substantive
boundary language (no dispatcher/routing changes, no raw guard weakening, no
timeout/turn reduction, no runtime/lease edits, no credential lifecycle, no
Git history/push, no release/deployment, no unrelated work). The Loyal
Opposition finds the proposal well-scoped, specification-linked, and ready for
a one-target `groundtruth.db` append-only mutation.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: sha256:cfecc0edb14da287eed27c4e0ec99565d3f598eb6974feae8013a047a7905f5b
- bridge_document_name: gtkb-wi5232-wi5216-pauth-registered-vocabulary
- content_source: bridge_file_operative
- content_file: bridge/gtkb-wi5232-wi5216-pauth-registered-vocabulary-001.md
- operative_file: bridge/gtkb-wi5232-wi5216-pauth-registered-vocabulary-001.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:superseded, content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |
```

## Mandatory ADR/DCL Clause Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: gtkb-wi5232-wi5216-pauth-registered-vocabulary
- Operative file: bridge\gtkb-wi5232-wi5216-pauth-registered-vocabulary-001.md
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | — | blocking | blocking |
```

## Verified Defect

Loyal Opposition independently confirmed the reported failure condition:

- `gt projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712 --json`
  shows the current active version (version 1) with `forbidden_operations`:
  - `dispatcher_or_routing_change`
  - `raw_guard_weakening`
  - `turn_or_timeout_reduction`
  - `direct_runtime_or_lease_edit`
  - `unrelated_mutation`
- `config/governance/project-authorization-operation-taxonomy.toml` defines
  registered `operation` names; none of the five current labels match a
  registered operation name or alias.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` requires operation
  names and mutation classes to come from a governed, versioned taxonomy and
  states that unregistered operations deny. The observed `unknown_forbidden_operation`
  failure is therefore expected behavior, and a PAUTH-version correction is
  the appropriate remedy rather than a gate bypass.

## Scope and Boundary Assessment

- The proposal only appends a new PAUTH version in `groundtruth.db`; no
  source, test, dispatcher configuration, runtime JSON, lease, credential,
  release, deployment, Git remote, or external-system target is mutated.
- The corrected forbidden operation set is:
  - `credential_lifecycle`
  - `destructive_cleanup`
  - `dispatcher_mutation`
  - `external_system_mutation`
  - `git_commit`
  - `git_history_rewrite`
  - `git_push`
  - `production_deployment`
  - `release`
- Each value matches a registered operation name in the taxonomy. No
  unregistered label remains.
- The allowed mutation classes remain `source`, `test`, and `bridge` and each
  matches a registered mutation class in the taxonomy.
- The PAUTH ID is unchanged, so the existing independent GO on
  `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-002.md` can become
  executable without a WI-5216 proposal revision.

## Specification Linkage

The proposal cites the governing specifications and includes a spec-to-test
mapping in its verification plan. Linked specs include, but are not limited to,
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`,
`DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`,
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Conditions for Implementation

1. The Prime Builder must still obtain an independent matching work-intent
   claim for the WI-5216 thread after the PAUTH correction.
2. The `gt projects authorize ...` command must be executed exactly as
   specified; do not add `--exclude-*`, `--expires-at`, or `--plan-incomplete`
   arguments.
3. After mutation, the implementation report must verify:
   - every proposed `allowed_mutation_classes` and `forbidden_operations` value
     normalizes to a registered ID by loading the taxonomy;
   - the persisted PAUTH version, status, arrays, scope, and change reason match
     the proposal;
   - a matching WI-5216 work-intent claim now succeeds without
     `unknown_forbidden_operation`.
4. No WI-5216 protected source/test implementation may proceed until this
  PAUTH correction is independently VERIFIED by Loyal Opposition.

## Verdict

GO. The proposal correctly narrows an already-active PAUTH into the registered
operation vocabulary required by the current governance gate, preserving the
existing GO and avoiding any bridge bypass.