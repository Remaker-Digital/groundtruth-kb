ADVISORY

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: interactive-codex-disable-stale-marker-for-attribution
created_at: 2026-07-04T16:11:00Z
bridge_kind: coordination_note
work_item: WI-4455
project: null

# WI-4455 Decision Packet: platform_tests spec-before-code coverage

## Claim

WI-4455 remains a real governance-design gap, but its current physical urgency
has changed since the original report. The active root hook at
`.claude/hooks/spec-before-code.py` is now a recovery stub that exits 0, so the
reported advisory miss is not currently firing in this checkout. The product
template hook at `groundtruth-kb/templates/hooks/spec-before-code.py` still
implements source_paths-only coverage, and managed artifact registration still
scaffolds the hook for dual-agent profiles. The gap therefore remains relevant
before spec-before-code enforcement is restored or scaffolded, but it should be
handled as a policy choice rather than an immediate source edit.

Recommended owner choice: Option A, bridge-derived coverage for platform tests,
with exact bridge and test-file evidence.

## Evidence

- `gt backlog show WI-4455 --json` shows WI-4455 is still open, P0,
  backlogged, unapproved, and has no project assignment or bridge thread. Its
  description states that `platform_tests/` files are spec-linked through bridge
  proposals and spec-derived verification plans rather than per-file
  `source_paths`.
- `.claude/hooks/spec-before-code.py` is a recovery stub. It emits nothing and
  exits 0, with comments tying replacement/removal to WI-4449 and backlog
  triage.
- `groundtruth-kb/templates/hooks/spec-before-code.py` still queries only
  `specifications.source_paths` and emits the advisory
  "No specification found covering <target>" when no `source_paths` entry
  matches. Relevant lines from `rg`: query behavior at lines 49-81 and advisory
  emission at lines 147-149.
- `groundtruth-kb/tests/test_governance_hooks.py` covers only the current
  `source_paths` cases: no source_paths, matching source_paths, non-matching
  source_paths, non-source files, and migrated DB schema. There is no
  platform_tests bridge-derived coverage test in the spec-before-code block
  around lines 437-577.
- `groundtruth-kb/templates/managed-artifacts.toml` keeps
  `hook.spec-before-code` as a GT-KB-managed artifact targeting
  `.claude/hooks/spec-before-code.py` at lines 202-210, and registers it for
  `PreToolUse` in dual-agent profiles at lines 693-705.
- WI-4455 sibling dependencies are terminal: WI-3183 is retired/resolved after
  VERIFIED SPA investigation/remediation, and WI-3184 is retired/resolved by the
  bridge VERIFIED backlog reconciler.

## Option Comparison

Option A: bridge-derived coverage for `platform_tests/`.

This option teaches the hook to recognize explicit bridge-layer evidence for
platform test files: current/latest bridge status, target/test file references,
Specification Links, Spec-to-Test Mapping, and verified implementation evidence
where available. It preserves the existing principle that implementation slices
must cite specs and tests without forcing every historical platform test file
into canonical spec `source_paths`. This is the least-regret choice because
bridge proposals already carry the spec-derived verification evidence that
WI-4455 says the hook is missing.

Option B: backfill `platform_tests/` files into MemBase `source_paths`.

This keeps the hook simple, but it converts bridge-slice test evidence into a
large canonical source-path maintenance problem. It risks duplicate authority:
the bridge thread would remain the implementation evidence, while `source_paths`
would become a second, easy-to-stale mirror. Choose this only if the owner wants
`source_paths` to be the exclusive hook lookup surface.

Option C: keep `platform_tests/` advisory-only until the hook is restored.

This is operationally safe because the active root hook is already a stub, but
it leaves the P0 governance gap unresolved. Choose this only if the owner wants
to defer the policy until WI-4449/spec-before-code restoration work reopens the
hook surface.

## Recommended Governed Implementation Path

1. Assign WI-4455 to an appropriate project or create a small governance-hook
   policy project/authorization envelope.
2. File a bridge proposal for Option A before protected mutation.
3. After LO GO and a work-intent claim, update only the template hook and its
   focused tests first:
   - `groundtruth-kb/templates/hooks/spec-before-code.py`
   - `groundtruth-kb/tests/test_governance_hooks.py`
4. Keep the active root stub untouched unless the same proposal explicitly
   coordinates with WI-4449 or a later hook-restoration slice.
5. Verification should include a synthetic bridge thread fixture proving a
   `platform_tests/.../test_*.py` edit with bridge Spec-to-Test Mapping passes,
   while an unrelated test path without source_paths or bridge evidence still
   emits the advisory.

## Architecture Alignment Ledger

- OPS consolidation: keeps enforcement tied to governed lifecycle evidence
  instead of inventing a second ad hoc test-linkage authority.
- Dispatcher daemon architecture: avoids direct dispatcher/runtime changes;
  this is a hook-policy slice only.
- Lifecycle-first/scoring-last: asks whether required lifecycle evidence exists
  before any scoring or ranking concern. This aligns with the OPS model's
  lifecycle precedence.
- Portfolio reconciliation: avoids backfilling duplicate authority unless the
  owner explicitly selects it. Bridge-derived coverage treats existing bridge
  threads as evidence to reconcile, not records to bypass.
- Harness/bridge outage aftermath: current root hook is stubbed, so the slice
  should not be treated as an emergency active-hook outage repair unless the
  hook restoration work is explicitly brought into scope.

## Decision Needed

The next PB action is blocked on one owner policy decision:

- A: implement bridge-derived coverage for platform tests.
- B: backfill platform tests into canonical `source_paths`.
- C: defer/keep platform_tests advisory-only until hook restoration.

No protected source/config/test mutation is authorized by this packet.
