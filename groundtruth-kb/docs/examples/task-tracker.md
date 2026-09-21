# Adopter Fixtures

The repository includes three small adopter fixtures for checking project layout
and isolation. Their tests copy each fixture into an isolated directory and run
the doctor. They are useful references for scaffold structure.

| Fixture | Purpose |
| --- | --- |
| [clean-adopter-minimal](../../examples/clean-adopter-minimal/README.md) | Minimal project layout and local-only scaffold profile. |
| [adopter-with-transport-tests](../../examples/adopter-with-transport-tests/README.md) | Layout used to exercise the transport-test scaffold. |
| [adopter-with-release-gate](../../examples/adopter-with-release-gate/README.md) | Layout used to exercise the release-gate scaffold. |

Run their existing smoke checks from the platform checkout:

```bash
python -m pytest groundtruth-kb/tests/test_examples_pass_doctor.py
```

These checks establish the fixture layout and the doctor's isolation findings.
Connecting an adopter to a native authority requires its own configured service,
current application scope and applicable project records. A fixture smoke pass
does not establish those operational conditions.

For a specification and executable-test walkthrough in your own configured
project, use [Your First Specification](../tutorials/first-spec.md). For the
hosted application boundary, see [Isolation](../architecture/isolation.md).
