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

// Key-Value Coding
static void * const GTAGCoordinatorKVOContext = (void*)&GTAGCoordinatorKVOContext;
static NSString * const kUserDefaultsControllerKeyPrefix = @"values.";
static NSString * const kUserDefaultsShortcutKeyEquivalentsKey = @"GSCommandKeyEquivalents";
// Shortcuts
static NSString * const kShortcutGroupTitle = @"Guten Tag";
static NSString * const kShortcutKeyCodeKey = @"keycode";
static NSString * const kShortcutModifierFlagsKey = @"modifierFlags";
// Shortcut Commands
static NSString * const kEditTagsShortcutIdentifier = @"com.FlorianPircher.GutenTag.EditTags";
static NSString * const kAddTagsShortcutIdentifier = @"com.FlorianPircher.GutenTag.AddTags";
static NSString * const kRemoveTagsShortcutIdentifier = @"com.FlorianPircher.GutenTag.RemoveTags";
static NSString * const kRenameTagsShortcutIdentifier = @"com.FlorianPircher.GutenTag.RenameTags";
// Events
const NSUInteger kEventModifierKeyFlagsMask = NSEventModifierFlagShift|NSEventModifierFlagControl|NSEventModifierFlagOption|NSEventModifierFlagCommand;
// Shared
static NSBundle *bundle;

BOOL isEmptyShortcut(GTAGShortcut *shortcut) {
    return shortcut[kShortcutKeyCodeKey].unsignedShortValue == 0xFFFF
        && shortcut[kShortcutModifierFlagsKey].unsignedLongValue == 0xFFFF;
}

@implementation GTAGCoordinator {
    NSMapTable *links;
    NSMutableSet<NSString *> *monitoredShortcutIdentifers;
    id eventMonitorHandle;
}

+ (void)initialize {
    bundle = [NSBundle bundleForClass:self.class];
}

+ (instancetype)sharedCoordinator {
    static GTAGCoordinator *sharedCoordinatorInstance = nil;
    static dispatch_once_t onceToken;
    
    dispatch_once(&onceToken, ^{
        sharedCoordinatorInstance = [self new];
    });
    
    return sharedCoordinatorInstance;
}

- (GTAGShortcut *)updateShortcut:(GTAGShortcut *)shortcut oldValue:(GTAGShortcut *)oldShortcut forShortcutIdentifier:(NSString *)identifer {
    if (shortcut == oldShortcut || [shortcut isEqual:oldShortcut]) {
        return oldShortcut;
    }
    
    if (shortcut != nil && !isEmptyShortcut(shortcut)) {
        [monitoredShortcutIdentifers addObject:identifer];
        
        if (eventMonitorHandle == nil && monitoredShortcutIdentifers.count > 0) {
            eventMonitorHandle = [NSEvent addLocalMonitorForEventsMatchingMask:NSEventMaskKeyDown handler:^NSEvent * _Nullable(NSEvent * _Nonnull event) {
                unsigned short keyCode = event.keyCode;
                NSEventModifierFlags modifierFlags = event.modifierFlags & kEventModifierKeyFlagsMask;
                
                GTAGShortcut *editTagsShortcut = self.editTagsShortcut;
                GTAGShortcut *addTagsShortcut = self.addTagsShortcut;
                GTAGShortcut *removeTagsShortcut = self.removeTagsShortcut;
                GTAGShortcut *renameTagsShortcut = self.renameTagsShortcut;
                
                if ([self->monitoredShortcutIdentifers containsObject:kEditTagsShortcutIdentifier]
                    && editTagsShortcut != nil
                    && editTagsShortcut[kShortcutKeyCodeKey].unsignedShortValue == keyCode
                    && editTagsShortcut[kShortcutModifierFlagsKey].unsignedLongValue == modifierFlags
                    && [self editTagsForWindow:NSApp.keyWindow]) {
                    return nil;
                }
                else if ([self->monitoredShortcutIdentifers containsObject:kAddTagsShortcutIdentifier]
                         && addTagsShortcut != nil
                         && addTagsShortcut[kShortcutKeyCodeKey].unsignedShortValue == keyCode
                         && addTagsShortcut[kShortcutModifierFlagsKey].unsignedLongValue == modifierFlags
                         && [self addTagsForWindow:NSApp.keyWindow]) {
                    return nil;
                }
                else if ([self->monitoredShortcutIdentifers containsObject:kRemoveTagsShortcutIdentifier]
                         && removeTagsShortcut != nil
                         && removeTagsShortcut[kShortcutKeyCodeKey].unsignedShortValue == keyCode
                         && removeTagsShortcut[kShortcutModifierFlagsKey].unsignedLongValue == modifierFlags
                         && [self removeTagsForWindow:NSApp.keyWindow]) {
                    return nil;
                }
                else if ([self->monitoredShortcutIdentifers containsObject:kRenameTagsShortcutIdentifier]
                         && renameTagsShortcut != nil
                         && renameTagsShortcut[kShortcutKeyCodeKey].unsignedShortValue == keyCode
                         && renameTagsShortcut[kShortcutModifierFlagsKey].unsignedLongValue == modifierFlags
                         && [self renameTagsForWindow:NSApp.keyWindow]) {
                    return nil;
                }
                
                return event;
            }];
        }
    }
    else {
        [monitoredShortcutIdentifers removeObject:identifer];
        
        if (monitoredShortcutIdentifers.count == 0 && eventMonitorHandle != nil) {
            [NSEvent removeMonitor:eventMonitorHandle];
            eventMonitorHandle = nil;
        }
    }
    
    return shortcut;
}

