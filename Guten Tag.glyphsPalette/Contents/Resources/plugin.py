import objc
from AppKit import (
    NSAffineTransform,
    NSBundle,
    NSFont,
    NSImage,
    NSMakeSize,
    NSMenu,
    NSMenuItem,
    NSMutableOrderedSet,
    NSTokenField,
    NSColor,
    NSMakeRect,
    NSBezierPath,
)
from GlyphsApp import *
from GlyphsApp.plugins import *


class GutenTag(PalettePlugin):
    dialogName = "net.addpixel.GutenTag"
    dialog = objc.IBOutlet()
    tokenField = objc.IBOutlet()
    tokenFieldDelegate = None
    noTagsPlaceholder = 'no tags'  # localized in `settings`
    showGlyphsWithTagLabel = 'Show Glyphs With Tag'  # localized in `settings`
    multipleSelectionPlaceholder = 'Multiple Selection'  # localized in `settings`
    tagPool = []

    # MARK: - Glyph Palette Plugin Methods

    @objc.python_method
    def settings(self):
        mainBundle = NSBundle.mainBundle()

        self.name = mainBundle.localizedStringForKey_value_table_(
            "Tags", "Tags", None)
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
            'en': 'Show all Glyphs',
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

        # set delegate
        self.tokenFieldDelegate = self
        self.tokenFieldDelegate.controller = self
        self.tokenField.setDelegate_(self.tokenFieldDelegate)

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
                self.setTagsValue(glyph.tags())
            else:
                # multiple glyphs are selected
                glyphsIter = iter(glyphs)
                firstTags = next(glyphsIter).tags()
                sameTagsForAllSelectedGlyphs = True

                for glyph in glyphsIter:
                    if glyph.tags() != firstTags:
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
    def containsTag(tag, tags):
        """Returns whether a set of tags contains the given tag."""
        try:
            return tag in tags
        except:
            return tags.containsObject_(tag)

    @objc.python_method
    def tagsIter(tags):
        """Returns an iterable over the given tags."""
        try:
            return iter(tags)
        except:
            return tags.set()  # fast, cheap proxy

    @objc.python_method
    def fontTags(font):
        """Returns a frozen set of all tags from all glyphs in the given font."""
        tags = NSMutableOrderedSet.new()

        for glyph in font.glyphs:
            tags.unionOrderedSet_(glyph.tags())

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
        tags = sorted(set(GutenTag.tagsIter(tags)))
        self.tokenField.setStringValue_(','.join(tags))

    @objc.IBAction
    def confirmTagsValue_(self, sender):
        """Confirms the entered tags and sets them on the selected glyphs."""
        tags = self.tokenField.objectValue()
        glyphs = self.selectedGlyphs()

        for glyph in glyphs:
            glyph.setTags_(tags)

    @objc.IBAction
    def openGlyph_(self, sender):
        """Opens the glyphs named by the title of the sender."""
        if font := self.currentFont():
            if font.currentTab:
                glyph = font.glyphs[sender.title()]
                view = self.windowController().graphicView()
                view.replaceActiveLayersWithGlyphs_([glyph])
            else:
                font.newTab('/' + sender.title())

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
                if GutenTag.containsTag(tag, glyph.tags()):
                    newTabText += "/" + glyph.name
            font.newTab(newTabText)

    # MARK: - NSTokenFieldDelegate

    def tokenField_displayStringForRepresentedObject_(self, tokenField, tagName):
        # the trailing spaces make space for the menu disclose button
        # \u200C prevents whitespace trimming
        # \u2068 and \u2069 embed the tag name such that the spaces are always to the right of the tag name (needed if the tag name displays as right-to-left text)
        return '\u2068' + tagName + '\u2069   \u200C'

    def tokenField_editingStringForRepresentedObject_(self, tokenField, tagName):
        return tagName

    def tokenField_hasMenuForRepresentedObject_(self, tokenField, tagName):
        return True

    def tokenField_menuForRepresentedObject_(self, tokenField, tagName):
        # add a menu with each glyph that has `tagName` as a tag
        menu = NSMenu.new()

        if font := self.controller.currentFont():
            master = font.selectedFontMaster

            # menu item layout setup
            upm = font.upm
            viewSize = 56  # pt
            margin = 6  # pt
            fontSize = viewSize - 2 * margin
            offset = upm / (fontSize / margin)
            # view bounds
            rect = NSMakeRect(0, 0, viewSize, viewSize)
            size = rect.size
            roundingRadius = 1  # pt
            roundedRect = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                rect, roundingRadius, roundingRadius)
            # layer clip is used to fill layer color if separate layer color
            layerClipRect = NSMakeRect(viewSize / 2, 0, viewSize / 2, viewSize)
            layerClipPath = NSBezierPath.bezierPathWithRect_(layerClipRect)
            # glyph clip is used to fill glyph color if separate layer color
            glyphClipRect = NSMakeRect(0, 0, viewSize / 2, viewSize)
            glyphClipPath = NSBezierPath.bezierPathWithRect_(glyphClipRect)

            # menu item font setup
            menuItemFontSize = NSFont.systemFontSize()
            menuItemFont = NSFont.legibileFontOfSize_(menuItemFontSize)

            # show all glyphs menu item
            item = NSMenuItem.new()
            item.setTitle_(self.showGlyphsWithTagLabel)
            item.setRepresentedObject_(tagName)
            item.setTarget_(self)
            item.setAction_(self.showGlyphsForTag_)
            menu.addItem_(item)

            menu.addItem_(NSMenuItem.separatorItem())

            for glyph in font.glyphs:
                if GutenTag.containsTag(tagName, glyph.tags()):
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
                        color.colorWithAlphaComponent_(0.6).set()
                        layerClipPath.setClip()
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

                    item = NSMenuItem.new()
                    item.setTitle_(glyph.name)
                    item.setImage_(image)
                    item.setFont_(menuItemFont)
                    item.setTarget_(self)
                    item.setAction_(self.openGlyph_)
                    menu.addItem_(item)

        return menu

    def tokenField_completionsForSubstring_indexOfToken_indexOfSelectedItem_(self, tokenField, substring, tokenIndex, selectedIndex):
        if font := self.currentFont():
            query = str(substring)
            matches = []

            setTags = tokenField.objectValue()
            tagPool = GutenTag.tagsIter(self.tagPool)
            # hide tags that are already set (part of `tokenField.objectValue`) except if the tag equals the query (`substring`)
            availableTags = [
                tag for tag in tagPool if tag == substring or not GutenTag.containsTag(tag, setTags)]

            for tag in availableTags:
                if str(tag).startswith(query):
                    matches.append(tag)

            if matches:
                return (matches, 0)

        return ([], -1)


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
