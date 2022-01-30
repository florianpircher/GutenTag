//
//  GTAGPlugin.m
//  Guten Tag
//
//  Copyright 2021 Florian Pircher
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.
//

#import "GTAGPlugin.h"

@implementation GTAGPlugin

@synthesize windowController;

// Key-Value Coding
static void * const GTAGPluginKVOContext = (void*)&GTAGPluginKVOContext;
static NSString * const kUserDefaultsControllerKeyPrefix = @"values.";
// Notifications
static NSString * const kUpdateInterface = @"GSUpdateInterface";
// User Defaults
static NSString * const kUserDefaultsKeyGlyphPreviewSize = @"GutenTagGlyphPreviewSize";
static NSString * const kUserDefaultsKeyGlyphPreviewInset = @"GutenTagGlyphPreviewInset";
static NSString * const kUserDefaultsKeyMaximumGlyphPreviewCount = @"GutenTagMaximumGlyphPreviewCount";
// User Defaults (Legacy)
static NSString * const kLegacyUserDefaultsKeyGlyphPreviewSize = @"com.FlorianPircher.GutenTag.GlyphPreviewSize";
static NSString * const kLegacyUserDefaultsKeyGlyphPreviewInset = @"com.FlorianPircher.GutenTag.GlyphPreviewInset";
static NSString * const kLegacyUserDefaultsKeyMaximumGlyphPreviewCount = @"com.FlorianPircher.GutenTag.MaximumGlyphPreviewCount";
// Default Values
const CGFloat DEFAULT_GLYPH_PREVIEW_SIZE = 36.0;
const CGFloat DEFAULT_GLYPH_PREVIEW_INSET = 4.0;
const NSInteger DEFAULT_MAXIMUM_GLYPH_PREVIEW_COUNT = 1000;
// Shared
static NSBundle *bundle;

+ (void)initialize {
    bundle = [NSBundle bundleForClass:self.class];
    
    // Register shortcut
    [GTAGCoordinator sharedCoordinator];
}

// MARK: - Utility

+ (NSFont *)legibileFontOfSize:(CGFloat)size {
    NSFontDescriptor *descriptor = [NSFont systemFontOfSize:size].fontDescriptor;
    NSFontDescriptor *legibileDescriptor = [descriptor fontDescriptorByAddingAttributes:@{
        NSFontFeatureSettingsAttribute: @[
                @{
                    NSFontFeatureTypeIdentifierKey: @(kStylisticAlternativesType),
                    NSFontFeatureSelectorIdentifierKey: @(kStylisticAltSixOnSelector),
                },
        ]
    }];
    return [NSFont fontWithDescriptor:legibileDescriptor size:size];
}

// MARK: - Glyphs API

- (NSUInteger)interfaceVersion {
    return 1;
}

- (NSString *)title {
    return NSLocalizedStringFromTableInBundle(@"Tags", nil, bundle, @"The heading of the palette section");
}

- (NSInteger)maxHeight {
    return NSIntegerMax;
}

- (NSInteger)minHeight {
    return 10;
}

- (NSUInteger)currentHeight {
    return [NSUserDefaults.standardUserDefaults integerForKey:@"GutenTagViewHeight"];
}

- (void)setCurrentHeight:(NSUInteger)newHeight {
    if (newHeight >= self.minHeight && newHeight <= self.maxHeight) {
        [NSUserDefaults.standardUserDefaults setInteger:newHeight forKey:@"GutenTagViewHeight"];
    }
}

- (NSView *)theView {
    return self.view;
}

// MARK: - Properties

- (void)setGlyphPreviewSize:(CGFloat)glyphPreviewSize {
    _glyphPreviewSize = fmax(8.0, glyphPreviewSize);
}

- (void)setMaximumGlyphPreviewCount:(NSInteger)maximumGlyphPreviewCount {
    _maximumGlyphPreviewCount = maximumGlyphPreviewCount > 0
        ? maximumGlyphPreviewCount
        : LONG_MAX; // lift limit for non-positive values
}

// MARK: - Init

