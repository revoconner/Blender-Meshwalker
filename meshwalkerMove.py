bl_info = {
    'name': 'Mesh PickWalker',
    'description': 'Transfers world/object position of vertices from target to source, even with unequal number of vertices',
    'author': 'Rév',
    'version': (1, 0),
    'blender': (3, 0, 0),
    'location': '3D View > N Panel > Tool',
    'category': 'Mesh'
}


import bpy
import bmesh
from bpy.types import Panel, Operator
from bpy.props import StringProperty

class MESH_OT_store_mesh_a_face(Operator):
    bl_idname = "mesh.store_mesh_a_face"
    bl_label = "Store Mesh A Face"
    bl_description = "Select a face of the source mesh"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_faces = [f for f in bm.faces if f.select]
            if len(selected_faces) == 1:
                context.scene.mesh_a_face = str(selected_faces[0].index)
                context.scene.mesh_a_name = obj.name  
            else:
                self.report({'ERROR'}, "Please select exactly one face")
        return {'FINISHED'}

class MESH_OT_store_mesh_a_vtx1(Operator):
    bl_idname = "mesh.store_mesh_a_vtx1"
    bl_label = "Store Mesh A Vertex 1"
    bl_description = "Pick a vertex that is part of the same face"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v for v in bm.verts if v.select]
            if len(selected_verts) == 1:
                context.scene.mesh_a_vtx1 = str(selected_verts[0].index)
                context.scene.mesh_a_name = obj.name  
            else:
                self.report({'ERROR'}, "Please select exactly one vertex")
        return {'FINISHED'}

class MESH_OT_store_mesh_a_vtx2(Operator):
    bl_idname = "mesh.store_mesh_a_vtx2"
    bl_label = "Store Mesh A Vertex 2"
    bl_description = "Pick a neighboring vertex that is part of the same face"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v for v in bm.verts if v.select]
            if len(selected_verts) == 1:
                context.scene.mesh_a_vtx2 = str(selected_verts[0].index)
                context.scene.mesh_a_name = obj.name  
            else:
                self.report({'ERROR'}, "Please select exactly one vertex")
        return {'FINISHED'}

class MESH_OT_store_mesh_b_face(Operator):
    bl_idname = "mesh.store_mesh_b_face"
    bl_label = "Store Mesh B Face"
    bl_description = "Select the equivalent face of the target mesh"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_faces = [f for f in bm.faces if f.select]
            if len(selected_faces) == 1:
                context.scene.mesh_b_face = str(selected_faces[0].index)
                context.scene.mesh_b_name = obj.name  
            else:
                self.report({'ERROR'}, "Please select exactly one face")
        return {'FINISHED'}

class MESH_OT_store_mesh_b_vtx1(Operator):
    bl_idname = "mesh.store_mesh_b_vtx1"
    bl_label = "Store Mesh B Vertex 1"
    bl_description = "Select the equivalent vertex 1 of the target mesh"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v for v in bm.verts if v.select]
            if len(selected_verts) == 1:
                context.scene.mesh_b_vtx1 = str(selected_verts[0].index)
                context.scene.mesh_b_name = obj.name  
            else:
                self.report({'ERROR'}, "Please select exactly one vertex")
        return {'FINISHED'}

class MESH_OT_store_mesh_b_vtx2(Operator):
    bl_idname = "mesh.store_mesh_b_vtx2"
    bl_label = "Store Mesh B Vertex 2"
    bl_description = "Select the equivalent vertex 2 of the target mesh"
    
    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v for v in bm.verts if v.select]
            if len(selected_verts) == 1:
                context.scene.mesh_b_vtx2 = str(selected_verts[0].index)
                context.scene.mesh_b_name = obj.name  
            else:
                self.report({'ERROR'}, "Please select exactly one vertex")
        return {'FINISHED'}

