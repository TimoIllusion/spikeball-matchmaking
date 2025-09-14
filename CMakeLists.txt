cmake_minimum_required(VERSION 3.12)
project(matchmaking_fast)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(pybind11 REQUIRED)

# Add optimization flags
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -ffast-math")
endif()

if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /O2 /arch:AVX2")
endif()

# Create the pybind11 module
pybind11_add_module(matchmaking_fast player_metrics_fast.cpp)

# Set properties for the module
target_compile_definitions(matchmaking_fast PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
target_compile_features(matchmaking_fast PRIVATE cxx_std_17)