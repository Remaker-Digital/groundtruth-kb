# NO-GO: F8 Provenance Reconciliation v6 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f8-011.md
**Prior review:** bridge/gtkb-spec-pipeline-f8-010.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F8 v6 resolves the prior type-specific glob dispatch issue for `file_exists`, `json_path`, `grep_absent`, and `count`. The remaining blocker is that the proposed file-target extractor assumes every assertion is a dict, while current GT-KB explicitly allows plain-text human assertions and skips them during assertion execution.

## Findings

### 1. Blocking: plain-text assertions can crash reconciliation

**Claim:** F8 orphan detection matches current assertion-runner behavior by extracting executable file targets and skipping non-executable assertions.

**Evidence:**
- F8 v6 defines `_extract_file_targets(assertion: dict, depth: int = 0)` and immediately calls `assertion.get("type", "")` at bridge/gtkb-spec-pipeline-f8-011.md:49-59.
- F8 v6 calls `_extract_file_targets()` for every parsed assertion in every spec at bridge/gtkb-spec-pipeline-f8-011.md:124-129.
- F8 v6 also recurses into composition children without guarding child type at bridge/gtkb-spec-pipeline-f8-011.md:61-68.
- Current assertion validation treats non-dict plain-text assertions as valid human notes at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertion_schema.py:60-62.
- Current assertion execution skips non-dict assertions instead of crashing at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:551-554.
- Current tests cover a spec with a plain-text assertion and `run_spec_assertions()` handles it successfully at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:244-255.
- The F8 v6 test plan covers typed orphan cases and authority/provenance cases at bridge/gtkb-spec-pipeline-f8-011.md:157-180, but it does not include top-level or nested plain-text/non-dict assertions.

**Risk/impact:** Any spec containing a manual text assertion can raise an AttributeError during reconciliation, aborting the full run before orphan, conflict, or duplicate findings are reported. That is especially risky for a corpus-maintenance feature intended to run across all specs.

**Required action:** Make `_extract_file_targets()` mirror runner skip semantics for non-dict assertions:

```python
if not isinstance(assertion, dict):
    return []
```

Add tests for at least:
1. A top-level plain-text assertion in `assertions_parsed`.
2. A composition assertion whose `assertions` list contains a plain-text child.
3. A non-machine dict child such as `{"type": "visual", ...}` to preserve the existing skip path.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py tests/test_cli.py -q --tb=short` passed in groundtruth-kb: `177 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.

## Conditions For GO

1. Add non-dict assertion guards to the extraction algorithm.
2. Add top-level and nested plain-text assertion tests for reconciliation.
3. Preserve the v6 type-specific dispatch semantics for executable assertions.
