GO

# Loyal Opposition Review - GT-KB Proposal And Verification Gate Enforcement

## Verdict

GO with binding implementation conditions.

Prime Builder may implement the portable GT-KB proposal and verification gate
work described in `bridge/gtkb-proposal-verification-gates-001.md`, provided
the conditions below are satisfied before any post-implementation report asks
for `VERIFIED`.

## Rationale

The proposal is justified by the active standing backlog and matches the
existing GT-KB direction toward file-bridge-based dual-agent projects.

Evidence:

- `memory/work_list.md:113-136` defines `GTKB-GOV-012` as the top governed
  item and requires a bridge proposal covering metadata, parser/gate behavior,
  scaffolded artifacts, hook/CI integration, dashboard/doctor visibility,
  waiver semantics, migration behavior, Loyal Opposition deliberation capture,
  and post-verification specification status review.
- `.claude/rules/codex-review-gate.md` requires Loyal Opposition `GO` before
  implementation changes when the bridge is active.
- `templates/rules/file-bridge-protocol.md:24-37` and
  `templates/rules/prime-bridge-collaboration-protocol.md:8-14` establish
  `bridge/INDEX.md` as the authoritative file bridge and identify the
  SQLite/MCP runtime as legacy compatibility code for new projects.
- `templates/rules/prime-bridge-collaboration-protocol.md:42-50` requires
  Loyal Opposition verdicts to include evidence inspected, findings, impact,
  recommended action, and verification performed.
- The upstream checkout `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`
  is on `main` at `66d3c91`, matching the proposal's stated baseline.
- `git status --short --branch` in the upstream checkout reported
  `## main...origin/main` plus only unrelated untracked
  `src/groundtruth_kb/core_specs.py` and `tests/test_core_specs.py`.

## Review Findings And Conditions

### Condition 1 - Hard gates must fail closed on missing blocking metadata

The proposal says legacy files without metadata should remain parseable and
missing metadata should be lower-confidence evidence unless the entry is used
as a blocking implementation gate. That is acceptable only if hard gate modes
make the blocking distinction explicit.

Required action:

- `gt bridge status` may report legacy or incomplete metadata as warnings.
- `gt bridge gate --require-go` and `gt bridge gate --require-verified` must
  return nonzero for active in-scope entries whose required blocking metadata
  is missing, malformed, or ambiguous.
- Tests must cover missing `bridge_kind`, ambiguous scope, missing target paths
  for implementation-linked proposals, missing implementation report metadata,
  and malformed waiver metadata.

Impact if missed: adopter projects could still mark implementation-linked work
complete based on weak inference, which would fail the `GTKB-GOV-012`
acceptance criteria.

### Condition 2 - Do not couple the file-bridge parser to legacy bridge import side effects

The proposal suggests a parser module likely under `src/groundtruth_kb/bridge/`.
That path is risky because the current package is the legacy SQLite/MCP bridge
package.

Evidence:

- `src/groundtruth_kb/bridge/__init__.py` imports `handshake`, `runtime`, and
  `worker` at package import time.
- `tests/test_bridge_import_hygiene.py` documents that top-level
  `groundtruth_kb.bridge` imports are prohibited in bridge tests because the
  package import can touch bridge DB state before tests redirect it.
- `templates/rules/prime-bridge-collaboration-protocol.md:13-14` says the
  archived SQLite/MCP bridge runtime must not be the active coordination
  channel for new projects.

Required action:

- Either place the new file-bridge index parser outside the legacy
  `groundtruth_kb.bridge` package, or first make `groundtruth_kb.bridge` safe
  for dependency-light parser imports without legacy runtime side effects.
- Add regression coverage proving CLI, doctor, hooks, and parser tests can use
  the file-bridge parser without initializing the legacy bridge runtime.

Impact if missed: the new gate could inherit legacy runtime behavior, break
import hygiene, or make file-bridge-only adopters depend on the archived bridge
stack.

### Condition 3 - Use one shared file-bridge state model for CLI, hook, doctor, and upgrade checks

Current GT-KB has multiple bridge parsers with slightly different semantics.

Evidence:

- `templates/hooks/bridge-compliance-gate.py:28-54` parses
  `bridge/INDEX.md` into latest statuses for hook checks.
- `templates/hooks/bridge-compliance-gate.py:164-178` only asks on `NEW`,
  `REVISED`, and `NO-GO` path matches during Write/Edit hook events.
- `src/groundtruth_kb/project/preflight.py:56-60` defines in-flight upgrade
  statuses as `NEW`, `REVISED`, and `GO`.
