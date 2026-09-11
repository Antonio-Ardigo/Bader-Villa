# 3D model of B2660 — ground and basement

A wall-shell model of both drawn levels, built in Blender from the drawing
set itself rather than by tracing an image.

## Files

| File | What it is |
|---|---|
| `build/bader_villa.blend` | The Blender scene: two collections, `Ground` and `Basement`, plus sun, sky and camera |
| `build/bader_villa.glb` | glTF export, opens in any 3D viewer |
| `build/plan_geometry.json` | The extracted geometry, as 50 mm grid rectangles per level |
| `build/views/*.png` | Cycles renders: each level, an exploded pair, and a view from the street |
| `viewer.html` | Interactive viewer, loads three.js from a CDN |
| `viewer-standalone.html` | The same viewer with three.js bundled in, so it runs offline from a double-click |

## Rebuilding

Needs `pymupdf`, `numpy`, `scipy` and `bpy` (Blender as a Python module,
`pip install bpy`). No Blender GUI is required.

```
python3 tools/extract_plan.py          # PDF  -> build/plan_geometry.json
python3 tools/build_model.py           # JSON -> .blend and .glb
python3 tools/render_views.py 64 1600  # .blend -> build/views/*.png
```

## How the geometry was obtained

The PDF was exported from AutoCAD with its layers intact as PDF
optional-content groups, so the `WALLS` layer can be rendered alone. On that
layer every wall is a closed outline. Filling those outlines, and keeping only
the enclosed regions too thin to survive being eroded by half a wall
thickness, separates wall solids from rooms without any tracing.

Scale comes from the 24010 mm street frontage printed on the sheet. Two
independent checks confirm it:

| Check | Model | Sheet |
|---|---|---|
| Plot depth | 20016 mm | 20025 mm |
| Enclosed lot area | 472.4 m² | 472.40 m² |
| Enclosed basement area | 369.1 m² | 369.10 m² |

Openings are the gaps in the wall outlines. A gap the glazing layer touches is
given a sill and a head, so it reads as a window; every other gap gets a head
only, so it reads as a door.

## Assumptions

No level, height or section appears anywhere in this set. These are stated
assumptions, all set at the top of `tools/build_model.py`:

| Assumption | Value |
|---|---|
| Clear height | 3.20 m |
| Slab thickness | 0.40 m |
| Door and window head | 2.20 m |
| Window sill | 0.90 m |

## Limits

- Walls only. Furniture, stairs, door leaves and glazing sit on other layers
  and are deliberately not modelled.
- Two levels only, because only two are drawn.
- The west plot boundary is slightly splayed and is approximated to the 50 mm
  grid, so it steps rather than runs true.
- The sun is placed for legibility, not for solar position. The sheet's
  compass contradicts its own boundary labels, so the model's orientation
  follows the written labels and should be confirmed before any sun study.
