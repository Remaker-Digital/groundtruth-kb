NO-GO

# Loyal Opposition Review: Canonical Terminology Surface Implementation

Reviewed document: `bridge/gtkb-canonical-terminology-surface-implementation-001.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The implementation bridge is directionally correct and resolves several prior
scope conditions: Agent Red does not get a repo `memory/MEMORY.md`, the command
surface remains `gt project doctor`, and GT-KB local `groundtruth.db` is not
treated as a release seed.

I cannot issue GO yet because the implementation plan still has scaffold and
doctor-contract gaps that would recreate the same failure class: fresh sessions
and fresh scaffolded dual-agent projects would not reliably inherit or check
the terminology.

## Prior Deliberations

I searched the deliberation archive per
`.claude/rules/deliberation-protocol.md`.

Relevant results for `canonical terminology glossary propagation bridge gate`
included `DELIB-0628` and `DELIB-0632` for bridge-gate governance history, plus
older bridge/runtime state records. Relevant results for `GroundTruth rename
transition Membase MemBase` included `DELIB-0105`, `DELIB-0023`,
`DELIB-0021`, `DELIB-0109`, `DELIB-0022`, `DELIB-0108`, and `DELIB-0020`.
I found no deliberation that supersedes this implementation bridge.

## Findings

### P1 - New canonical terminology files do not have a valid managed-artifact path

The proposal makes the reproducible seed depend on
`templates/canonical-terminology.md` and `templates/canonical-terminology.toml`
being scaffolded into adopter repos, then says to update
`templates/managed-artifacts.toml` with the two new template paths
(`bridge/gtkb-canonical-terminology-surface-implementation-001.md:66`,
`:208`, `:231`).

The current GT-KB managed registry does not have a generic `template` or
`project-file` artifact class. It accepts only `hook`, `rule`, `skill`,
`settings-hook-registration`, and `gitignore-pattern`
(`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:140`-`:145`),
and unknown classes fail validation
(`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:320`-`:323`).
The scaffold code only consumes registry file artifacts through specific
class filters: hooks and rules for base templates
(`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:183`-`:203`) and rules
for dual-agent templates (`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:282`-`:286`).

Impact: the proposed reproducible seed is not actually reproducible as written.
A revised bridge must either add and test a real generic managed project-file
class, or explicitly hard-code these two files into scaffold/upgrade/doctor
behavior and stop claiming they are handled by the existing registry model.

Required action: choose one implementation path and spell out exact source
paths, target paths, profiles, scaffold behavior, upgrade behavior, doctor
behavior, and tests.

### P1 - The GT-KB template plan omits the AGENTS.md template that Codex actually loads

The owner scope required startup-visible terminology in Agent Red
`CLAUDE.md` / `AGENTS.md` equivalents and GT-KB template inheritance for newly
scaffolded projects (`bridge/gtkb-canonical-terminology-surface-001.md:33`-`:36`,
`:57`-`:65`). The implementation bridge's Phase 3 updates
`templates/CLAUDE.md`, `templates/MEMORY.md`, and
`templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`, but not
`templates/project/AGENTS.md`
(`bridge/gtkb-canonical-terminology-surface-implementation-001.md:208`).

That is the wrong omission. GT-KB dual-agent scaffold copies
`templates/project/AGENTS.md` directly to root `AGENTS.md`
(`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:272`-`:275`). The
current AGENTS template defines the Loyal Opposition role and startup checklist
but does not define MemBase, GroundTruth KB, or the canonical terminology block
(`groundtruth-kb/templates/project/AGENTS.md:1`-`:5`, `:30`-`:35`, `:67`-`:70`).

Impact: a freshly scaffolded dual-agent project can still give Codex no
startup-visible definition of MemBase through its primary operating contract,
which is the incident this workstream is meant to prevent.

Required action: add `templates/project/AGENTS.md` as an explicit propagation
target and add tests that scaffold a dual-agent project and assert root
`AGENTS.md` contains the required canonical startup terms or the canonical
terminology pointer.

### P1 - The doctor algorithm excludes files the owner explicitly required it to check

The owner directive says the check should flag ADR-0001 terminology missing or
inconsistent across `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, `docs`, and
`templates` (`bridge/gtkb-canonical-terminology-surface-001.md:36`,
`:67`-`:69`). The proposed TOML defaults only check `CLAUDE.md`, `AGENTS.md`,
and `.claude/rules/*.md`
(`bridge/gtkb-canonical-terminology-surface-implementation-001.md:80`-`:83`).

This also conflicts with the proposal's own verification promise that a
freshly scaffolded project fails when repo `MEMORY.md` is missing
(`bridge/gtkb-canonical-terminology-surface-implementation-001.md:38`-`:39`).
As written, `MEMORY.md` is not in `checked_files`, and `memory/*.md` is ignored.

Impact: the doctor would not cover the template/doc drift class it is supposed
to guard, and it would not prove the default repo `MEMORY.md` contract for new
adopters.

Required action: revise the algorithm to define profile-aware checked surfaces:
Agent Red may skip harness-resolved MEMORY.md content checks, but default
scaffolded projects must check root `MEMORY.md`; GT-KB implementation evidence
must check the relevant `templates/` files and at least the live docs surfaces
where ADR-0001 terminology is published. Historical/archive exclusions are fine,
but the active docs/templates scope cannot be silently excluded.

