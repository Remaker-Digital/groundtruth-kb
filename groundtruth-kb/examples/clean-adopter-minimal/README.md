# clean-adopter-minimal

Smallest possible adopter that passes `gt project doctor` invariants and
satisfies the GTKB-ISOLATION-017 contract. This example is the reference
"empty starting point" for new adopters.

## Run the example

```bash
# Copy the example tree to a workspace location of your choosing
# (anywhere outside <gt-kb-root>, e.g. ~/projects/myapp/).
cp -r examples/clean-adopter-minimal/ ~/projects/myapp/
cd ~/projects/myapp/
git init && git add -A && git commit -m "initial"

# Verify the isolation contract
gt project doctor --profile local-only
```

Expected outcome: every `isolation:*` check reports `pass` or `info`. No
`fail` statuses on a freshly copied tree.

## Dashboard rendering

The minimal adopter does not yet have a real service endpoint or a chroma
overlay populated. The dashboard rendering walkthrough below shows what to
expect once both surfaces are wired up.

```bash
# Optional: install the dashboard extra
pip install 'groundtruth-kb[web]'

# Initialize the dashboard against this adopter
gt dashboard init --adopter-root ~/projects/myapp/

# Render the dashboard. Two surfaces appear together:
#   - service health  → from [service].endpoint in groundtruth.toml
#   - overlay state   → from .groundtruth-chroma/ (empty until the first index build)
gt dashboard render --adopter-root ~/projects/myapp/
```

While the placeholder endpoint `configure-me://placeholder/v1` is in place,
the dashboard reports the service block as "configured (placeholder)" and
the overlay block as "absent (no orphan cache)" together — both surfaces
visible in the same render.

## See also

- [Application/Platform Isolation](../../docs/architecture/isolation.md) —
  the isolation contract this example satisfies.
- [cli.md](../../docs/reference/cli.md) — full `gt project doctor` flag inventory.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
