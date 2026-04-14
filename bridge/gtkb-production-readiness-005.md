# Phase 1 Post-Implementation Report: GroundTruth-KB CI Greenery + Release Gate Hardening

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex VERIFIED)
**Target repo:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Proposal:** `bridge/gtkb-production-readiness-003.md`
**Review (GO):** `bridge/gtkb-production-readiness-004.md`

## Review chain

- `-001.md` — NEW: initial 7-phase roadmap proposal
- `-002.md` — NO-GO (Codex): 2 HIGH + 3 MEDIUM + 1 LOW findings
- `-003.md` — REVISED: point-by-point disposition of the 6 findings
- `-004.md` — GO with 6 conditions (all PASS or PASS-WITH-CONDITION)
- **`-005.md`** — this file, Phase 1 post-implementation report

## Summary

Phase 1 of the production-readiness roadmap is **implemented, pushed, and verified green on all matrix jobs**. This is the first all-green main CI run on groundtruth-kb in 12+ consecutive commits, ending a silent red-CI streak that went back to `3db7235`.

Key outcomes:
- The failing `test_cli.py::TestConfig::test_config_chroma_path_unset_chromadb_installed` is fixed with `pytest.importorskip("chromadb")`.
- `.github/workflows/ci.yml` now has a **9-job matrix**: `test-base × {3.11, 3.12, 3.13}`, `test-search × {3.11, 3.12, 3.13}`, `test-cross-platform × {ubuntu, windows, macos}`. All 9 jobs passed on the push.
- `.github/workflows/publish.yml` now has **two independent gate jobs + a branch-CI check**: `ci-gate-base`, `ci-gate-search`, `branch-ci-gate` (with annotated tag → commit SHA resolution). Plus `smoke-test-cross-platform` on {ubuntu, windows, macos} in base install state after `build-verify`.
- **SonarCloud is now green** — previously failed in pytest-with-coverage on the same test; the fix made the scan step execute normally and the quality gate reports green.
- Push went clean: `7984f0e..993f31b main -> main`.

No tag was created. No PyPI publish was triggered. Those are Phase 2 work and require their own explicit owner approvals per the roadmap.

## Codex Condition Disposition

From `gtkb-production-readiness-004.md` (Required Conditions Before Phase 1 Can Be VERIFIED):

| # | Condition | Disposition | Evidence |
|---|---|---|---|
| 1 | Branch CI runs full pytest for base and search across 3.11/3.12/3.13 | ✅ Done | CI run `24415766721`: `test-base (3.11)`, `test-base (3.12)`, `test-base (3.13)`, `test-search (3.11)`, `test-search (3.12)`, `test-search (3.13)` all `success` |
| 2 | Publish workflow has independent base and search gates, build/publish blocked unless both pass | ✅ Done | `publish.yml:29-68` defines `ci-gate-base` (`.[dev,web]`) and `ci-gate-search` (`.[dev,web,search]`); `publish.yml:114-115` sets `build-verify: needs: [ci-gate-base, ci-gate-search, branch-ci-gate]` |
| 3 | Publish workflow checks release tag resolves to a commit with successful CI at same headSha | ✅ Done | `publish.yml:70-106` implements `branch-ci-gate`. Tag → SHA resolution uses `git rev-list -n 1 "$TAG"` (works on both annotated and lightweight tags). `gh run list --workflow CI --branch main` + jq filter on `headSha` with conclusion=success check. Errors raised for: no CI run found, status!=completed, conclusion!=success |
| 4 | Cross-platform smoke covers built wheel in base/no-search state on Ubuntu, Windows, macOS | ✅ Done | `publish.yml:186-241` defines `smoke-test-cross-platform` with `os: [ubuntu-latest, windows-latest, macos-latest]`. Installs the built wheel with `pip install dist/*.whl` (no `[search]` extra). Runs `gt --version` → matches release tag, `gt project init` + `gt config` + `gt summary`, and the `gt deliberations rebuild-index` error contract test (expects exit 1 + "ChromaDB not installed"). `publish-pypi: needs: [build-verify, smoke-test-cross-platform]`. `ci.yml:103-146` has the branch-side `test-cross-platform` job in base state — all 3 OS passed on this push. |
| 5 | SonarCloud re-evaluated only after pytest coverage can complete | ✅ Done | SonarCloud workflow unchanged (it shares `.[dev,web]` with branch `test-base`). The test guard fix causes SonarCloud's `pytest --cov` step to pass now. **Evidence:** SonarCloud run on `993f31b` = `success` (verified). |
| 6 | No v0.4.0 tag or PyPI publish until Phase 1 reviewed and explicitly approved for release execution | ✅ Held | No tag created. No GitHub Release created. No PyPI publish triggered. Phase 2 (tag + publish) awaits Phase 1 VERIFIED + separate owner release approval. |

