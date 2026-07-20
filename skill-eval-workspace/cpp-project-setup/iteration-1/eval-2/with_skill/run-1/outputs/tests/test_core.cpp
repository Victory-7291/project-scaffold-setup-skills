#include <gtest/gtest.h>

#include "math_utils/core.hpp"

TEST(CoreTest, GreetsNamedUser) {
  EXPECT_EQ(math_utils::greeting("Codex"), "hello, Codex");
}

TEST(CoreTest, GreetsDefaultUser) {
  EXPECT_EQ(math_utils::greeting(""), "hello, modern C++");
}
