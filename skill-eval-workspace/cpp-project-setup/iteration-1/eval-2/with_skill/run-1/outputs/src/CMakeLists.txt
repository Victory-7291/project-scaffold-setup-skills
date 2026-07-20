add_library(math_utils_lib core.cpp)
add_library(math_utils::lib ALIAS math_utils_lib)

target_include_directories(math_utils_lib
  PUBLIC
    "${PROJECT_SOURCE_DIR}/include"
)
target_project_warnings(math_utils_lib)

add_executable(math_utils_app main.cpp)
target_link_libraries(math_utils_app PRIVATE math_utils::lib)
target_project_warnings(math_utils_app)
