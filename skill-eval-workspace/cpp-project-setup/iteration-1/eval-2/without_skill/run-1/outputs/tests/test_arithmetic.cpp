#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "math_utils/math_utils.hpp"

using ::testing::DoubleNear;

namespace math_utils {

TEST(ArithmeticTest, Add)
{
    EXPECT_EQ(add(2, 3), 5);
    EXPECT_EQ(add(-2, 3), 1);
    EXPECT_EQ(add(0, 0), 0);
}

TEST(ArithmeticTest, Subtract)
{
    EXPECT_EQ(subtract(5, 3), 2);
    EXPECT_EQ(subtract(3, 5), -2);
    EXPECT_EQ(subtract(0, 0), 0);
}

TEST(ArithmeticTest, Multiply)
{
    EXPECT_EQ(multiply(4, 5), 20);
    EXPECT_EQ(multiply(-4, 5), -20);
    EXPECT_EQ(multiply(0, 100), 0);
}

TEST(ArithmeticTest, Divide)
{
    EXPECT_EQ(divide(10, 2), 5);
    EXPECT_EQ(divide(7, 3), 2);
    EXPECT_THROW(static_cast<void>(divide(1, 0)), std::invalid_argument);
}

TEST(ArithmeticTest, Factorial)
{
    EXPECT_EQ(factorial(0), 1);
    EXPECT_EQ(factorial(1), 1);
    EXPECT_EQ(factorial(5), 120);
    EXPECT_THROW(static_cast<void>(factorial(-1)), std::invalid_argument);
}

TEST(ConstantsTest, PiValue)
{
    EXPECT_THAT(circle_area(1.0), DoubleNear(constants::pi, 1e-12));
}

TEST(ConstantsTest, CircleArea)
{
    EXPECT_THAT(circle_area(2.0), DoubleNear(4.0 * constants::pi, 1e-12));
}

} // namespace math_utils