- (void)setEditTagsShortcut:(GTAGShortcut *)editTagsShortcut {
    _editTagsShortcut = [self updateShortcut:editTagsShortcut
                                    oldValue:_editTagsShortcut
                       forShortcutIdentifier:kEditTagsShortcutIdentifier];
}

- (void)setAddTagsShortcut:(GTAGShortcut *)addTagsShortcut {
    _addTagsShortcut = [self updateShortcut:addTagsShortcut
                                   oldValue:_addTagsShortcut
                      forShortcutIdentifier:kAddTagsShortcutIdentifier];
}

- (void)setRemoveTagsShortcut:(GTAGShortcut *)removeTagsShortcut {
    _removeTagsShortcut = [self updateShortcut:removeTagsShortcut
                                      oldValue:_removeTagsShortcut
                         forShortcutIdentifier:kRemoveTagsShortcutIdentifier];
}

- (void)setRenameTagsShortcut:(GTAGShortcut *)renameTagsShortcut {
    _renameTagsShortcut = [self updateShortcut:renameTagsShortcut
                                      oldValue:_renameTagsShortcut
                         forShortcutIdentifier:kRenameTagsShortcutIdentifier];
}

- (void)reloadShortcuts:(NSDictionary<NSString *, GTAGShortcut *> *)shortcuts {
    if (shortcuts != nil) {
        self.editTagsShortcut = shortcuts[kEditTagsShortcutIdentifier];
        self.addTagsShortcut = shortcuts[kAddTagsShortcutIdentifier];
        self.removeTagsShortcut = shortcuts[kRemoveTagsShortcutIdentifier];
        self.renameTagsShortcut = shortcuts[kRenameTagsShortcutIdentifier];
    }
    else {
        self.editTagsShortcut = nil;
        self.addTagsShortcut = nil;
        self.removeTagsShortcut = nil;
        self.renameTagsShortcut = nil;
    }
}

