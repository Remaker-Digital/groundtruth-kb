NEW
::init gtkb lo
::open build

# WI-5497: Harden LO live-carrier mutation enforcement across harness payloads

bridge_kind: prime_proposal
Document: gtkb-wi5497-lo-file-safety-live-carrier-hardening
Version: 001
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5497-LO-FILE-SAFETY-SEVEN-FILE-BUILD-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5497

target_paths: [".claude/hooks/lo-file-safety-gate.py", ".codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py", "scripts/cursor_hook_adapter.py", "scripts/lo_file_safety_payloads.py", "scripts/antigravity_hook_adapter.py", "platform_tests/scripts/test_lo_file_safety_payloads.py", "platform_tests/scripts/test_antigravity_hook_adapter.py"]

implementation_scope: source | test | one internal hook implementation
requires_review: true
requires_verification: true
hook_registration_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Claim

The canonical Loyal Opposition file-safety gate does not consistently see
equivalent mutation intent across Claude, Codex, Cursor, and Antigravity
PreToolUse payload shapes. WI-5497 proposes one shared payload-normalization
and live-carrier mutation-classification layer, thin harness adapters, and
focused tests that deny whole-file replacement of `groundtruth.db` while
preserving allowed additive verdict publication and all existing role and
approval-packet behavior.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`, `TEST-11581`, the existing LO file-safety
gate, and the cross-harness parity authorities already define the required
outcome. The defect is incomplete and inconsistent implementation coverage,
not an unresolved policy choice. No new role, queue, hook registration,
dispatcher rule, or artifact authority is required.

## Defect / Reproduction

Canonical MemBase work item `WI-5497` records the read-only preproposal
reproduction:

1. The current canonical hook blocks `git restore` and path-oriented
   `git checkout` attempts against `groundtruth.db`.
2. The same hook permits `git reset` forms that can replace the tracked live
   carrier.
3. It permits Python whole-file copy forms such as `shutil`-based replacement
   of the live carrier.
4. Unsupported Antigravity `write_to_file` and
   `replace_file_content` payloads fall through because `_changed_paths`
   recognizes only Claude-style `Write`, `Edit`, `MultiEdit`, `Bash`, and
   apply-patch forms.

Current source establishes the mechanism:

- `.claude/hooks/lo-file-safety-gate.py` omits `git reset` from
  `WRITEISH_COMMAND_RE` and `_bash_targets`.
- `_changed_paths` returns an empty change set for unrecognized mutation tool
  names, which makes those payloads pass.
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` forwards its payload
  without a normalized mutation contract.
- `scripts/cursor_hook_adapter.py` has a local Claude-shaping function, but no
  shared mutation schema with the canonical gate.
- No in-root Antigravity adapter exists for the native
  `run_command`/write-tool payload family.

`TEST-11581` is the governed acceptance carrier. It requires Claude
Bash/PowerShell, Codex Bash/apply-patch, Cursor Shell/Write, and Antigravity
run-command/write fixtures to deny whole-carrier restoration or replacement,
preserve a concurrent sentinel row, preserve allowed new LO verdict writes,
and fail closed on opaque mutation syntax.

## In-Root Placement Evidence

Every implementation target is inside `E:/GT-KB`:

- `.claude/hooks/lo-file-safety-gate.py`
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`
- `scripts/cursor_hook_adapter.py`
- `scripts/lo_file_safety_payloads.py`
- `scripts/antigravity_hook_adapter.py`
- `platform_tests/scripts/test_lo_file_safety_payloads.py`
- `platform_tests/scripts/test_antigravity_hook_adapter.py`

No live dependency, evidence source, or test fixture is outside the project
root.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - prohibits whole-carrier replacement that
  erases concurrent governed rows and requires preservation of unrelated work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves the numbered bridge chain and
  role-authorized additive verdict path while denying destructive carrier
  mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the WI-specific PAUTH does
  not replace independent GO, claim, implementation-start, report, or
  verification gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - operation-time authority must
  match the exact seven-file proposal.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` - the active PAUTH
  includes only `WI-5497`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal names
  the project, PAUTH, WI, and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all governing
  requirements are explicitly linked.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent VERIFIED
  requires executed tests derived from the linked authorities and
  `TEST-11581`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Codex adapter must preserve the
  canonical gate's deny behavior and response contract.
