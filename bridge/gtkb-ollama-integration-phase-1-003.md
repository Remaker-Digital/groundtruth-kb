REVISED

# Phase-1 Ollama Harness Integration - Governance Umbrella Revision

bridge_kind: governance_review
Document: gtkb-ollama-integration-phase-1
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-ollama-integration-phase-1-002.md (NO-GO)
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-pb-2026-06-04T16-28Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Prime Builder bridge revision

target_paths: []
requires_verification: false
implementation_scope: governance_only
work_item_ids: [WI-4316, WI-4317, WI-4318, WI-4319, WI-4320, WI-4321, WI-4322, WI-4323, WI-4324, WI-4325]

## Revision Claim

This revision preserves the owner-approved Ollama Phase 1 architecture from
bridge/gtkb-ollama-integration-phase-1-001.md and corrects the NO-GO at -002 by
making the local tool-dispatch guard adapter a blocking Phase 1 design
contract.

Umbrella GO, if granted, authorizes only the governance design direction and
child-bridge filing sequence. It does not authorize any source mutation,
formal spec insertion, protected narrative edit, MemBase mutation, harness role
promotion, dispatch-substrate wiring, or skill-adapter generation without a
matching child bridge, project authorization envelope, and applicable approval
packets.

## Findings Addressed

### P1 - Full-parity local tool dispatch is now bound to existing guardrails

The original umbrella said the shim would respect bridge compliance,
scanner-safe-writer, destructive-gate, and author metadata, but it did not
define the local adapter contract that makes a standalone Python process
inherit those controls. This revision makes that contract explicit:

1. No model-requested mutating tool call may write files or run shell commands
   directly.
2. `Write`, `Edit`, and `Bash` dispatch must pass through an Ollama local
   guard adapter before mutation.
3. The adapter must synthesize the same guard-relevant payload shape used by
   Claude Code and Codex hook events and invoke the relevant existing GT-KB
   guard scripts.
4. Guard outcomes fail closed on deny, ask/checkpoint, malformed output,
   missing guard script, nonzero guard adapter error, out-of-root path, or
   unrecognized tool shape.
5. Author/model metadata must be set before every bridge-file or governed
   document mutation path, not only before a nominal `Write` helper.

The corrected contract is folded into the revised
`DCL-OLLAMA-TOOL-PARITY-GATE-001` draft below and into the child bridge
verification requirements.

### P2 - Child-level executable proof is now mandatory

The original umbrella treated Codex GO as the main test of the governance
contract. This revision requires the child implementation bridges to include
executable guard-adapter tests. The shim and verification children must prove
that local Ollama tool execution invokes the same controls that protect Claude
Code and Codex sessions.

## Specification Links

| Spec | Severity | How this revision complies |
|------|----------|----------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | Uses the append-only bridge thread, Version 003, and live INDEX authority. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | Carries explicit specification links and response mapping. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | Pushes executable proof into child bridge verification plans and names required tests. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | States that spec inserts and protected narrative edits remain packet-gated and are not authorized by umbrella GO alone. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | Keeps harness D registered with empty role-set; no active role or dispatch target in Phase 1. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | Cites the active Ollama Phase 1 PAUTH and preserves its forbidden-operation boundaries. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | Keeps child bridges tied to approved framing specs plus the revised inline Ollama spec drafts. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | blocking | Uses DELIB-20260663 as the owner-decision anchor for adopt/adapt handling. |
| `DCL-CONCEPT-ON-CONTACT-001` | blocking | Keeps glossary additions in the governance-implementation child, packet-gated. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | Keeps all Phase 1 implementation file touchpoints inside `E:\GT-KB` platform paths and outside adopter application roots. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | Preserves each decision, specification, bridge revision, and future child implementation as a durable artifact with explicit lifecycle state. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | advisory | Requires local adapter parity rather than assuming Claude/Codex hooks apply automatically. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | Preserves the project -> PAUTH -> umbrella -> child bridge artifact chain. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | Treats new harness, config, spec, source, and protected-doc work as child artifacts with explicit lifecycle states. |

## Prior Deliberations

