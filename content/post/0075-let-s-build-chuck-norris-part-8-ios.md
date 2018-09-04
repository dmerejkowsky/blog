---
authors: [dmerej]
slug: chuck-norris-part-8-ios
date: 2018-09-03T16:53:30.882200+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 8: Using C++ in an iOS application"
tags: [c++]
---

_Note: This is part 8 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._

If you came this far after reading part 1 to 7, congrats!

In this article, we'll use everything we learnt so far and write an iOS application able to show Chuck Norris facts. We'll also learn a few things specific to iOS and Xcode. Let's dive in!

# Introduction: CocoaPods

There are many ways to achieve our goal. Several tools exist, but for this post we'll concentrate on [CocoaPods](https://cocoapods.org). [^1]

It means we can configure the Xcode projects by writing code, which is good news!

CocoaPods can be used in two modes:

First, you can run `pod lib create foo`. This will create a `Foo.podspec` file. The *podspec* describes how to build the `foo` library, a bit like a Conan recipe. You can then upload the podspec file and the associated sources to a *repository*.

Second, you can run `pod init` next to an existing Xcode project. This will create an Xcode *workspace* and a `Podfile` file. You can secify one or several dependencies in the Podfile. Then, when you run `pod install`, the podspecs will be fetched and the workspace will be configured so that you can build and use those dependencies in the original Xcode project.

So, here's the plan:

* Create a *CocoaPods library* called `ChuckNorrisBindings` in `ios/bindings/ChuckNorrisBindings`.
* Create a blank iOS application with in the `ios/app/ChuckNorris` directory, called ChuckNorris.
* Use CocoaPods to create a dependency between ChuckNorrisBindings and ChuckNorris.

# The Bindings

We run `pod lib create ChuckNorrisBindings` and answer a few questions:

```
$ pod lib create ChuckNorrisBindings
Cloning `https://github.com/CocoaPods/pod-template.git` into `ChuckNorrisBindings`.
...
What platform do you want to use? [ iOS / macOS ]
> ios
What language do you want to use? [ Swift / ObjC ]
> ObjC
Would you like to include a demo application with your library? [ Yes / No ]
> No
Which testing frameworks will you use? [ Specta / Kiwi / None ]
> Specta
Would you like to do view based testing? [ Yes / No ]
> No
What is your class prefix?
CK
...
Running pod install on your new library.
...
Analyzing dependencies
Fetching podspec for `ChuckNorrisBindings` from `../`
Setting up CocoaPods master repo
...
 Ace! you're ready to go!
 We will start you off by opening your project in Xcode
  open 'ChuckNorrisBindings/Example/ChuckNorrisBindings.xcworkspace'
```

You will note CocoaPods has created lots of files. Among them:

* `ChuckNorrisBindings/Sources`: the sources of the library.
* `ChuckNorrisBindings.podspec`: the podspec used to build and use the ChuckNorrisBindings library
* `Example/ChuckNorrisBindings.xcodeproj` the Xcode project to build the sources
* `Example/ChuckNorrisBindings.xcworkspace` the Xcode workspace which we can use to:
    * build the library
    * build the test framework
    * build and run the tests themselves.

If we try to run the tests directly from Xcode, it won't work right away, instead we get this error message:

```
Scheme "Pods-ChuckNorrisBindings_Tests" is not configured for testing. Edit the scheme to enable testing, or cancel the action
```

We have to fiddle with the schemes CocoaPods generated for us:

Open the shceme editor:

![edit the testing scheme](/pics/xcode/manage-schemes.png)

Show the test scheme:

![show test scheme](/pics/xcode/show-test-scheme.png)

Click the `+` bottom at the bottom and select the test target.

![choose the test target](/pics/xcode/choose-test-target.png)

This time we get an other error message:

```
Could not find test host for ChuckNorrisBindings_Tests ...
```

Edit the project settings, under "General" and switch the Host application form "Custom" to "None":

![select test host](/pics/xcode/select-test-host-app.png)

And it works: a simulator is started and the tests run.


### Cross-compiling ChuckNorris for iOS

Our plan to bind the C++ library for iOS is a combination of techniques we already seen in *[Part 5: Python with cffi]({{< ref "post/0065-let-s-build-chuck-norris-part-5-python-and-cffi.md" >}})* and *[Part 6: Android and JNA]({{< ref "post/0074-let-s-build-chuck-norris-part-7-android-jna.md" >}})*.
We'll cross-compile ChuckNorris as a static library from macOS to iOS. And then we'll compile the Objective-C code by giving it the paths to the `libchucknorris.a` file, the conan dependencies, and the `chucknorris.h` C header.


Let's create a conan profile called `ios` and add a build dependency:

```ini
# In ~/.conan/profiles/ios
[settings]
os=iOS
os.version=9.0
arch=x86_64