- `ADR-CROSS-HARNESS-PARITY-001` - equivalent mutation intent must receive
  equivalent decisions on supported local harness carriers.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the proposal carries an
  explicit per-harness implementation and non-applicability disposition.
- `GOV-ARTIFACT-APPROVAL-001` - valid content-exact owner approval packets
  remain the exceptional LO mutation route.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - target, content, hash, and packet
  validation must not be weakened.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - hook, adapter, and test changes
  remain in-root as GT-KB platform infrastructure.
- `GOV-STANDING-BACKLOG-001` - `WI-5497` and `TEST-11581` are the canonical
  work and verification carriers; no duplicate item is created.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260718-WI5497-SEVEN-FILE-BUILD-SCOPE` - owner approved the exact
  seven-file build scope, superseding the earlier five-file boundary.
- `DELIB-2396` - Loyal Opposition review of the original LO file-safety
  PreToolUse enforcement.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` - owner selected
  phased black-box enforcement rather than silent unsupported surfaces.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - dispatcher
  configuration remains outside this work.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - this proposal cites
  only MemBase, Deliberation Archive, numbered bridge, source, and test
  authorities.

## Owner Decisions / Input

`DELIB-20260718-WI5497-SEVEN-FILE-BUILD-SCOPE` is the controlling owner
decision. It authorizes the expanded seven-file build boundary and makes the
existing Codex and Cursor adapters explicit implementation targets.

The active singleton authorization is
`PAUTH-DISPATCHER-BLACK-BOX-WI5497-LO-FILE-SAFETY-SEVEN-FILE-BUILD-20260718`.
It permits bridge, metadata, governance evidence, source, test, and the
configuration mutation class needed solely for the approved internal hook
file. It forbids hook registration, harness settings, dispatcher mutation,
TAFE mutation, runtime-state mutation, credentials, external systems,
deployment, destructive cleanup, Git history rewrite, push, and unrelated
paths.

The owner's dispatcher-configuration hold remains binding. This proposal does
not request or authorize dispatcher or TAFE configuration or runtime changes.

## Dependency And Ownership Disposition

- `WI-5487` is terminal retired as the decomposed umbrella. `WI-5497` is its
  build child and `WI-5498` is the later ops child.
- `WI-5477` is terminal retired as superseded by `WI-5498`; its Claude
  PowerShell matcher-registration requirement is not implemented here.
- `WI-5498` remains sequenced after verified WI-5497 behavior and owns Claude
  and Antigravity hook registration and harness configuration only.
- `WI-5275` remains a broader phased-hardening backlog item. WI-5497 owns this
  reproduced live-carrier defect and the exact seven files approved by the
  owner. Future WI-5275 work must preserve the verified WI-5497 behavior and
  may not re-own these defect hunks.

All seven declared paths are clean at proposal time. No foreign source or test
hunk is adopted by this proposal.

## Proposed Scope

1. Add `scripts/lo_file_safety_payloads.py` as the shared, side-effect-free
   normalization and mutation-intent layer. It must convert supported carrier
   payloads into one typed internal representation containing harness,
   operation, command or edit form, target paths, reconstructed content when
   available, and an explicit opaque-mutation state.
2. Refactor `.claude/hooks/lo-file-safety-gate.py` to consume that normalized
   representation while preserving its existing role-resolution,
   allow-list, bridge-addition, approval-packet, path-normalization, and
   response behavior.
3. Extend shell classification to cover:
   - `git reset` path forms and worktree-replacing modes that can affect
     `groundtruth.db`;
   - Python interpreter commands containing recognized whole-file
     copy/move/replace/delete APIs directed at `groundtruth.db`;
   - existing Bash and PowerShell copy, move, replace, delete, redirection,
     `git restore`, and `git checkout` forms;
   - opaque write-capable syntax involving the live carrier, which must deny
     rather than produce an empty change set.