- (instancetype)init {
    self = [super initWithNibName:@"View" bundle:bundle];
    
    if (self) {
        // MARK: Setup Preferences
        NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
        
        // MARK: Glyph Preview Size
        
        if ([defaults objectForKey:kUserDefaultsKeyGlyphPreviewSize] != nil) {
            self.glyphPreviewSize = [defaults doubleForKey:kUserDefaultsKeyGlyphPreviewSize];
        }
        else {
            if ([defaults objectForKey:kLegacyUserDefaultsKeyGlyphPreviewSize] != nil) {
                self.glyphPreviewSize = [defaults doubleForKey:kLegacyUserDefaultsKeyGlyphPreviewSize];
                [defaults removeObjectForKey:kLegacyUserDefaultsKeyGlyphPreviewSize];
                [defaults setDouble:self.glyphPreviewSize forKey:kUserDefaultsKeyGlyphPreviewSize];
            }
            else {
                self.glyphPreviewSize = DEFAULT_GLYPH_PREVIEW_SIZE;
            }
        }
        
        // MARK: Glyph Preview Inset
        
        if ([defaults objectForKey:kUserDefaultsKeyGlyphPreviewInset] != nil) {
            self.glyphPreviewInset = [defaults doubleForKey:kUserDefaultsKeyGlyphPreviewInset];
        }
        else {
            if ([defaults objectForKey:kLegacyUserDefaultsKeyGlyphPreviewInset] != nil) {
                self.glyphPreviewInset = [defaults doubleForKey:kLegacyUserDefaultsKeyGlyphPreviewInset];
                [defaults removeObjectForKey:kLegacyUserDefaultsKeyGlyphPreviewInset];
                [defaults setDouble:self.glyphPreviewInset forKey:kUserDefaultsKeyGlyphPreviewInset];
            }
            else {
                self.glyphPreviewInset = DEFAULT_GLYPH_PREVIEW_INSET;
            }
        }
        
        // MARK: Maximum Glyph Preview Count
        
        if ([defaults objectForKey:kUserDefaultsKeyMaximumGlyphPreviewCount] != nil) {
            self.maximumGlyphPreviewCount = [defaults integerForKey:kUserDefaultsKeyMaximumGlyphPreviewCount];
        }
        else {
            if ([defaults objectForKey:kLegacyUserDefaultsKeyMaximumGlyphPreviewCount] != nil) {
                self.maximumGlyphPreviewCount = [defaults integerForKey:kLegacyUserDefaultsKeyMaximumGlyphPreviewCount];
                [defaults removeObjectForKey:kLegacyUserDefaultsKeyMaximumGlyphPreviewCount];
                [defaults setInteger:self.maximumGlyphPreviewCount forKey:kUserDefaultsKeyMaximumGlyphPreviewCount];
            }
            else {
                self.maximumGlyphPreviewCount = DEFAULT_MAXIMUM_GLYPH_PREVIEW_COUNT;
            }
        }
        
        // MARK: Observe User Defaults
        
        NSUserDefaultsController *defaultsController = NSUserDefaultsController.sharedUserDefaultsController;
        [defaultsController addObserver:self
                             forKeyPath:[kUserDefaultsControllerKeyPrefix stringByAppendingString:kUserDefaultsKeyGlyphPreviewSize]
                                options:0
                                context:GTAGPluginKVOContext];
        [defaultsController addObserver:self
                             forKeyPath:[kUserDefaultsControllerKeyPrefix stringByAppendingString:kUserDefaultsKeyGlyphPreviewInset]
                                options:0
                                context:GTAGPluginKVOContext];
        [defaultsController addObserver:self
                             forKeyPath:[kUserDefaultsControllerKeyPrefix stringByAppendingString:kUserDefaultsKeyMaximumGlyphPreviewCount]
                                options:0
                                context:GTAGPluginKVOContext];
    }
    
    return self;
}

