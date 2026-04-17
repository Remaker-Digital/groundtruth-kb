# F8: Provenance Reconciliation — REVISED

**Feature:** F8 — Provenance Reconciliation
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Revision:** Addresses 4 conditions from NO-GO bridge/gtkb-spec-pipeline-f8-002.md

---

## Changes From v1

| NO-GO Condition | Resolution |
|----------------|-----------|
| 1. Schema field name mismatch (`authority_tier` vs `authority`) | Corrected to `authority` per F1 proposal. F8 explicitly depends on F1 for authority and provisional_until fields. |
| 2. Staleness depends on F7 but undeclared | Two options provided: (a) use F7 session snapshots if available, (b) fallback to `changed_at` timestamps from existing spec versions. F7 declared as optional dependency. |
| 3. Orphan detection lacks `project_root` | Added `project_root: Path` parameter to all orphan detection APIs, consistent with existing `run_all_assertions(db, project_root, ...)` at assertions.py:646. |
| 4. Authority conflict detection underspecified | Defined reproducible conflict detection: same section + same scope + overlapping assertion file targets. Does NOT attempt semantic similarity — only structural overlap. |

---

## Dependencies

**Required:** F1 (needs `authority`, `provisional_until` fields)
**Optional:** F7 (session snapshots improve staleness detection; fallback uses `changed_at` timestamps)
**Independent of:** F2 (conflict detection is self-contained, not delegated to F2's heuristic)

## Reconciliation Checks

### Check 1: Authority Conflicts

**Algorithm (reproducible, not semantic):**
```python
def find_authority_conflicts(kdb) -> list[dict]:
    stated = kdb.list_specs(authority='stated')
    inferred = kdb.list_specs(authority='inferred')
    
    conflicts = []
    for inf_spec in inferred:
        for st_spec in stated:
            if (inf_spec.get('section') == st_spec.get('section')
                and inf_spec.get('scope') == st_spec.get('scope')
                and _assertions_overlap(inf_spec, st_spec)):
                conflicts.append({
                    'inferred_spec': inf_spec['id'],
                    'stated_spec': st_spec['id'],
                    'overlap': 'same section/scope + overlapping assertion targets',
                })
    return conflicts
```

**`_assertions_overlap` definition:** Two specs have overlapping assertions when any assertion from each targets the same `file` value. This is a structural check — it does not evaluate whether the assertions contradict each other, only that they govern the same code.

### Check 2: Orphaned Specs

```python
def find_orphaned_specs(kdb, project_root: Path) -> list[dict]:
    """Find specs whose assertion targets no longer exist.
    
    Args:
        project_root: Required. Same as run_all_assertions() parameter.
                      Used to resolve relative file paths in assertions.
    """
```

Uses the same `_safe_resolve(path_str, project_root)` from assertions.py:67 to resolve file paths. If the resolved path doesn't exist, the assertion target is orphaned.

**Exemptions:**
- Assertions without a `file` field (pattern-only, behavioral) → skipped
- Assertions with glob patterns → evaluated via `_safe_glob()`, orphaned only if zero matches
- Non-executable assertion types → skipped (consistent with assertions.py:560)

### Check 3: Expired Provisionals

```python
def find_expired_provisionals(kdb) -> list[dict]:
    provisionals = kdb.get_provisional_specs()  # From F1
    expired = []
    for spec in provisionals:
        replacement_id = spec.get('provisional_until')
        replacement = kdb.get_spec(replacement_id)
        if replacement and replacement.get('status') in ('implemented', 'verified'):
            expired.append({
                'provisional_spec': spec['id'],
                'replacement_spec': replacement_id,
                'replacement_status': replacement['status'],
            })
    return expired
```

### Check 4: Stale Specs

**With F7 (optional):** Count session snapshots since spec's last `changed_at`. If spec unchanged for N sessions while its section has changes, flag as stale.

**Without F7 (fallback):** Use `changed_at` timestamps directly. If spec unchanged for >90 days while other specs in its section have been modified within 30 days, flag as stale.

```python
def find_stale_specs(
    kdb,
    *,
    staleness_days: int = 90,
    section_activity_days: int = 30,
) -> list[dict]:
    """Fallback staleness detection using changed_at timestamps."""
```

### Check 5: Duplicate Candidates

Title-only similarity using normalized string comparison (lowercase, strip punctuation, compare token overlap). Threshold: 80% token overlap.

**No ChromaDB dependency** for the initial implementation. If semantic similarity is needed later, it becomes a Phase B enhancement.

## API Design

```python
class KnowledgeDB:
    def run_reconciliation(
        self,
        project_root: Path,
        *,
        checks: list[str] | None = None,  # Default: all checks
    ) -> ReconciliationReport:
        """Run provenance reconciliation. Requires project_root for orphan detection."""
        ...
    
    def find_authority_conflicts(self) -> list[dict]: ...
    def find_orphaned_specs(self, project_root: Path) -> list[dict]: ...
    def find_expired_provisionals(self) -> list[dict]: ...
    def find_stale_specs(self, *, staleness_days: int = 90) -> list[dict]: ...
    def find_duplicate_candidates(self, *, threshold: float = 0.8) -> list[dict]: ...

@dataclass
class ReconciliationReport:
    timestamp: str
    checks_run: list[str]
    findings: dict          # {check_name: [findings]}
    total_findings: int
    critical_findings: int  # Authority conflicts, orphaned specs
    advisory_findings: int  # Stale, duplicates
```

**CLI (GT-KB owned):**
```
gt reconcile                     # Run all checks
gt reconcile --check orphans     # Run specific check
gt reconcile --project-root .    # Explicit project root
```

## Test Plan (synthetic fixtures)

1. **Authority conflict** — Create stated + inferred specs, same section, overlapping assertion file; verify conflict detected
2. **No false conflict** — Stated + inferred specs, different sections; verify NO conflict
3. **Orphan detection** — Create spec with assertion targeting nonexistent file; verify orphan detected with project_root resolution
4. **Expired provisional** — Create provisional spec with provisional_until=X; set X to implemented; verify expiration detected
5. **Stale detection (fallback)** — Create spec, update other specs in section, leave target unchanged; verify staleness flagged
6. **Duplicate detection** — Create two specs with 90% title token overlap; verify duplicate candidate reported

## Implementation Sequence

1. Authority conflict detection (requires F1 for authority field)
2. Orphan detection with project_root (uses existing assertion path resolution)
3. Expired provisional detection (requires F1 for provisional_until)
4. Stale spec detection (fallback using changed_at; F7-enhanced version later)
5. Duplicate detection (title token overlap)
6. Reconciliation report aggregator + CLI
7. Write 6 tests

---

*Submitted by: S286-Prime*
*Revision: Addresses NO-GO bridge/gtkb-spec-pipeline-f8-002.md*