4. Update the Codex adapter to normalize Codex Bash and apply-patch payload
   shapes without changing the canonical hook decision or exit-code contract.
5. Update the Cursor adapter to use the shared normalizer for Shell and Write
   payloads while preserving Cursor's existing deny-response translation and
   metadata defaults.
6. Add `scripts/antigravity_hook_adapter.py` for native
   `run_command`, `write_to_file`, `replace_file_content`, and
   `multi_replace_file_content` payloads. The adapter must translate the
   canonical gate response without registering itself in harness
   configuration.
7. Add focused unit and subprocess tests in the two approved test modules.
   Tests must prove equivalent decisions across harness payload variants,
   fail-closed malformed/opaque mutation handling, unchanged approval-packet
   behavior, allowed additive verdict creation, and disposable concurrent
   sentinel-row survival.

Out of scope:

- Hook registration, `.claude/settings.json`, `.codex/hooks.json`, Cursor
  settings, Antigravity settings, or any other harness configuration.
- Dispatcher or TAFE configuration, routing, eligibility, caps, leases,
  daemon state, runtime files, worker control, or provider contact.
- Modification of `groundtruth.db`, MemBase rows, or Deliberation Archive rows
  during implementation or tests. Sentinel tests use disposable temporary
  carriers only.
- Changing LO role authority, interactive role resolution, allow-list policy,
  approval-packet policy, bridge status authority, or artifact lifecycles.
- New parser dependencies, generated artifacts, caches, queues, alternate
  indexes, staging, push, deployment, release, or unrelated cleanup.

## Cross-Harness Disposition

- Harness A (Codex): applicable. The approved Codex Bash adapter must preserve
  the canonical gate's decision and exit contract for Bash and apply-patch
  payloads.
- Harness B (Claude Code): applicable. The canonical hook must recognize
  Claude Bash, PowerShell, Write, Edit, and MultiEdit payload forms. This work
  changes hook implementation only, not Claude hook registration.
- Harness C (Antigravity): applicable. Add the approved source adapter for
  native run-command and write payloads. Registration remains exclusively
  owned by later ops child `WI-5498`.
- Harness E (Cursor): applicable. Update the approved Cursor adapter for
  Shell and Write payload normalization while preserving its response
  translation.
- Harness D (Ollama), harness F (OpenRouter), and harness H (Alibaba): not
  implementation targets. Provider workers do not own the local interactive
  PreToolUse carrier files in this seven-file scope; their existing governed
  dispatch and finalization routes remain unchanged.

No typed parity waiver is requested. A, B, C, and E must receive equivalent
deny outcomes for equivalent live-carrier mutation intent, with
harness-native payload and response translation.

## Specification-Derived Verification Plan

