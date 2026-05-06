NEW

# Implementation Proposal - GTKB-AUQ-POLICY-GATES-001: Central Deterministic AUQ Policy Gate

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Architecture and implementation proposal
**Risk tier:** Medium-high (governance/action gating, owner-decision surfacing, commit/push safety, application/platform write protection; no production runtime deployment)
**Backlog item:** `GTKB-AUQ-POLICY-GATES-001 - Central deterministic AUQ policy gate with thin hook/CLI/dashboard adapters`

---

## Background

`GTKB-AUQ-POLICY-GATES-001` exists because S332 surfaced a wider action-gating
need around AskUserQuestion. AskUserQuestion is useful because it creates a
dedicated owner-choice dialog; hooks, CLI wrappers, and structural boundaries
are the mechanisms that can force high-risk actions back to that dialog instead
of relying on the agent to remember.

The current bridge item is a `NO-GO` advisory, not implementation approval:
`bridge/gtkb-auq-policy-gate-backlog-advisory-2026-05-04-001.md`. That advisory
recommends a central deterministic policy gate instead of a growing set of
bespoke hooks for commit, push, tests, build/deploy, requirements updates,
status probes, and application/platform scope protection.

This proposal turns that advisory into a normal Prime Builder implementation
proposal. It does not implement any hook or CLI behavior until Loyal Opposition
returns `GO` on this document.

## Current Evidence Snapshot

| Evidence | Source | Relevance |
|---|---|---|
| Backlog row exists and names this next step | `memory/work_list.md` row `GTKB-AUQ-POLICY-GATES-001` | Requires filing `bridge/gtkb-auq-policy-gates-001-001.md` before implementation |
| Advisory recommends central policy gate | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md` | Defines ALLOW/WARN/ASK/DENY outcomes, no-LLM constraint, action classes, receipts, and first adapter guidance |
| Bridge advisory makes the gap visible | `bridge/gtkb-auq-policy-gate-backlog-advisory-2026-05-04-001.md` | Latest status `NO-GO` is Prime-actionable as a request to file the normal proposal |
| Existing owner-decision tracker provides AUQ enforcement precedent | `.claude/hooks/owner-decision-tracker.py` | Existing hook already detects missing AskUserQuestion flows and pending owner decisions |
| Existing bridge compliance gate provides governance hook precedent | `.claude/hooks/bridge-compliance-gate.py` | Existing hook proves governance enforcement can be centralized and tested instead of hand-waved in prompts |
| Packaged CLI already exists | `groundtruth-kb/src/groundtruth_kb/cli.py` and `groundtruth-kb/pyproject.toml` script `gt = "groundtruth_kb.cli:main"` | Policy check should attach to the existing `gt` command surface |

## Specification Links

Cross-cutting specs required for bridge proposals:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) - `bridge/INDEX.md` is the live
  authority for this proposal. Compliance: this document is filed under
  `bridge/`, and the index entry is inserted with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) -
  implementation proposals must cite every relevant governing specification.
  Compliance: this section lists the bridge, backlog, artifact-governance,
  root-boundary, AUQ, requirements-update, and isolation surfaces that constrain
  the proposed work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) - any later
  implementation report must carry forward these links and map executed tests
  to linked requirements. Compliance: this proposal includes a
  specification-derived test plan.

Standing-backlog authority:

- `GOV-STANDING-BACKLOG-001` v2 (verified) - standing backlog is durable
  cross-session work authority. Compliance: this proposal is filed because the
  standing backlog records `GTKB-AUQ-POLICY-GATES-001` and this exact next
  bridge step.
- `PB-STANDING-BACKLOG-CONTINUITY-001` (verified) - Prime Builder must not
  bypass standing backlog continuity. Compliance: this proposal preserves the
  backlog row's scope and does not substitute unrelated governance work.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (verified) - backlog items are
  selectable work authority. Compliance: this bridge proposal is the governed
  route from backlog entry to implementation.

Artifact-oriented governance:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) - concrete requirements,
  decisions, risks, procedures, and future work should be preserved as durable
  artifacts. Compliance: the policy registry, approval receipts, and action
  outcomes become durable, inspectable artifacts instead of chat-only state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) - project memory is a
  traceable artifact graph. Compliance: each policy rule links action class,
  scope, path ownership, and owner-decision evidence where applicable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) - artifacts require clear
  lifecycle states. Compliance: policy outcomes are explicit `ALLOW`, `WARN`,
  `ASK`, and `DENY` states with defined behavior and receipt transitions.

Role, bridge, and root-boundary rules:

- `.claude/rules/file-bridge-protocol.md` - governs proposal filing, `GO`,
  implementation reports, and `VERIFIED`.
- `.claude/rules/codex-review-gate.md` - forbids implementation changes before
  Loyal Opposition `GO` when the bridge is active.
- `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md`
  - constrain Prime Builder authority and review handoff behavior.
- `.claude/rules/loyal-opposition.md` - constrains Loyal Opposition review and
  verification behavior after this `NEW` entry is filed.
- `.claude/rules/deliberation-protocol.md` - requires deliberation search and
  citation before proposal filing.
- `.claude/rules/canonical-terminology.md` - defines GT-KB, Internal Developer
  Platform, application, Agent Red, MemBase, bridge, Prime Builder, and Loyal
  Opposition terminology used by this proposal.
- `.claude/rules/project-root-boundary.md` - all active GT-KB files must remain
  under `E:\GT-KB`, and GT-KB application files must remain under
  `E:\GT-KB\applications\`. Compliance: proposed GT-KB platform files remain
  under the GT-KB root; Agent Red is treated only as external/application-scope
  context unless Mike explicitly declares Agent Red work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified/specified in live
  preflight data) - application/root placement and platform/application
  isolation must be respected. Compliance: path-ownership policy explicitly
  distinguishes GT-KB platform paths from application-scope paths and does not
  make Agent Red a live GT-KB artifact.

AUQ and requirements-update surfaces:

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v3 (verified) - requirements collection
  uses bounded owner clarification through AskUserQuestion where needed.
  Compliance: the `requirements-update` policy class must use the central
  policy gate before creating or mutating requirements/specification artifacts.
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` v3 (verified) - requirements
  clarification must use a bounded interaction contract rather than open-ended
  chat. Compliance: `ASK` outcomes must provide two to three viable
  AskUserQuestion options and must not ask several decisions at once.
