NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

# Codex adapter generator emits CRLF line endings that fail git diff --check on regenerated source_sha256 lines (WI-4701)

bridge_kind: implementation_proposal
Document: gtkb-wi4701-codex-adapter-crlf-whitespace-fix
Version: 001 (NEW)
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4701

target_paths: ["scripts/generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem / Diagnosis

`scripts/generate_codex_skill_adapters.py` writes every generated artifact in Python text mode without `newline=""`, so on Windows each emitted `\n` is translated to `\r\n`. The generated files (`.codex/skills/**/SKILL.md`, `.codex/skills/MANIFEST.json`, and the `[capabilities.codex]` blocks in `config/agent-control/harness-capability-registry.toml`) therefore carry a trailing carriage return on every line. `git diff --check` flags that trailing `\r` as a whitespace error on any line it treats as *added* — which, on a routine regeneration, is precisely the `source_sha256` lines whose hash changed. That is the "trailing whitespace on source_sha256 lines" reported in WI-4701; the offending byte is `0x0d` (CR), not a literal space.

Exact emission sites (the CR is introduced at write time, not in the string):
- `scripts/generate_codex_skill_adapters.py:249` — `_write_if_changed`: `path.write_text(content, encoding="utf-8")` (no `newline=""`). Writes every adapter `SKILL.md` and `MANIFEST.json`.
- `scripts/generate_codex_skill_adapters.py:331` — `update_registry` via `_rewrite_registry_text`: `registry_path.write_text(updated, encoding="utf-8")` (no `newline=""`). Writes the registry's `source_sha256 = "…"` lines (`_registry_adapter_block`, line 278).
- `scripts/generate_codex_skill_adapters.py:260` — `_write_bytes_if_changed` already writes bytes and is correct; it is listed only to scope the fix (no change needed there).

In-process proof the defect is in the *write* path, not the rendered string:
- The generator's in-memory `_manifest_content(...)` and `_rewrite_registry_text(...)` outputs contain zero CR bytes and zero `rstrip()`-trailing-whitespace lines; the `source_sha256` line ends at byte `0x22` (`"`).
- The on-disk `.codex/skills/MANIFEST.json` contains `\r\n` (byte preceding `\n` is `0x0d`).
- `os.linesep == '\r\n'` on the build host; `git ls-files --eol` reports the generated files as `i/crlf w/crlf attr/` (CRLF in index, no governing `.gitattributes` rule — `.gitattributes` exists but is empty), while their canonical sources (e.g. `.claude/skills/verify/SKILL.md`) are `i/lf`. Of 11,659 tracked files only 38 are CRLF-in-index, and the generator's outputs are among those 38 outliers. The generator is the sole producer of that CRLF skew.

Two accuracy corrections to the WI-4701 ticket text, surfaced honestly so the reviewer is not misled:
1. The root cause is a trailing CR from text-mode newline translation, not "an f-string with a trailing space" or "join with padding." No emitted string literal contains a trailing space.
2. The ticket states the finalization gate "runs `git diff --cached --check`." A repo-wide search (`*.py`, `*.sh`, `*.ps1`, `*.yml`, `*.yaml`, `*.toml`) finds **no** literal `git diff --check` / `git diff --cached --check` call in `.githooks/pre-commit`, `scripts/`, or CI. The pre-commit hook's gates are secret-scan, inventory-drift, narrative-evidence, `ruff format --check`, protected-commit-authorization, and PS1-parse. The CR-as-whitespace rejection therefore surfaces through `git diff --check` when it is run as a verification/inspection step (and is a latent contaminant for any author or external pre-commit that does run it), not through a hard call inside `finalize_verified_commit`. The fix is still correct and necessary — the generator must not emit CRLF — but the proposal does not claim a code path that does not exist.

WI-4680 linkage (confirmed at the artifact level, mechanism partially corrected): WI-4680 ("Make LO VERIFIED verdict recording atomic with final commit") churned through `bridge/gtkb-lo-verified-commit-atomicity-005` … `-016` with the regenerated `.codex/skills/verify/SKILL.md` and `.codex/skills/MANIFEST.json` adapters repeatedly stuck uncommitted in a dirty worktree (see `-016` findings P1–P3). Those two adapter files are exactly the CRLF-outlier artifacts this generator produces (`.codex/skills/verify/SKILL.md` → `i/crlf`; its source → `i/lf`). A CRLF-vs-LF normalization skew on the generated adapters is a credible, evidence-supported contributor to those files repeatedly showing as dirty/non-cleanly-committable across sessions and harnesses (a Windows author writing CRLF vs an LF-normalizing context produces phantom whole-file diffs and `git diff --check` whitespace errors). I therefore assert the linkage as **confirmed at the file level** (same artifacts, same CRLF defect) while noting the WI-4680 NO-GO chain has additional independent causes (≈60+ dirty unrelated files, headless write-handle denials) that this fix does not by itself resolve. Normalizing the generator to LF removes one concrete, repeatable source of the WI-4680 adapter-commit friction.

This is a small, surgical fix: force LF on write in the generator, plus a regression test that asserts generated output is CR-free and `rstrip`-clean.

## Proposed Change

Surgical, source-only. Make the generator emit LF unconditionally on every write, independent of host platform:

1. In `_write_if_changed` (`scripts/generate_codex_skill_adapters.py:242`), change the write to `path.write_text(content, encoding="utf-8", newline="\n")` and, for byte-accurate idempotency, normalize the read-back comparison so a previously-CRLF file is detected as changed and rewritten LF (read existing text with `newline=""` is not enough — compare against the LF form, e.g. treat `existing` as changed when it contains `\r`). Simplest robust form: keep the string compare but also return changed when `existing is not None and "\r" in existing`.
2. In `update_registry` (`scripts/generate_codex_skill_adapters.py:324-332`), change `registry_path.write_text(updated, encoding="utf-8")` to `...newline="\n"`, and apply the same "rewrite when existing contains `\r`" guard so an already-CRLF registry is corrected on the next run.
3. Leave `_write_bytes_if_changed` (line 253) unchanged — byte-mode writes are already EOL-faithful; resource mirrors copy source bytes verbatim and must not be newline-rewritten.
4. (Defense in depth, optional but recommended) After computing `content`, assert no line has trailing whitespace before write, raising a generator failure if the rendered string itself ever regresses — so `--check` PASS implies whitespace-clean output (this directly satisfies WI-4701 fix-candidate (b)/(c): generator PASS implies `git diff --check` PASS for the emitted lines).

Note on `.gitattributes` (flag, do not silently expand scope): the repository's `.gitattributes` is empty, so CRLF normalization is governed only by global `core.autocrlf=true`. A complementary `.gitattributes` rule (e.g. `*.json text eol=lf`, `*.toml text eol=lf`, `.codex/skills/** text eol=lf`) would harden this repo-wide, but that is a broader change touching files beyond `target_paths` and could re-normalize the other 36 CRLF outliers. I am intentionally **scoping this proposal to the generator fix only** and flagging the `.gitattributes` hardening as a candidate follow-up work item for separate review, not bundling it here.

Re-emission / approval-packet flag (per instruction, flagged not assumed): applying this fix and re-running the generator will rewrite the existing CRLF generated artifacts to LF, so a one-time regeneration will show `.codex/skills/**/SKILL.md`, `.codex/skills/MANIFEST.json`, and the registry's codex blocks as changed (whole-file EOL diffs). Those regenerated artifacts may therefore appear in the implementing commit alongside the two `target_paths`. They are mechanically generated outputs of the changed source (not hand-authored narrative), so they should not require a separate narrative-artifact approval packet; however, because the registry and adapters are governance-adjacent generated surfaces, the implementing session should confirm at commit time whether the protected-commit-authorization / narrative-evidence gates classify any of them as requiring evidence, and include the regeneration in the same VERIFIED transaction if so. This proposal does not pre-authorize that bundling; it surfaces it for the reviewer.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping provided in the verification plan below.
- `GOV-STANDING-BACKLOG-001` — WI-4701 is the governed backlog item for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed and inspected paths are under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex skill adapters must remain faithful, cleanly-committable generated parity surfaces; CRLF skew on the generated adapters undermines that parity guarantee (this is the same ADR carried in the WI-4680 `-016` verdict whose adapter churn this fix relieves).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the durable generated artifacts must be reproducible and contaminant-free.

## Owner Decisions / Input

- WI-4701 is an open P2 defect in PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, an owner-authorized (PAUTH) reliability project; the project-authorization citation above is finalized by the interactive Prime Builder session per the owner's AskUserQuestion authorization of the unauthorized bridge-tooling defect batch (WI-4565 / WI-4662 / WI-4701). No new owner decision is required to proceed once this proposal receives Loyal Opposition GO; the fix is source-only, additive in test coverage, and changes only line-ending emission (no behavioral change to adapter content or hashes — the `source_sha256` values are computed from LF-normalized source text and are unaffected).
- One reviewer decision is solicited: whether the one-time LF re-normalization of the existing generated artifacts should ride in the implementing commit (recommended, so the tree converges) or be staged as a separate follow-up. See the re-emission flag above.

## Prior Deliberations

- `DELIB-20265286` — owner directive and authorization basis for the WI-4680 atomicity thread whose adapter-commit friction this fix relieves.
- `bridge/gtkb-lo-verified-commit-atomicity-016.md` (and the `-005`…`-015` chain) — the WI-4680 NO-GO sequence documenting `.codex/skills/verify/SKILL.md` and `.codex/skills/MANIFEST.json` repeatedly stuck uncommitted in a dirty worktree; this proposal removes one concrete CRLF-normalization cause.
- Deliberation search `gt deliberations search "adapter generation source_sha256 trailing whitespace git diff check"` returned no directly-governing prior decision (top semantic matches were unrelated verification verdicts, scores 0.76–0.85); this proposal does not revisit a previously-rejected approach.

## Requirement Sufficiency

Existing requirements sufficient: WI-4701's acceptance summary ("generator-produced `.codex/skills/MANIFEST.json` and `harness-capability-registry.toml` pass `git diff --check` immediately after regeneration; generator `--check` and `git diff --check` agree") is a complete, testable requirement. No new specification is required before implementation.

## Specification-Derived Verification Plan

New/extended unit tests in `platform_tests/scripts/test_generate_codex_skill_adapters.py` (the existing generator test module, which already builds isolated `tmp_path` project roots via `_load_module()` / `_write_skill` / `_write_registry`). Spec-to-test mapping:

| Specification / requirement | Test | Expected |
| --- | --- | --- |
| WI-4701 acceptance: generated artifacts are `git diff --check`-clean (no trailing CR) | Run `generate(tmp_root, check=False)`; read `.codex/skills/MANIFEST.json` and each generated `SKILL.md` as bytes | no byte `0x0d` present; every decoded line equals its `rstrip()` |
| WI-4701 acceptance: registry codex blocks are CR-free | Run `update_registry(tmp_root, adapters)`; read the registry as bytes | every `source_sha256 = "…"` line ends at `"` with no trailing `\r`/space; no `\r\n` in file |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: generator `--check` PASS implies whitespace-clean | Pre-seed a generated file with CRLF, then run `generate(..., check=True)` | drift is reported (file flagged as would-update), i.e. `--check` no longer passes a CRLF-contaminated tree |
| Idempotency preserved on LF host state | Run `generate` twice; second run with `check=True` | second `--check` reports no drift (LF output is stable) |
| No content/hash regression | Compare `source_sha256` values and adapter body (minus EOL) before/after the fix | hashes and adapter text content unchanged; only EOL differs |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: adapter parity intact | Existing adapter-render assertions in the module | continue to pass unchanged |

Commands (run from `E:\GT-KB`):
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short`
- Regression: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_skill_load_smoke.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short`
- Post-fix regeneration drift check: `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry` (expect: only intended LF re-normalization, then clean)
- Format/lint: `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/generate_codex_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/generate_codex_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py`

## Risk And Rollback

- Risk: the one-time LF re-normalization produces a large whole-file diff on the existing generated artifacts. Mitigation: this is a single, intentional, reviewable convergence commit; subsequent runs are stable (idempotent on LF). The reviewer decision above governs whether it rides in this commit.
- Risk: changing the read-back/idempotency comparison could cause needless rewrites. Mitigation: the "rewrite when existing contains `\r`" guard fires only while a CRLF file still exists; after the first LF write it is inert, so steady-state behavior is unchanged.
- Risk: resource-mirror byte copies unintentionally newline-rewritten. Mitigation: `_write_bytes_if_changed` is deliberately left untouched; only the two text-write call sites change.
- Risk: `source_sha256` values change. Mitigation: none — hashes are computed from `_strip_generated_block(source_text).rstrip() + "\n"` (LF-normalized source), independent of how the *output* file is written; tests assert hash invariance.
- Rollback: revert the single source commit; the test additions are additive. No state migration; no schema change. If the EOL convergence commit is undesirable, regeneration restores prior bytes.

## Acceptance Criteria

- [ ] `scripts/generate_codex_skill_adapters.py` writes all text artifacts with `newline="\n"`; no generated `.codex/skills/**` file or registry codex block contains a CR byte.
- [ ] Immediately after regeneration, `.codex/skills/MANIFEST.json` and `config/agent-control/harness-capability-registry.toml` pass `git diff --check` (no trailing-whitespace errors on `source_sha256` lines).
- [ ] Generator `--check` reports drift for a CRLF-contaminated tree (generator PASS implies whitespace-clean output).
- [ ] `source_sha256` values and adapter body content are byte-identical except for EOL; no parity or hash regression.
- [ ] New/extended tests in `test_generate_codex_skill_adapters.py` pass; `test_codex_skill_load_smoke.py` regression passes; ruff check + format clean.
- [ ] The `.gitattributes` hardening is recorded as a flagged follow-up candidate, not silently bundled.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
