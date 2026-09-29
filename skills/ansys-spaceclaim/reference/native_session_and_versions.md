# Native SpaceClaim Scripting — Session & Versions

The **native SpaceClaim scripting API** (`SpaceClaim.Api.V<ver>`), used by
recorded scripts and ACT SpaceClaim wizards. This is a DIFFERENT family from
PyAnsys Geometry (`ansys.geometry.core`, see the other reference files) — use
this one for SpaceClaim/Discovery ACT extensions. Tokens verified from real ACT
extensions.

## Load the API (fixed version)

```python
import clr
clr.AddReference("SpaceClaim.Api.V252")
clr.AddReference("SpaceClaim.Api.V252.Scripting")
from SpaceClaim.Api.V252 import IDesignBody, MidSurfaceOffsetType
from SpaceClaim.Api.V252.Scripting.Selection import Selection, BodySelection, FaceSelection
from SpaceClaim.Api.V252.Scripting.Commands import Midsurface
from SpaceClaim.Api.V252.Scripting.Helpers import DocumentHelper, MeasureHelper, ViewHelper, MessageBox
```

Import the C#-extension methods so `face.GetTangentChain()` etc. work:

```python
clr.ImportExtensions(SpaceClaim.Api.V252.Scripting.Extensions.DesignFaceExtensions)
clr.ImportExtensions(SpaceClaim.Api.V252.Scripting.Extensions.DesignEdgeExtensions)
clr.ImportExtensions(SpaceClaim.Api.V252.Scripting.Extensions.DesignBodyExtensions)
clr.ImportExtensions(SpaceClaim.Api.V252.Scripting.Extensions.ComponentExtensions)
clr.ImportExtensions(SpaceClaim.Api.V252.Scripting.Extensions.DocObjectExtensions)
```

## Load the API (version auto-detect — recommended for portability)

Version namespaces change every release (V261, V26, V252, V251, V25, V242, V241,
V24, V232, V231, V23, V19 ...). Detect the installed one:

```python
def get_spaceclaim_api():
    import clr
    for ver in ["V261","V26","V252","V251","V25","V242","V241","V24","V232","V231","V23"]:
        try:
            clr.AddReference("SpaceClaim.Api." + ver)
            clr.AddReference("SpaceClaim.Api." + ver + ".Scripting")
            import SpaceClaim.Api
            sc = getattr(SpaceClaim.Api, ver)
            for ext in ("DesignFaceExtensions","DesignEdgeExtensions","DesignBodyExtensions",
                        "ComponentExtensions","DocObjectExtensions"):
                clr.ImportExtensions(getattr(sc.Scripting.Extensions, ext))
            return sc
        except Exception:
            continue
    raise Exception("No compatible SpaceClaim API version found.")

sc = get_spaceclaim_api()
Selection = sc.Scripting.Selection.Selection      # then reach everything via sc.*
```

With auto-detect, reference types as `sc.Scripting.Commands.Midsurface`,
`sc.Geometry.Cylinder`, `sc.Scripting.Helpers.DocumentHelper`, etc.

## Document, units, components

```python
doc = Window.ActiveWindow.Document
doc.Units.ActiveUnitsSystem = UnitsSystemType.Metric
doc.Units.MetricUnits = MetricUnits(MetricLengthUnit.Millimeters, MetricMassUnit.Grams, AngleUnit.Degrees)

root = DocumentHelper.GetRootPart()               # the root Part (see native_helpers)
comp = ComponentHelper.GetActive()                # active component
ComponentHelper.SetRootActive(None)               # activate root
ComponentHelper.SetActive(comp, None)             # restore
```

## Units helpers (ACT-injected)

`MM(x)`, `MM2(x)`, `DEG(x)` convert mm / mm^2 / degrees into the API's SI values.
Use them around every literal: `Point2D.Create(MM(1.0), MM(0))`, `DEG(360)`.

## ACT wizard entry (how inputs arrive)

As a SpaceClaim ACT wizard, the entry is `onupdateStep(step)` and inputs come
from `step.Properties['Name'].Value`. Standalone recorded scripts instead run at
module top level (no `onupdateStep`). The geometry API is identical either way.

## Notes

- `from SpaceClaim.Api.V<ver> import *` (fixed-version scripts) pulls `Selection`,
  `Point`, `Point2D`, `Direction`, `Vector`, `Line`, `Plane`, `Matrix`, command
  classes, helpers, and enums into scope directly.
- Keep one version idiom per script; mixing fixed-import and `sc.*` gets
  confusing.