class MESH_OT_compute_mapping(Operator):
    bl_idname = "mesh.compute_mapping"
    bl_label = "Compute Vertex Mapping"
    bl_description = "Move all target vertices to source vertices location in selected space"
    
    def move_vertices_world_space(self, obj_a, obj_b, bm_a, bm_b, reverse_map):
        for v_b in bm_b.verts:
            if v_b.index in reverse_map:
                v_a = bm_a.verts[reverse_map[v_b.index]]
                # Convert vertex position from mesh A's local space to world space
                world_pos_a = obj_a.matrix_world @ v_a.co
                # Convert world position to mesh B's local space
                local_pos_b = obj_b.matrix_world.inverted() @ world_pos_a
                # Update mesh B vertex position
                v_b.co = local_pos_b

    def move_vertices_object_space(self, obj_a, obj_b, bm_a, bm_b, reverse_map):
        for v_b in bm_b.verts:
            if v_b.index in reverse_map:
                v_a = bm_a.verts[reverse_map[v_b.index]]
                # Simply copy local coordinates
                v_b.co = v_a.co

    
    def get_next_vertex(self, face, vertex_pair):
        """Gets next vertex in face from current vertex pair"""
        prev_vert, curr_vert = vertex_pair
        face_verts = [v for v in face.verts]
        
        
        connected_edges = []
        for edge in face.edges:
            if curr_vert in edge.verts:
                connected_edges.append(edge)
                
        
        for edge in connected_edges:
            other_vert = edge.other_vert(curr_vert)
            # If vertex is in face and not the previous vertex
            if other_vert in face_verts and other_vert != prev_vert:
                return edge, other_vert
        return None

    def walk_face_double(self, bm_a, face_a, vertex_pair_a, bm_b, face_b, vertex_pair_b):
        """Walk around both faces simultaneously"""
        seen_verts_a = set()
        seen_verts_b = set()
        queue_items = []
        
        while True:
            # Check for facewalk complete
            if vertex_pair_a[1].index in seen_verts_a:
                if vertex_pair_b[1].index not in seen_verts_b:
                    self.report({'ERROR'}, "Face mismatch found!")
                break
            if vertex_pair_b[1].index in seen_verts_b and vertex_pair_a[1].index not in seen_verts_a:
                self.report({'ERROR'}, "Face mismatch found!")
                break
                
            # Get next vertices
            next_a = self.get_next_vertex(face_a, vertex_pair_a)
            next_b = self.get_next_vertex(face_b, vertex_pair_b)
            
            if next_a and next_b:
                edge_a, next_vert_a = next_a
                edge_b, next_vert_b = next_b
                
                # Update vertices for next iteration
                seen_verts_a.add(vertex_pair_a[1].index)
                seen_verts_b.add(vertex_pair_b[1].index)
                
                queue_items.append([
                    bm_a, face_a, edge_a, [vertex_pair_a[1], next_vert_a],
                    bm_b, face_b, edge_b, [vertex_pair_b[1], next_vert_b]
                ])
                
                # Update vertex pairs for next iteration
                vertex_pair_a = [vertex_pair_a[1], next_vert_a]
                vertex_pair_b = [vertex_pair_b[1], next_vert_b]
            else:
                break
                
        return queue_items

    def get_opposite_face(self, edge, current_face):
        """Get face on other side of edge"""
        return next((f for f in edge.link_faces if f != current_face), None)

    def execute(self, context):
        
        obj_a = bpy.data.objects.get(context.scene.mesh_a_name)
        obj_b = bpy.data.objects.get(context.scene.mesh_b_name)
        
        if not obj_a or not obj_b:
            self.report({'ERROR'}, "Please store both meshes first")
            return {'CANCELLED'}
        
        
        bm_a = bmesh.new()
        bm_b = bmesh.new()
        bm_a.from_mesh(obj_a.data)
        bm_b.from_mesh(obj_b.data)
        
        
        bm_a.faces.ensure_lookup_table()
        bm_a.verts.ensure_lookup_table()
        bm_b.faces.ensure_lookup_table()
        bm_b.verts.ensure_lookup_table()
        
        
        face_a = bm_a.faces[int(context.scene.mesh_a_face)]
        face_b = bm_b.faces[int(context.scene.mesh_b_face)]
        vert1_a = bm_a.verts[int(context.scene.mesh_a_vtx1)]
        vert2_a = bm_a.verts[int(context.scene.mesh_a_vtx2)]
        vert1_b = bm_b.verts[int(context.scene.mesh_b_vtx1)]
        vert2_b = bm_b.verts[int(context.scene.mesh_b_vtx2)]

        
        vertex_map = {}
        seen_edges = set()
        
        
        vertex_map[vert1_a.index] = vert1_b.index
        vertex_map[vert2_a.index] = vert2_b.index
        
        
        queues = self.walk_face_double(bm_a, face_a, [vert1_a, vert2_a],
                                     bm_b, face_b, [vert1_b, vert2_b])
        
        # Main walking loop
        while queues:
            (bm_a, face_a, edge_a, verts_a,
             bm_b, face_b, edge_b, verts_b) = queues.pop(0)
            
            if edge_a.index not in seen_edges:
                seen_edges.add(edge_a.index)
                
                
                vertex_map[verts_a[0].index] = verts_b[0].index
                vertex_map[verts_a[1].index] = verts_b[1].index
                
                
                opp_face_a = self.get_opposite_face(edge_a, face_a)
                opp_face_b = self.get_opposite_face(edge_b, face_b)
                
                
                if opp_face_a and opp_face_b:
                    next_queues = self.walk_face_double(
                        bm_a, opp_face_a, verts_a,
                        bm_b, opp_face_b, verts_b
                    )
                    queues.extend(next_queues)
        
        # Create reverse mapping from mesh B to mesh A vertices (previous iter printed ID so this is important)
        reverse_map = {v_b: v_a for v_a, v_b in vertex_map.items()}        
        # Move mesh B vertices to match mesh A world positions
        for v_b in bm_b.verts:
            if v_b.index in reverse_map:                
                v_a = bm_a.verts[reverse_map[v_b.index]]                
                # Convert vertex position from mesh A's local space to world space
                world_pos_a = obj_a.matrix_world @ v_a.co                
                # Convert world position to mesh B's local space
                local_pos_b = obj_b.matrix_world.inverted() @ world_pos_a                
                # Update mesh B vertex position
                v_b.co = local_pos_b
        
        if context.scene.mesh_walker_space == 'WORLD':
            self.move_vertices_world_space(obj_a, obj_b, bm_a, bm_b, reverse_map)
        else:
            self.move_vertices_object_space(obj_a, obj_b, bm_a, bm_b, reverse_map)

        # Update mesh B
        bm_b.to_mesh(obj_b.data)
        obj_b.data.update()
        
        bm_a.free()
        bm_b.free()
        
        self.report({'INFO'}, f"Vertex positions updated in {context.scene.mesh_walker_space.lower()} space")
        return {'FINISHED'}


