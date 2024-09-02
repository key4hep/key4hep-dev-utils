macro(key4hep_set_compiler_flags)
  if (DEFINED KEY4HEP_SET_COMPILER_FLAGS AND NOT KEY4HEP_SET_COMPILER_FLAGS)
    return()
  endif()

  set(COMPILER_FLAGS "-fPIC -Wall -Wextra -Wpedantic -Wshadow")

  if(CMAKE_CXX_COMPILER_ID MATCHES "^(Apple)?Clang$")
    set(COMPILER_FLAGS "${COMPILER_FLAGS} -Winconsistent-missing-override -Wheader-hygiene -fcolor-diagnostics")
  elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(COMPILER_FLAGS "${COMPILER_FLAGS} -fdiagnostics-color=always")
  endif()

  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COMPILER_FLAGS}")

endmacro()

macro(key4hep_set_build_type)
  message(WARNING "CMAKE_CONFIGURATION_TYPES: ${CMAKE_CONFIGURATION_TYPES}")
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
endmacro()

macro(key4hep_set_cxx_standard)
  set(CMAKE_CXX_STANDARD 20 CACHE STRING "")

  if(NOT CMAKE_CXX_STANDARD MATCHES "20|23")
    message(FATAL_ERROR "Unsupported C++ standard: ${CMAKE_CXX_STANDARD}, supported values are 20 and 23")
  endif()

endmacro()

###################################################

key4hep_set_compiler_flags()
key4hep_set_build_type()
key4hep_set_cxx_standard()