- (void)dealloc {
    NSUserDefaultsController *defaultsController = NSUserDefaultsController.sharedUserDefaultsController;
    [defaultsController removeObserver:self
                            forKeyPath:[kUserDefaultsControllerKeyPrefix stringByAppendingString:kUserDefaultsKeyGlyphPreviewSize]
                               context:GTAGPluginKVOContext];
    [defaultsController removeObserver:self
                            forKeyPath:[kUserDefaultsControllerKeyPrefix stringByAppendingString:kUserDefaultsKeyGlyphPreviewInset]
                               context:GTAGPluginKVOContext];
    [defaultsController removeObserver:self
                            forKeyPath:[kUserDefaultsControllerKeyPrefix stringByAppendingString:kUserDefaultsKeyMaximumGlyphPreviewCount]
                               context:GTAGPluginKVOContext];
    
    [NSNotificationCenter.defaultCenter removeObserver:self];
    [GTAGCoordinator.sharedCoordinator unlink:self];
}

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context {
    if (context == GTAGPluginKVOContext) {
        if (![keyPath hasPrefix:kUserDefaultsControllerKeyPrefix]) {
            return;
        }
        
        // MARK: Dynamically Update Preferences
        
        NSString *defaultsKey = [keyPath substringFromIndex:kUserDefaultsControllerKeyPrefix.length];
        NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
        
        if ([defaultsKey isEqualToString:kUserDefaultsKeyGlyphPreviewSize]) {
            if ([defaults objectForKey:kUserDefaultsKeyGlyphPreviewSize] != nil) {
                self.glyphPreviewSize = [defaults doubleForKey:kUserDefaultsKeyGlyphPreviewSize];
            }
            else {
                self.glyphPreviewSize = DEFAULT_GLYPH_PREVIEW_SIZE;
            }
        }
        else if ([defaultsKey isEqualToString:kUserDefaultsKeyGlyphPreviewInset]) {
            if ([defaults objectForKey:kUserDefaultsKeyGlyphPreviewInset] != nil) {
                self.glyphPreviewInset = [defaults doubleForKey:kUserDefaultsKeyGlyphPreviewInset];
            }
            else {
                self.glyphPreviewInset = DEFAULT_GLYPH_PREVIEW_INSET;
            }
        }
        else if ([defaultsKey isEqualToString:kUserDefaultsKeyMaximumGlyphPreviewCount]) {
            if ([defaults objectForKey:kUserDefaultsKeyMaximumGlyphPreviewCount] != nil) {
                self.maximumGlyphPreviewCount = [defaults integerForKey:kUserDefaultsKeyMaximumGlyphPreviewCount];
            }
            else {
                self.maximumGlyphPreviewCount = DEFAULT_MAXIMUM_GLYPH_PREVIEW_COUNT;
            }
        }
    } else {
        [super observeValueForKeyPath:keyPath ofObject:object change:change context:context];
    }
}

- (void)viewDidLoad {
    NSMutableCharacterSet *tokenizingCharacterSet = [NSMutableCharacterSet characterSetWithCharactersInString:@"\n"];
    NSCharacterSet *defaultCharSet = NSTokenField.defaultTokenizingCharacterSet;
    [tokenizingCharacterSet formUnionWithCharacterSet:defaultCharSet];
    
    CGFloat fontSize = NSFont.systemFontSize;
    NSFont *font = [GTAGPlugin legibileFontOfSize:fontSize];
    
    CGFloat smallFontSize = NSFont.smallSystemFontSize;
    NSFont *smallFont = [GTAGPlugin legibileFontOfSize:smallFontSize];
    
    _tagsField.enabled = NO;
    _tagsField.font = smallFont;
    _tagsField.tokenStyle = NSTokenStyleSquared;
    _tagsField.tokenizingCharacterSet = tokenizingCharacterSet;
    _tagsField.delegate = self;
    _tagsField.tagPoolDelegate = self;
    
    // re-set to `imageOnly` since applying localized strings for the titles unsets the image position
    _addButton.imagePosition = NSImageOnly;
    _removeButton.imagePosition = NSImageOnly;
    
    _promptTagsField.font = font;
    _promptTagsField.tokenStyle = NSTokenStyleSquared;
    _promptTagsField.tokenizingCharacterSet = tokenizingCharacterSet;
    _promptTagsField.delegate = self;
    
    _renameSearchField.font = font;
    _renameSearchField.delegate = self;
    
    _renameReplaceField.font = font;
    _renameReplaceField.delegate = self;
    
    [NSNotificationCenter.defaultCenter addObserver:self
                                           selector:@selector(interfaceDidUpdate)
                                               name:kUpdateInterface
                                             object:nil];
    
    [GTAGCoordinator.sharedCoordinator link:self];
}

// MARK: - Accessors

/// The font represented by document on which the palette is placed.
- (nullable GSFont *)documentFont {
    if (windowController == nil) return nil;
    return windowController.documentFont;
}

/// The currently selected font master.
- (nullable GSFontMaster *)selectedFontMaster {
    if (windowController == nil) return nil;
    
    GSDocument *document = windowController.document;
    
    if (document == nil) return nil;
    
    return document.selectedFontMaster;
}

/// Returns all selected glyphs, both in Edit View and in Font View.
- (NSArray<GSGlyph *> *)selectedGlyphs {
    if (windowController == nil) return @[];
    
    NSArray<GSLayer *> *layers = windowController.selectedLayers;
    NSMutableArray<GSGlyph *> *glyphs = [NSMutableArray new];
    
    for (GSLayer *layer in layers) {
        GSGlyph *glyph = layer.parent;
        [glyphs addObject:glyph];
    }
    
    return glyphs;
}

/// The union of all tags for all selected glyphs.
- (NSOrderedSet<NSString *> *)selectedTags {
    NSMutableOrderedSet *tags = [NSMutableOrderedSet new];
    
    for (GSGlyph *glyph in self.selectedGlyphs) {
        [tags unionOrderedSet:glyph.tags];
    }
    
    return tags;
}

