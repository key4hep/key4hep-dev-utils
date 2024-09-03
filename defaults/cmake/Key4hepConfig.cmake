macro(key4hep_set_compiler_flags)
  if (DEFINED KEY4HEP_SET_COMPILER_FLAGS AND NOT KEY4HEP_SET_COMPILER_FLAGS)
    return()
  endif()

  set(COMPILER_FLAGS "-fPIC -Wall -Wextra -Wpedantic -Wshadow -Wdeprecated")

  if(CMAKE_CXX_COMPILER_ID MATCHES "^(Apple)?Clang$")
    set(COMPILER_FLAGS "${COMPILER_FLAGS} -Winconsistent-missing-override -Wheader-hygiene -fcolor-diagnostics")
  elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(COMPILER_FLAGS "${COMPILER_FLAGS} -fdiagnostics-color=always")
  endif()

  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COMPILER_FLAGS}")

endmacro()

macro(key4hep_set_build_type)

  # For ccmake and cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "None" "Debug" "Release" "MinSizeRel" "RelWithDebInfo")

  if(NOT CMAKE_CONFIGURATION_TYPES)
    if(NOT CMAKE_BUILD_TYPE)
      set(CMAKE_BUILD_TYPE RelWithDebInfo
        CACHE STRING "Choose the type of build, options are: None, Release, MinSizeRel, Debug, RelWithDebInfo (default)"
        FORCE
        )
    else()
      set(CMAKE_BUILD_TYPE "${CMAKE_BUILD_TYPE}"
        CACHE STRING "Choose the type of build, options are: None, Release, MinSizeRel, Debug, RelWithDebInfo (default)"
        FORCE
        )
    endif()
  endif()
endmacro()

macro(key4hep_set_cxx_standard_and_extensions)
  set(CMAKE_CXX_STANDARD 20 CACHE STRING "")

  if(NOT CMAKE_CXX_STANDARD MATCHES "20|23")
    message(FATAL_ERROR "Unsupported C++ standard: ${CMAKE_CXX_STANDARD}, supported values are 20 and 23")
  endif()

  set(CMAKE_CXX_STANDARD_REQUIRED ON)
  set(CMAKE_CXX_EXTENSIONS OFF)

endmacro()

macro(key4hep_set_rpath)
  #  When building, don't use the install RPATH already (but later on when installing)
  set(CMAKE_SKIP_BUILD_RPATH FALSE)         # don't skip the full RPATH for the build tree
  set(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE) # use always the build RPATH for the build tree
  set(CMAKE_MACOSX_RPATH TRUE)              # use RPATH for MacOSX
  set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE) # point to directories outside the build tree to the install RPATH

  # Check whether to add RPATH to the installation (the build tree always has the RPATH enabled)
  if(APPLE)
    set(CMAKE_INSTALL_NAME_DIR "@rpath")
    set(CMAKE_INSTALL_RPATH "@loader_path/../lib")    # self relative LIBDIR
    # the RPATH to be used when installing, but only if it's not a system directory
    list(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${CMAKE_INSTALL_PREFIX}/lib" isSystemDir)
    if("${isSystemDir}" STREQUAL "-1")
      set(CMAKE_INSTALL_RPATH "@loader_path/../lib")
    endif("${isSystemDir}" STREQUAL "-1")
  elseif(DEFINED KEY4HEP_SET_RPATH AND NOT KEY4HEP_SET_RPATH)
    set(CMAKE_SKIP_INSTALL_RPATH TRUE)           # skip the full RPATH for the install tree
  else()
    set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${LIBDIR}") # install LIBDIR
    # the RPATH to be used when installing, but only if it's not a system directory
    list(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${CMAKE_INSTALL_PREFIX}/lib" isSystemDir)
    if("${isSystemDir}" STREQUAL "-1")
      set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${LIBDIR}")
    endif("${isSystemDir}" STREQUAL "-1")
  endif()
endmacro()

###################################################

key4hep_set_compiler_flags()
key4hep_set_build_type()
key4hep_set_cxx_standard_and_extensions()
key4hep_set_rpath()
