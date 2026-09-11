"""Build the Bader Villa 3D model in Blender from the extracted plan geometry.

Run with:  python3 tools/build_model.py
(bpy is Blender itself as a Python module, so no Blender GUI is needed.)

Heights are not given anywhere on the drawing set. The values below are
stated assumptions, gathered here so they are easy to change.
"""
import json
import math
import pathlib
import sys

import bpy
from mathutils import Vector

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
CELL = 0.05                  # metres, matches CELL_MM in extract_plan.py

CLEAR_HEIGHT = 3.20          # assumed floor to underside of slab
SLAB = 0.40                  # assumed structural slab thickness
LINTEL_HEAD = 2.20           # assumed head height of doors and windows
SILL = 0.90                  # assumed window sill height

LEVELS = {
    # name: (finished floor level, is the floor slab drawn under it)
    "ground":   0.0,
    "basement": -(CLEAR_HEIGHT + SLAB),
}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, rgb, roughness=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def boxes_to_mesh(name, rects, z0, z1, gw, origin, mat):
    """One mesh from many axis-aligned boxes. rects are (x, y, w, h) grid cells."""
    verts, faces = [], []
    ox, oy = origin
    for (gx, gy, w, h) in rects:
        # image +x runs west and image +y runs north, so east is mirrored
        x1 = (gw - gx) * CELL - ox
        x0 = (gw - gx - w) * CELL - ox
        y0 = gy * CELL - oy
        y1 = (gy + h) * CELL - oy
        i = len(verts)
        verts += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        faces += [(i, i + 1, i + 2, i + 3), (i + 7, i + 6, i + 5, i + 4),
                  (i, i + 4, i + 5, i + 1), (i + 1, i + 5, i + 6, i + 2),
                  (i + 2, i + 6, i + 7, i + 3), (i + 3, i + 7, i + 4, i)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    return ob


def main():
    geom = json.loads((BUILD / "plan_geometry.json").read_text())
    reset()

    wall_mat = material("Wall", (0.86, 0.82, 0.75))
    slab_mat = material("Slab", (0.38, 0.36, 0.34), roughness=0.9)
    trim_mat = material("Opening head", (0.72, 0.69, 0.64))

    # centre the model on the plot
    g = geom["floors"]["ground"]
    gw, gh = g["grid_w"], g["grid_h"]
    xs = [r[0] for r in g["slab_rects"]] + [r[0] + r[2] for r in g["slab_rects"]]
    ys = [r[1] for r in g["slab_rects"]] + [r[1] + r[3] for r in g["slab_rects"]]
    origin = (((gw - min(xs)) + (gw - max(xs))) / 2 * CELL,
              (min(ys) + max(ys)) / 2 * CELL)

    made = []
    for floor, z in LEVELS.items():
        f = geom["floors"][floor]
        coll = bpy.data.collections.new(floor.capitalize())
        bpy.context.scene.collection.children.link(coll)
        parts = [
            ("slab", f["slab_rects"], z - SLAB, z, slab_mat),
            ("walls", f["wall_rects"], z, z + CLEAR_HEIGHT, wall_mat),
            ("lintels", f["lintel_rects"], z + LINTEL_HEAD, z + CLEAR_HEIGHT, trim_mat),
            ("sills", f["sill_rects"], z, z + SILL, trim_mat),
        ]
        for part, rects, z0, z1, mat in parts:
            if not rects:
                continue
            ob = boxes_to_mesh(f"{floor}_{part}", rects, z0, z1, f["grid_w"], origin, mat)
            coll.objects.link(ob)
            made.append(ob)
        print(f"{floor}: {len(f['wall_rects'])} wall boxes at z={z:+.2f}")

    # ground plane for context
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -SLAB - 0.01))
    ground = bpy.context.active_object
    ground.name = "Site"
    ground.data.materials.append(material("Site", (0.42, 0.37, 0.30), roughness=1.0))

    # sun and sky
    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = 3.4
    sun_data.angle = math.radians(1.5)
    # the sun is placed for legibility of the model, not for solar accuracy:
    # the sheet's compass contradicts its own boundary labels (see PDF-NOTES.md)
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(48), 0, math.radians(20))
    bpy.context.scene.collection.objects.link(sun)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    sky = world.node_tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False          # the Sun lamp already provides the disc
    sky.sun_elevation = math.radians(48)
    sky.sun_rotation = math.radians(20)
    world.node_tree.links.new(sky.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 0.25
    bpy.context.scene.world = world

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Base Contrast"
    scene.view_settings.exposure = -0.6

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 35
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    BUILD.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BUILD / "bader_villa.blend"))
    bpy.ops.export_scene.gltf(filepath=str(BUILD / "bader_villa.glb"),
                              export_format="GLB", export_apply=True)
    print("saved bader_villa.blend and bader_villa.glb")


if __name__ == "__main__":
    main()
