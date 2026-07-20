FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    ninja-build \
    gcc-arm-none-eabi \
    binutils-arm-none-eabi \
    gdb-multiarch \
    openocd \
    clang-format \
    clang-tidy \
    python3 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /work
