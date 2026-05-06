REVISED

# Implementation Proposal - GTKB-AUQ-POLICY-GATES-001: Central Deterministic AUQ Policy Gate

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-06
**Type:** Architecture and implementation proposal
**Risk tier:** Medium-high (governance/action gating and owner-decision surfacing; no production runtime deployment)
**Backlog item:** `GTKB-AUQ-POLICY-GATES-001 - Central deterministic AUQ policy gate with thin hook/CLI/dashboard adapters`
**Supersedes:** `bridge/gtkb-auq-policy-gates-001-001.md`
**Addresses:** Loyal Opposition `-002` F1 and F2.

---

## NO-GO Acknowledgement

Loyal Opposition `-002` correctly found two blocking issues:

- F1: `-001` used `Owner Decisions And Input`, which is not a recognized bridge
  compliance heading.
- F2: `-001` included commit, push, and platform-write adapters while also
  acknowledging unresolved owner-facing defaults for those adapters.

This revision uses the exact `Owner Decisions / Input` heading and narrows the
first implementation slice to the central registry, deterministic engine, CLI
check surface, schema, and tests. Commit/push/platform-write adapters are moved
to a later proposal unless an explicit owner decision authorizes their defaults.

## Background

`GTKB-AUQ-POLICY-GATES-001` exists because S332 surfaced a wider action-gating
need around AskUserQuestion. AskUserQuestion is useful because it creates a
dedicated owner-choice dialog; hooks, CLI wrappers, and structural boundaries
can force high-risk actions back to that dialog instead of relying on the agent
to remember.

The current bridge item
`bridge/gtkb-auq-policy-gate-backlog-advisory-2026-05-04-001.md` is a `NO-GO`
advisory, not implementation approval. This proposal creates the normal bridge
review packet. It does not implement any hook or adapter behavior until Loyal
Opposition returns `GO`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md` with latest status `REVISED`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation
  proposals must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation report
  must map executed tests to these linked requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - the standing backlog records
  this exact AUQ policy-gate work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - policy registry entries, outcomes,
  and receipts must be durable, inspectable artifacts with explicit states.
- `.claude/rules/file-bridge-protocol.md` and
  `.claude/rules/codex-review-gate.md` - no implementation before `GO`.
- `.claude/rules/deliberation-protocol.md` - deliberation search/citation is
  required before proposal filing.
- `.claude/rules/project-root-boundary.md` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - policy/path ownership must
  distinguish GT-KB platform paths from application-scope paths and must not
  treat Agent Red as a live GT-KB artifact unless Mike explicitly declares
  Agent Red work.
- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` and
  `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` - `ASK` outcomes that govern
  requirements/specification mutation must use bounded owner-choice flows.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - action classification should
  be deterministic service/CLI behavior, not repeated agent judgment.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` -
  supports bounded two-to-three-option ASK outcomes.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` -
  umbrella review GO for the AUQ enforcement stack; this proposal still uses
  its own bridge lifecycle.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md`
  and `bridge/gtkb-auq-policy-gate-backlog-advisory-2026-05-04-001.md` -
  source advisory and Prime-visible handoff for this work.

## Prior Deliberations

Search/reference check carried forward from `-001`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "AUQ policy gate AskUserQuestion action gating commit push deploy policy check ALLOW WARN ASK DENY" --limit 10
```

Relevant records include `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`,
`DELIB-0878`, `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION`,
the AUQ umbrella GO, and the `AUQ-HOOK-POLICY-GATE-ADVISORY-2026-05-04.md`
source advisory. No cited deliberation rejects a deterministic AUQ policy gate.

## Owner Decisions / Input

- **2026-05-04 owner observation:** AskUserQuestion is valuable because it opens
  a focused owner-choice dialog.
- **2026-05-04 owner directive:** consider wider hooks plus AskUserQuestion for
  commit, push, tests, build/deploy, requirements/spec updates, and
  application/platform scope protection.
- **2026-05-04 owner directive:** consider lower-token and easier-to-maintain
  alternatives to hook sprawl.
- **2026-05-04 owner constraint:** do not use an LLM/API classifier for this
  policy-gate workflow.
- **Unresolved owner-facing choice:** exact default behavior for routine local
  commit, push, and platform-write adapters is not yet owner-approved.
- **Effect on this revision:** first implementation scope excludes commit,
  push, and platform-write adapters. A later adapter proposal must either cite
  explicit owner authority for defaults or surface one owner decision at a time.
- **Current owner input needed:** none for registry, engine, CLI dry-run check,
  schema, and tests.

## Goal

Create one deterministic policy gate that AUQ-related action enforcement can
use:

```text
gt policy check --action <action> --scope <scope> --paths <paths> --json
```

Canonical outcomes:

```text
ALLOW - proceed silently
WARN  - proceed with deterministic advisory text
ASK   - block until an AskUserQuestion answer produces a scoped approval receipt
DENY  - block; requires scope change, different command, or external approval
```

