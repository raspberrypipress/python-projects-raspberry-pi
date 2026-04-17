cmake_minimum_required(VERSION 3.10)
project(neopixel_pio C)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (CMAKE_VERSION VERSION_LESS "3.12")
    find_package(PythonInterp 3 REQUIRED)
    find_package(PythonLibs 3 REQUIRED)
    include_directories(${PYTHON_INCLUDE_DIRS})
else()
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    include_directories(${Python3_INCLUDE_DIRS})
endif()

add_subdirectory(../utils/piolib ./pio_build)

add_library(neopixel_pio MODULE neopixel_pio.c)
target_include_directories(neopixel_pio PRIVATE ${CMAKE_SOURCE_DIR}/../utils/piolib/include)

# Do not link the Python library into a Python extension module.
# The interpreter already provides the Python symbols at runtime.
target_link_libraries(neopixel_pio PRIVATE pio)

set_target_properties(
    neopixel_pio
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME "neopixel_pio"
        SUFFIX ".so"
        LINKER_LANGUAGE C
    )

