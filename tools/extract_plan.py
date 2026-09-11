"""Extract wall / door / glazing masks from the B2660 PDF, one per floor.

The PDF kept its AutoCAD layers as PDF optional-content groups, so each layer
can be rendered on its own. Walls are drawn as closed outlines; this turns
them into solid regions, calibrates them against the 24010 mm plot frontage
printed on the sheet, and writes a 50 mm grid the Blender build can consume.
"""
import json
import pathlib

import numpy as np
import pymupdf
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / "B2660-REV02- ( GROUND & BASEMENT).pdf"
OUT = ROOT / "build"
CLIP = pymupdf.Rect(250, 40, 980, 740)   # the plan, clear of the title block
DPI = 300
PLOT_FRONTAGE_MM = 24010.0               # bottom (street) dimension, both sheets
CELL_MM = 50.0
MAX_WALL_MM = 800.0                      # nothing in this plan is a thicker wall


def render_layers(page_no, names, dpi=DPI):
    """Render one page with only the named optional-content groups visible."""
    doc = pymupdf.open(PDF)
    for cfg in doc.layer_ui_configs():
        if cfg["type"] == "checkbox":
            doc.set_layer_ui_config(cfg["number"], 0 if cfg["text"] in names else 1)
    pix = doc[page_no].get_pixmap(dpi=dpi, clip=CLIP, colorspace=pymupdf.csGRAY)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()
    doc.close()
    return arr < 170


def erode_square(mask, r):
    """Erosion by a (2r+1) square, done as two 1-D passes so it stays fast."""
    m = ndimage.binary_erosion(mask, np.ones((1, 2 * r + 1), bool))
    return ndimage.binary_erosion(m, np.ones((2 * r + 1, 1), bool))


def plot_boundary_bbox(lines):
    """Bounding box of the plot boundary, ignoring stray table fragments."""
    lab, n = ndimage.label(lines, structure=np.ones((3, 3), bool))
    best, best_span = None, -1
    for sl in ndimage.find_objects(lab):
        span = (sl[0].stop - sl[0].start) + (sl[1].stop - sl[1].start)
        if span > best_span:
            best, best_span = sl, span
    return best


def wall_solid(lines, px_per_mm):
    """Fill the closed wall outlines, leaving rooms and outside empty."""
    lines = ndimage.binary_closing(lines, np.ones((3, 3), bool))
    free = ~lines
    lab, n = ndimage.label(free)
    # a room survives erosion by half a wall thickness; a wall's interior does not
    r = max(1, int(round(MAX_WALL_MM / 2 * px_per_mm)))
    fat = set(np.unique(lab[erode_square(free, r)]).tolist())
    border = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    drop = np.zeros(n + 1, bool)
    for i in fat | set(int(x) for x in border) | {0}:
        if 0 <= i <= n:
            drop[i] = True
    return ndimage.binary_closing(lines | ~drop[lab], np.ones((3, 3), bool))


def greedy_rects(mask):
    """Cover a boolean mask with a small set of axis-aligned rectangles."""
    m = mask.copy()
    h, w = m.shape
    out = []
    for y in range(h):
        x = 0
        while x < w:
            if not m[y, x]:
                x += 1
                continue
            run = np.argmin(m[y, x:])
            rw = int(run) if not m[y, x:].all() else w - x
            rh = 1
            while y + rh < h and m[y + rh, x:x + rw].all():
                rh += 1
            out.append((int(x), int(y), int(rw), int(rh)))
            m[y:y + rh, x:x + rw] = False
            x += rw
    return out


def drop_specks(mask, px_per_mm, min_sqm=0.05):
    """Remove tree symbols and stray title-block fragments."""
    lab, n = ndimage.label(mask, structure=np.ones((3, 3), bool))
    if n == 0:
        return mask
    min_px = min_sqm * 1e6 * px_per_mm ** 2
    sizes = np.bincount(lab.ravel())
    keep = sizes >= min_px
    keep[0] = False
    return keep[lab]


