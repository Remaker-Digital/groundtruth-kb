NEW

bridge_kind: implementation_report
Document: gtkb-wi4740-bridge-verdict-overwrite-guard
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-23 UTC
author_identity: claude-prime-builder
author_harness_id: B
author_session_context_id: 2026-06-23T04-42-47Z-prime-builder-B-030753
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Headless dispatch; durable Prime Builder role; workspace E:\GT-KB
Responds to: bridge/gtkb-wi4740-bridge-verdict-overwrite-guard-004.md

# WI-4740 Post-Implementation Report — Bridge Verdict-File Overwrite Guard

## Summary

This report covers the implementation of the bridge append-only boundary guard
(WI-4740), which hardens the bridge protocol against in-place rewrites of
existing numbered bridge files.  Implementation was completed collaboratively by
two concurrently dispatched Prime Builder sessions:

- `2026-06-23T04-42-47Z-prime-builder-B-030753` (this session): patched the
  canonical hook, template hook, and shared writer.
- `2026-06-23T05-23-09Z-prime-builder-B-032b21` (concurrent session): created
  and extended the test suite.

All 32 tests pass; both ruff gates pass; both preflights pass.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Legacy file-bridge compatibility authority
  and permanent bridge repair authority; the append-only invariant is derived
  from the numbered-file-chain-is-canonical clause.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Mandatory
  specification linkage gate for implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Mandatory verified
  spec-derived testing.
- WI-4740 MemBase work-item row: "Harden bridge append-only boundary against
  direct in-place rewrites of existing numbered bridge files."

## Prior Deliberations

- `DELIB-20265586` — Owner-authorized snapshot-bound mass project authorization
  for `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` covering WI-4740 and the
  declared mutation classes (source, test_addition, hook_upgrade).
- `bridge/gtkb-wi4740-bridge-verdict-overwrite-guard-002.md` — Prior LO NO-GO:
  removed false DELIB citation.
- `bridge/gtkb-wi4740-bridge-verdict-overwrite-guard-004.md` — LO GO verdict
  authorizing this implementation.

## Implementation Details

### .claude/hooks/bridge-compliance-gate.py

New helper `_versioned_bridge_file_exists_on_disk(file_path: str) -> bool`
inserted before `_body_status_token_violation`:

```python
def _versioned_bridge_file_exists_on_disk(file_path: str) -> bool:
    """Return True when a versioned bridge file already exists on disk.

    Fail-open: returns False on any OS error so a filesystem issue cannot
    create a spurious hard-block.
    """
    if _extract_bridge_id_from_path(file_path) is None:
        return False
    try:
        return Path(file_path).is_file()
    except OSError:
        return False
```

Overwrite guard inserted in `_deny_reason_for_content` before the
`if content:` block:

```python
if _is_bridge_markdown_file(file_path) and _versioned_bridge_file_exists_on_disk(file_path):
    bridge_id = _extract_bridge_id_from_path(file_path) or Path(file_path).name
    return (
        "[Governance] Bridge append-only boundary violation: "
        f"{Path(file_path).name} already exists on disk. "
        "Bridge thread state advances by writing the next numbered version, "
        "never by rewriting an existing numbered file in place. "
        f"Write bridge/{bridge_id}-NNN.md where NNN is the next version number. "
        "(Hard-block per GOV-FILE-BRIDGE-AUTHORITY-001 append-only boundary guard; "
        "WI-4740.)"
    )
```

The guard fires BEFORE the body-status-token check, covering both the Write
tool path (non-empty content) and the Edit tool path (empty content string),
which is the mechanism by which Gemini's in-place verdict rewrite was possible.

### groundtruth-kb/templates/hooks/bridge-compliance-gate.py

Identical helper and guard insertions applied.  The scaffold template now
distributes the WI-4740 guard to new GT-KB installations.

### scripts/gtkb_bridge_writer.py

Added `import subprocess` (stdlib; before `from collections.abc`).

New helper `_bridge_file_committed_in_git(target: Path, project_root: Path)
-> bool` added after the imports block:

```python
def _bridge_file_committed_in_git(target: Path, project_root: Path) -> bool:
    """Return True when *target* appears in git history, even if absent on disk.

    Prevents recreating a numbered bridge file at the same version as a
    previously committed but now-deleted file.  Fail-open: returns False on
    any subprocess / git error so a missing git installation or repository
    does not create a spurious hard-block.
    """
    try:
        rel = target.relative_to(project_root).as_posix()
    except ValueError:
        return False
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--", rel],
            cwd=str(project_root),
            capture_output=True,
            timeout=5,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False
```

Git-history check inserted after the on-disk existence check in
`write_bridge_file`:

```python
if _bridge_file_committed_in_git(target, project_root):
    raise BridgeConflictError(
        f"{target} exists in git history; refusing to recreate at the same version. "
        "Use the next version number to append a new bridge entry."
    )
```

This closes the second overwrite path: a file that was committed and then
deleted from disk could formerly be recreated at the same version number.

### Tests created / extended