/// Loads all tags of the font into the tag pool.
- (void)reloadTagPool {
    GSFont *font = self.documentFont;
    
    if (font != nil) {
        self.tagPool = font.allTags;
    }
    else {
        self.tagPool = @[];
    }
}

// MARK: - Interface Update

- (void)interfaceDidUpdate {
    BOOL isMultipleValues = NO;
    
    NSArray<GSGlyph *> *glyphs = self.selectedGlyphs;
    
    if (glyphs.count > 0) {
        _tagsField.placeholderString = NSLocalizedStringFromTableInBundle(@"no tags", nil, bundle, @"The placeholder for the tags field that is shown when the field is empty");
        _tagsField.enabled = YES;
        
        if (glyphs.count == 1) {
            // a single glyph is selected
            GSGlyph *glyph = glyphs.firstObject;
            [self displayTags:glyph.tags];
        }
        else {
            // multiple glyphs are selected
            GSGlyph *firstGlyph = glyphs.firstObject;
            NSOrderedSet<NSString *> *firstGlyphTags = firstGlyph.tags;
            
            for (int i = 1; i < glyphs.count; i++) {
                GSGlyph *glyph = glyphs[i];
                
                if ([glyph.tags isNotEqualTo:firstGlyphTags]) {
                    isMultipleValues = YES;
                    break;
                }
            }
            
            if (!isMultipleValues) {
                [self displayTags:firstGlyphTags];
            }
            else {
                _tagsField.placeholderString = NSLocalizedStringFromTableInBundle(@"Multiple Values", nil, bundle, @"The placeholder for the tags field that is shown when the field represents multiple incompatible values");
                [self displayTags:[NSOrderedSet new]];
            }
        }
    }
    else {
        // no glyphs are selected
        _tagsField.placeholderString = @"";
        _tagsField.enabled = NO;
        [self displayTags:[NSOrderedSet new]];
    }
    
    _batchEditToolbar.hidden = !isMultipleValues;
}

/// Sets the value of the token filed to the given tags.
- (void)displayTags:(NSOrderedSet<NSString *> *)tags {
    _tagsField.objectValue = tags.array;
}

// MARK: - Setting Tags

/// Confirms the entered tags and sets them on the selected glyphs.
- (IBAction)updateTagsForSelectedGlyphs:(nullable id)sender {
    NSArray<NSString *> *tags = _tagsField.objectValue;
    NSOrderedSet<NSString *> *tagsSet = [NSOrderedSet orderedSetWithArray:tags];
    
    [self.documentFont disableUpdateInterface];
    
    for (GSGlyph *glyph in self.selectedGlyphs) {
        [glyph setTags:tagsSet];
    }
    
    [self.documentFont enableUpdateInterface];
}

/// Confirm current value and resign as first responder.
- (void)commit {
    [self updateTagsForSelectedGlyphs:nil];
    
    if (windowController == nil) return;
    
    // resign first responder status
    [windowController.window makeFirstResponder:nil];
}

// MARK: - Glyph Preview Menu

/// Opens all glyphs for a given tag in a new edit view tab.
///
/// The tag is given as a string in the represented object of the menu item.
- (void)showGlyphsForTag:(NSMenuItem *)sender {
    if (windowController == nil) return;
    
    GSFont *font = self.documentFont;
    
    if (font == nil) return;
    
    NSString *tag = sender.representedObject;
    NSMutableArray<GSGlyph *> *glyphs = [NSMutableArray new];
    
    for (GSGlyph *glyph in font.glyphs) {
        if ([glyph.tags containsObject:tag]) {
            [glyphs addObject:glyph];
        }
    }
    
    [windowController addTabWithGlyphs:glyphs];
}

/// Opens the given glyph in a new edit view tab, if in the font view, or replaces the active layer by the given glyph, if in the edit view.
///
/// The glyph is given as a `GSGlyph` in the represented object of the menu item.
- (void)openGlyph:(NSMenuItem *)sender {
    if (windowController == nil) return;
    
    GSFont *font = self.documentFont;
    
    if (font == nil) return;
    
    NSArray<GSGlyph *> *glyphs = @[sender.representedObject];
    
    if (windowController.activeEditViewController != nil) {
        [windowController.activeEditViewController.graphicView replaceActiveLayersWithGlyphs:glyphs];
    }
    else {
        [windowController addTabWithGlyphs:glyphs];
    }
}

// MARK: - Batch Editing

// MARK: Prompt

/// Closes the prompt window with an affirmative response.
- (IBAction)confirmPrompt:(nullable id)sender {
    [windowController.window endSheet:_promptWindow returnCode:NSModalResponseOK];
}