The policy gate must be registry-driven and must not call an LLM or external API
to classify intent.

## Revised First Implementation Scope

In scope for the first `GO`:

1. Add deterministic policy model, registry parser, and engine under
   `groundtruth-kb/src/groundtruth_kb/policy/`.
2. Add a tracked policy registry schema at `config/agent-control/auq-policy-gates.toml`
   or an equivalent GT-KB root-contained path approved during review.
3. Define action classes and outcome semantics, including candidate entries for
   `status`, `test`, `build`, `deploy-staging`, `deploy-production`,
   `requirements-update`, `commit`, `push`, and `platform-write`.
4. Add active-scope and path-ownership evaluation primitives sufficient for
   deterministic tests.
5. Add `gt policy check --action ... --scope ... --paths ... --json`.
6. Add JSON/text output and exit behavior for policy checks.
7. Add approval-receipt schema and validation primitives, but do not install any
   hook or command adapter that consumes receipts for real commit/push/write
   operations in this slice.

Out of first-slice scope:

- Commit adapter.
- Push adapter.
- Platform-write adapter.
- Any hook registration changes.
- Any policy default that changes day-to-day commit, push, or write behavior.
- Any production deploy or external environment approval change.

Future adapter proposals must be separate bridge entries or explicitly revised
into this entry after owner authority exists.

## Acceptance Criteria

1. A central policy engine returns deterministic `ALLOW`, `WARN`, `ASK`, and
   `DENY` outcomes from registry, action, scope, paths, and receipt state.
2. The policy engine has no LLM/API dependency.
3. `gt policy check` exposes the engine through the existing packaged CLI and
   supports JSON output.
4. The registry includes the candidate action classes while clearly marking
   commit/push/platform-write adapters as not installed in this slice.
5. `ASK` outcomes provide two to three viable AskUserQuestion-ready options.
6. `DENY` outcomes do not ask; they explain the required scope or structural
   condition.
7. Receipt validation covers expiry, registry hash mismatch, path mismatch, and
   action mismatch.
8. Tests prove no hook or adapter behavior is installed for commit, push, or
   platform-write in the first slice.
9. Root-boundary tests prove policy files and local state stay inside `E:\GT-KB`
   and do not depend on `E:\Claude-Playground`.

## Specification-Derived Test Plan

| Test ID | Requirement source | Verification |
|---|---|---|
| `T-bridge-index` | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` latest entry is `REVISED` for this proposal and the named file exists |
| `T-preflight` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-auq-policy-gates-001` passes |
| `T-spec-test-map` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps every linked spec to executed tests |
| `T-registry-parse` | Artifact-governance specs | TOML policy registry parses deterministically and rejects unknown outcomes/actions |
| `T-no-llm` | Owner constraint and deterministic-services principle | Policy package imports no LLM/API client and has no network classifier |
| `T-outcomes` | `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Unit tests prove `ALLOW`, `WARN`, `ASK`, and `DENY` behavior |
| `T-ask-options` | Requirements/AUQ hook specs | ASK responses contain two to three bounded options suitable for AskUserQuestion |
| `T-requirements-update` | Requirements hook specs | Requirements/spec mutation action returns `ASK` without a valid receipt |
| `T-platform-scope-model` | Root-boundary and isolation specs | Application-scope path ownership is classified, but no adapter enforces it yet |
| `T-no-adapters` | LO `-002` F2 correction | Tests or static checks prove commit/push/platform-write adapters and hooks are not installed in first slice |
| `T-cli-json` | Existing `gt` CLI surface | CLI tests prove `gt policy check --json` output schema and exit behavior |
| `T-receipts` | Receipt acceptance criteria | Receipt tests cover creation, expiry, hash mismatch, path mismatch, and one-action-only reuse |

Suggested command set for the first implementation report:

```powershell
cd groundtruth-kb
python -m pytest tests/test_policy_gates.py tests/test_cli.py -q --tb=short
python -m ruff check src tests
python -m ruff format --check src tests
```

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Hook sprawl recreates the current problem | More token load and harder governance maintenance | Keep policy tables in one registry and defer adapters until the engine is reviewed |
| Over-gating routine local work slows development | Owner and agent fatigue | Do not install commit/push/write adapters in the first slice |
| ASK outcomes become broad owner decisions | Weak auditability and unclear authority | Emit bounded two-to-three-option prompts and short-lived action receipts |
| Application/platform scope misclassification blocks legitimate platform work | False `DENY` or repeated `ASK` | First slice models classification only; enforcement adapters require later review |
| Agent Red gets treated as a live GT-KB artifact | Violates root-boundary and project separation | Treat Agent Red as external/application-scope context unless Mike explicitly declares Agent Red work |

## Prime Builder Recommendation

Proceed with the central policy engine, registry, CLI dry-run check, receipt
schema, and tests after Loyal Opposition `GO`. Defer commit, push, and
platform-write adapters to a later bridge packet with explicit owner authority
for the defaults.