def openings(solid, doors, glazing, px_per_mm):
    """Find wall gaps, and say which ones are glazed.

    A gap is what a closing along the wall's own direction adds back. Gaps
    bigger than a normal opening are dropped so that narrow rooms are not
    mistaken for a doorway.
    """
    n = max(3, int(round(2000 * px_per_mm)))
    bridged = (ndimage.binary_closing(solid, np.ones((1, n), bool))
               | ndimage.binary_closing(solid, np.ones((n, 1), bool)))
    gaps = bridged & ~solid
    lab, count = ndimage.label(gaps, structure=np.ones((3, 3), bool))
    max_px = 5.0 * 1e6 * px_per_mm ** 2
    glaz = ndimage.binary_dilation(glazing, np.ones((9, 9), bool))
    door = ndimage.binary_dilation(doors, np.ones((9, 9), bool))
    lintel = np.zeros(count + 1, bool)
    sill = np.zeros(count + 1, bool)
    sizes = np.bincount(lab.ravel())
    for i in range(1, count + 1):
        if sizes[i] > max_px:
            continue
        sel = lab == i
        lintel[i] = True
        if glaz[sel].any() and not door[sel].any():
            sill[i] = True
    return lintel[lab], sill[lab]


def to_grid(mask, px_per_mm):
    cell_px = CELL_MM * px_per_mm
    gh = int(mask.shape[0] / cell_px)
    gw = int(mask.shape[1] / cell_px)
    yi = np.clip((np.arange(gh) * cell_px + cell_px / 2).astype(int), 0, mask.shape[0] - 1)
    xi = np.clip((np.arange(gw) * cell_px + cell_px / 2).astype(int), 0, mask.shape[1] - 1)
    return mask[np.ix_(yi, xi)]


def main():
    OUT.mkdir(exist_ok=True)
    ground_lines = render_layers(0, {"WALLS"})
    bb = plot_boundary_bbox(ground_lines)
    px_per_mm = (bb[1].stop - bb[1].start) / PLOT_FRONTAGE_MM
    print(f"plot boundary: {bb[1].stop - bb[1].start} x {bb[0].stop - bb[0].start} px")
    print(f"scale: {px_per_mm:.5f} px/mm ({1 / px_per_mm:.2f} mm/px)")
    print(f"implied plot depth: {(bb[0].stop - bb[0].start) / px_per_mm:.0f} mm "
          f"(sheet says 20025)")

    pad = int(round(200 * px_per_mm))
    keep = np.zeros_like(ground_lines)
    keep[max(0, bb[0].start - pad):bb[0].stop + pad,
         max(0, bb[1].start - pad):bb[1].stop + pad] = True

    meta = {"px_per_mm": px_per_mm, "cell_mm": CELL_MM,
            "origin_px": [int(bb[1].start), int(bb[0].start)], "floors": {}}

    for page_no, name in ((0, "ground"), (1, "basement")):
        lines = ground_lines if page_no == 0 else render_layers(page_no, {"WALLS"})
        lines = lines & keep
        solid = drop_specks(wall_solid(lines, px_per_mm), px_per_mm)
        doors = render_layers(page_no, {"A-DOOR"})
        glazing = render_layers(page_no, {"A-GLAZING"})
        lintel, sill = openings(solid, doors, glazing, px_per_mm)
        slab = ndimage.binary_fill_holes(solid)
        if slab.sum() < 1.5 * solid.sum():
            # the fill leaked: this outline is broken by a gate. Bridge and retry.
            n = max(3, int(round(4000 * px_per_mm)))
            bridged = (ndimage.binary_closing(solid, np.ones((1, n), bool))
                       | ndimage.binary_closing(solid, np.ones((n, 1), bool)))
            slab = ndimage.binary_fill_holes(bridged)

        grids = {k: to_grid(v, px_per_mm)
                 for k, v in (("wall", solid), ("lintel", lintel),
                              ("sill", sill), ("slab", slab))}
        meta["floors"][name] = {
            "grid_w": int(grids["wall"].shape[1]),
            "grid_h": int(grids["wall"].shape[0]),
            **{f"{k}_rects": greedy_rects(v) for k, v in grids.items()},
            "wall_area_sqm": round(float(grids["wall"].sum()) * (CELL_MM / 1000) ** 2, 1),
            "slab_area_sqm": round(float(grids["slab"].sum()) * (CELL_MM / 1000) ** 2, 1),
        }
        np.save(OUT / f"wall_{name}.npy", solid)
        f = meta["floors"][name]
        print(f"{name:9s}: {len(f['wall_rects']):4d} wall boxes, "
              f"{len(f['lintel_rects']):3d} lintel, {len(f['sill_rects']):3d} sill, "
              f"{len(f['slab_rects']):3d} slab | wall {f['wall_area_sqm']} sqm, "
              f"enclosed {f['slab_area_sqm']} sqm")

    (OUT / "plan_geometry.json").write_text(json.dumps(meta))
    print("wrote build/plan_geometry.json")


if __name__ == "__main__":
    main()
