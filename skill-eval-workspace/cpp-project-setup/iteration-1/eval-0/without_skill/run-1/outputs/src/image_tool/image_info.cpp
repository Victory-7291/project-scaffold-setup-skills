#include "image_tool/image_info.hpp"

#include <fmt/format.h>

#include <fstream>
#include <array>
#include <algorithm>
#include <iterator>

namespace image_tool {

namespace {

constexpr std::array<std::byte, 8> png_signature{
    std::byte{0x89}, std::byte{0x50}, std::byte{0x4E},
    std::byte{0x47}, std::byte{0x0D}, std::byte{0x0A},
    std::byte{0x1A}, std::byte{0x0A}};

constexpr std::array<std::byte, 3> jpeg_signature{
    std::byte{0xFF}, std::byte{0xD8}, std::byte{0xFF}};

constexpr std::array<std::byte, 4> bmp_signature{
    std::byte{0x42}, std::byte{0x4D}, std::byte{0x00}, std::byte{0x00}};

bool starts_with_signature(std::ifstream& in, std::span<const std::byte> sig) {
    std::vector<std::byte> buffer(sig.size());
    in.read(reinterpret_cast<char*>(buffer.data()), static_cast<std::streamsize>(sig.size()));
    if (!in) return false;
    return std::equal(sig.begin(), sig.end(), buffer.begin(), buffer.end());
}

std::optional<ImageInfo> parse_png(std::ifstream& in) {
    // IHDR starts at byte 16 after the 8-byte signature and 4-byte length/type.
    in.seekg(16, std::ios::beg);
    if (!in) return std::nullopt;

    std::array<std::byte, 13> ihdr{};
    in.read(reinterpret_cast<char*>(ihdr.data()), static_cast<std::streamsize>(ihdr.size()));
    if (!in) return std::nullopt;

    auto read_u32_be = [](std::span<const std::byte, 4> bytes) {
        return (std::to_integer<std::uint32_t>(bytes[0]) << 24u) |
               (std::to_integer<std::uint32_t>(bytes[1]) << 16u) |
               (std::to_integer<std::uint32_t>(bytes[2]) << 8u) |
               (std::to_integer<std::uint32_t>(bytes[3]));
    };

    ImageInfo info{};
    info.format = "png";
    info.width = static_cast<int>(read_u32_be(std::span<const std::byte, 4>{ihdr.data(), 4}));
    info.height = static_cast<int>(read_u32_be(std::span<const std::byte, 4>{ihdr.data() + 4, 4}));
    info.channels = std::to_integer<int>(ihdr[9]) == 0 ? 1 : std::to_integer<int>(ihdr[9]);
    info.valid = true;
    return info;
}

std::optional<ImageInfo> parse_jpeg(std::ifstream& /*in*/) {
    // JPEG parsing is non-trivial; report unknown dimensions but valid format.
    ImageInfo info{};
    info.format = "jpeg";
    info.valid = true;
    return info;
}

std::optional<ImageInfo> parse_bmp(std::ifstream& in) {
    in.seekg(18, std::ios::beg);
    if (!in) return std::nullopt;

    std::array<std::byte, 8> dib{};
    in.read(reinterpret_cast<char*>(dib.data()), static_cast<std::streamsize>(dib.size()));
    if (!in) return std::nullopt;

    auto read_u32_le = [](std::span<const std::byte, 4> bytes) {
        return std::to_integer<std::uint32_t>(bytes[0]) |
               (std::to_integer<std::uint32_t>(bytes[1]) << 8u) |
               (std::to_integer<std::uint32_t>(bytes[2]) << 16u) |
               (std::to_integer<std::uint32_t>(bytes[3]) << 24u);
    };

    ImageInfo info{};
    info.format = "bmp";
    info.width = static_cast<int>(read_u32_le(std::span<const std::byte, 4>{dib.data(), 4}));
    info.height = static_cast<int>(read_u32_le(std::span<const std::byte, 4>{dib.data() + 4, 4}));
    info.channels = 3;
    info.valid = true;
    return info;
}

} // namespace

std::optional<ImageInfo> parse_image_info(std::string_view path) {
    std::ifstream in{std::string{path}, std::ios::binary};
    if (!in) return std::nullopt;

    if (starts_with_signature(in, png_signature)) {
        in.clear();
        return parse_png(in);
    }
    in.clear();
    in.seekg(0, std::ios::beg);
    if (starts_with_signature(in, jpeg_signature)) {
        in.clear();
        return parse_jpeg(in);
    }
    in.clear();
    in.seekg(0, std::ios::beg);
    if (starts_with_signature(in, std::span<const std::byte>{bmp_signature.data(), 2})) {
        in.clear();
        return parse_bmp(in);
    }

    return std::nullopt;
}

std::vector<std::string> supported_formats() {
    return {"png", "jpeg", "bmp"};
}

} // namespace image_tool
