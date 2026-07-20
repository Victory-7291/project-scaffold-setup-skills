find_package(GTest CONFIG REQUIRED)
include(GoogleTest)

add_executable(image_tool_tests test_core.cpp)
target_link_libraries(image_tool_tests PRIVATE image_tool::lib GTest::gtest_main)
target_project_warnings(image_tool_tests)

gtest_discover_tests(image_tool_tests)
