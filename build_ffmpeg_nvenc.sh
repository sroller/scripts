#!/bin/bash

set -e

# Define directories
export SRC="$HOME/ffmpeg_sources"
export BUILD="$HOME/ffmpeg_build"
export BIN="$HOME/bin"
export PKG_CONFIG_PATH="$BUILD/lib/pkgconfig"

mkdir -p "$SRC" "$BUILD" "$BIN"

# Build x264
cd "$SRC"
rm -rf x264
git clone --depth 1 https://code.videolan.org/videolan/x264.git
cd x264
./configure --prefix="$BUILD" --bindir="$BIN" --enable-static
make -j$(nproc)
make install

# Build FFmpeg with NVENC and x264
cd "$SRC"
rm -rf ffmpeg
git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
cd ffmpeg
make distclean
./configure \
  --prefix="$BUILD" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$BUILD/include" \
  --extra-ldflags="-L$BUILD/lib" \
  --extra-libs="-lpthread -lm" \
  --bindir="$BIN" \
  --enable-gpl \
  --enable-nonfree \
  --enable-libx264 \
  --enable-cuda \
  --enable-cuvid \
  --enable-nvenc \
  --enable-libnpp \
  --disable-debug \
  --enable-static \
  --disable-shared
make -j$(nproc)
make install

echo -e "\n✅ FFmpeg built successfully!"
"$BIN/ffmpeg" -hwaccels
"$BIN/ffmpeg" -codecs | grep nvenc