- `DELIB-20260663` - owner decision record for the 12 AUQ Ollama Phase 1
  scope answers; source_type owner_conversation, outcome owner_decision.
- `.groundtruth/formal-artifact-approvals/2026-06-04-DELIB-20260663.json` -
  owner-approved deliberation packet backing the AUQ evidence.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-15-ollama-harness-routing-decision-memo.md`
  - source advisory recommending Option A.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-04-08-20-ollama-parity-gap-analysis.md`
  - source advisory calling out local tool parity and security concerns.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - supports keeping harness D
  registered and not wired into dispatch in Phase 1.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - supports role-set `[]`
  plus status `registered`.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - supports local
  invocation of external harness executables and servers while preserving the
  GT-KB project-root boundary.
- `bridge/gtkb-ollama-integration-phase-1-002.md` - operative NO-GO being
  corrected by this revision.

## Owner Decisions / Input

No new owner input is requested by this revision.

The owner decisions in `DELIB-20260663` remain sufficient:

- AUQ#1 selected Option A, a framework-free Python shim.
- AUQ#2 selected static `.ollama/routing.toml`.
- AUQ#3 selected harness D as registered with no active role.
- AUQ#4 selected the Phase 1 MVP boundary.
- AUQ#5 selected Qwen 2.5 Coder 14B Q4_K_M as the single MVP model.
- AUQ#6 selected full parity tools.
- AUQ#7 selected heavy governance.
- AUQ#8 selected one project PAUTH covering Phase 1 WIs.
- AUQ#9 selected round-trip plus bridge filing plus ruff/pytest E2E scope.
- AUQ#10 selected doctor reachability, model, and registry checks.
- AUQ#11 selected procedural plus machine-checkable GOV reach.
- AUQ#12 selected a flat project shape.

This revision interprets AUQ#6 full parity as full parity with GT-KB guardrails,
not raw local filesystem or subprocess authority.

## Revised Phase 1 Boundary

Phase 1 includes:

- harness D identity and registry as registered with role-set `[]`;
- `scripts/check_harness_parity.py` generalized for ollama;
- `[capabilities.ollama]` in `config/agent-control/harness-capability-registry.toml`;
- `scripts/ollama_harness.py` plus local fail-closed tool guard adapter;
- `.ollama/routing.toml` with one Qwen 2.5 Coder 14B mapping;
- author/model metadata injection before governed writes;
- `scripts/verify_ollama_dispatch.py`;
- doctor `_check_ollama_harness`;
- five formal specs and two protected narrative edits through approval packets.

Phase 1 excludes:

- promoting harness D to an active Prime Builder or Loyal Opposition role;
- wiring cross-harness or single-harness dispatch to Ollama;
- `.ollama/skills/` adapter generation;
- additional model registration beyond Qwen 2.5 Coder 14B;
- any raw bypass around the existing GT-KB guard scripts.

## Revised Spec Draft Delta

The Phase 1 spec count remains one ADR, three DCLs, and one GOV per AUQ#7.
This revision changes the substance of the tool-parity DCL and GOV capability
floor rather than adding a fourth DCL.

### ADR-OLLAMA-HARNESS-ADOPTION-001 Delta

Add this consequence:

> Ollama is a standalone local process and does not inherit Claude Code or
> Codex PreToolUse hooks. Therefore the Python shim must include a fail-closed
> local guard adapter that invokes the existing GT-KB guard scripts before any
> mutating model-requested tool call.

Add this assertion:

> `scripts/ollama_harness.py` routes `Write`, `Edit`, and `Bash` through a
> fail-closed guard adapter before mutation.

### DCL-OLLAMA-TOOL-PARITY-GATE-001 Revised Draft

**Type:** `design_constraint`. **Status:** `specified`. **Affected by:**
`ADR-OLLAMA-HARNESS-ADOPTION-001`.

**Title:** Ollama full-parity tools must dispatch through a fail-closed GT-KB
guard adapter.

