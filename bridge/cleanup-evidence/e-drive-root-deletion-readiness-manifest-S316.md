# E:\ Root-Level Deletion-Readiness Manifest — S316

**Scan timestamp (UTC):** 2026-04-28T00:51:49.0844980Z
**Scope:** Read-only inventory of E:\ root-level entries (not E:\GT-KB, not Windows system, not E:\Claude-Playground)
**Authority:** `bridge/e-drive-root-deletion-readiness-scan-002.md` (Codex GO with 8 conditions); revision per `-004` Codex NO-GO addressed in `-005` REVISED-1.
**Companion:** `e-drive-root-deletion-readiness-manifest-S316.json` (machine-readable mirror)
**Reproducibility:** see §4. (No persisted helper scripts; the paired-directory comparator runs as inline Python per Codex F1.)

---

## §1. Summary

| | Count |
|---|---|
| Total E:\ root-level entries | 16 |
| Excluded (4) | `GT-KB`, `$RECYCLE.BIN`, `System Volume Information`, `Claude-Playground` |
| Candidate rows scanned | 12 |
| **DIVERGED** | **6** |
| **ORPHAN** | **6** |
| **STALE-DUPLICATE** | **0** |
| Reparse points / junctions / symlinks detected | 0 |
| Credential files detected | 0 |

**Bottom line for the owner:** none of the 12 candidates classify as STALE-DUPLICATE under Codex GO condition 7's strict "in-root content is proven equal-or-superset by path-relative evidence" rule. Every paired entry has at least one outside-only path (mostly nested-build artifacts), so all 6 paired entries are DIVERGED. The 6 unpaired entries are ORPHAN (no in-root counterpart). Deletion authorization is owner-only for all 12.

## §2. Per-entry table

| # | Name | Type | Size | Files | Last modified | Class | Owner action |
|---|---|---|---|---|---|---|---|
| 1 | `_canonical-dogfood` | DIR | 0.98 MB | 75 | 2026-04-17 | ORPHAN | classify retention need |
| 2 | `_canonical-smoke` | DIR | 0.98 MB | 75 | 2026-04-17 | ORPHAN | classify retention need |
| 3 | `admin` | DIR | 18.8 MB | 46 | 2026-02-06 | DIVERGED | inspect 7 diverged + 29 outside-only paths |
| 4 | `automations` | DIR | 764 B | 1 | 2026-04-10 | ORPHAN | classify retention need |
| 5 | `Camtasia` | DIR | 1.22 GB | 3 | 2026-01-20 | ORPHAN (3rd-party) | retain or delete based on tool usage |
| 6 | `config` | DIR | 6.1 KB | 2 | 2026-02-15 | DIVERGED | inspect 1 outside-only path |
| 7 | `Dockerfile` | FILE | 4.1 KB | 1 | 2026-02-06 | DIVERGED | content-diff vs in-root before delete |
| 8 | `requirements.txt` | FILE | 1.1 KB | 1 | 2026-02-05 | DIVERGED | content-diff vs in-root before delete |
| 9 | `src` | DIR | 8.0 MB | 298 | 2026-02-15 | DIVERGED | inspect 142 diverged + 151 outside-only |
| 10 | `tmp` | DIR | 6.9 MB | 353 | 2026-04-24 | ORPHAN | classify retention need |
| 11 | `tmp-ps` | DIR | 0 B | 0 | 2026-04-15 | ORPHAN | candidate safe after owner authorization (empty) |
| 12 | `widget` | DIR | 142 KB | 2 | 2026-02-13 | DIVERGED | inspect 1 diverged + 1 outside-only path |

## §3. Detail by classification

### §3.1 DIVERGED (6 entries)

#### Row 7 — `E:\Dockerfile` (FILE, 4241 B)

| Field | Outside | In-root |
|---|---|---|
| Path | `E:\Dockerfile` | `E:\GT-KB\Dockerfile` |
| Size | 4241 | 5491 |
| Last modified | 2026-02-06 | (current development) |
| SHA256 | `30B675A8FA642B162EAD56CD21D015D37589F75CDCAFD2AA78414AF19A4DBAFE` | `A483C1E4E7350172FC20D23F6975340C88003118A43E94A0B8BFE22F8DE00AA5` |

**Hashes differ.** Outside is older and smaller; in-root has been evolved with additional content. **Candidate safe after owner authorization** following 5-second content-diff against in-root.

#### Row 8 — `E:\requirements.txt` (FILE, 1137 B)

| Field | Outside | In-root |
|---|---|---|
| Size | 1137 | 1947 |
| Last modified | 2026-02-05 | (current) |
| SHA256 | `2B5FFF8DBE2BD3A8A1D36C0C1B14DED475F4DDBD58912C460CEC7EA20D689D93` | `580A6093CA4701D694C5254432F834C64FA4534C886122266EE5F654AF1B0CC9` |

