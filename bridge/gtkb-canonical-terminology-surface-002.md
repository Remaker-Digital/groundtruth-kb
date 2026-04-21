GO

# Loyal Opposition Review: Canonical Terminology Surface

Reviewed document: `bridge/gtkb-canonical-terminology-surface-001.md`
Verdict: GO with conditions
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The proposed canonical terminology workstream should proceed. The triggering
failure is real: Agent Red's always-loaded control surface does not expose
`MemBase`, while GT-KB docs and templates already use the ADR-0001 vocabulary.
The right remediation is not another one-off doc edit; it is a governed
terminology record plus startup, template, doctor, and bridge-gate propagation.

This GO is conditional because two implementation details in the scope proposal
would otherwise create avoidable drift: Agent Red does not currently have a
repo `memory/MEMORY.md`, and any new bridge-gate rule must be propagated through
GT-KB's managed template registry if it is meant to survive scaffold/upgrade.

## Prior Deliberations

I searched the deliberation archive before review per
`.claude/rules/deliberation-protocol.md`.

Command:

```text
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'
python -m groundtruth_kb deliberations search "GroundTruth rename transition Membase MemBase" --limit 10
```

Relevant results included `DELIB-0105` (GroundTruth Rename Transition),
`DELIB-0023` (Membase Structural Separation Plan), `DELIB-0021`
(Membase-4-Claude v1 Platform Specification), `DELIB-0109`
(Membase Evaluation And Implementation), `DELIB-0022`, `DELIB-0108`,
`DELIB-0020`, and `DELIB-0215`.

A second search for `canonical terminology glossary propagation bridge gate`
returned governance/bridge-gate history including `DELIB-0628`,
`DELIB-0632`, and `DELIB-0229`, but no prior canonical-terminology-specific
proposal that supersedes this one.

## Evidence

- `rg -n "MemBase|Membase" CLAUDE.md AGENTS.md CLAUDE-REFERENCE.md CLAUDE-ARCHITECTURE.md` in Agent Red returned no matches. This verifies the proposal's core startup-visibility gap.
- Agent Red `CLAUDE.md:19` says all project knowledge lives in the Knowledge Database, but does not name `MemBase`.
- Agent Red `AGENTS.md:15` through `AGENTS.md:16` define Loyal Opposition and Prime Builder roles, but not the broader canonical term set.
- Agent Red `CLAUDE-ARCHITECTURE.md:225` references `Knowledge Database (groundtruth.db)`, but not `MemBase`.
- Agent Red has no repo `memory/MEMORY.md`: `Get-ChildItem -Force memory` returned only `s133-live-test-migration.md`, `testing-research.md`, and `work_list.md`.
- Agent Red `CLAUDE.md:10` says `memory/MEMORY.md` resolves through the Claude Code harness path `~/.claude/projects/<project-hash>/memory/`, not the repo `memory/` directory.
- GT-KB already defines the public architecture term: `docs/architecture/product-split.md:13` says `Core Knowledge Database (MemBase)`, and `docs/architecture/product-split.md:27` maps Layer 1 to ADR-0001's canonical knowledge/specifications tier.
- GT-KB templates already expose the term in part: `templates/CLAUDE.md:9` names MemBase, MEMORY.md, and Deliberation Archive; `templates/CLAUDE.md:78` has a `MemBase (Canonical Knowledge and Specifications)` section; `templates/MEMORY.md:6` and `templates/MEMORY.md:34` state the MEMORY.md operational-notepad boundary.
- GT-KB's doctor extension point exists as `gt project doctor`: `src/groundtruth_kb/cli.py:658` registers `@project.command("doctor")`, and `src/groundtruth_kb/project/doctor.py:1027` defines `run_doctor(...)`.
- GT-KB doctor checks are centrally assembled in `run_doctor()`: `src/groundtruth_kb/project/doctor.py:1038` through `src/groundtruth_kb/project/doctor.py:1069`.
- GT-KB's managed artifact registry controls scaffold/upgrade/doctor propagation. `templates/managed-artifacts.toml` contains `rule.deliberation-protocol` with target `.claude/rules/deliberation-protocol.md` and `doctor_required_profiles = ["dual-agent", "dual-agent-webapp"]`.
- GT-KB's document artifact model supports the proposed terminology record: `src/groundtruth_kb/db.py:145` creates `documents`, and `src/groundtruth_kb/db.py:2024` through `src/groundtruth_kb/db.py:2044` define `KnowledgeDB.insert_document(...)` with `category`, `tags`, `status`, `source_path`, `changed_by`, and append-only versioning.
- Local DB readback verified the relevant artifact surface. Agent Red `groundtruth.db` has `specifications=8317`, `documents=240`, `deliberations=720`. GT-KB `groundtruth.db` contains `ADR-0001` as `status=verified`, `type=architecture_decision`, title `Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)`.

## Conditions For Implementation

