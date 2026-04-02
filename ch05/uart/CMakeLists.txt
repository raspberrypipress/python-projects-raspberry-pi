cmake_minimum_required(VERSION 3.10)
project(mymodule)

find_package(PythonInterp 3.5 REQUIRED)

# This goes after, since it uses PythonInterp as hint
find_package(PythonLibs 3.5 REQUIRED)

include_directories ("${PYTHON_INCLUDE_DIRS}")

add_subdirectory(../utils/piolib ./pio_build)

add_library(uart_pio SHARED uart_pio.c)

include_directories(${CMAKE_SOURCE_DIR}/../utils/piolib/include)
target_link_libraries(uart_pio pio)

set_target_properties(
    uart_pio
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME "uart_pio"
        LINKER_LANGUAGE C
    )

