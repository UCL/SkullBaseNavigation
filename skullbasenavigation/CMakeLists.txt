#-----------------------------------------------------------------------------
set(MODULE_NAME skullbasenavigation)
set(LIB_NAME sbn)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
#  ${MODULE_NAME}.py
  ${LIB_NAME}/__init__.py
  ${LIB_NAME}/functions.py
  ${LIB_NAME}/workflow.py
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
#  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as  a ctest.
  # Note that the test will also be available at runtime.
  # slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
