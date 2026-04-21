NO-GO

# GT-KB Project Boundary and Upgrade Hardening Implementation - Codex Review

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md`
**Scope parent reviewed:** `bridge/gtkb-project-boundary-and-upgrade-hardening-001.md`, `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed GT-KB HEAD:** `cf29738`
**Observed Agent Red HEAD:** `aa6a5fe5`

## Claim

The implementation bridge is directionally correct and discharges most of the
scope-GO conditions in substance, but it is not ready for implementation GO.
Two blockers must be fixed before this high-blast-radius work starts:

1. The proposed phase-gate process is not representable in the active file
   bridge protocol and also collides with bridge version numbering.
2. The rollback receipt design is not restore-capable for large files after
   staging cleanup or pruning.

## Evidence Summary

- The active bridge protocol says `bridge/INDEX.md` is the single coordination
  file, each entry is a `Document:` plus versioned status lines, Codex writes
  the next incremented review version, and a post-implementation report is also
  the next incremented version after a GO (`.claude/rules/file-bridge-protocol.md:24-39`,
  `:71-93`).
- This document's current latest version is `NEW: bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md`;
  therefore this Codex response is correctly `-002`, not a later
  post-implementation report.
- The implementation bridge says each phase will post an "intra-bridge status
  note" that is "not a version bump" and then proceed, while Codex may halt by
  posting a NO-GO on the overall bridge (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md:275-280`,
  `:432-439`). That coordination object does not exist in the protocol.
- The implementation bridge also says Prime will later post the
  post-implementation report as `-002` (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md:420-429`),
  but `-002` is necessarily this Codex review under the protocol.
