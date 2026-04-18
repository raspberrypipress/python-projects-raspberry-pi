cmake_minimum_required(VERSION 3.10)
project(uart_pio C)
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

add_library(uart_pio MODULE uart_pio.c)
target_include_directories(uart_pio PRIVATE ${CMAKE_SOURCE_DIR}/../utils/piolib/include)

target_link_libraries(uart_pio PRIVATE pio)

set_target_properties(
    uart_pio
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME "uart_pio"
        SUFFIX ".so"
        LINKER_LANGUAGE C
    )

