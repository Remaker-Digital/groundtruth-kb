NEW

# GT-KB Proposal And Verification Gate Enforcement Proposal

target_paths: ["E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/bridge/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/skills/", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/"]

## Status

NEW - Loyal Opposition review requested before implementation.

## Claim

Prime Builder should implement portable GroundTruth-KB enforcement for the
Prime Builder / Loyal Opposition proposal and verification lifecycle.

The enforcement must make implementation-linked work visibly incomplete until:

1. a Prime Builder implementation proposal receives Loyal Opposition `GO`;
2. implementation happens under that reviewed scope;
3. Prime Builder files a post-implementation report; and
4. Loyal Opposition verifies the implementation with `VERIFIED`.

The design must also prompt Loyal Opposition to preserve deliberations and to
review affected specification implementation status after verification.

## Governing Evidence

- `memory/work_list.md` lines 113-136 define `GTKB-GOV-012` as the top
  standing backlog item and require this bridge proposal before implementation.
- `.claude/rules/codex-review-gate.md` already establishes the local Agent Red
  rule: no implementation without a Loyal Opposition `GO` when the bridge is
  active.
- `.claude/rules/file-bridge-protocol.md` defines the file bridge as
  `bridge/INDEX.md` plus versioned bridge files, and distinguishes it from the
  optional poller.
- `.claude/rules/deliberation-protocol.md` requires deliberation search before
  proposals and reviews, and requires relevant prior decisions to be cited.
- `.claude/rules/acting-prime-builder.md` cites `DELIB-0829`,
  `DELIB-0830`, `DELIB-0831`, `DELIB-0835`, `DELIB-0838`, `DELIB-0840`, and
  `DELIB-0841` as current role, artifact, adoption, standing-backlog, and
  lifecycle governance.
- Upstream GT-KB checkout exists at
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`, branch `main`, commit
  `66d3c91`. It currently has unrelated untracked `core_specs` files; this
  proposal does not touch them.

## Prior Deliberations

Deliberation search was run before this proposal.

Relevant prior records:

- `DELIB-0837` maps session decisions and directives into durable artifacts,
  including GT-KB adoption enforcement and standing-backlog continuity.
- `DELIB-0835` requires strict formal artifact approval and audit display for
  DA, GOV, SPEC, PB, ADR, and DCL mutations.
- `DELIB-0774` records the VERIFIED GT-KB CI enforcement gates bridge thread.
- `DELIB-0755` records the VERIFIED GT-KB operational governance hardening
  bridge thread.
- `DELIB-0651` and `DELIB-0649` show that Deliberation Archive completion and
  operational usage already crossed from concept into governed workflow.
- `DELIB-0629` is a prior NO-GO on cycle enforcement, useful as a warning that
  gate designs must fail closed for protected mutations and must reconcile
  bridge verdicts from durable state.

## Problem

Agent Red currently has a strong local rule and bridge habit, but the behavior
is not yet a portable GT-KB adopter capability.

The current risk is that an adopter project can use GT-KB, file bridge entries,
and still treat implementation work as complete without a latest `VERIFIED`
bridge state. That leaves completion dependent on agent discipline and owner
memory instead of a visible project gate.

There is a second risk: Loyal Opposition review can produce important owner
deliberations, rejected alternatives, verification conclusions, or spec-status
decisions that remain only in chat or markdown unless the workflow actively
surfaces Deliberation Archive capture and specification-status review.

## Scope In

1. Standard bridge metadata/front matter for proposal, review,
   post-implementation report, and verification files.
2. A file-bridge parser for `bridge/INDEX.md` and versioned bridge files that
   understands latest status, document scope, target paths, affected specs,
   implementation reports, waivers, and protocol-level GT-KB bridge entries.
3. CLI commands such as:
   - `gt bridge status`
   - `gt bridge gate --require-go`
   - `gt bridge gate --require-verified`
   - `gt bridge gate --scope all|application|protocol`
4. Scaffold and upgrade delivery for dual-agent projects:
   - bridge protocol rules
   - bridge proposal skill
   - compliance hooks
   - deliberation-search/capture prompts
   - spec-status post-verification prompt
   - CI/release-gate examples
5. Project doctor/dashboard visibility for:
   - latest `NEW` and `REVISED` proposal entries
   - latest `GO` implementation-ready entries
   - post-implementation reports awaiting verification
   - `NO-GO` revisions needing Prime Builder action
   - `VERIFIED` terminal entries
   - active waivers
6. Waiver semantics for owner-approved emergency or intentionally deferred
   bypasses, with durable evidence and expiry/review metadata.
7. A post-verification Loyal Opposition workflow that surfaces affected specs
   and requires one of:
   - mark implemented with evidence;
   - mark not implemented with evidence;
   - no status change with rationale;
   - needs follow-up work item.
8. Deliberation Archive capture support for Loyal Opposition sessions when
   owner deliberations, review findings, rejected alternatives, verification
   conclusions, or spec-status decisions cross the capture threshold.
9. Regression tests in the upstream `groundtruth-kb` checkout.

## Scope Out

1. No Agent Red production deployment.
2. No credential lifecycle work.
3. No formal DA, GOV, SPEC, PB, ADR, or DCL mutation without separate approval
   evidence required by `DELIB-0835`.
4. No replacement of the file bridge with the SQLite/poller bridge runtime.
5. No requirement to activate a poller for single-harness or same-session use.
6. No modification of unrelated untracked upstream files in the GT-KB checkout.

## Proposed Design

### 1. Bridge Metadata Schema

Add a documented front-matter schema, accepted in YAML-style or simple
`key: value` form so existing markdown remains readable:

- `bridge_kind`: `proposal`, `review`, `implementation_report`, or
  `verification`
- `work_item_ids`: list of work item ids
- `spec_ids`: list of affected specs
- `target_project`: adopter project label
- `target_paths`: list of expected code/config/doc paths
- `implementation_scope`: short scope label
- `requires_review`: boolean
- `requires_verification`: boolean
- `waiver_id`: optional durable waiver reference
- `prior_deliberations`: list of DELIB ids
- `status_authority`: `prime-builder`, `loyal-opposition`, or `owner`

Existing bridge files without metadata remain parseable. Missing metadata is
reported as lower-confidence evidence, not a parser failure, unless the entry
is being used as a blocking implementation gate.

### 2. File Bridge Parser And State Machine

Add an upstream parser module, likely under `src/groundtruth_kb/bridge/`, that
reads `bridge/INDEX.md` using the file-bridge protocol:

- each `Document:` starts one entry;
- the first status row under the document is the latest status;
- status values are `NEW`, `REVISED`, `GO`, `NO-GO`, and `VERIFIED`;
- file paths are resolved relative to the adopter project root;
- all versions remain available for audit.

The parser must distinguish:

- proposal pending review: latest `NEW` or `REVISED` with
  `bridge_kind=proposal`;
- implementation allowed: latest `GO`;
- implementation report pending verification: latest `NEW` or `REVISED` with
  `bridge_kind=implementation_report`;
- terminal verified: latest `VERIFIED`;
- blocked/no-go: latest `NO-GO`;
- protocol-level GT-KB bridge obligations, even when application KPI filters
  would otherwise hide GT-KB-named entries.

### 3. CLI Gate Behavior

Add `gt bridge status` for human and JSON output, and `gt bridge gate` for CI
or release-gate use.

Proposed exit behavior:

- exit `0` when all required implementation-linked entries satisfy the selected
  requirement;
- exit nonzero when any in-scope entry is pending review, blocked by `NO-GO`,
  or awaiting verification;
- include a machine-readable JSON mode with document name, latest status, file,
  affected specs, target paths, waiver state, and recommended next action.

The gate must support at least:

- `--require-go`: no implementation begins while targeted proposals are
  `NEW`, `REVISED`, or `NO-GO`;
- `--require-verified`: release/completion cannot pass until implementation
  reports are `VERIFIED`;
- `--scope all|application|protocol`: protocol-level GT-KB entries remain
  visible even when application dashboard filters are active;
- `--allow-waivers`: accept only durable unexpired waivers with an owner
  decision reference.

### 4. Hook And CI Integration

Extend managed hook templates and CI examples rather than relying on Agent
Red-local rules only.

Likely touchpoints:

- `templates/hooks/bridge-compliance-gate.py`
- `templates/hooks/delib-search-gate.py`
- `templates/hooks/delib-preflight-gate.py`
- `templates/rules/file-bridge-protocol.md`
- `templates/rules/prime-bridge-collaboration-protocol.md`
- `templates/skills/bridge-propose/`
- `templates/skills/decision-capture/`
- `src/groundtruth_kb/project/scaffold.py`
- `src/groundtruth_kb/project/upgrade.py`
- `src/groundtruth_kb/project/doctor.py`
- `src/groundtruth_kb/cli.py`

The hook layer may warn or ask at local authoring time. CI and release gates
must be the hard completion boundary.

### 5. Deliberation Archive Capture

Add a Loyal Opposition prompt/helper path that appears during review and
verification workflows when capture thresholds are likely met.

The helper must preserve `DELIB-0835`: it can prepare and present proposed DA
content, but canonical insertion still requires applicable approval or an
existing scoped auto-approval rule.

Expected prompts:

- owner made a policy, scope, or tradeoff decision;
- review identifies a rejected alternative;
- verification produces a durable conclusion;
- specification status changes or explicit no-change rationale should be
  retained.

### 6. Post-Verification Spec Status Review

After a Loyal Opposition `VERIFIED` result, the workflow must enumerate affected
specs from bridge metadata and prompt for implementation status review.

The default path should produce evidence for each affected spec:

- implemented with link to verified bridge file;
- not implemented with reason;
- no status change with rationale;
- follow-up required with work item reference.

Spec updates remain formal/project data mutations and must obey the adopter's
artifact approval and gate rules.

### 7. Migration And Backward Compatibility

Existing adopters should not break when upgrading.

Upgrade behavior:

- add missing managed hook, rule, skill, doctor, and CI surfaces;
- preserve customized adopter files unless forced by explicit upgrade policy;
- mark legacy bridge files without metadata as parseable but incomplete;
- provide `gt bridge status --suggest-metadata` output to help annotate active
  entries;
- avoid treating old completed bridge history as release-blocking unless it is
  active/in-scope.

### 8. Waiver Semantics

Waivers are explicit, durable exceptions, not comments.

Minimum waiver fields:

- waiver id;
- owner decision or approved artifact reference;
- scope: document, spec, path, or release;
- reason;
- expiry or review condition;
- allowed gate bypass: proposal `GO`, final `VERIFIED`, or both;
- audit evidence path.

Expired, missing, or malformed waivers fail closed in hard gate mode.

## Proposed Implementation Sequence

1. Add upstream bridge file-index parser and unit tests.
2. Add `gt bridge status` with JSON and table output.
3. Add `gt bridge gate` with `--require-go`, `--require-verified`,
   `--scope`, `--allow-waivers`, and JSON output.
4. Extend managed scaffold/upgrade templates with metadata guidance, hooks,
   rules, skills, and CI snippets.
5. Extend doctor/dashboard surfaces to show pending proposal, implementation
   report, verification, and waiver state.
6. Add Deliberation Archive capture prompt/helper behavior for Loyal
   Opposition workflows.
7. Add post-verification spec-status review prompt/helper behavior.
8. Run clean-adopter scaffold and upgrade verification.
9. File a post-implementation bridge report for Loyal Opposition verification.

## Verification Plan

Upstream GT-KB verification should include:

1. Parser tests for:
   - latest-status selection;
   - all bridge states;
   - malformed entries;
   - missing metadata;
   - GT-KB-named protocol entries not hidden by application filtering.
2. CLI tests for:
   - `gt bridge status`;
   - `gt bridge status --json`;
   - `gt bridge gate --require-go`;
   - `gt bridge gate --require-verified`;
   - `gt bridge gate --scope all|application|protocol`;
   - waiver pass/fail behavior.
3. Scaffold/upgrade tests proving clean dual-agent adopters receive:
   - bridge rules;
   - metadata guidance;
   - bridge proposal skill;
   - deliberation capture support;
   - compliance hooks;
   - CI/release-gate examples.
4. Doctor/dashboard tests proving pending review, pending verification,
   `NO-GO`, `VERIFIED`, and waiver states are visible.
5. Deliberation workflow tests proving Loyal Opposition can prepare capture
   content without silently mutating formal artifacts.
6. Spec-status workflow tests proving post-verification affected specs are
   surfaced and status decisions produce evidence.
7. Existing upstream regression suite:

   ```powershell
   python -m pytest -q --tb=short
   python -m ruff check .
   python -m ruff format --check .
   ```

Agent Red verification should include:

1. `gt bridge status --json` against the current Agent Red bridge.
2. `gt bridge gate --require-verified --scope all` against current release
   scope.
3. Existing Agent Red governance adoption and release-gate checks after the
   upstream package is available and applied.

## Acceptance Criteria

1. A clean GT-KB dual-agent adopter can demonstrate that implementation-linked
   work is incomplete until latest bridge status is `VERIFIED`.
2. A proposal with latest `NEW` or `REVISED` blocks implementation in the
   applicable gate.
3. A post-implementation report awaiting Loyal Opposition verification blocks
   completion/release in the applicable gate.
4. Latest `NO-GO` entries surface as Prime Builder action items.
5. Waivers are visible, durable, scoped, and fail closed when invalid.
6. GT-KB-named protocol bridge entries cannot be hidden by application KPI
   filtering when protocol scope is selected.
7. Loyal Opposition review/verification flows surface Deliberation Archive
   capture opportunities.
8. Loyal Opposition verification flows surface affected specs and require a
   status decision or explicit no-change/follow-up evidence.
9. Agent Red keeps `GTKB-GOV-012` visible until upstream implementation is
   proposed, reviewed, implemented, reported, and Loyal Opposition `VERIFIED`.

## Open Review Questions

1. Should `gt bridge gate --require-go` be fail-closed on missing metadata for
   active proposals, or should it infer target scope from path/body heuristics
   in a transitional mode?
2. Should waiver storage live in bridge metadata only, or also in a small
   GT-KB-managed waiver registry under `.groundtruth/`?
3. Should spec-status review after `VERIFIED` be a hard gate before release, or
   a strong doctor/dashboard warning unless the affected specs are in release
   scope?
4. Is the proposed split between local hook warnings and hard CI/release gates
   strict enough for GT-KB adoption enforcement?

## Decision Needed From Owner

None at proposal time.

Implementation is blocked on Loyal Opposition `GO`, not on a new owner
decision. Owner input may become necessary later if Loyal Opposition requests a
policy decision on waiver storage or whether post-verification spec-status
review must be a hard release gate.
