#!/usr/bin/env bash

set -euo pipefail

# --- Configuration ---
OPENCV_VERSION="4.12.0"
PYTHON=$(uv run which python)
PYTHON_SITE_PACKAGES=$(uv pip show numpy | awk '/Location:/{print $2}')
GCC_VERSION="12"
CUDA_ARCH_BIN="8.6"

# --- Check prerequisites ---
command -v uv >/dev/null || { echo "❌ uv not found. Please install it first."; exit 1; }
command -v cmake >/dev/null || { echo "❌ cmake not found."; exit 1; }
command -v nvcc >/dev/null || { echo "❌ CUDA toolkit not found."; exit 1; }

# --- Install GCC 12 if needed ---
if ! command -v gcc-12 >/dev/null; then
  echo "🔧 Installing GCC 12..."
  sudo apt update
  sudo apt install -y gcc-12 g++-12
fi

# --- Clone repositories ---
echo "📥 Cloning OpenCV $OPENCV_VERSION..."
rm -rf opencv opencv_contrib
git clone --branch "$OPENCV_VERSION" --depth 1 https://github.com/opencv/opencv.git
git clone --branch "$OPENCV_VERSION" --depth 1 https://github.com/opencv/opencv_contrib.git

# --- Build directory ---
mkdir -p opencv/build && cd opencv/build

# --- Configure with CMake ---
echo "⚙️ Configuring CMake..."
CC=/usr/bin/gcc-${GCC_VERSION}
CXX=/usr/bin/g++-${GCC_VERSION}
cmake -D CMAKE_BUILD_TYPE=Release \
      -D CMAKE_C_COMPILER=$CC \
      -D CMAKE_CXX_COMPILER=$CXX \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
      -D WITH_CUDA=ON \
      -D CUDA_ARCH_BIN=${CUDA_ARCH_BIN} \
      -D ENABLE_FAST_MATH=ON \
      -D CUDA_FAST_MATH=ON \
      -D WITH_CUBLAS=ON \
      -D WITH_CUDNN=ON \
      -D OPENCV_DNN_CUDA=ON \
      -D BUILD_opencv_python3=ON \
      -D BUILD_opencv_python2=OFF \
      -D PYTHON_EXECUTABLE="${PYTHON}" \
      -D PYTHON3_PACKAGES_PATH="${PYTHON_SITE_PACKAGES}" \
      -D BUILD_TESTS=OFF \
      -D BUILD_PERF_TESTS=OFF \
      -D BUILD_EXAMPLES=OFF \
      ..

# --- Build ---
echo "🔨 Building OpenCV with CUDA support..."
make -j"$(nproc)"

# --- Install ---
echo "📦 Installing OpenCV..."
sudo make install

# --- Copy cv2.so into uv env if needed ---
CV2_SO=$(find . -name "cv2*.so" | grep -m1 python-3)
if [[ -n "$CV2_SO" ]]; then
    echo "✅ Installing cv2.so to uv environment..."
    mkdir -p "$PYTHON_SITE_PACKAGES/cv2"
    cp "$CV2_SO" "$PYTHON_SITE_PACKAGES/cv2/cv2.so"
else
    echo "⚠️ Could not find built cv2.so"
fi

# --- Done ---
echo "🎉 OpenCV $OPENCV_VERSION with CUDA support is built and installed!"
echo "✅ Test with: uv python -c 'import cv2; print(cv2.getBuildInformation())'"
