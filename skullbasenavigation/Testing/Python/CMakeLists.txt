# Register the unittest subclass in the main script as a ctest.
# Note that the test will also be available at runtime.
#slicer_add_python_unittest(SCRIPT testing_slicer_functions.py SLICER_ARGS --additional-module-path ${DEPENDENCIES_ADDITIONAL_MODULE_PATHS} )
slicer_add_python_unittest(SCRIPT testing_slicer_functions.py)
