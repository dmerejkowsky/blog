---
authors: [dmerej]
slug: chuck-norris-part-8-ios
date: 2018-03-18T16:53:30.882200+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 8: iOS"
tags: [c++]
---

# Part 6: iOS

## The App

* Create Ojbective-C app from XCode
* Main storyboard
  * Add a Stack View
  * Add a Button

* Drag and drop (with alt) from designer to code (between @interface and @implementation) to create variables
* Drag and drop (with alt) from designer to code (after @implementation) to create handlers

## The Bindings

* Run `pod lib create ChuckNorrisBindings` and answer a few questions
* Fiddle with test scheme, and select None in the general project settings
* Can run the tests!

## What we'll need:

* chucknorris.a
* include/chucknorris.h
* and sqlite3.a

Like Python/cffi, but with cross-compiling.

## Building ChuckNorris for iOS

* Use the darwin-toolchain from The Delrieu

Create ~/.conan/profile/ios

```ini
[settings]
os=iOS
os.version=9.0
arch=x86_64

[build_requires]
darwin-toolchain/1.0@theodelrieu/stable
```

Note: we are usin x86_64 for now: it will *only* work in a simulator. But that should let us run the tests.

Export sqlite3 package:

```
cd conan/sqlite3
conan create . dmerej/test -pr ios -s arch=x86_6
```

Now we can build ChuckNorris with *exactly the same command:*

```
cd cpp/ChuckNorris
conan create . dmerej/test -pr ios -s arch=x86_6
```

After having patched the file to handle the static stuff, like we did for Android

```python
def imports():
      if self.settings.os == "Android":
          self.copy("*libc++_shared.so", dst="lib", keep_path=False)
      if self.settings.os == "iOS":
          self.copy("*.a", dst="lib", src="lib")

def package(self):
      self.copy("bin/cpp_demo", dst="bin", keep_path=False)
      self.copy("lib/*.so", dst="lib", keep_path=False)
      self.copy("lib/*.a", dst="lib", keep_path=False)
```

## The podspec

So know we specify include dirs and "vendored libs", ie libs that will *not* get built by cocapods:

```
  s.pod_target_xcconfig = {
    'HEADER_SEARCH_PATHS' => '../../../../cpp/ChuckNorris/include/'
  }

  s.vendored_libraries = Dir["out/*.a"]
```

(Ruby ftw)

## The Objective-C wrapper

Rename ReplaceMe.m into ChuckNorris.m and add ChuckNorris.h

Re-run `pod install`, easier that trying to add the files from Xcode (not kidding!)

## Link error

```
Undefined symbols for architecture x86_64:
  "operator delete(void*)", referenced from:
      _chuck_norris_version in libchucknorris.a(c_wrapper.cpp.o)
ld: symbol(s) not found for architecture x86_64
clang: error: linker command failed with exit code 1 (use -v to see invocation)
```

Or old friend the c++ library is back!

```
  s.libraries = ['c++', 'c++abi']
  s.vendored_libraries += Dir["out/*.a"]
```

## Going dirty

We'll just put the void* pointer directly in the class

```objective-c
/* in CKChuckNorris.h */
@interface CKChuckNorris: NSObject

@property void* ckPtr;
+(NSString*) versionString;

-(instancetype)init;
-(NSString*) getFact;

@end
```

```objective-c
/* in CKChuckNorris.m */
#import "CKChuckNorris.h"
#include "chucknorris.h"

@implementation CKChuckNorris

-(instancetype)init {
  self = [super init];
  self.ckPtr = chuck_norris_init();
  return self;
}

-(NSString *)getFact {
  const char* fact = chuck_norris_get_fact(self.ckPtr);
  return [NSString stringWithCString:fact encoding:NSUTF8StringEncoding];
}

+ (NSString*)versionString {
  return [NSString stringWithCString:chuck_norris_version() encoding:NSUTF8StringEncoding];
}
@end
```

Then we can patch the app:

```objective-c
 #import <UIKit/UIKit.h>
+#import "CKChuckNorris.h"

 @interface ViewController : UIViewController

+@property CKChuckNorris* ck;

 @end
```

```patch
- (IBAction)onClick:(id)sender {
-  self.textView.text = @"hello";
+  self.textView.text = [self.ck getFact];
 }

 - (void)viewDidLoad {
   [super viewDidLoad];
-  // Do any additional setup after loading the view, typically from a nib.
+  self.ck = [[CKChuckNorris alloc] init];
 }
```

Almost there:
```
Compiling CKChuckNorris.m -> fatal error: 'chucknorris.h' file not found
```
