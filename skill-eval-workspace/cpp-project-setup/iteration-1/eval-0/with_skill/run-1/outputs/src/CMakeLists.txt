add_library(image_tool_lib core.cpp)
add_library(image_tool::lib ALIAS image_tool_lib)

target_include_directories(image_tool_lib
  PUBLIC
    "${PROJECT_SOURCE_DIR}/include"
)
target_project_warnings(image_tool_lib)

add_executable(image_tool_app main.cpp)
target_link_libraries(image_tool_app PRIVATE image_tool::lib)
target_project_warnings(image_tool_app)