/// Closes the prompt window with a negative response.
- (IBAction)cancelPrompt:(nullable id)sender {
    [windowController.window endSheet:_promptWindow returnCode:NSModalResponseCancel];
}

/// Opens the prompt window prompting for tags to be added to the selected glyphs.
- (IBAction)promptAddTags:(nullable id)sender {
    [self reloadTagPool];
    self.suggestionTagPool = self.tagPool;
    
    _promptTitleLabel.stringValue = NSLocalizedStringFromTableInBundle(@"Add tags to selected glyphs", nil, bundle, @"The heading of the add-tags dialog window");
    
    _promptConfirmButton.title = NSLocalizedStringFromTableInBundle(@"Add Tags", nil, bundle, @"The confirmation button label of the add-tags dialog window");
    
    _promptTagsField.stringValue = @"";
    [_promptWindow makeFirstResponder:_promptTagsField];
    
    [windowController.window beginSheet:_promptWindow completionHandler:^(NSModalResponse returnCode) {
        if (returnCode != NSModalResponseOK) return;
        
        NSArray<NSString *> *addTags = self.promptTagsField.objectValue;
        
        [self.documentFont disableUpdateInterface];
        
        for (GSGlyph *glyph in self.selectedGlyphs) {
            NSMutableOrderedSet<NSString *> *set = [NSMutableOrderedSet orderedSetWithOrderedSet:glyph.tags];
            [set addObjectsFromArray:addTags];
            glyph.tags = set;
        }
        
        [self.documentFont enableUpdateInterface];
        
        [self interfaceDidUpdate];
    }];
}

/// Opens the prompt window prompting for tags to be removed from the selected glyphs.
- (IBAction)promptRemoveTags:(nullable id)sender {
    self.suggestionTagPool = self.selectedTags.array;
    
    _promptTitleLabel.stringValue = NSLocalizedStringFromTableInBundle(@"Remove tags from selected glyphs", nil, bundle, @"The heading of the remove-tags dialog window");
    
    _promptConfirmButton.title = NSLocalizedStringFromTableInBundle(@"Remove Tags", nil, bundle, @"The confirmation button label of the remove-tags dialog window");
    
    _promptTagsField.stringValue = @"";
    [_promptWindow makeFirstResponder:_promptTagsField];
    
    [windowController.window beginSheet:_promptWindow completionHandler:^(NSModalResponse returnCode) {
        if (returnCode != NSModalResponseOK) return;
        
        NSArray<NSString *> *removeTags = self.promptTagsField.objectValue;
        
        [self.documentFont disableUpdateInterface];
        
        for (GSGlyph *glyph in self.selectedGlyphs) {
            NSMutableOrderedSet<NSString *> *set = [NSMutableOrderedSet orderedSetWithOrderedSet:glyph.tags];
            [set removeObjectsInArray:removeTags];
            glyph.tags = set;
        }
        
        [self.documentFont enableUpdateInterface];
        
        [self interfaceDidUpdate];
    }];
}

// MARK: Rename Tag Form

/// Closes the prompt window with an affirmative response.
- (IBAction)confirmRename:(nullable id)sender {
    [windowController.window endSheet:_renameWindow returnCode:NSModalResponseOK];
}

/// Closes the prompt window with a negative response.
- (IBAction)cancelRename:(nullable id)sender {
    [windowController.window endSheet:_renameWindow returnCode:NSModalResponseCancel];
}

/// Opens the rename window quering for a tag name and its new name for the selected glyphs.
- (IBAction)promptRenameTags:(nullable id)sender {
    self.suggestionTagPool = self.selectedTags.array;
    
    [_renameSearchField removeAllItems];
    [_renameSearchField addItemsWithObjectValues:self.suggestionTagPool];
    
    if (self.suggestionTagPool.count == 1) {
        _renameSearchField.editable = NO;
        _renameSearchField.stringValue = self.suggestionTagPool.firstObject;
        [_renameWindow makeFirstResponder:_renameReplaceField];
    }
    else {
        _renameSearchField.editable = YES;
        _renameSearchField.stringValue = @"";
        [_renameWindow makeFirstResponder:_renameSearchField];
    }
    
    _renameReplaceField.stringValue = @"";
    
    _renameConfirmButton.enabled = NO;
    
    [windowController.window beginSheet:_renameWindow completionHandler:^(NSModalResponse returnCode) {
        if (returnCode != NSModalResponseOK) return;
        
        NSString *tagName = self.renameSearchField.stringValue;
        NSString *newTagName = self.renameReplaceField.stringValue;
        
        if (newTagName.length == 0) return;
        
        [self.documentFont disableUpdateInterface];
        
        for (GSGlyph *glyph in self.selectedGlyphs) {
            if ([glyph.tags containsObject:tagName]) {
                NSMutableOrderedSet<NSString *> *newTags = [NSMutableOrderedSet orderedSetWithOrderedSet:glyph.tags];
                [newTags removeObject:tagName];
                [newTags addObject:newTagName];
                glyph.tags = newTags;
            }
        }
        
        [self.documentFont enableUpdateInterface];
        
        [self interfaceDidUpdate];
    }];
}

