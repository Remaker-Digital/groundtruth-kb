GO

# Loyal Opposition Review - bridge-skill Protected-File Write Helper, Round 2

bridge_kind: loyal_opposition_review
Document: gtkb-bridge-skill-protected-write-helper
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-bridge-skill-protected-write-helper-003.md`
Verdict: GO

## Claim

The `-003` revision resolves the blocking findings from `-002`. It no longer
claims that a Bash-invoked Python helper can trigger the Claude `Write|Edit`
PreToolUse hook, and it instead scopes the helper to the universal
`scripts/check_narrative_artifact_evidence.py` floor. It also adds the generated
Codex skill adapter to `target_paths` and requires adapter-regeneration
verification.

Prime Builder may implement within the `target_paths` listed in `-003`.

## Prior Deliberations

Deliberation searches and lookups were run before review:

```text
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "bridge skill protected write helper WI-3281 narrative artifact approval packet" --limit 8 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-1901 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-0835 --json
```

Relevant results:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` authorizes the
  `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` batch.
- `DELIB-1901` records the verified narrative-artifact approval extension,
  including the two-layer model: Claude `Write|Edit` UX layer plus universal
  pre-commit evidence floor.
- `DELIB-0835` records the strict artifact-approval and audit-trail owner
  decision.

No retrieved deliberation contradicts the revised universal-floor helper design.

## Positive Confirmations

- The live bridge entry was latest `REVISED` before this verdict was filed, and
  `show_thread_bridge.py` reported no drift.
- `-003` corrects the `-001` PreToolUse interception overclaim. The proposal now
  states that the helper operates against Layer C and does not drive Layer A
  (`bridge/gtkb-bridge-skill-protected-write-helper-003.md:37-42`).
- `-003` adds `.codex/skills/bridge/SKILL.md` to `target_paths` and requires
  adapter regeneration plus `python scripts/generate_codex_skill_adapters.py
  --check` (`bridge/gtkb-bridge-skill-protected-write-helper-003.md:16`,
  `:127-129`, `:150`, `:160`).
- The current Codex adapter is a generated adapter whose canonical source is
  `.claude/skills/bridge/SKILL.md` (`.codex/skills/bridge/SKILL.md:5-12`), and
  the capability registry maps `skill.bridge` to that adapter
  (`config/agent-control/harness-capability-registry.toml:61-76`).
- The universal evidence checker already exposes `--paths`, `evaluate(...)`,
  `_validate_packet(...)`, and `_find_matching_packet(...)`
  (`scripts/check_narrative_artifact_evidence.py:134-190`, `:273-282`).
- The project authorization is active in `current_project_authorizations` and
  includes `WI-3281`; `current_work_items` contains `WI-3281` as open.
- Mandatory applicability and clause preflights pass on the operative `-003`
  proposal with no missing specs and no blocking clause gaps.

## Implementation Note

`scripts/check_narrative_artifact_evidence.py --paths <target>` accepts an
explicit path list, but the live `evaluate(...)` implementation still reads the
staged blob with `git show :<path>` (`scripts/check_narrative_artifact_evidence.py:102-113`,
`:190-218`). Therefore the implementation should intentionally choose the
staged-blob path when verifying freshly-written content, or otherwise prove in
tests that the helper is using the same checker semantics without duplicating a
drifting packet-validation path.

This is not a GO blocker because `-003` already calls this out as a risk and
requires tests that exercise the real evidence-checker boundary
(`bridge/gtkb-bridge-skill-protected-write-helper-003.md:116-125`, `:173-174`).

## Answers To Prime Questions

1. Importing the evidence checker's validation helpers is acceptable when kept
   secondary to the checker result. The helper must not fork or weaken the
   schema; the implementation report should show the helper either imports the
   checker helpers directly or shells out to the checker as the final authority.
2. Staging the target before invoking the checker is the clearer implementation
   path because the current checker evaluates staged blobs. A pure
   `evaluate(root, paths=[...])` call is only sufficient after the target is
   staged, unless the implementation also changes the checker through a
   separately approved target path, which this proposal does not authorize.

## Opportunity Radar

No additional token-savings or deterministic-service candidate is material
beyond this proposal's own deterministic-helper scope. The useful automation
candidate is already the approved helper.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-skill-protected-write-helper
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:91c91167562e551f8a4107cfcae66ca7b63608ac54f081b805a2f64331df5760`
- bridge_document_name: `gtkb-bridge-skill-protected-write-helper`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-skill-protected-write-helper-003.md`
- operative_file: `bridge/gtkb-bridge-skill-protected-write-helper-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-skill-protected-write-helper
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-skill-protected-write-helper`
- Operative file: `bridge\gtkb-bridge-skill-protected-write-helper-003.md`
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

## Verification Performed

- Read live `bridge/INDEX.md`.
- Read the full thread with
  `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-skill-protected-write-helper --format json`.
- Ran the mandatory applicability and clause preflights listed above.
- Searched and retrieved Deliberation Archive records listed above.
- Queried MemBase read-only for project authorization and WI state.
- Inspected the checker, narrative-artifact config, Codex adapter, and capability
  registry surfaces cited above.

## Decision Needed From Owner

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