**Constraint:** `scripts/ollama_harness.py` MAY expose the canonical full
tool set `("Read", "Write", "Edit", "Grep", "Glob", "Bash")` only when every
mutating tool path dispatches through a local guard adapter before mutation.
The shim MUST NOT implement raw filesystem writes, raw edits, or raw shell
execution as the first action for model-requested `Write`, `Edit`, or `Bash`.

**Guard coverage:**

- `Write` must run project-root containment, credential scan,
  scanner-safe-writer where applicable, bridge-compliance-gate,
  narrative-artifact-approval-gate, and implementation-start-gate before the
  file is persisted.
- `Edit` must run project-root containment, credential scan,
  bridge-compliance-gate, narrative-artifact-approval-gate, and
  implementation-start-gate before the file is changed.
- `Bash` must run project-root containment, destructive-gate,
  formal-artifact-approval-gate, and implementation-start-gate before command
  execution.

**Fail-closed rule:** Any guard deny, ask/checkpoint, parse failure, missing
guard file, nonzero adapter error, out-of-root path, unrecognized tool schema,
or ambiguous path resolution MUST stop the model tool call. The adapter must
return a structured error to the model and must not partially apply the
mutation.

**Root-boundary rule:** The adapter must reject out-of-root paths before
invoking the guard scripts. It must not normalize an out-of-root path back into
scope.

**Author metadata rule:** For bridge-file and governed-document writes, the
adapter must set `GTKB_AUTHOR_MODEL`, `GTKB_AUTHOR_MODEL_VERSION`, and the
Ollama harness identity metadata before invoking guard scripts and before
mutation.

**Assertions:**

- `scripts/ollama_harness.py` defines canonical tool names and rejects
  non-canonical names from `.ollama/routing.toml`.
- `scripts/ollama_harness.py` defines a fail-closed guard adapter path for
  `Write`, `Edit`, and `Bash`.
- Tests prove a denied guard prevents mutation.
- Tests prove a missing guard prevents mutation.
- Tests prove out-of-root paths are rejected before mutation.
- Tests prove author/model metadata is present on bridge-file writes.

### GOV-HARNESS-ONBOARDING-CONTRACT-001 Delta

Add one required capability-floor field:

```toml
tool_guard_adapter_fail_closed = true
```

Add this Layer 3 requirement:

> A harness that executes local mutating tools outside Claude Code or Codex
> hook runtimes must provide a fail-closed guard adapter that invokes the
> canonical GT-KB guard scripts before mutation. Declaring
> `bridge_compliance_gate_respect = true` is not sufficient unless that adapter
> is implemented and tested.

## Revised Child Bridge Mapping

### Child 1 - foundation

Primary WI: WI-4316. Bundled WIs: WI-4317, WI-4318.

Child file touchpoints remain:

- `harness-state/harness-identities.json`
- `harness-state/harness-registry.json`
- `scripts/check_harness_parity.py`
- `config/agent-control/harness-capability-registry.toml`

Additional verification required:

- `capabilities.ollama.tool_guard_adapter_fail_closed = true` exists.
- `capabilities.ollama.advertised_tool_subset` is a subset of the canonical
  six tools.
- harness D has status `registered` and role-set `[]`.

### Child 2 - shim and routing

Primary WI: WI-4319. Bundled WIs: WI-4320, WI-4321.

Child file touchpoints expand to:

- `scripts/ollama_harness.py`
- `scripts/ollama_tool_guard_adapter.py` if the adapter is split from the
  harness script
- `.ollama/routing.toml`
- `tests/scripts/test_ollama_harness.py`
- `tests/scripts/test_ollama_tool_guard_adapter.py`

Required verification:

- `Write` to a bridge file invokes credential scan, scanner-safe-writer, and
  bridge-compliance-gate before mutation.
- `Edit` to a bridge file invokes credential scan and bridge-compliance-gate
  before mutation.
- narrative-rule `Write` and `Edit` are blocked without a matching approval
  packet.
- source/config/test writes outside the active implementation-start target
  paths are blocked.
- out-of-root paths are rejected before guard invocation.
- missing guard script fails closed.
- successful bridge-file writes include harness D and routed-model author
  metadata.

