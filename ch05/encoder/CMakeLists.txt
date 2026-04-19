cmake_minimum_required(VERSION 3.10)
project(encoder_pio C)
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

add_library(encoder_pio MODULE encoder_pio.c)
target_include_directories(encoder_pio PRIVATE ${CMAKE_SOURCE_DIR}/../utils/piolib/include)

target_link_libraries(encoder_pio PRIVATE pio)

set_target_properties(
    encoder_pio
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME "encoder_pio"
        SUFFIX ".so"
        LINKER_LANGUAGE C
    )