#include <iostream>

#include "math_utils/core.hpp"

int main(int argc, char** argv) {
  const char* name = argc > 1 ? argv[1] : "";
  std::cout << math_utils::greeting(name) << '\n';
  return 0;
}
