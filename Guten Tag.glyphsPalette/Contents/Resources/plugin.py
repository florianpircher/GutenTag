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
    NSColor,
    NSControlStateValueMixed,
    NSControlStateValueOn,
    NSFont,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
    NSImage,
    NSImageOnly,
    NSMakePoint,
    NSMakeRect,
    NSMakeSize,
    NSMenu,
    NSMenuItem,
    NSModalResponseOK,
    NSModalResponseCancel,
    NSMutableAttributedString,
    NSMutableCharacterSet,
    NSTimer,
    NSTokenField,
    NSTokenStyleSquared,
)
from GlyphsApp import (Glyphs, UPDATEINTERFACE)
from GlyphsApp.plugins import PalettePlugin


# localization
TAGS_STRING = Glyphs.localize({
    "ar": "العلامات",
    "cs": "Značky",
    "de": "Tags",
    "en": "Tags",
    "es": "Etiquetas",
    "fr": "Badges",
    "it": "Tags",
    "ja": "タグ",
    "ko": "태그",
    "pt": "Etiquetas",
    "ru": "Меток",
    "tr": "Etiketler",
    "zh-Hans": "标签",
    "zh-Hant": "標籤",
})
MULTIPLE_VALUES_STRING = Glyphs.localize({
    "ar": "قيم متعددة",
    "cs": "Více hodnot",
    "de": "Mehrere Werte",
    "en": "Multiple Values",
    "es": "Valores múltiples",
    "fr": "Valeurs multiples",
    "it": "Valori Multipli",
    "ja": "複数値",
    "ko": "여러 값",
    "pt": "Seleção múltipla",  # TODO
    "ru": "Множественное выделение",  # TODO
    "tr": "Çoklu Değer",
    "zh-Hans": "多个值",
    "zh-Hant": "多選",  # TODO
})
NO_TAGS_STRING = Glyphs.localize({
    "ar": "بدون علامات",
    "cs": "žádné značky",
    "de": "keine Tags",
    "en": "no tags",
    "es": "sin etiquetas",
    "fr": "pas de balises",
    "it": "nessun tag",
    "ja": "タグなし",
    "ko": "태그 없음",
    "pt": "sem etiquetas",
    "ru": "без меток",
    "tr": "etiket yok",
    "zh-Hans": "没有标签",
    "zh-Hant": "没有標籤",
})
ADD_TAGS_TITLE_STRING = Glyphs.localize({
    "ar": "إضافة علامات إلى الصور الرمزية المحددة",
    "cs": "Přidat značky k vybraným glyfům",
    "en": "Add tags to the selected glyphs",
    "es": "Añadir etiquetas a los glifos seleccionados",
    "de": "Tags zu ausgewählten Glyphen hinzufügen",
    "fr": "Ajouter des badges aux glyphes sélectionnés",
    "it": "Aggiungi tag ai glifi selezionati",
    "ja": "選択したグリフにタグを追加します",
    "ko": "선택한 글리프에 태그 추가",
    "pt": "Adicionar etiquetas aos glifos selecionados",
    "ru": "Добавление меток для выбранных глифы",
    "tr": "Seçili glif’lere etiketler ekle",
    "zh-Hans": "为所选字形添加标签",
    "zh-Hant": "將標籤新增至所選字形",
})
ADD_TAGS_BUTTON_STRING = Glyphs.localize({
    "ar": "إضافة علامات",
    "cs": "Přidat značky",
    "en": "Add Tags",
    "es": "Añadir etiquetas",
    "de": "Tags hinzufügen",
    "fr": "Ajouter des badges",
    "it": "Aggiungi Tag",
    "ja": "タグを追加",
    "ko": "태그 추가",
    "pt": "Adicionar etiquetas",
    "ru": "Добавить",
    "tr": "Etiket ekle",
    "zh-Hans": "添加标签",
    "zh-Hant": "新增標籤",
})
REMOVE_TAGS_TITLE_STRING = Glyphs.localize({
    "ar": "إزالة العلامات من الصور الرمزية المحددة",
    "cs": "Odstranit značky z vybraných glyfů",
    "en": "Remove tags from the selected glyphs",
    "es": "Suprimir etiquetas de los glifos seleccionados",
    "de": "Tags von ausgewählten Glyphen entfernen",
    "fr": "Supprimer les badges des glyphes sélectionnés",
    "it": "Rimuovi i tag dai glifi selezionati",
    "ja": "選択したグリフからタグを削除します",
    "ko": "선택한 글리프에서 태그 제거",
    "pt": "Remover etiquetas dos glifos selecionados",
    "ru": "Удаление меток для выбранных глифы",
    "tr": "Seçili glif’lerin etiketlerini kaldır",
    "zh-Hans": "从所选字形删除标签",
    "zh-Hant": "移除所選字形的標籤",
})
REMOVE_TAGS_BUTTON_STRING = Glyphs.localize({
    "ar": "إزالة العلامات",
    "cs": "Odstranit značky",
    "en": "Remove Tags",
    "es": "Suprimir etiquetas",
    "de": "Tags entfernen",
    "fr": "Supprimer les badges",
    "it": "Rimuovi Tag",
    "ja": "タグを削除",
    "ko": "태그 제거",
    "pt": "Remover etiquetas",
    "ru": "Удалить",
    "tr": "Etiketleri kaldır",
    "zh-Hans": "移除标签",
    "zh-Hant": "移除標籤",
})
SHOW_ALL_GLYPHS_BUTTON_STRING = Glyphs.localize({
    "ar": "عرض كل المحارف",
    "cs": "Zobrazit všechny glyfy",
    "de": "Alle Glyphen anzeigen",
    "en": "Show All Glyphs",
    "es": "Mostrar todos los glifos",
    "it": "Mostra tutti i glifi",
    "fr": "Afficher tous les glyphes",
    "ja": "すべてのグリフを表示",
    "ko": "모든 글리프 보기",
    "pt": "Exibir Todos os Glifos",
    "ru": "Показать все глифы",
    "tr": "Tüm Glifleri Göster",
    "zh-Hans": "显示全部字符形",
    "zh-Hant": "顯示所有字符",
})


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


