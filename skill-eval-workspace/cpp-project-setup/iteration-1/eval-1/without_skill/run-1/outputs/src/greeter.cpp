#include "greeter/greeter.hpp"

#include <iostream>

namespace greeter {

std::string greeting_message() {
    return "Hello, legacy C++ project!";
}

void say_hello() {
    std::cout << greeting_message() << std::endl;
}

} // namespace greeter
