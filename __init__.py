# Megagrid created by Midge Systemic (cimetsys)
# Initial script and idea downloaded form https://github.com/mantissa-/RandoMesh
# Licensed under GPLv3

bl_info = {
    "name": "MegaGrid",
    "author": "Midge \"Mantissa\" Sinnaeve and Systemic",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > Megagrid Tab",
    "description": "Create megagrid cubes",
    "wiki_url": "https://github.com/systemik/MegaGrid",
    "category": "3D View",
    "warning": "You might have fun"
}


import bpy, bmesh, random
from bpy.props import (IntProperty, FloatProperty, BoolProperty, PointerProperty)
from bpy.types import (Panel, Operator, PropertyGroup)
from random import randint
from math import isclose

#------------#
# PROPERTIES #
#------------#

class MegaGridProps(PropertyGroup):
    
    
    int_divisions : IntProperty(
        name = "Number of divisions",
        description = "Set the number of division on the initial plane",
        default = 1,
        min = 1,
        soft_max = 5
        )
        
    int_levels : IntProperty(
        name = "Number of levels",
        description = "Set the amount of level for the megagrid",
        default = 1,
        min = 1,
        soft_max = 20
        )

    bool_create_dupliface : BoolProperty(
        name = "Cube and dupliface",
        description = "Create cube, parent it and enable dupliface",
        default = True
        )
        
    bool_create_modifiers : BoolProperty(
        name = "Create modifiers",
        description = "Create modifiers with mask texture",
        default = True
        )
        

#----#
# UI #
#----#

class MegaGridPanel(bpy.types.Panel):
    # Creates a Panel in the sidebar
    bl_label = "MegaGrid"
    bl_idname = "OBJECT_PT_MegaGrid"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "MegaGrid"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column(align=False)
        row = layout.row(align=False)
        
        
        col.prop(scene.rg_props, "int_divisions")
        col.separator()
        col.prop(scene.rg_props, "int_levels")
        col.separator()
        
        col.prop(scene.rg_props, "bool_create_dupliface")
        col.prop(scene.rg_props, "bool_create_modifiers")
        col.separator()
        
        sub = col.row()
        sub.scale_y = 2.0
        sub.operator("wm.megagrid")
        
        sub = col.row()
        sub.scale_y = 2.0
        sub.operator("wm.megagrid_deleteall")


#----------#
# OPERATOR #
#----------#

class MegaGridDelete(bpy.types.Operator):
    # RandoGrid Operator
    bl_idname = "wm.megagrid_deleteall"
    bl_label = "DELETE ALL"
    
    def execute(self, context):
        
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        return {'FINISHED'}
        


class MegaGrid(bpy.types.Operator):
    # RandoGrid Operator
    bl_idname = "wm.megagrid"
    bl_label = "CREATE RANDOM MEGAGRID"
    
    def execute(self, context):

        rgp = bpy.context.scene.rg_props
        
        divisions = rgp.int_divisions
        levels = rgp.int_levels

        for j in range(levels):
            
#############################
## Create initial plane
#############################

            bpy.ops.mesh.primitive_plane_add(size=10, enter_editmode=False, align='WORLD', location=(0, 0, 0))
            bpy.ops.transform.translate(value=(0, 0, j), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.context.active_object.name = 'LEVEL' + str(j)

#############################
## Subdive initial plane
#############################

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.subdivide(number_cuts=9)
            bpy.ops.object.editmode_toggle()

#############################
## Edge Split initial plane
#############################

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.edge_split()

#############################
## Loop
#############################

            for i in range(divisions):
                
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_random(percent=20, seed=randint(0, 9999), action='SELECT')
                bpy.ops.mesh.select_random(percent=20, seed=randint(0, 9999), action='SELECT')
                bpy.ops.mesh.subdivide(smoothness=0)
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.edge_split()
                
                
#############################
##CREATE Various LEVELS
#############################

            context = bpy.context

            ob = context.edit_object
            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            bpy.ops.mesh.select_all(action='DESELECT')

            for g in range(divisions+1):
                    a = round((4*100000)/(4**(g+1)), 0)
                    for f in bm.faces:
                        b = round((f.calc_area()*100000), 0)
                        if isclose(a,b,rel_tol=0.01):
                            f.select = isclose(f.calc_area()*100000, a,rel_tol=0.01)
                    print("faces selected:",g)
                    for h in range((2**g)-1):
                        print("h: ",((2**g)-1))
                        print("duplicate:",h)
                        print("value height:",1/2**(g))
                        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 1/2**(g)), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
                    bmesh.update_edit_mesh(me)
                    bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()