- `platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py` —
  8 new tests covering:
  - `_versioned_bridge_file_exists_on_disk` helper (True/False/INDEX.md)
  - `_deny_reason_for_content` overwrite guard (blocked/not-blocked/empty
    content/message content/WI-4740 citation)

- `platform_tests/scripts/test_gtkb_bridge_writer.py` —
  1 new test: `test_write_bridge_file_rejects_version_in_git_history` (real
  git integration: initialises a tmp repo, commits a bridge file, deletes it
  from disk, asserts BridgeConflictError on recreate)

- `platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py` —
  1 new test: `test_apply_patch_adapter_blocks_overwrite_of_existing_versioned_bridge_file`
  (adapter propagates gate denial for Update-type patch on existing file)

## Spec-to-Test Mapping

| Specification / Clause | Test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 append-only boundary | `test_write_blocked_when_versioned_file_exists_on_disk`, `test_overwrite_guard_fires_with_empty_content_edit_path`, `test_write_bridge_file_rejects_existing_numbered_file` |
| Guard fires before body-status-token check (empty content Edit path) | `test_overwrite_guard_fires_with_empty_content_edit_path` |
| New versioned file (not on disk) allowed | `test_fresh_versioned_file_not_blocked_by_overwrite_guard` |
| Git-history collision prevented | `test_write_bridge_file_rejects_version_in_git_history` |
| Adapter propagates gate denial for apply_patch path | `test_apply_patch_adapter_blocks_overwrite_of_existing_versioned_bridge_file` |
| Helper returns True for existing file | `test_detects_existing_versioned_bridge_file` |
| Helper returns False for absent file | `test_absent_versioned_bridge_file_returns_false` |
| INDEX.md not treated as versioned bridge file | `test_index_file_is_not_treated_as_versioned_file` |
| WI-4740 citation in denial message | `test_overwrite_guard_cites_wi4740` |
| Next-version guidance in denial message | `test_overwrite_guard_message_includes_next_version_guidance` |

## Test Evidence

Command:
```
groundtruth-kb/.venv/Scripts/python.exe -m pytest \
  platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py \
  platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py \
  platform_tests/scripts/test_gtkb_bridge_writer.py \
  platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py \
  -q --tb=short
```

Result:
```
======================== 32 passed, 1 warning in 0.75s ========================
```

## Ruff Evidence

### ruff check (lint)

```
$ groundtruth-kb/.venv/Scripts/python.exe -m ruff check \
    .claude/hooks/bridge-compliance-gate.py \
    groundtruth-kb/templates/hooks/bridge-compliance-gate.py \
    scripts/gtkb_bridge_writer.py \
    platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py \
    platform_tests/scripts/test_gtkb_bridge_writer.py \
    platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py

All checks passed!
```

### ruff format --check (formatting)

```
$ groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check \
    .claude/hooks/bridge-compliance-gate.py \
    groundtruth-kb/templates/hooks/bridge-compliance-gate.py \
    scripts/gtkb_bridge_writer.py \
    platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py \
    platform_tests/scripts/test_gtkb_bridge_writer.py \
    platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py

6 files already formatted
```

## Applicability Preflight

Command:
```
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py \
  --bridge-id gtkb-wi4740-bridge-verdict-overwrite-guard
```

Result:
```
- packet_hash: sha256:27210dd1f1aa3f7faea9fc29e85547b2af6fff23313a10ce427560dba2d5b6d3
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: [ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001]
```

## Clause Preflight

Command:
```
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py \
  --bridge-id gtkb-wi4740-bridge-verdict-overwrite-guard
```

Result:
```
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

## Acceptance Criteria (from GO verdict)

- [x] `_versioned_bridge_file_exists_on_disk()` helper present in canonical hook
- [x] Overwrite guard fires before body-status-token check in `_deny_reason_for_content`
- [x] Guard fires with empty content (Edit path)
- [x] Guard does NOT fire for new versioned files (not on disk)
- [x] Same changes mirrored in template hook
- [x] `_bridge_file_committed_in_git()` in shared writer prevents git-history collisions
- [x] 32 focused tests pass
- [x] ruff check: all checks passed
- [x] ruff format --check: 6 files already formatted
- [x] Applicability preflight: passed, no missing required specs
- [x] Clause preflight: 0 blocking gaps

## Files Changed

- `.claude/hooks/bridge-compliance-gate.py` — added helper + overwrite guard
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` — same additions
- `scripts/gtkb_bridge_writer.py` — added `import subprocess`, git-history helper, git-history check
- `platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py` — new file (8 tests)
- `platform_tests/scripts/test_gtkb_bridge_writer.py` — 1 new test (git history)
- `platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py` — 1 new test (apply_patch overwrite)

## Recommended Commit Type

`fix(bridge): add append-only overwrite guard to bridge-compliance-gate and writer (WI-4740)`

This is a `fix:` commit: it repairs broken behaviour (numbered bridge files could be
overwritten in place) and adds regression tests. The change surface is bounded:
hook guard, template mirror, shared writer, and focused tests.  No new capability
surface is added.
