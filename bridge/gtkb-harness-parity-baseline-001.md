NEW

# GTKB Harness Parity Baseline Implementation Proposal

Filed by: Codex
Date: 2026-05-06
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Claim

Establish harness parity as a governed, repeatable control so Claude Code and
Codex sessions know which role capabilities are required, where those
capabilities live, and whether each harness has native, fallback, unsupported,
or owner-gated access.

This proposal builds on the initial implementation already created in this
session:

- `.claude/skills/harness-parity-review/SKILL.md`
- `.claude/skills/structural-hygiene-review/SKILL.md`
- `config/agent-control/harness-capability-registry.toml`
- `scripts/check_harness_parity.py`
- `tests/scripts/test_check_harness_parity.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-PARITY-REVIEW-2026-05-06.md`

## Specification Links

- `.claude/rules/operating-model.md` - canonical operating-model vocabulary and
  role concepts.
- `.claude/rules/canonical-terminology.md` - glossary alignment source.
- `.claude/rules/project-root-boundary.md` - all live GT-KB harness parity
  artifacts must remain under `E:\GT-KB`.
- `harness-state/harness-identities.json` - durable harness installation IDs.
- `harness-state/role-assignments.json` - durable role assignment source of
  truth.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner-relevant process changes and
  accepted future work should be captured as durable artifacts.

## Current Baseline

The initial harness parity review was executed on 2026-05-06:

```powershell
python scripts/check_harness_parity.py --all --markdown
python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
```

Findings:

- all registered Claude project skills are `PASS`;
- all registered Codex project-skill capabilities are `DEGRADED` because Codex
  can read the `.claude/skills/*/SKILL.md` files but does not receive them as
  native Codex skills;
- no role-critical capability is `MISSING`;
- no project skill is undeclared in the registry.

This is an acceptable baseline for continued work, but it is not the target
state. The target state is that required capabilities are either native `PASS`
or explicitly documented as owner-gated/unsupported.

## Proposed Implementation

### Phase 1 - Baseline Control

Keep the newly added registry and checker as the authoritative parity control:

- `config/agent-control/harness-capability-registry.toml` declares semantic
  capabilities and per-harness access state.
- `scripts/check_harness_parity.py` evaluates selected harnesses and roles.
- `tests/scripts/test_check_harness_parity.py` verifies fallback, missing, and
  undeclared-surface behavior.

Acceptance for Phase 1:

- checker exits nonzero when a required selected capability is missing;
- checker exits zero with `WARN` when capabilities are available only through
  documented fallback;
- registry covers every `.claude/skills/*/SKILL.md` project skill;
- review output distinguishes `PASS`, `DEGRADED`, `MISSING`, `EXTRA`,
  `UNSUPPORTED`, and `OWNER_ACTION_REQUIRED`.

### Phase 2 - Event Triggers

Wire the parity checker into regular lifecycle events:

- Session start: run a fast role-scoped parity check after durable harness ID
  and role resolution.
- Role assignment change: run parity for the affected harness and newly assigned
  role after `scripts/harness_roles.py` updates `harness-state/role-assignments.json`.
- Capability source change: run full parity when any of these paths changes:
  `.claude/skills/**/SKILL.md`, `.claude/settings.json`, `.codex/hooks.json`,
  `.codex/config.toml`, `config/agent-control/harness-capability-registry.toml`,
  or harness-state role/identity files.
- Release candidate gate: include a full parity review so degraded or missing
  harness capabilities cannot remain invisible.

Implementation candidates:

- extend `scripts/session_self_initialization.py` to include parity status in
  startup output;
- extend `scripts/harness_roles.py` with a post-update parity check call;
- add a narrow watcher/check command, or reuse repo-native hook surfaces, to run
  parity after capability-source changes;
- add a release-gate assertion to fail only on required `MISSING`, while
  preserving `DEGRADED` as a visible warning until native parity is complete.

### Phase 3 - Native Codex Skill Parity

Move required Codex skill capabilities from `DEGRADED` to `PASS` by adding a
project-controlled native Codex skill surface or generated adapter surface.

Recommended approach:

- keep `.claude/skills` as the canonical authoring source for project skills
  unless a future decision creates a neutral `skills/` root;
- generate Codex-readable skill adapters under a project-owned path;
- include source hash, canonical source path, and generated timestamp in each
  adapter;
- update the registry so Codex required skills point to native adapters only
  when the adapter exists and matches the canonical source;
- add stale-adapter detection to `scripts/check_harness_parity.py`.

Acceptance for Phase 3:

- required Codex role capabilities are `PASS` or explicitly owner-gated;
- stale generated adapters are reported as `STALE`;
- manual edits to generated adapters are detected or overwritten by a governed
  regeneration command.

### Phase 4 - Structural Hygiene Integration

Use `structural-hygiene-review` as the companion control for parity:

- compare directory names, artifact names, skill names, glossary terms, command
  names, schemas, generated surfaces, and historical/archive markers;
- identify competing cues that can cause agent drift;
- prune, rename, archive, or isolate stale surfaces after bridge approval when
  the change is destructive or formal-governance-sensitive;
- run structural hygiene after parity changes and before release gating.

Acceptance for Phase 4:

- structural hygiene reports identify authority, cue, risk, correction, and
  verification for each issue;
- historical artifacts are clearly isolated and labeled;
- glossary terms are used consistently in capability names and documentation.

## Out Of Scope

- No credential lifecycle changes.
- No production deployment.
- No deletion of historical artifacts without an explicit cleanup proposal or
  owner approval.
- No assumption that Claude Code and Codex expose identical plugin or MCP
  surfaces; parity is semantic capability equivalence, not identical tooling.

## Specification-Derived Test Plan

| Test ID | Requirement | Test |
|---|---|---|
| T-registry-1 | Registry covers every project skill | Repository parity test asserts no undeclared `.claude/skills` entries. |
| T-required-1 | Missing required capability blocks parity | Unit test verifies required missing native surface yields `FAIL`. |
| T-fallback-1 | Documented fallback is visible but nonblocking | Unit test verifies Codex fallback yields `WARN`/`DEGRADED`. |
| T-extra-1 | Undeclared project skill is drift | Unit test verifies unregistered skill reports `EXTRA`. |
| T-session-1 | Session start surfaces parity | Add startup test after Phase 2 wiring. |
| T-role-1 | Role changes trigger role-scoped parity | Add harness role command test after Phase 2 wiring. |
| T-stale-1 | Generated adapter drift is detected | Add stale-adapter test after Phase 3 generator implementation. |
| T-release-1 | Release gate fails on required missing | Add release-gate coverage after Phase 2 or Phase 3. |

## Verification Commands

Current baseline verification:

```powershell
python -m pytest tests/scripts/test_check_harness_parity.py -q --tb=short
python -m ruff check scripts/check_harness_parity.py tests/scripts/test_check_harness_parity.py
python scripts/check_harness_parity.py --all --markdown
python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
```

Future implementation reports must also include targeted tests for any touched
startup, role-change, release-gate, or adapter-generation code.

## Acceptance Criteria

- Harness parity has a registry-backed single source of truth.
- Session-start and role-change flows surface parity status for the active
  harness and role.
- Capability-source changes run or request a parity review.
- Required capabilities are never silently missing.
- Fallbacks are explicit and visible until converted to native parity.
- Structural hygiene review is available as a repeatable skill and is invoked
  for naming, directory, artifact, glossary, schema, and historical-artifact
  alignment reviews.

## Decision Needed From Owner

None for Phase 1 baseline. Later destructive cleanup or formal artifact
renaming must return through the normal bridge/owner approval path.