1. Resolve the Agent Red `MEMORY.md` target before editing or doctor-scanning it.

   The scope proposal says to update `memory/MEMORY.md`, but that file is not
   present in the Agent Red repo, and `CLAUDE.md:10` says the operational
   MEMORY.md is a Claude Code harness artifact outside the repo. The
   implementation bridge must name the exact target and verification model:
   either update the harness-resolved MEMORY.md as local operational state and
   report it as non-git evidence, or create/adopt a repo-root `MEMORY.md` only
   with explicit owner approval and a matching `CLAUDE.md` wording update. Do
   not implement a doctor rule that fails Agent Red solely because repo
   `memory/MEMORY.md` is absent under the current contract.

2. Propagate any bridge-gate rule through the GT-KB managed template system.

   If the implementation modifies the existing deliberation rule, update both
   Agent Red `.claude/rules/deliberation-protocol.md` and GT-KB
   `templates/rules/deliberation-protocol.md`. If it adds a new
   `.claude/rules/canonical-terminology-propagation.md`, also add the
   corresponding `templates/rules/...` file, a `templates/managed-artifacts.toml`
   record, and focused scaffold/upgrade/doctor tests. Otherwise future
   scaffolded projects will not inherit the bridge gate.

3. Use the existing command name `gt project doctor`, unless the implementation
   deliberately adds and tests a top-level `gt doctor` alias.

   The live CLI registers doctor under the `project` group. The proposal may
   keep "doctor check" as plain English, but implementation docs, tests, and
   post-implementation evidence must not claim a top-level `gt doctor` contract
   unless that alias is actually implemented.

4. Treat local MemBase writes as local evidence unless they are also backed by a
   reproducible seed/template path.

   `insert_document()` is suitable for the Agent Red terminology record.
   However, prior ADR verification already noted that GT-KB `groundtruth.db` is
   not a git-tracked release artifact. If the terminology record is required in
   fresh GT-KB adopters, the implementation must provide a reproducible seed,
   scaffold, or migration path, not only a local DB row. Post-implementation
   evidence must include readback of the Agent Red document record and a clear
   statement of whether GT-KB local DB mutation is in scope.

5. Define the terminology consistency algorithm before coding the doctor check.

   The doctor rule should compare against a concrete canonical term set and
   report file:line evidence for missing or conflicting terms. Avoid a broad
   repository grep that fails on any historical, quoted, or changelog usage.
   At minimum, the implementation bridge must list: checked files/trees,
   required terms, accepted aliases, severity rules, and out-of-scope historical
   paths.

6. Keep the startup block concise and pointer-based.

   The concise glossary block in `CLAUDE.md` and `AGENTS.md` should define the
   owner-listed terms, then point to the full terminology record and the
   read-only terminology file. Do not paste the full `MEMBASE-4-CLAUDE.md`
   glossary into startup files.

## Recommendations

- Prefer updating the existing GT-KB `templates/rules/deliberation-protocol.md`
  unless the new bridge-gate behavior becomes large enough to justify a
  separate managed rule. A new managed rule is viable, but it has more scaffold,
  upgrade, doctor, and test surface.
- For the terminology record, use a stable document id such as
  `DOC-CANONICAL-TERMINOLOGY` rather than an auto-numbered local id, so startup
  pointers and doctor checks can refer to it deterministically.
- Make `ADR-0001` the authority for tier boundaries and the terminology record
  the authority for user-facing definitions. That keeps the ADR from becoming a
  glossary dump while still anchoring the hierarchy.
- Add a narrowly scoped verification test that simulates a freshly scaffolded
  dual-agent project and asserts the generated `CLAUDE.md`, `MEMORY.md`, and
  `.claude/rules/deliberation-protocol.md` contain the canonical terminology
  pointer.

## Decision Needed From Owner

- Confirm the Agent Red operational-memory target for this work: harness
  `~/.claude/projects/<hash>/memory/MEMORY.md`, a new/reintroduced repo
  `MEMORY.md`, or no Agent Red MEMORY.md edit for this phase.
- Confirm doctor severity: ERROR for missing required startup terms and WARN
  for minor definition drift is a reasonable default.

## Verification Commands Run

```text
Select-String -Path bridge/INDEX.md -Pattern '^Document: gtkb-canonical-terminology-surface$' -Context 0,5
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-001.md
rg -n "MemBase|Membase" CLAUDE.md AGENTS.md CLAUDE-REFERENCE.md CLAUDE-ARCHITECTURE.md
Get-ChildItem -Force memory
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "GroundTruth rename transition Membase MemBase" --limit 10
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "canonical terminology glossary propagation bridge gate" --limit 10
rg -n "def .*doctor|doctor|gt doctor|gt project doctor|ADR-0001|MemBase|Core Knowledge Database" .  (in groundtruth-kb)
rg -n "gt project doctor|gt doctor" docs templates src tests README.md CHANGELOG.md  (in groundtruth-kb)
Python sqlite readback of Agent Red and GT-KB `groundtruth.db` counts and ADR-0001 metadata
```

No code or product tests were run because this is a scope/proposal review, not
an implementation verification.
