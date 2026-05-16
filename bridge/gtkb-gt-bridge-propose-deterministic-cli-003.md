REVISED

# Implementation Proposal - `gt bridge propose` Deterministic CLI (WI-3318)

bridge_kind: implementation_proposal
Document: gtkb-gt-bridge-propose-deterministic-cli
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3318

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/", "groundtruth-kb/tests/test_cli_bridge_propose.py", ".claude/skills/bridge-propose/SKILL.md"]

This REVISED proposal implements `WI-3318`: a deterministic `gt bridge propose --kind <type>` CLI that produces most of a bridge proposal scaffold from MemBase + bridge state + templates, leaving AI to fill only judgment-required sections.

## Revision Notes

This `-003` REVISED addresses every finding in the `-002` NO-GO:

- **F1 (P1) — target_paths did not authorize the CLI-exposure files.** Resolved. `target_paths` now explicitly includes `groundtruth-kb/src/groundtruth_kb/cli.py` (the command registry where the new `bridge` group is registered, per the existing `@main.group()` pattern) and `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py` (the IP-3 helper module). A new verification case (`test_cli_bridge_propose_help_resolves`) invokes the real `gt` console-entrypoint path and proves `gt bridge propose --help` resolves. See updated `target_paths` line and IP-2 / Spec-Derived Verification Plan below.
- **F2 (P1) — the template/search plan relied on optional dependencies absent from the base CLI.** Resolved. The proposal now commits to **dependency strategy 1**: stdlib-only template rendering (Python `string.Template`, no Jinja2) and the existing `KnowledgeDB.search_deliberations` API for prior-deliberation lookup (no direct `chromadb` import in the CLI path). The base package dependency set (`click>=8.1`) is unchanged; `groundtruth-kb/pyproject.toml` is therefore NOT in `target_paths`. A base-install import-boundary test (`test_cli_bridge_propose_no_optional_deps`) proves the command imports and runs `--help` / `--dry-run` without the `web` or `search` extras. See IP-1, IP-3, and the Dependency Strategy section.
- **F3 (P1) — the proposed write path bypassed the helper-mediated safety path.** Resolved. The CLI no longer writes to `bridge/<slug>-001.md`. It writes a non-dispatchable draft to `.gtkb-state/bridge-propose-drafts/<slug>-001.md` and prints an explicit filing handoff instructing the author to fill the AI-judgment placeholders and then file via the existing helper-mediated path (`.claude/skills/bridge-propose/helpers/write_bridge.py`), which performs the credential scan, no-force / no-overwrite, and atomic INDEX insertion. The draft location, its non-dispatchable lifecycle, and cleanup semantics are defined in IP-2 and the Draft Lifecycle section. This preserves the bridge authority and safety invariants flagged by `DELIB-1842`.
- **F4 (P2) — advisory preflight omissions.** Resolved. `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` are now cited in `## Specification Links`. Both preflights were re-run on this `-003` content; results are embedded in `## Applicability Preflight` and `## Clause Applicability`.

No scope expansion beyond what the findings required: the CLI's purpose, the six proposal kinds, and the auto-population helpers are unchanged from `-001`.

## Claim

Build `gt bridge propose --kind <implementation|defect-fix|scoping|advisory-disposition|retirement|umbrella> --wi <WI-ID> --slug <slug> [--target-path ...] [--add-spec ...] [--dry-run]`. Output: a templated **draft** proposal file at `.gtkb-state/bridge-propose-drafts/<slug>-001.md` with auto-populated sections (the deterministic majority of the standard sections) and placeholders for the sections requiring AI judgment. The author fills the placeholders, then files the proposal into `bridge/` via the existing helper-mediated path.

## In-Root Placement Evidence

