# <img src="https://formkunft.com/glyphs/plugins/guten-tag/icons/plugin/128.png" width="42" height="42" alt align="top"> Guten Tag

*Guten Tag* is a plugin for [Glyphs](https://glyphsapp.com).
It allows you to edit glyph tags from both Font View and Edit View.

[![](Screenshot.png)](https://xgc.io/b/glyphs/guten-tag/1.mp4)

- View and edit your tags from Font View and Edit View.
- Use autocompletion to prevent typos in tag names.
- Preview all glyphs for a tag by clicking the disclosure button next to the tag name.
- Assign, remove, and rename tags using keyboard shortcuts.

## Usage

- Navigate between related glyphs using the tag menu.
- Tokens allow using tags in OpenType feature code: `$[tags contains "narrow"]`.
- Predicate rules can filter for glyphs by tags, including *Smart Filters*, master metric scopes, stem scopes, hinting scopes, and guide scopes.

[Read the Guten Tag **Handbook** <img src="https://formkunft.com/glyphs/plugins/guten-tag/icons/handbook/48.png" width="16" height="23" alt align="top">](https://florianpircher.com/glyphs/plugins/guten-tag/Handbook.pdf) for more details on Guten Tag and tags in Glyphs.
## Installation

### Plugin Manager

<a href="https://florianpircher.com/glyphs/plugins/anchor-annotations/install"><img src="Assets/DownloadBadge.svg" alt="Download on the Plugin Manager" height="50"></a>

### Manual Installation

1. Download the [lastest release](https://github.com/florianpircher/GutenTag/releases/latest) from GitHub.
2. Double-click the **Guten Tag.glyphsPalette** file. Glyphs will launch and prompt you to confirm the installation.
3. Quit and relaunch Glyphs. Now you can access Guten Tag in the top right corner of your Glyphs window.

## Preferences

Guten Tag offers a range of configurable preferences.

### Glyph Preview Size

The `GutenTagGlyphPreviewSize` (type: double, default: `36`) preference defines the width and height of a glyph preview image in display points.
The value must be a positive number.

Run the following line in the Macro panel to set the size (or set the value to `None` to use the default size):

```python
Glyphs.defaults['GutenTagGlyphPreviewSize'] = 56
```

### Glyph Preview Inset

The `GutenTagGlyphPreviewInset` (type: double, default: `4`) preference controls the inset on all four edges from a glyph preview image in display points.
The font size of the glyph preview is as follows:

```
GutenTagGlyphPreviewSize - (2 * GutenTagGlyphPreviewInset)
```

Negatives values crop into the image.

Run the following line in the Macro panel to set the inset (or set the value to `None` to use the default inset):

```python
Glyphs.defaults['GutenTagGlyphPreviewInset'] = 6
```

### Maximum Glyph Preview Count

The `GutenTagMaximumGlyphPreviewCount` (type: long, default: `1000`) preference limits the number of glyph previews shown in the tag menu.
This preference is useful since creating glyph previews can be impossibly slow if there are many glyphs for a tag.
The default limit of 1000 should be fast enough in most cases.
Remove the limit by setting the value to a non-positive number (for example, `-1`).

Run the following line in the Macro panel to set the count (or set the value to `None` to use the default count):

```python
Glyphs.defaults['GutenTagMaximumGlyphPreviewCount'] = 200
```

## Licenses

Licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
