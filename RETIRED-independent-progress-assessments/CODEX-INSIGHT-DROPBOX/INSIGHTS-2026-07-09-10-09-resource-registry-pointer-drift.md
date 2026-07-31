# Loyal Opposition Advisory - Resource Registry Pointer Drift and CI Defect

**Author:** Loyal Opposition (Antigravity, harness C)  
**Date:** 2026-07-09 UTC  
**Subject:** `Resource Registry Pointer Drift and CI Defect (Missing Pointer file)`  
**Severity:** **P1** (Causes CI test suite failure in platform_tests)

---

## 1. Observation

During a structural integrity audit of the repository, the following failures and warnings were observed:

1. Running `pytest platform_tests/scripts/test_project_resource_aliases.py` fails with two errors:
   - `test_governed_registry_is_valid_and_pointer_is_not_competing_registry` asserts `module.validate_pointer() == []` which fails with `pointer file missing: E:\GT-KB\.claude\rules\project-resource-aliases.toml`.
   - `test_cli_resolves_json_alias` asserts that `resolve_project_resource.py repo --json` returns exit code 0, but it fails with exit code 1 with `pointer file missing`.

2. Running `gt status` reports a warning regarding the resource registry:
   ```text
   - WARN resource-registry: 11 resource(s); unverified canonical=1; separate-project=4; pointer=missing
   ```

3. Git log shows `.claude/rules/project-resource-aliases.toml` was never committed to version control.

4. `.gitignore` has a blanket ignore on `.claude/*` and lacks a negation entry for `project-resource-aliases.toml`, meaning the pointer file was ignored and subsequently lost during a clean/reset or clone.

---

## 2. Deficiency Rationale

- **Control Gap**: The absence of the pointer file `.claude/rules/project-resource-aliases.toml` causes immediate failures in two test cases in `platform_tests/scripts/test_project_resource_aliases.py`.
- **Tooling Breakage**: The `resolve_project_resource.py` script exits with status code 1 when the pointer is missing, breaking any GT-KB tool workflows or hooks that resolve external resource aliases.
- **Git Ignore Oversights**: If a required startup/pointer file is not negation-included in `.gitignore`, it will not survive clean checkouts, leading to recurring environment-setup defects.

---

## 3. Proposed Solution/Enhancement

1. **Restore the Pointer File**: Create `.claude/rules/project-resource-aliases.toml` with the following content:
   ```toml
   schema_version = 1
   registry_path = "config/agent-control/project-resource-aliases.toml"
   ```
2. **Update Gitignore Rules**: Add a negation rule to `.gitignore` to track the pointer file:
   ```gitignore
   # Gitignore entry
   !.claude/rules/project-resource-aliases.toml
   ```
3. **Verify and Clean Run**: Run `pytest platform_tests/scripts/test_project_resource_aliases.py` and `gt status` to verify resolution.

---

## 4. Option Rationale

- **Why this approach**: Restoring the pointer is required by the current design of `resolve_project_resource.py` and `test_project_resource_aliases.py` which rejects a competing registry under `.claude/rules/` while checking for the presence of the pointer. Tracking the pointer in version control ensures environment consistency and avoids test suite regressions in future checkouts.

---

## Prime Builder Implementation Context

- **Preconditions**: This is a read-only session for Loyal Opposition. Prime Builder should execute this restoration.
- **Target Files**:
  - [`.gitignore`](file:///e:/GT-KB/.gitignore)
  - [`.claude/rules/project-resource-aliases.toml`](file:///e:/GT-KB/.claude/rules/project-resource-aliases.toml)
- **Implementation Sequence**:
  1. Add `!.claude/rules/project-resource-aliases.toml` to the AI Assistant/Rules section of `.gitignore`.
  2. Create the file `.claude/rules/project-resource-aliases.toml` with the pointer TOML content.
  3. Run the test suite: `pytest platform_tests/scripts/test_project_resource_aliases.py`.
  4. Run `gt status --component resource-registry` and verify pointer reports `delegated`.

---

## Advisory Report Mode

**Disposition Recommendation**: `adopt`

### Required Prime Builder Owner-Grilling Gate

- **Question**: Should the pointer file `.claude/rules/project-resource-aliases.toml` be committed to version control, or should it be generated dynamically during startup?
- **Options**:
  - **Option A (Recommended)**: Un-ignore it in `.gitignore` and commit it.
  - **Option B**: Keep it ignored and modify startup hooks to write it dynamically if missing.
- **Tradeoffs**:
  - *Option A*: Simple, clean, zero runtime overhead. The file is static and acts as a standard system pointer.
  - *Option B*: Avoids committing files to `.claude/rules/`, but adds complexity and could lead to race conditions if multiple harnesses try to write/verify it concurrently.
- **Durable Outcome**: Committing the pointer immediately satisfies the CI tests on clean checkouts.

---

Skills applied: loyal-opposition-report
