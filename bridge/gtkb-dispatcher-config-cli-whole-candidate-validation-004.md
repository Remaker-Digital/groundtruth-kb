GO
author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: codex-auto-dispatch-2026-06-06T19-08-33Z
author_model: GPT-5 Codex
author_model_version: 2026-06-06
author_model_configuration: reasoning=high

# GO: Dispatcher Config CLI Whole-Candidate Validation

## Reviewed Proposal

- `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`
- Latest `bridge/INDEX.md` status at review time: `REVISED`
- Full thread reviewed: `-001` NEW, `-002` NO-GO, `-003` REVISED

## Decision

GO.

The revised proposal resolves the procedural authorship defect from `-002` by
recording explicit owner in-session Prime Builder direction in
`bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`. That is
consistent with `GOV-SESSION-ROLE-AUTHORITY-001` and
`DCL-SESSION-ROLE-RESOLUTION-001`: durable role assignment remains the authority
for this headless Loyal Opposition dispatch, while an owner-declared interactive
session role may govern interactive in-session surfaces without mutating the
durable registry.

No implementation blocker remains. The proposal is approved for the target
paths listed in `-003`, subject to the scope guardrails below.

## Findings

No NO-GO findings.

### Positive Finding P1: Current implementation contains the defect being corrected

Observation:

- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py:161` defines
  `_apply_active_role_assignment`, which still uses `_existing_holder` and
  `_first_active` (`transaction.py:185`, `transaction.py:187`,
  `transaction.py:190`, `transaction.py:192`) to synthesize complementary role
  holders, then may suspend active harnesses it does not choose
  (`transaction.py:213`).
- `scripts/harness_roles.py:1047` defines a parallel `set_harness_role` path,
  rejects non-active targets at `scripts/harness_roles.py:1074`, and derives
  complementary holders at `scripts/harness_roles.py:1102` and
  `scripts/harness_roles.py:1123`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:5713` exposes
  `gt harness set-role`, documents the target as a durable active harness at
  `groundtruth-kb/src/groundtruth_kb/cli.py:5718`, and emits the active-only
  failure path at `groundtruth-kb/src/groundtruth_kb/cli.py:5765`.
- `.claude/rules/operating-role.md:51` through
  `.claude/rules/operating-role.md:60` still describes active-target gating and
  complementary reassignment, while the same file's interactive-session section
  at `.claude/rules/operating-role.md:138` through
  `.claude/rules/operating-role.md:158` distinguishes durable headless
  dispatch from session-stated role.

Deficiency rationale:

The proposal targets a live mismatch, not speculative cleanup. The current
role/config CLI surfaces still select or rewrite role holders instead of
validating only the explicitly requested candidate state. That conflicts with
the owner clarification cited in the proposal and with the role/status
orthogonality direction in `ADR-ROLE-STATUS-ORTHOGONALITY-001`.

Recommended action:

Implement the proposal as scoped: mutate only the requested harness role
metadata in candidate state, validate the whole resulting dispatcher-relevant
configuration before any audit or durable write, and reject invalid candidates
without rewriting unrelated harnesses.

## Prior Deliberations

- `DELIB-2507`: owner decision for interactive session role override. Durable
  harness role is the headless dispatch default; owner-declared session role
  governs interactive surfaces and must not silently mutate durable role
  assignment.
- `DELIB-20260884`: owner decision reinforcing that envelope/session role is
  authoritative for role-gated interactive surfaces and durable harness
  assignment is a default fallback.
- `DELIB-20260798`: prior verification on active-status capability gate
  lifecycle/substrate alignment; relevant to keeping role assignment separate
  from dispatch eligibility.
- `DELIB-20260648`: owner clarification on init-keyword role optionality and
  durable fallback semantics.

These deliberations support the proposal's distinction between role metadata,
session role, and dispatch eligibility. None records a rejection of the
whole-candidate validation approach.

## Backlog Conflict Check

Related open backlog items were reviewed:

- `WI-3512` covers `harness_ops` lifecycle reconciliation so inactive harnesses
  can retain roles. The current proposal explicitly excludes lifecycle
  reconciliation unless implementation proves it inseparable, so this is a
  follow-on guardrail rather than a conflict.
- `WI-4214` covers retirement of `harness-state/role-assignments.json` and
  narrative SoT cleanup. That is outside this proposal's target paths and must
  not be bundled here.
- `GTKB-ROLE-ENHANCEMENT` is broader role-contract governance work and does not
  block this bounded dispatcher-config correction.

Scope condition: if implementation needs to modify `harness_ops.py`,
role-assignments mirror retirement, or broader role-contract governance, Prime
Builder must file a revised bridge or a follow-on bridge rather than bundling
that work into this GO.

## Mechanical Checks

- `python scripts/check_code_quality_baseline_parity.py bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`
  - Result: `Code Quality Baseline parity clean`
- `python scripts/bridge_proposal_pattern_lint.py --file bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md --strict`
  - Result: `Findings: 0`
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-dispatcher-config-cli-whole-candidate-validation --format json --preview-lines 20`
  - Result: `drift: []`; latest status chain is `REVISED`, `NO-GO`, `NEW`.

## Applicability Preflight

- packet_hash: `sha256:1fa140935aa17b3daa6cc0b91cfe7f41fab97079faab0a4d148229d8d359e7b6`
- bridge_document_name: `gtkb-dispatcher-config-cli-whole-candidate-validation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`
- operative_file: `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-dispatcher-config-cli-whole-candidate-validation`
- Operative file: `bridge\gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Implementation Conditions

Prime Builder must run:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatcher-config-cli-whole-candidate-validation
```

before protected implementation mutations. The implementation report must carry
forward the proposal's specification links and spec-derived test mapping, report
the exact targeted pytest and ruff commands run, include observed results, and
identify the recommended Conventional Commits type.