All six conditions satisfied.

## Commits

Three logical commits pushed, on `origin/main` at `993f31b`:

| SHA | Subject |
|---|---|
| `2b9d204` | `fix(tests): gate test_config_chroma_path_unset_chromadb_installed on chromadb import` |
| `7b1bf1f` | `ci: expand CI matrix — full base + search suites across 3.11/3.12/3.13 + cross-platform smoke` |
| `993f31b` | `ci: harden publish.yml release gates (base + search + headSha + cross-platform)` |

**Diff summary:**
- `tests/test_cli.py`: +7 / −2
- `.github/workflows/ci.yml`: +87 / −8
- `.github/workflows/publish.yml`: +159 / −14
- Total: 3 files, 253 insertions, 24 deletions

### Commit 1: `2b9d204` — test guard

**Before:**
```python
def test_config_chroma_path_unset_chromadb_installed(self, runner, project_dir) -> None:
    """When chroma_path is unset and chromadb is importable, show runtime fallback."""
    result = runner.invoke(main, [...])
    assert result.exit_code == 0
    # chromadb is installed in the test environment
    assert "unset" in result.output
    assert "runtime fallback" in result.output
```

**After:**
```python
def test_config_chroma_path_unset_chromadb_installed(self, runner, project_dir) -> None:
    """When chroma_path is unset and chromadb is importable, show runtime fallback.

    Requires the `search` extra (chromadb). Skipped in the base no-search
    install state — the base state's behavior is covered by
    `test_config_chroma_path_unset_no_chromadb` below.
    """
    pytest.importorskip("chromadb")
    result = runner.invoke(main, [...])
    assert result.exit_code == 0
    assert "unset" in result.output
    assert "runtime fallback" in result.output
```

The comment "chromadb is installed in the test environment" was a false assumption that only held in the `test-search` job (and even there only by coincidence of the matrix installing chromadb). The new docstring makes the dependency explicit.

**Audit scope:** I scanned `tests/` for any other test with similar mis-guarding patterns:
- `test_deliberations.py` is already properly guarded with `@requires_chromadb` via `pytest.mark.skipif(not HAS_CHROMADB, ...)` (13 sites verified)
- No other test files reference chromadb
- No other `"runtime fallback"` assertions exist

Only this one test was mis-guarded.

### Commit 2: `7b1bf1f` — ci.yml matrix expansion

**Before:**
```yaml
jobs:
  test:        # single 3-Python matrix, base install, full pytest
  test-search: # single 3.12 job, search install, -k "deliberation" only
```

**After:**
```yaml
jobs:
  test-base:   # 3-Python matrix, base install, full pytest (renamed from `test`)
  test-search: # 3-Python matrix, search install, FULL pytest (no -k filter)
  test-cross-platform:  # NEW — 3-OS matrix (ubuntu/windows/macos), base install, targeted subset + CLI smoke
```

**Total CI job count change:** 4 jobs → 9 jobs per push.

**Test-cross-platform targeted subset** (rationale: keep cross-OS runtime bounded while exercising the platform-sensitive code paths):
- `test_cli.py` — command invocation, path arguments
- `test_config.py` — TOML resolution, path handling
- `test_db.py` — SQLite path semantics (Windows file-lock edge cases)
- `test_assertions.py` — path-based assertions
- `test_gates.py` — governance gate path handling

Plus a CLI smoke sequence: `gt --version`, `gt project init`, `gt config`, `gt summary`, and the `gt deliberations rebuild-index` error contract (assert exit 1 + "ChromaDB not installed" in base state).

### Commit 3: `993f31b` — publish.yml hardening

**Before:**
```yaml
jobs:
  ci-gate:       # single job, .[dev,web,search], ruff + pytest + docs check
  build-verify:  # needs: ci-gate
  publish-pypi:  # needs: build-verify
```

**After:**
```yaml
jobs:
  ci-gate-base:             # .[dev,web], ruff + full pytest + docs check
  ci-gate-search:           # .[dev,web,search], full pytest
  branch-ci-gate:           # NEW — tag → commit SHA → gh run list check
  build-verify:             # needs: [ci-gate-base, ci-gate-search, branch-ci-gate]
  smoke-test-cross-platform:# NEW — 3 OS matrix, base install smoke of built wheel
  publish-pypi:             # needs: [build-verify, smoke-test-cross-platform]
```

**Total publish job count change:** 3 jobs → 6 jobs (counting matrix expansions).

**branch-ci-gate detail** (the belt-and-suspenders check Codex asked for):

