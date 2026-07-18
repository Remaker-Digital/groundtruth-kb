NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Report - Redirect retired independent-progress-assessments references (config/gitignore/script batch)

bridge_kind: implementation_report
Document: gtkb-retire-ipa-refs-config-gitignore
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-retire-ipa-refs-config-gitignore-002.md
Approved proposal: bridge/gtkb-retire-ipa-refs-config-gitignore-001.md

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5492

target_paths: ["config/agent-control/CONTROL-MAP.md", "config/agent-control/REVIEW-MODE-SETUP.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/activity-disposition-profiles.toml", "config/agent-control/declarative-agent-role-manifest.yaml", "config/agent-control/system-interface-map.toml", "config/governance/lo-file-safety.toml", "config/governance/document-author-provenance.toml", "config/governance/evidence-freshness-boundaries.toml", "config/governance/hygiene-sweep-patterns.toml", "config/governance/hygiene-baseline-registry.toml", ".gitignore", "scripts/advisory_backlog_router.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Specification Links

Carried forward from the approved proposal (`bridge/gtkb-retire-ipa-refs-config-gitignore-001.md`):

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`

## Summary

Implemented all 15 target files exactly as approved. Every live reference to
the retired `independent-progress-assessments/` directory in this batch is now
either redirected to the Advisory Proposal / Deliberation Archive model,
corrected (pre-existing ALL-CAPS path-drift), narrowed (dead allow-list /
exclude-pattern / governed-surface entries removed), or annotated `(source
retired 2026-07-17)` without altering the historical content it supports.

## Authorization Evidence

- LO GO: `bridge/gtkb-retire-ipa-refs-config-gitignore-002.md`
- Work-intent claim: `python scripts/bridge_claim_cli.py claim gtkb-retire-ipa-refs-config-gitignore --session-id 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2 --ttl-seconds 5400`
- Claim result: acquired at `2026-07-18T00:43:29Z`, `claim_kind: go_implementation`
- Implementation-start command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-retire-ipa-refs-config-gitignore --session-id 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2`
- Implementation-start packet: created `2026-07-18T00:43:44Z`, expires `2026-07-18T02:43:44Z`, pre-start packet hash `sha256:feaeb5a64a05cbe9b8577c8b00debc0412d4241f32ce9d538adaccea521d4b83`, exact target-path globs matched the 15 files above

## Files Changed

1. `config/agent-control/CONTROL-MAP.md` - corrected pre-existing ALL-CAPS path-drift (9 refs -> real `.claude/rules/*.md` paths); removed the dropbox-only line with no replacement path.
2. `config/agent-control/REVIEW-MODE-SETUP.md` - identical pattern to CONTROL-MAP.md.
3. `config/agent-control/SESSION-STARTUP-INDEX.md` - simplified the now-moot "non-canonical session evidence" caveat to a plain retirement note.
4. `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` - same simplification.
5. `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` - same simplification.
6. `config/agent-control/activity-disposition-profiles.toml` - 6 refs found and fixed (1 more than the proposal's estimated 4): `[activities.deliberation]` terminology array entry, `[activities.deliberation.history_state]` source list entry, `[activities.deliberation.direction]` guardrails entry, `[activities.build]` terminology array entry, `[activities.build.history_state]` source list entry, `[activities.build.direction]` guardrails entry. Terminology/source-list entries removed outright; guardrail phrases replaced with a plain retirement note.
7. `config/agent-control/declarative-agent-role-manifest.yaml` - removed the dead `review_surfaces` list entry.
8. `config/agent-control/system-interface-map.toml` - redirected the `role_permissions` note.
9. `config/governance/lo-file-safety.toml` - removed the 3 dead `allow_patterns` entries; retained `memory/MEMORY.md`. Verified this is the exact gate that blocked a raw dropbox write earlier this session.
10. `config/governance/document-author-provenance.toml` - removed the dead `governed_surfaces` glob entry.
11. `config/governance/evidence-freshness-boundaries.toml` - annotated all 7 `evidence_path` citations (single `replace_all` edit, identical literal value) `(source retired 2026-07-17)`; removed the moot `citation_only_patterns` "insight-dropbox-report" entry.
12. `config/governance/hygiene-baseline-registry.toml` - annotated the header-comment citation and the `source_reports` array entry `(source retired 2026-07-17)`. HYG-060's frozen finding title/classification left byte-for-byte unchanged (frozen historical baseline; verified `source_reports` is loaded as descriptive strings only, never opened as a file, and the only test assertion is a count `== 2`, unaffected by in-place string annotation).
13. `.gitignore` - removed the entire dead block: header comment through final pattern (34 lines net removed, not literally 21 as originally estimated; the LO reviewer's proposal-review nit on this exact point is confirmed correct). One pre-existing, unrelated dirty hunk remains in this file (a session-envelope-runtime-state ignore-pattern addition attributed to a different, sibling work item, ~30 lines further down) - **not part of this implementation and must not be swept into this thread's eventual finalization commit**. See Risk and Rollback below for the required scoped-commit handling.
14. `scripts/advisory_backlog_router.py` - docstring/comment-only correction (module docstring, `DROPBOX_RELATIVE` constant comment, `collect_dropbox_advisories` docstring). Runtime behavior unchanged and verified unchanged: `collect_dropbox_advisories` already fails safe (`if not dropbox.is_dir(): return advisories`) and `DROPBOX_RELATIVE`'s literal value was deliberately left untouched per the approved scope (removing it would break the 8 dependent tests documented in the proposal's Out of Scope).

## Specification-Derived Verification

| Spec | Verification | Result |
| --- | --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `python -m pytest platform_tests/scripts/test_document_author_metadata.py -q` | Passed: 12 tests passed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Post-edit `grep -c independent-progress-assessments` over all 15 target files: every remaining hit verified by hand to be an intentional `(source retired ...)` annotation or the frozen HYG-060 title; zero unaddressed live references. | Passed (see Commands Executed for the exact per-file counts). |

## Commands Executed

- `python -m pytest platform_tests/scripts/test_gtkb_hygiene_investigation.py platform_tests/scripts/test_document_author_metadata.py platform_tests/scripts/test_advisory_backlog_router.py -q` -> 54 passed
- `python -m pytest platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/scripts/test_evidence_freshness_boundary.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_session_startup_control_map.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_system_interface_map.py -q` -> 63 passed
- `python -m ruff check scripts/advisory_backlog_router.py` -> All checks passed
- `python -m ruff format --check scripts/advisory_backlog_router.py` -> 1 file already formatted
- Direct parse verification (`tomllib.load` / `yaml.safe_load`) of every hand-edited TOML/YAML file: `lo-file-safety.toml`, `declarative-agent-role-manifest.yaml`, `hygiene-sweep-patterns.toml`, `evidence-freshness-boundaries.toml` all parse cleanly
- `git status --short -- .gitignore config/agent-control/ config/governance/ scripts/advisory_backlog_router.py` and `git diff -- .gitignore` - confirmed the pre-existing unrelated hunk noted above
- Post-edit reference sweep (`grep -c independent-progress-assessments` per file): CONTROL-MAP.md=1, REVIEW-MODE-SETUP.md=1, SESSION-STARTUP-INDEX.md=1, PRIME-BUILDER-STARTUP-OVERLAY.md=1, LOYAL-OPPOSITION-STARTUP-OVERLAY.md=1, activity-disposition-profiles.toml=2, declarative-agent-role-manifest.yaml=0, system-interface-map.toml=0, lo-file-safety.toml=0, document-author-provenance.toml=0, evidence-freshness-boundaries.toml=7, hygiene-sweep-patterns.toml=0, hygiene-baseline-registry.toml=3 (2 annotations + 1 untouched HYG-060 title), .gitignore=0, advisory_backlog_router.py=2 (1 annotation + 1 intentionally-untouched `DROPBOX_RELATIVE` value) - every count individually verified by hand against expected annotations.

## Acceptance Criteria Status

- [x] No config/agent-control, config/governance, .gitignore, or script surface references the retired directory as a durable/live path; historical citations are annotated not deleted.
- [x] `lo-file-safety.toml` and `document-author-provenance.toml` remain valid and load cleanly after removals; both changes narrow gate scope only.
- [x] `hygiene-baseline-registry.toml` HYG-060 finding text is byte-for-byte unchanged.
- [x] `advisory_backlog_router.py` existing test suite remains green; only docstring/comments changed.

## Risk And Rollback

Risk realized as anticipated in the GO verdict: `.gitignore` carries a second, pre-existing, unrelated dirty hunk (a session-envelope runtime-state ignore-pattern addition attributed to a different work item) not part of this implementation. **Finalization must stage `.gitignore` at hunk granularity** (e.g. `git add -p` selecting only this thread's removed block, or an equivalent scoped patch) so that other hunk is neither committed under this thread's authorship nor discarded. The other 14 files have no competing dirty state and may be staged as whole files.

Rollback: `git checkout -- <path>` per file (or `git diff > backup.patch` before finalization) restores pre-implementation content; no destructive operation was performed and no file outside the 15 approved target paths was touched.

## Recommended Commit Type

`chore` - reference/documentation correction, config narrowing, and docstring accuracy; no new capability surface. (Overrides the bridge-generated proposal's `feat` default per `.claude/rules/file-bridge-protocol.md` Conventional Commits Type Discipline, consistent with both LO reviewers' independent notes on this point.)

## Loyal Opposition Asks

1. Verify the 15 file diffs against the approved proposal's scope.
2. Confirm the `.gitignore` hunk-isolation requirement above before/at finalization.
3. Confirm HYG-060's frozen finding text is byte-for-byte unchanged.
4. Return `VERIFIED` if this report and implementation satisfy the approved proposal; otherwise return `NO-GO` with exact findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