- `.claude/hooks/owner-decision-tracker.py` - existing AskUserQuestion/pending
  decision hook. Compliance: any new hook adapter should call the central
  policy engine and must not duplicate owner-decision parsing rules.
- `.claude/hooks/bridge-compliance-gate.py` - existing governance enforcement
  hook. Compliance: this proposal keeps hook logic thin and policy tables
  centralized.

Deliberation and advisory context:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive AI work should move
  behind deterministic services and CLI/plumbing where possible. Compliance:
  action classification is deterministic and registry-driven.
- `DELIB-0878` - GT-KB isolation authority/topology planning relevant to
  platform/application separation. Compliance: path ownership and active-scope
  checks are part of the policy model.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` -
  demonstrates bounded owner choices for requirement clarification. Compliance:
  ASK outcomes produce bounded options and avoid LLM/API classification.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` -
  umbrella review GO for the A-through-F AUQ enforcement stack. Compliance:
  this proposal does not treat that umbrella GO as direct implementation
  authority; it files this specific sub-work through the bridge lifecycle.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md`
  - source advisory for this backlog item.

The proposed tests derive from these linked specs as follows: bridge authority
drives index/file checks; spec-linkage drives applicability preflight and
section checks; verified-spec testing drives the implementation report's
spec-to-test mapping; standing-backlog specs drive evidence that this proposal
matches the backlog row; artifact-governance specs drive registry, outcome, and
receipt tests; root-boundary and isolation specs drive path containment and
application/platform ownership tests; AUQ/requirements specs drive bounded ASK
option tests and requirements-update gating tests.

## Prior Deliberations

Search performed per `.claude/rules/deliberation-protocol.md`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "AUQ policy gate AskUserQuestion action gating commit push deploy policy check ALLOW WARN ASK DENY" --limit 10
```

