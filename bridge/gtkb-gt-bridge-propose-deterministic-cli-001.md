NEW

# Implementation Proposal - `gt bridge propose` Deterministic CLI (WI-3318)

bridge_kind: implementation_proposal
Document: gtkb-gt-bridge-propose-deterministic-cli
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3318

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/", "groundtruth-kb/tests/test_cli_bridge_propose.py", ".claude/skills/bridge-propose/SKILL.md"]

This NEW proposal implements `WI-3318`: a deterministic `gt bridge propose --kind <type>` CLI that produces 90% of a bridge proposal from MemBase + bridge state + templates, leaving AI to fill only judgment-required sections.

**Note on this proposal's own length**: this is the LAST intentionally-large LLM-generated bridge proposal of this session, per owner directive 2026-05-15 reframing toward deterministic services. After this CLI lands, subsequent proposals (including REVISED-1s on the ~52 pending NO-GOs) should be ~30 lines of AI-judgment content plus deterministic CLI invocation.

## Claim

Build `gt bridge propose --kind <implementation|defect-fix|scoping|advisory-disposition|retirement|umbrella> --wi <WI-ID> --slug <slug> [--target-path ...]`. Output: a templated proposal file at `bridge/<slug>-001.md` with auto-populated sections (8 of 13 standard sections) and placeholders for the 5 sections requiring AI judgment.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; CLI preserves invariants.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - deterministic-services framing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - template auto-populates Specification Links to ensure compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - template emits spec-to-test mapping skeleton.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - template auto-populates Project Authorization / Project / Work Item metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only; template auto-emits In-Root Placement Evidence.
- `GOV-STANDING-BACKLOG-001` - WI-3318 tracked.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - originating principle.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - batch-7 owner authorization (deterministic-services pivot).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - foundational principle ("repetitive work performed by AI is a defect").

## Owner Decisions / Input

- 2026-05-15 UTC, S350+: owner AUQ "How should we operationalize the deterministic-services preference for artifact production?" answered "Reframe session: stop LLM-bridge-proposals, build gt-bridge-propose-template CLI" (Option C).

## Requirement Sufficiency

Existing requirements sufficient. DELIB-S312 + the operative observation (Codex 4m10s vs script 2s) specify the determinism target.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-15-batch7-gt-bridge-propose-cli.json`. Review-packet inventory: IP-1 (templates) + IP-2 (CLI) + IP-3 (auto-population) + IP-4 (skill update) + IP-5 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Proposal templates per kind

`groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/`:
- `implementation.md.j2` (largest; covers code-change WIs)
- `defect-fix.md.j2` (defect class)
- `scoping.md.j2` (umbrella WI scoping; short scope)
- `advisory-disposition.md.j2` (route LO advisory; pre-fills disposition field)
- `retirement.md.j2` (mark WI as retired/wont_fix; shortest)
- `umbrella.md.j2` (multi-WI umbrella covering multiple atomic dispositions)

Each template includes Jinja2 placeholders for: `{slug}`, `{wi_id}`, `{wi_title}`, `{project_authorization_id}`, `{project_id}`, `{date}`, `{target_paths_json}`, `{auto_spec_links}`, `{auto_prior_delibs}`, `{auto_owner_decisions}`, `{kind_specific_intro}`, `{recommended_commit_type}`. AI-judgment placeholders: `{claim}`, `{proposed_scope_ip_blocks}`, `{verification_plan_table}`, `{acceptance_criteria}`, `{risks_rollback}`.

### IP-2: CLI entrypoint

`groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`:

```python
@bridge.command("propose")
@click.option("--kind", required=True, type=click.Choice([
    "implementation", "defect-fix", "scoping", "advisory-disposition",
    "retirement", "umbrella",
]))
@click.option("--wi", required=True, help="WI-NNNN identifier (must exist in MemBase)")
@click.option("--slug", required=True, help="Bridge slug (lowercase-hyphenated)")
@click.option("--target-path", multiple=True, help="Repeatable target path")
@click.option("--add-spec", multiple=True, help="Override auto-detected spec links")
@click.option("--dry-run", is_flag=True)
def bridge_propose(kind, wi, slug, target_path, add_spec, dry_run):
    """Emit a deterministic bridge proposal scaffold."""
    ctx = build_propose_context(kind, wi, slug, target_path, add_spec)
    rendered = render_template(kind, ctx)
    output_path = REPO_ROOT / "bridge" / f"{slug}-001.md"
    if dry_run:
        click.echo(rendered)
    else:
        output_path.write_text(rendered, encoding="utf-8")
        click.echo(f"Wrote: {output_path}")
        click.echo("Fill in the AI-judgment placeholders ({claim}, {proposed_scope_ip_blocks}, etc.) before INDEX update.")
