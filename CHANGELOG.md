# Changelog

## 5.1.2

Bug-fix release on top of 5.1.1. No new features; nothing was removed.

### Apply as Rest Pose

On many models the button reported *"Pose successfully applied as rest pose"* and changed
nothing. There were several independent causes:

- Cats only applied the pose to the armature picked in its own dropdown. On models where the
  clothing rides a second armature, the pose is often made on that second armature, so an empty
  pose was applied and reported as success. It now falls back to whichever armature is actually
  posed and says which one it used. If the selected armature is posed, only that one is changed,
  and any other posed armature is named in the report but left alone.
- "No bones are posed" is now a warning instead of a success message.
- Meshes bound by an Armature modifier without being parented were skipped. The mesh lookup only
  walked object parenting, so glTF/VRM/FBX imports and manually re-linked meshes were left
  un-baked while the rest pose still changed.
- Meshes hidden with `hide_viewport` (the monitor icon), or inside a collection hidden the same
  way, were skipped. Those objects are dropped from the depsgraph, so `evaluated_get()` returned
  undeformed geometry and the bake wrote the mesh back onto itself. They are now enabled for the
  bake and restored afterwards.
- Mesh data shared between objects is now copied first. Baking it in place used to move every
  other user of that mesh.
- Meshes in an excluded collection are named in the report instead of being dropped. They are not
  included automatically, because un-excluding a layer collection resets the per-object hide state
  inside it and cannot be restored reliably.
- `pose.armature_apply` is no longer called through a bare context override. Blender picks the
  armatures to operate on from the view layer's real active object, so overriding only
  `active_object` did nothing whenever a different object was active. The armature is now made
  active first, and if the rest pose did not change, that is reported as an error.
- The operator reports which armature it used, how many bones and meshes it changed, and the name
  of anything skipped.

### Other fixes

- Apply All Transforms crashed with `Object '<name>' cannot be selected because it is not in
  View Layer` on files containing objects that sit in no collection (leftovers from deleted
  collections, appended data, backup collections). `select`, `hide`, `set_active` and `is_hidden`
  now skip such objects with a console note instead of raising mid-operation and leaving the model
  half-processed.
- `stop_pose_mode` and `start_pose_mode` no longer abort their caller. They assumed Pose mode and
  a 3D View context, and `pose.rot_clear` / `object.hide_view_clear` raised "context is incorrect"
  otherwise, after the model had already been changed. Pose clearing now falls back to the data
  API when the operators cannot run.
- `get_meshes_objects(visible_only=True)` skipped every other mesh, because it removed items from
  the list it was iterating.
- `get_meshes_objects(check=True)` no longer passes objects outside the view layer to the "delete
  corrupted mesh" path.
- The shape-key bake no longer reuses a cached evaluated object across depsgraph updates, which
  could return stale mesh data, and it stops instead of writing bad data if the evaluated mesh has
  a different vertex count.
- Certificate verification is no longer disabled. The updater set
  `ssl._create_default_https_context = ssl._create_unverified_context`, which turns off TLS
  verification for every HTTPS request made by the Blender process, not just its own.
- The updater now checks this fork's releases. It previously checked a Team Neoneko host, so it
  could offer to replace this build with an unrelated one.
- The updater could never detect an update. It compared the release tag with the prefix stripped
  (`5.1.2` became `2`) against a hard-coded `CATS_VERSION` of `5.1.0.0` that was never bumped, so
  `[2] > [5, 1, 0, 0]` was always false. Its tag filter also required tags to start with `5.1.`
  while the actual tags are `v5.1.x`. Tag parsing now accepts a leading `v`, filters by Blender
  series, sorts newest first, prefers the attached `.zip` asset over the source zipball, and
  compares zero-padded version tuples. `CATS_VERSION` now matches the manifest, and `dev_branch`
  is off for release builds, so the version no longer shows as `-dev`.

### Known issues

Undo after Apply as Rest Pose has not been checked. Save your file before using it.
