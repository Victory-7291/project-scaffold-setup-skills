#include "greeter/greeter.hpp"

#include <gtest/gtest.h>

TEST(GreeterTest, MessageMatchesLegacyBehavior) {
    EXPECT_EQ(greeter::greeting_message(), "Hello, legacy C++ project!");
}

TEST(GreeterTest, MessageIsNotEmpty) {
    EXPECT_FALSE(greeter::greeting_message().empty());
}
