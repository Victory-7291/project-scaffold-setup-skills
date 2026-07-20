find_package(GTest CONFIG REQUIRED)
include(GoogleTest)

add_executable(math_utils_tests test_core.cpp)
target_link_libraries(math_utils_tests PRIVATE math_utils::lib GTest::gtest_main)
target_project_warnings(math_utils_tests)

gtest_discover_tests(math_utils_tests)