| Governing requirement | Executable verification | Required result |
|---|---|---|
| `TEST-11581`, `GOV-WORK-TREE-HYGIENE-001` | Exercise disposable carriers containing an initial row and a concurrently added sentinel row, then route whole-carrier restore/copy/reset payloads through each applicable adapter/gate path. | Every mutation is denied before execution and both rows remain present. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Exercise a new versioned bridge verdict payload and existing-artifact overwrite/delete payloads under LO role. | Allowed additive verdict behavior remains allowed; overwrite/delete remains denied. |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Run valid, target-mismatch, content-mismatch, hash-mismatch, malformed, and absent packet fixtures. | Existing valid packet behavior is preserved and every invalid packet fails closed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Parameterize equivalent Claude, Codex, Cursor, and Antigravity carrier payloads over reset, restore, checkout, copy, move, replace, delete, and opaque mutation cases. | A/B/C/E produce equivalent allow/deny outcomes and harness-native response shapes. |
| Existing role-resolution authorities | Run the unchanged `test_lo_file_safety_gate_role_resolution.py` module. | Interactive marker and durable fallback behavior remain green with no test or source changes outside the approved scope. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-WORK-TREE-HYGIENE-001` | Inspect exact-target status/diff, run `git diff --check`, and verify tests use only temporary carriers. | Only approved WI-5497 paths change and no canonical carrier is mutated. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest, Ruff, py_compile, both bridge preflights, and an independent LO rerun against the exact implementation bytes. | Every mapped check passes before VERIFIED and focused finalization. |

Required implementation and verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_file_safety_payloads.py platform_tests/scripts/test_antigravity_hook_adapter.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py scripts/lo_file_safety_payloads.py scripts/antigravity_hook_adapter.py platform_tests/scripts/test_lo_file_safety_payloads.py platform_tests/scripts/test_antigravity_hook_adapter.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py scripts/lo_file_safety_payloads.py scripts/antigravity_hook_adapter.py platform_tests/scripts/test_lo_file_safety_payloads.py platform_tests/scripts/test_antigravity_hook_adapter.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py scripts/lo_file_safety_payloads.py scripts/antigravity_hook_adapter.py
git diff --check -- .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py scripts/lo_file_safety_payloads.py scripts/antigravity_hook_adapter.py platform_tests/scripts/test_lo_file_safety_payloads.py platform_tests/scripts/test_antigravity_hook_adapter.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5497-lo-file-safety-live-carrier-hardening
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5497-lo-file-safety-live-carrier-hardening
```

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5497; TEST-11581; DELIB-20260718-WI5497-SEVEN-FILE-BUILD-SCOPE; PAUTH-DISPATCHER-BLACK-BOX-WI5497-LO-FILE-SAFETY-SEVEN-FILE-BUILD-20260718",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001; GOV-FILE-BRIDGE-AUTHORITY-001; canonical LO file-safety hook plus governed harness adapters",
  "primary_route": "harness-native PreToolUse payload -> shared side-effect-free normalization -> canonical LO file-safety decision -> harness-native response",
  "before_behavior": "equivalent live-carrier mutation intent is blocked for selected Claude-style restore and checkout forms but can pass through git reset, Python whole-file copy, and unsupported Antigravity write payloads",
  "after_behavior": "equivalent live-carrier restore, reset, copy, move, replace, delete, and opaque write intent is denied consistently across A/B/C/E while allowed additive bridge verdict and valid approval-packet behavior remains unchanged",
  "self_descriptive_naming": "the shared lo_file_safety_payloads module and normalized mutation representation name the policy boundary directly",
  "obsolete_guidance_disposition": "duplicated adapter-local payload interpretation is replaced in the approved adapters; no alternate policy engine or competing bridge authority is created",
  "history_preservation": "MemBase WI-5497, TEST-11581, the owner deliberation, PAUTH, numbered bridge chain, implementation report, and independent verdict preserve the lifecycle",
  "baseline": {
    "blocked_forms": "git restore and path-oriented git checkout recognized by the canonical hook",
    "false_negative_forms": "git reset, Python whole-file copy, and Antigravity write_to_file/replace_file_content payloads recorded in WI-5497",
    "role_and_packet_behavior": "existing role resolution, allow-list, additive verdict, and content-exact approval-packet behavior",
    "target_state": "all seven declared paths clean before proposal; four targets do not yet exist"
  },
  "expected_result": {
    "live_carrier_mutation": "denied before execution for equivalent A/B/C/E payloads",
    "sentinel_survival": "initial and concurrent rows remain present in every disposable-carrier integration fixture",
    "allowed_behavior": "new LO verdict publication and valid approval packets preserve current outcomes",
    "configuration_mutation": "zero hook registration, harness settings, dispatcher, TAFE, routing, lease, daemon, or runtime mutation"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused WI-5497 source and test hunks",
    "verification": "rerun focused payload, adapter, role-resolution, Ruff, py_compile, exact-target diff, and both bridge preflight checks"
  },
  "hard_invariants": [
    "the canonical hook remains the decision authority",
    "role resolution, allow-list, bridge-addition, and approval-packet semantics do not weaken",
    "equivalent mutation intent receives equivalent decisions on A/B/C/E",
    "tests never mutate canonical groundtruth.db",
    "WI-5498 retains exclusive ownership of hook registration and harness configuration",
    "no dispatcher or TAFE configuration/runtime state, provider worker, credential, external system, deployment, release, push, or unrelated worktree state is mutated"
  ],
  "fail_closed_conditions": [
    "a recognized mutation-capable payload cannot be normalized",
    "opaque syntax combines a write-capable operation with the live carrier",
    "any A/B/C/E equivalent-payload decision differs",
    "a sentinel row disappears from a disposable-carrier fixture",
    "allowed additive verdict or valid approval-packet behavior regresses",
    "any independent GO, exact claim, implementation-start, test, VERIFIED, or focused-finalization gate is absent"
  ],
  "essential_context_preservation": "harness identity, original tool name, mutation operation, target path, reconstructed content when available, opacity reason, canonical decision reason, role authority, and approval-packet evidence remain available to tests and diagnostics"
}
```

## Acceptance Criteria

1. The shared normalizer deterministically handles Claude Bash/PowerShell and
   write tools, Codex Bash/apply-patch, Cursor Shell/Write, and Antigravity
   run-command/write payloads.
2. `git restore`, `git checkout`, `git reset`, shell copy/move/delete/replace,
   Python whole-file copy/move/replace/delete, and opaque write-capable forms
   affecting `groundtruth.db` are denied under LO role.
3. Malformed mutation-capable payloads fail closed with a diagnostic instead
   of returning an empty change set.
4. Disposable-carrier tests prove initial and concurrent sentinel rows survive
   every denied whole-carrier operation.
5. New versioned LO verdict creation remains allowed and existing bridge
   overwrite/delete remains denied.
6. Valid content-exact approval packets remain allowed; invalid or mismatched
   packets remain denied.
7. A/B/C/E equivalent payloads produce equivalent decisions with the expected
   harness-native response contract.
8. Existing role-resolution tests remain unchanged and green.
9. No hook registration, harness settings, dispatcher/TAFE state, canonical
   MemBase carrier, or path outside the seven-file scope changes.
10. Focused pytest, Ruff check, Ruff format, py_compile, exact-target diff
    check, applicability preflight, clause preflight, independent VERIFIED,
    and focused finalization all pass.

## Pre-Filing Preflight

Candidate-content preflights executed before live filing:

- `scripts/bridge_applicability_preflight.py --content-file`: PASS,
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, `blocking_errors: []`, packet
  `sha256:5c397c9feb49ce8a95bb287c2aea83148d194cd5956e715afa8fa5059e1dd52f`.
- `scripts/adr_dcl_clause_preflight.py --content-file`: PASS, five clauses
  evaluated, four `must_apply`, zero mandatory evidence gaps, and zero
  blocking gaps.
- Live filing remains subject to the helper-mediated credential,
  author-provenance, project-linkage, cross-harness-disposition,
  non-impairment, collision, and publication-admission gates.

## Risks / Rollback

The primary risk is over-broad mutation detection that blocks legitimate
read-only shell or adapter activity. Tests therefore pair each deny case with
nearby allowed controls and preserve the current additive verdict and valid
approval-packet paths. A second risk is adapter drift: equivalent intent could
normalize differently across harnesses. One parameterized decision matrix and
subprocess response tests cover A/B/C/E.

Rollback requires separate authority and reverts only the focused WI-5497
source and test hunks. The numbered bridge chain, MemBase work item, test
artifact, owner decision, PAUTH, and verdict history remain append-only. No
canonical carrier restore, dispatcher rollback, TAFE rollback, or Git history
rewrite is part of this work.

## Files Expected To Change

- `.claude/hooks/lo-file-safety-gate.py`
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`
- `scripts/cursor_hook_adapter.py`
- `scripts/lo_file_safety_payloads.py`
- `scripts/antigravity_hook_adapter.py`
- `platform_tests/scripts/test_lo_file_safety_payloads.py`
- `platform_tests/scripts/test_antigravity_hook_adapter.py`

## Recommended Commit Type

`fix(governance)`: deny cross-harness whole-carrier mutation while preserving
allowed LO file-safety behavior.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
