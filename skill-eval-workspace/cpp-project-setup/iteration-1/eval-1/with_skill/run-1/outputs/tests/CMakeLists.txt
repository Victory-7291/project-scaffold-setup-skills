find_package(GTest CONFIG REQUIRED)
include(GoogleTest)

add_executable(cpp_eval_legacy_tests test_core.cpp)
target_link_libraries(cpp_eval_legacy_tests PRIVATE cpp_eval_legacy::lib GTest::gtest_main)
target_project_warnings(cpp_eval_legacy_tests)

gtest_discover_tests(cpp_eval_legacy_tests)
