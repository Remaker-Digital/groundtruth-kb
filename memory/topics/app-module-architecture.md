# App Module Architecture — Operational Patterns

> Full architecture: KB DOC-APP-ARCHITECTURE

## Patch Target Rules (Post-R1 Split)

After R1 split, `patch()` targets must reference the SOURCE module, not re-exports.

1. **Mutable state:** `import src.app.standalone_auth as m; m._admin_password_hash = h` — NOT `src.main`
2. **Functions:** `patch("src.app.standalone_auth._send_admin_reset_email")` — NOT `patch("src.main...")`
3. **lifecycle.py module-level imports** are patchable via `conftest.py`:
   ```python
   import src.app.lifecycle as _lifecycle_mod
   patch.object(_lifecycle_mod, "TenantRepository", ...)
   ```
4. **Lazy imports** (inside function bodies) cannot be patched via `patch.object()` — they re-import on each call

**Re-export exception:** Mutable containers (set, dict, list) share the same object — `.add()`, `.clear()` work across modules. But reassigning (`m._nonces = new_set`) does NOT propagate.

## SPA catch-all swallows static files (S82b)
Vite copies `public/` files to `dist/` root, but only `dist/assets/` is mounted as StaticFiles. The catch-all `/{full_path:path}` returns `index.html` for ALL requests. Fix: check `candidate = dist / full_path; if candidate.is_file(): return FileResponse(candidate)` BEFORE index.html fallback. Applied at `static_serving.py:60,102`.

## NATS decommission false alarm (S82b)
`get_nats_manager()` always creates a non-None instance. Correct pattern: `nats_deployed = nats_connected` — only report deployed if actually connected.
