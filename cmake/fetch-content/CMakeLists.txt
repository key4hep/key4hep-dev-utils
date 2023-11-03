set(pkgs EDM4HEP)

cmake_minimum_required(VERSION 3.12 FATAL_ERROR)
project(key4hep-build VERSION 1.0.0)
include(FetchContent)

option(ENV_CHECK "Check if there are paths to the new packages in the environment variables" ON)

set(env_variables
    PATH
    LD_LIBRARY_PATH
    PYTHONPATH
    ROOT_INCLUDE_PATH
    CMAKE_PREFIX_PATH
)

# Check if the environment variables contain paths to the packages we are compiling
# If ENV_CHECK is disabled, remove them from the env variables for the current cmake run
foreach(env_var ${env_variables})
    string(REGEX REPLACE ":" ";" current_env_var "$ENV{${env_var}}")
    foreach(pkg ${pkgs})
        string(TOLOWER ${pkg} pkg_lowercase)
        if ("${current_env_var}" MATCHES "/${pkg_lowercase}/")
            if (ENV_CHECK)
                message(FATAL_ERROR "The environment variable ${env_var} contains a path to ${pkg_lowercase}. Remove it from ${env_var} or run cmake with -DENV_CHECK=OFF at your own risk.")
            else()
                message(WARNING "The environment variable ${env_var} contains a path to ${pkg_lowercase}. This may cause issues.")
                list(FILTER current_env_var EXCLUDE REGEX "/${pkg_lowercase}/")
            endif()
        endif()
    endforeach()
    string(REGEX REPLACE ";" ":" current_env_var "${current_env_var}")
    set(ENV{${env_var}} "${current_env_var}")
endforeach()

# Create symlinks to each package so that it's possible to do
# `cd <pkg> && ctest`
foreach(pkg ${pkgs})
    string(TOLOWER ${pkg} pkg_lowercase)

    execute_process(
        COMMAND ${CMAKE_COMMAND} -E create_symlink ${CMAKE_BINARY_DIR}/_deps/${pkg_lowercase}-build ${pkg}
    )
endforeach()

# Delete .cmake files to avoid issues when packages are found in the installation paths
# and then many if not all targets are dropped, causing recompilations not to work anymore
# Set the directory to search for PKGConfig files
set(pkgconfig_dir ${CMAKE_INSTALL_PREFIX})

# Find all PKGConfig.cmake and PKGConfigVersion.cmake files recursively
file(GLOB_RECURSE pkgconfig_files "${pkgconfig_dir}/*Config.cmake" "${pkgconfig_dir}/*ConfigVersion.cmake")

# Delete all found PKGConfig files
foreach(pkgconfig_file ${pkgconfig_files})
    foreach(pkg ${pkgs})
        # Convert package name to lowercase
        string(TOLOWER ${pkg} pkg_lowercase)
        string(TOLOWER ${pkgconfig_file} pkgconfig_file_lowercase)
        # Delete the file if it is in the package directory
        if(${pkgconfig_file_lowercase} MATCHES "${pkg_lowercase}")
            message(STATUS "Deleting ${pkgconfig_file}")
            file(REMOVE ${pkgconfig_file})
        endif()
    endforeach()
endforeach()

# Creating a symbolic link in _deps/ExternalData works for builds that use symbolic links
# Create the _deps folder if it doesn't exist
execute_process(
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/_deps
)
# For builds that don't use symbolic links, create build/_deps since for some reason test files
# appear there
execute_process(
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/build/_deps
)
# Create a symbolic link for when using the cmake ExternalData to manage
# downloading test data
execute_process(
    COMMAND ${CMAKE_COMMAND} -E create_symlink ${CMAKE_BINARY_DIR}/ExternalData ${CMAKE_BINARY_DIR}/_deps/ExternalData
)
# Also create it at the top directory (for builds that don't use symbolic links)
execute_process(
    COMMAND ${CMAKE_COMMAND} -E create_symlink ${CMAKE_BINARY_DIR}/ExternalData ${CMAKE_SOURCE_DIR}/ExternalData
)

set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/install")
# Needed for being able to recompile as many PACKAGE_DIR variables will be set to the install path
# and cmake will look there for the .cmake files instead of in the build directory
# set(ILCSOFT_CMAKE_MODULES_ROOT "${CMAKE_INSTALL_PREFIX}/cmakemodules" CACHE PATH "Path to the iLCSoft CMake modules")
# set(ILCSOFT_CMAKE_MODULES "${CMAKE_INSTALL_PREFIX}/cmakemodules" CACHE PATH "Path to the iLCSoft CMake modules")

# These are needed when recompiling and changing CMakeLists.txt
# set(ILCSOFT_CMAKE_MODULES_DIR "${CMAKE_BINARY_DIR}/_deps/ilcutil-build/cmakemodules-prefix/src/cmakemodules-build" CACHE PATH "Path to the iLCSoft CMake modules")
# message(WARNING "ILCSOFT_CMAKE_MODULES_DIR: ${ILCSOFT_CMAKE_MODULES_DIR}")
set(streamlog_DIR "${CMAKE_BINARY_DIR}/_deps/ilcutil-build/streamlog/" CACHE PATH "Path to streamlog directory")
# # set(ILCTEST_DIR "${CMAKE_BINARY_DIR}/_deps/ilcutil-build/ilctest" CACHE PATH "Path to ilctest directory")
# set(ILCTEST_DIR "${CMAKE_INSTALL_PREFIX}" CACHE PATH "Path to ilctest directory")
# message(WARNING "ILCTEST_DIR: ${ILCTEST_DIR}")


# Needed by LCCD
set(LCIO_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/LCIO/src/cpp/include;${CMAKE_SOURCE_DIR}/LCIO/src/cpp/include/pre-generated" CACHE PATH "Path to LCIO include directory")
# Needed by Marlin
set(streamlog_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/iLCUtil/streamlog/source/include" CACHE PATH "Path to LCIO include directory")
set(GEAR_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/GEAR/include;${CMAKE_SOURCE_DIR}/GEAR/include/gear;${CMAKE_BINARY_DIR}/_deps/gear-build" CACHE PATH "Path to GEAR include directory")
set(LCCD_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/LCCD/source/include" CACHE PATH "Path to LCCD include directory")
# Needed by k4MarlinWrapper
set(Marlin_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/Marlin/source/include;${streamlog_INCLUDE_DIRS};${GEAR_INCLUDE_DIRS};${CMAKE_BINARY_DIR}/_deps/marlin-build" CACHE PATH "Path to Marlin include directory")


set(Marlin_LIBRARIES Marlin)