- (BOOL)shouldEnableRenameConfirmButton {
    return _renameReplaceField.stringValue.length != 0;
}

// MARK: - NSControlTextEditingDelegate

- (BOOL)control:(NSControl *)control textView:(NSTextView *)textView doCommandBySelector:(SEL)commandSelector {
    if (control == _tagsField) {
        if (commandSelector == @selector(cancelOperation:)) {
            // commit on Escape (and other cancel-operation commands)
            [self commit];
            return YES;
        }
    }
    return NO;
}

- (void)controlTextDidChange:(NSNotification *)obj {
    if (obj.object == _renameReplaceField) {
        _renameConfirmButton.enabled = self.shouldEnableRenameConfirmButton;
    }
}

// MARK: - NSComboBoxDelegate

- (void)comboBoxWillPopUp:(NSNotification *)notification {
    // disable confirm button while pop-up is open, otherwise the Return key would accept both the selected entry in the pop-up and confirm the rename window
    _renameConfirmButton.enabled = false;
}

- (void)comboBoxWillDismiss:(NSNotification *)notification {
    // there is no `comboBoxDidDismiss(_:)` delegate method, so this timer simulates that
    //Timer.scheduledTimer(timeInterval: 0.1, target: self, selector: #selector(comboBoxDidDismiss(_:)), userInfo: nil, repeats: false)
    [NSTimer scheduledTimerWithTimeInterval:0.1 target:self selector:@selector(comboBoxDidDismiss:) userInfo:nil repeats:NO];
}

- (void)comboBoxDidDismiss:(NSNotification *)notification {
    self.renameConfirmButton.enabled = self.shouldEnableRenameConfirmButton;
}

// MARK: - NSTokenFieldDelegate

- (BOOL)tokenField:(NSTokenField *)tokenField hasMenuForRepresentedObject:(id)representedObject {
    // only tokens in the main tags field offer the glyph preview menu
    return tokenField == _tagsField;
}

/// Constructs and returns an NSString object that is the result of interposing a separator matching the current locale between the elements of the array.
- (NSString *)localizedComponentsJoinedByString:(NSArray<NSString *> *)strings {
    static NSString *separator = nil;
    static NSString *itemPrefix = nil;
    static NSString *itemSuffix = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        NSString *languageCode = NSLocale.currentLocale.languageCode;
        
        if ([languageCode isEqualToString:@"ar"]) {
            separator = @" \u0648"; // SPACE -- ARABIC LETTER WAW
            itemPrefix = @"\u2068"; // FIRST STRONG ISOLATE
            itemSuffix = @"\u2069"; // POP DIRECTIONAL ISOLATE
        }
        else if ([languageCode isEqualToString:@"ja"] || [languageCode isEqualToString:@"zh"]) {
            separator = @"\u3001"; // IDEOGRAPHIC COMMA
            itemPrefix = @"";
            itemSuffix = @"";
        }
        else {
            separator = @", ";
            itemPrefix = @"";
            itemSuffix = @"";
        }
    });
    NSMutableArray<NSString *> *mappedStrings = [NSMutableArray new];
    
    for (NSString *string in strings) {
        NSString *mappedString = [NSString stringWithFormat:@"%@%@%@", itemPrefix, string, itemSuffix];
        [mappedStrings addObject:mappedString];
    }
    
    return [mappedStrings componentsJoinedByString:separator];
}

