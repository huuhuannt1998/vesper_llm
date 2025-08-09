
bl_info = {"name":"VESPER Tools","blender":(4,0,0),"category":"Object"}
import bpy

class VESPER_OT_tag_device(bpy.types.Operator):
    bl_idname = "vesper.tag_device"
    bl_label = "Tag Selected as Device"
    device_type: bpy.props.EnumProperty(items=[
        ('light','Light',''),('switch','Switch',''),('sensor','Sensor','')])
    device_id: bpy.props.StringProperty()

    def execute(self, ctx):
        for obj in ctx.selected_objects:
            obj["vesper_device"] = {
                "id": self.device_id,
                "type": self.device_type,
                "room": ctx.scene.get("vesper_room","Unknown")
            }
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(VESPER_OT_tag_device.bl_idname, text="Tag as VESPER Device")

def register():
    bpy.utils.register_class(VESPER_OT_tag_device)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(VESPER_OT_tag_device)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
