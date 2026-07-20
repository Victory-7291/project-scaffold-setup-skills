#include "cpp_eval_legacy/core.hpp"

namespace cpp_eval_legacy {

std::string greeting(std::string_view name) {
  return "Hello, " + std::string{name} + "!";
}

}  // namespace cpp_eval_legacy
