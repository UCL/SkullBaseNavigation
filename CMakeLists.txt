cmake_minimum_required(VERSION 3.9)

project(SkullBaseNavigationTesting)

#-----------------------------------------------------------------------------
# Extension meta-information
# set(EXTENSION_HOMEPAGE "https://github.com/XX")
# set(EXTENSION_CATEGORY "XX")
# set(EXTENSION_CONTRIBUTORS "XX")
# set(EXTENSION_DESCRIPTION "XX")
# set(EXTENSION_ICONURL "https://XX")
# set(EXTENSION_SCREENSHOTURLS "XX")

#-----------------------------------------------------------------------------
# Extension dependencies
set(Slicer_DIR "/Users/rolandguichard/Desktop/SkullProject/Slicer/Slicer-SuperBuild/Slicer-build" )

find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(skullbasenavigation/sbn)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