class MESH_OT_clear_values(Operator):
    bl_idname = "mesh.clear_values"
    bl_label = "Clear Values"
    bl_description = "Clear all stored variables"
    
    def execute(self, context):
        context.scene.mesh_a_face = ""
        context.scene.mesh_a_vtx1 = ""
        context.scene.mesh_a_vtx2 = ""
        context.scene.mesh_b_face = ""
        context.scene.mesh_b_vtx1 = ""
        context.scene.mesh_b_vtx2 = ""
        context.scene.mesh_a_name = ""
        context.scene.mesh_b_name = ""
        return {'FINISHED'}

class VIEW3D_PT_mesh_walker(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MeshWalker'
    bl_label = "Mesh Walker"

    
    def draw(self, context):
        layout = self.layout

        layout.label(text="Created by Rév O'Conner")
        box = layout.box()
        col = box.column(align=True) 
        col.label(text="1. Select equivalent faces")
        col.label(text="2. Select two neighboring vertices")
        col.label(text="   of the same face")

        box = layout.box()
        box.label(text="Source: Mesh that's copied from")
        col = box.column(align=True)
        row = col.row()
        row.operator("mesh.store_mesh_a_face", text="Face")
        row.label(text=context.scene.mesh_a_face)
        row = col.row()
        row.operator("mesh.store_mesh_a_vtx1", text="Vertex 1")
        row.label(text=context.scene.mesh_a_vtx1)
        row = col.row()
        row.operator("mesh.store_mesh_a_vtx2", text="Vertex 2")
        row.label(text=context.scene.mesh_a_vtx2)
        row = col.row()
        row.label(text="Mesh: " + (context.scene.mesh_a_name if context.scene.mesh_a_name else "None"))        

        box = layout.box()
        box.label(text="Target: Mesh that changes")
        col = box.column(align=True)
        row = col.row()
        row.operator("mesh.store_mesh_b_face", text="Face")
        row.label(text=context.scene.mesh_b_face)
        row = col.row()
        row.operator("mesh.store_mesh_b_vtx1", text="Vertex 1")
        row.label(text=context.scene.mesh_b_vtx1)
        row = col.row()
        row.operator("mesh.store_mesh_b_vtx2", text="Vertex 2")
        row.label(text=context.scene.mesh_b_vtx2)
        row = col.row()
        row.label(text="Mesh: " + (context.scene.mesh_b_name if context.scene.mesh_b_name else "None"))
        row = layout.row()
        row.prop(context.scene, "mesh_walker_space", expand=True)        

        layout.operator("mesh.compute_mapping", text="Move Vertices")
        layout.operator("mesh.clear_values", text="Clear All")

def register():
    bpy.types.Scene.mesh_a_face = StringProperty(default="")
    bpy.types.Scene.mesh_a_vtx1 = StringProperty(default="")
    bpy.types.Scene.mesh_a_vtx2 = StringProperty(default="")
    bpy.types.Scene.mesh_b_face = StringProperty(default="")
    bpy.types.Scene.mesh_b_vtx1 = StringProperty(default="")
    bpy.types.Scene.mesh_b_vtx2 = StringProperty(default="")    
    bpy.types.Scene.mesh_a_name = StringProperty(default="")
    bpy.types.Scene.mesh_b_name = StringProperty(default="")
    bpy.utils.register_class(MESH_OT_clear_values)    
    bpy.utils.register_class(MESH_OT_store_mesh_a_face)
    bpy.utils.register_class(MESH_OT_store_mesh_a_vtx1)
    bpy.utils.register_class(MESH_OT_store_mesh_a_vtx2)
    bpy.utils.register_class(MESH_OT_store_mesh_b_face)
    bpy.utils.register_class(MESH_OT_store_mesh_b_vtx1)
    bpy.utils.register_class(MESH_OT_store_mesh_b_vtx2)
    bpy.utils.register_class(MESH_OT_compute_mapping)
    bpy.utils.register_class(VIEW3D_PT_mesh_walker)
    bpy.types.Scene.mesh_walker_space = bpy.props.EnumProperty(
        items=[
            ('WORLD', "World Space", "Move vertices in world space"),
            ('OBJECT', "Object Space", "Move vertices in object space")
        ],
        default='WORLD'
    )

def unregister():
    del bpy.types.Scene.mesh_a_face
    del bpy.types.Scene.mesh_a_vtx1
    del bpy.types.Scene.mesh_a_vtx2
    del bpy.types.Scene.mesh_b_face
    del bpy.types.Scene.mesh_b_vtx1
    del bpy.types.Scene.mesh_b_vtx2
    del bpy.types.Scene.mesh_a_name
    del bpy.types.Scene.mesh_b_name
    del bpy.types.Scene.mesh_walker_space
    bpy.utils.unregister_class(MESH_OT_clear_values)
    bpy.utils.unregister_class(MESH_OT_store_mesh_a_face)
    bpy.utils.unregister_class(MESH_OT_store_mesh_a_vtx1)
    bpy.utils.unregister_class(MESH_OT_store_mesh_a_vtx2)
    bpy.utils.unregister_class(MESH_OT_store_mesh_b_face)
    bpy.utils.unregister_class(MESH_OT_store_mesh_b_vtx1)
    bpy.utils.unregister_class(MESH_OT_store_mesh_b_vtx2)
    bpy.utils.unregister_class(MESH_OT_compute_mapping)
    bpy.utils.unregister_class(VIEW3D_PT_mesh_walker)

if __name__ == "__main__":
    register()