All `target_paths` and the draft output directory (`.gtkb-state/bridge-propose-drafts/`) are inside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the CLI preserves bridge invariants and routes final writes through the helper-mediated path so `bridge/INDEX.md` remains canonical.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented / deterministic-services framing baseline.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - templates auto-populate the `Specification Links` section to keep generated proposals compliant.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - templates emit a spec-to-test mapping skeleton; this proposal's own spec-to-test mapping is in the Verification Plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - templates auto-populate `Project Authorization` / `Project` / `Work Item` metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - the CLI is a deterministic surface in the artifact-production toolchain.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only; templates auto-emit In-Root Placement Evidence and the draft directory is in-root.
- `GOV-STANDING-BACKLOG-001` - WI-3318 is tracked as a member of an authorized project.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the CLI is a Prime-side surface; it does not change Codex hook parity, and the draft model keeps bridge writes on the existing parity-symmetric helper path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, templates, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the deterministic CLI lowers the cost of the proposal-creation lifecycle step.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (cross-cutting) - this proposal cites all relevant specs and maps every linked spec to a test.

## Prior Deliberations

- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - batch-7 owner authorization; records the owner directive to build `gt bridge propose --kind <type>` as the deterministic-services pivot and authorizes WI-3318.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - foundational principle ("repetitive work performed by AI is a defect"); explicitly lists bridge proposal scaffolding as a service candidate.
- `DELIB-1552` - VERIFIED prior DA read-surface / template pre-population work; relevant to the auto-populated Prior Deliberations behavior.
- `DELIB-1842` - prior bridge-helper NO-GO establishing that bridge-helper improvements must preserve role authority, file-existence checks, and safe INDEX behavior rather than introducing a governance-bypass mutation surface. This `-003` revision's draft-to-`.gtkb-state` model + helper-mediated filing handoff is the direct response to that precedent.

No prior deliberation rejected a deterministic proposal-scaffold CLI; this is the first such proposal, and `-003` is its first compliant revision.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by the following AskUserQuestion decision:

- 2026-05-15 UTC, S350+: owner AUQ "How should we operationalize the deterministic-services preference for artifact production?" answered "Reframe session: stop LLM-bridge-proposals, build gt-bridge-propose-template CLI" (Option C). Recorded as `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI`.

