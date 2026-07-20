#include "image_tool/image_info.hpp"

#include <catch2/catch_test_macros.hpp>

#include <fstream>
#include <string>

TEST_CASE("supported_formats returns PNG, JPEG, and BMP", "[image_info]") {
    auto formats = image_tool::supported_formats();
    REQUIRE(formats.size() == 3);
    REQUIRE(formats[0] == "png");
    REQUIRE(formats[1] == "jpeg");
    REQUIRE(formats[2] == "bmp");
}

TEST_CASE("parse_image_info returns nullopt for a missing file", "[image_info]") {
    REQUIRE(image_tool::parse_image_info("/non/existent/file.png") == std::nullopt);
}

namespace {

void write_png_file(const std::string& path, std::uint32_t width, std::uint32_t height) {
    std::ofstream out{path, std::ios::binary};

    auto write_u32_be = [&out](std::uint32_t value) {
        char bytes[4] = {
            static_cast<char>((value >> 24u) & 0xFFu),
            static_cast<char>((value >> 16u) & 0xFFu),
            static_cast<char>((value >> 8u) & 0xFFu),
            static_cast<char>(value & 0xFFu)};
        out.write(bytes, 4);
    };

    // PNG signature
    const std::uint8_t sig[8] = {0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A};
    out.write(reinterpret_cast<const char*>(sig), 8);

    // IHDR chunk: length (4) + type (4) + data (13) + CRC (4)
    write_u32_be(13);
    out.write("IHDR", 4);
    write_u32_be(width);
    write_u32_be(height);
    char ihdr_rest[5] = {8, 2, 0, 0, 0}; // bit depth, color type RGB, compression, filter, interlace
    out.write(ihdr_rest, 5);
    write_u32_be(0); // placeholder CRC
}

} // namespace

TEST_CASE("parse_image_info parses a synthetic PNG", "[image_info]") {
    const std::string path = "/tmp/cpp_eval_image_tool_baseline_test.png";
    write_png_file(path, 1920, 1080);

    auto info = image_tool::parse_image_info(path);
    REQUIRE(info.has_value());
    REQUIRE(info->valid);
    REQUIRE(info->format == "png");
    REQUIRE(info->width == 1920);
    REQUIRE(info->height == 1080);

    std::remove(path.c_str());
}
