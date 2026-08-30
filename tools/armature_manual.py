# MIT License

import bpy
import operator
import math
import webbrowser
import numpy as np
import bmesh
from mathutils.geometry import intersect_point_line

from . import common as Common
from . import eyetracking as Eyetracking
from .register import register_wrap
from .translations import t

# Bone names from https://github.com/teamneoneko/immersive_scaler
bone_names = {
    "right_shoulder": ["rightshoulder", "shoulderr", "rshoulder"],
    "right_arm": ["rightarm", "armr", "rarm", "upperarmr", "rightupperarm", "uparmr", "ruparm"],
    "right_elbow": ["rightelbow", "elbowr", "relbow", "lowerarmr", "rightlowerarm", "lowerarmr", "lowarmr", "rlowarm"],
    "right_wrist": ["rightwrist", "wristr", "rwrist", "handr", "righthand", "rhand"],

    #hand l fingers
    "pinkie_1_r": ["littlefinger1r"],
    "pinkie_2_r": ["littlefinger2r"],
    "pinkie_3_r": ["littlefinger3r"],

    "ring_1_r": ["ringfinger1r"],
    "ring_2_r": ["ringfinger2r"],
    "ring_3_r": ["ringfinger3r"],

    "middle_1_r": ["middlefinger1r"],
    "middle_2_r": ["middlefinger2r"],
    "middle_3_r": ["middlefinger3r"],

    "index_1_r": ["indexfinger1r"],
    "index_2_r": ["indexfinger2r"],
    "index_3_r": ["indexfinger3r"],

    "thumb_1_r": ['thumb0r'],
    "thumb_2_r": ['thumb1r'],
    "thumb_3_r": ['thumb2r'],

    "right_leg": ["rightleg", "legr", "rleg", "upperlegr", "thighr", "rightupperleg", "uplegr", "rupleg"],
    "right_knee": ["rightknee", "kneer", "rknee", "lowerlegr", "calfr", "rightlowerleg", "lowlegr", "rlowleg"],
    "right_ankle": ["rightankle", "ankler", "rankle", "rightfoot", "footr", "rightfoot", "rightfeet", "feetright", "rfeet", "feetr"],
    "right_toe": ["righttoe", "toeright", "toer", "rtoe", "toesr", "rtoes"],

    "left_shoulder": ["leftshoulder", "shoulderl", "rshoulder"],
    "left_arm": ["leftarm", "arml", "rarm", "upperarml", "leftupperarm", "uparml", "luparm"],
    "left_elbow": ["leftelbow", "elbowl", "relbow", "lowerarml", "leftlowerarm", "lowerarml", "lowarml", "llowarm"],
    "left_wrist": ["leftwrist", "wristl", "rwrist", "handl", "lefthand", "lhand"],

    #hand l fingers
    "pinkie_1_l": ["littlefinger1l"],
    "pinkie_2_l": ["littlefinger2l"],
    "pinkie_3_l": ["littlefinger3l"],

    "ring_1_l": ["ringfinger1l"],
    "ring_2_l": ["ringfinger2l"],
    "ring_3_l": ["ringfinger3l"],

    "middle_1_l": ["middlefinger1l"],
    "middle_2_l": ["middlefinger2l"],
    "middle_3_l": ["middlefinger3l"],

    "index_1_l": ["indexfinger1l"],
    "index_2_l": ["indexfinger2l"],
    "index_3_l": ["indexfinger3l"],

    "thumb_1_l": ['thumb0l'],
    "thumb_2_l": ['thumb1l'],
    "thumb_3_l": ['thumb2l'],

    "left_leg": ["leftleg", "legl", "rleg", "upperlegl", "thighl","leftupperleg", "uplegl", "lupleg"],
    "left_knee": ["leftknee", "kneel", "rknee", "lowerlegl", "calfl", "leftlowerleg", 'lowlegl', 'llowleg'],
    "left_ankle": ["leftankle", "anklel", "rankle", "leftfoot", "footl", "leftfoot", "leftfeet", "feetleft", "lfeet", "feetl"],
    "left_toe": ["lefttoe", "toeleft", "toel", "ltoe", "toesl", "ltoes"],

    'hips': ["pelvis", "hips"],
    'spine': ["torso", "spine"],
    'chest': ["chest"],
    'upper_chest': ["upperchest"],
    'neck': ["neck"],
    'head': ["head"],
    'left_eye': ["eyeleft", "lefteye", "eyel", "leye"],
    'right_eye': ["eyeright", "righteye", "eyer", "reye"],
}

def simplify_bonename(n):
    return n.lower().translate(dict.fromkeys(map(ord, u" _.")))

@register_wrap
class DigitigradeTutorialButton(bpy.types.Operator):
    bl_idname = 'cats_manual.digitigrade_tutorial'
    bl_label = "How to use"
    bl_description = "This will open a basic tutorial on how to setup and use aim constraints for Digitigrade avatars. Desktop-only!"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open("https://www.furaffinity.net/view/44035707/")
        return {'FINISHED'}
        
@register_wrap
class TwistTutorialButton(bpy.types.Operator):
    bl_idname = 'cats_manual.twist_tutorial'
    bl_label = t('cats_twist.tutorial_button.label')
    bl_description = "This will open a basic tutorial on how to setup and use these constraints. You can skip to the Unity section."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open("https://www.youtube.com/watch?v=eOwd5KNypfA")
        return {'FINISHED'}

