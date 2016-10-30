+++
slug = "porting-tf2-to-visual-studio-qibuild"
date = "2016-05-06T14:40:56+00:00"
draft = true
title = "Porting tf2 to Visual Studio / qibuild"
+++

My journey to compile tf2 for Visual Sutdio

<!--more-->

For a less painful experience:

* Create a user account with no space in name
* Install python in C:\Python3 (that way:
 - no space in file name
 - no need to use --install, on Windows, C:\<whatever> is writeable
   by everyone \o/

Steps:

* compile console_bridge
  * -> write a custom console_bridge-config.cmak (upstream one sucks)
 * write a python script to run cmake with ninja
 * set CMAKE_DEBUG_POSTFIX=_d (required for qibuild)
 * set BOOST_ROOT
 * remove linux-specific stuff
 * generate console_bridge-config.cmake for qibuild (optimized, debug)

* get boost from sourceforge
  * move stuff around: 'boost' -> 'include/boost'
  * libs-32-vc140 -> 'lib'
  * mv `lib/*.dll` -> bin

* try to configure a catkin workspace
 * nice, they thought about symlink -> copy
 * catkin_find_package does not work -> it's a shebang script -> path catkin_pkg setup.py to use console entry points
```
env.bat fail
```
  -> Re-install Python in `C:\Python3`
 * `empy` not found : install it
 * boost is not found
 * set console_bridge_DIR:
 * remove everything in geometry2 but ft2_msgs and tf2
 * it configures!


* building:
 * console_bridge headers not found:
  * patch console_bridge-config.cmake to set variables that catkin expects
 * could not find libboost_system.lib: set Boost_USE_STATIC_LIBS=ON
   (life's too short ....)

```
C:\Users\dmerej\src\ros\workspace\src\geometry2\tf2\include\tf2/LinearMath/Quaternion.h(50): error C3646: '__attribute__': unknown override specifier
```
  * Again, life's too short: just remove it (after cleanup whitespace (grr))


* And now, build everything in release

* installing:
 * playing with prefix and dest dir
 * no tf2_d.lib -> they forgot to export symbols -> force static build

* using the package
 * Yet an other link error: symbol already defined in rostime -> set ROS_BUILD_SHARED_LIBS in TF2_DEFINITIONS

Trivia: In total, we've built 627 targets, and 6 .obj (much ado about nothing :)
