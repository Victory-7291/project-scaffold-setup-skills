#include <iostream>

#include "image_tool/core.hpp"

int main(int argc, char** argv) {
  const char* name = argc > 1 ? argv[1] : "";
  std::cout << image_tool::greeting(name) << '\n';
  return 0;
}
