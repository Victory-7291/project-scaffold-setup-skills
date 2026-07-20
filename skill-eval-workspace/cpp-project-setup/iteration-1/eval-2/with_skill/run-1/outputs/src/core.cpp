#include "math_utils/core.hpp"

namespace math_utils {

std::string greeting(std::string_view name) {
  if (name.empty()) {
    return "hello, modern C++";
  }
  return "hello, " + std::string{name};
}

}  // namespace math_utils
