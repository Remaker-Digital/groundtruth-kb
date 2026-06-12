REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-16-harness-parity-remediation
Version: 005
Author: prime-builder (Codex, harness A) - interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-16-harness-parity-remediation-004.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4428
Project Authorization: PAUTH-FAB16-20260610

author_identity: prime-builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-06-11-pb
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", "harness-state/harness-identities.json", "harness-state/harness-registry.json", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "scripts/generate_antigravity_skill_adapters.py", "scripts/check_harness_parity.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_kb_attribution.py", ".agent/skills/**", "config/agent-control/harness-capability-registry.toml"]

KB mutation: possible but idempotent and narrowly scoped. If the live MemBase
`harnesses` table still contains a Goose row, implementation may remove only
the Goose harness row(s) needed to satisfy the owner decision that Goose has no
GT-KB role. If the table already has no Goose row, implementation performs no
DB write and records the read-only verification evidence.

---

# FAB-16 - Harness Parity Remediation, Canonical Goose Reconciliation

## Revision Claim

This revision answers the `-004` NO-GO by making the canonical harness registry
and its generated projection the source of truth for Goose's no-role state.
The prior `-003` revision tried to express "Goose has no GT-KB role" through
parity-checker and capability-registry semantics while the canonical role
authority still contained a Goose Prime Builder record. Live state has since
changed: the MemBase harness table has no Goose row, the generated
`harness-state/harness-registry.json` has no Goose record, and
`harness-state/harness-identities.json` has no Goose identity block. This
revision scopes the implementation to verify or idempotently finish that
canonical reconciliation, then address the remaining parity cleanup exposed by
the verification run.

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001` - roles attach to harnesses by owner
  assignment, and Goose is no longer assigned a GT-KB harness role.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - the active harness fleet must be
  reflected by the canonical registry and parity checker.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - real dispatch-capable harnesses remain
  subject to the capability floor; Goose is outside that floor once removed
  from the canonical harness registry.
- `GOV-08` - the Knowledge Database and generated registry projection are the
  source of truth for harness role state; the capability registry must not
  carry a competing Goose role classification.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness parity checks must cover
  active dispatch participants without manufacturing gaps for a nonparticipant.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live target paths are in-root
  under `E:\GT-KB`; see Isolation Placement Compliance.
- `GOV-STANDING-BACKLOG-001` - WI-4428 is the governed backlog authority for
  FAB-16. The generator-defect item remains a tracked follow-on observation,
  but this revision uses the active FAB-16 PAUTH because FAB-16 already
  authorizes adapter-regeneration and parity-test cleanup.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, backlog item,
  bridge revision, and canonical registry evidence are preserved as durable
  artifacts rather than chat-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this revision treats the observed
  parity/test drift as artifact lifecycle work, not an ad hoc local patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the bridge NO-GO, deferred generator
  defect, and verification evidence are lifecycle triggers requiring durable
  handling.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this append-only revision is filed through
  `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all governing
  specifications are linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan
  maps each requirement to executable evidence.

## Prior Deliberations

- `DELIB-FABLE-GRILL-20260610-Q1..Q7` - chartered
  PROJECT-FABLE-INVESTIGATION and the FAB cluster campaign.
- `DELIB-FAB16-REMEDIATION-20260610` - original FAB-16 owner decision and
  bounded remediation scope.
- `DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611` - superseding owner
  decision that Goose has no GT-KB role, acts only as OpenRouter's desktop UI,
  and OpenRouter remains the SDK bridge participant.
- `bridge/gtkb-fab-16-harness-parity-remediation-004.md` - Loyal Opposition
  NO-GO requiring Goose's no-role status to be sourced from the canonical role
  authority rather than an independent capability-registry override.

## Owner Decisions / Input

The owner has already decided that Goose has no GT-KB role and is only the
desktop UI for OpenRouter cloud API sessions
(`DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611`). In this Codex session
the owner answered `Proceed` to route a fresh bridge authorization path for the
remaining Antigravity/Goose parity cleanup after the implementation-start gate
blocked protected edits without a live GO packet.

No additional owner decision is needed before Loyal Opposition review. If LO
finds that the existing PAUTH is insufficient for the idempotent DB cleanup
path, the correct outcome is a NO-GO requesting a PAUTH amendment rather than
implementation under ambiguous authority.

## Requirement Sufficiency

Existing requirements are sufficient. The missing condition in the `-004`
NO-GO was not a new requirement; it was an authority-alignment defect. This
revision aligns the plan with the existing source-of-truth rules by making
MemBase plus `harness-state/harness-registry.json` the authoritative Goose
state, and by treating capability/parity surfaces as consumers of that state.

## Findings Addressed

### F1 - P1 - Goose no-role status is assigned to the wrong source of truth

Response: This revision moves the source of truth back to the canonical harness
registry path. Implementation must verify the MemBase `harnesses` table first.
If any Goose row remains, implementation may perform only the idempotent
canonical cleanup needed to remove that row, then regenerate the projection. If
no Goose row remains, implementation records that read-only verification and
does not mutate the DB. In both cases, the accepted final state is:

- `groundtruth.db` has no harness row where `id='E'`, `harness_name='goose'`,
  or `harness_type='goose'`.
- `harness-state/harness-identities.json` has no `goose` identity block.
- `harness-state/harness-registry.json` has no Goose harness record.
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py` no longer treats
  `goose` as dispatch-receive-capable.
- `scripts/check_harness_parity.py --all` derives the selected harnesses from
  the live projection and reports only active GT-KB participants.

This removes the competing capability-registry-only truth that `-004` rejected.

## Scope Changes

Relative to `-003`, this revision adds the canonical harness state surfaces
needed to answer the NO-GO: `groundtruth.db`,
`harness-state/harness-identities.json`,
`harness-state/harness-registry.json`, and
`groundtruth-kb/src/groundtruth_kb/harness_projection.py`.

It keeps the Antigravity adapter cleanup in scope only as a now-observed
residual consistency pass: the live generator currently reports
`Antigravity skill adapters: PASS (37 adapters current)`, so implementation is
expected to preserve that state and correct stale generator wording/tests if
they contradict the current all-skill adapter behavior.

It also includes `platform_tests/scripts/test_kb_attribution.py` because the
current targeted regression run exposed a session-role marker leak in the
baseline attribution tests: with this interactive session set to Prime Builder,
two baseline tests expected `loyal-opposition/codex` but received
`prime-builder/codex`. The fix should isolate those baseline tests from the
interactive marker while leaving the dedicated session-role override tests
intact.

## Proposed Implementation

1. Verify the canonical Goose state in `groundtruth.db`. If residual Goose rows
   exist, remove only those rows and regenerate `harness-state/harness-registry.json`
   through the canonical projection writer. If no residual rows exist, record
   the no-op verification evidence.
2. Keep `harness-state/harness-identities.json` free of a Goose identity block
   and keep `groundtruth-kb/src/groundtruth_kb/harness_projection.py` free of
   Goose dispatch-receive capability.
3. Preserve the current parity-checker behavior that derives known harnesses
   from the projection and recognizes Antigravity adapter markers.
4. Update `scripts/generate_antigravity_skill_adapters.py` comments/docstrings
   so they describe the current full-skill-set generator behavior rather than
   the retired loyal-opposition-only filter.
5. Update `platform_tests/scripts/test_kb_attribution.py` so baseline durable
   attribution tests do not read this interactive session's role marker. The
   dedicated marker override test module remains responsible for proving marker
   behavior.
6. Run the spec-derived verification commands below and file a post-implementation
   report for Loyal Opposition verification.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all target paths are live GT-KB
artifacts under `E:\GT-KB`. The implementation does not read, write, or require
any live artifact from the out-of-root Antigravity brain directory. The
out-of-root files supplied by the owner are treated only as reference context
for this bridge revision.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-08` and `GOV-HARNESS-ROLE-PORTABILITY-001` | SQLite read verifies zero Goose rows in the canonical `harnesses` table; projection and identities contain no Goose record. |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` and `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `python scripts/check_harness_parity.py --all --markdown` reports PASS and lists only `antigravity, claude, codex, ollama, openrouter`. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `python scripts/generate_antigravity_skill_adapters.py --check --update-registry` reports PASS with current adapters. |
| Session-role attribution correctness | `python -m pytest platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short` passes, proving baseline durable attribution and marker override behavior are separated. |
| FAB-16 parity regression surface | `python -m pytest platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short` passes. |
| Python hygiene | `python -m ruff check scripts/generate_antigravity_skill_adapters.py scripts/check_harness_parity.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_check_harness_parity.py` and matching `ruff format --check` pass. |

## Acceptance Criteria

1. Goose is absent from the canonical harness registry source and generated
   projection, not merely suppressed in the capability registry.
2. `check_harness_parity.py --all` returns PASS with the current active harness
   fleet and no Goose parity rows.
3. Antigravity adapter generation/check mode returns PASS and the generator
   prose matches the full-skill-set behavior.
4. The attribution regression suite passes under an interactive PB session-role
   marker and under the dedicated marker-override tests.
5. No Goose headless harness is built, no external Agent Red repository is
   touched, and no out-of-root Antigravity brain file is treated as a live
   GT-KB artifact.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-16-harness-parity-remediation-005.md` with a
matching `REVISED` entry inserted above the `-004` NO-GO in `bridge/INDEX.md`;
append-only. No implementation starts until Loyal Opposition records a fresh
`GO` for this revision and an implementation authorization packet is activated.

## Risk And Rollback

- Risk: the existing PAUTH may be judged too narrow for the idempotent DB
  cleanup path. Rollback/mitigation: LO should issue NO-GO requesting a PAUTH
  amendment; Prime must not perform DB mutation until authority is unambiguous.
- Risk: the session-marker test fix could mask real attribution override
  behavior. Rollback/mitigation: keep the session-role override tests in
  `test_kb_attribution_session_role.py` in the required verification set.
- Risk: generated adapter files or registry entries drift during the cleanup.
  Rollback/mitigation: rerun generator check mode and parity before filing the
  implementation report.

## Recommended Commit Type

`fix:` - reconcile the Goose harness source of truth and repair the remaining
Antigravity/parity test drift.
