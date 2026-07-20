add_library(cpp_eval_legacy_lib core.cpp)
add_library(cpp_eval_legacy::lib ALIAS cpp_eval_legacy_lib)

target_include_directories(cpp_eval_legacy_lib
  PUBLIC
    "${PROJECT_SOURCE_DIR}/include"
)
target_project_warnings(cpp_eval_legacy_lib)

add_executable(cpp_eval_legacy_app main.cpp)
target_link_libraries(cpp_eval_legacy_app PRIVATE cpp_eval_legacy::lib)
target_project_warnings(cpp_eval_legacy_app)
