cmake_minimum_required(VERSION 3.14)
project(webplay VERSION 0.156.36 LANGUAGES NONE)

# WebPlay — Python-based media streaming server
# This CMake file provides build metadata and IDE integration.
# Actual build steps are delegated to setuptools / Makefile.

set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")
set(PROJECT_DESCRIPTION "Self-hosted media streaming server")
set(PROJECT_HOMEPAGE_URL "https://github.com/rkriad585/WebPlay")

# --- IDE Integration ---
# Mark Python source files for indexing
file(GLOB_RECURSE PYTHON_SOURCES
    "app.py"
    "config.py"
    "core/*.py"
)

# --- Custom Targets ---
set(REQUIREMENTS "${CMAKE_SOURCE_DIR}/requirements.txt")
set(APP_SCRIPT "${CMAKE_SOURCE_DIR}/app.py")

add_custom_target(install
    COMMAND pip install -r ${REQUIREMENTS}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Installing Python dependencies"
)

add_custom_target(test
    COMMAND python -m pytest -v
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running test suite"
)

add_custom_target(run
    COMMAND python ${APP_SCRIPT} free
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Starting WebPlay"
)

add_custom_target(clean-python
    COMMAND find ${CMAKE_SOURCE_DIR} -name "*.pyc" -delete
    COMMAND rm -rf ${CMAKE_SOURCE_DIR}/__pycache__
    COMMAND rm -rf ${CMAKE_SOURCE_DIR}/build
    COMMAND rm -rf ${CMAKE_SOURCE_DIR}/dist
    COMMENT "Cleaning Python build artifacts"
)

# --- Release Build Type ---
set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type")

message(STATUS "WebPlay v${PROJECT_VERSION}")
message(STATUS "Python sources: ${PYTHON_SOURCES}")
