REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-30-ruff-format-pre-file-gate-revised-4
author_model: claude-opus-4-8
author_model_version: 4.8-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3473
Implements: WI-3473

# Implementation Proposal - Catch `ruff format --check` pre-file: active-hook guardrail + rule-based checklist (WI-3473) (REVISED-4)

bridge_kind: implementation_proposal
Document: gtkb-ruff-format-pre-file-gate
Version: 007 (REVISED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-30 UTC
Session: S372
Responds to NO-GO: bridge/gtkb-ruff-format-pre-file-gate-006.md
Recommended commit type: feat:

target_paths: ["scripts/check_ruff_format.py", ".githooks/pre-commit", ".claude/rules/file-bridge-protocol.md", ".groundtruth/formal-artifact-approvals/2026-05-30-claude-rules-file-bridge-protocol-md.json", "platform_tests/scripts/test_check_ruff_format.py"]

## REVISED-4 Changes (closes NO-GO -006 F1)

NO-GO -006 confirmed REVISED-3's direction is correct (adapter machinery
avoided; checklist correctly in the canonical bridge-protocol rule; packet
listed in target_paths) and raised ONE finding:

- **-006 F1 (P1)** — the IP-3 `generate-approval-packet` command omitted two
  live-CLI-required fields: `--explicit-change-request` and `--change-reason`
  (both declared `[required]` per `groundtruth-kb/src/groundtruth_kb/cli.py`
  and `REQUIRED_PACKET_FIELDS` in `narrative_artifact_packet.py`). As written,
  packet generation would fail before the protected rule edit.

REVISED-4 closes it: the IP-3 command now includes both fields with concrete
values (verified against `generate-approval-packet --help`: the complete
required set is `--kind`, `--artifact-id`, `--action`, `--source-ref`,
`--explicit-change-request`, `--change-reason`, `--approval-mode`,
`--changed-by`, plus `--target` for narrative). Post-impl packet-field evidence
expectations are added to the spec-to-test mapping and acceptance criteria. No
other change from REVISED-3.

## REVISED-3 Changes (closes NO-GO -004 F1; owner-redirected checklist home)

NO-GO -004 confirmed F1/F2/F3 from -002 are closed, and raised ONE new finding:

- **-004 F1 (P1)** — the bridge-skill checklist half regenerated the Codex adapter, but the generator also writes `.codex/skills/MANIFEST.json` (and, with `--update-registry`, `config/agent-control/harness-capability-registry.toml`), which -003 did not authorize in `target_paths`.

Pre-revision investigation found a deeper blocker: `python scripts/generate_codex_skill_adapters.py --check` reports the adapter set is ALREADY DRIFTED from parallel-session edits (4 files: `bridge-propose`, `gtkb-hygiene-sweep`, `loyal-opposition-hygiene-assessment` adapters + `MANIFEST.json`). Editing the bridge skill + regenerating would bundle those 3 unrelated parallel-session adapters into this WI-3473 commit (a scoped-commit violation), because MANIFEST.json/registry are whole-file regenerations over all adapters.

Owner decision (S372 AUQ) on the resulting fork: **move the checklist to its canonical home, `.claude/rules/file-bridge-protocol.md`, via an owner-approved narrative-artifact-approval packet**, avoiding the adapter machinery entirely. REVISED-3:

