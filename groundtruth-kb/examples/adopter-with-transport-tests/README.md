# adopter-with-transport-tests

Demonstrates the **transport-contract test pattern**: an adopter-side test
suite that asserts the request/response shape of an external transport
without coupling to production endpoints. The structure mirrors the
Phase 3/4/5 transport patterns at scale, minimized to a 3-test demonstration.

## Run the example

```bash
# Copy the example tree to a workspace location of your choosing
cp -r examples/adopter-with-transport-tests/ ~/projects/transport-app/
cd ~/projects/transport-app/
git init && git add -A && git commit -m "initial"

# Verify the isolation contract
gt project doctor --profile dual-agent

# Run the example's transport tests in isolation (the example ships its
# own pyproject.toml, so the example's pytest invocation is independent
# of the platform's pytest lane).
python -m pytest tests/ -v
```

Expected outcome: `gt project doctor` reports every `isolation:*` check as
`pass` or `info`; the example's `tests/test_transport_contract.py` runs to
completion (the placeholder assertions exercise the request/response shape).

## Dashboard rendering

The dashboard rendering walkthrough exercises the overlay and service
surfaces together for an adopter that has indexed its transport tests
into the chroma overlay.

```bash
# Initialize chroma overlay against the adopter's groundtruth.db
gt deliberations rebuild-index --adopter-root ~/projects/transport-app/

# Render the dashboard
gt dashboard render --adopter-root ~/projects/transport-app/
```

The dashboard surfaces:

- **Service health** from `[service].endpoint` in `groundtruth.toml` —
  reports the placeholder state until you override the endpoint.
- **Overlay state** from `.groundtruth-chroma/` — reports the indexed
  transport-test deliberations and any cross-references.

Both surfaces appear in the same render so you can see the transport
contract's documented behavior alongside the indexed deliberations.

## See also

- [Application/Platform Isolation](../../docs/architecture/isolation.md)
- [cli.md](../../docs/reference/cli.md)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
