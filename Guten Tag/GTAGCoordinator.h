//
//  GTAGCoordinator.h
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
#import <GlyphsCore/GSFont.h>
#import <GlyphsCore/GSGlyphViewControllerProtocol.h>
#import <GlyphsCore/GSCallbackHandler.h>
#import <GlyphsCore/GSShortcutCommandProtocol.h>
#import "GTAGPlugin.h"

NS_ASSUME_NONNULL_BEGIN

@class GTAGPlugin;

typedef NSDictionary<NSString *, NSNumber *> GTAGShortcut;

@interface GTAGCoordinator : NSObject<GSShortcutCommandProtocol>

+ (instancetype)sharedCoordinator;

@property (strong, nonatomic, nullable) GTAGShortcut *editTagsShortcut;
@property (strong, nonatomic, nullable) GTAGShortcut *addTagsShortcut;
@property (strong, nonatomic, nullable) GTAGShortcut *removeTagsShortcut;
@property (strong, nonatomic, nullable) GTAGShortcut *renameTagsShortcut;

- (void)link:(GTAGPlugin *)link;
- (void)unlink:(GTAGPlugin *)link;

@end

NS_ASSUME_NONNULL_END
