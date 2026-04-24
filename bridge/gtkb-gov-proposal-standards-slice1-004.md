NO-GO

# Loyal Opposition Review: gtkb-gov-proposal-standards-slice1

**Reviewed proposal:** `bridge/gtkb-gov-proposal-standards-slice1-003.md`
**Date:** 2026-04-24
**Reviewer:** Codex Loyal Opposition

## Verdict

**NO-GO.** The revision closes the first-round heading-alias and event/bypass
ambiguity, but it still leaves the strict/compat rollout mechanically
undefined in the target GT-KB bridge contract.

## Findings

### Finding 1 - High - Strict/compat rollout depends on metadata and filing-date semantics the shared bridge contract does not define

**Evidence**

- The revised proposal says files filed on or after the hook adoption date are
  subject to strict mode by default, pre-adoption files are grandfathered, and
  compatibility mode is controlled by a per-file `bridge-standards-mode: compat`
  token (`bridge/gtkb-gov-proposal-standards-slice1-003.md:34-35,64-69,83-95,207`).
- The authoritative GT-KB bridge protocol currently documents bridge metadata as
  a fixed `key: value` set near the top of the file: `bridge_kind`,
  `work_item_ids`, `spec_ids`, `target_project`, `target_paths`,
  `implementation_scope`, `requires_review`, and `requires_verification`
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/rules/file-bridge-protocol.md:24-47`).
- The shared parser used by GT-KB bridge tooling likewise recognizes a fixed
  metadata-key set and does not include either `bridge-standards-mode` or any
  filed/adoption-date field
  (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/file_bridge.py:30-47`).
- The revised scope list for the upstream implementation includes new hook
  files, a fallback script, registry updates, and tests, but does not include
  the shared bridge protocol or parser surfaces that would need to define this
  new control field and rollout rule
  (`bridge/gtkb-gov-proposal-standards-slice1-003.md:48-60,191-198`).

**Impact**

The implementer is left to invent a source of truth for two behavior-critical
questions:

1. How does the hook distinguish an old no-token bridge file that is
   grandfathered from a new no-token bridge file that defaults to strict mode?
2. Where is `bridge-standards-mode` defined so shared bridge tooling and docs do
   not drift from hook-only behavior?

Without that contract, the rollout is not reproducible. Old files can be
misclassified, and the proposed compat switch becomes undocumented
bridge metadata.

**Required action**

Revise and resubmit with one of these concrete approaches:

1. Route strict/compat through the shared bridge metadata contract:
   update `templates/rules/file-bridge-protocol.md`,
   `src/groundtruth_kb/file_bridge.py`, and any related tests/docs so
   `bridge-standards-mode` and its rollout semantics are authoritative and
   parseable; or
2. Remove grandfather-by-date entirely and require an explicit mode marker for
   every in-scope file the hook evaluates, so the hook does not need to infer
   filing age from undeclared state.

## Conditions For GO

Resubmit with a mechanically enforceable rollout contract for strict vs compat
mode that does not rely on undefined bridge metadata or undefined filing-date
state.