- (NSMenu *)tokenField:(NSTokenField *)tokenField menuForRepresentedObject:(id)tag {
    // update selected glyph with current tags field value such that they are already reflected in the glyphs preview menu
    [self updateTagsForSelectedGlyphs:nil];
    
    GSFont *font = self.documentFont;
    
    if (font == nil) return nil;
    
    GSFontMaster *master = self.selectedFontMaster;
    
    if (master == nil) return nil;
    
    // create glyphs preview menu
    NSMenu *menu = [NSMenu new];
    
    NSSet<GSGlyph *> *selectedGlyphs = [NSSet setWithArray:self.selectedGlyphs];
    CGFloat upm = (CGFloat)font.unitsPerEm;
    /// The width and height of the preview image.
    CGFloat viewSize = self.glyphPreviewSize;
    /// The visual inset in the image from the top and bottom to prevent clipping ascenders and descenders.
    CGFloat inset = self.glyphPreviewInset;
    /// The point size at which the glyph is drawn.
    CGFloat fontSize = viewSize - 2.0 * inset;
    CGFloat offset = upm / (fontSize / inset);
    
    /// The rect representing the preview image.
    NSRect rect = NSMakeRect(0.0, 0.0, viewSize, viewSize);
    /// The size of the preview image.
    NSSize size = rect.size;
    /// The rounding radius applied on all four corners of the preview image.
    CGFloat roundingRadius = 3.0;
    /// The path of the rounded rect clipping the preview image background colors and glyph.
    NSBezierPath *roundedRectPath = [NSBezierPath bezierPathWithRoundedRect:rect xRadius:roundingRadius yRadius:roundingRadius];
    
    NSRect layerClipRect = NSMakeRect(viewSize / 2.0, 0.0, viewSize / 2.0, viewSize);
    /// The shape of the layer background color.
    NSBezierPath *layerClipPath = [NSBezierPath bezierPathWithRect:layerClipRect];
    
    /// The size used for the top left corner in `layerOnlyClipPath`.
    CGFloat cornerSize = viewSize / 5.0;
    /// The shape of the layer background color if only a layer color and no glyph color is set.
    NSBezierPath *layerOnlyClipPath = [NSBezierPath new];
    [layerOnlyClipPath moveToPoint:NSMakePoint(cornerSize, viewSize)];
    [layerOnlyClipPath moveToPoint:NSMakePoint(viewSize, viewSize)];
    [layerOnlyClipPath moveToPoint:NSMakePoint(viewSize, 0.0)];
    [layerOnlyClipPath moveToPoint:NSMakePoint(0.0, 0.0)];
    [layerOnlyClipPath moveToPoint:NSMakePoint(0.0, viewSize - cornerSize)];
    [layerOnlyClipPath closePath];
    
    NSRect glyphClipRect = NSMakeRect(0.0, 0.0, viewSize / 2.0, viewSize);
    /// The shape of the glyph background color if a layer color is also set.
    NSBezierPath *glyphClipPath = [NSBezierPath bezierPathWithRect:glyphClipRect];
    
    NSFont *menuItemFont = [GTAGPlugin legibileFontOfSize:NSFont.systemFontSize];
    NSFont *smallMenuItemFont = [GTAGPlugin legibileFontOfSize:NSFont.smallSystemFontSize];
    
    NSMenuItem *(^makeMenuItem)(GSGlyph *) = ^NSMenuItem *(GSGlyph *glyph) {
        NSString *glyphName = glyph.name ?: @"—";
        /// Whether the glyph is selected.
        BOOL isSelected = [selectedGlyphs containsObject:glyph];
        
        /// The layer to draw.
        GSLayer *layer = [glyph layerForId:master.id];
        /// The complete bezier path of the layer.
        NSBezierPath *path = layer.drawBezierPath;
        /// The image displaying the layer and the glyph and layer colors.
        NSImage *image = [NSImage imageWithSize:size flipped:NO drawingHandler:^BOOL(NSRect drawRect) {
            // draw glyph color
            if (glyph.color != nil) {
                if (layer.color != nil) {
                    // clip to the left half to allow for the layer color on the right
                    [glyphClipPath setClip];
                }
                
                [[glyph.color colorWithAlphaComponent:0.6] set];
                [roundedRectPath fill];
            }
            
            // draw layer color
            if (layer.color != nil) {
                if (glyph.color != nil) {
                    [layerClipPath setClip];
                }
                else {
                    [layerOnlyClipPath setClip];
                }
                
                [[layer.color colorWithAlphaComponent:0.6] set];
                [roundedRectPath fill];
            }
            
            // draw glyph
            NSAffineTransform *transform = [NSAffineTransform transform];
            [transform scaleBy:fontSize / upm];
            CGFloat dx = (upm - layer.width) / 2.0 + offset;
            CGFloat dy = -[master descenderForLayer:layer] + offset;
            [transform translateXBy:dx yBy:dy];
            [path transformUsingAffineTransform:transform];
            [roundedRectPath setClip];
            [NSColor.textColor set];
            [path fill];
            
            return YES;
        }];
        
        /// Title of the menu item with glyph name on top nad unicode values as secondary text below
        NSMutableAttributedString *attributedTitle = [[NSMutableAttributedString alloc] initWithString:glyphName attributes:@{
            NSFontAttributeName: menuItemFont,
        }];
        NSString *unicodesString;
        
        if (glyph.unicodes != nil && glyph.unicodes.count > 0) {
            unicodesString = [self localizedComponentsJoinedByString:glyph.unicodes.array];
        }
        else {
            unicodesString = @"\u2013"; // EN DASH
        }
        
        unicodesString = [@"\n" stringByAppendingString:unicodesString];
        
        NSAttributedString *unicodesAttributedString = [[NSAttributedString alloc] initWithString:unicodesString attributes:@{
            NSFontAttributeName: smallMenuItemFont,
            NSForegroundColorAttributeName: NSColor.secondaryLabelColor,
        }];
        [attributedTitle appendAttributedString:unicodesAttributedString];
        
        /// The menu item for the glyph.
        NSMenuItem *item = [NSMenuItem new];
        item.title = glyphName;
        item.attributedTitle = attributedTitle;
        item.image = image;
        item.target = self;
        item.action = @selector(openGlyph:);
        item.representedObject = glyph;
        
        if (isSelected && selectedGlyphs.count == 1) {
            item.state = NSOnState;
        }
        
        return item;
    };
    
    /// A menu items for opening all matching glyphs in a new edit view tab.
    NSMenuItem *showGlyphsItem = [NSMenuItem new];
    showGlyphsItem.title = NSLocalizedStringFromTableInBundle(@"Show All Glyphs", nil, bundle, @"The label for the menu item with the action of showing all glyphs that have the tag of the menu");
    showGlyphsItem.representedObject = tag;
    showGlyphsItem.target = self;
    showGlyphsItem.action = @selector(showGlyphsForTag:);
    
    [menu addItem:showGlyphsItem];
    [menu addItem:[NSMenuItem separatorItem]];
    
    /// All glyphs containg the tag.
    NSUInteger glyphCount = font.countOfGlyphs;
    NSInteger maxCount = self.maximumGlyphPreviewCount;
    int count = 0;
    
    for (NSInteger i = 0; i < glyphCount && count < maxCount; i++) {
        GSGlyph *glyph = [font glyphAtIndex:i];
        
        if ([glyph.tags containsObject:tag]) {
            [menu addItem:makeMenuItem(glyph)];
            count += 1;
        }
    }
    
    return menu;
}