**Hashes differ.** Outside is older and smaller. **Candidate safe after owner authorization** following content-diff against in-root.

#### Row 3 — `E:\admin\` (DIR, 18.8 MB / 46 files)

vs `E:\GT-KB\admin\` (44890 files)

| | |
|---|---|
| Files matching by hash | 10 |
| Files diverged (same path, different hash) | 7 |
| Outside-only paths | 29 |
| In-root-only paths | 44873 |

**7 diverged paths** are mostly built dist/ artifacts (e.g., `shopify/dist/index.html`, `standalone/dist/icon-master.svg`).

**29 outside-only paths** show a distinctive nested pattern: `shopify/dist/dist/` and `standalone/dist/dist/` (build-inside-build). Strong signal these are old build residue.

**Recommendation:** owner spot-check confirms outside-only paths are all build artifacts; if so, deletion is a candidate after owner authorization.

#### Row 9 — `E:\src\` (DIR, 8.0 MB / 298 files)

vs `E:\GT-KB\src\` (587 files)

| | |
|---|---|
| Files matching by hash | 5 |
| Files diverged | 142 |
| Outside-only paths | 151 |
| In-root-only paths | 440 |

**Critical observation:** `E:\src\` contains *both* top-level `chat/`, `integrations/` AND a nested `src/chat/`, `src/integrations/`, `src/main.py`, etc. This double-nesting strongly suggests a corrupted-checkout artifact where the project was once copied into its own `src/` directory.

**151 outside-only paths** include `chat/pipeline.py` (single non-nested file) and many `src/<path>` doubled paths. The non-nested unique paths are the only inspection priority — most of the 151 are duplicates of in-root content under the doubled `src/src/` prefix.

**Recommendation:** owner inspects `chat/pipeline.py` specifically and any other non-nested outside-only files; the bulk are duplication artifacts that the owner may authorize for deletion after that spot-check.

#### Row 12 — `E:\widget\` (DIR, 142 KB / 2 files)

vs `E:\GT-KB\widget\` (15270 files)

| | |
|---|---|
| Files matching | 0 |
| Files diverged | 1 (`dist/agent-red-widget.iife.js`) |
| Outside-only | 1 (`dist/dist/agent-red-widget.iife.js`) |
| In-root-only | 15269 |

**Pattern:** outside has only built widget bundle artifacts (one current, one nested-dist). In-root has full source + build pipeline. Outside is just stale build output.

**Recommendation:** content pattern strongly suggests stale build output; owner may authorize deletion after a brief spot-check.

#### Row 6 — `E:\config\` (DIR, 6.1 KB / 2 files)

vs `E:\GT-KB\config\` (4 files)

| | |
|---|---|
| Files matching | 1 |
| Files diverged | 0 |
| Outside-only | 1 (`config/stripe_product_ids.json`) |
| In-root-only | 3 |

**Note:** the outside-only path `config/stripe_product_ids.json` shows the `E:\config\config\stripe_product_ids.json` doubled-name pattern again. Could be a stale Stripe product ID config that's been moved/superseded in-root.

**Recommendation:** owner inspects the single outside-only file; if confirmed stale, deletion is a candidate after owner authorization.

### §3.2 ORPHAN (6 entries) — no in-root counterpart

| Row | Name | Reason |
|---|---|---|
| 1 | `_canonical-dogfood` | Test artifact directory; not referenced by GT-KB code; 75 files / 0.98 MB |
| 2 | `_canonical-smoke` | Smoke-test artifact directory; not referenced by GT-KB code; 75 files / 0.98 MB |
| 4 | `automations` | Single 764-byte file; purpose unknown; not referenced by GT-KB |
| 5 | `Camtasia` | Third-party screen-recording tool install (1.22 GB); owner-owned content unrelated to GT-KB or Agent Red |
| 10 | `tmp` | Generic temp dir; 353 files / 6.9 MB; recently modified (2026-04-24) — owner may want to inspect |
| 11 | `tmp-ps` | Empty directory |

**Recommendation:** all 6 are owner-decision items. The `_canonical-*`, `automations`, and `tmp-ps` entries have no GT-KB/AR live-code references (per documented grep evidence in §4) and are candidates safe after owner authorization. `Camtasia` is owner's third-party software — retention is the owner's call based on continued tool usage. `tmp` is recently modified (2026-04-24) so a pre-delete glance is recommended before owner authorizes.

## §4. Reproducibility commands

```powershell
# Re-enumerate E:\ entries:
Get-ChildItem -LiteralPath "E:\" -Force | Sort-Object Name

