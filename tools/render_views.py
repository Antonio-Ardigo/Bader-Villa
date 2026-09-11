"""Render preview images of the Bader Villa model.

Usage: python3 tools/render_views.py [samples] [width]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Vector

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SHOTS = BUILD / "views"

VIEWS = {
    # name: (camera position, target, collections shown, basement drop, show site)
    # north is +Y: the 15 m street runs along the +Y edge of the plot
    "ground_aerial":   ((20, 30, 30), (0, 0, 0), {"Ground"}, 0.0, True),
    # the basement is lifted to grade so it reads the same way as the ground floor
    "basement_aerial": ((20, 30, 30), (0, 0, 0), {"Basement"}, -3.6, True),
    "exploded":        ((28, 33, 14), (0, 0, -3), {"Ground", "Basement"}, 9.0, False),
    "street":          ((15, 31, 8), (0, 1, 1.5), {"Ground", "Basement"}, 0.0, True),
}


def aim(cam, at):
    d = Vector(at) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def main():
    samples = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 1600
    bpy.ops.wm.open_mainfile(filepath=str(BUILD / "bader_villa.blend"))
    SHOTS.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.cycles.samples = samples
    scene.render.resolution_x = width
    scene.render.resolution_y = int(width * 0.625)
    cam = scene.camera

    basement = bpy.data.collections["Basement"]
    base_z = {ob.name: ob.location.z for ob in basement.objects}

    site = bpy.data.objects["Site"]
    for name, (pos, target, show, explode, show_site) in VIEWS.items():
        site.hide_render = not show_site
        for coll in bpy.data.collections:
            hide = coll.name not in show
            coll.hide_render = hide
        for ob in basement.objects:
            ob.location.z = base_z[ob.name] - explode
        cam.location = Vector(pos)
        aim(cam, target)
        scene.render.filepath = str(SHOTS / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name)

    for ob in basement.objects:
        ob.location.z = base_z[ob.name]


if __name__ == "__main__":
    main()
