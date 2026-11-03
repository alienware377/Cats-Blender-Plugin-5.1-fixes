# Changelog

## 5.1.2

Bug-fix release on top of 5.1.1. No new features; nothing was removed.

### Apply as Rest Pose no longer silently does nothing

The headline bug: on many models the button reported *"Pose successfully applied as rest pose"*
and changed nothing at all. Several independent causes, all of them silent.

- **The pose was on a different armature than the one selected.** Cats only ever applied the pose
  to the armature picked in its own dropdown. Models where the clothing rides a second armature are
  common, and the pose is often made on that second armature, so Cats applied an empty pose and
  reported success. It now falls back to whichever armature is actually posed and
  says which one it used. If the selected armature *is* posed, only that one is touched, and any
  other posed armature is named in the report rather than being modified behind your back.
- **"No bones are posed" is now a warning instead of a success message.** Previously indistinguishable
  from a real apply.
- **Meshes bound by an Armature modifier without being parented were skipped.** The mesh lookup
  walked object parenting only, so glTF/VRM/FBX imports and any manually re-linked mesh were left
  un-baked while the rest pose still changed. That looks exactly like "nothing happened".
- **Meshes hidden with `hide_viewport` (the monitor icon), or inside a collection hidden the same
  way, were skipped.** Those objects are dropped from the depsgraph, so `evaluated_get()` returned
  *undeformed* geometry and the bake wrote the mesh back onto itself. They are now temporarily
  enabled for the bake and restored afterwards.
- **Mesh data shared between objects** is now copied first; baking it in place used to move every
  other user of that mesh.
- **Meshes in an excluded collection are named in the report** instead of being silently dropped.
  They are deliberately *not* auto-included: un-excluding a layer collection destroys the per-object
  hide state inside it and cannot be restored faithfully.
- **`pose.armature_apply` is no longer driven by a bare context override.** Blender resolves the
  armatures to operate on from the view layer's real active object, so overriding only
  `active_object` made the operator report success while doing nothing whenever a different object
  happened to be active. The armature is now made active first, and the result is checked: if the
  rest pose did not actually change, that is now an error rather than a success.
- The operator reports what it did: which armature, how many bones, how many meshes, and the name
  of anything skipped.

### Other fixes

- **Apply All Transforms crashed** with `Object '<name>' cannot be selected because it is not in
  View Layer` on any file containing objects that exist but sit in no collection (leftovers from
  deleted collections, appended data, backup collections). `select` / `hide` / `set_active` /
  `is_hidden` now skip such objects with a console note instead of raising mid-operation and
  leaving the model half-processed.
- **`stop_pose_mode` and `start_pose_mode` no longer abort their caller.** They assumed Pose mode
  and a 3D-View context; `pose.rot_clear` and `object.hide_view_clear` raised "context is incorrect"
  otherwise, which aborted whatever called them *after* the model had already been changed. Pose
  clearing now falls back to the data API when the operators cannot poll.
- **`get_meshes_objects(visible_only=True)` skipped every other mesh**, because it removed items from
  the list it was iterating.
- **`get_meshes_objects(check=True)` no longer treats objects outside the view layer as corrupt.**
  They were passed to the "delete corrupted mesh" path.
- **The shape-key bake no longer reuses a cached evaluated object** across depsgraph updates, which
  could hand back stale mesh data, and it bails out instead of writing garbage if the evaluated mesh
  comes back with a different vertex count.
- **Certificate verification is no longer disabled.** The updater set
  `ssl._create_default_https_context = ssl._create_unverified_context`, which turns off TLS
  verification for *every* HTTPS request made by the whole Blender process, not just its own.
- **The updater now points at this fork's releases.** It previously checked a Team Neoneko host, so
  it could offer to "update" this build onto an unrelated one and overwrite these fixes.
- **The updater could never detect an update at all.** It compared the release tag with the prefix
  stripped (`5.1.2` -> `2`) against a hard-coded `CATS_VERSION` of `5.1.0.0` that was never bumped,
  so `[2] > [5, 1, 0, 0]` was always false. Its tag filter also required tags to start with `5.1.`
  while the actual tags are `v5.1.x`. Tag parsing now accepts a leading `v`, filters by Blender
  series, sorts newest-first, prefers the attached `.zip` asset over the source zipball, and
  compares zero-padded version tuples. `CATS_VERSION` now tracks the manifest, and `dev_branch` is
  off for release builds so the version no longer reports itself as `-dev`.

### Tested

Tested on Blender 5.1.2 with single- and multi-armature models, including a body-plus-clothing
model with three armatures. The other main tools (Fix Model, Join Meshes, Separate, Merge Weights,
Twist Bones, Shape Key tools, Combine Materials, Visemes, Translate, Remove Doubles) were re-checked
after the changes.

Undo after Apply as Rest Pose has not been tested. Save your file before using it.
