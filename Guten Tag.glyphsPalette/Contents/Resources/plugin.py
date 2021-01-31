import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from AppKit import NSFont, NSMakeSize, NSMenu, NSMenuItem, NSMutableCharacterSet, NSMutableOrderedSet, NSTokenField


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


class GutenTagTokenFieldDelegate(NSObject):
    controller = None

    def tokenField_displayStringForRepresentedObject_(self, tokenField, representedObject):
        # the trailing spaces make space for the menu disclose button
        # \u200C prevents whitespace trimming
        return '\u2068' + representedObject + '\u2069   \u200C'

    def tokenField_editingStringForRepresentedObject_(self, tokenField, representedObject):
        return representedObject

    def tokenField_hasMenuForRepresentedObject_(self, tokenField, representedObject):
        return True

    def tokenField_menuForRepresentedObject_(self, tokenField, representedObject):
        # add a menu with each glyph that has `representedObject` as a tag
        menu = NSMenu.new()

        font = self.controller.currentFont()

        if font:
            for glyph in font.glyphs:
                tags = GutenTag.glyphTags(glyph)

                if representedObject in tags:
                    item = NSMenuItem.new()
                    item.setTitle_(glyph.name)
                    # set menu item font
                    fontSize = NSFont.systemFontSize()
                    font = NSFont.legibileFontOfSize_(fontSize)
                    item.setFont_(font)
                    # add item
                    menu.addItem_(item)

        return menu

    # # crashes Glyphs no matter the return value:
    # def tokenField_completionsForSubstring_indexOfToken_indexOfSelectedItem_(self, tokenField, substring, tokenIndex, selectedIndex):
    #   # filter from existing tags
    #   return []


class GutenTag(PalettePlugin):
    dialogName = "net.addpixel.GutenTag"
    dialog = objc.IBOutlet()
    tokenField = objc.IBOutlet()
    tokenFieldDelegate = None
    noTagsPlaceholder = 'no tags'  # localized in `settings`
    multipleSelectionPlaceholder = 'Multiple Selection'  # localized in `settings`

    @objc.python_method
    def settings(self):
        self.name = Glyphs.localize({
            'ar': 'العلامات',
            'ca': 'Etiquetes',
            'cs': 'Značky',
            'da': 'Tags',
            'de': 'Tags',
            'el': 'Ετικέτες',
            'en': 'Tags',
            'es': 'Etiquetas',
            'fi': 'Tageja',
            'fr': 'Badges',
            'he': 'תגים',
            'hr': 'Tagova',
            'hu': 'Címkék',
            'it': 'Tags',
            'ja': 'タグ',
            'ko': '태그',
            'nl': 'Tags',
            'no': 'Tags',
            'pl': 'Znaczniki',
            'pt': 'Etiquetas',
            'ro': 'Etichete',
            'ru': 'Tags',
            'sk': 'Značky',
            'sv': 'Taggar',
            'th': 'แท็ก',
            'tr': 'Etiketler',
            'uk': 'Теги',
            'zh-Hans': '标签',
        })
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
        self.multipleSelectionPlaceholder = Glyphs.localize({
            'ar': 'تحديد متعدد',
            'cs': 'Vícenásobný výběr',
            'de': 'Mehrere Werte',
            'en': 'Multiple Selection',
            'es': 'Valores múltiples',
            'fr': 'Sélections multiples',
            'it': 'Selezione multipla',
            'ja': '複数選択',
            'ko': '다중 선택',
            'pt': 'Seleção múltipla',
            'ru': 'Множественное выделение',
            'tr': 'Çoklu Seçim',
            'zh-Hans': '多选',
            'zh-Hant': '多選',
        })
        self.loadNib('IBdialog', __file__)

    @objc.python_method
    def start(self):
        # setup token field
        self.tokenField.controller = self
        self.tokenField.setEnabled_(False)

        # set delegate
        self.tokenFieldDelegate = GutenTagTokenFieldDelegate.new()
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

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__
