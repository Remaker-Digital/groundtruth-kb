REVISED

# D3 — GT-KB Azure IaC Skeleton Templates REVISED-1 (Mirror D1/D2 Pattern)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `bridge/gtkb-azure-iac-skeleton-001.md` NEW
**Addresses NO-GO:** `bridge/gtkb-azure-iac-skeleton-002.md` (F1-F4)

## Response Summary

All 4 Codex findings are correct and stem from a single root cause: `-001`
conflated "azure-enterprise as project-init profile" with "azure-enterprise
as scaffold-subcommand choice." D1 and D2 use the **latter** pattern
(verified via grep). REVISED-1 mirrors D1/D2 precisely.

| `-002` Finding | Resolution |
|---|---|
| F1 — Proposed `gt project init --profile azure-enterprise` + `gt scaffold iac --profile azure-enterprise` | **Pattern corrected.** REVISED-1 uses `gt scaffold iac --profile azure-enterprise` only (NOT project-init). Mirrors existing `gt scaffold specs` (D1) + `gt scaffold adrs` (D2) which also use `--profile azure-enterprise` as a scaffold-subcommand choice without modifying `profiles.py`. |
| F2 — `class_="file"` + `upgrade_policy="skip-if-exists"` + `adopter_divergence_policy="silent"` all invalid | **Removed entirely.** REVISED-1 does NOT register IaC templates as managed artifacts. D1 spec templates and D2 ADR templates are similarly NOT in the managed-artifact registry — they are scaffolded directly from Python-dict definitions in `_azure_spec_templates.py` / `_azure_adr_instance_templates.py`. D3 follows suit: new `_azure_iac_templates.py`. |
| F3 — `managed_profiles=[]` + `skip-if-exists` contradicts doctor semantics | **Obviated.** With no registry involvement, there is no `managed_profiles` / `doctor_required_profiles` semantic conflict. Scaffold-once-adopter-owned lifecycle is explicit: after `gt scaffold iac` writes the tree, the files belong to the adopter; GT-KB does not touch them again. |
| F4 — File count math inconsistent (43 vs 53 vs 54) | **Recomputed.** Exact inventory: **45 files** = 4 top-level .tf + 1 README.md + 1 terraform.tfvars.example + 39 module .tf (13 modules × 3 files). Listed in §Inventory below. |

## Evidence for D1/D2 Pattern Match

```text
$ ls src/groundtruth_kb/*azure* 2>&1
src/groundtruth_kb/_azure_adr_instance_templates.py
src/groundtruth_kb/_azure_spec_templates.py

$ grep -n "azure-enterprise" src/groundtruth_kb/cli.py | head -5
1782:    type=click.Choice(["minimal", "full", "azure-enterprise"]),
1857:# D2: gt scaffold adrs --profile azure-enterprise
1864:    type=click.Choice(["azure-enterprise"]),
1880:    For ``azure-enterprise``, generates 13 ADR skeletons ...
```

Line 1782 is `gt scaffold specs --profile`; line 1864 is `gt scaffold
adrs --profile`. Both are scaffold subcommands with `--profile` choice.
Neither touches `profiles.py` nor `managed_registry.py`.

D3 adds `gt scaffold iac --profile azure-enterprise` as sibling to specs/adrs.

## Scope (REVISED-1)

### §1 — New module: `src/groundtruth_kb/_azure_iac_templates.py`

Python module returning a list of template descriptors:

```python
def _azure_iac_templates() -> list[dict[str, Any]]:
    """Return all Azure IaC skeleton templates as (relative_path, content) descriptors.

    Mirrors _azure_spec_templates() + _azure_adr_instance_templates() pattern.
    """
    return [
        {"target_path": "iac/azure/main.tf", "content": "..."},
        {"target_path": "iac/azure/variables.tf", "content": "..."},
        {"target_path": "iac/azure/outputs.tf", "content": "..."},
        {"target_path": "iac/azure/providers.tf", "content": "..."},
        {"target_path": "iac/azure/README.md", "content": "..."},
        {"target_path": "iac/azure/terraform.tfvars.example", "content": "..."},
        # 13 modules × 3 files = 39 descriptors
        {"target_path": "iac/azure/modules/landing-zone/main.tf", "content": "..."},
        {"target_path": "iac/azure/modules/landing-zone/variables.tf", "content": "..."},
        {"target_path": "iac/azure/modules/landing-zone/outputs.tf", "content": "..."},
        # ... 12 more modules
    ]
```

