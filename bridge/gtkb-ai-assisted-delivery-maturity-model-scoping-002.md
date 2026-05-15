NO-GO

# Loyal Opposition Review - AI-Assisted Delivery Maturity Model Scoping

Reviewed: `bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md`
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Verdict: NO-GO

## Claim

The proposal is not ready for implementation. The blocking preflights pass, but
the proposal treats an advisory/candidate discussion artifact as sufficient
implementation requirements even though that source explicitly required Prime
Builder comment and a later owner decision before implementation. It also
changes the advisory's seven-layer model into a five-layer implementation model
without recording that as a decision.

## Review Scope

- Read live `bridge/INDEX.md` before acting. Latest status for this document was
  `NEW: bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md`.
- Read the full thread version chain; only `-001` exists.
- Resolved durable role from `harness-state/harness-identities.json` and
  `harness-state/role-assignments.json`: Codex harness `A` is assigned
  `loyal-opposition`.
- Read required bridge review rules:
  `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Read the cited source advisory:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md`.
- Inspected target-path existence:
  `docs/ai-assisted-delivery-maturity-model.md`,
  `groundtruth-kb/src/groundtruth_kb/maturity/model.py`, and
  `tests/maturity/test_maturity_model.py` do not currently exist.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ai-assisted-delivery-maturity-model-scoping
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:0639e7412ee4571b692da55ca73e7b0bf3902284462e9e34fc8123da616f2293`
- bridge_document_name: `gtkb-ai-assisted-delivery-maturity-model-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md`
- operative_file: `bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

The advisory omissions should be fixed in the revision, but they are not the
blocking basis for this NO-GO because the preflight reports
`missing_required_specs: []`.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ai-assisted-delivery-maturity-model-scoping
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ai-assisted-delivery-maturity-model-scoping`
- Operative file: `bridge\gtkb-ai-assisted-delivery-maturity-model-scoping-001.md`
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
```

## Prior Deliberations

Deliberation Archive search and exact source reads were run:

```text
python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "AI-assisted delivery maturity model advisory layered delivery capability prompting project memory task processing" --limit 8 --json
python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "seven-layer maturity model Claude Code levels governance release evidence sunk cost" --limit 10 --json
python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL Prime Builder owner decide formal deliberation roadmap input no implementation" --limit 8 --json
python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS
```

Relevant results and source evidence:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` authorizes the
  `PROJECT-GTKB-METHODOLOGY-AI-MATURITY` project grouping, but it does not
  record an owner decision adopting a concrete maturity-model shape.
- The source advisory itself lists relevant prior records, including
  `DELIB-0831`, `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`, `DELIB-0108`,
  `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, and
  `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md:59-83`.
- Search did not find a later Deliberation Archive record that accepts a
  five-layer replacement model or supersedes the advisory's "do not implement"
  recommendation.

## Findings

### F1 - Requirement sufficiency is not established because the source advisory explicitly says not to implement yet

Severity: P1 requirement-sufficiency failure; blocking.

Observation: the proposal says "Existing requirements sufficient" and that the
"Advisory document provides operative content":
`bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md:48-50`. The
advisory it relies on says it is an "advisory / candidate deliberation seed,"
that the model "should be treated as a candidate deliberation topic, not as a
committed change," and in the Recommendation section: "Do not implement anything
from this model yet":
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md:6`,
`:26-28`, and `:311-313`. The same advisory says Prime Builder should comment
first and then the owner can decide whether it remains discussion, becomes a
formal deliberation, or becomes governed architecture/design material:
`:297-325`.

Deficiency rationale: project authorization is not the same thing as an
accepted requirement. Here the operative source says it is not yet a committed
change and defines a decision path before implementation. The proposal does not
show that Prime Builder comment or owner acceptance happened.

Impact: a `GO` would let Prime implement methodology, code, and tests from a
candidate advisory that explicitly told Prime not to implement yet. That would
turn an exploration artifact into product behavior without the required
decision evidence.

Required action: revise the proposal to include the missing Prime Builder
response and owner decision, or narrow the thread to the decision artifact
itself: e.g. a no-code deliberation/roadmap input that classifies the advisory
as adopt, adapt, defer, reject, or monitor before implementation begins.

### F2 - The proposed five-layer model materially changes the advisory's seven-layer model without decision evidence

Severity: P1 requirement drift; blocking.

Observation: the advisory's proposed model has seven layers: Prompting, Project
Memory, Task Protocols, Specs And Evals, Hooks And Guards, Orchestration, and
Governance And Release Evidence:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md:17-24`.
The proposal scopes a five-layer model: Prompting, Project Memory, Task
Processing, Governance, and Lifecycle:
`bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md:64-69`.

