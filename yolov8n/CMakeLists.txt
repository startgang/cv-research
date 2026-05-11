# Minimum CMake version required
cmake_minimum_required(VERSION 3.10)

# Project name and language
project(DmCodeEveluation VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_CXX_FLAGS "-O3 -DNDEBUG -march=native -mtune=native -flto")

# Set output directories for executables and libraries
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

find_package(OpenCV REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(DMTX REQUIRED libdmtx)

add_executable(${PROJECT_NAME} dm_code_eveluation.cc)

target_link_libraries(${PROJECT_NAME}
    ${OpenCV_LIBS}
    ${DMTX_LIBRARIES}
)