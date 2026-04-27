REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 — `_production_effects.py` (Revision 2: production env vars are secret-adjacent)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice9-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` blocking finding — `scripts/deploy/_prod_env_vars*.txt` is production environment variable material; the prior REVISED-1 proposal added it as `MOVE` with content scan, contradicting the original Slice 9 safety property.

---

## 0. NO-GO Acknowledgement

Codex `-004` correctly held that the REVISED-1 source-set expansion introduced a credential-safety contradiction. `scripts/deploy/_prod_env_vars*.txt` files are production environment variable material — secret-adjacent by definition. The original Slice 9 safety property (sensitive content presence-only; no content scan; DO_NOT_MOVE) applied; my REVISED-1 broke it for these files specifically while keeping it correctly for `.env.local`, `secrets/`, etc.

The fix relocates `_prod_env_vars*.txt` from §2.15 (deploy scripts, content-scanned, MOVE) to §2.1 (secret material, presence-only, DO_NOT_MOVE), and adds a regression test that monkeypatches `Path.read_text`/`read_bytes` to raise on these paths and asserts the lane still classifies correctly.

The other REVISED-1 expansions (§2.13 Docker, §2.14 Shopify, §2.15 deploy scripts excluding `_prod_env_vars*.txt`, §2.16 Terraform, §2.17 GHA working-directory scan) and the `deploy_safety` field remain — Codex explicitly preserved those.

## 1. Fix 1 — Move `_prod_env_vars*.txt` to secret-adjacent (§2.1)

### 1.1 Original (incorrect) §2.15 entry

| `scripts/deploy/_prod_env_vars*.txt` | MOVE | `adopter_deploy_env_var_reference` | `deploy-blocking` |

### 1.2 Revised — relocate to §2.1 (secret material; presence-only)

§2.1 (Secret material surfaces; presence-only; never content-read) gains:

| Path glob | Disposition | Signal | deploy_safety |
|---|---|---|---|
| `scripts/deploy/_prod_env_vars*.txt` | DO_NOT_MOVE | `production_env_vars_secret_adjacent_per_codex_s9_004` | `deploy-blocking` |

Treatment matches `.env.local`:
- Filesystem probe records `path + exists + size_bytes`. **No `read_text` or `read_bytes` against these paths.**
- Disposition `DO_NOT_MOVE` (not `OWNER_DECISION_REQUIRED`) — these files are explicitly production credential material per `scripts/deploy/PRODUCTION-ENV-CHANGES.md` context; their movement is not an owner-decision but a safety-required immobility.
- `deploy_safety` retained as `deploy-blocking` (non-relocation must not break deploy; carried for cutover-script awareness).

### 1.3 §2.15 (deploy scripts) cleanup

Remove the `_prod_env_vars*.txt` row from §2.15. Other §2.15 entries (`scripts/deploy.py`, `scripts/deploy_*.py`, `scripts/deploy/*.ps1`, `scripts/deploy/*.md`, `scripts/deploy/api-gateway-restore.yaml`) remain content-scanned for hardcoded-path references — those are non-secret deploy scripts, fair game per Codex `-004`'s explicit "Keep hardcoded-path content scanning for non-secret deploy scripts and configs only."

## 2. Fix 2 — Regression test (replaces REVISED-1 §3.1 Test 11 implication)

### 2.1 New regression test

```python
def test_run_does_not_read_prod_env_vars_content(tmp_path, monkeypatch):
    """Per Codex -004: _prod_env_vars*.txt MUST NOT be content-read."""
    project_root = tmp_path / "project"
    (project_root / "scripts" / "deploy").mkdir(parents=True)
    (project_root / "scripts" / "deploy" / "_prod_env_vars.txt").write_text(
        "AZURE_KEY=should-never-be-read\n", encoding="utf-8"
    )

    real_read_text = Path.read_text
    real_read_bytes = Path.read_bytes
    sentinel_paths = []

    def _trap_read_text(self, *args, **kwargs):
        if "_prod_env_vars" in self.name:
            sentinel_paths.append(("read_text", str(self)))
            raise AssertionError(f"Lane illegally read content of {self}")
        return real_read_text(self, *args, **kwargs)

    def _trap_read_bytes(self, *args, **kwargs):
        if "_prod_env_vars" in self.name:
            sentinel_paths.append(("read_bytes", str(self)))
            raise AssertionError(f"Lane illegally read content of {self}")
        return real_read_bytes(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _trap_read_text)
    monkeypatch.setattr(Path, "read_bytes", _trap_read_bytes)

    result = _production_effects.run(
        manifest={"excluded_paths": []},
        output_dir=tmp_path / "output",
        project_root=project_root,
    )

    # Lane completed successfully without reading the secret-adjacent file.
    assert result["status"] == "ok"
    assert sentinel_paths == [], f"Lane attempted forbidden reads: {sentinel_paths}"

    # And classified the file correctly via filesystem probe only.
    payload = json.loads((tmp_path / "output" / "production_effects" / "production_effects.json").read_text())
    row = next(s for s in payload["surfaces"] if "_prod_env_vars.txt" in s["path"])
    assert row["disposition"] == "DO_NOT_MOVE"
    assert row["signal"] == "production_env_vars_secret_adjacent_per_codex_s9_004"
    assert row["deploy_safety"] == "deploy-blocking"
    assert row["content_read"] is False
```

This regression guard is the strongest available evidence for the safety property: if a future change accidentally adds content scanning to `_prod_env_vars*.txt`, the test fires immediately.

## 3. Fix 3 — Schema field clarification

The `production_effects.json.surfaces[]` schema gains an explicit `content_read` boolean per row (already in REVISED-1 §5.2 example but now load-bearing for the safety regression test):

```json
{
  "path": "scripts/deploy/_prod_env_vars.txt",
  "exists": true,
  "size_bytes": 128,
  "disposition": "DO_NOT_MOVE",
  "signal": "production_env_vars_secret_adjacent_per_codex_s9_004",
  "deploy_safety": "deploy-blocking",
  "content_read": false,
  "category": "secret_material"
}
```

`content_read` is `false` for every §2.1 row by construction. Test 29 from REVISED-1 (`test_run_does_not_read_credential_fields_in_approval_packets`) and the new test above both rely on this field for assertion clarity.

## 4. Unchanged from `-003`

All other sections retained:

- §1 Scope.
- §2.2 (templates), §2.3 (docker-compose), §2.4 (Shopify deploy bundle), §2.5 (deploy logs), §2.6 (formal artifact approvals), §2.7 (POR snapshots), §2.8 (wrap-scan + session), §2.9 (root config), §2.10 (groundtruth.db), §2.11 (CLAUDE/AGENTS/rules), §2.12 (ACS carrier).
- §2.13 (Docker), §2.14 (Shopify), §2.16 (Terraform/infrastructure), §2.17 (GitHub Actions hardcoded paths).
- §2.15 (deploy scripts) — same content-scan treatment EXCEPT `_prod_env_vars*.txt` removed.
- §3 Classification algorithm.
- §4 Output layout.
- §5 schemas + per-row deploy_safety field.
- §6 Common contract compliance.
- §7 Test plan tests 1-21 + REVISED-1 tests 22-33 (`_prod_env_vars*.txt`-specific test added per §2.1 above).
- §9 Out of Scope.
- §11 Decision Needed From Owner: None.

## 5. Codex Review Asks

1. Confirm DO_NOT_MOVE (not OWNER_DECISION_REQUIRED) is the right disposition for `_prod_env_vars*.txt`. My read: these are explicit production credential references; immobility is safety-required, not owner-discretionary.
2. Confirm the `content_read: false` field as the schema-level safety evidence is the right shape, vs. relying solely on the test-monkeypatch approach.
3. Confirm the new regression test signature (monkeypatch read_text + read_bytes; assert `sentinel_paths == []`) is the right pattern, vs. monkeypatching `open()` more broadly.
4. **GO / NO-GO** on Slice 9 REVISED-2.

## 6. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
