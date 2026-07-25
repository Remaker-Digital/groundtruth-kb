REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user; role_source=transcript_init_keyword
author_metadata_source: explicit current-session Codex bridge filing metadata


# Implementation Proposal: Deterministic full-root file-reference migration with retained safety copies

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-v3
Version: 003
Responds to: bridge/gtkb-file-move-rename-canonicalization-v3-002.md
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["scripts/gtkb_file_reference_migration.py", "scripts/generate_rule_compatibility_projections.py", "scripts/generate_cursor_skill_adapters.py", "config/file-reference-migration/wi5640.toml", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_generate_rule_compatibility_projections.py", "platform_tests/scripts/test_generate_cursor_skill_adapters.py", "platform_tests/fixtures/file_reference_migration/**", ".gtkb-state/file-reference-migration/wi5640/**"]
implementation_scope: source | test | configuration | documentation | metadata | runtime_state | governance_evidence

observation_scope: every filesystem entry beneath the repository root, every
configured current SQLite text field, and every separately classified nested
worktree/application/reparse boundary; observation does not grant mutation
authority.

## Claim

The surviving WI-5640 work must be restarted through a fresh lifecycle and
completed by one deterministic, CSV-driven migration program. The program will
inventory every in-root filesystem subtree, classify every path, create or
reconcile the 90 canonical destinations, update every live load-bearing
reference within the approved mutation boundary, regenerate derived artifacts,
and independently verify zero unexplained live residuals.

All 90 old paths will remain present during this program: 52 retained inert
hook/agent-control safety copies and 38 native `.claude/rules` compatibility
paths whose lifecycle is declared per row. Their presence is not a defect, but
no live consumer may continue resolving an obsolete hook or agent-control path.
Required `.claude/rules` projections must be generated one-way from canonical
control files rather than treated as independent authority. Removal of any old
path is outside this proposal and requires a later owner-authorized bridge
lifecycle.

This proposal supersedes the implementation authority of both prior file-move
chains. It preserves those chains as evidence and does not rely on either
terminal token, implementation report, claim, packet, or verification result.

## Revision Response To v3-002

- **F1 queue authority - closed.** Prime Builder filed terminal `WITHDRAWN`
  dispositions for `gtkb-file-move-rename-canonicalization` at version 008,
  `gtkb-skill-rename-rollout` at version 005, and
  `gtkb-skill-rename-cursor-goose-parity` at version 003. Current
  dispatcher/TAFE reports contain zero Prime Builder or Loyal Opposition
  actionable, blocked, or candidate matches for those three threads, and all
  three claim-status queries return null. The valid skill-rollout chain now
  resolves strictly as `NEW -> NO-GO -> REVISED -> GO -> WITHDRAWN`.
  The original file-move chain remains strict-invalid because its historical
  `NEW -> REVISED` defect is immutable; version 008 changes its latest dispatcher
  token but does not repair that evidence. The v2 chain likewise remains
  unsupported incident evidence, and the cursor/Goose chain remains
  strict-invalid because its historical GO lacks required author metadata.
  None is cited as valid authority.
- **Bridge-writer incident disclosure.** The governed writer omitted required
  author metadata from terminal `WITHDRAWN` files because
  `scripts/bridge_author_metadata.py` does not include `WITHDRAWN` in its
  metadata-status set. The same Prime Builder session immediately completed
  only the six missing provenance fields in the three new files; no status or
  semantic disposition text changed. That narrow in-place completion crossed
  the append-only boundary and is recorded as additional WI-5648 control-plane
  evidence, not represented as a clean helper result. This proposal does not
  authorize a bridge-helper repair or rely on that helper for implementation
  safety.
- **Technical advisory expansion.** The declared observation/mutation surfaces,
  scanner grammar, retained-source policy, per-row reconciliation, rule
  lifecycle policy, current-database correction, stable-hash contract, and
  generator/test evidence have been expanded below. These were not formal
  v3-002 findings, but they are treated as mandatory review inputs.

## First-Line Role Eligibility Check

PASS under transcript authority. This Codex session context
`019f863a-acd3-7320-80c0-1831f0936cc0` was initialized by the owner as
`::init gtkb pb`, and the owner subsequently assigned all Prime Builder work for
this program to this session. The durable registry also records Codex A as Prime
Builder. The shared runtime envelope currently reflects a distinct interactive
LO session (`A-2026-07-22T05-57-14Z`); that cache cannot override this
transcript-defined role and is not changed by this filing. `REVISED` is a Prime
Builder status, so this session is eligible to author version 003.

## Requirement Sufficiency

Existing requirements and owner direction are sufficient for this bounded
implementation proposal. No new or revised requirements are required. The
operative owner decisions are the deterministic all-root migration direction
in the current session and
`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.

## Current-State Evidence

- The CSV parses to exactly 90 rows: 33 hooks, 38 rules, and 19 agent-control
  mappings.
- All 90 source files and all 90 destinations currently exist.
- Byte hashes show 11/33 hook pairs equal and 22 different; 38/38 rule pairs
  equal; 16/19 agent-control pairs equal and 3 different. Text-normalized
  comparison proves 24 of the 25 byte divergences are newline-only. The sole
  substantive pair is `harness-capability-registry.toml` to
  `gtkb-harness-capability-registry.toml`.
- The 22 newline-only hook destinations equal their tracked HEAD blobs, but
  seven require explicit semantic adaptation or disposition before apply:
  bridge-axis skill-helper routing; `gtkb_delib_common` imports in the governance
  and owner-decision capture hooks; two renamed sibling-hook comments; three
  owner-decision-tracker ownership strings; and the project-completion Codex
  projection's obsolete byte-parity contract.
- The current renamed harness-capability registry contains 48 deliberate hook
  path changes but also whole-file UTF-8 mojibake and seven missed
  `activity_envelope_manifest_source` path changes. It is not content authority.
  The only acceptable destination is a deterministic reconstruction from the
  clean old source plus all applicable manifest path transformations, with
  Unicode preserved.
- Live obsolete references remain in Codex hook wrappers, managed-artifact
  templates, SoT/context registries, tests, and generated/projected surfaces.
- The focused parity suite currently reports 203 passed and 6 failed out of 209.
- A no-ignore inventory sees more than one million filesystem entries because
  runtime/test trees and nested worktrees dominate. A preliminary direct-literal
  scan generated 360 path forms and found 17,167 files with complete old paths;
  16,085 are in separate nested Git worktrees and 587 remain after only obvious
  history/runtime/application exclusions. These counts are reconnaissance, not
  closure evidence. A naive nested mapping-by-file scan stalls and cannot be
  completion evidence.
- The read-only current database row for harness H version 59 still stores
  `config/agent-control/harness-capability-registry.toml`. Historical harness
  versions are audit history; only the current row may be superseded through a
  governed API-level append and both tracked harness-registry projections must
  be regenerated.
- `groundtruth.db` is hundreds of megabytes and must be queried structurally in
  read-only mode, not decoded or rewritten as one binary file.
- The worktree contains unrelated staged, unstaged, and untracked work. This
  implementation must preserve the live Git index and must not use broad
  staging, reset, checkout, clean, stash apply/drop, or history rewrite.

## In-Root Placement Evidence

All implementation artifacts and mutable target paths are within `E:\GT-KB`.
The scanner's inventory root is exactly `E:\GT-KB`. Paths outside the root,
reparse-point targets, and the lifecycle-independent Agent Red repository are
never followed or mutated. `applications/` is inventoried and classified; any
load-bearing residual there fails the plan and requires a separately governed
application-boundary disposition before mutation.

## Proposed Scope

### 1. One governed migration engine

Create `scripts/gtkb_file_reference_migration.py` using Python standard-library
APIs and structured parsers where available. It must expose five deterministic
modes:

```text
preflight  Validate manifest, policy, root boundary, source/destination state,
           Git tracking, encodings, and complete path classification.
plan       Produce an immutable, sorted operation plan with preimage hashes,
           replacements, generator actions, exclusions, and inventory hash.
apply      Validate plan/preimages, then perform only plan-listed atomic writes.
verify     Re-enumerate independently and fail on residual or unclassified data.
rollback   Restore only plan-recorded preimages without broad Git/stash actions.
```

This proposal has two authorization stages:

1. **Stage A - engine and immutable plan.** A GO on this v3 revision, followed
   by an exact v3 claim and implementation-start packet, authorizes creation of
   the engine, policy, fixtures, and tests plus read-only `preflight`, `plan`,
   and `verify` observations. It does not authorize `apply` or any migration
   write to a repository consumer, destination, projection, registry, database,
   or retained source.
2. **Stage B - exact-plan apply.** Prime Builder must file a separate child
   proposal thread named
   `gtkb-file-move-rename-canonicalization-v3-plan-approval` containing the
   complete sorted operation plan, plan hash, closure fingerprint, all 90
   reconciliation dispositions, residual/exception ledger, generated-file
    actions, and exact normalized file write paths with no directory roots or
    globs. An unrelated LO session must issue GO on that
    exact child proposal. Apply additionally requires a fresh child-thread claim
    and implementation-start packet whose file pointers and target paths match
    the strict child lifecycle and plan. Any plan change requires a new child
    revision and GO.

The child proposal contains one machine-readable `migration_plan_binding` JSON
object with `schema_version`, `plan_sha256`, `closure_fingerprint`,
`write_set_sha256`, `engine_sha256`, `policy_sha256`, `csv_sha256`, and
`git_index_sha256`. Its canonical bytes are UTF-8 JSON with NFC-normalized path
strings, recursively sorted object keys, preserved array order, separators
`,`/`:`, no insignificant whitespace, and a single LF terminator. A separate
`binding_sha256` hashes those bytes.

After the child proposal is filed, LO computes its full-file SHA-256. The GO
must echo the identical binding object and `binding_sha256`, plus
`reviewed_proposal_file` and `reviewed_proposal_sha256`. Apply validates the
packet's own `packet_hash` and expiry, then requires its `bridge_id`,
`proposal_file`, and `go_file` pointers to equal the files returned by the strict
lifecycle resolver. It hashes the proposal bytes and compares them to the GO,
recomputes both binding hashes, and requires the packet's normalized
`target_path_globs` field to contain no patterns and equal the sorted write set
exactly. This supplies the content binding that the current packet schema does
not natively carry.

At Stage A completion, Prime Builder files the main v3 `NEW`
implementation report and releases its claim before filing or claiming the child
thread. Stage A and Stage B claims may never overlap. The child claim must be
held by the current Prime Builder session and its target set must be exactly the
plan's write set, with no reliance on acquisition-time packet preference.

`apply` itself, not only the shell hook, must fail closed unless it independently
proves all of the following: strict-valid child lifecycle with latest `GO`;
unrelated reviewer session; current-session child claim; valid named child
implementation packet and active PAUTH; identical structured `plan_hash` in the
child proposal and GO; exact equality between proposed writes and child
`target_paths`; and matching engine, policy, CSV, preimage, closure inventory,
classification, exception, generator-input, and Git-index hashes. The ordinary
implementation-start gate does not currently recognize this Python subcommand
or bind a packet to a migration-plan hash, so passing that hook is insufficient.
No main-v3 GO or Stage A packet may be interpreted as apply authority.

A changed plan requires a new child proposal version and independent GO. A
changed write set requires a fresh child claim and implementation packet.

### 2. Declarative policy and exclusion ledger

Create `config/file-reference-migration/wi5640.toml` as the canonical policy for
this migration. It must declare:

- repository root and CSV path;
- every mapping category and compatibility mode;
- mutable path roots and exact root-file allowlist;
- canonical authority and projection/generator rules;
- one explicit lifecycle/load-policy row for each of the 38 rule mappings;
- one explicit content-authority/adaptation row for each of the 25 byte-divergent
  pairs;
- encoding/newline preservation policy;
- immutable audit exclusions;
- runtime/cache/tooling exclusions;
- structured read-only data sources such as SQLite;
- application/reparse/external boundary behavior;
- residual classification and exception schema;
- repeated verification and idempotency requirements.

Every discovered path must receive exactly one recorded classification. At
minimum the inventory distinguishes mutable text, generated text, retained
obsolete source, canonical destination, immutable audit, runtime
non-authoritative, binary, structured SQLite, reparse point, application
boundary, unreadable, and unclassified. Unreadable, multiply classified, or
unclassified paths fail preflight/verify. Exclusions are never silent: reports
must include rule ID, path count, total bytes, sorted inventory hash, and
representative paths.

`bridge/**` is immutable canonical audit history and is inventoried but excluded
from correction and residual-failure counts. `.git/**`, `.gtkb-state/**`,
`.pytest-tmp/**`, virtual environments, package caches, build outputs, bytecode,
logs, and other runtime/tooling trees may be excluded only through explicit
policy rules and inventory evidence. The CSV itself is input authority and is
not rewritten by its own mappings.

Each excluded root receives a fixed classification record in the closure
inventory rather than disappearing from the scan. Separate repositories listed
by `git worktree list`, including `.claude/worktrees/**`, are report-only and
must not be traversed as mutable members of the main worktree. `applications/**`
is report-only under the independent application lifecycle. Bridge files,
formal-artifact approvals, barred/retired/archive/history surfaces, and
harness-local scratch/runtime state are each separately classified; none can be
used to hide a live root-owned consumer. Static references anchored to
`tmp_path`, application roots, unresolved variables, or external/reparse targets
are reported with anchor classification and are never auto-rewritten.

The volatile full observation still records every enumerable child beneath an
excluded root. The fixed excluded-root record is used only by the comparable
closure fingerprint. Tests add, change, and delete excluded children and prove
the full observation changes while the closure fingerprint remains stable;
scanner output beneath its own runtime directory must not perturb that
fingerprint.

Worktree discovery parses `git worktree list --porcelain -z` and covers an
in-root worktree represented by a `.git` file, a worktree beneath an excluded
root, an external worktree, and a registered-but-prunable missing worktree.
Registration records are separately hashed and reported; the scanner never
descends into another repository as though it belonged to the main worktree.

The current root contains an access-denied, non-reparse directory at
`groundtruth-kb/pytest-kpi-retro-codex/basetemp4`. Stage A must reproduce and
report that condition. Successful preflight and apply remain impossible until a
separately governed, non-destructive resolution makes the directory enumerable
or an owner-approved evidence standard can prove its contents; an excluded
ancestor may never silently conceal unreadable children.

The policy also declares repository EOL behavior. Unless an existing governed
rule requires otherwise, canonical Python hooks under `config/hooks/**` use LF
through a scoped `.gitattributes` rule so `core.autocrlf=true` cannot recreate
false source/destination divergence. Compatibility projections may preserve a
different native newline only when their generator and hash contract say so.

### 3. Efficient full-root enumeration

Walk the root once per phase with sorted `os.scandir()` traversal, without
following reparse points. Stream each candidate file once. Compile a
multi-pattern matcher or equivalent deterministic index so complexity is based
on total text size plus matches, not `files x mappings` repeated reads.

Binary detection, encoding selection, and text decoding must be deterministic.
Support at minimum UTF-8, UTF-8 with BOM, UTF-16 LE/BE with BOM, and explicitly
declared legacy text encodings. Preserve the original BOM, encoding, newline
convention, file attributes/permissions, and every unrelated byte. A file that
cannot be decoded under policy is classified, not silently skipped.

Query configured SQLite sources through read-only SQLite connections. Report
table, column, row identity, mapping, and variant for any text-field residual.
No raw SQLite mutation is authorized. A live database residual requiring change
stops apply and routes to a separately governed API-level correction.

### 4. Mapping variants and ambiguity policy

Build a collision-checked component trie for all 90 mappings. Matching decodes
one static escaping layer, normalizes Unicode to NFC, collapses separators and
dot components, applies Windows component `casefold`, and emits the exact
canonical destination spelling. Any old/new token collision, prefix ambiguity,
or normalization collision fails preflight.

For each mapping, fixtures and matching cover at minimum:

- direct repository-relative POSIX, Windows, mixed-separator, absolute Windows,
  drive-case, JSON/Python escaped, shell-quoted, `file:` URI,
  `$CLAUDE_PROJECT_DIR`/braced-variable, and referring-file-relative paths;
- statically resolvable segmented construction through `pathlib` `/`,
  `joinpath`, `os.path.join`, PowerShell `Join-Path`, and command/config argument
  fragments;
- glob-bearing forms including `*`, `*.py`, `**`, `glob`, `rglob`, `fnmatch`,
  and TOML/JSON/YAML arrays or fields;
- regular-expression forms including escaped dots, `[/\\]`, `[\\/]`,
  `(?:/|\\)`, escaped filenames, anchors, and case-insensitive flags;
- structured literals in SQLite text cells and generated manifest/registry
  fields.

The scanner also indexes family-level directory expressions that do not contain
one complete manifest filename: parent hook/rule/agent-control regexes, generic
registration patterns, directory-plus-glob constructions, loader roots, and
module import roots. These are reported against every affected mapping family
and require explicit loader-policy disposition; they are not assumed safe merely
because the 90-file component trie has no complete-token hit.

Replace only exact, unambiguous path tokens. Bare filenames, stems, Python
module stems/imports, natural-language names, and substring overlaps are never
blindly replaced, but they may not remain indefinitely unclassified. Resolve
them against the referring file's language, import search roots, configured
loader roots, sibling directories, manifest schema, or command working
directory. Every unresolved or multiply resolvable hit is reported with
file/line or structured-cell location and blocks apply until a machine-readable
policy entry or revised child proposal supplies one disposition.

Test fixtures must include all forms above plus audit-root exclusion, nested
worktree classification, SQLite current-versus-history records, mapping
collision rejection, retained compatibility exceptions, adopter/application
non-replacement, unresolved dynamic-anchor reporting, and literal Windows names
including `CON`, `$null`, `list[str]`, and `-p`. Enumeration and hashing must use
literal or extended Windows paths where needed and must never interpret a real
entry name as a device, option, glob, or expression.

### 5. Destination reconciliation and temporary retention

For each of the 90 rows, plan records source hash, destination hash, transformed
source hash, chosen canonical content hash, and compatibility mode.

- Equal source/destination pairs may proceed without content arbitration.
- A destination equal to the deterministic transformed source is accepted with
  evidence.
- Any other divergence fails planning until an explicit per-row content
  authority/resolution is recorded and independently reviewed. Blind source to
  destination or destination to source copying is forbidden.
- All obsolete sources remain present after apply.
- Old hook and agent-control paths become inert safety copies: launchers,
  registries, templates, docs, tests, and generators must resolve canonical
  destinations.
- `.claude/rules/<old>` remains a native compatibility projection. Its content
  must be generated or verified from canonical `config/agent-control/gtkb-*`
  content with deterministic parity; it is not an independent authority.

The preliminary mandatory hook dispositions are:

| Canonical destination | Required deterministic adaptation |
| --- | --- |
| `config/hooks/gtkb-bridge-axis-2-surface.py` | Replace the retired `.claude/skills/bridge/helpers/scan_bridge.py` helper route with `.claude/skills/gtkb-bridge/helpers/scan_bridge.py`. |
| `config/hooks/gtkb-gov-capture.py` | Import `gtkb_delib_common`, matching the renamed canonical module. |
| `config/hooks/gtkb-owner-decision-capture.py` | Import `gtkb_delib_common`, matching the renamed canonical module. |
| `config/hooks/gtkb-not-markdown.py` | Rename its sibling comment to `gtkb-spec-before-code.py`. |
| `config/hooks/gtkb-owner-decision-tracker.py` | Replace the three generated ownership strings naming `.claude/hooks/owner-decision-tracker.py` with the canonical hook path. |
| `config/hooks/gtkb-spec-before-code.py` | Rename its sibling comment to `gtkb-not-markdown.py`. |
| `config/hooks/gtkb-project-completion-surface.py` | Replace the obsolete byte-identical `.claude/hooks`/Codex contract with canonical-config authority and behaviorally equivalent native projections. |

All other hook byte divergences are newline-only and must reproduce the clean
source semantics under the declared LF policy. Managed-template hook names,
`.claude/session` runtime-state routes, and the session-start runtime cache path
remain intentional only when the policy cites the active consumer and test.

For the substantive registry pair, the plan must start from the clean old
`config/agent-control/harness-capability-registry.toml`, apply every applicable
CSV path transform including all 48 hook references and all seven
`activity_envelope_manifest_source` fields, and write valid Unicode. The current
mojibake destination is rejected as a source of content authority.

#### 5.1 Rule authority and load policy

The 38 rule rows use these classes: `CA` registered canonical authority, `AA`
maintained active authority/procedure, `PX` compatibility/provenance/navigation
projection, `MC` machine-consumed compatibility, `DEP` deprecated, and `TPL`
reusable template. Canonical content lives at the renamed
`config/agent-control/gtkb-*` path. Old `.claude/rules/<name>` files remain
retained, one-way generated projections when compatibility requires content;
they are never independently edited or treated as authority.

| Old `.claude/rules` filename | Class | Post-cutover load/lifecycle policy |
| --- | --- | --- |
| `acting-prime-builder.md` | PX | Explicit-query legacy role/provenance projection. |
| `active-workspace.md` | MC | New file is canonical; migrate the direct runtime reader, retain old generated machine projection. |
| `auto-finalization-sweep.md` | AA | Activity-only: ops/build. |
| `backlog-approval-state.md` | AA | Activity-only: project/build. |
| `bridge-essential.md` | AA | Global compact bridge guardrail. |
| `bridge-permanent-operations-runbook.md` | DEP | Never startup-load; preserve deprecated history. |
| `bridge-poller-canonical.md` | DEP/TPL | Never startup-load; preserve retired template/history. |
| `canonical-terminology.md` | CA | Global core primer; activity-specific remainder. |
| `canonical-terminology.toml` | CA/MC | Machine-only canonical registry; migrate doctor/startup readers. |
| `codex-dead-ends-and-false-positives.md` | PX | Explicit-query review history. |
| `codex-decision-ledger.md` | PX | Explicit-query decision history. |
| `codex-knowledge-base-index.md` | PX | Explicit-query navigation. |
| `codex-loyal-opposition-runbook.md` | AA | Activity-only: test/LO review; explicitly excluded from Prime Builder build. |
| `codex-review-checklists.md` | AA | Activity-only: test. |
| `codex-review-gate.md` | AA | Prime Builder/global implementation guardrail. |
| `codex-review-operating-contract.md` | AA | Activity-only: test/LO review; explicitly excluded from Prime Builder build. |
| `codex-session-bootstrap.md` | PX | Global restart-guide projection of startup index. |
| `codex-standing-priorities.md` | AA | Activity-only: project. |
| `codex-way-of-working.md` | AA | Activity-only: deliberation. |
| `deliberation-protocol.md` | AA | Keep global until a separately reviewed startup-load optimization; no silent deferral. |
| `dispatcher-daemon-substrate-rollback-runbook.md` | AA | Explicit-query ops incident runbook. |
| `file-bridge-protocol.md` | CA | Global baseline. |
| `governance-emergency-bootstrap-protocol.md` | AA | Global compact emergency guardrail. |
| `groundtruth-kb-vision.md` | AA | Activity-only: project. |
| `gtkb-capability-import-policy.md` | AA | Activity-only: build/spec dependency import. |
| `loyal-opposition.md` | AA | Loyal Opposition role overlay. |
| `operating-model.md` | CA | Explicit-query project/requirement interpretation. |
| `operating-role.md` | PX | Compact role pointer; full text explicit-query. |
| `peer-solution-advisory-loop.md` | AA | Activity-only: deliberation. |
| `prime-bridge-collaboration-protocol.md` | PX | Explicit-query historical/compatibility semantics. |
| `prime-builder.md` | PX | Explicit-query compatibility behavior text; `prime-builder-role.md` wins conflicts. |
| `prime-builder-role.md` | AA | Authoritative Prime Builder role overlay. |
| `project-root-boundary.md` | AA | Global compact guardrail. |
| `report-depth.md` | AA | Activity-only: test/build-review. |
| `report-depth-prime-builder-context.md` | PX/MC | Retained compatibility pointer for tests/skill metadata; never authority. |
| `sot-read-discipline.md` | AA | Machine-enforced; full rationale explicit-query. |
| `template-code-review.md` | TPL | Activity-only: test. |
| `template-decision-memo.md` | TPL | Activity-only: test; add the missing machine-manifest entry. |

Stage A validates this table against the SoT registry, startup control map,
activity-envelope manifest, and direct readers. The child plan must explicitly
repair the malformed `deferred_surfaces` entry in the canonical destination
`config/agent-control/gtkb-activity-envelope-sharding.toml`, remove the Loyal
Opposition runbook and review operating contract from the Prime Builder build
envelope, add the missing `template-decision-memo.md` manifest row, and migrate
direct readers such as
`active_workspace.py` and doctor/startup terminology loading, and record every
relative link or embedded manifest filename that must be rewritten beside the
renamed canonical files. A policy-table contradiction fails planning and
requires a revised child proposal; the implementation worker may not choose a
different authority or load policy ad hoc.

The retained old `config/agent-control/activity-envelope-sharding.toml` is one
of the 19 inert agent-control safety copies. It remains present and unmodified;
all loaders, registries, and tests must select the corrected canonical
`gtkb-*` destination.

No deletion, cleanup, or retirement of an obsolete file is in scope.
No delete, move, rename, unlink, or source-truncation operation is permitted for
any of the 90 old paths. For each of the 52 retained inert hook/agent-control
sources, verify records every loader, registry, glob, import, wrapper, template,
and generator search route and proves none can select the old path. For each of
the 38 native rule projections, verify proves the declared row policy and
one-way canonical hash relationship. A later removal requires a separate owner
decision, proposal, independent GO, claim, packet, repeated closure evidence,
and rollback plan.

### 6. Generator-first repair

The policy declares canonical generator/registry relationships. When a residual
occurs in generated output, apply must change the canonical source or registry,
run the declared generator, and verify the output. Direct edits to generated
files are forbidden unless the policy proves there is no generator and the
proposal explicitly lists the file as authoritative.

At minimum inspect and correctly disposition managed-artifact templates, SoT
registries, context-manifest projections, harness capability registries, Codex
hook wrappers/configuration, skill adapters, and all supported harness
projections under `.agent`, `.cursor`, `.codex`, and `.goose`.

Stage A creates `scripts/generate_rule_compatibility_projections.py` with
`--check` and tests. It consumes the 38-row policy ledger, transforms links and
embedded manifest filenames for each renamed canonical location, preserves
deprecated/template lifecycle classifications, enforces EOL policy, detects
orphan projections, and proves a second generation is a no-op.

Stage A also creates a side-effect-free
`scripts/generate_cursor_skill_adapters.py --check` path and tests. Migration
must never invoke `scripts/_bootstrap_cursor_harness.py`: that bootstrap changes
role and harness state before copying skills and is not a safe projection
generator.

The policy must name and check the repository generators, including:

```text
python scripts/generate_codex_skill_adapters.py --check
python scripts/generate_antigravity_skill_adapters.py --check
python scripts/generate_api_skill_adapters.py --check
python scripts/generate_api_skill_adapters.py --output-dir .goose/skills --check
python scripts/generate_goose_manifest.py --check
python scripts/generate_cursor_skill_adapters.py --check
python scripts/generate_rule_compatibility_projections.py --check
python scripts/check_harness_parity.py
```

If an exact command differs in the live generator CLI, Stage A must record the
discovered canonical command and update the child plan; it may not silently omit
the surface.

The current database harness reference is corrected only by adding a governed
`gt harness set-capabilities-ref` command (or equivalently named public service
operation) with transactional tests. It must append/supersede the current
harness version through domain APIs, preserve historical versions, and
regenerate the authoritative harness-state projection. Raw SQL and direct JSON
editing are forbidden.

Stage A must first establish and record the authority/source contract for the
root and nested tracked harness-registry projections. The current files disagree
on unrelated D and G records, and the existing projection writer emits only one
file for its supplied project root. The child plan may not copy one projection
over the other. Acceptance requires one appended H version to update
`current_harnesses`, preserve H versions 1 through 59 and all unrelated D/G
state, and regenerate each projection only from its declared authoritative
source.

### 7. Immutable plan, atomic writes, and bounded rollback

The runtime plan and reports live under
`.gtkb-state/file-reference-migration/wi5640/` and are non-authoritative runtime
evidence until summarized in the implementation report. The plan uses a stable
schema, sorted operations, SHA-256 hashes, and LF-normalized JSON serialization.

Hash roles are distinct and test-enforced:

- `full_observation_hash` may include volatile runtime diagnostics and is never
  compared across runs.
- `closure_inventory_hash` excludes volatile scanner-output payload bytes and
  substitutes one fixed classification record for every excluded root,
  including the scanner's own output directory. Each verify pass computes this
  hash before and after scanning and fails if the inventory changed mid-pass.
- `closure_fingerprint` is the cross-run value. It contains only schema version,
  CSV hash, policy hash, scanner hash, closure-inventory hash, classification
  hash, residual hash, exception hash, projection hash, proposed-write hash, and
  Git-index hash. Timestamps, run IDs, durations, report paths, process IDs, and
  observation-file bytes are excluded.

Two clean-process verification passes must produce the same
`closure_fingerprint`; a third pass is required after the complete test and
generator suite. Zero residuals without a stable fingerprint is not closure.

Apply uses same-directory temporary files plus atomic replace where supported.
Before each write it verifies the expected preimage hash. On failure it stops,
restores only already-written files from plan-recorded preimages, and emits a
partial-transaction report. It never invokes `git reset`, `git checkout`,
`git clean`, broad `git add`, stash operations, or deletion of retained sources.
The live Git index byte hash and staged-path set must be unchanged by the tool.

### 8. Independent verification

`verify` does not trust apply's replacement log. It re-parses the CSV and policy,
re-enumerates the root, re-queries structured data, re-hashes projections, and
recomputes residuals from scratch. Each residual record includes mapping ID,
variant, classification, file and line/column or database cell, load-bearing
status, exception ID, and evidence.

Run verify twice in separate processes after apply, then a third time after all
generators and tests. All passes must produce the identical stable closure
fingerprint, zero unexplained live residuals, zero unreadable/unclassified
paths, and no proposed writes.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "CSV manifest plus owner decisions and fresh incident-disposition GO",
  "canonical_authority": "config/hooks and config/agent-control gtkb-prefixed destinations",
  "primary_route": "Stage A deterministic preflight/plan plus separately GO-approved exact-plan Stage B apply/verify",
  "before_behavior": "mixed old/new authority, live obsolete references, manual partial repairs",
  "after_behavior": "canonical consumers use new paths; obsolete files remain as classified safety copies",
  "self_descriptive_naming": "gtkb_file_reference_migration and wi5640 policy identify purpose and scope",
  "obsolete_guidance_disposition": "live obsolete guidance is replaced; audit history is retained and excluded",
  "history_preservation": "both prior bridge chains, Git history, stash evidence, and obsolete files are preserved",
  "baseline": "90 mappings; 24 newline-only divergences; one substantive registry divergence; focused suite 203/209; residual closure unproven",
  "expected_result": "three stable-fingerprint zero-live-residual verification passes with all paths classified and old sources retained",
  "rollback": "plan-scoped preimage restoration only; no broad Git or deletion action",
  "hard_invariants": ["no apply under the main v3 GO", "no obsolete-file deletion", "no audit-history mutation", "no raw DB mutation", "no Git index mutation"],
  "fail_closed_conditions": ["unreadable or unclassified path", "ambiguous residual", "preimage drift", "generator drift", "inventory mismatch", "test failure"],
  "essential_context_preservation": "native Claude rules remain deterministic compatibility projections while canonical control moves to config"
}
```

## Cross-Harness Disposition

No parity waiver is requested. The migration applies the same canonical-path
contract to every supported harness and must preserve each harness's native
delivery mechanism:

| Harness surface | Disposition |
| --- | --- |
| Claude (`.claude/hooks`, `.claude/rules`, `.claude/settings.json`, `.claude/skills`) | Behavioral parity required. Canonical hook paths move to `config/hooks`; `.claude/rules` remains a deterministic native compatibility projection of `config/agent-control`; managed skills and settings must resolve only canonical live targets. |
| Codex (`.codex/gtkb-hooks`, `.codex/hooks.json`, `.codex/config.toml`, `.codex/skills`) | Behavioral parity required. Wrapper/config references must resolve canonical hook and control paths; generated skill adapters must be regenerated from canonical sources and pass parity checks. |
| Cursor (`.cursor`) | Behavioral parity required. Cursor projections and references must resolve the same canonical control artifacts, with generator-first repair where the surface is generated. |
| Antigravity (`.agent`) | Behavioral parity required. Antigravity projections and references must resolve the same canonical control artifacts, with generator-first repair where the surface is generated. |
| Goose (`.goose`) | Behavioral parity required. Goose projections and references must resolve the same canonical control artifacts and pass the applicable manifest/parity checks. |
| Ollama, OpenRouter, and Alibaba Cloud Studio shared/configured surfaces | Behavioral parity required. Their registry, manifest, prompt, and shared managed-artifact references discovered by the deterministic scan must resolve canonical paths and pass their applicable generator/parity checks. |

The implementation report must give a per-harness disposition and executed
evidence. Any harness that cannot be brought to parity is a blocking result;
the Prime Builder may not invent or infer a waiver during implementation.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - all supported harness projections and
  fallback paths must resolve equivalent canonical control surfaces.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - migration evidence must cover every
  governed harness delivery mechanism.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity assertions and generated
  adapters must be regenerated and tested rather than manually patched.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook wrappers and configuration
  must resolve the canonical hooks without weakening fallback enforcement.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - GT-KB must remain functional;
  retained safety copies and repeated verification prevent premature breakage.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this fresh chain, independent GO, exact
  claim, packet, report, and VERIFIED are mandatory.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the active PAUTH,
  project, WI-5640, and target boundary are declared above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links
  every relevant governing specification before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - final verification must
  derive from these requirements and include current executed evidence.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - claim and packet
  checks must use an already-authorized classifier and the exact v3 chain.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - proposal, plan, report, and verdict
  retain real harness/session/model attribution.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-question and approval surfaces moved by
  the manifest must remain load-bearing and discoverable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - traversal remains in-root and
  application-boundary hits fail closed instead of mutating Agent Red.
- `GOV-WORK-TREE-HYGIENE-001` - unrelated dirty work and the Git index are
  preserved; rollback is file-scoped and auditable.
- `GOV-STANDING-BACKLOG-001` - newly discovered out-of-scope defects are
  recorded rather than silently absorbed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - decisions, exceptions, plans, tests,
  reports, and later deletion remain durable lifecycle artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - manifest, plan, source changes,
  verification, and owner decisions retain traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - retained, migrated, blocked,
  verified, and deletion-candidate states remain explicit.

## Specification-Derived Verification Plan

| Requirement | Executed verification required in implementation report |
| --- | --- |
| Manifest integrity | Run `preflight`; prove 90 rows, 33/38/19 categories, no duplicate/no-op/out-of-root/directory rows, all sources/destinations classified, and stable manifest hash. |
| Full-root classification | Prove every discovered path belongs to exactly one policy class; report counts/bytes/hashes; fail on unreadable, multiply classified, or unclassified paths. |
| Reference closure | Run independent `verify` twice in separate processes and a third time after generators/tests; require the same closure fingerprint and zero unexplained live residuals across direct, segmented, glob, regex, relative, escaped, generated, and SQLite forms. |
| Content reconciliation | Report all 90 source/destination/transformed hashes; prove 24 newline-only divergences and the clean-source registry reconstruction; include the seven hook adaptations and every plan disposition; no blind overwrite. |
| Compatibility retention | Prove all 90 old paths remain; prove 52 hook/agent-control sources are not live dependencies; prove each of the 38 rule paths satisfies its row-specific lifecycle/load/projection policy. |
| Generator integrity | Run every policy-declared generator and its `--check` or parity test, including Codex, Antigravity, API, Goose adapters/manifest, side-effect-free Cursor, rule compatibility, and harness parity; prove generated files were not hand-edited and Cursor bootstrap was not invoked. |
| Migration engine | Run `python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py -q --tb=short`. Cover preflight, plan determinism, direct/segmented/family/glob/regex variants, encodings, literal Windows names, excluded-child observations, all worktree states, unreadable directories, SQLite, ambiguity, atomic failure, rollback, and idempotency. |
| Cross-harness behavior | Run `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_canonical_init_keyword_syntax.py -q --tb=short`; require 209/209 PASS. |
| Governance behavior | Run `python -m pytest groundtruth-kb/tests/test_governance_mutation.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_authorization_gfr_slice_a.py platform_tests/scripts/test_implementation_authorization_harness_selector.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_project_authorization.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short`; require PASS. |
| Worktree nonimpairment | Hash the Git index and enumerate staged/unstaged/untracked paths before and after; require unchanged index bytes/staged set except ordinary worktree modifications explicitly in the plan. |
| Root/application boundary | Prove traversal never follows reparse points or paths outside `E:\GT-KB`; report any `applications/` residual without mutating it. |
| No deletion | Compare all 90 source paths before/after and require every source still present; no cleanup command may run. |

## Acceptance Criteria

1. A single deterministic engine and policy implement all five modes with
   focused tests; `preflight-validation.ps1`, `temp_path_fixer.py`, ad hoc
   search/replace, and agent-authored recursive edits are not execution paths.
2. The immutable plan completely classifies the root and records all exclusions,
   structured data, mappings, variants, generators, hashes, and proposed writes.
3. The main v3 GO can authorize only Stage A engine/policy/test construction and
   read-only plan generation. Apply is impossible until the separate exact-plan
   child thread has independent GO, claim, packet, and matching plan hash.
4. Every one of the 25 divergent pairs receives a reproducible transform proof
   or explicit reviewed authority decision before apply.
5. Apply changes only plan-listed paths, preserves encoding/newlines/attributes
   and unrelated bytes, and leaves the Git index/staged set unchanged.
6. All live consumers resolve canonical destinations. Historical bridge text,
   runtime state, inert retained sources, and declared native compatibility
   projections are separately classified and never disguised as live closure.
7. Three independent verify passes produce identical closure fingerprints, no pending writes,
   zero unexplained live residuals, and zero unreadable/unclassified paths.
8. All 90 old paths remain present. No deletion, cleanup, stash
   drop, broad reset, push, release, deployment, or credential work occurs.
   Stage A and Stage B perform no commit under the active PAUTH; only later
   separately authorized one-slug atomic finalization may commit.
9. Migration-specific, cross-harness, generator, governance, and authorization
   tests pass with current observed commands and results in the report.
10. The implementation report includes exact commands, plan/inventory hashes,
   classification counts, exclusion ledger, 90-row reconciliation table,
   residual/exception ledger, generator evidence, test results, Git-index
   evidence, rollback evidence, and worker-quality observations.
11. After separate owner/PAUTH authorization, an unrelated Codex LO session must
    independently rerun verification and invoke the existing one-slug atomic
    finalizer first for main Stage A and then for child Stage B. Until then no
    VERIFIED or commit is permitted.

## Stage Termination And Finalization

The expected strict lifecycle branches are:

```text
main proposal: NEW -> NO-GO -> REVISED -> GO
main report:   GO -> NEW -> VERIFIED
               GO -> NEW -> NO-GO -> REVISED -> VERIFIED
child review:  NEW -> GO
               NEW -> NO-GO -> REVISED -> GO
child report:  GO -> NEW -> VERIFIED
               GO -> NEW -> NO-GO -> REVISED -> VERIFIED
```

`NO-ACTION` is not an implementation-report status and is forbidden in this
program. Prime Builder files the main v3 `NEW` Stage A verification-request
report and releases the Stage A claim before child review or claim acquisition.
After an authorized apply and complete verification, Prime Builder files the
child `NEW` verification-request report and releases the child claim. At that
point neither thread has a live implementation `GO`, even if finalization must
wait.

The active PAUTH expressly forbids commit, while the bridge protocol requires
each implementation, report, and VERIFIED verdict to enter one local atomic
commit. Therefore Loyal Opposition must not file VERIFIED on either thread until
a separate owner decision and applicable PAUTH authorize those specific local
finalizations. The existing helper finalizes one slug per transaction. Once
authorized, one unrelated LO session independently reruns the required evidence
and invokes that helper twice in order: first main-v3 Stage A files/report/verdict
in one local commit, then child Stage B files/report/verdict in a second local
commit. Each transaction must stage only its proposal-declared exact paths plus
its report and verdict, leaving unrelated and other-stage changes untouched. If
authorization is absent, both threads remain at `NEW` verification-request
reports; no VERIFIED token or commit may be fabricated.

## Files Expected To Change

Stage A may change only:

- `scripts/gtkb_file_reference_migration.py`
- `scripts/generate_rule_compatibility_projections.py`
- `scripts/generate_cursor_skill_adapters.py`
- `config/file-reference-migration/wi5640.toml`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`
- `platform_tests/scripts/test_generate_rule_compatibility_projections.py`
- `platform_tests/scripts/test_generate_cursor_skill_adapters.py`
- `platform_tests/fixtures/file_reference_migration/**`

Stage A may write runtime reports only beneath
`.gtkb-state/file-reference-migration/wi5640/**`. It may not modify a migrated
consumer, source/destination pair, projection, registry, database, or harness
state.

Stage B may change only the exact write paths listed in the independently
GO-approved child plan. Expected classes include plan-listed reference
consumers, canonical registries/templates and generated projections, the tested
public harness capabilities-reference command, current database state through
that API, its two generated registry projections, and `.gitattributes` for the
scoped `config/hooks/** text eol=lf` rule. The child proposal must enumerate
each exact path rather than relying on these class names.

- No file under `bridge/` except future append-only artifacts in this v3 thread
  and the separately reviewed exact-plan child thread.
- No obsolete source file is deleted.

## Pre-Filing Preflight

The following checks were executed against this exact non-dispatchable draft:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v3 --content-file .gtkb-state/bridge-propose-drafts/gtkb-file-move-rename-canonicalization-v3-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v3 --content-file .gtkb-state/bridge-propose-drafts/gtkb-file-move-rename-canonicalization-v3-001.md
python scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-file-move-rename-canonicalization-v3-001.md --strict --json
```

Observed results:

- Applicability: exit 0, `preflight_passed: true`, no missing required or
  advisory specs, no blocking errors, and no unclassified target paths.
- Clause gate: exit 0; five clauses evaluated, four `must_apply`, one
  `may_apply`, zero must-apply evidence gaps, and zero blocking gaps.
- Target coverage: exit 1, verdict `gaps`, with three generator, one integration,
  and eleven prose paths intentionally absent from main-v3 `target_paths`.
  Every uncovered path is a read-only evidence path, old path, or prospective
  Stage B write. Adding them to this header would recreate the over-broad GO
  defect. The current checker has no observation-only path class. The child
  exact-plan proposal must include every actual write and achieve strict
  `verdict: clean`; main-v3 Stage A remains mechanically incapable of apply.
- The applicability preflight reports expected future-parent warnings for the
  runtime report directory, policy path, and fixture directory. They must not be
  created before GO; Stage A creates them only after claim and packet
  authorization.
- Draft author-metadata warnings are expected on the non-dispatchable draft.
  The governed Codex writer inserts live author/session/model metadata before
  its in-memory compliance audit.
- `gt projects show-authorization` independently confirms the cited PAUTH is
  active, has no per-work-item inclusion restriction, covers source, test,
  configuration, documentation, metadata, runtime-state, governance-evidence,
  and bridge mutation classes, and forbids destructive cleanup, commit, push,
  release, deployment, dispatcher mutation, credential work, external-system
  mutation, and history rewrite.
- `gt projects show` confirms WI-5640 is an active project member.
- A filtered live dispatch report returns `matches: 0` for the three withdrawn
  stale-GO threads across both roles and all actionable/blocked/candidate queues.
  Their three claim-status queries each return null. The valid skill-rollout
  chain independently resolves to latest strict `WITHDRAWN`.

No implementation claim or authorization packet was requested or created.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the active Harness Parity project PAUTH while
  preserving independent review, exact claim, packet, nonimpairment, and no
  commit/destructive-cleanup boundaries.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` requires temporary retention
  of obsolete sources, repeated deterministic scans and functional checks, and
  a later separately authorized deletion phase.
- The owner directed that all `E:\GT-KB` files be deterministically inventoried
  and that every live obsolete reference be corrected except immutable audit
  trails such as `bridge/`; manual recursive find/replace is prohibited.
- The owner assigned all Prime Builder work for this program to Codex A and will
  use independent Codex interactive sessions for formal LO review.

## Prior Deliberations And Bridge Evidence

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - controlling retention and
  deletion-phase decision.
- `DELIB-202666274` - active project authorization owner decision.
- `DELIB-202667106` - prior Loyal Opposition review of the canonical skill
  renaming rollout.
- `bridge/gtkb-wi5648-file-move-false-verification-incident-001.md` and `-002.md`
  - independent incident/quarantine proposal and non-implementation GO.
- `bridge/gtkb-file-move-rename-canonicalization-001.md` through `-007.md` -
  preserved structurally invalid original chain; evidence only.
- `bridge/gtkb-file-move-rename-canonicalization-v2-001.md` through `-006.md` -
  preserved replacement chain with unsupported VERIFIED; evidence only.

No prior decision authorizes deletion, blind recopying, raw database mutation,
or reliance on either historical chain for implementation.

## Risks / Rollback

- **Incomplete enumeration:** fail on unreadable/unclassified paths and record
  every exclusion with inventory evidence.
- **Performance collapse:** single-pass streaming and indexed patterns replace
  nested mapping-by-file scans; large structured data uses native read APIs.
- **Corrupt encoding or unrelated bytes:** preimage hashes, explicit decoding,
  byte-preserving reconstruction, and atomic writes fail closed.
- **Divergent pair data loss:** no blind copy; transform proof or reviewed
  per-row authority is mandatory.
- **Generated drift recreation:** canonical registry/template changes precede
  generator execution and independent output scans.
- **Premature breakage:** obsolete sources remain until a later lifecycle after
  repeated verification.
- **Mixed-worktree damage:** no index mutation or broad Git/stash operation;
  rollback restores only plan-recorded preimages.
- **False zero-residual claim:** verify is independent of apply and must pass
  three times with an identical stable closure fingerprint and zero unexplained
  live residuals.
- **Over-broad GO reuse:** the main v3 GO is Stage A only; the engine fails
  closed on apply without an exact-plan child GO, claim, packet, and plan hash.

Rollback restores only files written by the immutable plan to their exact
preimage bytes and attributes, leaves every obsolete source in place, and emits
an auditable partial-transaction report. It does not delete evidence or invoke
broad repository operations.

## Explicit Non-Authority

This REVISED proposal does not itself authorize implementation. Prime Builder
must wait for an independent LO GO on this exact v3 revision, then acquire a
matching Stage A claim and implementation-start packet. Even after that GO, the
proposal authorizes no migration apply. Apply requires the separate exact-plan
child GO, child claim, child implementation-start packet, and matching plan
hash described above. Neither stage authorizes commit, staging, push, release,
deployment, credentials, deletion, dispatcher/TAFE mutation, raw database
mutation, or any action against preserved historical file-move chains.

## Recommended Commit Type

`feat(migration):`

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
