bl_info = {
	"name": "Lua Table Exporter (WinterMoon) v0.1",
	"author": "Asklepian",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "File > Export > Lua Table Format (.lua)",
	"description": "Export mesh data as Lua table with WinterMoon format",
	"category": "Import-Export",
}

import bpy
import bmesh
from mathutils import Vector

def write_lua_table(context, filepath, selected_only):
	scene = context.scene
	if selected_only:
		objects = context.selected_objects
	else:
		objects = scene.objects
	
	with open(filepath, 'w') as file:
		file.write("return {\n")
		
		first_object = True
		quad_count = 0
		skipped_faces = 0
		
		for obj in objects:
			if obj.type != 'MESH':
				continue
				
			mesh = obj.to_mesh()
			mesh.transform(obj.matrix_world)
			
			if not first_object:
				file.write(",\n")
			first_object = False
			
			file.write(f"\t-- Object: {obj.name}\n")
			
			first_face = True
			for face in mesh.polygons:
				if len(face.vertices) != 4:
					skipped_faces += 1
					continue
					
				if not first_face:
					file.write(",\n")
				first_face = False
				
				vertices = [mesh.vertices[i].co for i in face.vertices]
				
				tl = vertices[0]
				tr = vertices[1]
				br = vertices[2]
				bl = vertices[3]
				
				file.write("\t{\n")
				file.write(f"\t\ttl = {{{tl.x:.6f}, {tl.y:.6f}, {tl.z:.6f}}}, -- top left\n")
				file.write(f"\t\ttr = {{{tr.x:.6f}, {tr.y:.6f}, {tr.z:.6f}}}, -- top right\n")
				file.write(f"\t\tbr = {{{br.x:.6f}, {br.y:.6f}, {br.z:.6f}}}, -- bottom right\n")
				file.write(f"\t\tbl = {{{bl.x:.6f}, {bl.y:.6f}, {bl.z:.6f}}}, -- bottom left\n")
				file.write(f"\t\ttexture = 1\n")
				file.write("\t}")
				
				quad_count += 1
			
			obj.to_mesh_clear()
		
		file.write("\n}")
		
		if skipped_faces > 0:
			print(f"Exported {quad_count} quads, skipped {skipped_faces} non-quad faces")

	return {'FINISHED'}

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator


class ExportLuaTable(Operator, ExportHelper):
	"""Export selected objects to Lua table format (quads only)"""
	bl_idname = "export_mesh.lua_table"
	bl_label = "Export Lua Table"
	bl_options = {'PRESET'}

	filename_ext = ".lua"

	filter_glob: StringProperty(
		default="*.lua",
		options={'HIDDEN'},
		maxlen=255,
	)

	selected_only: BoolProperty(
		name="Selected Objects Only",
		description="Export only selected objects",
		default=True,
	)

	def execute(self, context):
		return write_lua_table(context, self.filepath, self.selected_only)

def menu_func_export(self, context):
	self.layout.operator(ExportLuaTable.bl_idname, text="Lua Table Format (.lua)")


def register():
	bpy.utils.register_class(ExportLuaTable)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(ExportLuaTable)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()