@register_wrap
class StartPoseMode(bpy.types.Operator):
    bl_idname = 'cats_manual.start_pose_mode'
    bl_label = t('StartPoseMode.label')
    bl_description = t('StartPoseMode.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        start_pose_mode(reset_pose=True)
        return {'FINISHED'}


@register_wrap
class StartPoseModeNoReset(bpy.types.Operator):
    bl_idname = 'cats_manual.start_pose_mode_no_reset'
    bl_label = t('StartPoseMode.label')
    bl_description = t('StartPoseModeNoReset.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        start_pose_mode(reset_pose=False)
        return {'FINISHED'}


def start_pose_mode(reset_pose=True):
    saved_data = Common.SavedData()

    current = ""
    if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT' and bpy.context.active_object.type == 'ARMATURE' and len(
            bpy.context.selected_editable_bones) > 0:
        current = bpy.context.selected_editable_bones[0].name
        pass

    armature = Common.set_default_stage()
    if armature is None:
        print('Cats start_pose_mode: no armature found')
        return
    Common.remove_rigidbodies_global()
    Common.switch('POSE')
    armature.data.pose_position = 'POSE'

    if reset_pose:
        for mesh in Common.get_meshes_objects():
            if Common.has_shapekeys(mesh):
                for shape_key in mesh.data.shape_keys.key_blocks:
                    shape_key.value = 0

    for pb in armature.pose.bones:
        pb.select = True

    if reset_pose:
        if armature.mode == 'POSE':
            for op in (bpy.ops.pose.rot_clear, bpy.ops.pose.scale_clear,
                       bpy.ops.pose.transforms_clear):
                try:
                    op()
                except RuntimeError as e:
                    print('Cats start_pose_mode: %s skipped: %s' % (op.idname(), e))
        else:
            for pb in armature.pose.bones:
                pb.matrix_basis.identity()

    bone = armature.data.bones.get(current)
    if bone is not None:
        for pb in armature.pose.bones:
            if bone.name != pb.name:
                pb.select = False
    else:
        for index, pb in enumerate(armature.pose.bones):
            if index != 0:
                pb.select = False
        try:
            bpy.ops.wm.tool_set_by_id(name="builtin.rotate")
        except RuntimeError as e:
            print('Cats start_pose_mode: tool_set_by_id skipped:', e)

    saved_data.load(hide_only=True)
    Common.hide(armature, False)


@register_wrap
class StopPoseMode(bpy.types.Operator):
    bl_idname = 'cats_manual.stop_pose_mode'
    bl_label = t('StopPoseMode.label')
    bl_description = t('StopPoseMode.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        stop_pose_mode(reset_pose=True)
        return {'FINISHED'}


@register_wrap
class StopPoseModeNoReset(bpy.types.Operator):
    bl_idname = 'cats_manual.stop_pose_mode_no_reset'
    bl_label = t('StopPoseMode.label')
    bl_description = t('StopPoseModeNoReset.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        stop_pose_mode(reset_pose=False)
        return {'FINISHED'}


def stop_pose_mode(reset_pose=True):
    saved_data = Common.SavedData()
    armature = Common.get_armature()
    if armature is None:
        return
    Common.set_active(armature)

    # Make all objects visible. Needs an Object-mode 3D View context, which is not guaranteed when
    # this is called from another operator, so never let it abort the rest of the cleanup.
    try:
        bpy.ops.object.hide_view_clear()
    except RuntimeError as e:
        print('Cats stop_pose_mode: hide_view_clear skipped:', e)

    for pb in armature.pose.bones:
        pb.hide = False
        pb.select = True

    # The pose.* operators only poll in Pose mode. This function used to assume it was always
    # entered from Pose mode and blew up with "context is incorrect" otherwise - which aborted the
    # whole caller (including Apply as Rest Pose) after it had already changed the model.
    if reset_pose:
        if armature.mode != 'POSE':
            try:
                Common.switch('POSE')
            except Exception as e:
                print('Cats stop_pose_mode: could not enter pose mode:', e)
        if armature.mode == 'POSE':
            for op in (bpy.ops.pose.rot_clear, bpy.ops.pose.scale_clear,
                       bpy.ops.pose.transforms_clear):
                try:
                    op()
                except RuntimeError as e:
                    print('Cats stop_pose_mode: %s skipped: %s' % (op.idname(), e))
        else:
            # Fall back to clearing the pose through the data API, which needs no context at all.
            for pb in armature.pose.bones:
                pb.matrix_basis.identity()

    for pb in armature.pose.bones:
        pb.select = False

    armature = Common.set_default_stage()
    Common.remove_rigidbodies_global()
    # armature.data.pose_position = 'REST'

    if reset_pose:
        for mesh in Common.get_meshes_objects():
            if Common.has_shapekeys(mesh):
                for shape_key in mesh.data.shape_keys.key_blocks:
                    shape_key.value = 0

    try:
        bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
    except RuntimeError as e:
        print('Cats stop_pose_mode: tool_set_by_id skipped:', e)

    Eyetracking.eye_left = None

    saved_data.load(hide_only=True)


@register_wrap
class PoseToShape(bpy.types.Operator):
    bl_idname = 'cats_manual.pose_to_shape'
    bl_label = t('PoseToShape.label')
    bl_description = t('PoseToShape.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = Common.get_armature()
        return armature and armature.mode == 'POSE'

    def execute(self, context):
        # pose_to_shapekey('Pose')
        bpy.ops.cats_manual.pose_name_popup('INVOKE_DEFAULT')

        return {'FINISHED'}


def pose_to_shapekey(name):
    saved_data = Common.SavedData()

    for mesh in Common.get_meshes_objects():
        Common.unselect_all()
        Common.set_active(mesh)

        Common.switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.remove_doubles(threshold=0)
        Common.switch('OBJECT')

        # Apply armature mod
        mod = mesh.modifiers.new(name, 'ARMATURE')
        mod.object = Common.get_armature()
        Common.apply_modifier(mod, as_shapekey=True)

    armature = Common.set_default_stage()
    Common.remove_rigidbodies_global()
    Common.switch('POSE')
    armature.data.pose_position = 'POSE'

    saved_data.load(ignore=armature.name)
    return armature


@register_wrap
class PoseNamePopup(bpy.types.Operator):
    bl_idname = "cats_manual.pose_name_popup"
    bl_label = t('PoseNamePopup.label')
    bl_description = t('PoseNamePopup.desc')
    bl_options = {'INTERNAL'}

    bpy.types.Scene.pose_to_shapekey_name = bpy.props.StringProperty(name="Pose Name")

    def execute(self, context):
        name = context.scene.pose_to_shapekey_name
        if not name:
            name = 'Pose'
        pose_to_shapekey(name)
        self.report({'INFO'}, t('PoseNamePopup.success'))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.scene.pose_to_shapekey_name = 'Pose'
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop(context.scene, 'pose_to_shapekey_name')


@register_wrap
class PoseToRest(bpy.types.Operator):
    bl_idname = 'cats_manual.pose_to_rest'
    bl_label = t('PoseToRest.label')
    bl_description = t('PoseToRest.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        # The Cats armature being in pose mode is the normal case, but the user may well be posing a
        # different armature than the one picked in the Cats dropdown (very common on models where the
        # clothing rides a second armature). Accept the active object too, and accept any armature in
        # the view layer that currently holds a pose, so the button is never silently dead.
        armature = Common.get_armature()
        if armature and armature.mode == 'POSE':
            return True
        active = context.view_layer.objects.active if context.view_layer else None
        if active and active.type == 'ARMATURE' and active.mode == 'POSE':
            return True
        return bool(PoseToRest.get_posed_armatures(context))

    # -- helpers -------------------------------------------------------------------------------

    @staticmethod
    def is_bone_posed(pose_bone, tolerance=1e-6):
        """True if this pose bone carries a transform relative to its rest position."""
        m = pose_bone.matrix_basis
        for i in range(4):
            for j in range(4):
                if abs(m[i][j] - (1.0 if i == j else 0.0)) > tolerance:
                    return True
        return False

    @staticmethod
    def count_posed_bones(armature_obj):
        return sum(1 for pb in armature_obj.pose.bones if PoseToRest.is_bone_posed(pb))

    @staticmethod
    def get_posed_armatures(context):
        """Every armature in the current view layer that actually holds a pose."""
        view_layer_objs = context.view_layer.objects if context.view_layer else []
        out = []
        for obj in view_layer_objs:
            if obj.type == 'ARMATURE' and obj.pose and PoseToRest.count_posed_bones(obj):
                out.append(obj)
        return out

    @staticmethod
    def get_bound_meshes(armature_obj, context):
        """Meshes deformed by this armature.

        The stock Cats lookup only walks object parenting, which silently misses meshes that are
        bound by an Armature modifier without being parented (glTF/VRM/FBX imports and any manually
        re-linked mesh). Those meshes were left un-baked while the rest pose still changed, so the
        model looked like nothing happened at all.
        """
        found = []
        seen = set()

        def add(ob):
            if ob.name not in seen and ob.type == 'MESH' and ob.data:
                seen.add(ob.name)
                found.append(ob)

        # 1. the original parenting rule (mesh -> armature, or mesh -> something -> armature)
        try:
            for ob in Common.get_meshes_objects(armature_name=armature_obj.name, check=False):
                add(ob)
        except Exception as e:
            print('Cats PoseToRest: parent-based mesh lookup failed:', e)

        # 2. anything carrying an Armature modifier that points at this armature
        for ob in bpy.data.objects:
            if ob.type != 'MESH' or not ob.data:
                continue
            for mod in ob.modifiers:
                if mod.type == 'ARMATURE' and mod.object == armature_obj and mod.show_viewport:
                    add(ob)
                    break

        # Objects that are not linked into the current view layer cannot be evaluated by the
        # depsgraph at all, so silently "baking" them would just write the un-deformed positions
        # back. Report them instead of corrupting them.
        in_view_layer = set()
        if context.view_layer:
            in_view_layer = {o.name for o in context.view_layer.objects}
        usable = [ob for ob in found if ob.name in in_view_layer]
        skipped = [ob.name for ob in found if ob.name not in in_view_layer]
        return usable, skipped

    @staticmethod
    def force_evaluable(objects, context):
        """Temporarily make objects visible/enabled so the depsgraph really evaluates them.

        Returns a restore callback. `hide_viewport` on an object or on any collection holding it,
        and `exclude` on a layer collection, all remove the object from the depsgraph. When that
        happens `evaluated_get()` hands back the *un-deformed* mesh and the bake writes the mesh
        back onto itself - a completely silent no-op, which is exactly what made this button look
        broken on real models.
        """
        obj_state = []
        coll_state = []
        layer_state = []

        wanted_collections = set()
        for ob in objects:
            for coll in ob.users_collection:
                wanted_collections.add(coll)

        for ob in objects:
            obj_state.append((ob, ob.hide_viewport))
            if ob.hide_viewport:
                ob.hide_viewport = False

        for coll in bpy.data.collections:
            if coll in wanted_collections and coll.hide_viewport:
                coll_state.append((coll, True))
                coll.hide_viewport = False

        def walk(layer_coll):
            if layer_coll.collection in wanted_collections:
                # Deliberately NOT touching `exclude`: un-excluding a layer collection destroys the
                # per-object hide state inside it and cannot be restored faithfully. Meshes in an
                # excluded collection are reported to the user instead.
                if layer_coll.hide_viewport:
                    layer_state.append((layer_coll, 'hide_viewport', True))
                    layer_coll.hide_viewport = False
            for child in layer_coll.children:
                walk(child)

        if context.view_layer:
            try:
                walk(context.view_layer.layer_collection)
            except Exception as e:
                print('Cats PoseToRest: could not unhide layer collections:', e)

        def restore():
            for layer_coll, attr, val in reversed(layer_state):
                try:
                    setattr(layer_coll, attr, val)
                except Exception:
                    pass
            for coll, val in coll_state:
                try:
                    coll.hide_viewport = val
                except Exception:
                    pass
            for ob, val in obj_state:
                try:
                    ob.hide_viewport = val
                except Exception:
                    pass

        return restore

    @staticmethod
    def make_single_user(mesh_obj):
        """Mesh data shared by several objects cannot be baked - writing it would move every user."""
        if mesh_obj.data.users > 1:
            mesh_obj.data = mesh_obj.data.copy()
            return True
        return False

    @staticmethod
    def apply_rest_pose_to_armature(armature_obj, context):
        """Run pose.armature_apply on armature_obj, making it genuinely active first.

        A bare context override does not work here: Blender resolves the armatures to operate on
        from the view layer's real active object, so overriding only `active_object` made the
        operator report success while doing nothing whenever some other object was active.
        """
        view_layer = context.view_layer
        previous_active = view_layer.objects.active
        previous_mode = armature_obj.mode
        was_hidden = armature_obj.hide_get() if armature_obj.name in view_layer.objects else False

        before = [tuple(round(v, 6) for row in b.matrix_local for v in row)
                  for b in armature_obj.data.bones]
        try:
            if was_hidden:
                armature_obj.hide_set(False)
            armature_obj.hide_viewport = False
            if previous_active is not None and previous_active.mode != 'OBJECT':
                try:
                    Common.switch('OBJECT')
                except Exception:
                    pass
            view_layer.objects.active = armature_obj
            armature_obj.select_set(True)
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.armature_apply(selected=False)
            bpy.ops.object.mode_set(mode='OBJECT')
        finally:
            if was_hidden:
                try:
                    armature_obj.hide_set(True)
                except Exception:
                    pass

        after = [tuple(round(v, 6) for row in b.matrix_local for v in row)
                 for b in armature_obj.data.bones]
        return before != after

    # -- main ----------------------------------------------------------------------------------

    def execute(self, context):
        saved_data = Common.SavedData()

        # Preferred targets: the armature picked in Cats and the active object.
        chosen = []
        primary = Common.get_armature()
        if primary is not None and primary.type == 'ARMATURE':
            chosen.append(primary)
        active = context.view_layer.objects.active if context.view_layer else None
        if active is not None and active.type == 'ARMATURE' and active not in chosen:
            chosen.append(active)
        chosen = [a for a in chosen
                  if context.view_layer is None or a.name in context.view_layer.objects]

        if not chosen and not PoseToRest.get_posed_armatures(context):
            self.report({'ERROR'}, 'Cats: no armature found to apply a pose to.')
            return {'CANCELLED'}

        targets = [a for a in chosen if PoseToRest.count_posed_bones(a)]
        fallback_note = ''
        if not targets:
            # The chosen armature holds no pose at all. On multi-armature models (body + clothing)
            # the pose the user actually made very often lives on a different armature than the one
            # in the Cats dropdown - applying only the chosen one is what made this button look
            # like it silently did nothing. Fall back to whatever really is posed, and say so.
            targets = PoseToRest.get_posed_armatures(context)
            if targets:
                fallback_note = (' NOTE: %s had no pose, so the pose on %s was applied instead.'
                                 % (', '.join(a.name for a in chosen) or 'the selected armature',
                                    ', '.join(a.name for a in targets)))

        if not targets:
            self.report({'WARNING'},
                        'Cats: no bones are posed on %s, so there is nothing to apply. '
                        'Pose the bones first, or pick the armature you actually posed.'
                        % (', '.join(a.name for a in chosen) or 'any armature'))
            return {'CANCELLED'}

        posed_total = sum(PoseToRest.count_posed_bones(a) for a in targets)
        also_posed = [a.name for a in PoseToRest.get_posed_armatures(context) if a not in targets]

        baked = 0
        skipped_all = []
        unlinked_all = []
        singled = []
        failed_armatures = []

        for armature_obj in targets:
            mesh_objs, unlinked = PoseToRest.get_bound_meshes(armature_obj, context)
            unlinked_all.extend(unlinked)

            restore_visibility = PoseToRest.force_evaluable(mesh_objs + [armature_obj], context)
            try:
                # Force a depsgraph rebuild so the objects we just re-enabled are actually evaluated.
                context.view_layer.update()
                for mesh_obj in mesh_objs:
                    me = mesh_obj.data
                    if not me:
                        continue
                    try:
                        if PoseToRest.make_single_user(mesh_obj):
                            singled.append(mesh_obj.name)
                            me = mesh_obj.data
                        if me.shape_keys and me.shape_keys.key_blocks:
                            key_blocks = me.shape_keys.key_blocks
                            if len(key_blocks) == 1:
                                # Only a basis key: drop it, bake, then put it back by name.
                                basis_shape_key = key_blocks[0]
                                original_basis_name = basis_shape_key.name
                                mesh_obj.shape_key_remove(basis_shape_key)
                                PoseToRest.apply_armature_to_mesh_with_no_shape_keys(
                                    armature_obj, mesh_obj)
                                mesh_obj.shape_key_add(name=original_basis_name)
                            else:
                                PoseToRest.apply_armature_to_mesh_with_shape_keys(
                                    armature_obj, mesh_obj, context.scene)
                        else:
                            PoseToRest.apply_armature_to_mesh_with_no_shape_keys(
                                armature_obj, mesh_obj)
                        baked += 1
                    except Exception as e:
                        print('Cats PoseToRest: failed on mesh %r: %s' % (mesh_obj.name, e))
                        skipped_all.append('%s (%s)' % (mesh_obj.name, e))

                # With the meshes baked, make the current pose the new rest pose.
                if not PoseToRest.apply_rest_pose_to_armature(armature_obj, context):
                    failed_armatures.append(armature_obj.name)
            finally:
                restore_visibility()

        # Stop pose mode after operation. This is cosmetic - never let it undo the work above.
        try:
            bpy.ops.cats_manual.stop_pose_mode()
        except Exception as e:
            print('Cats PoseToRest: stop_pose_mode failed (harmless):', e)

        saved_data.load(hide_only=True)

        if failed_armatures:
            self.report({'ERROR'},
                        'Cats: the rest pose did NOT change on %s. Nothing was applied there.'
                        % ', '.join(failed_armatures))
            return {'CANCELLED'}

        msg = '%s (%s: %d bones, %d meshes)' % (
            t('PoseToRest.success'),
            ', '.join(a.name for a in targets),
            posed_total, baked)
        msg += fallback_note
        if also_posed:
            msg += (' | %s is also posed but was NOT applied - select it in Cats and run this'
                    ' again if you want it baked too.' % ', '.join(also_posed[:4]))
        if singled:
            msg += ' | copied shared mesh data: %s' % ', '.join(singled[:4])
        if unlinked_all:
            msg += (' | SKIPPED, not in this view layer (their collection is excluded): %s'
                    % ', '.join(unlinked_all[:4]))
        if skipped_all:
            msg += ' | FAILED: %s' % '; '.join(skipped_all[:3])
        noisy = bool(skipped_all or unlinked_all or fallback_note or also_posed)
        self.report({'WARNING'} if noisy else {'INFO'}, msg)
        return {'FINISHED'}

    @staticmethod
    def apply_armature_to_mesh_with_no_shape_keys(armature_obj, mesh_obj):
        armature_mod = mesh_obj.modifiers.new('PoseToRest', 'ARMATURE')
        armature_mod.object = armature_obj
        # In the unlikely case that there was already a modifier with the same name as the new modifier, the new
        # modifier will have ended up with a different name
        mod_name = armature_mod.name
        # Context override to let us run the modifier operators on mesh_obj, even if it's not the active object
        context_override = {'object': mesh_obj}
        # Moving the modifier to the first index will prevent an Info message about the applied modifier not being
        # first and potentially having unexpected results.
        try:
            Common.op_override(bpy.ops.object.modifier_move_to_index, context_override,
                               modifier=mod_name, index=0)
            Common.op_override(bpy.ops.object.modifier_apply, context_override, modifier=mod_name)
        except Exception as e:
            # modifier_apply is picky about context (mode, multi-user data, linked libraries). Fall
            # back to the depsgraph bake, which needs no operator context at all.
            print('Cats PoseToRest: modifier_apply fell back to depsgraph bake on %r: %s'
                  % (mesh_obj.name, e))
            if armature_mod.name in [m.name for m in mesh_obj.modifiers]:
                mesh_obj.modifiers.remove(armature_mod)
            PoseToRest.bake_armature_into_vertices(armature_obj, mesh_obj)

    @staticmethod
    def bake_armature_into_vertices(armature_obj, mesh_obj):
        """Write the armature-deformed positions straight onto the mesh vertices."""
        me = mesh_obj.data
        mods_to_reenable_viewport = []
        for mod in mesh_obj.modifiers:
            if mod.show_viewport:
                mod.show_viewport = False
                mods_to_reenable_viewport.append(mod)
        armature_mod = mesh_obj.modifiers.new('PoseToRest', 'ARMATURE')
        armature_mod.object = armature_obj
        try:
            cos = PoseToRest.evaluated_vertex_cos(mesh_obj, len(me.vertices))
            if cos is not None:
                me.vertices.foreach_set('co', cos)
                me.update()
        finally:
            mesh_obj.modifiers.remove(armature_mod)
            for mod in mods_to_reenable_viewport:
                mod.show_viewport = True

    @staticmethod
    def evaluated_vertex_cos(mesh_obj, expected_vert_count, out=None):
        """Vertex positions of mesh_obj after modifier/shape-key evaluation, or None if unusable.

        Returns None when the depsgraph hands back a mesh with a different vertex count (some
        modifier is still generating geometry) - writing that back would scramble the mesh.
        """
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()
        evaluated = mesh_obj.evaluated_get(depsgraph)
        eval_mesh = evaluated.data
        if eval_mesh is None or len(eval_mesh.vertices) != expected_vert_count:
            print('Cats PoseToRest: %r evaluated to %s verts, expected %d - skipping'
                  % (mesh_obj.name,
                     'None' if eval_mesh is None else len(eval_mesh.vertices),
                     expected_vert_count))
            return None
        if out is None or len(out) != expected_vert_count * 3:
            out = np.empty(expected_vert_count * 3, dtype=np.single)
        eval_mesh.vertices.foreach_get('co', out)
        return out

    @staticmethod
    def apply_armature_to_mesh_with_shape_keys(armature_obj, mesh_obj, scene):
        # The active shape key will be changed, so save the current active index, so it can be restored afterwards
        old_active_shape_key_index = mesh_obj.active_shape_key_index

        # Shape key pinning shows the active shape key in the viewport without blending; effectively what you see when
        # in edit mode. Combined with an armature modifier, we can use this to figure out the correct positions for all
        # the shape keys.
        # Save the current value, so it can be restored afterwards.
        old_show_only_shape_key = mesh_obj.show_only_shape_key
        mesh_obj.show_only_shape_key = True

        # Temporarily remove vertex_groups from and disable mutes on shape keys because they affect pinned shape keys
        me = mesh_obj.data
        shape_key_vertex_groups = []
        shape_key_mutes = []
        key_blocks = me.shape_keys.key_blocks
        for shape_key in key_blocks:
            shape_key_vertex_groups.append(shape_key.vertex_group)
            shape_key.vertex_group = ''
            shape_key_mutes.append(shape_key.mute)
            shape_key.mute = False

        # Temporarily disable all modifiers from showing in the viewport so that they have no effect
        mods_to_reenable_viewport = []
        for mod in mesh_obj.modifiers:
            if mod.show_viewport:
                mod.show_viewport = False
                mods_to_reenable_viewport.append(mod)

        # Temporarily add a new armature modifier
        armature_mod = mesh_obj.modifiers.new('PoseToRest', 'ARMATURE')
        armature_mod.object = armature_obj

        # cos are xyz positions and get flattened when using the foreach_set/foreach_get functions, so the array length
        # will be 3 times the number of vertices
        vert_count = len(me.vertices)
        # We can re-use the same array over and over
        eval_verts_cos_array = np.empty(vert_count * 3, dtype=np.single)

        try:
            for i, shape_key in enumerate(key_blocks):
                # As shape key pinning is enabled, when we change the active shape key, it will change the state of
                # the mesh
                mesh_obj.active_shape_key_index = i
                # The cos of the vertices of the evaluated mesh include the effect of the pinned shape key and all
                # the modifiers (in this case, only the armature modifier we added since all the other modifiers are
                # disabled in the viewport). This gives the same result as applying the armature modifier to a mesh
                # shaped like the active shape key, so the shape key can simply take the evaluated positions.
                #
                # The evaluated object must be re-fetched after every depsgraph update: reusing a cached
                # evaluated object can hand back stale or freed mesh data.
                evaluated_cos = PoseToRest.evaluated_vertex_cos(
                    mesh_obj, vert_count, out=eval_verts_cos_array)
                if evaluated_cos is None:
                    # Nothing usable came back (object not evaluated, or geometry-generating modifier
                    # still active). Bail out rather than write garbage over the shape keys.
                    raise RuntimeError('mesh could not be evaluated by the depsgraph')
                # And set the shape key to those same cos
                shape_key.data.foreach_set('co', evaluated_cos)
                # If it's the basis shape key, we also have to set the mesh vertices to match, otherwise the two will
                # be desynced until Edit mode has been entered and exited, which can cause odd behaviour when
                # creating shape keys with from_mix=False or when removing all shape keys.
                if i == 0:
                    me.vertices.foreach_set('co', evaluated_cos)
            me.update()
        finally:
            # Restore temporarily changed attributes and remove the added armature modifier
            for mod in mods_to_reenable_viewport:
                mod.show_viewport = True
            if armature_mod.name in [m.name for m in mesh_obj.modifiers]:
                mesh_obj.modifiers.remove(armature_mod)
            for shape_key, vertex_group, mute in zip(me.shape_keys.key_blocks,
                                                     shape_key_vertex_groups, shape_key_mutes):
                shape_key.vertex_group = vertex_group
                shape_key.mute = mute
            mesh_obj.active_shape_key_index = old_active_shape_key_index
            mesh_obj.show_only_shape_key = old_show_only_shape_key

@register_wrap
class JoinMeshes(bpy.types.Operator):
    bl_idname = 'cats_manual.join_meshes'
    bl_label = t('JoinMeshes.label')
    bl_description = t('JoinMeshes.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) > 0

    def execute(self, context):
        # Apply transforms of this model
        Common.apply_transforms()
        
        saved_data = Common.SavedData()
        mesh = Common.join_meshes()
        if not mesh:
            saved_data.load()
            self.report({'ERROR'}, t('JoinMeshes.failure'))
            return {'CANCELLED'}

        saved_data.load()
        Common.unselect_all()
        Common.set_active(mesh)
        
        for i in range(0, 3):
            mesh.lock_location[i] = False
            mesh.lock_rotation[i] = False
            mesh.lock_scale[i] = False

        # Set layer of mesh to 0
        if hasattr(mesh, 'layers'):
            mesh.layers[0] = True
            
        self.report({'INFO'}, t('JoinMeshes.success'))
        return {'FINISHED'}


@register_wrap
class JoinMeshesSelected(bpy.types.Operator):
    bl_idname = 'cats_manual.join_meshes_selected'
    bl_label = t('JoinMeshesSelected.label')
    bl_description = t('JoinMeshesSelected.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) > 0

    def execute(self, context):
        saved_data = Common.SavedData()

        if not Common.get_meshes_objects(mode=3):
            saved_data.load()
            self.report({'ERROR'}, t('JoinMeshesSelected.error.noSelect'))
            return {'FINISHED'}

        mesh = Common.join_meshes(mode=1)
        if not mesh:
            saved_data.load()
            self.report({'ERROR'}, t('JoinMeshesSelected.error.cantJoin'))
            return {'CANCELLED'}

        saved_data.load()
        Common.unselect_all()
        Common.set_active(mesh)
        self.report({'INFO'}, t('JoinMeshesSelected.success'))
        
        for i in range(0, 3):
            mesh.lock_location[i] = False
            mesh.lock_rotation[i] = False
            mesh.lock_scale[i] = False

        # Set layer of mesh to 0
        if hasattr(mesh, 'layers'):
            mesh.layers[0] = True
        return {'FINISHED'}


@register_wrap
class SeparateByMaterials(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_materials'
    bl_label = t('SeparateByMaterials.label')
    bl_description = t('SeparateByMaterials.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) >= 1

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.noMesh'))
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.multipleMesh'))
                return {'FINISHED'}
            obj = meshes[0]

        obj_name = obj.name

        Common.separate_by_materials(context, obj)

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, t('SeparateByMaterials.success'))
        return {'FINISHED'}


@register_wrap
class SeparateByLooseParts(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_loose_parts'
    bl_label = t('SeparateByLooseParts.label')
    bl_description = t('SeparateByLooseParts.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.noMesh'))
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.multipleMesh'))
                return {'FINISHED'}
            obj = meshes[0]
        obj_name = obj.name

        Common.separate_by_loose_parts(context, obj)

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, t('SeparateByLooseParts.success'))
        return {'FINISHED'}


@register_wrap
class SeparateByShapekeys(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_shape_keys'
    bl_label = t('SeparateByShapekeys.label')
    bl_description = t('SeparateByShapekeys.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.noMesh'))
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.multipleMesh'))
                return {'FINISHED'}
            obj = meshes[0]
        obj_name = obj.name

        done_message = t('SeparateByShapekeys.success')
        if not Common.separate_by_shape_keys(context, obj):
            done_message = t('SeparateByX.warn.noSeparation')

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, done_message)
        return {'FINISHED'}

@register_wrap
class MergeWeights(bpy.types.Operator):
    bl_idname = 'cats_manual.merge_weights'
    bl_label = t('MergeWeights.label')
    bl_description = t('MergeWeights.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        if not active_obj or not context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and context.selected_editable_bones:
            return True
        if active_obj.mode == 'POSE' and context.selected_pose_bones:
            return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = context.object

        Common.switch('EDIT')

        # Find which bones to work on and put their name and their parent in a list
        parenting_list = {}
        for bone in context.selected_editable_bones:
            parent = bone.parent
            while parent and parent.parent and parent in context.selected_editable_bones:
                parent = parent.parent
            if not parent:
                continue
            parenting_list[bone.name] = parent.name

        # Merge all the bones in the parenting list
        merge_weights(armature, parenting_list)

        saved_data.load()

        self.report({'INFO'}, t('MergeWeights.success', number=str(len(parenting_list))))
        return {'FINISHED'}


@register_wrap
class MergeWeightsToActive(bpy.types.Operator):
    bl_idname = 'cats_manual.merge_weights_to_active'
    bl_label = t('MergeWeightsToActive.label')
    bl_description = t('MergeWeightsToActive.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones and len(bpy.context.selected_editable_bones) > 1:
            if bpy.context.active_bone in bpy.context.selected_editable_bones:
                return True
        elif active_obj.mode == 'POSE' and bpy.context.selected_pose_bones and len(bpy.context.selected_pose_bones) > 1:
            if bpy.context.active_pose_bone in bpy.context.selected_pose_bones:
                return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        # Find which bones to work on and put their name and their parent in a list and parent the bones to the active one
        parenting_list = {}
        for bone in bpy.context.selected_editable_bones:
            if bone.name == bpy.context.active_bone.name:
                continue
            parenting_list[bone.name] = bpy.context.active_bone.name
            bone.parent = bpy.context.active_bone

        # Merge all the bones in the parenting list
        merge_weights(armature, parenting_list)

        # Load original modes
        saved_data.load()

        self.report({'INFO'}, t('MergeWeightsToActive.success', number=str(len(parenting_list))))
        return {'FINISHED'}


def merge_weights(armature, parenting_list):
    Common.switch('OBJECT')
    # Merge the weights on the meshes
    for mesh in Common.get_meshes_objects(armature_name=armature.name, visible_only=bpy.context.scene.merge_visible_meshes_only):
        Common.set_active(mesh)

        for bone, parent in parenting_list.items():
            if not mesh.vertex_groups.get(bone):
                continue
            if not mesh.vertex_groups.get(parent):
                mesh.vertex_groups.new(name=parent)
            Common.mix_weights(mesh, bone, parent)

    # Select armature
    Common.unselect_all()
    Common.set_active(armature)
    Common.switch('EDIT')

    # Delete merged bones
    if not bpy.context.scene.keep_merged_bones:
        for bone in parenting_list.keys():
            edited_bone = armature.data.edit_bones.get(bone)
            if edited_bone is not None:
                armature.data.edit_bones.remove(edited_bone)


@register_wrap
class ApplyTransformations(bpy.types.Operator):
    bl_idname = 'cats_manual.apply_transformations'
    bl_label = t('ApplyTransformations.label')
    bl_description = t('ApplyTransformations.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.apply_transforms()

        saved_data.load()
        self.report({'INFO'}, t('ApplyTransformations.success'))
        return {'FINISHED'}


@register_wrap
class ApplyAllTransformations(bpy.types.Operator):
    bl_idname = 'cats_manual.apply_all_transformations'
    bl_label = t('ApplyAllTransformations.label')
    bl_description = t('ApplyAllTransformations.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.apply_all_transforms()

        saved_data.load()
        self.report({'INFO'}, t('ApplyAllTransformations.success'))
        return {'FINISHED'}


@register_wrap
class RemoveZeroWeightBones(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_zero_weight_bones'
    bl_label = t('RemoveZeroWeightBones.label')
    bl_description = t('RemoveZeroWeightBones.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        Common.remove_rigidbodies_global()
        count = Common.delete_zero_weight()
        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()
        self.report({'INFO'}, t('RemoveZeroWeightBones.success', number=str(count)))
        return {'FINISHED'}


@register_wrap
class RemoveZeroWeightGroups(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_zero_weight_groups'
    bl_label = t('RemoveZeroWeightGroups.label')
    bl_description = t('RemoveZeroWeightGroups.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return Common.get_meshes_objects(mode=2, check=False)

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        Common.remove_rigidbodies_global()
        count = Common.remove_unused_vertex_groups()

        saved_data.load()
        self.report({'INFO'}, t('RemoveZeroWeightGroups.success', number=str(count)))
        return {'FINISHED'}

    # Maybe only remove groups from selected meshes instead of from all of them
    # THis still needs some work
    #
    # @classmethod
    # def poll2(cls, context):
    #     return Common.get_meshes_objects(mode=3, check=False)
    #
    # def execute2(self, context):
    #     saved_data = Common.SavedData()
    #     remove_count = 0
    #
    #     for mesh in Common.get_meshes_objects(mode=3):
    #         remove_count += Common.remove_unused_vertex_groups_of_mesh(mesh)
    #
    #     saved_data.load()
    #     self.report({'INFO'}, 'Removed ' + str(remove_count) + ' zero weight vertex groups.')
    #     return {'FINISHED'}

@register_wrap
class RemoveConstraints(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_constraints'
    bl_label = t('RemoveConstraints.label')
    bl_description = t('RemoveConstraints.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        Common.remove_rigidbodies_global()
        Common.delete_bone_constraints()
        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()
        self.report({'INFO'}, t('RemoveConstraints.success'))
        return {'FINISHED'}

@register_wrap
class GenerateTwistBones(bpy.types.Operator):
    bl_idname = 'cats_manual.generate_twist_bones'
    bl_label = "Generate Twist Bones"
    bl_description = "Attempt to generate twistbones for the selected bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not Common.get_armature():
            return False
        return context.selected_editable_bones

    def execute(self, context):
        saved_data = Common.SavedData()
        
        # Check if the property exists in the scene, and create it if it doesn't
        if not hasattr(context.scene, 'generate_twistbones_upper'):
            bpy.types.Scene.generate_twistbones_upper = bpy.props.BoolProperty(
                name="Generate Twist Bones Upper",
                description="Generate Twist Bones Upper",
                default=True
            )

        context.object.data.use_mirror_x = False
        context.object.use_mesh_mirror_x = False
        context.object.pose.use_mirror_x = False
        generate_upper = context.scene.generate_twistbones_upper
        armature = context.object
        # For each bone...
        bone_pairs = []
        twist_locations = dict()
        editable_bone_names = [bone.name for bone in context.selected_editable_bones]
        for bone_name in editable_bone_names:
            # Add '<bone>_Twist' and move the head halfway to the tail
            bone = armature.data.edit_bones[bone_name]
            if not generate_upper:
                twist_bone = armature.data.edit_bones.new('~' + bone.name + "_Twist")
                twist_bone.tail = bone.tail
                twist_bone.head[:] = [(bone.head[i] + bone.tail[i]) / 2 for i in range(3)]
                twist_locations[twist_bone.name] = (twist_bone.head[:], twist_bone.tail[:])
            else:
                twist_bone = armature.data.edit_bones.new('~' + bone.name + "_UpperTwist")
                twist_bone.tail[:] = [(bone.head[i] + bone.tail[i]) / 2 for i in range(3)]
                twist_bone.head = bone.head
                twist_locations[twist_bone.name] = (twist_bone.tail[:], twist_bone.head[:])
            twist_bone.parent = bone

            bone_pairs.append((bone.name, twist_bone.name))

        Common.switch('OBJECT')
        for bone_name, twist_bone_name in bone_pairs:
            twist_bone_head_tail = twist_locations[twist_bone_name]
            print(twist_bone_head_tail[0])
            print(twist_bone_head_tail[1])
            for mesh in Common.get_meshes_objects(armature_name=armature.name):
                if not bone_name in mesh.vertex_groups:
                    continue

                Common.set_active(mesh)
                context.object.data.use_mirror_vertex_groups = False
                context.object.data.use_mirror_x = False
                context.object.use_mesh_mirror_x = False

                mesh.vertex_groups.new(name=twist_bone_name)

                # twist bone weights are a linear(?) gradient from head to tail, 0-1 * orig weight
                group_idx = mesh.vertex_groups[bone_name].index
                for vertex in mesh.data.vertices:
                    if any(group.group == group_idx for group in vertex.groups):
                        # calculate

                        _, dist = intersect_point_line(vertex.co, twist_bone_head_tail[0], twist_bone_head_tail[1])
                        clamped_dist = max(0.0, min(1.0, dist))
                        # orig bone weights are their original weight minus the twist weight
                        twist_weight = mesh.vertex_groups[bone_name].weight(vertex.index) * clamped_dist
                        untwist_weight = mesh.vertex_groups[bone_name].weight(vertex.index) * (1.0 - clamped_dist)
                        mesh.vertex_groups[twist_bone_name].add([vertex.index], twist_weight, "REPLACE")
                        mesh.vertex_groups[bone_name].add([vertex.index], untwist_weight, "REPLACE")

        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()
        self.report({'INFO'}, t('RemoveConstraints.success'))
        return {'FINISHED'}


@register_wrap
class RecalculateNormals(bpy.types.Operator):
    bl_idname = 'cats_manual.recalculate_normals'
    bl_label = t('RecalculateNormals.label')
    bl_description = t('RecalculateNormals.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')
        Common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)

        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()
        self.report({'INFO'}, t('RecalculateNormals.success'))
        return {'FINISHED'}


@register_wrap
class FlipNormals(bpy.types.Operator):
    bl_idname = 'cats_manual.flip_normals'
    bl_label = t('FlipNormals.label')
    bl_description = t('FlipNormals.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')
        Common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.flip_normals()

        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()
        self.report({'INFO'}, t('FlipNormals.success'))
        return {'FINISHED'}

@register_wrap
class RemoveDoubles(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_doubles'
    bl_label = t('RemoveDoubles.label')
    bl_description = t('RemoveDoubles.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True
        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def check_shapekeys_impact(self, mesh, context):
        if not Common.has_shapekeys(mesh):
            return False
            
        # Optimized shape key checking using numpy
        basis = np.array([v.co for v in mesh.data.shape_keys.key_blocks[0].data])
        threshold = context.scene.remove_doubles_threshold
        
        for shape in mesh.data.shape_keys.key_blocks[1:]:
            shape_verts = np.array([v.co for v in shape.data])
            distances = np.linalg.norm(basis - shape_verts, axis=1)
            if np.any(distances > threshold):
                return True
        return False

    def process_mesh(self, mesh, context):
        threshold = context.scene.remove_doubles_threshold
        try:
            # Create BMesh
            bm = bmesh.new()
            bm.from_mesh(mesh.data)
            
            # Store initial triangle count
            initial_tris = len(bm.faces)
            
            # Optimize BMesh operations
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=threshold)
            
            # Remove loose vertices
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
            
            # Update mesh
            bm.to_mesh(mesh.data)
            mesh.data.update()
            bm.free()
            
            return initial_tris - len(mesh.data.polygons)
            
        except Exception as e:
            raise ValueError(f"Failed to process mesh {mesh.name}: {str(e)}")

    def invoke(self, context, event):
        meshes = Common.get_meshes_objects(mode=3)
        if not meshes:
            meshes = [Common.get_meshes_objects()[0]]

        # Check for shape keys impact first
        for mesh in meshes:
            if self.check_shapekeys_impact(mesh, context):
                return context.window_manager.invoke_props_dialog(self)
        
        # If no shape keys affected, proceed directly
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text=t('RemoveDoubles.warning.shapekeys'))
        col.label(text=t('RemoveDoubles.warning.shapekeys.impact'))
        col.label(text=t('RemoveDoubles.warning.shapekeys.continue'))

    def execute(self, context):
        try:
            saved_data = Common.SavedData()
            removed_tris = 0
            
            meshes = Common.get_meshes_objects(mode=3)
            if not meshes:
                meshes = [Common.get_meshes_objects()[0]]

            Common.set_default_stage()
            Common.remove_rigidbodies_global()

            # Progress reporting
            wm = context.window_manager
            wm.progress_begin(0, len(meshes))

            # Process meshes with optimized handling
            for i, mesh in enumerate(meshes):
                try:
                    # Save shape keys state
                    if Common.has_shapekeys(mesh):
                        Common.save_shapekey_order(mesh.name)
                    
                    # Process mesh with optimized method
                    removed = self.process_mesh(mesh, context)
                    removed_tris += removed
                    
                    # Validate result
                    if not mesh.data.vertices or not mesh.data.polygons:
                        raise ValueError("Mesh data became invalid")
                        
                    # Repair shape keys if needed
                    if Common.has_shapekeys(mesh):
                        Common.repair_shapekey_order(mesh.name)
                        
                except Exception as e:
                    Common.show_error(4, [
                        t('RemoveDoubles.error.failed'),
                        str(e),
                        t('RemoveDoubles.error.mesh', mesh=mesh.name)
                    ])
                    continue
                finally:
                    wm.progress_update(i)

            wm.progress_end()
            Common.set_default_stage()
            Common.remove_rigidbodies_global()
            saved_data.load()

            self.report({'INFO'}, t('RemoveDoubles.success', number=str(removed_tris)))
            return {'FINISHED'}

        except Exception as e:
            if 'wm' in locals():
                wm.progress_end()
            Common.show_error(4, [
                t('RemoveDoubles.error.unexpected'),
                str(e)
            ])
            return {'CANCELLED'}

@register_wrap
class OptimizeStaticShapekeys(bpy.types.Operator):
    bl_idname = 'cats_manual.optimize_static_shapekeys'
    bl_label = 'Optimize Static Shapekeys'
    bl_description = "Move all shapekey-affected geometry into its own mesh, significantly decreasing GPU cost"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        objs = [context.active_object]
        if not objs[0] or (objs[0] and (objs[0].type != 'MESH' or objs[0].data.shape_keys is None)):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            objs = meshes

        if len([obj for obj in objs if obj.type == 'MESH']) > 1:
            self.report({'ERROR'}, "Meshes must first be combined for this to be beneficial.")

        for mesh in objs:
            if mesh.type == 'MESH' and mesh.data.shape_keys is not None:
                context.view_layer.objects.active = mesh

                # Ensure corner normals exist
                if not mesh.data.corner_normals:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type="VERT")
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.set_normals_from_faces(keep_sharp=True)

                    # Set custom normals from corner normals
                    normal_list = []
                    for corner_normal in mesh.data.corner_normals:
                        normal_list.append(corner_normal.normal)

                        mesh.data.normals_split_custom_set(normal_list)
                        mesh.data.update()

                # Separate non-animating
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_mode(type="VERT")
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                for key_block in mesh.data.shape_keys.key_blocks[1:]:
                    basis = mesh.data.shape_keys.key_blocks[0]

                    for idx, vert in enumerate(key_block.data):
                        if (math.sqrt(math.pow(basis.data[idx].co[0] - vert.co[0], 2.0) +
                        math.pow(basis.data[idx].co[1] - vert.co[1], 2.0) +
                        math.pow(basis.data[idx].co[2] - vert.co[2], 2.0)) > 0.0001):
                            mesh.data.vertices[idx].select = True

                if not all(v.select for v in mesh.data.vertices):
                    if any(v.select for v in mesh.data.vertices):
                        # Some affected, separate
                        bpy.ops.object.mode_set(mode = 'EDIT')
                        bpy.ops.mesh.select_more()
                        bpy.ops.mesh.split() # required or custom normals aren't preserved
                        bpy.ops.mesh.separate(type='SELECTED')
                        bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.context.object.active_shape_key_index = 0
                    mesh.name = "Static"
                    mesh['catsForcedExportName'] = "Static"
                    # remove all shape keys for 'Static'
                    bpy.ops.object.shape_key_remove(all=True)

        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()
        self.report({'INFO'}, "Separation complete.")
        return {'FINISHED'}
        

@register_wrap
class RepairShapekeys(bpy.types.Operator):
    bl_idname = 'cats_manual.repair_shapekeys'
    bl_label = 'Repair Broken Shapekeys'
    bl_description = "Attempt to repair messed up shapekeys caused by some Blender operations"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        objs = [context.active_object]
        if not objs[0] or (objs[0] and (objs[0].type != 'MESH' or objs[0].data.shape_keys is None)):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            objs = meshes

        for obj in objs:
            if obj.data.shape_keys is None:
                continue
            Common.unselect_all()
            Common.set_active(obj)
            Common.switch('EDIT')
            Common.switch('EDIT')
            points = []
            # For each vertex index...
            for vert_idx in range(0, len(obj.data.shape_keys.key_blocks[0].data)):
                # find the most common version of the point in all the non-basis keys
                verts = dict()
                for shape_idx in range(1, len(obj.data.shape_keys.key_blocks)):
                    vert_coord = obj.data.shape_keys.key_blocks[shape_idx].data[vert_idx]
                    if not vert_coord in verts:
                        verts[vert_coord] = 0
                    verts[vert_coord] += 1
                found_coord = max(verts.items(), key=operator.itemgetter(1))[0]
                print(found_coord)
                points.append(found_coord)
            # create a new shapekey
            Common.switch('OBJECT')
            bpy.ops.object.shape_key_add(from_mix=False)
            obj.active_shape_key.name = "CATS Antibasis"

            # set it to the most-common points
            for vert_idx in range(0, len(obj.data.shape_keys.key_blocks[0].data)):
                obj.active_shape_key.data[vert_idx].co[0] = points[vert_idx].co[0]
                obj.active_shape_key.data[vert_idx].co[1] = points[vert_idx].co[1]
                obj.active_shape_key.data[vert_idx].co[2] = points[vert_idx].co[2]
            # un-apply it to all other shapekeys
            for idx in range(1, len(obj.data.shape_keys.key_blocks) - 1):
                obj.active_shape_key_index = idx
                Common.switch('EDIT')
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.blend_from_shape(shape="CATS Antibasis", blend=-1.0, add=True)
                Common.switch('OBJECT')
            obj.shape_key_remove(key=obj.data.shape_keys.key_blocks["CATS Antibasis"])
            obj.active_shape_key_index = 0


        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()
        self.report({'INFO'}, "Repair complete.")
        return {'FINISHED'}


@register_wrap
class RemoveDoublesNormal(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_doubles_normal'
    bl_label = t('RemoveDoublesNormal.label')
    bl_description = t('RemoveDoublesNormal.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        removed_tris = 0
        meshes = Common.get_meshes_objects(mode=3)
        if not meshes:
            meshes = [Common.get_meshes_objects()[0]]

        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        for mesh in meshes:
            removed_tris += Common.remove_doubles(mesh, 0.00002, save_shapes=True)

        Common.set_default_stage()
        Common.remove_rigidbodies_global()

        saved_data.load()

        self.report({'INFO'}, t('RemoveDoublesNormal.success', number=str(removed_tris)))
        return {'FINISHED'}


@register_wrap
class FixVRMShapesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.fix_vrm_shapes'
    bl_label = t('FixVRMShapesButton.label')
    bl_description = t('FixVRMShapesButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.get_meshes_objects(check=False)

    def execute(self, context):
        saved_data = Common.SavedData()

        mesh = Common.get_meshes_objects()[0]
        slider_max_eyes = 0.33333
        slider_max_mouth = 0.94

        if not Common.has_shapekeys(mesh):
            self.report({'INFO'}, t('FixVRMShapesButton.warn.notDetected'))
            saved_data.load()
            return {'CANCELLED'}

        Common.set_active(mesh)
        bpy.ops.object.shape_key_clear()

        shapekeys = enumerate(mesh.data.shape_keys.key_blocks)

        # Find shapekeys to merge
        shapekeys_to_merge_eyes = {}
        shapekeys_to_merge_mouth = {}
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                continue

            # Set max slider
            if shapekey.name.startswith('eye_'):
                shapekey.slider_max = slider_max_eyes
            else:
                shapekey.slider_max = slider_max_mouth

            # Split name
            name_split = shapekey.name.split('00')
            if len(name_split) < 2:
                continue
            pre_name = name_split[0]
            post_name = name_split[1]

            # Put shapekey in corresponding list
            if pre_name == "eye_face.f":
                shapekeys_to_merge_eyes[post_name] = []
            elif pre_name == "kuti_face.f":
                shapekeys_to_merge_mouth[post_name] = []

        # Add all matching shapekeys to the merge list
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                continue

            name_split = shapekey.name.split('00')
            if len(name_split) < 2:
                continue
            pre_name = name_split[0]
            post_name = name_split[1]

            if post_name in shapekeys_to_merge_eyes.keys():
                if pre_name == 'eye_face.f' or pre_name == 'eye_siroL.sL' or pre_name == 'eye_line_u.elu':
                    shapekeys_to_merge_eyes[post_name].append(shapekey.name)

            elif post_name in shapekeys_to_merge_mouth.keys():
                if pre_name == 'kuti_face.f' or pre_name == 'kuti_ha.ha' or pre_name == 'kuti_sita.t':
                    shapekeys_to_merge_mouth[post_name].append(shapekey.name)

        # Merge all the shape keys
        shapekeys_used = []
        for name, shapekeys_merge in shapekeys_to_merge_eyes.items():
            if len(shapekeys_merge) <= 1:
                continue

            for shapekey_name in shapekeys_merge:
                mesh.data.shape_keys.key_blocks[shapekey_name].value = slider_max_eyes
                shapekeys_used.append(shapekey_name)

            mesh.shape_key_add(name='eyes_' + name[1:], from_mix=True)
            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.object.shape_key_move(type='TOP')
            bpy.ops.object.shape_key_clear()

        for name, shapekeys_merge in shapekeys_to_merge_mouth.items():
            if len(shapekeys_merge) <= 1:
                continue

            for shapekey_name in shapekeys_merge:
                mesh.data.shape_keys.key_blocks[shapekey_name].value = slider_max_mouth
                shapekeys_used.append(shapekey_name)

            mesh.shape_key_add(name='mouth_' + name[1:], from_mix=True)
            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.object.shape_key_move(type='TOP')
            bpy.ops.object.shape_key_clear()

        # Remove all the used shapekeys
        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey.name in shapekeys_used:
                bpy.ops.object.shape_key_remove(all=False)

        saved_data.load()

        self.report({'INFO'}, t('FixVRMShapesButton.success'))
        return {'FINISHED'}

def duplicatebone(b):
    arm = bpy.context.object.data
    cb = arm.edit_bones.new(b.name)

    cb.head = b.head
    cb.tail = b.tail
    cb.matrix = b.matrix
    cb.parent = b.parent
    return cb

@register_wrap
class CreateDigitigradeLegs(bpy.types.Operator):
    """Create digitigrade legs while in edit mode with digitigrade thighs selected."""
    bl_idname = "armature.createdigitigradelegs"
    bl_label = "Create Digitigrade Legs"

    @classmethod
    def poll(cls, context):
        if(context.active_object is None):
            return False
        if(context.selected_editable_bones is not None):
            if(len(context.selected_editable_bones) == 2):
                return True
        return False

    def execute(self, context):

        for digi0 in context.selected_editable_bones:
            digi1 = None
            digi2 = None
            digi3 = None

            try:
                digi1 = digi0.children[0]
                digi2 = digi1.children[0]
                digi3 = digi2.children[0]
            except:
                print("bone format incorrect! Please select a chain of 4 continious bones!")
            digi4 = None
            try:
                digi4 = digi3.children[0]
            except:
                print("no toe bone. Continuing.")
            digi0.select = True
            digi1.select = True
            digi2.select = True
            digi3.select = True
            if(digi4):
                digi4.select = True
            bpy.ops.armature.roll_clear()
            bpy.ops.armature.select_all(action='DESELECT')

            scene = context.scene
            #creating transform for upper leg
            digi0.select = True
            bpy.ops.transform.create_orientation(name="CATS_digi0", overwrite=True)
            bpy.ops.armature.select_all(action='DESELECT')


            #duplicate digi0 and assign it to thigh
            thigh = duplicatebone(digi0)
            bpy.ops.armature.select_all(action='DESELECT')

            #make digi2 parrallel to digi1
            digi2.align_orientation(digi0)

            #extrude thigh
            thigh.select_tail = True
            bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False},TRANSFORM_OT_translate=None)
            #set new bone to calf varible
            bpy.ops.armature.select_more()
            calf = context.selected_bones[0]
            bpy.ops.armature.select_all(action='DESELECT')

            #set calf end to  digi2 end
            calf.tail = digi2.tail

            #make copy of calf, flip it, and then align bone so that it's head is moved to match in align phase
            flipedcalf = duplicatebone(calf)
            bpy.ops.armature.select_all(action='DESELECT')
            flipedcalf.select = True
            bpy.ops.armature.switch_direction()
            bpy.ops.armature.select_all(action='DESELECT')
            flippeddigi1 = duplicatebone(digi1)
            bpy.ops.armature.select_all(action='DESELECT')
            flippeddigi1.select = True
            bpy.ops.armature.switch_direction()
            bpy.ops.armature.select_all(action='DESELECT')



            #align flipped calf to flipped middle leg to move the head
            flipedcalf.align_orientation(flippeddigi1)

            flipedcalf.length = flippeddigi1.length

            #assign calf tail to flipped calf head so it moves calf's head
            calf.head = flipedcalf.tail

            #delete helper bones
            bpy.ops.armature.select_all(action='DESELECT')
            flippeddigi1.select = True
            bpy.ops.armature.delete()
            bpy.ops.armature.select_all(action='DESELECT')
            flipedcalf.select = True
            bpy.ops.armature.delete()
            bpy.ops.armature.select_all(action='DESELECT')


            #Tada! It's done! Now to duplicate toes and change parents


            #duplicate old foot and reparent
            newfoot = duplicatebone(digi3)
            newfoot.parent = calf
            #create toe bone if it exists
            if(digi4):
                #duplicate old toe and reparent
                newtoe = duplicatebone(digi4)
                newtoe.parent = newfoot
            #finally done!
        return {'FINISHED'}

@register_wrap
class DuplicateBonesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.duplicate_bones'
    bl_label = t('DuplicateBonesButton.label')
    bl_description = t('DuplicateBonesButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones:
            return True
        elif active_obj.mode == 'POSE' and bpy.context.selected_pose_bones:
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()
        armature = bpy.context.object
        
        # Get selected bones before switching modes
        if armature.mode == 'POSE':
            selected_bone_names = [bone.name for bone in bpy.context.selected_pose_bones]
        else:
            selected_bone_names = [bone.name for bone in bpy.context.selected_editable_bones]
        
        # Switch to edit mode
        Common.switch('EDIT')
        
        # Cache edit bones
        edit_bones = armature.data.edit_bones
        selected_bones = [edit_bones[name] for name in selected_bone_names if name in edit_bones]
        bone_count = len(selected_bones)
        
        # Create mapping for duplicate bones
        duplicate_vertex_groups = {
            bone.name: f"{bone.name}{'_' if not bone.name.endswith('_') else ''}copy"
            for bone in selected_bones
        }
        
        # Batch create bones
        new_bones = {}
        for orig_name, new_name in duplicate_vertex_groups.items():
            orig_bone = edit_bones.get(orig_name)
            new_bone = edit_bones.new(new_name)
            new_bones[new_name] = new_bone
            
            new_bone.head = orig_bone.head
            new_bone.tail = orig_bone.tail
            new_bone.parent = orig_bone.parent

        # Fix parenting in batch
        for new_name, new_bone in new_bones.items():
            if new_bone.parent and new_bone.parent.name in duplicate_vertex_groups:
                new_bone.parent = edit_bones.get(duplicate_vertex_groups[new_bone.parent.name])

        # Process vertex groups for all meshes
        wm = context.window_manager
        meshes = Common.get_meshes_objects(armature_name=armature.name)
        wm.progress_begin(0, len(meshes))

        for idx, mesh in enumerate(meshes):
            self._process_mesh_weights(mesh, duplicate_vertex_groups)
            wm.progress_update(idx)

        wm.progress_end()
        saved_data.load()

        self.report({'INFO'}, t('DuplicateBonesButton.success', number=str(bone_count)))
        return {'FINISHED'}

    def _process_mesh_weights(self, mesh, duplicate_groups):
        Common.set_active(mesh)
        
        # Create all vertex groups first
        for new_name in duplicate_groups.values():
            mesh.vertex_groups.new(name=new_name)
            
        # Mix weights in batch
        for orig_name, new_name in duplicate_groups.items():
            Common.mix_weights(mesh, orig_name, new_name, delete_old_vg=False)


@register_wrap
class ConnectBonesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.connect_bones'
    bl_label = 'Connect Bones'
    bl_description = 'Connects all bones with their respective children'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        return active_obj and active_obj.type == 'ARMATURE'

    def execute(self, context):
        saved_data = Common.SavedData()
        armature = bpy.context.object
        
        try:
            Common.switch('EDIT')
            
            # Cache edit bones for better performance
            edit_bones = armature.data.edit_bones
            bones_processed = 0
            
            # Process bone connections in batch
            for bone in edit_bones:
                if bone.parent:
                    bone.use_connect = True
                    bones_processed += 1
            
            Common.fix_bone_orientations(armature)
            
            self.report({'INFO'}, f'Connected {bones_processed} bones successfully!')
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f'Failed to connect bones: {str(e)}')
            return {'CANCELLED'}
            
        finally:
            saved_data.load()


@register_wrap
class ConvertToValveButton(bpy.types.Operator):
    bl_idname = 'cats_manual.convert_to_valve'
    bl_label = 'Convert Bones To Valve'
    bl_description = 'Converts all main bone names to default valve bone names.' \
                     '\nMake sure your model has the CATS standard bone names from after using Fix Model'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    armature_name = bpy.props.StringProperty(default = "")

    @classmethod
    def poll(cls, context):
        if not Common.get_armature():
            return False
        return True

    def execute(self, context):
        translate_bone_fails = 0
        if self.armature_name == "":
            armature = Common.get_armature()
        else:
            armature = bpy.data.objects[self.armature_name]

        reverse_bone_lookup = dict()
        for (preferred_name, name_list) in bone_names.items():
            for name in name_list:
                reverse_bone_lookup[name] = preferred_name

        valve_translations = {
            'hips': "ValveBiped.Bip01_Pelvis",
            'spine': "ValveBiped.Bip01_Spine",
            'chest': "ValveBiped.Bip01_Spine1",
            'upper_chest': "ValveBiped.Bip01_Spine2",
            'neck': "ValveBiped.Bip01_Neck1",
            'head': "ValveBiped.Bip01_Head1", #head1 is on purpose.
            'left_leg': "ValveBiped.Bip01_L_Thigh",
            'left_knee': "ValveBiped.Bip01_L_Calf",
            'left_ankle': "ValveBiped.Bip01_L_Foot",
            'left_toe': "ValveBiped.Bip01_L_Toe0",
            'right_leg': "ValveBiped.Bip01_R_Thigh",
            'right_knee': "ValveBiped.Bip01_R_Calf",
            'right_ankle': "ValveBiped.Bip01_R_Foot",
            'right_toe': "ValveBiped.Bip01_R_Toe0",
            'left_shoulder': "ValveBiped.Bip01_L_Clavicle",
            'left_arm': "ValveBiped.Bip01_L_UpperArm",
            'left_elbow': "ValveBiped.Bip01_L_Forearm",
            'left_wrist': "ValveBiped.Bip01_L_Hand",
            'right_shoulder': "ValveBiped.Bip01_R_Clavicle",
            'right_arm': "ValveBiped.Bip01_R_UpperArm",
            'right_elbow': "ValveBiped.Bip01_R_Forearm",
            'right_wrist': "ValveBiped.Bip01_R_Hand",
            #need finger bones for Gmod Conversion Script
            'pinkie_1_l': "ValveBiped.Bip01_L_Finger4",
            'pinkie_2_l': "ValveBiped.Bip01_L_Finger41",
            'pinkie_3_l': "ValveBiped.Bip01_L_Finger42",
            'ring_1_l': "ValveBiped.Bip01_L_Finger3",
            'ring_2_l': "ValveBiped.Bip01_L_Finger31",
            'ring_3_l': "ValveBiped.Bip01_L_Finger32",
            'middle_1_l': "ValveBiped.Bip01_L_Finger2",
            'middle_2_l': "ValveBiped.Bip01_L_Finger21",
            'middle_3_l': "ValveBiped.Bip01_L_Finger22",
            'index_1_l': "ValveBiped.Bip01_L_Finger1",
            'index_2_l': "ValveBiped.Bip01_L_Finger11",
            'index_3_l': "ValveBiped.Bip01_L_Finger12",
            'thumb_1_l': "ValveBiped.Bip01_L_Finger0",
            'thumb_2_l': "ValveBiped.Bip01_L_Finger01",
            'thumb_3_l': "ValveBiped.Bip01_L_Finger02",

            'pinkie_1_r': "ValveBiped.Bip01_R_Finger4",
            'pinkie_2_r': "ValveBiped.Bip01_R_Finger41",
            'pinkie_3_r': "ValveBiped.Bip01_R_Finger42",
            'ring_1_r': "ValveBiped.Bip01_R_Finger3",
            'ring_2_r': "ValveBiped.Bip01_R_Finger31",
            'ring_3_r': "ValveBiped.Bip01_R_Finger32",
            'middle_1_r': "ValveBiped.Bip01_R_Finger2",
            'middle_2_r': "ValveBiped.Bip01_R_Finger21",
            'middle_3_r': "ValveBiped.Bip01_R_Finger22",
            'index_1_r': "ValveBiped.Bip01_R_Finger1",
            'index_2_r': "ValveBiped.Bip01_R_Finger11",
            'index_3_r': "ValveBiped.Bip01_R_Finger12",
            'thumb_1_r': "ValveBiped.Bip01_R_Finger0",
            'thumb_2_r': "ValveBiped.Bip01_R_Finger01",
            'thumb_3_r': "ValveBiped.Bip01_R_Finger02"
        }

        for bone in armature.data.bones:
            if simplify_bonename(bone.name) in reverse_bone_lookup and reverse_bone_lookup[simplify_bonename(bone.name)] in valve_translations:
                bone.name = valve_translations[reverse_bone_lookup[simplify_bonename(bone.name)]]
            else:
                translate_bone_fails += 1

        if translate_bone_fails > 0:
            self.report({'INFO'}, "Error! Failed to translate {translate_bone_fails} bones! Make sure your model has standard bone names!")

        self.report({'INFO'}, 'Connected all bones!')
        return {'FINISHED'}

@register_wrap
class RemoveRigidbodiesJointsOperator(bpy.types.Operator):
    bl_idname = 'my_plugin.remove_rigidbodies_joints'
    bl_label = t('RemoveRigidbodiesJointsOperator.label')
    bl_description = t('RemoveRigidbodiesJointsOperator.description')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not Common.get_armature():
            return False

        if len(Common.get_armature_objects()) == 0:
            return False

        return True

    def execute(self, context):
        Common.set_default_stage()
        armature = context.active_object
        to_delete = []
        for child in Common.get_top_parent(armature).children:
            if 'rigidbodies' in child.name or 'joints' in child.name and child.name not in to_delete:
                to_delete.append(child.name)
                continue
            for child2 in child.children:
                if 'rigidbodies' in child2.name or 'joints' in child2.name and child2.name not in to_delete:
                    to_delete.append(child2.name)
                    continue
        for obj_name in to_delete:
            Common.switch('EDIT')
            Common.switch('OBJECT')
            Common.delete_hierarchy(bpy.data.objects[obj_name])

        self.report({'INFO'}, 'Removed rigidbodies and joints.')
        return {'FINISHED'}