Relevant records and adjacent evidence:

| Record | Relevance |
|---|---|
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Supports central deterministic policy services instead of repeated agent judgment |
| `DELIB-0878` | Supports authority-matrix and isolation framing for platform/application boundaries |
| `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` | Supports bounded owner-choice patterns for ASK outcomes |
| `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` | Confirms umbrella sequencing is acceptable while preserving per-slice bridge lifecycle |
| `AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md` | Provides the concrete backlog recommendation, action classes, outcome model, and no-LLM constraint |

No deliberation found in this search rejects creating a deterministic AUQ policy
gate. The search returned weak older matches for unrelated deploy/credential
threads, so this proposal relies on the advisory, backlog row, umbrella GO, and
the relevant deterministic-services/isolation/requirements records above.

## Owner Decisions And Input

No new owner decision is needed to file this proposal. The backlog row and
advisory capture S332 owner direction to consider wider AUQ/hook use, lower-cost
alternatives, and GT-KB platform protection while in an application scope.

This proposal does not treat the advisory as formal implementation approval and
does not ask Loyal Opposition to supply owner authority. Future implementation
may need one-at-a-time owner input if policy defaults create a real product
choice, for example whether `commit` should default to `ASK` or `WARN` for
routine local commits after the first receipt model lands.

## Goal

Create one deterministic policy gate that all AUQ-related action enforcement can
use:

```text
gt policy check --action <action> --scope <scope> --paths <paths> --json
```

Canonical outcomes:

```text
ALLOW - proceed silently
WARN  - proceed with deterministic advisory text
ASK   - block until an AskUserQuestion answer produces an approval receipt
DENY  - block; requires scope change, different command, or external approval
```

The policy gate must be registry-driven and must not call an LLM or external API
to classify intent.

## Proposed Implementation Scope

### Slice 1 - Policy model and registry

Add a deterministic policy engine inside the packaged GT-KB codebase:

- `groundtruth-kb/src/groundtruth_kb/policy/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/policy/engine.py`
- `groundtruth-kb/src/groundtruth_kb/policy/models.py`
- `groundtruth-kb/src/groundtruth_kb/policy/registry.py`

Add a project policy registry:

- `config/agent-control/auq-policy-gates.toml`

The registry should define:

- action classes,
- default outcome,
- scope-specific overrides,
- path-ownership mappings,
- receipt requirements,
- optional warning text,
- DENY remediation text,
- ASK option templates suitable for AskUserQuestion.

Initial action classes:

| Action | Initial policy |
|---|---|
| `status` | `ALLOW` for deterministic local operating-state probes |
| `test` | `ALLOW` for local deterministic tests; `ASK` for long, external, live, destructive, or cost-bearing suites |
| `build` | `ALLOW` for local dry builds; `ASK` for external build service use |
| `commit` | `ASK` when staged changes exist, with concise staged/unstaged summary and intent options |
| `push` | `ASK` or `DENY` based on branch, remote, protected-scope policy, and receipt state |
| `deploy-staging` | `ASK` with target, commit, migration, and rollback summary |
| `deploy-production` | `DENY` unless external release prerequisites are present, then `ASK` plus environment approval |
| `requirements-update` | `ASK` before creating or mutating requirements, specifications, ADRs, DCLs, or tracked owner-decision artifacts |
| `platform-write` | `DENY` or `ASK` when active scope is an application and target paths belong to GT-KB platform/governance internals |

### Slice 2 - Active scope and path ownership

Add a deterministic active-scope resolver and path-ownership registry support.
The implementation should support at least:

```text
active_scope = platform:GT-KB
active_scope = application:<name>
```

The first implementation may store current local scope in a small local state
file under `.gtkb-state/` and read policy defaults from the tracked TOML
registry. Local scope state must not become release evidence by itself.

Path ownership should classify at least:

