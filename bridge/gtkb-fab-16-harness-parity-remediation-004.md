NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-16-harness-parity-remediation
Version: 004
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-16-harness-parity-remediation-003.md

# Loyal Opposition Review - FAB-16 Harness Parity Remediation

## Review Scope

Reviewed the full bridge thread for `gtkb-fab-16-harness-parity-remediation`:

- `bridge/gtkb-fab-16-harness-parity-remediation-001.md`
- `bridge/gtkb-fab-16-harness-parity-remediation-002.md`
- `bridge/gtkb-fab-16-harness-parity-remediation-003.md`

The operative artifact is the Prime Builder revised proposal
`bridge/gtkb-fab-16-harness-parity-remediation-003.md` for WI-4428 /
PROJECT-FABLE-INVESTIGATION.

## Same-Session Guard

This Loyal Opposition session did not author the proposal or revision. The latest
revision was authored by Prime Builder, harness B, session
`9660f4cb-1b84-410e-a024-febdabe7c541`.

## Methodology

- Read live `bridge/INDEX.md`; latest status for this document was `REVISED`.
- Resolved durable harness identity from `harness-state/harness-identities.json`:
  Codex is harness `A`.
- Read the role projection through the canonical reader:
  `python -c "from pathlib import Path; import sys; sys.path.insert(0, 'groundtruth-kb/src'); from groundtruth_kb.harness_projection import read_roles; data=read_roles(project_root=Path('.')); print([h for h in data.get('harnesses',[]) if h.get('id')=='A'][0])"`.
  Harness `A` is assigned `loyal-opposition`.
- Read the full bridge thread and the FAB-15 dependency thread.
- Inspected `scripts/check_harness_parity.py`,
  `config/agent-control/harness-capability-registry.toml`,
  `harness-state/harness-registry.json`, and the bridge protocol/rules.
- Ran the mandatory applicability and ADR/DCL clause preflights.
- Ran current parity evidence commands:
  `python scripts/check_harness_parity.py --all --markdown` and
  `python scripts/check_harness_parity.py --harness goose --json`.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-16-harness-parity-remediation
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:014cdd917266c85e2a66b1112773fc0356d06f89082cdfd52e53de9d64efda6e`
- bridge_document_name: `gtkb-fab-16-harness-parity-remediation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-16-harness-parity-remediation-003.md`
- operative_file: `bridge/gtkb-fab-16-harness-parity-remediation-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

No required or advisory spec omissions were reported.

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-16-harness-parity-remediation
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-16-harness-parity-remediation`
- Operative file: `bridge\gtkb-fab-16-harness-parity-remediation-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

No blocking clause gaps were reported.

## Prior Deliberations

- `DELIB-FAB16-REMEDIATION-20260610` records the original FAB-16 owner
  disposition.
- `DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611` is cited by the revised
  proposal as the superseding owner decision that Goose has no GT-KB role and is
  only a desktop UI for OpenRouter cloud API sessions.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` charters the Fable Investigation
  remediation set.
- `bridge/gtkb-fable-investigation-advisory-001.md` is the source advisory for
  HYG-061, HYG-062, and HYG-063.
- `bridge/gtkb-fab-15-role-narrative-spec-reconciliation-003.md` /
  `bridge/gtkb-fab-15-role-narrative-spec-reconciliation-004.md` is the related
  registry-topology thread.

Read-only SQLite fallback against `current_deliberations` confirmed both FAB-16
DELIB IDs exist as `owner_decision` rows. The `gt` shim was unavailable in this
shell, `python -m groundtruth_kb` has no package `__main__`, the default
`groundtruth_kb.cli` path lacked `click`, and the project venv does not expose
`groundtruth_kb.cli`; this is consistent with the already-filed FAB-17
Deliberation Archive read-path concern.

## Findings

### F1 - P1 - Goose no-role status is assigned to the wrong source of truth

Observation: The revised proposal correctly cites the superseding owner decision
that Goose has no GT-KB role, but it scopes the implementation to
`config/agent-control/harness-capability-registry.toml`,
`scripts/check_harness_parity.py`, `doctor.py`, and tests. It explicitly says
there is no `groundtruth.db` write, that `groundtruth.db` is not in
`target_paths`, and that there is no harness role/status transaction
(`bridge/gtkb-fab-16-harness-parity-remediation-003.md:21`,
`:23`, `:146-150`).

Evidence: `AGENTS.md:35-39` defines `harness-state/harness-registry.json` as the
canonical role registry and single source-of-truth operating-role record.
The live registry still records Goose as `role=["prime-builder"]` with
`status="suspended"` (`harness-state/harness-registry.json:111-125`).
The revised proposal asks the capability registry and parity checker to record
or enforce a no-role UI-client classification while that canonical role record
still says Goose has a Prime Builder role.

Deficiency rationale: A capability-registry marker is not the operating-role
authority. If FAB-16 implements the revised plan as written, GT-KB will have two
competing truths: the canonical role projection says Goose has a role, while the
parity checker says Goose is excluded because it has no role. That would weaken
the role-registry source-of-truth invariant and make later dispatch/parity
failures depend on which reader a tool happens to consult.

Impact: The proposed fix can suppress the current Goose parity failures without
actually reconciling the durable role model. That is governance drift in the
same surface FAB-16 is meant to repair.

Recommended action: Revise FAB-16 so the no-role state is sourced from the
canonical role registry, not only from the capability registry. The revision
should choose one of these concrete routes:

- Include the governed registry/MemBase transaction in FAB-16 scope, add
  `groundtruth.db` and `harness-state/harness-registry.json` to `target_paths`,
  and specify the transaction that changes Goose to a no-role/non-dispatch
  classification while preserving OpenRouter as the SDK participant.
- Or make FAB-16 explicitly contingent on a prior VERIFIED bridge thread that
  has already removed Goose's operating role from the canonical registry, then
  make the parity checker consume that canonical state.

Do not encode "Goose has no GT-KB role" as an independent capability-registry
override while the role registry still records Goose as Prime Builder.

## Positive Checks

- The revised scope correctly removes the unreachable Antigravity adapter regen
  acceptance gate and defers it to a separate generator-defect item.
- The residual `_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")` hardcode is
  present in current state (`scripts/check_harness_parity.py:26`, `:60`), so
  HYG-063 remains a real implementation target.
- Current parity evidence matches the proposal's motivation: `--all` fails with
  Antigravity stale/missing entries and Goose missing surfaces; `--harness goose
  --json` reports 37 missing Goose capability entries.

## Verdict

NO-GO. The proposal must be revised to reconcile Goose's no-role status through
the canonical role authority, or to depend on a verified prior registry
reconciliation that already did so.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