```

### IP-3: Auto-population helpers

In `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py`:
- `auto_spec_links(wi_id, kind, target_paths) -> list[str]` queries `current_specs` filtered by source_spec_id linkage + the spec-applicability TOML triggers.
- `auto_prior_delibs(wi_id, slug) -> list[str]` semantic-searches DA via ChromaDB for relevant prior deliberations.
- `auto_owner_decisions(wi_id) -> list[str]` reads `memory/pending-owner-decisions.md` + scans recent transcripts for AUQ answers referencing the WI.
- `auto_target_paths_in_root_evidence(target_paths) -> str` renders the standard In-Root Placement Evidence paragraph.
- `auto_project_metadata(wi_id) -> dict` queries MemBase for the WI's active project authorization + project ID.

### IP-4: Skill update

In `.claude/skills/bridge-propose/SKILL.md`, replace the "compose proposal manually" guidance with "invoke `gt bridge propose --kind <type> --wi <id> --slug <slug>` then fill the 5 AI-judgment placeholders". Document the placeholder set.

### IP-5: Tests

Tests cover each kind (template rendering), auto-population helpers (spec link auto-detect, DA search, owner-decisions extraction), CLI argument validation, dry-run mode, output file path correctness.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| implementation template renders | `test_implementation_template_renders` |
| defect-fix template renders | `test_defect_fix_template_renders` |
| scoping template renders | `test_scoping_template_renders` |
| advisory-disposition template renders | `test_advisory_disposition_template_renders` |
| retirement template renders | `test_retirement_template_renders` |
| umbrella template renders | `test_umbrella_template_renders` |
| auto_spec_links includes spec-applicability cross-cutting | `test_auto_spec_links_cross_cutting` |
| auto_prior_delibs returns DA matches | `test_auto_prior_delibs_da_search` |
| auto_owner_decisions extracts from pending file | `test_auto_owner_decisions_pending` |
| auto_project_metadata returns active auth | `test_auto_project_metadata_active_auth` |
| CLI dry-run prints without writing | `test_cli_dry_run_no_write` |
| CLI writes to correct path | `test_cli_writes_correct_path` |
| Missing WI fails clearly | `test_missing_wi_clear_error` |
| Rendered output passes both preflights | `test_rendered_output_passes_preflights` |

Run: `python -m pytest groundtruth-kb/tests/test_cli_bridge_propose.py -v`.

## Acceptance Criteria

- IP-1..IP-5 landed; 14 tests PASS.
- Both preflights PASS for this proposal.
- **Self-verification**: rendered output for a representative WI passes both bridge preflights (applicability + clause).
- Token-reduction smoke test: render a proposal via CLI + spot-check that ~80% of content is auto-populated.

## Risks / Rollback

- Risk: auto-populated Specification Links may miss specs the AI would catch from the WI's title/description context. Mitigation: `--add-spec` flag allows manual augmentation; spec-applicability TOML is the source of truth for cross-cutting.
- Risk: auto_prior_delibs ChromaDB search may return irrelevant matches. Mitigation: ranking threshold; CLI emits the matches as a candidate list, not a final list (AI prunes during fill-in).
- Risk: template drift from current proposal conventions. Mitigation: templates derived from this session's 57 proposals; CI test that runs preflights on rendered output catches drift.
- Rollback: remove the cli_bridge_propose module + templates dir. Existing manual-authored proposal flow continues to work.

## Recommended Commit Type

`feat` - new deterministic CLI surface; ~400 LOC (CLI + templates + auto-loader + tests). Target outcome: ~80% token reduction per future proposal.
