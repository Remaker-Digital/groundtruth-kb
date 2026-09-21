# Project templates

These files are packaged with GroundTruth-KB for its project scaffold and
project-owned CI and container configuration. Follow the
[native setup guide](../docs/start-here.md) to register and initialize an
application, bind its execution project and install its hooks.

The native scaffold selects the CI files under `ci/` and container files under
`project/` for the requested profile. Review the resulting project-owned files
before using them. Initialization and upgrade also install the supported hook
entry points from the selected GT-KB installation.

Harness instructions come from the shared authored baseline and its projector.
Run the supported initialization, upgrade or projection command when those
outputs need refreshing. Direct edits or manual template copies into generated
harness directories are not the source of truth.

To locate the packaged templates for inspecting or customizing project-owned
CI and container files:

```python
from groundtruth_kb import get_templates_dir
print(get_templates_dir())
```

Current bridge state and project records are read through the native CLI and
service. The owner selects work until the replacement dispatcher is qualified
and activated; these templates do not install an automatic dispatcher.
