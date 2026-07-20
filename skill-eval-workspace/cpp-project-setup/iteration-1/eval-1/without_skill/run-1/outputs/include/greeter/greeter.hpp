#pragma once

#include <string>

namespace greeter {

/// Returns the classic greeting message.
[[nodiscard]] std::string greeting_message();

/// Prints the classic greeting message to stdout.
void say_hello();

} // namespace greeter
