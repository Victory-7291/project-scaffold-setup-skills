#define CATCH_CONFIG_MAIN
#include <catch2/catch_session.hpp>

// Catch2WithMain target also provides main(), but this file is kept as a
// fallback for builds that want an explicit test main.
int main(int argc, char* argv[]) {
    return Catch::Session().run(argc, argv);
}
