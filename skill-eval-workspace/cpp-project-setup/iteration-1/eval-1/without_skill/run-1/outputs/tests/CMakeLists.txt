find_package(GTest CONFIG REQUIRED)

add_executable(greeter_tests test_greeter.cpp)
target_link_libraries(greeter_tests PRIVATE legacy_greeter::greeter GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(greeter_tests)