- `groundtruth-kb/**` as GT-KB platform package/source,
- `.claude/hooks/**` as governance/harness enforcement,
- `.claude/rules/**` as governance rules,
- `bridge/**` as bridge lifecycle artifacts,
- `memory/**` as operational/backlog/memory artifacts,
- `harness-state/**` as harness identity/role state,
- `applications/**` as GT-KB hosted application location,
- Agent Red references as external application-scope context unless Mike
  explicitly declares Agent Red work.

### Slice 3 - Approval receipts

Add short-lived approval receipts under local state:

- `.gtkb-state/policy/approval-receipts/`

Receipts should include:

- `receipt_id`,
- `action`,
- `scope`,
- `paths` or target,
- selected owner option,
- created timestamp,
- expiry timestamp,
- question hash,
- policy registry hash,
- harness identity or role when available.

Receipts prevent repeated AskUserQuestion prompts for the same already-approved
action while avoiding broad "yes forever" approvals. Receipts are local state,
not formal owner-decision records, unless a future proposal explicitly promotes
one.

### Slice 4 - CLI surface

Extend the existing Click CLI at `groundtruth-kb/src/groundtruth_kb/cli.py` with
a `policy` command group and `check` subcommand:

```text
gt policy check --action <action> --scope <scope> --paths <paths> --json
```

Expected JSON shape:

```json
{
  "outcome": "ASK",
  "action": "commit",
  "scope": "platform:GT-KB",
  "paths": ["bridge/INDEX.md"],
  "reason": "...",
  "ask": {
    "question": "...",
    "options": [
      {"label": "Proceed once", "description": "..."},
      {"label": "Revise scope", "description": "..."}
    ]
  },
  "receipt_required": true,
  "receipt_id": null
}
```

The command should also support human-readable output for local debugging, but
hook adapters must use JSON.

### Slice 5 - First adapters

Add thin adapters only after the policy engine and CLI are tested:

- commit adapter: checks staged/unstaged state and returns `ASK` before commit
  unless an unexpired receipt matches the action and file set.
- push adapter: checks current branch, remote, and upstream target and returns
  `ASK` or `DENY` based on policy.
- platform-write adapter: checks path ownership during observable hook events
  and returns `DENY` or `ASK` when an application-scope session targets platform
  or governance paths.

Adapters must call the central policy engine. They must not duplicate policy
tables or create a second action taxonomy.

### Out Of Scope

- No LLM/API classifier for action intent.
- No production deployment or external environment approval changes.
- No GitHub branch protection changes.
- No credential lifecycle changes.
- No Agent Red repository mutation.
- No formal artifact mutation beyond the bridge proposal/report lifecycle
  unless a later owner-approved proposal explicitly scopes it.
- No broad dashboard UI implementation in this slice, beyond leaving the policy
  check JSON stable enough for later dashboard/status integration.

## Acceptance Criteria

1. A central policy engine returns deterministic `ALLOW`, `WARN`, `ASK`, and
   `DENY` outcomes from registry, action, scope, paths, branch/remote context,
   and receipt state.
2. The policy engine has no LLM/API dependency.
3. `gt policy check` exposes the engine through the existing packaged CLI and
   supports JSON output for hooks/wrappers.
4. The policy registry includes the initial action classes listed above.
5. `ASK` outcomes provide two to three viable AskUserQuestion-ready options.
6. `DENY` outcomes do not ask; they explain the required scope or structural
   condition.
7. Active application scope blocks GT-KB platform/governance writes by default.
8. Commit and push adapters are thin callers of the central engine.
9. Approval receipts are short-lived, scoped, and registry-hash-bound.
10. Tests cover outcomes, path-scope enforcement, receipt matching/expiry,
    registry parsing, CLI JSON shape, and bypass attempts where hooks can
    observe them.

## Specification-Derived Test Plan

