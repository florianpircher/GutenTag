# 🔖 Guten Tag

This is a plugin for the [Glyphs font editor](https://glyphsapp.com).
It allows you to edit glyph tags from both the font view *and* edit view.

[![](Screenshot.png)](https://xgc.io/b/glyphs/guten-tag/1.mp4)

## Features

- View and edit your tags from the font view and the edit view.
- Use autocompletion to prevent typos in your tag names.
- Preview all glyphs for a tag by clicking on the little disclosure button to the right of a tag.

## Why Use Tags?

- Tags allow you to easily navigate between related glyphs ([movie demonstration](https://xgc.io/b/glyphs/guten-tag/1.mp4)).
- Tags can be used in OpenType feature code as [tokens](https://glyphsapp.com/learn/tokens#g-glyph-class-predicates): `$[tags contains "narrow"]`.
- Glyph names no longer need a cryptic naming scheme to represent all relevant attributes of a glyph.

## Installation

### Manual Installation

1. Download the [lastest release](https://github.com/florianpircher/GutenTag/releases/latest) from GitHub.
2. Double-click the <img src="Icons/Icon-16x16%402x.png" width="16" height="16" alt> **Guten Tag.glyphsPalette** file. Glyphs will launch and prompt you to confirm the installation.
3. Quit and relaunch Glyphs. Now you can access Guten Tag in the top right corner of your Glyphs window.

## Preferences

Guten Tag offers the following configurable preferences:

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `GlyphPreviewSize` | `int` | `56` | The width and height of a glyph preview image in display points. Must be a positive value. |
| `GlyphPreviewInset` | `int` | `6` | The inset on all four edges of the glyph preview image in display points. The font size of the glyph preview is `GlyphPreviewSize - (2 * GlyphPreviewInset)`, i.e. the image height without the top and bottom insets. Negatives values crop into the image. |
| `MaximumGlyphPreviewCount` | `int` | `1000` | Limits the number of glyph previews shown in the tag menu. This is useful since creating glyph previews can be impossibly slow if there are many glyphs for a tag. The limit can be lifted by setting the value to `-1`. |

Each key is prefixed by `com.FlorianPircher.GutenTag.` (for example `GlyphPreviewSize` is addressed as `com.FlorianPircher.GutenTag.GlyphPreviewSize`).

<details>
<summary>Set Preferences from the Command Line</summary>

Run the following line with `$KEY`, `$TYPE`, and `$VALUE` substituted.

```
defaults write com.GeorgSeifert.Glyphs3 com.FlorianPircher.GutenTag.$KEY -$TYPE $VALUE
```

For example, to set the `GlyphPreviewSize` to `100`:

```
defaults write com.GeorgSeifert.Glyphs3 com.FlorianPircher.GutenTag.GlyphPreviewSize -int 100
```
</details>

<details>
<summary>Set Preferences from Glyphs’s Macro Panel</summary>

Run the following line with `$KEY` and `$VALUE` substituted.

```
Glyphs.defaults['com.FlorianPircher.GutenTag.$KEY'] = $VALUE
```

For example, to set the `GlyphPreviewSize` to `100`:

```
Glyphs.defaults['com.FlorianPircher.GutenTag.GlyphPreviewSize'] = 100
```
</details>

<details>
<summary>Set Preferences using mekkablue’s scripts</summary>

Select *Script* → *mekkablue* → *App* → *Set Hidden App Preferences*. Enter the preference key (prefixed by `com.FlorianPircher.GutenTag.`) and the value and confirm with *Apply*.
</details>

## Licenses

Plugin source code licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

Plugin icons licensed under [Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

Plugin runner (`MacOS/Guten Tag`) copyright Georg Seifert (@schriftgestalt), Jan Gerner (@yanone), and Rainer Erich Scheichelbauer (@mekkablue); licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
