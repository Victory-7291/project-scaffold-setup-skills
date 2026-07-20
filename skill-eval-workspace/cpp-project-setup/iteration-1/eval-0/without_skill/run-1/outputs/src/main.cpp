#include "image_tool/image_info.hpp"

#include <CLI/CLI.hpp>
#include <fmt/format.h>

#include <cstdlib>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    CLI::App app{"image_tool: inspect image metadata from the command line"};
    argv = app.ensure_utf8(argv);

    std::string input_path;
    bool list_formats = false;

    app.add_option("-i,--input", input_path, "Path to the input image")
        ->required(false)
        ->check(CLI::ExistingFile);
    app.add_flag("-l,--list-formats", list_formats, "List supported image formats");

    try {
        app.parse(argc, argv);
    } catch (const CLI::ParseError& e) {
        return app.exit(e);
    }

    if (list_formats) {
        fmt::println("Supported formats:");
        for (const auto& format : image_tool::supported_formats()) {
            fmt::println("  {}", format);
        }
        return EXIT_SUCCESS;
    }

    if (input_path.empty()) {
        fmt::println(stderr, "Error: --input is required unless --list-formats is used.");
        return EXIT_FAILURE;
    }

    auto info = image_tool::parse_image_info(input_path);
    if (!info) {
        fmt::println(stderr, "Error: could not parse '{}' as a supported image.", input_path);
        return EXIT_FAILURE;
    }

    fmt::println("format:   {}", info->format);
    fmt::println("width:    {}", info->width);
    fmt::println("height:   {}", info->height);
    fmt::println("channels: {}", info->channels);

    return EXIT_SUCCESS;
}
