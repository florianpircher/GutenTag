//
//  GTAGPlugin.h
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

#import <Cocoa/Cocoa.h>
#import <GlyphsCore/GSFontMaster.h>
#import <GlyphsCore/GSGlyph.h>
#import <GlyphsCore/GSLayer.h>
#import <GlyphsCore/GlyphsPaletteProtocol.h>
#import <GlyphsCore/GSWindowControllerProtocol.h>
#import <GlyphsCore/GSGlyphEditViewProtocol.h>
#import <GlyphsCore/GSGlyphViewControllerProtocol.h>
#import "GTAGMultilineTokenField.h"
#import "GTAGPaletteTokenField.h"
#import "GTAGCoordinator.h"

NS_ASSUME_NONNULL_BEGIN

@class GTAGPaletteTokenField;
@class GTAGMultilineTokenField;
@class GTAGCoordinator;

@interface GTAGPlugin : NSViewController <
    GlyphsPalette,
    NSTokenFieldDelegate,
    NSControlTextEditingDelegate,
    NSComboBoxDelegate,
    NSTokenFieldDelegate
>

// Palette
@property (weak) IBOutlet GTAGPaletteTokenField *tagsField;
@property (weak) IBOutlet NSButton *addButton;
@property (weak) IBOutlet NSButton *removeButton;
@property (weak) IBOutlet NSStackView *batchEditToolbar;
// Prompt
@property (strong) IBOutlet NSWindow *promptWindow;
@property (weak) IBOutlet NSTextField *promptTitleLabel;
@property (weak) IBOutlet GTAGMultilineTokenField *promptTagsField;
@property (weak) IBOutlet NSButton *promptConfirmButton;
// Rename
@property (strong) IBOutlet NSWindow *renameWindow;
@property (weak) IBOutlet NSComboBox *renameSearchField;
@property (weak) IBOutlet NSTextField *renameReplaceField;
@property (weak) IBOutlet NSButton *renameConfirmButton;
// Store
@property (strong) NSArray<NSString *> *tagPool;
@property (strong) NSArray<NSString *> *suggestionTagPool;
// Preferences
@property (nonatomic) CGFloat glyphPreviewSize;
@property (nonatomic) CGFloat glyphPreviewInset;
@property (nonatomic) NSInteger maximumGlyphPreviewCount;

- (IBAction)updateTagsForSelectedGlyphs:(nullable id)sender;
- (IBAction)promptAddTags:(nullable id)sender;
- (IBAction)promptRemoveTags:(nullable id)sender;
- (IBAction)promptRenameTags:(nullable id)sender;
- (IBAction)confirmPrompt:(nullable id)sender;
- (IBAction)cancelPrompt:(nullable id)sender;
- (IBAction)confirmRename:(nullable id)sender;
- (IBAction)cancelRename:(nullable id)sender;

- (NSArray<GSGlyph *> *)selectedGlyphs;
- (NSOrderedSet<NSString *> *)selectedTags;
- (void)reloadTagPool;

@end

@interface NSView (private) <GSGlyphEditViewProtocol>
- (void)replaceActiveLayersWithGlyphs:(NSArray<GSGlyph *> *)glyphs;
@end

@interface GSDocument : NSDocument
@property (unsafe_unretained, readonly, nonatomic) GSFontMaster *selectedFontMaster;
@property (readonly, nonatomic) NSWindowController *windowController;
@end

NS_ASSUME_NONNULL_END