- (NSArray *)tokenField:(NSTokenField *)tokenField completionsForSubstring:(NSString *)substring indexOfToken:(NSInteger)tokenIndex indexOfSelectedItem:(NSInteger *)selectedIndex {
    // suggest tags for the token field using the suggestions from `suggestionTagPool`
    NSArray<NSString *> *setTags = tokenField.objectValue;
    NSMutableArray<NSString *> *matches = [NSMutableArray new];
    
    for (NSString *tagName in self.suggestionTagPool) {
        // hide tags that are already set (part of `tokenField.objectValue`) except if the tag equals the query (`substring`)
        if (([tagName isEqualToString:substring] || ![setTags containsObject:tagName]) && [tagName hasPrefix:substring]) {
            [matches addObject:tagName];
        }
    }
    
    *selectedIndex = matches.count > 0 ? 0 : -1;
    
    return matches;
}

- (NSArray *)tokenField:(NSTokenField *)tokenField readFromPasteboard:(NSPasteboard *)pboard {
    // pasted text will be inserted varbatim and tokenized by the usual methods
    return @[];
}

- (BOOL)tokenField:(NSTokenField *)tokenField writeRepresentedObjects:(NSArray *)objects toPasteboard:(NSPasteboard *)pboard {
    // write the tags as individual objects
    // - pasting into single-line text fields will separate by spaces (possible creating ambiguity since tags can also contain spaces)
    // - pasting into multi-line text fields will paste each tag onto a separe line (this also applies to the tags fields by guten tag, and because new-line is a tokenizing character all pasted tags are tokenized correctly and without ambiguity)
    [pboard clearContents];
    [pboard writeObjects:objects];
    
    return YES;
}

- (NSArray *)tokenField:(NSTokenField *)tokenField shouldAddObjects:(NSArray *)tokens atIndex:(NSUInteger)index {
    // count occurrences to prevent adding duplicates entries
    NSMutableDictionary<NSString *, NSNumber *> *table = [NSMutableDictionary dictionary];
    
    // count the number of occurences for each value tag
    for (NSString *tag in tokenField.objectValue) {
        NSNumber *currentValue = table[tag];
        
        table[tag] = currentValue == nil
            ? @1
            : @(currentValue.intValue + 1);
    }
    
    // filter to-add tags such that no multiple-occurences tags are returned
    NSMutableArray<NSString *> *returnTokens = [NSMutableArray new];
    
    for (NSString *token in tokens) {
        NSNumber *value = table[token];
        
        if (value == nil || value.intValue <= 1) {
            [returnTokens addObject:token];
        }
    }
    
    return returnTokens;
}

@end