[build_requires]
darwin-toolchain/1.0@theodelrieu/stable
```

For now, we've hard-coded the x86_64 architecture, because we'll run everything in simulators, and Xcode simulators need the x86_64 architecture. In order to run the code on actual devices, we'll invoke conan with the correct `--settings arch=<arch>` flag. This is similar to what we did in Part 6.

Note that this time we don't need to write the toolchain recipe ourselves, there is already one on conan-center.[^2]

Then, as we did for Android, we run `conan create` for `sqlite3`.

```bash
cd conan/sqlite3
conan create . dmerej/test --profile ios --settings arch=x86_64
```

As we did for Android with the `libc++shared.so` file, we patch the ChuckNorris recipe to deal with the copies of all the `.a` files, both in the `imports()` and `package()` methods:

{{< highlight python "hl_lines=2-5 10" >}}
def imports():
      if self.settings.os == "Android":
          self.copy("*libc++_shared.so", dst="lib", keep_path=False)
      if self.settings.os == "iOS":
          self.copy("*.a", dst="lib", src="lib")

def package(self):
      self.copy("bin/cpp_demo", dst="bin", keep_path=False)
      self.copy("lib/*.so", dst="lib", keep_path=False)
      self.copy("lib/*.a", dst="lib", keep_path=False)
{{</ highlight >}}

Then we can create the ChuckNorris package:

```
cd cpp/ChuckNorris
conan create . dmerej/test --profile ios --settings arch=x86_6
```

So far so good.


## The podspec

Note that all the `.a` are somewhere inside `~/.conan/data/`. Let's copy all the `a` into a `nativelibs/x86_64` directory next to the bindings code:

```
mkdir -p nativelibs/x86_64/
cp ~/.conan/data/.../*.a nativelibs/x86_64/
```

So that we don't forget, let's add `nativelibs` to the `.gitignore`.

Next we can edit the podspec to specify:

* The include directory. It's inside a directory called `pod_target_xcconfig`.
* The *vendored* libraries: that's our `libchucknorris.a` and `libsqlite3.a`. They are called "vendored" because they won't be compiled by CocoaPods itself, and are not already present on the target operating system either.

```ruby
Pod::Spec.new do |s|
  ...

  s.pod_target_xcconfig = {
    'HEADER_SEARCH_PATHS' => "${POD_ROOTS}/../../cpp/ChuckNorris/include/",
  }

  s.vendored_libraries = Dir["out/*.a"]
```

Two remarks:

* Since CocoaPods recipes are written in Ruby, we can use the overloaded `[]` operator for `Dir` objects to get the full list of files matching the `out/*.a` *glob* pattern.
* The `HEADER_SEARCH_PATHS` string contains a `${POD_ROOTS}` extension, that will be set by CocoaPods.

Note how it does not matter if we are building the `ChuckNorrisBindings` CocoaPods library or the `ChuckNorris` application: the resulting `HEADER_SEARCH_PATHS` will be the same.

# Objective-C

Like C++, you can use C code directly in Objective-C.

It's still dangerous to expose C code directly, so here's how we can proceed:

* Write a CKChuckNorris class. (It's a convention to prefix all the classes in a pod library by the initials of the projects)
* Write a CKChuckNorris+Private categary to hide the C code from the consumers of the CKChuckNorris class.

```Objective-C
/* In CKChuckNorris.h */
@interface CKChuckNorris: NSObject

@property void* ckPtr;

-(instancetype)init;
-(NSString*) getFact;

// TODO: deinit!

@end
```

```Objective-C
/* In CKChuckNorris.m */
#import "CKChuckNorris.h"
#include "CKChuckNorris+Private.m"

@implementation CKChuckNorris

-(instancetype)init {
  self = [super init];
  return [self createCkPtr];
}

-(NSString *)getFact {
  return [self getFactImpl];
}

