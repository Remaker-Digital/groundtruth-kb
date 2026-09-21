# clean-adopter-minimal

This small application tree is an executable fixture for the
GTKB-ISOLATION-017 application/platform isolation contract. The package test
`tests/test_examples_pass_doctor.py` copies it outside the platform tree and
checks the doctor's `isolation:*` results. The fixture does not configure a
native service, register a real application or establish that every doctor
check passes on a standalone copy.

## Inspect the example

Copy the directory outside the GT-KB platform root to inspect its layout.
The example's placeholder configuration and files illustrate the isolation
boundary; replace placeholders through normal project initialization before
using them for a real application.

For an application on a configured host, first register its application root
and select its canonical execution project. Use the supported
`gt project init <APPLICATION> --project-id <PROJECT> --host-root <HOST>
--owner <OWNER>` route, then inspect it with
`gt project doctor --project-id <PROJECT> --host-root <HOST> --json`.
Use the host's configuration with `gt --config <HOST>/groundtruth.toml ...`.
The [CLI reference](../../docs/reference/cli.md#gt-project-init) describes the
registration preconditions, dry-run option and exact command arguments.

## Dashboard

Use the native dashboard commands on the configured host after initialization.
The fixture has no independent dashboard renderer or overlay authority.
See [Dashboard commands](../../docs/reference/cli.md) for the current command
surface and prerequisites.

## See also

- [Application/Platform Isolation](../../docs/architecture/isolation.md)
- [CLI reference](../../docs/reference/cli.md)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
