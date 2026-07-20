#!/usr/bin/env python3
"""Generate a minimal valid 1x1 PNG for local testing/debugging."""

import struct
import zlib
import sys


def make_png() -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + chunk_type
            + data
            + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    # One scanline: filter byte 0 + R G B
    raw = b"\x00\xff\x00\x00"
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")

    return sig + chunk(b"IHDR", ihdr) + idat + iend


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "tools/sample.png"
    with open(out_path, "wb") as f:
        f.write(make_png())
    print(f"Wrote {out_path}")
