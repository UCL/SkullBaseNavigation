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
set(Slicer_DIR "/usr/src/Slicer-build/Slicer-build" )

find_package(Slicer REQUIRED)

set(DEPENDENCIES_ADDITIONAL_MODULE_PATHS "")
list(APPEND DEPENDENCIES_ADDITIONAL_MODULE_PATHS "/usr/src/SlicerOpenIGTLink/build/inner-build/lib/Slicer-4.10/qt-loadable-modules")
list(APPEND DEPENDENCIES_ADDITIONAL_MODULE_PATHS "/usr/src/SlicerOpenIGTLink/build/inner-build/lib/Slicer-4.10/qt-scripted-modules")
list(APPEND DEPENDENCIES_ADDITIONAL_MODULE_PATHS "/usr/src/SlicerIGT/build/lib/Slicer-4.10/qt-loadable-modules")
list(APPEND DEPENDENCIES_ADDITIONAL_MODULE_PATHS "/usr/src/SlicerIGT/build/lib/Slicer-4.10/qt-scripted-modules")

include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(skullbasenavigation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