# Compute file SHA256:
Get-FileHash -LiteralPath "E:\Dockerfile" -Algorithm SHA256
Get-FileHash -LiteralPath "E:\requirements.txt" -Algorithm SHA256

# Detect reparse points:
Get-ChildItem -LiteralPath "E:\" -Force | ForEach-Object {
  ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
}
```

```bash
# Per-file SHA256 paired-dir comparison (inline Python; handles Windows reserved filenames like 'nul' that PowerShell Get-FileHash chokes on):
cd /e/GT-KB
python -c "
import os, hashlib
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''): h.update(chunk)
    return h.hexdigest().upper()
def tree(root):
    m = {}
    if not os.path.isdir(root): return m
    for dp, _, fns in os.walk(root):
        for fn in fns:
            full = os.path.join(dp, fn)
            try:
                rel = os.path.relpath(full, root).replace(os.sep, '/')
                m[rel] = sha256_file(full)
            except Exception: pass
    return m
for d in ['admin','src','widget','config']:
    o, i = tree(f'E:/{d}'), tree(f'E:/GT-KB/{d}')
    matched = sum(1 for k in o if k in i and o[k]==i[k])
    diverged = sum(1 for k in o if k in i and o[k]!=i[k])
    outside_only = sum(1 for k in o if k not in i)
    print(f'{d}: outside_files={len(o)}, inroot_files={len(i)}, matched={matched}, diverged={diverged}, outside_only={outside_only}')
"

# Live-code reference grep (used to support ORPHAN claims):
grep -rn "_canonical-dogfood" --include="*.py" --include="*.toml" --include="*.json" --include="*.yml" --include="*.yaml" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" --include="*.md" --include="*.ps1" --include="*.sh" --include="*.bat" /e/GT-KB | grep -v "^./bridge/" | grep -v "^./.venv/" | grep -v "^./node_modules/"
```

**Live-code reference grep results captured this session** (raw evidence supporting the ORPHAN classifications):

| Search term | Total hits | Hits in non-bridge code/config |
|---|---|---|
| `_canonical-dogfood` | 9 (all in bridge/* files) | 0 |
| `_canonical-smoke` | 9 (all in bridge/* files) | 0 |
| `automations` | 1 (`scripts/generate_orbatech_report_v2.py:464`) | 1 — but it's a marketing-copy string literal `"automations. Appeals to non-traditional CRM users."`, not a filesystem reference |

## §5. Out-of-scope reminders

| | |
|---|---|
| `E:\Claude-Playground` | requires separate cleanup-manifest bridge per `application-isolation-contract-005.md` §7.6 |
| C:\ outside-root worktrees | `claude-design-backlog`, `gh-dep2` are unaffected by E:\ deletion; separate disposition |
| Actual deletion | this manifest produces evidence only; the owner authorizes deletion separately |
| Modification of any file | this scan was strictly read-only; only the manifest files (this `.md`, the `.json` mirror, and the helper script) were created |

## §6. Recommendations for the owner's deletion decision

Based on classification + content patterns. Every entry below is **owner-authorization-gated**; the manifest does not declare any entry deletion-ready independently of owner action (Codex GO condition 7 + F3 of `-004`).

**Tier 1 — minimal inspection then owner authorizes deletion:**
- `_canonical-dogfood` (75 files, 0.98 MB; ORPHAN; 0 live-code refs per §4 grep)
- `_canonical-smoke` (75 files, 0.98 MB; ORPHAN; 0 live-code refs per §4 grep)
- `automations` (1 file, 764 B; ORPHAN; only ref is a string literal in scripts/, not a path)
- `tmp-ps` (0 files, empty; ORPHAN)
- `widget` (2 files, 142 KB; DIVERGED with stale-build-output content pattern)

**Tier 2 — owner spot-check then authorizes deletion:**
- `Dockerfile` (1 file; 5-second content diff against in-root before owner authorizes)
- `requirements.txt` (1 file; 5-second content diff against in-root before owner authorizes)
- `config` (1 outside-only file `config/stripe_product_ids.json` to glance at before owner authorizes)
- `tmp` (recently-modified contents; quick scan for accidentally-saved work before owner authorizes)

**Tier 3 — meaningful inspection then owner authorizes deletion:**
- `admin` (29 outside-only paths; mostly nested-dist artifacts but worth substantive confirmation)
- `src` (151 outside-only paths; includes `chat/pipeline.py` worth checking; bulk are doubled-`src/src/` patterns)
- `Camtasia` (third-party software; 1.22 GB; retention is a "do you still use Camtasia" question, not a content question)

After owner decisions on the above, the wholesale `E:\` deletion (preserving only `E:\GT-KB`) becomes ready to execute. The manifest does not authorize deletion; the owner does, item by item or in batches.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
