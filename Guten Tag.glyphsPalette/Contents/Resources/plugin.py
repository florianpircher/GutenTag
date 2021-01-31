import objc
from AppKit import (
    NSBundle,
    NSFont,
    NSMakeSize,
    NSMenu,
    NSMenuItem,
    NSMutableCharacterSet,
    NSMutableOrderedSet,
    NSTokenField
)
from GlyphsApp import *
from GlyphsApp.plugins import *


class GutenTagTokenField(NSTokenField):
    controller = None

    def intrinsicContentSize(self):
        intrinsicContentSize = super().intrinsicContentSize()
        width = intrinsicContentSize.width
        frame = self.frame()
        frame.size.height = 0xFFFF
        height = self.cell().cellSizeForBounds_(frame).height
        return NSMakeSize(width, height)

    def textDidChange_(self, notification):
        super().textDidChange_(notification)
        self.invalidateIntrinsicContentSize()

    def textDidEndEditing_(self, notification):
        super().textDidEndEditing_(notification)
        self.controller.confirmTagsValue_(self)


class GutenTag(PalettePlugin):
    dialogName = "net.addpixel.GutenTag"
    dialog = objc.IBOutlet()
    tokenField = objc.IBOutlet()
    tokenFieldDelegate = None
    noTagsPlaceholder = 'no tags'  # localized in `settings`
    multipleSelectionPlaceholder = 'Multiple Selection'  # localized in `settings`

    @objc.python_method
    def settings(self):
        mainBundle = NSBundle.mainBundle()

        self.name = mainBundle.localizedStringForKey_value_table_(
            "Tags", "Tags", None)
        self.noTagsPlaceholder = Glyphs.localize({
            'ar': 'بدون علامات',
            'ca': 'sense etiquetes',
            'cs': 'žádné značky',
            'da': 'ingen tags',
            'de': 'keine Tags',
            'el': 'δεν ετικέτες',
            'en': 'no tags',
            'es': 'sin etiquetas',
            'fi': 'ei tunnisteita',
            'fr': 'pas de balises',
            'he': 'אין תגים',
            'hr': 'nema tagova',
            'hu': 'nincsenek címkék',
            'it': 'nessun tag',
            'ja': 'タグなし',
            'ko': '태그 없음',
            'nl': 'geen tags',
            'no': 'ingen tags',
            'pl': 'bez znaczników',
            'pt': 'sem etiquetas',
            'ro': 'fără etichete',
            'ru': 'без тегов',
            'sk': 'bez značiek',
            'sv': 'inga taggar',
            'th': 'ไม่มีแท็ก',
            'tr': 'etiket yok',
            'uk': 'відсутні теги',
            'zh-Hans': '没有标签',
        })
        self.multipleSelectionPlaceholder = mainBundle.localizedStringForKey_value_table_(
            "Multiple Selection", "Multiple Selection", None)
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

        # tokenizing character set
        tokenizingCharacterSet = NSMutableCharacterSet.new()
        tokenizingCharacterSet.formUnionWithCharacterSet_(
            NSTokenField.defaultTokenizingCharacterSet())
        tokenizingCharacterSet.addCharactersInString_(" ")  # space
        self.tokenField.setTokenizingCharacterSet_(tokenizingCharacterSet)

        # font
        fontSize = NSFont.smallSystemFontSize()
        font = NSFont.legibileFontOfSize_(fontSize)
        self.tokenField.setFont_(font)

        # Adding a callback for the 'GSUpdateInterface' event
        Glyphs.addCallback(self.update, UPDATEINTERFACE)

    @objc.python_method
    def __del__(self):
        Glyphs.removeCallback(self.update)

    @objc.python_method
    def currentFont(self):
        """Returns the current font, if any, None otherwise."""
        windowController = self.windowController()
        if windowController:
            font = windowController.document().font
            if font:
                return font

    @objc.python_method
    def glyphTags(glyph):
        """Returns a frozen set of the tags from the given glyph."""
        return frozenset(glyph.tags().array())

    @objc.python_method
    def fontTags(font):
        """Returns a frozen set of all tags from all glyphs in the given font."""
        tags = NSMutableOrderedSet.new()

        for glyph in font.glyphs:
            tags.unionOrderedSet_(glyph.tags())

        return frozenset(tags.array())

    def selectedGlyphs(self):
        """Returns all selected glyphs, both in edit view and in font view."""
        font = self.currentFont()

        if not font:
            return []

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

    @objc.python_method
    def update(self, sender):
        """
        Updates the value of the token field to reflect the new glyph selection.
        """
        glyphs = self.selectedGlyphs()

        if glyphs:
            self.tokenField.setPlaceholderString_(self.noTagsPlaceholder)
            self.tokenField.setEnabled_(True)

            if len(glyphs) == 1:
                # a single glyph is selected
                glyph = glyphs[0]
                tags = GutenTag.glyphTags(glyph)
                self.setTagsValue(tags)
            else:
                # multiple glyphs are selected
                tagsValues = set()

                for glyph in glyphs:
                    tagsValues.add(GutenTag.glyphTags(glyph))

                if len(tagsValues) == 1:
                    # all tags are the same for all glyphs
                    tags = next(iter(tagsValues))
                    self.setTagsValue(tags)
                else:
                    # tags differ from glyph to glyph
                    self.tokenField.setPlaceholderString_(
                        self.multipleSelectionPlaceholder)
                    self.setTagsValue([])
        else:
            # no glyphs are selected
            self.tokenField.setPlaceholderString_('')
            self.tokenField.setEnabled_(False)
            self.setTagsValue([])

    @objc.python_method
    def setTagsValue(self, tags):
        """Sets the value of the token filed to the given tags."""
        tags = list(tags)
        tags.sort()
        self.tokenField.setStringValue_(','.join(tags))

    @objc.IBAction
    def confirmTagsValue_(self, sender):
        """Confirms the entered tags and sets them on the selected glyphs."""
        tags = []

        for token in self.tokenField.objectValue():
            tags.append(str(token))

        glyphs = self.selectedGlyphs()

        for glyph in glyphs:
            glyph.setTags_(tags)

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

        font = self.controller.currentFont()

        if font:
            menuItemFontSize = NSFont.systemFontSize()
            menuItemFont = NSFont.legibileFontOfSize_(menuItemFontSize)

            for glyph in font.glyphs:
                tags = GutenTag.glyphTags(glyph)

                if tagName in tags:
                    item = NSMenuItem.new()
                    item.setTitle_(glyph.name)
                    item.setFont_(menuItemFont)
                    menu.addItem_(item)

        return menu

    def tokenField_completionsForSubstring_indexOfToken_indexOfSelectedItem_(self, tokenField, substring, tokenIndex, selectedIndex):
        # filter from existing tags
        font = self.currentFont()

        if not font:
            return

        existingTags = GutenTag.fontTags(font)

        query = str(substring)
        matches = []

        for tag in existingTags:
            if str(tag).startswith(query):
                matches.append(tag)

        if matches:
            return (matches, 0)
        else:
            return ([], -1)

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__
