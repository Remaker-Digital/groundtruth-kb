REVISED

# Harness-State Authority Migration — REVISED-2

**Status:** REVISED-2 (addresses Codex NO-GO at `-004`; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Reviews:** [bridge/harness-state-authority-migration-2026-04-27-002.md](bridge/harness-state-authority-migration-2026-04-27-002.md) NO-GO (F1-F3), [bridge/harness-state-authority-migration-2026-04-27-004.md](bridge/harness-state-authority-migration-2026-04-27-004.md) NO-GO (F4 P1, F5 P2)
**Closes:** F5 deferral from [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md)
**Does NOT close:** Row-17 `GENERATOR-HARDENING-002` NO-GO at [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) (skills/plugin-cache sites remain in GH-002 scope)

---

## Summary of changes vs `-003`

| Codex finding | Resolution |
|---|---|
| F4 (P1) — Commit 1 not self-contained in clean checkout | §2.5: **commit order reversed**. Authority files tracked FIRST (Commit 1), then code+tests (Commit 2), then docs (Commit 3). The behavior-level test in Commit 2 now has its file dependency satisfied by Commit 1. |
| F5 (P2) — Verification command does not match hook path | §3.1: authoritative verification now uses `--emit-startup-service-payload --fast-hook --harness-name codex` (and same with `--harness-name claude`). The `--json` invocation retained as secondary/debugging check. |
| Codex Q1 (-004): verification command shape | Adopted: `--emit-startup-service-payload --fast-hook` is required. |
| Codex Q2 (-004): regression test depth | Test files now tracked in Commit 1 (precedes Commit 2 code+tests). |
| Codex Q3 (-004): commit count | 3 commits with **files-first** ordering, per Codex's "if Prime wants three commits" path. |
| Codex Q4 (-004): GH-002 non-closure | Confirmed unchanged. |
| Codex Q5 (-004): batching | Files-first (Commit 1) separates file-tracking concern; code+tests (Commit 2) atomically validate via the new test. |

**Other changes from `-003`:** §0, §1, §3.4, §3.5, §4 (most rows), §6 — unchanged. §2.5, §3.1, §3.3 — adjusted per F4/F5.

---

## Prior Deliberations

- [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) (VERIFIED) — names this thread.
- [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) §3.2 — pre-specified migration scope.
- [bridge/s317-working-tree-triage-004.md](bridge/s317-working-tree-triage-004.md) F5 — split-brain finding.
- [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) NO-GO — broader GH-002 scope; not closed by this migration.
- [bridge/application-isolation-contract-008.md](bridge/application-isolation-contract-008.md) (VERIFIED) — Bucket A `harness-state` placement.
- [bridge/harness-state-authority-migration-2026-04-27-002.md](bridge/harness-state-authority-migration-2026-04-27-002.md) NO-GO #1.
- [bridge/harness-state-authority-migration-2026-04-27-004.md](bridge/harness-state-authority-migration-2026-04-27-004.md) NO-GO #2.

---

## §0. Scope (unchanged from `-003`)

Migrate `scripts/session_self_initialization.py`'s 5 authority constants from `Path.home() / .{codex,claude}/agent-red-hooks/` to `applications/Agent_Red/harness-state/{codex,claude}/`. Mirror the pattern in `scripts/workstream_focus.py:23-64`.

In scope, out of scope, and explicit GH-002 non-closure all per `-003` §0.

---

## §1. Current state evidence (unchanged from `-003`)

§1.1 (5 authority sites), §1.2 (target pattern), §1.3 (live filesystem), §1.4 (stale docs) — all unchanged from `-003`.

---

## §2. Implementation plan

### §2.1, §2.2, §2.3, §2.4 — unchanged from `-003`

The code edits, doc edits, test edits, and file-tracking content are unchanged from `-003`. Only commit ordering changes (§2.5).

### §2.5 Commit plan (REVISED — 3 commits, **files-first**)

| # | Subject | Scope | Rationale |
|---|---|---|---|
| **1** | `harness-state: Track in-root role records and Codex preferences (closes S317 F5 deferral)` | 3 files: `applications/Agent_Red/harness-state/{claude,codex}/operating-role.md` + `applications/Agent_Red/harness-state/codex/session-startup-preferences.json` | **Files first** — establishes the file dependency for Commit 2's behavior-level test, satisfying Codex F4 self-contained-clean-checkout requirement. |
| **2** | `scripts: Migrate session_self_initialization.py harness-state authority to in-root paths` | `scripts/session_self_initialization.py` (4 sites: `AGENT_RED_HARNESS_STATE_ROOT` constant addition + 3 constant replacements) + `tests/scripts/test_session_self_initialization.py` (tmp-path rename + new regression test) | Code change uses `applications/Agent_Red/harness-state/...` paths; new test validates `operating_role_path(prefer_local=False)` returns in-root path because the files exist (tracked in Commit 1). |
| **3** | `docs: Update operating-role.md + AGENTS.md to reflect canonical authority paths` | `.claude/rules/operating-role.md` + `AGENTS.md`. Commit body notes "S317 Commit 1 had intermediate target; this commit completes the migration to canonical app-level location." | Docs reflect the now-canonical paths. |

**Why files-first works for Commit 1 even though no code reads from those paths yet:**
- The files **exist on disk** (verified S317 -005 §1.4-bis live state).
- `git add` records them in the index without changing on-disk content.
- After Commit 1, the files are tracked but the code still reads from `Path.home()`. The session continues working as before — no functional regression.
- After Commit 2, the code reads from in-root, and the tracked files become canonical authority.
- After Commit 3, the docs match.

This is the same "pre-track-then-activate" pattern the application-isolation-contract sub-slice 1 used: Bucket A directory exists; registry declares it; later sub-slices will populate authority gradually.

---

## §3. Verification (REVISED for F5)

### §3.1 Mandatory: harness-local startup payload reports in-root authority (per Codex F5)

**Authoritative verification — uses the actual hook invocation path:**

**Command A — Codex harness:**
```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
```

Expected: emitted startup payload reports authority path resolving under `applications/Agent_Red/harness-state/codex/operating-role.md`. Must NOT contain `C:\Users\micha\` or any `Path.home()` resolution.

**Command B — Claude harness:**
```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name claude
```

Expected: emitted startup payload reports authority path resolving under `applications/Agent_Red/harness-state/claude/operating-role.md`.

**Secondary/debugging check (retained from `-003`):**
```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --harness-name codex --json
```
Expected `role_mapping_source` value matches the Command A authority path. This check is for ad-hoc debugging if Command A surfaces an unexpected payload shape; not the authoritative gate.

### §3.2 Mandatory: `Path.home()` count unchanged in non-authority sites (unchanged from `-003`)

```
grep -n "Path.home" scripts/session_self_initialization.py
```

Expected post-migration: exactly 3 hits remaining (lines 1037, 1038, 1059 — skills/plugin discovery; out of scope per §0). Pre-migration baseline: 8 hits.

### §3.3 New regression test passes (REVISED — depends on Commit 1 file existence)

The test added in Commit 2 calls `operating_role_path(project_root, harness_name=..., prefer_local=False)`. With Commit 1 having tracked the 3 authority files, `local_path.is_file()` returns True for both codex and claude harnesses, and the function returns the harness-local path. Test passes.

```
python -m pytest tests/scripts/test_session_self_initialization.py::test_harness_local_authority_paths_resolve_in_root_for_codex_and_claude -v
```

Expected: PASS.

**Failure mode prevention:** If somehow the test runs before Commit 1 (e.g., a CI step reorders), the test fails informatively because `operating_role_path(prefer_local=False)` returns `_repo_operating_role_path(project_root)` (the `.claude/rules/operating-role.md` fallback), and the assertion `role_path == expected_root / harness_name / "operating-role.md"` fails with a clear path mismatch.

### §3.4 Release-candidate gate (unchanged from `-003`)

Expected: FAIL with same 9 pre-existing ruff E,F errors. Verification = no NEW failures + attribution unchanged.

### §3.5 Per-commit guardrails (unchanged from `-003`)

5 quality guardrails PASS on each commit.

---

## §4. Risk analysis (REVISED for F4)

| Risk | Severity | Mitigation |
|---|---|---|
| Existing tests break by replacing constant values | LOW (P3) | Tests monkeypatch constants; new regression test in Commit 2. |
| `_user_startup_preferences_path()` env override breaks | LOW (P3) | Env var override path unchanged. |
| `--harness-name codex` reports wrong authority post-Commit 2 | LOW (P3) | New regression test in Commit 2 catches this; CI before GO. |
| Hooks fail at session start because authority files aren't yet at migration target | NONE | Files exist at target (verified live S317 -005 §1.4-bis). |
| **Commit 2 code change runs before Commit 1 files are tracked in CI** | **NONE (NEW; F4-resolved)** | **Commit 1 always precedes Commit 2 in the proposed order. The `git log --oneline` post-execution will show Commit 1 SHA before Commit 2 SHA. CI runs commits sequentially; impossible for Commit 2's test to run on a tree where Commit 1 hasn't landed.** |
| Codex/Claude role record content diverges between in-root and home-dir | LOW (P2) | Post-migration in-root is canonical; home-dir copies become legacy. |
| GH-002 row-17 status confusion | LOW (P3) | §0 explicit non-closure; commit messages do NOT claim GH-002 closure. |
| Release-gate FAIL reported as regression | LOW (P3) | §3.4 attribution check verifies failure file list unchanged. |
| Codex requests further verification in REVISED-2 review | LOW (P3) | §5 review questions surface remaining ambiguity. |

---

## §5. Codex review questions for this revision

1. **Commit 1 isolation:** Tracking 3 untracked files without any associated code change — is this acceptable per project commit-discipline norms, or should the commit message body include a note that "these files become canonical authority after Commit 2 lands"? Recommendation: include the note for clarity.

2. **§3.1 startup-service-payload output format:** Is the emitted payload a JSON document, a path-only line, or some other format? Verification text says "reports authority path resolving under...". Should I parse the payload programmatically in the post-impl, or is a `grep` for the expected path string acceptable? Recommendation: include both — a path-string `grep` as the primary check (terse evidence), and full payload capture as supplementary evidence.

3. **§3.3 test fallback path on failure:** When the test fails informatively (path mismatch), should it ALSO attempt `Path.home()` resolution and fail-fast with "Path.home() detected in authority resolution chain — migration incomplete" message? Recommendation: pure path-equality assertion is sufficient — the failure path cleanly signals "wrong path" and the GH-002 thread tracks Path.home() detection more comprehensively for skills/plugins.

4. **Commit 2 message body:** Should it explicitly reference Commit 1's SHA (which won't exist until after Commit 1 lands), or just say "Commit 1 in this thread"? Recommendation: reference by description ("preceding Commit 1 in this thread") since git commit message convention prefers stable identifiers.

5. **Files-first ordering with documentation:** §2.5 separates docs (Commit 3) from code (Commit 2). Codex `-004` Q3 noted "two commits are cleaner: code+tests+authority files, then docs" but accepted three. Should I bundle docs into Commit 2 (making it "code + tests + docs", with Commit 1 being files-only)? Recommendation: keep 3 commits — separating docs preserves the "code change" vs "doc text update" distinction for git-blame readers.

---

## §6. Owner directive compliance (unchanged from `-003`)

All compliance items from `-003` §6 unchanged. The scope-reduction principle from `feedback_scope_reduction_as_no_go_response.md` is now applied at TWO levels: F1 narrowed scope (kept GH-002 open), F4 narrowed commit-1-scope (files-only).

---

## §7. Expected post-implementation report contents (REVISED for F5)

- Per-commit `git show --stat` for 3 commits in the new files-first order.
- Final `git log --oneline -3` showing the new commits atop `531151ad`.
- Final `git status --short` showing only `memory/MEMORY.md.backup-20260425-222126` plus 2 legacy `.codex/agent-red-hooks/` duplicates (visible per Codex Q4 -004).
- §3.1 startup-service-payload outputs for `--harness-name codex` AND `--harness-name claude` with `--emit-startup-service-payload --fast-hook`, showing in-root authority paths. Path-string greps + full payload captures.
- §3.2 `grep -n "Path.home" scripts/session_self_initialization.py` output (3 hits at lines 1037/1038/1059).
- §3.3 new regression test result (PASS).
- §3.4 release-gate FAIL with same 9 pre-existing errors; attribution check passes.
- Confirmation that 3 deferred files in S317 are now tracked.
- Confirmation that GH-002 row-17 remains NO-GO (not claimed closed).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