### Child 3 - verification and doctor

Primary WI: WI-4322. Bundled WI: WI-4323.

Child file touchpoints remain:

- `scripts/verify_ollama_dispatch.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `tests/groundtruth_kb/test_doctor_ollama.py`

Additional verification required:

- E2E fixture proves a destructive Bash command is denied by the destructive
  gate path.
- E2E fixture proves formal-artifact and MemBase mutation commands are blocked
  without matching approval packets.
- Doctor reports WARN, not FAIL, when local Ollama is unreachable; registry and
  config consistency failures remain FAIL.

### Child 4 - governance implementation

Primary WI: WI-4324. Bundled WI: WI-4325.

Child file touchpoints remain packet-gated:

- five formal-artifact approval packets;
- two narrative-artifact approval packets;
- `.claude/rules/canonical-terminology.md`;
- `.claude/rules/operating-model.md`;
- `groundtruth.db` formal spec inserts.

Additional verification required:

- Formal spec text includes the revised tool-guard adapter clause.
- Narrative edits describe Ollama as registered/no-active-role until a later
  approved role-promotion bridge.
- No formal spec insert or protected narrative edit occurs without matching
  approval packets.

## Pre-Filing Preflight Subsection

The bridge revision helper will run candidate-content preflights before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1 --content-file <candidate>
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1 --content-file <candidate>
```

Expected result: applicability preflight passes with no missing required specs,
and ADR/DCL clause preflight exits 0 with no blocking gaps.

The same helper will write `bridge/gtkb-ollama-integration-phase-1-003.md`
and insert the `REVISED: bridge/gtkb-ollama-integration-phase-1-003.md` line
at the top of the existing `Document: gtkb-ollama-integration-phase-1` entry
in `bridge/INDEX.md`; prior bridge versions remain append-only and unchanged.

## Specification-Derived Verification Plan

Umbrella verification remains review-only because this is a
`governance_review` with `target_paths: []`. The child bridges must carry
executable verification for the revised safety contract:

| Contract | Child verification |
|----------|--------------------|
| Full-parity tools are not raw local mutation authority | Shim child tests prove every mutating tool enters the guard adapter before mutation. |
| Guard failures fail closed | Shim child tests cover deny, ask/checkpoint, malformed output, nonzero guard error, and missing guard. |
| Root-boundary is enforced before mutation | Shim child tests reject `..`, absolute out-of-root paths, and symlink-style escape fixtures before guard execution. |
| Existing GT-KB guard scripts remain authoritative | Shim and verification children call the existing guard scripts; no duplicate allowlist replaces destructive-gate, bridge-compliance-gate, credential scan, scanner-safe-writer, narrative approval, formal approval, or implementation-start gate. |
| Author/model metadata is injected before governed writes | Shim child tests inspect generated bridge-file content and environment passed to guard scripts. |
| Formal/protected artifact writes remain packet-gated | Governance child demonstrates matching formal/narrative approval packets before any insert or protected edit. |

## Risk And Rollback

Risk is reduced relative to -001 because the mutating local tool surface now
has an explicit fail-closed guard contract before implementation begins.

Residual risks:

- Guard payload shapes may diverge from Claude/Codex hook payloads. Mitigation:
  child tests must use fixture payloads modeled on live hook expectations.
- Local models may repeatedly request blocked mutations. Mitigation: the
  adapter returns structured denial results and stops partial mutation.
- Ollama Phase 1 may become too large if all guard-adapter tests land in one
  child. Mitigation: child bridges remain ordered and separable; a child NO-GO
  does not invalidate the umbrella.

Rollback:

- If this umbrella revision is NO-GO'd, no source or state mutation is needed;
  file a later REVISED version.
- If umbrella GO is granted but a child fails, revert that child only.
- If Phase 1 is abandoned, withdraw child threads, revoke the PAUTH, and leave
  harness D unregistered unless an owner-approved cleanup bridge says
  otherwise.

## Recommended Outcome

GO for the revised governance umbrella, with the condition that all child
implementation bridges carry the guard-adapter contract and tests above before
they can receive their own GO.
