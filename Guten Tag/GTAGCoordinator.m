//
//  GTAGCoordinator.m
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

#import "GTAGCoordinator.h"

static NSBundle *bundle;
static NSString * const kShortcutCommandsGroup = @"Guten Tag";

@implementation GTAGCoordinator {
    NSMapTable *links;
}

+ (void)initialize {
    bundle = [NSBundle bundleForClass:self.class];
}

+ (instancetype)sharedCoordinator {
    static GTAGCoordinator *sharedCoordinatorInstance = nil;
    static dispatch_once_t onceToken;
    
    dispatch_once(&onceToken, ^{
        sharedCoordinatorInstance = self.new;
    });
    
    return sharedCoordinatorInstance;
}

- (instancetype)init
{
    self = [super init];
    
    if (self) {
        links = [NSMapTable weakToStrongObjectsMapTable];
    }
    
    [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Edit Tags", nil, bundle, @"Shortcut command name for selecting the tags field")
                                         group:kShortcutCommandsGroup
                                    identifier:@"com.FlorianPircher.GutenTag.EditTags"
                                        action:@selector(editTags:)
                                        target:self
                                     character:@""
                                 modifierFlags:0];
    
    [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Add Tags", nil, bundle, @"Shortcut command name for adding tags to the selected glyphs")
                                         group:kShortcutCommandsGroup
                                    identifier:@"com.FlorianPircher.GutenTag.AddTags"
                                        action:@selector(addTags:)
                                        target:self
                                     character:@""
                                 modifierFlags:0];
    
    [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Remove Tags", nil, bundle, @"Shortcut command name for removing tags from the selected glyphs")
                                         group:kShortcutCommandsGroup
                                    identifier:@"com.FlorianPircher.GutenTag.RemoveTags"
                                        action:@selector(removeTags:)
                                        target:self
                                     character:@""
                                 modifierFlags:0];
    
    [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Rename Tags", nil, bundle, @"Shortcut command name for renaming tags for the selected glyphs")
                                         group:kShortcutCommandsGroup
                                    identifier:@"com.FlorianPircher.GutenTag.RenameTags"
                                        action:@selector(renameTags:)
                                        target:self
                                     character:@""
                                 modifierFlags:0];
    
    return self;
}

// MARK: - Linking

- (void)link:(GTAGPlugin *)link {
    [links setObject:NSNull.null forKey:link];
}

- (void)unlink:(GTAGPlugin *)link {
    [links removeObjectForKey:link];
}

// MARK: - Dispatch

- (nullable GTAGPlugin *)activeLink:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    GSFont *font = editViewController.representedObject;
    NSDocument *document = (NSDocument *)font.parent;
    
    if (document == nil) return nil;
    
    NSWindowController *windowController = document.windowController;
    
    if (windowController == nil) return nil;
    
    NSWindow *activeWindow = windowController.window;
    
    for (GTAGPlugin *link in links) {
        NSView *view = link.theView;
        NSWindow *window = view.window;
        
        if (activeWindow == window) {
            return link;
        }
    }
    
    return nil;
}

- (BOOL)validateShortcutCommand:(SEL)action editViewController:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    GTAGPlugin *link = [self activeLink:editViewController];
    
    if (link == nil) return NO;
    
    if (action == @selector(editTags:)) {
        return link.tagsField.enabled;
    }
    else if (action == @selector(addTags:)) {
        return link.selectedGlyphs.count > 0;
    }
    else if (action == @selector(removeTags:)) {
        return link.selectedTags.count > 0;
    }
    else if (action == @selector(renameTags:)) {
        return link.selectedTags.count > 0;
    }
    
    return NO;
}

// MARK: - Actions

- (void)editTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    GTAGPlugin *link = [self activeLink:editViewController];
    NSView *view = link.theView;
    NSWindow *window = view.window;
    
    [window makeFirstResponder:link.tagsField];
}

- (void)addTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    GTAGPlugin *link = [self activeLink:editViewController];
    [link promptAddTags:nil];
}

- (void)removeTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    GTAGPlugin *link = [self activeLink:editViewController];
    [link promptRemoveTags:nil];
}

- (void)renameTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    GTAGPlugin *link = [self activeLink:editViewController];
    [link promptRenameTags:nil];
}

@end