@end
```

```Objective-C
/* In CKChuckNorris+Private.h */
#import "CKChuckNorris.h"

@interface CKChuckNorris (Private)

-(instancetype) createCkPtr;
-(NSString*) getFactImpl;

@end
```

So far we have just *declared* the  `createCKPtr` and `getFactImpl` methods.

It's time to *define* them in the `CKChuckNorris+Private.m` file:

```Objective-C
/* In CKChuckNorris+Private.m */
#import "CKChuckNorris+Private.h"

#include "chucknorris.h"   // <- Our C header file

@implementation CKChuckNorris (Private)

-(instancetype)createCkPtr  {
  self.ckPtr = chuck_norris_init();
  return self;
}

-(NSString*)getFactImpl {
  const char* fact = chuck_norris_get_fact(self.ckPtr);
  return [NSString stringWithCString:fact encoding:NSUTF8StringEncoding];
}
@end
```

Note how the *only* file that depends on the `chucknorris.h` C header file is the *private implementation* of the `CKChuckNorris` class.

There's a similar technique known as "PIMPL" (pointer to implementation) you can use in C++ code to achieve the same kind of isolation.


It's now time to edit the tests:

```Objective-C
/* In Tests.m */
describe(@"ChuckNorris", ^{

  it(@"can get version", ^{
    expect([CKChuckNorris versionString]).to.equal(@"0.1");
  });

  it(@"can get a fact", ^{
    CKChuckNorris* ck = [[CKChuckNorris alloc] init];
    NSString* fact = [ck getFact];
    expect(fact).toNot.beEmpty();
    NSLog(@"Got fact: %@", fact);
  });


});
```

And see if they pass:

```
Undefined symbols for architecture x86_64:
  "operator delete(void*)", referenced from:
      _chuck_norris_version in libchucknorris.a(c_wrapper.cpp.o)
ld: symbol(s) not found for architecture x86_64
clang: error: linker command failed with exit code 1 (use -v to see invocation)
```

Whoops, we forgot to add the dependency to the C++ library. It's less hard than in the Android case, since they always have the same name for iOS:

```ruby
Pod::Spec.new do |s|
  ...

  s.vendored_libraries = ...
  s.libraries = ['c++', 'c++abi']
end
```

`libc++` and `libc++abi` are found on the target operating system, hence we use the `libraries` variable.

We can now try again, and this time the tests pass \o/.

# The GUI

We create the Objective-C application from Xcode.

TODO: screenshot

Then we edit the main storyboard to add a stack view and a button.

We drag and drop the components from the designer view to the code, while keeping the `alt` key pressed.

TODO: screenshot

For now, we'll just set the text view to the string `Hello` when the button is clicked:

```objective-c
/* In ViewController.m */
- (IBAction)onClick:(id)sender {
  self.textView.text = @"Hello";
}
```

OK, that works.

Now we can run `pod init` and patch the Podfile:

```ruby
target 'ChuckNorris' do
  pod 'ChuckNorrisBindings', :path => '../bindings/'
end
```

We took a small shortcut here. Rather than deploying the ChuckNorrisBindings to a spec repository, we just tell the Podfile to get the podspec directly from the file system.

Let's check this works:

```
$ cd ios/app
$ pod update
TODO: pod update output
```

Looks OK.

All that's left to do is add a `CKChuckNorris*` pointer to the controller, set it in `viewDidLoad` and call the `getFact()` method when the button is clicked:

{{< highlight objective-c "hl_lines=3 7" >}}
/* In ViewController.h */
#import <UIKit/UIKit.h>
#import "CKChuckNorris.h"

@interface ViewController : UIViewController

@property CKChuckNorris* ck;

@end
{{</ highlight >}}

{{< highlight objective-c "hl_lines=2-3 7" >}}
- (void)viewDidLoad {
  [super viewDidLoad];
  self.ck = [[CKChuckNorris alloc] init];
}

-(IBAction)onClick:(id)sender {
  self.textView.text = [self.ck getFact];
 }
{{</ highlight >}}

We can now run the application inside a simulator.

TODO: screenshot


# Dealing with the other architectures

* Run conan for armv7 and the like
* Use lipo in out/


[^1]: I heard Carthage is also a good option. Did not try it, though.
[^2]: This recipe was written and shared by my nice colleague Théo Delrieu from [tanker.io](https://tanker.io). Say thanks!
