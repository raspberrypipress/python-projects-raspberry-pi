cmake_minimum_required(VERSION 3.10)
project(encoder_pio)

find_package(PythonInterp 3.5 REQUIRED)

# This goes after, since it uses PythonInterp as hint
find_package(PythonLibs 3.5 REQUIRED)

include_directories ("${PYTHON_INCLUDE_DIRS}")

add_subdirectory(../utils/piolib ./pio_build)

add_library(encoder_pio SHARED encoder_pio.c)

include_directories(${CMAKE_SOURCE_DIR}/../utils/piolib/include)
target_link_libraries(encoder_pio pio)

set_target_properties(
    encoder_pio
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME "encoder_pio"
        LINKER_LANGUAGE C
    )