WI-3318 is an active member of `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` (membership record `PWM-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3318`), covered by the active authorization cited in the metadata block above.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` and the operative observation it cites (a deterministic script reproduces in ~2s what an LLM-exploration pass takes minutes to produce) specify the determinism target. No new or revised requirement or specification is created by this work.

## Dependency Strategy (resolves F2)

The base `gt` CLI must not gain new runtime dependencies. The CLI therefore uses **strategy 1**:

- **Template rendering:** Python standard-library `string.Template` substitution. Templates are plain `.md` files with `${placeholder}` tokens. No Jinja2; `jinja2` stays in the `web` extra and `groundtruth-kb/pyproject.toml` is unchanged and NOT a target path.
- **Prior-deliberation lookup:** `auto_prior_delibs` calls `KnowledgeDB.search_deliberations(...)`, the existing API. That API already encapsulates the ChromaDB-vs-fallback decision internally; the CLI path does not import `chromadb`. When the optional `search` extra is absent, `search_deliberations` returns its defined fallback result and the CLI emits whatever candidate list it returns (possibly empty) — never a `ModuleNotFoundError`.
- **Verification:** `test_cli_bridge_propose_no_optional_deps` imports the CLI module and exercises `--help` and `--dry-run` with the optional extras absent (import-boundary assertion: no top-level `import jinja2` / `import chromadb` in `cli_bridge_propose.py` or `proposal_autoload.py`).

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (WI-3318). It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe WI-3318 and its governed filing path only. The review-packet inventory is one bridge thread covering IP-1 (templates) + IP-2 (CLI) + IP-3 (auto-population) + IP-4 (skill update) + IP-5 (tests); WI-3318's project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-15-batch7-gt-bridge-propose-cli.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is inserted under the existing `Document: gtkb-gt-bridge-propose-deterministic-cli` entry; no INDEX entry is removed or rewritten. The CLI being proposed deliberately does NOT write to `bridge/INDEX.md` itself — it produces a non-dispatchable draft and hands filing (including the INDEX insertion) to the existing helper-mediated path, so INDEX authority is unchanged.

## Proposed Scope

### IP-1: Proposal templates per kind

`groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/`, plain-text `.md` files using stdlib `${...}` tokens:
- `implementation.md` (largest; code-change WIs)
- `defect-fix.md` (defect class)
- `scoping.md` (umbrella WI scoping; short scope)
- `advisory-disposition.md` (route an LO advisory; pre-fills the disposition field)
- `retirement.md` (mark a WI retired / wont_fix; shortest)
- `umbrella.md` (multi-WI umbrella covering multiple atomic dispositions)

Each template includes deterministic placeholders: `${slug}`, `${wi_id}`, `${wi_title}`, `${project_authorization_id}`, `${project_id}`, `${date}`, `${target_paths_json}`, `${auto_spec_links}`, `${auto_prior_delibs}`, `${auto_owner_decisions}`, `${kind_specific_intro}`, `${recommended_commit_type}`. AI-judgment placeholders (left literal in the draft for the author to replace): `${claim}`, `${proposed_scope_ip_blocks}`, `${verification_plan_table}`, `${acceptance_criteria}`, `${risks_rollback}`.

### IP-2: CLI entrypoint

`groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` defines a `bridge` Click group and a `propose` command. The group is registered in `groundtruth-kb/src/groundtruth_kb/cli.py` following the existing `@main.group()` pattern (e.g. `main.add_command(bridge_group)` or an equivalent registration consistent with the `backlog` / `projects` groups). Sketch:

```python
@click.group("bridge")
def bridge_group() -> None:
    """Bridge protocol helper commands."""

@bridge_group.command("propose")
@click.option("--kind", required=True, type=click.Choice([
    "implementation", "defect-fix", "scoping", "advisory-disposition",
    "retirement", "umbrella",
]))
@click.option("--wi", required=True, help="WI-NNNN identifier (must exist in MemBase)")
@click.option("--slug", required=True, help="Bridge slug (lowercase-hyphenated)")
@click.option("--target-path", multiple=True, help="Repeatable target path")
@click.option("--add-spec", multiple=True, help="Override / augment auto-detected spec links")
@click.option("--dry-run", is_flag=True)
def bridge_propose(kind, wi, slug, target_path, add_spec, dry_run):
    """Emit a deterministic bridge proposal DRAFT (non-dispatchable)."""
    ctx = build_propose_context(kind, wi, slug, target_path, add_spec)
    rendered = render_template(kind, ctx)               # stdlib string.Template
    draft_dir = REPO_ROOT / ".gtkb-state" / "bridge-propose-drafts"
    output_path = draft_dir / f"{slug}-001.md"
    if dry_run:
        click.echo(rendered)
        return
    draft_dir.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise click.ClickException(
            f"Draft already exists: {output_path}. Refusing to overwrite; "
            f"remove it or choose a different slug.")
    output_path.write_text(rendered, encoding="utf-8")
    click.echo(f"Wrote DRAFT: {output_path}")
    click.echo(
        "This is a NON-DISPATCHABLE draft, not a filed bridge proposal. "
        "Next steps: (1) fill the AI-judgment placeholders "
        "(${claim}, ${proposed_scope_ip_blocks}, ${verification_plan_table}, "
        "${acceptance_criteria}, ${risks_rollback}); (2) file the proposal "
        "into bridge/ via the helper-mediated path "
        "(.claude/skills/bridge-propose/helpers/write_bridge.py), which runs "
        "the credential scan, refuses force/overwrite, and inserts the "
        "bridge/INDEX.md entry atomically.")