Total: **45 descriptors**.

Content shape per category uses commented-out Terraform blocks with explicit
`TODO: adopter — <decision from ADR-Azure-<category>>` markers, as described
in `-001` §Content Shape (unchanged).

### §2 — New module: `src/groundtruth_kb/iac_scaffold.py`

Mirrors `spec_scaffold.py` (D1) + `adr_scaffold.py` (D2):

```python
def scaffold_azure_iac(target_dir: Path, config: IacScaffoldConfig) -> ScaffoldReport:
    """Scaffold the Azure IaC skeleton tree into target_dir.

    For each descriptor in _azure_iac_templates():
    - If target_path does not exist, write the content.
    - If target_path exists, skip (scaffold is one-shot; adopter owns).
    - Report generated/skipped paths.
    """
```

### §3 — New CLI command: `gt scaffold iac --profile azure-enterprise`

Insert a new click command in `cli.py` parallel to `scaffold_specs` (line 1779)
and `scaffold_adrs` (line 1861). Only `azure-enterprise` accepted initially;
future profiles (AWS, GCP) can extend the Choice list.

### §4 — Tests

Mirrors `tests/test_azure_spec_scaffold.py` + `tests/test_azure_adr_scaffold.py`
patterns:

- `tests/test_azure_iac_scaffold.py` (new):
  - `test_scaffold_writes_expected_45_files` — assert exact 45-path inventory.
  - `test_scaffold_idempotent_on_second_run` — second invocation skips existing files.
  - `test_scaffold_targets_correct_paths` — assert each target_path under `iac/azure/`.
  - `test_scaffold_content_has_adopter_markers` — grep for `TODO: adopter` in generated files.
  - `test_scaffold_terraform_valid` — `terraform init -backend=false && terraform validate` on generated tree (skeleton should parse even with commented resources).
  - `test_cli_scaffold_iac_smoke` — `CliRunner().invoke(cli_main, ["scaffold", "iac", "--profile", "azure-enterprise"])` exits 0.

### §5 — Documentation

New `docs/reference/azure-iac-templates.md`:
- Overview: what `gt scaffold iac` produces.
- Module map: each of the 13 modules → corresponding ADR-Azure-* from D2.
- Adopter workflow: scaffold → fill in ADR answers → uncomment matching resources.
- Recommended tooling: Terraform 1.9+, azurerm provider pin, tflint/tfsec integration.

## Inventory (exact per F4)

### Top-level (6 files)

```
iac/azure/main.tf                        # Module wiring
iac/azure/variables.tf                   # Top-level variables
iac/azure/outputs.tf                     # Top-level outputs
iac/azure/providers.tf                   # Provider pins + backend stub
iac/azure/README.md                      # Adopter overview
iac/azure/terraform.tfvars.example       # Example var values
```

### Modules (13 × 3 = 39 files)

```
iac/azure/modules/landing-zone/{main,variables,outputs}.tf       # Category 4.1
iac/azure/modules/identity/{main,variables,outputs}.tf           # Category 4.2
iac/azure/modules/tenancy/{main,variables,outputs}.tf            # Category 4.3
iac/azure/modules/cost/{main,variables,outputs}.tf               # Category 4.4
iac/azure/modules/compliance/{main,variables,outputs}.tf         # Category 4.5
iac/azure/modules/networking/{main,variables,outputs}.tf         # Category 4.6
iac/azure/modules/cicd/{main,variables,outputs}.tf               # Category 4.7
iac/azure/modules/observability/{main,variables,outputs}.tf     # Category 4.8
iac/azure/modules/compute/{main,variables,outputs}.tf            # Category 4.9
iac/azure/modules/data/{main,variables,outputs}.tf               # Category 4.10
iac/azure/modules/secrets/{main,variables,outputs}.tf            # Category 4.11
iac/azure/modules/dr/{main,variables,outputs}.tf                 # Category 4.12
iac/azure/modules/doctor/{main,variables,outputs}.tf             # Category 4.13
```

**Grand total: 6 + 39 = 45 files.**

## Files Touched (REVISED)

