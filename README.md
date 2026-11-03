# Cats Blender Plugin

A tool designed to shorten the steps needed to import and optimize models into VRChat.

> **This is an unofficial fork of a fork**, maintained for Blender 5.1 compatibility. It is not
> associated with the original Cats project, Team Neoneko, or akadon. Do not ask for support in the
> original Cats Discord.

> **5.1.2 fixes "Apply as Rest Pose does nothing".** On models with more than one armature (the
> usual body-plus-clothing setup), Cats only ever applied the pose to the armature selected in its
> own dropdown, so a pose made on any other armature was reported as applied while nothing changed.
> Several other silent skips are fixed too (meshes bound by modifier rather than parenting, meshes
> hidden with the monitor icon, shared mesh data). See [CHANGELOG.md](CHANGELOG.md).

---

## Features

- **Import:** MMD, XNALara, Mixamo, Source Engine, Unreal Engine, DAZ/Poser, Blender Rigify, Sims 2, Motion Builder, 3DS Max and more
- **Optimization:** Material combining, texture atlasing, bone merging
- **Eye Tracking:** SDK3 and Legacy eye tracking setup
- **Visemes:** Automatic lip sync configuration
- **Armature Tools:** Merge armatures, attach meshes, custom bone naming
- **Translation:** Convert Japanese bone/mesh names to English

## Requirements

- **Blender 5.1+**
- Windows: use the official installer from [blender.org](https://www.blender.org/download/) — Windows Store, Snap, and Flatpak versions are not supported

### Optional

- [Material Combiner](https://github.com/Grim-es/material-combiner-addon/) — texture atlasing
- [Immersive Scaler](https://github.com/triazo/immersive_scaler) — scaling tools

## Installation

1. Download the latest `.zip` from [Releases](https://github.com/alienware377/Cats-Blender-Plugin-5.1-fixes/releases)
2. In Blender: **Edit → Preferences → Extensions → Install from Disk**
3. Select the zip (do not extract it)
4. Enable the extension and restart Blender

## Credits

Originally created by [absolute-quantum](https://github.com/absolute-quantum/cats-blender-plugin).
Previously maintained by [Team Neoneko](https://github.com/teamneoneko/Cats-Blender-Plugin-Unofficial-).
Blender 5.1 port by [akadon](https://github.com/akadon/Cats-Blender-Plugin); this fork adds the
5.1.2 bug fixes listed in the changelog.

Licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).

Bundled libraries: [MMD Tools](https://github.com/UuuNyaa/blender_mmd_tools), [Material Combiner](https://github.com/Grim-es/material-combiner-addon), [Immersive Scaler](https://github.com/triazo/immersive_scaler)