| Test ID | Requirement source | Verification |
|---|---|---|
| `T-bridge-index` | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` latest entry is `NEW` for this proposal, and the named file exists |
| `T-preflight` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-auq-policy-gates-001` passes before implementation |
| `T-spec-test-map` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps every linked spec to executed tests |
| `T-registry-parse` | Artifact-governance specs | TOML policy registry parses deterministically and rejects unknown outcome/action fields |
| `T-no-llm` | S332 advisory/no-LLM constraint and deterministic-services principle | Policy package imports no LLM/API client and tests monkeypatch network-sensitive classifiers absent |
| `T-outcomes` | `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Unit tests prove `ALLOW`, `WARN`, `ASK`, and `DENY` behavior |
| `T-ask-options` | `GOV-REQUIREMENTS-COLLECTION-HOOK-001`; `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` | ASK responses contain two to three bounded options suitable for AskUserQuestion |
| `T-requirements-update` | Requirements hook specs | Mutating GOV/SPEC/ADR/DCL/owner-decision surfaces returns `ASK` unless a valid receipt is present |
| `T-platform-write` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `.claude/rules/project-root-boundary.md` | Application scope attempting GT-KB platform/governance path writes returns `DENY` or configured `ASK` |
| `T-root-boundary` | `.claude/rules/project-root-boundary.md` | Policy files and local state remain inside `E:\GT-KB`; no live dependency on `E:\Claude-Playground` |
| `T-cli-json` | Existing `gt` CLI surface | `CliRunner` tests prove `gt policy check --json` output schema and exit behavior |
| `T-receipts` | Receipt acceptance criteria | Receipt tests cover creation, expiry, hash mismatch, path mismatch, and one-action-only reuse |
| `T-adapters-thin` | Advisory hook-sprawl risk | Tests or code review evidence prove commit/push adapters delegate to central engine and do not carry policy tables |

Suggested command set for the first implementation report:

```powershell
cd groundtruth-kb
python -m pytest tests/test_policy_gates.py tests/test_cli.py tests/test_owner_decision_tracker_structural_guards.py -q --tb=short
python -m ruff check src tests
python -m ruff format --check src tests
```

The exact test file names may change during implementation, but the report must
map back to the test IDs above.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Hook sprawl recreates the current problem | More token load and harder governance maintenance | Keep policy tables in one registry and make adapters thin |
| Over-gating routine local work slows development | Owner and agent fatigue | Use `ALLOW` for deterministic local status/tests/builds and scoped receipts for repeated approved actions |
| ASK outcomes become broad owner decisions | Weak auditability and unclear authority | Emit bounded two-to-three-option prompts and short-lived action receipts |
| Application/platform scope misclassification blocks legitimate platform work | False `DENY` or repeated `ASK` | Start with explicit active scope and conservative path registry; allow Prime Builder platform scope for GT-KB root work |
| Agent Red gets treated as a live GT-KB artifact | Violates current root-boundary and project separation | Treat Agent Red as external/application-scope context unless Mike explicitly declares Agent Red work |
| Policy gate bypass through raw commands | Safety remains incomplete | Cover observable hook/wrapper paths first and document residual bypasses; structural branch/environment controls remain complementary |
| Production deployment gating appears complete when it is not | Release risk | Keep production deploy external approval out of scope; policy gate can only require that external prerequisites are present |

## Recommended Review Questions

1. Does the proposed registry/action/scope model satisfy the S332 advisory
   without creating a new hook taxonomy?
2. Is commit/push/platform-write the right first adapter slice, or should the
   first `GO` be limited to registry + CLI only?
3. Are approval receipts acceptable as local state under `.gtkb-state/policy/`,
   or should the receipt location/format be narrowed before implementation?
4. Does the Agent Red/application-scope framing comply with the current
   root-boundary and canonical-terminology rules?

## Prime Builder Recommendation

Proceed with the central policy engine, registry, CLI, receipt model, and first
thin adapters for commit, push, and platform-write after Loyal Opposition `GO`.

If Loyal Opposition considers the adapter slice too broad, the fallback should
be a narrower `GO` for registry + engine + CLI + tests only, followed by a
separate bridge proposal for adapters. The important constraint is to land the
central deterministic policy surface before adding any more bespoke hooks.