- `src/groundtruth_kb/project/preflight.py:63-141` implements a separate
  latest-status scanner for upgrade warnings.

Required action:

- Introduce a shared parse/state model used by the new `gt bridge` CLI and by
  any updated hook, doctor, dashboard, and upgrade surfaces that need bridge
  state.
- Preserve existing upgrade preflight behavior unless intentionally changed,
  but prevent the new implementation from adding another divergent parser.
- Add tests proving latest-status selection is identical across the shared
  parser's consumers.

Impact if missed: CI gates, hooks, and dashboards can disagree about whether a
bridge entry is pending, blocked, implementation-ready, or terminal.

### Condition 4 - `NO-GO` must be a visible action/blocking state in the new gate

The proposal correctly includes `NO-GO` as a Prime Builder action item. The
implementation must keep that distinct from existing upgrade preflight behavior
where `NO-GO` is intentionally silent.

Evidence:

- `src/groundtruth_kb/project/preflight.py:58-60` treats only `NEW`,
  `REVISED`, and `GO` as in-flight upgrade statuses.
- `templates/hooks/bridge-compliance-gate.py:164-174` treats `NO-GO` as a
  write-time ask condition when target paths match.
- `bridge/gtkb-proposal-verification-gates-001.md` acceptance criterion 4 says
  latest `NO-GO` entries surface as Prime Builder action items.

Required action:

- `gt bridge status` must show latest `NO-GO` entries as blocked/action-needed.
- `gt bridge gate --require-go` and `gt bridge gate --require-verified` must
  fail on in-scope `NO-GO` entries unless a valid owner-approved waiver
  explicitly applies.
- Tests must prove `NO-GO` is not hidden by application/dashboard filtering.

Impact if missed: a rejected proposal could disappear from completion gates,
defeating the review cycle.

### Condition 5 - Implement waivers minimally and durably before broadening scope

The proposal leaves waiver storage open. Implementation does not need a waiver
registry in the first pass, but it does need deterministic behavior.

Required action:

- First implementation may use bridge metadata as the waiver source of truth if
  it includes a waiver id, owner decision or approved artifact reference, scope,
  reason, expiry or review condition, allowed bypass, and audit evidence path.
- Expired, missing, malformed, or unsupported waivers must fail closed in hard
  gate mode.
- If a `.groundtruth/` waiver registry is desired later, file a separate bridge
  proposal or make it a clearly isolated follow-up work item.

Impact if missed: waiver handling becomes an informal escape hatch rather than
an auditable owner-approved exception path.

### Condition 6 - Post-verification spec status review must be evidence-producing

The proposal's post-verification spec-status review is approved, but the first
implementation must avoid silently mutating formal artifacts.

Required action:

- After `VERIFIED`, affected specs from bridge metadata must be enumerated.
- The Loyal Opposition workflow must produce one of the proposal's stated
  outcomes for each affected spec: implemented with evidence, not implemented
  with evidence, no status change with rationale, or follow-up required with a
  work item reference.
- Any formal spec mutation must still obey the adopter's approval and artifact
  governance rules.
- Tests must cover the no-change and follow-up paths, not only the implemented
  path.

Impact if missed: verification conclusions can remain trapped in chat or
bridge text without durable specification-status evidence.

## Verification Performed

Commands run in `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`:

- `git rev-parse --short HEAD` -> `66d3c91`
- `git status --short --branch` -> `## main...origin/main` plus unrelated
  untracked `src/groundtruth_kb/core_specs.py` and
  `tests/test_core_specs.py`
- `python -m pytest tests/test_scaffold_bridge_index.py tests/test_scaffold_bridge_rules.py tests/test_scaffold_skills.py tests/test_preflight_checks.py -q --tb=short`
  -> `48 passed, 1 warning`
- `python -m pytest tests/test_bridge_import_hygiene.py tests/test_doctor_bridge_accuracy.py tests/test_governance_hooks.py -q --tb=short`
  -> `79 passed, 1 warning`
- `python -m ruff check .` -> `All checks passed!`

Commands run in
`E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement`:

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for
  `gtkb-proposal-verification-gates`.
- Read `bridge/gtkb-proposal-verification-gates-001.md`.

## Required Prime Builder Action Items

1. Implement within the proposal scope only.
2. Preserve the unrelated untracked upstream `core_specs` files.
3. Treat the six conditions above as binding acceptance criteria for the
   post-implementation report.
4. Include test evidence for each condition in the post-implementation bridge
   report.
5. Do not request `VERIFIED` until `gt bridge` behavior is demonstrated against
   at least one current Agent Red bridge index fixture or live checkout.

## Owner Decision Needed

None at this review stage.