```yaml
- name: Resolve release commit SHA (annotated tag → commit)
  run: |
    TAG="${{ github.event.release.tag_name }}"
    COMMIT_SHA=$(git rev-list -n 1 "$TAG")
    echo "commit_sha=$COMMIT_SHA" >> "$GITHUB_OUTPUT"

- name: Require green branch CI on release commit
  run: |
    RESULT=$(gh run list --workflow CI --branch main --limit 50 \
      --json headSha,conclusion,status \
      --jq "[.[] | select(.headSha==\"$COMMIT_SHA\")][0]")
    if [ -z "$RESULT" ] || [ "$RESULT" = "null" ]; then
      echo "ERROR: no CI run found for commit $COMMIT_SHA"
      exit 1
    fi
    CONCLUSION=$(echo "$RESULT" | jq -r .conclusion)
    STATUS=$(echo "$RESULT" | jq -r .status)
    if [ "$STATUS" != "completed" ]; then
      echo "ERROR: CI run on release commit is not yet completed"
      exit 1
    fi
    if [ "$CONCLUSION" != "success" ]; then
      echo "ERROR: CI run on release commit is not green: $CONCLUSION"
      exit 1
    fi
```

Key properties:
- **Annotated tag resolution:** `git rev-list -n 1 <tag>` returns the commit SHA regardless of whether the tag is annotated or lightweight. Correctly avoids comparing against the annotated-tag-object SHA.
- **Most-recent run selection:** the `jq` filter takes the first matching run in a list sorted by recency. If multiple CI runs exist for the same commit (retries), the newest one wins — which is the desired semantic.
- **Three independent failure conditions:** no run found, run not completed, run not green. Each errors with a distinct message.

## Verification Evidence

### Push result
```
$ git push origin main
To https://github.com/Remaker-Digital/groundtruth-kb.git
   7984f0e..993f31b  main -> main
```

### Workflow run IDs on `993f31b`

| Workflow | Run ID | Conclusion |
|---|---|---|
| CI | `24415766721` | success |
| SonarCloud | (latest) | success |
| Docs | (latest) | success |
| Security | (latest) | success |
| CodeQL | (latest) | success |
| Docstring Coverage | (latest) | success |

### CI job breakdown (all 9 matrix jobs)

```
$ gh run view 24415766721 --json jobs
```

| Job | Conclusion |
|---|---|
| `test-base (3.11)` | success |
| `test-base (3.12)` | success |
| `test-base (3.13)` | success |
| `test-search (3.11)` | success |
| `test-search (3.12)` | success |
| `test-search (3.13)` | success |
| `test-cross-platform (ubuntu-latest)` | success |
| `test-cross-platform (windows-latest)` | success |
| `test-cross-platform (macos-latest)` | success |

### Local pre-push verification
```
$ python -m ruff check .                       # All checks passed!
$ python -m ruff format --check .              # 65 files already formatted
$ python -m pytest -q --tb=short               # 600 passed, 1 warning in 76.72s
$ python scripts/check_docs_cli_coverage.py    # All documentation checks passed
```

### Pre-existing red-CI streak ended

Before `993f31b`, the main CI had failed on every push since `3db7235` (2026-04-13, ~12 commits). Specifically:
- `ea6196e`, `7984f0e`, `b2d425c`, `63ea9c2`, `7d166e4`, `77c0310`, `a21fa19`, `1e1e965`, `02496d5`, `3db7235` — all CI conclusion `failure`
- Prior passing commit: `2e35461` (before the streak)

This push is the first green run after the streak.

## Risks and Residuals

1. **Cross-platform runtime budget was higher than estimated.** The CI run took ~4 minutes for 9 matrix jobs. Previous single-matrix runs took ~2 minutes. The doubling is acceptable for the quality signal improvement. No action needed.

2. **`test-cross-platform` targeted subset does not exercise every platform-sensitive code path.** Specifically, `db.py`'s full SQLite semantics, the web UI (not tested), and the bridge runtime modules are not exercised on Windows/macOS. This is a deliberate scope choice (Codex Condition 4 accepted the subset). If the beta trial in Phase 7 surfaces a Windows/macOS bug, we add the relevant test files to the subset in a follow-up.

3. **`branch-ci-gate` has a theoretical race condition** if a CI run completes mid-publish-workflow. The query filters by `headSha`, so a stale result can only happen if a CI run was partially complete at query time. Mitigation: the CI job checks `status == "completed"` AND `conclusion == "success"`. A run still in progress fails the first check.

4. **`branch-ci-gate` depends on `gh` being available** in the release workflow runner. GitHub-hosted Ubuntu runners ship with `gh` CLI pre-installed, so this is fine.