### P2 - The bridge-gate test plan overstates existing doctor coverage

The proposal says existing doctor tests for `rule.deliberation-protocol` will
automatically exercise the content-hash check
(`bridge/gtkb-canonical-terminology-surface-implementation-001.md:55`). The
current doctor result model has only name/required/found/status/message fields
(`groundtruth-kb/src/groundtruth_kb/project/doctor.py:25`-`:35`), `_check_rules`
only verifies that some rule files exist
(`groundtruth-kb/src/groundtruth_kb/project/doctor.py:353`-`:378`), and
`_check_file_bridge_setup` only verifies required bridge rule presence
(`groundtruth-kb/src/groundtruth_kb/project/doctor.py:804`-`:824`).

Impact: a stale `deliberation-protocol.md` could pass doctor even if the new
"Canonical Term Propagation Gate" section is absent.

Required action: add explicit scaffold and upgrade tests that read the generated
or upgraded `.claude/rules/deliberation-protocol.md` content and assert the new
section is present. If doctor should enforce rule content drift, add that as a
separate implementation item with tests rather than relying on current doctor
behavior.

### P2 - The minimum term-set wording needs to distinguish canonical records from aliases

The owner-listed terms include both `Knowledge Database` and `GT-KB`
(`bridge/gtkb-canonical-terminology-surface-001.md:33`, `:54`). The proposed
registry treats `Knowledge Database` as a MemBase alias and `GT-KB` as a
GroundTruth KB alias
(`bridge/gtkb-canonical-terminology-surface-implementation-001.md:85`-`:90`,
`:120`-`:125`), while the proposal text says it implements the "8 owner-listed
+ Work Item + Specification" minimum set
(`bridge/gtkb-canonical-terminology-surface-implementation-001.md:179`).

Impact: alias treatment is probably acceptable, but the bridge currently reads
as if all owner-listed terms are first-class term records. That ambiguity will
make post-implementation verification noisy.

Required action: state explicitly whether `Knowledge Database` and `GT-KB` are
aliases or independent canonical entries, and add tests/assertions for whichever
contract is chosen.

## Answers To Codex Questions

1. `templates/managed-artifacts.toml` is not sufficient as-is for
   `canonical-terminology.md` and `.toml`. The current registry has no generic
   template/project-file class. Do not register them as `rule` unless the
   target really is under `.claude/rules/`; that would be semantically wrong and
   would interact badly with rule-focused doctor logic.

2. Yes, extending `templates/rules/deliberation-protocol.md` needs test updates
   beyond assuming a doctor content-hash check. Add content assertions for
   scaffold and upgrade. Also update `templates/project/AGENTS.md`, because
   that is the dual-agent startup file Codex receives.

3. The regex-based conflicting-definition WARN is acceptable only as a
   non-blocking v1 heuristic. It must not be the only consistency protection,
   and it should be covered by focused tests showing file:line evidence. If
   implementation time is tight, defer conflict detection to v1.1 and ship
   presence/pointer checks first.

4. A full migration system can defer. Keep `[meta].version = "1.0.0"` now and
   make unsupported versions produce a clear WARN or ERROR. Do not build
   registry migrations until there is a second schema version.

## Required Conditions For Revised Proposal

- Define a real scaffold/upgrade/doctor path for `.claude/canonical-terminology.md`
  and `.claude/canonical-terminology.toml`, including whether this requires a
  new managed artifact class.
- Add `groundtruth-kb/templates/project/AGENTS.md` to the propagation plan and
  tests.
- Expand the doctor algorithm to cover root `MEMORY.md` for default projects
  and active GT-KB docs/templates, while preserving the Agent Red harness-memory
  exception.
- Replace the claimed automatic rule content-hash coverage with explicit
  content assertions, or implement and test actual doctor drift checks.
- Clarify alias versus canonical-record treatment for `Knowledge Database` and
  `GT-KB`.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-canonical-terminology-surface-implementation' -Context 20,80
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-001.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-001.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-002.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "canonical terminology glossary propagation bridge gate" --limit 8
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "GroundTruth rename transition Membase MemBase" --limit 8
rg -n "MemBase|MEMORY\.md|Deliberation Archive|Prime Builder|Loyal Opposition|GroundTruth KB|GT-KB|Knowledge Database" CLAUDE.md AGENTS.md .claude/rules/*.md
rg -n "managed-artifacts|ManagedArtifact|artifact|source|target|doctor_required_profiles|protected|upgrade" src/groundtruth_kb/project tests/test_upgrade.py tests/test_doctor_registry_parity.py tests/test_scaffold_project.py -S
rg -n "MemBase|GroundTruth KB|GT-KB|Deliberation Archive|Prime Builder|Loyal Opposition|MEMORY\.md|Knowledge Database|canonical terminology|Canonical Terminology" templates/project/AGENTS.md templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md templates/CLAUDE.md templates/MEMORY.md
Line-number reads of `managed_registry.py`, `scaffold.py`, `doctor.py`, `templates/project/AGENTS.md`, and `templates/rules/deliberation-protocol.md`
```

No product tests were run because this is a pre-implementation proposal review.
