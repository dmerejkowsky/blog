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

In this post, we are going to use everything we learnt so far and write an iOS application able to show Chuck Norris facts.

# Introduction: cocoapods

We are going to use [cocoapods]() which is a tool that helps you manage dependencies for iOS application.

It means we can configure the Xcode projects by writing code, which is good news!

Cocoapods can be used in two modes:

First, you can run `pod lib create foo`. This will create a `Foo.podspec` file. The podspec describes how to build the `foo` library, a bit like conan recipes. You can then upload the podspec file and the associated sources to a `repository`.

Second, you can run `pod init` next to an existing Xcode project. This will create an Xcode *workspace* and a `Podfile` file. You can then edit the pod file to specify dependencies. Then, we you run `pod install`, dependencies will be fetched and the workspace will be able to build the dependencies and use them in the original Xcode project.


So, here's the plan:

* First, create a *cocoapods library* called `ChuckNorrisBindings` in `ios/bindings/ChuckNorrisBindings`.
* Then, create a blank iOS application with in the `ios/app/ChuckNorris` directory, called ChuckNorris.
* Finally, use cocoapods to create a dependency between ChuckNorrisBindings and ChuckNorris.

# The Bindings

We run `pod lib create ChuckNorrisBindings` and answer a few questions.

You will note cocoapods has created lots of files. Among them:

TODO

If we try to run the tests directly from Xcode, it won't work right away.

We have to fiddle with the files cocoapods generated for us:

TODO: screen shots about the scheme management

Now we can write tests and run them.


### Cross-compiling ChuckNorris for iOS

Our plan to bind the C++ library for iOS is a combination of techniques we already seen in [Python with cffi](), and in [Android]().

We'll cross-compile ChuckNorris as a static library from macOS to iOS. And then we'll compile the Objective-C code by giving it the paths to the `libchucknorris.a` file, the conan dependencies, and the `chucknorris.h` C header.


As we did for Android, we'll create a conan profile called `ios` and add a build dependency:

```ini
[settings]
os=iOS
os.version=9.0
arch=x86_64

[build_requires]
darwin-toolchain/1.0@theodelrieu/stable
```

As with Android, in a real project, we'll need to cross-compile for a variety of CPUs:
`x86_64` for the simulator, `armv7` and `armv8` for the real devices.
TODO: check the architecture.

We'll do that by invoking conan with the `--settings arch=<arch>` flag.

Note that this time we don't need to write the toolchain recipe ourselves, there is already one on conan-center.[^1]
TODO: Check it's the conan-center remote:

Then, as we did for Android, we run `conan create` for `sqlite3`.

```
# For sqlite3
cd conan/sqlite3
conan create . dmerej/test --profile ios --settings arch=x86_6
```

As we did for Android with the `libc++shared.so` file, we patch the ChuckNorris recipe to deal with the copies of all the `.a` files, both in the `imports()` and `package()` methods:

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

Then we can create the ChuckNorris package:

```
cd cpp/ChuckNorris
conan create . dmerej/test --profile ios --settings arch=x86_6
```

So far so good.


## The podspec

Note that all the `.a` are somewhere inside `~/.conan/data/`. Since we do not plan to edit the C++ code just yet, we can simply copy the `.a` from the package into a `out/` directory next to the bindings code.

```
mkdir -p out/
cp ~/.conan/data/.../*.a out/
```

So that we don't forget, let's add `out` to the `.gitignore`.

Next we can edit the podspec to specify:

* The include directory. It's inside a directory called `pod_target_xcconfig`.
* The "vendored" libraries: that's our `libchucknorris.a` and `libsqlite3.a`. They are called "vendored" because they won't be compiled by cocoapods itself, and are not already present on the target operating system either.

```ruby
Pod::Spec.new do |s|
  ...

  s.pod_target_xcconfig = {
    'HEADER_SEARCH_PATHS' => "${PODROOTS}/../../cpp/ChuckNorris/include/",
  }

  s.vendored_libraries = Dir["out/*.a"]
```

TODO: check PODROOTS

Two remarks:

* Since cocoapods recipes are written in Ruby, we can use the overloaded `[]` operator for `Dir` objects to get the full list of files matching the `out/*.a` *glob* pattern.
* The `HEADER_SEARCH_PATHS` string contains a `${PODROOTS}` extension, that will be set by cocoapods.

Note how it does not matter if we are building the `ChuckNorrisBindings` cocoapods library or the `ChuckNorris` application: the resulting path will be the same in both cases.

# Objective-C

Like C++, you can use C code directly in Objective-C.

It's still dangerous to expose C code directly, so here's how we can proceed:

* Write a CKChuckNorris class. (It's a convention to prefix all the classes in a pod library by the initials of the projects)
* Write a CKChuckNorris+Private categary to hide the C code from the consumers of the CKChuckNorris class.

```Objective-C
/* In CKChuckNorris.h */
TODO
```

```Objective-C
/* In CKChuckNorris.m */
TODO
```

```Objective-C
/* In CKChuckNorris+Private.h */
TODO
```

So far we have just *declared* the  `createCKPtr` and `getFactImpl` methods.

It's time to *define* them in the `CKChuckNorris+Private.m` file:

```Objective-C
/* In CKChuckNorris+Private.m */
TODO
```

Note how the *only* file that depends on the `chucknorris.h` C header file is the *private implementation* of the `CKChuckNorris` class.

That's a technique often used in C++ code too, where it's named "PIMPL" (private implementation).

TODO: check the name.

It's now time to edit the tests:

```Objective-C
/* In Tests.m */
TODO
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
- (IBAction)onClick:(id)sender {
  NSLog(@"Hello!");
}
```

OK, that works. All that's left to do is add a `CKChuckNorris*` pointer to the controller, set it in `viewDidLoad` and call the `getFact()` method when the button is clicked:

```Objective-C
- (void)viewDidLoad {
  [super viewDidLoad];
  self.ck = [[CKChuckNorris alloc] init];
}

-(IBAction)onClick:(id)sender {
  self.textView.text = [self.ck getFact];
 }
```

We can now run the application inside a simulator.

TODO: screenshot


# Dealing with the other architectures

* Run conan for armv7 and the like
* Use lipo in out/


[^1]: This recipe was written and shared by my nice colleague Théo Delrieu from [tanker.io](https://tanker.io). Say thanks!
