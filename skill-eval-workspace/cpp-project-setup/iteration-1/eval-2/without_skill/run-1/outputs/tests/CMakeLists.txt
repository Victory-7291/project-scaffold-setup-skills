include(FetchContent)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
    GIT_SHALLOW TRUE
)

set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(math_utils_tests
    test_arithmetic.cpp
)

target_link_libraries(math_utils_tests PRIVATE math_utils::math_utils GTest::gtest_main)

if(MSVC)
    target_compile_options(math_utils_tests PRIVATE /W4 /WX-)
endif()

include(GoogleTest)
gtest_discover_tests(math_utils_tests)
