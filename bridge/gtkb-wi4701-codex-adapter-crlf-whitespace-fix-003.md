REVISED

# Codex adapter generator emits CRLF line endings; pin LF on write (WI-4701) — REVISED for source/test-only scope

bridge_kind: implementation_proposal
Document: gtkb-wi4701-codex-adapter-crlf-whitespace-fix
Version: 003 (REVISED)
Recommended commit type: fix:
Responds to: bridge/gtkb-wi4701-codex-adapter-crlf-whitespace-fix-002.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4701

target_paths: ["scripts/generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Summary

This REVISED version resolves the Loyal Opposition NO-GO at version 002. The NO-GO had one blocker (P1) and one minor finding (P2):

- P1: the prior version left an open reviewer decision about whether the one-time LF re-normalization of existing generated artifacts (`.codex/skills/**/SKILL.md`, `.codex/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`) would ride in the implementing commit, while `target_paths` authorized only source and test. A GO must not defer that scope decision to the implementation session.
- P2: the applicability preflight surfaced two un-cited advisory specs.

This version picks Loyal Opposition's **Option 1 (source/test only)** explicitly and encodes it in `target_paths`, acceptance criteria, risk/rollback, and the verification plan. The live-workspace LF re-normalization of the existing CRLF artifacts is **out of scope** here and is deferred to a separate authorized change (see Scope Resolution). Advisory citations are addressed in Specification Links.

## Problem / Diagnosis

`scripts/generate_codex_skill_adapters.py` writes generated text artifacts in Python text mode without `newline="\n"`, so on Windows (`os.linesep == '\r\n'`) every emitted `\n` is translated to `\r\n`. Generated files carry a trailing carriage return on every line, and `git diff --check` flags that trailing `\r` as a whitespace error on lines it treats as added (the regenerated `source_sha256` lines on a routine regeneration). The offending byte is `0x0d` (CR), not a literal space.

Exact emission sites:
- `scripts/generate_codex_skill_adapters.py:249` — `_write_if_changed`: `path.write_text(content, encoding="utf-8")` (no `newline="\n"`). Writes adapter `SKILL.md` and `MANIFEST.json`.
- `scripts/generate_codex_skill_adapters.py:331` — `update_registry` via `_rewrite_registry_text`: `registry_path.write_text(updated, encoding="utf-8")` (no `newline="\n"`). Writes the registry `source_sha256` lines.
- `scripts/generate_codex_skill_adapters.py:260` — `_write_bytes_if_changed` already writes bytes EOL-faithfully and is intentionally left unchanged.

In-process proof the defect is in the write path, not the rendered string: the in-memory `_manifest_content(...)` / `_rewrite_registry_text(...)` outputs contain zero CR bytes and zero rstrip-trailing-whitespace lines; the on-disk `.codex/skills/MANIFEST.json` contains `\r\n`; `git ls-files --eol` reports the generated files as `i/crlf w/crlf` while their canonical LF sources are `i/lf`. Loyal Opposition independently confirmed all of this in the version 002 Positive Confirmations.

Two ticket corrections carried forward from version 001 (surfaced honestly): the root cause is text-mode newline translation, not "an f-string with a trailing space"; and no literal `git diff --check` / `git diff --cached --check` call exists in `.githooks/pre-commit`, `scripts/`, or CI (verified by repo-wide search) — the CR-as-whitespace rejection surfaces when `git diff --check` is run as a verification/inspection step, and as a latent contaminant, not through a hard call inside `finalize_verified_commit`.

WI-4680 linkage (confirmed at the file level): the two adapter files in the `gtkb-lo-verified-commit-atomicity` `-005`..`-016` dirty-worktree churn (`.codex/skills/verify/SKILL.md`, `.codex/skills/MANIFEST.json`) are exactly these CRLF outliers. Fixing the generator removes one concrete, repeatable source of that adapter-commit friction. (The WI-4680 NO-GO chain has additional independent causes this fix does not resolve.)

## Proposed Change

Surgical, source-only. Make the generator emit LF unconditionally on every text write, independent of host platform.

1. `_write_if_changed` (`scripts/generate_codex_skill_adapters.py:242`): change the write to `path.write_text(content, encoding="utf-8", newline="\n")`, and make the read-back/idempotency comparison treat a previously-CRLF file as changed (return changed when `existing is not None and "\r" in existing`) so a stale CRLF file is corrected the next time the generator legitimately runs.
2. `update_registry` (`scripts/generate_codex_skill_adapters.py:324-332`): change `registry_path.write_text(updated, encoding="utf-8")` to add `newline="\n"`, with the same "rewrite when existing contains a carriage return" guard.
3. Leave `_write_bytes_if_changed` (line 253) unchanged — byte-mode writes are EOL-faithful; resource mirrors copy source bytes verbatim and must not be newline-rewritten.
4. Defense in depth: before write, assert no rendered line carries trailing whitespace, raising a generator failure if the rendered string itself ever regresses, so generator `--check` PASS implies whitespace-clean emitted output.

## Scope Resolution

Per Loyal Opposition Option 1, this bridge is **source and test only**:

- `target_paths` is exactly `scripts/generate_codex_skill_adapters.py` and `platform_tests/scripts/test_generate_codex_skill_adapters.py` — matching the `PAUTH-...-COMPLIANCE-DISPATCH-BATCH-002` allowed mutation classes (`source`, `test`), which forbid generated-artifact, config, GOV/ADR/DCL, and narrative-artifact mutation.
- The implementation session will **not** regenerate, commit, or leave dirty any live `.codex/skills/**` artifact or `config/agent-control/harness-capability-registry.toml`. There is no open reviewer decision.
- All correctness evidence is produced in isolated `tmp_path` project roots (the existing test module already builds these via `_load_module()` / `_write_skill` / `_write_registry`), plus a read-only generator `--check` run for observation. No live workspace mutation beyond the two `target_paths`.
- The one-time LF convergence of the existing repository CRLF artifacts (the ~38 CRLF-in-index outliers) is **explicitly deferred** as separate, broader-scope work that pairs naturally with the `.gitattributes eol=lf` hardening already captured as **WI-4714**. Converging those files requires authorization beyond `source`/`test` (it touches generated `.codex/skills/**` and `config/`), so it is intentionally not bundled here. Until that separate change lands, a manual generator `--check` against the live tree will report the pre-existing CRLF artifacts as drift; that is the deferred-convergence signal, not a regression introduced by this source-only fix (no commit-time gate runs the generator `--check` or `git diff --check`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + authorization metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` — WI-4701 is the governed backlog item for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed and inspected paths are under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex skill adapters must remain faithful, cleanly-committable generated parity surfaces; CRLF skew on the generated adapters undermines that parity guarantee.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the deferred live-artifact convergence is preserved as an explicit lifecycle state (deferred to WI-4714), satisfying the artifact-lifecycle-trigger advisory the version 002 preflight surfaced.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the durable generated artifacts must be reproducible and contaminant-free.
- Advisory `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (surfaced by the version 002 applicability preflight) is intentionally NOT cited: it does not resolve as a live specification in MemBase (`gt`/KB lookup returns no such spec). Citing a non-existent spec id would be worse than omitting an advisory; this is recorded here per verify-before-cite.

## Owner Decisions / Input

- This is project-authorized reliability work under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002` (owner AUQ 2026-06-21, `DELIB-20265459`), which authorizes WI-4701 implementation in `source` and `test` only. This REVISED version keeps the work strictly within that authorized scope, so no new owner decision is required to proceed after Loyal Opposition GO.
- The previously-solicited reviewer decision about committing regenerated artifacts is removed: scope is fixed to source/test-only (see Scope Resolution).

## Prior Deliberations

- `DELIB-20265286` — owner directive and authorization basis for the WI-4680 atomicity thread whose adapter-commit friction this fix relieves.
- `DELIB-20265459` — project authorization decision for the bridge-tooling/dispatch reliability batch including WI-4701.
- `bridge/gtkb-lo-verified-commit-atomicity-016.md` (and the `-005`..`-015` chain) — the WI-4680 NO-GO sequence documenting the CRLF adapter files repeatedly stuck uncommitted; this proposal removes one concrete CRLF-normalization cause.
- `bridge/gtkb-wi4701-codex-adapter-crlf-whitespace-fix-002.md` — the Loyal Opposition NO-GO this version answers.
- Deliberation search `gt deliberations search "codex adapter generator CRLF target_paths scope generated artifacts regeneration commit"` returned no directly-governing prior decision on the scope choice (top matches were unrelated verdicts); this proposal does not revisit a previously-rejected approach.

## Requirement Sufficiency

Existing requirements sufficient. WI-4701's acceptance summary (generator-produced artifacts pass `git diff --check` immediately after regeneration; generator `--check` and `git diff --check` agree on whitespace cleanliness) is a complete, testable requirement satisfied at the generator level by this source-only fix. No new specification is required before implementation.

## Specification-Derived Verification Plan

All tests run in isolated `tmp_path` project roots (no live-workspace mutation). Spec-to-test mapping:

| Specification / requirement | Test | Expected |
| --- | --- | --- |
| WI-4701 acceptance: generated artifacts are CR-free | `generate(tmp_root, check=False)`; read `.codex/skills/MANIFEST.json` and each generated `SKILL.md` as bytes | no byte `0x0d`; every decoded line equals its rstrip |
| WI-4701 acceptance: registry codex blocks are CR-free | `update_registry(tmp_root, adapters)`; read the registry as bytes | every `source_sha256` line ends at the closing quote with no trailing CR/space; no `\r\n` in file |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: generator `--check` PASS implies whitespace-clean | pre-seed a generated file with CRLF in `tmp_root`, run `generate(..., check=True)` | drift reported (CRLF tree fails `--check`) |
| Idempotency on LF | run `generate` twice in `tmp_root`; second run `check=True` | no drift (LF output stable) |
| No content/hash regression | compare `source_sha256` values and adapter body (minus EOL) before/after the fix | hashes and adapter text unchanged; only EOL differs |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: adapter parity intact | existing adapter-render assertions in the module | continue to pass unchanged |

Commands (run from `E:\GT-KB`):
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short`
- Regression: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_skill_load_smoke.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short`
- Read-only observation (no mutation): `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check` (documents the deferred live-artifact convergence; not a commit gate)
- Lint/format: `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/generate_codex_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py` and `... -m ruff format --check ...` on the same two files.

## Findings Addressed

### P1 - Target paths do not authorize the generated artifacts the proposal said may be rewritten

Response: Scope is fixed to source/test-only. `target_paths` remains exactly the generator plus its test module — matching the BATCH-002 allowed mutation classes. The implementation will not regenerate, commit, or leave dirty any `.codex/skills/**` artifact or the registry. Correctness is proven in isolated `tmp_path` roots plus a read-only `--check` observation. The live-artifact LF convergence is explicitly deferred to separate broader-scope work paired with WI-4714. The open reviewer decision is removed.

### P2 - Applicability preflight not fully clean on advisory specifications

Response: `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is now cited (the deferred convergence is an explicit lifecycle state). `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is explicitly NOT cited because it does not resolve as a live MemBase spec (verify-before-cite); a justification is recorded in Specification Links. Required-spec coverage was already complete; this clears the advisory surface to the extent the advisory specs exist.

## Risk And Rollback

- Risk: the source-only fix leaves the live CRLF artifacts unconverged, so a manual generator `--check` reports drift until the deferred WI-4714-paired change lands. Mitigation: documented as the deferred-convergence signal; no commit-time gate runs generator `--check` or `git diff --check` (verified by repo-wide search), so no commit is blocked, and the generator is now correct so any future legitimate regeneration produces LF.
- Risk: changing the read-back comparison could cause needless rewrites. Mitigation: the "rewrite when existing contains a carriage return" guard fires only while a CRLF file still exists; after the first LF write it is inert.
- Risk: `source_sha256` values change. Mitigation: none — hashes are computed from LF-normalized source text, independent of how the output file is written; tests assert hash invariance.
- Rollback: revert the single source commit; the test additions are additive. No state migration; no schema change.

## Acceptance Criteria

- [ ] `scripts/generate_codex_skill_adapters.py` writes all text artifacts with `newline="\n"`; generated output (verified in `tmp_path`) contains no CR byte.
- [ ] Generator `--check` reports drift for a CRLF-contaminated `tmp_path` tree (generator PASS implies whitespace-clean output).
- [ ] `source_sha256` values and adapter body content are byte-identical except for EOL; no parity or hash regression.
- [ ] `target_paths` remains source/test only; no `.codex/skills/**` or registry artifact is regenerated, committed, or left dirty under this bridge; the live-artifact convergence is deferred to WI-4714-paired work.
- [ ] New/extended tests in `test_generate_codex_skill_adapters.py` pass (isolated `tmp_path`); `test_codex_skill_load_smoke.py` regression passes; ruff check + format clean on the two changed files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
