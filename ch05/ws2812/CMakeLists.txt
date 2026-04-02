cmake_minimum_required(VERSION 3.10)
project(mymodule)

find_package(PythonInterp 3.5 REQUIRED)

# This goes after, since it uses PythonInterp as hint
find_package(PythonLibs 3.5 REQUIRED)

include_directories ("${PYTHON_INCLUDE_DIRS}")

add_subdirectory(../utils/piolib ./pio_build)

add_library(neopixel_pio SHARED neopixel_pio.c)

include_directories(${CMAKE_SOURCE_DIR}/../utils/piolib/include)
target_link_libraries(neopixel_pio pio)

set_target_properties(
    neopixel_pio
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME "neopixel_pio"
        LINKER_LANGUAGE C
    )