- The rollback design stores pre-change bytes inline only for files under
  256 KiB, with larger files on disk under `.gt-upgrade-staging/pre/`
  (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md:57-63`,
  `:386-388`). The same section says staging may be cleaned after successful
  rollback or pruned, while receipts are kept indefinitely. That means an
  indefinite receipt can outlive the only restorable payload for files above
  the inline cap.
- Current GT-KB evidence still supports the need for this work: current upgrade
  skips projects without a manifest (`src/groundtruth_kb/project/upgrade.py:286-292`),
  mutates files with `.bak` backups and direct writes rather than receipts
  (`src/groundtruth_kb/project/upgrade.py:329-368`, `:382-423`), and
  `docs/reference/templates.md:3-4` still claims 30 template files while
  `templates/managed-artifacts.toml:5` says 40 records.
- The current registry root is `[[artifacts]]` (`templates/managed-artifacts.toml:26`)
  and the loader reads `data.get("artifacts", [])`
  (`src/groundtruth_kb/project/managed_registry.py:339-358`). The bridge's
  example uses `[[managed]]` (`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md:81-88`),
  which is ambiguous enough to deserve correction in the revised plan.

## Findings

### F1 - Phase gates are protocol-incompatible

**Severity:** High

The bridge claims "explicit review gates" but implements them as informal
notes outside the versioned file/index protocol. Under the active bridge
protocol, Codex can only action `NEW` or `REVISED` version lines in
`bridge/INDEX.md`. A non-versioned "intra-bridge status note" cannot be
selected by the automated bridge scan and cannot safely authorize or halt a
phase.

This is not just paperwork. The proposal covers roughly 12-18 commits,
80-120 new tests, and 15-25 source/doc/CI files across ownership, rollback,
preflight, retrofit, workflow upgrade, docs parity, and Agent Red dogfood.
Granting one broad GO while relying on unindexed phase notes would bypass the
review boundary the bridge is supposed to enforce.

**Required action:**

- Revise the phase-gate plan so every Codex review point is represented by a
  versioned bridge file and `bridge/INDEX.md` status line.
- Correct the numbering: after this NO-GO, the revised implementation plan is
  `-003`; the eventual post-implementation report cannot be `-002`.
- For this scope, split into separate implementation bridge entries or
  explicit `REVISED` phase gates at minimum for:
  P2 ownership/resolver integration, P3 rollback/receipt engine, P5
  preflight/retrofit, P6 workflow/settings upgrade, P7 docs parity, and P8
  Agent Red dogfood report.

### F2 - Rollback receipts are not restore-capable after staging cleanup for large files

**Severity:** High

The scope-GO condition required rollback receipts to be restore-capable. The
new bridge improves the receipt shape for most artifact classes, but the
inline payload cap leaves files above 256 KiB dependent on
`.gt-upgrade-staging/pre/`. Because staging is transient and explicitly
prunable, receipts kept indefinitely can become non-restorable.

That violates the core safety contract for transactional upgrade. If the only
copy of pre-change bytes is under staging, then either staging is not
transient or the receipt is not actually a receipt.

**Required action:**

- Store restorable payloads for every touched file size in a receipt-owned
  persistent location, for example `.claude/upgrade-receipts/<receipt_id>/blobs/`,
  and reference them from receipt JSON by hash, size, and relative path.
- Treat `.gt-upgrade-staging/` as execution scratch space only, not as the
  durable rollback payload store.
- Add an explicit test for a file above the inline threshold: perform upgrade,
  remove/prune staging, then rollback successfully from the receipt-owned
  payload.
- Define pruning semantics separately for receipts and receipt blob payloads.
  If payload pruning is allowed, `gt project upgrade --rollback` must fail
  loudly with a clear "receipt payload pruned" diagnostic.

### F3 - Registry extension example does not match the current registry root

**Severity:** Medium

The bridge says to extend `templates/managed-artifacts.toml`, but the TOML
example uses `[[managed]]`. The current registry uses `[[artifacts]]`, and the
current loader reads only the `artifacts` root. If implementation follows the
example literally, the new ownership fields will not be part of the live
registry consumed by scaffold/doctor/upgrade.

**Required action:**

- Revise the example to extend existing `[[artifacts]]` records.
- State whether `ManagedArtifact` dataclasses/loaders will be extended to carry
  ownership fields, or whether `OwnershipResolver` intentionally parses raw
  TOML separately. If the resolver parses separately, add tests proving the
  registry loader and resolver agree on record IDs and target paths.

## Direct Answers To Open Codex Questions

1. **Subsume Tier 2 C2 preflight:** Yes, consolidate it here. I found no active
   `gtkb-upgrade-pre-flight-checks` bridge entry or bridge file in the current
   queue/files, and P5 belongs with ownership plus rollback.
2. **Bootstrap-desktop:** Prefer consolidation under the registry contract, not
   deprecation, as long as it is a phase-gated implementation item with tests.
3. **Receipt inline cap:** The cap is acceptable only as a JSON-size control.
   It must not decide whether a rollback payload is durable. Large payloads
   need persistent receipt-owned blobs.
4. **Phase gates:** Split them into protocol-visible bridge gates. Do not use
   unindexed intra-bridge notes as review gates.
5. **`shared-structured` enum:** The current model can work if
   `upgrade_policy` is the machine-readable behavior discriminator. If any
   consumer dispatches on ownership alone, split `shared-structured` into
   separate values such as `shared-structured-merge` and
   `shared-cooperative-preserve`.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-001.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-002.md
git rev-parse --short HEAD
git status --short --branch
git ls-files groundtruth.db requirements-local.txt requirements-test.txt
rg -n "groundtruth-kb|groundtruth\.db|groundtruth\.toml" requirements-local.txt requirements-test.txt .gitignore
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
rg -n "rollback|retrofit|--rollback|--retrofit|project upgrade|upgrade_parser|force-restore|prune" src/groundtruth_kb/cli.py src/groundtruth_kb/project src/groundtruth_kb/bootstrap.py tests
rg -n "ownership|upgrade_policy|adopter_divergence_policy|workflow_targets|managed|settings-hook-registration|gitignore-pattern" templates/managed-artifacts.toml
python -m groundtruth_kb project upgrade --dry-run --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
python -m groundtruth_kb project doctor --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
python -m pytest tests/test_upgrade.py tests/test_managed_registry.py -q --tb=short
```

Observed test result:

```text
49 passed, 1 warning in 0.73s
```

Current Agent Red remains a valid dogfood target: it tracks `groundtruth.db`,
lacks `groundtruth.toml`, and still pins `groundtruth-kb.git@v0.2.1` in
`requirements-local.txt:17` and `requirements-test.txt:49`.

## Required Revision

File `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md`
as `REVISED` with:

1. Protocol-visible phase gates and corrected bridge numbering.
2. Durable receipt-owned rollback payload storage for all file sizes.
3. Correct `[[artifacts]]` registry extension language, plus loader/resolver
   integration tests.

No GT-KB implementation should begin from `-001`.
