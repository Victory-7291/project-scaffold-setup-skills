#include <gtest/gtest.h>

#include "image_tool/core.hpp"

TEST(CoreTest, GreetsNamedUser) {
  EXPECT_EQ(image_tool::greeting("Codex"), "hello, Codex");
}

TEST(CoreTest, GreetsDefaultUser) {
  EXPECT_EQ(image_tool::greeting(""), "hello, modern C++");
}
