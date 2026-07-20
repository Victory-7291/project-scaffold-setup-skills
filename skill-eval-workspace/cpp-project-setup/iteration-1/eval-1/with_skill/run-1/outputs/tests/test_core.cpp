#include <gtest/gtest.h>

#include "cpp_eval_legacy/core.hpp"

TEST(CoreTest, GreetsLegacyProject) {
  EXPECT_EQ(cpp_eval_legacy::greeting("legacy C++ project"), "Hello, legacy C++ project!");
}

TEST(CoreTest, GreetsNamedUser) {
  EXPECT_EQ(cpp_eval_legacy::greeting("Codex"), "Hello, Codex!");
}

TEST(CoreTest, HandlesEmptyName) {
  EXPECT_EQ(cpp_eval_legacy::greeting(""), "Hello, !");
}