#############################
## Join Levels
#############################

        bpy.ops.object.select_all(action='DESELECT')
        for ob in bpy.context.visible_objects:
              if ob.type == 'MESH' and ('LEVEL' in ob.name):
                  ob.select_set(True)
                  bpy.ops.object.join()

#############################
## DUPLIFACE Option
#############################

        if rgp.bool_create_dupliface:

#############################
## Add a cube
#############################

            bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
            bpy.context.active_object.name = 'Cube'
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.translate(value=(-0, -0, 0.5), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.object.editmode_toggle()
            
#############################
## Cube modifiers
#############################   
            
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].thickness = 0.25
            bpy.context.object.modifiers["Solidify"].use_even_offset = True
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.context.object.modifiers["Bevel"].segments = 6
            bpy.context.object.modifiers["Bevel"].width = 0.05
            bpy.context.object.modifiers["Bevel"].show_viewport = False


#############################
## Parent object
#############################

            if ob.type == 'MESH' and ('LEVEL' in ob.name):
                      ob.select_set(True)
                      level = bpy.data.objects[ob.name]
                      bpy.context.view_layer.objects.active = level
            if ob.type == 'MESH' and ('Cube' in ob.name):
                      ob.select_set(True)

            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

#############################
## DupliFace
#############################

            bpy.context.object.instance_type = 'FACES'
            bpy.context.object.use_instance_faces_scale = True
            bpy.context.object.show_instancer_for_viewport = False
            bpy.context.object.show_instancer_for_render = False

#############################
## Create modifiers?
#############################

        if rgp.bool_create_modifiers:

#############################
## Empty vertex group
#############################

            bpy.ops.object.vertex_group_add()
            bpy.context.object.vertex_groups[0].name = "Mask"
            
#############################
## Modifier
#############################

            bpy.ops.texture.new()
            bpy.data.textures[0].name = "MaskTex"
            bpy.data.textures[0].type = 'DISTORTED_NOISE'
            bpy.data.textures[0].noise_basis = 'CELL_NOISE'
            bpy.data.textures[0].noise_distortion = 'CELL_NOISE'
            bpy.data.textures[0].noise_scale = 1.25

            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_EDIT')
            bpy.context.object.modifiers["VertexWeightEdit"].use_add = True
            bpy.context.object.modifiers["VertexWeightEdit"].use_remove = True
            bpy.context.object.modifiers["VertexWeightEdit"].falloff_type = 'CURVE'
            bpy.context.object.modifiers["VertexWeightEdit"].vertex_group = "Mask"
            bpy.context.object.modifiers["VertexWeightEdit"].mask_texture = bpy.data.textures[0]
            bpy.context.object.modifiers["VertexWeightEdit"].invert_falloff = True
            bpy.ops.object.modifier_add(type='MASK')
            bpy.context.object.modifiers["Mask"].vertex_group = "Mask"
            
        return {'FINISHED'}

#----------#
# REGISTER #
#----------#

def register():
    bpy.utils.register_class(MegaGridPanel)
    bpy.utils.register_class(MegaGrid)
    bpy.utils.register_class(MegaGridDelete)
    bpy.utils.register_class(MegaGridProps)
    bpy.types.Scene.rg_props = PointerProperty(type=MegaGridProps)

def unregister():
    bpy.utils.unregister_class(MegaGridPanel)
    bpy.utils.unregister_class(MegaGrid)
    bpy.utils.register_class(MegaGridDelete)
    bpy.utils.unregister_class(MegaGridProps)
    del bpy.types.Scene.rg_props

if __name__ == "__main__":
    register()
