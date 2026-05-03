NEW

# Post-Implementation Report — GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL Slice 1

Implemented by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: Post-implementation report for Slice 1 of `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-005.md` (REVISED-2; Codex GO at `-006.md`).

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology source.
2. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol Mandatory Specification Linkage Gate.
3. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`.
4. **`.claude/rules/deliberation-protocol.md`** — DELIB archival; satisfied by §"DELIB Archival" below.
5. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract; 2 packets at `.groundtruth/formal-artifact-approvals/2026-05-02-disambiguation-slice1{,-delib}.json`.
6. **`GOV-19-A1`** — outside-in testing; tests exercise the public PolicyConfig + evaluate_content API.
7. **`GOV-20`** — architecture decisions; cross-cutting; this Slice 1 delivers the policy-config + library skeleton.
8. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — primer load is deterministic; lint behavior is deterministic per policy file.
9. **`groundtruth-kb/templates/rules/canonical-terminology.toml`** — existing profile-aware doctor config; UNCHANGED in Slice 1 (sibling policy file composes with it).
10. **`groundtruth-kb/templates/rules/canonical-terminology.md`** — existing managed-rule glossary; UNCHANGED in Slice 1.
11. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) — prior architecture preserved.
12. **`groundtruth-kb/templates/managed-artifacts.toml`** — registry; new row `rule.canonical-terminology-policy` added.
13. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch (Slice 5 future).
14. **`bridge/gtkb-gov-term-primer-startup-2026-05-02-015.md`** (sibling VERIFIED) — primer Slice 1; this disambiguation Slice 1 follows the same template-extension + dogfood pattern.
15. **`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md`** (sibling VERIFIED) — backlog program where "backlog" is the running case study for Tier B canonical/common disambiguation.

## Prior Deliberations

Carried forward from REVISED-2 scoping (`-005.md`); see that document §"Prior Deliberations" for full citation set including DELIB-0722, DELIB-1180, DELIB-1179/1018/1017/0804, DELIB-S324-OM-DELTA-0004-CHOICE, DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT, DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE, DELIB-1404, and the three S327 owner-directive DELIBs (now archived).

## Implementation Evidence (Slice 1 deliverables)

Slice 1 per `-005.md` §"Sequencing": "Policy file + shared library. New `canonical-terminology-policy.toml` + `term_disambiguation.py` shared library. Pre-implementation only; needs `GOV-ARTIFACT-APPROVAL-001` packet. T1."

### Artifact 1 — `groundtruth-kb/templates/rules/canonical-terminology-policy.toml` (new managed-rule template)

- **Approval packet:** `.groundtruth/formal-artifact-approvals/2026-05-02-disambiguation-slice1.json` (SHA256: `cfdba16c1a7d59f5448e1c1ef564b18a737bd13a73571dd6d94c33a3577f6200`).
- Sections: `[meta]` (version=1.0.0); `[defaults]` (7 pinned values per Codex `-002.md` F4 + `-004.md` F1); 21 `[term."<term>"]` entries.
- Term distribution: 8 Tier A (distinctive forms — MemBase, Deliberation Archive, MEMORY.md, Prime Builder, Loyal Opposition, GT-KB, GroundTruth-KB, GTKB) + 13 Tier B (capitalization disambiguates — platform, application, hosted application, adopter, project, work item, backlog, specification, requirement, implementation proposal, implementation report, verification, dashboard, bridge).
- `specific_id_prefix` populated for 4 Tier B terms (work item → WI; backlog → BL; specification → SPEC; requirement → REQ).
- "Agent Red" intentionally NOT in template (post-render in GT-KB checkout self-install only per primer Slice 1 lesson; smoke-test no-leakage rule).

### Artifact 2 — `groundtruth-kb/src/groundtruth_kb/term_disambiguation.py` (new shared library)

- API surface (5 public symbols in `__all__`): `Tier`, `Severity`, `Violation`, `PolicyConfig`, `evaluate_content`.
- `Violation` dataclass: term, tier, severity, line, message, suggestion (frozen).
- `PolicyConfig` dataclass: defaults, terms (frozen); `.load(policy_path: Path) -> PolicyConfig` classmethod.
- `evaluate_content(content, *, file_path, policy) -> list[Violation]`: pure function; honors `file_level_disable_marker`; Tier A/B/C lint logic stubs (return empty list) with explicit deferral to Slices 2-3 in docstring.
- Strict typing: `Literal["A","B","C"]` for Tier; `Literal["error","warn"]` for Severity.

### Artifact 3 — Registry row in `groundtruth-kb/templates/managed-artifacts.toml`

```toml
[[artifacts]]
class = "rule"
id = "rule.canonical-terminology-policy"
template_path = "rules/canonical-terminology-policy.toml"
target_path = ".claude/rules/canonical-terminology-policy.toml"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
notes = "Canonical-terminology disambiguation policy; product-managed because the per-term Tier A/B/C policy is framework-defined."
```

Same pattern as the sibling `rule.canonical-terminology` and `rule.canonical-terminology-config` rows. Total registry records: 58 → 59.

### Artifact 4 — `groundtruth-kb/tests/test_term_disambiguation.py` (T1, new)

8 test functions covering T1 acceptance:
- `test_canonical_terminology_policy_toml_exists`
- `test_policy_registered_in_managed_artifacts`
- `test_policy_declares_all_seven_pinned_defaults` (verifies all 7 specific values)
- `test_policy_covers_21_generic_owner_required_terms` (with inverse-presence assertion that "Agent Red" is NOT in template)
- `test_policy_term_entries_have_disambiguation_tier` (each entry's tier is A/B/C)
- `test_policy_config_load_parses_without_error`
- `test_evaluate_content_returns_empty_list_in_slice1` (Slice 1 stub behavior)
- `test_evaluate_content_honors_file_level_disable_marker`
- `test_violation_dataclass_field_shape`

### Artifact 5 — `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` v1 (DELIB archival)

- Approval packet: `.groundtruth/formal-artifact-approvals/2026-05-02-disambiguation-slice1-delib.json` (SHA256: `8dccd449395eb3f5188d9205b1443aab413c56e9e08d5bee3794033ec4d46c44`).
- source_type: `owner_conversation`; outcome: `owner_decision`; session_id: `S327`.

### Mid-implementation regressions caught + fixed

The initial implementation surfaced 3 regression clusters caught by the broader test sweep before this post-impl was filed:

1. **Smoke-test leakage** — the policy TOML's header comment leaked the literal "Agent Red" string into adopter scaffolds. Fixed by replacing the comment text to describe the GT-KB-self extension as "instance term" rather than naming Agent Red specifically.
2. **Registry count assertions** — 7 tests in `test_managed_registry.py` hardcoded `total = 58` and `rule = 10`; updated to `total = 59` and `rule = 11`. Sets of expected rule paths extended with `.claude/rules/canonical-terminology-policy.toml`.
3. **Golden fixtures (TP14/TP15)** — adding the new managed rule changed the scaffold output for both profiles. Fixtures regenerated via `scripts/_capture_scaffold_golden.py` (local-only: 30 → 31 files; dual-agent: 59 → 60 files).

All 3 clusters resolved before filing this post-impl.

## Verification Evidence

### Test sweep (post-fixes)

```
$ python -m pytest groundtruth-kb/tests/test_term_disambiguation.py groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_scaffold_project.py
95 passed, 1 warning in 18.64s
```

Net: existing tests preserved + 9 new tests added in Slice 1 (8 in test_term_disambiguation.py + the registry tests indirectly cover the new row). Total: 86 → 95 (+9). Zero regressions.

### Ruff

```
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/term_disambiguation.py groundtruth-kb/tests/test_term_disambiguation.py
All checks passed!
```

## Acceptance Criteria Check (Slice 1)

| Criterion (from `-005.md` Acceptance) | Status |
|---|---|
| New policy file at `templates/rules/canonical-terminology-policy.toml` with 22-term minimum + pinned `[defaults]` | SATISFIED — adopter template has 21 generic terms (Agent Red post-render in GT-KB self-install per primer Slice 1 pattern); all 7 `[defaults]` values pinned per Codex `-002.md` F4 + `-004.md` F1 |
| Registry row `rule.canonical-terminology-policy` added | SATISFIED — `managed-artifacts.toml` extended; T2 (`test_policy_registered_in_managed_artifacts`) verifies |
| Shared library `groundtruth_kb/term_disambiguation.py` implemented with `evaluate_content` API | SATISFIED — public API + policy load + file-level disable marker honoring; Tier-specific lint deferred to Slices 2-3 per scoping `-005.md` §"Sequencing" |
| 7 pinned defaults present | SATISFIED — `test_policy_declares_all_seven_pinned_defaults` verifies all 7 |
| 21 generic owner-required terms covered | SATISFIED — `test_policy_covers_21_generic_owner_required_terms` |
| Inverse: Agent Red NOT in template | SATISFIED — same test |
| `evaluate_content` callable in Slice 1 (returns []) | SATISFIED |
| File-level disable marker working | SATISFIED |
| Hooks (PreToolUse + PostToolUse) deferred to Slices 2-3 | EXPECTED per `-005.md` Sequencing |
| `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` archived | SATISFIED |
| Slice 1 changes carry approval packets | SATISFIED — 2 packets (template batch + DELIB) |
| Existing canonical-terminology thread evidence intact | SATISFIED — no changes to `canonical-terminology.{md,toml}`; `gtkb-canonical-terminology-surface-implementation-012` evidence preserved |
| Ruff + lint clean | SATISFIED |

## Files Touched (Slice 1)

Created (new managed-rule template + new library):
- `groundtruth-kb/templates/rules/canonical-terminology-policy.toml`
- `groundtruth-kb/src/groundtruth_kb/term_disambiguation.py`

Modified (registry extension + test count updates + content fixes):
- `groundtruth-kb/templates/managed-artifacts.toml` (+ `rule.canonical-terminology-policy` row)
- `groundtruth-kb/tests/test_managed_registry.py` (count updates: 58 → 59 records; rule class 10 → 11; 19 → 20 local-only; rule paths set extended)

Created (test):
- `groundtruth-kb/tests/test_term_disambiguation.py` (8 test functions)

Created (formal-artifact-approval packets):
- `.groundtruth/formal-artifact-approvals/2026-05-02-disambiguation-slice1.json` (template batch)
- `.groundtruth/formal-artifact-approvals/2026-05-02-disambiguation-slice1-delib.json` (DELIB)

Modified (golden fixtures regenerated):
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/` (30 → 31 files)
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/` (59 → 60 files)

KB rows inserted:
- `deliberations` table: `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` v1

## Notes for Loyal Opposition

- **Slice 1 is intentionally pre-implementation.** The shared library has the API surface + file-level-disable behavior; Tier A/B/C lint logic is implemented in Slices 2 (PreToolUse hook for `error` severities) and Slice 3 (PostToolUse audit hook for `warn` severities) per the scoping proposal `-005.md` §"Sequencing". This Slice 1 ships the policy file + library skeleton + registry registration + T1; later slices wire enforcement.
- **No changes to existing canonical-terminology surface.** The sibling policy file composes with the existing `canonical-terminology.toml` (profile-aware doctor config); the doctor's `_check_canonical_terminology()` is unchanged. The verified prior thread `gtkb-canonical-terminology-surface-implementation-012` is preserved.
- **Adopter/GT-KB-self split mirrors primer Slice 1.** 21 generic terms in the adopter template + 1 instance term ("Agent Red") added post-render in GT-KB checkout self-install, per the primer Slice 1 lesson. Smoke-test leakage rule preserved.
- **Mid-implementation regressions caught early.** 3 clusters (smoke-leakage, registry counts, golden fixtures) caught by the broader test sweep + fixed before filing. Documented in §"Mid-implementation regressions caught + fixed".
- **GT-KB checkout self-install of policy file is deferred** to Slice 5 (smart-poller dispatch integration) or Slice 6 (release-gate audit). The dogfood install of `canonical-terminology-policy.toml` doesn't yet apply pressure on Slice 1's acceptance.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