1. **Drops** the bridge-skill edit, `.codex/skills/bridge/SKILL.md`, `.codex/skills/MANIFEST.json`, and the capability registry from scope (no adapter machinery; no parallel-drift entanglement).
2. **Moves the checklist** into `.claude/rules/file-bridge-protocol.md` (the canonical "Mandatory Specification-Derived Verification Gate" home) via a narrative-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-30-claude-rules-file-bridge-protocol-md.json`.
3. **Keeps the guardrail design unchanged** from -003: stdlib-only `scripts/check_ruff_format.py` with deterministic venv-first ruff resolution, invoked by the active `.githooks/pre-commit`; plus its tests.

## Summary

Closes the recurring formatter-gate defect (WI-3473): GT-KB enforces `ruff format --check` at CI (post-push), session-wrap (post-VERIFIED), and Codex verification (the NO-GO point), but nowhere at Prime's pre-file moment. Per the owner's "Both" design, this adds: (1) a mechanical guardrail wired into the active `.githooks/pre-commit` (deterministic venv-resolved ruff; commit-time defense-in-depth); and (2) a pre-file checklist step in the canonical verification-gate rule (`.claude/rules/file-bridge-protocol.md`) instructing Prime to run BOTH `ruff check` AND `ruff format --check` on changed Python before filing a post-impl report (the pre-file discipline that prevents the Codex NO-GO).

## Owner Decisions / Input

- **S372 AUQ #1** = "Start WI-3473 (formatter gate)".
- **S372 AUQ #2** = "Both: guardrail + checklist (Rec.)" — dual enforcement design.
- **S372 AUQ #3** = "Checklist in file-bridge-protocol rule (Rec.)" — after the adapter-drift blocker was surfaced, owner chose the canonical-rule home (narrative packet) over the adapter-entangled bridge-skill home or guardrail-only. This REVISED-3 implements exactly that.
- The protected-rule edit requires an owner-approved narrative-artifact-approval packet at implementation time (content + sha256 presented via AskUserQuestion before the protected write), per the precedent set this session on `.claude/rules/project-root-boundary.md`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — the guardrail/test/hook half is fast-lane (origin=defect; standing PAUTH by membership). The protected-rule half is authorized separately by the narrative-artifact-approval packet (below).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization + Project + Work Item header present.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — the `.claude/rules/file-bridge-protocol.md` edit is a protected narrative-artifact mutation requiring an owner-approved narrative-artifact-approval packet; the narrative-artifact-approval-gate hook validates the write against the packet sha256.
- `config/governance/narrative-artifact-approval.toml` — the protected narrative-artifact registry that enumerates `.claude/rules/*.md` + the Slice C pre-commit evidence floor (`scripts/check_narrative_artifact_evidence.py`).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers the source/test_addition/hook_upgrade half by membership; still goes through GO + impl-start packet + VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root; no `applications/**` mutation.
- `GOV-STANDING-BACKLOG-001` — WI-3473 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the guardrail is a deterministic check (subprocess + deterministic venv-first resolver; no LLM).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — (advisory) durable governance artifacts with traceability to WI-3473 + the motivating NO-GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — (advisory) owner-decision / work-item framing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — (advisory) WI-3473 lifecycle advances; VERIFIED gate on the post-impl report.

## Requirement Sufficiency

Existing requirements sufficient. The standard (`ruff format`) already exists and is enforced at CI / wrap / Codex-verify; this change adds the missing pre-file (rule) + commit-time (active hook) enforcement points. No new GOV/SPEC/ADR/DCL is required; the rule edit refines existing verification-gate guidance and is authorized by the narrative-artifact-approval packet.

## Authorization Split

- **Guardrail half** (`scripts/check_ruff_format.py` = source; `.githooks/pre-commit` = hook_upgrade; `platform_tests/scripts/test_check_ruff_format.py` = test_addition): covered by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through WI-3473's active project membership.
- **Checklist half** (`.claude/rules/file-bridge-protocol.md` = protected narrative artifact): authorized by the per-artifact narrative-artifact-approval packet (owner-approved at impl time). The standing PAUTH does NOT cover narrative-artifact edits; the packet is the authorization, consistent with `GOV-ARTIFACT-APPROVAL-001`.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing reliability fast-lane (project + PAUTH + GOV spec).
- `bridge/gtkb-ruff-format-pre-file-gate-002.md` / `-004.md` (Codex NO-GOs) — the findings this thread has closed across revisions (-002 F1 active hook, F2 resolver, F3 advisory; -004 F1 generator output set → resolved by moving off the adapter machinery).
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` — precedent on `.githooks` being the active hook path.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-006.md` (VERIFIED this session) — precedent for the protected-rule narrative-artifact-approval packet workflow used by the checklist half here.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-004.md` / `-006.md` — the formatter-gate NO-GO that motivated WI-3473 + its VERIFIED closure.
- WI-3473 backlog capture (PROJECT-GTKB-RELIABILITY-FIXES) — durable defect record + the A/B/C design tradeoff.

## Proposed Implementation

### IP-1: `scripts/check_ruff_format.py` (new stdlib-only guardrail; unchanged from -003)

Stdlib-only (no `groundtruth_kb` import). Separable, testable functions:

- `staged_python_files(repo_root) -> list[str]`: `git diff --cached --name-only --diff-filter=ACM` filtered to `*.py`.
- `resolve_ruff(search_root) -> list[str] | None`: deterministic, venv-first — (1) `<search_root>/groundtruth-kb/.venv/Scripts/python.exe` (Windows) or `.../bin/python` (POSIX) `-m ruff`; (2) `sys.executable -m ruff`; (3) `shutil.which("ruff")`. First whose `--version` returns rc 0; else `None`.
- `check_files(ruff_cmd, files) -> (ok, output)`: runs `<ruff_cmd> format --check <files>`.
- `main()`: repo_root via `git rev-parse --show-toplevel` (fallback cwd); no staged `.py` -> PASS (0). Resolve ruff; if `None` and `<root>/groundtruth-kb/.venv` exists -> FAIL (1, "venv present but ruff unresolvable"); if `None` and no venv -> WARN + PASS (0, non-dev/CI). If resolved -> check; PASS (0) formatted, FAIL (1) naming offenders + remedy (`ruff format <paths>`).

### IP-2: `.githooks/pre-commit` (active hook; unchanged from -003)

Insert, in the existing staged-check style, after the narrative-artifact-evidence check:

```bash
"$PYTHON_BIN" scripts/check_ruff_format.py --staged || exit $?
```

`PYTHON_BIN` need not have ruff: the stdlib-only script resolves ruff itself (venv-first). `.githooks` is the configured `core.hooksPath`, so the edit is live immediately (no reinstall).

### IP-3: `.claude/rules/file-bridge-protocol.md` checklist (narrative packet) — REPLACES the prior bridge-skill approach

Add a concise pre-file step to the "Mandatory Specification-Derived Verification Gate" section: before filing a post-implementation report, run BOTH `ruff check` AND `ruff format --check` on changed Python files; the two are separate gates (lint vs. format), both enforced at Codex VERIFIED and by the `check_ruff_format` pre-commit guardrail. Implementation:

1. Compose the post-edit full content + sha256.
2. Present content + sha256 to the owner via AskUserQuestion; on approval, generate the packet via the COMPLETE command (all live-CLI-required fields, verified via `generate-approval-packet --help`):

```text
python -m groundtruth_kb generate-approval-packet \
  --kind narrative \
  --target .claude/rules/file-bridge-protocol.md \
  --artifact-id claude-rules-file-bridge-protocol-md \
  --action update \
  --source-ref bridge/gtkb-ruff-format-pre-file-gate-<GO>.md \
  --explicit-change-request "Add a pre-file verification step to the Mandatory Specification-Derived Verification Gate: before filing a post-implementation report, run both ruff check and ruff format --check on changed Python files (separate lint vs format gates, both enforced at Codex VERIFIED and by the check_ruff_format pre-commit guardrail). Per WI-3473." \
  --change-reason "bridge/gtkb-ruff-format-pre-file-gate-<GO>.md" \
  --approval-mode approve \
  --changed-by claude-prime-builder \
  --out .groundtruth/formal-artifact-approvals/2026-05-30-claude-rules-file-bridge-protocol-md.json \
  --validate-after --json
```

The `<GO>` placeholder is substituted with the eventual GO version at implementation time.
3. Write the rule edit (narrative-artifact-approval-gate validates against the packet sha256).
4. Run `scripts/check_narrative_artifact_evidence.py --staged` (Slice C floor) before commit.

No Codex adapter machinery is touched (rules are not skill-adaptered).

### IP-4: `platform_tests/scripts/test_check_ruff_format.py` (tests; unchanged from -003)

- `test_passes_when_formatted`; `test_fails_when_unformatted`; `test_passes_when_no_python_staged`; `test_ignores_non_python`.
- `test_resolver_prefers_venv` (F2 regression): `resolve_ruff(REPO_ROOT)` returns a command under `groundtruth-kb/.venv` when present (proves no fail-open).
- `test_resolver_warn_pass_only_without_venv`: WARN-pass only when no venv; FAIL when venv present but ruff missing.

## Spec-to-Test Mapping

| Specification / Behavior | Test / Verification | Expected |
|---|---|---|
| Guardrail PASS when staged Python formatted | `test_passes_when_formatted` | PASS |
| Guardrail FAIL (exit 1) when unformatted | `test_fails_when_unformatted` | PASS |
| No-op PASS when no Python staged | `test_passes_when_no_python_staged` | PASS |
| Non-Python ignored | `test_ignores_non_python` | PASS |
| F2: deterministic venv-first resolution (no fail-open) | `test_resolver_prefers_venv` | PASS |
| F2: WARN-pass only without venv; FAIL when venv lacks ruff | `test_resolver_warn_pass_only_without_venv` | PASS |
| Active hook blocks unformatted in THIS checkout | post-impl `.githooks/pre-commit` dry-run | PASS at post-impl |
| `GOV-ARTIFACT-APPROVAL-001` rule edit authorized | narrative packet generated + `--validate-after` + narrative-artifact-approval-gate validates write; `check_narrative_artifact_evidence.py --staged` PASS | PASS at post-impl |
| -006 F1: packet carries required fields | post-impl `--validate-after --json` shows `artifact_type: narrative_artifact`, `target_path: .claude/rules/file-bridge-protocol.md`, non-empty `explicit_change_request` + `change_reason`, `presented_to_user: true`, `transcript_captured: true` | PASS at post-impl |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` deterministic check | inspection | PASS |

Verification commands:
- `python -m pytest platform_tests/scripts/test_check_ruff_format.py -q --tb=short`
- `<venv-python> -m ruff check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py`
- `<venv-python> -m ruff format --check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py` (dogfood)
- `python scripts/check_narrative_artifact_evidence.py --staged`
- Active-hook dry-run: stage an unformatted `.py`, run `.githooks/pre-commit`, observe block; format, observe pass.

## Bridge Protocol Handling

Filed as `REVISED` at `-005`; `REVISED` line inserted at the top of the document block. Append-only; `-001`..`-004` retained. `bridge/INDEX.md` canonical.

## Acceptance Criteria

- [ ] Codex GO on REVISED-3.
- [ ] Implementation-start packet activated from the GO.
- [ ] Owner-approved narrative packet for `.claude/rules/file-bridge-protocol.md` (content + sha256 presented; packet validates).
- [ ] Packet command includes `--explicit-change-request` + `--change-reason`; post-impl `--validate-after --json` evidence shows both fields non-empty plus `presented_to_user`/`transcript_captured` true (-006 F1).
- [ ] IP-1/IP-2/IP-3/IP-4 landed; all tests + `ruff check` + `ruff format --check` (venv) clean on new files (dogfood); Slice C narrative-evidence check PASS.
- [ ] Active-hook dry-run in THIS checkout: blocks unformatted staged `.py`, passes formatted.
- [ ] No `.codex` adapter / MANIFEST / registry touched (confirmed by `git status`).
- [ ] Post-impl report with test/ruff/dry-run/packet evidence.
- [ ] Codex VERIFIED.

## Risk and Rollback

Risk: low-moderate. Guardrail additive on the active hook; venv-first resolver (no fail-open in dev env). Protected-rule edit gated by owner packet. No adapter machinery (avoids the parallel-drift entanglement that blocked -003's bridge-skill approach).

- **Active-hook edit risk**: mitigated by minimal additive line + the dry-run acceptance criterion.
- **Protected-rule edit**: gated by the narrative-artifact-approval packet + Slice C evidence floor; owner approves content + sha256 before write.

Rollback: revert the source/hook/test/rule files; delete the packet JSON (gitignored). No data/state to roll back.

## Loyal Opposition Asks

1. Confirm the owner-redirected checklist home (`.claude/rules/file-bridge-protocol.md` via narrative packet) correctly avoids the adapter-machinery / parallel-drift blocker from -004, and that the split authorization (standing PAUTH for source/hook/test; narrative packet for the protected rule) is correct.
2. Confirm the guardrail design (active `.githooks/pre-commit`, venv-first resolver, fail-when-venv-but-no-ruff) carries forward correctly from -003.
3. Confirm `target_paths` is now complete for the chosen approach (no generator output set; the only generated artifact is the narrative packet, which is listed).
4. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
