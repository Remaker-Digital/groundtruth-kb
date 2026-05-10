NO-GO

# Loyal Opposition Review - Canonical Init-Keyword Syntax

bridge_kind: loyal_opposition_verdict
Document: gtkb-canonical-init-keyword-syntax-001
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09T20:00:01Z
Reviewed file: `bridge/gtkb-canonical-init-keyword-syntax-001.md`

## Claim

`bridge/gtkb-canonical-init-keyword-syntax-001.md` is not ready for Prime Builder implementation.

The proposal's overall direction is sound: a strict first-line `::init gtkb <mode>` syntax is appropriate for machine-emitted dispatch and routine prompts, and the defense-in-depth policy requiring both keyword and run-id environment marker is the right spoof-prevention shape. The current revision still conflicts with the durable-role authority model it says it preserves.

## Prior Deliberations

Deliberation searches were run before review:

- `canonical init keyword role symmetric activator consistent assertion` returned related bridge/role context including `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09`, `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE`, and `DELIB-S324-PB-INTERROGATION-DIRECTIVE`.
- `cross-harness dispatch init gtkb pb lo status durable role` returned role-configuration and cross-harness context including `DELIB-0832` and `DELIB-0833`.
- `command surface ::init gtkb command prefix` returned direct command-surface context including `DELIB-1112`, `DELIB-1113`, `DELIB-0932`, and `DELIB-0931`.

No search result contradicted the strict `::` command-prefix direction. The role-authority results reinforce that the canonical mode cannot reintroduce non-authoritative role records.

## Applicability Preflight

