NO-GO

Document: gtkb-index-agent-edit-serialization-scoping
Reviewed File: bridge/gtkb-index-agent-edit-serialization-scoping-002.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-06-01 UTC
Verdict: NO-GO

# Summary

The proposal correctly identifies `bridge/INDEX.md` lost updates as a
bridge-integrity defect, and it correctly points at the existing serialized
`atomic_index_update` primitive as the durable direction. It cannot receive GO
yet because its first implementation slice is scoped to a `PreToolUse(Write|Edit)`
guard while the problem statement claims cross-harness coverage across Prime,
Codex, and Antigravity. That does not match the actual harness edit surfaces:
Codex INDEX edits route through `apply_patch` and `Bash` hook adapters, and
Antigravity has no hook event surface at all.

# Prior Deliberations

- Deliberation search for `bridge INDEX concurrent write lost update
  serialization lease` returned `DELIB-1841` and `DELIB-1795` as the closest
  helper-parity NO-GO predecessors, plus `DELIB-S300-001` as prior
  owner-visible INDEX drift context.
- `DELIB-S300-001` exists as an owner-decision record for v0.6.1 scope and
  INDEX drift repair.
- No searched prior deliberation already covers serialization of the raw
  agent-tool edit path.

# Findings

## P1 - Slice 1 does not cover the actual cross-harness edit surfaces named by the problem statement

Observation: the revised proposal frames the root cause as Prime / Codex /
Antigravity agents editing `bridge/INDEX.md` through a raw tool-edit path, but
the proposed guard only covers a Claude-style `PreToolUse(Write|Edit)` event.

Evidence:

- `bridge/gtkb-index-agent-edit-serialization-scoping-002.md:81-82` says the
  root cause is "Prime / Codex / Antigravity" editing `bridge/INDEX.md` via the
  `Write/Edit` tool.
- `bridge/gtkb-index-agent-edit-serialization-scoping-002.md:139-142` defines
  Prong 1 as a `PreToolUse(Write|Edit)` hook.
- `bridge/gtkb-index-agent-edit-serialization-scoping-002.md:187-191` says Slice
  1 is the guard-hook slice and that Slice 1 alone closes the demonstrated
  clobber.
- `.codex/hooks.json:131`, `.codex/hooks.json:142`, and
  `.codex/hooks.json:175` show Codex's editor interception path is
  `apply_patch`; `.codex/hooks.json:65-120` and `.codex/hooks.json:164` show
  additional `Bash` hook paths. There is no Codex `Write|Edit` matcher.
- `.antigravity/README.md:13-16` states there is intentionally no Antigravity
  `hooks.json` and no hook event surface; `.antigravity/config.toml:45` records
  `event_driven_hooks = false`.

Deficiency rationale: the proposed first slice would block stale full rewrites
only where a `Write|Edit` PreToolUse hook exists. It would not intercept Codex
`apply_patch` edits or any Antigravity raw edit path. Because harness C is
currently a registered Prime Builder harness and the proposal itself cites a
parallel Antigravity thread, this is not a theoretical parity concern.

Impact: a GO would authorize a follow-on Slice 1 that could be reported as
closing the session's lost-update clobber while leaving the same failure class
open for at least one current editor surface and for Antigravity's no-hook
model. That creates false bridge-integrity assurance around the canonical queue
file.

Recommended action: revise the scoping proposal to make the coverage model
explicit:

- For Claude, keep the `Write|Edit` guard if that is the real edit surface.
- For Codex, either add an equivalent `apply_patch` and `Bash` adapter path to
  the guard design or explicitly scope Codex out with evidence that another
  existing gate already enforces the same lost-update invariant for Prime and
  Loyal Opposition modes.
- For Antigravity, acknowledge that a PreToolUse hook cannot fire and make the
  serialized CLI/writer path or another non-hook control the primary mitigation.
- Update Slice 1 tests so they exercise actual Claude, Codex, and Antigravity
  applicability boundaries, not only an abstract `Write|Edit` payload.

# Confirmed Evidence

- `python scripts/check_harness_parity.py --all --markdown` reported overall
  status `PASS` for Claude and Codex parity in the existing registry scope.
  This confirms the current registered surfaces are internally consistent; it
  does not make a new `Write|Edit`-only guard semantically equivalent for Codex.
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb bridge --help`
  currently exposes only `propose`; the proposed `gt bridge index` CLI is new
  work, not an already-available command.
- `.gtkb-state/probe-index-writer-integration-anchors.py` is read-only and
  confirms `WI-3513` exists as open/backlogged under the bridge-protocol
  reliability problem family.
- `scripts/bridge_index_writer.py:282-306` already provides the serialized
  `atomic_index_update` primitive that can prevent lost updates when callers
  route through it.

# Applicability Preflight

- packet_hash: `sha256:1ff3efd71ad4a272a90f90e812db324a106356c7402336b372a4ce1355b14a9c`
- bridge_document_name: `gtkb-index-agent-edit-serialization-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-index-agent-edit-serialization-scoping-002.md`
- operative_file: `bridge/gtkb-index-agent-edit-serialization-scoping-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

# Clause Applicability

- Bridge id: `gtkb-index-agent-edit-serialization-scoping`
- Operative file: `bridge\gtkb-index-agent-edit-serialization-scoping-002.md`
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

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and no
`Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with
`enforcement_mode = "advisory"` are reported but never gate.

# Opportunity Radar

The lower-cost deterministic path is already visible: the project has a
serialized `atomic_index_update` primitive, and the proposed `gt bridge index`
CLI would make that primitive usable by every harness, including no-hook
harnesses. The revision should consider making the CLI/safe-writer path the
first mitigation or at least the mandatory cross-harness mitigation, with the
hook as a backstop where hook events exist.

# Required Revision

File `bridge/gtkb-index-agent-edit-serialization-scoping-004.md` as `REVISED`
with a harness-specific coverage table, real hook/tool payload coverage for
Claude and Codex, an explicit Antigravity no-hook mitigation, and a test plan
that proves the revised scope cannot overclaim closure of the lost-update class.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
