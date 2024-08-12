macro(key4hep_set_compiler_flags)
  if (DEFINED KEY4HEP_SET_COMPILER_FLAGS AND NOT KEY4HEP_SET_COMPILER_FLAGS)
    return()
  endif()

  set(COMPILER_FLAGS "-fPIC -Wall -Wextra -Wpedantic -Wshadow")

  if(CMAKE_CXX_COMPILER_ID MATCHES "^(Apple)?Clang$")
    set (COMPILER_FLAGS "${COMPILER_FLAGS} -Winconsistent-missing-override -Wheader-hygiene -fcolor-diagnostics")
  elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set (COMPILER_FLAGS "${COMPILER_FLAGS} -fdiagnostics-color=always")
  endif()

  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COMPILER_FLAGS}")

endmacro()


###################################################

key4hep_set_compiler_flags()

if(NOT CMAKE_CONFIGURATION_TYPES)
  if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE RelWithDebInfo
      CACHE STRING "Choose the type of build, options are: None Release MinSizeRel Debug RelWithDebInfo"
      FORCE
      )
  else()
    set(CMAKE_BUILD_TYPE "${CMAKE_BUILD_TYPE}"
      CACHE STRING "Choose the type of build, options are: None Release MinSizeRel Debug RelWithDebInfo"
      FORCE
      )
  endif()
endif()
