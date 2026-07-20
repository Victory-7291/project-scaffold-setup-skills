#pragma once

#include <string>
#include <string_view>
#include <optional>
#include <vector>

namespace image_tool {

/// Minimal image metadata structure used by the CLI.
struct ImageInfo {
    int width{0};
    int height{0};
    int channels{0};
    std::string format{"unknown"};
    bool valid{false};
};

/// Parse basic metadata from a well-known image file path.
/// This is intentionally a simplified placeholder implementation.
std::optional<ImageInfo> parse_image_info(std::string_view path);

/// List supported image formats.
std::vector<std::string> supported_formats();

} // namespace image_tool