- (instancetype)init
{
    self = [super init];
    
    if (self) {
        links = [NSMapTable weakToStrongObjectsMapTable];
        monitoredShortcutIdentifers = [NSMutableSet new];
        eventMonitorHandle = nil;
        
        NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
        NSDictionary<NSString *, GTAGShortcut *> *shortcuts = [defaults dictionaryForKey:kUserDefaultsShortcutKeyEquivalentsKey];
        [self reloadShortcuts:shortcuts];
        
        [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Edit Tags", nil, bundle, @"Name of an action to start editing a text field containing tags")
                                             group:kShortcutGroupTitle
                                        identifier:kEditTagsShortcutIdentifier
                                            action:@selector(editTags:)
                                            target:self
                                         character:@""
                                     modifierFlags:0];
        
        [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Add Tags", nil, bundle, @"Shortcut command name for adding tags to the selected glyphs")
                                             group:kShortcutGroupTitle
                                        identifier:kAddTagsShortcutIdentifier
                                            action:@selector(addTags:)
                                            target:self
                                         character:@""
                                     modifierFlags:0];
        
        [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Remove Tags", nil, bundle, @"Shortcut command name for removing tags from the selected glyphs")
                                             group:kShortcutGroupTitle
                                        identifier:kRemoveTagsShortcutIdentifier
                                            action:@selector(removeTags:)
                                            target:self
                                         character:@""
                                     modifierFlags:0];
        
        [GSCallbackHandler registerShortcutCommand:NSLocalizedStringFromTableInBundle(@"Rename Tags", nil, bundle, @"Name of an action to rename a tag for a set of glyphs")
                                             group:kShortcutGroupTitle
                                        identifier:kRenameTagsShortcutIdentifier
                                            action:@selector(renameTags:)
                                            target:self
                                         character:@""
                                     modifierFlags:0];
        
        NSUserDefaultsController *defaultsController = NSUserDefaultsController.sharedUserDefaultsController;
        NSString *keyEquivalentsKeyPath = [kUserDefaultsControllerKeyPrefix stringByAppendingString:kUserDefaultsShortcutKeyEquivalentsKey];
        [defaultsController addObserver:self
                             forKeyPath:keyEquivalentsKeyPath
                                options:0
                                context:GTAGCoordinatorKVOContext];
    }
    
    return self;
}

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    if (context == GTAGCoordinatorKVOContext) {
        if (![keyPath hasPrefix:kUserDefaultsControllerKeyPrefix]) {
            return;
        }
        
        NSString *defaultsKey = [keyPath substringFromIndex:kUserDefaultsControllerKeyPrefix.length];
        NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
        
        if ([defaultsKey isEqualToString:kUserDefaultsShortcutKeyEquivalentsKey]) {
            NSDictionary<NSString *, GTAGShortcut *> *shortcuts = [defaults dictionaryForKey:kUserDefaultsShortcutKeyEquivalentsKey];
            [self reloadShortcuts:shortcuts];
        }
    } else {
        [super observeValueForKeyPath:keyPath ofObject:object change:change context:context];
    }
}

// MARK: - Linking

- (void)link:(GTAGPlugin *)link {
    [links setObject:NSNull.null forKey:link];
}

- (void)unlink:(GTAGPlugin *)link {
    [links removeObjectForKey:link];
}

// MARK: - Dispatch

- (nullable NSWindow *)windowForEditViewController:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    GSFont *font = editViewController.representedObject;
    GSDocument *document = font.parent;
    return document.windowController.window;
}

- (nullable GTAGPlugin *)linkForActiveWindow:(NSWindow *)activeWindow {
    if (activeWindow == nil) return nil;
    
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
    NSWindow *window = [self windowForEditViewController:editViewController];
    return [self validateShortcutCommand:action window:window];
}

- (BOOL)validateShortcutCommand:(SEL)action window:(NSWindow *)window {
    GTAGPlugin *link = [self linkForActiveWindow:window];
    
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

// MARK: - Shortcuts

- (void)editTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    NSWindow *window = [self windowForEditViewController:editViewController];
    [self editTagsForWindow:window];
}

- (void)addTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    NSWindow *window = [self windowForEditViewController:editViewController];
    [self addTagsForWindow:window];
}

- (void)removeTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    NSWindow *window = [self windowForEditViewController:editViewController];
    [self removeTagsForWindow:window];
}

- (void)renameTags:(NSViewController<GSGlyphEditViewControllerProtocol> *)editViewController {
    NSWindow *window = [self windowForEditViewController:editViewController];
    [self renameTagsForWindow:window];
}

// MARK: - Actions

- (BOOL)editTagsForWindow:(NSWindow *)window {
    if (![self validateShortcutCommand:@selector(editTags:) window:window]) {
        return NO;
    }
    GTAGPlugin *link = [self linkForActiveWindow:window];
    [window makeFirstResponder:link.tagsField];
    return YES;
}

- (BOOL)addTagsForWindow:(NSWindow *)window {
    if (![self validateShortcutCommand:@selector(addTags:) window:window]) {
        return NO;
    }
    GTAGPlugin *link = [self linkForActiveWindow:window];
    [link promptAddTags:nil];
    return YES;
}

- (BOOL)removeTagsForWindow:(NSWindow *)window {
    if (![self validateShortcutCommand:@selector(removeTags:) window:window]) {
        return NO;
    }
    GTAGPlugin *link = [self linkForActiveWindow:window];
    [link promptRemoveTags:nil];
    return YES;
}

- (BOOL)renameTagsForWindow:(NSWindow *)window {
    if (![self validateShortcutCommand:@selector(renameTags:) window:window]) {
        return NO;
    }
    GTAGPlugin *link = [self linkForActiveWindow:window];
    [link promptRenameTags:nil];
    return YES;
}

@end
