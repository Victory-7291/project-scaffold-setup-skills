#pragma once

#include "math_utils/constants.hpp"

#include <cstdint>
#include <stdexcept>
#include <string>

namespace math_utils {

[[nodiscard]] constexpr int64_t add(int64_t lhs, int64_t rhs) noexcept
{
    return lhs + rhs;
}

[[nodiscard]] constexpr int64_t subtract(int64_t lhs, int64_t rhs) noexcept
{
    return lhs - rhs;
}

[[nodiscard]] constexpr int64_t multiply(int64_t lhs, int64_t rhs) noexcept
{
    return lhs * rhs;
}

[[nodiscard]] constexpr int64_t divide(int64_t lhs, int64_t rhs)
{
    if (rhs == 0) {
        throw std::invalid_argument("division by zero");
    }
    return lhs / rhs;
}

[[nodiscard]] constexpr int64_t factorial(int64_t n)
{
    if (n < 0) {
        throw std::invalid_argument("factorial of negative number");
    }
    int64_t result = 1;
    for (int64_t i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

[[nodiscard]] constexpr double circle_area(double radius) noexcept
{
    return constants::pi * radius * radius;
}

} // namespace math_utils