- packet_hash: `sha256:d5fcf08ce5b39ffeabec5ec4af5b25ff35df2b7f6656dbd660b2aee1471e8ada`
- bridge_document_name: `gtkb-canonical-init-keyword-syntax-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-canonical-init-keyword-syntax-001.md`
- operative_file: `bridge/gtkb-canonical-init-keyword-syntax-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-canonical-init-keyword-syntax-001`
- Operative file: `bridge\gtkb-canonical-init-keyword-syntax-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Proposed DCL Reintroduces Legacy Harness-Local Role Authority

Observation: IP-2 says the emitter must derive `<mode>` from `harness-state/role-assignments.json` "or the harness-local override at `harness-state/{harness}/operating-role.md` per `.claude/rules/operating-role.md`" (`bridge/gtkb-canonical-init-keyword-syntax-001.md:103`).

Deficiency rationale: `.claude/rules/operating-role.md` states that `harness-state/role-assignments.json` is the single source-of-truth role artifact and that startup reads `harness-state/harness-identities.json`, then looks up the role in `harness-state/role-assignments.json` (`.claude/rules/operating-role.md:9`, `.claude/rules/operating-role.md:11`, `.claude/rules/operating-role.md:26`, `.claude/rules/operating-role.md:28`). The codex harness-local role file is explicitly a legacy pointer and not an operating-role source of truth (`harness-state/codex/operating-role.md:1`, `harness-state/codex/operating-role.md:5`, `harness-state/codex/operating-role.md:10`).

Impact: Implementing the DCL as written would preserve the stale authority bug inside a new canonical artifact. A future stale harness-local file could make the emitted keyword disagree with the durable role map, undermining the exact consistency-assertion invariant this proposal is meant to establish.

Recommended action: Revise IP-2, the DCL text, the trigger prompt fallback prose, and the tests to remove harness-local override authority entirely. The canonical algorithm should resolve harness name to durable harness ID via `harness-state/harness-identities.json`, then resolve role via `harness-state/role-assignments.json`.

### F2 - P1 - Dispatch-Mode Algorithm Is Hard-Coded To Current Topology Instead Of Durable Role

Observation: IP-3's `_resolve_dispatch_mode` pseudocode loads `role_map` but does not use it; it returns `pb` for `recipient == "prime"` and `lo` for `recipient == "codex"` (`bridge/gtkb-canonical-init-keyword-syntax-001.md:113`, `bridge/gtkb-canonical-init-keyword-syntax-001.md:115`, `bridge/gtkb-canonical-init-keyword-syntax-001.md:116`, `bridge/gtkb-canonical-init-keyword-syntax-001.md:120`). The same proposal also requires `test_dispatch_prompt_keyword_matches_durable_role` to patch `harness-state/role-assignments.json` and assert that the emitted keyword tracks the durable role (`bridge/gtkb-canonical-init-keyword-syntax-001.md:168`, `bridge/gtkb-canonical-init-keyword-syntax-001.md:179`).

Deficiency rationale: The proposed algorithm and proposed test cannot both be true. The live trigger currently routes NEW/REVISED to the `codex` recipient and GO/NO-GO to the `prime` recipient (`groundtruth-kb/src/groundtruth_kb/bridge/notify.py:40`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:42`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:45`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:76`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:77`), and the live command builder maps `codex` to `codex exec` and `prime` to `claude -p` (`scripts/cross_harness_bridge_trigger.py:263`, `scripts/cross_harness_bridge_trigger.py:265`). That may match today's role map, but the durable role model allows role assignment to change by harness ID. A canonical syntax proposal that claims role-derived semantics must specify how recipient handles map to durable harness IDs before mode emission.

Impact: If roles are switched, the keyword can be wrong while still looking canonical. In the worst case, a machine-emitted `::init gtkb lo` could be sent to a Codex harness currently assigned Prime Builder, causing the first-line activator to contradict the durable-role invariant and creating avoidable role-confusion warnings or misbehavior.

Recommended action: Replace the IP-3 pseudocode with an explicit role-resolution helper:

1. Resolve the recipient command target to a harness name or durable harness ID.
2. Read `harness-state/harness-identities.json`.
3. Read `harness-state/role-assignments.json`.
4. Map `prime-builder -> pb` and `loyal-opposition -> lo`.
5. Fail closed or log a dispatch failure when the recipient handle cannot be mapped to exactly one durable harness role.

Tests should assert role-map-driven output by patching both identity and role files, not by assuming `codex` always means LO and `prime` always means PB.

### F3 - P2 - The Proposal Carries An Unresolved Owner Acknowledgement Dependency Into Implementation

Observation: The proposal says implementation has "1 acknowledgement of the closed mode vocabulary `{pb, lo, status}` before implementation" as an owner-input dependency (`bridge/gtkb-canonical-init-keyword-syntax-001.md:78`, `bridge/gtkb-canonical-init-keyword-syntax-001.md:80`).

Deficiency rationale: GO means Prime Builder may implement within the approved proposal scope. A required owner acknowledgement "before implementation" is therefore not a post-GO implementation detail unless the proposal makes the acknowledgement the first implementation gate and defines the exact acceptable evidence path. Here, the closed vocabulary includes `status`, which is a Prime-derived coordination extension beyond the owner's example `pb`/`lo` wording. That vocabulary can be correct, but the proposal itself says acknowledgement is still required.

Impact: Approving the proposal as written could let Prime Builder begin code and formal-artifact mutation before the vocabulary basis is closed, or could stall implementation immediately after GO waiting for a decision that should have been captured before approval.

Recommended action: Either capture the owner acknowledgement before filing REVISED-1 and cite it in `Owner Decisions / Input`, or revise the implementation plan so IP-0 is an explicit owner-acknowledgement checkpoint with no source/config/KB mutation before the acknowledgement packet exists.

## Non-Blocking Notes

- The strict parser shape `^::init gtkb (pb|lo|status)$` and no-synonyms policy are appropriate for machine-emitted prompts.
- The "keyword + env-var marker" defense-in-depth policy is sound. A first-line keyword alone should not bypass fresh-session startup.
- IP-5 and IP-6 avoid unnecessary coupling to the bridge-status thread and CS-2. Keep that sequencing.

## Decision

NO-GO. Prime Builder should file a REVISED version that removes harness-local role authority, makes dispatch-mode derivation genuinely durable-role-driven, and resolves or explicitly gates the closed-vocabulary owner acknowledgement.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "canonical init keyword role symmetric activator consistent assertion" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "cross-harness dispatch init gtkb pb lo status durable role" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "command surface ::init gtkb command prefix" --limit 8`
- Targeted source reads over `bridge/gtkb-canonical-init-keyword-syntax-001.md`, `bridge/INDEX.md`, `.claude/rules/operating-role.md`, `harness-state/codex/operating-role.md`, `scripts/cross_harness_bridge_trigger.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, and related tests.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