class UserInterfaceContext:
    accessFont = None

    def __init__(self, accessFont):
        self.accessFont = accessFont

    def __enter__(self):
        if font := self.accessFont():
            font.disableUpdateInterface()
            return font
        else:
            return None

    def __exit__(self, type, value, traceback):
        if font := self.accessFont():
            font.enableUpdateInterface()


class GutenTag(PalettePlugin):
    dialogName = "com.FlorianPircher.GutenTag"
    # Interface Builder Outlets
    dialog = objc.IBOutlet()
    tokenField = objc.IBOutlet()
    batchEditToolbar = objc.IBOutlet()
    addButton = objc.IBOutlet()
    removeButton = objc.IBOutlet()
    promptWindow = objc.IBOutlet()
    promptTitleLabel = objc.IBOutlet()
    promptTokenField = objc.IBOutlet()
    promptConfirmButton = objc.IBOutlet()
    promptCancelButton = objc.IBOutlet()
    renameWindow = objc.IBOutlet()
    renameTitleLabel = objc.IBOutlet()
    renameSearchField = objc.IBOutlet()
    renameReplaceField = objc.IBOutlet()
    renameConfirmButton = objc.IBOutlet()
    renameCancelButton = objc.IBOutlet()
    # Used to wrap code in `disableUpdateInterface` ... `enableUpdateInterface` calls.
    uiContext = None
    # Offers access to the systems user defaults API for values related to the plugin.
    userDefaults = UserDefaults(prefix="com.FlorianPircher.GutenTag.")
    # Tag names of the current font.
    # Needs to be reloaded by calling `reloadTagPool`.
    # This is a cached and thus fast access to `GutenTag.fontTags(self.currentFont())`.
    tagPool = []
    # Tag names used for token field suggestions.
    suggestionTagPool = []

    # MARK: - Glyph Palette Plugin Methods

    @objc.python_method
    def settings(self):
        self.uiContext = UserInterfaceContext(self.currentFont)

        self.name = TAGS_STRING
        self.loadNib("View", __file__)
        self.loadNib("Prompt", __file__)

    @objc.python_method
    def start(self):
        # tokenizing character set
        charSet = NSMutableCharacterSet.new()
        defaultCharSet = NSTokenField.defaultTokenizingCharacterSet()
        charSet.formUnionWithCharacterSet_(defaultCharSet)
        charSet.addCharactersInString_("\n")

        # font
        fontSize = NSFont.systemFontSize()
        font = NSFont.legibileFontOfSize_(fontSize)

        smallFontSize = NSFont.smallSystemFontSize()
        smallFont = NSFont.legibileFontOfSize_(smallFontSize)

        # token field
        self.tokenField.controller = self
        self.tokenField.setTokenizingCharacterSet_(charSet)
        self.tokenField.setTokenStyle_(NSTokenStyleSquared)
        self.tokenField.setDelegate_(self)
        self.tokenField.setFont_(smallFont)
        self.tokenField.setEnabled_(False)

        # batch edit toolbar
        # note: setting `imagePosition` in the XIB does not suffice since when the localized string is applied as a title the `imagePosition` value is reset
        self.addButton.setImagePosition_(NSImageOnly)
        self.removeButton.setImagePosition_(NSImageOnly)

        # prompt token field
        self.promptTokenField.setTokenizingCharacterSet_(charSet)
        self.promptTokenField.setTokenStyle_(NSTokenStyleSquared)
        self.promptTokenField.setDelegate_(self)
        self.promptTokenField.setFont_(font)

        # rename prompt
        self.renameSearchField.setFont_(font)
        self.renameSearchField.setDelegate_(self)

        self.renameReplaceField.setFont_(font)

        # listen for 'GSUpdateInterface' event
        Glyphs.addCallback(self.update, UPDATEINTERFACE)

    @objc.python_method
    def update(self, sender):
        isMultipleSelection = False

        if glyphs := self.selectedGlyphs():
            self.tokenField.setPlaceholderString_(NO_TAGS_STRING)
            self.tokenField.setEnabled_(True)

            if len(glyphs) == 1:
                # a single glyph is selected
                glyph = glyphs[0]
                self.setFieldTags(glyph.tags)
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
                    self.setFieldTags(firstTags)
                else:
                    isMultipleSelection = True
                    self.tokenField.setPlaceholderString_(MULTIPLE_VALUES_STRING)
                    self.setFieldTags([])
        else:
            print("N")
            # no glyphs are selected
            self.tokenField.setPlaceholderString_("")
            self.tokenField.setEnabled_(False)
            self.setFieldTags([])

        self.batchEditToolbar.setHidden_(not isMultipleSelection)

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
        """Returns the tags of all glyphs in the given font."""
        tags = set()

        for glyph in font.glyphs:
            tags.update(glyph.tags)

        return tags

    @objc.python_method
    def selectedTags(self):
        """Returns the tags of all selected glyphs."""
        tags = set()

        for glyph in self.selectedGlyphs():
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
            if font.currentTab:
                return [layer.parent for layer in font.selectedLayers]
            else:
                try:
                    return font.selection
                except:
                    pass
        return []

    @objc.python_method
    def reloadTagPool(self):
        """Loads all tags of the font into the tag pool."""
        if font := self.currentFont():
            self.tagPool = GutenTag.fontTags(font)
        else:
            self.tagPool = []

    @objc.python_method
    def setFieldTags(self, tags):
        """Sets the value of the token filed to the given tags."""
        tags = sorted(set(tags))
        self.tokenField.setStringValue_(",".join(tags))

    @objc.IBAction
    def updateTagsForSelectedGlyphs_(self, sender):
        """Confirms the entered tags and sets them on the selected glyphs."""
        tags = self.tokenField.objectValue()
        glyphs = self.selectedGlyphs()

        with self.uiContext:
            for glyph in glyphs:
                glyph.setTags_(tags)

    @objc.python_method
    def commit(self):
        """Confirm current value and resign as first responder."""
        self.updateTagsForSelectedGlyphs_(None)

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
                font.newTab("/" + sender.representedObject().name)

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

    # MARK: - Prompts

    def confirmPrompt(self):
        self.windowController().window().endSheet_returnCode_(self.promptWindow, NSModalResponseOK)

    def cancelPrompt(self):
        self.windowController().window().endSheet_returnCode_(self.promptWindow, NSModalResponseCancel)

    # MARK: Add Prompt

    @objc.IBAction
    def promptAddTags_(self, sender):
        self.promptTitleLabel.setStringValue_(ADD_TAGS_TITLE_STRING)
        self.promptConfirmButton.setTitle_(ADD_TAGS_BUTTON_STRING)
        self.promptCancelButton.setAction_(self.cancelPrompt)
        self.promptCancelButton.setTarget_(self)
        self.promptConfirmButton.setAction_(self.confirmPrompt)
        self.promptConfirmButton.setTarget_(self)

        self.promptTokenField.setStringValue_("")

        self.reloadTagPool()
        self.suggestionTagPool = self.tagPool

        self.windowController().window().beginSheet_completionHandler_(self.promptWindow, self.handleAddTags_)

    def handleAddTags_(self, returnCode):
        if returnCode != NSModalResponseOK:
            return

        addTags = set(self.promptTokenField.objectValue())

        with self.uiContext:
            for glyph in self.selectedGlyphs():
                tags = set(glyph.tags)
                didExtend = False

                for tag in addTags:
                    if tag not in tags:
                        tags.add(tag)
                        didExtend = True

                if didExtend:
                    # `setTags_` does not accept sets
                    glyph.setTags_(list(tags))

        self.update(None)

    # MARK: Remove Prompt

    @objc.IBAction
    def promptRemoveTags_(self, sender):
        self.promptTitleLabel.setStringValue_(REMOVE_TAGS_TITLE_STRING)
        self.promptConfirmButton.setTitle_(REMOVE_TAGS_BUTTON_STRING)
        self.promptCancelButton.setAction_(self.cancelPrompt)
        self.promptCancelButton.setTarget_(self)
        self.promptConfirmButton.setAction_(self.confirmPrompt)
        self.promptConfirmButton.setTarget_(self)

        self.promptTokenField.setStringValue_("")

        self.suggestionTagPool = self.selectedTags()

        self.windowController().window().beginSheet_completionHandler_(self.promptWindow, self.handleRemoveTags_)

    def handleRemoveTags_(self, returnCode):
        if returnCode != NSModalResponseOK:
            return

        removeTags = set(self.promptTokenField.objectValue())

        with self.uiContext:
            for glyph in self.selectedGlyphs():
                tags = set(glyph.tags)
                didReduce = False

                for tag in removeTags:
                    if tag in tags:
                        tags.remove(tag)
                        didReduce = True

                if didReduce:
                    # `setTags_` does not accept sets
                    glyph.setTags_(list(tags))

        self.update(None)

    # MARK: Rename Prompt

    def confirmRenameForm(self):
        self.windowController().window().endSheet_returnCode_(self.renameWindow, NSModalResponseOK)

    def cancelRenameForm(self):
        self.windowController().window().endSheet_returnCode_(self.renameWindow, NSModalResponseCancel)

    @objc.IBAction
    def promptRenameTags_(self, sender):
        self.renameCancelButton.setAction_(self.cancelRenameForm)
        self.renameCancelButton.setTarget_(self)
        self.renameConfirmButton.setAction_(self.confirmRenameForm)
        self.renameConfirmButton.setTarget_(self)

        self.suggestionTagPool = self.selectedTags()
        tags = sorted(self.suggestionTagPool)

        if len(tags) == 1:
            self.renameSearchField.setEditable_(False)
            self.renameSearchField.setStringValue_(tags[0])
            self.renameWindow.makeFirstResponder_(self.renameReplaceField)
        else:
            self.renameSearchField.setEditable_(True)
            self.renameSearchField.setStringValue_("")
            self.renameWindow.makeFirstResponder_(self.renameSearchField)

        self.renameSearchField.removeAllItems()
        self.renameSearchField.addItemsWithObjectValues_(tags)
        self.renameReplaceField.setStringValue_("")

        self.windowController().window().beginSheet_completionHandler_(self.renameWindow, self.handleRenameTag_)

    def handleRenameTag_(self, returnCode):
        if returnCode != NSModalResponseOK:
            return

        tagName = self.renameSearchField.stringValue()
        newTagName = self.renameReplaceField.stringValue()

        with self.uiContext:
            for glyph in self.selectedGlyphs():
                if tagName in glyph.tags:
                    tags = set(glyph.tags)
                    tags.remove(tagName)
                    tags.add(newTagName)
                    # `setTags_` does not accept sets
                    glyph.setTags_(list(tags))

        self.update(None)

    # MARK: - NSComboBoxDelegate

    def comboBoxWillPopUp_(self, notification):
        # disable buttons while pop-up is open, otherwise (1) the Return would both accept the selected entry in the pop-up and confirm the promt and (2) the Escape key would both close the pop-up and the promp
        # note that (2) has not been observed in practice but it is still defended against since that requires only a few lines of code
        self.renameCancelButton.setEnabled_(False)
        self.renameConfirmButton.setEnabled_(False)

    def comboBoxWillDismiss_(self, notification):
        # there is no `comboBoxDidDismiss_` delegate method, so this timer simulates that
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.1, self, self.comboBoxDidDismiss_, None, False)

    def comboBoxDidDismiss_(self, userInfo):
        self.renameCancelButton.setEnabled_(True)
        self.renameConfirmButton.setEnabled_(True)

        # MARK: - NSTokenFieldDelegate

    def tokenField_displayStringForRepresentedObject_(self, tokenField, tag):
        return tag

    def tokenField_editingStringForRepresentedObject_(self, tokenField, tag):
        return tag

    def tokenField_hasMenuForRepresentedObject_(self, tokenField, tag):
        return tokenField is self.tokenField

    def tokenField_menuForRepresentedObject_(self, tokenField, tag):
        # apply tags to selected glyphs so that they show up in the menu
        self.updateTagsForSelectedGlyphs_(None)

        # add a menu with each glyph that has `tag` as a tag
        menu = NSMenu.new()

        if font := self.currentFont():
            master = font.selectedFontMaster
            selectedGlyphs = set(self.selectedGlyphs())

            # menu item layout setup
            upm = font.upm
            viewSize = self.userDefaults.read("GlyphPreviewSize", 56, transform=lambda x: max(1, int(x)))  # pt
            margin = self.userDefaults.read("GlyphPreviewInset", 6, transform=int)  # pt
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
            showGlyphsItem.setTitle_(SHOW_ALL_GLYPHS_BUTTON_STRING)
            showGlyphsItem.setRepresentedObject_(tag)
            showGlyphsItem.setTarget_(self)
            showGlyphsItem.setAction_(self.showGlyphsForTag_)
            menu.addItem_(showGlyphsItem)

            menu.addItem_(NSMenuItem.separatorItem())

            matchingGlyphs = [x for x in font.glyphs if tag in x.tags]

            maximumPreviewGlyphCount = self.userDefaults.read(
                "MaximumGlyphPreviewCount", 1000, transform=lambda x: max(-1, int(x)))

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
                transform.translateXBy_yBy_((upm - layer.width) / 2 + offset, -master.descender + offset)
                path.transformUsingAffineTransform_(transform)

                NSColor.textColor().set()
                roundedRect.setClip()
                path.fill()

                image.unlockFocus()

                # menu item label
                attributedTitle = NSMutableAttributedString.alloc().initWithString_attributes_(glyph.name, {
                    NSFontAttributeName: menuItemFont
                })
                unicodesString = ", ".join(glyph.unicodes) if glyph.unicodes else "—"
                unicodesAttrString = NSMutableAttributedString.alloc().initWithString_attributes_(
                    "\n" + unicodesString,
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
                menu.addItem_(item)

        return menu

    def tokenField_completionsForSubstring_indexOfToken_indexOfSelectedItem_(
            self, tokenField, substring, tokenIndex, selectedIndex):
        query = str(substring)
        matches = []

        setTags = tokenField.objectValue()

        # hide tags that are already set (part of `tokenField.objectValue`) except if the tag equals the query (`substring`)
        availableTags = [tag for tag in self.suggestionTagPool if tag == substring or not tag in setTags]

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
            if commandSelector == "cancel:":
                self.commit()
                return True
        return False


class MultilineTokenField(NSTokenField):
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


class GutenTagTokenField(MultilineTokenField):
    controller = None

    def textDidBeginEditing_(self, notification):
        super().textDidBeginEditing_(notification)
        self.controller.reloadTagPool()
        self.controller.suggestionTagPool = self.controller.tagPool

    def textShouldEndEditing_(self, notification):
        result = super().textShouldEndEditing_(notification)
        self.controller.updateTagsForSelectedGlyphs_(self)
        return result