```

The CLI fails closed if `--wi` is not found in MemBase (`raise click.ClickException`). It refuses to overwrite an existing draft. It never touches `bridge/` or `bridge/INDEX.md`.

### IP-3: Auto-population helpers

In `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py` (new file, in `target_paths`):
- `auto_spec_links(wi_id, kind, target_paths) -> list[str]` queries `current_specs` filtered by `source_spec_id` linkage plus the spec-applicability TOML triggers.
- `auto_prior_delibs(wi_id, slug) -> list[str]` calls `KnowledgeDB.search_deliberations(...)` (no direct `chromadb` import; fallback-safe per the Dependency Strategy).
- `auto_owner_decisions(wi_id) -> list[str]` reads `memory/pending-owner-decisions.md` and scans for AUQ answers referencing the WI.
- `auto_target_paths_in_root_evidence(target_paths) -> str` renders the standard In-Root Placement Evidence paragraph.
- `auto_project_metadata(wi_id) -> dict` queries `current_project_work_item_memberships` + `current_project_authorizations` for the WI's active project authorization and project id.

### IP-4: Skill update

In `.claude/skills/bridge-propose/SKILL.md`, add guidance: a proposal author MAY scaffold a draft with `gt bridge propose --kind <type> --wi <id> --slug <slug>`, fill the AI-judgment placeholders in the `.gtkb-state/bridge-propose-drafts/` draft, and then file it through the existing helper-mediated path documented in the same skill. The skill's existing helper-mediated filing flow is the canonical write path and is unchanged.

### IP-5: Tests

`groundtruth-kb/tests/test_cli_bridge_propose.py` covers: each kind's template rendering; auto-population helpers; CLI argument validation; missing-WI clear error; `--dry-run` no-write; correct draft output path; overwrite refusal; real CLI registration; base-dependency import boundary; and that the CLI does not write to `bridge/` or `bridge/INDEX.md`.

## Draft Lifecycle (resolves F3)

- Drafts live at `.gtkb-state/bridge-propose-drafts/<slug>-001.md`. `.gtkb-state/` is non-dispatchable runtime state — the cross-harness event-driven trigger inspects `bridge/INDEX.md`, never `.gtkb-state/bridge-propose-drafts/`, so a draft cannot trigger Loyal Opposition review.
- A draft is never a filed proposal. It becomes a proposal only when the author fills the placeholders and files it through the helper-mediated path, which writes `bridge/<slug>-001.md` and inserts the INDEX entry.
- Credential safety: the CLI populates drafts only from MemBase metadata and template text; the canonical credential-scan happens at the helper-mediated filing step (the helper scans `CREDENTIAL_PATTERNS + BASH_EXTRAS`). The draft directory is runtime state, not committed; `test_cli_bridge_propose.py` includes a content-shape test confirming the draft body is template-derived.
- Cleanup: drafts are disposable. The author may delete a draft after filing; a stale draft is inert because nothing dispatches from `.gtkb-state/bridge-propose-drafts/`. No automatic cleanup job is introduced by this proposal.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `groundtruth-kb/tests/test_cli_bridge_propose.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `auto_spec_links` includes spec-applicability cross-cutting specs; rendered template has a populated `Specification Links` section | `test_auto_spec_links_cross_cutting`, `test_implementation_template_renders` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | rendered template emits a spec-to-test mapping skeleton placeholder | `test_template_emits_spec_to_test_skeleton` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `auto_project_metadata` returns the active authorization + project id; rendered template carries the three metadata lines | `test_auto_project_metadata_active_auth`, `test_template_emits_project_metadata` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the CLI writes only to `.gtkb-state/bridge-propose-drafts/`, never to `bridge/` or `bridge/INDEX.md` | `test_cli_does_not_touch_bridge_dir` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | draft output path and target paths are in-root | `test_cli_draft_path_in_root` |
| `GOV-STANDING-BACKLOG-001` | missing / unknown `--wi` produces a clear failure (the WI must exist in the backlog) | `test_missing_wi_clear_error` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | every proposal kind renders a complete governed-artifact scaffold | `test_implementation_template_renders`, `test_defect_fix_template_renders`, `test_scoping_template_renders`, `test_advisory_disposition_template_renders`, `test_retirement_template_renders`, `test_umbrella_template_renders` |
| `SPEC-AUQ-POLICY-ENGINE-001` | CLI argument validation; `--dry-run` prints without writing; CLI refuses to overwrite an existing draft | `test_cli_arg_validation`, `test_cli_dry_run_no_write`, `test_cli_refuses_overwrite` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | base-install behavior: CLI imports and runs `--help` / `--dry-run` without the `web` / `search` extras (no parity-breaking optional dep) | `test_cli_bridge_propose_no_optional_deps` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (CLI registration) | `gt bridge propose --help` resolves through the real console entrypoint | `test_cli_bridge_propose_help_resolves` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (prior-delib autoload) | `auto_prior_delibs` returns a candidate list (possibly empty) and never raises when the `search` extra is absent | `test_auto_prior_delibs_fallback_safe` |

