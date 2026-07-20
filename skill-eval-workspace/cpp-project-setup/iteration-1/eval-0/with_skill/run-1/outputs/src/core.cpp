#include "image_tool/core.hpp"

namespace image_tool {

std::string greeting(std::string_view name) {
  if (name.empty()) {
    return "hello, modern C++";
  }
  return "hello, " + std::string{name};
}

}  // namespace image_tool