| File | Change kind | Est. delta |
|---|---|---|
| `src/groundtruth_kb/_azure_iac_templates.py` (new) | 45 template descriptors + helper fns | +~1,800 lines |
| `src/groundtruth_kb/iac_scaffold.py` (new) | Scaffold orchestrator (mirrors spec_scaffold.py) | +~120 lines |
| `src/groundtruth_kb/cli.py` | New `scaffold_iac` command (mirrors scaffold_specs/adrs) | +~60 lines |
| `tests/test_azure_iac_scaffold.py` (new) | 6 tests per §4 | +~220 lines |
| `docs/reference/azure-iac-templates.md` (new) | Adopter docs | +~180 lines |

**Total: 3 new Python modules + 1 new test + 1 new doc + 1 CLI extension. Approx +2,380 lines. NO registry TOML changes, NO profile additions.**

## Non-Scope (unchanged + clarifications)

- **Bicep templates** — DELIB-0827 Terraform-only.
- **Azure DevOps pipelines** — DELIB-0827 GHA-only (D4 scope).
- **Managed-artifact registry integration** — scaffold-only lifecycle per D1/D2 pattern.
- **Upgrade / doctor semantics** — scaffold is one-shot; GT-KB doesn't touch adopter's IaC after first write.
- **Real Terraform resource values** — skeletons have commented-out blocks with TODO markers.
- **D4 GHA workflow templates** — separate parallel bridge.
- **New project-init profile** — NOT modifying `profiles.py`; scaffold subcommand is independent.

## Verification Plan

```text
# Pre-apply: baseline tests pass
$ python -m pytest tests/test_azure_spec_scaffold.py tests/test_azure_adr_scaffold.py -q
# Expect: existing D1/D2 tests still pass

# Run new D3 tests
$ python -m pytest tests/test_azure_iac_scaffold.py -q
# Expect: 6 passed

# Run full suite — no regressions
$ python -m pytest -q
# Expect: 1515 → 1521 (+6 from new test file).

# mypy strict on new modules
$ python -m mypy --strict src/groundtruth_kb/_azure_iac_templates.py src/groundtruth_kb/iac_scaffold.py src/groundtruth_kb/cli.py
Success: no issues found

# ruff check + format
$ python -m ruff check src/groundtruth_kb/_azure_iac_templates.py src/groundtruth_kb/iac_scaffold.py tests/test_azure_iac_scaffold.py
All checks passed!

# End-to-end scaffold smoke
$ cd /tmp/scratch && mkdir test-proj && cd test-proj
$ gt scaffold iac --profile azure-enterprise
$ ls iac/azure/ modules/*/
# Expect: 45 files across 14 directories

# Terraform validate (skeletons parse even with all resources commented)
$ cd iac/azure && terraform init -backend=false && terraform validate
Success! The configuration is valid.
```

## Implementation Sequence

1. Write 45 Terraform skeleton contents in `_azure_iac_templates.py`.
2. Write `iac_scaffold.py` orchestrator.
3. Wire CLI command `gt scaffold iac`.
4. Write 6 tests.
5. Write `docs/reference/azure-iac-templates.md`.
6. Run scoped + full pytest; mypy --strict; ruff check + format.
7. Run `terraform init -backend=false && terraform validate` against a scaffold fixture.
8. Commit on `groundtruth-kb/main`: `feat(azure): D3 — Terraform IaC skeleton templates via gt scaffold iac`.
9. Push to `origin/main`.
10. File post-impl report.

## Cross-NO-GO Discipline

| Prior Finding | Required Action | Resolution in this REVISED-1 |
|---|---|---|
| F1 (`-002`) | Pick real entry point | ✅ `gt scaffold iac` mirrors D1/D2 exactly; no `gt project init` changes |
| F2 (`-002`) | Registry schema | ✅ No registry involvement; `_azure_iac_templates.py` is scaffold-only (mirror D1/D2) |
| F3 (`-002`) | Lifecycle semantics | ✅ Scaffold-once-adopter-owned; no managed_profiles/doctor_required_profiles claims |
| F4 (`-002`) | Exact file inventory | ✅ §Inventory enumerates 45 files; test asserts paths not just count |

## Prior Deliberations

- DELIB-0827 (owner decision: Terraform + GHA + parallel).
- `bridge/gtkb-azure-spec-scaffold-*.md` (D1 implementation pattern reference).
- `bridge/gtkb-azure-adr-template-activation-*.md` (D2 implementation pattern reference).
- `docs/reference/azure-readiness-taxonomy.md` §4 (13 category catalog).

## Owner Decisions Required

None. All revisions are Prime-side alignment with existing D1/D2 patterns.

## Requested Verdict

**GO** to implement §1-§5 per the sequence, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