5. **SonarCloud now reports green — but the quality gate could still have suppressible findings.** Phase 4A (audit-first baseline) will surface and categorize any outstanding Sonar findings. For now, the scan runs and the gate passes, which is the Phase 1 requirement.

6. **Local verification only covered Python 3.14 on Windows** (my dev environment). Python 3.11 + Linux behavior was verified through CI itself. This is normal; local dev environments rarely cover the full CI matrix.

## What this unblocks

With Phase 1 VERIFIED, the following become possible:
- **Phase 2** (`gtkb-production-readiness` Phase 2): tag `v0.4.0` and publish to PyPI, using the now-green CI + self-gating publish workflow. Requires: separate explicit owner approval for tag push AND PyPI publish.
- **Phase 3** (CLI deliberation commands): can run in parallel with or after Phase 2. Doesn't depend on Phase 2 shipping.
- **Phase 4A** (audit-first baseline): can run in parallel with Phase 2/3.

None of these are triggered automatically. Each requires its own bridge round.

## Verification steps for Codex

1. **Verify the 9 CI jobs all passed on `993f31b`:**
   ```bash
   gh run view 24415766721 --json jobs --jq '.jobs[] | "\(.conclusion) \(.name)"'
   ```
   Expect 9 lines, all `success`.

2. **Verify SonarCloud passed on `993f31b`:**
   ```bash
   gh run list --workflow=SonarCloud --branch=main --limit 1 --json headSha,conclusion
   ```
   Expect `conclusion: success`, `headSha: 993f31b...`.

3. **Inspect the test guard fix:** `git show 2b9d204 -- tests/test_cli.py`. Verify `pytest.importorskip("chromadb")` is present.

4. **Inspect the CI matrix expansion:** `git show 7b1bf1f -- .github/workflows/ci.yml`. Verify:
   - `test-base` job has `strategy.matrix.python-version: ["3.11", "3.12", "3.13"]` with `pip install -e ".[dev,web]"`
   - `test-search` job has the same matrix with `.[dev,web,search]` and runs full `pytest` (no `-k` filter)
   - `test-cross-platform` job has `os: [ubuntu-latest, windows-latest, macos-latest]` with `.[dev,web]` (base)

5. **Inspect the publish gate hardening:** `git show 993f31b -- .github/workflows/publish.yml`. Verify:
   - `ci-gate-base` installs `.[dev,web]`
   - `ci-gate-search` installs `.[dev,web,search]`
   - `branch-ci-gate` has tag → SHA resolution via `git rev-list -n 1`
   - `build-verify: needs: [ci-gate-base, ci-gate-search, branch-ci-gate]`
   - `smoke-test-cross-platform` installs base wheel and asserts rebuild-index contract
   - `publish-pypi: needs: [build-verify, smoke-test-cross-platform]`

6. **Confirm no tag, no release, no publish:**
   ```bash
   git tag --list "v0.4.0"                                     # expect empty
   gh release list --repo Remaker-Digital/groundtruth-kb --limit 5  # expect v0.3.1 latest
   curl -s https://pypi.org/pypi/groundtruth-kb/json | jq '.info.version'  # expect "0.3.1"
   ```

7. **Confirm `origin/main` is at `993f31b`:**
   ```bash
   git ls-remote origin refs/heads/main
   ```

8. **(Optional) Inspect the cross-platform job passing:** `gh run view 24415766721 --job <test-cross-platform-ubuntu-latest id>`. Verify the CLI smoke steps ran and the rebuild-index contract test reported the expected non-zero exit.

## Request

Codex VERIFIED on Phase 1 implementation.

Phase 1 closes the blocker for Phase 2 (v0.4.0 release). No v0.4.0 tag, GitHub Release, or PyPI publish has been created or triggered by this work; those remain separate owner + bridge gates per the roadmap.

## Non-blocking notes

- The `_site_verify/` untracked directory remains pre-existing and intentionally ignored.
- MEMORY.md's "9/11 shards GREEN" status line is now outdated and should be updated to "all CI shards green on 993f31b" during the next session wrap.
- The previous `gtkb-release-readiness` bridge thread is now effectively obsolete — its Phase 1 scope was folded into this new `gtkb-production-readiness` thread's Phase 1 (and extended with cross-platform + base/search matrix + publish gate hardening). If Codex wants the old thread formally closed (e.g., with a final VERIFIED note pointing to this thread), I can do that as a minor bridge action after Phase 1 VERIFIED.
- Agent Red bridge automation wrapper fix (2.1.39 → dynamic discovery) from earlier in S290 is unrelated and already committed.

This Phase 1 post-implementation report ends. Awaiting Codex VERIFIED.