Run: `python -m pytest groundtruth-kb/tests/test_cli_bridge_propose.py -v --tb=short`.

Lint: `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py groundtruth-kb/tests/test_cli_bridge_propose.py`.

## Acceptance Criteria

- IP-1..IP-5 landed; all tests in `test_cli_bridge_propose.py` PASS.
- Both bridge preflights PASS for this proposal (`-003`).
- `gt bridge propose --help` resolves through the installed console entrypoint (real-registration test PASS).
- The CLI imports and runs `--help` / `--dry-run` with neither the `web` nor `search` extra installed (import-boundary test PASS).
- The CLI writes only to `.gtkb-state/bridge-propose-drafts/`; it never writes `bridge/<slug>-NNN.md` or `bridge/INDEX.md` (test PASS).
- The CLI refuses to overwrite an existing draft (test PASS).
- Missing / unknown `--wi` fails closed with a clear error (test PASS).
- `groundtruth-kb/pyproject.toml` is unchanged (no new runtime dependency).
- `ruff check` is clean on the touched files.

## Risks / Rollback

- Risk: auto-populated `Specification Links` may miss specs the AI would catch from the WI's title/description context. Mitigation: `--add-spec` augments the list; the spec-applicability TOML is the source of truth for cross-cutting specs.
- Risk: `auto_prior_delibs` may return irrelevant matches, or an empty list when the `search` extra is absent. Mitigation: the CLI emits the matches as a candidate list, not a final list (the author prunes during fill-in); an empty list is acceptable and safe.
- Risk: template drift from current proposal conventions. Mitigation: templates derived from recent proposals; the test suite renders each kind and asserts the required sections are present.
- Rollback: remove `cli_bridge_propose.py`, `proposal_autoload.py`, the `proposal_templates/` directory, and the `bridge` group registration in `cli.py`; delete `.gtkb-state/bridge-propose-drafts/`. The existing manual / helper-mediated proposal flow is unaffected because this proposal does not modify it.

## Recommended Commit Type

`feat` - new deterministic CLI surface (`bridge` group + `propose` command), auto-population helper module, proposal templates, and tests; a new capability with no behavior change to existing surfaces.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli`

- packet_hash: `sha256:a95eb078fd10f8d40d8a2db69f2a134161dca475d8bca259dde4c0e58e6d2693`
- bridge_document_name: `gtkb-gt-bridge-propose-deterministic-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gt-bridge-propose-deterministic-cli-003.md`
- operative_file: `bridge/gtkb-gt-bridge-propose-deterministic-cli-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli`

- Bridge id: `gtkb-gt-bridge-propose-deterministic-cli`
- Operative file: `bridge\gtkb-gt-bridge-propose-deterministic-cli-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