Deficiency rationale: that is not a harmless wording change. It collapses
specs/evals, hooks/guards, and orchestration - three of the advisory's central
distinctions - into broader buckets without showing a rationale or an owner
decision. Those distinctions are directly relevant to GT-KB's bridge,
spec-to-test, hook, and release-evidence architecture.

Impact: the first implementation would codify a different maturity model than
the one the owner asked Loyal Opposition to preserve for Prime review. Future
roadmap, assessment, and dashboard work could then inherit a model shape that
was never actually accepted.

Required action: either implement the seven-layer advisory model as written, or
explicitly document the Prime/owner decision that replaced it with the proposed
five-layer structure. If adapting it, add a mapping table explaining every
merge, rename, and dropped layer.

### F3 - Prior Deliberations are incomplete for the source material the proposal relies on

Severity: P2 review-context gap; blocking until revised because it affects
requirement interpretation.

Observation: the proposal's Prior Deliberations section cites only
`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`:
`bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md:39-41`.
The cited advisory's own Prior Deliberations section lists the relevant role,
deterministic-services, operating-model, competitive-strategy, and execution-plan
records that framed the advisory:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AI-ASSISTED-DELIVERY-MATURITY-MODEL-ADVISORY-2026-05-03-11-35.md:59-83`.

Deficiency rationale: the bridge review gate requires substantive prior
deliberation context. This proposal depends on the advisory for requirement
content, so omitting the advisory's own deliberation context removes the
decision history needed to evaluate whether a five-layer implementation is a
valid adaptation.

Impact: Prime and Loyal Opposition would review the work as if batch
authorization were the only prior decision, missing the records that explain
sunk-cost resistance, role-contract context, and the absence of an exact prior
model deliberation.

Required action: carry forward the advisory report as an explicit source
artifact and cite its relevant Deliberation Archive records in the revised
proposal. If no newer owner decision exists, state that clearly.

### F4 - Test path is outside the package's established test root

Severity: P2 verification-plan gap.

Observation: the proposal places the package module under
`groundtruth-kb/src/groundtruth_kb/maturity/model.py`, but places tests at root
`tests/maturity/test_maturity_model.py` and runs
`python -m pytest tests/maturity/test_maturity_model.py -v`:
`bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md:16` and `:94`.
The package-local pytest config uses `groundtruth-kb/tests` as its test root:
`groundtruth-kb/pyproject.toml:71-73`. The repository root pytest config uses
`platform_tests` and `applications/Agent_Red/tests`:
`pyproject.toml:8-10`.

Deficiency rationale: a package feature should either use the package's normal
test root (`groundtruth-kb/tests/...`) or explicitly justify why a new root
`tests/` tree is being introduced and how CI will include it. The current plan
creates a one-off test location for a package module.

Impact: even if the explicit command works locally after file creation, the new
tests may be missed by the package's standard test runs and root CI expectations.

Required action: move the planned tests to
`groundtruth-kb/tests/maturity/test_maturity_model.py` and update the command,
or revise the proposal to add root `tests/` to the appropriate pytest/CI
surface with a justification.

## Required Revised Proposal Evidence

Prime Builder should file
`bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-003.md` as `REVISED`
only after:

1. Providing the missing Prime Builder response and owner decision that turns
   the advisory/candidate seed into implementation scope, or narrowing this
   thread to a no-code decision/disposition artifact.
2. Preserving the seven-layer model or documenting the accepted decision to
   replace it with a five-layer model.
3. Carrying forward the advisory's relevant Prior Deliberations.
4. Aligning the test path with the package's established test root or explicitly
   adding a new root test convention.
5. Rerunning both bridge preflights against the revised operative file.

No owner decision is required from this verdict. The current bridge result is
NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
