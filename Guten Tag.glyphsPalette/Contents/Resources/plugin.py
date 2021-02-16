# Guten Tag
# =========
#
# Copyright 2021 Florian Pircher
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict
import objc
from AppKit import (
    NSAffineTransform,
    NSBezierPath,
    NSBundle,
    NSColor,
    NSControlStateValueMixed,
    NSControlStateValueOn,
    NSFont,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
    NSImage,
    NSMakePoint,
    NSMakeRect,
    NSMakeSize,
    NSMenu,
    NSMenuItem,
    NSMutableAttributedString,
    NSMutableCharacterSet,
    NSTokenField,
)
from GlyphsApp import (Glyphs, UPDATEINTERFACE)
from GlyphsApp.plugins import PalettePlugin


class UserDefaults:
    prefix = ""

    def __init__(self, prefix):
        self.prefix = prefix

    def id(x):
        return x

    def key(self, key):
        return self.prefix + key

    def read(self, key, default, transform=None):
        if not transform:
            transform = UserDefaults

        if value := Glyphs.defaults[self.key(key)]:
            return transform(value)
        else:
            return default


class GutenTag(PalettePlugin):
    dialogName = "net.addpixel.GutenTag"
    dialog = objc.IBOutlet()
    tokenField = objc.IBOutlet()

    userDefaults = UserDefaults(prefix="net.addpixel.GutenTag.")
    tagPool = []
    menu = None

    # strings localized in `settings`
    noTagsPlaceholder = 'no tags'
    showGlyphsWithTagLabel = 'Show Glyphs With Tag'
    multipleSelectionPlaceholder = 'Multiple Selection'

    # MARK: - Glyph Palette Plugin Methods

    @objc.python_method
    def settings(self):
        mainBundle = NSBundle.mainBundle()

        self.name = mainBundle.localizedStringForKey_value_table_("Tags", "Tags", None)
        self.noTagsPlaceholder = Glyphs.localize({
            'ar': 'بدون علامات',
            'cs': 'žádné značky',
            'de': 'keine Tags',
            'en': 'no tags',
            'es': 'sin etiquetas',
            'fr': 'pas de balises',
            'it': 'nessun tag',
            'ja': 'タグなし',
            'ko': '태그 없음',
            'pt': 'sem etiquetas',
            'ru': 'без тегов',
            'tr': 'etiket yok',
            'zh-Hans': '没有标签',
            'zh-Hant': '没有標籤',
        })
        self.multipleSelectionPlaceholder = mainBundle.localizedStringForKey_value_table_(
            "Multiple Selection", "Multiple Selection", None)
        self.showGlyphsWithTagLabel = Glyphs.localize({  # match Glyphs KerningPanel.strings "aGI-5I-k6x.title" key
            'ar': 'عرض كل المحارف',
            'cs': 'Zobrazit všechny glyfy',
            'de': 'Alle Glyphen anzeigen',
            'en': 'Show All Glyphs',
            'es': 'Mostrar todos los glifos',
            'fr': 'Afficher tous les glyphes',
            'it': 'Mostra tutti i glifi',
            'ja': 'すべてのグリフを表示',
            'ko': '모든 글리프 보기',
            'pt': 'Exibir Todos os Glifos',
            'ru': 'Показать все глифы',
            'tr': 'Tüm Glifleri Göster',
            'zh-Hans': '显示全部字符形',
            'zh-Hant': '顯示所有字符',
        })
        self.loadNib('IBdialog', __file__)

    @objc.python_method
    def start(self):
        # setup token field
        self.tokenField.controller = self
        self.tokenField.setEnabled_(False)
        self.tokenField.setDelegate_(self)

        # tokenizing character set
        charSet = NSMutableCharacterSet.new()
        defaultCharSet = NSTokenField.defaultTokenizingCharacterSet()
        charSet.formUnionWithCharacterSet_(defaultCharSet)
        charSet.addCharactersInString_("\n")
        self.tokenField.setTokenizingCharacterSet_(charSet)

        # font
        fontSize = NSFont.smallSystemFontSize()
        font = NSFont.legibileFontOfSize_(fontSize)
        self.tokenField.setFont_(font)

        # Adding a callback for the 'GSUpdateInterface' event
        Glyphs.addCallback(self.update, UPDATEINTERFACE)

    @objc.python_method
    def update(self, sender):
        """
        Updates the value of the token field to reflect the new glyph selection.
        """

        if glyphs := self.selectedGlyphs():
            self.tokenField.setPlaceholderString_(self.noTagsPlaceholder)
            self.tokenField.setEnabled_(True)

            if len(glyphs) == 1:
                # a single glyph is selected
                glyph = glyphs[0]
                self.setTagsValue(glyph.tags)
            else:
                # multiple glyphs are selected
                glyphsIter = iter(glyphs)
                firstTags = next(glyphsIter).tags
                sameTagsForAllSelectedGlyphs = True

                for glyph in glyphsIter:
                    if glyph.tags != firstTags:
                        sameTagsForAllSelectedGlyphs = False
                        break

                if sameTagsForAllSelectedGlyphs:
                    self.setTagsValue(firstTags)
                else:
                    self.tokenField.setPlaceholderString_(
                        self.multipleSelectionPlaceholder)
                    self.setTagsValue([])
        else:
            # no glyphs are selected
            self.tokenField.setPlaceholderString_('')
            self.tokenField.setEnabled_(False)
            self.setTagsValue([])

    @objc.python_method
    def __del__(self):
        Glyphs.removeCallback(self.update)

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__

    # MARK: - Utility Functions

    @objc.python_method
    def fontTags(font):
        """Returns a frozen set of all tags from all glyphs in the given font."""
        tags = set()

        for glyph in font.glyphs:
            tags.update(glyph.tags)

        return tags

    # MARK: - Instance Methods

    @objc.python_method
    def currentFont(self):
        """Returns the current font, if any, None otherwise."""
        if (wc := self.windowController()) and (font := wc.document().font):
            return font

    @objc.python_method
    def selectedGlyphs(self):
        """Returns all selected glyphs, both in edit view and in font view."""
        if font := self.currentFont():
            glyphs = []

            if font.currentTab:
                for layer in font.selectedLayers:
                    glyphs.append(layer.parent)
            else:
                try:
                    for glyph in font.selection:
                        glyphs.append(glyph)
                except:
                    pass

            return glyphs
        else:
            return []

    @objc.python_method
    def reloadTagPool(self):
        """Loads all tags of the font into the tag pool."""
        if font := self.currentFont():
            self.tagPool = GutenTag.fontTags(font)
        else:
            self.tagPool = []

    @objc.python_method
    def setTagsValue(self, tags):
        """Sets the value of the token filed to the given tags."""
        tags = sorted(set(tags))
        self.tokenField.setStringValue_(','.join(tags))

    @objc.IBAction
    def confirmTagsValue_(self, sender):
        """Confirms the entered tags and sets them on the selected glyphs."""
        tags = self.tokenField.objectValue()
        glyphs = self.selectedGlyphs()

        for glyph in glyphs:
            glyph.setTags_(tags)

    @objc.python_method
    def commit(self):
        """Confirm current value and resign as first responder."""
        self.confirmTagsValue_(None)

        # resign as first responder
        if wc := self.windowController():
            wc.window().makeFirstResponder_(None)

    @objc.IBAction
    def openGlyph_(self, sender):
        """Opens the glyph (`representedObject`) of the sender."""
        if font := self.currentFont():
            if font.currentTab:
                glyph = sender.representedObject()
                view = self.windowController().graphicView()
                view.replaceActiveLayersWithGlyphs_([glyph])
            else:
                font.newTab('/' + sender.representedObject().name)

    @objc.IBAction
    def showGlyphsForTag_(self, sender):
        """
        Opens a new tag with all glyphs that have a specific tag.

        The tag name is specified by the `representedObject` of the sender.
        """
        if font := self.currentFont():
            tag = sender.representedObject()
            newTabText = ""
            for glyph in font.glyphs:
                if tag in glyph.tags:
                    newTabText += "/" + glyph.name
            font.newTab(newTabText)

    # MARK: - NSTokenFieldDelegate

    def tokenField_displayStringForRepresentedObject_(self, tokenField, tag):
        # the trailing spaces make space for the menu disclose button
        # \u200C prevents whitespace trimming
        # \u2068 and \u2069 embed the tag name such that the spaces are always to the right of the tag name (needed if the tag name displays as right-to-left text)
        return '\u2068' + tag + '\u2069   \u200C'

    def tokenField_editingStringForRepresentedObject_(self, tokenField, tag):
        return tag

    def tokenField_hasMenuForRepresentedObject_(self, tokenField, tag):
        return True

    def tokenField_menuForRepresentedObject_(self, tokenField, tag):
        # apply tags to selection
        self.confirmTagsValue_(None)

        # add a menu with each glyph that has `tag` as a tag
        self.menu = NSMenu.new()

        if font := self.currentFont():
            master = font.selectedFontMaster
            selectedGlyphs = set(self.selectedGlyphs())

            # menu item layout setup
            upm = font.upm
            viewSize = self.userDefaults.read('GlyphPreviewSize', 56, transform=int)  # pt
            margin = self.userDefaults.read('GlyphPreviewInset', 6, transform=int)  # pt
            fontSize = viewSize - 2 * margin
            offset = upm / (fontSize / margin)
            # view bounds
            rect = NSMakeRect(0, 0, viewSize, viewSize)
            size = rect.size
            roundingRadius = 3  # pt
            roundedRect = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(rect, roundingRadius, roundingRadius)
            # clip for layer color if glyph has a color
            layerClipRect = NSMakeRect(viewSize / 2, 0, viewSize / 2, viewSize)
            layerClipPath = NSBezierPath.bezierPathWithRect_(layerClipRect)
            # clip for layer color if glyph has no color
            cornerSize = viewSize / 5
            layerOnlyClipPath = NSBezierPath.bezierPath()
            layerOnlyClipPath.moveToPoint_(NSMakePoint(cornerSize, viewSize))
            layerOnlyClipPath.lineToPoint_(NSMakePoint(viewSize, viewSize))
            layerOnlyClipPath.lineToPoint_(NSMakePoint(viewSize, 0))
            layerOnlyClipPath.lineToPoint_(NSMakePoint(0, 0))
            layerOnlyClipPath.lineToPoint_(NSMakePoint(0, viewSize - cornerSize))
            layerOnlyClipPath.closePath()
            # clip for glyph color if layer has a color
            glyphClipRect = NSMakeRect(0, 0, viewSize / 2, viewSize)
            glyphClipPath = NSBezierPath.bezierPathWithRect_(glyphClipRect)

            # menu item font setup
            menuItemFontSize = NSFont.systemFontSize()
            menuItemFont = NSFont.legibileFontOfSize_(menuItemFontSize)

            # show all glyphs menu item
            showGlyphsItem = NSMenuItem.new()
            showGlyphsItem.setTitle_(self.showGlyphsWithTagLabel)
            showGlyphsItem.setRepresentedObject_(tag)
            showGlyphsItem.setTarget_(self)
            showGlyphsItem.setAction_(self.showGlyphsForTag_)
            self.menu.addItem_(showGlyphsItem)

            self.menu.addItem_(NSMenuItem.separatorItem())

            matchingGlyphs = [x for x in font.glyphs if tag in x.tags]

            maximumPreviewGlyphCount = self.userDefaults.read('MaximumGlyphPreviewCount', 1536, transform=int)

            if maximumPreviewGlyphCount != -1:
                previewGlyphs = matchingGlyphs[0:maximumPreviewGlyphCount]
            else:
                previewGlyphs = matchingGlyphs

            def makeManuItem(glyph):
                isSelected = glyph in selectedGlyphs

                # draw thumbnail image
                layer = glyph.layers[master.id]
                path = layer.completeBezierPath
                image = NSImage.alloc().initWithSize_(size)
                image.lockFocus()

                if color := glyph.colorObject:
                    color.colorWithAlphaComponent_(0.6).set()
                    if layer.color:
                        glyphClipPath.setClip()
                    roundedRect.fill()

                if color := layer.colorObject:
                    if glyph.color:
                        layerClipPath.setClip()
                    else:
                        layerOnlyClipPath.setClip()

                    color.colorWithAlphaComponent_(0.6).set()
                    roundedRect.fill()

                transform = NSAffineTransform.transform()
                transform.scaleBy_(fontSize / upm)
                transform.translateXBy_yBy_(
                    (upm - layer.width) / 2 + offset, -master.descender + offset)
                path.transformUsingAffineTransform_(transform)

                NSColor.textColor().set()
                roundedRect.setClip()
                path.fill()

                image.unlockFocus()

                # menu item label
                attributedTitle = NSMutableAttributedString.alloc().initWithString_attributes_(glyph.name, {
                    NSFontAttributeName: menuItemFont
                })
                unicodesString = ', '.join(glyph.unicodes) if glyph.unicodes else '—'
                unicodesAttrString = NSMutableAttributedString.alloc().initWithString_attributes_(
                    '\n' + unicodesString,
                    {
                        NSFontAttributeName: menuItemFont.fontWithSize_(NSFont.smallSystemFontSize()),
                        NSForegroundColorAttributeName: NSColor.secondaryLabelColor()
                    }
                )
                attributedTitle.appendAttributedString_(unicodesAttrString)

                # create menu item
                item = NSMenuItem.new()
                item.setTitle_(glyph.name)
                item.setAttributedTitle_(attributedTitle)
                item.setImage_(image)
                item.setFont_(menuItemFont)
                item.setTarget_(self)
                item.setAction_(self.openGlyph_)
                item.setRepresentedObject_(glyph)

                if isSelected:
                    if len(selectedGlyphs) == 1:
                        item.setState_(NSControlStateValueOn)
                    else:
                        item.setState_(NSControlStateValueMixed)

                return item

            menuItems = [makeManuItem(x) for x in previewGlyphs]

            for item in menuItems:
                self.menu.addItem_(item)

        return self.menu

    def tokenField_completionsForSubstring_indexOfToken_indexOfSelectedItem_(
            self, tokenField, substring, tokenIndex, selectedIndex):
        query = str(substring)
        matches = []

        setTags = tokenField.objectValue()
        # hide tags that are already set (part of `tokenField.objectValue`) except if the tag equals the query (`substring`)
        availableTags = [tag for tag in self.tagPool if tag == substring or not tag in setTags]

        for tag in availableTags:
            if str(tag).startswith(query):
                matches.append(tag)

        if matches:
            return (matches, 0)
        else:
            return ([], -1)

    def tokenField_readFromPasteboard_(self, tokenField, pboard):
        # pasted text will be inserted varbatim and tokenized by the usual methods
        return []

    def tokenField_writeRepresentedObjects_toPasteboard_(self, tokenField, objects, pboard):
        pboard.clearContents()
        pboard.writeObjects_(objects)
        return True

    def tokenField_shouldAddObjects_atIndex_(self, tokenField, objects, index):
        # prevent adding duplicates values
        table = defaultdict(int)
        # the tags of `objects` are included in `valueTags`
        valueTags = tokenField.objectValue()

        # count the number of occurences for each value tag
        for tag in valueTags:
            table[tag] += 1

        # filter to-add tags such that no multiple-occurences tags are returned
        return [x for x in objects if table[x] <= 1]

    # MARK: - NSControlTextEditingDelegate

    def control_textView_doCommandBySelector_(self, control, textView, commandSelector):
        if control == self.tokenField:
            if commandSelector == 'cancel:':
                self.commit()
                return True
        return False


class GutenTagTokenField(NSTokenField):
    controller = None

    def intrinsicContentSize(self):
        intrinsicContentSize = super().intrinsicContentSize()
        width = intrinsicContentSize.width
        frame = self.frame()
        frame.size.height = 0xFFFF
        height = self.cell().cellSizeForBounds_(frame).height
        return NSMakeSize(width, height)

    def textDidBeginEditing_(self, notification):
        super().textDidBeginEditing_(notification)
        self.controller.reloadTagPool()

    def textDidChange_(self, notification):
        super().textDidChange_(notification)
        self.invalidateIntrinsicContentSize()

    def textShouldEndEditing_(self, notification):
        result = super().textShouldEndEditing_(notification)
        self.controller.confirmTagsValue_(self)
        return result
